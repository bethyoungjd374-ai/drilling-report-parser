"""Canonical operation taxonomy independent from individual PDF templates."""

from __future__ import annotations

import re

from .text_structure import normalize_translation_paragraph


# Keys are syntactically normalized source labels.  Only high-confidence
# truncations, OCR word splits and established abbreviations belong here.
# Ambiguous labels intentionally keep their own code until business review.
OPERATION_CATEGORY_CODE_ALIASES = {
    "CEM": "CEMENTING",
    "CEME": "CEMENTING",
    "CIRCULATI_NG": "CIRCULATING",
    "CLEA": "CLEANING_HOLE",
    "CLEANNIN_G_HOLE": "CLEANING_HOLE",
    "COMPLETI_ON_OPS": "COMPLETION_OPS",
    "FISHI": "FISHING",
    "LOG": "LOGGING",
    "LOGG": "LOGGING",
    "MOV": "MOVE",
    "RIG_MANTAINA_NCE": "RIG_MAINTENANCE",
    "SLK": "SLICK_LINE",
    "SURF": "SURFACE_EQUIPMENT",
    "WELLHEA_D": "WELLHEAD",
}


OPERATION_SUBCATEGORY_CODE_ALIASES = {
    "DRILLSTRING_TU_BULAR": "DRILLSTRING_TUBULAR",
    "RU_RD_SURFACE_EQUIPM": "RU_RD_SURFACE_EQUIPMENT",
    "SERVICE_COMPANY_EQUI": "SERVICE_COMPANY_EQUIPMENT",
}


def standardize_operation_code(value: object, *, level: str = "category") -> str:
    """Convert a source label to a stable code and apply reviewed aliases."""
    normalized = normalize_translation_paragraph(value).upper()
    syntactic_code = re.sub(r"_+", "_", re.sub(r"[^A-Z0-9]+", "_", normalized)).strip("_")
    if not syntactic_code:
        return "UNSPECIFIED"
    aliases = OPERATION_SUBCATEGORY_CODE_ALIASES if level == "subcategory" else OPERATION_CATEGORY_CODE_ALIASES
    return aliases.get(syntactic_code, syntactic_code)
