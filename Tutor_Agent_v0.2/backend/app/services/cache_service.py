"""
Advanced Caching Service for Phase 6
Implements intelligent caching for performance optimization
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Cache configuration."""
    ttl: int  # Time to live in seconds
    max_size: int  # Maximum cache size
    enable_compression: bool = False

class CacheService:
    """Advanced caching service for performance optimization."""
    
    def __init__(self):
        self.default_ttl = 3600  # 1 hour
        self.cache_configs = {
            "rag_content": CacheConfig(ttl=1800, max_size=1000),  # 30 minutes
            "user_profile": CacheConfig(ttl=3600, max_size=500),  # 1 hour
            "study_plan": CacheConfig(ttl=7200, max_size=200),    # 2 hours
            "quiz_questions": CacheConfig(ttl=900, max_size=500), # 15 minutes
            "system_metrics": CacheConfig(ttl=300, max_size=100), # 5 minutes
            "agent_responses": CacheConfig(ttl=600, max_size=1000), # 10 minutes
        }
    
    async def get(self, key: str, cache_type: str = "default") -> Optional[Any]:
        """Get value from cache."""
        try:
            redis_client = await get_redis_client()
            cache_key = self._build_cache_key(key, cache_type)
            
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                # Update access time for LRU
                await redis_client.expire(cache_key, self._get_ttl(cache_type))
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get from cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, cache_type: str = "default", ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            redis_client = await get_redis_client()
            cache_key = self._build_cache_key(key, cache_type)
            
            # Serialize value
            serialized_value = json.dumps(value, default=str)
            
            # Set TTL
            cache_ttl = ttl or self._get_ttl(cache_type)
            
            # Store in cache
            await redis_client.setex(cache_key, cache_ttl, serialized_value)
            
            # Update cache statistics
            await self._update_cache_stats(cache_type, "set")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False
    
    async def delete(self, key: str, cache_type: str = "default") -> bool:
        """Delete value from cache."""
        try:
            redis_client = await get_redis_client()
            cache_key = self._build_cache_key(key, cache_type)
            
            result = await redis_client.delete(cache_key)
            await self._update_cache_stats(cache_type, "delete")
            
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete from cache: {e}")
            return False
    
    async def clear_cache(self, cache_type: str = "all") -> int:
        """Clear cache entries."""
        try:
            redis_client = await get_redis_client()
            
            if cache_type == "all":
                # Clear all cache keys
                keys = await redis_client.keys("cache:*")
            else:
                # Clear specific cache type
                keys = await redis_client.keys(f"cache:{cache_type}:*")
            
            if keys:
                deleted_count = await redis_client.delete(*keys)
                logger.info(f"Cleared {deleted_count} cache entries for type: {cache_type}")
                return deleted_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0
    
    async def get_or_set(self, key: str, factory_func, cache_type: str = "default", ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function."""
        try:
            # Try to get from cache first
            cached_value = await self.get(key, cache_type)
            if cached_value is not None:
                await self._update_cache_stats(cache_type, "hit")
                return cached_value
            
            # Cache miss - generate value
            value = await factory_func() if asyncio.iscoroutinefunction(factory_func) else factory_func()
            
            # Store in cache
            await self.set(key, value, cache_type, ttl)
            await self._update_cache_stats(cache_type, "miss")
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get or set cache: {e}")
            # Fallback to factory function
            return await factory_func() if asyncio.iscoroutinefunction(factory_func) else factory_func()
    
    async def cache_rag_content(self, query: str, agent_type: str, content: List[Dict[str, Any]]) -> bool:
        """Cache RAG content with intelligent key generation."""
        try:
            # Create cache key based on query and agent type
            cache_key = f"rag:{agent_type}:{self._hash_query(query)}"
            return await self.set(cache_key, content, "rag_content")
            
        except Exception as e:
            logger.error(f"Failed to cache RAG content: {e}")
            return False
    
    async def get_cached_rag_content(self, query: str, agent_type: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached RAG content."""
        try:
            cache_key = f"rag:{agent_type}:{self._hash_query(query)}"
            return await self.get(cache_key, "rag_content")
            
        except Exception as e:
            logger.error(f"Failed to get cached RAG content: {e}")
            return None
    
    async def cache_user_profile(self, user_id: str, profile: Dict[str, Any]) -> bool:
        """Cache user profile data."""
        try:
            cache_key = f"profile:{user_id}"
            return await self.set(cache_key, profile, "user_profile")
            
        except Exception as e:
            logger.error(f"Failed to cache user profile: {e}")
            return False
    
    async def get_cached_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user profile."""
        try:
            cache_key = f"profile:{user_id}"
            return await self.get(cache_key, "user_profile")
            
        except Exception as e:
            logger.error(f"Failed to get cached user profile: {e}")
            return None
    
    async def cache_agent_response(self, agent_name: str, user_input: str, context: Dict[str, Any], response: Dict[str, Any]) -> bool:
        """Cache agent responses for similar inputs."""
        try:
            # Create cache key based on agent, input, and context
            context_hash = self._hash_context(context)
            cache_key = f"agent:{agent_name}:{self._hash_query(user_input)}:{context_hash}"
            return await self.set(cache_key, response, "agent_responses")
            
        except Exception as e:
            logger.error(f"Failed to cache agent response: {e}")
            return False
    
    async def get_cached_agent_response(self, agent_name: str, user_input: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached agent response."""
        try:
            context_hash = self._hash_context(context)
            cache_key = f"agent:{agent_name}:{self._hash_query(user_input)}:{context_hash}"
            return await self.get(cache_key, "agent_responses")
            
        except Exception as e:
            logger.error(f"Failed to get cached agent response: {e}")
            return None
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            redis_client = await get_redis_client()
            
            stats = {}
            for cache_type in self.cache_configs.keys():
                # Get hit/miss counts
                hit_key = f"cache_stats:{cache_type}:hits"
                miss_key = f"cache_stats:{cache_type}:misses"
                
                hits = await redis_client.get(hit_key) or 0
                misses = await redis_client.get(miss_key) or 0
                
                total_requests = int(hits) + int(misses)
                hit_rate = (int(hits) / total_requests * 100) if total_requests > 0 else 0
                
                # Get cache size
                cache_keys = await redis_client.keys(f"cache:{cache_type}:*")
                cache_size = len(cache_keys)
                
                stats[cache_type] = {
                    "hits": int(hits),
                    "misses": int(misses),
                    "hit_rate": round(hit_rate, 2),
                    "cache_size": cache_size,
                    "max_size": self.cache_configs[cache_type].max_size
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache by removing least recently used items."""
        try:
            optimization_results = {}
            
            for cache_type, config in self.cache_configs.items():
                redis_client = await get_redis_client()
                cache_keys = await redis_client.keys(f"cache:{cache_type}:*")
                
                if len(cache_keys) > config.max_size:
                    # Sort by access time (LRU)
                    key_access_times = []
                    for key in cache_keys:
                        ttl = await redis_client.ttl(key)
                        key_access_times.append((key, ttl))
                    
                    # Sort by TTL (lower TTL = more recently accessed)
                    key_access_times.sort(key=lambda x: x[1])
                    
                    # Remove excess keys
                    keys_to_remove = key_access_times[config.max_size:]
                    if keys_to_remove:
                        keys_to_delete = [key for key, _ in keys_to_remove]
                        deleted_count = await redis_client.delete(*keys_to_delete)
                        optimization_results[cache_type] = {
                            "removed": deleted_count,
                            "remaining": len(cache_keys) - deleted_count
                        }
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to optimize cache: {e}")
            return {}
    
    def _build_cache_key(self, key: str, cache_type: str) -> str:
        """Build cache key with type prefix."""
        return f"cache:{cache_type}:{key}"
    
    def _get_ttl(self, cache_type: str) -> int:
        """Get TTL for cache type."""
        return self.cache_configs.get(cache_type, CacheConfig(ttl=self.default_ttl, max_size=1000)).ttl
    
    def _hash_query(self, query: str) -> str:
        """Create hash for query string."""
        return hashlib.md5(query.encode()).hexdigest()[:16]
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Create hash for context dictionary."""
        context_str = json.dumps(context, sort_keys=True, default=str)
        return hashlib.md5(context_str.encode()).hexdigest()[:16]
    
    async def _update_cache_stats(self, cache_type: str, operation: str) -> None:
        """Update cache statistics."""
        try:
            redis_client = await get_redis_client()
            stats_key = f"cache_stats:{cache_type}:{operation}s"
            await redis_client.incr(stats_key)
            await redis_client.expire(stats_key, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Failed to update cache stats: {e}")

# Global instance
_cache_service = None

async def get_cache_service() -> CacheService:
    """Get global cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
