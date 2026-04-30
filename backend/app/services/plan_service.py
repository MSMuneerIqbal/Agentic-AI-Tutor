"""Service for managing study plans and learning paths."""

import uuid
from typing import Any
from datetime import datetime

from app.core.logging import get_logger
from app.models.user_mongo import User
from app.core.session_store import session_store

logger = get_logger(__name__)


class PlanService:
    """Service for managing study plans and learning paths."""

    async def get_user_plans(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get user's study plans.
        
        Args:
            user_id: User identifier (email or user ID)
            limit: Maximum number of plans to return
            
        Returns:
            List of study plans
        """
        try:
            # Find user
            user = await User.find_one(User.email == user_id)
            if not user:
                try:
                    user = await User.get(user_id)
                except:
                    pass
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return []
            
            # Get plans from session store
            plans_data = await session_store.get_session(f"plans:{user.email}")
            
            if plans_data:
                # Return as list if it's a single plan
                if isinstance(plans_data, dict):
                    plans = [plans_data]
                else:
                    plans = plans_data
                
                # Apply limit
                return plans[:limit]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get user plans: {str(e)}")
            raise

    async def create_study_plan(
        self,
        user_id: str,
        plan_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create a new study plan for user.
        
        Args:
            user_id: User identifier (email or user ID)
            plan_data: Plan data including topics, learning_style, etc.
            
        Returns:
            Created study plan dictionary
        """
        try:
            # Find user
            user = await User.find_one(User.email == user_id)
            if not user:
                try:
                    user = await User.get(user_id)
                except:
                    pass
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return {}
            
            # Create plan — field names match what PlanningAgent sends:
            # {"summary", "goals", "learning_style", "full_plan"}
            plan_id = str(uuid.uuid4())
            goals = plan_data.get("goals", "")
            plan = {
                "id": plan_id,
                "user_id": str(user.id),
                "user_email": user.email,
                "summary": plan_data.get("summary", goals or "Study plan"),
                "full_plan": plan_data.get("full_plan", ""),
                "goals": goals,
                "learning_style": plan_data.get("learning_style", "visual"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            # Store plan in session store
            existing_plans = await session_store.get_session(f"plans:{user.email}")
            if existing_plans:
                if isinstance(existing_plans, list):
                    plans = existing_plans
                else:
                    plans = [existing_plans]
            else:
                plans = []
            
            plans.append(plan)
            await session_store.set_session(f"plans:{user.email}", plans, ttl=86400)
            
            logger.info(f"Created study plan: {plan_id} for user: {user_id}")
            return plan
            
        except Exception as e:
            logger.error(f"Failed to create study plan: {str(e)}")
            raise

    async def get_plan_stats(self) -> dict[str, Any]:
        """
        Get study plan statistics across all users.
        
        Returns:
            Plan statistics dictionary
        """
        try:
            # This would require scanning all users' plans
            # For now, return mock data
            return {
                "total_plans": 0,
                "total_topics": 0,
                "total_hours": 0,
                "average_topics_per_plan": 0.0,
                "average_hours_per_plan": 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get plan stats: {str(e)}")
            raise

    async def update_progress(
        self,
        user_id: str,
        topic_id: str,
        progress_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update user's progress on a specific topic.
        
        Args:
            user_id: User identifier (email or user ID)
            topic_id: Topic identifier
            progress_data: Progress data
            
        Returns:
            Updated progress dictionary
        """
        try:
            # Find user
            user = await User.find_one(User.email == user_id)
            if not user:
                try:
                    user = await User.get(user_id)
                except:
                    pass
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return {}
            
            # Update progress in session store
            progress_key = f"progress:{user.email}:{topic_id}"
            await session_store.set_session(progress_key, progress_data, ttl=86400)
            
            logger.info(f"Updated progress for user: {user_id}, topic: {topic_id}")
            return progress_data
            
        except Exception as e:
            logger.error(f"Failed to update progress: {str(e)}")
            raise

    async def get_latest_plan(
        self,
        user_id: str,
    ) -> dict[str, Any] | None:
        """
        Get user's latest study plan.
        
        Args:
            user_id: User identifier (email or user ID)
            
        Returns:
            Latest study plan dictionary or None
        """
        try:
            # Find user
            user = await User.find_one(User.email == user_id)
            if not user:
                try:
                    user = await User.get(user_id)
                except:
                    pass
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return None
            
            # Get latest plan from session store
            plans = await session_store.get_session(f"plans:{user.email}")
            
            if plans and isinstance(plans, list) and len(plans) > 0:
                # Return the most recent plan (first in list)
                return plans[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest plan: {str(e)}")
            raise

    async def get_plan_by_id(
        self,
        plan_id: str,
    ) -> dict[str, Any] | None:
        """
        Get study plan by ID.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Study plan dictionary or None
        """
        try:
            # Get plan from session store
            plan = await session_store.get_session(f"plan:{plan_id}")
            
            if plan:
                return plan
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get plan by ID: {str(e)}")
            raise

    async def update_plan_progress(
        self,
        plan_id: str,
        topic_id: str,
        progress_data: dict[str, Any],
    ) -> bool:
        """
        Update progress for a topic in a study plan.
        
        Args:
            plan_id: Plan identifier
            topic_id: Topic identifier
            progress_data: Progress data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update progress in session store
            progress_key = f"progress:{plan_id}:{topic_id}"
            await session_store.set_session(progress_key, progress_data, ttl=86400)
            
            logger.info(f"Updated progress for plan: {plan_id}, topic: {topic_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update plan progress: {str(e)}")
            return False

    async def delete_plan(
        self,
        plan_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete a study plan.
        
        Args:
            plan_id: Plan identifier
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete plan from session store
            await session_store.delete_session(f"plan:{plan_id}")
            
            logger.info(f"Deleted plan: {plan_id} for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete plan: {str(e)}")
            return False


# Create service instance
plan_service = PlanService()