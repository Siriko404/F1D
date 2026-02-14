"""Hashing configuration for F1D pipeline.

This module provides type-safe configuration for file hashing operations.
Hashing is used for data integrity verification and deduplication.
"""

from __future__ import annotations

import hashlib
from typing import Set

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Valid hashlib algorithms available on this platform
VALID_ALGORITHMS: Set[str] = set(hashlib.algorithms_available)


class HashingConfig(BaseSettings):
    """Configuration for file hashing operations.

    Hashing is used for data integrity verification and detecting
    duplicate files based on content.

    Attributes:
        algorithm: Hash algorithm to use (e.g., 'sha256', 'md5').
        chunk_size: Size of chunks to read at a time in bytes.

    Example:
        >>> config = HashingConfig()
        >>> config.algorithm
        'sha256'
        >>> config.chunk_size
        65536
    """

    model_config = SettingsConfigDict(extra="ignore")

    algorithm: str = Field(
        default="sha256",
        description="Hash algorithm (must be valid hashlib algorithm)",
    )
    chunk_size: int = Field(
        default=65536,
        ge=1024,
        description="Chunk size in bytes for file hashing",
    )

    @field_validator("algorithm", mode="after")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate that the algorithm is available in hashlib.

        Args:
            v: Algorithm name to validate.

        Returns:
            Validated algorithm name (lowercase).

        Raises:
            ValueError: If algorithm is not available.
        """
        algorithm = v.lower()
        if algorithm not in VALID_ALGORITHMS:
            available = ", ".join(sorted(VALID_ALGORITHMS))
            raise ValueError(
                f"Invalid hash algorithm '{v}'. Available algorithms: {available}"
            )
        return algorithm
