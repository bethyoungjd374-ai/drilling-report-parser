from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class TextPart:
    text: str
    separator_before: str = ""


def normalize_inline(value: Any) -> str:
    """Normalize horizontal spacing without changing punctuation."""
    return re.sub(r"[ \t\f\v]+", " ", str(value or "")).strip()


def normalize_multiline(value: Any) -> str:
    """Normalize line endings and horizontal spacing while preserving layout."""
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [normalize_inline(line) for line in text.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def normalize_translation_paragraph(value: Any) -> str:
    """Convert visual PDF line wrapping into one coherent model paragraph."""
    return re.sub(r"\s+", " ", normalize_multiline(value)).strip()


def join_text_lines(lines: Sequence[Any]) -> str:
    """Join extracted PDF lines without inventing punctuation."""
    return normalize_multiline("\n".join(str(line or "") for line in lines))


def column_text(
    words: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
    *,
    first_line_only: bool = False,
    preserve_lines: bool = False,
    line_tolerance: float = 2.5,
) -> str:
    """Read one coordinate column and optionally preserve its physical lines."""
    selected = [word for word in words if left <= float(word["x0"]) < right]
    if not selected:
        return ""
    if first_line_only:
        top = min(float(word["top"]) for word in selected)
        selected = [word for word in selected if abs(float(word["top"]) - top) <= line_tolerance]
    selected.sort(key=lambda word: (round(float(word["top"]), 1), float(word["x0"])))
    if not preserve_lines:
        return normalize_inline(" ".join(str(word.get("text", "") or "") for word in selected))

    lines: list[str] = []
    current_top: float | None = None
    current_words: list[str] = []
    for word in selected:
        top = round(float(word["top"]), 1)
        if current_top is None or abs(top - current_top) <= line_tolerance:
            current_top = top if current_top is None else current_top
            current_words.append(str(word.get("text", "") or ""))
            continue
        lines.append(normalize_inline(" ".join(current_words)))
        current_top = top
        current_words = [str(word.get("text", "") or "")]
    if current_words:
        lines.append(normalize_inline(" ".join(current_words)))
    return join_text_lines(lines)


def split_preserving_layout(value: Any, max_chars: int) -> list[TextPart]:
    """Split at line/sentence boundaries and retain each inter-part separator."""
    text = normalize_multiline(value)
    if not text or len(text) <= max_chars:
        return [TextPart(text)]

    atoms: list[TextPart] = []
    pending_separator = ""
    for token in re.split(r"(\n+)", text):
        if not token:
            continue
        if token.startswith("\n"):
            pending_separator += token
            continue
        inline_parts = _split_long_inline(token, max_chars)
        for index, part in enumerate(inline_parts):
            separator = pending_separator if index == 0 else " "
            atoms.append(TextPart(part, separator))
            pending_separator = ""

    packed: list[TextPart] = []
    current = ""
    current_separator = ""
    for atom in atoms:
        candidate = f"{current}{atom.separator_before}{atom.text}" if current else atom.text
        if current and len(candidate) > max_chars:
            packed.append(TextPart(current, current_separator))
            current = atom.text
            current_separator = atom.separator_before
        else:
            if not current:
                current_separator = atom.separator_before
            current = candidate
    if current or not packed:
        packed.append(TextPart(current, current_separator))
    if packed:
        packed[0] = TextPart(packed[0].text, "")
    return packed


def join_translated_parts(parts: Sequence[TextPart], translated_parts: Sequence[str]) -> str:
    values: list[str] = []
    for index, (part, translated) in enumerate(zip(parts, translated_parts)):
        text = normalize_multiline(translated)
        if index:
            values.append(part.separator_before)
        values.append(text)
    return normalize_multiline("".join(values))


def _split_long_inline(value: str, max_chars: int) -> list[str]:
    remaining = normalize_inline(value)
    parts: list[str] = []
    while len(remaining) > max_chars:
        window = remaining[: max_chars + 1]
        split_at = max(window.rfind(marker) for marker in (". ", "; ", "? ", "! ", " -", " +", " *"))
        if split_at < max_chars // 2:
            split_at = window.rfind(" ")
        if split_at <= 0:
            split_at = max_chars
        else:
            split_at += 1
        part = remaining[:split_at].strip()
        if part:
            parts.append(part)
        remaining = remaining[split_at:].strip()
    if remaining:
        parts.append(remaining)
    return parts or [""]
