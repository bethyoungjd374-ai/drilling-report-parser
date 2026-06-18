from __future__ import annotations

import unittest

from drilling_report_parser.report_excel import WARNING_FILL, build_completion_report_workbook, build_daily_report_workbook, build_move_report_workbook, build_workover_report_workbook


class ReportExcelTest(unittest.TestCase):
    def test_operation_type_warning_fill(self) -> None:
        workbook = build_daily_report_workbook({
            "report_fields": {
                "wellbore": "PCNC-040",
                "rig": "00 SINOPEC 248",
                "reportNo": "11",
                "reportDate": "2026-06-11",
                "lastCasingSize": "13.375in",
                "lastCasingDepth": "7,610ft",
                "nextCasingSize": "9.625in",
                "nextCasingDepth": "11,720ft",
                "mudTime": "2:00",
                "mudMd": "10,832.0",
                "pv": "8",
                "yp": "16",
            },
            "operations": [{
                "from": "6:00",
                "to": "12:00",
                "hours": "6.00",
                "op_code": "DRILLING",
                "op_sub": "Rotary - Directional",
                "op_type": "",
                "operation_details": "PERFORA CON BHA.",
            }],
        })
        worksheet = workbook.active
        type_header = next(cell for row in worksheet.iter_rows() for cell in row if cell.value == "Type")
        warning_cell = worksheet.cell(type_header.row + 1, type_header.column)
        self.assertEqual(warning_cell.fill.fgColor.rgb, f"00{WARNING_FILL}")

    def test_completion_operation_sc_type_is_valid(self) -> None:
        workbook = build_completion_report_workbook({
            "report_fields": {
                "wellbore": "SCHAS-513",
                "rig": "SINOPEC 219",
                "reportNo": "7",
                "reportDate": "2026-06-11",
            },
            "operations": [{
                "from": "11:30",
                "to": "12:30",
                "hours": "1.00",
                "op_code": "PERFORATING",
                "op_sub": "Tripping",
                "op_type": "SC",
                "operation_details": "TÉCNICO REALIZA MANIOBRA.",
            }],
        })
        worksheet = workbook.active
        type_header = next(cell for row in worksheet.iter_rows() for cell in row if cell.value == "Type")
        type_cell = worksheet.cell(type_header.row + 1, type_header.column)
        self.assertEqual(type_cell.value, "SC")
        self.assertNotEqual(type_cell.fill.fgColor.rgb, f"00{WARNING_FILL}")

    def test_workover_report_workbook_title_and_type(self) -> None:
        workbook = build_workover_report_workbook({
            "report_fields": {
                "wellbore": "ACAH-270H",
                "rig": "SINOPEC 933",
                "workoverNo": "03",
                "reportNo": "4",
                "reportDate": "2026-06-10",
            },
            "operations": [{
                "from": "6:00",
                "to": "7:30",
                "hours": "1.50",
                "op_code": "SURFACE EQUIPMENT",
                "op_sub": "PULL",
                "op_type": "P",
                "operation_details": "CONTINÚA DESFOGANDO POZO.",
            }],
        })
        worksheet = workbook.active
        self.assertEqual(worksheet.title, "Workover Report")
        self.assertEqual(worksheet["A1"].value, "DAILY WORKOVER OPERATIONS REPORT")
        type_header = next(cell for row in worksheet.iter_rows() for cell in row if cell.value == "Type")
        type_cell = worksheet.cell(type_header.row + 1, type_header.column)
        self.assertEqual(type_cell.value, "P")
        self.assertNotEqual(type_cell.fill.fgColor.rgb, f"00{WARNING_FILL}")

    def test_move_report_workbook_title_and_tables(self) -> None:
        workbook = build_move_report_workbook({
            "report_fields": {
                "wellbore": "TCHA-006I",
                "rig": "00 SINOPEC 168",
                "reportNo": "5",
                "reportDate": "2026-06-10",
            },
            "operations": [{
                "from": "6:30",
                "to": "18:00",
                "hours": "11.50",
                "op_code": "MOVE",
                "op_sub": "MOVE",
                "op_type": "P",
                "operation_details": "PERSONAL DE SINOPEC-168 PREPARA Y ENVÍA CARGAS.",
            }],
        })
        worksheet = workbook.active
        self.assertEqual(worksheet.title, "Move Report")
        self.assertEqual(worksheet["A1"].value, "DAILY RIG MOVE OPERATIONS REPORT")
        values = [cell.value for row in worksheet.iter_rows() for cell in row]
        self.assertNotIn("RIG MOVE PROGRESS", values)
        self.assertNotIn("PERSONNEL / INCIDENTS", values)
        self.assertNotIn("HEAVY EQUIPMENT", values)
        self.assertNotIn("MOVE LOADS", values)
        self.assertNotIn("DAILY COSTS / REMARKS", values)


if __name__ == "__main__":
    unittest.main()
