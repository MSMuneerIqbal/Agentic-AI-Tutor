"""Application configuration and settings."""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = ""  # Required: set OPENAI_API_KEY in .env
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Database Configuration
    database_url: str = ""  # Required: set DATABASE_URL in .env

    # Redis Configuration (unused — kept for backwards compat)
    redis_url: str = "redis://localhost:6379/0"

    # Pinecone Configuration
    pinecone_api_key: str = ""  # Required: set PINECONE_API_KEY in .env
    pinecone_env: str = ""
    pinecone_index_name: str = "tutor-lms"

    # Application Configuration
    secret_key: str = ""  # Set SECRET_KEY in .env
    port: int = 8000
    environment: str = "development"

    # Frontend URLs (for CORS)
    frontend_url: str = "http://localhost:3000"
    allowed_origins: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"

    # Logging
    log_level: str = "INFO"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse allowed origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() in ("development", "dev")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() in ("production", "prod")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

