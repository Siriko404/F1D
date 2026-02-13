# Phase 65: Architecture Standard Foundation - Research

**Researched:** 2026-02-13
**Domain:** Python project architecture, packaging standards, data science project organization
**Confidence:** HIGH

## Summary

This research covers industry-standard Python project architecture for scientific/data science projects, focusing on the src layout pattern recommended by Python Packaging Authority, cookiecutter-data-science conventions, and best practices for reproducible research projects. The key findings inform how to structure the ARCHITECTURE_STANDARD.md Section 1 (Folder Structure) to achieve portfolio-ready quality for the F1D thesis data processing pipeline.

**Primary recommendation:** Adopt a hybrid src-layout pattern that balances PyPA best practices with data science workflow conventions. Define a canonical target structure with clear migration guidance from the current flat layout.

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

None - all areas delegated to Claude's discretion.

### Claude's Discretion

#### Document Structure
- Research industry standards for Python project architecture documentation

#### Specification Depth
- Balance prescriptiveness with flexibility based on best practices

#### Current vs Target State
- Determine whether to document current state, ideal state, or include migration guidance

#### Module Organization
- Define __init__.py hierarchy and module boundaries based on Python packaging standards

### Key Guidance from CONTEXT.md
- Research industry standards (Python Packaging Authority, scientific Python projects, data science repos)
- Define standards that are portfolio-ready quality
- Consider the thesis/research context (data processing pipeline)
- Standards should be implementable in a future milestone
- Document rationale for each decision

### Specific Ideas
- User explicitly wants industry-standard approach
- Quality goal: portfolio-ready repository
- Context: F1D thesis data processing pipeline
- Must be research-grade: reproducible, verifiable, auditable

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope.

</user_constraints>

---

## Standard Stack

### Core
| Standard/Pattern | Version | Purpose | Why Standard |
|------------------|---------|---------|--------------|
| Python Packaging Authority (PyPA) src-layout | Current | Canonical project structure | Official recommendation, prevents import issues |
| Cookiecutter Data Science (CCDS) V2 | 2024+ | Data science project conventions | Widely adopted, industry-recognized template |
| pyproject.toml (PEP 621) | Current | Unified project configuration | Official standard, replaces setup.py |
| __init__.py package pattern | Current | Module organization | Enables proper imports, defines public API |

### Supporting
| Standard/Pattern | Purpose | When to Use |
|------------------|---------|-------------|
| Semantic Versioning (SemVer) | Version management | For package releases |
| Keep a Changelog | Change documentation | For project history |
| FAIR Principles | Research reproducibility | For scientific projects |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| src-layout | Flat layout | Flat layout simpler for scripts, but causes import path issues |
| data/raw, data/processed | data/01_raw, data/02_processed | Numbered prefixes clearer for pipelines, but less standard |
| config/ | configs/ or .config/ | Any naming works, config/ is most common |

---

## Architecture Patterns

### Recommended Target Structure (Hybrid src-layout + Data Science)

Based on PyPA recommendations, Cookiecutter Data Science V2, and scientific Python best practices:

```
project-root/
├── .github/                    # CI/CD workflows, issue templates
│   ├── workflows/
│   │   └── test.yml
│   └── ISSUE_TEMPLATE/
├── .planning/                  # GSD planning artifacts (project-specific)
├── config/                     # Configuration files
│   ├── project.yaml            # Main configuration
│   └── logging.yaml            # Logging configuration
├── data/                       # Data directory (gitignored)
│   ├── raw/                    # Original immutable data (read-only)
│   ├── interim/                # Intermediate processing stages
│   ├── processed/              # Cleaned, transformed data
│   └── external/               # Third-party reference data
├── docs/                       # Documentation
│   ├── ARCHITECTURE_STANDARD.md
│   ├── VARIABLE_CATALOG.md
│   ├── SCRIPT_DOCSTANDARD.md
│   └── index.md
├── results/                    # Analysis outputs (gitignored)
│   ├── figures/
│   ├── tables/
│   └── reports/
├── src/                        # Source code (src-layout)
│   └── f1d/                    # Main package
│       ├── __init__.py         # Package metadata, version
│       ├── sample/             # Stage 1: Sample construction
│       │   ├── __init__.py
│       │   └── build_manifest.py
│       ├── text/               # Stage 2: Text processing
│       │   ├── __init__.py
│       │   └── tokenize.py
│       ├── financial/          # Stage 3: Financial features
│       │   ├── __init__.py
│       │   └── variables.py
│       ├── econometric/        # Stage 4: Econometric analysis
│       │   ├── __init__.py
│       │   └── regressions.py
│       └── shared/             # Shared utilities
│           ├── __init__.py
│           ├── path_utils.py
│           ├── panel_ols.py
│           └── observability/
│               ├── __init__.py
│               ├── logging.py
│               └── stats.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── __init__.py
│   ├── integration/
│   │   └── __init__.py
│   ├── regression/
│   │   └── __init__.py
│   └── performance/
│       └── __init__.py
├── .___archive/                # Archived/deprecated code
│   ├── legacy/
│   ├── backups/
│   └── experiments/
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml              # Build system, tool configs
├── requirements.txt            # Pinned dependencies
└── setup.py                    # Optional backward compat
```

**Source:** Synthesized from:
- [PyPA src-layout discussion](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science)
- [Hitchhiker's Guide to Python](https://docs.python-guide.org/writing/structure/)

### Pattern 1: src-layout vs Flat Layout

**What:** The src-layout places importable code in a `src/package/` subdirectory, separating it from project configuration files.

**When to use:** Recommended for all projects that:
- May be packaged and distributed
- Need to prevent accidental usage of in-development code
- Want to ensure editable installs work correctly

**Example target vs current:**
```
# TARGET (src-layout):
src/f1d/shared/path_utils.py
# Import: from f1d.shared.path_utils import get_latest_output_dir

# CURRENT (flat layout):
2_Scripts/shared/path_utils.py
# Import: from shared.path_utils import get_latest_output_dir (with sys.path hack)
```

**Why src-layout wins:**
1. Prevents import conflicts between local checkout and installed version
2. Enforces proper package installation for testing
3. Makes packaging errors visible early (before distribution)
4. Standard among modern Python projects

**Source:** [PyPA src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

### Pattern 2: __init__.py Hierarchy

**What:** Each Python package directory must contain `__init__.py` to define it as a regular package and control the public API.

**Best practices:**
1. Keep `__init__.py` minimal - use for API definition, not heavy logic
2. Add docstrings to document package purpose
3. Use re-exports to define public API explicitly
4. Include version metadata in top-level package

**Example structure:**
```python
# src/f1d/__init__.py
"""F1D Data Processing Pipeline for CEO Uncertainty research."""

__version__ = "5.0.0"
__author__ = "Thesis Author"

# Public API re-exports
from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError
from f1d.shared.panel_ols import run_panel_ols

__all__ = [
    "get_latest_output_dir",
    "OutputResolutionError",
    "run_panel_ols",
]
```

```python
# src/f1d/shared/__init__.py
"""Shared utilities for F1D pipeline."""

from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.panel_ols import run_panel_ols

__all__ = ["get_latest_output_dir", "run_panel_ols"]
```

**Source:** [Real Python __init__.py guide](https://realpython.com/python-init-py/)

### Pattern 3: Data Directory Structure

**What:** Clear separation of data by processing stage with strict mutability rules.

**Recommended structure:**
```
data/
├── raw/           # NEVER modify - original data files (read-only)
├── interim/       # Intermediate processing (can regenerate)
├── processed/     # Final cleaned data for analysis
└── external/      # Third-party reference data
```

**Key principle:** Raw data is immutable. Never edit original files.

**Mapping to current structure:**
| Current | Target | Purpose |
|---------|--------|---------|
| 1_Inputs/ | data/raw/ | Original data |
| 4_Outputs/ (intermediate) | data/interim/ | Processing stages |
| 4_Outputs/ (final) | data/processed/ | Final datasets |
| 4_Outputs/ (reports) | results/ | Analysis outputs |

**Source:** [Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science)

### Pattern 4: Version Management

**What:** Strategy for managing multiple code versions (V1/V2) and deprecation.

**Recommendation for F1D:**

1. **Single Active Version:** Only V2 should be active. V1 is legacy.
2. **Deprecation Path:**
   - V1 remains in archive for reproducibility
   - V2 is the canonical implementation
   - No V3, V4, etc. - use semantic versioning on the package instead

3. **Archive Strategy:**
```
.___archive/
├── legacy/           # V1 scripts moved here
│   ├── 3_Financial/  # Original V1 financial scripts
│   └── 4_Econometric/# Original V1 econometric scripts
├── backups/          # Backup files (*.bak, *_backup.py)
└── experiments/      # Abandoned experiments
```

**Source:** [Stack Overflow - Legacy code handling](https://stackoverflow.com/questions/2815676/should-old-legacy-unused-code-be-deleted-from-source-control-repository)

### Anti-Patterns to Avoid

1. **Flat layout with sys.path hacks** - Current pattern requires try/except import fallbacks. Use proper package structure instead.

2. **Mixed data/output directories** - 4_Outputs/ contains both intermediate and final data. Separate into data/interim/ and data/processed/.

3. **Numbered script folders without package structure** - 2_Scripts/1_Sample/ etc. cannot be imported from. Use src/f1d/sample/ with __init__.py.

4. **Empty __init__.py without docstrings** - Every __init__.py should at minimum have a docstring explaining the package purpose.

5. **Parallel V1/V2/V3 structures** - Multiple "versions" as parallel directories is an anti-pattern. Use package versioning instead.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Package structure | Custom folder layout | src-layout per PyPA | Standard prevents import issues |
| Path resolution | sys.path.insert hacks | Proper package imports | Cleaner, testable, distributable |
| Data organization | Ad-hoc directories | Cookiecutter Data Science pattern | Industry standard |
| Version tracking | V1/V2/V3 folders | Git tags + semantic versioning | Proper version control |

**Key insight:** The current codebase has "hand-rolled" solutions for packaging problems (try/except imports, numbered directories). These should be replaced with standard Python packaging patterns.

---

## Common Pitfalls

### Pitfall 1: Import Path Confusion
**What goes wrong:** Scripts can't import from each other without sys.path manipulation, leading to try/except fallback patterns everywhere.
**Why it happens:** Flat layout without proper package structure.
**How to avoid:** Use src-layout with __init__.py in every directory. Install package in editable mode: `pip install -e .`
**Warning signs:** Frequent `sys.path.insert(0, ...)` calls in scripts.

### Pitfall 2: Data Directory Bleed
**What goes wrong:** Raw data gets modified accidentally, breaking reproducibility.
**Why it happens:** No clear separation between raw and processed data.
**How to avoid:** Separate data/raw/ (read-only) from data/processed/. Add file permissions or documented conventions.
**Warning signs:** Raw data files with timestamps newer than the original download.

### Pitfall 3: Version Proliferation
**What goes wrong:** V1, V2, V3 folders multiply, creating confusion about which is current.
**Why it happens:** Creating new folders instead of versioning the codebase properly.
**How to avoid:** Single active version, archive legacy code, use git tags for history.
**Warning signs:** Multiple *_V2/, *_V3/ directories in project.

### Pitfall 4: __init__.py Overload
**What goes wrong:** Too much logic in __init__.py causes slow imports and circular dependencies.
**Why it happens:** Treating __init__.py as a regular module instead of a package initializer.
**How to avoid:** Keep __init__.py minimal. Use it for API definition and re-exports only.
**Warning signs:** __init__.py files with >100 lines, heavy computations in imports.

---

## Code Examples

### Proper Package Structure

```python
# src/f1d/__init__.py
"""F1D Data Processing Pipeline.

A reproducible data processing pipeline for CEO uncertainty research.
This package implements a 4-stage pipeline: sample construction, text
processing, financial feature engineering, and econometric analysis.

Example:
    >>> from f1d import get_latest_output_dir
    >>> output = get_latest_output_dir("data/processed/manifest")
"""

__version__ = "5.0.0"
__author__ = "Thesis Author"

# Public API
from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError

__all__ = ["get_latest_output_dir", "OutputResolutionError"]
```

### Module Organization with Sub-packages

```python
# src/f1d/shared/__init__.py
"""Shared utilities for F1D pipeline."""

# Import from submodules for clean API
from f1d.shared.path_utils import (
    get_latest_output_dir,
    get_output_path,
    OutputResolutionError,
)
from f1d.shared.panel_ols import run_panel_ols, CollinearityError

__all__ = [
    "get_latest_output_dir",
    "get_output_path",
    "OutputResolutionError",
    "run_panel_ols",
    "CollinearityError",
]
```

### pyproject.toml Structure

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "f1d"
version = "5.0.0"
description = "F1D Data Processing Pipeline for CEO Uncertainty Research"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
authors = [
    {name = "Thesis Author", email = "author@university.edu"}
]
dependencies = [
    "pandas>=2.0",
    "numpy>=1.24",
    "pyyaml>=6.0",
    # ... other dependencies
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.1.0", "mypy>=1.0"]

[tool.setuptools.packages.find]
where = ["src"]

# Tool configurations (existing)
[tool.pytest.ini_options]
# ... existing pytest config
```

**Source:** [PyPA pyproject.toml guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| setup.py with setuptools | pyproject.toml (PEP 621) | 2021+ | Unified configuration, modern tooling |
| Flat layout | src-layout | 2019+ | Prevents import issues, better packaging |
| Namespace packages (no __init__.py) | Regular packages with __init__.py | Always | Faster imports, explicit structure |
| Multiple V1/V2/V3 directories | Single version with git tags | Best practice | Clear versioning, less confusion |

**Deprecated/outdated:**
- **setup.py as primary config:** Use pyproject.toml instead (setup.py optional for backward compat)
- **Empty __init__.py as default:** Include docstrings and API definitions
- **sys.path manipulation for imports:** Use proper package installation

---

## Current State vs Target State Analysis

### Current F1D Structure
```
F1D/
├── 1_Inputs/              # Raw data
├── 2_Scripts/             # All source code (flat)
│   ├── 1_Sample/
│   ├── 2_Text/
│   ├── 3_Financial/       # V1
│   ├── 3_Financial_V2/    # V2
│   ├── 4_Econometric/     # V1
│   ├── 4_Econometric_V2/  # V2
│   └── shared/
├── 3_Logs/                # Execution logs
├── 4_Outputs/             # All outputs
├── config/
├── docs/
├── tests/
├── .___archive/
└── pyproject.toml         # Tool config only (no build system)
```

### Target F1D Structure (v6.0+)
```
F1D/
├── src/f1d/               # Package source (src-layout)
│   ├── sample/
│   ├── text/
│   ├── financial/
│   ├── econometric/
│   └── shared/
├── data/                  # Data directory
│   ├── raw/               # (from 1_Inputs/)
│   ├── interim/           # (from 4_Outputs/ intermediate)
│   └── processed/         # (from 4_Outputs/ final)
├── results/               # Analysis outputs
├── logs/                  # Execution logs
├── config/
├── docs/
├── tests/
├── .___archive/
│   └── legacy/            # V1 scripts
└── pyproject.toml         # Full config with build system
```

### Recommendation: Document Target State with Migration Path

For ARCHITECTURE_STANDARD.md:
1. **Document target state** as the canonical standard
2. **Include migration guidance** as an appendix
3. **Mark current state** as legacy that will be deprecated
4. **Provide incremental migration steps** for v6.0+ implementation

---

## Open Questions

1. **Should we keep numbered stages (1_, 2_, 3_, 4_) or switch to semantic names (sample/, text/, financial/, econometric/)?**
   - What we know: Numbered prefixes help with pipeline ordering visibility
   - What's unclear: Whether semantic names are more Pythonic/standard
   - Recommendation: Use semantic names in src/f1d/ package, keep numbered references in documentation for pipeline clarity

2. **Should results/ and logs/ be under data/ or top-level?**
   - What we know: Cookiecutter puts reports/ top-level, logs often top-level
   - What's unclear: Best practice for research projects specifically
   - Recommendation: Keep top-level (results/, logs/) - separate from data/ which is for datasets

3. **How to handle large data files that shouldn't be in git?**
   - What we know: data/ is typically gitignored
   - What's unclear: Whether to document data retrieval/creation scripts
   - Recommendation: Document data sources in README, provide download/cache scripts, use DVC or similar for large datasets if needed

---

## Sources

### Primary (HIGH confidence)
- [PyPA src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) - Official guidance on project structure
- [PyPA Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - Official configuration guide
- [PyPA Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/) - Official tutorial
- [Real Python __init__.py Guide](https://realpython.com/python-init-py/) - Comprehensive module organization guide

### Secondary (MEDIUM confidence)
- [Cookiecutter Data Science V2](https://drivendata.co/blog/ccds-v2) - Industry-standard data science template (verified with GitHub)
- [Hitchhiker's Guide to Python - Structure](https://docs.python-guide.org/writing/structure/) - Community best practices
- [How to organize your Python data science project](https://gist.github.com/ericmjl/27e50331f24db3e8f957d1fe7bbbe510) - Practical data science organization

### Tertiary (LOW confidence)
- Various blog posts on Python project structure - Cross-verified with primary sources

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Directly from PyPA official documentation
- Architecture patterns: HIGH - Synthesized from multiple authoritative sources
- Pitfalls: MEDIUM - Based on observed patterns and expert guidance
- Current vs target analysis: HIGH - Based on direct codebase inspection

**Research date:** 2026-02-13
**Valid until:** 2026-03-15 (stable standards, 30 days for potential tooling updates)

---

*Research completed: 2026-02-13*
*Phase: 65-architecture-standard-foundation*
