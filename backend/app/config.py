"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "LLM Interactions API"
    app_version: str = "0.1.0"
    debug_mode: bool = False
    log_level: str = "INFO"

    # Server
    web_host: str = "0.0.0.0"
    web_port: int = 8017

    # Database
    database_url: str = (
        "postgresql+asyncpg://llm_interactions:password@localhost:5432/"
        "llm_interactions_db"
    )

    # CORS
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
