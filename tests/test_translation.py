from __future__ import annotations

import unittest

from drilling_report_parser.translation import TermsConfig, apply_translation_content
from drilling_report_parser.translation.service import (
    DrillingReportTranslator,
    TranslationTuningConfig,
    _split_translation_text,
    _translation_quality_error,
    detect_language,
    iter_payload_text_units,
    source_hash,
    translation_coverage,
)


class FakeLocalEngine:
    name = "fake-local"

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        return {str(item["id"]): f"local {item['source_text']}" for item in items}


class FlakyEngine:
    name = "flaky"

    def __init__(self) -> None:
        self.calls = 0

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary failure")
        return {str(item["id"]): "已完成翻译" for item in items}


class TranslationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.terms = TermsConfig.load()
        self.translator = DrillingReportTranslator(FakeLocalEngine(), self.terms, target_language="zh-CN")

    def test_detects_basic_languages(self) -> None:
        self.assertEqual(detect_language("已经完成钻进"), "zh-CN")
        self.assertEqual(detect_language("Drilled ahead with stable SPP."), "en")
        self.assertEqual(detect_language("Circuló fondo arriba con lodo."), "es")
        self.assertEqual(detect_language("SACA BHA #5 DIRECCIONAL"), "es")
        self.assertEqual(detect_language("Environ Incident? N INCIDENTES SIN REPORTAR EN LAS ULTIMAS 24 HORAS."), "es")

    def test_rejects_unchanged_or_barely_translated_chinese_output(self) -> None:
        source = "INCIDENTES SIN REPORTAR EN LAS ULTIMAS 24 HORAS. TRASLADO DE FLUIDOS DEL CAMPAMENTO."
        self.assertIn("unchanged", _translation_quality_error(source, source, "zh-CN"))
        self.assertIn("excessive", _translation_quality_error(source, f"{source} 钻进", "zh-CN"))
        self.assertEqual(_translation_quality_error(source, "过去 24 小时内无事故报告。已转运营地流体。", "zh-CN"), "")

    def test_splits_long_remarks_without_losing_text(self) -> None:
        source = "第一段内容。 " + ("LONG TECHNICAL REMARK - " * 45) + "最后一段。"
        parts = _split_translation_text(source, max_chars=180)
        self.assertGreater(len(parts), 2)
        self.assertTrue(all(len(part) <= 181 for part in parts))
        self.assertEqual("".join(parts).replace(" ", ""), source.replace(" ", ""))

    def test_extracts_only_configured_free_text_fields(self) -> None:
        payload = {
            "metadata": {"record_id": "drilling:PCNC-040:2026-06-11:11"},
            "report_fields": {
                "wellbore": "PCNC-040",
                "currentOps": "SACANDO BHA #3.",
                "incidentComments": "SIN INCIDENTES REPORTADOS.",
                "otherRemarks": "TRASLADO DE FLUIDOS DEL CAMPAMENTO.",
                "todayMd": "10832",
            },
            "operations": [
                {
                    "from": "00:00",
                    "op_code": "DRLG",
                    "operation_details": "PERFORA SECCION.",
                }
            ],
        }

        units = iter_payload_text_units(payload)

        self.assertEqual(
            [unit.field_code for unit in units],
            [
                "report_fields.currentOps",
                "report_fields.incidentComments",
                "report_fields.otherRemarks",
                "operations.operation_details",
            ],
        )
        self.assertTrue(all("wellbore" not in unit.field_code for unit in units))

    def test_generates_translation_content_and_preserves_original_payload(self) -> None:
        payload = {
            "metadata": {"record_id": "drilling:XX-101H:2026-06-11:11"},
            "report_fields": {
                "wellbore": "XX-101H",
                "currentOps": "ROP 18 m/hr while drilling 12.25 in section.",
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

        progress_updates = []
        result = self.translator.translate_report_payload(
            payload,
            on_progress=lambda language, completed, total: progress_updates.append((language, completed, total)),
        )

        self.assertEqual(result["metadata"]["engine"], "fake-local")
        self.assertEqual(result["metadata"]["target_language"], "zh-CN")
        self.assertIn("translation_content", result)
        self.assertEqual(payload["report_fields"]["wellbore"], "XX-101H")
        fields = result["translated_payload"]["report_fields"]
        self.assertIn("机械钻速", fields["currentOps"])
        translated_ops = result["translated_payload"]["operations"][0]["operation_details"]
        self.assertIn("井漏", translated_ops)
        self.assertTrue(all(row["source_hash"] for row in result["translation_content"]))
        self.assertEqual(progress_updates[-1], ("zh-CN", 2, 2))

    def test_applies_saved_translation_content_to_payload(self) -> None:
        payload = {
            "metadata": {"record_id": "drilling:PCNC-040:2026-06-11:11"},
            "report_fields": {"currentOps": "SACANDO BHA"},
            "operations": [{"operation_details": "PERFORA SECCION"}],
        }
        rows = [
            {
                "entity_id": "drilling:PCNC-040:2026-06-11:11",
                "field_code": "report_fields.currentOps",
                "target_language": "zh-CN",
                "translated_text": "起出 BHA",
                "translation_status": "COMPLETED",
            },
            {
                "entity_id": "drilling:PCNC-040:2026-06-11:11:operations:1",
                "field_code": "operations.operation_details",
                "target_language": "zh-CN",
                "translated_text": "钻进井段",
                "translation_status": "COMPLETED",
            },
        ]

        translated = apply_translation_content(payload, rows, "zh-CN")

        self.assertEqual(translated["report_fields"]["currentOps"], "起出 BHA")
        self.assertEqual(translated["operations"][0]["operation_details"], "钻进井段")

    def test_ignores_translation_when_source_hash_is_stale(self) -> None:
        payload = {
            "metadata": {"record_id": "drilling:A:1"},
            "report_fields": {"currentOps": "Drilling new section"},
        }
        rows = [{
            "entity_id": "drilling:A:1",
            "field_code": "report_fields.currentOps",
            "target_language": "zh-CN",
            "translated_text": "旧井段译文",
            "translation_status": "COMPLETED",
            "source_hash": source_hash("Drilling old section"),
        }]

        translated = apply_translation_content(payload, rows, "zh-CN")

        self.assertEqual(translated["report_fields"]["currentOps"], "Drilling new section")
        self.assertFalse(translation_coverage(payload, rows, "zh-CN")["ready"])

    def test_requires_complete_translation_coverage(self) -> None:
        payload = {
            "metadata": {"record_id": "drilling:A:1"},
            "report_fields": {"currentOps": "Drilling ahead"},
            "operations": [{"operation_details": "Circulate bottoms up"}],
        }
        rows = [{
            "entity_id": "drilling:A:1",
            "field_code": "report_fields.currentOps",
            "target_language": "zh-CN",
            "translated_text": "继续钻进",
            "translation_status": "COMPLETED",
            "source_hash": source_hash("Drilling ahead"),
        }]

        coverage = translation_coverage(payload, rows, "zh-CN")

        self.assertFalse(coverage["ready"])
        self.assertEqual(coverage["required_count"], 2)
        self.assertEqual(coverage["completed_count"], 1)

    def test_retries_model_calls_and_records_model_config_id(self) -> None:
        engine = FlakyEngine()
        translator = DrillingReportTranslator(
            engine,
            self.terms,
            target_language="zh-CN",
            model_config_id="model-primary",
            retry_count=1,
        )

        result = translator.translate_report_payload({"report_fields": {"currentOps": "Drilling ahead"}})

        self.assertEqual(engine.calls, 2)
        self.assertEqual(result["translation_content"][0]["model_config_id"], "model-primary")

    def test_tuning_limits_fields_and_changes_prompt(self) -> None:
        tuning = TranslationTuningConfig.from_data({
            "field_policies": [
                {"field_code": "report_fields.currentOps", "enabled": True},
                {"field_code": "rows.operation_details", "enabled": False},
            ],
            "prompt": {
                "system_prompt": "你是现场钻井翻译审核员。",
                "translation_instruction": "逐句翻译，禁止合并句子。",
            },
            "protections": {"numbers": True, "units": True, "acronyms": True, "proper_nouns": False},
            "version": "test-tuning-v1",
        })
        translator = DrillingReportTranslator(FakeLocalEngine(), self.terms, tuning=tuning)
        payload = {
            "report_fields": {"currentOps": "Drilling ahead", "otherRemarks": "Standby cement unit"},
            "operations": [{"operation_details": "Circulate bottoms up"}],
        }

        result = translator.translate_report_payload(payload)
        preview = translator.prompt_preview("ROP 18 m/hr while drilling", "zh-CN")

        self.assertEqual(len(result["translation_content"]), 1)
        self.assertEqual(result["translation_content"][0]["field_code"], "report_fields.currentOps")
        self.assertEqual(result["translation_content"][0]["prompt_version"], "test-tuning-v1")
        self.assertIn("现场钻井翻译审核员", preview)
        self.assertIn("逐句翻译，禁止合并句子", preview)
        self.assertIn("ROP", preview)

    def test_scope_rules_separate_report_types_and_modules(self) -> None:
        tuning = TranslationTuningConfig.from_data({
            "scope_rules": [
                {"report_type": "completion", "section": "report_fields", "field_name": "description", "enabled": True},
                {"report_type": "completion", "section": "operations", "field_name": "operation_details", "enabled": True},
            ]
        })
        translator = DrillingReportTranslator(FakeLocalEngine(), self.terms, tuning=tuning)
        drilling = {
            "metadata": {"report_type": "drilling"},
            "report_fields": {"description": "Drilling description"},
            "operations": [{"operation_details": "Drill ahead"}],
        }
        completion = {
            "metadata": {"report_type": "completion"},
            "report_fields": {"description": "Run completion string"},
            "operations": [{"operation_details": "Pressure test tubing"}],
        }

        self.assertEqual(translator.translate_report_payload(drilling)["translation_content"], [])
        rows = translator.translate_report_payload(completion)["translation_content"]
        self.assertEqual({row["field_code"] for row in rows}, {"report_fields.description", "operations.operation_details"})


if __name__ == "__main__":
    unittest.main()
