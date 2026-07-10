from __future__ import annotations

import unittest

from drilling_report_parser.mysql_database import _ensure_report_record_columns


class FakeCursor:
    def __init__(self, columns: list[str]) -> None:
        self.columns = columns
        self.statements: list[str] = []

    def execute(self, statement: str) -> None:
        self.statements.append(statement)

    def fetchall(self) -> list[dict[str, str]]:
        return [{"Field": column} for column in self.columns]


class MySQLDatabaseMigrationTest(unittest.TestCase):
    def test_adds_all_translation_columns_to_an_existing_records_table(self) -> None:
        cursor = FakeCursor(["record_id", "status", "validation_status"])

        _ensure_report_record_columns(cursor)

        self.assertEqual(cursor.statements[0], "SHOW COLUMNS FROM report_records")
        alter_statements = cursor.statements[1:]
        self.assertEqual(len(alter_statements), 6)
        self.assertIn("ADD COLUMN source_language", alter_statements[0])
        self.assertIn("ADD COLUMN translation_status", alter_statements[1])
        self.assertIn("ADD COLUMN translation_progress", alter_statements[2])
        self.assertIn("ADD COLUMN translation_error", alter_statements[3])
        self.assertIn("ADD COLUMN translation_version", alter_statements[4])
        self.assertIn("ADD COLUMN translation_updated_at", alter_statements[5])

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
        ])

        _ensure_report_record_columns(cursor)

        self.assertEqual(cursor.statements, ["SHOW COLUMNS FROM report_records"])


if __name__ == "__main__":
    unittest.main()
