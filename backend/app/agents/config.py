"""Agents SDK configuration — OpenAI client for all agents."""

from openai import AsyncOpenAI

from app.core.config import get_settings

settings = get_settings()

_openai_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _openai_client


# Backward-compat alias used by base.py
openai_client = None  # replaced by lazy get_openai_client()
