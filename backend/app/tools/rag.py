"""
RAG Tool — Pinecone vector search with OpenAI text-embedding-3-small embeddings.

Stores and retrieves course content chunks from Pinecone. Dimension: 1536.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.openai_manager import generate_embedding

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    content: str
    source: str
    page: Optional[int] = None
    chapter: Optional[str] = None
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGTool:
    """Retrieves relevant content chunks from Pinecone using OpenAI embeddings."""

    EMBEDDING_DIM = 1536  # text-embedding-3-small

    def __init__(self):
        self.index = None
        self._initialize()

    def _initialize(self):
        settings = get_settings()
        try:
            from pinecone import Pinecone, ServerlessSpec
        except ImportError:
            logger.warning("pinecone-client not installed — RAG running in offline mode")
            return

        try:
            pc = Pinecone(api_key=settings.pinecone_api_key)
            index_name = settings.pinecone_index_name

            existing = pc.list_indexes().names()
            if index_name not in existing:
                pc.create_index(
                    name=index_name,
                    dimension=self.EMBEDDING_DIM,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
                logger.info(f"Created Pinecone index '{index_name}' (dim={self.EMBEDDING_DIM})")

            self.index = pc.Index(index_name)
            logger.info("RAGTool connected to Pinecone")
        except Exception as e:
            logger.error(f"RAGTool init failed: {e}")

    async def query_content(
        self,
        query: str,
        agent_type: str = "general",
        max_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[RAGResult]:
        if self.index is None:
            raise RuntimeError("Pinecone index unavailable. Check PINECONE_API_KEY and index setup.")

        embedding = await generate_embedding(query)
        filters = self._agent_filters(agent_type)
        if filter_metadata:
            filters.update(filter_metadata)

        resp = self.index.query(
            vector=embedding,
            top_k=max_results,
            include_metadata=True,
            filter=filters if filters else None,
        )

        results = []
        for match in resp.matches:
            meta = match.metadata or {}
            results.append(RAGResult(
                content=meta.get("content", ""),
                source=meta.get("source", "Unknown"),
                page=meta.get("page"),
                chapter=meta.get("chapter"),
                relevance_score=match.score,
                metadata=meta,
            ))

        logger.info(f"RAG returned {len(results)} results for '{query[:60]}' (agent={agent_type})")
        return results

    def _agent_filters(self, agent_type: str) -> Dict[str, Any]:
        """Return Pinecone metadata filters appropriate for the agent type."""
        mapping = {
            "tutor": {"content_type": {"$in": ["lesson", "example", "explanation", "tutorial"]}},
            "planning": {"content_type": {"$in": ["overview", "structure", "curriculum", "roadmap"]}},
            "assessment": {"content_type": {"$in": ["concept", "definition", "comparison", "best_practice"]}},
            "quiz": {"content_type": {"$in": ["concept", "definition", "command", "configuration"]}},
            "orchestrator": {"content_type": {"$in": ["introduction", "overview", "welcome"]}},
        }
        return mapping.get(agent_type, {})

    async def get_topic_content(self, topic: str, agent_type: str = "general") -> List[RAGResult]:
        return await self.query_content(query=topic, agent_type=agent_type, max_results=3)

    async def get_quiz_content(self, topic: str) -> List[RAGResult]:
        return await self.query_content(
            query=f"{topic} concepts definitions",
            agent_type="quiz",
            max_results=5,
        )


_rag_tool: RAGTool | None = None


async def get_rag_tool() -> RAGTool:
    global _rag_tool
    if _rag_tool is None:
        _rag_tool = RAGTool()
    return _rag_tool
