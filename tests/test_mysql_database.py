from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from drilling_report_parser.mysql_database import (
    DPR_TABLE_ALIASES,
    INIT_SQL_PATH,
    _ensure_master_data_v3_columns,
    _ensure_report_record_columns,
    load_analytics_view_rows,
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
        self.assertNotIn("CREATE TABLE IF NOT EXISTS rel_project_rig_assignment", schema)
        self.assertIn("hours_source VARCHAR(16)", schema)
        self.assertIn("activity.hours_source", schema)

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
