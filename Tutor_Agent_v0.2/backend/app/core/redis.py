"""Redis client and session store utilities."""

import json
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()


class RedisClient:
    """Redis client wrapper for session and cache management."""

    def __init__(self):
        """Initialize Redis client."""
        self._client: Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self._client = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()

    @property
    def client(self) -> Redis:
        """Get Redis client instance."""
        if not self._client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    # Session management
    async def set_session(
        self, session_id: str, data: dict[str, Any], ttl: int = 3600
    ) -> None:
        """
        Store session data in Redis.

        Args:
            session_id: Session ID
            data: Session data dictionary
            ttl: Time to live in seconds (default 1 hour)
        """
        key = f"session:{session_id}"
        await self.client.setex(key, ttl, json.dumps(data))

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        Retrieve session data from Redis.

        Args:
            session_id: Session ID

        Returns:
            Session data dictionary or None if not found
        """
        key = f"session:{session_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def delete_session(self, session_id: str) -> None:
        """
        Delete session data from Redis.

        Args:
            session_id: Session ID
        """
        key = f"session:{session_id}"
        await self.client.delete(key)

    async def extend_session(self, session_id: str, ttl: int = 3600) -> None:
        """
        Extend session TTL.

        Args:
            session_id: Session ID
            ttl: Time to live in seconds
        """
        key = f"session:{session_id}"
        await self.client.expire(key, ttl)

    # Cache management
    async def cache_set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set cache value.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds
        """
        await self.client.setex(key, ttl, json.dumps(value))

    async def cache_get(self, key: str) -> Any | None:
        """
        Get cache value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def cache_delete(self, key: str) -> None:
        """
        Delete cache value.

        Args:
            key: Cache key
        """
        await self.client.delete(key)

    # Counter management (for rate limiting, metrics)
    async def increment_counter(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter.

        Args:
            key: Counter key
            amount: Amount to increment by

        Returns:
            New counter value
        """
        return await self.client.incrby(key, amount)

    async def get_counter(self, key: str) -> int:
        """
        Get counter value.

        Args:
            key: Counter key

        Returns:
            Counter value (0 if not found)
        """
        value = await self.client.get(key)
        return int(value) if value else 0

    # List operations (for recent messages, etc.)
    async def list_push(self, key: str, value: Any, max_length: int = 100) -> None:
        """
        Push value to list and trim to max length.

        Args:
            key: List key
            value: Value to push
            max_length: Maximum list length
        """
        await self.client.lpush(key, json.dumps(value))
        await self.client.ltrim(key, 0, max_length - 1)

    async def list_get(self, key: str, start: int = 0, end: int = -1) -> list[Any]:
        """
        Get list items.

        Args:
            key: List key
            start: Start index
            end: End index

        Returns:
            List of items
        """
        items = await self.client.lrange(key, start, end)
        return [json.loads(item) for item in items]

    # Set operations (for active sessions tracking)
    async def set_add(self, key: str, *values: str) -> int:
        """
        Add values to a set.

        Args:
            key: Set key
            *values: Values to add

        Returns:
            Number of values added
        """
        return await self.client.sadd(key, *values)

    async def set_remove(self, key: str, *values: str) -> int:
        """
        Remove values from a set.

        Args:
            key: Set key
            *values: Values to remove

        Returns:
            Number of values removed
        """
        return await self.client.srem(key, *values)

    async def set_cardinality(self, key: str) -> int:
        """
        Get set cardinality (number of members).

        Args:
            key: Set key

        Returns:
            Number of members in set
        """
        return await self.client.scard(key)

    # Generic Redis operations
    async def setex(self, key: str, time: int, value: str) -> None:
        """
        Set key with expiration time.

        Args:
            key: Key name
            time: Expiration time in seconds
            value: Value to set
        """
        await self.client.setex(key, time, value)

    async def get(self, key: str) -> str | None:
        """
        Get value by key.

        Args:
            key: Key name

        Returns:
            Value or None if not found
        """
        return await self.client.get(key)


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    Dependency for getting Redis client.

    Returns:
        RedisClient instance
    """
    return redis_client


def get_redis_client() -> RedisClient:
    """
    Get Redis client instance (synchronous version).

    Returns:
        RedisClient instance
    """
    return redis_client

