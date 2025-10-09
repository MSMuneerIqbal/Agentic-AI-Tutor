"""Integration tests for WebSocket endpoints."""

import asyncio
import json

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_websocket_greeting_e2e(client: AsyncClient):
    """
    Test WebSocket greeting E2E (FIRST RUNNER).

    Flow:
    1. Create session via POST /sessions/start
    2. Connect to WS /ws/sessions/{session_id}
    3. Receive greeting within 5s
    4. Verify greeting schema {type, agent, text, timestamp}
    """
    # Step 1: Create session
    response = await client.post("/api/v1/sessions/start", json={})
    assert response.status_code == 200
    session_data = response.json()
    session_id = session_data["session_id"]

    # Step 2 & 3: Connect to WebSocket and receive greeting
    with TestClient(app) as test_client:
        with test_client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # FIRST RUNNER: Receive greeting
            data = websocket.receive_json()

            # Step 4: Verify schema
            assert "type" in data
            assert data["type"] == "agent_message"
            assert "agent" in data
            assert data["agent"] == "orchestrator"
            assert "text" in data
            assert len(data["text"]) > 0
            assert "Hello" in data["text"] or "welcome" in data["text"].lower()
            assert "timestamp" in data
            assert "session_id" in data
            assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_websocket_user_message_echo(client: AsyncClient):
    """
    Test WebSocket SECOND RUNNER (user input loop).

    Flow:
    1. Connect to WS
    2. Receive greeting
    3. Send user message
    4. Receive response
    """
    # Create session
    response = await client.post("/api/v1/sessions/start", json={})
    session_id = response.json()["session_id"]

    with TestClient(app) as test_client:
        with test_client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Receive greeting
            greeting = websocket.receive_json()
            assert greeting["type"] == "agent_message"

            # Send user message
            websocket.send_json({"message": "I'm ready to start"})

            # Receive response
            response = websocket.receive_json()
            assert response["type"] == "agent_message"
            assert "text" in response
            assert len(response["text"]) > 0


@pytest.mark.asyncio
async def test_websocket_greeting_timeout_fallback():
    """
    Test WebSocket greeting with simulated Gemini timeout.

    Should return safe fallback greeting.
    """
    # This test would require mocking Gemini API timeout
    # For now, we just verify the greeting always arrives within 5s
    with TestClient(app) as test_client:
        # Create session
        response = test_client.post("/api/v1/sessions/start", json={})
        session_id = response.json()["session_id"]

        # Connect and verify greeting arrives quickly
        with test_client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Set a timeout
            import time

            start = time.time()
            data = websocket.receive_json()
            elapsed = time.time() - start

            # Verify greeting arrived within 5s
            assert elapsed < 5.0
            assert "text" in data


@pytest.mark.asyncio
async def test_websocket_connection_close():
    """Test WebSocket handles graceful disconnection."""
    with TestClient(app) as test_client:
        response = test_client.post("/api/v1/sessions/start", json={})
        session_id = response.json()["session_id"]

        with test_client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Receive greeting
            greeting = websocket.receive_json()
            assert greeting is not None

            # Close connection
            websocket.close()

        # Connection should close without errors
        # (WebSocketDisconnect is handled internally)

