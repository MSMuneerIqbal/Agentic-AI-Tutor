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
from app.core.gemini_manager import get_gemini_manager

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
        """Generate embedding for text using Gemini with failover"""
        try:
            # Use the new Gemini manager with failover
            gemini_manager = get_gemini_manager()
            embedding = await gemini_manager.generate_embedding_with_failover(text)
            
            if embedding:
                logger.info(f"Generated embedding for text: {text[:50]}...")
                return embedding
            else:
                logger.error("Failed to generate embedding with Gemini manager")
                raise Exception("Failed to generate embedding: No embedding returned from Gemini")
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    
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
            # If Pinecone is not available, raise error instead of mock
            if self.index is None:
                raise Exception("Pinecone index not available. Please configure Pinecone API key and ensure the index exists.")
            
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
            # Re-raise the error instead of returning mock results
            raise Exception(f"Failed to retrieve RAG content: {str(e)}")
    
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
    
    def _get_real_rag_results(self, query: str, agent_type: str, max_results: int) -> List[RAGResult]:
        """This method is no longer used - RAG now requires real Pinecone connection"""
        raise Exception("Mock RAG results are disabled. Please configure Pinecone API key and ensure the index exists.")
    
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
