"""Backend-neutral record and NPT helpers shared by storage adapters."""

from __future__ import annotations

import re
from typing import Any

from .report_schema import REPORT_TYPES


def safe_float(value: Any) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def npt_statuses() -> list[dict[str, str]]:
    return [
        {"value": "pending", "label": "待确认"},
        {"value": "draft", "label": "确认中"},
        {"value": "confirmed", "label": "已确认"},
    ]


def confirmation_group_status(item: dict[str, Any]) -> str:
    statuses = {
        str(value or "").strip().lower()
        for value in item.get("statuses", [])
        if str(value or "").strip()
    }
    review_statuses = {value for value in statuses if value in {"pending", "draft", "confirmed"}}
    if review_statuses and review_statuses == {"confirmed"}:
        return "confirmed"
    if "draft" in review_statuses or ("confirmed" in review_statuses and "pending" in review_statuses):
        return "draft"
    record_count = len(item.get("record_ids", []) or [])
    locked_count = int(item.get("locked_count", 0) or 0)
    if not review_statuses and record_count and locked_count >= record_count:
        return "confirmed"
    return "pending"


def normalize_report_type(report_type: str) -> str:
    normalized = (report_type or "").strip().lower()
    if normalized not in REPORT_TYPES:
        raise ValueError(f"Unsupported report_type: {report_type}")
    return normalized


def natural_record_id(report_type: str, fields: dict[str, Any]) -> str:
    parts = [report_type, fields.get("wellbore", ""), fields.get("reportDate", ""), fields.get("reportNo", "")]
    if not all(str(part or "").strip() for part in parts):
        return ""
    return ":".join(slug(str(part)) for part in parts)


def slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return text.strip("-") or "unknown"
