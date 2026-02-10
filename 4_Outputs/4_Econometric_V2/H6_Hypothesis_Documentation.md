# H6: SEC Scrutiny (CCCL) and Managerial Speech Uncertainty

**Generated:** 2026-02-10
**Source Script:** `2_Scripts/4_Econometric_V2/4.6_H6CCCLRegression.py`
**Results Date:** 2026-02-05 22:58:55

---

## Hypothesis Statements

### Theoretical Motivation

**SEC Comment Letters (CCCL):** The SEC's review and comment process represents exogenous regulatory scrutiny that affects firm disclosure practices. This study uses a **shift-share instrumental variable** design to identify the causal effect of SEC scrutiny on managerial speech uncertainty.

**Mechanisms:**
1. **Direct discipline:** SEC scrutiny leads to more careful, precise communication
2. **Legal risk:** Firms face liability for vague or misleading statements under review
3. **Information improvement:** SEC feedback improves disclosure quality and reduces uncertainty

**Shift-share instrument:** CCCL exposure = Σ (peer firm exposure) × (industry shock)

This instrument exploits differential exposure to SEC scrutiny across industries and time, providing exogenous variation in CCCL treatment.

### Formal Hypotheses

**H6-A (Primary):** SEC scrutiny (CCCL exposure) reduces speech uncertainty.

$$H_6\text{-}A: \beta_{CCCL} < 0$$

**H6-B (Mechanism):** CCCL effect is stronger in spontaneous Q&A than prepared Presentation.

$$|\beta_{CCCL}^{QA}| > |\beta_{CCCL}^{Pres}|$$

**H6-C (Gap):** CCCL reduces the Q&A-Presentation uncertainty gap.

$$H_6\text{-}C: \beta_{CCCL}^{gap} < 0$$

where gap = (QA_Uncertainty - Pres_Uncertainty)

---

## Model Specification

### Regression Equation

$$
\text{Uncertainty}_{i,t} = \beta_0 + \beta_{CCCL} \cdot \text{CCCL\_Exposure}_{i,t} + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

where:
- $\text{Uncertainty}_{i,t}$ = Speech uncertainty measure (6 variants)
- $\text{CCCL\_Exposure}_{i,t}$ = Shift-share instrument (Bartik instrument)
- $\text{Controls}_{i,t}$ = Firm-level control variables
- $\alpha_i$ = Firm fixed effects
- $\delta_t$ = Year fixed effects
- $\varepsilon_{i,t}$ = Error term

### Identification Strategy

**Shift-Share Instrument (Bartik Design):**

$$
\text{CCCL\_Exposure}_{i,t} = \sum_{k} \text{Weight}_{i,k}^{base} \times \text{Shock}_{k,t}
$$

where:
- $\text{Weight}_{i,k}^{base}$ = Base-period industry employment share (firm $i$ in industry $k$)
- $\text{Shock}_{k,t}$ = CCCL shock to industry $k$ in year $t$ (national exposure growth)

**Instrument validity:**
- **Relevance:** Industry shocks predict firm-level CCCL exposure (first stage F-stat)
- **Exogeneity:** Industry shocks are exogenous to individual firms (no firm can influence national industry trends)
- **Exclusion:** Industry shocks affect uncertainty only through CCCL exposure (no direct effect)

### Estimation Method

- **Estimator:** Two-Stage Least Squares (2SLS) with shift-share instrument
- **Fixed Effects:** Firm + Year
- **Standard Errors:** Clustered at firm level
- **Sample Period:** 2006-2018 (CCCL data availability)
- **Primary instrument:** shift_intensity_mkvalt_ff48_lag

### Dependent Variables

**Six measures of speech uncertainty:**

1. Manager_QA_Uncertainty_pct
2. Manager_QA_Weak_Modal_pct
3. Manager_Pres_Uncertainty_pct
4. CEO_QA_Uncertainty_pct
5. CEO_QA_Weak_Modal_pct
6. CEO_Pres_Uncertainty_pct

---

## Primary Results: H6-A (CCCL Reduces Uncertainty)

### Complete Results Table

| Uncertainty Measure | N | Firms | Years | R² | β_CCCL (SE) | t-stat | p (one-tailed) | FDR q | H6-A |
|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 21,988 | 2,343 | 13 | 0.0002 | -0.0918 (0.0660) | -1.39 | 0.0821 | 0.4926 | No |
| Manager_QA_Weak_Modal_pct | 21,988 | 2,343 | 13 | 0.0001 | -0.0376 (0.0407) | -0.92 | 0.1779 | 0.5246 | No |
| Manager_Pres_Uncertainty_pct | 22,089 | 2,346 | 13 | 0.0000 | -0.0005 (0.1066) | -0.00 | 0.4980 | 0.5976 | No |
| CEO_QA_Uncertainty_pct | 16,784 | 2,041 | 13 | 0.0000 | -0.0113 (0.1287) | -0.09 | 0.4649 | 0.5976 | No |
| CEO_QA_Weak_Modal_pct | 16,784 | 2,041 | 13 | 0.0000 | -0.0412 (0.0794) | -0.52 | 0.3019 | 0.5976 | No |
| CEO_Pres_Uncertainty_pct | 16,655 | 2,037 | 13 | 0.0000 | 0.0688 (0.0824) | 0.84 | 0.7982 | 0.7982 | No |

**Note:** Significance level: p < 0.05 (one-tailed). H6-A expects β_CCCL < 0. FDR q is Benjamini-Hochberg corrected p-value for multiple testing. None of the coefficients are statistically significant at conventional levels.

---

## FDR Correction Results

### Benjamini-Hochberg False Discovery Rate Correction

Multiple testing correction across 7 primary tests (6 uncertainty measures + 1 gap measure):

| Measure | p (original) | p (FDR) | FDR Sig? |
|---|---|---|---|
| Manager_QA_Uncertainty_pct | 0.0821 | 0.4926 | No |
| Manager_QA_Weak_Modal_pct | 0.1779 | 0.5246 | No |
| Manager_Pres_Uncertainty_pct | 0.4980 | 0.5976 | No |
| CEO_QA_Uncertainty_pct | 0.4649 | 0.5976 | No |
| CEO_QA_Weak_Modal_pct | 0.3019 | 0.5976 | No |
| CEO_Pres_Uncertainty_pct | 0.7982 | 0.7982 | No |
| uncertainty_gap | 0.2186 | 0.5246 | No |

**FDR Summary:**
- **Significant after FDR correction (q < 0.05):** 0/7
- **Significant uncorrected (p < 0.05):** 0/7
- **Lowest uncorrected p-value:** 0.0821 (Manager_QA_Uncertainty_pct)

---

## Hypothesis Test Outcomes

### H6-A: β_CCCL < 0 (CCCL Reduces Uncertainty)

**Result: NOT SUPPORTED**

- **Significant measures (uncorrected p < 0.05):** 0/6
- **Significant measures (FDR-corrected q < 0.05):** 0/6
- **Direction:** 5/6 negative (as hypothesized), 1/6 positive
- **Lowest p-value:** 0.0821 (not significant at 5% level)

**Interpretation:** No evidence that SEC scrutiny (CCCL exposure) significantly reduces managerial speech uncertainty. The direction is generally negative (5/6 measures), but none of the effects are statistically significant.

---

## Pre-trends Test (Falsification)

### Test for Anticipatory Effects

**Identification assumption:** Future CCCL exposure should not predict current uncertainty (no anticipatory effects).

| Variable | Beta | SE | p-value | Significant (p<0.05) |
|---|---|---|---|---|
| CCCL_{t+2} | -0.0910 | 0.0358 | 0.0118 | **Yes** |
| CCCL_{t+1} | -0.0847 | 0.0405 | 0.0378 | **Yes** |
| CCCL_t | -0.0514 | 0.0624 | 0.4079 | No |

**Pre-trends test: FAILED**

**Problem:** Future CCCL effects are significant, indicating:
1. **Anticipatory effects:** Firms may reduce uncertainty in anticipation of future SEC scrutiny
2. **Pre-trends violation:** Parallel trends assumption may not hold
3. **Omitted variable bias:** Time-varying confounders correlated with both future CCCL and current uncertainty

**Implication:** The causal interpretation of CCCL effects is weakened by the pre-trends violation. The significant future effects suggest the instrument may not satisfy the exclusion restriction.

---

## Mechanism Test: H6-B

### CCCL Effect Stronger in Q&A than Presentation

| QA Measure | QA β_CCCL | Pres Measure | Pres β_CCCL | |QA| > |Pres|? |
|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | -0.0918 | Manager_Pres_Uncertainty_pct | -0.0005 | Yes |
| CEO_QA_Uncertainty_pct | -0.0113 | CEO_Pres_Uncertainty_pct | 0.0688 | No |

**H6-B: NOT SUPPORTED**

**Result:** Only 1/2 QA effects larger in magnitude than presentation effects. Neither effect is statistically significant, so the comparison is not meaningful.

---

## Gap Analysis: H6-C

### CCCL Effect on Uncertainty Gap

**Model:** Uncertainty Gap = (QA_Uncertainty - Pres_Uncertainty)

| Metric | Result |
|---|---|
| β_CCCL | -0.0791 (SE = 0.1018) |
| t-stat | -0.78 |
| p-value (one-tailed) | 0.2186 |
| H6-C supported | No |

**Interpretation:** CCCL does not significantly reduce the Q&A-Presentation uncertainty gap. The negative coefficient is in the hypothesized direction but not statistically significant.

---

## Sample Statistics

| Statistic | Value |
|---|---|
| **Total Observations** | 22,089 (maximum) |
| **Firms** | 2,346 |
| **Sample Period** | 2006-2018 (13 years) |
| **R² Range** | 0.0000 - 0.0002 |
| **Observations per Measure** | 16,655 - 22,089 |

### Sample Composition

**Manager measures:** 21,988 - 22,089 observations
**CEO measures:** 16,655 - 16,784 observations

### Model Fit

The very low R² values (0.0000 - 0.0002) indicate that:
- CCCL exposure explains virtually none of the uncertainty variation
- Most variation is driven by unobserved factors
- The shift-share instrument may have limited relevance

---

## Robustness Checks

### Instrument Variants Tested

| Instrument | Description |
|---|---|
| shift_intensity_mkvalt_ff48_lag | Market value, 48 industries, lagged (PRIMARY) |
| shift_intensity_sale_ff48_lag | Sales, 48 industries, lagged |
| shift_intensity_mkvalt_ff12_lag | Market value, 12 industries, lagged |
| shift_intensity_sale_ff12_lag | Sales, 12 industries, lagged |
| shift_intensity_mkvalt_sic2_lag | Market value, SIC-2, lagged |
| shift_intensity_sale_sic2_lag | Sales, SIC-2, lagged |

### Specification Counts

| Specification | Regressions Run |
|---|---|
| double_cluster | 7 |
| firm_only | 7 |
| pooled | 7 |
| primary | 12 |
| robustness_instrument | 6 |

**Total:** 39 regression specifications tested

### Robustness Summary

Across all instrument variants and specifications, no CCCL effects are statistically significant at conventional levels after FDR correction. The null finding is robust to:
- Alternative industry definitions (FF12, FF48, SIC-2)
- Alternative weighting schemes (market value vs. sales)
- Alternative clustering strategies (firm vs. firm+year)
- Fixed effects variations (Firm+Year vs. Year-only vs. pooled)

---

## Economic Interpretation

### Null Finding

For **Manager_QA_Uncertainty_pct**, β_CCCL = -0.0918 (SE = 0.0660, p = 0.0821):

$$
\frac{\partial \text{Uncertainty}}{\partial \text{CCCL\_Exposure}} = -0.0918
$$

**Interpretation:**
- A 1 unit increase in CCCL exposure decreases uncertainty by 0.0918 percentage points
- Effect is not statistically significant (p = 0.0821)
- Even if significant, economic magnitude is small (< 0.1 pp change)

**Context:**
- Average speech uncertainty: 5-8%
- CCCL exposure standard deviation: ~1-2 units
- Maximum plausible effect: < 0.2 pp change in uncertainty (< 4% of mean)

---

## Identification Concerns

### Pre-trends Violation

The significant future CCCL effects (CCCL_{t+1} and CCCL_{t+2}) indicate:

1. **Anticipatory behavior:** Firms may reduce uncertainty when they expect future SEC scrutiny
2. **Time-varying confounders:** Factors correlated with both future CCCL exposure and current uncertainty
3. **Parallel trends violation:** The parallel trends assumption required for shift-share identification may not hold

**Implication:** The causal interpretation of CCCL effects is compromised. The null finding cannot be confidently attributed to a lack of causal effect—it may reflect:
- Weak instrument (low relevance)
- Violation of exclusion restriction (direct effects of industry shocks)
- Anticipatory effects contaminating the estimates

---

## Conclusion

**H6-A (CCCL reduces uncertainty): NOT SUPPORTED**

No evidence that SEC scrutiny (CCCL exposure) significantly reduces managerial speech uncertainty. None of the 6 uncertainty measures show statistically significant effects at the 5% level (uncorrected or FDR-corrected). The direction is generally negative (5/6 measures), suggesting possible effects that are not precisely estimated.

**H6-B (Stronger effect in Q&A): NOT SUPPORTED**

Only 1/2 comparisons show larger Q&A effects than presentation effects. Neither effect is significant, so the comparison is not meaningful.

**H6-C (CCCL reduces gap): NOT SUPPORTED**

CCCL does not significantly reduce the Q&A-Presentation uncertainty gap (p = 0.2186).

**Pre-trends test: FAILED**

Future CCCL exposure significantly predicts current uncertainty, indicating anticipatory effects or pre-trends violation. This weakens the causal interpretation of the shift-share design.

**Overall:** The shift-share IV design does not provide reliable evidence on the causal effect of SEC scrutiny on speech uncertainty. The null findings may reflect:
1. Genuinely small or zero causal effects
2. Weak instrument (low first-stage F-stats)
3. Violation of identification assumptions (exclusion restriction, parallel trends)
4. Anticipatory behavior by firms

**Implications:**
1. Shift-share designs require careful validation of identification assumptions
2. Pre-trends tests are essential for causal interpretation
3. SEC scrutiny may not affect managerial speech uncertainty in measurable ways, or the effects are too small to detect with available power
4. Alternative identification strategies may be needed to study SEC disclosure regulation effects

**Limitations:**
1. Short sample period (2006-2018, 13 years) limits power
2. Low R² values suggest limited explanatory power
3. Pre-trends violation compromises causal interpretation
4. Multiple testing with few significant effects raises concerns about spurious findings

---

*This documentation provides complete regression results for academic supervisor review and thesis defense.*
