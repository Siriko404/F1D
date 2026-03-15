# Coding Conventions

**Analysis Date:** 2026-03-15

## Naming Patterns

**Files:**
- Source modules: `snake_case.py` (e.g., `financial_utils.py`, `panel_ols.py`, `data_validation.py`)
- Econometric runners: `run_h{N}_{hypothesis_name}.py` (e.g., `run_h1_cash_holdings.py`, `run_h7_illiquidity.py`)
- Variable builders: `snake_case.py` named after the variable (e.g., `cash_holdings.py`, `amihud_illiq.py`, `earnings_surprise.py`)
- Test files: `test_{module_name}.py` (e.g., `test_financial_utils.py`, `test_panel_ols.py`)
- Config files: `snake_case.py` (e.g., `base.py`, `loader.py`, `step_configs.py`)
- Archived code: placed in `_archived/` subdirectories with underscore prefix

**Functions:**
- Use `snake_case` for all functions: `calculate_firm_controls()`, `run_panel_ols()`, `compute_vif()`
- Private/internal functions: prefix with underscore `_check_thin_cells()`, `_format_coefficient_table()`, `_finalize_data()`
- Factory functions: prefix with `_factory` as inner callable, return via closure pattern
- Builder methods: use `build()` as the primary entry point for `VariableBuilder` subclasses

**Variables:**
- Local variables: `snake_case` (e.g., `firm_data`, `compustat_work`, `merge_cols`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `LINEARMODELS_AVAILABLE`, `INPUT_SCHEMAS`, `DEFAULT_LOG_DIR`)
- DataFrame columns from Compustat: preserve original lowercase names (`at`, `dlc`, `dltt`, `oibdp`, `ceq`, `prcc_f`)
- Computed control variables (annual): `snake_case` (`size`, `leverage`, `profitability`, `market_to_book`)
- Computed control variables (quarterly): `PascalCase` (`Size`, `BM`, `Lev`, `ROA`, `CurrentRatio`, `RD_Intensity`)

**Types/Classes:**
- Use `PascalCase` for all classes: `VariableBuilder`, `VariableResult`, `VariableStats`
- Exception classes: `PascalCase` ending in `Error` (e.g., `FinancialCalculationError`, `CollinearityError`, `WeakInstrumentError`, `DataValidationError`)
- Pydantic settings: `PascalCase` ending in `Settings` or `Config` (e.g., `DataSettings`, `ProjectConfig`, `HashingConfig`)

## Code Style

**Formatting:**
- Tool: Ruff formatter (replaces Black)
- Line length: 88 characters
- Indent: 4 spaces
- Quote style: double quotes `"`
- Trailing comma: preserved (skip-magic-trailing-comma = false)
- Line ending: auto-detect

**Linting:**
- Tool: Ruff linter
- Target Python: 3.9
- Rule sets enabled: E (pycodestyle), W (warnings), F (pyflakes), I (isort), B (flake8-bugbear), C4 (comprehensions), UP (pyupgrade), ARG (unused-arguments), SIM (simplify)
- Ignored rules: E501 (line too long, handled by formatter), B008 (function calls in defaults)
- Per-file ignores: `__init__.py` allows E402/F401; `tests/**` allows S101/ARG

**Type Checking:**
- Tool: mypy (tiered strictness)
- Tier 1 (`f1d.shared.*`): strict mode with `ignore_missing_imports = true`
- Tier 2 (`f1d.sample.*`, `f1d.econometric.*`, etc.): relaxed mode allowing untyped defs
- Type stubs installed: `types-pandas`, `types-psutil`, `types-requests`, `types-PyYAML`

## Import Organization

**Order (enforced by ruff isort):**
1. `from __future__ import annotations` (when used)
2. Standard library imports (`sys`, `os`, `pathlib`, `typing`, `warnings`, `datetime`)
3. Third-party imports (`numpy`, `pandas`, `pydantic`, `structlog`, `linearmodels`, `statsmodels`)
4. First-party imports (`from f1d.shared.*`)

**Path Aliases:**
- `f1d` is the top-level package (configured via `known-first-party = ["f1d"]` in ruff isort)
- No other path aliases are used

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
- `CollinearityError`, `MulticollinearityError` in `src/f1d/shared/panel_ols.py`
- `WeakInstrumentError` in `src/f1d/shared/iv_regression.py`
- `DataValidationError` in `src/f1d/shared/data_validation.py`
- `ConfigError` in `src/f1d/shared/config/loader.py`

**Error message pattern:**
- Include context about what failed, what was expected, and what was found
- Example from `src/f1d/shared/financial_utils.py`:
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

## Logging

**Framework:** structlog (structured logging)

**Configuration:** `src/f1d/shared/logging/config.py`

**Patterns:**
- Get logger per module: `logger = get_logger(__name__)`
- Log with structured key-value pairs: `logger.info("processing_started", rows=1000)`
- Use `OperationContext` for correlated log entries across pipeline stages
- Dual output: colored console + JSON file logging via `configure_dual_output()`

## Comments

**Module-level docstrings:**
- Every source module has a detailed header block with: ID, Description, Inputs, Outputs, Dependencies, Author, Date
- Use the box-comment pattern (with `====` separators) for module headers:
```python
"""
================================================================================
SHARED MODULE: Panel OLS with Fixed Effects
================================================================================
ID: shared/panel_ols
Description: ...
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

## Function Design

**Size:** Functions are generally 20-60 lines. Larger functions (~100 lines) exist in econometric runners but are structured linearly.

**Parameters:**
- Use type hints on all parameters: `def calculate_firm_controls(row: pd.Series, compustat_df: pd.DataFrame, year: int) -> Dict[str, Union[float, int, None]]:`
- Use `Optional[X]` for nullable parameters with `None` defaults
- Factory functions accept `**kwargs` for extensibility

**Return Values:**
- Financial calculations return `Dict[str, Union[float, int, None]]`
- Builders return `VariableResult` dataclass (data + stats + metadata)
- Validation functions return `bool` or raise exceptions
- Panel regression returns `Dict[str, Any]` with standardized keys

## Module Design

**Exports:**
- Use explicit `__all__` lists in `__init__.py` files
- Re-export commonly used symbols from package `__init__.py` for convenience
- Example: `src/f1d/shared/config/__init__.py` re-exports all config classes

**Barrel Files:**
- `__init__.py` files serve as barrel re-exports for packages (`config`, `logging`, `observability`, `variables`)
- Include comprehensive `__all__` lists

**Base Class Pattern (Variable Builders):**
- `VariableBuilder` base class in `src/f1d/shared/variables/base.py`
- Each variable has its own module file (e.g., `cash_holdings.py`, `amihud_illiq.py`)
- Subclasses implement `build()` method returning `VariableResult`

**Configuration Pattern:**
- Pydantic `BaseSettings` models in `src/f1d/shared/config/base.py`
- YAML loading via `ProjectConfig.from_yaml()` class method
- Environment variable overrides with `F1D_` prefix (e.g., `F1D_DATA__YEAR_START`)
- Caching via `get_config()` in `src/f1d/shared/config/loader.py`

---

*Convention analysis: 2026-03-15*
