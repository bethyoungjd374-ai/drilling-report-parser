from __future__ import annotations

import unittest
from pathlib import Path

from drilling_report_parser.pdf_report_parser import parse_pdf_daily_report


SAMPLE_DIRS = [
    Path("/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/华为ai任务资料/钻井日报"),
    Path("/Users/wujianhui/Documents/1、Work/厄瓜多尔资料/华为ai任务资料/钻井日报"),
]


def sample_pdf(name_part: str) -> Path:
    for sample_dir in SAMPLE_DIRS:
        if not sample_dir.exists():
            continue
        matches = sorted(sample_dir.glob(f"*{name_part}*.pdf"))
        if matches:
            return matches[0]
    return SAMPLE_DIRS[0] / f"*{name_part}*.pdf"


class PdfReportParserTest(unittest.TestCase):
    def test_parse_schao_sample(self) -> None:
        pdf = sample_pdf("SCHAO-611")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")
        payload = parse_pdf_daily_report(pdf)
        fields = payload["report_fields"]
        self.assertEqual(fields["wellbore"], "SCHAO-611")
        self.assertEqual(fields["reportNo"], "16")
        self.assertEqual(fields["rig"], "SINOPEC 129")
        self.assertEqual(fields["prevMd"], "10754.00")
        self.assertEqual(fields["progress"], "0.00")
        self.assertEqual(fields["rotHrsToday"], "")
        self.assertEqual(fields["lastCasingSize"], "13.375in")
        self.assertEqual(fields["lastCasingDepth"], "7,111ft")
        self.assertEqual(fields["nextCasingSize"], "9.625in")
        self.assertEqual(fields["nextCasingDepth"], "10,754ft")
        self.assertEqual(fields["mudTime"], "21:00")
        self.assertEqual(fields["mudMd"], "10,754.0")
        self.assertEqual(fields["mudDensity"], "10.40")
        self.assertEqual(fields["mudTemperature"], "155")
        self.assertEqual(fields["viscosity"], "44.00")
        self.assertEqual(fields["pv"], "16")
        self.assertEqual(fields["yp"], "21")
        self.assertEqual(fields["gel10s"], "6")
        self.assertEqual(fields["gel10m"], "11")
        self.assertEqual(fields["gel30m"], "15")
        self.assertEqual(fields["oilPercent"], "5.0")
        self.assertEqual(fields["waterPercent"], "85.6")
        self.assertEqual(len(payload["survey_data"]), 6)
        self.assertEqual(len(payload["bha_components"]), 13)
        self.assertEqual(len(payload["operations"]), 13)
        self.assertEqual(payload["operations"][0]["op_sub"], "POOH Bit / BHA / Oth")
        self.assertTrue(all(row["op_type"] in {"P", "NPT"} for row in payload["operations"]))
        self.assertFalse(any("BHA / Oth" in row["operation_details"] for row in payload["operations"]))
        self.assertEqual(payload["bulks"][0]["bulk"], "DIESEL - RIG")

    def test_parse_pcnc_sample(self) -> None:
        pdf = sample_pdf("PCNC-040")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")
        payload = parse_pdf_daily_report(pdf)
        fields = payload["report_fields"]
        self.assertEqual(fields["wellbore"], "PCNC-040")
        self.assertEqual(fields["reportNo"], "11")
        self.assertEqual(fields["rig"], "SINOPEC 248")
        self.assertEqual(fields["prevMd"], "10641.00")
        self.assertEqual(fields["progress"], "191.00")
        self.assertEqual(fields["rotHrsToday"], "4.48")
        self.assertEqual(fields["lastCasingSize"], "13.375in")
        self.assertEqual(fields["lastCasingDepth"], "7,610ft")
        self.assertEqual(fields["nextCasingSize"], "9.625in")
        self.assertEqual(fields["nextCasingDepth"], "11,720ft")
        self.assertEqual(fields["mudTime"], "2:00")
        self.assertEqual(fields["mudMd"], "10,832.0")
        self.assertEqual(fields["mudDensity"], "9.80")
        self.assertEqual(fields["mudTemperature"], "138")
        self.assertEqual(fields["viscosity"], "36.00")
        self.assertEqual(fields["pv"], "8")
        self.assertEqual(fields["yp"], "16")
        self.assertEqual(fields["oilPercent"], "")
        self.assertEqual(fields["waterPercent"], "89.3")
        self.assertEqual(len(payload["survey_data"]), 6)
        self.assertEqual(len(payload["bha_components"]), 12)
        self.assertEqual(len(payload["operations"]), 6)
        self.assertEqual(payload["operations"][0]["op_sub"], "Rotary - Directional")
        self.assertTrue(all(row["op_type"] in {"P", "NPT"} for row in payload["operations"]))
        self.assertFalse(any("NG Directional" in row["operation_details"] or "BHA / Oth" in row["operation_details"] for row in payload["operations"]))
        self.assertEqual(len(payload["bulks"]), 2)


if __name__ == "__main__":
    unittest.main()
