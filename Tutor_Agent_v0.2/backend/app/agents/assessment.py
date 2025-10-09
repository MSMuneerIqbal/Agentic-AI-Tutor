"""Assessment Agent - Conducts VARK learning style assessment."""

import uuid
from typing import Any

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.assessment import AssessmentResult, LearningStyle

settings = get_settings()
logger = get_logger(__name__)


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
        self.min_questions = 5
        
        # VARK assessment questions
        self.questions = [
            {
                "question": "When learning something new, what helps you most?",
                "options": {
                    "a": "Diagrams, charts, or visual aids",
                    "b": "Listening to explanations or discussions", 
                    "c": "Reading detailed instructions or notes",
                    "d": "Trying it out hands-on"
                }
            },
            {
                "question": "How do you best remember information?",
                "options": {
                    "a": "Visualizing it in your mind",
                    "b": "Hearing it repeated or discussed",
                    "c": "Writing it down and reading it",
                    "d": "Practicing it repeatedly"
                }
            },
            {
                "question": "When studying for a test, you prefer to:",
                "options": {
                    "a": "Review diagrams and visual summaries",
                    "b": "Listen to recordings or discuss with others",
                    "c": "Read and re-read your notes",
                    "d": "Practice with real examples"
                }
            },
            {
                "question": "In a classroom, you learn best when the teacher:",
                "options": {
                    "a": "Uses visual aids, diagrams, or demonstrations",
                    "b": "Explains concepts verbally and encourages discussion",
                    "c": "Provides written materials and handouts",
                    "d": "Lets you try things hands-on"
                }
            },
            {
                "question": "When you need to understand a complex process, you:",
                "options": {
                    "a": "Draw diagrams or flowcharts",
                    "b": "Talk through it with someone",
                    "c": "Read step-by-step instructions",
                    "d": "Try to do it yourself first"
                }
            },
            {
                "question": "You prefer learning materials that are:",
                "options": {
                    "a": "Rich in images, charts, and visual elements",
                    "b": "Audio-based or discussion-focused",
                    "c": "Text-heavy with detailed explanations",
                    "d": "Interactive and hands-on"
                }
            },
            {
                "question": "When solving a problem, you typically:",
                "options": {
                    "a": "Draw it out or visualize the solution",
                    "b": "Talk it through out loud",
                    "c": "Write down your thoughts and reasoning",
                    "d": "Try different approaches experimentally"
                }
            },
            {
                "question": "You remember things best when you:",
                "options": {
                    "a": "See them in a visual format",
                    "b": "Hear them explained or discussed",
                    "c": "Read about them in detail",
                    "d": "Experience them directly"
                }
            }
        ]

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
            context: Assessment context (questions asked, answers, user_id, session_id)

        Returns:
            Response dictionary with next question or results
        """
        answers = context.get("answers", [])
        self.questions_asked = len(answers)
        user_id = context.get("user_id")
        session_id = context.get("session_id")

        # First interaction - ask first question
        if self.questions_asked == 0:
            return await self._ask_question(1, answers, user_id, session_id)

        # Validate user input
        if not self._validate_answer(user_input):
            return {
                "agent": self.name,
                "message": (
                    "Please choose one of the options (a, b, c, or d). "
                    "You can also type the full answer if you prefer!"
                ),
                "action": "collect_answer",
                "question_number": self.questions_asked,
                "answers": answers,
                "error": "invalid_input",
            }

        # Store answer
        answers.append({
            "question_number": self.questions_asked,
            "question": self.questions[self.questions_asked - 1]["question"],
            "answer": user_input,
            "normalized_answer": self._normalize_answer(user_input),
        })

        # Check if we should continue or complete assessment
        if self.questions_asked < self.min_questions:
            # Continue with more questions
            return await self._ask_question(self.questions_asked + 1, answers, user_id, session_id)
        
        # Check if we have enough data to determine learning style
        if self.questions_asked >= self.min_questions:
            style_confidence = self._calculate_confidence(answers)
            
            # If high confidence or max questions reached, complete assessment
            if style_confidence >= 0.7 or self.questions_asked >= self.max_questions:
                return await self._complete_assessment(answers, user_id, session_id)
            
            # Continue with more questions for better accuracy
            return await self._ask_question(self.questions_asked + 1, answers, user_id, session_id)

        # Fallback - complete assessment
        return await self._complete_assessment(answers, user_id, session_id)

    async def _ask_question(self, question_num: int, answers: list, user_id: str | None, session_id: str | None) -> dict[str, Any]:
        """Ask a specific question."""
        if question_num > len(self.questions):
            # All questions asked, complete assessment
            return await self._complete_assessment(answers, user_id, session_id)
        
        question_data = self.questions[question_num - 1]
        options_text = "\n".join([f"({key}) {value}" for key, value in question_data["options"].items()])
        
        return {
            "agent": self.name,
            "message": (
                f"**Question {question_num}:** {question_data['question']}\n\n"
                f"{options_text}\n\n"
                f"Please choose (a), (b), (c), or (d)."
            ),
            "action": "collect_answer",
            "question_number": question_num,
            "answers": answers,
        }

    async def _complete_assessment(self, answers: list, user_id: str | None, session_id: str | None) -> dict[str, Any]:
        """Complete the assessment and save results."""
        # Analyze answers to determine learning style
        style, confidence = self._analyze_answers(answers)
        
        # Save assessment result to database
        if user_id:
            try:
                async for db in get_db():
                    assessment_result = AssessmentResult(
                        user_id=uuid.UUID(user_id),
                        style=LearningStyle(style),
                        answers=answers,
                    )
                    db.add(assessment_result)
                    await db.commit()
                    await db.refresh(assessment_result)
                    
                    logger.info(
                        f"Assessment completed and saved",
                        extra={
                            "user_id": user_id,
                            "session_id": session_id,
                            "learning_style": style,
                            "confidence": confidence,
                            "questions_asked": len(answers),
                        },
                    )
                    break
            except Exception as e:
                logger.error(f"Failed to save assessment result: {str(e)}")
        
        return {
            "agent": self.name,
            "message": (
                f"✅ Assessment complete!\n\n"
                f"Your primary learning style is: **{self._get_style_name(style)}**\n\n"
                f"{self._get_style_description(style)}\n\n"
                f"I'll use this to personalize your learning experience! "
                f"Ready to start your personalized lessons?"
            ),
            "action": "assessment_complete",
            "learning_style": style,
            "confidence": confidence,
            "answers": answers,
            "next_state": "planning",
        }

    def _validate_answer(self, user_input: str) -> bool:
        """Validate user input for assessment questions."""
        user_input = user_input.lower().strip()
        
        # Check for single letter choices
        if user_input in ["a", "b", "c", "d"]:
            return True
        
        # Check for full text matches
        valid_responses = [
            "diagrams", "charts", "visual", "visual aids", "visualizing", "visualize",
            "listening", "hearing", "discussion", "discuss", "audio", "verbal",
            "reading", "notes", "written", "text", "instructions", "handouts",
            "hands-on", "practice", "trying", "experimental", "interactive"
        ]
        
        return any(valid in user_input for valid in valid_responses)

    def _normalize_answer(self, user_input: str) -> str:
        """Normalize user input to VARK choice."""
        user_input = user_input.lower().strip()
        
        # Direct letter choices
        if user_input in ["a", "b", "c", "d"]:
            return user_input
        
        # Visual indicators
        visual_keywords = ["diagrams", "charts", "visual", "visualizing", "visualize", "images", "pictures"]
        if any(keyword in user_input for keyword in visual_keywords):
            return "a"
        
        # Auditory indicators
        auditory_keywords = ["listening", "hearing", "discussion", "discuss", "audio", "verbal", "talk"]
        if any(keyword in user_input for keyword in auditory_keywords):
            return "b"
        
        # Reading indicators
        reading_keywords = ["reading", "notes", "written", "text", "instructions", "handouts", "write"]
        if any(keyword in user_input for keyword in reading_keywords):
            return "c"
        
        # Kinesthetic indicators
        kinesthetic_keywords = ["hands-on", "practice", "trying", "experimental", "interactive", "doing"]
        if any(keyword in user_input for keyword in kinesthetic_keywords):
            return "d"
        
        # Default to visual if unclear
        return "a"

    def _analyze_answers(self, answers: list[dict]) -> tuple[str, float]:
        """
        Analyze answers to determine learning style with confidence.

        Args:
            answers: List of answer dictionaries

        Returns:
            Tuple of (learning_style, confidence)
        """
        # Count normalized choices
        counts = {"a": 0, "b": 0, "c": 0, "d": 0}
        for answer in answers:
            choice = answer.get("normalized_answer", "a")
            if choice in counts:
                counts[choice] += 1

        # Calculate confidence based on distribution
        total_answers = sum(counts.values())
        if total_answers == 0:
            return "V", 0.0
        
        max_count = max(counts.values())
        confidence = max_count / total_answers

        # Map to VARK
        max_choice = max(counts.keys(), key=lambda k: counts[k])
        style_map = {"a": "V", "b": "A", "c": "R", "d": "K"}
        style = style_map.get(max_choice, "V")
        
        return style, confidence

    def _calculate_confidence(self, answers: list[dict]) -> float:
        """Calculate confidence in learning style determination."""
        if not answers:
            return 0.0
        
        style, confidence = self._analyze_answers(answers)
        return confidence

    def _get_style_name(self, style: str) -> str:
        """Get full name of learning style."""
        names = {
            "V": "Visual",
            "A": "Auditory", 
            "R": "Reading/Writing",
            "K": "Kinesthetic",
        }
        return names.get(style, "Visual")

    def _get_style_description(self, style: str) -> str:
        """Get description of learning style."""
        descriptions = {
            "V": "You're a **Visual learner**! You learn best through diagrams, charts, and visual representations.",
            "A": "You're an **Auditory learner**! You learn best through listening and verbal explanations.",
            "R": "You're a **Reading/Writing learner**! You learn best through reading and taking notes.",
            "K": "You're a **Kinesthetic learner**! You learn best through hands-on practice and real examples.",
        }
        return descriptions.get(style, "You have a unique learning style!")

