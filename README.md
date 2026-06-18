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

## 解析策略

工具不依赖固定单元格坐标，而是采用两种规则：

1. 按字段标签查找相邻值，例如 `Current Ops`、`24-Hr Summary`、`Last Casing`、`Mud Type`。
2. 按表头识别明细表，例如 `From / To / Hrs / Op Code / Operation Details`、`Component / OD / ID / Jts / Length`。

这样可以兼容模板轻微位移、合并单元格、PDF 转 Excel 后的行列变化。

## 开发测试

```bash
python -m unittest
```

## 后续建议

拿到真实 Excel 样例后，应补充样例回归测试，并把 `parse_warnings` 中真实存在但未识别的字段加入字段或表格规则。
