from __future__ import annotations

from drilling_report_parser.report_type_detection import (
    detect_report_type_from_event,
    extract_report_event_from_text,
    extract_report_events_from_text,
    normalize_report_event,
    report_types_from_event,
    storage_report_type_from_event,
)


def test_event_values_detect_all_daily_report_types() -> None:
    assert detect_report_type_from_event("DEV DRILLING") == "drilling"
    assert detect_report_type_from_event("DEV COMPLETION") == "completion"
    assert detect_report_type_from_event("WORKOVER") == "workover"
    assert detect_report_type_from_event("MAJOR RIG MOVE") == "move"


def test_rig_move_event_is_stored_with_drilling_and_keeps_event_classification() -> None:
    assert storage_report_type_from_event("MAJOR RIG MOVE") == "drilling"
    assert storage_report_type_from_event("DEV DRILLING") == "drilling"
    assert storage_report_type_from_event("DEV COMPLETION") == "completion"
    assert storage_report_type_from_event("WORKOVER") == "workover"


def test_event_detection_normalizes_accents_and_separators() -> None:
    assert normalize_report_event("  completación / diaria ") == "COMPLETACION DIARIA"
    assert detect_report_type_from_event("COMPLETACIÓN") == "completion"
    assert detect_report_type_from_event("WORK-OVER") == "workover"


def test_ambiguous_or_unknown_events_are_not_assigned_a_type() -> None:
    assert report_types_from_event("WORKOVER COMPLETION") == ("completion", "workover")
    assert detect_report_type_from_event("WORKOVER COMPLETION") == ""
    assert detect_report_type_from_event("GENERAL OPERATIONS") == ""
    assert detect_report_type_from_event("") == ""


def test_event_is_extracted_from_english_and_spanish_pdf_header_text() -> None:
    assert extract_report_event_from_text(
        "Event: MAJOR RIG MOVE             Date:TCHA-006I 06/10/2026"
    ) == "MAJOR RIG MOVE"
    assert extract_report_event_from_text(
        "Evento:  WORKOVER                Fecha:Nro:03ACAM-148 07/15/2026"
    ) == "WORKOVER"


def test_all_distinct_events_are_extracted_for_strict_mixed_type_validation() -> None:
    text = "\n".join([
        "Evento: DEV COMPLETION Fecha:Nro:COMWELL-A 07/14/2026",
        "Evento: DEV COMPLETION Fecha:Nro:COMWELL-A 07/14/2026",
        "Evento: WORKOVER Fecha:Nro:03WELL-A 07/15/2026",
    ])

    assert extract_report_events_from_text(text) == ("DEV COMPLETION", "WORKOVER")
