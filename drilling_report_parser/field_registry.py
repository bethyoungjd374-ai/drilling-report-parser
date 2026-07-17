"""Deterministic typed-field parsing rules for the normalized fact layer.

The raw audit layer keeps source text unchanged.  Only field-specific rules in
this module may remove labels or units before a value reaches a numeric column.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)")
STRICT_NUMBER_RE = re.compile(r"^[-+]?(?:\d+(?:\.\d*)?|\.\d+)$")


@dataclass(frozen=True)
class NumericFieldRule:
    allowed_tokens: tuple[str, ...] = ()
    minimum: float | None = None
    maximum: float | None = None


NUMERIC_FIELD_RULES: dict[str, NumericFieldRule] = {
    "refDatum": NumericFieldRule(("ORIGINAL", "KB", "FT")),
    "lastCasingSize": NumericFieldRule(("IN",), 0),
    "nextCasingSize": NumericFieldRule(("IN",), 0),
    "formTestEmw": NumericFieldRule(("FIT", "LOT", "PPG"), 0),
    "torqueOffBottom": NumericFieldRule(("FT-LBF", "FT LBF", "LBF-FT", "LBF FT"), 0),
    "torqueOnBottom": NumericFieldRule(("FT-LBF", "FT LBF", "LBF-FT", "LBF FT"), 0),
    "stringWeightUp": NumericFieldRule(("KIP",), 0),
    "stringWeightDown": NumericFieldRule(("KIP",), 0),
}


def parse_numeric_field(field_code: str, value: object) -> float | None:
    """Parse one number only when the field's known source labels are valid."""
    text = _text(value)
    if not text:
        return None
    compact = text.replace(",", "").strip()
    if STRICT_NUMBER_RE.fullmatch(compact):
        return _bounded(field_code, float(compact))

    rule = NUMERIC_FIELD_RULES.get(field_code)
    if rule is None:
        return None
    matches = NUMBER_RE.findall(compact)
    if len(matches) != 1 or not _residual_is_allowed(compact, matches[0], rule.allowed_tokens):
        return None
    return _bounded(field_code, float(matches[0]))


def parse_string_weight_pair(value: object) -> tuple[float | None, float | None]:
    """Parse the combined up/down hook-load source field without guessing."""
    text = _text(value).replace(",", "")
    matches = NUMBER_RE.findall(text)
    if len(matches) != 2 or not _residual_is_allowed(text, None, ("KIP",), remove_all_numbers=True):
        return None, None
    values = tuple(float(item) for item in matches)
    if any(item < 0 for item in values):
        return None, None
    return values[0], values[1]


def parse_afe_depth_days(value: object) -> tuple[float | None, float | None]:
    """Split the combined AFE MD/Days cell while respecting explicit units."""
    text = _text(value).replace(",", "")
    numbers = [float(item) for item in NUMBER_RE.findall(text)]
    if not numbers:
        return None, None
    upper = text.upper()
    has_days = bool(re.search(r"\bDAYS?\b|\bD\b", upper))
    has_depth = bool(re.search(r"\bFT\b|\bFEET\b", upper))
    if len(numbers) == 1:
        if has_days and not has_depth:
            return None, numbers[0]
        if has_depth and not has_days:
            return numbers[0], None
        return None, None
    return numbers[0], numbers[1]


def _bounded(field_code: str, value: float) -> float | None:
    rule = NUMERIC_FIELD_RULES.get(field_code)
    if rule is None:
        return value
    if rule.minimum is not None and value < rule.minimum:
        return None
    if rule.maximum is not None and value > rule.maximum:
        return None
    return value


def _residual_is_allowed(
    text: str,
    number: str | None,
    allowed_tokens: tuple[str, ...],
    *,
    remove_all_numbers: bool = False,
) -> bool:
    residual = text.upper()
    for token in sorted(allowed_tokens, key=len, reverse=True):
        residual = residual.replace(token, "")
    residual = NUMBER_RE.sub("", residual) if remove_all_numbers else residual.replace(str(number or ""), "", 1)
    residual = re.sub(r"[\s@/:()_\-]+", "", residual)
    return not residual


def _text(value: object) -> str:
    return str(value or "").strip()
