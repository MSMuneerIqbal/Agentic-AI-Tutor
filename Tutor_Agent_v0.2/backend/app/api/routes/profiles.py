"""Profile management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.services.profile_service import profile_service

logger = get_logger(__name__)
metrics = get_metrics_collector()

router = APIRouter()


class ProfileResponse(BaseModel):
    """User profile response."""
    
    user_id: str
    email: str
    display_name: str
    created_at: str
    learning_style: str | None = None
    assessment_confidence: float | None = None
    last_assessment: str | None = None


class AssessmentHistoryResponse(BaseModel):
    """Assessment history response."""
    
    assessments: list[dict[str, str | int]]


class LearningStyleStatsResponse(BaseModel):
    """Learning style statistics response."""
    
    total_assessments: int
    style_counts: dict[str, int]
    style_percentages: dict[str, float]
    most_common_style: str | None


@router.get("/profiles/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user profile with learning style information.
    
    Returns user profile including latest assessment result.
    """
    try:
        profile = await profile_service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Retrieved profile for user: {user_id}")
        
        return ProfileResponse(**profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@router.get("/profiles/{user_id}/assessments", response_model=AssessmentHistoryResponse)
async def get_assessment_history(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's assessment history.
    
    Returns list of previous assessments with learning styles.
    """
    try:
        assessments = await profile_service.get_assessment_history(user_id)
        
        logger.info(f"Retrieved {len(assessments)} assessments for user: {user_id}")
        
        return AssessmentHistoryResponse(assessments=assessments)
        
    except Exception as e:
        logger.error(f"Failed to get assessment history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assessment history")


@router.get("/profiles/stats/learning-styles", response_model=LearningStyleStatsResponse)
async def get_learning_style_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get learning style distribution statistics.
    
    Returns aggregated statistics about learning styles across all users.
    """
    try:
        stats = await profile_service.get_learning_style_stats()
        
        logger.info(f"Retrieved learning style stats: {stats['total_assessments']} total assessments")
        
        return LearningStyleStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get learning style stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@router.put("/profiles/{user_id}/preferences")
async def update_user_preferences(
    user_id: str,
    preferences: dict[str, str],
    db: AsyncSession = Depends(get_db),
):
    """
    Update user learning preferences.
    
    Updates user's learning preferences and stores them with their profile.
    """
    try:
        success = await profile_service.update_user_preferences(user_id, preferences, db)
        
        if not success:
            raise HTTPException(status_code=404, detail="User or assessment not found")
        
        logger.info(f"Updated preferences for user: {user_id}")
        
        return {"message": "Preferences updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")
