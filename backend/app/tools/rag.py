"""
RAG Tool — Pinecone vector search with OpenAI text-embedding-3-small embeddings.

Stores and retrieves course content chunks from Pinecone. Dimension: 1536.
"""

import logging
import uuid
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.openai_manager import generate_embedding

logger = logging.getLogger(__name__)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


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

    # ── content management ─────────────────────────────────────────────────────

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        chunks: List[str] = []
        current = ""
        for para in paragraphs:
            if len(current) + len(para) + 1 <= CHUNK_SIZE:
                current = f"{current}\n{para}".strip()
            else:
                if current:
                    chunks.append(current)
                if len(para) <= CHUNK_SIZE:
                    current = para
                else:
                    # hard-split long paragraphs
                    for i in range(0, len(para), CHUNK_SIZE - CHUNK_OVERLAP):
                        chunks.append(para[i : i + CHUNK_SIZE])
                    current = ""
        if current:
            chunks.append(current)
        return chunks or [text[:CHUNK_SIZE]]

    async def upload_content(
        self,
        title: str,
        content: str,
        content_type: str,
        topic: str,
        source: str = "manual_upload",
    ) -> Dict[str, Any]:
        """Chunk text, embed it, and upsert into Pinecone. Returns upload summary."""
        if self.index is None:
            raise RuntimeError("Pinecone index unavailable.")

        doc_id = str(uuid.uuid4())
        chunks = self._chunk_text(content)
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = await generate_embedding(chunk)
            vid = f"{doc_id}_chunk_{i}"
            vectors.append({
                "id": vid,
                "values": embedding,
                "metadata": {
                    "doc_id": doc_id,
                    "title": title,
                    "content": chunk,
                    "content_type": content_type,
                    "topic": topic,
                    "source": source,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
            })

        # upsert in batches of 100
        for i in range(0, len(vectors), 100):
            self.index.upsert(vectors=vectors[i : i + 100])

        logger.info(f"Uploaded '{title}' → {len(chunks)} chunks (doc_id={doc_id})")
        return {"doc_id": doc_id, "title": title, "chunks_uploaded": len(chunks)}

    async def list_content(self, max_items: int = 200) -> List[Dict[str, Any]]:
        """Return all documents stored in Pinecone (grouped by doc_id)."""
        if self.index is None:
            return []
        try:
            all_ids: List[str] = []
            for id_batch in self.index.list(limit=max_items):
                if isinstance(id_batch, list):
                    all_ids.extend(id_batch)
                else:
                    all_ids.append(id_batch)
                if len(all_ids) >= max_items:
                    break

            if not all_ids:
                return []

            # fetch metadata in batches of 100
            docs: Dict[str, Dict] = {}
            for i in range(0, len(all_ids), 100):
                batch = all_ids[i : i + 100]
                fetch_result = self.index.fetch(ids=batch)
                for vid, vector in fetch_result.vectors.items():
                    meta = vector.metadata or {}
                    doc_id = meta.get("doc_id", vid)
                    chunk_idx = meta.get("chunk_index", 0)
                    if doc_id not in docs or chunk_idx == 0:
                        docs[doc_id] = {
                            "doc_id": doc_id,
                            "title": meta.get("title", "Untitled"),
                            "content_preview": meta.get("content", "")[:300],
                            "content_type": meta.get("content_type", ""),
                            "topic": meta.get("topic", ""),
                            "source": meta.get("source", ""),
                            "total_chunks": meta.get("total_chunks", 1),
                        }
            return list(docs.values())
        except Exception as e:
            logger.error(f"list_content failed: {e}")
            return []

    async def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete all chunks belonging to a document."""
        if self.index is None:
            raise RuntimeError("Pinecone index unavailable.")
        try:
            self.index.delete(filter={"doc_id": {"$eq": doc_id}})
            logger.info(f"Deleted document doc_id={doc_id}")
            return {"deleted": True, "doc_id": doc_id}
        except Exception as e:
            logger.error(f"delete_document failed: {e}")
            raise RuntimeError(str(e))

    async def delete_all_content(self) -> Dict[str, Any]:
        """Delete ALL vectors from the index."""
        if self.index is None:
            raise RuntimeError("Pinecone index unavailable.")
        self.index.delete(delete_all=True)
        logger.warning("Deleted ALL content from Pinecone index")
        return {"deleted_all": True}


_rag_tool: RAGTool | None = None


async def get_rag_tool() -> RAGTool:
    global _rag_tool
    if _rag_tool is None:
        _rag_tool = RAGTool()
    return _rag_tool
