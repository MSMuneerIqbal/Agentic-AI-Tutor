"""Unit tests for RAGService — mocked RAGTool + WebSearchTool."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.rag_service import RAGService
from app.tools.rag import RAGResult
from app.tools.web_search import WebResult


# ── fixtures ──────────────────────────────────────────────────────────────────

def _rag_result(content="Lesson content", source="Textbook", score=0.9) -> RAGResult:
    return RAGResult(content=content, source=source, relevance_score=score)


def _web_result(title="Web Article", url="https://example.com", content="Example", score=0.8) -> WebResult:
    return WebResult(title=title, url=url, content=content, relevance_score=score, source="web")


def _make_service(rag_results=None, web_results=None) -> RAGService:
    """Return a pre-initialized RAGService with mocked tools."""
    svc = RAGService()
    svc._initialized = True

    mock_rag = MagicMock()
    mock_rag.query_content = AsyncMock(return_value=rag_results or [])
    mock_rag.get_topic_content = AsyncMock(return_value=rag_results or [])
    mock_rag.upload_content = AsyncMock(return_value={"doc_id": "abc", "chunks_uploaded": 2})
    mock_rag.list_content = AsyncMock(return_value=[])
    mock_rag.delete_document = AsyncMock(return_value={"deleted": True, "doc_id": "abc"})
    mock_rag.delete_all_content = AsyncMock(return_value={"deleted_all": True})
    svc.rag_tool = mock_rag

    mock_web = MagicMock()
    mock_web.search_topic = AsyncMock(return_value=web_results or [])
    mock_web.get_examples = AsyncMock(return_value=web_results or [])
    mock_web.get_best_practices = AsyncMock(return_value=[])
    svc.web_tool = mock_web

    return svc


# ── get_agent_content ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_agent_content_rag_only():
    svc = _make_service(rag_results=[_rag_result()])
    result = await svc.get_agent_content(agent_type="tutor", query="docker networking")

    assert result["agent_type"] == "tutor"
    assert result["query"] == "docker networking"
    assert len(result["rag_content"]) == 1
    assert result["rag_content"][0]["content"] == "Lesson content"
    assert result["web_results"] == []


@pytest.mark.asyncio
async def test_get_agent_content_with_web():
    svc = _make_service(rag_results=[_rag_result()], web_results=[_web_result()])
    result = await svc.get_agent_content(agent_type="tutor", query="docker", include_web=True)

    assert len(result["rag_content"]) == 1
    assert len(result["web_results"]) == 1
    assert result["web_results"][0]["title"] == "Web Article"


@pytest.mark.asyncio
async def test_get_agent_content_rag_failure_returns_empty():
    svc = _make_service()
    svc.rag_tool.query_content = AsyncMock(side_effect=Exception("Pinecone down"))

    result = await svc.get_agent_content(agent_type="tutor", query="test")

    assert result["rag_content"] == []
    assert result["agent_type"] == "tutor"


# ── get_tutor_lesson_content ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_tutor_lesson_content():
    svc = _make_service(rag_results=[_rag_result()], web_results=[_web_result()])
    result = await svc.get_tutor_lesson_content(topic="Python", learning_style="V")

    assert result["topic"] == "Python"
    assert result["learning_style"] == "V"
    assert len(result["rag_content"]) == 1
    assert len(result["web_results"]) == 1


# ── get_quiz_content ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_quiz_content_does_not_call_web():
    svc = _make_service(rag_results=[_rag_result()])
    result = await svc.get_quiz_content("networking")

    assert result["agent_type"] == "quiz"
    svc.web_tool.search_topic.assert_not_called()


# ── upload / list / delete ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_content_delegates_to_rag_tool():
    svc = _make_service()
    result = await svc.upload_content("Title", "Content", "lesson", "Python")

    assert result["doc_id"] == "abc"
    svc.rag_tool.upload_content.assert_called_once_with("Title", "Content", "lesson", "Python", "manual_upload")


@pytest.mark.asyncio
async def test_delete_document_delegates_to_rag_tool():
    svc = _make_service()
    result = await svc.delete_document("abc")

    assert result["deleted"] is True
    svc.rag_tool.delete_document.assert_called_once_with("abc")


@pytest.mark.asyncio
async def test_delete_all_content_delegates_to_rag_tool():
    svc = _make_service()
    result = await svc.delete_all_content()

    assert result["deleted_all"] is True


@pytest.mark.asyncio
async def test_upload_raises_when_rag_tool_unavailable():
    svc = RAGService()
    svc._initialized = True
    svc.rag_tool = None
    svc.web_tool = None

    with pytest.raises(RuntimeError, match="RAG tool not available"):
        await svc.upload_content("t", "c", "lesson", "topic")
