# Phase 31: H3 Payout Policy Variables - Research

**Researched:** 2026-02-05
**Domain:** Payout policy variable construction, dividend stability metrics, 5-year rolling windows
**Confidence:** HIGH

## Summary

This research investigates how to implement H3 (Payout Policy) variable construction according to the locked decisions in CONTEXT.md. The phase requires:

1. **Dividend Policy Stability DV** = `-StdDev(ΔDPS) / Mean(DPS)` over trailing 5 years (higher = more stable)
2. **Payout Flexibility DV** = `% of years with |ΔDPS| > 5% of prior DPS` over 5-year window
3. **Earnings Volatility** = `StdDev(annual EPS)` over trailing 5 years
4. **FCF Growth** = Year-over-year growth in `(OANCF - CAPX) / AT`
5. **Firm Maturity** = `RE/TE` ratio (Retained Earnings / Total Equity - DeAngelo proxy)
6. **Standard Controls** merged from H1 outputs or recomputed (Firm Size, ROA, Tobin's Q, Cash Holdings)

All required Compustat columns (`dvpspq`, `epspxq`, `req`, `seqq`, `oancfy`, `capxy`, `atq`) are **VERIFIED AVAILABLE**. The project has established patterns from H1 (Phase 29) and H2 (Phase 30) that should be followed exactly.

**Primary recommendation:** Follow H1/H2 script patterns exactly. H3 is simpler than H2 (no industry groupings, no cross-sectional regressions) - primarily rolling window statistics and ratio computations.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | >=1.5 | Data manipulation, groupby, rolling windows | Project standard, already in use |
| numpy | >=1.24 | Numerical operations | Project standard |
| pyarrow | >=14.0 | Parquet I/O, schema inspection | Already used for memory-safe Compustat reads |
| yaml | stdlib | Config loading | Project standard |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| psutil | any | Memory tracking | For observability stats |
| time | stdlib | Performance timing | For throughput metrics |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pandas rolling | scipy.stats | pandas is simpler for panel data, already used in H1/H2 |
| manual std calculation | scipy.stats.sem | Not needed; pandas .std() is correct |

**Installation:**
Already available in project environment - no new dependencies needed (verified in H2 phase research).

## Architecture Patterns

### Recommended Project Structure
```
2_Scripts/3_Financial_V2/
├── 3.1_H1Variables.py         # Existing H1 (reference pattern)
├── 3.2_H2Variables.py         # Existing H2 (reference pattern)
├── 3.3_H3Variables.py         # NEW: H3 Payout Policy
└── (shared resources via imports from shared/)
```

### Pattern 1: Annualization of Quarterly Data
**What:** Aggregate quarterly DPS/EPS to annual before computing stability/volatility
**When to use:** Both DVs and Earnings Volatility require annual values
**Example:**
```python
# Source: CONTEXT.md locked decisions + existing H1/H2 patterns
def annualize_quarterly_to_fiscal_year(df: pd.DataFrame, 
                                        value_col: str, 
                                        agg_method: str = "sum") -> pd.DataFrame:
    """
    Aggregate quarterly data to fiscal year level.
    
    For DPS (dvpspq): Sum quarters to get annual DPS
    For EPS (epspxq): Sum quarters to get annual EPS
    
    Args:
        df: Compustat quarterly data with gvkey, fiscal_year, value_col
        value_col: Column to aggregate (e.g., 'dvpspq', 'epspxq')
        agg_method: 'sum' for DPS/EPS, 'last' for point-in-time values
    
    Returns:
        DataFrame with gvkey, fiscal_year, annualized_{value_col}
    """
    # Filter to valid observations
    df_valid = df[df[value_col].notna()].copy()
    
    if agg_method == "sum":
        annual = df_valid.groupby(["gvkey", "fiscal_year"])[value_col].sum().reset_index()
    else:
        # Take last observation per year (for point-in-time values)
        df_sorted = df_valid.sort_values(["gvkey", "fiscal_year", "datadate"])
        annual = df_sorted.groupby(["gvkey", "fiscal_year"])[value_col].last().reset_index()
    
    annual.rename(columns={value_col: f"annual_{value_col}"}, inplace=True)
    
    return annual
```

### Pattern 2: 5-Year Rolling Window Statistics
**What:** Compute rolling statistics (StdDev, count, mean) over trailing 5 years
**When to use:** Dividend stability, payout flexibility, earnings volatility
**Example:**
```python
# Source: Existing H1/H2 patterns (compute_ocf_volatility, compute_efficiency_score)
MIN_YEARS = 2  # Per CONTEXT.md: minimum 2 years required
WINDOW_SIZE = 5  # Trailing 5 years (t-4 to t inclusive)

def compute_rolling_std(df: pd.DataFrame, 
                        value_col: str, 
                        min_years: int = 2, 
                        window: int = 5) -> pd.DataFrame:
    """
    Compute rolling standard deviation over trailing window.
    
    Memory-efficient: uses pandas rolling() instead of manual loops.
    """
    # Sort by gvkey and fiscal_year
    df = df.sort_values(["gvkey", "fiscal_year"])
    
    results = []
    
    for gvkey, group in df.groupby("gvkey"):
        group = group.sort_values("fiscal_year").reset_index(drop=True)
        
        # Compute rolling std
        rolling_std = group[value_col].rolling(window=window, min_periods=min_years).std()
        
        # Keep only valid observations
        mask = rolling_std.notna()
        if mask.any():
            group_result = group.loc[mask, ["gvkey", "fiscal_year"]].copy()
            group_result[f"{value_col}_std"] = rolling_std.loc[mask].values
            results.append(group_result)
    
    if results:
        return pd.concat(results, ignore_index=True)
    else:
        return pd.DataFrame(columns=["gvkey", "fiscal_year", f"{value_col}_std"])
```

### Pattern 3: Dividend Policy Stability (DV1)
**What:** Negative coefficient of variation of DPS changes
**When to use:** H3-01 requirement
**Example:**
```python
# Source: CONTEXT.md H3-01 locked formula
def compute_div_stability(annual_dps_df: pd.DataFrame,
                          min_years: int = 2,
                          window: int = 5) -> pd.DataFrame:
    """
    Compute Dividend Policy Stability = -StdDev(ΔDPS) / Mean(DPS)
    
    Higher values = more stable dividend policy (negative of CV makes it increasing in stability)
    
    Formula per CONTEXT.md:
    - Compute ΔDPS = DPS_t - DPS_{t-1}
    - Rolling 5-year window
    - Stability = -StdDev(ΔDPS) / Mean(DPS) over window
    """
    df = annual_dps_df.sort_values(["gvkey", "fiscal_year"]).copy()
    
    # Compute year-over-year change in DPS
    df["delta_dps"] = df.groupby("gvkey")["annual_dps"].diff()
    
    results = []
    
    for gvkey, group in df.groupby("gvkey"):
        group = group.sort_values("fiscal_year").reset_index(drop=True)
        
        # Rolling statistics
        rolling_delta_std = group["delta_dps"].rolling(window=window, min_periods=min_years).std()
        rolling_dps_mean = group["annual_dps"].rolling(window=window, min_periods=min_years).mean()
        
        for i, (idx, row) in enumerate(group.iterrows()):
            std_val = rolling_delta_std.iloc[i]
            mean_val = rolling_dps_mean.iloc[i]
            
            # Avoid division by zero (mean_dps near zero)
            if pd.notna(std_val) and pd.notna(mean_val) and abs(mean_val) > 0.001:
                div_stability = -std_val / abs(mean_val)  # Negative CV
            else:
                div_stability = np.nan
            
            results.append({
                "gvkey": gvkey,
                "fiscal_year": row["fiscal_year"],
                "div_stability": div_stability,
            })
    
    return pd.DataFrame(results)
```

### Pattern 4: Payout Flexibility (DV2)
**What:** Percentage of years with meaningful dividend changes
**When to use:** H3-02 requirement
**Example:**
```python
# Source: CONTEXT.md H3-02 locked formula
CHANGE_THRESHOLD = 0.05  # 5% threshold per CONTEXT.md

def compute_payout_flexibility(annual_dps_df: pd.DataFrame,
                               min_years: int = 2,
                               window: int = 5,
                               threshold: float = 0.05) -> pd.DataFrame:
    """
    Compute Payout Flexibility = % of years with |ΔDPS| > 5% of prior DPS
    
    Higher values = more flexible/discretionary payout policy
    
    Formula per CONTEXT.md:
    - Change = |DPS_t - DPS_{t-1}| / DPS_{t-1}
    - Meaningful change if > 5%
    - Flexibility = count(meaningful changes) / years_in_window
    """
    df = annual_dps_df.sort_values(["gvkey", "fiscal_year"]).copy()
    
    # Compute lagged DPS
    df["dps_lag"] = df.groupby("gvkey")["annual_dps"].shift(1)
    
    # Compute relative change (avoid division by zero)
    df["rel_change"] = np.where(
        df["dps_lag"].abs() > 0.001,
        (df["annual_dps"] - df["dps_lag"]).abs() / df["dps_lag"].abs(),
        np.nan
    )
    
    # Flag meaningful changes (> 5% threshold)
    df["is_change"] = (df["rel_change"] > threshold).astype(int)
    
    results = []
    
    for gvkey, group in df.groupby("gvkey"):
        group = group.sort_values("fiscal_year").reset_index(drop=True)
        
        # Rolling count of changes and total years
        rolling_changes = group["is_change"].rolling(window=window, min_periods=min_years).sum()
        rolling_count = group["is_change"].rolling(window=window, min_periods=min_years).count()
        
        for i, (idx, row) in enumerate(group.iterrows()):
            changes = rolling_changes.iloc[i]
            count = rolling_count.iloc[i]
            
            if pd.notna(changes) and pd.notna(count) and count >= min_years:
                payout_flexibility = changes / count
            else:
                payout_flexibility = np.nan
            
            results.append({
                "gvkey": gvkey,
                "fiscal_year": row["fiscal_year"],
                "payout_flexibility": payout_flexibility,
            })
    
    return pd.DataFrame(results)
```

### Pattern 5: Sample Scoping for Dividend Payers
**What:** Filter to firms with positive DPS in at least one year of window
**When to use:** Before computing stability/flexibility (undefined for never-payers)
**Example:**
```python
# Source: CONTEXT.md sample scope decisions
def flag_dividend_payers(annual_dps_df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Flag firms as dividend payers if DPS > 0 in at least one year of 5-year window.
    
    Non-payers have undefined stability/flexibility.
    """
    df = annual_dps_df.sort_values(["gvkey", "fiscal_year"]).copy()
    
    # Check if any positive DPS in rolling window
    df["has_dividend"] = (df["annual_dps"] > 0).astype(int)
    
    for gvkey, group in df.groupby("gvkey"):
        rolling_div_years = group["has_dividend"].rolling(window=window, min_periods=1).sum()
        df.loc[group.index, "is_div_payer"] = (rolling_div_years > 0).astype(int)
    
    return df
```

### Anti-Patterns to Avoid
- **Forgetting to annualize quarterly data:** `dvpspq` and `epspxq` are quarterly; must sum to annual before rolling
- **Division by zero in CV:** Use `abs(mean) > 0.001` threshold before computing stability
- **Including non-payers:** Stability/flexibility undefined for firms with no dividends in window
- **Wrong sign on stability:** Formula is `-StdDev/Mean` (negative CV) so higher = more stable

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rolling statistics | Manual window loops | `pandas.DataFrame.rolling()` | Vectorized, handles edge cases |
| Year-over-year diff | Manual shift loops | `groupby().diff()` | Pandas handles group boundaries |
| Quarterly to annual | Custom aggregation | `groupby().sum()` or `.last()` | Handles missing quarters properly |
| Standard controls | Recompute from scratch | Merge from H1 output OR copy compute functions | Tested, verified in Phase 29 |

**Key insight:** H3 is simpler than H2 - no industry-year groupings, no cross-sectional regressions. Focus on clean rolling window implementations and correct formula interpretation.

## Common Pitfalls

### Pitfall 1: Quarterly vs Annual Confusion
**What goes wrong:** Computing stability on quarterly DPS instead of annual
**Why it happens:** Compustat has `dvpspq` which is quarterly dividends per share
**How to avoid:** Always annualize first by summing quarters within fiscal year
```python
# WRONG: Using quarterly directly
df["delta_dps"] = df.groupby("gvkey")["dvpspq"].diff()

# RIGHT: Annualize first
annual_dps = df.groupby(["gvkey", "fiscal_year"])["dvpspq"].sum()
annual_dps["delta_dps"] = annual_dps.groupby("gvkey")["annual_dps"].diff()
```
**Warning signs:** Stability values fluctuating wildly (quarterly noise), too many change events

### Pitfall 2: Division by Zero in Stability Ratio
**What goes wrong:** NaN or Inf values when Mean(DPS) is zero or near-zero
**Why it happens:** Non-dividend payers have zero mean DPS
**How to avoid:** Filter to dividend payers first; add minimum threshold for denominator
```python
# Use threshold to avoid extreme values
if abs(mean_dps) > 0.001:
    stability = -std_delta / abs(mean_dps)
else:
    stability = np.nan
```
**Warning signs:** Infinite or extreme stability values (>10 or <-10)

### Pitfall 3: Overlapping Data in Rolling Windows
**What goes wrong:** Adjacent years share 4 of 5 years, creating serial correlation
**Why it happens:** 5-year rolling windows by design
**How to avoid:** This is expected for panel analysis; document for econometric phase
**Warning signs:** High autocorrelation in stability/flexibility (acceptable, but note it)

### Pitfall 4: Mixing Point-in-Time and Flow Variables
**What goes wrong:** Using end-of-period values for flow variables or vice versa
**Why it happens:** Confusion about Compustat variable semantics
**How to avoid:** 
- DPS, EPS, OANCF, CAPX = flow variables (sum quarters for annual)
- AT, RE, SE = point-in-time (use end-of-year value)
```python
# Flow: sum quarters
annual_dps = df.groupby(["gvkey", "fiscal_year"])["dvpspq"].sum()

# Stock: use end of year (last quarter's value)
annual_equity = df.groupby(["gvkey", "fiscal_year"])["seqq"].last()
```
**Warning signs:** Impossibly large annual DPS values (used last instead of sum)

### Pitfall 5: RE/TE Edge Cases
**What goes wrong:** Negative or zero equity creates invalid maturity ratios
**Why it happens:** Financially distressed firms can have negative equity
**How to avoid:** Filter to positive equity or winsorize
```python
# Handle negative/zero equity
df["firm_maturity"] = np.where(
    df["seqq"] > 0,
    df["req"] / df["seqq"],
    np.nan
)
```
**Warning signs:** Maturity values outside reasonable range (-5 to 5)

### Pitfall 6: FCF Growth Computation
**What goes wrong:** Extreme growth values when prior FCF is near zero
**Why it happens:** Division by small denominator creates outliers
**How to avoid:** Use absolute value in denominator; winsorize; or cap growth at +/-500%
```python
# Use absolute value of prior FCF
df["fcf_growth"] = (df["fcf"] - df["fcf_lag"]) / df["fcf_lag"].abs()
# Then winsorize at 1%/99%
```
**Warning signs:** Growth values > 100 or < -100

## Code Examples

Verified patterns from project sources:

### Loading Compustat with Schema Inspection
```python
# Source: 3.1_H1Variables.py (verified existing pattern)
import pyarrow.parquet as pq

def load_compustat_h3(compustat_file: Path) -> pd.DataFrame:
    """Load Compustat with only H3-required columns"""
    
    # H3-specific columns (verified AVAILABLE 2026-02-05)
    required_cols = [
        "gvkey", "datadate", "fyearq",
        # Dividend variables
        "dvpspq",    # Dividends per Share - Pay Date - Quarterly
        # EPS for earnings volatility
        "epspxq",    # EPS Basic - Excl Extra Items - Quarterly
        # Firm maturity (RE/TE)
        "req",       # Retained Earnings - Quarterly
        "seqq",      # Stockholders Equity - Quarterly
        # FCF components
        "oancfy",    # Operating Cash Flow - Annual
        "capxy",     # Capital Expenditures - Annual
        # Standard variables
        "atq",       # Total Assets - Quarterly
        "cheq",      # Cash and Equivalents - Quarterly
        "iby",       # Income Before Extra - Annual (for ROA if recomputing)
        "ceqq",      # Common Equity - Quarterly (for Tobin's Q if recomputing)
        "cshoq",     # Shares Outstanding - Quarterly
        "prccq",     # Price Close - Quarterly
    ]
    
    # Check schema
    pf = pq.ParquetFile(compustat_file)
    available = set(pf.schema_arrow.names)
    cols_to_read = [c for c in required_cols if c in available]
    
    missing = set(required_cols) - set(cols_to_read)
    if missing:
        print(f"  Warning: Missing columns: {missing}")
    
    df = pd.read_parquet(compustat_file, columns=cols_to_read)
    
    # Normalize gvkey
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["fiscal_year"] = df["fyearq"].astype("Int64")
    
    # Convert numerics
    numeric_cols = [c for c in cols_to_read if c not in ["gvkey", "datadate"]]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
    
    return df
```

### Computing Firm Maturity (RE/TE)
```python
# Source: CONTEXT.md H3-03 locked decision - DeAngelo et al. proxy
def compute_firm_maturity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Firm Maturity = RE / TE (Retained Earnings / Total Equity)
    
    DeAngelo et al. proxy for firm life cycle stage.
    Higher RE/TE = more mature firm (retained more earnings over time)
    
    Uses quarterly values; take end-of-year for each fiscal year.
    """
    print("\nComputing Firm Maturity (RE/TE)...")
    
    # Require positive equity
    df_valid = df[df["seqq"] > 0].copy()
    
    # Compute RE/TE ratio
    df_valid["firm_maturity"] = df_valid["req"] / df_valid["seqq"]
    
    # Keep most recent observation per fiscal year
    result = df_valid.sort_values(
        ["gvkey", "fiscal_year", "datadate"], ascending=[True, True, False]
    ).drop_duplicates(subset=["gvkey", "fiscal_year"], keep="first")
    
    result = result[["gvkey", "fiscal_year", "datadate", "firm_maturity"]].copy()
    
    n_computed = result["firm_maturity"].notna().sum()
    print(f"  Computed firm_maturity for {n_computed:,} observations")
    
    return result
```

### Computing FCF Growth
```python
# Source: CONTEXT.md H3-03 locked formula
def compute_fcf_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute FCF Growth = (FCF_t - FCF_{t-1}) / |FCF_{t-1}|
    
    Where FCF = (OANCF - CAPX) / AT
    """
    print("\nComputing FCF Growth...")
    
    # Require positive AT and valid cash flow
    df_valid = df[(df["atq"] > 0) & (df["oancfy"].notna())].copy()
    
    # Compute FCF/AT
    df_valid["fcf_at"] = (df_valid["oancfy"] - df_valid["capxy"].fillna(0)) / df_valid["atq"]
    
    # Aggregate to annual (take last observation per year)
    annual = df_valid.sort_values(["gvkey", "fiscal_year", "datadate"]).groupby(
        ["gvkey", "fiscal_year"]
    )["fcf_at"].last().reset_index()
    
    # Compute year-over-year growth
    annual = annual.sort_values(["gvkey", "fiscal_year"])
    annual["fcf_lag"] = annual.groupby("gvkey")["fcf_at"].shift(1)
    
    # Growth = (current - prior) / |prior|
    annual["fcf_growth"] = np.where(
        annual["fcf_lag"].abs() > 0.001,
        (annual["fcf_at"] - annual["fcf_lag"]) / annual["fcf_lag"].abs(),
        np.nan
    )
    
    result = annual[["gvkey", "fiscal_year", "fcf_growth"]].copy()
    
    n_computed = result["fcf_growth"].notna().sum()
    print(f"  Computed fcf_growth for {n_computed:,} observations")
    
    return result
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| ln(firm age) from IPO date | RE/TE ratio (DeAngelo) | Context decision | Much better coverage (99.96% vs 41%) |
| Simple coefficient of variation | Negative CV over trailing window | Methodology spec | Higher = more stable (intuitive) |
| Count all dividend changes | Relative threshold (5%) | Methodology spec | Ignores trivial changes |

**Deprecated/outdated:**
- **IPO date for maturity:** Only 41% coverage; RE/TE is superior proxy
- **Absolute DPS changes:** 5% relative threshold is more meaningful

## Open Questions

Things that couldn't be fully resolved:

1. **Partial year handling at sample edges**
   - What we know: Sample is 2002-2018; 5-year window first valid in 2006
   - What's unclear: How to handle 2002-2005 (incomplete windows)
   - Recommendation: Per CONTEXT.md, use available years if >= 2 years; document as data limitation

2. **Treatment of special dividends**
   - What we know: `dvpspq` includes regular and special dividends
   - What's unclear: Whether to separate regular vs special for stability calculation
   - Recommendation: Use total DPS as-is (no separation available); document choice

3. **Negative retained earnings firms**
   - What we know: Accumulated deficit firms have negative RE
   - What's unclear: How to interpret RE/TE for negative RE
   - Recommendation: Allow negative values (valid signal of immaturity); winsorize extreme values

## Sources

### Primary (HIGH confidence)
- **3.1_H1Variables.py** - Verified project pattern for variable construction, rolling windows
- **3.2_H2Variables.py** - Verified project pattern for complex variable construction
- **CONTEXT.md (Phase 31)** - All variable definitions locked
- **Compustat schema inspection** - All required columns verified AVAILABLE (2026-02-05)

### Secondary (MEDIUM confidence)
- **shared/observability_utils.py** - DualWriter, checksum, stats patterns
- **shared/path_utils.py** - Path validation patterns
- **REQUIREMENTS.md** - H3-01 through H3-05 requirement specifications

### Tertiary (LOW confidence)
- None - all findings verified against codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - No new dependencies; uses existing project patterns
- Architecture: HIGH - Direct pattern from H1/H2; simpler than H2
- Variable formulas: HIGH - All locked in CONTEXT.md; Compustat columns verified
- Pitfalls: HIGH - Based on code analysis and Compustat documentation

**Research date:** 2026-02-05
**Valid until:** 2026-03-07 (30 days - stable domain, established patterns)
