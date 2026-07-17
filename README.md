# 厄瓜多尔钻井日报解析与生产报表系统

系统用于解析海外厄瓜多尔油田钻井、完井、修井和搬迁日报，将结构化结果、翻译内容与AI提炼结果统一保存到 MySQL，并生成生产报表和NPT统计。Excel仅用于导入、导出和历史迁移，不作为运行时业务数据库。

当前根据用户提供的 PDF 模板识别了以下数据类型：

- `report_fields`：日报基础字段、井信息、作业摘要、井控、液压、人员、泥浆关键字段、事故字段等键值数据
- `operations`：24 小时作业明细
- `survey_data`：最后测斜数据
- `bit_record`：钻头记录
- `bit_parameters`：钻头运行参数
- `mud_products`：泥浆材料消耗
- `bha_components`：BHA 组件
- `fluid_losses`：钻井液注入量、返出量等漏失情况
- `bulks`：散装料/柴油等库存
- `raw_cells`：原始非空单元格审计记录
- `parse_warnings`：未识别字段或空表提醒
- `metadata`：解析元数据

## 命令行使用

```bash
python -m drilling_report_parser.cli /path/to/report.xlsx -o outputs/report_structured.xlsx
```

如果不传 `-o`，默认输出到当前目录的 `outputs/` 下。

## 本地上传页面

```bash
python -m drilling_report_parser.web_app --host 127.0.0.1 --port 8000
```

然后打开：

```text
http://127.0.0.1:8000
```

选择 `.xlsx` 或 `.xlsm` 文件上传后，浏览器会下载解析后的结构化 Excel。

## 钻井日报 Web 填报页面

项目还提供一个按 PDF 模板结构重新设计的 Web 填报页面，支持导入 PDF 日报自动预填和二次编辑：

```bash
python -m drilling_report_parser.form_server --host 127.0.0.1 --port 8080
```

然后打开：

```text
http://127.0.0.1:8080/web_form/
```

页面包含基础信息、作业摘要、井控与液压、测斜数据、泥浆数据、钻头与 BHA、作业明细、成本库存、事故备注等分区。固定界面支持中文和西班牙语；日报自由文本只提供原文和中文译文。前端会实时检查日期、井深、进尺、24小时作业合计、测斜范围、泥浆密度、BHA尺寸和HSE备注等基础限制规则，解析后的明细行不在页面中新增或删除。

PDF 导入按钮会把上传的日报发送到本地接口 `/api/import-pdf`，解析后填充到页面中预览。解析器按模块标题、字段标签和表头识别数据，不依赖固定页码或固定行号，当前已用两份样例 PDF 覆盖以下内容：

单个 PDF 可以包含连续多天的日报。导入时系统按“日报日期 + 井号 + 日报号”的身份变化自动拆分，重复页眉和无页眉续页会保留在同一份日报内；该逻辑统一适用于钻井、完井、修井和搬迁日报。如果同一井的某一天缺少井队，但同一 PDF 内其他日报的井队唯一且一致，系统会批内继承并在元数据中记录该回填。

入库前会严格核对基本信息中的 `Event` 与上传入口的日报类型。`DEV DRILLING` 和 `MAJOR RIG MOVE` 均使用钻井日报模板并归入钻井日报，日历再按 `Event` 区分钻井日和搬迁日；`DEV COMPLETION`、`WORKOVER` 分别归入完井、修井日报。缺少事件、无法判断、类型冲突或入口不匹配时，整份 PDF（包括合并 PDF 中已识别的其他日期）均不会入库。

- 抬头与基础字段：日期、井号、日报号、钻机、井深、进尺、作业摘要等
- 井控、液压、泥浆、钻头、BHA 基础字段
- `Survey Data`、`BHA Components`、`Operations`、`Bulks` 明细表
- HSE 事故状态、事故备注和其他备注

## 日报中文翻译

项目采用“前端静态国际化 + 后端字段级翻译内容表 + 可配置大模型异步翻译”的方案。系统菜单、按钮、标题、提示语由前端 `i18n` 语言包切换；日报原始结构化数据只保存一份；`Current Ops`、`Operation Details`、备注等自由文本的译文保存到独立的 `translation_content` 表。

字段级翻译表不会复制整份日报 payload，也不会翻译井号、日期、时间、深度、单位和文件名等业务标识。页面点击 `原文 / 中` 时，后端把 `translation_content` 里的中文译文覆盖到自由文本字段后返回；西班牙语只用于菜单、标题、字段名、单位和提示等固定界面。

译文只有在目标语言的全部自由文本字段都已完成、且 `source_hash` 与当前原文一致时才可展示。修改了待翻译字段会使原译文失效；只修改结构化数据不会无条件删除有效译文。

### 配置翻译模型

在 `系统后台 -> AI服务管理 -> 模型接入配置` 中维护公网 OpenAI-Compatible 接口、局域网模型或本机 Ollama。保存并测试默认模型后，点击 `翻译待处理` 才会批量调用模型；服务启动不会自动重试失败或待处理日报。`清空译文` 只重置翻译内容与状态，不删除原始日报。

### AI 任务停止、切换与继续

翻译和数据提炼任务统一遵循以下运行规则：

1. `QUEUED / IN_PROGRESS` 表示任务运行中。此时只能查看进度或停止任务，不能切换默认模型、修改翻译策略或修改提炼规则。
2. 点击“停止翻译”或“停止提炼”后，已完成结果保留，未完成日报标记为 `STOPPED`，不会在服务重启时自动执行。
3. 停止全部运行任务后可以切换默认模型。模型保存接口也会校验运行状态，防止绕过页面直接切换。
4. 切换完成后点击“继续未完成”，系统只补充未完成内容；提炼任务会跳过来源、规则版本均未变化的已完成结果。
5. 已经发出的模型 HTTP 请求无法从客户端撤回，但停止后其返回结果会被丢弃，且不会阻塞切换后新任务使用新的执行队列。

### 翻译调优

`系统后台 -> AI服务管理 -> 翻译调优` 将字段策略、Prompt、术语词库和测试工作台合并在一个入口：

- `字段与 Prompt`：按“日报类型 -> 模块/部分 -> 字段”新增精确翻译范围，并配置目标语言和数字/单位/缩写/专名保护规则。
- `术语词库`：维护全局生效的中英西映射、别名和锁定译法，作业类型只用于“通用、钻井、完井、修井、搬迁”分类管理。支持分页、Excel 导入导出和模板下载；标准模板优先直接解析，自定义布局由默认模型识别。重复项默认跳过，管理员复核后才能覆盖。
- `测试工作台`：选择已启用模型，用示例日报文本验证真实译文、最终 Prompt、耗时和质量检查；测试不写入日报数据库。

调优配置保存在本机 `outputs/translation_tuning.json`。Prompt 或范围规则变化后会生成新的版本号；旧版本译文会重新计入“待处理日报”。点击待处理卡片可查看明细，支持继续全部、勾选部分或清除选中译文后覆盖重译。

Excel 仅用于术语导入，不作为业务数据库或日报导出格式；日报数据仍只保存在 MySQL。

### 命令行使用本地 Qwen

Python 项目侧没有新增强制依赖，HTTP 调用使用标准库；本地翻译引擎推荐使用 Ollama/Qwen。

```bash
export DRP_TRANSLATION_ENGINE=ollama
export DRP_OLLAMA_URL=http://127.0.0.1:11434
export DRP_OLLAMA_MODEL=qwen3.5:9b
export DRP_TRANSLATION_TIMEOUT=120
export DRP_TRANSLATION_TARGET_LANGUAGES=zh-CN
```

术语词库配置由后台维护：

```text
系统后台 -> AI服务管理 -> 翻译调优 -> 术语词库
outputs/translation_terms.json
```

包内 `drilling_report_parser/translation/drilling_terms.json` 只作为默认种子。运行时接口会优先读取后台配置文件。

### 前端使用

启动填报页面：

```bash
python3 -m drilling_report_parser.form_server --host 127.0.0.1 --port 8080
```

打开 `http://127.0.0.1:8080/web_form/`，导入或打开钻井、完井、修井、搬迁日报后，可在原文和中文译文之间切换。已保存记录会通过 `/api/load-report` 携带 `lang` 参数读取当前语言数据；译文只读展示，不另存为独立日报记录。

后台翻译调优入口：

```text
http://127.0.0.1:8080/admin/
```

管理员登录后进入 `AI服务管理 -> 翻译调优`，可配置字段、Prompt、三语术语和测试模型输出。

大模型接入配置入口：

```text
系统后台 -> AI服务管理 -> 模型接入配置
```

模型配置支持公网或局域网的 OpenAI-Compatible 接口，以及本地 Ollama。保存默认启用模型后，日报翻译任务会优先使用后台配置；API Key 仅保存在本机 `outputs/ai_model_configs.json`，前端只显示掩码。连接测试会调用模型的最小请求，不写入业务数据。

### 后端接口

```http
GET /api/admin/translation-terms
POST /api/admin/translation-terms
GET /api/admin/translation-terms/template
GET /api/admin/translation-terms/export
POST /api/admin/translation-terms/import
POST /api/admin/translation-terms/import/resolve
GET /api/admin/translation-tuning
POST /api/admin/translation-tuning
POST /api/admin/translation-tuning/test
GET /api/admin/translations
POST /api/admin/translations/queue
POST /api/translate-report
```

`POST /api/translate-report` 请求体：

```json
{
  "target_language": "zh-CN",
  "payload": {
    "report_fields": {
      "currentOps": "ROP 18 m/hr while drilling 12.25 in section."
    },
    "operations": []
  }
}
```

### 命令行测试

仓库提供了一个英西混合样例：

```text
examples/mixed_drilling_report.json
```

运行翻译，默认目标语言为中文：

```bash
python3 -m drilling_report_parser.translate_cli examples/mixed_drilling_report.json -o outputs/mixed_translation.json
```

使用 Qwen/Ollama 翻译：

```bash
python3 -m drilling_report_parser.translate_cli examples/mixed_drilling_report.json \
  --engine ollama \
  --ollama-url http://127.0.0.1:11434 \
  --ollama-model qwen3.5:9b \
  -o outputs/mixed_translation_qwen.json
```

也可以直接读取 `.xlsx/.xlsm`、`.pdf` 或 `.txt`：

```bash
python3 -m drilling_report_parser.translate_cli /path/to/report.pdf -o outputs/report_translation.json
```

如果只想验证本地链路和术语保护，不启动翻译服务，可以使用：

```bash
python3 -m drilling_report_parser.translate_cli examples/mixed_drilling_report.json --engine noop -o outputs/mixed_translation_noop.json
```

`noop` 不做自然语言翻译，只执行语言识别、占位符保护和术语替换，适合开发回归测试。

### 翻译输出结构

输出 JSON 主要包含：

- `metadata`：翻译引擎、目标语言、条目数量、告警数量；
- `translation_content`：字段级翻译行，包含 `entity_type/entity_id/field_code/source_language/target_language/source_text/translated_text/source_hash/model_config_id/prompt_version/translation_status`；
- `translated_payload`：按原日报 payload 结构回填后的目标语言结果；
- `warnings`：翻译服务不可用、非翻译字段或无法识别语言等信息。

## 解析策略

工具不依赖固定单元格坐标，而是采用两种规则：

1. 按字段标签查找相邻值，例如 `Current Ops`、`24-Hr Summary`、`Last Casing`、`Mud Type`。
2. 按表头识别明细表，例如 `From / To / Hrs / Op Code / Operation Details`、`Component / OD / ID / Jts / Length`。

这样可以兼容模板轻微位移、合并单元格、PDF 转 Excel 后的行列变化。

## 开发测试

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m compileall -q drilling_report_parser scripts
node --check web_form/app.js
node --check web_form/admin.js
node --check web_form/login.js
```

### 代码结构

- `form_server.py`：HTTP 路由、权限校验和业务流程编排，不承载通用文件算法。
- `runtime_files.py`：配置原子写入、JSONL 追加、轮转和保留策略。
- `database_common.py`：MySQL 与历史 Excel 适配器共享的记录 ID、日报类型和 NPT 状态规则。
- `pdf_io.py`：钻井、完井、修井和搬迁解析器共享的 PDF 输入适配。
- `translation/service.py`：翻译引擎、翻译管线和质量校验。
- `translation/experience.py`：翻译失败原因诊断。
- `translation/experience_store.py`：经验建议的持久化、合并和状态流转。
- `web_form/http-client.js`：登录、前台和后台共用的同源 JSON 请求客户端。

业务模块新增能力时应优先放入相应领域模块，由 `form_server.py` 负责调用；避免继续把文件读写、状态归并或解析器公共能力直接写进 HTTP Handler。

## MySQL 本地数据库

当前运行时只使用 MySQL 保存日报、译文和 NPT 确认数据；旧版 Excel 文件库不再作为数据库写入或读取。Excel 解析、导出和历史数据迁移脚本仍保留。

### 1. 准备配置

复制示例配置为本地 `.env`：

```bash
cp .env.example .env
```

打开 `.env`，至少修改这两项密码：

```text
MYSQL_PASSWORD=你的普通用户密码
MYSQL_ROOT_PASSWORD=你的root密码
```

### 2. 启动 MySQL

如果使用 Docker：

```bash
docker compose --env-file .env up -d
```

phpMyAdmin 地址：

```text
http://127.0.0.1:8082
```

登录信息使用 `.env` 中的：

```text
服务器：mysql
用户名：drilling_user
密码：MYSQL_PASSWORD 对应的值
数据库：drilling_report_db
```

如果本机直接安装 MySQL，请先创建 `.env` 中配置的数据库和用户，然后执行 `db/init.sql` 初始化表结构。

### 3. 安装 Python 依赖

```bash
python3 -m pip install -r requirements.txt
```

### 4. 导入历史 Excel 数据

如果你手上还有旧版 Excel 数据库文件，可以手动迁移到 MySQL：

```bash
python3 scripts/migrate_excel_to_mysql.py --excel /path/to/old-report-database.xlsx
```

这个脚本不会被 Web 服务调用，只用于一次性历史迁移；相同 `record_id` 的日报会更新，不会重复插入。

### 5. 启动项目

```bash
python3 -m drilling_report_parser.form_server --host 127.0.0.1 --port 8081
```

打开：

```text
http://127.0.0.1:8081/web_form/
```

### 6. 验证数据已写入 MySQL

任选一种方式：

- 在页面导入或保存一份日报，然后在数据库工具中查看 `dpr_report_record` 表。
- 在 phpMyAdmin 执行：

```sql
SELECT record_id, report_type, report_date, wellbore, rig
FROM dpr_report_record
ORDER BY mysql_updated_at DESC
LIMIT 10;
```

### 7. 备份 MySQL 数据库

```bash
mkdir -p outputs/backups
docker compose --env-file .env exec mysql sh -c 'mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' > outputs/backups/drilling_report_db_$(date +%Y%m%d_%H%M%S).sql
```

### 8. 停止数据库服务

只停止容器，保留数据：

```bash
docker compose down
```

停止并删除 MySQL 数据卷（会清空数据库，谨慎使用）：

```bash
docker compose down -v
```

## 后续建议

拿到真实 Excel 样例后，应补充样例回归测试，并把 `parse_warnings` 中真实存在但未识别的字段加入字段或表格规则。
