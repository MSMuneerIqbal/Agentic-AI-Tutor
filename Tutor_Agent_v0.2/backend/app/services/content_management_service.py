"""
Content Management Service for Phase 6
Handles content updates, versioning, and dynamic content delivery
"""

import asyncio
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from app.core.database import get_db
from app.core.redis import get_redis_client
from app.services.rag import get_rag_tool

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content."""
    LESSON = "lesson"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    REFERENCE = "reference"
    VIDEO = "video"
    INTERACTIVE = "interactive"

class ContentStatus(Enum):
    """Content status."""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

class UpdatePriority(Enum):
    """Update priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ContentItem:
    """Content item definition."""
    id: str
    title: str
    content_type: ContentType
    topic: str
    content: str
    metadata: Dict[str, Any]
    version: str
    status: ContentStatus
    created_at: datetime
    updated_at: datetime
    author_id: str
    tags: List[str]
    difficulty_level: str
    estimated_time: int  # minutes
    prerequisites: List[str]
    learning_objectives: List[str]

@dataclass
class ContentUpdate:
    """Content update definition."""
    id: str
    content_id: str
    update_type: str  # new, edit, deprecate
    changes: Dict[str, Any]
    reason: str
    priority: UpdatePriority
    created_at: datetime
    applied_at: Optional[datetime] = None
    applied_by: Optional[str] = None

@dataclass
class ContentVersion:
    """Content version information."""
    version: str
    content_id: str
    changes: List[str]
    created_at: datetime
    created_by: str
    is_current: bool

class ContentManagementService:
    """Service for managing learning content and updates."""
    
    def __init__(self):
        self.content_cache_ttl = 3600  # 1 hour
        self.version_history_limit = 10
        self.auto_update_interval = 86400  # 24 hours
    
    async def create_content(
        self, 
        title: str, 
        content_type: ContentType, 
        topic: str, 
        content: str,
        author_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        difficulty_level: str = "medium",
        estimated_time: int = 30,
        prerequisites: Optional[List[str]] = None,
        learning_objectives: Optional[List[str]] = None
    ) -> Optional[ContentItem]:
        """Create new content item."""
        try:
            content_id = f"content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(title.encode()).hexdigest()[:8]}"
            
            content_item = ContentItem(
                id=content_id,
                title=title,
                content_type=content_type,
                topic=topic,
                content=content,
                metadata=metadata or {},
                version="1.0.0",
                status=ContentStatus.DRAFT,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                author_id=author_id,
                tags=tags or [],
                difficulty_level=difficulty_level,
                estimated_time=estimated_time,
                prerequisites=prerequisites or [],
                learning_objectives=learning_objectives or []
            )
            
            # Store content in database
            await self._store_content_item(content_item)
            
            # Update content index
            await self._update_content_index(content_item)
            
            # Invalidate related caches
            await self._invalidate_content_caches(topic)
            
            logger.info(f"Created content item {content_id}: {title}")
            return content_item
            
        except Exception as e:
            logger.error(f"Failed to create content: {e}")
            return None
    
    async def update_content(
        self, 
        content_id: str, 
        updates: Dict[str, Any], 
        author_id: str,
        reason: str = "Content update",
        priority: UpdatePriority = UpdatePriority.MEDIUM
    ) -> Optional[ContentItem]:
        """Update existing content item."""
        try:
            # Get current content
            current_content = await self.get_content_by_id(content_id)
            if not current_content:
                return None
            
            # Create version backup
            await self._create_version_backup(current_content)
            
            # Apply updates
            updated_content = self._apply_content_updates(current_content, updates)
            updated_content.updated_at = datetime.utcnow()
            updated_content.version = self._increment_version(current_content.version)
            
            # Store updated content
            await self._store_content_item(updated_content)
            
            # Create update record
            update_record = ContentUpdate(
                id=f"update_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                content_id=content_id,
                update_type="edit",
                changes=updates,
                reason=reason,
                priority=priority,
                created_at=datetime.utcnow(),
                applied_at=datetime.utcnow(),
                applied_by=author_id
            )
            await self._store_content_update(update_record)
            
            # Update content index
            await self._update_content_index(updated_content)
            
            # Invalidate caches
            await self._invalidate_content_caches(updated_content.topic)
            
            # Update RAG embeddings if content changed significantly
            if self._is_significant_content_change(updates):
                await self._update_rag_embeddings(updated_content)
            
            logger.info(f"Updated content {content_id} by {author_id}")
            return updated_content
            
        except Exception as e:
            logger.error(f"Failed to update content: {e}")
            return None
    
    async def get_content_by_id(self, content_id: str) -> Optional[ContentItem]:
        """Get content item by ID."""
        try:
            # Try cache first
            cached_content = await self._get_cached_content(content_id)
            if cached_content:
                return cached_content
            
            # Get from database
            content_item = await self._get_content_from_db(content_id)
            if content_item:
                # Cache the result
                await self._cache_content(content_item)
            
            return content_item
            
        except Exception as e:
            logger.error(f"Failed to get content by ID: {e}")
            return None
    
    async def get_content_by_topic(self, topic: str, content_type: Optional[ContentType] = None) -> List[ContentItem]:
        """Get content items by topic."""
        try:
            # Try cache first
            cache_key = f"topic_content:{topic}:{content_type.value if content_type else 'all'}"
            cached_content = await self._get_cached_content_list(cache_key)
            if cached_content:
                return cached_content
            
            # Get from database
            content_items = await self._get_content_by_topic_from_db(topic, content_type)
            
            # Cache the results
            await self._cache_content_list(cache_key, content_items)
            
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to get content by topic: {e}")
            return []
    
    async def search_content(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ContentItem]:
        """Search content using full-text search."""
        try:
            # Try cache first
            cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
            cached_results = await self._get_cached_content_list(cache_key)
            if cached_results:
                return cached_results
            
            # Perform search
            search_results = await self._perform_content_search(query, filters)
            
            # Cache results
            await self._cache_content_list(cache_key, search_results)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search content: {e}")
            return []
    
    async def get_content_updates(
        self, 
        since: Optional[datetime] = None,
        priority: Optional[UpdatePriority] = None
    ) -> List[ContentUpdate]:
        """Get content updates since a specific time."""
        try:
            async for db in get_db():
                # Build query
                query = "SELECT * FROM content_updates WHERE 1=1"
                params = {}
                
                if since:
                    query += " AND created_at >= :since"
                    params["since"] = since
                
                if priority:
                    query += " AND priority = :priority"
                    params["priority"] = priority.value
                
                query += " ORDER BY created_at DESC"
                
                result = await db.execute(query, params)
                updates = result.fetchall()
                
                return [self._deserialize_content_update(row) for row in updates]
                
        except Exception as e:
            logger.error(f"Failed to get content updates: {e}")
            return []
    
    async def get_content_versions(self, content_id: str) -> List[ContentVersion]:
        """Get version history for content item."""
        try:
            async for db in get_db():
                query = """
                SELECT * FROM content_versions 
                WHERE content_id = :content_id 
                ORDER BY created_at DESC 
                LIMIT :limit
                """
                result = await db.execute(query, {
                    "content_id": content_id,
                    "limit": self.version_history_limit
                })
                versions = result.fetchall()
                
                return [self._deserialize_content_version(row) for row in versions]
                
        except Exception as e:
            logger.error(f"Failed to get content versions: {e}")
            return []
    
    async def deprecate_content(
        self, 
        content_id: str, 
        reason: str, 
        author_id: str,
        replacement_id: Optional[str] = None
    ) -> bool:
        """Deprecate content item."""
        try:
            # Get current content
            content_item = await self.get_content_by_id(content_id)
            if not content_item:
                return False
            
            # Update status
            content_item.status = ContentStatus.DEPRECATED
            content_item.updated_at = datetime.utcnow()
            content_item.metadata["deprecation_reason"] = reason
            content_item.metadata["deprecated_by"] = author_id
            content_item.metadata["deprecated_at"] = datetime.utcnow().isoformat()
            
            if replacement_id:
                content_item.metadata["replacement_content_id"] = replacement_id
            
            # Store updated content
            await self._store_content_item(content_item)
            
            # Create update record
            update_record = ContentUpdate(
                id=f"deprecate_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                content_id=content_id,
                update_type="deprecate",
                changes={"status": "deprecated", "reason": reason},
                reason=reason,
                priority=UpdatePriority.HIGH,
                created_at=datetime.utcnow(),
                applied_at=datetime.utcnow(),
                applied_by=author_id
            )
            await self._store_content_update(update_record)
            
            # Invalidate caches
            await self._invalidate_content_caches(content_item.topic)
            
            logger.info(f"Deprecated content {content_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deprecate content: {e}")
            return False
    
    async def get_content_analytics(self) -> Dict[str, Any]:
        """Get content analytics and statistics."""
        try:
            async for db in get_db():
                # Get content statistics
                stats_query = await db.execute("""
                    SELECT 
                        content_type,
                        status,
                        COUNT(*) as count
                    FROM content_items 
                    GROUP BY content_type, status
                """)
                content_stats = stats_query.fetchall()
                
                # Get topic distribution
                topic_query = await db.execute("""
                    SELECT topic, COUNT(*) as count
                    FROM content_items 
                    WHERE status = 'published'
                    GROUP BY topic
                    ORDER BY count DESC
                """)
                topic_distribution = topic_query.fetchall()
                
                # Get recent updates
                updates_query = await db.execute("""
                    SELECT COUNT(*) as count
                    FROM content_updates 
                    WHERE created_at >= :week_ago
                """, {"week_ago": datetime.utcnow() - timedelta(days=7)})
                recent_updates = updates_query.scalar() or 0
                
                return {
                    "content_statistics": {
                        row[0]: {row[1]: row[2]} for row in content_stats
                    },
                    "topic_distribution": {
                        row[0]: row[1] for row in topic_distribution
                    },
                    "recent_updates": recent_updates,
                    "total_content_items": sum(row[2] for row in content_stats)
                }
                
        except Exception as e:
            logger.error(f"Failed to get content analytics: {e}")
            return {}
    
    async def auto_update_content(self) -> Dict[str, Any]:
        """Automatically update content based on external sources."""
        try:
            update_results = {
                "updated_items": 0,
                "new_items": 0,
                "errors": 0,
                "details": []
            }
            
            # Check for updates from external sources
            external_updates = await self._check_external_content_updates()
            
            for update in external_updates:
                try:
                    if update["type"] == "new":
                        # Create new content
                        content_item = await self.create_content(
                            title=update["title"],
                            content_type=ContentType(update["content_type"]),
                            topic=update["topic"],
                            content=update["content"],
                            author_id="system",
                            metadata=update.get("metadata", {}),
                            tags=update.get("tags", []),
                            difficulty_level=update.get("difficulty_level", "medium"),
                            estimated_time=update.get("estimated_time", 30)
                        )
                        
                        if content_item:
                            update_results["new_items"] += 1
                            update_results["details"].append(f"Created: {content_item.title}")
                    
                    elif update["type"] == "update":
                        # Update existing content
                        content_item = await self.update_content(
                            content_id=update["content_id"],
                            updates=update["changes"],
                            author_id="system",
                            reason="Automatic update from external source",
                            priority=UpdatePriority.LOW
                        )
                        
                        if content_item:
                            update_results["updated_items"] += 1
                            update_results["details"].append(f"Updated: {content_item.title}")
                
                except Exception as e:
                    update_results["errors"] += 1
                    update_results["details"].append(f"Error: {str(e)}")
            
            logger.info(f"Auto-update completed: {update_results}")
            return update_results
            
        except Exception as e:
            logger.error(f"Failed to auto-update content: {e}")
            return {"error": str(e)}
    
    def _apply_content_updates(self, content_item: ContentItem, updates: Dict[str, Any]) -> ContentItem:
        """Apply updates to content item."""
        updated_content = ContentItem(
            id=content_item.id,
            title=updates.get("title", content_item.title),
            content_type=ContentType(updates.get("content_type", content_item.content_type.value)),
            topic=updates.get("topic", content_item.topic),
            content=updates.get("content", content_item.content),
            metadata={**content_item.metadata, **updates.get("metadata", {})},
            version=content_item.version,
            status=ContentStatus(updates.get("status", content_item.status.value)),
            created_at=content_item.created_at,
            updated_at=content_item.updated_at,
            author_id=content_item.author_id,
            tags=updates.get("tags", content_item.tags),
            difficulty_level=updates.get("difficulty_level", content_item.difficulty_level),
            estimated_time=updates.get("estimated_time", content_item.estimated_time),
            prerequisites=updates.get("prerequisites", content_item.prerequisites),
            learning_objectives=updates.get("learning_objectives", content_item.learning_objectives)
        )
        return updated_content
    
    def _increment_version(self, current_version: str) -> str:
        """Increment version number."""
        try:
            parts = current_version.split(".")
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            patch += 1
            return f"{major}.{minor}.{patch}"
        except:
            return "1.0.1"
    
    def _is_significant_content_change(self, updates: Dict[str, Any]) -> bool:
        """Check if content changes are significant enough to update RAG embeddings."""
        significant_fields = ["content", "title", "learning_objectives", "prerequisites"]
        return any(field in updates for field in significant_fields)
    
    async def _update_rag_embeddings(self, content_item: ContentItem) -> None:
        """Update RAG embeddings for content item."""
        try:
            rag_tool = await get_rag_tool()
            
            # Generate new embedding for updated content
            embedding = await rag_tool.generate_embedding(content_item.content)
            
            if embedding:
                # Update Pinecone index
                await rag_tool.index.upsert(vectors=[{
                    "id": f"content_{content_item.id}",
                    "values": embedding,
                    "metadata": {
                        "text": content_item.content,
                        "source": "Content Management",
                        "content_id": content_item.id,
                        "topic": content_item.topic,
                        "type": content_item.content_type.value,
                        "version": content_item.version
                    }
                }])
                
                logger.info(f"Updated RAG embeddings for content {content_item.id}")
            
        except Exception as e:
            logger.error(f"Failed to update RAG embeddings: {e}")
    
    async def _check_external_content_updates(self) -> List[Dict[str, Any]]:
        """Check for updates from external content sources."""
        # This would typically integrate with external APIs, RSS feeds, etc.
        # For now, return empty list
        return []
    
    async def _store_content_item(self, content_item: ContentItem) -> None:
        """Store content item in database."""
        # This would typically store in a content_items table
        logger.info(f"Stored content item {content_item.id}")
    
    async def _get_content_from_db(self, content_id: str) -> Optional[ContentItem]:
        """Get content item from database."""
        # This would typically retrieve from database
        # For now, return None (would be implemented with actual database storage)
        return None
    
    async def _get_content_by_topic_from_db(self, topic: str, content_type: Optional[ContentType]) -> List[ContentItem]:
        """Get content items by topic from database."""
        # This would typically retrieve from database
        return []
    
    async def _perform_content_search(self, query: str, filters: Optional[Dict[str, Any]]) -> List[ContentItem]:
        """Perform full-text search on content."""
        # This would typically use database full-text search or Elasticsearch
        return []
    
    async def _store_content_update(self, update: ContentUpdate) -> None:
        """Store content update record."""
        logger.info(f"Stored content update {update.id}")
    
    async def _create_version_backup(self, content_item: ContentItem) -> None:
        """Create version backup of content item."""
        logger.info(f"Created version backup for content {content_item.id}")
    
    async def _update_content_index(self, content_item: ContentItem) -> None:
        """Update content search index."""
        logger.info(f"Updated content index for {content_item.id}")
    
    async def _invalidate_content_caches(self, topic: str) -> None:
        """Invalidate content caches for a topic."""
        try:
            redis_client = await get_redis_client()
            cache_keys = await redis_client.keys(f"*{topic}*")
            if cache_keys:
                await redis_client.delete(*cache_keys)
        except Exception as e:
            logger.error(f"Failed to invalidate caches: {e}")
    
    async def _get_cached_content(self, content_id: str) -> Optional[ContentItem]:
        """Get content from cache."""
        try:
            redis_client = await get_redis_client()
            cached_data = await redis_client.get(f"content:{content_id}")
            if cached_data:
                return self._deserialize_content_item(json.loads(cached_data))
        except Exception as e:
            logger.error(f"Failed to get cached content: {e}")
        return None
    
    async def _cache_content(self, content_item: ContentItem) -> None:
        """Cache content item."""
        try:
            redis_client = await get_redis_client()
            await redis_client.setex(
                f"content:{content_item.id}",
                self.content_cache_ttl,
                json.dumps(self._serialize_content_item(content_item))
            )
        except Exception as e:
            logger.error(f"Failed to cache content: {e}")
    
    async def _get_cached_content_list(self, cache_key: str) -> Optional[List[ContentItem]]:
        """Get content list from cache."""
        try:
            redis_client = await get_redis_client()
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return [self._deserialize_content_item(item) for item in json.loads(cached_data)]
        except Exception as e:
            logger.error(f"Failed to get cached content list: {e}")
        return None
    
    async def _cache_content_list(self, cache_key: str, content_items: List[ContentItem]) -> None:
        """Cache content list."""
        try:
            redis_client = await get_redis_client()
            serialized_items = [self._serialize_content_item(item) for item in content_items]
            await redis_client.setex(
                cache_key,
                self.content_cache_ttl,
                json.dumps(serialized_items)
            )
        except Exception as e:
            logger.error(f"Failed to cache content list: {e}")
    
    def _serialize_content_item(self, content_item: ContentItem) -> Dict[str, Any]:
        """Serialize content item for storage."""
        return {
            "id": content_item.id,
            "title": content_item.title,
            "content_type": content_item.content_type.value,
            "topic": content_item.topic,
            "content": content_item.content,
            "metadata": content_item.metadata,
            "version": content_item.version,
            "status": content_item.status.value,
            "created_at": content_item.created_at.isoformat(),
            "updated_at": content_item.updated_at.isoformat(),
            "author_id": content_item.author_id,
            "tags": content_item.tags,
            "difficulty_level": content_item.difficulty_level,
            "estimated_time": content_item.estimated_time,
            "prerequisites": content_item.prerequisites,
            "learning_objectives": content_item.learning_objectives
        }
    
    def _deserialize_content_item(self, data: Dict[str, Any]) -> ContentItem:
        """Deserialize content item from storage."""
        return ContentItem(
            id=data["id"],
            title=data["title"],
            content_type=ContentType(data["content_type"]),
            topic=data["topic"],
            content=data["content"],
            metadata=data["metadata"],
            version=data["version"],
            status=ContentStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            author_id=data["author_id"],
            tags=data["tags"],
            difficulty_level=data["difficulty_level"],
            estimated_time=data["estimated_time"],
            prerequisites=data["prerequisites"],
            learning_objectives=data["learning_objectives"]
        )
    
    def _deserialize_content_update(self, row) -> ContentUpdate:
        """Deserialize content update from database row."""
        return ContentUpdate(
            id=row.id,
            content_id=row.content_id,
            update_type=row.update_type,
            changes=row.changes,
            reason=row.reason,
            priority=UpdatePriority(row.priority),
            created_at=row.created_at,
            applied_at=row.applied_at,
            applied_by=row.applied_by
        )
    
    def _deserialize_content_version(self, row) -> ContentVersion:
        """Deserialize content version from database row."""
        return ContentVersion(
            version=row.version,
            content_id=row.content_id,
            changes=row.changes,
            created_at=row.created_at,
            created_by=row.created_by,
            is_current=row.is_current
        )

# Global instance
_content_management_service = None

async def get_content_management_service() -> ContentManagementService:
    """Get global content management service instance."""
    global _content_management_service
    if _content_management_service is None:
        _content_management_service = ContentManagementService()
    return _content_management_service
