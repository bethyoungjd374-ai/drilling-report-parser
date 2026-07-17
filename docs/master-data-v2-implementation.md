# 主数据 V2 实施说明

## 当前落地范围

本次改造保留原始 JSON 审计数据，并将原始日报物理表规范为 `dpr_report_record`、`dpr_report_field`、`dpr_report_row`。同一 MySQL 中包含主数据、有效期关系、作业实例、标准事实、质量问题和时间分类规则；旧生产统计及 NPT 接口继续可用。

日报保存后的处理链为：

1. 保存原始日报和活动行；
2. 通过确认别名解析标准队伍和井；
3. 按显式作业、井级范围、井队派遣的优先级确定唯一项目；
4. 写入日报、活动、井深、事件、事故等标准事实；
5. 执行规则分类并生成质量问题。

有效期统一采用 `[valid_from, valid_to)`。同一井级精确关系优先于井队级关系；零匹配为 `UNASSIGNED`，多匹配为 `AMBIGUOUS`，不会复制事实行。

## 功能开关

```dotenv
DRP_MASTER_DATA_V2=true
```

## 迁移与核对

正式迁移：

```bash
.venv/bin/python scripts/migrate_master_data_v2.py \
  --table4 "/path/to/表4.xlsx" \
  --table5 "/path/to/表5.xlsx" \
  --table6 "/path/to/表6.xlsx"
```

增加 `--dry-run` 可预演并回滚事务。脚本按 `batch_code` 和来源定位哈希幂等执行，重复运行不会新增主数据、关系或事实。需要回滚本批次时使用：

```bash
.venv/bin/python scripts/migrate_master_data_v2.py --rollback master-data-v2-2026
```

## 后台模块与数据归属

后台按业务职责拆分，禁止出现同一关系的两个正式维护入口：

- “主数据管理 / 实体数据”：只显示国家或区域、公司、油田、区块、队伍、井 6 类。钻井队和修井队统一维护为“队伍”，通过队伍类型区分，并在队伍上维护设备型号；不再单列“钻机”和“修井机”入口。井轨迹及设计井深属性直接维护在“井”上，不再设置独立井筒主数据。已有设备表及 `rig_id` 仅保留历史日报兼容用途。属性参考 OSDU 的稳定 ID、Master Data 与 Reference Data 分层思想做精简落地，旧合同、项目、设备型号等表仅保留兼容用途，不再作为本页主数据类型展示。6 类实体均提供删除操作：未被引用时物理删除；存在下级主数据、项目关系、日报事实或别名引用时拒绝删除并显示引用来源，此时须先解除引用或改为停用。
- “主数据管理 / 附录”：维护下拉选项类别和枚举值，对应 `md_appendix_category`、`md_appendix_value`。类别和值都有稳定编码、父级、层级、状态和审计字段；实体表保存枚举编码，不保存页面显示文字。附录类别和值同样支持带引用校验的删除。
- “项目与队伍”：按项目集中维护队伍派遣和项目井范围，对应 `rel_project_team_assignment`、`rel_project_well_scope`。钻机、修井机属于设备，项目归属使用队伍，不再直接使用设备。关系采用 `[valid_from, valid_to)`，保存前统一检查跨项目重叠。
- “数据标准化”：维护 `md_alias`、质量问题和时间分类规则。别名是解析规则，不再作为实体基本属性显示。

项目关系字段统一如下：

- 队伍派遣：`project_id`、`team_id`、`valid_from`、`valid_to`、`service_discipline`、`assignment_note`、`priority`、`status`、`change_reason`、`version`。
- 项目井范围：`project_id`、`well_id`、`job_type`、`scope_note`、`valid_from`、`valid_to`、`status`、`change_reason`、`version`。
- `assignment_note/scope_note` 保存业务说明；`change_reason` 只保存本次变更的审计原因，两者不得混用。

“项目与队伍”使用批量接口 `POST /api/admin/project-relationships` 在单个数据库事务中保存一个项目的全部关系。正式数据写入成功后，系统自动由 MySQL 生成只读兼容版 `project_team_config.json`；旧 JSON 不再是关系维护来源。

主数据、关系、质量问题和分类规则接口均使用现有登录与权限体系。写操作要求管理员权限，并写入创建人、修改人、原因、版本号及后台审计日志。并发更新必须提交 `version`，版本不一致返回冲突。

## 暂缓范围

后台暂不建设月报生成、冻结、重开和 Excel 导出模块。相关页面、接口和运行时服务已经移除；后续重新启动月报建设时，应基于已经治理完成的标准事实和唯一项目归属另行设计。
