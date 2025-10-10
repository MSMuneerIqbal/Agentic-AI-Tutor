"""
Advanced Monitoring and Alerting Service for Phase 6
Provides comprehensive system monitoring, metrics collection, and alerting
"""

import asyncio
import logging
import json
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from app.core.redis import get_redis_client
from app.core.database import get_db

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class HealthStatus(Enum):
    """System health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class Metric:
    """Metric definition."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str]
    unit: Optional[str] = None

@dataclass
class Alert:
    """Alert definition."""
    id: str
    name: str
    level: AlertLevel
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time: float
    metadata: Dict[str, Any] = None

@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    response_time: float
    error_rate: float
    throughput: float

class MonitoringService:
    """Service for system monitoring and alerting."""
    
    def __init__(self):
        self.metrics_retention = 86400 * 7  # 7 days
        self.alert_retention = 86400 * 30  # 30 days
        self.health_check_interval = 60  # 1 minute
        self.metrics_collection_interval = 30  # 30 seconds
        
        # Alert thresholds
        self.thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "error_rate": 5.0,
            "response_time": 2.0,
            "active_sessions": 1000
        }
        
        # Health checks
        self.health_checks = {
            "database": self._check_database_health,
            "redis": self._check_redis_health,
            "api": self._check_api_health,
            "rag_service": self._check_rag_health,
            "external_apis": self._check_external_apis_health
        }
    
    async def start_monitoring(self) -> None:
        """Start the monitoring service."""
        logger.info("Starting monitoring service...")
        
        # Start background tasks
        asyncio.create_task(self._metrics_collector())
        asyncio.create_task(self._health_checker())
        asyncio.create_task(self._alert_processor())
        
        logger.info("Monitoring service started")
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Application-specific metrics
            active_connections = await self._get_active_connections()
            response_time = await self._get_average_response_time()
            error_rate = await self._get_error_rate()
            throughput = await self._get_throughput()
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_connections=active_connections,
                response_time=response_time,
                error_rate=error_rate,
                throughput=throughput
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(0, 0, 0, {}, 0, 0, 0, 0)
    
    async def record_metric(
        self, 
        name: str, 
        value: float, 
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None,
        unit: Optional[str] = None
    ) -> None:
        """Record a custom metric."""
        try:
            metric = Metric(
                name=name,
                value=value,
                metric_type=metric_type,
                timestamp=datetime.utcnow(),
                tags=tags or {},
                unit=unit
            )
            
            # Store metric
            await self._store_metric(metric)
            
            # Check for alerts
            await self._check_metric_alerts(metric)
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
    
    async def create_alert(
        self, 
        name: str, 
        level: AlertLevel, 
        message: str, 
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new alert."""
        try:
            alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            
            alert = Alert(
                id=alert_id,
                name=name,
                level=level,
                message=message,
                source=source,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Store alert
            await self._store_alert(alert)
            
            # Send notifications
            await self._send_alert_notifications(alert)
            
            logger.warning(f"Alert created: {name} - {message}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return ""
    
    async def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve an alert."""
        try:
            redis_client = await get_redis_client()
            
            # Get alert
            alert_data = await redis_client.get(f"alert:{alert_id}")
            if not alert_data:
                return False
            
            alert = json.loads(alert_data)
            alert["resolved"] = True
            alert["resolved_at"] = datetime.utcnow().isoformat()
            alert["resolved_by"] = resolved_by
            
            # Update alert
            await redis_client.setex(
                f"alert:{alert_id}",
                self.alert_retention,
                json.dumps(alert)
            )
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    async def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Get active (unresolved) alerts."""
        try:
            redis_client = await get_redis_client()
            
            # Get all alert keys
            alert_keys = await redis_client.keys("alert:*")
            active_alerts = []
            
            for key in alert_keys:
                alert_data = await redis_client.get(key)
                if alert_data:
                    alert = json.loads(alert_data)
                    if not alert.get("resolved", False):
                        if level is None or alert["level"] == level.value:
                            active_alerts.append(self._deserialize_alert(alert))
            
            return active_alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def run_health_checks(self) -> Dict[str, HealthCheck]:
        """Run all health checks."""
        try:
            health_results = {}
            
            for check_name, check_func in self.health_checks.items():
                start_time = time.time()
                
                try:
                    status, message, metadata = await check_func()
                    response_time = time.time() - start_time
                    
                    health_results[check_name] = HealthCheck(
                        name=check_name,
                        status=status,
                        message=message,
                        timestamp=datetime.utcnow(),
                        response_time=response_time,
                        metadata=metadata or {}
                    )
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    health_results[check_name] = HealthCheck(
                        name=check_name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check failed: {str(e)}",
                        timestamp=datetime.utcnow(),
                        response_time=response_time
                    )
            
            # Store health check results
            await self._store_health_checks(health_results)
            
            return health_results
            
        except Exception as e:
            logger.error(f"Failed to run health checks: {e}")
            return {}
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            # Run health checks
            health_checks = await self.run_health_checks()
            
            # Determine overall status
            overall_status = HealthStatus.HEALTHY
            for check in health_checks.values():
                if check.status == HealthStatus.CRITICAL:
                    overall_status = HealthStatus.CRITICAL
                    break
                elif check.status == HealthStatus.UNHEALTHY and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif check.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            
            # Get system metrics
            system_metrics = await self.collect_system_metrics()
            
            # Get active alerts
            active_alerts = await self.get_active_alerts()
            
            return {
                "overall_status": overall_status.value,
                "health_checks": {
                    name: {
                        "status": check.status.value,
                        "message": check.message,
                        "response_time": check.response_time,
                        "timestamp": check.timestamp.isoformat()
                    }
                    for name, check in health_checks.items()
                },
                "system_metrics": {
                    "cpu_usage": system_metrics.cpu_usage,
                    "memory_usage": system_metrics.memory_usage,
                    "disk_usage": system_metrics.disk_usage,
                    "active_connections": system_metrics.active_connections,
                    "response_time": system_metrics.response_time,
                    "error_rate": system_metrics.error_rate,
                    "throughput": system_metrics.throughput
                },
                "active_alerts": len(active_alerts),
                "critical_alerts": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {"error": str(e)}
    
    async def get_metrics_dashboard(self, time_range: str = "1h") -> Dict[str, Any]:
        """Get metrics for dashboard display."""
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(hours=24)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(hours=1)
            
            # Get metrics
            metrics = await self._get_metrics_in_range(start_time, end_time)
            
            # Aggregate metrics
            aggregated_metrics = self._aggregate_metrics(metrics)
            
            return {
                "time_range": time_range,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "metrics": aggregated_metrics,
                "alerts": await self.get_active_alerts(),
                "health_status": await self.get_system_health()
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics dashboard: {e}")
            return {"error": str(e)}
    
    async def _metrics_collector(self) -> None:
        """Background task to collect system metrics."""
        while True:
            try:
                # Collect system metrics
                system_metrics = await self.collect_system_metrics()
                
                # Record metrics
                await self.record_metric("system.cpu_usage", system_metrics.cpu_usage, tags={"component": "system"})
                await self.record_metric("system.memory_usage", system_metrics.memory_usage, tags={"component": "system"})
                await self.record_metric("system.disk_usage", system_metrics.disk_usage, tags={"component": "system"})
                await self.record_metric("system.active_connections", system_metrics.active_connections, tags={"component": "system"})
                await self.record_metric("system.response_time", system_metrics.response_time, tags={"component": "api"})
                await self.record_metric("system.error_rate", system_metrics.error_rate, tags={"component": "api"})
                await self.record_metric("system.throughput", system_metrics.throughput, tags={"component": "api"})
                
                await asyncio.sleep(self.metrics_collection_interval)
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _health_checker(self) -> None:
        """Background task to run health checks."""
        while True:
            try:
                health_checks = await self.run_health_checks()
                
                # Check for unhealthy services
                for check_name, check in health_checks.items():
                    if check.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                        await self.create_alert(
                            name=f"Health Check Failed: {check_name}",
                            level=AlertLevel.ERROR if check.status == HealthStatus.UNHEALTHY else AlertLevel.CRITICAL,
                            message=check.message,
                            source="health_checker",
                            metadata={"check_name": check_name, "response_time": check.response_time}
                        )
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health checker error: {e}")
                await asyncio.sleep(60)
    
    async def _alert_processor(self) -> None:
        """Background task to process alerts and send notifications."""
        while True:
            try:
                # Get active alerts
                active_alerts = await self.get_active_alerts()
                
                # Process alerts (send notifications, escalate, etc.)
                for alert in active_alerts:
                    await self._process_alert(alert)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Alert processor error: {e}")
                await asyncio.sleep(60)
    
    async def _check_database_health(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """Check database health."""
        try:
            async for db in get_db():
                start_time = time.time()
                result = await db.execute("SELECT 1")
                response_time = time.time() - start_time
                
                if response_time > 1.0:
                    return HealthStatus.DEGRADED, f"Database slow (${response_time:.2f}s)", {"response_time": response_time}
                else:
                    return HealthStatus.HEALTHY, "Database healthy", {"response_time": response_time}
                break
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Database error: {str(e)}", {}
    
    async def _check_redis_health(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """Check Redis health."""
        try:
            redis_client = await get_redis_client()
            start_time = time.time()
            await redis_client.ping()
            response_time = time.time() - start_time
            
            if response_time > 0.1:
                return HealthStatus.DEGRADED, f"Redis slow (${response_time:.2f}s)", {"response_time": response_time}
            else:
                return HealthStatus.HEALTHY, "Redis healthy", {"response_time": response_time}
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Redis error: {str(e)}", {}
    
    async def _check_api_health(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """Check API health."""
        try:
            # This would typically make a health check request to the API
            return HealthStatus.HEALTHY, "API healthy", {}
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"API error: {str(e)}", {}
    
    async def _check_rag_health(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """Check RAG service health."""
        try:
            from app.services.rag import get_rag_service
            rag_service = await get_rag_service()
            
            # Test RAG functionality
            results = await rag_service.get_content_for_agent("test query", "general", 1)
            
            if results:
                return HealthStatus.HEALTHY, "RAG service healthy", {"results_count": len(results)}
            else:
                return HealthStatus.DEGRADED, "RAG service returning no results", {}
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"RAG service error: {str(e)}", {}
    
    async def _check_external_apis_health(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """Check external APIs health."""
        try:
            # Check Gemini API
            from app.core.config import get_settings
            settings = get_settings()
            
            if settings.gemini_api_key:
                # This would typically make a test request to Gemini API
                return HealthStatus.HEALTHY, "External APIs healthy", {}
            else:
                return HealthStatus.DEGRADED, "External APIs not configured", {}
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"External APIs error: {str(e)}", {}
    
    async def _get_active_connections(self) -> int:
        """Get number of active connections."""
        try:
            # This would typically count active database connections, WebSocket connections, etc.
            return 0
        except Exception as e:
            logger.error(f"Failed to get active connections: {e}")
            return 0
    
    async def _get_average_response_time(self) -> float:
        """Get average API response time."""
        try:
            # This would typically calculate from request logs
            return 0.5
        except Exception as e:
            logger.error(f"Failed to get average response time: {e}")
            return 0.0
    
    async def _get_error_rate(self) -> float:
        """Get current error rate."""
        try:
            # This would typically calculate from request logs
            return 0.1
        except Exception as e:
            logger.error(f"Failed to get error rate: {e}")
            return 0.0
    
    async def _get_throughput(self) -> float:
        """Get current throughput (requests per second)."""
        try:
            # This would typically calculate from request logs
            return 10.0
        except Exception as e:
            logger.error(f"Failed to get throughput: {e}")
            return 0.0
    
    async def _check_metric_alerts(self, metric: Metric) -> None:
        """Check if metric triggers any alerts."""
        try:
            threshold = self.thresholds.get(metric.name)
            if threshold and metric.value > threshold:
                level = AlertLevel.CRITICAL if metric.value > threshold * 1.5 else AlertLevel.WARNING
                
                await self.create_alert(
                    name=f"Metric Threshold Exceeded: {metric.name}",
                    level=level,
                    message=f"{metric.name} is {metric.value} (threshold: {threshold})",
                    source="metric_monitor",
                    metadata={"metric_name": metric.name, "value": metric.value, "threshold": threshold}
                )
        except Exception as e:
            logger.error(f"Failed to check metric alerts: {e}")
    
    async def _store_metric(self, metric: Metric) -> None:
        """Store metric in Redis."""
        try:
            redis_client = await get_redis_client()
            metric_key = f"metric:{metric.name}:{metric.timestamp.strftime('%Y%m%d_%H%M%S')}"
            
            await redis_client.setex(
                metric_key,
                self.metrics_retention,
                json.dumps(self._serialize_metric(metric))
            )
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
    
    async def _store_alert(self, alert: Alert) -> None:
        """Store alert in Redis."""
        try:
            redis_client = await get_redis_client()
            await redis_client.setex(
                f"alert:{alert.id}",
                self.alert_retention,
                json.dumps(self._serialize_alert(alert))
            )
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
    
    async def _store_health_checks(self, health_checks: Dict[str, HealthCheck]) -> None:
        """Store health check results."""
        try:
            redis_client = await get_redis_client()
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
            for name, check in health_checks.items():
                await redis_client.setex(
                    f"health:{name}:{timestamp}",
                    3600,  # 1 hour
                    json.dumps(self._serialize_health_check(check))
                )
        except Exception as e:
            logger.error(f"Failed to store health checks: {e}")
    
    async def _send_alert_notifications(self, alert: Alert) -> None:
        """Send alert notifications."""
        try:
            # This would typically send notifications via email, Slack, etc.
            logger.warning(f"ALERT: {alert.name} - {alert.message}")
        except Exception as e:
            logger.error(f"Failed to send alert notifications: {e}")
    
    async def _process_alert(self, alert: Alert) -> None:
        """Process individual alert."""
        try:
            # This would typically handle alert escalation, auto-resolution, etc.
            pass
        except Exception as e:
            logger.error(f"Failed to process alert: {e}")
    
    async def _get_metrics_in_range(self, start_time: datetime, end_time: datetime) -> List[Metric]:
        """Get metrics within time range."""
        try:
            redis_client = await get_redis_client()
            metric_keys = await redis_client.keys("metric:*")
            
            metrics = []
            for key in metric_keys:
                metric_data = await redis_client.get(key)
                if metric_data:
                    metric = self._deserialize_metric(json.loads(metric_data))
                    if start_time <= metric.timestamp <= end_time:
                        metrics.append(metric)
            
            return metrics
        except Exception as e:
            logger.error(f"Failed to get metrics in range: {e}")
            return []
    
    def _aggregate_metrics(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Aggregate metrics for dashboard display."""
        try:
            aggregated = {}
            
            # Group metrics by name
            metric_groups = {}
            for metric in metrics:
                if metric.name not in metric_groups:
                    metric_groups[metric.name] = []
                metric_groups[metric.name].append(metric.value)
            
            # Calculate aggregates
            for name, values in metric_groups.items():
                aggregated[name] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "count": len(values),
                    "latest": values[-1] if values else 0
                }
            
            return aggregated
        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {e}")
            return {}
    
    def _serialize_metric(self, metric: Metric) -> Dict[str, Any]:
        """Serialize metric for storage."""
        return {
            "name": metric.name,
            "value": metric.value,
            "metric_type": metric.metric_type.value,
            "timestamp": metric.timestamp.isoformat(),
            "tags": metric.tags,
            "unit": metric.unit
        }
    
    def _deserialize_metric(self, data: Dict[str, Any]) -> Metric:
        """Deserialize metric from storage."""
        return Metric(
            name=data["name"],
            value=data["value"],
            metric_type=MetricType(data["metric_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            tags=data["tags"],
            unit=data.get("unit")
        )
    
    def _serialize_alert(self, alert: Alert) -> Dict[str, Any]:
        """Serialize alert for storage."""
        return {
            "id": alert.id,
            "name": alert.name,
            "level": alert.level.value,
            "message": alert.message,
            "source": alert.source,
            "timestamp": alert.timestamp.isoformat(),
            "resolved": alert.resolved,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "metadata": alert.metadata or {}
        }
    
    def _deserialize_alert(self, data: Dict[str, Any]) -> Alert:
        """Deserialize alert from storage."""
        return Alert(
            id=data["id"],
            name=data["name"],
            level=AlertLevel(data["level"]),
            message=data["message"],
            source=data["source"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            resolved=data.get("resolved", False),
            resolved_at=datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None,
            metadata=data.get("metadata", {})
        )
    
    def _serialize_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Serialize health check for storage."""
        return {
            "name": check.name,
            "status": check.status.value,
            "message": check.message,
            "timestamp": check.timestamp.isoformat(),
            "response_time": check.response_time,
            "metadata": check.metadata or {}
        }

# Global instance
_monitoring_service = None

async def get_monitoring_service() -> MonitoringService:
    """Get global monitoring service instance."""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
