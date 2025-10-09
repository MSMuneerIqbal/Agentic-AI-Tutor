# Implementation Plan: Backend-first, agentic Tutor GPT flow

**Branch**: `001-backend-first-agentic` | **Date**: 2025-10-09 | **Spec**: ../spec.md
**Input**: Feature specification from `/specs/001-backend-first-agentic/spec.md`

## Summary

Backend-first Tutor GPT with an Orchestrator and two-stage runner: an initial backend-initiated greeting, followed by a user loop. Assessment uses a short VARK-style questionnaire; quizzes are bounded-adaptive (15–20 Q). The system integrates Agents SDK (Gemini LLM + Gemini embeddings), MySQL (durable), Redis (session/cache), Pinecone (RAG), and TAVILY (live search). Next.js frontend connects via REST + WebSocket after backend is ready.

## Technical Context

**Language/Version**: Python 3.12 (backend), Node 20 (frontend)  
**Primary Dependencies**: FastAPI, Uvicorn/Gunicorn, OpenAI Agents SDK, Pydantic, SQLAlchemy (async), Redis client, Pinecone client, httpx, pytest, ruff, Next.js  
**Storage**: MySQL (users, profiles, plans, quiz_attempts, directives, audit logs); Redis (session state, caches); Pinecone (vectors)  
**Testing**: pytest (unit, integration, contract), Playwright for UI testing via MCP  
**Target Platform**: Render (backend/services), Vercel/Render (frontend)  
**Project Type**: Web application (backend + frontend)  
**Performance Goals**: initial p95 < 500ms for non-indexing endpoints; WS first-greet < 2s  
**Constraints**: Backend-first delivery; MCP-only for search/docs/UI; Gemini-only models  
**Scale/Scope**: Single-tenant MVP; namespaces in Pinecone per project/user if needed

## Constitution Check

- MCP Usage: Live search/docs/UI testing must use MCPs (TAVILY, Context7, Playwright).  
- Model Policy: Models are Gemini via `GEMINI_BASE_URL` and `GEMINI_API_KEY`.  
- Backend-First: Backend agent capabilities precede frontend.  
- Prompt-as-Config: Prompts under `app/agents_prompts/` (Six-Part), hot-reload in dev.  
- Guardrails: Input/output/tripwires configured; sanitize and log on trigger.  
- Data Stores: MySQL/Postgres durable; Redis sessions/counters/cache; Pinecone for RAG (metadata only).  
- Observability: JSON logs, metrics for latency, agent errors, guardrails, tool errors; alerting.  
- CI & Quality: TDD, coverage ≥ 80%, lint, tests, Docker build; offline CI mocks network.  
- Security: Secrets from Render; no secrets in code/logs.

Status: All gates satisfied by design; no violations.

## Project Structure

```
backend/
  app/
    agents/
    tools/
    guards/
    api/
    models/
    services/
    core/
  tests/
    unit/
    integration/
    contract/
frontend/
  app/ (Next.js)
  components/
  lib/
  tests/
```

**Structure Decision**: Two-project web app (`backend/`, `frontend/`) to separate concerns and deployments.

## Implementation Strategy

- Phase 1: Backend core (Agents, guardrails, sessions, RAG endpoints)  
- Phase 2: Indexing worker and Pinecone integration  
- Phase 3: Frontend skeleton and WS integration  
- Phase 4: Polish, metrics, admin

## APIs and Contracts (high-level)

- POST `/sessions/start` → { session_id }  
- WS `/ws/sessions/{session_id}` → initial greeting + loop  
- POST `/api/v1/rag/index` → enqueue indexing job  
- POST `/api/v1/rag/retrieve` → { query, k, filter } → top-k chunks + metadata

## Environment Configuration

```
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_MODEL=text-embedding-004
DATABASE_URL=mysql+asyncmy://user:pass@mysql:3306/tutor_db
REDIS_URL=redis://redis:6379/0
PINECONE_API_KEY=<PINECONE_KEY>
PINECONE_ENV=<PINECONE_ENV>
SECRET_KEY=<SECRET>
PORT=8000
```

## RAG Design (Pinecone)

- Embeddings: Gemini embeddings (`EMBEDDING_MODEL` recorded in config)  
- Index: dimension matches embeddings; namespace per tenant/project  
- Metadata schema: source_id, source_type, title, url, chunk_id, uploaded_by?, created_at  
- Chunking: ~400–600 tokens (or 1–2KB) with ~20% overlap  
- Storage: store chunk IDs and short excerpts in DB; full text only with consent in controlled storage  
- Indexing worker: async background job → extract → split → embed → upsert batches → record status  
- Retrieval: `rag_tool.retrieve(query, k=5, filter?)` → embed → query → return chunk text (≤400 tokens) + citations; Redis cache TTL 1h  
- Failover: proceed without RAG on errors; log for admin  
- Monitoring: job success/failure, vector counts, latencies, quota/usage

## Tools Wiring

- `tools/rag_tool.py`  
  - `index_documents(docs, namespace)`  
  - `retrieve(query, k=5, namespace=None, filter=None)`  
- Idempotent with retry/backoff; guardrail‑compatible outputs

## Frontend Scope

Pages: index, dashboard, chat, lesson, quiz, admin (optional)  
Components: ChatClient (WS), TavilyCard, QuizQuestion, ProgressBar  
Integration: call `/sessions/start`, open WS, render FIRST RUNNER; request examples via agent flow; show loading placeholders; split long lessons; prevent skipping quizzes.

## Parallel Opportunities

- Implement RAG endpoints and indexing worker in parallel  
- Frontend skeleton parallel after backend WS + start endpoint ready

## Notes & References

- Six‑Part prompts and context engineering patterns  
  - [Six‑Part Prompting Framework](https://github.com/panaversity/learn-low-code-agentic-ai/blob/main/00_prompt_engineering/six_part_prompting_framework.md)  
  - [Context Engineering Tutorial](https://github.com/panaversity/learn-low-code-agentic-ai/blob/main/00_prompt_engineering/context_engineering_tutorial.md)  
  - [Prompt Engineering Readme](https://github.com/panaversity/learn-low-code-agentic-ai/blob/main/00_prompt_engineering/readme.md)  
- OpenAI Agents SDK docs (tools, guardrails, sessions, orchestration): [link](https://openai.github.io/openai-agents-python/)
