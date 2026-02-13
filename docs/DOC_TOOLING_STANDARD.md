# F1D Documentation and Tooling Standard

**Version:** 5.0
**Last Updated:** 2026-02-13
**Status:** DEFINITION - Implementation deferred to v6.0+
**Milestone:** v5.0 Architecture Standard Definition

---

## Purpose

This document defines the documentation standards and CI/CD tooling configuration for the F1D (Financial Text Analysis) data processing pipeline. It builds on the foundation established in ARCHITECTURE_STANDARD.md (folder structure, module organization), CODE_QUALITY_STANDARD.md (naming conventions, docstrings), and CONFIG_TESTING_STANDARD.md (configuration, testing) and ensures:

- **Portfolio-Ready Documentation:** Professional presentation for public repositories
- **Reproducible CI/CD Pipelines:** Automated quality gates that run identically locally and in CI
- **Consistent Contributor Experience:** Clear onboarding and contribution guidelines
- **Automated Quality Gates:** Pre-commit hooks and CI checks enforce standards automatically

This is a **DEFINITION document**. The standards described here represent the target documentation and tooling patterns that will be implemented in v6.0+. Current code may not fully comply with all standards.

---

## Document Structure

This standard is organized into 10 main sections:

**Documentation Requirements (DOC-01 to DOC-05):**
1. **README Structure (DOC-01):** Badges, description, quickstart, usage, license
2. **CHANGELOG Format (DOC-02):** Keep a Changelog specification
3. **CONTRIBUTING Guide (DOC-03):** Setup, workflow, standards, PR process
4. **API Documentation Approach (DOC-04):** MkDocs with mkdocstrings (Google-style)
5. **Code Comments Standard (DOC-05):** When and how to comment

**Tooling Requirements (TOOL-01 to TOOL-05):**
6. **pyproject.toml Structure (TOOL-01):** Build system, dependencies, tool configs
7. **Pre-commit Hooks Configuration (TOOL-02):** ruff, mypy, trailing-whitespace
8. **GitHub Actions Workflow (TOOL-03):** Test matrix, coverage, linting
9. **.gitignore Patterns (TOOL-04):** Python, data, IDE, OS-specific
10. **Linting/Formatting Configuration (TOOL-05):** ruff rules, mypy strictness

Additionally:
- **Appendix A:** Quick Reference Card
- **Appendix B:** Related Standards
- **Appendix C:** Anti-Patterns Summary
- **Appendix D:** Tool Version Matrix

---

## How to Use This Standard

### For New Development (v6.0+)

When creating new modules or scripts in v6.0+:
1. Follow the README structure (DOC-01) for new project documentation
2. Use the CHANGELOG format (DOC-02) for all version tracking
3. Update CONTRIBUTING guide (DOC-03) when adding new workflow requirements
4. Add API documentation (DOC-04) for all public functions
5. Use code comments (DOC-05) sparingly and purposefully
6. Configure pyproject.toml (TOOL-01) for any new dependencies
7. Ensure pre-commit hooks (TOOL-02) pass before committing
8. Verify GitHub Actions (TOOL-03) pass for all PRs
9. Update .gitignore (TOOL-04) for new file types
10. Follow linting rules (TOOL-05) with zero violations

### For Current Development (v5.0)

This is a **DEFINITION-only milestone**. Implementation is deferred to v6.0+:
- Use these standards as reference for understanding target patterns
- Do not modify existing code to comply - wait for v6.0 implementation
- Plan future work with these standards in mind
- Document deviations when implementing v6.0 migration

### For Code Review

When reviewing code in v6.0+:
1. Check README has required badges and sections
2. Verify CHANGELOG entries for user-facing changes
3. Ensure CONTRIBUTING guidelines are followed
4. Confirm API documentation is complete for public functions
5. Review comments for necessity and accuracy
6. Validate pyproject.toml changes are correct
7. Require pre-commit hooks to pass
8. Confirm CI passes all checks
9. Verify sensitive files are in .gitignore
10. Check linting/formatting compliance

---

## Design Principles

### Principle 1: Portfolio-Ready Documentation

**Goal:** Professional presentation suitable for public repositories and portfolio showcase.

**Rationale:** Documentation is the first impression for users, employers, and collaborators. Well-structured README, CHANGELOG, and CONTRIBUTING files signal project maturity.

**Application:**
- Use badges to show project health (build, coverage, version)
- Keep quickstart examples working and minimal
- Maintain consistent formatting across all documentation
- Provide clear installation and usage instructions

### Principle 2: Automation-First

**Goal:** Quality gates run automatically without manual intervention.

**Rationale:** Manual quality checks are forgotten, skipped, or inconsistent. Automation ensures standards are enforced consistently.

**Application:**
- Pre-commit hooks run on every commit
- CI pipelines run on every push and PR
- Linting failures block merges
- Coverage drops fail builds

### Principle 3: Contributor-Friendly

**Goal:** Clear onboarding path for new contributors.

**Rationale:** Complex contribution processes discourage participation. Clear guidelines reduce friction and increase quality contributions.

**Application:**
- Step-by-step setup instructions
- Explicit coding standards references
- Clear PR process with checklist
- Responsive feedback through CI checks

### Principle 4: Integration

**Goal:** Tools work together seamlessly, not in isolation.

**Rationale:** Fragmented tooling creates maintenance burden and inconsistent behavior. Integrated tooling provides predictable outcomes.

**Application:**
- Pre-commit hooks match CI configuration
- pyproject.toml consolidates all tool configs
- MkDocs uses docstrings from code
- Coverage integrates with PR status checks

---

## Relationship to Other Standards

This document is part of the v5.0 Architecture Standard Definition milestone:

| Standard | Scope | This Document Depends On |
|----------|-------|-------------------------|
| ARCHITECTURE_STANDARD.md | Folder structure, module tiers | N/A (foundation) |
| CODE_QUALITY_STANDARD.md | Naming, docstrings, type hints | ARCHITECTURE_STANDARD.md |
| CONFIG_TESTING_STANDARD.md | Configuration, testing | ARCHITECTURE_STANDARD.md, CODE_QUALITY_STANDARD.md |
| **DOC_TOOLING_STANDARD.md** | Documentation, CI/CD | All above standards |

**Key Cross-References:**
- DOC-04 (API Documentation) references Google-style docstrings from CODE_QUALITY_STANDARD.md
- TOOL-01 (pyproject.toml) references module tiers from ARCHITECTURE_STANDARD.md
- TOOL-05 (Linting/Formatting) references type hint coverage from CODE_QUALITY_STANDARD.md
- DOC-03 (CONTRIBUTING) references testing requirements from CONFIG_TESTING_STANDARD.md

---

## DOC-01: README Structure

### Requirement

All projects MUST have a README.md file at the repository root with the following structure:

1. **Title** - Clear, descriptive project name
2. **Badges** - 4-6 status indicators (build, coverage, version, license)
3. **Description** - 1-3 sentence project summary
4. **Quick Start** - Minimal installation and first-use instructions
5. **Usage** - Common use cases with code examples
6. **Documentation** - Link to full documentation
7. **Contributing** - Link to CONTRIBUTING.md
8. **License** - Link to LICENSE file

### Rationale

The README is the entry point for anyone discovering the project. A well-structured README:
- Quickly communicates what the project does
- Shows project health through badges
- Gets users running with minimal friction
- Directs contributors to proper channels

### Required Badges

Include these essential badges (4-6 maximum):

| Badge Type | Purpose | Example |
|------------|---------|---------|
| Build Status | CI/CD health | `[![Tests](https://github.com/user/repo/actions/workflows/test.yml/badge.svg)]` |
| Coverage | Test coverage | `[![Coverage](https://codecov.io/gh/user/repo/badge.svg)]` |
| Python Version | Supported versions | `[![Python](https://img.shields.io/pypi/pyversions/package.svg)]` |
| License | Legal status | `[![License](https://img.shields.io/github/license/user/repo.svg)]` |
| Code Style | Formatting tool | `[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)]` |

### Example README Template

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

```bash
# Clone the repository
git clone https://github.com/user/f1d.git
cd f1d

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the sample processing
python -m f1d.pipeline sample
```

## Usage

### Processing Raw Data

```python
from f1d.pipeline import DataPipeline

pipeline = DataPipeline(config_path="config/config.yaml")
pipeline.run_clean_metadata()
pipeline.run_construct_variables()
```

### Running Analysis

```python
from f1d.analysis import run_regression

results = run_regression(
    data_path="data/processed/analysis_dataset.parquet",
    model_spec="baseline"
)
```

## Documentation

Full documentation available at [docs/](docs/) or [ReadTheDocs](https://f1d.readthedocs.io/).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

This project is for academic research. See [LICENSE](LICENSE) for details.
```

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Too many badges | Clutters README, obscures content | Limit to 4-6 essential badges |
| Missing quickstart | Users can't get started quickly | Include minimal working example |
| Outdated examples | Commands fail, frustrating users | Test examples regularly |
| No badges | Missing visual health indicators | Add build and coverage badges |
| Vague description | Users don't understand purpose | Use specific, concrete language |

### Cross-References

- Badge URLs reference GitHub Actions workflow (TOOL-03)
- Installation commands reference pyproject.toml (TOOL-01)
- Usage examples reference API documentation (DOC-04)

---

## DOC-02: CHANGELOG Format

### Requirement

All projects MUST maintain a CHANGELOG.md file following the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format:

1. **Header** - Link to Keep a Changelog and Semantic Versioning specifications
2. **Unreleased Section** - Placeholder for upcoming changes at the top
3. **Version Sections** - Each release with version number and YYYY-MM-DD date
4. **Change Categories** - Grouped by: Added, Changed, Deprecated, Removed, Fixed, Security

### Rationale

A changelog serves as a curated, human-readable record of notable changes:
- Users can quickly understand what changed between versions
- Contributors see the impact of their work
- Maintainers track project evolution
- Automated tools can parse the format

### Required Sections

Each version entry MUST include:
- Version number (Semantic Versioning: MAJOR.MINOR.PATCH)
- Release date in YYYY-MM-DD format
- At least one change category with entries

**Change Categories:**

| Category | When to Use |
|----------|-------------|
| `Added` | New features, capabilities |
| `Changed` | Changes to existing functionality |
| `Deprecated` | Features to be removed in future |
| `Removed` | Features removed in this version |
| `Fixed` | Bug fixes |
| `Security` | Vulnerability fixes |

### Example CHANGELOG

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Placeholder for upcoming features

### Changed
- Placeholder for upcoming changes

## [6.0.0] - 2026-03-01

### Added
- DOC-01 through DOC-05: Documentation standards implementation
- TOOL-01 through TOOL-05: Tooling configuration implementation
- MkDocs site with API documentation
- Pre-commit hooks with ruff, mypy, bandit
- GitHub Actions CI/CD pipeline

### Changed
- Migrated from flat layout to src-layout (ARCHITECTURE_STANDARD.md)
- Consolidated all tool configs into pyproject.toml
- Updated all docstrings to Google-style format

### Deprecated
- Legacy V1 scripts will be removed in v7.0
- Old config format (YAML without pydantic validation)

### Fixed
- Sample size calculation bug in regression analysis
- Path resolution issues on Windows systems

### Security
- Added SecretStr for API keys in configuration

## [5.0.0] - 2026-02-13

### Added
- ARCHITECTURE_STANDARD.md with folder structure and module tiers
- CODE_QUALITY_STANDARD.md with naming and docstring standards
- CONFIG_TESTING_STANDARD.md with configuration and testing standards
- DOC_TOOLING_STANDARD.md with documentation and CI/CD standards

### Changed
- Folder structure consolidated (Phase 64)
- Single V2 variant for all active development

## [4.0.0] - 2026-02-12

### Added
- Initial v4.0 architecture standards definition

[Unreleased]: https://github.com/user/f1d/compare/v6.0.0...HEAD
[6.0.0]: https://github.com/user/f1d/compare/v5.0.0...v6.0.0
[5.0.0]: https://github.com/user/f1d/compare/v4.0.0...v5.0.0
[4.0.0]: https://github.com/user/f1d/releases/tag/v4.0.0
```

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Using git log as changelog | Not curated, includes trivial commits | Write human-readable summaries |
| Missing dates | Users can't correlate with releases | Always include YYYY-MM-DD date |
| No Unreleased section | Can't see upcoming changes | Keep Unreleased at top |
| Inconsistent categories | Hard to scan for specific change types | Use standard 6 categories |
| Missing version links | Can't compare versions | Add GitHub comparison links |

### Cross-References

- Version numbers reference pyproject.toml version (TOOL-01)
- Release process references GitHub Actions workflow (TOOL-03)
- Semantic Versioning aligns with dependency management

---

## DOC-03: CONTRIBUTING Guide

### Requirement

All projects MUST have a CONTRIBUTING.md file at the repository root with the following structure:

1. **Development Setup** - Step-by-step environment configuration
2. **Coding Standards** - Reference to CODE_QUALITY_STANDARD.md
3. **Testing Requirements** - Reference to CONFIG_TESTING_STANDARD.md
4. **Commit Message Format** - Conventional commits specification
5. **Pull Request Process** - Steps and checklist for PRs

### Rationale

A CONTRIBUTING guide:
- Reduces onboarding friction for new contributors
- Ensures consistent code quality
- Streamlines the review process
- Sets clear expectations

### Required Sections

#### Development Setup

Include exact commands for:
- Cloning and navigating to the project
- Creating virtual environment
- Installing dependencies (runtime and dev)
- Installing pre-commit hooks
- Running tests to verify setup

#### Coding Standards

Reference existing standards documents:
- CODE_QUALITY_STANDARD.md for naming, docstrings, type hints
- ARCHITECTURE_STANDARD.md for folder structure, module organization
- CONFIG_TESTING_STANDARD.md for testing patterns

#### Testing Requirements

Reference testing standards:
- Tier-based coverage targets (90% Tier 1, 80% Tier 2, 70% overall)
- Test categories (unit, integration, regression, e2e)
- How to run specific test types

#### Commit Message Format

Use Conventional Commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `refactor:` for code refactoring
- `test:` for test changes
- `chore:` for maintenance tasks

#### Pull Request Process

Define the PR workflow:
1. Create feature branch from main
2. Make changes with tests
3. Run pre-commit hooks locally
4. Push and create PR
5. Wait for CI checks
6. Address review feedback
7. Squash and merge

### Example CONTRIBUTING.md

```markdown
# Contributing to F1D

Thank you for your interest in contributing to F1D! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

### Setup Steps

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/f1d.git
   cd f1d
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Verify setup:**
   ```bash
   pytest tests/ -m "not e2e"
   ```

## Coding Standards

This project follows the standards defined in:

- [CODE_QUALITY_STANDARD.md](docs/CODE_QUALITY_STANDARD.md) - Naming conventions, docstrings, type hints
- [ARCHITECTURE_STANDARD.md](docs/ARCHITECTURE_STANDARD.md) - Folder structure, module organization
- [CONFIG_TESTING_STANDARD.md](docs/CONFIG_TESTING_STANDARD.md) - Testing patterns, coverage

### Key Requirements

- **Docstrings:** Google-style for all public functions (see CODE_QUALITY_STANDARD.md)
- **Type hints:** Required for Tier 1 modules (100% coverage), Tier 2 (80% coverage)
- **Imports:** Absolute imports only, no relative imports
- **Line length:** 88 characters (ruff default)

## Testing

### Running Tests

```bash
# Run all unit and integration tests
pytest tests/ -m "not e2e"

# Run only unit tests
pytest tests/ -m unit

# Run with coverage
pytest tests/ --cov=src/f1d --cov-report=term-missing

# Run E2E tests (requires data files)
pytest tests/ -m e2e
```

### Coverage Requirements

| Module Tier | Minimum Coverage |
|-------------|------------------|
| Tier 1 (Core) | 90% |
| Tier 2 (Processing) | 80% |
| Tier 3 (Scripts) | Optional |
| Overall | 70% |

## Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `refactor:` Code change without behavior change
- `test:` Test additions/modifications
- `chore:` Maintenance tasks

### Examples

```
feat(analysis): add rolling regression support

Add ability to run rolling window regressions for time-series analysis.
Includes configuration option for window size.

Closes #123
```

```
fix(pipeline): correct sample size calculation in bootstrap

The bootstrap sample size was incorrectly using population size
instead of sample size parameter.
```

## Pull Request Process

### Before Submitting

- [ ] Code follows coding standards
- [ ] All tests pass locally
- [ ] Pre-commit hooks pass
- [ ] New code has appropriate tests
- [ ] Coverage meets tier requirements
- [ ] Documentation updated if needed

### PR Steps

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with appropriate tests

3. Run pre-commit on all files:
   ```bash
   pre-commit run --all-files
   ```

4. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Wait for CI checks to pass

6. Address any review feedback

7. Once approved, a maintainer will squash and merge

### PR Title Format

Use the same format as commit messages:
```
feat(scope): brief description
```

## Questions?

Open an issue for bugs, feature requests, or questions.
```

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Missing setup commands | Contributors can't get started | Include exact, tested commands |
| No pre-commit instruction | Hooks not installed, CI fails | Make pre-commit install required |
| Outdated standards links | Contributors follow old rules | Link to standards, don't duplicate |
| Vague PR process | Contributors don't know workflow | Include step-by-step with checklist |
| No coverage requirements | Low-quality contributions | Reference tier-based targets |

### Cross-References

- Coding standards reference CODE_QUALITY_STANDARD.md
- Testing requirements reference CONFIG_TESTING_STANDARD.md
- Pre-commit hooks reference TOOL-02
- CI process references TOOL-03

---

## DOC-04: API Documentation Approach

### Requirement

All projects MUST use MkDocs with mkdocstrings for API documentation:

1. **MkDocs** - Static documentation generator
2. **mkdocs-material** - Material Design theme
3. **mkdocstrings** - Auto-generate docs from docstrings
4. **mkdocstrings-python** - Python handler (Google-style default)

### Rationale

MkDocs with mkdocstrings:
- Uses Markdown instead of RST (simpler than Sphinx)
- Auto-generates API docs from Google-style docstrings
- Provides beautiful, responsive documentation
- Integrates with ReadTheDocs for hosting
- No duplication between code and docs

### mkdocs.yml Configuration

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
    - navigation.indexes
    - content.code.copy
    - content.code.annotate
    - search.suggest
    - search.highlight

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
      - Pipeline Modules:
          - Data Processing: api/pipeline/processing.md
          - Analysis: api/pipeline/analysis.md
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
            members_order: source
            heading_level: 2

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
  - attr_list
  - md_in_html
```

### API Doc Page Pattern

Each API documentation page uses the mkdocstrings directive:

```markdown
# Panel OLS Module

Module for panel data ordinary least squares regression analysis.

::: f1d.shared.panel_ols
    options:
      show_root_heading: true
      show_source: true
      docstring_style: google
      docstring_section_style: table
      members_order: source
```

### Documentation Structure

```
docs/
├── index.md                 # Landing page
├── getting-started.md       # Quick start guide
├── user-guide/              # End-user documentation
│   ├── index.md
│   ├── installation.md
│   ├── configuration.md
│   └── pipeline-flow.md
├── api/                     # Auto-generated API docs
│   ├── index.md
│   ├── shared/
│   │   ├── index.md
│   │   ├── panel_ols.md     # ::: f1d.shared.panel_ols
│   │   └── financial_utils.md
│   └── pipeline/
│       ├── index.md
│       ├── processing.md
│       └── analysis.md
└── standards/               # Architecture standards
    ├── ARCHITECTURE_STANDARD.md
    ├── CODE_QUALITY_STANDARD.md
    ├── CONFIG_TESTING_STANDARD.md
    └── DOC_TOOLING_STANDARD.md

mkdocs.yml                   # MkDocs configuration
```

### Google-Style Docstrings

API documentation is generated from Google-style docstrings defined in CODE_QUALITY_STANDARD.md. Key elements:

```python
def calculate_panel_regression(
    data: pd.DataFrame,
    formula: str,
    entity_effects: bool = True,
    time_effects: bool = False,
) -> PanelRegressionResults:
    """Run panel regression with optional fixed effects.

    Executes a panel OLS regression using the specified formula and
    returns results including coefficients, standard errors, and
    diagnostic statistics.

    Args:
        data: Panel DataFrame with entity and time indices set.
        formula: Patsy-style formula string (e.g., 'y ~ x1 + x2').
        entity_effects: Include entity (firm) fixed effects.
            Defaults to True.
        time_effects: Include time (year) fixed effects.
            Defaults to False.

    Returns:
        PanelRegressionResults object containing:
            - coefficients: pd.Series of estimated coefficients
            - std_errors: pd.Series of standard errors
            - r_squared: float, within R-squared
            - n_obs: int, number of observations
            - n_entities: int, number of entities

    Raises:
        ValueError: If data does not have required MultiIndex.
        ValueError: If formula references columns not in data.

    Examples:
        >>> data = load_panel_data()
        >>> results = calculate_panel_regression(
        ...     data,
        ...     'investment ~ uncertainty + cash_flow',
        ...     entity_effects=True,
        ... )
        >>> print(results.r_squared)
        0.45

    Note:
        Uses linearmodels PanelOLS internally. For large datasets,
        consider setting cluster-robust standard errors.
    """
```

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Using Sphinx with RST | Steep learning curve, complex config | Use MkDocs with Markdown |
| Manual API documentation | Duplication, drift from code | Use mkdocstrings auto-generation |
| Missing docstrings | Empty API docs | Require docstrings per CODE_QUALITY_STANDARD.md |
| Wrong docstring style | mkdocstrings can't parse | Use Google-style consistently |
| No navigation structure | Hard to find documentation | Organize with nav sections in mkdocs.yml |

### Cross-References

- Google-style docstrings defined in CODE_QUALITY_STANDARD.md (CODE-01)
- Module organization follows ARCHITECTURE_STANDARD.md
- Configuration examples follow CONFIG_TESTING_STANDARD.md patterns

---

## DOC-05: Code Comments Standard

### Requirement

Comments MUST be used purposefully and sparingly:

1. **Document "why", not "what"** - Explain reasoning, not obvious operations
2. **Use docstrings for API documentation** - Comments are for reasoning
3. **Use TODO format** - `TODO(username): description`
4. **Update or delete with code changes** - No outdated comments

### Rationale

Good comments:
- Explain non-obvious decisions
- Document complex algorithms
- Provide context for workarounds
- Guide future maintainers

Bad comments:
- State the obvious
- Duplicate information in docstrings
- Become outdated and misleading
- Clutter the code

### When to Comment

**DO comment:**
- Complex algorithms that aren't self-explanatory
- Non-obvious business logic decisions
- Workarounds for external bugs or limitations
- Performance optimizations with trade-offs
- Links to relevant external resources (issues, papers)
- Warning about non-obvious side effects

**DO NOT comment:**
- Obvious operations (`# increment counter`)
- What the code does (use docstrings)
- Redundant explanations
- Commented-out code (delete it)

### Comment Format

```python
# GOOD: Explains why, references source
# Use winsorization at 1%/99% to handle outliers following
# methodology in Gul et al. (2010) Journal of Finance
data['measure'] = winsorize(data['measure'], limits=[0.01, 0.99])


# GOOD: Warns about non-obvious behavior
# Note: pandas.DataFrame.mean() silently ignores NaN values
# This is intentional for our use case but may cause issues
# if NaN handling changes
average = df.mean()


# GOOD: Documents workaround with link
# Workaround for pandas bug #12345 where groupby fails
# with categorical indices. Remove when fixed.
# https://github.com/pandas-dev/pandas/issues/12345
df = df.reset_index(drop=True)


# GOOD: TODO with owner
# TODO(username): Consider using numba for this loop
# Current implementation is O(n^2) which is slow for n > 10k


# BAD: States the obvious
# Set x to 5
x = 5


# BAD: Should be a docstring
# This function calculates the mean of a list
def calculate_mean(values):
    ...


# BAD: Outdated comment
# Use the old API endpoint (comment from v1.0, now wrong)
url = "https://api.example.com/v2/data"
```

### TODO Format

```python
# TODO(username): Single-line description
# TODO(username): Multi-line description that continues
#   on subsequent lines with consistent indentation
#   and provides enough detail for implementation.
```

**TODO types:**
- `TODO`: Future work
- `FIXME`: Known issue to fix
- `HACK`: Temporary workaround
- `XXX`: Dangerous or problematic code

### Comment Maintenance

When modifying code:
1. **Update related comments** - Ensure comments reflect new behavior
2. **Delete obsolete comments** - Remove comments that no longer apply
3. **Add comments for new complexity** - Document new non-obvious logic
4. **Review comments in diff** - Check that comments in changed code are still accurate

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Explaining "what" | Redundant with code | Delete or convert to "why" |
| Commented-out code | Clutters, confuses | Delete, rely on git history |
| Outdated comments | Misleading | Update or delete with code |
| Too many comments | Noise, hard to read | Keep only valuable comments |
| Missing "why" | Future maintainers confused | Add reasoning for non-obvious code |

### Cross-References

- Docstrings defined in CODE_QUALITY_STANDARD.md (CODE-01)
- Inline comments complement, don't replace docstrings
- TODO items can reference issues in GitHub

---

