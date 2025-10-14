"""Feedback Agent - Acts as Principal to monitor, collect feedback, and adapt agent behaviors."""

import logging
from typing import Any, Dict, List

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
settings = get_settings()


class FeedbackAgent(BaseAgent):
    """Feedback Agent acts as Principal to monitor and improve the tutoring system."""

    def __init__(self):
        """Initialize Feedback Agent."""
        super().__init__(name="Feedback", model=settings.gemini_model)
        self.rag_service = get_rag_service()
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent."""
        return Agent(
            name="Feedback",
            model=self.model,
            instructions="""You are the Feedback Agent, acting as the Principal of the AI tutoring system.

🎯 CORE MISSION:
Monitor system performance, collect student feedback, and provide improvement suggestions.

KEY RESPONSIBILITIES:
- Monitor agent performance and identify issues
- Collect and analyze student difficulties
- Provide system-wide optimization recommendations
- Coordinate improvements across all agents

Always be proactive in identifying issues and providing constructive feedback.""",
        )

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """Execute feedback and monitoring logic."""
        feedback_type = context.get("feedback_type", "general")
        agent_name = context.get("agent_name", "system")

        try:
            if feedback_type == "student_difficulty":
                return await self._handle_student_difficulty(user_input, context)
            elif feedback_type == "agent_performance":
                return await self._handle_agent_performance(user_input, context)
            elif feedback_type == "system_optimization":
                return await self._handle_system_optimization(user_input, context)
            else:
                return await self._handle_general_feedback(user_input, context)

        except Exception as e:
            logger.error(f"Error in Feedback Agent: {e}")
            return {
                "agent": self.name,
                "response": "I encountered an error while processing your feedback. Please try again.",
                "error": str(e)
            }

    async def _handle_student_difficulty(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle student difficulty feedback."""
        return {
            "agent": self.name,
            "response": "Thank you for sharing your difficulty. I'll analyze this and provide recommendations to improve your learning experience.",
            "feedback_type": "student_difficulty",
            "recommendations": ["Review the topic with additional examples", "Try a different learning approach"]
        }

    async def _handle_agent_performance(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent performance monitoring."""
        return {
            "agent": self.name,
            "response": "I'm monitoring agent performance and will provide improvement suggestions.",
            "feedback_type": "agent_performance",
            "improvements": ["Optimize response time", "Enhance content quality"]
        }

    async def _handle_system_optimization(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system-wide optimization analysis."""
        return {
            "agent": self.name,
            "response": "I'm analyzing system performance and will provide optimization recommendations.",
            "feedback_type": "system_optimization",
            "optimizations": ["Improve response time", "Enhance user experience"]
        }

    async def _handle_general_feedback(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general feedback and monitoring requests."""
        return {
            "agent": self.name,
            "response": "Thank you for your feedback. I'm continuously monitoring the system to ensure the best learning experience.",
            "feedback_type": "general",
            "status": "monitoring_active"
        }
