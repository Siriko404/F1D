"""Environment variable configuration for F1D pipeline.

Configuration follows CONFIG_TESTING_STANDARD.md CONF-02 patterns.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    """Environment variable configuration.

    Loads configuration from environment variables and .env file.
    Environment variables are prefixed with F1D_.

    Attributes:
        api_timeout_seconds: API request timeout in seconds.
        max_retries: Maximum number of API retry attempts.
    """

    model_config = SettingsConfigDict(
        env_prefix="F1D_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of API retry attempts",
    )


# Module-level singleton for easy access
env = EnvConfig()
