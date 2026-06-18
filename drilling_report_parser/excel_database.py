from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet


REPORT_TYPES = {"drilling", "completion", "workover", "move"}

BASE_COLUMNS = [
    "record_id",
    "report_type",
    "source_file",
    "parser",
    "reportDate",
    "reportNo",
    "wellbore",
    "rig",
    "status",
    "validation_status",
    "validation_warnings",
    "created_at",
    "updated_at",
]

COMMON_FIELD_COLUMNS = [
    "record_id",
    "event",
    "reportDate",
    "reportNo",
    "wellbore",
    "rig",
    "primaryReason",
    "afeNumber",
    "refDatum",
    "currentOps",
    "summary24h",
    "forecast24h",
    "otherRemarks",
]

DRILLING_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "todayMd",
    "prevMd",
    "progress",
    "rotHrsToday",
    "lastCasing",
    "lastCasingSize",
    "lastCasingDepth",
    "nextCasing",
    "nextCasingSize",
    "nextCasingDepth",
    "formTestEmw",
    "lastBopPressTest",
    "pumpRate",
    "pumpPress",
    "stringWeightUpDown",
    "torqueOnBottom",
    "mudEngineer",
    "sampleFrom",
    "mudType",
    "mudTime",
    "mudMd",
    "mudDensity",
    "mudTemperature",
    "rheologyTemp",
    "viscosity",
    "pv",
    "yp",
    "gel10s",
    "gel10m",
    "gel30m",
    "apiWl",
    "oilPercent",
    "waterPercent",
    "sand",
    "ecd",
    "mudComments",
    "bitNo",
    "bitSize",
    "bitManufacturer",
    "bitSerial",
    "bhaNo",
    "bhaMdIn",
    "bhaMdOut",
    "bhaTotalLength",
    "safetyIncident",
    "environmentIncident",
    "daysSinceRi",
    "daysSinceLta",
    "incidentComments",
]

COMPLETION_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "description",
    "operationStartDate",
    "afeCost",
    "dailyCost",
    "cumulativeCost",
    "supervisor1",
    "supervisor2",
    "engineer",
    "pamEngineer",
    "geologist",
    "totalPersonnel",
    "safetyComments",
]

WORKOVER_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "workoverNo",
    "description",
    "operationStartDate",
    "afeCost",
    "dailyCost",
    "cumulativeCost",
    "supervisor1",
    "supervisor2",
    "engineer",
    "pamEngineer",
    "geologist",
    "totalPersonnel",
    "safetyComments",
]

MOVE_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "todayMd",
    "prevMd",
    "progress",
    "rotHrsToday",
    "groundElev",
    "afeMdDays",
    "wellborePrefix",
]

ROW_COLUMNS = {
    "operations": ["from", "to", "hours", "op_code", "op_sub", "op_type", "operation_details"],
    "bulks": ["bulk", "qty_start", "qty_used", "qty_end"],
    "daily_costs": ["cost_description", "vendor", "amount"],
    "survey_data": ["md", "incl", "azi", "tvd", "vse", "ns", "dls", "build"],
    "bha_components": ["component", "od", "id", "joints", "length"],
    "perforation_intervals": [
        "formation",
        "top_md",
        "base_md",
        "length",
        "density",
        "charges",
        "phase",
        "penetration",
        "diameter",
        "date",
        "status",
        "comments",
    ],
    "mud_products": ["product", "unit", "received", "used", "returned", "ending"],
}

REPORT_TABLES = {
    "drilling": {
        "field_sheet": "drilling_fields",
        "field_columns": DRILLING_FIELD_COLUMNS,
        "multi": {
            "survey_data": "drilling_survey",
            "bha_components": "drilling_bha",
            "operations": "drilling_operations",
            "daily_costs": "drilling_costs",
            "bulks": "drilling_bulks",
        },
    },
    "completion": {
        "field_sheet": "completion_fields",
        "field_columns": COMPLETION_FIELD_COLUMNS,
        "multi": {
            "operations": "completion_operations",
            "bulks": "completion_bulks",
            "daily_costs": "completion_costs",
            "mud_products": "completion_mud_products",
            "perforation_intervals": "completion_intervals",
        },
    },
    "workover": {
        "field_sheet": "workover_fields",
        "field_columns": WORKOVER_FIELD_COLUMNS,
        "multi": {
            "operations": "workover_operations",
            "bulks": "workover_bulks",
            "daily_costs": "workover_costs",
            "mud_products": "workover_mud_products",
            "perforation_intervals": "workover_intervals",
        },
    },
    "move": {
        "field_sheet": "move_fields",
        "field_columns": MOVE_FIELD_COLUMNS,
        "multi": {
            "operations": "move_operations",
        },
    },
}


def initialize_database(database_path: str | Path) -> Path:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = _load_or_create_workbook(path)
    _ensure_schema(workbook)
    _format_workbook(workbook)
    workbook.save(path)
    return path


def save_report_payload(
    database_path: str | Path,
    payload: dict[str, Any],
    report_type: str,
    *,
    source_file: str = "",
) -> dict[str, Any]:
    report_type = _normalize_report_type(report_type)
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    workbook = _load_or_create_workbook(path)
    _ensure_schema(workbook)

    now = _now()
    fields = payload.get("report_fields", {}) or {}
    metadata = payload.get("metadata", {}) or {}
    record_id = str(metadata.get("record_id") or payload.get("record_id") or _natural_record_id(report_type, fields) or _generated_record_id(report_type, now))
    source_file = source_file or str(metadata.get("source_file") or "")

    existing = _record_index(workbook["records"]).get(record_id, {})
    created_at = existing.get("created_at") or now
    _replace_record_rows(workbook, report_type, record_id)

    _append_row(
        workbook["records"],
        BASE_COLUMNS,
        {
            "record_id": record_id,
            "report_type": report_type,
            "source_file": source_file,
            "parser": metadata.get("parser", ""),
            "reportDate": fields.get("reportDate", ""),
            "reportNo": fields.get("reportNo", ""),
            "wellbore": fields.get("wellbore", ""),
            "rig": fields.get("rig", ""),
            "status": metadata.get("status", "parsed"),
            "validation_status": metadata.get("validation_status", "ok"),
            "validation_warnings": metadata.get("validation_warnings", ""),
            "created_at": created_at,
            "updated_at": now,
        },
    )

    table_info = REPORT_TABLES[report_type]
    _append_row(workbook[table_info["field_sheet"]], table_info["field_columns"], {"record_id": record_id, **fields})
    for module_name, sheet_name in table_info["multi"].items():
        columns = ["record_id", "row_no", *ROW_COLUMNS[module_name]]
        for row_no, row in enumerate(payload.get(module_name, []) or [], start=1):
            _append_row(workbook[sheet_name], columns, {"record_id": record_id, "row_no": row_no, **(row or {})})

    _format_workbook(workbook)
    workbook.save(path)
    return {"record_id": record_id, "database_path": str(path), "updated_at": now}


def load_report_payload(database_path: str | Path, record_id: str) -> dict[str, Any]:
    path = Path(database_path)
    if not path.exists():
        raise FileNotFoundError(path)
    workbook = load_workbook(path)
    record = _record_index(workbook["records"]).get(record_id)
    if not record:
        raise KeyError(record_id)
    report_type = _normalize_report_type(str(record.get("report_type", "")))
    table_info = REPORT_TABLES[report_type]
    fields = _first_matching_row(workbook[table_info["field_sheet"]], record_id)
    payload: dict[str, Any] = {
        "metadata": {
            "record_id": record_id,
            "report_type": report_type,
            "source_file": record.get("source_file", ""),
            "parser": record.get("parser", ""),
        },
        "report_fields": fields,
    }
    for module_name, sheet_name in table_info["multi"].items():
        payload[module_name] = _matching_rows(workbook[sheet_name], record_id)
    return payload


def list_records(database_path: str | Path) -> list[dict[str, str]]:
    path = Path(database_path)
    if not path.exists():
        return []
    workbook = load_workbook(path, read_only=True, data_only=True)
    records = list(_record_index(workbook["records"]).values())
    records.sort(key=lambda record: (record.get("reportDate", ""), record.get("updated_at", "")), reverse=True)
    return records


def _load_or_create_workbook(path: Path) -> Workbook:
    if path.exists():
        return load_workbook(path)
    workbook = Workbook()
    workbook.active.title = "records"
    return workbook


def _ensure_schema(workbook: Workbook) -> None:
    _ensure_sheet(workbook, "records", BASE_COLUMNS)
    for report_type, table_info in REPORT_TABLES.items():
        _ensure_sheet(workbook, table_info["field_sheet"], table_info["field_columns"])
        for module_name, sheet_name in table_info["multi"].items():
            _ensure_sheet(workbook, sheet_name, ["record_id", "row_no", *ROW_COLUMNS[module_name]])


def _ensure_sheet(workbook: Workbook, name: str, columns: list[str]) -> Worksheet:
    worksheet = workbook[name] if name in workbook.sheetnames else workbook.create_sheet(name)
    if worksheet.max_row == 1 and all(cell.value is None for cell in worksheet[1]):
        for index, column in enumerate(columns, start=1):
            worksheet.cell(row=1, column=index, value=column)
    else:
        existing = [cell.value for cell in worksheet[1]]
        for column in columns:
            if column not in existing:
                worksheet.cell(row=1, column=len(existing) + 1, value=column)
                existing.append(column)
    return worksheet


def _replace_record_rows(workbook: Workbook, report_type: str, record_id: str) -> None:
    sheets = ["records", REPORT_TABLES[report_type]["field_sheet"], *REPORT_TABLES[report_type]["multi"].values()]
    for sheet_name in sheets:
        worksheet = workbook[sheet_name]
        for row_number in range(worksheet.max_row, 1, -1):
            if str(worksheet.cell(row=row_number, column=1).value or "") == record_id:
                worksheet.delete_rows(row_number)


def _append_row(worksheet: Worksheet, columns: list[str], values: dict[str, Any]) -> None:
    headers = _headers(worksheet)
    for column in columns:
        if column not in headers:
            worksheet.cell(row=1, column=len(headers) + 1, value=column)
            headers.append(column)
    worksheet.append([_cell_value(values.get(column, "")) for column in headers])


def _cell_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _record_index(worksheet: Worksheet) -> dict[str, dict[str, str]]:
    headers = _headers(worksheet)
    rows: dict[str, dict[str, str]] = {}
    for raw in worksheet.iter_rows(min_row=2, values_only=True):
        row = {headers[index]: _cell_value(value) for index, value in enumerate(raw) if index < len(headers)}
        record_id = row.get("record_id", "")
        if record_id:
            rows[record_id] = row
    return rows


def _first_matching_row(worksheet: Worksheet, record_id: str) -> dict[str, str]:
    rows = _matching_rows(worksheet, record_id)
    if not rows:
        return {}
    rows[0].pop("row_no", None)
    return rows[0]


def _matching_rows(worksheet: Worksheet, record_id: str) -> list[dict[str, str]]:
    headers = _headers(worksheet)
    rows: list[dict[str, str]] = []
    for raw in worksheet.iter_rows(min_row=2, values_only=True):
        row = {headers[index]: _cell_value(value) for index, value in enumerate(raw) if index < len(headers)}
        if row.get("record_id") == record_id:
            row.pop("record_id", None)
            rows.append(row)
    rows.sort(key=lambda item: int(item.get("row_no") or 0))
    for row in rows:
        row.pop("row_no", None)
    return rows


def _headers(worksheet: Worksheet) -> list[str]:
    return [_cell_value(cell.value) for cell in worksheet[1]]


def _natural_record_id(report_type: str, fields: dict[str, Any]) -> str:
    parts = [report_type, fields.get("wellbore", ""), fields.get("reportDate", ""), fields.get("reportNo", "")]
    if not all(str(part or "").strip() for part in parts):
        return ""
    return ":".join(_slug(str(part)) for part in parts)


def _generated_record_id(report_type: str, timestamp: str) -> str:
    return f"{report_type}:{_slug(timestamp)}"


def _slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return text.strip("-") or "unknown"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_report_type(report_type: str) -> str:
    normalized = (report_type or "").strip().lower()
    if normalized not in REPORT_TYPES:
        raise ValueError(f"Unsupported report_type: {report_type}")
    return normalized


def _format_workbook(workbook: Workbook) -> None:
    header_fill = PatternFill("solid", fgColor="D9EAF7")
    for worksheet in workbook.worksheets:
        worksheet.freeze_panes = "A2"
        for cell in worksheet[1]:
            cell.font = Font(bold=True)
            cell.fill = header_fill
        widths: dict[int, int] = {}
        for row in worksheet.iter_rows():
            for cell in row:
                value = _cell_value(cell.value)
                widths[cell.column] = min(max(widths.get(cell.column, 10), len(value) + 2), 48)
        for column, width in widths.items():
            worksheet.column_dimensions[worksheet.cell(row=1, column=column).column_letter].width = width
