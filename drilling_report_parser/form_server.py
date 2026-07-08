from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import mimetypes
import re
import secrets
import shutil
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from email.parser import BytesParser
from email.policy import default as email_policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from .completion_pdf_parser import parse_completion_pdf_daily_report
from .excel_database import (
    list_npt_confirmation_wells,
    load_npt_confirmation_detail,
    save_npt_confirmation,
)
from .storage import initialize_database, list_records, load_report_payload, mysql_status, save_report_payload
from .move_pdf_parser import parse_move_pdf_daily_report
from .pdf_report_parser import parse_pdf_daily_report
from .translation import TermsConfig, build_translator
from .workover_pdf_parser import parse_workover_pdf_daily_report


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web_form"
DATABASE_PATH = ROOT / "outputs" / "report_database.xlsx"
SOURCE_PDF_DIR = ROOT / "outputs" / "source_pdfs"
CONFIG_PATH = ROOT / "outputs" / "system_config.json"
USERS_PATH = ROOT / "outputs" / "users.json"
ROLES_PATH = ROOT / "outputs" / "roles.json"
PROJECT_TEAM_PATH = ROOT / "outputs" / "project_team_config.json"
TRANSLATION_TERMS_PATH = ROOT / "outputs" / "translation_terms.json"
DEFAULT_TRANSLATION_TERMS_PATH = ROOT / "drilling_report_parser" / "translation" / "drilling_terms.json"
PRODUCTION_REPORT_REMARKS_PATH = ROOT / "outputs" / "production_report_remarks.json"
AUDIT_LOG_PATH = ROOT / "outputs" / "audit_logs.jsonl"
BACKUP_DIR = ROOT / "outputs" / "backups"
SESSIONS: dict[str, dict[str, object]] = {}


@dataclass(frozen=True)
class UploadedFile:
    filename: str
    data: bytes


class FormHandler(BaseHTTPRequestHandler):
    server_version = "DrillingReportForm/0.1"

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", ""}:
            self._redirect_to("/login/")
            return
        if parsed.path == "/login":
            self._redirect_to("/login/")
            return
        if parsed.path == "/web_form":
            self._redirect_to("/web_form/")
            return
        if parsed.path == "/admin":
            self._redirect_to("/admin/")
            return
        if parsed.path == "/web_form/" and not self._current_user():
            self._redirect_login("/web_form/")
            return
        if parsed.path == "/admin/":
            user = self._current_user()
            if not user:
                self._redirect_login("/admin/")
                return
        self._serve_static(include_body=False)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", ""}:
            self._redirect_to("/login/")
            return
        if parsed.path == "/login":
            self._redirect_to("/login/")
            return
        if parsed.path == "/web_form":
            self._redirect_to("/web_form/")
            return
        if parsed.path == "/admin":
            self._redirect_to("/admin/")
            return
        if parsed.path == "/web_form/" and not self._current_user():
            self._redirect_login("/web_form/")
            return
        if parsed.path == "/admin/":
            user = self._current_user()
            if not user:
                self._redirect_login("/admin/")
                return
            if user.get("role") != "admin":
                self._serve_static_file(WEB_ROOT / "admin.html")
                return
        if parsed.path == "/api/records":
            if not self._require_permission("view"):
                return
            self._list_records(parsed.query)
            return
        if parsed.path == "/api/well-stats":
            if not self._require_permission("view"):
                return
            self._well_stats(parsed.query)
            return
        if parsed.path == "/api/production-summary":
            if not self._require_permission("view"):
                return
            self._production_summary(parsed.query)
            return
        if parsed.path == "/api/production-summary-export":
            if not self._require_permission("export"):
                return
            self._production_summary_export(parsed.query)
            return
        if parsed.path == "/api/npt-stats":
            if not self._require_permission("view"):
                return
            self._npt_stats(parsed.query)
            return
        if parsed.path == "/api/npt-stats-export":
            if not self._require_permission("export"):
                return
            self._npt_stats_export(parsed.query)
            return
        if parsed.path == "/api/npt-confirmations":
            user = self._require_permission("view")
            if not user:
                return
            self._npt_confirmations(parsed.query, user)
            return
        if parsed.path == "/api/npt-confirmation":
            user = self._require_permission("view")
            if not user:
                return
            self._npt_confirmation_detail(parsed.query, user)
            return
        if parsed.path == "/api/download-database":
            if not self._require_permission("export"):
                return
            self._download_database()
            return
        if parsed.path == "/api/source-pdf":
            if not self._require_permission("view"):
                return
            self._source_pdf(parsed.query)
            return
        if parsed.path == "/api/admin/session":
            self._admin_session()
            return
        if parsed.path == "/api/admin/users":
            self._admin_users()
            return
        if parsed.path == "/api/admin/config":
            self._admin_config()
            return
        if parsed.path == "/api/admin/roles":
            self._admin_roles()
            return
        if parsed.path == "/api/admin/project-teams":
            self._admin_project_teams()
            return
        if parsed.path == "/api/admin/translation-terms":
            self._admin_translation_terms()
            return
        if parsed.path == "/api/admin/data-status":
            self._admin_data_status()
            return
        if parsed.path == "/api/admin/audit-logs":
            self._admin_audit_logs()
            return
        self._serve_static()

    def do_POST(self) -> None:
        if self.path == "/api/admin/login":
            self._admin_login()
            return
        if self.path == "/api/admin/logout":
            self._admin_logout()
            return
        if self.path == "/api/admin/change-password":
            self._admin_change_password()
            return
        if self.path == "/api/admin/users":
            self._admin_save_user()
            return
        if self.path == "/api/admin/config":
            self._admin_save_config()
            return
        if self.path == "/api/admin/roles":
            self._admin_save_roles()
            return
        if self.path == "/api/admin/project-teams":
            self._admin_save_project_teams()
            return
        if self.path == "/api/admin/translation-terms":
            self._admin_save_translation_terms()
            return
        if self.path == "/api/admin/backup":
            self._admin_backup()
            return
        if self.path == "/api/import-pdf":
            if not self._require_permission("import"):
                return
            self._import_pdf()
            return
        if self.path == "/api/import-completion-pdf":
            if not self._require_permission("import"):
                return
            self._import_completion_pdf()
            return
        if self.path == "/api/import-workover-pdf":
            if not self._require_permission("import"):
                return
            self._import_workover_pdf()
            return
        if self.path == "/api/import-move-pdf":
            if not self._require_permission("import"):
                return
            self._import_move_pdf()
            return
        if self.path == "/api/save-report":
            if not self._require_permission("save"):
                return
            self._save_report()
            return
        if self.path == "/api/load-report":
            if not self._require_permission("view"):
                return
            self._load_report()
            return
        if self.path == "/api/production-report-remarks":
            user = self._require_permission("save")
            if not user:
                return
            self._save_production_report_remark(user)
            return
        if self.path == "/api/translate-report":
            if not self._require_permission("view"):
                return
            self._translate_report()
            return
        if self.path == "/api/npt-confirmation":
            user = self._require_permission("save")
            if not user:
                return
            self._save_npt_confirmation(user)
            return
        self.send_error(404)

    def _admin_session(self) -> None:
        user = self._current_user()
        self._send_json({"authenticated": bool(user), "user": _public_user(user) if user else None, "permissions": _role_permissions(user.get("role", "")) if user else {}})

    def _admin_login(self) -> None:
        payload = self._read_json_body()
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))
        users = _load_users()
        user = next((item for item in users if item.get("username") == username), None)
        if not user or user.get("status") != "active" or not _verify_password(password, str(user.get("password_hash", ""))):
            _write_audit(None, "login_failed", "system_admin", username, False, "invalid credentials")
            self._send_json({"error": "用户名或密码错误。"}, status=401)
            return
        token = secrets.token_urlsafe(32)
        user["last_login"] = datetime.now().isoformat(timespec="seconds")
        _save_users(users)
        SESSIONS[token] = {"username": username, "created_at": datetime.now().isoformat(timespec="seconds")}
        _write_audit(user, "login", "system_admin", username, True, "")
        self.send_response(200)
        body = json.dumps({"ok": True, "user": _public_user(user), "permissions": _role_permissions(str(user.get("role", "")))}, ensure_ascii=False).encode("utf-8")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Set-Cookie", f"drp_session={token}; Path=/; HttpOnly; SameSite=Lax")
        self.end_headers()
        self.wfile.write(body)

    def _admin_logout(self) -> None:
        token = self._session_token()
        user = self._current_user()
        if token:
            SESSIONS.pop(token, None)
        _write_audit(user, "logout", "system_admin", user.get("username", "") if user else "", True, "")
        self.send_response(200)
        body = json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Set-Cookie", "drp_session=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")
        self.end_headers()
        self.wfile.write(body)

    def _admin_change_password(self) -> None:
        user = self._current_user()
        if not user:
            self._send_json({"error": "请先登录。"}, status=401)
            return
        payload = self._read_json_body()
        old_password = str(payload.get("old_password", ""))
        new_password = str(payload.get("new_password", ""))
        if len(new_password) < 6:
            self._send_json({"error": "新密码至少 6 位。"}, status=400)
            return
        users = _load_users()
        target = next((item for item in users if item.get("username") == user.get("username")), None)
        if not target or not _verify_password(old_password, str(target.get("password_hash", ""))):
            self._send_json({"error": "原密码错误。"}, status=400)
            return
        target["password_hash"] = _hash_password(new_password)
        target["must_change_password"] = False
        _save_users(users)
        _write_audit(target, "change_password", "system_admin", str(target.get("username", "")), True, "")
        self._send_json({"ok": True, "user": _public_user(target)})

    def _admin_users(self) -> None:
        user = self._require_admin()
        if not user:
            return
        self._send_json({"users": [_public_user(item) for item in _load_users()], "roles": _role_definitions()})

    def _admin_save_user(self) -> None:
        user = self._require_admin()
        if not user:
            return
        payload = self._read_json_body()
        users = _load_users()
        username = str(payload.get("username", "")).strip()
        if not username:
            self._send_json({"error": "用户名不能为空。"}, status=400)
            return
        existing = next((item for item in users if item.get("username") == username), None)
        if existing is None:
            existing = {"id": str(uuid.uuid4()), "username": username, "created_at": datetime.now().isoformat(timespec="seconds")}
            users.append(existing)
        new_role = str(payload.get("role", "viewer")).strip() or "viewer"
        new_status = str(payload.get("status", "active")).strip() or "active"
        if new_role not in {str(role.get("value", "")) for role in _role_definitions()}:
            self._send_json({"error": "请选择有效角色。"}, status=400)
            return
        if existing.get("role") == "admin" and (new_role != "admin" or new_status != "active") and _active_admin_count(users) <= 1:
            self._send_json({"error": "不能停用或降级最后一个管理员。"}, status=400)
            return
        existing["display_name"] = str(payload.get("display_name", "") or username).strip()
        existing["email"] = str(payload.get("email", "")).strip()
        existing["role"] = new_role
        existing["status"] = new_status
        password = str(payload.get("password", ""))
        if password:
            existing["password_hash"] = _hash_password(password)
        elif not existing.get("password_hash"):
            existing["password_hash"] = _hash_password("123456")
        _save_users(users)
        _write_audit(user, "save_user", "system_admin", username, True, str(existing.get("role", "")))
        self._send_json({"ok": True, "users": [_public_user(item) for item in users]})

    def _admin_config(self) -> None:
        user = self._require_admin()
        if not user:
            return
        self._send_json({"config": _load_config()})

    def _admin_save_config(self) -> None:
        user = self._require_admin()
        if not user:
            return
        payload = self._read_json_body()
        current = _load_config()
        current.update({key: value for key, value in payload.items() if key in _default_config()})
        _save_config(current)
        _write_audit(user, "save_config", "system_admin", "system_config", True, "")
        self._send_json({"ok": True, "config": current})

    def _admin_roles(self) -> None:
        user = self._require_admin()
        if not user:
            return
        self._send_json({"roles": _role_definitions()})

    def _admin_save_roles(self) -> None:
        user = self._require_admin()
        if not user:
            return
        payload = self._read_json_body()
        roles = _normalize_roles(payload.get("roles", []))
        active_admins = [item for item in _load_users() if item.get("role") == "admin" and item.get("status") == "active"]
        if not active_admins:
            self._send_json({"error": "至少需要保留一个启用的管理员账号。"}, status=400)
            return
        _save_roles(roles)
        _write_audit(user, "save_roles", "system_admin", "roles", True, f"{len(roles)} roles")
        self._send_json({"ok": True, "roles": roles})

    def _admin_project_teams(self) -> None:
        user = self._require_admin()
        if not user:
            return
        self._send_json(_sync_project_wells_from_database(DATABASE_PATH))

    def _admin_save_project_teams(self) -> None:
        user = self._require_admin()
        if not user:
            return
        payload = self._read_json_body()
        config = _normalize_project_team_config(payload)
        _save_project_team_config(config)
        config = _sync_project_wells_from_database(DATABASE_PATH)
        _write_audit(user, "save_project_teams", "system_admin", "project_team_config", True, f"{len(config['projects'])} projects / {len(config['teams'])} teams")
        self._send_json({"ok": True, **config})

    def _admin_translation_terms(self) -> None:
        user = self._require_admin()
        if not user:
            return
        self._send_json(_load_translation_terms_config())

    def _admin_save_translation_terms(self) -> None:
        user = self._require_admin()
        if not user:
            return
        payload = self._read_json_body()
        config = _normalize_translation_terms_config(payload)
        _save_translation_terms_config(config)
        _write_audit(user, "save_translation_terms", "business_config", "translation_terms", True, f"{len(config['terms'])} terms")
        self._send_json({"ok": True, **config})

    def _admin_data_status(self) -> None:
        user = self._require_admin()
        if not user:
            return
        records = list_records(DATABASE_PATH)
        by_type: dict[str, int] = {}
        for record in records:
            report_type = str(record.get("report_type", "") or "unknown")
            by_type[report_type] = by_type.get(report_type, 0) + 1
        source_pdf_count = len(list(SOURCE_PDF_DIR.glob("*.pdf"))) if SOURCE_PDF_DIR.exists() else 0
        backups = sorted(BACKUP_DIR.glob("*.xlsx"), key=lambda item: item.stat().st_mtime, reverse=True)[:10] if BACKUP_DIR.exists() else []
        self._send_json({
            "records": len(records),
            "by_type": by_type,
            "database_path": str(DATABASE_PATH),
            "database_size": DATABASE_PATH.stat().st_size if DATABASE_PATH.exists() else 0,
            "database_updated_at": datetime.fromtimestamp(DATABASE_PATH.stat().st_mtime).isoformat(timespec="seconds") if DATABASE_PATH.exists() else "",
            "mysql": mysql_status(),
            "source_pdf_count": source_pdf_count,
            "backups": [{"name": item.name, "size": item.stat().st_size, "created_at": datetime.fromtimestamp(item.stat().st_mtime).isoformat(timespec="seconds")} for item in backups],
        })

    def _admin_backup(self) -> None:
        user = self._require_admin()
        if not user:
            return
        if not DATABASE_PATH.exists():
            initialize_database(DATABASE_PATH)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        target = BACKUP_DIR / f"report_database_{stamp}.xlsx"
        shutil.copyfile(DATABASE_PATH, target)
        _write_audit(user, "backup_database", "data_maintenance", target.name, True, "")
        self._send_json({"ok": True, "backup": {"name": target.name, "size": target.stat().st_size}})

    def _admin_audit_logs(self) -> None:
        user = self._require_admin()
        if not user:
            return
        logs = _read_audit_logs(limit=120)
        self._send_json({"logs": logs})

    def _session_token(self) -> str:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            name, _, value = part.strip().partition("=")
            if name == "drp_session":
                return value
        return ""

    def _current_user(self) -> dict[str, object] | None:
        _ensure_admin_files()
        session = SESSIONS.get(self._session_token())
        if not session:
            return None
        username = str(session.get("username", ""))
        return next((user for user in _load_users() if user.get("username") == username and user.get("status") == "active"), None)

    def _require_admin(self) -> dict[str, object] | None:
        user = self._current_user()
        if not user:
            self._send_json({"error": "请先登录后台。"}, status=401)
            return None
        if user.get("role") != "admin":
            self._send_json({"error": "当前账号没有后台管理权限。"}, status=403)
            return None
        return user

    def _require_permission(self, permission: str) -> dict[str, object] | None:
        user = self._current_user()
        if not user:
            self._send_json({"error": "请先登录。"}, status=401)
            return None
        if not _role_permissions(str(user.get("role", ""))).get(permission):
            self._send_json({"error": "当前账号没有该操作权限。"}, status=403)
            return None
        return user

    def _redirect_login(self, next_path: str) -> None:
        self._redirect_to(f"/login/?next={next_path}")

    def _redirect_to(self, location: str) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def _import_pdf(self) -> None:
        try:
            upload = self._read_pdf_upload()
            pdf_bytes = upload.data
            payload = parse_pdf_daily_report(pdf_bytes)
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "drilling")
            self._store_source_pdf(payload, pdf_bytes)
            self._send_json(payload)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_completion_pdf(self) -> None:
        try:
            upload = self._read_pdf_upload()
            pdf_bytes = upload.data
            payload = parse_completion_pdf_daily_report(pdf_bytes)
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "completion")
            self._store_source_pdf(payload, pdf_bytes)
            self._send_json(payload)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_workover_pdf(self) -> None:
        try:
            upload = self._read_pdf_upload()
            pdf_bytes = upload.data
            payload = parse_workover_pdf_daily_report(pdf_bytes)
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "workover")
            self._store_source_pdf(payload, pdf_bytes)
            self._send_json(payload)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_move_pdf(self) -> None:
        try:
            upload = self._read_pdf_upload()
            pdf_bytes = upload.data
            payload = parse_move_pdf_daily_report(pdf_bytes)
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "move")
            self._store_source_pdf(payload, pdf_bytes)
            self._send_json(payload)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _save_report(self) -> None:
        try:
            payload = self._read_json_body()
            report_type = str(payload.get("report_type", ""))
            report_payload = payload.get("payload", {})
            if not isinstance(report_payload, dict):
                self._send_json({"error": "Invalid report payload."}, status=400)
                return
            self._store_payload(report_payload, report_type)
            self._send_json({"ok": True, "metadata": report_payload.get("metadata", {})})
        except PermissionError as exc:
            self._send_json({"error": str(exc)}, status=409)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _load_report(self) -> None:
        try:
            payload = self._read_json_body()
            record_id = str(payload.get("record_id", "")).strip()
            if not record_id:
                self._send_json({"error": "record_id is required."}, status=400)
                return
            self._send_json(load_report_payload(DATABASE_PATH, record_id))
        except KeyError:
            self._send_json({"error": "Record not found."}, status=404)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _translate_report(self) -> None:
        try:
            request_payload = self._read_json_body()
            target_language = str(request_payload.get("target_language", "zh") or "zh").strip().lower()
            if target_language not in {"zh", "en", "es"}:
                self._send_json({"error": "target_language must be zh, en or es."}, status=400)
                return
            report_payload = request_payload.get("payload", {})
            if not isinstance(report_payload, dict):
                self._send_json({"error": "Invalid report payload."}, status=400)
                return
            terms = TermsConfig.from_data(_load_translation_terms_config())
            result = build_translator(terms=terms, target_language=target_language).translate_report_payload(report_payload)
            self._send_json(result)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _save_production_report_remark(self, user: dict[str, object]) -> None:
        payload = self._read_json_body()
        remark_key = str(payload.get("remark_key", "") or "").strip()
        remark = str(payload.get("remarks", "") or "").strip()[:500]
        if not remark_key:
            self._send_json({"error": "缺少备注行标识。"}, status=400)
            return
        remarks = _load_production_report_remarks()
        if remark:
            remarks[remark_key] = remark
        else:
            remarks.pop(remark_key, None)
        _save_production_report_remarks(remarks)
        _write_audit(user, "save_production_report_remark", "production_report", remark_key, True, "")
        self._send_json({"ok": True, "remark_key": remark_key, "remarks": remark})

    def _list_records(self, query: str) -> None:
        params = parse_qs(query)
        report_type = (params.get("report_type") or [""])[0]
        records = list_records(
            DATABASE_PATH,
            report_type=report_type,
            wellbore=(params.get("wellbore") or [""])[0],
            date=(params.get("date") or [""])[0],
            date_from=(params.get("date_from") or [""])[0],
            date_to=(params.get("date_to") or [""])[0],
        )
        self._send_json({"records": records})

    def _well_stats(self, query: str) -> None:
        params = parse_qs(query)
        report_type = (params.get("report_type") or [""])[0]
        wellbore = (params.get("wellbore") or [""])[0]
        records = list_records(DATABASE_PATH)
        matched = [
            record for record in records
            if (not report_type or record.get("report_type") == report_type)
            and (not wellbore or record.get("wellbore") == wellbore)
        ]
        stats = {
            "days": len({record.get("reportDate") for record in matched if record.get("reportDate")}),
            "total_hours": 0.0,
            "npt_hours": 0.0,
            "p_hours": 0.0,
            "sc_hours": 0.0,
            "rig": "",
            "afe_number": "",
            "move_date": "",
            "drilling_start_date": "",
            "completion_date": "",
            "workover_date": "",
        }
        for record in matched:
            record_id = str(record.get("record_id") or "")
            if not record_id:
                continue
            try:
                payload = load_report_payload(DATABASE_PATH, record_id)
            except KeyError:
                continue
            fields = payload.get("report_fields", {}) if isinstance(payload.get("report_fields", {}), dict) else {}
            if not stats["rig"] and fields.get("rig"):
                stats["rig"] = _normalize_rig_name(str(fields.get("rig", "") or ""))
            if not stats["afe_number"] and fields.get("afeNumber"):
                stats["afe_number"] = str(fields.get("afeNumber", "") or "")
            report_date = str(fields.get("reportDate", "") or record.get("reportDate", "") or "")
            event = str(fields.get("event", "") or record.get("event", "") or "")
            _apply_well_stat_dates(stats, event, report_date, str(record.get("report_type", "") or ""))
            operations = payload.get("operations", [])
            if not isinstance(operations, list):
                continue
            for row in operations:
                if not isinstance(row, dict):
                    continue
                try:
                    hours = float(str(row.get("hours", "") or "0").replace(",", ""))
                except ValueError:
                    hours = 0.0
                op_type = str(row.get("op_type", "") or "").strip().upper()
                stats["total_hours"] += hours
                if op_type == "NPT":
                    stats["npt_hours"] += hours
                elif op_type == "SC":
                    stats["sc_hours"] += hours
                elif op_type == "P":
                    stats["p_hours"] += hours
        self._send_json(stats)

    def _production_summary(self, query: str) -> None:
        self._send_json(_production_summary_payload(DATABASE_PATH, parse_qs(query)))

    def _production_summary_export(self, query: str) -> None:
        params = parse_qs(query)
        params["project_mode"] = ["1"]
        payload = _production_summary_payload(DATABASE_PATH, params)
        rows = payload.get("details", [])
        if not isinstance(rows, list):
            rows = []
        rows = _sort_production_export_rows(
            rows,
            _param(params, "sort_field"),
            _param(params, "sort_dir"),
        )
        data = _production_report_workbook_bytes(rows, show_rig=_param(params, "view") == "project")
        filename = f"生产报表-{datetime.now().strftime('%Y%m%d-%H%M%S')}.xlsx"
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f"attachment; filename=\"production-report.xlsx\"; filename*=UTF-8''{quote(filename)}")
        self.end_headers()
        self.wfile.write(data)

    def _npt_stats(self, query: str) -> None:
        self._send_json(_npt_stats_payload(DATABASE_PATH, parse_qs(query)))

    def _npt_stats_export(self, query: str) -> None:
        params = parse_qs(query)
        params["project_mode"] = ["1"]
        payload = _npt_stats_payload(DATABASE_PATH, params)
        rows = payload.get("details", [])
        if not isinstance(rows, list):
            rows = []
        rows = _sort_production_export_rows(
            rows,
            _param(params, "sort_field"),
            _param(params, "sort_dir"),
        )
        data = _npt_report_workbook_bytes(rows, show_rig=_param(params, "view") == "project")
        filename = f"NPT统计-{datetime.now().strftime('%Y%m%d-%H%M%S')}.xlsx"
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f"attachment; filename=\"npt-stats.xlsx\"; filename*=UTF-8''{quote(filename)}")
        self.end_headers()
        self.wfile.write(data)

    def _npt_confirmations(self, query: str, user: dict[str, object]) -> None:
        params = parse_qs(query)
        payload = list_npt_confirmation_wells(
            DATABASE_PATH,
            rig=(params.get("rig") or [""])[0],
            wellbore=(params.get("wellbore") or [""])[0],
            status=(params.get("status") or [""])[0],
            scope_rig=_npt_scope_rig(user),
        )
        payload["scope"] = {"all_rigs": _can_view_all_rigs(user), "rig": _npt_scope_rig(user)}
        self._send_json(payload)

    def _npt_confirmation_detail(self, query: str, user: dict[str, object]) -> None:
        params = parse_qs(query)
        wellbore = (params.get("wellbore") or [""])[0].strip()
        if not wellbore:
            self._send_json({"error": "wellbore is required."}, status=400)
            return
        try:
            self._send_json(load_npt_confirmation_detail(
                DATABASE_PATH,
                wellbore,
                rig=(params.get("rig") or [""])[0],
                scope_rig=_npt_scope_rig(user),
            ))
        except KeyError:
            self._send_json({"error": "NPT confirmation well not found."}, status=404)
        except Exception as exc:  # pragma: no cover - keeps local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _save_npt_confirmation(self, user: dict[str, object]) -> None:
        try:
            payload = self._read_json_body()
            wellbore = str(payload.get("wellbore", "")).strip()
            if not wellbore:
                self._send_json({"error": "wellbore is required."}, status=400)
                return
            operations = payload.get("operations", [])
            if not isinstance(operations, list):
                self._send_json({"error": "operations must be a list."}, status=400)
                return
            result = save_npt_confirmation(
                DATABASE_PATH,
                wellbore,
                operations,
                rig=str(payload.get("rig", "") or ""),
                note=str(payload.get("note", "") or ""),
                confirmed_by=str(user.get("username", "") or ""),
                submit=bool(payload.get("submit")),
            )
            _write_audit(user, "submit_npt_confirmation" if payload.get("submit") else "save_npt_confirmation", "npt_confirmation", wellbore, True, result.get("status", ""))
            self._send_json({"ok": True, **result})
        except PermissionError as exc:
            self._send_json({"error": str(exc)}, status=409)
        except Exception as exc:  # pragma: no cover - keeps local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _download_database(self) -> None:
        if not DATABASE_PATH.exists():
            initialize_database(DATABASE_PATH)
        data = DATABASE_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", 'attachment; filename="report_database.xlsx"')
        self.end_headers()
        self.wfile.write(data)

    def _source_pdf(self, query: str) -> None:
        record_id = (parse_qs(query).get("record_id") or [""])[0].strip()
        if not record_id:
            self.send_error(400, "record_id is required")
            return
        target = _source_pdf_path(record_id)
        if not target.exists():
            self.send_error(404, "Source PDF not found")
            return
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", 'inline; filename="source-report.pdf"')
        self.end_headers()
        self.wfile.write(data)

    def _store_payload(self, payload: dict[str, object], report_type: str) -> None:
        metadata = payload.setdefault("metadata", {})
        warnings = list(dict.fromkeys(_normalize_payload_values(payload) + _validation_warnings(payload, report_type)))
        if isinstance(metadata, dict):
            metadata.setdefault("status", "parsed")
            metadata["validation_status"] = "warning" if warnings else "ok"
            metadata["validation_warnings"] = "; ".join(warnings)
        result = save_report_payload(
            DATABASE_PATH,
            payload,
            report_type,
            source_file=str(metadata.get("source_file", "")) if isinstance(metadata, dict) else "",
        )
        _auto_register_project_well(payload, report_type)
        if isinstance(metadata, dict):
            metadata.update(result)

    def _store_source_pdf(self, payload: dict[str, object], pdf_bytes: bytes) -> None:
        if not _load_config().get("save_source_pdf", True):
            return
        metadata = payload.get("metadata", {})
        record_id = str(metadata.get("record_id", "") if isinstance(metadata, dict) else "").strip()
        if not record_id or not pdf_bytes:
            return
        target = _source_pdf_path(record_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(pdf_bytes)

    def _read_json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _read_pdf_upload(self) -> UploadedFile:
        upload = self._read_multipart_file("report")
        if not upload.filename:
            raise ValueError("No PDF file received.")
        if Path(upload.filename).suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")
        return upload

    def _read_multipart_file(self, field_name: str) -> UploadedFile:
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("multipart/form-data"):
            raise ValueError("Expected multipart form data.")
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            raise ValueError("No PDF file received.")

        body = self.rfile.read(length)
        message = BytesParser(policy=email_policy).parsebytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
        )
        if not message.is_multipart():
            raise ValueError("Invalid multipart form data.")

        for part in message.iter_parts():
            if part.get_content_disposition() != "form-data":
                continue
            if part.get_param("name", header="content-disposition") != field_name:
                continue
            filename = part.get_filename("")
            if not filename:
                break
            return UploadedFile(filename=filename, data=part.get_payload(decode=True) or b"")
        raise ValueError("No PDF file received.")

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def _serve_static(self, include_body: bool = True) -> None:
        raw_path = unquote(self.path.split("?", 1)[0])
        if raw_path.startswith("/login/"):
            rel = raw_path.removeprefix("/login/")
            target = WEB_ROOT / (rel or "login.html")
        elif raw_path.startswith("/admin/"):
            rel = raw_path.removeprefix("/admin/")
            target = WEB_ROOT / (rel or "admin.html")
        elif raw_path.startswith("/web_form/"):
            rel = raw_path.removeprefix("/web_form/")
            target = WEB_ROOT / (rel or "index.html")
        else:
            self.send_error(404)
            return

        self._serve_static_file(target, include_body=include_body)

    def _serve_static_file(self, target: Path, include_body: bool = True) -> None:

        target = target.resolve()
        if not str(target).startswith(str(WEB_ROOT.resolve())) or not target.exists() or target.is_dir():
            self.send_error(404)
            return

        data = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if target.suffix in {".html", ".css", ".js"}:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if include_body:
            self.wfile.write(data)


def _source_pdf_path(record_id: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9_.:-]+", "_", record_id).strip("._")
    return SOURCE_PDF_DIR / f"{safe_name or 'record'}.pdf"


def _default_config() -> dict[str, object]:
    return {
        "system_name": "钻完井日报分析系统",
        "default_language": "zh",
        "records_per_page": 10,
        "excel_path": str(DATABASE_PATH),
        "save_source_pdf": True,
        "source_pdf_retention_days": 365,
    }


def _permission_keys() -> tuple[str, ...]:
    return ("view", "import", "edit", "save", "export", "admin")


def _default_roles() -> list[dict[str, object]]:
    return [
        {"value": "admin", "label": "管理员", "permissions": {key: True for key in _permission_keys()}},
        {"value": "engineer", "label": "工程师", "permissions": {"view": True, "import": True, "edit": True, "save": True, "export": True, "admin": False}},
        {"value": "reviewer", "label": "审阅者", "permissions": {"view": True, "import": False, "edit": True, "save": True, "export": True, "admin": False}},
        {"value": "viewer", "label": "查看者", "permissions": {"view": True, "import": False, "edit": False, "save": False, "export": False, "admin": False}},
    ]


def _role_definitions() -> list[dict[str, object]]:
    return _normalize_roles(_load_roles())


def _role_permissions(role: str) -> dict[str, bool]:
    base = {key: False for key in _permission_keys()}
    target = next((item for item in _role_definitions() if item.get("value") == role), None)
    if not target:
        return base
    permissions = target.get("permissions") if isinstance(target.get("permissions"), dict) else {}
    return {key: bool(permissions.get(key)) for key in _permission_keys()}


def _normalize_role_value(value: object) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value or "").strip().lower()).strip("_")[:40]


def _normalize_roles(raw_roles: object) -> list[dict[str, object]]:
    source = raw_roles if isinstance(raw_roles, list) else []
    defaults = {str(role["value"]): role for role in _default_roles()}
    roles: list[dict[str, object]] = []
    seen: set[str] = set()
    for item in source:
        if not isinstance(item, dict):
            continue
        value = _normalize_role_value(item.get("value"))
        if not value or value in seen:
            continue
        label = str(item.get("label") or value).strip()[:40] or value
        input_permissions = item.get("permissions") if isinstance(item.get("permissions"), dict) else {}
        permissions = {key: bool(input_permissions.get(key)) for key in _permission_keys()}
        if value == "admin":
            label = label or "管理员"
            permissions = {key: True for key in _permission_keys()}
        roles.append({"value": value, "label": label, "permissions": permissions})
        seen.add(value)
    if "admin" not in seen:
        roles.insert(0, defaults["admin"])
        seen.add("admin")
    for value in ("engineer", "reviewer", "viewer"):
        if value not in seen:
            roles.append(defaults[value])
            seen.add(value)
    return roles


def _ensure_admin_files() -> None:
    ROOT.joinpath("outputs").mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        _save_config(_default_config())
    if not ROLES_PATH.exists():
        _save_roles(_default_roles())
    if not PROJECT_TEAM_PATH.exists():
        _save_project_team_config(_default_project_team_config())
    if not TRANSLATION_TERMS_PATH.exists():
        _save_translation_terms_config(_default_translation_terms_config())
    if not USERS_PATH.exists():
        admin = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "display_name": "系统管理员",
            "email": "",
            "role": "admin",
            "status": "active",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "last_login": "",
            "must_change_password": True,
            "password_hash": _hash_password("admin123"),
        }
        _save_users([admin])
        _write_audit(admin, "init_admin", "system_admin", "admin", True, "default password admin123")


def _load_config() -> dict[str, object]:
    _ensure_parent(CONFIG_PATH)
    if not CONFIG_PATH.exists():
        return _default_config()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {}
    return {**_default_config(), **{key: data.get(key) for key in _default_config() if key in data}}


def _save_config(config: dict[str, object]) -> None:
    _ensure_parent(CONFIG_PATH)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_roles() -> list[dict[str, object]]:
    _ensure_parent(ROLES_PATH)
    if not ROLES_PATH.exists():
        return _default_roles()
    try:
        data = json.loads(ROLES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else _default_roles()


def _save_roles(roles: list[dict[str, object]]) -> None:
    _ensure_parent(ROLES_PATH)
    ROLES_PATH.write_text(json.dumps(_normalize_roles(roles), ensure_ascii=False, indent=2), encoding="utf-8")


def _default_project_team_config() -> dict[str, object]:
    return {"teams": [], "projects": [], "pending_wells": []}


def _load_project_team_config() -> dict[str, object]:
    _ensure_parent(PROJECT_TEAM_PATH)
    if not PROJECT_TEAM_PATH.exists():
        return _default_project_team_config()
    try:
        data = json.loads(PROJECT_TEAM_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {}
    return _normalize_project_team_config(data)


def _save_project_team_config(config: dict[str, object]) -> None:
    _ensure_parent(PROJECT_TEAM_PATH)
    PROJECT_TEAM_PATH.write_text(json.dumps(_normalize_project_team_config(config), ensure_ascii=False, indent=2), encoding="utf-8")


def _load_production_report_remarks() -> dict[str, str]:
    _ensure_parent(PRODUCTION_REPORT_REMARKS_PATH)
    if not PRODUCTION_REPORT_REMARKS_PATH.exists():
        return {}
    try:
        data = json.loads(PRODUCTION_REPORT_REMARKS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        return {}
    return {str(key): str(value or "")[:500] for key, value in data.items() if str(key).strip()}


def _save_production_report_remarks(remarks: dict[str, str]) -> None:
    _ensure_parent(PRODUCTION_REPORT_REMARKS_PATH)
    clean = {str(key): str(value or "")[:500] for key, value in remarks.items() if str(key).strip() and str(value or "").strip()}
    PRODUCTION_REPORT_REMARKS_PATH.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")


def _default_translation_terms_config() -> dict[str, object]:
    try:
        data = json.loads(DEFAULT_TRANSLATION_TERMS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {"terms": [], "protected_terms": _default_protected_terms()}
    return _normalize_translation_terms_config(data)


def _load_translation_terms_config() -> dict[str, object]:
    _ensure_parent(TRANSLATION_TERMS_PATH)
    if not TRANSLATION_TERMS_PATH.exists():
        return _default_translation_terms_config()
    try:
        data = json.loads(TRANSLATION_TERMS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {}
    return _normalize_translation_terms_config(data)


def _save_translation_terms_config(config: dict[str, object]) -> None:
    _ensure_parent(TRANSLATION_TERMS_PATH)
    TRANSLATION_TERMS_PATH.write_text(json.dumps(_normalize_translation_terms_config(config), ensure_ascii=False, indent=2), encoding="utf-8")


def _normalize_translation_terms_config(raw: object) -> dict[str, object]:
    source = raw if isinstance(raw, dict) else {}
    now = datetime.now().isoformat(timespec="seconds")
    terms: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in _list_value(source.get("terms")):
        if not isinstance(item, dict):
            continue
        zh = str(item.get("zh", "") or "").strip()
        en = str(item.get("en", "") or "").strip()
        es = str(item.get("es", "") or "").strip()
        if not (zh or en or es):
            continue
        key = (zh.lower(), en.lower(), es.lower())
        if key in seen:
            continue
        seen.add(key)
        aliases_source = item.get("aliases") if isinstance(item.get("aliases"), dict) else {}
        aliases = {
            language: _normalized_string_list(aliases_source.get(language))
            for language in ("zh", "en", "es")
        }
        terms.append({
            "id": str(item.get("id") or uuid.uuid4()).strip(),
            "category": str(item.get("category", "drilling") or "drilling").strip()[:60],
            "zh": zh,
            "en": en,
            "es": es,
            "aliases": aliases,
            "protected": bool(item.get("protected", True)),
            "enabled": bool(item.get("enabled", True)),
            "updated_at": str(item.get("updated_at") or now),
        })

    protected_source = source.get("protected_terms") if isinstance(source.get("protected_terms"), dict) else {}
    protected_defaults = _default_protected_terms()
    protected_terms = {
        "acronyms": _normalized_string_list(protected_source.get("acronyms", protected_defaults["acronyms"])),
        "units": _normalized_string_list(protected_source.get("units", protected_defaults["units"])),
        "proper_nouns": _normalized_string_list(protected_source.get("proper_nouns", protected_defaults["proper_nouns"])),
    }
    return {"terms": terms, "protected_terms": protected_terms}


def _default_protected_terms() -> dict[str, list[str]]:
    return {
        "acronyms": [
            "ROP", "WOB", "RPM", "SPP", "TVD", "MD", "BHA", "BOP", "MW", "ECD", "NPT", "WOC",
            "AFE", "HSE", "HSSE", "LTA", "RI", "API", "HTHP", "PV", "YP", "EMW", "WBM", "OBM",
        ],
        "units": ["m", "ft", "in", "ppg", "psi", "bbl", "gpm", "klb", "lb", "hr", "hrs", "deg", "deg/100ft", "spf"],
        "proper_nouns": [
            "SINOPEC", "PETROECUADOR", "HALLIBURTON", "SCHLUMBERGER", "BAKER HUGHES",
            "WEATHERFORD", "NABORS", "Napo", "Hollin", "Tena", "Basal Tena", "Orteguaza",
        ],
    }


def _normalized_string_list(value: object) -> list[str]:
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


def _normalize_rig_name(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = re.sub(r"^00\s+(SINOPEC\b)", r"\1", text, flags=re.I)
    text = re.sub(r"\bSINOPEC[-\s]*(\d+)\b", r"SINOPEC \1", text, flags=re.I)
    return text


def _list_value(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _normalize_project_team_config(raw: object) -> dict[str, object]:
    source = raw if isinstance(raw, dict) else {}
    now = datetime.now().isoformat(timespec="seconds")
    teams: list[dict[str, object]] = []
    seen_teams: set[str] = set()
    for item in _list_value(source.get("teams")):
        if not isinstance(item, dict):
            continue
        raw_name = str(item.get("name", "") or item.get("rig", "") or "").strip()
        name = _normalize_rig_name(raw_name)
        if not name or name in seen_teams:
            continue
        aliases = _normalized_string_list(item.get("aliases"))
        if raw_name and raw_name != name and raw_name not in aliases:
            aliases.insert(0, raw_name)
        teams.append({
            "id": str(item.get("id") or uuid.uuid4()),
            "name": name,
            "code": str(item.get("code", "") or "").strip(),
            "contractor": str(item.get("contractor", "") or "").strip(),
            "aliases": aliases,
            "status": str(item.get("status", "active") or "active").strip() or "active",
            "created_at": str(item.get("created_at") or now),
        })
        seen_teams.add(name)

    projects: list[dict[str, object]] = []
    seen_projects: set[str] = set()
    for item in _list_value(source.get("projects")):
        if not isinstance(item, dict):
            continue
        contract_no = str(item.get("contract_no", "") or "").strip()
        project_name = str(item.get("project_name", "") or item.get("name", "") or "").strip()
        key = contract_no or project_name
        if not key or key in seen_projects:
            continue
        rigs: list[dict[str, object]] = []
        seen_rigs: set[str] = set()
        for rig_item in _list_value(item.get("rigs")):
            if not isinstance(rig_item, dict):
                continue
            rig_name = _normalize_rig_name(str(rig_item.get("rig", "") or rig_item.get("name", "") or "").strip())
            if not rig_name or rig_name in seen_rigs:
                continue
            wells = sorted({str(well or "").strip() for well in _list_value(rig_item.get("wells")) if str(well or "").strip()})
            rigs.append({
                "rig": rig_name,
                "start_date": str(rig_item.get("start_date", "") or "").strip(),
                "end_date": str(rig_item.get("end_date", "") or "").strip(),
                "wells": wells,
                "note": str(rig_item.get("note", "") or "").strip(),
            })
            seen_rigs.add(rig_name)
        projects.append({
            "id": str(item.get("id") or uuid.uuid4()),
            "contract_no": contract_no,
            "project_name": project_name,
            "status": str(item.get("status", "active") or "active").strip() or "active",
            "start_date": str(item.get("start_date", "") or "").strip(),
            "end_date": str(item.get("end_date", "") or "").strip(),
            "note": str(item.get("note", "") or "").strip(),
            "rigs": rigs,
            "created_at": str(item.get("created_at") or now),
            "updated_at": str(item.get("updated_at") or now),
        })
        seen_projects.add(key)

    pending: list[dict[str, object]] = []
    seen_pending: set[tuple[str, str]] = set()
    for item in _list_value(source.get("pending_wells")):
        if not isinstance(item, dict):
            continue
        rig = _normalize_rig_name(str(item.get("rig", "") or "").strip())
        wellbore = str(item.get("wellbore", "") or "").strip()
        if not rig or not wellbore or (rig, wellbore) in seen_pending:
            continue
        pending.append({
            "rig": rig,
            "wellbore": wellbore,
            "report_type": str(item.get("report_type", "") or "").strip(),
            "source": str(item.get("source", "report") or "report").strip(),
            "created_at": str(item.get("created_at") or now),
        })
        seen_pending.add((rig, wellbore))
    return {"teams": teams, "projects": projects, "pending_wells": pending}


def _auto_register_project_well(payload: dict[str, object], report_type: str) -> None:
    fields = payload.get("report_fields") if isinstance(payload.get("report_fields"), dict) else {}
    rig = _normalize_rig_name(str(fields.get("rig", "") or "").strip())
    wellbore = str(fields.get("wellbore", "") or "").strip()
    if not rig or not wellbore:
        return
    config = _load_project_team_config()
    now = datetime.now().isoformat(timespec="seconds")
    if not any(_team_name_matches(team, rig) for team in config["teams"]):
        config["teams"].append({"id": str(uuid.uuid4()), "name": rig, "code": "", "contractor": "", "aliases": [], "status": "active", "created_at": now})
    active_projects = [project for project in config["projects"] if str(project.get("status", "active")) == "active"]
    report_date = str(fields.get("reportDate", "") or "").strip()
    project_matches = _project_rig_matches(config, rig, report_date)
    if len(project_matches) == 1:
        project, target = project_matches[0]
        wells = target.setdefault("wells", [])
        if wellbore not in wells:
            wells.append(wellbore)
            wells.sort()
            project["updated_at"] = now
    elif len(active_projects) == 1:
        _add_pending_or_single_project_well(config, active_projects[0], rig, wellbore, now)
    else:
        pending_item = _find_pending_well(config, rig, wellbore)
        if pending_item is not None:
            if not str(pending_item.get("report_type", "") or "").strip():
                pending_item["report_type"] = report_type
        else:
            config["pending_wells"].append({"rig": rig, "wellbore": wellbore, "report_type": report_type, "source": "report", "created_at": now})
    _save_project_team_config(config)


def _sync_project_wells_from_database(database_path: Path = DATABASE_PATH) -> dict[str, object]:
    config = _load_project_team_config()
    if not database_path.exists():
        return config

    changed = False
    now = datetime.now().isoformat(timespec="seconds")
    for record in list_records(database_path):
        report_type = str(record.get("report_type", "") or "").strip()
        if report_type not in {"drilling", "completion", "workover"}:
            continue
        rig = _normalize_rig_name(str(record.get("rig", "") or "").strip())
        wellbore = str(record.get("wellbore", "") or "").strip()
        if not rig or not wellbore:
            continue
        if not any(_team_name_matches(team, rig) for team in config["teams"]):
            config["teams"].append({
                "id": str(uuid.uuid4()),
                "name": rig,
                "code": "",
                "contractor": "",
                "aliases": [],
                "status": "active",
                "created_at": now,
            })
            changed = True

        report_date = str(record.get("reportDate", "") or "").strip()
        project_matches = _project_rig_matches(config, rig, report_date)
        if len(project_matches) == 1:
            project, target = project_matches[0]
            wells = target.setdefault("wells", [])
            if wellbore not in wells:
                wells.append(wellbore)
                wells.sort()
                project["updated_at"] = now
                changed = True
            if _remove_pending_well(config, rig, wellbore):
                changed = True
            continue

        active_projects = [project for project in config["projects"] if str(project.get("status", "active")) == "active"]
        if len(active_projects) == 1:
            before = json.dumps(config, ensure_ascii=False, sort_keys=True)
            _add_pending_or_single_project_well(config, active_projects[0], rig, wellbore, now)
            changed = changed or before != json.dumps(config, ensure_ascii=False, sort_keys=True)
            continue

        if _project_has_well(config, rig, wellbore):
            continue
        pending_item = _find_pending_well(config, rig, wellbore)
        if pending_item is not None:
            if not str(pending_item.get("report_type", "") or "").strip():
                pending_item["report_type"] = report_type
                changed = True
            continue
        if not _pending_has_well(config, rig, wellbore):
            config["pending_wells"].append({
                "rig": rig,
                "wellbore": wellbore,
                "report_type": report_type,
                "source": "report",
                "created_at": now,
            })
            changed = True

    if changed:
        _save_project_team_config(config)
        config = _load_project_team_config()
    return config


def _project_has_well(config: dict[str, object], rig: str, wellbore: str) -> bool:
    for project in config.get("projects", []) if isinstance(config.get("projects"), list) else []:
        for rig_item in project.get("rigs", []) if isinstance(project.get("rigs"), list) else []:
            if not _rig_name_matches(config, str(rig_item.get("rig", "") or "").strip(), rig):
                continue
            wells = {str(well or "").strip() for well in _list_value(rig_item.get("wells")) if str(well or "").strip()}
            if wellbore in wells:
                return True
    return False


def _pending_has_well(config: dict[str, object], rig: str, wellbore: str) -> bool:
    return any(item.get("rig") == rig and item.get("wellbore") == wellbore for item in _list_value(config.get("pending_wells")))


def _find_pending_well(config: dict[str, object], rig: str, wellbore: str) -> dict[str, object] | None:
    for item in _list_value(config.get("pending_wells")):
        if item.get("rig") == rig and item.get("wellbore") == wellbore:
            return item
    return None


def _remove_pending_well(config: dict[str, object], rig: str, wellbore: str) -> bool:
    current = _list_value(config.get("pending_wells"))
    next_items = [item for item in current if not (item.get("rig") == rig and item.get("wellbore") == wellbore)]
    if len(next_items) == len(current):
        return False
    config["pending_wells"] = next_items
    return True


def _project_rig_matches(config: dict[str, object], rig: str, report_date: str = "") -> list[tuple[dict[str, object], dict[str, object]]]:
    matches = []
    for project in config.get("projects", []) if isinstance(config.get("projects"), list) else []:
        if str(project.get("status", "active") or "active") != "active":
            continue
        if not _date_in_range(report_date, str(project.get("start_date", "") or ""), str(project.get("end_date", "") or "")):
            continue
        for rig_item in project.get("rigs", []) if isinstance(project.get("rigs"), list) else []:
            if _rig_name_matches(config, str(rig_item.get("rig", "") or "").strip(), rig):
                matches.append((project, rig_item))
                break
    return matches


def _add_pending_or_single_project_well(config: dict[str, object], project: dict[str, object], rig: str, wellbore: str, now: str) -> None:
    rigs = project.setdefault("rigs", [])
    target = next((item for item in rigs if item.get("rig") == rig), None)
    if target is None:
        target = {"rig": rig, "start_date": "", "end_date": "", "wells": [], "note": ""}
        rigs.append(target)
    wells = target.setdefault("wells", [])
    if wellbore not in wells:
        wells.append(wellbore)
        wells.sort()
        project["updated_at"] = now
    config["pending_wells"] = [
        item for item in _list_value(config.get("pending_wells"))
        if not (item.get("rig") == rig and item.get("wellbore") == wellbore)
    ]


def _load_users() -> list[dict[str, object]]:
    if not USERS_PATH.exists():
        _ensure_admin_files()
    try:
        data = json.loads(USERS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else []


def _save_users(users: list[dict[str, object]]) -> None:
    _ensure_parent(USERS_PATH)
    USERS_PATH.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def _public_user(user: dict[str, object]) -> dict[str, object]:
    data = {key: user.get(key, "") for key in ("id", "username", "display_name", "email", "role", "status", "created_at", "last_login", "rig")}
    if "rigs" in user:
        data["rigs"] = user.get("rigs", [])
    data["must_change_password"] = bool(user.get("must_change_password"))
    return data


def _can_view_all_rigs(user: dict[str, object]) -> bool:
    return bool(_role_permissions(str(user.get("role", ""))).get("admin")) or str(user.get("role", "")) == "admin"


def _npt_scope_rig(user: dict[str, object]) -> str:
    if _can_view_all_rigs(user):
        return ""
    rigs = user.get("rigs")
    if isinstance(rigs, list) and rigs:
        return str(rigs[0] or "")
    return str(user.get("rig", "") or "")


def _active_admin_count(users: list[dict[str, object]]) -> int:
    return sum(1 for user in users if user.get("role") == "admin" and user.get("status") == "active")


def _reset_admin_password(username: str, password: str) -> None:
    users = _load_users()
    target = next((item for item in users if item.get("username") == username), None)
    if target is None:
        target = {
            "id": str(uuid.uuid4()),
            "username": username,
            "display_name": "系统管理员",
            "email": "",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        users.append(target)
    target["role"] = "admin"
    target["status"] = "active"
    target["password_hash"] = _hash_password(password)
    target["must_change_password"] = True
    _save_users(users)
    _write_audit(target, "reset_admin_password", "system_admin", username, True, "command line reset")


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt, digest = stored.split("$", 2)
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()
    return hmac.compare_digest(expected, digest)


def _write_audit(user: dict[str, object] | None, action: str, module: str, target: str, ok: bool, note: str = "") -> None:
    _ensure_parent(AUDIT_LOG_PATH)
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "user": user.get("username", "") if user else "",
        "display_name": user.get("display_name", "") if user else "",
        "action": action,
        "module": module,
        "target": target,
        "result": "success" if ok else "failed",
        "note": note,
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _read_audit_logs(limit: int = 100) -> list[dict[str, object]]:
    if not AUDIT_LOG_PATH.exists():
        return []
    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()[-limit:]
    logs = []
    for line in reversed(lines):
        try:
            logs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return logs


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the drilling report web form with PDF import.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument("--reset-admin", action="store_true", help="Reset or create an admin account, then exit.")
    parser.add_argument("--admin-username", default="admin")
    parser.add_argument("--admin-password", default="")
    args = parser.parse_args()
    if args.reset_admin:
        password = args.admin_password or secrets.token_urlsafe(10)
        _reset_admin_password(args.admin_username, password)
        print(f"Admin reset complete. username={args.admin_username} password={password}")
        return
    server = ThreadingHTTPServer((args.host, args.port), FormHandler)
    print(f"Drilling report form: http://{args.host}:{args.port}/web_form/")
    server.serve_forever()


def _validation_warnings(payload: dict[str, object], report_type: str) -> list[str]:
    fields = payload.get("report_fields", {})
    if not isinstance(fields, dict):
        return ["report_fields missing"]
    required_by_type = {
        "drilling": ["event", "reportDate", "reportNo", "wellbore", "rig", "todayMd", "progress", "currentOps", "summary24h", "forecast24h", "mudType", "mudDensity"],
        "completion": ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"],
        "workover": ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"],
        "move": ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"],
    }
    warnings: list[str] = []
    for field in required_by_type.get(report_type, []):
        if not str(fields.get(field, "") or "").strip():
            warnings.append(f"{field} missing")

    if report_type in {"completion", "workover"}:
        for field in ("afeCost", "dailyCost", "cumulativeCost", "totalPersonnel"):
            if _has_value(fields.get(field)) and _safe_float(fields.get(field)) < 0:
                warnings.append(f"{field} negative")

    operations = payload.get("operations", [])
    if isinstance(operations, list) and operations:
        total_hours = 0.0
        clock_hours_by_row = _operation_clock_hours_by_row(operations)
        for index, row in enumerate(operations, start=1):
            if not isinstance(row, dict):
                continue
            for field in ("from", "to", "hours", "op_code", "operation_details"):
                if not str(row.get(field, "") or "").strip():
                    warnings.append(f"operations row {index} {field} missing")
            try:
                total_hours += float(str(row.get("hours", "") or "0").replace(",", ""))
            except ValueError:
                warnings.append(f"operations row {index} hours invalid")
            valid_types = {"P", "NPT"} if report_type == "drilling" else {"P", "SC", "NPT"}
            if str(row.get("op_type", "") or "").strip() not in valid_types:
                warnings.append(f"operations row {index} type invalid")
            hours = _safe_float(row.get("hours"))
            if hours <= 0 or hours > 24:
                warnings.append(f"operations row {index} hours out of range")
            clock_hours = clock_hours_by_row.get(index - 1)
            if clock_hours is not None and _has_value(row.get("hours")) and abs(clock_hours - hours) > 0.1:
                warnings.append(f"operations row {index} time duration mismatch")
        if abs(total_hours - 24.0) > 0.05:
            warnings.append(f"operation hours total {total_hours:.2f}")
    elif report_type in required_by_type:
        warnings.append("operations missing")

    if fields.get("reportDate"):
        try:
            if datetime.strptime(str(fields.get("reportDate")), "%Y-%m-%d").date() > date.today():
                warnings.append("reportDate is in the future")
        except ValueError:
            warnings.append("reportDate invalid")
    if report_type in {"completion", "workover"} and fields.get("reportDate") and fields.get("operationStartDate"):
        try:
            if datetime.strptime(str(fields.get("operationStartDate")), "%Y-%m-%d").date() > datetime.strptime(str(fields.get("reportDate")), "%Y-%m-%d").date():
                warnings.append("operationStartDate later than reportDate")
        except ValueError:
            pass
    if report_type in {"drilling", "move"}:
        today_md = _safe_float(fields.get("todayMd"))
        prev_md = _safe_float(fields.get("prevMd"))
        progress = _safe_float(fields.get("progress"))
        if str(fields.get("todayMd", "") or "").strip() and str(fields.get("prevMd", "") or "").strip() and today_md < prev_md:
            warnings.append("todayMd less than prevMd")
        if str(fields.get("progress", "") or "").strip() and str(fields.get("todayMd", "") or "").strip() and str(fields.get("prevMd", "") or "").strip() and abs(progress - (today_md - prev_md)) > 0.5:
            warnings.append("progress mismatch")
    if report_type == "drilling":
        mud_density = _safe_float(fields.get("mudDensity"))
        if str(fields.get("mudDensity", "") or "").strip() and (mud_density < 6 or mud_density > 20):
            warnings.append("mudDensity out of range")
        sand = _safe_float(fields.get("sand"))
        if str(fields.get("sand", "") or "").strip() and sand > 10:
            warnings.append("sand out of range")

    if report_type == "drilling":
        survey_rows = payload.get("survey_data", [])
        if isinstance(survey_rows, list):
            today_md = _safe_float(fields.get("todayMd"))
            for index, row in enumerate(survey_rows, start=1):
                if not isinstance(row, dict):
                    continue
                md = _safe_float(row.get("md"))
                incl = _safe_float(row.get("incl"))
                dls = _safe_float(row.get("dls"))
                if str(row.get("md", "") or "").strip() and str(fields.get("todayMd", "") or "").strip() and md > today_md:
                    warnings.append(f"survey_data row {index} md greater than todayMd")
                if str(row.get("incl", "") or "").strip() and (incl < 0 or incl > 180):
                    warnings.append(f"survey_data row {index} incl out of range")
                if str(row.get("dls", "") or "").strip() and dls < 0:
                    warnings.append(f"survey_data row {index} dls negative")
        bha_rows = payload.get("bha_components", [])
        if isinstance(bha_rows, list):
            for index, row in enumerate(bha_rows, start=1):
                if not isinstance(row, dict):
                    continue
                od = _safe_float(row.get("od"))
                item_id = _safe_float(row.get("id"))
                if str(row.get("od", "") or "").strip() and str(row.get("id", "") or "").strip() and od < item_id:
                    warnings.append(f"bha_components row {index} od less than id")
                for field in ("od", "id", "joints", "length"):
                    if str(row.get(field, "") or "").strip() and _safe_float(row.get(field)) < 0:
                        warnings.append(f"bha_components row {index} {field} negative")

    interval_section = "perforation_intervals"
    rows = payload.get(interval_section, [])
    if report_type in {"completion", "workover"} and isinstance(rows, list):
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            top_md = _safe_float(row.get("top_md"))
            base_md = _safe_float(row.get("base_md"))
            length = _safe_float(row.get("length"))
            if str(row.get("top_md", "") or "").strip() and str(row.get("base_md", "") or "").strip() and base_md < top_md:
                warnings.append(f"{interval_section} row {index} base_md less than top_md")
            if str(row.get("length", "") or "").strip() and length < 0:
                warnings.append(f"{interval_section} row {index} length negative")
            for field in ("density", "phase", "penetration", "diameter"):
                if str(row.get(field, "") or "").strip() and _safe_float(row.get(field)) < 0:
                    warnings.append(f"{interval_section} row {index} {field} negative")
    return warnings


DATE_FIELDS = {"reportDate", "operationStartDate", "date", "entry_date"}
TIME_FIELDS = {"from", "to", "mudTime", "entry_time"}
NUMERIC_REPORT_FIELDS = {
    "todayMd", "prevMd", "progress", "rotHrsToday", "lastCasingDepth", "nextCasingDepth",
    "pumpRate", "pumpPress", "mudMd", "mudDensity", "mudTemperature", "rheologyTemp",
    "viscosity", "pv", "yp", "gel10s", "gel10m", "gel30m", "apiWl", "oilPercent",
    "waterPercent", "sand", "ecd", "bitSize", "bhaMdIn", "bhaMdOut", "bhaTotalLength",
    "daysSinceRi", "daysSinceLta", "afeCost", "dailyCost", "cumulativeCost",
    "totalPersonnel", "groundElev",
}
NUMERIC_TABLE_FIELDS = {
    "md", "incl", "azi", "tvd", "vse", "ns", "dls", "build", "od", "id", "joints",
    "length", "hours", "amount", "qty_start", "qty_used", "qty_end", "top_md", "base_md",
    "density", "phase", "penetration", "diameter", "trip",
}

REPORT_TYPE_LABELS = {
    "drilling": "钻井",
    "completion": "完井",
    "workover": "修井",
    "move": "搬迁/推井架",
}
UNASSIGNED_PROJECT_ID = "__unassigned__"


def _production_summary_payload(database_path: Path, params: dict[str, list[str]]) -> dict[str, object]:
    if _truthy(_param(params, "project_mode")) or _param_values(params, "project") or _param_values(params, "rig"):
        _sync_project_wells_from_database(database_path)
    rows = _filtered_fact_rows(database_path, params)
    records = rows["records"]
    operations = rows["operations"]
    unique_rigs = sorted({record["rig"] for record in records if record["rig"]})
    unique_wells = sorted({record["wellbore"] for record in records if record["wellbore"]})
    total_hours = sum(row["hours"] for row in operations)
    npt_hours = sum(row["hours"] for row in operations if row["op_type"] == "NPT")
    completeness = _completeness(records)

    by_rig: dict[str, dict[str, float]] = {}
    npt_by_rig: dict[str, float] = {}
    by_type = {key: 0.0 for key in REPORT_TYPE_LABELS}
    monthly: dict[str, dict[str, float]] = {}

    for row in operations:
        rig = row["rig"] or "未识别井队"
        report_type = row["report_type"]
        by_rig.setdefault(rig, {key: 0.0 for key in REPORT_TYPE_LABELS})
        by_rig[rig][report_type] = by_rig[rig].get(report_type, 0.0) + row["hours"]
        if row["op_type"] == "NPT":
            npt_by_rig[rig] = npt_by_rig.get(rig, 0.0) + row["hours"]
        if report_type in by_type:
            by_type[report_type] += row["hours"]
        month = row["reportDate"][:7] or "未识别"
        monthly.setdefault(month, {key: 0.0 for key in REPORT_TYPE_LABELS})
        monthly[month][report_type] = monthly[month].get(report_type, 0.0) + row["hours"]

    project_mode = _truthy(_param(params, "project_mode")) or bool(_param_values(params, "project"))
    details = _production_report_details(records, operations) if project_mode else _production_summary_details(records, operations)

    return {
        "filters": _filter_options(records, database_path),
        "kpis": {
            "rig_count": len(unique_rigs),
            "well_count": len(unique_wells),
            "total_hours": round(total_hours, 2),
            "npt_hours": round(npt_hours, 2),
            "completeness": completeness,
        },
        "by_rig": [{"rig": rig, **{key: round(value, 2) for key, value in values.items()}} for rig, values in sorted(by_rig.items())],
        "npt_by_rig": [{"label": rig, "hours": round(hours, 2)} for rig, hours in sorted(npt_by_rig.items(), key=lambda item: (-item[1], item[0]))],
        "by_type": [{"report_type": key, "label": REPORT_TYPE_LABELS[key], "hours": round(value, 2)} for key, value in by_type.items()],
        "monthly": [{"month": month, **{key: round(value, 2) for key, value in values.items()}} for month, values in sorted(monthly.items())],
        "details": details,
        "scope_note": "基于已保存到 Excel 库的日报解析数据",
    }


def _production_summary_details(records: list[dict[str, object]], operations: list[dict[str, object]]) -> list[dict[str, object]]:
    detail: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for row in operations:
        rig = str(row.get("rig", "") or "") or "未识别井队"
        report_type = str(row.get("report_type", "") or "")
        type_label = REPORT_TYPE_LABELS.get(report_type, report_type)
        report_date = str(row.get("reportDate", "") or "")
        key = (str(row.get("project_id", "") or ""), rig, str(row.get("wellbore", "") or ""), report_type)
        item = detail.setdefault(key, {
            "project_id": row.get("project_id", ""),
            "project_name": row.get("project_name", ""),
            "project_contract": row.get("project_contract", ""),
            "rig": rig,
            "wellbore": row.get("wellbore", ""),
            "report_type": report_type,
            "report_type_label": type_label,
            "start_date": report_date,
            "end_date": report_date,
            "drilling_hours": 0.0,
            "completion_hours": 0.0,
            "workover_hours": 0.0,
            "move_hours": 0.0,
            "npt_hours": 0.0,
            "record_id": row.get("record_id", ""),
            "status": "",
        })
        item["start_date"] = min(str(item["start_date"] or report_date), report_date)
        item["end_date"] = max(str(item["end_date"] or report_date), report_date)
        item[f"{report_type}_hours"] = float(item.get(f"{report_type}_hours", 0.0)) + float(row.get("hours", 0.0) or 0.0)
        if row.get("op_type") == "NPT":
            item["npt_hours"] = float(item["npt_hours"]) + float(row.get("hours", 0.0) or 0.0)

    record_index = {(str(record.get("project_id", "") or ""), record.get("rig", ""), record.get("wellbore", ""), record.get("report_type", "")): record for record in records}
    for key, item in detail.items():
        record = record_index.get(key, {})
        item["status"] = "有告警" if record.get("validation_status") == "warning" else "正常"

    return [_round_hour_fields(item) for item in detail.values()]


def _production_report_details(records: list[dict[str, object]], operations: list[dict[str, object]]) -> list[dict[str, object]]:
    detail: dict[tuple[str, str, str], dict[str, object]] = {}
    saved_remarks = _load_production_report_remarks()
    for record in records:
        rig = str(record.get("rig", "") or "") or "未识别井队"
        wellbore = str(record.get("wellbore", "") or "")
        project_id = str(record.get("project_id", "") or "")
        key = (project_id, rig, wellbore)
        remark_key = _production_report_remark_key(project_id, rig, wellbore)
        item = detail.setdefault(key, {
            "project_id": project_id,
            "project_name": record.get("project_name", ""),
            "project_contract": record.get("project_contract", ""),
            "contract_project": _contract_project_label(record),
            "rig": rig,
            "wellbore": wellbore,
            "move_date": "",
            "drilling_start_date": "",
            "drilling_finish_date": "",
            "completion_date": "",
            "workover_date": "",
            "move_hours": 0.0,
            "drilling_hours": 0.0,
            "completion_hours": 0.0,
            "workover_hours": 0.0,
            "npt_hours": 0.0,
            "record_id": record.get("record_id", ""),
            "report_type": record.get("report_type", ""),
            "status": "正常",
            "remark_key": remark_key,
            "remarks": saved_remarks.get(remark_key, ""),
        })
        if not item.get("record_id"):
            item["record_id"] = record.get("record_id", "")
            item["report_type"] = record.get("report_type", "")
        if record.get("validation_status") == "warning":
            item["status"] = "有告警"
        _apply_event_dates(item, str(record.get("event", "") or ""), str(record.get("reportDate", "") or ""), str(record.get("report_type", "") or ""))

    for row in operations:
        rig = str(row.get("rig", "") or "") or "未识别井队"
        wellbore = str(row.get("wellbore", "") or "")
        project_id = str(row.get("project_id", "") or "")
        key = (project_id, rig, wellbore)
        remark_key = _production_report_remark_key(project_id, rig, wellbore)
        item = detail.setdefault(key, {
            "project_id": project_id,
            "project_name": row.get("project_name", ""),
            "project_contract": row.get("project_contract", ""),
            "contract_project": _contract_project_label(row),
            "rig": rig,
            "wellbore": wellbore,
            "move_date": "",
            "drilling_start_date": "",
            "drilling_finish_date": "",
            "completion_date": "",
            "workover_date": "",
            "move_hours": 0.0,
            "drilling_hours": 0.0,
            "completion_hours": 0.0,
            "workover_hours": 0.0,
            "npt_hours": 0.0,
            "record_id": row.get("record_id", ""),
            "report_type": row.get("report_type", ""),
            "status": "正常",
            "remark_key": remark_key,
            "remarks": saved_remarks.get(remark_key, ""),
        })
        report_type = str(row.get("report_type", "") or "")
        if report_type in REPORT_TYPE_LABELS:
            item[f"{report_type}_hours"] = float(item.get(f"{report_type}_hours", 0.0)) + float(row.get("hours", 0.0) or 0.0)
        if row.get("op_type") == "NPT":
            item["npt_hours"] = float(item["npt_hours"]) + float(row.get("hours", 0.0) or 0.0)
        if row.get("validation_status") == "warning":
            item["status"] = "有告警"

    return [_round_hour_fields(item) for item in detail.values()]


def _sort_production_export_rows(rows: list[object], sort_field: str, sort_dir: str) -> list[dict[str, object]]:
    clean_rows = [row for row in rows if isinstance(row, dict)]
    if not sort_field:
        return clean_rows
    reverse = str(sort_dir or "").lower() != "asc"
    numeric_fields = {"move_hours", "drilling_hours", "completion_hours", "workover_hours", "npt_hours", "hours"}

    def key(row: dict[str, object]) -> tuple[int, object]:
        value = row.get(sort_field)
        if value in (None, ""):
            return (1, "")
        if sort_field in numeric_fields:
            return (0, _safe_float(value))
        return (0, str(value))

    return sorted(clean_rows, key=key, reverse=reverse)


def _default_sort_npt_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("wellbore") or ""),
            str(row.get("reportDate") or ""),
            str(row.get("project_name") or row.get("contract_project") or ""),
            str(row.get("rig") or ""),
        ),
    )


def _production_report_workbook_bytes(rows: list[dict[str, object]], show_rig: bool = False) -> bytes:
    columns: list[tuple[str, str]] = [
        ("wellbore", "井号"),
        *([("rig", "井队")] if show_rig else []),
        ("contract_project", "合同(项目)"),
        ("move_date", "搬迁日期"),
        ("drilling_start_date", "开钻日期"),
        ("drilling_finish_date", "完钻日期"),
        ("completion_date", "完井日期"),
        ("workover_date", "修井日期"),
        ("move_hours", "搬迁(h)"),
        ("drilling_hours", "钻井(h)"),
        ("completion_hours", "完井(h)"),
        ("workover_hours", "修井(h)"),
        ("npt_hours", "NPT(h)"),
        ("remarks", "备注"),
    ]
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "生产报表"
    header_fill = PatternFill("solid", fgColor="0B4D7A")
    header_font = Font(color="FFFFFF", bold=True)
    for col_index, (_, label) in enumerate(columns, start=1):
        cell = worksheet.cell(row=1, column=col_index, value=label)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for row_index, row in enumerate(rows, start=2):
        for col_index, (key, _) in enumerate(columns, start=1):
            value = row.get(key)
            if key == "contract_project":
                value = row.get("contract_project") or row.get("project_name") or ""
            elif key.endswith("_hours") or key == "npt_hours":
                value = _safe_float(value)
            worksheet.cell(row=row_index, column=col_index, value=value if value not in (None, "") else "-")
    for col_index, (key, label) in enumerate(columns, start=1):
        width = max(len(label) + 4, 12)
        if key == "contract_project":
            width = 30
        elif key == "remarks":
            width = 14
        elif key == "wellbore":
            width = 16
        worksheet.column_dimensions[worksheet.cell(row=1, column=col_index).column_letter].width = width
    worksheet.freeze_panes = "A2"
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _npt_report_workbook_bytes(rows: list[dict[str, object]], show_rig: bool = False) -> bytes:
    columns: list[tuple[str, str]] = [
        ("wellbore", "井号"),
        *([("rig", "井队")] if show_rig else []),
        ("project_name", "项目"),
        ("reportDate", "NPT日期"),
        ("hours", "NPT(h)"),
        ("npt_keyword", "NPT描述关键词"),
        ("operation_details", "备注（NPT描述）"),
    ]
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "NPT统计"
    header_fill = PatternFill("solid", fgColor="0B4D7A")
    header_font = Font(color="FFFFFF", bold=True)
    for col_index, (_, label) in enumerate(columns, start=1):
        cell = worksheet.cell(row=1, column=col_index, value=label)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for row_index, row in enumerate(rows, start=2):
        for col_index, (key, _) in enumerate(columns, start=1):
            if key == "project_name":
                value = row.get("project_name") or row.get("contract_project") or ""
            elif key == "hours":
                value = _safe_float(row.get("hours"))
            elif key == "npt_keyword":
                value = row.get("op_sub") or row.get("op_code") or row.get("reason") or ""
            else:
                value = row.get(key)
            worksheet.cell(row=row_index, column=col_index, value=value if value not in (None, "") else "-")
    for col_index, (key, label) in enumerate(columns, start=1):
        width = max(len(label) + 4, 12)
        if key == "project_name":
            width = 26
        elif key == "operation_details":
            width = 64
        elif key == "wellbore":
            width = 16
        worksheet.column_dimensions[worksheet.cell(row=1, column=col_index).column_letter].width = width
    worksheet.freeze_panes = "A2"
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _safe_float(value: object) -> float:
    try:
        return round(float(value or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def _production_report_remark_key(project_id: str, rig: str, wellbore: str) -> str:
    return "|".join([str(project_id or "").strip(), _normalize_rig_name(str(rig or "").strip()), str(wellbore or "").strip()])


def _contract_project_label(row: dict[str, object]) -> str:
    contract = str(row.get("project_contract", "") or "").strip()
    project = str(row.get("project_name", "") or "").strip()
    if contract and project and contract != project:
        return f"{contract} / {project}"
    return contract or project or "-"


def _apply_event_dates(item: dict[str, object], event: str, report_date: str, report_type: str) -> None:
    if not report_date:
        return
    event_text = event.lower()
    if report_type == "drilling" and "rig move" in event_text:
        item["move_date"] = _earliest_date(str(item.get("move_date", "") or ""), report_date)
    if report_type == "drilling" and "drilling" in event_text:
        item["drilling_start_date"] = _earliest_date(str(item.get("drilling_start_date", "") or ""), report_date)
        item["drilling_finish_date"] = _latest_date(str(item.get("drilling_finish_date", "") or ""), report_date)
    if report_type == "completion":
        item["completion_date"] = _latest_date(str(item.get("completion_date", "") or ""), report_date)
    if report_type == "workover" and "workover" in event_text:
        item["workover_date"] = _earliest_date(str(item.get("workover_date", "") or ""), report_date)


def _apply_well_stat_dates(item: dict[str, object], event: str, report_date: str, report_type: str) -> None:
    if not report_date:
        return
    event_text = event.lower()
    if report_type == "drilling" and "rig move" in event_text:
        item["move_date"] = _earliest_date(str(item.get("move_date", "") or ""), report_date)
    if report_type == "drilling" and "drilling" in event_text:
        item["drilling_start_date"] = _earliest_date(str(item.get("drilling_start_date", "") or ""), report_date)
    if report_type == "completion":
        item["completion_date"] = _latest_date(str(item.get("completion_date", "") or ""), report_date)
    if report_type == "workover" and "workover" in event_text:
        item["workover_date"] = _earliest_date(str(item.get("workover_date", "") or ""), report_date)


def _earliest_date(current: str, candidate: str) -> str:
    if not current:
        return candidate
    return min(current, candidate)


def _latest_date(current: str, candidate: str) -> str:
    if not current:
        return candidate
    return max(current, candidate)


def _round_hour_fields(item: dict[str, object]) -> dict[str, object]:
    return {**item, **{key: round(float(item.get(key, 0.0) or 0.0), 2) for key in ("drilling_hours", "completion_hours", "workover_hours", "move_hours", "npt_hours")}}


def _npt_stats_payload(database_path: Path, params: dict[str, list[str]]) -> dict[str, object]:
    rows = _filtered_fact_rows(database_path, params)
    records = rows["records"]
    npt_rows = [row for row in rows["operations"] if row["op_type"] == "NPT"]
    category_filter = _param(params, "reason")
    if category_filter:
        npt_rows = [row for row in npt_rows if row["reason"] == category_filter]
    total_npt = sum(row["hours"] for row in npt_rows)
    rigs = sorted({row["rig"] for row in npt_rows if row["rig"]})
    wells = sorted({row["wellbore"] for row in npt_rows if row["wellbore"]})

    by_rig = _sum_by(npt_rows, "rig")
    by_well = _sum_by(npt_rows, "wellbore")
    by_reason = _sum_by(npt_rows, "reason")
    by_month = _sum_by(npt_rows, "month")

    return {
        "filters": {**_filter_options(records, database_path), "reasons": sorted({row["reason"] for row in rows["operations"] if row["op_type"] == "NPT"})},
        "kpis": {
            "rig_count": len(rigs),
            "well_count": len(wells),
            "event_count": len(npt_rows),
            "total_npt": round(total_npt, 2),
        },
        "by_rig": [{"label": key, "hours": round(value, 2)} for key, value in by_rig],
        "by_well": [{"label": key, "hours": round(value, 2)} for key, value in by_well[:10]],
        "by_reason": [{"label": key, "hours": round(value, 2), "share": round((value / total_npt * 100) if total_npt else 0, 1)} for key, value in by_reason],
        "monthly": [{"month": key, "hours": round(value, 2)} for key, value in by_month],
        "details": [{
            "record_id": row["record_id"],
            "report_type": row["report_type"],
            "rig": row["rig"],
            "wellbore": row["wellbore"],
            "project_id": row.get("project_id", ""),
            "project_name": row.get("project_name", ""),
            "project_contract": row.get("project_contract", ""),
            "contract_project": _contract_project_label(row),
            "reportDate": row["reportDate"],
            "hours": round(row["hours"], 2),
            "reason": row["reason"],
            "op_code": row["op_code"],
            "op_sub": row["op_sub"],
            "operation_details": row["operation_details"],
        } for row in _default_sort_npt_rows(npt_rows)],
        "scope_note": "基于已保存到 Excel 库的日报解析数据；分类按日报 OP CODE / OP SUB 汇总",
    }


def _filtered_fact_rows(database_path: Path, params: dict[str, list[str]]) -> dict[str, list[dict[str, object]]]:
    date_from = _param(params, "date_from")
    date_to = _param(params, "date_to")
    rig_filter = {_normalize_rig_name(value) for value in _param_values(params, "rig")}
    type_filter = _param(params, "report_type")
    well_filter = _param(params, "wellbore")
    project_filter = set(_param_values(params, "project"))
    project_mode = _truthy(_param(params, "project_mode")) or bool(project_filter)
    records = []
    operations = []
    for raw_record in list_records(database_path):
        record = {**raw_record, "rig": _normalize_rig_name(str(raw_record.get("rig", "") or ""))}
        report_date = record.get("reportDate", "")
        if date_from and report_date < date_from:
            continue
        if date_to and report_date > date_to:
            continue
        if rig_filter and record.get("rig") not in rig_filter:
            continue
        if type_filter and record.get("report_type") != type_filter:
            continue
        if well_filter and well_filter.lower() not in str(record.get("wellbore", "") or "").lower():
            continue
        project_matches = _project_assignments_for_record(record, project_filter)
        if project_filter and not project_matches:
            continue
        if project_mode and not project_matches:
            project_matches = [_unassigned_project_assignment()]
        matched_records = [{**record, **project} for project in project_matches] if project_matches else [record]
        try:
            payload = load_report_payload(database_path, str(record.get("record_id") or ""))
        except (KeyError, FileNotFoundError, ValueError):
            continue
        fields = payload.get("report_fields", {}) if isinstance(payload.get("report_fields", {}), dict) else {}
        event = str(fields.get("event", "") or record.get("event", "") or "")
        payload_report_date = str(fields.get("reportDate", "") or report_date)
        enriched_records = [{**matched_record, "event": event, "reportDate": payload_report_date} for matched_record in matched_records]
        records.extend(enriched_records)
        for matched_record in enriched_records:
            for row in payload.get("operations", []) if isinstance(payload.get("operations", []), list) else []:
                if not isinstance(row, dict):
                    continue
                hours = _safe_float(row.get("hours"))
                op_type = str(row.get("op_type", "") or "").strip().upper()
                fact = {
                    "record_id": matched_record.get("record_id", ""),
                    "report_type": matched_record.get("report_type", ""),
                    "reportDate": payload_report_date,
                    "month": payload_report_date[:7],
                    "wellbore": matched_record.get("wellbore", ""),
                    "rig": matched_record.get("rig", ""),
                    "project_id": matched_record.get("project_id", ""),
                    "project_name": matched_record.get("project_name", ""),
                    "project_contract": matched_record.get("project_contract", ""),
                    "validation_status": matched_record.get("validation_status", ""),
                    "event": event,
                    "hours": hours,
                    "op_type": op_type,
                    "op_code": str(row.get("op_code", "") or ""),
                    "op_sub": str(row.get("op_sub", "") or ""),
                    "operation_details": str(row.get("operation_details", "") or ""),
                }
                fact["reason"] = _operation_category(fact)
                operations.append(fact)
    return {"records": records, "operations": operations}


def _filter_options(records: list[dict[str, str]], database_path: Path = DATABASE_PATH) -> dict[str, object]:
    return {
        "rigs": _production_filter_rigs(records, database_path),
        "wells": sorted({record.get("wellbore", "") for record in records if record.get("wellbore")}),
        "report_types": [{"value": key, "label": REPORT_TYPE_LABELS[key]} for key in REPORT_TYPE_LABELS],
        "projects": _project_filter_options(),
    }


def _production_filter_rigs(records: list[dict[str, str]], database_path: Path = DATABASE_PATH) -> list[str]:
    rigs = {_normalize_rig_name(str(record.get("rig", "") or "")) for record in records if record.get("rig")}
    config = _load_project_team_config()
    for team in config.get("teams", []) if isinstance(config.get("teams"), list) else []:
        name = _normalize_rig_name(str(team.get("name", "") or ""))
        if name:
            rigs.add(name)
    if database_path.exists():
        for record in list_records(database_path):
            name = _normalize_rig_name(str(record.get("rig", "") or ""))
            if name:
                rigs.add(name)
    return sorted(rigs, key=lambda value: value.lower())


def _param_values(params: dict[str, list[str]], name: str) -> list[str]:
    values: list[str] = []
    for raw in params.get(name, []):
        values.extend(part.strip() for part in str(raw or "").split(","))
    return [value for value in values if value]


def _project_filter_options() -> list[dict[str, str]]:
    projects = _load_project_team_config().get("projects", [])
    options = []
    for project in projects if isinstance(projects, list) else []:
        if str(project.get("status", "active") or "active") != "active":
            continue
        project_id = str(project.get("id", "") or "").strip()
        label = str(project.get("project_name", "") or project.get("contract_no", "") or project_id).strip()
        if not project_id or not label:
            continue
        options.append({
            "value": project_id,
            "label": label,
            "contract_no": str(project.get("contract_no", "") or ""),
            "start_date": str(project.get("start_date", "") or ""),
            "end_date": str(project.get("end_date", "") or ""),
        })
    return options


def _project_assignments_for_record(record: dict[str, str], selected_projects: set[str] | None = None) -> list[dict[str, str]]:
    rig = _normalize_rig_name(str(record.get("rig", "") or "").strip())
    wellbore = str(record.get("wellbore", "") or "").strip()
    report_date = str(record.get("reportDate", "") or "").strip()
    if not rig:
        return []
    config = _load_project_team_config()
    matches: list[dict[str, str]] = []
    for project in config.get("projects", []) if isinstance(config.get("projects"), list) else []:
        project_id = str(project.get("id", "") or "").strip()
        if selected_projects and project_id not in selected_projects:
            continue
        if str(project.get("status", "active") or "active") != "active":
            continue
        if not _date_in_range(report_date, str(project.get("start_date", "") or ""), str(project.get("end_date", "") or "")):
            continue
        for rig_item in project.get("rigs", []) if isinstance(project.get("rigs"), list) else []:
            if not _rig_name_matches(config, str(rig_item.get("rig", "") or "").strip(), rig):
                continue
            if not _date_in_range(report_date, str(rig_item.get("start_date", "") or ""), str(rig_item.get("end_date", "") or "")):
                continue
            wells = {str(well or "").strip() for well in _list_value(rig_item.get("wells")) if str(well or "").strip()}
            if wells and wellbore not in wells:
                continue
            matches.append({
                "project_id": project_id,
                "project_name": str(project.get("project_name", "") or project.get("contract_no", "") or project_id),
                "project_contract": str(project.get("contract_no", "") or ""),
            })
            break
    return matches


def _unassigned_project_assignment() -> dict[str, str]:
    return {
        "project_id": UNASSIGNED_PROJECT_ID,
        "project_name": "未归属项目",
        "project_contract": "",
    }


def _rig_name_matches(config: dict[str, object], configured_name: str, report_name: str) -> bool:
    if configured_name == report_name:
        return True
    for team in config.get("teams", []) if isinstance(config.get("teams"), list) else []:
        if not _team_name_matches(team, configured_name):
            continue
        return _team_name_matches(team, report_name)
    return False


def _team_name_matches(team: object, value: str) -> bool:
    if not isinstance(team, dict):
        return False
    target = str(value or "").strip()
    if not target:
        return False
    names = {str(team.get("name", "") or "").strip(), *{str(alias or "").strip() for alias in _list_value(team.get("aliases"))}}
    return target in names


def _date_in_range(value: str, start: str, end: str) -> bool:
    if not start and not end:
        return True
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""):
        return False
    if start and value < start:
        return False
    if end and value > end:
        return False
    return True


def _completeness(records: list[dict[str, str]]) -> dict[str, object]:
    uploaded = {record.get("reportDate") for record in records if record.get("reportDate")}
    warnings = {record.get("reportDate") for record in records if record.get("reportDate") and record.get("validation_status") == "warning"}
    missing = _missing_dates(uploaded)
    expected = len(uploaded) + len(missing)
    percent = round(((len(uploaded) - len(warnings) * 0.35) / expected * 100) if expected else 0, 1)
    return {"percent": max(0, percent), "missing_days": len(missing), "warning_days": len(warnings)}


def _missing_dates(dates: set[str]) -> list[str]:
    clean = sorted(date for date in dates if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""))
    if len(clean) < 2:
        return []
    cursor = datetime.strptime(clean[0], "%Y-%m-%d").date()
    end = datetime.strptime(clean[-1], "%Y-%m-%d").date()
    existing = set(clean)
    missing = []
    while cursor <= end:
        value = cursor.isoformat()
        if value not in existing:
            missing.append(value)
        cursor = date.fromordinal(cursor.toordinal() + 1)
    return missing


def _sum_by(rows: list[dict[str, object]], key: str) -> list[tuple[str, float]]:
    totals: dict[str, float] = {}
    for row in rows:
        label = str(row.get(key) or "未识别")
        totals[label] = totals.get(label, 0.0) + float(row.get("hours") or 0.0)
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)


def _operation_category(row: dict[str, object]) -> str:
    op_code = str(row.get("op_code", "") or "").strip()
    op_sub = str(row.get("op_sub", "") or "").strip()
    if op_code and op_sub:
        return f"{op_code} / {op_sub}"
    if op_code:
        return op_code
    if op_sub:
        return op_sub
    return "未填写 OP CODE / OP SUB"


def _safe_float(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def _truthy(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _has_value(value: object) -> bool:
    return bool(str(value or "").strip())


def _operation_clock_hours_by_row(rows: list[object]) -> dict[int, float]:
    durations: dict[int, float] = {}
    previous_end: int | None = None
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        start = _clock_minutes(row.get("from"))
        end = _clock_minutes(row.get("to"))
        if start is None or end is None:
            continue
        start_abs = start
        if previous_end is not None:
            while start_abs < previous_end:
                start_abs += 24 * 60
        day_offset = start_abs // (24 * 60)
        end_abs = end + day_offset * 24 * 60
        while end_abs < start_abs:
            end_abs += 24 * 60
        if end_abs == start_abs and _safe_float(row.get("hours")) >= 23.9:
            end_abs += 24 * 60
        durations[index] = (end_abs - start_abs) / 60
        previous_end = end_abs
    return durations


def _clock_minutes(value: object) -> int | None:
    text = str(value or "").strip()
    match = re.fullmatch(r"(\d{1,2})[:：](\d{2})", text)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour == 24 and minute == 0:
        return 24 * 60
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return hour * 60 + minute


def _param(params: dict[str, list[str]], key: str) -> str:
    return str((params.get(key) or [""])[0] or "").strip()


def _normalize_payload_values(payload: dict[str, object]) -> list[str]:
    warnings: list[str] = []
    fields = payload.get("report_fields", {})
    if isinstance(fields, dict):
        for key, value in list(fields.items()):
            if key in DATE_FIELDS:
                fields[key], warning = _normalize_date_value(value, key)
            elif key in TIME_FIELDS:
                fields[key], warning = _normalize_time_value(value, key)
            elif key in NUMERIC_REPORT_FIELDS:
                fields[key], warning = _normalize_number_value(value, key)
            else:
                warning = ""
            if warning:
                warnings.append(warning)

    for section, rows in payload.items():
        if section in {"metadata", "report_fields"} or not isinstance(rows, list):
            continue
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            for key, value in list(row.items()):
                label = f"{section} row {index} {key}"
                if key in DATE_FIELDS:
                    row[key], warning = _normalize_date_value(value, label)
                elif key in TIME_FIELDS:
                    row[key], warning = _normalize_time_value(value, label)
                elif key in NUMERIC_TABLE_FIELDS:
                    row[key], warning = _normalize_number_value(value, label)
                else:
                    warning = ""
                if warning:
                    warnings.append(warning)
    return warnings


def _normalize_date_value(value: object, label: str) -> tuple[str, str]:
    text = str(value or "").strip()
    if not text:
        return "", ""
    formats = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%m-%d-%Y")
    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt).date()
            if parsed > date.today():
                return parsed.isoformat(), f"{label} is in the future"
            return parsed.isoformat(), ""
        except ValueError:
            continue
    return text, f"{label} date invalid"


def _normalize_time_value(value: object, label: str) -> tuple[str, str]:
    text = str(value or "").strip()
    if not text:
        return "", ""
    match = re.fullmatch(r"(\d{1,2})[:：](\d{2})", text)
    if not match:
        return text, f"{label} time invalid"
    hour, minute = int(match.group(1)), int(match.group(2))
    if hour == 24 and minute == 0:
        return "24:00", ""
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return text, f"{label} time invalid"
    return f"{hour:02d}:{minute:02d}", ""


def _normalize_number_value(value: object, label: str) -> tuple[str, str]:
    text = str(value or "").strip()
    if not text:
        return "", ""
    cleaned = text.replace(",", "")
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", cleaned):
        return _trim_number(cleaned), ""
    match = re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", text)
    if not match:
        return text, f"{label} number invalid"
    leftovers = f"{text[:match.start()]} {text[match.end():]}".strip().lower()
    leftovers = re.sub(r"[\s,./()@:-]+", " ", leftovers).strip()
    allowed_units = {"ft", "feet", "in", "inch", "ppg", "psi", "gpm", "usd", "h", "hr", "hrs", "deg", "bbl", "spf", "lb", "lbs"}
    if not leftovers or all(part in allowed_units for part in leftovers.split()):
        return _trim_number(match.group(0).replace(",", "")), ""
    return _trim_number(match.group(0).replace(",", "")), f"{label} number corrected"


def _trim_number(value: str) -> str:
    if "." not in value:
        return value
    return value.rstrip("0").rstrip(".") or "0"


if __name__ == "__main__":
    main()
