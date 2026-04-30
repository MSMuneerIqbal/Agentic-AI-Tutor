"""RAG API endpoints for content retrieval and live web search."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])


class ContentRequest(BaseModel):
    query: str
    agent_type: str = "general"
    include_web: bool = False


class TopicRequest(BaseModel):
    topic: str
    agent_type: str = "general"


class LessonRequest(BaseModel):
    topic: str
    learning_style: str = "V"


class ContentResponse(BaseModel):
    rag_content: list
    web_results: list
    agent_type: str
    query: str
    error: Optional[str] = None


class LessonResponse(BaseModel):
    rag_content: list
    web_results: list
    best_practices: list
    topic: str
    learning_style: str
    error: Optional[str] = None


@router.get("/health")
async def rag_health():
    return {"status": "healthy", "service": "rag"}


@router.post("/content", response_model=ContentResponse)
async def get_content(request: ContentRequest, rag_service=Depends(get_rag_service)):
    try:
        result = await rag_service.get_agent_content(
            agent_type=request.agent_type,
            query=request.query,
            include_web=request.include_web,
        )
        return ContentResponse(**result)
    except Exception as exc:
        logger.error(f"Failed to get content: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/topic", response_model=ContentResponse)
async def get_topic_content(request: TopicRequest, rag_service=Depends(get_rag_service)):
    try:
        result = await rag_service.get_agent_content(
            agent_type=request.agent_type,
            query=request.topic,
        )
        return ContentResponse(**result)
    except Exception as exc:
        logger.error(f"Failed to get topic content: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/lesson", response_model=LessonResponse)
async def get_lesson_content(request: LessonRequest, rag_service=Depends(get_rag_service)):
    try:
        result = await rag_service.get_tutor_lesson_content(
            topic=request.topic,
            learning_style=request.learning_style,
        )
        return LessonResponse(**result)
    except Exception as exc:
        logger.error(f"Failed to get lesson content: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/quiz/{topic}")
async def get_quiz_content(topic: str, rag_service=Depends(get_rag_service)):
    try:
        return await rag_service.get_quiz_content(topic)
    except Exception as exc:
        logger.error(f"Failed to get quiz content: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/planning")
async def get_planning_content(
    goals: str = Query(..., description="Learning goals"),
    interests: str = Query(..., description="Student interests"),
    rag_service=Depends(get_rag_service),
):
    try:
        return await rag_service.get_planning_content(goals, interests)
    except Exception as exc:
        logger.error(f"Failed to get planning content: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/assessment/{topic}")
async def get_assessment_content(topic: str, rag_service=Depends(get_rag_service)):
    try:
        return await rag_service.get_assessment_content(topic)
    except Exception as exc:
        logger.error(f"Failed to get assessment content: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/live-examples/{topic}")
async def get_live_examples(
    topic: str,
    context: str = Query(default="", description="Additional search context"),
    max_results: int = Query(default=3, description="Maximum results"),
    rag_service=Depends(get_rag_service),
):
    try:
        from app.tools.web_search import get_web_search_tool
        web_tool = await get_web_search_tool()
        query = f"{topic} {context}".strip() if context else topic
        results = await web_tool.search(query=query, max_results=max_results)
        return {
            "topic": topic,
            "context": context,
            "examples": [
                {
                    "title": r.title,
                    "url": r.url,
                    "content": r.content,
                    "relevance_score": r.relevance_score,
                    "source": r.source,
                }
                for r in results
            ],
        }
    except Exception as exc:
        logger.error(f"Failed to get live examples: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
