from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from drilling_report_parser import excel_database, mysql_database  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Import existing Excel report database into MySQL.")
    parser.add_argument("--excel", default=str(ROOT / "outputs" / "report_database.xlsx"), help="Path to report_database.xlsx")
    parser.add_argument("--report-type", default="", choices=["", "drilling", "completion", "workover", "move"], help="Optional report type filter")
    args = parser.parse_args()

    excel_path = Path(args.excel)
    if not excel_path.exists():
        print(f"Excel file not found: {excel_path}", file=sys.stderr)
        return 1

    mysql_database.initialize_database()
    records = excel_database.list_records(excel_path)
    if args.report_type:
        records = [record for record in records if record.get("report_type") == args.report_type]

    imported = 0
    failed: list[tuple[str, str]] = []
    for record in records:
        record_id = str(record.get("record_id", "") or "")
        report_type = str(record.get("report_type", "") or "")
        if not record_id or not report_type:
            continue
        try:
            payload = excel_database.load_report_payload(excel_path, record_id)
            mysql_database.save_report_payload(excel_path, payload, report_type, source_file=str(record.get("source_file", "") or ""))
            imported += 1
        except Exception as exc:  # Keep importing the rest and report a useful summary.
            failed.append((record_id, str(exc)))

    print(f"Imported/updated {imported} report records into MySQL.")
    if failed:
        print(f"Failed {len(failed)} records:", file=sys.stderr)
        for record_id, error in failed[:20]:
            print(f"- {record_id}: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
