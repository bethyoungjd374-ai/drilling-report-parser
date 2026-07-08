from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


@dataclass(frozen=True)
class MySQLSettings:
    enabled: bool
    host: str
    port: int
    database: str
    user: str
    password: str
    connect_timeout: int
    retry_seconds: int


def mysql_settings() -> MySQLSettings:
    values = _env_values()
    return MySQLSettings(
        enabled=_truthy(values.get("DRP_USE_MYSQL", values.get("MYSQL_ENABLED", "true"))),
        host=values.get("MYSQL_HOST", "127.0.0.1"),
        port=_int_value(values.get("MYSQL_PORT"), 3306),
        database=values.get("MYSQL_DATABASE", "drilling_report_db"),
        user=values.get("MYSQL_USER", "drilling_user"),
        password=values.get("MYSQL_PASSWORD", ""),
        connect_timeout=_int_value(values.get("MYSQL_CONNECT_TIMEOUT"), 2),
        retry_seconds=_int_value(values.get("MYSQL_RETRY_SECONDS"), 10),
    )


def _env_values() -> dict[str, str]:
    values = _read_env_file(ENV_PATH)
    values.update({key: value for key, value in os.environ.items() if key.startswith(("MYSQL_", "DRP_"))})
    return values


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def _truthy(value: object) -> bool:
    return str(value or "").strip().lower() not in {"0", "false", "no", "off", "disabled"}


def _int_value(value: object, default: int) -> int:
    try:
        return int(str(value or "").strip())
    except ValueError:
        return default
