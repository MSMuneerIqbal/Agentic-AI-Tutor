"""Metrics collection and export for observability."""

import time
from collections import defaultdict
from datetime import datetime
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)

# Metric name constants
METRIC_REQUEST_LATENCY = "request_latency"
METRIC_LESSON_GENERATION_LATENCY = "lesson_generation_latency"
METRIC_GUARDRAIL_TRIGGER_COUNT = "guardrail_trigger_count"
METRIC_TAVILY_ERRORS_COUNT = "tavily_errors_count"
METRIC_PINECONE_QUERY_LATENCY = "pinecone_query_latency"
METRIC_SESSIONS_ACTIVE = "sessions_active"
METRIC_GEMINI_TIMEOUT_COUNT = "gemini_timeout_count"
METRIC_TOOL_ERROR_COUNT = "tool_error_count"


class MetricsCollector:
    """Simple metrics collector (stub for Prometheus/CloudWatch integration)."""

    def __init__(self):
        """Initialize metrics collector."""
        self._counters: dict[str, int] = defaultdict(int)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._gauges: dict[str, float] = defaultdict(float)

    def increment_counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        """
        Increment a counter metric.

        Args:
            name: Metric name
            value: Increment value
            labels: Optional labels
        """
        key = self._make_key(name, labels)
        self._counters[key] += value
        logger.debug(f"Counter incremented: {key}={self._counters[key]}")

    def record_histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """
        Record a histogram value.

        Args:
            name: Metric name
            value: Value to record
            labels: Optional labels
        """
        key = self._make_key(name, labels)
        self._histograms[key].append(value)
        logger.debug(f"Histogram recorded: {key}={value}")

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """
        Set a gauge value.

        Args:
            name: Metric name
            value: Gauge value
            labels: Optional labels
        """
        key = self._make_key(name, labels)
        self._gauges[key] = value
        logger.debug(f"Gauge set: {key}={value}")

    def get_metrics(self) -> dict[str, Any]:
        """
        Get all metrics in Prometheus-compatible format.

        Returns:
            Dictionary of all metrics with detailed stats
        """
        return {
            "counters": dict(self._counters),
            "histograms": {
                name: {
                    "count": len(values),
                    "sum": sum(values),
                    "min": min(values) if values else 0.0,
                    "max": max(values) if values else 0.0,
                    "mean": sum(values) / len(values) if values else 0.0,
                    "p50": self._percentile(values, 50),
                    "p95": self._percentile(values, 95),
                    "p99": self._percentile(values, 99),
                }
                for name, values in self._histograms.items()
            },
            "gauges": dict(self._gauges),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    # Convenience methods for core metrics
    
    def track_request_latency(self, endpoint: str, latency: float) -> None:
        """Track HTTP request latency."""
        self.record_histogram(
            METRIC_REQUEST_LATENCY,
            latency,
            labels={"endpoint": endpoint}
        )
    
    def track_lesson_generation_latency(self, latency: float) -> None:
        """Track lesson generation latency (for p95 monitoring)."""
        self.record_histogram(METRIC_LESSON_GENERATION_LATENCY, latency)
    
    def increment_guardrail_trigger(self, agent: str, violation_type: str) -> None:
        """Increment guardrail trigger counter."""
        self.increment_counter(
            METRIC_GUARDRAIL_TRIGGER_COUNT,
            labels={"agent": agent, "type": violation_type}
        )
    
    def increment_tavily_error(self, error_type: str) -> None:
        """Increment TAVILY error counter."""
        self.increment_counter(
            METRIC_TAVILY_ERRORS_COUNT,
            labels={"error_type": error_type}
        )
    
    def track_pinecone_query_latency(self, latency: float, namespace: str = "default") -> None:
        """Track Pinecone query latency."""
        self.record_histogram(
            METRIC_PINECONE_QUERY_LATENCY,
            latency,
            labels={"namespace": namespace}
        )
    
    def set_sessions_active(self, count: int) -> None:
        """Set active sessions gauge."""
        self.set_gauge(METRIC_SESSIONS_ACTIVE, float(count))
    
    def increment_gemini_timeout(self) -> None:
        """Increment Gemini timeout counter."""
        self.increment_counter(METRIC_GEMINI_TIMEOUT_COUNT)
    
    def increment_tool_error(self, tool_name: str, error_type: str) -> None:
        """Increment tool error counter."""
        self.increment_counter(
            METRIC_TOOL_ERROR_COUNT,
            labels={"tool": tool_name, "error_type": error_type}
        )

    @staticmethod
    def _make_key(name: str, labels: dict[str, str] | None) -> str:
        """Create metric key with labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    @staticmethod
    def _percentile(values: list[float], percentile: int) -> float:
        """Calculate percentile."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]


# Global metrics collector
metrics_collector = MetricsCollector()


class Timer:
    """Context manager for timing operations."""

    def __init__(self, metric_name: str, labels: dict[str, str] | None = None):
        """
        Initialize timer.

        Args:
            metric_name: Metric name to record duration
            labels: Optional labels
        """
        self.metric_name = metric_name
        self.labels = labels
        self.start_time = None

    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        """Stop timer and record metric."""
        if self.start_time:
            duration = time.time() - self.start_time
            metrics_collector.record_histogram(
                self.metric_name,
                duration,
                self.labels,
            )


def get_metrics_collector() -> MetricsCollector:
    """
    Get global metrics collector.

    Returns:
        MetricsCollector instance
    """
    return metrics_collector

