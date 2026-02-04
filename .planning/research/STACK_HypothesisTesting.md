# Technology Stack: Hypothesis Testing Extension

**Project:** F1D Clarity - Hypothesis Testing Milestone
**Researched:** 2026-02-04
**Focus:** Stack additions for H1-H3 hypothesis testing with interaction terms, manager FE, 2SLS, and subsample analyses

---

## Executive Summary

**Verdict:** The existing stack is 95% sufficient. ONE package needs to be formalized.

The current F1D pipeline already has the infrastructure needed for the hypothesis tests:
- `statsmodels==0.14.6` provides interaction terms and OLS regression
- `linearmodels` (already imported in 4.2_LiquidityRegressions.py) provides proper 2SLS and panel fixed effects
- The only gap is that **linearmodels is used but not declared** in requirements.txt

**Action Required:** Add `linearmodels==7.0` to requirements.txt (it's already installed and used).

---

## Current Stack Audit (Verified Feb 2026)

| Package | Pinned Version | PyPI Latest | Release Date | Status |
|---------|----------------|-------------|--------------|--------|
| pandas | 2.2.3 | 2.2.3 | - | OK |
| numpy | 2.3.2 | 2.3.2 | - | OK |
| scipy | 1.16.1 | 1.16.1 | - | OK |
| statsmodels | 0.14.6 | 0.14.6 | Dec 5, 2025 | OK |
| lifelines | 0.30.0 | 0.30.0 | - | OK |
| pyarrow | 21.0.0 | 21.0.0 | - | OK |

**Sources:** PyPI official pages (verified Feb 4, 2026)

---

## Stack Addition Required

### linearmodels 7.0 (CRITICAL - Already Used, Not Declared)

| Attribute | Value |
|-----------|-------|
| Package | linearmodels |
| Version | 7.0 |
| PyPI Release | Oct 21, 2025 |
| Python Requirement | >= 3.10 |
| Purpose | Panel FE, 2SLS IV, clustered standard errors |

**Current State in Codebase:**
```python
# Already in 4.2_LiquidityRegressions.py, line 105-106:
from linearmodels.iv import IV2SLS
LINEARMODELS_AVAILABLE = True
```

**But NOT in requirements.txt.** This is a dependency gap that must be fixed.

**Key Capabilities for Hypothesis Testing:**
- `PanelOLS`: Two-way fixed effects (entity + time) with proper demeaning
- `IV2SLS`: Two-stage least squares for endogeneity correction
- `FamaMacBeth`: Cross-sectional regression with time-series averaging
- Clustered standard errors by entity or time
- Native panel data index support

**Installation:**
```bash
pip install linearmodels==7.0
```

**Add to requirements.txt:**
```
# Panel Data / IV Regression
# Used in 4.2_LiquidityRegressions.py and 4.x_HypothesisTests.py
linearmodels==7.0
```

---

## Hypothesis-to-Existing-Stack Mapping

### H1: Cash Holdings with Uncertainty x Leverage Interaction

| Requirement | Solution | Library | Code Location |
|-------------|----------|---------|---------------|
| Panel regression | `PanelOLS` | linearmodels | New step |
| Firm + Year FE | `entity_effects + time_effects` | linearmodels | New step |
| **Interaction terms** | Formula: `Unc * Lev` | statsmodels/linearmodels | Native support |
| Clustered SEs | `cluster_entity=True` | linearmodels | Pattern in 4.2 |
| Industry controls | `_assign_industry_codes()` | shared/regression_helpers.py | Line 107-195 |

**Implementation Pattern (No New Packages Needed):**
```python
from linearmodels.panel import PanelOLS

# Set MultiIndex for panel data
data = data.set_index(['gvkey', 'year'])

# Model with interaction term - NATIVE SUPPORT
model = PanelOLS.from_formula(
    'CashHoldings ~ Uncertainty * Leverage + Size + ROA + EntityEffects + TimeEffects',
    data
)
result = model.fit(cov_type='clustered', cluster_entity=True)

# Interaction coefficient is automatically computed
print(result.params['Uncertainty:Leverage'])
```

### H2: Investment Efficiency (Over/Underinvestment Detection)

| Requirement | Solution | Library | Code Location |
|-------------|----------|---------|---------------|
| 2SLS instrumentation | `IV2SLS` | linearmodels | 4.2_LiquidityRegressions.py:524-618 |
| First-stage F-stat | `first_stage.fvalue` | statsmodels | 4.2_LiquidityRegressions.py:584-592 |
| Manager FE decomposition | `C(ceo_id)` dummies | statsmodels | 4.1_EstimateCeoClarity.py:377 |
| Subsample splits | Boolean indexing | pandas | Native |

**Implementation Pattern (Reuses Existing 4.2 Code):**
```python
from linearmodels.iv import IV2SLS
import statsmodels.api as sm

# Instruments: prior_firm_vagueness, peer_average_vagueness
# Endogenous: Uncertainty

# Already implemented pattern in 4.2_LiquidityRegressions.py:568-581
model = IV2SLS(y, exog, endog, instruments).fit(cov_type='robust')

# First-stage F-stat (for weak instrument test)
first_stage = sm.OLS(endog, sm.add_constant(pd.concat([instruments, exog], axis=1))).fit()
kp_f = first_stage.fvalue  # Kleibergen-Paap F-stat proxy
```

### H3: Payout Policy Stability (Dividend Volatility)

| Requirement | Solution | Library | Already Available |
|-------------|----------|---------|-------------------|
| Volatility calculation | `rolling().std()` | pandas | Yes |
| Crisis period dummies | Boolean flags | pandas | Yes |
| Subsample analysis | `.query()` / boolean mask | pandas | Yes |
| Quantile splits | `pd.qcut()` / `np.quantile()` | pandas/numpy | Yes |

**No Additional Packages Needed:**
```python
# Dividend volatility over rolling window
df['DivVolatility'] = df.groupby('gvkey')['Dividend'].transform(
    lambda x: x.rolling(window=5, min_periods=3).std()
)

# Crisis period dummy
df['Crisis'] = df['year'].isin([2007, 2008, 2009]).astype(int)

# High/low leverage subsample
df['HighLev'] = df['Leverage'] > df['Leverage'].median()
```

---

## Existing Code Reuse Map

### From 4.1_EstimateCeoClarity.py

| Pattern | Lines | Reuse For |
|---------|-------|-----------|
| CEO FE extraction | 408-428 | Manager fixed effect decomposition |
| Industry sample assignment | 321-323 | H1 subsample by industry |
| Min calls filter | 354-358 | Sample quality control |
| Dual logging | 748-750 | All new hypothesis scripts |

### From 4.2_LiquidityRegressions.py

| Pattern | Lines | Reuse For |
|---------|-------|-----------|
| IV2SLS setup | 568-581 | H2 instrumentation |
| First-stage F-stat | 584-592 | Weak instrument test |
| Clustered SEs | 498 | All hypothesis tests |
| Sample filtering | 678-683 | Industry/period subsamples |

### From shared/regression_helpers.py

| Function | Lines | Reuse For |
|----------|-------|-----------|
| `build_regression_sample()` | 198-352 | All hypothesis sample construction |
| `_assign_industry_codes()` | 107-195 | Industry FE assignment |
| `_check_missing_values()` | 79-104 | Data quality validation |

### From shared/regression_utils.py

| Function | Lines | Reuse For |
|----------|-------|-----------|
| `run_fixed_effects_ols()` | 34-68 | OLS with FE (if not using linearmodels) |
| `extract_ceo_fixed_effects()` | 71-85 | Manager FE extraction |
| `extract_regression_diagnostics()` | 88-107 | Model diagnostics |

---

## What NOT to Add

| Package | Why NOT |
|---------|---------|
| pyfixest | linearmodels already provides all needed FE functionality; pyfixest is newer, less battle-tested |
| wooldridge | Educational package for textbook examples, not production-grade |
| plm (R) | Would require R integration, adds complexity |
| pyhdfe | linearmodels.AbsorbingLS covers high-dimensional FE if needed |
| arch | Not needed; volatility here is simple std(), not GARCH |
| fixest (R) | Would require rpy2 bridge, unnecessary |

**Rationale:** The existing statsmodels + linearmodels stack covers all econometric needs for these hypotheses. Adding packages creates maintenance burden without capability gain.

---

## Requirements.txt Update

**Add this block:**
```
# =============================================================================
# Econometric Extensions (Panel Data / IV)
# =============================================================================
# Required for 2SLS and panel fixed effects in Steps 4.x
# Already used in 4.2_LiquidityRegressions.py but was undeclared
linearmodels==7.0
```

---

## Version Compatibility Check

| Package | Min Python | Our Stack | Compatible? |
|---------|------------|-----------|-------------|
| linearmodels 7.0 | 3.10 | ? | CHECK |
| statsmodels 0.14.6 | 3.9 | ? | YES |
| pandas 2.2.3 | 3.9 | ? | YES |

**IMPORTANT:** linearmodels 7.0 requires Python >= 3.10.

**Mitigation Options:**
1. **Verify Python version** - If 3.10+, no issue
2. **Use linearmodels 6.1** (Sep 2024) - Works with Python 3.9
3. **It's already working** - 4.2_LiquidityRegressions.py imports it, so environment must be compatible

---

## Interaction Terms: No Special Handling Needed

Both statsmodels and linearmodels support R-style formula interaction terms natively:

```python
# statsmodels formula interface
import statsmodels.formula.api as smf
model = smf.ols('Y ~ A * B', data=df)  # Creates A, B, and A:B terms

# linearmodels formula interface  
from linearmodels.panel import PanelOLS
model = PanelOLS.from_formula('Y ~ A * B + EntityEffects', data=df.set_index(['entity', 'time']))
```

**No patsy/formulaic manipulation required** - the formula parser handles it.

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| statsmodels 0.14.6 capabilities | HIGH | Verified via PyPI, Dec 2025 release |
| linearmodels 7.0 capabilities | HIGH | Verified via official docs, Oct 2025 release |
| Interaction term support | HIGH | Native in both formula interfaces |
| 2SLS/IV support | HIGH | Already implemented and tested in 4.2 |
| Panel FE support | HIGH | linearmodels.PanelOLS is purpose-built for this |
| Code reuse feasibility | HIGH | Reviewed existing implementations in 4.1/4.2 |
| Python version compatibility | MEDIUM | Need to verify environment Python version |

---

## Action Items for Roadmap

1. **Immediate:** Add `linearmodels==7.0` to requirements.txt (fix undeclared dependency)
2. **Phase 1:** Create shared panel data utilities extending `regression_helpers.py`
3. **Phase 2:** Implement H1 script following 4.1/4.2 patterns
4. **Phase 3:** Implement H2 script reusing IV2SLS from 4.2
5. **Phase 4:** Implement H3 script (simplest, mostly pandas operations)

**No new package exploration needed** - the stack is complete.

---

## Sources

| Source | URL | Verified |
|--------|-----|----------|
| PyPI statsmodels 0.14.6 | https://pypi.org/project/statsmodels/ | Feb 4, 2026 |
| PyPI linearmodels 7.0 | https://pypi.org/project/linearmodels/ | Feb 4, 2026 |
| linearmodels docs | https://bashtage.github.io/linearmodels/ | Feb 4, 2026 |
| Existing code: 4.2_LiquidityRegressions.py | Local codebase | Feb 4, 2026 |
| Existing code: 4.1_EstimateCeoClarity.py | Local codebase | Feb 4, 2026 |
| Existing code: shared/regression_helpers.py | Local codebase | Feb 4, 2026 |
