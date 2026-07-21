from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import BinaryIO

from .pdf_io import extract_page, reader, source_payload


PdfSource = str | Path | bytes | BinaryIO

REPORT_TYPE_LABELS = {
    "drilling": "钻井日报",
    "completion": "完井日报",
    "workover": "修井日报",
    "move": "搬迁日报",
}

_EVENT_TYPE_PATTERNS = {
    "drilling": (
        re.compile(r"\bDRILLING\b"),
        re.compile(r"\bPERFORACION\b"),
    ),
    "completion": (
        re.compile(r"\bCOMPLETION\b"),
        re.compile(r"\bCOMPLETACION\b"),
    ),
    "workover": (
        re.compile(r"\bWORK\s*OVER\b"),
        re.compile(r"\bREACONDICIONAMIENTO\b"),
    ),
    "move": (
        re.compile(r"\bRIG\s+(?:MOVE|MOVING|MOBILI[ZS]ATION)\b"),
        re.compile(r"\bMOVILI[ZS]ATION\b"),
        re.compile(r"\bMOVILIZACION\b"),
    ),
}


def normalize_report_event(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(character for character in text if not unicodedata.combining(character))
    return " ".join(re.sub(r"[^A-Z0-9]+", " ", text.upper()).split())


def report_types_from_event(value: object) -> tuple[str, ...]:
    event = normalize_report_event(value)
    if not event:
        return ()
    matches = [
        report_type
        for report_type, patterns in _EVENT_TYPE_PATTERNS.items()
        if any(pattern.search(event) for pattern in patterns)
    ]
    return tuple(matches)


def detect_report_type_from_event(value: object) -> str:
    matches = report_types_from_event(value)
    return matches[0] if len(matches) == 1 else ""


def storage_report_type_for_event_type(event_type: str) -> str:
    """Return the stored daily-report category for an Event.

    Rig-move reports use the drilling PDF template and belong to the drilling
    lifecycle.  ``move`` remains an Event classification only; it is not a
    separate persisted report type.
    """

    normalized = str(event_type or "").strip().lower()
    return "drilling" if normalized == "move" else normalized


def storage_report_type_from_event(value: object) -> str:
    return storage_report_type_for_event_type(detect_report_type_from_event(value))


def extract_report_events_from_text(text: str) -> tuple[str, ...]:
    events: list[str] = []
    for line in str(text or "").splitlines():
        match = re.search(r"\b(?:EVENTO|EVENT)\s*:\s*(.*)$", line, flags=re.I)
        if not match:
            continue
        value = re.split(r"\s+(?:FECHA|DATE)\s*:", match.group(1), maxsplit=1, flags=re.I)[0]
        value = " ".join(value.strip().split())
        if value and normalize_report_event(value) not in {
            normalize_report_event(existing) for existing in events
        }:
            events.append(value)
    return tuple(events)


def extract_report_event_from_text(text: str) -> str:
    events = extract_report_events_from_text(text)
    return events[0] if events else ""


def extract_pdf_report_events(source: PdfSource) -> tuple[str, ...]:
    payload_source = source_payload(source)
    pdf_reader = reader(payload_source)
    events: list[str] = []
    for page in pdf_reader.pages:
        for mode in ("layout", "plain"):
            for event in extract_report_events_from_text(extract_page(page, mode)):
                if normalize_report_event(event) not in {
                    normalize_report_event(existing) for existing in events
                }:
                    events.append(event)
    return tuple(events)


def extract_pdf_report_event(source: PdfSource) -> str:
    events = extract_pdf_report_events(source)
    return events[0] if events else ""
