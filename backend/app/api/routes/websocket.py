"""WebSocket endpoint for agent interactions."""

import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logging import get_logger
from app.core.session_store import session_store
from app.agents.agent_manager import AgentManager

logger = get_logger(__name__)

router = APIRouter()
agent_manager = AgentManager()


async def get_user_data_from_session(session_id: str) -> dict:
    """Extract user data from session for agent context."""
    try:
        # Try to get user data from session store
        user_data = await session_store.get_session(f"user_data:{session_id}")
        if user_data:
            return user_data
    except Exception as e:
        logger.warning(f"Could not retrieve user data for session {session_id}: {e}")
    
    # Return default user data
    return {"name": "Student", "email": "student@example.com"}


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time agent communication.

    Flow:
    1. Client connects with session_id
    2. Get user data and initialize agent manager
    3. Send personalized greeting based on user state
    4. Loop: receive user message → agent manager processes → send response
    """
    await websocket.accept()
    
    # Track active session using MongoDB
    await session_store.add_to_set("active_sessions", session_id)
    logger.info(f"WebSocket connection established: {session_id}")

    try:
        # Get user data for personalized experience
        user_data = await get_user_data_from_session(session_id)
        
        # Initialize conversation with agent manager
        initial_response = await agent_manager.process_message(
            user_input="hello",
            session_id=session_id,
            user_data=user_data
        )
        
        # Send initial greeting/assessment
        await websocket.send_json(initial_response)
        logger.info(f"Initial response sent: {session_id}")

        # User input loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "user_message")
            
            if message_type == "user_data_update":
                # Store user data for agent context
                user_data = data.get("user_data", {})
                await session_store.set_session(f"user_data:{session_id}", user_data, ttl=86400)
                logger.info(f"User data updated for session: {session_id}")
                continue
            
            user_input = data.get("message", "").strip()
            
            if not user_input:
                # Send empty input response
                response = {
                    "type": "agent_message",
                    "agent": "orchestrator",
                    "text": "I didn't receive your message. Please try again.",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "session_id": session_id,
                }
                await websocket.send_json(response)
                continue

            # Process user input with agent manager
            agent_response = await agent_manager.process_message(
                user_input=user_input,
                session_id=session_id,
                user_data=user_data
            )
            
            await websocket.send_json(agent_response)
            logger.debug(f"Agent response sent: {session_id}")

    except WebSocketDisconnect:
        # Handle disconnect gracefully
        await session_store.remove_from_set("active_sessions", session_id)
        logger.info(f"WebSocket disconnected: {session_id}")
        
    except Exception as e:
        # Log error and send error message to client
        logger.error(
            f"WebSocket error: {str(e)}",
            extra={"session_id": session_id, "error": str(e)},
        )
        
        try:
            error_message = {
                "type": "error",
                "message": "I encountered an issue. Please refresh and try again.",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "session_id": session_id,
            }
            await websocket.send_json(error_message)
        except:
            pass  # Connection might already be closed
        
        # Clean up session tracking
        await session_store.remove_from_set("active_sessions", session_id)
        await websocket.close()

