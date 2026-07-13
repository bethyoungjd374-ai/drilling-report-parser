"""Small, reusable helpers for bounded runtime files.

The web server writes several local JSON/JSONL files for configuration, audit,
and diagnostic telemetry.  Keeping the file lifecycle here gives every caller
the same atomic-write and retention guarantees without coupling those concerns
to the HTTP handler.
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from collections.abc import Callable
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_json(
    path: Path,
    value: object,
    *,
    private: bool = False,
    lock: threading.Lock | threading.RLock | None = None,
) -> None:
    """Write JSON through a same-directory temporary file and atomic replace."""
    ensure_parent(path)
    data = json.dumps(value, ensure_ascii=False, indent=2)
    context = lock if lock is not None else nullcontext()
    with context:
        temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(data, encoding="utf-8")
            if private:
                temporary.chmod(0o600)
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


def rotate_jsonl_if_needed(path: Path, max_bytes: int) -> bool:
    """Rotate a JSONL file to ``.1`` once it reaches the configured size."""
    if max_bytes <= 0:
        return False
    try:
        if not path.exists() or path.stat().st_size < max_bytes:
            return False
        rotated = path.with_suffix(path.suffix + ".1")
        rotated.unlink(missing_ok=True)
        path.replace(rotated)
        return True
    except OSError:
        return False


def append_jsonl(
    path: Path,
    record: dict[str, Any],
    *,
    lock: threading.Lock | threading.RLock | None = None,
    max_bytes: int = 0,
    sort_keys: bool = True,
    default: Callable[[object], object] | None = None,
) -> None:
    """Append one JSON object, optionally rotating before the write."""
    ensure_parent(path)
    dump_options: dict[str, object] = {"ensure_ascii": False, "sort_keys": sort_keys}
    if default is not None:
        dump_options["default"] = default
    line = json.dumps(record, **dump_options)
    context = lock if lock is not None else nullcontext()
    with context:
        rotate_jsonl_if_needed(path, max_bytes)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def prune_jsonl(
    path: Path,
    *,
    retention_days: int,
    max_entries: int,
    max_bytes: int,
    now: datetime | None = None,
    timestamp_field: str = "time",
    remove_rotated: bool = True,
) -> dict[str, int]:
    """Keep recent valid JSONL rows within count and byte limits.

    Invalid rows and rows without a parseable timestamp are discarded.  The
    result reports the original row count, retained count, and retained bytes.
    Callers own synchronization so a batch prune can be combined with other
    state changes under the same lock.
    """
    if remove_rotated:
        path.with_suffix(path.suffix + ".1").unlink(missing_ok=True)
    if not path.exists():
        return {"before": 0, "after": 0, "bytes": 0}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {"before": 0, "after": 0, "bytes": 0}

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    cutoff = current.astimezone(timezone.utc) - timedelta(days=max(0, retention_days))

    recent: list[str] = []
    for line in lines:
        try:
            row = json.loads(line)
            timestamp = datetime.fromisoformat(str(row.get(timestamp_field, "") or "").replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
        except (AttributeError, TypeError, ValueError, json.JSONDecodeError):
            continue
        if timestamp.astimezone(timezone.utc) >= cutoff:
            recent.append(line)

    entry_limit = max(0, max_entries)
    byte_limit = max(0, max_bytes)
    candidates = recent[-entry_limit:] if entry_limit else []
    bounded: list[str] = []
    retained_bytes = 0
    for line in reversed(candidates):
        line_bytes = len(line.encode("utf-8")) + 1
        if not byte_limit or line_bytes > byte_limit:
            continue
        if bounded and retained_bytes + line_bytes > byte_limit:
            break
        bounded.append(line)
        retained_bytes += line_bytes
    bounded.reverse()

    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text("".join(f"{line}\n" for line in bounded), encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return {"before": len(lines), "after": len(bounded), "bytes": retained_bytes}
