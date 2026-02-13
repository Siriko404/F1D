# Phase 68: Documentation & Tooling Standard - Research

**Researched:** 2026-02-13
**Domain:** Python documentation standards, CI/CD tooling, project configuration
**Confidence:** HIGH

## Summary

This phase defines documentation standards and CI/CD tooling configuration for the F1D pipeline. The research covers: (1) README structure with badges and quickstart sections, (2) Keep a Changelog format for CHANGELOG.md, (3) CONTRIBUTING guide structure with setup/workflow/standards, (4) MkDocs with mkdocstrings for API documentation (aligned with Google-style docstrings from CODE_QUALITY_STANDARD.md), (5) Code comment standards, (6) pyproject.toml structure (build system, dependencies, tool configs), (7) pre-commit hooks configuration (ruff, mypy, trailing-whitespace, end-of-file-fixer), (8) GitHub Actions workflow structure (test matrix, coverage, linting), (9) .gitignore patterns (Python, data, IDE, OS-specific), and (10) linting/formatting configuration (ruff rules, mypy strictness levels).

**Primary recommendation:** Create a unified DOC_TOOLING_STANDARD.md that integrates with existing ARCHITECTURE_STANDARD.md, CODE_QUALITY_STANDARD.md, and CONFIG_TESTING_STANDARD.md, using MkDocs Material with mkdocstrings for API docs, pre-commit hooks for code quality gates, and GitHub Actions for CI/CD.

## User Constraints (from Project Context)

No CONTEXT.md exists for this phase. This is a definition-only milestone where Claude has discretion on approach.

**Locked Decisions (from STATE.md):**
- [v5.0 Scope] Definition-only milestone - implementation deferred to v6.0+
- [65-01] Adopt src-layout over flat layout (PyPA recommendation)
- [65-01] Both V1 and V2 are active pipeline variants
- [65-01] Module tier system with quality bars (Tier 1-3)
- [66-01] Google-style docstrings for function/method documentation
- [66-01] Tier-based type hint coverage (100% Tier 1, 80% Tier 2, optional Tier 3)
- [66-01] PEP 760 compliance - no bare except clauses
- [66-01] Absolute imports over relative imports
- [67-01] pydantic-settings for type-safe configuration
- [67-01] structlog for structured JSON logging
- [67-01] Tier-based coverage targets (90% Tier 1, 80% Tier 2, 70% overall)

**Claude's Discretion:**
- README section structure and badge choices
- CHANGELOG format specifics
- CONTRIBUTING guide content
- API documentation tool choice (MkDocs vs Sphinx)
- Code comment philosophy
- pyproject.toml organization
- pre-commit hook selection
- GitHub Actions workflow design
- .gitignore pattern selection
- ruff rule selection and mypy strictness levels

**Deferred Ideas (OUT OF SCOPE):**
- Implementation of standards (deferred to v6.0+)
- Actual documentation writing
- CI/CD pipeline execution
- Publishing to PyPI

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| MkDocs | 1.6+ | Static documentation generator | Fast, Python-native, Markdown-based |
| mkdocs-material | 9.0+ | Material theme for MkDocs | Beautiful, responsive, feature-rich |
| mkdocstrings | 0.27+ | API documentation from docstrings | Google-style docstring support |
| mkdocstrings-python | 1.10+ | Python handler for mkdocstrings | Native Google-style default |
| pre-commit | 3.8+ | Git pre-commit hook framework | Industry standard, multi-language |
| ruff | 0.9+ | Linter and formatter | Replaces flake8, black, isort |
| mypy | 1.14+ | Static type checker | De facto Python type checker |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8.0+ | Testing framework | Already in use |
| pytest-cov | 5.0+ | Coverage reporting | CI pipelines |
| GitHub Actions | N/A | CI/CD platform | All automation |
| codecov | N/A | Coverage visualization | PR status checks |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| MkDocs | Sphinx | Sphinx has more features but steeper learning curve; MkDocs is simpler for Python |
| mkdocstrings | Sphinx autodoc | autodoc requires RST; mkdocstrings uses Markdown |
| pre-commit | husky (npm) | husky is JS-centric; pre-commit is Python-native |
| ruff | flake8 + black + isort | ruff is 100x faster and consolidates 3 tools |
| GitHub Actions | GitLab CI | Project uses GitHub; Actions has better integration |

**Installation:**
```bash
# Already in project - maintain existing versions
pip install mkdocs>=1.6 mkdocs-material>=9.0 mkdocstrings>=0.27 mkdocstrings-python>=1.10
pip install pre-commit>=3.8 ruff>=0.9 mypy>=1.14

# Initialize pre-commit
pre-commit install
```

## Architecture Patterns

### Recommended Documentation Structure

```
docs/
├── index.md                 # Landing page (redirect to README)
├── getting-started.md       # Quick start guide
├── user-guide/              # End-user documentation
│   ├── installation.md
│   ├── configuration.md
│   └── pipeline-flow.md
├── api/                     # Auto-generated API docs
│   ├── shared/
│   │   ├── panel_ols.md     # ::: f1d.shared.panel_ols
│   │   └── financial_utils.md
│   └── modules/
└── standards/               # Architecture standards
    ├── ARCHITECTURE_STANDARD.md
    ├── CODE_QUALITY_STANDARD.md
    ├── CONFIG_TESTING_STANDARD.md
    └── DOC_TOOLING_STANDARD.md

mkdocs.yml                   # MkDocs configuration
```

### Pattern 1: README Structure

**What:** Standard README sections with badges for project metadata
**When to use:** All Python projects for portfolio-ready presentation

**Required Sections:**
1. Title and description
2. Badges (build status, coverage, version, license)
3. Quick start / Installation
4. Usage examples
5. Documentation link
6. Contributing link
7. License

**Example:**
```markdown
# F1D Data Processing Pipeline

[![Tests](https://github.com/user/f1d/actions/workflows/test.yml/badge.svg)](https://github.com/user/f1d/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/user/f1d/branch/main/graph/badge.svg)](https://codecov.io/gh/user/f1d)
[![Python](https://img.shields.io/pypi/pyversions/f1d.svg)](https://pypi.org/project/f1d/)
[![License](https://img.shields.io/github/license/user/f1d.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)

Research data processing pipeline for F1D thesis. Processes earnings call transcripts,
constructs text-based measures, and runs econometric analyses.

## Quick Start

\`\`\`bash
pip install -r requirements.txt
python 2_Scripts/1_Sample/1.1_CleanMetadata.py
\`\`\`

## Documentation

Full documentation available at [docs/](docs/) or [ReadTheDocs](https://f1d.readthedocs.io/).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

This project is for academic research. See [LICENSE](LICENSE) for details.
```

**Source:** [Make a README](https://www.makeareadme.com/), [Daily.dev Badges Best Practices](https://daily.dev/blog/readme-badges-github-best-practices)

### Pattern 2: Keep a Changelog Format

**What:** Standardized changelog format with semantic versioning
**When to use:** All releases to track notable changes

**Guiding Principles:**
- Changelogs are for humans, not machines
- Every version has an entry
- Similar changes are grouped
- Versions and sections are linkable
- Latest version comes first
- Release date displayed (YYYY-MM-DD format)
- Mention Semantic Versioning

**Change Types:**
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` for vulnerability fixes

**Example:**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Placeholder for upcoming features

## [5.0.0] - 2026-02-13

### Added
- DOC-01 through DOC-05: Documentation standards
- TOOL-01 through TOOL-05: Tooling configuration standards
- Unified DOC_TOOLING_STANDARD.md document

### Changed
- Architecture standards now include CI/CD configuration

### Deprecated
- Old .pre-commit-config.yaml format (use new standard)

## [4.0.0] - 2026-02-12

### Added
- Folder structure consolidation (Phase 64)
- Single V2 variant for all active development
```

**Source:** [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)

### Pattern 3: CONTRIBUTING Guide Structure

**What:** Comprehensive contributor documentation
**When to use:** Open source or team projects

**Required Sections:**
1. Code of Conduct (if applicable)
2. How to contribute (PR process)
3. Development setup
4. Coding standards (reference to CODE_QUALITY_STANDARD.md)
5. Testing requirements
6. Commit message format

**Example Structure:**
```markdown
# Contributing to F1D

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Install dev dependencies: `pip install -r requirements-dev.txt`
5. Install pre-commit hooks: `pre-commit install`

## Coding Standards

This project follows the standards defined in:
- [CODE_QUALITY_STANDARD.md](docs/CODE_QUALITY_STANDARD.md) - Naming conventions, docstrings, type hints
- [CONFIG_TESTING_STANDARD.md](docs/CONFIG_TESTING_STANDARD.md) - Testing patterns, coverage targets

Key requirements:
- Google-style docstrings for all public functions
- Type hints required for Tier 1 modules (90%+ coverage)
- Pre-commit hooks must pass before committing

## Testing

Run tests with: `pytest tests/ -m "not e2e"`

Coverage requirements:
- Tier 1 modules: 90%+
- Tier 2 modules: 80%+
- Overall: 70%+

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/description`
2. Make changes and ensure tests pass
3. Run pre-commit: `pre-commit run --all-files`
4. Submit PR with description linking to any issues
5. Wait for CI checks to pass
```

### Pattern 4: MkDocs Configuration for API Docs

**What:** MkDocs with mkdocstrings for automatic API documentation from Google-style docstrings
**When to use:** All Python projects needing API documentation

**mkdocs.yml:**
```yaml
site_name: F1D Data Processing Pipeline
site_description: Research data processing pipeline for F1D thesis
site_url: https://f1d.readthedocs.io/
repo_url: https://github.com/user/f1d
repo_name: user/f1d

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.sections
    - navigation.expand
    - content.code.copy
    - content.code.annotate

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - User Guide:
      - Installation: user-guide/installation.md
      - Configuration: user-guide/configuration.md
      - Pipeline Flow: user-guide/pipeline-flow.md
  - API Reference:
      - Shared Modules:
          - Panel OLS: api/shared/panel_ols.md
          - Financial Utils: api/shared/financial_utils.md
  - Standards:
      - Architecture: standards/ARCHITECTURE_STANDARD.md
      - Code Quality: standards/CODE_QUALITY_STANDARD.md
      - Configuration: standards/CONFIG_TESTING_STANDARD.md
      - Documentation: standards/DOC_TOOLING_STANDARD.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            docstring_section_style: table
            show_source: true
            show_root_heading: true
            merge_init_into_class: true
            show_docstring_attributes: true
            show_docstring_parameters: true
            show_docstring_returns: true
            show_docstring_raises: true
            show_docstring_examples: true

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - admonition
  - pymdownx.details
  - toc:
      permalink: true
```

**API Doc Page Example (api/shared/panel_ols.md):**
```markdown
# Panel OLS Module

::: f1d.shared.panel_ols
    options:
      show_root_heading: true
      show_source: true
```

**Source:** [mkdocstrings-python Documentation](https://mkdocstrings.github.io/python/usage/configuration/docstrings/)

### Pattern 5: pyproject.toml Complete Structure

**What:** Comprehensive pyproject.toml with build system, dependencies, and all tool configurations
**When to use:** Modern Python packaging (PEP 621)

**Example:**
```toml
# Build system configuration
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

# Project metadata (PEP 621)
[project]
name = "f1d"
version = "6.0.0"
description = "F1D Data Processing Pipeline for thesis research"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
authors = [
    {name = "Author Name", email = "author@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "structlog>=25.0",
    "scipy>=1.10.0",
    "statsmodels>=0.14.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-mock>=3.12",
    "ruff>=0.9.0",
    "mypy>=1.14",
    "pre-commit>=3.8",
    "mkdocs>=1.6",
    "mkdocs-material>=9.0",
    "mkdocstrings>=0.27",
    "mkdocstrings-python>=1.10",
]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.0",
    "mkdocstrings>=0.27",
    "mkdocstrings-python>=1.10",
]

[project.urls]
Homepage = "https://github.com/user/f1d"
Documentation = "https://f1d.readthedocs.io/"
Repository = "https://github.com/user/f1d.git"

# Setuptools configuration for src-layout
[tool.setuptools.packages.find]
where = ["src"]

# pytest configuration
[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "--import-mode=importlib",
]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "regression: marks tests as regression tests",
    "unit: marks tests as unit tests",
    "e2e: marks tests as end-to-end pipeline tests",
    "performance: marks tests as performance regression tests",
]

# coverage configuration
[tool.coverage.run]
source = ["src/f1d"]
branch = true
omit = [
    "*/tests/*",
    "*/__pycache__/*",
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
    "@abstractmethod",
]
precision = 2
show_missing = true

# ruff configuration
[tool.ruff]
line-length = 88
indent-width = 4
target-version = "py39"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
]
ignore = [
    "E501",   # line too long (handled by formatter)
    "B008",   # do not perform function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]
"tests/**" = ["S101", "ARG"]

[tool.ruff.lint.isort]
known-first-party = ["f1d"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

# mypy configuration
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
check_untyped_defs = true
strict_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
show_error_codes = true
namespace_packages = true
explicit_package_bases = true

# Per-module strictness (tier-based)
[[tool.mypy.overrides]]
module = "f1d.shared.panel_ols"
disallow_untyped_defs = true
strict = true

[[tool.mypy.overrides]]
module = "f1d.shared.financial_utils"
disallow_untyped_defs = true
strict = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

**Source:** [PyPA pyproject.toml Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), [Real Python pyproject.toml](https://realpython.com/python-pyproject-toml/)

### Pattern 6: pre-commit Hooks Configuration

**What:** Comprehensive pre-commit configuration for code quality gates
**When to use:** All Python projects for automated quality checks

**.pre-commit-config.yaml:**
```yaml
# Pre-commit hooks configuration
# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks

repos:
  # General file quality
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        args: [--unsafe]
      - id: check-toml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: detect-private-key
      - id: debug-statements

  # Ruff - linter and formatter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      # Linter
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      # Formatter
      - id: ruff-format

  # Type checking with mypy
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic>=2.0
          - types-PyYAML
        args: [--config-file=pyproject.toml]
        pass_filenames: false
        entry: mypy src/f1d

  # Security checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.10
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]

# CI configuration
ci:
  autofix_commit_msg: |
    [pre-commit.ci] auto fixes from pre-commit.com hooks

    for more information, see https://pre-commit.ci
  autofix_prs: true
  autoupdate_branch: ''
  autoupdate_commit_msg: '[pre-commit.ci] pre-commit autoupdate'
  autoupdate_schedule: weekly
  skip: []
  submodules: false
```

**Source:** [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks), [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)

### Pattern 7: GitHub Actions Workflow Structure

**What:** Comprehensive CI workflow with test matrix, coverage, and linting
**When to use:** All Python projects for continuous integration

**.github/workflows/test.yml:**
```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

permissions:
  contents: read

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff mypy

      - name: Run Ruff (linting)
        run: ruff check --output-format=github

      - name: Run Ruff (formatting check)
        run: ruff format --diff

      - name: Run mypy
        run: mypy src/f1d --config-file pyproject.toml

  test:
    name: Test (Python ${{ matrix.python-version }}, ${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    needs: lint
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']

    steps:
      - uses: actions/checkout@v5

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest tests/ \
            -m "not e2e" \
            --cov=src/f1d \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=70 \
            -v

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
          token: ${{ secrets.CODECOV_TOKEN }}

      - name: Upload coverage artifact
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.python-version }}
          path: |
            coverage.xml
            htmlcov/
          retention-days: 30

  e2e-test:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v5

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest

      - name: Run E2E tests
        run: pytest tests/ -m e2e -v --timeout=1200
```

**Source:** [GitHub Actions Python Guide](https://docs.github.com/actions/guides/building-and-testing-python)

### Pattern 8: .gitignore Patterns

**What:** Comprehensive gitignore for Python data science projects
**When to use:** All Python projects with data files

**.gitignore:**
```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
junit/

# Translations
*.mo
*.pot

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# ruff
.ruff_cache/

# Data files (project-specific)
1_Inputs/
4_Outputs/
3_Logs/
data/raw/
data/processed/
data/interim/
*.parquet
*.csv
*.xlsx
*.feather
*.h5
*.hdf5

# Archives and backups
___Archive/
.___archive/
BACKUP_*/
*.rar
*.zip
*.tar.gz

# OS-specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Secrets (never commit)
*.pem
*.key
credentials.json
secrets.yaml
.secrets/
```

### Anti-Patterns to Avoid

- **No badges in README:** Missing visual indicators of project health
- **Commit log as changelog:** Using git log instead of curated changes
- **No contributing guide:** Contributors don't know the process
- **Sphinx with RST:** Unnecessarily complex for Python projects
- **Manual CI without caching:** Slow feedback loops
- **Ignoring .env files:** Security risk if secrets are committed
- **Missing pyproject.toml [project] section:** Not following PEP 621
- **Inconsistent pre-commit hooks:** Not matching CI checks

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Changelog management | Manual version tracking | Keep a Changelog format | Standardized, parseable |
| API documentation | Custom doc parser | mkdocstrings | Handles Google-style, renders beautifully |
| Pre-commit hooks | Shell scripts | pre-commit framework | Cross-platform, language-agnostic |
| Linting | Multiple tools (flake8, isort, black) | ruff | 100x faster, consolidates tools |
| Type checking | Runtime type checking | mypy | Static analysis, catches errors early |
| CI/CD | Custom scripts | GitHub Actions | Declarative, marketplace actions |

**Key insight:** The Python ecosystem has mature, integrated tooling for documentation and CI/CD. Custom solutions add maintenance burden without benefits.

## Common Pitfalls

### Pitfall 1: Outdated pyproject.toml Structure

**What goes wrong:** Using setup.py or old pyproject.toml without [project] section

**Why it happens:** Legacy projects, outdated tutorials

**How to avoid:**
1. Use PEP 621 compliant [project] section
2. Consolidate all tool configs in pyproject.toml
3. Remove setup.py entirely (unless using dynamic metadata)

**Warning signs:**
- setup.py still present
- No [project] section in pyproject.toml
- Tool configs in separate files (pytest.ini, .flake8, etc.)

### Pitfall 2: Pre-commit and CI Mismatch

**What goes wrong:** Pre-commit passes but CI fails (or vice versa)

**Why it happens:** Different tool versions or configurations between local and CI

**How to avoid:**
1. Pin tool versions in both .pre-commit-config.yaml and CI
2. Use identical command arguments
3. Test pre-commit hooks locally before pushing

**Warning signs:**
- CI fails on formatting that passes locally
- Different ruff/mypy versions between environments

### Pitfall 3: Missing Type Stubs

**What goes wrong:** mypy reports errors for third-party libraries without stubs

**Why it happens:** Not all packages ship with type information

**How to avoid:**
1. Install types-* packages for common libraries
2. Use `ignore_missing_imports = true` for specific modules
3. Create custom stubs for critical dependencies

**Warning signs:**
- Many "Cannot find implementation or library stub" errors
- CI blocked by third-party type errors

### Pitfall 4: Badge Overload

**What goes wrong:** Too many badges clutter README, obscuring important information

**Why it happens:** Adding every possible status indicator

**How to avoid:**
1. Limit to 4-6 essential badges (build, coverage, version, license)
2. Group related badges together
3. Remove stale/irrelevant badges

**Warning signs:**
- More badges than README content visible above fold
- Badges with "unknown" or error states

### Pitfall 5: Inconsistent Code Comments

**What goes wrong:** Comments explain "what" instead of "why", or are outdated

**Why it happens:** No comment standard, comments not updated with code

**How to avoid:**
1. Document "why", not "what" (code should be self-documenting for "what")
2. Use docstrings for API documentation, comments for reasoning
3. Update or delete comments when code changes

**Warning signs:**
- Comments that contradict the code
- Obvious comments like `# increment counter`
- Long comment blocks explaining simple operations

## Code Examples

### Complete MkDocs API Documentation Page

```markdown
# Shared Modules

## Panel OLS

::: f1d.shared.panel_ols
    options:
      show_root_heading: true
      show_source: true
      docstring_style: google
      docstring_section_style: table
      members_order: source

## Financial Utilities

::: f1d.shared.financial_utils
    options:
      show_root_heading: true
      show_source: true
      docstring_style: google
      docstring_section_style: table
```

### Complete pre-commit Configuration for Data Science

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=50000']  # 50MB for data files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, types-PyYAML]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| setup.py | pyproject.toml with [project] | PEP 621 (2020) | Single file for all configuration |
| Sphinx + RST | MkDocs + Markdown | ~2020 | Simpler, faster documentation |
| flake8 + black + isort | ruff | 2023+ | 100x faster, single tool |
| Manual CI scripts | GitHub Actions | ~2020 | Declarative, marketplace ecosystem |
| Requirements files only | pyproject.toml dependencies | PEP 621 (2020) | Optional dependencies, groups |

**Deprecated/outdated:**
- `setup.py` only: Use pyproject.toml with [build-system]
- `pytest.ini`: Move to [tool.pytest.ini_options] in pyproject.toml
- `.flake8`: Move to [tool.ruff.lint] in pyproject.toml
- Separate config files: Consolidate into pyproject.toml

## Open Questions

1. **Should DOC_TOOLING_STANDARD.md be one document or separate DOC_STANDARD.md + TOOLING_STANDARD.md?**
   - What we know: Phase 68 requirements cover both documentation (DOC-01 to DOC-05) and tooling (TOOL-01 to TOOL-05)
   - What's unclear: Whether to create unified standard or separate documents
   - Recommendation: Create unified DOC_TOOLING_STANDARD.md for related infrastructure concerns, similar to how CONFIG_TESTING_STANDARD.md covers configuration and testing together

2. **Should we use ReadTheDocs or GitHub Pages for documentation hosting?**
   - What we know: Both support MkDocs; ReadTheDocs has automatic PR previews
   - What's unclear: Hosting preference for academic projects
   - Recommendation: Use ReadTheDocs for automatic PR previews and versioning support

3. **What ruff rule set should be the baseline?**
   - What we know: Current config uses E4, E7, E9, F, B, W, I
   - What's unclear: Whether to add more rules (UP, C4, SIM, ARG)
   - Recommendation: Start with conservative set, add rules incrementally based on codebase needs

## Sources

### Primary (HIGH confidence)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) - Changelog format specification
- [PyPA pyproject.toml Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - Official packaging guide
- [GitHub Actions Python Guide](https://docs.github.com/actions/guides/building-and-testing-python) - Official CI documentation
- [mkdocstrings-python Documentation](https://mkdocstrings.github.io/python/usage/configuration/docstrings/) - API documentation configuration
- [Ruff Configuration](https://docs.astral.sh/ruff/configuration/) - Linter/formatter configuration
- [mypy Configuration File](https://mypy.readthedocs.io/en/latest/config_file.html) - Type checker configuration

### Secondary (MEDIUM confidence)
- [Real Python pyproject.toml Guide](https://realpython.com/python-pyproject-toml/) - Comprehensive tutorial
- [Make a README](https://www.makeareadme.com/) - README best practices
- [Daily.dev README Badges](https://daily.dev/blog/readme-badges-github-best-practices) - Badge best practices
- [pre-commit-hooks Repository](https://github.com/pre-commit/pre-commit-hooks) - Standard hooks

### Tertiary (LOW confidence)
- None - all core findings verified with primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools are mature, well-documented, and widely adopted
- Architecture: HIGH - Patterns align with existing ARCHITECTURE_STANDARD.md and CODE_QUALITY_STANDARD.md
- Pitfalls: HIGH - Based on common issues in Python project setup
- Code examples: HIGH - Verified against official documentation

**Research date:** 2026-02-13
**Valid until:** 2027-02-13 (1 year - these are stable patterns)
