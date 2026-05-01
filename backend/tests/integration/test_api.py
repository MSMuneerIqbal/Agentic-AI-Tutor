"""Integration tests for core API endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_check():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Tutor GPT API"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"


def test_metrics_endpoint():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "metrics" in data
    assert "counters" in data["metrics"]
    assert "histograms" in data["metrics"]
    assert "gauges" in data["metrics"]
