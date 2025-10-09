"""Orchestrator Agent - Manages agent flow and handoffs."""

from typing import Any

from agents import Agent, Handoff

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.models import SessionState

settings = get_settings()


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent manages the overall tutoring flow.

    Responsibilities:
    - Route user to appropriate agent based on session state
    - Handle handoffs between agents
    - Manage session state transitions
    - Send initial greeting (FIRST RUNNER)
    """

    def __init__(self):
        """Initialize Orchestrator Agent."""
        super().__init__(name="Orchestrator", model=settings.gemini_model)
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent."""
        return Agent(
            name="Orchestrator",
            model=self.model,
            instructions="""You are the Orchestrator for an AI tutoring system.

Your role is to:
1. Welcome new users warmly and explain the tutoring process
2. Route users to the appropriate specialist agent based on their current state
3. Manage smooth transitions between assessment, planning, tutoring, and quizzing
4. Maintain context throughout the learning journey

Session States:
- GREETING: Send a friendly welcome and explain next steps (assessment)
- ASSESSING: Hand off to Assessment Agent for learning style evaluation
- TUTORING: Hand off to Tutor Agent for lesson delivery
- QUIZZING: Hand off to Quiz Agent for knowledge testing
- REMEDIATING: Handle failed quiz scenarios with remediation
- DONE: Congratulate and offer next steps

Always be encouraging, clear, and maintain a professional yet friendly tone.""",
        )

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute orchestrator logic.

        Args:
            user_input: User input (or "hello" for FIRST RUNNER)
            context: Session context including state

        Returns:
            Response dictionary with message and next actions
        """
        session_state = context.get("state", SessionState.GREETING)

        # FIRST RUNNER: Initial greeting
        if user_input == "hello" and session_state == SessionState.GREETING:
            return {
                "agent": self.name,
                "message": (
                    "Hello! 👋 I'm your AI Tutor. I'm here to help you learn "
                    "in a way that works best for you.\n\n"
                    "First, I'll ask you a few quick questions to understand your "
                    "learning style. Then we'll create a personalized study plan "
                    "and start learning!\n\n"
                    "Ready to begin your learning journey?"
                ),
                "action": "await_confirmation",
                "next_state": SessionState.ASSESSING,
            }

        # Route based on state
        if session_state == SessionState.ASSESSING:
            return {
                "agent": self.name,
                "message": "Great! Let's start with a quick assessment to understand how you learn best.",
                "action": "handoff_to_assessment",
                "next_state": SessionState.ASSESSING,
            }

        if session_state == SessionState.TUTORING:
            return {
                "agent": self.name,
                "message": "Let's dive into your lesson!",
                "action": "handoff_to_tutor",
                "next_state": SessionState.TUTORING,
            }

        if session_state == SessionState.QUIZZING:
            return {
                "agent": self.name,
                "message": "Time to test your knowledge!",
                "action": "handoff_to_quiz",
                "next_state": SessionState.QUIZZING,
            }

        # Default response for other states
        return {
            "agent": self.name,
            "message": f"I'll help you continue from where we left off. Current state: {session_state}",
            "action": "continue",
        }

    def get_handoffs(self) -> list[Handoff]:
        """
        Get available handoff targets.

        Returns:
            List of Handoff objects for agent transitions
        """
        return [
            Handoff(
                target="Assessment",
                description="Hand off to Assessment Agent for learning style evaluation",
            ),
            Handoff(
                target="Planning",
                description="Hand off to Planning Agent for study plan creation",
            ),
            Handoff(
                target="Tutor",
                description="Hand off to Tutor Agent for lesson delivery",
            ),
            Handoff(
                target="Quiz",
                description="Hand off to Quiz Agent for knowledge testing",
            ),
            Handoff(
                target="Feedback",
                description="Hand off to Feedback Agent for performance review",
            ),
        ]

