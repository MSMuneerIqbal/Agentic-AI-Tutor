"""Unit tests for metrics collection."""

import pytest

from app.core.metrics import MetricsCollector, Timer, get_metrics_collector


def test_metrics_collector_counter():
    """Test counter metrics."""
    collector = MetricsCollector()
    
    collector.increment_counter("test_counter")
    collector.increment_counter("test_counter")
    collector.increment_counter("test_counter", value=3)
    
    metrics = collector.get_metrics()
    assert metrics["counters"]["test_counter"] == 5


def test_metrics_collector_histogram():
    """Test histogram metrics."""
    collector = MetricsCollector()
    
    collector.record_histogram("test_histogram", 100.0)
    collector.record_histogram("test_histogram", 200.0)
    collector.record_histogram("test_histogram", 150.0)
    
    metrics = collector.get_metrics()
    histogram = metrics["histograms"]["test_histogram"]
    
    assert histogram["count"] == 3
    assert histogram["sum"] == 450.0
    assert histogram["min"] == 100.0
    assert histogram["max"] == 200.0
    assert histogram["mean"] == 150.0


def test_metrics_collector_gauge():
    """Test gauge metrics."""
    collector = MetricsCollector()
    
    collector.set_gauge("test_gauge", 42.0)
    collector.set_gauge("test_gauge", 100.0)
    
    metrics = collector.get_metrics()
    assert metrics["gauges"]["test_gauge"] == 100.0


def test_metrics_collector_with_labels():
    """Test metrics with labels."""
    collector = MetricsCollector()
    
    collector.increment_counter("requests", labels={"endpoint": "/api/v1/sessions"})
    collector.increment_counter("requests", labels={"endpoint": "/api/v1/sessions"})
    collector.increment_counter("requests", labels={"endpoint": "/metrics"})
    
    metrics = collector.get_metrics()
    assert metrics["counters"]["requests{endpoint=/api/v1/sessions}"] == 2
    assert metrics["counters"]["requests{endpoint=/metrics}"] == 1


def test_metrics_percentiles():
    """Test percentile calculations."""
    collector = MetricsCollector()
    
    # Add values: 1-100
    for i in range(1, 101):
        collector.record_histogram("latency", float(i))
    
    metrics = collector.get_metrics()
    histogram = metrics["histograms"]["latency"]
    
    assert histogram["count"] == 100
    assert 48 <= histogram["p50"] <= 52  # Around 50
    assert 93 <= histogram["p95"] <= 97  # Around 95
    assert 97 <= histogram["p99"] <= 100  # Around 99


def test_timer_context_manager():
    """Test Timer context manager records to the global collector."""
    import time

    global_collector = get_metrics_collector()
    before = len(global_collector._histograms.get("test_operation_timer", []))

    with Timer("test_operation_timer"):
        time.sleep(0.05)

    after_values = global_collector._histograms.get("test_operation_timer", [])
    assert len(after_values) == before + 1
    assert after_values[-1] >= 0.04  # at least 40 ms recorded


def test_convenience_methods():
    """Test convenience methods for core metrics."""
    collector = MetricsCollector()

    collector.track_request_latency("/api/v1/sessions", 0.5)
    collector.track_lesson_generation_latency(2.5)
    collector.increment_guardrail_trigger("Tutor", "output_validation")
    collector.increment_tavily_error("timeout")
    collector.track_pinecone_query_latency(0.3, namespace="docker-k8s")
    collector.set_sessions_active(42)
    collector.increment_gemini_timeout()
    collector.increment_tool_error("pinecone", "connection_error")

    metrics = collector.get_metrics()

    assert "request_latency{endpoint=/api/v1/sessions}" in str(metrics["histograms"])
    assert "lesson_generation_latency" in metrics["histograms"]
    assert "guardrail_trigger_count{agent=Tutor,type=output_validation}" in str(metrics["counters"])
    assert "tavily_errors_count{error_type=timeout}" in str(metrics["counters"])
    assert "pinecone_query_latency{namespace=docker-k8s}" in str(metrics["histograms"])
    assert metrics["gauges"]["sessions_active"] == 42.0
    assert metrics["counters"]["gemini_timeout_count"] == 1
    assert "tool_error_count{error_type=connection_error,tool=pinecone}" in str(metrics["counters"])


def test_metrics_timestamp():
    """Test that metrics include timestamp."""
    collector = MetricsCollector()
    metrics = collector.get_metrics()
    
    assert "timestamp" in metrics
    assert metrics["timestamp"].endswith("Z")  # UTC format

