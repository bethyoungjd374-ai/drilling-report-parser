"""Backend API smoke test for drilling-report-parser after UI refactor.
Tests login flow, key API endpoints, static routes via FastAPI proxy.
"""
import os
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://visual-enhance-120.preview.emergentagent.com").rstrip("/")

USER = "admin"
PASSWORDS = ["Admin@2026", "admin123"]


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    last = None
    for pw in PASSWORDS:
        r = s.post(f"{BASE_URL}/api/admin/login",
                   json={"username": USER, "password": pw}, timeout=15)
        last = r
        if r.status_code == 200:
            try:
                data = r.json()
            except Exception:
                data = {}
            # Some auth flows require change on first login
            if data.get("must_change_password"):
                # try to change to Admin@2026
                s.post(f"{BASE_URL}/api/admin/change-password",
                       json={"username": USER, "old_password": pw,
                             "new_password": "Admin@2026"}, timeout=15)
            return s
    pytest.fail(f"Login failed with all passwords, last status={last.status_code} body={last.text[:200]}")


# --- Static / page routes ---
@pytest.mark.parametrize("path", ["/login/", "/web_form/", "/admin/",
                                   "/web_form/styles.css", "/web_form/app.js"])
def test_static_routes(path):
    r = requests.get(f"{BASE_URL}{path}", timeout=15)
    assert r.status_code == 200, f"{path} -> {r.status_code}"


def test_styles_css_has_new_tokens():
    r = requests.get(f"{BASE_URL}/web_form/styles.css", timeout=15)
    assert r.status_code == 200
    txt = r.text
    # Verify the new redesign tokens exist
    assert "--color" in txt or "--bg" in txt or ":root" in txt, "CSS doesn't look like new tokenized version"


# --- Auth APIs ---
def test_login_wrong_password():
    r = requests.post(f"{BASE_URL}/api/admin/login",
                      json={"username": USER, "password": "wrong_xxx"}, timeout=15)
    assert r.status_code in (401, 400, 403), f"got {r.status_code}"


def test_login_ok(session):
    # session fixture already logged in
    assert session is not None


# --- Business APIs ---
def test_list_records(session):
    r = session.get(f"{BASE_URL}/api/records", timeout=15)
    assert r.status_code == 200, r.text[:200]


def test_download_database(session):
    r = session.get(f"{BASE_URL}/api/download-database", timeout=30, stream=True)
    assert r.status_code == 200, f"got {r.status_code}"
    ctype = r.headers.get("Content-Type", "")
    # excel or octet-stream
    assert "sheet" in ctype or "excel" in ctype or "octet-stream" in ctype or "zip" in ctype, ctype


def test_production_summary(session):
    r = session.get(f"{BASE_URL}/api/production-summary", timeout=20)
    assert r.status_code == 200, r.text[:200]


def test_npt_stats(session):
    r = session.get(f"{BASE_URL}/api/npt-stats", timeout=20)
    assert r.status_code == 200, r.text[:200]


def test_save_report(session):
    # try minimal payload; endpoint should accept
    payload = {"report_type": "drilling", "well_name": "TEST_WELL_PCNC-040", "report_date": "2026-01-08", "data": {}}
    r = session.post(f"{BASE_URL}/api/save-report", json=payload, timeout=20)
    assert r.status_code in (200, 201), f"got {r.status_code}: {r.text[:200]}"


def test_admin_users(session):
    r = session.get(f"{BASE_URL}/api/admin/users", timeout=15)
    assert r.status_code == 200, r.text[:200]
    data = r.json()
    assert isinstance(data, (list, dict))
