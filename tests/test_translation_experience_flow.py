from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from drilling_report_parser.form_server import (
    _apply_translation_experience_suggestion,
    _load_translation_experience_pool,
    _mark_translation_experience_verified,
    _record_translation_experience_suggestions,
)


class TranslationExperienceFlowTest(unittest.TestCase):
    def test_suggestion_applies_to_global_pool_and_verifies_after_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            experience_path = root / "translation_experience.json"
            terms_path = root / "translation_terms.json"
            tuning_path = root / "translation_tuning.json"
            terms_path.write_text(json.dumps({"terms": [], "protected_terms": {"units": [], "acronyms": [], "proper_nouns": []}}), encoding="utf-8")
            tuning_path.write_text(json.dumps({"protections": {"mode": "placeholder"}}), encoding="utf-8")
            patches = (
                patch("drilling_report_parser.form_server.TRANSLATION_EXPERIENCE_PATH", experience_path),
                patch("drilling_report_parser.form_server.TRANSLATION_TERMS_PATH", terms_path),
                patch("drilling_report_parser.form_server.TRANSLATION_TUNING_PATH", tuning_path),
                patch("drilling_report_parser.form_server.list_records", return_value=[{
                    "record_id": "drilling:WELL-1:2026-01-01:1",
                    "translation_status": "COMPLETED",
                }]),
            )
            with patches[0], patches[1], patches[2], patches[3]:
                suggestions = _record_translation_experience_suggestions(
                    "drilling:WELL-1:2026-01-01:1",
                    "drilling",
                    [{
                        "field_code": "operations.operation_details",
                        "source_text": "PUMP AT 450 QPM",
                        "error_message": "model removed or changed units; missing=['qpm']",
                        "translation_status": "FAILED",
                    }],
                )
                self.assertEqual(len(suggestions), 1)
                suggestion_id = str(suggestions[0]["id"])

                applied = _apply_translation_experience_suggestion(suggestion_id, actor="admin")
                saved_terms = json.loads(terms_path.read_text(encoding="utf-8"))

                self.assertEqual(applied["status"], "APPLIED")
                self.assertIn("qpm", saved_terms["protected_terms"]["units"])
                self.assertEqual(_mark_translation_experience_verified("drilling:WELL-1:2026-01-01:1"), 1)
                pool = _load_translation_experience_pool()
                self.assertEqual(pool["suggestions"][0]["status"], "VERIFIED")


if __name__ == "__main__":
    unittest.main()
