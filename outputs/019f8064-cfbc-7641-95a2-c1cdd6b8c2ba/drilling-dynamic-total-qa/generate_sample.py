from pathlib import Path

from drilling_report_parser.form_server import _monthly_drilling_basic_workbook_bytes


rows = []
for index in range(1, 9):
    rows.append({
        "sequence": index,
        "team_code": f"SINOPEC {120 + index}",
        "country_region": "厄瓜多尔",
        "team_company": "江汉工程",
        "block_name": "SACHA",
        "rig_model": "ZJ70D",
        "well_name": f"TEST-{index:03d}",
        "well_profile": "定向井",
        "drilling_start_date": f"2026-07-{index:02d}",
        "drilling_end_date": f"2026-07-{index + 4:02d}",
        "completion_date": f"2026-07-{index + 6:02d}",
        "design_depth_ft": 12000,
        "current_depth_ft": 11000 + index,
        "month_progress_ft": 100 * index,
        "year_progress_ft": 200 * index,
        "actual_drilling_cycle_days": 5.0,
        "actual_completion_cycle_days": 2.0,
    })

output = Path(__file__).with_name("drilling-dynamic-total.xlsx")
output.write_bytes(_monthly_drilling_basic_workbook_bytes({
    "report_date": "2026-07-21",
    "rows": rows,
}))
