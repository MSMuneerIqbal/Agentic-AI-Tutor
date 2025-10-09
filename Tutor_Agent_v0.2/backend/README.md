# Tutor GPT Backend

Backend-first agentic tutoring system powered by Agents SDK and Gemini.

## Setup

```bash
# Install dependencies
uv sync

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix

# Copy env sample and configure
cp ../.env.sample .env

# Run development server
uvicorn app.main:app --reload
```

## Structure

- `app/agents/` - Agent implementations (Orchestrator, Assessment, Planning, Tutor, Quiz, Feedback)
- `app/tools/` - Agent tools (RAG, TAVILY, DB)
- `app/guards/` - Guardrails and validation
- `app/api/` - FastAPI routes and WebSocket handlers
- `app/models/` - SQLAlchemy models
- `app/services/` - Business logic services
- `app/core/` - Core utilities (Redis, config, logging)
- `tests/` - Unit, integration, and contract tests

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

