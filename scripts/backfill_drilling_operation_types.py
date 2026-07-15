from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from drilling_report_parser.mysql_database import load_report_payload, save_report_payload  # noqa: E402
from drilling_report_parser.pdf_report_parser import parse_pdf_daily_report  # noqa: E402


VALID_TYPES = {"P", "SC", "NPT"}
DEFAULT_SOURCE_DIR = ROOT / "outputs" / "source_pdfs"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Backfill missing drilling operation P/SC/NPT values from saved source PDFs."
    )
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE_DIR))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    summary: dict[str, Any] = {
        "scanned_pdfs": 0,
        "updated_records": 0,
        "updated_rows": 0,
        "skipped_records": [],
        "changes": [],
        "dry_run": bool(args.dry_run),
    }
    for pdf_path in sorted(Path(args.source_dir).glob("drilling:*.pdf")):
        summary["scanned_pdfs"] += 1
        record_id = pdf_path.stem
        try:
            payload = load_report_payload(None, record_id)
            parsed = parse_pdf_daily_report(pdf_path)
        except Exception as exc:
            summary["skipped_records"].append({"record_id": record_id, "reason": str(exc)})
            continue

        stored_rows = payload.get("operations", [])
        parsed_rows = parsed.get("operations", [])
        if not isinstance(stored_rows, list) or not isinstance(parsed_rows, list) or len(stored_rows) != len(parsed_rows):
            summary["skipped_records"].append({
                "record_id": record_id,
                "reason": f"operation row count differs: stored={len(stored_rows)} parsed={len(parsed_rows)}",
            })
            continue

        changes: list[dict[str, object]] = []
        for row_no, (stored, source) in enumerate(zip(stored_rows, parsed_rows), start=1):
            if not isinstance(stored, dict) or not isinstance(source, dict):
                continue
            if not _same_activity(stored, source):
                summary["skipped_records"].append({
                    "record_id": record_id,
                    "reason": f"row {row_no} activity identity differs",
                })
                changes = []
                break
            stored_type = str(stored.get("confirmed_op_type") or stored.get("op_type") or "").strip().upper()
            source_type = str(source.get("op_type") or "").strip().upper()
            if not stored_type and source_type in VALID_TYPES:
                stored["op_type"] = source_type
                changes.append({"row_no": row_no, "from": stored.get("from", ""), "to": stored.get("to", ""), "op_type": source_type})

        if not changes:
            continue
        summary["updated_records"] += 1
        summary["updated_rows"] += len(changes)
        summary["changes"].append({"record_id": record_id, "rows": changes})
        if not args.dry_run:
            metadata = payload.get("metadata", {}) if isinstance(payload.get("metadata"), dict) else {}
            save_report_payload(
                None,
                payload,
                "drilling",
                source_file=str(metadata.get("source_file", "") or pdf_path.name),
                invalidate_translations=False,
            )

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _same_activity(stored: dict[str, Any], source: dict[str, Any]) -> bool:
    return all(_time_key(stored.get(key)) == _time_key(source.get(key)) for key in ("from", "to"))


def _time_key(value: object) -> tuple[int, int] | str:
    text = str(value or "").strip()
    parts = text.split(":", 1)
    if len(parts) == 2 and all(part.isdigit() for part in parts):
        return int(parts[0]), int(parts[1])
    return text


if __name__ == "__main__":
    raise SystemExit(main())
