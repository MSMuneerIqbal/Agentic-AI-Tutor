---
description: "Task list for agent layer implementation"
---

# Tasks: Agent Layer Implementation

**Input**: Design documents from `/specs/001-specify-agents-only/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Created**: 2025-10-09

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Backend structure**: `/backend/app/` at repository root

<!-- 
  ============================================================================

  The tasks below implement the feature requirements from the specification.
  Tasks are organized by user story to enable independent implementation and testing.
  
  Each user story can be implemented and tested independently to deliver value incrementally.
  
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in `/backend/app/`
- [X] T002 Initialize Python 3.11 project with uv, FastAPI, OpenAI Agents SDK, SQLAlchemy, Redis-py, Pydantic, pytest dependencies
- [X] T003 [P] Configure linting and formatting tools (black, flake8, mypy)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Setup OpenAI Agents SDK for all agent implementations
- [ ] T005 [P] Configure MCP client for TAVILY integration with Tutor agent (app startup)
- [ ] T006 [P] Setup guardrails and validation for user-facing agent outputs
- [ ] T007 Create base Pydantic models (AgentRequest, AgentResponse) in `/backend/app/models/pydantic_models.py`
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management (avoid direct .env reads in production)
- [ ] T010 Define input/output contracts and failure modes for agents
- [ ] T011 Setup Agent Envelope: AgentRequest / AgentResponse framework
- [ ] T012 [P] Setup MySQL database models for entities in `/backend/app/db/models.py`
- [ ] T013 [P] Setup Redis connection and session management
- [ ] T014 Setup uv package manager integration

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Initial Student Assessment (Priority: P1) 🎯 MVP

**Goal**: Enable new students to complete an initial assessment to determine their knowledge level and learning preferences

**Independent Test**: The Assessment agent can conduct the 5-question assessment independently, save the profile to MySQL and Redis, and provide a complete student profile for other agents to use.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T015 [P] [US1] Contract test for assessment endpoint in `/backend/app/tests/contract/test_assessment.py`
- [ ] T016 [P] [US1] Integration test for assessment flow in `/backend/app/tests/integration/test_assessment_flow.py`
- [ ] T017 [P] [US1] Unit test for assessment service in `/backend/app/tests/unit/test_assessment.py`

### Implementation for User Story 1

- [ ] T018 [P] [US1] Create Student Profile model in `/backend/app/db/models.py` (requires T012)
- [ ] T019 [P] [US1] Create Assessment model in `/backend/app/db/models.py` (requires T012)
- [ ] T020 [US1] Implement Assessment service in `/backend/app/services/agents/assessment.py` (depends on T018, T019)
- [ ] T021 [US1] Implement assessment endpoint in `/backend/app/api/v1/internal_agents.py`
- [ ] T022 [US1] Add validation and error handling to assessment flow
- [ ] T023 [US1] Add logging for assessment operations
- [ ] T024 [US1] Implement 5-question assessment logic with sequential presentation

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Personalized Lesson Planning (Priority: P2)

**Goal**: Create study plans based on student profiles

**Independent Test**: The Planning agent can generate a study plan based on a student profile, save it for future reference, and make it human-readable for verification.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T025 [P] [US2] Contract test for planning endpoint in `/backend/app/tests/contract/test_planning.py`
- [ ] T026 [P] [US2] Integration test for planning flow in `/backend/app/tests/integration/test_planning_flow.py`
- [ ] T027 [P] [US2] Unit test for planning service in `/backend/app/tests/unit/test_planning.py`

### Implementation for User Story 2

- [ ] T028 [P] [US2] Create Study Plan model in `/backend/app/db/models.py`
- [ ] T029 [US2] Implement Planning service in `/backend/app/services/agents/planning.py`
- [ ] T030 [US2] Implement planning endpoint in `/backend/app/api/v1/internal_agents.py`
- [ ] T031 [US2] Integrate with User Story 1 components (student profile access)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Interactive Tutoring Session (Priority: P3)

**Goal**: Provide personalized instruction in three modes (TEACH, Q&A, RE-TEACH) with TAVILY integration

**Independent Test**: The Tutor agent can provide lessons with intro, explanation, example, and exercise in any of its three modes, greet users appropriately, and safely incorporate TAVILY results (≤150 chars).

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T032 [P] [US3] Contract test for tutor endpoint in `/backend/app/tests/contract/test_tutor.py`
- [ ] T033 [P] [US3] Integration test for tutor flow in `/backend/app/tests/integration/test_tutor_flow.py`
- [ ] T034 [P] [US3] Unit test for tutor greeting behavior in `/backend/app/tests/unit/test_tutor_greeting.py`
- [ ] T035 [P] [US3] Unit test for tutor TAVILY integration in `/backend/app/tests/unit/test_tutor_tavily.py`

### Implementation for User Story 3

- [ ] T036 [P] [US3] Create Lesson Content model in `/backend/app/db/models.py`
- [ ] T037 [US3] Implement Tavily wrapper service in `/backend/app/services/tavily_wrapper.py`
- [ ] T038 [US3] Implement Tutor service in `/backend/app/services/agents/tutor.py`
- [ ] T039 [US3] Implement tutor endpoint in `/backend/app/api/v1/internal_agents.py`
- [ ] T040 [US3] Integrate with Tavily wrapper and ensure ≤150 char summaries
- [ ] T041 [US3] Add appropriate guardrails for Tavily results
- [ ] T042 [US3] Implement three modes (TEACH, Q&A, RE-TEACH) in Tutor agent
- [ ] T043 [US3] Implement user greeting with name retrieval

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Additional Agents (Quiz & Feedback) - Lower Priority

### Tests for Additional Agents (OPTIONAL - only if tests requested) ⚠️

- [ ] T044 [P] [QA] Unit test for quiz agent in `/backend/app/tests/unit/test_quiz.py`
- [ ] T045 [P] [FB] Unit test for feedback agent in `/backend/app/tests/unit/test_feedback.py`

### Implementation for Additional Agents

- [ ] T046 [QA] Implement Quiz agent in `/backend/app/services/agents/quiz.py`
- [ ] T047 [FB] Implement Feedback agent in `/backend/app/services/agents/feedback.py`
- [ ] T048 [O] Implement Orchestrator agent in `/backend/app/services/orchestrator.py`
- [ ] T049 [QA] Add quiz endpoints to `/backend/app/api/v1/internal_agents.py`
- [ ] T050 [FB] Add feedback endpoints to `/backend/app/api/v1/internal_agents.py`
- [ ] T051 [O] Implement routing logic for full flow (GREETING→ASSESSING→...)

---

## Phase 7: Compliance & Quality Features

### FERPA/COPPA Compliance Tasks

- [ ] T052 Implement age verification for minors in `/backend/app/services/verification.py`
- [ ] T053 Add parental consent functionality for student accounts
- [ ] T054 Implement data access controls per FERPA requirements

### WCAG 2.1 AA Compliance Tasks

- [ ] T055 Implement accessibility features in API responses
- [ ] T056 Add ARIA labels and semantic structure to API data
- [ ] T057 Ensure proper contrast and text alternatives in content

### Data Retention Policy Tasks

- [ ] T058 Implement data retention policy (1 year after last activity) in `/backend/app/services/data_retention.py`
- [ ] T059 Create background job for automatic data deletion
- [ ] T060 Add last_activity tracking to student profiles

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T061 [P] Documentation updates in `/backend/app/docs/`
- [ ] T062 Code cleanup and refactoring
- [ ] T063 Performance optimization across all stories
- [ ] T064 [P] Ensure ≥90% test coverage for critical agent modules (Tutor, Orchestrator)
- [ ] T065 Security hardening - validate no secrets are logged
- [ ] T066 Run quickstart.md validation
- [ ] T067 Verify MySQL is used only for user data and Redis only for session memory
- [ ] T068 Implement security scanning in CI/CD

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Additional Agents (Phase 6)**: Depends on foundational phase and core user stories
- **Compliance Features (Phase 7)**: Can run in parallel with other phases after foundational
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for assessment endpoint in /backend/app/tests/contract/test_assessment.py"
Task: "Integration test for assessment flow in /backend/app/tests/integration/test_assessment_flow.py"
Task: "Unit test for assessment service in /backend/app/tests/unit/test_assessment.py"

# Launch all models for User Story 1 together:
Task: "Create Student Profile model in /backend/app/db/models.py"
Task: "Create Assessment model in /backend/app/db/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (if TDD approach used)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence