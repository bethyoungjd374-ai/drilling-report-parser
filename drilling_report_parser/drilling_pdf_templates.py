"""Selectable drilling PDF template profiles.

The original profile deliberately delegates to the established parser without
compatibility fallbacks.  The compatible profile starts with the same parser,
then fills only missing header fields from known alternate layouts or the
source filename.  Keeping the profiles separate makes imports reproducible and
allows new template variants to be added without changing original behaviour.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Callable

from .pdf_io import extract_page, reader, source_payload
from .pdf_report_parser import parse_pdf_daily_report


ORIGINAL_TEMPLATE_PROFILE = "original"
COMPATIBLE_TEMPLATE_PROFILE = "compatible"
SUPPORTED_DRILLING_TEMPLATE_PROFILES = {
    ORIGINAL_TEMPLATE_PROFILE,
    COMPATIBLE_TEMPLATE_PROFILE,
}

PdfSource = str | Path | bytes | BinaryIO
PdfParser = Callable[[bytes], dict[str, Any]]


def drilling_pdf_template_parser(profile: str, source_filename: str = "") -> PdfParser:
    """Return an isolated parser for the selected drilling template profile."""

    selected = normalize_drilling_template_profile(profile)
    if selected == ORIGINAL_TEMPLATE_PROFILE:
        return _original_parser

    def compatible_parser(source: bytes) -> dict[str, Any]:
        return parse_compatible_pdf_daily_report(source, source_filename=source_filename)

    return compatible_parser


def normalize_drilling_template_profile(profile: object) -> str:
    selected = str(profile or ORIGINAL_TEMPLATE_PROFILE).strip().lower()
    if selected not in SUPPORTED_DRILLING_TEMPLATE_PROFILES:
        raise ValueError(f"不支持的钻井 PDF 模板：{selected}。")
    return selected


def _original_parser(source: bytes) -> dict[str, Any]:
    payload = parse_pdf_daily_report(source)
    metadata = payload.setdefault("metadata", {})
    if isinstance(metadata, dict):
        metadata["template_profile"] = ORIGINAL_TEMPLATE_PROFILE
        metadata["template_variant"] = "daily_operations_report"
    return payload


def parse_compatible_pdf_daily_report(
    source: PdfSource,
    *,
    source_filename: str = "",
) -> dict[str, Any]:
    """Parse known drilling layouts without altering the original parser.

    The compatible profile supports the regular Daily Operations Report, its
    legacy exports with a blank Rig cell, and Daily Operations Short Report.
    Filename fallbacks are applied only to fields that the PDF body did not
    yield and are recorded in metadata.
    """

    payload_source = source_payload(source)
    payload = parse_pdf_daily_report(payload_source)
    pdf_reader = reader(payload_source)
    layout_pages = [extract_page(page, "layout") for page in pdf_reader.pages]
    plain_pages = [extract_page(page, "plain") for page in pdf_reader.pages]
    layout_text = "\n".join(layout_pages)
    plain_text = "\n".join(plain_pages)
    filename = source_filename or (Path(source).name if isinstance(source, (str, Path)) else "")

    fields = payload.setdefault("report_fields", {})
    if not isinstance(fields, dict):
        fields = {}
        payload["report_fields"] = fields

    variant = _detect_template_variant(layout_text, plain_text)
    candidates = _alternate_header_fields(layout_text, plain_text)
    filename_fields = _filename_header_fields(filename)
    compatibility_fields: list[str] = []
    filename_fallback_fields: list[str] = []

    for name, value in candidates.items():
        replace_short_reason = variant == "daily_operations_short_report" and name == "primaryReason"
        if value and (replace_short_reason or not str(fields.get(name, "") or "").strip()):
            fields[name] = value
            compatibility_fields.append(name)

    for name, value in filename_fields.items():
        if value and not str(fields.get(name, "") or "").strip():
            fields[name] = value
            compatibility_fields.append(name)
            filename_fallback_fields.append(name)

    if variant == "daily_operations_short_report":
        forecast = _layout_block(
            layout_pages[0].splitlines() if layout_pages else [],
            "24-Hr Forecast:",
            ("OPERATIONS",),
        )
        if forecast:
            fields["forecast24h"] = forecast
        afe_number = _first_group(layout_text, r"AFE Number:\s*([0-9]+)")
        if afe_number and not str(fields.get("afeNumber", "") or "").strip():
            fields["afeNumber"] = afe_number
            compatibility_fields.append("afeNumber")
        short_remarks = _short_other_remarks(layout_pages)
        if short_remarks:
            fields["otherRemarks"] = short_remarks
            compatibility_fields.append("otherRemarks")
        if _strip_short_operation_heading(payload):
            compatibility_fields.append("operations.operation_details")
        for name, value in _short_mud_fields(payload).items():
            if value and not str(fields.get(name, "") or "").strip():
                fields[name] = value
                compatibility_fields.append(name)

    cleaned_remarks = _strip_report_footer(str(fields.get("otherRemarks", "") or ""))
    if cleaned_remarks != str(fields.get("otherRemarks", "") or ""):
        fields["otherRemarks"] = cleaned_remarks
        compatibility_fields.append("otherRemarks")

    metadata = payload.setdefault("metadata", {})
    if isinstance(metadata, dict):
        metadata.update({
            "parser": "drilling_pdf_compatible_v1",
            "template_profile": COMPATIBLE_TEMPLATE_PROFILE,
            "template_variant": variant,
            "compatibility_fields": list(dict.fromkeys(compatibility_fields)),
            "filename_fallback_fields": list(dict.fromkeys(filename_fallback_fields)),
        })
    return payload


def _detect_template_variant(layout_text: str, plain_text: str) -> str:
    combined = f"{layout_text}\n{plain_text}".upper()
    if "DAILY OPERATIONS SHORT REPORT" in combined:
        return "daily_operations_short_report"
    return "daily_operations_report"


def _alternate_header_fields(layout_text: str, plain_text: str) -> dict[str, str]:
    combined = f"{plain_text}\n{layout_text}"
    fields: dict[str, str] = {}

    event = _first_group(combined, r"Event:\s*(.*?)\s+Date:")
    if event:
        fields["event"] = _clean(event)

    report_no = _first_group(combined, r"Report No:\s*(\d+)")
    if report_no:
        fields["reportNo"] = str(int(report_no))

    report_date = _first_group(combined, r"\b(\d{1,2}/\d{1,2}/\d{4})\b")
    if report_date:
        fields["reportDate"] = _input_date(report_date)

    wellbore = _first_group(
        combined,
        r"\b([A-Z]{2,}[A-Z0-9]*-[A-Z0-9-]+)\s+(?:DAILY OPERATIONS (?:SHORT )?REPORT|\|\s*DAILY OPERATIONS)",
        flags=re.I,
    )
    if not wellbore:
        wellbore = _first_group(combined, r"Date:\s*([A-Z]{2,}[A-Z0-9]*-[A-Z0-9-]+)")
    if wellbore:
        fields["wellbore"] = _clean(wellbore).upper()

    rig_patterns = (
        r"Wellbore:\s*00\s+Rig:\s*(SINOPEC[-\s]*\d+)",
        r"Wellbore:\s*00\s+(SINOPEC[-\s]*\d+)\s*Rig:",
        r"Rig:\s*(SINOPEC[-\s]*\d+)",
    )
    for pattern in rig_patterns:
        rig = _first_group(layout_text, pattern, flags=re.I)
        if rig:
            fields["rig"] = _normalize_rig(rig)
            break

    primary_reason = _first_group(combined, r"Prim\. Reason:\s*(.*?)\s*ECU(?:ADOR)?\b")
    if primary_reason:
        if wellbore:
            primary_reason = re.sub(re.escape(wellbore), "", primary_reason, flags=re.I)
        fields["primaryReason"] = _clean(primary_reason)
    return fields


def _filename_header_fields(filename: str) -> dict[str, str]:
    if not filename:
        return {}
    match = re.search(
        r"(?P<date>\d{8})-(?P<well>.+?)-(?P<rig>SIN(?:OPEC)?-\d+)-PEC-(?P<report>\d+)(?:-|\.)",
        Path(filename).name,
        re.I,
    )
    if not match:
        return {}
    values = match.groupdict()
    try:
        report_date = datetime.strptime(values["date"], "%m%d%Y").date().isoformat()
    except ValueError:
        report_date = ""
    rig_number = _first_group(values["rig"], r"(\d+)")
    return {
        "reportDate": report_date,
        "wellbore": _clean(values["well"]).upper(),
        "rig": f"SINOPEC {rig_number}" if rig_number else "",
        "reportNo": str(int(values["report"])),
    }


def _layout_block(lines: list[str], start: str, stops: tuple[str, ...]) -> str:
    collecting = False
    parts: list[str] = []
    for raw_line in lines:
        line = raw_line
        if not collecting and start in line:
            collecting = True
            line = line.split(start, 1)[1]
        if not collecting:
            continue
        for stop in stops:
            if stop in line:
                before = line.split(stop, 1)[0]
                if before.strip():
                    parts.append(before)
                return _clean(" ".join(parts))
        if line.strip():
            parts.append(line)
    return _clean(" ".join(parts))


def _short_other_remarks(layout_pages: list[str]) -> str:
    """Collect a short-report remarks section that starts on the next page."""

    collecting = False
    parts: list[str] = []
    for page in layout_pages:
        for raw_line in page.splitlines():
            line = raw_line.strip()
            if not collecting:
                heading = re.search(r"\bOTHER\s+REMARKS\b", line, re.I)
                if not heading:
                    continue
                collecting = True
                trailing = line[heading.end():].strip(" :-")
                if trailing:
                    parts.append(trailing)
                continue
            if _is_report_footer(line):
                break
            if _is_short_page_header(line):
                continue
            if line:
                parts.append(line)
    return _clean(" ".join(parts))


def _strip_short_operation_heading(payload: dict[str, Any]) -> bool:
    operations = payload.get("operations", [])
    if not isinstance(operations, list):
        return False
    changed = False
    for row in operations:
        if not isinstance(row, dict):
            continue
        details = str(row.get("operation_details", "") or "")
        cleaned = re.sub(r"(?:^|\n)\s*OTHER\s+REMARKS\s*$", "", details, flags=re.I).strip()
        if cleaned != details:
            row["operation_details"] = cleaned
            changed = True
    return changed


def _short_mud_fields(payload: dict[str, Any]) -> dict[str, str]:
    operations = payload.get("operations", [])
    if not isinstance(operations, list):
        return {}
    text = "\n".join(
        str(row.get("operation_details", "") or "")
        for row in operations
        if isinstance(row, dict)
    )
    marker = re.search(r"PROPIEDADES\s+(.+?):\s*PESO\s*([0-9]+(?:[.,][0-9]+)?)\s*PPG", text, re.I | re.S)
    if not marker:
        return {}
    mud_type = _clean(marker.group(1).splitlines()[-1])
    fields = {
        "mudType": mud_type,
        "mudDensity": _decimal(marker.group(2)),
        "viscosity": _decimal(_first_group(text, r"\bVISC\s*:\s*([0-9]+(?:[.,][0-9]+)?)\s*SEG/QT", flags=re.I)),
        "pv": _decimal(_first_group(text, r"\bPV\s*:\s*([0-9]+(?:[.,][0-9]+)?)", flags=re.I)),
        "yp": _decimal(_first_group(text, r"\bYP\s*:\s*([0-9]+(?:[.,][0-9]+)?)", flags=re.I)),
        "apiWl": _decimal(_first_group(text, r"\bAPI\s+FL\s*:\s*([0-9]+(?:[.,][0-9]+)?)", flags=re.I)),
        "sand": _decimal(_first_group(text, r"\b([0-9]+(?:[.,][0-9]+)?)\s*%\s*ARENA\b", flags=re.I)),
    }
    gels = re.search(
        r"\bGELES\s*([0-9]+(?:[.,][0-9]+)?)\s*/\s*([0-9]+(?:[.,][0-9]+)?)\s*/\s*([0-9]+(?:[.,][0-9]+)?)",
        text,
        re.I,
    )
    if gels:
        fields.update({
            "gel10s": _decimal(gels.group(1)),
            "gel10m": _decimal(gels.group(2)),
            "gel30m": _decimal(gels.group(3)),
        })
    return {name: value for name, value in fields.items() if value}


def _strip_report_footer(value: str) -> str:
    return re.sub(
        r"\s*\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)\s+"
        r"Page\s+\d+\s+of\s+\d+\s*$",
        "",
        value or "",
        flags=re.I,
    ).strip()


def _is_report_footer(line: str) -> bool:
    return bool(re.search(
        r"\b\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)\s+"
        r"Page\s+\d+\s+of\s+\d+\b",
        line or "",
        flags=re.I,
    ))


def _is_short_page_header(line: str) -> bool:
    text = _clean(line)
    if not text:
        return False
    if text.upper() == "EP PETROECUADOR":
        return True
    if text.startswith("Event:") and "Date:" in text:
        return True
    if text.startswith("Prim. Reason:") and "Report No:" in text:
        return True
    return text.startswith("Description:") and "Inicio OPR:" in text


def _first_group(text: str, pattern: str, *, flags: int = 0) -> str:
    match = re.search(pattern, text or "", flags)
    return match.group(1).strip() if match else ""


def _input_date(value: str) -> str:
    try:
        return datetime.strptime(value, "%m/%d/%Y").date().isoformat()
    except ValueError:
        return ""


def _normalize_rig(value: str) -> str:
    match = re.search(r"SINOPEC[-\s]*(\d+)", value or "", re.I)
    return f"SINOPEC {match.group(1)}" if match else _clean(value)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip(" :|-")


def _decimal(value: str) -> str:
    return str(value or "").strip().replace(",", ".")
