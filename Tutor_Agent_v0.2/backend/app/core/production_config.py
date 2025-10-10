"""
Production Configuration for Phase 6
Handles production-specific settings, deployment configurations, and environment management
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from app.core.config import Settings

logger = logging.getLogger(__name__)

class DeploymentEnvironment(Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class DatabaseType(Enum):
    """Database types."""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"

@dataclass
class ProductionSettings:
    """Production-specific settings."""
    environment: DeploymentEnvironment
    debug: bool
    log_level: str
    database_url: str
    redis_url: str
    secret_key: str
    cors_origins: list
    rate_limiting_enabled: bool
    monitoring_enabled: bool
    ssl_enabled: bool
    ssl_cert_path: Optional[str]
    ssl_key_path: Optional[str]
    worker_processes: int
    worker_connections: int
    max_requests: int
    max_requests_jitter: int
    timeout: int
    keepalive: int
    graceful_timeout: int
    preload_app: bool
    access_log: bool
    error_log: str
    pid_file: str
    user: Optional[str]
    group: Optional[str]
    tmp_upload_dir: str
    static_files_dir: str
    media_files_dir: str
    backup_enabled: bool
    backup_interval: int
    backup_retention: int
    health_check_interval: int
    metrics_collection_interval: int
    alert_notification_enabled: bool
    alert_email_recipients: list
    alert_slack_webhook: Optional[str]
    external_api_timeout: int
    external_api_retries: int
    cache_ttl: int
    session_timeout: int
    max_file_size: int
    allowed_file_types: list
    security_headers: Dict[str, str]
    rate_limit_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]

class ProductionConfig:
    """Production configuration manager."""
    
    def __init__(self):
        self.environment = self._get_environment()
        self.settings = self._load_production_settings()
    
    def _get_environment(self) -> DeploymentEnvironment:
        """Get current deployment environment."""
        env = os.getenv("DEPLOYMENT_ENVIRONMENT", "development").lower()
        
        if env == "production":
            return DeploymentEnvironment.PRODUCTION
        elif env == "staging":
            return DeploymentEnvironment.STAGING
        else:
            return DeploymentEnvironment.DEVELOPMENT
    
    def _load_production_settings(self) -> ProductionSettings:
        """Load production-specific settings."""
        base_settings = Settings()
        
        return ProductionSettings(
            environment=self.environment,
            debug=self.environment != DeploymentEnvironment.PRODUCTION,
            log_level=self._get_log_level(),
            database_url=self._get_database_url(),
            redis_url=self._get_redis_url(),
            secret_key=self._get_secret_key(),
            cors_origins=self._get_cors_origins(),
            rate_limiting_enabled=self._get_rate_limiting_enabled(),
            monitoring_enabled=self._get_monitoring_enabled(),
            ssl_enabled=self._get_ssl_enabled(),
            ssl_cert_path=self._get_ssl_cert_path(),
            ssl_key_path=self._get_ssl_key_path(),
            worker_processes=self._get_worker_processes(),
            worker_connections=self._get_worker_connections(),
            max_requests=self._get_max_requests(),
            max_requests_jitter=self._get_max_requests_jitter(),
            timeout=self._get_timeout(),
            keepalive=self._get_keepalive(),
            graceful_timeout=self._get_graceful_timeout(),
            preload_app=self._get_preload_app(),
            access_log=self._get_access_log(),
            error_log=self._get_error_log(),
            pid_file=self._get_pid_file(),
            user=self._get_user(),
            group=self._get_group(),
            tmp_upload_dir=self._get_tmp_upload_dir(),
            static_files_dir=self._get_static_files_dir(),
            media_files_dir=self._get_media_files_dir(),
            backup_enabled=self._get_backup_enabled(),
            backup_interval=self._get_backup_interval(),
            backup_retention=self._get_backup_retention(),
            health_check_interval=self._get_health_check_interval(),
            metrics_collection_interval=self._get_metrics_collection_interval(),
            alert_notification_enabled=self._get_alert_notification_enabled(),
            alert_email_recipients=self._get_alert_email_recipients(),
            alert_slack_webhook=self._get_alert_slack_webhook(),
            external_api_timeout=self._get_external_api_timeout(),
            external_api_retries=self._get_external_api_retries(),
            cache_ttl=self._get_cache_ttl(),
            session_timeout=self._get_session_timeout(),
            max_file_size=self._get_max_file_size(),
            allowed_file_types=self._get_allowed_file_types(),
            security_headers=self._get_security_headers(),
            rate_limit_config=self._get_rate_limit_config(),
            monitoring_config=self._get_monitoring_config()
        )
    
    def _get_log_level(self) -> str:
        """Get log level based on environment."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            return os.getenv("LOG_LEVEL", "INFO")
        elif self.environment == DeploymentEnvironment.STAGING:
            return os.getenv("LOG_LEVEL", "DEBUG")
        else:
            return os.getenv("LOG_LEVEL", "DEBUG")
    
    def _get_database_url(self) -> str:
        """Get database URL for production."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            return os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost:3306/tutor_agent_prod")
        else:
            return os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost:3306/tutor_agent_dev")
    
    def _get_redis_url(self) -> str:
        """Get Redis URL for production."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            return os.getenv("REDIS_URL", "redis://localhost:6379/0")
        else:
            return os.getenv("REDIS_URL", "redis://localhost:6379/1")
    
    def _get_secret_key(self) -> str:
        """Get secret key for production."""
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            if self.environment == DeploymentEnvironment.PRODUCTION:
                raise ValueError("SECRET_KEY must be set in production environment")
            else:
                secret_key = "dev-secret-key-change-in-production"
        
        return secret_key
    
    def _get_cors_origins(self) -> list:
        """Get CORS origins based on environment."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            origins = os.getenv("CORS_ORIGINS", "https://yourdomain.com,https://www.yourdomain.com")
            return [origin.strip() for origin in origins.split(",")]
        else:
            return ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
    
    def _get_rate_limiting_enabled(self) -> bool:
        """Get rate limiting enabled status."""
        return os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"
    
    def _get_monitoring_enabled(self) -> bool:
        """Get monitoring enabled status."""
        return os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    
    def _get_ssl_enabled(self) -> bool:
        """Get SSL enabled status."""
        return os.getenv("SSL_ENABLED", "false").lower() == "true"
    
    def _get_ssl_cert_path(self) -> Optional[str]:
        """Get SSL certificate path."""
        return os.getenv("SSL_CERT_PATH")
    
    def _get_ssl_key_path(self) -> Optional[str]:
        """Get SSL key path."""
        return os.getenv("SSL_KEY_PATH")
    
    def _get_worker_processes(self) -> int:
        """Get number of worker processes."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            return int(os.getenv("WORKER_PROCESSES", "4"))
        else:
            return int(os.getenv("WORKER_PROCESSES", "1"))
    
    def _get_worker_connections(self) -> int:
        """Get worker connections."""
        return int(os.getenv("WORKER_CONNECTIONS", "1000"))
    
    def _get_max_requests(self) -> int:
        """Get max requests per worker."""
        return int(os.getenv("MAX_REQUESTS", "1000"))
    
    def _get_max_requests_jitter(self) -> int:
        """Get max requests jitter."""
        return int(os.getenv("MAX_REQUESTS_JITTER", "100"))
    
    def _get_timeout(self) -> int:
        """Get worker timeout."""
        return int(os.getenv("TIMEOUT", "30"))
    
    def _get_keepalive(self) -> int:
        """Get keepalive timeout."""
        return int(os.getenv("KEEPALIVE", "2"))
    
    def _get_graceful_timeout(self) -> int:
        """Get graceful timeout."""
        return int(os.getenv("GRACEFUL_TIMEOUT", "30"))
    
    def _get_preload_app(self) -> bool:
        """Get preload app setting."""
        return os.getenv("PRELOAD_APP", "true").lower() == "true"
    
    def _get_access_log(self) -> bool:
        """Get access log setting."""
        return os.getenv("ACCESS_LOG", "true").lower() == "true"
    
    def _get_error_log(self) -> str:
        """Get error log path."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            return os.getenv("ERROR_LOG", "/var/log/tutor-agent/error.log")
        else:
            return os.getenv("ERROR_LOG", "error.log")
    
    def _get_pid_file(self) -> str:
        """Get PID file path."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            return os.getenv("PID_FILE", "/var/run/tutor-agent.pid")
        else:
            return os.getenv("PID_FILE", "tutor-agent.pid")
    
    def _get_user(self) -> Optional[str]:
        """Get user for running the application."""
        return os.getenv("APP_USER")
    
    def _get_group(self) -> Optional[str]:
        """Get group for running the application."""
        return os.getenv("APP_GROUP")
    
    def _get_tmp_upload_dir(self) -> str:
        """Get temporary upload directory."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            return os.getenv("TMP_UPLOAD_DIR", "/tmp/tutor-agent-uploads")
        else:
            return os.getenv("TMP_UPLOAD_DIR", "./tmp/uploads")
    
    def _get_static_files_dir(self) -> str:
        """Get static files directory."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            return os.getenv("STATIC_FILES_DIR", "/var/www/tutor-agent/static")
        else:
            return os.getenv("STATIC_FILES_DIR", "./static")
    
    def _get_media_files_dir(self) -> str:
        """Get media files directory."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            return os.getenv("MEDIA_FILES_DIR", "/var/www/tutor-agent/media")
        else:
            return os.getenv("MEDIA_FILES_DIR", "./media")
    
    def _get_backup_enabled(self) -> bool:
        """Get backup enabled status."""
        return os.getenv("BACKUP_ENABLED", "true").lower() == "true"
    
    def _get_backup_interval(self) -> int:
        """Get backup interval in hours."""
        return int(os.getenv("BACKUP_INTERVAL", "24"))
    
    def _get_backup_retention(self) -> int:
        """Get backup retention in days."""
        return int(os.getenv("BACKUP_RETENTION", "30"))
    
    def _get_health_check_interval(self) -> int:
        """Get health check interval in seconds."""
        return int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
    
    def _get_metrics_collection_interval(self) -> int:
        """Get metrics collection interval in seconds."""
        return int(os.getenv("METRICS_COLLECTION_INTERVAL", "30"))
    
    def _get_alert_notification_enabled(self) -> bool:
        """Get alert notification enabled status."""
        return os.getenv("ALERT_NOTIFICATION_ENABLED", "true").lower() == "true"
    
    def _get_alert_email_recipients(self) -> list:
        """Get alert email recipients."""
        recipients = os.getenv("ALERT_EMAIL_RECIPIENTS", "")
        return [email.strip() for email in recipients.split(",") if email.strip()]
    
    def _get_alert_slack_webhook(self) -> Optional[str]:
        """Get Slack webhook URL for alerts."""
        return os.getenv("ALERT_SLACK_WEBHOOK")
    
    def _get_external_api_timeout(self) -> int:
        """Get external API timeout in seconds."""
        return int(os.getenv("EXTERNAL_API_TIMEOUT", "30"))
    
    def _get_external_api_retries(self) -> int:
        """Get external API retry count."""
        return int(os.getenv("EXTERNAL_API_RETRIES", "3"))
    
    def _get_cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        return int(os.getenv("CACHE_TTL", "3600"))
    
    def _get_session_timeout(self) -> int:
        """Get session timeout in seconds."""
        return int(os.getenv("SESSION_TIMEOUT", "3600"))
    
    def _get_max_file_size(self) -> int:
        """Get max file size in bytes."""
        return int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    def _get_allowed_file_types(self) -> list:
        """Get allowed file types."""
        types = os.getenv("ALLOWED_FILE_TYPES", "pdf,doc,docx,txt,md")
        return [file_type.strip() for file_type in types.split(",")]
    
    def _get_security_headers(self) -> Dict[str, str]:
        """Get security headers configuration."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    def _get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return {
            "global_requests_per_hour": int(os.getenv("RATE_LIMIT_GLOBAL", "1000")),
            "user_requests_per_hour": int(os.getenv("RATE_LIMIT_USER", "100")),
            "ip_requests_per_hour": int(os.getenv("RATE_LIMIT_IP", "200")),
            "auth_requests_per_minute": int(os.getenv("RATE_LIMIT_AUTH", "10")),
            "burst_limit": int(os.getenv("RATE_LIMIT_BURST", "50")),
            "cooldown_period": int(os.getenv("RATE_LIMIT_COOLDOWN", "900"))
        }
    
    def _get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            "metrics_retention_days": int(os.getenv("METRICS_RETENTION_DAYS", "7")),
            "alert_retention_days": int(os.getenv("ALERT_RETENTION_DAYS", "30")),
            "health_check_timeout": int(os.getenv("HEALTH_CHECK_TIMEOUT", "10")),
            "cpu_threshold": float(os.getenv("CPU_THRESHOLD", "80.0")),
            "memory_threshold": float(os.getenv("MEMORY_THRESHOLD", "85.0")),
            "disk_threshold": float(os.getenv("DISK_THRESHOLD", "90.0")),
            "error_rate_threshold": float(os.getenv("ERROR_RATE_THRESHOLD", "5.0")),
            "response_time_threshold": float(os.getenv("RESPONSE_TIME_THRESHOLD", "2.0"))
        }
    
    def get_gunicorn_config(self) -> Dict[str, Any]:
        """Get Gunicorn configuration for production."""
        return {
            "bind": f"0.0.0.0:{os.getenv('PORT', '8000')}",
            "workers": self.settings.worker_processes,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "worker_connections": self.settings.worker_connections,
            "max_requests": self.settings.max_requests,
            "max_requests_jitter": self.settings.max_requests_jitter,
            "timeout": self.settings.timeout,
            "keepalive": self.settings.keepalive,
            "graceful_timeout": self.settings.graceful_timeout,
            "preload_app": self.settings.preload_app,
            "accesslog": self.settings.access_log,
            "errorlog": self.settings.error_log,
            "pidfile": self.settings.pid_file,
            "user": self.settings.user,
            "group": self.settings.group,
            "loglevel": self.settings.log_level.lower(),
            "capture_output": True,
            "enable_stdio_inheritance": True
        }
    
    def get_nginx_config(self) -> str:
        """Get Nginx configuration for production."""
        config = f"""
upstream tutor_agent {{
    server 127.0.0.1:{os.getenv('PORT', '8000')};
    keepalive 32;
}}

server {{
    listen 80;
    server_name {os.getenv('DOMAIN_NAME', 'localhost')};
    
    # Redirect HTTP to HTTPS in production
    {'return 301 https://$server_name$request_uri;' if self.settings.ssl_enabled else ''}
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=1r/s;
    
    location / {{
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://tutor_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }}
    
    location /auth/ {{
        limit_req zone=auth burst=5 nodelay;
        
        proxy_pass http://tutor_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /static/ {{
        alias {self.settings.static_files_dir}/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    location /media/ {{
        alias {self.settings.media_files_dir}/;
        expires 1M;
        add_header Cache-Control "public";
    }}
    
    # Health check endpoint
    location /health {{
        access_log off;
        proxy_pass http://tutor_agent;
    }}
}}
"""
        
        if self.settings.ssl_enabled:
            config += f"""
server {{
    listen 443 ssl http2;
    server_name {os.getenv('DOMAIN_NAME', 'localhost')};
    
    ssl_certificate {self.settings.ssl_cert_path};
    ssl_certificate_key {self.settings.ssl_key_path};
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Same location blocks as HTTP server
    location / {{
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://tutor_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }}
    
    location /auth/ {{
        limit_req zone=auth burst=5 nodelay;
        
        proxy_pass http://tutor_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /static/ {{
        alias {self.settings.static_files_dir}/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    location /media/ {{
        alias {self.settings.media_files_dir}/;
        expires 1M;
        add_header Cache-Control "public";
    }}
    
    location /health {{
        access_log off;
        proxy_pass http://tutor_agent;
    }}
}}
"""
        
        return config
    
    def get_docker_compose_config(self) -> Dict[str, Any]:
        """Get Docker Compose configuration for production."""
        return {
            "version": "3.8",
            "services": {
                "app": {
                    "build": ".",
                    "ports": [f"{os.getenv('PORT', '8000')}:8000"],
                    "environment": {
                        "DEPLOYMENT_ENVIRONMENT": "production",
                        "DATABASE_URL": self.settings.database_url,
                        "REDIS_URL": self.settings.redis_url,
                        "SECRET_KEY": self.settings.secret_key
                    },
                    "depends_on": ["mysql", "redis"],
                    "restart": "unless-stopped",
                    "volumes": [
                        f"{self.settings.static_files_dir}:/app/static",
                        f"{self.settings.media_files_dir}:/app/media"
                    ]
                },
                "mysql": {
                    "image": "mysql:8.0",
                    "environment": {
                        "MYSQL_ROOT_PASSWORD": os.getenv("MYSQL_ROOT_PASSWORD", "rootpassword"),
                        "MYSQL_DATABASE": "tutor_agent_prod",
                        "MYSQL_USER": "tutor_agent",
                        "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD", "password")
                    },
                    "volumes": [
                        "mysql_data:/var/lib/mysql",
                        "./backups:/backups"
                    ],
                    "restart": "unless-stopped"
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "volumes": [
                        "redis_data:/data"
                    ],
                    "restart": "unless-stopped"
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "./nginx.conf:/etc/nginx/nginx.conf",
                        f"{self.settings.ssl_cert_path}:/etc/ssl/certs/cert.pem" if self.settings.ssl_cert_path else "",
                        f"{self.settings.ssl_key_path}:/etc/ssl/private/key.pem" if self.settings.ssl_key_path else ""
                    ],
                    "depends_on": ["app"],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "mysql_data": {},
                "redis_data": {}
            }
        }
    
    def validate_production_config(self) -> List[str]:
        """Validate production configuration."""
        errors = []
        
        if self.environment == DeploymentEnvironment.PRODUCTION:
            # Check required production settings
            if not self.settings.secret_key or self.settings.secret_key == "dev-secret-key-change-in-production":
                errors.append("SECRET_KEY must be set to a secure value in production")
            
            if not self.settings.ssl_enabled:
                errors.append("SSL should be enabled in production")
            
            if self.settings.debug:
                errors.append("Debug mode should be disabled in production")
            
            if not self.settings.cors_origins or "localhost" in str(self.settings.cors_origins):
                errors.append("CORS origins should not include localhost in production")
            
            if not self.settings.rate_limiting_enabled:
                errors.append("Rate limiting should be enabled in production")
            
            if not self.settings.monitoring_enabled:
                errors.append("Monitoring should be enabled in production")
        
        return errors

# Global instance
_production_config = None

def get_production_config() -> ProductionConfig:
    """Get global production configuration instance."""
    global _production_config
    if _production_config is None:
        _production_config = ProductionConfig()
    return _production_config
