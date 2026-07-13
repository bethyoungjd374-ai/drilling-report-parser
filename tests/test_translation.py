from __future__ import annotations

import json
import re
import unittest
from unittest.mock import patch

from drilling_report_parser.translation import TermsConfig, apply_translation_content
from drilling_report_parser.translation.service import (
    DrillingReportTranslator,
    OpenAICompatibleTranslationEngine,
    TranslationCircuitOpen,
    TranslationQualityError,
    TranslationTuningConfig,
    TranslationTransportError,
    _numeric_quality_error,
    _openai_item_quality_error,
    _check_provider_circuit,
    _PROVIDER_CIRCUIT_LOCK,
    _PROVIDER_CIRCUITS,
    _restore_surgically_protected_values,
    _repair_protected_token_layout,
    _surgically_protect_values,
    _split_translation_text,
    _translation_part_item,
    _translation_quality_error,
    clean_translation_source,
    detect_language,
    iter_payload_text_units,
    source_hash,
    text_needs_translation,
    translation_coverage,
)


def legacy_tuning(**overrides):
    return TranslationTuningConfig(pipeline_mode="legacy", **overrides)


class FakeLocalEngine:
    name = "fake-local"

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        return {str(item["id"]): f"local {item['source_text']}" for item in items}


class RecordingTranslationEngine:
    name = "recording"

    def __init__(self, translated_text: str) -> None:
        self.translated_text = translated_text
        self.items = []

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        self.items.extend(items)
        return {str(item["id"]): self.translated_text for item in items}


class RepairingTranslationEngine:
    name = "repairing"

    def __init__(self) -> None:
        self.items = []

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        self.items.extend(items)
        return {
            str(item["id"]): (
                "使用BHA钻进至3200英尺。"
                if item.get("repair_context")
                else "钻进至3200英尺。"
            )
            for item in items
        }


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


class CountingEngine:
    name = "openai-compatible"

    def __init__(self) -> None:
        self.calls = 0
        self.batch_sizes = []
        self.batches = []

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        self.calls += 1
        self.batch_sizes.append(len(items))
        self.batches.append(list(items))
        return {
            str(item["id"]): "已完成翻译 " + " ".join(re.findall(r"\[\[P\d+]]", item["source_text"]))
            for item in items
        }


class ProtectedTokenEngine:
    name = "protected-token-engine"

    def __init__(self, *, drop_tokens: bool = False, reverse_tokens: bool = False) -> None:
        self.calls = 0
        self.items = []
        self.drop_tokens = drop_tokens
        self.reverse_tokens = reverse_tokens

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        self.calls += 1
        self.items.extend(items)
        if self.drop_tokens:
            return {str(item["id"]): "已完成翻译" for item in items}
        results = {}
        for item in items:
            tokens = re.findall(r"\[\[P\d+]]", item["source_text"])
            if self.reverse_tokens:
                tokens.reverse()
            results[str(item["id"])] = "已完成翻译 " + " ".join(tokens)
        return results


class PlaceholderRejectingEngine:
    name = "openai-compatible"

    def __init__(self) -> None:
        self.calls = 0
        self.items = []

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        self.calls += 1
        self.items.extend(items)
        if any(re.search(r"\[\[P\d+]]", str(item.get("source_text", ""))) for item in items):
            raise TranslationQualityError("model changed, removed, or duplicated protected placeholders")
        return {str(item["id"]): "已翻译" for item in items}


class PartialFailureEngine:
    name = "partial-failure-engine"

    def __init__(self) -> None:
        self.batch_sizes = []

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        self.batch_sizes.append(len(items))
        results = {}
        for item in items:
            tokens = re.findall(r"\[\[P\d+]]", item["source_text"])
            if len(items) > 1 and str(item["id"]) == "1":
                tokens = []
            results[str(item["id"])] = "已完成翻译 " + " ".join(tokens)
        return results


class OfflineEngine:
    name = "openai-compatible"

    def __init__(self) -> None:
        self.calls = 0

    def translate_items(self, items, target_language, timeout_seconds):
        del items, target_language, timeout_seconds
        self.calls += 1
        raise TranslationTransportError("provider offline", retryable=False)


class CoolingDownEngine:
    name = "openai-compatible"

    def __init__(self) -> None:
        self.calls = 0

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        self.calls += 1
        if self.calls == 1:
            raise TranslationCircuitOpen("provider cooling down", retry_after_seconds=2.5)
        return {
            str(item["id"]): "已完成翻译 " + " ".join(re.findall(r"\[\[P\d+]]", item["source_text"]))
            for item in items
        }


class ExtraNumberEngine:
    name = "extra-number"

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        return {
            str(item["id"]): "已完成翻译 999 " + " ".join(re.findall(r"\[\[P\d+]]", item["source_text"]))
            for item in items
        }


class MonthLocalizationEngine:
    name = "month-localization"

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        return {
            str(item["id"]): str(item["source_text"])
            .replace("DESDE EL", "自")
            .replace("DE MAYO DE", "年5月")
            .replace(".", "日。")
            for item in items
        }


class SuperscriptUnitEngine:
    name = "superscript-unit"

    def translate_items(self, items, target_language, timeout_seconds):
        del target_language, timeout_seconds
        return {
            str(item["id"]): str(item["source_text"])
            .replace("VOLUMEN", "体积")
            .replace("M3", "m³")
            for item in items
        }


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

    def test_mixed_chinese_and_spanish_text_still_requires_translation(self) -> None:
        source = "已确认：CONTINUAR BAJANDO CASING HASTA 10749 FT."

        self.assertTrue(text_needs_translation(source, "zh-CN"))
        result = self.translator.translate_report_payload({"report_fields": {"currentOps": source}})
        self.assertEqual(result["translation_content"][0]["translation_status"], "COMPLETED")

    def test_rejects_unchanged_or_barely_translated_chinese_output(self) -> None:
        source = "INCIDENTES SIN REPORTAR EN LAS ULTIMAS 24 HORAS. TRASLADO DE FLUIDOS DEL CAMPAMENTO."
        self.assertIn("unchanged", _translation_quality_error(source, source, "zh-CN"))
        self.assertIn("unchanged", _translation_quality_error(source, f"{source} 钻进", "zh-CN"))
        self.assertEqual(_translation_quality_error(source, "过去 24 小时内无事故报告。已转运营地流体。", "zh-CN"), "")
        self.assertIn(
            "unchanged",
            _translation_quality_error("RUN COMPLETION STRING\nTO PRODUCTION DEPTH.", "RUN COMPLETION STRING TO PRODUCTION DEPTH.", "zh-CN"),
        )

    def test_data_heavy_output_is_not_rejected_by_chinese_ratio(self) -> None:
        source = "ISIP: 5520 PSI; FRICTION GRADIENT: 0.16 PSI/FT; HHP: 4598 HHP."
        translated = "ISIP：5520 PSI；摩阻梯度：0.16 PSI/FT；HHP：4598 HHP。"

        self.assertEqual(_translation_quality_error(source, translated, "zh-CN"), "")

    def test_allows_preserved_spanish_terms_inside_chinese_output(self) -> None:
        source = "INSTALA EQUIPO (VENTA STP) COMO SIGUE."

        error = _translation_quality_error(source, "安装设备（VENTA STP），如下。", "zh-CN")

        self.assertEqual(error, "")

    def test_surgical_number_restore_preserves_adjacent_number_boundary(self) -> None:
        source = "GUÍA # 0177006 1 WINCHE; GUÍA # 0177003 1 GRÚA."
        protected, values = _surgically_protect_values({"id": "1", "source_text": source})
        collapsed = str(protected["source_text"])
        for index, value in enumerate(values):
            if index and value.get("separate_from_previous"):
                previous_token = str(values[index - 1]["token"])
                collapsed = collapsed.replace(f"{previous_token} {value['token']}", f"{previous_token}{value['token']}")

        restored = _restore_surgically_protected_values(collapsed, values)

        self.assertIn("0177006 1", restored)
        self.assertIn("0177003 1", restored)
        self.assertEqual(_numeric_quality_error(source, restored, "zh-CN"), "")

    def test_main_protection_restores_space_between_mixed_fraction_tokens(self) -> None:
        source = 'SECCIÓN [[P0]] [[P1]]"'

        repaired = _repair_protected_token_layout(source, '井段 [[P0]][[P1]]"')

        self.assertEqual(repaired, '井段 [[P0]] [[P1]]"')

    def test_main_protection_restores_punctuation_range_boundary(self) -> None:
        source = "低压 [[P0]]\n/ [[P1]] 高压"

        repaired = _repair_protected_token_layout(source, "低压[[P0]]/[[P1]]高压")

        self.assertEqual(repaired, "低压[[P0]]\n/ [[P1]]高压")
        restored = repaired.replace("[[P0]]", "300").replace("[[P1]]", "7500")
        self.assertEqual(_numeric_quality_error("低压 300\n/ 7500 高压", restored, "zh-CN"), "")

    def test_mixed_fraction_is_protected_as_one_value(self) -> None:
        translator = DrillingReportTranslator(
            ProtectedTokenEngine(),
            TermsConfig.from_data({}),
            target_language="zh-CN",
        )

        protected, tokens = translator._protect_source_text('PACKER 7" X 3-1/2"', "zh-CN")

        self.assertIn('[[P1]]"', protected)
        self.assertNotIn("-1/2", protected)
        self.assertEqual([item["replacement"] for item in tokens], ["7", "3-1/2"])

    def test_main_protection_removes_invented_fraction_suffix(self) -> None:
        source = "ARENA MAXPROP [[P1]] PARA TRABAJO"

        repaired = _repair_protected_token_layout(source, "MAXPROP [[P1]]/40砂用于作业")

        self.assertEqual(repaired, "MAXPROP [[P1]]砂用于作业")

    def test_main_protection_restores_space_after_latin_term(self) -> None:
        source = "ARENA MAXPROP [[P1]] PARA TRABAJO"

        repaired = _repair_protected_token_layout(source, "MaxProp[[P1]]砂用于作业")

        self.assertEqual(repaired, "MaxProp [[P1]]砂用于作业")

    def test_surgical_retry_protects_required_technical_identifier(self) -> None:
        protected, values = _surgically_protect_values({
            "id": "15",
            "source_text": "TCP + PURE - WO#01",
            "preserve_terms": ["WO#01"],
        })

        restored = _restore_surgically_protected_values("TCP + PURE - " + values[-1]["token"], values)

        self.assertNotIn("WO#01", protected["source_text"])
        self.assertTrue(any(value["replacement"] == "WO#01" for value in values))
        self.assertTrue(restored.endswith("WO#01"))

    def test_long_text_part_only_carries_terms_present_in_that_part(self) -> None:
        item = {
            "id": "0",
            "source_text": "FIRST ID-A1. SECOND ID-B2.",
            "glossary": [
                {"source": "FIRST", "target": "第一"},
                {"source": "SECOND", "target": "第二"},
            ],
            "preserve_terms": ["ID-A1", "ID-B2"],
        }

        part = _translation_part_item(item, "0::part-0", "FIRST ID-A1.")

        self.assertEqual(part["glossary"], [{"source": "FIRST", "target": "第一"}])
        self.assertEqual(part["preserve_terms"], ["ID-A1"])

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
        self.assertEqual(units[0].context["wellbore"], "PCNC-040")
        self.assertEqual(units[0].context["current_depth"], "10832")
        self.assertEqual(units[-1].context["start_time"], "00:00")
        self.assertEqual(units[-1].context["operation_code"], "DRLG")

    def test_cleans_only_high_confidence_pdf_artifacts_before_model_request(self) -> None:
        raw = "PERFO-\nRÓ HASTA 10832 ft.\nPage 2 of 4\nDAILY OPERATIONS REPORT"

        cleaned, actions = clean_translation_source(raw)

        self.assertEqual(cleaned, "PERFORÓ HASTA 10832 ft.")
        self.assertIn("join_hyphenated_line_break", actions)
        self.assertIn("remove_pdf_header_footer:2", actions)

        engine = RecordingTranslationEngine("钻进至10832英尺。")
        translator = DrillingReportTranslator(engine, TermsConfig.from_data({"protected_terms": {"units": ["ft"]}}), target_language="zh-CN")
        row = translator.translate_report_payload({"report_fields": {"currentOps": raw}})["translation_content"][0]
        self.assertEqual(row["source_text"], raw)
        self.assertEqual(engine.items[0]["source_text"], cleaned)

    def test_operation_event_context_includes_adjacent_actions_without_changing_source(self) -> None:
        engine = RecordingTranslationEngine("已完成作业。")
        translator = DrillingReportTranslator(engine, TermsConfig.from_data({}), target_language="zh-CN")
        payload = {
            "metadata": {"record_id": "drilling:CTX-2", "report_type": "drilling"},
            "operations": [
                {"row_no": "1", "from": "00:00", "to": "02:00", "op_code": "DRLG", "operation_details": "DRILLED AHEAD."},
                {"row_no": "2", "from": "02:00", "to": "03:30", "op_code": "CIRC", "operation_details": "CIRCULATED CLEAN."},
                {"row_no": "3", "from": "03:30", "to": "06:00", "op_code": "POOH", "operation_details": "PULLED BHA."},
            ],
        }

        translator.translate_report_payload(payload)

        middle = next(item for item in engine.items if item["source_text"] == "CIRCULATED CLEAN.")
        event_context = middle["prompt_context"]["event_context"]
        self.assertEqual(event_context["start_time"], "02:00")
        self.assertEqual(event_context["end_time"], "03:30")
        self.assertEqual(event_context["operation_code"], "CIRC")
        self.assertEqual(event_context["previous_event"], "DRILLED AHEAD.")
        self.assertEqual(event_context["next_event"], "PULLED BHA.")
        self.assertIn("钻进、循环", middle["prompt_context"]["business_prompt"])
        self.assertEqual(middle["source_text"], payload["operations"][1]["operation_details"])

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
        self.assertEqual(fields["currentOps"], "local ROP 18 m/hr while drilling 12.25 in section.")
        translated_ops = result["translated_payload"]["operations"][0]["operation_details"]
        self.assertEqual(translated_ops, "local Lost circulation while drilling 12.25 in section.")
        self.assertTrue(all(row["source_hash"] for row in result["translation_content"]))
        self.assertEqual(progress_updates[-1], ("zh-CN", 2, 2))

    def test_contextual_pipeline_sends_complete_source_and_typed_matched_terms(self) -> None:
        source = "SACA BHA #3 DESDE 3200 ft PARA CAMBIO DE BROCA PDC."
        engine = RecordingTranslationEngine("从3200 ft起出BHA #3，更换PDC钻头。")
        terms = TermsConfig.from_data({
            "terms": [
                {"id": "pdc", "es": "broca PDC", "zh": "PDC钻头", "term_type": "phrase", "priority": 100},
                {"id": "saca", "es": "saca", "zh": "起出", "term_type": "contextual", "priority": 30},
            ],
            "protected_terms": {"acronyms": ["BHA"], "units": ["ft"]},
        })
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN")

        result = translator.translate_report_payload({"report_fields": {"currentOps": source}})

        request_item = engine.items[0]
        self.assertEqual(request_item["source_text"], source)
        self.assertNotIn("[[P", request_item["source_text"])
        self.assertEqual(request_item["preserve_terms"], ["BHA"])
        self.assertEqual(
            [(item["source"], item["type"]) for item in request_item["glossary"]],
            [("broca PDC", "phrase"), ("saca", "contextual")],
        )
        self.assertEqual(result["translation_content"][0]["translation_status"], "COMPLETED")

    def test_contextual_pipeline_does_not_rewrite_model_output_after_translation(self) -> None:
        engine = RecordingTranslationEngine("下入 drill pipe（钻柱）。")
        terms = TermsConfig.from_data({
            "terms": [{"id": "dp", "en": "drill pipe", "zh": "钻杆", "protected": True}],
        })
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN")

        result = translator.translate_report_payload({"report_fields": {"currentOps": "RUN DRILL PIPE."}})

        self.assertEqual(result["translation_content"][0]["translated_text"], "下入 drill pipe（钻柱）。")

    def test_contextual_pipeline_repairs_only_after_deterministic_validation_failure(self) -> None:
        engine = RepairingTranslationEngine()
        terms = TermsConfig.from_data({
            "protected_terms": {"acronyms": ["BHA"], "units": ["ft"]},
        })
        translator = DrillingReportTranslator(
            engine,
            terms,
            target_language="zh-CN",
            retry_count=1,
            tuning=TranslationTuningConfig(unit_aliases=(("ft", ("英尺",)),)),
        )

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "DRILL WITH BHA TO 3200 ft."},
        })

        row = result["translation_content"][0]
        self.assertEqual(row["translation_status"], "COMPLETED")
        self.assertEqual(row["translated_text"], "使用BHA钻进至3200英尺。")
        self.assertEqual(len(engine.items), 2)
        repair = engine.items[1]["repair_context"]
        self.assertEqual(repair["draft_translation"], "钻进至3200英尺。")
        self.assertIn("BHA", repair["issues"][0])

        checks = translator.quality_checks("DRILL WITH BHA TO 3200 ft.", row["translated_text"])
        self.assertTrue(all(check["status"] == "passed" for check in checks))

    def test_emits_translation_rows_incrementally_by_chunk(self) -> None:
        translator = DrillingReportTranslator(
            FakeLocalEngine(),
            self.terms,
            target_language="zh-CN",
            chunk_max_chars=40,
        )
        persisted = []
        payload = {
            "report_fields": {
                "currentOps": "DRILL AHEAD WITH STABLE RETURNS.",
                "summary24h": "CIRCULATE BOTTOMS UP UNTIL CLEAN.",
            }
        }

        result = translator.translate_report_payload(
            payload,
            on_rows=lambda language, rows: persisted.append((language, list(rows))),
        )

        self.assertEqual(len(result["translation_content"]), 2)
        self.assertEqual(sum(len(rows) for _language, rows in persisted), 2)
        self.assertTrue(all(language == "zh-CN" for language, _rows in persisted))

    def test_translation_batch_exercises_multiple_items_in_one_request(self) -> None:
        engine = CountingEngine()
        translator = DrillingReportTranslator(engine, self.terms, target_language="zh-CN", chunk_max_chars=2400)

        rows = translator.translate_text_batch(["DRILL AHEAD WITH STABLE RETURNS."] * 6)

        self.assertEqual(len(rows), 6)
        self.assertEqual(engine.batch_sizes, [6])
        self.assertTrue(all(row["translation_status"] == "COMPLETED" for row in rows))

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
        events = []
        translator = DrillingReportTranslator(
            engine,
            TermsConfig.from_data({}),
            target_language="zh-CN",
            model_config_id="model-primary",
            retry_count=1,
            telemetry=events.append,
        )

        result = translator.translate_report_payload({"report_fields": {"currentOps": "Drilling ahead"}})

        self.assertEqual(engine.calls, 2)
        self.assertEqual(result["translation_content"][0]["model_config_id"], "model-primary")
        self.assertIn("model_request_retry", [event["event"] for event in events])
        self.assertNotIn("model_request_error", [event["event"] for event in events])

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
        self.assertEqual(result["translation_content"][0]["prompt_version"], translator.prompt_version)
        self.assertIn("现场钻井翻译审核员", preview)
        self.assertIn("逐句翻译，禁止合并句子", preview)
        self.assertIn("ROP", preview)

    def test_scoped_experience_rule_is_injected_only_for_matching_field(self) -> None:
        tuning = TranslationTuningConfig.from_data({
            "experience_rules": [{
                "report_type": "drilling",
                "field_code": "operations.operation_details",
                "instruction": "完整保留方向和时序。",
                "enabled": True,
            }],
        })
        translator = DrillingReportTranslator(FakeLocalEngine(), self.terms, tuning=tuning)

        matching = translator.prompt_preview(
            "DRILL AHEAD",
            "zh-CN",
            report_context={"report_type": "drilling"},
            event_context={"section": "operations", "content_role": "operation_details"},
            field_code="operations.operation_details",
        )
        other = translator.prompt_preview(
            "DRILL AHEAD",
            "zh-CN",
            report_context={"report_type": "drilling"},
            event_context={"section": "report_fields", "content_role": "currentOps"},
            field_code="report_fields.currentOps",
        )

        self.assertIn("已验证经验：完整保留方向和时序。", matching)
        self.assertNotIn("完整保留方向和时序。", other)

    def test_data_driven_protection_masks_and_restores_original_units(self) -> None:
        engine = ProtectedTokenEngine()
        terms = TermsConfig.from_data({"protected_terms": {"units": ["ft", "ft/hr"]}})
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "DRILL FROM 3,200 FT AT 17.5 ft/hr."},
        })

        model_text = engine.items[0]["source_text"]
        translated_text = result["translation_content"][0]["translated_text"]
        self.assertNotIn("3,200", model_text)
        self.assertNotIn("FT", model_text)
        self.assertNotIn("ft/hr", model_text)
        self.assertEqual(len(re.findall(r"\[\[P\d+]]", model_text)), 2)
        self.assertIn("3,200 FT", translated_text)
        self.assertIn("17.5 ft/hr", translated_text)

    def test_openai_compatible_uses_hard_unit_protection_and_longest_compound_match(self) -> None:
        engine = ProtectedTokenEngine()
        engine.name = "openai-compatible"
        terms = TermsConfig.from_data({"protected_terms": {"units": ["ft", "psi", "psi/ft", "ft/hr"]}})
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "GRADIENT 0.16 PSI/FT; DRILL AT 45 FT/HR."},
        })

        model_text = engine.items[0]["source_text"]
        translated_text = result["translation_content"][0]["translated_text"]
        self.assertEqual(len(re.findall(r"\[\[P\d+]]", model_text)), 2)
        self.assertNotIn("PSI/FT", model_text)
        self.assertNotIn("FT/HR", model_text)
        self.assertIn("0.16 PSI/FT", translated_text)
        self.assertIn("45 FT/HR", translated_text)

    def test_protected_unit_is_not_rewritten_by_post_translation_glossary(self) -> None:
        engine = ProtectedTokenEngine()
        engine.name = "openai-compatible"
        terms = TermsConfig.from_data({
            "terms": [{"id": "rpm", "en": "RPM", "zh": "转速", "protected": True, "enabled": True}],
            "protected_terms": {"units": ["rpm"]},
        })
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "ROTATE AT 120 RPM."},
        })

        translated_text = result["translation_content"][0]["translated_text"]
        self.assertIn("120 RPM", translated_text)
        self.assertNotIn("转速", translated_text)

    def test_placeholder_failure_recovers_with_structured_segments(self) -> None:
        engine = PlaceholderRejectingEngine()
        terms = TermsConfig.from_data({"protected_terms": {"units": ["ft"]}})
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", retry_count=0, tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "DRILL TO 3200 FT."},
        })

        row = result["translation_content"][0]
        self.assertEqual(row["translation_status"], "COMPLETED")
        self.assertEqual(row["translated_text"], "已翻译 3200 FT.")
        self.assertEqual(engine.calls, 3)
        self.assertTrue(any("[[P" in str(item.get("source_text", "")) for item in engine.items))
        self.assertTrue(any("[[P" not in str(item.get("source_text", "")) for item in engine.items))

    def test_placeholder_dense_item_uses_segments_before_model_request(self) -> None:
        engine = PlaceholderRejectingEngine()
        terms = TermsConfig.from_data({"protected_terms": {"units": ["ft", "psi"]}})
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", retry_count=0, tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "DRILL 100 FT, 200 FT, 300 FT; TEST 400 PSI AND 500 PSI."},
        })

        self.assertEqual(result["translation_content"][0]["translation_status"], "COMPLETED")
        self.assertTrue(engine.items)
        self.assertTrue(any("[[P" in str(item.get("source_text", "")) for item in engine.items))
        self.assertTrue(any("[[P" not in str(item.get("source_text", "")) for item in engine.items))

    def test_unchanged_generated_identifier_fragment_is_valid(self) -> None:
        item = {
            "id": "4::protected-part-8",
            "source_text": "[[P30]]” [[P31]] JSHET [[P32]]",
            "preserve_terms": [],
        }

        self.assertEqual(
            _openai_item_quality_error(item, item["source_text"], "zh-CN"),
            "",
        )

    def test_unchanged_uppercase_prose_fragment_still_fails_quality(self) -> None:
        item = {
            "id": "4::protected-part-8",
            "source_text": "[[P30]] CONTINUE DRILLING [[P31]] [[P32]]",
            "preserve_terms": [],
        }

        self.assertEqual(
            _openai_item_quality_error(item, item["source_text"], "zh-CN"),
            "source text was returned unchanged",
        )

    def test_all_protected_identifiers_skip_model_instead_of_failing_source_copy(self) -> None:
        engine = PlaceholderRejectingEngine()
        terms = TermsConfig.from_data({
            "protected_terms": {"acronyms": ["TCP", "PURE", "WO#01"]},
        })
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", retry_count=0)

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "TCP + PURE - WO#01"},
        })

        row = result["translation_content"][0]
        self.assertEqual(row["translation_status"], "NOT_REQUIRED")
        self.assertEqual(row["translated_text"], "TCP + PURE - WO#01")
        self.assertEqual(engine.calls, 0)

    def test_digit_glued_word_is_not_treated_as_preserved_identifier(self) -> None:
        translator = DrillingReportTranslator(
            ProtectedTokenEngine(),
            TermsConfig.from_data({}),
            target_language="zh-CN",
        )

        preserved = translator._preserve_terms("177.00INCIDENTES SIN REPORTAR", [])

        self.assertNotIn("00INCIDENTES", preserved)

    def test_standalone_numbers_use_compact_protection_and_restore_precision(self) -> None:
        engine = ProtectedTokenEngine()
        translator = DrillingReportTranslator(engine, TermsConfig.from_data({}), target_language="zh-CN", retry_count=0, tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "REPORT 2026 HAS 15 ITEMS."},
        })

        self.assertNotIn("2026", engine.items[0]["source_text"])
        self.assertEqual(result["translation_content"][0]["translation_status"], "COMPLETED")
        self.assertIn("2026", result["translation_content"][0]["translated_text"])
        self.assertIn("15", result["translation_content"][0]["translated_text"])

    def test_compact_technical_time_is_protected_without_false_extra_numbers(self) -> None:
        engine = ProtectedTokenEngine()
        translator = DrillingReportTranslator(engine, TermsConfig.from_data({}), target_language="zh-CN", retry_count=0, tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "INGRESA EL 25-01-2026 A LAS 06H00 AM."},
        })

        self.assertNotIn("06H00", engine.items[0]["source_text"])
        self.assertEqual(result["translation_content"][0]["translation_status"], "COMPLETED")
        self.assertIn("06H00", result["translation_content"][0]["translated_text"])

    def test_spanish_numeric_ordinals_are_protected_as_complete_values(self) -> None:
        engine = ProtectedTokenEngine()
        translator = DrillingReportTranslator(engine, TermsConfig.from_data({}), target_language="zh-CN", retry_count=0, tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "OBSERVA RUPTURA DE 1er. TAPON Y LIBERA 2do. TAPON."},
        })

        model_text = engine.items[0]["source_text"]
        self.assertNotIn("1er.", model_text)
        self.assertNotIn("2do.", model_text)
        self.assertEqual(result["translation_content"][0]["translation_status"], "COMPLETED")
        self.assertIn("1er.", result["translation_content"][0]["translated_text"])
        self.assertIn("2do.", result["translation_content"][0]["translated_text"])

    def test_decimal_touching_following_text_is_protected_as_one_value(self) -> None:
        engine = ProtectedTokenEngine()
        translator = DrillingReportTranslator(engine, TermsConfig.from_data({}), target_language="zh-CN", retry_count=0, tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"incidentComments": "N Days since Last LTA 188.00INCIDENTES SIN REPORTAR EN 24 HORAS."},
        })

        self.assertNotIn("188.00", engine.items[0]["source_text"])
        self.assertEqual(result["translation_content"][0]["translation_status"], "COMPLETED")
        self.assertIn("188.00", result["translation_content"][0]["translated_text"])

    def test_numeric_month_localization_is_not_treated_as_an_extra_value(self) -> None:
        translator = DrillingReportTranslator(
            MonthLocalizationEngine(),
            TermsConfig.from_data({}),
            target_language="zh-CN",
            retry_count=0,
        )

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "DESDE EL 8 DE MAYO DE 2026."},
        })

        row = result["translation_content"][0]
        self.assertEqual(row["translation_status"], "COMPLETED")
        self.assertIn("5月", row["translated_text"])

    def test_unit_identifier_digit_is_not_treated_as_a_changed_value(self) -> None:
        translator = DrillingReportTranslator(
            SuperscriptUnitEngine(),
            TermsConfig.from_data({}),
            target_language="zh-CN",
            retry_count=0,
        )

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "VOLUMEN 54.99 M3."},
        })

        row = result["translation_content"][0]
        self.assertEqual(row["translation_status"], "COMPLETED")
        self.assertIn("54.99 m³", row["translated_text"])

    def test_protection_rules_are_compiled_from_current_configuration(self) -> None:
        engine = ProtectedTokenEngine()
        terms = TermsConfig.from_data({"protected_terms": {"units": ["kPa"]}})
        translator = DrillingReportTranslator(
            engine,
            terms,
            target_language="zh-CN",
            tuning=legacy_tuning(protect_numbers=False),
        )

        translator.translate_report_payload({
            "report_fields": {"currentOps": "PRESSURE 500 kPa AND DEPTH 3200 FT."},
        })

        model_text = engine.items[0]["source_text"]
        self.assertNotIn("kPa", model_text)
        self.assertIn("3200 FT", model_text)

    def test_global_acronyms_proper_nouns_and_ambiguous_units_use_context(self) -> None:
        engine = ProtectedTokenEngine()
        terms = TermsConfig.from_data({
            "protected_terms": {"acronyms": ["BHA"], "units": ["in"], "proper_nouns": ["SINOPEC"]},
        })
        translator = DrillingReportTranslator(
            engine,
            terms,
            target_language="zh-CN",
            tuning=legacy_tuning(ambiguous_units=("in",)),
        )

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "WORK IN HOLE WITH BHA FOR SINOPEC, 12.25 in section."},
        })

        model_text = engine.items[0]["source_text"]
        self.assertIn("WORK IN HOLE", model_text)
        self.assertNotIn("BHA", model_text)
        self.assertNotIn("SINOPEC", model_text)
        self.assertNotIn("12.25 in", model_text)
        translated_text = result["translation_content"][0]["translated_text"]
        self.assertIn("BHA", translated_text)
        self.assertIn("SINOPEC", translated_text)
        self.assertIn("12.25 in", translated_text)

    def test_global_acronyms_require_exact_case(self) -> None:
        terms = TermsConfig.from_data({"protected_terms": {"acronyms": ["ES"]}})
        translator = DrillingReportTranslator(ProtectedTokenEngine(), terms, target_language="zh-CN")

        self.assertEqual(translator._preserve_terms("el pozo es vertical", []), [])
        self.assertEqual(translator._preserve_terms("REVISAR ES ANTES DE PERFORAR", []), ["ES"])

    def test_unicode_word_boundary_does_not_treat_linea_as_litre(self) -> None:
        terms = TermsConfig.from_data({"protected_terms": {"units": ["l"]}})
        translator = DrillingReportTranslator(ProtectedTokenEngine(), terms, target_language="zh-CN")

        checks = translator.quality_checks(
            "INSTALA LÍNEA CAPILAR Y PRUEBA LÍNEAS.",
            "安装毛细管线并测试管线。",
        )

        unit_check = next(check for check in checks if check["rule"] == "unit_integrity")
        self.assertEqual(unit_check["status"], "passed")

    def test_unit_boundary_allows_multiplication_sign_separator(self) -> None:
        terms = TermsConfig.from_data({"protected_terms": {"units": ["ppg"]}})
        translator = DrillingReportTranslator(ProtectedTokenEngine(), terms, target_language="zh-CN")

        checks = translator.quality_checks(
            "BOMBEA 8.5 ppg X 120 SEG.",
            "泵入8.5 ppg×120秒。",
        )

        unit_check = next(check for check in checks if check["rule"] == "unit_integrity")
        self.assertEqual(unit_check["status"], "passed")

    def test_localized_units_and_clock_suffix_are_semantically_valid(self) -> None:
        terms = TermsConfig.from_data({
            "protected_terms": {"units": ["l", "ton", "m3", "hrs"]},
        })
        tuning = TranslationTuningConfig(
            ambiguous_units=("l",),
            unit_aliases=(
                ("l", ("升",)),
                ("ton", ("吨",)),
                ("m3", ("立方米",)),
                ("hrs", ("小时",)),
            ),
            unit_context_exclusions=(("hrs", r"\b\d{1,2}:\d{2}\s+HRS\b"),),
        )
        translator = DrillingReportTranslator(
            ProtectedTokenEngine(),
            terms,
            target_language="zh-CN",
            tuning=tuning,
        )

        checks = translator.quality_checks(
            "MUEVE 2 TON, 3 M3 Y BOMBEA 60 L; INICIA A LAS 06:00 HRS.",
            "搬运2吨、3立方米并泵入60升；于06:00开始。",
        )

        unit_check = next(check for check in checks if check["rule"] == "unit_integrity")
        self.assertEqual(unit_check["status"], "passed")

    def test_m_in_m_lwd_is_not_treated_as_metre_unit(self) -> None:
        engine = ProtectedTokenEngine()
        terms = TermsConfig.from_data({"protected_terms": {"units": ["m"]}})
        translator = DrillingReportTranslator(
            engine,
            terms,
            target_language="zh-CN",
            tuning=legacy_tuning(
                ambiguous_units=("m",),
                unit_context_exclusions=(("m", r"\bM\s*/\s*[A-Z]{2,}\b"),),
            ),
        )

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "PERFORA CON HTAS. M/ LWD EN FORMACION TENA."},
        })

        self.assertEqual(result["translation_content"][0]["translation_status"], "COMPLETED")
        self.assertIn("M/ LWD", engine.items[0]["source_text"])

    def test_contextual_placeholder_mode_enforces_global_protection(self) -> None:
        engine = ProtectedTokenEngine()
        terms = TermsConfig.from_data({
            "protected_terms": {"units": ["gpm", "rpm", "ppg"]},
        })
        translator = DrillingReportTranslator(
            engine,
            terms,
            target_language="zh-CN",
            tuning=TranslationTuningConfig(protection_mode="placeholder"),
        )

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "BOMBEA 450 GPM A 120 RPM CON LODO 11.0 PPG."},
        })

        model_text = engine.items[0]["source_text"]
        self.assertNotIn("450 GPM", model_text)
        self.assertNotIn("120 RPM", model_text)
        self.assertNotIn("11.0 PPG", model_text)
        translated = result["translation_content"][0]["translated_text"]
        self.assertIn("450 GPM", translated)
        self.assertIn("120 RPM", translated)
        self.assertIn("11.0 PPG", translated)

    def test_unit_context_exclusions_are_loaded_from_tuning(self) -> None:
        terms = TermsConfig.from_data({
            "protected_terms": {"units": ["ft", "h", "in"]},
        })
        tuning = TranslationTuningConfig(
            ambiguous_units=("h", "in"),
            unit_context_exclusions=(
                ("h", r"\bH\s*/\s*[-+]?\d"),
                ("in", r"(?i)\bDRILL[\s-]*IN\b"),
                ("in", r"\bIN\s*/\s*OUT\b"),
            ),
        )
        translator = DrillingReportTranslator(
            ProtectedTokenEngine(),
            terms,
            target_language="zh-CN",
            tuning=tuning,
        )

        checks = translator.quality_checks(
            "VIAJE D/ 11453 FT, H/ 11200 FT CON FLUIDO DRILL-IN IN/OUT.",
            "从11453 FT至11200 FT，使用DRILL-IN流体进出。",
        )

        unit_check = next(check for check in checks if check["rule"] == "unit_integrity")
        self.assertEqual(unit_check["status"], "passed")

    def test_locked_glossary_term_is_restored_to_configured_target(self) -> None:
        engine = ProtectedTokenEngine()
        terms = TermsConfig.from_data({
            "terms": [{"id": "dp", "en": "drill pipe", "zh": "钻杆", "protected": True, "enabled": True}],
            "protected_terms": {},
        })
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "RUN DRILL PIPE."},
        })

        row = result["translation_content"][0]
        self.assertEqual(engine.calls, 0)
        self.assertEqual(row["translation_status"], "COMPLETED")
        self.assertIn("钻杆", row["translated_text"])

    def test_missing_protected_placeholder_is_retried_then_rejected(self) -> None:
        engine = ProtectedTokenEngine(drop_tokens=True)
        terms = TermsConfig.from_data({"protected_terms": {"units": ["ft"]}})
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", retry_count=1, tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "DRILL TO 3200 FT."},
        })

        row = result["translation_content"][0]
        self.assertEqual(engine.calls, 2)
        self.assertEqual(row["translation_status"], "FAILED")
        self.assertIn("protected placeholders", row["error_message"])

    def test_batch_placeholder_failure_retries_only_the_invalid_item(self) -> None:
        engine = PartialFailureEngine()
        terms = TermsConfig.from_data({"protected_terms": {"units": ["ft"]}})
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", retry_count=0, tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {
                "currentOps": "DRILL TO 3200 FT.",
                "summary24h": "PULL TO 1200 FT.",
            },
        })

        self.assertEqual(engine.batch_sizes, [2, 1])
        self.assertTrue(all(row["translation_status"] == "COMPLETED" for row in result["translation_content"]))

    def test_transport_failure_does_not_expand_batch_into_per_item_calls(self) -> None:
        engine = OfflineEngine()
        translator = DrillingReportTranslator(engine, self.terms, target_language="zh-CN", retry_count=3)

        result = translator.translate_report_payload({
            "report_fields": {
                "currentOps": "DRILL AHEAD WITH STABLE RETURNS.",
                "summary24h": "CIRCULATE BOTTOMS UP UNTIL CLEAN.",
            }
        })

        self.assertEqual(engine.calls, 1)
        self.assertTrue(all(row["translation_status"] == "FAILED" for row in result["translation_content"]))

    @patch("drilling_report_parser.translation.service.time.sleep")
    def test_open_circuit_waits_for_cooldown_then_retries(self, sleep) -> None:
        engine = CoolingDownEngine()
        translator = DrillingReportTranslator(engine, self.terms, target_language="zh-CN", retry_count=1)

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "DRILL AHEAD WITH STABLE RETURNS."},
        })

        self.assertEqual(engine.calls, 2)
        sleep.assert_called_once_with(2.5)
        self.assertEqual(result["translation_content"][0]["translation_status"], "COMPLETED")

    @patch("drilling_report_parser.translation.service.time.sleep")
    @patch("drilling_report_parser.translation.service.time.monotonic", side_effect=[100.0, 103.0])
    def test_provider_circuit_cooldown_wait_does_not_raise(self, _monotonic, sleep) -> None:
        key = "https://provider.test"
        with _PROVIDER_CIRCUIT_LOCK:
            _PROVIDER_CIRCUITS[key] = {"failures": 2.0, "opened_until": 103.0}

        _check_provider_circuit(key)

        sleep.assert_called_once_with(3.0)
        with _PROVIDER_CIRCUIT_LOCK:
            self.assertNotIn(key, _PROVIDER_CIRCUITS)

    def test_rejects_numbers_added_by_the_model(self) -> None:
        translator = DrillingReportTranslator(
            ExtraNumberEngine(),
            TermsConfig.from_data({}),
            target_language="zh-CN",
            retry_count=0,
        )

        result = translator.translate_report_payload({"report_fields": {"currentOps": "DRILL TO 3200 FT."}})

        row = result["translation_content"][0]
        self.assertEqual(row["translation_status"], "FAILED")
        self.assertIn("extra=['999']", row["error_message"])

    def test_translation_memory_hit_skips_model_request(self) -> None:
        engine = ProtectedTokenEngine()
        source = "DRILL AHEAD WITH STABLE RETURNS."
        translator = DrillingReportTranslator(
            engine,
            TermsConfig.from_data({}),
            target_language="zh-CN",
            translation_memory={source_hash(source): "继续钻进，返出稳定。"},
        )

        result = translator.translate_report_payload({"report_fields": {"currentOps": source}})

        self.assertEqual(engine.calls, 0)
        self.assertEqual(result["translation_content"][0]["translated_text"], "继续钻进，返出稳定。")

    def test_prompt_only_includes_protections_hit_by_current_text(self) -> None:
        terms = TermsConfig.from_data({"protected_terms": {"units": ["ft", "psi"], "acronyms": ["BHA"]}})
        translator = DrillingReportTranslator(ProtectedTokenEngine(), terms, target_language="zh-CN", tuning=legacy_tuning())

        preview = translator.prompt_preview("DRILL TO 3200 ft.", "zh-CN")

        self.assertIn("[[P0]]", preview)
        self.assertNotIn("psi", preview)
        self.assertNotIn("BHA", preview.split("Input JSON:\n", 1)[1])

    def test_reordered_protected_placeholders_are_allowed_when_all_are_preserved(self) -> None:
        engine = ProtectedTokenEngine(reverse_tokens=True)
        terms = TermsConfig.from_data({"protected_terms": {"units": ["ft"]}})
        translator = DrillingReportTranslator(engine, terms, target_language="zh-CN", retry_count=0, tuning=legacy_tuning())

        result = translator.translate_report_payload({
            "report_fields": {"currentOps": "DRILL FROM 3200 FT TO 5300 FT."},
        })

        row = result["translation_content"][0]
        self.assertEqual(row["translation_status"], "COMPLETED")
        self.assertIn("3200 FT", row["translated_text"])
        self.assertIn("5300 FT", row["translated_text"])

    def test_openai_compatible_batches_larger_translation_chunks(self) -> None:
        engine = CountingEngine()
        translator = DrillingReportTranslator(engine, self.terms, target_language="zh-CN", chunk_max_chars=2400)
        text = "PERFORA SECCION DIRECCIONAL Y CIRCULA RETORNOS LIMPIOS. " * 10
        payload = {
            "report_fields": {
                "currentOps": text,
                "summary24h": text,
                "forecast24h": text,
            }
        }

        result = translator.translate_report_payload(payload)

        self.assertEqual(len(result["translation_content"]), 3)
        self.assertEqual(engine.calls, 1)
        self.assertEqual(engine.batch_sizes, [3])

    def test_large_report_splits_at_business_module_boundaries(self) -> None:
        engine = CountingEngine()
        translator = DrillingReportTranslator(engine, TermsConfig.from_data({}), target_language="zh-CN", chunk_max_chars=500)
        text = "DRILL AHEAD WITH STABLE RETURNS AND MONITOR ALL PARAMETERS. " * 4
        payload = {
            "metadata": {"record_id": "drilling:CTX-1:2026-07-12:1", "report_type": "drilling"},
            "report_fields": {"currentOps": text, "summary24h": text},
            "operations": [
                {"row_no": "1", "operation_details": text},
                {"row_no": "2", "operation_details": text},
            ],
        }

        rows = translator.translate_report_payload(payload)["translation_content"]

        self.assertEqual(len(rows), 4)
        self.assertEqual(engine.calls, 2)
        self.assertEqual(
            [{item["context_group"] for item in batch} for batch in engine.batches],
            [{"report_fields"}, {"operations"}],
        )

    @patch("drilling_report_parser.translation.service._post_json")
    def test_openai_compatible_retries_unchanged_batch_items_individually_with_strict_prompt(self, post_json) -> None:
        sources = {
            "0": "BAJANDO CASING HASTA FONDO.",
            "1": "CIRCULA HASTA RETORNOS LIMPIOS.",
        }

        def response(items):
            return {
                "choices": [{
                    "message": {
                        "content": '{"items":[' + ",".join(
                            f'{{"id":"{item_id}","translated_text":"{text}"}}'
                            for item_id, text in items
                        ) + "]}",
                    }
                }]
            }

        post_json.side_effect = [
            response(list(sources.items())),
            response([("0", "下入套管至井底。")]),
            response([("1", "循环至返出干净。")]),
        ]
        engine = OpenAICompatibleTranslationEngine("https://example.test", "test-model", "secret")
        items = [
            {"id": item_id, "source_language": "es", "source_text": text, "glossary": []}
            for item_id, text in sources.items()
        ]

        translated = engine.translate_items(items, "zh-CN", 60)

        self.assertEqual(translated, {"0": "下入套管至井底。", "1": "循环至返出干净。"})
        self.assertEqual(post_json.call_count, 3)
        for call in post_json.call_args_list[1:]:
            prompt = call.args[1]["messages"][1]["content"]
            self.assertIn("上一次结果未满足完整性要求", prompt)
            self.assertNotIn("/no_think", prompt)

    @patch("drilling_report_parser.translation.service._post_json")
    def test_openai_compatible_only_retries_invalid_batch_items(self, post_json) -> None:
        post_json.side_effect = [
            {
                "choices": [{"message": {"content": (
                    '{"items":['
                    '{"id":"0","translated_text":"已完成中文翻译。"},'
                    '{"id":"1","translated_text":"CIRCULA HASTA RETORNOS LIMPIOS."}'
                    "]}"
                )}}]
            },
            {
                "choices": [{"message": {"content": (
                    '{"items":[{"id":"1","translated_text":"循环至返出干净。"}]}'
                )}}]
            },
        ]
        engine = OpenAICompatibleTranslationEngine("https://example.test", "test-model")
        items = [
            {"id": "0", "source_language": "es", "source_text": "BAJANDO CASING.", "glossary": []},
            {"id": "1", "source_language": "es", "source_text": "CIRCULA HASTA RETORNOS LIMPIOS.", "glossary": []},
        ]

        translated = engine.translate_items(items, "zh-CN", 60)

        self.assertEqual(translated["0"], "已完成中文翻译。")
        self.assertEqual(translated["1"], "循环至返出干净。")
        self.assertEqual(post_json.call_count, 2)
        retry_prompt = post_json.call_args_list[1].args[1]["messages"][1]["content"]
        self.assertIn('"id": "1"', retry_prompt)
        self.assertNotIn('"id": "0"', retry_prompt)

    @patch("drilling_report_parser.translation.service._post_json")
    def test_openai_compatible_retries_only_item_that_lost_placeholder(self, post_json) -> None:
        post_json.side_effect = [
            {"choices": [{"message": {"content": '{"items":[{"id":"0","translated_text":"已完成翻译。"}]}'}}]},
            {"choices": [{"message": {"content": '{"items":[{"id":"0","translated_text":"已完成翻译 [[P0]]。"}]}'}}]},
        ]
        engine = OpenAICompatibleTranslationEngine("https://example.test", "test-model")

        translated = engine.translate_items(
            [{"id": "0", "source_language": "en", "source_text": "DRILL TO [[P0]].", "glossary": []}],
            "zh-CN",
            60,
        )

        self.assertEqual(translated["0"], "已完成翻译 [[P0]]。")
        self.assertEqual(post_json.call_count, 2)
        self.assertIn("上一次结果未满足完整性要求", post_json.call_args_list[1].args[1]["messages"][1]["content"])

    @patch("drilling_report_parser.translation.service._post_json")
    def test_openai_translation_preserves_source_layout_and_uses_report_context(self, post_json) -> None:
        def response(_url, payload, _timeout, **_kwargs):
            prompt = payload["messages"][1]["content"]
            request_item = json.loads(prompt.split("Input JSON:\n", 1)[1])["items"][0]
            return {"choices": [{"message": {"content": json.dumps({
                "items": [{"id": "0", "translated_text": "下入 BHA。\n- 进行压力试验 3000 PSI。"}],
            }, ensure_ascii=False)}}]}

        post_json.side_effect = response
        terms = TermsConfig.from_data({"protected_terms": {"acronyms": ["BHA"]}})
        translator = DrillingReportTranslator(
            OpenAICompatibleTranslationEngine("https://example.test", "test-model"),
            terms,
            target_language="zh-CN",
            retry_count=0,
        )
        source = "RUN BHA.\n- PRESSURE TEST 3000 PSI."

        result = translator.translate_report_payload({
            "metadata": {"record_id": "drilling:TEST-1:2026-07-12:1", "report_type": "drilling"},
            "report_fields": {"currentOps": source, "wellbore": "TEST-1", "rig": "RIG-9", "reportDate": "2026-07-12"},
        })

        row = result["translation_content"][0]
        self.assertEqual(row["translation_status"], "COMPLETED")
        self.assertEqual(row["translated_text"].count("\n"), 1)
        self.assertEqual(post_json.call_count, 1)
        first_prompt = post_json.call_args_list[0].args[1]["messages"][1]["content"]
        request_items = json.loads(first_prompt.split("Input JSON:\n", 1)[1])["items"]
        self.assertEqual(request_items[0]["source_text"], source)
        self.assertIn('"wellbore": "TEST-1"', first_prompt)
        self.assertIn('"rig": "RIG-9"', first_prompt)
        self.assertEqual(len(re.findall(r"\[\[P\d+]]", request_items[0]["source_text"])), 0)
        self.assertEqual(request_items[0]["preserve_terms"], ["BHA"])

    @patch("drilling_report_parser.translation.service._post_json")
    def test_provider_telemetry_records_full_request_and_raw_response_without_api_key(self, post_json) -> None:
        raw_response = {"choices": [{"message": {"content": '{"items":[{"id":"0","translated_text":"继续钻进。"}]}'}}], "usage": {"total_tokens": 42}}
        post_json.return_value = raw_response
        events = []
        engine = OpenAICompatibleTranslationEngine(
            "https://example.test",
            "test-model",
            api_key="top-secret",
            telemetry=events.append,
        )

        translated = engine.translate_items(
            [{"id": "0", "source_language": "en", "source_text": "DRILL AHEAD.", "glossary": []}],
            "zh-CN",
            60,
        )

        self.assertEqual(translated["0"], "继续钻进。")
        request_event, response_event = events
        self.assertEqual(request_event["event"], "model_wire_request")
        self.assertIn("DRILL AHEAD.", json.dumps(request_event["request_payload"], ensure_ascii=False))
        self.assertNotIn("top-secret", json.dumps(request_event, ensure_ascii=False))
        self.assertEqual(response_event["event"], "model_wire_response")
        self.assertEqual(response_event["raw_response"], raw_response)

    def test_description_is_translated_as_one_paragraph(self) -> None:
        engine = CountingEngine()
        translator = DrillingReportTranslator(
            engine,
            TermsConfig.from_data({}),
            target_language="zh-CN",
            retry_count=0,
        )
        source = "RUN COMPLETION STRING\nTO PRODUCTION DEPTH."

        result = translator.translate_report_payload({"report_fields": {"description": source}})

        row = result["translation_content"][0]
        model_item = engine.batches[0][0]
        self.assertEqual(row["source_text"], source)
        self.assertNotIn("\n", model_item["source_text"])
        self.assertEqual(model_item["source_text"], "RUN COMPLETION STRING TO PRODUCTION DEPTH.")
        self.assertNotIn("\n", row["translated_text"])
        self.assertTrue(model_item["paragraph_layout"])

    @patch("drilling_report_parser.translation.service._post_json")
    def test_openai_compatible_retries_truncated_json_with_strict_prompt(self, post_json) -> None:
        post_json.side_effect = [
            {
                "choices": [{
                    "finish_reason": "length",
                    "message": {"content": '{"items":[{"id":"0","translated_text":"继续'},
                }]
            },
            {
                "choices": [{
                    "finish_reason": "stop",
                    "message": {"content": '{"items":[{"id":"0","translated_text":"继续钻进。"}]}'},
                }]
            },
        ]
        engine = OpenAICompatibleTranslationEngine("https://example.test", "test-model")

        translated = engine.translate_items(
            [{"id": "0", "source_language": "en", "source_text": "DRILL AHEAD.", "glossary": []}],
            "zh-CN",
            60,
        )

        self.assertEqual(translated, {"0": "继续钻进。"})
        self.assertEqual(post_json.call_count, 2)
        retry_prompt = post_json.call_args_list[1].args[1]["messages"][1]["content"]
        self.assertIn("上一次结果未满足完整性要求", retry_prompt)
        self.assertGreaterEqual(post_json.call_args_list[0].args[1]["max_tokens"], 4096)

    @patch("drilling_report_parser.translation.service._post_json")
    def test_openai_compatible_splits_long_items_before_request(self, post_json) -> None:
        def response(_url, payload, _timeout, **_kwargs):
            prompt = payload["messages"][1]["content"]
            request_items = json.loads(prompt.split("Input JSON:\n", 1)[1])["items"]
            content = {
                "items": [
                    {"id": item["id"], "translated_text": "已翻译该段内容。"}
                    for item in request_items
                ]
            }
            return {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(content, ensure_ascii=False)}}]}

        post_json.side_effect = response
        engine = OpenAICompatibleTranslationEngine("https://example.test", "test-model")
        source = "DRILL AHEAD WITH STABLE RETURNS. " * 400

        translated = engine.translate_items(
            [{"id": "0", "source_language": "en", "source_text": source, "glossary": []}],
            "zh-CN",
            60,
        )

        self.assertGreater(post_json.call_count, 1)
        self.assertTrue(translated["0"].startswith("已翻译"))

    @patch("drilling_report_parser.translation.service._post_json")
    def test_openai_prompt_keeps_provider_specific_directives_out_of_user_message(self, post_json) -> None:
        post_json.return_value = {
            "choices": [{"message": {"content": '{"items":[{"id":"0","translated_text":"继续钻进。"}]}'}}]
        }
        engine = OpenAICompatibleTranslationEngine("https://example.test", "test-model")

        engine.translate_items(
            [{"id": "0", "source_language": "en", "source_text": "DRILL AHEAD.", "glossary": [], "prompt_context": {"system_prompt": "SYSTEM ROLE"}}],
            "zh-CN",
            60,
        )

        payload = post_json.call_args.args[1]
        self.assertIn("SYSTEM ROLE", payload["messages"][0]["content"])
        self.assertNotIn("SYSTEM ROLE", payload["messages"][1]["content"])
        self.assertNotIn("/no_think", payload["messages"][1]["content"])
        self.assertGreaterEqual(payload["max_tokens"], 4096)

    @patch("drilling_report_parser.translation.service._post_json")
    def test_lm_studio_qwen_disabled_thinking_uses_prefill_and_template_switch(self, post_json) -> None:
        post_json.return_value = {
            "choices": [{"message": {"content": '{"items":[{"id":"0","translated_text":"继续钻进。"}]}'}}]
        }
        engine = OpenAICompatibleTranslationEngine(
            "http://127.0.0.1:1234/v1",
            "qwen3.5-9b",
            thinking_mode="disabled",
        )

        engine.translate_items(
            [{"id": "0", "source_language": "en", "source_text": "DRILL AHEAD.", "glossary": []}],
            "zh-CN",
            60,
        )

        payload = post_json.call_args.args[1]
        self.assertEqual(payload["chat_template_kwargs"], {"enable_thinking": False})
        self.assertEqual(payload["messages"][-1], {"role": "assistant", "content": "<think>\n\n</think>\n\n"})

    @patch("drilling_report_parser.translation.service._post_json")
    def test_deepseek_disabled_thinking_uses_deepseek_control_and_manual_options(self, post_json) -> None:
        post_json.return_value = {
            "choices": [{"message": {"content": '{"items":[{"id":"0","translated_text":"继续钻进。"}]}'}}]
        }
        engine = OpenAICompatibleTranslationEngine(
            "https://api.deepseek.com",
            "deepseek-v4-pro",
            thinking_mode="disabled",
            request_options={"reasoning_effort": "high"},
        )

        engine.translate_items(
            [{"id": "0", "source_language": "en", "source_text": "DRILL AHEAD.", "glossary": []}],
            "zh-CN",
            60,
        )

        payload = post_json.call_args.args[1]
        self.assertEqual(payload["thinking"], {"type": "disabled"})
        self.assertEqual(payload["reasoning_effort"], "high")
        self.assertNotIn("chat_template_kwargs", payload)

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

    def test_source_hash_distinguishes_paragraph_layout(self) -> None:
        self.assertNotEqual(source_hash("FIRST LINE\nSECOND LINE"), source_hash("FIRST LINE SECOND LINE"))


if __name__ == "__main__":
    unittest.main()
