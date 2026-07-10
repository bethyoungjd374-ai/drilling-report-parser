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

## Visual Evidence

- Full-view source comparison: `outputs/ui-qa/translation-test-result-comparison.png`
- Test workbench result: `outputs/ui-qa/translation-tuning-test-result.png`
- Field and Prompt configuration: `outputs/ui-qa/translation-tuning-fields-final.png`
- Terminology list and editor: `outputs/ui-qa/translation-tuning-terms-final.png`
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
