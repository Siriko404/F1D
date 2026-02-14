"""Base configuration classes using pydantic-settings.

This module provides type-safe configuration classes that validate all settings
at load time and support environment variable overrides.

Classes are designed to load from config/project.yaml following the
CONFIG_TESTING_STANDARD.md patterns.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataSettings(BaseSettings):
    """Configuration for data range settings.

    Attributes:
        year_start: Starting year for data processing (2000-2030).
        year_end: Ending year for data processing (2000-2030).

    Example:
        >>> settings = DataSettings(year_start=2002, year_end=2018)
        >>> settings.year_start
        2002
    """

    year_start: int = Field(ge=2000, le=2030, description="Starting year for data")
    year_end: int = Field(ge=2000, le=2030, description="Ending year for data")

    @model_validator(mode="after")
    def validate_year_range(self) -> "DataSettings":
        """Ensure year_end >= year_start."""
        if self.year_end < self.year_start:
            raise ValueError(
                f"year_end ({self.year_end}) must be >= year_start ({self.year_start})"
            )
        return self


class LoggingSettings(BaseSettings):
    """Configuration for logging settings.

    Attributes:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format: Log message format string.
        timestamp_format: Timestamp format for log messages.

    Example:
        >>> settings = LoggingSettings(level="INFO")
        >>> settings.level
        'INFO'
    """

    level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level",
    )
    format: str = Field(
        default="%(asctime)s [%(levelname)s] %(message)s",
        description="Log message format",
    )
    timestamp_format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Timestamp format for log messages",
    )

    @field_validator("level", mode="before")
    @classmethod
    def normalize_level(cls, v: str) -> str:
        """Normalize log level to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return v


class DeterminismSettings(BaseSettings):
    """Configuration for deterministic processing.

    Ensures reproducible results across runs by controlling random seeds,
    thread count, and input sorting.

    Attributes:
        random_seed: Random seed for reproducibility (>= 0).
        thread_count: Number of threads for parallel processing (1-32).
        sort_inputs: Whether to sort inputs before processing.

    Example:
        >>> settings = DeterminismSettings()
        >>> settings.random_seed
        42
    """

    random_seed: int = Field(default=42, ge=0, description="Random seed for reproducibility")
    thread_count: int = Field(
        default=1, ge=1, le=32, description="Number of threads for processing"
    )
    sort_inputs: bool = Field(default=True, description="Sort inputs before processing")


class ChunkProcessingSettings(BaseSettings):
    """Configuration for chunk-based memory-efficient processing.

    Controls how large datasets are processed in chunks to manage memory usage.

    Attributes:
        max_memory_percent: Maximum memory percentage before throttling (0-100).
        base_chunk_size: Base number of records per chunk (>= 1).
        enable_throttling: Whether to enable memory-based throttling.
        log_memory_status: Whether to log memory status during processing.

    Example:
        >>> settings = ChunkProcessingSettings()
        >>> settings.max_memory_percent
        80.0
    """

    max_memory_percent: float = Field(
        default=80.0, ge=0, le=100, description="Max memory percent before throttling"
    )
    base_chunk_size: int = Field(default=10000, ge=1, description="Base chunk size in records")
    enable_throttling: bool = Field(
        default=True, description="Enable memory-based throttling"
    )
    log_memory_status: bool = Field(
        default=True, description="Log memory status during processing"
    )


class ProjectSettings(BaseSettings):
    """Project metadata settings.

    Attributes:
        name: Project name.
        version: Project version string.
        description: Project description.

    Example:
        >>> settings = ProjectSettings(name="F1D_Clarity", version="1.0", description="Test")
        >>> settings.name
        'F1D_Clarity'
    """

    name: str = Field(default="F1D_Clarity", description="Project name")
    version: str = Field(description="Project version")
    description: str = Field(description="Project description")


class ProjectConfig(BaseSettings):
    """Root configuration for the F1D project.

    This is the main configuration class that aggregates all settings.
    It can be loaded from a YAML file and supports environment variable
    overrides with the F1D_ prefix.

    Attributes:
        project: Project metadata settings.
        data: Data range settings.
        logging: Logging configuration.
        determinism: Determinism settings.
        chunk_processing: Chunk processing settings.

    Environment Variables:
        F1D_DATA__YEAR_START: Override data.year_start
        F1D_LOGGING__LEVEL: Override logging.level
        etc.

    Example:
        >>> from pathlib import Path
        >>> config = ProjectConfig.from_yaml(Path("config/project.yaml"))
        >>> config.data.year_start
        2002
    """

    model_config = SettingsConfigDict(
        env_prefix="F1D_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    project: ProjectSettings
    data: DataSettings
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    determinism: DeterminismSettings = Field(default_factory=DeterminismSettings)
    chunk_processing: ChunkProcessingSettings = Field(
        default_factory=ChunkProcessingSettings
    )

    @classmethod
    def from_yaml(cls, path: Path) -> "ProjectConfig":
        """Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file.

        Returns:
            ProjectConfig instance populated from the YAML file.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            ValidationError: If the configuration is invalid.

        Example:
            >>> from pathlib import Path
            >>> config = ProjectConfig.from_yaml(Path("config/project.yaml"))
        """
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f)

        return cls.model_validate(data)

    def validate_paths(self, base: Path) -> Dict[str, Path]:
        """Validate and resolve paths relative to a base directory.

        This method is a stub for compatibility with paths.py PathsSettings.
        The actual path validation is handled by PathsSettings.

        Args:
            base: Base directory for resolving relative paths.

        Returns:
            Dictionary of validated paths (empty in this base implementation).

        Note:
            Use PathsSettings for actual path validation. This method exists
            for future integration with path settings.
        """
        return {}
