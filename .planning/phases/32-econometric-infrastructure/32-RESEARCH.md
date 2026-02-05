# Phase 32: Econometric Infrastructure - Research

**Researched:** 2026-02-05
**Domain:** Panel econometrics with fixed effects, 2SLS, clustered standard errors
**Confidence:** HIGH

## Summary

This phase builds reusable econometric utilities for panel regressions with fixed effects, interaction terms, and robustness diagnostics. The research confirms that the existing `linearmodels 7.0` and `statsmodels 0.14.5` stack is fully sufficient for all requirements (ECON-01 through ECON-07).

Key findings:
- **PanelOLS** from linearmodels provides firm + year + industry fixed effects via `entity_effects`, `time_effects`, and `other_effects` parameters
- **IV2SLS** from linearmodels provides 2SLS with built-in first-stage F-stat (`first_stage.diagnostics`) and Sargan overidentification test (`sargan`)
- **Clustered standard errors** work via `cov_type="clustered"` with `cluster_entity=True` or custom clusters array for double-clustering
- **Newey-West / HAC adjustment** uses `cov_type="kernel"` with `kernel="bartlett"` (Driscoll-Kraay in panel context)
- **VIF calculation** uses `statsmodels.stats.outliers_influence.variance_inflation_factor()` on the design matrix
- **LaTeX tables**: `stargazer` library (v0.0.7, not installed) provides booktabs-style tables; alternatively, custom generation with f-strings

**Primary recommendation:** Use linearmodels for all panel FE and IV estimation; statsmodels for VIF; build lightweight LaTeX table generator or install stargazer.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| linearmodels | 7.0 | Panel OLS with FE, IV2SLS | Purpose-built for panel econometrics, actively maintained |
| statsmodels | 0.14.5 | VIF calculation, diagnostics | Standard Python econometrics, `variance_inflation_factor()` |
| pandas | 2.x | Data manipulation | Standard for tabular data, MultiIndex for panel |
| numpy | 1.x | Numerical operations | Standard for array operations |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| stargazer | 0.0.7 | LaTeX regression tables | Publication-ready tables with booktabs |
| scipy | 1.x | Statistical tests | Chi-squared, F-distribution p-values |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| linearmodels | statsmodels OLS with dummies | linearmodels handles high-dim FE efficiently via within-transform |
| stargazer | custom LaTeX generator | stargazer is heavier dependency but more polished |
| stargazer | linearmodels.compare() | Built-in comparison tables, but less customizable |

**Installation (if stargazer needed):**
```bash
pip install stargazer
```

## Architecture Patterns

### Recommended Project Structure
```
2_Scripts/
├── shared/
│   ├── econometric_utils.py      # Core panel OLS, 2SLS wrappers
│   ├── diagnostics.py            # VIF, first-stage F, Hansen J
│   ├── centering.py              # Mean-centering for interactions
│   └── latex_tables.py           # LaTeX table generation
├── 4_Econometric/
│   ├── 4.X_H1_Regressions.py     # Uses shared utilities
│   ├── 4.Y_H2_Regressions.py
│   └── 4.Z_H3_Regressions.py
```

### Pattern 1: Panel OLS with Multiple Fixed Effects
**What:** Run panel OLS with firm + year + industry FE
**When to use:** Hypothesis testing with panel data
**Example:**
```python
# Source: https://bashtage.github.io/linearmodels/panel/panel/linearmodels.panel.model.PanelOLS.html
from linearmodels.panel.model import PanelOLS

# Set MultiIndex for panel data
df = df.set_index(['gvkey', 'year'])

# Industry FE via other_effects (since firms don't change industries)
model = PanelOLS(
    dependent=df['cash_ratio'],
    exog=df[['vagueness', 'size', 'leverage', 'roa']],
    entity_effects=True,      # Firm FE
    time_effects=True,        # Year FE
    other_effects=df['ff48_code'],  # Industry FE (Fama-French 48)
    drop_absorbed=False,      # CRITICAL: Don't silently drop collinear
    check_rank=True           # Detect rank deficiency
)

# Fit with clustered standard errors at firm level
result = model.fit(
    cov_type='clustered',
    cluster_entity=True,      # Cluster at firm level
    debiased=True            # Degree-of-freedom adjustment
)
```

### Pattern 2: Double-Clustered Standard Errors
**What:** Cluster at both firm and year level
**When to use:** Panel with both cross-sectional and time-series correlation
**Example:**
```python
# Source: linearmodels documentation
from linearmodels.panel.model import PanelOLS

df = df.set_index(['gvkey', 'year'])

# For double clustering, pass DataFrame with cluster IDs
clusters = df[['gvkey', 'year']].reset_index(drop=True)

model = PanelOLS(
    dependent=df['cash_ratio'],
    exog=df[exog_cols],
    entity_effects=True,
    time_effects=True
)

# Double-cluster: firm + year
result = model.fit(
    cov_type='clustered',
    clusters=clusters  # DataFrame with 2 columns for 2-way clustering
)
```

### Pattern 3: Mean-Centering for Interactions
**What:** Center continuous variables before creating interaction terms
**When to use:** ANY interaction between continuous variables to reduce multicollinearity
**Example:**
```python
# Source: Econometric best practice (Aiken & West 1991)
def mean_center(series: pd.Series) -> pd.Series:
    """Center variable around its mean for interaction terms."""
    return series - series.mean()

def create_interaction(df: pd.DataFrame, var1: str, var2: str) -> pd.DataFrame:
    """Create interaction with mean-centered variables."""
    df = df.copy()
    
    # Center continuous variables
    df[f'{var1}_c'] = mean_center(df[var1])
    df[f'{var2}_c'] = mean_center(df[var2])
    
    # Create interaction from centered variables
    df[f'{var1}_x_{var2}'] = df[f'{var1}_c'] * df[f'{var2}_c']
    
    return df
```

### Pattern 4: 2SLS with Instrument Diagnostics
**What:** Run 2SLS and extract first-stage F and overidentification tests
**When to use:** Endogeneity concerns, using instruments
**Example:**
```python
# Source: https://bashtage.github.io/linearmodels/iv/iv/linearmodels.iv.model.IV2SLS.html
from linearmodels.iv.model import IV2SLS

# 2SLS setup
# dependent: outcome variable (Y)
# exog: exogenous controls (X, always in model)
# endog: endogenous regressor (suspected endogenous variable)
# instruments: excluded instruments (Z, used to predict endog)

model = IV2SLS(
    dependent=df['investment'],
    exog=df[['size', 'leverage', 'roa', 'const']],  # Controls + constant
    endog=df['vagueness'],                          # Endogenous variable
    instruments=df[['prior_firm_vagueness', 'peer_vagueness']]  # Instruments
)

result = model.fit(cov_type='robust')

# First-stage diagnostics
first_stage = result.first_stage
diagnostics = first_stage.diagnostics
# Returns DataFrame with: rsquared, partial.rsquared, f.stat, f.pval, shea.rsquared

# Extract first-stage F-stat
f_stat = diagnostics.loc['vagueness', 'f.stat']
if f_stat < 10:
    raise ValueError(f"Weak instruments: First-stage F = {f_stat:.2f} < 10")

# Sargan overidentification test (only if # instruments > # endogenous)
sargan_test = result.sargan
print(f"Hansen J / Sargan: stat={sargan_test.stat:.3f}, p={sargan_test.pval:.3f}")
# Null: instruments are valid (uncorrelated with error)
# Reject if p < 0.05 -> instruments may be invalid
```

### Pattern 5: VIF Calculation for Multicollinearity
**What:** Compute VIF for each regressor, flag VIF > 5
**When to use:** Before running any regression to check specification
**Example:**
```python
# Source: https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
from statsmodels.stats.outliers_influence import variance_inflation_factor
import numpy as np

def compute_vif(df: pd.DataFrame, exog_cols: list) -> pd.DataFrame:
    """
    Compute VIF for each explanatory variable.
    
    NOTE: Exclude dummy variables (fixed effects) from VIF calculation.
    VIF is meaningful only for continuous regressors.
    """
    X = df[exog_cols].dropna()
    
    # Add constant if not present
    if 'const' not in X.columns:
        X = X.copy()
        X['const'] = 1.0
    
    vif_data = []
    for i, col in enumerate(X.columns):
        if col == 'const':
            continue  # Skip constant
        vif = variance_inflation_factor(X.values, i)
        vif_data.append({'variable': col, 'VIF': vif})
    
    vif_df = pd.DataFrame(vif_data)
    vif_df['flag'] = vif_df['VIF'] > 5  # Threshold
    
    return vif_df
```

### Pattern 6: Newey-West / HAC in Panel Context
**What:** Apply kernel-based HAC standard errors (Driscoll-Kraay)
**When to use:** When autocorrelation and heteroskedasticity are concerns
**Example:**
```python
# Source: https://bashtage.github.io/linearmodels/panel/panel/linearmodels.panel.model.PanelOLS.fit.html
from linearmodels.panel.model import PanelOLS

model = PanelOLS(
    dependent=df['Y'],
    exog=df[exog_cols],
    entity_effects=True,
    time_effects=True
)

# Driscoll-Kraay HAC estimator (panel Newey-West)
result = model.fit(
    cov_type='kernel',       # HAC covariance
    kernel='bartlett',       # Newey-West kernel (default)
    bandwidth=3              # Lag length (rule of thumb: T^(1/4))
)
# Produces Driscoll-Kraay standard errors
```

### Anti-Patterns to Avoid
- **Including firm + industry FE simultaneously without care:** Firms rarely change industries; can cause rank deficiency. Use `check_rank=True` and verify.
- **VIF on design matrix with dummies:** VIF explodes with many dummies; compute only on continuous regressors.
- **Interaction terms without centering:** Creates artificial multicollinearity between main effects and interaction.
- **Ignoring first-stage F < 10:** 2SLS is MORE biased than OLS with weak instruments; enforce F > 10 programmatically.
- **Using `drop_absorbed=True` silently:** Can hide specification problems; use `drop_absorbed=False` and fix manually.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Panel fixed effects | Manual dummies/within-transform | `linearmodels.PanelOLS` | Handles high-dim FE efficiently, proper SE adjustment |
| Clustered SE | Manual sandwich estimator | `cov_type='clustered'` | Correct small-sample adjustment, 1-way and 2-way |
| First-stage F-stat | Manual first-stage regression | `result.first_stage.diagnostics` | Accounts for all adjustments automatically |
| Sargan test | Manual residual regression | `result.sargan` | Correct chi-squared distribution, handles edge cases |
| HAC standard errors | Manual Newey-West loop | `cov_type='kernel', kernel='bartlett'` | Correct bandwidth selection, all kernels available |
| VIF calculation | Manual R-squared loop | `variance_inflation_factor()` | Numerically stable, handles constants |

**Key insight:** linearmodels and statsmodels handle all the econometric edge cases (degree-of-freedom adjustments, rank checks, singular matrices) that are easy to get wrong in custom implementations.

## Common Pitfalls

### Pitfall 1: FE Collinearity with Firm + Industry
**What goes wrong:** Firms don't change industries (usually), so firm FE spans industry FE. Model becomes rank-deficient.
**Why it happens:** Researcher wants to control for industry effects beyond what firm FE captures.
**How to avoid:** 
1. Use `check_rank=True` to detect
2. If need industry-time interactions, use `other_effects` for industry-year
3. Or: use only firm + year FE (firm FE absorbs industry mean)
**Warning signs:** Warning about "absorbed variables" or singular matrix errors

### Pitfall 2: Weak Instruments in 2SLS
**What goes wrong:** First-stage F < 10 means 2SLS coefficient is MORE biased than OLS, not less.
**Why it happens:** Instruments are weakly correlated with endogenous variable.
**How to avoid:**
1. ALWAYS check `first_stage.diagnostics['f.stat']`
2. Enforce F > 10 programmatically with hard fail
3. Consider LIML estimator (`linearmodels.IVLIML`) which is more robust to weak instruments
**Warning signs:** First-stage partial R-squared < 0.1, large 2SLS standard errors

### Pitfall 3: VIF Explosion with Dummies
**What goes wrong:** VIF values in millions when computed on full design matrix with FE dummies.
**Why it happens:** Dummy variables are by construction collinear (sum to 1) with constant.
**How to avoid:**
1. Compute VIF only on CONTINUOUS regressors (not dummies)
2. Drop constant before computing VIF on dummies if needed
3. Focus on key variables of interest only
**Warning signs:** VIF > 1000 for any variable

### Pitfall 4: Interaction Multicollinearity
**What goes wrong:** High VIF for main effects and interaction term.
**Why it happens:** If X and Z are not centered, X*Z is highly correlated with X and Z.
**How to avoid:**
1. ALWAYS mean-center continuous variables before multiplying
2. For binary interactions, centering not needed
3. Store centered variables for reproducibility
**Warning signs:** VIF > 5 for main effects when interaction added

### Pitfall 5: Silent Absorbed Variable Drops
**What goes wrong:** linearmodels silently drops collinear variables, results may not include expected coefficients.
**Why it happens:** `drop_absorbed=True` is sometimes default behavior in other packages.
**How to avoid:**
1. Use `drop_absorbed=False` (linearmodels 7.0 default is False)
2. Check `result.params.index` matches expected variables
3. Fail hard if expected coefficients missing
**Warning signs:** Fewer coefficients than expected in output

### Pitfall 6: Thin FE Cells
**What goes wrong:** Industry-year fixed effects with <5 firms per cell cause noisy estimates.
**Why it happens:** FF48 industries with small panel creates thin cells.
**How to avoid:**
1. Check cell counts before estimation: `df.groupby(['ff48', 'year']).size()`
2. Fall back to FF12 if median cell size < 5
3. Document which classification used
**Warning signs:** Warnings about singleton observations, wild coefficient swings

## Code Examples

Verified patterns from official sources:

### Complete Panel OLS with Diagnostics
```python
# Source: linearmodels official docs + statsmodels VIF
from linearmodels.panel.model import PanelOLS
from statsmodels.stats.outliers_influence import variance_inflation_factor
import pandas as pd
import numpy as np

def run_panel_ols_with_diagnostics(
    df: pd.DataFrame,
    dep_var: str,
    exog_vars: list,
    entity_col: str = 'gvkey',
    time_col: str = 'year',
    industry_col: str = None,
    cluster_type: str = 'entity',  # 'entity', 'time', 'double'
    cov_type: str = 'clustered',   # 'clustered', 'kernel', 'robust'
    vif_threshold: float = 5.0
) -> dict:
    """
    Run panel OLS with comprehensive diagnostics.
    
    Returns dict with:
    - result: PanelEffectsResults object
    - diagnostics: dict with R2, N, F, VIF
    - warnings: list of warning messages
    """
    warnings = []
    
    # Set panel index
    df_panel = df.set_index([entity_col, time_col])
    
    # Compute VIF on continuous regressors before estimation
    X_for_vif = df[exog_vars].dropna()
    X_for_vif['const'] = 1.0
    vif_data = []
    for i, col in enumerate(X_for_vif.columns):
        if col == 'const':
            continue
        vif = variance_inflation_factor(X_for_vif.values, i)
        vif_data.append({'variable': col, 'VIF': vif, 'flag': vif > vif_threshold})
    vif_df = pd.DataFrame(vif_data)
    
    # Check for high VIF
    high_vif = vif_df[vif_df['flag']]
    if len(high_vif) > 0:
        warning_msg = f"High VIF detected: {high_vif.to_dict('records')}"
        warnings.append(warning_msg)
        print(f"WARNING: {warning_msg}")
    
    # Build model
    model_kwargs = {
        'dependent': df_panel[dep_var],
        'exog': df_panel[exog_vars],
        'entity_effects': True,
        'time_effects': True,
        'drop_absorbed': False,
        'check_rank': True
    }
    
    if industry_col and industry_col in df_panel.columns:
        model_kwargs['other_effects'] = df_panel[industry_col]
    
    model = PanelOLS(**model_kwargs)
    
    # Fit with appropriate covariance
    fit_kwargs = {'debiased': True}
    
    if cov_type == 'clustered':
        fit_kwargs['cov_type'] = 'clustered'
        if cluster_type == 'entity':
            fit_kwargs['cluster_entity'] = True
        elif cluster_type == 'time':
            fit_kwargs['cluster_time'] = True
        elif cluster_type == 'double':
            # Double clustering requires explicit clusters DataFrame
            clusters = df[[entity_col, time_col]].copy()
            fit_kwargs['clusters'] = clusters
    elif cov_type == 'kernel':
        fit_kwargs['cov_type'] = 'kernel'
        fit_kwargs['kernel'] = 'bartlett'
    else:
        fit_kwargs['cov_type'] = 'robust'
    
    result = model.fit(**fit_kwargs)
    
    # Build diagnostics
    diagnostics = {
        'nobs': int(result.nobs),
        'rsquared': float(result.rsquared),
        'rsquared_within': float(result.rsquared_within) if hasattr(result, 'rsquared_within') else None,
        'f_statistic': float(result.f_statistic.stat) if result.f_statistic else None,
        'f_pvalue': float(result.f_statistic.pval) if result.f_statistic else None,
        'vif': vif_df.to_dict('records'),
        'entity_effects': result.entity_effects,
        'time_effects': result.time_effects,
        'other_effects': result.other_effects if hasattr(result, 'other_effects') else False
    }
    
    return {
        'result': result,
        'diagnostics': diagnostics,
        'warnings': warnings
    }
```

### Complete 2SLS with Instrument Validation
```python
# Source: linearmodels IV documentation
from linearmodels.iv.model import IV2SLS
import pandas as pd

def run_2sls_with_validation(
    df: pd.DataFrame,
    dep_var: str,
    endog_var: str,
    exog_vars: list,
    instruments: list,
    f_threshold: float = 10.0,
    sargan_alpha: float = 0.05
) -> dict:
    """
    Run 2SLS with first-stage F and overidentification tests.
    
    Raises:
        ValueError: If first-stage F < threshold (weak instruments)
    
    Returns dict with:
    - result: IVResults object
    - first_stage_diagnostics: DataFrame
    - overid_test: dict with stat and pval
    - warnings: list
    """
    warnings = []
    
    # Add constant to exog if not present
    df_reg = df.copy()
    if 'const' not in df_reg.columns:
        df_reg['const'] = 1.0
    
    exog_with_const = exog_vars + ['const'] if 'const' not in exog_vars else exog_vars
    
    model = IV2SLS(
        dependent=df_reg[dep_var],
        exog=df_reg[exog_with_const],
        endog=df_reg[[endog_var]],
        instruments=df_reg[instruments]
    )
    
    result = model.fit(cov_type='robust')
    
    # First-stage diagnostics
    first_stage = result.first_stage
    diagnostics_df = first_stage.diagnostics
    
    # Extract F-stat for endogenous variable
    f_stat = diagnostics_df.loc[endog_var, 'f.stat']
    f_pval = diagnostics_df.loc[endog_var, 'f.pval']
    partial_rsq = diagnostics_df.loc[endog_var, 'partial.rsquared']
    
    # HARD FAIL on weak instruments
    if f_stat < f_threshold:
        raise ValueError(
            f"WEAK INSTRUMENTS: First-stage F = {f_stat:.2f} < {f_threshold}. "
            f"2SLS is more biased than OLS. Cannot proceed."
        )
    
    # Overidentification test (Sargan)
    # Only valid if # instruments > # endogenous variables
    n_instr = len(instruments)
    n_endog = 1  # Single endogenous variable
    
    overid_test = {'stat': None, 'pval': None, 'valid': False}
    
    if n_instr > n_endog:
        sargan = result.sargan
        overid_test = {
            'stat': float(sargan.stat),
            'pval': float(sargan.pval),
            'valid': True,
            'reject_null': sargan.pval < sargan_alpha
        }
        
        if sargan.pval < sargan_alpha:
            warnings.append(
                f"Sargan test rejects null (p={sargan.pval:.3f}): "
                f"Instruments may be invalid (correlated with error)"
            )
    else:
        overid_test['note'] = "Exactly identified: Sargan test not available"
    
    return {
        'result': result,
        'first_stage_diagnostics': {
            'f_stat': float(f_stat),
            'f_pval': float(f_pval),
            'partial_rsquared': float(partial_rsq),
            'full_diagnostics': diagnostics_df.to_dict()
        },
        'overid_test': overid_test,
        'warnings': warnings
    }
```

### LaTeX Table Generation (Minimal Custom)
```python
# Source: Custom implementation following booktabs style
def generate_latex_table(
    results: list,
    model_names: list,
    dep_var_name: str,
    coef_names: dict = None,  # Optional rename mapping
    stars: bool = True,
    precision: int = 3
) -> str:
    """
    Generate booktabs-style LaTeX regression table.
    
    Args:
        results: List of fitted model results
        model_names: Column headers for each model
        dep_var_name: Name for dependent variable row
        coef_names: Dict mapping variable names to display names
        stars: Include significance stars
        precision: Decimal places
    
    Returns:
        LaTeX string ready for .tex file
    """
    if coef_names is None:
        coef_names = {}
    
    # Collect all coefficient names across models
    all_vars = []
    for r in results:
        all_vars.extend(r.params.index.tolist())
    all_vars = list(dict.fromkeys(all_vars))  # Preserve order, remove dups
    
    # Build table
    n_models = len(results)
    col_spec = 'l' + 'c' * n_models
    
    lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        f'\\begin{{tabular}}{{{col_spec}}}',
        r'\toprule',
        '& ' + ' & '.join(f'({i+1})' for i in range(n_models)) + r' \\',
        '& ' + ' & '.join(model_names) + r' \\',
        r'\midrule',
        f'\\multicolumn{{{n_models+1}}}{{l}}{{\\textit{{Dep. var: {dep_var_name}}}}} \\\\',
        r'\midrule'
    ]
    
    # Coefficient rows
    for var in all_vars:
        display_name = coef_names.get(var, var)
        row = [display_name]
        se_row = ['']
        
        for r in results:
            if var in r.params.index:
                coef = r.params[var]
                se = r.std_errors[var]
                pval = r.pvalues[var]
                
                # Format coefficient with stars
                coef_str = f'{coef:.{precision}f}'
                if stars:
                    if pval < 0.01:
                        coef_str += '***'
                    elif pval < 0.05:
                        coef_str += '**'
                    elif pval < 0.10:
                        coef_str += '*'
                
                row.append(coef_str)
                se_row.append(f'({se:.{precision}f})')
            else:
                row.append('')
                se_row.append('')
        
        lines.append(' & '.join(row) + r' \\')
        lines.append(' & '.join(se_row) + r' \\')
    
    # Footer statistics
    lines.append(r'\midrule')
    
    # Observations
    obs_row = ['Observations']
    for r in results:
        obs_row.append(f'{int(r.nobs):,}')
    lines.append(' & '.join(obs_row) + r' \\')
    
    # R-squared
    rsq_row = ['R$^2$']
    for r in results:
        rsq_row.append(f'{r.rsquared:.{precision}f}')
    lines.append(' & '.join(rsq_row) + r' \\')
    
    lines.extend([
        r'\bottomrule',
        r'\end{tabular}',
        r'\caption{Regression Results}',
        r'\label{tab:regression}',
        r'\begin{tablenotes}[flushleft]',
        r'\small',
        r'\item Note: Standard errors in parentheses. * p<0.1, ** p<0.05, *** p<0.01.',
        r'\end{tablenotes}',
        r'\end{table}'
    ])
    
    return '\n'.join(lines)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual within-transform for FE | linearmodels PanelOLS | linearmodels 1.0 (2017) | Handles high-dim FE efficiently |
| statsmodels OLS with dummy explosion | linearmodels other_effects | linearmodels 4.0+ | Proper memory handling |
| Manual Newey-West | cov_type='kernel' | linearmodels 4.0+ | Built-in bandwidth selection |
| Separate first-stage regression | first_stage.diagnostics | linearmodels 4.0+ | Automatic, matches second stage |

**Deprecated/outdated:**
- `pandas.stats.ols.PanelOLS`: Removed from pandas, use linearmodels
- Manual sandwich estimator implementations: Use linearmodels covariance options
- R-style formula API for FE: linearmodels formulas support `EntityEffects`, `TimeEffects`

## Open Questions

Things that couldn't be fully resolved:

1. **Stargazer compatibility with linearmodels**
   - What we know: Stargazer works with statsmodels OLS results
   - What's unclear: Whether it handles linearmodels PanelEffectsResults directly
   - Recommendation: Test with a simple model; if fails, extract coefficients into compatible format or use custom LaTeX generator

2. **FF48 vs FF12 thin cell threshold**
   - What we know: Thin cells cause noisy estimates
   - What's unclear: Exact threshold (5 firms? 10?) for when to fall back
   - Recommendation: Start with 5, log cell sizes, adjust based on results

3. **Optimal HAC bandwidth**
   - What we know: Rule of thumb is T^(1/4) or N^(1/4)
   - What's unclear: Best choice for this specific panel structure
   - Recommendation: Use linearmodels default, document choice, sensitivity check

## Sources

### Primary (HIGH confidence)
- linearmodels 7.0 official documentation - PanelOLS, IV2SLS, covariance estimators
  - https://bashtage.github.io/linearmodels/panel/panel/linearmodels.panel.model.PanelOLS.html
  - https://bashtage.github.io/linearmodels/panel/panel/linearmodels.panel.model.PanelOLS.fit.html
  - https://bashtage.github.io/linearmodels/iv/iv/linearmodels.iv.model.IV2SLS.html
  - https://bashtage.github.io/linearmodels/iv/iv/linearmodels.iv.results.FirstStageResults.diagnostics.html
  - https://bashtage.github.io/linearmodels/iv/iv/linearmodels.iv.results.IVResults.sargan.html
- statsmodels 0.14.5 official documentation - variance_inflation_factor
  - https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
- stargazer 0.0.7 PyPI/GitHub - LaTeX table generation
  - https://github.com/StatsReporting/stargazer

### Secondary (MEDIUM confidence)
- linearmodels DriscollKraay documentation for panel HAC
  - https://bashtage.github.io/linearmodels/panel/panel/linearmodels.panel.covariance.DriscollKraay.html

### Tertiary (LOW confidence)
- General best practice for mean-centering (Aiken & West 1991) - from training data

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - verified with pip show, tested imports
- Architecture (PanelOLS, IV2SLS API): HIGH - official docs fetched and verified
- First-stage F, Sargan: HIGH - official docs confirm `first_stage.diagnostics` and `sargan` properties
- VIF calculation: HIGH - statsmodels official docs verified
- Newey-West/HAC: HIGH - DriscollKraay docs confirm panel HAC via kernel covariance
- LaTeX tables: MEDIUM - stargazer exists but not installed; custom approach verified conceptually
- Pitfalls: HIGH - based on official docs warnings and known econometric issues

**Research date:** 2026-02-05
**Valid until:** 2026-03-05 (30 days - stable libraries)
