"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Tutor GPT API"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"


@pytest.mark.asyncio
async def test_start_session(client: AsyncClient):
    """Test session start endpoint."""
    response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "test@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "message" in data
    assert data["message"] == "Session created. Connect via WebSocket to begin."


@pytest.mark.asyncio
async def test_get_metrics(client: AsyncClient):
    """Test metrics endpoint."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "counters" in data["metrics"]
    assert "histograms" in data["metrics"]
    assert "gauges" in data["metrics"]

