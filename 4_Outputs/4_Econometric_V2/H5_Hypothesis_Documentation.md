# H5: Managerial Speech Uncertainty and Analyst Forecast Dispersion

---

## Model Specification

### Regression Equation (H5-A: Hedging Language)

$$
\text{Dispersion}_{i,t} = \beta_0 + \beta_1 \cdot \text{WeakModal}_{i,t} + \beta_2 \cdot \text{Uncertainty}_{i,t} + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypothesis H5-A:** $\beta_1 > 0$ (Weak modal predicts dispersion beyond general uncertainty)

### Regression Equation (H5-B: Uncertainty Gap)

$$
\text{Dispersion}_{i,t} = \beta_0 + \beta_1 \cdot (\text{QA\_Uncertainty}_{i,t} - \text{Pres\_Uncertainty}_{i,t}) + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypothesis H5-B:** $\beta_1 > 0$ (Uncertainty gap predicts dispersion)

**Estimation:** PanelOLS with Firm + Year FE, firm-clustered SE, Sample: 2002-2018

---

## Results

### Complete Results Table: H5-A (Hedging Language)

| Uncertainty Measure | N | R² | β₁ (SE) | t-stat | p₁ | Control Variable | β₂ (SE) | p₂ | H5-A |
|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Weak_Modal_pct | 258,560 | 0.0732 | -0.0124 (0.0053) | -2.34 | 0.9906 | Manager_QA_Uncertainty_pct | 0.0036 (0.0025) | 0.0723 | No |
| Manager_Pres_Weak_Modal_pct | 261,604 | 0.0732 | -0.0037 (0.0075) | -0.49 | 0.6891 | Manager_Pres_Uncertainty_pct | 0.0039 (0.0029) | 0.0890 | No |
| CEO_QA_Weak_Modal_pct | 191,159 | 0.0704 | -0.0051 (0.0046) | -1.11 | 0.8669 | CEO_QA_Uncertainty_pct | -0.0026 (0.0022) | 0.8841 | No |

**Note:** Significance level: p < 0.05 (one-tailed). H5-A expects β₁ > 0. β₂ is coefficient on general uncertainty control.

### Complete Results Table: H5-B (Uncertainty Gap)

| Specification | N | β₁ (SE) | t-stat | p₁ | Significant? |
|---|---|---|---|---|---|
| **primary** (Firm + Year FE) | 258,235 | -0.0025 (0.0028) | -0.89 | 0.8135 | No |
| **pooled** (No FE) | 258,235 | 0.0138 (0.0018) | 7.67 | <0.0001 | **Yes** |
| **year_only** (Year FE only) | 258,235 | 0.0090 (0.0029) | 3.10 | 0.0010 | **Yes** |
| **double_cluster** (Firm + Year FE, firm+year cluster) | 258,235 | -0.0025 (0.0028) | -0.89 | 0.8062 | No |

**Note:** Gap = (QA_Uncertainty - Pres_Uncertainty). H5-B expects β₁ > 0.

**Outcome:** H5-A NOT SUPPORTED (0/3 significant), H5-B MIXED (significant only without Firm FE)
