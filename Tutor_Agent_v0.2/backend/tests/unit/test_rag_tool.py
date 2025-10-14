"""
Unit tests for RAG Tool
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.tools.rag import RAGTool, RAGResult


class TestRAGTool:
    """Test cases for RAG Tool"""
    
    @pytest.fixture
    def mock_pinecone_client(self):
        """Mock Pinecone client"""
        mock_client = Mock()
        mock_index = Mock()
        mock_client.Index.return_value = mock_index
        mock_client.list_indexes.return_value.names.return_value = []
        mock_client.create_index.return_value = None
        mock_client.Index.return_value = mock_index
        return mock_client, mock_index
    
    @pytest.fixture
    def rag_tool(self, mock_pinecone_client):
        """Create RAG tool with mocked dependencies"""
        mock_client, mock_index = mock_pinecone_client
        
        with patch('app.tools.rag.Pinecone', return_value=mock_client), \
             patch('app.tools.rag.genai.configure'), \
             patch('app.tools.rag.GenerativeModel'):
            
            tool = RAGTool()
            tool.pinecone_client = mock_client
            tool.index = mock_index
            return tool
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, rag_tool):
        """Test embedding generation"""
        text = "Docker container networking"
        embedding = await rag_tool.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 768
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_query_content(self, rag_tool):
        """Test content querying"""
        # Mock Pinecone query response
        mock_matches = [
            Mock(
                score=0.95,
                metadata={
                    'content': 'Docker networking allows containers to communicate',
                    'source': 'Docker Book',
                    'page': 45,
                    'chapter': 'Networking',
                    'content_type': 'lesson'
                }
            ),
            Mock(
                score=0.87,
                metadata={
                    'content': 'Kubernetes networking concepts',
                    'source': 'Kubernetes Book',
                    'page': 123,
                    'chapter': 'Networking',
                    'content_type': 'example'
                }
            )
        ]
        
        rag_tool.index.query.return_value.matches = mock_matches
        
        results = await rag_tool.query_content(
            query="container networking",
            agent_type="tutor",
            max_results=2
        )
        
        assert len(results) == 2
        assert all(isinstance(r, RAGResult) for r in results)
        assert results[0].content == 'Docker networking allows containers to communicate'
        assert results[0].relevance_score == 0.95
        assert results[1].content == 'Kubernetes networking concepts'
        assert results[1].relevance_score == 0.87
    
    def test_get_agent_filters(self, rag_tool):
        """Test agent-specific filters"""
        # Test tutor agent filters
        tutor_filters = rag_tool._get_agent_filters("tutor")
        assert "content_type" in tutor_filters
        assert "lesson" in tutor_filters["content_type"]["$in"]
        
        # Test planning agent filters
        planning_filters = rag_tool._get_agent_filters("planning")
        assert "content_type" in planning_filters
        assert "overview" in planning_filters["content_type"]["$in"]
        
        # Test assessment agent filters
        assessment_filters = rag_tool._get_agent_filters("assessment")
        assert "content_type" in assessment_filters
        assert "concept" in assessment_filters["content_type"]["$in"]
        
        # Test quiz agent filters
        quiz_filters = rag_tool._get_agent_filters("quiz")
        assert "content_type" in quiz_filters
        assert "concept" in quiz_filters["content_type"]["$in"]
        
        # Test orchestrator agent filters
        orchestrator_filters = rag_tool._get_agent_filters("orchestrator")
        assert "content_type" in orchestrator_filters
        assert "introduction" in orchestrator_filters["content_type"]["$in"]
        
        # Test feedback agent filters (no specific filter)
        feedback_filters = rag_tool._get_agent_filters("feedback")
        assert feedback_filters == {}
    
    @pytest.mark.asyncio
    async def test_get_topic_content(self, rag_tool):
        """Test getting content for a specific topic"""
        # Mock the query_content method
        rag_tool.query_content = AsyncMock(return_value=[
            RAGResult(
                content="Docker networking topic content",
                source="Docker Book",
                relevance_score=0.9
            )
        ])
        
        results = await rag_tool.get_topic_content("networking", "tutor")
        
        assert len(results) == 1
        assert results[0].content == "Docker networking topic content"
        rag_tool.query_content.assert_called_once_with(
            query="Docker Kubernetes networking",
            agent_type="tutor",
            max_results=3
        )
    
    @pytest.mark.asyncio
    async def test_get_chapter_content(self, rag_tool):
        """Test getting content for a specific chapter"""
        # Mock the query_content method
        rag_tool.query_content = AsyncMock(return_value=[
            RAGResult(
                content="Chapter content",
                source="Docker Book",
                chapter="Networking",
                relevance_score=0.85
            )
        ])
        
        results = await rag_tool.get_chapter_content("Networking", "tutor")
        
        assert len(results) == 1
        assert results[0].chapter == "Networking"
        rag_tool.query_content.assert_called_once_with(
            query="Networking",
            agent_type="tutor",
            max_results=5,
            filter_metadata={"chapter": "Networking"}
        )
    
    @pytest.mark.asyncio
    async def test_get_examples_for_topic(self, rag_tool):
        """Test getting examples for a topic"""
        # Mock the query_content method
        rag_tool.query_content = AsyncMock(return_value=[
            RAGResult(
                content="Example content",
                source="Docker Book",
                relevance_score=0.9
            )
        ])
        
        results = await rag_tool.get_examples_for_topic("networking")
        
        assert len(results) == 1
        assert results[0].content == "Example content"
        rag_tool.query_content.assert_called_once_with(
            query="networking examples practical",
            agent_type="tutor",
            max_results=3,
            filter_metadata={"content_type": "example"}
        )
    
    @pytest.mark.asyncio
    async def test_get_quiz_content(self, rag_tool):
        """Test getting quiz content for a topic"""
        # Mock the query_content method
        rag_tool.query_content = AsyncMock(return_value=[
            RAGResult(
                content="Quiz content",
                source="Docker Book",
                relevance_score=0.8
            )
        ])
        
        results = await rag_tool.get_quiz_content("networking")
        
        assert len(results) == 1
        assert results[0].content == "Quiz content"
        rag_tool.query_content.assert_called_once_with(
            query="networking concepts definitions",
            agent_type="quiz",
            max_results=5
        )
