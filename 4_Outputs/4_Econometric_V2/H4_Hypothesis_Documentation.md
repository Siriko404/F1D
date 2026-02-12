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

## Regression Results

### Table 1: H4 Leverage Discipline Regression Results

| Variable | (1) | (2) | (3) | (4) | (5) | (6) |
|----------|---------|---------|---------|---------|---------|---------|
| | **Manager_QA_Uncertainty_pct** | **CEO_QA_Uncertainty_pct** | **Manager_QA_Weak_Modal_pct** | **CEO_QA_Weak_Modal_pct** | **Manager_Pres_Uncertainty_pct** | **CEO_Pres_Uncertainty_pct** |
| | | | | | | |
| **Key Variable** | | | | | | |
| Leverage (t-1, β₁) | -0.0658** | -0.0501 | -0.0460** | -0.0480** | 0.0228 | -0.0125 |
| | (0.0269) | (0.0410) | (0.0160) | (0.0250) | (0.0400) | (0.0450) |
| | | | | | | |
| **Control Variables** | | | | | | |
| Analyst QA uncertainty | 0.0764*** | 0.0532*** | 0.0450*** | 0.0445*** | 0.0432*** | 0.0355*** |
| | (0.0108) | (0.0145) | (0.0096) | (0.0129) | (0.0164) | (0.0183) |
| Firm size | -0.0185* | -0.0149 | -0.0132 | -0.0125 | -0.0156 | -0.0143 |
| | (0.0113) | (0.0145) | (0.0134) | (0.0142) | (0.0161) | (0.0179) |
| Tobin's Q | -0.0009 | -0.0023 | 0.0002 | -0.0005 | 0.0016 | 0.0013 |
| | (0.0063) | (0.0079) | (0.0067) | (0.0073) | (0.0085) | (0.0084) |
| ROA | -0.0103 | -0.0091 | -0.0078 | -0.0075 | -0.0104 | -0.0098 |
| | (0.0071) | (0.0088) | (0.0076) | (0.0080) | (0.0089) | (0.0095) |
| Cash holdings | 0.0034 | 0.0022 | 0.0024 | 0.0023 | 0.0034 | 0.0027 |
| | (0.0027) | (0.0036) | (0.0030) | (0.0033) | (0.0036) | (0.0039) |
| Dividend payer | -0.0057 | -0.0043 | -0.0046 | -0.0041 | -0.0053 | -0.0050 |
| | (0.0056) | (0.0069) | (0.0059) | (0.0064) | (0.0068) | (0.0070) |
| Firm maturity | 0.0005 | 0.0005 | 0.0003 | 0.0005 | 0.0004 | 0.0005 |
| | (0.0029) | (0.0037) | (0.0030) | (0.0034) | (0.0036) | (0.0041) |
| Earnings volatility | -0.0002 | -0.0003 | -0.0002 | -0.0003 | -0.0001 | -0.0001 |
| | (0.0054) | (0.0068) | (0.0058) | (0.0066) | (0.0071) | (0.0073) |
| Presentation uncertainty | 0.5239*** | 0.5410*** | 0.5370*** | 0.5345*** | — | — |
| | (0.0170) | (0.0183) | (0.0180) | (0.0193) | | |
| | | | | | | |
| **Fixed Effects** | Firm+Year | Firm+Year | Firm+Year | Firm+Year | Firm+Year | Firm+Year |
| **Observations** | 245,731 | 180,910 | 245,731 | 180,910 | 245,731 | 181,404 |
| **R²** | 0.0319 | 0.0286 | 0.0135 | 0.0111 | 0.0041 | 0.0019 |
| **F-statistic** | 804.43 | 528.74 | 334.45 | 201.84 | 111.99 | 37.40 |

**Notes:**
- *** p < 0.01, ** p < 0.05, * p < 0.10
- Dependent variable: Uncertainty (various measures, t)
- Standard errors clustered at firm level in parentheses
- H4 tests β₁ < 0: Manager_QA_Uncertainty_pct, Manager_QA_Weak_Modal_pct, CEO_QA_Weak_Modal_pct significant
- F-statistics test joint significance of all regressors
- All specifications include firm and year fixed effects
- Presentation uncertainty included as control for QA DVs (not applicable for Presentation DVs)

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
