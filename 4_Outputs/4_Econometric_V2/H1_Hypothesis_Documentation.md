# H1: Managerial Speech Uncertainty and Corporate Cash Holdings

---

## Model Specification

### Regression Equation

$$
\text{CashHoldings}_{i,t} = \beta_0 + \beta_1 \cdot \text{Uncertainty}_{i,t} + \beta_2 \cdot \text{Leverage}_{i,t} + \beta_3 \cdot (\text{Uncertainty}_{i,t} \times \text{Leverage}_{i,t}) + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypotheses:**
- H1a: $\beta_1 > 0$ (Uncertainty → More Cash)
- H1b: $\beta_3 < 0$ (Leverage attenuates uncertainty-cash relationship)

**Estimation:** PanelOLS with Firm + Year FE, firm-clustered SE, Sample: 2002-2018

---

## Regression Results

### Table 1: H1 Cash Holdings Regression Results

| Variable | (1) | (2) | (3) | (4) | (5) | (6) | (7) | (8) |
|----------|--------|--------|--------|--------|--------|--------|--------|
| | | | | | | | | | |
**Uncertainty Measures** | | | | | | | | |
Manager_QA_Uncertainty_pct | 0.0036 | (0.0038) | 0.95 | 0.1667 | -0.0292 | (0.0699) | -1.49 | 0.0687 | | |
CEO_QA_Uncertainty_pct | 0.0008 | (0.0030) | 0.27 | 0.3921 | -0.0216 | (0.0136) | -1.59 | 0.0557 | | |
Manager_QA_Weak_Modal_pct | 0.0002 | (0.0064) | 0.03 | 0.4852 | **-0.0690** | (0.0341) | -2.02 | 0.0216 | | |
CEO_QA_Weak_Modal_pct | -0.0036 | (0.0049) | -0.73 | 0.7706 | -0.0263 | (0.0217) | -1.21 | 0.1131 | | |
Manager_Pres_Uncertainty_pct | -0.0056 | (0.0039) | -1.44 | 0.9225 | 0.0148 | (0.0186) | 0.80 | 0.7864 | | |
CEO_Pres_Uncertainty_pct | 0.0016 | (0.0032) | 0.50 | 0.3066 | -0.0093 | (0.0154) | -0.60 | 0.2737 | | |
| | | | | | | | | | |
**Controls** | | | | | | | | | |
Leverage (β₂) | 0.0148 | (0.0196) | 0.75 | 0.1667 | -0.0292 | (0.0699) | -1.49 | 0.0687 | | |
| | | | | | | | | | |
Firm size | -0.0083*** | -0.0083*** | -0.0083*** | -4.62 | <0.0001 | | | | |
Tobin's Q | 0.0019 | 0.0019 | 0.0032 | 0.60 | 0.549 | | | | |
ROA | -0.0187*** | -0.0187*** | -0.0187*** | -2.43 | 0.015 | | | | |
CapEx/Assets | -0.0679*** | -0.0679*** | -0.0679*** | -4.47 | <0.0001 | | | | |
Dividend payer | 0.0146** | 0.0146** | 0.0146** | 2.52 | 0.012 | | | | |
OCF volatility | 0.0000 | 0.0000 | 0.0000 | 0.00 | 0.967 | | | | |
Current ratio | -0.0034 | -0.0034 | -0.0034 | -0.89 | 0.375 | | | | |
| | | | | | | | | | | |
**Fixed Effects** | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
**N** | 15,970 | 15,970 | 15,970 | 15,970 | 15,970 | 15,970 | 15,970 | 15,970 |
**R²** | 0.0095 | 0.0107 | 0.0095 | 0.0115 | 0.0123 | 0.0097 | 0.0106 |

**Notes:**
- *** p < 0.01, ** p < 0.05, * p < 0.10
- Dependent variable: CashHoldings (t+1)
- Standard errors clustered at firm level in parentheses
- H1a tests β₁ > 0: Manager_QA_Uncertainty_pct (0.0036) and CEO_QA_Uncertainty_pct (0.0008) positive but insignificant; Manager_QA_Weak_Modal_pct (0.0002) and CEO_QA_Weak_Modal_pct (-0.0036) wrong direction
- H1b tests β₃ < 0: Only Manager_QA_Weak_Modal_pct × Leverage significant (-0.0690, p=0.0216)
- All specifications include firm and year fixed effects

**Outcome:** H1a NOT SUPPORTED (0/6 significant in expected direction), H1b WEAK SUPPORT (1/6 significant)

---

## Control Variables

| Variable | Description | Source |
|----------|-------------|---------|
| Firm size | Log(total assets) - Firm size control | Compustat (AT) |
| Tobin's Q | Tobin's Q - Market-to-book ratio | Compustat |
| ROA | Return on assets - Profitability measure | Compustat |
| CapEx/Assets | Capital expenditures / Total assets - Investment intensity | Compustat |
| Dividend payer | Dividend payer dummy - Payout policy indicator | Compustat |
| OCF volatility | Operating cash flow volatility - Cash flow risk | Compustat |
| Current ratio | Current ratio - Liquidity measure | Compustat |
| Leverage | Debt / Total assets - Leverage control | Compustat |

**All control variables are winsorized at 1%/99% and lagged appropriately for causal identification.**
