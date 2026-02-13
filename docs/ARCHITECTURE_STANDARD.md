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

## References

- [Python Packaging Authority - src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Cookiecutter Data Science V2](https://drivendata.co/blog/ccds-v2)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [Semantic Versioning](https://semver.org/)
- [FAIR Principles](https://www.go-fair.org/fair-principles/)
