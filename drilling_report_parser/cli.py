from __future__ import annotations

import argparse
from pathlib import Path

from .parser import parse_excel_report, write_structured_workbook


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse Ecuador drilling daily report Excel files into structured sheets."
    )
    parser.add_argument("input", help="Path to the source .xlsx/.xlsm report exported from the drilling template.")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the structured .xlsx output. Defaults to outputs/<input>_structured.xlsx",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file does not exist: {input_path}")

    output_path = Path(args.output).expanduser().resolve() if args.output else _default_output(input_path)
    result = parse_excel_report(input_path)
    write_structured_workbook(result, output_path)
    print(f"Structured workbook: {output_path}")
    print(f"Fields: {len(result.fields)}")
    for table_name, rows in result.tables.items():
        print(f"{table_name}: {len(rows)} rows")
    if result.warnings:
        print(f"Warnings: {len(result.warnings)}; see parse_warnings sheet.")


def _default_output(input_path: Path) -> Path:
    return Path.cwd() / "outputs" / f"{input_path.stem}_structured.xlsx"


if __name__ == "__main__":
    main()
