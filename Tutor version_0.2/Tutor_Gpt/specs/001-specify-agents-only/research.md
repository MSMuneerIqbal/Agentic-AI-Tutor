# Research: Agent Layer Implementation

## Decision: Technology Stack Selection
**Rationale**: Python 3.11 with FastAPI was selected based on project requirements for async processing, strong typing with Pydantic, and compatibility with OpenAI Agents SDK. FastAPI provides excellent API documentation generation and performance suitable for agent communication. The uv package manager was selected as required by the constitution.

## Decision: Architecture Pattern
**Rationale**: Microservices architecture with a single backend service was chosen to keep the agents in one service for easier coordination and communication while maintaining separation of concerns between different agent types.

## Decision: MCP Client Initialization
**Rationale**: Initializing the MCP client at application startup and storing it in app.state ensures a single reusable connection, reducing overhead and managing the lifecycle properly with startup/shutdown events.

## Decision: Tavily Wrapper Design
**Rationale**: A small internal wrapper service was designed to handle caching, rate limiting, and guardrails for Tavily results, while keeping these concerns separate from the Tutor agent logic. When unavailable, the Tutor agent continues with generated content as specified in the requirements.

## Decision: Data Storage Strategy
**Rationale**: MySQL for user data ensures ACID compliance for critical student information (required by FERPA/COPPA), while Redis provides fast access for session data and temporary storage needed during tutoring sessions.

## Decision: Agent Communication Protocol
**Rationale**: Using Pydantic models for AgentRequest/AgentResponse ensures type safety and clear contracts between agents, making the system more maintainable and testable.

## Decision: Data Retention Policy
**Rationale**: Implementing a 1-year retention policy after last activity follows the requirement from the spec clarifications to automatically delete student data after this period, supporting privacy compliance.

## Decision: Accessibility Compliance
**Rationale**: Implementing WCAG 2.1 AA standards ensures the system is accessible to students with disabilities, meeting legal and ethical requirements for educational platforms.

## Alternatives Considered
- Using a different programming language (e.g., Node.js, Go) - rejected in favor of Python's strong AI/ML ecosystem and OpenAI SDK compatibility
- Direct Tavily API integration without MCP - rejected to comply with architectural requirements
- Single database for all data - rejected to leverage the strengths of both SQL and NoSQL databases
- No caching for Tavily results - rejected due to performance considerations
- Different accessibility standards - WCAG 2.1 AA chosen as the recognized standard for web accessibility