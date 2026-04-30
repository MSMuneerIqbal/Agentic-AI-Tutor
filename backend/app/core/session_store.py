"""MongoDB-based session storage - Redis alternative."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from beanie import Document, Indexed
from pydantic import Field

class Session(Document):
    """MongoDB session document."""
    session_id: str = Field(..., unique=True, index=True)
    user_id: Optional[str] = Field(None, index=True)
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    is_active: bool = Field(default=True)

    class Settings:
        name = "sessions"
        indexes = [
            [("session_id", 1)],
            [("user_id", 1)],
            [("expires_at", 1)],
        ]

class MongoDBSessionStore:
    """MongoDB-based session storage - alternative to Redis."""
    
    def __init__(self):
        self.default_ttl = 86400  # 24 hours

    async def set_session(self, session_id: str, data: Dict[str, Any], user_id: Optional[str] = None, ttl: int = None) -> bool:
        """Store session data in MongoDB."""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            session = await Session.find_one(Session.session_id == session_id)
            if session:
                session.data = data
                session.user_id = user_id
                session.updated_at = datetime.utcnow()
                session.expires_at = expires_at
                session.is_active = True
                await session.save()
            else:
                session = Session(
                    session_id=session_id,
                    user_id=user_id,
                    data=data,
                    expires_at=expires_at
                )
                await session.insert()
            
            return True
        except Exception as e:
            print(f"Error storing session: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from MongoDB."""
        try:
            session = await Session.find_one(Session.session_id == session_id)
            if session and session.is_active and session.expires_at > datetime.utcnow():
                return session.data
            return None
        except Exception as e:
            print(f"Error retrieving session: {e}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from MongoDB."""
        try:
            session = await Session.find_one(Session.session_id == session_id)
            if session:
                session.is_active = False
                await session.save()
                return True
            return False
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    async def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Cache data in MongoDB (alternative to Redis cache)."""
        return await self.set_session(f"cache:{key}", {"value": value}, ttl=ttl)

    async def get_cache(self, key: str) -> Optional[Any]:
        """Retrieve cached data from MongoDB."""
        data = await self.get_session(f"cache:{key}")
        return data.get("value") if data else None

    async def delete_cache(self, key: str) -> bool:
        """Delete cached data from MongoDB."""
        return await self.delete_session(f"cache:{key}")

    async def add_to_set(self, set_name: str, value: str) -> bool:
        """Add value to a set (Redis alternative)."""
        try:
            session = await Session.find_one(Session.session_id == f"set:{set_name}")
            if session:
                # Get existing values as list
                existing_values = session.data.get("values", [])
                if not isinstance(existing_values, list):
                    existing_values = []
                
                # Convert to set, add value, convert back to list
                values_set = set(existing_values)
                values_set.add(value)
                session.data["values"] = list(values_set)
                session.updated_at = datetime.utcnow()
                await session.save()
            else:
                session = Session(
                    session_id=f"set:{set_name}",
                    data={"values": [value]},
                    expires_at=datetime.utcnow() + timedelta(days=7)  # Sets expire in 7 days
                )
                await session.insert()
            return True
        except Exception as e:
            print(f"Error adding to set: {e}")
            return False

    async def remove_from_set(self, set_name: str, value: str) -> bool:
        """Remove value from a set (Redis alternative)."""
        try:
            session = await Session.find_one(Session.session_id == f"set:{set_name}")
            if session and "values" in session.data:
                values_list = session.data["values"]
                if isinstance(values_list, list) and value in values_list:
                    values_list.remove(value)
                    session.data["values"] = values_list
                    session.updated_at = datetime.utcnow()
                    await session.save()
                    return True
            return False
        except Exception as e:
            print(f"Error removing from set: {e}")
            return False

    async def get_set_members(self, set_name: str) -> list:
        """Get all members of a set (Redis alternative)."""
        try:
            session = await Session.find_one(Session.session_id == f"set:{set_name}")
            if session and "values" in session.data:
                return session.data["values"]
            return []
        except Exception as e:
            print(f"Error getting set members: {e}")
            return []

    async def cleanup_expired(self) -> int:
        """Clean up expired sessions."""
        try:
            expired_sessions = await Session.find(Session.expires_at < datetime.utcnow()).to_list()
            count = 0
            for session in expired_sessions:
                session.is_active = False
                await session.save()
                count += 1
            return count
        except Exception as e:
            print(f"Error cleaning up expired sessions: {e}")
            return 0

# Global session store instance
session_store = MongoDBSessionStore()
