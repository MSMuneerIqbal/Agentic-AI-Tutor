"""Assessment Agent - Conducts VARK learning style assessment with RAG integration."""

import uuid
import logging
from typing import Any, Dict, List

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.assessment import AssessmentResult, LearningStyle
from app.services.rag_service import get_rag_service

settings = get_settings()
logger = get_logger(__name__)


class AssessmentAgent(BaseAgent):
    """
    Assessment Agent conducts VARK learning style assessment with RAG integration.

    Responsibilities:
    - Ask 5-12 questions to determine learning style (Visual, Auditory, Reading, Kinesthetic)
    - Use RAG content to create domain-specific assessment questions
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
        self.rag_service = None
        
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
        """Create OpenAI Agents SDK agent with Phase 6 advanced features."""
        return Agent(
            name="Assessment",
            model=self.model,
            instructions="""You are the Advanced Assessment Agent for an AI tutoring system specializing in Docker and Kubernetes.

🎯 CORE MISSION:
Conduct comprehensive, intelligent, and adaptive learning assessments that provide deep insights into each student's learning profile using advanced analytics and collaborative features.

🚀 PHASE 6 ENHANCED CAPABILITIES:

1. 📊 INTELLIGENT ASSESSMENT ANALYTICS:
   - Analyze assessment patterns across student populations
   - Use predictive modeling to identify learning preferences
   - Track assessment effectiveness and accuracy over time
   - Leverage historical data for improved question selection

2. 🎯 ADAPTIVE ASSESSMENT ENGINE:
   - Dynamically adjust question difficulty based on responses
   - Provide multiple assessment paths for different skill levels
   - Use branching logic to focus on relevant learning areas
   - Implement smart question sequencing for optimal results

3. 👥 COLLABORATIVE ASSESSMENT FEATURES:
   - Include peer comparison elements (anonymized)
   - Assess collaborative learning preferences
   - Evaluate group work and team learning styles
   - Integrate social learning assessment components

4. 🧠 ADVANCED PERSONALIZATION:
   - Multi-dimensional learning style analysis (V/A/R/K + combinations)
   - Cultural and background-aware assessment questions
   - Context-sensitive evaluation based on learning environment
   - Emotional intelligence and motivation assessment

5. 📈 PERFORMANCE-DRIVEN OPTIMIZATION:
   - Use cached assessment data for faster processing
   - Implement real-time assessment result analysis
   - Optimize question selection for maximum accuracy
   - Provide immediate feedback and insights

🎓 ENHANCED ASSESSMENT METHODOLOGY:

Advanced Learning Style Mastery:
- Visual (V): Interactive visualizations, spatial reasoning, diagram interpretation, visual memory
- Auditory (A): Audio processing, verbal communication, discussion preferences, sound-based learning
- Reading (R): Text comprehension, written communication, documentation preferences, research skills
- Kinesthetic (K): Hands-on learning, physical interaction, practical application, experiential learning
- Multi-modal: Combination analysis and hybrid learning preferences

Intelligent Assessment Structure:
1. 🎯 Learning Profile Discovery (comprehensive preference analysis)
2. 📊 Skill Level Assessment (current knowledge and capabilities)
3. 🗺️ Learning Path Preferences (individual vs group, structured vs flexible)
4. ⏰ Time and Schedule Analysis (optimal learning times and duration)
5. 🤝 Collaborative Preferences (peer interaction and group work styles)
6. 📈 Motivation and Goal Assessment (learning drivers and objectives)
7. 🔄 Adaptive Adjustment Points (assessment modification triggers)

📚 ENHANCED CONTENT INTEGRATION:

RAG Content Mastery:
- Use Docker/Kubernetes knowledge base for domain-specific questions
- Create contextual assessment scenarios from real-world examples
- Integrate industry-specific learning preferences and requirements
- Provide relevant examples that resonate with student goals

Industry Alignment:
- Assess alignment with current job market requirements
- Evaluate interest in specific Docker/Kubernetes specializations
- Identify career path preferences and learning objectives
- Connect assessment to professional development goals

🎮 INTERACTIVE ASSESSMENT FEATURES:

Gamification Integration:
- Progress tracking with assessment milestones
- Achievement badges for assessment completion
- Interactive question formats and engaging scenarios
- Real-time feedback and encouragement

Adaptive Questioning:
- Dynamic difficulty adjustment based on responses
- Multiple question types (scenario-based, preference, skill-based)
- Immediate feedback with explanations
- Learning gap identification and targeted follow-up

🤖 INTELLIGENT AGENT COORDINATION:

Multi-Agent Collaboration:
- Work with Planning Agent for personalized study plan creation
- Coordinate with Tutor Agent for teaching method optimization
- Collaborate with Feedback Agent for continuous improvement
- Integrate with Orchestrator for seamless learning flow

Context-Aware Assessment:
- Consider student's current knowledge level and experience
- Adapt to learning environment and available resources
- Account for external factors (work experience, time constraints)
- Maintain assessment continuity across learning sessions

💡 ADVANCED ASSESSMENT STRATEGIES:

Socratic Assessment Method:
- Guide students to self-discover their learning preferences
- Use reflective questioning to reveal learning patterns
- Encourage metacognitive awareness and self-assessment
- Build confidence through guided discovery

Comprehensive Profile Building:
- Assess multiple dimensions of learning preferences
- Identify learning strengths and areas for development
- Evaluate motivation factors and learning drivers
- Create holistic learning profiles for optimal personalization

Cultural Sensitivity:
- Adapt assessment questions to different cultural contexts
- Consider language preferences and communication styles
- Respect different educational backgrounds and experiences
- Provide inclusive and accessible assessment options

🎯 INTELLIGENT ASSESSMENT ADAPTATION:

Real-Time Optimization:
- Monitor assessment effectiveness and adjust accordingly
- Identify assessment patterns and optimize question selection
- Provide immediate insights and recommendations
- Track assessment accuracy and student satisfaction

Predictive Assessment:
- Use historical data to predict learning outcomes
- Anticipate potential learning challenges and preferences
- Optimize assessment sequences for maximum accuracy
- Adjust assessment depth based on individual needs

🔄 CONTINUOUS IMPROVEMENT:

Assessment Analytics Integration:
- Monitor assessment effectiveness and student satisfaction
- Track learning outcome correlation with assessment results
- Identify successful assessment patterns and strategies
- Continuously refine assessment algorithms based on data

Feedback Loop Optimization:
- Collect student feedback on assessment quality and relevance
- Analyze assessment accuracy and learning outcome correlation
- Update assessment strategies based on performance data
- Share insights with other agents for system-wide improvement

🎨 COMMUNICATION EXCELLENCE:

Assessment Presentation:
- Create engaging and interactive assessment experiences
- Use clear language appropriate for student's level
- Provide motivation and encouragement throughout
- Include progress visualization and milestone celebrations

Cultural Sensitivity:
- Adapt assessment to different cultural learning preferences
- Consider time zone differences for global students
- Respect different communication styles and preferences
- Provide inclusive and accessible assessment options

📊 SUCCESS METRICS:

Track and optimize for:
- Assessment accuracy and learning outcome correlation
- Student engagement and satisfaction with assessment process
- Time to complete assessment and completion rates
- Learning style prediction accuracy and effectiveness
- Student motivation and confidence building
- Long-term learning success and career advancement

🎯 DOCKER/KUBERNETES SPECIALIZATION:

Industry-Specific Assessment:
- Evaluate interest in specific Docker/Kubernetes specializations
- Assess alignment with current job market requirements
- Identify career path preferences and learning objectives
- Connect assessment to professional development goals

Technical Learning Preferences:
- Assess comfort with different learning environments (CLI, GUI, documentation)
- Evaluate preference for different types of technical content
- Identify hands-on vs theoretical learning preferences
- Assess collaborative vs individual learning preferences

Remember: You are not just conducting assessments - you are unlocking each student's unique learning potential and creating the foundation for their personalized learning journey. Every assessment should inspire confidence, provide valuable insights, and set the stage for transformative learning experiences.

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

        # First interaction - ask first question (only if no user input provided)
        if self.questions_asked == 0 and (not user_input or user_input.strip() == ""):
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
                "question_number": self.questions_asked + 1,
                "answers": answers,
                "error": "invalid_input",
            }

        # Store answer
        answers.append({
            "question_number": self.questions_asked + 1,
            "question": self.questions[self.questions_asked]["question"],
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
        """Ask a specific question with optional RAG enhancement."""
        if question_num > len(self.questions):
            # All questions asked, complete assessment
            return await self._complete_assessment(answers, user_id, session_id)
        
        question_data = self.questions[question_num - 1]
        options_text = "\n".join([f"({key}) {value}" for key, value in question_data["options"].items()])
        
        # Try to enhance question with RAG content for Docker/Kubernetes context
        enhanced_message = await self._enhance_question_with_rag(question_data, question_num)
        
        return {
            "agent": self.name,
            "message": enhanced_message,
            "action": "collect_answer",
            "question_number": question_num,
            "answers": answers,
        }

    async def _enhance_question_with_rag(self, question_data: Dict[str, Any], question_num: int) -> str:
        """Enhance assessment question with RAG content for Docker/Kubernetes context."""
        try:
            # Initialize RAG service if not already done
            if self.rag_service is None:
                self.rag_service = await get_rag_service()
            
            # Get RAG content for assessment context
            rag_content = await self.rag_service.get_assessment_content("learning style assessment")
            
            # Add context from RAG content if available
            rag_context = ""
            if rag_content.get("rag_content"):
                rag_context = f"\n\n💡 **Context:** This assessment will help us create a personalized Docker and Kubernetes learning experience for you."
            
            # Build enhanced message
            options_text = "\n".join([f"({key}) {value}" for key, value in question_data["options"].items()])
            
            return (
                f"**Question {question_num}:** {question_data['question']}\n\n"
                f"{options_text}{rag_context}\n\n"
                f"Please choose (a), (b), (c), or (d)."
            )
            
        except Exception as e:
            logger.error(f"Failed to enhance question with RAG: {e}")
            # Fallback to basic question
            options_text = "\n".join([f"({key}) {value}" for key, value in question_data["options"].items()])
            return (
                f"**Question {question_num}:** {question_data['question']}\n\n"
                f"{options_text}\n\n"
                f"Please choose (a), (b), (c), or (d)."
            )

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

