# Tutor GPT Architecture Overview

## Components

- Backend (FastAPI)
  - OpenAi Agents SDK (Gemini LLM + tools)
  - Agents: Orchestrator, Assessment, Planning, Tutor, Quiz, Feedback
  - Tools: rag_tool (Pinecone), tavily_tool (MCP), db_tool
  - Guards: input/output/tripwire guardrails
  - API: REST + WebSocket
- Data Stores
  - MySQL: users, profiles, plans, quiz_attempts, directives, audit logs
  - Redis: session state, caches (tavily_cache, rag results)
  - Pinecone: vector index (metadata-only)
- Frontend (Next.js)
  - Pages: index, dashboard, chat, lesson, quiz, admin
  - Components: ChatClient (WS), TavilyCard, QuizQuestion, ProgressBar
- Observability
  - JSON logs, metrics (latency, guardrails, RAG), alerts

## Runtime Flow

1. Client POST `/sessions/start` → backend creates `session_id` (MySQL+Redis)
2. Client opens `ws/sessions/{session_id}` → Orchestrator runs FIRST RUNNER and emits greeting
3. User replies → Orchestrator routes to Assessment/Tutor/Quiz
4. Tutor uses RAG: `rag_tool.retrieve()` (Pinecone) and may call TAVILY (MCP) for live examples
5. Quiz: one-question flow, hints ≤2, bounded-adaptive 15–20; remediation if fail
6. Feedback captured; Planner updates study plan

## Data Model (high-level)

- User, Session, AssessmentResult, Plan, Lesson, QuizAttempt, Directive, Feedback, AgentLog

## Deployment

- Render services: Backend API/WS, Indexing Worker, Frontend
- Environment: `GEMINI_*`, `DATABASE_URL`, `REDIS_URL`, `PINECONE_*`, `SECRET_KEY`, `PORT`

## Security & Privacy

- Secrets via Render; no secrets in code/logs
- Metadata-only in Pinecone; snippets + citations only for copyrighted content
- Guardrails sanitize unsafe outputs and log events without sensitive data
