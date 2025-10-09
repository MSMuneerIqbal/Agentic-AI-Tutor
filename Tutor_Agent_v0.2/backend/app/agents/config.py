"""Agents SDK configuration and initialization."""

from openai import OpenAI

from app.core.config import get_settings

settings = get_settings()


def get_gemini_client() -> OpenAI:
    """
    Get configured Gemini client for Agents SDK.

    Returns:
        OpenAI client configured for Gemini
    """
    return OpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
    )


# Global client instance
gemini_client = get_gemini_client()

