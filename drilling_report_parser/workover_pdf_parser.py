from __future__ import annotations

import re
from pathlib import Path
from typing import Any, BinaryIO

from .completion_pdf_parser import (
    NUM_RE,
    _clean,
    _collect_block,
    _first_line,
    _parse_bulks,
    _parse_daily_costs,
    _parse_mud_products,
    _parse_operations_from_pdf,
    _value_between,
)
from .pdf_io import extract_page as _extract_page
from .pdf_io import reader as _reader
from .pdf_io import source_payload as _source_payload
from .text_structure import normalize_multiline


def parse_workover_pdf_daily_report(source: str | Path | bytes | BinaryIO) -> dict[str, Any]:
    payload_source = _source_payload(source)
    reader = _reader(payload_source)
    layout_pages = [_extract_page(page, "layout") for page in reader.pages]
    plain_pages = [_extract_page(page, "plain") for page in reader.pages]
    layout_text = "\n".join(layout_pages)
    plain_text = "\n".join(plain_pages)
    page1_lines = [line for line in layout_pages[0].splitlines() if line.strip()] if layout_pages else []

    fields = _parse_report_fields(page1_lines, layout_text, plain_text)
    fields["safetyComments"] = _parse_safety_comments(layout_pages)
    fields["otherRemarks"] = _parse_other_remarks(layout_text)

    return {
        "metadata": {"source": "pdf_import", "parser": "workover_pdf_parser_v1", "report_type": "workover"},
        "report_fields": fields,
        "operations": _parse_operations(payload_source),
        "bulks": _parse_bulks(layout_pages),
        "daily_costs": _parse_daily_costs(layout_text),
        "mud_products": _parse_mud_products(layout_text),
        "perforation_intervals": _parse_perforation_intervals(layout_pages),
    }


def _parse_report_fields(lines: list[str], layout_text: str, plain_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    event_line = _first_line(lines, "Evento:")
    event_match = re.search(r"Evento:\s*(.*?)\s+Fecha:Nro:([A-Z0-9-]+)\s+(\d{2}/\d{2}/\d{4})", event_line)
    if event_match:
        fields["event"] = _clean(event_match.group(1))
        number_and_well = _clean(event_match.group(2))
        wo_match = re.match(r"^(\d{1,2})([A-Z].*)$", number_and_well)
        if wo_match:
            fields["workoverNo"] = wo_match.group(1)
            fields["wellbore"] = wo_match.group(2)
        else:
            fields["wellbore"] = number_and_well
        fields["reportDate"] = _date_mdy_to_input(event_match.group(3))

    reason_line = _first_line(lines, "Razón Prim:")
    reason_match = re.search(r"Razón Prim:\s*(.*?)\s+Reporte No:\s*(\S+)", reason_line)
    if reason_match:
        fields["primaryReason"] = _clean(reason_match.group(1))
        fields["reportNo"] = _clean(reason_match.group(2))
        if not fields.get("workoverNo"):
            wo_match = re.search(r"#\s*(\d{1,2})", fields["primaryReason"])
            if wo_match:
                fields["workoverNo"] = wo_match.group(1)

    description_block = _collect_description(lines)
    start_match = re.search(r"Inicio OPR:\s*(\d{1,2}/\d{1,2}/\d{4})", description_block)
    fields["operationStartDate"] = _date_mdy_to_input(start_match.group(1)) if start_match else ""
    fields["description"] = _clean(re.sub(r"Inicio OPR:\s*\d{1,2}/\d{1,2}/\d{4}", "", description_block))

    rig_match = re.search(r"Taladro en Operación:\s*(SINOPEC[-\s]\d+)", layout_text)
    if rig_match:
        fields["rig"] = _clean(rig_match.group(1))

    afp_line = _first_line(lines, "AFP Número")
    fields["afeNumber"] = _value_between(afp_line, "AFP Número", "Rig Name")
    if not fields["afeNumber"]:
        fields["afeNumber"] = _clean(_value_after_label_words(afp_line, "AFP Número"))
    ref_match = re.search(r"Ref Datum:\s*(.*?)\s+Costo diario:\s*(\$?[-\d,.]+)", afp_line)
    if ref_match:
        fields["refDatum"] = _clean(ref_match.group(1))
        fields["dailyCost"] = _clean(ref_match.group(2))

    afp_cost_line = _first_line(lines, "AFP Costo")
    cost_match = re.search(r"AFP Costo\s*:?\s*(.*?)\s+Costo acumulado:\s*(\$?[-\d,.]+)", afp_cost_line)
    if cost_match:
        fields["afeCost"] = _clean(cost_match.group(1))
        fields["cumulativeCost"] = _clean(cost_match.group(2))

    fields["currentOps"] = _collect_block(lines, "Operación Actual", ("24-Hr Resumen:",)).lstrip(": ")
    fields["summary24h"] = _collect_block(lines, "24-Hr Resumen:", ("24-Hr Pronóstico:",))
    fields["forecast24h"] = _collect_block(lines, "24-Hr Pronóstico:", ("Supervisor 1", "OPERACIONES"))
    fields.update(_parse_workover_personnel(lines, layout_text))
    return fields


def _collect_description(lines: list[str]) -> str:
    collecting = False
    parts: list[str] = []
    for line in lines:
        if not collecting and "Description:" in line:
            collecting = True
            line = line.split("Description:", 1)[1]
        if collecting:
            if "Wellbore:" in line:
                before = line.split("Wellbore:", 1)[0]
                if before.strip():
                    parts.append(before)
                break
            parts.append(line)
            if "Inicio OPR:" in line:
                # Some descriptions continue before the label on the same line;
                # the label itself marks the end of the field.
                break
    return normalize_multiline("\n".join(parts))


def _value_after_label_words(line: str, label: str) -> str:
    if label not in line:
        return ""
    return line.split(label, 1)[1].split("Rig Name", 1)[0].strip(" :")


def _parse_workover_personnel(lines: list[str], layout_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    sup1_line = _first_line(lines, "Supervisor 1")
    sup1_match = re.search(r"Supervisor 1\s+(.*?)\s+Ingeniero\s+(.*?)(?:\s+Ingeniero PAM\s*(.*))?$", sup1_line)
    if sup1_match:
        fields["supervisor1"] = _clean(sup1_match.group(1))
        fields["engineer"] = _clean(sup1_match.group(2))
        pam = _clean(sup1_match.group(3) or "")
        fields["pamEngineer"] = _clean(pam.split("Supervisor 2", 1)[0])

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
    return fields


def _date_mdy_to_input(value: str) -> str:
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", value or "")
    if not match:
        return ""
    month, day, year = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def _date_dmy_to_input(value: str) -> str:
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", value or "")
    if not match:
        return ""
    day, month, year = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def _parse_operations(source: str | Path | bytes) -> list[dict[str, str]]:
    rows = _parse_operations_from_pdf(source)
    for row in rows:
        row["op_code"] = _normalize_workover_op_code(row.get("op_code", ""))
        row["op_sub"] = _clean_workover_op_sub(row.get("op_sub", ""))
    return rows


def _normalize_workover_op_code(value: str) -> str:
    text = _clean(value)
    compact = re.sub(r"[^A-Z]", "", text.upper())
    if compact.startswith("WELLHEAD"):
        return "WELLHEAD"
    if compact.startswith("COMPLETIONOPS") or compact.startswith("COMPLETI"):
        return "COMPLETION OPS"
    if compact.startswith("SURFACEEQUIPMEN"):
        return "SURFACE EQUIPMENT"
    if compact.startswith("WELLCONTROL"):
        return "WELL CONTROL"
    if compact.startswith("SLICKLINE"):
        return "SLICK LINE"
    if compact.startswith("BOPTEST"):
        return "BOP TEST"
    if compact.startswith("MOVE"):
        return "MOVE"
    if compact.startswith("TESTING"):
        return "TESTING"
    return text


def _clean_workover_op_sub(value: str) -> str:
    text = _clean(value)
    text = text.replace("Pre job safety meeti", "Pre job safety meeting")
    text = re.sub(r"\bsafety meeti\b", "safety meeting", text)
    return _clean(text)


def _parse_perforation_intervals(layout_pages: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(
        rf"^\s*([A-ZÁÉÍÓÚÑ0-9 \"#-]+?)\s+({NUM_RE})\s+({NUM_RE})\s+({NUM_RE})\s+({NUM_RE})\s+"
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
                "date": _date_dmy_to_input(date),
                "status": _clean(status),
                "comments": _clean(comments or ""),
            })
    return rows


def _parse_safety_comments(layout_pages: list[str]) -> str:
    parts: list[str] = []
    collecting = False
    diesel_pattern = re.compile(rf"DIESEL - RIG.*?{NUM_RE}\s+{NUM_RE}\s+{NUM_RE}(.*)$")
    for page in layout_pages:
        if "COMENTARIOS DE SEGURIDAD" not in page:
            continue
        for line in page.splitlines():
            if "PRODUCTOS DE LODOS" in line or "INTERVALOS CAÑONEADOS" in line or "COSTOS DIARIOS" in line:
                if collecting:
                    return _clean(" ".join(parts))
                continue
            if "June " in line and "OpenWells" in line:
                break
            if not collecting:
                match = diesel_pattern.search(line)
                if match:
                    collecting = True
                    if match.group(1).strip():
                        parts.append(match.group(1))
            elif line.strip():
                parts.append(line)
    return _clean(" ".join(parts))


def _parse_other_remarks(layout_text: str) -> str:
    match = re.search(r"(\*\*CONTROL DE SOLIDOS.*?)(?:\n\s*Combustible|\Z)", layout_text, re.S)
    return _clean(match.group(1)) if match else ""
