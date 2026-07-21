"""Compatibility wrapper for the former standalone rig-move parser.

Rig-move and drilling reports share the same PDF template.  New imports use
the drilling entry point directly; this name remains only for callers that
have not yet migrated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO

from .pdf_report_parser import parse_pdf_daily_report


def parse_move_pdf_daily_report(source: str | Path | bytes | BinaryIO) -> dict[str, Any]:
    return parse_pdf_daily_report(source)
