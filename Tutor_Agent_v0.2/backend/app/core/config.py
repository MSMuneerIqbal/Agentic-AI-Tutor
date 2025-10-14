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

    # Gemini Configuration
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_api_key: str = "your_gemini_key_here"
    gemini_model: str = "gemini-2.0-flash-exp"
    embedding_model: str = "gemini-embedding-1.0"

    # Database Configuration
    database_url: str = "mongodb+srv://mustafaadeel989_db_user:xhuqP857lVk2kOlP@cluster0.4nszshk.mongodb.net/tutor_gpt"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # Pinecone Configuration
    pinecone_api_key: str = "your_pinecone_key_here"
    pinecone_env: str = "your_pinecone_env_here"
    pinecone_index_name: str = "tutor-gpt"

    # Tavily MCP Configuration
    tavily_api_key: Optional[str] = None

    # Application Configuration
    secret_key: str = "tutor-gpt-secret-key-2024"
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

