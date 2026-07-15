from __future__ import annotations

from unittest.mock import MagicMock, patch

from drilling_report_parser.master_data_service import (
    _relationship_period_overlaps,
    _relationship_scope_overlaps,
    delete_master_entity,
    list_appendix_values,
    normalize_alias,
)
from drilling_report_parser.time_classification_service import classify_activity, save_rule
from drilling_report_parser.form_server import _normalize_ai_extraction_rule


def test_rig_aliases_share_one_canonical_name() -> None:
    variants = ["SINOPEC-905", "SINOPEC 905", "SINOPEC905", "W905", "RIG905", "SP905", "905"]
    assert {normalize_alias("rig", value) for value in variants} == {"SINOPEC 905"}


def test_suspected_well_typos_are_not_automatically_merged() -> None:
    assert normalize_alias("wellbore", "PCN-041") != normalize_alias("wellbore", "PCNA-041")
    assert normalize_alias("wellbore", "SHSG-160") != normalize_alias("wellbore", "SHSH-160")


def test_time_type_reference_values_are_loaded_in_appendix_order() -> None:
    connection = MagicMock()
    connection.__enter__.return_value = connection
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    connection.cursor.return_value = cursor
    cursor.fetchall.return_value = [
        {"value_code": "P", "value_name": "P", "sort_order": 10, "display_color": "#16875B"},
        {"value_code": "SC", "value_name": "SC", "sort_order": 20, "display_color": "#B7791F"},
        {"value_code": "NPT", "value_name": "NPT", "sort_order": 30, "display_color": "#D43F3A"},
    ]
    with patch("drilling_report_parser.master_data_service._db_connection", return_value=connection):
        items = list_appendix_values("time_type")
    assert [item["value_code"] for item in items] == ["P", "SC", "NPT"]
    assert cursor.execute.call_args.args[1] == ("TIME_TYPE",)


def _mock_master_delete_connection(row: dict[str, object]):
    connection = MagicMock()
    connection.__enter__.return_value = connection
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    connection.cursor.return_value = cursor
    cursor.fetchone.return_value = row
    cursor.rowcount = 1
    return connection, cursor


def test_unused_master_data_can_be_physically_deleted() -> None:
    connection, cursor = _mock_master_delete_connection({"id": 91, "version": 2, "region_code": "TEST", "region_name": "测试"})
    with patch("drilling_report_parser.master_data_service._db_connection", return_value=connection), patch(
        "drilling_report_parser.master_data_service._collect_master_references", return_value=[]
    ):
        deleted = delete_master_entity(
            "regions", {"id": 91, "version": 2, "change_reason": "测试删除"}, actor="admin"
        )
    assert deleted["id"] == 91
    assert deleted["delete_reason"] == "测试删除"
    assert any("DELETE FROM md_geo_region" in call.args[0] for call in cursor.execute.call_args_list)
    connection.commit.assert_called_once()


def test_referenced_master_data_is_not_deleted() -> None:
    connection, cursor = _mock_master_delete_connection({"id": 92, "version": 1, "well_code": "W-1", "well_name": "W-1"})
    with patch("drilling_report_parser.master_data_service._db_connection", return_value=connection), patch(
        "drilling_report_parser.master_data_service._collect_master_references",
        return_value=[{"table": "md_wellbore", "label": "井筒", "count": 2}],
    ):
        try:
            delete_master_entity("wells", {"id": 92, "version": 1, "change_reason": "测试删除"}, actor="admin")
        except RuntimeError as exc:
            assert "井筒 2 条" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("referenced master data should not be deleted")
    assert not any("DELETE FROM md_well " in call.args[0] for call in cursor.execute.call_args_list)
    connection.rollback.assert_called_once()


def test_project_relationship_period_uses_half_open_boundaries() -> None:
    first = {"valid_from": "2026-01-01 00:00:00", "valid_to": "2026-02-01 00:00:00"}
    adjacent = {"valid_from": "2026-02-01 00:00:00", "valid_to": "2026-03-01 00:00:00"}
    overlapping = {"valid_from": "2026-01-31 00:00:00", "valid_to": "2026-03-01 00:00:00"}
    assert _relationship_period_overlaps(first, adjacent) is False
    assert _relationship_period_overlaps(first, overlapping) is True


def test_project_rig_scope_conflicts_across_projects_for_same_rig() -> None:
    assert _relationship_scope_overlaps("project-rig", {"rig_id": 9, "project_id": 1}, {"rig_id": 9, "project_id": 2}) is True
    assert _relationship_scope_overlaps("project-rig", {"rig_id": 9}, {"rig_id": 10}) is False


def test_project_team_scope_conflicts_across_projects_for_same_team() -> None:
    assert _relationship_scope_overlaps("project-team", {"team_id": 9, "project_id": 1}, {"team_id": 9, "project_id": 2}) is True
    assert _relationship_scope_overlaps("project-team", {"team_id": 9}, {"team_id": 10}) is False


def test_project_well_scope_all_jobs_conflicts_with_specific_job() -> None:
    assert _relationship_scope_overlaps("project-well", {"wellbore_id": 7, "job_type": ""}, {"wellbore_id": 7, "job_type": "workover"}) is True
    assert _relationship_scope_overlaps("project-well", {"wellbore_id": 7, "job_type": "drilling"}, {"wellbore_id": 7, "job_type": "workover"}) is False


def test_time_rule_requires_a_match_condition_before_database_write() -> None:
    try:
        save_rule({
            "rule_code": "invalid-empty", "rule_name": "无匹配条件", "change_reason": "test",
            "classification": {"confirmed_op_type": "NPT"},
        }, actor="test")
    except ValueError as exc:
        assert "匹配条件" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("empty match condition should be rejected")


def test_ai_extraction_accepts_candidate_fields_without_making_them_formal() -> None:
    rule = _normalize_ai_extraction_rule({
        "id": "candidate-work-bucket", "name": "工作量候选", "report_type": "all",
        "source_section": "operations", "source_field": "operation_details",
        "target_field": "work_bucket_candidate", "output_format": "text", "enabled": True,
    }, 0)
    assert rule is not None
    assert rule["target_field"] == "work_bucket_candidate"


def test_op_code_rule_precedes_keyword_rule_even_with_lower_numeric_priority() -> None:
    class RuleCursor:
        def execute(self, _statement, _args=None):
            return None

        def fetchall(self):
            return [
                {"id": 1, "priority": 1, "op_code_pattern": "", "op_sub_pattern": "", "keyword_pattern": "repair",
                 "classification_json": '{"confirmed_op_type":"NPT","work_bucket":"MAINTENANCE"}', "rule_version": "keyword-v1"},
                {"id": 2, "priority": 100, "op_code_pattern": "^DRILLING$", "op_sub_pattern": "", "keyword_pattern": "",
                 "classification_json": '{"confirmed_op_type":"P","work_bucket":"OPERATION"}', "rule_version": "code-v1"},
            ]

    result = classify_activity(RuleCursor(), {
        "op_code": "DRILLING", "op_sub": "", "operation_details": "repair while drilling", "confirmed_op_type": "P",
    })
    assert result["rule_id"] == 2
    assert result["confirmed_op_type"] == "P"


def test_explicit_source_time_type_is_not_overwritten_by_rule() -> None:
    class RuleCursor:
        def execute(self, _statement, _args=None):
            return None

        def fetchall(self):
            return [{
                "id": 3, "priority": 10, "op_code_pattern": "^BHA$", "op_sub_pattern": "", "keyword_pattern": "",
                "classification_json": '{"confirmed_op_type":"NPT","work_bucket":"MAINTENANCE"}', "rule_version": "rule-v1",
            }]

    result = classify_activity(RuleCursor(), {
        "op_code": "BHA", "op_sub": "", "operation_details": "", "op_type": "SC",
    })
    assert result["confirmed_op_type"] == "SC"
    assert result["productive_flag"] == "NON_PRODUCTION"
    assert result["work_bucket"] == "MAINTENANCE"
    assert result["confirmation_status"] == "AUTO_CONFIRMED"


def test_rule_only_time_type_stays_pending_when_source_type_is_missing() -> None:
    class RuleCursor:
        def execute(self, _statement, _args=None):
            return None

        def fetchall(self):
            return [{
                "id": 4, "priority": 10, "op_code_pattern": "^BHA$", "op_sub_pattern": "", "keyword_pattern": "",
                "classification_json": '{"confirmed_op_type":"NPT","work_bucket":"MAINTENANCE"}', "rule_version": "rule-v1",
            }]

    result = classify_activity(RuleCursor(), {
        "op_code": "BHA", "op_sub": "", "operation_details": "", "op_type": "",
    })
    assert result["confirmed_op_type"] == "NPT"
    assert result["confirmation_status"] == "PENDING"
