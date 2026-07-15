from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import threading
import time
import unicodedata
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
    normalize_pdf_ocr_text,
    normalize_translation_paragraph,
    split_preserving_layout,
)


DEFAULT_TERMS_PATH = Path(__file__).with_name("drilling_terms.json")
LANGUAGES = ("zh-CN",)
TARGET_LANGUAGE = "zh-CN"
PROMPT_VERSION = "drilling-daily-v7"
DEFAULT_SYSTEM_PROMPT = "你是石油钻完井日报专业翻译器，熟悉钻井、完井、修井和搬迁作业术语。"
DEFAULT_TRANSLATION_INSTRUCTION = (
    "不得总结、删减、解释或添加说明；保持原文事实顺序和技术含义，同时使用符合目标语言习惯的完整句子。"
    "日期只要求年、月、日数值准确，月份名称和年月日语序必须按目标语言本地化；列表中的每个事项应保持主语、动作、对象和时间完整。"
)
DEFAULT_BUSINESS_PROMPT_TEMPLATES = (
    ("drilling", "结合钻进、循环、起下钻、BHA、井深及钻井参数的作业时序，使用中国钻井日报常用表达。"),
    ("completion", "结合完井管柱、射孔、压裂、测试和井口作业语义，使用中国完井日报常用表达。"),
    ("workover", "结合修井管柱、打捞、冲洗、试压和井筒处置语义，使用中国修井日报常用表达。"),
    ("move", "结合钻机搬迁、运输、吊装、组装和场地作业时序，使用中国钻机搬迁日报常用表达。"),
)
DEFAULT_OLLAMA_CHUNK_CHARS = 6000
DEFAULT_OPENAI_COMPATIBLE_CHUNK_CHARS = 2500
TRANSLATION_PIPELINE_VERSION = "report-context-v14-deterministic-validation"
TERM_TYPES = {"protected", "preferred", "contextual", "phrase"}
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
    contextual_translation: bool = True
    validate_results: bool = True
    date_format: str = "iso"
    ambiguous_units: tuple[str, ...] = ()
    unit_aliases: tuple[tuple[str, tuple[str, ...]], ...] = ()
    unit_context_exclusions: tuple[tuple[str, str], ...] = ()
    experience_rules: tuple[tuple[str, str, str], ...] = ()
    prompt_templates: tuple[tuple[str, str], ...] = DEFAULT_BUSINESS_PROMPT_TEMPLATES
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
        raw_templates = source.get("prompt_templates") if isinstance(source.get("prompt_templates"), dict) else {}
        prompt_templates = tuple(
            (report_type, str(raw_templates.get(report_type, default_text) or default_text).strip())
            for report_type, default_text in DEFAULT_BUSINESS_PROMPT_TEMPLATES
        )
        protections = source.get("protections") if isinstance(source.get("protections"), dict) else {}
        contextual_translation = bool(protections.get("contextual_translation", True))
        validate_results = bool(protections.get("validate_results", True))
        ambiguous_units = tuple(
            dict.fromkeys(
                str(item or "").strip().casefold()
                for item in (protections.get("ambiguous_units") if isinstance(protections.get("ambiguous_units"), list) else [])
                if str(item or "").strip()
            )
        )
        raw_unit_aliases = protections.get("unit_aliases") if isinstance(protections.get("unit_aliases"), dict) else {}
        unit_aliases = tuple(sorted(
            (
                str(unit or "").strip().casefold(),
                _string_tuple(aliases),
            )
            for unit, aliases in raw_unit_aliases.items()
            if str(unit or "").strip() and _string_tuple(aliases)
        ))
        unit_context_exclusions: list[tuple[str, str]] = []
        raw_exclusions = protections.get("unit_context_exclusions") if isinstance(protections.get("unit_context_exclusions"), list) else []
        for item in raw_exclusions:
            if not isinstance(item, dict):
                continue
            pattern = str(item.get("pattern", "") or "").strip()
            raw_units = item.get("units") if isinstance(item.get("units"), list) else [item.get("unit", "")]
            if not pattern:
                continue
            for configured_unit in raw_units:
                unit = str(configured_unit or "").strip().casefold()
                if unit:
                    unit_context_exclusions.append((unit, pattern))
        experience_rules: list[tuple[str, str, str]] = []
        raw_experience_rules = source.get("experience_rules") if isinstance(source.get("experience_rules"), list) else []
        for item in raw_experience_rules:
            if not isinstance(item, dict) or not item.get("enabled", True):
                continue
            instruction = str(item.get("instruction", "") or "").strip()
            if not instruction:
                continue
            experience_rules.append((
                str(item.get("report_type", "") or "").strip().lower(),
                str(item.get("field_code", "") or "").strip(),
                instruction,
            ))
        return cls(
            report_fields=report_fields,
            row_fields=row_fields,
            system_prompt=str(prompt.get("system_prompt", "") or DEFAULT_SYSTEM_PROMPT).strip(),
            translation_instruction=str(prompt.get("translation_instruction", "") or DEFAULT_TRANSLATION_INSTRUCTION).strip(),
            protect_numbers=bool(protections.get("numbers", True)),
            protect_units=bool(protections.get("units", True)),
            protect_acronyms=bool(protections.get("acronyms", True)),
            protect_proper_nouns=bool(protections.get("proper_nouns", True)),
            contextual_translation=contextual_translation,
            validate_results=validate_results,
            ambiguous_units=ambiguous_units,
            unit_aliases=unit_aliases,
            unit_context_exclusions=tuple(unit_context_exclusions),
            experience_rules=tuple(experience_rules),
            prompt_templates=prompt_templates,
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
    term_type: str = "preferred"
    strict_preserve: bool = False
    priority: int = 50
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

    @property
    def glossary_type(self) -> str:
        return self.term_type if self.term_type in TERM_TYPES else "preferred"


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
    context: dict[str, Any] = field(default_factory=dict)


class OllamaTranslationEngine:
    name = "ollama"

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen3.5:9b",
        temperature: float = 0.0,
        thinking_mode: str = "disabled",
        request_options: dict[str, Any] | None = None,
        telemetry: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.thinking_mode = _normalize_thinking_mode(thinking_mode)
        self.request_options = _safe_request_options(request_options)
        self.telemetry = telemetry

    def _trace(self, event: str, **fields: Any) -> None:
        if not self.telemetry:
            return
        try:
            self.telemetry({"event": event, "provider": self.name, "model": self.model, **fields})
        except Exception:
            pass

    def translate_items(self, items: list[dict[str, Any]], target_language: str, timeout_seconds: float) -> dict[str, str]:
        if not items:
            return {}
        if any(len(str(item.get("source_text", "") or "")) > 6000 for item in items):
            return self._translate_with_long_text_splitting(items, target_language, timeout_seconds)
        try:
            translated = self._request_translation(items, target_language, timeout_seconds, strict=False)
        except Exception:
            translated = self._request_translation(items, target_language, timeout_seconds, strict=True)
        invalid_errors = {
            str(item.get("id", "")): error
            for item in items
            if (error := _translation_quality_error(
                str(item.get("source_text", "") or ""),
                str(translated.get(str(item.get("id", "")), "") or ""),
                target_language,
            ))
        }
        if invalid_errors:
            retry_items = [
                _translation_repair_item(
                    item,
                    str(translated.get(str(item.get("id", "")), "") or ""),
                    invalid_errors[str(item.get("id", ""))],
                )
                for item in items
                if str(item.get("id", "")) in invalid_errors
            ]
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
        prompt = _ollama_batch_prompt(items, target_language, strict=strict)
        prompt_prefix_hash = source_hash(_prompt_system_message(items, target_language))[:16]
        payload = {
            "model": self.model,
            "stream": False,
            "think": self.thinking_mode == "enabled",
            "prompt": prompt,
            "options": {
                "temperature": self.temperature,
                "top_p": 0.2,
                "num_predict": 4096,
            },
        }
        payload.update(self.request_options)
        payload["model"] = self.model
        payload["prompt"] = prompt
        endpoint = f"{self.base_url}/api/generate"
        started = time.monotonic()
        self._trace(
            "model_wire_request",
            target_language=target_language,
            strict=strict,
            endpoint=endpoint,
            prompt_prefix_hash=prompt_prefix_hash,
            request_payload=payload,
        )
        try:
            data = _post_json(endpoint, payload, timeout_seconds)
        except Exception as exc:
            self._trace("model_wire_response", target_language=target_language, strict=strict, prompt_prefix_hash=prompt_prefix_hash, elapsed_ms=round((time.monotonic() - started) * 1000), error=str(exc))
            raise
        self._trace(
            "model_wire_response",
            target_language=target_language,
            strict=strict,
            prompt_prefix_hash=prompt_prefix_hash,
            elapsed_ms=round((time.monotonic() - started) * 1000),
            usage_metrics=_provider_usage_metrics(data),
            raw_response=data,
        )
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
        telemetry: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.thinking_mode = _normalize_thinking_mode(thinking_mode)
        self.request_options = _safe_request_options(request_options)
        self.telemetry = telemetry

    def _trace(self, event: str, **fields: Any) -> None:
        if not self.telemetry:
            return
        try:
            self.telemetry({"event": event, "provider": self.name, "model": self.model, **fields})
        except Exception:
            pass

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
        invalid_errors = {
            str(item.get("id", "")): error
            for item in items
            if (error := _openai_item_quality_error(
                item,
                str(translated.get(str(item.get("id", "")), "") or ""),
                target_language,
            ))
        }
        if invalid_errors:
            # A successful batch response can still contain copied source text or
            # otherwise unusable translations. Retrying the same batch and prompt
            # tends to reproduce that response (and makes long batches more likely
            # to time out), so recover only the invalid items with the strict prompt.
            for item in items:
                item_id = str(item.get("id", ""))
                if item_id not in invalid_errors:
                    continue
                retry_item = _translation_repair_item(item, str(translated.get(item_id, "") or ""), invalid_errors[item_id])
                retry_result = self._request_translation(
                    [retry_item],
                    target_language,
                    timeout_seconds,
                    strict=True,
                )
                translated[item_id] = str(retry_result.get(item_id, "") or "")
                retry_issue = _openai_item_quality_error(item, translated[item_id], target_language)
                if retry_issue:
                    # Protect only the class of value that still failed. When a
                    # required company/model token is missing, masking every
                    # number also masks date components and can make the repair
                    # turn a correct date into a fragmented or reordered one.
                    protected_item, protected_values = _surgically_protect_values(
                        item,
                        protect_numbers="numeric values" in retry_issue,
                    )
                    if protected_values:
                        protected_result = self._request_translation(
                            [protected_item],
                            target_language,
                            timeout_seconds,
                            strict=True,
                        )
                        protected_text = str(protected_result.get(item_id, "") or "")
                        expected_tokens = Counter(
                            _PROTECTED_PLACEHOLDER_PATTERN.findall(str(protected_item.get("source_text", "") or ""))
                        )
                        returned_tokens = Counter(_PROTECTED_PLACEHOLDER_PATTERN.findall(protected_text))
                        # A repair response is allowed to change prose, but it
                        # must never duplicate one protected value while dropping
                        # another. Keep the previous strict draft when that
                        # happens instead of turning a formatting issue into a
                        # new numeric-value error.
                        if returned_tokens == expected_tokens:
                            repaired_text = _restore_surgically_protected_values(
                                protected_text,
                                protected_values,
                            )
                            if not _openai_item_quality_error(item, repaired_text, target_language):
                                translated[item_id] = repaired_text

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
        system_message = _prompt_system_message(items, target_language)
        prompt_prefix_hash = source_hash(system_message)[:16]
        messages = [
            {"role": "system", "content": system_message},
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
        endpoint = _chat_completions_url(self.base_url)
        started = time.monotonic()
        self._trace(
            "model_wire_request",
            target_language=target_language,
            strict=strict,
            endpoint=endpoint,
            prompt_prefix_hash=prompt_prefix_hash,
            request_payload=payload,
        )
        try:
            data = _post_json(endpoint, payload, timeout_seconds, headers=_auth_headers(self.api_key))
        except Exception as exc:
            self._trace("model_wire_response", target_language=target_language, strict=strict, prompt_prefix_hash=prompt_prefix_hash, elapsed_ms=round((time.monotonic() - started) * 1000), error=str(exc))
            raise
        self._trace(
            "model_wire_response",
            target_language=target_language,
            strict=strict,
            prompt_prefix_hash=prompt_prefix_hash,
            elapsed_ms=round((time.monotonic() - started) * 1000),
            usage_metrics=_provider_usage_metrics(data),
            raw_response=data,
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
        # Keep the production path predictable: one initial request and at most
        # one focused repair/transport retry. More attempts tend to rewrite
        # already-correct prose and amplify a bad validation diagnosis.
        self.retry_count = min(1, max(0, retry_count))
        self.tuning = tuning or TranslationTuningConfig()
        self.chunk_max_chars = _translation_chunk_max_chars(engine.name, chunk_max_chars)
        self._term_matchers = _compiled_term_matchers(terms.entries, self.target_language)
        self._term_source_matchers = _compiled_glossary_matchers(terms.entries)
        self._protected_acronym_matchers = _compiled_literal_matchers(terms.acronyms, case_sensitive=True)
        self._protected_unit_matchers = _compiled_literal_matchers(terms.units, unit=True)
        self._protected_proper_noun_matchers = _compiled_literal_matchers(terms.proper_nouns)
        self._protected_measurement_matcher = _compiled_measurement_matcher(terms.units)
        self._ambiguous_units = frozenset(self.tuning.ambiguous_units)
        self._unit_aliases = {unit.casefold(): aliases for unit, aliases in self.tuning.unit_aliases}
        self._unit_context_exclusions = _compiled_unit_context_exclusions(self.tuning.unit_context_exclusions)
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
        used_item_ids: set[str] = set()
        for unit in units:
            source_text = _clean_text(unit.text)
            if not source_text:
                continue
            cleaned_source_text, cleanup_actions = clean_translation_source(source_text)
            if not cleaned_source_text:
                cleaned_source_text = source_text
            if cleanup_actions:
                self._emit_telemetry(
                    "translation_source_cleaned",
                    field_code=unit.field_code,
                    original_source_text=source_text,
                    cleaned_source_text=cleaned_source_text,
                    cleanup_actions=cleanup_actions,
                )
            source_chars += len(source_text)
            source_language = detect_language(cleaned_source_text)
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
            if not text_needs_translation(cleaned_source_text, target_language):
                rows.append({**base, "translated_text": _normalize_item_layout(unit.field_code, cleaned_source_text), "translation_status": "NOT_REQUIRED", "error_message": ""})
                continue
            memory_text = str(self.translation_memory.get(base["source_hash"], "") or "").strip()
            if memory_text and not _translation_quality_error(cleaned_source_text, memory_text, target_language):
                rows.append({**base, "translated_text": _normalize_item_layout(unit.field_code, memory_text), "translation_status": "COMPLETED", "error_message": ""})
                self._emit_telemetry("memory_hit", target_language=target_language, field_code=unit.field_code, source_chars=len(source_text))
                continue
            glossary_started = time.monotonic()
            glossary = self._term_glossary(cleaned_source_text, target_language)
            model_source_text = _normalize_item_layout(unit.field_code, cleaned_source_text)
            request_source_text, protected_tokens = self._prepare_source_for_model(
                model_source_text,
                target_language,
            )
            preserve_terms = self._preserve_terms(cleaned_source_text, glossary)
            protected_source_terms = {
                normalize_inline(item.get("source", "")).casefold()
                for item in protected_tokens
                if isinstance(item, dict) and normalize_inline(item.get("source", ""))
            }
            preserve_terms = [
                term for term in preserve_terms
                if normalize_inline(term).casefold() not in protected_source_terms
            ]
            if _is_technical_literal_fragment(model_source_text):
                rows.append({**base, "translated_text": model_source_text, "translation_status": "NOT_REQUIRED", "error_message": ""})
                continue
            glossary_seconds += time.monotonic() - glossary_started
            glossary_hits += len(glossary)
            item_id = _translation_unit_id(unit)
            if item_id in used_item_ids:
                identity = f"{unit.entity_id}|{unit.path}|{unit.field_code}"
                item_id = f"{item_id}-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:8]}"
            used_item_ids.add(item_id)
            pending.append({
                "id": item_id,
                "unit": unit,
                "base": base,
                "source_text": request_source_text,
                "monitor_source_text": cleaned_source_text,
                "source_language": source_language,
                "glossary": glossary,
                "preserve_terms": preserve_terms,
                "field_code": unit.field_code,
                "paragraph_layout": _uses_paragraph_layout(unit.field_code),
                "context_group": _translation_context_group(unit),
                "prompt_context": self._prompt_context(protected_tokens, report_context, unit.context),
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
            for item, row in zip(chunk, chunk_rows):
                translated_text = str(row.get("translated_text", "") or "")
                self._emit_telemetry(
                    "translation_item_final",
                    target_language=target_language,
                    entity_type=row.get("entity_type", ""),
                    entity_id=row.get("entity_id", ""),
                    field_code=row.get("field_code", ""),
                    original_source_text=item.get("monitor_source_text", ""),
                    model_source_text=item.get("source_text", ""),
                    matched_terms=item.get("glossary", []),
                    protected_terms=item.get("preserve_terms", []),
                    prompt_context=item.get("prompt_context", {}),
                    final_text=translated_text,
                    translation_status=row.get("translation_status", ""),
                    error_message=row.get("error_message", ""),
                    quality_checks=(
                        self.quality_checks(str(item.get("monitor_source_text", "") or ""), translated_text, target_language)
                        if translated_text else []
                    ),
                )
            rows.extend(chunk_rows)
            if chunk_rows and on_rows:
                on_rows(list(chunk_rows))
            completed_units += len(chunk)
            if on_progress:
                on_progress(completed_units, len(units))
        return rows

    def prompt_preview(
        self,
        text: str,
        target_language: str,
        *,
        report_context: dict[str, Any] | None = None,
        event_context: dict[str, Any] | None = None,
        field_code: str = "translation_test.text",
    ) -> str:
        item = self.translation_diagnostics(
            text,
            target_language,
            report_context=report_context,
            event_context=event_context,
            field_code=field_code,
        )["request_item"]
        if str(self.engine.name or "").lower() == "openai-compatible":
            return (
                f"System:\n{_prompt_system_message([item], target_language)}\n\n"
                f"User:\n{_openai_batch_prompt([item], target_language, strict=False)}"
            )
        return _ollama_batch_prompt([item], target_language, strict=False)

    def translation_diagnostics(
        self,
        text: str,
        target_language: str,
        *,
        report_context: dict[str, Any] | None = None,
        event_context: dict[str, Any] | None = None,
        field_code: str = "translation_test.text",
    ) -> dict[str, Any]:
        source_text = _clean_text(text)
        cleaned_source_text, cleanup_actions = clean_translation_source(source_text)
        cleaned_source_text = cleaned_source_text or source_text
        request_source_text, protected_tokens = self._prepare_source_for_model(
            cleaned_source_text,
            target_language,
        )
        glossary = self._term_glossary(cleaned_source_text, target_language)
        preserve_terms = self._preserve_terms(cleaned_source_text, glossary)
        item = {
            "id": "0",
            "field_code": field_code,
            "source_language": detect_language(source_text),
            "source_text": request_source_text,
            "monitor_source_text": cleaned_source_text,
            "glossary": glossary,
            "preserve_terms": preserve_terms,
            "prompt_context": self._prompt_context(protected_tokens, report_context, event_context),
            "protected_tokens": protected_tokens,
        }
        return {
            "contextual_translation": self.tuning.contextual_translation,
            "validate_results": self.tuning.validate_results,
            "source_text": source_text,
            "cleaned_source_text": cleaned_source_text,
            "cleanup_actions": cleanup_actions,
            "request_source_text": request_source_text,
            "matched_terms": glossary,
            "protected_terms": preserve_terms,
            "placeholder_count": len(protected_tokens),
            "request_item": item,
        }

    def quality_checks(self, source_text: str, translated_text: str, target_language: str | None = None) -> list[dict[str, str]]:
        language = normalize_language(target_language or self.target_language)
        glossary = self._term_glossary(source_text, language)
        preserve_terms = self._preserve_terms(source_text, glossary)
        checks: list[dict[str, str]] = []
        number_error = _numeric_quality_error(
            source_text,
            translated_text,
            language,
            self.tuning.date_format,
        ) if self.tuning.validate_results and self.tuning.protect_numbers else ""
        checks.append({
            "rule": "number_integrity",
            "label": "数字与数值精度",
            "status": "failed" if number_error else "passed" if self.tuning.validate_results else "skipped",
            "detail": number_error or ("结果校验已关闭" if not self.tuning.validate_results else ""),
        })
        date_error = _calendar_date_quality_error(
            source_text,
            translated_text,
            language,
            self.tuning.date_format,
        ) if self.tuning.validate_results and self.tuning.protect_numbers else ""
        checks.append({
            "rule": "calendar_date_localization",
            "label": "日期顺序与月份本地化",
            "status": "failed" if date_error else "passed" if self.tuning.validate_results else "skipped",
            "detail": date_error or ("结果校验已关闭" if not self.tuning.validate_results else ""),
        })
        validation_text = _restore_preserved_term_variants(translated_text, preserve_terms)
        missing_preserved = [term for term in preserve_terms if not _preserved_term_present(term, validation_text)] if self.tuning.validate_results else []
        checks.append({
            "rule": "protected_terms",
            "label": "编号、型号与严格保护项",
            "status": "failed" if missing_preserved else "passed" if self.tuning.validate_results else "skipped",
            "detail": f"missing={missing_preserved[:8]}" if missing_preserved else ("结果校验已关闭" if not self.tuning.validate_results else ""),
        })
        unit_error = _semantic_unit_quality_error(
            source_text,
            translated_text,
            self._protected_unit_matchers,
            ambiguous_units=self._ambiguous_units,
            exclusions=self._unit_context_exclusions,
        ) if self.tuning.validate_results and self.tuning.protect_units else ""
        checks.append({
            "rule": "unit_integrity",
            "label": "计量单位语义",
            "status": "failed" if unit_error else "passed" if self.tuning.validate_results else "skipped",
            "detail": unit_error or ("结果校验已关闭" if not self.tuning.validate_results else ""),
        })
        action_warning = _action_completeness_warning(source_text, translated_text)
        checks.append({
            "rule": "action_completeness",
            "label": "主要作业动作",
            "status": "warning" if action_warning else "passed",
            "detail": action_warning,
        })
        preferred_missing = [
            str(item.get("target", "") or "")
            for item in glossary
            if item.get("type") in {"preferred", "phrase"}
            and str(item.get("target", "") or "")
            and str(item.get("target", "") or "").casefold() not in translated_text.casefold()
        ]
        checks.append({
            "rule": "terminology_consistency",
            "label": "标准术语口径",
            "status": "warning" if preferred_missing else "passed",
            "detail": f"not_used={preferred_missing[:8]}" if preferred_missing else "",
        })
        return checks

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
                sum(
                    1
                    for token in item.get("protected_tokens", [])
                    if not isinstance(token, dict)
                    or token.get("kind") not in {"calendar_date", "context_unit"}
                )
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
                if (
                    _is_technical_literal_fragment(natural_fragment)
                    or _is_deterministic_protected_fragment(part_id, part.text)
                ):
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

    def _prepare_source_for_model(self, text: str, target_language: str) -> tuple[str, list[dict[str, str]]]:
        # Contextual mode keeps dates and ordinary numbers visible so the
        # model can place them naturally in the Chinese sentence. Deterministic
        # validation can enforce their integrity afterwards when enabled.
        # Measurement units and compact technical times remain masked because
        # their spelling is invariant and does not control sentence order.
        if self.tuning.contextual_translation and (self.tuning.protect_numbers or self.tuning.protect_units):
            return self._protect_contextual_invariants(text, target_language)
        return text, []

    def _mask_protection_candidates(
        self,
        text: str,
        candidates: list[tuple[int, int, int, str, str]],
    ) -> tuple[str, list[dict[str, str]]]:
        """Mask non-overlapping invariant values while preserving source order."""
        selected: list[tuple[int, int, int, str, str]] = []
        for candidate in sorted(candidates, key=lambda item: (item[2], -(item[1] - item[0]), item[0])):
            start, end, _priority, _replacement, _kind = candidate
            if any(start < existing_end and end > existing_start for existing_start, existing_end, _p, _r, _k in selected):
                continue
            selected.append(candidate)
        selected.sort(key=lambda item: item[0])
        if not selected:
            return text, []
        pieces: list[str] = []
        protected_tokens: list[dict[str, str]] = []
        cursor = 0
        for index, (start, end, _priority, replacement, kind) in enumerate(selected):
            token = f"[[P{index}]]"
            pieces.extend((text[cursor:start], token))
            protected_tokens.append({
                "token": token,
                "replacement": replacement,
                "source": text[start:end],
                "kind": kind,
            })
            cursor = end
        pieces.append(text[cursor:])
        return "".join(pieces), protected_tokens

    def _protect_contextual_invariants(self, text: str, target_language: str) -> tuple[str, list[dict[str, str]]]:
        candidates: list[tuple[int, int, int, str, str]] = []

        if self.tuning.protect_numbers and normalize_language(target_language) == "zh-CN":
            for match in _TECHNICAL_TIME_PATTERN.finditer(text):
                candidates.append((match.start(), match.end(), -2, match.group(0), "technical_time"))
        if self.tuning.protect_units:
            # In contextual mode protect only the unit spelling. Masking the
            # whole measurement (for example ``5/8IN``) hides the numeric fact
            # and encourages the model to invent a duplicate localized value
            # next to the placeholder.
            for configured_value, matcher in self._protected_unit_matchers:
                for match in matcher.finditer(text):
                    if not _unit_match_allowed(
                        text,
                        match,
                        configured_value,
                        ambiguous_units=self._ambiguous_units,
                        exclusions=self._unit_context_exclusions,
                    ):
                        continue
                    candidates.append((match.start(), match.end(), -1, match.group(0), "context_unit"))
        return self._mask_protection_candidates(text, candidates)

    def _protect_source_text(self, text: str, target_language: str) -> tuple[str, list[dict[str, str]]]:
        # Apply the same hard protection to every provider. Prompt-only unit
        # instructions are not reliable enough: models may localize FT to 英尺 or
        # partially rewrite compound units such as PSI/FT. Measurements and units
        # are therefore masked before the request and restored byte-for-byte.
        candidates: list[tuple[int, int, int, str, str]] = []

        def add_matches(matchers: list[tuple[str, re.Pattern[str]]], priority: int, *, units: bool = False) -> None:
            for configured_value, matcher in matchers:
                for match in matcher.finditer(text):
                    if units and not _unit_match_allowed(
                        text,
                        match,
                        configured_value,
                        ambiguous_units=self._ambiguous_units,
                        exclusions=self._unit_context_exclusions,
                    ):
                        continue
                    candidates.append((match.start(), match.end(), priority, match.group(0), "protected_value"))

        if self.tuning.protect_units and self._protected_measurement_matcher:
            for match in self._protected_measurement_matcher.finditer(text):
                candidates.append((match.start(), match.end(), -1, match.group(0), "measurement"))
        if self.tuning.protect_acronyms:
            add_matches(self._protected_acronym_matchers, 0)
        if self.tuning.protect_units:
            add_matches(self._protected_unit_matchers, 0, units=True)
        if self.tuning.protect_proper_nouns:
            add_matches(self._protected_proper_noun_matchers, 0)
        if self.tuning.protect_numbers:
            if normalize_language(target_language) == "zh-CN":
                for date in _calendar_date_matches(text):
                    candidates.append((
                        date.start,
                        date.end,
                        -4,
                        _localized_calendar_date_value(
                            date.year,
                            date.month,
                            date.day,
                            target_language,
                            self.tuning.date_format,
                        ),
                        "calendar_date",
                    ))
            # Protect mixed alpha-numeric equipment/well identifiers as one
            # value.  Protecting only their numeric suffix would split ST-80 or
            # SHSG-160 into meaningless prose fragments.
            for match in _TECHNICAL_IDENTIFIER_PATTERN.finditer(text):
                candidates.append((match.start(), match.end(), -2, match.group(0), "technical_identifier"))
            for match in _TECHNICAL_TIME_PATTERN.finditer(text):
                candidates.append((match.start(), match.end(), -1, match.group(0), "technical_time"))
            for match in _TECHNICAL_ORDINAL_PATTERN.finditer(text):
                candidates.append((match.start(), match.end(), -1, match.group(0), "ordinal"))
            for match in _PROTECTED_NUMBER_PATTERN.finditer(text):
                candidates.append((match.start(), match.end(), 2, match.group(0), "number"))
        for entry, _source_value, matcher in self._term_source_matchers:
            if not entry.protected:
                continue
            replacement = entry.value(target_language)
            if not replacement:
                continue
            for match in matcher.finditer(text):
                candidates.append((match.start(), match.end(), 1, replacement, "term"))

        return self._mask_protection_candidates(text, candidates)

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
                _set_item_repair_context(item, text, invalid[item_id])
                continue
            text = _repair_protected_token_layout(str(item.get("source_text", "") or ""), text)
            text = self._remove_localized_aliases_beside_unit_tokens(text, protected_tokens)
            for token_data in protected_tokens:
                if not isinstance(token_data, dict):
                    continue
                token = str(token_data.get("token", "") or "")
                replacement = str(token_data.get("replacement", "") or "")
                if token:
                    if token_data.get("kind") == "calendar_date":
                        # The model may move a date in front of a time. If the
                        # placeholder then touches the time (``[[P0]]14:00``),
                        # direct expansion creates ``2026-05-3014:00``. Restore
                        # a numeric boundary before expanding the token.
                        text = re.sub(rf"{re.escape(token)}(?=\d)", f"{token} ", text)
                        text = re.sub(rf"(?<=\d){re.escape(token)}", f" {token}", text)
                    text = text.replace(token, replacement)
            preserve_terms = item.get("preserve_terms", []) if isinstance(item.get("preserve_terms"), list) else []
            text = _restore_preserved_term_variants(text, preserve_terms)
            if self.tuning.validate_results and self.tuning.protect_numbers:
                text = _normalize_yearless_calendar_dates(
                    item.get("monitor_source_text", ""),
                    text,
                    self.target_language,
                )
                text = _restore_equivalent_numeric_formats(
                    item.get("monitor_source_text", ""),
                    text,
                    self.target_language,
                    self.tuning.date_format,
                )
                date_error = _calendar_date_quality_error(
                    item.get("monitor_source_text", ""),
                    text,
                    self.target_language,
                    self.tuning.date_format,
                )
                if date_error:
                    invalid[item_id] = f"{date_error} for item {item_id}"
                    _set_item_repair_context(item, text, invalid[item_id])
                    continue
                number_error = _numeric_quality_error(
                    item.get("monitor_source_text", ""),
                    text,
                    self.target_language,
                    self.tuning.date_format,
                )
                if number_error:
                    invalid[item_id] = f"{number_error} for item {item_id}"
                    _set_item_repair_context(item, text, invalid[item_id])
                    continue
            missing_preserved = [
                term
                for term in preserve_terms
                if normalize_inline(term) and not _preserved_term_present(term, text)
            ] if self.tuning.validate_results else []
            if missing_preserved:
                invalid[item_id] = f"model changed or removed protected terms for item {item_id}; missing={missing_preserved[:8]}"
                _set_item_repair_context(item, text, invalid[item_id])
                continue
            if self.tuning.validate_results and self.tuning.protect_units:
                unit_error = _semantic_unit_quality_error(
                    item.get("monitor_source_text", ""),
                    text,
                    self._protected_unit_matchers,
                    ambiguous_units=self._ambiguous_units,
                    exclusions=self._unit_context_exclusions,
                )
                if unit_error:
                    invalid[item_id] = f"{unit_error} for item {item_id}"
                    _set_item_repair_context(item, text, invalid[item_id])
                    continue
            restored[item_id] = text
        return restored, invalid

    def _remove_localized_aliases_beside_unit_tokens(
        self,
        text: str,
        protected_tokens: list[dict[str, Any]],
    ) -> str:
        """Drop a translated unit only when it directly duplicates a unit token."""
        result = str(text or "")
        configured_units = sorted(self._unit_aliases, key=len, reverse=True)
        for token_data in protected_tokens:
            if not isinstance(token_data, dict) or token_data.get("kind") != "context_unit":
                continue
            token = str(token_data.get("token", "") or "")
            replacement = str(token_data.get("replacement", "") or "")
            if not token or not replacement:
                continue
            unit = next(
                (
                    value for value in configured_units
                    if re.search(rf"{re.escape(value)}\s*$", replacement, re.IGNORECASE)
                ),
                "",
            )
            for alias in self._unit_aliases.get(unit, ()):
                localized = str(alias or "").strip()
                if not localized:
                    continue
                result = re.sub(rf"{re.escape(localized)}\s*{re.escape(token)}", token, result)
                result = re.sub(rf"{re.escape(token)}\s*{re.escape(localized)}", token, result)
        return result

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
            target = source_value if entry.strict_preserve else entry.value(target_language)
            if not target:
                continue
            if not matcher.search(text):
                continue
            key = (source_value.lower(), target)
            if key in seen:
                continue
            seen.add(key)
            records.append({
                "source": source_value,
                "target": target,
                "type": entry.glossary_type,
            })
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
        enabled_matchers: list[tuple[str, re.Pattern[str]]] = []
        if self.tuning.protect_acronyms:
            enabled_matchers.extend(self._protected_acronym_matchers)
        if self.tuning.protect_proper_nouns:
            enabled_matchers.extend(self._protected_proper_noun_matchers)
        for configured, matcher in enabled_matchers:
            if normalize_inline(configured).casefold() in translated_sources:
                continue
            match = matcher.search(text)
            if match:
                values.append(match.group(0))
        for entry, _source_value, matcher in self._term_source_matchers:
            if not entry.strict_preserve:
                continue
            match = matcher.search(text)
            if match:
                values.append(match.group(0))
        if self.tuning.protect_numbers:
            values.extend(
                match.group(0)
                for match in _TECHNICAL_IDENTIFIER_PATTERN.finditer(text)
                if not re.match(r"^\d", match.group(0))
                and not _OCR_ACTION_NUMBER_PATTERN.fullmatch(match.group(0))
            )
        return list(dict.fromkeys(values))[:40]

    def _prompt_context(
        self,
        protected_tokens: list[dict[str, str]] | None = None,
        report_context: dict[str, Any] | None = None,
        event_context: dict[str, Any] | None = None,
    ) -> dict[str, object]:
        protected = [
            str(item.get("source", "") or "")
            for item in (protected_tokens or [])
            if isinstance(item, dict)
            and str(item.get("source", "") or "")
            and not re.match(r"^\s*[-+]?\d", str(item.get("source", "") or ""))
        ]
        selected_report_context = dict(report_context or {})
        report_type = str(selected_report_context.get("report_type", "") or "").strip().lower()
        business_templates = dict(self.tuning.prompt_templates)
        selected_event_context = dict(event_context or {})
        return {
            "system_prompt": self.tuning.system_prompt,
            "translation_instruction": self.tuning.translation_instruction,
            "date_format": self.tuning.date_format,
            "contextual_translation": self.tuning.contextual_translation,
            "validate_results": self.tuning.validate_results,
            "protect_numbers": self.tuning.protect_numbers,
            "protect_units": self.tuning.protect_units,
            "protect_acronyms": self.tuning.protect_acronyms,
            "protect_proper_nouns": self.tuning.protect_proper_nouns,
            "protected_terms": list(dict.fromkeys(protected))[:40],
            "report_context": selected_report_context,
            "event_context": selected_event_context,
            "business_prompt": business_templates.get(report_type, ""),
            # Failure experience is diagnostic evidence, not a source of
            # production Prompt instructions. Keeping this empty makes the
            # baseline Prompt stable across translation runs.
            "experience_rules": [],
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
                if _unit_match_allowed(
                    text,
                    match,
                    configured_unit,
                    ambiguous_units=self._ambiguous_units,
                    exclusions=self._unit_context_exclusions,
                ):
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
    selected_engine = engine or build_engine(config, telemetry=telemetry)
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


def build_engine(
    config: TranslationConfig,
    telemetry: Callable[[dict[str, Any]], None] | None = None,
) -> TranslationEngine:
    engine = config.engine.lower()
    if engine == "ollama":
        return OllamaTranslationEngine(
            base_url=config.ollama_url,
            model=config.ollama_model,
            temperature=config.ollama_temperature,
            thinking_mode=config.thinking_mode,
            request_options=config.request_options,
            telemetry=telemetry,
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
            telemetry=telemetry,
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
                    context=_report_field_event_context(fields, key),
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
                        context=_row_event_context(rows, index, section, key, report_type),
                    ))
    return units


def _report_field_event_context(fields: dict[str, Any], field_name: str) -> dict[str, Any]:
    context = {
        "content_role": field_name,
        "wellbore": fields.get("wellbore"),
        "operation_event": fields.get("event"),
        "primary_reason": fields.get("primaryReason"),
        "current_depth": fields.get("todayMd") or fields.get("currentMd") or fields.get("currentDepth"),
        "previous_depth": fields.get("prevMd") or fields.get("previousMd"),
        "hole_section": fields.get("holeSection") or fields.get("section") or fields.get("holeSize"),
    }
    return _compact_event_context(context)


def _row_event_context(
    rows: list[Any],
    index: int,
    section: str,
    field_name: str,
    report_type: str,
) -> dict[str, Any]:
    row = rows[index] if 0 <= index < len(rows) and isinstance(rows[index], dict) else {}
    previous_row = rows[index - 1] if index > 0 and isinstance(rows[index - 1], dict) else {}
    next_row = rows[index + 1] if index + 1 < len(rows) and isinstance(rows[index + 1], dict) else {}
    context = {
        "content_role": field_name,
        "report_type": report_type,
        "section": section,
        "row_no": row.get("row_no") or index + 1,
        "start_time": row.get("from") or row.get("start_time") or row.get("startTime"),
        "end_time": row.get("to") or row.get("end_time") or row.get("endTime"),
        "duration_hours": row.get("hours") or row.get("duration") or row.get("duration_hours"),
        "operation_code": row.get("op_code") or row.get("operation_code") or row.get("code"),
        "operation_type": row.get("op_type") or row.get("operation_type") or row.get("type"),
        "hole_section": row.get("hole_section") or row.get("holeSection") or row.get("section"),
        "previous_event": previous_row.get("operation_details") or previous_row.get("comments"),
        "next_event": next_row.get("operation_details") or next_row.get("comments"),
    }
    return _compact_event_context(context)


def _compact_event_context(values: dict[str, Any]) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for key, value in values.items():
        if value in (None, "", [], {}):
            continue
        if isinstance(value, str):
            cleaned = normalize_inline(value)
            if not cleaned:
                continue
            context[key] = cleaned[:600]
        else:
            context[key] = value
    return context


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


def _provider_usage_metrics(data: object) -> dict[str, int | float | bool]:
    """Normalize token and prompt-cache counters returned by compatible providers."""
    if not isinstance(data, dict):
        return {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    prompt_details = usage.get("prompt_tokens_details") if isinstance(usage.get("prompt_tokens_details"), dict) else {}

    def first_integer(*values: object) -> int | None:
        for value in values:
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)) and value >= 0:
                return int(value)
        return None

    input_tokens = first_integer(
        usage.get("prompt_tokens"),
        usage.get("input_tokens"),
        data.get("prompt_eval_count"),
    )
    output_tokens = first_integer(
        usage.get("completion_tokens"),
        usage.get("output_tokens"),
        data.get("eval_count"),
    )
    total_tokens = first_integer(usage.get("total_tokens"))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    cached_input_tokens = first_integer(
        prompt_details.get("cached_tokens"),
        usage.get("prompt_cache_hit_tokens"),
        usage.get("cache_read_input_tokens"),
    )
    cache_write_input_tokens = first_integer(
        usage.get("prompt_cache_miss_tokens"),
        usage.get("cache_creation_input_tokens"),
    )

    metrics: dict[str, int | float | bool] = {}
    if input_tokens is not None:
        metrics["input_tokens"] = input_tokens
    if output_tokens is not None:
        metrics["output_tokens"] = output_tokens
    if total_tokens is not None:
        metrics["total_tokens"] = total_tokens
    if cached_input_tokens is not None:
        metrics["cached_input_tokens"] = cached_input_tokens
        metrics["prompt_cache_hit"] = cached_input_tokens > 0
        if input_tokens:
            metrics["prompt_cache_hit_ratio"] = round(cached_input_tokens / input_tokens, 4)
    if cache_write_input_tokens is not None:
        metrics["cache_write_input_tokens"] = cache_write_input_tokens
    return metrics


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
            "event_context": (
                item.get("prompt_context", {}).get("event_context", {})
                if isinstance(item.get("prompt_context"), dict) else {}
            ),
            "repair_context": item.get("repair_context", {}),
        }
        for item in items
    ]
    target = normalize_language(target_language)
    contexts = [item.get("prompt_context", {}) for item in items if isinstance(item.get("prompt_context"), dict)]
    date_format = _normalize_calendar_date_format(contexts[0].get("date_format", "iso") if contexts else "iso")
    retry_date_rule = _calendar_date_format_instruction(date_format, authoritative=False)
    retry_rule = f"上一次结果未满足完整性要求。请重新翻译，并逐项核对{retry_date_rule}、数字、编号和必保术语。" if strict and target == "zh-CN" else (
        "The previous result failed an integrity check. Translate again and verify every number, identifier, and preserved term." if strict else ""
    )
    context = contexts[0] if contexts else {}
    contextual_translation = bool(context.get("contextual_translation", True))
    business_prompt = str(context.get("business_prompt", "") or "").strip() if contextual_translation else ""
    report_context = context.get("report_context", {}) if contextual_translation and isinstance(context.get("report_context"), dict) else {}
    if not contextual_translation:
        for compact_item in compact_items:
            compact_item["segment_context"] = ""
            compact_item["event_context"] = {}
    rules = [business_prompt]
    experience_rules = context.get("experience_rules") if isinstance(context.get("experience_rules"), list) else []
    rules.extend(
        f"已验证经验：{str(rule).strip()}"
        for rule in experience_rules
        if str(rule or "").strip()
    )
    if any(_PROTECTED_PLACEHOLDER_PATTERN.search(str(item.get("source_text", "") or "")) for item in items):
        rules.append("source_text 中形如 [[P0]] 的占位符必须逐字原样保留，不得改写、删除或复制。")
    if any(str(item.get("segment_context", "") or "") for item in compact_items):
        rules.append("带 segment_context 的 source_text 是原句中的自然语言片段；结合脱敏上下文准确翻译该片段，但不要输出上下文或 <PROTECTED> 标记。")
    if any(isinstance(item.get("event_context"), dict) and item.get("event_context") for item in compact_items):
        rules.append("event_context 只用于理解当前作业事件的时间、代码、井段和前后动作，不得翻译或输出上下文字段。")
    if any(isinstance(item.get("repair_context"), dict) and item.get("repair_context") for item in compact_items):
        rules.append("repair_context 表示初译未通过确定性校验；保留初译整体表达，只修复列出的数字、编号、单位或术语问题，不要重新润色全文。")
    if any(item.get("layout") == "paragraph" for item in compact_items):
        rules.append("layout 为 paragraph 的 description 必须作为一个完整连续段落理解和输出，不得按原 PDF 的视觉换行拆句。")
    if retry_rule:
        rules.append(retry_rule)
    system_text = f"{_prompt_system_message(items, target_language)}\n" if include_system_prompt else ""
    return (
        system_text
        +
        f"请按固定翻译策略处理以下日报内容。目标语言：{_language_label(target_language)}。\n"
        + "\n".join(f"- {rule}" for rule in rules if rule)
        + "\n"
        + (f"日报上下文（只用于理解，不要翻译或输出）：\n{json.dumps(report_context, ensure_ascii=False)}\n" if report_context else "")
        +
        "每个输入 id 必须返回一条，不得漏项或改变 id。\n"
        f"Input JSON:\n{json.dumps({'items': compact_items}, ensure_ascii=False)}"
    )


def _translation_output_token_budget(items: list[dict[str, Any]]) -> int:
    source_chars = sum(len(str(item.get("source_text", "") or "")) for item in items)
    return max(4096, min(8192, source_chars * 4 + 2048))


def _translation_repair_item(item: dict[str, Any], draft_translation: str, issue: str) -> dict[str, Any]:
    return {
        **item,
        "repair_context": {
            "draft_translation": str(draft_translation or "")[:12000],
            "issues": [str(issue or "")[:1000]],
        },
    }


def _set_item_repair_context(item: dict[str, Any], draft_translation: str, issue: str) -> None:
    item["repair_context"] = _translation_repair_item(item, draft_translation, issue)["repair_context"]


def _prompt_system_message(items: list[dict[str, Any]], target_language: str) -> str:
    context = items[0].get("prompt_context", {}) if items and isinstance(items[0].get("prompt_context"), dict) else {}
    system_prompt = str(context.get("system_prompt", "") or DEFAULT_SYSTEM_PROMPT).strip()
    additional_instruction = str(context.get("translation_instruction", "") or DEFAULT_TRANSLATION_INSTRUCTION).strip()
    rules = [
        _target_translation_instruction(target_language),
        additional_instruction,
        "glossary 只包含当前原文命中的术语参考：protected 必须保留，preferred 和 phrase 原则上采用，contextual 由上下文决定；不得机械拼接术语。",
        "preserve_terms 中的井号、设备型号、BHA 编号、品牌和作业代码保持原样。",
    ]
    if context.get("contextual_translation", True):
        rules.extend([
            "先理解完整作业过程、动作关系和时序，再使用目标语言对应的石油钻完井行业自然、专业表达。",
            "保持作业事件先后顺序，不要求逐词对应或保留源语言语序；不得总结、遗漏或添加事实。",
            "对于以破折号、星号或加号连续列出的事项，先识别每个完整事项，再逐项翻译；不得把同一事项的主语、动作、对象或日期拆到相邻事项。",
        ])
    if context.get("protect_numbers", True):
        date_format = _normalize_calendar_date_format(context.get("date_format", "iso"))
        rules.append(
            _calendar_date_format_instruction(date_format, authoritative=True)
            + "其他时间、数字、数值精度和设备序列号不得改变。"
        )
    rules.append("只返回严格 JSON，格式为：{\"items\":[{\"id\":\"输入ID\",\"translated_text\":\"译文\"}]}。每个输入 id 必须返回一条。")
    return f"{system_prompt}\n固定翻译策略：\n" + "\n".join(f"- {rule}" for rule in rules if rule)


def _target_translation_instruction(target_language: str) -> str:
    target = normalize_language(target_language)
    return {
        "zh-CN": "将每个 source_text 中的西班牙语或英语自然语言完整翻译成简体中文。全大写的西班牙语或英语仍是正文，必须翻译。",
        "en": "Translate all Spanish or Chinese natural-language prose in every source_text completely into English. ALL-CAPS prose must also be translated.",
        "es": "Traduce completamente al español todo texto natural en chino o inglés de cada source_text. El texto en MAYÚSCULAS también debe traducirse.",
    }.get(target, f"Translate every source_text completely into {_language_label(target_language)}.")


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


def _preserved_term_variant_pattern(term: object) -> re.Pattern[str] | None:
    """Match only separator changes in a protected identifier or name."""
    value = normalize_inline(term)
    chunks = re.findall(r"[^\W_]+", value, flags=re.UNICODE)
    if len(chunks) < 2:
        return None
    body = r"[\s._/\-]*".join(re.escape(chunk) for chunk in chunks)
    return re.compile(rf"(?<!\w){body}(?!\w)", re.IGNORECASE)


def _preserved_term_present(term: object, text: object) -> bool:
    preserved = normalize_inline(term)
    candidate = normalize_inline(text)
    if not preserved:
        return True
    if preserved.casefold() in candidate.casefold():
        return True
    pattern = _preserved_term_variant_pattern(preserved)
    return bool(pattern and pattern.search(candidate))


def _restore_preserved_term_variants(text: object, preserve_terms: object) -> str:
    """Restore safe punctuation-only variants without inventing a missing term."""
    result = str(text or "")
    terms = preserve_terms if isinstance(preserve_terms, (list, tuple)) else []
    for term in sorted((normalize_inline(value) for value in terms), key=len, reverse=True):
        if not term or term.casefold() in normalize_inline(result).casefold():
            continue
        pattern = _preserved_term_variant_pattern(term)
        if pattern and pattern.search(result):
            result = pattern.sub(term, result)
    return result


def _restore_item_validation_placeholders(item: dict[str, Any], text: object) -> str:
    """Expand the current item's invariant tokens before fact validation."""
    restored = str(text or "")
    protected_tokens = item.get("protected_tokens", []) if isinstance(item.get("protected_tokens"), list) else []
    for token_data in protected_tokens:
        if not isinstance(token_data, dict):
            continue
        token = str(token_data.get("token", "") or "")
        if token:
            restored = restored.replace(token, str(token_data.get("replacement", "") or ""))
    return restored


def _openai_item_quality_error(item: dict[str, Any], translated_text: str, target_language: str) -> str:
    source_text = str(item.get("source_text", "") or "")
    if "<PROTECTED>" in str(translated_text or ""):
        return "model leaked protected context marker"
    quality_error = _translation_quality_error(source_text, translated_text, target_language)
    if (
        quality_error == "source text was returned unchanged"
        and normalize_translation_paragraph(source_text).casefold()
        == normalize_translation_paragraph(translated_text).casefold()
        and _is_deterministic_protected_fragment(str(item.get("id", "") or ""), source_text)
    ):
        quality_error = ""
    if quality_error:
        return quality_error
    expected = Counter(_PROTECTED_PLACEHOLDER_PATTERN.findall(source_text))
    returned = Counter(_PROTECTED_PLACEHOLDER_PATTERN.findall(str(translated_text or "")))
    if returned != expected:
        return "model changed, removed, or duplicated protected placeholders"
    preserve_terms = item.get("preserve_terms", []) if isinstance(item.get("preserve_terms"), list) else []
    validation_source = _restore_item_validation_placeholders(item, source_text)
    validation_text = _restore_item_validation_placeholders(item, translated_text)
    validation_text = _restore_preserved_term_variants(validation_text, preserve_terms)
    prompt_context = item.get("prompt_context") if isinstance(item.get("prompt_context"), dict) else {}
    validate_results = bool(prompt_context.get("validate_results", True))
    if validate_results and prompt_context.get("protect_numbers", True):
        date_format = _normalize_calendar_date_format(prompt_context.get("date_format", "iso"))
        date_error = _calendar_date_quality_error(
            validation_source,
            validation_text,
            target_language,
            date_format,
        )
        if date_error:
            return date_error
        number_error = _numeric_quality_error(
            validation_source,
            validation_text,
            target_language,
            date_format,
        )
        if number_error:
            return number_error
    if validate_results:
        for term in preserve_terms:
            preserved = normalize_inline(term)
            if preserved and not _preserved_term_present(preserved, validation_text):
                return f"required preserved term was changed or removed: {preserved}"
    return ""


def _numeric_quality_error(
    source_text: str,
    translated_text: str,
    target_language: str,
    date_format: str = "iso",
) -> str:
    source_for_numbers, translated_for_numbers = _texts_without_calendar_dates(
        source_text,
        translated_text,
        target_language,
        date_format,
    )
    ordinal_numbers: Counter[str] = Counter()
    ordinal_spans: list[tuple[int, int]] = []
    for match in _TECHNICAL_ORDINAL_PATTERN.finditer(source_for_numbers):
        ordinal_spans.append((match.start(), match.end()))
        ordinal_numbers.update(item.canonical for item in _validation_number_matches(match.group(0)))
    source_for_numbers = _mask_spans(source_for_numbers, ordinal_spans)
    source_numbers = Counter(item.canonical for item in _validation_number_matches(source_for_numbers))
    translated_numbers = Counter(item.canonical for item in _validation_number_matches(translated_for_numbers))
    missing = list((source_numbers - translated_numbers).elements())[:8]
    allowed_derived = Counter(
        _canonical_number_token(value)
        for value in _derived_number_tokens(source_for_numbers, target_language)
    )
    # Spanish/English numeric ordinals may naturally become Chinese words
    # (``1er.`` -> ``第一个``). They are optional numeric renderings: allow the
    # original digit when the model uses ``第1个``, but do not require it.
    allowed_derived.update(ordinal_numbers)
    extra = list(((translated_numbers - source_numbers) - allowed_derived).elements())[:8]
    if missing or extra:
        return f"model changed numeric values; missing={missing}; extra={extra}"
    return ""


_UNICODE_FRACTION_VALUES = {
    "¼": "1/4", "½": "1/2", "¾": "3/4",
    "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
}


@dataclass(frozen=True)
class _ValidationNumber:
    start: int
    end: int
    source: str
    canonical: str


def _canonical_number_token(value: object, trailing_context: str = "") -> str:
    """Return a comparison value while retaining the source spelling for output."""
    token = str(value or "").strip()
    for symbol, fraction in _UNICODE_FRACTION_VALUES.items():
        if symbol in token:
            whole = token.replace(symbol, "").strip(" .-")
            return f"{whole} {fraction}".strip()
    malformed_fraction = re.fullmatch(r"(\d+)\s+(\d)(\d)/?", token)
    if malformed_fraction:
        return f"{malformed_fraction.group(1)} {malformed_fraction.group(2)}/{malformed_fraction.group(3)}"
    mixed = re.fullmatch(r"(\d+)(?:\s+|-\s*|\.)(\d+/\d+)", token)
    if mixed:
        return f"{mixed.group(1)} {mixed.group(2)}"
    compact = re.sub(r"\s+", "", token)
    if re.fullmatch(r"[-+]?\d{1,3}(?:,\d{3})+", compact):
        return compact.replace(",", "")
    # In drilling text a dot followed by exactly three digits immediately
    # before a depth marker is an OCR/locale thousands separator, not a decimal.
    if re.fullmatch(r"[-+]?\d{1,3}\.\d{3}", compact) and re.match(
        r"\s*(?:['’′]|ft\b|feet\b|pies\b|m\b|md\b|tvd\b)",
        trailing_context,
        re.IGNORECASE,
    ):
        return compact.replace(".", "")
    # Decimal comma and decimal point are equivalent when the fractional part
    # has one or two digits. The restoration pass puts the source punctuation
    # back before the translation is persisted.
    if re.fullmatch(r"[-+]?\d+,\d{1,2}", compact):
        return compact.replace(",", ".")
    if re.fullmatch(r"\d+", compact):
        return str(int(compact))
    return compact


def _validation_number_matches(value: object) -> list[_ValidationNumber]:
    """Find numeric facts, including common PDF/OCR formatting variants."""
    text = str(value or "")
    candidates: list[tuple[int, int, int, str]] = []
    patterns = (
        (0, re.compile(r"(?<![A-Za-z0-9_])\d+\s+\d{2}/(?=\s*(?:IN(?=\b|英寸)|[\"”]))", re.IGNORECASE)),
        (0, re.compile(r"(?<![A-Za-z0-9_])\d+\s+\d{2}(?=\s*(?:英寸|IN(?=\b|英寸)|[\"”]))", re.IGNORECASE)),
        (0, re.compile(r"(?<![A-Za-z0-9_])\d+(?:\s+|-\s*|\.)\d+/\d+")),
        (0, re.compile(r"(?<![A-Za-z0-9_])\d+\s*[¼½¾⅛⅜⅝⅞]")),
        (1, re.compile(r"(?<![A-Za-z0-9_])\d{1,3}(?:,\s+\d{3})+(?!\d)")),
        (2, _VALIDATION_NUMBER_PATTERN),
    )
    for priority, pattern in patterns:
        for match in pattern.finditer(text):
            candidates.append((match.start(), match.end(), priority, match.group(0)))
    # OCR frequently removes the boundary between an action word and a volume
    # or depth (for example FILTRA1700 or INGRESA10000). A long alphabetic
    # prefix is required so equipment identifiers such as BHA3 stay untouched.
    for match in re.finditer(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{5,}(?P<number>\d{4,})(?![A-Za-z0-9_])", text):
        candidates.append((match.start("number"), match.end("number"), 1, match.group("number")))

    selected: list[tuple[int, int, str]] = []
    for start, end, priority, source in sorted(candidates, key=lambda item: (item[2], item[0], -(item[1] - item[0]))):
        if any(start < current_end and end > current_start for current_start, current_end, _ in selected):
            continue
        selected.append((start, end, source))
    selected.sort(key=lambda item: item[0])
    return [
        _ValidationNumber(start, end, source, _canonical_number_token(source, text[end:end + 16]))
        for start, end, source in selected
    ]


def _restored_number_spelling(match: _ValidationNumber) -> str:
    malformed_fraction = re.fullmatch(r"(\d+)\s+(\d)(\d)/?", match.source.strip())
    if malformed_fraction:
        return f"{malformed_fraction.group(1)} {malformed_fraction.group(2)}/{malformed_fraction.group(3)}"
    return match.source


def _restore_equivalent_numeric_formats(
    source_text: object,
    translated_text: object,
    target_language: str,
    date_format: str = "iso",
) -> str:
    """Put grouping separators back exactly as written in the source.

    Quality validation treats ``13000`` and ``13,000`` as the same value. This
    deterministic pass then restores the source spelling before persistence so
    the model cannot silently change numeric formatting.
    """
    source = str(source_text or "")
    translated = str(translated_text or "")
    source_date_spans = _calendar_date_spans(source) if normalize_language(target_language) == "zh-CN" else []
    source_ordinal_spans = [(match.start(), match.end()) for match in _TECHNICAL_ORDINAL_PATTERN.finditer(source)]

    def overlaps(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
        return any(start < span_end and end > span_start for span_start, span_end in spans)

    source_spellings: dict[str, list[str]] = {}
    for match in _validation_number_matches(source):
        if overlaps(match.start, match.end, source_date_spans + source_ordinal_spans):
            continue
        source_spellings.setdefault(match.canonical, []).append(_restored_number_spelling(match))

    translated_date_spans: list[tuple[int, int]] = []
    if normalize_language(target_language) == "zh-CN":
        for date in _calendar_date_matches(source):
            match = _localized_calendar_date_pattern(date, date_format).search(translated)
            if match:
                translated_date_spans.append((match.start(), match.end()))

    used: Counter[str] = Counter()
    pieces: list[str] = []
    cursor = 0
    for match in _validation_number_matches(translated):
        if overlaps(match.start, match.end, translated_date_spans):
            continue
        token = match.source
        canonical = match.canonical
        choices = source_spellings.get(canonical, [])
        index = used[canonical]
        if index >= len(choices):
            continue
        source_token = choices[index]
        used[canonical] += 1
        if source_token == token:
            continue
        pieces.extend((translated[cursor:match.start], source_token))
        cursor = match.end
    if not pieces:
        return translated
    pieces.append(translated[cursor:])
    return "".join(pieces)


def _surgically_protect_values(
    item: dict[str, Any],
    *,
    protect_numbers: bool = True,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    source_text = str(item.get("source_text", "") or "")
    candidates: list[tuple[int, int, str]] = []
    if protect_numbers:
        calendar_spans = _calendar_date_spans(source_text)
        for matcher in (_TECHNICAL_TIME_PATTERN, _PROTECTED_NUMBER_PATTERN):
            for match in matcher.finditer(source_text):
                if any(match.start() < end and match.end() > start for start, end in calendar_spans):
                    continue
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


def _translation_unit_id(unit: TextUnit) -> str:
    """Build a short business-readable ID that is stable across chunking and retries."""
    field_name = str(unit.field_code or unit.path or "text").rsplit(".", 1)[-1]
    if unit.entity_type == "daily_report" or unit.field_code.startswith("report_fields."):
        parts = ("report", field_name)
    else:
        row_reference = str(unit.entity_id or "").rsplit(":", 1)[-1]
        if not row_reference:
            match = re.search(r"\[(\d+)]", str(unit.path or ""))
            row_reference = str(int(match.group(1)) + 1) if match else "item"
        parts = (str(unit.entity_type or "item"), row_reference, field_name)
    return ":".join(_translation_id_component(value) for value in parts)


def _translation_id_component(value: object) -> str:
    component = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value or "").strip()).strip("-.")
    return component or "item"


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


def _is_deterministic_protected_fragment(item_id: str, value: str) -> bool:
    """Recognize generated placeholder fragments that contain no prose to translate.

    Dense protected fields are split into internal ``protected-part`` items. A
    part containing several already-protected values plus one uppercase label is
    effectively layout, not an independently translatable sentence. Treating an
    unchanged model response as a failure makes the whole report fail even when
    every translatable clause is correct.

    Keep this rule deliberately narrow: it applies only to generated internal
    parts, requires at least three placeholders, and allows exactly one short
    uppercase token. Ordinary source fields and multi-word uppercase prose still
    go through translation and quality validation.
    """
    if "::protected-part-" not in str(item_id or ""):
        return False
    text = str(value or "")
    if len(_PROTECTED_PLACEHOLDER_PATTERN.findall(text)) < 3:
        return False
    natural = normalize_inline(_PROTECTED_PLACEHOLDER_PATTERN.sub(" ", text))
    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", natural)
    if len(words) != 1:
        return False
    word = words[0]
    return 2 <= len(word) <= 24 and word.upper() == word and not _SPANISH_PROSE_PATTERN.search(word)


def _repair_protected_token_layout(source_text: str, translated_text: str) -> str:
    """Restore source boundaries between placeholders before value expansion."""
    source = str(source_text or "")
    repaired = str(translated_text or "")
    matches = list(_PROTECTED_PLACEHOLDER_PATTERN.finditer(source))
    for previous, current in zip(matches, matches[1:]):
        separator = source[previous.end():current.start()]
        # Numeric ranges and ratios are often formatted across PDF line breaks,
        # for example ``300\n/ 7500``. Models commonly collapse that to
        # ``[[P0]]/[[P1]]``, which changes two values into one apparent
        # fraction. Restore any punctuation-only boundary exactly; never touch
        # a boundary containing prose because the model may legitimately move
        # words while translating it.
        if separator and not re.search(r"\w", separator, flags=re.UNICODE):
            repaired = re.sub(
                rf"{re.escape(previous.group(0))}[^\w\[]*{re.escape(current.group(0))}",
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
    return sorted(
        matchers,
        key=lambda item: (
            item[0].priority,
            item[0].glossary_type == "phrase",
            len(item[1]),
        ),
        reverse=True,
    )


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
_OCR_ACTION_NUMBER_PATTERN = re.compile(
    r"(?:INGRESA|INGRESAN|FILTRA|PERFORA|BOMBEA|CIRCULA|DESPLAZA|RECUPERA|BAJA|SACA)\d{4,}",
    re.IGNORECASE,
)
_PROTECTED_NUMBER_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])[-+]?(?:"
    r"\d+-\d+/\d+"
    r"|\d+(?:(?:[,.]\d+)+(?:/\d+)?(?=$|[^0-9_])|(?:/\d+)?(?![A-Za-z0-9_]))"
    r")"
)
_VALIDATION_NUMBER_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?:\d+-\d+/\d+|\d+(?:[,.]\d+)*(?:/\d+)?)"
)
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
_MONTH_NAME_ALTERNATION = "|".join(
    sorted((re.escape(name) for name in _MONTH_NUMBER_BY_NAME), key=len, reverse=True)
)
_MONTH_NAME_PATTERN = re.compile(
    r"\b(" + _MONTH_NAME_ALTERNATION + r")\b",
    re.IGNORECASE,
)
_DAY_MONTH_DATE_PATTERN = re.compile(
    r"\b(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?:DE\s+)?"
    r"(?P<month>" + _MONTH_NAME_ALTERNATION + r")"
    r"(?:\s+(?:DE(?:L)?\s+)?(?P<year>\d{4}))?\b",
    re.IGNORECASE,
)
_MONTH_DAY_DATE_PATTERN = re.compile(
    r"\b(?P<month>" + _MONTH_NAME_ALTERNATION + r")\s+"
    r"(?P<day>\d{1,2})(?:st|nd|rd|th)?(?:,\s*|\s+)(?P<year>\d{4})\b",
    re.IGNORECASE,
)
_NUMERIC_DAY_MONTH_DATE_PATTERN = re.compile(
    r"(?<!\d)(?P<day>\d{1,2})[/-](?P<month>\d{1,2})[/-](?P<year>\d{4})(?!\d)"
)
_NUMERIC_YEAR_MONTH_DATE_PATTERN = re.compile(
    r"(?<!\d)(?P<year>\d{4})[/-](?P<month>\d{1,2})[/-](?P<day>\d{1,2})(?!\d)"
)


@dataclass(frozen=True)
class _CalendarDate:
    start: int
    end: int
    year: str
    month: str
    day: str
    source: str
_ACTION_CONCEPTS = (
    ("drill", re.compile(r"\b(?:perfor(?:a|ó|ando|ar)|drill(?:ed|ing)?)\b", re.IGNORECASE), re.compile(r"钻进|钻至|开钻")),
    ("pump", re.compile(r"\b(?:bombe(?:a|ó|ando|ar)|pump(?:ed|ing)?)\b", re.IGNORECASE), re.compile(r"泵入|泵送|注入")),
    ("circulate", re.compile(r"\b(?:circul(?:a|ó|ando|ar)|circulat(?:e|ed|ing))\b", re.IGNORECASE), re.compile(r"循环")),
    ("trip_out", re.compile(r"\b(?:saca|sacando|sacar|trip(?:ping)?\s+out|pull(?:ed|ing)?)\b", re.IGNORECASE), re.compile(r"起出|起钻|上提")),
    ("trip_in", re.compile(r"\b(?:baja|bajando|bajar|trip(?:ping)?\s+in|run(?:ning)?\s+in)\b", re.IGNORECASE), re.compile(r"下入|下钻|下放")),
    ("change", re.compile(r"\b(?:cambia|cambió|cambio|cambiar|chang(?:e|ed|ing))\b", re.IGNORECASE), re.compile(r"更换|换用|替换")),
    ("test", re.compile(r"\b(?:prueba|probar|test(?:ed|ing)?)\b", re.IGNORECASE), re.compile(r"试验|测试|检验")),
)


def _number_tokens(value: object) -> list[str]:
    return [match.source for match in _validation_number_matches(value)]


def _derived_number_tokens(value: object, target_language: str) -> list[str]:
    if normalize_language(target_language) != "zh-CN":
        return []
    return [_MONTH_NUMBER_BY_NAME[match.group(1).casefold()] for match in _MONTH_NAME_PATTERN.finditer(str(value or ""))]


def _normalize_calendar_date_format(value: object) -> str:
    normalized = str(value or "iso").strip().lower()
    return normalized if normalized in {"iso", "chinese"} else "iso"


def _calendar_date_format_instruction(date_format: str, *, authoritative: bool) -> str:
    selected = _normalize_calendar_date_format(date_format)
    prefix = "以下日期格式规则优先于其它提示中的日期示例：" if authoritative else "日期格式"
    if selected == "chinese":
        return f"{prefix}完整日期统一使用 YYYY年M月D日（如 2026年1月22日），缺少年份时使用 M月D日。"
    return f"{prefix}完整日期统一使用 ISO YYYY-MM-DD（如 2026-01-22），缺少年份时使用 M月D日。"


def _calendar_date_matches(value: object) -> list[_CalendarDate]:
    """Return every non-overlapping source calendar date in source order."""
    text = str(value or "")
    candidates: list[_CalendarDate] = []
    for pattern in (_DAY_MONTH_DATE_PATTERN, _MONTH_DAY_DATE_PATTERN):
        for match in pattern.finditer(text):
            month = _MONTH_NUMBER_BY_NAME.get(match.group("month").casefold(), "")
            day = str(int(match.group("day")))
            year = str(match.groupdict().get("year") or "")
            if month:
                candidates.append(_CalendarDate(
                    start=match.start(),
                    end=match.end(),
                    year=year,
                    month=month,
                    day=day,
                    source=match.group(0),
                ))
    for pattern in (_NUMERIC_DAY_MONTH_DATE_PATTERN, _NUMERIC_YEAR_MONTH_DATE_PATTERN):
        for match in pattern.finditer(text):
            year = str(int(match.group("year")))
            month = str(int(match.group("month")))
            day = str(int(match.group("day")))
            if not (1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                continue
            candidates.append(_CalendarDate(
                start=match.start(),
                end=match.end(),
                year=year,
                month=month,
                day=day,
                source=match.group(0),
            ))
    selected: list[_CalendarDate] = []
    for candidate in sorted(candidates, key=lambda item: (item.start, -(item.end - item.start))):
        if any(candidate.start < existing.end and candidate.end > existing.start for existing in selected):
            continue
        selected.append(candidate)
    return selected


def _calendar_date_components(value: object) -> list[tuple[str, str, str]]:
    """Return source calendar dates as ``(year, month, day)`` tuples."""
    return [(item.year, item.month, item.day) for item in _calendar_date_matches(value)]


def _calendar_date_spans(value: object) -> list[tuple[int, int]]:
    return [(item.start, item.end) for item in _calendar_date_matches(value)]


def _localized_calendar_date_value(
    year: str,
    month: str,
    day: str,
    target_language: str,
    date_format: str,
) -> str:
    if normalize_language(target_language) != "zh-CN":
        return "-".join(part for part in (year, month, day) if part)
    if not year:
        return f"{int(month)}月{int(day)}日"
    if _normalize_calendar_date_format(date_format) == "chinese":
        return f"{int(year)}年{int(month)}月{int(day)}日"
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"


def _localized_calendar_date_pattern(date: _CalendarDate, date_format: str) -> re.Pattern[str]:
    month = str(int(date.month))
    day = str(int(date.day))
    if not date.year:
        return re.compile(rf"(?<!\d)0*{re.escape(month)}\s*月\s*0*{re.escape(day)}\s*(?:日|号)")
    if _normalize_calendar_date_format(date_format) == "chinese":
        return re.compile(
            rf"(?<!\d){re.escape(str(int(date.year)))}\s*年\s*"
            rf"0*{re.escape(month)}\s*月\s*0*{re.escape(day)}\s*(?:日|号)"
        )
    expected = _localized_calendar_date_value(date.year, date.month, date.day, "zh-CN", "iso")
    return re.compile(rf"(?<!\d){re.escape(expected)}(?!\d)")


def _yearful_pattern_for_yearless_date(date: _CalendarDate) -> re.Pattern[str]:
    month = str(int(date.month))
    day = str(int(date.day))
    return re.compile(
        rf"(?<!\d)(?:\d{{4}}-0*{re.escape(month)}-0*{re.escape(day)}|"
        rf"\d{{4}}\s*年\s*0*{re.escape(month)}\s*月\s*0*{re.escape(day)}\s*(?:日|号))(?!\d)"
    )


def _calendar_date_output_match(
    date: _CalendarDate,
    translated: str,
    date_format: str,
) -> re.Match[str] | None:
    match = _localized_calendar_date_pattern(date, date_format).search(translated)
    if match or date.year:
        return match
    # A model may infer the report year for a source date that only says
    # "14 de mayo". Treat that as the same calendar day during validation;
    # persistence removes the inferred year below so no new fact is retained.
    return _yearful_pattern_for_yearless_date(date).search(translated)


def _normalize_yearless_calendar_dates(
    source_text: object,
    translated_text: object,
    target_language: str,
) -> str:
    if normalize_language(target_language) != "zh-CN":
        return str(translated_text or "")
    translated = str(translated_text or "")
    for date in _calendar_date_matches(source_text):
        if date.year or _localized_calendar_date_pattern(date, "iso").search(translated):
            continue
        match = _yearful_pattern_for_yearless_date(date).search(translated)
        if not match:
            continue
        replacement = _localized_calendar_date_value("", date.month, date.day, target_language, "iso")
        translated = translated[:match.start()] + replacement + translated[match.end():]
    return translated


def _mask_spans(value: str, spans: list[tuple[int, int]]) -> str:
    if not spans:
        return value
    pieces: list[str] = []
    cursor = 0
    for start, end in spans:
        pieces.extend((value[cursor:start], " "))
        cursor = end
    pieces.append(value[cursor:])
    return "".join(pieces)


def _texts_without_calendar_dates(
    source_text: object,
    translated_text: object,
    target_language: str,
    date_format: str,
) -> tuple[str, str]:
    source = str(source_text or "")
    translated = str(translated_text or "")
    if normalize_language(target_language) != "zh-CN":
        return source, translated
    dates = _calendar_date_matches(source)
    if not dates:
        return source, translated
    source = _mask_spans(source, [(item.start, item.end) for item in dates])
    for date in dates:
        match = _calendar_date_output_match(date, translated, date_format)
        if match:
            translated = translated[:match.start()] + " " + translated[match.end():]
    return source, translated


def _calendar_date_quality_error(
    source_text: object,
    translated_text: object,
    target_language: str,
    date_format: str = "iso",
) -> str:
    """Require every source date to use the configured target representation."""
    if normalize_language(target_language) != "zh-CN":
        return ""
    dates = _calendar_date_matches(source_text)
    if not dates:
        return ""
    translated = str(translated_text or "")
    missing: list[str] = []
    for date in dates:
        match = _calendar_date_output_match(date, translated, date_format)
        if match:
            translated = translated[:match.start()] + " " + translated[match.end():]
            continue
        missing.append(_localized_calendar_date_value(
            date.year,
            date.month,
            date.day,
            target_language,
            date_format,
        ))
    if missing:
        selected = _normalize_calendar_date_format(date_format)
        label = "ISO YYYY-MM-DD" if selected == "iso" else "Chinese YYYY年M月D日"
        return f"calendar dates were not localized to configured {label} format; missing={missing}"
    return ""


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
    tuning_material = {
        "version": tuning.version,
        "system_prompt": tuning.system_prompt,
        "translation_instruction": tuning.translation_instruction,
        "prompt_templates": tuning.prompt_templates,
        "contextual_translation": tuning.contextual_translation,
        "validate_results": tuning.validate_results,
        "numbers": tuning.protect_numbers,
        "units": tuning.protect_units,
        "acronyms": tuning.protect_acronyms,
        "proper_nouns": tuning.protect_proper_nouns,
        "ambiguous_units": tuning.ambiguous_units,
        "unit_aliases": tuning.unit_aliases,
        "unit_context_exclusions": tuning.unit_context_exclusions,
    }
    if tuning.experience_rules:
        tuning_material["experience_rules"] = tuning.experience_rules
    material = {
        "pipeline": TRANSLATION_PIPELINE_VERSION,
        "target": normalize_language(target_language),
        "model": model_identity,
        "tuning": tuning_material,
        "protected": {
            "units": terms.units,
            "acronyms": terms.acronyms,
            "proper_nouns": terms.proper_nouns,
        },
        "terms": [
            (
                entry.id,
                entry.zh,
                entry.en,
                entry.es,
                entry.aliases,
                entry.enabled,
                entry.protected,
                entry.term_type,
                entry.strict_preserve,
                entry.priority,
            )
            for entry in terms.entries
            if entry.enabled
        ],
    }
    digest = hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return f"{TRANSLATION_PIPELINE_VERSION}-{digest}"[:64]


def _compiled_literal_matchers(
    values: tuple[str, ...],
    *,
    unit: bool = False,
    case_sensitive: bool = False,
) -> list[tuple[str, re.Pattern[str]]]:
    matchers: list[tuple[str, re.Pattern[str]]] = []
    for value in values:
        clean_value = str(value or "").strip()
        if not clean_value:
            continue
        escaped = re.escape(clean_value).replace(r"\ ", r"\s+")
        # Keep the regex boundary ASCII-only, then let ``_unit_match_allowed``
        # perform a Unicode-letter check. A broad U+00C0-U+024F range also
        # contains symbols such as the multiplication sign (×), which is a
        # valid separator after units such as ``ppg×120``.
        # Units may be attached directly to a value (``5/8IN``, ``60BBL``),
        # so a leading digit is a valid boundary. Letters and underscores still
        # block matches inside ordinary words and identifiers.
        unit_prefix_word = r"A-Za-z_"
        unit_suffix_word = r"A-Za-z0-9_"
        boundary = rf"(?<![{unit_prefix_word}]){escaped}(?![{unit_suffix_word}])" if unit else _term_regex(clean_value)
        flags = 0 if case_sensitive else re.IGNORECASE
        matchers.append((clean_value, re.compile(boundary, flags)))
    return sorted(matchers, key=lambda item: len(item[0]), reverse=True)


def _compiled_unit_context_exclusions(
    values: tuple[tuple[str, str], ...],
) -> dict[str, tuple[re.Pattern[str], ...]]:
    compiled: dict[str, list[re.Pattern[str]]] = {}
    for configured_unit, pattern in values:
        try:
            matcher = re.compile(pattern)
        except re.error:
            continue
        compiled.setdefault(configured_unit.casefold(), []).append(matcher)
    return {unit: tuple(matchers) for unit, matchers in compiled.items()}


def _unit_match_allowed(
    text: str,
    match: re.Match[str],
    configured_unit: str,
    *,
    ambiguous_units: frozenset[str] = frozenset(),
    exclusions: dict[str, tuple[re.Pattern[str], ...]] | None = None,
) -> bool:
    def is_latin_word_character(value: str) -> bool:
        if not value:
            return False
        if value.isascii():
            return value.isalnum() or value == "_"
        return unicodedata.category(value).startswith(("L", "N")) and "LATIN" in unicodedata.name(value, "")

    if (
        match.start() > 0
        and is_latin_word_character(text[match.start() - 1])
        and not text[match.start() - 1].isdigit()
    ):
        return False
    if match.end() < len(text) and is_latin_word_character(text[match.end()]):
        return False
    configured_key = configured_unit.casefold()
    for exclusion in (exclusions or {}).get(configured_key, ()):
        if any(candidate.start() <= match.start() and candidate.end() >= match.end() for candidate in exclusion.finditer(text)):
            return False
    before = text[max(0, match.start() - 20):match.start()]
    after = text[match.end():min(len(text), match.end() + 20)]
    if configured_key not in ambiguous_units:
        return True
    return bool(
        re.search(r"\d[\d\s.,/'\"-]*$", before)
        or re.match(r"^\s*[/×x*-]\s*(?:\d|[A-Za-z])", after)
        or re.search(r"[/×x*-]\s*$", before)
    )


def _protected_unit_tokens(
    text: object,
    matchers: list[tuple[str, re.Pattern[str]]],
    *,
    ambiguous_units: frozenset[str] = frozenset(),
    exclusions: dict[str, tuple[re.Pattern[str], ...]] | None = None,
) -> list[str]:
    value = str(text or "")
    candidates: list[tuple[int, int, str]] = []
    for configured_unit, matcher in matchers:
        for match in matcher.finditer(value):
            if _unit_match_allowed(
                value,
                match,
                configured_unit,
                ambiguous_units=ambiguous_units,
                exclusions=exclusions,
            ):
                candidates.append((match.start(), match.end(), match.group(0)))
    selected: list[tuple[int, int, str]] = []
    for candidate in sorted(candidates, key=lambda item: (item[0], -(item[1] - item[0]))):
        start, end, _token = candidate
        if any(start < existing_end and end > existing_start for existing_start, existing_end, _existing in selected):
            continue
        selected.append(candidate)
    return [token for _start, _end, token in sorted(selected, key=lambda item: item[0])]


def _protected_unit_keys(
    text: object,
    matchers: list[tuple[str, re.Pattern[str]]],
    *,
    ambiguous_units: frozenset[str] = frozenset(),
    exclusions: dict[str, tuple[re.Pattern[str], ...]] | None = None,
) -> list[str]:
    value = str(text or "")
    candidates: list[tuple[int, int, str]] = []
    for configured_unit, matcher in matchers:
        for match in matcher.finditer(value):
            if _unit_match_allowed(
                value,
                match,
                configured_unit,
                ambiguous_units=ambiguous_units,
                exclusions=exclusions,
            ):
                candidates.append((match.start(), match.end(), configured_unit.casefold()))
    selected: list[tuple[int, int, str]] = []
    for candidate in sorted(candidates, key=lambda item: (item[0], -(item[1] - item[0]))):
        start, end, _key = candidate
        if any(start < existing_end and end > existing_start for existing_start, existing_end, _existing in selected):
            continue
        selected.append(candidate)
    return [key for _start, _end, key in sorted(selected, key=lambda item: item[0])]


def _semantic_unit_quality_error(
    source_text: object,
    translated_text: object,
    matchers: list[tuple[str, re.Pattern[str]]],
    *,
    ambiguous_units: frozenset[str] = frozenset(),
    exclusions: dict[str, tuple[re.Pattern[str], ...]] | None = None,
) -> str:
    source_counts = Counter(_protected_unit_keys(
        source_text,
        matchers,
        ambiguous_units=ambiguous_units,
        exclusions=exclusions,
    ))
    if not source_counts:
        return ""
    translated_value = str(translated_text or "")
    translated_counts = Counter(_protected_unit_keys(
        translated_value,
        matchers,
        ambiguous_units=ambiguous_units,
        exclusions=exclusions,
    ))
    missing: list[str] = []
    for unit, expected in source_counts.items():
        actual = translated_counts.get(unit, 0)
        if actual < expected:
            missing.extend([unit] * (expected - actual))
    return f"model removed or changed units; missing={missing[:8]}" if missing else ""


def _action_completeness_warning(source_text: object, translated_text: object) -> str:
    source = str(source_text or "")
    translated = str(translated_text or "")
    missing = [name for name, source_pattern, target_pattern in _ACTION_CONCEPTS if source_pattern.search(source) and not target_pattern.search(translated)]
    return f"translation may omit operation actions: {missing}" if missing else ""


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


_PDF_ARTIFACT_LINE_PATTERN = re.compile(
    r"^(?:page\s+\d+\s+of\s+\d+|daily\s+operations\s+report|ep\s+petroecuador)$",
    re.IGNORECASE,
)


def clean_translation_source(value: Any) -> tuple[str, list[str]]:
    """Remove only high-confidence PDF artifacts while retaining the stored raw source."""
    text = normalize_multiline(str(value or "").replace("\u00ad", ""))
    actions: list[str] = []
    normalized_ocr = normalize_pdf_ocr_text(text)
    if normalized_ocr != text:
        actions.append("normalize_pdf_ocr")
        text = normalized_ocr
    without_split_words = re.sub(
        r"(?<=[A-Za-zÁÉÍÓÚÜÑáéíóúüñ])-\n(?=[A-Za-zÁÉÍÓÚÜÑáéíóúüñ])",
        "",
        text,
    )
    if without_split_words != text:
        actions.append("join_hyphenated_line_break")
    kept_lines: list[str] = []
    removed_headers = 0
    for line in without_split_words.splitlines():
        if _PDF_ARTIFACT_LINE_PATTERN.fullmatch(normalize_inline(line)):
            removed_headers += 1
            continue
        kept_lines.append(line)
    if removed_headers:
        actions.append(f"remove_pdf_header_footer:{removed_headers}")
    return normalize_multiline("\n".join(kept_lines)), actions


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
    term_type = str(item.get("term_type", "preferred") or "preferred").strip().lower()
    if term_type not in TERM_TYPES:
        term_type = "preferred"
    strict_preserve = bool(item.get("strict_preserve", term_type == "protected"))
    try:
        priority = max(0, min(1000, int(item.get("priority", 50) or 50)))
    except (TypeError, ValueError):
        priority = 50
    id_values = [value for value in values.values() if value]
    return TermEntry(
        id=str(item.get("id", "") or _stable_term_id(id_values[0], id_values[1] if len(id_values) > 1 else "")),
        category=str(item.get("category", "drilling") or "drilling"),
        zh=values["zh"],
        en=values["en"],
        es=values["es"],
        aliases=aliases,
        protected=bool(item.get("protected", True)),
        term_type=term_type,
        strict_preserve=strict_preserve,
        priority=priority,
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
