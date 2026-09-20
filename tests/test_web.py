# tests/test_web.py
import os
import base64
import pytest
from fastapi.testclient import TestClient
from utils.database import Database
from web.app import create_app


@pytest.fixture
def test_db():
    """Create test database."""
    db_path = "tests/test_web.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = Database(db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "web": {
            "host": "0.0.0.0",
            "port": 8000,
            "username": "admin",
            "password": "secret123"
        }
    }


@pytest.fixture
def client(test_db, test_config):
    """Create test client."""
    app = create_app(test_db, test_config)
    return TestClient(app)


def _auth_header(username="admin", password="secret123"):
    """Create Basic Auth header."""
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


# --- Health check (no auth required) ---

def test_health_endpoint():
    """Health endpoint returns 200 without auth."""
    config = {"web": {"username": "admin", "password": "pw"}}
    db = Database("tests/test_health.db")
    try:
        app = create_app(db, config)
        c = TestClient(app)
        resp = c.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "healthy"}
    finally:
        if os.path.exists("tests/test_health.db"):
            os.remove("tests/test_health.db")


# --- Auth tests ---

def test_auth_rejects_wrong_credentials(client):
    """Wrong credentials return 401."""
    bad = base64.b64encode(b"wrong:creds").decode()
    resp = client.get("/", headers={"Authorization": f"Basic {bad}"})
    assert resp.status_code == 401


def test_auth_accepts_correct_credentials(client):
    """Correct credentials return 200 for index page."""
    resp = client.get("/", headers=_auth_header())
    assert resp.status_code == 200


def test_auth_api_endpoints_require_auth(client):
    """API endpoints require authentication."""
    endpoints = [
        ("GET", "/api/channels"),
        ("POST", "/api/channels"),
        ("GET", "/api/filters"),
        ("POST", "/api/filters"),
        ("GET", "/api/vacancies"),
        ("GET", "/api/stats"),
    ]
    for method, url in endpoints:
        if method == "GET":
            resp = client.get(url)
        else:
            resp = client.post(url, json={})
        assert resp.status_code == 401, f"{method} {url} should require auth"


# --- Channel API ---

def test_get_channels_empty(client):
    """GET /api/channels returns empty list initially."""
    resp = client.get("/api/channels", headers=_auth_header())
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_channel(client):
    """POST /api/channels creates a channel."""
    resp = client.post("/api/channels", json={"channel_name": "@test_ch"}, headers=_auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert data["channel_name"] == "@test_ch"
    assert "id" in data


def test_add_channel_missing_name(client):
    """POST /api/channels without channel_name returns 400."""
    resp = client.post("/api/channels", json={}, headers=_auth_header())
    assert resp.status_code == 400


def test_delete_channel(client):
    """DELETE /api/channels/{id} removes a channel."""
    # Create first
    c = client.post("/api/channels", json={"channel_name": "@del_me"}, headers=_auth_header())
    ch_id = c.json()["id"]

    resp = client.delete(f"/api/channels/{ch_id}", headers=_auth_header())
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True


def test_delete_channel_not_found(client):
    """DELETE /api/channels/99999 returns 404."""
    resp = client.delete("/api/channels/99999", headers=_auth_header())
    assert resp.status_code == 404


# --- Filter API ---

def test_get_filters_empty(client):
    """GET /api/filters returns empty list initially."""
    resp = client.get("/api/filters", headers=_auth_header())
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_filter(client):
    """POST /api/filters creates a filter."""
    payload = {
        "name": "Junior",
        "phrases": ["junior dev", "начинающий"],
        "exclude": ["senior"],
        "weight": 8
    }
    resp = client.post("/api/filters", json=payload, headers=_auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Junior"
    assert "id" in data


def test_add_filter_missing_name(client):
    """POST /api/filters without name returns 400."""
    resp = client.post("/api/filters", json={"phrases": ["test"]}, headers=_auth_header())
    assert resp.status_code == 400


def test_delete_filter(client):
    """DELETE /api/filters/{id} removes a filter."""
    c = client.post("/api/filters", json={"name": "Del", "phrases": ["x"]}, headers=_auth_header())
    f_id = c.json()["id"]
    resp = client.delete(f"/api/filters/{f_id}", headers=_auth_header())
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True


def test_delete_filter_not_found(client):
    """DELETE /api/filters/99999 returns 404."""
    resp = client.delete("/api/filters/99999", headers=_auth_header())
    assert resp.status_code == 404


# --- Vacancy API ---

def test_get_vacancies_empty(client):
    """GET /api/vacancies returns empty list initially."""
    resp = client.get("/api/vacancies", headers=_auth_header())
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_vacancies_after_add(test_db, test_config):
    """GET /api/vacancies returns vacancies created via DB."""
    test_db.add_vacancy(
        channel_name="@ch", message_id=1, category="Cat",
        matched_phrase="phrase", weight=5, text="text", link="http://link"
    )
    app = create_app(test_db, test_config)
    c = TestClient(app)
    resp = c.get("/api/vacancies", headers=_auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["channel_name"] == "@ch"


# --- Stats API ---

def test_get_stats(client):
    """GET /api/stats returns statistics dict."""
    resp = client.get("/api/stats", headers=_auth_header())
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_vacancies" in stats
    assert "vacancies_today" in stats
    assert "total_channels" in stats
    assert "total_filters" in stats
    assert "errors_today" in stats


# --- Index page (HTML) ---

def test_index_page(client):
    """GET / returns HTML page with auth."""
    resp = client.get("/", headers=_auth_header())
    assert resp.status_code == 200
    assert "Telegram Vacancy Bot" in resp.text


# --- create_app unit test ---

def test_create_app_returns_fastapi():
    """create_app returns a FastAPI instance."""
    from fastapi import FastAPI
    config = {"web": {"username": "a", "password": "b"}}
    db = Database("tests/test_create_app.db")
    try:
        app = create_app(db, config)
        assert isinstance(app, FastAPI)
        assert app.title == "Telegram Vacancy Bot"
    finally:
        if os.path.exists("tests/test_create_app.db"):
            os.remove("tests/test_create_app.db")
