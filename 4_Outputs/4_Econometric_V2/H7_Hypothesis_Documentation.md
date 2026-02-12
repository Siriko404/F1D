# H7: Managerial Speech Uncertainty and Stock Illiquidity

---

## Model Specification

### Regression Equation

$$
\text{Illiquidity}_{i,t} = \beta_0 + \beta_1 \cdot \text{Uncertainty}_{i,t} + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypothesis H7a:** $\beta_1 > 0$ (Uncertainty → Higher illiquidity)

**Estimation:** PanelOLS with Firm + Year FE, firm-clustered SE, Sample: 2002-2018

**Dependent Variable:** Amihud (2002) illiquidity measure

$$
\text{Illiquidity}_{i,t} = \frac{1}{D_{i,t}} \sum_{d=1}^{D_{i,t}} \frac{|R_{i,d}|}{\text{Volume}_{i,d}}
$$

---

## Regression Results

### Table 1: H7 Stock Illiquidity Regression Results (Primary Specification)

| Variable | (1) | (2) | (3) | (4) |
|----------|---------|---------|---------|---------|
| | **Manager_QA_Uncertainty_pct** | **CEO_QA_Uncertainty_pct** | **Manager_Pres_Uncertainty_pct** | **CEO_Pres_Uncertainty_pct** |
| | | | | |
| **Uncertainty Measures (β₁)** | | | | |
| Manager/CEO Uncertainty | 0.00125 | -0.00469 | 0.00431 | -0.00183 |
| | (0.00439) | (0.00360) | (0.00530) | (0.00513) |
| | | | | |
| **Control Variables** | | | | |
| Volatility | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | (0.0000) | (0.0000) | (0.0000) | (0.0000) |
| Stock return | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | (0.0000) | (0.0000) | (0.0000) | (0.0000) |
| | | | | |
| **Fixed Effects** | Firm+Year | Firm+Year | Firm+Year | Firm+Year |
| **Observations** | 26,135 | 28,444 | 37,340 | 27,900 |
| **R²** | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

### Table 2: Robustness Summary

| Specification | Alternative | Significant (p<0.05) |
|---|---|---|
| **Primary** | Amihud illiquidity | 0/4 |
| Alternative DV | Roll (1984) spread | 0/4 |
| Alternative DV | Log Amihud | 0/4 |
| Alternative IV | CEO only | 0/2 |
| Alternative IV | Presentation only | 0/2 |
| Alternative IV | QA only | 0/2 |
| **Total robustness** | 14 specifications | **0/14** |

**Notes:**
- *** p < 0.01, ** p < 0.05, * p < 0.10
- Dependent variable: Illiquidity (t+1) - Amihud measure (primary)
- Standard errors clustered at firm level in parentheses
- H7a expects β₁ > 0: All coefficients insignificant or wrong sign (negative for CEO measures)
- Significance level: FDR-corrected p < 0.05, one-tailed (β > 0)
- FDR q is Benjamini-Hochberg corrected p-value
- All specifications include firm and year fixed effects
- Minimum 50 trading days per year required

**Outcome:** H7a NOT SUPPORTED (0/4 primary, 0/14 robustness)

---

## Control Variables

| Variable | Description | Source |
|----------|-------------|---------|
| Volatility | Stock return volatility (annualized) - Market risk | CRSP Daily |
| StockRet | Annual stock return - Market performance | CRSP Daily |

**Primary Control Variables Used:**
- Volatility: Controls for stock risk factors
- StockRet: Controls for return performance

**Alternative Dependent Variables (Robustness):**
- Roll (1984) spread: Implicit bid-ask spread from serial covariance
- Log Amihud: Log-transformed illiquidity measure

**Alternative Independent Variables (Robustness):**
- CEO only: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct
- Presentation only: Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct
- QA only: Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct

**All variables are winsorized at 1%/99% with minimum 50 trading days per year required.**
