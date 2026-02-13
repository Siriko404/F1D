# Phase 67: Configuration & Testing Standard - Research

**Researched:** 2026-02-13
**Domain:** Python configuration management, testing infrastructure, pytest patterns
**Confidence:** HIGH

## Summary

This phase defines configuration management and testing infrastructure standards for the F1D pipeline. The research covers: (1) YAML configuration with Pydantic validation, (2) environment variable handling for secrets and optional dependencies, (3) src-layout package structure to eliminate sys.path.insert patterns, (4) timestamped output directories with checksums for reproducibility, (5) structured logging with structlog, and (6) comprehensive pytest testing patterns including fixture organization, coverage targets, naming conventions, and mocking strategies.

**Primary recommendation:** Create a unified CONFIG_TESTING_STANDARD.md that integrates with existing ARCHITECTURE_STANDARD.md and CODE_QUALITY_STANDARD.md, using pydantic-settings for configuration validation, structlog for structured logging, and pytest with factory fixtures for testing.

## User Constraints (from CONTEXT.md)

No CONTEXT.md exists for this phase. This is a definition-only milestone where Claude has discretion on approach.

**Locked Decisions (from Project Context):**
- [v5.0 Scope] Definition-only milestone - implementation deferred to v6.0+
- [65-01] Adopt src-layout over flat layout (PyPA recommendation)
- [65-01] Both V1 and V2 are active pipeline variants
- [65-01] Module tier system with quality bars (Tier 1-3)
- [66-01] Google-style docstrings for function/method documentation
- [66-01] Tier-based type hint coverage (100% Tier 1, 80% Tier 2, optional Tier 3)

**Claude's Discretion:**
- Configuration file schema design (project.yaml structure)
- Environment variable handling approach
- Output directory pattern specifics
- Logging format and level specifications
- Test organization and naming conventions
- Coverage target enforcement approach

**Deferred Ideas (OUT OF SCOPE):**
- Implementation of standards (deferred to v6.0+)
- CI/CD pipeline configuration
- Deployment procedures

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 8.0+ | Testing framework | Industry standard, powerful fixtures, marker system |
| pydantic | 2.0+ | Configuration validation | Type-safe config parsing with validation |
| pydantic-settings | 2.0+ | Environment variable management | Integrates YAML + env vars with secrets handling |
| PyYAML | 6.0+ | YAML parsing | Standard YAML library, already in use |
| structlog | 25.0+ | Structured logging | JSON logs, context binding, performance |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-cov | 5.0+ | Coverage reporting | CI pipelines, local coverage checks |
| pytest-mock | 3.12+ | Mocking utilities | Unit tests requiring mocks |
| coverage.py | 7.0+ | Coverage measurement | Via pytest-cov integration |
| freezegun | 1.4+ | Time mocking | Tests involving timestamps |
| pytest-xdist | 3.5+ | Parallel test execution | Large test suites |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pydantic-settings | dynaconf | Dynaconf has more features but heavier; pydantic-settings integrates better with existing pydantic usage |
| structlog | loguru | Loguru is simpler but structlog provides better structured output and context binding |
| pytest | unittest | unittest is stdlib but pytest fixtures and markers are significantly more powerful |
| pytest-mock | unittest.mock | pytest-mock provides cleaner fixture integration |

**Installation:**
```bash
# Already in project - maintain existing versions
pip install pytest>=8.0 pydantic>=2.0 pydantic-settings>=2.0 PyYAML>=6.0 structlog>=25.0 pytest-cov>=5.0
```

## Architecture Patterns

### Recommended Configuration Structure

```
config/
├── project.yaml              # Main project configuration (tracked)
├── logging.yaml              # Logging configuration (tracked)
├── hypotheses.yaml           # Hypothesis definitions (tracked)
├── .env.example              # Environment template (tracked)
└── .env                      # Local secrets (gitignored)
```

### Pattern 1: Pydantic Settings Configuration

**What:** Type-safe configuration with YAML file + environment variable override + validation
**When to use:** All configuration loading in the pipeline
**Example:**

```python
# src/f1d/shared/config.py
"""Configuration management with Pydantic Settings."""

from pathlib import Path
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class DataSettings(BaseSettings):
    """Data configuration settings."""
    year_start: int = Field(ge=2000, le=2030)
    year_end: int = Field(ge=2000, le=2030)

    @field_validator('year_end')
    @classmethod
    def validate_year_range(cls, v: int, info) -> int:
        if 'year_start' in info.data and v < info.data['year_start']:
            raise ValueError('year_end must be >= year_start')
        return v


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = "%(asctime)s [%(levelname)s] %(message)s"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"


class ProjectConfig(BaseSettings):
    """Main project configuration loaded from YAML with env var overrides."""

    model_config = SettingsConfigDict(
        env_prefix="F1D_",      # Environment variable prefix
        env_nested_delimiter="__",  # F1D_DATA__YEAR_START=2005
        extra="ignore"
    )

    # Project metadata
    name: str = "F1D_Clarity"
    version: str = "5.0.0"

    # Nested settings
    data: DataSettings
    logging: LoggingSettings = LoggingSettings()
    determinism: dict = Field(default_factory=lambda: {
        "random_seed": 42,
        "thread_count": 1,
        "sort_inputs": True
    })

    @classmethod
    def from_yaml(cls, path: Path) -> "ProjectConfig":
        """Load configuration from YAML file with environment variable overrides."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


# Usage
config = ProjectConfig.from_yaml(Path("config/project.yaml"))
```

**Source:** [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

### Pattern 2: Environment Variable Handling

**What:** Secure handling of secrets and optional dependencies via environment variables
**When to use:** External services (WRDS, APIs), deployment-specific settings

```python
# src/f1d/shared/env.py
"""Environment variable handling with validation."""

import os
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class EnvConfig(BaseSettings):
    """Environment-specific configuration with secrets handling."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Secrets (use SecretStr to prevent logging)
    wrds_username: Optional[str] = None
    wrds_password: Optional[SecretStr] = None  # Never logged in plain text

    # Optional dependency flags
    linearmodels_enabled: bool = Field(default=False, alias="LINEARMODELS_ENABLED")

    # API configuration
    api_timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)

    def get_wrds_password(self) -> Optional[str]:
        """Safely retrieve WRDS password."""
        if self.wrds_password:
            return self.wrds_password.get_secret_value()
        return None


# Usage
env = EnvConfig()
if env.linearmodels_enabled:
    import linearmodels  # Only import when enabled
```

### Pattern 3: Path Resolution (Eliminate sys.path.insert)

**What:** Proper package imports using src-layout with editable install
**When to use:** All imports in the project (current code uses sys.path.insert - migration required)

```toml
# pyproject.toml (updated for src-layout)
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build-meta"

[project]
name = "f1d"
version = "6.0.0"
requires-python = ">=3.9"

[tool.setuptools.packages.find]
where = ["src"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0", "ruff>=0.1.0"]
```

```python
# OLD PATTERN (to eliminate - found in 20+ files)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))
from shared.panel_ols import run_panel_ols  # BAD

# NEW PATTERN (after migration)
from f1d.shared.panel_ols import run_panel_ols  # GOOD
```

**Source:** [PyPA src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

### Pattern 4: Output Directory Pattern

**What:** Timestamped output directories with checksums for reproducibility
**When to use:** All pipeline script outputs

```python
# src/f1d/shared/output.py
"""Output directory management with timestamps and checksums."""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import List
import json


class OutputManager:
    """Manages timestamped output directories with reproducibility guarantees."""

    def __init__(self, base_path: Path, run_id: Optional[str] = None):
        self.base_path = base_path
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.run_id = run_id or self.timestamp
        self.output_dir = base_path / self.run_id
        self.checksums: dict[str, str] = {}

    def create_output_dir(self) -> Path:
        """Create timestamped output directory."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir

    def compute_checksum(self, filepath: Path, algorithm: str = "sha256") -> str:
        """Compute file checksum for integrity verification."""
        hasher = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def register_output(self, filepath: Path, description: str = "") -> Path:
        """Register output file with checksum."""
        checksum = self.compute_checksum(filepath)
        self.checksums[str(filepath.relative_to(self.output_dir))] = {
            "checksum": checksum,
            "algorithm": "sha256",
            "description": description,
            "created": datetime.now().isoformat()
        }
        return filepath

    def save_checksums(self) -> Path:
        """Save checksums manifest for reproducibility."""
        manifest_path = self.output_dir / "checksums.json"
        with open(manifest_path, "w") as f:
            json.dump({
                "run_id": self.run_id,
                "created": datetime.now().isoformat(),
                "files": self.checksums
            }, f, indent=2)
        return manifest_path

    def create_latest_symlink(self) -> Path:
        """Create/update 'latest' symlink to current output."""
        latest_path = self.base_path / "latest"
        if latest_path.is_symlink() or latest_path.exists():
            latest_path.unlink()
        latest_path.symlink_to(self.output_dir)
        return latest_path
```

### Pattern 5: Structured Logging

**What:** JSON-structured logging with context binding
**When to use:** All logging in the pipeline (replaces current DualWriter)

```python
# src/f1d/shared/logging.py
"""Structured logging configuration using structlog."""

import logging
import sys
from pathlib import Path
from typing import Any
import structlog


def configure_logging(
    log_level: str = "INFO",
    log_file: Path | None = None,
    json_output: bool = False
) -> None:
    """Configure structlog with optional file output."""

    # Shared processors for all loggers
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_output:
        # JSON format for machine parsing
        renderer = structlog.processors.JSONRenderer()
    else:
        # Human-readable console format
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[renderer],
        )
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                foreign_pre_chain=shared_processors,
                processors=[structlog.processors.JSONRenderer()],
            )
        )
        root_logger.addHandler(file_handler)


# Usage with context binding
logger = structlog.get_logger()

def process_data(df):
    log = logger.bind(gvkey_count=len(df["gvkey"].unique()))
    log.info("processing_started", stage="financial", rows=len(df))
    # ... processing ...
    log.info("processing_completed", rows_output=len(result))
```

**Source:** [structlog Documentation](https://www.structlog.org/en/stable/logging-best-practices.html)

### Pattern 6: Test Structure

**What:** Organized test directory with unit/integration/regression/e2e/performance tiers
**When to use:** All test organization

```
tests/
├── __init__.py
├── conftest.py               # Root-level shared fixtures
├── fixtures/                 # Test data files (parquet, csv, yaml)
│   ├── sample_data/
│   └── baseline_checksums.json
├── factories/                # Test data factories
│   ├── __init__.py
│   ├── dataframe_factory.py  # DataFrame generation
│   └── config_factory.py     # Configuration generation
├── unit/                     # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_panel_ols.py
│   └── test_path_utils.py
├── integration/              # Integration tests (module interactions)
│   ├── __init__.py
│   └── test_pipeline.py
├── regression/               # Regression tests (output stability)
│   ├── __init__.py
│   └── test_outputs.py
├── e2e/                      # End-to-end pipeline tests
│   ├── __init__.py
│   └── test_full_pipeline.py
└── performance/              # Performance benchmarks
    ├── __init__.py
    └── conftest.py           # Performance-specific fixtures
```

### Pattern 7: Test Naming Convention

**What:** Descriptive test names following `test_<module>_<function>_<scenario>` pattern
**When to use:** All test function names

```python
# GOOD: Descriptive test names
class TestRunPanelOls:
    """Tests for run_panel_ols function."""

    def test_run_panel_ols_valid_input_returns_results(self, sample_panel_data):
        """Test that valid input returns regression results."""
        pass

    def test_run_panel_ols_missing_columns_raises_error(self, sample_panel_data):
        """Test that missing required columns raises ValueError."""
        pass

    def test_run_panel_ols_multicollinearity_raises_collinearity_error(self, collinear_data):
        """Test that perfect multicollinearity raises CollinearityError."""
        pass

    def test_run_panel_ols_thin_cells_logs_warning(self, thin_cell_data, caplog):
        """Test that thin industry-year cells trigger warning."""
        pass


# BAD: Vague or non-descriptive names
def test_regression():  # What regression? What scenario?
def test_error():       # What error case?
def test_1():           # Numeric, no meaning
```

**Source:** [pytest Good Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)

### Pattern 8: Fixture Organization

**What:** Hierarchical conftest.py with factory fixtures
**When to use:** All shared test data and setup

```python
# tests/conftest.py - Root-level fixtures
"""Root-level pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
import pandas as pd
import numpy as np


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Path to repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dataframe_factory():
    """Factory fixture for creating sample DataFrames."""
    def _create(
        n_rows: int = 100,
        columns: dict | None = None,
        seed: int = 42
    ) -> pd.DataFrame:
        np.random.seed(seed)
        default_columns = {
            "gvkey": [f"{i:06d}" for i in np.random.randint(1, 1000, n_rows)],
            "year": np.random.randint(2000, 2020, n_rows),
            "value": np.random.randn(n_rows),
        }
        return pd.DataFrame(columns or default_columns)
    return _create


@pytest.fixture
def sample_panel_data(sample_dataframe_factory):
    """Sample panel data for regression tests."""
    return sample_dataframe_factory(
        n_rows=50,
        columns={
            "gvkey": [f"{i//5:06d}" for i in range(50)],  # 10 firms
            "year": [2000 + (i % 5) for i in range(50)],   # 5 years
            "dependent": np.random.randn(50),
            "independent": np.random.randn(50),
        }
    )


# tests/unit/conftest.py - Unit-test-specific fixtures
"""Unit test fixtures."""


@pytest.fixture
def mock_config(tmp_path):
    """Create temporary config file for unit tests."""
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text("""
project:
  name: TestProject
data:
  year_start: 2002
  year_end: 2005
""")
    return config_path


# tests/integration/conftest.py - Integration-test-specific fixtures
"""Integration test fixtures."""


@pytest.fixture(scope="module")
def subprocess_env(repo_root):
    """Environment for subprocess integration tests."""
    import os
    return {
        "PYTHONPATH": str(repo_root / "src"),
        **os.environ,
    }
```

**Source:** [pytest Fixtures Documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html)

### Pattern 9: Mocking and Test Data

**What:** pytest-mock integration with factory pattern for test data
**When to use:** Unit tests requiring isolation from external dependencies

```python
# tests/unit/test_financial_utils.py
"""Tests for financial utilities with mocking examples."""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd


class TestConstructVariables:
    """Tests for construct_variables function."""

    @pytest.fixture
    def mock_compustat_data(self, sample_dataframe_factory):
        """Factory-generated Compustat-like data."""
        return sample_dataframe_factory(
            n_rows=100,
            columns={
                "gvkey": [f"{i:06d}" for i in range(100)],
                "fyear": [2000] * 100,
                "at": [1000.0 + i * 10 for i in range(100)],  # Assets
                "che": [100.0 + i for i in range(100)],        # Cash
            }
        )

    def test_construct_variables_computes_cash_ratio(
        self, mock_compustat_data
    ):
        """Test that cash-to-assets ratio is computed correctly."""
        from f1d.financial.variables import construct_variables

        result = construct_variables(mock_compustat_data)

        assert "cash_ratio" in result.columns
        assert result["cash_ratio"].iloc[0] == pytest.approx(0.1, rel=0.01)

    @patch("f1d.financial.variables.load_compustat")
    def test_construct_variables_handles_missing_data(
        self, mock_load, mock_compustat_data
    ):
        """Test handling of missing Compustat data."""
        mock_load.return_value = mock_compustat_data

        # Test with missing values
        mock_compustat_data.loc[0:5, "at"] = pd.NA

        result = construct_variables(mock_compustat_data)

        assert result["cash_ratio"].isna().sum() == 5  # Missing for NA assets
```

**Source:** [Five Advanced Pytest Fixture Patterns](https://www.inspiredpython.com/article/five-advanced-pytest-fixture-patterns)

### Anti-Patterns to Avoid

- **sys.path.insert:** Use proper package imports with editable install instead
- **Empty conftest.py:** Should have at minimum docstring explaining purpose
- **Bare except:** Never catch all exceptions without logging (per CODE_QUALITY_STANDARD.md)
- **Magic numbers in tests:** Use named constants or fixtures
- **Shared mutable state:** Fixtures should return fresh data, not share references
- **Unparametrized similar tests:** Use @pytest.mark.parametrize for test variations
- **Logging sensitive data:** Use SecretStr for passwords, never log credentials
- **Hardcoded paths:** Always use Path objects and configuration for paths

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Configuration validation | Custom YAML parser with validation | pydantic-settings | Type safety, env var integration, validation built-in |
| Structured logging | Custom JSON formatter | structlog | Context binding, multiple outputs, performance |
| Test data generation | Manual DataFrame construction | Factory fixtures | Reusable, parametrizable, consistent |
| File checksums | Custom hash implementation | hashlib (stdlib) | Standard, well-tested, multiple algorithms |
| Mock objects | Manual mock classes | pytest-mock, unittest.mock | Auto-cleanup, assertion helpers |
| Coverage measurement | Manual line counting | pytest-cov, coverage.py | Branch coverage, report generation |

**Key insight:** The Python ecosystem has mature, well-tested solutions for all configuration and testing needs. Custom implementations introduce bugs and maintenance burden without adding value.

## Common Pitfalls

### Pitfall 1: sys.path.insert Scattered Throughout Codebase

**What goes wrong:** 20+ files in the current codebase use `sys.path.insert` to work around flat-layout imports. This causes:
- Import inconsistencies between scripts and tests
- Different behavior when running as module vs script
- Breakage when directory structure changes
- Inability to use proper package tools (mypy, IDE support)

**Why it happens:** Legacy flat-layout structure without proper package installation

**How to avoid:**
1. Adopt src-layout as defined in ARCHITECTURE_STANDARD.md
2. Configure pyproject.toml for editable install
3. Run `pip install -e .` once per environment
4. Replace all sys.path.insert with proper imports

**Warning signs:**
- `import sys; sys.path.insert` at top of files
- Tests only work with specific working directory
- IDE cannot resolve imports

### Pitfall 2: Configuration Sprawl

**What goes wrong:** Configuration spread across multiple files with inconsistent validation, hardcoded paths, and no type safety

**Why it happens:** Ad-hoc addition of configuration without central management

**How to avoid:**
1. Single config/project.yaml with schema
2. Use Pydantic models for all configuration sections
3. Environment variables for secrets and overrides
4. Validation on load, fail fast on misconfiguration

**Warning signs:**
- Multiple config files with overlapping settings
- Hardcoded paths in scripts
- Missing validation errors until runtime

### Pitfall 3: Fixture Pyramid

**What goes wrong:** Deep fixture hierarchies where test setup requires 5+ nested fixtures, making tests hard to understand and debug

**Why it happens:** Overusing fixture dependency injection instead of factory patterns

**How to avoid:**
1. Use factory fixtures for data generation
2. Keep fixtures flat where possible
3. Prefer composition over inheritance in fixtures
4. Document fixture dependencies clearly

**Warning signs:**
- Fixtures with 4+ parameters
- Tests that break when unrelated fixtures change
- Long stack traces in fixture failures

### Pitfall 4: Coverage Theater

**What goes wrong:** High coverage percentage but tests don't verify behavior, just exercise code paths

**Why it happens:** Focusing on metrics over meaningful tests

**How to avoid:**
1. Tier-based coverage targets (per ARCHITECTURE_STANDARD.md module tiers)
2. Focus on behavior verification, not line coverage
3. Use branch coverage, not just line coverage
4. Review uncovered code for test gaps

**Warning signs:**
- Tests with no assertions
- Coverage > 80% but bugs in production
- Tests that pass when code is broken

### Pitfall 5: Logging Sensitive Data

**What goes wrong:** Passwords, API keys, or secrets logged in plain text

**Why it happens:** Not using proper secret handling types

**How to avoid:**
1. Use SecretStr for password fields in Pydantic models
2. Never log raw config dictionaries
3. Use .get_secret_value() only when needed
4. Audit log output for sensitive data

**Warning signs:**
- Passwords visible in log files
- Config printed to console
- .env files tracked in git

## Code Examples

### Complete Configuration Example

```python
# src/f1d/shared/config.py
"""Complete configuration management example."""

from pathlib import Path
from typing import Dict, List, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class DeterminismSettings(BaseSettings):
    """Settings for reproducible execution."""
    random_seed: int = Field(default=42, ge=0)
    thread_count: int = Field(default=1, ge=1, le=32)
    sort_inputs: bool = True


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = "%(asctime)s [%(levelname)s] %(message)s"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"


class DataSettings(BaseSettings):
    """Data configuration settings."""
    year_start: int = Field(ge=2000, le=2030, description="Start year for data")
    year_end: int = Field(ge=2000, le=2030, description="End year for data")

    @model_validator(mode='after')
    def validate_year_range(self):
        if self.year_end < self.year_start:
            raise ValueError('year_end must be >= year_start')
        return self


class PathsSettings(BaseSettings):
    """Path configuration with defaults."""
    inputs: str = "data/raw"
    outputs: str = "results"
    logs: str = "logs"

    def resolve(self, base: Path) -> Dict[str, Path]:
        """Resolve all paths relative to base."""
        return {
            "inputs": base / self.inputs,
            "outputs": base / self.outputs,
            "logs": base / self.logs,
        }


class ProjectConfig(BaseSettings):
    """
    Main project configuration.

    Loads from YAML file with environment variable overrides.
    Environment variables use F1D_ prefix and __ delimiter for nested values.
    """

    model_config = SettingsConfigDict(
        env_prefix="F1D_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Project metadata
    name: str = "F1D_Clarity"
    version: str = "5.0.0"

    # Nested configuration sections
    data: DataSettings
    logging: LoggingSettings = LoggingSettings()
    determinism: DeterminismSettings = DeterminismSettings()
    paths: PathsSettings = PathsSettings()

    @classmethod
    def from_yaml(cls, path: Path) -> "ProjectConfig":
        """
        Load configuration from YAML file.

        Environment variables override YAML values.
        """
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        return cls(**data)

    def validate_paths(self, base: Path) -> Dict[str, Path]:
        """Validate and resolve all configured paths."""
        resolved = self.paths.resolve(base)
        for name, path in resolved.items():
            if not path.exists():
                if name == "outputs":
                    path.mkdir(parents=True, exist_ok=True)
                elif name == "logs":
                    path.mkdir(parents=True, exist_ok=True)
        return resolved


# Usage
if __name__ == "__main__":
    config = ProjectConfig.from_yaml(Path("config/project.yaml"))
    print(f"Project: {config.name} v{config.version}")
    print(f"Data range: {config.data.year_start}-{config.data.year_end}")
```

### Complete Test Example

```python
# tests/unit/test_path_utils.py
"""
Unit tests for path utilities module.

Tests verify path resolution, validation, and error handling.
Naming follows test_<module>_<function>_<scenario> convention.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

# After migration to src-layout
from f1d.shared.path_utils import (
    validate_output_path,
    ensure_output_dir,
    get_latest_output_dir,
    PathValidationError,
    OutputResolutionError,
)


class TestValidateOutputPath:
    """Tests for validate_output_path function."""

    def test_validate_output_path_existing_dir_returns_path(self, tmp_path):
        """Test that existing directory returns validated path."""
        result = validate_output_path(tmp_path, must_exist=True)
        assert result == tmp_path.resolve()

    def test_validate_output_path_nonexistent_with_must_exist_raises_error(self, tmp_path):
        """Test that nonexistent path with must_exist=True raises error."""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(PathValidationError, match="does not exist"):
            validate_output_path(nonexistent, must_exist=True)

    def test_validate_output_path_file_not_dir_raises_error(self, tmp_path):
        """Test that file path (not directory) raises error."""
        file_path = tmp_path / "file.txt"
        file_path.touch()
        with pytest.raises(PathValidationError, match="not a directory"):
            validate_output_path(file_path, must_exist=True)

    def test_validate_output_path_unwritable_raises_error(self, tmp_path):
        """Test that unwritable path raises error."""
        with patch.object(Path, 'touch', side_effect=PermissionError("denied")):
            with pytest.raises(PathValidationError, match="not writable"):
                validate_output_path(tmp_path, must_be_writable=True)


class TestEnsureOutputDir:
    """Tests for ensure_output_dir function."""

    def test_ensure_output_dir_creates_missing_directory(self, tmp_path):
        """Test that missing directory is created."""
        new_dir = tmp_path / "new_output"
        result = ensure_output_dir(new_dir)
        assert new_dir.exists()
        assert result == new_dir.resolve()

    def test_ensure_output_dir_existing_directory_returns_path(self, tmp_path):
        """Test that existing directory returns resolved path."""
        result = ensure_output_dir(tmp_path)
        assert result == tmp_path.resolve()


class TestGetLatestOutputDir:
    """Tests for get_latest_output_dir function."""

    @pytest.fixture
    def output_dirs(self, tmp_path):
        """Create timestamped output directories."""
        dates = ["2024-01-10", "2024-01-15", "2024-01-20"]
        for date in dates:
            (tmp_path / date).mkdir()
        return tmp_path

    def test_get_latest_output_dir_returns_most_recent(self, output_dirs):
        """Test that most recent directory is returned."""
        result = get_latest_output_dir(output_dirs)
        assert result.name == "2024-01-20"

    def test_get_latest_output_dir_empty_directory_raises_error(self, tmp_path):
        """Test that empty base directory raises error."""
        with pytest.raises(OutputResolutionError, match="No output directories"):
            get_latest_output_dir(tmp_path)

    def test_get_latest_output_dir_nonexistent_base_raises_error(self, tmp_path):
        """Test that nonexistent base path raises error."""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(OutputResolutionError, match="does not exist"):
            get_latest_output_dir(nonexistent)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual config parsing | Pydantic Settings with validation | 2024+ | Type safety, env var integration |
| print() statements | structlog structured logging | 2023+ | Machine-parseable logs, context binding |
| Flat layout with sys.path.insert | src-layout with pip install -e | PyPA recommendation | Proper imports, tool support |
| unittest.TestCase | pytest with fixtures | Industry standard | Less boilerplate, powerful fixtures |
| Global test fixtures | Factory fixtures | pytest best practice | Flexible test data generation |
| Line coverage only | Branch coverage | coverage.py default | Better quality measurement |

**Deprecated/outdated:**
- `nose` test runner: Use pytest instead
- `distutils`: Use setuptools with pyproject.toml
- `setup.py` only: Use pyproject.toml as primary configuration
- String-based config access: Use typed Pydantic models

## Open Questions

1. **Should CONFIG_TESTING_STANDARD.md be one document or two separate documents?**
   - What we know: Phase 67 requirements cover both configuration (CONF-01 to CONF-05) and testing (TEST-01 to TEST-05)
   - What's unclear: Whether to create unified standard or separate CONFIG_STANDARD.md + TESTING_STANDARD.md
   - Recommendation: Create unified CONFIG_TESTING_STANDARD.md for related infrastructure concerns, similar to how ARCHITECTURE_STANDARD.md covers multiple aspects

2. **Should coverage targets be enforced in CI or advisory?**
   - What we know: Current pyproject.toml has `fail_under = 60` for overall coverage
   - What's unclear: How strictly to enforce tier-based targets (Tier 1: 90%, Tier 2: 80%)
   - Recommendation: Enforce overall 70% in CI, track tier-based targets as quality gates for PRs

3. **How to handle legacy sys.path.insert during migration?**
   - What we know: 20+ files use this pattern, all need updating
   - What's unclear: Migration order and compatibility during transition
   - Recommendation: Create migration script per ARCHITECTURE_STANDARD.md Appendix A, migrate incrementally by stage

## Sources

### Primary (HIGH confidence)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Configuration management
- [structlog Documentation](https://www.structlog.org/en/stable/logging-best-practices.html) - Structured logging best practices
- [pytest Documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html) - Fixtures and testing patterns
- [PyPA src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) - Package structure recommendation

### Secondary (MEDIUM confidence)
- [Managing Application Configuration with Pydantic Settings](https://python.plainenglish.io/managing-application-configuration-in-python-with-pydantic-settings-c8c8694620c8) - Configuration patterns
- [pytest Fixture Factories](https://python.plainenglish.io/pytest-fixture-factories-the-secret-to-writing-flexible-maintainable-tests-2de79cf4084b) - Factory patterns
- [Five Advanced Pytest Fixture Patterns](https://www.inspiredpython.com/article/five-advanced-pytest-fixture-patterns) - Advanced testing patterns
- [Better Stack structlog Guide](https://betterstack.com/community/guides/logging/structlog/) - Structured logging implementation

### Tertiary (LOW confidence)
- None - all core findings verified with primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries are mature, well-documented, and widely adopted
- Architecture: HIGH - Patterns align with existing ARCHITECTURE_STANDARD.md and CODE_QUALITY_STANDARD.md
- Pitfalls: HIGH - Based on actual issues found in current codebase (sys.path.insert in 20+ files)
- Code examples: HIGH - Verified against official documentation

**Research date:** 2026-02-13
**Valid until:** 2027-02-13 (1 year - these are stable patterns)
