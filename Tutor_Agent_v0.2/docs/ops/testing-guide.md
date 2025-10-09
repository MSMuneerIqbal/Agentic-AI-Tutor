# Testing Guide - Tutor GPT

## Overview

Tutor GPT follows **Test-Driven Development (TDD)** with comprehensive test coverage across multiple test types.

## Test Structure

```
backend/tests/
├── unit/           # Unit tests (isolated components)
├── integration/    # Integration tests (API, DB, Redis)
├── contract/       # Contract tests (API schemas, guardrails)
└── e2e/            # End-to-end tests (Playwright)
```

## Test Types

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation

**Examples**:
- `test_models.py` - Database model creation and relationships
- `test_agents.py` - Agent logic and guardrails
- `test_guards.py` - Guardrail validation rules

**Run**:
```bash
pytest tests/unit -v
```

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test component interactions

**Examples**:
- `test_api.py` - FastAPI endpoints with database
- `test_websocket.py` - WebSocket greeting and messaging
- `test_reconnect.py` - Session reconnect and resume

**Run**:
```bash
pytest tests/integration -v
```

### 3. Contract Tests (`tests/contract/`)

**Purpose**: Test API contracts and guardrail policies

**Examples**:
- `test_guardrails.py` - Guardrail fallback and logging
- `test_rag.py` - RAG tool contracts (Phase 8)

**Run**:
```bash
pytest tests/contract -v
```

### 4. E2E Tests (`tests/e2e/`)

**Purpose**: Test full user flows via Playwright (MCP UI testing)

**Examples**:
- `test_playwright_greeting.py` - WebSocket greeting UI smoke test

**Run**:
```bash
pytest tests/e2e -v -m playwright
```

**Note**: Playwright tests are **optional** until frontend is ready (Phase 9).

## Coverage Requirements

**Target**: ≥80% code coverage

**Check coverage**:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Coverage exclusions**:
- `__init__.py` files
- Abstract methods
- `if __name__ == "__main__"`
- `if TYPE_CHECKING:`

## CI/CD Integration

### GitHub Actions Workflow

File: `.github/workflows/backend-tests.yml`

**Jobs**:
1. **test** - Run all tests with coverage
   - Linting (ruff check)
   - Format checking (ruff format)
   - Unit tests
   - Integration tests
   - Contract tests
   - Coverage upload to Codecov

2. **playwright** - Run E2E UI tests
   - Install Playwright browsers
   - Run Playwright tests
   - Upload test reports
   - **Optional gating** until frontend ready

**Quality Gates**:
- ✅ All tests must pass
- ✅ Coverage ≥ 80%
- ✅ No linting errors
- ✅ Format check passes

## Test Markers

Use pytest markers to organize and run specific tests:

```python
@pytest.mark.asyncio  # Async test
@pytest.mark.playwright  # Playwright E2E test
@pytest.mark.unit  # Unit test
@pytest.mark.integration  # Integration test
@pytest.mark.contract  # Contract test
@pytest.mark.slow  # Slow-running test
```

**Run specific markers**:
```bash
pytest -m unit  # Run only unit tests
pytest -m "not slow"  # Skip slow tests
pytest -m "asyncio and integration"  # Run async integration tests
```

## Guardrail Testing (T-GU-003, T-SEC-001)

**Required guardrail tests**:
- ✅ Input validation (length, empty, malformed)
- ✅ Output validation (secrets, length)
- ✅ Sanitization and fallback responses
- ✅ Agent registration in policy
- ✅ Agent-specific rules (quiz attempts, citations)

**Example**:
```python
@pytest.mark.asyncio
async def test_guardrail_secret_detection():
    from app.guards.schemas import validate_output
    
    output = "API_KEY: sk-12345"
    result = validate_output(output)
    
    assert result.violated is True
    assert result.sanitized_output == "[REDACTED: ...]"
```

## WebSocket Testing (T-GU-001, T-GU-004)

**Required WebSocket tests**:
- ✅ FIRST RUNNER greeting delivery (<5s)
- ✅ SECOND RUNNER user message loop
- ✅ Reconnect and resume session state
- ✅ Graceful disconnection

**Example**:
```python
@pytest.mark.asyncio
async def test_websocket_greeting():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/sessions/{id}") as ws:
            greeting = ws.receive_json()
            assert greeting["type"] == "agent_message"
```

## Playwright UI Testing (T-GU-005, T-CON-001)

**Constitutional Requirement**: MCP UI testing with Playwright

**Tests** (ready when frontend available):
- ✅ Greeting card appears within 8s
- ✅ Agent name displayed
- ✅ Options/actions visible

**Status**: Skipped until Phase 9 (Frontend Skeleton)

**CI**: Playwright job runs but doesn't gate PR until frontend ready

## Running Tests Locally

### Quick Test
```bash
cd backend
pytest
```

### With Coverage
```bash
pytest --cov=app --cov-report=term
```

### Specific Test File
```bash
pytest tests/unit/test_agents.py -v
```

### Specific Test Function
```bash
pytest tests/unit/test_agents.py::test_orchestrator_greeting -v
```

### Watch Mode (with pytest-watch)
```bash
uv add --dev pytest-watch
ptw -- tests/unit
```

## Debugging Tests

### Verbose Output
```bash
pytest -vv --tb=long
```

### Print Statements
```bash
pytest -s  # Show print() output
```

### Stop on First Failure
```bash
pytest -x
```

### Debug with pdb
```python
def test_example():
    import pdb; pdb.set_trace()
    assert True
```

## Test Data Management

### Fixtures
- `db_session` - Test database session (SQLite in-memory)
- `client` - Test HTTP client
- `redis_client` - Mock Redis client

### Factories (TODO)
- User factory
- Session factory
- Assessment factory

## Best Practices

1. **Follow TDD**: Write test first, then implementation
2. **Test one thing**: Each test should verify one behavior
3. **Use descriptive names**: `test_orchestrator_sends_greeting_on_hello()`
4. **Arrange-Act-Assert**: Clear test structure
5. **Mock external services**: Gemini API, Pinecone, TAVILY
6. **Clean up**: Use fixtures for setup/teardown
7. **Fast tests**: Keep unit tests <100ms
8. **Stable tests**: No flaky tests allowed

## Mocking External Services

### Gemini API
```python
@pytest.fixture
def mock_gemini():
    with patch("app.agents.config.gemini_client") as mock:
        mock.chat.completions.create.return_value = Mock(...)
        yield mock
```

### Redis (when not using fakeredis)
```python
@pytest.fixture
async def mock_redis():
    with patch("app.core.redis.redis_client") as mock:
        yield mock
```

## Future Enhancements

- [ ] Add mutation testing (mutmut)
- [ ] Add property-based testing (Hypothesis)
- [ ] Add load testing (Locust)
- [ ] Add visual regression testing (Percy)
- [ ] Add contract testing for agents (Pact)

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Playwright Python](https://playwright.dev/python/)
- [Coverage.py](https://coverage.readthedocs.io/)

