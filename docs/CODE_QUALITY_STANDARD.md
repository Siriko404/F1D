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
