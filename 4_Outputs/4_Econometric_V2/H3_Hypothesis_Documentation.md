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

## Results

### Complete Results Table: div_stability

| Uncertainty Measure | N | R² | β₁ (SE) | t-stat | p₁ | β₃ (SE) | t-stat | p₃ | H3a | H3b |
|---|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 243,492 | 0.0420 | -0.0262 (0.0250) | -1.05 | 0.1475 | 0.2599 (0.1633) | 1.59 | 0.9443 | No | No |
| CEO_QA_Uncertainty_pct | 182,748 | 0.0435 | -0.0172 (0.0207) | -0.83 | 0.2031 | -0.0389 (0.1176) | -0.33 | 0.3705 | No | No |
| Manager_QA_Weak_Modal_pct | 243,492 | 0.0416 | 0.0106 (0.0294) | 0.36 | 0.6413 | 0.0958 (0.2559) | 0.37 | 0.6460 | No | No |
| CEO_QA_Weak_Modal_pct | 182,748 | 0.0436 | 0.0399 (0.0293) | 1.36 | 0.9132 | -0.0423 (0.1740) | -0.24 | 0.4039 | No | No |
| Manager_Pres_Uncertainty_pct | 244,358 | 0.0422 | -0.0375 (0.0283) | -1.33 | 0.0926 | 0.1185 (0.1418) | 0.84 | 0.7983 | No | No |
| CEO_Pres_Uncertainty_pct | 180,401 | 0.0445 | **-0.0833 (0.0270)** | -3.09 | 0.0010 | 0.2308 (0.1477) | 1.56 | 0.9409 | **Yes** | No |

### Complete Results Table: payout_flexibility

| Uncertainty Measure | N | R² | β₁ (SE) | t-stat | p₁ | β₃ (SE) | t-stat | p₃ | H3a | H3b |
|---|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 243,713 | 0.0212 | 0.0134 (0.0132) | 1.02 | 0.1546 | -0.0091 (0.0734) | -0.12 | 0.5495 | No | No |
| CEO_QA_Uncertainty_pct | 182,868 | 0.0250 | 0.0013 (0.0113) | 0.12 | 0.4545 | -0.0512 (0.0559) | -0.92 | 0.8201 | No | No |
| Manager_QA_Weak_Modal_pct | 243,713 | 0.0218 | **0.0413 (0.0154)** | 2.68 | 0.0037 | -0.0729 (0.1195) | -0.61 | 0.7291 | **Yes** | No |
| CEO_QA_Weak_Modal_pct | 182,868 | 0.0256 | 0.0222 (0.0182) | 1.22 | 0.1116 | -0.1385 (0.0886) | -1.56 | 0.9409 | No | No |
| Manager_Pres_Uncertainty_pct | 244,579 | 0.0212 | 0.0044 (0.0145) | 0.30 | 0.3815 | -0.0237 (0.0668) | -0.35 | 0.6383 | No | No |
| CEO_Pres_Uncertainty_pct | 180,521 | 0.0247 | -0.0046 (0.0135) | -0.34 | 0.6317 | -0.0881 (0.0678) | -1.30 | 0.9033 | No | No |

**Note:** Significance level: p < 0.05 (one-tailed). Bold indicates statistical significance.

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
