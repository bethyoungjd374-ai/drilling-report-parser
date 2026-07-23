from __future__ import annotations

from datetime import date, datetime

import pytest

from drilling_report_parser.hsse_service import (
    HSSE_CATEGORIES,
    _month_bounds,
    _optional_ids,
    _overlap_day_count,
    _translated_summary,
    _validate_items,
    group_hsse_dashboard_events,
)
from drilling_report_parser.translation import source_hash


def _items(*, issue_code: str = "", description: str = "") -> list[dict[str, object]]:
    return [
        {
            "category_code": code,
            "has_issue": code == issue_code,
            "description": description if code == issue_code else "ignored when clear",
        }
        for code, _label in HSSE_CATEGORIES
    ]


def test_hsse_items_require_all_four_categories_and_clear_unused_text() -> None:
    normalized = _validate_items(_items(issue_code="SAFETY_HAZARD", description="吊带磨损，已更换"))

    assert [item["category_code"] for item in normalized] == [code for code, _label in HSSE_CATEGORIES]
    assert normalized[1]["has_issue"] is True
    assert normalized[1]["description"] == "吊带磨损，已更换"
    assert normalized[0]["description"] == ""


def test_hsse_issue_requires_description() -> None:
    with pytest.raises(ValueError, match="物的不安全状态.*必须填写内容"):
        _validate_items(_items(issue_code="SAFETY_HAZARD", description=""))


def test_hsse_month_bounds_support_december_rollover() -> None:
    start, end, normalized = _month_bounds("2026-12")

    assert normalized == "2026-12"
    assert start.isoformat() == "2026-12-01"
    assert end.isoformat() == "2027-01-01"


def test_hsse_optional_well_ids_are_unique_and_ordered() -> None:
    assert _optional_ids([12, "7", 12, "", None]) == [12, 7]
    assert _optional_ids(None) == []


def test_hsse_optional_well_ids_reject_invalid_values() -> None:
    with pytest.raises(ValueError, match="关联井号无效"):
        _optional_ids(["not-a-number"])


def test_hsse_dashboard_expected_days_use_assignment_overlap() -> None:
    assert _overlap_day_count(date(2026, 7, 1), date(2026, 7, 22), date(2026, 7, 5), date(2026, 7, 12)) == 8
    assert _overlap_day_count(date(2026, 7, 1), date(2026, 7, 22), datetime(2026, 6, 1), None) == 22
    assert _overlap_day_count(date(2026, 7, 1), date(2026, 6, 30), None, None) == 0


def test_hsse_dashboard_events_merge_by_date_and_team() -> None:
    common = {
        "date": "2026-07-22",
        "record_id": 3,
        "project_id": 8,
        "project_name": "PEC 西区二期总包",
        "team_id": 168,
        "team_code": "SINOPEC 168",
        "team_name": "SINOPEC 168",
        "well_names": [],
        "source_type": "MANUAL",
        "source": "HSSE填报",
        "source_reference": "",
        "submitter": "admin",
        "updated_at": "2026-07-22T18:33:00",
    }
    events = [
        {
            **common,
            "event_key": "3:PRODUCTION_ANOMALY",
            "category_code": "PRODUCTION_ANOMALY",
            "category_label": "生产异常情况",
            "description": "生产设备短时异常",
        },
        {
            **common,
            "event_key": "3:UNSAFE_BEHAVIOR",
            "category_code": "UNSAFE_BEHAVIOR",
            "category_label": "人的不安全行为（违章事件）",
            "description": "发现违章操作",
        },
        {
            **common,
            "date": "2026-07-21",
            "event_key": "2:SAFETY_HAZARD",
            "record_id": 2,
            "category_code": "SAFETY_HAZARD",
            "category_label": "物的不安全状态",
            "description": "护栏松动",
        },
    ]

    groups = group_hsse_dashboard_events(events)

    assert len(groups) == 2
    current = groups[0]
    assert current["event_key"] == "daily:2026-07-22:168"
    assert current["record_ids"] == [3]
    assert [item["category_code"] for item in current["categories"]] == [
        "UNSAFE_BEHAVIOR",
        "PRODUCTION_ANOMALY",
    ]
    assert current["category_label"] == "人的不安全行为（违章事件）、生产异常情况"
    assert current["description"] == "【人的不安全行为（违章事件）】发现违章操作；【生产异常情况】生产设备短时异常"


def test_hsse_summary_translation_requires_matching_completed_source() -> None:
    source = "INSTALAR CABEZAL DE PRODUCCION."
    translation = {
        "source_text": source,
        "source_hash": source_hash(source),
        "translated_text": "安装采油树。",
        "translation_status": "COMPLETED",
    }

    assert _translated_summary(source, translation) == "安装采油树。"
    assert _translated_summary("different source", translation) == ""
    assert _translated_summary(source, {**translation, "translation_status": "FAILED"}) == ""
