---
stage: constitution
title: Tutor GPT constitution authored
date: 2025-10-09
---

## Full Input

```
/sp.constitution 

Tutor GPT — an agentic autonomous tutor system built on a backend-first architecture using Agents SDK + Gemini; MySQL for durable data; Redis for session state; Pinecone for RAG; TAVILY + Context7 + Playwright as MCPs.

Main rule (non-negotiable)

Always use the MCPs provided (Context7, TAVILY, Playwright) for live search, documentation retrieval, and UI testing. Do not implement static crawling or scraping. Use dynamic prompts loaded at runtime. Use Gemini models only (configured via GEMINI_BASE_URL & GEMINI_API_KEY).

Core principles (short)

Backend-first & agentic: Build a complete backend with Agent objects and tools first; frontend follows. Agents are fully autonomous objects that call typed tools.

Prompt-as-config: Prompts are configuration files (Six-Part). Load them at startup; support hot-reload in dev. Prompts are not code constants.

Guardrails & Validation: Use Agents SDK guardrails (input/output/tripwires) to validate all agent outputs. On guardrail triggers, return sanitized messaging to user and log event.

Secrets & privacy: Use a secret manager (Render secrets). Never log secrets. Limit stored user content to what’s necessary. Respect copyright: show snippets + citations only.

Test & CI: TDD approach with coverage targets and CI gating PR merges. Include guardrail tests.

Observability: Structured JSON logs; metrics for latency, agent errors, guardrail triggers, and tool errors.

Architecture rules (short)

Use FastAPI (backend) + Next.js (frontend). Use Uvicorn + Gunicorn for production if needed.

Use MySQL/Postgres for durable storage; Redis for ephemeral session storage.

Use Pinecone for RAG with Gemini embeddings.

Agents are defined in app/agents/ and tools in app/tools/.

Prompts live in app/agents_prompts/ and follow the Six-Part pattern.

Data & storage rules (short)

MySQL: users, profiles, plans, quiz_attempts, directives, audit logs.

Redis: session:{id} state, last_messages (size-limited), tavily_cache:{hash} TTL 1 hour, rate counters.

Pinecone: vector index; store metadata only (do not store full copyrighted text unless permitted).

Guardrail & safety rules

Register input & output guardrails in all agents using the Agents SDK.

Define forbidden content lists and tripwires (e.g., secret leakage, PII exfiltration).

On guardrail breach: sanitize response, send user-friendly fallback, and write a record to agent_logs with no secret content.

Development & workflow rules

Use ADRs for all architecture changes. Store ADRs in /docs/adr/.

One coherent change per commit and PR. PRs must pass CI and tests before merge.

Prompts updated via PRs and versioned in Git. Add a prompts/CHANGELOG.md for prompt edits.

Tooling & style rules

Python: black + isort + flake8. Use type annotations and Pydantic models for public interfaces.

JS: prettier + eslint. Tailwind recommended for UI.

Add pre-commit hooks and GitHub Actions for CI.

Deployment & infra rules

Use Render for web services. Secrets via Render Environment/Secrets.

Separate services for backend, worker (indexer), and frontend if needed.

Daily backups for DB with 30-day retention.

Metrics & alerting for latency, error rates, guardrail reject rates, and tool failures.

Exceptions & review

Any exception to the constitution requires an ADR that explains the reason, scope, and review date.

Conduct a constitution review at each major milestone.

Daily checklist (developer)

Update spec before coding.

Write failing tests for new feature.

Implement feature → run tests → refactor.

Commit one coherent unit and push PR.

Add ADR if architectural change.

Short appendix: Dynamic prompts & MCP usage note

Always prefer calling a registered MCP tool (TAVILY/Context7) before generating long examples. Document allowed domains and show citations.

Prompts should include markers for when to call tools (e.g., [CALL_RAG], [CALL_TAVILY]) and expect tool results in a defined schema.
```

## Actions Taken

- Authored constitution in `.specify/memory/constitution.md` (v1.0.0) with Sync Impact Report.
- Aligned Constitution Check gates in `.specify/templates/plan-template.md`.
- Made tests mandatory in `.specify/templates/tasks-template.md` per TDD policy.
- Synced public copy to `docs/constitution.md`.

## Notes

- No `.specify/templates/commands/sp.phr.md` template found; recorded PHR directly under `docs/prompts/`.

