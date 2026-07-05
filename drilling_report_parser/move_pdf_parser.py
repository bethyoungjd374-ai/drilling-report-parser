from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO

import pdfplumber

from .completion_pdf_parser import (
    NUM_RE,
    TIME_TOKEN_RE,
    _clean,
    _collect_block,
    _extract_page,
    _first_line,
    _num,
    _reader,
    _source_payload,
)


def parse_move_pdf_daily_report(source: str | Path | bytes | BinaryIO) -> dict[str, Any]:
    payload_source = _source_payload(source)
    reader = _reader(payload_source)
    layout_pages = [_extract_page(page, "layout") for page in reader.pages]
    plain_pages = [_extract_page(page, "plain") for page in reader.pages]
    layout_text = "\n".join(layout_pages)
    plain_text = "\n".join(plain_pages)
    page1_lines = [line for line in layout_pages[0].splitlines() if line.strip()] if layout_pages else []

    operations = _parse_operations(payload_source)
    fields = _parse_report_fields(page1_lines, layout_text, plain_text)

    return {
        "metadata": {"source": "pdf_import", "parser": "move_pdf_parser_v1", "report_type": "drilling"},
        "report_fields": fields,
        "operations": operations,
    }


def _parse_report_fields(lines: list[str], layout_text: str, plain_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    event_line = _first_line(lines, "Event:")
    event_match = re.search(r"Event:\s*(.*?)\s+Date:\s*([A-Z0-9-]+)?\s*(\d{1,2}/\d{1,2}/\d{4})", event_line)
    if event_match:
        fields["event"] = _clean(event_match.group(1))
        if event_match.group(2):
            fields["wellbore"] = _clean(event_match.group(2))
        fields["reportDate"] = _date_mdy_to_input(event_match.group(3))
    else:
        fields["event"] = _clean(_value_after_plain_label(plain_text, "Event:", "Date:"))
        date_match = re.search(r"\b(\d{1,2}/\d{1,2}/\d{4})\b", plain_text)
        fields["reportDate"] = _date_mdy_to_input(date_match.group(1)) if date_match else ""

    reason_line = _first_line(lines, "Prim. Reason:")
    reason_match = re.search(r"Prim\.\s*Reason:\s*(.*?)\s+ECU\s+Report No:\s*(\d+)", reason_line)
    if reason_match:
        fields["primaryReason"] = _clean(reason_match.group(1))
        fields["reportNo"] = reason_match.group(2)
    else:
        fields["primaryReason"] = _clean(_value_after_plain_label(plain_text, "EP PETROECUADOR", "Prim. Reason:"))
        report_match = re.search(r"Report No:\s*(\d+)", plain_text)
        fields["reportNo"] = report_match.group(1) if report_match else ""

    if not fields.get("wellbore"):
        well_match = re.search(r"\b([A-Z]{3,6}-\d+[A-Z]?)\b", plain_text)
        fields["wellbore"] = well_match.group(1) if well_match else ""

    header_line = _first_line(lines, "Wellbore:")
    rig_match = re.search(r"Wellbore:\s*(.*?)\s+Rig:\s*(.*?)\s+Ref Datum:", header_line)
    if rig_match:
        fields["wellborePrefix"] = _clean(rig_match.group(1))
        fields["rig"] = _clean(rig_match.group(2))
    else:
        rig_plain = re.search(r"Current Ops:.*?\n(00\s+SINOPEC\s+\d+)", plain_text, re.S)
        fields["rig"] = _clean(rig_plain.group(1)) if rig_plain else ""

    ref_match = re.search(r"Ref Datum:\s*(.*?)\s+DFS:", header_line)
    if ref_match:
        fields["refDatum"] = _clean(ref_match.group(1))
    else:
        ref_match = re.search(r"(ORIGINAL\s+KB\s+@\S+)", plain_text)
        fields["refDatum"] = _clean(ref_match.group(1)) if ref_match else ""

    fields["currentOps"] = _collect_block(lines, "Current Ops:", ("24-Hr Summary:",))
    fields["summary24h"] = _collect_block(lines, "24-Hr Summary:", ("24-Hr Forecast:",))
    fields["forecast24h"] = _collect_block(lines, "24-Hr Forecast:", ("CASING/WELL",))
    if not fields["currentOps"]:
        fields["currentOps"] = _clean(_value_after_plain_label(plain_text, "Current Ops:", "00 SINOPEC"))
    if not fields["summary24h"]:
        fields["summary24h"] = _clean(_value_after_plain_label(plain_text, "24-Hr Summary:", "24-Hr Forecast:"))
    if not fields["forecast24h"]:
        fields["forecast24h"] = _clean(_value_after_plain_label(plain_text, "24-Hr Forecast:", "MUD GAS"))

    fields.update(_parse_metric_fields(layout_text, plain_text, header_line))
    fields["otherRemarks"] = _parse_other_remarks(plain_text)
    return fields


def _value_after_plain_label(text: str, start: str, stop: str) -> str:
    if start not in text:
        return ""
    value = text.split(start, 1)[1]
    if stop in value:
        value = value.split(stop, 1)[0]
    return _clean(value)


def _parse_metric_fields(layout_text: str, plain_text: str, header_line: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    ground_match = re.search(r"Ground Elev:\s*([\d,.]+\s*ft)", layout_text)
    fields["groundElev"] = _clean(ground_match.group(1)) if ground_match else ""
    afe_days_match = re.search(r"AFE MD/Days:\s*(.*?)\s+Cum Cost:", layout_text)
    fields["afeMdDays"] = _clean(afe_days_match.group(1)) if afe_days_match else ""
    afe_number_match = re.search(r"AFE Number:\s*([A-Z0-9-]+)", layout_text)
    fields["afeNumber"] = _clean(afe_number_match.group(1)) if afe_number_match else ""
    fields["todayMd"] = _value_from_layout_label(layout_text, "Today's MD:")
    fields["prevMd"] = _value_from_layout_label(layout_text, "Prev MD:")
    fields["progress"] = _value_from_layout_label(layout_text, "Progress:")
    fields["rotHrsToday"] = _value_from_layout_label(layout_text, "Rot Hrs Today")
    return fields


def _value_from_layout_label(text: str, label: str) -> str:
    match = re.search(rf"{re.escape(label)}\s*({NUM_RE})", text)
    return match.group(1).replace(",", "") if match else ""


def _parse_operations(source: str | Path | bytes) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with _pdfplumber_open(source) as pdf:
        for page in pdf.pages:
            rows.extend(_parse_operation_page(page))
    return rows


def _pdfplumber_open(source: str | Path | bytes):
    if isinstance(source, (str, Path)):
        return pdfplumber.open(str(source))
    return pdfplumber.open(BytesIO(source))


def _parse_operation_page(page) -> list[dict[str, str]]:
    words = page.extract_words(x_tolerance=1, y_tolerance=3) or []
    header_top = _operation_header_top(words)
    if header_top is None:
        return []
    end_top = _operation_end_top(words, header_top, page.height)
    starts = _operation_row_starts(words, header_top, end_top)
    rows: list[dict[str, str]] = []
    for index, start in enumerate(starts):
        row_top = start["top"]
        row_bottom = starts[index + 1]["top"] - 0.5 if index + 1 < len(starts) else end_top
        row_words = [word for word in words if row_top - 3 <= word["top"] < row_bottom and 20 <= word["x0"] <= 575]
        parsed = _operation_from_words(row_words)
        if parsed:
            rows.append(parsed)
    return rows


def _operation_header_top(words: list[dict[str, Any]]) -> float | None:
    for word in sorted(words, key=lambda item: item["top"]):
        if word["text"] != "From" or not 24 <= word["x0"] <= 34:
            continue
        top = word["top"]
        same_header = [item for item in words if top - 2 <= item["top"] <= top + 16]
        has_to = any(item["text"] == "To" and 55 <= item["x0"] <= 70 for item in same_header)
        has_code = any(item["text"] == "Code" and 105 <= item["x0"] <= 130 for item in same_header)
        has_details = any(item["text"] == "Details" and 390 <= item["x0"] <= 425 for item in same_header)
        if has_to and has_code and has_details:
            return top
    return None


def _operation_end_top(words: list[dict[str, Any]], header_top: float, page_height: float) -> float:
    candidates = [
        word["top"]
        for word in words
        if word["top"] > header_top + 20 and word["text"] in {"Safety", "Incident?", "Environ"}
    ]
    return min(candidates) - 3 if candidates else page_height - 30


def _operation_row_starts(words: list[dict[str, Any]], header_top: float, end_top: float) -> list[dict[str, Any]]:
    starts: list[dict[str, Any]] = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        if not TIME_TOKEN_RE.match(word["text"]):
            continue
        if not 25 <= word["x0"] <= 48 or word["top"] <= header_top + 10 or word["top"] >= end_top:
            continue
        same_line = [item for item in words if abs(item["top"] - word["top"]) <= 2.8]
        has_to = any(TIME_TOKEN_RE.match(item["text"]) and 54 <= item["x0"] <= 78 for item in same_line)
        has_hours = any(re.match(r"^\d+(?:\.\d+)?$", item["text"]) and 82 <= item["x0"] <= 108 for item in same_line)
        if has_to and has_hours:
            starts.append(word)
    return starts


def _operation_from_words(words: list[dict[str, Any]]) -> dict[str, str] | None:
    start = _column_text(words, 24, 53, first_line_only=True)
    end = _column_text(words, 53, 82, first_line_only=True)
    hours = _column_text(words, 82, 108, first_line_only=True)
    if not (start and end and hours):
        return None
    return {
        "from": start,
        "to": end,
        "hours": hours,
        "op_code": _normalize_op_code(_column_text(words, 108, 132)),
        "op_sub": _clean_op_sub(_column_text(words, 132, 185)),
        "op_type": _normalize_op_type(_column_text(words, 185, 207, first_line_only=True)),
        "operation_details": _clean_operation_details(_column_text(words, 207, 575, preserve_lines=True)),
    }


def _column_text(
    words: list[dict[str, Any]],
    left: float,
    right: float,
    first_line_only: bool = False,
    preserve_lines: bool = False,
) -> str:
    selected = [word for word in words if left <= word["x0"] < right]
    if not selected:
        return ""
    if first_line_only:
        top = min(word["top"] for word in selected)
        selected = [word for word in selected if abs(word["top"] - top) <= 2.8]
    selected.sort(key=lambda word: (round(word["top"], 1), word["x0"]))
    if preserve_lines:
        lines: list[str] = []
        current_top: float | None = None
        current_words: list[str] = []
        for word in selected:
            top = round(word["top"], 1)
            if current_top is None or abs(top - current_top) <= 2.8:
                current_top = top if current_top is None else current_top
                current_words.append(word["text"])
                continue
            lines.append(_clean(" ".join(current_words)))
            current_top = top
            current_words = [word["text"]]
        if current_words:
            lines.append(_clean(" ".join(current_words)))
        return _join_text_lines(lines)
    return _clean(" ".join(word["text"] for word in selected))


def _normalize_op_code(value: str) -> str:
    compact = re.sub(r"[^A-Z]", "", _clean(value).upper())
    if compact.startswith("MOVE") or compact == "MOVE":
        return "MOVE"
    return _clean(value)


def _normalize_op_type(value: str) -> str:
    upper = _clean(value).upper().replace(" ", "")
    if upper in {"P", "SC", "NPT"}:
        return upper
    if "NPT" in upper:
        return "NPT"
    return ""


def _clean_op_sub(value: str) -> str:
    text = _clean(value)
    text = text.replace("Pre job safety meeti", "Pre job safety meeting")
    text = text.replace("Waiting for night", "Waiting for night")
    return _clean(text)


def _clean_operation_details(value: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in str(value or "").splitlines()]
    return _join_text_lines(lines)


def _join_text_lines(lines: list[str]) -> str:
    cleaned = [_clean(line) for line in lines if _clean(line)]
    if not cleaned:
        return ""
    punctuated: list[str] = []
    for line in cleaned:
        if not re.search(r"[.!?;:。！？；：]$", line):
            line = f"{line};"
        punctuated.append(line)
    return "\n".join(punctuated)


def _parse_other_remarks(plain_text: str) -> str:
    match = re.search(r"(\*\* CUADRILLA.*?)(?:Other Remarks:|\n\s*\d{1,2}/\d{1,2}/\d{4}.*?Page\s+\d+\s+of\s+\d+|\Z)", plain_text, re.S)
    return _clean(match.group(1)) if match else ""


def _date_mdy_to_input(value: str) -> str:
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", value or "")
    if not match:
        return ""
    month, day, year = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"
