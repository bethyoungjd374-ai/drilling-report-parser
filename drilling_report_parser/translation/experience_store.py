"""Persistence and lifecycle operations for translation experience suggestions."""

from __future__ import annotations

import json
import re
import threading
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from ..runtime_files import atomic_write_json, ensure_parent


VALID_STATUSES = {"PENDING", "APPLIED", "VERIFIED", "DISMISSED"}


def normalize_experience_pool(raw: object) -> dict[str, object]:
    source = raw if isinstance(raw, dict) else {}
    suggestions: list[dict[str, object]] = []
    raw_suggestions = source.get("suggestions") if isinstance(source.get("suggestions"), list) else []
    for raw_item in raw_suggestions:
        if not isinstance(raw_item, dict):
            continue
        fingerprint = str(raw_item.get("fingerprint", "") or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
            continue
        status = str(raw_item.get("status", "PENDING") or "PENDING").strip().upper()
        if status not in VALID_STATUSES:
            status = "PENDING"
        proposed_change = raw_item.get("proposed_change") if isinstance(raw_item.get("proposed_change"), dict) else {}
        raw_evidence = raw_item.get("evidence") if isinstance(raw_item.get("evidence"), list) else []
        evidence = [
            {
                "record_id": str(item.get("record_id", "") or "")[:191],
                "field_code": str(item.get("field_code", "") or "")[:128],
                "source_text": str(item.get("source_text", "") or "")[:800],
                "error_message": str(item.get("error_message", "") or "")[:800],
            }
            for item in raw_evidence[:8]
            if isinstance(item, dict)
        ]
        suggestions.append({
            "id": str(raw_item.get("id", "") or f"exp-{fingerprint[:16]}")[:64],
            "fingerprint": fingerprint,
            "status": status,
            "category": str(raw_item.get("category", "") or "")[:64],
            "action_type": str(raw_item.get("action_type", "") or "")[:64],
            "token": str(raw_item.get("token", "") or "")[:128],
            "title": str(raw_item.get("title", "") or "")[:300],
            "cause": str(raw_item.get("cause", "") or "")[:1000],
            "recommendation": str(raw_item.get("recommendation", "") or "")[:1000],
            "report_type": str(raw_item.get("report_type", "") or "")[:32].lower(),
            "field_code": str(raw_item.get("field_code", "") or "")[:128],
            "confidence": str(raw_item.get("confidence", "medium") or "medium")[:16].lower(),
            "proposed_change": {str(key)[:64]: str(value or "")[:1000] for key, value in proposed_change.items()},
            "record_ids": _normalized_string_list(raw_item.get("record_ids"))[:100],
            "field_codes": _normalized_string_list(raw_item.get("field_codes"))[:100],
            "occurrence_count": max(1, int(raw_item.get("occurrence_count", 1) or 1)),
            "regression_count": max(0, int(raw_item.get("regression_count", 0) or 0)),
            "evidence": evidence,
            "first_seen_at": str(raw_item.get("first_seen_at", "") or "")[:64],
            "last_seen_at": str(raw_item.get("last_seen_at", "") or "")[:64],
            "applied_at": str(raw_item.get("applied_at", "") or "")[:64],
            "applied_by": str(raw_item.get("applied_by", "") or "")[:128],
            "verified_at": str(raw_item.get("verified_at", "") or "")[:64],
            "verified_record_id": str(raw_item.get("verified_record_id", "") or "")[:191],
            "dismissed_at": str(raw_item.get("dismissed_at", "") or "")[:64],
            "dismissed_by": str(raw_item.get("dismissed_by", "") or "")[:128],
        })
    return {"version": 1, "suggestions": suggestions}


def load_experience_pool(
    path: Path,
    *,
    lock: threading.Lock | threading.RLock | None = None,
) -> dict[str, object]:
    context = lock if lock is not None else nullcontext()
    with context:
        return _load_unlocked(path)


def save_experience_pool(
    path: Path,
    pool: dict[str, object],
    *,
    lock: threading.Lock | threading.RLock | None = None,
) -> None:
    context = lock if lock is not None else nullcontext()
    with context:
        _save_unlocked(path, pool)


def record_experience_suggestions(
    path: Path,
    diagnosed: list[dict[str, object]],
    *,
    lock: threading.Lock | threading.RLock | None = None,
    now: str = "",
) -> list[dict[str, object]]:
    if not diagnosed:
        return []
    timestamp = now or datetime.now().isoformat(timespec="seconds")
    context = lock if lock is not None else nullcontext()
    with context:
        pool = _load_unlocked(path)
        suggestions = pool.get("suggestions") if isinstance(pool.get("suggestions"), list) else []
        by_fingerprint = {
            str(item.get("fingerprint", "") or ""): item
            for item in suggestions
            if isinstance(item, dict)
        }
        updated: list[dict[str, object]] = []
        for candidate in diagnosed:
            fingerprint = str(candidate.get("fingerprint", "") or "")
            current = by_fingerprint.get(fingerprint)
            if current is None:
                current = {
                    **candidate,
                    "id": f"exp-{fingerprint[:16]}",
                    "status": "PENDING",
                    "regression_count": 0,
                    "first_seen_at": timestamp,
                    "last_seen_at": timestamp,
                    "applied_at": "",
                    "applied_by": "",
                    "verified_at": "",
                    "verified_record_id": "",
                    "dismissed_at": "",
                    "dismissed_by": "",
                }
                suggestions.append(current)
                by_fingerprint[fingerprint] = current
            else:
                previous_status = str(current.get("status", "PENDING") or "PENDING")
                if previous_status in {"APPLIED", "VERIFIED"}:
                    current["regression_count"] = int(current.get("regression_count", 0) or 0) + 1
                current["status"] = "PENDING"
                current["last_seen_at"] = timestamp
                current["occurrence_count"] = (
                    int(current.get("occurrence_count", 0) or 0)
                    + int(candidate.get("occurrence_count", 1) or 1)
                )
                current["record_ids"] = _normalized_string_list([
                    *current.get("record_ids", []),
                    *candidate.get("record_ids", []),
                ])[:100]
                current["field_codes"] = _normalized_string_list([
                    *current.get("field_codes", []),
                    *candidate.get("field_codes", []),
                ])[:100]
                current["evidence"] = [
                    *current.get("evidence", []),
                    *candidate.get("evidence", []),
                ][-8:]
            updated.append(current)
        pool["suggestions"] = suggestions
        _save_unlocked(path, pool)
        return updated


def update_experience_status(
    path: Path,
    suggestion_id: str,
    *,
    status: str,
    actor: str = "",
    verified_record_id: str = "",
    lock: threading.Lock | threading.RLock | None = None,
    now: str = "",
) -> dict[str, object] | None:
    timestamp = now or datetime.now().isoformat(timespec="seconds")
    context = lock if lock is not None else nullcontext()
    with context:
        pool = _load_unlocked(path)
        suggestions = pool.get("suggestions") if isinstance(pool.get("suggestions"), list) else []
        suggestion = next(
            (item for item in suggestions if str(item.get("id", "") or "") == suggestion_id),
            None,
        )
        if not isinstance(suggestion, dict):
            return None
        normalized_status = status.strip().upper()
        if normalized_status not in VALID_STATUSES:
            raise ValueError(f"Unsupported experience status: {status}")
        suggestion["status"] = normalized_status
        if normalized_status == "APPLIED":
            suggestion["applied_at"] = timestamp
            suggestion["applied_by"] = actor
        elif normalized_status == "VERIFIED":
            suggestion["verified_at"] = timestamp
            suggestion["verified_record_id"] = verified_record_id
        elif normalized_status == "DISMISSED":
            suggestion["dismissed_at"] = timestamp
            suggestion["dismissed_by"] = actor
        pool["suggestions"] = suggestions
        _save_unlocked(path, pool)
        return suggestion


def mark_experience_verified(
    path: Path,
    record_id: str,
    status_by_id: dict[str, str],
    *,
    lock: threading.Lock | threading.RLock | None = None,
    now: str = "",
) -> int:
    timestamp = now or datetime.now().isoformat(timespec="seconds")
    context = lock if lock is not None else nullcontext()
    with context:
        pool = _load_unlocked(path)
        suggestions = pool.get("suggestions") if isinstance(pool.get("suggestions"), list) else []
        verified = 0
        for suggestion in suggestions:
            if not isinstance(suggestion, dict) or str(suggestion.get("status", "") or "") != "APPLIED":
                continue
            if record_id not in suggestion.get("record_ids", []):
                continue
            affected_records = [str(item or "") for item in suggestion.get("record_ids", []) if str(item or "")]
            if any(status_by_id.get(item) != "COMPLETED" for item in affected_records):
                continue
            suggestion["status"] = "VERIFIED"
            suggestion["verified_at"] = timestamp
            suggestion["verified_record_id"] = record_id
            verified += 1
        if verified:
            pool["suggestions"] = suggestions
            _save_unlocked(path, pool)
        return verified


def _load_unlocked(path: Path) -> dict[str, object]:
    ensure_parent(path)
    if not path.exists():
        return {"version": 1, "suggestions": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    return normalize_experience_pool(data)


def _save_unlocked(path: Path, pool: dict[str, object]) -> None:
    atomic_write_json(path, normalize_experience_pool(pool))


def _normalized_string_list(value: object) -> list[str]:
    values = value if isinstance(value, (list, tuple, set)) else [value]
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        text = str(item or "").strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(text)
    return result
