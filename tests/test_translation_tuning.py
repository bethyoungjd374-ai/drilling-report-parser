from __future__ import annotations

import unittest
from io import BytesIO

from openpyxl import Workbook

from drilling_report_parser.form_server import (
    UploadedFile,
    _extract_excel_term_source,
    _merge_imported_translation_terms,
    _normalize_translation_tuning_config,
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


if __name__ == "__main__":
    unittest.main()
