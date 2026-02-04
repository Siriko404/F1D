# Econometric V2

## Purpose and Scope

This folder contains econometric analysis scripts for testing hypotheses H1, H2, and H3 on the relationship between managerial communication vagueness (uncertainty) and corporate financial policies.

**Primary Inputs:**
- Financial variables from `4_Outputs/3_Financial_V2/latest/` (H1/H2/H3 dependent and control variables)
- Speech uncertainty measures from `4_Outputs/2_Text_Processing/latest/` (main independent variables)

**Outputs:**
- Regression results: `4_Outputs/4_Econometric_V2/YYYY-MM-DD_HHMMSS/`
- Execution logs: `3_Logs/4_Econometric_V2/<timestamp>.log`

**Dependency Chain:**
```
Infrastructure (4.0) -> Regressions (4.1-4.3) -> Robustness (4.4-4.6) -> Identification (4.7) -> Publication (4.8)
```

---

## Econometric Infrastructure (Script 4.0_EconometricInfra.py)

The infrastructure script provides shared utilities for all regression analysis. Run this once before running hypothesis regression scripts.

### Core Econometric Methods

**Panel OLS with Fixed Effects:**
- Firm fixed effects: Controls for time-invariant firm heterogeneity
- Year fixed effects: Controls for macroeconomic time trends
- Industry fixed effects: Fama-French 48 industry classification

**Fixed Effect Collinearity Warning:**
Firm + industry FE are redundant because firms rarely change industries. This can cause multicollinearity. The infrastructure uses `drop_absorbed=False, check_rank=True` to handle this gracefully.

**Interaction Terms:**
- All continuous variables are mean-centered before creating interaction terms
- This avoids multicollinearity between main effects and interaction effects
- Example: `Uncertainty_Centered = Uncertainty - mean(Uncertainty)`

**Clustered Standard Errors:**
- Default: Firm-level clustering (accounts for within-firm correlation)
- Optional: Double clustering (firm + year) for additional robustness

**2SLS (Two-Stage Least Squares):**
Instruments for addressing endogeneity of managerial vagueness:

1. **Manager's Prior-Firm Vagueness:** Average vagueness of the manager during their tenure at previous firms. Requires manager mobility data (CEOs who moved between firms).

2. **Industry-Peer Average Vagueness:** Average vagueness of all other managers in the same industry-year, excluding the focal firm.

**Instrument Validation:**
- First-stage F-statistic: Must exceed 10 to avoid weak instrument bias
- Hansen J test: Overidentification test for instrument validity (p > 0.05 indicates instruments are valid)

**Newey-West Adjustment:**
- HAC (Heteroskedasticity and Autocorrelation Consistent) standard errors
- Accounts for both heteroskedasticity and serial correlation in panel data

**VIF Diagnostics:**
- Variance Inflation Factor calculated for all independent variables
- Threshold: VIF < 5 indicates acceptable multicollinearity levels

### Known Pitfalls and Warnings

> **WARNING: FE Collinearity Trap**
> Including both firm and industry fixed effects is redundant because firms do not change industries. This can cause rank deficiency in the design matrix. Solution: Use `check_rank=True` and allow absorbed effects to be dropped.
>
> **WARNING: Interaction Multicollinearity**
> Creating interaction terms without mean-centering causes high VIF (>10). Always center continuous variables before creating interactions.
>
> **WARNING: Weak Instruments in 2SLS**
> If first-stage F-statistic < 10, 2SLS is more biased than OLS. The infrastructure enforces F > 10 and falls back to OLS if instruments are weak.
>
> **WARNING: Manager FE Connectivity**
> With few "mover" CEOs who change firms, manager fixed effects conflate manager style with firm culture. Use manager FE only when sufficient within-manager variation exists.
>
> **WARNING: Multiple Testing in Subsamples**
> Running separate regressions on subsamples increases false discovery rate. Prefer interaction terms (e.g., `Uncertainty * HighLeverage_Dummy`) over subsample splits.

---

## H1 Cash Holdings Regression (Script 4.1_H1Regression.py)

Tests whether vague managers hold more cash as a precaution (H1) and whether leverage attenuates this effect (moderation).

### Model Specification

```
CashHoldings_{t+1} = beta_0 + beta_1*Uncertainty_t + beta_2*Leverage_t
                     + beta_3*(Uncertainty_t x Leverage_t)
                     + Controls + Firm_FE + Year_FE + Industry_FE + epsilon
```

**Where:**
- `CashHoldings_{t+1}`: Cash and marketable securities / Total assets (one-year ahead)
- `Uncertainty_t`: Speech vagueness measure (weak modals / total words)
- `Leverage_t`: Total debt / Total assets
- `Controls`: Firm size (log assets), Market-to-book (Tobin's Q), Cash flow, NWC, Capex, Leverage, Industry sigma, R&D

### Expected Signs

- `beta_1 > 0`: Vagueness increases cash holdings (precautionary motive)
- `beta_3 < 0`: Leverage attenuates the cash-vagueness relationship (debt discipline)

### Estimation

- **Primary:** Panel OLS with firm + year + industry fixed effects
- **Robustness:** 2SLS with manager prior-firm and industry-peer instruments
- **Standard Errors:** Clustered at firm level

### Output

- Coefficient table with beta, SE, t-stat, p-value
- Model fit statistics: R-squared (within, between, overall), N (observations), N (firms)
- Saved to: `4_Outputs/4_Econometric_V2/latest/h1_results.json`

---

## H2 Investment Efficiency Regression (Script 4.2_H2Regression.py)

Tests whether vagueness correlates with over/underinvestment relative to growth opportunities (H2).

### Model Specification

```
Efficiency_{t+1} = beta_0 + beta_1*Uncertainty_t + beta_2*Leverage_t
                   + beta_3*(Uncertainty_t x Leverage_t)
                   + Controls + Firm_FE + Year_FE + Industry_FE + epsilon
```

**Where:**
- `Efficiency_{t+1}`: Absolute deviation of investment from predicted level (one-year ahead)
  - Negative investment when Tobin's Q < 1 (underinvestment)
  - Positive investment when Tobin's Q > 1 (overinvestment)
- Alternative DV: `ROA Residual` from performance regression

### Expected Signs

- `beta_1 < 0`: Vagueness correlates with lower efficiency (more inefficient investment)
- `beta_3 > 0`: Leverage mitigates the vagueness-efficiency relationship

### Estimation

- Separate regressions for each DV specification (Efficiency Score, ROA Residual)
- Panel OLS with firm + year + industry fixed effects
- Standard errors clustered at firm level

### Output

- Coefficient tables for both DV specifications
- Saved to: `4_Outputs/4_Econometric_V2/latest/h2_results.json`

---

## H3 Payout Policy Regression (Script 4.3_H3Regression.py)

Tests whether vague managers have less stable dividend policies (H3) and whether leverage promotes smoothing.

### Model Specifications

**Stability Model:**

```
Stability_{t+1} = beta_0 + beta_1*Uncertainty_t + beta_2*Leverage_t
                  + beta_3*(Uncertainty_t x Leverage_t)
                  + Controls + Firm_FE + Year_FE + Industry_FE + epsilon
```

- `Stability_{t+1}`: Negative coefficient of variation of dividends over 3-year window
- Higher values = more stable payouts
- Expected: `beta_1 < 0` (vague managers have less stable policies)
- Expected: `beta_3 < 0` (leverage reduces instability)

**Flexibility Model:**

```
Flexibility_{t+1} = beta_0 + beta_1*Uncertainty_t + beta_2*Leverage_t
                    + beta_3*(Uncertainty_t x Leverage_t)
                    + Controls + Firm_FE + Year_FE + Industry_FE + epsilon
```

- `Flexibility_{t+1}`: Frequency of payout changes (dividend initiations, omissions, increases)
- Expected: `beta_1 > 0` (vague managers are more flexible)
- Expected: `beta_3 > 0` (leverage increases flexibility)

### Estimation

- Separate regressions for Stability and Flexibility DVs
- Panel OLS with firm + year + industry fixed effects
- Standard errors clustered at firm level

### Output

- Coefficient tables for both models
- Saved to: `4_Outputs/4_Econometric_V2/latest/h3_results.json`

---

## Robustness Checks (Scripts 4.4-4.6)

Each hypothesis has a dedicated robustness script:

| Script | Hypothesis | Tests |
|--------|------------|-------|
| 4.4_H1Robust.py | H1 Cash Holdings | Leverage subsample, Growth subsample, FCF subsample, Pre/post-2008, Alternative uncertainty, Crisis exclusion, Reverse causality |
| 4.5_H2Robust.py | H2 Investment Efficiency | Same tests as H1 |
| 4.6_H3Robust.py | H3 Payout Policy | Same tests as H1 |

### Robustness Test Specifications

**Leverage Subsample:**
- Below median leverage (low debt firms)
- Above median leverage (high debt firms)
- Compare coefficient sizes across subsamples

**Growth Subsample:**
- Tobin's Q <= 1.5 (low growth, value firms)
- Tobin's Q > 1.5 (high growth, growth firms)

**FCF Subsample:**
- Below median free cash flow (constrained firms)
- Above median free cash flow (unconstrained firms)

**Time Period Split:**
- Pre-2008 (before financial crisis)
- Post-2008 (after financial crisis)

**Alternative Uncertainty Measure:**
- Weak modals only (may, might, could)
- Excludes strong modals (will, shall, must)

**Crisis Year Exclusion:**
- Excluding 2008-2009 from sample
- Tests whether results are driven by crisis period

**Reverse Causality:**
- Regress uncertainty on lagged outcome variable
- Tests whether cash holdings predict future vagueness

---

## Identification Strategies (Script 4.7_Identification.py)

Additional tests to strengthen causal identification.

### Manager Fixed Effects

- Controls for time-invariant manager characteristics
- Requires within-manager variation (CEOs who changed firms)
- Reports within-manager R-squared and F-test for manager FE significance

### Propensity Score Matching

- Matches high-vagueness firms to similar low-vagueness firms
- Matching on: size, leverage, Tobin's Q, cash flow, industry, year
- Compares average treatment effect (ATE) of vagueness on outcomes

### Falsification Tests

Tests on placebo outcomes where no effect should exist:

- **H1 falsification:** Regress inventory/assets on vagueness (no theoretical relationship)
- **H2 falsification:** Regress administrative expenses on vagueness
- **H3 falsification:** Regress share repurchases on vagueness

Null results on placebo tests support the validity of main findings.

---

## Publication Output (Script 4.8_Publication.py)

Generates publication-ready tables and statistics.

### Output Format

**Coefficient Tables:**
- Beta coefficients
- Standard errors (clustered at firm level)
- t-statistics
- p-values (significance stars: *** p<0.01, ** p<0.05, * p<0.1)
- R-squared (within, between, overall)
- N (observations), N (firms)

**LaTeX-Formatted Tables:**
- Ready for inclusion in academic papers
- Follows standard journal format (e.g., JF, JFE, RFS)

**Economic Significance:**
- Effect of 1-SD change in uncertainty on outcome variable
- Marginal effects at mean leverage for interaction terms
- Compares economic magnitude to observable effects

**Complete Statistics File (stats.json):**
- All regression coefficients and diagnostics
- Model fit statistics
- Instrument validation (first-stage F, Hansen J)
- VIF scores
- Sample descriptive statistics

---

## Input/Output Mapping

| Type | Source | Contents |
|------|--------|----------|
| **Primary Input** | `4_Outputs/3_Financial_V2/latest/` | H1 variables: CashHoldings, Leverage, Controls<br>H2 variables: Efficiency, ROA_Residual, Controls<br>H3 variables: Stability, Flexibility, Controls |
| **Secondary Input** | `4_Outputs/2_Text_Processing/latest/` | Uncertainty measures: WeakModals, TotalWords, SpeechVagueness |
| **Output** | `4_Outputs/4_Econometric_V2/YYYY-MM-DD_HHMMSS/` | Regression results, coefficient tables, stats.json |
| **Logs** | `3_Logs/4_Econometric_V2/<timestamp>.log` | Execution logs with diagnostics |

---

## Script Execution Flow

```
4.0_EconometricInfra.py
     |
     | (Run once: creates shared utilities)
     v
4.1_H1Regression.py    4.2_H2Regression.py    4.3_H3Regression.py
     |                       |                       |
     | (Can run in parallel after infrastructure is ready)
     v                       v                       v
4.4_H1Robust.py        4.5_H2Robust.py         4.6_H3Robust.py
     |                       |                       |
     | (Can run in parallel after main regressions complete)
     v                       v                       v
                    4.7_Identification.py
                           |
                           | (Runs after all robustness checks)
                           v
                    4.8_Publication.py
                           |
                           v
                 Publication-ready output
```

### Execution Commands

```bash
# Infrastructure (run first)
python 2_Scripts/4_Econometric_V2/4.0_EconometricInfra.py

# Main regressions (can parallelize)
python 2_Scripts/4_Econometric_V2/4.1_H1Regression.py &
python 2_Scripts/4_Econometric_V2/4.2_H2Regression.py &
python 2_Scripts/4_Econometric_V2/4.3_H3Regression.py &
wait

# Robustness checks (can parallelize)
python 2_Scripts/4_Econometric_V2/4.4_H1Robust.py &
python 2_Scripts/4_Econometric_V2/4.5_H2Robust.py &
python 2_Scripts/4_Econometric_V2/4.6_H3Robust.py &
wait

# Identification (sequential)
python 2_Scripts/4_Econometric_V2/4.7_Identification.py

# Publication output (final step)
python 2_Scripts/4_Econometric_V2/4.8_Publication.py
```

---

## Key Econometric Notes

### Mean-Centering
Always center continuous variables before creating interaction terms. This reduces multicollinearity and makes coefficients interpretable as effects at the mean of other variables.

```python
# Correct approach
df['Uncertainty_Centered'] = df['Uncertainty'] - df['Uncertainty'].mean()
df['Leverage_Centered'] = df['Leverage'] - df['Leverage'].mean()
df['Interaction'] = df['Uncertainty_Centered'] * df['Leverage_Centered']
```

### Collinearity Between Fixed Effects
Firm and industry fixed effects are redundant because firms rarely change industries. Use `check_rank=True` to allow the estimator to drop collinear effects.

### Weak Instrument Rule
2SLS is only valid if first-stage F-statistic exceeds 10. Lower values indicate weak instruments that produce more bias than OLS. The infrastructure enforces this threshold.

### Clustering Standard Errors
By default, cluster standard errors at the firm level. This accounts for correlation of error terms within firms over time. For additional robustness, use double clustering (firm + year).

### Multiple Testing
When testing hypotheses across multiple subsamples, the false discovery rate increases. Prefer interaction terms with dummy variables over separate subsample regressions.
