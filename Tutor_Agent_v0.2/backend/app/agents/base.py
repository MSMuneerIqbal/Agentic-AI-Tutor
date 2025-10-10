"""Base agent configuration and utilities."""

from typing import Any

from app.agents.config import gemini_client
from app.core.config import get_settings
from app.guards.schemas import validate_input, validate_output

settings = get_settings()


class BaseAgent:
    """Base class for all agents with guardrail integration."""

    def __init__(self, name: str, model: str | None = None):
        """
        Initialize base agent.

        Args:
            name: Agent name
            model: Model name (defaults to settings.gemini_model)
        """
        self.name = name
        self.model = model or settings.gemini_model
        self.client = gemini_client

    async def validate_input(self, user_input: str) -> tuple[bool, str | None]:
        """
        Validate user input with guardrails.

        Args:
            user_input: User input text

        Returns:
            Tuple of (is_valid, error_message)
        """
        result = validate_input(user_input)
        return (not result.violated, result.reason)

    async def validate_output(self, agent_output: str) -> tuple[bool, str | None, str | None]:
        """
        Validate agent output with guardrails.

        Args:
            agent_output: Agent output text

        Returns:
            Tuple of (is_valid, error_message, sanitized_output)
        """
        result = validate_output(agent_output)
        return (not result.violated, result.reason, result.sanitized_output)

    async def run(self, user_input: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Run agent with guardrails.

        Args:
            user_input: User input
            context: Additional context

        Returns:
            Agent response dictionary

        Raises:
            ValueError: If input or output validation fails
        """
        # Input validation
        is_valid, error = await self.validate_input(user_input)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")

        # Execute agent logic (to be implemented in subclasses)
        response = await self._execute(user_input, context or {})

        # Output validation
        output_text = response.get("message", "")
        is_valid, error, sanitized = await self.validate_output(output_text)
        if not is_valid:
            # Log violation and return sanitized output
            response["message"] = sanitized or "[Error: Output validation failed]"
            response["guardrail_violated"] = True
            response["violation_reason"] = error

        return response

    async def execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute agent logic with input/output validation.

        Args:
            user_input: User input
            context: Context dictionary

        Returns:
            Response dictionary
        """
        # Validate input
        is_valid, error = await self.validate_input(user_input)
        if not is_valid:
            return {
                "agent": self.name,
                "message": f"Invalid input: {error}",
                "action": "input_validation_error",
                "guardrail_violated": True,
                "violation_reason": error
            }

        # Execute agent logic
        try:
            response = await self._execute(user_input, context)
            response["agent"] = self.name
            
            # Validate output
            return await self.validate_output(response)
        except Exception as e:
            return {
                "agent": self.name,
                "message": f"Error: {str(e)}",
                "action": "execution_error",
                "error": str(e)
            }

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute agent logic (to be implemented by subclasses).

        Args:
            user_input: User input
            context: Context dictionary

        Returns:
            Response dictionary
        """
        raise NotImplementedError("Subclasses must implement _execute()")

