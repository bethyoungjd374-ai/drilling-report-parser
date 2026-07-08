from __future__ import annotations

import unittest

from drilling_report_parser.translation import TermsConfig
from drilling_report_parser.translation.service import DrillingReportTranslator, detect_language


class FakeLocalEngine:
    name = "fake-local"

    def translate(self, text: str, source_language: str, target_language: str = "zh") -> str:
        return f"local[{source_language}->{target_language}] {text}"


class TranslationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.terms = TermsConfig.load()
        self.translator = DrillingReportTranslator(FakeLocalEngine(), self.terms, target_language="zh")

    def test_detects_basic_languages(self) -> None:
        self.assertEqual(detect_language("已经完成钻进"), "zh")
        self.assertEqual(detect_language("Drilled ahead with stable SPP."), "en")
        self.assertEqual(detect_language("Circuló fondo arriba con lodo."), "es")
        self.assertEqual(detect_language("SACA BHA #5 DIRECCIONAL"), "es")

    def test_protects_well_measurements_and_replaces_terms_to_chinese(self) -> None:
        item = self.translator.translate_text(
            'Drilling 8-1/2" hole on EB-D-12, ROP 18 m/hr, WOB 22 klb.',
            "report_fields.currentOps",
        )

        self.assertEqual(item["language"], "en")
        self.assertTrue(item["translated"])
        self.assertIn("EB-D-12", item["translated_text"])
        self.assertIn('8-1/2"', item["translated_text"])
        self.assertIn("机械钻速", item["translated_text"])
        self.assertIn("钻压", item["translated_text"])
        self.assertIn("EB-D-12", item["untranslated_tokens"])
        self.assertIn("18 m/hr", item["untranslated_tokens"])

    def test_replaces_terms_from_chinese_to_english(self) -> None:
        translator = DrillingReportTranslator(FakeLocalEngine(), self.terms, target_language="en")
        item = translator.translate_text("完成起钻后循环，检查防喷器。", "report_fields.summary24h")

        self.assertEqual(item["language"], "zh")
        self.assertIn("tripping out", item["translated_text"])
        self.assertIn("circulate", item["translated_text"])
        self.assertIn("BOP", item["translated_text"])
        self.assertTrue(any(record["replacement"] == "tripping out" for record in item["term_replacements"]))

    def test_replaces_terms_from_spanish_to_english(self) -> None:
        translator = DrillingReportTranslator(FakeLocalEngine(), self.terms, target_language="en")
        item = translator.translate_text("pérdida de circulación durante revestimiento", "operations[0].operation_details")

        self.assertEqual(item["language"], "es")
        self.assertIn("lost circulation", item["translated_text"])
        self.assertIn("casing", item["translated_text"])

    def test_replaces_terms_from_english_to_spanish(self) -> None:
        translator = DrillingReportTranslator(FakeLocalEngine(), self.terms, target_language="es")
        item = translator.translate_text("Lost circulation while drilling casing section.", "operations[0].operation_details")

        self.assertEqual(item["language"], "en")
        self.assertIn("pérdida de circulación", item["translated_text"])
        self.assertIn("perforación", item["translated_text"])
        self.assertIn("revestimiento", item["translated_text"])

    def test_translates_payload_and_preserves_original_result_items(self) -> None:
        payload = {
            "metadata": {"source_file": "mixed.pdf"},
            "report_fields": {
                "wellbore": "XX-101H",
                "currentOps": "Tripping out BHA #5. Circuló fondo arriba con MW 10.2 ppg.",
            },
            "operations": [
                {
                    "from": "00:00",
                    "to": "06:00",
                    "hours": "6",
                    "op_code": "DRLG",
                    "op_type": "P",
                    "operation_details": "Lost circulation while drilling 12.25 in section.",
                }
            ],
        }

        result = self.translator.translate_report_payload(payload)

        self.assertEqual(result["metadata"]["engine"], "fake-local")
        self.assertEqual(result["metadata"]["target_language"], "zh")
        self.assertIn("translated_payload", result)
        self.assertEqual(payload["report_fields"]["wellbore"], "XX-101H")
        translated_ops = result["translated_payload"]["operations"][0]["operation_details"]
        self.assertIn("井漏", translated_ops)
        self.assertIn("钻进", translated_ops)
        self.assertTrue(any(record["replacement"] == "井漏" for record in result["term_replacement_records"]))


if __name__ == "__main__":
    unittest.main()
