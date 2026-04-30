# Agents Overview - Tutor GPT

## Agent Architecture

The Tutor GPT system uses the **OpenAI Agents SDK** to implement a multi-agent tutoring system with the following key components:

### Base Agent (`app/agents/base.py`)

All agents inherit from `BaseAgent`, which provides:
- **Guardrail Integration**: Automatic input/output validation
- **Secret Detection**: Prevents leaking sensitive information
- **Error Handling**: Sanitization and fallback responses
- **Context Management**: Session and user context handling

### Implemented Agents

#### 1. Orchestrator Agent (`app/agents/orchestrator.py`)

**Role**: Traffic controller and session manager

**Responsibilities**:
- Send initial greeting (FIRST RUNNER)
- Route users to appropriate agents based on session state
- Manage handoffs between agents
- Maintain overall conversation flow

**States Managed**:
- `GREETING` → Welcome and explain process
- `ASSESSING` → Handoff to Assessment Agent
- `TUTORING` → Handoff to Tutor Agent
- `QUIZZING` → Handoff to Quiz Agent
- `REMEDIATING` → Handle failed quiz scenarios
- `DONE` → Congratulate and offer next steps

**Handoffs**:
- Assessment Agent
- Planning Agent
- Tutor Agent
- Quiz Agent
- Feedback Agent

**Example Flow**:
```python
orchestrator = OrchestratorAgent()
context = {"state": SessionState.GREETING}
response = await orchestrator.run("hello", context)
# Returns: Greeting message + next_state = ASSESSING
```

#### 2. Assessment Agent (`app/agents/assessment.py`)

**Role**: Learning style evaluator

**Responsibilities**:
- Conduct VARK assessment (5-12 questions)
- Ask one question at a time
- Analyze responses to determine learning style
- Provide encouraging summary

**VARK Learning Styles**:
- **V (Visual)**: Diagrams, charts, spatial understanding
- **A (Auditory)**: Listening, discussions
- **R (Reading/Writing)**: Reading, note-taking
- **K (Kinesthetic)**: Hands-on, practice

**Assessment Process**:
1. Ask first question
2. Collect answer
3. Ask next question (repeat 5-12 times)
4. Analyze answers
5. Return learning style (V/A/R/K)

**Example**:
```python
assessment = AssessmentAgent()
context = {"answers": []}
response = await assessment.run("start", context)
# Returns: Question 1 with options (a/b/c/d)
```

#### 3. Tutor Agent (`app/agents/tutor.py`)

**Role**: Personalized lesson delivery

**Responsibilities**:
- Deliver lessons adapted to learning style
- Use RAG tool for supporting content (TODO)
- Use TAVILY for live examples (TODO)
- Provide citations for external sources
- Check for understanding
- Offer practice exercises

**Learning Style Adaptation**:
- **Visual**: Diagrams, visual metaphors 🎨
- **Auditory**: Verbal explanations 🎧
- **Reading**: Detailed text 📚
- **Kinesthetic**: Hands-on examples 🛠️

**Lesson Structure**:
1. Introduction to topic
2. Core explanation (adapted)
3. Example/analogy
4. Understanding check
5. Practice exercise

**Example**:
```python
tutor = TutorAgent()
context = {
    "topic": "Docker",
    "learning_style": "V",
    "progress": 0
}
response = await tutor.run("teach me", context)
# Returns: Visual-adapted lesson on Docker
```

## Agent Communication Flow

```
User → WebSocket → Orchestrator Agent
                       ↓
            ┌──────────┴──────────┐
            ↓                     ↓
    Assessment Agent         Tutor Agent
            ↓                     ↓
      (VARK Test)           (Lessons)
            ↓                     ↓
    Planning Agent          Quiz Agent
            ↓                     ↓
     (Study Plan)          (Testing)
            ↓                     ↓
            └──────────┬──────────┘
                       ↓
              Feedback Agent
                       ↓
                  User (WS)
```

## Guardrails

All agents use built-in guardrails from `app/guards/schemas.py`:

### Input Guardrails
- **Length**: 1-5000 characters
- **Empty check**: Non-empty input required
- **Field validation**: Strict schema enforcement

### Output Guardrails
- **Secret detection**: Prevents API keys, passwords, tokens in output
- **Length**: Max 10,000 characters
- **Sanitization**: Automatic redaction of sensitive data

**Example**:
```python
# Input validation
is_valid, error = await agent.validate_input(user_input)
if not is_valid:
    raise ValueError(f"Input validation failed: {error}")

# Output validation
is_valid, error, sanitized = await agent.validate_output(agent_output)
if not is_valid:
    output = sanitized  # Use sanitized version
```

## Tools Integration (TODO)

Agents will integrate with tools for enhanced capabilities:

### RAG Tool (`app/tools/rag_tool.py`)
```python
# Retrieve relevant content from Pinecone
results = await rag_tool.retrieve(
    query="Docker containers",
    k=5,
    namespace="docker-k8s"
)
```

### TAVILY Tool (MCP)
```python
# Search for live examples
examples = await tavily_tool.search(
    query="Docker compose tutorial",
    max_results=3
)
```

### Database Tool
```python
# Store assessment results, lessons, quiz attempts
await db_tool.save_assessment(user_id, style, answers)
```

## Testing

All agents have comprehensive unit tests in `tests/unit/test_agents.py`:

- ✅ Orchestrator greeting and routing
- ✅ Assessment question flow and completion
- ✅ Tutor lesson delivery and style adaptation
- ✅ Input/output validation with guardrails
- ✅ Handoff mechanisms

**Run tests**:
```bash
cd backend
pytest tests/unit/test_agents.py -v
```

## Future Agents (TODO)

### Planning Agent
- Generate personalized study plans
- Set learning goals and milestones
- Track progress

### Quiz Agent
- Generate adaptive quizzes (15-20 questions)
- Provide hints (max 2 per question)
- Score and evaluate mastery
- Trigger remediation if score < 70%

### Feedback Agent
- Collect user feedback on lessons/quizzes
- Analyze performance data
- Adapt teaching approach
- Generate performance reports

## Configuration

Agents use settings from `app/core/config.py`:

```python
# .env file
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_API_KEY=your_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

## Best Practices

1. **Always use guardrails**: Never bypass input/output validation
2. **Keep messages concise**: 1-2 key points per message
3. **Cite sources**: Always credit RAG/TAVILY content
4. **Check understanding**: Ask questions before moving forward
5. **Be encouraging**: Maintain positive, supportive tone
6. **Adapt to learning style**: Use user's VARK preference
7. **Log violations**: Track guardrail triggers for monitoring

## Next Steps

1. Implement Planning, Quiz, and Feedback agents
2. Integrate RAG tool with Pinecone
3. Add TAVILY MCP for live search
4. Create agent-to-agent handoff logic
5. Add Six-Part prompting framework
6. Implement prompt-as-config (hot reload)

