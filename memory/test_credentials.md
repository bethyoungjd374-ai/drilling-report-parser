# Test Credentials

## Web App (login page: /login/)

- **Username**: `admin`
- **Password**: `Admin@2026`
  - The system's factory default password is `admin123`; on first login the app
    forces a change. The password above was set during setup on 2026-01-08 after
    pulling the latest upstream code (commit `4236bb1` — "完成两个主要日报").
  - If the backend is restarted with a fresh users file (e.g. `outputs/users.json`
    deleted), the system re-seeds `admin/admin123` and again prompts for change.
- **Role**: 管理员 (admin)

## URLs
- Frontend (public preview): https://d3c13dd8-5c5b-4f51-8324-6f4b01938f03.preview.emergentagent.com
- Login page: `/login/`
- Front workspace: `/web_form/`
- Admin console: `/admin/`

## Notes
- Sessions are cookie-based and stored in-memory inside the form_server process, so
  a supervisor restart of the backend invalidates all sessions.
- MySQL fallback (`drilling_report_parser/mysql_database.py`) is available but the
  system runs in Excel-only mode by default when no `DB_*` env vars are set.
