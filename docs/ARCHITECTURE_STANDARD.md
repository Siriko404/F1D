# F1D Architecture Standard

**Version:** 5.0
**Last Updated:** 2026-02-13
**Status:** DEFINITION - Implementation deferred to v6.0+
**Milestone:** v5.0 Architecture Standard Definition

---

## Purpose

This document defines the canonical architecture standard for the F1D (Financial Text Analysis) data processing pipeline. It establishes the folder structure, module organization, data management, versioning, and archival conventions that ensure:

- **Reproducibility:** All analyses can be recreated from raw data
- **Auditability:** Complete traceability from results to source data
- **Maintainability:** Clear structure that supports long-term maintenance
- **Quality:** Industry-standard practices for portfolio-ready code

This is a **DEFINITION document**. The standards described here represent the target architecture that will be implemented in v6.0+. Current code follows legacy patterns documented in Appendix A.

---

## Document Structure

This standard is organized into 5 main sections:

1. **Folder Structure** (ARCH-01): Canonical directory layout with src-layout pattern
2. **Module Organization** (ARCH-02): __init__.py hierarchy and package conventions
3. **Data Directory Structure** (ARCH-03): Data lifecycle stages and mutability rules
4. **Version Management** (ARCH-04): Single active version policy and deprecation strategy
5. **Archive and Legacy Code** (ARCH-05): Archive structure and legacy code handling

Additionally:
- **Appendix A**: Migration Guide from current to target state
- **Appendix B**: Relationship to other standards (naming, configuration, documentation)

---

## How to Use This Standard

### For New Development (v6.0+)

1. Follow the canonical folder structure (Section 1)
2. Use the module organization patterns (Section 2)
3. Store data according to lifecycle stage (Section 3)
4. Use semantic versioning on the package (Section 4)
5. Archive deprecated code properly (Section 5)

### For Current Development (v5.0)

1. Use this standard as reference for understanding the target architecture
2. New code should align with these patterns where feasible
3. Document deviations from the standard
4. Plan for migration to the standard structure

### For Code Review

1. Check alignment with folder structure conventions
2. Verify __init__.py follows the pattern
3. Ensure data storage follows mutability rules
4. Confirm deprecated code is properly archived

---

## Design Principles

### 1. Reproducibility (FAIR Principles)

The architecture supports FAIR principles (Findable, Accessible, Interoperable, Reusable):

- **Findable:** Clear structure makes data and code easy to locate
- **Accessible:** Standard paths and import patterns ensure code is usable
- **Interoperable:** Industry-standard patterns align with Python ecosystem
- **Reusable:** Proper packaging enables code reuse across projects

**Implementation:**
- Raw data is never modified (immutability)
- All transformations are version-controlled
- Dependencies are pinned and documented
- Processing scripts are deterministic

### 2. Auditability (Complete Traceability)

Every result can be traced back to source data and transformations:

- **Input provenance:** Clear separation of raw vs. processed data
- **Processing history:** Git tracks all code changes
- **Output lineage:** Results directory preserves analysis outputs
- **Configuration tracking:** Config files document parameters used

**Implementation:**
- data/raw/ is read-only
- data/processed/ documents transformation pipeline
- results/ captures all analysis outputs
- logs/ preserves execution history

### 3. Maintainability (Clear Structure)

The structure supports long-term maintenance and evolution:

- **Separation of concerns:** Code, data, config, docs, tests are separate
- **Explicit dependencies:** pyproject.toml manages all dependencies
- **Consistent patterns:** Same structure applies across all modules
- **Documentation:** Every package and module is documented

**Implementation:**
- src-layout prevents import issues
- __init__.py defines public APIs
- Tests mirror source structure
- Documentation is versioned with code

### 4. Industry Alignment (Standards Compliance)

The architecture follows recognized industry standards:

- **Python Packaging Authority (PyPA):** src-layout, pyproject.toml
- **Cookiecutter Data Science:** Data directory conventions
- **Semantic Versioning:** Package version management
- **Scientific Python:** Research project best practices

**Implementation:**
- PyPA-recommended src-layout pattern
- Cookiecutter data science directory structure
- PEP 621 compliant pyproject.toml
- Standard Python packaging conventions

---

## Standards Hierarchy

This architecture standard is the foundation for a suite of standards:

```
ARCHITECTURE_STANDARD.md (this document)
    ├── Defines: Folder structure, module organization
    │
    ├── Referenced by:
    │   ├── NAMING_STANDARD.md (Phase 66) - File and variable naming conventions
    │   ├── CONFIG_STANDARD.md (Phase 67) - Configuration file patterns
    │   └── DOC_STANDARD.md (Phase 68) - Documentation templates
    │
    └── All standards build upon this foundation
```

Changes to this document may require updates to dependent standards.

---

## Scope and Exclusions

### In Scope

- Directory structure and organization
- Package and module conventions
- Data lifecycle management
- Version control approach
- Archive and legacy handling

### Out of Scope

- Naming conventions (Phase 66: NAMING_STANDARD.md)
- Configuration patterns (Phase 67: CONFIG_STANDARD.md)
- Documentation templates (Phase 68: DOC_STANDARD.md)
- CI/CD pipeline configuration
- Deployment procedures

---

---

## 1. Folder Structure (ARCH-01)

This section defines the canonical directory layout for the F1D project using the src-layout pattern recommended by the Python Packaging Authority.

### Target Structure

```
F1D/                              # Project root
├── .github/                      # GitHub-specific configuration
│   ├── workflows/                # CI/CD workflows
│   │   └── test.yml              # Test automation
│   └── ISSUE_TEMPLATE/           # Issue templates
│
├── .planning/                    # GSD planning artifacts
│   ├── phases/                   # Phase-specific plans
│   ├── STATE.md                  # Current project state
│   ├── PROJECT.md                # Project overview
│   └── ROADMAP.md                # Milestone roadmap
│
├── config/                       # Configuration files
│   ├── project.yaml              # Main project configuration
│   ├── logging.yaml              # Logging configuration
│   └── hypotheses.yaml           # Hypothesis definitions
│
├── data/                         # Data directory (mostly gitignored)
│   ├── raw/                      # Original immutable data (READ-ONLY)
│   ├── interim/                  # Intermediate processing stages
│   ├── processed/                # Final cleaned datasets
│   └── external/                 # Third-party reference data
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE_STANDARD.md  # This document
│   ├── VARIABLE_CATALOG.md       # Variable definitions
│   ├── SCRIPT_DOCSTANDARD.md     # Script documentation standard
│   ├── index.md                  # Documentation index
│   └── figures/                  # Documentation figures
│
├── results/                      # Analysis outputs (gitignored)
│   ├── figures/                  # Generated plots and visualizations
│   ├── tables/                   # Generated tables (CSV, LaTeX)
│   └── reports/                  # Generated reports and summaries
│
├── src/                          # Source code (src-layout pattern)
│   └── f1d/                      # Main package
│       ├── __init__.py           # Package metadata and public API
│       │
│       ├── sample/               # Stage 1: Sample construction
│       │   ├── __init__.py
│       │   ├── build_manifest.py # Manifest construction
│       │   └── filters.py        # Sample filters
│       │
│       ├── text/                 # Stage 2: Text processing
│       │   ├── __init__.py
│       │   ├── tokenize.py       # Tokenization utilities
│       │   └── uncertainty.py    # Uncertainty measures
│       │
│       ├── financial/            # Stage 3: Financial features
│       │   ├── __init__.py
│       │   ├── variables.py      # Variable construction
│       │   └── investment.py     # Investment metrics
│       │
│       ├── econometric/          # Stage 4: Econometric analysis
│       │   ├── __init__.py
│       │   ├── regressions.py    # Regression models
│       │   └── diagnostics.py    # Model diagnostics
│       │
│       └── shared/               # Shared utilities
│           ├── __init__.py
│           ├── path_utils.py     # Path resolution
│           ├── panel_ols.py      # Panel OLS utilities
│           ├── io_utils.py       # I/O utilities
│           └── observability/    # Logging and monitoring
│               ├── __init__.py
│               ├── logging.py    # Logging configuration
│               └── stats.py      # Execution statistics
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration and fixtures
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py
│   │   ├── test_path_utils.py
│   │   └── test_panel_ols.py
│   ├── integration/              # Integration tests
│   │   ├── __init__.py
│   │   └── test_pipeline.py
│   ├── regression/               # Regression tests
│   │   ├── __init__.py
│   │   └── test_outputs.py
│   └── performance/              # Performance tests
│       ├── __init__.py
│       └── test_memory.py
│
├── logs/                         # Execution logs (gitignored)
│   └── *.log
│
├── .___archive/                  # Archived/deprecated code
│   ├── legacy/                   # V1 scripts and deprecated code
│   ├── backups/                  # Backup files (*.bak, *_backup.py)
│   ├── experiments/              # Abandoned experiments
│   ├── docs/                     # Old documentation versions
│   ├── README.md                 # Archive documentation
│   └── manifest.json             # Archive tracking
│
├── .gitignore                    # Git ignore patterns
├── .pre-commit-config.yaml       # Pre-commit hooks (optional)
├── LICENSE                       # License file
├── README.md                     # Project readme
├── pyproject.toml                # Build system and tool configs
├── requirements.txt              # Pinned dependencies
└── setup.py                      # Optional backward compatibility
```

### Directory Descriptions

#### Top-Level Directories

| Directory | Purpose | Git Status | Write Access |
|-----------|---------|------------|--------------|
| `.github/` | GitHub CI/CD and templates | Tracked | Developers |
| `.planning/` | GSD workflow planning artifacts | Tracked | GSD workflow |
| `config/` | Configuration files | Tracked | Developers |
| `data/` | All data files | Partially ignored | Pipeline only |
| `docs/` | Documentation | Tracked | Developers |
| `results/` | Analysis outputs | Ignored | Analysis scripts |
| `src/` | Source code package | Tracked | Developers |
| `tests/` | Test suite | Tracked | Developers |
| `logs/` | Execution logs | Ignored | Pipeline only |
| `.___archive/` | Archived code | Tracked | Archive process |

#### Data Subdirectories

| Directory | Purpose | Mutability | Notes |
|-----------|---------|------------|-------|
| `data/raw/` | Original immutable data | READ-ONLY | Never modify |
| `data/interim/` | Intermediate processing | Deletable | Can regenerate |
| `data/processed/` | Final cleaned data | Controlled | Source for analysis |
| `data/external/` | Third-party data | Reference | Document sources |

#### Results Subdirectories

| Directory | Purpose | Content Types |
|-----------|---------|---------------|
| `results/figures/` | Visualizations | PNG, PDF, SVG |
| `results/tables/` | Data tables | CSV, LaTeX, Excel |
| `results/reports/` | Generated reports | Markdown, PDF, HTML |

### File Placement Rules

#### Root Files (Required)

| File | Purpose | Required |
|------|---------|----------|
| `pyproject.toml` | Build system, dependencies, tool configs | Yes |
| `README.md` | Project overview and quick start | Yes |
| `LICENSE` | License information | Yes |
| `.gitignore` | Git ignore patterns | Yes |
| `requirements.txt` | Pinned dependencies | Recommended |
| `setup.py` | Backward compatibility | Optional |

#### Configuration Files

All configuration files MUST be placed in `config/`:

- `project.yaml` - Main project configuration
- `logging.yaml` - Logging configuration
- `hypotheses.yaml` - Hypothesis definitions
- Additional config files as needed

#### Documentation Files

All documentation files MUST be placed in `docs/`:

- Standards documents (ARCHITECTURE_STANDARD.md, etc.)
- Variable catalogs and references
- User guides and tutorials
- API documentation

#### Test Files

All test files MUST be placed in `tests/` with structure mirroring `src/`:

```
tests/
├── unit/test_path_utils.py    → src/f1d/shared/path_utils.py
├── integration/test_pipeline.py → End-to-end tests
└── regression/test_outputs.py  → Output validation
```

### Rationale

#### Why src-layout?

The src-layout pattern (placing code in `src/package/`) is recommended by PyPA over flat layout for several reasons:

1. **Prevents import confusion**: Separates importable code from project files
2. **Better editable installs**: Ensures `pip install -e .` works correctly
3. **Early error detection**: Packaging issues surface before distribution
4. **Industry standard**: Modern Python projects use src-layout

**Source:** [PyPA src-layout vs flat layout discussion](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

#### Why Separate data/ and results/?

1. **Different lifecycles**: Data is input, results are output
2. **Different git handling**: Data often gitignored, results always gitignored
3. **Clear semantics**: Separates source material from generated output
4. **Cookiecutter standard**: Aligns with data science conventions

#### Why .___archive/ Not Just Delete?

1. **Reproducibility**: Old code may be needed to reproduce old results
2. **Reference value**: Shows evolution of the codebase
3. **Git tracks history**: But archived files are explicitly marked as deprecated
4. **Clear boundaries**: Developers know archived code is not for active use

---

## 2. Module Organization (ARCH-02)

This section defines the package structure, __init__.py conventions, and module organization patterns for the F1D project.

### Package Structure

The F1D package follows a hierarchical structure with clear separation of concerns:

```
src/f1d/                    # Main package (root)
├── __init__.py             # Package metadata and public API
│
├── sample/                 # Stage 1: Sample construction
│   ├── __init__.py
│   ├── build_manifest.py   # Manifest construction
│   └── filters.py          # Sample filters
│
├── text/                   # Stage 2: Text processing
│   ├── __init__.py
│   ├── tokenize.py         # Tokenization
│   └── uncertainty.py      # Uncertainty measures
│
├── financial/              # Stage 3: Financial features
│   ├── __init__.py
│   ├── variables.py        # Variable construction
│   └── investment.py       # Investment metrics
│
├── econometric/            # Stage 4: Econometric analysis
│   ├── __init__.py
│   ├── regressions.py      # Regression models
│   └── diagnostics.py      # Model diagnostics
│
└── shared/                 # Shared utilities (cross-cutting)
    ├── __init__.py
    ├── path_utils.py       # Path resolution
    ├── panel_ols.py        # Panel OLS utilities
    ├── io_utils.py         # I/O utilities
    └── observability/      # Logging and monitoring
        ├── __init__.py
        ├── logging.py      # Logging configuration
        └── stats.py        # Execution statistics
```

### __init__.py Pattern

Every package directory MUST have an `__init__.py` file. This file serves three purposes:

1. **Marks directory as package**: Enables imports
2. **Documents package purpose**: Via docstring
3. **Defines public API**: Via re-exports

#### Required Content

```python
# src/f1d/__init__.py
"""F1D Data Processing Pipeline for CEO Uncertainty Research.

This package implements a 4-stage data processing pipeline:
1. Sample Construction - Build analyst-CEO manifest
2. Text Processing - Tokenize and analyze conference calls
3. Financial Features - Construct financial variables
4. Econometric Analysis - Run panel regressions

Example:
    >>> from f1d import get_latest_output_dir
    >>> output = get_latest_output_dir("data/processed/manifest")

Attributes:
    __version__: Package version (semantic versioning)
    __author__: Package author
"""

__version__ = "5.0.0"
__author__ = "Thesis Author"

# Public API re-exports
from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError
from f1d.shared.panel_ols import run_panel_ols

__all__ = [
    # Path utilities
    "get_latest_output_dir",
    "OutputResolutionError",
    # Econometric utilities
    "run_panel_ols",
]
```

#### Subpackage __init__.py Pattern

```python
# src/f1d/shared/__init__.py
"""Shared utilities for F1D pipeline.

This package contains cross-cutting utilities used across
all stages of the data processing pipeline.

Modules:
    path_utils: Path resolution and output directory utilities
    panel_ols: Panel OLS regression utilities
    io_utils: Input/output utilities
    observability: Logging and monitoring
"""

# Import key functions for clean API
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

#### Stage Package __init__.py Pattern

```python
# src/f1d/financial/__init__.py
"""Financial feature engineering for F1D pipeline.

Stage 3 of the pipeline - constructs financial variables
from Compustat and CRSP data.

Main Functions:
    construct_variables: Build all financial variables
    calculate_investment: Calculate investment metrics
"""

from f1d.financial.variables import construct_variables
from f1d.financial.investment import calculate_investment

__all__ = [
    "construct_variables",
    "calculate_investment",
]
```

### __init__.py Best Practices

#### DO:
- Include comprehensive docstring with purpose and usage
- Define `__version__` in top-level package only
- Use `__all__` to explicitly declare public API
- Re-export commonly used functions for convenience
- Keep the file minimal - no heavy logic

#### DON'T:
- Put complex logic in `__init__.py`
- Import everything from submodules (only public API)
- Create circular dependencies
- Leave `__init__.py` empty without docstring
- Execute slow operations at import time

### Module Example

```python
# src/f1d/shared/path_utils.py
"""Path resolution utilities for F1D pipeline.

This module provides utilities for resolving paths to data files
and output directories, handling versioning and date-based naming.

Example:
    >>> from f1d.shared.path_utils import get_latest_output_dir
    >>> latest = get_latest_output_dir("data/processed/manifest")
    >>> print(latest)
    data/processed/manifest/2024-01-15
"""

from pathlib import Path
from typing import Optional
from datetime import datetime


class OutputResolutionError(Exception):
    """Raised when output directory cannot be resolved."""
    pass


def get_latest_output_dir(base_path: str) -> Path:
    """Find the most recent output directory.

    Args:
        base_path: Base directory containing dated subdirectories

    Returns:
        Path to the most recent dated subdirectory

    Raises:
        OutputResolutionError: If no valid directories found

    Example:
        >>> get_latest_output_dir("data/processed/manifest")
        PosixPath('data/processed/manifest/2024-01-15')
    """
    base = Path(base_path)
    if not base.exists():
        raise OutputResolutionError(f"Base path does not exist: {base_path}")

    # Find all dated directories
    dated_dirs = [d for d in base.iterdir() if d.is_dir()]

    if not dated_dirs:
        raise OutputResolutionError(f"No output directories found in {base_path}")

    # Sort by name (assumes YYYY-MM-DD format)
    dated_dirs.sort(reverse=True)

    return dated_dirs[0]
```

### Module Tier System

Modules are organized into tiers based on their role and quality requirements:

#### Tier 1: Core Shared Utilities (Highest Quality Bar)

**Location:** `src/f1d/shared/`

**Characteristics:**
- Used across all stages
- 100% test coverage required
- Comprehensive docstrings
- Type hints required
- Breaking changes require deprecation period

**Examples:**
- `path_utils.py` - Path resolution
- `panel_ols.py` - Panel OLS utilities
- `io_utils.py` - I/O utilities

**Quality Requirements:**
- Test coverage: 100%
- Documentation: Complete with examples
- Review: Required for all changes
- Stability: Breaking changes deprecated for 30+ days

#### Tier 2: Stage-Specific Modules (Standard Quality)

**Location:** `src/f1d/{stage}/`

**Characteristics:**
- Specific to one pipeline stage
- 80%+ test coverage required
- Standard docstrings
- Type hints recommended

**Examples:**
- `sample/build_manifest.py`
- `text/uncertainty.py`
- `financial/variables.py`
- `econometric/regressions.py`

**Quality Requirements:**
- Test coverage: 80%+
- Documentation: Standard docstrings
- Review: Recommended for significant changes
- Stability: Normal change process

#### Tier 3: Scripts and One-offs (Lower Quality Bar)

**Location:** `scripts/` or stage-specific `scripts/` subdirectory

**Characteristics:**
- Ad-hoc analysis or data exploration
- May not have tests
- Minimal documentation acceptable
- Not imported by other modules

**Examples:**
- Data validation scripts
- One-time data migrations
- Exploratory analysis

**Quality Requirements:**
- Test coverage: Optional
- Documentation: Basic header comment
- Review: Optional
- Stability: No guarantees

### Import Conventions

#### Absolute Imports (Preferred)

```python
# CORRECT: Absolute imports
from f1d.shared.path_utils import get_latest_output_dir
from f1d.financial.variables import construct_variables
from f1d.econometric.regressions import run_panel_ols

# INCORRECT: Relative imports (avoid)
from ..shared.path_utils import get_latest_output_dir
from .variables import construct_variables
```

#### Import Order

Follow PEP 8 import order:

```python
# Standard library
import os
from pathlib import Path
from typing import Dict, List, Optional

# Third-party packages
import numpy as np
import pandas as pd
from linearmodels import PanelOLS

# Local imports
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.logging import get_logger
```

### Anti-Patterns to Avoid

#### 1. Empty __init__.py Without Docstring

```python
# BAD: Empty file
# (literally empty)

# GOOD: At minimum, has docstring
"""Shared utilities for F1D pipeline."""
```

#### 2. Heavy Logic in __init__.py

```python
# BAD: Heavy computation at import time
from f1d.shared.path_utils import get_latest_output_dir
LATEST_DATA = get_latest_output_dir("data/processed")  # SLOW!

# GOOD: Lazy evaluation
def get_latest_data():
    """Get latest data directory (lazy)."""
    return get_latest_output_dir("data/processed")
```

#### 3. Circular Dependencies

```python
# BAD: module_a imports module_b, module_b imports module_a
# module_a.py
from .module_b import func_b

# module_b.py
from .module_a import func_a

# GOOD: Refactor shared logic to third module
# shared_logic.py
def shared_func():
    pass

# module_a.py
from .shared_logic import shared_func

# module_b.py
from .shared_logic import shared_func
```

#### 4. Importing Everything

```python
# BAD: Import everything
from f1d.shared.path_utils import *

# GOOD: Import only what you need
from f1d.shared.path_utils import (
    get_latest_output_dir,
    OutputResolutionError,
)
```

### Rationale

#### Why __init__.py in Every Directory?

1. **Explicit package structure**: Clear what is importable
2. **Public API control**: Use `__all__` to define interface
3. **Documentation**: Docstrings document package purpose
4. **Re-exports**: Provide convenient import paths
5. **Namespace management**: Prevent accidental shadowing

#### Why Absolute Imports Over Relative?

1. **Clarity**: Import path shows exact location
2. **Refactoring**: Moving files doesn't break imports
3. **Tooling**: IDEs and linters work better
4. **Standard**: PEP 8 recommends absolute imports
5. **Debugging**: Easier to trace import errors

#### Why Module Tiers?

1. **Risk management**: Higher tiers have higher stakes
2. **Resource allocation**: Focus quality efforts on critical code
3. **Clear expectations**: Developers know the bar for each tier
4. **Scalability**: Allows rapid development where appropriate

---

## 3. Data Directory Structure (ARCH-03)

This section defines the data directory organization and mutability rules following Cookiecutter Data Science conventions.

### Data Lifecycle Stages

The `data/` directory is organized by data processing stage:

```
data/
├── raw/           # Original immutable data (NEVER MODIFY)
│   ├── transcripts/      # Raw earnings call transcripts
│   ├── compustat/        # Compustat fundamental data
│   ├── crsp/             # CRSP stock returns
│   └── ibes/             # IBES analyst forecasts
│
├── interim/       # Intermediate processing (CAN REGENERATE)
│   ├── sample/           # Sample construction intermediates
│   ├── text/             # Text processing intermediates
│   └── financial/        # Financial variable intermediates
│
├── processed/     # Final cleaned data (SOURCE FOR ANALYSIS)
│   ├── manifest/         # Final analyst-CEO manifest
│   ├── uncertainty/      # Final uncertainty measures
│   └── variables/        # Final financial variables
│
└── external/      # Third-party reference data
    ├── ff_factors/       # Fama-French factors
    ├── gvkey_cik/        # GVKEY-CIK mapping
    └── sic_codes/        # SIC code definitions
```

### Mutability Rules

#### data/raw/ - READ ONLY

**Purpose:** Original immutable data from external sources

**Rules:**
- NEVER modify files in this directory
- NEVER delete files without archiving
- NEVER overwrite existing files
- All files should have original timestamps
- Document data sources in `data/raw/README.md`

**Git:** Partially tracked (small reference files only, large data gitignored)

**Example structure:**
```
data/raw/
├── README.md                    # Data sources documentation
├── transcripts/
│   ├── 2024-01-15_download.log  # Download metadata
│   └── earnings_calls_2010_2023.parquet
├── compustat/
│   ├── 2024-01-10_download.log
│   └── compustat_annual_2000_2023.parquet
└── crsp/
    ├── 2024-01-10_download.log
    └── crsp_daily_2000_2023.parquet
```

#### data/interim/ - DELETABLE

**Purpose:** Intermediate processing stages that can be regenerated

**Rules:**
- Files can be deleted and regenerated from raw data
- Use dated subdirectories for versioning
- Document what each file contains
- Not source of truth - can be cleaned up

**Git:** Ignored (regenerable)

**Example structure:**
```
data/interim/
├── sample/
│   ├── 2024-01-15/
│   │   ├── step1_initial_filter.parquet
│   │   ├── step2_ceo_match.parquet
│   │   └── step3_analyst_link.parquet
│   └── 2024-01-20/
│       └── ... (updated version)
└── text/
    ├── 2024-01-16/
    │   ├── tokenized_transcripts.parquet
    │   └── uncertainty_scores.parquet
    └── ...
```

#### data/processed/ - CONTROLLED

**Purpose:** Final cleaned datasets used for analysis

**Rules:**
- These are the source of truth for analysis
- Changes require documentation and versioning
- Use dated subdirectories for versioning
- Changes should go through review process

**Git:** Partially tracked (final datasets tracked, intermediate ignored)

**Example structure:**
```
data/processed/
├── manifest/
│   ├── 2024-01-20/
│   │   ├── manifest_final.parquet      # Final manifest
│   │   ├── manifest_summary.yaml       # Summary statistics
│   │   └── VALIDATION.md               # Validation report
│   └── 2024-01-25/
│       └── ... (updated version)
├── uncertainty/
│   └── 2024-01-22/
│       ├── ceo_uncertainty.parquet
│       └── uncertainty_summary.yaml
└── variables/
    └── 2024-01-24/
        ├── financial_variables.parquet
        └── variables_summary.yaml
```

#### data/external/ - REFERENCE

**Purpose:** Third-party reference data not from primary sources

**Rules:**
- Document source and version
- Include license information if applicable
- Don't modify external data files
- Update with explicit process

**Git:** Tracked (usually small reference files)

**Example structure:**
```
data/external/
├── README.md                    # External data sources
├── ff_factors/
│   ├── README.md
│   └── fama_french_3factor.csv
├── gvkey_cik/
│   ├── README.md
│   └── gvkey_cik_mapping.csv
└── sic_codes/
    ├── README.md
    └── sic_definitions.csv
```

### Results Directory Structure

The `results/` directory contains analysis outputs:

```
results/
├── figures/                  # Generated visualizations
│   ├── uncertainty/
│   │   ├── uncertainty_distribution.png
│   │   └── uncertainty_over_time.png
│   ├── regressions/
│   │   ├── coefficient_plot.png
│   │   └── residual_diagnostic.png
│   └── descriptive/
│       └── sample_composition.png
│
├── tables/                   # Generated tables
│   ├── descriptive/
│   │   ├── sample_stats.tex
│   │   ├── sample_stats.csv
│   │   └── variable_definitions.tex
│   ├── regressions/
│   │   ├── main_results.tex
│   │   ├── main_results.csv
│   │   └── robustness.tex
│   └── correlations/
│       └── correlation_matrix.csv
│
└── reports/                  # Generated reports
    ├── 2024-01-30_analysis/
    │   ├── analysis_summary.md
    │   ├── full_report.pdf
    │   └── supplementary_materials/
    └── ...
```

### Current-to-Target Mapping

The following table shows how current directories map to the target structure:

| Current Location | Target Location | Content | Action Required |
|------------------|-----------------|---------|-----------------|
| `1_Inputs/` | `data/raw/` | Original data files | Move and document |
| `4_Outputs/` (intermediate) | `data/interim/` | Processing intermediates | Move and organize |
| `4_Outputs/` (final datasets) | `data/processed/` | Final cleaned data | Move and version |
| `4_Outputs/` (figures) | `results/figures/` | Generated plots | Move |
| `4_Outputs/` (tables) | `results/tables/` | Generated tables | Move |
| `4_Outputs/` (reports) | `results/reports/` | Generated reports | Move |
| `3_Logs/` | `logs/` | Execution logs | Move |

### Data Documentation Requirements

Every data directory MUST have a README.md documenting:

#### For data/raw/:
```markdown
# Raw Data Sources

## transcripts/
- **Source:** Thomson Reuters StreetEvents
- **Date Downloaded:** 2024-01-15
- **Date Range:** 2010-2023
- **Records:** 125,000 earnings calls
- **Format:** Parquet

## compustat/
- **Source:** Compustat Annual
- **Date Downloaded:** 2024-01-10
- **Date Range:** 2000-2023
- **Records:** 150,000 firm-years
- **Format:** Parquet
```

#### For data/processed/:
```markdown
# Processed Data: manifest/2024-01-20

## manifest_final.parquet
- **Records:** 45,000 analyst-CEO pairs
- **Variables:** analyst_id, ceo_id, gvkey, year, transcript_id
- **Source Script:** src/f1d/sample/build_manifest.py
- **Validation:** Passed all checks (see VALIDATION.md)
- **Created:** 2024-01-20 14:32:00

## Lineage
1. Raw data: data/raw/transcripts/, data/raw/compustat/, data/raw/crsp/
2. Interim: data/interim/sample/2024-01-15/
3. Processing: Step 1 (filter) -> Step 2 (match) -> Step 3 (link)
```

### File Naming Conventions

#### For data files:
- Use lowercase with underscores: `ceo_uncertainty.parquet`
- Include date for versioned files: `manifest_2024-01-20.parquet`
- Use descriptive names: NOT `data1.parquet`, `new_data.parquet`

#### For dated directories:
- Use ISO format: `YYYY-MM-DD` (e.g., `2024-01-20`)
- This ensures proper sorting
- Represents the date of creation, not data coverage

### Data File Formats

#### Preferred Formats:
| Use Case | Format | Why |
|----------|--------|-----|
| Tabular data | Parquet | Efficient, preserves types, compressed |
| Small reference | CSV | Human readable, widely compatible |
| Configuration | YAML | Human readable, structured |
| Documentation | Markdown | Human readable, version controllable |

#### Avoid:
- Excel files (except for final deliverables)
- Pickle files (security risk, version dependent)
- JSON for large datasets (inefficient)
- Proprietary formats

### Rationale

#### Why Separate Raw/Interim/Processed?

1. **Immutability of raw data**: Never lose original data
2. **Reproducibility**: Can always regenerate from raw
3. **Clear lineage**: Know which data is source of truth
4. **Storage efficiency**: Interim can be deleted when needed

**Source:** [Cookiecutter Data Science - Data Organization](https://drivendata.co/blog/ccds-v2)

#### Why Dated Subdirectories?

1. **Versioning**: Clear history of data versions
2. **Rollback**: Can use previous version if needed
3. **Auditability**: Know when data was created
4. **Sorting**: ISO format ensures chronological order

#### Why Separate results/ from data/?

1. **Different purpose**: data/ is input, results/ is output
2. **Different git treatment**: results always gitignored
3. **Clear semantics**: Analysts know where to find outputs
4. **Industry standard**: Cookiecutter uses this pattern

---

## 4. Version Management (ARCH-04)

This section defines the version management approach, deprecation strategy, and package versioning conventions.

### Single Active Version Policy

**Principle:** Only ONE version of the codebase is actively maintained at any time.

#### Current Situation (Legacy)

The project currently has parallel V1 and V2 structures:

```
2_Scripts/
├── 3_Financial/       # V1 - Legacy
├── 3_Financial_V2/    # V2 - Current
├── 4_Econometric/     # V1 - Legacy
└── 4_Econometric_V2/  # V2 - Current
```

**Problems with this approach:**
- Confusion about which version to use
- Bug fixes may be needed in multiple places
- Tests may be inconsistent across versions
- Import paths are unclear

#### Target State (Single Version)

```
src/f1d/
├── financial/         # THE active version
│   ├── variables.py
│   └── investment.py
└── econometric/       # THE active version
    ├── regressions.py
    └── diagnostics.py

.___archive/
└── legacy/
    ├── 3_Financial/       # V1 archived
    └── 4_Econometric/     # V1 archived
```

**Benefits:**
- Clear which code is canonical
- No duplicate maintenance burden
- Simpler import paths
- Proper version control via git

### Version Hierarchy

| Version | Status | Location | Maintenance |
|---------|--------|----------|-------------|
| Active (V2 equivalent) | Canonical | `src/f1d/` | Full support |
| Legacy (V1) | Archived | `.___archive/legacy/` | Read-only reference |

**Note:** Do NOT create V3, V4, etc. as parallel directories. Use semantic versioning on the package instead.

### Package Versioning

The F1D package uses semantic versioning (SemVer) with the format `MAJOR.MINOR.PATCH`.

#### Version Location

```python
# src/f1d/__init__.py
__version__ = "5.0.0"
```

#### Version Rules

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking changes | MAJOR | 4.0.0 -> 5.0.0 |
| New features (backward compatible) | MINOR | 5.0.0 -> 5.1.0 |
| Bug fixes (backward compatible) | PATCH | 5.0.0 -> 5.0.1 |

#### Git Tags for Releases

```bash
# Create a release tag
git tag -a v5.0.0 -m "Release version 5.0.0"
git push origin v5.0.0

# List tags
git tag -l

# Show tag details
git show v5.0.0
```

### Deprecation Strategy

#### When to Deprecate

Code should be deprecated when:

1. **Superseded:** Newer implementation exists and is better
2. **Problematic:** Known issues that are not worth fixing
3. **Unused:** No active code depends on it
4. **Inconsistent:** Doesn't match current patterns/standards

#### How to Deprecate

**Step 1: Add deprecation warning (in active code)**

```python
# src/f1d/shared/old_utility.py
import warnings

def old_function():
    """Old implementation - deprecated.

    .. deprecated:: 5.1.0
        Use new_function() instead. Will be removed in 6.0.0.
    """
    warnings.warn(
        "old_function() is deprecated. Use new_function() instead. "
        "Will be removed in version 6.0.0.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... existing implementation
```

**Step 2: Update imports and documentation**

```python
# Update any code using the deprecated function
# from f1d.shared.old_utility import old_function
from f1d.shared.new_utility import new_function
```

**Step 3: Move to archive after deprecation period**

```bash
# After 30+ day deprecation period
mkdir -p .___archive/legacy/deprecated_2024-01/
mv src/f1d/shared/old_utility.py .___archive/legacy/deprecated_2024-01/
```

**Step 4: Update archive manifest**

```json
// .___archive/manifest.json
{
  "archived_items": [
    {
      "original_path": "src/f1d/shared/old_utility.py",
      "archive_path": "legacy/deprecated_2024-01/old_utility.py",
      "date_archived": "2024-02-15",
      "reason": "Superseded by new_utility.py",
      "deprecated_version": "5.1.0",
      "removed_version": "6.0.0"
    }
  ]
}
```

#### Deprecation Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| 1. Announcement | Day 0 | Add deprecation warning |
| 2. Warning Period | 30+ days | Code runs with warnings |
| 3. Archive | After warning period | Move to `.___archive/` |
| 4. Major Version | Next MAJOR release | Remove from codebase |

### Migration Path

#### V1 to V2 Migration (Current to Target)

```
Phase 1: Create src/f1d/ package structure
├── Create src/f1d/ directory
├── Create __init__.py with version
└── Create subpackage directories

Phase 2: Move shared/ utilities
├── Move 2_Scripts/shared/ -> src/f1d/shared/
├── Update imports throughout codebase
└── Run tests to verify

Phase 3: Move stage scripts
├── Move 2_Scripts/3_Financial_V2/ -> src/f1d/financial/
├── Move 2_Scripts/4_Econometric_V2/ -> src/f1d/econometric/
├── Update imports
└── Run tests

Phase 4: Reorganize data directories
├── Move 1_Inputs/ -> data/raw/
├── Reorganize 4_Outputs/ -> data/interim/, data/processed/, results/
└── Update path references

Phase 5: Archive V1 code
├── Move 2_Scripts/3_Financial/ -> .___archive/legacy/
├── Move 2_Scripts/4_Econometric/ -> .___archive/legacy/
└── Update archive manifest

Phase 6: Clean up
├── Remove sys.path hacks
├── Update all imports to use f1d.* pattern
├── Update documentation
└── Verify reproducibility
```

### Breaking Changes

When making breaking changes (MAJOR version bump):

#### Document the Change

```markdown
## Breaking Changes in v6.0.0

### Import Paths Changed
- OLD: `from shared.path_utils import get_latest_output_dir`
- NEW: `from f1d.shared.path_utils import get_latest_output_dir`

### Function Signature Changed
- `run_panel_ols(df, x_vars, y_var)` -> `run_panel_ols(df, formula)`
  - OLD: `run_panel_ols(df, ['size', 'bm'], 'returns')`
  - NEW: `run_panel_ols(df, 'returns ~ size + bm')`
```

#### Provide Migration Script

```python
# scripts/migrate_v5_to_v6.py
"""Migration script for v5 -> v6 upgrade."""

import re
from pathlib import Path

def migrate_imports(file_path):
    """Update imports from v5 to v6 pattern."""
    content = file_path.read_text()

    # Replace old import patterns
    replacements = [
        ('from shared.', 'from f1d.shared.'),
        ('from sample.', 'from f1d.sample.'),
        ('from text.', 'from f1d.text.'),
        ('from financial.', 'from f1d.financial.'),
        ('from econometric.', 'from f1d.econometric.'),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    file_path.write_text(content)
    print(f"Migrated: {file_path}")

if __name__ == "__main__":
    for py_file in Path("scripts").rglob("*.py"):
        migrate_imports(py_file)
```

### Version Compatibility Matrix

| Version | Python | Dependencies | Status |
|---------|--------|--------------|--------|
| v5.0.x | 3.9+ | pandas 2.0+, numpy 1.24+ | Active development |
| v4.0.x | 3.9+ | pandas 1.5+, numpy 1.23+ | Maintenance only |
| v3.0.x | 3.8+ | pandas 1.3+, numpy 1.20+ | Security fixes only |
| v2.0.x | 3.7+ | pandas 1.0+ | End of life |

### Rationale

#### Why Single Active Version?

1. **Reduced confusion:** Developers know which code to use
2. **Lower maintenance:** No parallel bug fixes
3. **Clean codebase:** No duplicate functionality
4. **Git is version control:** Use git history, not directory versions

#### Why Semantic Versioning?

1. **Industry standard:** Widely understood convention
2. **Clear expectations:** Version number indicates change impact
3. **Dependency management:** Tools understand SemVer
4. **Release planning:** Helps plan upgrade paths

#### Why 30-Day Deprecation Period?

1. **Sufficient notice:** Time to update dependent code
2. **Not too long:** Prevents zombie code lingering
3. **Standard practice:** Aligns with Python community norms
4. **Flexibility:** Can extend for critical functionality

---

## 5. Archive and Legacy Code (ARCH-05)

This section defines the archive structure, conventions, and legacy code handling policies.

### Archive Directory Structure

```
.___archive/
├── legacy/                    # V1 scripts and deprecated code
│   ├── 3_Financial/           # V1 financial scripts
│   │   ├── script_31*.py
│   │   └── ...
│   ├── 4_Econometric/         # V1 econometric scripts
│   │   ├── script_41*.py
│   │   └── ...
│   └── deprecated/            # Other deprecated code
│       ├── 2024-01/
│       └── 2024-02/
│
├── backups/                   # Backup files
│   ├── *.bak
│   ├── *_backup.py
│   └── *_old.py
│
├── experiments/               # Abandoned experiments
│   ├── alternative_sample/
│   ├── new_uncertainty_measure/
│   └── ...
│
├── docs/                      # Old documentation versions
│   ├── v1_docs/
│   ├── v2_docs/
│   └── ...
│
├── README.md                  # Archive documentation
├── ARCHIVED.md                # Detailed archive log
└── manifest.json              # Machine-readable archive index
```

### When to Archive

Code should be moved to archive when:

| Reason | Description | Destination |
|--------|-------------|-------------|
| **Replaced** | Newer implementation exists and is active | `legacy/` |
| **Deprecated** | Functionality no longer recommended | `legacy/deprecated/` |
| **Experimental** | Experiment didn't pan out | `experiments/` |
| **Backup** | Temporary backup files older than 30 days | `backups/` |
| **Old docs** | Previous documentation versions | `docs/` |

### Archive Conventions

#### 1. Maintain Original Structure

When archiving, preserve the original directory structure:

```
# BEFORE (active code)
2_Scripts/3_Financial/
├── script_31_filter_data.py
├── script_32_construct_variables.py
└── script_33_merge_data.py

# AFTER (archived)
.___archive/legacy/3_Financial/
├── script_31_filter_data.py
├── script_32_construct_variables.py
└── script_33_merge_data.py
```

#### 2. Add ARCHIVED.md

Every archived item must have an ARCHIVED.md explaining:

```markdown
# Archived: 3_Financial (V1)

**Archive Date:** 2024-02-15
**Original Location:** 2_Scripts/3_Financial/
**Archive Location:** .___archive/legacy/3_Financial/

## Reason for Archival

Replaced by V2 implementation (src/f1d/financial/) which includes:
- Improved variable construction
- Better error handling
- Comprehensive test coverage
- Cleaner API

## Active Replacement

- **Location:** src/f1d/financial/
- **Main module:** variables.py
- **Import path:** from f1d.financial import construct_variables

## Historical Context

V1 financial scripts were created during v1.0 development (2023-2024).
They served their purpose but accumulated technical debt and lacked
proper testing. V2 was created as a clean rewrite following the
new architecture standard.

## Reproducibility

To reproduce results using V1 scripts:
1. Check out git tag: v4.0.0
2. Navigate to 2_Scripts/3_Financial/
3. Run scripts in order: 31 -> 32 -> 33

**Warning:** V1 scripts are not maintained. Use for reference only.

## Key Files

- `script_31_filter_data.py` - Initial data filtering
- `script_32_construct_variables.py` - Variable construction
- `script_33_merge_data.py` - Final merge

## Known Issues

- Missing null checks in script_32
- Hardcoded paths in script_31
- No unit tests
```

#### 3. Update manifest.json

```json
{
  "manifest_version": "1.0",
  "last_updated": "2024-02-15T10:30:00Z",
  "archived_items": [
    {
      "id": "legacy-3-financial",
      "original_path": "2_Scripts/3_Financial/",
      "archive_path": "legacy/3_Financial/",
      "date_archived": "2024-02-15",
      "archived_by": "developer",
      "reason": "Replaced by V2 implementation",
      "replacement_path": "src/f1d/financial/",
      "git_tag": "v4.0.0",
      "notes": "V1 financial scripts - functional but superseded"
    },
    {
      "id": "deprecated-old-utility",
      "original_path": "src/f1d/shared/old_utility.py",
      "archive_path": "legacy/deprecated/2024-02/old_utility.py",
      "date_archived": "2024-02-20",
      "archived_by": "developer",
      "reason": "Deprecated - use new_utility.py instead",
      "replacement_path": "src/f1d/shared/new_utility.py",
      "deprecated_version": "5.1.0",
      "removed_version": "6.0.0",
      "notes": "Had performance issues, replaced with optimized version"
    },
    {
      "id": "experiment-alternative-sample",
      "original_path": "experiments/alternative_sample/",
      "archive_path": "experiments/alternative_sample/",
      "date_archived": "2024-01-10",
      "archived_by": "developer",
      "reason": "Experiment did not improve results",
      "replacement_path": null,
      "notes": "Alternative sampling approach - tested but abandoned"
    }
  ],
  "statistics": {
    "total_items": 3,
    "by_category": {
      "legacy": 1,
      "deprecated": 1,
      "experiments": 1
    }
  }
}
```

### Legacy Code Policy

#### Access Rules

| Action | Allowed | Conditions |
|--------|---------|------------|
| Read archived code | Yes | Reference and reproducibility |
| Run archived code | Yes | Check out appropriate git tag first |
| Modify archived code | No | Archive is read-only |
| Import archived code | No | Use active replacement |
| Delete archived code | No | Git tracks history, archive preserves |

#### Reference Guidelines

When referencing legacy code:

1. **For reproducibility verification:**
   ```python
   # To verify old results match new implementation
   # 1. Check out git tag v4.0.0
   # 2. Run legacy script: 2_Scripts/3_Financial/script_32_construct_variables.py
   # 3. Compare output with new: src/f1d/financial/variables.py
   ```

2. **For understanding history:**
   ```markdown
   # In documentation
   The variable construction approach evolved from V1 (see `.___archive/legacy/3_Financial/`)
   to V2 (see `src/f1d/financial/`) with improved handling of missing values.
   ```

3. **Never for new work:**
   ```python
   # BAD: Importing from archive
   import sys
   sys.path.insert(0, '.___archive/legacy/3_Financial')
   from script_32 import construct_variables  # NO!

   # GOOD: Use active implementation
   from f1d.financial import construct_variables
   ```

### Archive Maintenance

#### Regular Cleanup

**Monthly:** Review `backups/` directory

```bash
# Remove backup files older than 30 days
find .___archive/backups/ -name "*.bak" -mtime +30 -delete
find .___archive/backups/ -name "*_backup.py" -mtime +30 -delete
```

**Quarterly:** Review `experiments/` directory

```bash
# Check if any experiments should be documented or removed
ls -la .___archive/experiments/

# Update ARCHIVED.md for experiments that have conclusions
```

**Annually:** Review entire archive

```bash
# Audit archive manifest
python scripts/audit_archive.py

# Check for items that can be removed (after major version bump)
# Note: Never remove during active major version
```

### Backup File Handling

#### Automatic Backup Detection

Files matching these patterns should be moved to `.___archive/backups/`:

- `*.bak`
- `*_backup.py`
- `*_old.py`
- `*.backup`
- `*~` (editor backups)

#### Backup Script

```python
# scripts/cleanup_backups.py
"""Move backup files to archive."""

import shutil
from pathlib import Path
from datetime import datetime

BACKUP_PATTERNS = ["*.bak", "*_backup.py", "*_old.py", "*.backup"]
ARCHIVE_DIR = Path(".___archive/backups")

def archive_backups(root_dir: Path, dry_run: bool = False):
    """Move backup files to archive directory."""
    for pattern in BACKUP_PATTERNS:
        for backup_file in root_dir.rglob(pattern):
            # Skip if already in archive
            if ".___archive" in str(backup_file):
                continue

            # Create dated subdirectory
            date_dir = ARCHIVE_DIR / datetime.now().strftime("%Y-%m")
            date_dir.mkdir(parents=True, exist_ok=True)

            dest = date_dir / backup_file.name

            if dry_run:
                print(f"Would move: {backup_file} -> {dest}")
            else:
                shutil.move(str(backup_file), str(dest))
                print(f"Archived: {backup_file} -> {dest}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    archive_backups(Path("."), dry_run=args.dry_run)
```

### Experiment Archival

When archiving an experiment:

#### 1. Document the Experiment

```markdown
# Experiment: Alternative Sample Construction

**Status:** Abandoned
**Date:** 2024-01-10
**Duration:** 2 weeks

## Goal

Test alternative sampling approach using propensity score matching
instead of the current industry-size matching.

## Results

- **Sample size:** Reduced by 15%
- **Balance:** Improved on observables
- **Results:** No significant change in main coefficients
- **Decision:** Not worth the complexity and sample size reduction

## Lessons Learned

1. PSM requires more careful specification than expected
2. Industry-size matching is "good enough" for our purposes
3. Sample size is more valuable than marginal balance improvement

## Files

- `alternative_matching.py` - Main experiment script
- `results/` - Experiment outputs
- `notes.md` - Development notes

## Recommendation

Keep current industry-size matching approach. The complexity of PSM
doesn't justify the marginal improvement in balance.
```

#### 2. Clean Up Working Directory

```bash
# Move experiment to archive
mv experiments/alternative_sample .___archive/experiments/

# Update manifest
python scripts/update_archive_manifest.py
```

### Rationale

#### Why Archive Instead of Delete?

1. **Reproducibility:** May need to verify old results
2. **Historical value:** Shows evolution of approach
3. **Learning opportunity:** Future developers can see what was tried
4. **Git is not enough:** Archive explicitly marks code as non-active
5. **Safe recovery:** Can restore if needed

#### Why Maintain Structure?

1. **Findability:** Easy to locate specific archived code
2. **Context preservation:** Directory structure provides context
3. **Minimal disruption:** Original code still works (in archived state)
4. **Clear boundaries:** Archive is obviously separate from active code

#### Why manifest.json?

1. **Machine readable:** Tools can query archive status
2. **Searchability:** Easy to find archived items by metadata
3. **Audit trail:** Track what was archived when and why
4. **Statistics:** Monitor archive growth and categories

---

## Appendix A: Migration Guide

This appendix documents the migration path from the current flat layout to the target src-layout architecture.

### Current State (v5.0)

The project currently uses a flat directory structure with numbered prefixes:

```
F1D/
├── 1_Inputs/                    # Raw data
│   ├── transcripts/
│   ├── compustat/
│   └── crsp/
│
├── 2_Scripts/                   # All source code (flat layout)
│   ├── 1_Sample/                # Stage 1
│   │   ├── script_11_*.py
│   │   ├── script_12_*.py
│   │   └── ...
│   ├── 2_Text/                  # Stage 2
│   │   ├── script_21_*.py
│   │   ├── script_22_*.py
│   │   └── ...
│   ├── 3_Financial/             # Stage 3 (V1 - Legacy)
│   ├── 3_Financial_V2/          # Stage 3 (V2 - Current)
│   │   ├── script_31_*.py
│   │   ├── script_32_*.py
│   │   └── ...
│   ├── 4_Econometric/           # Stage 4 (V1 - Legacy)
│   ├── 4_Econometric_V2/        # Stage 4 (V2 - Current)
│   │   ├── script_41_*.py
│   │   ├── script_42_*.py
│   │   └── ...
│   └── shared/                  # Shared utilities
│       ├── path_utils.py
│       ├── panel_ols.py
│       └── ...
│
├── 3_Logs/                      # Execution logs
│
├── 4_Outputs/                   # All outputs (mixed)
│   ├── sample/                  # Stage outputs
│   ├── text/
│   ├── financial/
│   ├── econometric/
│   └── ...
│
├── config/                      # Configuration
├── docs/                        # Documentation
├── tests/                       # Test suite
├── .___archive/                 # Archive
├── pyproject.toml               # Tool config only
└── README.md
```

### Key Characteristics of Current State

1. **Flat layout:** Scripts directly in `2_Scripts/` subdirectories
2. **Parallel versions:** V1 and V2 directories coexist
3. **Mixed outputs:** `4_Outputs/` contains both intermediate and final data
4. **sys.path hacks:** Many scripts use `sys.path.insert()` for imports
5. **No package structure:** Code is not organized as a Python package

### Target State (v6.0+)

The target state uses src-layout with proper package structure:

```
F1D/
├── src/f1d/                     # Main package (src-layout)
│   ├── __init__.py
│   ├── sample/
│   ├── text/
│   ├── financial/
│   ├── econometric/
│   └── shared/
│
├── data/                        # Data directory
│   ├── raw/                     # (from 1_Inputs/)
│   ├── interim/                 # (from 4_Outputs/ intermediate)
│   ├── processed/               # (from 4_Outputs/ final)
│   └── external/
│
├── results/                     # Analysis outputs
│   ├── figures/
│   ├── tables/
│   └── reports/
│
├── logs/                        # (from 3_Logs/)
├── config/
├── docs/
├── tests/
├── .___archive/
│   └── legacy/                  # V1 scripts
├── pyproject.toml               # Full config
└── README.md
```

### Key Differences

| Aspect | Current | Target |
|--------|---------|--------|
| **Layout** | Flat | src-layout |
| **Package** | None (scripts only) | f1d package with __init__.py |
| **Versions** | V1 and V2 parallel | Single active version |
| **Data** | Mixed in 4_Outputs/ | Separated by lifecycle |
| **Imports** | sys.path hacks | Proper package imports |
| **Results** | In 4_Outputs/ | Separate results/ directory |

### Migration Phases

#### Phase 1: Create Package Structure

**Goal:** Set up the basic src-layout package structure

**Steps:**
```bash
# Create src directory structure
mkdir -p src/f1d/sample
mkdir -p src/f1d/text
mkdir -p src/f1d/financial
mkdir -p src/f1d/econometric
mkdir -p src/f1d/shared/observability

# Create __init__.py files
touch src/f1d/__init__.py
touch src/f1d/sample/__init__.py
touch src/f1d/text/__init__.py
touch src/f1d/financial/__init__.py
touch src/f1d/econometric/__init__.py
touch src/f1d/shared/__init__.py
touch src/f1d/shared/observability/__init__.py
```

**Verification:**
```bash
# Verify package can be imported
python -c "import f1d; print(f1d.__version__)"
```

**Commit:** `feat(65-01): create src/f1d package structure`

---

#### Phase 2: Move Shared Utilities

**Goal:** Move shared utilities to the package

**Steps:**
```bash
# Move shared utilities
cp -r 2_Scripts/shared/*.py src/f1d/shared/

# Update __init__.py files
# Add docstrings, __all__, version
```

**Code changes:**
```python
# src/f1d/__init__.py
"""F1D Data Processing Pipeline."""

__version__ = "6.0.0"

from f1d.shared.path_utils import get_latest_output_dir

__all__ = ["get_latest_output_dir"]

# src/f1d/shared/__init__.py
"""Shared utilities for F1D pipeline."""

from f1d.shared.path_utils import get_latest_output_dir

__all__ = ["get_latest_output_dir"]
```

**Update imports in active code:**
```python
# OLD
import sys
sys.path.insert(0, '2_Scripts')
from shared.path_utils import get_latest_output_dir

# NEW
from f1d.shared.path_utils import get_latest_output_dir
```

**Verification:**
```bash
# Run tests
pytest tests/

# Verify imports work
python -c "from f1d.shared.path_utils import get_latest_output_dir"
```

**Commit:** `refactor(65-01): move shared utilities to src/f1d/shared/`

---

#### Phase 3: Move Stage Scripts

**Goal:** Move V2 stage scripts to package subpackages

**Steps (for each stage):**

**Financial (Stage 3):**
```bash
# Move V2 financial scripts
cp 2_Scripts/3_Financial_V2/script_31_*.py src/f1d/financial/
cp 2_Scripts/3_Financial_V2/script_32_*.py src/f1d/financial/

# Rename scripts to modules
mv src/f1d/financial/script_31_filter_data.py src/f1d/financial/filter_data.py
mv src/f1d/financial/script_32_construct_variables.py src/f1d/financial/variables.py

# Update __init__.py
```

**Econometric (Stage 4):**
```bash
# Similar process
cp 2_Scripts/4_Econometric_V2/script_41_*.py src/f1d/econometric/
cp 2_Scripts/4_Econometric_V2/script_42_*.py src/f1d/econometric/
```

**Update imports:**
```python
# OLD
sys.path.insert(0, '2_Scripts/3_Financial_V2')
from script_32_construct_variables import construct_variables

# NEW
from f1d.financial.variables import construct_variables
```

**Verification:**
```bash
# Run stage scripts to verify
python -m f1d.financial.variables

# Run tests
pytest tests/
```

**Commit:** `refactor(65-01): move financial and econometric modules to package`

---

#### Phase 4: Reorganize Data Directories

**Goal:** Reorganize data according to lifecycle stages

**Steps:**
```bash
# Create new structure
mkdir -p data/raw
mkdir -p data/interim
mkdir -p data/processed
mkdir -p data/external
mkdir -p results/figures
mkdir -p results/tables
mkdir -p results/reports

# Move raw data
mv 1_Inputs/* data/raw/

# Separate 4_Outputs into interim and processed
# (Manual review required - categorize each subdirectory)

# Move logs
mv 3_Logs logs
```

**Update path references in code:**
```python
# OLD
INPUT_DIR = Path("1_Inputs")
OUTPUT_DIR = Path("4_Outputs")
LOG_DIR = Path("3_Logs")

# NEW
DATA_RAW = Path("data/raw")
DATA_INTERIM = Path("data/interim")
DATA_PROCESSED = Path("data/processed")
RESULTS = Path("results")
LOG_DIR = Path("logs")
```

**Verification:**
```bash
# Verify data moved correctly
ls -la data/raw/
ls -la data/processed/

# Run scripts with new paths
python -m f1d.financial.variables
```

**Commit:** `refactor(65-01): reorganize data directories by lifecycle`

---

#### Phase 5: Archive V1 Code

**Goal:** Move V1 scripts to archive

**Steps:**
```bash
# Create archive structure
mkdir -p .___archive/legacy

# Move V1 directories
mv 2_Scripts/3_Financial .___archive/legacy/
mv 2_Scripts/4_Econometric .___archive/legacy/

# Create ARCHIVED.md
cat > .___archive/legacy/ARCHIVED.md << 'EOF'
# Archived V1 Scripts

**Archive Date:** 2024-XX-XX
**Reason:** Replaced by V2 implementation in src/f1d/

## Contents
- 3_Financial/ - V1 financial scripts
- 4_Econometric/ - V1 econometric scripts

## Active Replacement
See src/f1d/financial/ and src/f1d/econometric/
EOF

# Update manifest.json
python scripts/update_archive_manifest.py
```

**Verification:**
```bash
# Verify archived
ls -la .___archive/legacy/

# Verify still accessible (read-only)
cat .___archive/legacy/3_Financial/script_31_filter_data.py
```

**Commit:** `chore(65-01): archive V1 scripts to .___archive/legacy/`

---

#### Phase 6: Clean Up and Finalize

**Goal:** Remove sys.path hacks and finalize structure

**Steps:**
```bash
# Remove old directories (after verification)
rm -rf 2_Scripts/
rm -rf 4_Outputs/
rm -rf 1_Inputs/
rm -rf 3_Logs/

# Update pyproject.toml
# Add build system and package configuration
```

**Update pyproject.toml:**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "f1d"
version = "6.0.0"
description = "F1D Data Processing Pipeline for CEO Uncertainty Research"
requires-python = ">=3.9"

[tool.setuptools.packages.find]
where = ["src"]
```

**Clean up imports:**
```bash
# Remove all sys.path.insert statements
grep -r "sys.path.insert" src/ --files-with-matches | xargs sed -i '/sys.path.insert/d'

# Update all imports to use f1d.* pattern
# (Use migration script from Section 4)
```

**Verification:**
```bash
# Run full test suite
pytest tests/ -v

# Verify package installation
pip install -e .
python -c "from f1d import get_latest_output_dir; print('OK')"

# Run complete pipeline
python scripts/run_pipeline.py

# Verify reproducibility
# Compare outputs with v5.0 baseline
```

**Commit:** `refactor(65-01): complete migration to src-layout architecture`

---

### Breaking Changes

The migration introduces the following breaking changes:

#### 1. Import Paths

| Old | New |
|-----|-----|
| `from shared.path_utils import ...` | `from f1d.shared.path_utils import ...` |
| `from script_32_construct_variables import ...` | `from f1d.financial.variables import ...` |
| `sys.path.insert(0, '2_Scripts')` | (Removed - use package imports) |

#### 2. Data Paths

| Old | New |
|-----|-----|
| `1_Inputs/` | `data/raw/` |
| `4_Outputs/sample/` | `data/interim/sample/` or `data/processed/sample/` |
| `4_Outputs/figures/` | `results/figures/` |
| `3_Logs/` | `logs/` |

#### 3. Script Execution

| Old | New |
|-----|-----|
| `python 2_Scripts/3_Financial_V2/script_32.py` | `python -m f1d.financial.variables` |

### Compatibility Notes

#### Maintaining Reproducibility During Transition

1. **Git tags:** Create tag before migration starts
   ```bash
   git tag -a v5.0-final -m "Last version before migration"
   git push origin v5.0-final
   ```

2. **Parallel testing:** Run both old and new versions
   ```bash
   # Old version
   git checkout v5.0-final
   python 2_Scripts/3_Financial_V2/script_32.py

   # New version
   git checkout master
   python -m f1d.financial.variables

   # Compare outputs
   diff 4_Outputs/financial/ data/processed/financial/
   ```

3. **Gradual migration:** Migrate one stage at a time
   - Migrate shared utilities first
   - Then migrate one stage (e.g., financial)
   - Verify all outputs match
   - Continue with next stage

#### Testing Strategy

1. **Unit tests:** Update imports, verify all pass
2. **Integration tests:** Verify end-to-end pipeline
3. **Regression tests:** Compare outputs with baseline
4. **Performance tests:** Verify no degradation

### Rollback Plan

If issues arise during migration:

```bash
# Rollback to pre-migration state
git checkout v5.0-final

# Or revert specific migration commit
git revert <commit-hash>

# Restore data directories (if needed)
git checkout v5.0-final -- 1_Inputs/ 4_Outputs/
```

### Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Create structure | 1 day | None |
| Phase 2: Move shared | 2 days | Phase 1 |
| Phase 3: Move stages | 1 week | Phase 2 |
| Phase 4: Reorganize data | 2 days | Phase 3 |
| Phase 5: Archive V1 | 1 day | Phase 3 |
| Phase 6: Clean up | 2 days | Phases 4, 5 |
| **Total** | **~2 weeks** | |

### Post-Migration Tasks

After migration is complete:

1. **Update documentation:**
   - README.md with new structure
   - Script usage examples
   - Import examples

2. **Update CI/CD:**
   - Add package installation step
   - Update test commands

3. **Team communication:**
   - Announce new structure
   - Provide migration guide for local clones
   - Update onboarding docs

4. **Monitor:**
   - Watch for import errors
   - Verify all pipelines still work
   - Address any path issues

---

## Appendix B: Related Standards

This architecture standard is part of a suite of standards:

| Standard | Phase | Purpose | Status |
|----------|-------|---------|--------|
| ARCHITECTURE_STANDARD.md | 65 | Folder structure, module organization | This document |
| NAMING_STANDARD.md | 66 | File, variable, function naming | Planned |
| CONFIG_STANDARD.md | 67 | Configuration file patterns | Planned |
| DOC_STANDARD.md | 68 | Documentation templates | Planned |

**Dependencies:**
- ARCHITECTURE_STANDARD.md is the foundation
- Other standards build upon this structure
- Changes here may affect dependent standards

---

## References

- [Python Packaging Authority - src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Cookiecutter Data Science V2](https://drivendata.co/blog/ccds-v2)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [Semantic Versioning](https://semver.org/)
- [FAIR Principles](https://www.go-fair.org/fair-principles/)
