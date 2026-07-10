from __future__ import annotations

import http.client
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from drilling_report_parser import form_server
from drilling_report_parser.excel_database import load_report_payload
from tests.test_pdf_report_parser import sample_pdf


class FormServerImportTest(unittest.TestCase):
    def test_resume_translation_jobs_requeues_interrupted_failed_and_old_records(self) -> None:
        records = [
            {"record_id": "blank", "translation_status": "", "translation_version": ""},
            {"record_id": "failed", "translation_status": "FAILED", "translation_version": form_server.PROMPT_VERSION},
            {"record_id": "old", "translation_status": "COMPLETED", "translation_version": "old-version"},
            {"record_id": "done", "translation_status": "COMPLETED", "translation_version": form_server.PROMPT_VERSION},
        ]

        with (
            patch.object(form_server, "_translation_jobs_enabled", return_value=True),
            patch.object(form_server, "list_records", return_value=records),
            patch.object(form_server, "update_record_translation_status") as update_status,
            patch.object(form_server, "_schedule_translation_job") as schedule_job,
        ):
            form_server._resume_translation_jobs()

        self.assertEqual({call.args[0] for call in schedule_job.call_args_list}, {"blank", "failed", "old"})
        self.assertEqual(update_status.call_count, 3)
        for call in update_status.call_args_list:
            self.assertEqual(call.kwargs, {"status": "QUEUED", "progress": 0, "error": ""})

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

    def test_auto_register_well_uses_rig_project_binding_with_multiple_projects(self) -> None:
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
                            "rigs": [{"rig": "SINOPEC 248", "wells": []}],
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

                form_server._auto_register_project_well({
                    "report_fields": {
                        "rig": "SINOPEC 248",
                        "wellbore": "PCNC-040",
                        "reportDate": "2026-06-11",
                    },
                }, "drilling")
                config = form_server._load_project_team_config()
                first_project = next(project for project in config["projects"] if project["id"] == "project-1")
                second_project = next(project for project in config["projects"] if project["id"] == "project-2")
                self.assertEqual(first_project["rigs"][0]["wells"], ["PCNC-040"])
                self.assertEqual(second_project["rigs"][0]["wells"], [])
                self.assertEqual(config["pending_wells"], [])
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

    def test_project_report_query_backfills_completion_and_workover_wells(self) -> None:
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
                config = form_server._load_project_team_config()
                project = config["projects"][0]

                self.assertEqual(project["rigs"][0]["wells"], ["GCLH-022", "OLD-001"])
                self.assertEqual(config["pending_wells"], [])
                self.assertEqual(len(payload["details"]), 1)
                self.assertEqual(payload["details"][0]["wellbore"], "GCLH-022")
                self.assertEqual(payload["details"][0]["completion_date"], "2026-06-11")
                self.assertEqual(payload["details"][0]["workover_date"], "2026-06-12")
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
                        }
                    },
                    cookie,
                )
                self.assertEqual(response["status"], 200, response["body"])
                payload = json.loads(response["body"])
                self.assertEqual(payload["metadata"]["engine"], "noop")
                self.assertEqual(payload["metadata"]["target_language"], "zh-CN")
                self.assertIn("translation_content", payload)
                self.assertIn("机械钻速", payload["translated_payload"]["report_fields"]["currentOps"])
                self.assertTrue(any(row["field_code"] == "report_fields.currentOps" for row in payload["translation_content"]))
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
        return response.getheader("Set-Cookie", "").split(";", 1)[0]
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
