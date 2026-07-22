from __future__ import annotations

import hashlib
import json
import threading
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .database_common import (
    confirmation_group_status as _confirmation_group_status,
    natural_record_id as _natural_record_id,
    normalize_report_type as _normalize_report_type,
    npt_statuses as _npt_statuses,
    safe_float as _safe_float,
    slug as _slug,
)
from .db_config import mysql_settings
from .operation_standardization import (
    OPERATION_CATEGORY_CODE_ALIASES,
    OPERATION_SUBCATEGORY_CODE_ALIASES,
)
from .report_schema import REPORT_TABLES
from .text_structure import normalize_multiline


ROOT = Path(__file__).resolve().parents[1]
INIT_SQL_PATH = ROOT / "db" / "init.sql"
_DATABASE_INITIALIZED = False
_DATABASE_INIT_LOCK = threading.Lock()

# Canonical entities use their business meaning, not a catch-all ``common``
# namespace.  Each tuple contains historical aliases accepted for an in-place,
# data-preserving migration before the canonical CREATE TABLE statements run.
DPR_TABLE_ALIASES = {
    "dpr_report_record": ("report_records", "dpr_common_raw_report"),
    "dpr_report_field": ("report_fields", "dpr_common_raw_field"),
    "dpr_report_row": ("report_rows", "dpr_common_raw_row"),
    "translation_content": ("dpr_common_translation_content",),
    "translation_memory": ("dpr_common_translation_memory",),
    "translation_revision": ("translation_revisions", "dpr_common_translation_revision"),
    "ai_extraction_result": ("ai_extraction_results", "dpr_common_ai_extraction_result"),
    "dpr_report": ("fact_daily_report", "dpr_common_fact_report"),
    "dpr_operation": ("fact_activity", "dpr_common_fact_activity"),
    "dpr_operation_classification_rule": ("time_classification_rule", "dpr_common_time_classification_rule"),
    "dpr_operation_classification": ("fact_time_classification", "dpr_common_fact_time_classification"),
    "dpr_operation_classification_revision": ("time_classification_revision", "dpr_common_time_classification_revision"),
    "biz_job_event": ("fact_job_event", "dpr_common_fact_job_event"),
    "biz_job_depth_progress": ("fact_depth_progress", "dpr_common_fact_depth_progress"),
    "hsse_incident": ("fact_incident", "dpr_common_fact_incident"),
    "dpr_report_summary": ("fact_report_summary", "dpr_common_fact_report_summary"),
    "dq_issue": ("data_quality_issue", "dpr_common_quality_issue"),
    "dpr_drilling_report": ("fact_drilling_parameter", "dpr_drilling_fact_parameter"),
    "dpr_drilling_fluid_property": ("fact_drilling_fluid_property", "dpr_drilling_fact_fluid_property"),
    "dpr_drilling_directional_survey": ("fact_directional_survey", "dpr_drilling_fact_directional_survey"),
    "dpr_drilling_bha_component": ("fact_bha_component", "dpr_drilling_fact_bha_component"),
    "dpr_drilling_fluid_loss": ("fact_fluid_loss", "dpr_drilling_fact_fluid_loss"),
    "dpr_completion_report": ("fact_completion_parameter", "dpr_completion_fact_parameter"),
    "dpr_workover_report": ("fact_workover_parameter", "dpr_workover_fact_parameter"),
    "dpr_move_report": ("fact_move_parameter", "dpr_move_fact_parameter"),
    "dpr_bulk_inventory_legacy": ("fact_material_inventory", "dpr_common_fact_material_inventory"),
    "dpr_mud_product_legacy": ("fact_mud_product_usage", "dpr_common_fact_mud_product_usage"),
    "dpr_perforation_interval_legacy": ("fact_perforation_interval", "dpr_common_fact_perforation_interval"),
}

BASE_RECORD_COLUMNS = [
    "record_id",
    "report_type",
    "source_file",
    "parser",
    "source_page_start",
    "source_page_end",
    "source_report_index",
    "source_report_count",
    "batch_inherited_fields",
    "reportDate",
    "reportNo",
    "wellbore",
    "rig",
    "status",
    "source_language",
    "translation_status",
    "translation_progress",
    "translation_error",
    "translation_version",
    "translation_updated_at",
    "extraction_status", "extraction_progress", "extraction_error", "extraction_version", "extraction_updated_at",
    "validation_status",
    "validation_warnings",
    "locked",
    "confirmation_status",
    "confirmed_at",
    "confirmed_by",
    "confirmation_note",
    "created_at",
    "updated_at",
]

MYSQL_RECORD_COLUMNS = {
    "reportDate": "report_date",
    "reportNo": "report_no",
}


def initialize_database() -> None:
    global _DATABASE_INITIALIZED
    if _DATABASE_INITIALIZED:
        return
    with _DATABASE_INIT_LOCK:
        if _DATABASE_INITIALIZED:
            return
        statements = _sql_statements(INIT_SQL_PATH)
        if not statements:
            return
        with _connect() as connection:
            with connection.cursor() as cursor:
                _migrate_dpr_table_names(cursor)
                view_statements: list[str] = []
                for statement in statements:
                    if _server_scope_statement(statement):
                        continue
                    if statement.lstrip().upper().startswith("CREATE OR REPLACE VIEW"):
                        view_statements.append(statement)
                        continue
                    cursor.execute(statement)
                _migrate_report_type_children(cursor)
                _ensure_report_record_columns(cursor)
                _ensure_ai_extraction_storage_columns(cursor)
                _ensure_project_relationship_columns(cursor)
                _ensure_master_data_v3_columns(cursor)
                _migrate_remove_wellbore_master(cursor)
                _migrate_master_data_v3(cursor)
                _retire_legacy_database_objects(cursor)
                _migrate_replace_daily_cost_with_fluid_loss(cursor)
                _ensure_database_quality_v2(cursor)
                _migrate_move_reports_into_drilling(cursor)
                _ensure_report_record_indexes(cursor)
                _ensure_translation_content_indexes(cursor)
                _ensure_database_comments(cursor)
                for statement in view_statements:
                    cursor.execute(statement)
            connection.commit()
        _DATABASE_INITIALIZED = True


def _migrate_dpr_table_names(cursor: Any) -> None:
    """Rename legacy daily-report tables in place before creating the new schema."""
    cursor.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema=DATABASE() AND table_type='BASE TABLE'"
    )
    existing = {str(row.get("table_name") or row.get("TABLE_NAME") or "") for row in cursor.fetchall()}
    rename_pairs: list[tuple[str, str]] = []
    for canonical_name, aliases in DPR_TABLE_ALIASES.items():
        existing_aliases = [alias for alias in aliases if alias in existing]
        if canonical_name in existing and existing_aliases:
            raise RuntimeError(
                f"Daily-report table migration conflict: {canonical_name} and {existing_aliases} both exist."
            )
        if len(existing_aliases) > 1:
            raise RuntimeError(
                f"Daily-report table migration conflict: aliases {existing_aliases} both exist for {canonical_name}."
            )
        if existing_aliases:
            rename_pairs.append((existing_aliases[0], canonical_name))
    if not rename_pairs:
        return
    rename_sql = ", ".join(f"`{old}` TO `{new}`" for old, new in rename_pairs)
    cursor.execute(f"RENAME TABLE {rename_sql}")


def _migrate_report_type_children(cursor: Any) -> None:
    """Split formerly polymorphic detail rows into report-type-owned tables."""
    audit_columns = [
        "daily_report_id", "source_row_no", "source_hash",
        "created_at", "created_by", "updated_at", "updated_by",
    ]
    split_specs = (
        (
            "dpr_bulk_inventory_legacy",
            {
                "drilling": "dpr_drilling_bulk_inventory",
                "completion": "dpr_completion_bulk_inventory",
                "workover": "dpr_workover_bulk_inventory",
            },
            [
                "material_name", "opening_quantity", "received_quantity", "used_quantity",
                "closing_quantity", "quantity_unit_code", "quantity_balance_status",
            ],
        ),
        (
            "dpr_mud_product_legacy",
            {"completion": "dpr_completion_mud_product", "workover": "dpr_workover_mud_product"},
            [
                "product_name", "quantity_unit", "received_quantity", "used_quantity",
                "returned_quantity", "ending_quantity",
            ],
        ),
        (
            "dpr_perforation_interval_legacy",
            {
                "completion": "dpr_completion_perforation_interval",
                "workover": "dpr_workover_perforation_interval",
            },
            [
                "formation_name", "top_measured_depth_ft", "base_measured_depth_ft",
                "interval_length_ft", "shot_density_per_ft", "charge_description",
                "phase_angle_deg", "penetration_in", "hole_diameter_in", "perforation_date",
                "interval_status", "comments",
            ],
        ),
    )
    for legacy_table, targets, business_columns in split_specs:
        if not _table_exists(cursor, legacy_table):
            continue
        if legacy_table == "dpr_bulk_inventory_legacy":
            legacy_additions = (
                ("received_quantity", "DECIMAL(18,3) NULL AFTER opening_quantity"),
                ("quantity_unit_code", "VARCHAR(32) NOT NULL DEFAULT 'SOURCE_UNSPECIFIED' AFTER closing_quantity"),
                ("quantity_balance_status", "VARCHAR(32) NOT NULL DEFAULT 'NOT_CHECKABLE' AFTER quantity_unit_code"),
            )
            for column, definition in legacy_additions:
                if not _column_exists(cursor, legacy_table, column):
                    cursor.execute(f"ALTER TABLE {legacy_table} ADD COLUMN {column} {definition}")
        columns = ["daily_report_id", "source_row_no", *business_columns, *audit_columns[2:]]
        column_sql = ",".join(columns)
        update_sql = ",".join(
            f"{column}=VALUES({column})"
            for column in columns
            if column not in {"daily_report_id", "source_row_no", "created_at", "created_by"}
        )
        for report_type, target_table in targets.items():
            cursor.execute(
                f"INSERT INTO {target_table} ({column_sql}) "
                f"SELECT {','.join(f'legacy.`{column}`' for column in columns)} "
                f"FROM {legacy_table} legacy JOIN dpr_report report ON report.id=legacy.daily_report_id "
                f"WHERE report.report_type=%s ON DUPLICATE KEY UPDATE {update_sql}",
                (report_type,),
            )
        cursor.execute(
            f"SELECT COUNT(*) AS count_value FROM {legacy_table} legacy "
            "LEFT JOIN dpr_report report ON report.id=legacy.daily_report_id "
            f"WHERE report.id IS NULL OR report.report_type NOT IN ({','.join(['%s'] * len(targets))})",
            tuple(targets),
        )
        unmapped = int((cursor.fetchone() or {}).get("count_value", 0) or 0)
        if unmapped:
            raise RuntimeError(f"Cannot split {legacy_table}: {unmapped} rows have no valid report type.")
        cursor.execute(f"DROP TABLE {legacy_table}")


def _migrate_replace_daily_cost_with_fluid_loss(cursor: Any) -> None:
    """Remove the unused cost-detail module and its fabricated placeholder rows."""
    cursor.execute("DELETE FROM dpr_report_row WHERE module_name='daily_costs'")
    cursor.execute("DROP TABLE IF EXISTS fact_daily_cost")


def _migrate_move_reports_into_drilling(cursor: Any) -> None:
    """Merge the former move report type into drilling, preserving Event detail."""
    if _table_exists(cursor, "dpr_move_report"):
        transferable = [
            column for column in (
                "ground_elevation_ft",
                "afe_design_depth_ft",
                "afe_design_days",
                "rig_move_progress_pct",
                "rig_up_progress_pct",
                "loads_moved_today",
                "loads_moved_total",
                "loads_planned_total",
                "source_hash",
                "version",
                "created_at",
                "created_by",
                "updated_at",
                "updated_by",
            )
            if _column_exists(cursor, "dpr_move_report", column)
            and _column_exists(cursor, "dpr_drilling_report", column)
        ]
        insert_columns = ["daily_report_id", *transferable]
        update_columns = [column for column in transferable if column not in {"created_at", "created_by"}]
        update_clause = ",".join(f"{column}=VALUES({column})" for column in update_columns)
        if not update_clause:
            update_clause = "daily_report_id=VALUES(daily_report_id)"
        cursor.execute(
            f"INSERT INTO dpr_drilling_report ({','.join(insert_columns)}) "
            f"SELECT {','.join(insert_columns)} FROM dpr_move_report "
            f"ON DUPLICATE KEY UPDATE {update_clause}"
        )

    cursor.execute("UPDATE dpr_report_record SET report_type='drilling' WHERE report_type='move'")
    cursor.execute("UPDATE dpr_report SET report_type='drilling' WHERE report_type='move'")
    cursor.execute("UPDATE translation_memory SET report_type='drilling' WHERE report_type='move'")

    cursor.execute(
        "SELECT COUNT(*) AS count_value FROM information_schema.TABLE_CONSTRAINTS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='dpr_report' "
        "AND CONSTRAINT_NAME='ck_fact_daily_report_type' AND CONSTRAINT_TYPE='CHECK'"
    )
    if int((cursor.fetchone() or {}).get("count_value", 0) or 0):
        cursor.execute("ALTER TABLE dpr_report DROP CHECK ck_fact_daily_report_type")
    cursor.execute(
        "ALTER TABLE dpr_report ADD CONSTRAINT ck_fact_daily_report_type "
        "CHECK (report_type IN ('drilling','completion','workover'))"
    )
    cursor.execute("DROP TABLE IF EXISTS dpr_move_report")


def _ensure_database_quality_v2(cursor: Any) -> None:
    """Apply the strong-type and integrity corrections from the schema audit."""
    additions = {
        "dpr_report": (
            ("report_no", "INT UNSIGNED NULL COMMENT '日报序号；原始文本保留在dpr_report_record.report_no' AFTER report_date"),
        ),
        "dpr_operation": (
            ("source_from_text", "VARCHAR(16) NOT NULL DEFAULT '' COMMENT '来源表格FROM原文' AFTER source_row_no"),
            ("source_to_text", "VARCHAR(16) NOT NULL DEFAULT '' COMMENT '来源表格TO原文' AFTER source_from_text"),
            ("hours_source", "VARCHAR(16) NOT NULL DEFAULT 'DECLARED' COMMENT 'DECLARED/CLOCK_DERIVED' AFTER hours"),
            ("clock_hours", "DECIMAL(6,3) NULL COMMENT '由起止时间计算的钟表时长，单位h' AFTER hours"),
            ("duration_variance_hours", "DECIMAL(7,3) NULL COMMENT '申报时长减钟表时长，单位h' AFTER clock_hours"),
            ("cross_midnight_flag", "BOOLEAN NOT NULL DEFAULT FALSE COMMENT '结束时间是否跨至次日' AFTER duration_variance_hours"),
            ("time_validation_status", "VARCHAR(32) NOT NULL DEFAULT 'MISSING_TIME' COMMENT '时效校验状态' AFTER cross_midnight_flag"),
            ("work_category_code", "VARCHAR(80) NOT NULL DEFAULT 'UNSPECIFIED' COMMENT '标准化一级工作分类代码' AFTER op_sub"),
            ("work_subcategory_code", "VARCHAR(160) NOT NULL DEFAULT 'UNSPECIFIED' COMMENT '标准化二级工作分类代码' AFTER work_category_code"),
            ("operation_details_normalized", "TEXT NULL COMMENT '规范化空白后的工作内容描述' AFTER operation_details"),
            ("description_hash", "CHAR(64) NOT NULL DEFAULT '' COMMENT '规范化工作描述SHA-256' AFTER operation_details_normalized"),
        ),
        "dpr_operation_classification": (
            ("productivity_type_code", "VARCHAR(32) NOT NULL DEFAULT '' COMMENT '生产属性类别代码' AFTER productive_flag"),
        ),
        "biz_job_event": (
            ("event_date", "DATE NULL COMMENT '事件日期' AFTER event_type"),
            ("event_time", "TIME NULL COMMENT '事件时间；来源未提供时为NULL' AFTER event_date"),
            ("time_precision_code", "VARCHAR(16) NOT NULL DEFAULT 'DATE' COMMENT '时间精度：DATE或DATETIME' AFTER event_time"),
        ),
        "hsse_incident": (
            ("incident_date", "DATE NULL COMMENT '事故日期' AFTER incident_type"),
            ("incident_time", "TIME NULL COMMENT '事故时间；来源未提供时为NULL' AFTER incident_date"),
            ("time_precision_code", "VARCHAR(16) NOT NULL DEFAULT 'DATE' COMMENT '时间精度：DATE或DATETIME' AFTER incident_time"),
        ),
        "dpr_drilling_report": (
            ("torque_off_bottom_ft_lbf", "DECIMAL(16,3) NULL COMMENT '离底扭矩，单位ft-lbf' AFTER string_weight_down_kip"),
            ("ground_elevation_ft", "DECIMAL(14,3) NULL COMMENT '地面海拔，单位ft；搬迁Event适用' AFTER incident_comments"),
            ("afe_design_depth_ft", "DECIMAL(14,3) NULL COMMENT 'AFE设计井深，单位ft；搬迁Event适用' AFTER ground_elevation_ft"),
            ("afe_design_days", "DECIMAL(10,3) NULL COMMENT 'AFE设计周期，单位d；搬迁Event适用' AFTER afe_design_depth_ft"),
            ("rig_move_progress_pct", "DECIMAL(5,2) NULL COMMENT '搬迁进度，单位%' AFTER afe_design_days"),
            ("rig_up_progress_pct", "DECIMAL(5,2) NULL COMMENT '安装进度，单位%' AFTER rig_move_progress_pct"),
            ("loads_moved_today", "INT UNSIGNED NULL COMMENT '当日搬运载荷数量' AFTER rig_up_progress_pct"),
            ("loads_moved_total", "INT UNSIGNED NULL COMMENT '累计已搬运载荷数量' AFTER loads_moved_today"),
            ("loads_planned_total", "INT UNSIGNED NULL COMMENT '计划搬运载荷总数' AFTER loads_moved_total"),
        ),
        "dpr_drilling_directional_survey": (
            ("east_west_ft", "DECIMAL(14,3) NULL COMMENT '东西位移，单位ft' AFTER north_south_ft"),
        ),
    }
    for table, columns in additions.items():
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        existing = {str(row.get("Field", "") or "") for row in cursor.fetchall()}
        for column, definition in columns:
            if column not in existing:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    cursor.execute("ALTER TABLE dpr_operation MODIFY COLUMN hours DECIMAL(6,3) NULL COMMENT '来源作业时长，单位h；解析失败保留NULL'")
    cursor.execute("ALTER TABLE biz_job_event MODIFY COLUMN occurred_at DATETIME NULL COMMENT '仅来源明确到具体时间时填写'")

    cursor.execute(
        "UPDATE dpr_report d JOIN dpr_report_record r ON r.record_id=d.record_id "
        "SET d.report_no=CASE WHEN r.report_no REGEXP '^[0-9]+$' THEN CAST(r.report_no AS UNSIGNED) ELSE NULL END"
    )
    cursor.execute(
        "UPDATE dpr_operation SET ended_at=DATE_ADD(ended_at,INTERVAL 1 DAY) "
        "WHERE started_at IS NOT NULL AND ended_at IS NOT NULL AND ended_at<=started_at AND COALESCE(hours,0)>0"
    )
    cursor.execute(
        "UPDATE dpr_operation activity "
        "LEFT JOIN dpr_report report ON report.id=activity.daily_report_id "
        "LEFT JOIN dpr_report_row source_row ON source_row.record_id=report.record_id "
        "AND source_row.module_name='operations' AND source_row.row_no=activity.source_row_no "
        "SET activity.source_from_text=COALESCE(NULLIF(JSON_UNQUOTE(JSON_EXTRACT(source_row.row_json,'$.from')),'null'),''),"
        "activity.source_to_text=COALESCE(NULLIF(JSON_UNQUOTE(JSON_EXTRACT(source_row.row_json,'$.to')),'null'),''),"
        "activity.clock_hours=CASE WHEN activity.started_at IS NOT NULL AND activity.ended_at IS NOT NULL "
        "THEN ROUND(TIMESTAMPDIFF(SECOND,activity.started_at,activity.ended_at)/3600,3) END,"
        "activity.duration_variance_hours=CASE WHEN activity.hours IS NOT NULL AND activity.started_at IS NOT NULL "
        "AND activity.ended_at IS NOT NULL THEN ROUND(activity.hours-TIMESTAMPDIFF(SECOND,activity.started_at,activity.ended_at)/3600,3) END,"
        "activity.cross_midnight_flag=CASE WHEN activity.started_at IS NOT NULL AND activity.ended_at IS NOT NULL "
        "AND DATE(activity.ended_at)>DATE(activity.started_at) THEN TRUE ELSE FALSE END,"
        "activity.work_category_code=COALESCE(NULLIF(TRIM(BOTH '_' FROM REGEXP_REPLACE(UPPER(TRIM(activity.op_code)),'[^A-Z0-9]+','_')),''),'UNSPECIFIED'),"
        "activity.work_subcategory_code=COALESCE(NULLIF(TRIM(BOTH '_' FROM REGEXP_REPLACE(UPPER(TRIM(activity.op_sub)),'[^A-Z0-9]+','_')),''),'UNSPECIFIED'),"
        "activity.operation_details_normalized=TRIM(REGEXP_REPLACE(COALESCE(activity.operation_details,''),'[[:space:]]+',' '))"
    )
    cursor.execute(
        "UPDATE dpr_operation SET description_hash=CASE WHEN COALESCE(operation_details_normalized,'')='' THEN '' "
        "ELSE SHA2(operation_details_normalized,256) END,"
        "time_validation_status=CASE WHEN hours IS NULL THEN 'MISSING_HOURS' "
        "WHEN source_from_text='' OR source_to_text='' THEN 'MISSING_TIME' "
        "WHEN started_at IS NULL OR ended_at IS NULL THEN 'INVALID_TIME' "
        "WHEN ABS(COALESCE(duration_variance_hours,0))>0.05 THEN 'DURATION_MISMATCH' ELSE 'VALID' END"
    )
    cursor.executemany(
        "UPDATE dpr_operation SET work_category_code=%s WHERE work_category_code=%s",
        [(canonical, source) for source, canonical in OPERATION_CATEGORY_CODE_ALIASES.items()],
    )
    cursor.executemany(
        "UPDATE dpr_operation SET work_subcategory_code=%s WHERE work_subcategory_code=%s",
        [(canonical, source) for source, canonical in OPERATION_SUBCATEGORY_CODE_ALIASES.items()],
    )
    cursor.execute(
        "UPDATE dpr_operation_classification SET productivity_type_code=productive_flag "
        "WHERE productivity_type_code='' AND productive_flag<>''"
    )
    cursor.execute(
        "UPDATE biz_job_event SET event_date=COALESCE(event_date,DATE(occurred_at)),"
        "event_time=CASE WHEN occurred_at IS NOT NULL AND TIME(occurred_at)<>'00:00:00' THEN TIME(occurred_at) ELSE event_time END,"
        "time_precision_code=CASE WHEN occurred_at IS NOT NULL AND TIME(occurred_at)<>'00:00:00' THEN 'DATETIME' ELSE 'DATE' END"
    )
    cursor.execute("UPDATE biz_job_event SET occurred_at=NULL WHERE time_precision_code='DATE'")
    cursor.execute(
        "UPDATE hsse_incident SET incident_date=COALESCE(incident_date,DATE(occurred_at)),"
        "incident_time=CASE WHEN occurred_at IS NOT NULL AND TIME(occurred_at)<>'00:00:00' THEN TIME(occurred_at) ELSE incident_time END,"
        "time_precision_code=CASE WHEN occurred_at IS NOT NULL AND TIME(occurred_at)<>'00:00:00' THEN 'DATETIME' ELSE 'DATE' END"
    )
    cursor.execute("UPDATE hsse_incident SET occurred_at=NULL WHERE time_precision_code='DATE'")
    cursor.execute(
        "DELETE incident FROM hsse_incident incident JOIN dpr_report_field fields ON fields.record_id=incident.record_id "
        "WHERE (incident.incident_type='SAFETY' AND LOWER(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(fields.fields_json,'$.safetyIncident')),'')) "
        "NOT IN ('y','yes','true','1','是','有','si','sí')) OR "
        "(incident.incident_type='ENVIRONMENT' AND LOWER(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(fields.fields_json,'$.environmentIncident')),'')) "
        "NOT IN ('y','yes','true','1','是','有','si','sí'))"
    )
    for table in (
        "dpr_drilling_bulk_inventory",
        "dpr_completion_bulk_inventory",
        "dpr_workover_bulk_inventory",
    ):
        cursor.execute(
            f"UPDATE {table} SET quantity_unit_code=COALESCE(NULLIF(quantity_unit_code,''),'SOURCE_UNSPECIFIED'),"
            "quantity_balance_status=CASE WHEN received_quantity IS NULL OR quantity_unit_code IN ('','SOURCE_UNSPECIFIED') "
            "THEN 'NOT_CHECKABLE' WHEN ABS(opening_quantity+received_quantity-used_quantity-closing_quantity)<=0.001 "
            "THEN 'BALANCED' ELSE 'UNBALANCED' END"
        )

    _add_index_if_missing(
        cursor, "biz_job_event", "uq_fact_job_event_source_date",
        "job_id,event_type,event_date,source_record_id", unique=True,
    )
    checks = {
        "ck_md_well_coordinates": ("md_well", "(surface_latitude IS NULL OR (surface_latitude>=-90 AND surface_latitude<=90)) AND (surface_longitude IS NULL OR (surface_longitude>=-180 AND surface_longitude<=180))"),
        "ck_md_project_type": ("md_project", "project_type IN ('drilling','completion','workover')"),
        "ck_md_project_npt_allowance": ("md_project", "npt_allowance_hours>=0"),
        "ck_rel_project_team_period": ("rel_project_team_assignment", "valid_to IS NULL OR valid_to>valid_from"),
        "ck_rel_job_rig_period": ("rel_job_rig_assignment", "valid_to IS NULL OR valid_to>valid_from"),
        "ck_fact_daily_report_type": ("dpr_report", "report_type IN ('drilling','completion','workover')"),
        "ck_fact_activity_hours": ("dpr_operation", "hours IS NULL OR (hours>=0 AND hours<=24)"),
        "ck_fact_activity_hours_source": ("dpr_operation", "hours_source IN ('DECLARED','CLOCK_DERIVED')"),
        "ck_fact_activity_timeline": ("dpr_operation", "started_at IS NULL OR ended_at IS NULL OR ended_at>started_at"),
        "ck_fact_activity_source_type": ("dpr_operation", "source_op_type IN ('','P','SC','NPT')"),
        "ck_fact_activity_time_status": ("dpr_operation", "time_validation_status IN ('VALID','DURATION_MISMATCH','MISSING_TIME','INVALID_TIME','MISSING_HOURS')"),
        "ck_fact_time_classification_confidence": ("dpr_operation_classification", "confidence IS NULL OR (confidence>=0 AND confidence<=1)"),
        "ck_fact_directional_survey_values": ("dpr_drilling_directional_survey", "(inclination_deg IS NULL OR (inclination_deg>=0 AND inclination_deg<=180)) AND (azimuth_deg IS NULL OR (azimuth_deg>=0 AND azimuth_deg<360)) AND (dogleg_severity_deg_per_100ft IS NULL OR dogleg_severity_deg_per_100ft>=0)"),
        "ck_fact_bha_component_values": ("dpr_drilling_bha_component", "(outside_diameter_in IS NULL OR outside_diameter_in>=0) AND (inside_diameter_in IS NULL OR inside_diameter_in>=0) AND (joint_count IS NULL OR joint_count>=0) AND (component_length_ft IS NULL OR component_length_ft>=0) AND (outside_diameter_in IS NULL OR inside_diameter_in IS NULL OR outside_diameter_in>=inside_diameter_in)"),
        "ck_completion_perforation_interval_values": ("dpr_completion_perforation_interval", "(top_measured_depth_ft IS NULL OR base_measured_depth_ft IS NULL OR base_measured_depth_ft>=top_measured_depth_ft) AND (interval_length_ft IS NULL OR interval_length_ft>=0)"),
        "ck_workover_perforation_interval_values": ("dpr_workover_perforation_interval", "(top_measured_depth_ft IS NULL OR base_measured_depth_ft IS NULL OR base_measured_depth_ft>=top_measured_depth_ft) AND (interval_length_ft IS NULL OR interval_length_ft>=0)"),
        "ck_fact_drilling_move_progress": ("dpr_drilling_report", "rig_move_progress_pct IS NULL OR (rig_move_progress_pct>=0 AND rig_move_progress_pct<=100)"),
        "ck_fact_drilling_rig_up_progress": ("dpr_drilling_report", "rig_up_progress_pct IS NULL OR (rig_up_progress_pct>=0 AND rig_up_progress_pct<=100)"),
        "ck_drilling_bulk_inventory_nonnegative": (
            "dpr_drilling_bulk_inventory",
            "(opening_quantity IS NULL OR opening_quantity>=0) AND (received_quantity IS NULL OR received_quantity>=0) "
            "AND (used_quantity IS NULL OR used_quantity>=0) AND (closing_quantity IS NULL OR closing_quantity>=0)",
        ),
        "ck_completion_bulk_inventory_nonnegative": (
            "dpr_completion_bulk_inventory",
            "(opening_quantity IS NULL OR opening_quantity>=0) AND (received_quantity IS NULL OR received_quantity>=0) "
            "AND (used_quantity IS NULL OR used_quantity>=0) AND (closing_quantity IS NULL OR closing_quantity>=0)",
        ),
        "ck_workover_bulk_inventory_nonnegative": (
            "dpr_workover_bulk_inventory",
            "(opening_quantity IS NULL OR opening_quantity>=0) AND (received_quantity IS NULL OR received_quantity>=0) "
            "AND (used_quantity IS NULL OR used_quantity>=0) AND (closing_quantity IS NULL OR closing_quantity>=0)",
        ),
    }
    for constraint, (table, expression) in checks.items():
        _add_check_constraint_if_missing(cursor, table, constraint, expression)

    _add_index_if_missing(cursor, "dpr_operation", "idx_fact_activity_work_category", "work_category_code,work_subcategory_code")
    _add_index_if_missing(cursor, "dpr_operation", "idx_fact_activity_time_type", "source_op_type,time_validation_status")
    _add_index_if_missing(cursor, "dpr_operation", "idx_fact_activity_timeline", "started_at,ended_at")

    cursor.execute(
        "UPDATE dq_issue SET status='RESOLVED',resolution_note='有效期关系自动复检',"
        "resolved_at=NOW(),resolved_by='system',updated_by='system',version=version+1 "
        "WHERE issue_type='RELATIONSHIP_OVERLAP' AND status='OPEN'"
    )
    overlap_specs = (
        ("rel_project_team_assignment", "team_id", "project_id", "project_team_assignment", ""),
        (
            "rel_job_rig_assignment",
            "rig_id",
            "job_id",
            "job_rig_assignment",
            "AND NOT EXISTS (SELECT 1 FROM biz_job job_a JOIN biz_job job_b ON job_b.id=b.job_id "
            "WHERE job_a.id=a.job_id AND job_a.project_id<=>job_b.project_id "
            "AND job_a.well_id=job_b.well_id)",
        ),
    )
    for table, entity_column, owner_column, entity_type, extra_predicate in overlap_specs:
        cursor.execute(
            f"""
            INSERT INTO dq_issue
              (issue_key,issue_type,severity,entity_type,entity_id,details_json,status,created_by,updated_by)
            SELECT CONCAT('RELATIONSHIP_OVERLAP:{table}:',a.id,':',b.id),'RELATIONSHIP_OVERLAP','error',
                   %s,CAST(a.{entity_column} AS CHAR),
                   JSON_OBJECT('table','{table}','first_id',a.id,'second_id',b.id,
                               'first_owner_id',a.{owner_column},'second_owner_id',b.{owner_column},
                               'valid_from',a.valid_from,'valid_to',a.valid_to,
                               'overlap_valid_from',b.valid_from,'overlap_valid_to',b.valid_to),
                   'OPEN','system','system'
            FROM {table} a JOIN {table} b
              ON a.id<b.id AND a.{entity_column}=b.{entity_column}
             AND a.status='active' AND b.status='active'
             AND a.valid_from<COALESCE(b.valid_to,'9999-12-31 23:59:59')
             AND b.valid_from<COALESCE(a.valid_to,'9999-12-31 23:59:59')
             {extra_predicate}
            ON DUPLICATE KEY UPDATE details_json=VALUES(details_json),status='OPEN',
              resolution_note='',resolved_at=NULL,resolved_by='',updated_by='system',
              dq_issue.version=dq_issue.version+1
            """,
            (entity_type,),
        )

    for table, constraint, column, target in (
        ("md_block", "fk_md_block_field", "field_id", "md_field"),
        ("md_block", "fk_md_block_region", "region_id", "md_geo_region"),
        ("md_block", "fk_md_block_operator", "operator_company_id", "md_organization"),
        ("md_well", "fk_md_well_field", "field_id", "md_field"),
        ("md_well", "fk_md_well_operator", "operator_company_id", "md_organization"),
    ):
        _add_foreign_key_if_missing(cursor, table, constraint, column, target, "id")


@contextmanager
def background_job_lock(kind: str, record_id: str):
    lock_key = hashlib.sha256(f"drp:{kind}:{record_id}".encode("utf-8")).hexdigest()[:60]
    connection = _connect()
    acquired = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT GET_LOCK(%s, 0) AS acquired", (lock_key,))
            acquired = bool((cursor.fetchone() or {}).get("acquired"))
        yield acquired
    finally:
        if acquired:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT RELEASE_LOCK(%s)", (lock_key,))
            except Exception:
                pass
        connection.close()


def _ensure_report_record_columns(cursor: Any) -> None:
    cursor.execute("SHOW COLUMNS FROM dpr_report_record")
    columns = {str(row.get("Field", "") or "") for row in cursor.fetchall()}
    migrations = (
        ("source_page_start", "INT UNSIGNED NULL AFTER parser"),
        ("source_page_end", "INT UNSIGNED NULL AFTER source_page_start"),
        ("source_report_index", "INT UNSIGNED NULL AFTER source_page_end"),
        ("source_report_count", "INT UNSIGNED NULL AFTER source_report_index"),
        ("batch_inherited_fields", "VARCHAR(255) NOT NULL DEFAULT '' AFTER source_report_count"),
        ("source_language", "VARCHAR(16) NOT NULL DEFAULT '' AFTER status"),
        ("translation_status", "VARCHAR(64) NOT NULL DEFAULT '' AFTER source_language"),
        ("translation_progress", "VARCHAR(16) NOT NULL DEFAULT '' AFTER translation_status"),
        ("translation_error", "TEXT NULL AFTER translation_progress"),
        ("translation_version", "VARCHAR(64) NOT NULL DEFAULT '' AFTER translation_error"),
        ("translation_updated_at", "VARCHAR(64) NOT NULL DEFAULT '' AFTER translation_version"),
        ("extraction_status", "VARCHAR(64) NOT NULL DEFAULT '' AFTER translation_updated_at"),
        ("extraction_progress", "VARCHAR(16) NOT NULL DEFAULT '' AFTER extraction_status"),
        ("extraction_error", "TEXT NULL AFTER extraction_progress"),
        ("extraction_version", "VARCHAR(64) NOT NULL DEFAULT '' AFTER extraction_error"),
        ("extraction_updated_at", "VARCHAR(64) NOT NULL DEFAULT '' AFTER extraction_version"),
        ("rig_id", "BIGINT UNSIGNED NULL AFTER rig"),
        ("well_id", "BIGINT UNSIGNED NULL AFTER rig_id"),
        ("project_id", "BIGINT UNSIGNED NULL AFTER well_id"),
        ("job_id", "BIGINT UNSIGNED NULL AFTER project_id"),
        ("master_match_status", "VARCHAR(32) NOT NULL DEFAULT '' AFTER job_id"),
        ("master_match_message", "TEXT NULL AFTER master_match_status"),
    )
    for column, definition in migrations:
        if column in columns:
            continue
        cursor.execute(f"ALTER TABLE dpr_report_record ADD COLUMN {column} {definition}")
        columns.add(column)


def _ensure_ai_extraction_storage_columns(cursor: Any) -> None:
    migrations = {
        "ai_extraction_target_field": (
            ("grain", "VARCHAR(32) NOT NULL DEFAULT 'report' AFTER output_format"),
            ("allowed_grains", "JSON NULL AFTER grain"),
            ("field_description", "VARCHAR(512) NOT NULL DEFAULT '' AFTER allowed_grains"),
        ),
        "ai_extraction_aggregate_result": (
            ("record_id", "VARCHAR(191) NULL AFTER grain"),
            ("project_id", "BIGINT UNSIGNED NULL AFTER record_id"),
            ("job_id", "BIGINT UNSIGNED NULL AFTER project_id"),
            ("job_sequence_no", "INT UNSIGNED NULL AFTER job_id"),
            ("well_id", "BIGINT UNSIGNED NULL AFTER job_sequence_no"),
            ("profession", "VARCHAR(32) NOT NULL DEFAULT '' AFTER team_id"),
            ("output_format", "VARCHAR(32) NOT NULL DEFAULT 'text' AFTER target_field"),
            ("result_number", "DECIMAL(24,6) NULL AFTER result_text"),
            ("result_date", "DATE NULL AFTER result_number"),
            ("result_json", "JSON NULL AFTER result_date"),
        ),
    }
    for table, definitions in migrations.items():
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = {str(row.get("Field", "") or "") for row in cursor.fetchall()}
        for column, definition in definitions:
            if column not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    cursor.execute("ALTER TABLE ai_extraction_aggregate_result MODIFY COLUMN team_id BIGINT UNSIGNED NULL")
    cursor.execute("ALTER TABLE ai_extraction_aggregate_result MODIFY COLUMN period_start DATE NULL")
    cursor.execute("ALTER TABLE ai_extraction_aggregate_result MODIFY COLUMN period_end DATE NULL")
    _add_index_if_missing(cursor, "ai_extraction_target_field", "idx_ai_extraction_target_grain", "grain,enabled,field_label")
    _add_index_if_missing(cursor, "ai_extraction_aggregate_result", "idx_ai_aggregate_well", "well_id,period_start")


def _ensure_project_relationship_columns(cursor: Any) -> None:
    migrations = {
        "rel_project_well_scope": (
            ("scope_note", "VARCHAR(512) NOT NULL DEFAULT '' AFTER job_type"),
        ),
    }
    for table, definitions in migrations.items():
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = {str(row.get("Field", "") or "") for row in cursor.fetchall()}
        for column, definition in definitions:
            if column not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _ensure_master_data_v3_columns(cursor: Any) -> None:
    migrations = {
        "md_organization": (
            ("legal_name", "VARCHAR(255) NOT NULL DEFAULT '' AFTER organization_type"),
            ("country_region_id", "BIGINT UNSIGNED NULL AFTER legal_name"),
        ),
        "md_block": (
            ("field_id", "BIGINT UNSIGNED NULL AFTER parent_id"),
            ("region_id", "BIGINT UNSIGNED NULL AFTER field_id"),
            ("operator_company_id", "BIGINT UNSIGNED NULL AFTER region_id"),
            ("block_type_code", "VARCHAR(64) NOT NULL DEFAULT 'OPERATING_AREA' AFTER operator_company_id"),
        ),
        "md_team": (
            ("model_code", "VARCHAR(64) NOT NULL DEFAULT '' AFTER company_id"),
        ),
        "md_project": (
            ("project_type", "VARCHAR(32) NOT NULL DEFAULT 'drilling' AFTER project_name"),
            ("npt_allowance_hours", "DECIMAL(8,2) NOT NULL DEFAULT 5.00 AFTER project_type"),
        ),
        "md_rig": (
            ("team_id", "BIGINT UNSIGNED NULL AFTER rig_type"),
            ("manufacturer", "VARCHAR(128) NOT NULL DEFAULT '' AFTER team_id"),
            ("model_code", "VARCHAR(64) NOT NULL DEFAULT '' AFTER manufacturer"),
            ("drive_type_code", "VARCHAR(64) NOT NULL DEFAULT '' AFTER model_code"),
            ("rated_power_hp", "DECIMAL(12,2) NULL AFTER drive_type_code"),
            ("rated_depth_m", "DECIMAL(12,2) NULL AFTER rated_power_hp"),
            ("equipment_status_code", "VARCHAR(64) NOT NULL DEFAULT 'AVAILABLE' AFTER rated_depth_m"),
        ),
        "md_well": (
            ("field_id", "BIGINT UNSIGNED NULL AFTER block_id"),
            ("operator_company_id", "BIGINT UNSIGNED NULL AFTER field_id"),
            ("well_type_code", "VARCHAR(64) NOT NULL DEFAULT 'DEVELOPMENT' AFTER operator_company_id"),
            ("surface_latitude", "DECIMAL(10,7) NULL AFTER well_type_code"),
            ("surface_longitude", "DECIMAL(10,7) NULL AFTER surface_latitude"),
            ("well_profile_code", "VARCHAR(64) NOT NULL DEFAULT '' AFTER surface_longitude"),
            ("trajectory_status_code", "VARCHAR(64) NOT NULL DEFAULT 'PLANNED' AFTER well_profile_code"),
            ("kickoff_md_m", "DECIMAL(12,2) NULL AFTER trajectory_status_code"),
            ("planned_td_md_m", "DECIMAL(12,2) NULL AFTER kickoff_md_m"),
            ("lifecycle_status_code", "VARCHAR(64) NOT NULL DEFAULT 'ACTIVE' AFTER planned_td_md_m"),
        ),
        "md_appendix_value": (
            ("display_color", "VARCHAR(16) NOT NULL DEFAULT '' AFTER sort_order"),
        ),
    }
    well_profile_default: object = None
    for table, definitions in migrations.items():
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        column_rows = cursor.fetchall()
        columns = {str(row.get("Field", "") or "") for row in column_rows}
        if table == "md_well":
            profile_row = next((row for row in column_rows if row.get("Field") == "well_profile_code"), None)
            well_profile_default = profile_row.get("Default") if profile_row else None
        for column, definition in definitions:
            if column not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    if well_profile_default != "":
        cursor.execute("ALTER TABLE md_well MODIFY COLUMN well_profile_code VARCHAR(64) NOT NULL DEFAULT ''")
    cursor.execute(
        "UPDATE md_well SET well_profile_code='',"
        "change_reason=CONCAT_WS('；',NULLIF(change_reason,''),'井型无明确来源，清除历史默认直井'),"
        "updated_by='well-profile-source-audit',version=version+1 "
        "WHERE well_profile_code='VERTICAL' AND created_by=updated_by "
        "AND created_by IN ('migration','report-relation-audit-2026-07-18') "
        "AND change_reason NOT LIKE '%井型明确字段%'"
    )


def _migrate_remove_wellbore_master(cursor: Any) -> None:
    """Collapse the legacy one-to-one wellbore master into md_well and remove it."""
    cursor.execute(
        "UPDATE dq_issue SET status='RESOLVED',resolution_note='井筒实体已合并为井，旧复核项失效',"
        "resolved_at=NOW(),resolved_by='migration',updated_by='migration',version=version+1 "
        "WHERE issue_type='ALIAS_REVIEW' AND entity_type='wellbore' AND status='OPEN'"
    )
    if not _table_exists(cursor, "md_wellbore"):
        return
    for view in ("vw_workover_basic_metrics", "vw_job_efficiency", "vw_drilling_basic_metrics", "vw_monthly_rig_workload", "vw_rig_production_timeline"):
        cursor.execute(f"DROP VIEW IF EXISTS {view}")

    cursor.execute(
        "UPDATE md_well well JOIN md_wellbore wellbore ON wellbore.well_id=well.id SET "
        "well.well_profile_code=COALESCE(NULLIF(wellbore.wellbore_profile_code,''),well.well_profile_code),"
        "well.trajectory_status_code=COALESCE(NULLIF(wellbore.trajectory_status_code,''),well.trajectory_status_code),"
        "well.kickoff_md_m=COALESCE(well.kickoff_md_m,wellbore.kickoff_md_m),"
        "well.planned_td_md_m=COALESCE(well.planned_td_md_m,wellbore.planned_td_md_m),"
        "well.updated_by='wellbore-removal-migration',well.version=well.version+1"
    )
    migrations = {
        "dpr_report_record": "BIGINT UNSIGNED NULL AFTER rig_id",
        "rel_project_well_scope": "BIGINT UNSIGNED NULL AFTER project_id",
        "biz_job": "BIGINT UNSIGNED NULL AFTER project_id",
        "dpr_report": "BIGINT UNSIGNED NULL AFTER rig_id",
    }
    for table, definition in migrations.items():
        if not _column_exists(cursor, table, "well_id"):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN well_id {definition}")
        if _column_exists(cursor, table, "wellbore_id"):
            cursor.execute(
                f"UPDATE {table} target JOIN md_wellbore source ON source.id=target.wellbore_id "
                "SET target.well_id=source.well_id WHERE target.wellbore_id IS NOT NULL"
            )

    cursor.execute(
        "UPDATE md_alias alias_row JOIN md_wellbore source ON source.id=alias_row.entity_id "
        "SET alias_row.entity_type='well',alias_row.entity_id=source.well_id,"
        "alias_row.change_reason='井筒主数据移除，别名迁移至井',alias_row.updated_by='migration',"
        "alias_row.version=alias_row.version+1 WHERE alias_row.entity_type='wellbore'"
    )
    cursor.execute(
        "UPDATE dq_issue SET issue_type='MASTER_WELL_UNRESOLVED',"
        "details_json=JSON_SET(COALESCE(details_json,JSON_OBJECT()),'$.message','井未匹配主数据'),"
        "updated_by='migration',version=version+1 WHERE issue_type='MASTER_WELLBORE_UNRESOLVED'"
    )
    cursor.execute(
        "UPDATE md_appendix_category SET category_code='WELL_PROFILE',category_name='井轨迹类型',"
        "description='井轨迹轮廓',change_reason='井筒主数据移除后迁移至井',updated_by='migration',version=version+1 "
        "WHERE category_code='WELLBORE_PROFILE'"
    )

    legacy_indexes = {
        "dpr_report_record": ("idx_report_records_type_wellbore_date", "idx_report_records_master_refs"),
        "rel_project_well_scope": ("uq_project_well_scope_start", "idx_project_well_scope_lookup"),
        "biz_job": ("uq_biz_job_sequence", "idx_biz_job_wellbore"),
        "dpr_report": ("idx_fact_daily_report_refs",),
    }
    _add_index_if_missing(cursor, "rel_project_well_scope", "idx_project_well_scope_project", "project_id")
    _add_index_if_missing(cursor, "biz_job", "idx_biz_job_project", "project_id")
    _add_index_if_missing(cursor, "dpr_report", "idx_fact_daily_report_project", "project_id")
    _add_index_if_missing(cursor, "dpr_report", "idx_fact_daily_report_job", "job_id")
    _add_index_if_missing(cursor, "dpr_report", "idx_fact_daily_report_rig", "rig_id")
    for table in migrations:
        if not _column_exists(cursor, table, "wellbore_id"):
            continue
        _drop_foreign_keys_for_column(cursor, table, "wellbore_id")
        for index in legacy_indexes.get(table, ()):
            _drop_index_if_exists(cursor, table, index)
        cursor.execute(f"ALTER TABLE {table} DROP COLUMN wellbore_id")

    cursor.execute("ALTER TABLE rel_project_well_scope MODIFY COLUMN well_id BIGINT UNSIGNED NOT NULL")
    cursor.execute("ALTER TABLE biz_job MODIFY COLUMN well_id BIGINT UNSIGNED NOT NULL")
    _add_index_if_missing(cursor, "dpr_report_record", "idx_report_records_type_well_date", "report_type, well_id, report_date")
    _add_index_if_missing(cursor, "dpr_report_record", "idx_report_records_master_refs", "project_id, rig_id, well_id, job_id")
    _add_index_if_missing(cursor, "rel_project_well_scope", "uq_project_well_scope_start", "project_id, well_id, job_type, valid_from", unique=True)
    _add_index_if_missing(cursor, "rel_project_well_scope", "idx_project_well_scope_lookup", "well_id, job_type, valid_from, valid_to, status")
    _add_index_if_missing(cursor, "biz_job", "uq_biz_job_sequence", "project_id, well_id, job_type, sequence_no", unique=True)
    _add_index_if_missing(cursor, "biz_job", "idx_biz_job_well", "well_id, job_type, status")
    _add_index_if_missing(cursor, "dpr_report", "idx_fact_daily_report_refs", "project_id, job_id, rig_id, well_id")
    _add_foreign_key_if_missing(cursor, "rel_project_well_scope", "fk_project_well_scope_well", "well_id", "md_well", "id")
    _add_foreign_key_if_missing(cursor, "biz_job", "fk_biz_job_well", "well_id", "md_well", "id")
    _add_foreign_key_if_missing(cursor, "dpr_report", "fk_fact_daily_report_well", "well_id", "md_well", "id")
    cursor.execute("DROP TABLE md_wellbore")


def _table_exists(cursor: Any, table: str) -> bool:
    cursor.execute(
        "SELECT COUNT(*) AS count_value FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s",
        (table,),
    )
    return int((cursor.fetchone() or {}).get("count_value", 0) or 0) > 0


def _column_exists(cursor: Any, table: str, column: str) -> bool:
    cursor.execute(
        "SELECT COUNT(*) AS count_value FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s",
        (table, column),
    )
    return int((cursor.fetchone() or {}).get("count_value", 0) or 0) > 0


def _drop_foreign_keys_for_column(cursor: Any, table: str, column: str) -> None:
    cursor.execute(
        "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s AND REFERENCED_TABLE_NAME IS NOT NULL",
        (table, column),
    )
    for row in cursor.fetchall() or []:
        cursor.execute(f"ALTER TABLE {table} DROP FOREIGN KEY {row['CONSTRAINT_NAME']}")


def _drop_index_if_exists(cursor: Any, table: str, index: str) -> None:
    cursor.execute(
        "SELECT COUNT(*) AS count_value FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND INDEX_NAME=%s",
        (table, index),
    )
    if int((cursor.fetchone() or {}).get("count_value", 0) or 0):
        cursor.execute(f"ALTER TABLE {table} DROP INDEX {index}")


def _add_index_if_missing(cursor: Any, table: str, index: str, columns: str, *, unique: bool = False) -> None:
    cursor.execute(
        "SELECT COUNT(*) AS count_value FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND INDEX_NAME=%s",
        (table, index),
    )
    if not int((cursor.fetchone() or {}).get("count_value", 0) or 0):
        cursor.execute(f"ALTER TABLE {table} ADD {'UNIQUE ' if unique else ''}INDEX {index} ({columns})")


def _add_foreign_key_if_missing(
    cursor: Any, table: str, constraint: str, column: str, referenced_table: str, referenced_column: str
) -> None:
    cursor.execute(
        "SELECT COUNT(*) AS count_value FROM information_schema.TABLE_CONSTRAINTS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND CONSTRAINT_NAME=%s",
        (table, constraint),
    )
    if not int((cursor.fetchone() or {}).get("count_value", 0) or 0):
        cursor.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT {constraint} FOREIGN KEY ({column}) "
            f"REFERENCES {referenced_table}({referenced_column})"
        )


def _add_check_constraint_if_missing(cursor: Any, table: str, constraint: str, expression: str) -> None:
    cursor.execute(
        "SELECT COUNT(*) AS count_value FROM information_schema.TABLE_CONSTRAINTS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND CONSTRAINT_NAME=%s AND CONSTRAINT_TYPE='CHECK'",
        (table, constraint),
    )
    if not int((cursor.fetchone() or {}).get("count_value", 0) or 0):
        cursor.execute(f"ALTER TABLE {table} ADD CONSTRAINT {constraint} CHECK ({expression})")


def _migrate_master_data_v3(cursor: Any) -> None:
    categories = (
        ("REGION_TYPE", "国家/区域类型", "OSDU geographic context 精简枚举"),
        ("COMPANY_TYPE", "公司类型", "OSDU organisation 精简枚举"),
        ("FIELD_TYPE", "油田类型", "陆上/海上油田"),
        ("FIELD_STATUS", "油田生命周期", "油田生命周期状态"),
        ("BLOCK_TYPE", "区块类型", "许可区块或作业区"),
        ("TEAM_TYPE", "队伍类型", "钻井、修井或综合服务队"),
        ("EQUIPMENT_STATUS", "设备状态", "钻机/修井机运行状态"),
        ("RIG_DRIVE_TYPE", "设备驱动方式", "机械、电驱或液压"),
        ("RIG_TYPE", "钻机型号", "钻机和修井机规格型号"),
        ("WELL_TYPE", "井用途", "井的业务用途"),
        ("WELL_STATUS", "井生命周期", "井生命周期状态"),
        ("WELL_PROFILE", "井轨迹类型", "井轨迹轮廓"),
        ("TRAJECTORY_STATUS", "轨迹状态", "井轨迹计划与执行状态"),
        ("TIME_TYPE", "时效类型", "日报作业时效分类及显示颜色"),
        ("WORK_BUCKET", "工作量归类", "时效确认后的作业、搬迁、待工及维修归类"),
        ("RESPONSIBILITY", "责任方", "SC/NPT时段责任归属"),
        ("BILLING_STATUS", "计费状态", "时效时段计费状态"),
        ("CAUSE_CODE", "原因编码", "SC/NPT原因分类"),
    )
    cursor.executemany(
        "INSERT INTO md_appendix_category (category_code,category_name,description,status,change_reason,created_by,updated_by) "
        "VALUES (%s,%s,%s,'active','OSDU精简附录初始化','system','system') "
        "ON DUPLICATE KEY UPDATE category_code=VALUES(category_code)",
        categories,
    )
    values = {
        "REGION_TYPE": (("COUNTRY", "国家"), ("ADMIN_REGION", "行政区域"), ("BUSINESS_REGION", "业务区域")),
        "COMPANY_TYPE": (("OPERATOR", "作业者"), ("SERVICE_COMPANY", "油服公司"), ("CONTRACTOR", "承包商"), ("INTERNAL_UNIT", "内部单位")),
        "FIELD_TYPE": (("ONSHORE", "陆上"), ("OFFSHORE", "海上")),
        "FIELD_STATUS": (("PLANNED", "规划"), ("ACTIVE", "在产"), ("SUSPENDED", "暂停"), ("ABANDONED", "废弃")),
        "BLOCK_TYPE": (("CONCESSION", "特许区"), ("LICENSE_BLOCK", "许可区块"), ("OPERATING_AREA", "作业区")),
        "TEAM_TYPE": (("DRILLING", "钻井队"), ("WORKOVER", "修井队"), ("INTEGRATED", "综合服务队")),
        "EQUIPMENT_STATUS": (("AVAILABLE", "可用"), ("OPERATING", "作业中"), ("MAINTENANCE", "维修"), ("SUSPENDED", "停用"), ("RETIRED", "退役")),
        "RIG_DRIVE_TYPE": (("MECHANICAL", "机械驱动"), ("ELECTRIC", "电驱动"), ("HYDRAULIC", "液压驱动")),
        "RIG_TYPE": (("ZJ70D", "ZJ70D钻机"), ("ZJ30", "ZJ30钻机"), ("XJ650", "XJ650修井机"), ("650HP", "650HP修井机")),
        "WELL_TYPE": (("EXPLORATION", "探井"), ("APPRAISAL", "评价井"), ("DEVELOPMENT", "开发井"), ("INJECTION", "注入井"), ("OBSERVATION", "观察井")),
        "WELL_STATUS": (("PLANNED", "计划"), ("DRILLING", "钻进中"), ("COMPLETED", "已完井"), ("SUSPENDED", "暂停"), ("ABANDONED", "废弃"), ("ACTIVE", "有效")),
        "WELL_PROFILE": (("VERTICAL", "直井"), ("DIRECTIONAL", "定向井"), ("HORIZONTAL", "水平井"), ("SIDETRACK", "侧钻井")),
        "TRAJECTORY_STATUS": (("PLANNED", "计划"), ("ACTUAL", "实钻"), ("REVISED", "修订")),
        "WORK_BUCKET": (("OPERATION", "作业"), ("MOVE", "搬迁"), ("STANDBY_STAFFED", "有人待工"), ("STANDBY_UNSTAFFED", "无人待工"), ("FORCE_MAJEURE", "不可抗力"), ("MAINTENANCE", "维修")),
        "RESPONSIBILITY": (("OURS", "我方"), ("CLIENT", "甲方"), ("THIRD_PARTY", "第三方"), ("FORCE_MAJEURE", "不可抗力")),
        "BILLING_STATUS": (("FULL_RATE", "全日费"), ("PARTIAL_RATE", "部分日费"), ("ZERO_RATE", "零日费")),
        "CAUSE_CODE": (("EQUIPMENT", "设备"), ("TOOL", "工具"), ("PERSONNEL", "人员"), ("MATERIAL", "物资"), ("COMMUNITY", "社区"), ("WEATHER", "天气"), ("INCIDENT", "事故"), ("OTHER", "其他")),
    }
    for category_code, rows in values.items():
        cursor.execute("SELECT id FROM md_appendix_category WHERE category_code=%s", (category_code,))
        category_id = int(cursor.fetchone()["id"])
        cursor.executemany(
            "INSERT INTO md_appendix_value (category_id,value_code,value_name,status,change_reason,created_by,updated_by) "
            "VALUES (%s,%s,%s,'active','OSDU精简附录初始化','system','system') "
            "ON DUPLICATE KEY UPDATE value_code=VALUES(value_code)",
            [(category_id, code, name) for code, name in rows],
        )
    cursor.execute("SELECT id FROM md_appendix_category WHERE category_code='TIME_TYPE'")
    time_type_category_id = int(cursor.fetchone()["id"])
    cursor.executemany(
        "INSERT INTO md_appendix_value "
        "(category_id,value_code,value_name,sort_order,display_color,status,change_reason,created_by,updated_by) "
        "VALUES (%s,%s,%s,%s,%s,'active','时效类型附录初始化','system','system') "
        "ON DUPLICATE KEY UPDATE "
        "value_name=VALUES(value_name),sort_order=VALUES(sort_order),"
        "display_color=IF(display_color='',VALUES(display_color),display_color)",
        [
            (time_type_category_id, "P", "P", 10, "#16875B"),
            (time_type_category_id, "SC", "SC", 20, "#B7791F"),
            (time_type_category_id, "NPT", "NPT", 30, "#D43F3A"),
        ],
    )
    cursor.execute(
        "INSERT INTO md_geo_region (region_code,region_name,region_type_code,iso_alpha2,status,change_reason,created_by,updated_by) "
        "VALUES ('EC','厄瓜多尔','COUNTRY','EC','active','现有数据迁移','migration','migration') "
        "ON DUPLICATE KEY UPDATE region_name=VALUES(region_name),iso_alpha2=VALUES(iso_alpha2)"
    )
    cursor.execute("SELECT id FROM md_geo_region WHERE region_code='EC'")
    ecuador_id = int(cursor.fetchone()["id"])
    cursor.execute(
        "UPDATE md_organization SET legal_name=IF(legal_name='',organization_name,legal_name), "
        "organization_type=IF(organization_type IN ('','regional_company'),'INTERNAL_UNIT',UPPER(organization_type)), "
        "country_region_id=COALESCE(country_region_id,%s)",
        (ecuador_id,),
    )
    cursor.execute(
        "INSERT INTO md_field (field_code,field_name,region_id,field_type_code,lifecycle_status_code,status,change_reason,created_by,updated_by) "
        "SELECT block_code,block_name,%s,'ONSHORE','ACTIVE',status,'现有区块候选迁移','migration','migration' FROM md_block "
        "ON DUPLICATE KEY UPDATE field_name=VALUES(field_name),region_id=VALUES(region_id)",
        (ecuador_id,),
    )
    cursor.execute(
        "UPDATE md_block block JOIN md_field field ON field.field_code=block.block_code "
        "SET block.field_id=field.id,block.region_id=COALESCE(block.region_id,%s)",
        (ecuador_id,),
    )
    cursor.execute(
        "INSERT INTO md_team (team_code,team_name,team_type_code,company_id,status,change_reason,created_by,updated_by) "
        "SELECT rig_code,rig_name,IF(rig_type='workover','WORKOVER','DRILLING'),owner_organization_id,status,'现有井队迁移','migration','migration' FROM md_rig "
        "ON DUPLICATE KEY UPDATE team_name=VALUES(team_name),team_type_code=VALUES(team_type_code),company_id=VALUES(company_id)"
    )
    cursor.execute(
        "UPDATE md_rig rig JOIN md_team team ON team.team_code=rig.rig_code "
        "LEFT JOIN md_rig_model model ON model.id=rig.rig_model_id "
        "SET rig.team_id=team.id,rig.manufacturer=IF(rig.manufacturer='','SINOPEC',rig.manufacturer),"
        "rig.model_code=IF(rig.model_code='',COALESCE(model.model_code,''),rig.model_code),"
        "rig.equipment_status_code=IF(rig.equipment_status_code='','AVAILABLE',rig.equipment_status_code)"
    )
    cursor.execute(
        "UPDATE md_team team JOIN md_rig rig ON rig.team_id=team.id "
        "SET team.model_code=IF(team.model_code='',rig.model_code,team.model_code)"
    )
    if _table_exists(cursor, "rel_project_rig_assignment"):
        cursor.execute(
            "INSERT INTO rel_project_team_assignment (project_id,team_id,valid_from,valid_to,service_discipline,assignment_note,priority,status,change_reason,created_by,updated_by) "
            "SELECT relation.project_id,rig.team_id,relation.valid_from,relation.valid_to,relation.service_discipline,relation.assignment_note,relation.priority,relation.status,'由井队关系迁移','migration','migration' "
            "FROM rel_project_rig_assignment relation JOIN md_rig rig ON rig.id=relation.rig_id WHERE rig.team_id IS NOT NULL "
            "ON DUPLICATE KEY UPDATE valid_to=VALUES(valid_to),status=VALUES(status),assignment_note=VALUES(assignment_note)"
        )
    cursor.execute(
        "UPDATE md_well well JOIN md_block block ON UPPER(block.block_code)='SACHA' "
        "SET well.block_id=block.id WHERE well.block_id IS NULL AND UPPER(well.well_code) LIKE 'SCHA%'"
    )
    cursor.execute(
        "UPDATE md_well well LEFT JOIN md_block block ON block.id=well.block_id "
        "SET well.field_id=block.field_id,well.operator_company_id=COALESCE(well.operator_company_id,block.operator_company_id)"
    )
    cursor.execute(
        "DELETE field FROM md_field field "
        "LEFT JOIN md_block block ON block.field_id=field.id LEFT JOIN md_well well ON well.field_id=field.id "
        "WHERE field.field_code='EG01' AND block.id IS NULL AND well.id IS NULL"
    )
def _retire_legacy_database_objects(cursor: Any) -> None:
    """Remove superseded compatibility/statistics tables after safe migration."""

    if _table_exists(cursor, "rel_project_rig_assignment"):
        cursor.execute(
            """
            SELECT COUNT(*) AS count_value
            FROM rel_project_rig_assignment legacy
            JOIN md_rig rig ON rig.id=legacy.rig_id
            LEFT JOIN rel_project_team_assignment formal
              ON formal.project_id=legacy.project_id
             AND formal.team_id=rig.team_id
             AND formal.valid_from=legacy.valid_from
             AND (formal.valid_to=legacy.valid_to OR (formal.valid_to IS NULL AND legacy.valid_to IS NULL))
             AND formal.status=legacy.status
            WHERE formal.id IS NULL
            """
        )
        unmigrated = int((cursor.fetchone() or {}).get("count_value", 0) or 0)
        if unmigrated:
            raise RuntimeError(
                f"Cannot retire rel_project_rig_assignment: {unmigrated} rows have no formal team relation."
            )
        cursor.execute("DROP TABLE rel_project_rig_assignment")

    # The monthly freeze/reopen feature was removed. Reporting now reads
    # canonical facts through views; stale draft snapshots must not become a
    # second statistics source.
    cursor.execute("DROP TABLE IF EXISTS monthly_report_snapshot_row")
    cursor.execute("DROP TABLE IF EXISTS monthly_report_snapshot")


def _ensure_report_record_indexes(cursor: Any) -> None:
    cursor.execute("SHOW INDEX FROM dpr_report_record")
    indexes = {str(row.get("Key_name", "") or "") for row in cursor.fetchall()}
    if "idx_report_records_master_refs" not in indexes:
        cursor.execute(
            "CREATE INDEX idx_report_records_master_refs "
            "ON dpr_report_record (project_id, rig_id, well_id, job_id)"
        )
    if "idx_report_records_match_status" not in indexes:
        cursor.execute(
            "CREATE INDEX idx_report_records_match_status "
            "ON dpr_report_record (master_match_status)"
        )
    if "idx_report_records_type_well_date" not in indexes:
        cursor.execute(
            "CREATE INDEX idx_report_records_type_well_date "
            "ON dpr_report_record (report_type, well_id, report_date)"
        )
    if "uq_report_records_business_identity" not in indexes:
        cursor.execute(
            "CREATE UNIQUE INDEX uq_report_records_business_identity "
            "ON dpr_report_record (report_type, report_date, report_no, wellbore)"
        )


def _ensure_translation_content_indexes(cursor: Any) -> None:
    cursor.execute("SHOW INDEX FROM translation_content")
    indexes = {str(row.get("Key_name", "") or "") for row in cursor.fetchall()}
    if "idx_translation_memory_lookup" not in indexes:
        cursor.execute(
            "CREATE INDEX idx_translation_memory_lookup "
            "ON translation_content (target_language, prompt_version, translation_status, source_hash)"
        )


def _ensure_database_comments(cursor: Any) -> None:
    """Keep the legacy audit layer clearly documented without breaking its public names."""
    table_comments = {
        "dpr_report_record": "日报原始审计主表；保存来源、业务标识、处理状态及主数据引用",
        "dpr_report_field": "日报单值字段原始审计表；fields_json永久保留解析结果",
        "dpr_report_row": "日报重复明细原始审计表；按module_name和row_no保存来源行",
        "dpr_report": "标准日报事实主表；一份成功保存的日报对应一条记录",
        "dpr_operation": "日报作业时段标准事实",
        "dpr_operation_classification": "作业时段时效确认与责任分类标准事实",
        "biz_job_event": "作业实例关键事件标准事实",
        "biz_job_depth_progress": "作业实例井深与进尺标准事实",
        "hsse_incident": "日报事故与复杂情况标准事实",
        "dq_issue": "数据质量问题及处理状态",
        "production_report_remark": "生产报表人工备注；不保存统计结果",
    }
    for table, comment in table_comments.items():
        cursor.execute(
            "SELECT TABLE_COMMENT FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s",
            (table,),
        )
        current = str((cursor.fetchone() or {}).get("TABLE_COMMENT", "") or "")
        if current != comment:
            cursor.execute(f"ALTER TABLE {table} COMMENT='{comment}'")

    cursor.execute(
        "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() "
        "AND TABLE_TYPE='BASE TABLE' AND COALESCE(TABLE_COMMENT,'')=''"
    )
    for row in cursor.fetchall():
        table = str(row.get("TABLE_NAME", "") or "")
        comment = _generic_table_comment(table).replace("'", "''")
        cursor.execute(f"ALTER TABLE `{table}` COMMENT='{comment}'")

    column_comments = {
        ("dpr_report_record", "record_id"): ("VARCHAR(191) NOT NULL", "稳定日报业务ID"),
        ("dpr_report_record", "report_type"): ("VARCHAR(32) NOT NULL", "日报类型：drilling/completion/workover；搬迁由drilling的Event区分"),
        ("dpr_report_field", "fields_json"): ("JSON NOT NULL", "日报全部单值字段原始解析JSON"),
        ("dpr_report_row", "module_name"): ("VARCHAR(64) NOT NULL", "明细模块标准代码"),
        ("dpr_report_row", "row_no"): ("INT NOT NULL", "来源模块内行号，从1开始"),
        ("dpr_report_row", "row_json"): ("JSON NOT NULL", "日报明细行原始解析JSON"),
        ("dpr_report", "record_id"): ("VARCHAR(191) NOT NULL", "关联原始日报稳定业务ID"),
        ("dpr_report", "report_type"): ("VARCHAR(32) NOT NULL", "日报类型标准代码"),
    }
    for (table, column), (definition, comment) in column_comments.items():
        cursor.execute(f"SHOW FULL COLUMNS FROM {table} LIKE %s", (column,))
        current = str((cursor.fetchone() or {}).get("Comment", "") or "")
        if current != comment:
            cursor.execute(f"ALTER TABLE {table} MODIFY COLUMN {column} {definition} COMMENT '{comment}'")

    cursor.execute(
        "SELECT c.TABLE_NAME,c.COLUMN_NAME,c.COLUMN_TYPE,c.IS_NULLABLE,c.COLUMN_DEFAULT,c.EXTRA,c.DATA_TYPE "
        "FROM information_schema.COLUMNS c JOIN information_schema.TABLES t "
        "ON t.TABLE_SCHEMA=c.TABLE_SCHEMA AND t.TABLE_NAME=c.TABLE_NAME "
        "WHERE c.TABLE_SCHEMA=DATABASE() AND t.TABLE_TYPE='BASE TABLE' AND COALESCE(c.COLUMN_COMMENT,'')='' "
        "ORDER BY c.TABLE_NAME,c.ORDINAL_POSITION"
    )
    for row in cursor.fetchall():
        table = str(row.get("TABLE_NAME", "") or "")
        column = str(row.get("COLUMN_NAME", "") or "")
        definition = _column_definition_for_comment(row)
        comment = _generic_column_comment(column).replace("'", "''")
        cursor.execute(
            f"ALTER TABLE `{table}` MODIFY COLUMN `{column}` {definition} COMMENT '{comment}'"
        )


def _generic_table_comment(table: str) -> str:
    if table.startswith("md_"):
        return f"主数据表：{table}"
    if table.startswith("rel_"):
        return f"有效期关系表：{table}"
    if table.startswith("biz_"):
        return f"业务实例表：{table}"
    if table.startswith("fact_"):
        return f"标准事实表：{table}"
    if table.startswith("report_"):
        return f"原始日报审计表：{table}"
    if table.startswith("translation_"):
        return f"翻译业务表：{table}"
    return f"系统业务表：{table}"


def _generic_column_comment(column: str) -> str:
    exact = {
        "id": "稳定数值主键",
        "record_id": "稳定日报业务ID",
        "daily_report_id": "标准日报事实ID",
        "source_row_no": "来源明细行号，从1开始",
        "source_hash": "来源内容SHA-256哈希",
        "created_at": "创建时间",
        "created_by": "创建人",
        "updated_at": "更新时间",
        "updated_by": "更新人",
        "version": "乐观锁版本号",
        "change_reason": "本次变更原因",
        "status": "业务状态",
    }
    if column in exact:
        return exact[column]
    units = {
        "_ft_lbf": "，单位ft-lbf",
        "_deg_per_100ft": "，单位deg/100ft",
        "_lb_per_100ft2": "，单位lb/100ft²",
        "_sec_per_qt": "，单位sec/qt",
        "_bbl": "，单位bbl",
        "_psi": "，单位psi",
        "_ppg": "，单位ppg",
        "_gpm": "，单位gpm",
        "_kip": "，单位kip",
        "_usd": "，单位USD",
        "_pct": "，单位%",
        "_deg": "，单位deg",
        "_ft": "，单位ft",
        "_in": "，单位in",
        "_m": "，单位m",
    }
    suffix = next((label for key, label in units.items() if column.endswith(key)), "")
    if column.endswith("_id"):
        return f"关联实体稳定ID：{column}"
    if column.endswith("_code"):
        return f"标准编码：{column}"
    if column.endswith("_name"):
        return f"业务名称：{column}"
    if column.endswith("_status"):
        return f"业务状态：{column}"
    if column.endswith("_flag"):
        return f"业务标志：{column}"
    if column.endswith("_date"):
        return f"业务日期：{column}"
    if column.endswith("_at"):
        return f"业务日期时间：{column}"
    if column.endswith("_json"):
        return f"结构化JSON数据：{column}"
    return f"业务字段：{column}{suffix}"


def _column_definition_for_comment(row: dict[str, Any]) -> str:
    column_type = str(row.get("COLUMN_TYPE", "") or "")
    data_type = str(row.get("DATA_TYPE", "") or "").lower()
    definition = f"{column_type} {'NULL' if row.get('IS_NULLABLE') == 'YES' else 'NOT NULL'}"
    default = row.get("COLUMN_DEFAULT")
    if default is not None:
        default_text = str(default)
        if default_text.upper().startswith("CURRENT_TIMESTAMP"):
            definition += f" DEFAULT {default_text}"
        elif data_type in {"bigint", "int", "decimal", "tinyint", "smallint", "mediumint", "float", "double"}:
            definition += f" DEFAULT {default_text}"
        else:
            definition += f" DEFAULT '{default_text.replace(chr(39), chr(39) * 2)}'"
    extra = str(row.get("EXTRA", "") or "").replace("DEFAULT_GENERATED", "").strip()
    if extra:
        definition += f" {extra}"
    return definition


def save_report_payload(
    database_path: str | Path | None,
    payload: dict[str, Any],
    report_type: str,
    *,
    source_file: str = "",
    invalidate_translations: bool = True,
) -> dict[str, Any]:
    del database_path
    report_type = _normalize_report_type(report_type)
    initialize_database()
    fields = payload.get("report_fields", {}) or {}
    metadata = payload.get("metadata", {}) or {}
    requested_record_id = str(metadata.get("record_id") or payload.get("record_id") or "").strip()
    natural_record_id = _natural_record_id(report_type, fields)
    record_id = requested_record_id or natural_record_id or _generated_record_id(report_type)
    source_file = source_file or str(metadata.get("source_file") or "")
    now = _now()
    normalization: dict[str, Any] = {}

    with _connect() as connection:
        with connection.cursor() as cursor:
            identity_record_id = _record_id_for_business_identity(cursor, report_type, fields)
            if identity_record_id and identity_record_id != record_id:
                if requested_record_id:
                    cursor.execute(
                        "SELECT 1 FROM dpr_report_record WHERE record_id=%s",
                        (requested_record_id,),
                    )
                    if cursor.fetchone():
                        raise ValueError(
                            "日报业务身份已被另一条记录占用："
                            f"{report_type}/{fields.get('reportDate', '')}/{fields.get('wellbore', '')}/"
                            f"{fields.get('reportNo', '')}。请先处理重复日报。"
                        )
                record_id = identity_record_id
            cursor.execute(
                "SELECT locked, created_at, report_type, well_id, wellbore FROM dpr_report_record WHERE record_id=%s FOR UPDATE",
                (record_id,),
            )
            existing = cursor.fetchone() or {}
            if _truthy(existing.get("locked")):
                raise PermissionError(f"Record is locked after NPT confirmation: {record_id}")
            created_at = str(existing.get("created_at") or metadata.get("created_at") or now)
            updated_at = str(metadata.get("updated_at") or now)
            record = _record_from_payload(record_id, report_type, source_file, fields, metadata, created_at, updated_at)
            _upsert_record(cursor, record)
            cursor.execute(
                """
                INSERT INTO dpr_report_field (record_id, fields_json)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE fields_json=VALUES(fields_json)
                """,
                (record_id, _json_dumps(fields)),
            )
            cursor.execute("DELETE FROM dpr_report_row WHERE record_id=%s", (record_id,))
            for module_name in REPORT_TABLES[report_type]["multi"]:
                for row_no, row in enumerate(payload.get(module_name, []) or [], start=1):
                    if not isinstance(row, dict):
                        continue
                    cursor.execute(
                        """
                        INSERT INTO dpr_report_row (record_id, module_name, row_no, row_json)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (record_id, module_name, row_no, _json_dumps(row)),
                    )
            actor = str(metadata.get("updated_by", "") or metadata.get("confirmed_by", "") or "system")
            cursor.execute("SAVEPOINT normalize_report")
            try:
                from .report_normalization_service import refresh_boundary_hour_issues, synchronize_saved_report

                normalization = synchronize_saved_report(
                    cursor,
                    record_id=record_id,
                    report_type=report_type,
                    fields=fields,
                    operations=[
                        row for row in (payload.get("operations", []) or [])
                        if isinstance(row, dict)
                    ],
                    payload=payload,
                    actor=actor,
                )
                old_group = (
                    str(existing.get("report_type", "") or "").strip().lower(),
                    _positive_int(existing.get("well_id")),
                    str(existing.get("wellbore", "") or "").strip(),
                )
                new_group = (
                    report_type,
                    _positive_int(normalization.get("well_id")),
                    str(fields.get("wellbore", "") or "").strip(),
                )
                if existing and old_group != new_group:
                    refresh_boundary_hour_issues(
                        cursor,
                        report_type=old_group[0],
                        well_id=old_group[1],
                        wellbore=old_group[2],
                        actor=actor,
                    )
                cursor.execute("RELEASE SAVEPOINT normalize_report")
            except Exception as exc:
                cursor.execute("ROLLBACK TO SAVEPOINT normalize_report")
                cursor.execute("RELEASE SAVEPOINT normalize_report")
                normalization = {
                    "record_id": record_id,
                    "normalization_status": "NORMALIZATION_FAILED",
                    "error": str(exc),
                }
                cursor.execute(
                    """
                    UPDATE dpr_report_record
                    SET master_match_status='NORMALIZATION_FAILED', master_match_message=%s
                    WHERE record_id=%s
                    """,
                    (str(exc)[:2000], record_id),
                )
                cursor.execute(
                    "UPDATE dpr_report SET normalization_status='NORMALIZATION_FAILED',match_message=%s,"
                    "updated_by=%s,version=version+1 WHERE record_id=%s",
                    (str(exc)[:2000], actor, record_id),
                )
                cursor.execute(
                    """
                    INSERT INTO dq_issue
                      (issue_key,issue_type,severity,entity_type,entity_id,record_id,
                       details_json,status,created_by,updated_by)
                    VALUES (%s,'NORMALIZATION_FAILED','error','report',%s,%s,%s,'OPEN',%s,%s)
                    ON DUPLICATE KEY UPDATE details_json=VALUES(details_json),status='OPEN',
                      resolution_note='',resolved_at=NULL,resolved_by='',updated_by=VALUES(updated_by),
                      version=version+1
                    """,
                    (
                        f"{record_id}:NORMALIZATION_FAILED",
                        record_id,
                        record_id,
                        _json_dumps({"message": str(exc)[:2000], "report_type": report_type}),
                        actor,
                        actor,
                    ),
                )
            if invalidate_translations:
                cursor.execute("DELETE FROM translation_content WHERE record_id=%s", (record_id,))
                cursor.execute(
                    "UPDATE dpr_report_record SET translation_status=CASE "
                    "WHEN translation_status IN ('QUEUED','NOT_REQUIRED') THEN translation_status ELSE 'PENDING' END,"
                    "translation_progress=CASE WHEN translation_status='NOT_REQUIRED' THEN '100' ELSE '0' END,"
                    "translation_error='',translation_version='',translation_updated_at='' "
                    "WHERE record_id=%s",
                    (record_id,),
                )
        connection.commit()
    return {
        "record_id": record_id,
        "database_path": "mysql",
        "updated_at": updated_at,
        "normalization": normalization,
    }


def load_report_payload(database_path: str | Path | None, record_id: str) -> dict[str, Any]:
    del database_path
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM dpr_report_record WHERE record_id=%s", (record_id,))
            record = cursor.fetchone()
            if not record:
                raise KeyError(record_id)
            report_type = _normalize_report_type(str(record.get("report_type", "") or ""))
            cursor.execute("SELECT fields_json FROM dpr_report_field WHERE record_id=%s", (record_id,))
            fields_row = cursor.fetchone() or {}
            payload: dict[str, Any] = {
                "metadata": {
                    "record_id": record_id,
                    "report_type": report_type,
                    "source_file": record.get("source_file", ""),
                    "parser": record.get("parser", ""),
                    "source_page_start": record.get("source_page_start", ""),
                    "source_page_end": record.get("source_page_end", ""),
                    "source_report_index": record.get("source_report_index", ""),
                    "source_report_count": record.get("source_report_count", ""),
                    "batch_inherited_fields": [
                        value
                        for value in str(record.get("batch_inherited_fields", "") or "").split(",")
                        if value
                    ],
                    "source_language": record.get("source_language", ""),
                    "translation_status": record.get("translation_status", ""),
                    "translation_progress": record.get("translation_progress", ""),
                    "translation_error": record.get("translation_error", ""),
                    "translation_version": record.get("translation_version", ""),
                    "translation_updated_at": record.get("translation_updated_at", ""),
                    "extraction_status": record.get("extraction_status", ""),
                    "extraction_progress": record.get("extraction_progress", ""),
                    "extraction_error": record.get("extraction_error", ""),
                    "extraction_version": record.get("extraction_version", ""),
                    "extraction_updated_at": record.get("extraction_updated_at", ""),
                    "locked": record.get("locked", ""),
                    "confirmation_status": record.get("confirmation_status", ""),
                    "confirmed_at": record.get("confirmed_at", ""),
                    "confirmed_by": record.get("confirmed_by", ""),
                    "confirmation_note": record.get("confirmation_note", ""),
                },
                "report_fields": _json_loads(fields_row.get("fields_json"), {}),
            }
            cursor.execute(
                "SELECT module_name, row_json FROM dpr_report_row WHERE record_id=%s ORDER BY module_name, row_no",
                (record_id,),
            )
            rows = cursor.fetchall()
    for module_name in REPORT_TABLES[report_type]["multi"]:
        payload[module_name] = []
    for row in rows:
        module_name = str(row.get("module_name", "") or "")
        if module_name in payload:
            payload[module_name].append(_json_loads(row.get("row_json"), {}))
    translation_content = load_translation_content(None, record_id)
    if translation_content:
        payload["translation_content"] = translation_content
    return payload


def load_report_payloads(
    database_path: str | Path | None,
    record_ids: list[str],
    *,
    include_translations: bool = False,
) -> dict[str, dict[str, Any]]:
    del database_path
    clean_ids = list(dict.fromkeys(str(value or "").strip() for value in record_ids if str(value or "").strip()))
    if not clean_ids:
        return {}
    placeholders = ",".join(["%s"] * len(clean_ids))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT r.*, f.fields_json
                FROM dpr_report_record r
                LEFT JOIN dpr_report_field f ON f.record_id=r.record_id
                WHERE r.record_id IN ({placeholders})
                """,
                clean_ids,
            )
            records = cursor.fetchall()
            cursor.execute(
                f"""
                SELECT record_id, module_name, row_no, row_json
                FROM dpr_report_row
                WHERE record_id IN ({placeholders})
                ORDER BY record_id, module_name, row_no
                """,
                clean_ids,
            )
            rows = cursor.fetchall()
            translations: list[dict[str, Any]] = []
            if include_translations:
                cursor.execute(
                    f"SELECT * FROM translation_content WHERE record_id IN ({placeholders})",
                    clean_ids,
                )
                translations = cursor.fetchall()

    payloads: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = _text(record.get("record_id"))
        report_type = _normalize_report_type(_text(record.get("report_type")))
        payloads[record_id] = {
            "metadata": _payload_metadata(record),
            "report_fields": _json_loads(record.get("fields_json"), {}),
            **{module_name: [] for module_name in REPORT_TABLES[report_type]["multi"]},
        }
    for row in rows:
        payload = payloads.get(_text(row.get("record_id")))
        module_name = _text(row.get("module_name"))
        if payload is not None and isinstance(payload.get(module_name), list):
            payload[module_name].append(_json_loads(row.get("row_json"), {}))
    if include_translations:
        for row in translations:
            payload = payloads.get(_text(row.get("record_id")))
            if payload is not None:
                payload.setdefault("translation_content", []).append({
                    key: _text(value)
                    for key, value in row.items()
                    if key != "mysql_updated_at"
                })
    return payloads


def delete_report_payload(database_path: str | Path | None, record_id: str) -> bool:
    del database_path
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT report_type, well_id, wellbore FROM dpr_report_record WHERE record_id=%s FOR UPDATE",
                (record_id,),
            )
            existing = cursor.fetchone() or {}
            cursor.execute("DELETE FROM dpr_report_record WHERE record_id=%s", (record_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                from .report_normalization_service import refresh_boundary_hour_issues

                refresh_boundary_hour_issues(
                    cursor,
                    report_type=str(existing.get("report_type", "") or ""),
                    well_id=_positive_int(existing.get("well_id")),
                    wellbore=str(existing.get("wellbore", "") or ""),
                    actor="system",
                )
        connection.commit()
    return deleted


def save_translation_content(database_path: str | Path | None, record_id: str, rows: list[dict[str, Any]]) -> None:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM translation_content WHERE record_id=%s", (record_id,))
            for row in rows:
                if not isinstance(row, dict):
                    continue
                cursor.execute(
                    """
                    INSERT INTO translation_content (
                      record_id, entity_type, entity_id, field_code, source_language, target_language,
                      source_text, translated_text, source_hash, model_config_id, prompt_version,
                      translation_status, error_message, is_manual_modified, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                      source_text=VALUES(source_text),
                      translated_text=VALUES(translated_text),
                      source_hash=VALUES(source_hash),
                      model_config_id=VALUES(model_config_id),
                      prompt_version=VALUES(prompt_version),
                      translation_status=VALUES(translation_status),
                      error_message=VALUES(error_message),
                      is_manual_modified=VALUES(is_manual_modified),
                      updated_at=VALUES(updated_at)
                    """,
                    (
                        record_id,
                        _text(row.get("entity_type")),
                        _text(row.get("entity_id")),
                        _text(row.get("field_code")),
                        _text(row.get("source_language")),
                        _text(row.get("target_language")),
                        _text(row.get("source_text")),
                        _text(row.get("translated_text")),
                        _text(row.get("source_hash")),
                        _text(row.get("model_config_id")),
                        _text(row.get("prompt_version")),
                        _text(row.get("translation_status")),
                        _text(row.get("error_message")),
                        _text(row.get("is_manual_modified")),
                        _text(row.get("created_at")),
                        _text(row.get("updated_at")),
                    ),
                )
        connection.commit()


def upsert_translation_content(database_path: str | Path | None, record_id: str, rows: list[dict[str, Any]]) -> None:
    """Persist completed translation units without replacing other units for the report."""
    del database_path
    if not record_id or not rows:
        return
    initialize_database()
    values = [
        (
            record_id,
            _text(row.get("entity_type")),
            _text(row.get("entity_id")),
            _text(row.get("field_code")),
            _text(row.get("source_language")),
            _text(row.get("target_language")),
            _text(row.get("source_text")),
            _text(row.get("translated_text")),
            _text(row.get("source_hash")),
            _text(row.get("model_config_id")),
            _text(row.get("prompt_version")),
            _text(row.get("translation_status")),
            _text(row.get("error_message")),
            _text(row.get("is_manual_modified")),
            _text(row.get("created_at")),
            _text(row.get("updated_at")),
        )
        for row in rows
        if isinstance(row, dict)
    ]
    if not values:
        return
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO translation_content (
                  record_id, entity_type, entity_id, field_code, source_language, target_language,
                  source_text, translated_text, source_hash, model_config_id, prompt_version,
                  translation_status, error_message, is_manual_modified, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  source_text=VALUES(source_text),
                  translated_text=VALUES(translated_text),
                  source_hash=VALUES(source_hash),
                  model_config_id=VALUES(model_config_id),
                  prompt_version=VALUES(prompt_version),
                  translation_status=VALUES(translation_status),
                  error_message=VALUES(error_message),
                  is_manual_modified=IF(is_manual_modified<>'', is_manual_modified, VALUES(is_manual_modified)),
                  updated_at=VALUES(updated_at)
                """,
                values,
            )
        connection.commit()


def load_translation_content(database_path: str | Path | None, record_id: str) -> list[dict[str, str]]:
    del database_path
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM translation_content WHERE record_id=%s", (record_id,))
            rows = cursor.fetchall()
    return [{key: _text(value) for key, value in row.items() if key != "mysql_updated_at"} for row in rows]


def load_translation_memory(
    database_path: str | Path | None,
    target_language: str,
    prompt_version: str,
    source_hashes: list[str] | None = None,
    report_type: str = "",
) -> dict[str, str]:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            clean_hashes = list(dict.fromkeys(
                str(value or "").strip()
                for value in source_hashes or []
                if str(value or "").strip()
            ))
            memory: dict[str, str] = {}
            if clean_hashes:
                placeholders = ",".join(["%s"] * len(clean_hashes))
                memory_args: list[object] = [target_language, *clean_hashes]
                report_filter = ""
                if report_type:
                    report_filter = " AND report_type IN ('', %s)"
                    memory_args.append(report_type)
                cursor.execute(
                    f"""
                    SELECT source_hash, translated_text, report_type, updated_at
                    FROM translation_memory
                    WHERE target_language=%s
                      AND confirmed='true'
                      AND source_hash IN ({placeholders})
                      {report_filter}
                    ORDER BY (report_type<>'') DESC, updated_at DESC
                    """,
                    memory_args,
                )
                for row in cursor.fetchall():
                    key = _text(row.get("source_hash"))
                    value = _text(row.get("translated_text"))
                    if key and value and key not in memory:
                        memory[key] = value
            hash_filter = ""
            args: list[object] = [target_language, prompt_version]
            if clean_hashes:
                remaining_hashes = [value for value in clean_hashes if value not in memory]
                if not remaining_hashes:
                    return memory
                placeholders = ",".join(["%s"] * len(remaining_hashes))
                hash_filter = f" AND source_hash IN ({placeholders})"
                args.extend(remaining_hashes)
            cursor.execute(
                f"""
                SELECT source_hash, translated_text, is_manual_modified, updated_at
                FROM translation_content
                WHERE target_language=%s
                  AND prompt_version=%s
                  AND translation_status='COMPLETED'
                  AND source_hash<>''
                  AND translated_text<>''
                  {hash_filter}
                ORDER BY (is_manual_modified<>'') DESC, updated_at DESC
                """,
                args,
            )
            rows = cursor.fetchall()
    for row in rows:
        key = _text(row.get("source_hash"))
        value = _text(row.get("translated_text"))
        if key and value and key not in memory:
            memory[key] = value
    return memory


def list_translation_memory(
    database_path: str | Path | None,
    *,
    query: str = "",
    report_type: str = "",
    limit: int = 200,
) -> list[dict[str, Any]]:
    del database_path
    initialize_database()
    clauses = ["1=1"]
    args: list[object] = []
    if query.strip():
        clauses.append("(source_text LIKE %s OR translated_text LIKE %s)")
        pattern = f"%{query.strip()}%"
        args.extend([pattern, pattern])
    if report_type.strip():
        clauses.append("report_type=%s")
        args.append(report_type.strip().lower())
    args.append(max(1, min(int(limit or 200), 1000)))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM translation_memory
                WHERE {' AND '.join(clauses)}
                ORDER BY updated_at DESC, id DESC
                LIMIT %s
                """,
                args,
            )
            rows = cursor.fetchall()
    return [
        {key: (_text(value) if key != "usage_count" and key != "id" else value) for key, value in row.items() if key != "mysql_updated_at"}
        for row in rows
    ]


def save_translation_memory_entry(database_path: str | Path | None, entry: dict[str, Any]) -> dict[str, Any]:
    del database_path
    initialize_database()
    source_text = _text(entry.get("source_text")).strip()
    translated_text = _text(entry.get("translated_text")).strip()
    target_language = _text(entry.get("target_language") or "zh-CN").strip()
    if not source_text or not translated_text:
        raise ValueError("翻译记忆的原文和标准译文不能为空。")
    source_hash_value = _text(entry.get("source_hash")).strip() or _translation_source_hash(source_text)
    now = _now()
    values = (
        _text(entry.get("source_language")), target_language, source_text, source_hash_value,
        translated_text, _text(entry.get("report_type")).lower(), _text(entry.get("operation_category")),
        _text(entry.get("field_code")), _text(entry.get("source_record_id")),
        "true" if _truthy(entry.get("confirmed", True)) else "false", _text(entry.get("confirmed_by")),
        _text(entry.get("created_at") or now), now,
    )
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO translation_memory (
                  source_language, target_language, source_text, source_hash, translated_text,
                  report_type, operation_category, field_code, source_record_id, confirmed,
                  confirmed_by, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  id=LAST_INSERT_ID(id), source_language=VALUES(source_language), source_text=VALUES(source_text),
                  translated_text=VALUES(translated_text), operation_category=VALUES(operation_category),
                  source_record_id=VALUES(source_record_id), confirmed=VALUES(confirmed),
                  confirmed_by=VALUES(confirmed_by), updated_at=VALUES(updated_at)
                """,
                values,
            )
            entry_id = int(cursor.lastrowid or 0)
        connection.commit()
    return {"id": entry_id, "source_hash": source_hash_value, "updated_at": now}


def delete_translation_memory_entry(database_path: str | Path | None, entry_id: int) -> bool:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM translation_memory WHERE id=%s", (int(entry_id),))
            deleted = cursor.rowcount > 0
        connection.commit()
    return deleted


def revise_translation_content(
    database_path: str | Path | None,
    *,
    record_id: str,
    entity_id: str,
    field_code: str,
    target_language: str,
    revised_text: str,
    editor: str = "",
    note: str = "",
    add_to_memory: bool = True,
    report_type: str = "",
) -> dict[str, Any]:
    del database_path
    initialize_database()
    revised = _text(revised_text).strip()
    if not revised:
        raise ValueError("修订译文不能为空。")
    now = _now()
    memory_entry: dict[str, Any] | None = None
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT source_language, source_text, translated_text, source_hash
                   FROM translation_content
                   WHERE record_id=%s AND entity_id=%s AND field_code=%s AND target_language=%s
                   FOR UPDATE""",
                (record_id, entity_id, field_code, target_language),
            )
            current = cursor.fetchone()
            if not current:
                raise KeyError("未找到需要修订的译文。")
            previous = _text(current.get("translated_text"))
            cursor.execute(
                """UPDATE translation_content
                   SET translated_text=%s, translation_status='COMPLETED', error_message='',
                       is_manual_modified='true', updated_at=%s
                   WHERE record_id=%s AND entity_id=%s AND field_code=%s AND target_language=%s""",
                (revised, now, record_id, entity_id, field_code, target_language),
            )
            cursor.execute(
                """INSERT INTO translation_revision (
                     record_id, entity_id, field_code, target_language, source_text,
                     previous_text, revised_text, revision_type, editor, note, created_at
                   ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'manual', %s, %s, %s)""",
                (record_id, entity_id, field_code, target_language, _text(current.get("source_text")), previous, revised, editor, note, now),
            )
            if add_to_memory:
                memory_entry = {
                    "source_language": _text(current.get("source_language")),
                    "target_language": target_language,
                    "source_text": _text(current.get("source_text")),
                    "source_hash": _text(current.get("source_hash")),
                    "translated_text": revised,
                    "report_type": report_type,
                    "field_code": field_code,
                    "source_record_id": record_id,
                    "confirmed": True,
                    "confirmed_by": editor,
                }
        connection.commit()
    if memory_entry:
        save_translation_memory_entry(None, memory_entry)
    return {"record_id": record_id, "field_code": field_code, "translated_text": revised, "updated_at": now}


def load_operation_translations(database_path: str | Path | None, record_ids: list[str]) -> list[dict[str, str]]:
    del database_path
    clean_ids = list(dict.fromkeys(record_id for record_id in record_ids if record_id))
    if not clean_ids:
        return []
    placeholders = ",".join(["%s"] * len(clean_ids))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT record_id, entity_id, source_text, translated_text, source_hash,
                       target_language, translation_status, error_message
                FROM translation_content
                WHERE record_id IN ({placeholders})
                  AND entity_type='operations'
                  AND field_code='operations.operation_details'
                  AND target_language='zh-CN'
                """,
                clean_ids,
            )
            rows = cursor.fetchall()
    return [{key: _text(value) for key, value in row.items()} for row in rows]


def clear_translation_content(database_path: str | Path | None, record_id: str = "") -> None:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            if record_id:
                cursor.execute("DELETE FROM translation_content WHERE record_id=%s", (record_id,))
            else:
                cursor.execute("DELETE FROM translation_content")
            connection.commit()


def reset_translation_state(database_path: str | Path | None, record_id: str = "") -> dict[str, int]:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            if record_id:
                cursor.execute("DELETE FROM translation_content WHERE record_id=%s", (record_id,))
                deleted_rows = cursor.rowcount
                cursor.execute(
                    """
                    UPDATE dpr_report_record
                    SET translation_status='PENDING', translation_progress='0',
                        translation_error='', translation_version='', translation_updated_at=%s
                    WHERE record_id=%s
                    """,
                    (_now(), record_id),
                )
            else:
                cursor.execute("DELETE FROM translation_content")
                deleted_rows = cursor.rowcount
                cursor.execute(
                    """
                    UPDATE dpr_report_record
                    SET translation_status='PENDING', translation_progress='0',
                        translation_error='', translation_version='', translation_updated_at=%s
                    """,
                    (_now(),),
                )
            reset_records = cursor.rowcount
        connection.commit()
    return {"deleted_translation_rows": deleted_rows, "reset_records": reset_records}


def update_record_translation_status(
    database_path: str | Path | None,
    record_id: str,
    *,
    status: str,
    progress: int | str = "",
    error: str = "",
    version: str = "",
) -> None:
    del database_path
    if not record_id:
        return
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            if version:
                cursor.execute(
                    """
                    UPDATE dpr_report_record
                    SET translation_status=%s, translation_progress=%s, translation_error=%s,
                        translation_version=%s, translation_updated_at=%s
                    WHERE record_id=%s
                    """,
                    (_text(status), _text(progress), _text(error)[:500], _text(version), _now(), record_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE dpr_report_record
                    SET translation_status=%s, translation_progress=%s, translation_error=%s, translation_updated_at=%s
                    WHERE record_id=%s
                    """,
                    (_text(status), _text(progress), _text(error)[:500], _now(), record_id),
                )
            connection.commit()


def update_record_extraction_status(database_path: str | Path | None, record_id: str, *, status: str, progress: int | str = "", error: str = "", version: str = "") -> None:
    del database_path
    if not record_id:
        return
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE dpr_report_record SET extraction_status=%s, extraction_progress=%s,
                   extraction_error=%s, extraction_version=IF(%s='', extraction_version, %s), extraction_updated_at=%s
                   WHERE record_id=%s""",
                (_text(status), _text(progress), _text(error)[:500], _text(version), _text(version), _now(), record_id),
            )
        connection.commit()


def save_extraction_results(database_path: str | Path | None, rows: list[dict[str, Any]]) -> None:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            for row in rows:
                cursor.execute(
                    """INSERT INTO ai_extraction_result
                    (record_id, rule_id, source_section, source_row_no, source_field, target_field,
                     source_hash, result_text, extraction_status, error_message, model_config_id,
                     rule_version, attempt_count, started_at, completed_at, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE source_hash=VALUES(source_hash), result_text=VALUES(result_text),
                    extraction_status=VALUES(extraction_status), error_message=VALUES(error_message),
                    model_config_id=VALUES(model_config_id), rule_version=VALUES(rule_version),
                    attempt_count=VALUES(attempt_count), started_at=VALUES(started_at),
                    completed_at=VALUES(completed_at), updated_at=VALUES(updated_at)""",
                    (_text(row.get("record_id")), _text(row.get("rule_id")), _text(row.get("source_section")), int(row.get("source_row_no", 0) or 0),
                     _text(row.get("source_field")), _text(row.get("target_field")), _text(row.get("source_hash")), _text(row.get("result_text")),
                     _text(row.get("extraction_status")), _text(row.get("error_message"))[:500], _text(row.get("model_config_id")), _text(row.get("rule_version")),
                     int(row.get("attempt_count", 0) or 0), _text(row.get("started_at")), _text(row.get("completed_at")), _text(row.get("updated_at"))))
        connection.commit()


def load_extraction_results(database_path: str | Path | None, record_id: str = "") -> list[dict[str, Any]]:
    del database_path
    initialize_database()
    sql = "SELECT * FROM ai_extraction_result"
    args: tuple[object, ...] = ()
    if record_id:
        sql += " WHERE record_id=%s"
        args = (record_id,)
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
    return [{key: (_text(value) if key != "source_row_no" and key != "attempt_count" else int(value or 0)) for key, value in row.items() if key != "mysql_updated_at"} for row in rows]


def save_aggregate_extraction_results(database_path: str | Path | None, rows: list[dict[str, Any]]) -> None:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            for row in rows:
                source_record_ids = row.get("source_record_ids") if isinstance(row.get("source_record_ids"), list) else []
                result_json = row.get("result_json")
                if isinstance(result_json, (dict, list)):
                    result_json = json.dumps(result_json, ensure_ascii=False)
                cursor.execute(
                    """INSERT INTO ai_extraction_aggregate_result
                    (scope_key,rule_id,grain,record_id,project_id,job_id,job_sequence_no,well_id,team_id,
                     profession,period_start,period_end,target_field,output_format,source_hash,
                     source_record_count,source_record_ids,result_text,result_number,result_date,result_json,
                     extraction_status,error_message,model_config_id,rule_version,attempt_count,completed_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE grain=VALUES(grain),record_id=VALUES(record_id),
                    project_id=VALUES(project_id),job_id=VALUES(job_id),job_sequence_no=VALUES(job_sequence_no),
                    well_id=VALUES(well_id),team_id=VALUES(team_id),profession=VALUES(profession),
                    period_start=VALUES(period_start),period_end=VALUES(period_end),
                    output_format=VALUES(output_format),source_hash=VALUES(source_hash),source_record_count=VALUES(source_record_count),
                    source_record_ids=VALUES(source_record_ids),result_text=VALUES(result_text),
                    result_number=VALUES(result_number),result_date=VALUES(result_date),result_json=VALUES(result_json),
                    extraction_status=VALUES(extraction_status),error_message=VALUES(error_message),
                    model_config_id=VALUES(model_config_id),rule_version=VALUES(rule_version),
                    attempt_count=VALUES(attempt_count),completed_at=VALUES(completed_at),updated_at=VALUES(updated_at)""",
                    (
                        _text(row.get("scope_key")), _text(row.get("rule_id")), _text(row.get("grain")),
                        _text(row.get("record_id")) or None, int(row.get("project_id") or 0) or None,
                        int(row.get("job_id") or 0) or None, int(row.get("job_sequence_no") or 0) or None,
                        int(row.get("well_id") or 0) or None, int(row.get("team_id") or 0) or None,
                        _text(row.get("profession")), _text(row.get("period_start")) or None, _text(row.get("period_end")) or None,
                        _text(row.get("target_field")), _text(row.get("output_format") or "text"), _text(row.get("source_hash")),
                        int(row.get("source_record_count") or len(source_record_ids)),
                        json.dumps(source_record_ids, ensure_ascii=False), _text(row.get("result_text")),
                        row.get("result_number"), _text(row.get("result_date")) or None, result_json,
                        _text(row.get("extraction_status")), _text(row.get("error_message"))[:500],
                        _text(row.get("model_config_id")), _text(row.get("rule_version")),
                        int(row.get("attempt_count") or 0), _text(row.get("completed_at")), _text(row.get("updated_at")),
                    ),
                )
        connection.commit()


def load_aggregate_extraction_results(
    database_path: str | Path | None,
    *,
    rule_id: str = "",
    target_field: str = "",
    period_start: str = "",
    team_ids: list[int] | None = None,
    well_ids: list[int] | None = None,
    scope_keys: list[str] | None = None,
    grain: str = "",
) -> list[dict[str, Any]]:
    del database_path
    initialize_database()
    conditions: list[str] = []
    args: list[object] = []
    if rule_id:
        conditions.append("rule_id=%s")
        args.append(rule_id)
    if target_field:
        conditions.append("target_field=%s")
        args.append(target_field)
    if period_start:
        conditions.append("period_start=%s")
        args.append(period_start)
    if grain:
        conditions.append("grain=%s")
        args.append(grain)
    normalized_team_ids = [int(value) for value in (team_ids or []) if int(value) > 0]
    if normalized_team_ids:
        conditions.append(f"team_id IN ({','.join(['%s'] * len(normalized_team_ids))})")
        args.extend(normalized_team_ids)
    normalized_well_ids = [int(value) for value in (well_ids or []) if int(value) > 0]
    if normalized_well_ids:
        conditions.append(f"well_id IN ({','.join(['%s'] * len(normalized_well_ids))})")
        args.extend(normalized_well_ids)
    normalized_scope_keys = [str(value or "").strip() for value in (scope_keys or []) if str(value or "").strip()]
    if normalized_scope_keys:
        conditions.append(f"scope_key IN ({','.join(['%s'] * len(normalized_scope_keys))})")
        args.extend(normalized_scope_keys)
    sql = "SELECT * FROM ai_extraction_aggregate_result"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
    result: list[dict[str, Any]] = []
    for row in rows:
        item = {key: value for key, value in row.items() if key != "mysql_updated_at"}
        for key in ("project_id", "job_id", "job_sequence_no", "well_id", "team_id"):
            item[key] = int(item.get(key) or 0)
        item["source_record_count"] = int(item.get("source_record_count") or 0)
        item["attempt_count"] = int(item.get("attempt_count") or 0)
        item["period_start"] = _text(item.get("period_start"))[:10]
        item["period_end"] = _text(item.get("period_end"))[:10]
        raw_ids = item.get("source_record_ids")
        item["source_record_ids"] = _json_loads(raw_ids, []) if not isinstance(raw_ids, list) else raw_ids
        raw_json = item.get("result_json")
        item["result_json"] = _json_loads(raw_json, None) if not isinstance(raw_json, (dict, list)) else raw_json
        for key in ("scope_key", "rule_id", "grain", "record_id", "profession", "target_field", "output_format", "source_hash", "result_text", "result_date", "extraction_status", "error_message", "model_config_id", "rule_version", "completed_at", "updated_at"):
            item[key] = _text(item.get(key))
        result.append(item)
    return result


def save_extraction_result_sources(database_path: str | Path | None, rows: list[dict[str, Any]]) -> None:
    del database_path
    if not rows:
        return
    initialize_database()
    groups = sorted({
        (_text(row.get("scope_key")), _text(row.get("rule_id")), _text(row.get("target_field")))
        for row in rows
    })
    with _connect() as connection:
        with connection.cursor() as cursor:
            for scope_key, rule_id, target_field in groups:
                cursor.execute(
                    "DELETE FROM ai_extraction_result_source WHERE scope_key=%s AND rule_id=%s AND target_field=%s",
                    (scope_key, rule_id, target_field),
                )
            for row in rows:
                cursor.execute(
                    """INSERT INTO ai_extraction_result_source
                    (lineage_key,scope_key,rule_id,target_field,record_id,source_section,source_row_no,source_field,source_hash,created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        hashlib.sha256("|".join((
                            _text(row.get("scope_key")), _text(row.get("rule_id")), _text(row.get("target_field")),
                            _text(row.get("record_id")), _text(row.get("source_section")),
                            str(int(row.get("source_row_no") or 0)), _text(row.get("source_field")),
                        )).encode("utf-8")).hexdigest(),
                        _text(row.get("scope_key")), _text(row.get("rule_id")), _text(row.get("target_field")),
                        _text(row.get("record_id")), _text(row.get("source_section")),
                        int(row.get("source_row_no") or 0), _text(row.get("source_field")),
                        _text(row.get("source_hash")), _text(row.get("created_at") or _now()),
                    ),
                )
        connection.commit()


def list_aggregate_scope_report_records(
    database_path: str | Path | None,
    *,
    scope: dict[str, Any],
    report_types: list[str] | tuple[str, ...],
) -> list[dict[str, Any]]:
    del database_path
    initialize_database()
    normalized_types = [value for value in report_types if value in REPORT_TABLES]
    profession = _text(scope.get("profession")).lower()
    if profession == "workover":
        normalized_types = [value for value in normalized_types if value == "workover"]
    elif profession == "drilling":
        normalized_types = [value for value in normalized_types if value in {"drilling", "completion"}]
    if not normalized_types:
        return []
    conditions = [f"report.report_type IN ({','.join(['%s'] * len(normalized_types))})"]
    args: list[object] = [*normalized_types]
    for key, column in (("project_id", "report.project_id"), ("well_id", "report.well_id"), ("team_id", "rig.team_id")):
        value = int(scope.get(key) or 0)
        if value:
            conditions.append(f"{column}=%s")
            args.append(value)
    sequence = int(scope.get("job_sequence_no") or 0)
    if sequence:
        conditions.append("job.sequence_no=%s")
        args.append(sequence)
    period_start = _text(scope.get("period_start"))[:10]
    period_end = _text(scope.get("period_end"))[:10]
    if period_start and period_end:
        conditions.append("report.report_date BETWEEN %s AND %s")
        args.extend([period_start, period_end])
    sql = f"""
        SELECT report.record_id,report.report_type,DATE_FORMAT(report.report_date,'%%Y-%%m-%%d') AS report_date,
               report.project_id,report.job_id,job.sequence_no AS job_sequence_no,report.well_id,
               COALESCE(well.well_name,raw_record.wellbore) AS well_name,
               rig.team_id,team.team_name
        FROM dpr_report report
        JOIN dpr_report_record raw_record ON raw_record.record_id=report.record_id
        LEFT JOIN biz_job job ON job.id=report.job_id
        LEFT JOIN md_well well ON well.id=report.well_id
        LEFT JOIN md_rig rig ON rig.id=report.rig_id
        LEFT JOIN md_team team ON team.id=rig.team_id
        WHERE {' AND '.join(conditions)}
        ORDER BY report.report_date,report.report_type,report.record_id
    """
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall() or []
    return [{
        "record_id": _text(row.get("record_id")), "report_type": _text(row.get("report_type")),
        "report_date": _text(row.get("report_date"))[:10], "project_id": int(row.get("project_id") or 0),
        "job_id": int(row.get("job_id") or 0), "job_sequence_no": int(row.get("job_sequence_no") or 0),
        "well_id": int(row.get("well_id") or 0), "well_name": _text(row.get("well_name")),
        "team_id": int(row.get("team_id") or 0), "team_name": _text(row.get("team_name")),
    } for row in rows]


def list_team_month_report_records(
    database_path: str | Path | None,
    *,
    period_start: str,
    period_end: str,
    report_types: list[str] | tuple[str, ...] = ("drilling", "completion"),
    team_ids: list[int] | None = None,
) -> list[dict[str, Any]]:
    del database_path
    initialize_database()
    normalized_types = [value for value in report_types if value in REPORT_TABLES]
    if not normalized_types:
        return []
    conditions = ["report.report_date BETWEEN %s AND %s", f"report.report_type IN ({','.join(['%s'] * len(normalized_types))})", "rig.team_id IS NOT NULL"]
    args: list[object] = [period_start, period_end, *normalized_types]
    normalized_team_ids = [int(value) for value in (team_ids or []) if int(value) > 0]
    if normalized_team_ids:
        conditions.append(f"rig.team_id IN ({','.join(['%s'] * len(normalized_team_ids))})")
        args.extend(normalized_team_ids)
    sql = f"""
        SELECT report.record_id,report.report_type,DATE_FORMAT(report.report_date,'%%Y-%%m-%%d') AS report_date,
               report.well_id,COALESCE(well.well_name,raw_record.wellbore) AS well_name,
               rig.team_id,team.team_name
        FROM dpr_report report
        JOIN dpr_report_record raw_record ON raw_record.record_id=report.record_id
        LEFT JOIN md_well well ON well.id=report.well_id
        LEFT JOIN md_rig rig ON rig.id=report.rig_id
        LEFT JOIN md_team team ON team.id=rig.team_id
        WHERE {' AND '.join(conditions)}
        ORDER BY rig.team_id,report.report_date,report.report_type,report.record_id
    """
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
    return [{
        "record_id": _text(row.get("record_id")),
        "report_type": _text(row.get("report_type")),
        "report_date": _text(row.get("report_date"))[:10],
        "well_id": int(row.get("well_id") or 0),
        "well_name": _text(row.get("well_name")),
        "team_id": int(row.get("team_id") or 0),
        "team_name": _text(row.get("team_name")),
    } for row in rows]


def save_ai_extraction_target_fields(
    database_path: str | Path | None,
    fields: list[dict[str, Any]],
    *,
    actor: str = "system",
) -> None:
    del database_path
    if not fields:
        return
    initialize_database()
    now = _now()
    with _connect() as connection:
        with connection.cursor() as cursor:
            for field in fields:
                cursor.execute(
                    """INSERT INTO ai_extraction_target_field
                    (field_code,field_label,output_format,grain,allowed_grains,field_description,is_system,enabled,created_by,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE field_label=VALUES(field_label),
                    output_format=VALUES(output_format),grain=VALUES(grain),allowed_grains=VALUES(allowed_grains),
                    field_description=VALUES(field_description),is_system=VALUES(is_system),
                    enabled=VALUES(enabled),updated_at=VALUES(updated_at)""",
                    (
                        _text(field.get("value"))[:128],
                        _text(field.get("label") or field.get("value"))[:128],
                        _text(field.get("output_format") or "text")[:32],
                        _text(field.get("grain") or "report")[:32],
                        json.dumps([_text(field.get("grain") or "report")[:32]], ensure_ascii=False),
                        _text(field.get("description"))[:512],
                        1 if field.get("is_system") else 0,
                        0 if field.get("enabled") is False else 1,
                        _text(actor)[:128],
                        now,
                        now,
                    ),
                )
        connection.commit()


def list_ai_extraction_target_fields(database_path: str | Path | None = None) -> list[dict[str, Any]]:
    del database_path
    initialize_database()
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT field_code,field_label,output_format,grain,allowed_grains,field_description,is_system,enabled,created_by,created_at,updated_at "
                "FROM ai_extraction_target_field WHERE enabled=1 ORDER BY is_system DESC,field_label,field_code"
            )
            rows = cursor.fetchall() or []
    return [{
        "value": _text(row.get("field_code")),
        "label": _text(row.get("field_label")),
        "output_format": _text(row.get("output_format") or "text"),
        "grain": _text(row.get("grain") or "report"),
        "allowed_grains": [_text(row.get("grain") or "report")],
        "description": _text(row.get("field_description")),
        "is_system": bool(row.get("is_system")),
        "enabled": bool(row.get("enabled")),
        "created_by": _text(row.get("created_by")),
        "created_at": _text(row.get("created_at")),
        "updated_at": _text(row.get("updated_at")),
    } for row in rows]


def clear_extraction_results(database_path: str | Path | None, record_ids: list[str]) -> None:
    del database_path
    if not record_ids:
        return
    initialize_database()
    placeholders = ",".join(["%s"] * len(record_ids))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM ai_extraction_result WHERE record_id IN ({placeholders})", record_ids)
        connection.commit()


def list_records(
    database_path: str | Path | None = None,
    *,
    report_type: str = "",
    wellbore: str = "",
    date: str = "",
    date_from: str = "",
    date_to: str = "",
) -> list[dict[str, str]]:
    del database_path
    clauses: list[str] = []
    args: list[object] = []
    if report_type:
        clauses.append("r.report_type=%s")
        args.append(report_type)
    if wellbore:
        clauses.append("r.wellbore=%s")
        args.append(wellbore)
    if date:
        clauses.append("r.report_date=%s")
        args.append(date)
    if date_from:
        clauses.append("r.report_date >= %s")
        args.append(date_from)
    if date_to:
        clauses.append("r.report_date <= %s")
        args.append(date_to)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
        SELECT r.*, f.fields_json
        FROM dpr_report_record r
        LEFT JOIN dpr_report_field f ON f.record_id = r.record_id
        {where_sql}
        ORDER BY r.report_date DESC, r.updated_at DESC
    """
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            record_ids = [_text(row.get("record_id")) for row in rows if row.get("record_id")]
            operation_rows: list[dict[str, Any]] = []
            if record_ids:
                placeholders = ",".join(["%s"] * len(record_ids))
                cursor.execute(
                    f"SELECT record_id, row_json FROM dpr_report_row WHERE module_name='operations' AND record_id IN ({placeholders})",
                    record_ids,
                )
                operation_rows = cursor.fetchall()
    operation_stats = _operation_hour_summary(operation_rows)
    for row in rows:
        values = operation_stats.get(_text(row.get("record_id")), {})
        row["p_hours"] = round(float(values.get("p_hours", 0.0)), 2)
        row["sc_hours"] = round(float(values.get("sc_hours", 0.0)), 2)
        row["npt_hours"] = round(float(values.get("npt_hours", 0.0)), 2)
    return [_record_to_public(row) for row in rows]


def load_production_report_remarks(
    database_path: str | Path | None = None,
    remark_keys: list[str] | tuple[str, ...] = (),
) -> dict[str, str]:
    """Load user-authored reporting annotations, never calculated statistics."""

    del database_path
    initialize_database()
    clean_keys = [str(value or "").strip() for value in remark_keys if str(value or "").strip()]
    where_sql = ""
    args: list[object] = []
    if clean_keys:
        where_sql = f"WHERE remark_key IN ({','.join(['%s'] * len(clean_keys))})"
        args.extend(clean_keys)
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT remark_key,remark_text FROM production_report_remark {where_sql}",
                args,
            )
            rows = cursor.fetchall()
    return {
        _text(row.get("remark_key")): _text(row.get("remark_text"))
        for row in rows
        if _text(row.get("remark_key"))
    }


def save_production_report_remark(
    database_path: str | Path | None,
    remark_key: str,
    remark_text: str,
    *,
    actor: str,
) -> None:
    """Upsert or remove one structured production-report annotation."""

    del database_path
    initialize_database()
    clean_key = str(remark_key or "").strip()
    clean_text = str(remark_text or "").strip()[:500]
    if not clean_key:
        raise ValueError("remark_key is required.")
    key_parts = clean_key.split("|", 2)
    project_code = key_parts[0].strip() if key_parts else ""
    source_rig = key_parts[1].strip() if len(key_parts) > 1 else ""
    source_well = key_parts[2].strip() if len(key_parts) > 2 else ""
    with _connect() as connection:
        with connection.cursor() as cursor:
            if not clean_text:
                cursor.execute("DELETE FROM production_report_remark WHERE remark_key=%s", (clean_key,))
                connection.commit()
                return
            project_id: int | None = int(project_code) if project_code.isdigit() and int(project_code) > 0 else None
            rig_id: int | None = None
            well_id: int | None = None
            if source_rig:
                cursor.execute(
                    "SELECT id FROM md_rig WHERE rig_name=%s OR rig_code=%s ORDER BY status='active' DESC,id LIMIT 1",
                    (source_rig, source_rig),
                )
                row = cursor.fetchone()
                rig_id = int(row["id"]) if row else None
            if source_well:
                cursor.execute(
                    "SELECT id FROM md_well WHERE well_name=%s OR well_code=%s ORDER BY status='active' DESC,id LIMIT 1",
                    (source_well, source_well),
                )
                row = cursor.fetchone()
                well_id = int(row["id"]) if row else None
            cursor.execute(
                """
                INSERT INTO production_report_remark
                  (remark_key,project_id,rig_id,well_id,source_rig_name,source_well_name,
                   remark_text,created_by,updated_by)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                  project_id=VALUES(project_id),rig_id=VALUES(rig_id),well_id=VALUES(well_id),
                  source_rig_name=VALUES(source_rig_name),source_well_name=VALUES(source_well_name),
                  remark_text=VALUES(remark_text),updated_by=VALUES(updated_by),version=version+1
                """,
                (
                    clean_key, project_id, rig_id, well_id, source_rig, source_well,
                    clean_text, actor, actor,
                ),
            )
        connection.commit()


def load_analytics_view_rows(
    database_path: str | Path | None = None,
    *,
    date_from: str = "",
    date_to: str = "",
    rigs: list[str] | tuple[str, ...] = (),
    report_type: str = "",
    wellbore: str = "",
    exact_wellbore: bool = False,
    project_ids: list[str] | tuple[str, ...] = (),
) -> dict[str, Any]:
    """Load analytics facts from canonical views; never reconstruct them from row JSON."""
    del database_path
    initialize_database()
    clauses: list[str] = []
    args: list[object] = []
    if date_from:
        clauses.append("timeline.report_date >= %s")
        args.append(date_from)
    if date_to:
        clauses.append("timeline.report_date <= %s")
        args.append(date_to)
    clean_rigs = [str(value or "").strip() for value in rigs if str(value or "").strip()]
    if clean_rigs:
        clauses.append(f"timeline.rig_name IN ({','.join(['%s'] * len(clean_rigs))})")
        args.extend(clean_rigs)
    if report_type:
        clauses.append("timeline.report_type=%s")
        args.append(report_type)
    if wellbore:
        clauses.append("LOWER(timeline.well_name) = %s" if exact_wellbore else "LOWER(timeline.well_name) LIKE %s")
        args.append(wellbore.lower() if exact_wellbore else f"%{wellbore.lower()}%")
    raw_project_ids = [str(value or "").strip() for value in project_ids if str(value or "").strip()]
    clean_project_ids = [int(value) for value in raw_project_ids if value.isdigit() and int(value) > 0]
    if raw_project_ids:
        if clean_project_ids:
            clauses.append(f"timeline.project_id IN ({','.join(['%s'] * len(clean_project_ids))})")
            args.extend(clean_project_ids)
        else:
            clauses.append("1=0")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
        SELECT timeline.*
        FROM vw_rig_production_timeline timeline
        {where_sql}
        ORDER BY timeline.report_date, timeline.record_id, timeline.source_row_no
    """
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = list(cursor.fetchall() or [])
            quality_clauses = ["report.normalization_status='NORMALIZED'"]
            quality_args: list[object] = []
            if date_from:
                quality_clauses.append("report.report_date >= %s")
                quality_args.append(date_from)
            if date_to:
                quality_clauses.append("report.report_date <= %s")
                quality_args.append(date_to)
            if clean_rigs:
                quality_clauses.append(f"report.rig_name IN ({','.join(['%s'] * len(clean_rigs))})")
                quality_args.extend(clean_rigs)
            if report_type:
                quality_clauses.append("report.report_type=%s")
                quality_args.append(report_type)
            if wellbore:
                quality_clauses.append(
                    "LOWER(report.well_name) = %s"
                    if exact_wellbore else
                    "LOWER(report.well_name) LIKE %s"
                )
                quality_args.append(wellbore.lower() if exact_wellbore else f"%{wellbore.lower()}%")
            if raw_project_ids:
                if clean_project_ids:
                    quality_clauses.append(f"report.project_id IN ({','.join(['%s'] * len(clean_project_ids))})")
                    quality_args.extend(clean_project_ids)
                else:
                    quality_clauses.append("1=0")
            cursor.execute(
                f"""
                SELECT report.match_status,COUNT(DISTINCT report.record_id) AS count_value
                FROM vw_report_analytics report
                WHERE {' AND '.join(quality_clauses)}
                GROUP BY report.match_status
                """,
                quality_args,
            )
            quality_rows = list(cursor.fetchall() or [])

    records: dict[str, dict[str, Any]] = {}
    operations: list[dict[str, Any]] = []
    for row in rows:
        record_id = _text(row.get("record_id"))
        report_date = _text(row.get("report_date"))[:10]
        project_id = _text(row.get("project_id"))
        record = {
            "record_id": record_id,
            "report_type": _text(row.get("report_type")),
            "reportDate": report_date,
            "rig": _text(row.get("rig_name")),
            "wellbore": _text(row.get("well_name")),
            "project_id": project_id,
            "project_name": _text(row.get("project_name")),
            "project_contract": _text(row.get("project_contract")),
            "master_match_status": _text(row.get("master_match_status")) or "MATCHED",
            "master_match_message": _text(row.get("master_match_message")),
            "validation_status": _text(row.get("validation_status")),
            "event": _text(row.get("event")),
            "afeNumber": _text(row.get("afe_number")),
        }
        records.setdefault(record_id, record)
        statistics_status = _text(row.get("statistics_status")).upper()
        source_type = _text(row.get("source_op_type")).upper()
        effective_type = _text(row.get("effective_op_type")).upper()
        statistics_ready = statistics_status == "READY"
        operation = {
            **record,
            "month": report_date[:7],
            "hours": round(float(row.get("hours") or 0), 3),
            "statistical_hours": round(float(row.get("statistical_hours") or 0), 3) if statistics_ready else None,
            "from": _text(row.get("source_from_text")),
            "to": _text(row.get("source_to_text")),
            "op_type": effective_type if statistics_ready else "PENDING",
            "source_op_type": source_type,
            "confirmed_op_type": _text(row.get("confirmed_op_type")).upper(),
            "classification_status": _text(row.get("confirmation_status")).upper() or "PENDING",
            "statistics_status": statistics_status,
            "statistics_ready": statistics_ready,
            "time_validation_status": _text(row.get("time_validation_status")).upper(),
            "hours_source": _text(row.get("hours_source")).upper() or "DECLARED",
            "op_code": _text(row.get("op_code")),
            "op_sub": _text(row.get("op_sub")),
            "work_category_code": _text(row.get("work_category_code")),
            "work_subcategory_code": _text(row.get("work_subcategory_code")),
            "operation_details": _text(row.get("operation_details")),
            "operation_details_normalized": _text(row.get("operation_details_normalized")),
            "source_row_no": int(row.get("source_row_no") or 0),
            "work_bucket": _text(row.get("work_bucket")),
            "billing_status": _text(row.get("billing_status")),
            "responsibility": _text(row.get("responsibility")),
            "cause_code": _text(row.get("cause_code")),
            "service_line": _text(row.get("service_line")),
            "rule_version": _text(row.get("rule_version")),
        }
        operation["time_range"] = " - ".join(value for value in (operation["from"], operation["to"]) if value)
        operation["reason"] = (
            operation["work_subcategory_code"]
            or operation["work_category_code"]
            or operation["op_sub"]
            or operation["op_code"]
            or "未分类"
        )
        operations.append(operation)
    quality_counts = {_text(row.get("match_status")): int(row.get("count_value") or 0) for row in quality_rows}
    return {
        "records": list(records.values()),
        "operations": operations,
        "quality": {
            "unassigned_count": quality_counts.get("UNASSIGNED", 0),
            "ambiguous_count": quality_counts.get("AMBIGUOUS", 0),
        },
    }


def load_monthly_efficiency_report_rows(
    database_path: str | Path | None = None,
    *,
    date_from: str = "",
    date_to: str = "",
    year_start: str = "",
) -> dict[str, Any]:
    """Load source-backed drilling/completion/workover facts at job grain for an optional date range."""
    del database_path
    initialize_database()
    range_start = date_from or "1000-01-01"
    range_end = date_to or "9999-12-31"
    cumulative_start = year_start or range_start
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                  DATE_FORMAT(MAX(report_date),'%Y-%m') AS latest_month,
                  DATE_FORMAT(MIN(report_date),'%Y-%m-%d') AS available_date_from,
                  DATE_FORMAT(MAX(report_date),'%Y-%m-%d') AS available_date_to
                FROM dpr_report
                WHERE match_status='MATCHED' AND normalization_status='NORMALIZED'
                  AND job_id IS NOT NULL
                """
            )
            latest_row = cursor.fetchone() or {}
            latest_month = _text(latest_row.get("latest_month"))
            available_date_from = _text(latest_row.get("available_date_from"))
            available_date_to = _text(latest_row.get("available_date_to"))

            cursor.execute(
                """
                SELECT
                  job.id AS job_id,
                  job.job_code,
                  job.job_type,
                  job.project_id,
                  project.project_code,
                  project.project_name,
                  contract.contract_no,
                  job.well_id,
                  well.well_code,
                  well.well_name,
                  well.well_type_code,
                  well.well_profile_code,
                  COALESCE(job.planned_depth_ft, well.planned_td_md_m * 3.280839895) AS design_depth_ft,
                  block.block_code,
                  block.block_name,
                  block.country,
                  GROUP_CONCAT(DISTINCT rig.rig_name ORDER BY rig.rig_name SEPARATOR ' / ') AS rig_name,
                  GROUP_CONCAT(DISTINCT team.team_code ORDER BY team.team_code SEPARATOR ' / ') AS team_code,
                  GROUP_CONCAT(DISTINCT team.team_name ORDER BY team.team_name SEPARATOR ' / ') AS team_name,
                  GROUP_CONCAT(DISTINCT team_company.organization_name ORDER BY team_company.organization_name SEPARATOR ' / ') AS team_company,
                  GROUP_CONCAT(DISTINCT rig_model.model_name ORDER BY rig_model.model_name SEPARATOR ' / ') AS rig_model,
                  MIN(report.report_date) AS report_start_date,
                  MAX(report.report_date) AS report_end_date,
                  COUNT(DISTINCT report.record_id) AS report_count,
                  SUBSTRING_INDEX(GROUP_CONCAT(report.record_id ORDER BY report.report_date DESC, report.id DESC), ',', 1) AS record_id,
                  GROUP_CONCAT(NULLIF(summary.other_remarks, '') ORDER BY report.report_date SEPARATOR '\n') AS other_remarks
                FROM biz_job job
                JOIN md_project project ON project.id=job.project_id
                LEFT JOIN md_contract contract ON contract.id=project.contract_id
                JOIN md_well well ON well.id=job.well_id
                LEFT JOIN md_block block ON block.id=well.block_id
                JOIN dpr_report report ON report.job_id=job.id
                  AND report.match_status='MATCHED'
                  AND report.normalization_status='NORMALIZED'
                  AND report.report_date BETWEEN %s AND %s
                LEFT JOIN md_rig rig ON rig.id=report.rig_id
                LEFT JOIN md_rig_model rig_model ON rig_model.id=rig.rig_model_id
                LEFT JOIN md_team team ON team.id=rig.team_id
                LEFT JOIN md_organization team_company ON team_company.id=team.company_id
                LEFT JOIN dpr_report_summary summary ON summary.daily_report_id=report.id
                WHERE job.job_type IN ('drilling','completion','workover')
                GROUP BY
                  job.id, job.job_code, job.job_type,
                  job.project_id, project.project_code, project.project_name, contract.contract_no,
                  job.well_id, well.well_code, well.well_name, well.well_type_code,
                  well.well_profile_code, job.planned_depth_ft, well.planned_td_md_m,
                  block.block_code, block.block_name, block.country
                ORDER BY project.project_name, well.well_name, job.job_type, job.id
                """,
                (range_start, range_end),
            )
            rows = [dict(row) for row in (cursor.fetchall() or [])]
            job_ids = [int(row["job_id"]) for row in rows if row.get("job_id") is not None]
            if not job_ids:
                return {
                    "latest_month": latest_month,
                    "available_date_from": available_date_from,
                    "available_date_to": available_date_to,
                    "rows": [],
                }

            placeholders = ",".join(["%s"] * len(job_ids))
            cursor.execute(
                f"""
                SELECT
                  report.job_id,
                  COUNT(operation.activity_id) AS operation_count,
                  SUM(CASE WHEN operation.statistics_status='READY' THEN 1 ELSE 0 END) AS ready_operation_count,
                  SUM(CASE WHEN operation.statistics_status<>'READY' THEN 1 ELSE 0 END) AS pending_operation_count,
                  ROUND(SUM(CASE WHEN operation.statistics_status='READY' AND operation.effective_op_type='P' THEN operation.statistical_hours ELSE 0 END),3) AS production_hours,
                  ROUND(SUM(CASE WHEN operation.statistics_status='READY' AND operation.effective_op_type='NPT' THEN operation.statistical_hours ELSE 0 END),3) AS npt_hours,
                  ROUND(SUM(CASE WHEN operation.statistics_status='READY' AND operation.effective_op_type='SC' THEN operation.statistical_hours ELSE 0 END),3) AS sc_hours,
                  ROUND(SUM(CASE WHEN operation.statistics_status<>'READY' THEN COALESCE(operation.declared_hours,0) ELSE 0 END),3) AS pending_hours,
                  GROUP_CONCAT(DISTINCT CASE
                    WHEN operation.statistics_status='READY' AND operation.effective_op_type IN ('NPT','SC')
                    THEN NULLIF(operation.operation_details_normalized,'') END
                    ORDER BY operation.report_date SEPARATOR '\n') AS nonproductive_description
                FROM vw_operation_structured operation
                JOIN dpr_report report ON report.record_id=operation.record_id
                WHERE report.job_id IN ({placeholders})
                  AND report.report_date BETWEEN %s AND %s
                  AND report.match_status='MATCHED'
                  AND report.normalization_status='NORMALIZED'
                GROUP BY report.job_id
                """,
                [*job_ids, range_start, range_end],
            )
            operations_by_job = {int(row["job_id"]): dict(row) for row in (cursor.fetchall() or [])}

            cursor.execute(
                f"""
                SELECT
                  report.job_id,
                  operation.record_id,
                  operation.source_row_no,
                  operation.operation_details,
                  operation.operation_details_normalized
                FROM vw_operation_structured operation
                JOIN dpr_report report ON report.record_id=operation.record_id
                WHERE report.job_id IN ({placeholders})
                  AND report.report_date BETWEEN %s AND %s
                  AND report.match_status='MATCHED'
                  AND report.normalization_status='NORMALIZED'
                  AND operation.statistics_status='READY'
                  AND operation.effective_op_type IN ('NPT','SC')
                  AND COALESCE(NULLIF(operation.operation_details,''), NULLIF(operation.operation_details_normalized,'')) IS NOT NULL
                ORDER BY report.job_id,report.report_date,operation.source_row_no
                """,
                [*job_ids, range_start, range_end],
            )
            nonproductive_operations_by_job: dict[int, list[dict[str, Any]]] = {}
            for operation_row in cursor.fetchall() or []:
                job_id = int(operation_row["job_id"])
                nonproductive_operations_by_job.setdefault(job_id, []).append({
                    "record_id": _text(operation_row.get("record_id")),
                    "source_row_no": int(operation_row.get("source_row_no") or 0),
                    "operation_details": _text(operation_row.get("operation_details")),
                    "operation_details_normalized": _text(operation_row.get("operation_details_normalized")),
                })

            cursor.execute(
                f"""
                SELECT job_id,progress_date,measured_depth_ft,daily_progress_ft,record_id
                FROM biz_job_depth_progress
                WHERE job_id IN ({placeholders}) AND progress_date BETWEEN %s AND %s
                ORDER BY job_id,progress_date,updated_at,id
                """,
                [*job_ids, cumulative_start, range_end],
            )
            depth_by_job: dict[int, dict[str, Any]] = {}
            for depth_row in cursor.fetchall() or []:
                job_id = int(depth_row["job_id"])
                item = depth_by_job.setdefault(job_id, {
                    "current_depth_ft": None,
                    "month_progress_ft": 0.0,
                    "year_progress_ft": 0.0,
                    "month_progress_count": 0,
                    "year_progress_count": 0,
                })
                progress_date = _text(depth_row.get("progress_date"))[:10]
                measured_depth = depth_row.get("measured_depth_ft")
                daily_progress = depth_row.get("daily_progress_ft")
                if measured_depth is not None:
                    item["current_depth_ft"] = float(measured_depth)
                if daily_progress is not None:
                    progress = float(daily_progress)
                    item["year_progress_ft"] += progress
                    item["year_progress_count"] += 1
                    if range_start <= progress_date <= range_end:
                        item["month_progress_ft"] += progress
                        item["month_progress_count"] += 1

            cursor.execute(
                f"""
                SELECT job_id,event_type,event_date,time_precision_code,confirmation_status
                FROM biz_job_event
                WHERE job_id IN ({placeholders})
                  AND event_type IN ('DRILLING_START','DRILLING_END','COMPLETION_START','COMPLETION_END','WORKOVER_START','WORKOVER_END')
                ORDER BY job_id,event_date,id
                """,
                job_ids,
            )
            events_by_job: dict[int, dict[str, str]] = {}
            for event_row in cursor.fetchall() or []:
                job_id = int(event_row["job_id"])
                event_type = _text(event_row.get("event_type")).upper()
                event_date = _text(event_row.get("event_date"))[:10]
                if event_type and event_date:
                    job_events = events_by_job.setdefault(job_id, {})
                    current = job_events.get(event_type, "")
                    if event_type.endswith("_START"):
                        job_events[event_type] = min(current, event_date) if current else event_date
                    else:
                        job_events[event_type] = max(current, event_date) if current else event_date

    for row in rows:
        job_id = int(row["job_id"])
        row.update(operations_by_job.get(job_id, {}))
        row.update(depth_by_job.get(job_id, {}))
        row["events"] = events_by_job.get(job_id, {})
        row["nonproductive_operations"] = nonproductive_operations_by_job.get(job_id, [])
    return {
        "latest_month": latest_month,
        "available_date_from": available_date_from,
        "available_date_to": available_date_to,
        "rows": rows,
    }


def load_drilling_basic_monthly_report_rows(
    database_path: str | Path | None = None,
    *,
    report_date: str,
) -> dict[str, Any]:
    """Load Appendix 4 drilling rows from the normalized monthly source view."""
    del database_path
    initialize_database()
    selected = date.fromisoformat(report_date)
    month_start = selected.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    year_start = selected.replace(month=1, day=1)
    current_month_start = date.today().replace(day=1)
    current_month_end = (current_month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT DATE_FORMAT(report_date, '%%Y-%%m') AS report_month
                FROM dpr_report
                WHERE report_type IN ('drilling','completion')
                  AND report_date IS NOT NULL
                  AND report_date <= %s
                ORDER BY report_month DESC
                """,
                (current_month_end,),
            )
            available_months = [
                _text(row.get("report_month"))
                for row in (cursor.fetchall() or [])
                if _text(row.get("report_month"))
            ]
            cursor.execute(
                """
                SELECT DISTINCT project_id,well_id,job_sequence_no
                FROM vw_drilling_basic_monthly_source
                WHERE report_type IN ('drilling','completion')
                  AND report_date BETWEEN %s AND %s
                ORDER BY project_id,well_id,job_sequence_no
                """,
                (month_start, month_end),
            )
            scope_keys = {
                (int(row.get("project_id") or 0), int(row.get("well_id") or 0), int(row.get("job_sequence_no") or 1))
                for row in (cursor.fetchall() or [])
            }
            if not scope_keys:
                return {
                    "report_date": report_date,
                    "month_start": month_start.isoformat(),
                    "month_end": month_end.isoformat(),
                    "year_start": year_start.isoformat(),
                    "available_months": available_months,
                    "rows": [],
                }
            project_ids = sorted({scope[0] for scope in scope_keys})
            placeholders = ",".join(["%s"] * len(project_ids))
            cursor.execute(
                f"""
                SELECT *
                FROM vw_drilling_basic_monthly_source
                WHERE report_type IN ('drilling','completion')
                  AND project_id IN ({placeholders})
                ORDER BY project_id,well_id,job_sequence_no,report_type,report_date,report_no,daily_report_id
                """,
                project_ids,
            )
            source_rows = [dict(row) for row in (cursor.fetchall() or [])]
    grouped: dict[tuple[int, int, int], dict[str, list[dict[str, Any]]]] = {}
    for row in source_rows:
        key = (int(row.get("project_id") or 0), int(row.get("well_id") or 0), int(row.get("job_sequence_no") or 1))
        if key not in scope_keys:
            continue
        report_type = _text(row.get("report_type")).lower()
        if report_type not in {"drilling", "completion"}:
            continue
        grouped.setdefault(key, {"drilling": [], "completion": []})[report_type].append(row)
    result_rows = [
        _drilling_basic_monthly_scope_row(
            phases["drilling"],
            phases["completion"],
            month_start=month_start,
            month_end=month_end,
            year_start=year_start,
        )
        for phases in grouped.values()
    ]
    result_rows.sort(key=lambda row: (
        _text(row.get("team_code")),
        _text(row.get("well_name")),
        int(row.get("job_id") or 0),
    ))
    return {
        "report_date": report_date,
        "month_start": month_start.isoformat(),
        "month_end": month_end.isoformat(),
        "year_start": year_start.isoformat(),
        "available_months": available_months,
        "rows": result_rows,
    }


def _drilling_basic_monthly_scope_row(
    drilling_rows: list[dict[str, Any]],
    completion_rows: list[dict[str, Any]],
    *,
    month_start: date,
    month_end: date,
    year_start: date,
) -> dict[str, Any]:
    ordered = sorted(drilling_rows, key=lambda row: (
        _text(row.get("report_date"))[:10],
        int(row.get("report_no") or 0),
        int(row.get("daily_report_id") or 0),
    ))
    completion = sorted(completion_rows, key=lambda row: (
        _text(row.get("report_date"))[:10],
        int(row.get("report_no") or 0),
        int(row.get("daily_report_id") or 0),
    ))
    all_rows = ordered + completion
    if not all_rows:
        raise ValueError("Monthly drilling scope requires at least one drilling or completion report")
    base = ordered[-1] if ordered else completion[-1]
    numbered = [row for row in ordered if row.get("report_no") is not None]
    first_report = next((row for row in numbered if int(row.get("report_no") or 0) == 1), None)
    last_report = max(numbered, key=lambda row: (int(row.get("report_no") or 0), _text(row.get("report_date")))) if numbered else None
    month_progress = sum(
        float(row.get("daily_progress_ft") or 0)
        for row in ordered
        if month_start.isoformat() <= _text(row.get("report_date"))[:10] <= month_end.isoformat()
    )
    year_progress = sum(
        float(row.get("daily_progress_ft") or 0)
        for row in ordered
        if year_start.isoformat() <= _text(row.get("report_date"))[:10] <= month_end.isoformat()
    )
    current_depth_rows = [
        row for row in ordered
        if row.get("measured_depth_ft") is not None and _text(row.get("report_date"))[:10] <= month_end.isoformat()
    ]
    drilling_hours = sum(float(row.get("report_hours") or 0) for row in ordered)
    completion_hours = sum(float(row.get("report_hours") or 0) for row in completion)
    planned_start = ordered[-1].get("planned_start") if ordered else None
    planned_end = ordered[-1].get("planned_end") if ordered else None
    planned_drilling_days = None
    if planned_start and planned_end:
        planned_drilling_days = round((planned_end - planned_start).total_seconds() / 86400, 4)
    completion_planned_start = next((row.get("planned_start") for row in completion if row.get("planned_start")), None)
    completion_planned_end = next((row.get("planned_end") for row in reversed(completion) if row.get("planned_end")), None)
    planned_completion_days = None
    if completion_planned_start and completion_planned_end:
        planned_completion_days = round((completion_planned_end - completion_planned_start).total_seconds() / 86400, 4)
    return {
        "job_id": int(base.get("job_id") or 0),
        "job_sequence_no": int(base.get("job_sequence_no") or 0),
        "project_id": int(base.get("project_id") or 0),
        "project_name": _text(base.get("project_name")),
        "team_id": int(base.get("team_id") or 0) if base.get("team_id") is not None else None,
        "team_code": _text(base.get("team_name") or base.get("team_code")),
        "country_region": _text(base.get("country_region")),
        "team_company": _text(base.get("team_company")),
        "block_name": _text(base.get("block_name") or base.get("block_code")),
        "rig_model": _text(base.get("rig_model")),
        "well_id": int(base.get("well_id") or 0),
        "well_name": _text(base.get("well_name") or base.get("well_code")),
        "well_profile": _text(base.get("well_profile_name") or base.get("well_profile_code")),
        "drilling_start_date": _text(first_report.get("report_date") if first_report else "")[:10],
        "drilling_end_date": _text(last_report.get("report_date") if last_report else "")[:10],
        "completion_date": _text(max(completion, key=lambda row: (_text(row.get("report_date")), int(row.get("report_no") or 0))).get("report_date") if completion else "")[:10],
        "design_depth_ft": round(float(base["design_depth_ft"]), 2) if base.get("design_depth_ft") is not None else None,
        "current_depth_ft": round(float(current_depth_rows[-1]["measured_depth_ft"]), 2) if current_depth_rows else None,
        "month_progress_ft": round(month_progress, 2),
        "year_progress_ft": round(year_progress, 2),
        "planned_drilling_cycle_days": planned_drilling_days,
        "planned_completion_cycle_days": planned_completion_days,
        "actual_drilling_cycle_days": round(drilling_hours / 24, 4) if ordered else None,
        "actual_completion_cycle_days": round(completion_hours / 24, 4) if completion else None,
        "well_control_incident": "",
        "accident_waiting": "",
        "remarks": "",
        "drilling_report_count": len(ordered),
        "completion_report_count": len(completion),
    }


def load_workover_basic_monthly_report_rows(
    database_path: str | Path | None = None,
    *,
    report_date: str,
) -> dict[str, Any]:
    """Load Appendix 5 workover rows from the normalized monthly source view."""
    del database_path
    initialize_database()
    selected = date.fromisoformat(report_date)
    month_start = selected.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    current_month_start = date.today().replace(day=1)
    current_month_end = (current_month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT DATE_FORMAT(report_date, '%%Y-%%m') AS report_month
                FROM dpr_report
                WHERE report_type = 'workover'
                  AND report_date IS NOT NULL
                  AND report_date <= %s
                ORDER BY report_month DESC
                """,
                (current_month_end,),
            )
            available_months = [
                _text(row.get("report_month"))
                for row in (cursor.fetchall() or [])
                if _text(row.get("report_month"))
            ]
            cursor.execute(
                """
                SELECT DISTINCT job_id
                FROM vw_workover_basic_monthly_source
                WHERE report_date BETWEEN %s AND %s
                ORDER BY job_id
                """,
                (month_start, month_end),
            )
            job_ids = [int(row["job_id"]) for row in (cursor.fetchall() or []) if row.get("job_id") is not None]
            if not job_ids:
                return {
                    "report_date": report_date,
                    "month_start": month_start.isoformat(),
                    "month_end": month_end.isoformat(),
                    "available_months": available_months,
                    "rows": [],
                }
            placeholders = ",".join(["%s"] * len(job_ids))
            cursor.execute(
                f"""
                SELECT *
                FROM vw_workover_basic_monthly_source
                WHERE job_id IN ({placeholders})
                ORDER BY job_id,report_date,report_no,daily_report_id
                """,
                job_ids,
            )
            source_rows = [dict(row) for row in (cursor.fetchall() or [])]
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in source_rows:
        grouped.setdefault(int(row["job_id"]), []).append(row)
    result_rows = [_workover_basic_monthly_job_row(rows) for rows in grouped.values()]
    result_rows.sort(key=lambda row: (
        _text(row.get("team_code")),
        _text(row.get("well_name")),
        int(row.get("job_id") or 0),
    ))
    return {
        "report_date": report_date,
        "month_start": month_start.isoformat(),
        "month_end": month_end.isoformat(),
        "available_months": available_months,
        "rows": result_rows,
    }


def _workover_basic_monthly_job_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: (
        _text(row.get("report_date"))[:10],
        int(row.get("report_no") or 0),
        int(row.get("daily_report_id") or 0),
    ))
    if not ordered:
        raise ValueError("Monthly workover job requires at least one workover report")
    base = ordered[-1]
    numbered = [row for row in ordered if row.get("report_no") is not None]
    first_report = next((row for row in numbered if int(row.get("report_no") or 0) == 1), None)
    last_report = max(
        numbered,
        key=lambda row: (int(row.get("report_no") or 0), _text(row.get("report_date"))[:10]),
    ) if numbered else None
    translated_reason = next(
        (_text(row.get("primary_reason_translated")) for row in reversed(ordered) if _text(row.get("primary_reason_translated"))),
        "",
    )
    source_reason = next(
        (_text(row.get("primary_reason_source")) for row in reversed(ordered) if _text(row.get("primary_reason_source"))),
        "",
    )
    return {
        "job_id": int(base.get("job_id") or 0),
        "job_sequence_no": int(base.get("job_sequence_no") or 0),
        "project_id": int(base.get("project_id") or 0),
        "project_name": _text(base.get("project_name")),
        "team_id": int(base.get("team_id") or 0) if base.get("team_id") is not None else None,
        "team_code": _text(base.get("team_name") or base.get("team_code")),
        "country_region": _text(base.get("country_region")),
        "team_company": _text(base.get("team_company")),
        "block_name": _text(base.get("block_name") or base.get("block_code")),
        "rig_model": _text(base.get("rig_model")),
        "well_id": int(base.get("well_id") or 0),
        "well_name": _text(base.get("well_name") or base.get("well_code")),
        "well_profile": _text(base.get("well_profile_name") or base.get("well_profile_code")),
        "workover_start_date": _text(first_report.get("report_date") if first_report else "")[:10],
        "workover_end_date": _text(last_report.get("report_date") if last_report else "")[:10],
        "primary_operation": translated_reason,
        "primary_operation_source": source_reason,
        "primary_operation_zh": translated_reason,
        "well_control_incident": "",
        "accident_waiting": "",
        "remarks": "",
        "workover_report_count": len(ordered),
    }


def load_drilling_workover_efficiency_monthly_report_rows(
    database_path: str | Path | None = None,
    *,
    report_date: str,
) -> dict[str, Any]:
    """Load Appendix 6 monthly efficiency rows grouped by well and profession."""
    del database_path
    initialize_database()
    selected = date.fromisoformat(report_date)
    month_start = selected.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    current_month_start = date.today().replace(day=1)
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT DATE_FORMAT(report_date, '%%Y-%%m') AS report_month
                FROM dpr_report
                WHERE report_type IN ('drilling','completion','workover')
                  AND report_date IS NOT NULL
                  AND report_date < DATE_ADD(%s, INTERVAL 1 MONTH)
                ORDER BY report_month DESC
                """,
                (current_month_start,),
            )
            available_months = [
                _text(row.get("report_month"))
                for row in (cursor.fetchall() or [])
                if _text(row.get("report_month"))
            ]
            cursor.execute(
                """
                SELECT *
                FROM vw_drilling_workover_efficiency_monthly
                WHERE month_start = %s
                ORDER BY team_name,well_name,profession,project_id,well_id
                """,
                (month_start,),
            )
            source_rows = [dict(row) for row in (cursor.fetchall() or [])]
    rows = [_drilling_workover_efficiency_monthly_row(source) for source in source_rows]
    return {
        "report_date": report_date,
        "month_start": month_start.isoformat(),
        "month_end": month_end.isoformat(),
        "available_months": available_months,
        "rows": rows,
    }


def _drilling_workover_efficiency_monthly_row(source: dict[str, Any]) -> dict[str, Any]:
    production_hours = max(0.0, float(source.get("production_hours") or 0))
    npt_hours = max(0.0, float(source.get("npt_hours") or 0))
    allowance_hours = max(0.0, float(source.get("npt_allowance_hours") or 0))
    paid_repair_hours = min(npt_hours, allowance_hours)
    zero_rate_repair_hours = max(0.0, npt_hours - allowance_hours)
    accident_complex_hours = 0.0
    other_hours = 0.0
    denominator = production_hours + paid_repair_hours + zero_rate_repair_hours + accident_complex_hours + other_hours
    profession = _text(source.get("profession")).lower()
    return {
        "project_id": int(source.get("project_id") or 0),
        "project_name": _text(source.get("project_name")),
        "project_type": _text(source.get("project_type")),
        "well_id": int(source.get("well_id") or 0),
        "team_id": int(source.get("team_id") or 0),
        "well_name": _text(source.get("well_name") or source.get("well_code")),
        "profession": profession,
        "profession_label": "修井" if profession == "workover" else "钻井",
        "team_code": _text(source.get("team_name") or source.get("team_code")),
        "country_region": _text(source.get("country_region")),
        "team_company": _text(source.get("team_company")),
        "block_name": _text(source.get("block_name")),
        "rig_model": _text(source.get("rig_model")),
        "move_hours": round(max(0.0, float(source.get("move_hours") or 0)), 1),
        "production_hours": round(production_hours, 1),
        "npt_allowance_hours": round(allowance_hours, 1),
        "paid_repair_hours": round(paid_repair_hours, 1),
        "zero_rate_repair_hours": round(zero_rate_repair_hours, 1),
        "accident_complex_hours": accident_complex_hours,
        "other_hours": other_hours,
        "well_efficiency": round(production_hours / denominator, 6) if denominator else None,
        "nonproductive_description": "",
        "average_efficiency": None,
        "remarks": "",
        "report_count": int(source.get("report_count") or 0),
        "operation_count": int(source.get("operation_count") or 0),
        "npt_hours": round(npt_hours, 1),
    }


def load_monthly_team_workload_report_rows(
    database_path: str | Path | None = None,
    *,
    report_date: str,
) -> dict[str, Any]:
    """Load monthly workload rows grouped by project, standard team, and profession."""
    del database_path
    initialize_database()
    selected = date.fromisoformat(report_date)
    month_start = selected.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    current_month_start = date.today().replace(day=1)
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT DATE_FORMAT(report_date, '%%Y-%%m') AS report_month
                FROM dpr_report
                WHERE report_type IN ('drilling','completion','workover')
                  AND report_date IS NOT NULL
                  AND report_date < DATE_ADD(%s, INTERVAL 1 MONTH)
                ORDER BY report_month DESC
                """,
                (current_month_start,),
            )
            available_months = [
                _text(row.get("report_month"))
                for row in (cursor.fetchall() or [])
                if _text(row.get("report_month"))
            ]
            cursor.execute(
                """
                SELECT *
                FROM vw_monthly_team_workload
                WHERE month_start = %s
                ORDER BY profession,team_name,project_id
                """,
                (month_start,),
            )
            source_rows = [dict(row) for row in (cursor.fetchall() or [])]
    rows = [_monthly_team_workload_row(source) for source in source_rows]
    return {
        "report_date": report_date,
        "month_start": month_start.isoformat(),
        "month_end": month_end.isoformat(),
        "available_months": available_months,
        "rows": rows,
    }


def _monthly_team_workload_row(source: dict[str, Any]) -> dict[str, Any]:
    profession = _text(source.get("profession")).lower()
    team_name = _text(source.get("team_name") or source.get("team_code") or "未匹配队伍")
    operation_hours = max(0.0, float(source.get("operation_hours") or 0))
    move_hours = max(0.0, float(source.get("move_hours") or 0))
    manned_standby_hours = max(0.0, float(source.get("manned_standby_hours") or 0))
    unmanned_standby_hours = max(0.0, float(source.get("unmanned_standby_hours") or 0))
    force_majeure_hours = max(0.0, float(source.get("force_majeure_hours") or 0))
    zero_rate_repair_hours = max(0.0, float(source.get("zero_rate_repair_hours") or 0))
    total_hours = (
        operation_hours
        + move_hours
        + manned_standby_hours
        + unmanned_standby_hours
        + force_majeure_hours
        + zero_rate_repair_hours
    )
    return {
        "project_id": int(source.get("project_id") or 0),
        "project_name": _text(source.get("project_name")),
        "profession": profession,
        "team_id": int(source.get("team_id") or 0),
        "profession_label": "修井" if profession == "workover" else "钻井",
        "category_label": "修井" if profession == "workover" else "钻机",
        "team_code": team_name,
        "team_name": team_name,
        "operation_hours": round(operation_hours, 3),
        "move_hours": round(move_hours, 3),
        "manned_standby_hours": round(manned_standby_hours, 3),
        "unmanned_standby_hours": round(unmanned_standby_hours, 3),
        "force_majeure_hours": round(force_majeure_hours, 3),
        "zero_rate_repair_hours": round(zero_rate_repair_hours, 3),
        "total_hours": round(total_hours, 3),
        "remarks": "",
        "well_count": int(source.get("well_count") or 0),
        "report_count": int(source.get("report_count") or 0),
    }


def list_ai_job_status(kind: str) -> list[dict[str, str]]:
    if kind not in {"translation", "extraction"}:
        raise ValueError("Unsupported AI job kind")
    prefix = "translation" if kind == "translation" else "extraction"
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT record_id,
                       {prefix}_status AS status,
                       {prefix}_progress AS progress,
                       {prefix}_error AS error,
                       {prefix}_updated_at AS updated_at
                FROM dpr_report_record
                ORDER BY report_date DESC, updated_at DESC
                """
            )
            rows = cursor.fetchall()
    return [{key: _text(value) for key, value in row.items()} for row in rows]


def list_translation_queue_records() -> list[dict[str, str]]:
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT record_id, report_type, report_date AS reportDate, report_no AS reportNo,
                       wellbore, rig, translation_status, translation_progress,
                       translation_error, translation_version, translation_updated_at
                FROM dpr_report_record
                ORDER BY report_date DESC, updated_at DESC
                """
            )
            rows = cursor.fetchall()
    return [{key: _text(value) for key, value in row.items()} for row in rows]


def load_activity_classifications(record_ids: list[str]) -> dict[tuple[str, int], dict[str, Any]]:
    clean_ids = sorted({str(value or "").strip() for value in record_ids if str(value or "").strip()})
    if not clean_ids:
        return {}
    placeholders = ",".join(["%s"] * len(clean_ids))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT d.record_id,a.source_row_no,a.source_op_type,c.productive_flag,
                       c.confirmed_op_type,c.work_bucket,c.billing_status,c.responsibility,
                       c.cause_code,c.service_line,c.confirmation_status,c.rule_version,
                       c.confirmed_at,c.confirmed_by,c.version
                FROM dpr_report d
                JOIN dpr_operation a ON a.daily_report_id=d.id
                LEFT JOIN dpr_operation_classification c ON c.activity_id=a.id
                WHERE d.record_id IN ({placeholders})
                """,
                clean_ids,
            )
            rows = cursor.fetchall()
    return {
        (_text(row.get("record_id")), int(row.get("source_row_no", 0) or 0)): {
            key: _text(value) for key, value in row.items()
        }
        for row in rows
    }


def list_npt_confirmation_wells(
    database_path: str | Path | None,
    *,
    rig: str = "",
    wellbore: str = "",
    status: str = "",
    scope_rig: str = "",
) -> dict[str, Any]:
    del database_path
    records = _npt_candidate_records(rig=rig, wellbore=wellbore, scope_rig=scope_rig)
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        operations = record.pop("operations", [])
        has_non_p = any(_system_type(row) in {"SC", "NPT"} for row in operations)
        if not has_non_p:
            continue
        record_rig = str(record.get("rig", "") or "")
        record_well = str(record.get("wellbore", "") or "")
        if not record_well:
            continue
        key = (record_rig, record_well)
        item = groups.setdefault(key, {
            "rig": record_rig,
            "wellbore": record_well,
            "start_date": record.get("reportDate", ""),
            "end_date": record.get("reportDate", ""),
            "record_ids": [],
            "statuses": [],
            "locked_count": 0,
            "row_count": 0,
            "sc_hours": 0.0,
            "npt_hours": 0.0,
        })
        date_value = str(record.get("reportDate", "") or "")
        if date_value:
            item["start_date"] = min(str(item["start_date"] or date_value), date_value)
            item["end_date"] = max(str(item["end_date"] or date_value), date_value)
        item["record_ids"].append(str(record.get("record_id", "") or ""))
        if str(record.get("confirmation_status", "") or "").strip().lower() == "draft":
            item["statuses"].append("draft")
        if _truthy(record.get("locked")):
            item["locked_count"] += 1
        for row in operations:
            op_type = _system_type(row)
            hours = _safe_float(row.get("hours"))
            item["row_count"] += 1
            if op_type in {"SC", "NPT"}:
                item["statuses"].append(str(row.get("_review_status", "") or "PENDING"))
            if op_type == "SC":
                item["sc_hours"] += hours
            elif op_type == "NPT":
                item["npt_hours"] += hours
    items = []
    for item in groups.values():
        item_status = _confirmation_group_status(item)
        if status and item_status != status:
            continue
        items.append({
            "wellbore": item["wellbore"],
            "rig": item["rig"],
            "start_date": item["start_date"],
            "end_date": item["end_date"],
            "status": item_status,
            "record_count": len(item["record_ids"]),
            "row_count": item["row_count"],
            "sc_hours": round(float(item["sc_hours"]), 2),
            "npt_hours": round(float(item["npt_hours"]), 2),
        })
    items.sort(key=lambda row: (str(row["status"] != "pending"), str(row["end_date"])), reverse=False)
    rigs = sorted({str(record.get("rig", "") or "") for record in records if record.get("rig")})
    return {"items": items, "filters": {"rigs": rigs, "statuses": _npt_statuses()}}


def load_npt_confirmation_detail(
    database_path: str | Path | None,
    wellbore: str,
    *,
    rig: str = "",
    scope_rig: str = "",
) -> dict[str, Any]:
    del database_path
    records = _npt_candidate_records(rig=rig, wellbore=wellbore, scope_rig=scope_rig, exact_wellbore=True)
    if not records:
        raise KeyError(wellbore)
    relevant_records = [
        record for record in records
        if any(_system_type(row) in {"SC", "NPT"} for row in record.get("operations", []))
    ]
    if not relevant_records:
        raise KeyError(wellbore)
    rows: list[dict[str, Any]] = []
    for record in sorted(relevant_records, key=lambda item: str(item.get("reportDate", "") or "")):
        for row in record.get("operations", []):
            system_type = _system_type(row)
            fact = row.get("_fact_classification", {}) if isinstance(row.get("_fact_classification"), dict) else {}
            draft = row.get("draft_classification", {}) if isinstance(row.get("draft_classification"), dict) else {}
            confirmed_type = str(
                draft.get("confirmed_op_type", "")
                or fact.get("confirmed_op_type", "")
                or row.get("confirmed_op_type", "")
                or system_type
            ).strip().upper()
            rows.append({
                "record_id": record.get("record_id", ""),
                "report_type": record.get("report_type", ""),
                "reportDate": record.get("reportDate", ""),
                "row_no": row.get("row_no", ""),
                "from": row.get("from", ""),
                "to": row.get("to", ""),
                "hours": row.get("hours", ""),
                "op_code": row.get("op_code", ""),
                "op_sub": row.get("op_sub", ""),
                "operation_details": row.get("operation_details", ""),
                "system_op_type": system_type,
                "confirmed_op_type": str(row.get("draft_op_type", "") or confirmed_type).strip().upper(),
                "review_status": str(fact.get("confirmation_status", "") or ("AUTO_CONFIRMED" if system_type == "P" else "PENDING")),
                "work_bucket": str(draft.get("work_bucket", "") or fact.get("work_bucket", "") or row.get("work_bucket", "") or ""),
                "billing_status": str(draft.get("billing_status", "") or fact.get("billing_status", "") or row.get("billing_status", "") or ""),
                "responsibility": str(draft.get("responsibility", "") or fact.get("responsibility", "") or row.get("responsibility", "") or ""),
                "cause_code": str(draft.get("cause_code", "") or fact.get("cause_code", "") or row.get("cause_code", "") or ""),
                "service_line": str(draft.get("service_line", "") or fact.get("service_line", "") or row.get("service_line", "") or ""),
                "row_revision": _npt_row_revision(row),
            })
    dates = [str(record.get("reportDate", "") or "") for record in relevant_records if record.get("reportDate")]
    meta = {
        "wellbore": wellbore,
        "rig": rig or str(relevant_records[0].get("rig", "") or ""),
        "start_date": min(dates) if dates else "",
        "end_date": max(dates) if dates else "",
        "status": _confirmation_group_status({
            "record_ids": [record.get("record_id", "") for record in relevant_records],
            "statuses": [
                *["draft" for record in relevant_records if str(record.get("confirmation_status", "") or "").lower() == "draft"],
                *[
                    str(row.get("_review_status", "") or "PENDING")
                    for record in relevant_records
                    for row in record.get("operations", [])
                    if _system_type(row) in {"SC", "NPT"}
                ],
            ],
            "locked_count": sum(1 for record in relevant_records if _truthy(record.get("locked"))),
        }),
        "record_count": len(relevant_records),
        "locked": all(_truthy(record.get("locked")) for record in relevant_records),
        "confirmation_note": next((str(record.get("confirmation_note", "") or "") for record in relevant_records if record.get("confirmation_note")), ""),
    }
    return {"meta": meta, "operations": rows}


def save_npt_confirmation(
    database_path: str | Path | None,
    wellbore: str,
    operations: list[dict[str, Any]],
    *,
    rig: str = "",
    note: str = "",
    confirmed_by: str = "",
    submit: bool = False,
) -> dict[str, Any]:
    del database_path
    detail = load_npt_confirmation_detail(None, wellbore, rig=rig)
    if detail["meta"].get("locked"):
        raise PermissionError(f"Well is locked after NPT confirmation: {wellbore}")
    candidate_rows = [row for row in detail["operations"] if str(row.get("system_op_type", "") or "").upper() in {"SC", "NPT"}]
    allowed_record_ids = {str(row.get("record_id", "") or "") for row in candidate_rows}
    candidate_keys = {(str(row.get("record_id", "") or ""), int(str(row.get("row_no", "") or "0"))) for row in candidate_rows}
    reference_codes = _npt_reference_code_sets()
    updates: dict[tuple[str, int], dict[str, str]] = {}
    revisions: dict[tuple[str, int], str] = {}
    for row in operations:
        record_id = str(row.get("record_id", "") or "")
        if record_id not in allowed_record_ids:
            continue
        try:
            row_no = int(str(row.get("row_no", "") or "0"))
        except ValueError:
            row_no = 0
        confirmed_type = str(row.get("confirmed_op_type", "") or "").strip().upper()
        key = (record_id, row_no)
        if confirmed_type in {"P", "SC", "NPT"} and row_no > 0 and key in candidate_keys:
            classification = {
                "confirmed_op_type": confirmed_type,
                "productive_flag": "PRODUCTION" if confirmed_type == "P" else "NON_PRODUCTION",
                "work_bucket": str(row.get("work_bucket", "") or "").strip(),
                "billing_status": str(row.get("billing_status", "") or "").strip(),
                "responsibility": str(row.get("responsibility", "") or "").strip(),
                "cause_code": str(row.get("cause_code", "") or "").strip(),
                "service_line": str(row.get("service_line", "") or "").strip(),
            }
            if confirmed_type == "P":
                classification.update({
                    "work_bucket": "OPERATION", "billing_status": "FULL_RATE",
                    "responsibility": "", "cause_code": "",
                })
            elif submit:
                if classification["work_bucket"] not in reference_codes["WORK_BUCKET"]:
                    raise ValueError(f"第 {row_no} 行必须选择工作量归类（含有/无人待工）。")
                if classification["responsibility"] not in reference_codes["RESPONSIBILITY"]:
                    raise ValueError(f"第 {row_no} 行必须选择责任方。")
                if classification["billing_status"] and classification["billing_status"] not in reference_codes["BILLING_STATUS"]:
                    raise ValueError(f"第 {row_no} 行计费状态不是当前启用的附录值。")
                if classification["cause_code"] and classification["cause_code"] not in reference_codes["CAUSE_CODE"]:
                    raise ValueError(f"第 {row_no} 行原因编码不是当前启用的附录值。")
            updates[key] = classification
            revisions[(record_id, row_no)] = str(row.get("row_revision", "") or "")
    if not updates:
        raise ValueError("No valid NPT confirmation rows.")
    if submit and set(updates) != candidate_keys:
        raise ValueError("提交前必须完成该井全部 SC/NPT 时段的复核。")
    touched_ids: set[str] = set()
    now = _now()
    with _connect() as connection:
        with connection.cursor() as cursor:
            record_ids = sorted(allowed_record_ids)
            placeholders = ",".join(["%s"] * len(record_ids))
            cursor.execute(
                f"SELECT record_id, locked FROM dpr_report_record WHERE record_id IN ({placeholders}) FOR UPDATE",
                record_ids,
            )
            locked_records = [
                _text(row.get("record_id"))
                for row in cursor.fetchall()
                if _truthy(row.get("locked"))
            ]
            if locked_records:
                raise PermissionError(f"Report is locked after NPT confirmation: {locked_records[0]}")
            for (record_id, row_no), classification in updates.items():
                cursor.execute(
                    """
                    SELECT row_json
                    FROM dpr_report_row
                    WHERE record_id=%s AND module_name='operations' AND row_no=%s
                    """,
                    (record_id, row_no),
                )
                row = cursor.fetchone()
                if not row:
                    continue
                row_json = _json_loads(row.get("row_json"), {})
                expected_revision = revisions.get((record_id, row_no), "")
                if expected_revision and expected_revision != _npt_row_revision(row_json):
                    raise RuntimeError("NPT operation changed after it was loaded; refresh and try again.")
                current_type = str(row_json.get("op_type", "") or "").strip().upper()
                row_json.setdefault("system_op_type", current_type)
                if submit:
                    row_json.update({key: value for key, value in classification.items() if key != "productive_flag"})
                    row_json["confirmed_classification"] = classification
                    row_json.pop("draft_op_type", None)
                    row_json.pop("draft_classification", None)
                else:
                    row_json["draft_op_type"] = classification["confirmed_op_type"]
                    row_json["draft_classification"] = classification
                cursor.execute(
                    """
                    UPDATE dpr_report_row
                    SET row_json=%s
                    WHERE record_id=%s AND module_name='operations' AND row_no=%s
                    """,
                    (_json_dumps(row_json), record_id, row_no),
                )
                if submit:
                    _sync_npt_type_fact(
                        cursor,
                        record_id=record_id,
                        row_no=row_no,
                        classification=classification,
                        actor=_text(confirmed_by) or "system",
                        note=_text(note),
                    )
                else:
                    _mark_npt_fact_draft(cursor, record_id=record_id, row_no=row_no, actor=_text(confirmed_by) or "system")
                touched_ids.add(record_id)
            for record_id in allowed_record_ids:
                if submit:
                    cursor.execute(
                        """
                        UPDATE dpr_report_record
                        SET confirmation_status='confirmed', confirmation_note=%s, updated_at=%s,
                            locked='yes', confirmed_at=%s, confirmed_by=%s
                        WHERE record_id=%s
                        """,
                        (_text(note), now, now, _text(confirmed_by), record_id),
                    )
                    _resolve_classification_pending_issue(
                        cursor,
                        record_id=record_id,
                        actor=_text(confirmed_by) or "system",
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE dpr_report_record
                        SET confirmation_status='draft', confirmation_note=%s, updated_at=%s
                        WHERE record_id=%s
                        """,
                        (_text(note), now, record_id),
                    )
        connection.commit()
    return {"wellbore": wellbore, "updated_records": len(touched_ids), "status": "confirmed" if submit else "draft", "locked": submit, "updated_at": now}


def _resolve_classification_pending_issue(cursor: Any, *, record_id: str, actor: str) -> bool:
    """Close a report-level pending issue only when every operation is statistics-ready."""
    cursor.execute(
        "SELECT COUNT(*) count FROM dpr_operation_classification c "
        "JOIN dpr_operation a ON a.id=c.activity_id "
        "JOIN dpr_report d ON d.id=a.daily_report_id "
        "WHERE d.record_id=%s AND c.confirmation_status NOT IN ('CONFIRMED','AUTO_CONFIRMED')",
        (record_id,),
    )
    pending_count = int((cursor.fetchone() or {}).get("count", 0) or 0)
    if pending_count:
        return False
    cursor.execute(
        "UPDATE dq_issue SET status='RESOLVED',resolution_note='全部活动已确认',"
        "resolved_at=NOW(),resolved_by=%s,updated_by=%s,version=version+1 "
        "WHERE issue_key=%s AND status='OPEN'",
        (actor, actor, f"{record_id}:CLASSIFICATION_PENDING"),
    )
    return True


def _sync_npt_type_fact(
    cursor: Any,
    *,
    record_id: str,
    row_no: int,
    classification: dict[str, str],
    actor: str,
    note: str,
) -> None:
    cursor.execute(
        "SELECT c.*,a.id activity_id FROM dpr_report d "
        "JOIN dpr_operation a ON a.daily_report_id=d.id AND a.source_row_no=%s "
        "LEFT JOIN dpr_operation_classification c ON c.activity_id=a.id WHERE d.record_id=%s",
        (row_no, record_id),
    )
    previous = cursor.fetchone()
    if not previous or not previous.get("activity_id"):
        return
    activity_id = int(previous["activity_id"])
    revised = dict(classification)
    cursor.execute(
        "INSERT INTO dpr_operation_classification_revision "
        "(activity_id,previous_json,revised_json,revision_type,reason,created_by) "
        "VALUES (%s,%s,%s,'npt_confirmation',%s,%s)",
        (activity_id, _json_dumps(previous), _json_dumps(revised), note or "NPT确认模块人工确认", actor),
    )
    cursor.execute(
        "UPDATE dpr_operation_classification SET confirmed_op_type=%s,productive_flag=%s,work_bucket=%s,"
        "billing_status=%s,responsibility=%s,cause_code=%s,service_line=%s,confirmation_status='CONFIRMED',"
        "confirmed_at=NOW(),confirmed_by=%s,change_reason=%s,updated_by=%s,version=version+1 "
        "WHERE activity_id=%s",
        (
            revised["confirmed_op_type"], revised["productive_flag"], revised["work_bucket"],
            revised["billing_status"], revised["responsibility"], revised["cause_code"], revised["service_line"],
            actor, note or "NPT确认模块人工确认", actor, activity_id,
        ),
    )


def _mark_npt_fact_draft(cursor: Any, *, record_id: str, row_no: int, actor: str) -> None:
    cursor.execute(
        "UPDATE dpr_operation_classification c "
        "JOIN dpr_operation a ON a.id=c.activity_id "
        "JOIN dpr_report d ON d.id=a.daily_report_id "
        "SET c.confirmation_status='DRAFT',c.updated_by=%s,c.version=c.version+1 "
        "WHERE d.record_id=%s AND a.source_row_no=%s AND a.source_op_type IN ('SC','NPT') "
        "AND c.confirmation_status<>'CONFIRMED'",
        (actor, record_id, row_no),
    )


def _npt_reference_code_sets() -> dict[str, set[str]]:
    categories = ("WORK_BUCKET", "RESPONSIBILITY", "BILLING_STATUS", "CAUSE_CODE")
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT category.category_code,value.value_code FROM md_appendix_value value "
                "JOIN md_appendix_category category ON category.id=value.category_id "
                "WHERE category.category_code IN (%s,%s,%s,%s) "
                "AND category.status='active' AND value.status='active'",
                categories,
            )
            rows = cursor.fetchall()
    result = {category: set() for category in categories}
    for row in rows:
        category = _text(row.get("category_code"))
        if category in result:
            result[category].add(_text(row.get("value_code")))
    return result


def is_available() -> bool:
    try:
        with _connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        return True
    except Exception:
        return False


def _connect(*, use_database: bool = True):
    settings = mysql_settings()
    if not settings.enabled:
        raise RuntimeError("MySQL storage is disabled.")
    if not settings.password:
        raise RuntimeError("MYSQL_PASSWORD is empty. Copy .env.example to .env and set a password.")
    try:
        import pymysql
    except ImportError as exc:
        raise RuntimeError("PyMySQL is not installed. Run: pip install -r requirements.txt") from exc
    return pymysql.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password,
        database=settings.database if use_database else None,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        connect_timeout=settings.connect_timeout,
    )


def _upsert_record(cursor: Any, record: dict[str, str]) -> None:
    columns = [
        "record_id",
        "report_type",
        "source_file",
        "parser",
        "source_page_start",
        "source_page_end",
        "source_report_index",
        "source_report_count",
        "batch_inherited_fields",
        "report_date",
        "report_no",
        "wellbore",
        "rig",
        "status",
        "source_language",
        "translation_status",
        "translation_progress",
        "translation_error",
        "translation_version",
        "translation_updated_at",
        "extraction_status", "extraction_progress", "extraction_error", "extraction_version", "extraction_updated_at",
        "validation_status",
        "validation_warnings",
        "locked",
        "confirmation_status",
        "confirmed_at",
        "confirmed_by",
        "confirmation_note",
        "created_at",
        "updated_at",
    ]
    placeholders = ", ".join(["%s"] * len(columns))
    immutable_after_insert = {
        "record_id",
        "locked",
        "confirmation_status",
        "confirmed_at",
        "confirmed_by",
        "confirmation_note",
    }
    update_clause = ", ".join(
        f"{column}=VALUES({column})"
        for column in columns
        if column not in immutable_after_insert
    )
    cursor.execute(
        f"""
        INSERT INTO dpr_report_record ({", ".join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
        """,
        [record.get(column, "") for column in columns],
    )


def _record_from_payload(
    record_id: str,
    report_type: str,
    source_file: str,
    fields: dict[str, Any],
    metadata: dict[str, Any],
    created_at: str,
    updated_at: str,
) -> dict[str, Any]:
    values = {
        "record_id": record_id,
        "report_type": report_type,
        "source_file": source_file,
        "parser": metadata.get("parser", ""),
        "source_page_start": metadata.get("source_page_start", ""),
        "source_page_end": metadata.get("source_page_end", ""),
        "source_report_index": metadata.get("source_report_index", ""),
        "source_report_count": metadata.get("source_report_count", ""),
        "batch_inherited_fields": ",".join(
            str(value) for value in metadata.get("batch_inherited_fields", []) if value
        ),
        "reportDate": fields.get("reportDate", ""),
        "reportNo": fields.get("reportNo", ""),
        "wellbore": fields.get("wellbore", ""),
        "rig": fields.get("rig", ""),
        "status": metadata.get("status", "parsed"),
        "source_language": metadata.get("source_language", ""),
        "translation_status": metadata.get("translation_status", ""),
        "translation_progress": metadata.get("translation_progress", ""),
        "translation_error": metadata.get("translation_error", ""),
        "translation_version": metadata.get("translation_version", ""),
        "translation_updated_at": metadata.get("translation_updated_at", ""),
        "extraction_status": metadata.get("extraction_status", ""),
        "extraction_progress": metadata.get("extraction_progress", ""),
        "extraction_error": metadata.get("extraction_error", ""),
        "extraction_version": metadata.get("extraction_version", ""),
        "extraction_updated_at": metadata.get("extraction_updated_at", ""),
        "validation_status": metadata.get("validation_status", "ok"),
        "validation_warnings": metadata.get("validation_warnings", ""),
        "locked": metadata.get("locked", ""),
        "confirmation_status": metadata.get("confirmation_status", ""),
        "confirmed_at": metadata.get("confirmed_at", ""),
        "confirmed_by": metadata.get("confirmed_by", ""),
        "confirmation_note": metadata.get("confirmation_note", ""),
        "created_at": created_at,
        "updated_at": updated_at,
    }
    record: dict[str, Any] = {
        MYSQL_RECORD_COLUMNS.get(key, key): _text(value)
        for key, value in values.items()
    }
    for field in ("source_page_start", "source_page_end", "source_report_index", "source_report_count"):
        record[field] = _positive_int(metadata.get(field))
    return record


def _record_id_for_business_identity(
    cursor: Any,
    report_type: str,
    fields: dict[str, Any],
) -> str:
    report_date = _text(fields.get("reportDate")).strip()
    report_no = _text(fields.get("reportNo")).strip()
    wellbore = _text(fields.get("wellbore")).strip()
    if not report_date or not report_no or not wellbore:
        return ""
    cursor.execute(
        "SELECT record_id FROM dpr_report_record "
        "WHERE report_type=%s AND report_date=%s AND report_no=%s AND wellbore=%s "
        "LIMIT 1 FOR UPDATE",
        (report_type, report_date, report_no, wellbore),
    )
    return _text((cursor.fetchone() or {}).get("record_id"))


def _record_to_public(row: dict[str, Any]) -> dict[str, str]:
    fields = _json_loads(row.get("fields_json"), {})
    return {
        "record_id": _text(row.get("record_id")),
        "report_type": _text(row.get("report_type")),
        "source_file": _text(row.get("source_file")),
        "parser": _text(row.get("parser")),
        "source_page_start": _text(row.get("source_page_start")),
        "source_page_end": _text(row.get("source_page_end")),
        "source_report_index": _text(row.get("source_report_index")),
        "source_report_count": _text(row.get("source_report_count")),
        "batch_inherited_fields": _text(row.get("batch_inherited_fields")),
        "reportDate": _text(row.get("report_date")),
        "reportNo": _text(row.get("report_no")),
        "wellbore": _text(row.get("wellbore")),
        "rig": _text(row.get("rig")),
        "rig_id": _text(row.get("rig_id")),
        "well_id": _text(row.get("well_id")),
        "project_id": _text(row.get("project_id")),
        "job_id": _text(row.get("job_id")),
        "master_match_status": _text(row.get("master_match_status")),
        "master_match_message": _text(row.get("master_match_message")),
        "status": _text(row.get("status")),
        "source_language": _text(row.get("source_language")),
        "translation_status": _text(row.get("translation_status")),
        "translation_progress": _text(row.get("translation_progress")),
        "translation_error": _text(row.get("translation_error")),
        "translation_version": _text(row.get("translation_version")),
        "translation_updated_at": _text(row.get("translation_updated_at")),
        "extraction_status": _text(row.get("extraction_status")),
        "extraction_progress": _text(row.get("extraction_progress")),
        "extraction_error": _text(row.get("extraction_error")),
        "extraction_version": _text(row.get("extraction_version")),
        "extraction_updated_at": _text(row.get("extraction_updated_at")),
        "validation_status": _text(row.get("validation_status")),
        "validation_warnings": _text(row.get("validation_warnings")),
        "locked": _text(row.get("locked")),
        "confirmation_status": _text(row.get("confirmation_status")),
        "confirmed_at": _text(row.get("confirmed_at")),
        "confirmed_by": _text(row.get("confirmed_by")),
        "confirmation_note": _text(row.get("confirmation_note")),
        "created_at": _text(row.get("created_at")),
        "updated_at": _text(row.get("updated_at")),
        "afeNumber": _text(fields.get("afeNumber")),
        "event": _text(fields.get("event")),
        "p_hours": _text(row.get("p_hours")),
        "sc_hours": _text(row.get("sc_hours")),
        "npt_hours": _text(row.get("npt_hours")),
    }


def _payload_metadata(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": _text(row.get("record_id")),
        "report_type": _text(row.get("report_type")),
        "source_file": _text(row.get("source_file")),
        "parser": _text(row.get("parser")),
        "source_page_start": _text(row.get("source_page_start")),
        "source_page_end": _text(row.get("source_page_end")),
        "source_report_index": _text(row.get("source_report_index")),
        "source_report_count": _text(row.get("source_report_count")),
        "batch_inherited_fields": [
            value for value in _text(row.get("batch_inherited_fields")).split(",") if value
        ],
        "rig_id": _text(row.get("rig_id")),
        "well_id": _text(row.get("well_id")),
        "project_id": _text(row.get("project_id")),
        "job_id": _text(row.get("job_id")),
        "master_match_status": _text(row.get("master_match_status")),
        "master_match_message": _text(row.get("master_match_message")),
        "source_language": _text(row.get("source_language")),
        "translation_status": _text(row.get("translation_status")),
        "translation_progress": _text(row.get("translation_progress")),
        "translation_error": _text(row.get("translation_error")),
        "translation_version": _text(row.get("translation_version")),
        "translation_updated_at": _text(row.get("translation_updated_at")),
        "extraction_status": _text(row.get("extraction_status")),
        "extraction_progress": _text(row.get("extraction_progress")),
        "extraction_error": _text(row.get("extraction_error")),
        "extraction_version": _text(row.get("extraction_version")),
        "extraction_updated_at": _text(row.get("extraction_updated_at")),
        "locked": _text(row.get("locked")),
        "confirmation_status": _text(row.get("confirmation_status")),
        "confirmed_at": _text(row.get("confirmed_at")),
        "confirmed_by": _text(row.get("confirmed_by")),
        "confirmation_note": _text(row.get("confirmation_note")),
    }


def _npt_candidate_records(
    *,
    rig: str = "",
    wellbore: str = "",
    scope_rig: str = "",
    exact_wellbore: bool = False,
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    args: list[object] = []
    if scope_rig:
        clauses.append("r.rig=%s")
        args.append(scope_rig)
    if rig:
        clauses.append("r.rig=%s")
        args.append(rig)
    if wellbore:
        if exact_wellbore:
            clauses.append("r.wellbore=%s")
            args.append(wellbore)
        else:
            clauses.append("LOWER(r.wellbore) LIKE %s")
            args.append(f"%{wellbore.lower()}%")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
        SELECT
          r.record_id, r.report_type, r.report_date, r.wellbore, r.rig, r.locked,
          r.confirmation_status, r.confirmation_note, rr.row_no, rr.row_json,
          c.productive_flag AS fact_productive_flag,
          c.confirmed_op_type AS fact_confirmed_op_type,
          c.work_bucket AS fact_work_bucket,
          c.billing_status AS fact_billing_status,
          c.responsibility AS fact_responsibility,
          c.cause_code AS fact_cause_code,
          c.service_line AS fact_service_line,
          c.confirmation_status AS fact_confirmation_status,
          c.version AS fact_version
        FROM dpr_report_record r
        LEFT JOIN dpr_report_row rr
          ON rr.record_id = r.record_id AND rr.module_name = 'operations'
        LEFT JOIN dpr_report d ON d.record_id=r.record_id
        LEFT JOIN dpr_operation a ON a.daily_report_id=d.id AND a.source_row_no=rr.row_no
        LEFT JOIN dpr_operation_classification c ON c.activity_id=a.id
        {where_sql}
        ORDER BY r.report_date, r.record_id, rr.row_no
    """
    grouped: dict[str, dict[str, Any]] = {}
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
    for row in rows:
        record_id = _text(row.get("record_id"))
        if not record_id:
            continue
        record = grouped.setdefault(record_id, {
            "record_id": record_id,
            "report_type": _text(row.get("report_type")),
            "reportDate": _text(row.get("report_date")),
            "wellbore": _text(row.get("wellbore")),
            "rig": _text(row.get("rig")),
            "locked": _text(row.get("locked")),
            "confirmation_status": _text(row.get("confirmation_status")),
            "confirmation_note": _text(row.get("confirmation_note")),
            "operations": [],
        })
        row_json = _json_loads(row.get("row_json"), {})
        if not row_json:
            continue
        row_json["row_no"] = _text(row.get("row_no"))
        row_json["_fact_classification"] = {
            "productive_flag": _text(row.get("fact_productive_flag")),
            "confirmed_op_type": _text(row.get("fact_confirmed_op_type")),
            "work_bucket": _text(row.get("fact_work_bucket")),
            "billing_status": _text(row.get("fact_billing_status")),
            "responsibility": _text(row.get("fact_responsibility")),
            "cause_code": _text(row.get("fact_cause_code")),
            "service_line": _text(row.get("fact_service_line")),
            "confirmation_status": _text(row.get("fact_confirmation_status")),
            "version": _text(row.get("fact_version")),
        }
        row_json["_review_status"] = _text(row.get("fact_confirmation_status"))
        record["operations"].append(row_json)
    return list(grouped.values())


def _npt_row_revision(row: dict[str, Any]) -> str:
    persisted = {key: value for key, value in row.items() if key != "row_no" and not key.startswith("_")}
    value = json.dumps(persisted, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _operation_hour_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for row in rows:
        record_id = _text(row.get("record_id"))
        if not record_id:
            continue
        values = stats.setdefault(record_id, {"p_hours": 0.0, "sc_hours": 0.0, "npt_hours": 0.0})
        operation = _json_loads(row.get("row_json"), {})
        op_type = str(operation.get("confirmed_op_type", "") or operation.get("op_type", "") or operation.get("system_op_type", "")).strip().upper()
        key = {"P": "p_hours", "SC": "sc_hours", "NPT": "npt_hours"}.get(op_type)
        if key:
            values[key] += _safe_float(operation.get("hours"))
    return {
        record_id: {key: round(value, 2) for key, value in values.items()}
        for record_id, values in stats.items()
    }


def _system_type(row: dict[str, Any]) -> str:
    return str(row.get("system_op_type", "") or row.get("op_type", "") or "").strip().upper()


def _sql_statements(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [statement.strip() for statement in text.split(";") if statement.strip()]


def _server_scope_statement(statement: str) -> bool:
    normalized = " ".join(statement.strip().lower().split())
    return normalized.startswith("create database ") or normalized.startswith("use ")


def _json_dumps(value: Any) -> str:
    return json.dumps(_json_safe(value), ensure_ascii=False)


def _json_loads(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value or ""))
    except json.JSONDecodeError:
        return default


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if value is None:
        return ""
    return str(value)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "locked", "confirmed"}


def _positive_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _translation_source_hash(value: Any) -> str:
    normalized = normalize_multiline(value)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _generated_record_id(report_type: str) -> str:
    return f"{report_type}:{_slug(_now())}"
