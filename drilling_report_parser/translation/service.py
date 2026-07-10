from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

from ..parser import ParseResult


DEFAULT_TERMS_PATH = Path(__file__).with_name("drilling_terms.json")
LANGUAGES = ("zh-CN", "en", "es")
TARGET_LANGUAGE = "zh-CN"
PROMPT_VERSION = "drilling-daily-v4"
TRANSLATABLE_REPORT_FIELDS = {
    "currentOps",
    "summary24h",
    "forecast24h",
    "mudComments",
    "incidentComments",
    "otherRemarks",
    "description",
    "safetyComments",
}
TRANSLATABLE_ROW_FIELDS = {
    "operation_details",
    "comments",
}


class TranslationError(RuntimeError):
    """Raised when the configured local translation engine cannot translate text."""


class TranslationEngine(Protocol):
    name: str

    def translate_items(self, items: list[dict[str, Any]], target_language: str, timeout_seconds: float) -> dict[str, str]:
        ...


@dataclass(frozen=True)
class TranslationConfig:
    engine: str = "ollama"
    target_language: str = TARGET_LANGUAGE
    target_languages: tuple[str, ...] = LANGUAGES
    terms_path: Path = DEFAULT_TERMS_PATH
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3.5:9b"
    ollama_temperature: float = 0.0
    timeout_seconds: float = 120.0

    @classmethod
    def from_env(cls) -> "TranslationConfig":
        terms_path = Path(os.environ.get("DRP_TRANSLATION_TERMS", str(DEFAULT_TERMS_PATH))).expanduser()
        return cls(
            engine=os.environ.get("DRP_TRANSLATION_ENGINE", "ollama").strip() or "ollama",
            target_language=normalize_language(os.environ.get("DRP_TRANSLATION_TARGET", TARGET_LANGUAGE)),
            target_languages=tuple(_target_languages_from_env()),
            terms_path=terms_path,
            ollama_url=os.environ.get("DRP_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/"),
            ollama_model=os.environ.get("DRP_OLLAMA_MODEL", "qwen3.5:9b").strip() or "qwen3.5:9b",
            ollama_temperature=float(os.environ.get("DRP_OLLAMA_TEMPERATURE", "0") or "0"),
            timeout_seconds=float(os.environ.get("DRP_TRANSLATION_TIMEOUT", "120") or "120"),
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
        attr = "zh" if normalize_language(language) == "zh-CN" else normalize_language(language)
        return str(getattr(self, attr, "") or "").strip()

    def source_values(self) -> list[tuple[str, str]]:
        values: list[tuple[str, str]] = []
        for language in ("zh", "en", "es"):
            value = str(getattr(self, language, "") or "").strip()
            if value:
                values.append((normalize_language(language), value))
            for alias in self.aliases.get(language, ()):
                alias_text = str(alias or "").strip()
                if alias_text:
                    values.append((normalize_language(language), alias_text))
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
                if source_value and zh_value:
                    entries.append(TermEntry(id=_stable_term_id(source_value, zh_value), zh=zh_value, en=source_value))
        return cls(
            entries=tuple(entries),
            acronyms=_string_tuple(protected.get("acronyms")),
            units=_string_tuple(protected.get("units")),
            proper_nouns=_string_tuple(protected.get("proper_nouns")),
        )


@dataclass(frozen=True)
class TextUnit:
    path: str
    text: str
    entity_type: str
    entity_id: str
    field_code: str


class OllamaTranslationEngine:
    name = "ollama"

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen3.5:9b",
        temperature: float = 0.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature

    def translate_items(self, items: list[dict[str, Any]], target_language: str, timeout_seconds: float) -> dict[str, str]:
        if not items:
            return {}
        if any(len(str(item.get("source_text", "") or "")) > 250 for item in items):
            return self._translate_with_long_text_splitting(items, target_language, timeout_seconds)
        try:
            translated = self._request_translation(items, target_language, timeout_seconds, strict=False)
        except Exception:
            translated = self._request_translation(items, target_language, timeout_seconds, strict=True)
        invalid_ids = [
            str(item.get("id", ""))
            for item in items
            if _translation_quality_error(
                str(item.get("source_text", "") or ""),
                str(translated.get(str(item.get("id", "")), "") or ""),
                target_language,
            )
        ]
        if invalid_ids:
            retry_items = [item for item in items if str(item.get("id", "")) in invalid_ids]
            translated.update(self._request_translation(retry_items, target_language, timeout_seconds, strict=True))
        quality_errors = {
            str(item.get("id", "")): _translation_quality_error(
                str(item.get("source_text", "") or ""),
                str(translated.get(str(item.get("id", "")), "") or ""),
                target_language,
            )
            for item in items
        }
        failed = {item_id: error for item_id, error in quality_errors.items() if error}
        if failed:
            details = "; ".join(f"{item_id}: {error}" for item_id, error in failed.items())
            raise TranslationError(f"Ollama returned low-quality translation ({details}).")
        return translated

    def _translate_with_long_text_splitting(
        self,
        items: list[dict[str, Any]],
        target_language: str,
        timeout_seconds: float,
    ) -> dict[str, str]:
        translated: dict[str, str] = {}
        for item in items:
            item_id = str(item.get("id", ""))
            parts = _split_translation_text(str(item.get("source_text", "") or ""))
            if len(parts) == 1:
                translated.update(self.translate_items([item], target_language, timeout_seconds))
                continue
            part_items = [
                {
                    **item,
                    "id": f"{item_id}::part-{index}",
                    "source_text": part,
                }
                for index, part in enumerate(parts)
            ]
            part_results: dict[str, str] = {}
            for chunk in _translation_chunks(part_items, max_chars=700):
                try:
                    part_results.update(self.translate_items(chunk, target_language, timeout_seconds))
                except Exception:
                    for part_item in chunk:
                        part_results.update(self.translate_items([part_item], target_language, timeout_seconds))
            translated_parts = [
                str(part_results.get(str(part_item["id"]), "") or "").strip()
                for part_item in part_items
            ]
            translated[item_id] = " ".join(part for part in translated_parts if part).strip()
        return translated

    def _request_translation(
        self,
        items: list[dict[str, Any]],
        target_language: str,
        timeout_seconds: float,
        *,
        strict: bool,
    ) -> dict[str, str]:
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "prompt": _ollama_batch_prompt(items, target_language, strict=strict),
            "options": {
                "temperature": self.temperature,
                "top_p": 0.2,
                "num_predict": 4096,
            },
        }
        data = _post_json(f"{self.base_url}/api/generate", payload, timeout_seconds)
        response = str(data.get("response", "") if isinstance(data, dict) else "")
        parsed = _json_object_from_text(response)
        raw_items = parsed.get("items")
        if not isinstance(raw_items, list):
            raise TranslationError("Ollama response missing items array.")
        return {
            str(item.get("id", "")): str(item.get("translated_text", "") or "")
            for item in raw_items
            if isinstance(item, dict)
        }


class NoopTranslationEngine:
    name = "noop"

    def translate_items(self, items: list[dict[str, Any]], target_language: str, timeout_seconds: float) -> dict[str, str]:
        del target_language, timeout_seconds
        return {str(item.get("id", "")): str(item.get("source_text", "") or "") for item in items}


class DrillingReportTranslator:
    def __init__(
        self,
        engine: TranslationEngine,
        terms: TermsConfig,
        target_language: str = TARGET_LANGUAGE,
        timeout_seconds: float = 120.0,
    ) -> None:
        self.engine = engine
        self.terms = terms
        self.target_language = normalize_language(target_language)
        self.timeout_seconds = timeout_seconds
        self._term_matchers = _compiled_term_matchers(terms.entries, self.target_language)

    def translate_report_payload(
        self,
        payload: dict[str, Any],
        *,
        record_id: str = "",
        target_languages: list[str] | tuple[str, ...] | None = None,
        on_progress: Callable[[str, int, int], None] | None = None,
    ) -> dict[str, Any]:
        source_payload = copy.deepcopy(payload)
        source_payload.pop("translation_content", None)
        record_id = record_id or str(source_payload.get("metadata", {}).get("record_id", "") or "")
        target_languages = [normalize_language(language) for language in (target_languages or [self.target_language])]
        units = iter_payload_text_units(source_payload, record_id=record_id)
        rows: list[dict[str, str]] = []
        warnings: list[str] = []
        for target_language in target_languages:
            rows.extend(self.translate_units(
                units,
                target_language,
                warnings,
                on_progress=(
                    (lambda completed, total, language=target_language: on_progress(language, completed, total))
                    if on_progress else None
                ),
            ))
        translated_payload = apply_translation_content(source_payload, rows, self.target_language)
        return {
            "metadata": {
                "source": "translation_content",
                "engine": self.engine.name,
                "target_language": self.target_language,
                "target_languages": target_languages,
                "prompt_version": PROMPT_VERSION,
                "generated_at": _now(),
                "item_count": len(rows),
                "translated_count": sum(1 for row in rows if row.get("translation_status") in {"COMPLETED", "NOT_REQUIRED"}),
                "warning_count": len(warnings),
            },
            "translation_content": rows,
            "translated_payload": translated_payload,
            "warnings": warnings,
        }

    def translate_parse_result(self, result: ParseResult) -> dict[str, Any]:
        payload = {
            "metadata": {"source_file": result.source_file},
            "report_fields": result.fields,
            **result.tables,
        }
        return self.translate_report_payload(payload)

    def translate_plain_text(self, text: str) -> dict[str, Any]:
        payload = {"metadata": {"record_id": "plain-text"}, "report_fields": {"text": text}}
        units = [TextUnit("report_fields.text", text, "daily_report", "plain-text", "report_fields.text")]
        rows = self.translate_units(units, self.target_language, [])
        return {
            "metadata": {"source": "plain_text_translation", "engine": self.engine.name, "target_language": self.target_language},
            "translation_content": rows,
            "translated_text": rows[0]["translated_text"] if rows else "",
            "translated_payload": apply_translation_content(payload, rows, self.target_language),
        }

    def translate_units(
        self,
        units: list[TextUnit],
        target_language: str,
        warnings: list[str],
        on_progress: Callable[[int, int], None] | None = None,
    ) -> list[dict[str, str]]:
        target_language = normalize_language(target_language)
        now = _now()
        rows: list[dict[str, str]] = []
        pending: list[dict[str, Any]] = []
        for unit in units:
            source_text = _clean_text(unit.text)
            if not source_text:
                continue
            source_language = detect_language(source_text)
            base = {
                "entity_type": unit.entity_type,
                "entity_id": unit.entity_id,
                "field_code": unit.field_code,
                "source_language": source_language,
                "target_language": target_language,
                "source_text": source_text,
                "source_hash": source_hash(source_text),
                "model_config_id": self.engine.name,
                "prompt_version": PROMPT_VERSION,
                "is_manual_modified": "",
                "created_at": now,
                "updated_at": now,
            }
            if source_language == target_language:
                rows.append({**base, "translated_text": source_text, "translation_status": "NOT_REQUIRED", "error_message": ""})
                continue
            pending.append({
                "id": str(len(pending)),
                "unit": unit,
                "base": base,
                "source_text": source_text,
                "source_language": source_language,
                "glossary": self._term_glossary(source_text, target_language),
            })

        completed_units = len(rows)
        if on_progress:
            on_progress(completed_units, len(units))

        for chunk in _translation_chunks(pending):
            try:
                translated = self.engine.translate_items(chunk, target_language, self.timeout_seconds)
            except Exception as exc:
                if len(chunk) > 1:
                    rows.extend(self._translate_items_one_by_one(chunk, target_language, warnings, str(exc)))
                else:
                    warnings.append(str(exc))
                    for item in chunk:
                        rows.append({**item["base"], "translated_text": "", "translation_status": "FAILED", "error_message": str(exc)})
            else:
                for item in chunk:
                    translated_text = str(translated.get(item["id"], "") or "").strip()
                    if translated_text:
                        translated_text = self._apply_term_replacements(translated_text)
                        rows.append({**item["base"], "translated_text": translated_text, "translation_status": "COMPLETED", "error_message": ""})
                    else:
                        rows.append({**item["base"], "translated_text": "", "translation_status": "FAILED", "error_message": "missing translated_text"})
            completed_units += len(chunk)
            if on_progress:
                on_progress(completed_units, len(units))
        return rows

    def _translate_items_one_by_one(
        self,
        chunk: list[dict[str, Any]],
        target_language: str,
        warnings: list[str],
        first_error: str,
    ) -> list[dict[str, str]]:
        warnings.append(first_error)
        rows: list[dict[str, str]] = []
        for item in chunk:
            try:
                translated = self.engine.translate_items([item], target_language, self.timeout_seconds)
            except Exception as exc:
                warnings.append(str(exc))
                rows.append({**item["base"], "translated_text": "", "translation_status": "FAILED", "error_message": str(exc)})
                continue
            translated_text = str(translated.get(item["id"], "") or "").strip()
            if translated_text:
                translated_text = self._apply_term_replacements(translated_text)
                rows.append({**item["base"], "translated_text": translated_text, "translation_status": "COMPLETED", "error_message": ""})
            else:
                rows.append({**item["base"], "translated_text": "", "translation_status": "FAILED", "error_message": "missing translated_text"})
        return rows

    def _term_glossary(self, text: str, target_language: str) -> list[dict[str, str]]:
        records: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for entry in self.terms.entries:
            if not entry.enabled:
                continue
            target = entry.value(target_language)
            if not target:
                continue
            for _, source_value in entry.source_values():
                if not source_value or not re.search(_term_regex(source_value), text, flags=re.IGNORECASE):
                    continue
                key = (source_value.lower(), target)
                if key in seen:
                    continue
                seen.add(key)
                records.append({"source": source_value, "target": target})
        return records[:30]

    def _apply_term_replacements(self, text: str) -> str:
        translated = text
        for pattern, replacement in self._term_matchers:
            translated = pattern.sub(replacement, translated)
        return _clean_translation_artifacts(translated)


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
        timeout_seconds=config.timeout_seconds,
    )


def build_engine(config: TranslationConfig) -> TranslationEngine:
    engine = config.engine.lower()
    if engine == "ollama":
        return OllamaTranslationEngine(
            base_url=config.ollama_url,
            model=config.ollama_model,
            temperature=config.ollama_temperature,
        )
    if engine in {"noop", "none"}:
        return NoopTranslationEngine()
    raise ValueError(f"Unsupported translation engine: {config.engine}. Use ollama or noop.")


def apply_translation_content(payload: dict[str, Any], rows: list[dict[str, Any]], target_language: str) -> dict[str, Any]:
    target_language = normalize_language(target_language)
    translated_payload = copy.deepcopy(payload)
    translated_payload.pop("translation_content", None)
    for row in rows:
        if normalize_language(row.get("target_language", "")) != target_language:
            continue
        if str(row.get("translation_status", "")) not in {"COMPLETED", "NOT_REQUIRED"}:
            continue
        text = str(row.get("translated_text", "") or "")
        if not text:
            continue
        path = field_code_to_path(str(row.get("field_code", "")), str(row.get("entity_id", "")))
        _set_payload_value(translated_payload, path, text)
    translated_payload["translation_content"] = rows
    return translated_payload


def iter_payload_text_units(payload: dict[str, Any], *, record_id: str = "") -> list[TextUnit]:
    record_id = record_id or str(payload.get("metadata", {}).get("record_id", "") or "")
    fields = payload.get("report_fields", {})
    units: list[TextUnit] = []
    if isinstance(fields, dict):
        for key in sorted(TRANSLATABLE_REPORT_FIELDS):
            value = fields.get(key)
            if _is_text_value(value):
                units.append(TextUnit(
                    path=f"report_fields.{key}",
                    text=str(value),
                    entity_type="daily_report",
                    entity_id=record_id,
                    field_code=f"report_fields.{key}",
                ))
    for section, rows in payload.items():
        if section in {"metadata", "report_fields", "translation_content"} or not isinstance(rows, list):
            continue
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            row_no = str(row.get("row_no") or index + 1)
            for key in sorted(TRANSLATABLE_ROW_FIELDS):
                value = row.get(key)
                if _is_text_value(value):
                    units.append(TextUnit(
                        path=f"{section}[{index}].{key}",
                        text=str(value),
                        entity_type=section,
                        entity_id=f"{record_id}:{section}:{row_no}",
                        field_code=f"{section}.{key}",
                    ))
    return units


def iter_parse_result_text_units(result: ParseResult) -> list[TextUnit]:
    payload = {"report_fields": result.fields, **result.tables}
    return iter_payload_text_units(payload)


def field_code_to_path(field_code: str, entity_id: str) -> str:
    if field_code.startswith("report_fields."):
        return field_code
    section, _, key = field_code.partition(".")
    try:
        row_no = int(str(entity_id).rsplit(":", 1)[1])
    except (IndexError, ValueError):
        row_no = 1
    return f"{section}[{max(row_no - 1, 0)}].{key}"


def normalize_language(value: object) -> str:
    language = str(value or "").strip().lower().replace("_", "-")
    if language in {"zh", "zh-cn", "cn", "中文"}:
        return "zh-CN"
    if language in {"en", "english", "eng"}:
        return "en"
    if language in {"es", "spanish", "spa"}:
        return "es"
    return "es" if language.startswith("es") else language or TARGET_LANGUAGE


def detect_language(text: str) -> str:
    value = str(text or "")
    if re.search(r"[\u4e00-\u9fff]", value):
        return "zh-CN"
    spanish_markers = (
        r"[ÁÉÍÓÚÜÑáéíóúüñ¿¡]|\b(?:con|para|desde|hasta|perfora|saca|bombea|circula|pozo|broca|"
        r"revestimiento|herramienta|incidentes?|sin|reportar|ultimas?|traslado|fluidos?|campamentos?|"
        r"personal|ingresa|servicio|aguas?|cortes|perforacion)\b"
    )
    if re.search(spanish_markers, value, flags=re.IGNORECASE):
        return "es"
    return "en"


def source_hash(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _target_languages_from_env() -> list[str]:
    raw = os.environ.get("DRP_TRANSLATION_TARGET_LANGUAGES", "zh-CN,en,es")
    languages: list[str] = []
    for item in raw.split(","):
        language = normalize_language(item)
        if language in LANGUAGES and language not in languages:
            languages.append(language)
    return languages or list(LANGUAGES)


def _post_json(url: str, payload: dict[str, Any], timeout_seconds: float) -> Any:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = str(exc)
        raise TranslationError(f"{url} returned HTTP {exc.code}: {detail[:200]}") from exc
    except urllib.error.URLError as exc:
        raise TranslationError(f"{url} is unavailable: {exc}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TranslationError(f"{url} returned non-JSON response.") from exc


def _ollama_batch_prompt(items: list[dict[str, Any]], target_language: str, *, strict: bool = False) -> str:
    compact_items = [
        {
            "id": item["id"],
            "source_language": item["source_language"],
            "source_text": item["source_text"],
            "glossary": item.get("glossary", []),
        }
        for item in items
    ]
    target = normalize_language(target_language)
    instruction = {
        "zh-CN": "将每个 source_text 中的西班牙语或英语自然语言完整翻译成简体中文。全大写的西班牙语或英语仍是正文，必须翻译。",
        "en": "Translate all Spanish or Chinese natural-language prose in every source_text completely into English. ALL-CAPS prose must also be translated.",
        "es": "Traduce completamente al español todo texto natural en chino o inglés de cada source_text. El texto en MAYÚSCULAS también debe traducirse.",
    }.get(target, f"Translate every source_text completely into {_language_label(target_language)}.")
    retry_rule = "上一次结果照抄了原文。本次必须翻译所有自然语言正文。" if strict and target == "zh-CN" else (
        "The previous result copied source prose. This time translate every natural-language phrase." if strict else ""
    )
    return (
        "/no_think\n"
        "你是石油钻井日报专业翻译器。\n"
        f"{instruction}\n"
        "不得总结、删减、解释或添加说明。保留井名、公司名、设备型号、专业缩写、日期、数字和单位，并应用每条记录的 glossary。\n"
        f"{retry_rule}\n"
        "只返回严格 JSON，格式为：{\"items\":[{\"id\":\"0\",\"translated_text\":\"译文\"}]}。每个输入 id 必须返回一条。\n"
        f"Input JSON:\n{json.dumps({'items': compact_items}, ensure_ascii=False)}"
    )


def _translation_quality_error(source_text: str, translated_text: str, target_language: str) -> str:
    source = _clean_text(source_text)
    translated = _clean_text(translated_text)
    if not translated:
        return "missing translated_text"
    if source.casefold() == translated.casefold():
        return "source text was returned unchanged"
    if normalize_language(target_language) == "zh-CN" and detect_language(source) != "zh-CN":
        cjk_count = len(re.findall(r"[\u4e00-\u9fff]", translated))
        latin_count = len(re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", translated))
        if cjk_count < 2 or (latin_count >= 40 and cjk_count / max(cjk_count + latin_count, 1) < 0.12):
            return "Chinese output still contains excessive source-language prose"
    return ""


def _json_object_from_text(text: str) -> dict[str, Any]:
    cleaned = re.sub(r"<think>.*?</think>", "", str(text or ""), flags=re.IGNORECASE | re.DOTALL).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise TranslationError("Model returned JSON that is not an object.")
    return data


def _translation_chunks(items: list[dict[str, Any]], max_chars: int = 900) -> list[list[dict[str, Any]]]:
    chunks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_chars = 0
    for item in items:
        item_chars = len(str(item.get("source_text", ""))) + len(json.dumps(item.get("glossary", []), ensure_ascii=False))
        if current and current_chars + item_chars > max_chars:
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(item)
        current_chars += item_chars
    if current:
        chunks.append(current)
    return chunks


def _split_translation_text(text: str, max_chars: int = 180) -> list[str]:
    remaining = _clean_text(text)
    parts: list[str] = []
    while len(remaining) > max_chars:
        window = remaining[: max_chars + 1]
        break_positions = [
            window.rfind(marker)
            for marker in (". ", "; ", "? ", "! ", " -", " +", " *")
        ]
        split_at = max(break_positions)
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
    section, index_text, key = match.groups()
    rows = payload.get(section)
    index = int(index_text)
    if isinstance(rows, list) and 0 <= index < len(rows) and isinstance(rows[index], dict):
        rows[index][key] = value


def _compiled_term_matchers(entries: tuple[TermEntry, ...], target_language: str) -> list[tuple[re.Pattern[str], str]]:
    matchers: list[tuple[re.Pattern[str], str]] = []
    for entry in entries:
        if not entry.enabled:
            continue
        replacement = entry.value(target_language)
        if not replacement:
            continue
        for _, source_value in entry.source_values():
            if source_value and source_value != replacement:
                matchers.append((re.compile(_term_regex(source_value), re.IGNORECASE), replacement))
    return sorted(matchers, key=lambda item: len(item[0].pattern), reverse=True)


def _term_regex(term: str) -> str:
    escaped = re.escape(term).replace(r"\ ", r"\s+")
    return rf"(?<![A-Za-z0-9_/-]){escaped}(?![A-Za-z0-9_/-])"


def _clean_translation_artifacts(text: str) -> str:
    duplicate_note = re.compile(
        r"([A-Za-z\u4e00-\u9fff][A-Za-z0-9\u4e00-\u9fff/ -]{0,30}?)\s*[（(]\s*([A-Za-z\u4e00-\u9fff][A-Za-z0-9\u4e00-\u9fff/ -]{0,30}?)\s*[）)]"
    )

    def replace_duplicate(match: re.Match[str]) -> str:
        left = match.group(1).strip()
        inner = match.group(2).strip()
        return left if left == inner or left.endswith(inner) else match.group(0)

    return re.sub(r"\s{2,}", " ", duplicate_note.sub(replace_duplicate, text)).strip()


def _is_text_value(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and bool(re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\u4e00-\u9fff]", value))


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\r", "\n")).strip()


def _language_label(language: str) -> str:
    return {
        "zh-CN": "Simplified Chinese",
        "en": "English",
        "es": "Spanish",
    }.get(normalize_language(language), str(language))


def _term_entry_from_object(item: object) -> TermEntry | None:
    if not isinstance(item, dict):
        return None
    aliases_source = item.get("aliases", {}) if isinstance(item.get("aliases"), dict) else {}
    aliases: dict[str, tuple[str, ...]] = {}
    for language in ("zh", "en", "es"):
        raw_aliases = aliases_source.get(language, [])
        aliases[language] = tuple(str(alias or "").strip() for alias in raw_aliases if str(alias or "").strip()) if isinstance(raw_aliases, list) else ()
    values = {language: str(item.get(language, "") or "").strip() for language in ("zh", "en", "es")}
    if not any(values.values()):
        return None
    id_values = [value for value in values.values() if value]
    return TermEntry(
        id=str(item.get("id", "") or _stable_term_id(id_values[0], id_values[1] if len(id_values) > 1 else "")),
        category=str(item.get("category", "drilling") or "drilling"),
        zh=values["zh"],
        en=values["en"],
        es=values["es"],
        aliases=aliases,
        protected=bool(item.get("protected", True)),
        enabled=bool(item.get("enabled", True)),
        updated_at=str(item.get("updated_at", "") or ""),
    )


def _stable_term_id(source: str, target: str = "") -> str:
    digest = hashlib.sha1(f"{source}|{target}".encode("utf-8")).hexdigest()[:12]
    return f"term-{digest}"


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item or "").strip() for item in value if str(item or "").strip())


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
