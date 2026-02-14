"""Integration tests for configuration loading.

These tests validate the configuration system works with the actual
project.yaml file and real project structure.

Run with: python -m pytest tests/integration/test_config_integration.py -v -m integration
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest
from pydantic import ValidationError

from f1d.shared.config import (
    ProjectConfig,
    load_config,
    clear_config_cache,
    get_config,
    reload_config,
)
from f1d.shared.config.loader import (
    ConfigError,
    get_config_sources,
    validate_env_override,
)


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def clean_environment() -> Generator[None, None, None]:
    """Clear config cache and clean env vars before and after each test."""
    # Clear cache
    clear_config_cache()

    # Save and clear any F1D_ environment variables
    env_vars_to_clean = [k for k in os.environ if k.startswith("F1D_")]
    original_values = {k: os.environ.pop(k) for k in env_vars_to_clean}

    yield

    # Restore original environment
    for k in [k for k in os.environ if k.startswith("F1D_")]:
        del os.environ[k]
    for k, v in original_values.items():
        os.environ[k] = v

    # Clear cache again
    clear_config_cache()


class TestActualProjectConfig:
    """Tests that load the actual config/project.yaml file."""

    def test_load_actual_project_config(self) -> None:
        """Load config/project.yaml and verify all expected sections."""
        config_path = Path("config/project.yaml")

        # Skip if project.yaml doesn't exist (e.g., in CI without full repo)
        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")

        config = get_config(config_path)

        # Verify project metadata
        assert config.project.name == "F1D_Clarity"
        assert config.project.version

        # Verify data settings
        assert config.data.year_start == 2002
        assert config.data.year_end == 2018

        # Verify logging settings
        assert config.logging.level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        # Verify determinism settings
        assert config.determinism.random_seed >= 0
        assert 1 <= config.determinism.thread_count <= 32

    def test_config_path_resolution(self) -> None:
        """Load config and verify path resolution works correctly."""
        config_path = Path("config/project.yaml")

        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")

        config = get_config(config_path)

        # Verify paths section exists
        assert config.paths is not None

        # Verify input paths can be resolved
        resolved = config.paths.resolve(Path("."))

        # Check that input paths are present
        assert "inputs" in resolved
        assert isinstance(resolved["inputs"], Path)

    def test_step_configs_load(self) -> None:
        """Verify step_00 through step_09 configs load correctly."""
        config_path = Path("config/project.yaml")

        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")

        config = get_config(config_path)

        # Verify steps section exists
        assert config.steps is not None

        # Check required step configs exist and have required fields
        expected_steps = [
            "step_00",
            "step_00b",
            "step_00c",
            "step_01",
            "step_02",
            "step_02_5",
            "step_02_5b",
            "step_02_5c",
            "step_03",
            "step_04",
            "step_07",
            "step_08",
            "step_09",
        ]

        for step_name in expected_steps:
            step_config = getattr(config.steps, step_name, None)
            # Some steps may be disabled or not present, that's OK
            # Just verify we can access them without error
            if step_config is not None:
                assert hasattr(step_config, "enabled")
                assert hasattr(step_config, "output_subdir")

    def test_datasets_config_load(self) -> None:
        """Verify datasets configuration loads correctly."""
        config_path = Path("config/project.yaml")

        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")

        config = get_config(config_path)

        # Verify datasets section exists
        assert config.datasets is not None

        # Check that we can get enabled datasets
        enabled_datasets = config.datasets.get_enabled_datasets()
        assert isinstance(enabled_datasets, list)

        # Verify at least some datasets are configured
        assert len(enabled_datasets) > 0

    def test_hashing_config_load(self) -> None:
        """Verify hashing configuration loads correctly."""
        config_path = Path("config/project.yaml")

        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")

        config = get_config(config_path)

        # Verify hashing section exists
        assert config.hashing is not None
        assert config.hashing.algorithm == "sha256"
        assert config.hashing.chunk_size > 0

    def test_string_matching_config_load(self) -> None:
        """Verify string matching configuration loads correctly."""
        config_path = Path("config/project.yaml")

        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")

        config = get_config(config_path)

        # Verify string_matching section exists
        assert config.string_matching is not None
        assert config.string_matching.company_name is not None
        assert config.string_matching.entity_name is not None

        # Verify threshold values are in valid range
        assert 0 <= config.string_matching.company_name.default_threshold <= 100


class TestConfigLoader:
    """Tests for config loader functions with caching."""

    def test_get_config_caches_result(self, sample_config_yaml_factory) -> None:
        """Test that get_config caches configuration."""
        config_path = sample_config_yaml_factory()

        # First load
        config1 = get_config(config_path)

        # Second load should return cached instance
        config2 = get_config(config_path)

        # Same instance (cached)
        assert config1 is config2

    def test_get_config_reload_bypasses_cache(self, sample_config_yaml_factory) -> None:
        """Test that reload=True bypasses cache."""
        config_path = sample_config_yaml_factory(year_start=2002)

        # First load
        config1 = get_config(config_path)
        assert config1.data.year_start == 2002

        # Modify YAML file (include all required fields)
        config_path.write_text("""
project:
  name: TestProject
  version: "2.0.0"
  description: Updated test configuration
data:
  year_start: 2010
  year_end: 2020
logging:
  level: INFO
determinism:
  random_seed: 42
  thread_count: 1
""")

        # Reload should get new values
        config2 = get_config(config_path, reload=True)
        assert config2.data.year_start == 2010

    def test_reload_config_raises_without_prior_load(self) -> None:
        """Test that reload_config raises ValueError if no config loaded."""
        clear_config_cache()
        with pytest.raises(ValueError, match="No configuration has been loaded"):
            reload_config()

    def test_reload_config_from_cached_path(self, sample_config_yaml_factory) -> None:
        """Test reload_config uses cached path."""
        config_path = sample_config_yaml_factory(year_start=2002)

        # Initial load
        config1 = get_config(config_path)

        # Modify file (include all required fields)
        config_path.write_text("""
project:
  name: TestProject
  version: "2.0.0"
  description: Updated test configuration
data:
  year_start: 2015
  year_end: 2020
logging:
  level: INFO
determinism:
  random_seed: 42
  thread_count: 1
""")

        # Reload should work
        config2 = reload_config()
        assert config2.data.year_start == 2015

    def test_get_config_file_not_found(self) -> None:
        """Test FileNotFoundError for missing config file."""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            get_config(Path("nonexistent/config.yaml"))

    def test_config_error_wraps_validation_errors(self, tmp_path: Path) -> None:
        """Test that ConfigError wraps validation errors with context."""
        # Create invalid config
        config_path = tmp_path / "invalid.yaml"
        config_path.write_text("""
project:
  name: Test
  version: "1.0"
data:
  year_start: 2020
  year_end: 2010  # Invalid: end before start
logging:
  level: INFO
""")

        with pytest.raises(ConfigError) as exc_info:
            get_config(config_path)

        # Check error message includes path
        assert str(config_path) in str(exc_info.value)
        assert "validation failed" in str(exc_info.value).lower()


class TestConfigError:
    """Tests for ConfigError exception class."""

    def test_config_error_with_path(self) -> None:
        """Test ConfigError includes path in message."""
        path = Path("config/test.yaml")
        error = ConfigError(path, "Invalid configuration")

        assert error.path == path
        assert error.message == "Invalid configuration"
        assert str(path) in str(error)
        assert "Invalid configuration" in str(error)

    def test_config_error_without_path(self) -> None:
        """Test ConfigError works with None path."""
        error = ConfigError(None, "General error")

        assert error.path is None
        assert error.message == "General error"
        assert "General error" in str(error)


class TestEnvOverrideFunctions:
    """Tests for environment variable override helper functions."""

    def test_validate_env_override_with_f1d_prefix(self) -> None:
        """Test validate_env_override recognizes F1D_ prefix."""
        os.environ["F1D_DATA__YEAR_START"] = "2010"

        assert validate_env_override("F1D_DATA__YEAR_START") is True

    def test_validate_env_override_without_f1d_prefix(self) -> None:
        """Test validate_env_override rejects non-F1D_ prefix."""
        os.environ["DATA__YEAR_START"] = "2010"

        assert validate_env_override("DATA__YEAR_START") is False

    def test_validate_env_override_not_set(self) -> None:
        """Test validate_env_override returns False for unset vars."""
        assert validate_env_override("F1D_NONEXISTENT_VAR") is False

    def test_get_config_sources_identifies_env_overrides(self) -> None:
        """Test get_config_sources identifies env vs yaml sources."""
        # Set an env override
        os.environ["F1D_DATA__YEAR_START"] = "2010"

        sources = get_config_sources()

        # This should be from env
        assert sources.get("data.year_start") == "env"

        # This should be from yaml (not set)
        assert sources.get("data.year_end") == "yaml"

    def test_get_config_sources_all_from_yaml_when_no_env(self) -> None:
        """Test get_config_sources shows yaml when no env vars set."""
        sources = get_config_sources()

        # All should be from yaml since no env vars set
        assert sources.get("data.year_start") == "yaml"
        assert sources.get("data.year_end") == "yaml"
        assert sources.get("logging.level") == "yaml"


class TestConfigCaching:
    """Tests for configuration cache behavior."""

    def test_clear_config_cache(self, sample_config_yaml_factory) -> None:
        """Test clear_config_cache clears the cache."""
        config_path = sample_config_yaml_factory()

        # Load to cache
        config1 = get_config(config_path)

        # Clear cache
        clear_config_cache()

        # Load again - should be new instance
        config2 = get_config(config_path)

        # Different instances after cache clear
        assert config1 is not config2
        # But same values
        assert config1.data.year_start == config2.data.year_start

    def test_cache_uses_path_for_validation(self, tmp_path: Path) -> None:
        """Test cache validates against path."""
        # Create two separate config files in the same temp directory
        config_path1 = tmp_path / "config1.yaml"
        config_path1.write_text("""
project:
  name: TestProject
  version: "1.0.0"
  description: Test configuration 1
data:
  year_start: 2002
  year_end: 2018
logging:
  level: INFO
determinism:
  random_seed: 42
  thread_count: 1
""")

        config_path2 = tmp_path / "config2.yaml"
        config_path2.write_text("""
project:
  name: TestProject
  version: "1.0.0"
  description: Test configuration 2
data:
  year_start: 2010
  year_end: 2020
logging:
  level: INFO
determinism:
  random_seed: 42
  thread_count: 1
""")

        # Load first config
        config1 = get_config(config_path1)

        # Load different path - should not use cache
        config2 = get_config(config_path2)

        assert config1.data.year_start == 2002
        assert config2.data.year_start == 2010


class TestEnvironmentVariableOverride:
    """Tests for environment variable overriding YAML values."""

    def test_env_var_override_year_start(self, sample_config_yaml_factory) -> None:
        """Test F1D_DATA__YEAR_START overrides YAML value."""
        config_path = sample_config_yaml_factory(year_start=2002, year_end=2018)

        # Set env override
        os.environ["F1D_DATA__YEAR_START"] = "2010"

        # Load config with override
        config = get_config(config_path, reload=True)

        # Env var should override
        assert config.data.year_start == 2010
        # Original YAML value should still be used for non-overridden
        assert config.data.year_end == 2018

    def test_env_var_override_logging_level(self, sample_config_yaml_factory) -> None:
        """Test F1D_LOGGING__LEVEL overrides YAML value."""
        config_path = sample_config_yaml_factory()

        os.environ["F1D_LOGGING__LEVEL"] = "DEBUG"

        config = get_config(config_path, reload=True)

        assert config.logging.level == "DEBUG"


class TestPathsSettings:
    """Tests for PathsSettings path resolution and validation."""

    def test_paths_resolve_basic_directories(self, tmp_path: Path) -> None:
        """Test resolve() returns basic directories."""
        from f1d.shared.config.paths import PathsSettings

        paths = PathsSettings()
        resolved = paths.resolve(tmp_path)

        assert "inputs" in resolved
        assert "outputs" in resolved
        assert "logs" in resolved
        assert "scripts" in resolved

        # Verify they are absolute paths
        assert resolved["inputs"].is_absolute()
        assert resolved["outputs"].is_absolute()

    def test_paths_resolve_optional_files(self, tmp_path: Path) -> None:
        """Test resolve() handles optional file paths."""
        from f1d.shared.config.paths import PathsSettings

        paths = PathsSettings(
            lm_dictionary="dictionaries/lm.txt",
            unified_info="data/unified.parquet",
        )
        resolved = paths.resolve(tmp_path)

        assert "lm_dictionary" in resolved
        assert "unified_info" in resolved

    def test_paths_resolve_pattern(self, tmp_path: Path) -> None:
        """Test resolve() keeps pattern as string."""
        from f1d.shared.config.paths import PathsSettings

        paths = PathsSettings(speaker_data_pattern="data/speakers_{year}.parquet")
        resolved = paths.resolve(tmp_path)

        assert "speaker_data_pattern" in resolved
        # Pattern should be string for later formatting
        assert isinstance(resolved["speaker_data_pattern"], str)
        assert "{year}" in resolved["speaker_data_pattern"]

    def test_paths_validate_paths_creates_directories(self, tmp_path: Path) -> None:
        """Test validate_paths creates output and log directories."""
        from f1d.shared.config.paths import PathsSettings

        # Create input directory so validation passes
        inputs_dir = tmp_path / "1_Inputs"
        inputs_dir.mkdir()

        paths = PathsSettings()
        resolved = paths.validate_paths(tmp_path)

        # Output and logs directories should be created
        assert (tmp_path / "4_Outputs").exists()
        assert (tmp_path / "3_Logs").exists()

    def test_paths_validate_paths_raises_for_missing_inputs(self, tmp_path: Path) -> None:
        """Test validate_paths raises FileNotFoundError for missing inputs."""
        from f1d.shared.config.paths import PathsSettings

        paths = PathsSettings()

        with pytest.raises(FileNotFoundError, match="Input directory not found"):
            paths.validate_paths(tmp_path)

    def test_paths_validate_paths_raises_for_missing_optional_files(
        self, tmp_path: Path
    ) -> None:
        """Test validate_paths raises for missing optional files."""
        from f1d.shared.config.paths import PathsSettings

        # Create inputs directory
        inputs_dir = tmp_path / "1_Inputs"
        inputs_dir.mkdir()

        # Specify optional file that doesn't exist
        paths = PathsSettings(lm_dictionary="nonexistent.txt")

        with pytest.raises(FileNotFoundError, match="LM dictionary not found"):
            paths.validate_paths(tmp_path)


class TestMultiModuleIntegration:
    """Tests for multi-module integration with config system."""

    def test_config_provides_paths_to_modules(self, sample_config_yaml_factory) -> None:
        """Test config paths can be used by other modules."""
        config_path = sample_config_yaml_factory()

        config = get_config(config_path)

        # Get resolved paths
        resolved = config.paths.resolve(Path("."))

        # Paths should be usable Path objects
        inputs_path = resolved["inputs"]
        assert isinstance(inputs_path, Path)

    def test_config_determinism_settings_available(self, sample_config_yaml_factory) -> None:
        """Test determinism settings are accessible for processing modules."""
        config_path = sample_config_yaml_factory()

        config = get_config(config_path)

        # Determinism settings should be accessible
        assert config.determinism.random_seed >= 0
        assert 1 <= config.determinism.thread_count <= 32
        assert isinstance(config.determinism.sort_inputs, bool)

    def test_config_chunk_processing_settings(self, sample_config_yaml_factory) -> None:
        """Test chunk processing settings are available."""
        config_path = sample_config_yaml_factory()

        config = get_config(config_path)

        # Chunk processing settings should have defaults
        assert 0 <= config.chunk_processing.max_memory_percent <= 100
        assert config.chunk_processing.base_chunk_size >= 1
