"""WebSocket endpoint for agent interactions."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time agent communication.

    Flow:
    1. Client connects with session_id
    2. Backend sends FIRST RUNNER greeting immediately
    3. Loop: receive user message → process → send response

    TODO: Implement full orchestrator integration.
    """
    await websocket.accept()

    try:
        # FIRST RUNNER: Send initial greeting
        greeting = {
            "type": "agent_message",
            "agent": "orchestrator",
            "text": "Hello! I'm your AI tutor. Ready to begin your learning journey?",
            "timestamp": "2025-10-09T00:00:00Z",
            "session_id": session_id,
        }
        await websocket.send_json(greeting)

        # SECOND RUNNER: User input loop
        while True:
            data = await websocket.receive_json()
            user_input = data.get("message", "")

            # TODO: Process through orchestrator and agents
            # Placeholder echo response
            response = {
                "type": "agent_message",
                "agent": "orchestrator",
                "text": f"You said: {user_input}",
                "timestamp": "2025-10-09T00:00:00Z",
                "session_id": session_id,
            }
            await websocket.send_json(response)

    except WebSocketDisconnect:
        # TODO: Handle disconnect, save session state
        pass
    except Exception as e:
        # TODO: Log error and send error message to client
        error_message = {
            "type": "error",
            "message": f"An error occurred: {str(e)}",
        }
        await websocket.send_json(error_message)
        await websocket.close()

