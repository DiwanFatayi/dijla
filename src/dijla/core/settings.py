"""Strict, env-driven settings for the platform.

Settings are read once at process startup. Tests override them via
``Settings.model_construct`` or by setting environment variables before import.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvName = Literal["development", "testing", "production"]


class Settings(BaseSettings):
    """Top-level platform configuration."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    env: EnvName = "development"
    log_level: str = "INFO"
    api_key: str = "dev-api-key"
    api_title: str = "Dijla — Scientific Spiral Platform"
    api_version: str = "0.1.0"

    # External services (read with their own prefixes for clarity)
    database_url: str = Field(
        default="sqlite+aiosqlite:///./dijla.db",
        validation_alias=AliasChoices("database_url", "DATABASE_URL"),
    )
    memgraph_host: str = Field(
        default="localhost", validation_alias=AliasChoices("memgraph_host", "MEMGRAPH_HOST")
    )
    memgraph_port: int = Field(
        default=7687, validation_alias=AliasChoices("memgraph_port", "MEMGRAPH_PORT")
    )
    memgraph_username: str = Field(
        default="", validation_alias=AliasChoices("memgraph_username", "MEMGRAPH_USERNAME")
    )
    memgraph_password: str = Field(
        default="", validation_alias=AliasChoices("memgraph_password", "MEMGRAPH_PASSWORD")
    )

    minio_endpoint: str = Field(
        default="localhost:9000",
        validation_alias=AliasChoices("minio_endpoint", "MINIO_ENDPOINT"),
    )
    minio_access_key: str = Field(
        default="dijla", validation_alias=AliasChoices("minio_access_key", "MINIO_ACCESS_KEY")
    )
    minio_secret_key: str = Field(
        default="dijla-secret",
        validation_alias=AliasChoices("minio_secret_key", "MINIO_SECRET_KEY"),
    )
    minio_secure: bool = Field(
        default=False, validation_alias=AliasChoices("minio_secure", "MINIO_SECURE")
    )
    minio_bucket_proofs: str = Field(
        default="proofs",
        validation_alias=AliasChoices("minio_bucket_proofs", "MINIO_BUCKET_PROOFS"),
    )
    minio_bucket_certificates: str = Field(
        default="certificates",
        validation_alias=AliasChoices("minio_bucket_certificates", "MINIO_BUCKET_CERTIFICATES"),
    )
    minio_bucket_attacks: str = Field(
        default="attacks",
        validation_alias=AliasChoices("minio_bucket_attacks", "MINIO_BUCKET_ATTACKS"),
    )
    minio_bucket_models: str = Field(
        default="models",
        validation_alias=AliasChoices("minio_bucket_models", "MINIO_BUCKET_MODELS"),
    )

    langgraph_checkpoint_backend: Literal["memory", "sqlite", "postgres"] = Field(
        default="memory",
        validation_alias=AliasChoices(
            "langgraph_checkpoint_backend", "LANGGRAPH_CHECKPOINT_BACKEND"
        ),
    )

    anthropic_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("anthropic_api_key", "ANTHROPIC_API_KEY"),
    )

    @property
    def use_mock_models(self) -> bool:
        """Mocks are used unless a real API key is provided."""
        return not self.anthropic_api_key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


def reset_settings_cache() -> None:
    """Reset the cached settings — useful for tests that mutate env vars."""
    get_settings.cache_clear()
