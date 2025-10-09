# Research: Backend-first, agentic Tutor GPT flow

## Decisions

- Models: Use Gemini for chat and embeddings (per constitution).
- RAG: Pinecone index with Gemini embeddings; metadata-only storage long-term.
- Sessions: Redis for ephemeral state and caches; MySQL for durable records.
- Frontend: Next.js after backend readiness; WS for agent loop.
- Quiz length: bounded-adaptive 15–20 (early stop on mastery, extend if borderline).

## Rationale

- MCP-first ensures consistent live search/docs/UI via TAVILY/Context7/Playwright.
- Gemini-only simplifies provider configuration and ensures embedding/model coherence.
- Metadata-only storage respects privacy while enabling citations.

## Alternatives Considered

- Vector DB alternatives (e.g., pgvector, Milvus): deferred to future ADR if constraints change.
- Fixed quiz length: rejected for reduced adaptivity.
- Store full text in DB: rejected due to privacy and cost.
