from __future__ import annotations

import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any

from drilling_report_parser import form_server
from drilling_report_parser.excel_database import load_report_payload
from tests.test_pdf_report_parser import sample_pdf


class FormServerImportTest(unittest.TestCase):
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
                self.assertEqual(stored["report_fields"]["rig"], "00 SINOPEC 248")
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
