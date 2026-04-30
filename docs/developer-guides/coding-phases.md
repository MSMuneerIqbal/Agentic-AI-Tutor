# Coding Phases Guide

## Overview

This guide breaks down the implementation into **9 phases** based on `specs/001-backend-first-agentic/tasks.md`. Each phase has clear goals, deliverables, and validation steps.

---

## Phase 1: Setup (Shared Infrastructure)

**Tasks**: T001–T005  
**Duration**: ~1-2 days  
**Goal**: Initialize project structure, dependencies, and environment

### What You'll Code

1. **T001**: Create directories
   ```
   backend/
     app/
       api/, agents/, tools/, guards/, models/, services/, core/
     tests/
       unit/, integration/, contract/
   frontend/
     app/, components/, lib/, tests/
   ```

2. **T002**: Backend dependencies
   ```bash
   cd backend
   uv venv && .venv/Scripts/activate
   uv init --python 3.12
   uv add fastapi "uvicorn[standard]" pydantic python-dotenv httpx pytest ruff openai-agents aiomysql sqlalchemy[asyncio] redis pinecone-client
   ```

3. **T003**: Frontend scaffolding
   ```bash
   cd frontend
   npx create-next-app@latest . --typescript --tailwind --app
   npm install
   ```

4. **T004**: Linting/formatting
   - Add `backend/ruff.toml`, `backend/pyproject.toml` (ruff, black, isort)
   - Add `frontend/.eslintrc.json`, `frontend/.prettierrc`
   - Add `.pre-commit-config.yaml`

5. **T005**: Environment
   - Create `.env.sample` with all vars (see `plan.md` env section)
   - Add `.gitignore` (secrets, venv, node_modules, build)

### Validation

- Run `uv sync` in backend → no errors
- Run `npm run dev` in frontend → starts on port 3000
- Run `ruff check backend/` → passes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Tasks**: T006–T012  
**Duration**: ~3-5 days  
**Goal**: Core infrastructure that ALL user stories depend on

### What You'll Code

1. **T006**: Database models
   - `backend/app/models/base.py` (SQLAlchemy Base)
   - `backend/app/models/user.py`, `session.py`, `assessment_result.py`, etc. (from `data-model.md`)
   - Migration setup (Alembic or raw SQL)

2. **T007**: Redis client
   - `backend/app/core/redis.py` (connection pool, session helpers)

3. **T008**: Agents SDK + Guardrails
   - `backend/app/agents/base.py` (import OpenAI Agents SDK, Gemini config)
   - `backend/app/guards/` (input/output/tripwire guardrail schemas)

4. **T009**: FastAPI app
   - `backend/app/main.py` (app init, CORS, error handlers)
   - `backend/app/api/routes.py` (router placeholders)

5. **T010**: Logging/metrics
   - `backend/app/core/logging.py` (JSON logger, metrics stubs)

6. **T011**: WebSocket endpoint skeleton
   - `backend/app/api/ws.py` (endpoint `/ws/sessions/{session_id}`)

7. **T012**: Session start endpoint
   - `backend/app/api/sessions.py` (POST `/sessions/start`)

### Validation

- Start backend: `uvicorn app.main:app --reload`
- Curl `POST /sessions/start` → returns `{ session_id }`
- Open WS connection → connects (no greeting yet)

---

## Phase 2A: Core Tests, Guardrails, MCP UI

**Tasks**: T-GU-001 to T-GU-005, T-CON-001, T-SEC-001  
**Duration**: ~2-3 days  
**Goal**: Add TDD tests and guardrail implementation

### What You'll Code

1. **T-GU-001**: WS greeting e2e test
   - `backend/tests/integration/test_ws_greeting.py`
   - Mock Gemini, assert greeting schema

2. **T-GU-002**: RAG contract test
   - `backend/tests/contract/test_rag_tool.py`
   - Mock Pinecone or test namespace

3. **T-GU-003**: Guardrail fallback test
   - `backend/tests/integration/test_guardrail.py`
   - Trigger output guardrail, assert sanitized response

4. **T-GU-004**: Reconnect test
   - `backend/tests/integration/test_reconnect.py`

5. **T-GU-005**: Playwright smoke test
   - `frontend/tests/e2e/greeting.spec.ts`
   - Use `@playwright/test`, assert greeting card appears

6. **T-SEC-001**: Implement guardrails
   - `backend/app/guards/policies.py` (forbidden patterns, PII filters)

### Validation

- Run `pytest backend/tests/` → all pass
- Run `npx playwright test` → smoke test passes

---

## Phase 2B: Observability & Metrics

**Tasks**: T-OBS-001, T-OBS-002  
**Duration**: ~1 day  
**Goal**: Metrics emission and alerts

### What You'll Code

1. **T-OBS-001**: Emit metrics
   - `backend/app/core/metrics.py` (Prometheus client or structured log format)
   - Instrument endpoints: latency, p95, guardrail_trigger_count

2. **T-OBS-002**: Alert definitions
   - `docs/ops/alerts.md` (runbook, thresholds)

### Validation

- Hit `/metrics` endpoint → see counters
- Check logs for structured metrics

---

## Phase 3: User Story 1 (Session Start & Greeting)

**Tasks**: T013–T015  
**Duration**: ~2 days  
**Goal**: First user story — greeting flow

### What You'll Code

1. **T013**: Implement `/sessions/start`
   - Create session in MySQL/Redis
   - Return `{ session_id }`

2. **T014**: Orchestrator FIRST RUNNER
   - `backend/app/agents/orchestrator.py`
   - `Runner.run(agent, "hello", session)` → sends greeting over WS

3. **T015**: Persist directives
   - Save directive to DB

### Validation

- Call `/sessions/start`, open WS → greeting appears within 2s
- Run T-GU-001 test → passes

---

## Phase 4: User Story 2 (Assessment)

**Tasks**: T016–T018  
**Duration**: ~2-3 days  
**Goal**: VARK assessment (5–12 Q)

### What You'll Code

1. **T016**: Assessment agent
   - `backend/app/agents/assessment.py`
   - Question flow, validation

2. **T017**: Persist `AssessmentResult`
   - Save to MySQL

3. **T018**: State transitions
   - Orchestrator → assessing → tutoring

### Validation

- Complete assessment → profile stored
- Run e2e test for assessment flow

---

## Phase 5: User Story 3 (Lesson with RAG)

**Tasks**: T019–T021  
**Duration**: ~3-4 days  
**Goal**: Tutor delivers lessons with citations

### What You'll Code

1. **T019**: RAG tool
   - `backend/app/tools/rag_tool.py`
   - `retrieve(query, k, namespace, filter)` → Pinecone query + Redis cache

2. **T020**: RAG retrieve endpoint
   - `POST /api/v1/rag/retrieve`

3. **T021**: Tutor agent
   - `backend/app/agents/tutor.py`
   - Uses RAG + TAVILY (MCP) for examples

### Validation

- Request lesson → see examples + citations
- Run T-GU-002 test → passes

---

## Phase 6: User Story 4 (Quiz with Hints)

**Tasks**: T022–T024, T-DF-001  
**Duration**: ~3-4 days  
**Goal**: Bounded-adaptive quiz (15–20 Q)

### What You'll Code

1. **T022**: Quiz agent
   - `backend/app/agents/quiz.py`
   - Hinting (max 2), scoring

2. **T023**: Bounded-adaptive logic
   - Early stop ≥15 on mastery; extend to 20 if borderline

3. **T024**: Remediation flow
   - Mini-lesson + mini-quiz on fail

4. **T-DF-001**: Quiz policy tests
   - Unit tests for length logic

### Validation

- Complete quiz → score ≥70% passes
- Early stop on mastery works
- Remediation triggers on fail

---

## Phase 7: User Story 5 (Feedback)

**Tasks**: T025–T026  
**Duration**: ~1-2 days  
**Goal**: Capture feedback and adapt

### What'll Code

1. **T025**: Feedback API
   - `POST /api/v1/feedback`

2. **T026**: Adaptation hooks
   - Tutor/Planner adjusts tone/difficulty

### Validation

- Submit feedback → next lesson reflects changes

---

## Phase 8: RAG Indexing Worker

**Tasks**: T-RAG-001, T027–T029, T-RAG-002  
**Duration**: ~3-4 days  
**Goal**: Indexing pipeline

### What You'll Code

1. **T-RAG-001**: Embedding model + index
   - Document `EMBEDDING_MODEL=gemini-embedding-1.0`
   - Script to compute dimension

2. **T027**: Pinecone setup
   - Index creation script, chunker

3. **T028**: Background worker
   - `backend/app/workers/indexer.py`

4. **T029**: Index endpoint
   - `POST /api/v1/rag/index`

5. **T-RAG-002**: Status endpoint
   - `GET /api/v1/rag/index/{job_id}`

### Validation

- Index sample docs → vectors in Pinecone
- Query status → see job progress

---

## Phase 9: Frontend Skeleton

**Tasks**: T030–T032, T-UX-001  
**Duration**: ~4-5 days  
**Goal**: Next.js UI with WS client

### What You'll Code

1. **T030**: Pages
   - `frontend/app/(auth)/login/page.tsx`
   - `frontend/app/dashboard/page.tsx`
   - `frontend/app/chat/page.tsx`
   - `frontend/app/lesson/page.tsx`
   - `frontend/app/quiz/page.tsx`
   - `frontend/app/admin/page.tsx`

2. **T031**: Components
   - `frontend/components/ChatClient.tsx` (WS)
   - `frontend/components/TavilyCard.tsx`
   - `frontend/components/QuizQuestion.tsx`
   - `frontend/components/ProgressBar.tsx`

3. **T032**: WS connect
   - Call `/sessions/start`, open WS, render messages

4. **T-UX-001**: Admin indexing page
   - Query indexing status, show jobs

### Validation

- Start session → greeting appears
- Navigate lesson/quiz flows
- Run Playwright test (T-GU-005) → passes

---

## Phase N: Polish & Cross-Cutting

**Tasks**: T033–T035  
**Duration**: ~2-3 days  
**Goal**: Final refinements

### What You'll Code

1. **T033**: Documentation
2. **T034**: Dashboards/alerts
3. **T035**: Security hardening

### Validation

- All tests pass
- Coverage ≥80%
- Constitution compliance check

---

## Summary

**Total Estimated Duration**: ~25-35 days (varies by team size and experience)

**Recommended Order**:
1. Phase 1 (Setup) → **START HERE**
2. Phase 2 (Foundational) → **CRITICAL BLOCKER**
3. Phase 2A+2B (Tests/Observability)
4. Phase 3 (US1) → **MVP CHECKPOINT**
5. Phases 4-7 (US2-US5) → Incremental delivery
6. Phase 8 (RAG Worker) → Can parallelize after Phase 2
7. Phase 9 (Frontend) → After backend WS+endpoints ready
8. Phase N (Polish)

**Next Step**: Begin with **Phase 1: Setup** (T001-T005)

