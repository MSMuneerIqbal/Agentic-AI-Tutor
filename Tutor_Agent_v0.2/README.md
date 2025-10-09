# Tutor GPT - Agentic Tutoring System

Backend-first agentic tutoring system powered by OpenAI Agents SDK and Gemini.

## Overview

Tutor GPT is an autonomous AI tutor that:
- Conducts VARK-style learning assessments
- Creates personalized study plans
- Delivers interactive lessons with RAG-enhanced content
- Provides adaptive quizzes with hints and remediation
- Captures feedback for continuous improvement

## Architecture

- **Backend**: FastAPI + Agents SDK (Gemini) + MySQL + Redis + Pinecone
- **Frontend**: Next.js with WebSocket for real-time agent interactions
- **Agents**: Orchestrator, Assessment, Planning, Tutor, Quiz, Feedback
- **Tools**: RAG (Pinecone), TAVILY (live search), DB utilities
- **MCPs**: TAVILY, Context7, Playwright for testing

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- MySQL
- Redis
- Pinecone account
- Gemini API key

### Setup

1. **Clone and configure**
   ```bash
   # Copy environment template
   cp .env.sample .env
   # Edit .env with your credentials
   ```

2. **Backend setup**
   ```bash
   cd backend
   uv sync
   source .venv/bin/activate  # Unix
   # .venv\Scripts\activate  # Windows
   uvicorn app.main:app --reload
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
Tutor_Agent_v0.2/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── agents/    # Agent implementations
│   │   ├── tools/     # Agent tools (RAG, TAVILY, DB)
│   │   ├── guards/    # Guardrails
│   │   ├── api/       # REST + WebSocket endpoints
│   │   ├── models/    # SQLAlchemy models
│   │   ├── services/  # Business logic
│   │   └── core/      # Config, Redis, logging
│   └── tests/         # Unit, integration, contract tests
├── frontend/          # Next.js frontend
│   ├── app/           # Pages (App Router)
│   ├── components/    # React components
│   └── lib/           # Utilities
├── docs/              # Documentation
│   ├── architecture/
│   ├── developer-guides/
│   ├── api/
│   ├── adr/          # Architecture Decision Records
│   └── prompts/      # Prompt History Records
└── specs/            # Feature specifications
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
ruff check .
ruff format .

# Frontend linting
cd frontend
npm run lint
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Technology Stack & Coding Approach](docs/developer-guides/stack-and-coding.md)
- [API Endpoints](docs/api/endpoints-overview.md)
- [Coding Phases](docs/developer-guides/coding-phases.md)
- [Constitution](docs/constitution.md)

## Deployment

See deployment guides in `docs/deployment/` for:
- Render (backend)
- Vercel (frontend)
- Docker + Kubernetes

## License

MIT

## Contributing

See `docs/constitution.md` for project principles and development standards.

