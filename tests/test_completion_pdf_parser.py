from __future__ import annotations

import unittest
from pathlib import Path

from drilling_report_parser.completion_pdf_parser import parse_completion_pdf_daily_report


SAMPLE_DIR = Path("/Users/wujianhui/Documents/1、Work/厄瓜多尔资料/华为ai任务资料/完井日报")


class CompletionPdfParserTest(unittest.TestCase):
    def test_parse_schas_completion_sample(self) -> None:
        pdf = SAMPLE_DIR / "06112026-SCHAS-513-SIN-219-PEC-007-V1R1 REPORTE DIARIO DE COMPLETACIÓN.pdf"
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

    def test_parse_lobc_completion_sample(self) -> None:
        pdf = SAMPLE_DIR / "06112026-LOBC-010-SIN-127-PEC-008-V1R1-REPORTE DIARIO DE COMPLETACIÓN.pdf"
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
        interval = payload["perforation_intervals"][0]
        self.assertEqual(interval["formation"], "ARENISCA T")
        self.assertEqual(interval["top_md"], "10991.00")
        self.assertEqual(interval["base_md"], "11023.00")
        self.assertEqual(interval["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
