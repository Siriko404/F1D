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

