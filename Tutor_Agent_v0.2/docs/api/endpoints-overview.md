# API Endpoints Overview

## Session & WebSocket

- POST `/sessions/start`
  - Response: `{ session_id }`
  - Side effects: create session (MySQL), seed Redis state
- WS `/ws/sessions/{session_id}`
  - Server push: FIRST RUNNER greeting
  - Bidirectional: user messages and agent responses

## RAG

- POST `/api/v1/rag/index`
  - Body: `{ docs:[...], namespace }`
  - Effect: enqueue indexing job; worker extracts→chunks→embeds→upserts; status recorded
- GET `/api/v1/rag/index/{job_id}`
  - Response: job status, vector counts
- POST `/api/v1/rag/retrieve`
  - Body: `{ query, k=5, namespace?, filter? }`
  - Response: top-k `{ text<=400t, title, url, source_type, chunk_id }`

## Notes

- All endpoints return JSON; errors include safe messages
- Authentication optional at MVP; add later if required
