"""Runner service for orchestrating agent interactions."""

import json
import uuid
from datetime import datetime
from typing import Any

from app.agents.assessment import AssessmentAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.planning import PlanningAgent
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.core.redis import redis_client
from app.models.session import SessionState
from app.services.directive_service import directive_service

logger = get_logger(__name__)
metrics = get_metrics_collector()


class Runner:
    """
    Runner service that orchestrates agent interactions.
    
    Implements the two-stage runner pattern:
    1. FIRST RUNNER: Backend-initiated greeting
    2. SECOND RUNNER: User input loop
    """

    def __init__(self):
        """Initialize Runner with Orchestrator, Assessment, and Planning Agents."""
        self.orchestrator = OrchestratorAgent()
        self.assessment = AssessmentAgent()
        self.planning = PlanningAgent()

    async def run_first_runner(self, session_id: str) -> dict[str, Any]:
        """
        Execute FIRST RUNNER - backend-initiated greeting.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Greeting message and context
        """
        try:
            # Get session context from Redis
            session_context = await self._get_session_context(session_id)
            
            # Execute orchestrator with "hello" trigger
            result = await self.orchestrator.run("hello", session_context)
            
            # Update session state if needed
            if "next_state" in result:
                await self._update_session_state(session_id, result["next_state"])
            
            # Persist greeting directive
            async for db in get_db():
                await directive_service.create_greeting_directive(
                    session_id=session_id,
                    greeting_message=result.get("message", "Hello! Ready to begin?"),
                    db=db,
                )
                break
            
            # Create greeting message
            greeting = {
                "type": "agent_message",
                "agent": result.get("agent", "orchestrator"),
                "text": result.get("message", "Hello! Ready to begin?"),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "session_id": session_id,
                "action": result.get("action", "continue"),
            }
            
            # Log greeting sent
            logger.info(
                f"FIRST RUNNER greeting sent",
                extra={
                    "session_id": session_id,
                    "agent": result.get("agent"),
                    "action": result.get("action"),
                },
            )
            
            return greeting
            
        except Exception as e:
            logger.error(
                f"FIRST RUNNER failed: {str(e)}",
                extra={"session_id": session_id, "error": str(e)},
            )
            
            # Return fallback greeting
            return {
                "type": "agent_message",
                "agent": "orchestrator",
                "text": "Hello! I'm your AI tutor. Ready to begin your learning journey?",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "session_id": session_id,
                "action": "continue",
                "error": "fallback_greeting",
            }

    async def run_second_runner(
        self, session_id: str, user_input: str
    ) -> dict[str, Any]:
        """
        Execute SECOND RUNNER - process user input.
        
        Args:
            session_id: Session identifier
            user_input: User message
            
        Returns:
            Agent response
        """
        try:
            # Get session context
            session_context = await self._get_session_context(session_id)
            
            # Route to appropriate agent based on session state
            session_state = session_context.get("state", SessionState.GREETING)
            
            if session_state == SessionState.ASSESSING:
                # Route to Assessment Agent
                result = await self.assessment.run(user_input, session_context)
            elif session_state == SessionState.PLANNING:
                # Route to Planning Agent
                result = await self.planning.run(user_input, session_context)
            else:
                # Route to Orchestrator Agent
                result = await self.orchestrator.run(user_input, session_context)
            
            # Update session state if needed
            if "next_state" in result:
                next_state = result["next_state"]
                if isinstance(next_state, str):
                    # Convert string to SessionState enum
                    try:
                        next_state = SessionState(next_state)
                    except ValueError:
                        logger.warning(f"Invalid state transition: {next_state}")
                        next_state = SessionState.TUTORING  # Default fallback
                
                await self._update_session_state(session_id, next_state)
                
                # Create state transition directive
                if session_state != next_state:
                    async for db in get_db():
                        await directive_service.create_state_transition_directive(
                            session_id=session_id,
                            from_state=session_state.value,
                            to_state=next_state.value,
                            reason=f"Agent action: {result.get('action', 'unknown')}",
                            db=db,
                        )
                        break
            
            # Persist user input and agent response directives
            async for db in get_db():
                await directive_service.create_user_input_directive(
                    session_id=session_id,
                    user_input=user_input,
                    db=db,
                )
                await directive_service.create_agent_response_directive(
                    session_id=session_id,
                    agent_name=result.get("agent", "orchestrator"),
                    response_message=result.get("message", "I understand. Let me help you with that."),
                    action=result.get("action"),
                    db=db,
                )
                break
            
            # Create response message
            response = {
                "type": "agent_message",
                "agent": result.get("agent", "orchestrator"),
                "text": result.get("message", "I understand. Let me help you with that."),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "session_id": session_id,
                "action": result.get("action", "continue"),
            }
            
            # Log response sent
            logger.info(
                f"SECOND RUNNER response sent",
                extra={
                    "session_id": session_id,
                    "agent": result.get("agent"),
                    "action": result.get("action"),
                    "user_input_length": len(user_input),
                },
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"SECOND RUNNER failed: {str(e)}",
                extra={"session_id": session_id, "error": str(e)},
            )
            
            # Return error response
            return {
                "type": "error",
                "message": "I encountered an issue processing your request. Please try again.",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "session_id": session_id,
            }

    async def _get_session_context(self, session_id: str) -> dict[str, Any]:
        """Get session context from Redis."""
        try:
            session_data_str = await redis_client.get(f"session:{session_id}")
            if session_data_str:
                session_data = json.loads(session_data_str)
                return {
                    "session_id": session_id,
                    "state": SessionState(session_data.get("state", "greeting")),
                    "user_id": session_data.get("user_id"),
                    "last_checkpoint": session_data.get("last_checkpoint"),
                }
        except Exception as e:
            logger.warning(f"Failed to get session context: {e}")
        
        # Return default context
        return {
            "session_id": session_id,
            "state": SessionState.GREETING,
            "user_id": None,
            "last_checkpoint": None,
        }

    async def _update_session_state(
        self, session_id: str, new_state: SessionState
    ) -> None:
        """Update session state in Redis."""
        try:
            # Get current session data
            session_data_str = await redis_client.get(f"session:{session_id}")
            if session_data_str:
                session_data = json.loads(session_data_str)
                # Update state
                session_data["state"] = new_state.value
                session_data["last_checkpoint"] = f"state_changed_to_{new_state.value}"
                session_data["updated_at"] = datetime.utcnow().isoformat()
                
                # Save back to Redis
                await redis_client.setex(
                    f"session:{session_id}",
                    86400,  # 24 hours TTL
                    json.dumps(session_data),
                )
                
                logger.debug(f"Updated session state: {session_id} -> {new_state.value}")
                
        except Exception as e:
            logger.warning(f"Failed to update session state: {e}")


# Global runner instance
runner = Runner()
