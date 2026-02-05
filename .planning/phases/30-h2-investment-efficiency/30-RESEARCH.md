# Phase 30: H2 Investment Efficiency Variables - Research

**Researched:** 2026-02-04
**Domain:** Investment efficiency variable construction, Fama-French industry classification, IBES-Compustat linking
**Confidence:** MEDIUM

## Summary

This research investigates how to implement H2 (Investment Efficiency) variable construction according to the locked decisions in CONTEXT.md. The phase requires:

1. **Over/Underinvestment classification** using Capex/Depreciation thresholds with industry-year comparisons
2. **5-year rolling efficiency scores** tracking inefficient investment years
3. **Biddle et al. (2009) ROA residual methodology** via industry-year cross-sectional regressions
4. **IBES-based analyst dispersion** with CUSIP-based linking
5. **FF48 industry classification** from Siccodes48.txt with FF12 fallback

The project already has established patterns from H1 (Phase 29) that should be followed: DualWriter logging, timestamped outputs, PyArrow schema inspection for Compustat, and the existing IBES-CUSIP linking pattern in `3.1_FirmControls.py`.

**Primary recommendation:** Follow H1 script pattern exactly, with additional complexity for industry-year grouping operations and cross-sectional regressions.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | >=1.5 | Data manipulation, groupby operations | Project standard, already in use |
| numpy | >=1.24 | Numerical operations, rolling windows | Project standard |
| statsmodels | >=0.14 | OLS regressions for residual extraction | Industry standard for econometrics |
| pyarrow | >=14.0 | Parquet I/O, schema inspection | Already used for memory-safe Compustat reads |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| zipfile | stdlib | Parse Siccodes48.zip FF industry files | For building SIC-to-FF48 mapping |
| scipy.stats | >=1.10 | Optional statistical functions | If more complex stats needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| statsmodels OLS | sklearn LinearRegression | statsmodels has better residual handling, standard errors |
| pandas groupby | dask groupby | Not needed for dataset size; pandas is simpler |

**Installation:**
Already available in project environment - no new dependencies needed.

## Architecture Patterns

### Recommended Project Structure
```
2_Scripts/3_Financial_V2/
├── 3.1_H1Variables.py         # Existing H1 (reference pattern)
├── 3.2_H2Variables.py         # NEW: H2 Investment Efficiency
├── README.md                  # Existing documentation
└── (shared resources via imports from shared/)
```

### Pattern 1: Industry Classification Lookup
**What:** Build SIC-to-FF48 mapping from Siccodes48.zip, with FF12 fallback
**When to use:** Any variable requiring industry-year grouping
**Example:**
```python
# Source: Project's shared/industry_utils.py + Siccodes48.txt format
def build_ff_industry_mapping(siccodes_path: Path, num_industries: int = 48) -> Dict[int, int]:
    """
    Parse Fama-French industry classification from Siccodes zip file.
    
    Returns dict: SIC code -> FF industry number
    Unmapped SICs -> 48 (Other)
    """
    from shared.industry_utils import parse_ff_industries
    
    mapping = parse_ff_industries(siccodes_path, num_industries)
    # Returns: {sic_code: (industry_code, industry_name)}
    # Convert to {sic_code: industry_code}
    return {sic: code for sic, (code, name) in mapping.items()}

def assign_ff48_industry(df: pd.DataFrame, ff48_map: Dict[int, int]) -> pd.DataFrame:
    """Assign FF48 industry code; unmapped -> 48 (Other)"""
    df = df.copy()
    df["sic"] = pd.to_numeric(df["sic"], errors="coerce").astype("Int64")
    df["ff48"] = df["sic"].map(ff48_map).fillna(48).astype(int)
    return df
```

### Pattern 2: Industry-Year Grouping with Minimum Cell Size
**What:** Compute industry-year medians/means with fallback for thin cells
**When to use:** Over/underinvestment thresholds, industry CapEx intensity
**Example:**
```python
# Source: Based on project CONTEXT.md decisions
MIN_FF48_CELL = 5   # Minimum firms for FF48-year cell
MIN_FF12_CELL = 5   # Minimum firms for FF12 fallback

def compute_industry_year_median(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """
    Compute industry-year median with FF12 fallback for thin FF48 cells.
    """
    # First try FF48 grouping
    grouped = df.groupby(["ff48", "fiscal_year"])
    cell_sizes = grouped[value_col].transform("count")
    
    # Mark thin cells for fallback
    df["use_ff12"] = cell_sizes < MIN_FF48_CELL
    
    # Compute FF48 medians where cell is thick enough
    ff48_medians = grouped[value_col].transform("median")
    
    # Compute FF12 medians for fallback
    ff12_medians = df.groupby(["ff12", "fiscal_year"])[value_col].transform("median")
    
    # Apply fallback
    df[f"{value_col}_ind_median"] = np.where(
        df["use_ff12"], ff12_medians, ff48_medians
    )
    
    return df
```

### Pattern 3: Cross-Sectional Regression per Industry-Year
**What:** Run OLS regressions within each FF48-year cell, extract residuals
**When to use:** Biddle et al. ROA residual methodology
**Example:**
```python
# Source: Biddle, Hilary, Verdi (2009) methodology
import statsmodels.api as sm

MIN_REGRESSION_OBS = 20  # Per CONTEXT.md

def compute_roa_residuals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run industry-year cross-sectional regressions:
    Delta_ROA_{t+2} = alpha + beta1*Capex_AT + beta2*TobinsQ + beta3*Cash + beta4*Leverage + epsilon
    
    Residual = actual - predicted
    """
    residuals = []
    
    for (ind, year), group in df.groupby(["ff48", "fiscal_year"]):
        if len(group) < MIN_REGRESSION_OBS:
            # Fall back to FF12 if FF48 cell too small
            continue
        
        # Prepare regression data
        y = group["delta_roa_t2"]  # ROA(t+2) - ROA(t)
        X = group[["capex_at", "tobins_q", "cash_holdings", "leverage"]]
        X = sm.add_constant(X)
        
        # Drop rows with any missing values
        valid = y.notna() & X.notna().all(axis=1)
        if valid.sum() < MIN_REGRESSION_OBS:
            continue
            
        y_valid = y[valid]
        X_valid = X[valid]
        
        try:
            model = sm.OLS(y_valid, X_valid).fit()
            predicted = model.predict(X_valid)
            
            for idx, pred in zip(y_valid.index, predicted):
                residuals.append({
                    "index": idx,
                    "roa_residual": y_valid.loc[idx] - pred,
                    "predicted_delta_roa": pred,
                })
        except Exception:
            continue  # Skip problematic groups
    
    return pd.DataFrame(residuals).set_index("index")
```

### Pattern 4: IBES-Compustat Linking via CUSIP8
**What:** Match IBES analyst data to Compustat firms using 8-digit CUSIP
**When to use:** Analyst dispersion control variable
**Example:**
```python
# Source: Existing 3.1_FirmControls.py pattern (verified)
def link_ibes_to_compustat(ibes_df: pd.DataFrame, ccm_file: Path) -> pd.DataFrame:
    """
    Link IBES to Compustat via 8-digit CUSIP through CCM.
    
    IBES has CUSIP (8-digit), CCM has cusip + gvkey.
    Join on first 8 characters of CUSIP.
    """
    # Load CCM linking table
    ccm = pd.read_parquet(ccm_file, columns=["cusip", "gvkey"])
    ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]
    ccm_lookup = ccm[["cusip8", "gvkey"]].drop_duplicates().dropna()
    ccm_lookup["gvkey"] = ccm_lookup["gvkey"].astype(str).str.zfill(6)
    
    # Link IBES
    ibes_df["cusip8"] = ibes_df["CUSIP"].astype(str).str[:8]
    ibes_linked = ibes_df.merge(ccm_lookup, on="cusip8", how="inner")
    
    return ibes_linked
```

### Pattern 5: Analyst Dispersion with Edge Case Handling
**What:** Compute dispersion = STDEV / |MEANEST| with safeguards
**When to use:** H2-05 Analyst Dispersion control
**Example:**
```python
# Source: CONTEXT.md decisions
MIN_ANALYSTS = 2        # NUMEST >= 2 required
MIN_MEANEST_ABS = 0.01  # Avoid extreme CV with near-zero mean

def compute_analyst_dispersion(ibes_linked: pd.DataFrame) -> pd.DataFrame:
    """
    Analyst Dispersion = STDEV / |MEANEST| (coefficient of variation)
    
    Filters:
    - NUMEST >= 2 for meaningful dispersion
    - |MEANEST| >= 0.01 to avoid extreme CV
    - EPS measure, annual (FPI appropriate for annual forecasts)
    """
    # Filter to valid dispersion calculations
    valid = (
        (ibes_linked["NUMEST"] >= MIN_ANALYSTS) & 
        (ibes_linked["STDEV"].notna()) &
        (ibes_linked["MEANEST"].abs() >= MIN_MEANEST_ABS)
    )
    
    df = ibes_linked[valid].copy()
    df["analyst_dispersion"] = df["STDEV"] / df["MEANEST"].abs()
    
    # Aggregate to firm-year level (take median dispersion across periods)
    dispersion_by_firm_year = (
        df.groupby(["gvkey", "fiscal_year"])["analyst_dispersion"]
        .median()
        .reset_index()
    )
    
    return dispersion_by_firm_year
```

### Anti-Patterns to Avoid
- **Forgetting FF12 fallback:** Always implement thin-cell fallback for industry groupings
- **Integer division for depreciation:** Use `dp.replace(0, np.nan)` before Capex/DP to avoid divide-by-zero
- **Ignoring mutual exclusivity:** Firms cannot be both overinvesting AND underinvesting in same year
- **Wrong fiscal year for Delta-ROA:** Remember delta_roa_t2 = ROA(t+2) - ROA(t), need forward-looking data

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SIC-to-FF48 mapping | Manual SIC range parsing | `shared.industry_utils.parse_ff_industries()` | Already handles edge cases, tested |
| IBES-Compustat linking | Custom fuzzy matching | CUSIP8 join via CCM (existing pattern) | Industry standard, already working in 3.1_FirmControls.py |
| Rolling statistics | Manual loop over windows | `pandas.DataFrame.rolling()` | Vectorized, handles edge cases |
| OLS residuals | Manual matrix operations | `statsmodels.OLS().fit()` | Proper statistics, residuals available |

**Key insight:** The IBES linking and FF48 parsing are solved problems in this codebase. Focus implementation effort on the novel H2-specific logic (over/underinvestment classification, efficiency score rolling windows).

## Common Pitfalls

### Pitfall 1: Depreciation Edge Cases
**What goes wrong:** Division by zero when DP=0, or negative depreciation values
**Why it happens:** Some firms report zero or negative depreciation in Compustat
**How to avoid:** 
```python
# Replace zero/negative DP with NaN before computing Capex/DP
df["dpq_safe"] = df["dpq"].where(df["dpq"] > 0)
df["capex_dp"] = df["capxy"] / df["dpq_safe"]
```
**Warning signs:** Inf values in capex_dp ratio, extreme outliers

### Pitfall 2: Industry Classification Missing Values
**What goes wrong:** Firms with missing/invalid SIC codes excluded from industry-year calculations
**Why it happens:** Compustat SIC field can be missing or contain invalid codes
**How to avoid:** Assign unmapped SICs to FF48 #48 (Other) per CONTEXT.md
```python
df["ff48"] = df["sic"].map(ff48_map).fillna(48).astype(int)
```
**Warning signs:** Large number of firms excluded from industry medians

### Pitfall 3: Forward-Looking Bias in Delta-ROA
**What goes wrong:** Using future ROA values that weren't available at time t
**Why it happens:** Confusion about what Delta-ROA means temporally
**How to avoid:** Clearly label: `delta_roa_t2 = roa.shift(-2) - roa` (note: shift(-2) gives t+2 value)
```python
# Compute delta_roa: ROA(t+2) - ROA(t)
df = df.sort_values(["gvkey", "fiscal_year"])
df["roa_t2"] = df.groupby("gvkey")["roa"].shift(-2)  # Forward 2 years
df["delta_roa_t2"] = df["roa_t2"] - df["roa"]
```
**Warning signs:** Suspiciously high R-squared in Biddle regressions

### Pitfall 4: Insufficient Observations for Regression
**What goes wrong:** statsmodels OLS fails or produces unstable estimates with few observations
**Why it happens:** Some FF48-year cells have fewer than 20 firms
**How to avoid:** Enforce minimum 20 obs (per CONTEXT.md), fall back to FF12
```python
if len(group) < MIN_REGRESSION_OBS:
    # Try FF12 grouping instead
    # Or skip and mark as missing
```
**Warning signs:** `LinAlgError`, `PerfectCollinearity`, warnings from statsmodels

### Pitfall 5: Overlapping Efficiency Windows
**What goes wrong:** Efficiency scores computed with overlapping information, autocorrelation
**Why it happens:** 5-year rolling windows share 4 years of data between adjacent years
**How to avoid:** This is expected for panel analysis; document for econometric phase
**Warning signs:** High serial correlation in efficiency_score variable (acceptable, but note it)

### Pitfall 6: IBES Periodicity Confusion
**What goes wrong:** Mixing quarterly and annual IBES forecasts
**Why it happens:** IBES has both FISCALP='QTR' and FISCALP='ANN'
**How to avoid:** For analyst dispersion, typically use annual (ANN) or match to fiscal year end
```python
# Filter IBES to annual EPS forecasts
ibes_annual = ibes[(ibes["MEASURE"] == "EPS") & (ibes["FISCALP"] == "ANN")]
```
**Warning signs:** Multiple dispersion values per firm-year, inconsistent coverage

## Code Examples

Verified patterns from project sources:

### Loading Compustat with Schema Inspection
```python
# Source: 3.1_H1Variables.py (verified existing pattern)
import pyarrow.parquet as pq

def load_compustat_h2(compustat_file: Path) -> pd.DataFrame:
    """Load Compustat with only H2-required columns"""
    
    # H2-specific columns
    required_cols = [
        "gvkey", "datadate", "fyearq", "sic",
        # For Capex/Depreciation
        "capxy", "dpq",
        # For Sales Growth  
        "saleq", "saley",
        # For ROA and controls
        "atq", "iby", "cheq", "ceqq",
        "cshoq", "prccq",
        "dlttq", "dlcq",
        "oancfy",
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

### Efficiency Score Computation
```python
# Source: CONTEXT.md locked decisions + REQUIREMENTS.md H2-03
MIN_YEARS_IN_WINDOW = 3
WINDOW_SIZE = 5

def compute_efficiency_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Efficiency Score = 1 - (# inefficient years / # years in window)
    where inefficient = overinvest OR underinvest (mutually exclusive)
    
    Window: trailing 5 years (t-4 to t, inclusive)
    Minimum: 3 valid years required
    """
    df = df.sort_values(["gvkey", "fiscal_year"])
    
    # Mark inefficient years (mutually exclusive)
    df["inefficient"] = df["overinvest_dummy"] | df["underinvest_dummy"]
    
    results = []
    
    for gvkey, group in df.groupby("gvkey"):
        group = group.sort_values("fiscal_year")
        
        for idx, row in group.iterrows():
            fy = row["fiscal_year"]
            
            # Trailing window: t-4 to t (inclusive)
            window = group[
                (group["fiscal_year"] >= fy - 4) & 
                (group["fiscal_year"] <= fy)
            ]
            
            # Require minimum valid years
            valid_in_window = window["inefficient"].notna().sum()
            if valid_in_window < MIN_YEARS_IN_WINDOW:
                efficiency = np.nan
            else:
                inefficient_years = window["inefficient"].sum()
                efficiency = 1.0 - (inefficient_years / valid_in_window)
            
            results.append({
                "gvkey": gvkey,
                "fiscal_year": fy,
                "efficiency_score": efficiency,
                "years_in_window": valid_in_window,
                "inefficient_years": inefficient_years if valid_in_window >= MIN_YEARS_IN_WINDOW else np.nan,
            })
    
    return pd.DataFrame(results)
```

### Over/Underinvestment Classification
```python
# Source: REQUIREMENTS.md H2-01, H2-02 + CONTEXT.md
CAPEX_DP_OVERINVEST = 1.5   # > 1.5 for overinvestment
CAPEX_DP_UNDERINVEST = 0.75  # < 0.75 for underinvestment
TOBINS_Q_THRESHOLD = 1.5     # > 1.5 for underinvestment condition

def compute_investment_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Overinvest = 1 if (Capex/DP > 1.5) AND (Sales Growth < industry-year median)
    Underinvest = 1 if (Capex/DP < 0.75) AND (Tobin's Q > 1.5)
    
    Mutually exclusive: cannot be both in same year
    """
    df = df.copy()
    
    # Compute Capex/DP (handle DP=0)
    df["dpq_safe"] = df["dpq"].where(df["dpq"] > 0)
    df["capex_dp"] = df["capxy"] / df["dpq_safe"]
    
    # Compute sales growth
    df = df.sort_values(["gvkey", "fiscal_year"])
    df["sale_lag"] = df.groupby("gvkey")["saley"].shift(1)
    df["sales_growth"] = (df["saley"] - df["sale_lag"]) / df["sale_lag"].abs()
    
    # Industry-year median sales growth (with fallback)
    df = compute_industry_year_median(df, "sales_growth")
    
    # Classification
    df["high_capex"] = df["capex_dp"] > CAPEX_DP_OVERINVEST
    df["low_capex"] = df["capex_dp"] < CAPEX_DP_UNDERINVEST
    df["low_growth"] = df["sales_growth"] < df["sales_growth_ind_median"]
    df["high_q"] = df["tobins_q"] > TOBINS_Q_THRESHOLD
    
    # Investment dummies (mutually exclusive)
    df["overinvest_dummy"] = (df["high_capex"] & df["low_growth"]).astype(int)
    df["underinvest_dummy"] = (df["low_capex"] & df["high_q"]).astype(int)
    
    # Enforce mutual exclusivity (cannot be both)
    both_flags = df["overinvest_dummy"] & df["underinvest_dummy"]
    if both_flags.any():
        print(f"  Warning: {both_flags.sum()} obs flagged as both over AND under - setting to neither")
        df.loc[both_flags, "overinvest_dummy"] = 0
        df.loc[both_flags, "underinvest_dummy"] = 0
    
    return df
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single industry median | FF48 with FF12 fallback | Industry standard | Better coverage for small industries |
| Manual IBES matching | CUSIP8-based via CCM | Established | Standard academic practice |
| Simple OLS for residuals | statsmodels with diagnostics | Current best practice | Proper inference |

**Deprecated/outdated:**
- **Ticker-based IBES linking:** CUSIP is more reliable; ticker changes frequently
- **Manual SIC range parsing:** Use existing `parse_ff_industries()` utility

## Open Questions

Things that couldn't be fully resolved:

1. **Delta-ROA timing with data availability**
   - What we know: Need ROA(t+2), but sample may not have 2 years forward for recent years
   - What's unclear: Exact sample end dates and forward data availability
   - Recommendation: Compute where possible, document missing as data limitation (not an error)

2. **IBES annual vs quarterly for dispersion**
   - What we know: CONTEXT.md says use STDEV/|MEANEST|, but doesn't specify periodicity
   - What's unclear: Whether to use annual forecasts only or aggregate quarterly
   - Recommendation: Use annual EPS forecasts (FISCALP='ANN') for fiscal year match, document choice

3. **Winsorization timing for cross-sectional regression**
   - What we know: Project standard is 1%/99% winsorization
   - What's unclear: Winsorize before or after computing residuals?
   - Recommendation: Winsorize inputs (capex_at, tobins_q, etc.) BEFORE regression, winsorize residuals AFTER

## Sources

### Primary (HIGH confidence)
- **3.1_H1Variables.py** - Verified project pattern for variable construction
- **3.1_FirmControls.py** - IBES-CUSIP linking pattern, IBES loading pattern
- **shared/industry_utils.py** - FF industry parsing utility
- **CONTEXT.md** - Locked decisions on thresholds, methodologies
- **README.md (3_Financial_V2)** - Variable specifications and formulas

### Secondary (MEDIUM confidence)
- **Kenneth French Data Library** - FF48 definition format verification (webfetch verified)
- **IBES_Variable_reference.txt** - Column definitions for IBES data
- **Siccodes48.zip** - Actual format verified by reading file content

### Tertiary (LOW confidence)
- **Biddle et al. (2009) methodology** - Based on README.md description; original paper not directly accessed
- Recommend planner/executor verify regression specification against paper if available

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Uses existing project patterns and dependencies
- Architecture: HIGH - Direct pattern from H1, verified in codebase
- Pitfalls: MEDIUM - Based on code analysis and domain knowledge
- Biddle methodology: MEDIUM - Based on project README; paper not directly verified

**Research date:** 2026-02-04
**Valid until:** 2026-03-04 (30 days - stable domain, established patterns)
