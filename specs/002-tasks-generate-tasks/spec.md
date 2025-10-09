# Feature Specification: Agent Layer Implementation

**Feature Branch**: `001-specify-agents-only`  
**Created**: 2025-10-09  
**Status**: Draft  
**Input**: User description: "/specify — Agents-only (What & Why) — short & clear One-line goal Build the agent layer (Orchestrator, Assessment, Planning, Tutor, Quiz, Feedback) using OpenAI Agents SDK. Tutor will call TAVILY via MCP for live examples. No RAG yet. Use MySQL for user data and Redis for session memory. Why Agents give a clear, testable flow for tutoring: assess → plan → teach → quiz → remediate → feedback. TAVILY makes lessons current and interesting by finding real projects and short notes during the lesson. Building agents first keeps the core logic separate and makes frontend later simpler. Key rules (short) Agents only with OpenAI Agents SDK. No other agent frameworks. TAVILY only via MCP and only inside the Tutor agent. No separate tavily service file. MCP client created at app startup and reused. No RAG yet. Add RAG later when agents are stable. MySQL for long-term user data; Redis for session and short-term memory. Tests first (TDD) for every agent (unit + integration). All user-facing text passes SDK guardrails + app validation. Agents & acceptance (short) Orchestrator — routes actions, maintains state in Redis, logs trace_id. Accept: routes full flow (GREETING→ASSESSING→...). Assessment — asks 5 fixed Qs (one per turn), returns profile JSON. Accept: profile saved in MySQL + Redis. Planning — creates a small study plan. Accept: plan saved and human-readable. Tutor — three modes (TEACH, Q&A, RE-TEACH). Greets user first. May call TAVILY via MCP for up to 3 results. Accept: lesson with intro, explanation, example, exercise; greets; TAVILY results are short ≤150 chars and safe. Quiz — 1-question-at-a-time quizzes; hint support (max 2); pass ≥70%. Accept: compute score, identify weak topics. Feedback — collects ratings/comments; produces teaching directives in profile. Accept: directives stored and used by Tutor. all agents can handoff to each others"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Initial Student Assessment (Priority: P1)

A new student begins their tutoring session by completing an initial assessment to determine their knowledge level and learning preferences. The Assessment agent asks 5 fixed questions one at a time, collecting responses to build a student profile.

**Why this priority**: Establishing the student's baseline knowledge is essential for creating effective personalized learning experiences throughout the system.

**Independent Test**: The Assessment agent can conduct the 5-question assessment independently, save the profile to MySQL and Redis, and provide a complete student profile for other agents to use.

**Acceptance Scenarios**:

1. **Given** a new student starts a session, **When** the Assessment agent presents each question sequentially, **Then** the student can answer each question and the system stores their responses
2. **Given** all 5 questions have been answered, **When** the assessment completes, **Then** a complete student profile is saved to both MySQL and Redis

---

### User Story 2 - Personalized Lesson Planning (Priority: P2)

Based on the student's assessment profile, the Planning agent creates a small, human-readable study plan tailored to the student's knowledge gaps and learning preferences.

**Why this priority**: After understanding the student's baseline, the next critical step is creating a personalized learning path to address their specific needs.

**Independent Test**: The Planning agent can generate a study plan based on a student profile, save it for future reference, and make it human-readable for verification.

**Acceptance Scenarios**:

1. **Given** a completed student profile exists, **When** the Planning agent creates a study plan, **Then** a small, human-readable plan is generated and saved

---

### User Story 3 - Interactive Tutoring Session (Priority: P3)

The Tutor agent provides personalized instruction in three modes (TEACH, Q&A, RE-TEACH), greeting the user first and potentially calling TAVILY via MCP for live examples and current information.

**Why this priority**: This is the core teaching functionality that delivers the primary value to students after initial assessment and planning.

**Independent Test**: The Tutor agent can provide lessons with intro, explanation, example, and exercise in any of its three modes, greet users appropriately, and safely incorporate TAVILY results (≤150 chars).

**Acceptance Scenarios**:

1. **Given** a student starts a tutoring session, **When** the Tutor agent greets them and provides instruction in TEACH mode, **Then** they receive a complete lesson with intro, explanation, example, and exercise
2. **Given** a student is in a tutoring session, **When** the Tutor agent accesses TAVILY via MCP, **Then** the returned results are ≤150 characters, safe, and relevant to the lesson
3. **Given** a student requests Q&A or RE-TEACH, **When** the Tutor agent switches modes, **Then** the session adapts to the requested mode

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when the TAVILY service is temporarily unavailable during a lesson?
- How does the system handle students who consistently score below the 70% passing threshold?
- What happens when a student abandons a session at different stages of the process?
- How does the system handle multiple concurrent sessions for the same student?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST use the OpenAI Agents SDK for all agent implementations (Orchestrator, Assessment, Planning, Tutor, Quiz, Feedback)
- **FR-002**: TAVILY MUST be accessed only via MCP client attached to Tutor agent (no direct access from other agents or separate service file)
- **FR-003**: All user-facing agent outputs MUST pass OpenAI Agents SDK AND app-level validation
- **FR-004**: System MUST NOT read .env files directly in production or log secrets
- **FR-005**: Agents MUST be able to handoff to each other using standard Agent Envelope: AgentRequest / AgentResponse
- **FR-006**: System MUST use MySQL for long-term user data storage and Redis for session and short-term memory
- **FR-007**: The Orchestrator agent MUST route actions, maintain state in Redis, and log trace_id for all operations
- **FR-008**: The Assessment agent MUST ask 5 fixed questions one at a time and return a complete profile JSON
- **FR-009**: The Assessment agent MUST save the student profile to both MySQL and Redis
- **FR-010**: The Planning agent MUST create a small, human-readable study plan
- **FR-011**: The Tutor agent MUST operate in three modes (TEACH, Q&A, RE-TEACH) and greet users first
- **FR-012**: The Tutor agent MUST call TAVILY via MCP for up to 3 results during lessons
- **FR-013**: The Tutor agent MUST provide lessons with intro, explanation, example, and exercise
- **FR-014**: TAVILY results used by Tutor agent MUST be ≤150 characters and safe
- **FR-015**: The Quiz agent MUST present 1 question at a time with hint support (max 2 hints)
- **FR-016**: The Quiz agent MUST compute scores and identify weak topics with a pass threshold of ≥70%
- **FR-017**: The Feedback agent MUST collect ratings and comments from students
- **FR-018**: The Feedback agent MUST produce teaching directives that are stored in the student profile
- **FR-019**: Teaching directives from the Feedback agent MUST be used by the Tutor agent
- **FR-020**: All agents MUST follow the TDD approach with unit and integration tests written first
- **FR-021**: System MUST comply with educational standards FERPA and COPPA for student data protection and parental consent
- **FR-022**: Student data MUST be retained for 1 year after last activity, then automatically deleted
- **FR-023**: When TAVILY service is unavailable, Tutor agent MUST continue lesson with generated content (no TAVILY)
- **FR-024**: System MUST meet WCAG 2.1 AA accessibility compliance standards

### Key Entities *(include if feature involves data)*

- **Student Profile**: Represents the student's knowledge level, learning preferences, assessment results, and study history; stored in both MySQL (long-term) and Redis (session)
- **Study Plan**: Customized learning path created for each student based on their profile; human-readable and stored for reference
- **Lesson Content**: Instructional material provided by the Tutor agent, including intro, explanation, example, and exercise components
- **Quiz Results**: Records of student performance on quizzes, including scores, weak topics identified, and hints used
- **Teaching Directives**: Feedback-generated instructions for improving the tutoring experience, stored in the student profile for use by the Tutor agent

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Students can complete the initial 5-question assessment in under 5 minutes
- **SC-002**: System generates personalized study plans within 30 seconds of assessment completion
- **SC-003**: At least 80% of students who complete a tutoring session report improved understanding of the subject matter
- **SC-004**: Tutor agent successfully retrieves and incorporates TAVILY results in at least 90% of lessons that request current examples
- **SC-005**: Students achieve a pass rate of ≥70% on quizzes after completing relevant tutoring sessions
- **SC-006**: System can handle 100 concurrent tutoring sessions without degradation in response time
- **SC-007**: Agents demonstrate ≥90% test coverage for critical modules through unit and integration tests

## Clarifications

### Session 2025-10-09

- Q: What specific security and privacy compliance requirements must the system satisfy? → A: Educational compliance (FERPA, COPPA)
- Q: For the Tutor agent's response time, what is the maximum acceptable latency for generating lesson content? → A: Best effort, no strict limits
- Q: How long should student data be retained in the system? → A: 1 year after last activity
- Q: When the TAVILY service is temporarily unavailable, how should the Tutor agent respond? → A: Continue lesson with generated content (no TAVILY)
- Q: What accessibility standards must the system support for students with disabilities? → A: WCAG 2.1 AA compliance