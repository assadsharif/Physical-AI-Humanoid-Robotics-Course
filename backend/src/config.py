"""
Application configuration using Pydantic settings.

Supports multiple environments (dev, staging, prod) via environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = "Physical AI & Humanoid Robotics Textbook"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
    ]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/robotics_db"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600

    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 24 * 60  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Keys
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Qdrant Vector Store
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "robotics_embeddings"

    # Email (for password reset)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SENDER_EMAIL: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Validate required keys based on environment
if settings.ENVIRONMENT == "production":
    required_keys = [
        "SECRET_KEY",
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "QDRANT_API_KEY",
    ]
    missing_keys = [key for key in required_keys if not getattr(settings, key)]
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {missing_keys}")
