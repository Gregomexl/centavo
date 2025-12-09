"""Configuration management using pydantic-settings."""

from functools import lru_cache
from typing import Literal

import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    """Application settings."""

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Centavo"
    app_env: Literal["development", "production", "test"] = "development"
    debug: bool = True
    secret_key: str = pydantic.Field(..., min_length=32)

    # Database
    database_url: pydantic.PostgresDsn = pydantic.Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/centavo"
    )
    alembic_database_url: str = pydantic.Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/centavo"
    )
    database_echo: bool = False

    # Redis
    redis_url: pydantic.RedisDsn = pydantic.Field(default="redis://localhost:6379/0")

    # JWT
    jwt_secret_key: str = pydantic.Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Telegram
    telegram_bot_token: str | None = None
    telegram_webhook_secret: str | None = None
    telegram_webhook_url: str | None = None

    # CORS
    cors_origins: list[str] = pydantic.Field(default=["http://localhost:3000"])


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
