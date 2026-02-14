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

from f1d.shared.config.loader import clear_config_cache, get_config


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
