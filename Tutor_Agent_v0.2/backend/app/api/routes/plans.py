"""Plan management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.services.plan_service import plan_service

logger = get_logger(__name__)
metrics = get_metrics_collector()

router = APIRouter()


class PlanResponse(BaseModel):
    """Study plan response."""
    
    id: str
    summary: str
    topics: list[dict]
    created_at: str
    updated_at: str
    topic_count: int
    total_hours: int


class PlanListResponse(BaseModel):
    """Study plan list response."""
    
    plans: list[dict]


class PlanStatsResponse(BaseModel):
    """Plan statistics response."""
    
    total_plans: int
    total_topics: int
    total_hours: int
    average_topics_per_plan: float
    average_hours_per_plan: float


class ProgressUpdateRequest(BaseModel):
    """Progress update request."""
    
    topic_id: str
    progress_data: dict


@router.get("/plans/{user_id}", response_model=PlanListResponse)
async def get_user_plans(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's study plans.
    
    Returns list of study plans for the specified user.
    """
    try:
        plans = await plan_service.get_user_plans(user_id, limit, db)
        
        logger.info(f"Retrieved {len(plans)} plans for user: {user_id}")
        
        return PlanListResponse(plans=plans)
        
    except Exception as e:
        logger.error(f"Failed to get user plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve plans")


@router.get("/plans/{user_id}/latest", response_model=PlanResponse)
async def get_latest_plan(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's latest study plan.
    
    Returns the most recent study plan for the specified user.
    """
    try:
        plan = await plan_service.get_latest_plan(user_id, db)
        
        if not plan:
            raise HTTPException(status_code=404, detail="No study plan found")
        
        logger.info(f"Retrieved latest plan for user: {user_id}")
        
        return PlanResponse(**plan)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve latest plan")


@router.get("/plans/plan/{plan_id}", response_model=PlanResponse)
async def get_plan_by_id(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get study plan by ID.
    
    Returns the study plan with the specified ID.
    """
    try:
        plan = await plan_service.get_plan_by_id(plan_id, db)
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        logger.info(f"Retrieved plan: {plan_id}")
        
        return PlanResponse(**plan)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plan by ID: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve plan")


@router.put("/plans/{plan_id}/progress")
async def update_plan_progress(
    plan_id: str,
    request: ProgressUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update progress for a topic in a study plan.
    
    Updates the progress information for a specific topic.
    """
    try:
        success = await plan_service.update_plan_progress(
            plan_id, 
            request.topic_id, 
            request.progress_data, 
            db
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Plan or topic not found")
        
        logger.info(f"Updated progress for topic {request.topic_id} in plan {plan_id}")
        
        return {"message": "Progress updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update plan progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update progress")


@router.get("/plans/stats/overview", response_model=PlanStatsResponse)
async def get_plan_statistics(
    db: AsyncSession = Depends(get_db),
):
    """
    Get study plan statistics.
    
    Returns aggregated statistics about study plans across all users.
    """
    try:
        stats = await plan_service.get_plan_statistics(db)
        
        logger.info(f"Retrieved plan statistics: {stats['total_plans']} total plans")
        
        return PlanStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get plan statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a study plan.
    
    Deletes the specified study plan for the user.
    """
    try:
        success = await plan_service.delete_plan(plan_id, user_id, db)
        
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found or access denied")
        
        logger.info(f"Deleted plan {plan_id} for user {user_id}")
        
        return {"message": "Plan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete plan")
