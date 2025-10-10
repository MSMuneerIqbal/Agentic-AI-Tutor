"""
Feedback Agent - Acts as Principal to monitor, collect feedback, and adapt agent behaviors.
"""

import logging
from typing import Any, Dict, List, Optional

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
settings = get_settings()


class FeedbackAgent(BaseAgent):
    """
    Feedback Agent acts as Principal to monitor and improve the tutoring system.

    Responsibilities:
    - Monitor other agents' performance and student interactions
    - Collect student difficulties and feedback
    - Provide instructions for agent improvement
    - Adapt agent behaviors based on student needs
    - Analyze learning patterns and suggest optimizations
    - Coordinate system-wide improvements
    """

    def __init__(self):
        """Initialize Feedback Agent."""
        super().__init__(name="Feedback", model=settings.gemini_model)
        self.agent = self._create_agent()
        self.rag_service = None
        self.student_feedback = []
        self.agent_performance = {}
        self.learning_patterns = {}
        self.improvement_suggestions = []

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent."""
        return Agent(
            name="Feedback",
            model=self.model,
            instructions="""You are the Feedback Agent, acting as the Principal of the AI tutoring system.

Your role is to monitor, analyze, and improve the entire tutoring system.

Principal Responsibilities:
1. Monitor all agents' performance and student interactions
2. Collect and analyze student difficulties and feedback
3. Provide instructions for agent behavior improvements
4. Adapt system behavior based on student needs
5. Analyze learning patterns and suggest optimizations
6. Coordinate system-wide improvements

Monitoring Areas:
- Tutor Agent: Lesson effectiveness, student engagement, learning style adaptation
- Assessment Agent: Question quality, assessment accuracy, learning style detection
- Planning Agent: Plan quality, goal alignment, time estimation accuracy
- Quiz Agent: Question difficulty, assessment fairness, feedback quality
- Orchestrator Agent: Flow management, handoff efficiency, state transitions

Feedback Collection:
- Student difficulties with specific topics
- Learning style mismatches
- Pace and difficulty issues
- Engagement and motivation problems
- Technical or interface issues

Improvement Actions:
- Adjust agent prompts and instructions
- Modify learning paths and content delivery
- Optimize assessment questions and methods
- Enhance topic skipping logic
- Improve handoff coordination
- Personalize learning experiences

Analysis and Reporting:
- Learning pattern analysis
- Performance metrics tracking
- Student satisfaction monitoring
- System optimization recommendations
- Continuous improvement suggestions

Always be proactive in identifying issues and providing constructive feedback for system improvement.""",
        )

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute feedback and monitoring logic.

        Args:
            user_input: Student feedback or monitoring request
            context: System context including agent performance, student data, etc.

        Returns:
            Response dictionary with feedback analysis and improvement suggestions
        """
        feedback_type = context.get("feedback_type", "general")
        agent_name = context.get("agent_name", "system")
        student_id = context.get("student_id")
        session_id = context.get("session_id")

        try:
            # Initialize RAG service if not already done
            if self.rag_service is None:
                self.rag_service = await get_rag_service()

            # Handle different types of feedback
            if feedback_type == "student_difficulty":
                return await self._handle_student_difficulty(user_input, context)
            elif feedback_type == "agent_performance":
                return await self._handle_agent_performance(user_input, context)
            elif feedback_type == "learning_pattern":
                return await self._handle_learning_pattern(user_input, context)
            elif feedback_type == "system_optimization":
                return await self._handle_system_optimization(user_input, context)
            else:
                return await self._handle_general_feedback(user_input, context)

        except Exception as e:
            logger.error(f"Feedback Agent execution failed: {e}")
            return {
                "agent": self.name,
                "message": f"I encountered an issue while processing feedback. Let me analyze this and provide recommendations.",
                "action": "error_recovery",
                "error": str(e)
            }

    async def _handle_student_difficulty(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle student difficulty feedback."""
        topic = context.get("topic", "current topic")
        difficulty_type = context.get("difficulty_type", "general")
        learning_style = context.get("learning_style", "unknown")
        
        # Store student difficulty
        self.student_feedback.append({
            "type": "difficulty",
            "topic": topic,
            "difficulty_type": difficulty_type,
            "learning_style": learning_style,
            "feedback": user_input,
            "timestamp": context.get("timestamp")
        })

        # Analyze difficulty and provide recommendations
        analysis = await self._analyze_student_difficulty(topic, difficulty_type, learning_style, user_input)
        
        return {
            "agent": self.name,
            "message": f"I've noted your difficulty with {topic}. Let me provide some recommendations to help improve your learning experience.",
            "action": "difficulty_analysis",
            "topic": topic,
            "difficulty_type": difficulty_type,
            "analysis": analysis,
            "recommendations": analysis.get("recommendations", []),
            "agent_instructions": analysis.get("agent_instructions", {})
        }

    async def _handle_agent_performance(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent performance monitoring."""
        agent_name = context.get("agent_name", "unknown")
        performance_metrics = context.get("performance_metrics", {})
        student_satisfaction = context.get("student_satisfaction", 0)
        
        # Store agent performance data
        self.agent_performance[agent_name] = {
            "metrics": performance_metrics,
            "satisfaction": student_satisfaction,
            "timestamp": context.get("timestamp")
        }

        # Analyze performance and provide improvement suggestions
        analysis = await self._analyze_agent_performance(agent_name, performance_metrics, student_satisfaction)
        
        return {
            "agent": self.name,
            "message": f"I've analyzed {agent_name} agent's performance. Here are my findings and recommendations for improvement.",
            "action": "performance_analysis",
            "agent_name": agent_name,
            "analysis": analysis,
            "improvements": analysis.get("improvements", []),
            "instructions": analysis.get("instructions", {})
        }

    async def _handle_learning_pattern(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle learning pattern analysis."""
        student_id = context.get("student_id")
        learning_data = context.get("learning_data", {})
        progress_data = context.get("progress_data", {})
        
        # Store learning pattern data
        self.learning_patterns[student_id] = {
            "learning_data": learning_data,
            "progress_data": progress_data,
            "timestamp": context.get("timestamp")
        }

        # Analyze learning patterns
        analysis = await self._analyze_learning_patterns(student_id, learning_data, progress_data)
        
        return {
            "agent": self.name,
            "message": f"I've analyzed your learning patterns. Here are my insights and suggestions for optimizing your learning experience.",
            "action": "pattern_analysis",
            "student_id": student_id,
            "analysis": analysis,
            "optimizations": analysis.get("optimizations", []),
            "personalization": analysis.get("personalization", {})
        }

    async def _handle_system_optimization(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system-wide optimization analysis."""
        system_metrics = context.get("system_metrics", {})
        user_feedback = context.get("user_feedback", [])
        
        # Analyze system performance
        analysis = await self._analyze_system_performance(system_metrics, user_feedback)
        
        return {
            "agent": self.name,
            "message": "I've conducted a comprehensive system analysis. Here are my recommendations for system-wide improvements.",
            "action": "system_optimization",
            "analysis": analysis,
            "optimizations": analysis.get("optimizations", []),
            "priority_actions": analysis.get("priority_actions", [])
        }

    async def _handle_general_feedback(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general feedback and monitoring requests."""
        return {
            "agent": self.name,
            "message": "I'm here to monitor and improve the tutoring system. I can help with student difficulties, agent performance analysis, learning pattern optimization, and system-wide improvements. What would you like me to analyze?",
            "action": "feedback_menu",
            "available_analyses": [
                "student_difficulty",
                "agent_performance", 
                "learning_pattern",
                "system_optimization"
            ]
        }

    async def _analyze_student_difficulty(self, topic: str, difficulty_type: str, learning_style: str, feedback: str) -> Dict[str, Any]:
        """Analyze student difficulty and provide recommendations."""
        try:
            # Get RAG content for the topic to understand context
            rag_content = await self.rag_service.get_assessment_content(topic)
            
            # Analyze difficulty patterns
            difficulty_analysis = {
                "topic": topic,
                "difficulty_type": difficulty_type,
                "learning_style": learning_style,
                "common_issues": self._identify_common_issues(topic, difficulty_type),
                "recommendations": self._generate_difficulty_recommendations(topic, difficulty_type, learning_style),
                "agent_instructions": self._generate_agent_instructions(topic, difficulty_type, learning_style)
            }
            
            return difficulty_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze student difficulty: {e}")
            return {
                "topic": topic,
                "difficulty_type": difficulty_type,
                "learning_style": learning_style,
                "common_issues": ["General learning difficulty"],
                "recommendations": ["Review the topic with additional examples"],
                "agent_instructions": {"tutor": "Provide more examples and practice"}
            }

    async def _analyze_agent_performance(self, agent_name: str, metrics: Dict[str, Any], satisfaction: float) -> Dict[str, Any]:
        """Analyze agent performance and provide improvement suggestions."""
        performance_analysis = {
            "agent_name": agent_name,
            "satisfaction_score": satisfaction,
            "performance_issues": self._identify_performance_issues(agent_name, metrics, satisfaction),
            "improvements": self._generate_performance_improvements(agent_name, metrics, satisfaction),
            "instructions": self._generate_agent_improvement_instructions(agent_name, metrics, satisfaction)
        }
        
        return performance_analysis

    async def _analyze_learning_patterns(self, student_id: str, learning_data: Dict[str, Any], progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learning patterns and provide optimization suggestions."""
        pattern_analysis = {
            "student_id": student_id,
            "learning_style_effectiveness": self._analyze_learning_style_effectiveness(learning_data),
            "pace_analysis": self._analyze_learning_pace(progress_data),
            "engagement_patterns": self._analyze_engagement_patterns(learning_data),
            "optimizations": self._generate_learning_optimizations(learning_data, progress_data),
            "personalization": self._generate_personalization_suggestions(learning_data, progress_data)
        }
        
        return pattern_analysis

    async def _analyze_system_performance(self, system_metrics: Dict[str, Any], user_feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze system-wide performance and provide optimization recommendations."""
        system_analysis = {
            "overall_performance": self._calculate_overall_performance(system_metrics),
            "bottlenecks": self._identify_system_bottlenecks(system_metrics),
            "user_satisfaction": self._analyze_user_satisfaction(user_feedback),
            "optimizations": self._generate_system_optimizations(system_metrics, user_feedback),
            "priority_actions": self._prioritize_system_actions(system_metrics, user_feedback)
        }
        
        return system_analysis

    def _identify_common_issues(self, topic: str, difficulty_type: str) -> List[str]:
        """Identify common issues for a topic and difficulty type."""
        common_issues = {
            "conceptual": ["Abstract concepts", "Theory vs practice", "Complex relationships"],
            "practical": ["Command syntax", "Configuration", "Troubleshooting"],
            "pacing": ["Too fast", "Too slow", "Inconsistent pace"],
            "engagement": ["Boring content", "Irrelevant examples", "Poor explanations"]
        }
        return common_issues.get(difficulty_type, ["General learning difficulty"])

    def _generate_difficulty_recommendations(self, topic: str, difficulty_type: str, learning_style: str) -> List[str]:
        """Generate recommendations for addressing student difficulties."""
        recommendations = {
            "conceptual": [
                f"Use more visual diagrams for {topic}",
                "Provide real-world analogies",
                "Break down complex concepts into smaller parts"
            ],
            "practical": [
                f"Add more hands-on exercises for {topic}",
                "Provide step-by-step tutorials",
                "Include troubleshooting guides"
            ],
            "pacing": [
                "Adjust lesson pace based on student feedback",
                "Add more practice time",
                "Provide additional resources for self-study"
            ],
            "engagement": [
                f"Use more interactive examples for {topic}",
                "Include current, relevant use cases",
                "Add gamification elements"
            ]
        }
        return recommendations.get(difficulty_type, ["Review and adjust teaching approach"])

    def _generate_agent_instructions(self, topic: str, difficulty_type: str, learning_style: str) -> Dict[str, str]:
        """Generate specific instructions for agents to address difficulties."""
        return {
            "tutor": f"Focus on {difficulty_type} aspects of {topic}, adapt to {learning_style} learning style",
            "assessment": f"Create questions that test {difficulty_type} understanding of {topic}",
            "planning": f"Adjust plan to address {difficulty_type} challenges with {topic}",
            "quiz": f"Generate questions that reinforce {difficulty_type} aspects of {topic}"
        }

    def _identify_performance_issues(self, agent_name: str, metrics: Dict[str, Any], satisfaction: float) -> List[str]:
        """Identify performance issues for an agent."""
        issues = []
        if satisfaction < 0.7:
            issues.append("Low student satisfaction")
        if metrics.get("response_time", 0) > 5:
            issues.append("Slow response times")
        if metrics.get("error_rate", 0) > 0.1:
            issues.append("High error rate")
        if metrics.get("engagement_score", 0) < 0.6:
            issues.append("Low engagement")
        return issues

    def _generate_performance_improvements(self, agent_name: str, metrics: Dict[str, Any], satisfaction: float) -> List[str]:
        """Generate performance improvement suggestions."""
        improvements = []
        if satisfaction < 0.7:
            improvements.append("Improve response quality and relevance")
        if metrics.get("response_time", 0) > 5:
            improvements.append("Optimize response generation speed")
        if metrics.get("error_rate", 0) > 0.1:
            improvements.append("Reduce error rate through better validation")
        if metrics.get("engagement_score", 0) < 0.6:
            improvements.append("Enhance engagement through interactive content")
        return improvements

    def _generate_agent_improvement_instructions(self, agent_name: str, metrics: Dict[str, Any], satisfaction: float) -> Dict[str, str]:
        """Generate specific improvement instructions for agents."""
        instructions = {}
        if satisfaction < 0.7:
            instructions["quality"] = "Focus on providing more accurate and helpful responses"
        if metrics.get("response_time", 0) > 5:
            instructions["speed"] = "Optimize for faster response generation"
        if metrics.get("error_rate", 0) > 0.1:
            instructions["accuracy"] = "Improve validation and error handling"
        if metrics.get("engagement_score", 0) < 0.6:
            instructions["engagement"] = "Make responses more interactive and engaging"
        return instructions

    def _analyze_learning_style_effectiveness(self, learning_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze effectiveness of different learning styles."""
        return {
            "visual": learning_data.get("visual_effectiveness", 0.8),
            "auditory": learning_data.get("auditory_effectiveness", 0.7),
            "reading": learning_data.get("reading_effectiveness", 0.9),
            "kinesthetic": learning_data.get("kinesthetic_effectiveness", 0.6)
        }

    def _analyze_learning_pace(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learning pace and progress patterns."""
        return {
            "current_pace": progress_data.get("pace", "moderate"),
            "pace_effectiveness": progress_data.get("pace_effectiveness", 0.8),
            "recommended_adjustments": ["Maintain current pace", "Add more practice time"]
        }

    def _analyze_engagement_patterns(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student engagement patterns."""
        return {
            "engagement_score": learning_data.get("engagement", 0.7),
            "peak_engagement_times": learning_data.get("peak_times", ["morning", "evening"]),
            "engagement_factors": ["Interactive content", "Real-world examples", "Progress feedback"]
        }

    def _generate_learning_optimizations(self, learning_data: Dict[str, Any], progress_data: Dict[str, Any]) -> List[str]:
        """Generate learning optimization suggestions."""
        return [
            "Adjust content delivery based on learning style effectiveness",
            "Optimize pacing based on progress patterns",
            "Enhance engagement through personalized content",
            "Provide more targeted practice opportunities"
        ]

    def _generate_personalization_suggestions(self, learning_data: Dict[str, Any], progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalization suggestions."""
        return {
            "content_adaptation": "Focus on most effective learning style",
            "pace_adjustment": "Optimize based on progress patterns",
            "engagement_enhancement": "Use preferred engagement factors",
            "practice_optimization": "Target weak areas with additional practice"
        }

    def _calculate_overall_performance(self, system_metrics: Dict[str, Any]) -> float:
        """Calculate overall system performance score."""
        return system_metrics.get("overall_score", 0.8)

    def _identify_system_bottlenecks(self, system_metrics: Dict[str, Any]) -> List[str]:
        """Identify system bottlenecks."""
        bottlenecks = []
        if system_metrics.get("response_time", 0) > 3:
            bottlenecks.append("Slow response times")
        if system_metrics.get("error_rate", 0) > 0.05:
            bottlenecks.append("High error rates")
        if system_metrics.get("user_satisfaction", 0) < 0.8:
            bottlenecks.append("Low user satisfaction")
        return bottlenecks

    def _analyze_user_satisfaction(self, user_feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user satisfaction from feedback."""
        if not user_feedback:
            return {"average_satisfaction": 0.8, "common_issues": [], "positive_feedback": []}
        
        satisfaction_scores = [f.get("satisfaction", 0.8) for f in user_feedback]
        return {
            "average_satisfaction": sum(satisfaction_scores) / len(satisfaction_scores),
            "common_issues": ["Slow responses", "Complex explanations"],
            "positive_feedback": ["Helpful content", "Good explanations"]
        }

    def _generate_system_optimizations(self, system_metrics: Dict[str, Any], user_feedback: List[Dict[str, Any]]) -> List[str]:
        """Generate system-wide optimization suggestions."""
        optimizations = []
        if system_metrics.get("response_time", 0) > 3:
            optimizations.append("Optimize response generation speed")
        if system_metrics.get("error_rate", 0) > 0.05:
            optimizations.append("Improve error handling and validation")
        if system_metrics.get("user_satisfaction", 0) < 0.8:
            optimizations.append("Enhance user experience and content quality")
        return optimizations

    def _prioritize_system_actions(self, system_metrics: Dict[str, Any], user_feedback: List[Dict[str, Any]]) -> List[str]:
        """Prioritize system improvement actions."""
        priorities = []
        if system_metrics.get("user_satisfaction", 0) < 0.7:
            priorities.append("HIGH: Improve user satisfaction")
        if system_metrics.get("error_rate", 0) > 0.1:
            priorities.append("HIGH: Reduce error rates")
        if system_metrics.get("response_time", 0) > 5:
            priorities.append("MEDIUM: Optimize response times")
        return priorities
