"""Environment variable configuration for F1D pipeline.

Purpose:
    Provides environment variable configuration following
    CONFIG_TESTING_STANDARD.md CONF-02 patterns. Loads configuration
    from environment variables and .env file with F1D_ prefix.

Key Classes:
    - EnvConfig: Environment variable configuration class

Usage:
    from f1d.shared.config.env import env, EnvConfig

    # Access singleton instance
    timeout = env.api_timeout_seconds

    # Or create new instance
    custom_env = EnvConfig()
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
