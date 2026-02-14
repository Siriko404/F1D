# Phase 59: Critical Bug Fixes - Research

**Researched:** 2026-02-10
**Domain:** Data pipeline bug fixes (H7-H8 data truncation, error handling, division by zero)
**Confidence:** HIGH

## Summary

Phase 59 addresses three critical bugs in the F1D data processing pipeline:

1. **BUG-01: H7-H8 Data Truncation** — Volatility and StockRet control variables are 100% missing for 2005-2018 in H7_Illiquidity.parquet, causing H8 to silently truncate from 39,408 observations (2002-2018) to 12,408 observations (2002-2004).

2. **BUG-02: Empty DataFrame Returns** — 100+ functions return empty containers (dicts, DataFrames, lists) on error paths, hiding useful debugging information.

3. **BUG-03: Division by Zero Guards** — Functions return 0.0 for duration_seconds <= 0, masking underlying data quality issues with transcript timestamps.

The research identified the root causes, existing patterns in the codebase, and testing infrastructure available for regression tests.

**Primary recommendation:** Fix BUG-01 first (highest impact), then BUG-02 (affects debugging), then BUG-03 (affects data quality visibility).

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.x | DataFrame operations | Already used throughout codebase |
| numpy | 1.x | Numerical operations | Already used throughout codebase |
| pytest | 7.x+ | Testing framework | Existing test infrastructure uses pytest |
| parquet | pyarrow | File I/O | Standard format for pipeline outputs |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| logging | stdlib | Structured logging | For exception messages and warnings |
| unittest.mock | stdlib | Test doubles | For testing error conditions |
| hashlib | stdlib | Checksums | For regression test baselines |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom exceptions | Built-in exceptions | Custom exceptions carry more context |
| pytest | unittest | pytest has better fixtures already defined |
| Raising exceptions | Returning empty containers | Exceptions force error handling, empty containers hide bugs |

**Installation:** All dependencies are already installed in the project environment.

## Architecture Patterns

### Recommended Project Structure

The bug fixes follow the existing project structure:

```
2_Scripts/
├── 3_Financial_V2/          # BUG-01 fixes (H7 script)
│   ├── 3.7_H7IlliquidityVariables.py  # Add Volatility calculation
│   └── 3.8_H8TakeoverVariables.py     # May need updates
├── shared/                  # BUG-02 fixes
│   ├── financial_utils.py  # Replace empty returns with exceptions
│   └── path_utils.py        # Already has PathValidationError
└── 2_Text/                 # BUG-03 fixes
    ├── 2.1_TokenizeAndCount.py
    └── 2.2_ConstructVariables.py

tests/
├── unit/                   # Unit tests for individual functions
├── integration/            # Integration tests for error propagation
└── regression/             # Regression tests to prevent bug recurrence
```

### Pattern 1: Custom Exception Hierarchy

**What:** The codebase already uses custom exceptions for validation errors.

**When to use:** For all error conditions that should halt processing.

**Example:**

```python
# Source: 2_Scripts/shared/data_validation.py
class DataValidationError(Exception):
    """Raised when input data validation fails."""
    pass
```

**Extend with:**

```python
# New: For financial calculation errors
class FinancialCalculationError(Exception):
    """Raised when financial metric calculation fails."""
    pass

# New: For data quality issues
class DataQualityError(Exception):
    """Raised when data quality issues are detected."""
    pass
```

### Pattern 2: Context-Rich Exception Messages

**What:** Include file paths, variable names, and relevant values in exception messages.

**When to use:** All new exception raises.

**Example:**

```python
# Instead of:
return {}

# Use:
raise FinancialCalculationError(
    f"Cannot calculate firm controls: "
    f"gvkey={row.get('gvkey')}, year={year}, "
    f"firm_data.empty={firm_data.empty}, "
    f"Compustat records={len(compustat_df)}"
)
```

### Pattern 3: Regression Tests with Checksums

**What:** Use SHA256 checksums of output files to detect unintended changes.

**When to use:** For BUG-01 to prevent data truncation recurrence.

**Example:**

```python
# Source: tests/regression/generate_baseline_checksums.py
def test_h7_output_stable():
    """Verify H7 output hasn't changed (detects data truncation)."""
    output_file = Path("4_Outputs/3_Financial_V2/latest/H7_Illiquidity.parquet")
    actual = compute_file_checksum(output_file)
    expected = load_baseline_checksum("H7_Illiquidity.parquet")
    assert actual == expected, "H7 output changed - possible data truncation"
```

### Anti-Patterns to Avoid

- **Empty returns on error:** `return {}`, `return None`, `return pd.DataFrame()` — these hide errors
- **Silent fallback to 0.0:** `return 0.0 if duration <= 0` — masks data quality issues
- **Generic exceptions:** Use specific exception types, not bare `raise Exception()`

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Test fixtures | Custom setup/teardown | pytest fixtures | Already defined in conftest.py |
| Checksum calculation | Custom SHA256 code | `compute_file_checksum()` from observability_utils | Already exists |
| Exception handling patterns | Ad-hoc try/except | Context managers and custom exception classes | Consistent error handling |
| Test data generation | Mock DataFrames manually | pytest fixtures with sample data | Already defined in conftest.py |

**Key insight:** The codebase has existing infrastructure for testing, checksums, and exceptions. Use it rather than building new patterns.

## Common Pitfalls

### Pitfall 1: Modifying H7 Without Updating H8

**What goes wrong:** Fixing H7 to calculate Volatility directly from CRSP may produce different output formats than H8 expects.

**Why it happens:** H8 reads H7_Illiquidity.parquet and expects specific column names.

**How to avoid:**
1. Preserve exact column names from H7 output
2. Verify H8 can load the new H7 output
3. Run integration test: H7 -> H8 pipeline

**Warning signs:** H8 fails to load H7 output, column name mismatches in merge operations

### Pitfall 2: Breaking Downstream Scripts

**What goes wrong:** Changing `return {}` to `raise Exception` breaks scripts that expect empty containers.

**Why it happens:** Callers may have `if not result:` checks that expect empty containers.

**How to avoid:**
1. Audit all callers before changing function signatures
2. Update callers to handle exceptions explicitly
3. Use grep to find all call sites: `grep -r "function_name(" 2_Scripts/`

**Warning signs:** Scripts fail with `TypeError: cannot unpack empty iterable`

### Pitfall 3: Test Data Doesn't Cover Edge Cases

**What goes wrong:** Tests pass with synthetic data but fail with real data.

**Why it happens:** Test fixtures don't include missing values, edge cases, or corrupt data.

**How to avoid:**
1. Use real data samples from actual pipeline outputs
2. Include tests with missing values, empty DataFrames
3. Include tests with division by zero conditions

**Warning signs:** All tests pass but pipeline fails in production

### Pitfall 4: Ignoring Logging Context

**What goes wrong:** Exceptions don't include enough context to debug issues.

**Why it happens:** Generic exception messages without file paths, gvkey, year, etc.

**How to avoid:**
1. Include file paths in all exception messages
2. Include relevant identifiers (gvkey, year, permno)
3. Include the operation that failed

**Warning signs:** Need to add print statements to debug failures

## Code Examples

### BUG-01 Fix: Calculate Volatility in H7 Script

**Current code (BUG-01):**

```python
# From 3.7_H7IlliquidityVariables.py, lines 269-299
def load_market_variables(market_dir, years):
    """Load market variables for additional controls"""
    dfs = []
    for year in years:
        fp = market_dir / f"market_variables_{year}.parquet"
        if fp.exists():
            df = pd.read_parquet(fp)
            dfs.append(df)
    if not dfs:
        return None  # BUG: Returns None, Volatility/StockRet missing for 2005-2018
    # ...
```

**Fixed code:**

```python
# From 3.7_H7IlliquidityVariables.py, lines 448-513
def calculate_stock_volatility_and_returns(crsp_df, permno_list=None, min_days=50):
    """
    Calculate annualized stock return volatility and annual stock returns from CRSP daily data.

    Volatility = Annualized standard deviation of daily returns * 100
    StockRet = Cumulative annual return * 100

    Args:
        crsp_df: CRSP daily data with PERMNO, date, RET
        permno_list: Optional list of PERMNOs to filter for
        min_days: Minimum trading days required (default: 50)

    Returns:
        DataFrame with PERMNO, year, Volatility, StockRet
    """
    print("\nCalculating stock volatility and returns from CRSP...")

    # Filter to sample permnos if provided
    if permno_list is not None:
        crsp_df = crsp_df[crsp_df["PERMNO"].isin(permno_list)].copy()

    # Add year
    crsp_df["year"] = crsp_df["date"].dt.year

    # Filter valid returns
    valid = crsp_df[
        (crsp_df["RET"].notna()) &
        (crsp_df["RET"].between(-0.66, 0.66))
    ].copy()

    # Calculate annual metrics for each firm-year
    def calc_metrics(group):
        rets = group["RET"].dropna()
        n = len(rets)
        if n < min_days:
            return pd.Series({
                "Volatility": np.nan,
                "StockRet": np.nan,
                "n_obs": n
            })
        # Daily volatility (std dev), annualized by sqrt(252) and convert to percent
        vol = rets.std() * 100 * (252 ** 0.5)
        # Annual stock return: (1 + r1*r2*...*rn) - 1, * 100
        stock_ret = ((1 + rets).prod() - 1) * 100
        return pd.Series({
            "Volatility": vol,
            "StockRet": stock_ret,
            "n_obs": n
        })

    metrics_df = (valid.groupby(["PERMNO", "year"])
                    .apply(calc_metrics, include_groups=False)
                    .reset_index())

    # Require minimum trading days
    metrics_df = metrics_df[metrics_df["n_obs"] >= min_days].copy()

    print(f"  Computed metrics for {len(metrics_df):,} firm-years")
    return metrics_df[["PERMNO", "year", "Volatility", "StockRet"]]
```

### BUG-02 Fix: Replace Empty Returns with Exceptions

**Current code (BUG-02):**

```python
# From shared/financial_utils.py, lines 28-53
def calculate_firm_controls(
    row: pd.Series, compustat_df: pd.DataFrame, year: int
) -> dict:
    """Calculate firm-level control variables from Compustat data."""
    gvkey = row.get("gvkey")
    if gvkey is None:
        return {}  # BUG: Silent failure, hides missing gvkey

    # Get firm's data for the year
    firm_data = compustat_df[
        (compustat_df["gvkey"] == gvkey) & (compustat_df["fyear"] == year)
    ]

    if firm_data.empty:
        return {}  # BUG: Silent failure, hides missing data
```

**Fixed code:**

```python
# Add new exception class
class FinancialCalculationError(Exception):
    """Raised when financial metric calculation fails."""
    pass

def calculate_firm_controls(
    row: pd.Series, compustat_df: pd.DataFrame, year: int
) -> dict:
    """
    Calculate firm-level control variables from Compustat data.

    Raises:
        FinancialCalculationError: If gvkey is missing or data not found
    """
    gvkey = row.get("gvkey")
    if gvkey is None:
        raise FinancialCalculationError(
            f"Cannot calculate firm controls: missing gvkey in row, "
            f"row columns: {list(row.index)}"
        )

    # Get firm's data for the year
    firm_data = compustat_df[
        (compustat_df["gvkey"] == gvkey) & (compustat_df["fyear"] == year)
    ]

    if firm_data.empty:
        # Provide context for debugging
        available_years = compustat_df[compustat_df["gvkey"] == gvkey]["fyear"].unique()
        raise FinancialCalculationError(
            f"Cannot calculate firm controls: no data found for "
            f"gvkey={gvkey}, year={year}. "
            f"Available years for this gvkey: {list(available_years)}. "
            f"Total Compustat records: {len(compustat_df)}"
        )
```

### BUG-03 Fix: Log Instead of Silent 0.0

**Current code (BUG-03):**

```python
# From 2.1_TokenizeAndCount.py, lines 565-579
def calculate_throughput(rows_processed, duration_seconds):
    """
    Calculate throughput in rows per second.

    Returns:
        Throughput in rows per second (rounded to 2 decimals)
        Returns 0.0 if duration_seconds <= 0 to avoid division by zero
    """
    if duration_seconds <= 0:
        return 0.0  # BUG: Silent masking of invalid duration
    return round(rows_processed / duration_seconds, 2)
```

**Fixed code:**

```python
import logging

logger = logging.getLogger(__name__)

def calculate_throughput(rows_processed, duration_seconds):
    """
    Calculate throughput in rows per second.

    Args:
        rows_processed: Number of rows processed
        duration_seconds: Duration in seconds

    Returns:
        Throughput in rows per second (rounded to 2 decimals)

    Raises:
        ValueError: If duration_seconds <= 0 (indicates timing error)
    """
    if duration_seconds <= 0:
        logger.warning(
            f"Invalid duration_seconds={duration_seconds} <= 0, "
            f"rows_processed={rows_processed}. "
            f"This may indicate a timing error in the pipeline."
        )
        raise ValueError(
            f"Cannot calculate throughput: duration_seconds={duration_seconds} <= 0. "
            f"rows_processed={rows_processed}. "
            f"Check script timing logic."
        )
    return round(rows_processed / duration_seconds, 2)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Empty returns on error | Exceptions with context | Phase 59 (planned) | Forces error handling, better debugging |
| Silent 0.0 for division by zero | Logging + ValueError | Phase 59 (planned) | Exposes data quality issues |
| External market_variables files | Direct CRSP calculation | Phase 59 (planned) | Eliminates data truncation bug |
| No regression tests | Checksum-based regression tests | Phase 59 (planned) | Prevents bug recurrence |

**Deprecated/outdated:**
- **Empty return pattern:** `return {}` on error — should raise exceptions instead
- **Silent fallback to 0.0:** Masks underlying data issues
- **Dependency on market_variables files:** Incomplete data coverage

## Open Questions

1. **Extent of empty return pattern audit**

   What we know: 100+ functions return empty containers based on grep results.
   What's unclear: Exact count and priority order for fixing.

   Recommendation: Focus on shared/financial_utils.py and V2 scripts first (highest impact).

2. **Backward compatibility for H7 output changes**

   What we know: H8 reads H7_Illiquidity.parquet as base dataset.
   What's unclear: Whether H8 depends on exact column names or structure.

   Recommendation: Preserve exact column names from existing H7 output; only add missing values.

3. **Logging configuration for pipeline scripts**

   What we know: Scripts use DualWriter for stdout/stderr logging.
   What's unclear: Whether a separate logger module is needed.

   Recommendation: Extend existing DualWriter pattern or use Python's logging module for exceptions.

4. **Test data availability for regression tests**

   What we know: tests/conftest.py defines fixtures for synthetic data.
   What's unclear: Whether real H7/H8 output samples exist for baseline checksums.

   Recommendation: Create baseline from current H7 output (39,408 rows, 2002-2018) as "good" reference.

## Sources

### Primary (HIGH confidence)

- **Source: Codebase inspection** — Read H7/H8 scripts, shared utilities
  - File: `2_Scripts/3_Financial_V2/3.7_H7IlliquidityVariables.py` — Complete H7 script with existing Volatility calculation function
  - File: `2_Scripts/3_Financial_V2/3.8_H8TakeoverVariables.py` — Complete H8 script showing merge logic
  - File: `2_Scripts/shared/financial_utils.py` — Empty return patterns in calculate_firm_controls()
  - File: `2_Scripts/shared/data_validation.py` — Existing DataValidationError pattern
  - File: `2_Scripts/2_Text/2.1_TokenizeAndCount.py` — calculate_throughput with silent 0.0 return

- **Source: Debug documentation** — `.planning/debug/h7-h8-v2-sample-size-bug.md`
  - Root cause analysis: Volatility/StockRet 100% missing for 2005-2018
  - Current state: H7 has 39,408 rows (2002-2018) but H8 only 12,408 rows (2002-2004)

- **Source: Test infrastructure** — `tests/conftest.py`
  - Existing pytest fixtures for sample DataFrames
  - Test patterns already established

- **Source: REQUIREMENTS.md** — `.planning/REQUIREMENTS.md`
  - BUG-01 through BUG-03 requirement specifications

### Secondary (MEDIUM confidence)

- **Source: H7/H8 output documentation**
  - File: `4_Outputs/4_Econometric_V2/H7_Hypothesis_Documentation.md` — Shows current N=26,135 (truncated)
  - File: `4_Outputs/4_Econometric_V2/H8_Hypothesis_Documentation.md` — Different H8 (not takeover H8)

### Tertiary (LOW confidence)

- None — All findings verified from codebase inspection

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in use
- Architecture: HIGH - Existing codebase patterns well understood
- Pitfalls: HIGH - Root causes identified in code
- Testing patterns: HIGH - Existing test infrastructure reviewed

**Research date:** 2026-02-10
**Valid until:** 30 days (stable codebase, patterns unlikely to change)

**Key findings for planning:**

1. BUG-01 fix requires:
   - Calling existing `calculate_stock_volatility_and_returns()` in H7 main()
   - Merging results via permno crosswalk
   - Ensuring Volatility/StockRet columns are populated for all years

2. BUG-02 fix requires:
   - Creating `FinancialCalculationError` exception class
   - Auditing all `return {}` patterns in shared/financial_utils.py
   - Updating callers to handle exceptions

3. BUG-03 fix requires:
   - Adding logging to `calculate_throughput()` and similar functions
   - Raising `ValueError` for invalid durations instead of returning 0.0
   - Investigating root cause of duration <= 0 in transcript processing

4. Regression test requires:
   - Creating checksum baseline from corrected H7 output
   - Testing year coverage (2002-2018, not just 2002-2004)
   - Testing that H8 can load corrected H7 output
