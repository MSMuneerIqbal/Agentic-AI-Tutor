"""
Tavily MCP (Model Context Protocol) Integration

This module provides integration with Tavily MCP server to fetch live,
real-world examples and current information for the Tutor Agent.
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
class TavilyResult:
    """Result from Tavily MCP query containing live examples and information"""
    title: str
    url: str
    content: str
    relevance_score: float
    published_date: Optional[str] = None
    source: str = "tavily"
    metadata: Dict[str, Any] = None


class TavilyMCPClient:
    """
    Tavily MCP Client for fetching live examples and current information
    to enhance Tutor Agent lessons with real-world context.
    """
    
    def __init__(self):
        """Initialize Tavily MCP client"""
        self.base_url = "https://api.tavily.com"
        settings = get_settings()
        self.api_key = getattr(settings, 'tavily_api_key', None)
        
        # Try to import httpx
        try:
            import httpx
            self.client = httpx.AsyncClient(timeout=30.0)
        except ImportError:
            logger.warning("httpx not available, using mock mode")
            self.client = None
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate Tavily configuration"""
        if not self.api_key or self.client is None:
            logger.warning("Tavily API key not configured or httpx not available. Using mock responses.")
        else:
            logger.info("Tavily MCP client initialized successfully")
    
    async def search_live_examples(
        self, 
        topic: str, 
        context: str = "Docker Kubernetes",
        max_results: int = 3
    ) -> List[TavilyResult]:
        """
        Search for live examples related to a topic
        
        Args:
            topic: The topic to search for (e.g., "container networking")
            context: Additional context (e.g., "Docker Kubernetes")
            max_results: Maximum number of results to return
            
        Returns:
            List of TavilyResult objects with live examples
        """
        try:
            if not self.api_key or self.client is None:
                return await self._get_mock_examples(topic, max_results)
            
            # Construct search query
            query = f"{context} {topic} examples tutorial guide"
            
            # Make API request to Tavily
            response = await self.client.post(
                f"{self.base_url}/search",
                json={
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True,
                    "include_images": False,
                    "include_raw_content": False,
                    "max_results": max_results,
                    "include_domains": [
                        "docker.com",
                        "kubernetes.io", 
                        "docs.docker.com",
                        "kubernetes.io/docs",
                        "github.com",
                        "stackoverflow.com",
                        "medium.com",
                        "dev.to"
                    ],
                    "exclude_domains": [
                        "reddit.com",
                        "twitter.com",
                        "facebook.com"
                    ]
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Tavily API error: {response.status_code} - {response.text}")
                return await self._get_mock_examples(topic, max_results)
            
            data = response.json()
            results = []
            
            # Process search results
            for item in data.get("results", []):
                result = TavilyResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    relevance_score=item.get("score", 0.0),
                    published_date=item.get("published_date"),
                    metadata=item
                )
                results.append(result)
            
            logger.info(f"Tavily search returned {len(results)} live examples for topic: {topic}")
            return results
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return await self._get_mock_examples(topic, max_results)
    
    async def get_current_best_practices(
        self, 
        topic: str, 
        context: str = "Docker Kubernetes"
    ) -> List[TavilyResult]:
        """Get current best practices for a topic"""
        query = f"{context} {topic} best practices 2024 2025"
        return await self.search_live_examples(topic, context, max_results=2)
    
    async def get_troubleshooting_examples(
        self, 
        topic: str, 
        context: str = "Docker Kubernetes"
    ) -> List[TavilyResult]:
        """Get troubleshooting examples for a topic"""
        query = f"{context} {topic} troubleshooting common issues solutions"
        return await self.search_live_examples(topic, context, max_results=2)
    
    async def get_real_world_use_cases(
        self, 
        topic: str, 
        context: str = "Docker Kubernetes"
    ) -> List[TavilyResult]:
        """Get real-world use cases for a topic"""
        query = f"{context} {topic} real world use cases production examples"
        return await self.search_live_examples(topic, context, max_results=3)
    
    async def _get_mock_examples(self, topic: str, max_results: int) -> List[TavilyResult]:
        """Get mock examples when Tavily API is not available"""
        mock_examples = {
            "container networking": [
                TavilyResult(
                    title="Docker Networking Best Practices",
                    url="https://docs.docker.com/network/",
                    content="Docker provides several networking options including bridge, host, overlay, and macvlan networks. Bridge networks are the default and provide isolation between containers.",
                    relevance_score=0.95,
                    source="mock"
                ),
                TavilyResult(
                    title="Kubernetes Network Policies",
                    url="https://kubernetes.io/docs/concepts/services-networking/network-policies/",
                    content="Network policies in Kubernetes allow you to control traffic flow between pods. They provide fine-grained control over network communication.",
                    relevance_score=0.90,
                    source="mock"
                )
            ],
            "container orchestration": [
                TavilyResult(
                    title="Kubernetes Deployment Strategies",
                    url="https://kubernetes.io/docs/concepts/workloads/controllers/deployment/",
                    content="Kubernetes deployments provide declarative updates to pods and ReplicaSets. Common strategies include RollingUpdate and Recreate.",
                    relevance_score=0.95,
                    source="mock"
                ),
                TavilyResult(
                    title="Docker Swarm vs Kubernetes",
                    url="https://docs.docker.com/engine/swarm/",
                    content="Docker Swarm provides native clustering for Docker containers, while Kubernetes offers more advanced orchestration features.",
                    relevance_score=0.85,
                    source="mock"
                )
            ],
            "container security": [
                TavilyResult(
                    title="Container Security Best Practices",
                    url="https://kubernetes.io/docs/concepts/security/",
                    content="Container security involves image scanning, runtime protection, network policies, and RBAC. Always use non-root users in containers.",
                    relevance_score=0.95,
                    source="mock"
                ),
                TavilyResult(
                    title="Docker Security Scanning",
                    url="https://docs.docker.com/engine/scan/",
                    content="Docker provides built-in security scanning to identify vulnerabilities in container images before deployment.",
                    relevance_score=0.90,
                    source="mock"
                )
            ]
        }
        
        # Return relevant mock examples or generic ones
        examples = mock_examples.get(topic.lower(), [
            TavilyResult(
                title=f"{topic} - Live Example",
                url="https://example.com",
                content=f"This is a live example related to {topic}. In a real implementation, this would be fetched from current web sources.",
                relevance_score=0.80,
                source="mock"
            )
        ])
        
        return examples[:max_results]
    
    async def close(self):
        """Close the HTTP client"""
        if self.client is not None:
            await self.client.aclose()


# Global Tavily MCP client instance (lazy-loaded)
_tavily_client = None


async def get_tavily_client() -> TavilyMCPClient:
    """Get the global Tavily MCP client instance"""
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyMCPClient()
    return _tavily_client
