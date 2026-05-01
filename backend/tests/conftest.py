"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def test_client():
    """Sync FastAPI test client (no live DB or external services needed)."""
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
