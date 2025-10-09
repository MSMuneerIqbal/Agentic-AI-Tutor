"""WebSocket endpoint for agent interactions."""

from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.core.redis import redis_client
from app.services.runner import runner

logger = get_logger(__name__)
metrics = get_metrics_collector()

router = APIRouter()


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time agent communication.

    Flow:
    1. Client connects with session_id
    2. Backend sends FIRST RUNNER greeting immediately
    3. Loop: receive user message → process → send response
    """
    await websocket.accept()
    
    # Track active session
    await redis_client.set_add("active_sessions", session_id)
    metrics.set_sessions_active(await redis_client.set_cardinality("active_sessions"))
    
    logger.info(f"WebSocket connection established: {session_id}")

    try:
        # FIRST RUNNER: Send initial greeting via Orchestrator
        greeting = await runner.run_first_runner(session_id)
        await websocket.send_json(greeting)
        
        logger.info(f"FIRST RUNNER greeting sent: {session_id}")

        # SECOND RUNNER: User input loop
        while True:
            data = await websocket.receive_json()
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

            # Process through orchestrator and agents
            response = await runner.run_second_runner(session_id, user_input)
            await websocket.send_json(response)
            
            logger.debug(f"SECOND RUNNER response sent: {session_id}")

    except WebSocketDisconnect:
        # Handle disconnect gracefully
        await redis_client.set_remove("active_sessions", session_id)
        metrics.set_sessions_active(await redis_client.set_cardinality("active_sessions"))
        
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
        await redis_client.set_remove("active_sessions", session_id)
        metrics.set_sessions_active(await redis_client.set_cardinality("active_sessions"))
        
        await websocket.close()

