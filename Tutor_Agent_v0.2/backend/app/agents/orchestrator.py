"""Orchestrator Agent - Manages agent flow and handoffs with topic skipping logic."""

import logging
from typing import Any, Dict

from agents import Agent, Handoff

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.models import SessionState

logger = logging.getLogger(__name__)
settings = get_settings()


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent manages the overall tutoring flow with topic skipping logic.

    Responsibilities:
    - Route user to appropriate agent based on session state
    - Handle handoffs between agents
    - Manage session state transitions
    - Send initial greeting (FIRST RUNNER)
    - Handle topic skipping requests and quiz assessments
    - Coordinate between Tutor and Quiz agents for topic skipping
    """

    def __init__(self):
        """Initialize Orchestrator Agent."""
        super().__init__(name="Orchestrator", model=settings.gemini_model)
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent with Phase 6 advanced features."""
        return Agent(
            name="Orchestrator",
            model=self.model,
            instructions="""You are the Advanced Orchestrator for an AI tutoring system specializing in Docker and Kubernetes.

🎯 CORE MISSION:
Intelligently coordinate and manage the entire learning ecosystem, ensuring seamless agent collaboration, optimal learning flow, and exceptional student experiences using advanced analytics and multi-user capabilities.

🚀 PHASE 6 ENHANCED CAPABILITIES:

1. 📊 INTELLIGENT ORCHESTRATION ANALYTICS:
   - Analyze learning flow patterns across student populations
   - Use predictive modeling to optimize agent handoffs
   - Track orchestration effectiveness and student satisfaction
   - Leverage historical data for improved routing decisions

2. 🎯 ADAPTIVE FLOW MANAGEMENT:
   - Dynamically adjust learning paths based on student performance
   - Provide multiple learning route options for different preferences
   - Use intelligent branching for personalized learning journeys
   - Implement smart session management for optimal outcomes

3. 👥 MULTI-USER COORDINATION:
   - Manage multiple concurrent student sessions efficiently
   - Coordinate collaborative learning opportunities between students
   - Facilitate study group formation and peer interactions
   - Integrate social learning elements into individual journeys

4. 🧠 ADVANCED CONTEXT MANAGEMENT:
   - Multi-dimensional session state tracking (learning, emotional, social)
   - Cultural and background-aware orchestration decisions
   - Context-sensitive routing based on learning environment
   - Emotional intelligence in agent handoff management

5. 📈 PERFORMANCE-DRIVEN OPTIMIZATION:
   - Use cached session data for faster routing decisions
   - Implement real-time learning flow optimization
   - Optimize agent handoff sequences for maximum effectiveness
   - Provide immediate feedback and flow adjustments

🎓 ENHANCED ORCHESTRATION METHODOLOGY:

Advanced Session State Management:
- GREETING: Personalized welcome with learning journey preview
- ASSESSING: Intelligent learning style and skill evaluation
- PLANNING: Adaptive study plan creation with multiple options
- TUTORING: Personalized lesson delivery with real-time adaptation
- QUIZZING: Comprehensive knowledge assessment with immediate feedback
- COLLABORATING: Peer learning and study group coordination
- REMEDIATING: Targeted skill development and gap filling
- ADVANCING: Accelerated learning for high-performing students
- COMPLETING: Achievement celebration and next steps planning

Intelligent Flow Structure:
1. 🎯 Learning Profile Analysis (comprehensive student assessment)
2. 📊 Goal Setting & Prioritization (SMART objectives with milestones)
3. 🗺️ Learning Path Mapping (multiple route options with decision points)
4. ⏰ Session Management (optimal timing and duration)
5. 🤝 Collaborative Coordination (peer interaction and group activities)
6. 📈 Progress Tracking (analytics and feedback loops)
7. 🔄 Adaptive Adjustment Points (flow modification triggers)

📚 ENHANCED AGENT COORDINATION:

Multi-Agent Collaboration:
- Seamless handoffs between all specialist agents
- Context preservation across agent transitions
- Coordinated learning objective alignment
- Integrated feedback and improvement loops

Intelligent Routing:
- Consider student's current knowledge level and experience
- Adapt to learning environment and available resources
- Account for external factors (work schedule, preferences)
- Maintain learning continuity across sessions

💡 ADVANCED ORCHESTRATION STRATEGIES:

Predictive Flow Management:
- Anticipate student needs and preferences
- Proactively suggest learning path adjustments
- Identify potential learning challenges and interventions
- Optimize learning sequences for maximum retention

Context-Aware Decision Making:
- Monitor student engagement and emotional state
- Adjust learning pace based on performance indicators
- Provide alternative approaches when current methods fail
- Maintain motivation and learning momentum

🎯 INTELLIGENT TOPIC SKIPPING MANAGEMENT:

Smart Skipping Logic:
- Analyze student's current knowledge level and learning objectives
- Assess topic importance for overall learning goals
- Consider prerequisite dependencies and learning sequences
- Provide alternative learning paths and acceleration options

Assessment Integration:
- Coordinate comprehensive quizzes for skipped topics
- Use adaptive questioning to gauge true understanding
- Provide detailed remediation if knowledge gaps exist
- Track skipping patterns for curriculum improvement

🔄 CONTINUOUS IMPROVEMENT:

Orchestration Analytics Integration:
- Monitor learning flow effectiveness and student satisfaction
- Track agent handoff success rates and optimization opportunities
- Identify successful orchestration patterns and strategies
- Continuously refine routing algorithms based on data

Feedback Loop Optimization:
- Collect student feedback on learning flow quality and effectiveness
- Analyze learning outcomes and satisfaction metrics
- Update orchestration strategies based on performance data
- Share insights with all agents for system-wide improvement

🎨 COMMUNICATION EXCELLENCE:

Orchestration Presentation:
- Create engaging and motivating learning journey introductions
- Use clear language appropriate for student's level
- Provide encouragement and support throughout transitions
- Include progress visualization and milestone celebrations

Cultural Sensitivity:
- Adapt orchestration to different cultural learning preferences
- Consider time zone differences for global students
- Respect different communication styles and preferences
- Provide inclusive and accessible learning flow options

📊 SUCCESS METRICS:

Track and optimize for:
- Learning flow completion rates and student satisfaction
- Agent handoff success and context preservation
- Time to learning objective achievement
- Student engagement and motivation levels
- Collaborative learning participation rates
- Long-term learning success and career advancement

🎯 DOCKER/KUBERNETES SPECIALIZATION:

Industry-Specific Orchestration:
- Align learning flow with Docker and Kubernetes certification paths
- Coordinate real-world project integration and portfolio building
- Facilitate hands-on lab environments and practice scenarios
- Integrate current industry best practices and trends

Career-Focused Learning Flow:
- Map learning objectives to specific job roles and requirements
- Coordinate interview preparation and skill development
- Facilitate networking and community participation opportunities
- Design for continuous learning and professional growth

🤖 INTELLIGENT AGENT COORDINATION:

Advanced Handoff Management:
- Preserve context and learning state across agent transitions
- Coordinate learning objective alignment between agents
- Facilitate seamless information sharing and collaboration
- Optimize handoff timing for maximum learning effectiveness

Multi-Agent Collaboration:
- Work with all specialist agents for optimal learning outcomes
- Coordinate feedback and improvement across the entire system
- Facilitate cross-agent learning and knowledge sharing
- Integrate insights from all agents for comprehensive student support

🎮 INTERACTIVE ORCHESTRATION FEATURES:

Gamification Integration:
- Progress tracking with learning journey milestones
- Achievement badges for learning flow completion
- Learning streaks and challenge systems
- Peer comparison and leaderboards (anonymized)

Adaptive Flow Management:
- Real-time learning path adjustment based on performance
- Multiple learning route options for different preferences
- Dynamic difficulty progression and challenge levels
- Personalized learning pace and intensity management

Remember: You are not just managing agent handoffs - you are orchestrating transformative learning journeys that guide students toward mastery and career success. Every orchestration decision should inspire confidence, provide clear direction, and create optimal learning experiences.

Available Advanced Tools:
- Comprehensive multi-agent coordination and context sharing
- Real-time learning analytics and progress tracking
- Collaborative learning platform integration
- Adaptive assessment and feedback systems
- Multi-user session management and coordination
- Industry trend analysis and career alignment tools""",
        )

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute orchestrator logic.

        Args:
            user_input: User input (or "hello" for FIRST RUNNER)
            context: Session context including state

        Returns:
            Response dictionary with message and next actions
        """
        session_state = context.get("state", SessionState.GREETING)

        # FIRST RUNNER: Initial greeting
        if user_input == "hello" and session_state == SessionState.GREETING:
            return {
                "agent": self.name,
                "message": (
                    "Hello! 👋 I'm your AI Tutor. I'm here to help you learn "
                    "in a way that works best for you.\n\n"
                    "First, I'll ask you a few quick questions to understand your "
                    "learning style. Then we'll create a personalized study plan "
                    "and start learning!\n\n"
                    "Ready to begin your learning journey?"
                ),
                "action": "await_confirmation",
                "next_state": SessionState.ASSESSING,
            }

        # Route based on state
        if session_state == SessionState.ASSESSING:
            return {
                "agent": self.name,
                "message": "Great! Let's start with a quick assessment to understand how you learn best.",
                "action": "handoff_to_assessment",
                "next_state": SessionState.ASSESSING,
            }
        
        if session_state == SessionState.PLANNING:
            return {
                "agent": self.name,
                "message": "Perfect! Now let's create your personalized study plan.",
                "action": "handoff_to_planning",
                "next_state": SessionState.PLANNING,
            }
        
        # Handle user confirmation to start assessment
        if (session_state == SessionState.GREETING and 
            user_input.lower() in ["yes", "ready", "start", "begin", "ok", "okay", "sure"]):
            return {
                "agent": self.name,
                "message": "Perfect! Let's begin your learning style assessment.",
                "action": "start_assessment",
                "next_state": SessionState.ASSESSING,
            }

        if session_state == SessionState.TUTORING:
            return {
                "agent": self.name,
                "message": "Let's dive into your lesson!",
                "action": "handoff_to_tutor",
                "next_state": SessionState.TUTORING,
            }

        if session_state == SessionState.QUIZZING:
            return {
                "agent": self.name,
                "message": "Time to test your knowledge!",
                "action": "handoff_to_quiz",
                "next_state": SessionState.QUIZZING,
            }

        # Handle topic skipping logic
        if session_state == SessionState.TUTORING and "skip" in user_input.lower() and "topic" in user_input.lower():
            return await self._handle_topic_skip_request(user_input, context)

        # Handle quiz results from topic skipping assessment
        if context.get("quiz_result") == "passed":
            return await self._handle_quiz_passed(context)
        elif context.get("quiz_result") == "failed":
            return await self._handle_quiz_failed(context)

        # Handle topic skip assessment state
        if session_state == SessionState.TOPIC_SKIP_ASSESSMENT:
            return {
                "agent": self.name,
                "message": "Let's assess your knowledge of this topic to see if you can skip it.",
                "action": "handoff_to_quiz",
                "next_state": SessionState.TOPIC_SKIP_ASSESSMENT,
                "quiz_type": "topic_skip_assessment",
                "topic": context.get("topic", "current topic")
            }

        # Default response for other states
        return {
            "agent": self.name,
            "message": f"I'll help you continue from where we left off. Current state: {session_state}",
            "action": "continue",
        }

    async def _handle_topic_skip_request(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle student request to skip a topic."""
        topic = context.get("topic", "current topic")
        
        # Check if student is insisting after initial guidance
        if context.get("skip_request") and context.get("next_state") == "waiting_for_confirmation":
            # Student is insisting, generate quiz for assessment
            return {
                "agent": self.name,
                "message": f"I understand you want to skip {topic}. Let me generate a quiz to assess your knowledge of this topic. If you pass, we can move on to the next topic.",
                "action": "generate_skip_quiz",
                "next_state": SessionState.TOPIC_SKIP_ASSESSMENT,
                "topic": topic,
                "quiz_type": "topic_skip_assessment"
            }
        else:
            # First request, let Tutor Agent provide guidance
            return {
                "agent": self.name,
                "message": f"I see you want to skip {topic}. Let me have our Tutor Agent provide some guidance on why this topic is important for your learning journey.",
                "action": "handoff_to_tutor",
                "next_state": SessionState.TUTORING,
                "topic": topic,
                "skip_request": True
            }

    async def _handle_quiz_passed(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle passed quiz result from topic skipping assessment."""
        topic = context.get("topic", "the topic")
        score = context.get("score_percentage", 0)
        
        return {
            "agent": self.name,
            "message": f"🎉 Excellent! You scored {score:.1f}% on the {topic} quiz. You clearly understand this topic well and can skip it. Let's move on to the next topic in your learning path!",
            "action": "topic_skipped",
            "next_state": SessionState.TUTORING,
            "topic_skipped": True,
            "next_topic": True
        }

    async def _handle_quiz_failed(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed quiz result from topic skipping assessment."""
        topic = context.get("topic", "the topic")
        score = context.get("score_percentage", 0)
        
        return {
            "agent": self.name,
            "message": f"I see you scored {score:.1f}% on the {topic} quiz. This topic is important for your understanding, so let's learn it properly together. Our Tutor Agent will help you master this topic step by step.",
            "action": "remediation_required",
            "next_state": SessionState.TUTORING,
            "topic": topic,
            "remediation": True,
            "quiz_result": "failed"
        }

    def get_handoffs(self) -> list[Handoff]:
        """
        Get available handoff targets.

        Returns:
            List of Handoff objects for agent transitions
        """
        return [
            Handoff(
                target="Assessment",
                description="Hand off to Assessment Agent for learning style evaluation",
            ),
            Handoff(
                target="Planning",
                description="Hand off to Planning Agent for study plan creation",
            ),
            Handoff(
                target="Tutor",
                description="Hand off to Tutor Agent for lesson delivery",
            ),
            Handoff(
                target="Quiz",
                description="Hand off to Quiz Agent for knowledge testing",
            ),
            Handoff(
                target="Feedback",
                description="Hand off to Feedback Agent for performance review",
            ),
        ]

