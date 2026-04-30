# Tutor Agent — Backend

FastAPI backend for the AI tutoring system. Runs on Python 3.12+.

## Quick Start

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac / Linux

# Install dependencies
pip install -e .

# Copy env template and fill in your keys
copy .env.example .env

# Start dev server
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Required Environment Variables

See `.env.example` for the full list. Minimum to run:

```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pc-...
DATABASE_URL=mongodb+srv://...
PINECONE_INDEX_NAME=tutor-lms
```

## Structure

```
app/
├── main.py                  # FastAPI entry point
├── agents/                  # 6 AI agents + manager
│   ├── base.py              # BaseAgent with _call_llm() helper
│   ├── agent_manager.py     # routes messages, owns session state
│   ├── orchestrator.py
│   ├── assessment.py
│   ├── planning.py
│   ├── tutor.py
│   ├── quiz.py
│   └── feedback.py
├── api/routes/              # REST + WebSocket endpoints
├── core/
│   ├── config.py            # Settings from .env
│   ├── openai_manager.py    # chat_complete(), web_search(), generate_embedding()
│   ├── session_store.py     # MongoDB session storage
│   └── mongodb.py           # Beanie init
├── guards/                  # Input/output validation
├── models/                  # Pydantic / Beanie models
├── services/                # Business logic (rag_service, plan_service, profile_service)
└── tools/
    ├── rag.py               # Pinecone queries via OpenAI embeddings
    └── web_search.py        # OpenAI web_search_preview
```

## Testing

```bash
pytest                     # all tests
pytest --cov=app           # with coverage
```
