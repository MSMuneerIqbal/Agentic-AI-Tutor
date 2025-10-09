"""Unit tests for database models."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Session, SessionState


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        display_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.email == "test@example.com"
    assert user.display_name == "Test User"
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_create_session(db_session: AsyncSession):
    """Test creating a session."""
    # First create a user
    user = User(
        email="test@example.com",
        display_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create session
    session = Session(
        user_id=user.id,
        state=SessionState.GREETING,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    assert session.id is not None
    assert session.user_id == user.id
    assert session.state == SessionState.GREETING
    assert session.created_at is not None


@pytest.mark.asyncio
async def test_user_sessions_relationship(db_session: AsyncSession):
    """Test user-sessions relationship."""
    # Create user
    user = User(
        email="test@example.com",
        display_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create multiple sessions
    session1 = Session(user_id=user.id, state=SessionState.GREETING)
    session2 = Session(user_id=user.id, state=SessionState.ASSESSING)
    db_session.add_all([session1, session2])
    await db_session.commit()

    # Refresh user to load relationship
    await db_session.refresh(user, ["sessions"])

    assert len(user.sessions) == 2
    assert session1 in user.sessions
    assert session2 in user.sessions

