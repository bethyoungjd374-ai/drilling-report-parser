from __future__ import annotations

import argparse
import cgi
import hashlib
import hmac
import json
import mimetypes
import re
import secrets
import shutil
import uuid
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .completion_pdf_parser import parse_completion_pdf_daily_report
from .excel_database import initialize_database, list_records, load_report_payload, save_report_payload
from .pdf_report_parser import parse_pdf_daily_report
from .workover_pdf_parser import parse_workover_pdf_daily_report


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web_form"
DATABASE_PATH = ROOT / "outputs" / "report_database.xlsx"
SOURCE_PDF_DIR = ROOT / "outputs" / "source_pdfs"
CONFIG_PATH = ROOT / "outputs" / "system_config.json"
USERS_PATH = ROOT / "outputs" / "users.json"
ROLES_PATH = ROOT / "outputs" / "roles.json"
AUDIT_LOG_PATH = ROOT / "outputs" / "audit_logs.jsonl"
BACKUP_DIR = ROOT / "outputs" / "backups"
SESSIONS: dict[str, dict[str, object]] = {}


class FormHandler(BaseHTTPRequestHandler):
    server_version = "DrillingReportForm/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", ""}:
            self.send_response(302)
            self.send_header("Location", "/login/")
            self.end_headers()
            return
        if parsed.path == "/login":
            self.send_response(302)
            self.send_header("Location", "/login/")
            self.end_headers()
            return
        if parsed.path == "/web_form":
            self.send_response(302)
            self.send_header("Location", "/web_form/")
            self.end_headers()
            return
        if parsed.path == "/admin":
            self.send_response(302)
            self.send_header("Location", "/admin/")
            self.end_headers()
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
        if parsed.path == "/api/npt-stats":
            if not self._require_permission("view"):
                return
            self._npt_stats(parsed.query)
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
            self._import_pdf()
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
        self.send_response(302)
        self.send_header("Location", f"/login/?next={next_path}")
        self.end_headers()

    def _import_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            pdf_bytes = upload.file.read()
            payload = parse_pdf_daily_report(pdf_bytes)
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "drilling")
            self._store_source_pdf(payload, pdf_bytes)
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_completion_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            pdf_bytes = upload.file.read()
            payload = parse_completion_pdf_daily_report(pdf_bytes)
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "completion")
            self._store_source_pdf(payload, pdf_bytes)
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_workover_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            pdf_bytes = upload.file.read()
            payload = parse_workover_pdf_daily_report(pdf_bytes)
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._store_payload(payload, "workover")
            self._store_source_pdf(payload, pdf_bytes)
            self._send_json(payload)
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

    def _list_records(self, query: str) -> None:
        params = parse_qs(query)
        report_type = (params.get("report_type") or [""])[0]
        records = list_records(DATABASE_PATH)
        if report_type:
            records = [record for record in records if record.get("report_type") == report_type]
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
        }
        for record in matched:
            record_id = str(record.get("record_id") or "")
            if not record_id:
                continue
            try:
                payload = load_report_payload(DATABASE_PATH, record_id)
            except KeyError:
                continue
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

    def _npt_stats(self, query: str) -> None:
        self._send_json(_npt_stats_payload(DATABASE_PATH, parse_qs(query)))

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
        report_type = _canonical_report_type(report_type)
        metadata = payload.setdefault("metadata", {})
        warnings = list(dict.fromkeys(_normalize_payload_values(payload) + _validation_warnings(payload, report_type)))
        if isinstance(metadata, dict):
            metadata.setdefault("status", "parsed")
            metadata["report_type"] = report_type
            metadata["validation_status"] = "warning" if warnings else "ok"
            metadata["validation_warnings"] = "; ".join(warnings)
        result = save_report_payload(
            DATABASE_PATH,
            payload,
            report_type,
            source_file=str(metadata.get("source_file", "")) if isinstance(metadata, dict) else "",
        )
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

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def _serve_static(self) -> None:
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

        self._serve_static_file(target)

    def _serve_static_file(self, target: Path) -> None:

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
    data = {key: user.get(key, "") for key in ("id", "username", "display_name", "email", "role", "status", "created_at", "last_login")}
    data["must_change_password"] = bool(user.get("must_change_password"))
    return data


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
    report_type = _canonical_report_type(report_type)
    fields = payload.get("report_fields", {})
    if not isinstance(fields, dict):
        return ["report_fields missing"]
    required_by_type = {
        "drilling": ["event", "reportDate", "reportNo", "wellbore", "rig", "todayMd", "progress", "currentOps", "summary24h", "forecast24h", "mudType", "mudDensity"],
        "completion": ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"],
        "workover": ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"],
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
    if report_type == "drilling":
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
}


def _canonical_report_type(report_type: str) -> str:
    return {"move": "drilling"}.get((report_type or "").strip().lower(), (report_type or "").strip().lower())


def _production_summary_payload(database_path: Path, params: dict[str, list[str]]) -> dict[str, object]:
    rows = _filtered_fact_rows(database_path, params)
    records = rows["records"]
    operations = rows["operations"]
    unique_rigs = sorted({record["rig"] for record in records if record["rig"]})
    unique_wells = sorted({record["wellbore"] for record in records if record["wellbore"]})
    total_hours = sum(row["hours"] for row in operations)
    npt_hours = sum(row["hours"] for row in operations if row["op_type"] == "NPT")
    completeness = _completeness(records)

    by_rig: dict[str, dict[str, float]] = {}
    by_type = {key: 0.0 for key in REPORT_TYPE_LABELS}
    monthly: dict[str, dict[str, float]] = {}
    detail: dict[tuple[str, str, str], dict[str, object]] = {}

    for row in operations:
        rig = row["rig"] or "未识别井队"
        report_type = row["report_type"]
        type_label = REPORT_TYPE_LABELS.get(report_type, report_type)
        by_rig.setdefault(rig, {key: 0.0 for key in REPORT_TYPE_LABELS})
        by_rig[rig][report_type] = by_rig[rig].get(report_type, 0.0) + row["hours"]
        if report_type in by_type:
            by_type[report_type] += row["hours"]
        month = row["reportDate"][:7] or "未识别"
        monthly.setdefault(month, {key: 0.0 for key in REPORT_TYPE_LABELS})
        monthly[month][report_type] = monthly[month].get(report_type, 0.0) + row["hours"]
        key = (rig, row["wellbore"], report_type)
        item = detail.setdefault(key, {
            "rig": rig,
            "wellbore": row["wellbore"],
            "report_type": report_type,
            "report_type_label": type_label,
            "start_date": row["reportDate"],
            "end_date": row["reportDate"],
            "drilling_hours": 0.0,
            "completion_hours": 0.0,
            "workover_hours": 0.0,
            "npt_hours": 0.0,
            "record_id": row["record_id"],
            "status": "",
        })
        item["start_date"] = min(str(item["start_date"] or row["reportDate"]), row["reportDate"])
        item["end_date"] = max(str(item["end_date"] or row["reportDate"]), row["reportDate"])
        item[f"{report_type}_hours"] = float(item.get(f"{report_type}_hours", 0.0)) + row["hours"]
        if row["op_type"] == "NPT":
            item["npt_hours"] = float(item["npt_hours"]) + row["hours"]

    record_index = {(record["rig"], record["wellbore"], record["report_type"]): record for record in records}
    for key, item in detail.items():
        record = record_index.get(key, {})
        item["status"] = "有告警" if record.get("validation_status") == "warning" else "正常"

    return {
        "filters": _filter_options(records),
        "kpis": {
            "rig_count": len(unique_rigs),
            "well_count": len(unique_wells),
            "total_hours": round(total_hours, 2),
            "npt_hours": round(npt_hours, 2),
            "completeness": completeness,
        },
        "by_rig": [{"rig": rig, **{key: round(value, 2) for key, value in values.items()}} for rig, values in sorted(by_rig.items())],
        "by_type": [{"report_type": key, "label": REPORT_TYPE_LABELS[key], "hours": round(value, 2)} for key, value in by_type.items()],
        "monthly": [{"month": month, **{key: round(value, 2) for key, value in values.items()}} for month, values in sorted(monthly.items())],
        "details": [{**item, **{k: round(float(item.get(k, 0.0)), 2) for k in ("drilling_hours", "completion_hours", "workover_hours", "npt_hours")}} for item in detail.values()],
        "scope_note": "基于已保存到 Excel 库的日报解析数据",
    }


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
        "filters": {**_filter_options(records), "reasons": sorted({row["reason"] for row in rows["operations"] if row["op_type"] == "NPT"})},
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
            "reportDate": row["reportDate"],
            "hours": round(row["hours"], 2),
            "reason": row["reason"],
            "op_code": row["op_code"],
            "op_sub": row["op_sub"],
            "operation_details": row["operation_details"],
        } for row in npt_rows],
        "scope_note": "基于已保存到 Excel 库的日报解析数据；分类按日报 OP CODE / OP SUB 汇总",
    }


def _filtered_fact_rows(database_path: Path, params: dict[str, list[str]]) -> dict[str, list[dict[str, object]]]:
    date_from = _param(params, "date_from")
    date_to = _param(params, "date_to")
    rig_filter = _param(params, "rig")
    type_filter = _param(params, "report_type")
    well_filter = _param(params, "wellbore")
    records = []
    operations = []
    for record in list_records(database_path):
        report_date = record.get("reportDate", "")
        if date_from and report_date < date_from:
            continue
        if date_to and report_date > date_to:
            continue
        if rig_filter and record.get("rig") != rig_filter:
            continue
        if type_filter and record.get("report_type") != type_filter:
            continue
        if well_filter and record.get("wellbore") != well_filter:
            continue
        records.append(record)
        try:
            payload = load_report_payload(database_path, str(record.get("record_id") or ""))
        except (KeyError, FileNotFoundError, ValueError):
            continue
        for row in payload.get("operations", []) if isinstance(payload.get("operations", []), list) else []:
            if not isinstance(row, dict):
                continue
            hours = _safe_float(row.get("hours"))
            op_type = str(row.get("op_type", "") or "").strip().upper()
            fact = {
                "record_id": record.get("record_id", ""),
                "report_type": record.get("report_type", ""),
                "reportDate": report_date,
                "month": report_date[:7],
                "wellbore": record.get("wellbore", ""),
                "rig": record.get("rig", ""),
                "validation_status": record.get("validation_status", ""),
                "hours": hours,
                "op_type": op_type,
                "op_code": str(row.get("op_code", "") or ""),
                "op_sub": str(row.get("op_sub", "") or ""),
                "operation_details": str(row.get("operation_details", "") or ""),
            }
            fact["reason"] = _operation_category(fact)
            operations.append(fact)
    return {"records": records, "operations": operations}


def _filter_options(records: list[dict[str, str]]) -> dict[str, object]:
    return {
        "rigs": sorted({record.get("rig", "") for record in records if record.get("rig")}),
        "wells": sorted({record.get("wellbore", "") for record in records if record.get("wellbore")}),
        "report_types": [{"value": key, "label": REPORT_TYPE_LABELS[key]} for key in REPORT_TYPE_LABELS],
    }


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
