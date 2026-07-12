from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

from ..parser import ParseResult
from ..text_structure import (
    TextPart,
    join_translated_parts,
    normalize_inline,
    normalize_multiline,
    normalize_translation_paragraph,
    split_preserving_layout,
)


DEFAULT_TERMS_PATH = Path(__file__).with_name("drilling_terms.json")
LANGUAGES = ("zh-CN",)
TARGET_LANGUAGE = "zh-CN"
PROMPT_VERSION = "drilling-daily-v7"
DEFAULT_SYSTEM_PROMPT = "你是石油钻完井日报专业翻译器，熟悉钻井、完井、修井和搬迁作业术语。"
DEFAULT_TRANSLATION_INSTRUCTION = "不得总结、删减、解释或添加说明；保持原文信息顺序和技术含义。"
DEFAULT_OLLAMA_CHUNK_CHARS = 6000
DEFAULT_OPENAI_COMPATIBLE_CHUNK_CHARS = 2500
TRANSLATION_PIPELINE_VERSION = "report-context-v8-coherent-protected-chunks"
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
REPORT_FIELD_TRANSLATION_ORDER = (
    "currentOps",
    "summary24h",
    "forecast24h",
    "description",
    "mudComments",
    "incidentComments",
    "safetyComments",
    "otherRemarks",
)
ROW_FIELD_TRANSLATION_ORDER = ("operation_details", "comments")


class TranslationError(RuntimeError):
    """Raised when the configured local translation engine cannot translate text."""


class TranslationTransportError(TranslationError):
    """A provider/network failure that must not be multiplied into per-item calls."""

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


class TranslationCircuitOpen(TranslationTransportError):
    def __init__(self, message: str, *, retry_after_seconds: float) -> None:
        super().__init__(message, retryable=True)
        self.retry_after_seconds = max(0.0, float(retry_after_seconds))


class TranslationQualityError(TranslationError):
    """The provider returned a response, but its translation failed validation."""


class TranslationResponseError(TranslationError):
    """The provider response was truncated or could not be parsed as structured JSON."""


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
    openai_base_url: str = ""
    openai_api_key: str = ""
    openai_model: str = ""
    openai_temperature: float = 0.0
    timeout_seconds: float = 120.0
    model_config_id: str = ""
    retry_count: int = 2
    chunk_max_chars: int = 0
    thinking_mode: str = "auto"
    request_options: dict[str, Any] = field(default_factory=dict)

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
            openai_base_url=os.environ.get("DRP_OPENAI_COMPATIBLE_URL", "").rstrip("/"),
            openai_api_key=os.environ.get("DRP_OPENAI_COMPATIBLE_API_KEY", ""),
            openai_model=os.environ.get("DRP_OPENAI_COMPATIBLE_MODEL", "").strip(),
            openai_temperature=float(os.environ.get("DRP_OPENAI_COMPATIBLE_TEMPERATURE", "0") or "0"),
            timeout_seconds=float(os.environ.get("DRP_TRANSLATION_TIMEOUT", "120") or "120"),
            model_config_id=os.environ.get("DRP_TRANSLATION_MODEL_CONFIG_ID", "").strip(),
            retry_count=max(0, int(os.environ.get("DRP_TRANSLATION_RETRY_COUNT", "2") or "2")),
            chunk_max_chars=max(0, int(os.environ.get("DRP_TRANSLATION_CHUNK_CHARS", "0") or "0")),
            thinking_mode=_normalize_thinking_mode(os.environ.get("DRP_TRANSLATION_THINKING_MODE", "auto")),
        )


@dataclass(frozen=True)
class TranslationTuningConfig:
    report_fields: tuple[str, ...] = tuple(sorted(TRANSLATABLE_REPORT_FIELDS))
    row_fields: tuple[str, ...] = tuple(sorted(TRANSLATABLE_ROW_FIELDS))
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    translation_instruction: str = DEFAULT_TRANSLATION_INSTRUCTION
    protect_numbers: bool = True
    protect_units: bool = True
    protect_acronyms: bool = True
    protect_proper_nouns: bool = True
    version: str = PROMPT_VERSION
    scope_rules: tuple[tuple[str, str, str], ...] = ()

    @classmethod
    def from_data(cls, data: object) -> "TranslationTuningConfig":
        source = data if isinstance(data, dict) else {}
        raw_fields = source.get("scope_rules") if isinstance(source.get("scope_rules"), list) else source.get("field_policies") if isinstance(source.get("field_policies"), list) else []
        enabled_codes = {
            str(item.get("field_code", "") or "")
            for item in raw_fields
            if isinstance(item, dict) and item.get("enabled", True)
        }
        report_fields = tuple(sorted(
            code.split(".", 1)[1]
            for code in enabled_codes
            if code.startswith("report_fields.") and "." in code
        ))
        row_fields = tuple(sorted(
            code.split(".", 1)[1]
            for code in enabled_codes
            if code.startswith("rows.") and "." in code
        ))
        if not raw_fields:
            report_fields = tuple(sorted(TRANSLATABLE_REPORT_FIELDS))
            row_fields = tuple(sorted(TRANSLATABLE_ROW_FIELDS))
        scope_rules: list[tuple[str, str, str]] = []
        for item in raw_fields:
            if not isinstance(item, dict) or not item.get("enabled", True):
                continue
            field_code = str(item.get("field_code", "") or "")
            report_type = str(item.get("report_type", "*") or "*").strip().lower()
            section = str(item.get("section", "") or "").strip()
            field_name = str(item.get("field_name", "") or "").strip()
            if not section or not field_name:
                prefix, _, suffix = field_code.partition(".")
                if prefix == "report_fields":
                    section, field_name = "report_fields", suffix
                elif prefix == "rows":
                    section, field_name = "*", suffix
                elif prefix and suffix:
                    section, field_name = prefix, suffix
            if section and field_name:
                scope_rules.append((report_type, section, field_name))
        prompt = source.get("prompt") if isinstance(source.get("prompt"), dict) else {}
        protections = source.get("protections") if isinstance(source.get("protections"), dict) else {}
        return cls(
            report_fields=report_fields,
            row_fields=row_fields,
            system_prompt=str(prompt.get("system_prompt", "") or DEFAULT_SYSTEM_PROMPT).strip(),
            translation_instruction=str(prompt.get("translation_instruction", "") or DEFAULT_TRANSLATION_INSTRUCTION).strip(),
            protect_numbers=bool(protections.get("numbers", True)),
            protect_units=bool(protections.get("units", True)),
            protect_acronyms=bool(protections.get("acronyms", True)),
            protect_proper_nouns=bool(protections.get("proper_nouns", True)),
            version=str(source.get("version", "") or PROMPT_VERSION).strip(),
            scope_rules=tuple(sorted(set(scope_rules))),
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
        thinking_mode: str = "disabled",
        request_options: dict[str, Any] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.thinking_mode = _normalize_thinking_mode(thinking_mode)
        self.request_options = _safe_request_options(request_options)

    def translate_items(self, items: list[dict[str, Any]], target_language: str, timeout_seconds: float) -> dict[str, str]:
        if not items:
            return {}
        if any(len(str(item.get("source_text", "") or "")) > 6000 for item in items):
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
            raise TranslationQualityError(f"Ollama returned low-quality translation ({details}).")
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
            parts = split_preserving_layout(str(item.get("source_text", "") or ""), 3000)
            if len(parts) == 1:
                translated.update(self.translate_items([item], target_language, timeout_seconds))
                continue
            part_items = [
                _translation_part_item(item, f"{item_id}::part-{index}", part.text)
                for index, part in enumerate(parts)
            ]
            part_results: dict[str, str] = {}
            for chunk in _translation_chunks(part_items, max_chars=6000):
                try:
                    part_results.update(self.translate_items(chunk, target_language, timeout_seconds))
                except Exception:
                    for part_item in chunk:
                        part_results.update(self.translate_items([part_item], target_language, timeout_seconds))
            translated_parts = [
                str(part_results.get(str(part_item["id"]), "") or "").strip()
                for part_item in part_items
            ]
            translated[item_id] = join_translated_parts(parts, translated_parts)
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
            "think": self.thinking_mode == "enabled",
            "prompt": _ollama_batch_prompt(items, target_language, strict=strict),
            "options": {
                "temperature": self.temperature,
                "top_p": 0.2,
                "num_predict": 4096,
            },
        }
        payload.update(self.request_options)
        payload["model"] = self.model
        payload["prompt"] = _ollama_batch_prompt(items, target_language, strict=strict)
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


class OpenAICompatibleTranslationEngine:
    name = "openai-compatible"

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "",
        temperature: float = 0.0,
        thinking_mode: str = "auto",
        request_options: dict[str, Any] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.thinking_mode = _normalize_thinking_mode(thinking_mode)
        self.request_options = _safe_request_options(request_options)

    def translate_items(self, items: list[dict[str, Any]], target_language: str, timeout_seconds: float) -> dict[str, str]:
        if not items:
            return {}
        if any(len(str(item.get("source_text", "") or "")) > 3000 for item in items):
            return self._translate_with_long_text_splitting(items, target_language, timeout_seconds)
        try:
            translated = self._request_translation(items, target_language, timeout_seconds, strict=False)
        except TranslationResponseError:
            try:
                translated = self._request_translation(items, target_language, timeout_seconds, strict=True)
            except TranslationResponseError as exc:
                raise TranslationQualityError(str(exc)) from exc
        invalid_ids = {
            str(item.get("id", ""))
            for item in items
            if _openai_item_quality_error(
                item,
                str(translated.get(str(item.get("id", "")), "") or ""),
                target_language,
            )
        }
        if invalid_ids:
            # A successful batch response can still contain copied source text or
            # otherwise unusable translations. Retrying the same batch and prompt
            # tends to reproduce that response (and makes long batches more likely
            # to time out), so recover only the invalid items with the strict prompt.
            for item in items:
                item_id = str(item.get("id", ""))
                if item_id not in invalid_ids:
                    continue
                retry_result = self._request_translation(
                    [item],
                    target_language,
                    timeout_seconds,
                    strict=True,
                )
                translated[item_id] = str(retry_result.get(item_id, "") or "")
                if _openai_item_quality_error(item, translated[item_id], target_language):
                    protected_item, protected_values = _surgically_protect_values(item)
                    if protected_values:
                        protected_result = self._request_translation(
                            [protected_item],
                            target_language,
                            timeout_seconds,
                            strict=True,
                        )
                        translated[item_id] = _restore_surgically_protected_values(
                            str(protected_result.get(item_id, "") or ""),
                            protected_values,
                        )

        failed = {
            str(item.get("id", "")): _openai_item_quality_error(
                item,
                str(translated.get(str(item.get("id", "")), "") or ""),
                target_language,
            )
            for item in items
        }
        failed = {item_id: error for item_id, error in failed.items() if error}
        if failed:
            details = "; ".join(f"{item_id}: {error}" for item_id, error in failed.items())
            raise TranslationQualityError(f"OpenAI-compatible model returned low-quality translation ({details}).")
        return translated

    def _translate_with_long_text_splitting(
        self,
        items: list[dict[str, Any]],
        target_language: str,
        timeout_seconds: float,
    ) -> dict[str, str]:
        expanded: list[dict[str, Any]] = []
        part_ids: dict[str, list[str]] = {}
        item_parts: dict[str, list[TextPart]] = {}
        for item in items:
            item_id = str(item.get("id", ""))
            parts = split_preserving_layout(str(item.get("source_text", "") or ""), 2000)
            ids: list[str] = []
            for index, part in enumerate(parts):
                part_id = f"{item_id}::part-{index}"
                ids.append(part_id)
                expanded.append(_translation_part_item(item, part_id, part.text))
            part_ids[item_id] = ids
            item_parts[item_id] = parts

        part_results: dict[str, str] = {}
        for chunk in _translation_chunks(expanded, max_chars=2500):
            part_results.update(self.translate_items(chunk, target_language, timeout_seconds))
        return {
            item_id: join_translated_parts(
                item_parts[item_id],
                [str(part_results.get(part_id, "") or "") for part_id in ids],
            )
            for item_id, ids in part_ids.items()
        }

    def _request_translation(
        self,
        items: list[dict[str, Any]],
        target_language: str,
        timeout_seconds: float,
        *,
        strict: bool,
    ) -> dict[str, str]:
        messages = [
            {"role": "system", "content": _prompt_system_message(items)},
            {"role": "user", "content": _openai_batch_prompt(items, target_language, strict=strict)},
        ]
        if self.thinking_mode == "disabled" and _needs_qwen_no_think_prefill(self.base_url, self.model):
            # LM Studio currently ignores per-request chat_template_kwargs for
            # Qwen3.5. An empty completed think block is the equivalent assistant
            # prefill and makes the model continue directly with the final answer.
            messages.append({"role": "assistant", "content": "<think>\n\n</think>\n\n"})
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": _translation_output_token_budget(items),
            "messages": messages,
        }
        if self.thinking_mode != "auto":
            if _is_deepseek_endpoint(self.base_url, self.model):
                payload["thinking"] = {"type": self.thinking_mode}
            else:
                payload["chat_template_kwargs"] = {"enable_thinking": self.thinking_mode == "enabled"}
        payload.update(self.request_options)
        data = _post_json(
            _chat_completions_url(self.base_url),
            payload,
            timeout_seconds,
            headers=_auth_headers(self.api_key),
        )
        content = _chat_content(data)
        choices = data.get("choices") if isinstance(data, dict) else []
        first_choice = choices[0] if isinstance(choices, list) and choices and isinstance(choices[0], dict) else {}
        if str(first_choice.get("finish_reason", "") or "").lower() == "length":
            raise TranslationResponseError("OpenAI-compatible response was truncated by the output-token limit.")
        try:
            parsed = _json_object_from_text(content)
        except (json.JSONDecodeError, TranslationError) as exc:
            raise TranslationResponseError(f"OpenAI-compatible response was not valid JSON: {exc}") from exc
        raw_items = parsed.get("items")
        if not isinstance(raw_items, list):
            raise TranslationError("OpenAI-compatible response missing items array.")
        translated = {
            str(item.get("id", "")): str(item.get("translated_text", "") or "")
            for item in raw_items
            if isinstance(item, dict)
        }
        return translated


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
        model_config_id: str = "",
        retry_count: int = 2,
        tuning: TranslationTuningConfig | None = None,
        chunk_max_chars: int = 0,
        telemetry: Callable[[dict[str, Any]], None] | None = None,
        translation_memory: dict[str, str] | None = None,
    ) -> None:
        self.engine = engine
        self.terms = terms
        self.target_language = normalize_language(target_language)
        self.timeout_seconds = timeout_seconds
        self.model_config_id = model_config_id or engine.name
        self.retry_count = max(0, retry_count)
        self.tuning = tuning or TranslationTuningConfig()
        self.chunk_max_chars = _translation_chunk_max_chars(engine.name, chunk_max_chars)
        self._term_matchers = _compiled_term_matchers(terms.entries, self.target_language)
        self._term_source_matchers = _compiled_glossary_matchers(terms.entries)
        self._protected_acronym_matchers = _compiled_literal_matchers(terms.acronyms)
        self._protected_unit_matchers = _compiled_literal_matchers(terms.units, unit=True)
        self._protected_proper_noun_matchers = _compiled_literal_matchers(terms.proper_nouns)
        self._protected_measurement_matcher = _compiled_measurement_matcher(terms.units)
        self._term_glossary_cache: dict[tuple[str, str], list[dict[str, str]]] = {}
        model_identity = f"{self.engine.name}:{getattr(self.engine, 'model', '')}:{self.model_config_id}"
        self.prompt_version = translation_memory_version(terms, self.tuning, self.target_language, model_identity)
        self.translation_memory = dict(translation_memory or {})
        self.telemetry = telemetry

    def _emit_telemetry(self, event: str, **fields: Any) -> None:
        if not self.telemetry:
            return
        try:
            self.telemetry({"event": event, **fields})
        except Exception:
            pass

    def translate_report_payload(
        self,
        payload: dict[str, Any],
        *,
        record_id: str = "",
        target_languages: list[str] | tuple[str, ...] | None = None,
        on_progress: Callable[[str, int, int], None] | None = None,
        on_rows: Callable[[str, list[dict[str, str]]], None] | None = None,
    ) -> dict[str, Any]:
        source_payload = copy.deepcopy(payload)
        source_payload.pop("translation_content", None)
        record_id = record_id or str(source_payload.get("metadata", {}).get("record_id", "") or "")
        target_languages = [normalize_language(language) for language in (target_languages or [self.target_language])]
        units = iter_payload_text_units(
            source_payload,
            record_id=record_id,
            report_fields=set(self.tuning.report_fields),
            row_fields=set(self.tuning.row_fields),
            scope_rules=set(self.tuning.scope_rules) if self.tuning.scope_rules else None,
        )
        report_context = _report_translation_context(source_payload, record_id)
        self._emit_telemetry(
            "payload_units",
            record_id=record_id,
            unit_count=len(units),
            source_chars=sum(len(unit.text or "") for unit in units),
            target_languages=target_languages,
        )
        rows: list[dict[str, str]] = []
        warnings: list[str] = []
        for target_language in target_languages:
            rows.extend(self.translate_units(
                units,
                target_language,
                warnings,
                report_context=report_context,
                on_progress=(
                    (lambda completed, total, language=target_language: on_progress(language, completed, total))
                    if on_progress else None
                ),
                on_rows=(
                    (lambda completed_rows, language=target_language: on_rows(language, completed_rows))
                    if on_rows else None
                ),
            ))
        translated_payload = apply_translation_content(source_payload, rows, self.target_language)
        return {
            "metadata": {
                "source": "translation_content",
                "engine": self.engine.name,
                "target_language": self.target_language,
                "target_languages": target_languages,
                "prompt_version": self.prompt_version,
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

    def translate_text_batch(self, texts: list[str], target_language: str | None = None) -> list[dict[str, str]]:
        language = normalize_language(target_language or self.target_language)
        units = [
            TextUnit(
                path=f"batch[{index}]",
                text=str(text or ""),
                entity_type="translation_test",
                entity_id=f"translation-test:{index}",
                field_code="translation_test.text",
            )
            for index, text in enumerate(texts)
            if str(text or "").strip()
        ]
        return self.translate_units(units, language, [])

    def translate_units(
        self,
        units: list[TextUnit],
        target_language: str,
        warnings: list[str],
        report_context: dict[str, Any] | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        on_rows: Callable[[list[dict[str, str]]], None] | None = None,
    ) -> list[dict[str, str]]:
        target_language = normalize_language(target_language)
        now = _now()
        rows: list[dict[str, str]] = []
        pending: list[dict[str, Any]] = []
        prepare_started = time.monotonic()
        glossary_seconds = 0.0
        glossary_hits = 0
        source_chars = 0
        for unit in units:
            source_text = _clean_text(unit.text)
            if not source_text:
                continue
            source_chars += len(source_text)
            source_language = detect_language(source_text)
            base = {
                "entity_type": unit.entity_type,
                "entity_id": unit.entity_id,
                "field_code": unit.field_code,
                "source_language": source_language,
                "target_language": target_language,
                "source_text": source_text,
                "source_hash": source_hash(source_text),
                "model_config_id": self.model_config_id,
                "prompt_version": self.prompt_version,
                "is_manual_modified": "",
                "created_at": now,
                "updated_at": now,
            }
            if not text_needs_translation(source_text, target_language):
                rows.append({**base, "translated_text": _normalize_item_layout(unit.field_code, source_text), "translation_status": "NOT_REQUIRED", "error_message": ""})
                continue
            memory_text = str(self.translation_memory.get(base["source_hash"], "") or "").strip()
            if memory_text and not _translation_quality_error(source_text, memory_text, target_language):
                rows.append({**base, "translated_text": _normalize_item_layout(unit.field_code, memory_text), "translation_status": "COMPLETED", "error_message": ""})
                self._emit_telemetry("memory_hit", target_language=target_language, field_code=unit.field_code, source_chars=len(source_text))
                continue
            glossary_started = time.monotonic()
            glossary = self._term_glossary(source_text, target_language)
            model_source_text = _normalize_item_layout(unit.field_code, source_text)
            protected_text, protected_tokens = self._protect_source_text(model_source_text, target_language)
            preserve_terms = self._preserve_terms(source_text, glossary)
            protected_source_terms = {
                normalize_inline(item.get("source", "")).casefold()
                for item in protected_tokens
                if isinstance(item, dict) and normalize_inline(item.get("source", ""))
            }
            preserve_terms = [
                term for term in preserve_terms
                if normalize_inline(term).casefold() not in protected_source_terms
            ]
            remaining_prose = _PROTECTED_PLACEHOLDER_PATTERN.sub("", protected_text)
            if not text_needs_translation(remaining_prose, target_language):
                deterministic_text = protected_text
                for token_data in protected_tokens:
                    token = str(token_data.get("token", "") or "")
                    replacement = str(token_data.get("replacement", "") or "")
                    if token:
                        deterministic_text = deterministic_text.replace(token, replacement)
                deterministic_text = _normalize_item_layout(unit.field_code, self._apply_term_replacements_preserving_units(deterministic_text))
                status = "COMPLETED" if deterministic_text != source_text else "NOT_REQUIRED"
                rows.append({**base, "translated_text": deterministic_text, "translation_status": status, "error_message": ""})
                continue
            glossary_seconds += time.monotonic() - glossary_started
            glossary_hits += len(glossary)
            pending.append({
                "id": str(len(pending)),
                "unit": unit,
                "base": base,
                "source_text": protected_text,
                "monitor_source_text": source_text,
                "source_language": source_language,
                "glossary": glossary,
                "preserve_terms": preserve_terms,
                "field_code": unit.field_code,
                "paragraph_layout": _uses_paragraph_layout(unit.field_code),
                "context_group": _translation_context_group(unit),
                "prompt_context": self._prompt_context(protected_tokens, report_context),
                "protected_tokens": protected_tokens,
            })

        completed_units = len(rows)
        if rows and on_rows:
            on_rows(list(rows))
        if on_progress:
            on_progress(completed_units, len(units))

        chunks = _semantic_translation_chunks(pending, max_chars=self.chunk_max_chars)
        self._emit_telemetry(
            "language_prepare",
            target_language=target_language,
            unit_count=len(units),
            pending_count=len(pending),
            not_required_count=len(rows),
            chunk_count=len(chunks),
            chunk_max_chars=self.chunk_max_chars,
            source_chars=source_chars,
            glossary_hits=glossary_hits,
            glossary_ms=round(glossary_seconds * 1000),
            elapsed_ms=round((time.monotonic() - prepare_started) * 1000),
        )

        for chunk_index, chunk in enumerate(chunks, start=1):
            chunk_started = time.monotonic()
            chunk_rows: list[dict[str, str]] = []
            self._emit_telemetry(
                "chunk_start",
                target_language=target_language,
                chunk_index=chunk_index,
                chunk_count=len(chunks),
                item_count=len(chunk),
                source_chars=sum(len(str(item.get("source_text", "") or "")) for item in chunk),
                glossary_count=sum(len(item.get("glossary", []) or []) for item in chunk),
            )
            try:
                translated = self._translate_with_retries(chunk, target_language)
            except Exception as exc:
                self._emit_telemetry(
                    "chunk_error",
                    target_language=target_language,
                    chunk_index=chunk_index,
                    chunk_count=len(chunks),
                    item_count=len(chunk),
                    elapsed_ms=round((time.monotonic() - chunk_started) * 1000),
                    error=str(exc)[:500],
                    fallback_one_by_one=len(chunk) > 1,
                )
                if len(chunk) > 1 and _allows_item_fallback(exc):
                    chunk_rows.extend(self._translate_items_one_by_one(chunk, target_language, warnings, str(exc)))
                else:
                    warnings.append(str(exc))
                    for item in chunk:
                        chunk_rows.append({**item["base"], "translated_text": "", "translation_status": "FAILED", "error_message": str(exc)})
            else:
                for item in chunk:
                    translated_text = str(translated.get(item["id"], "") or "").strip()
                    if translated_text:
                        translated_text = _normalize_item_layout(item.get("field_code", ""), translated_text)
                        chunk_rows.append({**item["base"], "translated_text": translated_text, "translation_status": "COMPLETED", "error_message": ""})
                    else:
                        chunk_rows.append({
                            **item["base"],
                            "translated_text": "",
                            "translation_status": "FAILED",
                            "error_message": str(item.get("translation_error", "") or "missing translated_text"),
                        })
                self._emit_telemetry(
                    "chunk_complete",
                    target_language=target_language,
                    chunk_index=chunk_index,
                    chunk_count=len(chunks),
                    item_count=len(chunk),
                    translated_count=len([item for item in chunk if translated.get(item["id"])]),
                    elapsed_ms=round((time.monotonic() - chunk_started) * 1000),
                )
            rows.extend(chunk_rows)
            if chunk_rows and on_rows:
                on_rows(list(chunk_rows))
            completed_units += len(chunk)
            if on_progress:
                on_progress(completed_units, len(units))
        return rows

    def prompt_preview(self, text: str, target_language: str) -> str:
        source_text = _clean_text(text)
        protected_text, protected_tokens = self._protect_source_text(source_text, target_language)
        item = {
            "id": "0",
            "source_language": detect_language(source_text),
            "source_text": protected_text,
            "monitor_source_text": source_text,
            "glossary": self._term_glossary(source_text, target_language),
            "prompt_context": self._prompt_context(protected_tokens),
            "protected_tokens": protected_tokens,
        }
        if str(self.engine.name or "").lower() == "openai-compatible":
            return (
                f"System:\n{_prompt_system_message([item])}\n\n"
                f"User:\n{_openai_batch_prompt([item], target_language, strict=False)}"
            )
        return _ollama_batch_prompt([item], target_language, strict=False)

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
                translated = self._translate_with_retries([item], target_language)
            except Exception as exc:
                warnings.append(str(exc))
                rows.append({**item["base"], "translated_text": "", "translation_status": "FAILED", "error_message": str(exc)})
                continue
            translated_text = str(translated.get(item["id"], "") or "").strip()
            if translated_text:
                translated_text = _normalize_item_layout(item.get("field_code", ""), translated_text)
                rows.append({**item["base"], "translated_text": translated_text, "translation_status": "COMPLETED", "error_message": ""})
            else:
                rows.append({**item["base"], "translated_text": "", "translation_status": "FAILED", "error_message": "missing translated_text"})
        return rows

    def _translate_with_retries(self, items: list[dict[str, Any]], target_language: str) -> dict[str, str]:
        last_error: Exception | None = None
        source_preview = " | ".join(str(item.get("monitor_source_text", item.get("source_text", "")) or "").strip() for item in items if item.get("source_text"))[:600]
        for attempt in range(self.retry_count + 1):
            started = time.monotonic()
            self._emit_telemetry(
                "model_request_start",
                target_language=target_language,
                attempt=attempt + 1,
                max_attempts=self.retry_count + 1,
                item_count=len(items),
                source_chars=sum(len(str(item.get("source_text", "") or "")) for item in items),
                engine=self.engine.name,
                model_config_id=self.model_config_id,
                source_preview=source_preview,
            )
            try:
                raw_result = self._translate_engine_items(items, target_language)
                result, invalid = self._restore_protected_items_partial(items, raw_result)
                if invalid and len(items) > 1:
                    self._emit_telemetry(
                        "partial_retry",
                        target_language=target_language,
                        item_count=len(items),
                        retry_item_count=len(invalid),
                        valid_item_count=len(result),
                    )
                    for item in items:
                        item_id = str(item.get("id", ""))
                        if item_id in invalid:
                            try:
                                result.update(self._translate_with_retries([item], target_language))
                            except Exception as exc:
                                item["translation_error"] = str(exc)
                elif invalid:
                    raise TranslationError(invalid[str(items[0].get("id", ""))])
                self._emit_telemetry(
                    "model_request_complete",
                    target_language=target_language,
                    attempt=attempt + 1,
                    item_count=len(items),
                    translated_count=len(result),
                    elapsed_ms=round((time.monotonic() - started) * 1000),
                    engine=self.engine.name,
                    model_config_id=self.model_config_id,
                    source_preview=source_preview,
                    response_preview=" | ".join(str(value or "").strip() for value in result.values() if value)[:600],
                )
                return result
            except Exception as exc:
                last_error = exc
                will_retry = attempt < self.retry_count and _is_retryable_error(exc)
                self._emit_telemetry(
                    "model_request_retry" if will_retry else "model_request_error",
                    target_language=target_language,
                    attempt=attempt + 1,
                    item_count=len(items),
                    elapsed_ms=round((time.monotonic() - started) * 1000),
                    engine=self.engine.name,
                    model_config_id=self.model_config_id,
                    source_preview=source_preview,
                    error=str(exc)[:500],
                )
                if will_retry:
                    retry_after = getattr(exc, "retry_after_seconds", None)
                    delay = float(retry_after) if retry_after is not None else min(0.5 * (2 ** attempt), 4.0)
                    time.sleep(max(0.0, delay))
                    continue
                break
        assert last_error is not None
        raise last_error

    def _translate_engine_items(self, items: list[dict[str, Any]], target_language: str) -> dict[str, str]:
        protected_count = sum(
            len(item.get("protected_tokens", []))
            for item in items
            if isinstance(item.get("protected_tokens"), list)
        )
        max_item_protected_count = max(
            (
                len(item.get("protected_tokens", []))
                for item in items
                if isinstance(item.get("protected_tokens"), list)
            ),
            default=0,
        )
        if max_item_protected_count > 4:
            self._emit_telemetry(
                "protected_segment_mode",
                target_language=target_language,
                item_count=len(items),
                protected_count=protected_count,
                max_item_protected_count=max_item_protected_count,
                reason="placeholder_dense",
            )
            return self._translate_segmented_protected_items(items, target_language)
        try:
            return self.engine.translate_items(items, target_language, self.timeout_seconds)
        except TranslationQualityError as exc:
            if "protected placeholders" not in str(exc).lower() or protected_count <= 0:
                raise
            self._emit_telemetry(
                "protected_segment_mode",
                target_language=target_language,
                item_count=len(items),
                protected_count=protected_count,
                reason="placeholder_recovery",
            )
            return self._translate_segmented_protected_items(items, target_language)

    def _translate_segmented_protected_items(
        self,
        items: list[dict[str, Any]],
        target_language: str,
    ) -> dict[str, str]:
        """Translate placeholder-dense text in coherent, bounded clauses.

        Splitting on every placeholder creates fragments such as ``"X"`` or
        ``"LPG X"`` that have no independently translatable meaning.  It also
        tempts a model to echo a supplied full-sentence context.  Keep a small
        number of placeholders inside each complete clause instead, and use the
        placeholder-free span fallback only for a provider that still cannot
        preserve that small set.
        """
        expanded: list[dict[str, Any]] = []
        part_results: dict[str, str] = {}
        part_ids: dict[str, list[str]] = {}
        item_parts: dict[str, list[TextPart]] = {}

        for item in items:
            item_id = str(item.get("id", ""))
            source_text = str(item.get("source_text", "") or "")
            protected_tokens = item.get("protected_tokens", []) if isinstance(item.get("protected_tokens"), list) else []
            if not protected_tokens:
                expanded.append(item)
                part_ids[item_id] = [item_id]
                item_parts[item_id] = [TextPart(source_text)]
                continue

            parts = _split_protected_layout(source_text)
            ids: list[str] = []
            token_by_name = {
                str(token.get("token", "")): token
                for token in protected_tokens
                if isinstance(token, dict) and str(token.get("token", ""))
            }
            for index, part in enumerate(parts):
                part_id = f"{item_id}::protected-part-{index}"
                ids.append(part_id)
                natural_fragment = _PROTECTED_PLACEHOLDER_PATTERN.sub("", part.text)
                if _is_technical_literal_fragment(natural_fragment):
                    part_results[part_id] = part.text
                    continue
                part_item = _translation_part_item(item, part_id, part.text)
                part_item["protected_tokens"] = [
                    token_by_name[token]
                    for token in _PROTECTED_PLACEHOLDER_PATTERN.findall(part.text)
                    if token in token_by_name
                ]
                expanded.append(part_item)
            part_ids[item_id] = ids
            item_parts[item_id] = parts

        for chunk in _translation_chunks(expanded, max_chars=max(600, self.chunk_max_chars)):
            try:
                part_results.update(self.engine.translate_items(chunk, target_language, self.timeout_seconds))
            except TranslationQualityError as chunk_error:
                if len(chunk) == 1:
                    if "protected placeholders" not in str(chunk_error).lower():
                        raise
                    part_results.update(self._translate_placeholder_free_spans(chunk, target_language))
                    continue
                for part_item in chunk:
                    try:
                        part_results.update(self.engine.translate_items([part_item], target_language, self.timeout_seconds))
                    except TranslationQualityError as exc:
                        if "protected placeholders" not in str(exc).lower():
                            raise
                        part_results.update(self._translate_placeholder_free_spans([part_item], target_language))

        return {
            item_id: join_translated_parts(
                item_parts[item_id],
                [str(part_results.get(part_id, "") or "") for part_id in ids],
            )
            for item_id, ids in part_ids.items()
        }

    def _translate_placeholder_free_spans(
        self,
        items: list[dict[str, Any]],
        target_language: str,
    ) -> dict[str, str]:
        model_items: list[dict[str, Any]] = []
        plans: dict[str, list[dict[str, str]]] = {}

        for item in items:
            item_id = str(item.get("id", ""))
            source_text = str(item.get("source_text", "") or "")
            protected_tokens = item.get("protected_tokens", []) if isinstance(item.get("protected_tokens"), list) else []
            if not protected_tokens:
                model_items.append(item)
                plans[item_id] = [{"kind": "translated", "id": item_id, "prefix": "", "suffix": ""}]
                continue

            plan: list[dict[str, str]] = []
            cursor = 0
            segment_index = 0

            def append_prose(value: str) -> None:
                nonlocal segment_index
                if not value:
                    return
                whitespace = re.match(r"^(\s*)(.*?)(\s*)$", value, flags=re.DOTALL)
                prefix, core, suffix = whitespace.groups() if whitespace else ("", value, "")
                if not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", core):
                    plan.append({"kind": "literal", "text": value})
                    return
                if _is_technical_literal_fragment(core):
                    plan.append({"kind": "literal", "text": value})
                    return
                segment_id = f"{item_id}::segment-{segment_index}"
                segment_index += 1
                segment_item = dict(item)
                segment_item.update({
                    "id": segment_id,
                    "source_text": core,
                    "monitor_source_text": core,
                    "protected_tokens": [],
                    "preserve_terms": [],
                    "glossary": [
                        entry for entry in item.get("glossary", [])
                        if isinstance(entry, dict)
                        and normalize_inline(entry.get("source", "")).casefold() in normalize_inline(core).casefold()
                    ],
                })
                model_items.append(segment_item)
                plan.append({"kind": "translated", "id": segment_id, "prefix": prefix, "suffix": suffix})

            for match in _PROTECTED_PLACEHOLDER_PATTERN.finditer(source_text):
                append_prose(source_text[cursor:match.start()])
                plan.append({"kind": "literal", "text": match.group(0)})
                cursor = match.end()
            append_prose(source_text[cursor:])
            plans[item_id] = plan

        translated_segments: dict[str, str] = {}
        for chunk in _translation_chunks(model_items, max_chars=max(600, self.chunk_max_chars)):
            try:
                translated_segments.update(self.engine.translate_items(chunk, target_language, self.timeout_seconds))
            except TranslationQualityError:
                if len(chunk) == 1:
                    raise
                for segment_item in chunk:
                    translated_segments.update(self.engine.translate_items([segment_item], target_language, self.timeout_seconds))

        reconstructed: dict[str, str] = {}
        for item_id, plan in plans.items():
            pieces: list[str] = []
            for part in plan:
                if part.get("kind") == "literal":
                    pieces.append(str(part.get("text", "") or ""))
                    continue
                segment_id = str(part.get("id", "") or "")
                translated = str(translated_segments.get(segment_id, "") or "").strip()
                if not translated:
                    raise TranslationResponseError(f"Segmented translation missing result for {segment_id}.")
                pieces.extend((str(part.get("prefix", "") or ""), translated, str(part.get("suffix", "") or "")))
            reconstructed[item_id] = "".join(pieces)
        return reconstructed

    def _protect_source_text(self, text: str, target_language: str) -> tuple[str, list[dict[str, str]]]:
        # Apply the same hard protection to every provider. Prompt-only unit
        # instructions are not reliable enough: models may localize FT to 英尺 or
        # partially rewrite compound units such as PSI/FT. Measurements and units
        # are therefore masked before the request and restored byte-for-byte.
        candidates: list[tuple[int, int, int, str]] = []

        def add_matches(matchers: list[tuple[str, re.Pattern[str]]], priority: int, *, units: bool = False) -> None:
            for configured_value, matcher in matchers:
                for match in matcher.finditer(text):
                    if units and not _unit_match_allowed(text, match, configured_value):
                        continue
                    candidates.append((match.start(), match.end(), priority, match.group(0)))

        if self.tuning.protect_units and self._protected_measurement_matcher:
            for match in self._protected_measurement_matcher.finditer(text):
                candidates.append((match.start(), match.end(), -1, match.group(0)))
        if self.tuning.protect_acronyms:
            add_matches(self._protected_acronym_matchers, 0)
        if self.tuning.protect_units:
            add_matches(self._protected_unit_matchers, 0, units=True)
        if self.tuning.protect_proper_nouns:
            add_matches(self._protected_proper_noun_matchers, 0)
        if self.tuning.protect_numbers:
            # Protect mixed alpha-numeric equipment/well identifiers as one
            # value.  Protecting only their numeric suffix would split ST-80 or
            # SHSG-160 into meaningless prose fragments.
            for match in _TECHNICAL_IDENTIFIER_PATTERN.finditer(text):
                candidates.append((match.start(), match.end(), -2, match.group(0)))
            for match in _TECHNICAL_TIME_PATTERN.finditer(text):
                candidates.append((match.start(), match.end(), -1, match.group(0)))
            for match in _TECHNICAL_ORDINAL_PATTERN.finditer(text):
                candidates.append((match.start(), match.end(), -1, match.group(0)))
            for match in _PROTECTED_NUMBER_PATTERN.finditer(text):
                candidates.append((match.start(), match.end(), 2, match.group(0)))
        for entry, _source_value, matcher in self._term_source_matchers:
            if not entry.protected:
                continue
            replacement = entry.value(target_language)
            if not replacement:
                continue
            for match in matcher.finditer(text):
                candidates.append((match.start(), match.end(), 1, replacement))

        selected: list[tuple[int, int, int, str]] = []
        for candidate in sorted(candidates, key=lambda item: (item[2], -(item[1] - item[0]), item[0])):
            start, end, _priority, _replacement = candidate
            if any(start < existing_end and end > existing_start for existing_start, existing_end, _p, _r in selected):
                continue
            selected.append(candidate)
        selected.sort(key=lambda item: item[0])
        if not selected:
            return text, []

        pieces: list[str] = []
        protected_tokens: list[dict[str, str]] = []
        cursor = 0
        for index, (start, end, _priority, replacement) in enumerate(selected):
            token = f"[[P{index}]]"
            pieces.extend((text[cursor:start], token))
            protected_tokens.append({"token": token, "replacement": replacement, "source": text[start:end]})
            cursor = end
        pieces.append(text[cursor:])
        return "".join(pieces), protected_tokens

    def _restore_protected_items_partial(
        self,
        items: list[dict[str, Any]],
        translated: dict[str, str],
    ) -> tuple[dict[str, str], dict[str, str]]:
        restored: dict[str, str] = {}
        invalid: dict[str, str] = {}
        for item in items:
            item_id = str(item.get("id", ""))
            text = str(translated.get(item_id, "") or "")
            protected_tokens = item.get("protected_tokens", [])
            if not isinstance(protected_tokens, list):
                protected_tokens = []
            expected_tokens = [
                str(token_data.get("token", ""))
                for token_data in protected_tokens
                if isinstance(token_data, dict) and str(token_data.get("token", ""))
            ]
            returned_tokens = _PROTECTED_PLACEHOLDER_PATTERN.findall(text)
            if Counter(returned_tokens) != Counter(expected_tokens):
                invalid[item_id] = f"model changed, removed, or duplicated protected placeholders for item {item_id}"
                continue
            text = _repair_protected_token_layout(str(item.get("source_text", "") or ""), text)
            for token_data in protected_tokens:
                if not isinstance(token_data, dict):
                    continue
                token = str(token_data.get("token", "") or "")
                replacement = str(token_data.get("replacement", "") or "")
                if token:
                    text = text.replace(token, replacement)
            text = self._apply_term_replacements_preserving_units(text)
            if self.tuning.protect_numbers:
                source_numbers = Counter(_number_tokens(item.get("monitor_source_text", "")))
                translated_numbers = Counter(_number_tokens(text))
                missing = list((source_numbers - translated_numbers).elements())[:8]
                allowed_derived = Counter(_derived_number_tokens(item.get("monitor_source_text", ""), self.target_language))
                extra = list(((translated_numbers - source_numbers) - allowed_derived).elements())[:8]
                if missing or extra:
                    invalid[item_id] = (
                        f"model changed numeric values for item {item_id}; "
                        f"missing={missing}; extra={extra}"
                    )
                    continue
            if self.tuning.protect_units:
                source_units = Counter(_protected_unit_tokens(item.get("monitor_source_text", ""), self._protected_unit_matchers))
                translated_units = Counter(_protected_unit_tokens(text, self._protected_unit_matchers))
                missing_units = list((source_units - translated_units).elements())[:8]
                extra_units = list((translated_units - source_units).elements())[:8]
                if missing_units or extra_units:
                    invalid[item_id] = (
                        f"model changed protected units for item {item_id}; "
                        f"missing={missing_units}; extra={extra_units}"
                    )
                    continue
            restored[item_id] = text
        return restored, invalid

    def _restore_protected_items(self, items: list[dict[str, Any]], translated: dict[str, str]) -> dict[str, str]:
        restored, invalid = self._restore_protected_items_partial(items, translated)
        if invalid:
            raise TranslationError(next(iter(invalid.values())))
        return restored

    def _term_glossary(self, text: str, target_language: str) -> list[dict[str, str]]:
        cache_key = (normalize_language(target_language), source_hash(text))
        cached = self._term_glossary_cache.get(cache_key)
        if cached is not None:
            return [dict(item) for item in cached]
        records: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for entry, source_value, matcher in self._term_source_matchers:
            target = entry.value(target_language)
            if not target:
                continue
            if not matcher.search(text):
                continue
            key = (source_value.lower(), target)
            if key in seen:
                continue
            seen.add(key)
            records.append({"source": source_value, "target": target})
        records = records[:30]
        self._term_glossary_cache[cache_key] = [dict(item) for item in records]
        return records

    def _preserve_terms(self, text: str, glossary: list[dict[str, str]]) -> list[str]:
        translated_sources = {
            normalize_inline(item.get("source", "")).casefold()
            for item in glossary
            if normalize_inline(item.get("source", ""))
            and normalize_inline(item.get("source", "")).casefold() != normalize_inline(item.get("target", "")).casefold()
        }
        values: list[str] = []
        for configured, matcher in (*self._protected_acronym_matchers, *self._protected_proper_noun_matchers):
            if normalize_inline(configured).casefold() in translated_sources:
                continue
            match = matcher.search(text)
            if match:
                values.append(match.group(0))
        values.extend(
            match.group(0)
            for match in _TECHNICAL_IDENTIFIER_PATTERN.finditer(text)
            if not re.match(r"^\d", match.group(0))
        )
        return list(dict.fromkeys(values))[:40]

    def _prompt_context(
        self,
        protected_tokens: list[dict[str, str]] | None = None,
        report_context: dict[str, Any] | None = None,
    ) -> dict[str, object]:
        protected = [
            str(item.get("source", "") or "")
            for item in (protected_tokens or [])
            if isinstance(item, dict)
            and str(item.get("source", "") or "")
            and not re.match(r"^\s*[-+]?\d", str(item.get("source", "") or ""))
        ]
        return {
            "system_prompt": self.tuning.system_prompt,
            "translation_instruction": self.tuning.translation_instruction,
            "protect_numbers": self.tuning.protect_numbers,
            "protected_terms": list(dict.fromkeys(protected))[:40],
            "report_context": dict(report_context or {}),
        }

    def _apply_term_replacements(self, text: str) -> str:
        translated = text
        for pattern, replacement in self._term_matchers:
            translated = pattern.sub(replacement, translated)
        return _clean_translation_artifacts(translated)

    def _apply_term_replacements_preserving_units(self, text: str) -> str:
        candidates: list[tuple[int, int, str]] = []
        for configured_unit, matcher in self._protected_unit_matchers:
            for match in matcher.finditer(text):
                if _unit_match_allowed(text, match, configured_unit):
                    candidates.append((match.start(), match.end(), match.group(0)))
        selected: list[tuple[int, int, str]] = []
        for candidate in sorted(candidates, key=lambda item: (item[0], -(item[1] - item[0]))):
            start, end, _unit = candidate
            if any(start < existing_end and end > existing_start for existing_start, existing_end, _existing in selected):
                continue
            selected.append(candidate)
        if not selected:
            return self._apply_term_replacements(text)
        masked = text
        replacements: list[tuple[str, str]] = []
        for index, (start, end, unit) in enumerate(sorted(selected, key=lambda item: item[0], reverse=True)):
            token = f"\ue000UNIT{index}\ue001"
            masked = masked[:start] + token + masked[end:]
            replacements.append((token, unit))
        translated = self._apply_term_replacements(masked)
        for token, unit in replacements:
            translated = translated.replace(token, unit)
        return translated


def build_translator(
    config: TranslationConfig | None = None,
    engine: TranslationEngine | None = None,
    terms: TermsConfig | None = None,
    target_language: str | None = None,
    tuning: TranslationTuningConfig | None = None,
    telemetry: Callable[[dict[str, Any]], None] | None = None,
    translation_memory: dict[str, str] | None = None,
) -> DrillingReportTranslator:
    config = config or TranslationConfig.from_env()
    selected_terms = terms or TermsConfig.load(config.terms_path)
    selected_engine = engine or build_engine(config)
    return DrillingReportTranslator(
        selected_engine,
        selected_terms,
        target_language=target_language or config.target_language,
        timeout_seconds=config.timeout_seconds,
        model_config_id=config.model_config_id,
        retry_count=config.retry_count,
        tuning=tuning,
        chunk_max_chars=config.chunk_max_chars,
        telemetry=telemetry,
        translation_memory=translation_memory,
    )


def build_engine(config: TranslationConfig) -> TranslationEngine:
    engine = config.engine.lower()
    if engine == "ollama":
        return OllamaTranslationEngine(
            base_url=config.ollama_url,
            model=config.ollama_model,
            temperature=config.ollama_temperature,
            thinking_mode=config.thinking_mode,
            request_options=config.request_options,
        )
    if engine in {"openai-compatible", "openai_compatible", "openai"}:
        if not config.openai_base_url or not config.openai_model:
            raise ValueError("OpenAI-compatible base URL and model are required.")
        return OpenAICompatibleTranslationEngine(
            base_url=config.openai_base_url,
            model=config.openai_model,
            api_key=config.openai_api_key,
            temperature=config.openai_temperature,
            thinking_mode=config.thinking_mode,
            request_options=config.request_options,
        )
    if engine in {"noop", "none"}:
        return NoopTranslationEngine()
    raise ValueError(f"Unsupported translation engine: {config.engine}. Use ollama, openai-compatible or noop.")


def _normalize_thinking_mode(value: object) -> str:
    mode = str(value or "auto").strip().lower()
    aliases = {
        "off": "disabled",
        "false": "disabled",
        "disable": "disabled",
        "on": "enabled",
        "true": "enabled",
        "enable": "enabled",
    }
    mode = aliases.get(mode, mode)
    return mode if mode in {"auto", "disabled", "enabled"} else "auto"


def _safe_request_options(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    reserved = {"authorization", "api_key", "apikey", "base_url", "messages", "model", "prompt", "stream"}
    filtered = {
        str(key): copy.deepcopy(item)
        for key, item in value.items()
        if str(key).strip().lower() not in reserved
    }
    try:
        encoded = json.dumps(filtered, ensure_ascii=False, separators=(",", ":"))
        return json.loads(encoded) if len(encoded.encode("utf-8")) <= 12_000 else {}
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}


def _is_deepseek_endpoint(base_url: str, model: str) -> bool:
    endpoint = str(base_url or "").lower()
    model_name = str(model or "").lower()
    return "api.deepseek.com" in endpoint or model_name.startswith("deepseek-")


def _needs_qwen_no_think_prefill(base_url: str, model: str) -> bool:
    local_lm_studio = bool(re.match(r"^https?://(?:127\.0\.0\.1|localhost|\[::1\])(?::1234)?(?:/|$)", str(base_url or ""), re.IGNORECASE))
    normalized_model = re.sub(r"[^a-z0-9]", "", str(model or "").lower())
    return local_lm_studio and "qwen35" in normalized_model


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
        expected_hash = str(row.get("source_hash", "") or "")
        source_value = _payload_value(payload, path)
        if expected_hash and source_hash(_clean_text(source_value)) != expected_hash:
            continue
        _set_payload_value(translated_payload, path, text)
    translated_payload["translation_content"] = rows
    return translated_payload


def translation_coverage(
    payload: dict[str, Any],
    rows: list[dict[str, Any]],
    target_language: str,
    tuning: TranslationTuningConfig | None = None,
) -> dict[str, Any]:
    target_language = normalize_language(target_language)
    valid_rows = {
        (
            str(row.get("entity_id", "") or ""),
            str(row.get("field_code", "") or ""),
        ): row
        for row in rows
        if isinstance(row, dict)
        and normalize_language(row.get("target_language", "")) == target_language
        and str(row.get("translation_status", "")) in {"COMPLETED", "NOT_REQUIRED"}
    }
    selected_tuning = tuning or TranslationTuningConfig()
    required = [
        unit
        for unit in iter_payload_text_units(
            payload,
            report_fields=set(selected_tuning.report_fields),
            row_fields=set(selected_tuning.row_fields),
            scope_rules=set(selected_tuning.scope_rules) if selected_tuning.scope_rules else None,
        )
        if text_needs_translation(unit.text, target_language)
    ]
    missing: list[str] = []
    for unit in required:
        row = valid_rows.get((unit.entity_id, unit.field_code))
        if not row or str(row.get("source_hash", "") or "") != source_hash(_clean_text(unit.text)):
            missing.append(unit.path)
    return {
        "ready": not missing,
        "required_count": len(required),
        "completed_count": len(required) - len(missing),
        "missing": missing,
    }


def iter_payload_text_units(
    payload: dict[str, Any],
    *,
    record_id: str = "",
    report_fields: set[str] | None = None,
    row_fields: set[str] | None = None,
    scope_rules: set[tuple[str, str, str]] | None = None,
) -> list[TextUnit]:
    record_id = record_id or str(payload.get("metadata", {}).get("record_id", "") or "")
    metadata = payload.get("metadata", {}) if isinstance(payload.get("metadata"), dict) else {}
    report_type = str(metadata.get("report_type", "") or "").strip().lower()
    fields = payload.get("report_fields", {})
    units: list[TextUnit] = []
    selected_report_fields = TRANSLATABLE_REPORT_FIELDS if report_fields is None else report_fields
    selected_row_fields = TRANSLATABLE_ROW_FIELDS if row_fields is None else row_fields
    if scope_rules is not None:
        selected_report_fields = {
            field_name
            for rule_report_type, section, field_name in scope_rules
            if section == "report_fields" and rule_report_type in {"*", report_type}
        }
    if isinstance(fields, dict):
        for key in _ordered_translation_fields(selected_report_fields, REPORT_FIELD_TRANSLATION_ORDER):
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
            section_row_fields = selected_row_fields
            if scope_rules is not None:
                section_row_fields = {
                    field_name
                    for rule_report_type, rule_section, field_name in scope_rules
                    if rule_report_type in {"*", report_type} and rule_section in {"*", section}
                }
            for key in _ordered_translation_fields(section_row_fields, ROW_FIELD_TRANSLATION_ORDER):
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


def _ordered_translation_fields(values: set[str], preferred: tuple[str, ...]) -> list[str]:
    rank = {value: index for index, value in enumerate(preferred)}
    return sorted(values, key=lambda value: (rank.get(value, len(rank)), value))


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
    if _SPANISH_PROSE_PATTERN.search(value):
        return "es"
    return "en"


def text_needs_translation(text: str, target_language: str) -> bool:
    """Return whether meaningful non-target prose remains in a possibly mixed field."""
    value = _clean_text(_PROTECTED_PLACEHOLDER_PATTERN.sub("", str(text or "")))
    if not value:
        return False
    target = normalize_language(target_language)
    if target == "zh-CN":
        latin_letters = len(re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", value))
        latin_words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{2,}", value)
        return latin_letters >= 4 and bool(latin_words)
    return detect_language(value) != target


def source_hash(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _target_languages_from_env() -> list[str]:
    raw = os.environ.get("DRP_TRANSLATION_TARGET_LANGUAGES", "zh-CN")
    languages: list[str] = []
    for item in raw.split(","):
        language = normalize_language(item)
        if language in LANGUAGES and language not in languages:
            languages.append(language)
    return languages or list(LANGUAGES)


def _post_json(url: str, payload: dict[str, Any], timeout_seconds: float, *, headers: dict[str, str] | None = None) -> Any:
    circuit_key = _provider_circuit_key(url)
    _check_provider_circuit(circuit_key)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request_headers = {"Content-Type": "application/json; charset=utf-8", **(headers or {})}
    request = urllib.request.Request(url, data=body, headers=request_headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = str(exc)
        retryable = exc.code in {408, 425, 429} or 500 <= exc.code < 600
        if retryable:
            _record_provider_transport_failure(circuit_key)
        raise TranslationTransportError(
            f"{url} returned HTTP {exc.code}: {detail[:200]}",
            retryable=retryable,
        ) from exc
    except urllib.error.URLError as exc:
        _record_provider_transport_failure(circuit_key)
        raise TranslationTransportError(f"{url} is unavailable: {exc}", retryable=True) from exc
    except TimeoutError as exc:
        _record_provider_transport_failure(circuit_key)
        raise TranslationTransportError(f"{url} timed out: {exc}", retryable=True) from exc
    _record_provider_success(circuit_key)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TranslationError(f"{url} returned non-JSON response.") from exc


_PROVIDER_CIRCUIT_LOCK = threading.Lock()
_PROVIDER_CIRCUITS: dict[str, dict[str, float]] = {}
_PROVIDER_CIRCUIT_FAILURE_THRESHOLD = 2
_PROVIDER_CIRCUIT_COOLDOWN_SECONDS = 30.0


def _provider_circuit_key(url: str) -> str:
    match = re.match(r"^(https?://[^/]+)", str(url or ""), flags=re.IGNORECASE)
    return (match.group(1) if match else str(url or "")).lower()


def _check_provider_circuit(key: str) -> None:
    while True:
        now = time.monotonic()
        with _PROVIDER_CIRCUIT_LOCK:
            state = _PROVIDER_CIRCUITS.get(key)
            if not state:
                return
            opened_until = float(state.get("opened_until", 0.0) or 0.0)
            if opened_until <= now:
                _PROVIDER_CIRCUITS.pop(key, None)
                return
            remaining = max(0.1, opened_until - now)
        # Do not turn a shared provider cooldown into an immediate job failure.
        # Waiting here also avoids consuming the caller's retry budget before a
        # network request has actually been attempted.
        time.sleep(remaining)


def _record_provider_transport_failure(key: str) -> None:
    with _PROVIDER_CIRCUIT_LOCK:
        state = _PROVIDER_CIRCUITS.setdefault(key, {"failures": 0.0, "opened_until": 0.0})
        failures = int(state.get("failures", 0.0) or 0.0) + 1
        state["failures"] = float(failures)
        if failures >= _PROVIDER_CIRCUIT_FAILURE_THRESHOLD:
            state["opened_until"] = time.monotonic() + _PROVIDER_CIRCUIT_COOLDOWN_SECONDS


def _record_provider_success(key: str) -> None:
    with _PROVIDER_CIRCUIT_LOCK:
        _PROVIDER_CIRCUITS.pop(key, None)


def _is_retryable_error(exc: Exception) -> bool:
    retryable = getattr(exc, "retryable", None)
    if retryable is not None:
        return bool(retryable)
    return not isinstance(exc, TranslationQualityError)


def _allows_item_fallback(exc: Exception) -> bool:
    return not isinstance(exc, TranslationTransportError)


def _auth_headers(api_key: str) -> dict[str, str]:
    key = str(api_key or "").strip()
    return {"Authorization": f"Bearer {key}"} if key else {}


def _chat_completions_url(base_url: str) -> str:
    base = str(base_url or "").rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def _chat_content(data: Any) -> str:
    if not isinstance(data, dict):
        raise TranslationError("OpenAI-compatible endpoint returned invalid response.")
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise TranslationError("OpenAI-compatible response missing choices.")
    first = choices[0]
    if not isinstance(first, dict):
        raise TranslationError("OpenAI-compatible response choice is invalid.")
    message = first.get("message")
    if isinstance(message, dict):
        return str(message.get("content", "") or "")
    return str(first.get("text", "") or "")


def _ollama_batch_prompt(items: list[dict[str, Any]], target_language: str, *, strict: bool = False) -> str:
    return "/no_think\n" + _translation_batch_prompt(
        items,
        target_language,
        strict=strict,
        include_system_prompt=True,
    )


def _openai_batch_prompt(items: list[dict[str, Any]], target_language: str, *, strict: bool = False) -> str:
    return _translation_batch_prompt(
        items,
        target_language,
        strict=strict,
        include_system_prompt=False,
    )


def _translation_batch_prompt(
    items: list[dict[str, Any]],
    target_language: str,
    *,
    strict: bool,
    include_system_prompt: bool,
) -> str:
    compact_items = [
        {
            "id": item["id"],
            "field_code": item.get("field_code", ""),
            "source_language": item["source_language"],
            "source_text": item["source_text"],
            "glossary": item.get("glossary", []),
            "preserve_terms": item.get("preserve_terms", []),
            "layout": "paragraph" if item.get("paragraph_layout") else "structured",
            "segment_context": (
                item.get("prompt_context", {}).get("segment_context", "")
                if isinstance(item.get("prompt_context"), dict) else ""
            ),
        }
        for item in items
    ]
    target = normalize_language(target_language)
    instruction = {
        "zh-CN": "将每个 source_text 中的西班牙语或英语自然语言完整翻译成简体中文。全大写的西班牙语或英语仍是正文，必须翻译。",
        "en": "Translate all Spanish or Chinese natural-language prose in every source_text completely into English. ALL-CAPS prose must also be translated.",
        "es": "Traduce completamente al español todo texto natural en chino o inglés de cada source_text. El texto en MAYÚSCULAS también debe traducirse.",
    }.get(target, f"Translate every source_text completely into {_language_label(target_language)}.")
    retry_rule = "上一次结果未满足完整性要求。请重新翻译，并逐项核对原文中的数字、编号和必保术语。" if strict and target == "zh-CN" else (
        "The previous result failed an integrity check. Translate again and verify every number, identifier, and preserved term." if strict else ""
    )
    contexts = [item.get("prompt_context", {}) for item in items if isinstance(item.get("prompt_context"), dict)]
    context = contexts[0] if contexts else {}
    system_prompt = str(context.get("system_prompt", "") or DEFAULT_SYSTEM_PROMPT).strip()
    additional_instruction = str(context.get("translation_instruction", "") or DEFAULT_TRANSLATION_INSTRUCTION).strip()
    report_context = context.get("report_context", {}) if isinstance(context.get("report_context"), dict) else {}
    rules = [
        additional_instruction,
        "结合日报上下文理解作业含义，使用自然、专业、通顺的中文表达，避免逐字硬译。",
        "保持 source_text 原有段落、换行、列表和项目顺序；不得总结、删减、添加事实。",
        "应用每条记录中实际命中的 glossary；preserve_terms 中的缩写、单位、公司名和标识符保持原样。",
    ]
    if context.get("protect_numbers", True):
        rules.append("保留日期、时间、数字、数值精度和设备序列号，不得改写格式。")
    if any(_PROTECTED_PLACEHOLDER_PATTERN.search(str(item.get("source_text", "") or "")) for item in items):
        rules.append("source_text 中形如 [[P0]] 的占位符必须逐字原样保留，不得改写、删除或复制。")
    if any(str(item.get("segment_context", "") or "") for item in compact_items):
        rules.append("带 segment_context 的 source_text 是原句中的自然语言片段；结合脱敏上下文准确翻译该片段，但不要输出上下文或 <PROTECTED> 标记。")
    if any(item.get("layout") == "paragraph" for item in compact_items):
        rules.append("layout 为 paragraph 的 description 必须作为一个完整连续段落理解和输出，不得按原 PDF 的视觉换行拆句。")
    if retry_rule:
        rules.append(retry_rule)
    system_text = f"{system_prompt}\n" if include_system_prompt else ""
    return (
        system_text
        +
        f"{instruction}\n"
        + "\n".join(f"- {rule}" for rule in rules if rule)
        + "\n"
        + (f"日报上下文（只用于理解，不要翻译或输出）：\n{json.dumps(report_context, ensure_ascii=False)}\n" if report_context else "")
        +
        "只返回严格 JSON，格式为：{\"items\":[{\"id\":\"0\",\"translated_text\":\"译文\"}]}。每个输入 id 必须返回一条。\n"
        f"Input JSON:\n{json.dumps({'items': compact_items}, ensure_ascii=False)}"
    )


def _translation_output_token_budget(items: list[dict[str, Any]]) -> int:
    source_chars = sum(len(str(item.get("source_text", "") or "")) for item in items)
    return max(4096, min(8192, source_chars * 4 + 2048))


def _prompt_system_message(items: list[dict[str, Any]]) -> str:
    context = items[0].get("prompt_context", {}) if items and isinstance(items[0].get("prompt_context"), dict) else {}
    system_prompt = str(context.get("system_prompt", "") or DEFAULT_SYSTEM_PROMPT).strip()
    return f"{system_prompt} Return strict JSON only."


def _translation_quality_error(source_text: str, translated_text: str, target_language: str) -> str:
    source = _clean_text(source_text)
    translated = _clean_text(translated_text)
    if not translated:
        return "missing translated_text"
    source_natural = _clean_text(_PROTECTED_PLACEHOLDER_PATTERN.sub("", source))
    translated_natural = _clean_text(_PROTECTED_PLACEHOLDER_PATTERN.sub("", translated))
    if not source_natural:
        return ""
    # Layout-only changes are not a translation. Collapse all whitespace so a
    # model cannot pass quality checks merely by removing PDF line wrapping.
    source_folded = normalize_translation_paragraph(source_natural).casefold()
    translated_folded = normalize_translation_paragraph(translated_natural).casefold()
    if source_folded == translated_folded:
        return "source text was returned unchanged"
    # Only reject a provable full-source copy. Proper nouns, company names,
    # abbreviations and technical labels often remain in Latin/Spanish form in an
    # otherwise valid Chinese translation, so language-pattern checks are too
    # noisy to be a reliable quality gate.
    if len(source_folded) >= 20 and source_folded in translated_folded:
        return "source text was returned unchanged"
    return ""


def _openai_item_quality_error(item: dict[str, Any], translated_text: str, target_language: str) -> str:
    source_text = str(item.get("source_text", "") or "")
    if "<PROTECTED>" in str(translated_text or ""):
        return "model leaked protected context marker"
    quality_error = _translation_quality_error(source_text, translated_text, target_language)
    if quality_error:
        return quality_error
    expected = Counter(_PROTECTED_PLACEHOLDER_PATTERN.findall(source_text))
    returned = Counter(_PROTECTED_PLACEHOLDER_PATTERN.findall(str(translated_text or "")))
    if returned != expected:
        return "model changed, removed, or duplicated protected placeholders"
    number_error = _numeric_quality_error(source_text, translated_text, target_language)
    if number_error:
        return number_error
    translated_folded = normalize_inline(translated_text).casefold()
    for term in item.get("preserve_terms", []) if isinstance(item.get("preserve_terms"), list) else []:
        preserved = normalize_inline(term)
        if preserved and preserved.casefold() not in translated_folded:
            return f"required preserved term was changed or removed: {preserved}"
    return ""


def _numeric_quality_error(source_text: str, translated_text: str, target_language: str) -> str:
    source_numbers = Counter(_number_tokens(source_text))
    translated_numbers = Counter(_number_tokens(translated_text))
    missing = list((source_numbers - translated_numbers).elements())[:8]
    allowed_derived = Counter(_derived_number_tokens(source_text, target_language))
    extra = list(((translated_numbers - source_numbers) - allowed_derived).elements())[:8]
    if missing or extra:
        return f"model changed numeric values; missing={missing}; extra={extra}"
    return ""


def _surgically_protect_values(item: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    source_text = str(item.get("source_text", "") or "")
    candidates: list[tuple[int, int, str]] = []
    for matcher in (_TECHNICAL_TIME_PATTERN, _PROTECTED_NUMBER_PATTERN):
        for match in matcher.finditer(source_text):
            candidates.append((match.start(), match.end(), match.group(0)))
    preserve_terms = item.get("preserve_terms", []) if isinstance(item.get("preserve_terms"), list) else []
    for term in preserve_terms:
        value = str(term or "").strip()
        if not value:
            continue
        for match in re.finditer(re.escape(value), source_text, flags=re.IGNORECASE):
            candidates.append((match.start(), match.end(), match.group(0)))
    selected: list[tuple[int, int, str]] = []
    for candidate in sorted(candidates, key=lambda value: (value[0], -(value[1] - value[0]))):
        start, end, _value = candidate
        if any(start < existing_end and end > existing_start for existing_start, existing_end, _ in selected):
            continue
        selected.append(candidate)
    selected.sort(key=lambda value: value[0])
    if not selected:
        return dict(item), []
    pieces: list[str] = []
    values: list[dict[str, str]] = []
    cursor = 0
    for index, (start, end, value) in enumerate(selected):
        token = f"[[P{index}]]"
        pieces.extend((source_text[cursor:start], token))
        separator_before = source_text[selected[index - 1][1]:start] if index else ""
        values.append({
            "token": token,
            "replacement": value,
            "separate_from_previous": bool(index and separator_before and separator_before.isspace()),
        })
        cursor = end
    pieces.append(source_text[cursor:])
    return {**item, "source_text": "".join(pieces)}, values


def _restore_surgically_protected_values(text: str, values: list[dict[str, str]]) -> str:
    restored = str(text or "")
    # Models sometimes keep both numeric placeholders but remove the whitespace
    # between them. Restore that source boundary before replacing the tokens so
    # identifiers such as "0177006 1" cannot become the new number "01770061".
    for index, value in enumerate(values):
        if not index or not value.get("separate_from_previous"):
            continue
        previous_token = str(values[index - 1].get("token", "") or "")
        token = str(value.get("token", "") or "")
        if previous_token and token:
            restored = re.sub(
                rf"{re.escape(previous_token)}\s*{re.escape(token)}",
                f"{previous_token} {token}",
                restored,
            )
    for value in values:
        restored = restored.replace(str(value.get("token", "") or ""), str(value.get("replacement", "") or ""))
    return normalize_multiline(restored)


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


def _translation_chunks(
    items: list[dict[str, Any]],
    max_chars: int = 2500,
    max_items: int = 12,
) -> list[list[dict[str, Any]]]:
    chunks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_chars = 0
    for item in items:
        item_chars = _translation_item_size(item)
        if current and (current_chars + item_chars > max_chars or len(current) >= max_items):
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(item)
        current_chars += item_chars
    if current:
        chunks.append(current)
    return chunks


def _semantic_translation_chunks(items: list[dict[str, Any]], max_chars: int) -> list[list[dict[str, Any]]]:
    """Keep a small report together; split a large report only at module boundaries."""
    if not items:
        return []
    total_chars = sum(_translation_item_size(item) for item in items)
    if total_chars <= max_chars and len(items) <= 12:
        return [items]
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        key = str(item.get("context_group", "report_fields") or "report_fields")
        groups.setdefault(key, []).append(item)
    chunks: list[list[dict[str, Any]]] = []
    for group_items in groups.values():
        chunks.extend(_translation_chunks(group_items, max_chars=max_chars))
    return chunks


def _translation_item_size(item: dict[str, Any]) -> int:
    return len(str(item.get("source_text", "") or "")) + len(json.dumps(item.get("glossary", []), ensure_ascii=False))


def _uses_paragraph_layout(field_code: object) -> bool:
    return str(field_code or "").strip() == "report_fields.description"


def _normalize_item_layout(field_code: object, text: object) -> str:
    if _uses_paragraph_layout(field_code):
        return normalize_translation_paragraph(text)
    return normalize_multiline(text)


def _translation_context_group(unit: TextUnit) -> str:
    if unit.entity_type == "daily_report" or unit.field_code.startswith("report_fields."):
        return "report_fields"
    return str(unit.entity_type or unit.field_code.partition(".")[0] or "report_fields")


def _report_translation_context(payload: dict[str, Any], record_id: str = "") -> dict[str, Any]:
    """Build stable report background shared by every self-contained model call."""
    metadata = payload.get("metadata", {}) if isinstance(payload.get("metadata"), dict) else {}
    fields = payload.get("report_fields", {}) if isinstance(payload.get("report_fields"), dict) else {}
    context: dict[str, Any] = {
        "record_id": record_id or str(metadata.get("record_id", "") or ""),
        "report_type": str(metadata.get("report_type", "") or ""),
        "report_date": str(fields.get("reportDate", "") or ""),
        "report_number": str(fields.get("reportNo", "") or ""),
        "wellbore": str(fields.get("wellbore", "") or ""),
        "rig": str(fields.get("rig", "") or ""),
        "operation_event": str(fields.get("event", "") or ""),
        "primary_reason": str(fields.get("primaryReason", "") or ""),
    }
    module_counts = {
        key: len(value)
        for key, value in payload.items()
        if isinstance(value, list) and key != "translation_content" and value
    }
    if module_counts:
        context["module_row_counts"] = module_counts
    return {key: value for key, value in context.items() if value not in ("", None) and value != {}}


def _translation_part_item(item: dict[str, Any], part_id: str, part_text: str) -> dict[str, Any]:
    folded = normalize_inline(part_text).casefold()
    glossary = [
        value
        for value in item.get("glossary", []) if isinstance(item.get("glossary"), list) and isinstance(value, dict)
        and normalize_inline(value.get("source", "")).casefold() in folded
    ]
    preserve_terms = [
        str(value)
        for value in item.get("preserve_terms", []) if isinstance(item.get("preserve_terms"), list)
        and normalize_inline(value).casefold() in folded
    ]
    return {
        **item,
        "id": part_id,
        "source_text": part_text,
        "glossary": glossary,
        "preserve_terms": preserve_terms,
    }


def _split_protected_layout(
    text: str,
    *,
    max_chars: int = 320,
    max_placeholders: int = 4,
) -> list[TextPart]:
    """Split dense protected text while retaining exact inter-part layout."""
    initial = split_preserving_layout(text, max_chars)
    parts: list[TextPart] = []
    for initial_part in initial:
        remaining = initial_part.text
        separator_before = initial_part.separator_before
        while True:
            matches = list(_PROTECTED_PLACEHOLDER_PATTERN.finditer(remaining))
            if len(matches) <= max_placeholders:
                if remaining or not parts:
                    parts.append(TextPart(remaining, separator_before))
                break

            # Cut immediately before the next placeholder. Any whitespace at
            # that boundary belongs to the following part as its separator.
            cutoff = matches[max_placeholders].start()
            left = remaining[:cutoff]
            content = left.rstrip()
            boundary_separator = left[len(content):]
            if not content:
                # Defensive fallback for adjacent placeholders. Four adjacent
                # tokens still form a safe bounded part.
                cutoff = matches[max_placeholders - 1].end()
                content = remaining[:cutoff]
                boundary_separator = ""
            parts.append(TextPart(content, separator_before))
            remaining = remaining[cutoff:]
            separator_before = boundary_separator
    if parts:
        parts[0] = TextPart(parts[0].text, "")
    return parts


def _is_technical_literal_fragment(value: str) -> bool:
    """Recognize short identifier/operator fragments that should stay literal."""
    text = normalize_inline(value)
    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", text)
    if not words:
        return True
    def is_technical_word(word: str) -> bool:
        return len(word) <= 4 and (word.upper() == word or word.casefold() == "x")

    if len(words) == 1 and is_technical_word(words[0]):
        return True
    if words and all(is_technical_word(word) for word in words):
        return True
    if re.search(r"[\d#/+*]", text) and len(words) <= 4 and all(is_technical_word(word) for word in words):
        return True
    return False


def _repair_protected_token_layout(source_text: str, translated_text: str) -> str:
    """Restore source boundaries between placeholders before value expansion."""
    source = str(source_text or "")
    repaired = str(translated_text or "")
    matches = list(_PROTECTED_PLACEHOLDER_PATTERN.finditer(source))
    for previous, current in zip(matches, matches[1:]):
        separator = source[previous.end():current.start()]
        if separator and separator.isspace():
            repaired = re.sub(
                rf"{re.escape(previous.group(0))}\s*{re.escape(current.group(0))}",
                f"{previous.group(0)}{separator}{current.group(0)}",
                repaired,
            )

    for match in matches:
        token = match.group(0)
        before = source[:match.start()]
        after = source[match.end():]
        if before and before[-1].isspace():
            repaired = re.sub(rf"(?<=[A-Za-z0-9_]){re.escape(token)}", f" {token}", repaired)
        if after and after[0].isspace():
            repaired = re.sub(rf"{re.escape(token)}(?=[A-Za-z0-9_])", f"{token} ", repaired)

    # A model occasionally expands a masked mesh/fraction value, e.g. emits
    # ``[[P1]]/40`` for the already protected source value ``20/40``. Numeric
    # content outside placeholders is never legitimate when number protection
    # is enabled, so remove only a directly attached invented fraction suffix.
    for match in matches:
        token = match.group(0)
        source_suffix = source[match.end():]
        if not re.match(r"\s*/\s*\d", source_suffix):
            repaired = re.sub(rf"{re.escape(token)}\s*/\s*\d+(?:[.,]\d+)?", token, repaired)
    return repaired


def _translation_chunk_max_chars(engine_name: str, configured: int = 0) -> int:
    if configured > 0:
        return max(300, min(int(configured), 24000))
    if str(engine_name or "").lower() in {"openai-compatible", "openai_compatible", "openai"}:
        return DEFAULT_OPENAI_COMPATIBLE_CHUNK_CHARS
    return DEFAULT_OLLAMA_CHUNK_CHARS


def _split_translation_text(text: str, max_chars: int = 180) -> list[str]:
    return [part.text for part in split_preserving_layout(text, max_chars)]


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


def _payload_value(payload: dict[str, Any], path: str) -> object:
    if path.startswith("report_fields."):
        fields = payload.get("report_fields")
        return fields.get(path.split(".", 1)[1], "") if isinstance(fields, dict) else ""
    match = re.match(r"([A-Za-z0-9_]+)\[(\d+)]\.([A-Za-z0-9_]+)$", path)
    if not match:
        return ""
    section, index_text, key = match.groups()
    rows = payload.get(section)
    index = int(index_text)
    if isinstance(rows, list) and 0 <= index < len(rows) and isinstance(rows[index], dict):
        return rows[index].get(key, "")
    return ""


def _compiled_term_matchers(entries: tuple[TermEntry, ...], target_language: str) -> list[tuple[re.Pattern[str], str]]:
    matchers: list[tuple[re.Pattern[str], str]] = []
    for entry in entries:
        if not entry.enabled or not entry.protected:
            continue
        replacement = entry.value(target_language)
        if not replacement:
            continue
        for _, source_value in entry.source_values():
            if source_value and source_value != replacement:
                matchers.append((re.compile(_term_regex(source_value), re.IGNORECASE), replacement))
    return sorted(matchers, key=lambda item: len(item[0].pattern), reverse=True)


def _compiled_glossary_matchers(entries: tuple[TermEntry, ...]) -> list[tuple[TermEntry, str, re.Pattern[str]]]:
    matchers: list[tuple[TermEntry, str, re.Pattern[str]]] = []
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        if not entry.enabled:
            continue
        for _, source_value in entry.source_values():
            if not source_value:
                continue
            key = (entry.id, source_value.lower())
            if key in seen:
                continue
            seen.add(key)
            matchers.append((entry, source_value, re.compile(_term_regex(source_value), re.IGNORECASE)))
    return sorted(matchers, key=lambda item: len(item[1]), reverse=True)


_PROTECTED_PLACEHOLDER_PATTERN = re.compile(r"\[\[P\d+]]")
_SPANISH_PROSE_PATTERN = re.compile(
    r"[ÁÉÍÓÚÜÑáéíóúüñ¿¡]|\b(?:con|para|desde|hasta|perfora|saca|bombea|circula|pozo|broca|"
    r"revestimiento|herramienta|incidentes?|sin|reportar|ultimas?|traslado|fluidos?|campamentos?|"
    r"personal|ingresa|servicio|aguas?|cortes|perforacion|venta|provisto|cerrada|realiza|prueba|"
    r"presion|como|sigue|izquierda|mecanico|completacion)\b",
    re.IGNORECASE,
)
_TECHNICAL_IDENTIFIER_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?=[A-Z][A-Z0-9#-]{3,}(?![A-Za-z0-9_]))(?=[A-Z0-9#-]*\d)[A-Z][A-Z0-9#-]{3,}",
    re.IGNORECASE,
)
_TECHNICAL_TIME_PATTERN = re.compile(r"(?<![A-Za-z0-9_])\d{1,2}H\d{2}(?![A-Za-z0-9_])", re.IGNORECASE)
_TECHNICAL_ORDINAL_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])\d+(?:er|do|ro|to|ta|mo|vo|no)\.?(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
_PROTECTED_NUMBER_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])[-+]?\d+(?:(?:[,.]\d+)+(?:/\d+)?(?=$|[^0-9_])|(?:/\d+)?(?![A-Za-z0-9_]))"
)
_VALIDATION_NUMBER_PATTERN = re.compile(r"(?<![A-Za-z0-9_])\d+(?:[,.]\d+)*(?:/\d+)?")
_MONTH_NUMBER_BY_NAME = {
    "enero": "1", "january": "1", "jan": "1",
    "febrero": "2", "february": "2", "feb": "2",
    "marzo": "3", "march": "3", "mar": "3",
    "abril": "4", "april": "4", "apr": "4",
    "mayo": "5", "may": "5",
    "junio": "6", "june": "6", "jun": "6",
    "julio": "7", "july": "7", "jul": "7",
    "agosto": "8", "august": "8", "aug": "8",
    "septiembre": "9", "setiembre": "9", "september": "9", "sep": "9", "sept": "9",
    "octubre": "10", "october": "10", "oct": "10",
    "noviembre": "11", "november": "11", "nov": "11",
    "diciembre": "12", "december": "12", "dec": "12",
}
_MONTH_NAME_PATTERN = re.compile(
    r"\b(" + "|".join(sorted((re.escape(name) for name in _MONTH_NUMBER_BY_NAME), key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)
_AMBIGUOUS_SHORT_UNITS = {"h", "in", "m"}


def _number_tokens(value: object) -> list[str]:
    # Validation must also see values touching OCR/PDF text (``M3``,
    # ``5/8IN`` or Chinese date suffixes). Protection remains boundary-aware
    # so identifiers are not fragmented into excessive placeholders.
    return _VALIDATION_NUMBER_PATTERN.findall(str(value or ""))


def _derived_number_tokens(value: object, target_language: str) -> list[str]:
    if normalize_language(target_language) != "zh-CN":
        return []
    return [_MONTH_NUMBER_BY_NAME[match.group(1).casefold()] for match in _MONTH_NAME_PATTERN.finditer(str(value or ""))]


def _compiled_measurement_matcher(values: tuple[str, ...]) -> re.Pattern[str] | None:
    unit_patterns = []
    for value in sorted({str(item or "").strip() for item in values if str(item or "").strip()}, key=len, reverse=True):
        unit_patterns.append(re.escape(value).replace(r"\ ", r"\s+"))
    if not unit_patterns:
        return None
    unit = "(?:" + "|".join(unit_patterns) + ")"
    number = r"[-+]?\d+(?:[,.]\d+)*(?:/\d+)?"
    range_number = rf"{number}(?:\s*[-–]\s*{number})?"
    return re.compile(
        rf"(?<![A-Za-z0-9_]){range_number}\s*{unit}(?:\s*[/×x-]\s*{unit})*(?![A-Za-z0-9_])",
        re.IGNORECASE,
    )


def translation_memory_version(
    terms: TermsConfig,
    tuning: TranslationTuningConfig,
    target_language: str,
    model_identity: str = "",
) -> str:
    material = {
        "pipeline": TRANSLATION_PIPELINE_VERSION,
        "target": normalize_language(target_language),
        "model": model_identity,
        "tuning": {
            "version": tuning.version,
            "system_prompt": tuning.system_prompt,
            "translation_instruction": tuning.translation_instruction,
            "numbers": tuning.protect_numbers,
            "units": tuning.protect_units,
            "acronyms": tuning.protect_acronyms,
            "proper_nouns": tuning.protect_proper_nouns,
        },
        "protected": {
            "units": terms.units,
            "acronyms": terms.acronyms,
            "proper_nouns": terms.proper_nouns,
        },
        "locked_terms": [
            (entry.id, entry.zh, entry.en, entry.es, entry.aliases, entry.enabled, entry.protected)
            for entry in terms.entries
            if entry.enabled and entry.protected
        ],
    }
    digest = hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return f"{TRANSLATION_PIPELINE_VERSION}-{digest}"[:64]


def _compiled_literal_matchers(values: tuple[str, ...], *, unit: bool = False) -> list[tuple[str, re.Pattern[str]]]:
    matchers: list[tuple[str, re.Pattern[str]]] = []
    for value in values:
        clean_value = str(value or "").strip()
        if not clean_value:
            continue
        escaped = re.escape(clean_value).replace(r"\ ", r"\s+")
        boundary = rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])" if unit else _term_regex(clean_value)
        matchers.append((clean_value, re.compile(boundary, re.IGNORECASE)))
    return sorted(matchers, key=lambda item: len(item[0]), reverse=True)


def _unit_match_allowed(text: str, match: re.Match[str], configured_unit: str) -> bool:
    normalized = re.sub(r"[^a-z]", "", configured_unit.casefold())
    if normalized not in _AMBIGUOUS_SHORT_UNITS:
        return True
    before = text[max(0, match.start() - 20):match.start()]
    after = text[match.end():min(len(text), match.end() + 20)]
    # ``M/LWD`` means measurement/logging while drilling; the leading M is an
    # acronym component, not the metre unit. Do not turn it into a unit
    # integrity failure when the translation normalizes the acronym to LWD.
    if normalized == "m" and re.match(r"^\s*/\s*[A-Z]{2,}\b", after):
        return False
    return bool(
        re.search(r"\d[\d\s.,/'\"-]*$", before)
        or re.match(r"^\s*[/×x*-]\s*(?:\d|[A-Za-z])", after)
        or re.search(r"[/×x*-]\s*$", before)
    )


def _protected_unit_tokens(text: object, matchers: list[tuple[str, re.Pattern[str]]]) -> list[str]:
    value = str(text or "")
    candidates: list[tuple[int, int, str]] = []
    for configured_unit, matcher in matchers:
        for match in matcher.finditer(value):
            if _unit_match_allowed(value, match, configured_unit):
                candidates.append((match.start(), match.end(), match.group(0)))
    selected: list[tuple[int, int, str]] = []
    for candidate in sorted(candidates, key=lambda item: (item[0], -(item[1] - item[0]))):
        start, end, _token = candidate
        if any(start < existing_end and end > existing_start for existing_start, existing_end, _existing in selected):
            continue
        selected.append(candidate)
    return [token for _start, _end, token in sorted(selected, key=lambda item: item[0])]


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

    return normalize_multiline(re.sub(r"[ \t]{2,}", " ", duplicate_note.sub(replace_duplicate, text)))


def _is_text_value(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and bool(re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\u4e00-\u9fff]", value))


def _clean_text(value: Any) -> str:
    return normalize_multiline(value)


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
