# 日报数据验收与统计口径标准

更新日期：2026-07-18

## 1. 验收结论分层

日报验收分为三个互不替代的结论，任何页面或报告都不得混写：

1. **技术数据验收**：PDF 来源可追溯、日报已匹配和规范化、operation 逐行结构完整、时钟和时长有效、翻译状态与译文内容一致、事实表和视图可对账。
2. **正式统计就绪**：在技术验收通过的基础上，operation 的时效分类已经 `CONFIRMED` 或 `AUTO_CONFIRMED`。未确认行必须作为待复核工时单列，不能静默计入 P、SC、NPT 或效率指标。
3. **业务总体覆盖验收**：需由业务方给出明确项目、井队、井、日期范围及应报日历后才能判断缺报。测试库、部分上传批次或主数据尚未维护完整时，不从当前最早/最晚日报日期反推“应有完整月份”。

当前库的技术数据验收为 **PASS**；正式统计技术就绪为 **PASS**；业务总体覆盖为 **NOT_ASSESSED**。本轮 SC/NPT 确认用于系统验收，包含随机测试调整，不能替代业务负责人对真实责任和时效类型的最终签字。

## 2. 当前验收基线

| 项目 | 当前值 | 结论 |
|---|---:|---|
| 日报 | 172 份 | 全部 `MATCHED`、`NORMALIZED` |
| operation | 1,404 行 | 与分类表、结构化视图、统计时间线视图逐行相等 |
| 解析总工时 | 3,967.5 h | 所有 operation 时间校验为 `VALID` |
| 正式统计工时 | 3,967.5 h | 与解析工时守恒，统计就绪率 100% |
| 待分类复核 | 0 行 / 0 h | 确认队列已清零 |
| SC/NPT 验收样本 | 106 行 / 323.5 h | 97 行保持来源类型，9 行为带“测试调整”备注的模拟变更 |
| PDF 来源 | 172/172 可定位 | 1 个同名文件为内容完全相同的副本，不构成冲突 |
| 翻译 | 172/172 有译文内容 | LOBC-009 2026-04-23 的 `report_fields.otherRemarks` 已有中文译文 |
| 非 24 小时日报 | 14 份 | 均为当前连续日报段首尾边界，保留质量提示，不判作 operation 丢失 |
| 推导时长 | 1 行 / 12 h | ACAH-270H 2026-06-08 来源小时格为空，由 18:00–06:00 推导，标记 `CLOCK_DERIVED` |

按日报类型的工时如下：

| 日报类型 | 日报数 | operation 行 | 解析工时 | 正式工时 | 待复核工时 |
|---|---:|---:|---:|---:|---:|
| 钻井 | 79 | 686 | 1,830.5 | 1,830.5 | 0.0 |
| 完井 | 52 | 392 | 1,218.0 | 1,218.0 | 0.0 |
| 修井 | 40 | 323 | 895.0 | 895.0 | 0.0 |
| 搬迁 | 1 | 3 | 24.0 | 24.0 | 0.0 |

## 3. 统计口径冻结

### 3.1 数据范围

- 正式统计事实源只能是 `vw_rig_production_timeline`。
- 该视图只纳入 `normalization_status='NORMALIZED'` 且 `match_status='MATCHED'` 的日报。
- 未关联项目、井队、井或作业任务的日报不进入正式统计。这是业务规则，不是统计接口补造关系的理由。
- 日报日期按厄瓜多尔作业日理解，业务时区固定为 `America/Guayaquil`（UTC-5）；服务器时区不改变 `report_date` 的业务含义。

### 3.2 operation 粒度与时间

- 一条 `dpr_operation` 对应来源日报 operation 表的一行，以 `(daily_report_id, source_row_no)` 唯一。
- `hours` 是主统计时长。来源明示时为 `DECLARED`；仅在来源小时格为空且 FROM/TO 完整一致时允许 `CLOCK_DERIVED`。
- `time_validation_status` 必须为 `VALID` 才可统计。申报时长与钟表时长容差为 `0.05h`。
- 一级、二级工作分类分别存 `work_category_code`、`work_subcategory_code`。模板未提供的层级存 `UNSPECIFIED`，不能留空或塞回 JSON。

### 3.3 正式工时、P、SC、NPT 与效率

- `statistics_status='READY'` 的条件是：时间有效，且分类为 `CONFIRMED` 或 `AUTO_CONFIRMED`。
- 正式工时：`SUM(statistical_hours)`，只汇总 `READY` 行。
- 待复核工时：时间无效或分类未确认的 `hours`，必须在接口中同时返回数量和工时。
- P/SC/NPT 采用 `effective_op_type`，但 SC/NPT 来源值不能仅凭模板标签自动成为正式统计；需完成业务确认。
- 效率：`productive_hours / (productive_hours + included_nonproductive_hours)`；SC 排除工时不进分母。任一相关 operation 尚待复核时，单井/任务效率为 `NULL`，状态为 `PENDING_CLASSIFICATION` 或 `PENDING_TIME_REVIEW`。
- 聚合结果保留数据库精度，界面和导出按指标需要显示 2–3 位小数；不得对明细逐行先四舍五入再求和。

### 3.4 统计完整性

- 没有显式 `date_from`、`date_to` 时，接口返回 `completeness.assessed=false`，不制造缺报率。
- 有显式日期范围时，当前 `completeness` 只表示“范围内至少存在一份已匹配日报的日历日覆盖”，`coverage_basis=CALENDAR_DAY_WITH_ANY_MATCHED_REPORT`；它不是井队日、项目日或井日完整率。
- 要验收完整月份，后续需用项目—井队—井有效期关系生成明确的应报井队日清单，再与实际日报做差集。

## 4. 视图与接口责任

统计分析不新增快照统计表，保持“规范化事实表 → SQL 视图 → API”三层：

| 层 | 对象 | 责任 |
|---|---|---|
| 事实层 | `dpr_report`, `dpr_operation`, `dpr_operation_classification` | 保存可追溯、可复核的结构化事实与确认状态 |
| 质量门 | `vw_operation_structured` | 统一生成 `statistics_status`、`statistical_hours` |
| 统计时间线 | `vw_rig_production_timeline` | 只暴露已匹配、已规范化的 operation |
| 月度汇总 | `vw_monthly_rig_workload` | 对正式工时按月、项目、井队、工作桶聚合 |
| 任务效率 | `vw_job_efficiency` | 计算生产、非生产、排除、待复核工时和官方状态 |
| API | `/api/production-summary`, `/api/well-stats`, `/api/npt-stats` | 读取视图，不从日报 JSON 重算统计事实 |

API 已与视图对账：生产汇总总工时 3,967.5 h、NPT 164.0 h 与视图一致；NPT API 返回 46 条 NPT 明细、164.0 h，待分类复核为 0 行 / 0 h。接口与视图的数值守恒已通过，但其中 9 条类型调整是带备注的系统测试数据，正式业务使用前应由责任人复核或恢复为业务确认值。

## 5. 外部月报对账结论

`2026.6-厄子公司石油工程项目工作量统计表.xls` 覆盖 15 支队伍、10,183 h 的整月或预计工作量；当前库在这些队伍上的 6 月日报只覆盖 9 支队伍、1,529 h。两者范围不相等，因此当前不能做“总量必须相等”的统计验收，也不能用 8,654 h 差额判断解析错误。

`NPT.xlsx` 与 `NPT's RIG 220 Consolidado.xlsx` 是跨年度事件台账。可可靠解析到的 2026 年 6 月事件只有 SINOPEC 905 / SHSH-155 的 2 条、4 h，而当前日报库未覆盖对应日期，故没有可做逐事件对账的交集。

外部表当前用于三类检查：实体名称和关系参照、统计字段设计参照、未来完整批次的期望总体。323.5 h 分类流程已经完成；待上传范围与月报范围一致、且测试调整经业务复核后，再执行正式月度总量和 NPT 逐事件对账。

## 6. 自动回归执行

从项目根目录运行：

```bash
source .venv/bin/activate
python scripts/audit_data_acceptance.py \
  --source-root '/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料' \
  --output-dir outputs/data-acceptance-2026-07-18
```

脚本输出：

- `acceptance_snapshot.json`：机器可读的总体验收、约束对账、分类就绪率和逐日报结果。
- `report_acceptance.csv`：逐日报 PASS/REVIEW/FAIL 与问题代码。
- `external_monthly_workload_reconciliation.csv`：当前库与 2026 年 6 月工作量表的队伍级范围差异，仅用于覆盖分析。

技术验收出现 `FAIL` 时脚本返回非零退出码，可直接接入 CI。脚本同时校验统计视图守恒、待复核工时和 `CLASSIFICATION_PENDING` 质量问题生命周期；技术状态为 `PASS` 仍不替代业务总体覆盖和人工分类口径签字。
