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
