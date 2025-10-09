"""Integration tests for session creation and management."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_start_session_with_email(client: AsyncClient):
    """Test starting a session with a user email."""
    response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "test@example.com"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "session_id" in data
    assert "message" in data
    assert data["message"] == "Session created. Connect via WebSocket to begin."
    
    # Verify session_id is a valid UUID
    import uuid
    uuid.UUID(data["session_id"])


@pytest.mark.asyncio
async def test_start_session_without_email(client: AsyncClient):
    """Test starting a session without a user email (creates temp user)."""
    response = await client.post(
        "/api/v1/sessions/start",
        json={},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "session_id" in data
    assert "message" in data


@pytest.mark.asyncio
async def test_start_session_creates_user(client: AsyncClient):
    """Test that starting a session creates a user if they don't exist."""
    email = "newuser@example.com"
    
    response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": email},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify we can get the session
    session_response = await client.get(f"/api/v1/sessions/{data['session_id']}")
    assert session_response.status_code == 200


@pytest.mark.asyncio
async def test_get_session_from_cache(client: AsyncClient):
    """Test retrieving session from Redis cache."""
    # Create a session
    response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "cache_test@example.com"},
    )
    
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Get session (should be from cache)
    session_response = await client.get(f"/api/v1/sessions/{session_id}")
    assert session_response.status_code == 200
    
    data = session_response.json()
    assert data["session_id"] == session_id
    assert "data" in data
    assert data["source"] == "cache"


@pytest.mark.asyncio
async def test_get_nonexistent_session(client: AsyncClient):
    """Test retrieving a session that doesn't exist."""
    fake_session_id = "00000000-0000-0000-0000-000000000000"
    
    response = await client.get(f"/api/v1/sessions/{fake_session_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_session_creation_metrics(client: AsyncClient):
    """Test that session creation is tracked in metrics."""
    # Create a session
    response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "metrics_test@example.com"},
    )
    
    assert response.status_code == 200
    
    # Check metrics endpoint
    metrics_response = await client.get("/metrics/summary")
    assert metrics_response.status_code == 200
    
    metrics_data = metrics_response.json()
    assert "capacity" in metrics_data
    assert "sessions_active" in metrics_data["capacity"]


@pytest.mark.asyncio
async def test_session_creation_logging(client: AsyncClient):
    """Test that session creation is properly logged."""
    # This test would require access to logs, which is complex in integration tests
    # For now, just verify the endpoint works without errors
    response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "logging_test@example.com"},
    )
    
    assert response.status_code == 200
    assert "session_id" in response.json()
