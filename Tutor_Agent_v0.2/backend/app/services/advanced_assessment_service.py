"""
Advanced Assessment Service for Phase 6
Provides intelligent assessment, adaptive testing, and learning analytics
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from app.core.database import get_db
from app.models.quiz import QuizAttempt
from app.models.assessment import AssessmentResult
from app.services.analytics_service import get_analytics_service

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Types of assessment questions."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_IN_BLANK = "fill_in_blank"
    PRACTICAL_EXERCISE = "practical_exercise"
    CODE_REVIEW = "code_review"
    SCENARIO_BASED = "scenario_based"

class DifficultyLevel(Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class AssessmentType(Enum):
    """Types of assessments."""
    DIAGNOSTIC = "diagnostic"
    FORMATIVE = "formative"
    SUMMATIVE = "summative"
    ADAPTIVE = "adaptive"
    PEER_REVIEW = "peer_review"

@dataclass
class AssessmentQuestion:
    """Assessment question definition."""
    id: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    topic: str
    question_text: str
    options: List[str]  # For multiple choice
    correct_answer: str
    explanation: str
    learning_objectives: List[str]
    estimated_time: int  # seconds
    metadata: Dict[str, Any] = None

@dataclass
class AssessmentSession:
    """Assessment session data."""
    id: str
    user_id: str
    assessment_type: AssessmentType
    topic: str
    questions: List[AssessmentQuestion]
    current_question_index: int
    answers: Dict[str, str]
    start_time: datetime
    time_limit: int  # seconds
    adaptive_parameters: Dict[str, Any]
    is_completed: bool = False

@dataclass
class AssessmentResult:
    """Comprehensive assessment result."""
    session_id: str
    user_id: str
    topic: str
    total_questions: int
    correct_answers: int
    score: float
    time_taken: int  # seconds
    difficulty_progression: List[DifficultyLevel]
    knowledge_gaps: List[str]
    strengths: List[str]
    recommendations: List[str]
    next_steps: List[str]

class AdvancedAssessmentService:
    """Service for advanced assessment and adaptive testing."""
    
    def __init__(self):
        self.question_bank = self._initialize_question_bank()
        self.adaptive_parameters = {
            "initial_difficulty": DifficultyLevel.MEDIUM,
            "difficulty_adjustment": 0.1,
            "confidence_threshold": 0.7,
            "max_questions": 20,
            "min_questions": 5
        }
    
    def _initialize_question_bank(self) -> Dict[str, List[AssessmentQuestion]]:
        """Initialize question bank with Docker and Kubernetes questions."""
        return {
            "docker_basics": [
                AssessmentQuestion(
                    id="docker_001",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    difficulty=DifficultyLevel.EASY,
                    topic="docker_basics",
                    question_text="What is Docker?",
                    options=[
                        "A virtualization platform",
                        "A containerization platform",
                        "A cloud service",
                        "A programming language"
                    ],
                    correct_answer="A containerization platform",
                    explanation="Docker is a containerization platform that allows you to package applications and their dependencies into containers.",
                    learning_objectives=["Understand Docker basics"],
                    estimated_time=30
                ),
                AssessmentQuestion(
                    id="docker_002",
                    question_type=QuestionType.TRUE_FALSE,
                    difficulty=DifficultyLevel.EASY,
                    topic="docker_basics",
                    question_text="Docker containers share the host OS kernel.",
                    options=["True", "False"],
                    correct_answer="True",
                    explanation="Docker containers share the host OS kernel, making them more efficient than virtual machines.",
                    learning_objectives=["Understand container architecture"],
                    estimated_time=20
                )
            ],
            "kubernetes_basics": [
                AssessmentQuestion(
                    id="k8s_001",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    difficulty=DifficultyLevel.MEDIUM,
                    topic="kubernetes_basics",
                    question_text="What is the smallest deployable unit in Kubernetes?",
                    options=["Container", "Pod", "Node", "Service"],
                    correct_answer="Pod",
                    explanation="A Pod is the smallest deployable unit in Kubernetes, which can contain one or more containers.",
                    learning_objectives=["Understand Kubernetes architecture"],
                    estimated_time=45
                ),
                AssessmentQuestion(
                    id="k8s_002",
                    question_type=QuestionType.SCENARIO_BASED,
                    difficulty=DifficultyLevel.HARD,
                    topic="kubernetes_basics",
                    question_text="You need to deploy a web application that requires 3 replicas and should be accessible from outside the cluster. What Kubernetes resources would you create?",
                    options=[
                        "Deployment and Service",
                        "Pod and ConfigMap",
                        "ReplicaSet and Ingress",
                        "StatefulSet and PersistentVolume"
                    ],
                    correct_answer="Deployment and Service",
                    explanation="A Deployment manages the replicas, and a Service exposes the application to external traffic.",
                    learning_objectives=["Understand Kubernetes deployments"],
                    estimated_time=60
                )
            ]
        }
    
    async def create_adaptive_assessment(
        self, 
        user_id: str, 
        topic: str, 
        assessment_type: AssessmentType = AssessmentType.ADAPTIVE
    ) -> Optional[AssessmentSession]:
        """Create an adaptive assessment session."""
        try:
            session_id = f"assessment_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Get user's current knowledge level
            analytics_service = await get_analytics_service()
            progress = await analytics_service.get_user_learning_progress(user_id)
            
            # Determine initial difficulty
            initial_difficulty = self._determine_initial_difficulty(progress)
            
            # Select initial questions
            questions = self._select_adaptive_questions(topic, initial_difficulty, 3)
            
            session = AssessmentSession(
                id=session_id,
                user_id=user_id,
                assessment_type=assessment_type,
                topic=topic,
                questions=questions,
                current_question_index=0,
                answers={},
                start_time=datetime.utcnow(),
                time_limit=1800,  # 30 minutes
                adaptive_parameters={
                    "current_difficulty": initial_difficulty,
                    "confidence_score": 0.5,
                    "questions_answered": 0,
                    "correct_streak": 0,
                    "incorrect_streak": 0
                }
            )
            
            # Store session in database
            await self._store_assessment_session(session)
            
            logger.info(f"Created adaptive assessment {session_id} for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create adaptive assessment: {e}")
            return None
    
    async def submit_answer(
        self, 
        session_id: str, 
        question_id: str, 
        answer: str, 
        time_taken: int
    ) -> Dict[str, Any]:
        """Submit an answer and get adaptive feedback."""
        try:
            # Get session
            session = await self._get_assessment_session(session_id)
            if not session:
                return {"error": "Session not found"}
            
            # Find question
            question = next((q for q in session.questions if q.id == question_id), None)
            if not question:
                return {"error": "Question not found"}
            
            # Record answer
            session.answers[question_id] = answer
            
            # Check if answer is correct
            is_correct = self._evaluate_answer(question, answer)
            
            # Update adaptive parameters
            self._update_adaptive_parameters(session, is_correct, time_taken)
            
            # Determine next question
            next_question = self._select_next_question(session)
            
            # Update session
            session.current_question_index += 1
            await self._update_assessment_session(session)
            
            return {
                "is_correct": is_correct,
                "explanation": question.explanation,
                "next_question": next_question,
                "adaptive_feedback": self._generate_adaptive_feedback(session, is_correct),
                "progress": {
                    "questions_answered": len(session.answers),
                    "total_questions": len(session.questions),
                    "current_difficulty": session.adaptive_parameters["current_difficulty"].value
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to submit answer: {e}")
            return {"error": str(e)}
    
    async def complete_assessment(self, session_id: str) -> Optional[AssessmentResult]:
        """Complete an assessment and generate comprehensive results."""
        try:
            # Get session
            session = await self._get_assessment_session(session_id)
            if not session:
                return None
            
            # Calculate results
            total_questions = len(session.answers)
            correct_answers = sum(1 for q_id, answer in session.answers.items() 
                                if self._evaluate_answer(
                                    next(q for q in session.questions if q.id == q_id), 
                                    answer
                                ))
            
            score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            time_taken = int((datetime.utcnow() - session.start_time).total_seconds())
            
            # Analyze performance
            knowledge_gaps = self._identify_knowledge_gaps(session)
            strengths = self._identify_strengths(session)
            recommendations = self._generate_recommendations(session, score)
            next_steps = self._generate_next_steps(session, score)
            
            # Create result
            result = AssessmentResult(
                session_id=session_id,
                user_id=session.user_id,
                topic=session.topic,
                total_questions=total_questions,
                correct_answers=correct_answers,
                score=score,
                time_taken=time_taken,
                difficulty_progression=[q.difficulty for q in session.questions],
                knowledge_gaps=knowledge_gaps,
                strengths=strengths,
                recommendations=recommendations,
                next_steps=next_steps
            )
            
            # Store result
            await self._store_assessment_result(result)
            
            # Update user progress
            await self._update_user_progress(session.user_id, result)
            
            # Mark session as completed
            session.is_completed = True
            await self._update_assessment_session(session)
            
            logger.info(f"Completed assessment {session_id} with score {score}%")
            return result
            
        except Exception as e:
            logger.error(f"Failed to complete assessment: {e}")
            return None
    
    async def get_peer_review_assessment(self, user_id: str, topic: str) -> Optional[AssessmentSession]:
        """Create a peer review assessment session."""
        try:
            # This would typically involve finding peers and creating collaborative assessments
            # For now, we'll create a standard assessment with peer review elements
            
            session = await self.create_adaptive_assessment(user_id, topic, AssessmentType.PEER_REVIEW)
            if session:
                # Add peer review specific questions
                peer_questions = self._generate_peer_review_questions(topic)
                session.questions.extend(peer_questions)
                
                # Update session
                await self._update_assessment_session(session)
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create peer review assessment: {e}")
            return None
    
    async def get_assessment_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive assessment analytics for a user."""
        try:
            async for db in get_db():
                # Get assessment history
                history_query = await db.execute(
                    "SELECT * FROM assessment_results WHERE user_id = :user_id ORDER BY created_at DESC",
                    {"user_id": user_id}
                )
                assessment_history = history_query.fetchall()
                
                if not assessment_history:
                    return {"message": "No assessment history found"}
                
                # Calculate analytics
                total_assessments = len(assessment_history)
                average_score = sum(row.score for row in assessment_history) / total_assessments
                
                # Performance trends
                recent_scores = [row.score for row in assessment_history[:5]]
                performance_trend = "improving" if len(recent_scores) > 1 and recent_scores[0] > recent_scores[-1] else "stable"
                
                # Topic performance
                topic_performance = {}
                for row in assessment_history:
                    topic = row.topic
                    if topic not in topic_performance:
                        topic_performance[topic] = []
                    topic_performance[topic].append(row.score)
                
                # Calculate average per topic
                topic_averages = {topic: sum(scores) / len(scores) 
                                for topic, scores in topic_performance.items()}
                
                return {
                    "total_assessments": total_assessments,
                    "average_score": round(average_score, 2),
                    "performance_trend": performance_trend,
                    "topic_performance": topic_averages,
                    "recent_scores": recent_scores,
                    "recommendations": self._generate_analytics_recommendations(assessment_history)
                }
                
        except Exception as e:
            logger.error(f"Failed to get assessment analytics: {e}")
            return {"error": str(e)}
    
    def _determine_initial_difficulty(self, progress) -> DifficultyLevel:
        """Determine initial difficulty based on user progress."""
        if not progress:
            return DifficultyLevel.EASY
        
        if progress.completion_percentage > 0.8:
            return DifficultyLevel.HARD
        elif progress.completion_percentage > 0.5:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.EASY
    
    def _select_adaptive_questions(self, topic: str, difficulty: DifficultyLevel, count: int) -> List[AssessmentQuestion]:
        """Select questions for adaptive assessment."""
        topic_questions = self.question_bank.get(topic, [])
        
        # Filter by difficulty
        difficulty_questions = [q for q in topic_questions if q.difficulty == difficulty]
        
        # If not enough questions of this difficulty, include adjacent difficulties
        if len(difficulty_questions) < count:
            all_questions = topic_questions
        else:
            all_questions = difficulty_questions
        
        # Randomly select questions
        return random.sample(all_questions, min(count, len(all_questions)))
    
    def _evaluate_answer(self, question: AssessmentQuestion, answer: str) -> bool:
        """Evaluate if an answer is correct."""
        return answer.strip().lower() == question.correct_answer.strip().lower()
    
    def _update_adaptive_parameters(self, session: AssessmentSession, is_correct: bool, time_taken: int) -> None:
        """Update adaptive parameters based on answer."""
        params = session.adaptive_parameters
        
        if is_correct:
            params["correct_streak"] += 1
            params["incorrect_streak"] = 0
            
            # Increase difficulty if doing well
            if params["correct_streak"] >= 2:
                params["current_difficulty"] = self._increase_difficulty(params["current_difficulty"])
                params["correct_streak"] = 0
        else:
            params["incorrect_streak"] += 1
            params["correct_streak"] = 0
            
            # Decrease difficulty if struggling
            if params["incorrect_streak"] >= 2:
                params["current_difficulty"] = self._decrease_difficulty(params["current_difficulty"])
                params["incorrect_streak"] = 0
        
        # Update confidence score
        total_answered = len(session.answers)
        if total_answered > 0:
            correct_count = sum(1 for q_id, answer in session.answers.items() 
                              if self._evaluate_answer(
                                  next(q for q in session.questions if q.id == q_id), 
                                  answer
                              ))
            params["confidence_score"] = correct_count / total_answered
    
    def _select_next_question(self, session: AssessmentSession) -> Optional[AssessmentQuestion]:
        """Select the next question based on adaptive parameters."""
        # Check if assessment should continue
        if len(session.answers) >= self.adaptive_parameters["max_questions"]:
            return None
        
        if (len(session.answers) >= self.adaptive_parameters["min_questions"] and 
            session.adaptive_parameters["confidence_score"] > self.adaptive_parameters["confidence_threshold"]):
            return None
        
        # Select next question based on current difficulty
        current_difficulty = session.adaptive_parameters["current_difficulty"]
        next_questions = self._select_adaptive_questions(session.topic, current_difficulty, 1)
        
        return next_questions[0] if next_questions else None
    
    def _generate_adaptive_feedback(self, session: AssessmentSession, is_correct: bool) -> str:
        """Generate adaptive feedback based on performance."""
        if is_correct:
            if session.adaptive_parameters["correct_streak"] > 1:
                return "Excellent! You're mastering this topic. The next question will be more challenging."
            else:
                return "Correct! Keep up the good work."
        else:
            if session.adaptive_parameters["incorrect_streak"] > 1:
                return "Don't worry! Let's try an easier question to build your confidence."
            else:
                return "Not quite right. Let's review this concept and try again."
    
    def _identify_knowledge_gaps(self, session: AssessmentSession) -> List[str]:
        """Identify knowledge gaps from assessment."""
        gaps = []
        
        for q_id, answer in session.answers.items():
            question = next(q for q in session.questions if q.id == q_id)
            if not self._evaluate_answer(question, answer):
                gaps.extend(question.learning_objectives)
        
        return list(set(gaps))  # Remove duplicates
    
    def _identify_strengths(self, session: AssessmentSession) -> List[str]:
        """Identify strengths from assessment."""
        strengths = []
        
        for q_id, answer in session.answers.items():
            question = next(q for q in session.questions if q.id == q_id)
            if self._evaluate_answer(question, answer):
                strengths.extend(question.learning_objectives)
        
        return list(set(strengths))  # Remove duplicates
    
    def _generate_recommendations(self, session: AssessmentSession, score: float) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        if score >= 90:
            recommendations.append("Excellent performance! Consider moving to advanced topics.")
        elif score >= 70:
            recommendations.append("Good work! Review the incorrect answers and practice more.")
        elif score >= 50:
            recommendations.append("You're making progress. Focus on the fundamentals before advancing.")
        else:
            recommendations.append("Consider reviewing the basic concepts before retaking the assessment.")
        
        # Add topic-specific recommendations
        knowledge_gaps = self._identify_knowledge_gaps(session)
        if knowledge_gaps:
            recommendations.append(f"Focus on these areas: {', '.join(knowledge_gaps[:3])}")
        
        return recommendations
    
    def _generate_next_steps(self, session: AssessmentSession, score: float) -> List[str]:
        """Generate next steps for learning."""
        next_steps = []
        
        if score >= 80:
            next_steps.append("Proceed to the next topic in your learning path")
            next_steps.append("Try advanced exercises and projects")
        elif score >= 60:
            next_steps.append("Review the lesson materials for this topic")
            next_steps.append("Practice with additional exercises")
        else:
            next_steps.append("Revisit the basic concepts for this topic")
            next_steps.append("Take the assessment again after more study")
        
        return next_steps
    
    def _generate_peer_review_questions(self, topic: str) -> List[AssessmentQuestion]:
        """Generate peer review specific questions."""
        return [
            AssessmentQuestion(
                id=f"peer_review_{topic}_001",
                question_type=QuestionType.CODE_REVIEW,
                difficulty=DifficultyLevel.MEDIUM,
                topic=topic,
                question_text="Review this Dockerfile and identify potential improvements:",
                options=[],
                correct_answer="Review completed",
                explanation="Peer review helps identify best practices and potential issues.",
                learning_objectives=["Code review skills"],
                estimated_time=120
            )
        ]
    
    def _generate_analytics_recommendations(self, assessment_history) -> List[str]:
        """Generate recommendations based on assessment analytics."""
        recommendations = []
        
        if len(assessment_history) < 3:
            recommendations.append("Take more assessments to get better insights into your progress")
        
        recent_scores = [row.score for row in assessment_history[:3]]
        if len(recent_scores) > 1 and recent_scores[0] < recent_scores[-1]:
            recommendations.append("Your performance is improving! Keep up the good work")
        
        return recommendations
    
    def _increase_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """Increase difficulty level."""
        levels = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD, DifficultyLevel.EXPERT]
        current_index = levels.index(current)
        if current_index < len(levels) - 1:
            return levels[current_index + 1]
        return current
    
    def _decrease_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """Decrease difficulty level."""
        levels = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD, DifficultyLevel.EXPERT]
        current_index = levels.index(current)
        if current_index > 0:
            return levels[current_index - 1]
        return current
    
    async def _store_assessment_session(self, session: AssessmentSession) -> None:
        """Store assessment session in database."""
        # This would typically store in a dedicated assessment_sessions table
        logger.info(f"Stored assessment session {session.id}")
    
    async def _get_assessment_session(self, session_id: str) -> Optional[AssessmentSession]:
        """Get assessment session from database."""
        # This would typically retrieve from database
        # For now, return None (would be implemented with actual database storage)
        return None
    
    async def _update_assessment_session(self, session: AssessmentSession) -> None:
        """Update assessment session in database."""
        logger.info(f"Updated assessment session {session.id}")
    
    async def _store_assessment_result(self, result: AssessmentResult) -> None:
        """Store assessment result in database."""
        logger.info(f"Stored assessment result for session {result.session_id}")
    
    async def _update_user_progress(self, user_id: str, result: AssessmentResult) -> None:
        """Update user progress based on assessment result."""
        logger.info(f"Updated progress for user {user_id} based on assessment result")

# Global instance
_advanced_assessment_service = None

async def get_advanced_assessment_service() -> AdvancedAssessmentService:
    """Get global advanced assessment service instance."""
    global _advanced_assessment_service
    if _advanced_assessment_service is None:
        _advanced_assessment_service = AdvancedAssessmentService()
    return _advanced_assessment_service
