"""
RAG API endpoints for content retrieval and live examples

These endpoints provide access to RAG content and Tavily MCP integration
for all agents in the Tutor GPT system.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])


class ContentRequest(BaseModel):
    """Request model for content retrieval"""
    query: str
    agent_type: str = "general"
    include_live_examples: bool = False


class TopicRequest(BaseModel):
    """Request model for topic-specific content"""
    topic: str
    agent_type: str = "general"


class LessonRequest(BaseModel):
    """Request model for lesson content"""
    topic: str
    learning_style: str = "visual"


class ContentResponse(BaseModel):
    """Response model for content retrieval"""
    rag_content: list
    live_examples: list
    agent_type: str
    query: str
    error: Optional[str] = None


class LessonResponse(BaseModel):
    """Response model for lesson content"""
    rag_content: list
    live_examples: list
    best_practices: list
    troubleshooting: list
    topic: str
    learning_style: str
    content_type: str
    error: Optional[str] = None


@router.get("/health")
async def rag_health():
    """Health check for RAG service"""
    return {"status": "healthy", "service": "rag"}


@router.post("/content", response_model=ContentResponse)
async def get_content(
    request: ContentRequest,
    rag_service = Depends(get_rag_service)
):
    """
    Get content for a specific agent type
    
    Args:
        request: Content request with query and agent type
        rag_service: RAG service dependency
        
    Returns:
        Content response with RAG content and live examples
    """
    try:
        result = await rag_service.get_agent_content(
            agent_type=request.agent_type,
            query=request.query,
            include_live_examples=request.include_live_examples
        )
        
        return ContentResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to get content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topic", response_model=ContentResponse)
async def get_topic_content(
    request: TopicRequest,
    rag_service = Depends(get_rag_service)
):
    """
    Get content for a specific topic
    
    Args:
        request: Topic request with topic name and agent type
        rag_service: RAG service dependency
        
    Returns:
        Content response with topic-specific content
    """
    try:
        result = await rag_service.get_topic_content(
            topic=request.topic,
            agent_type=request.agent_type
        )
        
        return ContentResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to get topic content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lesson", response_model=LessonResponse)
async def get_lesson_content(
    request: LessonRequest,
    rag_service = Depends(get_rag_service)
):
    """
    Get comprehensive lesson content for Tutor agent
    
    Args:
        request: Lesson request with topic and learning style
        rag_service: RAG service dependency
        
    Returns:
        Lesson response with comprehensive content
    """
    try:
        result = await rag_service.get_tutor_lesson_content(
            topic=request.topic,
            learning_style=request.learning_style
        )
        
        return LessonResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to get lesson content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quiz/{topic}")
async def get_quiz_content(
    topic: str,
    rag_service = Depends(get_rag_service)
):
    """
    Get quiz-worthy content for a topic
    
    Args:
        topic: Topic to get quiz content for
        rag_service: RAG service dependency
        
    Returns:
        Quiz content response
    """
    try:
        result = await rag_service.get_quiz_content(topic)
        return result
        
    except Exception as e:
        logger.error(f"Failed to get quiz content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/planning")
async def get_planning_content(
    goals: str = Query(..., description="Learning goals"),
    interests: str = Query(..., description="Student interests"),
    rag_service = Depends(get_rag_service)
):
    """
    Get content for Planning agent
    
    Args:
        goals: Learning goals
        interests: Student interests
        rag_service: RAG service dependency
        
    Returns:
        Planning content response
    """
    try:
        result = await rag_service.get_planning_content(goals, interests)
        return result
        
    except Exception as e:
        logger.error(f"Failed to get planning content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assessment/{topic}")
async def get_assessment_content(
    topic: str,
    rag_service = Depends(get_rag_service)
):
    """
    Get content for Assessment agent
    
    Args:
        topic: Topic to assess
        rag_service: RAG service dependency
        
    Returns:
        Assessment content response
    """
    try:
        result = await rag_service.get_assessment_content(topic)
        return result
        
    except Exception as e:
        logger.error(f"Failed to get assessment content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live-examples/{topic}")
async def get_live_examples(
    topic: str,
    context: str = Query(default="Docker Kubernetes", description="Search context"),
    max_results: int = Query(default=3, description="Maximum results"),
    rag_service = Depends(get_rag_service)
):
    """
    Get live examples for a topic using Tavily MCP
    
    Args:
        topic: Topic to get examples for
        context: Search context
        max_results: Maximum number of results
        rag_service: RAG service dependency
        
    Returns:
        Live examples response
    """
    try:
        # Get Tavily client directly for live examples
        from app.tools.tavily_mcp import get_tavily_client
        tavily_client = await get_tavily_client()
        examples = await tavily_client.search_live_examples(
            topic=topic,
            context=context,
            max_results=max_results
        )
        
        return {
            "topic": topic,
            "context": context,
            "examples": [
                {
                    "title": ex.title,
                    "url": ex.url,
                    "content": ex.content,
                    "relevance_score": ex.relevance_score,
                    "published_date": ex.published_date,
                    "source": ex.source
                }
                for ex in examples
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get live examples: {e}")
        raise HTTPException(status_code=500, detail=str(e))
