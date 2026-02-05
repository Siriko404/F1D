# Phase 33: H1 Cash Holdings Regression - Research

**Researched:** 2026-02-05
**Domain:** Panel OLS Regression with Fixed Effects and Interaction Terms
**Confidence:** HIGH

## Summary

Phase 33 implements the core H1 hypothesis test: whether speech uncertainty predicts higher cash holdings, and whether leverage moderates this effect. The phase leverages existing infrastructure from Phase 32 (econometric modules) and Phase 29 (H1 variable construction), requiring only data merging, aggregation, and regression execution.

The primary technical challenges are:
1. **Call-to-firm-year aggregation:** Speech uncertainty measures exist at call level; H1 variables exist at firm-year level. Aggregation (fiscal-year mean) is required before merging.
2. **Interaction term construction:** Mean-centering both Uncertainty and Leverage before creating the interaction term reduces VIF and improves coefficient interpretability.
3. **Fixed effects configuration:** Firm + Year FE is the primary spec; industry FE should NOT be combined with firm FE (near-perfect collinearity).
4. **Clustered standard errors:** Firm-level clustering is standard; double-clustering (firm + year) is a robustness check.

**Primary recommendation:** Use `run_panel_ols()` from `shared/panel_ols.py` with `entity_effects=True`, `time_effects=True`, `cov_type='clustered'`, `cluster_entity=True`. Center variables with `center_continuous()` before creating interaction terms. VIF threshold of 5.0 applies only to non-interaction variables per 2024 econometric consensus.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| linearmodels | 7.0+ | PanelOLS with fixed effects | Gold standard for panel regression in Python |
| statsmodels | 0.14+ | VIF calculation, OLS utilities | Required dependency for diagnostics |
| pandas | 2.0+ | Data manipulation, groupby aggregation | Standard for tabular data |
| numpy | 1.24+ | Numerical operations | Required for array operations |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pyarrow | 12+ | Parquet I/O | Already used throughout project |
| scipy | 1.10+ | Statistical tests | For F-tests, p-value computation |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| linearmodels.PanelOLS | statsmodels.OLS with dummies | PanelOLS is 10-100x faster, handles large FE sets |
| Clustered SE | HAC/Newey-West | Clustered is standard for panel data with firm correlation |

**Installation:**
```bash
pip install linearmodels statsmodels pandas numpy pyarrow
```

## Architecture Patterns

### Recommended Project Structure
```
2_Scripts/
    4_H1_CashRegression/
        4.1_H1CashHoldingsRegression.py  # Main script
    shared/
        panel_ols.py       # run_panel_ols() - EXISTING
        centering.py       # center_continuous(), create_interaction() - EXISTING
        diagnostics.py     # compute_vif(), check_multicollinearity() - EXISTING
```

### Pattern 1: Call-to-Firm-Year Aggregation

**What:** Aggregate call-level speech uncertainty to firm-year level before merging with H1 variables.

**When to use:** Always when merging call-level text measures with annual financial data.

**Example:**
```python
# Source: Project convention, validated in 4.1_EstimateCeoClarity.py
def aggregate_speech_to_firmyear(speech_df: pd.DataFrame, uncertainty_cols: list) -> pd.DataFrame:
    """
    Aggregate call-level speech measures to fiscal-year level.
    
    Args:
        speech_df: Call-level data with file_name, gvkey, start_date, uncertainty columns
        uncertainty_cols: List of uncertainty measure columns to aggregate
    
    Returns:
        DataFrame at gvkey-fiscal_year level with mean uncertainty measures
    """
    # Extract fiscal year from call date
    speech_df = speech_df.copy()
    speech_df['fiscal_year'] = pd.to_datetime(speech_df['start_date']).dt.year
    
    # Aggregate: mean of all calls within fiscal year
    agg_dict = {col: 'mean' for col in uncertainty_cols}
    agg_dict['file_name'] = 'count'  # Track number of calls
    
    firm_year = speech_df.groupby(['gvkey', 'fiscal_year']).agg(agg_dict)
    firm_year = firm_year.rename(columns={'file_name': 'n_calls'})
    firm_year = firm_year.reset_index()
    
    return firm_year
```

### Pattern 2: Merge with Lead Dependent Variable

**What:** The regression is `CashHoldings_{t+1} ~ Uncertainty_t + Controls_t`, requiring a lead on the dependent variable.

**When to use:** For predictive regressions testing lagged effects.

**Example:**
```python
# Source: Standard econometric practice for predictive regressions
def prepare_regression_data(h1_df: pd.DataFrame, speech_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge H1 variables with speech uncertainty and create lead DV.
    """
    # Merge speech uncertainty (already at firm-year level)
    merged = h1_df.merge(
        speech_df[['gvkey', 'fiscal_year'] + uncertainty_cols],
        on=['gvkey', 'fiscal_year'],
        how='inner'
    )
    
    # Create lead cash_holdings (t+1)
    merged = merged.sort_values(['gvkey', 'fiscal_year'])
    merged['cash_holdings_lead'] = merged.groupby('gvkey')['cash_holdings'].shift(-1)
    
    # Drop last year per firm (no lead available)
    merged = merged.dropna(subset=['cash_holdings_lead'])
    
    return merged
```

### Pattern 3: Mean-Centered Interaction Construction

**What:** Center both interaction constituents, then multiply centered versions.

**When to use:** Always for continuous x continuous interactions (per CONTEXT.md decision).

**Example:**
```python
# Source: shared/centering.py (EXISTING)
from shared.centering import center_continuous, create_interaction

# Center both variables
df, means = center_continuous(df, ['uncertainty', 'leverage'], suffix='_c')

# Create interaction from centered versions
df['uncertainty_x_leverage'] = df['uncertainty_c'] * df['leverage_c']

# Exog list for regression
exog = ['uncertainty_c', 'leverage_c', 'uncertainty_x_leverage'] + control_vars
```

### Pattern 4: Panel OLS with Clustered SE

**What:** Use linearmodels.PanelOLS with entity/time effects and clustered covariance.

**When to use:** For all H1 regression specifications.

**Example:**
```python
# Source: linearmodels documentation + shared/panel_ols.py (EXISTING)
from shared.panel_ols import run_panel_ols

result = run_panel_ols(
    df=regression_df,
    dependent='cash_holdings_lead',
    exog=['uncertainty_c', 'leverage_c', 'uncertainty_x_leverage'] + controls,
    entity_col='gvkey',
    time_col='fiscal_year',
    entity_effects=True,     # Firm FE
    time_effects=True,       # Year FE
    industry_effects=False,  # DO NOT use with firm FE
    cov_type='clustered',
    cluster_cols=['gvkey'],  # Cluster at firm level
    vif_threshold=5.0
)

# Access results
coefficients = result['coefficients']
r_squared = result['summary']['rsquared']
vif_diagnostics = result['diagnostics']['vif']
```

### Anti-Patterns to Avoid

- **Firm + Industry FE together:** Firms rarely change industries; firm FE subsumes industry FE, causing near-perfect collinearity. Use one or the other.
- **VIF on interaction terms:** Per 2024 consensus, high VIF on interaction terms and their constituents is expected ("structural multicollinearity") and does NOT invalidate the interaction coefficient. Only apply VIF threshold to control variables.
- **Uncentered interaction interpretation:** Without centering, the main effect coefficient is "effect of X when Z=0" which may be outside data range. Centering makes it "effect at mean Z".
- **Ignoring clustering:** Serial correlation within firms inflates standard errors; always cluster at entity level.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Panel FE estimation | Manual demeaning + OLS | `linearmodels.PanelOLS` | Handles unbalanced panels, sparse matrices, degrees of freedom correctly |
| VIF calculation | Manual R-squared approach | `statsmodels.variance_inflation_factor` | Numerically stable, handles edge cases |
| Clustered SE | Manual sandwich formula | `cov_type='clustered'` in linearmodels | Handles multi-way clustering correctly |
| Fiscal year extraction | Manual date parsing | `pd.to_datetime().dt.year` | Handles edge cases, timezones |

**Key insight:** The existing infrastructure in `shared/panel_ols.py`, `shared/centering.py`, and `shared/diagnostics.py` covers 90% of the implementation. The planner should reuse these modules rather than reimplementing.

## Common Pitfalls

### Pitfall 1: Multicollinearity Panic on Interaction Terms
**What goes wrong:** VIF > 10 on uncertainty, leverage, and uncertainty*leverage triggers script failure.
**Why it happens:** Interaction terms are mathematically correlated with their constituents.
**How to avoid:** 
- Apply VIF check ONLY to non-interaction control variables
- OR compute VIF on the design matrix AFTER fixed effects demeaning (already done in linearmodels)
- Mean-centering reduces VIF on constituents but does NOT change interaction coefficient significance
**Warning signs:** VIF > 100 on interaction term with "threshold exceeded" errors

### Pitfall 2: Industry FE + Firm FE Collinearity
**What goes wrong:** PanelOLS raises `CollinearityError` or produces extreme/unstable coefficients.
**Why it happens:** Firm FE perfectly absorbs industry FE for firms that never switch industries.
**How to avoid:** 
- Primary spec: Firm + Year FE only (industry_effects=False)
- If industry variation is needed, use Pooled OLS or Year FE only
**Warning signs:** `check_rank=True` fails, warning about "thin cells"

### Pitfall 3: Missing Lead Values at Panel End
**What goes wrong:** Last observation per firm has NaN for cash_holdings_lead, regression silently drops observations.
**Why it happens:** Lead variable construction shifts the dependent variable.
**How to avoid:** 
- Explicitly count dropped observations in logs
- Verify remaining N matches expectations
- Document in stats.json: `"lead_dropped_obs": N`
**Warning signs:** Regression N is ~10-15% lower than merged N

### Pitfall 4: Multiple Calls Per Firm-Year After Merge
**What goes wrong:** Duplicate rows in regression data inflate standard errors and bias results.
**Why it happens:** Merging call-level data directly with firm-year data without aggregation.
**How to avoid:** 
- ALWAYS aggregate speech measures to firm-year BEFORE merging with H1 variables
- Verify 1:1 merge ratio after joining
**Warning signs:** len(merged) > len(h1_df), merge indicator shows "both" counts higher than expected

### Pitfall 5: VIF Computed on Raw Data Instead of Demeaned Data
**What goes wrong:** VIF is computed on the raw exog matrix, not after fixed effects transformation.
**Why it happens:** VIF function receives untransformed data.
**How to avoid:** 
- linearmodels internally demeans for FE; the VIF in `run_panel_ols()` is computed on raw exog as a pre-flight check
- For post-estimation VIF, extract residualized exog from model
- For Phase 33, the pre-flight VIF on raw data is acceptable (conservative)
**Warning signs:** Extremely high VIF on time-varying controls that should be orthogonal within-firm

## Code Examples

Verified patterns from official sources and existing project infrastructure:

### Complete H1 Regression Specification
```python
# Source: Adapted from shared/panel_ols.py + CONTEXT.md decisions
from shared.panel_ols import run_panel_ols
from shared.centering import center_continuous
from shared.diagnostics import check_multicollinearity, MulticollinearityError

# Define regression configuration
UNCERTAINTY_MEASURES = [
    'Manager_QA_Uncertainty_pct',
    'CEO_QA_Uncertainty_pct',
    'Manager_QA_Weak_Modal_pct',
    'CEO_QA_Weak_Modal_pct',
    'Manager_Pres_Uncertainty_pct',
    'CEO_Pres_Uncertainty_pct',
]

CONTROL_VARS = [
    'firm_size', 'tobins_q', 'roa', 'capex_at', 
    'dividend_payer', 'ocf_volatility', 'current_ratio'
]

SPECS = {
    'primary': {'entity_effects': True, 'time_effects': True, 'cluster_entity': True},
    'pooled': {'entity_effects': False, 'time_effects': False, 'cluster_entity': True},
    'year_only': {'entity_effects': False, 'time_effects': True, 'cluster_entity': True},
    'double_cluster': {'entity_effects': True, 'time_effects': True, 'cluster_entity': True, 'cluster_time': True},
}

def run_single_regression(df, uncertainty_var, spec_name, spec_config):
    """Run single H1 regression with given uncertainty measure and specification."""
    
    # Create working copy
    reg_df = df.copy()
    
    # Center uncertainty and leverage
    reg_df, means = center_continuous(reg_df, [uncertainty_var, 'leverage'])
    unc_c = f'{uncertainty_var}_c'
    lev_c = 'leverage_c'
    
    # Create interaction
    interaction_name = f'{uncertainty_var}_x_leverage'
    reg_df[interaction_name] = reg_df[unc_c] * reg_df[lev_c]
    
    # Build exog list
    exog = [unc_c, lev_c, interaction_name] + CONTROL_VARS
    
    # Pre-flight VIF check on controls only (not interaction terms)
    control_vif = check_multicollinearity(
        reg_df, 
        CONTROL_VARS,  # Exclude uncertainty, leverage, interaction
        vif_threshold=5.0,
        fail_on_violation=True  # STRICT mode per CONTEXT.md
    )
    
    # Run regression
    result = run_panel_ols(
        df=reg_df,
        dependent='cash_holdings_lead',
        exog=exog,
        entity_col='gvkey',
        time_col='fiscal_year',
        entity_effects=spec_config.get('entity_effects', True),
        time_effects=spec_config.get('time_effects', True),
        cov_type='clustered',
        cluster_cols=['gvkey'] if not spec_config.get('cluster_time') else ['gvkey', 'fiscal_year'],
        vif_threshold=5.0,
        check_collinearity=True
    )
    
    return {
        'spec': spec_name,
        'uncertainty_var': uncertainty_var,
        'result': result,
        'means': means,
        'control_vif': control_vif
    }
```

### Double-Clustering Configuration
```python
# Source: linearmodels documentation
# Double-cluster: cluster by entity AND time

# Option 1: Use built-in flags
result = mod.fit(
    cov_type='clustered',
    cluster_entity=True,
    cluster_time=True
)

# Option 2: Pass DataFrame with two cluster columns
clusters = df[['gvkey', 'fiscal_year']].reset_index(drop=True)
result = mod.fit(
    cov_type='clustered',
    clusters=clusters
)
```

### VIF Diagnostic with Threshold Enforcement
```python
# Source: shared/diagnostics.py (EXISTING)
from shared.diagnostics import check_multicollinearity, MulticollinearityError

# STRICT mode: fail if ANY control variable exceeds VIF threshold
try:
    result = check_multicollinearity(
        df=reg_df,
        columns=CONTROL_VARS,  # Only controls, NOT interaction terms
        vif_threshold=5.0,
        condition_threshold=30.0,
        fail_on_violation=True
    )
except MulticollinearityError as e:
    print(f"FATAL: Multicollinearity detected - {e}")
    sys.exit(1)
```

### Output Format for stats.json
```python
# Source: Project convention from 3.1_H1Variables.py and 4.1_EstimateCeoClarity.py
stats = {
    "step_id": "4.1_H1CashHoldingsRegression",
    "timestamp": timestamp,
    "input": {
        "files": ["H1_CashHoldings.parquet", "linguistic_variables_*.parquet"],
        "checksums": {...},
        "total_rows": merged_count,
        "speech_agg_method": "fiscal_year_mean",
        "lead_dropped_obs": lead_dropped
    },
    "processing": {
        "regressions_run": 24,  # 6 measures x 4 specs
        "centering_means": {
            "Manager_QA_Uncertainty_pct": 0.91,
            "leverage": 0.32
        },
        "vif_checks_passed": True
    },
    "output": {
        "files": ["H1_Regression_Results.parquet", "stats.json", "H1_RESULTS.md"],
        "checksums": {...}
    },
    "regressions": {
        "primary_Manager_QA_Uncertainty_pct": {
            "N": 15234,
            "rsquared": 0.42,
            "rsquared_within": 0.08,
            "f_statistic": 45.2,
            "f_pvalue": 0.0001,
            "coefficients": {
                "Manager_QA_Uncertainty_pct_c": {"beta": 0.023, "se": 0.008, "t": 2.87, "p": 0.004},
                "leverage_c": {"beta": -0.15, "se": 0.02, "t": -7.5, "p": 0.0001},
                "Manager_QA_Uncertainty_pct_x_leverage": {"beta": -0.05, "se": 0.02, "t": -2.5, "p": 0.012}
            },
            "hypothesis_tests": {
                "beta1_positive": {"test": "beta1 > 0", "result": True, "p_one_tail": 0.002},
                "beta3_negative": {"test": "beta3 < 0", "result": True, "p_one_tail": 0.006}
            }
        }
    },
    "timing": {...},
    "memory": {...}
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Remove correlated variables | Keep interaction terms, ignore structural VIF | 2020+ | Centering for interpretation, not "fixing" |
| VIF threshold 10 | VIF threshold 5 for controls only | 2024 consensus | More conservative for non-structural collinearity |
| Single clustering | Double-clustering as robustness | 2020+ | Addresses both serial and cross-sectional correlation |
| LSDV (dummy approach) | Within-transformation (linearmodels) | Always | 10-100x faster for large N |

**Deprecated/outdated:**
- **pandas.Panel:** Removed in pandas 1.0; use MultiIndex DataFrame instead
- **statsmodels.PanelOLS:** Never existed in mainline statsmodels; use linearmodels
- **Computing VIF manually:** Use `statsmodels.variance_inflation_factor` for stability

## Open Questions

Things that couldn't be fully resolved:

1. **Industry FE implementation:**
   - What we know: Firm FE subsumes industry FE; linearmodels supports `other_effects` for 3-way FE
   - What's unclear: Whether Phase 33 should attempt industry FE at all given firm FE is primary
   - Recommendation: Per CONTEXT.md, primary spec is Firm + Year only; skip industry FE entirely

2. **Fiscal year mapping edge cases:**
   - What we know: H1_CashHoldings uses `fiscal_year` from Compustat's `fyearq`; speech uses calendar year from `start_date`
   - What's unclear: Whether fiscal year = calendar year for all firms
   - Recommendation: Use calendar year from call date; document mismatch rate in stats.json

3. **Number of calls per firm-year:**
   - What we know: Multiple earnings calls per year (typically 4 quarterly + potential special calls)
   - What's unclear: Whether to aggregate all calls or filter to Q4 only
   - Recommendation: Per CONTEXT.md, average all calls in fiscal year; track `n_calls` for transparency

## Sources

### Primary (HIGH confidence)
- linearmodels 7.0 official documentation - Panel OLS examples, clustered SE, fixed effects
- shared/panel_ols.py (531 lines) - Existing project infrastructure, fully verified
- shared/centering.py (340 lines) - Existing project infrastructure, fully verified
- shared/diagnostics.py (413 lines) - Existing project infrastructure, fully verified
- 33-CONTEXT.md - User decisions on specification, centering, diagnostics

### Secondary (MEDIUM confidence)
- Google Search: "panel regression VIF interaction terms 2024" - Consensus on structural vs essential multicollinearity
- 3.1_H1Variables.py (1036 lines) - H1 variable construction patterns
- 4.2_LiquidityRegressions.py - Existing regression script patterns in project

### Tertiary (LOW confidence)
- General econometric best practices for cash holdings regressions (not project-specific)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - linearmodels is well-documented, existing infrastructure verified
- Architecture: HIGH - Direct extension of existing patterns in project
- Pitfalls: HIGH - Based on existing project code and linearmodels documentation
- Integration: MEDIUM - Aggregation logic needs verification against actual data

**Research date:** 2026-02-05
**Valid until:** 2026-03-05 (30 days - stable domain, existing infrastructure)
