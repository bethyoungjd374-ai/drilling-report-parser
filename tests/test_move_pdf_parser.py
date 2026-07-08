from __future__ import annotations

import unittest
from pathlib import Path

from drilling_report_parser.move_pdf_parser import parse_move_pdf_daily_report


SAMPLE_DIR = Path("/Users/wujianhui/Documents/1、Work/厄瓜多尔资料/华为ai任务资料/搬迁日报")


class MovePdfParserTest(unittest.TestCase):
    def test_parse_tcha_move_sample(self) -> None:
        pdf = SAMPLE_DIR / "06102026-TCHA-006I-SIN-168-PEC-005-V1R1-REPORTE DIARIO DE MOVILIZACIÓN.pdf"
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")
        payload = parse_move_pdf_daily_report(pdf)
        fields = payload["report_fields"]
        self.assertEqual(fields["event"], "MAJOR RIG MOVE")
        self.assertEqual(fields["wellbore"], "TCHA-006I")
        self.assertEqual(fields["reportDate"], "2026-06-10")
        self.assertEqual(fields["reportNo"], "5")
        self.assertEqual(fields["primaryReason"], "INICIAL MOVE")
        self.assertEqual(fields["rig"], "SINOPEC 168")
        self.assertNotIn("supervisor1", fields)
        self.assertNotIn("engineer", fields)
        self.assertNotIn("rigMovePercent", fields)
        self.assertNotIn("rigUpPercent", fields)
        self.assertNotIn("loadsSentToday", fields)
        self.assertNotIn("loadsSentTotal", fields)
        self.assertNotIn("loadsPlannedTotal", fields)
        self.assertNotIn("safetyIncident", fields)
        self.assertNotIn("environmentIncident", fields)
        self.assertNotIn("daysSinceRi", fields)
        self.assertNotIn("daysSinceLta", fields)
        self.assertNotIn("incidentComments", fields)
        self.assertNotIn("afeCost", fields)
        self.assertNotIn("dailyCost", fields)
        self.assertNotIn("cumulativeCost", fields)
        self.assertEqual(len(payload["operations"]), 3)
        self.assertAlmostEqual(sum(float(row["hours"]) for row in payload["operations"]), 24.0)
        self.assertEqual(payload["operations"][0]["op_code"], "MOVE")
        self.assertEqual(payload["operations"][0]["op_sub"], "Pre job safety meeting")
        self.assertEqual(payload["operations"][2]["op_sub"], "Waiting for night")
        self.assertTrue(all(row["op_type"] in {"P", "SC", "NPT"} for row in payload["operations"]))
        self.assertNotIn("heavy_equipment", payload)
        self.assertNotIn("move_loads", payload)
        self.assertNotIn("daily_costs", payload)


if __name__ == "__main__":
    unittest.main()
