"""
Adaptive Learning Service for Phase 6
Provides intelligent learning path customization and adaptive content delivery
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
from app.models.quiz import QuizAttempt
from app.models.lesson import Lesson
from app.services.analytics_service import get_analytics_service, LearningProgressLevel

logger = logging.getLogger(__name__)

class DifficultyLevel(Enum):
    """Difficulty levels for content."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class ContentType(Enum):
    """Types of learning content."""
    THEORETICAL = "theoretical"
    PRACTICAL = "practical"
    INTERACTIVE = "interactive"
    ASSESSMENT = "assessment"

@dataclass
class LearningObjective:
    """Learning objective definition."""
    id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    content_type: ContentType
    prerequisites: List[str]
    estimated_time: int  # minutes
    learning_outcomes: List[str]

@dataclass
class AdaptivePath:
    """Adaptive learning path."""
    user_id: str
    current_objective: str
    path_sequence: List[str]
    difficulty_progression: List[DifficultyLevel]
    content_adaptations: Dict[str, Any]
    estimated_completion: datetime
    success_probability: float

@dataclass
class LearningRecommendation:
    """Personalized learning recommendation."""
    objective_id: str
    reason: str
    priority: int  # 1-10
    estimated_benefit: float
    content_suggestions: List[str]

class AdaptiveLearningService:
    """Service for adaptive learning and personalized content delivery."""
    
    def __init__(self):
        self.learning_objectives = self._initialize_learning_objectives()
        self.difficulty_thresholds = {
            DifficultyLevel.EASY: 0.8,
            DifficultyLevel.MEDIUM: 0.6,
            DifficultyLevel.HARD: 0.4,
            DifficultyLevel.EXPERT: 0.2
        }
    
    def _initialize_learning_objectives(self) -> Dict[str, LearningObjective]:
        """Initialize learning objectives for Docker and Kubernetes."""
        return {
            "docker_basics": LearningObjective(
                id="docker_basics",
                title="Docker Fundamentals",
                description="Understand Docker containers and images",
                difficulty=DifficultyLevel.EASY,
                content_type=ContentType.THEORETICAL,
                prerequisites=[],
                estimated_time=30,
                learning_outcomes=["Understand containers", "Create Docker images", "Run containers"]
            ),
            "docker_practice": LearningObjective(
                id="docker_practice",
                title="Docker Hands-on Practice",
                description="Practice Docker commands and workflows",
                difficulty=DifficultyLevel.MEDIUM,
                content_type=ContentType.PRACTICAL,
                prerequisites=["docker_basics"],
                estimated_time=45,
                learning_outcomes=["Master Docker commands", "Build applications", "Manage containers"]
            ),
            "kubernetes_basics": LearningObjective(
                id="kubernetes_basics",
                title="Kubernetes Fundamentals",
                description="Understand Kubernetes architecture and concepts",
                difficulty=DifficultyLevel.MEDIUM,
                content_type=ContentType.THEORETICAL,
                prerequisites=["docker_basics"],
                estimated_time=40,
                learning_outcomes=["Understand pods", "Create deployments", "Manage services"]
            ),
            "kubernetes_practice": LearningObjective(
                id="kubernetes_practice",
                title="Kubernetes Hands-on Practice",
                description="Practice Kubernetes deployments and management",
                difficulty=DifficultyLevel.HARD,
                content_type=ContentType.PRACTICAL,
                prerequisites=["kubernetes_basics", "docker_practice"],
                estimated_time=60,
                learning_outcomes=["Deploy applications", "Scale services", "Manage clusters"]
            ),
            "advanced_orchestration": LearningObjective(
                id="advanced_orchestration",
                title="Advanced Container Orchestration",
                description="Master advanced Kubernetes features",
                difficulty=DifficultyLevel.EXPERT,
                content_type=ContentType.INTERACTIVE,
                prerequisites=["kubernetes_practice"],
                estimated_time=90,
                learning_outcomes=["Advanced deployments", "Service mesh", "Monitoring"]
            )
        }
    
    async def create_adaptive_path(self, user_id: str) -> Optional[AdaptivePath]:
        """Create an adaptive learning path for a user."""
        try:
            analytics_service = await get_analytics_service()
            progress = await analytics_service.get_user_learning_progress(user_id)
            metrics = await analytics_service.get_user_performance_metrics(user_id)
            
            if not progress or not metrics:
                return None
            
            # Determine starting point based on progress
            current_objective = self._determine_current_objective(progress, metrics)
            
            # Generate path sequence
            path_sequence = self._generate_path_sequence(current_objective, progress, metrics)
            
            # Determine difficulty progression
            difficulty_progression = self._determine_difficulty_progression(progress, metrics)
            
            # Generate content adaptations
            content_adaptations = self._generate_content_adaptations(progress, metrics)
            
            # Estimate completion time
            estimated_completion = self._estimate_completion_time(path_sequence, progress)
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(progress, metrics, path_sequence)
            
            return AdaptivePath(
                user_id=user_id,
                current_objective=current_objective,
                path_sequence=path_sequence,
                difficulty_progression=difficulty_progression,
                content_adaptations=content_adaptations,
                estimated_completion=estimated_completion,
                success_probability=success_probability
            )
            
        except Exception as e:
            logger.error(f"Failed to create adaptive path: {e}")
            return None
    
    async def get_learning_recommendations(self, user_id: str) -> List[LearningRecommendation]:
        """Get personalized learning recommendations."""
        try:
            analytics_service = await get_analytics_service()
            progress = await analytics_service.get_user_learning_progress(user_id)
            metrics = await analytics_service.get_user_performance_metrics(user_id)
            
            if not progress or not metrics:
                return []
            
            recommendations = []
            
            # Analyze current progress and identify gaps
            for objective_id, objective in self.learning_objectives.items():
                recommendation = self._analyze_objective(objective, progress, metrics)
                if recommendation:
                    recommendations.append(recommendation)
            
            # Sort by priority
            recommendations.sort(key=lambda x: x.priority, reverse=True)
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to get learning recommendations: {e}")
            return []
    
    async def adapt_content_difficulty(self, user_id: str, objective_id: str, current_difficulty: DifficultyLevel) -> DifficultyLevel:
        """Adapt content difficulty based on user performance."""
        try:
            analytics_service = await get_analytics_service()
            metrics = await analytics_service.get_user_performance_metrics(user_id)
            
            if not metrics:
                return current_difficulty
            
            # Get recent performance for this objective
            recent_performance = self._get_recent_performance(user_id, objective_id)
            
            if recent_performance is None:
                return current_difficulty
            
            # Adjust difficulty based on performance
            if recent_performance > 0.8:
                # High performance - increase difficulty
                return self._increase_difficulty(current_difficulty)
            elif recent_performance < 0.5:
                # Low performance - decrease difficulty
                return self._decrease_difficulty(current_difficulty)
            else:
                # Moderate performance - maintain difficulty
                return current_difficulty
                
        except Exception as e:
            logger.error(f"Failed to adapt content difficulty: {e}")
            return current_difficulty
    
    async def personalize_content_delivery(self, user_id: str, objective_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Personalize content delivery based on user preferences and performance."""
        try:
            analytics_service = await get_analytics_service()
            progress = await analytics_service.get_user_learning_progress(user_id)
            
            if not progress:
                return content
            
            # Get user's learning style
            learning_style = progress.learning_style if hasattr(progress, 'learning_style') else 'V'
            
            # Adapt content based on learning style
            adapted_content = self._adapt_content_for_learning_style(content, learning_style)
            
            # Adjust content complexity based on progress level
            adapted_content = self._adjust_content_complexity(adapted_content, progress.current_level)
            
            # Add personalized examples and explanations
            adapted_content = self._add_personalized_examples(adapted_content, user_id, objective_id)
            
            return adapted_content
            
        except Exception as e:
            logger.error(f"Failed to personalize content delivery: {e}")
            return content
    
    async def track_learning_progress(self, user_id: str, objective_id: str, performance: float) -> bool:
        """Track learning progress for adaptive adjustments."""
        try:
            # Store performance data for future analysis
            async for db in get_db():
                # This would typically store in a learning_progress table
                # For now, we'll log the progress
                logger.info(f"Learning progress: User {user_id}, Objective {objective_id}, Performance {performance}")
                break
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track learning progress: {e}")
            return False
    
    def _determine_current_objective(self, progress, metrics) -> str:
        """Determine the current learning objective based on progress."""
        if progress.completion_percentage < 0.2:
            return "docker_basics"
        elif progress.completion_percentage < 0.4:
            return "docker_practice"
        elif progress.completion_percentage < 0.6:
            return "kubernetes_basics"
        elif progress.completion_percentage < 0.8:
            return "kubernetes_practice"
        else:
            return "advanced_orchestration"
    
    def _generate_path_sequence(self, current_objective: str, progress, metrics) -> List[str]:
        """Generate optimal learning path sequence."""
        # Start with current objective
        sequence = [current_objective]
        
        # Add remaining objectives based on prerequisites and performance
        remaining_objectives = [obj_id for obj_id in self.learning_objectives.keys() if obj_id != current_objective]
        
        # Sort by prerequisites and estimated benefit
        for obj_id in remaining_objectives:
            objective = self.learning_objectives[obj_id]
            if self._can_access_objective(objective, sequence):
                sequence.append(obj_id)
        
        return sequence
    
    def _determine_difficulty_progression(self, progress, metrics) -> List[DifficultyLevel]:
        """Determine difficulty progression based on user performance."""
        if progress.current_level == LearningProgressLevel.BEGINNER:
            return [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
        elif progress.current_level == LearningProgressLevel.INTERMEDIATE:
            return [DifficultyLevel.MEDIUM, DifficultyLevel.HARD, DifficultyLevel.EXPERT]
        else:
            return [DifficultyLevel.HARD, DifficultyLevel.EXPERT]
    
    def _generate_content_adaptations(self, progress, metrics) -> Dict[str, Any]:
        """Generate content adaptations based on user profile."""
        adaptations = {
            "learning_style": progress.learning_style if hasattr(progress, 'learning_style') else 'V',
            "preferred_content_type": self._determine_preferred_content_type(metrics),
            "difficulty_preference": self._determine_difficulty_preference(metrics),
            "pace_adjustment": self._determine_pace_adjustment(metrics),
            "example_complexity": self._determine_example_complexity(progress)
        }
        return adaptations
    
    def _estimate_completion_time(self, path_sequence: List[str], progress) -> datetime:
        """Estimate completion time for the learning path."""
        total_time = sum(self.learning_objectives[obj_id].estimated_time for obj_id in path_sequence)
        
        # Adjust based on user's learning velocity
        if hasattr(progress, 'learning_velocity') and progress.learning_velocity > 0:
            adjusted_time = total_time / progress.learning_velocity
        else:
            adjusted_time = total_time
        
        return datetime.utcnow() + timedelta(minutes=adjusted_time)
    
    def _calculate_success_probability(self, progress, metrics, path_sequence: List[str]) -> float:
        """Calculate probability of successful completion."""
        base_probability = 0.7  # Base success rate
        
        # Adjust based on current performance
        if metrics.average_quiz_score > 80:
            base_probability += 0.2
        elif metrics.average_quiz_score < 60:
            base_probability -= 0.2
        
        # Adjust based on learning streak
        if hasattr(progress, 'learning_streak') and progress.learning_streak > 5:
            base_probability += 0.1
        
        # Adjust based on path complexity
        complex_objectives = sum(1 for obj_id in path_sequence if self.learning_objectives[obj_id].difficulty in [DifficultyLevel.HARD, DifficultyLevel.EXPERT])
        if complex_objectives > 2:
            base_probability -= 0.1
        
        return max(0.1, min(0.95, base_probability))
    
    def _analyze_objective(self, objective: LearningObjective, progress, metrics) -> Optional[LearningRecommendation]:
        """Analyze if an objective should be recommended."""
        # Check if user can access this objective
        if not self._can_access_objective(objective, []):
            return None
        
        # Calculate priority based on various factors
        priority = 5  # Base priority
        
        # Increase priority if it's a prerequisite for advanced topics
        if objective.difficulty == DifficultyLevel.EASY:
            priority += 2
        
        # Increase priority if user is struggling with current level
        if progress.completion_percentage < 0.3 and objective.difficulty == DifficultyLevel.EASY:
            priority += 3
        
        # Increase priority if it matches user's learning style
        if objective.content_type == ContentType.PRACTICAL and metrics.learning_velocity > 1.0:
            priority += 1
        
        if priority >= 6:  # Only recommend high-priority objectives
            return LearningRecommendation(
                objective_id=objective.id,
                reason=f"Recommended based on your learning progress and {objective.difficulty.value} difficulty level",
                priority=priority,
                estimated_benefit=0.8,
                content_suggestions=[f"Focus on {objective.title} to build foundational knowledge"]
            )
        
        return None
    
    def _can_access_objective(self, objective: LearningObjective, completed_sequence: List[str]) -> bool:
        """Check if user can access an objective based on prerequisites."""
        return all(prereq in completed_sequence for prereq in objective.prerequisites)
    
    def _get_recent_performance(self, user_id: str, objective_id: str) -> Optional[float]:
        """Get recent performance for a specific objective."""
        # This would typically query the database for recent quiz/lesson performance
        # For now, return a mock value
        return 0.7
    
    def _increase_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """Increase difficulty level."""
        difficulty_order = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD, DifficultyLevel.EXPERT]
        current_index = difficulty_order.index(current)
        if current_index < len(difficulty_order) - 1:
            return difficulty_order[current_index + 1]
        return current
    
    def _decrease_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """Decrease difficulty level."""
        difficulty_order = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD, DifficultyLevel.EXPERT]
        current_index = difficulty_order.index(current)
        if current_index > 0:
            return difficulty_order[current_index - 1]
        return current
    
    def _adapt_content_for_learning_style(self, content: Dict[str, Any], learning_style: str) -> Dict[str, Any]:
        """Adapt content based on learning style."""
        adapted_content = content.copy()
        
        if learning_style == 'V':  # Visual
            adapted_content['visual_elements'] = True
            adapted_content['diagrams'] = True
        elif learning_style == 'A':  # Auditory
            adapted_content['audio_explanations'] = True
            adapted_content['discussions'] = True
        elif learning_style == 'R':  # Reading/Writing
            adapted_content['detailed_text'] = True
            adapted_content['note_taking'] = True
        elif learning_style == 'K':  # Kinesthetic
            adapted_content['hands_on_exercises'] = True
            adapted_content['practical_examples'] = True
        
        return adapted_content
    
    def _adjust_content_complexity(self, content: Dict[str, Any], level: LearningProgressLevel) -> Dict[str, Any]:
        """Adjust content complexity based on learning level."""
        adapted_content = content.copy()
        
        if level == LearningProgressLevel.BEGINNER:
            adapted_content['simplified_explanations'] = True
            adapted_content['step_by_step'] = True
        elif level == LearningProgressLevel.EXPERT:
            adapted_content['advanced_concepts'] = True
            adapted_content['deep_dives'] = True
        
        return adapted_content
    
    def _add_personalized_examples(self, content: Dict[str, Any], user_id: str, objective_id: str) -> Dict[str, Any]:
        """Add personalized examples based on user context."""
        adapted_content = content.copy()
        
        # Add personalized examples based on objective
        if objective_id == "docker_basics":
            adapted_content['examples'] = ["Simple web application", "Database container", "Development environment"]
        elif objective_id == "kubernetes_basics":
            adapted_content['examples'] = ["Multi-tier application", "Microservices deployment", "Scaling web services"]
        
        return adapted_content
    
    def _determine_preferred_content_type(self, metrics) -> ContentType:
        """Determine preferred content type based on performance."""
        if metrics.lesson_completion_rate > 0.8:
            return ContentType.PRACTICAL
        else:
            return ContentType.THEORETICAL
    
    def _determine_difficulty_preference(self, metrics) -> DifficultyLevel:
        """Determine difficulty preference based on performance."""
        if metrics.average_quiz_score > 85:
            return DifficultyLevel.HARD
        elif metrics.average_quiz_score > 70:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.EASY
    
    def _determine_pace_adjustment(self, metrics) -> float:
        """Determine pace adjustment factor."""
        if metrics.learning_velocity > 1.5:
            return 1.2  # Faster pace
        elif metrics.learning_velocity < 0.5:
            return 0.8  # Slower pace
        else:
            return 1.0  # Normal pace
    
    def _determine_example_complexity(self, progress) -> str:
        """Determine example complexity based on progress."""
        if progress.current_level == LearningProgressLevel.BEGINNER:
            return "simple"
        elif progress.current_level == LearningProgressLevel.INTERMEDIATE:
            return "moderate"
        else:
            return "complex"

# Global instance
_adaptive_learning_service = None

async def get_adaptive_learning_service() -> AdaptiveLearningService:
    """Get global adaptive learning service instance."""
    global _adaptive_learning_service
    if _adaptive_learning_service is None:
        _adaptive_learning_service = AdaptiveLearningService()
    return _adaptive_learning_service
