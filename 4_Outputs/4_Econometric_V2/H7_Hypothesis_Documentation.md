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

## Results

### Complete Results Table

| Uncertainty Measure | N | R² | β (SE) | t-stat | p (one-tailed) | FDR q | Significant? |
|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 26,135 | 0.0000 | 0.001253 (0.004389) | 0.29 | 0.3876 | 0.7753 | No |
| CEO_QA_Uncertainty_pct | 26,135 | 0.0000 | -0.004695 (0.003595) | -1.31 | 0.9041 | 0.9041 | No |
| Manager_Pres_Uncertainty_pct | 26,135 | 0.0000 | 0.004314 (0.005298) | 0.81 | 0.2078 | 0.7753 | No |
| CEO_Pres_Uncertainty_pct | 26,135 | 0.0000 | -0.001826 (0.005133) | -0.36 | 0.6390 | 0.8520 | No |

**Note:** Significance level: FDR-corrected p < 0.05, one-tailed (β > 0). FDR q is Benjamini-Hochberg corrected p-value.

### Robustness Summary

| Specification | Alternative | Significant (p<0.05) |
|---|---|---|
| **Primary** | Amihud illiquidity | 0/4 |
| Alternative DV | Roll (1984) spread | 0/4 |
| Alternative DV | Log Amihud | 0/4 |
| Alternative IV | CEO only | 0/2 |
| Alternative IV | Presentation only | 0/2 |
| Alternative IV | QA only | 0/2 |
| **Total robustness** | 14 specifications | **0/14** |

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

---

## Control Variable Coefficient Results

### Primary Specification (Firm + Year FE, Firm-Clustered SE)

**Example: Manager_QA_Uncertainty_pct regression with Amihud lag1 DV**

| Variable | Coefficient | Std. Error | t-stat | p-value |
|----------|-------------|-------------|---------|----------|
| Manager_QA_Uncertainty_pct (β₁) | 0.00125 | 0.00439 | 0.29 | 0.775 |
| Volatility | 0.0000 | 0.0000 | -0.02 | 0.983 |
| StockRet | 0.0000 | 0.0000 | 0.00 | 0.998 |

**Notes:**
- β₁ (uncertainty) is the key hypothesis test coefficient: H7a expects β₁ > 0
- Uncertainty coefficient is positive but not significant
- Control variables (Volatility, StockRet) are not significant
- Full coefficient results available in: `4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184021/H7_Regression_Results.parquet`

**All variables are winsorized at 1%/99% with minimum 50 trading days per year required.**
