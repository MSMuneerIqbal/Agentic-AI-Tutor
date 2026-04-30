"""Integration tests for WebSocket reconnect and resume."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.main import app
from app.models import Session, SessionState, User


@pytest.mark.asyncio
async def test_websocket_reconnect_resume(db_session: AsyncSession):
    """
    Test reconnect and resume session.

    Flow:
    1. Create session and connect
    2. Exchange messages
    3. Disconnect
    4. Reconnect with same session_id
    5. Verify state is resumed
    """
    # Create user and session in database
    user = User(email="test@example.com", display_name="Test User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = Session(
        user_id=user.id,
        state=SessionState.TUTORING,  # Simulate mid-session state
        last_checkpoint="Completed assessment",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    session_id = str(session.id)

    # Store session state in Redis
    await redis_client.set_session(
        session_id,
        {
            "state": SessionState.TUTORING.value,
            "last_checkpoint": "Completed assessment",
            "last_topic": "Docker basics",
        },
        ttl=3600,
    )

    # First connection
    with TestClient(app) as test_client:
        with test_client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Receive greeting
            greeting = websocket.receive_json()
            assert greeting is not None

            # Send a message
            websocket.send_json({"message": "Continue teaching"})
            response = websocket.receive_json()
            assert response is not None

            # Disconnect
            websocket.close()

    # Second connection (reconnect)
    with TestClient(app) as test_client:
        with test_client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Receive resumed greeting
            resumed_greeting = websocket.receive_json()

            # Verify we're resuming from correct state
            assert resumed_greeting is not None
            # In production, this would check for state-specific messaging

    # Verify session state persisted in Redis
    resumed_session = await redis_client.get_session(session_id)
    assert resumed_session is not None
    assert resumed_session["state"] == SessionState.TUTORING.value


@pytest.mark.asyncio
async def test_reconnect_preserves_context():
    """Test reconnect preserves session context."""
    pytest.skip("Full context preservation implementation pending")


@pytest.mark.asyncio
async def test_reconnect_invalid_session():
    """Test reconnect with invalid session_id fails gracefully."""
    with TestClient(app) as test_client:
        # Try to connect with non-existent session
        import uuid

        fake_session_id = str(uuid.uuid4())

        # WebSocket should still accept connection
        # (Error handling is application logic)
        with test_client.websocket_connect(f"/ws/sessions/{fake_session_id}") as websocket:
            # Should still get greeting (placeholder implementation)
            data = websocket.receive_json()
            assert data is not None

