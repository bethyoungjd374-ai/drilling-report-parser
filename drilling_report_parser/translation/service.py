from __future__ import annotations

import copy
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from ..parser import ParseResult


DEFAULT_TERMS_PATH = Path(__file__).with_name("drilling_terms.json")
LANGUAGES = ("zh", "en", "es")
TARGET_LANGUAGE = "zh"
SUPPORTED_TRANSLATION_LANGUAGES = {"zh", "en", "es"}


class TranslationError(RuntimeError):
    """Raised when the configured local translation engine cannot translate text."""


class TranslationEngine(Protocol):
    name: str

    def translate(self, text: str, source_language: str, target_language: str = TARGET_LANGUAGE) -> str:
        ...


@dataclass(frozen=True)
class TranslationConfig:
    engine: str = "libretranslate"
    target_language: str = TARGET_LANGUAGE
    terms_path: Path = DEFAULT_TERMS_PATH
    libretranslate_url: str = "http://127.0.0.1:5000"
    libretranslate_api_key: str = ""
    timeout_seconds: float = 20.0

    @classmethod
    def from_env(cls) -> "TranslationConfig":
        terms_path = Path(os.environ.get("DRP_TRANSLATION_TERMS", str(DEFAULT_TERMS_PATH))).expanduser()
        return cls(
            engine=os.environ.get("DRP_TRANSLATION_ENGINE", "libretranslate").strip() or "libretranslate",
            target_language=os.environ.get("DRP_TRANSLATION_TARGET", TARGET_LANGUAGE).strip() or TARGET_LANGUAGE,
            terms_path=terms_path,
            libretranslate_url=os.environ.get("DRP_LIBRETRANSLATE_URL", "http://127.0.0.1:5000").rstrip("/"),
            libretranslate_api_key=os.environ.get("DRP_LIBRETRANSLATE_API_KEY", ""),
            timeout_seconds=float(os.environ.get("DRP_TRANSLATION_TIMEOUT", "20") or "20"),
        )


@dataclass(frozen=True)
class TermEntry:
    id: str
    category: str = "drilling"
    zh: str = ""
    en: str = ""
    es: str = ""
    aliases: dict[str, tuple[str, ...]] = field(default_factory=dict)
    protected: bool = True
    enabled: bool = True
    updated_at: str = ""

    def value(self, language: str) -> str:
        return str(getattr(self, language, "") or "").strip()

    def source_values(self) -> list[tuple[str, str]]:
        values: list[tuple[str, str]] = []
        for language in LANGUAGES:
            value = self.value(language)
            if value:
                values.append((language, value))
            for alias in self.aliases.get(language, ()):
                alias_text = str(alias or "").strip()
                if alias_text:
                    values.append((language, alias_text))
        return values


@dataclass(frozen=True)
class TermsConfig:
    entries: tuple[TermEntry, ...] = ()
    acronyms: tuple[str, ...] = ()
    units: tuple[str, ...] = ()
    proper_nouns: tuple[str, ...] = ()

    @classmethod
    def load(cls, path: str | Path = DEFAULT_TERMS_PATH) -> "TermsConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_data(data)

    @classmethod
    def from_data(cls, data: object) -> "TermsConfig":
        source = data if isinstance(data, dict) else {}
        protected = source.get("protected_terms", {}) if isinstance(source.get("protected_terms"), dict) else {}
        raw_terms = source.get("terms")
        entries: list[TermEntry] = []

        if isinstance(raw_terms, list):
            for item in raw_terms:
                entry = _term_entry_from_object(item)
                if entry:
                    entries.append(entry)
        elif isinstance(raw_terms, dict):
            for source_text, zh_text in raw_terms.items():
                source_value = str(source_text or "").strip()
                zh_value = str(zh_text or "").strip()
                if not source_value or not zh_value:
                    continue
                entries.append(TermEntry(
                    id=_stable_term_id(source_value, zh_value),
                    category="drilling",
                    zh=zh_value,
                    en=source_value,
                    es="",
                    aliases={language: () for language in LANGUAGES},
                    protected=True,
                    enabled=True,
                ))

        return cls(
            entries=tuple(entries),
            acronyms=_string_tuple(protected.get("acronyms")),
            units=_string_tuple(protected.get("units")),
            proper_nouns=_string_tuple(protected.get("proper_nouns")),
        )


@dataclass(frozen=True)
class Protection:
    placeholder: str
    original: str
    replacement: str
    category: str
    term_id: str = ""
    target_language: str = ""


@dataclass(frozen=True)
class TextUnit:
    path: str
    text: str


@dataclass(frozen=True)
class TermMatcher:
    entry: TermEntry
    source_language: str
    source_value: str
    target_language: str
    replacement: str
    pattern: re.Pattern[str]


class LibreTranslateEngine:
    name = "libretranslate"

    def __init__(self, base_url: str = "http://127.0.0.1:5000", api_key: str = "", timeout_seconds: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def translate(self, text: str, source_language: str, target_language: str = TARGET_LANGUAGE) -> str:
        payload = {
            "q": text,
            "source": source_language,
            "target": target_language,
            "format": "text",
        }
        if self.api_key:
            payload["api_key"] = self.api_key
        body = urllib.parse.urlencode(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/translate",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise TranslationError(f"LibreTranslate service is unavailable: {exc}") from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TranslationError("LibreTranslate returned non-JSON response.") from exc

        translated = data.get("translatedText") if isinstance(data, dict) else None
        if not isinstance(translated, str):
            raise TranslationError(f"LibreTranslate returned unexpected response: {raw[:200]}")
        return translated


class NoopTranslationEngine:
    name = "noop"

    def translate(self, text: str, source_language: str, target_language: str = TARGET_LANGUAGE) -> str:
        return text


class DrillingReportTranslator:
    def __init__(
        self,
        engine: TranslationEngine,
        terms: TermsConfig,
        target_language: str = TARGET_LANGUAGE,
    ) -> None:
        self.engine = engine
        self.terms = terms
        self.target_language = normalize_language(target_language)
        self._term_matchers = _compiled_term_matchers(terms.entries, self.target_language)
        self._protect_patterns = _compiled_protect_patterns(terms)

    def translate_report_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        source_payload = copy.deepcopy(payload)
        units = list(iter_payload_text_units(source_payload))
        translated_payload = copy.deepcopy(source_payload)
        items: list[dict[str, Any]] = []
        warnings: list[str] = []
        untranslated_fields: list[dict[str, str]] = []
        term_records: list[dict[str, str]] = []

        for unit in units:
            segment_items = self.translate_text_unit(unit)
            items.extend(segment_items)
            _set_payload_value(
                translated_payload,
                unit.path,
                " ".join(str(item.get("translated_text", "")) for item in segment_items).strip(),
            )
            for item in segment_items:
                item_path = str(item.get("path", unit.path))
                if item.get("term_replacements"):
                    term_records.extend({"path": item_path, **record} for record in item["term_replacements"])
                if item.get("untranslated_tokens"):
                    untranslated_fields.append({
                        "path": item_path,
                        "tokens": ", ".join(item["untranslated_tokens"]),
                    })
                if item.get("warnings"):
                    warnings.extend(f"{item_path}: {warning}" for warning in item["warnings"])
                if item.get("error"):
                    warnings.append(f"{item_path}: {item['error']}")

        return {
            "metadata": {
                "source": "drilling_report_translation",
                "engine": self.engine.name,
                "target_language": self.target_language,
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "item_count": len(items),
                "translated_count": sum(1 for item in items if item.get("translated")),
                "warning_count": len(warnings),
            },
            "items": items,
            "translated_payload": translated_payload,
            "untranslated_fields": untranslated_fields,
            "term_replacement_records": term_records,
            "warnings": warnings,
        }

    def translate_parse_result(self, result: ParseResult) -> dict[str, Any]:
        units = list(iter_parse_result_text_units(result))
        items = [item for unit in units for item in self.translate_text_unit(unit)]
        term_records: list[dict[str, str]] = []
        warnings: list[str] = []
        untranslated_fields: list[dict[str, str]] = []
        for item in items:
            path = str(item.get("path", ""))
            term_records.extend({"path": path, **record} for record in item.get("term_replacements", []))
            if item.get("untranslated_tokens"):
                untranslated_fields.append({"path": path, "tokens": ", ".join(item["untranslated_tokens"])})
            warnings.extend(f"{path}: {warning}" for warning in item.get("warnings", []))
            if item.get("error"):
                warnings.append(f"{path}: {item['error']}")

        return {
            "metadata": {
                "source": "drilling_report_translation",
                "engine": self.engine.name,
                "target_language": self.target_language,
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "source_file": result.source_file,
                "item_count": len(items),
                "translated_count": sum(1 for item in items if item.get("translated")),
                "warning_count": len(warnings),
            },
            "items": items,
            "untranslated_fields": untranslated_fields,
            "term_replacement_records": term_records,
            "warnings": warnings,
        }

    def translate_plain_text(self, text: str) -> dict[str, Any]:
        items = [
            self.translate_text(segment, f"text[{index}]")
            for index, segment in enumerate(split_segments(text))
            if segment.strip()
        ]
        return {
            "metadata": {
                "source": "plain_text_translation",
                "engine": self.engine.name,
                "target_language": self.target_language,
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "item_count": len(items),
                "translated_count": sum(1 for item in items if item.get("translated")),
            },
            "items": items,
            "translated_text": " ".join(str(item.get("translated_text", "")) for item in items).strip(),
            "term_replacement_records": [
                {"path": str(item.get("path", "")), **record}
                for item in items
                for record in item.get("term_replacements", [])
            ],
            "warnings": [
                f"{item.get('path')}: {warning}"
                for item in items
                for warning in item.get("warnings", [])
            ],
        }

    def translate_text_unit(self, unit: TextUnit) -> list[dict[str, Any]]:
        segments = split_segments(unit.text)
        if len(segments) <= 1:
            return [self.translate_text(unit.text, unit.path)]
        return [
            self.translate_text(segment, f"{unit.path}#{index}")
            for index, segment in enumerate(segments)
        ]

    def translate_text(self, text: str, path: str = "") -> dict[str, Any]:
        original = _clean_text(text)
        language = detect_language(original)
        warnings: list[str] = []
        error = ""

        if not original:
            return _translation_item(path, text, "", language, False, [], [], warnings, error)

        protected_text, protections = self._protect(original)
        untranslated_tokens = [
            protection.original
            for protection in protections
            if protection.category not in {"term"}
        ]
        protected_term_replacements = [
            _term_record(protection.original, protection.replacement, protection.term_id, protection.target_language)
            for protection in protections
            if protection.category == "term" and protection.original != protection.replacement
        ]

        if language == self.target_language and not _has_effective_term_replacement(protections):
            translated = self._restore(protected_text, protections)
            translated, term_replacements = self._apply_term_replacements(translated)
            return _translation_item(path, original, translated, language, False, untranslated_tokens, term_replacements, warnings, error)

        if language not in SUPPORTED_TRANSLATION_LANGUAGES or _looks_non_translatable(original, protections):
            translated = self._restore(protected_text, protections)
            translated, term_replacements = self._apply_term_replacements(translated)
            term_replacements = protected_term_replacements + term_replacements
            reason = "non_translatable" if _looks_non_translatable(original, protections) else f"unsupported_language:{language}"
            warnings.append(reason)
            return _translation_item(path, original, translated, language, False, untranslated_tokens, term_replacements, warnings, error)

        try:
            translated = self.engine.translate(protected_text, language, self.target_language)
            translated_flag = self.engine.name != "noop"
            if not translated_flag:
                warnings.append("noop_engine; returned terminology-protected source text")
        except Exception as exc:
            translated = protected_text
            translated_flag = False
            error = str(exc)
            warnings.append("engine_failed; returned terminology-protected source text")

        translated = self._restore(translated, protections)
        translated, term_replacements = self._apply_term_replacements(translated)
        term_replacements = protected_term_replacements + term_replacements
        return _translation_item(path, original, translated, language, translated_flag, untranslated_tokens, term_replacements, warnings, error)

    def _protect(self, text: str) -> tuple[str, list[Protection]]:
        protections: list[Protection] = []

        def placeholder_for(index: int) -> str:
            letters = ""
            value = index
            while True:
                letters = chr(ord("A") + (value % 26)) + letters
                value = value // 26 - 1
                if value < 0:
                    break
            return f"DRPPLACEHOLDER{letters}"

        def add(original: str, replacement: str, category: str, term_id: str = "") -> str:
            placeholder = placeholder_for(len(protections))
            protections.append(Protection(
                placeholder=placeholder,
                original=original,
                replacement=replacement,
                category=category,
                term_id=term_id,
                target_language=self.target_language if term_id else "",
            ))
            return placeholder

        protected = text
        for category, pattern in self._protect_patterns:
            protected = pattern.sub(lambda match, category=category: add(match.group(0), match.group(0), category), protected)

        for matcher in self._term_matchers:
            if not matcher.entry.protected:
                continue

            def replace(match: re.Match[str], matcher: TermMatcher = matcher) -> str:
                return add(match.group(0), matcher.replacement, "term", matcher.entry.id)

            protected = matcher.pattern.sub(replace, protected)

        return protected, protections

    @staticmethod
    def _restore(text: str, protections: list[Protection]) -> str:
        restored = text
        for protection in protections:
            restored = restored.replace(protection.placeholder, protection.replacement)
        return restored

    def _apply_term_replacements(self, text: str) -> tuple[str, list[dict[str, str]]]:
        records: list[dict[str, str]] = []
        translated = text
        for matcher in self._term_matchers:
            def replace(match: re.Match[str], matcher: TermMatcher = matcher) -> str:
                original = match.group(0)
                if original == matcher.replacement:
                    return original
                records.append(_term_record(original, matcher.replacement, matcher.entry.id, self.target_language))
                return matcher.replacement

            translated = matcher.pattern.sub(replace, translated)
        return translated, records


def build_translator(
    config: TranslationConfig | None = None,
    engine: TranslationEngine | None = None,
    terms: TermsConfig | None = None,
    target_language: str | None = None,
) -> DrillingReportTranslator:
    config = config or TranslationConfig.from_env()
    selected_terms = terms or TermsConfig.load(config.terms_path)
    selected_engine = engine or build_engine(config)
    return DrillingReportTranslator(
        selected_engine,
        selected_terms,
        target_language=target_language or config.target_language,
    )


def build_engine(config: TranslationConfig) -> TranslationEngine:
    engine = config.engine.lower()
    if engine == "libretranslate":
        return LibreTranslateEngine(
            base_url=config.libretranslate_url,
            api_key=config.libretranslate_api_key,
            timeout_seconds=config.timeout_seconds,
        )
    if engine in {"noop", "none"}:
        return NoopTranslationEngine()
    raise ValueError(f"Unsupported translation engine: {config.engine}")


def normalize_language(value: object) -> str:
    language = str(value or TARGET_LANGUAGE).strip().lower()
    if language not in SUPPORTED_TRANSLATION_LANGUAGES:
        raise ValueError("target_language must be one of zh, en, es.")
    return language


def detect_language(text: str) -> str:
    normalized = _clean_text(text)
    if not normalized:
        return "und"
    cjk_count = sum(1 for char in normalized if "\u4e00" <= char <= "\u9fff")
    latin_count = sum(1 for char in normalized if char.isascii() and char.isalpha())
    if cjk_count and cjk_count >= latin_count:
        return "zh"
    if not latin_count and not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", normalized):
        return "und"
    if re.search(r"[ÁÉÍÓÚÜÑáéíóúüñ¿¡]", normalized):
        return "es"

    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", normalized.lower())
    if not words:
        return "und"
    spanish_score = sum(1 for word in words if word in SPANISH_HINTS)
    english_score = sum(1 for word in words if word in ENGLISH_HINTS)
    if spanish_score > english_score:
        return "es"
    return "en"


def iter_payload_text_units(payload: dict[str, Any]) -> list[TextUnit]:
    units: list[TextUnit] = []
    fields = payload.get("report_fields", {})
    if isinstance(fields, dict):
        for key, value in fields.items():
            if _is_text_value(value):
                units.append(TextUnit(f"report_fields.{key}", str(value)))

    for table_name, rows in payload.items():
        if table_name in {"metadata", "report_fields"} or not isinstance(rows, list):
            continue
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            for key, value in row.items():
                if key in {"source_sheet", "source_row"}:
                    continue
                if _is_text_value(value):
                    units.append(TextUnit(f"{table_name}[{row_index}].{key}", str(value)))
    return units


def iter_parse_result_text_units(result: ParseResult) -> list[TextUnit]:
    units: list[TextUnit] = []
    for row in result.fields:
        field_name = str(row.get("field", "")).strip() or "unknown"
        value = row.get("value", "")
        if _is_text_value(value):
            units.append(TextUnit(f"fields.{field_name}", str(value)))
    for table_name, rows in result.tables.items():
        for row_index, row in enumerate(rows):
            for key, value in row.items():
                if key in {"source_sheet", "source_row"}:
                    continue
                if _is_text_value(value):
                    units.append(TextUnit(f"tables.{table_name}[{row_index}].{key}", str(value)))
    return units


def split_segments(text: str) -> list[str]:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    if not lines:
        lines = [_clean_text(text)] if _clean_text(text) else []
    segments: list[str] = []
    for line in lines:
        parts = re.split(r"(?<=[.!?。！？;；])\s+", line)
        segments.extend(part.strip() for part in parts if part.strip())
    return segments


def _compiled_term_matchers(entries: tuple[TermEntry, ...], target_language: str) -> list[TermMatcher]:
    matchers: list[TermMatcher] = []
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        if not entry.enabled:
            continue
        replacement = entry.value(target_language)
        if not replacement:
            continue
        for source_language, source_value in entry.source_values():
            key = (source_language, source_value.lower())
            if not source_value or key in seen:
                continue
            seen.add(key)
            matchers.append(TermMatcher(
                entry=entry,
                source_language=source_language,
                source_value=source_value,
                target_language=target_language,
                replacement=replacement,
                pattern=re.compile(_term_regex(source_value), re.IGNORECASE),
            ))
    return sorted(matchers, key=lambda item: len(item.source_value), reverse=True)


def _compiled_protect_patterns(terms: TermsConfig) -> list[tuple[str, re.Pattern[str]]]:
    patterns: list[tuple[str, re.Pattern[str]]] = [
        ("well_or_equipment_id", re.compile(r"\b[A-Z]{1,6}(?:-[A-Z0-9]{1,6}){1,4}[A-Z]?\b")),
        ("datetime", re.compile(r"\b(?:\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}:\d{2})(?:\s*[AP]M)?\b", re.IGNORECASE)),
        ("measurement", re.compile(r"\b\d[\d,]*(?:\.\d+)?(?:\s*(?:m|ft|in|ppg|psi|bbl|gpm|klb|lb|hr|hrs|deg|spf)(?:/[A-Za-z0-9]+)?)\b", re.IGNORECASE)),
        ("inch_fraction", re.compile(r"\b\d+(?:-\d+/\d+|\.\d+)?\s*(?:\"|”|in)\b", re.IGNORECASE)),
    ]

    term_sources = {
        value.lower()
        for entry in terms.entries
        if entry.enabled
        for _, value in entry.source_values()
    }
    protected_terms: set[str] = set()
    protected_terms.update(item for item in terms.acronyms if item.lower() not in term_sources)
    protected_terms.update(item for item in terms.units if len(item) > 2 or "/" in item)
    protected_terms.update(item for item in terms.proper_nouns if item.lower() not in term_sources)
    for term in sorted({item for item in protected_terms if str(item or "").strip()}, key=len, reverse=True):
        patterns.append(("protected_term", re.compile(_term_regex(str(term)), re.IGNORECASE)))
    return patterns


def _term_regex(term: str) -> str:
    escaped = re.escape(term).replace(r"\ ", r"\s+")
    return rf"(?<![A-Za-z0-9_/-]){escaped}(?![A-Za-z0-9_/-])"


def _looks_non_translatable(text: str, protections: list[Protection]) -> bool:
    stripped = _clean_text(text)
    if not stripped:
        return True
    if not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\u4e00-\u9fff]", stripped):
        return True
    if protections:
        protected_text = stripped
        for protection in sorted(protections, key=lambda item: len(item.original), reverse=True):
            protected_text = protected_text.replace(protection.original, " ")
        protected_text = re.sub(r"[\s,.;:/@#()+\-_'\"%&]+", "", protected_text)
        if not protected_text:
            return True
    return False


def _has_effective_term_replacement(protections: list[Protection]) -> bool:
    return any(
        protection.category == "term" and protection.original != protection.replacement
        for protection in protections
    )


def _set_payload_value(payload: dict[str, Any], path: str, value: str) -> None:
    if path.startswith("report_fields."):
        key = path.split(".", 1)[1]
        fields = payload.setdefault("report_fields", {})
        if isinstance(fields, dict):
            fields[key] = value
        return

    match = re.match(r"([A-Za-z0-9_]+)\[(\d+)]\.([A-Za-z0-9_]+)$", path)
    if not match:
        return
    table_name, index_text, key = match.groups()
    rows = payload.get(table_name)
    index = int(index_text)
    if isinstance(rows, list) and 0 <= index < len(rows) and isinstance(rows[index], dict):
        rows[index][key] = value


def _translation_item(
    path: str,
    original: str,
    translated: str,
    language: str,
    translated_flag: bool,
    untranslated_tokens: list[str],
    term_replacements: list[dict[str, str]],
    warnings: list[str],
    error: str,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "path": path,
        "original_text": original,
        "language": language,
        "translated_text": translated,
        "translated": translated_flag,
        "untranslated_tokens": list(dict.fromkeys(untranslated_tokens)),
        "term_replacements": term_replacements,
        "warnings": warnings,
    }
    if error:
        item["error"] = error
    return item


def _term_record(source: str, replacement: str, term_id: str, target_language: str) -> dict[str, str]:
    return {
        "term_id": term_id,
        "source": source,
        "original": source,
        "target": target_language,
        "replacement": replacement,
    }


def _term_entry_from_object(item: object) -> TermEntry | None:
    if not isinstance(item, dict):
        return None
    values = {language: str(item.get(language, "") or "").strip() for language in LANGUAGES}
    if not any(values.values()):
        return None
    aliases_source = item.get("aliases") if isinstance(item.get("aliases"), dict) else {}
    aliases = {
        language: tuple(_unique_strings(aliases_source.get(language)))
        for language in LANGUAGES
    }
    stable_source = values.get("en") or values.get("zh") or values.get("es") or json.dumps(values, ensure_ascii=False)
    return TermEntry(
        id=str(item.get("id") or _stable_term_id(stable_source, values.get("zh", ""))).strip(),
        category=str(item.get("category") or "drilling").strip()[:60],
        zh=values["zh"],
        en=values["en"],
        es=values["es"],
        aliases=aliases,
        protected=bool(item.get("protected", True)),
        enabled=bool(item.get("enabled", True)),
        updated_at=str(item.get("updated_at") or ""),
    )


def _stable_term_id(source: str, target: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", source.strip().lower()).strip("-")[:40]
    if base:
        return f"term-{base}"
    return f"term-{abs(hash((source, target)))}"


def _string_tuple(value: object) -> tuple[str, ...]:
    return tuple(_unique_strings(value))


def _unique_strings(value: object) -> list[str]:
    raw = value if isinstance(value, list) else []
    result: list[str] = []
    seen: set[str] = set()
    for item in raw:
        text = str(item or "").strip()
        key = text.lower()
        if text and key not in seen:
            result.append(text)
            seen.add(key)
    return result


def _is_text_value(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return bool(text)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\n", " ")).strip()


SPANISH_HINTS = {
    "a", "al", "arriba", "bajando", "broca", "cementacion", "cementación", "circula", "circulacion",
    "circulación", "con", "continua", "continuar", "de", "del", "direccional", "el", "en", "fondo",
    "hueco", "la", "las", "lodo", "los", "para", "perfora", "perforacion", "perforación", "por",
    "pozo", "que", "reamer", "revestimiento", "saca", "sacando", "se", "sin", "tuberia", "tubería",
    "viaje", "y",
}


ENGLISH_HINTS = {
    "and", "bottom", "casing", "cementing", "circulate", "continue", "drill", "drilled", "drilling",
    "from", "hole", "in", "lost", "monitor", "of", "out", "pipe", "reaming", "section", "stuck",
    "the", "to", "tripping", "with",
}
