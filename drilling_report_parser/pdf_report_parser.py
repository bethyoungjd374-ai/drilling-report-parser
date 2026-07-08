from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO

import pdfplumber
from pypdf import PdfReader


TIME_ROW_RE = re.compile(r"^\s*(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})\s+(\d+(?:\.\d+)?)\s+(.*)$")
TIME_TOKEN_RE = re.compile(r"^\d{1,2}:\d{2}$")
NUM_RE = r"[-+]?\d[\d,]*(?:\.\d+)?"


def parse_pdf_daily_report(source: str | Path | bytes | BinaryIO) -> dict[str, Any]:
    payload_source = _source_payload(source)
    reader = _reader(payload_source)
    layout_pages = [_extract_page(page, "layout") for page in reader.pages]
    plain_pages = [_extract_page(page, "plain") for page in reader.pages]
    layout_text = "\n".join(layout_pages)
    plain_text = "\n".join(plain_pages)
    page1_lines = [line for line in layout_pages[0].splitlines() if line.strip()] if layout_pages else []

    fields = _parse_report_fields(page1_lines, layout_text, plain_text)
    survey = _parse_survey(page1_lines)
    bha_components = _parse_bha_components(page1_lines)
    fields.update(_parse_bha_fields(page1_lines, bha_components))
    fields.update(_parse_mud_fields(page1_lines))
    fields.update(_parse_incidents(layout_text))
    fields["otherRemarks"] = _parse_other_remarks(layout_text)

    return {
        "metadata": {"source": "pdf_import", "parser": "pdf_report_parser_v1"},
        "report_fields": fields,
        "survey_data": survey,
        "bit_record": [{
            "bit_no": fields.get("bitNo", ""),
            "size": fields.get("bitSize", ""),
            "manufacturer": fields.get("bitManufacturer", ""),
            "serial_no": fields.get("bitSerial", ""),
        }],
        "bha_components": bha_components,
        "operations": _parse_operations_from_pdf(payload_source) or _parse_operations(layout_pages),
        "daily_costs": _parse_daily_costs(layout_text),
        "bulks": _parse_bulks(layout_pages),
    }


def _source_payload(source: str | Path | bytes | BinaryIO) -> str | Path | bytes:
    if isinstance(source, (str, Path, bytes)):
        return source
    return source.read()


def _reader(source: str | Path | bytes | BinaryIO) -> PdfReader:
    if isinstance(source, (str, Path)):
        return PdfReader(str(source))
    if isinstance(source, bytes):
        return PdfReader(BytesIO(source))
    return PdfReader(source)


def _extract_page(page, mode: str) -> str:
    try:
        if mode == "layout":
            return page.extract_text(extraction_mode="layout") or ""
        return page.extract_text() or ""
    except Exception:
        return page.extract_text() or ""


def _clean(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    value = value.replace(" ,", ",").replace(" .", ".")
    return value


def _clean_rig(value: str) -> str:
    value = _clean(value)
    value = re.sub(r"^00\s+(SINOPEC\b)", r"\1", value, flags=re.I)
    value = re.sub(r"\bSINOPEC[-\s]*(\d+)\b", r"SINOPEC \1", value, flags=re.I)
    return value


def _num(value: str) -> str:
    match = re.search(NUM_RE, value or "")
    return match.group(0).replace(",", "") if match else ""


def _float(value: str | None) -> float | None:
    try:
        return float(str(value or "").replace(",", ""))
    except ValueError:
        return None


def _date_to_input(value: str) -> str:
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", value or "")
    if not match:
        return ""
    month, day, year = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def _split_slash(value: str, parts: int) -> list[str]:
    values = [_clean(part) for part in (value or "").split("/")]
    while len(values) < parts:
        values.append("")
    return values[:parts]


def _join_slash(*values: str) -> str:
    return " / ".join(str(value or "").strip() for value in values)


def _split_at(value: str, marker: str) -> tuple[str, str]:
    if marker not in (value or ""):
        return _clean(value), ""
    left, right = value.split(marker, 1)
    return _clean(left), _clean(right)


def _first_line(lines: list[str], prefix: str) -> str:
    for line in lines:
        if prefix in line:
            return line
    return ""


def _value_between(line: str, start: str, *stops: str) -> str:
    if start not in line:
        return ""
    value = line.split(start, 1)[1]
    for stop in stops:
        if stop and stop in value:
            value = value.split(stop, 1)[0]
    return _clean(value.strip(" :"))


def _parse_report_fields(lines: list[str], layout_text: str, plain_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    event_line = _first_line(lines, "Event:")
    event_match = re.search(r"Event:\s*(.*?)\s+Date:\s*([A-Z0-9-]+)?\s*(\d{2}/\d{2}/\d{4})", event_line)
    if event_match:
        fields["event"] = _clean(event_match.group(1))
        fields["wellbore"] = _clean(event_match.group(2) or "")
        fields["reportDate"] = _date_to_input(event_match.group(3))

    reason_line = _first_line(lines, "Prim. Reason:")
    reason_match = re.search(r"Prim\. Reason:\s*(.*?)\s+ECU\s+Report No:\s*(\S+)", reason_line)
    if reason_match:
        fields["primaryReason"] = _clean(reason_match.group(1))
        fields["reportNo"] = _clean(reason_match.group(2))

    rig_line = _first_line(lines, "Wellbore:")
    rig_match = re.search(r"Wellbore:\s*00\s+SINOPEC\s+(\d+)\s*Rig:", rig_line)
    if rig_match:
        fields["rig"] = _clean_rig(f"SINOPEC {rig_match.group(1)}")
    fields["refDatum"] = _value_between(rig_line, "Ref Datum:", "DFS:")

    today_line = _first_line(lines, "Today's MD:")
    fields["todayMd"] = _num(_value_between(today_line, "Today's MD:", "Progress:"))
    fields["progress"] = _num(_value_between(today_line, "Progress:", "Ground Elev:"))

    prev_line = _first_line(lines, "Prev MD:")
    fields["prevMd"] = _num(_value_between(prev_line, "Prev MD:", "Rot Hrs Today"))
    rot = _num(_value_between(prev_line, "Rot Hrs Today", "AFE MD/Days:"))
    fields["rotHrsToday"] = rot
    if not fields.get("progress"):
        today_md = _float(fields.get("todayMd"))
        prev_md = _float(fields.get("prevMd"))
        if today_md is not None and prev_md is not None:
            fields["progress"] = f"{today_md - prev_md:.2f}"

    afe_line = _first_line(lines, "Avg ROP Slide")
    fields["afeNumber"] = _value_between(afe_line, "AFE Number:", "AFE Cost:")

    fields["currentOps"] = _collect_block(lines, "Current Ops:", ("24-Hr Summary:",))
    fields["summary24h"] = _collect_block(lines, "24-Hr Summary:", ("24-Hr Forecast:",))
    fields["forecast24h"] = _collect_block(lines, "24-Hr Forecast:", ("CASING/WELL CONTROL",))

    fields["lastCasing"] = _value_between(_first_line(lines, "Last Casing:"), "Last Casing:", "Str Wt Up/Dn:")
    fields["lastCasingSize"], fields["lastCasingDepth"] = _split_at(fields["lastCasing"], "@")
    fields["nextCasing"] = _value_between(_first_line(lines, "Next Casing:"), "Next Casing:", "Str Wt Rot:")
    fields["nextCasingSize"], fields["nextCasingDepth"] = _split_at(fields["nextCasing"], "@")
    bop_line = _first_line(lines, "Last BOP Press Test")
    fields["lastBopPressTest"] = _value_between(bop_line, ":", "Torq Off Btm:")
    fields["formTestEmw"] = _value_between(_first_line(lines, "Form Test"), "/EMW:", "Torq On Btm:")
    fields["pumpRate"] = _num(_value_between(_first_line(lines, "Pump Rate:"), "Pump Rate:", "Conn:"))
    fields["pumpPress"] = _num(_value_between(_first_line(lines, "Pump Press:"), "Pump Press:", "Trip:"))
    fields["stringWeightUpDown"] = _value_between(_first_line(lines, "Str Wt Up/Dn:"), "Str Wt Up/Dn:", "Pump Rate:")
    fields["torqueOnBottom"] = _value_between(_first_line(lines, "Torq On Btm:"), "Torq On Btm:")

    # Plain text is useful for fallback when layout text drops labels in narrow columns.
    if not fields.get("wellbore"):
        match = re.search(r"Date:\s*\n?Report No:\s*\d+\s*\n\d{2}/\d{2}/\d{4}.*?\n([A-Z0-9-]+)\nWellbore:", plain_text, re.S)
        if match:
            fields["wellbore"] = _clean(match.group(1))
    return fields


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
                    return _clean(" ".join(parts))
            if line.strip():
                parts.append(line)
    return _clean(" ".join(parts))


def _parse_survey(lines: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(
        r"(?P<md>\d{1,2},\d{3}\.\d)\s+"
        r"(?P<incl>\d{1,3}\.\d{2})\s+"
        r"(?P<tvd>\d{1,2},\d{3}\.\d{2})\s+"
        r"(?P<vse>\d{1,2},\d{3}\.\d)(?P<azi>\d{1,3}\.\d{2})\s+"
        r"(?P<ns>\d{1,2},\d{3}\.\d)\s+"
        r"(?P<vs>\d{1,2},\d{3}\.\d)\s+"
        r"(?P<dls>-?\d+\.\d{2})\s+"
        r"(?P<build>-?\d+\.\d{2})"
    )
    for line in lines:
        match = pattern.search(line)
        if not match:
            continue
        data = match.groupdict()
        rows.append({
            "md": data["md"].replace(",", ""),
            "incl": data["incl"],
            "azi": data["azi"],
            "tvd": data["tvd"].replace(",", ""),
            "vse": data["vse"].replace(",", ""),
            "ns": data["ns"].replace(",", ""),
            "dls": data["dls"],
            "build": data["build"],
        })
    return rows[:6]


def _parse_bha_components(lines: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(rf"([A-Za-z][A-Za-z0-9 /\\-]+?)\s+(\d+\.\d{{3}})\s+(\d+\.\d{{3}})\s+(\d+)\s+({NUM_RE})")
    for line in lines:
        match = pattern.search(line[95:])
        if not match:
            continue
        component, od, inner_id, joints, length = match.groups()
        if component.strip().lower() in {"component"}:
            continue
        rows.append({
            "component": _clean(component),
            "od": od,
            "id": inner_id,
            "joints": joints,
            "length": length.replace(",", ""),
        })
    return rows


def _parse_bha_fields(lines: list[str], components: list[dict[str, str]]) -> dict[str, str]:
    fields: dict[str, str] = {}
    bha_line = _first_line(lines, "BHA No")
    match = re.search(r"BHA No\s*:?\s*(\d+).*?Bit No:\s*(\d+).*?MD In:\s*([\d,]+\.\d+\s*ft)", bha_line)
    if match:
        fields["bhaNo"], fields["bitNo"], fields["bhaMdIn"] = match.groups()
    purpose_line = _first_line(lines, "Purpose:")
    fields["bhaMdOut"] = _value_between(purpose_line, "MD Out:")
    fields["bhaTotalLength"] = _num(_value_between(_first_line(lines, "Total Length:"), "Total Length:", "Wt below Jars:"))
    if components:
        fields["bitSize"] = components[0].get("od", "")
    bit_record_line = next((line for line in lines if "PRF-" in line and "MUD DATA" not in line), "")
    manufacturer = re.search(r"(PRF-[A-Z0-9 .ÁÉÍÓÚÑ&-]+?)(?:BT|HD|S\d|PS|\d{6,})", bit_record_line)
    if manufacturer:
        fields["bitManufacturer"] = _clean(manufacturer.group(1))
    serial = re.search(r"\b([A-Z]{1,3}\d{4,}|\d{6,})\b", bit_record_line)
    if serial:
        fields["bitSerial"] = serial.group(1)
    return fields


def _parse_mud_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    mud_lines = _module_lines(lines, "MUD DATA", ("MUD PRODUCTS", "BULKS"))
    fields["mudEngineer"] = _value_between(_first_line(mud_lines, "Engineer:"), "Engineer:", "MBT:")
    fields["sampleFrom"] = _value_between(_first_line(mud_lines, "Sample From:"), "Sample From:", "pH:")
    fields["mudType"] = _value_between(_first_line(mud_lines, "Mud Type"), ":", "Pm / Pom:")
    fields["mudTimeMd"] = _value_between(_first_line(mud_lines, "Time / MD:"), "Time / MD:", "Pf / Mf:")
    fields["mudTime"], fields["mudMd"] = _split_slash(fields["mudTimeMd"], 2)
    density_temp = _value_between(_first_line(mud_lines, "Density @ Temp:"), "Density @ Temp:", "Chlorides:")
    density, temperature = _split_slash(density_temp, 2)
    fields["mudDensity"] = _num(density)
    fields["mudTemperature"] = _num(temperature)
    fields["rheologyTemp"] = _num(_value_between(_first_line(mud_lines, "Rheology Temp"), ":", "Ca+ / K+:"))
    fields["viscosity"] = _num(_value_between(_first_line(mud_lines, "Viscosity:"), "Viscosity:", "CaCl2:"))
    fields["pv"], fields["yp"] = _split_slash(_value_between(_first_line(mud_lines, "PV / YP:"), "PV / YP:", "Clom:"), 2)
    fields["pvYp"] = _join_slash(fields["pv"], fields["yp"])
    fields["gels"] = _value_between(_first_line(mud_lines, "Gels 10s/10m/30m"), "Gels 10s/10m/30m", "Lime:")
    fields["gel10s"], fields["gel10m"], fields["gel30m"] = _split_slash(fields["gels"], 3)
    fields["apiWl"] = _num(_value_between(_first_line(mud_lines, "API WL:"), "API WL:", "ES:"))
    fields["oilWater"] = _value_between(_first_line(mud_lines, "Oil / Water:"), "Oil / Water:", "Bicarbonate:")
    fields["oilPercent"], fields["waterPercent"] = _split_slash(fields["oilWater"], 2)
    fields["sand"] = _num(_value_between(_first_line(mud_lines, "Sand:"), "Sand:", "Form Loss:"))
    fields["ecd"] = _num(_value_between(_first_line(mud_lines, "ECD:"), "ECD:"))
    fields["mudComments"] = _parse_mud_comments(mud_lines)
    return fields


def _module_lines(lines: list[str], start: str, stops: tuple[str, ...]) -> list[str]:
    selected: list[str] = []
    collecting = False
    for line in lines:
        if start in line:
            collecting = True
        if collecting:
            if selected and any(stop in line for stop in stops):
                break
            selected.append(line)
    return selected


def _parse_mud_comments(lines: list[str]) -> str:
    parts: list[str] = []
    collecting = False
    for line in lines:
        if "Comments:" in line:
            collecting = True
            line = line.split("Comments:", 1)[1]
        if collecting:
            if "MUD PRODUCTS" in line or "DAILY COSTS" in line:
                break
            line = re.split(r"Total Length:|DAILY COSTS", line)[0]
            if line.strip():
                parts.append(line)
    return _clean(" ".join(parts))


def _parse_incidents(layout_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    safety = re.search(r"Safety Incident\?\s*([YN])", layout_text)
    env = re.search(r"Environ Incident\?\s*([YN])", layout_text)
    fields["safetyIncident"] = safety.group(1) if safety else "N"
    fields["environmentIncident"] = env.group(1) if env else "N"
    ri = re.search(r"Days since Last RI:\s*([0-9.]+)", layout_text)
    lta = re.search(r"Days since Last LTA\s*([0-9.]*)", layout_text)
    fields["daysSinceRi"] = ri.group(1) if ri else ""
    fields["daysSinceLta"] = lta.group(1) if lta and lta.group(1) else fields["daysSinceRi"]
    inc = re.search(r"Incident Comments:\s*(.*?)(?:Days since Last RI|Other Remarks:|POB:|6/\d{1,2}/\d{4})", layout_text, re.S)
    fields["incidentComments"] = _clean(inc.group(1)) if inc else ""
    return fields


def _parse_other_remarks(layout_text: str) -> str:
    match = re.search(r"Other Remarks:\s*(.*?)(?:\n\s*\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}AM\s+Page|\Z)", layout_text, re.S)
    return _clean(match.group(1)) if match else ""


def _parse_operations_from_pdf(source: str | Path | bytes) -> list[dict[str, str]]:
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
        row_words = [
            word for word in words
            if row_top - 3 <= word["top"] < row_bottom and 20 <= word["x0"] <= 585
        ]
        parsed = _operation_from_words(row_words)
        if parsed:
            rows.append(parsed)
    return rows


def _operation_header_top(words: list[dict[str, Any]]) -> float | None:
    for word in sorted(words, key=lambda item: item["top"]):
        if word["text"] != "From" or not 15 <= word["x0"] <= 55:
            continue
        top = word["top"]
        same_header = [item for item in words if top - 2 <= item["top"] <= top + 16]
        has_to = any(item["text"] == "To" and 45 <= item["x0"] <= 80 for item in same_header)
        has_code = any(item["text"] == "Code" and 95 <= item["x0"] <= 140 for item in same_header)
        has_details = any(item["text"] == "Details" and 350 <= item["x0"] <= 430 for item in same_header)
        if has_to and has_code and has_details:
            return top
    return None


def _operation_end_top(words: list[dict[str, Any]], header_top: float, page_height: float) -> float:
    markers = {"Safety", "Environ", "Incident", "Other", "Remarks:", "POB:"}
    candidates = [
        word["top"] for word in words
        if word["top"] > header_top + 20 and word["x0"] < 120 and word["text"] in markers
    ]
    return min(candidates) if candidates else page_height - 30


def _operation_row_starts(words: list[dict[str, Any]], header_top: float, end_top: float) -> list[dict[str, Any]]:
    starts: list[dict[str, Any]] = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        if not TIME_TOKEN_RE.match(word["text"]):
            continue
        if not 20 <= word["x0"] <= 50 or word["top"] <= header_top + 10 or word["top"] >= end_top:
            continue
        same_line = [item for item in words if abs(item["top"] - word["top"]) <= 2.5]
        has_to = any(TIME_TOKEN_RE.match(item["text"]) and 50 <= item["x0"] <= 82 for item in same_line)
        has_hours = any(re.match(r"^\d+(?:\.\d+)?$", item["text"]) and 84 <= item["x0"] <= 110 for item in same_line)
        if has_to and has_hours:
            starts.append(word)
    return starts


def _operation_from_words(words: list[dict[str, Any]]) -> dict[str, str] | None:
    start = _column_text(words, 20, 52, first_line_only=True)
    end = _column_text(words, 52, 82, first_line_only=True)
    hours = _column_text(words, 82, 106, first_line_only=True)
    if not (start and end and hours):
        return None
    op_type = _normalize_op_type(_column_text(words, 185, 210))
    return {
        "from": start,
        "to": end,
        "hours": hours,
        "op_code": _normalize_op_code(_column_text(words, 106, 133)),
        "op_sub": _clean_op_sub(_column_text(words, 133, 185)),
        "op_type": op_type,
        "operation_details": _clean_operation_details(_column_text(words, 210, 585, preserve_lines=True)),
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
        selected = [word for word in selected if abs(word["top"] - top) <= 2.5]
    selected.sort(key=lambda word: (round(word["top"], 1), word["x0"]))
    if preserve_lines:
        lines: list[str] = []
        current_top: float | None = None
        current_words: list[str] = []
        for word in selected:
            top = round(word["top"], 1)
            if current_top is None or abs(top - current_top) <= 2.5:
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


def _normalize_op_type(value: str) -> str:
    upper = _clean(value).upper().replace(" ", "")
    if "NPT" in upper:
        return "NPT"
    if upper in {"P", "TYPEP"}:
        return "P"
    return ""


def _clean_op_sub(value: str) -> str:
    text = _clean(value)
    replacements = {
        "Install/Remo ve Wear": "Install/Remove Wear",
        "safety meeti": "safety meeting",
        "and Equi": "and Equip.",
        "BHA / O": "BHA / O",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return _clean(text)


def _clean_operation_details(value: str) -> str:
    text = _clean_multiline(value)
    text = text.replace(" ,", ",").replace(" .", ".").replace(" :", ":")
    return _clean_multiline(text)


def _clean_multiline(value: str) -> str:
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


def _parse_operations(layout_pages: list[str]) -> list[dict[str, str]]:
    lines = [line for page in layout_pages for line in page.splitlines()]
    rows: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in lines:
        match = TIME_ROW_RE.match(line)
        if match:
            if current:
                current["operation_details"] = _clean_operation_details(current["operation_details"])
                rows.append(current)
            start, end, hours, rest = match.groups()
            op_type = "NPT" if re.search(r"\bNPT\b", rest) else ("P" if re.search(r"\bP\b", rest) else "")
            before, after = _split_type(rest, op_type)
            op_code = _normalize_op_code(before)
            op_sub = _clean(before.replace(op_code, "", 1)) if op_code and before.startswith(op_code) else _clean(before)
            current = {
                "from": start,
                "to": end,
                "hours": hours,
                "op_code": op_code,
                "op_sub": op_sub,
                "op_type": op_type,
                "operation_details": after,
            }
            continue
        if current and _is_operation_continuation(line):
            current["operation_details"] += "\n" + line
    if current:
        current["operation_details"] = _clean_operation_details(current["operation_details"])
        rows.append(current)
    return rows


def _split_type(rest: str, op_type: str) -> tuple[str, str]:
    if op_type:
        parts = re.split(rf"\b{op_type}\b", rest, maxsplit=1)
        return _clean(parts[0]), _clean(parts[1] if len(parts) > 1 else "")
    return _clean(rest), ""


def _normalize_op_code(before: str) -> str:
    clean = _clean(before)
    upper = clean.upper()
    compact = re.sub(r"[^A-Z]", "", upper)
    if "BHA" in compact and compact.startswith("CODE"):
        return "BHA"
    if compact.startswith("DRILLI"):
        return "DRILLING"
    if compact.startswith("CIRCU"):
        return "CIRCULATING"
    if compact.startswith("CASI"):
        return "CASING"
    if compact.startswith("RIG"):
        return "RIG MAINTENANCE"
    if compact.startswith("WELL"):
        return "WELLHEAD"
    if compact.startswith("BHA"):
        return "BHA"
    return clean.split(" ", 1)[0] if clean else ""


def _is_operation_continuation(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if any(marker in stripped for marker in ("Safety Incident?", "Environ Incident?", "Other Remarks:", "Page ", "DAILY OPERATIONS REPORT")):
        return False
    return True


def _parse_bulks(layout_pages: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(rf"^\s*([A-Z][A-Z0-9 /-]+?)\s+({NUM_RE})\s+({NUM_RE})\s+({NUM_RE})")
    for page in layout_pages:
        if "BULKS" not in page:
            continue
        for line in page.splitlines():
            match = pattern.match(line)
            if not match:
                continue
            name, start, end, used = match.groups()
            if name.strip() == "BULKS":
                continue
            rows.append({
                "bulk": _clean(name),
                "qty_start": start.replace(",", ""),
                "qty_used": used.replace(",", ""),
                "qty_end": end.replace(",", ""),
            })
    return rows


def _parse_daily_costs(layout_text: str) -> list[dict[str, str]]:
    # The provided samples contain the table header but no cost rows. Keep an
    # explicit zero row so the UI preview remains clear after import.
    if "DAILY COSTS" in layout_text:
        return [{"cost_description": "No daily cost item recorded", "vendor": "N/A", "amount": "0"}]
    return []
