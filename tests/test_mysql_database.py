from __future__ import annotations

import unittest
from pathlib import Path

from drilling_report_parser.mysql_database import (
    DPR_TABLE_ALIASES,
    INIT_SQL_PATH,
    _ensure_report_record_columns,
    _migrate_dpr_table_names,
    _npt_row_revision,
    _operation_hour_summary,
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

    def test_adds_all_translation_columns_to_an_existing_records_table(self) -> None:
        cursor = FakeCursor(["record_id", "status", "validation_status"])

        _ensure_report_record_columns(cursor)

        self.assertEqual(cursor.statements[0], "SHOW COLUMNS FROM dpr_report_record")
        alter_statements = cursor.statements[1:]
        self.assertEqual(len(alter_statements), 17)
        self.assertIn("ADD COLUMN source_language", alter_statements[0])
        self.assertIn("ADD COLUMN translation_status", alter_statements[1])
        self.assertIn("ADD COLUMN translation_progress", alter_statements[2])
        self.assertIn("ADD COLUMN translation_error", alter_statements[3])
        self.assertIn("ADD COLUMN translation_version", alter_statements[4])
        self.assertIn("ADD COLUMN translation_updated_at", alter_statements[5])
        self.assertIn("ADD COLUMN extraction_status", alter_statements[6])
        self.assertIn("ADD COLUMN extraction_progress", alter_statements[7])
        self.assertIn("ADD COLUMN extraction_error", alter_statements[8])
        self.assertIn("ADD COLUMN extraction_version", alter_statements[9])
        self.assertIn("ADD COLUMN extraction_updated_at", alter_statements[10])
        self.assertIn("ADD COLUMN rig_id", alter_statements[11])
        self.assertIn("ADD COLUMN well_id", alter_statements[12])
        self.assertIn("ADD COLUMN project_id", alter_statements[13])
        self.assertIn("ADD COLUMN job_id", alter_statements[14])
        self.assertIn("ADD COLUMN master_match_status", alter_statements[15])
        self.assertIn("ADD COLUMN master_match_message", alter_statements[16])

    def test_keeps_existing_translation_columns(self) -> None:
        cursor = FakeCursor([
            "record_id",
            "status",
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
