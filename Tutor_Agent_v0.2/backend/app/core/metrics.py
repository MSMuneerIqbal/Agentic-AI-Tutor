"""Metrics collection and export stubs."""

import time
from collections import defaultdict
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


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
        Get all metrics.

        Returns:
            Dictionary of all metrics
        """
        return {
            "counters": dict(self._counters),
            "histograms": {
                name: {
                    "count": len(values),
                    "sum": sum(values),
                    "p50": self._percentile(values, 50),
                    "p95": self._percentile(values, 95),
                    "p99": self._percentile(values, 99),
                }
                for name, values in self._histograms.items()
            },
            "gauges": dict(self._gauges),
        }

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

