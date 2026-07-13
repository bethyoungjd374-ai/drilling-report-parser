from __future__ import annotations

import hashlib
import http.client
import json
import os
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from drilling_report_parser import excel_database, form_server
from drilling_report_parser.excel_database import load_report_payload
from tests.test_pdf_report_parser import sample_pdf


class FormServerImportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repository_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.repository_tmp.cleanup)
        self.repository_path = Path(self.repository_tmp.name) / "report_database.xlsx"
        original_database_path = form_server.DATABASE_PATH
        form_server.DATABASE_PATH = self.repository_path
        self.addCleanup(setattr, form_server, "DATABASE_PATH", original_database_path)

        def repository(path: Path | str | None) -> Path:
            value = Path(path or self.repository_path)
            return self.repository_path if value == Path("mysql") else value

        def save_payload(path: Path, payload: dict[str, Any], report_type: str, **kwargs: Any) -> dict[str, Any]:
            kwargs.pop("invalidate_translations", None)
            return excel_database.save_report_payload(repository(path), payload, report_type, **kwargs)

        def load_payload(path: Path, record_id: str) -> dict[str, Any]:
            return excel_database.load_report_payload(repository(path), record_id)

        def load_payloads(path: Path, record_ids: list[str], **_kwargs: Any) -> dict[str, dict[str, Any]]:
            payloads = {}
            for record_id in record_ids:
                try:
                    payloads[record_id] = excel_database.load_report_payload(repository(path), record_id)
                except KeyError:
                    continue
            return payloads

        def operation_translations(path: Path, record_ids: list[str]) -> list[dict[str, str]]:
            return [
                row
                for record_id in record_ids
                for row in excel_database.load_translation_content(repository(path), record_id)
                if str(row.get("entity_type", "")) == "operations"
            ]

        def records(path: Path | None = None, **filters: str) -> list[dict[str, str]]:
            values = excel_database.list_records(repository(path))
            return [
                row for row in values
                if (not filters.get("report_type") or row.get("report_type") == filters["report_type"])
                and (not filters.get("wellbore") or row.get("wellbore") == filters["wellbore"])
                and (not filters.get("date") or row.get("reportDate") == filters["date"])
                and (not filters.get("date_from") or str(row.get("reportDate", "")) >= filters["date_from"])
                and (not filters.get("date_to") or str(row.get("reportDate", "")) <= filters["date_to"])
            ]

        patchers = [
            patch.object(form_server, "save_report_payload", side_effect=save_payload),
            patch.object(form_server, "load_report_payload", side_effect=load_payload),
            patch.object(form_server, "load_report_payloads", side_effect=load_payloads),
            patch.object(form_server, "list_records", side_effect=records),
            patch.object(form_server, "load_operation_translations", side_effect=operation_translations),
            patch.object(form_server, "load_extraction_results", return_value=[]),
            patch.object(form_server, "_extraction_jobs_enabled", return_value=False),
        ]
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_report_identity_requires_date_well_and_rig(self) -> None:
        payload = {"report_fields": {"reportDate": "", "wellbore": "PCNC-039", "rig": ""}}

        self.assertEqual(form_server._report_identity_errors(payload), ["日报日期", "井队"])
        self.assertEqual(form_server._report_identity_errors({"report_fields": {
            "reportDate": "2026-05-22", "wellbore": "PCNC-039", "rig": "SINOPEC 248",
        }}), [])

    def test_lm_studio_qwen_disabled_thinking_payload_uses_compatibility_prefill(self) -> None:
        model = {
            "base_url": "http://127.0.0.1:1234/v1",
            "model": "qwen3.5-9b",
            "thinking_mode": "disabled",
        }
        payload = form_server._openai_payload_for_model(model, {
            "model": "qwen3.5-9b",
            "messages": [{"role": "user", "content": "translate"}],
        })

        self.assertEqual(payload["chat_template_kwargs"], {"enable_thinking": False})
        self.assertEqual(payload["messages"][-1], {"role": "assistant", "content": "<think>\n\n</think>\n\n"})

    def test_system_model_temperature_is_fixed_for_deterministic_workflows(self) -> None:
        model = form_server._normalize_ai_model({
            "id": "deterministic-model",
            "name": "Deterministic",
            "api_type": "openai-compatible",
            "base_url": "https://example.test/v1",
            "model": "example-model",
            "temperature": 1.7,
        })

        self.assertNotIn("temperature", model)
        config = form_server._translation_config_for_model(model)
        self.assertEqual(config.openai_temperature, 0.0)

    def test_deepseek_thinking_and_manual_request_options_use_provider_wire_format(self) -> None:
        model = {
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-v4-pro",
            "thinking_mode": "disabled",
            "request_options": {"reasoning_effort": "high"},
        }

        payload = form_server._openai_payload_for_model(model, {
            "model": "deepseek-v4-pro",
            "messages": [{"role": "user", "content": "translate"}],
        })

        self.assertEqual(payload["thinking"], {"type": "disabled"})
        self.assertEqual(payload["reasoning_effort"], "high")
        self.assertNotIn("chat_template_kwargs", payload)

    def test_manual_request_options_cannot_override_core_request_fields(self) -> None:
        options = form_server._normalize_model_request_options({
            "model": "wrong-model",
            "messages": [{"role": "user", "content": "wrong"}],
            "Authorization": "secret",
            "thinking": {"type": "disabled"},
        })

        self.assertEqual(options, {"thinking": {"type": "disabled"}})

    def test_operation_translation_accepts_whitespace_normalization_and_rejects_stale_source(self) -> None:
        source = "WAIT ON SERVICE\nCOMPANY"
        stored_source = "WAIT ON SERVICE COMPANY"
        translation = {
            "source_text": stored_source,
            "source_hash": form_server.hashlib.sha256(stored_source.encode("utf-8")).hexdigest(),
            "translated_text": "等待服务公司",
            "translation_status": "COMPLETED",
        }

        self.assertEqual(form_server._current_operation_translation(source, translation), ("等待服务公司", "COMPLETED"))
        self.assertEqual(form_server._current_operation_translation("DIFFERENT SOURCE", translation), ("", "COMPLETED"))

    def test_production_npt_ranking_includes_rigs_with_zero_npt(self) -> None:
        records = [
            {"rig": "RIG A", "wellbore": "WELL A", "reportDate": "2026-05-22", "report_type": "drilling", "validation_status": "ok"},
            {"rig": "RIG B", "wellbore": "WELL B", "reportDate": "2026-05-22", "report_type": "drilling", "validation_status": "ok"},
        ]
        operations = [
            {**records[0], "hours": 2.0, "op_type": "NPT"},
            {**records[1], "hours": 24.0, "op_type": "P"},
        ]

        with patch.object(form_server, "_filtered_fact_rows", return_value={"records": records, "operations": operations}):
            payload = form_server._production_summary_payload(Path("mysql"), {})

        self.assertEqual(payload["npt_by_rig"], [
            {"label": "RIG A", "hours": 2.0},
            {"label": "RIG B", "hours": 0.0},
        ])

    def test_ai_extraction_rules_validate_source_and_target_fields(self) -> None:
        config = form_server._normalize_ai_extraction_config({
            "rules": [
                {
                    "id": "npt-owner",
                    "name": "NPT责任方",
                    "report_type": "drilling",
                    "source_section": "operations",
                    "source_field": "operation_details",
                    "condition": "仅NPT",
                    "instruction": "提取责任公司",
                    "target_field": "service_line",
                    "output_format": "company",
                    "enabled": True,
                },
                {
                    "id": "invalid-target",
                    "name": "覆盖井号",
                    "report_type": "drilling",
                    "source_section": "report_fields",
                    "source_field": "currentOps",
                    "instruction": "错误规则",
                    "target_field": "wellbore",
                },
            ],
        })

        self.assertEqual(len(config["rules"]), 1)
        self.assertEqual(config["rules"][0]["target_field"], "service_line")
        self.assertIn("target_fields", config["catalog"])

    def test_stopped_extraction_is_available_to_continue(self) -> None:
        self.assertTrue(form_server._extraction_record_needs_processing(
            {"extraction_status": "STOPPED", "extraction_version": "rules-v1"},
            "rules-v1",
        ))
        self.assertFalse(form_server._extraction_record_needs_processing(
            {"extraction_status": "IN_PROGRESS", "extraction_version": "rules-v1"},
            "rules-v1",
        ))

    def test_stop_translation_invalidates_jobs_and_rotates_executor(self) -> None:
        old_executor = Mock()
        new_executor = Mock()
        original_executor = form_server.TRANSLATION_EXECUTOR
        form_server.TRANSLATION_EXECUTOR = old_executor
        self.addCleanup(setattr, form_server, "TRANSLATION_EXECUTOR", original_executor)
        form_server.TRANSLATION_JOB_GENERATIONS["report-1"] = 4
        self.addCleanup(form_server.TRANSLATION_JOB_GENERATIONS.pop, "report-1", None)

        with (
            patch.object(form_server, "list_ai_job_status", return_value=[{
                "record_id": "report-1", "status": "IN_PROGRESS", "progress": "42",
            }]),
            patch.object(form_server, "update_record_translation_status") as update_status,
            patch.object(form_server, "_write_translation_metric"),
            patch.object(form_server, "ThreadPoolExecutor", return_value=new_executor),
        ):
            stopped = form_server._stop_active_translation_jobs()

        self.assertEqual(stopped, 1)
        self.assertIs(form_server.TRANSLATION_EXECUTOR, new_executor)
        self.assertEqual(form_server.TRANSLATION_JOB_GENERATIONS["report-1"], 5)
        old_executor.shutdown.assert_called_once_with(wait=False, cancel_futures=True)
        update_status.assert_called_once_with(
            form_server.DATABASE_PATH, "report-1", status="STOPPED", progress="42", error="",
        )

    def test_ai_job_status_snapshot_is_lightweight_and_reports_processing_count(self) -> None:
        records = [
            {"record_id": "report-1", "translation_status": "IN_PROGRESS", "translation_progress": "38", "translation_updated_at": "now"},
            {"record_id": "report-2", "translation_status": "COMPLETED", "translation_progress": "100", "translation_updated_at": "before"},
        ]
        lightweight_records = [
            {"record_id": row["record_id"], "status": row["translation_status"], "progress": row["translation_progress"], "updated_at": row["translation_updated_at"]}
            for row in records
        ]
        with patch.object(form_server, "list_ai_job_status", return_value=lightweight_records):
            snapshot = form_server._ai_job_status_snapshot("translation")

        self.assertEqual(snapshot["processing_count"], 1)
        self.assertEqual(snapshot["records"][0], {
            "record_id": "report-1", "status": "IN_PROGRESS", "progress": "38", "error": "", "updated_at": "now",
        })

    def test_ai_job_monitor_keeps_separate_translation_and_extraction_streams(self) -> None:
        original_path = form_server.AI_JOB_MONITOR_PATH
        form_server.AI_JOB_MONITOR_PATH = Path(self.repository_tmp.name) / "ai_job_monitor.jsonl"
        self.addCleanup(setattr, form_server, "AI_JOB_MONITOR_PATH", original_path)

        form_server._write_ai_job_monitor("translation", "request", record_id="report-1", source_preview="DRILL AHEAD")
        form_server._write_ai_job_monitor("translation", "response", record_id="report-1", response_preview="继续钻进")
        form_server._write_ai_job_monitor("extraction", "response", record_id="report-2", response_preview="SLB")

        translation = form_server._ai_job_monitor_snapshot("translation", 10)
        extraction = form_server._ai_job_monitor_snapshot("extraction", 10)
        self.assertEqual([row["event"] for row in translation["events"]], ["request", "response"])
        self.assertEqual(extraction["events"][0]["record_id"], "report-2")

    def test_translation_debug_log_retention_limits_age_count_and_rotated_file(self) -> None:
        debug_path = Path(self.repository_tmp.name) / "translation_debug_logs.jsonl"
        rotated_path = debug_path.with_suffix(debug_path.suffix + ".1")
        now = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)
        rows = [
            {"time": "2026-07-01T12:00:00Z", "event": "old", "index": 0},
            *[
                {"time": f"2026-07-{day:02d}T12:00:00Z", "event": "recent", "index": day}
                for day in range(9, 14)
            ],
        ]
        debug_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        rotated_path.write_text("old rotated data", encoding="utf-8")

        with (
            patch.object(form_server, "TRANSLATION_DEBUG_LOG_PATH", debug_path),
            patch.object(form_server, "TRANSLATION_DEBUG_RETENTION_DAYS", 7),
            patch.object(form_server, "TRANSLATION_DEBUG_MAX_ENTRIES", 3),
            patch.object(form_server, "TRANSLATION_DEBUG_MAX_BYTES", 1024 * 1024),
        ):
            result = form_server._prune_translation_debug_logs(now=now)

        retained = [json.loads(line) for line in debug_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([row["index"] for row in retained], [11, 12, 13])
        self.assertEqual(result["after"], 3)
        self.assertFalse(rotated_path.exists())

    def test_default_ai_extraction_rule_is_disabled_until_reviewed(self) -> None:
        config = form_server._default_ai_extraction_config()

        self.assertEqual(config["rules"][0]["id"], "npt-service-line")
        self.assertFalse(config["rules"][0]["enabled"])

    def test_ai_extraction_source_includes_row_context(self) -> None:
        source, count = form_server._ai_extraction_source_from_payload({
            "operations": [
                {"from": "08:00", "to": "09:30", "hours": "1.5", "op_type": "NPT", "operation_details": "WAIT ON SERVICE COMPANY"},
                {"from": "09:30", "to": "10:00", "hours": "0.5", "op_type": "P", "operation_details": "RESUME DRILLING"},
            ],
        }, {"source_section": "operations", "source_field": "operation_details"})

        self.assertEqual(count, 2)
        self.assertIn('"op_type": "NPT"', source)
        self.assertIn("WAIT ON SERVICE COMPANY", source)

    def test_ai_extraction_version_is_stable_and_changes_with_rules(self) -> None:
        raw = {
            "auto_execute": True,
            "rules": [{
                "id": "npt-owner", "name": "NPT责任方", "report_type": "drilling",
                "source_section": "operations", "source_field": "operation_details",
                "instruction": "提取责任公司", "target_field": "service_line",
                "output_format": "company", "enabled": True,
            }],
        }
        first = form_server._normalize_ai_extraction_config(raw)
        second = form_server._normalize_ai_extraction_config(raw)
        changed = form_server._normalize_ai_extraction_config({**raw, "auto_execute": False})

        self.assertEqual(first["version"], second["version"])
        self.assertNotEqual(first["version"], changed["version"])

    def test_ai_extraction_units_only_include_npt_rows_for_service_line(self) -> None:
        units = form_server._ai_extraction_units({"operations": [
            {"op_type": "P", "operation_details": "DRILLING"},
            {"op_type": "NPT", "from": "08:00", "to": "09:00", "operation_details": "WAIT ON SINOPEC"},
        ]}, {
            "source_section": "operations", "source_field": "operation_details",
            "target_field": "service_line", "condition": "仅处理 NPT",
        })

        self.assertEqual(len(units), 1)
        self.assertEqual(units[0]["source_row_no"], 2)
        self.assertIn("WAIT ON SINOPEC", units[0]["prompt_text"])

    def test_all_report_type_rule_accepts_common_operation_field(self) -> None:
        config = form_server._normalize_ai_extraction_config({
            "rules": [{
                "id": "all-npt-owner", "name": "全类型NPT责任方", "report_type": "all",
                "source_section": "operations", "source_field": "operation_details",
                "instruction": "提取责任公司", "target_field": "service_line",
                "output_format": "company", "enabled": True,
            }],
        })

        self.assertEqual(config["rules"][0]["report_type"], "all")
        self.assertEqual(config["catalog"]["report_types"][0]["value"], "all")
        enabled = [config["rules"][0]]
        self.assertTrue(form_server._payload_has_extraction_units(
            {"operations": [{"op_type": "NPT", "operation_details": "NPT A CARGO DE SLB"}]},
            "completion",
            enabled,
        ))

    def test_explicit_npt_responsibility_is_extracted_and_expanded_to_rig(self) -> None:
        source = "CONTINUA OPERACION; NPT A CARGO DE SINOPEC;"
        payload = {"report_fields": {"rig": "SINOPEC 248"}}

        company = form_server._explicit_responsible_party(source)

        self.assertEqual(company, "SINOPEC")
        self.assertEqual(form_server._normalize_responsible_party(company, payload), "SINOPEC 248")
        self.assertEqual(form_server._normalize_responsible_party("SINOPEC-SLB FRACTURA", payload), "SINOPEC-SLB FRACTURA")

    def test_explicit_npt_responsibility_stops_at_line_boundary(self) -> None:
        source = "NPT A CARGO DE SINOPEC\nIncident Comments:"

        self.assertEqual(form_server._explicit_responsible_party(source), "SINOPEC")

    def test_operation_extraction_status_is_row_specific(self) -> None:
        source = "NPT A CARGO DE SERVICE COMPANY"
        source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        current = {
            "source_hash": source_hash,
            "rule_version": "rules-v2",
            "extraction_status": "COMPLETED",
            "result_text": "SERVICE COMPANY",
            "updated_at": "2026-07-13T10:00:00",
        }

        self.assertEqual(
            form_server._current_operation_extraction(source, current, "rules-v2"),
            ("SERVICE COMPANY", "COMPLETED", "", "2026-07-13T10:00:00"),
        )
        self.assertEqual(form_server._current_operation_extraction(source, {}, "rules-v2"), ("", "PENDING", "", ""))
        self.assertEqual(form_server._current_operation_extraction(source, current, "rules-v3")[1], "STALE")
        self.assertEqual(form_server._current_operation_extraction(f"{source} CHANGED", current, "rules-v2")[1], "STALE")

    def test_npt_confirmation_rows_include_current_responsible_party(self) -> None:
        source = "NPT A CARGO DE SERVICE COMPANY"
        rows = [{
            "record_id": "report-1",
            "row_no": 2,
            "system_op_type": "NPT",
            "operation_details": source,
        }]
        result = {
            "record_id": "report-1",
            "source_section": "operations",
            "source_row_no": 2,
            "target_field": "service_line",
            "source_hash": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "rule_version": "rules-v2",
            "extraction_status": "COMPLETED",
            "result_text": "SERVICE COMPANY",
        }

        with (
            patch.object(form_server, "load_extraction_results", return_value=[result]),
            patch.object(form_server, "_load_ai_extraction_config", return_value={"version": "rules-v2"}),
        ):
            form_server._enrich_operation_extraction_rows(rows)

        self.assertEqual(rows[0]["service_line"], "SERVICE COMPANY")
        self.assertEqual(rows[0]["extraction_status"], "COMPLETED")

    def test_fault_evidence_maps_directional_tool_brand_to_service_line(self) -> None:
        source = "HALLIBURTON SPERRY REVISA FALLA / COMPORTAMIENTO ANÓMALO DE HERRAMIENTA ICRUISE MWD"

        self.assertEqual(form_server._evidence_responsible_party(source), "HALLIBURTON SPERRY")

    def test_directional_tool_mention_does_not_override_drill_pipe_failure(self) -> None:
        source = "SACA BHA CON ICRUISE Y M/LWD; OBSERVA WASHOUT EN JUNTA DE DRILL PIPE #171"

        self.assertEqual(form_server._evidence_responsible_party(source), "")

    def test_extraction_rule_filters_out_reports_with_only_p_operations(self) -> None:
        rule = {
            "report_type": "drilling", "source_section": "operations",
            "source_field": "operation_details", "target_field": "service_line",
            "condition": "仅处理 NPT", "enabled": True,
        }
        p_only = {"operations": [{"op_type": "P", "operation_details": "DRILLING"}]}
        with_npt = {"operations": [{"op_type": "NPT", "operation_details": "WAIT ON SERVICE"}]}

        self.assertFalse(form_server._payload_has_extraction_units(p_only, "drilling", [rule]))
        self.assertTrue(form_server._payload_has_extraction_units(with_npt, "drilling", [rule]))

    def test_project_team_normalization_preserves_rig_binding_metadata(self) -> None:
        normalized = form_server._normalize_project_team_config({
            "teams": [{"name": "00 SINOPEC 248"}],
            "projects": [{
                "contract_no": "EC-2026-001",
                "project_name": "Test Project",
                "rigs": [{
                    "rig": "00 SINOPEC 248",
                    "start_date": "2026-07-04",
                    "end_date": "2026-08-04",
                    "wells": ["PCNC-040"],
                    "note": "phase 1",
                }],
            }],
        })

        self.assertEqual(normalized["teams"][0]["name"], "SINOPEC 248")
        self.assertEqual(normalized["teams"][0]["aliases"], ["00 SINOPEC 248"])
        rig = normalized["projects"][0]["rigs"][0]
        self.assertEqual(rig["rig"], "SINOPEC 248")
        self.assertEqual(rig["start_date"], "2026-07-04")
        self.assertEqual(rig["end_date"], "2026-08-04")
        self.assertEqual(rig["note"], "phase 1")
        self.assertEqual(rig["wells"], ["PCNC-040"])

    def test_project_team_normalization_drops_placeholder_rigs(self) -> None:
        normalized = form_server._normalize_project_team_config({
            "teams": [
                {"name": "DRPPLACEHOLDER A 248"},
                {"name": "SINOPEC 248"},
            ],
            "projects": [{
                "contract_no": "EC-2026-001",
                "project_name": "Test Project",
                "rigs": [
                    {"rig": "DRPPLACEHOLDER A 248", "wells": ["BAD-001"]},
                    {"rig": "SINOPEC 248", "wells": ["PCNC-040"]},
                ],
            }],
            "pending_wells": [
                {"rig": "DRPPLACEHOLDER A 248", "wellbore": "BAD-001"},
                {"rig": "SINOPEC 248", "wellbore": "PCNC-040"},
            ],
        })

        self.assertEqual([team["name"] for team in normalized["teams"]], ["SINOPEC 248"])
        self.assertEqual([rig["rig"] for rig in normalized["projects"][0]["rigs"]], ["SINOPEC 248"])
        self.assertEqual([item["rig"] for item in normalized["pending_wells"]], ["SINOPEC 248"])

    def test_production_filter_rigs_excludes_placeholder_and_unbound_global_teams(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_project_team_path = form_server.PROJECT_TEAM_PATH
            original_list_records = form_server.list_records
            form_server.PROJECT_TEAM_PATH = Path(tmp) / "project_team_config.json"
            try:
                form_server._save_project_team_config({
                    "teams": [
                        {"name": "DRPPLACEHOLDER A 248"},
                        {"name": "SINOPEC 999"},
                    ],
                    "projects": [{
                        "id": "project-1",
                        "contract_no": "EC-2026-001",
                        "project_name": "Test Project",
                        "status": "active",
                        "rigs": [{"rig": "SINOPEC 933", "wells": []}],
                    }],
                })
                form_server.list_records = lambda database_path: [
                    {"rig": "DRPPLACEHOLDER A 248"},
                    {"rig": "SINOPEC 127"},
                ]

                rigs = form_server._production_filter_rigs([{"rig": "SINOPEC 248"}], Path(tmp) / "unused.xlsx")

                self.assertEqual(rigs, ["SINOPEC 127", "SINOPEC 248", "SINOPEC 933"])
            finally:
                form_server.PROJECT_TEAM_PATH = original_project_team_path
                form_server.list_records = original_list_records

    def test_project_assignment_matches_project_period_rig_and_well(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_project_team_path = form_server.PROJECT_TEAM_PATH
            form_server.PROJECT_TEAM_PATH = Path(tmp) / "project_team_config.json"
            try:
                form_server._save_project_team_config({
                    "teams": [{"name": "SINOPEC 248", "aliases": ["00 SINOPEC 248"]}],
                    "projects": [{
                        "id": "project-1",
                        "contract_no": "EC-2026-001",
                        "project_name": "Test Project",
                        "status": "active",
                        "start_date": "2026-07-01",
                        "end_date": "2026-07-31",
                        "rigs": [{"rig": "SINOPEC 248", "wells": ["PCNC-040"]}],
                    }],
                })

                matches = form_server._project_assignments_for_record({
                    "rig": "00 SINOPEC 248",
                    "wellbore": "PCNC-040",
                    "reportDate": "2026-07-15",
                }, {"project-1"})
                self.assertEqual(matches[0]["project_name"], "Test Project")
                self.assertEqual(form_server._project_assignments_for_record({
                    "rig": "00 SINOPEC 248",
                    "wellbore": "PCNC-041",
                    "reportDate": "2026-07-15",
                }, {"project-1"}), [])
                self.assertEqual(form_server._project_assignments_for_record({
                    "rig": "00 SINOPEC 248",
                    "wellbore": "PCNC-040",
                    "reportDate": "2026-08-01",
                }, {"project-1"}), [])
            finally:
                form_server.PROJECT_TEAM_PATH = original_project_team_path

    def test_discovered_well_does_not_mutate_project_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_project_team_path = form_server.PROJECT_TEAM_PATH
            form_server.PROJECT_TEAM_PATH = Path(tmp) / "project_team_config.json"
            try:
                form_server._save_project_team_config({
                    "teams": [{"name": "SINOPEC 248"}, {"name": "SINOPEC 168"}],
                    "projects": [
                        {
                            "id": "project-1",
                            "contract_no": "EC-2026-001",
                            "project_name": "Drilling Project",
                            "status": "active",
                            "start_date": "2026-01-01",
                            "end_date": "2026-12-31",
                            "rigs": [{"rig": "SINOPEC 248", "wells": ["EXISTING-001"]}],
                        },
                        {
                            "id": "project-2",
                            "contract_no": "EC-2026-002",
                            "project_name": "Move Project",
                            "status": "active",
                            "start_date": "2026-01-01",
                            "end_date": "2026-12-31",
                            "rigs": [{"rig": "SINOPEC 168", "wells": []}],
                        },
                    ],
                })

                before = form_server.PROJECT_TEAM_PATH.read_text(encoding="utf-8")
                with patch.object(form_server, "list_records", return_value=[{
                    "rig": "SINOPEC 248",
                    "wellbore": "PCNC-040",
                    "reportDate": "2026-06-11",
                    "report_type": "drilling",
                    "created_at": "2026-06-11T00:00:00",
                }]):
                    discovered = form_server._sync_project_wells_from_database(Path("mysql"))
                config = form_server._load_project_team_config()
                first_project = next(project for project in config["projects"] if project["id"] == "project-1")
                second_project = next(project for project in config["projects"] if project["id"] == "project-2")
                self.assertEqual(first_project["rigs"][0]["wells"], ["EXISTING-001"])
                self.assertEqual(second_project["rigs"][0]["wells"], [])
                self.assertEqual(config["pending_wells"], [])
                self.assertEqual(discovered["pending_wells"][0]["wellbore"], "PCNC-040")
                self.assertEqual(form_server.PROJECT_TEAM_PATH.read_text(encoding="utf-8"), before)
            finally:
                form_server.PROJECT_TEAM_PATH = original_project_team_path

    def test_project_mode_production_report_groups_well_stage_dates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_project_team_path = form_server.PROJECT_TEAM_PATH
            database_path = Path(tmp) / "report_database.xlsx"
            form_server.PROJECT_TEAM_PATH = Path(tmp) / "project_team_config.json"
            try:
                form_server._save_project_team_config({
                    "teams": [{"name": "SINOPEC 248"}],
                    "projects": [{
                        "id": "project-1",
                        "contract_no": "EC-2026-001",
                        "project_name": "Test Project",
                        "status": "active",
                        "start_date": "2026-06-01",
                        "end_date": "2026-06-30",
                        "rigs": [{"rig": "SINOPEC 248", "wells": ["PCNC-040"]}],
                    }],
                })

                def store(report_type: str, date: str, event: str, hours: str, report_no: str) -> None:
                    form_server.save_report_payload(database_path, {
                        "report_fields": {
                            "event": event,
                            "reportDate": date,
                            "reportNo": report_no,
                            "wellbore": "PCNC-040",
                            "rig": "SINOPEC 248",
                        },
                        "operations": [{"hours": hours, "op_type": "P", "operation_details": event}],
                    }, report_type)

                store("drilling", "2026-06-01", "Rig Move", "0", "1")
                store("move", "2026-06-01", "MOVE", "12", "2")
                store("drilling", "2026-06-02", "DRILLING", "24", "3")
                store("drilling", "2026-06-05", "drilling", "24", "4")
                store("completion", "2026-06-10", "Completion", "18", "5")
                store("completion", "2026-06-11", "Completion", "6", "7")
                store("workover", "2026-06-12", "WORKOVER", "6", "6")

                payload = form_server._production_summary_payload(database_path, {"project_mode": ["1"], "project": ["project-1"]})
                self.assertEqual(len(payload["details"]), 1)
                detail = payload["details"][0]
                self.assertEqual(detail["wellbore"], "PCNC-040")
                self.assertEqual(detail["contract_project"], "EC-2026-001 / Test Project")
                self.assertEqual(detail["move_date"], "2026-06-01")
                self.assertEqual(detail["drilling_start_date"], "2026-06-02")
                self.assertEqual(detail["drilling_finish_date"], "2026-06-05")
                self.assertEqual(detail["completion_date"], "2026-06-11")
                self.assertEqual(detail["workover_date"], "2026-06-12")
                self.assertEqual(detail["move_hours"], 12.0)
                self.assertEqual(detail["drilling_hours"], 48.0)
                self.assertEqual(detail["completion_hours"], 24.0)
                self.assertEqual(detail["workover_hours"], 6.0)
            finally:
                form_server.PROJECT_TEAM_PATH = original_project_team_path

    def test_project_report_keeps_unassigned_wells_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_project_team_path = form_server.PROJECT_TEAM_PATH
            database_path = Path(tmp) / "report_database.xlsx"
            form_server.PROJECT_TEAM_PATH = Path(tmp) / "project_team_config.json"
            try:
                form_server._save_project_team_config({
                    "teams": [{"name": "SINOPEC 183"}],
                    "projects": [{
                        "id": "project-1",
                        "contract_no": "EC-2026-001",
                        "project_name": "Test Project",
                        "status": "active",
                        "start_date": "2026-06-01",
                        "end_date": "2026-06-30",
                        "rigs": [{"rig": "SINOPEC 183", "wells": ["OLD-001"]}],
                    }],
                })

                for report_type, event, date, report_no in [
                    ("completion", "Completion", "2026-06-11", "1"),
                    ("workover", "Workover", "2026-06-12", "2"),
                ]:
                    form_server.save_report_payload(database_path, {
                        "report_fields": {
                            "event": event,
                            "reportDate": date,
                            "reportNo": report_no,
                            "wellbore": "GCLH-022",
                            "rig": "SINOPEC 183",
                        },
                        "operations": [{"hours": "12", "op_type": "P", "operation_details": event}],
                    }, report_type)

                payload = form_server._production_summary_payload(database_path, {"project_mode": ["1"], "project": ["project-1"]})
                discovered = form_server._sync_project_wells_from_database(database_path)
                config = form_server._load_project_team_config()
                project = config["projects"][0]

                self.assertEqual(project["rigs"][0]["wells"], ["OLD-001"])
                self.assertEqual(config["pending_wells"], [])
                self.assertEqual(payload["details"], [])
                self.assertEqual(discovered["pending_wells"][0]["wellbore"], "GCLH-022")
            finally:
                form_server.PROJECT_TEAM_PATH = original_project_team_path

    def test_production_report_remarks_are_user_saved_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_project_team_path = form_server.PROJECT_TEAM_PATH
            original_remarks_path = form_server.PRODUCTION_REPORT_REMARKS_PATH
            database_path = Path(tmp) / "report_database.xlsx"
            form_server.PROJECT_TEAM_PATH = Path(tmp) / "project_team_config.json"
            form_server.PRODUCTION_REPORT_REMARKS_PATH = Path(tmp) / "production_report_remarks.json"
            try:
                form_server._save_project_team_config({
                    "teams": [{"name": "SINOPEC 248"}],
                    "projects": [{
                        "id": "project-1",
                        "contract_no": "EC-2026-001",
                        "project_name": "Test Project",
                        "status": "active",
                        "start_date": "2026-06-01",
                        "end_date": "2026-06-30",
                        "rigs": [{"rig": "SINOPEC 248", "wells": ["PCNC-040"]}],
                    }],
                })
                form_server.save_report_payload(database_path, {
                    "report_fields": {
                        "event": "DRILLING",
                        "reportDate": "2026-06-11",
                        "reportNo": "1",
                        "wellbore": "PCNC-040",
                        "rig": "SINOPEC 248",
                    },
                    "operations": [{"hours": "24", "op_type": "P", "operation_details": "Drilling"}],
                }, "drilling")

                payload = form_server._production_summary_payload(database_path, {"project_mode": ["1"], "project": ["project-1"]})
                detail = payload["details"][0]
                self.assertEqual(detail["remarks"], "")

                form_server._save_production_report_remarks({detail["remark_key"]: "用户填写备注"})
                payload = form_server._production_summary_payload(database_path, {"project_mode": ["1"], "project": ["project-1"]})
                self.assertEqual(payload["details"][0]["remarks"], "用户填写备注")
            finally:
                form_server.PROJECT_TEAM_PATH = original_project_team_path
                form_server.PRODUCTION_REPORT_REMARKS_PATH = original_remarks_path

    def test_project_mode_production_report_filters_by_multiple_rigs_across_projects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_project_team_path = form_server.PROJECT_TEAM_PATH
            database_path = Path(tmp) / "report_database.xlsx"
            form_server.PROJECT_TEAM_PATH = Path(tmp) / "project_team_config.json"
            try:
                form_server._save_project_team_config({
                    "teams": [{"name": "SINOPEC 127"}, {"name": "SINOPEC 248"}, {"name": "SINOPEC 933"}],
                    "projects": [
                        {
                            "id": "project-1",
                            "contract_no": "EC-2026-001",
                            "project_name": "First Project",
                            "status": "active",
                            "start_date": "2026-06-01",
                            "end_date": "2026-06-30",
                            "rigs": [
                                {"rig": "SINOPEC 127", "wells": ["LOBC-010"]},
                                {"rig": "SINOPEC 248", "wells": ["PCNC-040"]},
                            ],
                        },
                        {
                            "id": "project-2",
                            "contract_no": "EC-2026-002",
                            "project_name": "Second Project",
                            "status": "active",
                            "start_date": "2026-06-01",
                            "end_date": "2026-06-30",
                            "rigs": [{"rig": "SINOPEC 933", "wells": ["ACAH-270H"]}],
                        },
                    ],
                })
                for rig, wellbore, report_type, date, event in [
                    ("SINOPEC 127", "LOBC-010", "completion", "2026-06-11", "Completion"),
                    ("SINOPEC 248", "PCNC-040", "drilling", "2026-06-11", "DRILLING"),
                    ("SINOPEC 933", "ACAH-270H", "workover", "2026-06-10", "WORKOVER"),
                ]:
                    form_server.save_report_payload(database_path, {
                        "report_fields": {
                            "event": event,
                            "reportDate": date,
                            "reportNo": f"{rig}-{wellbore}",
                            "wellbore": wellbore,
                            "rig": rig,
                        },
                        "operations": [{"hours": "24", "op_type": "P", "operation_details": event}],
                    }, report_type)

                payload = form_server._production_summary_payload(database_path, {
                    "project_mode": ["1"],
                    "rig": ["SINOPEC 127", "SINOPEC 933"],
                })
                wells = {item["wellbore"] for item in payload["details"]}
                projects = {item["contract_project"] for item in payload["details"]}

                self.assertEqual(wells, {"LOBC-010", "ACAH-270H"})
                self.assertEqual(projects, {"EC-2026-001 / First Project", "EC-2026-002 / Second Project"})
            finally:
                form_server.PROJECT_TEAM_PATH = original_project_team_path

    def test_project_mode_production_report_intersects_projects_rigs_and_well_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_project_team_path = form_server.PROJECT_TEAM_PATH
            database_path = Path(tmp) / "report_database.xlsx"
            form_server.PROJECT_TEAM_PATH = Path(tmp) / "project_team_config.json"
            try:
                form_server._save_project_team_config({
                    "teams": [{"name": "SINOPEC 127"}, {"name": "SINOPEC 248"}, {"name": "SINOPEC 933"}],
                    "projects": [
                        {
                            "id": "project-1",
                            "contract_no": "EC-2026-001",
                            "project_name": "First Project",
                            "status": "active",
                            "start_date": "2026-06-01",
                            "end_date": "2026-06-30",
                            "rigs": [
                                {"rig": "SINOPEC 127", "wells": ["LOBC-010"]},
                                {"rig": "SINOPEC 248", "wells": ["PCNC-040", "PCNC-039"]},
                            ],
                        },
                        {
                            "id": "project-2",
                            "contract_no": "EC-2026-002",
                            "project_name": "Second Project",
                            "status": "active",
                            "start_date": "2026-06-01",
                            "end_date": "2026-06-30",
                            "rigs": [{"rig": "SINOPEC 933", "wells": ["ACAH-270H"]}],
                        },
                    ],
                })
                for rig, wellbore, report_type, date, event in [
                    ("SINOPEC 127", "LOBC-010", "completion", "2026-06-11", "Completion"),
                    ("SINOPEC 248", "PCNC-040", "drilling", "2026-06-11", "DRILLING"),
                    ("SINOPEC 248", "PCNC-039", "drilling", "2026-06-12", "DRILLING"),
                    ("SINOPEC 933", "ACAH-270H", "workover", "2026-06-10", "WORKOVER"),
                ]:
                    form_server.save_report_payload(database_path, {
                        "report_fields": {
                            "event": event,
                            "reportDate": date,
                            "reportNo": f"{rig}-{wellbore}",
                            "wellbore": wellbore,
                            "rig": rig,
                        },
                        "operations": [{"hours": "24", "op_type": "P", "operation_details": event}],
                    }, report_type)

                payload = form_server._production_summary_payload(database_path, {
                    "project_mode": ["1"],
                    "project": ["project-1"],
                    "rig": ["SINOPEC 248", "SINOPEC 933"],
                    "wellbore": ["PCNC"],
                })

                self.assertEqual({item["wellbore"] for item in payload["details"]}, {"PCNC-039", "PCNC-040"})
                self.assertEqual({item["project_id"] for item in payload["details"]}, {"project-1"})
                self.assertEqual(payload["filters"]["rigs"], ["SINOPEC 127", "SINOPEC 248", "SINOPEC 933"])
            finally:
                form_server.PROJECT_TEAM_PATH = original_project_team_path

    def test_well_stats_returns_card_basic_fields_and_stage_dates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_database_path = form_server.DATABASE_PATH
            original_users_path = form_server.USERS_PATH
            form_server.DATABASE_PATH = Path(tmp) / "report_database.xlsx"
            form_server.USERS_PATH = Path(tmp) / "users.json"
            form_server.SESSIONS.clear()
            try:
                for report_type, date, event, report_no in [
                    ("drilling", "2026-06-01", "Rig Move", "1"),
                    ("drilling", "2026-06-02", "DRILLING", "2"),
                    ("completion", "2026-06-10", "Completion", "3"),
                    ("completion", "2026-06-11", "Final report", "4"),
                ]:
                    form_server.save_report_payload(form_server.DATABASE_PATH, {
                        "report_fields": {
                            "event": event,
                            "reportDate": date,
                            "reportNo": report_no,
                            "wellbore": "PCNC-040",
                            "rig": "00 SINOPEC 248",
                            "afeNumber": "AFE-001",
                        },
                        "operations": [{"hours": "24", "op_type": "P", "operation_details": event}],
                    }, report_type)

                server = form_server.ThreadingHTTPServer(("127.0.0.1", 0), form_server.FormHandler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    cookie = _login(server.server_port, "admin", "admin123")
                    response = _get_json(server.server_port, "/api/well-stats?wellbore=PCNC-040", cookie)
                    self.assertEqual(response["status"], 200, response["body"])
                    payload = json.loads(response["body"])
                    self.assertEqual(payload["rig"], "SINOPEC 248")
                    self.assertEqual(payload["afe_number"], "AFE-001")
                    self.assertEqual(payload["move_date"], "2026-06-01")
                    self.assertEqual(payload["drilling_start_date"], "2026-06-02")
                    self.assertEqual(payload["completion_date"], "2026-06-11")
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=2)
            finally:
                form_server.DATABASE_PATH = original_database_path
                form_server.USERS_PATH = original_users_path
                form_server.SESSIONS.clear()

    def test_project_well_sync_keeps_ambiguous_wells_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_project_team_path = form_server.PROJECT_TEAM_PATH
            database_path = Path(tmp) / "report_database.xlsx"
            form_server.PROJECT_TEAM_PATH = Path(tmp) / "project_team_config.json"
            try:
                form_server._save_project_team_config({
                    "teams": [{"name": "SINOPEC 127"}],
                    "projects": [
                        {
                            "id": "project-1",
                            "contract_no": "EC-2026-001",
                            "project_name": "First Project",
                            "status": "active",
                            "start_date": "2026-06-01",
                            "end_date": "2026-06-30",
                            "rigs": [],
                        },
                        {
                            "id": "project-2",
                            "contract_no": "EC-2026-002",
                            "project_name": "Second Project",
                            "status": "active",
                            "start_date": "2026-06-01",
                            "end_date": "2026-06-30",
                            "rigs": [],
                        },
                    ],
                })
                form_server.save_report_payload(database_path, {
                    "report_fields": {
                        "event": "Completion",
                        "reportDate": "2026-06-11",
                        "reportNo": "1",
                        "wellbore": "LOBC-010",
                        "rig": "SINOPEC 127",
                    },
                    "operations": [{"hours": "8", "op_type": "P", "operation_details": "Completion"}],
                }, "completion")

                config = form_server._sync_project_wells_from_database(database_path)

                self.assertEqual(config["pending_wells"], [{
                    "rig": "SINOPEC 127",
                    "wellbore": "LOBC-010",
                    "report_type": "completion",
                    "source": "report",
                    "created_at": config["pending_wells"][0]["created_at"],
                }])

                project_payload = form_server._production_summary_payload(database_path, {"project_mode": ["1"], "project": ["project-1"]})
                self.assertEqual(project_payload["details"], [])

                all_payload = form_server._production_summary_payload(database_path, {"project_mode": ["1"]})
                self.assertEqual(len(all_payload["details"]), 1)
                detail = all_payload["details"][0]
                self.assertEqual(detail["project_id"], form_server.UNASSIGNED_PROJECT_ID)
                self.assertEqual(detail["contract_project"], "未归属项目")
                self.assertEqual(detail["wellbore"], "LOBC-010")
                self.assertEqual(detail["completion_date"], "2026-06-11")
                self.assertEqual(detail["completion_hours"], 8.0)
            finally:
                form_server.PROJECT_TEAM_PATH = original_project_team_path

    def test_drilling_validation_matches_detail_required_fields(self) -> None:
        payload = {
            "report_fields": {
                "event": "DRILLING",
                "reportDate": "2026-05-31",
                "reportNo": "19",
                "wellbore": "PCNC-039",
                "rig": "SINOPEC 248",
                "todayMd": "1000",
                "progress": "0",
                "currentOps": "Drilling",
                "summary24h": "Operations",
                "forecast24h": "Continue",
            },
            "operations": [
                {"from": "00:00", "to": "08:00", "hours": "8", "op_code": "BHA", "op_type": "P", "operation_details": "Trip"},
            ],
        }
        warnings = form_server._validation_warnings(payload, "drilling")
        self.assertIn("mudType missing", warnings)
        self.assertIn("mudDensity missing", warnings)
        self.assertIn("operation hours total 8.00", warnings)

    def test_operation_duration_mismatch_is_flagged(self) -> None:
        payload = {
            "report_fields": {
                "event": "DRILLING",
                "reportDate": "2026-05-31",
                "reportNo": "19",
                "wellbore": "PCNC-039",
                "rig": "SINOPEC 248",
                "todayMd": "1000",
                "progress": "0",
                "currentOps": "Drilling",
                "summary24h": "Operations",
                "forecast24h": "Continue",
                "mudType": "WBM",
                "mudDensity": "10.2",
            },
            "operations": [
                {"from": "00:00", "to": "08:00", "hours": "7.5", "op_code": "DRILLING", "op_type": "P", "operation_details": "Drill ahead"},
                {"from": "08:00", "to": "24:00", "hours": "16.5", "op_code": "BHA", "op_type": "P", "operation_details": "Trip"},
            ],
        }
        warnings = form_server._validation_warnings(payload, "drilling")
        self.assertIn("operations row 1 time duration mismatch", warnings)

    def test_operation_same_clock_time_can_mean_next_day(self) -> None:
        payload = {
            "report_fields": {
                "event": "DRILLING",
                "reportDate": "2026-05-31",
                "reportNo": "19",
                "wellbore": "PCNC-039",
                "rig": "SINOPEC 248",
                "todayMd": "1000",
                "progress": "0",
                "currentOps": "Drilling",
                "summary24h": "Operations",
                "forecast24h": "Continue",
                "mudType": "WBM",
                "mudDensity": "10.2",
            },
            "operations": [
                {"from": "06:00", "to": "06:00", "hours": "24", "op_code": "DRILLING", "op_type": "P", "operation_details": "Drill ahead"},
            ],
        }
        warnings = form_server._validation_warnings(payload, "drilling")
        self.assertNotIn("operations row 1 time duration mismatch", warnings)

    def test_cost_inventory_are_not_validated_but_intervals_still_are(self) -> None:
        completion_payload = {
            "report_fields": {
                "event": "COMPLETION",
                "reportDate": "2026-05-31",
                "reportNo": "1",
                "wellbore": "PCNC-039",
                "rig": "SINOPEC 248",
                "currentOps": "Completion",
                "summary24h": "Operations",
                "forecast24h": "Continue",
            },
            "operations": [
                {"from": "00:00", "to": "24:00", "hours": "24", "op_code": "COMPLETION", "op_type": "P", "operation_details": "Run completion"},
            ],
            "bulks": [{"qty_start": "10", "qty_used": "3", "qty_end": "8"}],
            "perforation_intervals": [{"top_md": "1200", "base_md": "1100", "length": "10", "density": "-1"}],
        }
        warnings = form_server._validation_warnings(completion_payload, "completion")
        self.assertNotIn("bulks row 1 ending quantity inconsistent", warnings)
        self.assertIn("perforation_intervals row 1 base_md less than top_md", warnings)
        self.assertIn("perforation_intervals row 1 density negative", warnings)

    def test_login_page_supports_head_health_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_users_path = form_server.USERS_PATH
            form_server.USERS_PATH = Path(tmp) / "users.json"
            form_server.SESSIONS.clear()
            server = form_server.ThreadingHTTPServer(("127.0.0.1", 0), form_server.FormHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                response = _head(server.server_port, "/login/")
                self.assertEqual(response["status"], 200)
                self.assertEqual(response["body"], b"")
                self.assertGreater(int(response["content_length"]), 0)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
                form_server.USERS_PATH = original_users_path
                form_server.SESSIONS.clear()

    def test_import_drilling_pdf_endpoint_parses_and_stores_record(self) -> None:
        pdf = sample_pdf("PCNC-040")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")

        with tempfile.TemporaryDirectory() as tmp:
            original_database_path = form_server.DATABASE_PATH
            original_users_path = form_server.USERS_PATH
            original_config_path = form_server.CONFIG_PATH
            original_audit_log_path = form_server.AUDIT_LOG_PATH
            form_server.DATABASE_PATH = Path(tmp) / "report_database.xlsx"
            form_server.USERS_PATH = Path(tmp) / "users.json"
            form_server.CONFIG_PATH = Path(tmp) / "system_config.json"
            form_server.AUDIT_LOG_PATH = Path(tmp) / "audit_logs.jsonl"
            form_server.SESSIONS.clear()
            server = form_server.ThreadingHTTPServer(("127.0.0.1", 0), form_server.FormHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                cookie = _login(server.server_port, "admin", "admin123")
                response = _post_pdf(server.server_port, "/api/import-pdf", pdf, cookie)
                self.assertEqual(response["status"], 200, response["body"])
                payload = json.loads(response["body"])
                self.assertEqual(payload["report_fields"]["wellbore"], "PCNC-040")
                self.assertEqual(payload["report_fields"]["reportNo"], "11")
                self.assertEqual(payload["metadata"]["record_id"], "drilling:PCNC-040:2026-06-11:11")

                stored = load_report_payload(form_server.DATABASE_PATH, payload["metadata"]["record_id"])
                self.assertEqual(stored["report_fields"]["rig"], "SINOPEC 248")
                self.assertEqual(len(stored["operations"]), 6)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
                form_server.DATABASE_PATH = original_database_path
                form_server.USERS_PATH = original_users_path
                form_server.CONFIG_PATH = original_config_path
                form_server.AUDIT_LOG_PATH = original_audit_log_path
                form_server.SESSIONS.clear()

    def test_translate_report_endpoint_returns_structured_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_users_path = form_server.USERS_PATH
            original_terms_path = form_server.TRANSLATION_TERMS_PATH
            original_engine = os.environ.get("DRP_TRANSLATION_ENGINE")
            form_server.USERS_PATH = Path(tmp) / "users.json"
            form_server.TRANSLATION_TERMS_PATH = Path(tmp) / "translation_terms.json"
            os.environ["DRP_TRANSLATION_ENGINE"] = "noop"
            form_server.SESSIONS.clear()
            server = form_server.ThreadingHTTPServer(("127.0.0.1", 0), form_server.FormHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                cookie = _login(server.server_port, "admin", "admin123")
                with patch.object(
                    form_server,
                    "_active_translation_config",
                    return_value=form_server.TranslationConfig(engine="noop"),
                ):
                    response = _post_json(
                        server.server_port,
                        "/api/translate-report",
                        {
                            "target_language": "zh",
                            "payload": {
                                "metadata": {"source_file": "mixed.pdf"},
                                "report_fields": {
                                    "wellbore": "EB-D-12",
                                    "currentOps": "ROP 18 m/hr while drilling 12.25 in section.",
                                },
                                "operations": [],
                            },
                        },
                        cookie,
                    )
                self.assertEqual(response["status"], 200, response["body"])
                payload = json.loads(response["body"])
                self.assertEqual(payload["metadata"]["engine"], "noop")
                self.assertEqual(payload["metadata"]["target_language"], "zh-CN")
                self.assertIn("translation_content", payload)
                self.assertEqual(
                    payload["translated_payload"]["report_fields"]["currentOps"],
                    "ROP 18 m/hr while drilling 12.25 in section.",
                )
                self.assertIsInstance(payload["translation_content"], list)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
                form_server.USERS_PATH = original_users_path
                form_server.TRANSLATION_TERMS_PATH = original_terms_path
                if original_engine is None:
                    os.environ.pop("DRP_TRANSLATION_ENGINE", None)
                else:
                    os.environ["DRP_TRANSLATION_ENGINE"] = original_engine
                form_server.SESSIONS.clear()

    def test_admin_translation_terms_can_be_read_and_saved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_users_path = form_server.USERS_PATH
            original_terms_path = form_server.TRANSLATION_TERMS_PATH
            form_server.USERS_PATH = Path(tmp) / "users.json"
            form_server.TRANSLATION_TERMS_PATH = Path(tmp) / "translation_terms.json"
            form_server.SESSIONS.clear()
            server = form_server.ThreadingHTTPServer(("127.0.0.1", 0), form_server.FormHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                cookie = _login(server.server_port, "admin", "admin123")
                get_response = _get_json(server.server_port, "/api/admin/translation-terms", cookie)
                self.assertEqual(get_response["status"], 200, get_response["body"])
                config = json.loads(get_response["body"])
                self.assertTrue(any(term["zh"] == "机械钻速" for term in config["terms"]))

                config["terms"].append({
                    "id": "term-test-flowline",
                    "category": "equipment",
                    "zh": "流管线",
                    "en": "flowline",
                    "es": "línea de flujo",
                    "aliases": {"zh": [], "en": ["flow line"], "es": ["linea de flujo"]},
                    "protected": True,
                    "enabled": True,
                })
                post_response = _post_json(server.server_port, "/api/admin/translation-terms", config, cookie)
                self.assertEqual(post_response["status"], 200, post_response["body"])
                saved = json.loads(post_response["body"])
                self.assertTrue(any(term["en"] == "flowline" for term in saved["terms"]))
                self.assertTrue(form_server.TRANSLATION_TERMS_PATH.exists())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
                form_server.USERS_PATH = original_users_path
                form_server.TRANSLATION_TERMS_PATH = original_terms_path
                form_server.SESSIONS.clear()


def _login(port: int, username: str, password: str) -> str:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
    body = json.dumps({"username": username, "password": password}).encode("utf-8")
    try:
        connection.request(
            "POST",
            "/api/admin/login",
            body=body,
            headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        response = connection.getresponse()
        payload = response.read().decode("utf-8")
        if response.status != 200:
            raise AssertionError(payload)
        cookie = response.getheader("Set-Cookie", "").split(";", 1)[0]
        login_payload = json.loads(payload)
        if login_payload.get("user", {}).get("must_change_password"):
            changed = _post_json(
                port,
                "/api/admin/change-password",
                {"old_password": password, "new_password": f"{password}-changed"},
                cookie,
            )
            if changed["status"] != 200:
                raise AssertionError(changed["body"])
        return cookie
    finally:
        connection.close()


def _head(port: int, path: str) -> dict[str, Any]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
    try:
        connection.request("HEAD", path)
        response = connection.getresponse()
        return {
            "status": response.status,
            "content_length": response.getheader("Content-Length", "0"),
            "body": response.read(),
        }
    finally:
        connection.close()


def _get_json(port: int, path: str, cookie: str = "") -> dict[str, Any]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
    try:
        headers = {}
        if cookie:
            headers["Cookie"] = cookie
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        return {"status": response.status, "body": response.read().decode("utf-8")}
    finally:
        connection.close()


def _post_json(port: int, path: str, payload: dict[str, Any], cookie: str = "") -> dict[str, Any]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
    body = json.dumps(payload).encode("utf-8")
    try:
        headers = {"Content-Type": "application/json", "Content-Length": str(len(body))}
        if cookie:
            headers["Cookie"] = cookie
        connection.request("POST", path, body=body, headers=headers)
        response = connection.getresponse()
        return {"status": response.status, "body": response.read().decode("utf-8")}
    finally:
        connection.close()


def _post_pdf(port: int, path: str, pdf: Path, cookie: str = "") -> dict[str, Any]:
    boundary = "----drilling-report-test-boundary"
    data = pdf.read_bytes()
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="report"; filename="{pdf.name}"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8")
    tail = f"\r\n--{boundary}--\r\n".encode("utf-8")
    body = head + data + tail
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
    try:
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body))}
        if cookie:
            headers["Cookie"] = cookie
        connection.request(
            "POST",
            path,
            body=body,
            headers=headers,
        )
        response = connection.getresponse()
        return {"status": response.status, "body": response.read().decode("utf-8")}
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()
