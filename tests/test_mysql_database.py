from __future__ import annotations

import unittest

from drilling_report_parser.mysql_database import _ensure_report_record_columns, _npt_row_revision, _operation_hour_summary, _upsert_record


class FakeCursor:
    def __init__(self, columns: list[str]) -> None:
        self.columns = columns
        self.statements: list[str] = []

    def execute(self, statement: str, _args: object = None) -> None:
        self.statements.append(statement)

    def fetchall(self) -> list[dict[str, str]]:
        return [{"Field": column} for column in self.columns]


class MySQLDatabaseMigrationTest(unittest.TestCase):
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

        self.assertEqual(cursor.statements[0], "SHOW COLUMNS FROM report_records")
        alter_statements = cursor.statements[1:]
        self.assertEqual(len(alter_statements), 11)
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
        ])

        _ensure_report_record_columns(cursor)

        self.assertEqual(cursor.statements, ["SHOW COLUMNS FROM report_records"])


if __name__ == "__main__":
    unittest.main()
