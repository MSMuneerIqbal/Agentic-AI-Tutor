"""Session management endpoints."""

import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.core.session_store import session_store
from app.models.session import SessionState
from app.models.user_mongo import User

logger = get_logger(__name__)
metrics = get_metrics_collector()

router = APIRouter()


class SessionStartRequest(BaseModel):
    """Request to start a new session."""

    user_email: str | None = None  # Optional for now


class SessionStartResponse(BaseModel):
    """Response with new session ID."""

    session_id: str
    message: str


@router.post("/sessions/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest):
    """
    Start a new tutoring session.

    Creates a session in MongoDB and returns the session ID.
    Frontend will use this ID to connect via WebSocket.
    """
    try:
        # Track request latency
        start_time = datetime.utcnow()
        
        # Get or create user
        user = await get_or_create_user(request.user_email)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create session state in MongoDB session store
        session_data = {
            "session_id": session_id,
            "user_id": str(user.id),
            "user_email": user.email,
            "state": SessionState.GREETING,
            "last_checkpoint": "session_started",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "conversation_history": [],
            "assessment_data": {
                "vark_responses": [],
                "experience_questions": [],
                "answers": [],
                "completed": False
            },
            "progress": {
                "topics_completed": [],
                "quiz_scores": [],
                "time_spent": 0
            }
        }
        
        # Store session in MongoDB
        await session_store.set_session(f"session:{session_id}", session_data, ttl=86400)
        
        # Add to active sessions
        await session_store.add_to_set("active_sessions", session_id)
        
        # Track metrics
        latency = (datetime.utcnow() - start_time).total_seconds()
        metrics.track_request_latency("/api/v1/sessions/start", latency)
        
        logger.info(
            f"Session created successfully",
            extra={
                "session_id": session_id,
                "user_id": str(user.id),
                "user_email": user.email,
                "latency_ms": latency * 1000,
            },
        )
        
        return SessionStartResponse(
            session_id=session_id,
            message="Session created. Connect via WebSocket to begin.",
        )
        
    except Exception as e:
        logger.error(
            f"Failed to create session: {str(e)}",
            extra={"user_email": request.user_email, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail="Failed to create session")


async def get_or_create_user(user_email: Optional[str]) -> User:
    """Get existing user or create new one."""
    if not user_email:
        # For now, create a temporary user with a generated email
        user_email = f"temp_user_{uuid.uuid4().hex[:8]}@tutorgpt.local"
    
    # Try to find existing user
    user = await User.find_one(User.email == user_email)
    
    if user:
        logger.info(f"Found existing user: {user.email}")
        return user
    
    # Create new user
    user = User(
        email=user_email,
        display_name=user_email.split("@")[0],  # Use email prefix as display name
    )
    
    await user.insert()
    
    logger.info(f"Created new user: {user.email}")
    return user


async def get_active_sessions_count() -> int:
    """Get count of active sessions from MongoDB."""
    try:
        count = await session_store.get_set_members("active_sessions")
        return len(count) if count else 0
    except Exception as e:
        logger.warning(f"Failed to get active sessions count: {e}")
        return 0


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get session details.

    Retrieves session from MongoDB session store.
    """
    try:
        # Get session from MongoDB
        session_data = await session_store.get_session(f"session:{session_id}")
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Retrieved session: {session_id}")
        return {
            "session_id": session_id,
            "data": session_data,
            "source": "mongodb",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")

