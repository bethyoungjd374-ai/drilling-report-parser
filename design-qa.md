# Design QA

## Scope

- Feature: unified translation tuning workspace
- Route: `http://127.0.0.1:8081/admin/`
- Primary reference: `/Users/wujianhui/Downloads/ChatGPT Image Jul 10, 2026, 05_16_36 PM (5).png`
- Supporting references:
  - `/Users/wujianhui/Downloads/ChatGPT Image Jul 10, 2026, 05_16_36 PM (4).png`
  - `/Users/wujianhui/Downloads/ChatGPT Image Jul 10, 2026, 05_16_35 PM (3).png`
  - `/Users/wujianhui/Downloads/ChatGPT Image Jul 10, 2026, 05_16_33 PM (2).png`

## Verification State

- Authenticated as the local administrator.
- Opened the `Translation Tuning` navigation item.
- Switched between `Fields & Prompt`, `Terminology`, and `Test Workbench`.
- Saved the tuning strategy and confirmed that the page reloaded it.
- Ran one real model translation in the workbench without starting a batch job or writing report translations.
- Checked desktop and narrow viewports.
- Checked the browser console: no errors.

### Annotation follow-up

- Added exact translation scope rules for report type, module, and field.
- Added the pending-report selection modal with continue and overwrite modes.
- Added Excel terminology import, AI extraction, duplicate review, and explicit overwrite selection.
- Verified the updated page in an isolated DOM runtime: the tuning panel rendered, dependent selects updated, the queue modal opened with records, and the Excel import control was present.
- The configured public model parsed two complete synthetic terminology pairs from a flexible three-language worksheet layout.
- Live in-app browser reload was blocked by the local URL policy during this pass, so the previous visual screenshots remain the latest browser-rendered evidence.

### Terminology follow-up

- Used the 1288 x 895 annotated terminology screenshot as the source for the layout correction.
- Removed the always-visible term detail editor and moved add/edit into one focused modal.
- Replaced legacy technical categories with operation-type categories: general, drilling, completion, workover, and move. Categories are organizational only; enabled terms remain global translation rules.
- Added search, operation-type filtering, 10/20/50-row pagination, Excel template download, and Excel export.
- Reworked global protections into a full-width three-column section below the table.
- Isolated DOM verification passed for 10-row pagination, template/export links, modal editing, five operation types, and the protection layout.
- Template and export endpoints returned valid two-sheet workbooks. A real template upload returned two duplicate review items and did not add test data.

### Terminology toolbar follow-up

- Used the 1288 x 895 annotated toolbar and pagination screenshots as the source of truth.
- Kept only import/export/create commands in the heading and moved search into a dedicated table toolbar.
- Replaced the full-width operation-type select with a compact six-option segmented filter.
- Set pagination controls to fixed flex sizing, a 74px minimum button width, and no-wrap labels.
- Isolated DOM and computed-style verification passed for search position, six filter segments, filtering behavior, and pagination sizing.
- Live in-app browser verification passed on `http://127.0.0.1:8081/admin/`: toolbar actions, six-segment filtering, search, 20-row page size, add-term modal, and template/export xlsx endpoints.

## Visual Evidence

- Full-view source comparison: `outputs/ui-qa/translation-test-result-comparison.png`
- Test workbench result: `outputs/ui-qa/translation-tuning-test-result.png`
- Field and Prompt configuration: `outputs/ui-qa/translation-tuning-fields-final.png`
- Terminology list and editor: `outputs/ui-qa/translation-tuning-terms-final.png`
- Terminology toolbar browser verification: `outputs/ui-qa/translation-tuning-terms-browser-final.png`
- Narrow viewport: `outputs/ui-qa/translation-tuning-mobile.png`
- Reference viewport: 1672 x 941
- Implementation viewport: 1724 x 998; normalized to the reference size for comparison

## Comparison Review

- Layout: preserves the reference's dense administration layout, two-column test workspace, prompt preview, output validation, and list-plus-detail editing pattern.
- Typography: matches the existing application's type scale and density; control text was reduced from an overly bold first pass.
- Spacing: sections align to the existing admin grid and remain readable without horizontal overflow.
- Color: retains the product's existing dark navigation and blue action language, with green reserved for successful model validation.
- Assets: keeps the existing icon family; the referenced administrative screens do not require raster imagery.
- Copy: labels are specific to report translation and avoid generic AI-skill terminology.

## Intentional Deviations

- Combined field translation settings, terminology mapping, and model testing under one `Translation Tuning` menu.
- Kept model connection settings separate because credentials, endpoints, and availability are infrastructure concerns.
- Omitted generic skill version publishing, schema builders, test baselines/history, and daily-report Excel storage/export because they do not support the current translation workflow. Excel is used only as a terminology import source.
- Restricted configurable fields to known textual report fields so identifiers, dates, depths, and numeric values cannot accidentally be translated.

## Iterations

1. Initial implementation matched the reference structure but used overly heavy form text and allowed the terminology table to push the editor below the first viewport.
2. Reduced input/body font weight, constrained the terminology list with a sticky header, and rechecked all three tabs.
3. Replaced the fixed field table with a compact scope builder, added queue and duplicate-review modals, and verified their interaction contracts in an isolated page runtime.

## Findings

- P0: none
- P1: none
- P2: none remaining

Final result: passed

---

## Navigation redesign follow-up

Result: passed

## Source truth

- Selected concept: `/Users/jason/.codex/generated_images/019f5a7b-28d2-7422-af93-3038758ff9a6/exec-026b5cdc-f3ed-4190-8585-714a41b78d6e.png`
- Implementation screenshots: `design-qa-front.png`, `design-qa-admin.png`
- Same-state comparisons: `design-qa-full-comparison.png`, `design-qa-sidebar-comparison.png`
- Browser viewport: 1959 × 1137 CSS px; Chinese locale; first menu item active; all menu groups expanded.

## Visual comparison

- P0: none. Both front and admin navigation render and remain usable.
- P1: none. Selected concept hierarchy, navy palette, outline icon family, cyan active marker, group dividers, and bottom system action are implemented.
- P2: none. Front and admin computed typography and spacing match exactly: group 13px / 42px, item 12px / 40px, group padding 8px 9px, item padding 6px 10px 6px 13px, sidebar padding 16px 12px, width 224px.
- P3: the selected concept uses a visually wider sidebar and larger density than the existing product viewport. The implementation intentionally keeps the established 224px product grid while preserving the selected visual language.

## Interaction and asset checks

- Front group collapse/reopen: passed.
- Front navigation active-state switch and restoration: passed.
- Admin group collapse/reopen: passed.
- Admin tab active-state switch and restoration: passed.
- Chinese / Spanish menu label switching: passed.
- Front icons: 17/17 loaded; admin icons: 17/17 loaded.
- Browser console errors on checked front/admin states: none.

---

## 月度时效报表列精简与译文切换

Final result: passed

### Source visual truth

- `browser:Selected browser region`（本轮 Browser Comment 1，右侧辅助列删除范围）
- `browser:非生产原因`（本轮 Browser Comment 2，中文切换使用对应译文）
- Reference viewport: 1959 × 1137 CSS px，月度时效报表，2026 年 7 月。

### Implementation evidence

- Full-view screenshot: `/Users/jason/Documents/GitHub/drilling-report-parser/outputs/monthly-efficiency-columns-translation-qa.png`
- Horizontal table-state screenshot: `/Users/jason/Documents/GitHub/drilling-report-parser/outputs/monthly-efficiency-right-columns-qa.png`
- Browser-rendered route: `http://127.0.0.1:8080/web_form/`

### Full-view comparison

- The existing report hierarchy, filters, KPI cards, section spacing, typography, colors, table density, sticky first column, and interaction behavior remain unchanged.
- The table now has 31 columns. The annotated auxiliary columns `Other Remarks`, `日报数`, `来源状态`, and `待定字段` are absent; the final group contains only `非生产原因` under `原因说明`.
- The four removed columns were also removed from the Excel export so the screen and exported report remain structurally consistent.

### Focused region comparison

- Chinese locale (`html[lang=zh-CN]`): populated `非生产原因` cells render completed `zh-CN` operation translations from the existing translation store. Live sample begins `起出BHA #2定向钻具组合…`.
- Spanish locale (`html[lang=es]`): the same cell returns to the original report text. Live sample begins `BAJA BHA #3 DD…`.
- Switching back to Chinese restores the translated text without another page load.

### Required fidelity surfaces

- Fonts and typography: unchanged from the existing report; header and body hierarchy remain consistent.
- Spacing and layout rhythm: the group-header colspan was reduced from five to one, eliminating the annotated empty auxiliary region without changing neighboring column rhythm.
- Colors and visual tokens: existing navy group header, pale column header, borders, pending pills, and hover tokens preserved.
- Image quality and assets: no image or icon changes were required.
- Copy and content: `来源与说明` is now the accurate `原因说明`; Chinese/Spanish non-production descriptions follow the active interface language.

### Interaction and technical checks

- Language switch Chinese → Spanish → Chinese: passed.
- Removed-column DOM check: passed; no forbidden headers present.
- Populated Chinese translation check: passed.
- Populated Spanish source-text check: passed.
- Browser console errors: none.
- Automated tests: 299 passed, 16 skipped.

### Comparison history

1. Source state contained four unwanted auxiliary columns and always displayed source-language non-production descriptions.
2. Removed the four columns from screen/export, reused source-hash-validated operation translations, and corrected group-header sizing.
3. Post-fix browser verification found no remaining P0, P1, or P2 issue.

### Findings

- P0: none.
- P1: none.
- P2: none.
- P3: very long translated reasons remain intentionally clamped to two lines with the full text available in the cell title, matching the existing dense-report pattern.

---

## 月度时效报表日期区间与导出一致性

### Source visual truth

- `browser:统计月份`（Browser Comment 1：改为日期区间，默认不限日期）
- `browser:monthly-efficiency-toolbar`（Browser Comment 2：筛选栏等宽协调）
- `browser:导出Excel`（Browser Comment 3：导出当前表格内容并跟随界面语言）
- Reference viewport: 1959 × 1137 CSS px，月度时效报表筛选区。

### Implementation evidence

- Browser-rendered screenshot: `/Users/jason/Documents/GitHub/drilling-report-parser/outputs/monthly-efficiency-date-range-final.jpg`
- Implementation viewport: 1600 × 900 CSS px；按相同桌面断点和页面状态与参考图进行比例归一化比较。
- Route: `http://127.0.0.1:8080/web_form/`
- State: 中文界面、日期起止均为空、全部项目/井队/专业、第一页。

### Full-view comparison evidence

- 保留现有页面标题、KPI、报表主体、表格密度和导航结构，仅替换被标注的筛选控件与导出行为。
- 两个日期控件、项目、井队、专业类型、井号使用六个等权栅格列；在桌面宽度下边缘对齐、间距统一，操作按钮保持独立固定宽度。
- 日期为空时状态徽标显示“全部日期”，并展示数据库中全部主数据已匹配且标准化的有效日报数据。

### Focused region comparison evidence

- 日期筛选：默认两个日期输入均为空；选择 `2026-06-01` 至 `2026-06-30` 后，界面显示 12 口井、66 份日报、NPT 83.00h、SC 39.00h；点击重置恢复全部日期的 26 口井、171 份日报、NPT 164.00h、SC 159.50h。
- 语言切换：中文表格显示中文列名与中文非生产原因译文；西语表格显示西语列名、`Perforación` 等专业名称与原始西语原因。
- 导出：工作簿列数与当前表格一致为 31 列，不含月份、合同号或已删除的辅助列；查询参数携带当前筛选、排序和界面语言；导出全部筛选结果，不受当前分页截断。

### Required fidelity surfaces

- Fonts and typography: 延续现有字体、字号、字重和控件标签层级；无新增字体或异常换行。
- Spacing and layout rhythm: 六个筛选字段等宽，12px 列间距和工具栏上下留白保持统一；KPI 与报表区域位置不变。
- Colors and visual tokens: 复用现有白色面板、蓝色主按钮、浅灰边框和焦点状态。
- Image quality and assets: 本次不新增图片或图标；现有品牌和导航资产未改动。
- Copy and content: “统计月份”改为“日期起/日期止”；空日期明确显示“全部日期”；进尺列相应改为“区间进尺/累计进尺”。

### Interaction and technical checks

- 默认不限日期：passed。
- 指定日期区间查询：passed。
- 重置恢复不限日期：passed。
- 中文/西语表格切换：passed。
- 中文/西语工作簿结构与内容：passed。
- 页面无错误提示，服务端请求无异常：passed。
- Automated tests: 301 passed, 16 skipped。

### Comparison history

1. 参考状态仅支持月份，加载时自动锁定最新月，筛选字段宽度不一致，导出还包含屏幕外辅助字段。
2. 首次实现将前后端改为可空日期区间，并统一筛选栅格；实际浏览器验证发现存储适配层仍保留旧月份参数。
3. 修正存储适配层并重启后，不限日期与六月区间均返回正确统计；中西语表格和工作簿通过复核。

### Findings

- P0: none.
- P1: none.
- P2: none.
- P3: none.

final result: passed

---

## 月度时效报表移除“批次”

### Source visual truth

- `browser:批次`（本轮 Browser Comment 1：月度时效报表中“批次”列的标注截图）。
- Reference viewport: 1666 × 1137 px；中文月度时效报表、全日期、全量数据状态。

### Implementation evidence

- Browser-rendered screenshot: `/Users/jason/Documents/GitHub/drilling-report-parser/outputs/monthly-efficiency-remove-batch-final-1666.jpg`
- Original browser capture: `/Users/jason/Documents/GitHub/drilling-report-parser/outputs/monthly-efficiency-remove-batch-final.jpg`
- Implementation viewport: 1666 × 1137 CSS px；截图按设备像素比归一化到 1666 × 1137 px。
- Route: `http://127.0.0.1:8080/web_form/`
- State: 中文界面、不限日期、全部项目/井队/类型，26 口井、171 份标准日报。

### Full-view and focused comparison evidence

- Full-view: 页面结构、筛选区、四项 KPI、报表标题、分组表头和明细密度保持不变；没有因删除一列产生空白或分组错位。
- Focused table comparison: 来源截图中“批次”位于“专业”与“日报覆盖起”之间；实现中“专业”后直接进入“日报覆盖起”，基础信息分组从 11 列同步收敛为 10 列。
- DOM evidence: 明细表表头 30 列、首行 30 个单元格；页面和表头均不包含“批次”或西语“Lote”。

### Required fidelity surfaces

- Fonts and typography: 表头字号、字重、行高和排序图标沿用现有表格规范，删除列后相邻标题无换行或层级漂移。
- Spacing and layout rhythm: 基础信息分组列数与明细严格对应，后续进度、时效、原因分组保持原宽度与节奏。
- Colors and visual tokens: 蓝色分组表头、浅灰列头、边框与斑马纹未变化。
- Image quality and assets: 本次无新增或替换图片、图标和品牌资产。
- Copy and content: “批次/Lote”从页面、接口、排序、导出和统计口径中移除；口径文案改为“作业实例”。

### Primary interactions and technical checks

- 月度报表导航、页面加载及全量查询：passed。
- 表头/首行列数一致，且无“批次/Lote”：passed。
- 中西语 Excel 导出列清单均不含“批次/Lote”：passed（自动化测试）。
- Console errors checked: 0。
- Automated tests: 301 passed, 16 skipped。

### Comparison history and findings

1. 来源状态包含没有分析价值的“批次”列，且当前 29 个作业实例的内部序号全部为 1。
2. 删除月报查询字段、接口字段、排序入口、页面列和双语导出列；基础信息分组列数与末列宽度索引同步更新。
3. 保留数据库内部作业实例序号，用于将来同一井重复同类作业的身份区分；该字段不再进入月报链路。
4. 浏览器复核未发现 P0、P1 或 P2 视觉/交互问题。

- P0: none.
- P1: none.
- P2: none.
- P3: none.

final result: passed

---

## 月度时效报表筛选框内提示

### Source visual truth

- `browser:Selected browser region`（本轮 Browser Comment 1：删除筛选框上方字段标题，仅保留框内提示）。
- Reference viewport: 1959 × 1137 CSS px，月度时效报表筛选工具栏。

### Implementation evidence

- Screenshot: `/Users/jason/Documents/GitHub/drilling-report-parser/outputs/monthly-efficiency-inline-filter-hints.jpg`
- Implementation viewport: 1600 × 900 CSS px；中文界面、不限日期、全量数据状态。
- Route: `http://127.0.0.1:8080/web_form/`

### Comparison evidence and fidelity surfaces

- 日期、项目、井队、专业类型、井号上方的可见标题均已删除；框内分别显示“不限日期、全部项目、全部井队、全部类型、输入井号”。
- 工具栏上下内边距收敛至 12px，五个筛选框和三个操作按钮保持同一基线。
- 字体、边框、焦点色、按钮、日历图标和表格区域均沿用现有设计体系；无图片或资产变化。
- 可访问名称保留在控件属性中，删除可见标题不会影响浏览器语义定位。

### Interaction checks

- 日期范围弹层展开、清除和关闭：passed。
- 项目、井队、专业类型、井号的框内提示：passed。
- 默认全量统计未变化：26 口井、171 份日报、NPT 164.00h、SC 159.50h。
- Automated tests: 301 passed, 16 skipped。

### Findings

- P0: none.
- P1: none.
- P2: none.
- P3: none.

final result: passed

---

## 月度时效报表单一日期范围控件

### Source visual truth

- `browser:Selected browser region`（本轮 Browser Comment 1：原两个独立日期控件合并为一个日期范围控件）。
- Reference viewport: 1959 × 1137 CSS px，月度时效报表筛选区。

### Implementation evidence

- Open-state screenshot: `/Users/jason/Documents/GitHub/drilling-report-parser/outputs/monthly-efficiency-single-date-range-open.jpg`
- Implementation viewport: 1600 × 900 CSS px；按同一桌面断点、中文界面和不限日期状态归一化比较。
- Route: `http://127.0.0.1:8080/web_form/`

### Full-view and focused comparison evidence

- 工具栏由两个独立日期输入收敛为一个与项目、井队、专业、井号同宽的“日期范围”控件，其余筛选和报表结构未变化。
- 默认闭合状态显示“不限日期”和既有日历图标；展开后在一个弹层中提供日期起、日期止、清除、确定。
- 弹层左对齐控件、宽度 380px，使用现有白色面板、蓝色按钮、浅灰边框和阴影体系；未引入新视觉资产。

### Required fidelity surfaces

- Fonts and typography: 沿用筛选标签和输入文字规格，日期值不会与图标重叠。
- Spacing and layout rhythm: 五个筛选字段使用等权栅格；弹层内部 12px 双列间距、14px 内边距和右对齐操作区。
- Colors and visual tokens: 沿用现有边框、焦点蓝、按钮和面板阴影。
- Image quality and assets: 复用项目已有 `calendar-stats.svg`，无替代图形或占位资产。
- Copy and content: 默认“不限日期”；中西语标签、日期范围文案及操作按钮均跟随界面语言。

### Interaction checks

- 展开/收起及点击外部关闭：passed。
- 起止日期应用并生成单一范围文本：passed。
- `2026-06-01` 至 `2026-06-30` 查询仍返回 NPT 83.00h / SC 39.00h：passed。
- 清除与页面重置恢复“不限日期”：passed。
- Automated tests: 301 passed, 16 skipped。

### Comparison history and findings

1. 原实现用两个并列原生日期输入，不符合单一控件要求。
2. 合并为单一触发器与日期范围弹层，保持原查询参数、重置和导出逻辑。
3. 浏览器复核未发现 P0、P1 或 P2 问题。

- P0: none.
- P1: none.
- P2: none.
- P3: none.

final result: passed
