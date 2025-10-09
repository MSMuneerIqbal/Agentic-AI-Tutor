"""Service for managing user profiles and assessment results."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.assessment import AssessmentResult, LearningStyle
from app.models.user import User

logger = get_logger(__name__)


class ProfileService:
    """Service for managing user profiles and learning preferences."""

    async def get_user_profile(
        self,
        user_id: str,
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        """
        Get user profile with latest assessment result.
        
        Args:
            user_id: User identifier
            db: Database session (optional)
            
        Returns:
            User profile dictionary
        """
        if db is None:
            async for db_session in get_db():
                return await self.get_user_profile(user_id, db_session)
        
        try:
            # Get user
            result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return {}
            
            # Get latest assessment result
            assessment_result = await self.get_latest_assessment(user_id, db)
            
            profile = {
                "user_id": str(user.id),
                "email": user.email,
                "display_name": user.display_name,
                "created_at": user.created_at.isoformat(),
                "learning_style": assessment_result.get("style") if assessment_result else None,
                "assessment_confidence": assessment_result.get("confidence") if assessment_result else None,
                "last_assessment": assessment_result.get("created_at") if assessment_result else None,
            }
            
            logger.debug(f"Retrieved user profile: {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            raise

    async def get_latest_assessment(
        self,
        user_id: str,
        db: AsyncSession | None = None,
    ) -> dict[str, Any] | None:
        """
        Get user's latest assessment result.
        
        Args:
            user_id: User identifier
            db: Database session (optional)
            
        Returns:
            Latest assessment result or None
        """
        if db is None:
            async for db_session in get_db():
                return await self.get_latest_assessment(user_id, db_session)
        
        try:
            result = await db.execute(
                select(AssessmentResult)
                .where(AssessmentResult.user_id == uuid.UUID(user_id))
                .order_by(AssessmentResult.created_at.desc())
                .limit(1)
            )
            assessment = result.scalar_one_or_none()
            
            if not assessment:
                return None
            
            return {
                "id": str(assessment.id),
                "style": assessment.style.value,
                "answers": assessment.answers,
                "created_at": assessment.created_at.isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get latest assessment: {str(e)}")
            return None

    async def get_assessment_history(
        self,
        user_id: str,
        limit: int = 10,
        db: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get user's assessment history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of assessments to return
            db: Database session (optional)
            
        Returns:
            List of assessment results
        """
        if db is None:
            async for db_session in get_db():
                return await self.get_assessment_history(user_id, limit, db_session)
        
        try:
            result = await db.execute(
                select(AssessmentResult)
                .where(AssessmentResult.user_id == uuid.UUID(user_id))
                .order_by(AssessmentResult.created_at.desc())
                .limit(limit)
            )
            assessments = result.scalars().all()
            
            return [
                {
                    "id": str(assessment.id),
                    "style": assessment.style.value,
                    "created_at": assessment.created_at.isoformat(),
                    "question_count": len(assessment.answers) if assessment.answers else 0,
                }
                for assessment in assessments
            ]
            
        except Exception as e:
            logger.error(f"Failed to get assessment history: {str(e)}")
            return []

    async def update_user_preferences(
        self,
        user_id: str,
        preferences: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> bool:
        """
        Update user learning preferences.
        
        Args:
            user_id: User identifier
            preferences: Learning preferences dictionary
            db: Database session (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if db is None:
            async for db_session in get_db():
                return await self.update_user_preferences(user_id, preferences, db_session)
        
        try:
            # For now, we'll store preferences in the latest assessment
            # In a full implementation, you might have a separate preferences table
            latest_assessment = await self.get_latest_assessment(user_id, db)
            
            if latest_assessment:
                # Update the assessment with preferences
                result = await db.execute(
                    select(AssessmentResult)
                    .where(AssessmentResult.id == uuid.UUID(latest_assessment["id"]))
                )
                assessment = result.scalar_one_or_none()
                
                if assessment:
                    # Add preferences to answers
                    if not assessment.answers:
                        assessment.answers = {}
                    
                    assessment.answers["preferences"] = preferences
                    await db.commit()
                    
                    logger.info(f"Updated user preferences: {user_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update user preferences: {str(e)}")
            await db.rollback()
            return False

    async def get_learning_style_stats(
        self,
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        """
        Get learning style distribution statistics.
        
        Args:
            db: Database session (optional)
            
        Returns:
            Learning style statistics
        """
        if db is None:
            async for db_session in get_db():
                return await self.get_learning_style_stats(db_session)
        
        try:
            # Get all assessment results
            result = await db.execute(select(AssessmentResult))
            assessments = result.scalars().all()
            
            # Count learning styles
            style_counts = {"V": 0, "A": 0, "R": 0, "K": 0}
            total_assessments = len(assessments)
            
            for assessment in assessments:
                style = assessment.style.value
                if style in style_counts:
                    style_counts[style] += 1
            
            # Calculate percentages
            style_percentages = {}
            for style, count in style_counts.items():
                percentage = (count / total_assessments * 100) if total_assessments > 0 else 0
                style_percentages[style] = round(percentage, 1)
            
            return {
                "total_assessments": total_assessments,
                "style_counts": style_counts,
                "style_percentages": style_percentages,
                "most_common_style": max(style_counts, key=style_counts.get) if total_assessments > 0 else None,
            }
            
        except Exception as e:
            logger.error(f"Failed to get learning style stats: {str(e)}")
            return {
                "total_assessments": 0,
                "style_counts": {"V": 0, "A": 0, "R": 0, "K": 0},
                "style_percentages": {"V": 0, "A": 0, "R": 0, "K": 0},
                "most_common_style": None,
            }


# Global profile service instance
profile_service = ProfileService()
