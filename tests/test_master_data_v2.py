from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from drilling_report_parser.field_registry import (
    parse_afe_depth_days,
    parse_numeric_field,
    parse_string_weight_pair,
)
from drilling_report_parser.master_data_service import (
    ASSIGNMENT_ENTITIES,
    _normalize_project_values,
    _json_row,
    _relationship_period_overlaps,
    _relationship_scope_overlaps,
    delete_master_entity,
    list_appendix_values,
    normalize_alias,
)
from drilling_report_parser.operation_standardization import standardize_operation_code
from drilling_report_parser.time_classification_service import (
    _pending_classification_count,
    classify_activity,
    save_rule,
)
from drilling_report_parser.form_server import _normalize_ai_extraction_rule
from drilling_report_parser.report_normalization_service import (
    _activity_datetimes,
    _activity_time_facts,
    _merge_activity_windows,
    _boundary_report_dates,
    _boundary_report_segments,
    _has_business_value,
    _move_load_counts,
    _nullable_float,
    _nullable_report_no,
    _percentage_from_text,
    _report_normalization_status,
    _sync_incident,
    refresh_report_master_matches,
    synchronize_structured_report_facts,
)
from scripts.migrate_master_data_v2 import _normalize_well_profile_code


def test_rig_aliases_share_one_canonical_name() -> None:
    variants = ["SINOPEC-905", "SINOPEC 905", "SINOPEC905", "W905", "RIG905", "SP905", "905"]
    assert {normalize_alias("rig", value) for value in variants} == {"SINOPEC 905"}


def test_project_npt_allowance_defaults_follow_project_type() -> None:
    assert _normalize_project_values({"project_type": "drilling"}, is_new=True)["npt_allowance_hours"] == 5
    assert _normalize_project_values({"project_type": "completion"}, is_new=True)["npt_allowance_hours"] == 5
    assert _normalize_project_values({"project_type": "workover"}, is_new=True)["npt_allowance_hours"] == 12


def test_project_npt_allowance_accepts_manual_override() -> None:
    values = _normalize_project_values(
        {"project_type": "workover", "npt_allowance_hours": "8.5", "valid_to": ""},
        is_new=True,
    )
    assert values["npt_allowance_hours"] == 8.5
    assert values["valid_to"] is None


def test_master_data_decimal_values_are_json_serializable() -> None:
    assert _json_row({"npt_allowance_hours": Decimal("12.50")}) == {"npt_allowance_hours": "12.50"}


def test_project_configuration_rejects_unknown_type_and_negative_allowance() -> None:
    for values in (
        {"project_type": "move"},
        {"project_type": "drilling", "npt_allowance_hours": "-0.25"},
    ):
        try:
            _normalize_project_values(values, is_new=True)
        except ValueError:
            pass
        else:  # pragma: no cover
            raise AssertionError("invalid project configuration should be rejected")


def test_suspected_well_typos_are_not_automatically_merged() -> None:
    assert normalize_alias("wellbore", "PCN-041") != normalize_alias("wellbore", "PCNA-041")
    assert normalize_alias("wellbore", "SHSG-160") != normalize_alias("wellbore", "SHSH-160")


def test_well_profile_accepts_only_explicit_source_values() -> None:
    assert _normalize_well_profile_code("直井") == "VERTICAL"
    assert _normalize_well_profile_code("定向井") == "DIRECTIONAL"
    assert _normalize_well_profile_code("水平井") == "HORIZONTAL"
    assert _normalize_well_profile_code("侧钻井") == "SIDETRACK"
    assert _normalize_well_profile_code("directional") == "DIRECTIONAL"
    assert _normalize_well_profile_code("油井") == ""
    assert _normalize_well_profile_code("修井") == ""
    assert _normalize_well_profile_code("GCLH-024H") == ""
    assert _normalize_well_profile_code("") == ""


def test_report_hour_boundaries_use_only_first_and_last_dates() -> None:
    rows = [
        {"record_id": "middle", "report_date": "2026-06-02"},
        {"record_id": "last", "report_date": "2026-06-03"},
        {"record_id": "first", "report_date": "2026-06-01"},
        {"record_id": "duplicate-middle", "report_date": "2026-06-02"},
    ]
    assert _boundary_report_dates(rows) == ("2026-06-01", "2026-06-03")


def test_single_report_date_is_both_hour_boundaries() -> None:
    assert _boundary_report_dates([{"report_date": "2026-06-11"}]) == ("2026-06-11", "2026-06-11")


def test_typed_numeric_facts_reject_values_containing_units() -> None:
    assert _nullable_float("13.375") == 13.375
    assert _nullable_float("13.375in") is None


def test_report_number_requires_an_integer_source_value() -> None:
    assert _nullable_report_no("17") == 17
    assert _nullable_report_no("17.5") is None
    assert _nullable_report_no("") is None


def test_field_registry_accepts_only_known_units_and_labels() -> None:
    assert parse_numeric_field("refDatum", "ORIGINAL KB @1,045.17ft") == 1045.17
    assert parse_numeric_field("lastCasingSize", "13.375in") == 13.375
    assert parse_numeric_field("formTestEmw", "FIT / 13.70 ppg") == 13.7
    assert parse_numeric_field("torqueOffBottom", "15,000.0 ft-lbf") == 15000.0
    assert parse_numeric_field("torqueOnBottom", "15,000.0 ft-lbf") == 15000.0
    assert parse_numeric_field("lastCasingSize", "13.375 bananas") is None


def test_combined_weight_and_afe_values_are_split_without_inventing_depth() -> None:
    assert parse_string_weight_pair("295.0 180.0 kip/") == (295.0, 180.0)
    assert parse_afe_depth_days("/ 28.0 days") == (None, 28.0)
    assert parse_afe_depth_days("12000 ft / 28 days") == (12000.0, 28.0)


def test_activity_timeline_rolls_cross_midnight_end_to_next_day() -> None:
    started_at, ended_at = _activity_datetimes("2026-06-10", "22:30", "03:00", 4.5)
    assert started_at == datetime(2026, 6, 10, 22, 30)
    assert ended_at == datetime(2026, 6, 11, 3, 0)


def test_activity_time_facts_persist_source_clock_and_validate_duration() -> None:
    facts = _activity_time_facts("2026-06-10", "22:30", "03:00", 4.5)
    assert facts["source_from_text"] == "22:30"
    assert facts["source_to_text"] == "03:00"
    assert facts["clock_hours"] == 4.5
    assert facts["duration_variance_hours"] == 0.0
    assert facts["cross_midnight_flag"] is True
    assert facts["time_validation_status"] == "VALID"


def test_activity_time_facts_block_mismatched_duration_from_official_statistics() -> None:
    facts = _activity_time_facts("2026-06-10", "08:00", "12:00", 3.0)
    assert facts["clock_hours"] == 4.0
    assert facts["duration_variance_hours"] == -1.0
    assert facts["time_validation_status"] == "DURATION_MISMATCH"


def test_job_rig_activity_windows_keep_exact_handoff_without_overlap() -> None:
    windows = [
        (datetime(2026, 6, 7, 6), datetime(2026, 6, 7, 22)),
        (datetime(2026, 6, 7, 22), datetime(2026, 6, 8, 6)),
        (datetime(2026, 6, 9, 6), datetime(2026, 6, 10, 6)),
    ]

    assert _merge_activity_windows(windows) == [
        (datetime(2026, 6, 7, 6), datetime(2026, 6, 8, 6)),
        (datetime(2026, 6, 9, 6), datetime(2026, 6, 10, 6)),
    ]


def test_hour_validation_treats_gaps_as_separate_report_segments() -> None:
    rows = [
        {"report_date": "2025-09-07"},
        {"report_date": "2025-09-08"},
        {"report_date": "2025-10-01"},
        {"report_date": "2025-10-02"},
    ]

    assert _boundary_report_segments(rows) == [
        ("2025-09-07", "2025-09-08"),
        ("2025-10-01", "2025-10-02"),
    ]


def test_operation_category_codes_are_stable_and_source_labels_remain_separate() -> None:
    assert standardize_operation_code("Surface equipment / BOP") == "SURFACE_EQUIPMENT_BOP"
    assert standardize_operation_code("  Pre-job   safety meeting ", level="subcategory") == "PRE_JOB_SAFETY_MEETING"
    assert standardize_operation_code("", level="subcategory") == "UNSPECIFIED"


def test_reviewed_operation_aliases_merge_ocr_splits_without_changing_source_text() -> None:
    assert standardize_operation_code("COMPLETI ON OPS") == "COMPLETION_OPS"
    assert standardize_operation_code("RIG MANTAINA NCE") == "RIG_MAINTENANCE"
    assert standardize_operation_code("CEME") == "CEMENTING"


def test_move_metrics_are_extracted_from_explicit_summary_text() -> None:
    summary = "RECIBE Y UBICA 19 CARGAS. RIG MOVE: 69%. RIG UP: 28%. CARGAS TOTALES ENVIADAS: 99/144"
    assert _percentage_from_text(summary, "RIG MOVE") == 69.0
    assert _percentage_from_text(summary, "RIG UP") == 28.0
    assert _move_load_counts(summary) == (19, 99, 144)


def test_negative_incident_statement_does_not_create_incident_fact() -> None:
    cursor = MagicMock()
    _sync_incident(
        cursor,
        job_id=5,
        record_id="drilling:test",
        report_date="2026-06-10",
        fields={"safetyIncident": "N", "environmentIncident": "N", "incidentComments": "SIN INCIDENTES"},
        actor="test",
    )
    statements = [call.args[0] for call in cursor.execute.call_args_list]
    assert any("DELETE FROM hsse_incident" in statement for statement in statements)
    assert not any("INSERT INTO hsse_incident" in statement for statement in statements)


def test_structured_report_facts_write_report_type_and_child_tables() -> None:
    class RecordingCursor:
        def __init__(self) -> None:
            self.calls = []

        def execute(self, statement, args=None):
            self.calls.append((" ".join(statement.split()), args))

    cursor = RecordingCursor()
    synchronize_structured_report_facts(
        cursor,
        daily_report_id=11,
        report_type="drilling",
        fields={
            "event": "DEV DRILLING", "todayMd": "10832", "bitNo": "03",
            "bitSerial": "14456485", "mudDensity": "9.8", "torqueOffBottom": "15000",
        },
        payload={
            "survey_data": [{"md": "10718", "incl": "43.16", "ew": "2703.3"}],
            "bha_components": [{"component": "PDC Bit", "od": "12.25", "joints": "1"}],
            "fluid_losses": [{"injected_volume_bbl": "12.5", "returned_volume_bbl": "3.25"}],
            "operations": [],
        },
        actor="test",
    )
    statements = [statement for statement, _args in cursor.calls]
    assert any("INSERT INTO dpr_report_summary" in statement for statement in statements)
    assert any("INSERT INTO dpr_drilling_report" in statement for statement in statements)
    assert any("torque_off_bottom_ft_lbf" in statement for statement in statements)
    assert any("bit_sequence_no" in statement and "bit_serial_no" in statement for statement in statements)
    assert any("INSERT INTO dpr_drilling_fluid_property" in statement for statement in statements)
    assert any("INSERT INTO dpr_drilling_directional_survey" in statement for statement in statements)
    assert any("east_west_ft" in statement for statement in statements)
    assert any("INSERT INTO dpr_drilling_bha_component" in statement for statement in statements)
    assert any("INSERT INTO dpr_drilling_fluid_loss" in statement for statement in statements)


def test_completion_and_workover_extensions_use_canonical_tables() -> None:
    class RecordingCursor:
        def __init__(self) -> None:
            self.calls = []

        def execute(self, statement, args=None):
            self.calls.append((" ".join(statement.split()), args))

    for report_type, expected_table in (
        ("completion", "dpr_completion_report"),
        ("workover", "dpr_workover_report"),
    ):
        cursor = RecordingCursor()
        synchronize_structured_report_facts(
            cursor,
            daily_report_id=21,
            report_type=report_type,
            fields={"description": "Explicit report extension"},
            payload={},
            actor="test",
        )
        statements = [statement for statement, _args in cursor.calls]
        assert any(f"INSERT INTO {expected_table}" in statement for statement in statements)
        assert not any("INSERT INTO fact_" in statement for statement in statements)


def test_empty_typed_extensions_are_deleted_instead_of_inserted() -> None:
    class RecordingCursor:
        def __init__(self) -> None:
            self.calls = []

        def execute(self, statement, args=None):
            self.calls.append((" ".join(statement.split()), args))

    cursor = RecordingCursor()
    synchronize_structured_report_facts(
        cursor,
        daily_report_id=12,
        report_type="drilling",
        fields={},
        payload={"survey_data": [{}], "bha_components": [{}]},
        actor="test",
    )
    statements = [statement for statement, _args in cursor.calls]
    assert "DELETE FROM dpr_report_summary WHERE daily_report_id=%s" in statements
    assert "DELETE FROM dpr_drilling_report WHERE daily_report_id=%s" in statements
    assert "DELETE FROM dpr_drilling_fluid_property WHERE daily_report_id=%s" in statements
    assert not any("INSERT INTO dpr_report_summary" in statement for statement in statements)
    assert not any("INSERT INTO dpr_drilling_report" in statement for statement in statements)
    assert not any("INSERT INTO dpr_drilling_fluid_property" in statement for statement in statements)
    assert not any("INSERT INTO dpr_drilling_directional_survey" in statement for statement in statements)
    assert not any("INSERT INTO dpr_drilling_bha_component" in statement for statement in statements)


def test_zero_is_a_meaningful_typed_fact_value() -> None:
    assert _has_business_value([None, "", "  "]) is False
    assert _has_business_value([None, 0, ""]) is True


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
        return_value=[{"table": "report_records", "label": "原始日报", "count": 2}],
    ):
        try:
            delete_master_entity("wells", {"id": 92, "version": 1, "change_reason": "测试删除"}, actor="admin")
        except RuntimeError as exc:
            assert "原始日报 2 条" in str(exc)
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


def test_retired_project_rig_scope_is_not_a_supported_relationship_kind() -> None:
    assert "project-rig" not in ASSIGNMENT_ENTITIES


def test_project_team_scope_conflicts_across_projects_for_same_team() -> None:
    assert _relationship_scope_overlaps("project-team", {"team_id": 9, "project_id": 1}, {"team_id": 9, "project_id": 2}) is True
    assert _relationship_scope_overlaps("project-team", {"team_id": 9}, {"team_id": 10}) is False


def test_project_well_scope_all_jobs_conflicts_with_specific_job() -> None:
    assert _relationship_scope_overlaps("project-well", {"well_id": 7, "job_type": ""}, {"well_id": 7, "job_type": "workover"}) is True
    assert _relationship_scope_overlaps("project-well", {"well_id": 7, "job_type": "drilling"}, {"well_id": 7, "job_type": "workover"}) is False


def test_master_relationship_refresh_moves_historical_report_into_matched_scope() -> None:
    connection = MagicMock()
    connection.__enter__.return_value = connection
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.fetchall.return_value = [{
        "id": 7, "record_id": "drilling:well-a:2026-06-01:1",
        "report_date": "2026-06-01", "report_type": "drilling",
        "rig_id": 2, "well_id": 3, "rig": "RIG A", "wellbore": "WELL A",
    }]
    connection.cursor.return_value = cursor
    with patch("drilling_report_parser.report_normalization_service._db_connection", return_value=connection), patch(
        "drilling_report_parser.report_normalization_service.resolve_master_id", side_effect=[2, 3]
    ), patch(
        "drilling_report_parser.report_normalization_service.resolve_project_assignment",
        return_value={"status": "MATCHED", "project_id": 5, "job_id": 9, "message": "", "matches": []},
    ):
        result = refresh_report_master_matches(actor="admin")

    statements = [call.args[0] for call in cursor.execute.call_args_list]
    assert any("UPDATE dpr_report\n" in statement for statement in statements)
    assert any("UPDATE dpr_report_record" in statement for statement in statements)
    assert result == {"matched": 1, "unassigned": 0, "ambiguous": 0, "normalization_failed": 0}
    connection.commit.assert_called_once()


def test_missing_master_data_is_unassigned_not_normalization_failed() -> None:
    assert _report_normalization_status("2026-07-18") == "NORMALIZED"
    assert _report_normalization_status("") == "NORMALIZATION_FAILED"


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
    assert result["work_bucket"] == ""
    assert result["confirmation_status"] == "PENDING"


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


def test_pending_classification_count_includes_sc_and_npt_rows() -> None:
    cursor = MagicMock()
    cursor.fetchone.return_value = {"count": 2}

    assert _pending_classification_count(cursor, "report-1") == 2
    statement = cursor.execute.call_args.args[0]
    assert "source_op_type" not in statement
    assert "confirmation_status NOT IN ('CONFIRMED','AUTO_CONFIRMED')" in statement
