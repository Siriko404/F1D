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

## Regression Results

### Table 1: H5-A Analyst Dispersion Regression Results (Hedging Language)

| Variable | (1) | (2) | (3) |
|----------|---------|---------|---------|
| | **Manager_QA_Weak_Modal_pct** | **Manager_Pres_Weak_Modal_pct** | **CEO_QA_Weak_Modal_pct** |
| | | | |
| **Key Variable** | | | |
| Weak Modal (β₁) | -0.0124** | -0.0037 | -0.0051 |
| | (0.0053) | (0.0075) | (0.0104) |
| | | | |
| **Control Variables** | | | |
| Prior dispersion | 0.2210*** | 0.2210*** | 0.2210*** |
| | (0.0069) | (0.0069) | (0.0070) |
| Earnings surprise | -0.0009** | -0.0009** | -0.0009** |
| | (0.0004) | (0.0004) | (0.0004) |
| Analyst coverage | -0.0015 | -0.0015 | -0.0015 |
| | (0.0012) | (0.0012) | (0.0012) |
| Loss dummy | -0.0018 | -0.0018 | -0.0018 |
| | (0.0050) | (0.0050) | (0.0050) |
| Firm size | 0.0001 | 0.0001 | 0.0001 |
| | (0.0001) | (0.0001) | (0.0001) |
| Leverage | -0.0047 | -0.0047 | -0.0047 |
| | (0.0033) | (0.0033) | (0.0033) |
| Earnings volatility | 0.0003 | 0.0003 | 0.0003 |
| | (0.0031) | (0.0031) | (0.0031) |
| Tobin's Q | 0.0039 | 0.0039 | 0.0039 |
| | (0.0029) | (0.0029) | (0.0029) |
| Manager QA uncertainty | 0.0036 | 0.0039 | -0.0026 |
| | (0.0025) | (0.0029) | (0.0022) |
| Manager Pres uncertainty | 0.0039 | 0.0040 | -0.0040 |
| | (0.0029) | (0.0034) | (0.0030) |
| | | | |
| **Fixed Effects** | Firm+Year | Firm+Year | Firm+Year |
| **Observations** | 258,560 | 261,604 | 191,159 |
| **R²** | 0.0732 | 0.0732 | 0.0704 |

### Table 2: H5-B Uncertainty Gap Regression Results

| Specification | Coefficient | Std. Error | t-stat | p-value | Significant? |
|---|---|---|---|---|---|
| **Primary** (Firm+Year FE) | -0.0025 | (0.0028) | -0.89 | 0.8135 | No |
| **Pooled OLS** (No FE) | 0.0138*** | (0.0018) | 7.67 | <0.0001 | Yes |
| **Year FE** (Year FE only) | 0.0090*** | (0.0029) | 3.10 | 0.0010 | Yes |
| **Double cluster** (Firm+Year FE, 2-way cluster) | -0.0025 | (0.0028) | -0.89 | 0.8062 | No |

**Sample size:** N = 258,235 across all specifications

**Notes:**
- *** p < 0.01, ** p < 0.05, * p < 0.10
- Dependent variable: dispersion_lead (t+1)
- Standard errors clustered at firm level in parentheses
- H5-A expects β₁ > 0: All weak modal coefficients are negative (wrong direction)
- H5-B expects β₁ > 0: Significant only without Firm FE (not in primary specification)
- All specifications include firm and/or year fixed effects

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
