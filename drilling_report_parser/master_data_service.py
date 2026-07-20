"""Master-data CRUD, effective-dated assignments, and report identity resolution."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any


MASTER_ENTITIES: dict[str, dict[str, object]] = {
    "regions": {
        "table": "md_geo_region", "code": "region_code", "name": "region_name",
        "alias_types": ("region",),
        "fields": ("region_code", "region_name", "region_type_code", "iso_alpha2", "parent_id", "status", "change_reason"),
    },
    "companies": {
        "table": "md_organization", "code": "organization_code", "name": "organization_name",
        "alias_types": ("company", "organization"),
        "fields": ("organization_code", "organization_name", "legal_name", "organization_type", "country_region_id", "parent_id", "status", "change_reason"),
    },
    "fields": {
        "table": "md_field", "code": "field_code", "name": "field_name",
        "alias_types": ("field",),
        "fields": ("field_code", "field_name", "region_id", "operator_company_id", "field_type_code", "lifecycle_status_code", "status", "change_reason"),
    },
    "organizations": {
        "table": "md_organization",
        "code": "organization_code",
        "name": "organization_name",
        "fields": ("organization_code", "organization_name", "organization_type", "parent_id", "status", "change_reason"),
    },
    "blocks": {
        "table": "md_block",
        "code": "block_code",
        "name": "block_name",
        "alias_types": ("block",),
        "fields": ("block_code", "block_name", "field_id", "region_id", "operator_company_id", "block_type_code", "parent_id", "status", "change_reason"),
    },
    "rig-models": {
        "table": "md_rig_model",
        "code": "model_code",
        "name": "model_name",
        "fields": ("model_code", "model_name", "equipment_type", "specification_json", "status", "change_reason"),
    },
    "rigs": {
        "table": "md_rig",
        "code": "rig_code",
        "name": "rig_name",
        "fields": ("rig_code", "rig_name", "rig_model_id", "owner_organization_id", "rig_type", "team_id", "manufacturer", "model_code", "drive_type_code", "rated_power_hp", "rated_depth_m", "equipment_status_code", "status", "change_reason"),
    },
    "teams": {
        "table": "md_team", "code": "team_code", "name": "team_name",
        "alias_types": ("team",),
        "fields": ("team_code", "team_name", "team_type_code", "company_id", "model_code", "status", "change_reason"),
    },
    "drilling-rigs": {
        "table": "md_rig", "code": "rig_code", "name": "rig_name", "where": "rig_type='drilling'", "fixed": {"rig_type": "drilling"},
        "fields": ("rig_code", "rig_name", "team_id", "owner_organization_id", "manufacturer", "model_code", "drive_type_code", "rated_depth_m", "equipment_status_code", "status", "change_reason"),
    },
    "workover-rigs": {
        "table": "md_rig", "code": "rig_code", "name": "rig_name", "where": "rig_type='workover'", "fixed": {"rig_type": "workover"},
        "fields": ("rig_code", "rig_name", "team_id", "owner_organization_id", "manufacturer", "model_code", "rated_power_hp", "drive_type_code", "equipment_status_code", "status", "change_reason"),
    },
    "wells": {
        "table": "md_well",
        "code": "well_code",
        "name": "well_name",
        "alias_types": ("well",),
        "fields": ("well_code", "well_name", "field_id", "block_id", "operator_company_id", "well_type_code", "surface_latitude", "surface_longitude", "well_profile_code", "trajectory_status_code", "kickoff_md_m", "planned_td_md_m", "lifecycle_status_code", "status", "change_reason"),
    },
    "contracts": {
        "table": "md_contract",
        "code": "contract_no",
        "name": "contract_name",
        "fields": ("contract_no", "contract_name", "customer_organization_id", "valid_from", "valid_to", "status", "change_reason"),
    },
    "projects": {
        "table": "md_project",
        "code": "project_code",
        "name": "project_name",
        "fields": ("project_code", "project_name", "contract_id", "service_scope", "valid_from", "valid_to", "status", "change_reason"),
    },
    "aliases": {
        "table": "md_alias",
        "code": "normalized_alias",
        "name": "alias_value",
        "fields": ("entity_type", "source_system", "alias_value", "normalized_alias", "entity_id", "confirmation_status", "status", "change_reason"),
    },
    "appendix-categories": {
        "table": "md_appendix_category", "code": "category_code", "name": "category_name",
        "fields": ("category_code", "category_name", "parent_id", "level_no", "description", "status", "change_reason"),
    },
    "appendix-values": {
        "table": "md_appendix_value", "code": "value_code", "name": "value_name",
        "order_by": "sort_order, value_code",
        "fields": ("category_id", "value_code", "value_name", "parent_value_id", "level_no", "sort_order", "display_color", "description", "status", "change_reason"),
    },
}

ASSIGNMENT_ENTITIES: dict[str, dict[str, object]] = {
    "project-team": {
        "table": "rel_project_team_assignment",
        "fields": ("project_id", "team_id", "valid_from", "valid_to", "service_discipline", "assignment_note", "priority", "status", "change_reason"),
        "overlap": ("team_id",),
        "required": ("project_id", "team_id"),
    },
    "project-well": {
        "table": "rel_project_well_scope",
        "fields": ("project_id", "well_id", "job_type", "scope_note", "valid_from", "valid_to", "status", "change_reason"),
        "overlap": ("well_id", "job_type"),
        "required": ("project_id", "well_id"),
    },
    "job-rig": {
        "table": "rel_job_rig_assignment",
        "fields": ("job_id", "rig_id", "valid_from", "valid_to", "status", "change_reason"),
        "overlap": ("rig_id",),
        "required": ("job_id", "rig_id"),
    },
}


REFERENCE_TABLE_LABELS = {
    "md_geo_region": "国家/区域",
    "md_organization": "公司",
    "md_field": "油田",
    "md_block": "区块",
    "md_team": "队伍",
    "md_rig": "历史设备",
    "md_well": "井",
    "md_appendix_category": "附录类别",
    "md_appendix_value": "附录值",
    "md_contract": "合同",
    "md_project": "项目",
    "rel_project_team_assignment": "项目队伍关系",
    "rel_project_well_scope": "项目井范围",
    "biz_job": "作业实例",
    "rel_job_rig_assignment": "作业设备关系",
    "dpr_report": "标准日报",
    "dpr_report_record": "原始日报",
    "md_alias": "别名",
}

LOGICAL_MASTER_REFERENCES = {
    "wells": (("dpr_report_record", "well_id"),),
}

APPENDIX_CODE_REFERENCES = {
    "REGION_TYPE": (("md_geo_region", "region_type_code"),),
    "COMPANY_TYPE": (("md_organization", "organization_type"),),
    "FIELD_TYPE": (("md_field", "field_type_code"),),
    "FIELD_STATUS": (("md_field", "lifecycle_status_code"),),
    "BLOCK_TYPE": (("md_block", "block_type_code"),),
    "TEAM_TYPE": (("md_team", "team_type_code"),),
    "RIG_TYPE": (("md_team", "model_code"), ("md_rig", "model_code")),
    "RIG_DRIVE_TYPE": (("md_rig", "drive_type_code"),),
    "EQUIPMENT_STATUS": (("md_rig", "equipment_status_code"),),
    "WELL_TYPE": (("md_well", "well_type_code"),),
    "WELL_STATUS": (("md_well", "lifecycle_status_code"),),
    "WELL_PROFILE": (("md_well", "well_profile_code"),),
    "TRAJECTORY_STATUS": (("md_well", "trajectory_status_code"),),
}


def normalize_alias(entity_type: str, value: object) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip().upper()
    if entity_type == "rig":
        text = re.sub(r"^00\s+", "", text)
        match = re.fullmatch(r"(?:SINOPEC|RIG|SP|W)?[-\s]*(\d{2,4})", text)
        if match:
            return f"SINOPEC {match.group(1)}"
    return text


def list_master_entities(entity: str, *, query: str = "", status: str = "", limit: int = 500) -> list[dict[str, Any]]:
    config = _master_config(entity)
    clauses: list[str] = [str(config["where"])] if config.get("where") else []
    args: list[object] = []
    if status:
        clauses.append("status=%s")
        args.append(status)
    if query:
        clauses.append(f"({config['code']} LIKE %s OR {config['name']} LIKE %s)")
        args.extend([f"%{query}%", f"%{query}%"])
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    order_by = str(config.get("order_by") or config["code"])
    sql = f"SELECT * FROM {config['table']} {where} ORDER BY status, {order_by} LIMIT %s"
    args.append(max(1, min(int(limit), 2000)))
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
    return [_json_row(row) for row in rows]


def list_appendix_values(category_code: str) -> list[dict[str, Any]]:
    normalized_code = str(category_code or "").strip().upper()
    if not normalized_code:
        raise ValueError("缺少附录类别编码。")
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT appendix_value.value_code,appendix_value.value_name,appendix_value.level_no,appendix_value.sort_order,"
                "appendix_value.display_color,appendix_value.description "
                "FROM md_appendix_value appendix_value "
                "JOIN md_appendix_category category ON category.id=appendix_value.category_id "
                "WHERE category.category_code=%s AND category.status='active' AND appendix_value.status='active' "
                "ORDER BY appendix_value.sort_order,appendix_value.value_code",
                (normalized_code,),
            )
            rows = cursor.fetchall()
    return [_json_row(row) for row in rows]


def list_reporting_projects() -> list[dict[str, str]]:
    """Return the formal project filter projection used by analytics APIs."""

    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT project.id,project.project_code,project.project_name,
                       contract.contract_no,project.valid_from,project.valid_to
                FROM md_project project
                LEFT JOIN md_contract contract ON contract.id=project.contract_id
                WHERE project.status='active'
                ORDER BY project.project_name,project.project_code
                """
            )
            rows = cursor.fetchall()
    return [{
        "value": str(row.get("id") or ""),
        "label": str(row.get("project_name") or row.get("project_code") or row.get("id") or ""),
        "contract_no": str(row.get("contract_no") or ""),
        "start_date": str(row.get("valid_from") or "")[:10],
        "end_date": str(row.get("valid_to") or "")[:10],
    } for row in rows]


def save_master_entity(entity: str, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
    config = _master_config(entity)
    table = str(config["table"])
    allowed = tuple(str(field) for field in config["fields"])
    values = {field: payload.get(field) for field in allowed if field in payload}
    values.update(config.get("fixed", {}))
    if not str(payload.get("change_reason", "") or "").strip():
        raise ValueError("新增或修改主数据必须填写变更原因。")
    if entity == "aliases" and values.get("alias_value") and not values.get("normalized_alias"):
        values["normalized_alias"] = normalize_alias(str(values.get("entity_type", "")), values["alias_value"])
    code_field = str(config["code"])
    name_field = str(config["name"])
    if not str(values.get(code_field, "") or "").strip():
        raise ValueError(f"缺少字段：{code_field}")
    if entity != "aliases" and not str(values.get(name_field, "") or "").strip():
        values[name_field] = values[code_field]
    if "specification_json" in values and isinstance(values["specification_json"], (dict, list)):
        values["specification_json"] = json.dumps(values["specification_json"], ensure_ascii=False)
    values.setdefault("status", "active")
    values.setdefault("change_reason", "")
    entity_id = int(payload.get("id", 0) or 0)
    expected_version = int(payload.get("version", 0) or 0)
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                if entity_id:
                    if not expected_version:
                        raise ValueError("更新主数据必须提供 version。")
                    assignments = ", ".join(f"{field}=%s" for field in values)
                    cursor.execute(
                        f"UPDATE {table} SET {assignments}, updated_by=%s, version=version+1 "
                        "WHERE id=%s AND version=%s",
                        [*values.values(), actor, entity_id, expected_version],
                    )
                    if cursor.rowcount != 1:
                        raise RuntimeError("数据已被其他用户修改，请刷新后重试。")
                else:
                    columns = [*values.keys(), "created_by", "updated_by"]
                    placeholders = ", ".join(["%s"] * len(columns))
                    cursor.execute(
                        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                        [*values.values(), actor, actor],
                    )
                    entity_id = int(cursor.lastrowid)
                cursor.execute(f"SELECT * FROM {table} WHERE id=%s", (entity_id,))
                row = cursor.fetchone()
            connection.commit()
        except Exception as exc:
            connection.rollback()
            if getattr(exc, "args", ()) and exc.args[0] == 1062:
                raise ValueError("编码或别名已存在，不能重复新增。") from exc
            raise
    return _json_row(row or {})


def delete_master_entity(entity: str, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
    """Physically delete an unused master-data row after optimistic-lock and reference checks."""
    config = _master_config(entity)
    table = str(config["table"])
    entity_id = int(payload.get("id", 0) or 0)
    expected_version = int(payload.get("version", 0) or 0)
    reason = str(payload.get("change_reason", "") or "").strip()
    if not entity_id:
        raise ValueError("删除主数据必须提供 id。")
    if not expected_version:
        raise ValueError("删除主数据必须提供 version。")
    if not reason:
        raise ValueError("删除主数据必须填写删除原因。")
    where = "id=%s"
    if config.get("where"):
        where += f" AND {config['where']}"
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} WHERE {where} FOR UPDATE", (entity_id,))
                row = cursor.fetchone()
                if not row:
                    raise KeyError("主数据不存在或已经删除。")
                if int(row.get("version", 0) or 0) != expected_version:
                    raise RuntimeError("数据已被其他用户修改，请刷新后重试。")
                references = _collect_master_references(cursor, entity, config, row)
                if references:
                    detail = "、".join(f"{item['label']} {item['count']} 条" for item in references[:6])
                    raise RuntimeError(f"该数据已被引用，不能删除。请先解除引用或改为停用。引用来源：{detail}。")
                cursor.execute(f"DELETE FROM {table} WHERE {where} AND version=%s", (entity_id, expected_version))
                if cursor.rowcount != 1:
                    raise RuntimeError("数据已被其他用户修改，请刷新后重试。")
            connection.commit()
        except Exception as exc:
            connection.rollback()
            if getattr(exc, "args", ()) and exc.args[0] == 1451:
                raise RuntimeError("该数据已被引用，不能删除。请先解除引用或改为停用。") from exc
            raise
    deleted = _json_row(row)
    deleted.update({"deleted_by": actor, "delete_reason": reason})
    return deleted


def _collect_master_references(
    cursor: Any,
    entity: str,
    config: dict[str, object],
    row: dict[str, Any],
) -> list[dict[str, object]]:
    table = str(config["table"])
    entity_id = int(row["id"])
    cursor.execute(
        "SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE REFERENCED_TABLE_SCHEMA=DATABASE() AND REFERENCED_TABLE_NAME=%s",
        (table,),
    )
    columns_by_table: dict[str, list[str]] = {}
    for reference in cursor.fetchall():
        reference_table = str(reference.get("TABLE_NAME", ""))
        reference_column = str(reference.get("COLUMN_NAME", ""))
        if re.fullmatch(r"[A-Za-z0-9_]+", reference_table) and re.fullmatch(r"[A-Za-z0-9_]+", reference_column):
            columns_by_table.setdefault(reference_table, []).append(reference_column)

    for reference_table, reference_column in LOGICAL_MASTER_REFERENCES.get(entity, ()):
        columns_by_table.setdefault(reference_table, []).append(reference_column)

    references: list[dict[str, object]] = []
    for reference_table, reference_columns in columns_by_table.items():
        unique_columns = list(dict.fromkeys(reference_columns))
        predicate = " OR ".join(f"`{column}`=%s" for column in unique_columns)
        cursor.execute(
            f"SELECT COUNT(*) AS reference_count FROM `{reference_table}` WHERE {predicate}",
            [entity_id] * len(unique_columns),
        )
        count = int((cursor.fetchone() or {}).get("reference_count", 0) or 0)
        if count:
            references.append({"table": reference_table, "label": REFERENCE_TABLE_LABELS.get(reference_table, reference_table), "count": count})

    alias_types = tuple(str(value) for value in config.get("alias_types", ()))
    if alias_types:
        cursor.execute(
            f"SELECT COUNT(*) AS reference_count FROM md_alias WHERE entity_type IN ({', '.join(['%s'] * len(alias_types))}) AND entity_id=%s",
            [*alias_types, entity_id],
        )
        count = int((cursor.fetchone() or {}).get("reference_count", 0) or 0)
        if count:
            references.append({"table": "md_alias", "label": "别名", "count": count})

    if entity == "appendix-values":
        cursor.execute("SELECT category_code FROM md_appendix_category WHERE id=%s", (row.get("category_id"),))
        category_code = str((cursor.fetchone() or {}).get("category_code", ""))
        for reference_table, reference_column in APPENDIX_CODE_REFERENCES.get(category_code, ()):
            cursor.execute(
                f"SELECT COUNT(*) AS reference_count FROM `{reference_table}` WHERE `{reference_column}`=%s",
                (row.get("value_code"),),
            )
            count = int((cursor.fetchone() or {}).get("reference_count", 0) or 0)
            if count:
                references.append({"table": reference_table, "label": REFERENCE_TABLE_LABELS.get(reference_table, reference_table), "count": count})
    return references


def list_assignments(kind: str, *, status: str = "", limit: int = 1000) -> list[dict[str, Any]]:
    config = _assignment_config(kind)
    where = "WHERE status=%s" if status else ""
    args: list[object] = [status] if status else []
    args.append(max(1, min(int(limit), 5000)))
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM {config['table']} {where} ORDER BY valid_from DESC, id DESC LIMIT %s",
                args,
            )
            rows = cursor.fetchall()
    return [_json_row(row) for row in rows]


def validate_assignment(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    config = _assignment_config(kind)
    for field in config.get("required", ()):
        if not payload.get(field):
            raise ValueError(f"缺少字段：{field}")
    start = _require_datetime(payload.get("valid_from"), "valid_from")
    end = _optional_datetime(payload.get("valid_to"))
    if end and end <= start:
        raise ValueError("valid_to 必须晚于 valid_from。")
    if str(payload.get("status", "active") or "active") != "active":
        return {"valid": True, "conflicts": []}
    clauses = ["status='active'", "id<>%s", "valid_from < COALESCE(%s, '9999-12-31 23:59:59')", "COALESCE(valid_to, '9999-12-31 23:59:59') > %s"]
    args: list[object] = [int(payload.get("id", 0) or 0), end, start]
    for field in config["overlap"]:
        if kind == "project-well" and field == "job_type":
            clauses.append("(job_type=%s OR job_type='' OR %s='')")
            args.extend([payload.get(field, "") or "", payload.get(field, "") or ""])
        else:
            clauses.append(f"{field}=%s")
            args.append(payload.get(field, "") or "")
    with _db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM {config['table']} WHERE {' AND '.join(clauses)} ORDER BY valid_from",
                args,
            )
            conflicts = cursor.fetchall()
    return {"valid": not conflicts, "conflicts": [_json_row(row) for row in conflicts]}


def save_assignment(kind: str, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
    config = _assignment_config(kind)
    if not str(payload.get("change_reason", "") or "").strip():
        raise ValueError("新增或修改关系必须填写变更原因。")
    validation = validate_assignment(kind, payload)
    if not validation["valid"]:
        raise ValueError("关系有效期与现有记录重叠。")
    values = {field: payload.get(field) for field in config["fields"] if field in payload}
    values["valid_from"] = _require_datetime(values.get("valid_from"), "valid_from")
    values["valid_to"] = _optional_datetime(values.get("valid_to"))
    values.setdefault("status", "active")
    values.setdefault("change_reason", "")
    entity_id = int(payload.get("id", 0) or 0)
    expected_version = int(payload.get("version", 0) or 0)
    table = str(config["table"])
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                if entity_id:
                    if not expected_version:
                        raise ValueError("更新关系必须提供 version。")
                    assignments = ", ".join(f"{field}=%s" for field in values)
                    cursor.execute(
                        f"UPDATE {table} SET {assignments}, updated_by=%s, version=version+1 "
                        "WHERE id=%s AND version=%s",
                        [*values.values(), actor, entity_id, expected_version],
                    )
                    if cursor.rowcount != 1:
                        raise RuntimeError("关系已被其他用户修改，请刷新后重试。")
                else:
                    columns = [*values.keys(), "created_by", "updated_by"]
                    cursor.execute(
                        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                        [*values.values(), actor, actor],
                    )
                    entity_id = int(cursor.lastrowid)
                cursor.execute(f"SELECT * FROM {table} WHERE id=%s", (entity_id,))
                row = cursor.fetchone()
            connection.commit()
        except Exception as exc:
            connection.rollback()
            if getattr(exc, "args", ()) and exc.args[0] == 1062:
                raise ValueError("相同关系和生效时间已经存在。") from exc
            raise
    return _json_row(row or {})


def save_project_relationships(payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
    """Save all project-team and project-well relationships in one transaction."""
    project_id = int(payload.get("project_id", 0) or 0)
    reason = str(payload.get("change_reason", "") or "").strip()
    if not project_id:
        raise ValueError("缺少字段：project_id")
    if not reason:
        raise ValueError("保存项目关系必须填写变更原因。")
    batches = {
        "project-team": _normalize_relationship_batch("project-team", payload.get("team_assignments", payload.get("rig_assignments")), project_id, reason),
        "project-well": _normalize_relationship_batch("project-well", payload.get("well_scopes"), project_id, reason),
    }
    with _db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM md_project WHERE id=%s FOR UPDATE", (project_id,))
                if not cursor.fetchone():
                    raise ValueError("项目主数据不存在。")
                for kind, rows in batches.items():
                    _validate_relationship_batch(cursor, kind, rows)
                for kind, rows in batches.items():
                    for row in rows:
                        _save_relationship_row(cursor, kind, row, actor)
                cursor.execute(
                    "SELECT * FROM rel_project_team_assignment WHERE project_id=%s ORDER BY valid_from DESC, id DESC",
                    (project_id,),
                )
                rig_rows = cursor.fetchall()
                cursor.execute(
                    "SELECT * FROM rel_project_well_scope WHERE project_id=%s ORDER BY valid_from DESC, id DESC",
                    (project_id,),
                )
                well_rows = cursor.fetchall()
            connection.commit()
        except Exception as exc:
            connection.rollback()
            if getattr(exc, "args", ()) and exc.args[0] == 1062:
                raise ValueError("相同关系和生效时间已经存在。") from exc
            raise
    return {
        "project_id": project_id,
        "team_assignments": [_json_row(row) for row in rig_rows],
        "well_scopes": [_json_row(row) for row in well_rows],
    }


def _normalize_relationship_batch(kind: str, value: object, project_id: int, reason: str) -> list[dict[str, Any]]:
    config = _assignment_config(kind)
    source = value if isinstance(value, list) else []
    rows: list[dict[str, Any]] = []
    for raw in source:
        if not isinstance(raw, dict):
            raise ValueError("项目关系数据格式无效。")
        row = {field: raw.get(field) for field in config["fields"] if field in raw}
        row["project_id"] = project_id
        row["change_reason"] = reason
        row["status"] = str(row.get("status", "active") or "active")
        row["valid_from"] = _require_datetime(row.get("valid_from"), "valid_from")
        row["valid_to"] = _optional_datetime(row.get("valid_to"))
        row["id"] = int(raw.get("id", 0) or 0)
        row["version"] = int(raw.get("version", 0) or 0)
        for field in config.get("required", ()):
            if not row.get(field):
                raise ValueError(f"缺少字段：{field}")
        rows.append(row)
    return rows


def _validate_relationship_batch(cursor: Any, kind: str, rows: list[dict[str, Any]]) -> None:
    config = _assignment_config(kind)
    table = str(config["table"])
    update_ids = {int(row["id"]) for row in rows if row.get("id")}
    for row in rows:
        if row.get("id"):
            cursor.execute(f"SELECT project_id FROM {table} WHERE id=%s FOR UPDATE", (row["id"],))
            existing = cursor.fetchone()
            if not existing or int(existing["project_id"]) != int(row["project_id"]):
                raise ValueError("关系不存在或不属于当前项目。")
            if not row.get("version"):
                raise ValueError("更新关系必须提供 version。")
    cursor.execute(f"SELECT * FROM {table} WHERE status='active'")
    existing_rows = [row for row in cursor.fetchall() if int(row["id"]) not in update_ids]
    active_rows = [row for row in rows if row.get("status") == "active"]
    for row in active_rows:
        for existing in existing_rows:
            if _relationship_scope_overlaps(kind, row, existing) and _relationship_period_overlaps(row, existing):
                raise ValueError("关系有效期与现有记录重叠。")
    for index, row in enumerate(active_rows):
        for other in active_rows[index + 1:]:
            if _relationship_scope_overlaps(kind, row, other) and _relationship_period_overlaps(row, other):
                raise ValueError("本次提交中存在有效期重叠的关系。")


def _relationship_scope_overlaps(kind: str, left: dict[str, Any], right: dict[str, Any]) -> bool:
    if kind == "project-team":
        return int(left.get("team_id") or 0) == int(right.get("team_id") or 0)
    if int(left.get("well_id") or 0) != int(right.get("well_id") or 0):
        return False
    left_type = str(left.get("job_type", "") or "")
    right_type = str(right.get("job_type", "") or "")
    return not left_type or not right_type or left_type == right_type


def _relationship_period_overlaps(left: dict[str, Any], right: dict[str, Any]) -> bool:
    maximum = datetime.max
    left_start = datetime.fromisoformat(str(left["valid_from"]))
    right_start = datetime.fromisoformat(str(right["valid_from"]))
    left_end = datetime.fromisoformat(str(left["valid_to"])) if left.get("valid_to") else maximum
    right_end = datetime.fromisoformat(str(right["valid_to"])) if right.get("valid_to") else maximum
    return left_start < right_end and right_start < left_end


def _save_relationship_row(cursor: Any, kind: str, row: dict[str, Any], actor: str) -> None:
    config = _assignment_config(kind)
    table = str(config["table"])
    values = {field: row.get(field) for field in config["fields"]}
    if row.get("id"):
        assignments = ", ".join(f"{field}=%s" for field in values)
        cursor.execute(
            f"UPDATE {table} SET {assignments}, updated_by=%s, version=version+1 WHERE id=%s AND version=%s",
            [*values.values(), actor, row["id"], row["version"]],
        )
        if cursor.rowcount != 1:
            raise RuntimeError("关系已被其他用户修改，请刷新后重试。")
        return
    columns = [*values.keys(), "created_by", "updated_by"]
    cursor.execute(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
        [*values.values(), actor, actor],
    )


def resolve_master_id(cursor: Any, entity_type: str, raw_value: object) -> int | None:
    normalized = normalize_alias(entity_type, raw_value)
    if not normalized:
        return None
    cursor.execute(
        "SELECT entity_id FROM md_alias "
        "WHERE entity_type=%s AND normalized_alias=%s AND status='active' AND confirmation_status='confirmed' "
        "ORDER BY source_system='manual' DESC, id LIMIT 1",
        (entity_type, normalized),
    )
    row = cursor.fetchone()
    if row:
        return int(row["entity_id"])
    if entity_type == "rig":
        cursor.execute("SELECT id FROM md_rig WHERE status='active' AND (rig_code=%s OR rig_name=%s) LIMIT 1", (normalized, normalized))
    elif entity_type == "well":
        cursor.execute("SELECT id FROM md_well WHERE status='active' AND (well_code=%s OR well_name=%s) LIMIT 1", (normalized, normalized))
    else:
        return None
    row = cursor.fetchone()
    return int(row["id"]) if row else None


def resolve_project_assignment(
    cursor: Any,
    *,
    report_date: str,
    report_type: str,
    rig_id: int | None,
    well_id: int | None,
    explicit_job_id: int | None = None,
) -> dict[str, Any]:
    at_value = f"{report_date} 12:00:00"
    if explicit_job_id:
        cursor.execute(
            "SELECT id, project_id FROM biz_job WHERE id=%s AND status<>'inactive'",
            (explicit_job_id,),
        )
        job = cursor.fetchone()
        if job:
            return {"status": "MATCHED", "project_id": job.get("project_id"), "job_id": int(job["id"]), "matches": []}
    if not rig_id or not well_id or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", report_date or ""):
        return {"status": "UNASSIGNED", "project_id": None, "job_id": None, "matches": [], "message": "缺少井队、井或有效日期"}

    cursor.execute(
        """
        SELECT DISTINCT p.id, p.project_code, p.project_name
        FROM md_project p
        JOIN rel_project_well_scope ws
          ON ws.project_id=p.id AND ws.well_id=%s AND ws.status='active'
         AND ws.valid_from<=%s AND (ws.valid_to IS NULL OR ws.valid_to>%s)
         AND (ws.job_type='' OR ws.job_type=%s)
        JOIN md_rig source_rig ON source_rig.id=%s
        JOIN rel_project_team_assignment ra
          ON ra.project_id=p.id AND ra.team_id=source_rig.team_id AND ra.status='active'
         AND ra.valid_from<=%s AND (ra.valid_to IS NULL OR ra.valid_to>%s)
        WHERE p.status='active'
        ORDER BY p.id
        """,
        (well_id, at_value, at_value, report_type, rig_id, at_value, at_value),
    )
    exact = cursor.fetchall()
    candidates = exact
    if not candidates:
        cursor.execute(
            """
            SELECT DISTINCT p.id, p.project_code, p.project_name
            FROM md_project p
            JOIN md_rig source_rig ON source_rig.id=%s
            JOIN rel_project_team_assignment ra
              ON ra.project_id=p.id AND ra.team_id=source_rig.team_id AND ra.status='active'
             AND ra.valid_from<=%s AND (ra.valid_to IS NULL OR ra.valid_to>%s)
            WHERE p.status='active'
            ORDER BY p.id
            """,
            (rig_id, at_value, at_value),
        )
        candidates = cursor.fetchall()
    if len(candidates) == 1:
        project_id = int(candidates[0]["id"])
        job_id = _active_or_create_job(cursor, project_id, well_id, report_type, report_date)
        return {"status": "MATCHED", "project_id": project_id, "job_id": job_id, "matches": [_json_row(candidates[0])], "message": ""}
    if len(candidates) > 1:
        return {
            "status": "AMBIGUOUS",
            "project_id": None,
            "job_id": None,
            "matches": [_json_row(row) for row in candidates],
            "message": "同时匹配多个有效项目关系",
        }
    return {"status": "UNASSIGNED", "project_id": None, "job_id": None, "matches": [], "message": "未匹配到有效项目关系"}


def _active_or_create_job(cursor: Any, project_id: int, well_id: int, job_type: str, report_date: str) -> int:
    cursor.execute(
        "SELECT id FROM biz_job WHERE project_id=%s AND well_id=%s AND job_type=%s "
        "AND status IN ('planned','active') ORDER BY sequence_no DESC LIMIT 1",
        (project_id, well_id, job_type),
    )
    row = cursor.fetchone()
    if row:
        return int(row["id"])
    cursor.execute(
        "SELECT COALESCE(MAX(sequence_no),0)+1 AS sequence_no FROM biz_job "
        "WHERE project_id=%s AND well_id=%s AND job_type=%s",
        (project_id, well_id, job_type),
    )
    sequence_no = int((cursor.fetchone() or {}).get("sequence_no", 1) or 1)
    cursor.execute("SELECT project_code FROM md_project WHERE id=%s", (project_id,))
    project_code = str((cursor.fetchone() or {}).get("project_code", project_id))
    cursor.execute("SELECT well_code FROM md_well WHERE id=%s", (well_id,))
    well_code = str((cursor.fetchone() or {}).get("well_code", well_id))
    job_code = f"{project_code}:{well_code}:{job_type}:{sequence_no}"
    cursor.execute(
        "INSERT INTO biz_job "
        "(job_code, project_id, well_id, job_type, sequence_no, planned_start, status, created_by, updated_by) "
        "VALUES (%s,%s,%s,%s,%s,%s,'active','system','system')",
        (job_code, project_id, well_id, job_type, sequence_no, f"{report_date} 00:00:00"),
    )
    return int(cursor.lastrowid)


def _master_config(entity: str) -> dict[str, object]:
    config = MASTER_ENTITIES.get(str(entity or "").strip().lower())
    if not config:
        raise ValueError(f"不支持的主数据类型：{entity}")
    return config


def _assignment_config(kind: str) -> dict[str, object]:
    config = ASSIGNMENT_ENTITIES.get(str(kind or "").strip().lower())
    if not config:
        raise ValueError(f"不支持的关系类型：{kind}")
    return config


def _require_datetime(value: object, field: str) -> str:
    text = str(value or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return f"{text} 00:00:00"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?", text):
        return text.replace("T", " ") + (":00" if len(text) == 16 else "")
    raise ValueError(f"{field} 必须是有效日期或日期时间。")


def _optional_datetime(value: object) -> str | None:
    return _require_datetime(value, "valid_to") if str(value or "").strip() else None


def _json_row(row: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat(sep=" ", timespec="seconds")
        elif hasattr(value, "isoformat"):
            result[key] = value.isoformat()
        elif isinstance(value, bytes):
            result[key] = value.decode("utf-8", errors="replace")
        else:
            result[key] = value
    return result


def _db_connection():
    from .mysql_database import _connect, initialize_database

    initialize_database()
    return _connect()
