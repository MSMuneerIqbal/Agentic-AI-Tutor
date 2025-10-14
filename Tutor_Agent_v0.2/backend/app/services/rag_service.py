"""
RAG Service for managing content retrieval and live examples

This service coordinates between RAG tool and Tavily MCP to provide
comprehensive content for all agents in the Tutor GPT system.
"""

import logging
from typing import List, Dict, Any, Optional
from app.tools.rag import RAGTool, RAGResult, get_rag_tool
from app.tools.tavily_mcp import TavilyMCPClient, TavilyResult, get_tavily_client

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service for managing RAG content retrieval and live examples
    """
    
    def __init__(self):
        """Initialize RAG service with tools"""
        self.rag_tool = None
        self.tavily_client = None
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Ensure RAG service is initialized"""
        if not self._initialized:
            try:
                self.rag_tool = await get_rag_tool()
                self.tavily_client = await get_tavily_client()
                self._initialized = True
                logger.info("RAG Service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize RAG Service: {e}")
                # Set to initialized anyway to avoid repeated attempts
                self._initialized = True
    
    async def get_agent_content(
        self, 
        agent_type: str, 
        query: str, 
        include_live_examples: bool = False
    ) -> Dict[str, Any]:
        """
        Get content for a specific agent type
        
        Args:
            agent_type: Type of agent (tutor, planning, assessment, quiz, orchestrator, feedback)
            query: Content query
            include_live_examples: Whether to include live examples from Tavily
            
        Returns:
            Dictionary containing RAG content and optionally live examples
        """
        try:
            await self._ensure_initialized()
            
            result = {
                "rag_content": [],
                "live_examples": [],
                "agent_type": agent_type,
                "query": query
            }
            
            # Get RAG content if tool is available
            if self.rag_tool:
                rag_results = await self.rag_tool.query_content(
                    query=query,
                    agent_type=agent_type,
                    max_results=5
                )
                result["rag_content"] = [self._format_rag_result(r) for r in rag_results]
            
            # Get live examples if requested and tool is available
            if include_live_examples and agent_type == "tutor" and self.tavily_client:
                live_examples = await self.tavily_client.search_live_examples(
                    topic=query,
                    context="Docker Kubernetes",
                    max_results=3
                )
                result["live_examples"] = [self._format_tavily_result(t) for t in live_examples]
            
            logger.info(f"Retrieved content for {agent_type} agent: {len(result['rag_content'])} RAG results, {len(result['live_examples'])} live examples")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get agent content: {e}")
            return {
                "rag_content": [],
                "live_examples": [],
                "agent_type": agent_type,
                "query": query,
                "error": str(e)
            }
    
    async def get_topic_content(
        self, 
        topic: str, 
        agent_type: str = "general"
    ) -> Dict[str, Any]:
        """Get content for a specific topic"""
        return await self.get_agent_content(
            agent_type=agent_type,
            query=f"Docker Kubernetes {topic}",
            include_live_examples=(agent_type == "tutor")
        )
    
    async def get_chapter_content(
        self, 
        chapter: str, 
        agent_type: str = "general"
    ) -> Dict[str, Any]:
        """Get content for a specific chapter"""
        return await self.get_agent_content(
            agent_type=agent_type,
            query=chapter,
            include_live_examples=(agent_type == "tutor")
        )
    
    async def get_quiz_content(self, topic: str) -> Dict[str, Any]:
        """Get quiz-worthy content for a topic"""
        return await self.get_agent_content(
            agent_type="quiz",
            query=f"{topic} concepts definitions commands",
            include_live_examples=False
        )
    
    async def get_tutor_lesson_content(
        self, 
        topic: str, 
        learning_style: str = "visual"
    ) -> Dict[str, Any]:
        """Get comprehensive lesson content for Tutor agent"""
        try:
            await self._ensure_initialized()
            
            # Get RAG content if tool is available
            rag_results = []
            if self.rag_tool:
                rag_results = await self.rag_tool.get_topic_content(topic, "tutor")
            
            # Get live examples if tool is available
            live_examples = []
            if self.tavily_client:
                live_examples = await self.tavily_client.search_live_examples(
                    topic=topic,
                    context="Docker Kubernetes",
                    max_results=3
                )
            
            # Get best practices if tool is available
            best_practices = []
            if self.tavily_client:
                best_practices = await self.tavily_client.get_current_best_practices(topic)
            
            # Get troubleshooting examples if tool is available
            troubleshooting = []
            if self.tavily_client:
                troubleshooting = await self.tavily_client.get_troubleshooting_examples(topic)
            
            return {
                "rag_content": [self._format_rag_result(r) for r in rag_results],
                "live_examples": [self._format_tavily_result(t) for t in live_examples],
                "best_practices": [self._format_tavily_result(t) for t in best_practices],
                "troubleshooting": [self._format_tavily_result(t) for t in troubleshooting],
                "topic": topic,
                "learning_style": learning_style,
                "content_type": "lesson"
            }
            
        except Exception as e:
            logger.error(f"Failed to get tutor lesson content: {e}")
            return {
                "rag_content": [],
                "live_examples": [],
                "best_practices": [],
                "troubleshooting": [],
                "topic": topic,
                "learning_style": learning_style,
                "error": str(e)
            }
    
    async def get_planning_content(self, goals: str, interests: str) -> Dict[str, Any]:
        """Get content for Planning agent"""
        query = f"learning path curriculum structure {goals} {interests}"
        return await self.get_agent_content(
            agent_type="planning",
            query=query,
            include_live_examples=False
        )
    
    async def get_assessment_content(self, topic: str) -> Dict[str, Any]:
        """Get content for Assessment agent"""
        query = f"assessment questions concepts {topic}"
        return await self.get_agent_content(
            agent_type="assessment",
            query=query,
            include_live_examples=False
        )
    
    def _format_rag_result(self, result: RAGResult) -> Dict[str, Any]:
        """Format RAG result for API response"""
        return {
            "content": result.content,
            "source": result.source,
            "page": result.page,
            "chapter": result.chapter,
            "relevance_score": result.relevance_score,
            "metadata": result.metadata or {}
        }
    
    def _format_tavily_result(self, result: TavilyResult) -> Dict[str, Any]:
        """Format Tavily result for API response"""
        return {
            "title": result.title,
            "url": result.url,
            "content": result.content,
            "relevance_score": result.relevance_score,
            "published_date": result.published_date,
            "source": result.source,
            "metadata": result.metadata or {}
        }


# Global RAG service instance (lazy-loaded)
_rag_service = None


async def get_rag_service() -> RAGService:
    """Get the global RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
