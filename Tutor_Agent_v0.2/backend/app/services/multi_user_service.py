"""
Multi-User Support Service for Phase 6
Handles concurrent users, session management, and user isolation
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from app.core.database import get_db
from app.core.redis import get_redis_client
from app.models.user import User
from app.models.session import Session
from app.models import SessionState

logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """User session information."""
    user_id: str
    session_id: str
    state: SessionState
    current_topic: str
    learning_style: str
    progress: int
    last_activity: datetime
    is_active: bool

@dataclass
class SystemMetrics:
    """System performance metrics."""
    active_users: int
    total_sessions: int
    average_session_duration: float
    system_load: float
    memory_usage: float

class MultiUserService:
    """Service for managing multiple concurrent users."""
    
    def __init__(self):
        self.max_concurrent_users = 1000
        self.session_timeout = 3600  # 1 hour
        self.cleanup_interval = 300  # 5 minutes
        
    async def create_user_session(self, user_id: str, initial_state: SessionState = SessionState.GREETING) -> UserSession:
        """Create a new user session."""
        try:
            session_id = str(uuid.uuid4())
            redis_client = await get_redis_client()
            
            # Create session data
            session_data = UserSession(
                user_id=user_id,
                session_id=session_id,
                state=initial_state,
                current_topic="",
                learning_style="V",
                progress=0,
                last_activity=datetime.utcnow(),
                is_active=True
            )
            
            # Store in Redis for fast access
            await redis_client.setex(
                f"session:{session_id}",
                self.session_timeout,
                self._serialize_session(session_data)
            )
            
            # Store in database for persistence
            async for db in get_db():
                db_session = Session(
                    id=session_id,
                    user_id=user_id,
                    state=initial_state,
                    current_topic="",
                    learning_style="V",
                    progress=0,
                    created_at=datetime.utcnow()
                )
                db.add(db_session)
                await db.commit()
                break
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to create user session: {e}")
            raise
    
    async def get_user_session(self, session_id: str) -> Optional[UserSession]:
        """Get user session by ID."""
        try:
            redis_client = await get_redis_client()
            
            # Try Redis first
            session_data = await redis_client.get(f"session:{session_id}")
            if session_data:
                return self._deserialize_session(session_data)
            
            # Fallback to database
            async for db in get_db():
                db_session = await db.get(Session, session_id)
                if db_session:
                    return UserSession(
                        user_id=db_session.user_id,
                        session_id=db_session.id,
                        state=db_session.state,
                        current_topic=db_session.current_topic,
                        learning_style=db_session.learning_style,
                        progress=db_session.progress,
                        last_activity=db_session.updated_at or db_session.created_at,
                        is_active=True
                    )
                break
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user session: {e}")
            return None
    
    async def update_user_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update user session."""
        try:
            redis_client = await get_redis_client()
            
            # Get current session
            session = await self.get_user_session(session_id)
            if not session:
                return False
            
            # Update session data
            for key, value in updates.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            session.last_activity = datetime.utcnow()
            
            # Update Redis
            await redis_client.setex(
                f"session:{session_id}",
                self.session_timeout,
                self._serialize_session(session)
            )
            
            # Update database
            async for db in get_db():
                db_session = await db.get(Session, session_id)
                if db_session:
                    for key, value in updates.items():
                        if hasattr(db_session, key):
                            setattr(db_session, key, value)
                    db_session.updated_at = datetime.utcnow()
                    await db.commit()
                break
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user session: {e}")
            return False
    
    async def end_user_session(self, session_id: str) -> bool:
        """End a user session."""
        try:
            redis_client = await get_redis_client()
            
            # Remove from Redis
            await redis_client.delete(f"session:{session_id}")
            
            # Update database
            async for db in get_db():
                db_session = await db.get(Session, session_id)
                if db_session:
                    db_session.is_active = False
                    db_session.ended_at = datetime.utcnow()
                    await db.commit()
                break
            
            logger.info(f"Ended session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end user session: {e}")
            return False
    
    async def get_active_users(self) -> List[UserSession]:
        """Get all active user sessions."""
        try:
            redis_client = await get_redis_client()
            
            # Get all session keys
            session_keys = await redis_client.keys("session:*")
            active_sessions = []
            
            for key in session_keys:
                session_data = await redis_client.get(key)
                if session_data:
                    session = self._deserialize_session(session_data)
                    if session.is_active:
                        active_sessions.append(session)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"Failed to get active users: {e}")
            return []
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get system performance metrics."""
        try:
            active_sessions = await self.get_active_users()
            active_users = len(active_sessions)
            
            # Calculate average session duration
            total_duration = 0
            for session in active_sessions:
                duration = (datetime.utcnow() - session.last_activity).total_seconds()
                total_duration += duration
            
            average_duration = total_duration / active_users if active_users > 0 else 0
            
            # Get total sessions from database
            total_sessions = 0
            async for db in get_db():
                result = await db.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = result.scalar()
                break
            
            return SystemMetrics(
                active_users=active_users,
                total_sessions=total_sessions,
                average_session_duration=average_duration,
                system_load=active_users / self.max_concurrent_users,
                memory_usage=0.0  # Would be implemented with system monitoring
            )
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return SystemMetrics(0, 0, 0.0, 0.0, 0.0)
    
    async def cleanup_inactive_sessions(self) -> int:
        """Clean up inactive sessions."""
        try:
            redis_client = await get_redis_client()
            cleaned_count = 0
            
            # Get all session keys
            session_keys = await redis_client.keys("session:*")
            
            for key in session_keys:
                session_data = await redis_client.get(key)
                if session_data:
                    session = self._deserialize_session(session_data)
                    
                    # Check if session is inactive
                    if (datetime.utcnow() - session.last_activity).total_seconds() > self.session_timeout:
                        await redis_client.delete(key)
                        cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} inactive sessions")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup inactive sessions: {e}")
            return 0
    
    def _serialize_session(self, session: UserSession) -> str:
        """Serialize session data for Redis storage."""
        return f"{session.user_id}|{session.session_id}|{session.state.value}|{session.current_topic}|{session.learning_style}|{session.progress}|{session.last_activity.isoformat()}|{session.is_active}"
    
    def _deserialize_session(self, data: str) -> UserSession:
        """Deserialize session data from Redis."""
        parts = data.split("|")
        return UserSession(
            user_id=parts[0],
            session_id=parts[1],
            state=SessionState(parts[2]),
            current_topic=parts[3],
            learning_style=parts[4],
            progress=int(parts[5]),
            last_activity=datetime.fromisoformat(parts[6]),
            is_active=parts[7] == "True"
        )

# Global instance
_multi_user_service = None

async def get_multi_user_service() -> MultiUserService:
    """Get global multi-user service instance."""
    global _multi_user_service
    if _multi_user_service is None:
        _multi_user_service = MultiUserService()
    return _multi_user_service
