# Stack and Coding Guide

## Technology Stack

- Backend: FastAPI, Uvicorn/Gunicorn, OpenAI Agents SDK (Python)
- LLM/Embeddings: Gemini (via `GEMINI_BASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `EMBEDDING_MODEL`)
- Storage: MySQL (SQLAlchemy async), Redis, Pinecone (vectors)
- Frontend: Next.js (TypeScript), WebSocket client
- Observability: JSON logs, metrics (Prometheus-style or structured logs), alerts
- Testing: pytest, Playwright (MCP UI smoke), Contract/integration tests
- CI: pre-commit, ruff, pytest, Docker build

## Coding Standards

- Type hints on public interfaces (Pydantic models for I/O)
- Guardrails: register input/output/tripwires for all agents
- TDD: add minimal failing tests before implementing core flows
- Secrets only via environment; never hardcode
- Small, composable modules; no deep coupling

## Directory Layout (proposed)

```
backend/
  app/
    api/
    agents/
    tools/
    guards/
    models/
    services/
    core/
  tests/
frontend/
  app/
  components/
  lib/
```

## Feature Implementation Flow

1. Update spec if needed → `/sp.clarify` for gaps
2. `/sp.plan` updates plan, data model, contracts
3. `/sp.tasks` generates tasks per story
4. Implement in phases (backend first) following tasks
5. Add e2e/contract tests (WS greeting, RAG, guardrails)
6. Frontend skeleton after backend endpoints + WS are ready

## RAG Notes

- Use Gemini embeddings; document model name and index dimension
- Chunk 400–600 tokens with ~20% overlap
- Return snippet ≤400 tokens + citations; cache results 1h in Redis

## MCP Usage

- TAVILY for live examples; Context7 for docs; Playwright for UI smoke test

## Env Vars

See `quickstart.md` for full list and setup.
