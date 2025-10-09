"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import metrics, profiles, sessions, websocket
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.metrics import get_metrics_collector
from app.core.redis import redis_client

settings = get_settings()

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Tutor GPT API")
    await redis_client.connect()
    logger.info("Redis connected")
    yield
    # Shutdown
    logger.info("Shutting down Tutor GPT API")
    await redis_client.disconnect()
    logger.info("Redis disconnected")


app = FastAPI(
    title="Tutor GPT API",
    description="Backend-first agentic tutoring system",
    version="0.1.0",
    lifespan=lifespan,
)

# Metrics middleware (first, to track all requests)
from app.api.middleware import MetricsMiddleware

app.add_middleware(MetricsMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(profiles.router, prefix="/api/v1", tags=["profiles"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(metrics.router, tags=["metrics"])


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Tutor GPT API",
        "version": "0.1.0",
        "docs": "/docs",
    }


# Metrics endpoints are now in app.api.routes.metrics

