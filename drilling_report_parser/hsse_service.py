"""Structured daily HSSE entry backed by effective-dated master data."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timedelta
import json
from typing import Any, Iterator

from .translation import source_hash


HSSE_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("UNSAFE_BEHAVIOR", "人的不安全行为（违章事件）"),
    ("SAFETY_HAZARD", "物的不安全状态"),
    ("CONCERN_EMPLOYEE", "不放心员工"),
    ("PRODUCTION_ANOMALY", "生产异常情况"),
)
HSSE_CATEGORY_CODES = {code for code, _label in HSSE_CATEGORIES}


@contextmanager
def _db_connection() -> Iterator[Any]:
    from .mysql_database import _connect, initialize_database

    initialize_database()
    with _connect() as connection:
        yield connection


def _json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    return value


def _json_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _json_value(value) for key, value in row.items()}


def _json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, (str, bytes, bytearray)) and value:
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _required_date(value: Any, label: str = "record_date") -> date:
    try:
        parsed = date.fromisoformat(str(value or "").strip()[:10])
    except ValueError as exc:
        raise ValueError(f"{label} 必须是有效日期。") from exc
    return parsed


def _required_id(value: Any, label: str) -> int:
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} 无效。") from exc
    if parsed <= 0:
        raise ValueError(f"请选择{label}。")
    return parsed


def _translated_summary(source_text: Any, translation: dict[str, Any] | None) -> str:
    source = str(source_text or "")
    row = translation or {}
    if str(row.get("translation_status") or "").upper() not in {"COMPLETED", "NOT_REQUIRED"}:
        return ""
    translated = str(row.get("translated_text") or "").strip()
    if not translated:
        return ""
    expected_hash = str(row.get("source_hash") or "")
    if expected_hash and expected_hash != source_hash(source):
        return ""
    translated_source = str(row.get("source_text") or "")
    if translated_source and source_hash(translated_source) != source_hash(source):
        return ""
    return translated


def _month_bounds(value: Any) -> tuple[date, date, str]:
    text = str(value or "").strip()[:7]
    try:
        start = date.fromisoformat(f"{text}-01")
    except ValueError as exc:
        raise ValueError("month 必须使用 YYYY-MM 格式。") from exc
    end = date(start.year + (1 if start.month == 12 else 0), 1 if start.month == 12 else start.month + 1, 1)
    return start, end, text


def load_hsse_form_options(record_date: str) -> dict[str, Any]:
    selected_date = _required_date(record_date)
    previous_date = selected_date - timedelta(days=1)
    day_end = selected_date + timedelta(days=1)
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id,project_code,project_name,project_type,service_scope "
                "FROM md_project WHERE status='active' "
                "AND (valid_from IS NULL OR valid_from<=%s) AND (valid_to IS NULL OR valid_to>=%s) "
                "ORDER BY project_name,project_code",
                (selected_date, selected_date),
            )
            projects = cursor.fetchall()
            cursor.execute(
                "SELECT assignment.project_id,assignment.team_id,assignment.service_discipline,"
                "project.project_code,project.project_name,"
                "team.team_code,team.team_name,team.team_type_code,team.model_code,team.company_id,"
                "organization.organization_name AS company_name "
                "FROM rel_project_team_assignment assignment "
                "JOIN md_project project ON project.id=assignment.project_id AND project.status='active' "
                "JOIN md_team team ON team.id=assignment.team_id AND team.status='active' "
                "LEFT JOIN md_organization organization ON organization.id=team.company_id "
                "WHERE assignment.status='active' AND assignment.valid_from<%s "
                "AND (assignment.valid_to IS NULL OR assignment.valid_to>%s) "
                "ORDER BY team.team_code,team.team_name",
                (day_end, selected_date),
            )
            teams = cursor.fetchall()
            cursor.execute(
                "SELECT report.id AS report_id,report.record_id,report.project_id,team.id AS team_id,report.well_id,"
                "well.well_code,well.well_name,report.report_date,summary.summary_24h "
                "FROM dpr_report report "
                "JOIN md_rig rig ON rig.id=report.rig_id "
                "JOIN md_team team ON team.id=rig.team_id "
                "JOIN md_well well ON well.id=report.well_id AND well.status='active' "
                "LEFT JOIN dpr_report_summary summary ON summary.daily_report_id=report.id "
                "WHERE report.report_date IN (%s,%s) AND report.match_status='MATCHED' "
                "ORDER BY team.team_code,report.report_date DESC,well.well_name,well.well_code,report.id DESC",
                (previous_date, selected_date),
            )
            report_rows = list(cursor.fetchall())
            record_ids = list(dict.fromkeys(
                str(row.get("record_id") or "")
                for row in report_rows
                if str(row.get("record_id") or "")
            ))
            summary_translations: dict[str, dict[str, Any]] = {}
            if record_ids:
                placeholders = ",".join(["%s"] * len(record_ids))
                cursor.execute(
                    "SELECT record_id,source_text,translated_text,source_hash,translation_status "
                    f"FROM translation_content WHERE record_id IN ({placeholders}) "
                    "AND field_code='report_fields.summary24h' AND target_language='zh-CN' "
                    "AND translation_status IN ('COMPLETED','NOT_REQUIRED')",
                    tuple(record_ids),
                )
                summary_translations = {
                    str(row.get("record_id") or ""): row
                    for row in cursor.fetchall()
                    if str(row.get("record_id") or "")
                }

    daily_wells: list[dict[str, Any]] = []
    daily_summaries: list[dict[str, Any]] = []
    seen_wells: set[tuple[int, int]] = set()
    seen_summaries: set[tuple[int, str, int]] = set()
    for row in report_rows:
        team_id = int(row.get("team_id") or 0)
        well_id = int(row.get("well_id") or 0)
        report_day = row.get("report_date")
        if not team_id or not well_id or not isinstance(report_day, date):
            continue
        summary_key = (team_id, report_day.isoformat(), well_id)
        if summary_key not in seen_summaries:
            seen_summaries.add(summary_key)
            summary_text = str(row.get("summary_24h") or "")
            daily_summaries.append({
                "project_id": int(row.get("project_id") or 0),
                "team_id": team_id,
                "well_id": well_id,
                "well_code": str(row.get("well_code") or ""),
                "well_name": str(row.get("well_name") or row.get("well_code") or ""),
                "report_date": report_day.isoformat(),
                "summary_24h": summary_text,
                "summary_24h_zh": _translated_summary(
                    summary_text,
                    summary_translations.get(str(row.get("record_id") or "")),
                ),
            })
        if report_day == selected_date and (team_id, well_id) not in seen_wells:
            seen_wells.add((team_id, well_id))
            daily_wells.append({
                "project_id": int(row.get("project_id") or 0),
                "team_id": team_id,
                "well_id": well_id,
                "well_code": str(row.get("well_code") or ""),
                "well_name": str(row.get("well_name") or row.get("well_code") or ""),
            })

    return {
        "record_date": selected_date.isoformat(),
        "previous_date": previous_date.isoformat(),
        "categories": [{"code": code, "label": label} for code, label in HSSE_CATEGORIES],
        "projects": [_json_row(row) for row in projects],
        "teams": [_json_row(row) for row in teams],
        "daily_wells": daily_wells,
        "daily_summaries": daily_summaries,
    }


def list_hsse_daily_records(
    *, month: str, project_id: Any = 0, team_id: Any = 0, source_type: str = "",
) -> dict[str, Any]:
    start, end, normalized_month = _month_bounds(month)
    clauses = ["record.record_date>=%s", "record.record_date<%s"]
    args: list[Any] = [start, end]
    if int(project_id or 0):
        clauses.append("record.project_id=%s")
        args.append(int(project_id))
    if int(team_id or 0):
        clauses.append("record.team_id=%s")
        args.append(int(team_id))
    normalized_source_type = str(source_type or "").strip().upper()
    if normalized_source_type in {"MANUAL", "EXCEL_IMPORT", "SIMULATED"}:
        clauses.append("record.data_source_type=%s")
        args.append(normalized_source_type)
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT record.* FROM hsse_daily_record record "
                f"WHERE {' AND '.join(clauses)} ORDER BY record.record_date DESC,record.team_code_snapshot",
                args,
            )
            rows = list(cursor.fetchall())
            record_ids = [int(row["id"]) for row in rows]
            item_rows: list[dict[str, Any]] = []
            well_rows: list[dict[str, Any]] = []
            if record_ids:
                placeholders = ",".join(["%s"] * len(record_ids))
                cursor.execute(
                    "SELECT daily_record_id,category_code,has_issue,description,sort_order "
                    f"FROM hsse_daily_item WHERE daily_record_id IN ({placeholders}) "
                    "ORDER BY daily_record_id,sort_order",
                    record_ids,
                )
                item_rows = list(cursor.fetchall())
                cursor.execute(
                    "SELECT daily_record_id,well_id,well_name_snapshot,sort_order "
                    f"FROM hsse_daily_record_well WHERE daily_record_id IN ({placeholders}) "
                    "ORDER BY daily_record_id,sort_order,id",
                    record_ids,
                )
                well_rows = list(cursor.fetchall())
    items_by_record: dict[int, list[dict[str, Any]]] = {record_id: [] for record_id in record_ids}
    wells_by_record: dict[int, list[dict[str, Any]]] = {record_id: [] for record_id in record_ids}
    for item in item_rows:
        normalized = _json_row(item)
        normalized["has_issue"] = bool(item.get("has_issue"))
        items_by_record[int(item["daily_record_id"])].append(normalized)
    for well in well_rows:
        wells_by_record[int(well["daily_record_id"])].append(_json_row(well))
    records: list[dict[str, Any]] = []
    issue_counts = {code: 0 for code, _label in HSSE_CATEGORIES}
    for row in rows:
        record = _json_row(row)
        record["source_context"] = _json_object(row.get("source_context_json"))
        record.pop("source_context_json", None)
        record["items"] = items_by_record.get(int(row["id"]), [])
        record_wells = wells_by_record.get(int(row["id"]), [])
        if not record_wells and row.get("well_id"):
            record_wells = [{
                "daily_record_id": int(row["id"]),
                "well_id": int(row["well_id"]),
                "well_name_snapshot": str(row.get("well_name_snapshot") or ""),
                "sort_order": 1,
            }]
        record["wells"] = record_wells
        record["well_ids"] = [int(well["well_id"]) for well in record_wells]
        for item in record["items"]:
            if item["has_issue"]:
                issue_counts[item["category_code"]] += 1
        records.append(record)
    return {
        "month": normalized_month,
        "records": records,
        "summary": {"record_count": len(records), "issue_counts": issue_counts},
    }


def _overlap_day_count(start: date, end: date, valid_from: Any, valid_to: Any) -> int:
    """Return inclusive assignment days inside [start, end]."""
    if end < start:
        return 0
    valid_start = valid_from.date() if isinstance(valid_from, datetime) else valid_from
    valid_end = valid_to.date() if isinstance(valid_to, datetime) else valid_to
    lower = max(start, valid_start if isinstance(valid_start, date) else start)
    upper = min(end, valid_end if isinstance(valid_end, date) else end)
    return max((upper - lower).days + 1, 0)


def group_hsse_dashboard_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge HSSE issue items into one dashboard row per date and team."""
    category_order = {code: index for index, (code, _label) in enumerate(HSSE_CATEGORIES)}
    grouped: dict[tuple[str, int], dict[str, Any]] = {}
    for event in events:
        event_date = str(event.get("date") or "")[:10]
        event_team_id = int(event.get("team_id") or 0)
        key = (event_date, event_team_id)
        group = grouped.get(key)
        if group is None:
            group = {
                "event_key": f"daily:{event_date}:{event_team_id}",
                "date": event_date,
                "project_id": int(event.get("project_id") or 0),
                "project_name": str(event.get("project_name") or ""),
                "team_id": event_team_id,
                "team_code": str(event.get("team_code") or ""),
                "team_name": str(event.get("team_name") or ""),
                "well_names": [],
                "categories": [],
                "record_ids": [],
                "source_types": [],
                "sources": [],
                "source_references": [],
                "submitters": [],
                "updated_at": "",
            }
            grouped[key] = group

        for well_name in event.get("well_names", []):
            normalized_well = str(well_name or "").strip()
            if normalized_well and normalized_well not in group["well_names"]:
                group["well_names"].append(normalized_well)
        record_id = int(event.get("record_id") or 0)
        if record_id and record_id not in group["record_ids"]:
            group["record_ids"].append(record_id)
        for target, value in (
            ("source_types", str(event.get("source_type") or "").strip()),
            ("sources", str(event.get("source") or "").strip()),
            ("source_references", str(event.get("source_reference") or "").strip()),
            ("submitters", str(event.get("submitter") or "").strip()),
        ):
            if value and value not in group[target]:
                group[target].append(value)
        updated_at = str(event.get("updated_at") or "")
        if updated_at > group["updated_at"]:
            group["updated_at"] = updated_at
        group["categories"].append({
            "event_key": str(event.get("event_key") or ""),
            "category_code": str(event.get("category_code") or ""),
            "category_label": str(event.get("category_label") or ""),
            "description": str(event.get("description") or ""),
        })

    result = list(grouped.values())
    for group in result:
        group["categories"].sort(
            key=lambda item: (
                category_order.get(str(item.get("category_code") or ""), len(category_order)),
                str(item.get("category_label") or ""),
            )
        )
        group["category_labels"] = [item["category_label"] for item in group["categories"]]
        group["category_label"] = "、".join(group["category_labels"])
        group["description"] = "；".join(
            f"【{item['category_label']}】{item['description'] or '未填写描述'}"
            for item in group["categories"]
        )
        group["record_id"] = group["record_ids"][0] if len(group["record_ids"]) == 1 else 0
        group["source_type"] = group["source_types"][0] if len(group["source_types"]) == 1 else "MIXED"
        group["source"] = "、".join(group["sources"]) or "HSSE填报"
        group["source_reference"] = "；".join(group["source_references"])
        group["submitter"] = "、".join(group["submitters"])
    result.sort(
        key=lambda item: (
            str(item.get("date") or ""),
            str(item.get("team_code") or ""),
            int(item.get("team_id") or 0),
        ),
        reverse=True,
    )
    return result


def load_hsse_dashboard(
    *,
    month: str,
    project_id: Any = 0,
    organization_id: Any = 0,
    discipline: str = "",
    team_id: Any = 0,
    source_type: str = "",
    only_issues: bool = False,
) -> dict[str, Any]:
    """Build the monthly safety cockpit from the full active-team roster and HSSE entries."""
    start, end, normalized_month = _month_bounds(month)
    today = date.today()
    due_end = min(end - timedelta(days=1), today) if start <= today else start - timedelta(days=1)
    selected_project = int(project_id or 0)
    selected_organization = int(organization_id or 0)
    selected_team = int(team_id or 0)
    selected_discipline = str(discipline or "").strip()
    selected_source_type = str(source_type or "").strip().upper()

    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT assignment.id AS assignment_id,assignment.project_id,assignment.team_id,"
                "assignment.service_discipline,assignment.valid_from,assignment.valid_to,assignment.priority,"
                "project.project_code,project.project_name,team.team_code,team.team_name,team.team_type_code,"
                "team.model_code,team.company_id AS organization_id,organization.organization_name "
                "FROM rel_project_team_assignment assignment "
                "JOIN md_project project ON project.id=assignment.project_id AND project.status='active' "
                "JOIN md_team team ON team.id=assignment.team_id AND team.status='active' "
                "LEFT JOIN md_organization organization ON organization.id=team.company_id "
                "WHERE assignment.status='active' AND assignment.valid_from<%s "
                "AND (assignment.valid_to IS NULL OR assignment.valid_to>=%s) "
                "ORDER BY assignment.team_id,assignment.priority,assignment.valid_from DESC,assignment.id DESC",
                (end, start),
            )
            roster_rows = list(cursor.fetchall())

    # One effective assignment per team keeps the cockpit at the operational team grain.
    roster_by_team: dict[int, dict[str, Any]] = {}
    for raw in roster_rows:
        row = _json_row(raw)
        row["valid_from_raw"] = raw.get("valid_from")
        row["valid_to_raw"] = raw.get("valid_to")
        roster_by_team.setdefault(int(raw.get("team_id") or 0), row)

    records = list_hsse_daily_records(
        month=normalized_month,
        source_type=selected_source_type,
    )["records"]
    records_by_team: dict[int, list[dict[str, Any]]] = {}
    for record in records:
        records_by_team.setdefault(int(record.get("team_id") or 0), []).append(record)

    # Retain historical entries even if their current master assignment has since been retired.
    for record in records:
        current_team_id = int(record.get("team_id") or 0)
        if current_team_id in roster_by_team:
            continue
        roster_by_team[current_team_id] = {
            "project_id": int(record.get("project_id") or 0),
            "team_id": current_team_id,
            "project_name": str(record.get("project_name_snapshot") or ""),
            "team_code": str(record.get("team_code_snapshot") or ""),
            "team_name": str(record.get("team_name_snapshot") or ""),
            "organization_id": int(record.get("organization_id") or 0),
            "organization_name": str(record.get("organization_name_snapshot") or ""),
            "service_discipline": str(record.get("team_type_snapshot") or ""),
            "model_code": str(record.get("team_model_snapshot") or ""),
            "valid_from_raw": start,
            "valid_to_raw": end - timedelta(days=1),
        }

    def matches(row: dict[str, Any]) -> bool:
        return (
            (not selected_project or int(row.get("project_id") or 0) == selected_project)
            and (not selected_organization or int(row.get("organization_id") or 0) == selected_organization)
            and (not selected_team or int(row.get("team_id") or 0) == selected_team)
            and (not selected_discipline or str(row.get("service_discipline") or "") == selected_discipline)
        )

    category_labels = dict(HSSE_CATEGORIES)
    issue_counts = {code: 0 for code, _label in HSSE_CATEGORIES}
    events: list[dict[str, Any]] = []
    teams: list[dict[str, Any]] = []
    total_expected_days = 0
    total_filled_days = 0
    reported_team_ids: set[int] = set()

    for row in sorted(
        (item for item in roster_by_team.values() if matches(item)),
        key=lambda item: (str(item.get("project_name") or ""), str(item.get("team_code") or "")),
    ):
        current_team_id = int(row.get("team_id") or 0)
        team_records = sorted(records_by_team.get(current_team_id, []), key=lambda item: str(item.get("record_date") or ""))
        expected_days = _overlap_day_count(start, due_end, row.get("valid_from_raw"), row.get("valid_to_raw"))
        filled_days = len({str(item.get("record_date") or "")[:10] for item in team_records})
        team_counts = {code: 0 for code, _label in HSSE_CATEGORIES}
        timeline: list[dict[str, Any]] = []
        by_date = {str(item.get("record_date") or "")[:10]: item for item in team_records}
        for day_number in range(1, (end - start).days + 1):
            day_value = start + timedelta(days=day_number - 1)
            record = by_date.get(day_value.isoformat())
            day_categories = {code: False for code, _label in HSSE_CATEGORIES}
            if record:
                for item in record.get("items", []):
                    code = str(item.get("category_code") or "")
                    if code in day_categories and bool(item.get("has_issue")):
                        day_categories[code] = True
            timeline.append({
                "date": day_value.isoformat(),
                "day": day_number,
                "recorded": bool(record),
                "is_due": day_value <= due_end,
                "issues": day_categories,
                "issue_count": sum(1 for value in day_categories.values() if value),
            })

        for record in team_records:
            source_context = record.get("source_context") if isinstance(record.get("source_context"), dict) else {}
            context_well = str(source_context.get("well_descriptor") or "").strip()
            well_names = [str(well.get("well_name_snapshot") or "") for well in record.get("wells", []) if well.get("well_name_snapshot")]
            if not well_names and context_well:
                well_names = [context_well]
            source_code = str(record.get("data_source_type") or "MANUAL").upper()
            source_label = {
                "EXCEL_IMPORT": "Excel真实记录",
                "SIMULATED": "模拟数据",
                "MANUAL": "HSSE填报",
            }.get(source_code, "HSSE填报")
            for item in record.get("items", []):
                code = str(item.get("category_code") or "")
                if code not in team_counts or not bool(item.get("has_issue")):
                    continue
                team_counts[code] += 1
                issue_counts[code] += 1
                events.append({
                    "event_key": f"{record.get('id')}:{code}",
                    "record_id": int(record.get("id") or 0),
                    "date": str(record.get("record_date") or "")[:10],
                    "project_id": int(record.get("project_id") or 0),
                    "project_name": str(record.get("project_name_snapshot") or row.get("project_name") or ""),
                    "team_id": current_team_id,
                    "team_code": str(record.get("team_code_snapshot") or row.get("team_code") or ""),
                    "team_name": str(record.get("team_name_snapshot") or row.get("team_name") or ""),
                    "well_names": well_names,
                    "category_code": code,
                    "category_label": category_labels.get(code, code),
                    "description": str(item.get("description") or ""),
                    "source_type": source_code,
                    "source": source_label,
                    "source_reference": str(record.get("source_reference") or ""),
                    "submitter": str(record.get("updated_by") or record.get("created_by") or ""),
                    "updated_at": str(record.get("updated_at") or record.get("created_at") or ""),
                })

        total_issues = sum(team_counts.values())
        if only_issues and total_issues == 0:
            continue
        risk_code = "medium" if total_issues else "low"
        risk_level = "中" if total_issues else "低"
        latest_record = team_records[-1] if team_records else {}
        latest_context = latest_record.get("source_context") if isinstance(latest_record.get("source_context"), dict) else {}
        source_labels = {
            "MANUAL": "HSSE填报",
            "EXCEL_IMPORT": "Excel真实记录",
            "SIMULATED": "模拟数据",
        }
        source_counts = {"MANUAL": 0, "EXCEL_IMPORT": 0, "SIMULATED": 0}
        source_references: dict[str, list[str]] = {source_code: [] for source_code in source_counts}
        for record in team_records:
            source_code = str(record.get("data_source_type") or "MANUAL").upper()
            if source_code in source_counts:
                source_counts[source_code] += 1
                source_reference = str(record.get("source_reference") or "").strip()
                if source_reference and source_reference not in source_references[source_code]:
                    source_references[source_code].append(source_reference)
        source_summary = [
            {
                "type": source_code,
                "label": source_labels[source_code],
                "record_days": source_counts[source_code],
                "references": source_references[source_code],
            }
            for source_code in ("EXCEL_IMPORT", "MANUAL", "SIMULATED")
            if source_counts[source_code]
        ]
        if filled_days:
            reported_team_ids.add(current_team_id)
        total_expected_days += expected_days
        total_filled_days += min(filled_days, expected_days) if expected_days else 0
        teams.append({
            "project_id": int(row.get("project_id") or 0),
            "project_name": str(row.get("project_name") or ""),
            "team_id": current_team_id,
            "team_code": str(row.get("team_code") or ""),
            "team_name": str(row.get("team_name") or ""),
            "organization_id": int(row.get("organization_id") or 0),
            "organization_name": str(row.get("organization_name") or ""),
            "discipline": str(row.get("service_discipline") or row.get("team_type_code") or ""),
            "model_code": str(row.get("model_code") or ""),
            "current_well": str(
                latest_context.get("well_descriptor")
                or latest_record.get("well_name_snapshot")
                or ""
            ),
            "progress_summary": str(latest_context.get("drilled_remaining") or ""),
            "source_counts": source_counts,
            "source_summary": source_summary,
            "filled_days": filled_days,
            "expected_days": expected_days,
            "missing_days": max(expected_days - filled_days, 0),
            "issue_counts": team_counts,
            "total_issues": total_issues,
            "attention": "关注" if total_issues else "正常",
            "risk_code": risk_code,
            "risk_level": risk_level,
            "timeline": timeline,
        })

    teams.sort(key=lambda item: (-int(item.get("total_issues") or 0), str(item.get("project_name") or ""), str(item.get("team_code") or "")))
    events.sort(key=lambda item: (item["date"], item["team_code"], item["category_code"]), reverse=True)
    event_groups = group_hsse_dashboard_events(events)
    total_issues = sum(issue_counts.values())
    roster_count = len(teams)
    summary = {
        "roster_team_count": roster_count,
        "reported_team_count": len(reported_team_ids),
        "team_coverage_pct": round((len(reported_team_ids) / roster_count * 100) if roster_count else 0, 1),
        "expected_team_days": total_expected_days,
        "filled_team_days": total_filled_days,
        "missing_team_days": max(total_expected_days - total_filled_days, 0),
        "completeness_pct": round((total_filled_days / total_expected_days * 100) if total_expected_days else 0, 1),
        "issue_counts": issue_counts,
        "total_issues": total_issues,
        "category_distribution": {
            code: round((count / total_issues * 100) if total_issues else 0, 1)
            for code, count in issue_counts.items()
        },
    }
    all_roster = list(roster_by_team.values())
    return {
        "month": normalized_month,
        "as_of_date": due_end.isoformat() if due_end >= start else "",
        "month_days": (end - start).days,
        "categories": [{"code": code, "label": label} for code, label in HSSE_CATEGORIES],
        "filters": {
            "projects": sorted({(int(row.get("project_id") or 0), str(row.get("project_name") or "")) for row in all_roster if row.get("project_id")}),
            "organizations": sorted({(int(row.get("organization_id") or 0), str(row.get("organization_name") or "")) for row in all_roster if row.get("organization_id")}),
            "disciplines": sorted({str(row.get("service_discipline") or "") for row in all_roster if row.get("service_discipline")}),
            "teams": sorted({(int(row.get("team_id") or 0), str(row.get("team_code") or row.get("team_name") or "")) for row in all_roster if row.get("team_id")}),
            "source_types": [
                ("EXCEL_IMPORT", "Excel真实记录"),
                ("SIMULATED", "模拟数据"),
                ("MANUAL", "手工填报"),
            ],
        },
        "summary": summary,
        "teams": teams,
        "events": events,
        "event_groups": event_groups,
    }


def _validate_items(raw_items: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_items, list):
        raise ValueError("四类事项数据格式无效。")
    by_code: dict[str, dict[str, Any]] = {}
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        code = str(raw.get("category_code") or "").strip().upper()
        if code not in HSSE_CATEGORY_CODES or code in by_code:
            continue
        has_issue = bool(raw.get("has_issue"))
        description = str(raw.get("description") or "").strip()
        if has_issue and not description:
            label = dict(HSSE_CATEGORIES)[code]
            raise ValueError(f"{label}选择‘有记录’后必须填写内容。")
        by_code[code] = {"category_code": code, "has_issue": has_issue, "description": description if has_issue else ""}
    missing = [label for code, label in HSSE_CATEGORIES if code not in by_code]
    if missing:
        raise ValueError(f"缺少分类事项：{'、'.join(missing)}。")
    return [by_code[code] for code, _label in HSSE_CATEGORIES]


def _optional_ids(value: Any) -> list[int]:
    raw_values = value if isinstance(value, list) else ([] if value in (None, "") else [value])
    normalized: list[int] = []
    for raw in raw_values:
        try:
            item_id = int(raw or 0)
        except (TypeError, ValueError) as exc:
            raise ValueError("关联井号无效。") from exc
        if item_id > 0 and item_id not in normalized:
            normalized.append(item_id)
    return normalized


def save_hsse_daily_record(payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
    record_date = _required_date(payload.get("record_date"))
    team_id = _required_id(payload.get("team_id"), "队伍")
    well_ids = _optional_ids(payload.get("well_ids", payload.get("well_id")))
    expected_version = int(payload.get("version") or 0)
    items = _validate_items(payload.get("items"))
    day_end = record_date + timedelta(days=1)

    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT project.id AS project_id,project.project_name,team.id AS team_id,team.team_code,"
                    "team.team_name,team.team_type_code,team.model_code,team.company_id,"
                    "organization.organization_name,assignment.service_discipline "
                    "FROM rel_project_team_assignment assignment "
                    "JOIN md_project project ON project.id=assignment.project_id AND project.status='active' "
                    "JOIN md_team team ON team.id=assignment.team_id AND team.status='active' "
                    "LEFT JOIN md_organization organization ON organization.id=team.company_id "
                    "WHERE assignment.team_id=%s AND assignment.status='active' "
                    "AND assignment.valid_from<%s AND (assignment.valid_to IS NULL OR assignment.valid_to>%s) "
                    "ORDER BY assignment.priority,assignment.valid_from DESC",
                    (team_id, day_end, record_date),
                )
                assignments = list(cursor.fetchall())
                project_ids = {int(row.get("project_id") or 0) for row in assignments if row.get("project_id")}
                if not assignments:
                    raise ValueError("所选日期下队伍没有有效项目关系，请先维护主数据关系。")
                if len(project_ids) != 1:
                    raise ValueError("所选日期下队伍存在多个有效项目关系，请先修正主数据。")
                master = assignments[0]
                project_id = int(master["project_id"])

                cursor.execute(
                    "SELECT report.well_id,well.well_name,well.well_code,summary.summary_24h "
                    "FROM dpr_report report "
                    "JOIN md_rig rig ON rig.id=report.rig_id "
                    "JOIN md_team team ON team.id=rig.team_id "
                    "JOIN md_well well ON well.id=report.well_id AND well.status='active' "
                    "LEFT JOIN dpr_report_summary summary ON summary.daily_report_id=report.id "
                    "WHERE report.project_id=%s AND team.id=%s AND report.report_date=%s "
                    "AND report.match_status='MATCHED' ORDER BY well.well_name,well.well_code,report.id DESC",
                    (project_id, team_id, record_date),
                )
                available_rows = list(cursor.fetchall())
                available_wells: dict[int, dict[str, Any]] = {}
                for row in available_rows:
                    available_wells.setdefault(int(row["well_id"]), row)
                if any(item_id not in available_wells for item_id in well_ids):
                    raise ValueError("关联井号必须来自所选队伍填报日期当天的日报。")
                selected_wells = [available_wells[item_id] for item_id in well_ids]
                first_well_id = well_ids[0] if well_ids else None
                first_well_name = ""
                if selected_wells:
                    first_well_name = str(selected_wells[0].get("well_name") or selected_wells[0].get("well_code") or "")
                work_status = "\n".join(
                    f"[{row.get('well_name') or row.get('well_code') or ''}] {str(row.get('summary_24h') or '').strip()}".strip()
                    for row in selected_wells
                    if str(row.get("summary_24h") or "").strip()
                )

                cursor.execute(
                    "SELECT id,version FROM hsse_daily_record WHERE team_id=%s AND record_date=%s FOR UPDATE",
                    (team_id, record_date),
                )
                existing = cursor.fetchone()
                values = (
                    project_id, first_well_id, master.get("company_id"), master.get("project_name") or "",
                    master.get("team_code") or "", master.get("team_name") or "",
                    master.get("organization_name") or "", master.get("service_discipline") or "",
                    master.get("model_code") or "", first_well_name, work_status,
                    "MANUAL", "", None, "submitted", actor,
                )
                if existing:
                    if expected_version and expected_version != int(existing.get("version") or 0):
                        raise RuntimeError("该记录已被其他用户更新，请刷新后重试。")
                    record_id = int(existing["id"])
                    cursor.execute(
                        "UPDATE hsse_daily_record SET project_id=%s,well_id=%s,organization_id=%s,"
                        "project_name_snapshot=%s,team_code_snapshot=%s,team_name_snapshot=%s,"
                        "organization_name_snapshot=%s,team_type_snapshot=%s,team_model_snapshot=%s,"
                        "well_name_snapshot=%s,work_status_snapshot=%s,data_source_type=%s,"
                        "source_reference=%s,source_context_json=%s,status=%s,updated_by=%s,version=version+1 "
                        "WHERE id=%s",
                        (*values, record_id),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO hsse_daily_record (record_date,project_id,team_id,well_id,organization_id,"
                        "project_name_snapshot,team_code_snapshot,team_name_snapshot,organization_name_snapshot,"
                        "team_type_snapshot,team_model_snapshot,well_name_snapshot,work_status_snapshot,"
                        "data_source_type,source_reference,source_context_json,status,created_by,updated_by) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (record_date, project_id, team_id, first_well_id, master.get("company_id"),
                         master.get("project_name") or "", master.get("team_code") or "", master.get("team_name") or "",
                         master.get("organization_name") or "", master.get("service_discipline") or "",
                         master.get("model_code") or "", first_well_name, work_status,
                         "MANUAL", "", None, "submitted", actor, actor),
                    )
                    record_id = int(cursor.lastrowid)

                cursor.execute("DELETE FROM hsse_daily_record_well WHERE daily_record_id=%s", (record_id,))
                for sort_order, row in enumerate(selected_wells, start=1):
                    cursor.execute(
                        "INSERT INTO hsse_daily_record_well (daily_record_id,well_id,well_name_snapshot,sort_order,created_by,updated_by) "
                        "VALUES (%s,%s,%s,%s,%s,%s)",
                        (record_id, int(row["well_id"]), row.get("well_name") or row.get("well_code") or "", sort_order, actor, actor),
                    )

                for sort_order, item in enumerate(items, start=1):
                    cursor.execute(
                        "INSERT INTO hsse_daily_item (daily_record_id,category_code,has_issue,description,sort_order,created_by,updated_by) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE has_issue=VALUES(has_issue),"
                        "description=VALUES(description),sort_order=VALUES(sort_order),updated_by=VALUES(updated_by)",
                        (record_id, item["category_code"], item["has_issue"], item["description"], sort_order, actor, actor),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    month = record_date.strftime("%Y-%m")
    records = list_hsse_daily_records(month=month, team_id=team_id)["records"]
    return next(record for record in records if int(record["id"]) == record_id)


def _resolve_hsse_team_master(cursor: Any, *, team_code: str, record_date: date) -> dict[str, Any] | None:
    day_end = record_date + timedelta(days=1)
    cursor.execute(
        "SELECT project.id AS project_id,project.project_name,team.id AS team_id,team.team_code,"
        "team.team_name,team.team_type_code,team.model_code,team.company_id,"
        "organization.organization_name,assignment.service_discipline "
        "FROM rel_project_team_assignment assignment "
        "JOIN md_project project ON project.id=assignment.project_id AND project.status='active' "
        "JOIN md_team team ON team.id=assignment.team_id AND team.status='active' "
        "LEFT JOIN md_organization organization ON organization.id=team.company_id "
        "WHERE REPLACE(UPPER(team.team_code),' ','')=%s AND assignment.status='active' "
        "AND assignment.valid_from<%s AND (assignment.valid_to IS NULL OR assignment.valid_to>%s) "
        "ORDER BY assignment.priority,assignment.valid_from DESC,assignment.id DESC",
        (str(team_code or "").replace(" ", "").upper(), day_end, record_date),
    )
    rows = list(cursor.fetchall())
    if not rows:
        return None
    if len({int(row.get("project_id") or 0) for row in rows}) != 1:
        return None
    return rows[0]


def _upsert_sourced_hsse_record(
    cursor: Any,
    *,
    record_date: date,
    master: dict[str, Any],
    items: list[dict[str, Any]],
    source_type: str,
    source_reference: str,
    source_context: dict[str, Any],
    actor: str,
    preserve_manual: bool = True,
) -> tuple[str, int]:
    team_id = int(master["team_id"])
    cursor.execute(
        "SELECT id,data_source_type FROM hsse_daily_record WHERE team_id=%s AND record_date=%s FOR UPDATE",
        (team_id, record_date),
    )
    existing = cursor.fetchone()
    existing_source = str((existing or {}).get("data_source_type") or "MANUAL").upper()
    if existing and preserve_manual and existing_source == "MANUAL":
        return "preserved_manual", int(existing["id"])
    if existing and source_type == "SIMULATED" and existing_source != "SIMULATED":
        return "preserved_source", int(existing["id"])

    context_json = json.dumps(source_context, ensure_ascii=False)
    well_descriptor = str(source_context.get("well_descriptor") or "").strip()
    values = (
        int(master["project_id"]),
        master.get("company_id"),
        master.get("project_name") or "",
        master.get("team_code") or "",
        master.get("team_name") or "",
        master.get("organization_name") or "",
        master.get("service_discipline") or master.get("team_type_code") or "",
        master.get("model_code") or "",
        well_descriptor,
        str(source_context.get("raw_text") or ""),
        source_type,
        source_reference,
        context_json,
        "submitted",
        actor,
    )
    if existing:
        record_id = int(existing["id"])
        cursor.execute(
            "UPDATE hsse_daily_record SET project_id=%s,organization_id=%s,well_id=NULL,"
            "project_name_snapshot=%s,team_code_snapshot=%s,team_name_snapshot=%s,"
            "organization_name_snapshot=%s,team_type_snapshot=%s,team_model_snapshot=%s,"
            "well_name_snapshot=%s,work_status_snapshot=%s,data_source_type=%s,source_reference=%s,"
            "source_context_json=%s,status=%s,updated_by=%s,version=version+1 WHERE id=%s",
            (*values, record_id),
        )
        action = "updated"
    else:
        cursor.execute(
            "INSERT INTO hsse_daily_record (record_date,project_id,team_id,organization_id,"
            "project_name_snapshot,team_code_snapshot,team_name_snapshot,organization_name_snapshot,"
            "team_type_snapshot,team_model_snapshot,well_name_snapshot,work_status_snapshot,"
            "data_source_type,source_reference,source_context_json,status,created_by,updated_by) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (record_date, int(master["project_id"]), team_id, master.get("company_id"),
             master.get("project_name") or "", master.get("team_code") or "", master.get("team_name") or "",
             master.get("organization_name") or "", master.get("service_discipline") or master.get("team_type_code") or "",
             master.get("model_code") or "", well_descriptor, str(source_context.get("raw_text") or ""),
             source_type, source_reference, context_json, "submitted", actor, actor),
        )
        record_id = int(cursor.lastrowid)
        action = "inserted"

    cursor.execute("DELETE FROM hsse_daily_record_well WHERE daily_record_id=%s", (record_id,))
    cursor.execute("DELETE FROM hsse_daily_item WHERE daily_record_id=%s", (record_id,))
    for sort_order, item in enumerate(items, start=1):
        cursor.execute(
            "INSERT INTO hsse_daily_item (daily_record_id,category_code,has_issue,description,sort_order,created_by,updated_by) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (record_id, item["category_code"], item["has_issue"], item["description"], sort_order, actor, actor),
        )
    return action, record_id


def import_hsse_records(
    records: list[dict[str, Any]], *, actor: str = "excel-import", source_file: str = "",
) -> dict[str, Any]:
    """Import artifact-tool-normalized Excel cells at the team/day grain."""
    stats: dict[str, Any] = {
        "input_records": len(records),
        "inserted": 0,
        "updated": 0,
        "preserved_manual": 0,
        "unmatched": [],
    }
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                for raw in records:
                    record_date = _required_date(raw.get("record_date"))
                    team_code = str(raw.get("team_code") or "").strip()
                    master = _resolve_hsse_team_master(cursor, team_code=team_code, record_date=record_date)
                    if not master:
                        stats["unmatched"].append({"team_code": team_code, "record_date": record_date.isoformat()})
                        continue
                    items = _validate_items(raw.get("items"))
                    source_reference = " · ".join(filter(None, (
                        source_file,
                        str(raw.get("source_sheet") or ""),
                        str(raw.get("source_cell") or ""),
                    )))
                    source_context = {
                        "source_project_name": str(raw.get("project_name") or ""),
                        "source_organization_name": str(raw.get("organization_name") or ""),
                        "source_discipline": str(raw.get("discipline") or ""),
                        "well_descriptor": str(raw.get("well_descriptor") or ""),
                        "drilled_remaining": str(raw.get("drilled_remaining") or ""),
                        "raw_text": str(raw.get("raw_text") or ""),
                        "source_sheet": str(raw.get("source_sheet") or ""),
                        "source_cell": str(raw.get("source_cell") or ""),
                    }
                    action, _record_id = _upsert_sourced_hsse_record(
                        cursor,
                        record_date=record_date,
                        master=master,
                        items=items,
                        source_type="EXCEL_IMPORT",
                        source_reference=source_reference,
                        source_context=source_context,
                        actor=actor,
                    )
                    stats[action] = int(stats.get(action, 0)) + 1
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    stats["unmatched_count"] = len(stats["unmatched"])
    return stats


def seed_hsse_simulated_records(
    *, month: str, records_per_team: int = 3, actor: str = "hsse-simulator",
) -> dict[str, Any]:
    """Create clearly marked, deterministic demo records only on empty team dates."""
    start, end, normalized_month = _month_bounds(month)
    inserted = 0
    skipped = 0
    descriptions = {
        "UNSAFE_BEHAVIOR": "【模拟数据】班前检查发现一名外协人员未规范使用个人防护用品，现场纠正并重新交底。",
        "SAFETY_HAZARD": "【模拟数据】巡检发现作业区一处临边防护松动，已设置警示并安排现场加固。",
        "CONCERN_EMPLOYEE": "【模拟数据】一名新到岗员工对当日高风险作业流程不熟悉，安排专人带教和监护。",
        "PRODUCTION_ANOMALY": "【模拟数据】设备短时报警导致作业节奏调整，现场检查后恢复正常运行。",
    }
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT assignment.project_id,assignment.team_id,assignment.service_discipline,"
                    "project.project_name,team.team_code,team.team_name,team.team_type_code,team.model_code,"
                    "team.company_id,organization.organization_name "
                    "FROM rel_project_team_assignment assignment "
                    "JOIN md_project project ON project.id=assignment.project_id AND project.status='active' "
                    "JOIN md_team team ON team.id=assignment.team_id AND team.status='active' "
                    "LEFT JOIN md_organization organization ON organization.id=team.company_id "
                    "WHERE assignment.status='active' AND assignment.valid_from<%s "
                    "AND (assignment.valid_to IS NULL OR assignment.valid_to>=%s) "
                    "ORDER BY assignment.team_id,assignment.priority,assignment.valid_from DESC",
                    (end, start),
                )
                masters_by_team: dict[int, dict[str, Any]] = {}
                for master in cursor.fetchall():
                    masters_by_team.setdefault(int(master.get("team_id") or 0), master)

                cursor.execute(
                    "SELECT team_id,DAY(record_date) AS day_number,source_context_json,data_source_type "
                    "FROM hsse_daily_record WHERE record_date>=%s AND record_date<%s ORDER BY record_date",
                    (start, end),
                )
                occupied: dict[int, set[int]] = {}
                contexts: dict[int, dict[str, Any]] = {}
                simulated_counts: dict[int, int] = {}
                for row in cursor.fetchall():
                    current_team_id = int(row.get("team_id") or 0)
                    occupied.setdefault(current_team_id, set()).add(int(row.get("day_number") or 0))
                    if str(row.get("data_source_type") or "").upper() == "SIMULATED":
                        simulated_counts[current_team_id] = simulated_counts.get(current_team_id, 0) + 1
                    context = _json_object(row.get("source_context_json"))
                    if context and not contexts.get(current_team_id):
                        contexts[current_team_id] = context

                month_days = (end - start).days
                for team_id, master in masters_by_team.items():
                    used_days = occupied.setdefault(team_id, set())
                    preferred_days = [
                        3 + team_id % 5,
                        10 + team_id % 5,
                        17 + team_id % 5,
                        24 + team_id % 5,
                        28 + team_id % 3,
                    ]
                    created_for_team = min(simulated_counts.get(team_id, 0), max(int(records_per_team), 0))
                    for day_number in preferred_days:
                        if created_for_team >= max(int(records_per_team), 0):
                            break
                        if day_number > month_days or day_number in used_days:
                            continue
                        issue_code = HSSE_CATEGORIES[(team_id + day_number) % len(HSSE_CATEGORIES)][0]
                        items = [
                            {
                                "category_code": code,
                                "has_issue": code == issue_code,
                                "description": descriptions[code] if code == issue_code else "",
                            }
                            for code, _label in HSSE_CATEGORIES
                        ]
                        base_context = contexts.get(team_id, {})
                        source_context = {
                            "is_simulated": True,
                            "simulation_batch": f"hsse-cockpit-demo-{normalized_month}",
                            "well_descriptor": str(base_context.get("well_descriptor") or "模拟井场记录"),
                            "drilled_remaining": str(base_context.get("drilled_remaining") or "—"),
                            "raw_text": descriptions[issue_code],
                        }
                        action, _record_id = _upsert_sourced_hsse_record(
                            cursor,
                            record_date=start + timedelta(days=day_number - 1),
                            master=master,
                            items=items,
                            source_type="SIMULATED",
                            source_reference=f"generated:hsse-cockpit-demo-{normalized_month}",
                            source_context=source_context,
                            actor=actor,
                        )
                        if action == "inserted":
                            inserted += 1
                            created_for_team += 1
                            used_days.add(day_number)
                        else:
                            skipped += 1
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return {"month": normalized_month, "inserted": inserted, "skipped": skipped, "team_count": len(masters_by_team)}
