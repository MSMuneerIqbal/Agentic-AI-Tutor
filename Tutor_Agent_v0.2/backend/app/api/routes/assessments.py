"""Assessment endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.profile_service import profile_service

logger = get_logger(__name__)

router = APIRouter()


class AssessmentHistoryResponse(BaseModel):
    """Response model for assessment history."""
    assessments: List[dict]


class LearningStyleStatsResponse(BaseModel):
    """Response model for learning style statistics."""
    total_assessments: int
    style_counts: dict
    style_percentages: dict
    most_common_style: Optional[str]


@router.get("/assessments/{user_id}/history", response_model=AssessmentHistoryResponse)
async def get_assessment_history(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of assessments to return"),
):
    """
    Get user's assessment history.
    
    Returns list of previous assessments with learning styles.
    """
    try:
        assessments = await profile_service.get_assessment_history(user_id)
        
        # Limit results if needed
        if len(assessments) > limit:
            assessments = assessments[:limit]
        
        logger.info(f"Retrieved {len(assessments)} assessments for user: {user_id}")
        
        return AssessmentHistoryResponse(assessments=assessments)
        
    except Exception as e:
        logger.error(f"Failed to get assessment history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assessment history")


@router.get("/assessments/stats/learning-styles", response_model=LearningStyleStatsResponse)
async def get_learning_style_stats():
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
        raise HTTPException(status_code=500, detail="Failed to retrieve learning style statistics")
