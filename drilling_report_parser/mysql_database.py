from __future__ import annotations

import hashlib
import json
import re
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db_config import mysql_settings
from .report_schema import REPORT_TABLES, REPORT_TYPES


ROOT = Path(__file__).resolve().parents[1]
INIT_SQL_PATH = ROOT / "db" / "init.sql"
_DATABASE_INITIALIZED = False
_DATABASE_INIT_LOCK = threading.Lock()

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
    "source_language",
    "translation_status",
    "translation_progress",
    "translation_error",
    "translation_version",
    "translation_updated_at",
    "extraction_status", "extraction_progress", "extraction_error", "extraction_version", "extraction_updated_at",
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
    global _DATABASE_INITIALIZED
    if _DATABASE_INITIALIZED:
        return
    with _DATABASE_INIT_LOCK:
        if _DATABASE_INITIALIZED:
            return
        statements = _sql_statements(INIT_SQL_PATH)
        if not statements:
            return
        with _connect() as connection:
            with connection.cursor() as cursor:
                for statement in statements:
                    if _server_scope_statement(statement):
                        continue
                    cursor.execute(statement)
                _ensure_report_record_columns(cursor)
                _ensure_translation_content_indexes(cursor)
            connection.commit()
        _DATABASE_INITIALIZED = True


@contextmanager
def background_job_lock(kind: str, record_id: str):
    lock_key = hashlib.sha256(f"drp:{kind}:{record_id}".encode("utf-8")).hexdigest()[:60]
    connection = _connect()
    acquired = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT GET_LOCK(%s, 0) AS acquired", (lock_key,))
            acquired = bool((cursor.fetchone() or {}).get("acquired"))
        yield acquired
    finally:
        if acquired:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT RELEASE_LOCK(%s)", (lock_key,))
            except Exception:
                pass
        connection.close()


def _ensure_report_record_columns(cursor: Any) -> None:
    cursor.execute("SHOW COLUMNS FROM report_records")
    columns = {str(row.get("Field", "") or "") for row in cursor.fetchall()}
    migrations = (
        ("source_language", "VARCHAR(16) NOT NULL DEFAULT '' AFTER status"),
        ("translation_status", "VARCHAR(64) NOT NULL DEFAULT '' AFTER source_language"),
        ("translation_progress", "VARCHAR(16) NOT NULL DEFAULT '' AFTER translation_status"),
        ("translation_error", "TEXT NULL AFTER translation_progress"),
        ("translation_version", "VARCHAR(64) NOT NULL DEFAULT '' AFTER translation_error"),
        ("translation_updated_at", "VARCHAR(64) NOT NULL DEFAULT '' AFTER translation_version"),
        ("extraction_status", "VARCHAR(64) NOT NULL DEFAULT '' AFTER translation_updated_at"),
        ("extraction_progress", "VARCHAR(16) NOT NULL DEFAULT '' AFTER extraction_status"),
        ("extraction_error", "TEXT NULL AFTER extraction_progress"),
        ("extraction_version", "VARCHAR(64) NOT NULL DEFAULT '' AFTER extraction_error"),
        ("extraction_updated_at", "VARCHAR(64) NOT NULL DEFAULT '' AFTER extraction_version"),
    )
    for column, definition in migrations:
        if column in columns:
            continue
        cursor.execute(f"ALTER TABLE report_records ADD COLUMN {column} {definition}")
        columns.add(column)


def _ensure_translation_content_indexes(cursor: Any) -> None:
    cursor.execute("SHOW INDEX FROM translation_content")
    indexes = {str(row.get("Key_name", "") or "") for row in cursor.fetchall()}
    if "idx_translation_memory_lookup" not in indexes:
        cursor.execute(
            "CREATE INDEX idx_translation_memory_lookup "
            "ON translation_content (target_language, prompt_version, translation_status, source_hash)"
        )


def save_report_payload(
    database_path: str | Path | None,
    payload: dict[str, Any],
    report_type: str,
    *,
    source_file: str = "",
    invalidate_translations: bool = True,
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
            cursor.execute(
                "SELECT locked, created_at FROM report_records WHERE record_id=%s FOR UPDATE",
                (record_id,),
            )
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
            if invalidate_translations:
                cursor.execute("DELETE FROM translation_content WHERE record_id=%s", (record_id,))
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
                    "source_language": record.get("source_language", ""),
                    "translation_status": record.get("translation_status", ""),
                    "translation_progress": record.get("translation_progress", ""),
                    "translation_error": record.get("translation_error", ""),
                    "translation_version": record.get("translation_version", ""),
                    "translation_updated_at": record.get("translation_updated_at", ""),
                    "extraction_status": record.get("extraction_status", ""),
                    "extraction_progress": record.get("extraction_progress", ""),
                    "extraction_error": record.get("extraction_error", ""),
                    "extraction_version": record.get("extraction_version", ""),
                    "extraction_updated_at": record.get("extraction_updated_at", ""),
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
    translation_content = load_translation_content(None, record_id)
    if translation_content:
        payload["translation_content"] = translation_content
    return payload


def load_report_payloads(
    database_path: str | Path | None,
    record_ids: list[str],
    *,
    include_translations: bool = False,
) -> dict[str, dict[str, Any]]:
    del database_path
    clean_ids = list(dict.fromkeys(str(value or "").strip() for value in record_ids if str(value or "").strip()))
    if not clean_ids:
        return {}
    placeholders = ",".join(["%s"] * len(clean_ids))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT r.*, f.fields_json
                FROM report_records r
                LEFT JOIN report_fields f ON f.record_id=r.record_id
                WHERE r.record_id IN ({placeholders})
                """,
                clean_ids,
            )
            records = cursor.fetchall()
            cursor.execute(
                f"""
                SELECT record_id, module_name, row_no, row_json
                FROM report_rows
                WHERE record_id IN ({placeholders})
                ORDER BY record_id, module_name, row_no
                """,
                clean_ids,
            )
            rows = cursor.fetchall()
            translations: list[dict[str, Any]] = []
            if include_translations:
                cursor.execute(
                    f"SELECT * FROM translation_content WHERE record_id IN ({placeholders})",
                    clean_ids,
                )
                translations = cursor.fetchall()

    payloads: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = _text(record.get("record_id"))
        report_type = _normalize_report_type(_text(record.get("report_type")))
        payloads[record_id] = {
            "metadata": _payload_metadata(record),
            "report_fields": _json_loads(record.get("fields_json"), {}),
            **{module_name: [] for module_name in REPORT_TABLES[report_type]["multi"]},
        }
    for row in rows:
        payload = payloads.get(_text(row.get("record_id")))
        module_name = _text(row.get("module_name"))
        if payload is not None and isinstance(payload.get(module_name), list):
            payload[module_name].append(_json_loads(row.get("row_json"), {}))
    if include_translations:
        for row in translations:
            payload = payloads.get(_text(row.get("record_id")))
            if payload is not None:
                payload.setdefault("translation_content", []).append({
                    key: _text(value)
                    for key, value in row.items()
                    if key != "mysql_updated_at"
                })
    return payloads


def delete_report_payload(database_path: str | Path | None, record_id: str) -> bool:
    del database_path
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM report_records WHERE record_id=%s", (record_id,))
            deleted = cursor.rowcount > 0
        connection.commit()
    return deleted


def save_translation_content(database_path: str | Path | None, record_id: str, rows: list[dict[str, Any]]) -> None:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM translation_content WHERE record_id=%s", (record_id,))
            for row in rows:
                if not isinstance(row, dict):
                    continue
                cursor.execute(
                    """
                    INSERT INTO translation_content (
                      record_id, entity_type, entity_id, field_code, source_language, target_language,
                      source_text, translated_text, source_hash, model_config_id, prompt_version,
                      translation_status, error_message, is_manual_modified, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                      source_text=VALUES(source_text),
                      translated_text=VALUES(translated_text),
                      source_hash=VALUES(source_hash),
                      model_config_id=VALUES(model_config_id),
                      prompt_version=VALUES(prompt_version),
                      translation_status=VALUES(translation_status),
                      error_message=VALUES(error_message),
                      is_manual_modified=VALUES(is_manual_modified),
                      updated_at=VALUES(updated_at)
                    """,
                    (
                        record_id,
                        _text(row.get("entity_type")),
                        _text(row.get("entity_id")),
                        _text(row.get("field_code")),
                        _text(row.get("source_language")),
                        _text(row.get("target_language")),
                        _text(row.get("source_text")),
                        _text(row.get("translated_text")),
                        _text(row.get("source_hash")),
                        _text(row.get("model_config_id")),
                        _text(row.get("prompt_version")),
                        _text(row.get("translation_status")),
                        _text(row.get("error_message")),
                        _text(row.get("is_manual_modified")),
                        _text(row.get("created_at")),
                        _text(row.get("updated_at")),
                    ),
                )
        connection.commit()


def upsert_translation_content(database_path: str | Path | None, record_id: str, rows: list[dict[str, Any]]) -> None:
    """Persist completed translation units without replacing other units for the report."""
    del database_path
    if not record_id or not rows:
        return
    initialize_database()
    values = [
        (
            record_id,
            _text(row.get("entity_type")),
            _text(row.get("entity_id")),
            _text(row.get("field_code")),
            _text(row.get("source_language")),
            _text(row.get("target_language")),
            _text(row.get("source_text")),
            _text(row.get("translated_text")),
            _text(row.get("source_hash")),
            _text(row.get("model_config_id")),
            _text(row.get("prompt_version")),
            _text(row.get("translation_status")),
            _text(row.get("error_message")),
            _text(row.get("is_manual_modified")),
            _text(row.get("created_at")),
            _text(row.get("updated_at")),
        )
        for row in rows
        if isinstance(row, dict)
    ]
    if not values:
        return
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO translation_content (
                  record_id, entity_type, entity_id, field_code, source_language, target_language,
                  source_text, translated_text, source_hash, model_config_id, prompt_version,
                  translation_status, error_message, is_manual_modified, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  source_text=VALUES(source_text),
                  translated_text=VALUES(translated_text),
                  source_hash=VALUES(source_hash),
                  model_config_id=VALUES(model_config_id),
                  prompt_version=VALUES(prompt_version),
                  translation_status=VALUES(translation_status),
                  error_message=VALUES(error_message),
                  is_manual_modified=IF(is_manual_modified<>'', is_manual_modified, VALUES(is_manual_modified)),
                  updated_at=VALUES(updated_at)
                """,
                values,
            )
        connection.commit()


def load_translation_content(database_path: str | Path | None, record_id: str) -> list[dict[str, str]]:
    del database_path
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM translation_content WHERE record_id=%s", (record_id,))
            rows = cursor.fetchall()
    return [{key: _text(value) for key, value in row.items() if key != "mysql_updated_at"} for row in rows]


def load_translation_memory(
    database_path: str | Path | None,
    target_language: str,
    prompt_version: str,
    source_hashes: list[str] | None = None,
) -> dict[str, str]:
    del database_path
    with _connect() as connection:
        with connection.cursor() as cursor:
            clean_hashes = list(dict.fromkeys(
                str(value or "").strip()
                for value in source_hashes or []
                if str(value or "").strip()
            ))
            hash_filter = ""
            args: list[object] = [target_language, prompt_version]
            if clean_hashes:
                placeholders = ",".join(["%s"] * len(clean_hashes))
                hash_filter = f" AND source_hash IN ({placeholders})"
                args.extend(clean_hashes)
            cursor.execute(
                f"""
                SELECT source_hash, translated_text, is_manual_modified, updated_at
                FROM translation_content
                WHERE target_language=%s
                  AND prompt_version=%s
                  AND translation_status='COMPLETED'
                  AND source_hash<>''
                  AND translated_text<>''
                  {hash_filter}
                ORDER BY (is_manual_modified<>'') DESC, updated_at DESC
                """,
                args,
            )
            rows = cursor.fetchall()
    memory: dict[str, str] = {}
    for row in rows:
        key = _text(row.get("source_hash"))
        value = _text(row.get("translated_text"))
        if key and value and key not in memory:
            memory[key] = value
    return memory


def load_operation_translations(database_path: str | Path | None, record_ids: list[str]) -> list[dict[str, str]]:
    del database_path
    clean_ids = list(dict.fromkeys(record_id for record_id in record_ids if record_id))
    if not clean_ids:
        return []
    placeholders = ",".join(["%s"] * len(clean_ids))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT record_id, entity_id, source_text, translated_text, source_hash,
                       target_language, translation_status, error_message
                FROM translation_content
                WHERE record_id IN ({placeholders})
                  AND entity_type='operations'
                  AND field_code='operations.operation_details'
                  AND target_language='zh-CN'
                """,
                clean_ids,
            )
            rows = cursor.fetchall()
    return [{key: _text(value) for key, value in row.items()} for row in rows]


def clear_translation_content(database_path: str | Path | None, record_id: str = "") -> None:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            if record_id:
                cursor.execute("DELETE FROM translation_content WHERE record_id=%s", (record_id,))
            else:
                cursor.execute("DELETE FROM translation_content")
            connection.commit()


def reset_translation_state(database_path: str | Path | None, record_id: str = "") -> dict[str, int]:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            if record_id:
                cursor.execute("DELETE FROM translation_content WHERE record_id=%s", (record_id,))
                deleted_rows = cursor.rowcount
                cursor.execute(
                    """
                    UPDATE report_records
                    SET translation_status='PENDING', translation_progress='0',
                        translation_error='', translation_version='', translation_updated_at=%s
                    WHERE record_id=%s
                    """,
                    (_now(), record_id),
                )
            else:
                cursor.execute("DELETE FROM translation_content")
                deleted_rows = cursor.rowcount
                cursor.execute(
                    """
                    UPDATE report_records
                    SET translation_status='PENDING', translation_progress='0',
                        translation_error='', translation_version='', translation_updated_at=%s
                    """,
                    (_now(),),
                )
            reset_records = cursor.rowcount
        connection.commit()
    return {"deleted_translation_rows": deleted_rows, "reset_records": reset_records}


def update_record_translation_status(
    database_path: str | Path | None,
    record_id: str,
    *,
    status: str,
    progress: int | str = "",
    error: str = "",
    version: str = "",
) -> None:
    del database_path
    if not record_id:
        return
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            if version:
                cursor.execute(
                    """
                    UPDATE report_records
                    SET translation_status=%s, translation_progress=%s, translation_error=%s,
                        translation_version=%s, translation_updated_at=%s
                    WHERE record_id=%s
                    """,
                    (_text(status), _text(progress), _text(error)[:500], _text(version), _now(), record_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE report_records
                    SET translation_status=%s, translation_progress=%s, translation_error=%s, translation_updated_at=%s
                    WHERE record_id=%s
                    """,
                    (_text(status), _text(progress), _text(error)[:500], _now(), record_id),
                )
            connection.commit()


def update_record_extraction_status(database_path: str | Path | None, record_id: str, *, status: str, progress: int | str = "", error: str = "", version: str = "") -> None:
    del database_path
    if not record_id:
        return
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE report_records SET extraction_status=%s, extraction_progress=%s,
                   extraction_error=%s, extraction_version=IF(%s='', extraction_version, %s), extraction_updated_at=%s
                   WHERE record_id=%s""",
                (_text(status), _text(progress), _text(error)[:500], _text(version), _text(version), _now(), record_id),
            )
        connection.commit()


def save_extraction_results(database_path: str | Path | None, rows: list[dict[str, Any]]) -> None:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            for row in rows:
                cursor.execute(
                    """INSERT INTO ai_extraction_results
                    (record_id, rule_id, source_section, source_row_no, source_field, target_field,
                     source_hash, result_text, extraction_status, error_message, model_config_id,
                     rule_version, attempt_count, started_at, completed_at, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE source_hash=VALUES(source_hash), result_text=VALUES(result_text),
                    extraction_status=VALUES(extraction_status), error_message=VALUES(error_message),
                    model_config_id=VALUES(model_config_id), rule_version=VALUES(rule_version),
                    attempt_count=VALUES(attempt_count), started_at=VALUES(started_at),
                    completed_at=VALUES(completed_at), updated_at=VALUES(updated_at)""",
                    (_text(row.get("record_id")), _text(row.get("rule_id")), _text(row.get("source_section")), int(row.get("source_row_no", 0) or 0),
                     _text(row.get("source_field")), _text(row.get("target_field")), _text(row.get("source_hash")), _text(row.get("result_text")),
                     _text(row.get("extraction_status")), _text(row.get("error_message"))[:500], _text(row.get("model_config_id")), _text(row.get("rule_version")),
                     int(row.get("attempt_count", 0) or 0), _text(row.get("started_at")), _text(row.get("completed_at")), _text(row.get("updated_at"))))
        connection.commit()


def load_extraction_results(database_path: str | Path | None, record_id: str = "") -> list[dict[str, Any]]:
    del database_path
    initialize_database()
    sql = "SELECT * FROM ai_extraction_results"
    args: tuple[object, ...] = ()
    if record_id:
        sql += " WHERE record_id=%s"
        args = (record_id,)
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
    return [{key: (_text(value) if key != "source_row_no" and key != "attempt_count" else int(value or 0)) for key, value in row.items() if key != "mysql_updated_at"} for row in rows]


def clear_extraction_results(database_path: str | Path | None, record_ids: list[str]) -> None:
    del database_path
    if not record_ids:
        return
    initialize_database()
    placeholders = ",".join(["%s"] * len(record_ids))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM ai_extraction_results WHERE record_id IN ({placeholders})", record_ids)
        connection.commit()


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
            record_ids = [_text(row.get("record_id")) for row in rows if row.get("record_id")]
            operation_rows: list[dict[str, Any]] = []
            if record_ids:
                placeholders = ",".join(["%s"] * len(record_ids))
                cursor.execute(
                    f"SELECT record_id, row_json FROM report_rows WHERE module_name='operations' AND record_id IN ({placeholders})",
                    record_ids,
                )
                operation_rows = cursor.fetchall()
    operation_stats = _operation_hour_summary(operation_rows)
    for row in rows:
        values = operation_stats.get(_text(row.get("record_id")), {})
        row["p_hours"] = round(float(values.get("p_hours", 0.0)), 2)
        row["sc_hours"] = round(float(values.get("sc_hours", 0.0)), 2)
        row["npt_hours"] = round(float(values.get("npt_hours", 0.0)), 2)
    return [_record_to_public(row) for row in rows]


def list_ai_job_status(kind: str) -> list[dict[str, str]]:
    if kind not in {"translation", "extraction"}:
        raise ValueError("Unsupported AI job kind")
    prefix = "translation" if kind == "translation" else "extraction"
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT record_id,
                       {prefix}_status AS status,
                       {prefix}_progress AS progress,
                       {prefix}_error AS error,
                       {prefix}_updated_at AS updated_at
                FROM report_records
                ORDER BY report_date DESC, updated_at DESC
                """
            )
            rows = cursor.fetchall()
    return [{key: _text(value) for key, value in row.items()} for row in rows]


def list_translation_queue_records() -> list[dict[str, str]]:
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT record_id, report_type, report_date AS reportDate, report_no AS reportNo,
                       wellbore, rig, translation_status, translation_progress,
                       translation_error, translation_version, translation_updated_at
                FROM report_records
                ORDER BY report_date DESC, updated_at DESC
                """
            )
            rows = cursor.fetchall()
    return [{key: _text(value) for key, value in row.items()} for row in rows]


def query_records(**filters: str) -> list[dict[str, str]]:
    return list_records(None, **filters)


def list_npt_confirmation_wells(
    database_path: str | Path | None,
    *,
    rig: str = "",
    wellbore: str = "",
    status: str = "",
    scope_rig: str = "",
) -> dict[str, Any]:
    del database_path
    records = _npt_candidate_records(rig=rig, wellbore=wellbore, scope_rig=scope_rig)
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        operations = record.pop("operations", [])
        has_non_p = any(_system_type(row) in {"SC", "NPT"} for row in operations)
        if not has_non_p:
            continue
        record_rig = str(record.get("rig", "") or "")
        record_well = str(record.get("wellbore", "") or "")
        if not record_well:
            continue
        key = (record_rig, record_well)
        item = groups.setdefault(key, {
            "rig": record_rig,
            "wellbore": record_well,
            "start_date": record.get("reportDate", ""),
            "end_date": record.get("reportDate", ""),
            "record_ids": [],
            "statuses": [],
            "locked_count": 0,
            "row_count": 0,
            "sc_hours": 0.0,
            "npt_hours": 0.0,
        })
        date_value = str(record.get("reportDate", "") or "")
        if date_value:
            item["start_date"] = min(str(item["start_date"] or date_value), date_value)
            item["end_date"] = max(str(item["end_date"] or date_value), date_value)
        item["record_ids"].append(str(record.get("record_id", "") or ""))
        item["statuses"].append(str(record.get("confirmation_status", "") or "pending"))
        if _truthy(record.get("locked")):
            item["locked_count"] += 1
        for row in operations:
            op_type = _system_type(row)
            hours = _safe_float(row.get("hours"))
            item["row_count"] += 1
            if op_type == "SC":
                item["sc_hours"] += hours
            elif op_type == "NPT":
                item["npt_hours"] += hours
    items = []
    for item in groups.values():
        item_status = _confirmation_group_status(item)
        if status and item_status != status:
            continue
        items.append({
            "wellbore": item["wellbore"],
            "rig": item["rig"],
            "start_date": item["start_date"],
            "end_date": item["end_date"],
            "status": item_status,
            "record_count": len(item["record_ids"]),
            "row_count": item["row_count"],
            "sc_hours": round(float(item["sc_hours"]), 2),
            "npt_hours": round(float(item["npt_hours"]), 2),
        })
    items.sort(key=lambda row: (str(row["status"] != "pending"), str(row["end_date"])), reverse=False)
    rigs = sorted({str(record.get("rig", "") or "") for record in records if record.get("rig")})
    return {"items": items, "filters": {"rigs": rigs, "statuses": _npt_statuses()}}


def load_npt_confirmation_detail(
    database_path: str | Path | None,
    wellbore: str,
    *,
    rig: str = "",
    scope_rig: str = "",
) -> dict[str, Any]:
    del database_path
    records = _npt_candidate_records(rig=rig, wellbore=wellbore, scope_rig=scope_rig, exact_wellbore=True)
    if not records:
        raise KeyError(wellbore)
    relevant_records = [
        record for record in records
        if any(_system_type(row) in {"SC", "NPT"} for row in record.get("operations", []))
    ]
    if not relevant_records:
        raise KeyError(wellbore)
    rows: list[dict[str, Any]] = []
    for record in sorted(relevant_records, key=lambda item: str(item.get("reportDate", "") or "")):
        for row in record.get("operations", []):
            system_type = _system_type(row)
            confirmed_type = str(row.get("confirmed_op_type", "") or row.get("op_type", "") or system_type).strip().upper()
            rows.append({
                "record_id": record.get("record_id", ""),
                "report_type": record.get("report_type", ""),
                "reportDate": record.get("reportDate", ""),
                "row_no": row.get("row_no", ""),
                "from": row.get("from", ""),
                "to": row.get("to", ""),
                "hours": row.get("hours", ""),
                "op_code": row.get("op_code", ""),
                "op_sub": row.get("op_sub", ""),
                "operation_details": row.get("operation_details", ""),
                "system_op_type": system_type,
                "confirmed_op_type": str(row.get("draft_op_type", "") or confirmed_type).strip().upper(),
                "row_revision": _npt_row_revision(row),
            })
    dates = [str(record.get("reportDate", "") or "") for record in relevant_records if record.get("reportDate")]
    meta = {
        "wellbore": wellbore,
        "rig": rig or str(relevant_records[0].get("rig", "") or ""),
        "start_date": min(dates) if dates else "",
        "end_date": max(dates) if dates else "",
        "status": _confirmation_group_status({
            "record_ids": [record.get("record_id", "") for record in relevant_records],
            "statuses": [str(record.get("confirmation_status", "") or "pending") for record in relevant_records],
            "locked_count": sum(1 for record in relevant_records if _truthy(record.get("locked"))),
        }),
        "record_count": len(relevant_records),
        "locked": all(_truthy(record.get("locked")) for record in relevant_records),
        "confirmation_note": next((str(record.get("confirmation_note", "") or "") for record in relevant_records if record.get("confirmation_note")), ""),
    }
    return {"meta": meta, "operations": rows}


def save_npt_confirmation(
    database_path: str | Path | None,
    wellbore: str,
    operations: list[dict[str, Any]],
    *,
    rig: str = "",
    note: str = "",
    confirmed_by: str = "",
    submit: bool = False,
) -> dict[str, Any]:
    del database_path
    detail = load_npt_confirmation_detail(None, wellbore, rig=rig)
    if detail["meta"].get("locked"):
        raise PermissionError(f"Well is locked after NPT confirmation: {wellbore}")
    allowed_record_ids = {str(row.get("record_id", "") or "") for row in detail["operations"]}
    updates: dict[tuple[str, int], str] = {}
    revisions: dict[tuple[str, int], str] = {}
    for row in operations:
        record_id = str(row.get("record_id", "") or "")
        if record_id not in allowed_record_ids:
            continue
        try:
            row_no = int(str(row.get("row_no", "") or "0"))
        except ValueError:
            row_no = 0
        confirmed_type = str(row.get("confirmed_op_type", "") or "").strip().upper()
        if confirmed_type in {"P", "SC", "NPT"} and row_no > 0:
            updates[(record_id, row_no)] = confirmed_type
            revisions[(record_id, row_no)] = str(row.get("row_revision", "") or "")
    if not updates:
        raise ValueError("No valid NPT confirmation rows.")
    touched_ids: set[str] = set()
    now = _now()
    with _connect() as connection:
        with connection.cursor() as cursor:
            record_ids = sorted(allowed_record_ids)
            placeholders = ",".join(["%s"] * len(record_ids))
            cursor.execute(
                f"SELECT record_id, locked FROM report_records WHERE record_id IN ({placeholders}) FOR UPDATE",
                record_ids,
            )
            locked_records = [
                _text(row.get("record_id"))
                for row in cursor.fetchall()
                if _truthy(row.get("locked"))
            ]
            if locked_records:
                raise PermissionError(f"Report is locked after NPT confirmation: {locked_records[0]}")
            for (record_id, row_no), confirmed_type in updates.items():
                cursor.execute(
                    """
                    SELECT row_json
                    FROM report_rows
                    WHERE record_id=%s AND module_name='operations' AND row_no=%s
                    """,
                    (record_id, row_no),
                )
                row = cursor.fetchone()
                if not row:
                    continue
                row_json = _json_loads(row.get("row_json"), {})
                expected_revision = revisions.get((record_id, row_no), "")
                if expected_revision and expected_revision != _npt_row_revision(row_json):
                    raise RuntimeError("NPT operation changed after it was loaded; refresh and try again.")
                current_type = str(row_json.get("op_type", "") or "").strip().upper()
                row_json.setdefault("system_op_type", current_type)
                if submit:
                    row_json["confirmed_op_type"] = confirmed_type
                    row_json["op_type"] = confirmed_type
                    row_json.pop("draft_op_type", None)
                else:
                    row_json["draft_op_type"] = confirmed_type
                cursor.execute(
                    """
                    UPDATE report_rows
                    SET row_json=%s
                    WHERE record_id=%s AND module_name='operations' AND row_no=%s
                    """,
                    (_json_dumps(row_json), record_id, row_no),
                )
                touched_ids.add(record_id)
            for record_id in allowed_record_ids:
                if submit:
                    cursor.execute(
                        """
                        UPDATE report_records
                        SET confirmation_status='confirmed', confirmation_note=%s, updated_at=%s,
                            locked='yes', confirmed_at=%s, confirmed_by=%s
                        WHERE record_id=%s
                        """,
                        (_text(note), now, now, _text(confirmed_by), record_id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE report_records
                        SET confirmation_status='draft', confirmation_note=%s, updated_at=%s
                        WHERE record_id=%s
                        """,
                        (_text(note), now, record_id),
                    )
        connection.commit()
    return {"wellbore": wellbore, "updated_records": len(touched_ids), "status": "confirmed" if submit else "draft", "locked": submit, "updated_at": now}


def is_available() -> bool:
    try:
        with _connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        return True
    except Exception:
        return False


def _connect(*, use_database: bool = True):
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
        database=settings.database if use_database else None,
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
        "source_language",
        "translation_status",
        "translation_progress",
        "translation_error",
        "translation_version",
        "translation_updated_at",
        "extraction_status", "extraction_progress", "extraction_error", "extraction_version", "extraction_updated_at",
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
    immutable_after_insert = {
        "record_id",
        "locked",
        "confirmation_status",
        "confirmed_at",
        "confirmed_by",
        "confirmation_note",
    }
    update_clause = ", ".join(
        f"{column}=VALUES({column})"
        for column in columns
        if column not in immutable_after_insert
    )
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
        "source_language": metadata.get("source_language", ""),
        "translation_status": metadata.get("translation_status", ""),
        "translation_progress": metadata.get("translation_progress", ""),
        "translation_error": metadata.get("translation_error", ""),
        "translation_version": metadata.get("translation_version", ""),
        "translation_updated_at": metadata.get("translation_updated_at", ""),
        "extraction_status": metadata.get("extraction_status", ""),
        "extraction_progress": metadata.get("extraction_progress", ""),
        "extraction_error": metadata.get("extraction_error", ""),
        "extraction_version": metadata.get("extraction_version", ""),
        "extraction_updated_at": metadata.get("extraction_updated_at", ""),
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
        "source_language": _text(row.get("source_language")),
        "translation_status": _text(row.get("translation_status")),
        "translation_progress": _text(row.get("translation_progress")),
        "translation_error": _text(row.get("translation_error")),
        "translation_version": _text(row.get("translation_version")),
        "translation_updated_at": _text(row.get("translation_updated_at")),
        "extraction_status": _text(row.get("extraction_status")),
        "extraction_progress": _text(row.get("extraction_progress")),
        "extraction_error": _text(row.get("extraction_error")),
        "extraction_version": _text(row.get("extraction_version")),
        "extraction_updated_at": _text(row.get("extraction_updated_at")),
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
        "p_hours": _text(row.get("p_hours")),
        "sc_hours": _text(row.get("sc_hours")),
        "npt_hours": _text(row.get("npt_hours")),
    }


def _payload_metadata(row: dict[str, Any]) -> dict[str, str]:
    return {
        "record_id": _text(row.get("record_id")),
        "report_type": _text(row.get("report_type")),
        "source_file": _text(row.get("source_file")),
        "parser": _text(row.get("parser")),
        "source_language": _text(row.get("source_language")),
        "translation_status": _text(row.get("translation_status")),
        "translation_progress": _text(row.get("translation_progress")),
        "translation_error": _text(row.get("translation_error")),
        "translation_version": _text(row.get("translation_version")),
        "translation_updated_at": _text(row.get("translation_updated_at")),
        "extraction_status": _text(row.get("extraction_status")),
        "extraction_progress": _text(row.get("extraction_progress")),
        "extraction_error": _text(row.get("extraction_error")),
        "extraction_version": _text(row.get("extraction_version")),
        "extraction_updated_at": _text(row.get("extraction_updated_at")),
        "locked": _text(row.get("locked")),
        "confirmation_status": _text(row.get("confirmation_status")),
        "confirmed_at": _text(row.get("confirmed_at")),
        "confirmed_by": _text(row.get("confirmed_by")),
        "confirmation_note": _text(row.get("confirmation_note")),
    }


def _npt_candidate_records(
    *,
    rig: str = "",
    wellbore: str = "",
    scope_rig: str = "",
    exact_wellbore: bool = False,
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    args: list[object] = []
    if scope_rig:
        clauses.append("r.rig=%s")
        args.append(scope_rig)
    if rig:
        clauses.append("r.rig=%s")
        args.append(rig)
    if wellbore:
        if exact_wellbore:
            clauses.append("r.wellbore=%s")
            args.append(wellbore)
        else:
            clauses.append("LOWER(r.wellbore) LIKE %s")
            args.append(f"%{wellbore.lower()}%")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
        SELECT
          r.record_id, r.report_type, r.report_date, r.wellbore, r.rig, r.locked,
          r.confirmation_status, r.confirmation_note, rr.row_no, rr.row_json
        FROM report_records r
        LEFT JOIN report_rows rr
          ON rr.record_id = r.record_id AND rr.module_name = 'operations'
        {where_sql}
        ORDER BY r.report_date, r.record_id, rr.row_no
    """
    grouped: dict[str, dict[str, Any]] = {}
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
    for row in rows:
        record_id = _text(row.get("record_id"))
        if not record_id:
            continue
        record = grouped.setdefault(record_id, {
            "record_id": record_id,
            "report_type": _text(row.get("report_type")),
            "reportDate": _text(row.get("report_date")),
            "wellbore": _text(row.get("wellbore")),
            "rig": _text(row.get("rig")),
            "locked": _text(row.get("locked")),
            "confirmation_status": _text(row.get("confirmation_status")),
            "confirmation_note": _text(row.get("confirmation_note")),
            "operations": [],
        })
        row_json = _json_loads(row.get("row_json"), {})
        if not row_json:
            continue
        row_json["row_no"] = _text(row.get("row_no"))
        record["operations"].append(row_json)
    return list(grouped.values())


def _safe_float(value: Any) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def _npt_row_revision(row: dict[str, Any]) -> str:
    persisted = {key: value for key, value in row.items() if key != "row_no"}
    value = json.dumps(persisted, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _operation_hour_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for row in rows:
        record_id = _text(row.get("record_id"))
        if not record_id:
            continue
        values = stats.setdefault(record_id, {"p_hours": 0.0, "sc_hours": 0.0, "npt_hours": 0.0})
        operation = _json_loads(row.get("row_json"), {})
        op_type = str(operation.get("confirmed_op_type", "") or operation.get("op_type", "") or operation.get("system_op_type", "")).strip().upper()
        key = {"P": "p_hours", "SC": "sc_hours", "NPT": "npt_hours"}.get(op_type)
        if key:
            values[key] += _safe_float(operation.get("hours"))
    return {
        record_id: {key: round(value, 2) for key, value in values.items()}
        for record_id, values in stats.items()
    }


def _system_type(row: dict[str, Any]) -> str:
    return str(row.get("system_op_type", "") or row.get("op_type", "") or "").strip().upper()


def _npt_statuses() -> list[dict[str, str]]:
    return [
        {"value": "pending", "label": "待确认"},
        {"value": "draft", "label": "确认中"},
        {"value": "confirmed", "label": "已确认"},
    ]


def _confirmation_group_status(item: dict[str, Any]) -> str:
    statuses = {str(value or "").strip().lower() for value in item.get("statuses", []) if str(value or "").strip()}
    record_count = len(item.get("record_ids", []) or [])
    locked_count = int(item.get("locked_count", 0) or 0)
    if record_count and locked_count >= record_count:
        return "confirmed"
    if "confirmed" in statuses and record_count and locked_count >= record_count:
        return "confirmed"
    if "draft" in statuses or "confirmed" in statuses:
        return "draft"
    return "pending"


def _sql_statements(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [statement.strip() for statement in text.split(";") if statement.strip()]


def _server_scope_statement(statement: str) -> bool:
    normalized = " ".join(statement.strip().lower().split())
    return normalized.startswith("create database ") or normalized.startswith("use ")


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
