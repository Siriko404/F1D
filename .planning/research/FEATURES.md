# Feature Landscape: Hypothesis Testing Pipeline

**Domain:** Empirical Finance Hypothesis Testing (Panel Regressions)
**Researched:** 2026-02-04
**Mode:** Features dimension for milestone research
**Context:** Adding hypothesis testing capabilities to existing F1D data pipeline

## Executive Summary

This feature landscape maps what hypothesis testing scripts in empirical finance typically provide, categorized by necessity level. The three hypotheses involve panel regressions with interaction terms, fixed effects, and robustness checks against corporate finance outcomes (cash holdings, investment efficiency, dividend volatility).

**Existing infrastructure (already built):**
- OLS panel regressions with fixed effects (`statsmodels`)
- 2SLS instrumental variable regressions (`linearmodels`)
- CEO fixed effects extraction
- Clustered standard errors (HC1, firm-level)
- DualWriter logging, stats.json output
- CLI with `--dry-run` and `--help`

**Key additions needed:** Interaction terms, hypothesis-specific variable construction, structured robustness checks, publication-quality output formatting.

---

## Table Stakes

Features users (academic reviewers, PhD committees) expect. Missing = results are not credible.

| Feature | Why Expected | Complexity | Depends On | Notes |
|---------|--------------|------------|------------|-------|
| **Baseline OLS with Fixed Effects** | Standard empirical finance specification | Low | statsmodels | Already implemented in 4.1/4.2 |
| **Firm + Year + Industry Fixed Effects** | Controls for unobserved heterogeneity | Low | existing FE infrastructure | 4.1 uses CEO + Year FE; add Firm FE |
| **Interaction Terms (X * Z)** | Core hypothesis mechanism (leverage moderates uncertainty) | Medium | regression_helpers.py | H1 requires Speech_Uncertainty × Firm_Leverage |
| **Clustered Standard Errors** | Correct for within-cluster correlation | Low | statsmodels `cov_type` | Already implemented (HC1); need firm-level clustering |
| **Complete Case Filtering** | Valid inference requires no missing DV/IV | Low | build_regression_sample() | Already implemented |
| **Winsorization** | Outlier treatment standard in finance | Low | pandas/numpy | Apply at 1%/99% per variable |
| **Sample Size Reporting** | N per model, pre/post filtering | Low | stats.json pattern | Already implemented |
| **Coefficient Table Output** | β, SE, t-stat, p-value per variable | Low | statsmodels summary | Already implemented |
| **R-squared Reporting** | Within/Adjusted R² per model | Low | statsmodels | Already implemented |
| **Model Diagnostics (VIF, F-stat)** | Multicollinearity, joint significance | Medium | statsmodels | Partial in 4.2; expand |
| **Lag Structure (t+1 outcomes)** | Temporal precedence for causality | Low | pandas shift/merge | Merge lagged outcomes |

### Baseline Regression Specification

Per methodology in hypothesis file, each hypothesis requires:

```
Y_{i,t+1} = α + β₁ Speech_Uncertainty_{i,t} 
              + β₂ Firm_Leverage_{i,t} 
              + β₃ (Speech_Uncertainty_{i,t} × Firm_Leverage_{i,t}) 
              + Σ γ_k Controls_{k,i,t} 
              + Firm_FE_i + Year_FE_t + Industry_FE_j 
              + ε_{i,t}
```

**Required coefficients to report:**
- β₁ > 0: Main effect (vagueness → outcome)
- β₃ < 0: Interaction effect (debt discipline moderates)

---

## Differentiators

Features that distinguish publication-quality work. Not strictly required but valued by top journals.

| Feature | Value Proposition | Complexity | Depends On | Notes |
|---------|-------------------|------------|------------|-------|
| **Subsample Analysis** | Split by leverage, growth, crisis periods | Medium | sample filtering | H1: low/high leverage; H2: high/low Tobin's Q |
| **Alternative Specifications** | Different DV constructions, control sets | Medium | modular regression | Robustness for reviewer skepticism |
| **Instrumental Variable (2SLS)** | Endogeneity mitigation | High | linearmodels | Already implemented in 4.2; extend to H1-H3 |
| **Quantile Regression** | Heterogeneity at distribution tails | Medium | statsmodels.quantile | H1: 25th/50th/75th percentile cash |
| **Difference-in-Differences** | Causal identification around events | High | Event study setup | Around CEO turnovers, leverage shocks |
| **Propensity Score Matching** | Balance high/low vagueness samples | High | scikit-learn or custom | Pre-regression matching |
| **Marginal Effects Calculation** | Economic magnitude at mean/median | Medium | Manual or statsmodels | Effect size at average leverage |
| **LaTeX Table Output** | Publication-ready formatting | Medium | stargazer or manual | Multi-model comparison tables |
| **Falsification Tests** | Placebo outcomes show no effect | Medium | Same regression on unrelated DV | Test on inventory/assets, advertising |
| **Economic Significance** | Standardized coefficients, $ impact | Medium | Post-estimation calculation | 1-SD change in X → Y change |
| **Coefficient Stability** | Oster (2019) bounds for omitted variable bias | High | External package | Beyond typical publication requirements |

### Subsample Specifications (from hypothesis file)

| Hypothesis | Subsample Splits | Purpose |
|------------|------------------|---------|
| H1 (Cash) | Low/high leverage (median split) | Test discipline-of-debt mechanism |
| H1 (Cash) | Pre/post-2008 crisis | Economic uncertainty context |
| H1 (Cash) | High/low FCF (median split) | Agency problem severity |
| H2 (Investment) | High/low Tobin's Q (1.5 threshold) | Growth opportunity context |
| H2 (Investment) | Low-growth vs high-growth industries | Sector-specific effects |
| H3 (Payout) | Mature/young firms (20-year threshold) | Firm lifecycle effects |
| H3 (Payout) | High/low institutional ownership | Governance quality |

---

## Anti-Features

Features to explicitly NOT build. Common over-engineering mistakes.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Interactive Dashboard** | Academic replication = batch scripts, not web apps | Timestamped output files |
| **Automated Model Selection** | Cherry-picking risk; reviewers want explicit choices | Pre-specified models from methodology |
| **Machine Learning Prediction** | Causal inference ≠ prediction; confuses contribution | Stick to interpretable OLS/2SLS |
| **Real-time Database Updates** | Frozen sample for replication | Static data snapshots |
| **GUI for Specification Tweaks** | Researcher degrees of freedom problem | Config-driven, version-controlled |
| **Bayesian Estimation** | Non-standard for corporate finance journals | Frequentist with clustered SEs |
| **Bootstrap Everything** | Overkill when analytical SEs available | Reserve for specific tests (e.g., mediation) |
| **Fancy Visualization Suite** | Tables, not charts, for regression results | Simple coefficient plots if any |
| **Multi-Language Support** | English-only for academic papers | Single language |
| **Cloud Deployment** | Local reproducibility is sufficient | `python script.py` workflow |

---

## Feature Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    HYPOTHESIS TESTING PIPELINE              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                       │
│  │ Variable        │ ◄── Depends on Steps 1-3:             │
│  │ Construction    │     - Speech Uncertainty (2.2)        │
│  │ (H1, H2, H3)    │     - Financial controls (3.x)        │
│  └────────┬────────┘     - CEO clarity scores (4.1)        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │ Sample          │ ◄── Winsorization, complete cases,    │
│  │ Preparation     │     industry/year filters             │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐    ┌─────────────────┐               │
│  │ Baseline        │───▶│ Interaction     │               │
│  │ Regression      │    │ Terms           │               │
│  └────────┬────────┘    └────────┬────────┘               │
│           │                      │                         │
│           ▼                      ▼                         │
│  ┌─────────────────────────────────────────┐               │
│  │        ROBUSTNESS CHECKS                │               │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ │               │
│  │  │Subsamples│ │Alt Specs │ │  2SLS    │ │               │
│  │  └──────────┘ └──────────┘ └──────────┘ │               │
│  └────────────────────┬────────────────────┘               │
│                       │                                     │
│                       ▼                                     │
│  ┌─────────────────────────────────────────┐               │
│  │        OUTPUT GENERATION                 │               │
│  │  - stats.json (diagnostics)              │               │
│  │  - regression_results.txt (full)         │               │
│  │  - report.md (summary tables)            │               │
│  │  - LaTeX tables (publication)            │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Hypothesis-Specific Features

### H1: Cash Holdings ~ Speech Uncertainty × Leverage

**DV Construction:**
```python
# Cash Holdings = CHE / AT (already available as Cash_Holdings)
df['Cash_Holdings'] = df['che'] / df['at']
```

**Interaction Term:**
```python
# Moderator × IV
df['Uncertainty_x_Leverage'] = df['Speech_Uncertainty'] * df['Firm_Leverage']
```

**Controls Required:**
| Variable | Compustat Code | Already Available? |
|----------|----------------|-------------------|
| Operating CF Volatility | 5-yr std(OANCF/AT) | Need to compute |
| Firm Size | ln(AT) | Likely in 3.x |
| Current Ratio | ACT/LCT | Likely in 3.x |
| Tobin's Q | (MVE + Debt) / AT | Likely in 3.x |
| ROA | NI/AT | Yes (3.x) |
| CapEx | CAPX/AT | Need to verify |
| Dividend Payer | DVC > 0 dummy | Need to compute |

### H2: Investment Efficiency ~ Speech Uncertainty

**DV Construction (complex):**
```python
# Option 1: Efficiency score based on over/underinvestment classification
# Overinvest = (CAPX/DP > 1.5) AND (Sales_Growth < industry median)
# Underinvest = (CAPX/DP < 0.75) AND (Tobin's Q > 1.5)

# Option 2: Residual-based (Biddle et al. 2009)
# Regress ∆ROA(t+2) on CAPX(t)/AT, take absolute residual
```

**Additional Controls:**
| Variable | Purpose |
|----------|---------|
| Analyst Forecast Dispersion | Information asymmetry proxy |
| Industry CapEx Intensity | Sector norms |
| Free Cash Flow | Agency problem proxy |

### H3: Payout Stability ~ Speech Uncertainty

**DV Construction:**
```python
# DV1: Stability = negative of (std(∆DPS) / mean(DPS)) over 5 years
# DV2: Flexibility = % of years with dividend change > 5%
df['DPS'] = df['dvc'] / df['csho']
df['Delta_DPS'] = df.groupby('gvkey')['DPS'].diff()
```

**Additional Controls:**
| Variable | Purpose |
|----------|---------|
| Earnings Volatility | Fundamental uncertainty |
| FCF Growth | Capacity to pay |
| Firm Maturity | Age or dividend history |

---

## Output Specifications

### Required Output Files (Table Stakes)

| File | Content | Format |
|------|---------|--------|
| `hypothesis_X_baseline.txt` | Full regression output | statsmodels summary |
| `hypothesis_X_diagnostics.csv` | N, R², F-stat, VIF per model | CSV |
| `stats.json` | Observability metrics | JSON |
| `report.md` | Summary tables | Markdown |

### Publication-Quality Output (Differentiator)

| File | Content | Format |
|------|---------|--------|
| `table_X.tex` | Multi-column coefficient table | LaTeX |
| `coefficient_plot.png` | Visual comparison across models | PNG |
| `robustness_summary.csv` | All specifications side-by-side | CSV |

---

## MVP Recommendation

For initial implementation, prioritize:

### Phase 1: Core Hypothesis Testing
1. **Variable construction** for H1, H2, H3 DVs and controls
2. **Interaction term support** in regression formula
3. **Baseline regressions** with firm + year + industry FE
4. **Standard output** (stats.json, regression_results.txt, report.md)

### Phase 2: Robustness Infrastructure
5. **Subsample analysis** framework (config-driven splits)
6. **Alternative specifications** (different control sets)
7. **2SLS extension** (already have infrastructure from 4.2)

### Phase 3: Publication Polish
8. **LaTeX table generation**
9. **Economic significance calculation**
10. **Falsification tests**

**Defer to post-thesis:**
- Propensity score matching
- Difference-in-differences
- Coefficient stability bounds (Oster)

---

## Complexity Assessment

| Feature Category | Complexity | Estimated Effort | Priority |
|------------------|------------|------------------|----------|
| Variable Construction | Medium | 4-8 hours | P0 |
| Interaction Terms | Low | 1-2 hours | P0 |
| Baseline Regressions | Low | 2-4 hours | P0 |
| Fixed Effects (Firm/Year/Industry) | Low | 2-3 hours | P0 |
| Clustered SEs | Low | 1 hour | P0 |
| Subsample Framework | Medium | 4-6 hours | P1 |
| 2SLS Extension | Low | 2-3 hours | P1 |
| LaTeX Output | Medium | 4-6 hours | P2 |
| Quantile Regression | Medium | 3-4 hours | P2 |
| Economic Significance | Medium | 2-3 hours | P2 |

---

## Sources

- **Hypothesis Methodology:** F1DV2 Hypothesis List.txt (project file)
- **Existing Infrastructure:**
  - `2_Scripts/shared/regression_helpers.py`
  - `2_Scripts/shared/regression_utils.py`
  - `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py`
  - `2_Scripts/4_Econometric/4.2_LiquidityRegressions.py`
- **Econometric Patterns:** 
  - Loughran & McDonald (2011) - uncertainty measurement
  - Dzielinski, Wagner, Zeckhauser (2017) - vague talker decomposition
  - Jensen (1986) - discipline of debt
  - Biddle et al. (2009) - investment efficiency residuals
- **Confidence:** HIGH for existing infrastructure assessment; MEDIUM for academic expectations (based on methodology file and standard practices)

---

*Research conducted: 2026-02-04*
*Mode: Features dimension for hypothesis testing milestone*
