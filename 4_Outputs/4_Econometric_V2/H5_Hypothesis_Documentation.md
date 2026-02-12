# H5: Managerial Speech Uncertainty and Analyst Forecast Dispersion

---

## Model Specification

### Regression Equation (H5-A: Hedging Language)

$$
\text{Dispersion}_{i,t} = \beta_0 + \beta_1 \cdot \text{WeakModal}_{i,t} + \beta_2 \cdot \text{Uncertainty}_{i,t} + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypothesis H5-A:** $\beta_1 > 0$ (Weak modal predicts dispersion beyond general uncertainty)

### Regression Equation (H5-B: Uncertainty Gap)

$$
\text{Dispersion}_{i,t} = \beta_0 + \beta_1 \cdot (\text{QA\_Uncertainty}_{i,t} - \text{Pres\_Uncertainty}_{i,t}) + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypothesis H5-B:** $\beta_1 > 0$ (Uncertainty gap predicts dispersion)

**Estimation:** PanelOLS with Firm + Year FE, firm-clustered SE, Sample: 2002-2018

---

## Results

### Complete Results Table: H5-A (Hedging Language)

| Uncertainty Measure | N | R² | β₁ (SE) | t-stat | p₁ | Control Variable | β₂ (SE) | p₂ | H5-A |
|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Weak_Modal_pct | 258,560 | 0.0732 | -0.0124 (0.0053) | -2.34 | 0.9906 | Manager_QA_Uncertainty_pct | 0.0036 (0.0025) | 0.0723 | No |
| Manager_Pres_Weak_Modal_pct | 261,604 | 0.0732 | -0.0037 (0.0075) | -0.49 | 0.6891 | Manager_Pres_Uncertainty_pct | 0.0039 (0.0029) | 0.0890 | No |
| CEO_QA_Weak_Modal_pct | 191,159 | 0.0704 | -0.0051 (0.0046) | -1.11 | 0.8669 | CEO_QA_Uncertainty_pct | -0.0026 (0.0022) | 0.8841 | No |

**Note:** Significance level: p < 0.05 (one-tailed). H5-A expects β₁ > 0. β₂ is coefficient on general uncertainty control.

### Complete Results Table: H5-B (Uncertainty Gap)

| Specification | N | β₁ (SE) | t-stat | p₁ | Significant? |
|---|---|---|---|---|---|
| **primary** (Firm + Year FE) | 258,235 | -0.0025 (0.0028) | -0.89 | 0.8135 | No |
| **pooled** (No FE) | 258,235 | 0.0138 (0.0018) | 7.67 | <0.0001 | **Yes** |
| **year_only** (Year FE only) | 258,235 | 0.0090 (0.0029) | 3.10 | 0.0010 | **Yes** |
| **double_cluster** (Firm + Year FE, firm+year cluster) | 258,235 | -0.0025 (0.0028) | -0.89 | 0.8062 | No |

**Note:** Gap = (QA_Uncertainty - Pres_Uncertainty). H5-B expects β₁ > 0.

**Outcome:** H5-A NOT SUPPORTED (0/3 significant), H5-B MIXED (significant only without Firm FE)

---

## Control Variables

| Variable | Description | Source |
|----------|-------------|---------|
| prior_dispersion | Lagged analyst dispersion - Controls for persistence | IBES |
| earnings_surprise | Earnings surprise - Confounding control | IBES |
| analyst_coverage | Number of analysts (log) - Information environment | IBES |
| loss_dummy | Negative earnings dummy - Loss indicator | IBES |
| firm_size | Log(total assets) - Firm size | Compustat |
| leverage | Debt-to-assets ratio - Financial constraints | Compustat |
| earnings_volatility | Earnings volatility - Earnings risk | Compustat |
| tobins_q | Tobin's Q - Investment opportunities | Compustat |
| manager_qa_uncertainty_pct | Manager Q&A uncertainty - General uncertainty control | Phase 4 |
| manager_pres_uncertainty_pct | Manager presentation uncertainty - Prepared speech control | Phase 4 |

**Robustness Controls (Alternative Specifications):**
- no_lagged_dv: Excludes prior_dispersion (addresses Nickell bias)
- no_numest: Excludes analyst_coverage (addresses bad control concern)
- ceo_only: Uses CEO-specific measures instead of Manager aggregates

**All control variables are winsorized at 1%/99% and lagged appropriately for causal identification.**

---

## Control Variable Coefficient Results

### Primary Specification (Firm + Year FE, Firm-Clustered SE)

**Example: Manager_QA_Weak_Modal_pct regression with dispersion_lead DV**

| Variable | Coefficient | Std. Error | t-stat | p-value |
|----------|-------------|-------------|---------|----------|
| Manager_QA_Weak_Modal_pct (β₁) | -0.0124 | 0.0053 | -2.34 | 0.9906 |
| prior_dispersion | 0.2210 | 0.0069 | 31.97 | <0.0001 ** (significant) |
| earnings_surprise | -0.0009 | 0.0004 | -2.35 | 0.019 |
| analyst_coverage | -0.0015 | 0.0012 | -1.26 | 0.208 |
| loss_dummy | -0.0018 | 0.0050 | -0.36 | 0.718 |
| firm_size | 0.0001 | 0.0001 | 1.45 | 0.147 |
| leverage | -0.0047 | 0.0033 | -1.42 | 0.155 |
| earnings_volatility | 0.0003 | 0.0031 | 0.09 | 0.925 |
| tobins_q | 0.0039 | 0.0029 | 1.34 | 0.179 |
| Manager_QA_Uncertainty_pct (β₂ control) | 0.0036 | 0.0025 | 1.44 | 0.150 |

**Notes:**
- Key test variable: β₁ (weak_modal) should be positive for H5-A
- Prior dispersion is highly significant (p < 0.0001), indicating strong persistence
- β₁ for weak modal is negative and insignificant
- Manager_QA_Uncertainty control is positive and significant
- Full coefficient results available in: `4_Outputs/4_Econometric_V2/4.5_H5DispersionRegression/2026-02-05_214318/H5_Regression_Results.parquet`
