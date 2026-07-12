from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from drilling_report_parser import storage


class StorageMySQLOnlyTest(unittest.TestCase):
    def test_rejects_legacy_file_database_paths(self) -> None:
        with patch("drilling_report_parser.mysql_database.save_report_payload") as save:
            with self.assertRaisesRegex(ValueError, "Only MySQL storage"):
                storage.save_report_payload(Path("report_database.xlsx"), {"report_fields": {}}, "drilling")
        save.assert_not_called()

    def test_save_report_payload_delegates_to_mysql_only(self) -> None:
        payload = {
            "report_fields": {
                "reportDate": "2026-06-11",
                "reportNo": "1",
                "wellbore": "A-001",
                "rig": "RIG 1",
            }
        }
        with patch("drilling_report_parser.mysql_database.save_report_payload") as save:
            save.return_value = {"record_id": "drilling:A-001:2026-06-11:1", "database_path": "mysql"}

            result = storage.save_report_payload(Path("mysql"), payload, "drilling", source_file="daily.pdf")

        save.assert_called_once_with(None, payload, "drilling", source_file="daily.pdf", invalidate_translations=True)
        self.assertEqual(result["database_path"], "mysql")
        self.assertEqual(payload["metadata"]["database_path"], "mysql")

    def test_list_records_delegates_filters_to_mysql(self) -> None:
        with patch("drilling_report_parser.mysql_database.list_records") as list_records:
            list_records.return_value = [{"record_id": "1", "wellbore": "A-001"}]

            records = storage.list_records(
                Path("mysql"),
                report_type="drilling",
                wellbore="A-001",
                date_from="2026-06-01",
                date_to="2026-06-30",
            )

        list_records.assert_called_once_with(
            None,
            report_type="drilling",
            wellbore="A-001",
            date="",
            date_from="2026-06-01",
            date_to="2026-06-30",
        )
        self.assertEqual(records[0]["wellbore"], "A-001")

    def test_npt_confirmation_delegates_to_mysql(self) -> None:
        rows = [{"record_id": "1", "row_no": "1", "confirmed_op_type": "NPT"}]
        with patch("drilling_report_parser.mysql_database.save_npt_confirmation") as save:
            save.return_value = {"wellbore": "A-001", "status": "confirmed"}

            result = storage.save_npt_confirmation(
                Path("mysql"),
                "A-001",
                rows,
                rig="RIG 1",
                note="checked",
                confirmed_by="admin",
                submit=True,
            )

        save.assert_called_once_with(
            None,
            "A-001",
            rows,
            rig="RIG 1",
            note="checked",
            confirmed_by="admin",
            submit=True,
        )
        self.assertEqual(result["status"], "confirmed")


if __name__ == "__main__":
    unittest.main()
