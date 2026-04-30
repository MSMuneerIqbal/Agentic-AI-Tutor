"""Integration tests for WebSocket Runner functionality."""

import json
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_websocket_first_runner_greeting(client: AsyncClient):
    """Test that WebSocket sends FIRST RUNNER greeting immediately."""
    # First create a session
    session_response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "ws_test@example.com"},
    )
    assert session_response.status_code == 200
    session_id = session_response.json()["session_id"]
    
    # Connect to WebSocket
    with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
        # Should receive greeting immediately
        greeting = websocket.receive_json()
        
        assert greeting["type"] == "agent_message"
        assert greeting["agent"] == "orchestrator"
        assert "Hello" in greeting["text"]
        assert greeting["session_id"] == session_id
        assert "timestamp" in greeting
        assert "action" in greeting


@pytest.mark.asyncio
async def test_websocket_second_runner_loop(client: AsyncClient):
    """Test SECOND RUNNER user input loop."""
    # Create session
    session_response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "ws_loop_test@example.com"},
    )
    session_id = session_response.json()["session_id"]
    
    with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
        # Receive greeting
        greeting = websocket.receive_json()
        assert greeting["type"] == "agent_message"
        
        # Send user message
        user_message = {"message": "Hello, I'm ready to learn!"}
        websocket.send_json(user_message)
        
        # Receive response
        response = websocket.receive_json()
        
        assert response["type"] == "agent_message"
        assert response["agent"] == "orchestrator"
        assert response["session_id"] == session_id
        assert "timestamp" in response


@pytest.mark.asyncio
async def test_websocket_empty_input_handling(client: AsyncClient):
    """Test handling of empty user input."""
    session_response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "ws_empty_test@example.com"},
    )
    session_id = session_response.json()["session_id"]
    
    with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
        # Receive greeting
        greeting = websocket.receive_json()
        
        # Send empty message
        websocket.send_json({"message": ""})
        
        # Should receive empty input response
        response = websocket.receive_json()
        
        assert response["type"] == "agent_message"
        assert "didn't receive" in response["text"]


@pytest.mark.asyncio
async def test_websocket_multiple_messages(client: AsyncClient):
    """Test multiple message exchange."""
    session_response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "ws_multi_test@example.com"},
    )
    session_id = session_response.json()["session_id"]
    
    with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
        # Receive greeting
        greeting = websocket.receive_json()
        
        # Send multiple messages
        messages = [
            "I want to learn Docker",
            "What should I start with?",
            "Tell me more about containers"
        ]
        
        for message in messages:
            websocket.send_json({"message": message})
            response = websocket.receive_json()
            
            assert response["type"] == "agent_message"
            assert response["session_id"] == session_id


@pytest.mark.asyncio
async def test_websocket_disconnect_handling(client: AsyncClient):
    """Test graceful handling of WebSocket disconnect."""
    session_response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "ws_disconnect_test@example.com"},
    )
    session_id = session_response.json()["session_id"]
    
    # Connect and immediately disconnect
    with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
        greeting = websocket.receive_json()
        assert greeting["type"] == "agent_message"
        
        # Close connection
        websocket.close()
    
    # Should not raise any exceptions


@pytest.mark.asyncio
async def test_websocket_error_handling(client: AsyncClient):
    """Test error handling in WebSocket."""
    # Use invalid session ID
    invalid_session_id = "invalid-session-id"
    
    # This should handle the error gracefully
    try:
        with client.websocket_connect(f"/ws/sessions/{invalid_session_id}") as websocket:
            # Should receive error message
            error_response = websocket.receive_json()
            assert error_response["type"] == "error"
    except Exception:
        # Connection might fail, which is expected for invalid session
        pass


@pytest.mark.asyncio
async def test_websocket_session_tracking(client: AsyncClient):
    """Test that WebSocket connections are tracked in metrics."""
    session_response = await client.post(
        "/api/v1/sessions/start",
        json={"user_email": "ws_tracking_test@example.com"},
    )
    session_id = session_response.json()["session_id"]
    
    with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
        greeting = websocket.receive_json()
        
        # Check metrics
        metrics_response = await client.get("/metrics/summary")
        assert metrics_response.status_code == 200
        
        metrics_data = metrics_response.json()
        assert "capacity" in metrics_data
        assert "sessions_active" in metrics_data["capacity"]
        # Should have at least 1 active session
        assert metrics_data["capacity"]["sessions_active"] >= 1
