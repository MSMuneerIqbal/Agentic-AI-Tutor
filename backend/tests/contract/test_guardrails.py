"""Contract tests for guardrail schemas and policies."""

import pytest

from app.guards.policies import GuardrailPolicy
from app.guards.schemas import validate_input, validate_output


# ── validate_input ────────────────────────────────────────────────────────────

def test_valid_input_passes():
    result = validate_input("Hello, I want to learn Python.")
    assert result.violated is False


def test_empty_input_is_rejected():
    result = validate_input("   ")
    assert result.violated is True
    assert "empty" in result.reason.lower()


def test_input_too_long_is_rejected():
    result = validate_input("x" * 5001)
    assert result.violated is True
    assert "5000" in result.reason


# ── validate_output ───────────────────────────────────────────────────────────

def test_clean_output_passes():
    result = validate_output("Here is a lesson about Python loops.")
    assert result.violated is False


def test_output_with_openai_key_is_redacted():
    # Must match the pattern: sk-[A-Za-z0-9]{48}
    fake_key = "sk-" + "A" * 48
    result = validate_output(f"Your key is {fake_key}")
    assert result.violated is True
    assert result.sanitized_output == "[REDACTED: Output contained sensitive information]"


def test_output_too_long_is_truncated():
    result = validate_output("x" * 10001)
    assert result.violated is True
    assert result.sanitized_output.endswith("... [truncated]")
    assert len(result.sanitized_output) <= 10020


# ── GuardrailPolicy ───────────────────────────────────────────────────────────

def test_all_agents_are_registered():
    registered = GuardrailPolicy.get_registered_agents()
    for agent in ["Orchestrator", "Assessment", "Planning", "Tutor", "Quiz", "Feedback"]:
        assert agent in registered


def test_is_agent_registered():
    assert GuardrailPolicy.is_agent_registered("Tutor") is True
    assert GuardrailPolicy.is_agent_registered("GhostAgent") is False


def test_valid_agent_input_passes():
    result = GuardrailPolicy.validate_agent_input("Orchestrator", "Hello", {})
    assert result.violated is False


def test_empty_input_rejected_by_policy():
    result = GuardrailPolicy.validate_agent_input("Orchestrator", "", {})
    assert result.violated is True


def test_unregistered_agent_rejected():
    result = GuardrailPolicy.validate_agent_input("UnknownAgent", "Hello", {})
    assert result.violated is True
    assert "not registered" in result.reason


def test_quiz_attempt_limit_enforced():
    ok = GuardrailPolicy.validate_agent_input("Quiz", "answer: a", {"quiz_attempts": 2})
    assert ok.violated is False

    exceeded = GuardrailPolicy.validate_agent_input("Quiz", "answer: a", {"quiz_attempts": 4})
    assert exceeded.violated is True
    assert "Maximum quiz attempts" in exceeded.reason


def test_tutor_output_citation_required():
    # Tutor output referencing rag_result without "source:" should be flagged
    result = GuardrailPolicy.validate_agent_output(
        "Tutor", "According to rag_result, Python is great."
    )
    assert result.violated is True
    assert "Citations required" in result.sanitized_output


def test_tutor_output_with_citation_passes():
    result = GuardrailPolicy.validate_agent_output(
        "Tutor", "According to source: Python docs, lists are mutable."
    )
    assert result.violated is False


def test_clean_agent_output_passes():
    result = GuardrailPolicy.validate_agent_output("Assessment", "What is your learning style?")
    assert result.violated is False
