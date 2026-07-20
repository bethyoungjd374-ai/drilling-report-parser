# Operation 结构化数据标准

## 1. 存储边界

Operation 同时保留两层数据，两者不能互相替代：

- `dpr_report_row.row_json`：来源快照，只用于追溯、重放和解析对账。
- `dpr_operation` + `dpr_operation_classification`：正式结构化事实，作业时效和效率统计只能读这一层。

四类日报（钻井、完井、修井、搬迁）共用同一张 `dpr_operation`，通过 `dpr_report.report_type` 区分来源。每一条原始 operation 必须与一条事实记录一一对应，唯一键为 `(daily_report_id, source_row_no)`。

## 2. 作业事实字段

| 业务含义 | 标准字段 | 口径 |
|---|---|---|
| 原始行定位 | `daily_report_id`, `source_row_no`, `source_hash` | 保证可与原始 JSON 逐行对账 |
| 原始时钟 | `source_from_text`, `source_to_text` | 原样保留 FROM/TO，解析失败也不丢失 |
| 标准时间 | `started_at`, `ended_at` | `DATETIME`；跨零点时 `ended_at` 落在次日 |
| 申报时效 | `hours` | 日报明示时长，单位 h，主计量值 |
| 钟表时效 | `clock_hours` | `ended_at - started_at`，单位 h |
| 时差 | `duration_variance_hours` | `hours - clock_hours` |
| 跨日 | `cross_midnight_flag` | 起止时间是否跨日 |
| 时长来源 | `hours_source` | `DECLARED` 为日报申报值；仅当原表时长留空且起止时间完整时使用 `CLOCK_DERIVED` |
| 时效质量 | `time_validation_status` | `VALID`、`DURATION_MISMATCH`、`MISSING_TIME`、`INVALID_TIME`、`MISSING_HOURS` |
| 来源工作分类 | `op_code`, `op_sub` | 保留模板中的一/二级分类文字 |
| 标准工作分类 | `work_category_code`, `work_subcategory_code` | 大写下划线机器代码，再经已审核别名映射，用于跨模板分组；模板未提供某一级时存 `UNSPECIFIED`，不留空 |
| 来源时效类型 | `source_op_type` | 来源 P/SC/NPT，永不被人工确认结果覆盖 |
| 工作内容原文 | `operation_details` | 独立 `TEXT` 字段，不是 JSON |
| 规范化工作内容 | `operation_details_normalized` | 统一换行和空白，用于检索、规则和文本分析 |
| 描述指纹 | `description_hash` | 规范化描述 SHA-256，用于去重和变更识别 |

时效一致容差为 `0.05h`（3 分钟）。超过容差的行保留申报值，但标记为 `DURATION_MISMATCH`，不直接进入正式统计。

工作分类的别名映射独立放在 `operation_standardization.py`，不与任一 PDF 模板解析器绑定。例如 `COMPLETI ON OPS` 与 `COMPLETION OPS` 统一为 `COMPLETION_OPS`，`CEM` / `CEME` 统一为 `CEMENTING`。只接受可以由源文和业务含义确认的映射；如 `ST`、`GYR` 这类仍可能有多义的缩写保留独立代码，不做猜测归并。

模板没有一级或二级分类时，对应标准代码使用 `UNSPECIFIED`。这表示“源模板未提供”，与解析失败或未知业务分类分开，便于统计时显式分组和后续补录。

## 3. 时效与责任分类

`dpr_operation_classification` 与 operation 一对一，所有可统计的分类项都是独立字段：

- `confirmed_op_type`：人工/规则确认后的 P、SC、NPT。
- `productive_flag`, `productivity_type_code`：生产/非生产属性。
- `work_bucket`：作业、搬迁、有人待工、无人待工、不可抗力、维修。
- `billing_status`：全日费、部分日费、零日费。
- `responsibility`：我方、甲方、第三方、不可抗力。
- `cause_code`, `service_line`：原因类别和服务线。
- `rule_id`, `rule_version`, `confidence`：规则来源及置信度。
- `confirmation_status`, `confirmed_at`, `confirmed_by`, `change_reason`：审批状态和责任链。

`WORK_BUCKET`、`RESPONSIBILITY`、`BILLING_STATUS`、`CAUSE_CODE` 的可选编码由 `md_appendix_category` / `md_appendix_value` 管理，不在 JSON 中自由填写。SC/NPT 必须经过正式确认流程；规则只能给候选结果，不能替代责任判定。

## 4. 统计口径

`vw_operation_structured` 是 operation 的统一查询入口，它给出：

- `effective_op_type = confirmed_op_type` 非空时取确认值，否则取 `source_op_type`。
- `statistics_status = READY` 仅当时效校验为 `VALID` 且分类状态为 `CONFIRMED` / `AUTO_CONFIRMED`。
- `statistical_hours` 仅在 `READY` 时有值；其他行保留原始事实，但不混入官方汇总。

`vw_monthly_rig_workload` 只汇总 `statistical_hours`。`vw_job_efficiency` 如存在时间异常或待确认分类，`efficiency` 返回 `NULL`，`official_status` 分别标识 `PENDING_TIME_REVIEW` 或 `PENDING_CLASSIFICATION`。

生产统计、项目生产明细、NPT 统计及其 Excel 导出共用 `vw_rig_production_timeline` 查询服务。该视图只包含 `normalization_status='NORMALIZED'` 且 `match_status='MATCHED'` 的日报；未关联项目、井队或井的数据只出现在数据质量计数中，不进入 KPI。后台主数据关系保存后会自动重算历史日报匹配状态。系统不创建统计汇总表。

## 5. 一致性要求

1. 保存日报必须在同一事务中写原始行和标准事实。
2. 原始 operation 行数必须等于 `dpr_operation` 行数；`source_hash` 用于核验内容版本。
3. 源 P/SC/NPT 只写 `source_op_type`，人工结果只写 `confirmed_op_type`，不允许反向覆盖原值。
4. 时效异常和分类待审必须可见，不能以 0 小时或默认分类静默代替。
5. 统计查询不得直接从 `row_json` 抽取业务口径。
