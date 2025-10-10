#!/usr/bin/env python3
"""
Test the complete Tutor GPT system functionality.
This script tests all agents and components in mock mode.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.agents.orchestrator import OrchestratorAgent
from app.agents.assessment import AssessmentAgent
from app.agents.planning import PlanningAgent
from app.agents.tutor import TutorAgent
from app.agents.quiz import QuizAgent
from app.agents.feedback import FeedbackAgent
from app.services.rag_service import get_rag_service
from app.tools.tavily_mcp import get_tavily_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_orchestrator_agent():
    """Test Orchestrator Agent functionality."""
    logger.info("🎭 Testing Orchestrator Agent...")
    
    try:
        orchestrator = OrchestratorAgent()
        
        # Test greeting
        response = await orchestrator.execute("hello", {"state": "GREETING"})
        logger.info(f"✅ Greeting: {response['message'][:100]}...")
        
        # Test topic skipping logic
        response = await orchestrator.execute("I want to skip this topic", {
            "state": "TUTORING",
            "topic": "Docker containers"
        })
        logger.info(f"✅ Topic skip handling: {response['message'][:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Orchestrator test failed: {e}")
        return False

async def test_assessment_agent():
    """Test Assessment Agent functionality."""
    logger.info("📊 Testing Assessment Agent...")
    
    try:
        assessment = AssessmentAgent()
        
        # Test assessment start
        response = await assessment.execute("start assessment", {
            "user_id": "test_user",
            "session_id": "test_session"
        })
        logger.info(f"✅ Assessment start: {response['message'][:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Assessment test failed: {e}")
        return False

async def test_planning_agent():
    """Test Planning Agent functionality."""
    logger.info("📋 Testing Planning Agent...")
    
    try:
        planning = PlanningAgent()
        
        # Test planning start
        response = await planning.execute("I want to learn Docker and Kubernetes", {
            "user_id": "test_user",
            "session_id": "test_session",
            "planning_stage": "goals"
        })
        logger.info(f"✅ Planning start: {response['message'][:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Planning test failed: {e}")
        return False

async def test_tutor_agent():
    """Test Tutor Agent functionality."""
    logger.info("👩‍🏫 Testing Tutor Agent...")
    
    try:
        tutor = TutorAgent()
        
        # Test lesson delivery
        response = await tutor.execute("Tell me about Docker containers", {
            "topic": "Docker containers",
            "learning_style": "V",
            "progress": 0
        })
        logger.info(f"✅ Lesson delivery: {response['message'][:100]}...")
        
        # Test topic skipping guidance
        response = await tutor.execute("I want to skip this topic", {
            "topic": "Docker containers",
            "learning_style": "V",
            "progress": 1
        })
        logger.info(f"✅ Topic skip guidance: {response['message'][:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Tutor test failed: {e}")
        return False

async def test_quiz_agent():
    """Test Quiz Agent functionality."""
    logger.info("📝 Testing Quiz Agent...")
    
    try:
        quiz = QuizAgent()
        
        # Test quiz generation
        response = await quiz.execute("Generate a quiz", {
            "topic": "Docker containers",
            "quiz_type": "knowledge_check"
        })
        logger.info(f"✅ Quiz generation: {response['message'][:100]}...")
        
        # Test topic skip assessment
        response = await quiz.execute("Assess my knowledge", {
            "topic": "Docker containers",
            "quiz_type": "topic_skip_assessment"
        })
        logger.info(f"✅ Topic skip assessment: {response['message'][:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Quiz test failed: {e}")
        return False

async def test_feedback_agent():
    """Test Feedback Agent functionality."""
    logger.info("📈 Testing Feedback Agent...")
    
    try:
        feedback = FeedbackAgent()
        
        # Test feedback collection
        response = await feedback.execute("I'm having trouble understanding Docker", {
            "feedback_type": "student_difficulty",
            "topic": "Docker containers",
            "difficulty_type": "conceptual"
        })
        logger.info(f"✅ Feedback collection: {response['message'][:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Feedback test failed: {e}")
        return False

async def test_rag_service():
    """Test RAG Service functionality."""
    logger.info("📚 Testing RAG Service...")
    
    try:
        rag_service = await get_rag_service()
        
        # Test content retrieval
        results = await rag_service.get_agent_content("tutor", "Docker containers", include_live_examples=True)
        logger.info(f"✅ RAG content retrieval: Found {len(results.get('rag_content', []))} RAG items")
        logger.info(f"✅ Live examples: Found {len(results.get('live_examples', []))} live examples")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG Service test failed: {e}")
        return False

async def test_tavily_client():
    """Test Tavily MCP Client functionality."""
    logger.info("🌐 Testing Tavily MCP Client...")
    
    try:
        tavily_client = await get_tavily_client()
        
        # Test live examples
        results = await tavily_client.search_live_examples("Docker best practices", "Docker Kubernetes", max_results=2)
        logger.info(f"✅ Tavily search: Found {len(results)} live examples")
        
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. {result.title}")
            logger.info(f"     URL: {result.url}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Tavily test failed: {e}")
        return False

async def test_topic_skipping_flow():
    """Test the complete topic skipping flow."""
    logger.info("🔄 Testing Topic Skipping Flow...")
    
    try:
        # Initialize agents
        orchestrator = OrchestratorAgent()
        tutor = TutorAgent()
        quiz = QuizAgent()
        
        # Step 1: Student wants to skip topic
        logger.info("Step 1: Student requests to skip topic")
        response = await orchestrator.execute("I want to skip Docker containers", {
            "state": "TUTORING",
            "topic": "Docker containers"
        })
        logger.info(f"✅ Orchestrator response: {response['message'][:100]}...")
        
        # Step 2: Tutor provides guidance
        logger.info("Step 2: Tutor provides guidance")
        response = await tutor.execute("I still want to skip this topic", {
            "topic": "Docker containers",
            "learning_style": "V",
            "skip_request": True
        })
        logger.info(f"✅ Tutor guidance: {response['message'][:100]}...")
        
        # Step 3: Generate quiz for assessment
        logger.info("Step 3: Generate quiz for assessment")
        response = await quiz.execute("Generate assessment quiz", {
            "topic": "Docker containers",
            "quiz_type": "topic_skip_assessment"
        })
        logger.info(f"✅ Quiz generation: {response['message'][:100]}...")
        
        # Step 4: Process quiz results (simulated)
        logger.info("Step 4: Process quiz results")
        response = await orchestrator.execute("Quiz completed", {
            "quiz_result": "passed",
            "topic": "Docker containers",
            "score_percentage": 85
        })
        logger.info(f"✅ Quiz result processing: {response['message'][:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Topic skipping flow test failed: {e}")
        return False

async def main():
    """Main test function."""
    logger.info("🚀 Starting Tutor GPT System Tests")
    logger.info("=" * 60)
    
    # Test individual agents
    tests = [
        ("Orchestrator Agent", test_orchestrator_agent),
        ("Assessment Agent", test_assessment_agent),
        ("Planning Agent", test_planning_agent),
        ("Tutor Agent", test_tutor_agent),
        ("Quiz Agent", test_quiz_agent),
        ("Feedback Agent", test_feedback_agent),
        ("RAG Service", test_rag_service),
        ("Tavily MCP Client", test_tavily_client),
        ("Topic Skipping Flow", test_topic_skipping_flow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 Test Results Summary:")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info("=" * 60)
    logger.info(f"Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 All tests passed! Your Tutor GPT system is fully functional!")
    else:
        logger.info("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
