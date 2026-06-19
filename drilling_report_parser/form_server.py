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
        if parsed.path == "/api/well-stats":
            self._well_stats(parsed.query)
            return
        if parsed.path == "/api/production-summary":
            self._production_summary(parsed.query)
            return
        if parsed.path == "/api/npt-stats":
            self._npt_stats(parsed.query)
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

    def _well_stats(self, query: str) -> None:
        params = parse_qs(query)
        report_type = (params.get("report_type") or [""])[0]
        wellbore = (params.get("wellbore") or [""])[0]
        records = list_records(DATABASE_PATH)
        matched = [
            record for record in records
            if (not report_type or record.get("report_type") == report_type)
            and (not wellbore or record.get("wellbore") == wellbore)
        ]
        stats = {
            "days": len({record.get("reportDate") for record in matched if record.get("reportDate")}),
            "total_hours": 0.0,
            "npt_hours": 0.0,
            "p_hours": 0.0,
            "sc_hours": 0.0,
        }
        for record in matched:
            record_id = str(record.get("record_id") or "")
            if not record_id:
                continue
            try:
                payload = load_report_payload(DATABASE_PATH, record_id)
            except KeyError:
                continue
            operations = payload.get("operations", [])
            if not isinstance(operations, list):
                continue
            for row in operations:
                if not isinstance(row, dict):
                    continue
                try:
                    hours = float(str(row.get("hours", "") or "0").replace(",", ""))
                except ValueError:
                    hours = 0.0
                op_type = str(row.get("op_type", "") or "").strip().upper()
                stats["total_hours"] += hours
                if op_type == "NPT":
                    stats["npt_hours"] += hours
                elif op_type == "SC":
                    stats["sc_hours"] += hours
                elif op_type == "P":
                    stats["p_hours"] += hours
        self._send_json(stats)

    def _production_summary(self, query: str) -> None:
        self._send_json(_production_summary_payload(DATABASE_PATH, parse_qs(query)))

    def _npt_stats(self, query: str) -> None:
        self._send_json(_npt_stats_payload(DATABASE_PATH, parse_qs(query)))

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

REPORT_TYPE_LABELS = {
    "drilling": "钻井",
    "completion": "完井",
    "workover": "修井",
    "move": "搬迁/推井架",
}


def _production_summary_payload(database_path: Path, params: dict[str, list[str]]) -> dict[str, object]:
    rows = _filtered_fact_rows(database_path, params)
    records = rows["records"]
    operations = rows["operations"]
    unique_rigs = sorted({record["rig"] for record in records if record["rig"]})
    unique_wells = sorted({record["wellbore"] for record in records if record["wellbore"]})
    total_hours = sum(row["hours"] for row in operations)
    npt_hours = sum(row["hours"] for row in operations if row["op_type"] == "NPT")
    completeness = _completeness(records)

    by_rig: dict[str, dict[str, float]] = {}
    by_type = {key: 0.0 for key in REPORT_TYPE_LABELS}
    monthly: dict[str, dict[str, float]] = {}
    detail: dict[tuple[str, str, str], dict[str, object]] = {}

    for row in operations:
        rig = row["rig"] or "未识别井队"
        report_type = row["report_type"]
        type_label = REPORT_TYPE_LABELS.get(report_type, report_type)
        by_rig.setdefault(rig, {label: 0.0 for label in REPORT_TYPE_LABELS.values()})
        by_rig[rig][type_label] = by_rig[rig].get(type_label, 0.0) + row["hours"]
        if report_type in by_type:
            by_type[report_type] += row["hours"]
        month = row["reportDate"][:7] or "未识别"
        monthly.setdefault(month, {label: 0.0 for label in REPORT_TYPE_LABELS.values()})
        monthly[month][type_label] = monthly[month].get(type_label, 0.0) + row["hours"]
        key = (rig, row["wellbore"], report_type)
        item = detail.setdefault(key, {
            "rig": rig,
            "wellbore": row["wellbore"],
            "report_type": report_type,
            "report_type_label": type_label,
            "start_date": row["reportDate"],
            "end_date": row["reportDate"],
            "drilling_hours": 0.0,
            "completion_hours": 0.0,
            "workover_hours": 0.0,
            "move_hours": 0.0,
            "npt_hours": 0.0,
            "record_id": row["record_id"],
            "status": "",
        })
        item["start_date"] = min(str(item["start_date"] or row["reportDate"]), row["reportDate"])
        item["end_date"] = max(str(item["end_date"] or row["reportDate"]), row["reportDate"])
        item[f"{report_type}_hours"] = float(item.get(f"{report_type}_hours", 0.0)) + row["hours"]
        if row["op_type"] == "NPT":
            item["npt_hours"] = float(item["npt_hours"]) + row["hours"]

    record_index = {(record["rig"], record["wellbore"], record["report_type"]): record for record in records}
    for key, item in detail.items():
        record = record_index.get(key, {})
        item["status"] = "有告警" if record.get("validation_status") == "warning" else "正常"

    return {
        "filters": _filter_options(records),
        "kpis": {
            "rig_count": len(unique_rigs),
            "well_count": len(unique_wells),
            "total_hours": round(total_hours, 2),
            "npt_hours": round(npt_hours, 2),
            "completeness": completeness,
        },
        "by_rig": [{"rig": rig, **{key: round(value, 2) for key, value in values.items()}} for rig, values in sorted(by_rig.items())],
        "by_type": [{"report_type": key, "label": REPORT_TYPE_LABELS[key], "hours": round(value, 2)} for key, value in by_type.items()],
        "monthly": [{"month": month, **{key: round(value, 2) for key, value in values.items()}} for month, values in sorted(monthly.items())],
        "details": [{**item, **{k: round(float(item.get(k, 0.0)), 2) for k in ("drilling_hours", "completion_hours", "workover_hours", "move_hours", "npt_hours")}} for item in detail.values()],
        "scope_note": "基于已保存到 Excel 库的日报解析数据",
    }


def _npt_stats_payload(database_path: Path, params: dict[str, list[str]]) -> dict[str, object]:
    rows = _filtered_fact_rows(database_path, params)
    records = rows["records"]
    npt_rows = [row for row in rows["operations"] if row["op_type"] == "NPT"]
    category_filter = _param(params, "reason")
    if category_filter:
        npt_rows = [row for row in npt_rows if row["reason"] == category_filter]
    total_npt = sum(row["hours"] for row in npt_rows)
    rigs = sorted({row["rig"] for row in npt_rows if row["rig"]})
    wells = sorted({row["wellbore"] for row in npt_rows if row["wellbore"]})

    by_rig = _sum_by(npt_rows, "rig")
    by_well = _sum_by(npt_rows, "wellbore")
    by_reason = _sum_by(npt_rows, "reason")
    by_month = _sum_by(npt_rows, "month")

    return {
        "filters": {**_filter_options(records), "reasons": sorted({row["reason"] for row in rows["operations"] if row["op_type"] == "NPT"})},
        "kpis": {
            "rig_count": len(rigs),
            "well_count": len(wells),
            "event_count": len(npt_rows),
            "total_npt": round(total_npt, 2),
        },
        "by_rig": [{"label": key, "hours": round(value, 2)} for key, value in by_rig],
        "by_well": [{"label": key, "hours": round(value, 2)} for key, value in by_well[:10]],
        "by_reason": [{"label": key, "hours": round(value, 2), "share": round((value / total_npt * 100) if total_npt else 0, 1)} for key, value in by_reason],
        "monthly": [{"month": key, "hours": round(value, 2)} for key, value in by_month],
        "details": [{
            "record_id": row["record_id"],
            "report_type": row["report_type"],
            "rig": row["rig"],
            "wellbore": row["wellbore"],
            "reportDate": row["reportDate"],
            "hours": round(row["hours"], 2),
            "reason": row["reason"],
            "op_code": row["op_code"],
            "op_sub": row["op_sub"],
            "operation_details": row["operation_details"],
        } for row in npt_rows],
        "scope_note": "基于已保存到 Excel 库的日报解析数据；分类按日报 OP CODE / OP SUB 汇总",
    }


def _filtered_fact_rows(database_path: Path, params: dict[str, list[str]]) -> dict[str, list[dict[str, object]]]:
    date_from = _param(params, "date_from")
    date_to = _param(params, "date_to")
    rig_filter = _param(params, "rig")
    type_filter = _param(params, "report_type")
    well_filter = _param(params, "wellbore")
    records = []
    operations = []
    for record in list_records(database_path):
        report_date = record.get("reportDate", "")
        if date_from and report_date < date_from:
            continue
        if date_to and report_date > date_to:
            continue
        if rig_filter and record.get("rig") != rig_filter:
            continue
        if type_filter and record.get("report_type") != type_filter:
            continue
        if well_filter and record.get("wellbore") != well_filter:
            continue
        records.append(record)
        try:
            payload = load_report_payload(database_path, str(record.get("record_id") or ""))
        except (KeyError, FileNotFoundError, ValueError):
            continue
        for row in payload.get("operations", []) if isinstance(payload.get("operations", []), list) else []:
            if not isinstance(row, dict):
                continue
            hours = _safe_float(row.get("hours"))
            op_type = str(row.get("op_type", "") or "").strip().upper()
            fact = {
                "record_id": record.get("record_id", ""),
                "report_type": record.get("report_type", ""),
                "reportDate": report_date,
                "month": report_date[:7],
                "wellbore": record.get("wellbore", ""),
                "rig": record.get("rig", ""),
                "validation_status": record.get("validation_status", ""),
                "hours": hours,
                "op_type": op_type,
                "op_code": str(row.get("op_code", "") or ""),
                "op_sub": str(row.get("op_sub", "") or ""),
                "operation_details": str(row.get("operation_details", "") or ""),
            }
            fact["reason"] = _operation_category(fact)
            operations.append(fact)
    return {"records": records, "operations": operations}


def _filter_options(records: list[dict[str, str]]) -> dict[str, object]:
    return {
        "rigs": sorted({record.get("rig", "") for record in records if record.get("rig")}),
        "wells": sorted({record.get("wellbore", "") for record in records if record.get("wellbore")}),
        "report_types": [{"value": key, "label": REPORT_TYPE_LABELS[key]} for key in REPORT_TYPE_LABELS],
    }


def _completeness(records: list[dict[str, str]]) -> dict[str, object]:
    uploaded = {record.get("reportDate") for record in records if record.get("reportDate")}
    warnings = {record.get("reportDate") for record in records if record.get("reportDate") and record.get("validation_status") == "warning"}
    missing = _missing_dates(uploaded)
    expected = len(uploaded) + len(missing)
    percent = round(((len(uploaded) - len(warnings) * 0.35) / expected * 100) if expected else 0, 1)
    return {"percent": max(0, percent), "missing_days": len(missing), "warning_days": len(warnings)}


def _missing_dates(dates: set[str]) -> list[str]:
    clean = sorted(date for date in dates if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""))
    if len(clean) < 2:
        return []
    cursor = datetime.strptime(clean[0], "%Y-%m-%d").date()
    end = datetime.strptime(clean[-1], "%Y-%m-%d").date()
    existing = set(clean)
    missing = []
    while cursor <= end:
        value = cursor.isoformat()
        if value not in existing:
            missing.append(value)
        cursor = date.fromordinal(cursor.toordinal() + 1)
    return missing


def _sum_by(rows: list[dict[str, object]], key: str) -> list[tuple[str, float]]:
    totals: dict[str, float] = {}
    for row in rows:
        label = str(row.get(key) or "未识别")
        totals[label] = totals.get(label, 0.0) + float(row.get("hours") or 0.0)
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)


def _operation_category(row: dict[str, object]) -> str:
    op_code = str(row.get("op_code", "") or "").strip()
    op_sub = str(row.get("op_sub", "") or "").strip()
    if op_code and op_sub:
        return f"{op_code} / {op_sub}"
    if op_code:
        return op_code
    if op_sub:
        return op_sub
    return "未填写 OP CODE / OP SUB"


def _safe_float(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def _param(params: dict[str, list[str]], key: str) -> str:
    return str((params.get(key) or [""])[0] or "").strip()


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
