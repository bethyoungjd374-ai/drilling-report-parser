from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_LABEL = Path("mysql")
_last_mysql_error = ""


@contextmanager
def background_job_lock(kind: str, record_id: str):
    from . import mysql_database

    with mysql_database.background_job_lock(kind, record_id) as acquired:
        yield acquired


def initialize_database(database_path: str | Path | None = None) -> Path:
    _validate_mysql_label(database_path)
    from . import mysql_database

    mysql_database.initialize_database()
    _clear_mysql_failure()
    return DEFAULT_DATABASE_LABEL


def save_report_payload(
    database_path: str | Path,
    payload: dict[str, Any],
    report_type: str,
    *,
    source_file: str = "",
    invalidate_translations: bool = True,
) -> dict[str, Any]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    result = mysql_database.save_report_payload(
        None,
        payload,
        report_type,
        source_file=source_file,
        invalidate_translations=invalidate_translations,
    )
    metadata = payload.setdefault("metadata", {})
    if isinstance(metadata, dict):
        metadata.update(result)
    _clear_mysql_failure()
    return result


def load_report_payload(database_path: str | Path, record_id: str) -> dict[str, Any]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    payload = mysql_database.load_report_payload(None, record_id)
    _clear_mysql_failure()
    return payload


def load_report_payloads(
    database_path: str | Path,
    record_ids: list[str],
    *,
    include_translations: bool = False,
) -> dict[str, dict[str, Any]]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    payloads = mysql_database.load_report_payloads(
        None,
        record_ids,
        include_translations=include_translations,
    )
    _clear_mysql_failure()
    return payloads


def save_translation_content(database_path: str | Path, record_id: str, rows: list[dict[str, Any]]) -> None:
    _validate_mysql_label(database_path)
    from . import mysql_database

    mysql_database.save_translation_content(None, record_id, rows)
    _clear_mysql_failure()


def load_translation_content(database_path: str | Path, record_id: str) -> list[dict[str, str]]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    rows = mysql_database.load_translation_content(None, record_id)
    _clear_mysql_failure()
    return rows


def load_operation_translations(database_path: str | Path, record_ids: list[str]) -> list[dict[str, str]]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    rows = mysql_database.load_operation_translations(None, record_ids)
    _clear_mysql_failure()
    return rows


def clear_translation_content(database_path: str | Path, record_id: str = "") -> None:
    _validate_mysql_label(database_path)
    from . import mysql_database

    mysql_database.clear_translation_content(None, record_id)
    _clear_mysql_failure()


def reset_translation_state(database_path: str | Path, record_id: str = "") -> dict[str, int]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    result = mysql_database.reset_translation_state(None, record_id)
    _clear_mysql_failure()
    return result


def update_record_translation_status(
    database_path: str | Path,
    record_id: str,
    *,
    status: str,
    progress: int | str = "",
    error: str = "",
    version: str = "",
) -> None:
    _validate_mysql_label(database_path)
    from . import mysql_database

    mysql_database.update_record_translation_status(
        None,
        record_id,
        status=status,
        progress=progress,
        error=error,
        version=version,
    )
    _clear_mysql_failure()


def update_record_extraction_status(
    database_path: str | Path,
    record_id: str,
    *,
    status: str,
    progress: int | str = "",
    error: str = "",
    version: str = "",
) -> None:
    _validate_mysql_label(database_path)
    from . import mysql_database

    mysql_database.update_record_extraction_status(
        None,
        record_id,
        status=status,
        progress=progress,
        error=error,
        version=version,
    )
    _clear_mysql_failure()


def save_extraction_results(database_path: str | Path, rows: list[dict[str, Any]]) -> None:
    _validate_mysql_label(database_path)
    from . import mysql_database

    mysql_database.save_extraction_results(None, rows)
    _clear_mysql_failure()


def load_extraction_results(database_path: str | Path, record_id: str = "") -> list[dict[str, Any]]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    rows = mysql_database.load_extraction_results(None, record_id)
    _clear_mysql_failure()
    return rows


def clear_extraction_results(database_path: str | Path, record_ids: list[str]) -> None:
    _validate_mysql_label(database_path)
    from . import mysql_database

    mysql_database.clear_extraction_results(None, record_ids)
    _clear_mysql_failure()


def delete_report_payload(database_path: str | Path, record_id: str) -> bool:
    _validate_mysql_label(database_path)
    from . import mysql_database

    deleted = mysql_database.delete_report_payload(None, record_id)
    _clear_mysql_failure()
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
    _validate_mysql_label(database_path)
    from . import mysql_database

    records = mysql_database.list_records(
        None,
        report_type=report_type,
        wellbore=wellbore,
        date=date,
        date_from=date_from,
        date_to=date_to,
    )
    _clear_mysql_failure()
    return records


def list_npt_confirmation_wells(
    database_path: str | Path,
    *,
    rig: str = "",
    wellbore: str = "",
    status: str = "",
    scope_rig: str = "",
) -> dict[str, Any]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    payload = mysql_database.list_npt_confirmation_wells(
        None,
        rig=rig,
        wellbore=wellbore,
        status=status,
        scope_rig=scope_rig,
    )
    _clear_mysql_failure()
    return payload


def load_npt_confirmation_detail(
    database_path: str | Path,
    wellbore: str,
    *,
    rig: str = "",
    scope_rig: str = "",
) -> dict[str, Any]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    payload = mysql_database.load_npt_confirmation_detail(None, wellbore, rig=rig, scope_rig=scope_rig)
    _clear_mysql_failure()
    return payload


def save_npt_confirmation(
    database_path: str | Path,
    wellbore: str,
    operations: list[dict[str, Any]],
    *,
    rig: str = "",
    note: str = "",
    confirmed_by: str = "",
    submit: bool = False,
) -> dict[str, Any]:
    _validate_mysql_label(database_path)
    from . import mysql_database

    result = mysql_database.save_npt_confirmation(
        None,
        wellbore,
        operations,
        rig=rig,
        note=note,
        confirmed_by=confirmed_by,
        submit=submit,
    )
    _clear_mysql_failure()
    return result


def mysql_status() -> dict[str, object]:
    from .db_config import mysql_settings

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


def _validate_mysql_label(database_path: str | Path | None) -> None:
    if database_path is None:
        return
    if str(database_path).strip().lower() != str(DEFAULT_DATABASE_LABEL):
        raise ValueError("Only MySQL storage is supported; file database paths are not allowed.")


def _clear_mysql_failure() -> None:
    global _last_mysql_error
    _last_mysql_error = ""
