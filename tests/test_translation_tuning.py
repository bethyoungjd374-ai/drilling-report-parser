from __future__ import annotations

import unittest
from io import BytesIO

from openpyxl import Workbook

from drilling_report_parser.form_server import (
    UploadedFile,
    _decode_ai_terms_json,
    _extract_excel_term_source,
    _merge_imported_translation_terms,
    _normalize_translation_tuning_config,
    _normalize_translation_terms_config,
    _parse_standard_translation_terms,
    _translation_record_needs_processing,
    _current_translation_revision,
    _translation_terms_workbook_bytes,
)


class TranslationTuningConfigTest(unittest.TestCase):
    def test_keeps_only_supported_translation_fields(self) -> None:
        config = _normalize_translation_tuning_config({
            "field_policies": [
                {"field_code": "report_fields.currentOps", "enabled": False},
                {"field_code": "report_fields.wellbore", "enabled": True},
            ],
            "target_languages": ["zh", "invalid"],
        })

        rules = config["scope_rules"]
        self.assertFalse(any(item["field_name"] == "wellbore" for item in rules))
        current_ops = [item for item in rules if item["field_name"] == "currentOps"]
        self.assertEqual(len(current_ops), 4)
        self.assertTrue(all(item["enabled"] is False for item in current_ops))
        self.assertEqual(config["target_languages"], ["zh-CN"])

    def test_keeps_exact_report_module_and_field_scope(self) -> None:
        config = _normalize_translation_tuning_config({
            "scope_rules": [{
                "report_type": "completion",
                "section": "perforation_intervals",
                "field_name": "comments",
                "enabled": True,
            }]
        })

        self.assertEqual(len(config["scope_rules"]), 1)
        self.assertEqual(config["scope_rules"][0]["field_code"], "perforation_intervals.comments")

    def test_prompt_changes_produce_a_new_version(self) -> None:
        first = _normalize_translation_tuning_config({"prompt": {"system_prompt": "Prompt A"}})
        second = _normalize_translation_tuning_config({"prompt": {"system_prompt": "Prompt B"}})

        self.assertNotEqual(first["version"], second["version"])

    def test_runtime_revision_changes_with_terms_and_model(self) -> None:
        tuning = _normalize_translation_tuning_config({"prompt": {"system_prompt": "Prompt A"}})
        model_a = {"id": "model-a", "api_type": "openai-compatible", "model": "alpha"}
        model_b = {"id": "model-b", "api_type": "openai-compatible", "model": "beta"}
        terms_a = {"terms": [{"id": "bha", "en": "BHA", "zh": "钻具组合", "enabled": True, "protected": True}]}
        terms_b = {"terms": [{"id": "bha", "en": "BHA", "zh": "井底钻具组合", "enabled": True, "protected": True}]}

        base = _current_translation_revision(model=model_a, terms_config=terms_a, tuning_config=tuning)
        changed_terms = _current_translation_revision(model=model_a, terms_config=terms_b, tuning_config=tuning)
        changed_model = _current_translation_revision(model=model_b, terms_config=terms_a, tuning_config=tuning)

        self.assertNotEqual(base, changed_terms)
        self.assertNotEqual(base, changed_model)

    def test_extracts_flexible_excel_cells_without_assuming_headers(self) -> None:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Glossary"
        sheet.append(["English term", "Spanish", "Chinese"])
        sheet.append(["Drill Ahead", "Continuar Perforando", "继续钻进"])
        buffer = BytesIO()
        workbook.save(buffer)

        text, stats = _extract_excel_term_source(UploadedFile("terms.xlsx", buffer.getvalue()))

        self.assertIn("Drill Ahead", text)
        self.assertEqual(stats["sheet_count"], 1)
        self.assertGreaterEqual(stats["cell_count"], 6)

    def test_import_skips_duplicates_and_adds_new_terms(self) -> None:
        config = {
            "terms": [{"id": "existing", "category": "drilling", "zh": "开钻", "en": "Spud Well", "es": "Iniciar Pozo", "aliases": {}, "enabled": True, "protected": True}],
            "protected_terms": {},
        }
        candidates = [
            {"category": "drilling", "zh": "开钻", "en": "Spud", "es": "Iniciar Pozo", "aliases": {}},
            {"category": "drilling", "zh": "继续钻进", "en": "Drill Ahead", "es": "Continuar Perforando", "aliases": {}},
        ]

        imported, duplicates = _merge_imported_translation_terms(config, candidates)

        self.assertEqual(len(imported), 1)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["existing_id"], "existing")

    def test_migrates_legacy_categories_to_operation_types(self) -> None:
        config = _normalize_translation_terms_config({
            "terms": [
                {"zh": "钻进", "en": "drilling", "category": "operation"},
                {"zh": "立管压力", "en": "standpipe pressure", "category": "通用"},
            ]
        })

        self.assertEqual([term["category"] for term in config["terms"]], ["drilling", "general"])

    def test_template_round_trips_through_standard_parser(self) -> None:
        data = _translation_terms_workbook_bytes({"terms": [], "protected_terms": {}}, template=True)

        terms = _parse_standard_translation_terms(UploadedFile("template.xlsx", data))

        self.assertEqual(len(terms), 2)
        self.assertEqual(terms[0]["category"], "drilling")
        self.assertTrue(all(sum(bool(term.get(language)) for language in ("zh", "en", "es")) >= 2 for term in terms))

    def test_decodes_fenced_or_array_ai_json(self) -> None:
        fenced = 'analysis\n```json\n{"terms":[{"zh":"钻进","en":"drilling"}]}\n```'
        array = '[{"zh":"循环","en":"circulate"}] trailing text'

        self.assertIsInstance(_decode_ai_terms_json(fenced), dict)
        self.assertIsInstance(_decode_ai_terms_json(array), list)

    def test_only_actionable_translation_states_count_as_pending(self) -> None:
        current_version = "prompt-v2"

        self.assertTrue(_translation_record_needs_processing({"translation_status": "PENDING"}, current_version))
        self.assertTrue(_translation_record_needs_processing({"translation_status": "STOPPED"}, current_version))
        self.assertTrue(_translation_record_needs_processing({"translation_status": "FAILED"}, current_version))
        self.assertTrue(_translation_record_needs_processing({"translation_status": "COMPLETED", "translation_version": "prompt-v1"}, current_version))
        self.assertFalse(_translation_record_needs_processing({"translation_status": "QUEUED"}, current_version))
        self.assertFalse(_translation_record_needs_processing({"translation_status": "IN_PROGRESS"}, current_version))
        self.assertFalse(_translation_record_needs_processing({"translation_status": "NOT_REQUIRED"}, current_version))


if __name__ == "__main__":
    unittest.main()
