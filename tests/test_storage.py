from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from drilling_report_parser import storage


class StorageFallbackTest(unittest.TestCase):
    def test_mysql_unavailable_falls_back_to_excel_save_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_default = storage.DEFAULT_EXCEL_PATH
            original_disabled_until = storage._mysql_disabled_until
            original_env = {key: os.environ.get(key) for key in ("DRP_USE_MYSQL", "MYSQL_PASSWORD", "MYSQL_PORT", "MYSQL_RETRY_SECONDS")}
            database = Path(tmp) / "report_database.xlsx"
            storage.DEFAULT_EXCEL_PATH = database
            storage._mysql_disabled_until = 0
            os.environ["DRP_USE_MYSQL"] = "true"
            os.environ["MYSQL_PASSWORD"] = "not-used"
            os.environ["MYSQL_PORT"] = "1"
            os.environ["MYSQL_RETRY_SECONDS"] = "1"
            try:
                result = storage.save_report_payload(database, {
                    "report_fields": {
                        "event": "DRILLING",
                        "reportDate": "2026-06-11",
                        "reportNo": "11",
                        "wellbore": "PCNC-040",
                        "rig": "SINOPEC 248",
                    },
                    "operations": [{"hours": "24", "op_type": "P"}],
                }, "drilling")

                loaded = storage.load_report_payload(database, result["record_id"])
                self.assertEqual(loaded["report_fields"]["wellbore"], "PCNC-040")
                self.assertEqual(len(loaded["operations"]), 1)
            finally:
                storage.DEFAULT_EXCEL_PATH = original_default
                storage._mysql_disabled_until = original_disabled_until
                for key, value in original_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_excel_fallback_list_records_filters_basic_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "report_database.xlsx"
            original = os.environ.get("DRP_USE_MYSQL")
            os.environ["DRP_USE_MYSQL"] = "false"
            try:
                storage.save_report_payload(database, {
                    "report_fields": {"reportDate": "2026-06-11", "reportNo": "1", "wellbore": "A-001", "rig": "RIG 1"},
                }, "drilling")
                storage.save_report_payload(database, {
                    "report_fields": {"reportDate": "2026-06-12", "reportNo": "2", "wellbore": "B-002", "rig": "RIG 2"},
                }, "completion")

                self.assertEqual(len(storage.list_records(database, report_type="drilling")), 1)
                self.assertEqual(storage.list_records(database, wellbore="B-002")[0]["report_type"], "completion")
                self.assertEqual(storage.list_records(database, date="2026-06-11")[0]["wellbore"], "A-001")
                self.assertEqual(len(storage.list_records(database, date_from="2026-06-12", date_to="2026-06-12")), 1)
            finally:
                if original is None:
                    os.environ.pop("DRP_USE_MYSQL", None)
                else:
                    os.environ["DRP_USE_MYSQL"] = original


if __name__ == "__main__":
    unittest.main()
