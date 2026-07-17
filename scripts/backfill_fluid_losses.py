from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from drilling_report_parser.mysql_database import _connect, initialize_database  # noqa: E402
from drilling_report_parser.pdf_report_parser import parse_pdf_daily_report  # noqa: E402


DEFAULT_SOURCE_DIR = ROOT / "outputs" / "source_pdfs"


def backfill(source_dir: Path) -> dict[str, int]:
    initialize_database()
    counts = {"reports": 0, "updated": 0, "missing_pdf": 0, "parse_failed": 0}

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.record_id, f.id AS daily_report_id
                FROM dpr_report_record r
                INNER JOIN dpr_report f ON f.record_id=r.record_id
                WHERE r.report_type='drilling'
                ORDER BY r.record_id
                """
            )
            reports = cursor.fetchall()
            counts["reports"] = len(reports)

            for report in reports:
                record_id = str(report["record_id"])
                pdf_path = source_dir / f"{record_id}.pdf"
                if not pdf_path.exists():
                    counts["missing_pdf"] += 1
                    continue
                try:
                    rows = parse_pdf_daily_report(pdf_path).get("fluid_losses", [])
                except Exception:
                    counts["parse_failed"] += 1
                    continue

                cursor.execute(
                    "DELETE FROM dpr_report_row WHERE record_id=%s AND module_name='fluid_losses'",
                    (record_id,),
                )
                cursor.execute(
                    "DELETE FROM dpr_drilling_fluid_loss WHERE daily_report_id=%s",
                    (report["daily_report_id"],),
                )
                for row_no, row in enumerate(rows, start=1):
                    raw = json.dumps(row, ensure_ascii=False, sort_keys=True)
                    source_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
                    cursor.execute(
                        """
                        INSERT INTO dpr_report_row (record_id, module_name, row_no, row_json)
                        VALUES (%s, 'fluid_losses', %s, %s)
                        """,
                        (record_id, row_no, raw),
                    )
                    cursor.execute(
                        """
                        INSERT INTO dpr_drilling_fluid_loss
                          (daily_report_id, source_row_no, injected_volume_bbl,
                           returned_volume_bbl, source_hash, created_by, updated_by)
                        VALUES (%s, %s, %s, %s, %s, 'fluid-loss-backfill', 'fluid-loss-backfill')
                        """,
                        (
                            report["daily_report_id"],
                            row_no,
                            row.get("injected_volume_bbl") or None,
                            row.get("returned_volume_bbl") or None,
                            source_hash,
                        ),
                    )
                counts["updated"] += 1
        connection.commit()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill drilling fluid-loss facts from saved source PDFs.")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    args = parser.parse_args()
    print(json.dumps(backfill(args.source_dir), ensure_ascii=False))


if __name__ == "__main__":
    main()
