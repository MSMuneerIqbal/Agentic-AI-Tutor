"""Guardrail schemas and validation rules."""

from pydantic import BaseModel, Field


class GuardrailViolation(BaseModel):
    """Guardrail violation response."""

    violated: bool
    reason: str | None = None
    sanitized_output: str | None = None


class AgentInputGuardrail(BaseModel):
    """Input validation schema for agents."""

    user_input: str = Field(..., min_length=1, max_length=5000)
    context: dict = Field(default_factory=dict)

    class Config:
        """Pydantic config."""

        extra = "forbid"  # Reject unknown fields


class AgentOutputGuardrail(BaseModel):
    """Output validation schema for agents."""

    agent_name: str
    message: str = Field(..., min_length=1, max_length=10000)
    action: str | None = None
    metadata: dict = Field(default_factory=dict)

    class Config:
        """Pydantic config."""

        extra = "allow"  # Allow additional fields


class SecretDetectionRule:
    """Detect actual credential leaks in agent output (not educational content)."""

    # Only match patterns that look like real secrets (alphanumeric values after the label)
    # e.g. "api_key=AIzaSy..." or "password: s3cr3t123" but NOT "how does a token work?"
    PATTERNS = [
        r"api[_-]?key\s*[=:]\s*[A-Za-z0-9_\-]{20,}",
        r"secret[_-]?key\s*[=:]\s*[A-Za-z0-9_\-]{20,}",
        r"password\s*[=:]\s*[A-Za-z0-9!@#$%^&*]{8,}",
        r"bearer\s+[A-Za-z0-9\-_=.]{20,}",
        r"AIza[A-Za-z0-9\-_]{35}",  # Google API key pattern
        r"sk-[A-Za-z0-9]{48}",       # OpenAI key pattern
    ]

    @staticmethod
    def contains_secret(text: str) -> bool:
        """
        Check if text contains actual credential leaks (not just educational mentions).

        Args:
            text: Text to check

        Returns:
            True if actual secret credential detected
        """
        import re

        for pattern in SecretDetectionRule.PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


def sanitize_output(text: str) -> str:
    """
    Sanitize agent output by removing potential secrets.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    if SecretDetectionRule.contains_secret(text):
        return "[REDACTED: Output contained sensitive information]"
    return text


def validate_input(user_input: str) -> GuardrailViolation:
    """
    Validate user input against guardrails.

    Args:
        user_input: User input text

    Returns:
        GuardrailViolation result
    """
    # Length check
    if len(user_input) > 5000:
        return GuardrailViolation(
            violated=True,
            reason="Input exceeds maximum length of 5000 characters",
        )

    # Empty input check
    if not user_input.strip():
        return GuardrailViolation(
            violated=True,
            reason="Input cannot be empty",
        )

    return GuardrailViolation(violated=False)


def validate_output(agent_output: str) -> GuardrailViolation:
    """
    Validate agent output against guardrails.

    Args:
        agent_output: Agent output text

    Returns:
        GuardrailViolation result
    """
    # Secret detection
    if SecretDetectionRule.contains_secret(agent_output):
        return GuardrailViolation(
            violated=True,
            reason="Output contains potential sensitive information",
            sanitized_output=sanitize_output(agent_output),
        )

    # Length check
    if len(agent_output) > 10000:
        return GuardrailViolation(
            violated=True,
            reason="Output exceeds maximum length",
            sanitized_output=agent_output[:10000] + "... [truncated]",
        )

    return GuardrailViolation(violated=False)

