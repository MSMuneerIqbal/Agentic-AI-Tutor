"""Plan management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.services.plan_service import plan_service

logger = get_logger(__name__)
metrics = get_metrics_collector()

router = APIRouter()


class PlanResponse(BaseModel):
    id: str
    summary: str
    goals: str = ""
    full_plan: str = ""
    learning_style: str = "visual"
    created_at: str
    updated_at: str


class PlanListResponse(BaseModel):
    plans: list[dict]


class PlanStatsResponse(BaseModel):
    total_plans: int
    total_topics: int
    total_hours: int
    average_topics_per_plan: float
    average_hours_per_plan: float


class ProgressUpdateRequest(BaseModel):
    topic_id: str
    progress_data: dict


@router.get("/plans/{user_id}", response_model=PlanListResponse)
async def get_user_plans(user_id: str, limit: int = 10):
    try:
        plans = await plan_service.get_user_plans(user_id, limit)
        return PlanListResponse(plans=plans)
    except Exception as exc:
        logger.error(f"Failed to get user plans: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve plans")


@router.get("/plans/{user_id}/latest")
async def get_latest_plan(user_id: str):
    try:
        plan = await plan_service.get_latest_plan(user_id)
        if not plan:
            raise HTTPException(status_code=404, detail="No study plan found")
        return plan
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to get latest plan: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve latest plan")


@router.get("/plans/plan/{plan_id}")
async def get_plan_by_id(plan_id: str):
    try:
        plan = await plan_service.get_plan_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return plan
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to get plan by ID: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve plan")


@router.put("/plans/{plan_id}/progress")
async def update_plan_progress(plan_id: str, request: ProgressUpdateRequest):
    try:
        success = await plan_service.update_plan_progress(plan_id, request.topic_id, request.progress_data)
        if not success:
            raise HTTPException(status_code=404, detail="Plan or topic not found")
        return {"message": "Progress updated successfully"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to update plan progress: {exc}")
        raise HTTPException(status_code=500, detail="Failed to update progress")


@router.get("/plans/stats/overview", response_model=PlanStatsResponse)
async def get_plan_statistics():
    try:
        stats = await plan_service.get_plan_stats()
        return PlanStatsResponse(**stats)
    except Exception as exc:
        logger.error(f"Failed to get plan statistics: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, user_id: str):
    try:
        success = await plan_service.delete_plan(plan_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found or access denied")
        return {"message": "Plan deleted successfully"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to delete plan: {exc}")
        raise HTTPException(status_code=500, detail="Failed to delete plan")
