"""
RAG Service — coordinates Pinecone vector search and OpenAI web search.
Provides content retrieval for all agents in the LMS tutor system.
"""

import logging
from typing import Any, Dict, List

from app.tools.rag import RAGResult, RAGTool, get_rag_tool
from app.tools.web_search import WebResult, WebSearchTool, get_web_search_tool

logger = logging.getLogger(__name__)


class RAGService:
    """Unified interface for RAG + web search content retrieval."""

    def __init__(self):
        self.rag_tool: RAGTool | None = None
        self.web_tool: WebSearchTool | None = None
        self._initialized = False

    async def _ensure_initialized(self):
        if not self._initialized:
            try:
                self.rag_tool = await get_rag_tool()
                self.web_tool = await get_web_search_tool()
                self._initialized = True
                logger.info("RAGService initialized")
            except Exception as e:
                logger.error(f"RAGService init error: {e}")
                self._initialized = True

    # ── public API ─────────────────────────────────────────────────────────────

    async def get_agent_content(
        self,
        agent_type: str,
        query: str,
        include_web: bool = False,
    ) -> Dict[str, Any]:
        await self._ensure_initialized()

        rag_results: List[RAGResult] = []
        web_results: List[WebResult] = []

        if self.rag_tool:
            try:
                rag_results = await self.rag_tool.query_content(query=query, agent_type=agent_type)
            except Exception as e:
                logger.warning(f"RAG query failed: {e}")

        if include_web and self.web_tool:
            try:
                web_results = await self.web_tool.search_topic(query)
            except Exception as e:
                logger.warning(f"Web search failed: {e}")

        return {
            "rag_content": [self._fmt_rag(r) for r in rag_results],
            "web_results": [self._fmt_web(r) for r in web_results],
            "agent_type": agent_type,
            "query": query,
        }

    async def get_tutor_lesson_content(self, topic: str, learning_style: str = "V") -> Dict[str, Any]:
        await self._ensure_initialized()

        rag_results, web_results, best_practices = [], [], []

        if self.rag_tool:
            try:
                rag_results = await self.rag_tool.get_topic_content(topic, "tutor")
            except Exception as e:
                logger.warning(f"RAG topic content failed: {e}")

        if self.web_tool:
            try:
                web_results = await self.web_tool.get_examples(topic)
                best_practices = await self.web_tool.get_best_practices(topic)
            except Exception as e:
                logger.warning(f"Web content failed: {e}")

        return {
            "rag_content": [self._fmt_rag(r) for r in rag_results],
            "web_results": [self._fmt_web(r) for r in web_results],
            "best_practices": [self._fmt_web(r) for r in best_practices],
            "topic": topic,
            "learning_style": learning_style,
        }

    async def get_quiz_content(self, topic: str) -> Dict[str, Any]:
        return await self.get_agent_content(
            agent_type="quiz",
            query=f"{topic} concepts definitions",
            include_web=False,
        )

    async def get_planning_content(self, goals: str, interests: str) -> Dict[str, Any]:
        return await self.get_agent_content(
            agent_type="planning",
            query=f"learning path curriculum {goals} {interests}",
            include_web=True,
        )

    async def get_assessment_content(self, topic: str) -> Dict[str, Any]:
        return await self.get_agent_content(
            agent_type="assessment",
            query=f"assessment concepts {topic}",
            include_web=False,
        )

    # ── content management ─────────────────────────────────────────────────────

    async def upload_content(
        self,
        title: str,
        content: str,
        content_type: str,
        topic: str,
        source: str = "manual_upload",
    ) -> Dict[str, Any]:
        await self._ensure_initialized()
        if not self.rag_tool:
            raise RuntimeError("RAG tool not available.")
        return await self.rag_tool.upload_content(title, content, content_type, topic, source)

    async def list_content(self) -> List[Dict[str, Any]]:
        await self._ensure_initialized()
        if not self.rag_tool:
            return []
        return await self.rag_tool.list_content()

    async def delete_document(self, doc_id: str) -> Dict[str, Any]:
        await self._ensure_initialized()
        if not self.rag_tool:
            raise RuntimeError("RAG tool not available.")
        return await self.rag_tool.delete_document(doc_id)

    async def delete_all_content(self) -> Dict[str, Any]:
        await self._ensure_initialized()
        if not self.rag_tool:
            raise RuntimeError("RAG tool not available.")
        return await self.rag_tool.delete_all_content()

    # ── format helpers ──────────────────────────────────────────────────────────

    def _fmt_rag(self, r: RAGResult) -> Dict[str, Any]:
        return {
            "content": r.content,
            "source": r.source,
            "page": r.page,
            "chapter": r.chapter,
            "relevance_score": r.relevance_score,
            "metadata": r.metadata,
        }

    def _fmt_web(self, r: WebResult) -> Dict[str, Any]:
        return {
            "title": r.title,
            "url": r.url,
            "content": r.content,
            "relevance_score": r.relevance_score,
            "source": r.source,
        }


_rag_service: RAGService | None = None


async def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
