"""
Unit tests for RAG Service
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.rag_service import RAGService
from app.tools.rag import RAGResult
from app.tools.tavily_mcp import TavilyResult


class TestRAGService:
    """Test cases for RAG Service"""
    
    @pytest.fixture
    def rag_service(self):
        """Create RAG service with mocked dependencies"""
        with patch('app.services.rag_service.get_rag_tool') as mock_rag_tool, \
             patch('app.services.rag_service.get_tavily_client') as mock_tavily_client:
            
            service = RAGService()
            service.rag_tool = Mock()
            service.tavily_client = Mock()
            return service
    
    @pytest.mark.asyncio
    async def test_get_agent_content_tutor_with_examples(self, rag_service):
        """Test getting content for tutor agent with live examples"""
        # Mock RAG results
        rag_results = [
            RAGResult(
                content="Docker networking lesson content",
                source="Docker Book",
                relevance_score=0.95
            )
        ]
        
        # Mock Tavily results
        tavily_results = [
            TavilyResult(
                title="Live Example",
                url="https://example.com",
                content="Live example content",
                relevance_score=0.9,
                source="tavily"
            )
        ]
        
        rag_service.rag_tool.query_content = AsyncMock(return_value=rag_results)
        rag_service.tavily_client.search_live_examples = AsyncMock(return_value=tavily_results)
        
        result = await rag_service.get_agent_content(
            agent_type="tutor",
            query="container networking",
            include_live_examples=True
        )
        
        assert result["agent_type"] == "tutor"
        assert result["query"] == "container networking"
        assert len(result["rag_content"]) == 1
        assert len(result["live_examples"]) == 1
        assert result["rag_content"][0]["content"] == "Docker networking lesson content"
        assert result["live_examples"][0]["title"] == "Live Example"
        
        # Verify method calls
        rag_service.rag_tool.query_content.assert_called_once_with(
            query="container networking",
            agent_type="tutor",
            max_results=5
        )
        rag_service.tavily_client.search_live_examples.assert_called_once_with(
            topic="container networking",
            context="Docker Kubernetes",
            max_results=3
        )
    
    @pytest.mark.asyncio
    async def test_get_agent_content_planning_without_examples(self, rag_service):
        """Test getting content for planning agent without live examples"""
        # Mock RAG results
        rag_results = [
            RAGResult(
                content="Learning path structure",
                source="Docker Book",
                relevance_score=0.9
            )
        ]
        
        rag_service.rag_tool.query_content = AsyncMock(return_value=rag_results)
        
        result = await rag_service.get_agent_content(
            agent_type="planning",
            query="learning path",
            include_live_examples=False
        )
        
        assert result["agent_type"] == "planning"
        assert result["query"] == "learning path"
        assert len(result["rag_content"]) == 1
        assert len(result["live_examples"]) == 0
        assert result["rag_content"][0]["content"] == "Learning path structure"
        
        # Verify Tavily was not called
        rag_service.tavily_client.search_live_examples.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_topic_content(self, rag_service):
        """Test getting content for a specific topic"""
        rag_service.get_agent_content = AsyncMock(return_value={
            "rag_content": [],
            "live_examples": [],
            "agent_type": "tutor",
            "query": "Docker Kubernetes networking"
        })
        
        result = await rag_service.get_topic_content("networking", "tutor")
        
        assert result["agent_type"] == "tutor"
        assert result["query"] == "Docker Kubernetes networking"
        rag_service.get_agent_content.assert_called_once_with(
            agent_type="tutor",
            query="Docker Kubernetes networking",
            include_live_examples=True
        )
    
    @pytest.mark.asyncio
    async def test_get_chapter_content(self, rag_service):
        """Test getting content for a specific chapter"""
        rag_service.get_agent_content = AsyncMock(return_value={
            "rag_content": [],
            "live_examples": [],
            "agent_type": "tutor",
            "query": "Networking"
        })
        
        result = await rag_service.get_chapter_content("Networking", "tutor")
        
        assert result["agent_type"] == "tutor"
        assert result["query"] == "Networking"
        rag_service.get_agent_content.assert_called_once_with(
            agent_type="tutor",
            query="Networking",
            include_live_examples=True
        )
    
    @pytest.mark.asyncio
    async def test_get_quiz_content(self, rag_service):
        """Test getting quiz content"""
        rag_service.get_agent_content = AsyncMock(return_value={
            "rag_content": [],
            "live_examples": [],
            "agent_type": "quiz",
            "query": "networking concepts definitions commands"
        })
        
        result = await rag_service.get_quiz_content("networking")
        
        assert result["agent_type"] == "quiz"
        assert result["query"] == "networking concepts definitions commands"
        rag_service.get_agent_content.assert_called_once_with(
            agent_type="quiz",
            query="networking concepts definitions commands",
            include_live_examples=False
        )
    
    @pytest.mark.asyncio
    async def test_get_tutor_lesson_content(self, rag_service):
        """Test getting comprehensive lesson content for Tutor agent"""
        # Mock RAG results
        rag_results = [
            RAGResult(
                content="Lesson content",
                source="Docker Book",
                relevance_score=0.95
            )
        ]
        
        # Mock Tavily results
        live_examples = [
            TavilyResult(
                title="Live Example",
                url="https://example.com",
                content="Live example content",
                relevance_score=0.9,
                source="tavily"
            )
        ]
        
        best_practices = [
            TavilyResult(
                title="Best Practice",
                url="https://example.com",
                content="Best practice content",
                relevance_score=0.85,
                source="tavily"
            )
        ]
        
        troubleshooting = [
            TavilyResult(
                title="Troubleshooting",
                url="https://example.com",
                content="Troubleshooting content",
                relevance_score=0.8,
                source="tavily"
            )
        ]
        
        rag_service.rag_tool.get_topic_content = AsyncMock(return_value=rag_results)
        rag_service.tavily_client.search_live_examples = AsyncMock(return_value=live_examples)
        rag_service.tavily_client.get_current_best_practices = AsyncMock(return_value=best_practices)
        rag_service.tavily_client.get_troubleshooting_examples = AsyncMock(return_value=troubleshooting)
        
        result = await rag_service.get_tutor_lesson_content("networking", "visual")
        
        assert result["topic"] == "networking"
        assert result["learning_style"] == "visual"
        assert result["content_type"] == "lesson"
        assert len(result["rag_content"]) == 1
        assert len(result["live_examples"]) == 1
        assert len(result["best_practices"]) == 1
        assert len(result["troubleshooting"]) == 1
        
        # Verify all methods were called
        rag_service.rag_tool.get_topic_content.assert_called_once_with("networking", "tutor")
        rag_service.tavily_client.search_live_examples.assert_called_once_with(
            topic="networking",
            context="Docker Kubernetes",
            max_results=3
        )
        rag_service.tavily_client.get_current_best_practices.assert_called_once_with("networking")
        rag_service.tavily_client.get_troubleshooting_examples.assert_called_once_with("networking")
    
    @pytest.mark.asyncio
    async def test_get_planning_content(self, rag_service):
        """Test getting content for Planning agent"""
        rag_service.get_agent_content = AsyncMock(return_value={
            "rag_content": [],
            "live_examples": [],
            "agent_type": "planning",
            "query": "learning path curriculum structure goals interests"
        })
        
        result = await rag_service.get_planning_content("learn Docker", "containerization")
        
        assert result["agent_type"] == "planning"
        assert result["query"] == "learning path curriculum structure learn Docker containerization"
        rag_service.get_agent_content.assert_called_once_with(
            agent_type="planning",
            query="learning path curriculum structure learn Docker containerization",
            include_live_examples=False
        )
    
    @pytest.mark.asyncio
    async def test_get_assessment_content(self, rag_service):
        """Test getting content for Assessment agent"""
        rag_service.get_agent_content = AsyncMock(return_value={
            "rag_content": [],
            "live_examples": [],
            "agent_type": "assessment",
            "query": "assessment questions concepts networking"
        })
        
        result = await rag_service.get_assessment_content("networking")
        
        assert result["agent_type"] == "assessment"
        assert result["query"] == "assessment questions concepts networking"
        rag_service.get_agent_content.assert_called_once_with(
            agent_type="assessment",
            query="assessment questions concepts networking",
            include_live_examples=False
        )
    
    def test_format_rag_result(self, rag_service):
        """Test formatting RAG result"""
        rag_result = RAGResult(
            content="Test content",
            source="Test Book",
            page=42,
            chapter="Test Chapter",
            relevance_score=0.95,
            metadata={"key": "value"}
        )
        
        formatted = rag_service._format_rag_result(rag_result)
        
        assert formatted["content"] == "Test content"
        assert formatted["source"] == "Test Book"
        assert formatted["page"] == 42
        assert formatted["chapter"] == "Test Chapter"
        assert formatted["relevance_score"] == 0.95
        assert formatted["metadata"] == {"key": "value"}
    
    def test_format_tavily_result(self, rag_service):
        """Test formatting Tavily result"""
        tavily_result = TavilyResult(
            title="Test Title",
            url="https://example.com",
            content="Test content",
            relevance_score=0.9,
            published_date="2024-01-15",
            source="tavily",
            metadata={"key": "value"}
        )
        
        formatted = rag_service._format_tavily_result(tavily_result)
        
        assert formatted["title"] == "Test Title"
        assert formatted["url"] == "https://example.com"
        assert formatted["content"] == "Test content"
        assert formatted["relevance_score"] == 0.9
        assert formatted["published_date"] == "2024-01-15"
        assert formatted["source"] == "tavily"
        assert formatted["metadata"] == {"key": "value"}
    
    @pytest.mark.asyncio
    async def test_get_agent_content_error_handling(self, rag_service):
        """Test error handling in get_agent_content"""
        rag_service.rag_tool.query_content = AsyncMock(side_effect=Exception("RAG error"))
        
        result = await rag_service.get_agent_content(
            agent_type="tutor",
            query="test query",
            include_live_examples=False
        )
        
        assert result["agent_type"] == "tutor"
        assert result["query"] == "test query"
        assert result["rag_content"] == []
        assert result["live_examples"] == []
        assert result["error"] == "RAG error"
    
    @pytest.mark.asyncio
    async def test_get_tutor_lesson_content_error_handling(self, rag_service):
        """Test error handling in get_tutor_lesson_content"""
        rag_service.rag_tool.get_topic_content = AsyncMock(side_effect=Exception("Lesson error"))
        
        result = await rag_service.get_tutor_lesson_content("networking", "visual")
        
        assert result["topic"] == "networking"
        assert result["learning_style"] == "visual"
        assert result["rag_content"] == []
        assert result["live_examples"] == []
        assert result["best_practices"] == []
        assert result["troubleshooting"] == []
        assert result["error"] == "Lesson error"
