# Tutor Agent — System Specification

> Complete technical reference for the project. Read this before touching any code.

---

## 1. What This Project Is

A **general-purpose LMS tutor agent** — a web application where a student opens a chat,
gets their learning style assessed (VARK), receives a personalised study plan, and is
taught any subject using content retrieved from a Pinecone vector database. The system
supports interactive lessons, quizzes, brainstorming sessions, and progress tracking on
a dashboard.

**It is not tied to any specific domain.** All teaching content comes from whatever
PDFs / documents you upload to Pinecone. The agents never assume a subject.

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.12+), Uvicorn |
| Agents / LLM | OpenAI GPT-4o via `AsyncOpenAI` |
| Embeddings | OpenAI `text-embedding-3-small` (1536 dimensions) |
| Web Search | OpenAI Responses API — `web_search_preview` tool |
| Vector DB | Pinecone (serverless, cosine metric, 1536 dims) |
| Session / Cache | MongoDB via Beanie/Motor (`MongoDBSessionStore`) |
| User Data | MongoDB (Beanie ODM) |
| Real-time comms | WebSocket (FastAPI native) |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Frontend state | React Context (`Providers`) + localStorage |
| UI components | Heroicons, Framer Motion, react-hot-toast |

**No Redis.** All caching and session storage goes through MongoDB.

---

## 3. Repository Structure

```
Sir-Project-Tutor-Agent/
├── backend/
│   ├── app/
│   │   ├── main.py                  ← FastAPI entry point
│   │   ├── agents/                  ← 6 AI agents + manager
│   │   │   ├── base.py              ← BaseAgent + _call_llm()
│   │   │   ├── config.py            ← AsyncOpenAI client
│   │   │   ├── agent_manager.py     ← routes messages, manages session state
│   │   │   ├── orchestrator.py
│   │   │   ├── assessment.py
│   │   │   ├── planning.py
│   │   │   ├── tutor.py
│   │   │   ├── quiz.py
│   │   │   └── feedback.py
│   │   ├── api/
│   │   │   ├── middleware.py        ← metrics middleware
│   │   │   └── routes/
│   │   │       ├── websocket.py     ← /ws/sessions/{session_id}
│   │   │       ├── auth.py          ← /auth/login, /auth/register
│   │   │       ├── sessions.py      ← /api/v1/sessions/*
│   │   │       ├── profiles.py      ← /api/v1/profiles/*
│   │   │       ├── assessments.py   ← /api/v1/assessments/*
│   │   │       ├── plans.py         ← /api/v1/plans/*
│   │   │       ├── rag.py           ← /api/v1/rag/*
│   │   │       ├── metrics.py       ← /metrics/*
│   │   │       └── phase6.py        ← advanced features
│   │   ├── core/
│   │   │   ├── config.py            ← Settings (pydantic-settings, reads .env)
│   │   │   ├── openai_manager.py    ← chat_complete(), web_search(), generate_embedding()
│   │   │   ├── session_store.py     ← MongoDBSessionStore
│   │   │   ├── mongodb.py           ← Beanie init / connect / disconnect
│   │   │   ├── logging.py
│   │   │   └── metrics.py
│   │   ├── guards/
│   │   │   ├── schemas.py           ← input/output guardrails + secret detection
│   │   │   └── policies.py
│   │   ├── models/
│   │   │   ├── user_mongo.py        ← MongoDB user document (Beanie)
│   │   │   ├── session.py           ← SessionState enum + SQLAlchemy Session (legacy)
│   │   │   └── (plan, quiz, assessment, feedback, lesson, directive, agent_log)
│   │   ├── services/
│   │   │   ├── rag_service.py       ← RAGService: Pinecone + web search coordinator
│   │   │   ├── plan_service.py      ← CRUD for study plans
│   │   │   ├── profile_service.py   ← user profile read/write
│   │   │   └── runner.py            ← legacy two-stage runner (still used by some routes)
│   │   └── tools/
│   │       ├── rag.py               ← RAGTool: Pinecone queries via OpenAI embeddings
│   │       └── web_search.py        ← WebSearchTool: OpenAI web_search_preview
│   ├── tests/                       ← pytest test suite
│   ├── .env.example                 ← required environment variables template
│   └── pyproject.toml               ← dependencies (openai, fastapi, beanie, pinecone…)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             ← renders <LandingPage />
│   │   │   ├── dashboard/page.tsx   ← renders <Dashboard />
│   │   │   ├── layout.tsx           ← wraps everything in <Providers>
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── providers.tsx        ← React Context: user, session, WebSocket
│   │   │   ├── chat/
│   │   │   │   └── chat-interface.tsx   ← main chat UI, WebSocket consumer
│   │   │   ├── dashboard/
│   │   │   │   ├── dashboard.tsx    ← tab layout, embeds ChatInterface
│   │   │   │   ├── sidebar.tsx
│   │   │   │   ├── header.tsx
│   │   │   │   ├── stats-cards.tsx
│   │   │   │   ├── learning-progress.tsx
│   │   │   │   ├── recent-activity.tsx
│   │   │   │   ├── study-groups.tsx
│   │   │   │   └── quick-actions.tsx
│   │   │   ├── auth/
│   │   │   │   ├── login-modal.tsx
│   │   │   │   └── register-modal.tsx
│   │   │   └── landing/
│   │   │       └── landing-page.tsx
│   │   └── lib/
│   │       └── api.ts               ← REST API helpers (fetch wrappers)
│   ├── package.json                 ← Next.js, Tailwind, Framer Motion, Heroicons
│   └── tailwind.config.js
└── docs/                            ← architecture diagrams, API docs
```

---

## 4. Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
# Required
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pc-...
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/tutor_lms

# Defaults you can leave as-is
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
PINECONE_INDEX_NAME=tutor-lms
PINECONE_ENV=us-east-1-aws
ENVIRONMENT=development
PORT=8000
FRONTEND_URL=http://localhost:3000
```

Settings are loaded by `app/core/config.py` via `pydantic-settings` from `.env`.

---

## 5. How to Run

### Backend

```bash
cd backend
pip install -e .          # or: uv sync
uvicorn app.main:app --reload --port 8000
```

API docs auto-generated at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev               # runs on http://localhost:3000
```

### Environment variable the frontend needs

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 6. Agent Architecture

### 6.1 The 6 Agents

All agents extend `BaseAgent` (`app/agents/base.py`) which provides:

- `_call_llm(system_prompt, user_input, rag_context, history)` — calls GPT-4o and returns the text
- `validate_input()` / `validate_output()` — guardrail checks
- `execute()` — wraps `_execute()` with validation + error handling

| Agent | File | Role |
|---|---|---|
| **Orchestrator** | `orchestrator.py` | Greets the student, understands what they want to learn, routes to other agents, handles general conversation |
| **Assessment** | `assessment.py` | Runs the 6-question VARK test, determines learning style (V/A/R/K), persists result to MongoDB session |
| **Planning** | `planning.py` | Asks about goals and time commitment, calls GPT-4o with RAG + web context to generate a structured study plan, saves to MongoDB |
| **Tutor** | `tutor.py` | Delivers lessons from RAG content + web search, adapts style to VARK, also handles brainstorming requests |
| **Quiz** | `quiz.py` | Uses GPT-4o to generate JSON quiz questions from RAG content, evaluates answers, produces score + feedback |
| **Feedback** | `feedback.py` | Analyses session progress data (topics done, quiz scores, time) and produces personalised coaching feedback |

### 6.2 Agent Manager (`agent_manager.py`)

The `AgentManager` singleton is instantiated once in `websocket.py`. It:

1. Gets or creates session state from MongoDB (`session_store.get_session("session_state:{id}")`)
2. Selects which agent to call based on `SessionState` and user input keywords
3. Builds a `context` dict and calls `agent._execute(user_input, context)`
4. Persists the updated session state back to MongoDB
5. Returns a standardised response dict to the WebSocket handler

**Routing logic (priority order):**

```
SessionState.GREETING   → orchestrator
SessionState.ASSESSING  → assessment
SessionState.PLANNING   → planning
SessionState.TUTORING   → tutor
SessionState.QUIZZING   → quiz
keyword "quiz/test/practice" → quiz
keyword "feedback/progress"  → feedback
keyword "brainstorm"         → tutor
keyword "learn/explain/what" → tutor
default                      → orchestrator
```

### 6.3 Session State Machine

```
GREETING → ASSESSING → PLANNING → TUTORING → QUIZZING → (back to TUTORING)
```

Transitions happen automatically inside `_update_session_state()`:
- Assessment complete (`action == "assessment_complete"`) → saves learning style → moves to `PLANNING`
- Plan complete (`action == "plan_complete"`) → moves to `TUTORING`
- State can also be set explicitly by any agent returning `"next_state"` in its response dict

### 6.4 Session State Document (MongoDB)

Every session is one document stored under key `"session_state:{session_id}"`:

```python
{
  "session_id": str,
  "current_state": SessionState,          # e.g. "tutoring"
  "user_profile": {
    "name": str,
    "email": str,
    "learning_style": "V" | "A" | "R" | "K" | None,
  },
  "current_topic": str | None,
  "progress": {
    "topics_completed": [],
    "quiz_scores": [],
    "plan_topics": [],
    "time_spent": 0,
  },
  "assessment_data": {
    "answers": [],                        # accumulated VARK answers
    "completed": bool,
  },
  "quiz_data": dict | None,              # active quiz state (questions, index, score)
  "planning_stage": str,                 # "ask_goals" | "ask_time" | "generate_plan"
  "goals": str | None,                   # student's stated learning goals
  "conversation_history": [...],         # last 50 messages (user + agent)
  "created_at": ISO timestamp,
  "last_updated": ISO timestamp,
}
```

---

## 7. RAG + Web Search Pipeline

### 7.1 RAG (Pinecone)

`app/tools/rag.py` — `RAGTool`

- On startup, connects to Pinecone index `tutor-lms` (creates it if missing)
- **Embedding model:** `text-embedding-3-small` → 1536-dimensional vectors
- Each content chunk stored with metadata: `content`, `source`, `page`, `chapter`, `content_type`
- `content_type` filter per agent: tutors get `["lesson","example","tutorial"]`, quiz gets `["concept","definition"]`, etc.

### 7.2 Web Search (OpenAI)

`app/tools/web_search.py` — `WebSearchTool`

- Calls `openai_manager.web_search(query)` which uses the **Responses API** with `web_search_preview` tool
- Returns `WebResult` objects: `title`, `url`, `content` (first 500 chars)
- Used by Tutor (live examples, best practices) and Planning (curriculum ideas)

### 7.3 RAG Service

`app/services/rag_service.py` — `RAGService`

The coordination layer. Every agent calls this instead of `RAGTool` / `WebSearchTool` directly. Provides:

| Method | Returns |
|---|---|
| `get_tutor_lesson_content(topic, style)` | RAG chunks + web examples + best practices |
| `get_quiz_content(topic)` | RAG chunks filtered for quiz-worthy content |
| `get_planning_content(goals, interests)` | RAG chunks + web curriculum ideas |
| `get_assessment_content(topic)` | RAG chunks for assessment context |

### 7.4 Uploading Content to Pinecone

There is no automated ingestion pipeline in the app. Upload PDFs manually:

1. Extract text from PDFs (use `pdfplumber` or `pypdf2`)
2. Split into chunks (~500 tokens)
3. Call `openai_manager.generate_embedding(chunk_text)` for each chunk
4. Upsert to Pinecone with metadata: `{"content": text, "source": filename, "page": n, "content_type": "lesson"}`

The index name must match `PINECONE_INDEX_NAME=tutor-lms` and dimension must be `1536`.

---

## 8. WebSocket Communication Protocol

**Endpoint:** `ws://localhost:8000/ws/sessions/{session_id}`

### Client → Server

```json
{
  "type": "user_message",
  "message": "I want to learn Python",
  "user_id": "user-uuid",
  "timestamp": "2026-04-30T10:00:00Z"
}
```

Special message type for updating user context:
```json
{ "type": "user_data_update", "user_data": { "name": "...", "email": "..." } }
```

### Server → Client

```json
{
  "type": "agent_message",
  "agent": "tutor",
  "text": "Let's dive into Python...",
  "timestamp": "2026-04-30T10:00:01Z",
  "session_id": "abc123",
  "conversation_state": "tutoring",
  "metadata": { ... }
}
```

On error:
```json
{ "type": "error", "message": "...", "timestamp": "..." }
```

### Connection Flow

1. Client connects → server sends automatic greeting (`"hello"` message to orchestrator)
2. Client sends `user_data_update` with user profile
3. Full duplex conversation loop until disconnect

---

## 9. REST API Routes

All prefixed with `/api/v1` unless noted.

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Health check |
| GET | `/docs` | Swagger UI |
| POST | `/auth/login` | Authenticate user |
| POST | `/auth/register` | Register new user |
| GET | `/api/v1/sessions/{id}` | Get session state |
| POST | `/api/v1/sessions` | Create session |
| GET | `/api/v1/profiles/{user_id}` | Get user profile |
| PUT | `/api/v1/profiles/{user_id}` | Update user profile |
| GET | `/api/v1/assessments/{user_id}` | Get assessment results |
| POST | `/api/v1/assessments` | Save assessment result |
| GET | `/api/v1/plans/{user_id}` | Get user's study plans |
| POST | `/api/v1/plans` | Create study plan |
| GET | `/api/v1/rag/query` | Query RAG content directly |
| GET | `/api/v1/rag/live-examples` | Web search for live examples |
| GET | `/metrics` | System metrics |

---

## 10. Frontend Architecture

### State Management

`providers.tsx` exposes a React context with:

- `user` — logged-in user object (persisted in `localStorage` + `sessionStorage`)
- `session` — current learning session state
- `websocket` — the active WebSocket connection
- `isConnected` — connection status boolean
- `setUser()`, `connectWebSocket()`, `disconnectWebSocket()`

The `Providers` wrapper is applied in `app/layout.tsx` so every page has access.

### Page Flow

```
/ (page.tsx)
  └── <LandingPage>
        ├── Login / Register modals
        └── On success → navigate to /dashboard

/dashboard (dashboard/page.tsx)
  └── <Dashboard>
        ├── <Sidebar>      — navigation tabs
        ├── <Header>       — user info, notifications
        ├── <StatsCards>   — progress stats
        ├── <LearningProgress> — topic completion bars
        ├── <RecentActivity>   — last sessions
        ├── <StudyGroups>      — peer groups (UI only)
        ├── <QuickActions>     — shortcut buttons
        └── <ChatInterface>    — floating chat panel (WebSocket)
```

### ChatInterface

`components/chat/chat-interface.tsx`

- Opens a WebSocket connection to `ws://localhost:8000/ws/sessions/{user.id}`
- All agent messages arrive as `{ type: "agent_message", text: "..." }` events
- Shows a typing indicator (3-dot bounce) while waiting for the agent response
- Handles the `error` message type gracefully

---

## 11. Guardrails

`app/guards/schemas.py`

Every agent response passes through two checks:

**Input validation:**
- Max 5000 characters
- Cannot be empty

**Output validation:**
- Max 10,000 characters (truncates if exceeded)
- Secret detection — blocks real credentials matching patterns like `sk-[48 chars]`, `AIza[35 chars]`, `api_key=<value>`, etc. Educational mentions of "API key" in prose are NOT blocked.

Violations are caught in `BaseAgent.execute()` and returned as a safe error message instead of raising an exception.

---

## 12. VARK Learning Style System

The Assessment Agent runs exactly 6 questions (up to 8 if confidence is low). Each question has 4 options mapping to:

| Option | Style | Code |
|---|---|---|
| a | Visual | V |
| b | Auditory | A |
| c | Reading/Writing | R |
| d | Kinesthetic | K |

The dominant choice (by count) becomes the student's style. Confidence = dominant\_count / total\_answers. Assessment completes when confidence ≥ 0.7 OR all questions are asked.

The style is stored in `session["user_profile"]["learning_style"]` and passed to Tutor and Planning agents via context to adapt content delivery.

---

## 13. Key Architectural Decisions

**Why MongoDB for sessions instead of Redis?**
Redis was removed to reduce infrastructure dependencies. `MongoDBSessionStore` provides the same interface (`set_session`, `get_session`, `add_to_set`, etc.) using Beanie documents with TTL via an `expires_at` field.

**Why session-scoped quiz state instead of instance variables?**
`AgentManager` is a singleton shared across all WebSocket connections. If quiz state were stored on the `QuizAgent` instance, two students would overwrite each other's quiz. All quiz state lives in the MongoDB session document under `"quiz_data"`.

**Why not use the OpenAI Agents SDK runner?**
The `agents` library runner would take over the execution loop. The custom `_execute()` pattern gives fine-grained control over state transitions, context injection, and session persistence that the SDK runner doesn't expose cleanly.

**Why OpenAI Responses API for web search instead of Tavily?**
Fewer external dependencies (one API key instead of two), native integration with the same client used for chat, and the `web_search_preview` tool is grounded — it returns citations.

**Why Pinecone index dimension 1536?**
That is the output dimension of `text-embedding-3-small`. The old Gemini embedding model used 768 dimensions. Any existing Pinecone index built with Gemini must be deleted and recreated at 1536 before use.

---

## 14. Known Stubs / Incomplete Areas

| File / Area | Status |
|---|---|
| `app/core/gemini_manager.py` | Stale — never imported by live code, safe to delete later |
| `app/tools/tavily_mcp.py` | Stale — never imported by live code, safe to delete later |
| `app/core/database.py` | Legacy SQLAlchemy stub — `get_db()` returns `None`. Never called in live flow. |
| `app/models/session.py` `Session` class | SQLAlchemy model — the `SessionState` enum is used, but the `Session` table is not |
| `StudyGroups` dashboard component | UI rendered but not connected to real data |
| `QuickActions` dashboard component | UI rendered but actions are not wired to backend |
| Rate limiting middleware | Code exists in `app/middleware/rate_limiting.py` but commented out in `main.py` |

---

## 15. Adding New Course Content

1. Prepare your documents (PDFs, text files)
2. Chunk the text (~400–600 tokens per chunk)
3. For each chunk, call the OpenAI embeddings API with model `text-embedding-3-small`
4. Upsert vectors to Pinecone index `tutor-lms` with this metadata schema:
   ```json
   {
     "content": "the chunk text",
     "source": "filename.pdf",
     "page": 12,
     "chapter": "Chapter 3: Variables",
     "content_type": "lesson"
   }
   ```
   Valid `content_type` values: `lesson`, `example`, `explanation`, `tutorial`, `overview`,
   `structure`, `curriculum`, `roadmap`, `concept`, `definition`, `comparison`,
   `best_practice`, `command`, `configuration`, `introduction`

5. Restart the backend — `RAGTool` will pick up the new content automatically on the next query.
