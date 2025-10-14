"""
Quiz Agent - Generates and evaluates quizzes for knowledge assessment with RAG integration.
"""

import logging
import random
from typing import Any, Dict, List, Optional

from agents import Agent

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
settings = get_settings()


class QuizAgent(BaseAgent):
    """
    Quiz Agent generates and evaluates quizzes for knowledge assessment.

    Responsibilities:
    - Generate quiz questions based on RAG content from Docker/Kubernetes books
    - Create multiple choice, true/false, and practical questions
    - Evaluate student responses and provide feedback
    - Assess knowledge gaps and provide remediation suggestions
    - Handle topic skipping assessment quizzes
    """

    def __init__(self):
        """Initialize Quiz Agent."""
        super().__init__(name="Quiz", model=settings.gemini_model)
        self.agent = self._create_agent()
        self.rag_service = None
        self.current_quiz = None
        self.quiz_questions = []
        self.current_question_index = 0
        self.student_answers = []
        self.quiz_score = 0

    def _create_agent(self) -> Agent:
        """Create OpenAI Agents SDK agent."""
        return Agent(
            name="Quiz",
            model=self.model,
            instructions="""You are the Advanced Quiz Agent for an AI tutoring system specializing in Docker and Kubernetes.

🎯 CORE MISSION:
Generate intelligent, adaptive, and comprehensive quizzes that accurately assess student knowledge while providing valuable learning experiences using advanced analytics and collaborative features.

🚀 PHASE 6 ENHANCED CAPABILITIES:

1. 📊 INTELLIGENT QUIZ ANALYTICS:
   - Analyze quiz performance patterns across student populations
   - Use predictive modeling to identify knowledge gaps
   - Track quiz effectiveness and question quality over time
   - Leverage historical data for improved question selection

2. 🎯 ADAPTIVE QUIZ ENGINE:
   - Dynamically adjust question difficulty based on responses
   - Provide multiple quiz paths for different skill levels
   - Use branching logic to focus on relevant knowledge areas
   - Implement smart question sequencing for optimal assessment

3. 👥 COLLABORATIVE QUIZ FEATURES:
   - Include peer comparison elements (anonymized)
   - Assess collaborative problem-solving skills
   - Evaluate group work and team knowledge sharing
   - Integrate social learning assessment components

4. 🧠 ADVANCED PERSONALIZATION:
   - Multi-dimensional knowledge assessment (theoretical, practical, analytical)
   - Cultural and background-aware question design
   - Context-sensitive evaluation based on learning environment
   - Emotional intelligence in feedback delivery

5. 📈 PERFORMANCE-DRIVEN OPTIMIZATION:
   - Use cached quiz data for faster processing
   - Implement real-time quiz result analysis
   - Optimize question selection for maximum accuracy
   - Provide immediate feedback and insights

🎓 ENHANCED QUIZ METHODOLOGY:

Advanced Question Types:
- Multiple Choice (4-5 options with detailed explanations)
- True/False with comprehensive reasoning
- Practical/Scenario-based questions with real-world context
- Command/Configuration questions with hands-on application
- Case Study questions with complex problem-solving
- Collaborative questions requiring peer interaction
- Adaptive questions that adjust based on previous responses

Intelligent Quiz Structure:
1. 🎯 Knowledge Profile Assessment (comprehensive skill evaluation)
2. 📊 Difficulty Progression (adaptive challenge levels)
3. 🗺️ Learning Path Integration (quiz results inform study plans)
4. ⏰ Time Management (optimal quiz duration and pacing)
5. 🤝 Collaborative Elements (peer interaction and group assessment)
6. 📈 Progress Tracking (analytics and feedback loops)
7. 🔄 Adaptive Adjustment Points (quiz modification triggers)

📚 ENHANCED CONTENT INTEGRATION:

RAG Content Mastery:
- Comprehensive Docker/Kubernetes knowledge base analysis
- Cross-reference multiple learning resources for question creation
- Identify prerequisite relationships and knowledge dependencies
- Create question clusters for related topic mastery

Industry Alignment:
- Map quiz questions to current job market requirements
- Integrate latest industry trends and emerging technologies
- Align with professional certification paths (Docker, Kubernetes, CKA, etc.)
- Connect assessment to real-world career scenarios

🎮 INTERACTIVE QUIZ FEATURES:

Gamification Integration:
- Progress tracking with quiz milestones and achievements
- Learning streaks and challenge systems
- Peer comparison and leaderboards (anonymized)
- Skill-based progression and leveling

Adaptive Assessment:
- Real-time difficulty adjustment based on performance
- Multiple question formats and interactive elements
- Immediate feedback with detailed explanations
- Learning gap identification and targeted remediation

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

💡 ADVANCED QUIZ STRATEGIES:

Socratic Questioning Method:
- Guide students to discover answers through strategic questioning
- Use reflective questioning to reveal understanding levels
- Encourage metacognitive awareness and self-assessment
- Build confidence through guided discovery

Comprehensive Knowledge Assessment:
- Assess multiple dimensions of understanding (factual, conceptual, procedural)
- Identify learning strengths and areas for development
- Evaluate problem-solving skills and critical thinking
- Create holistic knowledge profiles for optimal personalization

Cultural Sensitivity:
- Adapt quiz questions to different cultural contexts
- Consider language preferences and communication styles
- Respect different educational backgrounds and experiences
- Provide inclusive and accessible assessment options

🎯 INTELLIGENT QUIZ ADAPTATION:

Real-Time Optimization:
- Monitor quiz effectiveness and adjust accordingly
- Identify quiz patterns and optimize question selection
- Provide immediate insights and recommendations
- Track quiz accuracy and student satisfaction

Predictive Assessment:
- Use historical data to predict learning outcomes
- Anticipate potential knowledge gaps and challenges
- Optimize quiz sequences for maximum accuracy
- Adjust quiz depth based on individual needs

🔄 CONTINUOUS IMPROVEMENT:

Quiz Analytics Integration:
- Monitor quiz effectiveness and student satisfaction
- Track learning outcome correlation with quiz results
- Identify successful quiz patterns and strategies
- Continuously refine quiz algorithms based on data

Feedback Loop Optimization:
- Collect student feedback on quiz quality and relevance
- Analyze quiz accuracy and learning outcome correlation
- Update quiz strategies based on performance data
- Share insights with other agents for system-wide improvement

🎨 COMMUNICATION EXCELLENCE:

Quiz Presentation:
- Create engaging and interactive quiz experiences
- Use clear language appropriate for student's level
- Provide motivation and encouragement throughout
- Include progress visualization and milestone celebrations

Cultural Sensitivity:
- Adapt quiz to different cultural learning preferences
- Consider time zone differences for global students
- Respect different communication styles and preferences
- Provide inclusive and accessible quiz options

📊 SUCCESS METRICS:

Track and optimize for:
- Quiz accuracy and learning outcome correlation
- Student engagement and satisfaction with quiz process
- Time to complete quiz and completion rates
- Knowledge assessment accuracy and effectiveness
- Student motivation and confidence building
- Long-term learning success and career advancement

🎯 DOCKER/KUBERNETES SPECIALIZATION:

Industry-Specific Assessment:
- Evaluate knowledge of specific Docker/Kubernetes specializations
- Assess alignment with current job market requirements
- Identify career path preferences and learning objectives
- Connect assessment to professional development goals

Technical Knowledge Assessment:
- Assess comfort with different technical environments (CLI, GUI, documentation)
- Evaluate understanding of different types of technical content
- Identify hands-on vs theoretical knowledge preferences
- Assess collaborative vs individual problem-solving skills

🎯 TOPIC SKIPPING INTELLIGENCE:

Smart Skipping Assessment:
- Generate comprehensive quiz for skipped topics
- Test both theoretical knowledge and practical understanding
- Use adaptive questioning to gauge true comprehension
- Provide detailed remediation if knowledge gaps exist

Assessment Thresholds:
- Pass threshold: 70% or higher with understanding demonstration
- Fail threshold: Below 70% requires targeted remediation
- Advanced threshold: 90%+ indicates mastery and acceleration potential
- Remediation threshold: Below 50% requires fundamental review

Remember: You are not just conducting quizzes - you are providing comprehensive knowledge assessment that guides students toward mastery and career success. Every quiz should inspire confidence, provide valuable insights, and set the stage for continued learning growth.

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
        Execute quiz logic.

        Args:
            user_input: User's answer or quiz request
            context: Quiz context (topic, quiz_type, session_state, etc.)

        Returns:
            Response dictionary with quiz content or evaluation
        """
        topic = context.get("topic", "Docker and Kubernetes")
        quiz_type = context.get("quiz_type", "knowledge_check")
        session_state = context.get("session_state", "QUIZ")

        try:
            # Initialize RAG service if not already done
            if self.rag_service is None:
                self.rag_service = await get_rag_service()

            # Handle different quiz scenarios
            if quiz_type == "topic_skip_assessment":
                return await self._handle_topic_skip_quiz(topic, user_input, context)
            elif quiz_type == "knowledge_check":
                return await self._handle_knowledge_check_quiz(topic, user_input, context)
            elif quiz_type == "chapter_completion":
                return await self._handle_chapter_completion_quiz(topic, user_input, context)
            else:
                return await self._handle_general_quiz(topic, user_input, context)

        except Exception as e:
            logger.error(f"Quiz Agent execution failed: {e}")
            return {
                "agent": self.name,
                "message": f"I apologize, but I encountered an issue generating the quiz for {topic}. Let me try a different approach.",
                "action": "error_recovery",
                "topic": topic,
                "error": str(e)
            }

    async def _handle_topic_skip_quiz(self, topic: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quiz for topic skipping assessment."""
        if not self.current_quiz:
            # Generate quiz for skipped topic
            self.current_quiz = await self._generate_topic_skip_quiz(topic)
            self.quiz_questions = self.current_quiz["questions"]
            self.current_question_index = 0
            self.student_answers = []
            self.quiz_score = 0

            return {
                "agent": self.name,
                "message": f"Let's assess your knowledge of {topic} to see if you can skip it. I'll ask you {len(self.quiz_questions)} questions.",
                "action": "start_quiz",
                "topic": topic,
                "quiz_type": "topic_skip_assessment",
                "total_questions": len(self.quiz_questions),
                "current_question": 1,
                "question": self.quiz_questions[0]
            }

        # Process answer and move to next question
        return await self._process_quiz_answer(user_input, context)

    async def _handle_knowledge_check_quiz(self, topic: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general knowledge check quiz."""
        if not self.current_quiz:
            # Generate knowledge check quiz
            self.current_quiz = await self._generate_knowledge_check_quiz(topic)
            self.quiz_questions = self.current_quiz["questions"]
            self.current_question_index = 0
            self.student_answers = []
            self.quiz_score = 0

            return {
                "agent": self.name,
                "message": f"Let's test your understanding of {topic}. I'll ask you {len(self.quiz_questions)} questions.",
                "action": "start_quiz",
                "topic": topic,
                "quiz_type": "knowledge_check",
                "total_questions": len(self.quiz_questions),
                "current_question": 1,
                "question": self.quiz_questions[0]
            }

        # Process answer and move to next question
        return await self._process_quiz_answer(user_input, context)

    async def _handle_chapter_completion_quiz(self, topic: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quiz after chapter completion."""
        if not self.current_quiz:
            # Generate chapter completion quiz
            self.current_quiz = await self._generate_chapter_completion_quiz(topic)
            self.quiz_questions = self.current_quiz["questions"]
            self.current_question_index = 0
            self.student_answers = []
            self.quiz_score = 0

            return {
                "agent": self.name,
                "message": f"Great job completing the chapter on {topic}! Let's test your understanding with a quick quiz.",
                "action": "start_quiz",
                "topic": topic,
                "quiz_type": "chapter_completion",
                "total_questions": len(self.quiz_questions),
                "current_question": 1,
                "question": self.quiz_questions[0]
            }

        # Process answer and move to next question
        return await self._process_quiz_answer(user_input, context)

    async def _handle_general_quiz(self, topic: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general quiz request."""
        return {
            "agent": self.name,
            "message": f"I can create quizzes for {topic}. What type of quiz would you like? (knowledge check, topic assessment, or chapter review)",
            "action": "quiz_type_selection",
            "topic": topic
        }

    async def _process_quiz_answer(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process student's answer and move to next question or complete quiz."""
        # Store the answer
        self.student_answers.append({
            "question_index": self.current_question_index,
            "answer": user_input,
            "question": self.quiz_questions[self.current_question_index]
        })

        # Evaluate the answer
        is_correct = self._evaluate_answer(user_input, self.quiz_questions[self.current_question_index])
        if is_correct:
            self.quiz_score += 1

        # Move to next question or complete quiz
        self.current_question_index += 1

        if self.current_question_index >= len(self.quiz_questions):
            # Quiz completed
            return await self._complete_quiz(context)
        else:
            # Next question
            next_question = self.quiz_questions[self.current_question_index]
            feedback = self._get_answer_feedback(is_correct, self.quiz_questions[self.current_question_index - 1])

            return {
                "agent": self.name,
                "message": f"{feedback}\n\n**Question {self.current_question_index + 1}:** {next_question['question']}\n\n{self._format_question_options(next_question)}",
                "action": "next_question",
                "topic": context.get("topic"),
                "current_question": self.current_question_index + 1,
                "total_questions": len(self.quiz_questions),
                "question": next_question,
                "previous_feedback": feedback
            }

    async def _complete_quiz(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the quiz and provide results."""
        total_questions = len(self.quiz_questions)
        score_percentage = (self.quiz_score / total_questions) * 100
        topic = context.get("topic", "the topic")
        quiz_type = context.get("quiz_type", "knowledge_check")

        # Determine pass/fail for topic skip assessment
        passed = score_percentage >= 70
        quiz_result = "passed" if passed else "failed"

        # Generate detailed feedback
        feedback = self._generate_quiz_feedback(score_percentage, passed, topic)

        # Reset quiz state
        self.current_quiz = None
        self.quiz_questions = []
        self.current_question_index = 0
        self.student_answers = []
        self.quiz_score = 0

        return {
            "agent": self.name,
            "message": feedback,
            "action": "quiz_complete",
            "topic": topic,
            "quiz_type": quiz_type,
            "score": self.quiz_score,
            "total_questions": total_questions,
            "score_percentage": score_percentage,
            "passed": passed,
            "quiz_result": quiz_result,
            "next_state": "orchestrator" if quiz_type == "topic_skip_assessment" else "continue_learning"
        }

    async def _generate_topic_skip_quiz(self, topic: str) -> Dict[str, Any]:
        """Generate comprehensive quiz for topic skipping assessment."""
        try:
            # Get RAG content for the topic
            rag_content = await self.rag_service.get_quiz_content(topic)
            
            # Generate questions based on RAG content
            questions = self._generate_questions_from_rag(rag_content, topic, num_questions=5)
            
            return {
                "topic": topic,
                "type": "topic_skip_assessment",
                "questions": questions,
                "pass_threshold": 70,
                "description": f"Comprehensive assessment for {topic} to determine if you can skip this topic"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate topic skip quiz: {e}")
            return self._get_fallback_quiz(topic, "topic_skip_assessment")

    async def _generate_knowledge_check_quiz(self, topic: str) -> Dict[str, Any]:
        """Generate knowledge check quiz."""
        try:
            # Get RAG content for the topic
            rag_content = await self.rag_service.get_quiz_content(topic)
            
            # Generate questions based on RAG content
            questions = self._generate_questions_from_rag(rag_content, topic, num_questions=3)
            
            return {
                "topic": topic,
                "type": "knowledge_check",
                "questions": questions,
                "pass_threshold": 60,
                "description": f"Knowledge check for {topic}"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate knowledge check quiz: {e}")
            return self._get_fallback_quiz(topic, "knowledge_check")

    async def _generate_chapter_completion_quiz(self, topic: str) -> Dict[str, Any]:
        """Generate chapter completion quiz."""
        try:
            # Get RAG content for the topic
            rag_content = await self.rag_service.get_quiz_content(topic)
            
            # Generate questions based on RAG content
            questions = self._generate_questions_from_rag(rag_content, topic, num_questions=4)
            
            return {
                "topic": topic,
                "type": "chapter_completion",
                "questions": questions,
                "pass_threshold": 70,
                "description": f"Chapter completion quiz for {topic}"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate chapter completion quiz: {e}")
            return self._get_fallback_quiz(topic, "chapter_completion")

    def _generate_questions_from_rag(self, rag_content: Dict[str, Any], topic: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate quiz questions from RAG content."""
        rag_topics = rag_content.get("rag_content", [])
        questions = []

        # Generate questions based on available RAG content
        for i in range(min(num_questions, len(rag_topics) + 1)):
            if i < len(rag_topics):
                # Generate question from RAG content
                content = rag_topics[i]
                question = self._create_question_from_content(content, topic, i + 1)
            else:
                # Generate fallback question
                question = self._create_fallback_question(topic, i + 1)
            
            questions.append(question)

        return questions

    def _create_question_from_content(self, content: Dict[str, Any], topic: str, question_num: int) -> Dict[str, Any]:
        """Create a quiz question from RAG content."""
        content_text = content.get("content", "")
        source = content.get("source", "Docker/Kubernetes Book")
        
        # Create different types of questions based on content
        question_types = ["multiple_choice", "true_false", "practical"]
        question_type = random.choice(question_types)
        
        if question_type == "multiple_choice":
            return {
                "id": f"q{question_num}",
                "type": "multiple_choice",
                "question": f"Based on the content about {topic}, which of the following is correct?",
                "options": {
                    "a": f"Option A: {content_text[:50]}...",
                    "b": f"Option B: Alternative approach",
                    "c": f"Option C: {content_text[50:100]}...",
                    "d": f"Option D: Different method"
                },
                "correct_answer": "a",
                "explanation": f"According to {source}, the correct answer is based on the content: {content_text[:100]}...",
                "source": source
            }
        elif question_type == "true_false":
            return {
                "id": f"q{question_num}",
                "type": "true_false",
                "question": f"True or False: {content_text[:80]}...",
                "options": {
                    "a": "True",
                    "b": "False"
                },
                "correct_answer": "a",
                "explanation": f"This is true according to {source}: {content_text[:100]}...",
                "source": source
            }
        else:  # practical
            return {
                "id": f"q{question_num}",
                "type": "practical",
                "question": f"How would you apply this concept about {topic} in practice?",
                "options": {
                    "a": f"Use the approach described in {source}",
                    "b": "Use a different method",
                    "c": "Combine multiple approaches",
                    "d": "Use the most common approach"
                },
                "correct_answer": "a",
                "explanation": f"The best practice is described in {source}: {content_text[:100]}...",
                "source": source
            }

    def _create_fallback_question(self, topic: str, question_num: int) -> Dict[str, Any]:
        """Create a fallback question when RAG content is not available."""
        return {
            "id": f"q{question_num}",
            "type": "multiple_choice",
            "question": f"What is the most important concept to understand about {topic}?",
            "options": {
                "a": f"Understanding the fundamentals of {topic}",
                "b": f"Learning advanced techniques in {topic}",
                "c": f"Memorizing commands for {topic}",
                "d": f"Reading documentation about {topic}"
            },
            "correct_answer": "a",
            "explanation": f"Understanding the fundamentals is crucial for mastering {topic}.",
            "source": "General Knowledge"
        }

    def _get_fallback_quiz(self, topic: str, quiz_type: str) -> Dict[str, Any]:
        """Get fallback quiz when RAG content is not available."""
        questions = [
            self._create_fallback_question(topic, 1),
            self._create_fallback_question(topic, 2),
            self._create_fallback_question(topic, 3)
        ]
        
        return {
            "topic": topic,
            "type": quiz_type,
            "questions": questions,
            "pass_threshold": 70,
            "description": f"Basic assessment for {topic}"
        }

    def _evaluate_answer(self, user_answer: str, question: Dict[str, Any]) -> bool:
        """Evaluate if the user's answer is correct."""
        correct_answer = question.get("correct_answer", "")
        user_choice = user_answer.lower().strip()
        
        # Handle different answer formats
        if user_choice in ["a", "b", "c", "d"]:
            return user_choice == correct_answer
        elif user_choice in ["true", "false"]:
            return user_choice == correct_answer
        else:
            # Try to match with option text
            options = question.get("options", {})
            for key, value in options.items():
                if user_choice in value.lower():
                    return key == correct_answer
            
            return False

    def _get_answer_feedback(self, is_correct: bool, question: Dict[str, Any]) -> str:
        """Get feedback for the student's answer."""
        if is_correct:
            return f"✅ **Correct!** {question.get('explanation', 'Well done!')}"
        else:
            correct_answer = question.get("correct_answer", "")
            options = question.get("options", {})
            correct_text = options.get(correct_answer, "")
            return f"❌ **Incorrect.** The correct answer is ({correct_answer}) {correct_text}. {question.get('explanation', '')}"

    def _generate_quiz_feedback(self, score_percentage: float, passed: bool, topic: str) -> str:
        """Generate comprehensive quiz feedback."""
        if passed:
            if score_percentage >= 90:
                feedback = f"🎉 **Excellent!** You scored {score_percentage:.1f}% on the {topic} quiz. You have a strong understanding of this topic!"
            elif score_percentage >= 80:
                feedback = f"🎉 **Great job!** You scored {score_percentage:.1f}% on the {topic} quiz. You understand this topic well!"
            else:
                feedback = f"✅ **Good work!** You scored {score_percentage:.1f}% on the {topic} quiz. You have a solid understanding of this topic."
        else:
            feedback = f"📚 **Let's review together.** You scored {score_percentage:.1f}% on the {topic} quiz. Don't worry - this is a great opportunity to strengthen your understanding!"

        return feedback

    def _format_question_options(self, question: Dict[str, Any]) -> str:
        """Format question options for display."""
        options = question.get("options", {})
        options_text = "\n".join([f"({key}) {value}" for key, value in options.items()])
        return f"{options_text}\n\nPlease choose your answer."
