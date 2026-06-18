from __future__ import annotations

import argparse
import cgi
import re
import json
import mimetypes
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .completion_pdf_parser import parse_completion_pdf_daily_report
from .excel_database import initialize_database, list_records, load_report_payload, save_report_payload
from .move_pdf_parser import parse_move_pdf_daily_report
from .pdf_report_parser import parse_pdf_daily_report
from .workover_pdf_parser import parse_workover_pdf_daily_report


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web_form"
DATABASE_PATH = ROOT / "outputs" / "report_database.xlsx"


class FormHandler(BaseHTTPRequestHandler):
    server_version = "DrillingReportForm/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", ""}:
            self.send_response(302)
            self.send_header("Location", "/web_form/")
            self.end_headers()
            return
        if parsed.path == "/web_form":
            self.send_response(302)
            self.send_header("Location", "/web_form/")
            self.end_headers()
            return
        if parsed.path == "/api/records":
            self._list_records(parsed.query)
            return
        if parsed.path == "/api/download-database":
            self._download_database()
            return
        self._serve_static()

    def do_POST(self) -> None:
        if self.path == "/api/import-pdf":
            self._import_pdf()
            return
        if self.path == "/api/import-completion-pdf":
            self._import_completion_pdf()
            return
        if self.path == "/api/import-workover-pdf":
            self._import_workover_pdf()
            return
        if self.path == "/api/import-move-pdf":
            self._import_move_pdf()
            return
        if self.path == "/api/save-report":
            self._save_report()
            return
        if self.path == "/api/load-report":
            self._load_report()
            return
        self.send_error(404)

    def _import_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            payload = parse_pdf_daily_report(upload.file.read())
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "drilling")
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_completion_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            payload = parse_completion_pdf_daily_report(upload.file.read())
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "completion")
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_workover_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            payload = parse_workover_pdf_daily_report(upload.file.read())
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "workover")
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_move_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            payload = parse_move_pdf_daily_report(upload.file.read())
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "move")
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _save_report(self) -> None:
        try:
            payload = self._read_json_body()
            report_type = str(payload.get("report_type", ""))
            report_payload = payload.get("payload", {})
            if not isinstance(report_payload, dict):
                self._send_json({"error": "Invalid report payload."}, status=400)
                return
            self._store_payload(report_payload, report_type)
            self._send_json({"ok": True, "metadata": report_payload.get("metadata", {})})
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _load_report(self) -> None:
        try:
            payload = self._read_json_body()
            record_id = str(payload.get("record_id", "")).strip()
            if not record_id:
                self._send_json({"error": "record_id is required."}, status=400)
                return
            self._send_json(load_report_payload(DATABASE_PATH, record_id))
        except KeyError:
            self._send_json({"error": "Record not found."}, status=404)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _list_records(self, query: str) -> None:
        params = parse_qs(query)
        report_type = (params.get("report_type") or [""])[0]
        records = list_records(DATABASE_PATH)
        if report_type:
            records = [record for record in records if record.get("report_type") == report_type]
        self._send_json({"records": records})

    def _download_database(self) -> None:
        if not DATABASE_PATH.exists():
            initialize_database(DATABASE_PATH)
        data = DATABASE_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", 'attachment; filename="report_database.xlsx"')
        self.end_headers()
        self.wfile.write(data)

    def _store_payload(self, payload: dict[str, object], report_type: str) -> None:
        metadata = payload.setdefault("metadata", {})
        warnings = _normalize_payload_values(payload) + _validation_warnings(payload, report_type)
        if isinstance(metadata, dict):
            metadata.setdefault("status", "parsed")
            metadata["validation_status"] = "warning" if warnings else "ok"
            metadata["validation_warnings"] = "; ".join(warnings)
        result = save_report_payload(
            DATABASE_PATH,
            payload,
            report_type,
            source_file=str(metadata.get("source_file", "")) if isinstance(metadata, dict) else "",
        )
        if isinstance(metadata, dict):
            metadata.update(result)

    def _read_json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def _serve_static(self) -> None:
        raw_path = unquote(self.path.split("?", 1)[0])
        if raw_path.startswith("/web_form/"):
            rel = raw_path.removeprefix("/web_form/")
            target = WEB_ROOT / (rel or "index.html")
        else:
            self.send_error(404)
            return

        target = target.resolve()
        if not str(target).startswith(str(WEB_ROOT.resolve())) or not target.exists() or target.is_dir():
            self.send_error(404)
            return

        data = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if target.suffix in {".html", ".css", ".js"}:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the drilling report web form with PDF import.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), FormHandler)
    print(f"Drilling report form: http://{args.host}:{args.port}/web_form/")
    server.serve_forever()


def _validation_warnings(payload: dict[str, object], report_type: str) -> list[str]:
    fields = payload.get("report_fields", {})
    if not isinstance(fields, dict):
        return ["report_fields missing"]
    required_by_type = {
        "drilling": ["reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"],
        "completion": ["reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"],
        "workover": ["reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"],
        "move": ["reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"],
    }
    warnings: list[str] = []
    for field in required_by_type.get(report_type, []):
        if not str(fields.get(field, "") or "").strip():
            warnings.append(f"{field} missing")
    operations = payload.get("operations", [])
    if isinstance(operations, list) and operations:
        total_hours = 0.0
        for index, row in enumerate(operations, start=1):
            if not isinstance(row, dict):
                continue
            try:
                total_hours += float(str(row.get("hours", "") or "0").replace(",", ""))
            except ValueError:
                warnings.append(f"operations row {index} hours invalid")
            valid_types = {"P", "NPT"} if report_type == "drilling" else {"P", "SC", "NPT"}
            if str(row.get("op_type", "") or "").strip() not in valid_types:
                warnings.append(f"operations row {index} type invalid")
        if abs(total_hours - 24.0) > 0.05:
            warnings.append(f"operation hours total {total_hours:.2f}")
    return warnings


DATE_FIELDS = {"reportDate", "operationStartDate", "date", "entry_date"}
TIME_FIELDS = {"from", "to", "mudTime", "entry_time"}
NUMERIC_REPORT_FIELDS = {
    "todayMd", "prevMd", "progress", "rotHrsToday", "lastCasingDepth", "nextCasingDepth",
    "pumpRate", "pumpPress", "mudMd", "mudDensity", "mudTemperature", "rheologyTemp",
    "viscosity", "pv", "yp", "gel10s", "gel10m", "gel30m", "apiWl", "oilPercent",
    "waterPercent", "sand", "ecd", "bitSize", "bhaMdIn", "bhaMdOut", "bhaTotalLength",
    "daysSinceRi", "daysSinceLta", "afeCost", "dailyCost", "cumulativeCost",
    "totalPersonnel", "groundElev",
}
NUMERIC_TABLE_FIELDS = {
    "md", "incl", "azi", "tvd", "vse", "ns", "dls", "build", "od", "id", "joints",
    "length", "hours", "amount", "qty_start", "qty_used", "qty_end", "top_md", "base_md",
    "density", "phase", "penetration", "diameter", "trip",
}


def _normalize_payload_values(payload: dict[str, object]) -> list[str]:
    warnings: list[str] = []
    fields = payload.get("report_fields", {})
    if isinstance(fields, dict):
        for key, value in list(fields.items()):
            if key in DATE_FIELDS:
                fields[key], warning = _normalize_date_value(value, key)
            elif key in TIME_FIELDS:
                fields[key], warning = _normalize_time_value(value, key)
            elif key in NUMERIC_REPORT_FIELDS:
                fields[key], warning = _normalize_number_value(value, key)
            else:
                warning = ""
            if warning:
                warnings.append(warning)

    for section, rows in payload.items():
        if section in {"metadata", "report_fields"} or not isinstance(rows, list):
            continue
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            for key, value in list(row.items()):
                label = f"{section} row {index} {key}"
                if key in DATE_FIELDS:
                    row[key], warning = _normalize_date_value(value, label)
                elif key in TIME_FIELDS:
                    row[key], warning = _normalize_time_value(value, label)
                elif key in NUMERIC_TABLE_FIELDS:
                    row[key], warning = _normalize_number_value(value, label)
                else:
                    warning = ""
                if warning:
                    warnings.append(warning)
    return warnings


def _normalize_date_value(value: object, label: str) -> tuple[str, str]:
    text = str(value or "").strip()
    if not text:
        return "", ""
    formats = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%m-%d-%Y")
    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt).date()
            if parsed > date.today():
                return parsed.isoformat(), f"{label} is in the future"
            return parsed.isoformat(), ""
        except ValueError:
            continue
    return text, f"{label} date invalid"


def _normalize_time_value(value: object, label: str) -> tuple[str, str]:
    text = str(value or "").strip()
    if not text:
        return "", ""
    match = re.fullmatch(r"(\d{1,2})[:：](\d{2})", text)
    if not match:
        return text, f"{label} time invalid"
    hour, minute = int(match.group(1)), int(match.group(2))
    if hour == 24 and minute == 0:
        return "24:00", ""
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return text, f"{label} time invalid"
    return f"{hour:02d}:{minute:02d}", ""


def _normalize_number_value(value: object, label: str) -> tuple[str, str]:
    text = str(value or "").strip()
    if not text:
        return "", ""
    cleaned = text.replace(",", "")
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", cleaned):
        return _trim_number(cleaned), ""
    match = re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", text)
    if not match:
        return text, f"{label} number invalid"
    leftovers = f"{text[:match.start()]} {text[match.end():]}".strip().lower()
    leftovers = re.sub(r"[\s,./()@:-]+", " ", leftovers).strip()
    allowed_units = {"ft", "feet", "in", "inch", "ppg", "psi", "gpm", "usd", "h", "hr", "hrs", "deg", "bbl", "spf", "lb", "lbs"}
    if not leftovers or all(part in allowed_units for part in leftovers.split()):
        return _trim_number(match.group(0).replace(",", "")), ""
    return _trim_number(match.group(0).replace(",", "")), f"{label} number corrected"


def _trim_number(value: str) -> str:
    if "." not in value:
        return value
    return value.rstrip("0").rstrip(".") or "0"


if __name__ == "__main__":
    main()
