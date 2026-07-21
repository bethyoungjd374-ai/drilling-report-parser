from pathlib import Path

from drilling_report_parser.form_server import _monthly_workover_basic_workbook_bytes


rows = []
for index in range(1, 6):
    rows.append({
        "sequence": index,
        "team_code": f"SINOPEC {900 + index}修井队",
        "country_region": "厄瓜多尔",
        "team_company": "华东工程",
        "block_name": "AUCA",
        "rig_model": "XJ650",
        "well_name": f"TEST-{index:03d}",
        "well_profile": "油井",
        "workover_start_date": f"2026-07-{index:02d}",
        "workover_end_date": f"2026-07-{index + 5:02d}",
        "primary_operation": "检泵",
        "well_control_incident": "",
        "accident_waiting": "",
        "remarks": "",
    })

payload = {"report_date": "2026-07-21", "rows": rows}
output_path = Path(__file__).with_name("workover-dynamic-total.xlsx")
output_path.write_bytes(_monthly_workover_basic_workbook_bytes(payload))
print(output_path)
