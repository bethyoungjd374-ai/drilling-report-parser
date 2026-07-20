"""PDF import strategies and cross-template validation.

The four report categories share the same batch splitting and identity
validation flow, while every parser remains independently selectable.  HTTP
handlers consume this registry instead of embedding parser/type exceptions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .completion_pdf_parser import parse_completion_pdf_daily_report
from .drilling_pdf_templates import drilling_pdf_template_parser
from .move_pdf_parser import parse_move_pdf_daily_report
from .pdf_batch import PdfReportSegment
from .report_type_detection import (
    REPORT_TYPE_LABELS,
    extract_pdf_report_events,
    normalize_report_event,
    report_types_from_event,
    storage_report_type_for_event_type,
)
from .workover_pdf_parser import parse_workover_pdf_daily_report


PdfParser = Callable[[bytes], dict[str, Any]]


@dataclass(frozen=True)
class PdfImportStrategy:
    import_type: str
    storage_report_type: str
    parser: PdfParser
    template_profile: str


def pdf_import_strategy(
    import_type: object,
    *,
    template_profile: object = "original",
    source_filename: str = "",
) -> PdfImportStrategy:
    """Resolve one explicit parser strategy without cross-template fallback."""

    report_type = str(import_type or "").strip().lower()
    if report_type == "drilling":
        profile = str(template_profile or "original").strip().lower()
        return PdfImportStrategy(
            import_type=report_type,
            storage_report_type="drilling",
            parser=drilling_pdf_template_parser(profile, source_filename),
            template_profile=profile,
        )
    strategies: dict[str, PdfParser] = {
        "completion": parse_completion_pdf_daily_report,
        "workover": parse_workover_pdf_daily_report,
        "move": parse_move_pdf_daily_report,
    }
    parser = strategies.get(report_type)
    if parser is None:
        raise ValueError(f"不支持的 PDF 日报类型：{report_type or '(空)'}。")
    return PdfImportStrategy(
        import_type=report_type,
        storage_report_type=report_type,
        parser=parser,
        template_profile="original",
    )


def report_identity_errors(payload: dict[str, object]) -> list[str]:
    fields = payload.get("report_fields", {})
    if not isinstance(fields, dict):
        return ["日报日期", "井号", "井队"]
    labels = (("reportDate", "日报日期"), ("wellbore", "井号"), ("rig", "井队"))
    return [label for field, label in labels if not str(fields.get(field, "") or "").strip()]


def validate_pdf_report_type(
    expected_report_type: str,
    payload: dict[str, Any],
    segment: PdfReportSegment,
    *,
    report_index: int,
    report_count: int,
) -> None:
    """Reject missing, ambiguous, or wrong-entry Event classifications."""

    fields = payload.get("report_fields", {})
    parsed_event = str(fields.get("event", "") or "").strip() if isinstance(fields, dict) else ""
    source_events = extract_pdf_report_events(segment.data)
    event_values = list(dict.fromkeys(
        value for value in (*source_events, parsed_event) if normalize_report_event(value)
    ))
    detected_event_types = {
        report_type
        for value in event_values
        for report_type in report_types_from_event(value)
    }

    metadata = payload.get("metadata", {})
    source_file = str(metadata.get("source_file", "") or "") if isinstance(metadata, dict) else ""
    source_label = f"（{source_file}）" if source_file else ""
    page_label = (
        f"第{segment.start_page}页"
        if segment.start_page == segment.end_page
        else f"第{segment.start_page}-{segment.end_page}页"
    )
    report_label = f"合并 PDF 第{report_index}份日报，{page_label}，" if report_count > 1 else f"{page_label}，"
    expected_label = REPORT_TYPE_LABELS.get(expected_report_type, expected_report_type)
    event_label = " / ".join(event_values)

    if not event_values:
        raise ValueError(
            f"日报类型校验失败{source_label}：{report_label}基本信息中缺少 Event 字段，"
            f"不能作为{expected_label}解析入库。"
        )
    if not detected_event_types:
        raise ValueError(
            f"日报类型校验失败{source_label}：{report_label}无法根据 Event“{event_label}”识别日报类型，"
            f"不能作为{expected_label}解析入库。"
        )
    if len(detected_event_types) != 1:
        detected_labels = "、".join(
            REPORT_TYPE_LABELS.get(value, value) for value in sorted(detected_event_types)
        )
        raise ValueError(
            f"日报类型校验失败{source_label}：{report_label}Event 内容存在类型冲突“{event_label}”"
            f"（同时匹配{detected_labels}），已拒绝入库。"
        )

    detected_event_type = next(iter(detected_event_types))
    detected_storage_type = storage_report_type_for_event_type(detected_event_type)
    if detected_storage_type != expected_report_type:
        detected_label = REPORT_TYPE_LABELS.get(detected_event_type, detected_event_type)
        storage_label = REPORT_TYPE_LABELS.get(detected_storage_type, detected_storage_type)
        raise ValueError(
            f"日报类型不匹配{source_label}：{report_label}Event“{event_label}”识别为{detected_label}，"
            f"该事件应归入{storage_label}，当前上传入口是{expected_label}。"
            f"请改用{storage_label}入口重新上传；本次未入库。"
        )

    if isinstance(metadata, dict):
        metadata["detected_event_type"] = detected_event_type
        metadata["detected_report_type"] = detected_storage_type
        metadata["report_type_validated"] = True


def pdf_import_response(
    payloads: list[dict[str, Any]],
    source_file: str,
    report_count: int,
) -> dict[str, Any]:
    if not payloads:
        raise ValueError("PDF 中未识别到日报。")
    if report_count == 1:
        return payloads[0]
    response = dict(payloads[0])
    first_metadata = payloads[0].get("metadata", {})
    metadata = dict(first_metadata) if isinstance(first_metadata, dict) else {}
    metadata.update({
        "source_file": Path(source_file).name,
        "multi_report": True,
        "imported_count": len(payloads),
    })
    response["metadata"] = metadata
    response["reports"] = payloads
    return response


def inherit_consistent_batch_rigs(payloads: list[dict[str, Any]]) -> None:
    """Fill a missing rig only when the same well has one unanimous batch rig."""

    rigs_by_well: dict[str, dict[str, str]] = {}
    for payload in payloads:
        fields = payload.get("report_fields", {})
        if not isinstance(fields, dict):
            continue
        wellbore = " ".join(str(fields.get("wellbore", "") or "").upper().split())
        rig = " ".join(str(fields.get("rig", "") or "").split())
        if not wellbore or not rig:
            continue
        rig_key = re.sub(r"[^A-Z0-9]+", "", rig.upper())
        rigs_by_well.setdefault(wellbore, {})[rig_key] = rig

    for payload in payloads:
        fields = payload.get("report_fields", {})
        if not isinstance(fields, dict) or str(fields.get("rig", "") or "").strip():
            continue
        wellbore = " ".join(str(fields.get("wellbore", "") or "").upper().split())
        candidates = rigs_by_well.get(wellbore, {})
        if len(candidates) != 1:
            continue
        fields["rig"] = next(iter(candidates.values()))
        metadata = payload.setdefault("metadata", {})
        if isinstance(metadata, dict):
            metadata["batch_inherited_fields"] = ["rig"]
