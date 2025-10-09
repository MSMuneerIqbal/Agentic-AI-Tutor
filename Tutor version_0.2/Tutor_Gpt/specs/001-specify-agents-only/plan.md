# Implementation Plan: Agent Layer Implementation

**Branch**: `001-specify-agents-only` | **Date**: 2025-10-09 | **Spec**: [link](spec.md)
**Input**: Feature specification from `/specs/001-specify-agents-only/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build the agent layer (Orchestrator, Assessment, Planning, Tutor, Quiz, Feedback) using OpenAI Agents SDK. Tutor will call TAVILY via MCP for live examples. System must comply with educational standards FERPA and COPPA for student data protection. Implementation follows TDD approach with comprehensive test coverage. Student data retained for 1 year after last activity. The system will meet WCAG 2.1 AA accessibility compliance standards.

## Technical Context

**Language/Version**: Python 3.11+ (as required by constitution)  
**Primary Dependencies**: OpenAI Agents SDK, FastAPI, SQLAlchemy, Redis-py, Pydantic, pytest, uv (as required by constitution)  
**Storage**: MySQL (user data), Redis (session memory and caching)  
**Testing**: pytest with unit and integration tests  
**Target Platform**: Linux server (backend service)  
**Project Type**: web (backend service)  
**Performance Goals**: Handle 100 concurrent tutoring sessions; best effort approach for Tutor agent response time (no strict limits on generation)  
**Constraints**: <200ms p95 for internal agent communication, no secrets in logs, FERPA/COPPA compliance  
**Scale/Scope**: Support 10k students, 1M+ tutoring interactions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Agent Implementation Compliance
- [X] All agent implementations use the OpenAI Agents SDK (no other agent frameworks)
- [X] TAVILY MCP usage is only via MCP client attached to Tutor agent
- [X] External data follows priority: context7 → tavily via MCP → playwright for automation

### Guardrails & Security
- [X] All user-facing agent outputs pass OpenAI Agents SDK AND app-level validation
- [X] No secrets logged, and .env files not read directly in production
- [X] Proper fallback messages and error logging implemented

### Testing & Infrastructure
- [X] TDD approach implemented with ≥90% coverage for critical modules
- [X] Infrastructure follows approach: MySQL for user data, Redis for sessions
- [X] RAG implemented after stability verification (as per constitution update)

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```
/backend/app/
  core/
    config.py
    startup.py            # app startup: DB, Redis, Agent SDK provider, MCP client attach
  api/v1/
    internal_agents.py    # internal endpoints (X-Internal-Key)
  services/
    orchestrator.py
    agents/
      assessment.py
      planning.py
      tutor.py            # Tutor contains MCP usage and calls
      quiz.py
      feedback.py
    tavily_wrapper.py     # very small internal helper inside services (not top-level)
  models/
    pydantic_models.py
  db/
    models.py
    migrations/
  tests/
    unit/
    integration/
```

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |