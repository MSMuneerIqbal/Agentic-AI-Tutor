# PHR: Phase 3 Implementation (User Story 1: Session Start & Greeting)

**Stage**: implementation  
**Date**: 2025-10-09  
**Feature**: 001-backend-first-agentic

## User Request

```
/sp.implement Phase 3: User Story 1 (T013-T015)
```

## Actions Completed

### T013: Implement POST /sessions/start ✅

**Enhanced Session Management** (`backend/app/api/routes/sessions.py`):

**Full Session Creation Logic**:
- User lookup/creation with email validation
- Session creation with proper state initialization (GREETING)
- MySQL persistence with proper relationships
- Redis caching with 24-hour TTL
- Active sessions tracking via Redis sets
- Comprehensive error handling and logging
- Metrics tracking (request latency, active sessions)

**Key Features**:
```python
# User creation/lookup
async def get_or_create_user(db: AsyncSession, user_email: str | None) -> User:
    if not user_email:
        user_email = f"temp_user_{uuid.uuid4().hex[:8]}@tutorgpt.local"
    
    # Try to find existing user
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    
    if user:
        return user
    
    # Create new user
    user = User(email=user_email, display_name=user_email.split("@")[0])
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# Session creation with Redis caching
session = Session(
    user_id=user.id,
    state=SessionState.GREETING,
    last_checkpoint="session_started",
)
db.add(session)
await db.commit()
await db.refresh(session)

# Store in Redis with TTL
await store_session_state(session)
```

**Session Retrieval**:
- Redis-first lookup for performance
- Database fallback for cache misses
- Automatic cache refresh on database hits
- Proper error handling (404 for missing sessions)

**Metrics Integration**:
- Request latency tracking per endpoint
- Active sessions count via Redis sets
- Structured logging with session context

### T014: Implement Orchestrator Runner ✅

**Runner Service** (`backend/app/services/runner.py`):

**Two-Stage Runner Pattern**:
1. **FIRST RUNNER**: Backend-initiated greeting via Orchestrator Agent
2. **SECOND RUNNER**: User input processing loop

**Key Implementation**:
```python
class Runner:
    def __init__(self):
        self.orchestrator = OrchestratorAgent()

    async def run_first_runner(self, session_id: str) -> dict[str, Any]:
        # Get session context from Redis
        session_context = await self._get_session_context(session_id)
        
        # Execute orchestrator with "hello" trigger
        result = await self.orchestrator.run("hello", session_context)
        
        # Update session state if needed
        if "next_state" in result:
            await self._update_session_state(session_id, result["next_state"])
        
        # Create greeting message
        greeting = {
            "type": "agent_message",
            "agent": result.get("agent", "orchestrator"),
            "text": result.get("message", "Hello! Ready to begin?"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "action": result.get("action", "continue"),
        }
        return greeting

    async def run_second_runner(self, session_id: str, user_input: str) -> dict[str, Any]:
        # Get session context
        session_context = await self._get_session_context(session_id)
        
        # Execute orchestrator with user input
        result = await self.orchestrator.run(user_input, session_context)
        
        # Update session state if needed
        if "next_state" in result:
            await self._update_session_state(session_id, result["next_state"])
        
        # Create response message
        response = {
            "type": "agent_message",
            "agent": result.get("agent", "orchestrator"),
            "text": result.get("message", "I understand. Let me help you with that."),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "action": result.get("action", "continue"),
        }
        return response
```

**Session Context Management**:
- Redis-based session state retrieval
- Default context fallback for missing sessions
- State transitions with checkpoint tracking
- JSON serialization/deserialization for Redis storage

**WebSocket Integration** (`backend/app/api/routes/websocket.py`):
- Automatic greeting on connection (FIRST RUNNER)
- User input loop (SECOND RUNNER)
- Active session tracking via Redis sets
- Graceful disconnect handling
- Error handling with user-friendly messages
- Metrics integration (active sessions count)

### T015: Persist Directives and Initial Events ✅

**Directive Service** (`backend/app/services/directive_service.py`):

**Comprehensive Directive Management**:
- Session start directives
- Greeting directives
- User input directives
- Agent response directives
- State transition directives

**Key Features**:
```python
class DirectiveService:
    async def create_session_start_directive(self, session_id: str, user_id: str) -> Directive:
        payload = {
            "event": "session_started",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "initial_state": "greeting",
        }
        return await self.create_directive(session_id, "orchestrator", payload)

    async def create_greeting_directive(self, session_id: str, greeting_message: str) -> Directive:
        payload = {
            "event": "greeting_sent",
            "message": greeting_message,
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "orchestrator",
        }
        return await self.create_directive(session_id, "orchestrator", payload)

    async def create_user_input_directive(self, session_id: str, user_input: str) -> Directive:
        payload = {
            "event": "user_input_received",
            "input": user_input,
            "timestamp": datetime.utcnow().isoformat(),
            "input_length": len(user_input),
        }
        return await self.create_directive(session_id, "user", payload)

    async def create_agent_response_directive(self, session_id: str, agent_name: str, 
                                            response_message: str, action: str | None = None) -> Directive:
        payload = {
            "event": "agent_response_sent",
            "agent": agent_name,
            "message": response_message,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "response_length": len(response_message),
        }
        return await self.create_directive(session_id, "agent", payload)
```

**Integration Points**:
- Session creation automatically creates session start directive
- Runner service persists greeting and user interaction directives
- All directives include timestamps and structured metadata
- Database transactions with proper error handling

### Enhanced Redis Client ✅

**Redis Operations** (`backend/app/core/redis.py`):

**Added Missing Methods**:
- `set_add()` - Add values to Redis sets
- `set_remove()` - Remove values from Redis sets  
- `set_cardinality()` - Get set member count
- `setex()` - Set key with expiration
- `get()` - Generic key retrieval

**Active Sessions Tracking**:
- Redis set for active session IDs
- Automatic cleanup on disconnect
- Metrics integration for session counts

### Testing Infrastructure ✅

**Integration Tests**:
- `test_session_creation.py` - Session creation and retrieval
- `test_websocket_runner.py` - WebSocket greeting and user loop
- `test_directive_service.py` - Directive creation and retrieval

**Test Coverage**:
- Session creation with/without email
- User creation and lookup
- Redis caching behavior
- WebSocket greeting flow
- User input processing
- Error handling scenarios
- Metrics tracking
- Directive persistence

## Deliverables

**Files Created/Modified**: 8 files
- `app/api/routes/sessions.py` - Enhanced session management (200+ lines)
- `app/services/runner.py` - Two-stage runner implementation (NEW, 230+ lines)
- `app/services/directive_service.py` - Directive management (NEW, 300+ lines)
- `app/api/routes/websocket.py` - WebSocket integration (100+ lines)
- `app/core/redis.py` - Enhanced Redis operations (50+ lines)
- `tests/integration/test_session_creation.py` - Session tests (NEW)
- `tests/integration/test_websocket_runner.py` - WebSocket tests (NEW)
- `tests/unit/test_directive_service.py` - Directive tests (NEW)

**Tasks Completed**: T013, T014, T015 (3/3) ✅

**Key Features Implemented**:
- Full session lifecycle (create → greet → interact → persist)
- Two-stage runner pattern (FIRST/SECOND RUNNER)
- Comprehensive directive tracking
- Redis caching with MySQL persistence
- Active session monitoring
- Error handling and fallbacks
- Metrics integration
- WebSocket real-time communication

**End-to-End Flow**:
1. **POST /sessions/start** → Creates user + session + directive
2. **WebSocket /ws/sessions/{id}** → FIRST RUNNER greeting
3. **User input loop** → SECOND RUNNER processing + directives
4. **All events persisted** → MySQL + Redis + metrics

## Acceptance Criteria Met

✅ **T013 Acceptance**:
- Session creation with user lookup/creation
- MySQL persistence with proper relationships
- Redis caching with TTL
- Error handling and logging
- Metrics tracking

✅ **T014 Acceptance**:
- Orchestrator Runner with FIRST/SECOND RUNNER
- WebSocket integration with immediate greeting
- Session state management
- User input processing loop
- Error handling and fallbacks

✅ **T015 Acceptance**:
- Directive persistence for all events
- Session start, greeting, user input, agent response directives
- Database transactions with error handling
- Structured metadata and timestamps

## Technical Implementation

**Architecture**:
- **Session Management**: MySQL + Redis hybrid storage
- **Runner Pattern**: Orchestrator Agent + Runner Service
- **Directive Tracking**: Comprehensive event logging
- **WebSocket**: Real-time bidirectional communication
- **Metrics**: Request latency, active sessions, error tracking

**Data Flow**:
```
POST /sessions/start → User/Session Creation → Redis Cache → Directive
WebSocket Connect → FIRST RUNNER → Orchestrator → Greeting → Directive
User Input → SECOND RUNNER → Orchestrator → Response → Directive
```

**Error Handling**:
- Graceful fallbacks for Redis failures
- User-friendly error messages
- Comprehensive logging with context
- Database transaction rollbacks

## Next Steps

**Phase 4: User Story 2 - Learning Style Assessment** (T016-T018):
- Assessment Agent with VARK questions
- Profile persistence and updates
- Orchestrator state transitions

**OR Phase 5: User Story 3 - Lesson Delivery** (T019-T021):
- RAG tool implementation
- Tutor Agent integration
- Citation and example handling

**OR Phase 8: RAG Implementation** (T-RAG-001/002):
- Pinecone index setup
- Gemini embeddings integration
- Indexing worker and status endpoint

---

**Status**: ✅ Phase 3 complete. Full session lifecycle with greeting flow working end-to-end!

**Ready for `/sp.implement Phase 4` (User Story 2: Learning Style Assessment)** 

This will add the Assessment Agent with VARK questions and profile management to complete the user onboarding flow.
