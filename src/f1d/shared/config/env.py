"""Environment variable and secrets configuration for F1D pipeline.

This module provides secure handling of environment variables and secrets
using pydantic-settings SecretStr for sensitive data like passwords.

Configuration follows CONFIG_TESTING_STANDARD.md CONF-02 patterns.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    """Environment variable configuration with secrets management.

    Loads configuration from environment variables and .env file.
    Sensitive values like passwords use SecretStr for protection.

    Environment variables are prefixed with F1D_ and use __ as nested delimiter.
    Values from .env file override defaults but not explicit environment variables.

    Attributes:
        wrds_username: WRDS username for data downloads.
        wrds_password: WRDS password (stored securely as SecretStr).
        api_timeout_seconds: API request timeout in seconds.
        max_retries: Maximum number of API retry attempts.

    Example:
        >>> env = EnvConfig()
        >>> env.api_timeout_seconds
        30
        >>> env.get_wrds_password() is None  # No password set
        True

    Security:
        - Passwords are stored as SecretStr and never logged in plain text
        - Use get_wrds_password() to access the password value only when needed
        - .env file should be in .gitignore and never committed
    """

    model_config = SettingsConfigDict(
        env_prefix="F1D_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    wrds_username: Optional[str] = Field(
        default=None,
        description="WRDS username for data downloads",
    )
    wrds_password: Optional[SecretStr] = Field(
        default=None,
        description="WRDS password (stored securely)",
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

    def get_wrds_password(self) -> Optional[str]:
        """Get the WRDS password value.

        Returns the plain text password only when explicitly needed.
        Returns None if no password is configured.

        Returns:
            Plain text password or None if not set.

        Example:
            >>> env = EnvConfig()
            >>> env.get_wrds_password() is None
            True
        """
        if self.wrds_password is None:
            return None
        return self.wrds_password.get_secret_value()


# Module-level singleton for easy access
env = EnvConfig()
