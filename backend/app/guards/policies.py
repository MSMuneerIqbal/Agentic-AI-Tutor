"""Guardrail policies for all agents."""

from typing import Any

from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.guards.schemas import (
    GuardrailViolation,
    SecretDetectionRule,
    sanitize_output,
    validate_input,
    validate_output,
)

logger = get_logger(__name__)
metrics = get_metrics_collector()


class GuardrailPolicy:
    """Central guardrail policy manager for all agents."""

    # Registered agent names
    REGISTERED_AGENTS = [
        "Orchestrator",
        "Assessment",
        "Planning",
        "Tutor",
        "Quiz",
        "Feedback",
    ]

    # Input guardrail rules
    INPUT_RULES = {
        "min_length": 1,
        "max_length": 5000,
        "reject_empty": True,
        "reject_unknown_fields": True,
    }

    # Output guardrail rules
    OUTPUT_RULES = {
        "max_length": 10000,
        "detect_secrets": True,
        "sanitize_on_violation": True,
    }

    @classmethod
    def validate_agent_input(
        cls, agent_name: str, user_input: str, context: dict[str, Any] | None = None
    ) -> GuardrailViolation:
        """
        Validate agent input with registered guardrails.

        Args:
            agent_name: Name of the agent
            user_input: User input text
            context: Optional context data

        Returns:
            GuardrailViolation result
        """
        if agent_name not in cls.REGISTERED_AGENTS:
            return GuardrailViolation(
                violated=True,
                reason=f"Agent '{agent_name}' not registered in guardrail policy",
            )

        # Apply input validation
        result = validate_input(user_input)
        
        # Track guardrail trigger if violated
        if result.violated:
            metrics.increment_guardrail_trigger(agent_name, "input_validation")
            logger.warning(
                f"Input guardrail triggered for {agent_name}",
                extra={"agent": agent_name, "reason": result.reason},
            )

        # Additional agent-specific rules can be added here
        if agent_name == "Quiz" and context:
            # Quiz-specific: check for quiz attempt limits
            attempts = context.get("quiz_attempts", 0)
            if attempts > 3:
                return GuardrailViolation(
                    violated=True,
                    reason="Maximum quiz attempts exceeded (3)",
                )

        return result

    @classmethod
    def validate_agent_output(
        cls, agent_name: str, agent_output: str
    ) -> GuardrailViolation:
        """
        Validate agent output with registered guardrails.

        Args:
            agent_name: Name of the agent
            agent_output: Agent output text

        Returns:
            GuardrailViolation result with sanitized output if violated
        """
        if agent_name not in cls.REGISTERED_AGENTS:
            return GuardrailViolation(
                violated=True,
                reason=f"Agent '{agent_name}' not registered in guardrail policy",
                sanitized_output="[Agent not registered]",
            )

        # Apply output validation
        result = validate_output(agent_output)
        
        # Track guardrail trigger if violated
        if result.violated:
            metrics.increment_guardrail_trigger(agent_name, "output_validation")
            logger.warning(
                f"Output guardrail triggered for {agent_name}",
                extra={"agent": agent_name, "reason": result.reason},
            )

        # Additional agent-specific rules
        if agent_name == "Tutor":
            # Tutor-specific: ensure citations are present if using RAG
            if "rag_result" in agent_output.lower() and "source:" not in agent_output.lower():
                return GuardrailViolation(
                    violated=True,
                    reason="Tutor output must include source citations when using RAG",
                    sanitized_output=agent_output + "\n\n[Note: Citations required for external sources]",
                )

        return result

    @classmethod
    def is_agent_registered(cls, agent_name: str) -> bool:
        """Check if agent is registered in guardrail policy."""
        return agent_name in cls.REGISTERED_AGENTS

    @classmethod
    def get_registered_agents(cls) -> list[str]:
        """Get list of all registered agents."""
        return cls.REGISTERED_AGENTS.copy()

    @classmethod
    def register_agent(cls, agent_name: str) -> None:
        """
        Register a new agent in the guardrail policy.

        Args:
            agent_name: Name of agent to register
        """
        if agent_name not in cls.REGISTERED_AGENTS:
            cls.REGISTERED_AGENTS.append(agent_name)

