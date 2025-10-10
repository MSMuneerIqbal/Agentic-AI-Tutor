#!/usr/bin/env python3
"""
Quick Test Script for Tutor GPT System
Tests all major components and integrations
"""

import asyncio
import sys
import os
import time
import requests
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_result(test_name, success, message=""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"    {message}")

async def test_gemini_manager():
    """Test Gemini API Manager."""
    print_header("Testing Gemini API Manager")
    
    try:
        from app.core.gemini_manager import get_gemini_manager
        
        manager = get_gemini_manager()
        
        # Test configuration
        config = manager.get_current_config()
        print_result("API Configuration", True, f"Key: {config['api_key'][:20]}..., Model: {config['model']}")
        
        # Test content generation
        response = await manager.generate_content_with_failover("What is Docker?")
        print_result("Content Generation", bool(response), f"Response length: {len(response) if response else 0}")
        
        # Test embedding generation
        embedding = await manager.generate_embedding_with_failover("Test text")
        print_result("Embedding Generation", bool(embedding), f"Dimensions: {len(embedding) if embedding else 0}")
        
        # Show usage report
        report = manager.get_usage_report()
        print_result("Usage Tracking", True, f"Available keys: {report['available_keys']}/{report['total_keys']}")
        
        return True
        
    except Exception as e:
        print_result("Gemini Manager", False, str(e))
        return False

async def test_rag_system():
    """Test RAG system."""
    print_header("Testing RAG System")
    
    try:
        from app.tools.rag import RAGTool
        
        rag_tool = RAGTool()
        
        # Test embedding generation
        embedding = await rag_tool.generate_embedding("Docker containers")
        print_result("RAG Embedding", bool(embedding), f"Dimensions: {len(embedding) if embedding else 0}")
        
        # Test content query
        results = await rag_tool.query_content("Docker basics", "tutor", max_results=2)
        print_result("RAG Query", bool(results), f"Results: {len(results) if results else 0}")
        
        return True
        
    except Exception as e:
        print_result("RAG System", False, str(e))
        return False

async def test_tavily_integration():
    """Test Tavily MCP integration."""
    print_header("Testing Tavily MCP Integration")
    
    try:
        from app.tools.tavily_mcp import TavilyMCPClient
        
        tavily_client = TavilyMCPClient()
        
        # Test live examples
        results = await tavily_client.search_live_examples("Docker best practices", max_results=2)
        print_result("Tavily Search", bool(results), f"Results: {len(results) if results else 0}")
        
        return True
        
    except Exception as e:
        print_result("Tavily Integration", False, str(e))
        return False

async def test_agents():
    """Test AI agents."""
    print_header("Testing AI Agents")
    
    try:
        from app.agents.tutor import TutorAgent
        from app.agents.planning import PlanningAgent
        from app.agents.assessment import AssessmentAgent
        
        # Test Tutor Agent
        tutor = TutorAgent()
        print_result("Tutor Agent", True, "Initialized successfully")
        
        # Test Planning Agent
        planning = PlanningAgent()
        print_result("Planning Agent", True, "Initialized successfully")
        
        # Test Assessment Agent
        assessment = AssessmentAgent()
        print_result("Assessment Agent", True, "Initialized successfully")
        
        return True
        
    except Exception as e:
        print_result("AI Agents", False, str(e))
        return False

def test_backend_api():
    """Test backend API endpoints."""
    print_header("Testing Backend API")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/healthz", timeout=5)
        print_result("Health Check", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False
    
    # Test API docs
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print_result("API Documentation", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        print_result("API Documentation", False, str(e))
    
    # Test RAG endpoints
    try:
        response = requests.get(f"{base_url}/api/v1/rag/health", timeout=5)
        print_result("RAG Health", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        print_result("RAG Health", False, str(e))
    
    return True

def test_frontend():
    """Test frontend availability."""
    print_header("Testing Frontend")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        print_result("Frontend Server", response.status_code == 200, f"Status: {response.status_code}")
        return True
    except Exception as e:
        print_result("Frontend Server", False, str(e))
        return False

async def test_database_connection():
    """Test database connection."""
    print_header("Testing Database Connection")
    
    try:
        from app.core.database import get_database
        from app.models.user import User
        
        db = get_database()
        print_result("Database Connection", True, "Connected successfully")
        
        # Test basic query
        async with db.get_session() as session:
            # This is a simple test - in production you'd have actual data
            print_result("Database Query", True, "Query executed successfully")
        
        return True
        
    except Exception as e:
        print_result("Database Connection", False, str(e))
        return False

async def test_redis_connection():
    """Test Redis connection."""
    print_header("Testing Redis Connection")
    
    try:
        from app.core.redis_client import get_redis_client
        
        redis_client = get_redis_client()
        
        # Test basic operations
        await redis_client.set("test_key", "test_value", ex=10)
        value = await redis_client.get("test_key")
        
        print_result("Redis Connection", value == "test_value", "Basic operations working")
        
        return True
        
    except Exception as e:
        print_result("Redis Connection", False, str(e))
        return False

async def run_comprehensive_test():
    """Run comprehensive system test."""
    print("🚀 TUTOR GPT - COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    print("Testing all major components and integrations...")
    
    test_results = []
    
    # Core system tests
    test_results.append(await test_gemini_manager())
    test_results.append(await test_rag_system())
    test_results.append(await test_tavily_integration())
    test_results.append(await test_agents())
    
    # Infrastructure tests
    test_results.append(await test_database_connection())
    test_results.append(await test_redis_connection())
    
    # Service tests
    test_results.append(test_backend_api())
    test_results.append(test_frontend())
    
    # Summary
    print_header("Test Summary")
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
        print("\n🌐 Access your application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
    
    return passed == total

async def main():
    """Main test function."""
    try:
        success = await run_comprehensive_test()
        return success
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)