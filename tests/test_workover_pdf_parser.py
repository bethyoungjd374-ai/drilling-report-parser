from __future__ import annotations

import unittest
from pathlib import Path

from drilling_report_parser.workover_pdf_parser import parse_workover_pdf_daily_report


SAMPLE_DIRS = (
    Path("/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/华为ai任务资料/修井日报"),
    Path("/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/日报资料/修井"),
    Path("/Users/wujianhui/Documents/1、Work/厄瓜多尔资料/华为ai任务资料/修井日报"),
)


def sample_pdf(name: str) -> Path:
    for sample_dir in SAMPLE_DIRS:
        matches = sorted(sample_dir.rglob(name)) if sample_dir.exists() else []
        if matches:
            return matches[0]
    return SAMPLE_DIRS[0] / name


class WorkoverPdfParserTest(unittest.TestCase):
    def test_parse_acah_workover_sample(self) -> None:
        pdf = sample_pdf("4. 10062026_RDO_ACAH-270H_WO#03 SINOPEC-933.pdf")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")
        payload = parse_workover_pdf_daily_report(pdf)
        fields = payload["report_fields"]
        self.assertEqual(fields["event"], "WORKOVER")
        self.assertEqual(fields["workoverNo"], "03")
        self.assertEqual(fields["wellbore"], "ACAH-270H")
        self.assertEqual(fields["reportDate"], "2026-06-10")
        self.assertEqual(fields["reportNo"], "4")
        self.assertEqual(fields["rig"], "SINOPEC 933")
        self.assertEqual(fields["supervisor1"], "JOSE GENCON")
        self.assertEqual(fields["engineer"], "LUCAS PEREIRA (SLB)")
        self.assertEqual(fields["pamEngineer"], "")
        self.assertEqual(len(payload["operations"]), 11)
        self.assertAlmostEqual(sum(float(row["hours"]) for row in payload["operations"]), 24.0)
        self.assertEqual(payload["operations"][0]["op_code"], "SURFACE EQUIPMENT")
        self.assertEqual(payload["operations"][5]["op_code"], "WELLHEAD")
        self.assertTrue(all(row["op_type"] in {"P", "SC", "NPT"} for row in payload["operations"]))
        self.assertEqual(payload["bulks"][0]["qty_used"], "180.00")
        self.assertNotIn("daily_costs", payload)
        interval = payload["perforation_intervals"][0]
        self.assertEqual(interval["formation"], "ARENA U INFERIOR")
        self.assertEqual(interval["date"], "2023-06-21")
        self.assertEqual(interval["comments"], "TCP + PURE - WO#01")

    def test_parse_shsg_workover_sample(self) -> None:
        pdf = sample_pdf("2- REPORTE DIARIO SHSG-160 WO#05 11-JUNIO-2026.pdf")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")
        payload = parse_workover_pdf_daily_report(pdf)
        fields = payload["report_fields"]
        self.assertEqual(fields["event"], "WORKOVER")
        self.assertEqual(fields["workoverNo"], "05")
        self.assertEqual(fields["wellbore"], "SHSG-160")
        self.assertEqual(fields["operationStartDate"], "2026-06-10")
        self.assertEqual(fields["rig"], "SINOPEC-905")
        self.assertIn("RECUPERAR EQUIPO ESP", fields["description"])
        self.assertIn("CHARLA SSA", fields["safetyComments"])
        self.assertEqual(len(payload["operations"]), 11)
        self.assertAlmostEqual(sum(float(row["hours"]) for row in payload["operations"]), 24.0)
        self.assertEqual(payload["operations"][0]["op_sub"], "Pre job safety meeting")
        self.assertEqual(payload["operations"][5]["op_code"], "COMPLETION OPS")
        self.assertEqual(payload["operations"][-1]["op_code"], "SLICK LINE")
        self.assertEqual(payload["bulks"][0]["qty_end"], "1670.00")
        self.assertNotIn("daily_costs", payload)
        interval = payload["perforation_intervals"][0]
        self.assertEqual(interval["formation"], "ARENA T INFERIOR")
        self.assertEqual(interval["date"], "2017-08-24")
        self.assertEqual(interval["comments"], 'REPUNZONAMIENTO ARENA "TI"')

    def test_operation_interval_prose_does_not_truncate_workover_rows(self) -> None:
        pdf = sample_pdf("4. 06012026_RDO_ACAH-273H_WO#02 SINOPEC-933.pdf")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")

        payload = parse_workover_pdf_daily_report(pdf)

        self.assertAlmostEqual(sum(float(row["hours"]) for row in payload["operations"]), 24.0)
        self.assertEqual(payload["operations"][-1]["to"], "6:00")

    def test_blank_declared_hours_are_derived_from_complete_clock_range(self) -> None:
        pdf = sample_pdf("2. 08062026_RDO_ACAH-270H_WO#03 SINOPEC-933.pdf")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")

        payload = parse_workover_pdf_daily_report(pdf)

        self.assertAlmostEqual(sum(float(row["hours"]) for row in payload["operations"]), 24.0)
        self.assertEqual(payload["operations"][-1]["hours"], "12.00")
        self.assertEqual(payload["operations"][-1]["hours_source"], "CLOCK_DERIVED")


if __name__ == "__main__":
    unittest.main()
