"""Unit tests for RAGTool — pure logic + mocked Pinecone."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.tools.rag import RAGTool, RAGResult


# ── helpers ─────────────────────────────────────────────────────────────────

def _make_tool() -> RAGTool:
    """Return a RAGTool whose Pinecone index is replaced with a MagicMock."""
    tool = RAGTool.__new__(RAGTool)
    tool.index = MagicMock()
    return tool


# ── _chunk_text (pure logic, no mocks needed) ────────────────────────────────

def test_chunk_text_short_content():
    tool = _make_tool()
    chunks = tool._chunk_text("Short content.")
    assert chunks == ["Short content."]


def test_chunk_text_splits_on_double_newline():
    tool = _make_tool()
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = tool._chunk_text(text)
    assert len(chunks) >= 1
    combined = " ".join(chunks)
    assert "Paragraph one" in combined
    assert "Paragraph two" in combined


def test_chunk_text_long_paragraph_is_hard_split():
    tool = _make_tool()
    long_para = "x" * 2000
    chunks = tool._chunk_text(long_para)
    assert all(len(c) <= 900 for c in chunks)  # CHUNK_SIZE=800 + a little overlap


def test_chunk_text_never_empty():
    tool = _make_tool()
    assert tool._chunk_text("") == [""]
    assert tool._chunk_text("   ") != []


# ── _agent_filters (pure logic) ───────────────────────────────────────────────

def test_agent_filters_tutor():
    tool = _make_tool()
    f = tool._agent_filters("tutor")
    assert "content_type" in f
    assert "lesson" in f["content_type"]["$in"]
    assert "example" in f["content_type"]["$in"]


def test_agent_filters_planning():
    tool = _make_tool()
    f = tool._agent_filters("planning")
    assert "overview" in f["content_type"]["$in"]


def test_agent_filters_quiz():
    tool = _make_tool()
    f = tool._agent_filters("quiz")
    assert "concept" in f["content_type"]["$in"]


def test_agent_filters_unknown_returns_empty():
    tool = _make_tool()
    f = tool._agent_filters("unknown_agent")
    assert f == {}


# ── query_content (mocked Pinecone + embedding) ──────────────────────────────

@pytest.mark.asyncio
async def test_query_content_returns_rag_results():
    tool = _make_tool()

    mock_matches = [
        MagicMock(score=0.95, metadata={
            "content": "Docker networking basics",
            "source": "Docker Book",
            "page": 10,
            "chapter": "Networking",
            "content_type": "lesson",
        }),
        MagicMock(score=0.80, metadata={
            "content": "Kubernetes pod communication",
            "source": "K8s Docs",
            "page": None,
            "chapter": None,
            "content_type": "example",
        }),
    ]
    tool.index.query.return_value.matches = mock_matches

    with patch("app.tools.rag.generate_embedding", new=AsyncMock(return_value=[0.1] * 1536)):
        results = await tool.query_content("container networking", agent_type="tutor")

    assert len(results) == 2
    assert all(isinstance(r, RAGResult) for r in results)
    assert results[0].content == "Docker networking basics"
    assert results[0].relevance_score == 0.95
    assert results[1].relevance_score == 0.80


@pytest.mark.asyncio
async def test_query_content_raises_when_index_unavailable():
    tool = RAGTool.__new__(RAGTool)
    tool.index = None

    with pytest.raises(RuntimeError, match="Pinecone index unavailable"):
        await tool.query_content("test")


# ── upload_content (mocked embedding + Pinecone upsert) ──────────────────────

@pytest.mark.asyncio
async def test_upload_content_returns_summary():
    tool = _make_tool()
    tool.index.upsert = MagicMock()

    with patch("app.tools.rag.generate_embedding", new=AsyncMock(return_value=[0.0] * 1536)):
        result = await tool.upload_content(
            title="Test Doc",
            content="Some content here.",
            content_type="lesson",
            topic="Python",
            source="manual",
        )

    assert result["title"] == "Test Doc"
    assert result["chunks_uploaded"] >= 1
    assert "doc_id" in result
    tool.index.upsert.assert_called()


@pytest.mark.asyncio
async def test_upload_content_raises_when_index_unavailable():
    tool = RAGTool.__new__(RAGTool)
    tool.index = None

    with pytest.raises(RuntimeError, match="Pinecone index unavailable"):
        await tool.upload_content("t", "c", "lesson", "topic")


# ── delete_document ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_document_calls_pinecone():
    tool = _make_tool()
    tool.index.delete = MagicMock()

    result = await tool.delete_document("some-doc-id")

    assert result["deleted"] is True
    assert result["doc_id"] == "some-doc-id"
    tool.index.delete.assert_called_once_with(filter={"doc_id": {"$eq": "some-doc-id"}})


@pytest.mark.asyncio
async def test_delete_all_content():
    tool = _make_tool()
    tool.index.delete = MagicMock()

    result = await tool.delete_all_content()

    assert result["deleted_all"] is True
    tool.index.delete.assert_called_once_with(delete_all=True)
