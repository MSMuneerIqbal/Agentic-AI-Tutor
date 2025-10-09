# Tasks: Backend-first, agentic Tutor GPT flow

**Input**: Design documents from `/specs/001-backend-first-agentic/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Initialize backend project structure under `backend/` and `frontend/`
- [ ] T002 Add Python environment and dependencies via `uv` (FastAPI, Agents SDK, SQLAlchemy async, Redis, Pinecone, httpx, pytest, ruff)
- [ ] T003 Add Node/Next.js scaffolding with `frontend/` baseline (no pages yet)
- [ ] T004 [P] Add lint/format config (ruff, black/isort, eslint/prettier) and pre-commit hooks
- [ ] T005 Create `.env.sample` with required variables (Gemini, DB, Redis, Pinecone, Secret, Port)

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T006 Setup database engine and base models per `data-model.md` in `backend/app/models/`
- [ ] T007 [P] Configure Redis client and session store utilities in `backend/app/core/redis.py`
- [ ] T008 [P] Configure Agents SDK (Gemini LLM + embeddings) and guardrails in `backend/app/agents/`
- [ ] T009 Create API app skeleton with FastAPI, routers, error handlers in `backend/app/api/__init__.py`
- [ ] T010 Configure structured JSON logging and metrics stubs
- [ ] T011 Add WebSocket endpoint skeleton `/ws/sessions/{session_id}`
- [ ] T012 Add REST endpoint skeleton `POST /sessions/start`

## Phase 3: User Story 1 - Session start and first-run greeting (Priority: P1)

**Goal**: Start a session and send a contextual greeting with first action.
**Independent Test**: Call `/sessions/start` and open WS; verify greeting + first action.

### Implementation
- [ ] T013 [US1] Implement `POST /sessions/start` to create session and persist to MySQL/Redis
- [ ] T014 [US1] Implement Orchestrator Runner to send initial greeting over WS
- [ ] T015 [US1] Persist directives and initial events to DB

## Phase 4: User Story 2 - Learning style assessment and profile (Priority: P1)

**Goal**: Conduct a 5–12 Q assessment; store profile.
**Independent Test**: Complete assessment and verify stored profile.

### Implementation
- [ ] T016 [US2] Add Assessment agent with question flow and validation
- [ ] T017 [US2] Persist `AssessmentResult` and profile updates
- [ ] T018 [US2] Orchestrator state transition into/out of assessing

## Phase 5: User Story 3 - Lesson with supporting knowledge (Priority: P2)

**Goal**: Deliver concise lesson with examples and optional citations.
**Independent Test**: Request lesson; verify examples and citations (when available).

### Implementation
- [ ] T019 [P] [US3] Implement `tools/rag_tool.py` with `retrieve(query,k,namespace,filter)` and Redis caching
- [ ] T020 [P] [US3] Implement `POST /api/v1/rag/retrieve` endpoint wiring to tool
- [ ] T021 [US3] Tutor agent integration: use RAG (and TAVILY via MCP) and show citations

## Phase 6: User Story 4 - Dynamic quiz with hints and remediation (Priority: P2)

**Goal**: One-question-at-a-time quiz, hints ≤2, bounded-adaptive 15–20, remediation on fail.
**Independent Test**: Complete quiz; verify early stop/extension and remediation.

### Implementation
- [ ] T022 [US4] Quiz agent with hinting and scoring; pass at ≥70%
- [ ] T023 [US4] Bounded-adaptive length logic (early stop ≥15 mastery; extend to 20 if borderline)
- [ ] T024 [US4] Remediation mini-lesson and mini-quiz flow

## Phase 7: User Story 5 - Feedback and continuous improvement (Priority: P3)

**Goal**: Capture feedback and adapt subsequent content.
**Independent Test**: Submit feedback; observe adjustments in next interactions.

### Implementation
- [ ] T025 [US5] Feedback capture API and persistence
- [ ] T026 [US5] Adaptation hooks in Tutor/Planner to apply feedback

## Phase 8: RAG Indexing Worker and Pinecone Setup (Shared)

**Goal**: Index documents into Pinecone and monitor status.
**Independent Test**: Index sample docs; verify vector count and retrieval.

### Implementation
- [ ] T027 [P] task/pinecone-setup: index creation script, embedding wrapper, chunker
- [ ] T028 [P] task/index-worker: background worker to run indexing jobs and emit status to MySQL
- [ ] T029 task/rag-api: implement `POST /api/v1/rag/index` endpoint to enqueue jobs

## Phase 9: Frontend Skeleton & WS client

**Goal**: Next.js app with pages and WS client.
**Independent Test**: Start session, open WS, see FIRST RUNNER greeting; navigate lesson/quiz flows.

### Implementation
- [ ] T030 [P] task/frontend-skeleton: scaffold Next.js with pages (index, dashboard, chat, lesson, quiz, admin)
- [ ] T031 [P] Components: ChatClient, TavilyCard, QuizQuestion, ProgressBar
- [ ] T032 WS connect and render loop; show loading placeholders and split long lessons

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T033 Documentation updates in `docs/`
- [ ] T034 Observability dashboards and alerts for RAG and agent errors
- [ ] T035 Security hardening and secret management validation

## Dependencies & Execution Order

- Foundational (Phase 2) blocks all user stories.
- US1 → independent after Phase 2. US2 depends on session state; US3/US4 depend on agents and RAG tools; US5 depends on core agents.
- RAG worker (Phase 8) can progress in parallel once models and DB are ready.
- Frontend (Phase 9) after WS and start endpoint are functional.

## Parallel Examples

- Launch `T019` and `T020` in parallel (different files) for RAG retrieval.
- Run `T027` and `T028` in parallel for indexing setup and worker.

## Implementation Strategy

- MVP: Complete Phases 1–3 (US1) then validate.
- Incremental: Add US2 → US3 → US4 → US5; integrate RAG worker; then frontend skeleton.
