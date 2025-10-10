"""
Real-time Collaboration Service for Phase 6
Enables collaborative learning features and real-time interactions
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from app.core.redis import get_redis_client
from app.core.database import get_db

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Types of collaboration."""
    STUDY_GROUP = "study_group"
    PEER_REVIEW = "peer_review"
    LIVE_SESSION = "live_session"
    DISCUSSION_FORUM = "discussion_forum"
    MENTORING = "mentoring"

class SessionStatus(Enum):
    """Collaboration session status."""
    WAITING = "waiting"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class CollaborationSession:
    """Collaboration session data."""
    id: str
    type: CollaborationType
    title: str
    description: str
    host_id: str
    participants: List[str]
    max_participants: int
    topic: str
    status: SessionStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    settings: Dict[str, Any] = None

@dataclass
class CollaborationMessage:
    """Collaboration message."""
    id: str
    session_id: str
    sender_id: str
    sender_name: str
    message_type: str  # text, question, answer, resource
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class StudyGroup:
    """Study group data."""
    id: str
    name: str
    description: str
    topic: str
    members: List[str]
    admin_id: str
    created_at: datetime
    is_public: bool = True
    max_members: int = 10

class CollaborationService:
    """Service for real-time collaboration features."""
    
    def __init__(self):
        self.max_sessions_per_user = 5
        self.session_timeout = 7200  # 2 hours
        self.message_retention = 86400  # 24 hours
    
    async def create_collaboration_session(
        self, 
        host_id: str, 
        session_type: CollaborationType, 
        title: str, 
        description: str,
        topic: str,
        max_participants: int = 10,
        settings: Optional[Dict[str, Any]] = None
    ) -> Optional[CollaborationSession]:
        """Create a new collaboration session."""
        try:
            session_id = str(uuid.uuid4())
            redis_client = await get_redis_client()
            
            session = CollaborationSession(
                id=session_id,
                type=session_type,
                title=title,
                description=description,
                host_id=host_id,
                participants=[host_id],
                max_participants=max_participants,
                topic=topic,
                status=SessionStatus.WAITING,
                created_at=datetime.utcnow(),
                settings=settings or {}
            )
            
            # Store session in Redis
            await redis_client.setex(
                f"collab_session:{session_id}",
                self.session_timeout,
                json.dumps(self._serialize_session(session))
            )
            
            # Add to host's sessions
            await redis_client.sadd(f"user_sessions:{host_id}", session_id)
            
            # Add to topic-based index
            await redis_client.sadd(f"topic_sessions:{topic}", session_id)
            
            logger.info(f"Created collaboration session {session_id} for topic {topic}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create collaboration session: {e}")
            return None
    
    async def join_collaboration_session(self, session_id: str, user_id: str) -> bool:
        """Join a collaboration session."""
        try:
            redis_client = await get_redis_client()
            
            # Get session data
            session_data = await redis_client.get(f"collab_session:{session_id}")
            if not session_data:
                return False
            
            session = self._deserialize_session(json.loads(session_data))
            
            # Check if session is joinable
            if session.status != SessionStatus.WAITING:
                return False
            
            # Check if session is full
            if len(session.participants) >= session.max_participants:
                return False
            
            # Add user to participants
            if user_id not in session.participants:
                session.participants.append(user_id)
                
                # Update session in Redis
                await redis_client.setex(
                    f"collab_session:{session_id}",
                    self.session_timeout,
                    json.dumps(self._serialize_session(session))
                )
                
                # Add to user's sessions
                await redis_client.sadd(f"user_sessions:{user_id}", session_id)
                
                # Notify other participants
                await self._notify_participants(session_id, f"User {user_id} joined the session")
                
                logger.info(f"User {user_id} joined session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to join collaboration session: {e}")
            return False
    
    async def leave_collaboration_session(self, session_id: str, user_id: str) -> bool:
        """Leave a collaboration session."""
        try:
            redis_client = await get_redis_client()
            
            # Get session data
            session_data = await redis_client.get(f"collab_session:{session_id}")
            if not session_data:
                return False
            
            session = self._deserialize_session(json.loads(session_data))
            
            # Remove user from participants
            if user_id in session.participants:
                session.participants.remove(user_id)
                
                # If host leaves, transfer host to another participant or end session
                if session.host_id == user_id and session.participants:
                    session.host_id = session.participants[0]
                elif session.host_id == user_id and not session.participants:
                    session.status = SessionStatus.CANCELLED
                
                # Update session in Redis
                await redis_client.setex(
                    f"collab_session:{session_id}",
                    self.session_timeout,
                    json.dumps(self._serialize_session(session))
                )
                
                # Remove from user's sessions
                await redis_client.srem(f"user_sessions:{user_id}", session_id)
                
                # Notify other participants
                await self._notify_participants(session_id, f"User {user_id} left the session")
                
                logger.info(f"User {user_id} left session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to leave collaboration session: {e}")
            return False
    
    async def start_collaboration_session(self, session_id: str, host_id: str) -> bool:
        """Start a collaboration session."""
        try:
            redis_client = await get_redis_client()
            
            # Get session data
            session_data = await redis_client.get(f"collab_session:{session_id}")
            if not session_data:
                return False
            
            session = self._deserialize_session(json.loads(session_data))
            
            # Check if user is the host
            if session.host_id != host_id:
                return False
            
            # Check if session can be started
            if session.status != SessionStatus.WAITING:
                return False
            
            # Start session
            session.status = SessionStatus.ACTIVE
            session.started_at = datetime.utcnow()
            
            # Update session in Redis
            await redis_client.setex(
                f"collab_session:{session_id}",
                self.session_timeout,
                json.dumps(self._serialize_session(session))
            )
            
            # Notify participants
            await self._notify_participants(session_id, "Session started!")
            
            logger.info(f"Started collaboration session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start collaboration session: {e}")
            return False
    
    async def send_collaboration_message(
        self, 
        session_id: str, 
        sender_id: str, 
        sender_name: str,
        message_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a message in a collaboration session."""
        try:
            redis_client = await get_redis_client()
            
            # Check if session exists and is active
            session_data = await redis_client.get(f"collab_session:{session_id}")
            if not session_data:
                return False
            
            session = self._deserialize_session(json.loads(session_data))
            if session.status != SessionStatus.ACTIVE:
                return False
            
            # Check if sender is a participant
            if sender_id not in session.participants:
                return False
            
            # Create message
            message = CollaborationMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                sender_id=sender_id,
                sender_name=sender_name,
                message_type=message_type,
                content=content,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Store message
            message_key = f"collab_messages:{session_id}"
            await redis_client.lpush(message_key, json.dumps(self._serialize_message(message)))
            await redis_client.expire(message_key, self.message_retention)
            
            # Limit message history
            await redis_client.ltrim(message_key, 0, 999)  # Keep last 1000 messages
            
            # Notify participants
            await self._notify_participants(session_id, f"New message from {sender_name}")
            
            logger.info(f"Message sent in session {session_id} by {sender_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send collaboration message: {e}")
            return False
    
    async def get_collaboration_messages(self, session_id: str, limit: int = 50) -> List[CollaborationMessage]:
        """Get recent messages from a collaboration session."""
        try:
            redis_client = await get_redis_client()
            message_key = f"collab_messages:{session_id}"
            
            # Get recent messages
            message_data = await redis_client.lrange(message_key, 0, limit - 1)
            
            messages = []
            for data in message_data:
                message = self._deserialize_message(json.loads(data))
                messages.append(message)
            
            # Return in chronological order
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"Failed to get collaboration messages: {e}")
            return []
    
    async def get_available_sessions(self, topic: str, user_id: str) -> List[CollaborationSession]:
        """Get available collaboration sessions for a topic."""
        try:
            redis_client = await get_redis_client()
            
            # Get session IDs for topic
            session_ids = await redis_client.smembers(f"topic_sessions:{topic}")
            
            available_sessions = []
            for session_id in session_ids:
                session_data = await redis_client.get(f"collab_session:{session_id}")
                if session_data:
                    session = self._deserialize_session(json.loads(session_data))
                    
                    # Check if session is available and user can join
                    if (session.status == SessionStatus.WAITING and 
                        len(session.participants) < session.max_participants and
                        user_id not in session.participants):
                        available_sessions.append(session)
            
            return available_sessions
            
        except Exception as e:
            logger.error(f"Failed to get available sessions: {e}")
            return []
    
    async def create_study_group(
        self, 
        admin_id: str, 
        name: str, 
        description: str, 
        topic: str,
        is_public: bool = True,
        max_members: int = 10
    ) -> Optional[StudyGroup]:
        """Create a study group."""
        try:
            group_id = str(uuid.uuid4())
            redis_client = await get_redis_client()
            
            study_group = StudyGroup(
                id=group_id,
                name=name,
                description=description,
                topic=topic,
                members=[admin_id],
                admin_id=admin_id,
                created_at=datetime.utcnow(),
                is_public=is_public,
                max_members=max_members
            )
            
            # Store study group
            await redis_client.setex(
                f"study_group:{group_id}",
                86400 * 30,  # 30 days
                json.dumps(self._serialize_study_group(study_group))
            )
            
            # Add to topic index
            await redis_client.sadd(f"topic_groups:{topic}", group_id)
            
            # Add to admin's groups
            await redis_client.sadd(f"user_groups:{admin_id}", group_id)
            
            logger.info(f"Created study group {group_id} for topic {topic}")
            return study_group
            
        except Exception as e:
            logger.error(f"Failed to create study group: {e}")
            return None
    
    async def join_study_group(self, group_id: str, user_id: str) -> bool:
        """Join a study group."""
        try:
            redis_client = await get_redis_client()
            
            # Get group data
            group_data = await redis_client.get(f"study_group:{group_id}")
            if not group_data:
                return False
            
            study_group = self._deserialize_study_group(json.loads(group_data))
            
            # Check if group is joinable
            if len(study_group.members) >= study_group.max_members:
                return False
            
            # Add user to members
            if user_id not in study_group.members:
                study_group.members.append(user_id)
                
                # Update group in Redis
                await redis_client.setex(
                    f"study_group:{group_id}",
                    86400 * 30,
                    json.dumps(self._serialize_study_group(study_group))
                )
                
                # Add to user's groups
                await redis_client.sadd(f"user_groups:{user_id}", group_id)
                
                logger.info(f"User {user_id} joined study group {group_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to join study group: {e}")
            return False
    
    async def get_study_groups_for_topic(self, topic: str) -> List[StudyGroup]:
        """Get study groups for a specific topic."""
        try:
            redis_client = await get_redis_client()
            
            # Get group IDs for topic
            group_ids = await redis_client.smembers(f"topic_groups:{topic}")
            
            study_groups = []
            for group_id in group_ids:
                group_data = await redis_client.get(f"study_group:{group_id}")
                if group_data:
                    study_group = self._deserialize_study_group(json.loads(group_data))
                    if study_group.is_public:
                        study_groups.append(study_group)
            
            return study_groups
            
        except Exception as e:
            logger.error(f"Failed to get study groups for topic: {e}")
            return []
    
    async def _notify_participants(self, session_id: str, message: str) -> None:
        """Notify all participants of a session."""
        try:
            redis_client = await get_redis_client()
            
            # Get session data
            session_data = await redis_client.get(f"collab_session:{session_id}")
            if not session_data:
                return
            
            session = self._deserialize_session(json.loads(session_data))
            
            # Send notification to each participant
            for participant_id in session.participants:
                notification_key = f"notifications:{participant_id}"
                notification = {
                    "type": "collaboration",
                    "session_id": session_id,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await redis_client.lpush(notification_key, json.dumps(notification))
                await redis_client.expire(notification_key, 86400)  # 24 hours
                
        except Exception as e:
            logger.error(f"Failed to notify participants: {e}")
    
    def _serialize_session(self, session: CollaborationSession) -> Dict[str, Any]:
        """Serialize collaboration session for storage."""
        return {
            "id": session.id,
            "type": session.type.value,
            "title": session.title,
            "description": session.description,
            "host_id": session.host_id,
            "participants": session.participants,
            "max_participants": session.max_participants,
            "topic": session.topic,
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "settings": session.settings or {}
        }
    
    def _deserialize_session(self, data: Dict[str, Any]) -> CollaborationSession:
        """Deserialize collaboration session from storage."""
        return CollaborationSession(
            id=data["id"],
            type=CollaborationType(data["type"]),
            title=data["title"],
            description=data["description"],
            host_id=data["host_id"],
            participants=data["participants"],
            max_participants=data["max_participants"],
            topic=data["topic"],
            status=SessionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data["started_at"] else None,
            ended_at=datetime.fromisoformat(data["ended_at"]) if data["ended_at"] else None,
            settings=data.get("settings", {})
        )
    
    def _serialize_message(self, message: CollaborationMessage) -> Dict[str, Any]:
        """Serialize collaboration message for storage."""
        return {
            "id": message.id,
            "session_id": message.session_id,
            "sender_id": message.sender_id,
            "sender_name": message.sender_name,
            "message_type": message.message_type,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "metadata": message.metadata or {}
        }
    
    def _deserialize_message(self, data: Dict[str, Any]) -> CollaborationMessage:
        """Deserialize collaboration message from storage."""
        return CollaborationMessage(
            id=data["id"],
            session_id=data["session_id"],
            sender_id=data["sender_id"],
            sender_name=data["sender_name"],
            message_type=data["message_type"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )
    
    def _serialize_study_group(self, group: StudyGroup) -> Dict[str, Any]:
        """Serialize study group for storage."""
        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "topic": group.topic,
            "members": group.members,
            "admin_id": group.admin_id,
            "created_at": group.created_at.isoformat(),
            "is_public": group.is_public,
            "max_members": group.max_members
        }
    
    def _deserialize_study_group(self, data: Dict[str, Any]) -> StudyGroup:
        """Deserialize study group from storage."""
        return StudyGroup(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            topic=data["topic"],
            members=data["members"],
            admin_id=data["admin_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            is_public=data.get("is_public", True),
            max_members=data.get("max_members", 10)
        )

# Global instance
_collaboration_service = None

async def get_collaboration_service() -> CollaborationService:
    """Get global collaboration service instance."""
    global _collaboration_service
    if _collaboration_service is None:
        _collaboration_service = CollaborationService()
    return _collaboration_service
