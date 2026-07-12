# AI 工作流一致性审查

## 范围

- AI 数据提炼：规则配置、单日报试运行。
- 翻译调优：字段策略、待处理队列、继续/覆盖执行。
- NPT 统计：责任方 Service Line 目标单元格。

## 现状

1. 数据提炼只有规则 JSON 和试运行接口，没有持久化结果、后台任务、任务状态或规则版本失效机制。
2. 翻译已有记录级状态、规则版本、后台队列、失败原因、继续和覆盖模式；新日报入库后目前标记为 PENDING，不会自动执行。
3. NPT 统计直接读取作业行中的 service_line，当前没有提炼结果覆盖层，因此单元格只能显示原值或 `-`。
4. 两个后台页面的信息架构不一致：翻译使用三视图和队列弹窗，提炼使用规则列表、编辑表单和右侧试运行。

## 建议目标

- 两个模块统一为：`规则配置 / 任务队列 / 测试工作台`。
- 两个模块统一状态：`PENDING / QUEUED / IN_PROGRESS / COMPLETED / FAILED / STALE / NOT_REQUIRED`。
- 两个模块统一执行模式：`处理待办`与`覆盖重跑`。
- 每个模块独立配置“新日报自动执行”；数据提炼默认开启，翻译按现有业务决定默认值。
- 保存规则生成版本号。历史结果保留并标记 STALE，只有明确触发“按新规则覆盖重跑”后才替换。
- 覆盖过程原值继续可见；新结果成功后原子替换，失败时保留旧值并显示“更新失败”。

## 数据设计

- report_records 增加提炼任务摘要状态、进度、错误、版本和更新时间。
- 新建 ai_extraction_results，以 record_id、rule_id、source_section、source_row_no、target_field 为唯一键。
- 每条结果保存 source_hash、result_text、status、error、model_config_id、rule_version、attempt_count 和时间戳。
- NPT 查询按 record_id + operations row_no 关联结果，在查询层覆盖 service_line，不修改原始解析 row_json。

## 触发规则

1. 新日报上传或来源字段变化：匹配启用规则，有内容则自动 QUEUED；没有内容则 NOT_REQUIRED。
2. 保存规则：停止该模块未完成任务，生成新版本；旧结果显示 STALE，不立即产生批量模型费用。
3. 手动“处理待办”：执行 PENDING、FAILED、STALE，跳过当前版本已完成结果。
4. 手动“覆盖重跑”：选中日报/结果全部按当前版本重跑；成功后替换，失败保留旧值。
5. 服务重启：QUEUED/IN_PROGRESS 恢复为 QUEUED 并续跑，使用 generation 防止旧任务回写。

## NPT 单元格

- QUEUED：排队中。
- IN_PROGRESS：提炼中 + 进度。
- COMPLETED：结果值 + 已提炼；空结果显示“未识别”。
- FAILED：失败，可查看原因并重试。
- STALE：继续显示旧值，同时标记“规则已更新”。
- 重跑中/更新失败：继续显示旧值，避免表格内容闪空。

## 证据

- 01-ai-extraction.png：数据提炼规则与单日报试运行。
- 02-translation-tuning.png：翻译字段策略。
- 03-translation-queue.png：翻译待处理队列、继续与覆盖操作。
- 04-npt-service-line.png：NPT 责任方目标列当前为空。
