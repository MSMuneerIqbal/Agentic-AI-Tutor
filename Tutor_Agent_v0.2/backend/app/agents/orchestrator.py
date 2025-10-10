"""Orchestrator Agent - Manages agent flow and handoffs with topic skipping logic."""

import logging
from typing import Any, Dict

from agents import Agent, Handoff

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.models import SessionState

logger = logging.getLogger(__name__)
settings = get_settings()


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent manages the overall tutoring flow with topic skipping logic.

    Responsibilities:
    - Route user to appropriate agent based on session state
    - Handle handoffs between agents
    - Manage session state transitions
    - Send initial greeting (FIRST RUNNER)
    - Handle topic skipping requests and quiz assessments
    - Coordinate between Tutor and Quiz agents for topic skipping
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
            instructions="""You are the Orchestrator for an AI tutoring system specializing in Docker and Kubernetes.

Your role is to:
1. Welcome new users warmly and explain the tutoring process
2. Route users to the appropriate specialist agent based on their current state
3. Manage smooth transitions between assessment, planning, tutoring, and quizzing
4. Handle topic skipping requests and coordinate assessments
5. Maintain context throughout the learning journey

Session States:
- GREETING: Send a friendly welcome and explain next steps (assessment)
- ASSESSING: Hand off to Assessment Agent for learning style evaluation
- PLANNING: Hand off to Planning Agent for study plan creation
- TUTORING: Hand off to Tutor Agent for lesson delivery
- QUIZZING: Hand off to Quiz Agent for knowledge testing
- TOPIC_SKIP_ASSESSMENT: Coordinate topic skipping quiz assessment
- REMEDIATING: Handle failed quiz scenarios with remediation
- DONE: Congratulate and offer next steps

Topic Skipping Logic:
- When student wants to skip: Tutor Agent provides guidance
- If student insists: Generate quiz for topic assessment
- If quiz passed: Allow skipping and move to next topic
- If quiz failed: Require remediation of the topic

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
        
        if session_state == SessionState.PLANNING:
            return {
                "agent": self.name,
                "message": "Perfect! Now let's create your personalized study plan.",
                "action": "handoff_to_planning",
                "next_state": SessionState.PLANNING,
            }
        
        # Handle user confirmation to start assessment
        if (session_state == SessionState.GREETING and 
            user_input.lower() in ["yes", "ready", "start", "begin", "ok", "okay", "sure"]):
            return {
                "agent": self.name,
                "message": "Perfect! Let's begin your learning style assessment.",
                "action": "start_assessment",
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

        # Handle topic skipping logic
        if session_state == SessionState.TUTORING and "skip" in user_input.lower() and "topic" in user_input.lower():
            return await self._handle_topic_skip_request(user_input, context)

        # Handle quiz results from topic skipping assessment
        if context.get("quiz_result") == "passed":
            return await self._handle_quiz_passed(context)
        elif context.get("quiz_result") == "failed":
            return await self._handle_quiz_failed(context)

        # Handle topic skip assessment state
        if session_state == SessionState.TOPIC_SKIP_ASSESSMENT:
            return {
                "agent": self.name,
                "message": "Let's assess your knowledge of this topic to see if you can skip it.",
                "action": "handoff_to_quiz",
                "next_state": SessionState.TOPIC_SKIP_ASSESSMENT,
                "quiz_type": "topic_skip_assessment",
                "topic": context.get("topic", "current topic")
            }

        # Default response for other states
        return {
            "agent": self.name,
            "message": f"I'll help you continue from where we left off. Current state: {session_state}",
            "action": "continue",
        }

    async def _handle_topic_skip_request(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle student request to skip a topic."""
        topic = context.get("topic", "current topic")
        
        # Check if student is insisting after initial guidance
        if context.get("skip_request") and context.get("next_state") == "waiting_for_confirmation":
            # Student is insisting, generate quiz for assessment
            return {
                "agent": self.name,
                "message": f"I understand you want to skip {topic}. Let me generate a quiz to assess your knowledge of this topic. If you pass, we can move on to the next topic.",
                "action": "generate_skip_quiz",
                "next_state": SessionState.TOPIC_SKIP_ASSESSMENT,
                "topic": topic,
                "quiz_type": "topic_skip_assessment"
            }
        else:
            # First request, let Tutor Agent provide guidance
            return {
                "agent": self.name,
                "message": f"I see you want to skip {topic}. Let me have our Tutor Agent provide some guidance on why this topic is important for your learning journey.",
                "action": "handoff_to_tutor",
                "next_state": SessionState.TUTORING,
                "topic": topic,
                "skip_request": True
            }

    async def _handle_quiz_passed(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle passed quiz result from topic skipping assessment."""
        topic = context.get("topic", "the topic")
        score = context.get("score_percentage", 0)
        
        return {
            "agent": self.name,
            "message": f"🎉 Excellent! You scored {score:.1f}% on the {topic} quiz. You clearly understand this topic well and can skip it. Let's move on to the next topic in your learning path!",
            "action": "topic_skipped",
            "next_state": SessionState.TUTORING,
            "topic_skipped": True,
            "next_topic": True
        }

    async def _handle_quiz_failed(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed quiz result from topic skipping assessment."""
        topic = context.get("topic", "the topic")
        score = context.get("score_percentage", 0)
        
        return {
            "agent": self.name,
            "message": f"I see you scored {score:.1f}% on the {topic} quiz. This topic is important for your understanding, so let's learn it properly together. Our Tutor Agent will help you master this topic step by step.",
            "action": "remediation_required",
            "next_state": SessionState.TUTORING,
            "topic": topic,
            "remediation": True,
            "quiz_result": "failed"
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

