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
