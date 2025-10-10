"""
Phase 6 API Routes
Advanced features endpoints for multi-user support, analytics, collaboration, etc.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.multi_user_service import get_multi_user_service, UserSession, SystemMetrics
from app.services.analytics_service import get_analytics_service, LearningProgress, PerformanceMetrics, SystemAnalytics
from app.services.cache_service import get_cache_service
from app.services.adaptive_learning_service import get_adaptive_learning_service, AdaptivePath, LearningRecommendation
from app.services.collaboration_service import get_collaboration_service, CollaborationSession, StudyGroup
from app.services.advanced_assessment_service import get_advanced_assessment_service, AssessmentSession, AssessmentResult
from app.services.content_management_service import get_content_management_service, ContentItem, ContentUpdate
from app.services.monitoring_service import get_monitoring_service, Alert, HealthCheck
from app.middleware.rate_limiting import RateLimitingMiddleware

router = APIRouter(prefix="/api/v1/phase6", tags=["Phase 6 - Advanced Features"])

# Multi-User Support Endpoints
@router.post("/users/sessions", response_model=Dict[str, Any])
async def create_user_session(
    user_id: str = Query(..., description="User ID"),
    initial_state: str = Query("greeting", description="Initial session state")
):
    """Create a new user session."""
    try:
        multi_user_service = await get_multi_user_service()
        session = await multi_user_service.create_user_session(user_id, initial_state)
        
        if session:
            return {
                "success": True,
                "session": {
                    "id": session.session_id,
                    "user_id": session.user_id,
                    "state": session.state.value,
                    "current_topic": session.current_topic,
                    "learning_style": session.learning_style,
                    "progress": session.progress,
                    "is_active": session.is_active
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/sessions/{session_id}", response_model=Dict[str, Any])
async def get_user_session(session_id: str = Path(..., description="Session ID")):
    """Get user session by ID."""
    try:
        multi_user_service = await get_multi_user_service()
        session = await multi_user_service.get_user_session(session_id)
        
        if session:
            return {
                "success": True,
                "session": {
                    "id": session.session_id,
                    "user_id": session.user_id,
                    "state": session.state.value,
                    "current_topic": session.current_topic,
                    "learning_style": session.learning_style,
                    "progress": session.progress,
                    "last_activity": session.last_activity.isoformat(),
                    "is_active": session.is_active
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/sessions/{session_id}", response_model=Dict[str, Any])
async def update_user_session(
    session_id: str = Path(..., description="Session ID"),
    updates: Dict[str, Any] = None
):
    """Update user session."""
    try:
        multi_user_service = await get_multi_user_service()
        success = await multi_user_service.update_user_session(session_id, updates or {})
        
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/active", response_model=Dict[str, Any])
async def get_active_users():
    """Get all active user sessions."""
    try:
        multi_user_service = await get_multi_user_service()
        active_sessions = await multi_user_service.get_active_users()
        
        return {
            "success": True,
            "active_users": len(active_sessions),
            "sessions": [
                {
                    "id": session.session_id,
                    "user_id": session.user_id,
                    "state": session.state.value,
                    "current_topic": session.current_topic,
                    "last_activity": session.last_activity.isoformat()
                }
                for session in active_sessions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/metrics", response_model=Dict[str, Any])
async def get_system_metrics():
    """Get system performance metrics."""
    try:
        multi_user_service = await get_multi_user_service()
        metrics = await multi_user_service.get_system_metrics()
        
        return {
            "success": True,
            "metrics": {
                "active_users": metrics.active_users,
                "total_sessions": metrics.total_sessions,
                "average_session_duration": metrics.average_session_duration,
                "system_load": metrics.system_load,
                "memory_usage": metrics.memory_usage
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@router.get("/analytics/progress/{user_id}", response_model=Dict[str, Any])
async def get_user_learning_progress(user_id: str = Path(..., description="User ID")):
    """Get user learning progress."""
    try:
        analytics_service = await get_analytics_service()
        progress = await analytics_service.get_user_learning_progress(user_id)
        
        if progress:
            return {
                "success": True,
                "progress": {
                    "user_id": progress.user_id,
                    "current_level": progress.current_level.value,
                    "topics_completed": progress.topics_completed,
                    "total_topics": progress.total_topics,
                    "completion_percentage": progress.completion_percentage,
                    "average_quiz_score": progress.average_quiz_score,
                    "total_study_time": progress.total_study_time,
                    "learning_streak": progress.learning_streak,
                    "last_activity": progress.last_activity.isoformat()
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User progress not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/performance/{user_id}", response_model=Dict[str, Any])
async def get_user_performance_metrics(user_id: str = Path(..., description="User ID")):
    """Get user performance metrics."""
    try:
        analytics_service = await get_analytics_service()
        metrics = await analytics_service.get_user_performance_metrics(user_id)
        
        if metrics:
            return {
                "success": True,
                "metrics": {
                    "user_id": metrics.user_id,
                    "quiz_scores": metrics.quiz_scores,
                    "lesson_completion_rate": metrics.lesson_completion_rate,
                    "average_session_duration": metrics.average_session_duration,
                    "topic_mastery": metrics.topic_mastery,
                    "learning_velocity": metrics.learning_velocity,
                    "retention_rate": metrics.retention_rate
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User performance metrics not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/system", response_model=Dict[str, Any])
async def get_system_analytics():
    """Get system-wide analytics."""
    try:
        analytics_service = await get_analytics_service()
        analytics = await analytics_service.get_system_analytics()
        
        return {
            "success": True,
            "analytics": {
                "total_users": analytics.total_users,
                "active_users": analytics.active_users,
                "total_sessions": analytics.total_sessions,
                "average_session_duration": analytics.average_session_duration,
                "popular_topics": analytics.popular_topics,
                "learning_style_distribution": analytics.learning_style_distribution,
                "system_engagement": analytics.system_engagement
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/insights/{user_id}", response_model=Dict[str, Any])
async def get_learning_insights(user_id: str = Path(..., description="User ID")):
    """Get personalized learning insights."""
    try:
        analytics_service = await get_analytics_service()
        insights = await analytics_service.get_learning_insights(user_id)
        
        return {
            "success": True,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cache Management Endpoints
@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats():
    """Get cache statistics."""
    try:
        cache_service = await get_cache_service()
        stats = await cache_service.get_cache_stats()
        
        return {
            "success": True,
            "cache_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear", response_model=Dict[str, Any])
async def clear_cache(cache_type: str = Query("all", description="Cache type to clear")):
    """Clear cache entries."""
    try:
        cache_service = await get_cache_service()
        deleted_count = await cache_service.clear_cache(cache_type)
        
        return {
            "success": True,
            "deleted_entries": deleted_count,
            "cache_type": cache_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/optimize", response_model=Dict[str, Any])
async def optimize_cache():
    """Optimize cache by removing least recently used items."""
    try:
        cache_service = await get_cache_service()
        results = await cache_service.optimize_cache()
        
        return {
            "success": True,
            "optimization_results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Adaptive Learning Endpoints
@router.post("/adaptive/path", response_model=Dict[str, Any])
async def create_adaptive_path(
    user_id: str = Query(..., description="User ID"),
    topic: str = Query(..., description="Learning topic")
):
    """Create adaptive learning path for user."""
    try:
        adaptive_service = await get_adaptive_learning_service()
        path = await adaptive_service.create_adaptive_path(user_id)
        
        if path:
            return {
                "success": True,
                "path": {
                    "user_id": path.user_id,
                    "current_objective": path.current_objective,
                    "path_sequence": path.path_sequence,
                    "difficulty_progression": [d.value for d in path.difficulty_progression],
                    "content_adaptations": path.content_adaptations,
                    "estimated_completion": path.estimated_completion.isoformat(),
                    "success_probability": path.success_probability
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create adaptive path")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adaptive/recommendations/{user_id}", response_model=Dict[str, Any])
async def get_learning_recommendations(user_id: str = Path(..., description="User ID")):
    """Get personalized learning recommendations."""
    try:
        adaptive_service = await get_adaptive_learning_service()
        recommendations = await adaptive_service.get_learning_recommendations(user_id)
        
        return {
            "success": True,
            "recommendations": [
                {
                    "objective_id": rec.objective_id,
                    "reason": rec.reason,
                    "priority": rec.priority,
                    "estimated_benefit": rec.estimated_benefit,
                    "content_suggestions": rec.content_suggestions
                }
                for rec in recommendations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Collaboration Endpoints
@router.post("/collaboration/sessions", response_model=Dict[str, Any])
async def create_collaboration_session(
    host_id: str = Query(..., description="Host user ID"),
    session_type: str = Query(..., description="Session type"),
    title: str = Query(..., description="Session title"),
    description: str = Query(..., description="Session description"),
    topic: str = Query(..., description="Session topic"),
    max_participants: int = Query(10, description="Maximum participants")
):
    """Create a collaboration session."""
    try:
        collaboration_service = await get_collaboration_service()
        session = await collaboration_service.create_collaboration_session(
            host_id, session_type, title, description, topic, max_participants
        )
        
        if session:
            return {
                "success": True,
                "session": {
                    "id": session.id,
                    "type": session.type.value,
                    "title": session.title,
                    "description": session.description,
                    "host_id": session.host_id,
                    "participants": session.participants,
                    "max_participants": session.max_participants,
                    "topic": session.topic,
                    "status": session.status.value,
                    "created_at": session.created_at.isoformat()
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create collaboration session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collaboration/sessions/{session_id}/join", response_model=Dict[str, Any])
async def join_collaboration_session(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Query(..., description="User ID")
):
    """Join a collaboration session."""
    try:
        collaboration_service = await get_collaboration_service()
        success = await collaboration_service.join_collaboration_session(session_id, user_id)
        
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collaboration/sessions/available", response_model=Dict[str, Any])
async def get_available_sessions(
    topic: str = Query(..., description="Topic to filter by"),
    user_id: str = Query(..., description="User ID")
):
    """Get available collaboration sessions for a topic."""
    try:
        collaboration_service = await get_collaboration_service()
        sessions = await collaboration_service.get_available_sessions(topic, user_id)
        
        return {
            "success": True,
            "sessions": [
                {
                    "id": session.id,
                    "type": session.type.value,
                    "title": session.title,
                    "description": session.description,
                    "host_id": session.host_id,
                    "participants": len(session.participants),
                    "max_participants": session.max_participants,
                    "topic": session.topic,
                    "status": session.status.value,
                    "created_at": session.created_at.isoformat()
                }
                for session in sessions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collaboration/sessions/{session_id}/messages", response_model=Dict[str, Any])
async def send_collaboration_message(
    session_id: str = Path(..., description="Session ID"),
    sender_id: str = Query(..., description="Sender user ID"),
    sender_name: str = Query(..., description="Sender name"),
    message_type: str = Query("text", description="Message type"),
    content: str = Query(..., description="Message content")
):
    """Send a message in a collaboration session."""
    try:
        collaboration_service = await get_collaboration_service()
        success = await collaboration_service.send_collaboration_message(
            session_id, sender_id, sender_name, message_type, content
        )
        
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collaboration/sessions/{session_id}/messages", response_model=Dict[str, Any])
async def get_collaboration_messages(
    session_id: str = Path(..., description="Session ID"),
    limit: int = Query(50, description="Number of messages to retrieve")
):
    """Get messages from a collaboration session."""
    try:
        collaboration_service = await get_collaboration_service()
        messages = await collaboration_service.get_collaboration_messages(session_id, limit)
        
        return {
            "success": True,
            "messages": [
                {
                    "id": message.id,
                    "sender_id": message.sender_id,
                    "sender_name": message.sender_name,
                    "message_type": message.message_type,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat()
                }
                for message in messages
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Advanced Assessment Endpoints
@router.post("/assessment/adaptive", response_model=Dict[str, Any])
async def create_adaptive_assessment(
    user_id: str = Query(..., description="User ID"),
    topic: str = Query(..., description="Assessment topic"),
    assessment_type: str = Query("adaptive", description="Assessment type")
):
    """Create an adaptive assessment session."""
    try:
        assessment_service = await get_advanced_assessment_service()
        session = await assessment_service.create_adaptive_assessment(user_id, topic, assessment_type)
        
        if session:
            return {
                "success": True,
                "session": {
                    "id": session.id,
                    "user_id": session.user_id,
                    "assessment_type": session.assessment_type.value,
                    "topic": session.topic,
                    "questions_count": len(session.questions),
                    "current_question_index": session.current_question_index,
                    "time_limit": session.time_limit,
                    "start_time": session.start_time.isoformat()
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create assessment session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/{session_id}/submit", response_model=Dict[str, Any])
async def submit_assessment_answer(
    session_id: str = Path(..., description="Session ID"),
    question_id: str = Query(..., description="Question ID"),
    answer: str = Query(..., description="User answer"),
    time_taken: int = Query(..., description="Time taken in seconds")
):
    """Submit an answer for an assessment question."""
    try:
        assessment_service = await get_advanced_assessment_service()
        result = await assessment_service.submit_answer(session_id, question_id, answer, time_taken)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/{session_id}/complete", response_model=Dict[str, Any])
async def complete_assessment(session_id: str = Path(..., description="Session ID")):
    """Complete an assessment and get results."""
    try:
        assessment_service = await get_advanced_assessment_service()
        result = await assessment_service.complete_assessment(session_id)
        
        if result:
            return {
                "success": True,
                "result": {
                    "session_id": result.session_id,
                    "user_id": result.user_id,
                    "topic": result.topic,
                    "total_questions": result.total_questions,
                    "correct_answers": result.correct_answers,
                    "score": result.score,
                    "time_taken": result.time_taken,
                    "knowledge_gaps": result.knowledge_gaps,
                    "strengths": result.strengths,
                    "recommendations": result.recommendations,
                    "next_steps": result.next_steps
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to complete assessment")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assessment/analytics/{user_id}", response_model=Dict[str, Any])
async def get_assessment_analytics(user_id: str = Path(..., description="User ID")):
    """Get assessment analytics for a user."""
    try:
        assessment_service = await get_advanced_assessment_service()
        analytics = await assessment_service.get_assessment_analytics(user_id)
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content Management Endpoints
@router.post("/content", response_model=Dict[str, Any])
async def create_content(
    title: str = Query(..., description="Content title"),
    content_type: str = Query(..., description="Content type"),
    topic: str = Query(..., description="Content topic"),
    content: str = Query(..., description="Content body"),
    author_id: str = Query(..., description="Author user ID")
):
    """Create new content item."""
    try:
        content_service = await get_content_management_service()
        content_item = await content_service.create_content(
            title, content_type, topic, content, author_id
        )
        
        if content_item:
            return {
                "success": True,
                "content": {
                    "id": content_item.id,
                    "title": content_item.title,
                    "content_type": content_item.content_type.value,
                    "topic": content_item.topic,
                    "version": content_item.version,
                    "status": content_item.status.value,
                    "created_at": content_item.created_at.isoformat(),
                    "author_id": content_item.author_id
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create content")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{content_id}", response_model=Dict[str, Any])
async def get_content(content_id: str = Path(..., description="Content ID")):
    """Get content item by ID."""
    try:
        content_service = await get_content_management_service()
        content_item = await content_service.get_content_by_id(content_id)
        
        if content_item:
            return {
                "success": True,
                "content": {
                    "id": content_item.id,
                    "title": content_item.title,
                    "content_type": content_item.content_type.value,
                    "topic": content_item.topic,
                    "content": content_item.content,
                    "version": content_item.version,
                    "status": content_item.status.value,
                    "created_at": content_item.created_at.isoformat(),
                    "updated_at": content_item.updated_at.isoformat(),
                    "author_id": content_item.author_id,
                    "tags": content_item.tags,
                    "difficulty_level": content_item.difficulty_level,
                    "estimated_time": content_item.estimated_time
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Content not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/topic/{topic}", response_model=Dict[str, Any])
async def get_content_by_topic(
    topic: str = Path(..., description="Topic name"),
    content_type: Optional[str] = Query(None, description="Filter by content type")
):
    """Get content items by topic."""
    try:
        content_service = await get_content_management_service()
        content_items = await content_service.get_content_by_topic(topic, content_type)
        
        return {
            "success": True,
            "content_items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "content_type": item.content_type.value,
                    "topic": item.topic,
                    "version": item.version,
                    "status": item.status.value,
                    "created_at": item.created_at.isoformat(),
                    "author_id": item.author_id,
                    "tags": item.tags,
                    "difficulty_level": item.difficulty_level,
                    "estimated_time": item.estimated_time
                }
                for item in content_items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/analytics", response_model=Dict[str, Any])
async def get_content_analytics():
    """Get content analytics and statistics."""
    try:
        content_service = await get_content_management_service()
        analytics = await content_service.get_content_analytics()
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Monitoring Endpoints
@router.get("/monitoring/health", response_model=Dict[str, Any])
async def get_system_health():
    """Get system health status."""
    try:
        monitoring_service = await get_monitoring_service()
        health = await monitoring_service.get_system_health()
        
        return {
            "success": True,
            "health": health
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/alerts", response_model=Dict[str, Any])
async def get_active_alerts(level: Optional[str] = Query(None, description="Alert level filter")):
    """Get active alerts."""
    try:
        monitoring_service = await get_monitoring_service()
        alerts = await monitoring_service.get_active_alerts(level)
        
        return {
            "success": True,
            "alerts": [
                {
                    "id": alert.id,
                    "name": alert.name,
                    "level": alert.level.value,
                    "message": alert.message,
                    "source": alert.source,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/dashboard", response_model=Dict[str, Any])
async def get_metrics_dashboard(time_range: str = Query("1h", description="Time range for metrics")):
    """Get metrics dashboard data."""
    try:
        monitoring_service = await get_monitoring_service()
        dashboard = await monitoring_service.get_metrics_dashboard(time_range)
        
        return {
            "success": True,
            "dashboard": dashboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitoring/alerts/{alert_id}/resolve", response_model=Dict[str, Any])
async def resolve_alert(
    alert_id: str = Path(..., description="Alert ID"),
    resolved_by: str = Query("system", description="Who resolved the alert")
):
    """Resolve an alert."""
    try:
        monitoring_service = await get_monitoring_service()
        success = await monitoring_service.resolve_alert(alert_id, resolved_by)
        
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
