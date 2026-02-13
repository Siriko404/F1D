# F1D Code Quality Standard

**Version:** 5.0
**Last Updated:** 2026-02-13
**Status:** DEFINITION - Implementation deferred to v6.0+
**Milestone:** v5.0 Architecture Standard Definition

---

## Purpose

This document defines the naming conventions and code quality standards for the F1D (Financial Text Analysis) data processing pipeline. It builds on the foundation established in ARCHITECTURE_STANDARD.md (folder structure, module organization) and ensures:

- **Readability:** Code is read more often than written
- **Consistency:** Same patterns applied across the codebase
- **Industry Alignment:** PEP 8, Google Style Guide compliance
- **Tool Support:** ruff, mypy enforcement capabilities

This is a **DEFINITION document**. The standards described here represent the target quality standards that will be implemented in v6.0+. Current code may not fully comply with all standards.

---

## Document Structure

This standard is organized into 6 main sections:

1. **Naming Conventions** (NAM-01 through NAM-05): Script, module, function, variable, and output file naming
2. **Docstring Standard** (CODE-01): Google-style docstrings for functions, methods, and modules
3. **Type Hint Coverage** (CODE-02): Type hint requirements per module tier
4. **Import Organization** (CODE-03): PEP 8 import order and conventions
5. **Error Handling** (CODE-04): Custom exceptions, no bare except policy
6. **Function Size and Module Organization** (CODE-05): Size limits and organization rules

Additionally:
- **Appendix A**: Quick Reference Card
- **Appendix B**: Related Standards

---

## How to Use This Standard

### For New Development (v6.0+)

1. Follow all naming conventions (Section 1)
2. Use Google-style docstrings (Section 2)
3. Add type hints per tier requirements (Section 3)
4. Organize imports per PEP 8 (Section 4)
5. Handle errors with custom exceptions (Section 5)
6. Keep functions focused and small (Section 6)

### For Current Development (v5.0)

1. Use this standard as reference for understanding target quality
2. New code should align with these patterns where feasible
3. Document deviations from the standard
4. Plan for migration to full compliance

### For Code Review

1. Check naming conventions compliance
2. Verify docstrings follow Google-style
3. Ensure type hints on Tier 1 and Tier 2 modules
4. Confirm import organization
5. Check error handling patterns
6. Review function size and complexity

---

## Design Principles

### 1. Readability

Code is read far more often than it is written. Every convention in this standard prioritizes clarity and comprehension:

- **Descriptive names:** Names should reveal intent
- **Consistent patterns:** Same concept, same name
- **Documented behavior:** Docstrings explain what and why
- **Visual structure:** Whitespace and organization aid scanning

**Implementation:**
- Use full words, not abbreviations (except standard ones)
- Follow established naming patterns
- Write self-documenting code with clear docstrings
- Organize code logically

### 2. Consistency

The same patterns should be applied uniformly across the entire codebase:

- **Naming:** Same naming convention for same entity types
- **Formatting:** Same indentation, spacing, line length
- **Documentation:** Same docstring structure everywhere
- **Error handling:** Same exception patterns throughout

**Implementation:**
- Follow this standard without deviation
- Use automated tools (ruff, mypy) for enforcement
- Review for consistency in code review
- Update existing code to match patterns

### 3. Industry Alignment

Follow recognized industry standards to ensure:

- **Familiarity:** Developers recognize patterns
- **Tooling:** IDEs and linters understand conventions
- **Portability:** Code style transfers to other projects
- **Best practices:** Benefit from community wisdom

**Implementation:**
- PEP 8 for style conventions
- Google Style Guide for docstrings
- PEP 484 for type hints
- PEP 760 for exception handling

### 4. Tool Support

Standards should be enforceable with automated tools:

- **ruff:** Linting and formatting
- **mypy:** Type checking
- **pytest:** Testing framework
- **pre-commit:** Git hook automation

**Implementation:**
- Configure tools in pyproject.toml
- Run checks in CI pipeline
- Use pre-commit hooks locally
- Fix violations immediately

---

## Standards Hierarchy

This code quality standard builds on the architecture foundation:

```
ARCHITECTURE_STANDARD.md (Phase 65)
    ├── Defines: Folder structure, module organization, data lifecycle
    │
    └── Referenced by:
        ├── CODE_QUALITY_STANDARD.md (this document)
        │   └── Builds on: Module tiers, import conventions, __init__.py patterns
        │
        ├── CONFIG_STANDARD.md (Phase 67 - Planned)
        │   └── Builds on: config/ directory structure
        │
        └── DOC_STANDARD.md (Phase 68 - Planned)
            └── Builds on: docs/ directory structure
```

Changes to ARCHITECTURE_STANDARD.md may require updates to this document.

---

## Scope and Exclusions

### In Scope

- Naming conventions for all code entities
- Docstring format and requirements
- Type hint coverage requirements
- Import organization patterns
- Error handling conventions
- Function and module organization

### Out of Scope

- Folder structure (see ARCHITECTURE_STANDARD.md)
- Configuration file patterns (Phase 67)
- Documentation templates (Phase 68)
- CI/CD pipeline configuration
- Deployment procedures

---

## Requirements Overview

This document defines the following requirements:

### Naming Conventions

| Requirement | Description |
|-------------|-------------|
| **NAM-01** | Script naming convention (Stage.Step_Description.py) |
| **NAM-02** | Module naming convention (snake_case) |
| **NAM-03** | Function/class naming (snake_case/PascalCase) |
| **NAM-04** | Variable naming patterns |
| **NAM-05** | Output file naming patterns |

### Code Quality Standards

| Requirement | Description |
|-------------|-------------|
| **CODE-01** | Docstring standard (Google-style) |
| **CODE-02** | Type hint coverage per tier |
| **CODE-03** | Import organization (stdlib -> third-party -> local) |
| **CODE-04** | Error handling (custom exceptions, no bare except) |
| **CODE-05** | Function size limits and module organization |

---

## 1. Naming Conventions

This section defines naming conventions for all code entities in the F1D project. Consistent naming improves code readability and maintainability.

### 1.1 Script Naming Convention (NAM-01)

**Pattern:** `{Stage}.{Step}_{Description}.py`

| Component | Format | Example |
|-----------|--------|---------|
| Stage | Single digit (1-4) | 1, 2, 3, 4 |
| Step | Single decimal | 0, 1, 2, etc. |
| Description | PascalCase | BuildSampleManifest, H1Variables |
| Separator | Underscore after step | 1.0_BuildSampleManifest.py |

**Examples from codebase:**

```python
# Stage 1: Sample Construction
1.0_BuildSampleManifest.py    # Orchestrator script
1.1_CleanMetadata.py          # Metadata cleaning

# Stage 3: Financial Variables
3.1_H1Variables.py            # H1 hypothesis variables
3.2_H2Variables.py            # H2 hypothesis variables

# Stage 4: Econometric Analysis
4.11_H9_Regression.py         # H9 regression analysis
4.12_H10_Regression.py        # H10 regression analysis
```

**Naming Rules:**

1. **Stage numbers:**
   - Stage 1: Sample construction (manifest, filtering)
   - Stage 2: Text processing (tokenization, uncertainty measures)
   - Stage 3: Financial features (variable construction)
   - Stage 4: Econometric analysis (regressions, diagnostics)

2. **Step numbers:**
   - Use .0 for orchestrator or main entry scripts
   - Use sequential decimals (.1, .2, .3) for processing steps
   - Keep step numbers stable - don't renumber

3. **Description:**
   - Use PascalCase (capitalized words)
   - Start with verb for actions (Build, Process, Calculate)
   - Use noun for outputs (H1Variables, RegressionResults)
   - Be specific - avoid vague names like "Process" or "Utils"

**Anti-patterns to avoid:**

```python
# WRONG: Missing step number
BuildSampleManifest.py

# WRONG: Using hyphens instead of underscores
1.0-Build-Sample-Manifest.py

# WRONG: snake_case in description
1.0_build_sample_manifest.py

# WRONG: Vague description
1.0_Process.py

# WRONG: Abbreviated names
1.0_BldManifest.py
```

**Rationale:**

The Stage.Step prefix provides:
- **Natural sort order:** Scripts list in pipeline sequence
- **Immediate context:** Know where script fits from filename
- **Dependency clarity:** Higher step numbers depend on lower ones
- **Orchestrator identification:** .0 suffix marks entry points

### 1.2 Module Naming Convention (NAM-02)

**Pattern:** `{descriptive_name}.py` using snake_case

| Element | Convention | Example |
|---------|------------|---------|
| Module files | snake_case | `panel_ols.py`, `path_utils.py` |
| Package directories | snake_case | `shared/`, `observability/` |
| Version variants | lowercase v + number | `v1/`, `v2/` |

**Naming Rules:**

1. **Use full words:**
   ```python
   # GOOD
   panel_ols.py
   path_utils.py
   data_validation.py

   # BAD
   pnl_ols.py        # Abbreviated
   pu.py             # Too abbreviated
   dv.py             # Unreadable
   ```

2. **Use underscores for word separation:**
   ```python
   # GOOD
   regression_diagnostics.py
   uncertainty_measures.py

   # BAD
   regressionDiagnostics.py   # camelCase
   Regression_Diagnostics.py  # Mixed case
   regressiondiagnostics.py   # No separator
   ```

3. **Be specific and descriptive:**
   ```python
   # GOOD
   investment_metrics.py
   collinearity_diagnostics.py

   # BAD
   metrics.py         # Too vague
   utils.py           # Catch-all, avoid
   helpers.py         # Non-specific
   ```

**Package directory naming:**

```python
# GOOD: Clear purpose
shared/              # Cross-cutting utilities
observability/       # Logging and monitoring
financial/           # Financial feature construction

# BAD: Vague or inconsistent
utils/               # Too generic
misc/                # "Miscellaneous" is a code smell
common_stuff/        # Informal naming
```

**Version variant naming:**

```python
# Version variants become subpackages
src/f1d/financial/
├── v1/              # V1 methodology (active variant)
│   ├── variables.py
│   └── investment.py
└── v2/              # V2 methodology (active variant)
    ├── variables.py
    └── investment.py
```

**Anti-patterns to avoid:**

| Anti-pattern | Example | Problem |
|--------------|---------|---------|
| camelCase | `panelOls.py` | Not PEP 8 compliant |
| Abbreviated | `pu.py`, `ut.py` | Unclear purpose |
| Mixed conventions | `Panel_OLS.py` | Inconsistent style |
| Generic names | `utils.py`, `common.py` | No indication of content |
| Numbers in names | `utils2.py`, `helpers_new.py` | Sign of poor organization |

**Rationale:**

snake_case naming follows PEP 8 and provides:
- **PEP 8 compliance:** Standard Python convention
- **Readability:** Underscores separate words clearly
- **Import clarity:** `from path_utils import ...` reads naturally
- **IDE support:** Autocomplete works better with distinct names

### 1.3 Function/Class Naming Convention (NAM-03)

**Source:** [PEP 8 - Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions)

| Element | Convention | Example |
|---------|------------|---------|
| Functions | snake_case | `get_latest_output_dir()`, `run_panel_ols()` |
| Methods | snake_case | `validate_data()`, `transform_column()` |
| Classes | PascalCase | `CollinearityError`, `DualWriter` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Private functions | _leading_underscore | `_check_thin_cells()`, `_format_table()` |
| Type aliases | PascalCase | `DataFrameDict`, `VariableList` |

#### Function Naming

```python
# GOOD: snake_case, verb_noun pattern
def get_latest_output_dir(base_path: Path) -> Path:
    ...

def run_panel_ols(df: pd.DataFrame, dependent: str) -> Dict[str, Any]:
    ...

def construct_h1_variables(manifest: pd.DataFrame) -> pd.DataFrame:
    ...

# GOOD: Boolean functions use is_, has_, should_ prefixes
def is_valid_gvkey(gvkey: str) -> bool:
    ...

def has_missing_values(df: pd.DataFrame) -> bool:
    ...

def should_skip_firm(firm_data: pd.Series) -> bool:
    ...

# BAD: camelCase
def getLatestOutputDir():    # Wrong convention
    ...

# BAD: Missing verb
def latest_output_dir():     # Unclear if getter or something else
    ...

# BAD: Too abbreviated
def get_lod():               # What is "lod"?
    ...
```

#### Class Naming

```python
# GOOD: PascalCase, noun pattern
class CollinearityError(Exception):
    ...

class DualWriter:
    ...

class PanelOLSResults:
    ...

# GOOD: Exception classes end with "Error"
class DataValidationError(Exception):
    ...

class OutputResolutionError(Exception):
    ...

# BAD: snake_case
class collinearity_error:    # Wrong convention
    ...

# BAD: Missing context
class Error:                 # Too generic
    ...

# BAD: Inconsistent suffix
class DataValidation(Exception):  # Should be DataValidationError
    ...
```

#### Constants

```python
# GOOD: UPPER_SNAKE_CASE at module level
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
CACHE_DIRECTORY = Path(".cache")
SUPPORTED_FORMATS = ["parquet", "csv", "feather"]

# GOOD: Grouped constants
# Panel OLS settings
PANEL_OLS_DEFAULT_ENTITY_EFFECTS = True
PANEL_OLS_DEFAULT_TIME_EFFECTS = True
PANEL_OLS_CLUSTER_BY = "entity"

# BAD: camelCase or snake_case
maxRetries = 3              # Should be MAX_RETRIES
default_timeout = 30        # Should be DEFAULT_TIMEOUT

# BAD: "Magic numbers" without constants
time.sleep(30)              # What is 30? Use DEFAULT_TIMEOUT
```

#### Private Functions

```python
# GOOD: Leading underscore for internal functions
def _check_thin_cells(df: pd.DataFrame, threshold: int) -> List[str]:
    """Internal function to check for thin cells."""
    ...

def _format_coefficient_table(results: Dict) -> pd.DataFrame:
    """Internal function to format coefficient output."""
    ...

def _validate_column_types(df: pd.DataFrame) -> None:
    """Internal validation - not part of public API."""
    ...

# Usage: Private functions are called by public functions
def run_panel_ols(df: pd.DataFrame) -> Dict:
    """Public API function."""
    _validate_column_types(df)       # Internal call
    results = _estimate_model(df)    # Internal call
    return _format_coefficient_table(results)  # Internal call
```

#### Type Aliases

```python
# GOOD: PascalCase for type aliases
from typing import Dict, List, Any

DataFrameDict = Dict[str, pd.DataFrame]
VariableList = List[str]
RegressionResults = Dict[str, Any]

# Usage
def run_regressions(
    data: DataFrameDict,
    variables: VariableList,
) -> RegressionResults:
    ...
```

**Rationale:**

- **snake_case for functions:** PEP 8 standard, reads naturally
- **PascalCase for classes:** Distinguishes types from functions
- **UPPER_SNAKE_CASE for constants:** Visual distinction for fixed values
- **Leading underscore for private:** Convention for internal implementation

### 1.4 Variable Naming Patterns (NAM-04)

Variable names should be descriptive and follow context-specific patterns.

| Context | Pattern | Example |
|---------|---------|---------|
| DataFrame | descriptive_df or just descriptive | `df`, `manifest_df`, `panel_df` |
| Series | descriptive_s or just descriptive | `returns_s`, `uncertainty` |
| Counts | n_ prefix or _count suffix | `n_firms`, `record_count` |
| Indices | i_, j_, k_ for simple loops | `i_row`, `j_col` |
| Boolean | is_, has_, should_ prefixes | `is_valid`, `has_missing`, `should_retry` |
| Paths | _path or _dir suffix | `output_path`, `input_dir` |
| Config | _config suffix | `model_config`, `logging_config` |

#### DataFrame Variables

```python
# GOOD: Clear, descriptive names
manifest_df = pd.read_parquet("manifest.parquet")
panel_df = construct_panel_data(manifest_df)
results_df = run_regressions(panel_df)

# GOOD: Short names acceptable when context is clear
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process input dataframe."""
    # Here 'df' is fine - context is clear
    return df.dropna()

# BAD: Single letters in broad scope
d = pd.read_parquet("data.parquet")  # What is 'd'?
x = d.groupby("gvkey")               # Confusing

# BAD: Numbered variables
df1 = load_data()
df2 = process_data(df1)
df3 = validate_data(df2)  # Use descriptive names instead
```

#### Series Variables

```python
# GOOD: Descriptive with optional _s suffix
uncertainty = df["uncertainty_measure"]
returns_s = df["stock_returns"]

# GOOD: Clear variable purpose
ceo_uncertainty = calculate_uncertainty_score(transcript)
firm_sizes = df.groupby("gvkey")["size"].mean()

# BAD: Cryptic names
u = df["uncertainty"]  # Too short
s1 = df["returns"]     # Numbered series
```

#### Count Variables

```python
# GOOD: n_ prefix for counts
n_firms = df["gvkey"].nunique()
n_observations = len(df)
n_missing = df["uncertainty"].isna().sum()

# GOOD: _count suffix also acceptable
record_count = len(df)
missing_count = df.isna().sum().sum()

# Context-specific naming
n_treated = (df["treatment"] == 1).sum()
n_control = (df["treatment"] == 0).sum()
```

#### Index Variables

```python
# GOOD: i_, j_, k_ for simple loops
for i_row in range(len(df)):
    ...

for i, (gvkey, group) in enumerate(df.groupby("gvkey")):
    ...

# GOOD: More descriptive for nested loops
for i_firm, firm_data in firms.items():
    for i_year, year_data in firm_data.items():
        ...

# BAD: Single letters in complex loops
for i in firms:
    for j in i:     # Confusing - what is j?
        for k in j: # Even more confusing
            ...
```

#### Boolean Variables

```python
# GOOD: is_, has_, should_ prefixes
is_valid = validate_data(df)
has_missing = df.isna().any().any()
should_retry = attempt < MAX_RETRIES

# GOOD: Questions that can be answered yes/no
data_loaded = df is not None
regression_converged = results.converged
model_significant = results.p_value < 0.05

# BAD: Negative naming
is_not_valid = not validate_data(df)  # Confusing double negatives
if not is_not_valid:  # Very confusing
    ...
```

#### Path Variables

```python
# GOOD: _path or _dir suffix
output_path = Path("4_Outputs") / "results.parquet"
input_dir = Path("1_Inputs")
log_path = Path("3_Logs") / "execution.log"

# GOOD: Clear variable purpose
manifest_path = get_latest_output_dir("manifest")
results_dir = ensure_output_dir("regressions")

# BAD: Ambiguous names
file = "data.parquet"  # Is this a path or filename?
location = Path("data")  # File or directory?
```

#### Configuration Variables

```python
# GOOD: _config suffix
model_config = {
    "entity_effects": True,
    "time_effects": True,
    "cluster_se": True,
}

logging_config = load_yaml("config/logging.yaml")

# GOOD: Descriptive config names
regression_settings = load_regression_config()
data_paths = load_path_config()
```

**Rationale:**

- **Consistent patterns:** Same variable type uses same naming pattern
- **Context awareness:** Short names acceptable in narrow scope
- **Self-documenting:** Variable name hints at type and purpose
- **IDE-friendly:** Autocomplete suggests appropriate patterns

### 1.5 Output File Naming Patterns (NAM-05)

Output files should follow consistent naming patterns that convey context, timing, and integrity.

| Component | Format | Example |
|-----------|--------|---------|
| Timestamp | ISO 8601 compact | `20260213_143052` |
| Date-only | ISO 8601 | `2026-02-13` |
| Checksum | SHA-256 (12 chars) | `a3f2b8c91d2f` |
| Version | v + number | `v1`, `v2` |

#### Directory Naming

```python
# GOOD: ISO 8601 date format for directories
4_Outputs/1.0_BuildSampleManifest/2026-02-13-143052/
4_Outputs/3.1_H1Variables/2026-02-13/
data/processed/manifest/2026-02-13/

# Pattern: {script_name}/{YYYY-MM-DD}[-{HHMMSS}]

# With timestamp (for frequent runs)
output_dir = base_dir / "2026-02-13-143052"

# Date-only (for daily runs)
output_dir = base_dir / "2026-02-13"
```

#### File Naming

```python
# GOOD: Descriptive with date
master_manifest_20260213.parquet
h1_regression_results_20260213.parquet
uncertainty_scores_2026-02-13.parquet

# GOOD: With checksum for data integrity
manifest_20260213_a3f2b8c91d2f.parquet
panel_data_2026-02-13_b4c5d6e7f8g9.parquet

# GOOD: With version suffix
regression_results_v1.parquet
regression_results_v2.parquet

# Pattern examples
# {descriptor}_{YYYYMMDD}.{ext}
# {descriptor}_{YYYYMMDD}_{checksum}.{ext}
# {descriptor}_{version}.{ext}
```

#### Complete Path Examples

```python
# Standard output directory structure
4_Outputs/
├── 1.0_BuildSampleManifest/
│   └── 2026-02-13-143052/
│       ├── master_manifest.parquet
│       ├── stats.json
│       └── execution.log
│
├── 3.1_H1Variables/
│   └── 2026-02-13/
│       ├── h1_variables.parquet
│       └── variable_summary.yaml
│
└── 4.11_H9_Regression/
    └── 2026-02-13-150000/
        ├── regression_results.parquet
        ├── coefficient_table.csv
        └── diagnostics.json
```

#### Naming Rules

1. **Use ISO 8601 dates:**
   - Directories: `YYYY-MM-DD` or `YYYY-MM-DD-HHMMSS`
   - Files: `YYYYMMDD` (compact) or `YYYY-MM-DD`
   - Enables natural chronological sorting

2. **Include script identifier:**
   - Directory name includes script: `4_Outputs/1.0_BuildSampleManifest/`
   - Traces output back to source

3. **Checksums for data integrity:**
   - Use SHA-256 truncated to 12 characters
   - Add when data integrity is critical
   - Enables verification without full comparison

4. **Version suffixes for variants:**
   - Use `v1`, `v2`, etc. for methodology variants
   - Distinguish processing approaches
   - Keep version numbers stable

**Anti-patterns to avoid:**

```python
# BAD: Non-ISO date format
output_13-02-2026.parquet    # Ambiguous (DD-MM or MM-DD?)
results_Feb13.parquet        # Not sortable

# BAD: No date or version
data.parquet                 # Which version?
results_latest.parquet       # Overwrites previous

# BAD: Timestamps that aren't sortable
outputs/13022026/            # DDMMYYYY - wrong order
outputs/2026-13-02/          # YYYY-DD-MM - wrong order

# BAD: Spaces in filenames
regression results.parquet   # Breaks scripts, URLs
```

#### Code Examples for Output Naming

```python
from datetime import datetime
from pathlib import Path
import hashlib


def get_output_dir(script_name: str, base_dir: Path = Path("4_Outputs")) -> Path:
    """Create timestamped output directory.

    Args:
        script_name: Script identifier (e.g., "1.0_BuildSampleManifest")
        base_dir: Base output directory

    Returns:
        Path to created output directory
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    output_dir = base_dir / script_name / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def compute_checksum(file_path: Path, length: int = 12) -> str:
    """Compute SHA-256 checksum truncated to specified length.

    Args:
        file_path: Path to file
        length: Number of checksum characters to return

    Returns:
        Truncated hex digest string
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:length]


def save_with_checksum(
    df: pd.DataFrame,
    base_name: str,
    output_dir: Path,
) -> Path:
    """Save DataFrame with checksum in filename.

    Args:
        df: DataFrame to save
        base_name: Base filename without extension
        output_dir: Output directory

    Returns:
        Path to saved file
    """
    # Save to temporary file first
    temp_path = output_dir / f"{base_name}_temp.parquet"
    df.to_parquet(temp_path)

    # Compute checksum
    checksum = compute_checksum(temp_path)

    # Rename with checksum
    date_str = datetime.now().strftime("%Y%m%d")
    final_path = output_dir / f"{base_name}_{date_str}_{checksum}.parquet"
    temp_path.rename(final_path)

    return final_path
```

**Rationale:**

- **ISO 8601 dates:** Unambiguous, sortable, international standard
- **Script identifiers:** Trace outputs back to source
- **Checksums:** Verify data integrity without full comparison
- **Version suffixes:** Distinguish methodology variants
- **No spaces:** Compatibility with scripts, URLs, all systems

### 1.6 Naming Conventions Summary

| Entity | Convention | Example |
|--------|------------|---------|
| Script | Stage.Step_Description.py | `1.0_BuildSampleManifest.py` |
| Module | snake_case | `panel_ols.py` |
| Package | snake_case | `shared/`, `observability/` |
| Function | snake_case | `get_latest_output_dir()` |
| Class | PascalCase | `CollinearityError` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Private | _leading_underscore | `_check_thin_cells()` |
| DataFrame | descriptive_df | `manifest_df`, `panel_df` |
| Series | descriptive_s | `returns_s`, `uncertainty` |
| Count | n_prefix or _count | `n_firms`, `record_count` |
| Boolean | is_/has_/should_ | `is_valid`, `has_missing` |
| Path | _path or _dir | `output_path`, `input_dir` |
| Output dir | ISO 8601 date | `2026-02-13-143052` |
| Output file | descriptor_date_checksum | `manifest_20260213_a3f2b8c91d2f.parquet` |

---

## 2. Docstring Standard (CODE-01)

This section defines the docstring format for inline documentation. Scripts use the custom header format defined in SCRIPT_DOCSTANDARD.md; this section covers inline docstrings for functions, methods, classes, and modules.

**Source:** [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

### 2.1 Module Headers (Existing Standard)

For script-level documentation, the project uses a custom header format defined in **SCRIPT_DOCSTANDARD.md**. This format includes:

- Script ID and step number
- Description and purpose
- Inputs and outputs
- Dependencies
- Deterministic flag
- Author and date

**Reference:** See `docs/SCRIPT_DOCSTANDARD.md` for complete header template and examples.

This section (CODE-01) adds inline docstrings for functions, methods, classes, and modules to complement the script headers.

### 2.2 Docstring Requirements by Module Tier

Docstring requirements vary by module tier as defined in ARCHITECTURE_STANDARD.md Section 2.

| Tier | Args | Returns | Raises | Examples |
|------|------|---------|--------|----------|
| **Tier 1 (Core)** | Required | Required | Required | Required |
| **Tier 2 (Stage)** | Required | Required | Required | Recommended |
| **Tier 3 (Scripts)** | Recommended | If non-void | If exceptions | Optional |

**Rationale:**

- **Tier 1 (Core Shared):** Highest documentation bar - used across all stages, must be fully documented
- **Tier 2 (Stage-Specific):** Standard documentation - used within pipeline stages
- **Tier 3 (Scripts):** Lower bar - ad-hoc scripts, basic documentation acceptable

### 2.3 Google-style Docstring Format

Google-style docstrings provide a clean, readable format with structured sections.

#### Complete Function Docstring

```python
def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    entity_col: str = "gvkey",
    time_col: str = "year",
) -> Dict[str, Any]:
    """Execute panel regression with fixed effects.

    Runs a PanelOLS regression with entity and time fixed effects,
    clustered standard errors, and multicollinearity diagnostics.

    Args:
        df: DataFrame with panel data containing all variables.
            Must include entity_col, time_col, dependent, and all
            exogenous variables.
        dependent: Name of the dependent variable column.
        exog: List of exogenous variable column names.
        entity_col: Column name for entity identifier.
            Defaults to "gvkey".
        time_col: Column name for time period.
            Defaults to "year".

    Returns:
        Dictionary containing:
            - model: Fitted PanelOLS object
            - coefficients: DataFrame with beta, SE, t-stat, p-value
            - summary: Dict with R2, adj_R2, N, F-stat
            - diagnostics: Dict with VIF values, condition_number
            - warnings: List of warning messages

    Raises:
        CollinearityError: If perfect collinearity detected in
            design matrix.
        MulticollinearityError: If VIF threshold exceeded for
            any variable.
        ValueError: If required columns missing from DataFrame.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "gvkey": [1, 1, 2, 2],
        ...     "year": [2020, 2021, 2020, 2021],
        ...     "cash_holdings": [0.1, 0.15, 0.08, 0.12],
        ...     "uncertainty": [0.5, 0.4, 0.6, 0.55],
        ...     "leverage": [0.3, 0.25, 0.4, 0.35],
        ... })
        >>> result = run_panel_ols(df, "cash_holdings", ["uncertainty", "leverage"])
        >>> print(result["summary"]["r2"])
        0.45
    """
    # Implementation...
```

#### Section Descriptions

**1. Summary Line (Required)**

- Single line ending with period
- Starts with verb ("Execute", "Calculate", "Return")
- Describes what function does

**2. Extended Description (Recommended)**

- More detail on behavior
- Any important notes or caveats
- Empty line separates from summary

**3. Args Section (Required for Tier 1-2)**

```python
Args:
    param_name: Description of parameter.
        Can span multiple lines with proper indentation.
    another_param: Description. Defaults to "value".
```

- List each parameter in order
- Include type implicitly through description
- Document default values
- Multi-line descriptions indented

**4. Returns Section (Required for non-void)**

```python
Returns:
    Description of return value.

Returns:
    Dict containing:
        - key1: Description of value1
        - key2: Description of value2
```

- Describe what is returned
- For complex returns, list structure
- Be specific about types

**5. Raises Section (Required if exceptions)**

```python
Raises:
    ExceptionType: Description of when raised.
    AnotherException: Different condition description.
```

- List all exceptions that can be raised
- Describe the condition that triggers each
- Include custom exceptions

**6. Examples Section (Required for Tier 1)**

```python
Examples:
    >>> from f1d.shared.panel_ols import run_panel_ols
    >>> result = run_panel_ols(df, "y", ["x1", "x2"])
    >>> print(result["summary"]["r2"])
    0.45
```

- Use doctest format
- Show import statement
- Include expected output
- Keep examples simple but realistic

### 2.4 Simple Function Docstrings

For simpler functions, a concise docstring is acceptable:

```python
def get_latest_output_dir(base_path: Path) -> Path:
    """Find the most recent output directory by timestamp.

    Args:
        base_path: Base directory containing dated subdirectories.

    Returns:
        Path to the most recent dated subdirectory.

    Raises:
        OutputResolutionError: If no valid directories found.
    """
    ...
```

```python
def compute_checksum(file_path: Path, length: int = 12) -> str:
    """Compute SHA-256 checksum truncated to specified length.

    Args:
        file_path: Path to file for checksum computation.
        length: Number of hex characters to return. Defaults to 12.

    Returns:
        Truncated hex digest string.
    """
    ...
```

### 2.5 Method Docstrings

Methods follow the same format as functions:

```python
class DataValidator:
    """Validates financial data for consistency and completeness."""

    def validate_panel(self, df: pd.DataFrame) -> List[str]:
        """Validate panel data structure and content.

        Checks for required columns, missing values, and data types.

        Args:
            df: Panel DataFrame to validate.

        Returns:
            List of validation error messages. Empty if valid.

        Examples:
            >>> validator = DataValidator()
            >>> errors = validator.validate_panel(df)
            >>> len(errors)
            0
        """
        ...

    def _check_balance(self, df: pd.DataFrame) -> bool:
        """Check if panel is balanced (internal method).

        Args:
            df: Panel DataFrame to check.

        Returns:
            True if panel is balanced, False otherwise.
        """
        ...
```

### 2.6 Class Docstrings

Classes should have docstrings explaining their purpose and usage:

```python
class CollinearityError(Exception):
    """Raised when perfect collinearity is detected in regression.

    This exception indicates that the design matrix has perfect
    multicollinearity, making regression impossible.

    Attributes:
        message: Explanation of the collinearity issue.
        variables: List of collinear variable names.
    """

    def __init__(self, message: str, variables: List[str] = None):
        """Initialize CollinearityError.

        Args:
            message: Explanation of the collinearity.
            variables: List of collinear variable names.
        """
        self.message = message
        self.variables = variables or []
        super().__init__(self.message)
```

```python
class DualWriter:
    """Write output to both file and console simultaneously.

    Provides a file-like object that duplicates writes to both
    a log file and stdout. Used for capturing execution logs
    while still displaying progress.

    Attributes:
        file: Open file handle for log file.
        stdout: Reference to sys.stdout.

    Examples:
        >>> with open("output.log", "w") as f:
        ...     writer = DualWriter(f)
        ...     sys.stdout = writer
        ...     print("This appears in both file and console")
    """

    def __init__(self, file: TextIO):
        """Initialize DualWriter.

        Args:
            file: Open file handle to write logs to.
        """
        ...
```

### 2.7 Module Docstrings

Every module MUST have a module-level docstring at the top of the file:

```python
"""Panel OLS regression utilities for F1D pipeline.

This module provides standardized panel regression functions with
fixed effects, clustered standard errors, and multicollinearity
diagnostics. It wraps linearmodels.PanelOLS with additional
validation and diagnostic capabilities.

Main Functions:
    run_panel_ols: Execute panel regression with fixed effects
    compute_vif: Calculate variance inflation factors
    check_collinearity: Detect perfect multicollinearity

Example:
    >>> from f1d.shared.panel_ols import run_panel_ols
    >>> results = run_panel_ols(df, "cash_holdings", ["uncertainty"])
    >>> print(results["summary"]["r2"])

Dependencies:
    linearmodels: For PanelOLS implementation
    pandas: For DataFrame handling
    numpy: For numerical operations
"""
```

#### Module Docstring Requirements

1. **First line:** Brief description of module purpose
2. **Extended description:** More detail on what module provides
3. **Main functions/classes:** List key public API
4. **Example:** Show typical usage
5. **Dependencies:** List required packages (if non-standard)

### 2.8 Package __init__.py Docstrings

Package __init__.py files should document the package:

```python
"""Shared utilities for F1D pipeline.

This package contains cross-cutting utilities used across
all stages of the data processing pipeline.

Modules:
    path_utils: Path resolution and output directory utilities
    panel_ols: Panel OLS regression utilities
    io_utils: Input/output utilities
    observability: Logging and monitoring

Public API:
    get_latest_output_dir: Find latest output directory
    run_panel_ols: Execute panel regression
    OutputResolutionError: Path resolution exception
    CollinearityError: Regression collinearity exception

Example:
    >>> from f1d.shared import get_latest_output_dir, run_panel_ols
    >>> output = get_latest_output_dir("data/processed/manifest")
"""

from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError
from f1d.shared.panel_ols import run_panel_ols, CollinearityError

__all__ = [
    "get_latest_output_dir",
    "OutputResolutionError",
    "run_panel_ols",
    "CollinearityError",
]
```

### 2.9 Docstring Anti-Patterns

Avoid these common docstring mistakes:

#### Anti-pattern 1: Missing or Minimal Docstring

```python
# BAD: No docstring
def process_data(df):
    return df.dropna()

# BAD: Useless docstring
def process_data(df):
    """Process data."""
    return df.dropna()

# GOOD: Descriptive docstring
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing values from DataFrame.

    Args:
        df: Input DataFrame with potential missing values.

    Returns:
        DataFrame with all rows containing NaN values removed.
    """
    return df.dropna()
```

#### Anti-pattern 2: Documentation by Assertion

```python
# BAD: Assumes reader knows what happens
def run_regression(df, x, y):
    """Runs the regression."""
    ...

# GOOD: Explains what and why
def run_regression(df: pd.DataFrame, x: List[str], y: str) -> Dict:
    """Execute OLS regression of y on x variables.

    Performs ordinary least squares regression with the specified
    dependent variable and exogenous variables.

    Args:
        df: DataFrame containing all regression variables.
        x: List of exogenous variable column names.
        y: Name of dependent variable column.

    Returns:
        Dictionary with coefficients, standard errors, and fit statistics.
    """
    ...
```

#### Anti-pattern 3: Missing Type Information

```python
# BAD: No types in docstring or signature
def merge_data(left, right, key):
    """Merge two dataframes."""
    ...

# GOOD: Types in both signature and docstring
def merge_data(
    left: pd.DataFrame,
    right: pd.DataFrame,
    key: str,
) -> pd.DataFrame:
    """Merge two DataFrames on specified key column.

    Args:
        left: Left DataFrame for merge.
        right: Right DataFrame for merge.
        key: Column name to merge on.

    Returns:
        Merged DataFrame.
    """
    ...
```

#### Anti-pattern 4: Missing Raises Documentation

```python
# BAD: Doesn't document exceptions
def load_data(path):
    """Load data from file."""
    with open(path) as f:
        return json.load(f)

# GOOD: Documents all exceptions
def load_data(path: Path) -> Dict:
    """Load JSON data from file.

    Args:
        path: Path to JSON file.

    Returns:
        Parsed JSON data as dictionary.

    Raises:
        FileNotFoundError: If file does not exist.
        json.JSONDecodeError: If file is not valid JSON.
    """
    with open(path) as f:
        return json.load(f)
```

#### Anti-pattern 5: Examples That Don't Work

```python
# BAD: Example can't run as written
def process(df):
    """Process data.

    Examples:
        >>> result = process(data)  # 'data' undefined
        >>> print(result)
    """
    ...

# GOOD: Self-contained example
def process(df: pd.DataFrame) -> pd.DataFrame:
    """Process data by removing missing values.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"a": [1, None, 3]})
        >>> result = process(df)
        >>> len(result)
        2
    """
    ...
```

### 2.10 Docstring Checklist

When writing docstrings, ensure:

- [ ] Summary line ends with period
- [ ] Summary line starts with verb
- [ ] Args section lists all parameters
- [ ] Args include types in description
- [ ] Defaults documented in Args
- [ ] Returns section for non-void functions
- [ ] Returns describes structure for complex returns
- [ ] Raises section lists all exceptions
- [ ] Examples section for Tier 1 functions
- [ ] Examples include import statements
- [ ] Examples have expected output
- [ ] Module has module-level docstring
- [ ] Classes have class docstrings
- [ ] No "documentation by assertion"

---

## 3. Type Hint Coverage (CODE-02)

This section defines type hint requirements based on the module tier system established in ARCHITECTURE_STANDARD.md. Type hints improve code readability, enable static analysis, and enhance IDE support.

**Source:** [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)

### 3.1 Tier Requirements

Type hint coverage requirements vary by module tier:

| Tier | Coverage Target | mypy Mode | Enforcement |
|------|-----------------|-----------|-------------|
| **Tier 1 (Core Shared)** | 100% | `strict = true` | CI blocking |
| **Tier 2 (Stage-Specific)** | 80%+ | `disallow_untyped_defs = false` | Warning |
| **Tier 3 (Scripts)** | Optional | Excluded from mypy | None |

**Tier 1 (Core Shared):**

- Location: `src/f1d/shared/`
- Coverage: 100% of public functions and methods
- All parameters and return types must be annotated
- mypy strict mode enabled
- CI pipeline blocks on type errors

**Tier 2 (Stage-Specific):**

- Location: `src/f1d/{stage}/`
- Coverage: 80%+ recommended
- Public functions should have type hints
- Gradual adoption allowed
- mypy warnings (not blocking)

**Tier 3 (Scripts):**

- Location: `scripts/` or stage `scripts/` subdirectories
- Coverage: Optional
- Type hints encouraged but not required
- Excluded from mypy checking

### 3.2 mypy Configuration

Configure mypy in `pyproject.toml` with tier-specific settings:

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
check_untyped_defs = true
disallow_incomplete_defs = true

# Strict mode for Tier 1 (Core Shared)
[[tool.mypy.overrides]]
module = [
    "f1d.shared.observability.*",
    "f1d.shared.path_utils",
    "f1d.shared.exceptions",
]
strict = true

# Gradual adoption for Tier 2 (Stage-Specific)
[[tool.mypy.overrides]]
module = [
    "f1d.shared.panel_ols",
    "f1d.shared.io_utils",
]
disallow_untyped_defs = false
warn_return_any = false

# Exclude Tier 3 (Scripts) from type checking
[[tool.mypy.overrides]]
module = [
    "scripts.*",
    "f1d.*.scripts.*",
]
ignore_errors = true
```

### 3.3 Type Hint Examples

#### Basic Type Hints

```python
from pathlib import Path
from typing import Dict, List, Optional, Union

# Basic types
def get_name() -> str:
    return "F1D Pipeline"

def get_count(items: List[str]) -> int:
    return len(items)

# Optional types (can be None)
def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    if path is None:
        path = Path("config/default.yaml")
    ...

# Union types (one of several types)
def parse_value(value: Union[str, int, float]) -> float:
    return float(value)
```

#### Collection Types

```python
from typing import Dict, List, Set, Tuple, Sequence

# Lists
def process_items(items: List[str]) -> List[int]:
    return [len(item) for item in items]

# Dictionaries
def count_by_category(
    items: List[str],
) -> Dict[str, int]:
    ...

# Tuples (fixed-length, typed)
def get_coordinates() -> Tuple[float, float]:
    return (45.5, -122.6)

# Sets
def unique_items(items: List[str]) -> Set[str]:
    return set(items)

# Sequences (abstract, accepts list or tuple)
def process_sequence(items: Sequence[int]) -> int:
    return sum(items)
```

#### Pandas Types

```python
import pandas as pd
from pandas import DataFrame, Series
from typing import Any

# DataFrame
def load_data(path: Path) -> pd.DataFrame:
    ...

# Series
def extract_column(df: pd.DataFrame, col: str) -> pd.Series:
    ...

# Any for complex pandas operations
def summarize_results(df: pd.DataFrame) -> Dict[str, Any]:
    ...
```

#### Callable Types

```python
from typing import Callable

# Function parameter
def apply_transform(
    df: pd.DataFrame,
    transform: Callable[[pd.DataFrame], pd.DataFrame],
) -> pd.DataFrame:
    return transform(df)

# Function with specific signature
ValidatorFunc = Callable[[pd.DataFrame], List[str]]

def validate_and_fix(
    df: pd.DataFrame,
    validator: ValidatorFunc,
) -> pd.DataFrame:
    errors = validator(df)
    if errors:
        df = fix_errors(df, errors)
    return df
```

### 3.4 Type Aliases

Create type aliases for complex types to improve readability:

```python
from typing import Dict, List, Any, TypedDict

# Simple type aliases
DataFrameDict = Dict[str, pd.DataFrame]
VariableList = List[str]
RegressionResults = Dict[str, Any]

# TypedDict for structured dictionaries
class PanelDataSpec(TypedDict):
    """Specification for panel data structure."""
    entity_col: str
    time_col: str
    dependent: str
    exog: VariableList

# Usage
def run_regression(
    df: pd.DataFrame,
    spec: PanelDataSpec,
) -> RegressionResults:
    ...
```

### 3.5 Generic Types and Protocols

For advanced type hinting with generics:

```python
from typing import TypeVar, Generic, Protocol, runtime_checkable

# Type variable for generic functions
T = TypeVar("T")

def first(items: List[T]) -> T:
    return items[0]

# Generic class
class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

# Protocol for duck typing
@runtime_checkable
class Summable(Protocol):
    def __sum__(self) -> float:
        ...

def total(items: List[Summable]) -> float:
    return sum(items)
```

### 3.6 Type Hint Anti-Patterns

Avoid these common type hint mistakes:

#### Anti-pattern 1: Using Any Without Justification

```python
# BAD: Any everywhere loses type safety
def process(data: Any) -> Any:
    ...

# GOOD: Specific types where possible
def process(df: pd.DataFrame) -> Dict[str, Any]:
    ...

# ACCEPTABLE: Any for genuinely dynamic data
def parse_json(path: Path) -> Any:
    """Parse JSON - structure unknown at compile time."""
    ...
```

#### Anti-pattern 2: Missing Return Type Hints

```python
# BAD: No return type on public function
def get_output_path(base: Path, name: str):
    return base / name

# GOOD: Return type specified
def get_output_path(base: Path, name: str) -> Path:
    return base / name
```

#### Anti-pattern 3: Incomplete Parameter Types

```python
# BAD: Some parameters lack types
def run_regression(
    df: pd.DataFrame,
    dependent,
    exog: List[str],
) -> Dict:
    ...

# GOOD: All parameters typed
def run_regression(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
) -> Dict[str, Any]:
    ...
```

#### Anti-pattern 4: Type Ignore Comments Without Justification

```python
# BAD: type: ignore without reason
result = legacy_function()  # type: ignore

# ACCEPTABLE: Documented reason
result = legacy_function()  # type: ignore[no-untyped-call]  # Legacy code
```

### 3.7 Type Checking Commands

Run mypy type checking:

```bash
# Check entire codebase
mypy src/

# Check specific module
mypy src/f1d/shared/panel_ols.py

# Check with strict mode
mypy --strict src/f1d/shared/

# Generate HTML report
mypy --html-report ./mypy-report src/

# Check specific error codes
mypy --disable-error-code=import-untyped src/
```

### 3.8 Type Hint Coverage Verification

Verify type hint coverage:

```bash
# Using mypy-report
mypy --linecount-report ./type-coverage src/

# Using coverage.py with mypy plugin
pip install mypy-coverage-plugin
coverage run -m pytest
coverage report
```

### 3.9 Rationale

**Why Type Hints?**

1. **Catch errors before runtime:** Static analysis finds bugs early
2. **Better IDE support:** Autocomplete, inline documentation
3. **Self-documenting code:** Types serve as documentation
4. **Easier refactoring:** IDE can safely rename and restructure
5. **Cross-reference to ARCHITECTURE_STANDARD.md:** Module tiers guide quality bars

**Why Tiered Requirements?**

1. **Risk management:** Core shared code affects all stages
2. **Resource allocation:** Focus effort on high-impact code
3. **Practical adoption:** Gradual typing enables incremental improvement
4. **Team velocity:** Lower bar for exploratory code

---

## 4. Import Organization (CODE-03)

This section defines the import organization pattern, following PEP 8 conventions. Proper import organization improves code readability and makes dependencies explicit.

**Note:** This section restates conventions already defined in ARCHITECTURE_STANDARD.md Section 2.4 for completeness.

**Source:** [PEP 8 - Imports](https://peps.python.org/pep-0008/#imports)

### 4.1 Import Order

Imports should be grouped in the following order, separated by blank lines:

1. **Standard library** (alphabetical)
2. **Third-party packages** (alphabetical)
3. **Local imports** (absolute, alphabetical)

```python
#!/usr/bin/env python3
"""Module demonstrating proper import organization."""

# =============================================================================
# 1. Standard library imports (alphabetical)
# =============================================================================
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# =============================================================================
# 2. Third-party package imports (alphabetical)
# =============================================================================
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from scipy import stats

# =============================================================================
# 3. Local imports (absolute, alphabetical)
# =============================================================================
from f1d.shared.exceptions import (
    CollinearityError,
    DataValidationError,
    F1DError,
)
from f1d.shared.observability import get_logger, Stats
from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError
```

### 4.2 Import Rules

#### Rule 1: Absolute Imports Over Relative

Always use absolute imports for clarity and refactoring safety:

```python
# GOOD: Absolute imports
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.panel_ols import run_panel_ols
from f1d.financial.v2.variables import construct_variables

# BAD: Relative imports (avoid in production code)
from ..shared.path_utils import get_latest_output_dir
from .variables import construct_variables
```

**Exception:** Relative imports acceptable in `__init__.py` for re-exports within the same package.

#### Rule 2: Group Imports with Blank Lines

Separate import groups with a single blank line:

```python
# Standard library
import os
from pathlib import Path

# Third-party
import pandas as pd

# Local
from f1d.shared.path_utils import get_latest_output_dir
```

#### Rule 3: Sort Alphabetically Within Each Group

Sort imports alphabetically within each section:

```python
# GOOD: Alphabetical order
from f1d.shared.exceptions import CollinearityError, DataValidationError
from f1d.shared.observability import get_logger
from f1d.shared.path_utils import get_latest_output_dir

# BAD: Random order
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.exceptions import CollinearityError, DataValidationError
from f1d.shared.observability import get_logger
```

#### Rule 4: Use `from X import Y` for Specific Items

Import specific items rather than entire modules when possible:

```python
# GOOD: Import specific items
from f1d.shared.path_utils import get_latest_output_dir
from typing import Dict, List, Optional

# ACCEPTABLE: Import module for module-level access
import pandas as pd
import numpy as np

# BAD: Import everything
from f1d.shared.path_utils import *
```

#### Rule 5: One Import Per Line for Multiple Items

When importing multiple items from the same module, use parentheses for readability:

```python
# GOOD: Multiple imports with parentheses
from f1d.shared.exceptions import (
    CollinearityError,
    DataValidationError,
    F1DError,
    OutputResolutionError,
)

# BAD: All on one line (too long)
from f1d.shared.exceptions import CollinearityError, DataValidationError, F1DError, OutputResolutionError

# BAD: Multiple import statements for same module
from f1d.shared.exceptions import CollinearityError
from f1d.shared.exceptions import DataValidationError
from f1d.shared.exceptions import F1DError
```

### 4.3 Import Patterns

#### Standard Library Imports

```python
# Common standard library imports for F1D
import json
import logging
import os
import re
import sys
import warnings
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)
```

#### Third-Party Imports

```python
# Common third-party imports for F1D
import numpy as np
import pandas as pd
import yaml
from linearmodels.panel import PanelOLS
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
```

#### Local Imports

```python
# Local imports use the f1d package namespace
from f1d import __version__
from f1d.shared.exceptions import F1DError
from f1d.shared.observability import get_logger, Stats
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.panel_ols import run_panel_ols
```

### 4.4 Import Anti-Patterns

Avoid these common import mistakes:

#### Anti-pattern 1: Star Imports

```python
# BAD: Star import pollutes namespace
from pandas import *
from f1d.shared.path_utils import *

# GOOD: Import specific items
import pandas as pd
from f1d.shared.path_utils import get_latest_output_dir
```

#### Anti-pattern 2: Multiple Imports on One Line

```python
# BAD: Multiple imports on one line
import os, sys, json

# GOOD: One import per line
import json
import os
import sys
```

#### Anti-pattern 3: Mixed Import Styles

```python
# BAD: Inconsistent style
from pathlib import Path
import pandas
from datetime import datetime
import numpy

# GOOD: Consistent style
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
```

#### Anti-pattern 4: Relative Imports in Production Code

```python
# BAD: Relative imports break when module moves
from ..shared import path_utils
from . import variables

# GOOD: Absolute imports survive refactoring
from f1d.shared import path_utils
from f1d.financial.v2 import variables
```

#### Anti-pattern 5: Importing Inside Functions

```python
# BAD: Import inside function (unless avoiding circular import)
def run_analysis():
    from f1d.shared.panel_ols import run_panel_ols
    ...

# GOOD: Import at module level
from f1d.shared.panel_ols import run_panel_ols

def run_analysis():
    ...
```

**Exception:** Import inside function acceptable for:
- Avoiding circular imports
- Lazy loading heavy dependencies
- Optional dependencies

```python
# ACCEPTABLE: Lazy import to avoid circular dependency
def get_config():
    from f1d.config.loader import load_config  # Avoids circular import
    return load_config()

# ACCEPTABLE: Lazy import for optional dependency
def plot_results(df):
    try:
        import matplotlib.pyplot as plt  # Optional dependency
    except ImportError:
        raise ImportError("matplotlib required for plotting")
    ...
```

### 4.5 ruff isort Configuration

Configure ruff to automatically organize imports:

```toml
[tool.ruff]
select = ["I"]  # Enable isort rules

[tool.ruff.isort]
known-first-party = ["f1d"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
```

Run ruff to organize imports:

```bash
# Check import order
ruff check --select I src/

# Auto-fix import order
ruff check --select I --fix src/

# Format entire codebase
ruff format src/
```

### 4.6 Import Organization Checklist

When organizing imports, ensure:

- [ ] Imports grouped: stdlib, third-party, local
- [ ] Blank line between each group
- [ ] Alphabetical order within groups
- [ ] Absolute imports used (not relative)
- [ ] Specific imports (not `import *`)
- [ ] Multiple imports in parentheses
- [ ] No multiple imports on one line
- [ ] No imports inside functions (unless necessary)
- [ ] ruff isort configured and passing

### 4.7 Cross-Reference

This section aligns with:

- **ARCHITECTURE_STANDARD.md Section 2.4:** Import conventions
- **ARCHITECTURE_STANDARD.md Section 2.3:** Module tier system affects import paths
- **ARCHITECTURE_STANDARD.md Section 1:** Folder structure defines import paths

### 4.8 Rationale

**Why This Import Order?**

1. **Clarity:** Grouped imports show dependency categories
2. **Standard compliance:** PEP 8 convention
3. **Tool support:** isort and ruff automate organization
4. **Readability:** Alphabetical sorting aids scanning

**Why Absolute Imports?**

1. **Clarity:** Import path shows exact location
2. **Refactoring:** Moving files doesn't break imports
3. **Tooling:** IDEs and linters work better
4. **Standard:** PEP 8 recommends absolute imports

**Why No Star Imports?**

1. **Namespace pollution:** Unclear where names come from
2. **IDE support:** Autocomplete can't suggest imported names
3. **Conflicts:** May shadow existing names
4. **Explicit is better:** Zen of Python

---

## 5. Error Handling (CODE-04)

This section defines the error handling patterns for the F1D project, including custom exceptions and the no-bare-except policy.

**Source:** [PEP 760 - No More Bare Excepts](https://peps.python.org/pep-0760/) (2024)

### 5.1 Custom Exceptions (CODE-04)

Use a hierarchy of custom exceptions to provide clear error context and enable specific error handling.

#### Exception Hierarchy

```python
# src/f1d/shared/exceptions.py
"""Custom exceptions for F1D pipeline."""

from typing import Optional, List


class F1DError(Exception):
    """Base exception for all F1D-specific errors.

    All custom exceptions in the F1D project should inherit from
    this base class to enable catching all F1D errors with a
    single except clause.

    Attributes:
        message: Human-readable error description.
        details: Optional additional context about the error.
    """

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


# =============================================================================
# Data Validation Errors
# =============================================================================

class DataValidationError(F1DError):
    """Raised when data validation fails.

    Indicates that input data does not meet expected format,
    constraints, or quality requirements.

    Attributes:
        column: Name of column that failed validation.
        reason: Specific reason for validation failure.
    """

    def __init__(
        self,
        message: str,
        column: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        self.column = column
        self.reason = reason
        details = f"Column: {column}, Reason: {reason}" if column else None
        super().__init__(message, details)


class FinancialCalculationError(F1DError):
    """Raised when financial metric calculation fails.

    Indicates an error in computing financial variables such as
    cash holdings, leverage, or investment measures.

    Attributes:
        metric: Name of the metric that failed to calculate.
        gvkey: Firm identifier if available.
    """

    def __init__(
        self,
        message: str,
        metric: Optional[str] = None,
        gvkey: Optional[str] = None,
    ):
        self.metric = metric
        self.gvkey = gvkey
        details = f"Metric: {metric}, GVKEY: {gvkey}" if metric else None
        super().__init__(message, details)


# =============================================================================
# Regression Errors
# =============================================================================

class CollinearityError(F1DError):
    """Raised when perfect collinearity is detected.

    Indicates that the design matrix has perfect multicollinearity,
    making regression estimation impossible.

    Attributes:
        variables: List of collinear variable names.
    """

    def __init__(self, message: str, variables: Optional[List[str]] = None):
        self.variables = variables or []
        details = f"Variables: {', '.join(variables)}" if variables else None
        super().__init__(message, details)


class MulticollinearityError(F1DError):
    """Raised when VIF threshold is exceeded.

    Indicates problematic (but not perfect) multicollinearity
    detected through variance inflation factor analysis.

    Attributes:
        variable: Variable with high VIF.
        vif_value: The calculated VIF value.
    """

    def __init__(
        self,
        message: str,
        variable: Optional[str] = None,
        vif_value: Optional[float] = None,
    ):
        self.variable = variable
        self.vif_value = vif_value
        details = f"Variable: {variable}, VIF: {vif_value:.2f}" if variable else None
        super().__init__(message, details)


class RegressionValidationError(F1DError):
    """Raised when regression inputs fail validation.

    Indicates missing data, incorrect types, or invalid
    regression specifications.

    Attributes:
        field: Field that failed validation.
        expected: Expected format or type.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        expected: Optional[str] = None,
    ):
        self.field = field
        self.expected = expected
        details = f"Field: {field}, Expected: {expected}" if field else None
        super().__init__(message, details)


# =============================================================================
# Path and IO Errors
# =============================================================================

class PathValidationError(F1DError):
    """Raised when path validation fails.

    Indicates that a path does not meet expected criteria
    such as existence, accessibility, or format.

    Attributes:
        path: The path that failed validation.
    """

    def __init__(self, message: str, path: Optional[str] = None):
        self.path = path
        details = f"Path: {path}" if path else None
        super().__init__(message, details)


class OutputResolutionError(F1DError):
    """Raised when output directory cannot be resolved.

    Indicates failure to find or create an output directory,
    typically when looking for the latest dated directory.

    Attributes:
        base_path: Base directory searched.
    """

    def __init__(self, message: str, base_path: Optional[str] = None):
        self.base_path = base_path
        details = f"Base path: {base_path}" if base_path else None
        super().__init__(message, details)


# =============================================================================
# Configuration Errors
# =============================================================================

class EnvValidationError(F1DError):
    """Raised when environment validation fails.

    Indicates missing or invalid environment variables
    required for pipeline execution.

    Attributes:
        env_var: Name of the environment variable.
    """

    def __init__(self, message: str, env_var: Optional[str] = None):
        self.env_var = env_var
        details = f"Environment variable: {env_var}" if env_var else None
        super().__init__(message, details)


# =============================================================================
# Instrumental Variable Errors
# =============================================================================

class WeakInstrumentError(F1DError):
    """Raised when instrumental variables are weak.

    Indicates that the first-stage F-statistic is below
    the threshold for strong instruments.

    Attributes:
        f_statistic: The calculated F-statistic value.
        threshold: The threshold that was not met.
    """

    def __init__(
        self,
        message: str,
        f_statistic: Optional[float] = None,
        threshold: float = 10.0,
    ):
        self.f_statistic = f_statistic
        self.threshold = threshold
        details = f"F-statistic: {f_statistic:.2f}, Threshold: {threshold}" if f_statistic else None
        super().__init__(message, details)
```

### 5.2 Current Exceptions in Codebase

The F1D codebase currently has **11 custom exceptions** across **6 files**:

| Exception | Location | Purpose |
|-----------|----------|---------|
| `CollinearityError` | panel_ols.py, diagnostics.py | Perfect collinearity |
| `MulticollinearityError` | panel_ols.py, diagnostics.py | High VIF values |
| `PathValidationError` | path_utils.py | Path validation failure |
| `OutputResolutionError` | path_utils.py | Output directory not found |
| `DataValidationError` | data_validation.py | Data quality issues |
| `FinancialCalculationError` | data_validation.py | Financial metric errors |
| `EnvValidationError` | env_validation.py | Environment variable issues |
| `WeakInstrumentError` | iv_regression.py | Weak IV detection |
| `RegressionValidationError` | regression_validation.py | Regression input errors |

**Recommendation:** Consolidate all custom exceptions into `src/f1d/shared/exceptions.py` for central management and consistent documentation.

### 5.3 No Bare Except (Critical)

**PEP 760 (2024)** introduces a mandate to eliminate bare `except:` clauses. Bare excepts catch ALL exceptions, including system exceptions that should not be caught.

#### Anti-pattern (NEVER use)

```python
# DANGEROUS: Bare except catches everything
try:
    operation()
except:  # WRONG - catches SystemExit, KeyboardInterrupt, GeneratorExit
    pass

# This can prevent:
# - Clean shutdown (SystemExit)
# - Keyboard interrupts (KeyboardInterrupt)
# - Generator cleanup (GeneratorExit)
# - Debugging (makes errors invisible)
```

#### Correct Patterns

**1. Catch specific exceptions:**

```python
# GOOD: Catch specific exception
try:
    df = pd.read_parquet(path)
except FileNotFoundError as e:
    logger.error(f"File not found: {path}")
    raise DataValidationError(f"Required file missing: {path}") from e
```

**2. Catch multiple specific exceptions:**

```python
# GOOD: Multiple specific exceptions
try:
    result = run_regression(df, spec)
except (CollinearityError, MulticollinearityError) as e:
    logger.error(f"Regression failed: {e}")
    raise
```

**3. Catch Exception (not bare) if needed:**

```python
# ACCEPTABLE: Catch Exception (not base except)
try:
    risky_operation()
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise DataValidationError(f"Operation failed: {e}") from e

# Note: This still allows SystemExit, KeyboardInterrupt to propagate
```

**4. Re-raise with context:**

```python
# GOOD: Re-raise with exception chaining
try:
    data = load_config(path)
except FileNotFoundError as e:
    raise EnvValidationError(
        f"Configuration file not found: {path}"
    ) from e

# The 'from e' preserves the original traceback
```

**5. Handle and continue (when appropriate):**

```python
# GOOD: Handle specific error and continue
for file in files:
    try:
        process_file(file)
    except DataValidationError as e:
        logger.warning(f"Skipping {file}: {e}")
        continue  # Continue with next file
```

### 5.4 Exception Handling Rules

1. **Never use bare `except:`** (PEP 760)
2. **Always specify exception type(s)**
3. **Either handle the exception or re-raise it**
4. **Use `raise ... from e` for exception chaining**
5. **Log exceptions before re-raising when appropriate**
6. **Create specific custom exceptions for domain errors**

### 5.5 Exception Handling Patterns

#### Pattern 1: Validate and Raise

```python
def load_panel_data(path: Path) -> pd.DataFrame:
    """Load panel data with validation.

    Args:
        path: Path to panel data file.

    Returns:
        Loaded DataFrame.

    Raises:
        PathValidationError: If path doesn't exist.
        DataValidationError: If data doesn't meet requirements.
    """
    # Validate path
    if not path.exists():
        raise PathValidationError(
            f"Panel data file not found: {path}",
            path=str(path),
        )

    # Load data
    try:
        df = pd.read_parquet(path)
    except Exception as e:
        raise DataValidationError(
            f"Failed to load panel data: {e}",
            details=str(e),
        ) from e

    # Validate content
    required_cols = ["gvkey", "year", "uncertainty"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise DataValidationError(
            f"Missing required columns: {missing}",
            column=", ".join(missing),
        )

    return df
```

#### Pattern 2: Try-Except-Log-Reraise

```python
def run_regression_safely(
    df: pd.DataFrame,
    spec: RegressionSpec,
) -> RegressionResults:
    """Run regression with comprehensive error handling.

    Args:
        df: Panel data for regression.
        spec: Regression specification.

    Returns:
        Regression results.

    Raises:
        CollinearityError: If perfect collinearity detected.
        MulticollinearityError: If VIF threshold exceeded.
        RegressionValidationError: If inputs invalid.
    """
    logger = get_logger(__name__)

    try:
        results = run_panel_ols(df, spec)
    except CollinearityError as e:
        logger.error(f"Collinearity detected: {e.variables}")
        raise
    except MulticollinearityError as e:
        logger.warning(f"High VIF for {e.variable}: {e.vif_value:.2f}")
        raise
    except Exception as e:
        logger.error(f"Unexpected regression error: {e}")
        raise RegressionValidationError(
            f"Regression failed: {e}",
            field="unknown",
            expected="valid regression inputs",
        ) from e

    return results
```

#### Pattern 3: Cleanup in Finally

```python
def process_with_cleanup(input_path: Path, output_path: Path) -> None:
    """Process data with guaranteed cleanup.

    Args:
        input_path: Path to input file.
        output_path: Path for output file.
    """
    temp_file = None

    try:
        # Create temp file
        temp_file = output_path.with_suffix(".tmp")
        temp_file.touch()

        # Process data
        df = pd.read_parquet(input_path)
        result = transform_data(df)
        result.to_parquet(temp_file)

        # Atomic rename
        temp_file.rename(output_path)

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        # Clean up temp file on failure
        if temp_file and temp_file.exists():
            temp_file.unlink()
        raise

    finally:
        # Always clean up temp file
        if temp_file and temp_file.exists():
            temp_file.unlink()
```

### 5.6 Error Handling Anti-Patterns

#### Anti-pattern 1: Catching and Doing Nothing

```python
# BAD: Silent failure
try:
    process_data()
except:  # Also bare except!
    pass  # Error is silently ignored

# GOOD: Log the error at minimum
try:
    process_data()
except DataValidationError as e:
    logger.error(f"Data processing failed: {e}")
    raise
```

#### Anti-pattern 2: Catching Too Broadly

```python
# BAD: Catching Exception when specific type is known
try:
    df = pd.read_parquet(path)
except Exception as e:
    ...

# GOOD: Catch specific exception
try:
    df = pd.read_parquet(path)
except FileNotFoundError as e:
    raise PathValidationError(f"File not found: {path}") from e
```

#### Anti-pattern 3: Losing Traceback

```python
# BAD: Losing original traceback
try:
    risky_operation()
except ValueError as e:
    raise CustomError(str(e))  # Original traceback lost

# GOOD: Preserve traceback with exception chaining
try:
    risky_operation()
except ValueError as e:
    raise CustomError(str(e)) from e  # Original traceback preserved
```

### 5.7 Error Handling Checklist

When handling errors, ensure:

- [ ] No bare `except:` clauses
- [ ] Specific exception types caught
- [ ] Either handle or re-raise (not both ignored)
- [ ] `raise ... from e` for exception chaining
- [ ] Errors logged before re-raising
- [ ] Custom exceptions inherit from F1DError
- [ ] Custom exceptions have descriptive names ending in "Error"
- [ ] Custom exceptions include relevant context attributes
- [ ] Cleanup in `finally` block when needed

### 5.8 Rationale

**Why Custom Exceptions?**

1. **Clear error context:** Specific exceptions indicate what went wrong
2. **Selective handling:** Callers can catch specific error types
3. **Documentation:** Exception types document failure modes
4. **Debugging:** Stack traces point to exception source

**Why No Bare Except (PEP 760)?**

1. **System stability:** Catches SystemExit, KeyboardInterrupt incorrectly
2. **Debugging:** Makes errors invisible and hard to trace
3. **Best practice:** Explicit is better than implicit
4. **Future standard:** PEP 760 makes this official Python policy

**Why Exception Chaining?**

1. **Full context:** Preserves original traceback
2. **Debugging:** Can trace error to root cause
3. **Documentation:** Shows error transformation chain
4. **Python 3 feature:** Built-in language support

---
---
