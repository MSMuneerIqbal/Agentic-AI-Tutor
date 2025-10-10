"""Tutor Agent - Delivers personalized lessons with RAG and Tavily integration."""

import logging
from typing import Any, Dict, List

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
settings = get_settings()


class TutorAgent(BaseAgent):
    """
    Tutor Agent delivers personalized lessons with RAG and Tavily integration.

    Responsibilities:
    - Deliver lessons adapted to user's learning style
    - Use RAG tool to retrieve supporting content from Docker/Kubernetes books
    - Use Tavily MCP for live examples and current best practices
    - Provide clear explanations with citations
    - Offer exercises and practice opportunities
    - Handle topic skipping with assessment
    """

    def __init__(self):
        """Initialize Tutor Agent."""
        super().__init__(name="Tutor", model=settings.gemini_model)
        self.agent = self._create_agent()
        self.rag_service = None

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent with Phase 6 advanced features."""
        return Agent(
            name="Tutor",
            model=self.model,
            instructions="""You are Olivia, the Advanced Tutor Agent for an AI tutoring system specializing in Docker and Kubernetes.

🎯 CORE MISSION:
Deliver personalized, adaptive, and engaging lessons that evolve with each student's learning journey using advanced AI capabilities.

🚀 PHASE 6 ENHANCED CAPABILITIES:

1. 📊 INTELLIGENT LEARNING ANALYTICS:
   - Track student progress in real-time
   - Adapt teaching pace based on performance metrics
   - Identify learning patterns and adjust accordingly
   - Use historical data to predict learning outcomes

2. 🎯 ADAPTIVE CONTENT DELIVERY:
   - Dynamically adjust lesson complexity based on student mastery
   - Provide multiple learning paths for different skill levels
   - Offer alternative explanations when student struggles
   - Accelerate learning for advanced students

3. 👥 COLLABORATIVE LEARNING SUPPORT:
   - Encourage peer learning and study groups
   - Facilitate knowledge sharing between students
   - Guide students to help each other effectively
   - Create collaborative learning opportunities

4. 🧠 ADVANCED PERSONALIZATION:
   - Deep learning style adaptation (V/A/R/K + combinations)
   - Context-aware content delivery
   - Emotional intelligence in responses
   - Cultural and background sensitivity

5. 📈 PERFORMANCE OPTIMIZATION:
   - Use cached content for faster responses
   - Leverage predictive analytics for better outcomes
   - Optimize learning sequences for maximum retention
   - Provide real-time feedback and adjustments

🎓 ENHANCED TEACHING METHODOLOGY:

Learning Style Mastery:
- Visual (V): Interactive diagrams, mind maps, visual storytelling, AR/VR concepts
- Auditory (A): Podcast-style explanations, verbal discussions, sound-based learning
- Reading (R): Comprehensive documentation, detailed guides, written exercises
- Kinesthetic (K): Hands-on labs, interactive simulations, real-world projects
- Multi-modal: Combine styles for maximum engagement

Advanced Lesson Structure:
1. 🎯 Learning Objective Preview (what student will achieve)
2. 📊 Progress Check (where student currently stands)
3. 🧠 Core Concept Delivery (adapted to learning style + analytics)
4. 🌟 Real-world Application (with live examples from Tavily)
5. 🤝 Collaborative Element (peer interaction opportunity)
6. ✅ Understanding Verification (adaptive assessment)
7. 🚀 Next Steps Preview (personalized learning path)

📚 ENHANCED CONTENT INTEGRATION:

RAG Content Usage:
- Retrieve relevant content from Docker/Kubernetes knowledge base
- Cross-reference multiple sources for comprehensive understanding
- Provide source citations with credibility indicators
- Update content based on latest industry practices

Tavily Live Examples:
- Fetch current best practices and real-world implementations
- Show industry trends and emerging technologies
- Provide troubleshooting examples from actual scenarios
- Connect learning to current job market requirements

🎮 INTERACTIVE LEARNING FEATURES:

Gamification Elements:
- Progress badges and achievements
- Learning streaks and challenges
- Peer comparison (anonymized)
- Skill-based leveling system

Adaptive Assessments:
- Real-time difficulty adjustment
- Multiple question types (MCQ, practical, scenario-based)
- Immediate feedback with explanations
- Learning gap identification and remediation

🤖 INTELLIGENT AGENT COORDINATION:

Multi-Agent Collaboration:
- Work seamlessly with Planning Agent for curriculum adaptation
- Coordinate with Assessment Agent for skill evaluation
- Collaborate with Feedback Agent for continuous improvement
- Integrate with Orchestrator for optimal learning flow

Context Awareness:
- Remember previous interactions and learning history
- Adapt to student's emotional state and engagement level
- Consider external factors (time of day, learning environment)
- Maintain conversation continuity across sessions

💡 ADVANCED TEACHING STRATEGIES:

Socratic Method:
- Guide students to discover answers through questioning
- Encourage critical thinking and problem-solving
- Build confidence through guided discovery
- Develop independent learning skills

Scaffolding Approach:
- Break complex topics into manageable steps
- Provide support that gradually decreases
- Build on previous knowledge systematically
- Ensure mastery before advancing

Metacognitive Development:
- Teach students how to learn effectively
- Develop self-assessment skills
- Encourage reflection on learning process
- Build lifelong learning capabilities

🎯 TOPIC SKIPPING INTELLIGENCE:

Smart Skipping Logic:
- Analyze student's current knowledge level
- Assess topic importance for learning objectives
- Consider prerequisite dependencies
- Provide alternative learning paths

Assessment Integration:
- Generate targeted quizzes for skipped topics
- Use adaptive questioning to gauge understanding
- Provide remediation if knowledge gaps exist
- Track skipping patterns for curriculum improvement

🔄 CONTINUOUS IMPROVEMENT:

Learning Analytics Integration:
- Monitor teaching effectiveness in real-time
- Adjust strategies based on student outcomes
- Identify successful teaching patterns
- Continuously refine personalization algorithms

Feedback Loop:
- Collect student feedback on lesson quality
- Analyze learning outcomes and satisfaction
- Update teaching methods based on data
- Share insights with other agents for system-wide improvement

🎨 COMMUNICATION EXCELLENCE:

Tone and Style:
- Warm, encouraging, and supportive
- Professional yet approachable
- Culturally sensitive and inclusive
- Emotionally intelligent responses

Language Adaptation:
- Adjust complexity based on student level
- Use appropriate technical terminology
- Provide clear explanations for complex concepts
- Maintain engaging and conversational tone

📊 SUCCESS METRICS:

Track and optimize for:
- Student engagement and retention
- Learning outcome achievement
- Time to mastery
- Student satisfaction scores
- Knowledge retention rates
- Skill application success

Remember: You are not just teaching Docker and Kubernetes - you are developing the next generation of cloud-native professionals. Every interaction should inspire, educate, and empower students to achieve their learning goals.

Available Advanced Tools:
- RAG content from comprehensive Docker/Kubernetes knowledge base
- Live examples and best practices from Tavily MCP
- Real-time learning analytics and progress tracking
- Collaborative learning platform integration
- Adaptive assessment and feedback systems
- Multi-agent coordination and context sharing""",
        )

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute tutoring logic with RAG and Tavily integration.

        Args:
            user_input: User question or response
            context: Lesson context (topic, learning_style, progress, session_state)

        Returns:
            Response dictionary with lesson content
        """
        topic = context.get("topic", "Docker and Kubernetes")
        learning_style = context.get("learning_style", "V")
        progress = context.get("progress", 0)
        session_state = context.get("session_state", "TUTORING")

        try:
            # Initialize RAG service if not already done
            if self.rag_service is None:
                self.rag_service = await get_rag_service()

            # Handle topic skipping request
            if "skip" in user_input.lower() and "topic" in user_input.lower():
                return await self._handle_topic_skip_request(topic, context)

            # Handle quiz results (from orchestrator)
            if context.get("quiz_result") == "failed":
                return await self._handle_failed_quiz(topic, learning_style, context)
            elif context.get("quiz_result") == "passed":
                return await self._handle_passed_quiz(topic, context)

            # Generate comprehensive lesson content
            lesson_content = await self._generate_lesson_content(topic, learning_style, user_input, progress)
            
            return {
                "agent": self.name,
                "message": lesson_content["message"],
                "action": lesson_content["action"],
                "topic": topic,
                "progress": progress + 1,
                "learning_style": learning_style,
                "rag_content": lesson_content.get("rag_content", []),
                "live_examples": lesson_content.get("live_examples", []),
                "best_practices": lesson_content.get("best_practices", []),
                "troubleshooting": lesson_content.get("troubleshooting", [])
            }

        except Exception as e:
            logger.error(f"Tutor Agent execution failed: {e}")
            return {
                "agent": self.name,
                "message": f"I apologize, but I encountered an issue. Let me try a different approach to explain {topic}.",
                "action": "error_recovery",
                "topic": topic,
                "progress": progress,
                "error": str(e)
            }

    async def _generate_lesson_content(self, topic: str, learning_style: str, user_input: str, progress: int) -> Dict[str, Any]:
        """Generate comprehensive lesson content using RAG and Tavily."""
        try:
            # Get comprehensive lesson content from RAG service
            lesson_data = await self.rag_service.get_tutor_lesson_content(topic, learning_style)
            
            # Extract content
            rag_content = lesson_data.get("rag_content", [])
            live_examples = lesson_data.get("live_examples", [])
            best_practices = lesson_data.get("best_practices", [])
            troubleshooting = lesson_data.get("troubleshooting", [])
            
            # Generate lesson message based on learning style and progress
            message = self._build_lesson_message(topic, learning_style, user_input, progress, rag_content, live_examples)
            
            return {
                "message": message,
                "action": "deliver_lesson" if progress == 0 else "continue_lesson",
                "rag_content": rag_content,
                "live_examples": live_examples,
                "best_practices": best_practices,
                "troubleshooting": troubleshooting
            }
            
        except Exception as e:
            logger.error(f"Failed to generate lesson content: {e}")
            return {
                "message": self._get_fallback_lesson(topic, learning_style),
                "action": "deliver_lesson",
                "rag_content": [],
                "live_examples": [],
                "best_practices": [],
                "troubleshooting": []
            }

    def _build_lesson_message(self, topic: str, learning_style: str, user_input: str, progress: int, 
                            rag_content: List[Dict], live_examples: List[Dict]) -> str:
        """Build lesson message adapted to learning style with RAG and live examples."""
        
        if progress == 0:
            # Lesson introduction
            intro = self._get_lesson_intro(topic, learning_style)
            
            # Add RAG content if available
            if rag_content:
                intro += f"\n\n📚 **From our Docker/Kubernetes resources:**\n"
                for content in rag_content[:2]:  # Show first 2 RAG results
                    intro += f"• {content['content'][:100]}...\n"
            
            # Add live examples if available
            if live_examples:
                intro += f"\n\n🌐 **Live Example:**\n"
                example = live_examples[0]
                intro += f"• {example['title']}: {example['content'][:100]}...\n"
            
            return intro
        
        else:
            # Continue lesson based on user input
            response = f"Great question about {topic}! Let me explain that further...\n\n"
            
            # Add relevant RAG content
            if rag_content:
                response += f"📚 **According to our resources:**\n"
                for content in rag_content[:1]:
                    response += f"{content['content']}\n\n"
            
            # Add live examples
            if live_examples:
                response += f"🌐 **Real-world example:**\n"
                example = live_examples[0]
                response += f"{example['title']}: {example['content']}\n\n"
            
            # Add learning style specific guidance
            response += self._get_learning_style_guidance(learning_style, topic)
            
            return response

    def _get_lesson_intro(self, topic: str, learning_style: str) -> str:
        """Get lesson introduction adapted to learning style."""
        intros = {
            "V": f"Let's learn about **{topic}**! 🎨\n\nImagine containers as shipping boxes that can be moved anywhere...",
            "A": f"Let's talk about **{topic}**! 🎧\n\nThink of it this way - like a conversation between systems...",
            "R": f"Let's study **{topic}**! 📚\n\nHere's a detailed explanation with documentation...",
            "K": f"Let's practice **{topic}**! 🛠️\n\nWe'll learn by doing hands-on exercises...",
        }
        return intros.get(
            learning_style,
            f"Let's learn about **{topic}**!\n\nI'll explain this step by step...",
        )

    def _get_learning_style_guidance(self, learning_style: str, topic: str) -> str:
        """Get learning style specific guidance."""
        guidance = {
            "V": f"💡 **Visual Tip:** Try drawing a diagram of how {topic} works. Visualizing helps with understanding!",
            "A": f"💡 **Discussion Tip:** Try explaining {topic} out loud to someone. Teaching helps you learn!",
            "R": f"💡 **Reading Tip:** Take notes while studying {topic}. Writing helps retention!",
            "K": f"💡 **Practice Tip:** Try the commands yourself! Hands-on practice is the best way to learn {topic}!",
        }
        return guidance.get(learning_style, f"💡 **Tip:** Practice makes perfect with {topic}!")

    def _get_fallback_lesson(self, topic: str, learning_style: str) -> str:
        """Get fallback lesson when RAG/Tavily is unavailable."""
        return f"Let's learn about **{topic}**! 🚀\n\nI'll explain this concept step by step, adapted to your {learning_style} learning style.\n\nDo you have any specific questions about {topic}?"

    async def _handle_topic_skip_request(self, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle student request to skip a topic."""
        return {
            "agent": self.name,
            "message": f"This topic ({topic}) has benefits for you. Please complete in sequence, then go next. Understanding {topic} will help you with more advanced concepts later.",
            "action": "topic_skip_guidance",
            "topic": topic,
            "skip_request": True,
            "next_state": "waiting_for_confirmation"
        }

    async def _handle_failed_quiz(self, topic: str, learning_style: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed quiz result - teach the topic properly."""
        return {
            "agent": self.name,
            "message": f"I see you struggled with the {topic} quiz. No worries! Let's learn this topic properly together. I'll explain it step by step, adapted to your {learning_style} learning style.",
            "action": "remediation_lesson",
            "topic": topic,
            "learning_style": learning_style,
            "remediation": True
        }

    async def _handle_passed_quiz(self, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle passed quiz result - congratulate and move to next topic."""
        return {
            "agent": self.name,
            "message": f"🎉 Congratulations! You passed the {topic} quiz! You clearly understand this topic well. Let's move on to the next topic in your learning path.",
            "action": "quiz_passed",
            "topic": topic,
            "next_state": "next_topic"
        }

