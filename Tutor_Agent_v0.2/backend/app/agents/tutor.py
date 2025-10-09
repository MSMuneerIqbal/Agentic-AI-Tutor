"""Tutor Agent - Delivers personalized lessons."""

from typing import Any

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings

settings = get_settings()


class TutorAgent(BaseAgent):
    """
    Tutor Agent delivers personalized lessons.

    Responsibilities:
    - Deliver lessons adapted to user's learning style
    - Use RAG tool to retrieve supporting content
    - Use TAVILY for live examples
    - Provide clear explanations with citations
    - Offer exercises and practice opportunities
    """

    def __init__(self):
        """Initialize Tutor Agent."""
        super().__init__(name="Tutor", model=settings.gemini_model)
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent."""
        return Agent(
            name="Tutor",
            model=self.model,
            instructions="""You are the Tutor Agent for an AI tutoring system.

Your role is to:
1. Deliver clear, engaging lessons adapted to the user's learning style
2. Break down complex topics into digestible chunks
3. Use examples, analogies, and practice exercises
4. Provide citations when using external sources
5. Check for understanding before moving forward
6. Encourage questions and provide supportive feedback

Learning Style Adaptation:
- Visual (V): Use diagrams, charts, visual metaphors
- Auditory (A): Use verbal explanations, discussions
- Reading (R): Provide detailed text explanations
- Kinesthetic (K): Focus on hands-on examples and practice

Lesson Structure:
1. Brief introduction to topic
2. Core explanation (adapted to learning style)
3. Example or analogy
4. Quick check for understanding
5. Practice exercise

Keep lessons concise (1-2 key points per message). Be encouraging and patient.

When using external sources (RAG or TAVILY), always cite them briefly:
- Example: "According to [Source], Docker containers..."

Available Tools (to be integrated):
- rag_tool.retrieve(topic) - Get relevant content from knowledge base
- tavily_tool.search(query) - Get live examples from web""",
        )

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute tutoring logic.

        Args:
            user_input: User question or response
            context: Lesson context (topic, learning_style, progress)

        Returns:
            Response dictionary with lesson content
        """
        topic = context.get("topic", "Docker and Kubernetes")
        learning_style = context.get("learning_style", "V")
        progress = context.get("progress", 0)

        # Simplified lesson delivery (in production, use agent + tools)
        if progress == 0:
            return {
                "agent": self.name,
                "message": self._get_lesson_intro(topic, learning_style),
                "action": "deliver_lesson",
                "topic": topic,
                "progress": 1,
            }

        # Continue lesson based on user response
        return {
            "agent": self.name,
            "message": (
                "Great question! Let me explain that further...\n\n"
                f"[Lesson content would be generated here based on: {user_input}]\n\n"
                "Do you have any questions about this?"
            ),
            "action": "continue_lesson",
            "topic": topic,
            "progress": progress + 1,
        }

    def _get_lesson_intro(self, topic: str, learning_style: str) -> str:
        """Get lesson introduction adapted to learning style."""
        intros = {
            "V": f"Let's learn about **{topic}**! 🎨\n\nImagine containers as shipping boxes...",
            "A": f"Let's talk about **{topic}**! 🎧\n\nThink of it this way...",
            "R": f"Let's study **{topic}**! 📚\n\nHere's a detailed explanation...",
            "K": f"Let's practice **{topic}**! 🛠️\n\nWe'll learn by doing...",
        }
        return intros.get(
            learning_style,
            f"Let's learn about **{topic}**!\n\n[Lesson content starts here]",
        )

