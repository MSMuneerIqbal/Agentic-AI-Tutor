"""Session management endpoints."""

import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.core.redis import redis_client
from app.models.session import Session, SessionState
from app.models.user import User
from app.services.directive_service import directive_service

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
async def start_session(
    request: SessionStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new tutoring session.

    Creates a session in the database and returns the session ID.
    Frontend will use this ID to connect via WebSocket.
    """
    try:
        # Track request latency
        start_time = datetime.utcnow()
        
        # Get or create user
        user = await get_or_create_user(db, request.user_email)
        
        # Create new session
        session = Session(
            user_id=user.id,
            state=SessionState.GREETING,
            last_checkpoint="session_started",
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # Store session state in Redis
        await store_session_state(session)
        
        # Create initial session start directive
        await directive_service.create_session_start_directive(
            session_id=str(session.id),
            user_id=str(user.id),
            db=db,
        )
        
        # Track metrics
        latency = (datetime.utcnow() - start_time).total_seconds()
        metrics.track_request_latency("/api/v1/sessions/start", latency)
        metrics.set_sessions_active(await get_active_sessions_count())
        
        logger.info(
            f"Session created successfully",
            extra={
                "session_id": str(session.id),
                "user_id": str(user.id),
                "user_email": user.email,
                "latency_ms": latency * 1000,
            },
        )
        
        return SessionStartResponse(
            session_id=str(session.id),
            message="Session created. Connect via WebSocket to begin.",
        )
        
    except Exception as e:
        logger.error(
            f"Failed to create session: {str(e)}",
            extra={"user_email": request.user_email, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail="Failed to create session")


async def get_or_create_user(db: AsyncSession, user_email: str | None) -> User:
    """Get existing user or create new one."""
    if not user_email:
        # For now, create a temporary user with a generated email
        user_email = f"temp_user_{uuid.uuid4().hex[:8]}@tutorgpt.local"
    
    # Try to find existing user
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    
    if user:
        logger.info(f"Found existing user: {user.email}")
        return user
    
    # Create new user
    user = User(
        email=user_email,
        display_name=user_email.split("@")[0],  # Use email prefix as display name
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"Created new user: {user.email}")
    return user


async def store_session_state(session: Session) -> None:
    """Store session state in Redis for fast access."""
    session_data = {
        "id": str(session.id),
        "user_id": str(session.user_id),
        "state": session.state.value,
        "last_checkpoint": session.last_checkpoint,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }
    
    # Store with TTL of 24 hours
    await redis_client.setex(
        f"session:{session.id}",
        86400,  # 24 hours
        json.dumps(session_data),
    )
    
    # Add to active sessions set
    await redis_client.set_add("active_sessions", str(session.id))
    
    logger.debug(f"Stored session state in Redis: {session.id}")


async def get_active_sessions_count() -> int:
    """Get count of active sessions from Redis."""
    try:
        count = await redis_client.set_cardinality("active_sessions")
        return count
    except Exception as e:
        logger.warning(f"Failed to get active sessions count: {e}")
        return 0


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get session details.

    Retrieves session from database and Redis cache.
    """
    try:
        # Try Redis first for fast access
        session_data_str = await redis_client.get(f"session:{session_id}")
        
        if session_data_str:
            session_data = json.loads(session_data_str)
            logger.debug(f"Retrieved session from Redis cache: {session_id}")
            return {
                "session_id": session_id,
                "data": session_data,
                "source": "cache",
            }
        
        # Fallback to database
        result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update Redis cache
        await store_session_state(session)
        
        session_data = {
            "id": str(session.id),
            "user_id": str(session.user_id),
            "state": session.state.value,
            "last_checkpoint": session.last_checkpoint,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
        }
        
        logger.info(f"Retrieved session from database: {session_id}")
        return {
            "session_id": session_id,
            "data": session_data,
            "source": "database",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")

