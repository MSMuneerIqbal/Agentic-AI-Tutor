---
stage: spec
title: Backend-first agentic spec authored
date: 2025-10-09
---

## Full Input

```
/sp.specify 

/sp.specify Backend-first, agentic Tutor GPT flow — Orchestrator runs a two-stage runner (backend-initiated "hello" then user loop). Assessment uses VARK (5–12 Q). Quiz is dynamic (15–20 Q). Use Gemini for LLMs and embeddings. MySQL for durable user data, Redis for session, Pinecone for RAG, TAVILY for live search.

Key actors (reminder)

Orchestrator, Assessment, Planning, Tutor, Quiz, Feedback — plus tools: tavily_tool, rag_tool (Pinecone), db_tool. All agents use Agents SDK guardrails.

Flow summary (end-to-end)

Frontend calls POST /sessions/start → backend creates session_id and persists session basics to MySQL and Redis.

Frontend opens WebSocket ws://.../ws/sessions/{session_id}.

FIRST RUNNER: Backend checks session.state → Orchestrator picks an agent and runs Runner.run(agent, "hello", session) → agent returns a single contextual greeting + first action (assessment Q or last-topic summary). Send to frontend immediately.

SECOND RUNNER: User answers/type → backend Runner.run(agent, user_input, session) → agent returns response → update Redis/MySQL. Loop until disconnect or state change.

When Tutor needs external knowledge: call rag_tool.retrieve(topic) (Pinecone) → optionally call tavily_tool for recent live examples → combine and validate via guardrails → present to user.

Quizzes: Quiz Agent produces dynamic 15–20 Qs (one per turn, hints ≤2). On fail, Orchestrator triggers remediation micro-lessons then mini-quiz.

All important events persisted to MySQL (plans, quiz_attempts, directives) and session state in Redis.

Frontend (where it fits & what it does)

Built after backend; connects via REST + WebSocket.

Pages/components to implement:

Landing / Auth (signup/login)

Dashboard: progress, last quiz score, next lesson, streak

Chat UI: main chat pane (messages), typing indicator, agent cards

Lesson view: lesson text + example + one exercise

Quiz UI: one-question-at-a-time, hint button, radio UI for A/B/C

TAVILY card component: title + short snippet + link

Settings/profile page (edit goals, time commitment)

Small admin dashboard: monitor guardrail triggers & tool errors (optional)

WebSocket client:

Open ws/sessions/{session_id} after sessions/start

Show greeting from FIRST RUNNER instantly

Send user messages to WS; render responses

Behavior:

All state transitions driven by Orchestrator via messages

Allow “pause/continue”, “ask question”, “ready for quiz”

Keep UI light; split long lessons into Part 1/Part 2 if needed

Deployment:

Next.js app on Render or Vercel; NEXT_PUBLIC_API_URL points to backend.

Ensure WebSocket origin/allowlist and secure cookies/tokens.

RAG (Pinecone) — where it fits in flow

When to call: Tutor Agent calls rag_tool at lesson start or when user asks for supporting content. Quiz Agent may call for question generation.

Retrieval usage: rag_tool.retrieve(query, k=5) returns top chunks + metadata to include as citations in lessons.

Fallback: if Pinecone unavailable, generate lesson without RAG and log the error.

Error handling & observability (short)

TAVILY errors → silent fallback to RAG; log for admin.

Pinecone errors → fallback to RAG-less lesson; alert admin.

Gemini timeouts → friendly message; retry; use cache if present.

Guardrail triggers logged to agent_logs for review.


Responsibility:
1. Orchestrator Agent: can do Orchestrat all Agentic flow manage all system , 2. Assessment- Greeting Agent: He can greet the user and mainly get his context his intrust and learning style , 3. Planning agent can get user context and slabes generate a study plan , 4. Tutor agent : can get and see user context and study plan , teach to students. ,5. Quiz agent:  can take Quiz and give to student his score in his assessment if user gai. His marks above 70% than he is pass if low than give back to tutor agent his result and say two teach his these topic and sub topic again if he pass than also give his result to tutor agent, 6: Feedback agent, Now all context are come to this agent he can see all student history and he act like a principle and he ask to student about quiz and tutor his teaching style and tone etc and than any student give problem and etc he can tell me to tutor agent and quiz agent and update his prompt mens say to him please teach the user in  this type student did not clear this topic and also say to quiz agent if any problem he can face , if all is good than continue workflow re again next topic next subtopic and etc teach 
```

## Artifacts

- Created feature branch and spec file at `specs/001-backend-first-agentic/spec.md`.
- Created quality checklist at `specs/001-backend-first-agentic/checklists/requirements.md` and validated as pass.

## Notes

- No clarifications required beyond reasonable defaults. Ready for `/sp.plan`.

