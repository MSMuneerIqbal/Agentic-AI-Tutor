# Tutor GPT Constitution
<!--
Sync Impact Report
Version change: 1.0.0 → 2.0.0
Modified principles: none
Added sections: none
Removed sections: none
Templates requiring updates:
✅ .specify/templates/plan-template.md (no changes required)
✅ .specify/templates/spec-template.md (no changes required)
✅ .specify/templates/tasks-template.md (no changes required)
Follow-ups:
None.
-->

## Core Principles

### I. MCP‑First and Gemini‑Only (NON‑NEGOTIABLE)
All live search, documentation retrieval, and UI testing MUST use registered MCP tools: TAVILY (web), Context7 (docs/code libraries), and Playwright (browser). Do NOT implement static crawling or scraping. All model calls MUST use Gemini models configured via `GEMINI_BASE_URL` and `GEMINI_API_KEY`. Prompts are loaded dynamically at runtime.

### II. Backend‑First & Agentic Architecture
Deliver a complete backend before frontend. Agents are autonomous objects defined with typed tools, running on the backend using the Agents SDK. Frontend (Next.js) consumes backend APIs and is added after stable agent capabilities exist.

### III. Prompt‑as‑Config (Six‑Part)
Prompts are configuration files, not code constants. Use a Six‑Part pattern and store under `app/agents_prompts/`. Load at startup and support hot‑reload in development. Version prompts via PRs and maintain `prompts/CHANGELOG.md`.

### IV. Guardrails & Validation
Use Agents SDK guardrails (input, output, and tripwires) to validate all agent interactions. On any trigger: sanitize output, return a user‑friendly fallback, and log a non‑sensitive record. Never echo secrets or PII.

### V. Secrets & Privacy by Design
Use a secret manager (Render Secrets). Never hardcode or log secrets. Store only necessary user content. Respect copyright by returning minimal snippets with citations and metadata; avoid storing full copyrighted text unless permitted.

### VI. Test‑Driven Delivery & Observability
Adopt TDD with CI gates: write failing tests, implement to green, then refactor. Enforce coverage thresholds and block PRs on failures. Emit structured JSON logs and metrics for latency, agent errors, guardrail triggers, and tool errors; alert on SLO breaches.

## Architecture & Operational Rules
**Platform**
- FastAPI backend; Next.js frontend. Use Uvicorn in development and Uvicorn+Gunicorn for production as needed.

**Agents & Tools**
- Agents live in `app/agents/`; tools in `app/tools/`. Prompts live in `app/agents_prompts/` (Six‑Part format).
- MCP tools: TAVILY (web search/cache), Context7 (library/docs fetching), Playwright (UI testing); always prefer these over ad‑hoc code.

**Data & Storage**
- Durable DB: MySQL (or Postgres if required) for users, profiles, plans, quiz_attempts, directives, audit logs.
- Session: Redis for `session:{id}` state, `last_messages` (size‑limited), `tavily_cache:{hash}` with 1‑hour TTL, and rate counters.
- RAG: Pinecone vector index using Gemini embeddings; store only metadata unless explicit permission to persist full text.

**Security & Compliance**
- Secrets via Render Environment/Secrets. No secrets in code or logs. PII minimization. Clear audit logging for agent actions and guardrail events.

## Development Workflow, Tooling, and Quality Gates
**Development & Governance**
- Use ADRs for significant architecture decisions; store in `docs/adr/`. One coherent change per PR.
- CI gates PR merges: tests, coverage, lint/format, Docker build, and policy checks must pass.
- Prompts updated via PRs and versioned; maintain `prompts/CHANGELOG.md`.

**Testing & CI**
- TDD workflow; include guardrail tests. Target coverage ≥ 80% unless otherwise specified.
- Mock network calls in offline CI by default.

**Tooling & Style**
- Python: black + isort + flake8; type annotations and Pydantic for public interfaces.
- JavaScript/TypeScript: prettier + eslint; Tailwind recommended for UI.
- Pre‑commit hooks and GitHub Actions for CI.

**Deployment & Infra**
- Deploy on Render as separate services for backend, worker (indexer), and frontend if needed.
- Daily DB backups with 30‑day retention. Metrics and alerting for latency, error rates, guardrail rejects, and tool failures.

**Exceptions & Reviews**
- Any exception to this constitution requires an ADR with rationale, scope, and review date. Review the constitution at each major milestone.

**Daily Checklist**
- Update spec before coding → write failing tests → implement → run tests → refactor → commit a coherent unit → open PR → add ADR if architecture changed.

## Governance
**Scope & Supremacy**
- This constitution sets non‑negotiable standards for architecture, safety, and delivery. Conflicts resolve in favor of this document.

**Amendment Procedure**
- Propose via PR with change summary and migration plan. Require approval from maintainers. Create or update ADRs for material architecture changes. On merge, bump constitution version per semantic rules and update review cadences if needed.

**Versioning Policy**
- Semantic: MAJOR (backward‑incompatible governance changes), MINOR (new or materially expanded sections), PATCH (clarifications or wording fixes).

**Compliance Reviews**
- During `/sp.plan` and PR reviews, verify compliance with Core Principles and Architecture & Operational Rules. Non‑compliance requires explicit ADR plus mitigation plan.

**Observability & Enforcement**
- Track CI pass/fail rates, guardrail triggers, tool failures, and SLOs. Alerts must notify owners. Repeated violations prompt a governance review.

**Version**: 2.0.0 | **Ratified**: 2025-10-09 | **Last Amended**: 2025-10-09
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
