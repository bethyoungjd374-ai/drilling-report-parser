"""Shared PDF source adapters used by all daily-report parsers."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pdfplumber
from pypdf import PdfReader

from .text_structure import normalize_pdf_ocr_text


PdfSource = str | Path | bytes | BinaryIO
PdfPayload = str | Path | bytes


def source_payload(source: PdfSource) -> PdfPayload:
    if isinstance(source, (str, Path, bytes)):
        return source
    return source.read()


def reader(source: PdfSource) -> PdfReader:
    if isinstance(source, (str, Path)):
        return PdfReader(str(source))
    if isinstance(source, bytes):
        return PdfReader(BytesIO(source))
    return PdfReader(source)


def extract_page(page: object, mode: str) -> str:
    extract_text = getattr(page, "extract_text")
    try:
        if mode == "layout":
            text = extract_text(extraction_mode="layout") or ""
        else:
            text = extract_text() or ""
    except Exception:
        text = extract_text() or ""
    return normalize_pdf_ocr_text(text)


def pdfplumber_open(source: str | Path | bytes):
    if isinstance(source, (str, Path)):
        return pdfplumber.open(str(source))
    return pdfplumber.open(BytesIO(source))
