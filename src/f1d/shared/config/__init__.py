"""Configuration module for F1D project.

This module provides type-safe configuration management using pydantic-settings.
Configuration can be loaded from YAML files with environment variable overrides.

Example:
    from f1d.shared.config import load_config, get_config
    from pathlib import Path

    # Simple loading with caching
    config = get_config()  # Loads from config/project.yaml
    print(config.data.year_start)

    # Environment variable override
    # F1D_DATA__YEAR_START=2005
    # config.data.year_start == 2005
"""

from pathlib import Path
from typing import Optional

from f1d.shared.config.base import (
    ChunkProcessingSettings,
    DataSettings,
    DeterminismSettings,
    LoggingSettings,
    ProjectConfig,
    ProjectSettings,
)
from f1d.shared.config.datasets import DatasetConfig, DatasetsConfig
from f1d.shared.config.env import EnvConfig, env
from f1d.shared.config.hashing import HashingConfig
from f1d.shared.config.loader import (
    ConfigError,
    clear_config_cache,
    clear_variable_config_cache,
    get_config,
    get_config_sources,
    load_variable_config,
    reload_config,
    validate_env_override,
)
from f1d.shared.config.paths import PathsSettings
from f1d.shared.config.step_configs import (
    BaseStepConfig,
    Step00Config,
    Step00bConfig,
    Step00cConfig,
    Step01Config,
    Step02Config,
    Step02_5Config,
    Step02_5bConfig,
    Step02_5cConfig,
    Step03Config,
    Step04Config,
    Step07Config,
    Step08Config,
    Step09Config,
    StepsConfig,
)
from f1d.shared.config.string_matching import (
    CompanyNameMatchingConfig,
    EntityNameMatchingConfig,
    StringMatchingConfig,
)

__all__ = [
    # Main config loaders
    "ProjectConfig",
    "load_config",
    "get_config",
    "reload_config",
    "clear_config_cache",
    "ConfigError",
    # Variable config
    "load_variable_config",
    "clear_variable_config_cache",
    # Config source helpers
    "validate_env_override",
    "get_config_sources",
    # Project settings
    "ProjectSettings",
    "DataSettings",
    "LoggingSettings",
    "DeterminismSettings",
    "ChunkProcessingSettings",
    "PathsSettings",
    # Step configs
    "StepsConfig",
    "BaseStepConfig",
    "Step00Config",
    "Step00bConfig",
    "Step00cConfig",
    "Step01Config",
    "Step02Config",
    "Step02_5Config",
    "Step02_5bConfig",
    "Step02_5cConfig",
    "Step03Config",
    "Step04Config",
    "Step07Config",
    "Step08Config",
    "Step09Config",
    # Dataset configs
    "DatasetsConfig",
    "DatasetConfig",
    # Hashing and string matching
    "HashingConfig",
    "StringMatchingConfig",
    "CompanyNameMatchingConfig",
    "EntityNameMatchingConfig",
    # Environment
    "EnvConfig",
    "env",
]


def load_config(path: Optional[Path] = None) -> ProjectConfig:
    """Load configuration from project.yaml with env var overrides.

    Convenience function that loads the F1D project configuration from
    the default location or a specified path. This is an alias for
    get_config() for backward compatibility.

    Args:
        path: Path to configuration file. Defaults to config/project.yaml.

    Returns:
        ProjectConfig instance populated from the YAML file.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        ValidationError: If the configuration is invalid.

    Example:
        >>> from f1d.shared.config import load_config
        >>> config = load_config()
        >>> config.project.name
        'F1D_Clarity'
    """
    return get_config(path)
