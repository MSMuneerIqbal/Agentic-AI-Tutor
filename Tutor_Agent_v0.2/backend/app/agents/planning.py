"""Planning Agent - Creates personalized study plans based on learning style assessment."""

import uuid
from typing import Any

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.assessment import LearningStyle
from app.models.plan import Plan
from app.services.profile_service import profile_service

settings = get_settings()
logger = get_logger(__name__)


class PlanningAgent(BaseAgent):
    """
    Planning Agent creates personalized study plans.

    Responsibilities:
    - Analyze user's learning style assessment
    - Gather user goals and preferences
    - Generate personalized study plan structure
    - Create learning milestones and checkpoints
    - Adapt plan based on learning style (VARK)
    """

    def __init__(self):
        """Initialize Planning Agent."""
        super().__init__(name="Planning", model=settings.gemini_model)
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent."""
        return Agent(
            name="Planning",
            model=self.model,
            instructions="""You are the Planning Agent for an AI tutoring system.

Your role is to create personalized study plans based on the user's learning style assessment.

Learning Style Adaptations:
- V (Visual): Use diagrams, charts, visual aids, mind maps, infographics
- A (Auditory): Use discussions, audio content, verbal explanations, group work
- R (Reading/Writing): Use detailed text, note-taking, written exercises, documentation
- K (Kinesthetic): Use hands-on practice, real examples, interactive exercises, projects

Planning Process:
1. Analyze the user's learning style from their assessment
2. Ask about their learning goals and interests
3. Determine their time commitment and availability
4. Create a structured study plan with topics and milestones
5. Adapt the plan format to their learning style
6. Set realistic timelines and checkpoints

Plan Structure:
- Main topics with subtopics
- Learning objectives for each topic
- Suggested activities based on learning style
- Estimated time for each topic
- Milestones and progress checkpoints
- Review and assessment points

Keep plans practical, achievable, and personalized to the user's learning style.""",
        )

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute planning logic.

        Args:
            user_input: User response to planning questions
            context: Planning context (user_id, session_id, learning_style, etc.)

        Returns:
            Response dictionary with planning questions or generated plan
        """
        user_id = context.get("user_id")
        session_id = context.get("session_id")
        planning_stage = context.get("planning_stage", "goals")

        # Get user profile and learning style
        learning_style = "V"  # Default to Visual
        if user_id:
            try:
                async for db in get_db():
                    profile = await profile_service.get_user_profile(user_id, db)
                    learning_style = profile.get("learning_style", "V")
                    break
            except Exception as e:
                logger.error(f"Failed to get user profile: {str(e)}")
                learning_style = "V"  # Default to Visual

        # Planning stages
        if planning_stage == "goals":
            return await self._ask_about_goals(learning_style, context)

        elif planning_stage == "interests":
            return await self._ask_about_interests(learning_style, context)

        elif planning_stage == "time_commitment":
            return await self._ask_about_time(learning_style, context)

        elif planning_stage == "generate_plan":
            return await self._generate_study_plan(user_input, learning_style, context)

        else:
            return {
                "agent": self.name,
                "message": "I'm ready to help you create a personalized study plan!",
                "action": "start_planning",
                "planning_stage": "goals",
            }

    async def _ask_about_goals(self, learning_style: str, context: dict[str, Any]) -> dict[str, Any]:
        """Ask about learning goals."""
        style_adaptation = self._get_style_adaptation(learning_style)
        
        return {
            "agent": self.name,
            "message": (
                f"Great! Now let's create your personalized study plan. {style_adaptation}\n\n"
                "**What are your main learning goals?**\n"
                "Please tell me:\n"
                "• What subject or topic do you want to learn?\n"
                "• What specific skills do you want to develop?\n"
                "• What level are you aiming for? (beginner, intermediate, advanced)\n"
                "• Any particular areas you want to focus on?"
            ),
            "action": "collect_goals",
            "planning_stage": "interests",
            "context": context,
        }

    async def _ask_about_interests(self, learning_style: str, context: dict[str, Any]) -> dict[str, Any]:
        """Ask about interests and preferences."""
        goals = context.get("goals", "")
        style_adaptation = self._get_style_adaptation(learning_style)
        
        return {
            "agent": self.name,
            "message": (
                f"Excellent goals! {style_adaptation}\n\n"
                "**What interests you most about this topic?**\n"
                "Please share:\n"
                "• What aspects excite you most?\n"
                "• Any real-world applications you're interested in?\n"
                "• Previous experience or knowledge you have?\n"
                "• Any challenges you've faced with this topic before?"
            ),
            "action": "collect_interests",
            "planning_stage": "time_commitment",
            "goals": goals,
            "context": context,
        }

    async def _ask_about_time(self, learning_style: str, context: dict[str, Any]) -> dict[str, Any]:
        """Ask about time commitment."""
        goals = context.get("goals", "")
        interests = context.get("interests", "")
        style_adaptation = self._get_style_adaptation(learning_style)
        
        return {
            "agent": self.name,
            "message": (
                f"Perfect! {style_adaptation}\n\n"
                "**What's your time commitment?**\n"
                "Please tell me:\n"
                "• How much time can you dedicate per week? (hours)\n"
                "• How many days per week can you study?\n"
                "• Do you prefer short daily sessions or longer weekly sessions?\n"
                "• Any time constraints or deadlines?"
            ),
            "action": "collect_time_commitment",
            "planning_stage": "generate_plan",
            "goals": goals,
            "interests": interests,
            "context": context,
        }

    async def _generate_study_plan(
        self, 
        user_input: str, 
        learning_style: str, 
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate the personalized study plan."""
        goals = context.get("goals", "")
        interests = context.get("interests", "")
        time_commitment = user_input
        
        # Generate plan structure based on learning style
        plan_structure = self._create_plan_structure(learning_style, goals, interests, time_commitment)
        
        # Save plan to database
        user_id = context.get("user_id")
        if user_id:
            try:
                async for db in get_db():
                    plan = Plan(
                        user_id=uuid.UUID(user_id),
                        summary=plan_structure["summary"],
                        topics=plan_structure["topics"],
                    )
                    db.add(plan)
                    await db.commit()
                    await db.refresh(plan)
                    
                    logger.info(
                        f"Study plan created and saved",
                        extra={
                            "user_id": user_id,
                            "plan_id": str(plan.id),
                            "learning_style": learning_style,
                            "topics_count": len(plan_structure["topics"]),
                        },
                    )
                    break
            except Exception as e:
                logger.error(f"Failed to save study plan: {str(e)}")
        
        return {
            "agent": self.name,
            "message": (
                f"🎉 **Your Personalized Study Plan is Ready!**\n\n"
                f"{plan_structure['summary']}\n\n"
                f"**Your Learning Style**: {self._get_style_name(learning_style)}\n"
                f"**Plan Overview**:\n{self._format_plan_overview(plan_structure['topics'])}\n\n"
                f"Ready to start your first lesson? I'll adapt all content to your {self._get_style_name(learning_style).lower()} learning style!"
            ),
            "action": "plan_complete",
            "plan_id": str(plan.id) if user_id else None,
            "learning_style": learning_style,
            "topics": plan_structure["topics"],
            "next_state": "tutoring",
        }

    def _create_plan_structure(
        self, 
        learning_style: str, 
        goals: str, 
        interests: str, 
        time_commitment: str
    ) -> dict[str, Any]:
        """Create structured study plan based on inputs."""
        # This is a simplified plan generator
        # In production, this would use the LLM to generate more sophisticated plans
        
        topics = [
            {
                "id": "topic_1",
                "title": "Introduction and Fundamentals",
                "description": "Basic concepts and terminology",
                "estimated_hours": 4,
                "activities": self._get_style_activities(learning_style, "fundamentals"),
                "milestones": ["Understand basic concepts", "Complete practice exercises"],
            },
            {
                "id": "topic_2", 
                "title": "Core Concepts and Applications",
                "description": "Main principles and real-world applications",
                "estimated_hours": 6,
                "activities": self._get_style_activities(learning_style, "applications"),
                "milestones": ["Apply concepts to examples", "Complete project"],
            },
            {
                "id": "topic_3",
                "title": "Advanced Topics and Practice",
                "description": "Complex scenarios and advanced techniques",
                "estimated_hours": 8,
                "activities": self._get_style_activities(learning_style, "advanced"),
                "milestones": ["Master advanced concepts", "Complete final project"],
            },
        ]
        
        summary = f"Personalized study plan for {goals} using {self._get_style_name(learning_style).lower()} learning approach. Estimated total time: {sum(topic['estimated_hours'] for topic in topics)} hours."
        
        return {
            "summary": summary,
            "topics": topics,
            "learning_style": learning_style,
            "total_hours": sum(topic["estimated_hours"] for topic in topics),
        }

    def _get_style_activities(self, learning_style: str, topic_type: str) -> list[str]:
        """Get learning activities based on style and topic type."""
        activities = {
            "V": {
                "fundamentals": ["Create concept maps", "Watch video explanations", "Use visual diagrams"],
                "applications": ["Design flowcharts", "Create infographics", "Use visual examples"],
                "advanced": ["Build visual models", "Create comprehensive diagrams", "Design presentations"],
            },
            "A": {
                "fundamentals": ["Listen to explanations", "Participate in discussions", "Use audio recordings"],
                "applications": ["Explain concepts aloud", "Join study groups", "Use verbal practice"],
                "advanced": ["Teach others", "Participate in debates", "Use audio summaries"],
            },
            "R": {
                "fundamentals": ["Read detailed materials", "Take comprehensive notes", "Write summaries"],
                "applications": ["Write detailed explanations", "Create documentation", "Use written exercises"],
                "advanced": ["Write research papers", "Create detailed guides", "Use written analysis"],
            },
            "K": {
                "fundamentals": ["Hands-on practice", "Use real examples", "Interactive exercises"],
                "applications": ["Build projects", "Use practical examples", "Interactive simulations"],
                "advanced": ["Complete complex projects", "Use real-world scenarios", "Interactive challenges"],
            },
        }
        
        return activities.get(learning_style, activities["V"]).get(topic_type, [])

    def _get_style_adaptation(self, learning_style: str) -> str:
        """Get learning style adaptation message."""
        adaptations = {
            "V": "I'll create a plan with lots of visual elements, diagrams, and charts to help you learn effectively.",
            "A": "I'll design a plan that emphasizes discussions, audio content, and verbal explanations.",
            "R": "I'll structure a plan with detailed reading materials, note-taking, and written exercises.",
            "K": "I'll create a hands-on plan with practical exercises, real examples, and interactive activities.",
        }
        return adaptations.get(learning_style, adaptations["V"])

    def _get_style_name(self, learning_style: str) -> str:
        """Get full name of learning style."""
        names = {
            "V": "Visual",
            "A": "Auditory",
            "R": "Reading/Writing", 
            "K": "Kinesthetic",
        }
        return names.get(learning_style, "Visual")

    def _format_plan_overview(self, topics: list[dict]) -> str:
        """Format plan overview for display."""
        overview = ""
        for i, topic in enumerate(topics, 1):
            overview += f"{i}. **{topic['title']}** ({topic['estimated_hours']} hours)\n"
            overview += f"   {topic['description']}\n"
        return overview
