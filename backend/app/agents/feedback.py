"""Feedback Agent — analyses progress and provides actionable learning feedback."""

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are a learning coach and progress analyst for an LMS tutoring system.

Your role is to:
1. Analyse the student's learning progress (quiz scores, topics completed, time spent)
2. Identify strengths and areas for improvement
3. Provide specific, actionable recommendations tailored to their learning style
4. Be encouraging — celebrate wins, frame gaps as opportunities
5. Suggest concrete next steps

Base your analysis on the data provided. Do not fabricate numbers or assume information
that has not been given. Keep responses warm, concise, and motivating."""


class FeedbackAgent(BaseAgent):
    """Provides progress analysis and personalised learning recommendations."""

    def __init__(self):
        super().__init__(name="feedback")
        self.rag_service = None

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        if self.rag_service is None:
            try:
                self.rag_service = await get_rag_service()
            except Exception as e:
                logger.warning(f"RAG unavailable: {e}")

        progress = context.get("progress", {})
        quiz_scores: list = progress.get("quiz_scores", [])
        topics_done: list = progress.get("topics_completed", [])
        plan_topics: list = progress.get("plan_topics", [])
        learning_style = context.get("learning_style", "V")
        current_topic = context.get("topic", "")

        # Build a progress summary for the LLM
        style_names = {"V": "Visual", "A": "Auditory", "R": "Reading/Writing", "K": "Kinesthetic"}
        style_name = style_names.get(learning_style, "Visual")

        avg_score = (sum(quiz_scores) / len(quiz_scores)) if quiz_scores else None
        progress_summary = (
            f"Learning style: {style_name}\n"
            f"Current topic: {current_topic or 'not set'}\n"
            f"Topics completed: {len(topics_done)} "
            + (f"of {len(plan_topics)}" if plan_topics else "(plan not started)")
            + "\n"
            f"Quiz attempts: {len(quiz_scores)}\n"
            + (f"Average quiz score: {avg_score:.1f}%\n" if avg_score is not None else "No quizzes taken yet.\n")
        )

        history = self._build_history(context)

        response = await self._call_llm(
            system_prompt=SYSTEM_PROMPT,
            user_input=(
                f"Student progress data:\n{progress_summary}\n\n"
                f"Student message: {user_input}"
            ),
            history=history,
        )

        return {
            "agent": self.name,
            "message": response,
            "action": "feedback_delivered",
            "progress_snapshot": {
                "topics_done": len(topics_done),
                "quiz_attempts": len(quiz_scores),
                "avg_score": avg_score,
            },
        }

    def _build_history(self, context: dict[str, Any]) -> list[dict[str, str]]:
        history = []
        for entry in context.get("conversation_history", [])[-6:]:
            if entry.get("user_message"):
                history.append({"role": "user", "content": entry["user_message"]})
            if entry.get("agent_response"):
                history.append({"role": "assistant", "content": entry["agent_response"]})
        return history
