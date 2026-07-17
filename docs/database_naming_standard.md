# 日报数据库结构、关系与命名规范

## 1. 设计结论

数据库只保留三种共享关系：日报源记录、标准日报、作业时段。它们确实由钻井、完井、修井、搬迁四类日报共同使用。库存、泥浆材料、射孔井段等明细必须归属具体日报类型，不得再放进无类型约束的 `common` 表。

`dpr` 表示 daily operations report（日常作业日报），不是 daily production report。数据库中不再创建任何 `dpr_common_*` 物理表；历史名称只允许出现在启动迁移的别名清单中。

## 2. 核心关系

```text
dpr_report_record（来源、处理状态、原始业务标识）
├── dpr_report_field（1:1，原始单值字段 JSON）
├── dpr_report_row（1:N，原始明细行 JSON）
├── translation_content（1:N，字段译文）
├── ai_extraction_result（1:N，AI 提炼结果）
└── dpr_report（1:1，强类型日期、日报号和主数据关系）
    ├── dpr_report_summary（1:1，四类日报都存在的摘要字段）
    ├── dpr_operation（1:N，四类日报格式一致的作业时段）
    │   └── dpr_operation_classification（1:1，NPT/SC/责任方确认）
    ├── dpr_<type>_report（1:1，各日报类型专属字段）
    └── dpr_<type>_<detail>（1:N，各日报类型专属明细）
```

`dpr_report_record.record_id` 是外部稳定业务 ID；`dpr_report.id` 是标准层数值主键。所有标准明细使用 `daily_report_id` 关联 `dpr_report.id`，并通过 `daily_report_id + source_row_no` 保证来源行唯一。

## 3. 四类日报表清单

| 日报类型 | 一对一专属表 | 一对多专属表 | 共享但有明确业务原因的表 |
|---|---|---|---|
| 钻井 | `dpr_drilling_report`、`dpr_drilling_fluid_property` | `dpr_drilling_directional_survey`、`dpr_drilling_bha_component`、`dpr_drilling_fluid_loss`、`dpr_drilling_bulk_inventory` | `dpr_report`、`dpr_report_summary`、`dpr_operation` |
| 完井 | `dpr_completion_report` | `dpr_completion_bulk_inventory`、`dpr_completion_mud_product`、`dpr_completion_perforation_interval` | `dpr_report`、`dpr_report_summary`、`dpr_operation` |
| 修井 | `dpr_workover_report` | `dpr_workover_bulk_inventory`、`dpr_workover_mud_product`、`dpr_workover_perforation_interval` | `dpr_report`、`dpr_report_summary`、`dpr_operation` |
| 搬迁 | `dpr_move_report` | 无 | `dpr_report`、`dpr_report_summary`、`dpr_operation` |

### 钻井日报

- `dpr_drilling_report`：井深、进尺、套管、地层测试、BOP、泵参数、钻柱重量、离底/井底扭矩、钻头和 BHA 标识、HSE 标志。
- `dpr_drilling_fluid_property`：泥浆取样、密度、温度、流变、失水、油水比、含砂和 ECD。
- `dpr_drilling_directional_survey`：MD、Incl、Azi、TVD、VS、N/S、E/W、DLS、Build。
- `dpr_drilling_bha_component`：组件、内外径、根数和长度。
- `dpr_drilling_fluid_loss`：注入量和返出量。
- `dpr_drilling_bulk_inventory`：钻井日报散装料期初、接收、使用和期末数量。

### 完井日报

- `dpr_completion_report`：说明、开工日期、成本、监督/工程师/地质师、人数和安全备注。
- `dpr_completion_bulk_inventory`：完井散装料库存。
- `dpr_completion_mud_product`：完井泥浆产品收、用、退、存。
- `dpr_completion_perforation_interval`：完井射孔地层、顶底深、孔密、弹型、相位、日期和状态。

### 修井日报

- `dpr_workover_report`：修井编号、说明、开工日期、成本、人员和安全备注。
- `dpr_workover_bulk_inventory`：修井散装料库存。
- `dpr_workover_mud_product`：修井泥浆产品收、用、退、存。
- `dpr_workover_perforation_interval`：修井射孔井段；与完井分表，禁止跨类型误写。

### 搬迁日报

- `dpr_move_report`：地面海拔、AFE 设计天数、搬迁进度、安装进度、当日/累计/计划载荷数和井号前缀。
- 搬迁模板中空置的 MD、进尺、旋转时长只在原始 JSON 留痕，不进入搬迁标准事实。

## 4. 功能模块与数据归属

| 功能模块 | 读取/写入的正式表 |
|---|---|
| PDF 导入、日报编辑 | `dpr_report_record`、`dpr_report_field`、`dpr_report_row`，同事务同步标准表 |
| 日报翻译 | `translation_content`、`translation_memory`、`translation_revision` |
| AI 数据提炼 | `ai_extraction_result` |
| NPT 确认 | `dpr_operation`、`dpr_operation_classification`、规则及修订表 |
| 生产进度与效率 | `dpr_report`、`dpr_operation`、`biz_job_depth_progress` 和统计视图 |
| 作业里程碑 | `biz_job_event` |
| HSE 事件 | `hsse_incident`；只有来源明确为事故时才创建 |
| 数据治理 | `dq_issue`、`md_*`、`rel_*`、`biz_job` |

`biz_job_event`、`biz_job_depth_progress` 属于作业实例，不属于“公共日报事实”；`hsse_incident` 属于 HSE 域；`dq_issue` 属于数据质量域，所以均不使用 `dpr_common` 前缀。

### 主数据、项目和作业关系

```text
md_project
├── rel_project_team_assignment ── md_team ──< md_rig
├── rel_project_well_scope ─────── md_well
└── biz_job（项目 + 井 + 作业类型 + 序次）
    ├── rel_job_rig_assignment ─── md_rig
    ├── biz_job_event
    └── biz_job_depth_progress
```

- 日报只有在“井、队伍、日期”完整，并且日报日期同时落在项目-队伍与项目-井的有效期内时，才自动绑定项目；仅凭井号相似或队号相同不得猜项目。
- `md_alias` 必须保存来源系统和确认状态。日报中的新井号只尝试匹配已确认别名，不得反向自动创建主数据。
- `dpr_report` 通过 `project_id`、`job_id`、`rig_id`、`well_id` 关联治理层；匹配失败仍保留日报，并在 `dq_issue` 中登记。
- 同一项目、同一井在同一天由“搬迁”切换到“钻井”等不同作业阶段时，可以存在两个 `biz_job`；日级精度下的同井钻机关系不视为资源冲突。不同井或不同项目的钻机有效期重叠仍是错误。
- 项目资源冲突以 `rel_project_team_assignment` 为准；`rel_project_rig_assignment` 只保留旧接口兼容，不重复生成同一批质量问题。
- 项目关系使用左闭右开的有效期 `[valid_from, valid_to)`，避免相邻班次或项目交接在边界日重复命中。

## 5. 强类型和审计规则

- 原始 JSON 永久保留来源文本；标准化失败不得删除原始日报。
- 标准日期、时间、金额和工程量使用 `DATE/TIME/DATETIME/DECIMAL`，解析失败保存 `NULL` 并创建质量问题，禁止用 0 伪装成功。
- 字段单位写入列名和注释，例如 `_ft`、`_in`、`_psi`、`_ppg`、`_usd`。
- 作业跨午夜时结束时间进入次日；单行工时必须在 0 到 24 小时之间。
- 射孔底深不得小于顶深；测斜角、方位角、搬迁进度和库存数量使用数据库约束。
- 库存来源缺少接收量或单位时标记 `NOT_CHECKABLE`，不得强行判定平衡或不平衡。
- 每个标准事实保存 `source_hash`、创建/更新人和时间；人工分类另存修订历史。

## 6. 迁移规则

启动迁移先把历史表原地改名，再按 `dpr_report.report_type` 将历史库存、泥浆材料和射孔行拆入类型专属表。迁移必须满足：

1. 日报、作业、分类、译文和质量问题行数不变；
2. 类型专属明细拆分后的行数之和等于迁移前行数；
3. 不存在无法识别日报类型的明细行；
4. 所有外键、唯一键、检查约束和统计视图可重新创建；
5. 迁移完成后不存在 `dpr_common_*` 物理表。
