#!/usr/bin/env python3
"""Load artifact-tool-normalized HSSE workbook rows and seed labelled demo gaps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from drilling_report_parser.hsse_service import import_hsse_records, seed_hsse_simulated_records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", type=Path)
    parser.add_argument("--month", default="2026-06")
    parser.add_argument("--simulated-per-team", type=int, default=3)
    args = parser.parse_args()

    payload = json.loads(args.json_path.read_text(encoding="utf-8"))
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise SystemExit("normalized JSON does not contain a records list")

    imported = import_hsse_records(
        records,
        actor="excel-import",
        source_file=str(payload.get("source_file") or ""),
    )
    simulated = seed_hsse_simulated_records(
        month=args.month,
        records_per_team=max(args.simulated_per_team, 0),
    )
    print(json.dumps({"imported": imported, "simulated": simulated}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
