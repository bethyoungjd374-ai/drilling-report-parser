from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Callable

from pypdf import PdfReader, PdfWriter


PdfSource = str | Path | bytes | BinaryIO
PdfParser = Callable[[bytes], dict[str, Any]]


@dataclass(frozen=True)
class PdfReportSegment:
    data: bytes
    start_page: int
    end_page: int
    identity: tuple[str, str, str] | None


def split_pdf_daily_reports(source: PdfSource, parser: PdfParser) -> list[PdfReportSegment]:
    """Split a PDF whenever a complete daily-report identity changes.

    Report headers may repeat on every page (common for drilling reports), while
    continuation pages may omit the header entirely (common for completion and
    workover reports).  A new segment therefore starts only when a page exposes
    a complete date/well/report-number identity that differs from the current
    report.  Headerless pages remain attached to the preceding report.
    """

    pdf_bytes = _source_bytes(source)
    reader = PdfReader(BytesIO(pdf_bytes))
    if not reader.pages:
        raise ValueError("PDF does not contain any pages.")

    page_identities = [_page_identity(page, parser) for page in reader.pages]
    ranges: list[tuple[int, int, tuple[str, str, str] | None]] = []
    start_index = 0
    current_identity: tuple[str, str, str] | None = None

    for page_index, identity in enumerate(page_identities):
        if identity is None:
            continue
        if current_identity is None:
            current_identity = identity
            continue
        if identity == current_identity:
            continue
        ranges.append((start_index, page_index - 1, current_identity))
        start_index = page_index
        current_identity = identity

    ranges.append((start_index, len(reader.pages) - 1, current_identity))
    return [
        PdfReportSegment(
            data=_pages_bytes(reader, start, end),
            start_page=start + 1,
            end_page=end + 1,
            identity=identity,
        )
        for start, end, identity in ranges
    ]


def report_identity(payload: dict[str, Any]) -> tuple[str, str, str] | None:
    fields = payload.get("report_fields", {})
    if not isinstance(fields, dict):
        return None
    report_date = str(fields.get("reportDate", "") or "").strip()
    wellbore = " ".join(str(fields.get("wellbore", "") or "").upper().split())
    report_no = str(fields.get("reportNo", "") or "").strip()
    if not report_date or not wellbore or not report_no:
        return None
    if report_no.isdigit():
        report_no = str(int(report_no))
    return report_date, wellbore, report_no


def _page_identity(page: object, parser: PdfParser) -> tuple[str, str, str] | None:
    try:
        payload = parser(_page_bytes(page))
    except Exception:
        return None
    return report_identity(payload)


def _source_bytes(source: PdfSource) -> bytes:
    if isinstance(source, bytes):
        return source
    if isinstance(source, (str, Path)):
        return Path(source).read_bytes()
    return source.read()


def _page_bytes(page: object) -> bytes:
    writer = PdfWriter()
    writer.add_page(page)  # type: ignore[arg-type]
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def _pages_bytes(reader: PdfReader, start: int, end: int) -> bytes:
    writer = PdfWriter()
    for page_index in range(start, end + 1):
        writer.add_page(reader.pages[page_index])
    output = BytesIO()
    writer.write(output)
    return output.getvalue()
