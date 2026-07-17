"""Rule-first, human-confirmed time classification for daily activities."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from typing import Any


CLASSIFICATION_FIELDS = (
    "productive_flag",
    "confirmed_op_type",
    "work_bucket",
    "billing_status",
    "responsibility",
    "cause_code",
    "service_line",
)


def current_rule_version(cursor: Any | None = None) -> str:
    if cursor is not None:
        cursor.execute(
            "SELECT rule_version AS version FROM dpr_operation_classification_rule "
            "WHERE status='active' ORDER BY updated_at DESC,id DESC LIMIT 1"
        )
        return str((cursor.fetchone() or {}).get("version", "") or "classification-v1")
    with _db_connection() as connection:
        with connection.cursor() as current:
            return current_rule_version(current)


def classify_activity(cursor: Any, row: dict[str, Any]) -> dict[str, Any]:
    op_code = str(row.get("op_code", "") or "").strip()
    op_sub = str(row.get("op_sub", "") or "").strip()
    details = str(row.get("operation_details", "") or "").strip()
    # The source value is immutable.  A later NPT review may create an effective
    # type, but it must never become the next normalization run's source value.
    source_type = str(
        row.get("source_op_type", "")
        or row.get("system_op_type", "")
        or row.get("op_type", "")
        or ""
    ).strip().upper()
    source_type = source_type if source_type in {"P", "SC", "NPT"} else ""
    cursor.execute(
        "SELECT * FROM dpr_operation_classification_rule WHERE status='active' ORDER BY priority, id"
    )
    matched: list[dict[str, Any]] = []
    for rule in cursor.fetchall():
        if _rule_matches(rule, op_code=op_code, op_sub=op_sub, details=details):
            matched.append(rule)
    if matched:
        best_specificity = min(
            0 if str(rule.get("op_code_pattern", "") or "").strip() or str(rule.get("op_sub_pattern", "") or "").strip() else 1
            for rule in matched
        )
        specific = [
            rule for rule in matched
            if (0 if str(rule.get("op_code_pattern", "") or "").strip() or str(rule.get("op_sub_pattern", "") or "").strip() else 1) == best_specificity
        ]
        best_priority = min(int(rule.get("priority", 100) or 100) for rule in specific)
        best = [rule for rule in specific if int(rule.get("priority", 100) or 100) == best_priority]
        outputs = [_classification_json(rule.get("classification_json")) for rule in best]
        signatures = {json.dumps(output, ensure_ascii=False, sort_keys=True) for output in outputs}
        if len(signatures) == 1:
            result = _complete_classification(outputs[0], source_type)
            if source_type in {"SC", "NPT"}:
                # Responsibility, standby/work bucket and billing are formal
                # business decisions made in the NPT confirmation workflow.
                # Rules may match the row, but may not make those decisions.
                result = _default_classification(source_type)
            result.update({
                "rule_id": int(best[0]["id"]),
                "rule_version": str(best[0].get("rule_version", "") or ""),
                # The source report's explicit P/SC/NPT value is authoritative.
                # A rule can enrich workload/billing/cause fields, but a rule-only
                # type remains pending until the missing source value is reviewed.
                "confirmation_status": "AUTO_CONFIRMED" if source_type == "P" else "PENDING",
                "confidence": 1.0 if source_type else 0.75,
            })
            return result
        return {
            **_default_classification(source_type),
            "rule_id": None,
            "rule_version": current_rule_version(cursor),
            "confirmation_status": "CONFLICT",
            "confidence": 0.0,
        }
    default = _default_classification(source_type)
    default.update({
        "rule_id": None,
        "rule_version": current_rule_version(cursor),
        "confirmation_status": "AUTO_CONFIRMED" if source_type == "P" else "PENDING",
        "confidence": 1.0 if source_type else 0.0,
    })
    return default


def upsert_activity_classification(cursor: Any, activity_id: int, row: dict[str, Any]) -> dict[str, Any]:
    classification = classify_activity(cursor, row)
    classification["productivity_type_code"] = classification.get("productive_flag", "")
    fields = ["productive_flag", "productivity_type_code", *CLASSIFICATION_FIELDS[1:], "rule_id", "rule_version", "confirmation_status", "confidence"]
    cursor.execute(
        f"""
        INSERT INTO dpr_operation_classification
          (activity_id, {', '.join(fields)}, created_by, updated_by)
        VALUES (%s, {', '.join(['%s'] * len(fields))}, 'system', 'system')
        ON DUPLICATE KEY UPDATE
          {', '.join(f"{field}=IF(confirmation_status='CONFIRMED',{field},VALUES({field}))" for field in fields)},
          updated_by=IF(confirmation_status='CONFIRMED',updated_by,'system'),
          version=IF(confirmation_status='CONFIRMED',version,version+1)
        """,
        [activity_id, *[classification.get(field) for field in fields]],
    )
    return classification


def list_rules(*, status: str = "", limit: int = 500) -> list[dict[str, Any]]:
    where = "WHERE status=%s" if status else ""
    args: list[object] = [status] if status else []
    args.append(max(1, min(int(limit), 2000)))
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM dpr_operation_classification_rule {where} ORDER BY priority, rule_code LIMIT %s",
                args,
            )
            rows = cursor.fetchall()
    return [_json_row(row) for row in rows]


def save_rule(payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
    rule_code = str(payload.get("rule_code", "") or "").strip()
    rule_name = str(payload.get("rule_name", "") or "").strip()
    if not rule_code or not rule_name:
        raise ValueError("rule_code 和 rule_name 不能为空。")
    classification = payload.get("classification")
    if not isinstance(classification, dict):
        classification = payload.get("classification_json")
    if isinstance(classification, str):
        classification = json.loads(classification)
    if not isinstance(classification, dict):
        raise ValueError("classification 必须是对象。")
    clean = {field: str(classification.get(field, "") or "").strip() for field in CLASSIFICATION_FIELDS}
    rule_version = str(payload.get("rule_version", "") or "").strip() or _new_rule_version(rule_code, payload, clean)
    values = {
        "rule_code": rule_code,
        "rule_name": rule_name,
        "priority": int(payload.get("priority", 100) or 100),
        "op_code_pattern": str(payload.get("op_code_pattern", "") or ""),
        "op_sub_pattern": str(payload.get("op_sub_pattern", "") or ""),
        "keyword_pattern": str(payload.get("keyword_pattern", "") or ""),
        "classification_json": json.dumps(clean, ensure_ascii=False),
        "rule_version": rule_version,
        "status": str(payload.get("status", "active") or "active"),
        "change_reason": str(payload.get("change_reason", "") or ""),
    }
    if not any(str(values[field] or "").strip() for field in ("op_code_pattern", "op_sub_pattern", "keyword_pattern")):
        raise ValueError("分类规则至少需要一个 OP CODE、OP SUB 或关键词匹配条件。")
    if not any(clean.values()):
        raise ValueError("分类规则至少需要设置一个分类结果字段。")
    if not str(values["change_reason"] or "").strip():
        raise ValueError("新增或修改分类规则必须填写变更原因。")
    for pattern_field in ("op_code_pattern", "op_sub_pattern", "keyword_pattern"):
        pattern = values[pattern_field]
        if pattern:
            re.compile(str(pattern), flags=re.I)
    rule_id = int(payload.get("id", 0) or 0)
    expected_version = int(payload.get("version", 0) or 0)
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                if rule_id:
                    if not expected_version:
                        raise ValueError("更新规则必须提供 version。")
                    cursor.execute(
                        """
                        UPDATE dpr_operation_classification_rule
                        SET rule_code=%s, rule_name=%s, priority=%s, op_code_pattern=%s,
                            op_sub_pattern=%s, keyword_pattern=%s, classification_json=%s,
                            rule_version=%s, status=%s, change_reason=%s,
                            updated_by=%s, version=version+1
                        WHERE id=%s AND version=%s
                        """,
                        [*values.values(), actor, rule_id, expected_version],
                    )
                    if cursor.rowcount != 1:
                        raise RuntimeError("规则已被其他用户修改，请刷新后重试。")
                else:
                    cursor.execute(
                        """
                        INSERT INTO dpr_operation_classification_rule
                          (rule_code, rule_name, priority, op_code_pattern, op_sub_pattern,
                           keyword_pattern, classification_json, rule_version, status,
                           change_reason, created_by, updated_by)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        [*values.values(), actor, actor],
                    )
                    rule_id = int(cursor.lastrowid)
                cursor.execute("SELECT * FROM dpr_operation_classification_rule WHERE id=%s", (rule_id,))
                row = cursor.fetchone()
            connection.commit()
        except Exception as exc:
            connection.rollback()
            if getattr(exc, "args", ()) and exc.args[0] == 1062:
                raise ValueError("规则编码已存在。") from exc
            raise
    return _json_row(row or {})


def list_confirmation_queue(*, status: str = "", limit: int = 1000) -> list[dict[str, Any]]:
    statuses = [status] if status else ["PENDING", "CONFLICT"]
    placeholders = ",".join(["%s"] * len(statuses))
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT c.*, a.daily_report_id, a.source_row_no, a.hours, a.op_code, a.op_sub,
                       a.source_op_type, a.operation_details, d.record_id, d.report_date,
                       d.report_type, d.match_status
                FROM dpr_operation_classification c
                JOIN dpr_operation a ON a.id=c.activity_id
                JOIN dpr_report d ON d.id=a.daily_report_id
                WHERE c.confirmation_status IN ({placeholders})
                  AND COALESCE(a.source_op_type, '') NOT IN ('SC','NPT')
                ORDER BY d.report_date DESC, d.record_id, a.source_row_no
                LIMIT %s
                """,
                [*statuses, max(1, min(int(limit), 5000))],
            )
            rows = cursor.fetchall()
    return [_json_row(row) for row in rows]


def confirm_classification(activity_id: int, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
    expected_version = int(payload.get("version", 0) or 0)
    if not expected_version:
        raise ValueError("确认分类必须提供 version。")
    revised = {field: str(payload.get(field, "") or "").strip() for field in CLASSIFICATION_FIELDS}
    reason = str(payload.get("change_reason", "") or "").strip()
    if not reason:
        raise ValueError("人工确认必须填写变更原因。")
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT c.*,a.source_op_type FROM dpr_operation_classification c "
                    "JOIN dpr_operation a ON a.id=c.activity_id WHERE c.activity_id=%s FOR UPDATE",
                    (activity_id,),
                )
                previous = cursor.fetchone()
                if not previous:
                    raise KeyError(activity_id)
                if str(previous.get("source_op_type", "") or "").strip().upper() in {"SC", "NPT"}:
                    raise ValueError("SC/NPT 必须在前台 NPT确认 模块完成调整、责任和待工属性划分。")
                cursor.execute(
                    "INSERT INTO dpr_operation_classification_revision "
                    "(activity_id, previous_json, revised_json, revision_type, reason, created_by) "
                    "VALUES (%s,%s,%s,'manual',%s,%s)",
                    (
                        activity_id,
                        json.dumps(_json_row(previous), ensure_ascii=False),
                        json.dumps(revised, ensure_ascii=False),
                        reason,
                        actor,
                    ),
                )
                assignments = ", ".join(f"{field}=%s" for field in CLASSIFICATION_FIELDS)
                cursor.execute(
                    f"UPDATE dpr_operation_classification SET {assignments}, confirmation_status='CONFIRMED', "
                    "productivity_type_code=%s, "
                    "confirmed_at=NOW(), confirmed_by=%s, change_reason=%s, updated_by=%s, version=version+1 "
                    "WHERE activity_id=%s AND version=%s",
                    [*[revised[field] for field in CLASSIFICATION_FIELDS], revised["productive_flag"], actor, reason, actor, activity_id, expected_version],
                )
                if cursor.rowcount != 1:
                    raise RuntimeError("分类已被其他用户修改，请刷新后重试。")
                cursor.execute(
                    "SELECT d.record_id FROM dpr_operation a JOIN dpr_report d ON d.id=a.daily_report_id "
                    "WHERE a.id=%s",
                    (activity_id,),
                )
                report_row = cursor.fetchone() or {}
                record_id = str(report_row.get("record_id", "") or "")
                if record_id:
                    cursor.execute(
                        "SELECT COUNT(*) count FROM dpr_operation_classification c "
                        "JOIN dpr_operation a ON a.id=c.activity_id JOIN dpr_report d ON d.id=a.daily_report_id "
                        "WHERE d.record_id=%s AND c.confirmation_status NOT IN ('CONFIRMED','AUTO_CONFIRMED') "
                        "AND COALESCE(a.source_op_type,'') NOT IN ('SC','NPT')",
                        (record_id,),
                    )
                    if int((cursor.fetchone() or {}).get("count", 0) or 0) == 0:
                        cursor.execute(
                            "UPDATE dq_issue SET status='RESOLVED',resolution_note='全部活动已人工确认',"
                            "resolved_at=NOW(),resolved_by=%s,updated_by=%s,version=version+1 "
                            "WHERE issue_key=%s AND status='OPEN'",
                            (actor, actor, f"{record_id}:CLASSIFICATION_PENDING"),
                        )
                cursor.execute("SELECT * FROM dpr_operation_classification WHERE activity_id=%s", (activity_id,))
                row = cursor.fetchone()
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return _json_row(row or {})


def reclassify_non_manual(*, actor: str) -> dict[str, int | str]:
    """Apply the current rules without overwriting manually confirmed rows."""
    processed = 0
    pending = 0
    npt_pending = 0
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                rule_version = current_rule_version(cursor)
                cursor.execute(
                    "SELECT a.id activity_id,a.op_code,a.op_sub,a.source_op_type,a.operation_details,d.record_id "
                    "FROM dpr_operation a JOIN dpr_report d ON d.id=a.daily_report_id "
                    "LEFT JOIN dpr_operation_classification c ON c.activity_id=a.id "
                    "WHERE c.confirmation_status IS NULL OR c.confirmation_status<>'CONFIRMED' "
                    "ORDER BY d.report_date,d.record_id,a.source_row_no"
                )
                rows = cursor.fetchall()
                record_ids: set[str] = set()
                for row in rows:
                    classification = upsert_activity_classification(cursor, int(row["activity_id"]), {
                        "op_code": row.get("op_code", ""), "op_sub": row.get("op_sub", ""),
                        "source_op_type": row.get("source_op_type", ""),
                        "operation_details": row.get("operation_details", ""),
                    })
                    processed += 1
                    is_pending = classification.get("confirmation_status") not in {"CONFIRMED", "AUTO_CONFIRMED"}
                    source_type = str(row.get("source_op_type", "") or "").strip().upper()
                    if is_pending and source_type in {"SC", "NPT"}:
                        npt_pending += 1
                    elif is_pending:
                        pending += 1
                    record_ids.add(str(row.get("record_id", "") or ""))
                for record_id in record_ids:
                    cursor.execute(
                        "SELECT COUNT(*) count FROM dpr_operation_classification c "
                        "JOIN dpr_operation a ON a.id=c.activity_id JOIN dpr_report d ON d.id=a.daily_report_id "
                        "WHERE d.record_id=%s AND c.confirmation_status NOT IN ('CONFIRMED','AUTO_CONFIRMED') "
                        "AND COALESCE(a.source_op_type,'') NOT IN ('SC','NPT')",
                        (record_id,),
                    )
                    record_pending = int((cursor.fetchone() or {}).get("count", 0) or 0)
                    issue_key = f"{record_id}:CLASSIFICATION_PENDING"
                    if record_pending:
                        cursor.execute(
                            "INSERT INTO dq_issue "
                            "(issue_key,issue_type,severity,entity_type,entity_id,record_id,details_json,status,created_by,updated_by) "
                            "VALUES (%s,'CLASSIFICATION_PENDING','warning','report',%s,%s,%s,'OPEN',%s,%s) "
                            "ON DUPLICATE KEY UPDATE details_json=VALUES(details_json),status='OPEN',resolution_note='',"
                            "resolved_at=NULL,resolved_by='',updated_by=VALUES(updated_by),version=version+1",
                            (issue_key, record_id, record_id, json.dumps({"pending_count": record_pending}, ensure_ascii=False), actor, actor),
                        )
                    else:
                        cursor.execute(
                            "UPDATE dq_issue SET status='RESOLVED',resolution_note='规则重算后已全部确认',"
                            "resolved_at=NOW(),resolved_by=%s,updated_by=%s,version=version+1 "
                            "WHERE issue_key=%s AND status='OPEN'",
                            (actor, actor, issue_key),
                        )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return {"processed": processed, "pending": pending, "npt_pending": npt_pending, "rule_version": rule_version}


def _default_classification(source_type: str) -> dict[str, str]:
    source_type = source_type if source_type in {"P", "SC", "NPT"} else ""
    return {
        "productive_flag": "PRODUCTION" if source_type == "P" else "NON_PRODUCTION" if source_type else "",
        "confirmed_op_type": source_type,
        "work_bucket": "OPERATION" if source_type == "P" else "",
        "billing_status": "FULL_RATE" if source_type == "P" else "",
        "responsibility": "",
        "cause_code": "",
        "service_line": "",
    }


def _complete_classification(classification: dict[str, Any], source_type: str) -> dict[str, str]:
    default = _default_classification(source_type)
    for field in CLASSIFICATION_FIELDS:
        value = str(classification.get(field, "") or "").strip()
        if value:
            default[field] = value
    if source_type in {"P", "SC", "NPT"}:
        default["confirmed_op_type"] = source_type
        default["productive_flag"] = "PRODUCTION" if source_type == "P" else "NON_PRODUCTION"
    return default


def _classification_json(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(str(value or "{}"))
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _rule_matches(rule: dict[str, Any], *, op_code: str, op_sub: str, details: str) -> bool:
    patterns = (
        ("op_code_pattern", op_code),
        ("op_sub_pattern", op_sub),
        ("keyword_pattern", details),
    )
    has_pattern = False
    for field, value in patterns:
        pattern = str(rule.get(field, "") or "").strip()
        if not pattern:
            continue
        has_pattern = True
        try:
            if not re.search(pattern, value, flags=re.I):
                return False
        except re.error:
            return False
    return has_pattern


def _new_rule_version(rule_code: str, payload: dict[str, Any], classification: dict[str, str]) -> str:
    raw = json.dumps(
        {
            "rule_code": rule_code,
            "priority": payload.get("priority", 100),
            "op_code_pattern": payload.get("op_code_pattern", ""),
            "op_sub_pattern": payload.get("op_sub_pattern", ""),
            "keyword_pattern": payload.get("keyword_pattern", ""),
            "classification": classification,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return f"classification-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]}"


def _json_row(row: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat(sep=" ", timespec="seconds")
        elif isinstance(value, Decimal):
            result[key] = float(value)
        elif hasattr(value, "isoformat"):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


def _db_connection():
    from .mysql_database import _connect, initialize_database

    initialize_database()
    return _connect()
