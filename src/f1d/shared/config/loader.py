"""Configuration loader with caching and error handling.

This module provides utilities for loading and caching configuration
with clear error messages and environment variable override support.

Example:
    from f1d.shared.config.loader import get_config

    # Load from default location (config/project.yaml)
    config = get_config()
    print(config.data.year_start)

    # Environment variable override
    # F1D_DATA__YEAR_START=2005
    # config.data.year_start == 2005
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, Optional

from f1d.shared.config.base import ProjectConfig


class ConfigError(Exception):
    """Custom exception for configuration-related errors.

    Attributes:
        path: Path to the configuration file that caused the error.
        message: Human-readable error description.

    Example:
        >>> raise ConfigError("config/project.yaml", "Invalid year range")
    """

    def __init__(self, path: Optional[Path], message: str) -> None:
        """Initialize ConfigError.

        Args:
            path: Path to the configuration file (or None if not applicable).
            message: Error description.
        """
        self.path = path
        self.message = message
        super().__init__(f"Configuration error ({path}): {message}")


class _ConfigCache:
    """Internal cache for configuration instances.

    This class is not meant to be used directly. Use get_config() instead.
    """

    def __init__(self) -> None:
        """Initialize empty cache."""
        self._config: Optional[ProjectConfig] = None
        self._config_path: Optional[Path] = None
        self._loaded_at: Optional[float] = None

    def clear(self) -> None:
        """Clear the cached configuration."""
        self._config = None
        self._config_path = None
        self._loaded_at = None

    def is_valid(self, path: Optional[Path]) -> bool:
        """Check if cached config is valid for the given path.

        Args:
            path: Path to check against cached config path.

        Returns:
            True if cache is valid for this path.
        """
        return (
            self._config is not None
            and self._config_path is not None
            and self._config_path == path
        )

    def get(self) -> Optional[ProjectConfig]:
        """Get cached configuration.

        Returns:
            Cached ProjectConfig or None if not cached.
        """
        return self._config

    def set(self, config: ProjectConfig, path: Path) -> None:
        """Cache a configuration instance.

        Args:
            config: ProjectConfig to cache.
            path: Path from which config was loaded.
        """
        self._config = config
        self._config_path = path
        self._loaded_at = time.time()


# Module-level cache singleton
_cache = _ConfigCache()


def get_config(path: Optional[Path] = None, reload: bool = False) -> ProjectConfig:
    """Load and cache configuration from YAML file.

    Returns cached configuration if available and path matches.
    Loads from path if not cached or reload=True.

    Args:
        path: Path to configuration file. Defaults to config/project.yaml.
        reload: Force reload from file even if cached.

    Returns:
        ProjectConfig instance with loaded settings.

    Raises:
        ConfigError: If configuration validation fails with clear error message.
        FileNotFoundError: If the YAML file does not exist.

    Example:
        >>> from f1d.shared.config.loader import get_config
        >>> config = get_config()  # Loads from config/project.yaml
        >>> config.data.year_start
        2002

        # With environment override:
        # F1D_DATA__YEAR_START=2010
        >>> config = get_config(reload=True)
        >>> config.data.year_start
        2010
    """
    if path is None:
        path = Path("config/project.yaml")

    # Check cache
    if not reload and _cache.is_valid(path):
        cached = _cache.get()
        if cached is not None:
            return cached

    # Load from file
    try:
        config = ProjectConfig.from_yaml(path)
        _cache.set(config, path)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Configuration file not found: {path}\n"
            f"Please ensure the file exists at this location."
        )
    except Exception as e:
        # Wrap validation errors with helpful context
        raise ConfigError(
            path,
            f"Configuration validation failed: {e}"
        ) from e


def reload_config() -> ProjectConfig:
    """Force reload of configuration from the same path.

    Clears cache and reloads configuration from the previously used path.
    Useful for detecting configuration changes during runtime.

    Returns:
        ProjectConfig instance with fresh settings.

    Raises:
        ConfigError: If configuration validation fails.
        ValueError: If no configuration has been loaded yet.

    Example:
        >>> from f1d.shared.config.loader import get_config, reload_config
        >>> config = get_config()  # Initial load
        >>> # ... config file changes ...
        >>> fresh_config = reload_config()  # Reload from same path
    """
    cached_path = _cache._config_path
    if cached_path is None:
        raise ValueError(
            "No configuration has been loaded yet. "
            "Use get_config() first."
        )
    return get_config(cached_path, reload=True)


def clear_config_cache() -> None:
    """Clear the cached configuration.

    Useful for testing or when you want to ensure fresh config load.
    After calling this, the next get_config() will load from file.

    Example:
        >>> from f1d.shared.config.loader import get_config, clear_config_cache
        >>> config1 = get_config()
        >>> clear_config_cache()
        >>> config2 = get_config()  # Fresh load from file
    """
    _cache.clear()


def validate_env_override(env_var: str, config_path: Optional[str] = None) -> bool:
    """Check if an environment variable would override a config value.

    Useful for debugging configuration issues and understanding
    which values come from environment vs YAML.

    Args:
        env_var: Environment variable name (e.g., "F1D_DATA__YEAR_START").
        config_path: Dot-notation path in config (e.g., "data.year_start").
                     If None, only checks if env var is set and has F1D_ prefix.

    Returns:
        True if the environment variable is set and would override.

    Example:
        >>> import os
        >>> os.environ["F1D_DATA__YEAR_START"] = "2010"
        >>> validate_env_override("F1D_DATA__YEAR_START")
        True
        >>> validate_env_override("F1D_DATA__YEAR_START", "data.year_start")
        True
        >>> validate_env_override("F1D_UNKNOWN_VAR")
        False
        >>> validate_env_override("DATA__YEAR_START")  # No F1D_ prefix
        False
    """
    # Always require F1D_ prefix
    if not env_var.startswith("F1D_"):
        return False

    # Check if env var is set
    if env_var not in os.environ:
        return False

    return True


def get_config_sources() -> Dict[str, str]:
    """Get mapping of configuration keys to their sources.

    Returns a dictionary showing which configuration values come from
    environment variables ("env") vs YAML file ("yaml").

    Returns:
        Dict mapping config keys to "env" or "yaml".

    Example:
        >>> import os
        >>> os.environ["F1D_DATA__YEAR_START"] = "2010"
        >>> from f1d.shared.config.loader import get_config_sources
        >>> sources = get_config_sources()
        >>> sources["data.year_start"]
        'env'
        >>> sources["data.year_end"]
        'yaml'
    """
    sources: Dict[str, str] = {}

    # Check known environment variable patterns
    env_patterns = [
        ("F1D_DATA__YEAR_START", "data.year_start"),
        ("F1D_DATA__YEAR_END", "data.year_end"),
        ("F1D_LOGGING__LEVEL", "logging.level"),
        ("F1D_LOGGING__FORMAT", "logging.format"),
        ("F1D_DETERMINISM__RANDOM_SEED", "determinism.random_seed"),
        ("F1D_DETERMINISM__THREAD_COUNT", "determinism.thread_count"),
    ]

    for env_var, config_key in env_patterns:
        if env_var in os.environ:
            sources[config_key] = "env"
        else:
            sources[config_key] = "yaml"

    return sources
