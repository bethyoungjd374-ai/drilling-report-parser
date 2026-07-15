"""Dual-write normalized report facts while preserving the original report payload."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Any

from .master_data_service import resolve_master_id, resolve_project_assignment
from .time_classification_service import upsert_activity_classification


def synchronize_saved_report(
    cursor: Any,
    *,
    record_id: str,
    report_type: str,
    fields: dict[str, Any],
    operations: list[dict[str, Any]],
    actor: str = "system",
) -> dict[str, Any]:
    report_date = str(fields.get("reportDate", "") or "").strip()
    rig_id = resolve_master_id(cursor, "rig", fields.get("rig"))
    wellbore_id = resolve_master_id(cursor, "wellbore", fields.get("wellbore"))
    explicit_job_id = _positive_int(fields.get("jobId") or fields.get("job_id"))
    resolution = resolve_project_assignment(
        cursor,
        report_date=report_date,
        report_type=report_type,
        rig_id=rig_id,
        wellbore_id=wellbore_id,
        explicit_job_id=explicit_job_id,
    )
    match_status = str(resolution.get("status", "UNASSIGNED") or "UNASSIGNED")
    match_message = str(resolution.get("message", "") or "")
    project_id = _positive_int(resolution.get("project_id"))
    job_id = _positive_int(resolution.get("job_id"))
    normalization_status = "NORMALIZED" if rig_id and wellbore_id else "NORMALIZATION_FAILED"

    cursor.execute(
        """
        UPDATE report_records
        SET rig_id=%s, wellbore_id=%s, project_id=%s, job_id=%s,
            master_match_status=%s, master_match_message=%s
        WHERE record_id=%s
        """,
        (rig_id, wellbore_id, project_id, job_id, match_status, match_message, record_id),
    )
    cursor.execute(
        """
        INSERT INTO fact_daily_report
          (record_id, report_date, report_type, project_id, job_id, rig_id, wellbore_id,
           match_status, match_message, normalization_status, source_version, created_by, updated_by)
        VALUES (%s,NULLIF(%s,''),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          report_date=VALUES(report_date), report_type=VALUES(report_type),
          project_id=VALUES(project_id), job_id=VALUES(job_id), rig_id=VALUES(rig_id),
          wellbore_id=VALUES(wellbore_id), match_status=VALUES(match_status),
          match_message=VALUES(match_message), normalization_status=VALUES(normalization_status),
          source_version=VALUES(source_version), updated_by=VALUES(updated_by), version=version+1
        """,
        (
            record_id,
            report_date,
            report_type,
            project_id,
            job_id,
            rig_id,
            wellbore_id,
            match_status,
            match_message,
            normalization_status,
            _source_version(fields, operations),
            actor,
            actor,
        ),
    )
    cursor.execute("SELECT id FROM fact_daily_report WHERE record_id=%s", (record_id,))
    daily_report_id = int((cursor.fetchone() or {})["id"])

    source_rows: set[int] = set()
    pending_classifications = 0
    total_hours = 0.0
    for row_no, row in enumerate(operations, start=1):
        if not isinstance(row, dict):
            continue
        source_rows.add(row_no)
        hours = _safe_float(row.get("hours"))
        total_hours += hours
        source_hash = _activity_hash(row)
        cursor.execute(
            """
            INSERT INTO fact_activity
              (daily_report_id, source_row_no, started_at, ended_at, hours, op_code, op_sub,
               source_op_type, operation_details, source_hash, created_by, updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
              started_at=VALUES(started_at), ended_at=VALUES(ended_at), hours=VALUES(hours),
              op_code=VALUES(op_code), op_sub=VALUES(op_sub), source_op_type=VALUES(source_op_type),
              operation_details=VALUES(operation_details), source_hash=VALUES(source_hash),
              updated_by=VALUES(updated_by), version=version+1
            """,
            (
                daily_report_id,
                row_no,
                _activity_datetime(report_date, row.get("from")),
                _activity_datetime(report_date, row.get("to")),
                hours,
                str(row.get("op_code", "") or ""),
                str(row.get("op_sub", "") or ""),
                str(row.get("confirmed_op_type", "") or row.get("op_type", "") or row.get("system_op_type", "") or "").upper(),
                str(row.get("operation_details", "") or ""),
                source_hash,
                actor,
                actor,
            ),
        )
        cursor.execute(
            "SELECT id FROM fact_activity WHERE daily_report_id=%s AND source_row_no=%s",
            (daily_report_id, row_no),
        )
        activity_id = int((cursor.fetchone() or {})["id"])
        classification = upsert_activity_classification(cursor, activity_id, row)
        if classification.get("confirmation_status") not in {"CONFIRMED", "AUTO_CONFIRMED"}:
            pending_classifications += 1

    if source_rows:
        placeholders = ",".join(["%s"] * len(source_rows))
        cursor.execute(
            f"DELETE FROM fact_activity WHERE daily_report_id=%s AND source_row_no NOT IN ({placeholders})",
            [daily_report_id, *sorted(source_rows)],
        )
    else:
        cursor.execute("DELETE FROM fact_activity WHERE daily_report_id=%s", (daily_report_id,))

    _refresh_quality_issues(
        cursor,
        record_id=record_id,
        report_type=report_type,
        rig_id=rig_id,
        wellbore_id=wellbore_id,
        resolution=resolution,
        total_hours=total_hours,
        activity_count=len(source_rows),
        pending_classifications=pending_classifications,
        actor=actor,
    )
    if job_id:
        if rig_id:
            _sync_job_rig_assignment(cursor, job_id=job_id, rig_id=rig_id, report_date=report_date, actor=actor)
        _sync_job_events(cursor, job_id=job_id, record_id=record_id, report_type=report_type, report_date=report_date, fields=fields, actor=actor)
        _sync_depth_progress(cursor, job_id=job_id, record_id=record_id, report_date=report_date, fields=fields, actor=actor)
        _sync_incident(cursor, job_id=job_id, record_id=record_id, report_date=report_date, fields=fields, actor=actor)
    return {
        "record_id": record_id,
        "rig_id": rig_id,
        "wellbore_id": wellbore_id,
        "project_id": project_id,
        "job_id": job_id,
        "match_status": match_status,
        "normalization_status": normalization_status,
        "activity_count": len(source_rows),
        "pending_classifications": pending_classifications,
        "total_hours": round(total_hours, 3),
    }


def list_quality_issues(*, status: str = "OPEN", issue_type: str = "", limit: int = 1000) -> list[dict[str, Any]]:
    clauses: list[str] = []
    args: list[object] = []
    if status:
        clauses.append("status=%s")
        args.append(status)
    if issue_type:
        clauses.append("issue_type=%s")
        args.append(issue_type)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    args.append(max(1, min(int(limit), 5000)))
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM data_quality_issue {where} ORDER BY severity DESC, updated_at DESC LIMIT %s",
                args,
            )
            rows = cursor.fetchall()
    return [_json_row(row) for row in rows]


def resolve_quality_issue(issue_id: int, *, note: str, actor: str, expected_version: int) -> dict[str, Any]:
    if not note.strip():
        raise ValueError("解决质量问题必须填写说明。")
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE data_quality_issue
                    SET status='RESOLVED', resolution_note=%s, resolved_at=NOW(), resolved_by=%s,
                        updated_by=%s, version=version+1
                    WHERE id=%s AND version=%s
                    """,
                    (note, actor, actor, issue_id, expected_version),
                )
                if cursor.rowcount != 1:
                    raise RuntimeError("质量问题已被其他用户修改，请刷新后重试。")
                cursor.execute("SELECT * FROM data_quality_issue WHERE id=%s", (issue_id,))
                row = cursor.fetchone()
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return _json_row(row or {})


def _refresh_quality_issues(
    cursor: Any,
    *,
    record_id: str,
    report_type: str,
    rig_id: int | None,
    wellbore_id: int | None,
    resolution: dict[str, Any],
    total_hours: float,
    activity_count: int,
    pending_classifications: int,
    actor: str,
) -> None:
    cursor.execute(
        """
        UPDATE data_quality_issue
        SET status='RESOLVED', resolution_note='自动复检已通过', resolved_at=NOW(),
            resolved_by='system', updated_by='system', version=version+1
        WHERE record_id=%s AND status='OPEN'
        """,
        (record_id,),
    )
    if not rig_id:
        _upsert_issue(cursor, record_id, "MASTER_RIG_UNRESOLVED", "error", {"message": "井队未匹配主数据"}, actor)
    if not wellbore_id:
        _upsert_issue(cursor, record_id, "MASTER_WELLBORE_UNRESOLVED", "error", {"message": "井筒未匹配主数据"}, actor)
    status = str(resolution.get("status", "") or "")
    if status in {"UNASSIGNED", "AMBIGUOUS"}:
        _upsert_issue(
            cursor,
            record_id,
            f"PROJECT_{status}",
            "error",
            {"message": resolution.get("message", ""), "matches": resolution.get("matches", [])},
            actor,
        )
    if activity_count and abs(total_hours - 24.0) > 0.01:
        _upsert_issue(
            cursor,
            record_id,
            "HOURS_NOT_24",
            "warning",
            {"total_hours": round(total_hours, 3), "difference": round(total_hours - 24.0, 3), "report_type": report_type},
            actor,
        )
    if pending_classifications:
        _upsert_issue(
            cursor,
            record_id,
            "CLASSIFICATION_PENDING",
            "warning",
            {"pending_count": pending_classifications},
            actor,
        )


def _upsert_issue(
    cursor: Any,
    record_id: str,
    issue_type: str,
    severity: str,
    details: dict[str, Any],
    actor: str,
) -> None:
    issue_key = f"{record_id}:{issue_type}"
    cursor.execute(
        """
        INSERT INTO data_quality_issue
          (issue_key, issue_type, severity, entity_type, entity_id, record_id,
           details_json, status, created_by, updated_by)
        VALUES (%s,%s,%s,'report',%s,%s,%s,'OPEN',%s,%s)
        ON DUPLICATE KEY UPDATE
          severity=VALUES(severity), details_json=VALUES(details_json), status='OPEN',
          resolution_note='', resolved_at=NULL, resolved_by='', updated_by=VALUES(updated_by),
          version=version+1
        """,
        (issue_key, issue_type, severity, record_id, record_id, json.dumps(details, ensure_ascii=False), actor, actor),
    )


def _sync_depth_progress(
    cursor: Any,
    *,
    job_id: int,
    record_id: str,
    report_date: str,
    fields: dict[str, Any],
    actor: str,
) -> None:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", report_date or ""):
        return
    measured_depth = _nullable_float(fields.get("todayMd"))
    daily_progress = _nullable_float(fields.get("progress"))
    if measured_depth is None and daily_progress is None:
        return
    cursor.execute(
        """
        INSERT INTO fact_depth_progress
          (job_id, record_id, progress_date, measured_depth_ft, daily_progress_ft,
           source_field, created_by, updated_by)
        VALUES (%s,%s,%s,%s,%s,'report_fields',%s,%s)
        ON DUPLICATE KEY UPDATE
          measured_depth_ft=VALUES(measured_depth_ft), daily_progress_ft=VALUES(daily_progress_ft),
          updated_by=VALUES(updated_by), version=version+1
        """,
        (job_id, record_id, report_date, measured_depth, daily_progress, actor, actor),
    )


def _sync_job_rig_assignment(
    cursor: Any,
    *,
    job_id: int,
    rig_id: int,
    report_date: str,
    actor: str,
) -> None:
    try:
        start = datetime.strptime(report_date, "%Y-%m-%d")
    except ValueError:
        return
    end = start + timedelta(days=1)
    cursor.execute(
        "SELECT * FROM rel_job_rig_assignment WHERE job_id=%s AND rig_id=%s AND status='active' "
        "AND valid_from <= %s AND COALESCE(valid_to,'9999-12-31 23:59:59') >= %s ORDER BY valid_from LIMIT 1",
        (job_id, rig_id, end, start),
    )
    existing = cursor.fetchone()
    if existing:
        current_start = existing["valid_from"]
        current_end = existing.get("valid_to")
        cursor.execute(
            "UPDATE rel_job_rig_assignment SET valid_from=%s,valid_to=%s,updated_by=%s,version=version+1 WHERE id=%s",
            (min(current_start, start), max(current_end, end) if current_end else None, actor, existing["id"]),
        )
        return
    cursor.execute(
        "INSERT INTO rel_job_rig_assignment "
        "(job_id,rig_id,valid_from,valid_to,status,change_reason,created_by,updated_by) "
        "VALUES (%s,%s,%s,%s,'active','由标准日报自动建立',%s,%s)",
        (job_id, rig_id, start, end, actor, actor),
    )


def _sync_job_events(
    cursor: Any,
    *,
    job_id: int,
    record_id: str,
    report_type: str,
    report_date: str,
    fields: dict[str, Any],
    actor: str,
) -> None:
    event_types = {
        "drilling": ("DRILLING_START", "DRILLING_END"),
        "workover": ("WORKOVER_START", "WORKOVER_END"),
        "completion": ("COMPLETION_START", "COMPLETION_END"),
        "move": ("MOVE_START", "MOVE_END"),
    }
    start_type, end_type = event_types.get(report_type, ("JOB_START", "JOB_END"))
    start_value = _first_date(fields, "operationStartDate", "startDate", "spudDate", "moveStartDate")
    end_value = _first_date(fields, "operationEndDate", "endDate", "completionDate", "moveEndDate")
    for event_type, occurred_on in ((start_type, start_value), (end_type, end_value)):
        if not occurred_on:
            continue
        occurred_at = f"{occurred_on} 00:00:00"
        cursor.execute(
            "SELECT id FROM fact_job_event WHERE job_id=%s AND event_type=%s AND occurred_at=%s LIMIT 1",
            (job_id, event_type, occurred_at),
        )
        if cursor.fetchone():
            continue
        cursor.execute(
            "INSERT INTO fact_job_event "
            "(job_id,event_type,occurred_at,source_record_id,source_type,confirmation_status,note,created_by,updated_by) "
            "VALUES (%s,%s,%s,%s,'report','AUTO','从日报显式日期字段提取',%s,%s)",
            (job_id, event_type, occurred_at, record_id, actor, actor),
        )


def _first_date(fields: dict[str, Any], *names: str) -> str:
    for name in names:
        text = str(fields.get(name, "") or "").strip()[:10]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return text
    return ""


def _sync_incident(
    cursor: Any,
    *,
    job_id: int,
    record_id: str,
    report_date: str,
    fields: dict[str, Any],
    actor: str,
) -> None:
    description = str(fields.get("incidentComments", "") or fields.get("safetyComments", "") or "").strip()
    incident_flag = str(fields.get("safetyIncident", "") or "").strip().lower()
    if not description and incident_flag not in {"yes", "true", "1", "是", "有"}:
        return
    cursor.execute("DELETE FROM fact_incident WHERE record_id=%s AND incident_type='SAFETY'", (record_id,))
    cursor.execute(
        """
        INSERT INTO fact_incident
          (job_id, record_id, incident_type, occurred_at, description,
           confirmation_status, created_by, updated_by)
        VALUES (%s,%s,'SAFETY',%s,%s,'PENDING',%s,%s)
        """,
        (job_id, record_id, f"{report_date} 00:00:00" if report_date else None, description, actor, actor),
    )


def _activity_datetime(report_date: str, value: object) -> str | None:
    text = str(value or "").strip()
    if not report_date or not text:
        return None
    if re.fullmatch(r"\d{1,2}:\d{2}", text):
        hour, minute = text.split(":", 1)
        return f"{report_date} {int(hour):02d}:{minute}:00"
    return None


def _source_version(fields: dict[str, Any], operations: list[dict[str, Any]]) -> str:
    raw = json.dumps({"fields": fields, "operations": operations}, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _activity_hash(row: dict[str, Any]) -> str:
    raw = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _positive_int(value: object) -> int | None:
    try:
        parsed = int(str(value or "0"))
        return parsed if parsed > 0 else None
    except ValueError:
        return None


def _safe_float(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def _nullable_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def _json_row(row: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat(sep=" ", timespec="seconds")
        elif hasattr(value, "isoformat"):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


def _db_connection():
    from .mysql_database import _connect, initialize_database

    initialize_database()
    return _connect()
