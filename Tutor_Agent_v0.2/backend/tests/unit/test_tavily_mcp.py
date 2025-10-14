"""
Unit tests for Tavily MCP Client
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.tools.tavily_mcp import TavilyMCPClient, TavilyResult


class TestTavilyMCPClient:
    """Test cases for Tavily MCP Client"""
    
    @pytest.fixture
    def tavily_client(self):
        """Create Tavily client with mocked dependencies"""
        with patch('app.tools.tavily_mcp.httpx.AsyncClient') as mock_client:
            client = TavilyMCPClient()
            client.api_key = "test_api_key"
            return client
    
    @pytest.mark.asyncio
    async def test_search_live_examples_with_api_key(self, tavily_client):
        """Test searching live examples with API key"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Docker Networking Guide",
                    "url": "https://docs.docker.com/network/",
                    "content": "Docker networking allows containers to communicate",
                    "score": 0.95,
                    "published_date": "2024-01-15"
                },
                {
                    "title": "Kubernetes Networking",
                    "url": "https://kubernetes.io/docs/concepts/services-networking/",
                    "content": "Kubernetes networking concepts and best practices",
                    "score": 0.87,
                    "published_date": "2024-01-10"
                }
            ]
        }
        
        tavily_client.client.post = AsyncMock(return_value=mock_response)
        
        results = await tavily_client.search_live_examples(
            topic="container networking",
            context="Docker Kubernetes",
            max_results=2
        )
        
        assert len(results) == 2
        assert all(isinstance(r, TavilyResult) for r in results)
        assert results[0].title == "Docker Networking Guide"
        assert results[0].relevance_score == 0.95
        assert results[1].title == "Kubernetes Networking"
        assert results[1].relevance_score == 0.87
        
        # Verify API call was made correctly
        tavily_client.client.post.assert_called_once()
        call_args = tavily_client.client.post.call_args
        assert call_args[0][0] == "https://api.tavily.com/search"
        assert "Authorization" in call_args[1]["headers"]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_api_key"
    
    @pytest.mark.asyncio
    async def test_search_live_examples_without_api_key(self, tavily_client):
        """Test searching live examples without API key (mock mode)"""
        tavily_client.api_key = None
        
        results = await tavily_client.search_live_examples(
            topic="container networking",
            context="Docker Kubernetes",
            max_results=2
        )
        
        assert len(results) == 2
        assert all(isinstance(r, TavilyResult) for r in results)
        assert all(r.source == "mock" for r in results)
    
    @pytest.mark.asyncio
    async def test_search_live_examples_api_error(self, tavily_client):
        """Test handling API errors"""
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        tavily_client.client.post = AsyncMock(return_value=mock_response)
        
        results = await tavily_client.search_live_examples(
            topic="container networking",
            context="Docker Kubernetes",
            max_results=2
        )
        
        # Should fall back to mock examples
        assert len(results) == 2
        assert all(isinstance(r, TavilyResult) for r in results)
        assert all(r.source == "mock" for r in results)
    
    @pytest.mark.asyncio
    async def test_get_current_best_practices(self, tavily_client):
        """Test getting current best practices"""
        tavily_client.search_live_examples = AsyncMock(return_value=[
            TavilyResult(
                title="Best Practices Guide",
                url="https://example.com",
                content="Best practices content",
                relevance_score=0.9,
                source="tavily"
            )
        ])
        
        results = await tavily_client.get_current_best_practices(
            topic="container security",
            context="Docker Kubernetes"
        )
        
        assert len(results) == 1
        assert results[0].title == "Best Practices Guide"
        tavily_client.search_live_examples.assert_called_once_with(
            topic="container security",
            context="Docker Kubernetes",
            max_results=2
        )
    
    @pytest.mark.asyncio
    async def test_get_troubleshooting_examples(self, tavily_client):
        """Test getting troubleshooting examples"""
        tavily_client.search_live_examples = AsyncMock(return_value=[
            TavilyResult(
                title="Troubleshooting Guide",
                url="https://example.com",
                content="Troubleshooting content",
                relevance_score=0.85,
                source="tavily"
            )
        ])
        
        results = await tavily_client.get_troubleshooting_examples(
            topic="container networking",
            context="Docker Kubernetes"
        )
        
        assert len(results) == 1
        assert results[0].title == "Troubleshooting Guide"
        tavily_client.search_live_examples.assert_called_once_with(
            topic="container networking",
            context="Docker Kubernetes",
            max_results=2
        )
    
    @pytest.mark.asyncio
    async def test_get_real_world_use_cases(self, tavily_client):
        """Test getting real-world use cases"""
        tavily_client.search_live_examples = AsyncMock(return_value=[
            TavilyResult(
                title="Real World Use Case",
                url="https://example.com",
                content="Use case content",
                relevance_score=0.88,
                source="tavily"
            )
        ])
        
        results = await tavily_client.get_real_world_use_cases(
            topic="container orchestration",
            context="Docker Kubernetes"
        )
        
        assert len(results) == 1
        assert results[0].title == "Real World Use Case"
        tavily_client.search_live_examples.assert_called_once_with(
            topic="container orchestration",
            context="Docker Kubernetes",
            max_results=3
        )
    
    @pytest.mark.asyncio
    async def test_get_mock_examples(self, tavily_client):
        """Test getting mock examples for known topics"""
        # Test container networking
        results = await tavily_client._get_mock_examples("container networking", 2)
        assert len(results) == 2
        assert all(isinstance(r, TavilyResult) for r in results)
        assert all(r.source == "mock" for r in results)
        
        # Test container orchestration
        results = await tavily_client._get_mock_examples("container orchestration", 2)
        assert len(results) == 2
        assert all(isinstance(r, TavilyResult) for r in results)
        
        # Test unknown topic
        results = await tavily_client._get_mock_examples("unknown topic", 1)
        assert len(results) == 1
        assert results[0].title == "unknown topic - Live Example"
        assert results[0].source == "mock"
    
    @pytest.mark.asyncio
    async def test_close_client(self, tavily_client):
        """Test closing the HTTP client"""
        tavily_client.client.aclose = AsyncMock()
        
        await tavily_client.close()
        
        tavily_client.client.aclose.assert_called_once()
