"""Service for managing user profiles and assessment results."""

import uuid
from typing import Any
from datetime import datetime

from app.core.logging import get_logger
from app.models.user_mongo import User
from app.core.session_store import session_store

logger = get_logger(__name__)


class ProfileService:
    """Service for managing user profiles and learning preferences."""

    async def get_user_profile(
        self,
        user_id: str,
    ) -> dict[str, Any]:
        """
        Get user profile with latest assessment result.
        
        Args:
            user_id: User identifier (email or user ID)
            
        Returns:
            User profile dictionary
        """
        try:
            # Try to find user by email first, then by ID
            user = await User.find_one(User.email == user_id)
            if not user:
                # Try by ID if email lookup fails
                try:
                    user = await User.get(user_id)
                except:
                    pass
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return {}
            
            # Get latest assessment result from session store
            assessment_data = await session_store.get_session(f"assessment:{user.email}")
            learning_style = None
            assessment_confidence = None
            last_assessment = None
            
            if assessment_data:
                learning_style = assessment_data.get("learning_style")
                assessment_confidence = assessment_data.get("confidence", 0.0)
                last_assessment = assessment_data.get("completed_at")
            
            return {
                "user_id": str(user.id),
                "email": user.email,
                "display_name": user.display_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "learning_style": learning_style,
                "assessment_confidence": assessment_confidence,
                "last_assessment": last_assessment
            }
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            raise

    async def update_user_profile(
        self,
        user_id: str,
        profile_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update user profile data.
        
        Args:
            user_id: User identifier (email or user ID)
            profile_data: Profile data to update
            
        Returns:
            Updated user profile dictionary
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
            
            # Update user fields if provided
            if "learning_style" in profile_data:
                # Store assessment data in session store
                assessment_data = {
                    "learning_style": profile_data["learning_style"],
                    "confidence": profile_data.get("assessment_confidence", 0.0),
                    "completed_at": datetime.utcnow().isoformat()
                }
                await session_store.set_session(f"assessment:{user.email}", assessment_data, ttl=86400)
            
            # Update user document if needed
            if "display_name" in profile_data:
                user.display_name = profile_data["display_name"]
                await user.save()
            
            logger.info(f"Updated user profile: {user_id}")
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {str(e)}")
            raise

    async def get_assessment_history(
        self,
        user_id: str,
    ) -> list[dict[str, Any]]:
        """
        Get user's assessment history.
        
        Args:
            user_id: User identifier (email or user ID)
            
        Returns:
            List of assessment results
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
            
            # Get assessment data from session store
            assessment_data = await session_store.get_session(f"assessment:{user.email}")
            
            if assessment_data:
                return [assessment_data]  # Return as list for compatibility
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get assessment history: {str(e)}")
            raise

    async def get_learning_style_stats(self) -> dict[str, Any]:
        """
        Get learning style statistics across all users.
        
        Returns:
            Learning style statistics dictionary
        """
        try:
            # This would require scanning all users' assessment data
            # For now, return mock data
            return {
                "total_assessments": 0,
                "style_counts": {
                    "visual": 0,
                    "auditory": 0,
                    "reading": 0,
                    "kinesthetic": 0
                },
                "style_percentages": {
                    "visual": 0.0,
                    "auditory": 0.0,
                    "reading": 0.0,
                    "kinesthetic": 0.0
                },
                "most_common_style": None
            }
            
        except Exception as e:
            logger.error(f"Failed to get learning style stats: {str(e)}")
            raise


# Create service instance
profile_service = ProfileService()