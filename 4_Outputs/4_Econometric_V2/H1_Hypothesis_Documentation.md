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

## Results

### Complete Results Table

| Uncertainty Measure | N | R² | β₁ (SE) | t-stat | p₁ | β₃ (SE) | t-stat | p₃ | H1a | H1b |
|---|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 21,557 | 0.1287 | 0.0036 (0.0038) | 0.95 | 0.1667 | -0.0292 (0.0196) | -1.49 | 0.0687 | No | No |
| CEO_QA_Uncertainty_pct | 16,829 | 0.1316 | 0.0008 (0.0030) | 0.27 | 0.3921 | -0.0216 (0.0136) | -1.59 | 0.0557 | No | No |
| Manager_QA_Weak_Modal_pct | 21,557 | 0.1288 | 0.0002 (0.0064) | 0.03 | 0.4852 | **-0.0690 (0.0341)** | -2.02 | 0.0216 | No | **Yes** |
| CEO_QA_Weak_Modal_pct | 16,829 | 0.1316 | -0.0036 (0.0049) | -0.73 | 0.7706 | -0.0263 (0.0217) | -1.21 | 0.1131 | No | No |
| Manager_Pres_Uncertainty_pct | 21,690 | 0.1290 | -0.0056 (0.0039) | -1.44 | 0.9225 | 0.0148 (0.0186) | 0.80 | 0.7864 | No | No |
| CEO_Pres_Uncertainty_pct | 16,667 | 0.1327 | 0.0016 (0.0032) | 0.50 | 0.3066 | -0.0093 (0.0154) | -0.60 | 0.2737 | No | No |

**Note:** Significance level: p < 0.05 (one-tailed). Bold indicates statistical significance.

**Outcome:** H1a NOT SUPPORTED (0/6 significant), H1b WEAK SUPPORT (1/6 significant)

---

## Control Variables

| Variable | Description | Source |
|----------|-------------|---------|
| firm_size | Log(total assets) - Firm size control | Compustat (AT) |
| tobins_q | Tobin's Q - Market-to-book ratio | Compustat |
| roa | Return on assets - Profitability measure | Compustat |
| capex_at | Capital expenditures / Total assets - Investment intensity | Compustat |
| dividend_payer | Dividend payer dummy - Payout policy indicator | Compustat |
| ocf_volatility | Operating cash flow volatility - Cash flow risk | Compustat |
| current_ratio | Current ratio - Liquidity measure | Compustat |
| leverage | Debt / Total assets - Leverage control | Compustat |

**All control variables are winsorized at 1%/99% and lagged appropriately for causal identification.**
