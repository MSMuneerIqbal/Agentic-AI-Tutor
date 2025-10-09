# Quickstart: Backend-first, agentic Tutor GPT

## Environment

Copy `.env.sample` and set:

```
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_MODEL=text-embedding-004
DATABASE_URL=mysql+asyncmy://user:pass@mysql:3306/tutor_db
REDIS_URL=redis://redis:6379/0
PINECONE_API_KEY=...
PINECONE_ENV=...
SECRET_KEY=...
PORT=8000
```

## Install & Run (backend)

```
uv venv && . .venv/Scripts/activate
uv init --python 3.12
uv add fastapi "uvicorn[standard]" pydantic python-dotenv httpx pytest ruff openai-agents aiomysql sqlalchemy[asyncio] redis pinecone-client
uv run uvicorn app.main:app --reload --port %PORT%
```

## Endpoints
- POST `/sessions/start` → `{ session_id }`
- WS `/ws/sessions/{session_id}` → initial greeting + loop
- POST `/api/v1/rag/index` → enqueue indexing job
- POST `/api/v1/rag/retrieve` → top-k chunks with citations

## Frontend
- Next.js app uses `NEXT_PUBLIC_API_URL` to call backend
- Open WS after `/sessions/start`, render FIRST RUNNER

## Notes
- MCP tools for live search/docs/UI testing
- Respect privacy; return snippets + citations
