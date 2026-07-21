from __future__ import annotations

import unittest
from pathlib import Path

from drilling_report_parser.pdf_report_parser import (
    _clean_operation_details,
    _normalize_op_type,
    _parse_incidents,
    _parse_fluid_losses,
    _parse_report_fields,
    parse_pdf_daily_report,
)
from drilling_report_parser.drilling_pdf_templates import (
    _filename_header_fields,
    _short_other_remarks,
    _strip_report_footer,
    parse_compatible_pdf_daily_report,
)


SAMPLE_DIRS = [
    Path("/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/华为ai任务资料/钻井日报"),
    Path("/Users/wujianhui/Documents/1、Work/厄瓜多尔资料/华为ai任务资料/钻井日报"),
]


def sample_pdf(name_part: str) -> Path:
    for sample_dir in SAMPLE_DIRS:
        if not sample_dir.exists():
            continue
        matches = sorted(sample_dir.rglob(f"*{name_part}*.pdf"))
        if matches:
            return matches[0]
    return SAMPLE_DIRS[0] / f"*{name_part}*.pdf"


class PdfReportParserTest(unittest.TestCase):
    def test_compatible_filename_fields_support_sinopec_export_name(self) -> None:
        fields = _filename_header_fields(
            "04232026-LOBC-009-SIN-127-PEC-013-V1R1-REPORTE DIARIO.pdf"
        )

        self.assertEqual(fields, {
            "reportDate": "2026-04-23",
            "wellbore": "LOBC-009",
            "rig": "SINOPEC 127",
            "reportNo": "13",
        })

    def test_compatible_short_remarks_cross_page_and_skip_repeated_header(self) -> None:
        pages = [
            "OPERATIONS\nOTHER REMARKS\n04/29/2026 8:23:44PM Page 1 of 2",
            "\n".join([
                "EP PETROECUADOR",
                "Event: DEV DRILLING Date:DAILY OPERATIONS SHORT REPORT04/23/2026",
                "Prim. Reason: DEEPEN DIR LOBC-009ECU Report No: 13",
                "Description: Inicio OPR:DIRECTO CON PEC4/10/2026",
                "** CUADRILLA COMPLETA",
                "- EVACUACION DE CORTES DIARIO: 73.2 M3",
                "04/29/2026 8:23:44PM Page 2 of 2",
            ]),
        ]

        remarks = _short_other_remarks(pages)

        self.assertEqual(
            remarks,
            "** CUADRILLA COMPLETA - EVACUACION DE CORTES DIARIO: 73.2 M3",
        )
        self.assertNotIn("EP PETROECUADOR", remarks)
        self.assertNotIn("Page 2 of 2", remarks)

    def test_compatible_footer_cleanup_accepts_am_and_pm(self) -> None:
        self.assertEqual(
            _strip_report_footer("OBSERVACION 4/29/2026 8:15:56PM Page 2 of 2"),
            "OBSERVACION",
        )

    def test_compatible_profile_parses_lobc_short_report(self) -> None:
        sample_dir = Path(
            "/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/日报资料/钻井/ow fin"
        )
        matches = sorted(sample_dir.glob("04232026-LOBC-009-*.pdf"))
        if not matches:
            self.skipTest("LOBC-009 short report sample not found")

        payload = parse_compatible_pdf_daily_report(matches[0])
        fields = payload["report_fields"]

        self.assertEqual(fields["event"], "DEV DRILLING")
        self.assertEqual(fields["reportDate"], "2026-04-23")
        self.assertEqual(fields["reportNo"], "13")
        self.assertEqual(fields["wellbore"], "LOBC-009")
        self.assertEqual(fields["rig"], "SINOPEC 127")
        self.assertEqual(fields["primaryReason"], "DEEPEN DIR")
        self.assertEqual(payload["metadata"]["template_profile"], "compatible")
        self.assertEqual(payload["metadata"]["template_variant"], "daily_operations_short_report")
        self.assertNotIn("OPERATIONS From To", fields["forecast24h"])
        self.assertIn("CUADRILLA COMPLETA", fields["otherRemarks"])
        self.assertIn("EVACUACION DE CORTES DIARIO", fields["otherRemarks"])
        self.assertNotIn("EP PETROECUADOR", fields["otherRemarks"])
        self.assertNotIn("Page 2 of 2", fields["otherRemarks"])
        self.assertFalse(any(
            "OTHER REMARKS" in row["operation_details"].upper()
            for row in payload["operations"]
        ))
        self.assertEqual(fields["mudType"], "FLUIDO POLIMÉRICO")
        self.assertEqual(fields["mudDensity"], "10.2")
        self.assertEqual(fields["viscosity"], "43")
        self.assertEqual(fields["pv"], "11")
        self.assertEqual(fields["yp"], "12")
        self.assertEqual(fields["gel10s"], "10")
        self.assertEqual(fields["gel10m"], "17")
        self.assertEqual(fields["gel30m"], "25")
        self.assertEqual(fields["apiWl"], "14.6")
        self.assertEqual(fields["sand"], "0.1")

    def test_compatible_profile_fills_blank_rig_from_filename(self) -> None:
        sample_dir = Path(
            "/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/日报资料/钻井/ow fin"
        )
        matches = sorted(sample_dir.glob("04112026-LOBC-009-*.pdf"))
        if not matches:
            self.skipTest("LOBC-009 legacy report sample not found")

        payload = parse_compatible_pdf_daily_report(matches[0])

        self.assertEqual(payload["report_fields"]["rig"], "SINOPEC 127")
        self.assertEqual(payload["metadata"]["filename_fallback_fields"], ["rig"])

    def test_compatible_profile_removes_full_report_footer_from_remarks(self) -> None:
        sample_dir = Path(
            "/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/日报资料/钻井/ow fin"
        )
        matches = sorted(sample_dir.glob("04152026-LOBC-009-*.pdf"))
        if not matches:
            self.skipTest("LOBC-009 footer sample not found")

        remarks = parse_compatible_pdf_daily_report(matches[0])["report_fields"]["otherRemarks"]

        self.assertIn("CUADRILLA COMPLETA", remarks)
        self.assertNotIn("Page 2 of 2", remarks)

    def test_report_number_accepts_full_ecuador_country_label(self) -> None:
        lines = [
            "Event: DEV DRILLING Date:JVNC-024 07/15/2026",
            "Prim. Reason: INICIAL MOVE ECUADOR Report No: 15",
        ]

        fields = _parse_report_fields(lines, "\n".join(lines), "\n".join(lines))

        self.assertEqual(fields["reportNo"], "15")

    def test_fluid_losses_are_parsed_as_numeric_text_without_units(self) -> None:
        rows = _parse_fluid_losses(
            "FLUID LOSSES\nInjected Volume: 12.50 (bbl)\nReturned Volume: 3.25 (bbl)"
        )

        self.assertEqual(rows, [{
            "injected_volume_bbl": "12.50",
            "returned_volume_bbl": "3.25",
        }])

    def test_operation_type_keeps_source_sc_value(self) -> None:
        self.assertEqual(_normalize_op_type("SC"), "SC")

    def test_operation_details_drop_trailing_incident_heading(self) -> None:
        self.assertEqual(
            _clean_operation_details("NPT A CARGO DE SINOPEC\nIncident Comments:"),
            "NPT A CARGO DE SINOPEC",
        )
        self.assertEqual(
            _clean_operation_details("ROMPE CIRCULACIÓN CADA 1000'\nIncident Comments: 37.00"),
            "ROMPE CIRCULACIÓN CADA 1000'",
        )

    def test_operation_details_keep_actual_incident_comment_prose(self) -> None:
        value = "Verify incident comments: no injuries were reported."

        self.assertEqual(_clean_operation_details(value), value)

    def test_incident_comments_stop_at_page_boundary_and_exclude_labels(self) -> None:
        pages = [
            "\n".join([
                "Safety Incident? N Days since Last RI: Incident Comments:",
                "Environ Incident? N Days since Last LTA :INCIDENTES SIN REPORTAR EN LAS ULTIMAS 24 HORAS.",
                "5/17/2026 5:26:07AM Page 3 of 4",
            ]),
            "\n".join([
                "EP PETROECUADOR",
                "DAILY OPERATIONS REPORT",
                "Event: DEV DRILLING Date:PCNC-03905/17/2026",
                "Prim. Reason: DEEPEN DIR ECU Report No: 5",
                "Other Remarks: POB:",
            ]),
        ]

        fields = _parse_incidents(pages)

        self.assertEqual(fields["incidentComments"], "INCIDENTES SIN REPORTAR EN LAS ULTIMAS 24 HORAS.")
        self.assertNotIn("Page 3 of 4", fields["incidentComments"])
        self.assertNotIn("DAILY OPERATIONS REPORT", fields["incidentComments"])

    def test_incident_days_and_wrapped_comment_are_parsed_separately(self) -> None:
        page = "\n".join([
            "Safety Incident? N Days since Last RI: 37.00 Incident Comments:",
            "Environ Incident? N Days since Last LTA 37.00 INCIDENTES SIN REPORTAR EN LAS ULTIMAS 24 HORAS.",
            "OPERACIONES SIMULTANEAS TALADRO SINOPEC 129 Y",
            "EQUIPO TRIBOIL GAS 104: ARMA Y BAJA EQUIPO BES",
        ])

        fields = _parse_incidents([page])

        self.assertEqual(fields["daysSinceRi"], "37.00")
        self.assertEqual(fields["daysSinceLta"], "37.00")
        self.assertEqual(
            fields["incidentComments"],
            "INCIDENTES SIN REPORTAR EN LAS ULTIMAS 24 HORAS. "
            "OPERACIONES SIMULTANEAS TALADRO SINOPEC 129 Y EQUIPO TRIBOIL GAS 104: ARMA Y BAJA EQUIPO BES",
        )

    def test_parse_schao_sample(self) -> None:
        pdf = sample_pdf("SCHAO-611")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")
        payload = parse_pdf_daily_report(pdf)
        fields = payload["report_fields"]
        self.assertEqual(fields["wellbore"], "SCHAO-611")
        self.assertEqual(fields["reportNo"], "16")
        self.assertEqual(fields["rig"], "SINOPEC 129")
        self.assertEqual(fields["wellboreNo"], "00")
        self.assertEqual(fields["groundElev"], "865.01")
        self.assertEqual(fields["dfs"], "15.75")
        self.assertEqual(fields["dailyCost"], "$0")
        self.assertEqual(fields["cumulativeCost"], "$0")
        self.assertEqual(fields["afeCost"], "$4,587,000")
        self.assertEqual(fields["avgRopSlide"], "0.00")
        self.assertEqual(fields["avgRopRot"], "0.00")
        self.assertEqual(fields["supervisor1"], "JOSE IZQUIERDO")
        self.assertEqual(fields["supervisor2"], "JHONATAN ANDRADE")
        self.assertEqual(fields["pamEngineer"], "RAY BAEZ")
        self.assertEqual(fields["geologist"], "")
        self.assertEqual(fields["totalPersonnel"], "100")
        self.assertEqual(fields["prevMd"], "10754.00")
        self.assertEqual(fields["progress"], "0.00")
        self.assertEqual(fields["rotHrsToday"], "")
        self.assertEqual(fields["lastCasingSize"], "13.375")
        self.assertEqual(fields["lastCasingDepth"], "7111")
        self.assertEqual(fields["nextCasingSize"], "9.625")
        self.assertEqual(fields["nextCasingDepth"], "10754")
        self.assertEqual(fields["formTestType"], "FIT")
        self.assertEqual(fields["formTestEmw"], "11.50")
        self.assertEqual(fields["bitNo"], "05")
        self.assertEqual(fields["bitSerial"], "SPS3739")
        self.assertEqual(fields["bitWearIodl"], "0-1-CT-S")
        self.assertEqual(fields["bitWearBgor"], "X-I-NO-TD")
        self.assertEqual(fields["bhaMdIn"], "9215.00")
        self.assertEqual(fields["bhaMdOut"], "10754.00")
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
        self.assertEqual(payload["fluid_losses"], [{
            "injected_volume_bbl": "0.0",
            "returned_volume_bbl": "0.0",
        }])
        self.assertNotIn("daily_costs", payload)
        self.assertEqual(payload["operations"][0]["op_sub"], "POOH Bit / BHA / Oth")
        self.assertTrue(all(row["op_type"] in {"P", "NPT"} for row in payload["operations"]))
        self.assertFalse(any("BHA / Oth" in row["operation_details"] for row in payload["operations"]))
        self.assertFalse(any("Incident Comments:" in row["operation_details"] for row in payload["operations"]))
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
        self.assertEqual(fields["wellboreNo"], "00")
        self.assertEqual(fields["prevMd"], "10641.00")
        self.assertEqual(fields["progress"], "191.00")
        self.assertEqual(fields["rotHrsToday"], "4.48")
        self.assertEqual(fields["lastCasingSize"], "13.375")
        self.assertEqual(fields["lastCasingDepth"], "7610")
        self.assertEqual(fields["nextCasingSize"], "9.625")
        self.assertEqual(fields["nextCasingDepth"], "11720")
        self.assertEqual(fields["formTestType"], "FIT")
        self.assertEqual(fields["formTestEmw"], "13.70")
        self.assertEqual(fields["lastBopPressTest"], "2026-06-06")
        self.assertEqual(fields["bitNo"], "03")
        self.assertEqual(fields["bitSerial"], "14456485")
        self.assertEqual(fields["bitWearIodl"], "")
        self.assertEqual(fields["bitWearBgor"], "")
        self.assertEqual(fields["bhaMdIn"], "7610.00")
        self.assertEqual(fields["bhaMdOut"], "")
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
        self.assertEqual(payload["fluid_losses"], [{
            "injected_volume_bbl": "0.0",
            "returned_volume_bbl": "0.0",
        }])
        self.assertNotIn("daily_costs", payload)
        self.assertEqual(payload["operations"][0]["op_sub"], "Rotary - Directional")
        self.assertTrue(all(row["op_type"] in {"P", "NPT"} for row in payload["operations"]))
        self.assertFalse(any("NG Directional" in row["operation_details"] or "BHA / Oth" in row["operation_details"] for row in payload["operations"]))
        self.assertFalse(any("Incident Comments:" in row["operation_details"] for row in payload["operations"]))
        self.assertEqual(len(payload["bulks"]), 2)

    def test_parse_pcnc_039_incident_comment(self) -> None:
        pdf = sample_pdf("05-17-2026")
        if not pdf.exists():
            self.skipTest(f"Sample PDF not found: {pdf}")

        fields = parse_pdf_daily_report(pdf)["report_fields"]

        self.assertEqual(fields["wellbore"], "PCNC-039")
        self.assertEqual(fields["incidentComments"], "INCIDENTES SIN REPORTAR EN LAS ULTIMAS 24 HORAS.")


if __name__ == "__main__":
    unittest.main()
