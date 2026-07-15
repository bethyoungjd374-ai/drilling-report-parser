from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from drilling_report_parser.form_server import (
    _apply_translation_experience_suggestion,
    _drain_queued_translation_experience_once,
    _load_translation_experience_pool,
    _mark_translation_experience_verified,
    _record_translation_experience_suggestions,
    _update_translation_experience_status,
)
from drilling_report_parser.translation.experience_store import normalize_experience_pool


class TranslationExperienceFlowTest(unittest.TestCase):
    def test_legacy_prompt_actions_are_migrated_to_diagnostic_reruns(self) -> None:
        fingerprint = "a" * 64

        pool = normalize_experience_pool({"suggestions": [{
            "fingerprint": fingerprint,
            "action_type": "add_prompt_rule",
            "title": "追加字段规则",
            "recommendation": "写入 Prompt",
            "proposed_change": {"action": "add_prompt_rule", "instruction": "extra rule"},
        }]})

        suggestion = pool["suggestions"][0]
        self.assertEqual(suggestion["action_type"], "retry_current_rules")
        self.assertEqual(suggestion["proposed_change"], {"action": "retry_current_rules"})
        self.assertIn("不写入正式 Prompt", suggestion["recommendation"])

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

    def test_waiting_suggestions_apply_together_after_active_translation_finishes(self) -> None:
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
            )
            with patches[0], patches[1], patches[2]:
                first = _record_translation_experience_suggestions(
                    "drilling:WELL-1:2026-01-01:1",
                    "drilling",
                    [{
                        "field_code": "operations.operation_details",
                        "source_text": "PUMP AT 450 QPM",
                        "error_message": "model removed or changed units; missing=['qpm']",
                        "translation_status": "FAILED",
                    }],
                )[0]
                second = _record_translation_experience_suggestions(
                    "drilling:WELL-2:2026-01-02:2",
                    "drilling",
                    [{
                        "field_code": "operations.operation_details",
                        "source_text": "PRESSURE 1200 PSI",
                        "error_message": "model removed or changed units; missing=['psi']",
                        "translation_status": "FAILED",
                    }],
                )[0]
                _update_translation_experience_status(str(first["id"]), status="QUEUED", actor="admin")
                _update_translation_experience_status(str(second["id"]), status="QUEUED", actor="admin")
                repeated = _record_translation_experience_suggestions(
                    "drilling:WELL-3:2026-01-03:3",
                    "drilling",
                    [{
                        "field_code": "operations.operation_details",
                        "source_text": "PUMP AT 500 QPM",
                        "error_message": "model removed or changed units; missing=['qpm']",
                        "translation_status": "FAILED",
                    }],
                )[0]
                self.assertEqual(repeated["status"], "QUEUED")

                with patch("drilling_report_parser.form_server._active_ai_job_counts", return_value={"translation": 0, "extraction": 0, "total": 0}), patch(
                    "drilling_report_parser.form_server._queue_translation_record_ids",
                    return_value=(3, 0),
                ) as queue_records:
                    result = _drain_queued_translation_experience_once()

                self.assertEqual(result["applied_suggestions"], 2)
                self.assertEqual(result["queued_records"], 3)
                queued_ids = queue_records.call_args.args[0]
                self.assertEqual(set(queued_ids), {
                    "drilling:WELL-1:2026-01-01:1",
                    "drilling:WELL-3:2026-01-03:3",
                    "drilling:WELL-2:2026-01-02:2",
                })
                saved_terms = json.loads(terms_path.read_text(encoding="utf-8"))
                self.assertEqual(set(saved_terms["protected_terms"]["units"]), {"qpm", "psi"})
                pool = _load_translation_experience_pool()
                self.assertEqual({item["status"] for item in pool["suggestions"]}, {"APPLIED"})
                self.assertEqual({item["queued_by"] for item in pool["suggestions"]}, {"admin"})


if __name__ == "__main__":
    unittest.main()
