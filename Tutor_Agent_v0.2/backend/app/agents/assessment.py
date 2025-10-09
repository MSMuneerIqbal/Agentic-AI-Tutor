"""Assessment Agent - Conducts VARK learning style assessment."""

from typing import Any

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings

settings = get_settings()


class AssessmentAgent(BaseAgent):
    """
    Assessment Agent conducts VARK learning style assessment.

    Responsibilities:
    - Ask 5-12 questions to determine learning style (Visual, Auditory, Reading, Kinesthetic)
    - Evaluate responses to identify primary learning preference
    - Store assessment results
    - Provide learning style summary to user
    """

    def __init__(self):
        """Initialize Assessment Agent."""
        super().__init__(name="Assessment", model=settings.gemini_model)
        self.agent = self._create_agent()
        self.questions_asked = 0
        self.max_questions = 12

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent."""
        return Agent(
            name="Assessment",
            model=self.model,
            instructions="""You are the Assessment Agent for an AI tutoring system.

Your role is to conduct a VARK learning style assessment (5-12 questions).

VARK Learning Styles:
- V (Visual): Learns best through images, diagrams, and spatial understanding
- A (Auditory): Learns best through listening and discussion
- R (Reading/Writing): Learns best through reading and note-taking
- K (Kinesthetic): Learns best through hands-on practice and movement

Assessment Process:
1. Ask ONE question at a time about learning preferences
2. Present questions in a friendly, conversational manner
3. Wait for user response before proceeding
4. Ask 5-12 questions total (adjust based on clarity of pattern)
5. After assessment, summarize the user's learning style

Question Examples:
- "When learning something new, do you prefer: (a) diagrams and charts, (b) listening to explanations, (c) reading instructions, or (d) trying it hands-on?"
- "How do you best remember information: (a) visualizing it, (b) hearing it, (c) writing it down, or (d) practicing it?"

Keep questions clear, concise, and engaging. After assessment, provide a brief, encouraging summary of their learning style.""",
        )

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute assessment logic.

        Args:
            user_input: User response to question
            context: Assessment context (questions asked, answers)

        Returns:
            Response dictionary with next question or results
        """
        answers = context.get("answers", [])
        self.questions_asked = len(answers)

        # First interaction - ask first question
        if self.questions_asked == 0:
            return {
                "agent": self.name,
                "message": (
                    "Let's discover your learning style! I'll ask you a few quick questions.\n\n"
                    "**Question 1:** When you're learning something new, what helps you most?\n"
                    "(a) Diagrams, charts, or visual aids\n"
                    "(b) Listening to explanations or discussions\n"
                    "(c) Reading detailed instructions or notes\n"
                    "(d) Trying it out hands-on"
                ),
                "action": "collect_answer",
                "question_number": 1,
            }

        # Store answer and continue assessment
        answers.append({"question": self.questions_asked, "answer": user_input})

        # Continue assessment (simplified - in production, use agent to generate questions)
        if self.questions_asked < 5:  # Minimum 5 questions
            return {
                "agent": self.name,
                "message": f"**Question {self.questions_asked + 1}:** How do you prefer to study for a test?\n"
                "(a) Review diagrams and visual summaries\n"
                "(b) Listen to recordings or discuss with others\n"
                "(c) Read and re-read your notes\n"
                "(d) Practice with real examples",
                "action": "collect_answer",
                "question_number": self.questions_asked + 1,
                "answers": answers,
            }

        # Assessment complete - analyze results (simplified)
        # In production, use more sophisticated analysis
        style = self._analyze_answers(answers)

        return {
            "agent": self.name,
            "message": (
                f"✅ Assessment complete!\n\n"
                f"Your primary learning style is: **{style}**\n\n"
                f"{self._get_style_description(style)}\n\n"
                f"I'll use this to personalize your learning experience!"
            ),
            "action": "assessment_complete",
            "learning_style": style,
            "answers": answers,
        }

    def _analyze_answers(self, answers: list[dict]) -> str:
        """
        Analyze answers to determine learning style.

        Args:
            answers: List of answer dictionaries

        Returns:
            Learning style (V/A/R/K)
        """
        # Simplified analysis - count letter choices
        counts = {"a": 0, "b": 0, "c": 0, "d": 0}
        for answer in answers:
            choice = answer["answer"].lower().strip()
            if choice in counts:
                counts[choice] += 1

        # Map to VARK
        max_choice = max(counts, key=counts.get)
        style_map = {"a": "V", "b": "A", "c": "R", "d": "K"}
        return style_map.get(max_choice, "V")

    def _get_style_description(self, style: str) -> str:
        """Get description of learning style."""
        descriptions = {
            "V": "You're a **Visual learner**! You learn best through diagrams, charts, and visual representations.",
            "A": "You're an **Auditory learner**! You learn best through listening and verbal explanations.",
            "R": "You're a **Reading/Writing learner**! You learn best through reading and taking notes.",
            "K": "You're a **Kinesthetic learner**! You learn best through hands-on practice and real examples.",
        }
        return descriptions.get(style, "You have a unique learning style!")

