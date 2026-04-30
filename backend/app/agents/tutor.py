"""Tutor Agent — delivers personalised lessons using RAG + web search + real LLM calls."""

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are an expert tutor in an LMS (Learning Management System).

You teach any subject based solely on the content retrieved from the knowledge base and
web search results provided to you. Do NOT invent facts — ground every explanation in the
provided context. If the context doesn't cover something, say so honestly and offer to
look it up or suggest what to explore next.

Adapt your explanation style to the student's VARK learning style:
- Visual (V): use analogies, diagrams described in text, visual metaphors
- Auditory (A): conversational tone, think-aloud walkthroughs, discussion prompts
- Reading/Writing (R): structured prose, bullet lists, definitions, written exercises
- Kinesthetic (K): step-by-step instructions, "try this yourself" prompts, practical tasks

Be warm, precise, and encouraging. End each response with a check-in question or a
"try this" prompt to keep the student engaged."""


class TutorAgent(BaseAgent):
    """Delivers adaptive lessons from RAG knowledge base with web search augmentation."""

    def __init__(self):
        super().__init__(name="tutor")
        self.rag_service = None

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        topic = context.get("topic") or user_input
        learning_style = context.get("learning_style", "V")
        progress = context.get("progress", 0)

        # Lazy-init RAG service
        if self.rag_service is None:
            try:
                self.rag_service = await get_rag_service()
            except Exception as e:
                logger.warning(f"RAG service unavailable: {e}")

        # Brainstorming mode
        if any(w in user_input.lower() for w in ["brainstorm", "ideas", "think together", "explore"]):
            return await self._brainstorm(user_input, topic, learning_style, context)

        # Build RAG + web context
        rag_context = await self._fetch_context(user_input, topic)

        # Build conversation history for continuity
        history = self._build_history(context)

        style_names = {"V": "Visual", "A": "Auditory", "R": "Reading/Writing", "K": "Kinesthetic"}
        style_instruction = f"The student is a {style_names.get(learning_style, 'Visual')} learner."

        system = f"{SYSTEM_PROMPT}\n\n{style_instruction}"

        lesson = await self._call_llm(
            system_prompt=system,
            user_input=(
                f"Topic: {topic}\n"
                f"Student message: {user_input}\n"
                f"This is lesson interaction #{progress + 1}."
            ),
            rag_context=rag_context,
            history=history,
        )

        return {
            "agent": self.name,
            "message": lesson,
            "action": "deliver_lesson" if progress == 0 else "continue_lesson",
            "topic": topic,
            "progress": progress + 1,
            "learning_style": learning_style,
        }

    async def _brainstorm(self, user_input: str, topic: str, learning_style: str, context: dict[str, Any]) -> dict[str, Any]:
        """Collaborative brainstorming session with the student."""
        rag_context = await self._fetch_context(user_input, topic)
        history = self._build_history(context)

        brainstorm_prompt = (
            "You are now in brainstorming mode. Think collaboratively with the student. "
            "Build on their ideas, offer alternative angles, ask probing questions, and "
            "help them explore the topic creatively. Use the knowledge base context to "
            "ground ideas in reality."
        )

        response = await self._call_llm(
            system_prompt=f"{SYSTEM_PROMPT}\n\n{brainstorm_prompt}",
            user_input=f"Topic: {topic}\nStudent: {user_input}",
            rag_context=rag_context,
            history=history,
            temperature=0.85,
        )

        return {
            "agent": self.name,
            "message": response,
            "action": "brainstorm",
            "topic": topic,
        }

    async def _fetch_context(self, query: str, topic: str) -> str:
        """Fetch RAG + web context and format as a single string."""
        if not self.rag_service:
            return ""

        parts: list[str] = []

        try:
            lesson_data = await self.rag_service.get_tutor_lesson_content(topic)
            rag_chunks = lesson_data.get("rag_content", [])
            if rag_chunks:
                parts.append("Knowledge base content:\n" + "\n\n".join(
                    f"[{c.get('source', 'KB')}] {c['content']}" for c in rag_chunks[:3]
                ))

            web = lesson_data.get("web_results", [])
            if web:
                parts.append("Web resources:\n" + "\n".join(
                    f"- {r.get('title', '')}: {r.get('content', '')[:300]}" for r in web[:2]
                ))
        except Exception as e:
            logger.warning(f"Context fetch failed: {e}")

        return "\n\n".join(parts)

    def _build_history(self, context: dict[str, Any]) -> list[dict[str, str]]:
        history = []
        for entry in context.get("conversation_history", [])[-8:]:
            if entry.get("user_message"):
                history.append({"role": "user", "content": entry["user_message"]})
            if entry.get("agent_response"):
                history.append({"role": "assistant", "content": entry["agent_response"]})
        return history
