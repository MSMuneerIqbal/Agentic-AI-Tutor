"""Profile management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.services.profile_service import profile_service

logger = get_logger(__name__)
metrics = get_metrics_collector()

router = APIRouter()


class ProfileResponse(BaseModel):
    user_id: str
    email: str
    display_name: str
    created_at: str
    learning_style: str | None = None
    assessment_confidence: float | None = None
    last_assessment: str | None = None


class AssessmentHistoryResponse(BaseModel):
    assessments: list[dict]


class LearningStyleStatsResponse(BaseModel):
    total_assessments: int
    style_counts: dict[str, int]
    style_percentages: dict[str, float]
    most_common_style: str | None


@router.get("/profiles/{user_id}", response_model=ProfileResponse)
async def get_user_profile(user_id: str):
    try:
        profile = await profile_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        return ProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to get user profile: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@router.get("/profiles/{user_id}/assessments", response_model=AssessmentHistoryResponse)
async def get_assessment_history(user_id: str, limit: int = 10):
    try:
        assessments = await profile_service.get_assessment_history(user_id)
        return AssessmentHistoryResponse(assessments=assessments)
    except Exception as exc:
        logger.error(f"Failed to get assessment history: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assessment history")


@router.get("/profiles/stats/learning-styles", response_model=LearningStyleStatsResponse)
async def get_learning_style_stats():
    try:
        stats = await profile_service.get_learning_style_stats()
        return LearningStyleStatsResponse(**stats)
    except Exception as exc:
        logger.error(f"Failed to get learning style stats: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@router.put("/profiles/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: dict[str, str]):
    try:
        updated = await profile_service.update_user_profile(user_id, preferences)
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Preferences updated successfully"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to update user preferences: {exc}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")
