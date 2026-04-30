"""Orchestrator Agent — manages session flow and routes between agents."""

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.models import SessionState

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are the Orchestrator for an intelligent LMS tutoring system.

Your role is to welcome students, understand what they want to learn, and guide them
through the learning journey. You coordinate between assessment, planning, tutoring,
quiz, and feedback agents.

Keep your responses warm, concise, and encouraging. Never mention specific subjects
unless the student has told you what they want to learn. Always follow the student's
stated goals and interests.

When asked general questions about how you work or what you can do, be honest and helpful."""


class OrchestratorAgent(BaseAgent):
    """Routes users through the tutoring flow and handles general conversation."""

    def __init__(self):
        super().__init__(name="orchestrator")

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        session_state = context.get("state", SessionState.GREETING)

        if isinstance(session_state, str):
            try:
                session_state = SessionState(session_state)
            except ValueError:
                session_state = SessionState.GREETING

        history = context.get("conversation_history", [])

        # ── GREETING state ────────────────────────────────────────────────────────
        if session_state == SessionState.GREETING:
            if not history:
                # First ever message — send welcome
                user_profile = context.get("user_profile", {})
                name = user_profile.get("name", "")
                greeting_prompt = (
                    f"The student{' ' + name if name else ''} has just arrived. "
                    "Greet them warmly, briefly introduce what the tutor can do (personalised "
                    "learning, assessments, quizzes, brainstorming, progress tracking), then "
                    "ask what subject or skill they want to learn today. "
                    "Keep it to 3–4 sentences."
                )
                message = await self._call_llm(
                    system_prompt=SYSTEM_PROMPT,
                    user_input=greeting_prompt,
                )
                return {
                    "agent": self.name,
                    "message": message,
                    "action": "await_topic",
                    "next_state": SessionState.GREETING,
                }

            # Subsequent messages in GREETING state — detect intent
            user_lower = user_input.lower().strip()

            # User says yes/ready — start assessment
            if user_lower in {"yes", "ya", "yep", "ok", "okay", "sure", "ready", "start", "begin", "yeah"}:
                return {
                    "agent": self.name,
                    "message": "Perfect! Let's begin with a quick learning style assessment so I can personalise your experience.",
                    "action": "start_assessment",
                    "next_state": SessionState.ASSESSING,
                }

            # User mentions a topic — start assessment first
            topic_keywords = ["learn", "study", "teach", "explain", "understand", "how", "what", "why",
                              "show", "help", "want", "need", "practice", "course"]
            if any(w in user_lower for w in topic_keywords):
                return {
                    "agent": self.name,
                    "message": (
                        "Great! Before we dive in, let me quickly assess your learning style "
                        "so I can tailor lessons just for you. Ready to answer a few short questions?"
                    ),
                    "action": "start_assessment",
                    "next_state": SessionState.ASSESSING,
                    "topic": user_input,
                }

            # General conversation
            llm_history = self._build_history(context)
            message = await self._call_llm(
                system_prompt=SYSTEM_PROMPT,
                user_input=user_input,
                history=llm_history,
            )
            return {
                "agent": self.name,
                "message": message,
                "action": "general_response",
                "next_state": SessionState.GREETING,
            }

        # ── PLANNING bridge (orchestrator called during planning transition) ──────
        if session_state == SessionState.PLANNING:
            message = await self._call_llm(
                system_prompt=SYSTEM_PROMPT,
                user_input=(
                    "The student has completed the learning style assessment. "
                    "Tell them we are now going to build their personalised study plan. "
                    "Be brief and encouraging."
                ),
                history=self._build_history(context),
            )
            return {
                "agent": self.name,
                "message": message,
                "action": "handoff_to_planning",
                "next_state": SessionState.PLANNING,
            }

        # ── General fallback ─────────────────────────────────────────────────────
        llm_history = self._build_history(context)
        message = await self._call_llm(
            system_prompt=SYSTEM_PROMPT,
            user_input=user_input,
            history=llm_history,
        )
        return {
            "agent": self.name,
            "message": message,
            "action": "general_response",
        }

    def _build_history(self, context: dict[str, Any]) -> list[dict[str, str]]:
        history = []
        for entry in context.get("conversation_history", [])[-10:]:
            if entry.get("user_message"):
                history.append({"role": "user", "content": entry["user_message"]})
            if entry.get("agent_response"):
                history.append({"role": "assistant", "content": entry["agent_response"]})
        return history
