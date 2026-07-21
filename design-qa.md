# Design QA — 月报月份选择器

- Source visual truth: 当前任务中的用户附件（月选择器参考图；会话内图片，无本地文件路径）
- Implementation screenshot: `/Users/jason/Documents/GitHub/drilling-report-parser/outputs/monthly-month-picker-compact-qa.png`
- Viewport: 1892 × 1137
- State: 钻井基础指标数据月报表，2026 年月份选择器展开，当前月份 7 月选中

## Full-view comparison evidence

实现保留了参考图的核心结构：带日历图标的月份触发框、年份标题、左右年份切换、3 × 4 月份宫格、蓝色选中态以及灰色禁用态。控件尺寸按现有月报工具栏的紧凑密度等比收敛；触发框为 148 × 36 px，弹层为 270 × 203 px，未改变相邻项目、队伍和操作按钮的既有布局。

## Focused region comparison evidence

参考图本身即为月份选择器的聚焦视图；实现截图中的展开弹层尺寸足以清晰检查标题、导航、12 个月份状态和选中态，因此不需要另做放大裁切。

## Required fidelity surfaces

- Fonts and typography: 沿用系统现有中文无衬线字体；年份使用更大加粗层级，月份文本字重和参考图一致，未出现截断或换行。
- Spacing and layout rhythm: 年份栏与月份宫格分区明确；月份使用 3 列 4 行等距网格；圆角、阴影和触发框焦点态与现有系统组件协调。
- Colors and visual tokens: 白色弹层、深色正文、灰色禁用态和系统蓝色选中态均与参考图一致，并复用现有品牌蓝色。
- Image quality and asset fidelity: 日历及年份导航使用项目既有 SVG 图标资产，显示清晰，无位图模糊、占位图或自绘图标替代。
- Copy and content: 使用“请选择月份”“2026年”“1月–12月”；触发框显示 `YYYY年MM月`，符合参考图表达。

## Interaction verification

- 三个月报均可展开同一月份宫格组件。
- 钻井月报 2026 年仅 4–7 月可点；2025 年仅 8–10 月可点，其余月份禁用。
- 修井月报 2026 年仅 5–7 月可点。
- 钻修井时效月报 2026 年仅 4–7 月可点。
- 下一年在当前年份禁用；历史年份可通过“上一年”进入。
- 选择 2025 年 8 月后，触发框显示 `2025年08月`，填报时间显示 `2025年8月31日`；查询后返回 PCND-034 数据。
- 页面控制台无 error 或 warning。

## Findings

没有可执行的 P0、P1 或 P2 差异。

## Comparison history

- Pass 1: 首版月份宫格功能和状态正确，但弹层相对现有筛选控件偏宽、标题栏与月份按钮偏松散，记录为 P2 密度不一致。
- Pass 2: 将弹层从 330 px 收紧为 270 px，标题栏从 52 px 收紧为 40 px，月份按钮从 42 px 收紧为 32 px，并统一 7 px 圆角及较轻阴影。复测后与项目/队伍筛选控件的密度和视觉语言一致，P2 已关闭。

## Follow-up polish

- 无必须处理的 P3 项。

final result: passed
