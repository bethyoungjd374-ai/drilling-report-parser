from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db_config import mysql_settings
from .excel_database import REPORT_TABLES, REPORT_TYPES


ROOT = Path(__file__).resolve().parents[1]
INIT_SQL_PATH = ROOT / "db" / "init.sql"

BASE_RECORD_COLUMNS = [
    "record_id",
    "report_type",
    "source_file",
    "parser",
    "reportDate",
    "reportNo",
    "wellbore",
    "rig",
    "status",
    "validation_status",
    "validation_warnings",
    "locked",
    "confirmation_status",
    "confirmed_at",
    "confirmed_by",
    "confirmation_note",
    "created_at",
    "updated_at",
]

MYSQL_RECORD_COLUMNS = {
    "reportDate": "report_date",
    "reportNo": "report_no",
}


def initialize_database() -> None:
    statements = _sql_statements(INIT_SQL_PATH)
    if not statements:
        return
    with _connect() as connection:
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        connection.commit()


def save_report_payload(
    database_path: str | Path | None,
    payload: dict[str, Any],
    report_type: str,
    *,
    source_file: str = "",
) -> dict[str, Any]:
    del database_path
    report_type = _normalize_report_type(report_type)
    initialize_database()
    fields = payload.get("report_fields", {}) or {}
    metadata = payload.get("metadata", {}) or {}
    record_id = str(metadata.get("record_id") or payload.get("record_id") or _natural_record_id(report_type, fields) or _generated_record_id(report_type))
    source_file = source_file or str(metadata.get("source_file") or "")
    now = _now()

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT locked, created_at FROM report_records WHERE record_id=%s", (record_id,))
            existing = cursor.fetchone() or {}
            if _truthy(existing.get("locked")):
                raise PermissionError(f"Record is locked after NPT confirmation: {record_id}")
            created_at = str(existing.get("created_at") or metadata.get("created_at") or now)
            updated_at = str(metadata.get("updated_at") or now)
            record = _record_from_payload(record_id, report_type, source_file, fields, metadata, created_at, updated_at)
            _upsert_record(cursor, record)
            cursor.execute(
                """
                INSERT INTO report_fields (record_id, fields_json)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE fields_json=VALUES(fields_json)
                """,
                (record_id, _json_dumps(fields)),
            )
            cursor.execute("DELETE FROM report_rows WHERE record_id=%s", (record_id,))
            for module_name in REPORT_TABLES[report_type]["multi"]:
                for row_no, row in enumerate(payload.get(module_name, []) or [], start=1):
                    if not isinstance(row, dict):
                        continue
                    cursor.execute(
                        """
                        INSERT INTO report_rows (record_id, module_name, row_no, row_json)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (record_id, module_name, row_no, _json_dumps(row)),
                    )
        connection.commit()
    return {"record_id": record_id, "database_path": "mysql", "updated_at": updated_at}


def load_report_payload(database_path: str | Path | None, record_id: str) -> dict[str, Any]:
    del database_path
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM report_records WHERE record_id=%s", (record_id,))
            record = cursor.fetchone()
            if not record:
                raise KeyError(record_id)
            report_type = _normalize_report_type(str(record.get("report_type", "") or ""))
            cursor.execute("SELECT fields_json FROM report_fields WHERE record_id=%s", (record_id,))
            fields_row = cursor.fetchone() or {}
            payload: dict[str, Any] = {
                "metadata": {
                    "record_id": record_id,
                    "report_type": report_type,
                    "source_file": record.get("source_file", ""),
                    "parser": record.get("parser", ""),
                    "locked": record.get("locked", ""),
                    "confirmation_status": record.get("confirmation_status", ""),
                    "confirmed_at": record.get("confirmed_at", ""),
                    "confirmed_by": record.get("confirmed_by", ""),
                    "confirmation_note": record.get("confirmation_note", ""),
                },
                "report_fields": _json_loads(fields_row.get("fields_json"), {}),
            }
            cursor.execute(
                "SELECT module_name, row_json FROM report_rows WHERE record_id=%s ORDER BY module_name, row_no",
                (record_id,),
            )
            rows = cursor.fetchall()
    for module_name in REPORT_TABLES[report_type]["multi"]:
        payload[module_name] = []
    for row in rows:
        module_name = str(row.get("module_name", "") or "")
        if module_name in payload:
            payload[module_name].append(_json_loads(row.get("row_json"), {}))
    return payload


def delete_report_payload(database_path: str | Path | None, record_id: str) -> bool:
    del database_path
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM report_records WHERE record_id=%s", (record_id,))
            deleted = cursor.rowcount > 0
        connection.commit()
    return deleted


def list_records(
    database_path: str | Path | None = None,
    *,
    report_type: str = "",
    wellbore: str = "",
    date: str = "",
    date_from: str = "",
    date_to: str = "",
) -> list[dict[str, str]]:
    del database_path
    clauses: list[str] = []
    args: list[object] = []
    if report_type:
        clauses.append("r.report_type=%s")
        args.append(report_type)
    if wellbore:
        clauses.append("r.wellbore=%s")
        args.append(wellbore)
    if date:
        clauses.append("r.report_date=%s")
        args.append(date)
    if date_from:
        clauses.append("r.report_date >= %s")
        args.append(date_from)
    if date_to:
        clauses.append("r.report_date <= %s")
        args.append(date_to)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
        SELECT r.*, f.fields_json
        FROM report_records r
        LEFT JOIN report_fields f ON f.record_id = r.record_id
        {where_sql}
        ORDER BY r.report_date DESC, r.updated_at DESC
    """
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
    return [_record_to_public(row) for row in rows]


def query_records(**filters: str) -> list[dict[str, str]]:
    return list_records(None, **filters)


def is_available() -> bool:
    try:
        with _connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        return True
    except Exception:
        return False


def _connect():
    settings = mysql_settings()
    if not settings.enabled:
        raise RuntimeError("MySQL storage is disabled.")
    if not settings.password:
        raise RuntimeError("MYSQL_PASSWORD is empty. Copy .env.example to .env and set a password.")
    try:
        import pymysql
    except ImportError as exc:
        raise RuntimeError("PyMySQL is not installed. Run: pip install -r requirements.txt") from exc
    return pymysql.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password,
        database=settings.database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        connect_timeout=settings.connect_timeout,
    )


def _upsert_record(cursor: Any, record: dict[str, str]) -> None:
    columns = [
        "record_id",
        "report_type",
        "source_file",
        "parser",
        "report_date",
        "report_no",
        "wellbore",
        "rig",
        "status",
        "validation_status",
        "validation_warnings",
        "locked",
        "confirmation_status",
        "confirmed_at",
        "confirmed_by",
        "confirmation_note",
        "created_at",
        "updated_at",
    ]
    placeholders = ", ".join(["%s"] * len(columns))
    update_clause = ", ".join(f"{column}=VALUES({column})" for column in columns if column != "record_id")
    cursor.execute(
        f"""
        INSERT INTO report_records ({", ".join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
        """,
        [record.get(column, "") for column in columns],
    )


def _record_from_payload(
    record_id: str,
    report_type: str,
    source_file: str,
    fields: dict[str, Any],
    metadata: dict[str, Any],
    created_at: str,
    updated_at: str,
) -> dict[str, str]:
    values = {
        "record_id": record_id,
        "report_type": report_type,
        "source_file": source_file,
        "parser": metadata.get("parser", ""),
        "reportDate": fields.get("reportDate", ""),
        "reportNo": fields.get("reportNo", ""),
        "wellbore": fields.get("wellbore", ""),
        "rig": fields.get("rig", ""),
        "status": metadata.get("status", "parsed"),
        "validation_status": metadata.get("validation_status", "ok"),
        "validation_warnings": metadata.get("validation_warnings", ""),
        "locked": metadata.get("locked", ""),
        "confirmation_status": metadata.get("confirmation_status", ""),
        "confirmed_at": metadata.get("confirmed_at", ""),
        "confirmed_by": metadata.get("confirmed_by", ""),
        "confirmation_note": metadata.get("confirmation_note", ""),
        "created_at": created_at,
        "updated_at": updated_at,
    }
    return {MYSQL_RECORD_COLUMNS.get(key, key): _text(value) for key, value in values.items()}


def _record_to_public(row: dict[str, Any]) -> dict[str, str]:
    fields = _json_loads(row.get("fields_json"), {})
    return {
        "record_id": _text(row.get("record_id")),
        "report_type": _text(row.get("report_type")),
        "source_file": _text(row.get("source_file")),
        "parser": _text(row.get("parser")),
        "reportDate": _text(row.get("report_date")),
        "reportNo": _text(row.get("report_no")),
        "wellbore": _text(row.get("wellbore")),
        "rig": _text(row.get("rig")),
        "status": _text(row.get("status")),
        "validation_status": _text(row.get("validation_status")),
        "validation_warnings": _text(row.get("validation_warnings")),
        "locked": _text(row.get("locked")),
        "confirmation_status": _text(row.get("confirmation_status")),
        "confirmed_at": _text(row.get("confirmed_at")),
        "confirmed_by": _text(row.get("confirmed_by")),
        "confirmation_note": _text(row.get("confirmation_note")),
        "created_at": _text(row.get("created_at")),
        "updated_at": _text(row.get("updated_at")),
        "afeNumber": _text(fields.get("afeNumber")),
        "event": _text(fields.get("event")),
    }


def _sql_statements(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [statement.strip() for statement in text.split(";") if statement.strip()]


def _json_dumps(value: Any) -> str:
    return json.dumps(_json_safe(value), ensure_ascii=False)


def _json_loads(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value or ""))
    except json.JSONDecodeError:
        return default


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if value is None:
        return ""
    return str(value)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "locked", "confirmed"}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_report_type(report_type: str) -> str:
    normalized = (report_type or "").strip().lower()
    if normalized not in REPORT_TYPES:
        raise ValueError(f"Unsupported report_type: {report_type}")
    return normalized


def _natural_record_id(report_type: str, fields: dict[str, Any]) -> str:
    parts = [report_type, fields.get("wellbore", ""), fields.get("reportDate", ""), fields.get("reportNo", "")]
    if not all(str(part or "").strip() for part in parts):
        return ""
    return ":".join(_slug(str(part)) for part in parts)


def _generated_record_id(report_type: str) -> str:
    return f"{report_type}:{_slug(_now())}"


def _slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return text.strip("-") or "unknown"
