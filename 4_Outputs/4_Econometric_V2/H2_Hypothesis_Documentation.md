# H2: Managerial Speech Uncertainty and Investment Efficiency

---

## Model Specification

### Regression Equation

$$
\text{InvestmentResidual}_{i,t} = \beta_0 + \beta_1 \cdot \text{Uncertainty}_{i,t} + \beta_2 \cdot \text{Leverage}_{i,t} + \beta_3 \cdot (\text{Uncertainty}_{i,t} \times \text{Leverage}_{i,t}) + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypotheses:**
- H2a: $\beta_1 < 0$ (Uncertainty → Lower Investment Efficiency)
- H2b: $\beta_3 > 0$ (Leverage attenuates negative relationship)

**Estimation:** PanelOLS with Firm + Year FE, firm-clustered SE, Sample: 2002-2018

**Dependent Variables:** (1) efficiency_score (Biddle residuals), (2) roa_residual

---

## Regression Results

### Table 1: H2 Investment Efficiency Regression Results (efficiency_score DV)

| Variable | (1) | (2) | (3) | (4) | (5) | (6) |
|----------|--------|--------|--------|--------|--------|--------|
| | | | | | | | |
**Uncertainty Measures** | | | | | | | |
Manager_QA_Uncertainty_pct | 0.0235 | (0.0141) | 1.67 | 0.9527 | 0.0145 | (0.0699) |
CEO_QA_Uncertainty_pct | 0.0065 | (0.0118) | 0.55 | 0.7082 | 0.0089 | (0.0597) |
Manager_QA_Weak_Modal_pct | 0.0189 | (0.0191) | 0.99 | 0.8378 | 0.0623 | (0.1181) |
CEO_QA_Weak_Modal_pct | 0.0085 | (0.0175) | 0.49 | 0.6861 | 0.0178 | (0.0877) |
Manager_Pres_Uncertainty_pct | 0.0271 | (0.0141) | 1.92 | 0.9724 | -0.0864 | (0.0619) |
CEO_Pres_Uncertainty_pct | 0.0034 | (0.0124) | 0.27 | 0.6086 | -0.0123 | (0.0541) |
| | | | | | | | |
**Controls** | | | | | | | |
Leverage | | | | | | | |
tobins_q | -0.0103*** | (0.0024) | -4.26 | <0.0001 | | |
cf_volatility | -0.0004 | (0.0141) | -0.03 | 0.975 | | |
industry_capex_intensity | -0.0375** | (0.0159) | -2.36 | 0.018 | | |
analyst_dispersion | 0.0012*** | (0.0004) | 3.02 | 0.003 | | |
firm_size | 0.0008 | (0.0014) | 0.56 | 0.577 | | |
roa | -0.0649*** | (0.0234) | -2.77 | 0.006 | | |
fcf | 0.0000 | (0.0141) | 0.00 | 0.996 | | |
earnings_volatility | -0.0117 | (0.0090) | -1.30 | 0.194 | | |
| | | | | | | | |
**Fixed Effects** | Yes | Yes | Yes | Yes | Yes | Yes |
**N (efficiency_score)** | 341,149 | 260,122 | 341,149 | 260,122 | 342,421 | 256,999 |
**R²** | 0.0020 | 0.0023 | 0.0019 | 0.0023 | 0.0023 | 0.0024 |

### Table 2: H2 Investment Efficiency Regression Results (roa_residual DV)

| Variable | (1) | (2) | (3) | (4) | (5) | (6) |
|----------|--------|--------|--------|--------|--------|--------|
| | | | | | | | |
**Uncertainty Measures** | | | | | | | |
Manager_QA_Uncertainty_pct | -0.0110 | (0.0987) | -0.11 | 0.4557 | 0.2430 | (0.5458) |
CEO_QA_Uncertainty_pct | -0.0199 | (0.1008) | -0.20 | 0.4217 | 0.3791 | (0.4771) |
Manager_QA_Weak_Modal_pct | -0.0459 | (0.1248) | -0.37 | 0.3565 | 0.1471 | (0.8392) |
CEO_QA_Weak_Modal_pct | -0.1087 | (0.1346) | -0.81 | 0.2096 | 0.2019 | (0.7252) |
Manager_Pres_Uncertainty_pct | 0.0685 | (0.1003) | 0.68 | 0.7527 | -0.9259 | (0.6322) |
CEO_Pres_Uncertainty_pct | 0.0437 | (0.1328) | 0.33 | 0.6291 | -0.8557 | (0.5776) |
| | | | | | | | |
**Controls** | | | | | | | |
Leverage | | | | | | | |
tobins_q | -0.0115*** | (0.0032) | -3.55 | <0.0001 | | |
cf_volatility | -0.0078 | (0.0169) | -0.46 | 0.326 | | |
industry_capex_intensity | -0.0216 | (0.0185) | -1.17 | 0.243 | | |
analyst_dispersion | 0.0008*** | (0.0002) | 3.87 | <0.0001 | | |
firm_size | -0.0002 | (0.0018) | -0.12 | 0.452 | | |
roa | 0.0841*** | (0.0259) | 3.25 | 0.0012 | | |
fcf | -0.0049 | (0.0320) | -0.15 | 0.440 | | |
earnings_volatility | -0.0128 | (0.0113) | -1.13 | 0.259 | | |
| | | | | | | | |
**Fixed Effects** | Yes | Yes | Yes | Yes | Yes | Yes |
**N (roa_residual)** | 340,864 | 259,879 | 340,864 | 259,879 | 342,136 | 256,756 |
**R²** | 0.0004 | 0.0004 | 0.0004 | 0.0004 | 0.0005 | 0.0005 |

**Notes:**
- *** p < 0.01, ** p < 0.05, * p < 0.10
- Dependent variable: InvestmentResidual (t+1) - efficiency_score or roa_residual
- Standard errors clustered at firm level in parentheses
- H2a tests β₁ < 0: None significant (all coefficients wrong direction or insignificant)
- H2b tests β₃ > 0 (leverage × uncertainty interaction): Not significant in any specification
- All specifications include firm and year fixed effects

**Outcome:** H2a NOT SUPPORTED (0/12), H2b NOT SUPPORTED (0/12)

---

## Control Variables

| Variable | Description | Source |
|----------|-------------|---------|
| tobins_q | Tobin's Q - Investment opportunities | Compustat |
| cf_volatility | Cash flow volatility - Cash flow risk | Compustat |
| industry_capex_intensity | Industry capital expenditure intensity | Compustat |
| analyst_dispersion | Analyst forecast dispersion - Information environment | IBES |
| firm_size | Log(total assets) - Firm size | Compustat |
| roa | Return on assets - Profitability | Compustat |
| fcf | Free cash flow - Internal funds | Compustat |
| earnings_volatility | Earnings volatility - Earnings risk | Compustat |

**All control variables are winsorized at 1%/99% and lagged appropriately for causal identification.**
