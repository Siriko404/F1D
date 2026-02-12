# H3: Managerial Speech Uncertainty and Payout Policy

---

## Model Specification

### Regression Equation

$$
\text{PayoutMeasure}_{i,t} = \beta_0 + \beta_1 \cdot \text{Uncertainty}_{i,t} + \beta_2 \cdot \text{Leverage}_{i,t} + \beta_3 \cdot (\text{Uncertainty}_{i,t} \times \text{Leverage}_{i,t}) + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypotheses:**
- H3a_stability: $\beta_1 < 0$ (Uncertainty → Less Dividend Stability)
- H3b_stability: $\beta_3 < 0$ (Leverage amplifies negative effect)
- H3a_flexibility: $\beta_1 > 0$ (Uncertainty → More Payout Flexibility)
- H3b_flexibility: $\beta_3 > 0$ (Leverage amplifies positive effect)

**Estimation:** PanelOLS with Firm + Year FE, firm-clustered SE, Sample: 2002-2018

---

## Regression Results

### Table 1: H3 Payout Policy Regression Results (div_stability DV)

| Variable | (1) | (2) | (3) | (4) | (5) | (6) |
|----------|--------|--------|--------|--------|--------|--------|
| | | | | | | | |
**Uncertainty Measures** | | | | | | | |
Manager_QA_Uncertainty_pct | -0.0262 | (0.0250) | -1.05 | 0.1475 | 0.2599 | (0.1633) |
CEO_QA_Uncertainty_pct | -0.0172 | (0.0207) | -0.83 | 0.2031 | -0.0389 | (0.1176) |
Manager_QA_Weak_Modal_pct | 0.0106 | (0.0294) | 0.36 | 0.6413 | 0.0958 | (0.2559) |
CEO_QA_Weak_Modal_pct | 0.0399 | (0.0293) | 1.36 | 0.9132 | -0.0423 | (0.1740) |
Manager_Pres_Uncertainty_pct | -0.0375 | (0.0283) | -1.33 | 0.0926 | 0.1185 | (0.1418) |
CEO_Pres_Uncertainty_pct | -0.0833** | (0.0270) | -3.09 | 0.0010 | 0.2308 | (0.1477) |
| | | | | | | | |
**Controls** | | | | | | | |
Leverage | | | | | | | |
earnings_volatility | 0.0000 | (0.0092) | 0.00 | 0.990 | | |
fcf_growth | -0.0034* | (0.0018) | -1.89 | 0.059 | | |
firm_maturity | -0.0026* | (0.0014) | -1.86 | 0.063 | | |
firm_size | -0.0013 | (0.0011) | -1.17 | 0.241 | | |
roa | -0.0187** | (0.0077) | -2.43 | 0.015 | | |
tobins_q | 0.0019 | (0.0032) | 0.60 | 0.549 | | |
cash_holdings | -0.0086** | (0.0038) | -2.27 | 0.023 | | |
| | | | | | | | |
**Fixed Effects** | Yes | Yes | Yes | Yes | Yes | Yes |
**N (div_stability)** | 243,492 | 182,748 | 243,492 | 182,748 | 244,358 | 180,401 |
**R²** | 0.0420 | 0.0435 | 0.0416 | 0.0436 | 0.0422 | 0.0445 |

### Table 2: H3 Payout Policy Regression Results (payout_flexibility DV)

| Variable | (1) | (2) | (3) | (4) | (5) | (6) |
|----------|--------|--------|--------|--------|--------|--------|
| | | | | | | | |
**Uncertainty Measures** | | | | | | | |
Manager_QA_Uncertainty_pct | 0.0134 | (0.0132) | 1.02 | 0.1546 | -0.0091 | (0.0734) |
CEO_QA_Uncertainty_pct | 0.0013 | (0.0113) | 0.12 | 0.4545 | -0.0512 | (0.0559) |
Manager_QA_Weak_Modal_pct | 0.0413** | (0.0154) | 2.68 | 0.0037 | -0.0729 | (0.1195) |
CEO_QA_Weak_Modal_pct | 0.0222 | (0.0182) | 1.22 | 0.1116 | -0.1385 | (0.0886) |
Manager_Pres_Uncertainty_pct | 0.0044 | (0.0145) | 0.30 | 0.3815 | -0.0237 | (0.0668) |
CEO_Pres_Uncertainty_pct | -0.0046 | (0.0135) | -0.34 | 0.6317 | -0.0881 | (0.0678) |
| | | | | | | | |
**Controls** | | | | | | | |
Leverage | | | | | | | |
earnings_volatility | -0.0035 | (0.0052) | -0.68 | 0.500 | | |
fcf_growth | 0.0031 | (0.0034) | 0.90 | 0.636 | | |
firm_maturity | 0.0011 | (0.0016) | 0.66 | 0.512 | | |
firm_size | 0.0002 | (0.0009) | 0.22 | 0.828 | | |
roa | -0.0122 | (0.0087) | -1.40 | 0.161 | | |
tobins_q | 0.0016 | (0.0026) | 0.62 | 0.537 | | |
cash_holdings | 0.0020 | (0.0020) | 1.02 | 0.309 | | |
| | | | | | | | |
**Fixed Effects** | Yes | Yes | Yes | Yes | Yes | Yes |
**N (payout_flexibility)** | 243,713 | 182,868 | 243,713 | 182,868 | 244,579 | 180,521 |
**R²** | 0.0212 | 0.0250 | 0.0218 | 0.0256 | 0.0212 | 0.0247 |

**Notes:**
- *** p < 0.01, ** p < 0.05, * p < 0.10
- Dependent variable: PayoutMeasure (t+1) - div_stability or payout_flexibility
- Standard errors clustered at firm level in parentheses
- H3a_stability tests β₁ < 0: Only CEO_Pres_Uncertainty_pct significant (-0.0833**)
- H3b_stability tests β₃ < 0: None significant
- H3a_flexibility tests β₁ > 0: Only Manager_QA_Weak_Modal_pct significant (0.0413**)
- H3b_flexibility tests β₃ > 0: None significant
- All specifications include firm and year fixed effects

**Outcome:** H3a_stability WEAK SUPPORT (1/6), H3b_stability NOT SUPPORTED (0/6), H3a_flexibility WEAK SUPPORT (1/6), H3b_flexibility NOT SUPPORTED (0/6)

---

## Control Variables

| Variable | Description | Source |
|----------|-------------|---------|
| earnings_volatility | Earnings volatility - Earnings risk | Compustat |
| fcf_growth | Free cash flow growth - Cash flow dynamics | Compustat |
| firm_maturity | Firm age - Lifecycle stage | Compustat |
| firm_size | Log(total assets) - Firm size | Compustat |
| roa | Return on assets - Profitability | Compustat |
| tobins_q | Tobin's Q - Investment opportunities | Compustat |
| cash_holdings | Cash-to-assets ratio - Financial slack | Compustat (H1) |
| leverage | Debt-to-assets ratio - Financial constraints | Compustat (H1) |

**All control variables are winsorized at 1%/99% and lagged appropriately for causal identification.**
