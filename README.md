# 厄瓜多尔钻井日报 Excel 解析工具

这个工具用于解析海外厄瓜多尔油田 `DAILY OPERATIONS REPORT / REPORTE DIARIO DE PERFORACION` 模板导出的 Excel 文件，并把结构化数据输出到一个新的 Excel 工作簿中。输出工作簿按数据类型拆分为多个 sheet，暂时不依赖数据库。

当前根据用户提供的 PDF 模板识别了以下数据类型：

- `report_fields`：日报基础字段、井信息、作业摘要、井控、液压、人员、泥浆关键字段、事故字段等键值数据
- `operations`：24 小时作业明细
- `survey_data`：最后测斜数据
- `bit_record`：钻头记录
- `bit_parameters`：钻头运行参数
- `mud_products`：泥浆材料消耗
- `bha_components`：BHA 组件
- `daily_costs`：日成本
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

页面包含基础信息、作业摘要、井控与液压、测斜数据、泥浆数据、钻头与 BHA、作业明细、成本库存、事故备注等分区。界面支持中文、英文、西班牙语切换。明细表支持增删行，前端会实时检查日期、井深、进尺、24 小时作业合计、测斜范围、泥浆密度、BHA 尺寸、HSE 备注等基础限制规则。

PDF 导入按钮会把上传的日报发送到本地接口 `/api/import-pdf`，解析后填充到页面中预览。解析器按模块标题、字段标签和表头识别数据，不依赖固定页码或固定行号，当前已用两份样例 PDF 覆盖以下内容：

- 抬头与基础字段：日期、井号、日报号、钻机、井深、进尺、作业摘要等
- 井控、液压、泥浆、钻头、BHA 基础字段
- `Survey Data`、`BHA Components`、`Operations`、`Bulks` 明细表
- HSE 事故状态、事故备注和其他备注

## 中英西混合日报翻译

项目新增了一个本地翻译链路，位于 `drilling_report_parser/translation/`。它不会替换现有解析逻辑，而是在解析结果之后处理 `report_fields` 和各明细表单元格。前台通过右上角 `原文 / 中 / EN / ES` 切换显示语言：打开日报默认显示原始解析内容，点击 `中 / EN / ES` 后将静态 UI 和当前日报填报内容一起切换为目标语言；译文为只读预览，不写入 Excel 数据库，点击 `原文` 后恢复可编辑原始内容。

第一版默认适配本地 LibreTranslate 服务，不调用 ChatGPT、DeepSeek、Qwen 等通用大模型，也不调用外部商业翻译 API。翻译引擎通过环境变量配置，后续可以替换为 Argos Translate、OPUS-MT / MarianMT 等本地开源引擎。

### 启动本地翻译服务

Python 项目侧没有新增强制依赖，HTTP 调用使用标准库；本地翻译引擎由 LibreTranslate 容器提供。

```bash
docker run --rm -p 5000:5000 libretranslate/libretranslate
```

然后在另一个终端配置项目使用本地服务：

```bash
export DRP_TRANSLATION_ENGINE=libretranslate
export DRP_LIBRETRANSLATE_URL=http://127.0.0.1:5000
```

术语翻译配置由后台维护：

```text
系统后台 -> 业务配置 -> 术语翻译
outputs/translation_terms.json
```

包内 `drilling_report_parser/translation/drilling_terms.json` 只作为默认种子。运行时接口会优先读取后台配置文件。

### 前端使用

启动填报页面：

```bash
python3 -m drilling_report_parser.form_server --host 127.0.0.1 --port 8080
```

打开 `http://127.0.0.1:8080/web_form/`，导入或打开钻井、完井、修井、搬迁日报后，点击右上角 `中 / EN / ES`。页面会调用 `/api/translate-report`，将当前表单字段和明细表单元格替换为目标语言展示值，并进入只读预览态；保存、新增行、删除行会禁用。点击 `原文` 恢复原始草稿和编辑保存能力。

后台术语维护入口：

```text
http://127.0.0.1:8080/admin/
```

管理员登录后进入 `业务配置 -> 术语翻译`，可新增、编辑、启停、删除三语术语行。

### 后端接口

```http
GET /api/admin/translation-terms
POST /api/admin/translation-terms
POST /api/translate-report
```

`POST /api/translate-report` 请求体：

```json
{
  "target_language": "zh",
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
- `items`：逐字段或逐句的原文、识别语言、译文、未翻译 token、术语替换、告警；
- `translated_payload`：按原日报 payload 结构回填后的目标语言结果；
- `untranslated_fields`：井号、日期、井深、单位、缩写等被保护内容；
- `term_replacement_records`：如 `ROP -> 机械钻速`、`lost circulation -> 井漏`；
- `warnings`：翻译服务不可用、非翻译字段或无法识别语言等信息。

## 解析策略

工具不依赖固定单元格坐标，而是采用两种规则：

1. 按字段标签查找相邻值，例如 `Current Ops`、`24-Hr Summary`、`Last Casing`、`Mud Type`。
2. 按表头识别明细表，例如 `From / To / Hrs / Op Code / Operation Details`、`Component / OD / ID / Jts / Length`。

这样可以兼容模板轻微位移、合并单元格、PDF 转 Excel 后的行列变化。

## 开发测试

```bash
python -m unittest
```

## MySQL 本地数据库（Docker）

项目第一版数据库迁移采用“优先 MySQL、Excel 兜底”的方式：页面和接口保持原样，日报保存时仍会写入 `outputs/report_database.xlsx`，同时在 MySQL 可用时写入 MySQL。这样本地数据库出问题时，旧的 Excel 功能仍可继续使用。

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

### 2. 启动 MySQL 和 phpMyAdmin

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

### 3. 安装 Python 依赖

```bash
python3 -m pip install -r requirements.txt
```

### 4. 导入历史 Excel 数据

```bash
python3 scripts/migrate_excel_to_mysql.py --excel outputs/report_database.xlsx
```

这个脚本可以重复执行；相同 `record_id` 的日报会更新，不会重复插入。

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

- 在页面导入或保存一份日报，然后打开 phpMyAdmin 查看 `report_records` 表。
- 在 phpMyAdmin 执行：

```sql
SELECT record_id, report_type, report_date, wellbore, rig
FROM report_records
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
