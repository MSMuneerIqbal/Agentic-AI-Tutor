"""
Rate Limiting Middleware for Phase 6
Implements intelligent rate limiting and security measures
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Types of rate limits."""
    GLOBAL = "global"
    PER_USER = "per_user"
    PER_IP = "per_ip"
    PER_ENDPOINT = "per_endpoint"

class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests: int
    window: int  # seconds
    rate_limit_type: RateLimitType
    security_level: SecurityLevel
    burst_limit: Optional[int] = None
    cooldown_period: Optional[int] = None

@dataclass
class RateLimitInfo:
    """Rate limit information for a request."""
    limit: int
    remaining: int
    reset_time: int
    retry_after: Optional[int] = None

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for API security."""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limits = self._initialize_rate_limits()
        self.blocked_ips = set()
        self.suspicious_ips = set()
        self.security_events = []
    
    def _initialize_rate_limits(self) -> Dict[str, RateLimit]:
        """Initialize rate limit configurations."""
        return {
            # Global rate limits
            "global": RateLimit(
                requests=1000,
                window=3600,  # 1 hour
                rate_limit_type=RateLimitType.GLOBAL,
                security_level=SecurityLevel.MEDIUM
            ),
            
            # Per-user rate limits
            "user_auth": RateLimit(
                requests=10,
                window=300,  # 5 minutes
                rate_limit_type=RateLimitType.PER_USER,
                security_level=SecurityLevel.HIGH,
                cooldown_period=900  # 15 minutes after limit exceeded
            ),
            
            "user_chat": RateLimit(
                requests=100,
                window=3600,  # 1 hour
                rate_limit_type=RateLimitType.PER_USER,
                security_level=SecurityLevel.MEDIUM
            ),
            
            "user_quiz": RateLimit(
                requests=50,
                window=1800,  # 30 minutes
                rate_limit_type=RateLimitType.PER_USER,
                security_level=SecurityLevel.MEDIUM
            ),
            
            # Per-IP rate limits
            "ip_general": RateLimit(
                requests=200,
                window=3600,  # 1 hour
                rate_limit_type=RateLimitType.PER_IP,
                security_level=SecurityLevel.MEDIUM
            ),
            
            "ip_auth": RateLimit(
                requests=20,
                window=300,  # 5 minutes
                rate_limit_type=RateLimitType.PER_IP,
                security_level=SecurityLevel.HIGH,
                cooldown_period=1800  # 30 minutes after limit exceeded
            ),
            
            # Per-endpoint rate limits
            "endpoint_rag": RateLimit(
                requests=200,
                window=3600,  # 1 hour
                rate_limit_type=RateLimitType.PER_ENDPOINT,
                security_level=SecurityLevel.MEDIUM
            ),
            
            "endpoint_analytics": RateLimit(
                requests=50,
                window=3600,  # 1 hour
                rate_limit_type=RateLimitType.PER_ENDPOINT,
                security_level=SecurityLevel.MEDIUM
            ),
            
            "endpoint_collaboration": RateLimit(
                requests=100,
                window=1800,  # 30 minutes
                rate_limit_type=RateLimitType.PER_ENDPOINT,
                security_level=SecurityLevel.MEDIUM
            )
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        try:
            # Get client information
            client_ip = self._get_client_ip(request)
            user_id = self._get_user_id(request)
            endpoint = self._get_endpoint(request)
            
            # Check if IP is blocked
            if client_ip in self.blocked_ips:
                return self._create_rate_limit_response(
                    "IP address is blocked due to suspicious activity",
                    403
                )
            
            # Determine applicable rate limits
            applicable_limits = self._get_applicable_limits(endpoint, user_id, client_ip)
            
            # Check rate limits
            for limit_name, rate_limit in applicable_limits.items():
                rate_limit_info = await self._check_rate_limit(
                    limit_name, rate_limit, client_ip, user_id, endpoint
                )
                
                if rate_limit_info.remaining <= 0:
                    # Rate limit exceeded
                    await self._handle_rate_limit_exceeded(
                        limit_name, rate_limit, client_ip, user_id, endpoint
                    )
                    
                    return self._create_rate_limit_response(
                        f"Rate limit exceeded for {limit_name}",
                        429,
                        rate_limit_info
                    )
            
            # Process request
            response = await call_next(request)
            
            # Update rate limit counters
            for limit_name, rate_limit in applicable_limits.items():
                await self._update_rate_limit_counter(
                    limit_name, rate_limit, client_ip, user_id, endpoint
                )
            
            # Add rate limit headers
            self._add_rate_limit_headers(response, applicable_limits)
            
            # Log security events
            await self._log_security_event(request, response, "request_processed")
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            return await call_next(request)
    
    async def _check_rate_limit(
        self, 
        limit_name: str, 
        rate_limit: RateLimit, 
        client_ip: str, 
        user_id: Optional[str], 
        endpoint: str
    ) -> RateLimitInfo:
        """Check if request exceeds rate limit."""
        try:
            redis_client = await get_redis_client()
            
            # Generate rate limit key
            key = self._generate_rate_limit_key(limit_name, rate_limit, client_ip, user_id, endpoint)
            
            # Get current count
            current_count = await redis_client.get(key)
            current_count = int(current_count) if current_count else 0
            
            # Check if limit is exceeded
            if current_count >= rate_limit.requests:
                # Check cooldown period
                if rate_limit.cooldown_period:
                    cooldown_key = f"cooldown:{key}"
                    cooldown_end = await redis_client.get(cooldown_key)
                    if cooldown_end:
                        cooldown_end_time = int(cooldown_end)
                        if time.time() < cooldown_end_time:
                            retry_after = int(cooldown_end_time - time.time())
                            return RateLimitInfo(
                                limit=rate_limit.requests,
                                remaining=0,
                                reset_time=cooldown_end_time,
                                retry_after=retry_after
                            )
                
                return RateLimitInfo(
                    limit=rate_limit.requests,
                    remaining=0,
                    reset_time=int(time.time()) + rate_limit.window
                )
            
            # Calculate remaining requests
            remaining = rate_limit.requests - current_count - 1
            
            return RateLimitInfo(
                limit=rate_limit.requests,
                remaining=max(0, remaining),
                reset_time=int(time.time()) + rate_limit.window
            )
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            # Allow request on error
            return RateLimitInfo(
                limit=rate_limit.requests,
                remaining=rate_limit.requests,
                reset_time=int(time.time()) + rate_limit.window
            )
    
    async def _update_rate_limit_counter(
        self, 
        limit_name: str, 
        rate_limit: RateLimit, 
        client_ip: str, 
        user_id: Optional[str], 
        endpoint: str
    ) -> None:
        """Update rate limit counter."""
        try:
            redis_client = await get_redis_client()
            
            # Generate rate limit key
            key = self._generate_rate_limit_key(limit_name, rate_limit, client_ip, user_id, endpoint)
            
            # Increment counter
            current_count = await redis_client.incr(key)
            
            # Set expiration if this is the first request
            if current_count == 1:
                await redis_client.expire(key, rate_limit.window)
            
        except Exception as e:
            logger.error(f"Failed to update rate limit counter: {e}")
    
    async def _handle_rate_limit_exceeded(
        self, 
        limit_name: str, 
        rate_limit: RateLimit, 
        client_ip: str, 
        user_id: Optional[str], 
        endpoint: str
    ) -> None:
        """Handle rate limit exceeded event."""
        try:
            # Log security event
            await self._log_security_event(
                None, None, "rate_limit_exceeded",
                {
                    "limit_name": limit_name,
                    "client_ip": client_ip,
                    "user_id": user_id,
                    "endpoint": endpoint,
                    "security_level": rate_limit.security_level.value
                }
            )
            
            # Apply security measures based on level
            if rate_limit.security_level == SecurityLevel.HIGH:
                # Add to suspicious IPs
                self.suspicious_ips.add(client_ip)
                
                # Set cooldown period
                if rate_limit.cooldown_period:
                    redis_client = await get_redis_client()
                    cooldown_key = f"cooldown:{self._generate_rate_limit_key(limit_name, rate_limit, client_ip, user_id, endpoint)}"
                    await redis_client.setex(
                        cooldown_key,
                        rate_limit.cooldown_period,
                        int(time.time()) + rate_limit.cooldown_period
                    )
            
            elif rate_limit.security_level == SecurityLevel.CRITICAL:
                # Block IP temporarily
                self.blocked_ips.add(client_ip)
                
                # Schedule unblock
                asyncio.create_task(self._schedule_ip_unblock(client_ip, 3600))  # 1 hour
            
        except Exception as e:
            logger.error(f"Failed to handle rate limit exceeded: {e}")
    
    async def _schedule_ip_unblock(self, client_ip: str, delay: int) -> None:
        """Schedule IP unblock after delay."""
        await asyncio.sleep(delay)
        self.blocked_ips.discard(client_ip)
        logger.info(f"Unblocked IP: {client_ip}")
    
    def _get_applicable_limits(self, endpoint: str, user_id: Optional[str], client_ip: str) -> Dict[str, RateLimit]:
        """Get applicable rate limits for request."""
        applicable = {}
        
        # Always apply global limit
        applicable["global"] = self.rate_limits["global"]
        
        # Apply IP-based limits
        applicable["ip_general"] = self.rate_limits["ip_general"]
        
        # Apply endpoint-specific limits
        if "/auth/" in endpoint:
            applicable["ip_auth"] = self.rate_limits["ip_auth"]
            if user_id:
                applicable["user_auth"] = self.rate_limits["user_auth"]
        
        elif "/chat/" in endpoint:
            if user_id:
                applicable["user_chat"] = self.rate_limits["user_chat"]
        
        elif "/quiz/" in endpoint:
            if user_id:
                applicable["user_quiz"] = self.rate_limits["user_quiz"]
        
        elif "/rag/" in endpoint:
            applicable["endpoint_rag"] = self.rate_limits["endpoint_rag"]
        
        elif "/analytics/" in endpoint:
            applicable["endpoint_analytics"] = self.rate_limits["endpoint_analytics"]
        
        elif "/collaboration/" in endpoint:
            applicable["endpoint_collaboration"] = self.rate_limits["endpoint_collaboration"]
        
        return applicable
    
    def _generate_rate_limit_key(
        self, 
        limit_name: str, 
        rate_limit: RateLimit, 
        client_ip: str, 
        user_id: Optional[str], 
        endpoint: str
    ) -> str:
        """Generate rate limit key based on type."""
        if rate_limit.rate_limit_type == RateLimitType.GLOBAL:
            return f"rate_limit:{limit_name}:global"
        elif rate_limit.rate_limit_type == RateLimitType.PER_USER and user_id:
            return f"rate_limit:{limit_name}:user:{user_id}"
        elif rate_limit.rate_limit_type == RateLimitType.PER_IP:
            return f"rate_limit:{limit_name}:ip:{client_ip}"
        elif rate_limit.rate_limit_type == RateLimitType.PER_ENDPOINT:
            return f"rate_limit:{limit_name}:endpoint:{endpoint}"
        else:
            return f"rate_limit:{limit_name}:ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """Get user ID from request."""
        # This would typically extract from JWT token or session
        return request.headers.get("X-User-ID")
    
    def _get_endpoint(self, request: Request) -> str:
        """Get endpoint path."""
        return request.url.path
    
    def _create_rate_limit_response(
        self, 
        message: str, 
        status_code: int, 
        rate_limit_info: Optional[RateLimitInfo] = None
    ) -> JSONResponse:
        """Create rate limit response."""
        response_data = {
            "error": "Rate limit exceeded",
            "message": message,
            "status_code": status_code
        }
        
        if rate_limit_info:
            response_data.update({
                "limit": rate_limit_info.limit,
                "remaining": rate_limit_info.remaining,
                "reset_time": rate_limit_info.reset_time
            })
            
            if rate_limit_info.retry_after:
                response_data["retry_after"] = rate_limit_info.retry_after
        
        response = JSONResponse(content=response_data, status_code=status_code)
        
        # Add rate limit headers
        if rate_limit_info:
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info.limit)
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.remaining)
            response.headers["X-RateLimit-Reset"] = str(rate_limit_info.reset_time)
            
            if rate_limit_info.retry_after:
                response.headers["Retry-After"] = str(rate_limit_info.retry_after)
        
        return response
    
    def _add_rate_limit_headers(self, response: Response, applicable_limits: Dict[str, RateLimit]) -> None:
        """Add rate limit headers to response."""
        # Use the most restrictive limit for headers
        most_restrictive = min(applicable_limits.values(), key=lambda x: x.requests)
        
        response.headers["X-RateLimit-Limit"] = str(most_restrictive.requests)
        response.headers["X-RateLimit-Window"] = str(most_restrictive.window)
        response.headers["X-RateLimit-Type"] = most_restrictive.rate_limit_type.value
    
    async def _log_security_event(
        self, 
        request: Optional[Request], 
        response: Optional[Response], 
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log security event."""
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "metadata": metadata or {}
            }
            
            if request:
                event["client_ip"] = self._get_client_ip(request)
                event["user_id"] = self._get_user_id(request)
                event["endpoint"] = self._get_endpoint(request)
                event["method"] = request.method
                event["user_agent"] = request.headers.get("User-Agent")
            
            if response:
                event["status_code"] = response.status_code
            
            # Store security event
            self.security_events.append(event)
            
            # Keep only recent events
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-500:]
            
            # Log to monitoring service
            if event_type in ["rate_limit_exceeded", "suspicious_activity"]:
                logger.warning(f"Security event: {event_type} - {event}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events."""
        return self.security_events[-limit:]
    
    async def get_rate_limit_status(self, client_ip: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current rate limit status for client."""
        try:
            status = {
                "client_ip": client_ip,
                "user_id": user_id,
                "is_blocked": client_ip in self.blocked_ips,
                "is_suspicious": client_ip in self.suspicious_ips,
                "rate_limits": {}
            }
            
            redis_client = await get_redis_client()
            
            # Check each rate limit
            for limit_name, rate_limit in self.rate_limits.items():
                key = self._generate_rate_limit_key(limit_name, rate_limit, client_ip, user_id, "")
                current_count = await redis_client.get(key)
                current_count = int(current_count) if current_count else 0
                
                status["rate_limits"][limit_name] = {
                    "current": current_count,
                    "limit": rate_limit.requests,
                    "remaining": max(0, rate_limit.requests - current_count),
                    "window": rate_limit.window,
                    "type": rate_limit.rate_limit_type.value,
                    "security_level": rate_limit.security_level.value
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return {"error": str(e)}
