from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from . import excel_database
from .db_config import mysql_settings


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCEL_PATH = ROOT / "outputs" / "report_database.xlsx"
_mysql_disabled_until = 0.0
_last_mysql_error = ""


def initialize_database(database_path: str | Path = DEFAULT_EXCEL_PATH) -> Path:
    path = excel_database.initialize_database(database_path)
    if _should_try_mysql(database_path):
        try:
            from . import mysql_database

            mysql_database.initialize_database()
        except Exception as exc:
            _mark_mysql_failure(exc)
    return path


def save_report_payload(
    database_path: str | Path,
    payload: dict[str, Any],
    report_type: str,
    *,
    source_file: str = "",
) -> dict[str, Any]:
    excel_result = excel_database.save_report_payload(database_path, payload, report_type, source_file=source_file)
    metadata = payload.setdefault("metadata", {})
    if isinstance(metadata, dict):
        metadata.update(excel_result)
    if _should_try_mysql(database_path):
        try:
            from . import mysql_database

            mysql_database.save_report_payload(database_path, payload, report_type, source_file=source_file)
        except Exception as exc:
            _mark_mysql_failure(exc)
    return excel_result


def load_report_payload(database_path: str | Path, record_id: str) -> dict[str, Any]:
    if _should_try_mysql(database_path):
        try:
            from . import mysql_database

            return mysql_database.load_report_payload(database_path, record_id)
        except Exception as exc:
            _mark_mysql_failure(exc)
    return excel_database.load_report_payload(database_path, record_id)


def save_translation_content(database_path: str | Path, record_id: str, rows: list[dict[str, Any]]) -> None:
    excel_database.save_translation_content(database_path, record_id, rows)
    if _should_try_mysql(database_path):
        try:
            from . import mysql_database

            mysql_database.save_translation_content(database_path, record_id, rows)
        except Exception as exc:
            _mark_mysql_failure(exc)


def load_translation_content(database_path: str | Path, record_id: str) -> list[dict[str, str]]:
    if _should_try_mysql(database_path):
        try:
            from . import mysql_database

            return mysql_database.load_translation_content(database_path, record_id)
        except Exception as exc:
            _mark_mysql_failure(exc)
    return excel_database.load_translation_content(database_path, record_id)


def clear_translation_content(database_path: str | Path, record_id: str = "") -> None:
    excel_database.clear_translation_content(database_path, record_id)
    if _should_try_mysql(database_path):
        try:
            from . import mysql_database

            mysql_database.clear_translation_content(database_path, record_id)
        except Exception as exc:
            _mark_mysql_failure(exc)


def update_record_translation_status(
    database_path: str | Path,
    record_id: str,
    *,
    status: str,
    progress: int | str = "",
    error: str = "",
    version: str = "",
) -> None:
    excel_database.update_record_translation_status(
        database_path,
        record_id,
        status=status,
        progress=progress,
        error=error,
        version=version,
    )
    if _should_try_mysql(database_path):
        try:
            from . import mysql_database

            mysql_database.update_record_translation_status(
                database_path,
                record_id,
                status=status,
                progress=progress,
                error=error,
                version=version,
            )
        except Exception as exc:
            _mark_mysql_failure(exc)


def delete_report_payload(database_path: str | Path, record_id: str) -> bool:
    deleted = excel_database.delete_report_payload(database_path, record_id)
    if _should_try_mysql(database_path):
        try:
            from . import mysql_database

            mysql_deleted = mysql_database.delete_report_payload(database_path, record_id)
            deleted = deleted or mysql_deleted
        except Exception as exc:
            _mark_mysql_failure(exc)
    return deleted


def list_records(
    database_path: str | Path,
    *,
    report_type: str = "",
    wellbore: str = "",
    date: str = "",
    date_from: str = "",
    date_to: str = "",
) -> list[dict[str, str]]:
    if _should_try_mysql(database_path):
        try:
            from . import mysql_database

            return mysql_database.list_records(
                database_path,
                report_type=report_type,
                wellbore=wellbore,
                date=date,
                date_from=date_from,
                date_to=date_to,
            )
        except Exception as exc:
            _mark_mysql_failure(exc)
    records = excel_database.list_records(database_path)
    return _filter_records(records, report_type=report_type, wellbore=wellbore, date=date, date_from=date_from, date_to=date_to)


def mysql_status() -> dict[str, object]:
    settings = mysql_settings()
    status = {"enabled": settings.enabled, "available": False, "error": _last_mysql_error}
    if not settings.enabled:
        return status
    try:
        from . import mysql_database

        status["available"] = mysql_database.is_available()
        if status["available"]:
            status["error"] = ""
    except Exception as exc:
        status["error"] = str(exc)
    return status


def _filter_records(
    records: list[dict[str, str]],
    *,
    report_type: str = "",
    wellbore: str = "",
    date: str = "",
    date_from: str = "",
    date_to: str = "",
) -> list[dict[str, str]]:
    result = []
    for record in records:
        report_date = str(record.get("reportDate", "") or "")
        if report_type and record.get("report_type") != report_type:
            continue
        if wellbore and record.get("wellbore") != wellbore:
            continue
        if date and report_date != date:
            continue
        if date_from and report_date < date_from:
            continue
        if date_to and report_date > date_to:
            continue
        result.append(record)
    return result


def _should_try_mysql(database_path: str | Path) -> bool:
    settings = mysql_settings()
    if not settings.enabled:
        return False
    if time.monotonic() < _mysql_disabled_until:
        return False
    try:
        path = Path(database_path).resolve()
    except (OSError, TypeError):
        path = DEFAULT_EXCEL_PATH.resolve()
    return path == DEFAULT_EXCEL_PATH.resolve()


def _mark_mysql_failure(exc: Exception) -> None:
    global _mysql_disabled_until, _last_mysql_error
    settings = mysql_settings()
    _last_mysql_error = str(exc)
    _mysql_disabled_until = time.monotonic() + max(1, settings.retry_seconds)
