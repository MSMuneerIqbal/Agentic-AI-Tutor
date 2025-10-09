# Tasks: Backend-first, agentic Tutor GPT flow

**Input**: Design documents from `/specs/001-backend-first-agentic/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Initialize backend project structure under `backend/` and `frontend/`
- [X] T002 Add Python environment and dependencies via `uv` (FastAPI, Agents SDK, SQLAlchemy async, Redis, Pinecone, httpx, pytest, ruff)
- [X] T003 Add Node/Next.js scaffolding with `frontend/` baseline (no pages yet)
- [X] T004 [P] Add lint/format config (ruff, black/isort, eslint/prettier) and pre-commit hooks
- [X] T005 Create `.env.sample` with required variables (Gemini, DB, Redis, Pinecone, Secret, Port)

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T006 Setup database engine and base models per `data-model.md` in `backend/app/models/`
- [ ] T007 [P] Configure Redis client and session store utilities in `backend/app/core/redis.py`
- [ ] T008 [P] Configure Agents SDK (Gemini LLM + embeddings) and guardrails in `backend/app/agents/`
- [ ] T009 Create API app skeleton with FastAPI, routers, error handlers in `backend/app/api/__init__.py`
- [ ] T010 Configure structured JSON logging and metrics stubs
- [ ] T011 Add WebSocket endpoint skeleton `/ws/sessions/{session_id}`
- [ ] T012 Add REST endpoint skeleton `POST /sessions/start`

## Phase 2A: Core Tests, Guardrails, and MCP UI

- [ ] T-GU-001 | tests/ws_greeting_e2e
  - Title: WebSocket Greeting E2E test (GREETING → Assessment/Tutor)
  - Description: End-to-end test opens WS to `/ws/sessions/{id}`, triggers FIRST RUNNER (backend sends "hello"), asserts frontend receives single contextual greeting message matching schema {type, agent, text, timestamp}. Mock Gemini & tools in CI; run Orchestrator and session state.
  - Acceptance: WS opens; greeting within 5s; JSON schema matches; on simulated Gemini timeout, safe fallback greeting is returned.
  - Priority: HIGH
- [ ] T-GU-002 | tests/rag_contract
  - Title: RAG retrieval contract test (rag_tool.retrieve)
  - Description: Unit/integration test calls `rag_tool.retrieve(query)` with sample indexed vectors (test namespace or mock). Asserts list of `{chunk_id, text_snippet<=400 tokens, metadata:{title,url,source_type}}` and Redis TTL cache.
  - Acceptance: returns ≤k items; required metadata present; snippet ≤400 tokens; Redis cache key created TTL ~3600s.
  - Priority: HIGH
- [ ] T-GU-003 | tests/guardrail_fallback
  - Title: Guardrail fallback & logging test
  - Description: Simulate output guardrail violation; assert sanitized fallback response, `agent_logs` entry without secrets.
  - Acceptance: sanitized response delivered; `agent_logs` entry exists; CI asserts log schema.
  - Priority: HIGH
- [ ] T-GU-004 | tests/reconnect_resume
  - Title: Reconnect & resume session test
  - Description: Disconnect mid-session; reconnect with same session_id; assert resume state and context.
  - Acceptance: WS receives resumed-state greeting; session state matches Redis/MySQL snapshot.
  - Priority: MEDIUM
- [ ] T-GU-005 | tests/playwright_greeting_smoke
  - Title: Playwright smoke test for WS greeting (MCP UI test)
  - Description: Use Playwright to open frontend chat, call `/sessions/start`, open WS, assert greeting card appears; satisfies MCP UI test requirement.
  - Acceptance: Greeting card appears with expected agent name/options within 8s; failures logged as MCP/Playwright failures.
  - Priority: HIGH
- [ ] T-CON-001 | constitution/playwright_task
  - Title: Ensure constitution rule: Playwright UI test present
  - Description: Add Playwright smoke into CI to satisfy MCP UI testing requirement; reference T-GU-005.
  - Acceptance: CI runs Playwright test; docs mention constitutional check.
  - Priority: HIGH
- [ ] T-SEC-001 | guardrail/policy_task
  - Title: Guardrail policy implementation task
  - Description: Implement guardrail schema definitions; register input/output guardrails for all agents; create minimal e2e to validate fallback (T-GU-003).
  - Acceptance: Guardrails present for assessment/tutor/quiz; tests pass.
  - Priority: HIGH

## Phase 2B: Observability & Metrics

- [ ] T-OBS-001 | metrics/emit_core
  - Title: Emit core metrics & dashboards
  - Description: Instrument request latency (per endpoint), p95 for lesson generation, guardrail_trigger_count, tavily_errors_count, pinecone_query_latency, sessions_active. Expose Prometheus endpoint or structured logs.
  - Acceptance: metrics exported and testable; p95 collector for lesson generation present.
  - Priority: HIGH
- [ ] T-OBS-002 | metrics/alerts
  - Title: Alerts for tool/guardrail failures
  - Description: Alert rules: guardrail_reject_rate > X%/5m, Pinecone error rate >1%, Gemini timeout spike. Document runbook.
  - Acceptance: alert definitions in docs and runbook snippet in `docs/ops`.
  - Priority: MEDIUM

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
- [ ] T-DF-001 | quiz/length_policy_test
  - Title: Quiz length bounded-adaptive policy unit tests
  - Description: Unit tests assert 15–20 based on profiles; early stop when mastery detected.
  - Acceptance: covers ≥3 profiles; asserts chosen length & early stop.
  - Priority: MEDIUM

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
- [ ] T-RAG-001 | pinecone/embedding_model_and_index
  - Title: Specify embedding model and compute index dimension
  - Description: Document Gemini embedding model (e.g., `gemini-embedding-1.0`). Compute vector dimension from model metadata; validate Pinecone index settings.
  - Acceptance: plan.md updated with `EMBEDDING_MODEL=gemini-embedding-1.0`; index script verifies dimension match.
  - Priority: HIGH
- [ ] T027 [P] task/pinecone-setup: index creation script, embedding wrapper, chunker
- [ ] T028 [P] task/index-worker: background worker to run indexing jobs and emit status to MySQL
- [ ] T029 task/rag-api: implement `POST /api/v1/rag/index` endpoint to enqueue jobs
- [ ] T-RAG-002 | pinecone/indexer_worker
  - Title: Indexing worker & indexing-status endpoint
  - Description: Implement background indexer; add `GET /api/v1/rag/index/{job_id}` to return status.
  - Acceptance: job states (queued→running→done/failed); status endpoint returns job metadata and vector counts.
  - Priority: HIGH

## Phase 9: Frontend Skeleton & WS client

**Goal**: Next.js app with pages and WS client.
**Independent Test**: Start session, open WS, see FIRST RUNNER greeting; navigate lesson/quiz flows.

### Implementation
- [ ] T030 [P] task/frontend-skeleton: scaffold Next.js with pages (index, dashboard, chat, lesson, quiz, admin)
- [ ] T031 [P] Components: ChatClient, TavilyCard, QuizQuestion, ProgressBar
- [ ] T032 WS connect and render loop; show loading placeholders and split long lessons
- [ ] T-UX-001 | admin/indexing_status_page
  - Title: Admin page: Indexing job status
  - Description: Frontend admin component queries indexing-status endpoint and displays job history, vector counts, errors.
  - Acceptance: Admin page lists jobs with status and links to logs.
  - Priority: LOW

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
