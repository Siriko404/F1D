"""Unit tests for configuration validation.

This module tests all configuration classes including:
- DataSettings validation (year ranges)
- LoggingSettings validation (log levels)
- DeterminismSettings validation (random seed, thread count)
- PathSettings resolution
- ProjectConfig loading
- Environment variable overrides
- Configuration caching

Uses pytest fixtures from conftest.py for temporary YAML files.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest
from pydantic import ValidationError

from f1d.shared.config.base import (
    ChunkProcessingSettings,
    DataSettings,
    DeterminismSettings,
    LoggingSettings,
    ProjectConfig,
    ProjectSettings,
)
from f1d.shared.config.loader import (
    ConfigError,
    clear_config_cache,
    get_config,
    get_config_sources,
    reload_config,
    validate_env_override,
)


# ==============================================================================
# Test DataSettings validation
# ==============================================================================


class TestDataSettingsValidation:
    """Tests for DataSettings field validation."""

    def test_year_start_valid_range(self) -> None:
        """Test year_start accepts valid range (2000-2030)."""
        for year in [2000, 2002, 2015, 2030]:
            settings = DataSettings(year_start=year, year_end=2030)
            assert settings.year_start == year

    def test_year_start_invalid_below_2000_raises(self) -> None:
        """Test year_start below 2000 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DataSettings(year_start=1999, year_end=2018)
        assert "greater than or equal to 2000" in str(exc_info.value)

    def test_year_start_invalid_above_2030_raises(self) -> None:
        """Test year_start above 2030 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DataSettings(year_start=2031, year_end=2035)
        assert "less than or equal to 2030" in str(exc_info.value)

    def test_year_end_before_year_start_raises(self) -> None:
        """Test year_end < year_start raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DataSettings(year_start=2018, year_end=2002)
        assert "must be >=" in str(exc_info.value)

    def test_year_range_valid(self) -> None:
        """Test valid year range is accepted."""
        settings = DataSettings(year_start=2002, year_end=2018)
        assert settings.year_start == 2002
        assert settings.year_end == 2018

    def test_year_range_same_year_valid(self) -> None:
        """Test same year for start and end is valid."""
        settings = DataSettings(year_start=2010, year_end=2010)
        assert settings.year_start == 2010
        assert settings.year_end == 2010


# ==============================================================================
# Test LoggingSettings validation
# ==============================================================================


class TestLoggingSettingsValidation:
    """Tests for LoggingSettings field validation."""

    def test_valid_log_levels(self) -> None:
        """Test all valid log levels are accepted."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            settings = LoggingSettings(level=level)
            assert settings.level == level

    def test_log_level_case_insensitive(self) -> None:
        """Test log level is normalized to uppercase."""
        settings = LoggingSettings(level="debug")
        assert settings.level == "DEBUG"

        settings = LoggingSettings(level="Warning")
        assert settings.level == "WARNING"

    def test_invalid_log_level_raises(self) -> None:
        """Test invalid log level raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingSettings(level="INVALID")
        assert "String should match pattern" in str(exc_info.value)

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        settings = LoggingSettings()
        assert settings.level == "INFO"
        assert "%(asctime)s" in settings.format
        assert settings.timestamp_format == "%Y-%m-%d %H:%M:%S"


# ==============================================================================
# Test DeterminismSettings validation
# ==============================================================================


class TestDeterminismSettingsValidation:
    """Tests for DeterminismSettings field validation."""

    def test_random_seed_non_negative(self) -> None:
        """Test random_seed accepts non-negative values."""
        settings = DeterminismSettings(random_seed=0)
        assert settings.random_seed == 0

        settings = DeterminismSettings(random_seed=42)
        assert settings.random_seed == 42

    def test_random_seed_negative_raises(self) -> None:
        """Test negative random_seed raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DeterminismSettings(random_seed=-1)
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_thread_count_range(self) -> None:
        """Test thread_count accepts valid range (1-32)."""
        for count in [1, 4, 16, 32]:
            settings = DeterminismSettings(thread_count=count)
            assert settings.thread_count == count

    def test_invalid_thread_count_zero_raises(self) -> None:
        """Test thread_count=0 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DeterminismSettings(thread_count=0)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_invalid_thread_count_above_32_raises(self) -> None:
        """Test thread_count > 32 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DeterminismSettings(thread_count=33)
        assert "less than or equal to 32" in str(exc_info.value)


# ==============================================================================
# Test ChunkProcessingSettings validation
# ==============================================================================


class TestChunkProcessingSettingsValidation:
    """Tests for ChunkProcessingSettings field validation."""

    def test_max_memory_percent_range(self) -> None:
        """Test max_memory_percent accepts valid range (0-100)."""
        for percent in [0, 50.0, 80.0, 100]:
            settings = ChunkProcessingSettings(max_memory_percent=percent)
            assert settings.max_memory_percent == percent

    def test_max_memory_percent_invalid_raises(self) -> None:
        """Test max_memory_percent outside 0-100 raises ValidationError."""
        with pytest.raises(ValidationError):
            ChunkProcessingSettings(max_memory_percent=-1)

        with pytest.raises(ValidationError):
            ChunkProcessingSettings(max_memory_percent=101)

    def test_base_chunk_size_minimum(self) -> None:
        """Test base_chunk_size accepts >= 1."""
        settings = ChunkProcessingSettings(base_chunk_size=1)
        assert settings.base_chunk_size == 1

        settings = ChunkProcessingSettings(base_chunk_size=10000)
        assert settings.base_chunk_size == 10000

    def test_base_chunk_size_zero_raises(self) -> None:
        """Test base_chunk_size=0 raises ValidationError."""
        with pytest.raises(ValidationError):
            ChunkProcessingSettings(base_chunk_size=0)


# ==============================================================================
# Test ProjectConfig loading
# ==============================================================================


class TestProjectConfigLoading:
    """Tests for ProjectConfig YAML loading."""

    def test_from_yaml_loads_valid_config(self, sample_config_yaml: Path) -> None:
        """Test from_yaml loads a valid configuration."""
        config = ProjectConfig.from_yaml(sample_config_yaml)
        assert config.project.name == "TestProject"
        assert config.data.year_start == 2002
        assert config.data.year_end == 2018

    def test_from_yaml_file_not_found_raises(self, tmp_path: Path) -> None:
        """Test from_yaml raises FileNotFoundError for missing file."""
        missing_path = tmp_path / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError) as exc_info:
            ProjectConfig.from_yaml(missing_path)
        assert "Configuration file not found" in str(exc_info.value)

    def test_from_yaml_invalid_yaml_raises(self, tmp_path: Path) -> None:
        """Test from_yaml raises ValidationError for invalid YAML content."""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("data:\n  year_start: invalid_type")
        with pytest.raises(ValidationError):
            ProjectConfig.from_yaml(invalid_yaml)


# ==============================================================================
# Test environment variable overrides
# ==============================================================================


class TestEnvironmentVariableOverrides:
    """Tests for environment variable override functionality."""

    @pytest.fixture(autouse=True)
    def clear_cache_and_env(self) -> Generator[None, None, None]:
        """Clear config cache and clean env vars before/after each test."""
        clear_config_cache()
        # Clean up any F1D_ env vars that might interfere
        env_vars_to_clean = [k for k in os.environ if k.startswith("F1D_")]
        original_values = {k: os.environ.pop(k) for k in env_vars_to_clean}
        yield
        # Restore original values
        for k, v in original_values.items():
            os.environ[k] = v
        clear_config_cache()

    def test_env_override_year_start(self, sample_config_yaml: Path) -> None:
        """Test F1D_DATA__YEAR_START overrides YAML value."""
        os.environ["F1D_DATA__YEAR_START"] = "2010"
        config = get_config(sample_config_yaml, reload=True)
        assert config.data.year_start == 2010

    def test_env_override_log_level(self, sample_config_yaml: Path) -> None:
        """Test F1D_LOGGING__LEVEL overrides YAML value."""
        os.environ["F1D_LOGGING__LEVEL"] = "DEBUG"
        config = get_config(sample_config_yaml, reload=True)
        assert config.logging.level == "DEBUG"

    def test_env_prefix_required(self, sample_config_yaml: Path) -> None:
        """Test that F1D_ prefix is required for env vars."""
        # Set without prefix - should be ignored
        os.environ["DATA__YEAR_START"] = "2015"
        config = get_config(sample_config_yaml, reload=True)
        # Should use YAML value, not env var (2002 from fixture)
        assert config.data.year_start == 2002

    def test_env_nested_delimiter(self, sample_config_yaml: Path) -> None:
        """Test that __ delimiter is used for nested config access."""
        os.environ["F1D_DETERMINISM__THREAD_COUNT"] = "8"
        config = get_config(sample_config_yaml, reload=True)
        assert config.determinism.thread_count == 8


# ==============================================================================
# Test configuration caching
# ==============================================================================


class TestConfigurationCaching:
    """Tests for configuration caching functionality."""

    @pytest.fixture(autouse=True)
    def clear_cache(self) -> Generator[None, None, None]:
        """Clear config cache before/after each test."""
        clear_config_cache()
        yield
        clear_config_cache()

    def test_get_config_caches_result(self, sample_config_yaml: Path) -> None:
        """Test get_config returns cached result on subsequent calls."""
        config1 = get_config(sample_config_yaml)
        config2 = get_config(sample_config_yaml)
        # Same object in memory (cached)
        assert config1 is config2

    def test_reload_config_forces_reload(self, sample_config_yaml: Path) -> None:
        """Test reload=True forces fresh load from file."""
        config1 = get_config(sample_config_yaml)
        config2 = get_config(sample_config_yaml, reload=True)
        # Different objects (reloaded)
        assert config1 is not config2
        # But same values
        assert config1.data.year_start == config2.data.year_start

    def test_clear_cache_forces_reload(self, sample_config_yaml: Path) -> None:
        """Test clear_config_cache forces fresh load on next call."""
        config1 = get_config(sample_config_yaml)
        clear_config_cache()
        config2 = get_config(sample_config_yaml)
        # Different objects (cache cleared)
        assert config1 is not config2


# ==============================================================================
# Test helper functions
# ==============================================================================


class TestHelperFunctions:
    """Tests for loader helper functions."""

    @pytest.fixture(autouse=True)
    def clean_env(self) -> Generator[None, None, None]:
        """Clean env vars before/after each test."""
        env_vars_to_clean = [k for k in os.environ if k.startswith("F1D_")]
        original_values = {k: os.environ.pop(k) for k in env_vars_to_clean}
        yield
        for k in [k for k in os.environ if k.startswith("F1D_")]:
            del os.environ[k]
        for k, v in original_values.items():
            os.environ[k] = v

    def test_validate_env_override_set(self) -> None:
        """Test validate_env_override returns True for set env var."""
        os.environ["F1D_DATA__YEAR_START"] = "2010"
        assert validate_env_override("F1D_DATA__YEAR_START") is True

    def test_validate_env_override_not_set(self) -> None:
        """Test validate_env_override returns False for unset env var."""
        assert validate_env_override("F1D_DATA__YEAR_START") is False

    def test_validate_env_override_no_prefix(self) -> None:
        """Test validate_env_override returns False without F1D_ prefix."""
        os.environ["DATA__YEAR_START"] = "2010"
        assert validate_env_override("DATA__YEAR_START") is False

    def test_get_config_sources_env(self) -> None:
        """Test get_config_sources identifies env var sources."""
        os.environ["F1D_DATA__YEAR_START"] = "2010"
        sources = get_config_sources()
        assert sources["data.year_start"] == "env"

    def test_get_config_sources_yaml(self) -> None:
        """Test get_config_sources identifies yaml sources."""
        # No env var set
        sources = get_config_sources()
        assert sources["data.year_start"] == "yaml"
        assert sources["data.year_end"] == "yaml"


# ==============================================================================
# Test ConfigError
# ==============================================================================


class TestConfigError:
    """Tests for ConfigError exception."""

    def test_config_error_message(self, tmp_path: Path) -> None:
        """Test ConfigError includes path and message."""
        error = ConfigError(tmp_path / "config.yaml", "Invalid configuration")
        assert "config.yaml" in str(error)
        assert "Invalid configuration" in str(error)

    def test_config_error_none_path(self) -> None:
        """Test ConfigError handles None path."""
        error = ConfigError(None, "Generic error")
        assert "Generic error" in str(error)
