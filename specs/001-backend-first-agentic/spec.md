# Feature Specification: Backend-first, agentic Tutor GPT flow

**Feature Branch**: `001-backend-first-agentic`  
**Created**: 2025-10-09  
**Status**: Draft  
**Input**: User description: "/sp.specify Backend-first, agentic Tutor GPT flow — Orchestrator runs a two-stage runner (backend-initiated \"hello\" then user loop). Assessment uses VARK (5–12 Q). Quiz is dynamic (15–20 Q). Use Gemini for LLMs and embeddings. MySQL for durable user data, Redis for session, Pinecone for RAG, TAVILY for live search.\n\nKey actors (reminder)\n\nOrchestrator, Assessment, Planning, Tutor, Quiz, Feedback — plus tools: tavily_tool, rag_tool (Pinecone), db_tool. All agents use Agents SDK guardrails.\n\nFlow summary (end-to-end)\n\nFrontend calls POST /sessions/start → backend creates session_id and persists session basics to MySQL and Redis.\n\nFrontend opens WebSocket ws://.../ws/sessions/{session_id}.\n\nFIRST RUNNER: Backend checks session.state → Orchestrator picks an agent and runs Runner.run(agent, \"hello\", session) → agent returns a single contextual greeting + first action (assessment Q or last-topic summary). Send to frontend immediately.\n\nSECOND RUNNER: User answers/type → backend Runner.run(agent, user_input, session) → agent returns response → update Redis/MySQL. Loop until disconnect or state change.\n\nWhen Tutor needs external knowledge: call rag_tool.retrieve(topic) (Pinecone) → optionally call tavily_tool for recent live examples → combine and validate via guardrails → present to user.\n\nQuizzes: Quiz Agent produces dynamic 15–20 Qs (one per turn, hints ≤2). On fail, Orchestrator triggers remediation micro-lessons then mini-quiz.\n\nAll important events persisted to MySQL (plans, quiz_attempts, directives) and session state in Redis.\n\nFrontend (where it fits & what it does)\n\nBuilt after backend; connects via REST + WebSocket.\n\nPages/components to implement:\n\nLanding / Auth (signup/login)\n\nDashboard: progress, last quiz score, next lesson, streak\n\nChat UI: main chat pane (messages), typing indicator, agent cards\n\nLesson view: lesson text + example + one exercise\n\nQuiz UI: one-question-at-a-time, hint button, radio UI for A/B/C\n\nTAVILY card component: title + short snippet + link\n\nSettings/profile page (edit goals, time commitment)\n\nSmall admin dashboard: monitor guardrail triggers & tool errors (optional)\n\nWebSocket client:\n\nOpen ws/sessions/{session_id} after sessions/start\n\nShow greeting from FIRST RUNNER instantly\n\nSend user messages to WS; render responses\n\nBehavior:\n\nAll state transitions driven by Orchestrator via messages\n\nAllow “pause/continue”, “ask question”, “ready for quiz”\n\nKeep UI light; split long lessons into Part 1/Part 2 if needed\n\nDeployment:\n\nNext.js app on Render or Vercel; NEXT_PUBLIC_API_URL points to backend.\n\nEnsure WebSocket origin/allowlist and secure cookies/tokens.\n\nRAG (Pinecone) — where it fits in flow\n\nWhen to call: Tutor Agent calls rag_tool at lesson start or when user asks for supporting content. Quiz Agent may call for question generation.\n\nRetrieval usage: rag_tool.retrieve(query, k=5) returns top chunks + metadata to include as citations in lessons.\n\nFallback: if Pinecone unavailable, generate lesson without RAG and log the error.\n\nError handling & observability (short)\n\nTAVILY errors → silent fallback to RAG; log for admin.\n\nPinecone errors → fallback to RAG-less lesson; alert admin.\n\nGemini timeouts → friendly message; retry; use cache if present.\n\nGuardrail triggers logged to agent_logs for review.\n\n\nResponsibility:\n1. Orchestrator Agent: can do Orchestrat all Agentic flow manage all system , 2. Assessment- Greeting Agent: He can greet the user and mainly get his context his intrust and learning style , 3. Planning agent can get user context and slabes generate a study plan , 4. Tutor agent : can get and see user context and study plan , teach to students. ,5. Quiz agent:  can take Quiz and give to student his score in his assessment if user gai. His marks above 70% than he is pass if low than give back to tutor agent his result and say two teach his these topic and sub topic again if he pass than also give his result to tutor agent, 6: Feedback agent, Now all context are come to this agent he can see all student history and he act like a principle and he ask to student about quiz and tutor his teaching style and tone etc and than any student give problem and etc he can tell me to tutor agent and quiz agent and update his prompt mens say to him please teach the user in  this type student did not clear this topic and also say to quiz agent if any problem he can face , if all is good than continue workflow re again next topic next subtopic and etc teach"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Session start and first-run greeting (Priority: P1)

On starting a learning session, the system greets the learner with a contextual welcome and suggests the first action (either a brief recap of the last topic or the initial assessment question).

**Why this priority**: Establishes trust and momentum; critical for engagement and flow.

**Independent Test**: Start a new session and verify receipt of a single greeting and first actionable next step without additional input.

**Acceptance Scenarios**:

1. Given a new session, When the session starts, Then the learner receives a greeting and either a recap or the first assessment prompt.
2. Given an existing session, When the learner returns, Then the greeting references prior progress and suggests the next step.

---

### User Story 2 - Learning style assessment and profile (Priority: P1)

The learner completes a brief learning-style assessment (5–12 questions) and confirms areas of interest to personalize the plan.

**Why this priority**: Personalization improves lesson relevance and outcomes.

**Independent Test**: Complete the assessment flow and verify a stored learning-style profile and preferences.

**Acceptance Scenarios**:

1. Given a new learner, When they answer the assessment questions, Then a profile with learning style and interests is created.
2. Given a profile exists, When the learner edits preferences, Then the updated preferences affect subsequent recommendations.

---

### User Story 3 - Lesson with supporting knowledge (Priority: P2)

The learner receives a concise lesson with examples and can request supporting references; the system cites sources and keeps content focused.

**Why this priority**: High-quality context and examples improve understanding.

**Independent Test**: Request a lesson on a topic; verify that the lesson includes optional references and concise examples with citations.

**Acceptance Scenarios**:

1. Given a topic, When the learner asks for a lesson, Then a structured explanation with examples and citations is presented.
2. Given references are requested, When external content is unavailable, Then a lesson is delivered without references and a non-blocking note is recorded.

---

### User Story 4 - Dynamic quiz with hints and remediation (Priority: P2)

The learner answers a dynamic one-question-at-a-time quiz (15–20 questions total) with up to two hints per question; a remediation mini-lesson follows if needed.

**Why this priority**: Measures progress and reinforces learning.

**Independent Test**: Complete a quiz; verify hint availability, scoring, pass/fail threshold at 70%, and remediation on failure.

**Acceptance Scenarios**:

1. Given a quiz in progress, When the learner requests a hint, Then at most two hints are provided for that question.
2. Given a failing score, When the quiz ends, Then the learner receives a remediation mini-lesson and a short follow-up quiz.

---

### User Story 5 - Feedback and continuous improvement (Priority: P3)

After a quiz or lesson, the learner provides brief feedback about clarity and tone; the system adapts subsequent lessons and questions.

**Why this priority**: Feedback loops improve user satisfaction and outcomes.

**Independent Test**: Submit feedback and verify that future content reflects the preferences and issues raised.

**Acceptance Scenarios**:

1. Given feedback submitted, When future lessons are generated, Then tone and difficulty reflect the feedback.
2. Given repeated issues reported, When recommendations are generated, Then adjustments and acknowledgments appear in guidance.

### Edge Cases

- What happens when the connection drops mid-session? The session remains resumable without data loss and resumes at the last checkpoint.
- How does the system handle tool or retrieval errors? Provide graceful fallbacks and continue the flow with a short, friendly notice.
- What happens when the learner requests to pause or skip? The system acknowledges and queues the next appropriate step on resume.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a session start flow that returns a contextual greeting and a single next action.
- **FR-002**: The system MUST support a brief learning-style assessment (5–12 questions) and persist the resulting profile.
- **FR-003**: The system MUST allow the learner to receive concise lessons with examples and optional source citations.
- **FR-004**: The system MUST generate a dynamic quiz of 15–20 questions, delivering one question per turn with up to two hints per question.
- **FR-005**: The system MUST determine pass/fail using a 70% threshold and trigger remediation mini-lessons followed by a mini-quiz on failure.
- **FR-006**: The system MUST maintain session continuity across reconnects and maintain the latest state checkpoint.
- **FR-007**: The system MUST record important events (e.g., plans, quiz attempts, directives) and user progress for reporting.
- **FR-008**: The system MUST provide a mechanism to reference supporting material and display brief citations when available.
- **FR-009**: The system MUST support learner controls including pause/continue, ask-question, and ready-for-quiz within the conversation.
- **FR-010**: The system MUST enforce output safety and content policies and present user-friendly fallbacks on safety triggers.
- **FR-011**: The system MUST offer a feedback prompt after lessons/quizzes and adapt subsequent content accordingly.
- **FR-012**: The system MUST provide a dashboard summarizing progress, last quiz score, next lesson, and engagement streaks.

### Key Entities *(include if feature involves data)*

- **User**: Learner identity and profile preferences (e.g., interests, availability).
- **Session**: Conversation and learning state including current step, last checkpoint, recent messages.
- **AssessmentResult**: Learning-style responses and computed profile.
- **Plan**: High-level study plan with topics, subtopics, and pacing assumptions.
- **Lesson**: Content blocks with examples and optional citations.
- **QuizAttempt**: Set of questions, answers, hints used, score, and pass/fail status.
- **Directive**: System-level messages guiding state transitions and orchestration decisions.
- **Feedback**: Post-lesson or post-quiz responses about clarity, tone, and difficulty.
- **AgentLog**: Records for safety triggers and notable events for review.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of new sessions receive a greeting and first action within 2 seconds of session start.
- **SC-002**: 90% of learners complete the assessment within 4 minutes and fewer than 12 questions.
- **SC-003**: Learners achieve an average quiz pass rate ≥ 70% by the second attempt after remediation.
- **SC-004**: 90% of lesson requests include at least one example; 80% of referenced lessons include citations when sources are available.
- **SC-005**: 85% of feedback submissions lead to at least one observable adjustment (tone, pacing, or difficulty) in the next two interactions.
- **SC-006**: Session resumes succeed without data loss after reconnects in 99% of cases tested.

