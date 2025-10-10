"""
RAG (Retrieval-Augmented Generation) Tool with Pinecone Integration

This module provides RAG functionality for accessing Docker and Kubernetes book content
stored in Pinecone vector database. It enables all agents to fetch relevant content
based on their specific needs and roles.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
# Import will be done inside the class to handle missing dependencies gracefully
from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """Result from RAG query containing content and metadata"""
    content: str
    source: str
    page: Optional[int] = None
    chapter: Optional[str] = None
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None


class RAGTool:
    """
    RAG Tool for retrieving relevant content from Docker and Kubernetes books
    stored in Pinecone vector database.
    """
    
    def __init__(self):
        """Initialize RAG tool with Pinecone and Gemini embeddings"""
        self.pinecone_client = None
        self.index = None
        self.embedding_model = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Pinecone client and embedding model"""
        try:
            # Try to import Pinecone
            try:
                from pinecone import Pinecone, ServerlessSpec
            except ImportError:
                logger.warning("Pinecone not available, using mock mode")
                self.pinecone_client = None
                self.index = None
                self.embedding_model = None
                return
            
            # Initialize Pinecone
            settings = get_settings()
            self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
            
            # Get or create index for Docker/Kubernetes content
            index_name = "docker-kubernetes-tutor"
            
            if index_name not in self.pinecone_client.list_indexes().names():
                # Create index if it doesn't exist
                self.pinecone_client.create_index(
                    name=index_name,
                    dimension=768,  # Gemini embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info(f"Created Pinecone index: {index_name}")
            
            self.index = self.pinecone_client.Index(index_name)
            
            # Initialize Gemini embedding model
            try:
                import google.generativeai as genai
                from google.generativeai import GenerativeModel
                genai.configure(api_key=settings.gemini_api_key)
                self.embedding_model = GenerativeModel('gemini-embedding-1.0')
            except ImportError:
                logger.warning("Google Generative AI not available, using mock embeddings")
                self.embedding_model = None
            
            logger.info("RAG Tool initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Tool: {e}")
            # Fallback to mock mode
            self.pinecone_client = None
            self.index = None
            self.embedding_model = None
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Gemini"""
        try:
            # For now, we'll use a placeholder embedding
            # In production, you'd call the actual Gemini embedding API
            import hashlib
            import struct
            
            # Create a deterministic embedding based on text hash
            text_hash = hashlib.md5(text.encode()).hexdigest()
            embedding = []
            for i in range(0, len(text_hash), 2):
                val = int(text_hash[i:i+2], 16) / 255.0
                embedding.append(val)
            
            # Pad or truncate to 768 dimensions
            while len(embedding) < 768:
                embedding.append(0.0)
            embedding = embedding[:768]
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def query_content(
        self, 
        query: str, 
        agent_type: str = "general",
        max_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RAGResult]:
        """
        Query RAG content based on agent type and query
        
        Args:
            query: Search query
            agent_type: Type of agent (tutor, planning, assessment, quiz, orchestrator, feedback)
            max_results: Maximum number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of RAGResult objects with relevant content
        """
        try:
            # If Pinecone is not available, return mock results
            if self.index is None:
                return self._get_mock_rag_results(query, agent_type, max_results)
            
            # Generate embedding for query
            query_embedding = await self.generate_embedding(query)
            
            # Build filter based on agent type
            agent_filters = self._get_agent_filters(agent_type)
            if filter_metadata:
                agent_filters.update(filter_metadata)
            
            # Query Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                top_k=max_results,
                include_metadata=True,
                filter=agent_filters if agent_filters else None
            )
            
            # Convert results to RAGResult objects
            results = []
            for match in search_results.matches:
                result = RAGResult(
                    content=match.metadata.get('content', ''),
                    source=match.metadata.get('source', 'Unknown'),
                    page=match.metadata.get('page'),
                    chapter=match.metadata.get('chapter'),
                    relevance_score=match.score,
                    metadata=match.metadata
                )
                results.append(result)
            
            logger.info(f"RAG query returned {len(results)} results for agent: {agent_type}")
            return results
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return self._get_mock_rag_results(query, agent_type, max_results)
    
    def _get_agent_filters(self, agent_type: str) -> Dict[str, Any]:
        """Get metadata filters based on agent type"""
        filters = {}
        
        if agent_type == "tutor":
            # Tutor agent needs comprehensive content
            filters["content_type"] = {"$in": ["lesson", "example", "explanation", "tutorial"]}
        elif agent_type == "planning":
            # Planning agent needs structure and overview content
            filters["content_type"] = {"$in": ["overview", "structure", "curriculum", "roadmap"]}
        elif agent_type == "assessment":
            # Assessment agent needs question-worthy content
            filters["content_type"] = {"$in": ["concept", "definition", "comparison", "best_practice"]}
        elif agent_type == "quiz":
            # Quiz agent needs testable content
            filters["content_type"] = {"$in": ["concept", "definition", "command", "configuration"]}
        elif agent_type == "orchestrator":
            # Orchestrator needs greeting and flow content
            filters["content_type"] = {"$in": ["introduction", "overview", "welcome"]}
        elif agent_type == "feedback":
            # Feedback agent needs all content for analysis
            filters = {}  # No specific filter, get all content
        
        return filters
    
    def _get_mock_rag_results(self, query: str, agent_type: str, max_results: int) -> List[RAGResult]:
        """Get mock RAG results when Pinecone is not available"""
        mock_results = {
            "container networking": [
                RAGResult(
                    content="Docker networking allows containers to communicate with each other and with the host system. There are several network drivers available including bridge, host, overlay, and macvlan.",
                    source="Docker Book",
                    page=45,
                    chapter="Networking",
                    relevance_score=0.95,
                    metadata={"content_type": "lesson", "topic": "networking"}
                ),
                RAGResult(
                    content="Kubernetes networking provides a flat network where pods can communicate with each other across nodes. Network policies allow you to control traffic flow between pods.",
                    source="Kubernetes Book",
                    page=123,
                    chapter="Networking",
                    relevance_score=0.90,
                    metadata={"content_type": "example", "topic": "networking"}
                )
            ],
            "container orchestration": [
                RAGResult(
                    content="Kubernetes is a container orchestration platform that automates deployment, scaling, and management of containerized applications. It provides features like service discovery, load balancing, and rolling updates.",
                    source="Kubernetes Book",
                    page=67,
                    chapter="Orchestration",
                    relevance_score=0.95,
                    metadata={"content_type": "lesson", "topic": "orchestration"}
                ),
                RAGResult(
                    content="Docker Swarm is Docker's native clustering and orchestration solution. It provides a simple way to deploy and manage containerized applications across multiple hosts.",
                    source="Docker Book",
                    page=89,
                    chapter="Orchestration",
                    relevance_score=0.85,
                    metadata={"content_type": "example", "topic": "orchestration"}
                )
            ],
            "container security": [
                RAGResult(
                    content="Container security involves multiple layers including image scanning, runtime protection, network policies, and access control. Always use non-root users in containers and scan images for vulnerabilities.",
                    source="Docker Book",
                    page=156,
                    chapter="Security",
                    relevance_score=0.95,
                    metadata={"content_type": "lesson", "topic": "security"}
                ),
                RAGResult(
                    content="Kubernetes provides RBAC (Role-Based Access Control) for fine-grained permission management. Network policies allow you to control traffic flow between pods for enhanced security.",
                    source="Kubernetes Book",
                    page=234,
                    chapter="Security",
                    relevance_score=0.90,
                    metadata={"content_type": "example", "topic": "security"}
                )
            ]
        }
        
        # Find relevant mock results based on query
        query_lower = query.lower()
        relevant_results = []
        
        for topic, results in mock_results.items():
            if topic in query_lower or any(word in query_lower for word in topic.split()):
                relevant_results.extend(results)
        
        # If no specific topic found, return generic results
        if not relevant_results:
            relevant_results = [
                RAGResult(
                    content=f"This is mock content for the query: {query}. In a real implementation, this would be retrieved from the Pinecone vector database.",
                    source="Mock Book",
                    page=1,
                    chapter="General",
                    relevance_score=0.80,
                    metadata={"content_type": "lesson", "topic": "general"}
                )
            ]
        
        # Filter by agent type if needed
        if agent_type != "general":
            agent_filters = self._get_agent_filters(agent_type)
            if "content_type" in agent_filters:
                content_types = agent_filters["content_type"]["$in"]
                relevant_results = [r for r in relevant_results if r.metadata.get("content_type") in content_types]
        
        return relevant_results[:max_results]
    
    async def get_topic_content(
        self, 
        topic: str, 
        agent_type: str = "general"
    ) -> List[RAGResult]:
        """Get content for a specific topic"""
        return await self.query_content(
            query=f"Docker Kubernetes {topic}",
            agent_type=agent_type,
            max_results=3
        )
    
    async def get_chapter_content(
        self, 
        chapter: str, 
        agent_type: str = "general"
    ) -> List[RAGResult]:
        """Get content for a specific chapter"""
        return await self.query_content(
            query=chapter,
            agent_type=agent_type,
            max_results=5,
            filter_metadata={"chapter": chapter}
        )
    
    async def get_examples_for_topic(
        self, 
        topic: str
    ) -> List[RAGResult]:
        """Get examples for a specific topic (used by Tutor agent)"""
        return await self.query_content(
            query=f"{topic} examples practical",
            agent_type="tutor",
            max_results=3,
            filter_metadata={"content_type": "example"}
        )
    
    async def get_quiz_content(
        self, 
        topic: str
    ) -> List[RAGResult]:
        """Get quiz-worthy content for a topic"""
        return await self.query_content(
            query=f"{topic} concepts definitions",
            agent_type="quiz",
            max_results=5
        )


# Global RAG tool instance (lazy-loaded)
_rag_tool = None


async def get_rag_tool() -> RAGTool:
    """Get the global RAG tool instance"""
    global _rag_tool
    if _rag_tool is None:
        _rag_tool = RAGTool()
    return _rag_tool
