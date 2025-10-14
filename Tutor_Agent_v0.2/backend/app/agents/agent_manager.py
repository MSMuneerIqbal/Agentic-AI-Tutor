"""AI Agent Manager for Tutor GPT system - Connects existing agents to frontend."""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import json

from app.core.logging import get_logger
from app.core.session_store import session_store
from app.models.user_mongo import User
from app.models import SessionState

# Import existing agents
from app.agents.orchestrator import OrchestratorAgent
from app.agents.assessment import AssessmentAgent
from app.agents.tutor import TutorAgent
from app.agents.quiz import QuizAgent
from app.agents.feedback import FeedbackAgent

logger = get_logger(__name__)


class AgentManager:
    """Manages AI agent interactions and conversation flow using existing agents."""
    
    def __init__(self):
        # Initialize existing agents
        self.orchestrator = OrchestratorAgent()
        self.assessment = AssessmentAgent()
        self.tutor = TutorAgent()
        self.quiz = QuizAgent()
        self.feedback = FeedbackAgent()
        
        # Agent mapping
        self.agents = {
            "orchestrator": self.orchestrator,
            "assessment": self.assessment,
            "tutor": self.tutor,
            "quiz": self.quiz,
            "feedback": self.feedback,
        }
    
    async def process_message(
        self, 
        user_input: str, 
        session_id: str, 
        user_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process user message and return appropriate agent response."""
        
        # Get or create session state
        session_state = await self._get_session_state(session_id, user_data)
        logger.info(f"Processing message for session {session_id}: '{user_input}', current state: {session_state['current_state']}")
        
        # Determine which agent should handle this message
        agent_type = await self._select_agent(user_input, session_state)
        logger.info(f"Selected agent: {agent_type}")
        
        # Get agent response using existing agents
        agent_response = await self._execute_agent(agent_type, user_input, session_state)
        logger.info(f"Agent response: {agent_response}")
        
        # Update session state
        await self._update_session_state(session_id, user_input, agent_response, session_state)
        
        return {
            "type": "agent_message",
            "agent": agent_type,
            "text": agent_response.get("message", agent_response.get("response", "")),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "conversation_state": session_state["current_state"],
            "metadata": agent_response
        }
    
    async def _get_session_state(self, session_id: str, user_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get or create session state."""
        
        # Try to get existing session
        existing_session = await session_store.get_session(f"session_state:{session_id}")
        
        if existing_session:
            return existing_session
        
        # Create new session state using existing SessionState enum
        session_state = {
            "session_id": session_id,
            "current_state": SessionState.GREETING,
            "user_profile": {
                "learning_style": None,
                "experience_level": None,
                "learning_goals": [],
                "preferred_topics": []
            },
            "conversation_history": [],
            "current_topic": None,
            "progress": {
                "topics_completed": [],
                "quiz_scores": [],
                "time_spent": 0
            },
            "assessment_data": {
                "vark_responses": [],
                "experience_questions": [],
                "completed": False
            },
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # If user data is provided, populate user profile
        if user_data:
            session_state["user_profile"]["name"] = user_data.get("name", "")
            session_state["user_profile"]["email"] = user_data.get("email", "")
        
        return session_state
    
    async def _select_agent(self, user_input: str, session_state: Dict[str, Any]) -> str:
        """Select appropriate agent based on user input and session state."""
        
        current_state = session_state["current_state"]
        user_input_lower = user_input.lower().strip()
        
        # Map SessionState to agent selection
        if current_state == SessionState.GREETING:
            return "orchestrator"
        
        if current_state == SessionState.ASSESSING:
            return "assessment"
        
        if current_state == SessionState.PLANNING:
            return "orchestrator"  # Planning handled by orchestrator
        
        if current_state == SessionState.TUTORING:
            return "tutor"
        
        if current_state == SessionState.QUIZZING:
            return "quiz"
        
        # Handle user input-based routing
        if any(word in user_input_lower for word in ['quiz', 'test', 'practice', 'exercise']):
            return "quiz"
        elif any(word in user_input_lower for word in ['feedback', 'progress', 'how am i doing']):
            return "feedback"
        elif any(word in user_input_lower for word in ['assess', 'assessment', 'learning style']):
            return "assessment"
        elif any(word in user_input_lower for word in ['learn', 'teach', 'explain', 'lesson']):
            return "tutor"
        
        # Default to orchestrator
        return "orchestrator"
    
    async def _execute_agent(self, agent_type: str, user_input: str, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the selected agent with proper context."""
        
        # Prepare context for agent execution
        context = {
            "state": session_state["current_state"],
            "user_profile": session_state["user_profile"],
            "topic": session_state.get("current_topic"),
            "learning_style": session_state["user_profile"].get("learning_style"),
            "progress": session_state.get("progress", {}),
            "session_id": session_state["session_id"],
            "user_id": session_state["user_profile"].get("email"),  # Use email as user_id
            "session_state": session_state["current_state"],
            "answers": session_state.get("assessment_data", {}).get("answers", []),  # For assessment agent
            "vark_responses": session_state.get("assessment_data", {}).get("vark_responses", [])  # For assessment agent
        }
        
        # Execute the appropriate agent
        if agent_type == "orchestrator":
            return await self.orchestrator._execute(user_input, context)
        elif agent_type == "assessment":
            return await self.assessment._execute(user_input, context)
        elif agent_type == "tutor":
            return await self.tutor._execute(user_input, context)
        elif agent_type == "quiz":
            return await self.quiz._execute(user_input, context)
        elif agent_type == "feedback":
            return await self.feedback._execute(user_input, context)
        else:
            # Fallback to orchestrator
            return await self.orchestrator._execute(user_input, context)
    
    async def _update_session_state(
        self, 
        session_id: str, 
        user_input: str, 
        agent_response: Dict[str, Any], 
        session_state: Dict[str, Any]
    ) -> None:
        """Update session state with new conversation data."""
        
        # Update session state if agent returned a next_state
        if "next_state" in agent_response:
            session_state["current_state"] = agent_response["next_state"]
            logger.info(f"Session {session_id} state updated to: {agent_response['next_state']}")
        
        # Update current topic if provided
        if "topic" in agent_response:
            session_state["current_topic"] = agent_response["topic"]
            logger.info(f"Session {session_id} topic updated to: {agent_response['topic']}")
        
        # Add to conversation history
        session_state["conversation_history"].append({
            "user_message": user_input,
            "agent_response": agent_response.get("message", agent_response.get("response", "")),
            "agent_type": agent_response.get("agent", "unknown"),
            "action": agent_response.get("action", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update last activity
        session_state["last_updated"] = datetime.utcnow().isoformat()
        
        # Store updated session state
        await session_store.set_session(f"session_state:{session_id}", session_state, ttl=86400)  # 24 hours