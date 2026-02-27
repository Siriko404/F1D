# Docstring Standardization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Standardize all docstrings across 163 Python modules to a consistent Google-style format, treating code as source of truth.

**Architecture:** Process modules in dependency order (shared infrastructure first, then stage scripts). Use 4 templates based on module type. Preserve high-quality existing docstrings. Verify each phase with pydocstyle/interrogate/mypy.

**Tech Stack:** Python 3.9+, pydocstyle, interrogate, mypy

---

## Prerequisites

### Task 0: Install Verification Tools

**Files:**
- Modify: `requirements.txt`

**Step 1: Add verification dependencies**

Add to `requirements.txt`:
```
pydocstyle>=2.3.0
interrogate>=1.5.0
```

**Step 2: Install dependencies**

Run: `pip install pydocstyle interrogate`

**Step 3: Verify installation**

Run: `pydocstyle --version && interrogate --version`
Expected: Version numbers printed

---

## Phase 1: Package Root

### Task 1.1: Standardize src/f1d/__init__.py

**Files:**
- Modify: `src/f1d/__init__.py`

**Step 1: Read current file**

Run: Read `src/f1d/__init__.py`

**Step 2: Analyze existing docstring**

Check if docstring exists and if it follows Google-style. If high-quality, preserve and only add missing fields.

**Step 3: Write/update module docstring**

If needs standardization, replace/add module docstring:

```python
"""F1D - CEO Communication Clarity Pipeline.

This package provides an econometric pipeline for estimating CEO-level
fixed effects in linguistic uncertainty from earnings call transcripts.

Key Modules:
    - sample: Stage 1 sample construction
    - text: Stage 2 text processing
    - variables: Stage 3 panel builders
    - econometric: Stage 4 hypothesis tests
    - shared: Cross-stage utilities and variable builders

Usage:
    from f1d import get_latest_output_dir, run_panel_ols
    from f1d.shared.variables import VariableBuilder
"""
```

**Step 4: Verify file is valid Python**

Run: `python -c "import f1d; print(f1d.__version__)"`
Expected: Version number or no error

**Step 5: Commit**

```bash
git add src/f1d/__init__.py
git commit -m "docs: standardize docstring in f1d/__init__.py"
```

---

## Phase 2: Shared Config (6 files)

### Task 2.1: List config modules

Run: `find src/f1d/shared/config -name "*.py" -type f`

Expected files:
- `__init__.py`
- `base.py`
- `loader.py`
- `datasets.py`
- `env.py`
- `paths.py`

### Task 2.2: Standardize src/f1d/shared/config/__init__.py

**Files:**
- Modify: `src/f1d/shared/config/__init__.py`

**Step 1: Read current file**

Run: Read `src/f1d/shared/config/__init__.py`

**Step 2: Write package init docstring**

```python
"""Configuration package for F1D pipeline.

This package provides Pydantic-based configuration models with
environment variable support and YAML file loading.

Modules:
    - base: Base configuration models
    - loader: Configuration loading and caching
    - datasets: Dataset path configuration
    - env: Environment variable settings
    - paths: Path utilities and resolution
"""
```

**Step 3: Commit**

```bash
git add src/f1d/shared/config/__init__.py
git commit -m "docs: standardize docstring in shared/config/__init__.py"
```

### Task 2.3: Standardize src/f1d/shared/config/base.py

**Files:**
- Modify: `src/f1d/shared/config/base.py`

**Step 1: Read current file**

Run: Read `src/f1d/shared/config/base.py`

**Step 2: Check if docstring should be preserved**

If existing docstring is Google-style with Args/Returns, preserve it.

**Step 3: Write/update module docstring if needed**

```python
"""Base configuration models for F1D pipeline.

Purpose:
    Provides Pydantic base classes for configuration validation.

Key Classes:
    - BaseSettings: Base class for settings with env var support
    - DataSettings: Data path configuration
    - LoggingSettings: Logging configuration

Usage:
    from f1d.shared.config.base import DataSettings
    settings = DataSettings()
"""
```

**Step 4: Update function docstrings**

For each function/class, ensure Google-style docstring:

```python
def load_config(path: Path) -> ProjectConfig:
    """Load configuration from YAML file.

    Args:
        path: Path to YAML configuration file.

    Returns:
        ProjectConfig instance with validated settings.

    Raises:
        ConfigError: If file not found or validation fails.
    """
```

**Step 5: Commit**

```bash
git add src/f1d/shared/config/base.py
git commit -m "docs: standardize docstring in shared/config/base.py"
```

### Task 2.4-2.6: Repeat for remaining config modules

Follow same pattern for:
- `loader.py`
- `datasets.py`
- `env.py`
- `paths.py`

### Task 2.7: Verify Phase 2

**Step 1: Run pydocstyle**

Run: `pydocstyle --convention=google src/f1d/shared/config/`
Expected: No errors (or list errors to fix)

**Step 2: Run interrogate**

Run: `interrogate -v src/f1d/shared/config/`
Expected: 100% coverage

**Step 3: Run mypy**

Run: `mypy src/f1d/shared/config/`
Expected: No new errors

**Step 4: Phase commit**

```bash
git add -A
git commit -m "docs: standardize docstrings in shared/config (phase 2 complete)"
```

---

## Phase 3: Shared Logging (3 files)

### Task 3.1: List logging modules

Run: `find src/f1d/shared/logging -name "*.py" -type f`

Expected files:
- `__init__.py`
- `config.py`
- `context.py` (or `handlers.py`)

### Task 3.2-3.4: Standardize each logging module

Follow same pattern as Phase 2 for each file.

Template for `__init__.py`:
```python
"""Logging package for F1D pipeline.

This package provides structured logging with context propagation
and dual output (console + file).

Modules:
    - config: Logging configuration
    - context: Operation context management
"""
```

### Task 3.5: Verify Phase 3

Run verification commands and commit.

---

## Phase 4: Shared Observability (10 files)

### Task 4.1: List observability modules

Run: `find src/f1d/shared/observability -name "*.py" -type f`

### Task 4.2-4.11: Standardize each observability module

Note: `stats.py` is large (5,309 lines). Process in sections if needed.

Template for `__init__.py`:
```python
"""Observability package for F1D pipeline.

This package provides memory tracking, throughput measurement,
file checksums, and anomaly detection.

Modules:
    - memory: Memory usage tracking
    - throughput: Processing throughput measurement
    - files: File checksum utilities
    - stats: Comprehensive statistics collection
    - anomalies: Anomaly detection (z-score, IQR)
"""
```

### Task 4.12: Verify Phase 4

Run verification commands and commit.

---

## Phase 5: Shared Core Utilities (15 files)

### Task 5.1: List shared utility modules

Run: `ls src/f1d/shared/*.py`

Expected files include:
- `__init__.py`
- `panel_ols.py`
- `iv_regression.py`
- `data_validation.py`
- `path_utils.py`
- `chunked_reader.py`
- `string_matching.py`
- `financial_utils.py`
- `industry_utils.py`
- `centering.py`
- `diagnostics.py`
- `regression_validation.py`
- `output_schemas.py`
- `dual_writer.py`
- `subprocess_validation.py`

### Task 5.2: Standardize src/f1d/shared/__init__.py

**Files:**
- Modify: `src/f1d/shared/__init__.py`

**Step 1: Read current file**

Run: Read `src/f1d/shared/__init__.py`

**Step 2: Write package docstring**

```python
"""Shared utilities for F1D pipeline.

This package provides cross-cutting utilities used across all
pipeline stages.

Key Modules:
    - panel_ols: Panel OLS regression
    - iv_regression: Instrumental variable regression
    - data_validation: DataFrame validation
    - path_utils: Path resolution utilities
    - variables: Variable builder framework

Public API:
    - run_panel_ols: Execute panel regression
    - get_latest_output_dir: Resolve timestamped output
    - DualWriter: Console + file logging
"""
```

**Step 3: Commit**

```bash
git add src/f1d/shared/__init__.py
git commit -m "docs: standardize docstring in shared/__init__.py"
```

### Task 5.3-5.16: Standardize each utility module

Use Library Module Template for each:

```python
"""{module_name} - {one-line description}.

Purpose:
    {What this module provides.}

Key Classes/Functions:
    - {ClassName}: {brief description}
    - {function_name}: {brief description}

Usage:
    from f1d.shared.{module_name} import {ClassName}
"""
```

For functions, ensure Google-style:
```python
def function_name(param: Type) -> ReturnType:
    """One-line description.

    Args:
        param: Description.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When this happens.
    """
```

### Task 5.17: Verify Phase 5

Run verification commands and commit.

---

## Phase 6: Variable Builder Base (1 file)

### Task 6.1: Standardize src/f1d/shared/variables/base.py

**Files:**
- Modify: `src/f1d/shared/variables/base.py`

**Step 1: Read current file**

Run: Read `src/f1d/shared/variables/base.py`

**Step 2: Check if docstring should be preserved**

This file likely has good existing docstrings (noted in audit). Preserve if high-quality.

**Step 3: Only add missing sections if needed**

If docstring exists but is missing Raises sections on functions, add them.

**Step 4: Commit**

```bash
git add src/f1d/shared/variables/base.py
git commit -m "docs: standardize docstring in shared/variables/base.py"
```

---

## Phase 7: Variable Builders (83 files)

### Task 7.1: List variable builder modules

Run: `find src/f1d/shared/variables -name "*.py" -type f ! -name "__pycache__"`

### Task 7.2: Batch process variable builders (10 files per batch)

Process in batches to maintain momentum:

**Batch 1-8: Process 10 files each**

For each file:
1. Read file
2. Check if preservation applies
3. Write/update docstring using Library Module Template
4. Verify syntax
5. Note in running log

Example template for a variable builder:
```python
"""{variable_name} - {one-line description}.

Purpose:
    Builds the {VariableName} column for panel construction.

Key Classes:
    - {VariableName}Builder: Builder class for this variable

Usage:
    from f1d.shared.variables.{variable_name} import {VariableName}Builder
    builder = {VariableName}Builder()
    result = builder.build(years, root_path)
"""
```

### Task 7.3: Verify Phase 7

Run: `pydocstyle --convention=google src/f1d/shared/variables/`
Run: `interrogate -v src/f1d/shared/variables/`

Commit phase completion.

---

## Phase 8: Sample Scripts (7 files)

### Task 8.1: List sample modules

Run: `find src/f1d/sample -name "*.py" -type f`

Expected files:
- `__init__.py`
- `clean_metadata.py`
- `link_entities.py`
- `build_tenure_map.py`
- `assemble_manifest.py`
- `build_sample_manifest.py`
- `utils.py`

### Task 8.2: Standardize src/f1d/sample/__init__.py

Use Package `__init__.py` Template:
```python
"""Sample construction package (Stage 1).

This package provides scripts for building the master sample manifest
linking earnings call transcripts to firms.

Modules:
    - clean_metadata: Clean transcript metadata
    - link_entities: Link companies to CCM/CRSP identifiers
    - build_tenure_map: Build CEO tenure panel
    - assemble_manifest: Assemble final manifest
"""
```

### Task 8.3-8.7: Standardize executable scripts

For executable scripts (have `if __name__ == "__main__"`), use Executable Script Template:

```python
#!/usr/bin/env python3
"""clean_metadata - Clean transcript metadata.

Stage: 1
Entry Point: Yes

Purpose:
    Cleans and normalizes metadata from earnings call transcripts.

Flow:
    1. Load raw transcript metadata
    2. Parse and normalize dates
    3. Extract speaker information
    4. Write cleaned metadata to output

Inputs:
    - inputs/Earnings_Calls_Transcripts/: Raw transcript files

Outputs:
    - outputs/sample/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet

Usage:
    python -m f1d.sample.clean_metadata

Dependencies:
    - pandas, numpy
    - f1d.shared.path_utils
"""
```

**Note:** For `assemble_manifest.py`, preserve existing structured docstring if it's complete.

### Task 8.8: Verify Phase 8

Run verification and commit.

---

## Phase 9: Text Scripts (3 files)

### Task 9.1: List text modules

Run: `find src/f1d/text -name "*.py" -type f`

### Task 9.2: Standardize src/f1d/text/__init__.py

```python
"""Text processing package (Stage 2).

This package provides scripts for tokenizing transcripts and
computing linguistic measures using the Loughran-McDonald dictionary.

Modules:
    - tokenize_transcripts: Tokenize and count LM words
    - build_linguistic_variables: Compute uncertainty/sentiment
"""
```

### Task 9.3-9.4: Standardize executable scripts

Use Executable Script Template for:
- `tokenize_transcripts.py`
- `build_linguistic_variables.py`

### Task 9.5: Verify Phase 9

Run verification and commit.

---

## Phase 10: Panel Builders (15 files)

### Task 10.1: List variables modules

Run: `find src/f1d/variables -name "*.py" -type f`

### Task 10.2: Standardize src/f1d/variables/__init__.py

```python
"""Panel builder package (Stage 3).

This package provides scripts for building regression-ready panels
by merging manifest data with computed variables.

Modules:
    - build_h0_1_manager_clarity_panel: Manager clarity panel
    - build_h0_2_ceo_clarity_panel: CEO clarity panel
    - build_h1_cash_holdings_panel: Cash holdings panel
    - build_h2_investment_panel: Investment efficiency panel
    - build_h3_payout_policy_panel: Payout policy panel
    - build_h4_leverage_panel: Leverage panel
    - build_h5_dispersion_panel: Analyst dispersion panel
    - build_h6_cccl_panel: CCCL instrument panel
    - build_h7_illiquidity_panel: Illiquidity panel
    - build_h8_political_risk_panel: Political risk panel
    - build_h9_takeover_panel: Takeover hazard panel
    - build_h10_tone_at_top_panel: Tone-at-top panel
"""
```

### Task 10.3-10.14: Standardize panel builder scripts

Use Executable Script Template for each `build_h*_*.py` file.

### Task 10.15: Verify Phase 10

Run verification and commit.

---

## Phase 11: Econometric Scripts (17 files)

### Task 11.1: List econometric modules

Run: `find src/f1d/econometric -name "*.py" -type f`

### Task 11.2: Standardize src/f1d/econometric/__init__.py

```python
"""Econometric analysis package (Stage 4).

This package provides scripts for running hypothesis tests and
generating LaTeX regression tables.

Modules:
    - run_h0_1_manager_clarity: Manager fixed effects
    - run_h0_2_ceo_clarity: CEO fixed effects
    - run_h0_3_ceo_clarity_extended: Extended controls robustness
    - run_h0_4_ceo_clarity_regime: Regime analysis
    - run_h0_5_ceo_tone: CEO tone regressions
    - run_h1_cash_holdings: Cash holdings hypothesis
    - run_h2_investment: Investment efficiency
    - run_h3_payout_policy: Payout policy
    - run_h4_leverage: Leverage decisions
    - run_h5_dispersion: Analyst dispersion
    - run_h6_cccl: CCCL instrument IV
    - run_h7_illiquidity: Illiquidity regressions
    - run_h8_political_risk: Political risk interaction
    - run_h9_takeover_hazards: Cox PH survival analysis
    - run_h10_tone_at_top: Tone-at-top Granger test
"""
```

### Task 11.3-11.17: Standardize econometric scripts

Use Executable Script Template for each `run_h*.py` file.

### Task 11.18: Verify Phase 11

Run verification and commit.

---

## Phase 12: Reporting (2 files)

### Task 12.1: List reporting modules

Run: `find src/f1d/reporting -name "*.py" -type f`

### Task 12.2: Standardize src/f1d/reporting/__init__.py

```python
"""Reporting package for F1D pipeline.

This package provides scripts for generating summary statistics
and descriptive tables.

Modules:
    - generate_summary_stats: Summary statistics generation
"""
```

### Task 12.3: Standardize generate_summary_stats.py

Use Executable Script Template.

### Task 12.4: Verify Phase 12

Run verification and commit.

---

## Final Verification

### Task F.1: Run full pydocstyle check

Run: `pydocstyle --convention=google src/f1d/ > docs/pydocstyle_report.txt 2>&1`

Expected: Empty report or only acceptable warnings

### Task F.2: Run full interrogate check

Run: `interrogate src/f1d/`

Expected: 100% coverage

### Task F.3: Run full mypy check

Run: `mypy src/f1d/`

Expected: No new errors compared to baseline

### Task F.4: Run test suite

Run: `pytest tests/ -m "not e2e" -v`

Expected: All tests pass

### Task F.5: Generate final report

Write `docs/DOCSTRING_AUDIT_REPORT.md` with:
- Summary statistics
- Per-phase results
- Files modified/added
- Verification results

### Task F.6: Final commit

```bash
git add docs/DOCSTRING_AUDIT_REPORT.md docs/pydocstyle_report.txt
git commit -m "docs: complete docstring standardization (163 files)

- All modules have Google-style docstrings
- pydocstyle: PASS
- interrogate: 100% coverage
- Tests: PASS"
```

---

## Acceptance Checklist

- [ ] All 163 files have module docstrings
- [ ] All public functions have Google-style docstrings
- [ ] `pydocstyle --convention=google src/f1d/` passes
- [ ] `interrogate src/f1d/` shows 100% coverage
- [ ] `mypy src/f1d/` shows no new errors
- [ ] `pytest tests/ -m "not e2e"` passes
- [ ] Report generated at `docs/DOCSTRING_AUDIT_REPORT.md`

---

*Plan created: 2026-02-26*
*Based on design: docs/plans/2026-02-26-docstring-standardization-design.md*
