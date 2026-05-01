"""Integration tests for RAG API endpoints (mocked service)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)

# ── shared mock factory ───────────────────────────────────────────────────────

def _mock_service(**kwargs):
    """Return a mock RAGService with sensible defaults."""
    svc = MagicMock()
    svc.get_agent_content = AsyncMock(return_value={
        "rag_content": [], "web_results": [], "agent_type": "tutor", "query": "test"
    })
    svc.get_tutor_lesson_content = AsyncMock(return_value={
        "rag_content": [], "web_results": [], "best_practices": [],
        "topic": "Python", "learning_style": "V",
    })
    svc.get_quiz_content = AsyncMock(return_value={
        "rag_content": [], "web_results": [], "agent_type": "quiz", "query": "test"
    })
    svc.get_planning_content = AsyncMock(return_value={
        "rag_content": [], "web_results": [], "agent_type": "planning", "query": "test"
    })
    svc.get_assessment_content = AsyncMock(return_value={
        "rag_content": [], "web_results": [], "agent_type": "assessment", "query": "test"
    })
    svc.upload_content = AsyncMock(return_value={"doc_id": "doc-123", "title": "T", "chunks_uploaded": 2})
    svc.list_content = AsyncMock(return_value=[])
    svc.delete_document = AsyncMock(return_value={"deleted": True, "doc_id": "doc-123"})
    svc.delete_all_content = AsyncMock(return_value={"deleted_all": True})
    for k, v in kwargs.items():
        setattr(svc, k, v)
    return svc


# ── health ────────────────────────────────────────────────────────────────────

def test_rag_health():
    resp = client.get("/api/v1/rag/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# ── /rag/content ──────────────────────────────────────────────────────────────

def test_get_content_returns_200():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.post("/api/v1/rag/content", json={"query": "docker", "agent_type": "tutor"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent_type"] == "tutor"
    assert "rag_content" in data


def test_get_content_service_error_returns_500():
    svc = _mock_service()
    svc.get_agent_content = AsyncMock(side_effect=Exception("boom"))
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.post("/api/v1/rag/content", json={"query": "x", "agent_type": "tutor"})
    assert resp.status_code == 500


# ── /rag/lesson ───────────────────────────────────────────────────────────────

def test_get_lesson_returns_200():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.post("/api/v1/rag/lesson", json={"topic": "Python", "learning_style": "V"})
    assert resp.status_code == 200
    assert resp.json()["topic"] == "Python"


# ── /rag/quiz/{topic} ─────────────────────────────────────────────────────────

def test_get_quiz_content_returns_200():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.get("/api/v1/rag/quiz/networking")
    assert resp.status_code == 200


# ── /rag/planning ─────────────────────────────────────────────────────────────

def test_get_planning_content_returns_200():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.get("/api/v1/rag/planning?goals=learn+Python&interests=AI")
    assert resp.status_code == 200


# ── /rag/assessment/{topic} ───────────────────────────────────────────────────

def test_get_assessment_content_returns_200():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.get("/api/v1/rag/assessment/python")
    assert resp.status_code == 200


# ── /rag/documents  (CRUD) ────────────────────────────────────────────────────

def test_list_documents_empty():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.get("/api/v1/rag/documents")
    assert resp.status_code == 200
    assert resp.json() == {"documents": [], "total": 0}


def test_list_documents_returns_items():
    doc = {"doc_id": "d1", "title": "T", "content_preview": "...",
           "content_type": "lesson", "topic": "Python", "source": "manual", "total_chunks": 1}
    svc = _mock_service()
    svc.list_content = AsyncMock(return_value=[doc])
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.get("/api/v1/rag/documents")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["documents"][0]["doc_id"] == "d1"


def test_upload_text_document_returns_201():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.post("/api/v1/rag/documents", json={
            "title": "Python Basics",
            "content": "Variables, loops, functions.",
            "content_type": "lesson",
            "topic": "Python",
        })
    assert resp.status_code == 201
    assert resp.json()["doc_id"] == "doc-123"


def test_upload_text_invalid_content_type_returns_422():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.post("/api/v1/rag/documents", json={
            "title": "X", "content": "Y", "content_type": "nonsense", "topic": "Z",
        })
    assert resp.status_code == 422


def test_upload_text_empty_title_returns_422():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.post("/api/v1/rag/documents", json={
            "title": "  ", "content": "Some content", "content_type": "lesson", "topic": "T",
        })
    assert resp.status_code == 422


def test_delete_document_returns_200():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.delete("/api/v1/rag/documents/doc-123")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True


def test_delete_all_documents_returns_200():
    svc = _mock_service()
    with patch("app.api.routes.rag.get_rag_service", return_value=svc):
        resp = client.delete("/api/v1/rag/documents")
    assert resp.status_code == 200
    assert resp.json()["deleted_all"] is True
