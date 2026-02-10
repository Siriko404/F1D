# H1: Managerial Speech Uncertainty and Corporate Cash Holdings

**Generated:** 2026-02-10
**Source Script:** `2_Scripts/4_Econometric_V2/4.1_H1CashHoldingsRegression.py`
**Results Date:** 2026-02-05 16:51:25

---

## Hypothesis Statements

### Theoretical Motivation
Precautionary savings theory suggests that firms facing higher uncertainty should hold more cash as a buffer against adverse shocks. Managerial speech uncertainty reflects information opacity and internal uncertainty about future prospects, which should lead to higher cash holdings.

### Formal Hypotheses

**H1a:** Higher managerial speech uncertainty leads to increased corporate cash holdings.

$$H_1a: \beta_1 > 0$$

**H1b:** Financial leverage attenuates the positive uncertainty-cash relationship.

$$H_1b: \beta_3 < 0$$

The interaction term captures the moderating effect of leverage: highly leveraged firms have less capacity to increase cash holdings, so the uncertainty-cash relationship should be weaker.

---

## Model Specification

### Regression Equation

$$
\text{CashHoldings}_{i,t} = \beta_0 + \beta_1 \cdot \text{Uncertainty}_{i,t} + \beta_2 \cdot \text{Leverage}_{i,t} + \beta_3 \cdot (\text{Uncertainty}_{i,t} \times \text{Leverage}_{i,t}) + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

where:
- $\text{CashHoldings}_{i,t}$ = Cash and marketable securities / Total assets
- $\text{Uncertainty}_{i,t}$ = Speech uncertainty measure (6 variants)
- $\text{Leverage}_{i,t}$ = Total debt / Total assets
- $\text{Uncertainty}_{i,t} \times \text{Leverage}_{i,t}$ = Interaction term
- $\text{Controls}_{i,t}$ = Firm-level control variables (size, market-to-book, profitability, etc.)
- $\alpha_i$ = Firm fixed effects
- $\delta_t$ = Year fixed effects
- $\varepsilon_{i,t}$ = Error term

### Estimation Method

- **Estimator:** PanelOLS (Fixed Effects)
- **Fixed Effects:** Firm + Year
- **Standard Errors:** Clustered at firm level
- **Sample Period:** 2002-2018

### Dependent Variable

**CashHoldings:** Ratio of cash and marketable securities to total assets. This measures the firm's liquidity buffer.

---

## Primary Results

### Complete Results Table

| Uncertainty Measure | N | R² | β₁ (SE) | t-stat | p₁ (one-tailed) | β₃ (SE) | t-stat | p₃ (one-tailed) | H1a | H1b |
|---|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 21,557 | 0.1287 | 0.0036 (0.0038) | 0.95 | 0.1667 | -0.0292 (0.0196) | -1.49 | 0.0687 | No | No |
| CEO_QA_Uncertainty_pct | 16,829 | 0.1316 | 0.0008 (0.0030) | 0.27 | 0.3921 | -0.0216 (0.0136) | -1.59 | 0.0557 | No | No |
| Manager_QA_Weak_Modal_pct | 21,557 | 0.1288 | 0.0002 (0.0064) | 0.03 | 0.4852 | **-0.0690 (0.0341)** | -2.02 | 0.0216 | No | **Yes** |
| CEO_QA_Weak_Modal_pct | 16,829 | 0.1316 | -0.0036 (0.0049) | -0.73 | 0.7706 | -0.0263 (0.0217) | -1.21 | 0.1131 | No | No |
| Manager_Pres_Uncertainty_pct | 21,690 | 0.1290 | -0.0056 (0.0039) | -1.44 | 0.9225 | 0.0148 (0.0186) | 0.80 | 0.7864 | No | No |
| CEO_Pres_Uncertainty_pct | 16,667 | 0.1327 | 0.0016 (0.0032) | 0.50 | 0.3066 | -0.0093 (0.0154) | -0.60 | 0.2737 | No | No |

**Note:** Significance level: p < 0.05 (one-tailed). Bold indicates statistical significance. t-stats are calculated as coefficient/SE.

---

## Hypothesis Test Outcomes

### H1a: β₁ > 0 (Uncertainty → More Cash)

**Result: NOT SUPPORTED**

- **Significant measures:** 0/6
- **Direction:** Mixed (3 positive, 3 negative)
- **Interpretation:** No evidence that speech uncertainty increases cash holdings

### H1b: β₃ < 0 (Leverage Attenuates Uncertainty-Cash Relationship)

**Result: WEAK SUPPORT**

- **Significant measures:** 1/6
- **Supporting measure:** Manager_QA_Weak_Modal_pct
  - β₃ = -0.0690 (SE = 0.0341)
  - t-stat = -2.02
  - p = 0.0216 (one-tailed)
- **Interpretation:** Limited evidence that leverage moderates the uncertainty-cash relationship

---

## Sample Statistics

| Statistic | Value |
|---|---|
| **Total Observations** | 21,690 (maximum) |
| **Firms** | ~2,000+ |
| **Sample Period** | 2002-2018 |
| **R² Range** | 0.1287 - 0.1327 |
| **Observations per Measure** | 16,667 - 21,690 |

### Sample Composition

- **Manager measures:** 21,557 - 21,690 observations
- **CEO measures:** 16,667 - 16,829 observations
- **QA measures:** Match Manager measures
- **Presentation measures:** Match Manager measures

---

## Robustness Checks

### Specification Comparison

| Specification | Entity FE | Time FE | Cluster SE | Notes |
|---|---|---|---|---|
| **primary** | Yes (Firm) | Yes (Year) | Firm | Main specification |
| **pooled** | No | No | Firm | OLS without fixed effects |
| **year_only** | No | Yes | Firm | Year FE only |
| **double_cluster** | Yes (Firm) | Yes (Year) | Firm + Year | Two-way clustering |

### Robustness Summary

The primary specification (Firm + Year FE with firm-clustered SE) provides the most rigorous identification strategy. The robustness specifications test sensitivity to:
- Fixed effects inclusion
- Clustering structure
- Model specification (pooled OLS vs. fixed effects)

---

## Economic Interpretation

### Significant Finding (H1b)

For **Manager_QA_Weak_Modal_pct**, the interaction coefficient β₃ = -0.0690 indicates that:

$$
\frac{\partial^2 \text{CashHoldings}}{\partial \text{Uncertainty} \partial \text{Leverage}} = -0.0690
$$

**Interpretation:** A 1 percentage point increase in leverage reduces the uncertainty-cash sensitivity by 0.069 percentage points. For a firm at median leverage, this represents a meaningful moderation effect.

**Example:** If leverage increases from 0.20 to 0.30 (10 pp), the effect of uncertainty on cash holdings decreases by 0.69 pp.

---

## Conclusion

**H1a:** Managerial speech uncertainty does **NOT** significantly increase corporate cash holdings. None of the 6 uncertainty measures show a statistically significant positive effect at the 5% level (one-tailed).

**H1b:** Leverage provides **WEAK** attenuation of the uncertainty-cash relationship. Only Manager_QA_Weak_Modal_pct shows a significant negative interaction (p = 0.0216).

**Overall:** The precautionary savings motivation for cash holdings in response to speech uncertainty is not supported by the data. While leverage may moderate the relationship for hedging language (weak modal verbs), the main effect of uncertainty on cash is not statistically distinguishable from zero.

---

*This documentation provides complete regression results for academic supervisor review and thesis defense.*
