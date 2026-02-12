# H4: Leverage Discipline and Managerial Speech Uncertainty

---

## Model Specification

### Regression Equation

$$
\text{Uncertainty}_{i,t} = \beta_0 + \beta_1 \cdot \text{Leverage}_{i,t-1} + \beta_2 \cdot \text{AnalystUncertainty}_{i,t} + \beta_3 \cdot \text{PresentationUncertainty}_{i,t} + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypothesis:** H4: $\beta_1 < 0$ (Higher leverage → Lower uncertainty)

**Estimation:** PanelOLS with Firm + Year FE, firm-clustered SE, Sample: 2002-2018

**Key feature:** Leverage is lagged (t-1) to address reverse causality

---

## Results

### Complete Results Table

| Dependent Variable | N | R² | β₁ (SE) | t-stat | p (one-tailed) | F-stat | F p-value | H4 |
|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 245,731 | 0.0319 | **-0.0658 (0.0269)** | -2.45 | 0.0072 | 804.43 | 0.0000 | **Yes** |
| Manager_QA_Weak_Modal_pct | 245,731 | 0.0135 | **-0.0460 (0.0159)** | -2.89 | 0.0019 | 334.45 | 0.0000 | **Yes** |
| Manager_Pres_Uncertainty_pct | 245,731 | 0.0041 | 0.0228 (0.0402) | 0.57 | 0.7141 | 111.99 | 0.0000 | No |
| CEO_QA_Uncertainty_pct | 180,910 | 0.0286 | -0.0501 (0.0409) | -1.23 | 0.1098 | 528.74 | 0.0000 | No |
| CEO_QA_Weak_Modal_pct | 180,910 | 0.0111 | **-0.0480 (0.0245)** | -1.96 | 0.0251 | 201.84 | 0.0000 | **Yes** |
| CEO_Pres_Uncertainty_pct | 181,404 | 0.0019 | -0.0125 (0.0454) | -0.28 | 0.3906 | 37.40 | 0.0000 | No |

**Note:** Significance level: p < 0.05 (one-tailed). H4 expects β₁ < 0. Bold indicates statistical significance. F-statistics test joint significance of all regressors.

**Outcome:** H4 PARTIAL SUPPORT (3/6 significant)

---

## Control Variables

| Variable | Description | Source |
|----------|-------------|---------|
| analyst_qa_uncertainty | Analyst Q&A uncertainty - Controls for analyst questioning environment | IBES/Phase 4 |
| firm_size | Log(total assets) - Firm size | Compustat |
| tobins_q | Tobin's Q - Market-to-book ratio | Compustat |
| roa | Return on assets - Profitability | Compustat |
| cash_holdings | Cash-to-assets ratio - Financial slack | Compustat |
| dividend_payer | Dividend payer dummy - Payout policy | Compustat |
| firm_maturity | Firm age - Lifecycle stage | Compustat |
| earnings_volatility | Earnings volatility - Earnings risk | Compustat |
| leverage_lag1 | Lagged leverage (t-1) - Key independent variable | Compustat |
| presentation_uncertainty | Presentation uncertainty - Controls for prepared speech | Phase 4 |

**All control variables are winsorized at 1%/99% and lagged appropriately for causal identification.**

---

## Control Variable Coefficient Results

### Primary Specification (Firm + Year FE, Firm-Clustered SE)

**Example: Manager_QA_Uncertainty_pct regression (DV = Manager_QA_Uncertainty_pct)**

| Variable | Coefficient | Std. Error | t-stat | p-value |
|----------|-------------|-------------|---------|----------|
| leverage_lag1 (β₁) | -0.0658 | 0.0269 | -2.45 | 0.0072 ** (significant) |
| analyst_qa_uncertainty | 0.0764 | 0.0108 | 7.09 | <0.0001 ** (significant) |
| firm_size | -0.0185 | 0.0113 | -1.64 | 0.101 |
| tobins_q | -0.0009 | 0.0063 | -0.15 | 0.883 |
| roa | -0.0103 | 0.0071 | -1.45 | 0.147 |
| cash_holdings | 0.0034 | 0.0027 | 1.25 | 0.211 |
| dividend_payer | -0.0057 | 0.0056 | -1.01 | 0.313 |
| firm_maturity | 0.0005 | 0.0029 | 0.18 | 0.855 |
| earnings_volatility | -0.0002 | 0.0054 | -0.04 | 0.969 |
| presentation_uncertainty (for QA DVs) | 0.5239 | 0.0170 | 30.80 | <0.0001 ** (significant) |

**Notes:**
- β₁ (leverage_lag1) is the key hypothesis test coefficient: H4 expects β₁ < 0
- Manager_QA_Uncertainty and Manager_QA_Weak_Modal show significant leverage effects (β₁ < 0)
- Presentation uncertainty is included as control for QA DVs to distinguish prepared vs spontaneous speech
- Full coefficient results available in: `4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/2026-02-05_195212/H4_Regression_Results.parquet`
