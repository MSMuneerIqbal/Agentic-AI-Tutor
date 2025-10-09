"""Service for managing study plans."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.plan import Plan
from app.models.user import User

logger = get_logger(__name__)


class PlanService:
    """Service for managing study plans."""

    async def get_user_plans(
        self,
        user_id: str,
        limit: int = 10,
        db: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get user's study plans.
        
        Args:
            user_id: User identifier
            limit: Maximum number of plans to return
            db: Database session (optional)
            
        Returns:
            List of study plans
        """
        if db is None:
            async for db_session in get_db():
                return await self.get_user_plans(user_id, limit, db_session)
        
        try:
            if db is None:
                raise ValueError("Database session is required")
            result = await db.execute(
                select(Plan)
                .where(Plan.user_id == uuid.UUID(user_id))
                .order_by(Plan.created_at.desc())
                .limit(limit)
            )
            plans = result.scalars().all()
            
            return [
                {
                    "id": str(plan.id),
                    "summary": plan.summary,
                    "topics": plan.topics,
                    "created_at": plan.created_at.isoformat(),
                    "updated_at": plan.updated_at.isoformat(),
                    "topic_count": len(plan.topics) if plan.topics else 0,
                    "total_hours": sum(topic.get("estimated_hours", 0) for topic in plan.topics) if plan.topics else 0,
                }
                for plan in plans
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user plans: {str(e)}")
            return []

    async def get_latest_plan(
        self,
        user_id: str,
        db: AsyncSession | None = None,
    ) -> dict[str, Any] | None:
        """
        Get user's latest study plan.
        
        Args:
            user_id: User identifier
            db: Database session (optional)
            
        Returns:
            Latest study plan or None
        """
        if db is None:
            async for db_session in get_db():
                return await self.get_latest_plan(user_id, db_session)
        
        try:
            if db is None:
                raise ValueError("Database session is required")
            result = await db.execute(
                select(Plan)
                .where(Plan.user_id == uuid.UUID(user_id))
                .order_by(Plan.created_at.desc())
                .limit(1)
            )
            plan = result.scalar_one_or_none()
            
            if not plan:
                return None
            
            return {
                "id": str(plan.id),
                "summary": plan.summary,
                "topics": plan.topics,
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat(),
                "topic_count": len(plan.topics) if plan.topics else 0,
                "total_hours": sum(topic.get("estimated_hours", 0) for topic in plan.topics) if plan.topics else 0,
            }
            
        except Exception as e:
            logger.error(f"Failed to get latest plan: {str(e)}")
            return None

    async def get_plan_by_id(
        self,
        plan_id: str,
        db: AsyncSession | None = None,
    ) -> dict[str, Any] | None:
        """
        Get study plan by ID.
        
        Args:
            plan_id: Plan identifier
            db: Database session (optional)
            
        Returns:
            Study plan or None
        """
        if db is None:
            async for db_session in get_db():
                return await self.get_plan_by_id(plan_id, db_session)
        
        try:
            result = await db.execute(
                select(Plan).where(Plan.id == uuid.UUID(plan_id))
            )
            plan = result.scalar_one_or_none()
            
            if not plan:
                return None
            
            return {
                "id": str(plan.id),
                "user_id": str(plan.user_id),
                "summary": plan.summary,
                "topics": plan.topics,
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat(),
                "topic_count": len(plan.topics) if plan.topics else 0,
                "total_hours": sum(topic.get("estimated_hours", 0) for topic in plan.topics) if plan.topics else 0,
            }
            
        except Exception as e:
            logger.error(f"Failed to get plan by ID: {str(e)}")
            return None

    async def update_plan_progress(
        self,
        plan_id: str,
        topic_id: str,
        progress_data: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> bool:
        """
        Update progress for a specific topic in a plan.
        
        Args:
            plan_id: Plan identifier
            topic_id: Topic identifier
            progress_data: Progress information
            db: Database session (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if db is None:
            async for db_session in get_db():
                return await self.update_plan_progress(plan_id, topic_id, progress_data, db_session)
        
        try:
            if db is None:
                raise ValueError("Database session is required")
            result = await db.execute(
                select(Plan).where(Plan.id == uuid.UUID(plan_id))
            )
            plan = result.scalar_one_or_none()
            
            if not plan:
                return False
            
            # Update progress for the specific topic
            if plan.topics:
                for topic in plan.topics:
                    if topic.get("id") == topic_id:
                        topic["progress"] = progress_data
                        break
                
                # Update the plan
                plan.topics = plan.topics
                await db.commit()
                
                logger.info(f"Updated progress for topic {topic_id} in plan {plan_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update plan progress: {str(e)}")
            await db.rollback()
            return False

    async def get_plan_statistics(
        self,
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        """
        Get study plan statistics.
        
        Args:
            db: Database session (optional)
            
        Returns:
            Plan statistics
        """
        if db is None:
            async for db_session in get_db():
                return await self.get_plan_statistics(db_session)
        
        try:
            if db is None:
                raise ValueError("Database session is required")
            # Get all plans
            result = await db.execute(select(Plan))
            plans = result.scalars().all()
            
            total_plans = len(plans)
            total_topics = sum(len(plan.topics) if plan.topics else 0 for plan in plans)
            total_hours = sum(
                sum(topic.get("estimated_hours", 0) for topic in plan.topics) 
                if plan.topics else 0 
                for plan in plans
            )
            
            # Calculate average topics per plan
            avg_topics = total_topics / total_plans if total_plans > 0 else 0
            
            # Calculate average hours per plan
            avg_hours = total_hours / total_plans if total_plans > 0 else 0
            
            return {
                "total_plans": total_plans,
                "total_topics": total_topics,
                "total_hours": total_hours,
                "average_topics_per_plan": round(avg_topics, 1),
                "average_hours_per_plan": round(avg_hours, 1),
            }
            
        except Exception as e:
            logger.error(f"Failed to get plan statistics: {str(e)}")
            return {
                "total_plans": 0,
                "total_topics": 0,
                "total_hours": 0,
                "average_topics_per_plan": 0,
                "average_hours_per_plan": 0,
            }

    async def delete_plan(
        self,
        plan_id: str,
        user_id: str,
        db: AsyncSession | None = None,
    ) -> bool:
        """
        Delete a study plan.
        
        Args:
            plan_id: Plan identifier
            user_id: User identifier (for authorization)
            db: Database session (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if db is None:
            async for db_session in get_db():
                return await self.delete_plan(plan_id, user_id, db_session)
        
        try:
            if db is None:
                raise ValueError("Database session is required")
            result = await db.execute(
                select(Plan)
                .where(Plan.id == uuid.UUID(plan_id))
                .where(Plan.user_id == uuid.UUID(user_id))
            )
            plan = result.scalar_one_or_none()
            
            if not plan:
                return False
            
            await db.delete(plan)
            await db.commit()
            
            logger.info(f"Deleted plan {plan_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete plan: {str(e)}")
            await db.rollback()
            return False


# Global plan service instance
plan_service = PlanService()
