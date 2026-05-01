"""RAG API endpoints for content retrieval and live web search."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
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


# ── Knowledge Base Management ──────────────────────────────────────────────────

ALLOWED_CONTENT_TYPES = {
    "lesson", "example", "explanation", "tutorial",
    "overview", "structure", "curriculum", "roadmap",
    "concept", "definition", "comparison", "best_practice",
    "command", "configuration", "introduction", "welcome",
}


class UploadTextRequest(BaseModel):
    title: str
    content: str
    content_type: str
    topic: str
    source: str = "manual_upload"


@router.post("/documents", status_code=201)
async def upload_text_content(request: UploadTextRequest, rag_service=Depends(get_rag_service)):
    """Upload plain text content into Pinecone."""
    if not request.title.strip() or not request.content.strip():
        raise HTTPException(status_code=422, detail="title and content are required")
    if request.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid content_type. Choose from: {sorted(ALLOWED_CONTENT_TYPES)}")
    try:
        result = await rag_service.upload_content(
            title=request.title.strip(),
            content=request.content.strip(),
            content_type=request.content_type,
            topic=request.topic.strip(),
            source=request.source or "manual_upload",
        )
        return result
    except Exception as exc:
        logger.error(f"upload_text_content failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/documents/file", status_code=201)
async def upload_file_content(
    file: UploadFile = File(...),
    title: str = Form(...),
    content_type: str = Form(...),
    topic: str = Form(...),
    source: str = Form(default="file_upload"),
    rag_service=Depends(get_rag_service),
):
    """Upload a .txt, .md, or .pdf file into Pinecone."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid content_type. Choose from: {sorted(ALLOWED_CONTENT_TYPES)}")

    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower()

    raw = await file.read()
    text = ""

    if ext in ("txt", "md"):
        text = raw.decode("utf-8", errors="ignore")
    elif ext == "pdf":
        try:
            import io
            import pdfplumber
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"PDF parse error: {e}")
    elif ext == "docx":
        try:
            import io
            from docx import Document
            doc = Document(io.BytesIO(raw))
            text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"DOCX parse error: {e}")
    else:
        raise HTTPException(status_code=422, detail="Supported formats: .txt, .md, .pdf, .docx")

    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from file.")

    try:
        result = await rag_service.upload_content(
            title=title.strip(),
            content=text.strip(),
            content_type=content_type,
            topic=topic.strip(),
            source=source or filename,
        )
        return result
    except Exception as exc:
        logger.error(f"upload_file_content failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/documents")
async def list_documents(rag_service=Depends(get_rag_service)):
    """List all documents stored in Pinecone."""
    try:
        docs = await rag_service.list_content()
        return {"documents": docs, "total": len(docs)}
    except Exception as exc:
        logger.error(f"list_documents failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, rag_service=Depends(get_rag_service)):
    """Delete all chunks of a document by doc_id."""
    try:
        return await rag_service.delete_document(doc_id)
    except Exception as exc:
        logger.error(f"delete_document failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/documents")
async def delete_all_documents(rag_service=Depends(get_rag_service)):
    """Delete ALL content from Pinecone (destructive)."""
    try:
        return await rag_service.delete_all_content()
    except Exception as exc:
        logger.error(f"delete_all_documents failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
