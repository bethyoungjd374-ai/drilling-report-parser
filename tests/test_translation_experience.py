from __future__ import annotations

import unittest

from drilling_report_parser.translation.experience import diagnose_translation_failures


class TranslationExperienceDiagnosisTest(unittest.TestCase):
    def test_suggests_new_unit_for_unregistered_missing_unit(self) -> None:
        suggestions = diagnose_translation_failures(
            record_id="drilling:WELL-1:2026-01-01:1",
            report_type="drilling",
            failed_rows=[{
                "field_code": "operations.operation_details",
                "source_text": "PUMP AT 450 QPM",
                "error_message": "model removed or changed units; missing=['qpm']",
            }],
            protected_terms={"units": ["gpm"]},
            tuning={"protections": {"mode": "placeholder"}},
        )

        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0]["action_type"], "add_protected_unit")
        self.assertEqual(suggestions[0]["token"], "qpm")
        self.assertEqual(suggestions[0]["record_ids"], ["drilling:WELL-1:2026-01-01:1"])

    def test_suggests_placeholder_mode_when_known_unit_is_only_prompt_protected(self) -> None:
        suggestions = diagnose_translation_failures(
            record_id="drilling:WELL-1:2026-01-01:1",
            report_type="drilling",
            failed_rows=[{
                "field_code": "report_fields.currentOps",
                "source_text": "PUMP AT 450 GPM",
                "error_message": "model removed or changed units; missing=['gpm']",
            }],
            protected_terms={"units": ["gpm"]},
            tuning={"protections": {"mode": "prompt"}},
        )

        self.assertEqual(suggestions[0]["action_type"], "enable_placeholder")
        self.assertEqual(suggestions[0]["confidence"], "high")

    def test_classifies_unregistered_uppercase_term_as_acronym(self) -> None:
        suggestions = diagnose_translation_failures(
            record_id="drilling:WELL-1:2026-01-01:1",
            report_type="drilling",
            failed_rows=[{
                "field_code": "operations.operation_details",
                "source_text": "RUN XYZ TOOL",
                "error_message": "model changed or removed protected terms; missing=['XYZ']",
            }],
            protected_terms={"acronyms": [], "proper_nouns": []},
            tuning={"protections": {"mode": "placeholder"}},
        )

        self.assertEqual(suggestions[0]["action_type"], "add_protected_acronym")
        self.assertEqual(suggestions[0]["token"], "XYZ")

    def test_generic_semantic_failure_becomes_field_prompt_experience(self) -> None:
        suggestions = diagnose_translation_failures(
            record_id="drilling:WELL-1:2026-01-01:1",
            report_type="drilling",
            failed_rows=[{
                "field_code": "operations.operation_details",
                "source_text": "CONTINUE DRILLING",
                "error_message": "translation may omit operation actions: ['drill']",
            }],
            protected_terms={},
            tuning={"protections": {"mode": "placeholder"}},
        )

        suggestion = suggestions[0]
        self.assertEqual(suggestion["action_type"], "add_prompt_rule")
        self.assertEqual(suggestion["report_type"], "drilling")
        self.assertEqual(suggestion["field_code"], "operations.operation_details")
        self.assertIn("动作、对象、方向、时序", suggestion["proposed_change"]["instruction"])

    def test_transient_error_only_recommends_rerun(self) -> None:
        suggestions = diagnose_translation_failures(
            record_id="drilling:WELL-1:2026-01-01:1",
            report_type="drilling",
            failed_rows=[{"field_code": "", "source_text": "", "error_message": "The remote end closed the connection"}],
            protected_terms={},
            tuning={},
        )

        self.assertEqual(suggestions[0]["action_type"], "retry_current_rules")
        self.assertEqual(suggestions[0]["category"], "transient_provider")

    def test_generated_protected_fragment_failure_is_not_turned_into_prompt_rule(self) -> None:
        suggestions = diagnose_translation_failures(
            record_id="drilling:WELL-1:2026-01-01:1",
            report_type="drilling",
            failed_rows=[{
                "field_code": "report_fields.otherRemarks",
                "source_text": "A long protected technical description",
                "error_message": (
                    "OpenAI-compatible model returned low-quality translation "
                    "(4::protected-part-8: source text was returned unchanged)."
                ),
            }],
            protected_terms={},
            tuning={"protections": {"mode": "placeholder"}},
        )

        self.assertEqual(suggestions[0]["category"], "deterministic_protected_fragment")
        self.assertEqual(suggestions[0]["action_type"], "retry_current_rules")
        self.assertNotIn("instruction", suggestions[0]["proposed_change"])

    def test_placeholder_numeric_layout_failure_is_not_turned_into_prompt_rule(self) -> None:
        suggestions = diagnose_translation_failures(
            record_id="drilling:WELL-1:2026-01-01:1",
            report_type="drilling",
            failed_rows=[{
                "field_code": "operations.operation_details",
                "source_text": "LOW/HIGH PRESSURE 300 / 7500 PSI",
                "error_message": "model changed numeric values for item 8; missing=['300', '7500']; extra=['300/7500']",
            }],
            protected_terms={},
            tuning={"protections": {"mode": "placeholder"}},
        )

        self.assertEqual(suggestions[0]["category"], "deterministic_numeric_layout")
        self.assertEqual(suggestions[0]["action_type"], "retry_current_rules")
        self.assertNotIn("instruction", suggestions[0]["proposed_change"])


if __name__ == "__main__":
    unittest.main()
