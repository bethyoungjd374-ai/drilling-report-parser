from __future__ import annotations

import re
from pathlib import Path
from typing import Any, BinaryIO

from .pdf_io import extract_page as _extract_page
from .pdf_io import pdfplumber_open as _pdfplumber_open
from .pdf_io import reader as _reader
from .pdf_io import source_payload as _source_payload
from .text_structure import column_text as _structured_column_text
from .text_structure import normalize_multiline


TIME_TOKEN_RE = re.compile(r"^\d{1,2}:\d{2}$")
NUM_RE = r"[-+]?\d[\d,]*(?:\.\d+)?"


def parse_completion_pdf_daily_report(source: str | Path | bytes | BinaryIO) -> dict[str, Any]:
    payload_source = _source_payload(source)
    reader = _reader(payload_source)
    layout_pages = [_extract_page(page, "layout") for page in reader.pages]
    plain_pages = [_extract_page(page, "plain") for page in reader.pages]
    layout_text = "\n".join(layout_pages)
    plain_text = "\n".join(plain_pages)
    page1_lines = [line for line in layout_pages[0].splitlines() if line.strip()] if layout_pages else []

    fields = _parse_report_fields(page1_lines, layout_text, plain_text)
    fields["safetyComments"] = _parse_safety_comments(layout_text)
    fields["otherRemarks"] = _parse_other_remarks(layout_text)

    return {
        "metadata": {"source": "pdf_import", "parser": "completion_pdf_parser_v2_ocr", "report_type": "completion"},
        "report_fields": fields,
        "operations": _parse_operations_from_pdf(payload_source),
        "bulks": _parse_bulks(layout_pages),
        "mud_products": _parse_mud_products(layout_text),
        "perforation_intervals": _parse_perforation_intervals(layout_pages),
    }


def _clean(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    value = value.replace(" ,", ",").replace(" .", ".").replace(" :", ":")
    return value


def _num(value: str) -> str:
    match = re.search(NUM_RE, value or "")
    return match.group(0).replace(",", "") if match else ""


def _ref_datum_number(value: str) -> str:
    return _num(value)


def _date_to_input(value: str) -> str:
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", value or "")
    if not match:
        return ""
    month, day, year = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def _first_line(lines: list[str], contains: str) -> str:
    return next((line for line in lines if contains in line), "")


def _value_between(line: str, start: str, *stops: str) -> str:
    if start not in line:
        return ""
    value = line.split(start, 1)[1]
    for stop in stops:
        if stop and stop in value:
            value = value.split(stop, 1)[0]
    return _clean(value.strip(" :"))


def _collect_block(lines: list[str], start: str, stops: tuple[str, ...]) -> str:
    collecting = False
    parts: list[str] = []
    for line in lines:
        if not collecting and start in line:
            collecting = True
            line = line.split(start, 1)[1]
        if collecting:
            for stop in stops:
                if stop in line:
                    before = line.split(stop, 1)[0]
                    if before.strip():
                        parts.append(before)
                    return normalize_multiline("\n".join(parts))
            if line.strip():
                parts.append(line)
    return normalize_multiline("\n".join(parts))


def _parse_report_fields(lines: list[str], layout_text: str, plain_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    event_line = _first_line(lines, "Evento:")
    event_match = re.search(r"Evento:\s*(.*?)\s+Fecha:Nro:([A-Z0-9-]+)\s+(\d{2}/\d{2}/\d{4})", event_line)
    if event_match:
        fields["event"] = _clean(event_match.group(1))
        fields["wellbore"] = re.sub(r"^COM", "", _clean(event_match.group(2)))
        fields["reportDate"] = _date_to_input(event_match.group(3))

    reason_line = _first_line(lines, "Razón Prim:")
    reason_match = re.search(r"Razón Prim:\s*(.*?)\s+Reporte No:\s*(\S+)", reason_line)
    if reason_match:
        fields["primaryReason"] = _clean(reason_match.group(1))
        fields["reportNo"] = _clean(reason_match.group(2))

    description_line = _first_line(lines, "Description:")
    fields["description"] = _value_between(description_line, "Description:", "Inicio OPR:")
    fields["operationStartDate"] = _date_to_input(_value_between(description_line, "Inicio OPR:"))

    rig_match = re.search(r"Taladro en Operación:\s*SINOPEC\s+(\d+)", layout_text)
    if rig_match:
        fields["rig"] = f"SINOPEC {rig_match.group(1)}"

    afp_line = _first_line(lines, "AFP Número")
    fields["afeNumber"] = _value_between(afp_line, "AFP Número", "Rig Name")
    if not fields["afeNumber"]:
        fields["afeNumber"] = _num(afp_line)
    ref_match = re.search(r"Ref Datum:\s*(.*?)\s+Costo diario:\s*(\$?[-\d,.]+)", afp_line)
    if ref_match:
        fields["refDatum"] = _ref_datum_number(ref_match.group(1))
        fields["dailyCost"] = _clean(ref_match.group(2))

    afp_cost_line = _first_line(lines, "AFP Costo")
    cost_match = re.search(r"AFP Costo\s*:?\s*(\$?[\d,]+).*?Costo acumulado:\s*(\$?[-\d,.]+)", afp_cost_line)
    if cost_match:
        fields["afeCost"] = _clean(cost_match.group(1))
        fields["cumulativeCost"] = _clean(cost_match.group(2))

    fields["currentOps"] = _collect_block(lines, "Operación Actual", ("24-Hr Resumen:",))
    fields["currentOps"] = fields["currentOps"].lstrip(": ")
    fields["summary24h"] = _collect_block(lines, "24-Hr Resumen:", ("24-Hr Pronóstico:",))
    fields["forecast24h"] = _collect_block(lines, "24-Hr Pronóstico:", ("Supervisor 1", "OPERACIONES"))
    fields.update(_parse_personnel(lines, layout_text, plain_text))
    return fields


def _parse_personnel(lines: list[str], layout_text: str, plain_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    sup1_line = _first_line(lines, "Supervisor 1")
    sup1_match = re.search(r"Supervisor 1\s+(.*?)\s+Ingeniero\s+(.*?)\s+Ingeniero PAM\s+(.*)$", sup1_line)
    if sup1_match:
        fields["supervisor1"] = _clean(sup1_match.group(1))
        fields["engineer"] = _clean(sup1_match.group(2))
        fields["pamEngineer"] = _clean(sup1_match.group(3))

    sup2_line = _first_line(lines, "Supervisor 2")
    sup2_match = re.search(r"Supervisor 2\s+(.*?)\s+Geólogo\s*(.*)$", sup2_line)
    if sup2_match:
        fields["supervisor2"] = _clean(sup2_match.group(1))
        tail = sup2_match.group(2)
        total_match = re.search(r"(\d+(?:\.\d+)?)\s*Total personal|Total personal\s*(\d+(?:\.\d+)?)", tail)
        if total_match:
            fields["totalPersonnel"] = total_match.group(1) or total_match.group(2) or ""
            fields["geologist"] = _clean(tail[: total_match.start()])
        else:
            fields["geologist"] = _clean(tail)

    if not fields.get("totalPersonnel"):
        total_match = re.search(r"(\d+(?:\.\d+)?)\s*Total personal|Total personal\s*(\d+(?:\.\d+)?)", layout_text)
        if total_match:
            fields["totalPersonnel"] = total_match.group(1) or total_match.group(2) or ""

    # Plain text occasionally preserves personnel labels when layout spacing is extreme.
    if not fields.get("supervisor1"):
        sup1_match = re.search(r"Supervisor 1\s+(.+?)\s+Ingeniero\s+(.+?)\s+Ingeniero PAM\s+(.+)", plain_text)
        if sup1_match:
            fields["supervisor1"] = _clean(sup1_match.group(1))
            fields["engineer"] = _clean(sup1_match.group(2))
            fields["pamEngineer"] = _clean(sup1_match.group(3))
    return fields


def _parse_operations_from_pdf(source: str | Path | bytes) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with _pdfplumber_open(source) as pdf:
        for page in pdf.pages:
            rows.extend(_parse_operation_page(page))
    return rows


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
        row_words = [
            word for word in words
            if row_top - 3 <= word["top"] < row_bottom and 175 <= word["x0"] <= 590
        ]
        parsed = _operation_from_words(row_words)
        if parsed:
            rows.append(parsed)
    return rows


def _operation_header_top(words: list[dict[str, Any]]) -> float | None:
    for word in sorted(words, key=lambda item: item["top"]):
        if word["text"] != "Desde" or not 175 <= word["x0"] <= 205:
            continue
        top = word["top"]
        same_header = [item for item in words if top - 2 <= item["top"] <= top + 16]
        has_to = any(item["text"] == "Hasta" and 200 <= item["x0"] <= 225 for item in same_header)
        has_code = any(item["text"] == "Código" and 240 <= item["x0"] <= 270 for item in same_header)
        has_details = any(item["text"] == "Detalle" and 400 <= item["x0"] <= 450 for item in same_header)
        if has_to and has_code and has_details:
            return top
    return None


def _operation_end_top(words: list[dict[str, Any]], header_top: float, page_height: float) -> float:
    candidates: list[float] = []
    for word in words:
        if word["top"] <= header_top + 24:
            continue
        text = word["text"]
        if text in {"Combustible", "June"}:
            candidates.append(word["top"])
        elif text == "INTERVALOS" and _is_perforation_interval_heading(words, word):
            candidates.append(word["top"])
        elif word["x0"] < 260 and (text.startswith("**") or text.startswith("*CUADRILLA")):
            candidates.append(word["top"])
    return min(candidates) - 3 if candidates else page_height - 30


def _is_perforation_interval_heading(words: list[dict[str, Any]], interval_word: dict[str, Any]) -> bool:
    """Distinguish the lower perforation table from prose inside an operation row."""

    return any(
        abs(word["top"] - interval_word["top"]) <= 3
        and word["x0"] >= interval_word["x1"]
        and re.sub(r"[^A-ZÁÉÍÓÚÑ]", "", word["text"].upper()).startswith("CAÑONEAD")
        for word in words
    )


def _operation_row_starts(words: list[dict[str, Any]], header_top: float, end_top: float) -> list[dict[str, Any]]:
    starts: list[dict[str, Any]] = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        if not TIME_TOKEN_RE.match(word["text"]):
            continue
        if not 180 <= word["x0"] <= 200 or word["top"] <= header_top + 6 or word["top"] >= end_top:
            continue
        same_line = [item for item in words if abs(item["top"] - word["top"]) <= 2.8]
        has_to = any(TIME_TOKEN_RE.match(item["text"]) and 200 <= item["x0"] <= 222 for item in same_line)
        has_hours = any(re.match(r"^\d+(?:\.\d+)?$", item["text"]) and 218 <= item["x0"] <= 235 for item in same_line)
        has_operation_value = any(
            item["text"].strip() and 234 <= item["x0"] <= 324
            for item in same_line
        )
        if has_to and (has_hours or has_operation_value):
            starts.append(word)
    return starts


def _operation_from_words(words: list[dict[str, Any]]) -> dict[str, str] | None:
    start = _column_text(words, 180, 202, first_line_only=True)
    end = _column_text(words, 202, 219.5, first_line_only=True)
    hours = _column_text(words, 219.5, 234.4, first_line_only=True)
    hours_source = "DECLARED"
    if not hours:
        hours = _hours_from_clock_range(start, end)
        hours_source = "CLOCK_DERIVED"
    if not (start and end and hours):
        return None
    return {
        "from": start,
        "to": end,
        "hours": hours,
        "hours_source": hours_source,
        "op_code": _normalize_op_code(_column_text(words, 234.4, 266)),
        "op_sub": _clean_op_sub(_column_text(words, 266, 302)),
        "op_type": _normalize_op_type(_column_text(words, 302, 324, first_line_only=True)),
        "operation_details": _clean_operation_details(_column_text(words, 324, 590, preserve_lines=True)),
    }


def _hours_from_clock_range(start: str, end: str) -> str:
    def minutes(value: str) -> int | None:
        match = re.fullmatch(r"(\d{1,2}):(\d{2})", value.strip())
        if not match:
            return None
        hour, minute = int(match.group(1)), int(match.group(2))
        if minute >= 60 or hour > 24 or (hour == 24 and minute):
            return None
        return hour * 60 + minute

    start_minutes = minutes(start)
    end_minutes = minutes(end)
    if start_minutes is None or end_minutes is None:
        return ""
    if end_minutes <= start_minutes:
        end_minutes += 24 * 60
    duration = (end_minutes - start_minutes) / 60
    return f"{duration:.2f}"


def _column_text(
    words: list[dict[str, Any]],
    left: float,
    right: float,
    first_line_only: bool = False,
    preserve_lines: bool = False,
) -> str:
    return _structured_column_text(
        words,
        left,
        right,
        first_line_only=first_line_only,
        preserve_lines=preserve_lines,
        line_tolerance=2.8,
    )


def _normalize_op_code(value: str) -> str:
    text = _clean(value)
    compact = re.sub(r"[^A-Z]", "", text.upper())
    if compact.startswith("PERFORAT"):
        return "PERFORATING"
    if compact.startswith("STIMULATI"):
        return "STIMULATION"
    if compact.startswith("SURFACEEQUIPMEN"):
        return "SURFACE EQUIPMENT"
    if compact.startswith("SLICKLINE"):
        return "SLICK LINE"
    if compact.startswith("SAFETY"):
        return "SAFETY"
    if compact.startswith("LOGGING"):
        return "LOGGING"
    return text


def _normalize_op_type(value: str) -> str:
    upper = _clean(value).upper().replace(" ", "")
    if "NPT" in upper:
        return "NPT"
    if upper in {"P", "SC"}:
        return upper
    return ""


def _clean_op_sub(value: str) -> str:
    text = _clean(value)
    replacements = {
        "MU/Breakd own": "MU/Breakdown",
        "Armado/De sarmado": "Armado/Desarmado",
        "Fracturamie nto": "Fracturamiento",
        "Run/Pull Packer, Bri": "Run/Pull Packer, Bri",
        "desarmado d": "desarmado de",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return _clean(text)


def _clean_operation_details(value: str) -> str:
    return normalize_multiline(value)


def _parse_bulks(layout_pages: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(rf"^\s*([A-Z][A-Z0-9 /-]+?)\s+({NUM_RE})\s+({NUM_RE})\s+({NUM_RE})(?=[A-Z]|\s|$)")
    for page in layout_pages:
        if "Combustible" not in page:
            continue
        for line in page.splitlines():
            if "PRODUCTOS DE LODOS" in line or "INTERVALOS CAÑONEADOS" in line:
                break
            match = pattern.match(line)
            if not match:
                continue
            name, start, used, end = match.groups()
            if name.strip() in {"Combustible", "PRODUCTOS DE LODOS"}:
                continue
            rows.append({
                "bulk": _clean(name),
                "qty_start": start.replace(",", ""),
                "qty_used": used.replace(",", ""),
                "qty_end": end.replace(",", ""),
            })
    return rows


def _parse_mud_products(layout_text: str) -> list[dict[str, str]]:
    if "PRODUCTOS DE LODOS" in layout_text:
        return []
    return []


def _parse_perforation_intervals(layout_pages: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(
        rf"^\s*([A-ZÁÉÍÓÚÑ0-9 ]+?)\s+({NUM_RE})\s+({NUM_RE})\s+({NUM_RE})\s+({NUM_RE})\s+"
        rf"(.+?)\s+({NUM_RE})\s+({NUM_RE})\s+({NUM_RE})\s+(\d{{1,2}}/\d{{1,2}}/\d{{4}})\s+([A-Z]+)(?:\s+(.*))?$"
    )
    for page in layout_pages:
        if "INTERVALOS CAÑONEADOS" not in page:
            continue
        for line in page.splitlines():
            match = pattern.match(line)
            if not match:
                continue
            formation, top_md, base_md, length, density, charges, phase, penetration, diameter, date, status, comments = match.groups()
            rows.append({
                "formation": _clean(formation),
                "top_md": top_md.replace(",", ""),
                "base_md": base_md.replace(",", ""),
                "length": length.replace(",", ""),
                "density": density.replace(",", ""),
                "charges": _clean(charges),
                "phase": phase.replace(",", ""),
                "penetration": penetration.replace(",", ""),
                "diameter": diameter.replace(",", ""),
                "date": _date_to_input(date),
                "status": _clean(status),
                "comments": _clean(comments or ""),
            })
    return rows


def _parse_safety_comments(layout_text: str) -> str:
    match = re.search(r"(INCIDENTES.*?)(?:\n\s*PRODUCTOS DE LODOS|\n\s*INTERVALOS|\n\s*COSTOS DIARIOS|\n.*OpenWells|\Z)", layout_text, re.S)
    return _clean(match.group(1)) if match else ""


def _parse_other_remarks(layout_text: str) -> str:
    match = re.search(r"(\*\*CONTROL DE SOLIDOS.*?)(?:\n\s*Combustible|\Z)", layout_text, re.S)
    if match:
        return _clean(match.group(1))
    crew = re.search(r"(\* CUADRILLA COMPLETA.*?)(?:\n\s*Combustible|\Z)", layout_text, re.S)
    return _clean(crew.group(1)) if crew else ""
