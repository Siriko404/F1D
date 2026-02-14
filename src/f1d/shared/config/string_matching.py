"""String matching configuration for F1D pipeline.

This module provides type-safe configuration for fuzzy string matching
operations used in company name and entity name matching.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Valid fuzzywuzzy scorer types
ScorerType = Literal[
    "ratio",
    "partial_ratio",
    "token_sort_ratio",
    "token_set_ratio",
    "partial_token_sort_ratio",
    "partial_token_set_ratio",
    "WRatio",
    "QRatio",
    "UQRatio",
    "UWRatio",
]


class CompanyNameMatchingConfig(BaseSettings):
    """Configuration for company name fuzzy matching.

    Company names typically require higher thresholds due to their
    formal nature and the importance of precise matching.

    Attributes:
        default_threshold: Default similarity threshold (0-100).
        min_threshold: Minimum acceptable threshold (0-100).
        scorer: Fuzzy matching scorer to use.
        preprocess: Whether to preprocess strings before matching.

    Example:
        >>> config = CompanyNameMatchingConfig()
        >>> config.default_threshold
        92.0
    """

    model_config = SettingsConfigDict(extra="ignore")

    default_threshold: float = Field(
        default=92.0,
        ge=0,
        le=100,
        description="Default similarity threshold for company names",
    )
    min_threshold: float = Field(
        default=85.0,
        ge=0,
        le=100,
        description="Minimum acceptable threshold for company names",
    )
    scorer: str = Field(
        default="token_sort_ratio",
        description="Fuzzy matching scorer to use",
    )
    preprocess: bool = Field(
        default=True,
        description="Whether to preprocess strings before matching",
    )

    @model_validator(mode="after")
    def validate_thresholds(self) -> "CompanyNameMatchingConfig":
        """Ensure min_threshold <= default_threshold."""
        if self.min_threshold > self.default_threshold:
            raise ValueError(
                f"min_threshold ({self.min_threshold}) must be <= "
                f"default_threshold ({self.default_threshold})"
            )
        return self


class EntityNameMatchingConfig(BaseSettings):
    """Configuration for entity name fuzzy matching.

    Entity names (e.g., person names) can have more variation due to
    abbreviations, typos, and formatting differences, so lower thresholds
    are typically used.

    Attributes:
        default_threshold: Default similarity threshold (0-100).
        min_threshold: Minimum acceptable threshold (0-100).
        scorer: Fuzzy matching scorer to use.
        preprocess: Whether to preprocess strings before matching.

    Example:
        >>> config = EntityNameMatchingConfig()
        >>> config.default_threshold
        85.0
    """

    model_config = SettingsConfigDict(extra="ignore")

    default_threshold: float = Field(
        default=85.0,
        ge=0,
        le=100,
        description="Default similarity threshold for entity names",
    )
    min_threshold: float = Field(
        default=70.0,
        ge=0,
        le=100,
        description="Minimum acceptable threshold for entity names",
    )
    scorer: str = Field(
        default="WRatio",
        description="Fuzzy matching scorer to use",
    )
    preprocess: bool = Field(
        default=True,
        description="Whether to preprocess strings before matching",
    )

    @model_validator(mode="after")
    def validate_thresholds(self) -> "EntityNameMatchingConfig":
        """Ensure min_threshold <= default_threshold."""
        if self.min_threshold > self.default_threshold:
            raise ValueError(
                f"min_threshold ({self.min_threshold}) must be <= "
                f"default_threshold ({self.default_threshold})"
            )
        return self


class StringMatchingConfig(BaseSettings):
    """Container for all string matching configurations.

    Provides unified configuration for fuzzy string matching operations
    including company and entity name matching.

    Attributes:
        company_name: Company name matching configuration.
        entity_name: Entity name matching configuration.
        batch_size: Number of comparisons per batch.
        enable_parallel: Whether to enable parallel processing.

    Example:
        >>> config = StringMatchingConfig()
        >>> config.company_name.default_threshold
        92.0
        >>> config.batch_size
        1000
    """

    model_config = SettingsConfigDict(extra="ignore")

    company_name: CompanyNameMatchingConfig = Field(
        default_factory=CompanyNameMatchingConfig,
        description="Company name matching settings",
    )
    entity_name: EntityNameMatchingConfig = Field(
        default_factory=EntityNameMatchingConfig,
        description="Entity name matching settings",
    )
    batch_size: int = Field(
        default=1000,
        ge=1,
        description="Number of comparisons per batch",
    )
    enable_parallel: bool = Field(
        default=False,
        description="Whether to enable parallel processing",
    )
