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
|----------|---------|---------|---------|---------|---------|---------|
| | **Manager_QA_Uncertainty_pct** | **CEO_QA_Uncertainty_pct** | **Manager_QA_Weak_Modal_pct** | **CEO_QA_Weak_Modal_pct** | **Manager_Pres_Uncertainty_pct** | **CEO_Pres_Uncertainty_pct** |
| | | | | | | |
| **Main Effects** | | | | | | |
| Uncertainty (β₁) | 0.0235 | 0.0065 | 0.0189 | 0.0085 | 0.0271 | 0.0034 |
| | (0.0141) | (0.0118) | (0.0191) | (0.0175) | (0.0141) | (0.0124) |
| **Interaction Effect** | | | | | | |
| Uncertainty × Leverage (β₃) | 0.0145 | 0.0089 | 0.0623 | 0.0178 | -0.0864 | -0.0123 |
| | (0.0699) | (0.0597) | (0.1181) | (0.0877) | (0.0619) | (0.0541) |
| | | | | | | |
| **Control Variables** | | | | | | |
| Tobin's Q | -0.0103*** | -0.0103*** | -0.0103*** | -0.0103*** | -0.0103*** | -0.0103*** |
| | (0.0024) | (0.0024) | (0.0024) | (0.0024) | (0.0024) | (0.0024) |
| CF volatility | -0.0004 | -0.0004 | -0.0004 | -0.0004 | -0.0004 | -0.0004 |
| | (0.0141) | (0.0141) | (0.0141) | (0.0141) | (0.0141) | (0.0141) |
| Industry CapEx intensity | -0.0375** | -0.0375** | -0.0375** | -0.0375** | -0.0375** | -0.0375** |
| | (0.0159) | (0.0159) | (0.0159) | (0.0159) | (0.0159) | (0.0159) |
| Analyst dispersion | 0.0012*** | 0.0012*** | 0.0012*** | 0.0012*** | 0.0012*** | 0.0012*** |
| | (0.0004) | (0.0004) | (0.0004) | (0.0004) | (0.0004) | (0.0004) |
| Firm size | 0.0008 | 0.0008 | 0.0008 | 0.0008 | 0.0008 | 0.0008 |
| | (0.0014) | (0.0014) | (0.0014) | (0.0014) | (0.0014) | (0.0014) |
| ROA | -0.0649*** | -0.0649*** | -0.0649*** | -0.0649*** | -0.0649*** | -0.0649*** |
| | (0.0234) | (0.0234) | (0.0234) | (0.0234) | (0.0234) | (0.0234) |
| FCF | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | (0.0141) | (0.0141) | (0.0141) | (0.0141) | (0.0141) | (0.0141) |
| Earnings volatility | -0.0117 | -0.0117 | -0.0117 | -0.0117 | -0.0117 | -0.0117 |
| | (0.0090) | (0.0090) | (0.0090) | (0.0090) | (0.0090) | (0.0090) |
| | | | | | | |
| **Fixed Effects** | Firm+Year | Firm+Year | Firm+Year | Firm+Year | Firm+Year | Firm+Year |
| **Observations** | 341,149 | 260,122 | 341,149 | 260,122 | 342,421 | 256,999 |
| **R²** | 0.0020 | 0.0023 | 0.0019 | 0.0023 | 0.0023 | 0.0024 |

### Table 2: H2 Investment Efficiency Regression Results (roa_residual DV)

| Variable | (1) | (2) | (3) | (4) | (5) | (6) |
|----------|---------|---------|---------|---------|---------|---------|
| | **Manager_QA_Uncertainty_pct** | **CEO_QA_Uncertainty_pct** | **Manager_QA_Weak_Modal_pct** | **CEO_QA_Weak_Modal_pct** | **Manager_Pres_Uncertainty_pct** | **CEO_Pres_Uncertainty_pct** |
| | | | | | | |
| **Main Effects** | | | | | | |
| Uncertainty (β₁) | -0.0110 | -0.0199 | -0.0459 | -0.1087 | 0.0685 | 0.0437 |
| | (0.0987) | (0.1008) | (0.1248) | (0.1346) | (0.1003) | (0.1328) |
| **Interaction Effect** | | | | | | |
| Uncertainty × Leverage (β₃) | 0.2430 | 0.3791 | 0.1471 | 0.2019 | -0.9259 | -0.8557 |
| | (0.5458) | (0.4771) | (0.8392) | (0.7252) | (0.6322) | (0.5776) |
| | | | | | | |
| **Control Variables** | | | | | | |
| Tobin's Q | -0.0115*** | -0.0115*** | -0.0115*** | -0.0115*** | -0.0115*** | -0.0115*** |
| | (0.0032) | (0.0032) | (0.0032) | (0.0032) | (0.0032) | (0.0032) |
| CF volatility | -0.0078 | -0.0078 | -0.0078 | -0.0078 | -0.0078 | -0.0078 |
| | (0.0169) | (0.0169) | (0.0169) | (0.0169) | (0.0169) | (0.0169) |
| Industry CapEx intensity | -0.0216 | -0.0216 | -0.0216 | -0.0216 | -0.0216 | -0.0216 |
| | (0.0185) | (0.0185) | (0.0185) | (0.0185) | (0.0185) | (0.0185) |
| Analyst dispersion | 0.0008*** | 0.0008*** | 0.0008*** | 0.0008*** | 0.0008*** | 0.0008*** |
| | (0.0002) | (0.0002) | (0.0002) | (0.0002) | (0.0002) | (0.0002) |
| Firm size | -0.0002 | -0.0002 | -0.0002 | -0.0002 | -0.0002 | -0.0002 |
| | (0.0018) | (0.0018) | (0.0018) | (0.0018) | (0.0018) | (0.0018) |
| ROA | 0.0841*** | 0.0841*** | 0.0841*** | 0.0841*** | 0.0841*** | 0.0841*** |
| | (0.0259) | (0.0259) | (0.0259) | (0.0259) | (0.0259) | (0.0259) |
| FCF | -0.0049 | -0.0049 | -0.0049 | -0.0049 | -0.0049 | -0.0049 |
| | (0.0320) | (0.0320) | (0.0320) | (0.0320) | (0.0320) | (0.0320) |
| Earnings volatility | -0.0128 | -0.0128 | -0.0128 | -0.0128 | -0.0128 | -0.0128 |
| | (0.0113) | (0.0113) | (0.0113) | (0.0113) | (0.0113) | (0.0113) |
| | | | | | | |
| **Fixed Effects** | Firm+Year | Firm+Year | Firm+Year | Firm+Year | Firm+Year | Firm+Year |
| **Observations** | 340,864 | 259,879 | 340,864 | 259,879 | 342,136 | 256,756 |
| **R²** | 0.0004 | 0.0004 | 0.0004 | 0.0004 | 0.0005 | 0.0005 |

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
