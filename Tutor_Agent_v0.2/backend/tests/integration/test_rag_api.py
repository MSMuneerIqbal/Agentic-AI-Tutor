"""
Integration tests for RAG API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.tools.rag import RAGResult
from app.tools.tavily_mcp import TavilyResult


class TestRAGAPI:
    """Test cases for RAG API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service"""
        with patch('app.api.routes.rag.get_rag_service') as mock_service:
            service_instance = AsyncMock()
            mock_service.return_value = service_instance
            yield service_instance
    
    def test_rag_health_endpoint(self, client):
        """Test RAG health endpoint"""
        response = client.get("/api/v1/rag/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "rag"
    
    def test_get_content_endpoint(self, client, mock_rag_service):
        """Test get content endpoint"""
        # Mock service response
        mock_rag_service.get_agent_content.return_value = {
            "rag_content": [
                {
                    "content": "Test content",
                    "source": "Test Book",
                    "relevance_score": 0.95
                }
            ],
            "live_examples": [
                {
                    "title": "Test Example",
                    "url": "https://example.com",
                    "content": "Example content",
                    "relevance_score": 0.9,
                    "source": "tavily"
                }
            ],
            "agent_type": "tutor",
            "query": "test query"
        }
        
        request_data = {
            "query": "container networking",
            "agent_type": "tutor",
            "include_live_examples": True
        }
        
        response = client.post("/api/v1/rag/content", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_type"] == "tutor"
        assert data["query"] == "test query"
        assert len(data["rag_content"]) == 1
        assert len(data["live_examples"]) == 1
        assert data["rag_content"][0]["content"] == "Test content"
        assert data["live_examples"][0]["title"] == "Test Example"
        
        # Verify service was called correctly
        mock_rag_service.get_agent_content.assert_called_once_with(
            agent_type="tutor",
            query="container networking",
            include_live_examples=True
        )
    
    def test_get_topic_content_endpoint(self, client, mock_rag_service):
        """Test get topic content endpoint"""
        # Mock service response
        mock_rag_service.get_topic_content.return_value = {
            "rag_content": [
                {
                    "content": "Topic content",
                    "source": "Docker Book",
                    "relevance_score": 0.9
                }
            ],
            "live_examples": [],
            "agent_type": "tutor",
            "query": "Docker Kubernetes networking"
        }
        
        request_data = {
            "topic": "networking",
            "agent_type": "tutor"
        }
        
        response = client.post("/api/v1/rag/topic", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_type"] == "tutor"
        assert data["query"] == "Docker Kubernetes networking"
        assert len(data["rag_content"]) == 1
        assert data["rag_content"][0]["content"] == "Topic content"
        
        # Verify service was called correctly
        mock_rag_service.get_topic_content.assert_called_once_with(
            topic="networking",
            agent_type="tutor"
        )
    
    def test_get_lesson_content_endpoint(self, client, mock_rag_service):
        """Test get lesson content endpoint"""
        # Mock service response
        mock_rag_service.get_tutor_lesson_content.return_value = {
            "rag_content": [
                {
                    "content": "Lesson content",
                    "source": "Docker Book",
                    "relevance_score": 0.95
                }
            ],
            "live_examples": [
                {
                    "title": "Live Example",
                    "url": "https://example.com",
                    "content": "Example content",
                    "relevance_score": 0.9,
                    "source": "tavily"
                }
            ],
            "best_practices": [
                {
                    "title": "Best Practice",
                    "url": "https://example.com",
                    "content": "Best practice content",
                    "relevance_score": 0.85,
                    "source": "tavily"
                }
            ],
            "troubleshooting": [
                {
                    "title": "Troubleshooting",
                    "url": "https://example.com",
                    "content": "Troubleshooting content",
                    "relevance_score": 0.8,
                    "source": "tavily"
                }
            ],
            "topic": "networking",
            "learning_style": "visual",
            "content_type": "lesson"
        }
        
        request_data = {
            "topic": "networking",
            "learning_style": "visual"
        }
        
        response = client.post("/api/v1/rag/lesson", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["topic"] == "networking"
        assert data["learning_style"] == "visual"
        assert data["content_type"] == "lesson"
        assert len(data["rag_content"]) == 1
        assert len(data["live_examples"]) == 1
        assert len(data["best_practices"]) == 1
        assert len(data["troubleshooting"]) == 1
        
        # Verify service was called correctly
        mock_rag_service.get_tutor_lesson_content.assert_called_once_with(
            topic="networking",
            learning_style="visual"
        )
    
    def test_get_quiz_content_endpoint(self, client, mock_rag_service):
        """Test get quiz content endpoint"""
        # Mock service response
        mock_rag_service.get_quiz_content.return_value = {
            "rag_content": [
                {
                    "content": "Quiz content",
                    "source": "Docker Book",
                    "relevance_score": 0.9
                }
            ],
            "live_examples": [],
            "agent_type": "quiz",
            "query": "networking concepts definitions commands"
        }
        
        response = client.get("/api/v1/rag/quiz/networking")
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_type"] == "quiz"
        assert data["query"] == "networking concepts definitions commands"
        assert len(data["rag_content"]) == 1
        assert data["rag_content"][0]["content"] == "Quiz content"
        
        # Verify service was called correctly
        mock_rag_service.get_quiz_content.assert_called_once_with("networking")
    
    def test_get_planning_content_endpoint(self, client, mock_rag_service):
        """Test get planning content endpoint"""
        # Mock service response
        mock_rag_service.get_planning_content.return_value = {
            "rag_content": [
                {
                    "content": "Planning content",
                    "source": "Docker Book",
                    "relevance_score": 0.9
                }
            ],
            "live_examples": [],
            "agent_type": "planning",
            "query": "learning path curriculum structure learn Docker containerization"
        }
        
        response = client.get("/api/v1/rag/planning?goals=learn%20Docker&interests=containerization")
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_type"] == "planning"
        assert data["query"] == "learning path curriculum structure learn Docker containerization"
        assert len(data["rag_content"]) == 1
        assert data["rag_content"][0]["content"] == "Planning content"
        
        # Verify service was called correctly
        mock_rag_service.get_planning_content.assert_called_once_with("learn Docker", "containerization")
    
    def test_get_assessment_content_endpoint(self, client, mock_rag_service):
        """Test get assessment content endpoint"""
        # Mock service response
        mock_rag_service.get_assessment_content.return_value = {
            "rag_content": [
                {
                    "content": "Assessment content",
                    "source": "Docker Book",
                    "relevance_score": 0.9
                }
            ],
            "live_examples": [],
            "agent_type": "assessment",
            "query": "assessment questions concepts networking"
        }
        
        response = client.get("/api/v1/rag/assessment/networking")
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_type"] == "assessment"
        assert data["query"] == "assessment questions concepts networking"
        assert len(data["rag_content"]) == 1
        assert data["rag_content"][0]["content"] == "Assessment content"
        
        # Verify service was called correctly
        mock_rag_service.get_assessment_content.assert_called_once_with("networking")
    
    def test_get_live_examples_endpoint(self, client):
        """Test get live examples endpoint"""
        with patch('app.api.routes.rag.get_tavily_client') as mock_tavily_client:
            # Mock Tavily client
            tavily_instance = AsyncMock()
            mock_tavily_client.return_value = tavily_instance
            
            # Mock Tavily results
            tavily_instance.search_live_examples.return_value = [
                TavilyResult(
                    title="Live Example",
                    url="https://example.com",
                    content="Example content",
                    relevance_score=0.9,
                    published_date="2024-01-15",
                    source="tavily"
                )
            ]
            
            response = client.get("/api/v1/rag/live-examples/networking?context=Docker%20Kubernetes&max_results=3")
            assert response.status_code == 200
            
            data = response.json()
            assert data["topic"] == "networking"
            assert data["context"] == "Docker Kubernetes"
            assert len(data["examples"]) == 1
            assert data["examples"][0]["title"] == "Live Example"
            assert data["examples"][0]["url"] == "https://example.com"
            assert data["examples"][0]["relevance_score"] == 0.9
            
            # Verify Tavily client was called correctly
            tavily_instance.search_live_examples.assert_called_once_with(
                topic="networking",
                context="Docker Kubernetes",
                max_results=3
            )
    
    def test_get_content_endpoint_error_handling(self, client, mock_rag_service):
        """Test error handling in get content endpoint"""
        # Mock service to raise exception
        mock_rag_service.get_agent_content.side_effect = Exception("Service error")
        
        request_data = {
            "query": "test query",
            "agent_type": "tutor",
            "include_live_examples": False
        }
        
        response = client.post("/api/v1/rag/content", json=request_data)
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data
        assert "Service error" in data["detail"]
    
    def test_get_lesson_content_endpoint_error_handling(self, client, mock_rag_service):
        """Test error handling in get lesson content endpoint"""
        # Mock service to raise exception
        mock_rag_service.get_tutor_lesson_content.side_effect = Exception("Lesson error")
        
        request_data = {
            "topic": "networking",
            "learning_style": "visual"
        }
        
        response = client.post("/api/v1/rag/lesson", json=request_data)
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data
        assert "Lesson error" in data["detail"]
    
    def test_get_live_examples_endpoint_error_handling(self, client):
        """Test error handling in get live examples endpoint"""
        with patch('app.api.routes.rag.get_tavily_client') as mock_tavily_client:
            # Mock Tavily client to raise exception
            tavily_instance = AsyncMock()
            tavily_instance.search_live_examples.side_effect = Exception("Tavily error")
            mock_tavily_client.return_value = tavily_instance
            
            response = client.get("/api/v1/rag/live-examples/networking")
            assert response.status_code == 500
            
            data = response.json()
            assert "detail" in data
            assert "Tavily error" in data["detail"]
