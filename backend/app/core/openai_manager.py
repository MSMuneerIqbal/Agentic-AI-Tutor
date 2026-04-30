"""OpenAI client manager — chat completions, web search, and embeddings."""

import logging
from typing import Any

from openai import AsyncOpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def chat_complete(
    system_prompt: str,
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1500,
) -> str:
    """Run a chat completion and return the response text."""
    client = get_openai_client()
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = await client.chat.completions.create(
        model=model or settings.openai_model,
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


async def web_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    Search the web using OpenAI's native web_search_preview tool via the Responses API.
    Returns a list of result dicts with title, url, content.
    """
    client = get_openai_client()
    try:
        response = await client.responses.create(
            model="gpt-4o",
            tools=[{"type": "web_search_preview"}],
            input=query,
        )
        results = []
        for item in response.output:
            if hasattr(item, "type") and item.type == "web_search_call":
                continue
            if hasattr(item, "content"):
                for block in item.content:
                    if hasattr(block, "annotations"):
                        for ann in block.annotations:
                            if hasattr(ann, "url"):
                                results.append({
                                    "title": getattr(ann, "title", ""),
                                    "url": ann.url,
                                    "content": getattr(block, "text", "")[:500],
                                })
                    elif hasattr(block, "text"):
                        if not results:
                            results.append({
                                "title": "Web Search Result",
                                "url": "",
                                "content": block.text[:800],
                            })
        return results[:max_results]
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return []


async def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector using text-embedding-3-small (1536 dims)."""
    client = get_openai_client()
    response = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=text,
    )
    return response.data[0].embedding
