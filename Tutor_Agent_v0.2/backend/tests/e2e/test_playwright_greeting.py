"""Playwright E2E smoke test for WS greeting (MCP UI test)."""

import pytest
from playwright.async_api import Page, expect


@pytest.mark.asyncio
@pytest.mark.playwright
async def test_greeting_card_appears(page: Page):
    """
    Playwright smoke test for WebSocket greeting.

    This satisfies the MCP UI testing requirement from the constitution.

    Flow:
    1. Navigate to frontend chat page
    2. Backend creates session via /sessions/start
    3. Frontend opens WebSocket
    4. Greeting card appears within 8s

    TODO: Requires frontend to be running (Phase 9: Frontend Skeleton)
    """
    pytest.skip("Frontend not yet implemented (Phase 9: T030-T032)")

    # When frontend is ready, this test will:
    # 1. Navigate to http://localhost:3000/chat
    # 2. Wait for greeting card to appear
    # 3. Assert greeting contains expected agent name and options


@pytest.mark.asyncio
@pytest.mark.playwright
async def test_greeting_contains_agent_name(page: Page):
    """Test greeting card shows agent name."""
    pytest.skip("Frontend not yet implemented")


@pytest.mark.asyncio
@pytest.mark.playwright
async def test_greeting_shows_options(page: Page):
    """Test greeting card shows next action options."""
    pytest.skip("Frontend not yet implemented")


# Placeholder for when frontend is ready
"""
Example implementation when frontend exists:

@pytest.mark.asyncio
@pytest.mark.playwright
async def test_greeting_card_appears(page: Page):
    # Navigate to chat page
    await page.goto("http://localhost:3000/chat")
    
    # Wait for greeting card (max 8s as per requirements)
    greeting_card = page.locator('[data-testid="greeting-card"]')
    await expect(greeting_card).to_be_visible(timeout=8000)
    
    # Verify agent name
    agent_name = greeting_card.locator('[data-testid="agent-name"]')
    await expect(agent_name).to_have_text("Orchestrator")
    
    # Verify greeting text
    greeting_text = greeting_card.locator('[data-testid="greeting-text"]')
    await expect(greeting_text).to_contain_text("Hello")
"""

