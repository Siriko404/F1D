"""Configuration module for F1D project.

This module provides type-safe configuration management using pydantic-settings.
Configuration can be loaded from YAML files with environment variable overrides.

Example:
    from f1d.shared.config import ProjectConfig
    from pathlib import Path

    config = ProjectConfig.from_yaml(Path("config/project.yaml"))
    print(f"Data range: {config.data.year_start}-{config.data.year_end}")
"""

from f1d.shared.config.base import (
    ChunkProcessingSettings,
    DataSettings,
    DeterminismSettings,
    LoggingSettings,
    ProjectConfig,
    ProjectSettings,
)
from f1d.shared.config.paths import PathsSettings

__all__ = [
    "ProjectConfig",
    "ProjectSettings",
    "DataSettings",
    "LoggingSettings",
    "DeterminismSettings",
    "ChunkProcessingSettings",
    "PathsSettings",
]
