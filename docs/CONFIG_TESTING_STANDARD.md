# F1D Configuration and Testing Standard

**Version:** 5.0
**Last Updated:** 2026-02-13
**Status:** DEFINITION - Implementation deferred to v6.0+
**Milestone:** v5.0 Architecture Standard Definition

---

## Purpose

This document defines the configuration management and testing infrastructure standards for the F1D (Financial Text Analysis) data processing pipeline. It builds on the foundation established in ARCHITECTURE_STANDARD.md (folder structure, module organization) and CODE_QUALITY_STANDARD.md (naming conventions, docstrings) and ensures:

- **Type Safety:** All configuration validated at load time with pydantic-settings
- **Reproducibility:** Outputs are deterministic, versioned, and verifiable
- **Testability:** Code designed for testing from the start
- **Security:** Secrets handled securely, never logged in plain text

This is a **DEFINITION document**. The standards described here represent the target configuration and testing patterns that will be implemented in v6.0+. Current code may not fully comply with all standards.

---

## Document Structure

This standard is organized into 10 main sections:

**Configuration Requirements (CONF-01 to CONF-05):**
1. **Configuration File Structure (CONF-01):** YAML schema with pydantic-settings validation
2. **Environment Variable Handling (CONF-02):** Secrets management with SecretStr
3. **Path Resolution Pattern (CONF-03):** Eliminating sys.path.insert with src-layout
4. **Output Directory Pattern (CONF-04):** Timestamped runs with checksums
5. **Logging Pattern (CONF-05):** Structured logging with structlog

**Testing Requirements (TEST-01 to TEST-05):**
6. **Test Structure (TEST-01):** Unit/integration/regression/e2e/performance tiers
7. **Coverage Targets (TEST-02):** Tier-based coverage requirements
8. **Test Naming Convention (TEST-03):** Descriptive test function names
9. **Fixture Organization (TEST-04):** Hierarchical conftest.py with factory fixtures
10. **Mocking and Test Data (TEST-05):** pytest-mock and test data patterns

Additionally:
- **Appendix A**: Quick Reference Card
- **Appendix B**: Related Standards
- **Appendix C**: Anti-Patterns Summary

---

## How to Use This Standard

### For New Development (v6.0+)

1. Use pydantic-settings for all configuration loading (CONF-01)
2. Handle secrets with SecretStr (CONF-02)
3. Use proper package imports, never sys.path.insert (CONF-03)
4. Create timestamped output directories with checksums (CONF-04)
5. Use structlog for structured logging (CONF-05)
6. Follow test structure conventions (TEST-01)
7. Meet tier-based coverage targets (TEST-02)
8. Use descriptive test names (TEST-03)
9. Organize fixtures hierarchically (TEST-04)
10. Use pytest-mock for test isolation (TEST-05)

### For Current Development (v5.0)

1. Use this standard as reference for understanding the target patterns
2. New code should align with these patterns where feasible
3. Document deviations from the standard
4. Plan for migration to the standard patterns

### For Code Review

1. Check configuration follows pydantic-settings pattern
2. Verify secrets are handled with SecretStr
3. Ensure no sys.path.insert patterns exist
4. Confirm output directories follow timestamped pattern
5. Verify test coverage meets tier requirements
6. Check test names follow naming convention

---

## Design Principles

### 1. Type Safety (Configuration Validation)

All configuration must be validated at load time, not at runtime:

- **Schema enforcement:** Pydantic models define configuration structure
- **Type coercion:** Automatic conversion with validation
- **Fail fast:** Configuration errors caught immediately on startup
- **IDE support:** Type hints enable autocomplete and static analysis

**Implementation:**
- Use pydantic-settings for all configuration
- Define nested settings classes for configuration sections
- Add field validators for business rules
- Never use raw dictionaries for configuration

### 2. Reproducibility (Deterministic Outputs)

Every output must be reproducible and verifiable:

- **Timestamped runs:** Each execution creates unique output directory
- **Checksums:** SHA-256 hashes verify file integrity
- **Configuration capture:** Full configuration saved with outputs
- **Random seeds:** All randomness controlled via configuration

**Implementation:**
- OutputManager creates timestamped directories
- Checksums computed for all output files
- Configuration serialized to output directory
- Random seeds set from configuration

### 3. Testability (Design for Testing)

Code must be designed for testing from the start:

- **Dependency injection:** External dependencies passed, not imported
- **Pure functions:** Prefer functions without side effects
- **Modular design:** Small, testable units
- **Mock-friendly:** External services easy to mock

**Implementation:**
- Use factory fixtures for test data
- Mock external APIs with pytest-mock
- Test edge cases and error paths
- Separate concerns for isolated testing

### 4. Security (Secrets Handling)

Secrets must never be exposed in logs or configuration files:

- **SecretStr:** Passwords and API keys use SecretStr type
- **Environment variables:** Secrets from .env files (gitignored)
- **No logging:** SecretStr values never logged in plain text
- **.env.example:** Template file documents required secrets

**Implementation:**
- Use SecretStr for sensitive configuration
- Access secrets via .get_secret_value() only when needed
- Never log configuration dictionaries directly
- Audit log output for sensitive data

---

## Relationship to Other Standards

This configuration and testing standard builds upon and references:

### ARCHITECTURE_STANDARD.md

**Cross-references:**
- Folder structure for config/ and tests/ directories
- Module tier system (Tier 1, 2, 3) for coverage targets
- src-layout pattern eliminates sys.path.insert
- Version management for configuration versioning

**Key alignment:**
- Configuration files in config/ directory
- Tests in tests/ directory mirroring src/ structure
- Coverage targets aligned with module tiers

### CODE_QUALITY_STANDARD.md

**Cross-references:**
- Naming conventions for test functions
- Type hint requirements per module tier
- Error handling patterns in configuration loading
- Docstring standards for configuration classes

**Key alignment:**
- Test naming follows descriptive pattern
- Configuration classes have Google-style docstrings
- Error handling uses custom exception hierarchy

---

## Scope and Exclusions

### In Scope

- Configuration file structure and validation
- Environment variable handling for secrets
- Path resolution and package imports
- Output directory management
- Structured logging patterns
- Test organization and structure
- Coverage targets and measurement
- Test naming conventions
- Fixture organization patterns
- Mocking and test data patterns

### Out of Scope

- CI/CD pipeline configuration (future phase)
- Deployment and environment provisioning
- Database configuration (not applicable)
- Performance testing specifics (benchmark definitions)

---

## Standard Stack

### Core Libraries

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 8.0+ | Testing framework | Industry standard, powerful fixtures, marker system |
| pydantic | 2.0+ | Configuration validation | Type-safe config parsing with validation |
| pydantic-settings | 2.0+ | Environment variable management | Integrates YAML + env vars with secrets handling |
| PyYAML | 6.0+ | YAML parsing | Standard YAML library, already in use |
| structlog | 25.0+ | Structured logging | JSON logs, context binding, performance |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-cov | 5.0+ | Coverage reporting | CI pipelines, local coverage checks |
| pytest-mock | 3.12+ | Mocking utilities | Unit tests requiring mocks |
| coverage.py | 7.0+ | Coverage measurement | Via pytest-cov integration |
| freezegun | 1.4+ | Time mocking | Tests involving timestamps |
| pytest-xdist | 3.5+ | Parallel test execution | Large test suites |

**Installation:**
```bash
pip install pytest>=8.0 pydantic>=2.0 pydantic-settings>=2.0 PyYAML>=6.0 structlog>=25.0 pytest-cov>=5.0
```

---

---

## 1. Configuration File Structure (CONF-01)

This section defines the configuration file structure using YAML with pydantic-settings for type-safe validation.

### Recommended Config Directory Structure

```
config/
├── project.yaml              # Main project configuration (tracked)
├── logging.yaml              # Logging configuration (tracked)
├── hypotheses.yaml           # Hypothesis definitions (tracked)
├── .env.example              # Environment template (tracked)
└── .env                      # Local secrets (gitignored)
```

### project.yaml Schema

The main configuration file should follow this structure:

```yaml
# config/project.yaml
# F1D Pipeline Configuration
# Version: 5.0

project:
  name: F1D_Clarity
  version: "5.0.0"

data:
  year_start: 2002
  year_end: 2022

logging:
  level: INFO
  format: "%(asctime)s [%(levelname)s] %(message)s"
  timestamp_format: "%Y-%m-%d %H:%M:%S"

determinism:
  random_seed: 42
  thread_count: 1
  sort_inputs: true

paths:
  inputs: data/raw
  outputs: results
  logs: logs
```

### Pydantic Settings Model

Define type-safe configuration models using pydantic-settings:

```python
# src/f1d/shared/config.py
"""Configuration management with Pydantic Settings.

This module provides type-safe configuration loading from YAML files
with environment variable overrides and validation.

Example:
    >>> from f1d.shared.config import ProjectConfig
    >>> config = ProjectConfig.from_yaml(Path("config/project.yaml"))
    >>> print(config.data.year_start)
    2002
"""

from pathlib import Path
from typing import Dict, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class DataSettings(BaseSettings):
    """Data configuration settings.

    Attributes:
        year_start: Start year for data range (inclusive).
        year_end: End year for data range (inclusive).
    """

    year_start: int = Field(ge=2000, le=2030, description="Start year for data")
    year_end: int = Field(ge=2000, le=2030, description="End year for data")

    @model_validator(mode='after')
    def validate_year_range(self) -> "DataSettings":
        """Validate that year_end >= year_start."""
        if self.year_end < self.year_start:
            raise ValueError('year_end must be >= year_start')
        return self


class LoggingSettings(BaseSettings):
    """Logging configuration settings.

    Attributes:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format: Log message format string.
        timestamp_format: Timestamp format for log messages.
    """

    level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    format: str = "%(asctime)s [%(levelname)s] %(message)s"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"


class DeterminismSettings(BaseSettings):
    """Settings for reproducible execution.

    Attributes:
        random_seed: Seed for random number generators.
        thread_count: Number of threads for parallel processing.
        sort_inputs: Whether to sort inputs for determinism.
    """

    random_seed: int = Field(default=42, ge=0)
    thread_count: int = Field(default=1, ge=1, le=32)
    sort_inputs: bool = True


class PathsSettings(BaseSettings):
    """Path configuration with defaults.

    Attributes:
        inputs: Path to input data directory.
        outputs: Path to output directory.
        logs: Path to logs directory.
    """

    inputs: str = "data/raw"
    outputs: str = "results"
    logs: str = "logs"

    def resolve(self, base: Path) -> Dict[str, Path]:
        """Resolve all paths relative to base directory.

        Args:
            base: Base directory to resolve paths from.

        Returns:
            Dictionary mapping path names to resolved Path objects.
        """
        return {
            "inputs": base / self.inputs,
            "outputs": base / self.outputs,
            "logs": base / self.logs,
        }


class ProjectConfig(BaseSettings):
    """Main project configuration loaded from YAML.

    Loads from YAML file with environment variable overrides.
    Environment variables use F1D_ prefix and __ delimiter.

    Attributes:
        name: Project name.
        version: Project version string.
        data: Data configuration settings.
        logging: Logging configuration settings.
        determinism: Determinism settings.
        paths: Path configuration settings.

    Example:
        >>> config = ProjectConfig.from_yaml(Path("config/project.yaml"))
        >>> print(config.name)
        F1D_Clarity
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
        """Load configuration from YAML file.

        Environment variables override YAML values.

        Args:
            path: Path to YAML configuration file.

        Returns:
            ProjectConfig instance with loaded values.

        Raises:
            FileNotFoundError: If configuration file does not exist.
            ValueError: If configuration validation fails.
        """
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        return cls(**data)

    def validate_paths(self, base: Path) -> Dict[str, Path]:
        """Validate and resolve all configured paths.

        Creates output and log directories if they don't exist.

        Args:
            base: Base directory to resolve paths from.

        Returns:
            Dictionary mapping path names to resolved Path objects.
        """
        resolved = self.paths.resolve(base)
        for name, path in resolved.items():
            if not path.exists():
                if name in ("outputs", "logs"):
                    path.mkdir(parents=True, exist_ok=True)
        return resolved
```

### Validation Rules

| Field | Validation | Error Message |
|-------|------------|---------------|
| data.year_start | 2000 <= value <= 2030 | "Input should be greater than or equal to 2000" |
| data.year_end | 2000 <= value <= 2030 | "Input should be less than or equal to 2030" |
| data.year_range | year_end >= year_start | "year_end must be >= year_start" |
| logging.level | DEBUG/INFO/WARNING/ERROR/CRITICAL | "String should match pattern" |
| determinism.random_seed | value >= 0 | "Input should be greater than or equal to 0" |
| determinism.thread_count | 1 <= value <= 32 | "Input should be between 1 and 32" |

### Usage Example

```python
# Loading configuration in a script
from pathlib import Path
from f1d.shared.config import ProjectConfig

# Load from YAML with environment variable overrides
config = ProjectConfig.from_yaml(Path("config/project.yaml"))

# Access nested configuration
print(f"Project: {config.name} v{config.version}")
print(f"Data range: {config.data.year_start}-{config.data.year_end}")
print(f"Log level: {config.logging.level}")

# Override via environment variable
# export F1D_DATA__YEAR_START=2005
# export F1D_LOGGING__LEVEL=DEBUG

# Validate and resolve paths
paths = config.validate_paths(Path.cwd())
print(f"Output directory: {paths['outputs']}")
```

### Cross-field Validation

For validation that depends on multiple fields:

```python
class DataSettings(BaseSettings):
    """Data configuration with cross-field validation."""

    year_start: int = Field(ge=2000, le=2030)
    year_end: int = Field(ge=2000, le=2030)
    min_observations: int = Field(default=100, ge=10)

    @model_validator(mode='after')
    def validate_settings(self) -> "DataSettings":
        """Validate cross-field constraints."""
        years = self.year_end - self.year_start + 1
        if years < 5:
            raise ValueError(
                f"Data range must span at least 5 years, got {years}"
            )
        min_expected = years * 100
        if self.min_observations < min_expected:
            raise ValueError(
                f"min_observations ({self.min_observations}) too low "
                f"for {years} years (expected >= {min_expected})"
            )
        return self
```

### Rationale

#### Why YAML for Configuration?

1. **Human readable:** Easy to edit and understand
2. **Comments supported:** Document configuration choices
3. **Industry standard:** Widely used for configuration
4. **Tool support:** Good editor support with validation

#### Why pydantic-settings?

1. **Type safety:** Automatic validation and type coercion
2. **Environment integration:** Seamless env var overrides
3. **Secrets handling:** SecretStr for sensitive data
4. **IDE support:** Autocomplete and type checking
5. **Documentation:** Field descriptions become documentation

**Source:** [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

## 2. Environment Variable Handling (CONF-02)

This section defines the pattern for secure handling of secrets and optional dependencies via environment variables.

### EnvConfig Pattern

Use pydantic-settings with SecretStr for secure secret management:

```python
# src/f1d/shared/env.py
"""Environment variable handling with validation.

This module provides secure handling of secrets and environment-specific
configuration using pydantic-settings with SecretStr for sensitive data.

Example:
    >>> from f1d.shared.env import EnvConfig
    >>> env = EnvConfig()
    >>> if env.wrds_password:
    ...     password = env.get_wrds_password()  # Only when needed
"""

import os
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    """Environment-specific configuration with secrets handling.

    Configuration is loaded from .env file with environment variable
    overrides. Secrets are protected with SecretStr type.

    Attributes:
        wrds_username: Username for WRDS data access.
        wrds_password: Password for WRDS (SecretStr - never logged).
        linearmodels_enabled: Flag for optional linearmodels dependency.
        api_timeout_seconds: Timeout for external API calls.
        max_retries: Maximum retry attempts for API calls.

    Example:
        >>> env = EnvConfig()
        >>> print(env.wrds_username)  # OK to print
        >>> print(env.wrds_password)  # Shows 'SecretStr(...)'
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Secrets (use SecretStr to prevent logging)
    wrds_username: Optional[str] = None
    wrds_password: Optional[SecretStr] = None  # Never logged in plain text

    # Optional dependency flags
    linearmodels_enabled: bool = Field(
        default=False,
        alias="LINEARMODELS_ENABLED"
    )

    # API configuration
    api_timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)

    def get_wrds_password(self) -> Optional[str]:
        """Safely retrieve WRDS password.

        Returns:
            Password string or None if not configured.

        Note:
            Only call this when the password is actually needed.
            Never log or print the returned value.
        """
        if self.wrds_password:
            return self.wrds_password.get_secret_value()
        return None


# Usage
env = EnvConfig()
if env.linearmodels_enabled:
    import linearmodels  # Only import when enabled
```

### .env File Structure

Create a `.env` file for local secrets (gitignored):

```bash
# .env (DO NOT COMMIT)
# WRDS credentials
WRDS_USERNAME=your_username
WRDS_PASSWORD=your_password

# Optional dependencies
LINEARMODELS_ENABLED=true

# API settings
API_TIMEOUT_SECONDS=60
MAX_RETRIES=5
```

### .env.example Template

Always provide a template file (tracked in git):

```bash
# .env.example (commit this file)
# Copy to .env and fill in values

# WRDS credentials (required for data download)
WRDS_USERNAME=your_wrds_username
WRDS_PASSWORD=your_wrds_password

# Optional dependencies
LINEARMODELS_ENABLED=false

# API settings
API_TIMEOUT_SECONDS=30
MAX_RETRIES=3
```

### Environment Variable Naming Convention

Use the `F1D_` prefix with `__` delimiter for nested values:

| Environment Variable | Configuration Path |
|---------------------|-------------------|
| `F1D_DATA__YEAR_START=2005` | `config.data.year_start` |
| `F1D_LOGGING__LEVEL=DEBUG` | `config.logging.level` |
| `F1D_DETERMINISM__RANDOM_SEED=123` | `config.determinism.random_seed` |

**Example:**
```bash
# Override configuration via environment
export F1D_DATA__YEAR_START=2005
export F1D_DATA__YEAR_END=2020
export F1D_LOGGING__LEVEL=DEBUG

# Python code automatically picks up overrides
config = ProjectConfig.from_yaml(Path("config/project.yaml"))
# config.data.year_start == 2005 (from env, not YAML)
```

### Security Best Practices

#### DO:
- Use `SecretStr` for all passwords, API keys, and tokens
- Access secrets via `.get_secret_value()` only when needed
- Keep `.env` in `.gitignore`
- Provide `.env.example` for documentation
- Use environment variables for deployment-specific settings

#### DON'T:
- Log `SecretStr` values directly (shows `SecretStr(...)`)
- Print configuration dictionaries that contain secrets
- Commit `.env` files to version control
- Store secrets in YAML configuration files
- Use plain strings for sensitive configuration

### Logging Secrets Safely

```python
# BAD: Logging configuration directly
logger.info(f"Configuration: {config.dict()}")  # May expose secrets

# GOOD: Log non-sensitive configuration only
logger.info(
    "Configuration loaded",
    extra={
        "project": config.name,
        "version": config.version,
        "data_range": f"{config.data.year_start}-{config.data.year_end}",
    }
)

# GOOD: SecretStr values are protected
env = EnvConfig()
print(env.wrds_password)  # Output: SecretStr('**********')
```

### Rationale

#### Why SecretStr?

1. **Prevents accidental exposure:** `print()` and `str()` show `SecretStr(...)`
2. **Logging safety:** Structured logging won't serialize the actual value
3. **Explicit access:** Must call `.get_secret_value()` to retrieve
4. **Type safety:** Clear distinction between public and secret config

**Source:** [Pydantic Secret Types](https://docs.pydantic.dev/latest/concepts/fields/#secret-types)

---

## 3. Path Resolution Pattern (CONF-03)

This section defines the pattern for eliminating `sys.path.insert` hacks using proper src-layout package structure.

### The Problem: sys.path.insert Anti-Pattern

The current codebase has `sys.path.insert` in 20+ files:

```python
# BAD: sys.path.insert scattered throughout codebase
import sys
from pathlib import Path

# Found in 20+ files
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.panel_ols import run_panel_ols  # Fragile import
```

**Issues with this pattern:**
- Import inconsistencies between scripts and tests
- Different behavior when running as module vs script
- Breakage when directory structure changes
- No IDE support for imports
- mypy and other tools can't resolve imports

### The Solution: src-layout with Editable Install

#### pyproject.toml Configuration

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build-meta"

[project]
name = "f1d"
version = "6.0.0"
description = "F1D Data Processing Pipeline for CEO Uncertainty Research"
requires-python = ">=3.9"

[tool.setuptools.packages.find]
where = ["src"]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-mock>=3.12",
    "ruff>=0.1.0",
    "mypy>=1.0",
]
```

#### Installation

```bash
# Install package in editable mode (one-time setup)
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

### Migration Pattern

**Before (current code):**
```python
# 2_Scripts/3_Financial/script_32_construct_variables.py
import sys
from pathlib import Path

# Anti-pattern: manipulating sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.panel_ols import run_panel_ols
from shared.path_utils import get_latest_output_dir
```

**After (with src-layout):**
```python
# src/f1d/financial/v1/variables.py
# Clean imports with no sys.path manipulation
from f1d.shared.panel_ols import run_panel_ols
from f1d.shared.path_utils import get_latest_output_dir
```

### Import Resolution

With src-layout and editable install:

```python
# All imports use the f1d package namespace
from f1d import get_latest_output_dir  # From top-level __init__.py
from f1d.shared.panel_ols import run_panel_ols
from f1d.financial.v1.variables import construct_variables
from f1d.econometric.v2.regressions import run_panel_ols
```

### Verification

After migration, verify imports work from any directory:

```bash
# Should work from project root
python -c "from f1d.shared.panel_ols import run_panel_ols; print('OK')"

# Should work from any subdirectory
cd tests/unit
python -c "from f1d.shared.panel_ols import run_panel_ols; print('OK')"

# Should work when running as module
python -m f1d.financial.v1.variables
```

### Migration Script

Use this script to find and update sys.path.insert patterns:

```python
# scripts/migrate_imports.py
"""Migration script for sys.path.insert elimination."""

import re
from pathlib import Path
from typing import List, Tuple

PATTERNS = [
    # Pattern: sys.path.insert(0, ...)
    (r'sys\.path\.insert\(0,\s*str\(Path\(__file__\)\.parent\.parent\)\)', ''),
    (r'sys\.path\.insert\(0,\s*str\(Path\(__file__\)\.parent\.parent\.parent / "2_Scripts"\)\)', ''),
    # Pattern: from shared.xxx import
    (r'from shared\.', 'from f1d.shared.'),
    # Pattern: from script_XX_ import
    (r'from script_(\d+)_', 'from f1d.'),
]

def migrate_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Migrate a single file to use proper imports.

    Args:
        file_path: Path to Python file.

    Returns:
        Tuple of (modified, list of changes).
    """
    content = file_path.read_text()
    original = content
    changes = []

    for pattern, replacement in PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes.append(f"Replaced: {pattern}")

    if content != original:
        file_path.write_text(content)
        return True, changes
    return False, []

def find_sys_path_files(root: Path) -> List[Path]:
    """Find all Python files with sys.path.insert.

    Args:
        root: Root directory to search.

    Returns:
        List of files containing sys.path.insert.
    """
    files = []
    for py_file in root.rglob("*.py"):
        if "___archive" in str(py_file):
            continue
        content = py_file.read_text()
        if "sys.path.insert" in content:
            files.append(py_file)
    return files

if __name__ == "__main__":
    root = Path(".")
    files = find_sys_path_files(root)
    print(f"Found {len(files)} files with sys.path.insert")
    for f in files:
        print(f"  {f}")
```

### Rationale

#### Why src-layout?

1. **Prevents import confusion:** Separates importable code from project files
2. **Better editable installs:** `pip install -e .` works correctly
3. **Early error detection:** Packaging issues surface before distribution
4. **Industry standard:** PyPA recommendation for modern projects

**Source:** [PyPA src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

---

## 4. Output Directory Pattern (CONF-04)

This section defines the pattern for timestamped output directories with checksums for reproducibility.

### OutputManager Pattern

Use a centralized OutputManager for reproducible outputs:

```python
# src/f1d/shared/output.py
"""Output directory management with timestamps and checksums.

This module provides utilities for creating timestamped output directories
and computing checksums for output files, ensuring reproducibility.

Example:
    >>> from f1d.shared.output import OutputManager
    >>> manager = OutputManager(Path("results/financial"))
    >>> output_dir = manager.create_output_dir()
    >>> # Save outputs...
    >>> manager.register_output(output_file, "Financial variables")
    >>> manager.save_checksums()
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any


class OutputManager:
    """Manages timestamped output directories with reproducibility guarantees.

    Creates unique directories for each run with automatic timestamping
    and checksum computation for all output files.

    Attributes:
        base_path: Base directory for outputs.
        run_id: Unique identifier for this run.
        timestamp: ISO format timestamp of run start.
        output_dir: Full path to this run's output directory.

    Example:
        >>> manager = OutputManager(Path("results"))
        >>> manager.create_output_dir()
        >>> manager.output_dir.name  # e.g., "2024-01-15_143022"
    """

    def __init__(self, base_path: Path, run_id: Optional[str] = None):
        """Initialize OutputManager.

        Args:
            base_path: Base directory for outputs.
            run_id: Optional custom run ID. Defaults to timestamp.
        """
        self.base_path = base_path
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.run_id = run_id or self.timestamp
        self.output_dir = base_path / self.run_id
        self.checksums: Dict[str, Dict[str, Any]] = {}

    def create_output_dir(self) -> Path:
        """Create timestamped output directory.

        Returns:
            Path to the created output directory.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir

    def compute_checksum(
        self,
        filepath: Path,
        algorithm: str = "sha256"
    ) -> str:
        """Compute file checksum for integrity verification.

        Args:
            filepath: Path to file to hash.
            algorithm: Hash algorithm (sha256, md5, etc.).

        Returns:
            Hexadecimal checksum string.
        """
        hasher = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def register_output(
        self,
        filepath: Path,
        description: str = ""
    ) -> Path:
        """Register output file with checksum.

        Args:
            filepath: Path to output file.
            description: Human-readable description of the file.

        Returns:
            The input filepath for chaining.
        """
        checksum = self.compute_checksum(filepath)
        relative_path = str(
            filepath.relative_to(self.output_dir)
            if filepath.is_relative_to(self.output_dir)
            else filepath.name
        )
        self.checksums[relative_path] = {
            "checksum": checksum,
            "algorithm": "sha256",
            "description": description,
            "size_bytes": filepath.stat().st_size,
            "created": datetime.now().isoformat(),
        }
        return filepath

    def save_checksums(self) -> Path:
        """Save checksums manifest for reproducibility.

        Returns:
            Path to the checksums.json file.
        """
        manifest_path = self.output_dir / "checksums.json"
        manifest = {
            "run_id": self.run_id,
            "created": datetime.now().isoformat(),
            "files": self.checksums,
        }
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        return manifest_path

    def create_latest_symlink(self) -> Optional[Path]:
        """Create/update 'latest' symlink to current output.

        Returns:
            Path to the 'latest' symlink, or None on failure.

        Note:
            On Windows, may require Administrator privileges.
        """
        latest_path = self.base_path / "latest"
        try:
            if latest_path.is_symlink() or latest_path.exists():
                latest_path.unlink()
            latest_path.symlink_to(self.output_dir)
            return latest_path
        except (OSError, NotImplementedError) as e:
            # Symlinks may not be supported or require elevated privileges
            return None


# Usage example
if __name__ == "__main__":
    manager = OutputManager(Path("results/financial"))
    output_dir = manager.create_output_dir()

    # Save some output
    output_file = output_dir / "variables.parquet"
    # df.to_parquet(output_file)  # Your actual save operation

    # Register with checksum
    manager.register_output(output_file, "Financial variables dataset")
    manager.save_checksums()
    manager.create_latest_symlink()
```

### Directory Structure

```
results/
├── 2024-01-15_143022/              # Timestamped run directory
│   ├── output.parquet               # Output file
│   ├── summary.yaml                 # Run summary
│   └── checksums.json               # Integrity manifest
├── 2024-01-16_091530/              # Another run
│   └── ...
└── latest -> 2024-01-16_091530/    # Symlink to most recent
```

### Checksum Manifest Format

```json
// checksums.json
{
  "run_id": "2024-01-15_143022",
  "created": "2024-01-15T14:30:22.123456",
  "files": {
    "output.parquet": {
      "checksum": "a1b2c3d4e5f6...",
      "algorithm": "sha256",
      "description": "Financial variables dataset",
      "size_bytes": 12345678,
      "created": "2024-01-15T14:30:45.654321"
    }
  }
}
```

### Integration with Configuration

```python
# Combine OutputManager with ProjectConfig
from pathlib import Path
from f1d.shared.config import ProjectConfig
from f1d.shared.output import OutputManager

# Load configuration
config = ProjectConfig.from_yaml(Path("config/project.yaml"))

# Create output manager
base_output = Path(config.paths.outputs)
manager = OutputManager(base_output / "financial")

# Create output directory
output_dir = manager.create_output_dir()

# Save configuration snapshot
config_snapshot = output_dir / "config.yaml"
with open(config_snapshot, "w") as f:
    yaml.dump(config.model_dump(), f)
manager.register_output(config_snapshot, "Configuration snapshot")
```

### Rationale

#### Why Timestamped Directories?

1. **Version history:** Each run preserves its outputs
2. **Auditability:** Know exactly when each output was created
3. **Rollback:** Can reference previous outputs if needed
4. **Parallel runs:** Multiple runs don't overwrite each other

#### Why Checksums?

1. **Integrity verification:** Detect file corruption
2. **Reproducibility checks:** Compare outputs across runs
3. **Cache invalidation:** Know when outputs change
4. **Audit trails:** Prove outputs haven't been modified

---

## 5. Logging Pattern (CONF-05)

This section defines structured logging using structlog for machine-parseable logs.

### Structured Logging with structlog

```python
# src/f1d/shared/logging.py
"""Structured logging configuration using structlog.

This module provides structured logging with JSON output support,
context binding, and multiple output formats.

Example:
    >>> from f1d.shared.logging import configure_logging, get_logger
    >>> configure_logging(log_level="INFO", json_output=False)
    >>> logger = get_logger(__name__)
    >>> logger.info("processing_started", rows=1000, stage="financial")
"""

import logging
import sys
from pathlib import Path
from typing import Any, Optional
import structlog


def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    json_output: bool = False
) -> None:
    """Configure structlog with optional file output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path for log file output.
        json_output: If True, use JSON format; otherwise human-readable.
    """
    # Shared processors for all loggers
    shared_processors: list[Any] = [
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
        # Human-readable console format with colors
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
    root_logger.handlers.clear()  # Remove existing handlers
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Optional file handler (always JSON for files)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                foreign_pre_chain=shared_processors,
                processors=[structlog.processors.JSONRenderer()],
            )
        )
        root_logger.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name, typically __name__.

    Returns:
        Bound logger instance.
    """
    return structlog.get_logger(name)


# Usage with context binding
logger = get_logger(__name__)

def process_data(df: Any, stage: str) -> Any:
    """Process data with context-aware logging.

    Args:
        df: DataFrame to process.
        stage: Processing stage name.

    Returns:
        Processed DataFrame.
    """
    log = logger.bind(
        stage=stage,
        gvkey_count=len(df["gvkey"].unique()) if hasattr(df, 'gvkey') else 0,
    )

    log.info("processing_started", rows=len(df))

    # ... processing logic ...

    log.info("processing_completed", rows_output=len(df))
    return df
```

### Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| DEBUG | Detailed diagnostic information | Variable values, loop iterations |
| INFO | General operational messages | Stage start/end, row counts |
| WARNING | Unexpected but handled situations | Missing data, fallback used |
| ERROR | Serious problems, operation failed | API failure, data corruption |
| CRITICAL | System-wide failures | Database connection lost |

### Configuration via YAML

```yaml
# config/logging.yaml
version: 1
disable_existing_loggers: false

formatters:
  json:
    class: structlog.stdlib.ProcessorFormatter
    processors:
      - structlog.processors.JSONRenderer

  console:
    class: structlog.stdlib.ProcessorFormatter
    processors:
      - structlog.dev.ConsoleRenderer

handlers:
  console:
    class: logging.StreamHandler
    formatter: console
    stream: ext://sys.stdout

  file:
    class: logging.FileHandler
    formatter: json
    filename: logs/pipeline.log

root:
  level: INFO
  handlers: [console, file]
```

### Context Binding Pattern

```python
# Bind context for correlated logging
from f1d.shared.logging import get_logger

logger = get_logger(__name__)

def run_pipeline(config):
    """Run pipeline with correlation context."""
    # Bind pipeline-wide context
    log = logger.bind(
        pipeline_id=config.run_id,
        version=config.version,
    )

    log.info("pipeline_started")

    # Each stage can add its own context
    stage_log = log.bind(stage="financial")
    stage_log.info("stage_started")

    # ... processing ...

    stage_log.info("stage_completed", duration_seconds=45.2)
    log.info("pipeline_completed")
```

### Console vs File Output

**Console (Human-readable):**
```
2024-01-15 14:30:22 [info     ] processing_started           rows=1000 stage=financial
2024-01-15 14:30:45 [info     ] processing_completed         rows_output=995 stage=financial
```

**File (JSON for parsing):**
```json
{"event": "processing_started", "rows": 1000, "stage": "financial", "level": "info", "timestamp": "2024-01-15T14:30:22Z"}
{"event": "processing_completed", "rows_output": 995, "stage": "financial", "level": "info", "timestamp": "2024-01-15T14:30:45Z"}
```

### Integration with Output Directories

```python
# Save logs to run-specific directory
from f1d.shared.output import OutputManager
from f1d.shared.logging import configure_logging

manager = OutputManager(Path("results/financial"))
output_dir = manager.create_output_dir()

# Configure logging to output directory
log_file = output_dir / "pipeline.log"
configure_logging(
    log_level="DEBUG",
    log_file=log_file,
    json_output=True,  # JSON for machine parsing
)

# Register log file with checksums
manager.register_output(log_file, "Pipeline execution log")
```

### Never Log Sensitive Data

```python
# BAD: Logging secrets
logger.info("connected", password=config.db_password)  # NO!

# GOOD: SecretStr prevents this
env = EnvConfig()
logger.info("connected", username=env.wrds_username)  # OK
# env.wrds_password is SecretStr - safe to pass but won't expose value

# GOOD: Log non-sensitive indicators
logger.info("configuration_loaded", has_password=bool(env.wrds_password))
```

### Rationale

#### Why structlog?

1. **Structured output:** JSON logs for machine parsing
2. **Context binding:** Correlate related log messages
3. **Multiple outputs:** Console (colored) + file (JSON)
4. **Performance:** Efficient event-based logging
5. **Standard library compatible:** Works with logging module

**Source:** [structlog Documentation](https://www.structlog.org/en/stable/logging-best-practices.html)

---

## 6. Test Structure (TEST-01)

This section defines the test directory structure and test type taxonomy.

### Test Directory Structure

```
tests/
├── __init__.py                   # Package marker
├── conftest.py                   # Root-level shared fixtures
│
├── fixtures/                     # Test data files
│   ├── sample_data/              # Sample parquet/csv files
│   │   ├── sample_panel.parquet
│   │   └── sample_transcripts.parquet
│   └── baseline_checksums.json   # For regression tests
│
├── factories/                    # Test data factories
│   ├── __init__.py
│   ├── dataframe_factory.py      # DataFrame generation utilities
│   └── config_factory.py         # Configuration generation utilities
│
├── unit/                         # Fast, isolated tests
│   ├── __init__.py
│   ├── conftest.py               # Unit-test-specific fixtures
│   ├── test_path_utils.py        # Tests for path_utils module
│   ├── test_panel_ols.py         # Tests for panel_ols module
│   └── test_config.py            # Tests for configuration loading
│
├── integration/                  # Module interaction tests
│   ├── __init__.py
│   ├── conftest.py               # Integration-test-specific fixtures
│   ├── test_pipeline.py          # End-to-end stage tests
│   └── test_financial_econometric.py  # Cross-module tests
│
├── regression/                   # Output stability tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_outputs.py           # Compare against baselines
│
├── e2e/                          # End-to-end pipeline tests
│   ├── __init__.py
│   └── test_full_pipeline.py     # Complete pipeline execution
│
└── performance/                  # Performance benchmarks
    ├── __init__.py
    ├── conftest.py               # Performance-specific fixtures
    └── test_memory.py            # Memory usage tests
```

### Test Type Definitions

| Type | Purpose | Speed | Dependencies | When to Use |
|------|---------|-------|--------------|-------------|
| **Unit** | Single function/method | Fast (< 1s) | Mocked | Testing individual logic |
| **Integration** | Multiple modules | Medium (1-30s) | Real | Testing interactions |
| **Regression** | Output comparison | Medium | Baselines | Preventing regressions |
| **E2E** | Full pipeline | Slow (min+) | Full stack | Smoke testing |
| **Performance** | Benchmarks | Varies | Full stack | Performance monitoring |

### Test Type Details

#### Unit Tests

**Purpose:** Test individual functions in isolation

**Characteristics:**
- Fast execution (< 1 second each)
- All external dependencies mocked
- Test single function or method
- No file I/O or network calls

**Example:**
```python
# tests/unit/test_path_utils.py
"""Unit tests for path utilities module."""

import pytest
from pathlib import Path
from unittest.mock import patch

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
```

#### Integration Tests

**Purpose:** Test interactions between modules

**Characteristics:**
- Medium execution time (1-30 seconds)
- Real dependencies (no mocks)
- Test data flow between modules
- May use temporary databases/files

**Example:**
```python
# tests/integration/test_financial_econometric.py
"""Integration tests for financial to econometric pipeline."""

import pytest
from pathlib import Path
import pandas as pd

from f1d.financial.v1.variables import construct_variables
from f1d.econometric.v1.regressions import run_panel_ols


class TestFinancialToEconometric:
    """Tests for financial-to-econometric integration."""

    @pytest.fixture
    def sample_data(self, test_data_dir: Path) -> pd.DataFrame:
        """Load sample data for integration test."""
        return pd.read_parquet(test_data_dir / "sample_panel.parquet")

    def test_financial_to_regression_pipeline(self, sample_data):
        """Test that financial variables can be used in regressions."""
        # Construct financial variables
        with_vars = construct_variables(sample_data)

        # Run regression
        result = run_panel_ols(
            with_vars,
            formula="investment ~ uncertainty + size + mtb",
            entity_effects=True,
            time_effects=True,
        )

        # Verify regression ran successfully
        assert result.rsquared > 0
        assert "uncertainty" in result.params.index
```

#### Regression Tests

**Purpose:** Ensure outputs remain stable across changes

**Characteristics:**
- Compare outputs against baselines
- Detect unintended changes
- Use checksum comparison
- Alert on drift

**Example:**
```python
# tests/regression/test_outputs.py
"""Regression tests for output stability."""

import pytest
import hashlib
from pathlib import Path
import pandas as pd


class TestOutputRegression:
    """Tests for output stability."""

    @pytest.fixture
    def baseline_checksums(self, test_data_dir: Path) -> dict:
        """Load baseline checksums."""
        import json
        with open(test_data_dir / "baseline_checksums.json") as f:
            return json.load(f)

    def test_financial_variables_output_stability(
        self,
        sample_panel_data,
        baseline_checksums
    ):
        """Test that financial variables output is stable."""
        from f1d.financial.v1.variables import construct_variables

        # Generate output
        result = construct_variables(sample_panel_data)

        # Compute checksum
        checksum = hashlib.sha256(
            pd.util.hash_pandas_object(result, index=True).values
        ).hexdigest()

        # Compare with baseline
        expected = baseline_checksums["financial_variables"]
        assert checksum == expected, (
            f"Output checksum changed: {checksum[:8]}... != {expected[:8]}..."
        )
```

#### E2E Tests

**Purpose:** Test complete pipeline execution

**Characteristics:**
- Slow execution (minutes)
- Full stack test
- Minimal mocking
- Run in CI for releases

**Example:**
```python
# tests/e2e/test_full_pipeline.py
"""End-to-end pipeline tests."""

import pytest
from pathlib import Path
import pandas as pd


@pytest.mark.e2e
class TestFullPipeline:
    """Tests for complete pipeline execution."""

    @pytest.fixture
    def sample_inputs(self, test_data_dir: Path) -> dict:
        """Load all sample inputs."""
        return {
            "transcripts": pd.read_parquet(
                test_data_dir / "sample_transcripts.parquet"
            ),
            "compustat": pd.read_parquet(
                test_data_dir / "sample_compustat.parquet"
            ),
        }

    @pytest.mark.slow
    def test_full_pipeline_produces_outputs(self, sample_inputs, tmp_path):
        """Test that full pipeline produces expected outputs."""
        from f1d.sample.build_manifest import build_manifest
        from f1d.text.uncertainty import compute_uncertainty
        from f1d.financial.v1.variables import construct_variables
        from f1d.econometric.v1.regressions import run_panel_ols

        # Stage 1: Build manifest
        manifest = build_manifest(
            sample_inputs["transcripts"],
            output_dir=tmp_path / "stage1"
        )
        assert len(manifest) > 0

        # Stage 2: Compute uncertainty
        uncertainty = compute_uncertainty(
            manifest,
            output_dir=tmp_path / "stage2"
        )
        assert "uncertainty" in uncertainty.columns

        # Stage 3: Construct variables
        variables = construct_variables(
            sample_inputs["compustat"],
            output_dir=tmp_path / "stage3"
        )
        assert len(variables) > 0

        # Stage 4: Run regression
        results = run_panel_ols(
            variables,
            formula="investment ~ uncertainty + controls",
        )
        assert results.rsquared > 0
```

#### Performance Tests

**Purpose:** Monitor and benchmark performance

**Characteristics:**
- Measure execution time
- Track memory usage
- Set performance thresholds
- Run periodically, not on every commit

**Example:**
```python
# tests/performance/test_memory.py
"""Performance tests for memory usage."""

import pytest
import pandas as pd
import numpy as np


@pytest.mark.performance
class TestMemoryUsage:
    """Tests for memory performance."""

    def test_large_dataframe_memory_usage(self):
        """Test memory usage with large DataFrame."""
        import tracemalloc

        tracemalloc.start()

        # Create large DataFrame
        df = pd.DataFrame({
            f"col_{i}": np.random.randn(1_000_000)
            for i in range(50)
        })

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Assert peak memory is reasonable (< 500MB for this test)
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 500, f"Peak memory too high: {peak_mb:.1f}MB"
```

### Running Specific Test Types

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run only regression tests
pytest tests/regression/

# Run only e2e tests (slow)
pytest tests/e2e/ -m e2e

# Run only performance tests
pytest tests/performance/ -m performance

# Skip slow tests
pytest -m "not slow"
```

---

## 7. Coverage Targets (TEST-02)

This section defines tier-based coverage targets aligned with ARCHITECTURE_STANDARD.md module tiers.

### Tier-Based Coverage Targets

| Module Tier | Location | Target Coverage | Rationale |
|-------------|----------|-----------------|-----------|
| **Tier 1** (Core Shared) | `src/f1d/shared/` | 90% minimum | Critical utilities, widely used |
| **Tier 2** (Stage-Specific) | `src/f1d/{stage}/` | 80% minimum | Important but localized |
| **Tier 3** (Scripts) | `scripts/` | No requirement | Advisory only, exploratory |
| **Overall Project** | All | 70% minimum | Baseline quality gate |

### pyproject.toml Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
branch = true
source = ["src/f1d"]
omit = [
    "tests/*",
    "*/__pycache__/*",
    "*/site-packages/*",
]

[tool.coverage.report]
fail_under = 70
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
show_missing = true
skip_covered = true

[tool.coverage.html]
directory = "htmlcov"

[tool.pytest.ini_options]
addopts = "--cov=f1d --cov-report=term-missing --cov-report=html"
testpaths = ["tests"]
```

### Coverage Quality vs Quantity

**Coverage theater to avoid:**
- Tests with no assertions
- Tests that pass when code is broken
- Testing trivial getters/setters
- 100% coverage with no behavior verification

**Good coverage practices:**
- Test behavior, not implementation
- Cover edge cases and error paths
- Test business logic thoroughly
- Use branch coverage, not just line coverage

### Coverage Commands

```bash
# Run tests with coverage
pytest --cov=f1d --cov-report=term-missing

# Run with HTML report
pytest --cov=f1d --cov-report=html
open htmlcov/index.html

# Run with coverage for specific module
pytest --cov=f1d.shared tests/unit/test_path_utils.py

# Check coverage threshold (fails if < 70%)
pytest --cov=f1d --cov-fail-under=70

# Generate coverage badge
coverage-badge -o coverage.svg -f
```

### Tier-Specific Coverage Enforcement

For CI/CD enforcement of tier-specific targets:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests with coverage
        run: pytest --cov=f1d --cov-report=xml

      - name: Check overall coverage
        run: |
          coverage report --fail-under=70

      - name: Check Tier 1 coverage
        run: |
          coverage report --include="src/f1d/shared/*" --fail-under=90

      - name: Check Tier 2 coverage
        run: |
          coverage report --include="src/f1d/financial/*,src/f1d/econometric/*" --fail-under=80
```

### Coverage Reports

**Terminal output:**
```
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
src/f1d/__init__.py                           5      0   100%
src/f1d/shared/__init__.py                    3      0   100%
src/f1d/shared/path_utils.py                 45      2    96%   23-24
src/f1d/shared/panel_ols.py                  78      8    90%   45-52
-----------------------------------------------------------------------
TOTAL                                       131     10    92%
```

**HTML report:** Interactive report showing covered/uncovered lines with syntax highlighting.

### Rationale

#### Why Tier-Based Coverage?

1. **Risk-based:** Higher coverage where risk is higher
2. **Practical:** 100% everywhere is unrealistic
3. **Focused:** Effort directed at critical code
4. **Measurable:** Clear targets for each tier

#### Why 70% Overall?

1. **Achievable:** Realistic for research code
2. **Meaningful:** Catches major issues
3. **Standard:** Common industry baseline
4. **Improvable:** Can increase over time

**Source:** [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

---

## 8. Test Naming Convention (TEST-03)

This section defines the standard naming convention for test functions.

### Standard Pattern

**Pattern:** `test_<module>_<function>_<scenario>`

### Good Examples

```python
# tests/unit/test_panel_ols.py
"""Tests for panel_ols module."""

import pytest
import pandas as pd
import numpy as np

from f1d.shared.panel_ols import run_panel_ols, CollinearityError


class TestRunPanelOls:
    """Tests for run_panel_ols function."""

    def test_run_panel_ols_valid_input_returns_results(self, sample_panel_data):
        """Test that valid input returns regression results."""
        result = run_panel_ols(
            sample_panel_data,
            formula="dependent ~ independent",
            entity_effects=True,
        )

        assert result is not None
        assert hasattr(result, 'params')
        assert hasattr(result, 'rsquared')

    def test_run_panel_ols_missing_columns_raises_error(self, sample_panel_data):
        """Test that missing required columns raises ValueError."""
        # Remove required column
        data = sample_panel_data.drop(columns=['dependent'])

        with pytest.raises(ValueError, match="missing.*column"):
            run_panel_ols(
                data,
                formula="dependent ~ independent",
            )

    def test_run_panel_ols_multicollinearity_raises_collinearity_error(self, collinear_data):
        """Test that perfect multicollinearity raises CollinearityError."""
        with pytest.raises(CollinearityError):
            run_panel_ols(
                collinear_data,
                formula="y ~ x1 + x2",  # x1 and x2 are perfectly collinear
            )

    def test_run_panel_ols_thin_cells_logs_warning(self, thin_cell_data, caplog):
        """Test that thin industry-year cells trigger warning."""
        with caplog.at_level(logging.WARNING):
            run_panel_ols(
                thin_cell_data,
                formula="y ~ x",
            )

        assert "thin cells" in caplog.text.lower()

    def test_run_panel_ols_with_fixed_effects_returns_correct_dof(self, sample_panel_data):
        """Test that fixed effects correctly adjust degrees of freedom."""
        result = run_panel_ols(
            sample_panel_data,
            formula="dependent ~ independent",
            entity_effects=True,
            time_effects=True,
        )

        # Degrees of freedom should account for fixed effects
        n_entities = sample_panel_data['gvkey'].nunique()
        n_years = sample_panel_data['year'].nunique()
        expected_dof = n_entities + n_years - 2  # -2 for entity + time FE

        assert result.df_model == expected_dof

    def test_run_panel_ols_clustered_standard_errors_valid(self, sample_panel_data):
        """Test that clustered standard errors are computed correctly."""
        result = run_panel_ols(
            sample_panel_data,
            formula="dependent ~ independent",
            cluster_by='gvkey',
        )

        # Clustered SE should be larger than non-clustered
        assert result.std_errors_clustered is not None
```

### Anti-Patterns to Avoid

```python
# BAD: Too vague
def test_regression():
    """What regression? What scenario?"""
    pass

# BAD: What error?
def test_error():
    """What kind of error? Under what conditions?"""
    pass

# BAD: Numeric, no meaning
def test_1():
    """What does test_1 test?"""
    pass

# BAD: Too generic
def test_function():
    """Which function? What scenario?"""
    pass

# BAD: Implementation detail
def test_returns_pandas_dataframe():
    """Tests implementation, not behavior."""
    pass

# BAD: Multiple scenarios
def test_errors_and_warnings():
    """Tests multiple things - split into separate tests."""
    pass
```

### Naming Pattern Breakdown

| Component | Description | Example |
|-----------|-------------|---------|
| `test_` | Prefix for pytest discovery | `test_` |
| `<module>` | Module or class being tested | `panel_ols` |
| `<function>` | Function or method being tested | `run_panel_ols` |
| `<scenario>` | Specific test scenario | `valid_input_returns_results` |

### Scenario Naming Guidelines

| Scenario Type | Naming Pattern | Example |
|---------------|----------------|---------|
| Happy path | `valid_<input>_returns_<expected>` | `valid_input_returns_results` |
| Validation error | `invalid_<input>_raises_<error>` | `missing_columns_raises_error` |
| Edge case | `<edge_case>_<behavior>` | `empty_dataframe_returns_empty` |
| Warning | `<condition>_logs_warning` | `thin_cells_logs_warning` |
| Configuration | `with_<config>_<behavior>` | `with_fixed_effects_correct_dof` |

### Class-Based Test Organization

For related tests, organize into classes:

```python
class TestValidateOutputPath:
    """Tests for validate_output_path function."""

    def test_validate_output_path_existing_dir_returns_path(self):
        """Test existing directory case."""
        pass

    def test_validate_output_path_nonexistent_raises_error(self):
        """Test nonexistent directory case."""
        pass

    def test_validate_output_path_file_raises_error(self):
        """Test file instead of directory case."""
        pass


class TestEnsureOutputDir:
    """Tests for ensure_output_dir function."""

    def test_ensure_output_dir_creates_missing(self):
        """Test directory creation."""
        pass

    def test_ensure_output_dir_existing_returns_path(self):
        """Test existing directory handling."""
        pass
```

### Benefits of Descriptive Names

1. **Self-documenting:** Name describes what's being tested
2. **Failure messages:** Clear what failed from name alone
3. **Searchable:** Easy to find tests for specific scenarios
4. **Review-friendly:** Reviewers understand test purpose quickly

---

## 9. Fixture Organization (TEST-04)

This section defines the hierarchical conftest.py pattern with factory fixtures.

### Hierarchical conftest.py Pattern

```
tests/
├── conftest.py               # Root-level fixtures (session scope)
├── fixtures/                 # Test data files
├── factories/                # Test data factories
│
├── unit/
│   └── conftest.py           # Unit-test-specific fixtures
│
├── integration/
│   └── conftest.py           # Integration-test-specific fixtures
│
├── regression/
│   └── conftest.py           # Regression-test-specific fixtures
│
└── e2e/
    └── conftest.py           # E2E-test-specific fixtures
```

### Root conftest.py

```python
# tests/conftest.py
"""Root-level pytest configuration and shared fixtures.

This module defines fixtures shared across all test types.
Session-scoped fixtures for expensive setup are defined here.
"""

import pytest
from pathlib import Path
import pandas as pd
import numpy as np


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Path to repository root directory.

    Returns:
        Path to the repository root.
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(repo_root: Path) -> Path:
    """Path to test fixtures directory.

    Args:
        repo_root: Repository root path fixture.

    Returns:
        Path to tests/fixtures directory.
    """
    return repo_root / "tests" / "fixtures"


@pytest.fixture(scope="session")
def sample_dataframe_factory():
    """Factory fixture for creating sample DataFrames.

    Returns:
        Factory function for DataFrame generation.

    Example:
        >>> df = sample_dataframe_factory(n_rows=100, seed=42)
    """
    def _create(
        n_rows: int = 100,
        columns: dict | None = None,
        seed: int = 42
    ) -> pd.DataFrame:
        """Create a sample DataFrame.

        Args:
            n_rows: Number of rows to generate.
            columns: Column definitions. If None, uses defaults.
            seed: Random seed for reproducibility.

        Returns:
            Generated DataFrame.
        """
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
    """Sample panel data for regression tests.

    Args:
        sample_dataframe_factory: Factory for creating DataFrames.

    Returns:
        DataFrame with panel structure (10 firms, 5 years).
    """
    return sample_dataframe_factory(
        n_rows=50,
        columns={
            "gvkey": [f"{i//5:06d}" for i in range(50)],  # 10 firms
            "year": [2000 + (i % 5) for i in range(50)],   # 5 years
            "dependent": np.random.randn(50),
            "independent": np.random.randn(50),
        }
    )


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Temporary output directory for tests.

    Args:
        tmp_path: pytest's built-in temporary path fixture.

    Returns:
        Path to temporary output directory.
    """
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir
```

### Unit Test conftest.py

```python
# tests/unit/conftest.py
"""Unit test fixtures.

Provides fast, isolated fixtures for unit testing.
All external dependencies should be mocked here.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_config(tmp_path: Path):
    """Create temporary config file for unit tests.

    Args:
        tmp_path: pytest's temporary path fixture.

    Returns:
        Path to test config file.
    """
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text("""
project:
  name: TestProject
  version: "1.0.0"
data:
  year_start: 2002
  year_end: 2005
logging:
  level: DEBUG
determinism:
  random_seed: 42
""")
    return config_path


@pytest.fixture
def mock_panel_ols_result():
    """Mock result from run_panel_ols.

    Returns:
        MagicMock configured as panel OLS result.
    """
    result = MagicMock()
    result.params = pd.Series({"intercept": 0.5, "x": 1.2})
    result.rsquared = 0.45
    result.pvalues = pd.Series({"intercept": 0.1, "x": 0.01})
    return result


@pytest.fixture
def mock_logger():
    """Mock logger for testing logging calls.

    Returns:
        MagicMock configured as logger.
    """
    with patch("f1d.shared.logging.get_logger") as mock:
        logger = MagicMock()
        mock.return_value = logger
        yield logger
```

### Integration Test conftest.py

```python
# tests/integration/conftest.py
"""Integration test fixtures.

Provides fixtures for testing module interactions.
Uses real dependencies where practical.
"""

import pytest
from pathlib import Path
import pandas as pd
import os


@pytest.fixture(scope="module")
def subprocess_env(repo_root: Path) -> dict:
    """Environment for subprocess integration tests.

    Args:
        repo_root: Repository root path fixture.

    Returns:
        Environment dictionary for subprocess calls.
    """
    return {
        "PYTHONPATH": str(repo_root / "src"),
        **os.environ,
    }


@pytest.fixture(scope="module")
def sample_compustat_data(test_data_dir: Path) -> pd.DataFrame:
    """Load sample Compustat data for integration tests.

    Args:
        test_data_dir: Path to test fixtures directory.

    Returns:
        DataFrame with Compustat-like data.
    """
    return pd.read_parquet(test_data_dir / "sample_data" / "sample_compustat.parquet")


@pytest.fixture(scope="module")
def sample_transcripts_data(test_data_dir: Path) -> pd.DataFrame:
    """Load sample transcripts data for integration tests.

    Args:
        test_data_dir: Path to test fixtures directory.

    Returns:
        DataFrame with transcript data.
    """
    return pd.read_parquet(test_data_dir / "sample_data" / "sample_transcripts.parquet")
```

### Factory Fixtures over Fixture Pyramids

**Avoid fixture pyramids (deep nesting):**

```python
# BAD: Deep fixture nesting
@pytest.fixture
def fixture_a():
    return "a"

@pytest.fixture
def fixture_b(fixture_a):
    return f"{fixture_a}_b"

@pytest.fixture
def fixture_c(fixture_b):
    return f"{fixture_b}_c"

@pytest.fixture
def fixture_d(fixture_c):
    return f"{fixture_c}_d"  # Hard to understand dependencies
```

**Use factory fixtures instead:**

```python
# GOOD: Factory fixture pattern
@pytest.fixture
def data_factory():
    """Factory for creating test data with customizable parameters."""
    def _create(
        n_firms: int = 10,
        n_years: int = 5,
        with_missing: bool = False,
        seed: int = 42,
    ) -> pd.DataFrame:
        np.random.seed(seed)
        rows = n_firms * n_years
        data = {
            "gvkey": [f"{i//n_years:06d}" for i in range(rows)],
            "year": [2000 + (i % n_years) for i in range(rows)],
            "value": np.random.randn(rows),
        }
        if with_missing:
            data["value"][0:5] = np.nan
        return pd.DataFrame(data)
    return _create


# Usage in tests
def test_with_defaults(data_factory):
    df = data_factory()
    assert len(df) == 50  # 10 firms * 5 years

def test_with_custom_params(data_factory):
    df = data_factory(n_firms=20, n_years=10)
    assert len(df) == 200

def test_with_missing_data(data_factory):
    df = data_factory(with_missing=True)
    assert df["value"].isna().sum() == 5
```

### Fixture Scope Guidelines

| Scope | When to Use | Example |
|-------|-------------|---------|
| `session` | Expensive setup, read-only data | Database connections, large files |
| `module` | Per-module setup | Test data files |
| `class` | Per-class setup | Shared test state |
| `function` | Default, per-test isolation | Temporary directories |

### fixtures/ Directory Organization

```
tests/fixtures/
├── sample_data/
│   ├── sample_panel.parquet        # Small panel dataset
│   ├── sample_compustat.parquet    # Compustat-like data
│   ├── sample_transcripts.parquet  # Transcript excerpts
│   └── sample_crsp.parquet         # CRSP-like returns
│
├── expected_outputs/
│   ├── financial_variables.parquet # Expected output for regression
│   └── regression_results.json     # Expected regression results
│
└── baseline_checksums.json         # Checksums for regression tests
```

### factories/ Directory Organization

```
tests/factories/
├── __init__.py
├── dataframe_factory.py            # DataFrame generation utilities
│
│   def create_panel_data(...)
│   def create_compustat_data(...)
│   def create_transcript_data(...)
│
└── config_factory.py               # Configuration generation utilities
    def create_test_config(...)
    def create_env_config(...)
```

### Rationale

#### Why Hierarchical conftest.py?

1. **Scope control:** Fixtures available only where needed
2. **Avoid pollution:** Test types don't share unrelated fixtures
3. **Clear organization:** Know where to find fixtures
4. **Performance:** Expensive fixtures only loaded when needed

#### Why Factory Fixtures?

1. **Flexibility:** Customize data per test
2. **Reusability:** One factory, many variations
3. **Readability:** Parameters show test intent
4. **Maintainability:** Single source of truth for data creation

**Source:** [pytest Fixtures Documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html)

---

## 10. Mocking and Test Data Patterns (TEST-05)

This section defines mocking patterns using pytest-mock and test data best practices.

### pytest-mock Integration

pytest-mock provides the `mocker` fixture for clean mock management:

```python
# tests/unit/test_financial_utils.py
"""Tests for financial utilities with mocking examples."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock


class TestConstructVariables:
    """Tests for construct_variables function."""

    @pytest.fixture
    def mock_compustat_data(self, sample_dataframe_factory):
        """Factory-generated Compustat-like data.

        Args:
            sample_dataframe_factory: Factory for creating DataFrames.

        Returns:
            DataFrame with Compustat-like structure.
        """
        return sample_dataframe_factory(
            n_rows=100,
            columns={
                "gvkey": [f"{i:06d}" for i in range(100)],
                "fyear": [2000] * 100,
                "at": [1000.0 + i * 10 for i in range(100)],  # Assets
                "che": [100.0 + i for i in range(100)],        # Cash
                "revt": [500.0 + i * 5 for i in range(100)],   # Revenue
            }
        )

    def test_construct_variables_computes_cash_ratio(self, mock_compustat_data):
        """Test that cash-to-assets ratio is computed correctly."""
        from f1d.financial.v1.variables import construct_variables

        result = construct_variables(mock_compustat_data)

        assert "cash_ratio" in result.columns
        assert result["cash_ratio"].iloc[0] == pytest.approx(0.1, rel=0.01)

    @patch("f1d.financial.variables.load_compustat")
    def test_construct_variables_handles_missing_data(
        self,
        mock_load,
        mock_compustat_data
    ):
        """Test handling of missing Compustat data."""
        mock_load.return_value = mock_compustat_data

        # Test with missing values
        mock_compustat_data.loc[0:5, "at"] = pd.NA

        from f1d.financial.v1.variables import construct_variables
        result = construct_variables(mock_compustat_data)

        assert result["cash_ratio"].isna().sum() == 5  # Missing for NA assets

    def test_construct_variables_with_mocker(self, mocker, mock_compustat_data):
        """Test using pytest-mock's mocker fixture."""
        # mocker provides automatic cleanup
        mock_logger = mocker.patch("f1d.financial.variables.logger")

        from f1d.financial.v1.variables import construct_variables
        construct_variables(mock_compustat_data)

        # Verify logger was called
        mock_logger.info.assert_called()
```

### Mock Object Patterns

#### Use pytest-mock for Auto-Cleanup

```python
# GOOD: pytest-mock fixture (auto-cleanup)
def test_with_mocker(mocker):
    """mocker fixture automatically cleans up after test."""
    mock = mocker.patch("some.module.function")
    # Test code here
    # Mock automatically restored after test


# ACCEPTABLE: unittest.mock.patch context manager
def test_with_context_manager():
    """Context manager provides explicit scope."""
    with patch("some.module.function") as mock:
        # Test code here
        pass
    # Mock restored when exiting context


# AVOID: unittest.mock.patch decorator (no auto-cleanup on failure)
@patch("some.module.function")
def test_with_decorator(mock_func):
    """Decorator style - less flexible."""
    pass
```

#### Mock External Dependencies

```python
# Mock external APIs
def test_wrds_connection_with_mock(mocker):
    """Test WRDS connection handling."""
    mock_connect = mocker.patch("wrds.Connection")
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    # Test code that uses WRDS
    from f1d.data.wrds import get_compustat_data
    result = get_compustat_data()

    mock_connect.assert_called_once()
    mock_conn.get_table.assert_called_once()


# Mock file system
def test_file_writing_with_mock(mocker, tmp_path):
    """Test file writing without actual I/O."""
    # Use tmp_path for actual file tests, or mock for unit tests
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    from f1d.shared.io_utils import save_results
    save_results({"data": "value"}, "output.json")

    mock_open.assert_called_once_with("output.json", "w")
```

#### Don't Mock What You Own

```python
# BAD: Mocking internal business logic
def test_with_internal_mock(mocker):
    """This mocks the code you're trying to test."""
    mock_calculate = mocker.patch("f1d.financial.variables.calculate_ratio")
    mock_calculate.return_value = 0.5

    # This test doesn't actually test calculate_ratio!
    from f1d.financial.v1.variables import construct_variables
    result = construct_variables(data)


# GOOD: Test real implementation, mock external dependencies
def test_with_external_mock(mocker):
    """Mock external dependencies, test real business logic."""
    # Mock external API
    mocker.patch("f1d.external.api.fetch_data", return_value=sample_data)

    # Test actual business logic
    from f1d.financial.v1.variables import construct_variables
    result = construct_variables(data)

    # Verify business logic works correctly
    assert result["cash_ratio"].mean() > 0
```

### Test Data Patterns

#### Factory Fixtures for Generated Data

```python
# tests/factories/dataframe_factory.py
"""Factory functions for test data generation."""

import pandas as pd
import numpy as np
from typing import Optional


def create_panel_data(
    n_firms: int = 10,
    n_years: int = 5,
    seed: int = 42,
    with_uncertainty: bool = True,
    with_financial: bool = True,
) -> pd.DataFrame:
    """Create balanced panel data for testing.

    Args:
        n_firms: Number of firms (GVKEYs).
        n_years: Number of years per firm.
        seed: Random seed for reproducibility.
        with_uncertainty: Include uncertainty measures.
        with_financial: Include financial variables.

    Returns:
        DataFrame with panel structure.
    """
    np.random.seed(seed)
    rows = n_firms * n_years

    data = {
        "gvkey": [f"{i//n_years:06d}" for i in range(rows)],
        "year": [2000 + (i % n_years) for i in range(rows)],
        "fyear": [2000 + (i % n_years) for i in range(rows)],  # Fiscal year
    }

    if with_uncertainty:
        data.update({
            "uncertainty": np.random.uniform(0, 1, rows),
            "uncertainty_lm": np.random.uniform(0, 1, rows),
        })

    if with_financial:
        data.update({
            "at": np.random.uniform(100, 10000, rows),  # Assets
            "che": np.random.uniform(10, 1000, rows),   # Cash
            "revt": np.random.uniform(50, 5000, rows),  # Revenue
            "investment": np.random.uniform(0, 0.5, rows),
        })

    return pd.DataFrame(data)


def create_compustat_data(
    n_obs: int = 1000,
    seed: int = 42,
    with_missing: bool = False,
) -> pd.DataFrame:
    """Create Compustat-like data for testing.

    Args:
        n_obs: Number of observations.
        seed: Random seed for reproducibility.
        with_missing: Include missing values.

    Returns:
        DataFrame with Compustat structure.
    """
    np.random.seed(seed)

    data = {
        "gvkey": [f"{np.random.randint(1, 500):06d}" for _ in range(n_obs)],
        "fyear": np.random.randint(2000, 2020, n_obs),
        "at": np.random.uniform(100, 10000, n_obs),
        "che": np.random.uniform(10, 1000, n_obs),
        "revt": np.random.uniform(50, 5000, n_obs),
        "ni": np.random.uniform(-100, 500, n_obs),
        "dvt": np.random.uniform(0, 100, n_obs),
    }

    df = pd.DataFrame(data)

    if with_missing:
        # Add 5% missing values
        for col in ["at", "che", "revt", "ni"]:
            mask = np.random.random(n_obs) < 0.05
            df.loc[mask, col] = np.nan

    return df
```

#### fixtures/ Directory for Static Test Files

```
tests/fixtures/
├── sample_data/
│   ├── sample_panel_10firms_5years.parquet   # Small test dataset
│   ├── sample_transcripts_100.parquet        # 100 sample transcripts
│   └── sample_compustat_1000.parquet         # 1000 sample observations
│
├── expected_outputs/
│   ├── financial_variables_expected.parquet  # Expected output for regression
│   └── uncertainty_scores_expected.parquet
│
└── baseline_checksums.json                   # For regression test validation
```

#### Deterministic Data with Seed Control

```python
# Always use explicit seeds for reproducibility
def test_reproducible_random_data():
    """Test that random data is reproducible with seed."""
    np.random.seed(42)
    data1 = np.random.randn(100)

    np.random.seed(42)
    data2 = np.random.randn(100)

    np.testing.assert_array_equal(data1, data2)
```

### Anti-Patterns to Avoid

#### Shared Mutable State in Fixtures

```python
# BAD: Shared mutable state
@pytest.fixture
def shared_data():
    return {"value": 0}  # Mutable!

def test_1(shared_data):
    shared_data["value"] = 1  # Modifies shared state

def test_2(shared_data):
    assert shared_data["value"] == 0  # Fails if test_1 ran first!
```

```python
# GOOD: Immutable or fresh data per test
@pytest.fixture
def fresh_data():
    return {"value": 0}  # New dict each time

def test_1(fresh_data):
    fresh_data["value"] = 1  # Only affects this test's copy

def test_2(fresh_data):
    assert fresh_data["value"] == 0  # Always passes
```

#### Magic Numbers in Tests

```python
# BAD: Magic numbers
def test_regression():
    result = calculate_ratio(100, 50)
    assert result == 0.5  # What do these numbers mean?


# GOOD: Named constants with meaning
def test_regression():
    TOTAL_ASSETS = 100.0
    CASH_HOLDINGS = 50.0
    EXPECTED_CASH_RATIO = 0.5

    result = calculate_cash_ratio(TOTAL_ASSETS, CASH_HOLDINGS)
    assert result == EXPECTED_CASH_RATIO
```

#### Unparametrized Similar Tests

```python
# BAD: Copy-paste tests with minor variations
def test_with_valid_input():
    result = process("valid")
    assert result.success

def test_with_invalid_input():
    result = process("invalid")
    assert not result.success

def test_with_empty_input():
    result = process("")
    assert not result.success


# GOOD: Parametrized test
@pytest.mark.parametrize("input_value,expected_success", [
    ("valid", True),
    ("invalid", False),
    ("", False),
])
def test_process_various_inputs(input_value, expected_success):
    result = process(input_value)
    assert result.success == expected_success
```

---

## Appendix A: Quick Reference Card

### Configuration Loading

```python
from f1d.shared.config import ProjectConfig

# Load configuration
config = ProjectConfig.from_yaml(Path("config/project.yaml"))

# Access values
year_start = config.data.year_start
log_level = config.logging.level

# Override via environment
# export F1D_DATA__YEAR_START=2005
```

### Environment Variables

```python
from f1d.shared.env import EnvConfig

# Load environment config
env = EnvConfig()

# Access secrets safely
if env.wrds_password:
    password = env.get_wrds_password()  # Only when needed
```

### Output Management

```python
from f1d.shared.output import OutputManager

# Create output directory
manager = OutputManager(Path("results/financial"))
output_dir = manager.create_output_dir()

# Register outputs with checksums
manager.register_output(output_file, "Financial variables")
manager.save_checksums()
```

### Structured Logging

```python
from f1d.shared.logging import configure_logging, get_logger

# Configure logging
configure_logging(log_level="INFO", json_output=False)

# Use with context
logger = get_logger(__name__)
log = logger.bind(stage="financial")
log.info("processing_started", rows=1000)
```

### Test Coverage Targets

| Tier | Location | Target |
|------|----------|--------|
| Tier 1 | `src/f1d/shared/` | 90% |
| Tier 2 | `src/f1d/{stage}/` | 80% |
| Overall | All | 70% |

### Test Naming Pattern

```
test_<module>_<function>_<scenario>
```

Examples:
- `test_run_panel_ols_valid_input_returns_results`
- `test_validate_path_nonexistent_raises_error`

---

## Appendix B: Related Standards

### ARCHITECTURE_STANDARD.md

**Cross-references:**
- Section 1 (ARCH-01): Folder structure for config/ and tests/
- Section 2 (ARCH-02): Module tier system for coverage targets
- Section 3 (ARCH-03): Data directory structure
- Appendix A: Migration guide (sys.path.insert elimination)

**Key alignment:**
- config/ directory defined in ARCH-01
- tests/ structure mirrors src/ (ARCH-01)
- Module tiers (Tier 1, 2, 3) inform coverage targets

### CODE_QUALITY_STANDARD.md

**Cross-references:**
- Section 1 (NAM-01 to NAM-05): Naming conventions for test functions
- Section 2 (CODE-01): Docstring standards for configuration classes
- Section 3 (CODE-02): Type hint requirements for configuration models
- Section 5 (CODE-05): Error handling in configuration loading

**Key alignment:**
- Test naming follows `test_<module>_<function>_<scenario>` pattern
- Configuration classes use Google-style docstrings
- Type hints required for all configuration models

### SCRIPT_DOCSTANDARD.md

**Cross-references:**
- Script header documentation for configuration usage
- Output file documentation requirements

---

## Appendix C: Anti-Patterns Summary

### Configuration Anti-Patterns

| Anti-Pattern | Issue | Solution |
|--------------|-------|----------|
| `sys.path.insert` | Import fragility (20+ files) | src-layout with pip install -e |
| Raw dict config | No validation, no type safety | pydantic-settings models |
| Secrets in YAML | Exposed in logs and git | SecretStr + .env files |
| Hardcoded paths | Not portable | Configuration + Path objects |
| Configuration sprawl | Multiple overlapping configs | Single project.yaml |

### Testing Anti-Patterns

| Anti-Pattern | Issue | Solution |
|--------------|-------|----------|
| Fixture pyramids | Deep nesting, hard to debug | Factory fixtures |
| Coverage theater | High %, no behavior testing | Focus on edge cases |
| Shared mutable state | Test order dependency | Fresh data per test |
| Magic numbers | Unexplained values | Named constants |
| Unparametrized similar tests | Code duplication | @pytest.mark.parametrize |
| Mocking what you own | Doesn't test real code | Mock external only |

### Logging Anti-Patterns

| Anti-Pattern | Issue | Solution |
|--------------|-------|----------|
| Logging secrets | Security exposure | SecretStr protection |
| print() statements | No structure, hard to parse | structlog |
| Unstructured messages | Hard to query | JSON format + context binding |
| Missing context | Can't correlate logs | logger.bind() for context |

---

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [structlog Documentation](https://www.structlog.org/en/stable/logging-best-practices.html)
- [pytest Documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [PyPA src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Five Advanced Pytest Fixture Patterns](https://www.inspiredpython.com/article/five-advanced-pytest-fixture-patterns)

---

*Last updated: 2026-02-13*
*Version: 5.0*
*Status: DEFINITION - Implementation deferred to v6.0+*

