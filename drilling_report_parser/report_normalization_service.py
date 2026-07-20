"""Dual-write normalized report facts while preserving the original report payload."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Any

from .field_registry import parse_afe_depth_days, parse_numeric_field, parse_string_weight_pair
from .master_data_service import resolve_master_id, resolve_project_assignment
from .operation_standardization import standardize_operation_code
from .text_structure import normalize_translation_paragraph
from .time_classification_service import upsert_activity_classification


def synchronize_saved_report(
    cursor: Any,
    *,
    record_id: str,
    report_type: str,
    fields: dict[str, Any],
    operations: list[dict[str, Any]],
    payload: dict[str, Any] | None = None,
    actor: str = "system",
) -> dict[str, Any]:
    source_report_date = str(fields.get("reportDate", "") or "").strip()
    report_date = _nullable_date(source_report_date)
    rig_id = resolve_master_id(cursor, "rig", fields.get("rig"))
    well_id = resolve_master_id(cursor, "well", fields.get("wellbore"))
    explicit_job_id = _positive_int(fields.get("jobId") or fields.get("job_id"))
    resolution = resolve_project_assignment(
        cursor,
        report_date=report_date or "",
        report_type=report_type,
        rig_id=rig_id,
        well_id=well_id,
        explicit_job_id=explicit_job_id,
    )
    match_status = str(resolution.get("status", "UNASSIGNED") or "UNASSIGNED")
    match_message = str(resolution.get("message", "") or "")
    project_id = _positive_int(resolution.get("project_id"))
    job_id = _positive_int(resolution.get("job_id"))
    normalization_status = _report_normalization_status(report_date)

    cursor.execute(
        """
        UPDATE dpr_report_record
        SET rig_id=%s, well_id=%s, project_id=%s, job_id=%s,
            master_match_status=%s, master_match_message=%s
        WHERE record_id=%s
        """,
        (rig_id, well_id, project_id, job_id, match_status, match_message, record_id),
    )
    report_no = _nullable_report_no(fields.get("reportNo"))
    cursor.execute(
        """
        INSERT INTO dpr_report
          (record_id, report_date, report_no, report_type, project_id, job_id, rig_id, well_id,
           match_status, match_message, normalization_status, source_version, created_by, updated_by)
        VALUES (%s,NULLIF(%s,''),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          report_date=VALUES(report_date), report_no=VALUES(report_no), report_type=VALUES(report_type),
          project_id=VALUES(project_id), job_id=VALUES(job_id), rig_id=VALUES(rig_id),
          well_id=VALUES(well_id), match_status=VALUES(match_status),
          match_message=VALUES(match_message), normalization_status=VALUES(normalization_status),
          source_version=VALUES(source_version), updated_by=VALUES(updated_by), version=version+1
        """,
        (
            record_id,
            report_date or "",
            report_no,
            report_type,
            project_id,
            job_id,
            rig_id,
            well_id,
            match_status,
            match_message,
            normalization_status,
            _source_version(fields, operations),
            actor,
            actor,
        ),
    )
    cursor.execute("SELECT id FROM dpr_report WHERE record_id=%s", (record_id,))
    daily_report_id = int((cursor.fetchone() or {})["id"])

    structured_payload = dict(payload or {})
    structured_payload["operations"] = operations
    synchronize_structured_report_facts(
        cursor,
        daily_report_id=daily_report_id,
        report_type=report_type,
        fields=fields,
        payload=structured_payload,
        actor=actor,
    )

    source_rows: set[int] = set()
    invalid_activity_hours = 0
    invalid_activity_times = 0
    mismatched_activity_times = 0
    total_hours = 0.0
    for row_no, row in enumerate(operations, start=1):
        if not isinstance(row, dict):
            continue
        source_rows.add(row_no)
        hours = _nullable_float(row.get("hours"))
        hours_source = str(row.get("hours_source", "DECLARED") or "DECLARED").strip().upper()
        if hours_source not in {"DECLARED", "CLOCK_DERIVED"}:
            hours_source = "DECLARED"
        if hours is None:
            invalid_activity_hours += 1
        total_hours += hours or 0.0
        source_hash = _activity_hash(row)
        time_facts = _activity_time_facts(report_date or "", row.get("from"), row.get("to"), hours)
        if time_facts["time_validation_status"] in {"MISSING_TIME", "INVALID_TIME"}:
            invalid_activity_times += 1
        elif time_facts["time_validation_status"] == "DURATION_MISMATCH":
            mismatched_activity_times += 1
        details = str(row.get("operation_details", "") or "")
        normalized_details = normalize_translation_paragraph(details)
        cursor.execute(
            """
            INSERT INTO dpr_operation
              (daily_report_id, source_row_no, source_from_text, source_to_text,
               started_at, ended_at, hours, hours_source, clock_hours, duration_variance_hours,
               cross_midnight_flag, time_validation_status, op_code, op_sub,
               work_category_code, work_subcategory_code, source_op_type,
               operation_details, operation_details_normalized, description_hash,
               source_hash, created_by, updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
              source_from_text=VALUES(source_from_text), source_to_text=VALUES(source_to_text),
              started_at=VALUES(started_at), ended_at=VALUES(ended_at), hours=VALUES(hours),
              hours_source=VALUES(hours_source),
              clock_hours=VALUES(clock_hours), duration_variance_hours=VALUES(duration_variance_hours),
              cross_midnight_flag=VALUES(cross_midnight_flag),
              time_validation_status=VALUES(time_validation_status), op_code=VALUES(op_code),
              op_sub=VALUES(op_sub), work_category_code=VALUES(work_category_code),
              work_subcategory_code=VALUES(work_subcategory_code),
              source_op_type=VALUES(source_op_type), operation_details=VALUES(operation_details),
              operation_details_normalized=VALUES(operation_details_normalized),
              description_hash=VALUES(description_hash), source_hash=VALUES(source_hash),
              updated_by=VALUES(updated_by), version=version+1
            """,
            (
                daily_report_id,
                row_no,
                time_facts["source_from_text"],
                time_facts["source_to_text"],
                time_facts["started_at"],
                time_facts["ended_at"],
                hours,
                hours_source,
                time_facts["clock_hours"],
                time_facts["duration_variance_hours"],
                time_facts["cross_midnight_flag"],
                time_facts["time_validation_status"],
                str(row.get("op_code", "") or ""),
                str(row.get("op_sub", "") or ""),
                standardize_operation_code(row.get("op_code")),
                standardize_operation_code(row.get("op_sub"), level="subcategory"),
                str(row.get("system_op_type", "") or row.get("op_type", "") or "").upper(),
                details,
                normalized_details,
                hashlib.sha256(normalized_details.encode("utf-8")).hexdigest() if normalized_details else "",
                source_hash,
                actor,
                actor,
            ),
        )
        cursor.execute(
            "SELECT id FROM dpr_operation WHERE daily_report_id=%s AND source_row_no=%s",
            (daily_report_id, row_no),
        )
        activity_id = int((cursor.fetchone() or {})["id"])
        upsert_activity_classification(cursor, activity_id, row)

    if source_rows:
        placeholders = ",".join(["%s"] * len(source_rows))
        cursor.execute(
            f"DELETE FROM dpr_operation WHERE daily_report_id=%s AND source_row_no NOT IN ({placeholders})",
            [daily_report_id, *sorted(source_rows)],
        )
    else:
        cursor.execute("DELETE FROM dpr_operation WHERE daily_report_id=%s", (daily_report_id,))

    cursor.execute(
        "SELECT COUNT(*) AS count_value FROM dpr_operation activity "
        "LEFT JOIN dpr_operation_classification classification ON classification.activity_id=activity.id "
        "WHERE activity.daily_report_id=%s "
        "AND COALESCE(classification.confirmation_status,'PENDING') NOT IN ('CONFIRMED','AUTO_CONFIRMED')",
        (daily_report_id,),
    )
    pending_classifications = int((cursor.fetchone() or {}).get("count_value", 0) or 0)

    _refresh_quality_issues(
        cursor,
        record_id=record_id,
        report_type=report_type,
        rig_id=rig_id,
        well_id=well_id,
        resolution=resolution,
        pending_classifications=pending_classifications,
        invalid_activity_hours=invalid_activity_hours,
        invalid_activity_times=invalid_activity_times,
        mismatched_activity_times=mismatched_activity_times,
        fields=fields,
        actor=actor,
    )
    boundary_hours = refresh_boundary_hour_issues(
        cursor,
        report_type=report_type,
        well_id=well_id,
        wellbore=str(fields.get("wellbore", "") or ""),
        actor=actor,
    )
    if job_id:
        if rig_id:
            _sync_job_rig_assignment(cursor, job_id=job_id, rig_id=rig_id, report_date=report_date or "", actor=actor)
        _sync_job_events(cursor, job_id=job_id, record_id=record_id, report_type=report_type, report_date=report_date or "", fields=fields, actor=actor)
        _sync_depth_progress(cursor, job_id=job_id, record_id=record_id, report_date=report_date or "", fields=fields, actor=actor)
        _sync_incident(cursor, job_id=job_id, record_id=record_id, report_date=report_date or "", fields=fields, actor=actor)
    return {
        "record_id": record_id,
        "rig_id": rig_id,
        "well_id": well_id,
        "project_id": project_id,
        "job_id": job_id,
        "match_status": match_status,
        "normalization_status": normalization_status,
        "activity_count": len(source_rows),
        "pending_classifications": pending_classifications,
        "total_hours": round(total_hours, 3),
        "hours_validation_required": record_id in boundary_hours["boundary_record_ids"],
        "first_report_date": boundary_hours["first_report_date"],
        "last_report_date": boundary_hours["last_report_date"],
    }


def synchronize_structured_report_facts(
    cursor: Any,
    *,
    daily_report_id: int,
    report_type: str,
    fields: dict[str, Any],
    payload: dict[str, Any],
    actor: str = "system",
) -> None:
    """Write typed report extensions while the JSON audit payload remains unchanged."""
    summary_fields = {
        "event_name": _text(fields.get("event")),
        "primary_reason": _text(fields.get("primaryReason")),
        "afe_number": _text(fields.get("afeNumber")),
        "reference_datum_ft": parse_numeric_field("refDatum", fields.get("refDatum")),
        "current_operation": _nullable_text(fields.get("currentOps")),
        "summary_24h": _nullable_text(fields.get("summary24h")),
        "forecast_24h": _nullable_text(fields.get("forecast24h")),
        "other_remarks": _nullable_text(fields.get("otherRemarks")),
    }
    _upsert_typed_extension(cursor, "dpr_report_summary", daily_report_id, summary_fields, fields, actor)

    typed_tables = {
        "drilling": ("dpr_drilling_report", "dpr_drilling_fluid_property"),
        "completion": ("dpr_completion_report",),
        "workover": ("dpr_workover_report",),
        "move": ("dpr_move_report",),
    }
    all_typed_tables = {table for tables in typed_tables.values() for table in tables}
    active_tables = set(typed_tables.get(report_type, ()))
    for table in all_typed_tables - active_tables:
        cursor.execute(f"DELETE FROM {table} WHERE daily_report_id=%s", (daily_report_id,))

    if report_type == "drilling":
        drilling_fields = {
            "measured_depth_ft": _nullable_float(fields.get("todayMd")),
            "previous_measured_depth_ft": _nullable_float(fields.get("prevMd")),
            "daily_progress_ft": _nullable_float(fields.get("progress")),
            "rotary_hours": _nullable_float(fields.get("rotHrsToday")),
            "previous_casing_description": _text(fields.get("lastCasing")),
            "previous_casing_size_in": parse_numeric_field("lastCasingSize", fields.get("lastCasingSize")),
            "previous_casing_depth_ft": _nullable_float(fields.get("lastCasingDepth")),
            "next_casing_description": _text(fields.get("nextCasing")),
            "next_casing_size_in": parse_numeric_field("nextCasingSize", fields.get("nextCasingSize")),
            "next_casing_depth_ft": _nullable_float(fields.get("nextCasingDepth")),
            "formation_test_type": _text(fields.get("formTestType")).upper(),
            "formation_test_emw_ppg": parse_numeric_field("formTestEmw", fields.get("formTestEmw")),
            "last_bop_test_date": _nullable_date(fields.get("lastBopPressTest")),
            "pump_rate_gpm": _nullable_float(fields.get("pumpRate")),
            "pump_pressure_psi": _nullable_float(fields.get("pumpPress")),
            "string_weight_up_kip": parse_numeric_field("stringWeightUp", fields.get("stringWeightUp")),
            "string_weight_down_kip": parse_numeric_field("stringWeightDown", fields.get("stringWeightDown")),
            "torque_off_bottom_ft_lbf": parse_numeric_field("torqueOffBottom", fields.get("torqueOffBottom")),
            "torque_on_bottom_ft_lbf": parse_numeric_field("torqueOnBottom", fields.get("torqueOnBottom")),
            "bit_sequence_no": _text(fields.get("bitNo")),
            "bit_size_in": _nullable_float(fields.get("bitSize")),
            "bit_manufacturer": _text(fields.get("bitManufacturer")),
            "bit_serial_no": _text(fields.get("bitSerial")),
            "bit_wear_iodl": _text(fields.get("bitWearIodl")),
            "bit_wear_bgor": _text(fields.get("bitWearBgor")),
            "bha_no": _text(fields.get("bhaNo")),
            "bha_md_in_ft": _nullable_float(fields.get("bhaMdIn")),
            "bha_md_out_ft": _nullable_float(fields.get("bhaMdOut")),
            "bha_total_length_ft": _nullable_float(fields.get("bhaTotalLength")),
            "safety_incident_flag": _text(fields.get("safetyIncident")),
            "environmental_incident_flag": _text(fields.get("environmentIncident")),
            "days_since_recordable_incident": _nullable_int(fields.get("daysSinceRi")),
            "days_since_lost_time_accident": _nullable_int(fields.get("daysSinceLta")),
            "incident_comments": _nullable_text(fields.get("incidentComments")),
        }
        combined_up, combined_down = parse_string_weight_pair(fields.get("stringWeightUpDown"))
        if drilling_fields["string_weight_up_kip"] is None:
            drilling_fields["string_weight_up_kip"] = combined_up
        if drilling_fields["string_weight_down_kip"] is None:
            drilling_fields["string_weight_down_kip"] = combined_down
        _upsert_typed_extension(cursor, "dpr_drilling_report", daily_report_id, drilling_fields, fields, actor)
        fluid_fields = {
            "mud_engineer": _text(fields.get("mudEngineer")),
            "sample_source": _text(fields.get("sampleFrom")),
            "mud_type": _text(fields.get("mudType")),
            "sample_time": _nullable_time(fields.get("mudTime")),
            "sample_depth_ft": _nullable_float(fields.get("mudMd")),
            "density_ppg": _nullable_float(fields.get("mudDensity")),
            "mud_temperature_f": _nullable_float(fields.get("mudTemperature")),
            "rheology_temperature_f": _nullable_float(fields.get("rheologyTemp")),
            "funnel_viscosity_sec_per_qt": _nullable_float(fields.get("viscosity")),
            "plastic_viscosity_cp": _nullable_float(fields.get("pv")),
            "yield_point_lb_per_100ft2": _nullable_float(fields.get("yp")),
            "gel_10s_lb_per_100ft2": _nullable_float(fields.get("gel10s")),
            "gel_10m_lb_per_100ft2": _nullable_float(fields.get("gel10m")),
            "gel_30m_lb_per_100ft2": _nullable_float(fields.get("gel30m")),
            "api_fluid_loss_ml_30min": _nullable_float(fields.get("apiWl")),
            "oil_percent": _nullable_float(fields.get("oilPercent")),
            "water_percent": _nullable_float(fields.get("waterPercent")),
            "sand_percent": _nullable_float(fields.get("sand")),
            "equivalent_circulating_density_ppg": _nullable_float(fields.get("ecd")),
            "comments": _nullable_text(fields.get("mudComments")),
        }
        _upsert_typed_extension(cursor, "dpr_drilling_fluid_property", daily_report_id, fluid_fields, fields, actor)
    elif report_type in {"completion", "workover"}:
        service_fields = {
            "description": _nullable_text(fields.get("description")),
            "operation_start_date": _nullable_date(fields.get("operationStartDate")),
            "afe_cost_usd": _nullable_float(fields.get("afeCost")),
            "daily_cost_usd": _nullable_float(fields.get("dailyCost")),
            "cumulative_cost_usd": _nullable_float(fields.get("cumulativeCost")),
            "supervisor_1": _text(fields.get("supervisor1")),
            "supervisor_2": _text(fields.get("supervisor2")),
            "engineer": _text(fields.get("engineer")),
            "pam_engineer": _text(fields.get("pamEngineer")),
            "geologist": _text(fields.get("geologist")),
            "total_personnel": _nullable_int(fields.get("totalPersonnel")),
            "safety_comments": _nullable_text(fields.get("safetyComments")),
        }
        if report_type == "workover":
            service_fields = {"workover_no": _text(fields.get("workoverNo")), **service_fields}
        _upsert_typed_extension(cursor, f"dpr_{report_type}_report", daily_report_id, service_fields, fields, actor)
    elif report_type == "move":
        afe_depth, afe_days = parse_afe_depth_days(fields.get("afeMdDays"))
        operation_text = " ".join(
            _text(row.get("operation_details"))
            for row in (payload.get("operations", []) or [])
            if isinstance(row, dict)
        )
        loads_today, loads_total, loads_planned = _move_load_counts(
            fields.get("summary24h"), fields.get("otherRemarks"), operation_text
        )
        move_fields = {
            "ground_elevation_ft": _nullable_float(fields.get("groundElev")),
            "afe_design_depth_ft": afe_depth,
            "afe_design_days": afe_days,
            "rig_move_progress_pct": _percentage_from_text(fields.get("summary24h"), "RIG MOVE"),
            "rig_up_progress_pct": _percentage_from_text(fields.get("summary24h"), "RIG UP"),
            "loads_moved_today": loads_today,
            "loads_moved_total": loads_total,
            "loads_planned_total": loads_planned,
            "wellbore_prefix": _text(fields.get("wellborePrefix")),
        }
        _upsert_typed_extension(cursor, "dpr_move_report", daily_report_id, move_fields, fields, actor)

    shared_bulk_mapping = {
        "material_name": ("bulk", _text), "opening_quantity": ("qty_start", _nullable_float),
        "received_quantity": ("qty_received", _nullable_float),
        "used_quantity": ("qty_used", _nullable_float), "closing_quantity": ("qty_end", _nullable_float),
        "quantity_unit_code": ("unit_code", _inventory_unit_code),
        "quantity_balance_status": ("balance_status", _inventory_balance_status),
    }
    shared_mud_product_mapping = {
        "product_name": ("product", _text), "quantity_unit": ("unit", _text),
        "received_quantity": ("received", _nullable_float), "used_quantity": ("used", _nullable_float),
        "returned_quantity": ("returned", _nullable_float), "ending_quantity": ("ending", _nullable_float),
    }
    shared_perforation_mapping = {
        "formation_name": ("formation", _text), "top_measured_depth_ft": ("top_md", _nullable_float),
        "base_measured_depth_ft": ("base_md", _nullable_float), "interval_length_ft": ("length", _nullable_float),
        "shot_density_per_ft": ("density", _nullable_float), "charge_description": ("charges", _text),
        "phase_angle_deg": ("phase", _nullable_float), "penetration_in": ("penetration", _nullable_float),
        "hole_diameter_in": ("diameter", _nullable_float), "perforation_date": ("date", _nullable_date),
        "interval_status": ("status", _text), "comments": ("comments", _nullable_text),
    }
    child_specs_by_type = {
        "drilling": {
            "dpr_drilling_directional_survey": ("survey_data", {
            "measured_depth_ft": ("md", _nullable_float), "inclination_deg": ("incl", _nullable_float),
            "azimuth_deg": ("azi", _nullable_float), "true_vertical_depth_ft": ("tvd", _nullable_float),
            "vertical_section_ft": ("vse", _nullable_float), "north_south_ft": ("ns", _nullable_float),
            "east_west_ft": ("ew", _nullable_float),
            "dogleg_severity_deg_per_100ft": ("dls", _nullable_float), "build_rate_deg_per_100ft": ("build", _nullable_float),
            }),
            "dpr_drilling_bha_component": ("bha_components", {
            "component_name": ("component", _text), "outside_diameter_in": ("od", _nullable_float),
            "inside_diameter_in": ("id", _nullable_float), "joint_count": ("joints", _nullable_int),
            "component_length_ft": ("length", _nullable_float),
            }),
            "dpr_drilling_bulk_inventory": ("bulks", shared_bulk_mapping),
            "dpr_drilling_fluid_loss": ("fluid_losses", {
            "injected_volume_bbl": ("injected_volume_bbl", _nullable_float),
            "returned_volume_bbl": ("returned_volume_bbl", _nullable_float),
            }),
        },
        "completion": {
            "dpr_completion_bulk_inventory": ("bulks", shared_bulk_mapping),
            "dpr_completion_mud_product": ("mud_products", shared_mud_product_mapping),
            "dpr_completion_perforation_interval": ("perforation_intervals", shared_perforation_mapping),
        },
        "workover": {
            "dpr_workover_bulk_inventory": ("bulks", shared_bulk_mapping),
            "dpr_workover_mud_product": ("mud_products", shared_mud_product_mapping),
            "dpr_workover_perforation_interval": ("perforation_intervals", shared_perforation_mapping),
        },
        "move": {},
    }
    child_specs = child_specs_by_type.get(report_type, {})
    all_child_tables = {
        table
        for type_specs in child_specs_by_type.values()
        for table in type_specs
    }
    for table in all_child_tables - set(child_specs):
        cursor.execute(f"DELETE FROM {table} WHERE daily_report_id=%s", (daily_report_id,))
    for table, (module_name, mapping) in child_specs.items():
        rows = [row for row in (payload.get(module_name, []) or []) if isinstance(row, dict)]
        _replace_typed_children(cursor, table, daily_report_id, rows, mapping, actor)


def _upsert_typed_extension(
    cursor: Any,
    table: str,
    daily_report_id: int,
    values: dict[str, Any],
    source: dict[str, Any],
    actor: str,
) -> None:
    if not _has_business_value(values.values()):
        cursor.execute(f"DELETE FROM {table} WHERE daily_report_id=%s", (daily_report_id,))
        return
    columns = ["daily_report_id", *values, "source_hash", "created_by", "updated_by"]
    args = [daily_report_id, *values.values(), _content_hash(source), actor, actor]
    updates = [f"{column}=VALUES({column})" for column in values]
    updates.extend(["source_hash=VALUES(source_hash)", "updated_by=VALUES(updated_by)", "version=version+1"])
    cursor.execute(
        f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(['%s'] * len(columns))}) "
        f"ON DUPLICATE KEY UPDATE {','.join(updates)}",
        args,
    )


def _replace_typed_children(
    cursor: Any,
    table: str,
    daily_report_id: int,
    rows: list[dict[str, Any]],
    mapping: dict[str, tuple[str, Any]],
    actor: str,
) -> None:
    cursor.execute(f"DELETE FROM {table} WHERE daily_report_id=%s", (daily_report_id,))
    columns = ["daily_report_id", "source_row_no", *mapping, "source_hash", "created_by", "updated_by"]
    statement = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(['%s'] * len(columns))})"
    for row_no, row in enumerate(rows, start=1):
        values = [converter(row.get(source_name)) for source_name, converter in mapping.values()]
        if not _has_business_value(values):
            continue
        cursor.execute(statement, [daily_report_id, row_no, *values, _content_hash(row), actor, actor])


def _has_business_value(values: Any) -> bool:
    """Return whether a typed fact contains at least one meaningful business value."""
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return True
    return False


def _content_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _text(value: object) -> str:
    return str(value or "").strip()


def _nullable_text(value: object) -> str | None:
    text = _text(value)
    return text or None


def _nullable_int(value: object) -> int | None:
    number = _nullable_float(value)
    return int(number) if number is not None else None


def _nullable_report_no(value: object) -> int | None:
    text = _text(value)
    return int(text) if re.fullmatch(r"\d+", text) else None


def _nullable_date(value: object) -> str | None:
    text = _text(value)[:10]
    if not text:
        return None
    for pattern in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, pattern).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _report_normalization_status(report_date: object) -> str:
    """Treat missing master-data links as assignment quality, not fact failure."""

    return "NORMALIZED" if _nullable_date(report_date) else "NORMALIZATION_FAILED"


def _nullable_time(value: object) -> str | None:
    text = _text(value)
    match = re.search(r"\b(\d{1,2}):(\d{2})\b", text)
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    return f"{hour:02d}:{minute:02d}:00" if hour < 24 and minute < 60 else None


def _number_pair(value: object) -> tuple[float | None, float | None]:
    numbers = re.findall(r"[-+]?\d+(?:\.\d+)?", _text(value).replace(",", ""))
    parsed = [float(item) for item in numbers[:2]]
    return (parsed[0] if parsed else None, parsed[1] if len(parsed) > 1 else None)


def refresh_report_master_matches(*, actor: str = "system") -> dict[str, int]:
    """Re-evaluate stored reports after master-data relationships change."""
    counts = {"matched": 0, "unassigned": 0, "ambiguous": 0, "normalization_failed": 0}
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT report.id,report.record_id,report.report_date,report.report_type,
                           report.rig_id,report.well_id,source.rig,source.wellbore
                    FROM dpr_report report
                    JOIN dpr_report_record source ON source.record_id=report.record_id
                    ORDER BY report.id
                    FOR UPDATE
                    """
                )
                reports = list(cursor.fetchall() or [])
                for report in reports:
                    record_id = str(report.get("record_id", "") or "")
                    report_date = str(report.get("report_date", "") or "")[:10]
                    report_type = str(report.get("report_type", "") or "")
                    rig_id = resolve_master_id(cursor, "rig", report.get("rig")) or _positive_int(report.get("rig_id"))
                    well_id = resolve_master_id(cursor, "well", report.get("wellbore")) or _positive_int(report.get("well_id"))
                    resolution = resolve_project_assignment(
                        cursor,
                        report_date=report_date,
                        report_type=report_type,
                        rig_id=rig_id,
                        well_id=well_id,
                    )
                    match_status = str(resolution.get("status", "UNASSIGNED") or "UNASSIGNED")
                    match_message = str(resolution.get("message", "") or "")
                    project_id = _positive_int(resolution.get("project_id"))
                    job_id = _positive_int(resolution.get("job_id"))
                    normalization_status = _report_normalization_status(report_date)
                    cursor.execute(
                        """
                        UPDATE dpr_report
                        SET project_id=%s,job_id=%s,rig_id=%s,well_id=%s,match_status=%s,
                            match_message=%s,normalization_status=%s,updated_by=%s,version=version+1
                        WHERE id=%s
                        """,
                        (
                            project_id, job_id, rig_id, well_id, match_status,
                            match_message, normalization_status, actor, report["id"],
                        ),
                    )
                    cursor.execute(
                        """
                        UPDATE dpr_report_record
                        SET project_id=%s,job_id=%s,rig_id=%s,well_id=%s,
                            master_match_status=%s,master_match_message=%s
                        WHERE record_id=%s
                        """,
                        (project_id, job_id, rig_id, well_id, match_status, match_message, record_id),
                    )
                    cursor.execute(
                        """
                        UPDATE dq_issue
                        SET status='RESOLVED',resolution_note='主数据关系变更后自动重算',resolved_at=NOW(),
                            resolved_by=%s,updated_by=%s,version=version+1
                        WHERE record_id=%s AND status='OPEN'
                          AND issue_type IN ('MASTER_RIG_UNRESOLVED','MASTER_WELL_UNRESOLVED',
                                             'PROJECT_UNASSIGNED','PROJECT_AMBIGUOUS')
                        """,
                        (actor, actor, record_id),
                    )
                    if not rig_id:
                        _upsert_issue(cursor, record_id, "MASTER_RIG_UNRESOLVED", "error", {"message": "井队未匹配主数据"}, actor)
                    if not well_id:
                        _upsert_issue(cursor, record_id, "MASTER_WELL_UNRESOLVED", "error", {"message": "井未匹配主数据"}, actor)
                    if match_status in {"UNASSIGNED", "AMBIGUOUS"}:
                        _upsert_issue(
                            cursor,
                            record_id,
                            f"PROJECT_{match_status}",
                            "error",
                            {"message": match_message, "matches": resolution.get("matches", [])},
                            actor,
                        )
                    if normalization_status != "NORMALIZED":
                        counts["normalization_failed"] += 1
                    elif match_status == "MATCHED":
                        counts["matched"] += 1
                    elif match_status == "AMBIGUOUS":
                        counts["ambiguous"] += 1
                    else:
                        counts["unassigned"] += 1
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return counts


def list_quality_issues(*, status: str = "OPEN", issue_type: str = "", limit: int = 1000) -> list[dict[str, Any]]:
    clauses: list[str] = []
    args: list[object] = []
    if status:
        clauses.append("status=%s")
        args.append(status)
    if issue_type:
        clauses.append("issue_type=%s")
        args.append(issue_type)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    args.append(max(1, min(int(limit), 5000)))
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM dq_issue {where} ORDER BY severity DESC, updated_at DESC LIMIT %s",
                args,
            )
            rows = cursor.fetchall()
    return [_json_row(row) for row in rows]


def resolve_quality_issue(issue_id: int, *, note: str, actor: str, expected_version: int) -> dict[str, Any]:
    if not note.strip():
        raise ValueError("解决质量问题必须填写说明。")
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE dq_issue
                    SET status='RESOLVED', resolution_note=%s, resolved_at=NOW(), resolved_by=%s,
                        updated_by=%s, version=version+1
                    WHERE id=%s AND version=%s
                    """,
                    (note, actor, actor, issue_id, expected_version),
                )
                if cursor.rowcount != 1:
                    raise RuntimeError("质量问题已被其他用户修改，请刷新后重试。")
                cursor.execute("SELECT * FROM dq_issue WHERE id=%s", (issue_id,))
                row = cursor.fetchone()
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return _json_row(row or {})


def _refresh_quality_issues(
    cursor: Any,
    *,
    record_id: str,
    report_type: str,
    rig_id: int | None,
    well_id: int | None,
    resolution: dict[str, Any],
    pending_classifications: int,
    invalid_activity_hours: int,
    invalid_activity_times: int,
    mismatched_activity_times: int,
    fields: dict[str, Any],
    actor: str,
) -> None:
    cursor.execute(
        """
        UPDATE dq_issue
        SET status='RESOLVED', resolution_note='自动复检已通过', resolved_at=NOW(),
            resolved_by='system', updated_by='system', version=version+1
        WHERE record_id=%s AND status='OPEN'
        """,
        (record_id,),
    )
    if not rig_id:
        _upsert_issue(cursor, record_id, "MASTER_RIG_UNRESOLVED", "error", {"message": "井队未匹配主数据"}, actor)
    if not well_id:
        _upsert_issue(cursor, record_id, "MASTER_WELL_UNRESOLVED", "error", {"message": "井未匹配主数据"}, actor)
    status = str(resolution.get("status", "") or "")
    if status in {"UNASSIGNED", "AMBIGUOUS"}:
        _upsert_issue(
            cursor,
            record_id,
            f"PROJECT_{status}",
            "error",
            {"message": resolution.get("message", ""), "matches": resolution.get("matches", [])},
            actor,
        )
    if pending_classifications:
        _upsert_issue(
            cursor,
            record_id,
            "CLASSIFICATION_PENDING",
            "warning",
            {"pending_count": pending_classifications},
            actor,
        )
    if invalid_activity_hours:
        _upsert_issue(
            cursor,
            record_id,
            "ACTIVITY_HOURS_INVALID",
            "error",
            {"invalid_count": invalid_activity_hours, "message": "作业时长缺失或不是纯数字"},
            actor,
        )
    if invalid_activity_times:
        _upsert_issue(
            cursor,
            record_id,
            "ACTIVITY_TIME_INVALID",
            "error",
            {"invalid_count": invalid_activity_times, "message": "作业起止时间缺失或无法解析"},
            actor,
        )
    if mismatched_activity_times:
        _upsert_issue(
            cursor,
            record_id,
            "ACTIVITY_DURATION_MISMATCH",
            "error",
            {"mismatch_count": mismatched_activity_times, "message": "申报时长与起止时间计算值不一致"},
            actor,
        )
    if _nullable_date(fields.get("reportDate")) is None:
        _upsert_issue(
            cursor,
            record_id,
            "REPORT_DATE_INVALID",
            "error",
            {"field": "reportDate", "source_value": _text(fields.get("reportDate"))},
            actor,
        )
    source_report_no = _text(fields.get("reportNo"))
    if _nullable_report_no(source_report_no) is None:
        _upsert_issue(
            cursor,
            record_id,
            "REPORT_NO_INVALID",
            "warning",
            {"field": "reportNo", "source_value": source_report_no},
            actor,
        )
    numeric_fields = {
        "refDatum": "参考基准",
        "lastCasingSize": "上一层套管尺寸",
        "nextCasingSize": "下一层套管尺寸",
        "formTestEmw": "地层测试EMW",
        "torqueOffBottom": "离底扭矩",
        "torqueOnBottom": "井底扭矩",
    }
    for field_code, label in numeric_fields.items():
        raw = _text(fields.get(field_code))
        if raw and raw.lower() not in {"-", "/", "n/a", "none", "null"} and parse_numeric_field(field_code, raw) is None:
            _upsert_issue(
                cursor,
                record_id,
                f"NUMERIC_PARSE_FAILED_{field_code.upper()}",
                "error",
                {"field": field_code, "label": label, "source_value": raw},
                actor,
            )
    combined_weight = _text(fields.get("stringWeightUpDown"))
    if combined_weight and combined_weight not in {"-", "/"}:
        up_value, down_value = parse_string_weight_pair(combined_weight)
        if up_value is None or down_value is None:
            _upsert_issue(
                cursor,
                record_id,
                "NUMERIC_PARSE_FAILED_STRING_WEIGHT",
                "error",
                {"field": "stringWeightUpDown", "label": "钻柱上提/下放重量", "source_value": combined_weight},
                actor,
            )


def refresh_boundary_hour_issues(
    cursor: Any,
    *,
    report_type: str,
    well_id: int | None,
    wellbore: str,
    actor: str = "system",
) -> dict[str, Any]:
    """Rebuild 24-hour checks for every contiguous report segment boundary."""
    normalized_type = str(report_type or "").strip().lower()
    normalized_wellbore = str(wellbore or "").strip()
    if not normalized_type or (not well_id and not normalized_wellbore):
        return {
            "boundary_record_ids": [],
            "first_report_date": "",
            "last_report_date": "",
        }

    group_sql = "r.well_id=%s" if well_id else "r.well_id IS NULL AND UPPER(TRIM(r.wellbore))=UPPER(TRIM(%s))"
    group_value: object = well_id if well_id else normalized_wellbore
    cursor.execute(
        f"""
        SELECT r.record_id, DATE_FORMAT(d.report_date,'%%Y-%%m-%%d') AS report_date,
               r.validation_warnings, COUNT(a.id) AS activity_count,
               COALESCE(SUM(a.hours),0) AS total_hours
        FROM dpr_report_record r
        JOIN dpr_report d ON d.record_id=r.record_id
        LEFT JOIN dpr_operation a ON a.daily_report_id=d.id
        WHERE r.report_type=%s AND {group_sql} AND d.report_date IS NOT NULL
        GROUP BY r.record_id, d.report_date, r.validation_warnings
        ORDER BY d.report_date, r.record_id
        """,
        (normalized_type, group_value),
    )
    rows = list(cursor.fetchall() or [])
    record_ids = [str(row.get("record_id", "") or "") for row in rows if row.get("record_id")]
    if record_ids:
        placeholders = ",".join(["%s"] * len(record_ids))
        cursor.execute(
            f"""
            UPDATE dq_issue
            SET status='RESOLVED', resolution_note='边界日期自动重算', resolved_at=NOW(),
                resolved_by='system', updated_by=%s, version=version+1
            WHERE issue_type='HOURS_NOT_24' AND status='OPEN'
              AND record_id IN ({placeholders})
            """,
            [actor, *record_ids],
        )

    first_date, last_date = _boundary_report_dates(rows)
    segment_roles: dict[str, tuple[str, str, str]] = {}
    for segment_first, segment_last in _boundary_report_segments(rows):
        if segment_first == segment_last:
            segment_roles[segment_first] = ("FIRST_AND_LAST", segment_first, segment_last)
        else:
            segment_roles[segment_first] = ("FIRST", segment_first, segment_last)
            segment_roles[segment_last] = ("LAST", segment_first, segment_last)
    boundary_record_ids: list[str] = []
    for row in rows:
        record_id = str(row.get("record_id", "") or "")
        report_date = str(row.get("report_date", "") or "")
        boundary = segment_roles.get(report_date)
        is_boundary = boundary is not None
        if is_boundary:
            boundary_record_ids.append(record_id)
        total_hours = _safe_float(row.get("total_hours"))
        activity_count = int(row.get("activity_count", 0) or 0)
        warning = f"operation hours total {total_hours:.2f}"
        warnings = [
            item.strip()
            for item in str(row.get("validation_warnings", "") or "").split(";")
            if item.strip() and not item.strip().lower().startswith("operation hours total ")
        ]
        if is_boundary and activity_count and abs(total_hours - 24.0) > 0.05:
            warnings.append(warning)
            boundary_role, segment_first, segment_last = boundary
            _upsert_issue(
                cursor,
                record_id,
                "HOURS_NOT_24",
                "warning",
                {
                    "total_hours": round(total_hours, 3),
                    "difference": round(total_hours - 24.0, 3),
                    "report_type": normalized_type,
                    "boundary_role": boundary_role,
                    "first_report_date": segment_first,
                    "last_report_date": segment_last,
                },
                actor,
            )
        cursor.execute(
            "UPDATE dpr_report_record SET validation_status=%s, validation_warnings=%s WHERE record_id=%s",
            ("warning" if warnings else "ok", "; ".join(warnings), record_id),
        )
    return {
        "boundary_record_ids": boundary_record_ids,
        "first_report_date": first_date,
        "last_report_date": last_date,
    }


def _boundary_report_dates(rows: list[dict[str, Any]]) -> tuple[str, str]:
    dates = sorted({str(row.get("report_date", "") or "") for row in rows if row.get("report_date")})
    if not dates:
        return "", ""
    return dates[0], dates[-1]


def _boundary_report_segments(rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    dates = sorted({str(row.get("report_date", "") or "") for row in rows if row.get("report_date")})
    if not dates:
        return []
    segments: list[list[str]] = [[dates[0]]]
    for value in dates[1:]:
        previous = datetime.strptime(segments[-1][-1], "%Y-%m-%d")
        current = datetime.strptime(value, "%Y-%m-%d")
        if current - previous > timedelta(days=1):
            segments.append([value])
        else:
            segments[-1].append(value)
    return [(segment[0], segment[-1]) for segment in segments]


def _upsert_issue(
    cursor: Any,
    record_id: str,
    issue_type: str,
    severity: str,
    details: dict[str, Any],
    actor: str,
) -> None:
    issue_key = f"{record_id}:{issue_type}"
    cursor.execute(
        """
        INSERT INTO dq_issue
          (issue_key, issue_type, severity, entity_type, entity_id, record_id,
           details_json, status, created_by, updated_by)
        VALUES (%s,%s,%s,'report',%s,%s,%s,'OPEN',%s,%s)
        ON DUPLICATE KEY UPDATE
          severity=VALUES(severity), details_json=VALUES(details_json), status='OPEN',
          resolution_note='', resolved_at=NULL, resolved_by='', updated_by=VALUES(updated_by),
          version=version+1
        """,
        (issue_key, issue_type, severity, record_id, record_id, json.dumps(details, ensure_ascii=False), actor, actor),
    )


def _sync_depth_progress(
    cursor: Any,
    *,
    job_id: int,
    record_id: str,
    report_date: str,
    fields: dict[str, Any],
    actor: str,
) -> None:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", report_date or ""):
        return
    measured_depth = _nullable_float(fields.get("todayMd"))
    daily_progress = _nullable_float(fields.get("progress"))
    if measured_depth is None and daily_progress is None:
        return
    cursor.execute(
        """
        INSERT INTO biz_job_depth_progress
          (job_id, record_id, progress_date, measured_depth_ft, daily_progress_ft,
           source_field, created_by, updated_by)
        VALUES (%s,%s,%s,%s,%s,'dpr_report_field',%s,%s)
        ON DUPLICATE KEY UPDATE
          measured_depth_ft=VALUES(measured_depth_ft), daily_progress_ft=VALUES(daily_progress_ft),
          updated_by=VALUES(updated_by), version=version+1
        """,
        (job_id, record_id, report_date, measured_depth, daily_progress, actor, actor),
    )


def _sync_job_rig_assignment(
    cursor: Any,
    *,
    job_id: int,
    rig_id: int,
    report_date: str,
    actor: str,
) -> None:
    del report_date
    cursor.execute(
        """
        SELECT report.report_date, MIN(activity.started_at) AS started_at,
               MAX(activity.ended_at) AS ended_at
        FROM dpr_report report
        LEFT JOIN dpr_operation activity ON activity.daily_report_id=report.id
        WHERE report.job_id=%s AND report.rig_id=%s AND report.report_date IS NOT NULL
        GROUP BY report.id, report.report_date
        ORDER BY report.report_date, report.id
        """,
        (job_id, rig_id),
    )
    windows: list[tuple[datetime, datetime]] = []
    for row in cursor.fetchall() or []:
        report_day = row.get("report_date")
        day_start = datetime.combine(report_day, datetime.min.time())
        start = row.get("started_at") or day_start
        end = row.get("ended_at") or day_start + timedelta(days=1)
        if end > start:
            windows.append((start, end))

    cursor.execute(
        "DELETE FROM rel_job_rig_assignment "
        "WHERE job_id=%s AND rig_id=%s AND change_reason='由标准日报自动建立'",
        (job_id, rig_id),
    )
    for start, end in _merge_activity_windows(windows):
        cursor.execute(
            "INSERT INTO rel_job_rig_assignment "
            "(job_id,rig_id,valid_from,valid_to,status,change_reason,created_by,updated_by) "
            "VALUES (%s,%s,%s,%s,'active','由标准日报自动建立',%s,%s)",
            (job_id, rig_id, start, end, actor, actor),
        )


def _merge_activity_windows(windows: list[tuple[datetime, datetime]]) -> list[tuple[datetime, datetime]]:
    merged: list[tuple[datetime, datetime]] = []
    for start, end in sorted(windows):
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
            continue
        previous_start, previous_end = merged[-1]
        merged[-1] = (previous_start, max(previous_end, end))
    return merged


def _sync_job_events(
    cursor: Any,
    *,
    job_id: int,
    record_id: str,
    report_type: str,
    report_date: str,
    fields: dict[str, Any],
    actor: str,
) -> None:
    event_types = {
        "drilling": ("DRILLING_START", "DRILLING_END"),
        "workover": ("WORKOVER_START", "WORKOVER_END"),
        "completion": ("COMPLETION_START", "COMPLETION_END"),
        "move": ("MOVE_START", "MOVE_END"),
    }
    start_type, end_type = event_types.get(report_type, ("JOB_START", "JOB_END"))
    start_value = _first_date(fields, "operationStartDate", "startDate", "spudDate", "moveStartDate")
    end_value = _first_date(fields, "operationEndDate", "endDate", "completionDate", "moveEndDate")
    for event_type, occurred_on in ((start_type, start_value), (end_type, end_value)):
        if not occurred_on:
            continue
        cursor.execute(
            "SELECT id FROM biz_job_event WHERE job_id=%s AND event_type=%s AND event_date=%s "
            "AND source_record_id=%s LIMIT 1",
            (job_id, event_type, occurred_on, record_id),
        )
        if cursor.fetchone():
            continue
        cursor.execute(
            "INSERT INTO biz_job_event "
            "(job_id,event_type,event_date,event_time,time_precision_code,occurred_at,source_record_id,source_type,confirmation_status,note,created_by,updated_by) "
            "VALUES (%s,%s,%s,NULL,'DATE',NULL,%s,'report','AUTO','从日报显式日期字段提取；来源未提供具体时间',%s,%s)",
            (job_id, event_type, occurred_on, record_id, actor, actor),
        )


def _first_date(fields: dict[str, Any], *names: str) -> str:
    for name in names:
        text = str(fields.get(name, "") or "").strip()[:10]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return text
    return ""


def _sync_incident(
    cursor: Any,
    *,
    job_id: int,
    record_id: str,
    report_date: str,
    fields: dict[str, Any],
    actor: str,
) -> None:
    description = str(fields.get("incidentComments", "") or fields.get("safetyComments", "") or "").strip()
    cursor.execute("DELETE FROM hsse_incident WHERE record_id=%s", (record_id,))
    positive_values = {"y", "yes", "true", "1", "是", "有", "si", "sí"}
    flags = (
        ("SAFETY", str(fields.get("safetyIncident", "") or "").strip().lower()),
        ("ENVIRONMENT", str(fields.get("environmentIncident", "") or "").strip().lower()),
    )
    for incident_type, incident_flag in flags:
        if incident_flag not in positive_values:
            continue
        cursor.execute(
            """
            INSERT INTO hsse_incident
              (job_id, record_id, incident_type, incident_date, incident_time,
               time_precision_code, occurred_at, description, confirmation_status,
               created_by, updated_by)
            VALUES (%s,%s,%s,NULLIF(%s,''),NULL,'DATE',NULL,%s,'PENDING',%s,%s)
            """,
            (job_id, record_id, incident_type, report_date, description or None, actor, actor),
        )


def _activity_datetime(report_date: str, value: object) -> datetime | None:
    text = str(value or "").strip()
    if not report_date or not text:
        return None
    if re.fullmatch(r"\d{1,2}:\d{2}", text):
        hour, minute = text.split(":", 1)
        hour_value, minute_value = int(hour), int(minute)
        if hour_value == 24 and minute_value == 0:
            return datetime.strptime(report_date, "%Y-%m-%d") + timedelta(days=1)
        if hour_value < 24 and minute_value < 60:
            return datetime.strptime(f"{report_date} {hour_value:02d}:{minute_value:02d}", "%Y-%m-%d %H:%M")
    return None


def _activity_datetimes(
    report_date: str, start_value: object, end_value: object, hours: float | None
) -> tuple[datetime | None, datetime | None]:
    start = _activity_datetime(report_date, start_value)
    end = _activity_datetime(report_date, end_value)
    if start is not None and end is not None and end <= start and (hours or 0) > 0:
        end += timedelta(days=1)
    return start, end


def _activity_time_facts(
    report_date: str, start_value: object, end_value: object, hours: float | None
) -> dict[str, Any]:
    """Return persisted time facts without discarding the source clock text."""
    source_from_text = str(start_value or "").strip()[:16]
    source_to_text = str(end_value or "").strip()[:16]
    started_at, ended_at = _activity_datetimes(report_date, source_from_text, source_to_text, hours)
    clock_hours = None
    duration_variance_hours = None
    if started_at is not None and ended_at is not None:
        clock_hours = round((ended_at - started_at).total_seconds() / 3600, 3)
        if hours is not None:
            duration_variance_hours = round(hours - clock_hours, 3)

    if hours is None:
        status = "MISSING_HOURS"
    elif not source_from_text or not source_to_text:
        status = "MISSING_TIME"
    elif started_at is None or ended_at is None:
        status = "INVALID_TIME"
    elif abs(duration_variance_hours or 0.0) > 0.05:
        status = "DURATION_MISMATCH"
    else:
        status = "VALID"
    return {
        "source_from_text": source_from_text,
        "source_to_text": source_to_text,
        "started_at": started_at,
        "ended_at": ended_at,
        "clock_hours": clock_hours,
        "duration_variance_hours": duration_variance_hours,
        "cross_midnight_flag": bool(
            started_at is not None and ended_at is not None and ended_at.date() > started_at.date()
        ),
        "time_validation_status": status,
    }


def _percentage_from_text(value: object, label: str) -> float | None:
    match = re.search(rf"\b{re.escape(label)}\s*:\s*(\d+(?:\.\d+)?)\s*%", _text(value), re.I)
    if not match:
        return None
    number = float(match.group(1))
    return number if 0 <= number <= 100 else None


def _move_load_counts(*values: object) -> tuple[int | None, int | None, int | None]:
    """Extract explicit today/cumulative/planned move-load counts without guessing."""
    text = " ".join(_text(value) for value in values)
    today_patterns = (
        r"CARGAS?\s+(?:ENVIADAS?\s+)?HOY\s*:?\s*(\d+)",
        r"TODAY(?:'S)?\s+LOADS?\s*:?\s*(\d+)",
        r"\b(\d+)\s+CARGAS?\b",
    )
    total_patterns = (
        r"CARGAS?\s+TOTALES?\s+ENVIADAS?\s*:?\s*(\d+)\s*/\s*(\d+)",
        r"TOTAL\s+LOADS?\s+(?:MOVED|SENT)\s*:?\s*(\d+)\s*/\s*(\d+)",
    )
    today = next(
        (int(match.group(1)) for pattern in today_patterns if (match := re.search(pattern, text, re.I))),
        None,
    )
    total_match = next(
        (match for pattern in total_patterns if (match := re.search(pattern, text, re.I))),
        None,
    )
    if total_match is None:
        return today, None, None
    return today, int(total_match.group(1)), int(total_match.group(2))


def _source_version(fields: dict[str, Any], operations: list[dict[str, Any]]) -> str:
    raw = json.dumps({"fields": fields, "operations": operations}, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _activity_hash(row: dict[str, Any]) -> str:
    raw = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _positive_int(value: object) -> int | None:
    try:
        parsed = int(str(value or "0"))
        return parsed if parsed > 0 else None
    except ValueError:
        return None


def _safe_float(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def _nullable_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def _inventory_unit_code(value: object) -> str:
    return _text(value).upper() or "SOURCE_UNSPECIFIED"


def _inventory_balance_status(value: object) -> str:
    return _text(value).upper() or "NOT_CHECKABLE"


def _json_row(row: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat(sep=" ", timespec="seconds")
        elif hasattr(value, "isoformat"):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


def _db_connection():
    from .mysql_database import _connect, initialize_database

    initialize_database()
    return _connect()
