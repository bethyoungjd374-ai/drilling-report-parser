from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader, PdfWriter

from drilling_report_parser.pdf_batch import report_identity, split_pdf_daily_reports


def _pdf_with_page_widths(*widths: float) -> bytes:
    writer = PdfWriter()
    for width in widths:
        writer.add_blank_page(width=width, height=300)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def _identity_parser(source: bytes) -> dict[str, object]:
    pages = PdfReader(BytesIO(source)).pages
    width = round(float(pages[0].mediabox.width))
    identities = {
        101: ("2026-06-01", "WELL-A", "01"),
        102: ("2026-06-01", "well-a", "1"),
        201: ("2026-06-02", "WELL-A", "2"),
        202: ("2026-06-02", "WELL-A", "02"),
    }
    identity = identities.get(width)
    fields = {}
    if identity:
        fields = {
            "reportDate": identity[0],
            "wellbore": identity[1],
            "reportNo": identity[2],
        }
    return {"report_fields": fields, "page_count": len(pages)}


def test_split_pdf_groups_repeated_headers_and_headerless_continuation_pages() -> None:
    source = _pdf_with_page_widths(101, 102, 150, 201, 250, 202)

    segments = split_pdf_daily_reports(source, _identity_parser)

    assert [(item.start_page, item.end_page) for item in segments] == [(1, 3), (4, 6)]
    assert [len(PdfReader(BytesIO(item.data)).pages) for item in segments] == [3, 3]
    assert segments[0].identity == ("2026-06-01", "WELL-A", "1")
    assert segments[1].identity == ("2026-06-02", "WELL-A", "2")


def test_split_pdf_keeps_unrecognized_document_as_one_report() -> None:
    source = _pdf_with_page_widths(150, 151, 152)

    segments = split_pdf_daily_reports(source, _identity_parser)

    assert len(segments) == 1
    assert (segments[0].start_page, segments[0].end_page) == (1, 3)
    assert segments[0].identity is None


def test_report_identity_requires_all_three_fields_and_normalizes_values() -> None:
    assert report_identity({"report_fields": {
        "reportDate": "2026-06-01",
        "wellbore": " well-a ",
        "reportNo": "001",
    }}) == ("2026-06-01", "WELL-A", "1")
    assert report_identity({"report_fields": {
        "reportDate": "2026-06-01",
        "wellbore": "WELL-A",
        "reportNo": "",
    }}) is None
