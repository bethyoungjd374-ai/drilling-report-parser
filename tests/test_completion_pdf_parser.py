from __future__ import annotations

import unittest
from pathlib import Path

import pdfplumber

from drilling_report_parser.completion_pdf_parser import (
    _parse_operation_page,
    _ref_datum_number,
    parse_completion_pdf_daily_report,
)


SAMPLE_DIRS = (
    Path("/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/华为ai任务资料/完井日报"),
    Path("/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/日报资料/完井"),
    Path("/Users/wujianhui/Documents/1、Work/厄瓜多尔资料/华为ai任务资料/完井日报"),
)


def sample_pdf(name: str) -> Path:
    for sample_dir in SAMPLE_DIRS:
        matches = sorted(sample_dir.rglob(name)) if sample_dir.exists() else []
        if matches:
            return matches[0]
    return SAMPLE_DIRS[0] / name


class CompletionPdfParserTest(unittest.TestCase):
    def test_ref_datum_keeps_only_numeric_value(self) -> None:
        self.assertEqual(_ref_datum_number("ORIGINAL KB @987.55ft"), "987.55")
        self.assertEqual(_ref_datum_number("ORIGINAL KB @1,045.17ft"), "1045.17")

    def test_parse_schas_completion_sample(self) -> None:
        pdf = sample_pdf("06112026-SCHAS-513-SIN-219-PEC-007-V1R1 REPORTE DIARIO DE COMPLETACIÓN.pdf")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")
        payload = parse_completion_pdf_daily_report(pdf)
        fields = payload["report_fields"]
        self.assertEqual(fields["wellbore"], "SCHAS-513")
        self.assertEqual(fields["reportNo"], "7")
        self.assertEqual(fields["rig"], "SINOPEC 219")
        self.assertEqual(fields["supervisor1"], "ROBERTO OCHOA")
        self.assertEqual(fields["totalPersonnel"], "88.00")
        self.assertEqual(len(payload["operations"]), 9)
        self.assertEqual(payload["operations"][0]["op_code"], "PERFORATING")
        self.assertEqual(payload["operations"][0]["op_sub"], "Tripping")
        self.assertEqual(payload["operations"][0]["op_type"], "P")
        self.assertTrue(all(row["op_type"] in {"P", "SC", "NPT"} for row in payload["operations"]))
        self.assertFalse(any("PERFORAT" in row["hours"] for row in payload["operations"]))
        self.assertEqual(payload["bulks"][0]["bulk"], "DIESEL - RIG")
        self.assertEqual(payload["bulks"][0]["qty_used"], "1677.00")
        self.assertNotIn("daily_costs", payload)

    def test_parse_lobc_completion_sample(self) -> None:
        pdf = sample_pdf("06112026-LOBC-010-SIN-127-PEC-008-V1R1-REPORTE DIARIO DE COMPLETACIÓN.pdf")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")
        payload = parse_completion_pdf_daily_report(pdf)
        fields = payload["report_fields"]
        self.assertEqual(fields["wellbore"], "LOBC-010")
        self.assertEqual(fields["reportNo"], "8")
        self.assertEqual(fields["rig"], "SINOPEC 127")
        self.assertEqual(fields["engineer"], "MONICA QUISNANCELA")
        self.assertEqual(len(payload["operations"]), 5)
        self.assertEqual(payload["operations"][0]["op_code"], "STIMULATION")
        self.assertEqual(payload["operations"][0]["hours"], "11.00")
        self.assertEqual(payload["operations"][0]["op_type"], "P")
        self.assertTrue(all(row["op_type"] in {"P", "SC", "NPT"} for row in payload["operations"]))
        self.assertEqual(len(payload["bulks"]), 1)
        self.assertEqual(len(payload["perforation_intervals"]), 1)
        self.assertNotIn("daily_costs", payload)
        interval = payload["perforation_intervals"][0]
        self.assertEqual(interval["formation"], "ARENISCA T")
        self.assertEqual(interval["top_md"], "10991.00")
        self.assertEqual(interval["base_md"], "11023.00")
        self.assertEqual(interval["status"], "OPEN")

    def test_operation_interval_prose_does_not_truncate_remaining_rows(self) -> None:
        pdf = sample_pdf("REPORTES COMPLETOS CPI - SCHR-407.pdf")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")

        with pdfplumber.open(pdf) as document:
            rows = _parse_operation_page(document.pages[5])

        self.assertEqual(len(rows), 8)
        self.assertAlmostEqual(sum(float(row["hours"]) for row in rows), 24.0)
        self.assertEqual(rows[0]["from"], "6:00")
        self.assertEqual(rows[-1]["to"], "6:00")


if __name__ == "__main__":
    unittest.main()
