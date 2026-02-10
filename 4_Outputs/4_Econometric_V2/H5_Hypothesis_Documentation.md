# H5: Managerial Speech Uncertainty and Analyst Forecast Dispersion

**Generated:** 2026-02-10
**Source Script:** `2_Scripts/4_Econometric_V2/4.5_H5DispersionRegression.py`
**Results Date:** 2026-02-05 21:49:06

---

## Hypothesis Statements

### Theoretical Motivation

Managerial speech uncertainty may affect analyst forecast disagreement through two distinct mechanisms:

#### H5-A: Hedging Language Hypothesis

**Weak modal verbs** (may, might, could, possibly) represent hedging language distinct from general uncertainty words. If hedging has incremental predictive power:

- Analysts may interpret hedging as intentional ambiguity signaling
- Hedging language may capture managerial caution beyond general uncertainty
- Hedging should predict analyst dispersion even after controlling for general uncertainty

**Formal hypothesis:**

$$H_5\text{-}A: \beta_1 > 0$$

where $\beta_1$ is the coefficient on weak modal language, controlling for general uncertainty.

#### H5-B: Uncertainty Gap Hypothesis

The **gap between spontaneous and scripted speech** (Q&A uncertainty minus Presentation uncertainty) captures:

- Unrehearsed vs. rehearsed communication differences
- Spontaneous revelation of information vs. prepared messaging
- Managerial uncertainty that emerges under questioning

A larger gap (more spontaneous uncertainty relative to prepared remarks) should increase analyst disagreement.

**Formal hypothesis:**

$$H_5\text{-}B: \beta_1 > 0$$

where $\beta_1$ is the coefficient on the uncertainty gap (QA_Uncertainty - Pres_Uncertainty).

---

## Model Specification

### Regression Equation (H5-A: Hedging Language)

$$
\text{Dispersion}_{i,t} = \beta_0 + \beta_1 \cdot \text{WeakModal}_{i,t} + \beta_2 \cdot \text{Uncertainty}_{i,t} + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

where:
- $\text{Dispersion}_{i,t}$ = Analyst forecast dispersion (standard deviation of forecasts scaled by stock price)
- $\text{WeakModal}_{i,t}$ = Weak modal verb percentage (hedging language)
- $\text{Uncertainty}_{i,t}$ = General uncertainty percentage (control variable)
- $\text{Controls}_{i,t}$ = Established determinants of dispersion (prior dispersion, earnings surprise, analyst coverage, firm size)
- $\alpha_i$ = Firm fixed effects
- $\delta_t$ = Year fixed effects
- $\varepsilon_{i,t}$ = Error term

### Regression Equation (H5-B: Uncertainty Gap)

$$
\text{Dispersion}_{i,t} = \beta_0 + \beta_1 \cdot (\text{QA\_Uncertainty}_{i,t} - \text{Pres\_Uncertainty}_{i,t}) + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

### Estimation Method

- **Estimator:** PanelOLS (Fixed Effects)
- **Fixed Effects:** Firm + Year
- **Standard Errors:** Clustered at firm level
- **Sample Period:** 2002-2018

### Dependent Variable

**Analyst Forecast Dispersion:** Standard deviation of analyst earnings forecasts scaled by stock price. Higher values indicate greater disagreement among analysts about future earnings.

---

## Primary Results: H5-A (Hedging Language)

### Complete Results Table

| Uncertainty Measure | N | R² | β₁ (SE) | t-stat | p₁ (one-tailed) | Control Variable | β₂ (SE) | p₂ (one-tailed) | H5-A |
|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Weak_Modal_pct | 258,560 | 0.0732 | -0.0124 (0.0053) | -2.34 | 0.9906 | Manager_QA_Uncertainty_pct | 0.0036 (0.0025) | 0.0723 | No |
| Manager_Pres_Weak_Modal_pct | 261,604 | 0.0732 | -0.0037 (0.0075) | -0.49 | 0.6891 | Manager_Pres_Uncertainty_pct | 0.0039 (0.0029) | 0.0890 | No |
| CEO_QA_Weak_Modal_pct | 191,159 | 0.0704 | -0.0051 (0.0046) | -1.11 | 0.8669 | CEO_QA_Uncertainty_pct | -0.0026 (0.0022) | 0.8841 | No |

**Note:** Significance level: p < 0.05 (one-tailed). H5-A expects β₁ > 0. β₂ is the coefficient on the general uncertainty control. t-stats are calculated as coefficient/SE.

### Interpretation Framework

| Result Pattern | Interpretation | Contribution |
|---|---|---|
| Weak Modal sig, Uncertainty sig | Hedging adds INCREMENTAL info | Primary novel finding |
| Weak Modal insig, Uncertainty sig | Hedging doesn't add beyond uncertainty | Confirms uncertainty as key driver |
| Both insig (our result) | Speech doesn't predict dispersion with Firm FE | Null finding |

**Our finding:** Both weak modal language and general uncertainty are insignificant in the primary specification (Firm + Year FE). This differs from pooled OLS where uncertainty is sometimes significant, suggesting firm fixed effects capture time-invariant heterogeneity that drives the speech-dispersion relationship.

---

## Primary Results: H5-B (Uncertainty Gap)

### Primary Specification (Firm + Year FE)

| Metric | Uncertainty Gap Measure | N | R² | β₁ (SE) | t-stat | p₁ (one-tailed) | H5-B |
|---|---|---|---|---|---|---|---|
| Manager Gap | Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct | 258,235 | 0.0731 | -0.0025 (0.0028) | -0.89 | 0.8135 | No |

**Note:** H5-B expects β₁ > 0. The gap is defined as (QA_Uncertainty - Pres_Uncertainty). Negative coefficient suggests higher gap reduces dispersion, opposite of hypothesis.

### Specification Comparison for Gap Model

| Specification | N | β₁ (SE) | t-stat | p₁ (one-tailed) | Significant? |
|---|---|---|---|---|---|
| **primary** (Firm + Year FE) | 258,235 | -0.0025 (0.0028) | -0.89 | 0.8135 | No |
| **pooled** (No FE) | 258,235 | 0.0138 (0.0018) | 7.67 | <0.0001 | **Yes** |
| **year_only** (Year FE only) | 258,235 | 0.0090 (0.0029) | 3.10 | 0.0010 | **Yes** |
| **double_cluster** (Firm + Year FE, firm+year cluster) | 258,235 | -0.0025 (0.0028) | -0.89 | 0.8062 | No |

**Key insight:** The uncertainty gap effect is significant in specifications **without firm fixed effects** but becomes insignificant when firm FE are included. This suggests the gap effect is driven by time-invariant firm heterogeneity (between-firm differences) rather than within-firm causal effects.

---

## Hypothesis Test Outcomes

### H5-A: β₁ > 0 (Weak Modal Predicts Dispersion Beyond Uncertainty)

**Result: NOT SUPPORTED**

- **Significant measures:** 0/3
- **Direction:** 3/3 negative (opposite of hypothesis)
- **Control variable (Uncertainty):** Also insignificant (3/3 measures)
- **All p-values:** > 0.07

**Interpretation:** In the primary specification (Firm + Year FE), neither weak modal language nor general uncertainty significantly predict analyst forecast dispersion. The negative weak modal coefficients contradict the hypothesis.

### H5-B: β₁ > 0 (Uncertainty Gap Predicts Dispersion)

**Result: MIXED**

- **Primary spec (Firm + Year FE):** NOT SUPPORTED
  - β₁ = -0.0025 (SE = 0.0028)
  - p = 0.8135 (one-tailed)
  - Negative coefficient (opposite direction)

- **Pooled spec (No FE):** SUPPORTED
  - β₁ = 0.0138 (SE = 0.0018)
  - p < 0.0001
  - Positive and significant

- **Year-only spec (Year FE only):** SUPPORTED
  - β₁ = 0.0090 (SE = 0.0029)
  - p = 0.0010

**Interpretation:** The gap effect is significant only when firm fixed effects are omitted. With firm FE, the gap effect disappears and becomes slightly negative. This suggests:
- Between-firm differences drive the gap-dispersion relationship
- Within-firm changes in the gap do not affect dispersion
- Firm fixed effects absorb the variation that makes the gap appear significant

---

## Sample Statistics

| Statistic | Value |
|---|---|
| **Total Observations** | 261,604 (maximum) |
| **Firms** | 2,027 unique firms |
| **Sample Period** | 2002-2018 (17 years) |
| **Quarters** | 4 per year |
| **R² Range** | 0.0704 - 0.0732 |
| **R² (within)** | 0.079 (7.9% of within-firm variation explained) |

### Sample Composition

**Manager measures:**
- QA: 258,560 observations
- Presentation: 261,604 observations
- Gap: 258,235 observations

**CEO measures:**
- QA: 191,159 observations
- Presentation: (not tested for hedging)

### Model Fit

The R² values (0.0704 - 0.0732) indicate that:
- Speech uncertainty and controls explain 7-8% of dispersion variation
- Within-firm R² = 7.9% (substantial for within-firm variation)
- Most dispersion variation is driven by unobserved factors or time-invariant firm heterogeneity

---

## Robustness Checks

### Specification Comparison

| Specification | Entity FE | Time FE | Cluster SE | Weak Modal Sig? | Gap Sig? |
|---|---|---|---|---|---|
| **primary** | Yes (Firm) | Yes (Year) | Firm | No (3/3) | No |
| **pooled** | No | No | Firm | No | Yes |
| **year_only** | No | Yes (Year) | Firm | No | Yes |
| **double_cluster** | Yes (Firm) | Yes (Year) | Firm + Year | No (3/3) | No |

### Robustness Summary

**H5-A (Weak Modal):** Consistently insignificant across all specifications with Firm FE. Never significant in the hypothesized direction.

**H5-B (Gap):** Significant only in specifications without Firm FE. Becomes insignificant with Firm FE included. This pattern suggests the gap effect is driven by between-firm heterogeneity, not within-firm causal effects.

### VIF and Multicollinearity

VIF checks were performed. No high multicollinearity (VIF > 5) was detected between Weak Modal and Uncertainty measures. This suggests the results are not driven by multicollinearity concerns.

---

## Economic Interpretation

### Null Finding: Weak Modal Language

For **Manager_QA_Weak_Modal_pct**, β₁ = -0.0124 (SE = 0.0053, p = 0.9906):

$$
\frac{\partial \text{Dispersion}}{\partial \text{WeakModal}} = -0.0124
$$

**Interpretation:**
- The negative coefficient contradicts H5-A (predicted positive)
- A 1 percentage point increase in weak modal language decreases dispersion by 0.0124
- Effect is not statistically significant
- The sign suggests analysts may view hedging as cautious, not ambiguous

### Mixed Finding: Uncertainty Gap

**Primary specification (Firm + Year FE):**
- β₁ = -0.0025 (SE = 0.0028, p = 0.8135)
- Negative and insignificant

**Pooled specification (No FE):**
- β₁ = 0.0138 (SE = 0.0018, p < 0.0001)
- Positive and significant

**Interpretation:**
- Firms with persistently higher Q&A uncertainty relative to presentation uncertainty have higher analyst dispersion (between-firm effect)
- Within-firm changes in the gap do not affect dispersion (within-firm effect)
- Firm fixed effects absorb the gap variation, indicating it's a firm trait, not a causal driver

---

## Mechanism Analysis

### Why Firm Fixed Effects Matter

**The gap effect pattern across specifications:**

| Specification | Gap Effect | Interpretation |
|---|---|---|
| Pooled OLS (No FE) | Significant (β = 0.0138) | Between-firm differences drive gap-dispersion relationship |
| Year FE only | Significant (β = 0.0090) | Time shocks don't eliminate between-firm effect |
| Firm + Year FE | Insignificant (β = -0.0025) | Within-firm gap changes don't affect dispersion |

**Explanation:**
1. **Between-firm mechanism:** Some firms have systematically higher Q&A uncertainty relative to presentation uncertainty (communication style). These firms also have higher analyst dispersion (analyst following, firm complexity, etc.).
2. **Within-firm mechanism:** When a firm's gap increases over time, dispersion does not increase. The gap is not a causal driver of dispersion.
3. **Firm FE role:** Firm fixed effects control for time-invariant firm traits (communication style, business model, etc.). Once these are controlled, the gap effect disappears.

### Why Speech Doesn't Predict Dispersion with Firm FE

**Potential explanations:**
1. **Analyst inattention:** Analysts may not process linguistic differences in real-time
2. **Alternative information sources:** Analysts rely more on financial statements, guidance, and private channels than public speech
3. **Firm communication strategy:** Firms may use speech strategically, and analysts adjust for this
4. **Measurement:** Speech measures may not capture the uncertainty dimensions analysts care about

---

## Conclusion

**H5-A (Hedging Language): NOT SUPPORTED**

Weak modal language does **NOT** predict analyst forecast dispersion beyond general uncertainty. None of the 3 weak modal measures are significant in the primary specification. The coefficients are negative (opposite of hypothesized direction), suggesting analysts may not interpret hedging as increasing ambiguity.

**H5-B (Uncertainty Gap): NOT SUPPORTED in primary specification**

The uncertainty gap (Q&A - Presentation) is significant in pooled OLS but becomes insignificant with firm fixed effects. This indicates:
- **Between-firm effect:** Firms with persistently higher gaps have higher dispersion (correlation, not causation)
- **Within-firm effect:** Changes in the gap over time do not affect dispersion (no causal effect)

**Overall:** In the most rigorous specification (Firm + Year FE), neither hedging language nor the spontaneous-scripted uncertainty gap significantly predicts analyst forecast dispersion. This suggests:
1. Speech measures may not capture the information dimensions analysts use to form forecasts
2. Firm fixed effects absorb the relevant variation (between-firm differences in communication style)
3. Within-firm changes in speech do not meaningfully affect analyst disagreement

**Implications:**
1. Analysts appear to process different types of speech uncertainty similarly (hedging vs. general uncertainty)
2. The spontaneous-scripted distinction matters less for analysts than firm-level communication traits
3. Research on speech and analyst forecasts should carefully consider firm fixed effects to distinguish between-firm correlation from within-firm causation

---

*This documentation provides complete regression results for academic supervisor review and thesis defense.*
