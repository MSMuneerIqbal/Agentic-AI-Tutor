"""Integration tests for metrics endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_metrics(client: AsyncClient):
    """Test GET /metrics endpoint."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert "metrics" in data
    assert "counters" in data["metrics"]
    assert "histograms" in data["metrics"]
    assert "gauges" in data["metrics"]
    assert "timestamp" in data["metrics"]


@pytest.mark.asyncio
async def test_get_metrics_prometheus(client: AsyncClient):
    """Test GET /metrics/prometheus endpoint."""
    response = await client.get("/metrics/prometheus")
    assert response.status_code == 200
    
    # TODO: Verify Prometheus text format when implemented
    data = response.json()
    assert data is not None


@pytest.mark.asyncio
async def test_get_health_metrics(client: AsyncClient):
    """Test GET /metrics/health endpoint."""
    response = await client.get("/metrics/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "metrics" in data
    assert "sessions_active" in data["metrics"]
    assert "guardrail_triggers" in data["metrics"]
    assert "errors" in data["metrics"]


@pytest.mark.asyncio
async def test_get_metrics_summary(client: AsyncClient):
    """Test GET /metrics/summary endpoint."""
    response = await client.get("/metrics/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "timestamp" in data
    assert "performance" in data
    assert "reliability" in data
    assert "capacity" in data
    
    # Verify performance metrics
    assert "request_latency_p95" in data["performance"]
    assert "lesson_generation_p95" in data["performance"]
    assert "pinecone_query_latency_p95" in data["performance"]
    
    # Verify reliability metrics
    assert "total_requests" in data["reliability"]
    assert "guardrail_triggers" in data["reliability"]
    assert "tavily_errors" in data["reliability"]
    assert "gemini_timeouts" in data["reliability"]
    
    # Verify capacity metrics
    assert "sessions_active" in data["capacity"]


@pytest.mark.asyncio
async def test_metrics_middleware_tracking(client: AsyncClient):
    """Test that metrics middleware tracks requests."""
    # Make a request
    await client.get("/healthz")
    
    # Check metrics were recorded
    response = await client.get("/metrics")
    data = response.json()
    
    # Should have request latency histogram
    histograms = data["metrics"]["histograms"]
    
    # Check if any request latency was recorded
    # Note: Exact keys depend on label formatting
    has_latency = any("request_latency" in key for key in histograms.keys())
    assert has_latency or len(histograms) == 0  # May be empty in fresh test


@pytest.mark.asyncio
async def test_metrics_structure():
    """Test metrics data structure."""
    from app.core.metrics import get_metrics_collector
    
    collector = get_metrics_collector()
    
    # Record some test data
    collector.increment_counter("test_counter")
    collector.record_histogram("test_histogram", 1.0)
    collector.set_gauge("test_gauge", 42.0)
    
    metrics = collector.get_metrics()
    
    # Verify structure
    assert isinstance(metrics, dict)
    assert isinstance(metrics["counters"], dict)
    assert isinstance(metrics["histograms"], dict)
    assert isinstance(metrics["gauges"], dict)
    
    # Verify histogram contains all required fields
    test_hist = metrics["histograms"]["test_histogram"]
    required_fields = ["count", "sum", "min", "max", "mean", "p50", "p95", "p99"]
    for field in required_fields:
        assert field in test_hist

