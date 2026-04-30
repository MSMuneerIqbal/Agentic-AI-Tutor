"""Base agent with OpenAI LLM calling and guardrail integration."""

from typing import Any

from app.core.config import get_settings
from app.core.openai_manager import chat_complete
from app.guards.schemas import validate_input, validate_output

settings = get_settings()


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, name: str, model: str | None = None):
        self.name = name
        self.model = model or settings.openai_model

    async def _call_llm(
        self,
        system_prompt: str,
        user_input: str,
        rag_context: str = "",
        history: list[dict[str, str]] | None = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Call OpenAI with system prompt, optional RAG context, conversation history,
        and user input. Returns the assistant text.
        """
        messages: list[dict[str, str]] = list(history or [])

        if rag_context:
            messages.append({
                "role": "system",
                "content": f"Relevant knowledge base content:\n\n{rag_context}",
            })

        messages.append({"role": "user", "content": user_input})

        return await chat_complete(
            system_prompt=system_prompt,
            messages=messages,
            model=self.model,
            temperature=temperature,
        )

    async def validate_input(self, user_input: str) -> tuple[bool, str | None]:
        result = validate_input(user_input)
        return (not result.violated, result.reason)

    async def validate_output(self, agent_output: str) -> tuple[bool, str | None, str | None]:
        result = validate_output(agent_output)
        return (not result.violated, result.reason, result.sanitized_output)

    async def execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        is_valid, error = await self.validate_input(user_input)
        if not is_valid:
            return {
                "agent": self.name,
                "message": f"Invalid input: {error}",
                "action": "input_validation_error",
                "guardrail_violated": True,
                "violation_reason": error,
            }

        try:
            response = await self._execute(user_input, context)
            response["agent"] = self.name

            output_text = response.get("message", response.get("response", ""))
            if output_text:
                is_valid, error, sanitized = await self.validate_output(output_text)
                if not is_valid:
                    response["message"] = sanitized or "[Error: Output validation failed]"
                    response["guardrail_violated"] = True
                    response["violation_reason"] = error

            return response
        except Exception as e:
            return {
                "agent": self.name,
                "message": f"Error: {str(e)}",
                "action": "execution_error",
                "error": str(e),
            }

    async def _execute(self, user_input: str, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Subclasses must implement _execute()")
