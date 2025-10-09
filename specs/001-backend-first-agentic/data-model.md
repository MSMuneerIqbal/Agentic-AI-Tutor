# Data Model: Backend-first, agentic Tutor GPT flow

## Entities

### User
- id (uuid)
- email
- display_name
- created_at

### Session
- id (uuid)
- user_id → User.id
- state (enum: greeting, assessing, tutoring, quizzing, remediating, done)
- last_checkpoint
- created_at, updated_at

### AssessmentResult
- id (uuid)
- user_id → User.id
- style (enum, e.g., V/A/R/K)
- answers (json)
- created_at

### Plan
- id (uuid)
- user_id → User.id
- summary
- topics (json)
- created_at, updated_at

### Lesson
- id (uuid)
- user_id → User.id
- topic
- content (text blocks)
- citations (json: title, url, source_type)
- created_at

### QuizAttempt
- id (uuid)
- user_id → User.id
- session_id → Session.id
- score (0-100)
- passed (bool, threshold 70)
- total_questions
- hints_used (int)
- created_at

### Directive
- id (uuid)
- session_id → Session.id
- type (orchestrator, agent)
- payload (json)
- created_at

### Feedback
- id (uuid)
- user_id → User.id
- context (lesson|quiz)
- content (json)
- created_at

### AgentLog
- id (uuid)
- session_id → Session.id
- event_type (guardrail_trigger, tool_error, etc.)
- details (json)
- created_at

## Notes
- Indexing jobs tracked in MySQL with statuses; vectors live in Pinecone.
- Store only metadata and excerpts for RAG.
