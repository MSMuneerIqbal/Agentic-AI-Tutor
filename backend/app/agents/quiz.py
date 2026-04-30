"""Quiz Agent — generates and evaluates quizzes using LLM + RAG content."""

import json
import logging
from typing import Any, Dict, List

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
settings = get_settings()

QUIZ_GEN_PROMPT = """You are a quiz generator for an LMS tutoring system.

Given a topic and optional knowledge-base excerpts, produce exactly {n} multiple-choice questions.
Use only factual content from the provided context. Do NOT invent facts.
If context is thin, ask fundamental conceptual questions about the topic.

Return ONLY valid JSON — no markdown fences, no extra text:
[
  {{
    "question": "...",
    "options": {{"a": "...", "b": "...", "c": "...", "d": "..."}},
    "correct": "a",
    "explanation": "..."
  }},
  ...
]"""

EVAL_PROMPT = """You are an expert tutor evaluating a student's quiz performance.

Quiz topic: {topic}
Score: {score}/{total} ({pct:.0f}%)
Passed: {passed}

Student answers summary:
{summary}

Write 2–3 sentences of constructive, encouraging feedback. Point out a specific strength
and one area to review if they scored below 80%. Be warm and motivating."""


class QuizAgent(BaseAgent):
    """Generates LLM-powered quizzes from RAG content; state is session-scoped."""

    def __init__(self):
        super().__init__(name="quiz")
        self.rag_service = None

    def _load_qs(self, context: dict[str, Any]) -> dict[str, Any]:
        return context.get("quiz_state") or {
            "questions": [],
            "index": 0,
            "answers": [],
            "score": 0,
            "topic": None,
        }

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        topic = context.get("topic") or "general knowledge"

        if self.rag_service is None:
            try:
                self.rag_service = await get_rag_service()
            except Exception as e:
                logger.warning(f"RAG unavailable: {e}")

        qs = self._load_qs(context)

        # No active quiz → start a new one
        if not qs["questions"]:
            return await self._start_quiz(topic, context, qs)

        # Active quiz → process answer
        return await self._process_answer(user_input, topic, context, qs)

    # ── quiz lifecycle ──────────────────────────────────────────────────────────

    async def _start_quiz(self, topic: str, context: dict[str, Any], qs: dict[str, Any]) -> dict[str, Any]:
        n = 5
        rag_context = await self._get_rag_context(topic)

        questions = await self._generate_questions(topic, rag_context, n)
        if not questions:
            return {
                "agent": self.name,
                "message": f"I couldn't generate quiz questions for '{topic}' right now. Please try a different topic or check back later.",
                "action": "quiz_error",
                "quiz_state": None,
            }

        qs["questions"] = questions
        qs["index"] = 0
        qs["answers"] = []
        qs["score"] = 0
        qs["topic"] = topic

        q = questions[0]
        return {
            "agent": self.name,
            "message": (
                f"Quiz time! I'll ask you {len(questions)} questions about **{topic}**.\n\n"
                f"**Question 1 of {len(questions)}:** {q['question']}\n\n"
                + self._fmt_options(q)
            ),
            "action": "start_quiz",
            "topic": topic,
            "total_questions": len(questions),
            "quiz_state": qs,
        }

    async def _process_answer(self, user_input: str, topic: str, context: dict[str, Any], qs: dict[str, Any]) -> dict[str, Any]:
        idx = qs["index"]
        q = qs["questions"][idx]
        chosen = self._parse_choice(user_input)
        correct = q.get("correct", "a")
        is_correct = chosen == correct

        if is_correct:
            qs["score"] += 1

        qs["answers"].append({
            "question": q["question"],
            "chosen": chosen,
            "correct": correct,
            "is_correct": is_correct,
        })
        qs["index"] += 1

        feedback = (
            f"Correct! {q.get('explanation', '')}"
            if is_correct
            else f"Not quite. The correct answer is **({correct})** {q['options'].get(correct, '')}. {q.get('explanation', '')}"
        )

        # Quiz complete
        if qs["index"] >= len(qs["questions"]):
            return await self._finish_quiz(topic, qs, feedback)

        # Next question
        next_q = qs["questions"][qs["index"]]
        return {
            "agent": self.name,
            "message": (
                f"{'✅' if is_correct else '❌'} {feedback}\n\n"
                f"**Question {qs['index'] + 1} of {len(qs['questions'])}:** {next_q['question']}\n\n"
                + self._fmt_options(next_q)
            ),
            "action": "next_question",
            "topic": topic,
            "quiz_state": qs,
        }

    async def _finish_quiz(self, topic: str, qs: dict[str, Any], last_feedback: str) -> dict[str, Any]:
        total = len(qs["questions"])
        score = qs["score"]
        pct = (score / total * 100) if total else 0
        passed = pct >= 70

        summary = "\n".join(
            f"Q{i+1}: {'✓' if a['is_correct'] else '✗'} {a['question'][:60]}..."
            for i, a in enumerate(qs["answers"])
        )

        try:
            eval_text = await self._call_llm(
                system_prompt=EVAL_PROMPT.format(
                    topic=topic, score=score, total=total, pct=pct,
                    passed=passed, summary=summary,
                ),
                user_input="Generate quiz feedback.",
                temperature=0.6,
            )
        except Exception:
            eval_text = (
                f"You scored {score}/{total} ({pct:.0f}%)."
                + (" Great work!" if passed else " Keep practising!")
            )

        return {
            "agent": self.name,
            "message": (
                f"{'✅' if passed else '❌'} {last_feedback}\n\n"
                f"**Quiz Complete!** Score: {score}/{total} ({pct:.0f}%)\n\n"
                f"{eval_text}"
            ),
            "action": "quiz_complete",
            "topic": topic,
            "score": score,
            "total_questions": total,
            "score_percentage": pct,
            "passed": passed,
            "quiz_result": "passed" if passed else "failed",
            "quiz_state": None,  # clear state
        }

    # ── helpers ─────────────────────────────────────────────────────────────────

    async def _generate_questions(self, topic: str, rag_context: str, n: int) -> List[Dict[str, Any]]:
        prompt = (
            f"Topic: {topic}\n"
            f"Number of questions: {n}\n\n"
            f"{'Context:\n' + rag_context if rag_context else 'No context available — use general knowledge.'}"
        )
        try:
            raw = await self._call_llm(
                system_prompt=QUIZ_GEN_PROMPT.format(n=n),
                user_input=prompt,
                temperature=0.5,
            )
            # Strip markdown fences if present
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            questions = json.loads(raw)
            # Validate structure
            valid = []
            for q in questions:
                if isinstance(q, dict) and "question" in q and "options" in q and "correct" in q:
                    valid.append(q)
            return valid
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return []

    async def _get_rag_context(self, topic: str) -> str:
        if not self.rag_service:
            return ""
        try:
            data = await self.rag_service.get_quiz_content(topic)
            chunks = data.get("rag_content", [])
            return "\n\n".join(c["content"] for c in chunks[:4] if c.get("content"))
        except Exception as e:
            logger.warning(f"RAG context fetch failed: {e}")
            return ""

    def _parse_choice(self, user_input: str) -> str:
        ui = user_input.lower().strip()
        if ui in {"a", "b", "c", "d"}:
            return ui
        for letter in ("a", "b", "c", "d"):
            if f"({letter})" in ui or ui.startswith(letter + " ") or ui.startswith(letter + "."):
                return letter
        return ui[0] if ui and ui[0] in "abcd" else "a"

    def _fmt_options(self, q: dict) -> str:
        opts = q.get("options", {})
        return "\n".join(f"**({k})** {v}" for k, v in opts.items()) + "\n\nType a, b, c, or d."
