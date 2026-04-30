"""
Web search tool using OpenAI's native web_search_preview via the Responses API.
Replaces Tavily for all agents that need live web content.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.core.openai_manager import web_search as _openai_web_search

logger = logging.getLogger(__name__)


@dataclass
class WebResult:
    title: str
    url: str
    content: str
    relevance_score: float = 1.0
    source: str = "web"
    metadata: Dict[str, Any] = field(default_factory=dict)


class WebSearchTool:
    """Wraps OpenAI web_search_preview into a structured interface."""

    async def search(self, query: str, max_results: int = 5) -> List[WebResult]:
        try:
            raw = await _openai_web_search(query=query, max_results=max_results)
            return [
                WebResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    content=r.get("content", ""),
                )
                for r in raw
            ]
        except Exception as e:
            logger.warning(f"WebSearchTool.search failed: {e}")
            return []

    async def search_topic(self, topic: str, context: str = "", max_results: int = 3) -> List[WebResult]:
        query = f"{topic} {context}".strip() if context else topic
        return await self.search(query=query, max_results=max_results)

    async def get_best_practices(self, topic: str) -> List[WebResult]:
        return await self.search(f"{topic} best practices latest", max_results=3)

    async def get_examples(self, topic: str) -> List[WebResult]:
        return await self.search(f"{topic} practical examples tutorial", max_results=3)


_web_search_tool: WebSearchTool | None = None


async def get_web_search_tool() -> WebSearchTool:
    global _web_search_tool
    if _web_search_tool is None:
        _web_search_tool = WebSearchTool()
    return _web_search_tool
