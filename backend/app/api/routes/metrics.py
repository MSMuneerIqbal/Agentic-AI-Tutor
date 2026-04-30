"""Metrics and observability endpoints."""

from fastapi import APIRouter

from app.core.metrics import get_metrics_collector

router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    """
    Get application metrics (Prometheus-compatible format).

    Returns comprehensive metrics:
    - Counters: guardrail_trigger_count, tavily_errors_count, etc.
    - Histograms: request_latency (with p50, p95, p99), lesson_generation_latency
    - Gauges: sessions_active

    Can be scraped by Prometheus or viewed directly for monitoring.
    """
    metrics = get_metrics_collector().get_metrics()
    return {"metrics": metrics}


@router.get("/metrics/prometheus")
async def get_metrics_prometheus():
    """
    Get metrics in Prometheus text format.

    TODO: Implement proper Prometheus text format export.
    For now, returns JSON format.
    """
    metrics = get_metrics_collector().get_metrics()
    
    # TODO: Convert to Prometheus text format
    # Example:
    # # HELP request_latency Request latency in seconds
    # # TYPE request_latency histogram
    # request_latency_bucket{endpoint="/api/v1/sessions/start",le="0.1"} 10
    # request_latency_count{endpoint="/api/v1/sessions/start"} 100
    # request_latency_sum{endpoint="/api/v1/sessions/start"} 5.2
    
    return metrics


@router.get("/metrics/health")
async def get_health_metrics():
    """
    Get health-related metrics for monitoring.

    Returns:
        Health status and key metrics
    """
    metrics = get_metrics_collector()
    all_metrics = metrics.get_metrics()
    
    # Extract key health indicators
    return {
        "status": "healthy",
        "metrics": {
            "sessions_active": all_metrics["gauges"].get("sessions_active", 0),
            "guardrail_triggers": sum(
                v for k, v in all_metrics["counters"].items()
                if "guardrail_trigger_count" in k
            ),
            "errors": {
                "tavily": sum(
                    v for k, v in all_metrics["counters"].items()
                    if "tavily_errors_count" in k
                ),
                "gemini_timeouts": all_metrics["counters"].get("gemini_timeout_count", 0),
                "tool_errors": sum(
                    v for k, v in all_metrics["counters"].items()
                    if "tool_error_count" in k
                ),
            },
        },
    }


@router.get("/metrics/summary")
async def get_metrics_summary():
    """
    Get human-readable metrics summary.

    Returns key metrics in a simplified format for dashboards.
    """
    metrics = get_metrics_collector().get_metrics()
    
    # Calculate summary statistics
    request_latencies = metrics["histograms"].get("request_latency", {})
    lesson_latencies = metrics["histograms"].get("lesson_generation_latency", {})
    
    return {
        "timestamp": metrics["timestamp"],
        "performance": {
            "request_latency_p95": request_latencies.get("p95", 0),
            "lesson_generation_p95": lesson_latencies.get("p95", 0),
            "pinecone_query_latency_p95": metrics["histograms"]
            .get("pinecone_query_latency", {})
            .get("p95", 0),
        },
        "reliability": {
            "total_requests": request_latencies.get("count", 0),
            "guardrail_triggers": sum(
                v
                for k, v in metrics["counters"].items()
                if "guardrail_trigger_count" in k
            ),
            "tavily_errors": sum(
                v for k, v in metrics["counters"].items() if "tavily_errors_count" in k
            ),
            "gemini_timeouts": metrics["counters"].get("gemini_timeout_count", 0),
        },
        "capacity": {
            "sessions_active": metrics["gauges"].get("sessions_active", 0),
        },
    }

