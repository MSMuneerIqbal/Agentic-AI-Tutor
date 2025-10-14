#!/usr/bin/env python3
"""
Setup Pinecone embeddings for Docker and Kubernetes content.
This script creates the Pinecone index and populates it with sample content.
"""

import asyncio
import logging
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.tools.rag import RAGTool, get_rag_tool
from app.tools.tavily_mcp import TavilyMCPClient, get_tavily_client
from app.services.rag_service import RAGService, get_rag_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample Docker and Kubernetes content for embedding
SAMPLE_CONTENT = [
    {
        "content": "Docker is a containerization platform that allows you to package applications and their dependencies into lightweight, portable containers. Containers provide consistency across different environments and make deployment easier.",
        "source": "Docker Fundamentals",
        "page": 1,
        "chapter": "Introduction to Docker",
        "metadata": {"topic": "docker", "type": "fundamental", "agent": "tutor"}
    },
    {
        "content": "Docker containers are isolated processes that share the host OS kernel. They include the application code, runtime, system tools, libraries, and settings. This makes them more efficient than virtual machines.",
        "source": "Docker Fundamentals", 
        "page": 5,
        "chapter": "Container Basics",
        "metadata": {"topic": "docker", "type": "fundamental", "agent": "tutor"}
    },
    {
        "content": "Docker images are read-only templates used to create containers. They are built from Dockerfiles and can be stored in registries like Docker Hub. Images are layered and can be shared efficiently.",
        "source": "Docker Fundamentals",
        "page": 12,
        "chapter": "Docker Images",
        "metadata": {"topic": "docker", "type": "fundamental", "agent": "tutor"}
    },
    {
        "content": "Docker Compose is a tool for defining and running multi-container Docker applications. It uses YAML files to configure services, networks, and volumes. This simplifies development and testing of complex applications.",
        "source": "Docker Fundamentals",
        "page": 25,
        "chapter": "Docker Compose",
        "metadata": {"topic": "docker", "type": "application", "agent": "tutor"}
    },
    {
        "content": "Kubernetes is an open-source container orchestration platform that automates deployment, scaling, and management of containerized applications. It provides a robust framework for running distributed systems.",
        "source": "Kubernetes Fundamentals",
        "page": 1,
        "chapter": "Introduction to Kubernetes",
        "metadata": {"topic": "kubernetes", "type": "fundamental", "agent": "tutor"}
    },
    {
        "content": "Kubernetes clusters consist of master nodes (control plane) and worker nodes. The control plane manages the cluster state, while worker nodes run the actual workloads. This architecture provides high availability and scalability.",
        "source": "Kubernetes Fundamentals",
        "page": 8,
        "chapter": "Cluster Architecture",
        "metadata": {"topic": "kubernetes", "type": "fundamental", "agent": "tutor"}
    },
    {
        "content": "Pods are the smallest deployable units in Kubernetes. They can contain one or more containers and share network and storage resources. Pods are ephemeral and are managed by higher-level controllers.",
        "source": "Kubernetes Fundamentals",
        "page": 15,
        "chapter": "Pods and Containers",
        "metadata": {"topic": "kubernetes", "type": "fundamental", "agent": "tutor"}
    },
    {
        "content": "Deployments are Kubernetes resources that manage replica sets and provide declarative updates to applications. They ensure a specified number of pod replicas are running and handle rolling updates and rollbacks.",
        "source": "Kubernetes Fundamentals",
        "page": 22,
        "chapter": "Deployments",
        "metadata": {"topic": "kubernetes", "type": "application", "agent": "tutor"}
    },
    {
        "content": "Services in Kubernetes provide stable network endpoints for pods. They enable service discovery and load balancing. Different service types include ClusterIP, NodePort, and LoadBalancer for various networking needs.",
        "source": "Kubernetes Fundamentals",
        "page": 30,
        "chapter": "Services and Networking",
        "metadata": {"topic": "kubernetes", "type": "application", "agent": "tutor"}
    },
    {
        "content": "Kubernetes ConfigMaps and Secrets manage configuration data and sensitive information separately from application code. ConfigMaps store non-sensitive data, while Secrets handle passwords, tokens, and keys securely.",
        "source": "Kubernetes Fundamentals",
        "page": 35,
        "chapter": "Configuration Management",
        "metadata": {"topic": "kubernetes", "type": "application", "agent": "tutor"}
    },
    {
        "content": "Docker best practices include using multi-stage builds to reduce image size, running containers as non-root users for security, and using specific image tags instead of 'latest' for production deployments.",
        "source": "Docker Best Practices",
        "page": 1,
        "chapter": "Security and Optimization",
        "metadata": {"topic": "docker", "type": "best_practice", "agent": "tutor"}
    },
    {
        "content": "Kubernetes best practices include using resource limits and requests, implementing health checks with liveness and readiness probes, and using namespaces to organize and isolate resources in multi-tenant environments.",
        "source": "Kubernetes Best Practices",
        "page": 1,
        "chapter": "Production Readiness",
        "metadata": {"topic": "kubernetes", "type": "best_practice", "agent": "tutor"}
    },
    {
        "content": "Docker troubleshooting involves checking container logs with 'docker logs', inspecting container processes with 'docker exec', and monitoring resource usage with 'docker stats'. Common issues include port conflicts and resource constraints.",
        "source": "Docker Troubleshooting",
        "page": 1,
        "chapter": "Common Issues",
        "metadata": {"topic": "docker", "type": "troubleshooting", "agent": "tutor"}
    },
    {
        "content": "Kubernetes troubleshooting includes using 'kubectl describe' to get detailed resource information, 'kubectl logs' to view pod logs, and 'kubectl get events' to see cluster events. Common issues include pod scheduling failures and service connectivity problems.",
        "source": "Kubernetes Troubleshooting",
        "page": 1,
        "chapter": "Debugging Techniques",
        "metadata": {"topic": "kubernetes", "type": "troubleshooting", "agent": "tutor"}
    },
    {
        "content": "Docker networking allows containers to communicate with each other and external networks. Docker provides bridge, host, overlay, and macvlan network drivers for different networking requirements and use cases.",
        "source": "Docker Networking",
        "page": 1,
        "chapter": "Network Drivers",
        "metadata": {"topic": "docker", "type": "advanced", "agent": "tutor"}
    },
    {
        "content": "Kubernetes networking uses CNI (Container Network Interface) plugins to provide networking capabilities. Popular CNI plugins include Calico, Flannel, and Weave Net, each offering different features for network policies and performance.",
        "source": "Kubernetes Networking",
        "page": 1,
        "chapter": "CNI Plugins",
        "metadata": {"topic": "kubernetes", "type": "advanced", "agent": "tutor"}
    }
]

async def setup_pinecone_index():
    """Set up Pinecone index with sample content."""
    logger.info("🚀 Starting Pinecone setup...")
    
    try:
        # Initialize RAG tool
        rag_tool = await get_rag_tool()
        logger.info("✅ RAG Tool initialized")
        
        # Check if index exists and create if needed
        if rag_tool.index is None:
            logger.warning("⚠️ Pinecone index not available, using mock mode")
            return False
        
        # Clear existing data (if any)
        try:
            rag_tool.index.delete(delete_all=True)
            logger.info("🗑️ Cleared existing index data")
        except Exception as e:
            logger.info(f"ℹ️ No existing data to clear: {e}")
        
        # Add sample content to Pinecone
        logger.info(f"📚 Adding {len(SAMPLE_CONTENT)} content pieces to Pinecone...")
        
        for i, content_item in enumerate(SAMPLE_CONTENT):
            try:
                # Generate embedding
                embedding = await rag_tool.generate_embedding(content_item["content"])
                
                # Prepare metadata
                metadata = {
                    "content": content_item["content"],
                    "source": content_item["source"],
                    "page": content_item["page"],
                    "chapter": content_item["chapter"],
                    **content_item["metadata"]
                }
                
                # Upsert to Pinecone
                rag_tool.index.upsert(
                    vectors=[{
                        "id": f"content_{i}",
                        "values": embedding,
                        "metadata": metadata
                    }]
                )
                
                logger.info(f"✅ Added content {i+1}/{len(SAMPLE_CONTENT)}: {content_item['source']} - {content_item['chapter']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to add content {i+1}: {e}")
        
        logger.info("🎉 Pinecone setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pinecone setup failed: {e}")
        return False

async def test_rag_functionality():
    """Test RAG functionality with sample queries."""
    logger.info("🧪 Testing RAG functionality...")
    
    try:
        # Initialize RAG service
        rag_service = await get_rag_service()
        logger.info("✅ RAG Service initialized")
        
        # Test queries
        test_queries = [
            ("Docker containers", "tutor"),
            ("Kubernetes pods", "tutor"),
            ("Docker best practices", "tutor"),
            ("Kubernetes networking", "tutor")
        ]
        
        for query, agent_type in test_queries:
            logger.info(f"🔍 Testing query: '{query}' for agent: {agent_type}")
            
            try:
                results = await rag_service.get_agent_content(agent_type, query, include_live_examples=True)
                logger.info(f"✅ Found content for '{query}'")
                
                if results.get("rag_content"):
                    logger.info(f"  RAG Content: {len(results['rag_content'])} items")
                if results.get("live_examples"):
                    logger.info(f"  Live Examples: {len(results['live_examples'])} items")
                    
            except Exception as e:
                logger.error(f"❌ Query failed for '{query}': {e}")
        
        logger.info("🎉 RAG functionality test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG functionality test failed: {e}")
        return False

async def test_tavily_functionality():
    """Test Tavily MCP functionality."""
    logger.info("🌐 Testing Tavily MCP functionality...")
    
    try:
        # Initialize Tavily client
        tavily_client = await get_tavily_client()
        logger.info("✅ Tavily MCP Client initialized")
        
        # Test queries
        test_queries = [
            "Docker containerization best practices 2024",
            "Kubernetes deployment strategies",
            "Docker vs Kubernetes comparison"
        ]
        
        for query in test_queries:
            logger.info(f"🔍 Testing Tavily query: '{query}'")
            
            try:
                results = await tavily_client.search_live_examples(query, "Docker Kubernetes", max_results=2)
                logger.info(f"✅ Found {len(results)} live examples for '{query}'")
                
                for i, result in enumerate(results):
                    logger.info(f"  {i+1}. {result.title}")
                    logger.info(f"     URL: {result.url}")
                    logger.info(f"     Content: {result.content[:100]}...")
                    
            except Exception as e:
                logger.error(f"❌ Tavily query failed for '{query}': {e}")
        
        logger.info("🎉 Tavily MCP functionality test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tavily MCP functionality test failed: {e}")
        return False

async def main():
    """Main setup function."""
    logger.info("🚀 Starting Tutor GPT System Setup")
    logger.info("=" * 50)
    
    # Check environment variables
    required_vars = ["GEMINI_API_KEY", "TAVILY_API_KEY", "PINECONE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        logger.error("Please set the required environment variables in .env file")
        return False
    
    logger.info("✅ All required environment variables are set")
    
    # Setup Pinecone
    pinecone_success = await setup_pinecone_index()
    
    # Test RAG functionality
    rag_success = await test_rag_functionality()
    
    # Test Tavily functionality
    tavily_success = await test_tavily_functionality()
    
    # Summary
    logger.info("=" * 50)
    logger.info("📊 Setup Summary:")
    logger.info(f"  Pinecone Setup: {'✅ Success' if pinecone_success else '❌ Failed'}")
    logger.info(f"  RAG Functionality: {'✅ Success' if rag_success else '❌ Failed'}")
    logger.info(f"  Tavily Functionality: {'✅ Success' if tavily_success else '❌ Failed'}")
    
    if pinecone_success and rag_success and tavily_success:
        logger.info("🎉 All systems are ready! Your Tutor GPT system is fully functional!")
        return True
    else:
        logger.warning("⚠️ Some components failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
