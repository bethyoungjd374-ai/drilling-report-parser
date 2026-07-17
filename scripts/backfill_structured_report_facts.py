from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from drilling_report_parser.mysql_database import _connect, initialize_database  # noqa: E402
from drilling_report_parser.pdf_report_parser import parse_pdf_daily_report  # noqa: E402
from drilling_report_parser.report_normalization_service import synchronize_structured_report_facts  # noqa: E402


DEFAULT_SOURCE_DIR = ROOT / "outputs" / "source_pdfs"


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill typed facts from the immutable JSON report audit layer.")
    parser.add_argument("--batch-code", default="structured-report-facts-v2")
    parser.add_argument("--actor", default="migration")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--enrich-drilling-source-pdfs", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    initialize_database()
    with _connect() as connection:
        try:
            with connection.cursor() as cursor:
                summary = backfill(
                    cursor,
                    batch_code=args.batch_code,
                    actor=args.actor,
                    source_dir=args.source_dir if args.enrich_drilling_source_pdfs else None,
                )
            if args.dry_run:
                connection.rollback()
                summary["dry_run"] = True
            else:
                connection.commit()
        except Exception:
            connection.rollback()
            raise
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def backfill(
    cursor: Any,
    *,
    batch_code: str,
    actor: str,
    source_dir: Path | None = None,
) -> dict[str, Any]:
    cursor.execute(
        "INSERT INTO migration_batch "
        "(batch_code,source_type,source_path,batch_status,started_at,created_by) "
        "VALUES (%s,'MYSQL','dpr_report_field/dpr_report_row','RUNNING',NOW(),%s) "
        "ON DUPLICATE KEY UPDATE batch_status='RUNNING',started_at=NOW(),completed_at=NULL,rolled_back_at=NULL",
        (batch_code, actor),
    )
    cursor.execute("SELECT id FROM migration_batch WHERE batch_code=%s", (batch_code,))
    batch_id = int((cursor.fetchone() or {})["id"])

    cursor.execute(
        "SELECT d.id AS daily_report_id,r.record_id,r.report_type,f.fields_json "
        "FROM dpr_report d JOIN dpr_report_record r ON r.record_id=d.record_id "
        "JOIN dpr_report_field f ON f.record_id=r.record_id ORDER BY r.report_date,r.record_id"
    )
    reports = list(cursor.fetchall() or [])
    counters = {
        "reports": 0,
        "drilling": 0,
        "completion": 0,
        "workover": 0,
        "move": 0,
        "source_pdfs_found": 0,
        "source_pdfs_missing": 0,
        "source_pdfs_failed": 0,
        "torque_off_bottom_enriched": 0,
        "report_number_enriched": 0,
        "survey_east_west_rows_enriched": 0,
    }
    for report in reports:
        record_id = str(report.get("record_id", "") or "")
        report_type = str(report.get("report_type", "") or "")
        fields = _json_value(report.get("fields_json"), {})
        payload: dict[str, Any] = {"report_fields": fields}
        cursor.execute(
            "SELECT module_name,row_json FROM dpr_report_row WHERE record_id=%s ORDER BY module_name,row_no",
            (record_id,),
        )
        for row in cursor.fetchall() or []:
            payload.setdefault(str(row.get("module_name", "") or ""), []).append(_json_value(row.get("row_json"), {}))
        if source_dir is not None and report_type == "drilling":
            _enrich_drilling_from_source_pdf(
                cursor,
                source_dir=source_dir,
                record_id=record_id,
                fields=fields,
                payload=payload,
                counters=counters,
            )
        synchronize_structured_report_facts(
            cursor,
            daily_report_id=int(report["daily_report_id"]),
            report_type=report_type,
            fields=fields,
            payload=payload,
            actor=actor,
        )
        source_locator = f"mysql:report:{record_id}"
        locator_hash = hashlib.sha256(source_locator.encode("utf-8")).hexdigest()
        result = {"daily_report_id": int(report["daily_report_id"]), "report_type": report_type}
        cursor.execute(
            "INSERT INTO migration_entry "
            "(batch_id,source_locator,source_locator_hash,entity_type,entity_id,new_value_json,entry_status) "
            "VALUES (%s,%s,%s,'structured_fact',%s,%s,'APPLIED') "
            "ON DUPLICATE KEY UPDATE entity_id=VALUES(entity_id),new_value_json=VALUES(new_value_json),entry_status='APPLIED'",
            (batch_id, source_locator, locator_hash, record_id, json.dumps(result, ensure_ascii=False)),
        )
        counters["reports"] += 1
        if report_type in counters:
            counters[report_type] += 1

    cursor.execute(
        "UPDATE migration_batch SET batch_status='COMPLETED',summary_json=%s,completed_at=NOW() WHERE id=%s",
        (json.dumps(counters, ensure_ascii=False), batch_id),
    )
    return {"batch_id": batch_id, "batch_code": batch_code, **counters}


def _enrich_drilling_from_source_pdf(
    cursor: Any,
    *,
    source_dir: Path,
    record_id: str,
    fields: dict[str, Any],
    payload: dict[str, Any],
    counters: dict[str, int],
) -> None:
    pdf_path = source_dir / f"{record_id}.pdf"
    if not pdf_path.exists():
        counters["source_pdfs_missing"] += 1
        return
    counters["source_pdfs_found"] += 1
    try:
        parsed = parse_pdf_daily_report(pdf_path)
    except Exception:
        counters["source_pdfs_failed"] += 1
        return

    source_fields = parsed.get("report_fields", {}) or {}
    fields_changed = False
    torque_off_bottom = str(source_fields.get("torqueOffBottom", "") or "").strip()
    if torque_off_bottom and torque_off_bottom != str(fields.get("torqueOffBottom", "") or "").strip():
        fields["torqueOffBottom"] = torque_off_bottom
        fields_changed = True
        counters["torque_off_bottom_enriched"] += 1

    source_report_no = str(source_fields.get("reportNo", "") or "").strip()
    target_report_no = str(fields.get("reportNo", "") or "").strip()
    if not target_report_no and re.fullmatch(r"\d+", source_report_no):
        fields["reportNo"] = source_report_no
        fields_changed = True
        counters["report_number_enriched"] += 1
        cursor.execute(
            "UPDATE dpr_report_record SET report_no=%s WHERE record_id=%s AND report_no=''",
            (source_report_no, record_id),
        )

    if fields_changed:
        cursor.execute(
            "UPDATE dpr_report_field SET fields_json=%s WHERE record_id=%s",
            (json.dumps(fields, ensure_ascii=False), record_id),
        )

    source_surveys = [row for row in (parsed.get("survey_data", []) or []) if isinstance(row, dict)]
    target_surveys = [row for row in (payload.get("survey_data", []) or []) if isinstance(row, dict)]
    for row_no, (target, source) in enumerate(zip(target_surveys, source_surveys), start=1):
        east_west = str(source.get("ew", "") or "").strip()
        if not east_west or east_west == str(target.get("ew", "") or "").strip():
            continue
        target["ew"] = east_west
        counters["survey_east_west_rows_enriched"] += 1
        cursor.execute(
            "UPDATE dpr_report_row SET row_json=%s WHERE record_id=%s AND module_name='survey_data' AND row_no=%s",
            (json.dumps(target, ensure_ascii=False), record_id, row_no),
        )


def _json_value(value: object, default: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value or ""))
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


if __name__ == "__main__":
    raise SystemExit(main())
