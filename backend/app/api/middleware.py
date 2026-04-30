"""FastAPI middleware for metrics and observability."""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track request latency and other metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track metrics.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        start_time = time.time()
        
        # Track request
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            # Call next middleware/handler
            response = await call_next(request)
            
            # Calculate latency
            latency = time.time() - start_time
            
            # Track metrics
            metrics.track_request_latency(endpoint, latency)
            
            # Log slow requests (>1s)
            if latency > 1.0:
                logger.warning(
                    f"Slow request detected",
                    extra={
                        "endpoint": endpoint,
                        "latency": latency,
                        "status_code": response.status_code,
                    },
                )
            
            return response
            
        except Exception as e:
            # Track error
            latency = time.time() - start_time
            metrics.track_request_latency(endpoint, latency)
            
            logger.error(
                f"Request failed",
                extra={
                    "endpoint": endpoint,
                    "latency": latency,
                    "error": str(e),
                },
            )
            raise


class SessionCounterMiddleware(BaseHTTPMiddleware):
    """Middleware to track active sessions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Track active sessions.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # TODO: Implement session counting from Redis
        # For now, just pass through
        response = await call_next(request)
        return response

