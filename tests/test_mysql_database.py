from __future__ import annotations

import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from drilling_report_parser.mysql_database import (
    DPR_TABLE_ALIASES,
    INIT_SQL_PATH,
    _ensure_master_data_v3_columns,
    _ensure_hsse_source_columns,
    _drilling_basic_monthly_scope_row,
    _drilling_workover_efficiency_monthly_row,
    _ai_extraction_task_manifest_runtime,
    _monthly_team_workload_row,
    _workover_basic_monthly_job_row,
    _ensure_report_record_columns,
    load_analytics_view_rows,
    list_aggregate_scope_report_records,
    _migrate_dpr_table_names,
    _npt_row_revision,
    _operation_hour_summary,
    _record_from_payload,
    _resolve_classification_pending_issue,
    _translation_source_hash,
    _upsert_record,
)
from drilling_report_parser.text_structure import normalize_multiline
from drilling_report_parser.translation import source_hash


class FakeCursor:
    def __init__(self, columns: list[str]) -> None:
        self.columns = columns
        self.statements: list[str] = []

    def execute(self, statement: str, _args: object = None) -> None:
        self.statements.append(statement)

    def fetchall(self) -> list[dict[str, str]]:
        return [{"Field": column} for column in self.columns]


class MySQLDatabaseMigrationTest(unittest.TestCase):
    def test_hsse_source_migration_adds_provenance_columns(self) -> None:
        cursor = FakeCursor(["id", "record_date"])

        _ensure_hsse_source_columns(cursor)

        statements = "\n".join(cursor.statements)
        self.assertIn("ADD COLUMN data_source_type", statements)
        self.assertIn("ADD COLUMN source_reference", statements)
        self.assertIn("ADD COLUMN source_context_json", statements)

    def test_aggregate_scope_query_uses_only_dimensions_owned_by_grain(self) -> None:
        def captured_query(scope: dict[str, object]) -> tuple[str, list[object]]:
            connection = MagicMock()
            connection.__enter__.return_value = connection
            cursor = MagicMock()
            cursor.__enter__.return_value = cursor
            cursor.fetchall.return_value = []
            connection.cursor.return_value = cursor
            with patch("drilling_report_parser.mysql_database.initialize_database"), patch(
                "drilling_report_parser.mysql_database._connect", return_value=connection,
            ):
                list_aggregate_scope_report_records(
                    None, scope=scope, report_types=["drilling", "completion", "workover"],
                )
            call = cursor.execute.call_args
            return call.args[0], list(call.args[1])

        team_sql, team_args = captured_query({
            "grain": "team_month", "project_id": 3, "well_id": 7, "team_id": 9,
            "job_sequence_no": 2, "profession": "drilling",
            "period_start": "2026-07-01", "period_end": "2026-07-31",
        })
        self.assertIn("rig.team_id=%s", team_sql)
        self.assertIn("report.report_date BETWEEN %s AND %s", team_sql)
        self.assertNotIn("report.project_id=%s", team_sql)
        self.assertNotIn("report.well_id=%s", team_sql)
        self.assertNotIn("job.sequence_no=%s", team_sql)
        self.assertEqual(team_args, ["drilling", "completion", 9, "2026-07-01", "2026-07-31"])

        job_sql, job_args = captured_query({
            "grain": "well_job", "project_id": 3, "well_id": 7, "team_id": 9,
            "job_sequence_no": 2, "profession": "drilling",
            "period_start": "2026-07-01", "period_end": "2026-07-31",
        })
        self.assertIn("report.project_id=%s", job_sql)
        self.assertIn("report.well_id=%s", job_sql)
        self.assertIn("job.sequence_no=%s", job_sql)
        self.assertNotIn("rig.team_id=%s", job_sql)
        self.assertNotIn("report.report_date BETWEEN %s AND %s", job_sql)
        self.assertEqual(job_args, ["drilling", "completion", 3, 7, 2])

    def test_manifest_reconcile_cannot_overwrite_worker_terminal_status(self) -> None:
        incoming = {
            "source_hash": "same", "rule_version": "rules-v1", "status": "IN_PROGRESS",
            "progress": 1, "attempt_count": 2, "error_message": "", "started_at": "start-old",
            "completed_at": "", "updated_at": "read-before-worker-finished",
        }
        current = {
            "source_hash": "same", "rule_version": "rules-v1", "status": "COMPLETED",
            "progress": 100, "attempt_count": 3, "error_message": "", "started_at": "start",
            "completed_at": "finished", "updated_at": "worker-finished",
        }

        runtime = _ai_extraction_task_manifest_runtime(incoming, current)

        self.assertEqual(runtime["status"], "COMPLETED")
        self.assertEqual(runtime["progress"], 100)
        self.assertEqual(runtime["completed_at"], "finished")
        self.assertEqual(runtime["updated_at"], "worker-finished")

    def test_nullable_pdf_segment_metadata_round_trips_as_null(self) -> None:
        record = _record_from_payload(
            "drilling:WELL-1:2026-01-01:1",
            "drilling",
            "one-report.pdf",
            {"reportDate": "2026-01-01", "reportNo": "1", "wellbore": "WELL-1"},
            {"source_page_start": "", "source_page_end": None},
            "2026-01-01T00:00:00",
            "2026-01-01T00:00:00",
        )

        self.assertIsNone(record["source_page_start"])
        self.assertIsNone(record["source_page_end"])

    def test_analytics_query_reads_canonical_view_without_report_row_json(self) -> None:
        connection = MagicMock()
        connection.__enter__.return_value = connection
        cursor = MagicMock()
        cursor.__enter__.return_value = cursor
        cursor.fetchall.side_effect = [[], [{"match_status": "UNASSIGNED", "count_value": 2}]]
        connection.cursor.return_value = cursor

        with patch("drilling_report_parser.mysql_database.initialize_database"), patch(
            "drilling_report_parser.mysql_database._connect", return_value=connection
        ):
            payload = load_analytics_view_rows(None, date_from="2026-06-01", project_ids=("5",))

        statements = [call.args[0] for call in cursor.execute.call_args_list]
        self.assertIn("FROM vw_rig_production_timeline timeline", statements[0])
        self.assertNotIn("dpr_report_row", " ".join(statements))
        self.assertEqual(payload["quality"]["unassigned_count"], 2)

    def test_legacy_daily_report_tables_are_renamed_in_one_statement(self) -> None:
        class RenameCursor:
            def __init__(self) -> None:
                self.statements: list[str] = []

            def execute(self, statement: str, _args: object = None) -> None:
                self.statements.append(statement)

            def fetchall(self) -> list[dict[str, str]]:
                return [{"TABLE_NAME": "report_records"}, {"TABLE_NAME": "fact_activity"}]

        cursor = RenameCursor()
        _migrate_dpr_table_names(cursor)

        rename_statement = cursor.statements[-1]
        self.assertTrue(rename_statement.startswith("RENAME TABLE "))
        self.assertIn("`report_records` TO `dpr_report_record`", rename_statement)
        self.assertIn("`fact_activity` TO `dpr_operation`", rename_statement)

    def test_schema_has_no_common_catch_all_tables(self) -> None:
        schema = Path(INIT_SQL_PATH).read_text(encoding="utf-8")

        self.assertNotIn("CREATE TABLE IF NOT EXISTS dpr_common_", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS dpr_drilling_bulk_inventory", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS dpr_completion_perforation_interval", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS dpr_workover_perforation_interval", schema)
        self.assertIn("dpr_report", DPR_TABLE_ALIASES)

    def test_schema_contains_translation_memory_and_revision_tables(self) -> None:
        schema = Path(INIT_SQL_PATH).read_text(encoding="utf-8")

        self.assertIn("CREATE TABLE IF NOT EXISTS translation_memory", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS translation_revision", schema)

    def test_schema_uses_views_for_analytics_and_structured_business_remarks(self) -> None:
        schema = Path(INIT_SQL_PATH).read_text(encoding="utf-8")

        self.assertIn("CREATE OR REPLACE VIEW vw_report_analytics", schema)
        self.assertIn("CREATE OR REPLACE VIEW vw_rig_production_timeline", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS production_report_remark", schema)
        self.assertNotIn("CREATE TABLE IF NOT EXISTS monthly_report_snapshot", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS ai_extraction_target_field", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS ai_extraction_aggregate_result", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS ai_extraction_result_source", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS ai_extraction_task", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS ai_extraction_task_source", schema)
        self.assertIn("grain VARCHAR(32) NOT NULL DEFAULT 'report'", schema)
        self.assertIn("allowed_grains JSON", schema)
        self.assertIn("well_id BIGINT UNSIGNED NULL", schema)
        self.assertNotIn("CREATE TABLE IF NOT EXISTS rel_project_rig_assignment", schema)
        self.assertIn("hours_source VARCHAR(16)", schema)
        self.assertIn("activity.hours_source", schema)
        self.assertIn("CREATE OR REPLACE VIEW vw_drilling_basic_monthly_source", schema)
        self.assertIn("CREATE OR REPLACE VIEW vw_workover_basic_monthly_source", schema)
        self.assertIn("CREATE OR REPLACE VIEW vw_drilling_workover_efficiency_monthly", schema)
        self.assertIn("CREATE OR REPLACE VIEW vw_monthly_team_workload", schema)

    def test_drilling_workover_efficiency_splits_npt_by_project_allowance(self) -> None:
        result = _drilling_workover_efficiency_monthly_row({
            "project_id": 14,
            "project_name": "Workover Project",
            "project_type": "workover",
            "well_id": 25,
            "well_name": "W-25",
            "profession": "workover",
            "team_name": "SINOPEC 933修井队",
            "country_region": "厄瓜多尔",
            "team_company": "华东工程",
            "block_name": "SHUSHUFINDI",
            "rig_model": "ZJ30",
            "move_hours": 12.26,
            "production_hours": 80,
            "npt_hours": 15,
            "npt_allowance_hours": 12,
            "report_count": 4,
            "operation_count": 20,
        })

        self.assertEqual(result["profession_label"], "修井")
        self.assertEqual(result["team_code"], "SINOPEC 933修井队")
        self.assertEqual(result["move_hours"], 12.3)
        self.assertEqual(result["production_hours"], 80.0)
        self.assertEqual(result["paid_repair_hours"], 12.0)
        self.assertEqual(result["zero_rate_repair_hours"], 3.0)
        self.assertEqual(result["accident_complex_hours"], 0.0)
        self.assertEqual(result["other_hours"], 0.0)
        self.assertEqual(result["well_efficiency"], round(80 / 95, 6))
        self.assertEqual(result["nonproductive_description"], "")
        self.assertEqual(result["remarks"], "")

    def test_monthly_team_workload_total_uses_all_six_hour_buckets(self) -> None:
        result = _monthly_team_workload_row({
            "project_id": 14,
            "project_name": "Project",
            "profession": "drilling",
            "team_name": "SINOPEC 127",
            "operation_hours": 100.125,
            "move_hours": 24,
            "manned_standby_hours": 0,
            "unmanned_standby_hours": 0,
            "force_majeure_hours": 0,
            "zero_rate_repair_hours": 5.375,
        })

        self.assertEqual(result["category_label"], "钻机")
        self.assertEqual(result["team_name"], "SINOPEC 127")
        self.assertEqual(result["operation_hours"], 100.125)
        self.assertEqual(result["zero_rate_repair_hours"], 5.375)
        self.assertEqual(result["total_hours"], 129.5)

    def test_drilling_basic_monthly_row_uses_report_numbers_and_accumulated_hours(self) -> None:
        common = {
            "job_id": 11, "project_id": 2, "project_name": "P", "well_id": 3,
            "well_name": "W-1", "job_sequence_no": 1, "team_code": "248", "team_name": "SINOPEC 248钻井队",
            "daily_report_id": 1, "team_id": 9, "country_region": "厄瓜多尔",
            "team_company": "西南工程", "block_name": "PUCUNA", "rig_model": "ZJ70D",
            "well_profile_code": "定向井", "planned_start": datetime(2026, 1, 1),
            "planned_end": datetime(2026, 1, 16), "design_depth_ft": 10000,
        }
        rows = [
            {**common, "report_date": date(2026, 6, 30), "report_no": 1, "report_hours": 12, "daily_progress_ft": 100, "measured_depth_ft": 100},
            {**common, "daily_report_id": 2, "report_date": date(2026, 7, 1), "report_no": 2, "report_hours": 24, "daily_progress_ft": 200, "measured_depth_ft": 300},
            {**common, "daily_report_id": 3, "report_date": date(2026, 7, 2), "report_no": 3, "report_hours": 6, "daily_progress_ft": 50, "measured_depth_ft": 350},
        ]
        completion = [
            {**common, "job_id": 12, "report_date": date(2026, 7, 3), "report_no": 1, "report_hours": 12},
            {**common, "job_id": 12, "report_date": date(2026, 7, 4), "report_no": 2, "report_hours": 12},
        ]

        result = _drilling_basic_monthly_scope_row(
            rows, completion, month_start=date(2026, 7, 1), month_end=date(2026, 7, 31), year_start=date(2026, 1, 1)
        )

        self.assertEqual(result["team_code"], "SINOPEC 248钻井队")
        self.assertEqual(result["drilling_start_date"], "2026-06-30")
        self.assertEqual(result["drilling_end_date"], "2026-07-02")
        self.assertEqual(result["month_progress_ft"], 250.0)
        self.assertEqual(result["year_progress_ft"], 350.0)
        self.assertEqual(result["actual_drilling_cycle_days"], 1.75)
        self.assertEqual(result["actual_completion_cycle_days"], 1.0)
        self.assertEqual(result["well_control_incident"], "")
        self.assertEqual(result["accident_waiting"], "")
        self.assertEqual(result["remarks"], "")

    def test_drilling_basic_monthly_row_supports_completion_only_monthly_scope(self) -> None:
        completion = [{
            "job_id": 12, "project_id": 2, "project_name": "P", "well_id": 3,
            "well_name": "W-1", "job_sequence_no": 1, "team_code": "248",
            "team_name": "SINOPEC 248钻井队", "daily_report_id": 4, "team_id": 9,
            "report_date": date(2026, 7, 4), "report_no": 1, "report_hours": 12,
            "planned_start": datetime(2026, 7, 4), "planned_end": datetime(2026, 7, 6),
        }]

        result = _drilling_basic_monthly_scope_row(
            [], completion, month_start=date(2026, 7, 1), month_end=date(2026, 7, 31), year_start=date(2026, 1, 1)
        )

        self.assertEqual(result["drilling_start_date"], "")
        self.assertIsNone(result["actual_drilling_cycle_days"])
        self.assertEqual(result["completion_date"], "2026-07-04")
        self.assertEqual(result["actual_completion_cycle_days"], 0.5)
        self.assertEqual(result["planned_completion_cycle_days"], 2.0)

    def test_workover_basic_monthly_row_uses_report_numbers_and_translated_primary_reason(self) -> None:
        common = {
            "job_id": 21, "project_id": 2, "project_name": "P", "well_id": 3,
            "well_name": "W-1", "job_sequence_no": 1, "team_code": "932",
            "team_name": "SINOPEC 932修井队", "team_id": 9, "country_region": "厄瓜多尔",
            "team_company": "华东工程", "block_name": "AUCA", "rig_model": "XJ650",
            "well_profile_name": "油井",
        }
        rows = [
            {**common, "daily_report_id": 1, "report_date": date(2026, 6, 30), "report_no": 1, "primary_reason_source": "PULLING RUN BES", "primary_reason_translated": ""},
            {**common, "daily_report_id": 2, "report_date": date(2026, 7, 1), "report_no": 2, "primary_reason_source": "PULLING RUN BES", "primary_reason_translated": "检泵"},
            {**common, "daily_report_id": 3, "report_date": date(2026, 7, 2), "report_no": 3, "primary_reason_source": "PULLING RUN BES", "primary_reason_translated": ""},
        ]

        result = _workover_basic_monthly_job_row(rows)

        self.assertEqual(result["team_code"], "SINOPEC 932修井队")
        self.assertEqual(result["workover_start_date"], "2026-06-30")
        self.assertEqual(result["workover_end_date"], "2026-07-02")
        self.assertEqual(result["primary_operation"], "检泵")
        self.assertEqual(result["primary_operation_source"], "PULLING RUN BES")
        self.assertEqual(result["primary_operation_zh"], "检泵")
        self.assertEqual(result["well_control_incident"], "")
        self.assertEqual(result["accident_waiting"], "")
        self.assertEqual(result["remarks"], "")

    def test_project_schema_contains_type_and_npt_allowance(self) -> None:
        schema = Path(INIT_SQL_PATH).read_text(encoding="utf-8")
        cursor = FakeCursor([])

        _ensure_master_data_v3_columns(cursor)

        statements = "\n".join(cursor.statements)
        self.assertIn("project_type VARCHAR(32) NOT NULL DEFAULT 'drilling'", schema)
        self.assertIn("npt_allowance_hours DECIMAL(8,2) NOT NULL DEFAULT 5.00", schema)
        self.assertIn("ALTER TABLE md_project ADD COLUMN project_type", statements)
        self.assertIn("ALTER TABLE md_project ADD COLUMN npt_allowance_hours", statements)

    def test_well_profile_has_no_inferred_default_and_legacy_default_is_cleared(self) -> None:
        schema = Path(INIT_SQL_PATH).read_text(encoding="utf-8")
        cursor = FakeCursor([])

        _ensure_master_data_v3_columns(cursor)

        statements = "\n".join(cursor.statements)
        self.assertIn("well_profile_code VARCHAR(64) NOT NULL DEFAULT ''", schema)
        self.assertNotIn("well_profile_code VARCHAR(64) NOT NULL DEFAULT 'VERTICAL'", schema)
        self.assertIn("MODIFY COLUMN well_profile_code VARCHAR(64) NOT NULL DEFAULT ''", statements)
        self.assertIn("井型无明确来源，清除历史默认直井", statements)
        self.assertNotIn("well_name LIKE '%水平%'", Path(__file__).parents[1].joinpath(
            "drilling_report_parser", "mysql_database.py"
        ).read_text(encoding="utf-8"))

    def test_schema_prevents_duplicate_report_business_identities(self) -> None:
        schema = Path(INIT_SQL_PATH).read_text(encoding="utf-8")

        self.assertIn(
            "UNIQUE KEY uq_report_records_business_identity (report_type, report_date, report_no, wellbore)",
            schema,
        )

    def test_manual_memory_hash_matches_translation_pipeline_hash(self) -> None:
        text = "DRILL AHEAD.\r\nCIRCULATE CLEAN."

        self.assertEqual(_translation_source_hash(text), source_hash(normalize_multiline(text)))

    def test_operation_hour_summary_uses_confirmed_type(self) -> None:
        summary = _operation_hour_summary([
            {"record_id": "r-1", "row_json": '{"hours":"18","op_type":"P"}'},
            {"record_id": "r-1", "row_json": '{"hours":"2.5","op_type":"SC"}'},
            {"record_id": "r-1", "row_json": '{"hours":"3.5","op_type":"P","confirmed_op_type":"NPT"}'},
        ])

        self.assertEqual(summary["r-1"], {"p_hours": 18.0, "sc_hours": 2.5, "npt_hours": 3.5})

    def test_operation_hour_summary_ignores_draft_type(self) -> None:
        summary = _operation_hour_summary([
            {"record_id": "r-1", "row_json": '{"hours":"3.5","op_type":"SC","draft_op_type":"NPT"}'},
        ])

        self.assertEqual(summary["r-1"], {"p_hours": 0.0, "sc_hours": 3.5, "npt_hours": 0.0})

    def test_report_upsert_does_not_overwrite_confirmation_lock(self) -> None:
        cursor = FakeCursor([])

        _upsert_record(cursor, {"record_id": "r-1"})

        statement = cursor.statements[0]
        update_clause = statement.split("ON DUPLICATE KEY UPDATE", 1)[1]
        self.assertNotIn("locked=VALUES(locked)", update_clause)
        self.assertNotIn("confirmation_status=VALUES(confirmation_status)", update_clause)
        self.assertIn("translation_status=VALUES(translation_status)", update_clause)

    def test_npt_revision_ignores_query_only_row_number(self) -> None:
        persisted = {"hours": "3.5", "op_type": "NPT"}
        loaded = {**persisted, "row_no": "7"}

        self.assertEqual(_npt_row_revision(persisted), _npt_row_revision(loaded))

    def test_npt_confirmation_resolves_stale_pending_issue_only_when_all_rows_are_ready(self) -> None:
        cursor = MagicMock()
        cursor.fetchone.return_value = {"count": 0}

        resolved = _resolve_classification_pending_issue(cursor, record_id="r-1", actor="admin")

        self.assertTrue(resolved)
        statements = [call.args[0] for call in cursor.execute.call_args_list]
        self.assertNotIn("source_op_type", statements[0])
        self.assertIn("UPDATE dq_issue", statements[1])
        self.assertEqual(cursor.execute.call_args_list[1].args[1][2], "r-1:CLASSIFICATION_PENDING")

    def test_npt_confirmation_keeps_issue_open_when_any_row_is_pending(self) -> None:
        cursor = MagicMock()
        cursor.fetchone.return_value = {"count": 1}

        resolved = _resolve_classification_pending_issue(cursor, record_id="r-1", actor="admin")

        self.assertFalse(resolved)
        self.assertEqual(cursor.execute.call_count, 1)

    def test_adds_all_translation_columns_to_an_existing_records_table(self) -> None:
        cursor = FakeCursor(["record_id", "status", "validation_status"])

        _ensure_report_record_columns(cursor)

        self.assertEqual(cursor.statements[0], "SHOW COLUMNS FROM dpr_report_record")
        alter_statements = cursor.statements[1:]
        expected_columns = [
            "source_page_start", "source_page_end", "source_report_index", "source_report_count",
            "batch_inherited_fields", "source_language", "translation_status", "translation_progress",
            "translation_error", "translation_version", "translation_updated_at", "extraction_status",
            "extraction_progress", "extraction_error", "extraction_version", "extraction_updated_at",
            "rig_id", "well_id", "project_id", "job_id", "master_match_status", "master_match_message",
        ]
        self.assertEqual(len(alter_statements), len(expected_columns))
        for statement, column in zip(alter_statements, expected_columns):
            self.assertIn(f"ADD COLUMN {column}", statement)

    def test_keeps_existing_translation_columns(self) -> None:
        cursor = FakeCursor([
            "record_id",
            "status",
            "source_page_start",
            "source_page_end",
            "source_report_index",
            "source_report_count",
            "batch_inherited_fields",
            "source_language",
            "translation_status",
            "translation_progress",
            "translation_error",
            "translation_version",
            "translation_updated_at",
            "extraction_status",
            "extraction_progress",
            "extraction_error",
            "extraction_version",
            "extraction_updated_at",
            "rig_id",
            "well_id",
            "project_id",
            "job_id",
            "master_match_status",
            "master_match_message",
        ])

        _ensure_report_record_columns(cursor)

        self.assertEqual(cursor.statements, ["SHOW COLUMNS FROM dpr_report_record"])


if __name__ == "__main__":
    unittest.main()
