# 日报解析与数据架构审计（2026-07-18）

## 结论

本轮确认并修正了三类高风险耦合：搬迁日报借用钻井类型导致重复入库、项目关系同时存在 MySQL 与 JSON 两套来源、统计接口在应用层拼接原始 JSON。当前正式链路统一为：

```text
PDF 独立模板策略
  -> 原始审计层（dpr_report_record / dpr_report_field / dpr_report_row）
  -> 标准事实层（dpr_report / dpr_operation / 类型专属事实）
  -> 独立叠加层（translation_content / ai_extraction_result）
  -> 数据库视图（vw_report_analytics / vw_rig_production_timeline）
  -> HTTP 响应与导出
```

原始 JSON 只用于追溯和重放；Operation 的分类、起止时间、时长、规范化描述、来源哈希和统计门禁均为强类型列。统计接口不建立统计结果表，只读取视图。用户备注属于业务事实，不属于统计结果，保存在结构化 `production_report_remark` 表。

## 各层审计结果

### 1. PDF 解析

- 钻井、完井、修井、搬迁四类入口现在分别注册解析器与存储类型，搬迁保存为 `move`，不再映射为 `drilling`。
- 钻井“原模板”和“兼容模板”由 `drilling_pdf_templates.py` 独立选择；兼容规则不修改原解析器。
- `pdf_import_service.py` 集中处理 Event 类型门禁、日报身份字段校验、合并 PDF 响应和批内井队继承；HTTP Handler 只负责编排。
- 新增业务唯一键 `(report_type, report_date, report_no, wellbore)`，重复导入复用正式记录，显式 ID 与业务身份冲突时拒绝写入。

### 2. 数据存储与 Operation 标准化

- `dpr_report_record/field/row`：保存来源、原字段和原表行，是可追溯层，不直接作为统计口径。
- `dpr_report`：保存日期、类型、项目、作业、队伍、井和匹配状态。
- `dpr_operation`：保存来源行号、FROM/TO 原文、标准时间、申报/钟表时长、跨日标志、时效校验状态、工作分类、OP Code/Sub、原始及规范化描述和描述哈希。
- `dpr_operation_classification`：保存生产属性、有效类型、工作量分类、计费状态、责任方、原因、服务线、规则版本和确认状态；人工修改另存 revision。
- 钻井、完井、修井、搬迁的专属字段继续写入各自强类型事实表，不合并成公共 JSON 大表。
- 未维护项目/队伍/井关系的日报保留为 `UNASSIGNED`，不会进入正式统计；这是主数据质量门禁，不是解析失败。

### 3. 翻译和 AI 提炼

- 原文只保存在原始层和标准事实层；译文只保存在 `translation_content`，按日报、实体、字段、目标语言和 `source_hash` 唯一关联。
- 读取中文时在响应阶段叠加译文；来源哈希或 Prompt 版本失效时不展示旧译文，也不覆盖原文。
- 人工译文修订保存在 `translation_revision`，可复用记忆保存在 `translation_memory`。
- AI 服务线等提炼结果保存在 `ai_extraction_result`，按来源哈希和规则版本判断是否可复用，不写回 Operation 原文。

### 4. 统计视图和接口

- `vw_operation_structured`：Operation 标准字段与分类口径，输出 `statistics_status/statistical_hours`。
- `vw_report_analytics`：日报级项目、合同、队伍、井、事件、AFE、质量和匹配状态。
- `vw_rig_production_timeline`：正式 operation 统计接口，关联以上两层并保留来源定位字段。
- 生产报表、时效分析和 NPT 接口统一通过 `load_analytics_view_rows` 读取视图；已删除运行时 Excel/原始 JSON 统计适配器。
- 月度工作量、钻井/修井基础指标和作业效率继续使用只读视图；没有新增统计快照表。

## 已退役和清理的内容

- `rel_project_rig_assignment`：14 行全部验证存在等价 `rel_project_team_assignment` 后退役；运行时只维护项目—队伍和项目—井关系。
- `monthly_report_snapshot/monthly_report_snapshot_row`：仅有 1 个 DRAFT 头和 3 个派生 JSON 行，功能与接口均已删除，改由视图实时查询。
- `project_team_config.json`、`/api/admin/project-teams` 及前后端兼容分支：正式关系只来自 MySQL；旧文件仅允许作为一次性迁移输入。
- 两条重复日报：删除 `drilling:TCHA-006I:2026-06-10:5`（保留独立 move 记录）和旧生成 ID `drilling:2026-07-15T18-07-14-00-00`（保留自然业务 ID）。随外键级联清理 13 条重复 Operation、13 条分类和 24 条译文。
- 运行时监控和翻译指标统一写入忽略的 `outputs/runtime/`；旧配置投影、服务日志和 PID 不再纳入版本控制；对应源 PDF 已移动到可恢复备份目录。
- 清理过程记录在 `migration_batch.batch_code = architecture-cleanup-20260718`（批次 ID 12），旧值和替代对象保存在 `migration_entry`。

清理后数据库为 172 条原始日报、172 条标准日报、1384 条 Operation、1384 条分类、2367 条翻译内容；raw/fact、operation/fact、classification/operation、translation/raw 孤儿均为 0，业务身份重复为 0。

主数据状态已重新计算为 89 条 `MATCHED`、81 条 `UNASSIGNED`、2 条 `AMBIGUOUS`，172 条事实均为 `NORMALIZED`。主数据缺失现在只影响归属和统计资格，不再误标为事实标准化失败。

## 保留对象及原因

- `migration_batch/migration_entry`：迁移审计和回滚证据，不是临时统计表。
- `translation_memory/revision`、分类规则/revision：分别承担可复用翻译和人工分类审计，不与正式内容表重复。
- `rel_job_rig_assignment`：作业实例的设备履历，语义不同于项目—队伍关系。
- `md_rig`：设备主数据和历史日报设备引用；项目归属仍以 `md_team` 为准。
- 当前为空的 HSSE、材料等类型表：已有明确页面或事实模型，属于可用业务能力，不按“空表”误删。

## 剩余工程风险

`form_server.py`、`translation/service.py` 和两个前端入口仍然偏大。当前已把 PDF 策略、模板兼容、主数据服务、Operation 标准化、数据库访问和运行时文件操作移出 Handler；后续新增功能应继续按领域拆分路由和页面组件，禁止重新引入文件数据库、应用层统计 SQL 或第二套主数据来源。大文件本身不作为删除依据，只有在接口边界和回归覆盖明确时再逐段迁移。
