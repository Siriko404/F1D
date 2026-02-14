"""Factory fixtures for generating configuration test data.

This module provides pytest fixtures that generate configuration data
for testing the F1D configuration system. Each factory is function-scoped
to ensure fresh data per test.

Available Factories:
    - sample_config_yaml_factory: Generate temporary YAML config files
    - sample_project_config_factory: Generate ProjectConfig instances
    - sample_env_vars_factory: Generate F1D_* environment variable dicts
    - invalid_config_yaml_factory: Generate intentionally invalid configs
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict

import pytest
import yaml


@pytest.fixture
def sample_config_yaml_factory(tmp_path: Path) -> Callable[..., Path]:
    """Factory fixture to generate temporary YAML config files.

    Returns a callable that creates a temporary project.yaml file
    with customizable configuration values.

    Args (via factory call):
        year_start: Start year for data range (default 2002)
        year_end: End year for data range (default 2018)
        **kwargs: Additional fields to merge into config

    Returns:
        Path to the generated YAML config file

    Note:
        Uses tmp_path fixture for automatic cleanup.

    Example:
        def test_config_loading(sample_config_yaml_factory):
            config_path = sample_config_yaml_factory(year_start=2010)
            assert config_path.exists()
    """

    def _factory(
        year_start: int = 2002,
        year_end: int = 2018,
        **kwargs: Any,
    ) -> Path:
        config_data = {
            "project": {
                "name": "TestProject",
                "version": "1.0.0",
                "description": "Test configuration for unit tests",
            },
            "data": {
                "year_start": year_start,
                "year_end": year_end,
            },
            "logging": {
                "level": "INFO",
            },
            "determinism": {
                "random_seed": 42,
                "thread_count": 1,
                "sort_inputs": True,
            },
        }

        # Merge any additional kwargs
        for key, value in kwargs.items():
            if key in config_data and isinstance(config_data[key], dict) and isinstance(value, dict):
                config_data[key].update(value)
            else:
                config_data[key] = value

        config_path = tmp_path / "project.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        return config_path

    return _factory


@pytest.fixture
def sample_project_config_factory(sample_config_yaml_factory: Callable[..., Path]) -> Callable[..., Any]:
    """Factory fixture to generate ProjectConfig instances.

    Returns a callable that creates a ProjectConfig instance loaded
    from a generated YAML file.

    Args (via factory call):
        year_start: Start year for data range (default 2002)
        year_end: End year for data range (default 2018)
        **kwargs: Additional fields to merge into config

    Returns:
        ProjectConfig instance

    Example:
        def test_with_config(sample_project_config_factory):
            config = sample_project_config_factory(year_start=2010, year_end=2015)
            assert config.data.year_start == 2010
            assert config.data.year_end == 2015
    """

    def _factory(
        year_start: int = 2002,
        year_end: int = 2018,
        **kwargs: Any,
    ) -> Any:
        from f1d.shared.config.base import ProjectConfig

        config_path = sample_config_yaml_factory(
            year_start=year_start,
            year_end=year_end,
            **kwargs,
        )
        return ProjectConfig.from_yaml(config_path)

    return _factory


@pytest.fixture
def sample_env_vars_factory() -> Callable[..., Dict[str, str]]:
    """Factory fixture to generate F1D_* environment variable dicts.

    Returns a callable that generates a dictionary of F1D-prefixed
    environment variables suitable for os.environ.update().

    Args (via factory call):
        data__year_start: Override data.year_start (default None)
        data__year_end: Override data.year_end (default None)
        logging__level: Override logging.level (default None)
        **kwargs: Additional F1D_* env vars (without prefix)

    Returns:
        Dict[str, str] of environment variables with F1D_ prefix

    Example:
        def test_env_override(sample_env_vars_factory):
            env_vars = sample_env_vars_factory(data__year_start="2010")
            with patch.dict(os.environ, env_vars):
                config = EnvConfig()
                assert config.data.year_start == 2010
    """

    def _factory(
        data__year_start: str | None = None,
        data__year_end: str | None = None,
        logging__level: str | None = None,
        **kwargs: str | None,
    ) -> Dict[str, str]:
        env_vars: Dict[str, str] = {}

        # Map common parameters to F1D env vars
        if data__year_start is not None:
            env_vars["F1D_DATA__YEAR_START"] = data__year_start
        if data__year_end is not None:
            env_vars["F1D_DATA__YEAR_END"] = data__year_end
        if logging__level is not None:
            env_vars["F1D_LOGGING__LEVEL"] = logging__level

        # Add any additional kwargs as F1D_* env vars
        for key, value in kwargs.items():
            if value is not None:
                env_vars[f"F1D_{key.upper()}"] = value

        return env_vars

    return _factory


@pytest.fixture
def invalid_config_yaml_factory(tmp_path: Path) -> Callable[..., Path]:
    """Factory fixture to generate intentionally invalid config files.

    Returns a callable that creates YAML config files with specific
    validation errors, useful for testing error handling.

    Args (via factory call):
        error_type: Type of error to generate (default 'year_order')
            - 'year_order': year_start > year_end
            - 'missing_required': Missing required field
            - 'invalid_type': Wrong type for a field

    Returns:
        Path to the invalid YAML config file

    Example:
        def test_invalid_config_raises(invalid_config_yaml_factory):
            from pydantic import ValidationError
            from f1d.shared.config.base import ProjectConfig

            config_path = invalid_config_yaml_factory(error_type="year_order")
            with pytest.raises(ValidationError):
                ProjectConfig.from_yaml(config_path)
    """

    def _factory(error_type: str = "year_order") -> Path:
        if error_type == "year_order":
            config_data = {
                "project": {
                    "name": "InvalidYearOrder",
                    "version": "1.0.0",
                },
                "data": {
                    "year_start": 2018,
                    "year_end": 2002,  # Invalid: end before start
                },
                "logging": {
                    "level": "INFO",
                },
            }
        elif error_type == "missing_required":
            config_data = {
                "project": {
                    "name": "MissingRequired",
                    # Missing version
                },
                "data": {
                    "year_start": 2002,
                    "year_end": 2018,
                },
            }
        elif error_type == "invalid_type":
            config_data = {
                "project": {
                    "name": "InvalidType",
                    "version": "1.0.0",
                },
                "data": {
                    "year_start": "not_a_number",  # Invalid: should be int
                    "year_end": 2018,
                },
                "logging": {
                    "level": "INFO",
                },
            }
        else:
            raise ValueError(f"Unknown error_type: {error_type}")

        config_path = tmp_path / f"invalid_config_{error_type}.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        return config_path

    return _factory
