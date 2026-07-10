# Drilling Report Parser — UI Redesign PRD

## Original Problem Statement
> 拉取这个项目看看，对整个系统的UI进行升级。
> Repo: https://github.com/bethyoungjd374-ai/drilling-report-parser
> Preference: 现代简约风格，主题自由发挥；升级范围 = 视觉 + 交互 + 布局重构。

## Product
厄瓜多尔油田钻完井日报分析系统 — 一套面向工程师、井队和管理员的企业级日报采集、
统计与分析工作台。功能覆盖钻井/完井/修井/搬迁四类日报的填报与解析、生产报表、
NPT 时效分析与确认、HSSE 管理、系统后台（账号/权限/项目/队伍/日志）。

## User Personas
1. **现场工程师** — 每日填报或从 PDF 导入日报，重点是表单密度和录入效率。
2. **数据统计员** — 使用生产/NPT 报表模块查看趋势与排名，需要图表清晰。
3. **系统管理员** — 通过 /admin/ 后台维护账号、角色、项目、系统配置与日志。

## Tech Stack
- **Backend**: Python `http.server` (`drilling_report_parser/form_server.py`), reused
  behind a FastAPI proxy (`/app/backend/server.py`) that spawns it on `127.0.0.1:8090`
  and forwards all traffic. Serves under `uvicorn` on `:8001`.
- **Frontend**: Pure HTML/CSS/JS in `/app/web_form/`. Served on `:3000` via a minimal
  Node/Express static server (`/app/frontend/server.js`) that also proxies
  `/api /login /admin` to the backend.
- Excel/PDF parsing: `openpyxl`, `pdfplumber`, `pypdf` (loaded from
  `/app/drilling_report_parser`).

## Redesign Goals (completed)
1. Replace old liquid-glass, over-bold, over-crowded look with a Swiss / Control-Room
   modern minimalist system.
2. Introduce a coherent design token layer (colors, typography, radii, spacing) using
   CSS custom properties.
3. Preserve every existing HTML class / id / data-* attribute so `app.js`,
   `admin.js`, `login.js` continue to work unchanged.
4. Provide dense but breathable form layouts for high-density data entry.
5. Modernize the sidebar, topbar, KPI cards, panels, tables, buttons, forms, modals,
   toasts, calendars, charts, admin console.

## What was implemented (2026-01-08)
- Backend wrapper: `/app/backend/server.py` (FastAPI + threaded proxy to
  `drilling_report_parser.form_server.FormHandler`).
- Frontend server: `/app/frontend/server.js` (Express static + selective backend proxy).
- HTML head updates (`index.html`, `login.html`, `admin.html`): Google Fonts
  (Chivo, IBM Plex Sans, IBM Plex Mono) + versioned stylesheet (`?v=modern-minimal-2`).
- Full rewrite of `/app/web_form/styles.css` mapping every legacy class name to the
  new design system.
- Liquid-glass visual effect fully neutralized (JS retained, filters/overlays hidden
  via CSS to preserve dynamic surface enhancement without visual artifacts).
- **Icon migration**: All 12 sidebar PNG icons in `index.html` replaced with inline
  SVG `mask-image` classes (`.icon-parsing`, `.icon-production`, `.icon-hsse`,
  `.icon-drilling`, `.icon-completion`, `.icon-workover`, `.icon-summary`,
  `.icon-analytics`, `.icon-check-list`, `.icon-form`, `.icon-dashboard`,
  `.icon-report`) that render via `currentColor`.
- **Layout squeeze fix**: `.admin-standalone` now uses `width: 100%; max-width: 1520px;
  margin: 0 auto` so grid items don't collapse to content width. `.record-top-grid`
  redesigned as `minmax(380px,420px) minmax(0,1fr)` so KPI panel takes the wide side
  and 4 KPI cards render horizontally on ≥1441px. Rules panel widened 320→360px.
- **Upstream code refresh (2026-01-08 iter 4)**: Pulled the latest commit `4236bb1`
  ("完成两个主要日报", +9102 LOC) which added MySQL backend, translation service,
  new "生产报表" and "NPT统计" pages with segmented tabs, project multiselect,
  filter dropdowns, Gantt chart, NPT description modal, etc. Re-applied the UI
  redesign (HTML heads, sidebar icons, styles.css). Added ~350 lines of NEW CSS
  covering: `.production-report-tabs` (segmented control), `.production-time-page`,
  `.production-time-filter/-kpis/-grid/-card-*`, `.production-report-shell`,
  `.production-report-filter-{trigger,dropdown,menu,options}`,
  `.production-check-option`, `.production-filter-{field,label,menu-actions}`,
  `.production-search-field` (with SVG search icon), `.production-action-button`,
  `.production-gantt/-axis/-rows/-row/-label/-track/-segment/-legend`,
  `.production-npt-ranking/-rank-{no,row,track}` (top-3 medals),
  `.production-side-{heading,actions,search,list}`, `.production-well-shortcut`,
  `.production-remark-{cell,input,save}`, `.npt-kpi/-icon`,
  `.npt-ranking-scroll/-rank-medal` (top-3 medals),
  `.npt-report-description/-button`, `.npt-donut-center/-stage`,
  `.npt-pending-table/-detail-table-lite/-description-cell/-preview/-view-all-pending`,
  `.project-multiselect-{trigger,menu,search,options,option,empty}`,
  `.npt-confirm-page/-row-actions/-confirm-link`. Also added missing i18n entries
  for `scope_type` (筛选方式 / Filter By / Filtrar Por) and `scope_value`
  (范围 / Scope / Alcance) which were showing as raw keys in the production filter.
- **Regression tested**: `python -m unittest` → **44/44 pass** (8 env-skipped).
  Screenshot suite verified all 8 workspace pages + 6 admin tabs at 1920×900.

## Design tokens
- Fonts: **Chivo** (headings, KPI numbers), **IBM Plex Sans** (body & forms),
  **IBM Plex Mono** (kickers, chips, menu category labels).
- Primary: `#0F52BA` (sapphire industrial blue) + amber accent `#E07B24`.
- Neutrals: cool grays #F4F5F7 → #0F172A.
- Sidebar: `#0B1220` slate, white text, 3px left indicator on active item.
- Corners: 4/6/8/12 px scale. Sharp, minimal shadow, 1px borders throughout.

## Deferred / Next Action Items
- P1: Reintroduce a subtle animated hover state on well cards (currently static).
- P1: Localise date input placeholders (browser defaults show "mm/dd/yyyy" in EN mode).
- P2: Redesign the calendar month view with proper today marker & event badges.
- P2: Add empty-state illustrations for analytics KPIs and NPT dashboards.
- P2: Sidebar collapse (icon-only) mode for smaller screens.
- P3: Convert PNG menu icons under `/app/web_form/icons/` to inline SVGs.

## Enhancement suggestion
Would you like to add a **dashboard-first landing page** (e.g. `/web_form/` root) that
surfaces "latest reports uploaded today", "wells needing attention" and "top NPT
causes this week"? It would turn the current well-first entry into a
manager-friendly overview and can drive daily active usage.
