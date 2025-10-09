<!-- 
Sync Impact Report:
- Version change: 1.1.0 → 1.2.0
- Modified principles: 
  - Principle 1: Single implementation rule (updated)
  - Principle 2: TAVILY MCP usage (updated)  
  - Principle 3: MCP priority for external data (updated)
  - Principle 4: Guardrails (updated)
- Added sections: Tech Stack Requirements, RAG Implementation, Enhanced Security
- Removed sections: Minimal Infra for Agents-Only MVP (replaced with updated infrastructure section)
- Templates requiring updates: 
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ updated  
  - .specify/templates/tasks-template.md ✅ updated
- Follow-up TODOs: None
-->

# TuTor GPT Constitution

## Core Principles

### Single Implementation Rule
All agent implementations must use the OpenAI Agents SDK. No other agent frameworks, handcrafted LLM wrappers, or static prompt-only services are allowed without an ADR and admin approval.

### TAVILY MCP Usage
TAVILY MUST be used only via an MCP client attached to the Tutor agent (orchestrator may call Tutor which will call TAVILY). Do not create a top-level tavily.py service or expose TAVILY directly to frontend clients.

### MCP Priority for External Data
When external context is required:
First consult context7 (library docs, API signatures)
Then tavily via MCP (live repos, blog posts, short market notes)
playwright only for frontend test automation (if needed)

### Guardrails
All user-facing agent outputs must pass:
OpenAI Agents SDK guardrails (schema & safety)
App-level validation (length, blacklist, JSON schema)
If rejected, return a safe fallback message and log the reason (no secrets).

## Tech Stack Requirements
The project MUST use:
- uv package manager for dependency management and virtual environments
- Python 3.11+ as the minimum required version
- OpenAI Agents SDK for all agent implementations
- MCP servers for external service integration

## RAG Implementation
The system MAY incorporate RAG (Retrieval Augmented Generation) capabilities when appropriate for enhancing agent responses, but only after stability has been verified.

## Enhanced Security
- Agents MUST NOT read .env files directly in production environments
- Secrets MUST NOT be leaked to logs, console output, or external services
- All sensitive configuration MUST be managed through the deployment platform's secret manager
- Local development MAY use .env files but MUST NOT commit them to version control

## Testing Protocol
All code changes MUST pass comprehensive tests before merging:
- Unit tests with ≥90% coverage for critical modules
- Integration tests covering agent handoffs and data flow
- CI pipeline MUST block merge on any failing tests
- Security scanning MUST pass before merge

## Handoffs & Contracts
Each agent publishes an input/output contract (Pydantic models) and failure modes. Agents hand off via the standard Agent Envelope: AgentRequest / AgentResponse. Orchestrator must log trace_id for each handoff.

## Infrastructure
The system uses:
- MySQL for long-term user data storage
- Redis for session memory and caching
- RAG capabilities as appropriate for enhanced responses

## Single-Author Policy
Any deviation requires an ADR documenting the change, reasons, and a planned revert/review date.

## Governance
All implementations must comply with these principles. Deviations require Architectural Decision Record (ADR) with approval. Amendments must be documented with versioning, clear rationale, and migration plan when necessary. All PRs and code reviews must verify compliance with these principles.

**Version**: 1.2.0 | **Ratified**: 2025-10-09 | **Last Amended**: 2025-10-09
