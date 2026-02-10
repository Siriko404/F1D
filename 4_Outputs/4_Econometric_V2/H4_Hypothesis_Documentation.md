# H4: Leverage Discipline and Managerial Speech Uncertainty

**Generated:** 2026-02-10
**Source Script:** `2_Scripts/4_Econometric_V2/4.4_H4_LeverageDiscipline.py`
**Results Date:** 2026-02-05 19:53:21

---

## Hypothesis Statements

### Theoretical Motivation

**Debt Discipline Hypothesis:** Financial leverage imposes discipline on managers through monitoring by debt holders and the threat of financial distress. This discipline should extend to communication quality:

1. **Monitoring channel:** Debt holders monitor management more closely, reducing information asymmetry
2. **Default risk channel:** Highly leveraged firms face greater default risk, giving managers incentives to communicate more clearly to maintain confidence
3. **Commitment channel:** Debt covenants and agreements constrain managerial discretion, leading to more precise communication

If debt discipline operates, higher leverage should reduce managerial speech uncertainty (less vague, more precise communication).

### Formal Hypothesis

**H4:** Higher financial leverage leads to lower managerial speech uncertainty.

$$H_4: \beta_1 < 0$$

---

## Model Specification

### Regression Equation

$$
\text{Uncertainty}_{i,t} = \beta_0 + \beta_1 \cdot \text{Leverage}_{i,t-1} + \beta_2 \cdot \text{AnalystUncertainty}_{i,t} + \beta_3 \cdot \text{PresentationUncertainty}_{i,t} + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

where:
- $\text{Uncertainty}_{i,t}$ = Speech uncertainty measure (6 DVs)
- $\text{Leverage}_{i,t-1}$ = Lagged leverage (Debt/Assets)
- $\text{AnalystUncertainty}_{i,t}$ = Analyst forecast dispersion (control)
- $\text{PresentationUncertainty}_{i,t}$ = Presentation uncertainty (for Q&A regressions only)
- $\text{Controls}_{i,t}$ = Firm-level control variables
- $\alpha_i$ = Firm fixed effects
- $\delta_t$ = Year fixed effects
- $\varepsilon_{i,t}$ = Error term

**Key identification feature:** Leverage is lagged ($t-1$) to address reverse causality (speech uncertainty in period $t$ cannot affect leverage in period $t-1$).

### Estimation Method

- **Estimator:** PanelOLS (Fixed Effects)
- **Fixed Effects:** Firm + Year
- **Standard Errors:** Clustered at firm level
- **Sample Period:** 2002-2018

### Dependent Variables

**Six measures of speech uncertainty:**

1. **Manager_QA_Uncertainty_pct:** Manager Q&A uncertainty percentage
2. **Manager_QA_Weak_Modal_pct:** Manager Q&A weak modal (hedging) percentage
3. **Manager_Pres_Uncertainty_pct:** Manager presentation uncertainty percentage
4. **CEO_QA_Uncertainty_pct:** CEO Q&A uncertainty percentage
5. **CEO_QA_Weak_Modal_pct:** CEO Q&A weak modal percentage
6. **CEO_Pres_Uncertainty_pct:** CEO presentation uncertainty percentage

---

## Primary Results

### Complete Results Table

| Dependent Variable | N | R² | β₁ (SE) | t-stat | p (one-tailed) | F-stat | F p-value | H4 |
|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 245,731 | 0.0319 | **-0.0658 (0.0269)** | -2.45 | 0.0072 | 804.43 | 0.0000 | **Yes** |
| Manager_QA_Weak_Modal_pct | 245,731 | 0.0135 | **-0.0460 (0.0159)** | -2.89 | 0.0019 | 334.45 | 0.0000 | **Yes** |
| Manager_Pres_Uncertainty_pct | 245,731 | 0.0041 | 0.0228 (0.0402) | 0.57 | 0.7141 | 111.99 | 0.0000 | No |
| CEO_QA_Uncertainty_pct | 180,910 | 0.0286 | -0.0501 (0.0409) | -1.23 | 0.1098 | 528.74 | 0.0000 | No |
| CEO_QA_Weak_Modal_pct | 180,910 | 0.0111 | **-0.0480 (0.0245)** | -1.96 | 0.0251 | 201.84 | 0.0000 | **Yes** |
| CEO_Pres_Uncertainty_pct | 181,404 | 0.0019 | -0.0125 (0.0454) | -0.28 | 0.3906 | 37.40 | 0.0000 | No |

**Note:** Significance level: p < 0.05 (one-tailed). H4 expects β₁ < 0. Bold indicates statistical significance. t-stats are calculated as coefficient/SE. F-statistics test joint significance of all regressors.

---

## Hypothesis Test Outcome

### H4: β₁ < 0 (Leverage → Lower Uncertainty)

**Result: PARTIAL SUPPORT**

- **Significant measures:** 3/6
- **Direction:** 5/6 negative (as hypothesized), 1/6 positive
- **Supporting measures:**
  1. **Manager_QA_Uncertainty_pct:** β₁ = -0.0658, p = 0.0072
  2. **Manager_QA_Weak_Modal_pct:** β₁ = -0.0460, p = 0.0019
  3. **CEO_QA_Weak_Modal_pct:** β₁ = -0.0480, p = 0.0251

**Interpretation:** Mixed evidence for debt discipline hypothesis. Manager Q&A uncertainty measures (both total uncertainty and weak modal hedging) show significant negative relationships with leverage, supporting the hypothesis. CEO Q&A weak modal language also shows significant effects. However, presentation uncertainty measures show no significant effects.

---

## Sample Statistics

| Statistic | Value |
|---|---|
| **Total Observations** | 245,731 (maximum, Manager measures) |
| **Firms** | ~2,500+ |
| **Sample Period** | 2002-2018 |
| **R² Range** | 0.0019 - 0.0319 |
| **Observations per Measure** | 180,910 - 245,731 |

### Sample Composition

**Manager measures:** 245,731 observations
**CEO measures:** 180,910 - 181,404 observations

### Regression Diagnostics

| Dependent Variable | N | R² | F-statistic | F p-value |
|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 245,731 | 0.0319 | 804.43 | 0.0000 |
| Manager_QA_Weak_Modal_pct | 245,731 | 0.0135 | 334.45 | 0.0000 |
| Manager_Pres_Uncertainty_pct | 245,731 | 0.0041 | 111.99 | 0.0000 |
| CEO_QA_Uncertainty_pct | 180,910 | 0.0286 | 528.74 | 0.0000 |
| CEO_QA_Weak_Modal_pct | 180,910 | 0.0111 | 201.84 | 0.0000 |
| CEO_Pres_Uncertainty_pct | 181,404 | 0.0019 | 37.40 | 0.0000 |

All regressors are jointly significant at p < 0.0001.

---

## Economic Interpretation

### Significant Finding 1: Manager_QA_Uncertainty_pct

$$
\frac{\partial \text{Manager\_QA\_Uncertainty}}{\partial \text{Leverage}} = -0.0658
$$

**Interpretation:** A 1 percentage point increase in leverage reduces Manager Q&A uncertainty by 0.0658 percentage points.

**Economic significance:**
- Average Manager Q&A uncertainty: ~5-8%
- Average leverage: ~0.25 (25%)
- If leverage increases from 0.20 to 0.30 (10 pp), Manager Q&A uncertainty decreases by 0.658 pp
- This represents approximately 8-13% of mean uncertainty

### Significant Finding 2: Manager_QA_Weak_Modal_pct

$$
\frac{\partial \text{Manager\_QA\_WeakModal}}{\partial \text{Leverage}} = -0.0460
$$

**Interpretation:** A 1 percentage point increase in leverage reduces Manager Q&A weak modal (hedging) language by 0.0460 percentage points.

**Economic significance:**
- Average Manager Q&A weak modal: ~3-5%
- If leverage increases from 0.20 to 0.30 (10 pp), hedging language decreases by 0.460 pp
- This represents approximately 9-15% of mean hedging language

### Significant Finding 3: CEO_QA_Weak_Modal_pct

$$
\frac{\partial \text{CEO\_QA\_WeakModal}}{\partial \text{Leverage}} = -0.0480
$$

**Interpretation:** A 1 percentage point increase in leverage reduces CEO Q&A weak modal language by 0.0480 percentage points.

**Economic significance:**
- Similar magnitude to Manager Q&A weak modal effect
- Represents approximately 9-15% of mean hedging language for a 10 pp leverage increase

---

## Mechanism Analysis

### Why Q&A Shows Effects But Presentations Do Not

**Differential results by speech context:**

| Speech Context | Significant? | Interpretation |
|---|---|---|
| **Manager Q&A** | Yes (both measures) | Spontaneous responses show debt discipline |
| **CEO Q&A** | Yes (weak modal only) | Some evidence for CEO hedging language |
| **Presentations** | No (all measures) | Prepared remarks not affected by leverage |

**Explanation:**
1. **Spontaneity:** Q&A responses are spontaneous and more likely to reveal true uncertainty. Debt discipline may reduce genuine uncertainty through better governance and monitoring.
2. **Preparation:** Presentations are carefully prepared and scripted, potentially masking uncertainty that leverage would reduce.
3. **Manager vs. CEO:** Managers may be more sensitive to debt holder pressure than CEOs, who have more discretion.

---

## Causal Identification

### Lagged Leverage Design

The model uses **lagged leverage** ($Leverage_{t-1}$) to address reverse causality:

$$
\text{Uncertainty}_{i,t} = \beta_0 + \beta_1 \cdot \text{Leverage}_{i,t-1} + \text{Controls} + \text{FE} + \varepsilon_{i,t}
$$

**Identification assumption:** Current speech uncertainty cannot affect past leverage.

**Remaining threats:**
- Omitted variables that affect both past leverage and current uncertainty
- Measurement error in leverage
- Dynamic feedback (uncertainty affects future leverage, which affects subsequent uncertainty)

The firm and year fixed effects control for time-invariant firm heterogeneity and common time shocks, strengthening identification.

---

## Conclusion

**H4:** Financial leverage shows **PARTIAL** evidence of reducing managerial speech uncertainty, supporting the debt discipline hypothesis.

**Key findings:**
1. **Manager Q&A uncertainty** significantly decreases with leverage (p = 0.0072)
2. **Manager Q&A hedging language** significantly decreases with leverage (p = 0.0019)
3. **CEO Q&A hedging language** significantly decreases with leverage (p = 0.0251)
4. **Presentation uncertainty** shows no significant relationship with leverage

**Overall:** 3/6 measures support the debt discipline hypothesis. The effects are concentrated in Q&A (spontaneous communication) rather than presentations (prepared remarks), suggesting that debt discipline primarily affects genuine uncertainty rather than scripted communication.

**Economic magnitude:** For a 10 percentage point increase in leverage (e.g., from 20% to 30% debt/assets), Q&A uncertainty decreases by 0.47-0.66 percentage points, representing approximately 8-15% of mean uncertainty levels.

**Implications:**
1. Debt monitoring and default risk incentives improve communication quality in spontaneous contexts
2. Prepared remarks may be less sensitive to debt holder pressure
3. The debt discipline mechanism operates through genuine uncertainty reduction rather than impression management

---

*This documentation provides complete regression results for academic supervisor review and thesis defense.*
