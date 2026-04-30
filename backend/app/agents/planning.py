"""Planning Agent — creates personalised study plans based on VARK style and RAG content."""

import logging
from typing import Any, Dict

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.services.plan_service import plan_service
from app.services.profile_service import profile_service
from app.services.rag_service import get_rag_service

settings = get_settings()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert academic planner for an LMS tutoring system.

Your task is to create a clear, structured, and personalised study plan based on:
- The student's stated goals and interests
- Their VARK learning style (Visual / Auditory / Reading / Kinesthetic)
- Course content retrieved from the knowledge base

The plan must:
1. Be broken into 3–5 concrete topics with estimated hours
2. Include specific, style-appropriate learning activities for each topic
3. Be encouraging and motivating in tone
4. Avoid filler or generic advice — every sentence should be actionable

Respond only with the study plan content, no preamble."""


class PlanningAgent(BaseAgent):
    """Creates personalised multi-topic study plans from RAG content and user goals."""

    def __init__(self):
        super().__init__(name="planning")
        self.rag_service = None

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        user_id = context.get("user_id")
        learning_style = context.get("learning_style") or "V"

        # Supplement learning style from profile if not already set
        if learning_style == "V" and user_id:
            try:
                profile = await profile_service.get_user_profile(user_id)
                style = profile.get("learning_style")
                if style:
                    learning_style = style
            except Exception as e:
                logger.warning(f"Could not load user profile: {e}")

        planning_stage = context.get("planning_stage", "ask_goals")

        if planning_stage == "ask_goals":
            return self._ask_goals(learning_style)

        if planning_stage == "ask_time":
            return self._ask_time(user_input)

        # Generate the full plan
        return await self._generate_plan(user_input, learning_style, context, user_id)

    # ── stage handlers ─────────────────────────────────────────────────────────

    def _ask_goals(self, learning_style: str) -> dict[str, Any]:
        adaptation = {
            "V": "I'll fill it with diagrams, charts, and visual walkthroughs.",
            "A": "I'll emphasise discussions, explanations, and audio-friendly content.",
            "R": "I'll include detailed reading materials and structured notes.",
            "K": "I'll centre it around hands-on exercises and real-world projects.",
        }.get(learning_style, "I'll tailor it to your preferences.")

        return {
            "agent": self.name,
            "message": (
                f"Let's build your personalised study plan! {adaptation}\n\n"
                "To get started, please tell me:\n"
                "• **What subject or skill** do you want to learn?\n"
                "• **What level** are you aiming for? (beginner / intermediate / advanced)\n"
                "• **Any specific topics or areas** you want to focus on?\n"
                "• **Why** are you learning this — career, project, curiosity?"
            ),
            "action": "collect_goals",
            "planning_stage": "ask_time",
        }

    def _ask_time(self, goals: str) -> dict[str, Any]:
        return {
            "agent": self.name,
            "message": (
                "Got it! One more thing to calibrate the plan:\n\n"
                "• How many **hours per week** can you dedicate?\n"
                "• Over how many **weeks** do you want to complete this?\n"
                "• Do you prefer **short daily sessions** (30–60 min) or **longer weekend blocks**?"
            ),
            "action": "collect_time",
            "planning_stage": "generate_plan",
            "goals": goals,
        }

    async def _generate_plan(
        self,
        user_input: str,
        learning_style: str,
        context: dict[str, Any],
        user_id: str | None,
    ) -> dict[str, Any]:
        goals = context.get("goals", user_input)

        # Fetch RAG content to ground the plan
        rag_context = ""
        if self.rag_service is None:
            try:
                self.rag_service = await get_rag_service()
            except Exception as e:
                logger.warning(f"RAG service unavailable: {e}")

        if self.rag_service:
            try:
                rag_data = await self.rag_service.get_planning_content(goals, user_input)
                chunks = rag_data.get("rag_content", [])
                if chunks:
                    rag_context = "\n\n".join(
                        f"[Source: {c.get('source', 'KB')}]\n{c['content']}"
                        for c in chunks[:4]
                    )
            except Exception as e:
                logger.warning(f"RAG content fetch failed: {e}")

        # Web results for enrichment
        web_context = ""
        if self.rag_service and self.rag_service.web_tool:
            try:
                web_results = await self.rag_service.web_tool.search_topic(goals, max_results=2)
                if web_results:
                    web_context = "\n".join(f"- {r.title}: {r.content[:200]}" for r in web_results)
            except Exception as e:
                logger.warning(f"Web search failed: {e}")

        combined_context = rag_context
        if web_context:
            combined_context += f"\n\nRecent web resources:\n{web_context}"

        style_names = {"V": "Visual", "A": "Auditory", "R": "Reading/Writing", "K": "Kinesthetic"}
        style_note = (
            f"The student's learning style is {style_names.get(learning_style, 'Visual')}. "
            "Tailor activity suggestions to this style."
        )

        llm_prompt = (
            f"Student goals: {goals}\n"
            f"Time commitment: {user_input}\n\n"
            f"{style_note}\n\n"
            "Create a structured 3–5 topic study plan with estimated hours and "
            "specific activities per topic. Format each topic as:\n"
            "**Topic N: [Title]** (~X hours)\n"
            "Description and key activities."
        )

        plan_text = await self._call_llm(
            system_prompt=SYSTEM_PROMPT,
            user_input=llm_prompt,
            rag_context=combined_context,
        )

        # Persist plan
        plan_id = None
        if user_id:
            try:
                saved = await plan_service.create_study_plan(
                    user_id=user_id,
                    plan_data={
                        "summary": plan_text[:500],
                        "goals": goals,
                        "learning_style": learning_style,
                        "full_plan": plan_text,
                    },
                )
                plan_id = saved.get("id")
            except Exception as e:
                logger.error(f"Failed to save plan: {e}")

        return {
            "agent": self.name,
            "message": f"Your personalised study plan is ready!\n\n{plan_text}\n\nShall we start with the first topic?",
            "action": "plan_complete",
            "plan_id": plan_id,
            "learning_style": learning_style,
            "next_state": "tutoring",
        }
