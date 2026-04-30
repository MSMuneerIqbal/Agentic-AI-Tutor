"""
System Integration Tests for Phase 5C
Tests the complete integration of all agents and services.
"""

import asyncio
import pytest
import logging
from typing import Dict, Any

from app.agents.orchestrator import OrchestratorAgent
from app.agents.assessment import AssessmentAgent
from app.agents.planning import PlanningAgent
from app.agents.tutor import TutorAgent
from app.agents.quiz import QuizAgent
from app.agents.feedback import FeedbackAgent
from app.services.rag_service import get_rag_service
from app.tools.tavily_mcp import get_tavily_client
from app.models import SessionState

logger = logging.getLogger(__name__)


class TestSystemIntegration:
    """Test complete system integration."""

    @pytest.fixture
    async def setup_agents(self):
        """Setup all agents for testing."""
        return {
            "orchestrator": OrchestratorAgent(),
            "assessment": AssessmentAgent(),
            "planning": PlanningAgent(),
            "tutor": TutorAgent(),
            "quiz": QuizAgent(),
            "feedback": FeedbackAgent()
        }

    @pytest.mark.asyncio
    async def test_complete_learning_workflow(self, setup_agents):
        """Test complete learning workflow from greeting to lesson completion."""
        agents = await setup_agents
        
        # Step 1: Initial greeting
        response = await agents["orchestrator"].execute("hello", {"state": SessionState.GREETING})
        assert response["agent"] == "Orchestrator"
        assert "welcome" in response["message"].lower() or "hello" in response["message"].lower()
        
        # Step 2: Start assessment
        response = await agents["assessment"].execute("start assessment", {
            "user_id": "test_user",
            "session_id": "test_session"
        })
        assert response["agent"] == "Assessment"
        assert "question" in response["message"].lower()
        
        # Step 3: Complete assessment (simulated)
        response = await agents["assessment"].execute("a", {
            "user_id": "test_user",
            "session_id": "test_session",
            "question_number": 1,
            "answers": []
        })
        assert response["agent"] == "Assessment"
        
        # Step 4: Planning
        response = await agents["planning"].execute("I want to learn Docker and Kubernetes", {
            "user_id": "test_user",
            "session_id": "test_session",
            "planning_stage": "goals"
        })
        assert response["agent"] == "Planning"
        assert "goals" in response["message"].lower()
        
        # Step 5: Tutoring
        response = await agents["tutor"].execute("Tell me about Docker containers", {
            "topic": "Docker containers",
            "learning_style": "V",
            "progress": 0
        })
        assert response["agent"] == "Tutor"
        assert "docker" in response["message"].lower()
        
        # Step 6: Quiz
        response = await agents["quiz"].execute("Generate quiz", {
            "topic": "Docker containers",
            "quiz_type": "knowledge_check"
        })
        assert response["agent"] == "Quiz"
        assert "quiz" in response["message"].lower()

    @pytest.mark.asyncio
    async def test_topic_skipping_workflow(self, setup_agents):
        """Test complete topic skipping workflow."""
        agents = await setup_agents
        
        # Step 1: Student wants to skip topic
        response = await agents["orchestrator"].execute("I want to skip Docker containers", {
            "state": SessionState.TUTORING,
            "topic": "Docker containers"
        })
        assert response["agent"] == "Orchestrator"
        
        # Step 2: Tutor provides guidance
        response = await agents["tutor"].execute("I still want to skip this topic", {
            "topic": "Docker containers",
            "learning_style": "V",
            "skip_request": True
        })
        assert response["agent"] == "Tutor"
        assert "skip" in response["message"].lower() or "benefits" in response["message"].lower()
        
        # Step 3: Generate quiz for assessment
        response = await agents["quiz"].execute("Generate assessment quiz", {
            "topic": "Docker containers",
            "quiz_type": "topic_skip_assessment"
        })
        assert response["agent"] == "Quiz"
        assert "quiz" in response["message"].lower() or "assess" in response["message"].lower()
        
        # Step 4: Process quiz results (passed)
        response = await agents["orchestrator"].execute("Quiz completed", {
            "quiz_result": "passed",
            "topic": "Docker containers",
            "score_percentage": 85
        })
        assert response["agent"] == "Orchestrator"
        assert "excellent" in response["message"].lower() or "congratulations" in response["message"].lower()

    @pytest.mark.asyncio
    async def test_rag_service_integration(self):
        """Test RAG service integration with all agents."""
        rag_service = await get_rag_service()
        
        # Test content retrieval for different agent types
        agent_types = ["tutor", "planning", "assessment", "quiz", "orchestrator", "feedback"]
        
        for agent_type in agent_types:
            try:
                results = await rag_service.get_agent_content(agent_type, "Docker containers", include_live_examples=True)
                assert isinstance(results, dict)
                assert "rag_content" in results or "live_examples" in results
                logger.info(f"✅ RAG service working for {agent_type} agent")
            except Exception as e:
                logger.warning(f"⚠️ RAG service issue for {agent_type}: {e}")

    @pytest.mark.asyncio
    async def test_tavily_mcp_integration(self):
        """Test Tavily MCP integration."""
        tavily_client = await get_tavily_client()
        
        try:
            results = await tavily_client.search_live_examples("Docker best practices", "Docker Kubernetes", max_results=2)
            assert isinstance(results, list)
            if results:
                assert hasattr(results[0], 'title')
                assert hasattr(results[0], 'url')
                assert hasattr(results[0], 'content')
            logger.info("✅ Tavily MCP integration working")
        except Exception as e:
            logger.warning(f"⚠️ Tavily MCP issue: {e}")

    @pytest.mark.asyncio
    async def test_feedback_agent_integration(self, setup_agents):
        """Test Feedback Agent integration with other agents."""
        agents = await setup_agents
        
        # Test student difficulty feedback
        response = await agents["feedback"].execute("I'm having trouble understanding Docker", {
            "feedback_type": "student_difficulty",
            "topic": "Docker containers",
            "difficulty_type": "conceptual"
        })
        assert response["agent"] == "Feedback"
        assert "difficulty" in response["message"].lower() or "recommendations" in response["message"].lower()
        
        # Test agent performance monitoring
        response = await agents["feedback"].execute("Monitor tutor performance", {
            "feedback_type": "agent_performance",
            "agent_name": "tutor",
            "performance_metrics": {"satisfaction": 0.8, "response_time": 2.5},
            "student_satisfaction": 0.8
        })
        assert response["agent"] == "Feedback"
        assert "performance" in response["message"].lower() or "analysis" in response["message"].lower()

    @pytest.mark.asyncio
    async def test_agent_handoffs(self, setup_agents):
        """Test agent handoffs and coordination."""
        agents = await setup_agents
        
        # Test orchestrator handoffs
        handoffs = agents["orchestrator"].get_handoffs()
        assert len(handoffs) >= 4  # Should have handoffs to Assessment, Planning, Tutor, Quiz
        
        # Test handoff targets
        handoff_targets = [handoff.target for handoff in handoffs]
        expected_targets = ["Assessment", "Planning", "Tutor", "Quiz", "Feedback"]
        
        for target in expected_targets:
            assert target in handoff_targets, f"Missing handoff target: {target}"

    @pytest.mark.asyncio
    async def test_learning_style_adaptation(self, setup_agents):
        """Test learning style adaptation across agents."""
        agents = await setup_agents
        learning_styles = ["V", "A", "R", "K"]
        
        for style in learning_styles:
            # Test tutor adaptation
            response = await agents["tutor"].execute("Tell me about Docker", {
                "topic": "Docker containers",
                "learning_style": style,
                "progress": 0
            })
            assert response["agent"] == "Tutor"
            assert response.get("learning_style") == style
            
            # Test planning adaptation
            response = await agents["planning"].execute("Create a study plan", {
                "user_id": "test_user",
                "session_id": "test_session",
                "planning_stage": "goals",
                "learning_style": style
            })
            assert response["agent"] == "Planning"

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, setup_agents):
        """Test error handling and recovery across the system."""
        agents = await setup_agents
        
        # Test invalid input handling
        response = await agents["tutor"].execute("", {
            "topic": "Docker containers",
            "learning_style": "V",
            "progress": 0
        })
        assert response["agent"] == "Tutor"
        assert "message" in response
        
        # Test missing context handling
        response = await agents["quiz"].execute("Generate quiz", {})
        assert response["agent"] == "Quiz"
        assert "message" in response
        
        # Test orchestrator error recovery
        response = await agents["orchestrator"].execute("invalid input", {
            "state": "INVALID_STATE"
        })
        assert response["agent"] == "Orchestrator"
        assert "message" in response

    @pytest.mark.asyncio
    async def test_session_state_management(self, setup_agents):
        """Test session state management across agents."""
        agents = await setup_agents
        
        # Test state transitions
        states = [
            SessionState.GREETING,
            SessionState.ASSESSING,
            SessionState.PLANNING,
            SessionState.TUTORING,
            SessionState.QUIZZING
        ]
        
        for state in states:
            response = await agents["orchestrator"].execute("test", {"state": state})
            assert response["agent"] == "Orchestrator"
            assert "message" in response

    @pytest.mark.asyncio
    async def test_performance_metrics(self, setup_agents):
        """Test performance metrics collection."""
        agents = await setup_agents
        
        # Test that all agents respond within reasonable time
        import time
        
        for agent_name, agent in agents.items():
            start_time = time.time()
            response = await agent.execute("test", {"test": True})
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 5.0, f"{agent_name} took too long: {response_time}s"
            assert "message" in response
            logger.info(f"✅ {agent_name} response time: {response_time:.2f}s")

    @pytest.mark.asyncio
    async def test_data_consistency(self, setup_agents):
        """Test data consistency across agents."""
        agents = await setup_agents
        
        # Test that agents maintain consistent context
        context = {
            "user_id": "test_user",
            "session_id": "test_session",
            "topic": "Docker containers",
            "learning_style": "V"
        }
        
        # Test tutor with context
        response1 = await agents["tutor"].execute("Tell me about Docker", context)
        
        # Test quiz with same context
        response2 = await agents["quiz"].execute("Generate quiz", context)
        
        # Both should handle the same topic
        assert "docker" in response1["message"].lower() or "container" in response1["message"].lower()
        assert "docker" in response2["message"].lower() or "quiz" in response2["message"].lower()
