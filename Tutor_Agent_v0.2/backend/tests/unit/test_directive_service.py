"""Unit tests for directive service."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.directive import Directive
from app.services.directive_service import DirectiveService


@pytest.mark.asyncio
async def test_create_directive(db_session: AsyncSession):
    """Test creating a directive."""
    service = DirectiveService()
    session_id = str(uuid.uuid4())
    
    directive = await service.create_directive(
        session_id=session_id,
        directive_type="test",
        payload={"test": "data"},
        db=db_session,
    )
    
    assert directive.id is not None
    assert directive.session_id == uuid.UUID(session_id)
    assert directive.type == "test"
    assert directive.payload == {"test": "data"}
    assert directive.created_at is not None


@pytest.mark.asyncio
async def test_get_session_directives(db_session: AsyncSession):
    """Test retrieving directives for a session."""
    service = DirectiveService()
    session_id = str(uuid.uuid4())
    
    # Create multiple directives
    directive1 = await service.create_directive(
        session_id=session_id,
        directive_type="type1",
        payload={"data": 1},
        db=db_session,
    )
    
    directive2 = await service.create_directive(
        session_id=session_id,
        directive_type="type2",
        payload={"data": 2},
        db=db_session,
    )
    
    # Get all directives for session
    directives = await service.get_session_directives(
        session_id=session_id,
        db=db_session,
    )
    
    assert len(directives) == 2
    assert directives[0].id == directive1.id
    assert directives[1].id == directive2.id


@pytest.mark.asyncio
async def test_create_session_start_directive(db_session: AsyncSession):
    """Test creating session start directive."""
    service = DirectiveService()
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    directive = await service.create_session_start_directive(
        session_id=session_id,
        user_id=user_id,
        db=db_session,
    )
    
    assert directive.type == "orchestrator"
    assert directive.payload["event"] == "session_started"
    assert directive.payload["user_id"] == user_id
    assert directive.payload["initial_state"] == "greeting"
    assert "timestamp" in directive.payload


@pytest.mark.asyncio
async def test_create_greeting_directive(db_session: AsyncSession):
    """Test creating greeting directive."""
    service = DirectiveService()
    session_id = str(uuid.uuid4())
    greeting_message = "Hello! Ready to begin?"
    
    directive = await service.create_greeting_directive(
        session_id=session_id,
        greeting_message=greeting_message,
        db=db_session,
    )
    
    assert directive.type == "orchestrator"
    assert directive.payload["event"] == "greeting_sent"
    assert directive.payload["message"] == greeting_message
    assert directive.payload["agent"] == "orchestrator"
    assert "timestamp" in directive.payload


@pytest.mark.asyncio
async def test_create_user_input_directive(db_session: AsyncSession):
    """Test creating user input directive."""
    service = DirectiveService()
    session_id = str(uuid.uuid4())
    user_input = "I want to learn Docker"
    
    directive = await service.create_user_input_directive(
        session_id=session_id,
        user_input=user_input,
        db=db_session,
    )
    
    assert directive.type == "user"
    assert directive.payload["event"] == "user_input_received"
    assert directive.payload["input"] == user_input
    assert directive.payload["input_length"] == len(user_input)
    assert "timestamp" in directive.payload


@pytest.mark.asyncio
async def test_create_agent_response_directive(db_session: AsyncSession):
    """Test creating agent response directive."""
    service = DirectiveService()
    session_id = str(uuid.uuid4())
    agent_name = "tutor"
    response_message = "Let's start with Docker basics"
    action = "continue"
    
    directive = await service.create_agent_response_directive(
        session_id=session_id,
        agent_name=agent_name,
        response_message=response_message,
        action=action,
        db=db_session,
    )
    
    assert directive.type == "agent"
    assert directive.payload["event"] == "agent_response_sent"
    assert directive.payload["agent"] == agent_name
    assert directive.payload["message"] == response_message
    assert directive.payload["action"] == action
    assert directive.payload["response_length"] == len(response_message)
    assert "timestamp" in directive.payload


@pytest.mark.asyncio
async def test_create_state_transition_directive(db_session: AsyncSession):
    """Test creating state transition directive."""
    service = DirectiveService()
    session_id = str(uuid.uuid4())
    from_state = "greeting"
    to_state = "assessing"
    reason = "user confirmed readiness"
    
    directive = await service.create_state_transition_directive(
        session_id=session_id,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
        db=db_session,
    )
    
    assert directive.type == "orchestrator"
    assert directive.payload["event"] == "state_transition"
    assert directive.payload["from_state"] == from_state
    assert directive.payload["to_state"] == to_state
    assert directive.payload["reason"] == reason
    assert "timestamp" in directive.payload


@pytest.mark.asyncio
async def test_directive_timestamps_are_recent(db_session: AsyncSession):
    """Test that directive timestamps are recent."""
    service = DirectiveService()
    session_id = str(uuid.uuid4())
    
    directive = await service.create_directive(
        session_id=session_id,
        directive_type="test",
        payload={"test": "data"},
        db=db_session,
    )
    
    # Check that created_at is recent (within last minute)
    now = datetime.utcnow()
    time_diff = (now - directive.created_at).total_seconds()
    assert time_diff < 60  # Less than 1 minute


@pytest.mark.asyncio
async def test_directive_payload_structure(db_session: AsyncSession):
    """Test that directive payloads have proper structure."""
    service = DirectiveService()
    session_id = str(uuid.uuid4())
    
    # Test session start directive
    directive = await service.create_session_start_directive(
        session_id=session_id,
        user_id=str(uuid.uuid4()),
        db=db_session,
    )
    
    payload = directive.payload
    assert isinstance(payload, dict)
    assert "event" in payload
    assert "timestamp" in payload
    assert "user_id" in payload
    assert "initial_state" in payload
    
    # Verify timestamp format
    timestamp = payload["timestamp"]
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
