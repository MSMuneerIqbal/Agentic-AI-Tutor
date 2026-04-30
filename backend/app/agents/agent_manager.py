"""AI Agent Manager — routes messages to the correct agent and manages session state."""

from typing import Dict, Any, Optional
from datetime import datetime

from app.core.logging import get_logger
from app.core.session_store import session_store
from app.models import SessionState

from app.agents.orchestrator import OrchestratorAgent
from app.agents.assessment import AssessmentAgent
from app.agents.planning import PlanningAgent
from app.agents.tutor import TutorAgent
from app.agents.quiz import QuizAgent
from app.agents.feedback import FeedbackAgent

logger = get_logger(__name__)


class AgentManager:
    """Routes messages to the right agent and persists session state."""

    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.assessment = AssessmentAgent()
        self.planning = PlanningAgent()
        self.tutor = TutorAgent()
        self.quiz = QuizAgent()
        self.feedback = FeedbackAgent()

        self.agents = {
            "orchestrator": self.orchestrator,
            "assessment": self.assessment,
            "planning": self.planning,
            "tutor": self.tutor,
            "quiz": self.quiz,
            "feedback": self.feedback,
        }

    async def process_message(
        self,
        user_input: str,
        session_id: str,
        user_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process user message and return appropriate agent response."""

        session_state = await self._get_session_state(session_id, user_data)
        logger.info(
            f"Processing message for session {session_id}: '{user_input}', "
            f"state: {session_state['current_state']}"
        )

        agent_type = await self._select_agent(user_input, session_state)
        logger.info(f"Selected agent: {agent_type}")

        agent_response = await self._execute_agent(agent_type, user_input, session_state)
        logger.info(f"Agent response action: {agent_response.get('action')}")

        await self._update_session_state(session_id, user_input, agent_response, session_state)

        return {
            "type": "agent_message",
            "agent": agent_type,
            "text": agent_response.get("message", agent_response.get("response", "")),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "conversation_state": session_state["current_state"],
            "metadata": agent_response,
        }

    # ── session state ─────────────────────────────────────────────────────────

    async def _get_session_state(
        self, session_id: str, user_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        existing = await session_store.get_session(f"session_state:{session_id}")
        if existing:
            return existing

        state = {
            "session_id": session_id,
            "current_state": SessionState.GREETING,
            "user_profile": {
                "learning_style": None,
                "experience_level": None,
                "learning_goals": [],
                "preferred_topics": [],
            },
            "conversation_history": [],
            "current_topic": None,
            "progress": {
                "topics_completed": [],
                "quiz_scores": [],
                "time_spent": 0,
            },
            "assessment_data": {
                "vark_responses": [],
                "experience_questions": [],
                "completed": False,
            },
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }

        if user_data:
            state["user_profile"]["name"] = user_data.get("name", "")
            state["user_profile"]["email"] = user_data.get("email", "")

        return state

    # ── agent selection ───────────────────────────────────────────────────────

    async def _select_agent(self, user_input: str, session_state: Dict[str, Any]) -> str:
        current_state = session_state["current_state"]
        user_lower = user_input.lower().strip()

        if current_state == SessionState.GREETING:
            return "orchestrator"

        if current_state == SessionState.ASSESSING:
            return "assessment"

        if current_state == SessionState.PLANNING:
            return "planning"

        if current_state == SessionState.TUTORING:
            # Allow keyword-based override while in tutoring
            if any(w in user_lower for w in ["quiz", "test me", "practice", "exercise", "challenge"]):
                return "quiz"
            if any(w in user_lower for w in ["feedback", "progress", "how am i doing", "my score", "performance"]):
                return "feedback"
            return "tutor"

        if current_state == SessionState.QUIZZING:
            if any(w in user_lower for w in ["stop quiz", "end quiz", "back to lesson", "continue learning"]):
                return "tutor"
            return "quiz"

        # Fallback keyword routing for any other state
        if any(w in user_lower for w in ["feedback", "progress", "how am i doing", "my score"]):
            return "feedback"
        if any(w in user_lower for w in ["assess", "assessment", "learning style"]):
            return "assessment"

        return "orchestrator"

    # ── agent execution ───────────────────────────────────────────────────────

    async def _execute_agent(
        self, agent_type: str, user_input: str, session_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        assessment_data = session_state.get("assessment_data", {})
        context = {
            "state": session_state["current_state"],
            "user_profile": session_state["user_profile"],
            "topic": session_state.get("current_topic"),
            "learning_style": session_state["user_profile"].get("learning_style") or "V",
            "progress": session_state.get("progress", {}),
            "session_id": session_state["session_id"],
            "user_id": session_state["user_profile"].get("email"),
            "session_state": session_state["current_state"],
            # Assessment state
            "answers": assessment_data.get("answers", []),
            "current_question": session_state.get("current_question", 0),
            "vark_responses": assessment_data.get("vark_responses", []),
            # Quiz state
            "quiz_state": session_state.get("quiz_data"),
            # Planning state
            "planning_stage": session_state.get("planning_stage", "ask_goals"),
            "goals": session_state.get("goals"),
            # Conversation history
            "conversation_history": session_state.get("conversation_history", []),
        }

        agent = self.agents.get(agent_type)
        if agent:
            return await agent._execute(user_input, context)
        return await self.orchestrator._execute(user_input, context)

    # ── session state update ──────────────────────────────────────────────────

    async def _update_session_state(
        self,
        session_id: str,
        user_input: str,
        agent_response: Dict[str, Any],
        session_state: Dict[str, Any],
    ) -> None:
        if "next_state" in agent_response:
            session_state["current_state"] = agent_response["next_state"]
            logger.info(f"Session {session_id} state → {agent_response['next_state']}")

        if "topic" in agent_response:
            session_state["current_topic"] = agent_response["topic"]

        # Persist assessment answers
        if "answers" in agent_response:
            session_state.setdefault("assessment_data", {})["answers"] = agent_response["answers"]

        # Persist which question is currently displayed
        if "current_question" in agent_response:
            session_state["current_question"] = agent_response["current_question"]

        # Persist quiz state
        if "quiz_state" in agent_response:
            session_state["quiz_data"] = agent_response["quiz_state"]

        # Persist planning stage and goals
        if "planning_stage" in agent_response:
            session_state["planning_stage"] = agent_response["planning_stage"]
        if agent_response.get("goals"):
            session_state["goals"] = agent_response["goals"]

        # Assessment complete — store learning style and move to planning
        if agent_response.get("action") == "assessment_complete" and "learning_style" in agent_response:
            style = agent_response["learning_style"]
            session_state["user_profile"]["learning_style"] = style
            session_state["current_state"] = SessionState.PLANNING
            logger.info(f"Session {session_id} learning style = {style}, moving to PLANNING")

        # Plan complete — move to tutoring
        if agent_response.get("action") == "plan_complete":
            session_state["current_state"] = SessionState.TUTORING
            if "topics" in agent_response:
                session_state["progress"]["plan_topics"] = agent_response["topics"]

        # Append to conversation history (capped at 50)
        session_state.setdefault("conversation_history", []).append({
            "user_message": user_input,
            "agent_response": agent_response.get("message", agent_response.get("response", "")),
            "agent_type": agent_response.get("agent", "unknown"),
            "action": agent_response.get("action", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
        })
        if len(session_state["conversation_history"]) > 50:
            session_state["conversation_history"] = session_state["conversation_history"][-50:]

        session_state["last_updated"] = datetime.utcnow().isoformat()

        await session_store.set_session(
            f"session_state:{session_id}", session_state, ttl=86400
        )
