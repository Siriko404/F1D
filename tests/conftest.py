"""
Pytest configuration and shared fixtures for testing.

This file provides common fixtures used across all test files.

PYTEST CONFIGURATION

Subprocess Testing Pattern:
    Integration tests invoke pipeline scripts via subprocess.run().
    These scripts import from 'f1d.shared' modules (src-layout), requiring
    PYTHONPATH to be set for subprocess to find src/f1d/.

    Always use the subprocess_env fixture for subprocess calls:

        def test_my_script(subprocess_env):
            result = subprocess.run(
                ["python", "script.py"],
                env=subprocess_env,  # Critical: enables f1d.shared imports
                ...
            )

COVERAGE CONFIGURATION

Coverage.py configuration is managed via:
    - pyproject.toml [tool.coverage.*] sections
    - .coveragerc file (local override)
    - CI workflow pytest --cov flags

Branch coverage is enabled to measure both line and branch coverage.
"""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, Generator

import pandas as pd
import pytest
import yaml


@pytest.fixture(scope="session")
def repo_root():
    """Path to repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def subprocess_env():
    """
    Provide environment variables for subprocess calls in integration tests.

    Sets PYTHONPATH to enable subprocess to import f1d.shared modules (src-layout).
    All integration tests that invoke scripts via subprocess should use this:

        result = subprocess.run(
            ["python", str(script_path)],
            env=subprocess_env,
            ...
        )

    Returns:
        Dict[str, str]: Environment variables with PYTHONPATH set
    """
    import os
    from pathlib import Path

    repo_root = Path(__file__).parent.parent
    return {
        "PYTHONPATH": str(repo_root / "src" / "f1d"),
        **os.environ,  # Preserve existing environment variables
    }


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory (shared across all tests)."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "file_name": ["test1.docx", "test2.docx", "test3.docx"],
            "Total_Words": [100, 200, 150],
            "MaQaUnc_pct": [0.5, 0.75, 0.6],
        }
    )


@pytest.fixture
def sample_parquet_file(tmp_path, sample_dataframe):
    """Create a temporary Parquet file for testing."""
    file_path = tmp_path / "test_data.parquet"
    sample_dataframe.to_parquet(file_path)
    return file_path


@pytest.fixture
def sample_config_path(test_data_dir):
    """Path to sample project.yaml for testing."""
    config_path = test_data_dir / "sample_yaml" / "project.yaml"
    if not config_path.exists():
        pytest.skip(f"Sample config not found: {config_path}")
    return config_path


@pytest.fixture
def sample_parquet_file_with_schema(tmp_path):
    """Create a temporary Parquet file matching Unified-info schema."""
    df = pd.DataFrame(
        {
            "event_type": ["1", "1", "2"],  # String for object dtype
            "file_name": ["call1.docx", "call2.docx", "call3.docx"],
            "start_date": pd.to_datetime(["2002-01-15", "2002-02-20", "2002-03-10"]),
            "speaker_record_count": [2, 1, 1],  # Matches schema
        }
    )
    file_path = tmp_path / "unified_info_test.parquet"
    df.to_parquet(file_path)
    return file_path


@pytest.fixture
def mock_project_config(tmp_path):
    """Create a minimal project.yaml for testing."""
    config_data = {
        "project": {
            "name": "F1D_Test",
            "version": "1.0.0",
        },
        "data": {
            "year_start": 2002,
            "year_end": 2005,
        },
        "determinism": {
            "random_seed": 42,
            "thread_count": 1,
        },
    }
    config_path = tmp_path / "project.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return config_path


@pytest.fixture
def capture_output():
    """Capture stdout and stderr for testing console output."""

    class Capture:
        def __init__(self):
            self.stdout_buf = StringIO()
            self.stderr_buf = StringIO()
            self.old_stdout = sys.stdout
            self.old_stderr = sys.stderr

        def start(self):
            sys.stdout = self.stdout_buf
            sys.stderr = self.stderr_buf

        def stop(self):
            sys.stdout = self.old_stdout
            sys.stderr = self.old_stderr
            return (self.stdout_buf.getvalue(), self.stderr_buf.getvalue())

        def reset(self):
            self.stdout_buf = StringIO()
            self.stderr_buf = StringIO()

    capture = Capture()
    yield capture
    # Cleanup: restore original streams
    sys.stdout = capture.old_stdout
    sys.stderr = capture.old_stderr


# ==============================================================================
# Configuration Testing Fixtures
# ==============================================================================


@pytest.fixture
def sample_config_yaml(tmp_path: Path) -> Path:
    """Create a temporary project.yaml with minimal valid config.

    Returns:
        Path to the temporary config file.

    Example:
        def test_config_loading(sample_config_yaml):
            from f1d.shared.config import ProjectConfig
            config = ProjectConfig.from_yaml(sample_config_yaml)
            assert config.data.year_start == 2002
    """
    config_path = tmp_path / "project.yaml"
    config_path.write_text("""
project:
  name: TestProject
  version: "1.0.0"
  description: Test configuration for unit tests

data:
  year_start: 2002
  year_end: 2018

logging:
  level: INFO

determinism:
  random_seed: 42
  thread_count: 1
  sort_inputs: true
""")
    return config_path


@pytest.fixture
def sample_config(sample_config_yaml: Path):
    """Create a valid ProjectConfig instance for testing.

    Uses sample_config_yaml fixture to load the configuration.

    Returns:
        ProjectConfig instance populated from sample YAML.

    Example:
        def test_with_sample_config(sample_config):
            assert sample_config.data.year_start == 2002
    """
    from f1d.shared.config.base import ProjectConfig

    return ProjectConfig.from_yaml(sample_config_yaml)


@pytest.fixture
def invalid_config_yaml(tmp_path: Path) -> Path:
    """Create YAML with invalid values (year_start > year_end).

    Returns:
        Path to the temporary config file with invalid data.

    Example:
        def test_invalid_config_raises(invalid_config_yaml):
            from pydantic import ValidationError
            from f1d.shared.config import ProjectConfig
            with pytest.raises(ValidationError):
                ProjectConfig.from_yaml(invalid_config_yaml)
    """
    config_path = tmp_path / "invalid_config.yaml"
    config_path.write_text("""
project:
  name: InvalidProject
  version: "1.0.0"

data:
  year_start: 2018
  year_end: 2002  # Invalid: end before start

logging:
  level: INFO
""")
    return config_path


@pytest.fixture
@contextmanager
def env_override() -> Generator[Dict[str, str], None, None]:
    """Context manager to temporarily set environment variables.

    Restores original values on exit.

    Yields:
        Dict that can be used to track what was set.

    Example:
        def test_env_override(env_override):
            with env_override:
                os.environ['F1D_DATA__YEAR_START'] = '2010'
                # ... test code ...
            # Environment is restored after context exits
    """
    # Save original values
    env_vars_to_save = [k for k in os.environ if k.startswith("F1D_")]
    original_values = {k: os.environ[k] for k in env_vars_to_save}

    try:
        yield {}
    finally:
        # Remove any F1D_ vars that were added
        for k in list(os.environ.keys()):
            if k.startswith("F1D_"):
                del os.environ[k]
        # Restore original values
        for k, v in original_values.items():
            os.environ[k] = v


# ==============================================================================
# Factory Fixtures
# ==============================================================================
# These fixtures are factory functions that return callables for generating
# test data. They follow the callable fixture pattern from 74-01.


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

    Example:
        def test_with_config(sample_project_config_factory):
            config = sample_project_config_factory(year_start=2010, year_end=2015)
            assert config.data.year_start == 2010
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

        if data__year_start is not None:
            env_vars["F1D_DATA__YEAR_START"] = data__year_start
        if data__year_end is not None:
            env_vars["F1D_DATA__YEAR_END"] = data__year_end
        if logging__level is not None:
            env_vars["F1D_LOGGING__LEVEL"] = logging__level

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


# ==============================================================================
# Financial Data Factory Fixtures
# ==============================================================================
# These fixtures generate Compustat-style financial data for testing.


@pytest.fixture
def sample_compustat_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate Compustat-style panel data.

    Returns a callable that generates a DataFrame with standard Compustat
    columns for testing financial data processing functions.

    Args (via factory call):
        n_firms: Number of unique firms (default 10)
        n_years: Number of years per firm (default 5)
        seed: Random seed for reproducibility (default 42)

    Returns:
        pd.DataFrame with columns: gvkey, fyear, at, dlc, dltt, oancf, sale, ib
    """

    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        seed: int = 42,
    ) -> pd.DataFrame:
        import numpy as np

        rng = np.random.default_rng(seed)
        data = []

        for firm_id in range(n_firms):
            gvkey = str(firm_id).zfill(6)
            base_assets = rng.uniform(100, 10000)

            for year_offset in range(n_years):
                fyear = 2000 + year_offset
                # Generate realistic financial values
                at = base_assets * rng.uniform(0.9, 1.1)  # Total assets
                sale = at * rng.uniform(0.5, 2.0)  # Sales
                dlc = at * rng.uniform(0.01, 0.1)  # Debt in current liabilities
                dltt = at * rng.uniform(0.05, 0.3)  # Long-term debt
                oancf = sale * rng.uniform(-0.1, 0.2)  # Operating cash flow
                ib = sale * rng.uniform(-0.1, 0.15)  # Income before extraordinary items

                data.append({
                    "gvkey": gvkey,
                    "fyear": fyear,
                    "at": round(at, 2),
                    "dlc": round(dlc, 2),
                    "dltt": round(dltt, 2),
                    "oancf": round(oancf, 2),
                    "sale": round(sale, 2),
                    "ib": round(ib, 2),
                })

        return pd.DataFrame(data)

    return _factory


@pytest.fixture
def sample_panel_data_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate panel regression test data.

    Returns a callable that generates a DataFrame suitable for testing
    panel regression functions with dependent and independent variables.

    Args (via factory call):
        n_firms: Number of unique firms (default 10)
        n_years: Number of years per firm (default 5)
        n_independent: Number of independent variables (default 2)
        seed: Random seed for reproducibility (default 42)

    Returns:
        pd.DataFrame with columns: gvkey, year, dependent, independent1, ...
    """

    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        n_independent: int = 2,
        seed: int = 42,
    ) -> pd.DataFrame:
        import numpy as np

        rng = np.random.default_rng(seed)
        data = []

        for firm_id in range(n_firms):
            gvkey = str(firm_id).zfill(6)
            firm_effect = rng.normal(0, 1)  # Random firm fixed effect

            for year_offset in range(n_years):
                year = 2000 + year_offset

                # Generate independent variables
                independents = {}
                for i in range(n_independent):
                    independents[f"independent{i + 1}"] = rng.normal(0, 1)

                # Generate dependent variable with firm effect
                dependent = firm_effect + sum(independents.values()) + rng.normal(0, 0.5)

                # Generate industry code (ff48) - assign each firm to an industry
                ff48_code = (firm_id % 48) + 1  # Industries 1-48

                row = {
                    "gvkey": gvkey,
                    "year": year,
                    "dependent": round(dependent, 4),
                    "ff48_code": ff48_code,
                    **{k: round(v, 4) for k, v in independents.items()},
                }
                data.append(row)

        return pd.DataFrame(data)

    return _factory


@pytest.fixture
def sample_financial_row_factory() -> Callable[..., pd.Series]:
    """Factory fixture to generate a single Compustat row (Series).

    Returns a callable that generates a pd.Series representing a single
    Compustat observation. Useful for testing functions that operate on
    individual rows like calculate_firm_controls.

    Args (via factory call):
        gvkey: Firm identifier (default "000001")
        fyear: Fiscal year (default 2010)
        seed: Random seed for reproducibility (default 42)

    Returns:
        pd.Series with Compustat columns: gvkey, fyear, at, dlc, dltt, oancf, sale, ib
    """

    def _factory(
        gvkey: str = "000001",
        fyear: int = 2010,
        seed: int = 42,
    ) -> pd.Series:
        import numpy as np

        rng = np.random.default_rng(seed)

        at = rng.uniform(100, 10000)
        sale = at * rng.uniform(0.5, 2.0)
        dlc = at * rng.uniform(0.01, 0.1)
        dltt = at * rng.uniform(0.05, 0.3)
        oancf = sale * rng.uniform(-0.1, 0.2)
        ib = sale * rng.uniform(-0.1, 0.15)

        return pd.Series({
            "gvkey": gvkey,
            "fyear": fyear,
            "at": round(at, 2),
            "dlc": round(dlc, 2),
            "dltt": round(dltt, 2),
            "oancf": round(oancf, 2),
            "sale": round(sale, 2),
            "ib": round(ib, 2),
        })

    return _factory
