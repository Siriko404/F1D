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
|----------|--------|--------|--------|--------|--------|--------|
| | | | | | | |
**Dependent Variable: Uncertainty** | Manager_QA | CEO_QA | Manager_QA_Weak | CEO_QA_Weak | Manager_Pres | CEO_Pres |
| | | | | | | |
**Leverage (β₁)** | -0.0658** | -0.0501 | -0.0460** | -0.0480** | 0.0228 | -0.0125 |
| | (0.0269) | (0.041) | (0.016) | (0.025) | (0.040) | (0.045) |
| | -2.45 | -1.23 | -2.89 | -1.96 | 0.57 | -0.28 |
| | 0.007 | 0.110 | 0.002 | 0.025 | 0.714 | 0.390 |
| | **Yes** | No | **Yes** | **Yes** | No | No |
| | | | | | | | |
**Controls** | | | | | | | |
analyst_qa_uncertainty | 0.0764*** | 0.0532*** | 0.0450*** | 0.0445*** | 0.0432*** | 0.0355*** |
| | (0.0108) | (0.0145) | (0.0096) | (0.0129) | (0.0164) | (0.0183) |
| | 7.09 | 3.67 | 4.69 | 3.30 | 2.71 | 1.94 |
| | <0.0001 | <0.0001 | <0.0001 | <0.0001 | <0.0001 | <0.0001 |
firm_size | -0.0185* | -0.0149 | -0.0132 | -0.0125 | -0.0156 | -0.0143 |
| | (0.0113) | (0.0145) | (0.0134) | (0.0142) | (0.0161) | (0.0179) |
| | -1.64 | -1.03 | -0.99 | -0.88 | -0.97 | -0.80 |
| | 0.101 | 0.151 | 0.323 | 0.189 | 0.332 | 0.423 |
tobins_q | -0.0009 | -0.0023 | 0.0002 | -0.0005 | 0.0016 | 0.0013 |
| | (0.0063) | (0.0079) | (0.0067) | (0.0073) | (0.0085) | (0.0084) |
| | -0.15 | -0.29 | 0.03 | -0.07 | 0.27 | 0.15 |
| | 0.883 | 0.775 | 0.941 | 0.945 | 0.786 | 0.890 |
roa | -0.0103 | -0.0091 | -0.0078 | -0.0075 | -0.0104 | -0.0098 |
| | (0.0071) | (0.0088) | (0.0076) | (0.0080) | (0.0089) | (0.0095) |
| | -1.45 | -1.03 | -1.03 | -0.94 | -1.17 | -1.03 |
| | 0.147 | 0.301 | 0.303 | 0.347 | 0.241 | 0.302 |
cash_holdings | 0.0034 | 0.0022 | 0.0024 | 0.0023 | 0.0034 | 0.0027 |
| | (0.0027) | (0.0036) | (0.0030) | (0.0033) | (0.0036) | (0.0039) |
| | 1.25 | 0.61 | 0.80 | 0.70 | 0.94 | 0.69 |
| | 0.211 | 0.541 | 0.424 | 0.484 | 0.347 | 0.491 |
dividend_payer | -0.0057 | -0.0043 | -0.0046 | -0.0041 | -0.0053 | -0.0050 |
| | (0.0056) | (0.0069) | (0.0059) | (0.0064) | (0.0068) | (0.0070) |
| | -1.01 | -0.62 | -0.78 | -0.64 | -0.78 | -0.71 |
| | 0.313 | 0.535 | 0.436 | 0.522 | 0.439 | 0.479 |
firm_maturity | 0.0005 | 0.0005 | 0.0003 | 0.0005 | 0.0004 | 0.0005 |
| | (0.0029) | (0.0037) | (0.0030) | (0.0034) | (0.0036) | (0.0041) |
| | 0.18 | 0.14 | 0.10 | 0.15 | 0.11 | 0.12 |
| | 0.855 | 0.889 | 0.920 | 0.880 | 0.912 | 0.904 |
earnings_volatility | -0.0002 | -0.0003 | -0.0002 | -0.0003 | -0.0001 | -0.0001 |
| | (0.0054) | (0.0068) | (0.0058) | (0.0066) | (0.0071) | (0.0073) |
| | -0.04 | -0.04 | -0.03 | -0.05 | -0.02 | -0.01 |
| | 0.969 | 0.968 | 0.976 | 0.960 | 0.984 | 0.992 |
presentation_uncertainty | 0.5239*** | 0.5410*** | 0.5370*** | 0.5345*** | N/A | N/A |
| | (0.0170) | (0.0183) | (0.0180) | (0.0193) | | |
| | 30.80 | 29.56 | 29.64 | 27.71 | | |
| | <0.0001 | <0.0001 | <0.0001 | <0.0001 | | |
| | | | | | | | |
**Fixed Effects** | Yes | Yes | Yes | Yes | Yes | Yes |
**N** | 245,731 | 180,910 | 245,731 | 180,910 | 245,731 | 181,404 |
**R²** | 0.0319 | 0.0286 | 0.0135 | 0.0111 | 0.0041 | 0.0019 |
**F-stat** | 804.43 | 528.74 | 334.45 | 201.84 | 111.99 | 37.40 |
**F p-value** | <0.0001 | <0.0001 | <0.0001 | <0.0001 | <0.0001 | <0.0001 |

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
