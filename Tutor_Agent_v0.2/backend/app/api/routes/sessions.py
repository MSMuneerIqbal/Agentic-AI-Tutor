"""Session management endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


class SessionStartRequest(BaseModel):
    """Request to start a new session."""

    user_email: str | None = None  # Optional for now


class SessionStartResponse(BaseModel):
    """Response with new session ID."""

    session_id: str
    message: str


@router.post("/sessions/start", response_model=SessionStartResponse)
async def start_session(
    request: SessionStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new tutoring session.

    Creates a session in the database and returns the session ID.
    Frontend will use this ID to connect via WebSocket.
    """
    # TODO: Implement full session creation logic with user lookup/creation
    # For now, generate a session ID
    session_id = str(uuid.uuid4())

    return SessionStartResponse(
        session_id=session_id,
        message="Session created. Connect via WebSocket to begin.",
    )


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get session details.

    TODO: Implement session retrieval from database.
    """
    # Placeholder
    return {
        "session_id": session_id,
        "status": "active",
        "message": "Session endpoint placeholder",
    }

