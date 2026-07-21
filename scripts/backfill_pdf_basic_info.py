from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from drilling_report_parser.completion_pdf_parser import parse_completion_pdf_daily_report
from drilling_report_parser.mysql_database import _connect
from drilling_report_parser.pdf_report_parser import parse_pdf_daily_report
from drilling_report_parser.workover_pdf_parser import parse_workover_pdf_daily_report


SOURCE_PDF_DIR = ROOT / "outputs" / "source_pdfs"

Parser = Callable[[Path], dict[str, Any]]

PARSERS: dict[str, Parser] = {
    "drilling": parse_pdf_daily_report,
    "move": parse_pdf_daily_report,
    "completion": parse_completion_pdf_daily_report,
    "workover": parse_workover_pdf_daily_report,
}

BACKFILL_FIELDS = {
    "drilling": (
        "wellboreNo", "dfs", "groundElev", "dailyCost", "cumulativeCost", "afeCost",
        "avgRopSlide", "avgRopRot", "supervisor1", "supervisor2", "engineer",
        "pamEngineer", "geologist", "totalPersonnel",
    ),
    "move": (
        "wellboreNo", "dfs", "groundElev", "dailyCost", "cumulativeCost", "afeCost",
        "avgRopSlide", "avgRopRot", "supervisor1", "supervisor2", "engineer",
        "pamEngineer", "geologist", "totalPersonnel",
    ),
    "completion": (
        "completionNo", "wellboreNo", "groundElev", "dol", "dfs", "rigContractName",
    ),
    "workover": (
        "wellboreNo", "groundElev", "dol", "dfs", "rigContractName",
    ),
}


def _json_object(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(str(value or "{}"))
    except json.JSONDecodeError:
        return {}
    return dict(parsed) if isinstance(parsed, dict) else {}


def _is_valid_number(value: object) -> bool:
    return bool(re.fullmatch(r"[-+]?\d+(?:\.\d+)?", str(value or "").replace(",", "").strip()))


def backfill(*, apply_changes: bool) -> dict[str, int]:
    result = {"pdf_count": 0, "record_count": 0, "updated_count": 0, "field_count": 0, "error_count": 0}
    with _connect() as connection:
        with connection.cursor() as cursor:
            for source_path in sorted(SOURCE_PDF_DIR.glob("*.pdf")):
                source_kind = source_path.stem.split(":", 1)[0]
                parser = PARSERS.get(source_kind)
                if parser is None:
                    continue
                result["pdf_count"] += 1
                try:
                    parsed_fields = parser(source_path).get("report_fields", {})
                except Exception:
                    result["error_count"] += 1
                    continue
                if not isinstance(parsed_fields, dict):
                    result["error_count"] += 1
                    continue
                record_id = source_path.stem
                cursor.execute("SELECT fields_json FROM dpr_report_field WHERE record_id=%s", (record_id,))
                row = cursor.fetchone()
                if not row:
                    continue
                result["record_count"] += 1
                existing_fields = _json_object(row.get("fields_json"))
                changes: dict[str, Any] = {}
                for field_name in BACKFILL_FIELDS[source_kind]:
                    parsed_value = parsed_fields.get(field_name, "")
                    if str(parsed_value or "").strip() == "":
                        continue
                    existing_value = existing_fields.get(field_name, "")
                    should_replace = str(existing_value or "").strip() == ""
                    if field_name == "groundElev" and not _is_valid_number(existing_value):
                        should_replace = True
                    if should_replace:
                        changes[field_name] = parsed_value
                if not changes:
                    continue
                result["updated_count"] += 1
                result["field_count"] += len(changes)
                if not apply_changes:
                    continue
                existing_fields.update(changes)
                cursor.execute(
                    "UPDATE dpr_report_field SET fields_json=%s WHERE record_id=%s",
                    (json.dumps(existing_fields, ensure_ascii=False, separators=(",", ":")), record_id),
                )
                if source_kind in {"drilling", "move"} and "groundElev" in changes:
                    cursor.execute(
                        """
                        UPDATE dpr_drilling_report dr
                        JOIN dpr_report report ON report.id=dr.daily_report_id
                        SET dr.ground_elevation_ft=%s
                        WHERE report.record_id=%s
                        """,
                        (str(changes["groundElev"]).replace(",", ""), record_id),
                    )
        if apply_changes:
            connection.commit()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill missing PDF header/basic information fields.")
    parser.add_argument("--apply", action="store_true", help="Write missing fields to MySQL; default is dry-run.")
    args = parser.parse_args()
    result = backfill(apply_changes=args.apply)
    mode = "applied" if args.apply else "dry-run"
    print(mode, json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
