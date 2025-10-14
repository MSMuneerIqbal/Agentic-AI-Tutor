"""
Advanced Analytics Service for Phase 6
Tracks learning progress, performance metrics, and provides insights
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from app.core.database import get_db
from app.models.user import User
from app.models.assessment import AssessmentResult
from app.models.plan import Plan
from app.models.session import Session
from app.models.quiz import QuizAttempt
from app.models.lesson import Lesson
from app.models.feedback import Feedback

logger = logging.getLogger(__name__)

class LearningProgressLevel(Enum):
    """Learning progress levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class LearningProgress:
    """Learning progress data."""
    user_id: str
    current_level: LearningProgressLevel
    topics_completed: int
    total_topics: int
    completion_percentage: float
    average_quiz_score: float
    total_study_time: int  # minutes
    learning_streak: int  # days
    last_activity: datetime

@dataclass
class PerformanceMetrics:
    """Performance metrics for a user."""
    user_id: str
    quiz_scores: List[float]
    lesson_completion_rate: float
    average_session_duration: float
    topic_mastery: Dict[str, float]
    learning_velocity: float
    retention_rate: float

@dataclass
class SystemAnalytics:
    """System-wide analytics."""
    total_users: int
    active_users: int
    total_sessions: int
    average_session_duration: float
    popular_topics: List[Tuple[str, int]]
    learning_style_distribution: Dict[str, int]
    system_engagement: float

class AnalyticsService:
    """Service for learning analytics and progress tracking."""
    
    def __init__(self):
        self.progress_thresholds = {
            LearningProgressLevel.BEGINNER: 0.0,
            LearningProgressLevel.INTERMEDIATE: 0.3,
            LearningProgressLevel.ADVANCED: 0.6,
            LearningProgressLevel.EXPERT: 0.9
        }
    
    async def get_user_learning_progress(self, user_id: str) -> Optional[LearningProgress]:
        """Get comprehensive learning progress for a user."""
        try:
            async for db in get_db():
                # Get user's study plan
                plan_query = await db.execute(
                    "SELECT * FROM plans WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1",
                    {"user_id": user_id}
                )
                plan_data = plan_query.fetchone()
                
                if not plan_data:
                    return None
                
                total_topics = len(plan_data.topics) if plan_data.topics else 0
                
                # Get completed lessons
                lessons_query = await db.execute(
                    "SELECT COUNT(*) FROM lessons WHERE user_id = :user_id AND completed = true",
                    {"user_id": user_id}
                )
                topics_completed = lessons_query.scalar() or 0
                
                # Get quiz scores
                quiz_query = await db.execute(
                    "SELECT score FROM quiz_results WHERE user_id = :user_id",
                    {"user_id": user_id}
                )
                quiz_scores = [row[0] for row in quiz_query.fetchall()]
                average_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0.0
                
                # Get total study time
                time_query = await db.execute(
                    "SELECT SUM(duration_minutes) FROM lessons WHERE user_id = :user_id",
                    {"user_id": user_id}
                )
                total_study_time = time_query.scalar() or 0
                
                # Get learning streak
                streak_query = await db.execute(
                    "SELECT COUNT(DISTINCT DATE(created_at)) FROM lessons WHERE user_id = :user_id AND created_at >= :week_ago",
                    {"user_id": user_id, "week_ago": datetime.utcnow() - timedelta(days=7)}
                )
                learning_streak = streak_query.scalar() or 0
                
                # Get last activity
                activity_query = await db.execute(
                    "SELECT MAX(created_at) FROM lessons WHERE user_id = :user_id",
                    {"user_id": user_id}
                )
                last_activity = activity_query.scalar() or datetime.utcnow()
                
                # Calculate completion percentage
                completion_percentage = (topics_completed / total_topics) if total_topics > 0 else 0.0
                
                # Determine current level
                current_level = self._determine_learning_level(completion_percentage, average_quiz_score)
                
                return LearningProgress(
                    user_id=user_id,
                    current_level=current_level,
                    topics_completed=topics_completed,
                    total_topics=total_topics,
                    completion_percentage=completion_percentage,
                    average_quiz_score=average_quiz_score,
                    total_study_time=total_study_time,
                    learning_streak=learning_streak,
                    last_activity=last_activity
                )
                
        except Exception as e:
            logger.error(f"Failed to get learning progress: {e}")
            return None
    
    async def get_user_performance_metrics(self, user_id: str) -> Optional[PerformanceMetrics]:
        """Get detailed performance metrics for a user."""
        try:
            async for db in get_db():
                # Get quiz scores
                quiz_query = await db.execute(
                    "SELECT score FROM quiz_results WHERE user_id = :user_id",
                    {"user_id": user_id}
                )
                quiz_scores = [row[0] for row in quiz_query.fetchall()]
                
                # Get lesson completion rate
                lessons_query = await db.execute(
                    "SELECT COUNT(*) as total, SUM(CASE WHEN completed = true THEN 1 ELSE 0 END) as completed FROM lessons WHERE user_id = :user_id",
                    {"user_id": user_id}
                )
                lesson_data = lessons_query.fetchone()
                total_lessons = lesson_data[0] if lesson_data[0] else 0
                completed_lessons = lesson_data[1] if lesson_data[1] else 0
                completion_rate = (completed_lessons / total_lessons) if total_lessons > 0 else 0.0
                
                # Get average session duration
                session_query = await db.execute(
                    "SELECT AVG(duration_minutes) FROM lessons WHERE user_id = :user_id",
                    {"user_id": user_id}
                )
                average_session_duration = session_query.scalar() or 0.0
                
                # Get topic mastery
                topic_query = await db.execute(
                    "SELECT topic, AVG(feedback_score) FROM lessons WHERE user_id = :user_id GROUP BY topic",
                    {"user_id": user_id}
                )
                topic_mastery = {row[0]: row[1] for row in topic_query.fetchall()}
                
                # Calculate learning velocity (topics per week)
                velocity_query = await db.execute(
                    "SELECT COUNT(*) FROM lessons WHERE user_id = :user_id AND created_at >= :week_ago",
                    {"user_id": user_id, "week_ago": datetime.utcnow() - timedelta(days=7)}
                )
                weekly_progress = velocity_query.scalar() or 0
                learning_velocity = weekly_progress / 7.0  # topics per day
                
                # Calculate retention rate (based on quiz performance over time)
                retention_query = await db.execute(
                    "SELECT AVG(score) FROM quiz_results WHERE user_id = :user_id AND created_at >= :month_ago",
                    {"user_id": user_id, "month_ago": datetime.utcnow() - timedelta(days=30)}
                )
                retention_rate = retention_query.scalar() or 0.0
                
                return PerformanceMetrics(
                    user_id=user_id,
                    quiz_scores=quiz_scores,
                    lesson_completion_rate=completion_rate,
                    average_session_duration=average_session_duration,
                    topic_mastery=topic_mastery,
                    learning_velocity=learning_velocity,
                    retention_rate=retention_rate
                )
                
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return None
    
    async def get_system_analytics(self) -> SystemAnalytics:
        """Get system-wide analytics."""
        try:
            async for db in get_db():
                # Get total users
                users_query = await db.execute("SELECT COUNT(*) FROM users")
                total_users = users_query.scalar() or 0
                
                # Get active users (users with activity in last 7 days)
                active_query = await db.execute(
                    "SELECT COUNT(DISTINCT user_id) FROM lessons WHERE created_at >= :week_ago",
                    {"week_ago": datetime.utcnow() - timedelta(days=7)}
                )
                active_users = active_query.scalar() or 0
                
                # Get total sessions
                sessions_query = await db.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = sessions_query.scalar() or 0
                
                # Get average session duration
                duration_query = await db.execute("SELECT AVG(duration_minutes) FROM lessons")
                average_session_duration = duration_query.scalar() or 0.0
                
                # Get popular topics
                topics_query = await db.execute(
                    "SELECT topic, COUNT(*) as count FROM lessons GROUP BY topic ORDER BY count DESC LIMIT 10"
                )
                popular_topics = [(row[0], row[1]) for row in topics_query.fetchall()]
                
                # Get learning style distribution
                style_query = await db.execute(
                    "SELECT style, COUNT(*) FROM assessment_results GROUP BY style"
                )
                learning_style_distribution = {row[0]: row[1] for row in style_query.fetchall()}
                
                # Calculate system engagement (active users / total users)
                system_engagement = (active_users / total_users) if total_users > 0 else 0.0
                
                return SystemAnalytics(
                    total_users=total_users,
                    active_users=active_users,
                    total_sessions=total_sessions,
                    average_session_duration=average_session_duration,
                    popular_topics=popular_topics,
                    learning_style_distribution=learning_style_distribution,
                    system_engagement=system_engagement
                )
                
        except Exception as e:
            logger.error(f"Failed to get system analytics: {e}")
            return SystemAnalytics(0, 0, 0, 0.0, [], {}, 0.0)
    
    async def get_learning_insights(self, user_id: str) -> Dict[str, Any]:
        """Get personalized learning insights for a user."""
        try:
            progress = await self.get_user_learning_progress(user_id)
            metrics = await self.get_user_performance_metrics(user_id)
            
            if not progress or not metrics:
                return {}
            
            insights = {
                "current_level": progress.current_level.value,
                "completion_percentage": progress.completion_percentage,
                "learning_streak": progress.learning_streak,
                "average_quiz_score": progress.average_quiz_score,
                "total_study_time": progress.total_study_time,
                "learning_velocity": metrics.learning_velocity,
                "retention_rate": metrics.retention_rate,
                "topic_mastery": metrics.topic_mastery,
                "recommendations": self._generate_recommendations(progress, metrics)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            return {}
    
    async def track_learning_event(self, user_id: str, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Track a learning event for analytics."""
        try:
            # This would typically store events in a dedicated analytics table
            # For now, we'll log the event
            logger.info(f"Learning event: {event_type} for user {user_id}: {event_data}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track learning event: {e}")
            return False
    
    def _determine_learning_level(self, completion_percentage: float, average_quiz_score: float) -> LearningProgressLevel:
        """Determine learning level based on progress and performance."""
        # Weighted score: 70% completion, 30% quiz performance
        weighted_score = (completion_percentage * 0.7) + ((average_quiz_score / 100) * 0.3)
        
        if weighted_score >= self.progress_thresholds[LearningProgressLevel.EXPERT]:
            return LearningProgressLevel.EXPERT
        elif weighted_score >= self.progress_thresholds[LearningProgressLevel.ADVANCED]:
            return LearningProgressLevel.ADVANCED
        elif weighted_score >= self.progress_thresholds[LearningProgressLevel.INTERMEDIATE]:
            return LearningProgressLevel.INTERMEDIATE
        else:
            return LearningProgressLevel.BEGINNER
    
    def _generate_recommendations(self, progress: LearningProgress, metrics: PerformanceMetrics) -> List[str]:
        """Generate personalized learning recommendations."""
        recommendations = []
        
        if progress.completion_percentage < 0.3:
            recommendations.append("Focus on completing more lessons to build foundational knowledge")
        
        if progress.average_quiz_score < 70:
            recommendations.append("Review previous lessons and retake quizzes to improve understanding")
        
        if progress.learning_streak < 3:
            recommendations.append("Try to maintain a consistent learning schedule for better retention")
        
        if metrics.learning_velocity < 0.5:
            recommendations.append("Consider increasing your study frequency to accelerate progress")
        
        if metrics.retention_rate < 80:
            recommendations.append("Practice spaced repetition to improve long-term retention")
        
        # Topic-specific recommendations
        for topic, mastery in metrics.topic_mastery.items():
            if mastery < 3.0:
                recommendations.append(f"Review {topic} content to improve mastery")
        
        return recommendations

# Global instance
_analytics_service = None

async def get_analytics_service() -> AnalyticsService:
    """Get global analytics service instance."""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
