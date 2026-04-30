"""Assessment Agent — conducts VARK learning style assessment."""

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.core.session_store import session_store

settings = get_settings()
logger = logging.getLogger(__name__)

VARK_QUESTIONS = [
    {
        "question": "When learning something new, what helps you most?",
        "options": {
            "a": "Diagrams, charts, or visual aids",
            "b": "Listening to explanations or discussions",
            "c": "Reading detailed instructions or notes",
            "d": "Trying it out hands-on",
        },
    },
    {
        "question": "How do you best remember information?",
        "options": {
            "a": "Visualising it in your mind",
            "b": "Hearing it repeated or discussed",
            "c": "Writing it down and reading it",
            "d": "Practising it repeatedly",
        },
    },
    {
        "question": "When studying for a test, you prefer to:",
        "options": {
            "a": "Review diagrams and visual summaries",
            "b": "Listen to recordings or discuss with others",
            "c": "Read and re-read your notes",
            "d": "Practise with real examples",
        },
    },
    {
        "question": "In a classroom, you learn best when the teacher:",
        "options": {
            "a": "Uses visual aids, diagrams, or demonstrations",
            "b": "Explains concepts verbally and encourages discussion",
            "c": "Provides written materials and handouts",
            "d": "Lets you try things hands-on",
        },
    },
    {
        "question": "When you need to understand a complex process, you:",
        "options": {
            "a": "Draw diagrams or flowcharts",
            "b": "Talk through it with someone",
            "c": "Read step-by-step instructions",
            "d": "Try to do it yourself first",
        },
    },
    {
        "question": "You prefer learning materials that are:",
        "options": {
            "a": "Rich in images, charts, and visual elements",
            "b": "Audio-based or discussion-focused",
            "c": "Text-heavy with detailed explanations",
            "d": "Interactive and hands-on",
        },
    },
]

MIN_QUESTIONS = 5
MAX_QUESTIONS = len(VARK_QUESTIONS)


class AssessmentAgent(BaseAgent):
    """Conducts the VARK learning style assessment and persists results."""

    def __init__(self):
        super().__init__(name="assessment")

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        answers: list[dict] = list(context.get("answers", []))
        # current_question tracks which question is currently displayed (1-indexed, 0 = none shown)
        current_question: int = context.get("current_question", 0)
        user_id = context.get("user_id")
        session_id = context.get("session_id")

        # No question displayed yet — show Q1
        if current_question == 0:
            return self._ask_question(1, answers)

        # A question is on screen — the user is answering it
        normalized = self._normalize(user_input)
        if not normalized:
            return {
                "agent": self.name,
                "message": "Please choose one of the options: (a), (b), (c), or (d).",
                "action": "collect_answer",
                "question_number": current_question,
                "current_question": current_question,
                "answers": answers,
            }

        # Record the answer for the current question
        q = VARK_QUESTIONS[current_question - 1]
        answers.append({
            "question_number": current_question,
            "question": q["question"],
            "answer": user_input,
            "normalized_answer": normalized,
        })

        answered = len(answers)

        # Decide: continue or complete
        if answered < MIN_QUESTIONS:
            return self._ask_question(current_question + 1, answers)

        confidence = self._confidence(answers)
        if confidence >= 0.7 or answered >= MAX_QUESTIONS:
            return await self._complete(answers, user_id, session_id)

        if answered < MAX_QUESTIONS:
            return self._ask_question(current_question + 1, answers)

        return await self._complete(answers, user_id, session_id)

    # ── helpers ────────────────────────────────────────────────────────────────

    def _ask_question(self, num: int, answers: list) -> dict[str, Any]:
        if num > MAX_QUESTIONS:
            return {
                "agent": self.name,
                "message": "Assessment complete!",
                "action": "assessment_complete",
                "current_question": num,
                "answers": answers,
            }
        q = VARK_QUESTIONS[num - 1]
        options = "\n".join(f"({k}) {v}" for k, v in q["options"].items())
        return {
            "agent": self.name,
            "message": (
                f"**Question {num} of {MAX_QUESTIONS}:** {q['question']}\n\n"
                f"{options}\n\nPlease choose (a), (b), (c), or (d)."
            ),
            "action": "collect_answer",
            "question_number": num,
            "current_question": num,
            "answers": answers,
        }

    async def _complete(
        self, answers: list, user_id: str | None, session_id: str | None
    ) -> dict[str, Any]:
        style, confidence = self._analyze(answers)

        if session_id:
            try:
                await session_store.set_session(
                    f"assessment:{session_id}",
                    {
                        "user_id": user_id,
                        "style": style,
                        "confidence": confidence,
                        "answers": answers,
                        "completed": True,
                    },
                    ttl=86400,
                )
            except Exception as exc:
                logger.error(f"Failed to save assessment: {exc}")

        style_names = {"V": "Visual", "A": "Auditory", "R": "Reading/Writing", "K": "Kinesthetic"}
        style_descs = {
            "V": "You grasp concepts quickly through diagrams, charts, and visual representations.",
            "A": "You retain information best through listening, discussion, and verbal explanations.",
            "R": "You excel by reading detailed explanations and taking structured notes.",
            "K": "You learn most effectively through hands-on practice and real-world application.",
        }

        return {
            "agent": self.name,
            "message": (
                f"Assessment complete!\n\n"
                f"Your primary learning style is **{style_names.get(style, 'Visual')}**.\n\n"
                f"{style_descs.get(style, '')}\n\n"
                "I'll use this to personalise your learning experience. "
                "Let's create your study plan!"
            ),
            "action": "assessment_complete",
            "learning_style": style,
            "confidence": confidence,
            "current_question": MAX_QUESTIONS + 1,
            "answers": answers,
            "next_state": "planning",
        }

    def _normalize(self, user_input: str) -> str | None:
        ui = user_input.lower().strip()
        if ui in {"a", "b", "c", "d"}:
            return ui
        visual = {"diagram", "chart", "visual", "image", "picture"}
        auditory = {"listen", "hear", "discuss", "audio", "verbal", "talk"}
        reading = {"read", "note", "written", "text", "instruction", "handout", "write"}
        kinesthetic = {"hands-on", "practice", "try", "experiment", "interactive", "doing"}
        if any(k in ui for k in visual):
            return "a"
        if any(k in ui for k in auditory):
            return "b"
        if any(k in ui for k in reading):
            return "c"
        if any(k in ui for k in kinesthetic):
            return "d"
        return None

    def _analyze(self, answers: list) -> tuple[str, float]:
        counts = {"a": 0, "b": 0, "c": 0, "d": 0}
        for a in answers:
            choice = a.get("normalized_answer", "a")
            if choice in counts:
                counts[choice] += 1
        total = sum(counts.values()) or 1
        best = max(counts, key=lambda k: counts[k])
        return {"a": "V", "b": "A", "c": "R", "d": "K"}[best], counts[best] / total

    def _confidence(self, answers: list) -> float:
        _, conf = self._analyze(answers)
        return conf
