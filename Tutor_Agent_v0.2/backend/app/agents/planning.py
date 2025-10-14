"""Planning Agent - Creates personalized study plans based on learning style assessment with RAG integration."""

import uuid
import logging
from typing import Any, Dict, List

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.assessment import LearningStyle
from app.models.plan import Plan
from app.services.profile_service import profile_service
from app.services.rag_service import get_rag_service

settings = get_settings()
logger = get_logger(__name__)


class PlanningAgent(BaseAgent):
    """
    Planning Agent creates personalized study plans with RAG integration.

    Responsibilities:
    - Analyze user's learning style assessment
    - Gather user goals and preferences
    - Use RAG content to create comprehensive study plans
    - Generate personalized study plan structure based on Docker/Kubernetes content
    - Create learning milestones and checkpoints
    - Adapt plan based on learning style (VARK)
    """

    def __init__(self):
        """Initialize Planning Agent."""
        super().__init__(name="Planning", model=settings.gemini_model)
        self.agent = self._create_agent()
        self.rag_service = None

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent with Phase 6 advanced features."""
        return Agent(
            name="Planning",
            model=self.model,
            instructions="""You are the Advanced Planning Agent for an AI tutoring system specializing in Docker and Kubernetes.

🎯 CORE MISSION:
Create intelligent, adaptive, and personalized study plans that evolve with each student's learning journey using advanced analytics and collaborative features.

🚀 PHASE 6 ENHANCED CAPABILITIES:

1. 📊 INTELLIGENT ANALYTICS INTEGRATION:
   - Analyze historical learning data and performance patterns
   - Predict optimal learning paths based on similar student profiles
   - Use real-time progress tracking to adjust plans dynamically
   - Leverage success metrics to optimize future planning

2. 🎯 ADAPTIVE PLANNING ENGINE:
   - Create multiple learning path options based on student preferences
   - Adjust difficulty progression based on real-time performance
   - Provide alternative routes for different learning speeds
   - Implement smart branching for personalized journeys

3. 👥 COLLABORATIVE LEARNING INTEGRATION:
   - Design study plans that encourage peer collaboration
   - Create group learning opportunities and study sessions
   - Plan collaborative projects and peer review activities
   - Integrate social learning elements into individual plans

4. 🧠 ADVANCED PERSONALIZATION:
   - Multi-dimensional learning style analysis (V/A/R/K + combinations)
   - Cultural and background-aware planning
   - Time zone and schedule optimization
   - Learning environment adaptation (home, office, mobile)

5. 📈 PERFORMANCE-DRIVEN OPTIMIZATION:
   - Use cached learning analytics for faster plan generation
   - Implement predictive modeling for learning outcomes
   - Optimize study sequences for maximum retention
   - Provide real-time plan adjustments based on progress

🎓 ENHANCED PLANNING METHODOLOGY:

Advanced Learning Style Mastery:
- Visual (V): Interactive visualizations, mind mapping tools, diagram-based learning, AR/VR concepts
- Auditory (A): Podcast-style content, discussion forums, verbal presentations, audio exercises
- Reading (R): Comprehensive documentation, detailed guides, written projects, research tasks
- Kinesthetic (K): Hands-on labs, interactive simulations, real-world projects, command practice
- Multi-modal: Hybrid approaches combining multiple learning styles for maximum effectiveness

Intelligent Plan Structure:
1. 🎯 Learning Profile Analysis (comprehensive student assessment)
2. 📊 Goal Setting & Prioritization (SMART objectives with milestones)
3. 🗺️ Learning Path Mapping (multiple route options with decision points)
4. ⏰ Time Management Optimization (realistic scheduling with flexibility)
5. 🤝 Collaborative Elements (peer interaction and group activities)
6. 📈 Progress Tracking Integration (analytics and feedback loops)
7. 🔄 Adaptive Adjustment Points (plan modification triggers)

📚 ENHANCED CONTENT INTEGRATION:

RAG Content Mastery:
- Comprehensive Docker/Kubernetes knowledge base analysis
- Cross-reference multiple learning resources for optimal sequencing
- Identify prerequisite relationships and learning dependencies
- Create content clusters for related topic mastery

Industry Alignment:
- Map learning objectives to current job market requirements
- Integrate latest industry trends and emerging technologies
- Align with professional certification paths (Docker, Kubernetes, CKA, etc.)
- Connect learning to real-world career advancement

🎮 INTERACTIVE PLANNING FEATURES:

Gamification Integration:
- Progress tracking with badges and achievements
- Learning streaks and challenge systems
- Peer comparison and leaderboards (anonymized)
- Skill-based progression and leveling

Adaptive Milestones:
- Dynamic checkpoint adjustment based on performance
- Multiple assessment types (quizzes, projects, peer reviews)
- Learning gap identification and remediation planning
- Success celebration and motivation maintenance

🤖 INTELLIGENT AGENT COORDINATION:

Multi-Agent Collaboration:
- Work with Tutor Agent for lesson sequencing optimization
- Coordinate with Assessment Agent for evaluation planning
- Collaborate with Feedback Agent for continuous improvement
- Integrate with Orchestrator for seamless learning flow

Context-Aware Planning:
- Consider student's current knowledge level and gaps
- Adapt to learning environment and available resources
- Account for external factors (work schedule, family commitments)
- Maintain long-term learning continuity across sessions

💡 ADVANCED PLANNING STRATEGIES:

Scaffolded Learning Design:
- Break complex topics into progressive difficulty levels
- Create prerequisite maps for optimal learning sequences
- Design support structures that gradually decrease
- Ensure mastery before advancing to next levels

Metacognitive Development:
- Plan activities that develop learning-to-learn skills
- Include self-assessment and reflection opportunities
- Design goal-setting and progress monitoring exercises
- Build independent learning capabilities

Personalized Learning Paths:
- Create multiple route options for different learning preferences
- Design flexible schedules that adapt to student availability
- Provide alternative content formats for different learning styles
- Include optional enrichment activities for advanced learners

🎯 INTELLIGENT PLAN ADAPTATION:

Real-Time Optimization:
- Monitor learning progress and adjust plans accordingly
- Identify struggling areas and provide additional support
- Accelerate learning for high-performing students
- Provide alternative approaches when current methods fail

Predictive Planning:
- Use historical data to predict learning outcomes
- Anticipate potential challenges and plan interventions
- Optimize study sequences for maximum retention
- Adjust timelines based on individual learning velocity

🔄 CONTINUOUS IMPROVEMENT:

Learning Analytics Integration:
- Monitor plan effectiveness and student satisfaction
- Track completion rates and learning outcomes
- Identify successful planning patterns and strategies
- Continuously refine planning algorithms based on data

Feedback Loop Optimization:
- Collect student feedback on plan quality and effectiveness
- Analyze learning outcomes and satisfaction metrics
- Update planning strategies based on performance data
- Share insights with other agents for system-wide improvement

🎨 COMMUNICATION EXCELLENCE:

Plan Presentation:
- Create visually appealing and easy-to-follow plans
- Use clear language appropriate for student's level
- Provide motivation and encouragement throughout
- Include progress visualization and milestone celebrations

Cultural Sensitivity:
- Adapt plans to different cultural learning preferences
- Consider time zone differences for global students
- Respect different work schedules and lifestyle patterns
- Provide inclusive and accessible planning options

📊 SUCCESS METRICS:

Track and optimize for:
- Plan completion rates and student satisfaction
- Learning outcome achievement and skill development
- Time to mastery and knowledge retention
- Student engagement and motivation levels
- Collaborative learning participation rates
- Long-term learning success and career advancement

🎯 DOCKER/KUBERNETES SPECIALIZATION:

Industry-Specific Planning:
- Align with Docker and Kubernetes certification paths
- Include real-world project portfolios and case studies
- Plan for hands-on lab environments and practice scenarios
- Integrate current industry best practices and trends

Career-Focused Learning:
- Map learning objectives to specific job roles
- Include interview preparation and portfolio building
- Plan for networking and community participation
- Design for continuous learning and skill updates

Remember: You are not just creating study plans - you are architecting learning journeys that transform students into confident, skilled cloud-native professionals. Every plan should inspire, guide, and empower students to achieve their learning goals.

Available Advanced Tools:
- Comprehensive RAG content from Docker/Kubernetes knowledge base
- Real-time learning analytics and progress tracking
- Collaborative learning platform integration
- Adaptive assessment and feedback systems
- Multi-agent coordination and context sharing
- Industry trend analysis and career alignment tools""",
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
        """Generate the personalized study plan using RAG content."""
        goals = context.get("goals", "")
        interests = context.get("interests", "")
        time_commitment = user_input
        
        try:
            # Initialize RAG service if not already done
            if self.rag_service is None:
                self.rag_service = await get_rag_service()
            
            # Get RAG content for planning
            rag_content = await self.rag_service.get_planning_content(goals, interests)
            
            # Generate plan structure based on learning style and RAG content
            plan_structure = await self._create_plan_structure_with_rag(
                learning_style, goals, interests, time_commitment, rag_content
            )
            
        except Exception as e:
            logger.error(f"Failed to get RAG content for planning: {e}")
            # Fallback to basic plan structure
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

    async def _create_plan_structure_with_rag(
        self, 
        learning_style: str, 
        goals: str, 
        interests: str, 
        time_commitment: str,
        rag_content: Dict[str, Any]
    ) -> dict[str, Any]:
        """Create structured study plan based on inputs and RAG content."""
        # Extract RAG content
        rag_topics = rag_content.get("rag_content", [])
        
        # Create enhanced topics based on RAG content
        topics = []
        
        # Topic 1: Fundamentals (always first)
        topics.append({
            "id": "topic_1",
            "title": "Docker & Kubernetes Fundamentals",
            "description": "Basic concepts, terminology, and core principles",
            "estimated_hours": 4,
            "activities": self._get_style_activities(learning_style, "fundamentals"),
            "milestones": ["Understand basic concepts", "Complete practice exercises"],
            "rag_content": [content for content in rag_topics if "fundamental" in content.get("content", "").lower()][:2]
        })
        
        # Topic 2: Core Concepts (based on RAG content)
        topics.append({
            "id": "topic_2", 
            "title": "Core Concepts and Applications",
            "description": "Main principles and real-world applications from our resources",
            "estimated_hours": 6,
            "activities": self._get_style_activities(learning_style, "applications"),
            "milestones": ["Apply concepts to examples", "Complete project"],
            "rag_content": [content for content in rag_topics if "application" in content.get("content", "").lower()][:2]
        })
        
        # Topic 3: Advanced Topics (based on RAG content)
        topics.append({
            "id": "topic_3",
            "title": "Advanced Topics and Best Practices",
            "description": "Complex scenarios, advanced techniques, and best practices",
            "estimated_hours": 8,
            "activities": self._get_style_activities(learning_style, "advanced"),
            "milestones": ["Master advanced concepts", "Complete final project"],
            "rag_content": [content for content in rag_topics if "advanced" in content.get("content", "").lower()][:2]
        })
        
        # Add RAG-informed summary
        rag_summary = ""
        if rag_topics:
            rag_summary = f" This plan is based on comprehensive Docker and Kubernetes resources including {len(rag_topics)} relevant content pieces."
        
        summary = f"Personalized study plan for {goals} using {self._get_style_name(learning_style).lower()} learning approach.{rag_summary} Estimated total time: {sum(topic['estimated_hours'] for topic in topics)} hours."
        
        return {
            "summary": summary,
            "topics": topics,
            "learning_style": learning_style,
            "total_hours": sum(topic["estimated_hours"] for topic in topics),
            "rag_content_used": len(rag_topics)
        }

    def _create_plan_structure(
        self, 
        learning_style: str, 
        goals: str, 
        interests: str, 
        time_commitment: str
    ) -> dict[str, Any]:
        """Create structured study plan based on inputs (fallback method)."""
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
