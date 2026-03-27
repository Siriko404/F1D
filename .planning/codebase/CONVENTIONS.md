# Coding Conventions

**Analysis Date:** 2026-03-25

## Naming Patterns

**Files:**
- Source modules: `snake_case.py` (e.g., `financial_utils.py`, `panel_ols.py`, `data_validation.py`)
- Econometric runners: `run_h{N}_{hypothesis_name}.py` (e.g., `run_h1_cash_holdings.py`, `run_h16_rd_sales.py`)
- Moderation/channel suites: `run_h{N}_{N}_{channel_name}.py` (e.g., `run_h1_1_cash_tsimm.py`, `run_h1_2_cash_constraint.py`, `run_h13_1_competition.py`)
- Variable builders (Stage 3): `build_h{N}_{hypothesis_name}_panel.py` (e.g., `build_h1_cash_holdings_panel.py`)
- Shared variable modules: `snake_case.py` named after the variable (e.g., `cash_holdings.py`, `amihud_illiq.py`, `johnson_disp.py`, `rd_sales.py`)
- Private engines: `_prefixed_engine.py` (e.g., `_compustat_engine.py`, `_crsp_engine.py`, `_ibes_engine.py`, `_hassan_engine.py`, `_clarity_residual_engine.py`, `_linguistic_engine.py`, `_ibes_detail_engine.py`)
- Test files: `test_{module_name}.py` (e.g., `test_financial_utils.py`, `test_panel_ols.py`)
- Archived code: placed in `_archived/` subdirectories with underscore prefix

**Functions:**
- Use `snake_case` for all functions: `calculate_firm_controls()`, `run_panel_ols()`, `compute_vif()`
- Private/internal functions: prefix with underscore `_check_thin_cells()`, `_format_coefficient_table()`, `_save_latex_table()`
- Factory functions: prefix with `_factory` as inner callable, return via closure pattern
- Builder methods: use `build()` as the primary entry point for `VariableBuilder` subclasses
- CLI parsing: use `parse_arguments()` as the standard name in all runners

**Variables:**
- Local variables: `snake_case` (e.g., `firm_data`, `compustat_work`, `merge_cols`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `KEY_IVS`, `BASE_CONTROLS`, `EXTENDED_CONTROLS`, `MODEL_SPECS`, `MIN_CALLS_PER_FIRM`)
- DataFrame columns from Compustat: preserve original lowercase names (`at`, `dlc`, `dltt`, `oibdp`, `ceq`, `prcc_f`, `xrdy`, `saley`)
- Computed control variables (quarterly engine output): `PascalCase` (`Size`, `BM`, `BookLev`, `ROA`, `CurrentRatio`, `RD_Intensity`, `CashHoldings`, `TobinsQ`, `CapexAt`, `DividendPayer`, `OCF_Volatility`)
- Linguistic variables: `PascalCase` with speaker prefix (`CEO_QA_Uncertainty_pct`, `Manager_Pres_Uncertainty_pct`)
- Lead/lag suffixes: `_lead` for t+1 variables, `_lag` for t-1 variables (e.g., `CashHoldings_lead`, `CapexAt_lead`)

**Types/Classes:**
- Use `PascalCase` for all classes: `VariableBuilder`, `VariableResult`, `VariableStats`, `CompustatEngine`
- Builder classes: `{Variable}Builder` (e.g., `CashHoldingsBuilder`, `SizeBuilder`, `JohnsonDispBuilder`, `RDSalesBuilder`)
- Exception classes: `PascalCase` ending in `Error` (e.g., `FinancialCalculationError`, `CollinearityError`, `WeakInstrumentError`, `DataValidationError`, `OutputResolutionError`, `ConfigError`)
- Pydantic settings: `PascalCase` ending in `Settings` or `Config` (e.g., `DataSettings`, `ProjectConfig`, `HashingConfig`, `EnvConfig`)

## Code Style

**Formatting:**
- Tool: Ruff formatter (replaces Black)
- Line length: 88 characters
- Indent: 4 spaces
- Quote style: double quotes `"`
- Trailing comma: preserved (skip-magic-trailing-comma = false)
- Line ending: auto-detect
- Config: `pyproject.toml` `[tool.ruff.format]`

**Linting:**
- Tool: Ruff linter
- Target Python: 3.9
- Rule sets enabled: E (pycodestyle), W (warnings), F (pyflakes), I (isort), B (flake8-bugbear), C4 (comprehensions), UP (pyupgrade), ARG (unused-arguments), SIM (simplify)
- Ignored rules: E501 (line too long, handled by formatter), B008 (function calls in defaults)
- Per-file ignores: `__init__.py` allows E402/F401; `tests/**` allows S101/ARG
- Config: `pyproject.toml` `[tool.ruff.lint]`

**Type Checking:**
- Tool: mypy (tiered strictness)
- Tier 1 (`f1d.shared.*`): strict mode with `ignore_missing_imports = true`
- Tier 2 (`f1d.sample.*`, `f1d.econometric.*`, `f1d.text.*`, `f1d.financial.*`): relaxed mode allowing untyped defs
- Type stubs installed: `types-pandas`, `types-psutil`, `types-requests`, `types-PyYAML`
- Config: `pyproject.toml` `[tool.mypy]`

**Security Scanning:**
- Tool: Bandit (SAST)
- Excludes: `tests/`, `.___archive/`, `2_Scripts/`
- Skips: B101 (assert in non-test code)
- Config: `pyproject.toml` `[tool.bandit]`

## Import Organization

**Order (enforced by ruff isort):**
1. `from __future__ import annotations` (always first, when used)
2. Standard library imports (`sys`, `os`, `pathlib`, `typing`, `warnings`, `datetime`, `argparse`, `threading`)
3. Third-party imports (`numpy`, `pandas`, `pydantic`, `structlog`, `linearmodels`, `statsmodels`, `lifelines`)
4. First-party imports (`from f1d.shared.*`)

**Path Aliases:**
- `f1d` is the top-level package (configured via `known-first-party = ["f1d"]` in ruff isort)
- No other path aliases are used

**Standard import block in econometric runners:**
```python
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
```

**Import pattern for optional dependencies:**
```python
try:
    from linearmodels.panel.model import PanelOLS
    LINEARMODELS_AVAILABLE = True
except ImportError:
    LINEARMODELS_AVAILABLE = False
    PanelOLS = None  # type: ignore[misc,assignment]
```

## Error Handling

**Custom Exception Hierarchy:**
- Define domain-specific exceptions per module (not a global hierarchy)
- `FinancialCalculationError` in `src/f1d/shared/data_validation.py`
- `DataValidationError` in `src/f1d/shared/data_validation.py`
- `CollinearityError`, `MulticollinearityError` in `src/f1d/shared/panel_ols.py`
- `WeakInstrumentError` in `src/f1d/shared/iv_regression.py`
- `ConfigError` in `src/f1d/shared/config/loader.py`
- `OutputResolutionError` in `src/f1d/shared/path_utils.py`

**Error message pattern -- include context:**
```python
raise FinancialCalculationError(
    f"Cannot calculate firm controls: no Compustat data found. "
    f"gvkey={gvkey}, year={year}. "
    f"Available years for this gvkey: {list(available_years)}. "
    f"Total Compustat records: {len(compustat_df)}"
)
```

**NaN for missing/invalid financial data:**
- Use `np.nan` for invalid ratios (division by zero, negative denominators) rather than raising exceptions
- Only raise exceptions for truly unrecoverable errors (missing gvkey, no matching data)
- Guard divisions: `if data.get("at") and data["at"] > 0 else np.nan`
- Replace inf with NaN before regression: `df = df.replace([np.inf, -np.inf], np.nan)`

**Regression error handling:**
- Wrap `PanelOLS.fit()` in try/except to catch collinearity/singular matrix errors
- Log warning and return `(None, {})` on failure, allowing remaining specs to continue
- Minimum observation guard: skip regression if N < 100

## Logging

**Framework:** structlog (structured logging)

**Configuration:** `src/f1d/shared/logging/config.py`

**Patterns:**
- Get logger per module: `logger = get_logger(__name__)`
- Log with structured key-value pairs: `logger.info("processing_started", rows=1000, stage="financial")`
- Use `OperationContext` for correlated log entries across pipeline stages
- Dual output: colored console + JSON file logging via `configure_dual_output()`
- Run logging setup: `setup_run_logging(log_base_dir, suite_name, timestamp)` captures stdout to log file via TeeOutput

**Console output pattern in runners:**
- Use `print()` with `"="*60` separators for major stages
- Print row counts with `f"{len(df):,}"` formatting (comma-separated)
- Print IV significance with stars inline: `f"  {iv}: beta={beta:.4f} SE={se:.4f} p1={p_one:.4f} {stars}"`

## Comments and Documentation

**Module-level docstrings:**
- Every source module has a detailed header block with: ID, Description, Inputs, Outputs, Dependencies, Author, Date
- Use the box-comment pattern with `====` separators:
```python
"""
================================================================================
STAGE 4: Test H1 Cash Holdings Hypothesis
================================================================================
ID: econometric/test_h1_cash_holdings
Description: Run H1 Cash Holdings hypothesis test using 8 model specifications ...

Model Specifications (8 columns in one table):
    Cols 1-4: DV = CashHoldings (contemporaneous)
    Cols 5-8: DV = CashHoldings_lead (t+1)
    ...

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet

Outputs:
    - outputs/econometric/h1_cash_holdings/{timestamp}/h1_cash_holdings_table.tex
    ...

Deterministic: true
Author: Thesis Author
Date: 2026-03-15
================================================================================
"""
```

**Docstrings:**
- Use Google-style docstrings with Args, Returns, Raises, Example sections
- All public functions and classes have docstrings
- Include type information in Args descriptions

**Inline comments:**
- Use sparingly for non-obvious logic
- Financial formula explanations: `# leverage = (dlc + dltt) / at`
- Model specification comments in econometric runners
- Bad-control exclusion comments: `# NOTE: RD_Intensity EXCLUDED -- DV is R&D-based (bad control).`

**Provenance documentation (per suite):**
- Location: `docs/provenance/{SUITE_ID}.md` (e.g., `H1.md`, `H16.md`, `H1_2.md`)
- Red-team audits: `docs/provenance/Audits/{SUITE_ID}_red_team.md`
- 19 suites have full provenance docs + red-team audits
- Each provenance doc contains: Suite Overview, Model Specification, Variable Definitions, Identification Strategy, Data Flow, Limitations

## Common Patterns

### Econometric Runner Pattern (Stage 4)

Every `run_h{N}_*.py` follows this structure:
1. **Configuration block**: `KEY_IVS`, `BASE_CONTROLS`, `EXTENDED_CONTROLS`, `MODEL_SPECS` (list of dicts), `VARIABLE_LABELS`, `SUMMARY_STATS_VARS`
2. **CLI**: `parse_arguments()` with `--dry-run` and `--panel-path`
3. **Data loading**: `load_panel()` reads parquet from Stage 3 output
4. **Sample filter**: `filter_main_sample()` excludes Finance (ff12=11) and Utility (ff12=8)
5. **Prepare**: `prepare_regression_data()` with DV filter, complete cases, min-calls filter
6. **Regression**: `run_regression()` using `PanelOLS` with firm-clustered SEs
7. **Output**: save diagnostics CSV, LaTeX table, summary stats, attrition table, run manifest, markdown report
8. **Main**: timestamp-based output dir, setup logging, run all specs, save, report

**Standard 8-column specification:**
- Cols 1-4: contemporaneous DV; Cols 5-8: lead DV (t+1)
- Odd cols: Industry FE (FF12 via `other_effects`) + Year FE; Even cols: Firm FE + Year FE
- Cols 1-2, 5-6: Base controls; Cols 3-4, 7-8: Extended controls

**4 key IVs (all simultaneous in every spec):**
```python
KEY_IVS = [
    "CEO_QA_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
    "Manager_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
]
```

**Lagged DV control convention:**
- Lead specs (cols 5-8) include the contemporaneous DV as a control (lagged DV)
- Must be ONE unified row across all specs, not separate variables
- Must appear in ALL specs (both DVs), not just lead specs

**Bad control exclusion:**
- Exclude any control sharing the DV's numerator concept
- E.g., H13 (CapexAt DV) excludes `CapexAt` from controls; H16 (RDSales DV) excludes `RD_Intensity`
- Comment required in docstring: `NOTE: RD_Intensity EXCLUDED -- DV is R&D-based (bad control).`

### Variable Builder Pattern (Stage 3)

Each builder in `src/f1d/shared/variables/` follows:
1. Import `VariableBuilder`, `VariableResult` from `.base`
2. Import engine singleton via `get_engine()` from the private engine module
3. Implement `build(years, root_path) -> VariableResult` returning (file_name, variable_column)
4. Return `VariableResult(data=df, stats=stats, metadata=metadata)`
5. Export via `__all__` list

```python
class CashHoldingsBuilder(VariableBuilder):
    def build(self, years: range, root_path: Path) -> VariableResult:
        manifest = pd.read_parquet(manifest_path, columns=["file_name", "gvkey", "start_date"])
        engine = get_engine()
        merged = engine.match_to_manifest(manifest, root_path)
        data = merged[["file_name", "CashHoldings"]].copy()
        stats = self.get_stats(data["CashHoldings"], "CashHoldings")
        return VariableResult(data=data, stats=stats, metadata={...})
```

### Engine Singleton Pattern

7 private compute engines load expensive data once per process:
- `_compustat_engine.py`: `CompustatEngine` -- raw Compustat quarterly with winsorization
- `_crsp_engine.py`: `CRSPEngine` -- CRSP daily stock returns
- `_ibes_engine.py`: `IbesEngine` -- IBES consensus estimates
- `_ibes_detail_engine.py`: `IbesDetailEngine` -- IBES individual analyst forecasts
- `_linguistic_engine.py`: `LinguisticEngine` -- Stage 2 text analysis outputs
- `_hassan_engine.py`: `HassanEngine` -- Hassan political risk scores
- `_clarity_residual_engine.py`: `ClarityResidualEngine` -- CEO/Manager clarity scores

Access via `get_engine()` function. Thread-safe via `threading.Lock()`.

### Panel Builder Pattern (Stage 3)

Each `build_h{N}_*_panel.py` follows:
1. Import all needed VariableBuilders from `f1d.shared.variables`
2. Load config via `load_variable_config()`, `get_config()`
3. Load manifest, iterate `build()` on each builder
4. Merge all results onto manifest by `file_name` (zero-row-delta enforced)
5. Compute lead variables via firm-year aggregation + shift
6. Assign industry sample (Main/Finance/Utility) via `assign_industry_sample()`
7. Save parquet panel + summary stats + markdown report

### Moderation/Channel Suite Pattern

Channel suites (H1.1, H1.2, H13.1) extend the parent's design:
- Single IV (the parent's strongest signal), mean-centered on Main sample
- Moderator variable (TNIC similarity, credit constraint category, etc.)
- Interaction terms (IV x moderator)
- Industry + FiscalYear FE only (not firm FE -- interaction absorbs variation)
- Extended controls always included
- 2 columns typically (contemporaneous + lead DV)

### Output Path Convention

All outputs use timestamped directories:
```
outputs/{stage}/{suite_id}/{YYYY-MM-DD_HHMMSS}/
```
e.g., `outputs/econometric/h1_cash_holdings/2026-03-18_211024/`

Resolved via `get_latest_output_dir()` which finds the most recent valid timestamp directory.

### LaTeX Table Convention

- Use `.4f` formatting for all coefficients
- Significance stars: `***` p<0.01, `**` p<0.05, `*` p<0.10
- SEs in parentheses on separate row below coefficient
- FE indicators: Yes/blank
- Variable labels use actual pipeline names (not pretty/human-readable labels) per `generate_all_tables.py`
- All control coefficients shown (no "Controls: Yes" shortcut)

### Memory-Safe Builder Convention

- Builders that process large yearly data must use per-gvkey loops with explicit memory cleanup
- Call `gc.collect()` and `del` intermediate DataFrames in yearly iteration loops
- Required for builders touching CRSP daily data or IBES detail data

---

*Convention analysis: 2026-03-25*
