# H2: Managerial Speech Uncertainty and Investment Efficiency

---

## Model Specification

### Regression Equation

$$
\text{InvestmentResidual}_{i,t} = \beta_0 + \beta_1 \cdot \text{Uncertainty}_{i,t} + \beta_2 \cdot \text{Leverage}_{i,t} + \beta_3 \cdot (\text{Uncertainty}_{i,t} \times \text{Leverage}_{i,t}) + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypotheses:**
- H2a: $\beta_1 < 0$ (Uncertainty → Lower Investment Efficiency)
- H2b: $\beta_3 > 0$ (Leverage attenuates negative relationship)

**Estimation:** PanelOLS with Firm + Year FE, firm-clustered SE, Sample: 2002-2018

**Dependent Variables:** (1) efficiency_score (Biddle residuals), (2) roa_residual

---

## Results

### Complete Results Table: efficiency_score

| Uncertainty Measure | N | R² | β₁ (SE) | t-stat | p₁ | β₃ (SE) | t-stat | p₃ | H2a | H2b |
|---|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 341,149 | 0.0020 | 0.0235 (0.0141) | 1.67 | 0.9527 | 0.0145 (0.0699) | 0.21 | 0.4181 | No | No |
| CEO_QA_Uncertainty_pct | 260,122 | 0.0023 | 0.0065 (0.0118) | 0.55 | 0.7082 | 0.0089 (0.0597) | 0.15 | 0.4404 | No | No |
| Manager_QA_Weak_Modal_pct | 341,149 | 0.0019 | 0.0189 (0.0191) | 0.99 | 0.8378 | 0.0623 (0.1181) | 0.53 | 0.2990 | No | No |
| CEO_QA_Weak_Modal_pct | 260,122 | 0.0023 | 0.0085 (0.0175) | 0.49 | 0.6861 | 0.0178 (0.0877) | 0.20 | 0.4195 | No | No |
| Manager_Pres_Uncertainty_pct | 342,421 | 0.0023 | 0.0271 (0.0141) | 1.92 | 0.9724 | -0.0864 (0.0619) | -1.40 | 0.9185 | No | No |
| CEO_Pres_Uncertainty_pct | 256,999 | 0.0024 | 0.0034 (0.0124) | 0.27 | 0.6086 | -0.0123 (0.0541) | -0.23 | 0.5902 | No | No |

### Complete Results Table: roa_residual

| Uncertainty Measure | N | R² | β₁ (SE) | t-stat | p₁ | β₃ (SE) | t-stat | p₃ | H2a | H2b |
|---|---|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 340,864 | 0.0004 | -0.0110 (0.0987) | -0.11 | 0.4557 | 0.2430 (0.5458) | 0.45 | 0.3281 | No | No |
| CEO_QA_Uncertainty_pct | 259,879 | 0.0004 | -0.0199 (0.1008) | -0.20 | 0.4217 | 0.3791 (0.4771) | 0.79 | 0.2134 | No | No |
| Manager_QA_Weak_Modal_pct | 340,864 | 0.0004 | -0.0459 (0.1248) | -0.37 | 0.3565 | 0.1471 (0.8392) | 0.18 | 0.4304 | No | No |
| CEO_QA_Weak_Modal_pct | 259,879 | 0.0004 | -0.1087 (0.1346) | -0.81 | 0.2096 | 0.2019 (0.7252) | 0.28 | 0.3903 | No | No |
| Manager_Pres_Uncertainty_pct | 342,136 | 0.0005 | 0.0685 (0.1003) | 0.68 | 0.7527 | -0.9259 (0.6322) | -1.46 | 0.9285 | No | No |
| CEO_Pres_Uncertainty_pct | 256,756 | 0.0005 | 0.0437 (0.1328) | 0.33 | 0.6291 | -0.8557 (0.5776) | -1.48 | 0.9307 | No | No |

**Note:** Significance level: p < 0.05 (one-tailed). Bold indicates statistical significance.

**Outcome:** H2a NOT SUPPORTED (0/12 significant), H2b NOT SUPPORTED (0/12 significant)
