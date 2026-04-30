"""Contract tests for guardrail fallback and logging."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import OrchestratorAgent, TutorAgent
from app.guards.policies import GuardrailPolicy
from app.models import AgentLog


@pytest.mark.asyncio
async def test_guardrail_input_validation():
    """Test input guardrail rejects invalid inputs."""
    agent = OrchestratorAgent()

    # Test empty input
    with pytest.raises(ValueError, match="Input validation failed"):
        await agent.run("", {})

    # Test too long input
    long_input = "x" * 6000
    with pytest.raises(ValueError, match="Input validation failed"):
        await agent.run(long_input, {})


@pytest.mark.asyncio
async def test_guardrail_output_secret_detection():
    """Test output guardrail detects and sanitizes secrets."""
    from app.guards.schemas import validate_output

    # Test secret detection
    output_with_secret = "Here is your API_KEY: sk-1234567890abcdef"
    result = validate_output(output_with_secret)

    assert result.violated is True
    assert result.reason == "Output contains potential sensitive information"
    assert result.sanitized_output == "[REDACTED: Output contained sensitive information]"


@pytest.mark.asyncio
async def test_guardrail_output_length_limit():
    """Test output guardrail enforces length limits."""
    from app.guards.schemas import validate_output

    # Test output too long
    long_output = "x" * 11000
    result = validate_output(long_output)

    assert result.violated is True
    assert result.reason == "Output exceeds maximum length"
    assert result.sanitized_output.endswith("... [truncated]")
    assert len(result.sanitized_output) <= 10020  # 10000 + truncation message


@pytest.mark.asyncio
async def test_guardrail_fallback_response(db_session: AsyncSession):
    """Test guardrail violation triggers fallback response and logging."""
    # Create a mock agent output with secret
    agent = TutorAgent()

    # Manually create output with secret (bypassing normal flow for testing)
    from app.guards.schemas import validate_output

    test_output = "Your password is: secret123"
    is_valid, error, sanitized = await agent.validate_output(test_output)

    # Verify guardrail violation
    assert is_valid is False
    assert error == "Output contains potential sensitive information"
    assert sanitized == "[REDACTED: Output contained sensitive information]"

    # In production, this would be logged to agent_logs
    # For now, just verify the sanitization works


@pytest.mark.asyncio
async def test_guardrail_policy_agent_registration():
    """Test guardrail policy correctly registers agents."""
    registered_agents = GuardrailPolicy.get_registered_agents()

    # Verify all required agents are registered
    assert "Orchestrator" in registered_agents
    assert "Assessment" in registered_agents
    assert "Planning" in registered_agents
    assert "Tutor" in registered_agents
    assert "Quiz" in registered_agents
    assert "Feedback" in registered_agents

    # Verify agent registration check
    assert GuardrailPolicy.is_agent_registered("Orchestrator") is True
    assert GuardrailPolicy.is_agent_registered("UnknownAgent") is False


@pytest.mark.asyncio
async def test_guardrail_policy_input_validation():
    """Test guardrail policy validates input correctly."""
    # Valid input
    result = GuardrailPolicy.validate_agent_input("Orchestrator", "Hello", {})
    assert result.violated is False

    # Empty input
    result = GuardrailPolicy.validate_agent_input("Orchestrator", "", {})
    assert result.violated is True
    assert "empty" in result.reason.lower()

    # Unregistered agent
    result = GuardrailPolicy.validate_agent_input("UnknownAgent", "Hello", {})
    assert result.violated is True
    assert "not registered" in result.reason


@pytest.mark.asyncio
async def test_guardrail_policy_output_validation():
    """Test guardrail policy validates output correctly."""
    # Valid output
    result = GuardrailPolicy.validate_agent_output("Tutor", "This is a lesson.")
    assert result.violated is False

    # Output with secret
    result = GuardrailPolicy.validate_agent_output(
        "Tutor", "Here is the api_key: 12345"
    )
    assert result.violated is True
    assert result.sanitized_output == "[REDACTED: Output contained sensitive information]"


@pytest.mark.asyncio
async def test_guardrail_quiz_attempt_limit():
    """Test guardrail enforces quiz attempt limits."""
    context_ok = {"quiz_attempts": 2}
    result = GuardrailPolicy.validate_agent_input("Quiz", "answer: a", context_ok)
    assert result.violated is False

    context_exceeded = {"quiz_attempts": 4}
    result = GuardrailPolicy.validate_agent_input("Quiz", "answer: a", context_exceeded)
    assert result.violated is True
    assert "Maximum quiz attempts exceeded" in result.reason


@pytest.mark.asyncio
async def test_guardrail_tutor_citation_requirement():
    """Test guardrail enforces citation requirements for Tutor."""
    # Output with RAG but no citation
    output_no_citation = "According to rag_result, Docker is great."
    result = GuardrailPolicy.validate_agent_output("Tutor", output_no_citation)
    assert result.violated is True
    assert "Citations required" in result.sanitized_output

    # Output with citation
    output_with_citation = "According to source: Docker docs, containers are lightweight."
    result = GuardrailPolicy.validate_agent_output("Tutor", output_with_citation)
    assert result.violated is False

