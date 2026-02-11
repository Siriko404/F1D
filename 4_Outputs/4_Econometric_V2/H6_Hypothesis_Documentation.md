# H6: SEC Scrutiny (CCCL) and Managerial Speech Uncertainty

---

## Model Specification

### Regression Equation

$$
\text{Uncertainty}_{i,t} = \beta_0 + \beta_{CCCL} \cdot \text{CCCL\_Exposure}_{i,t} + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**Hypotheses:**
- H6-A: $\beta_{CCCL} < 0$ (CCCL reduces uncertainty)
- H6-B: $|\beta_{CCCL}^{QA}| > |\beta_{CCCL}^{Pres}|$ (Stronger effect in Q&A)
- H6-C: $\beta_{CCCL}^{gap} < 0$ (CCCL reduces QA-Pres gap)

**Estimation:** 2SLS with shift-share instrument, Firm + Year FE, firm-clustered SE, Sample: 2006-2018

**Instrument:** shift_intensity_mkvalt_ff48_lag (primary)

---

## Results

### Complete Results Table: H6-A (CCCL Reduces Uncertainty)

| Uncertainty Measure | N | Firms | R² | β_CCCL (SE) | t-stat | p (one-tailed) | FDR q | H6-A |
|---|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 21,988 | 2,343 | 0.0002 | -0.0918 (0.0660) | -1.39 | 0.0821 | 0.4926 | No |
| Manager_QA_Weak_Modal_pct | 21,988 | 2,343 | 0.0001 | -0.0376 (0.0407) | -0.92 | 0.1779 | 0.5246 | No |
| Manager_Pres_Uncertainty_pct | 22,089 | 2,346 | 0.0000 | -0.0005 (0.1066) | -0.00 | 0.4980 | 0.5976 | No |
| CEO_QA_Uncertainty_pct | 16,784 | 2,041 | 0.0000 | -0.0113 (0.1287) | -0.09 | 0.4649 | 0.5976 | No |
| CEO_QA_Weak_Modal_pct | 16,784 | 2,041 | 0.0000 | -0.0412 (0.0794) | -0.52 | 0.3019 | 0.5976 | No |
| CEO_Pres_Uncertainty_pct | 16,655 | 2,037 | 0.0000 | 0.0688 (0.0824) | 0.84 | 0.7982 | 0.7982 | No |

**Note:** Significance level: p < 0.05 (one-tailed). FDR q is Benjamini-Hochberg corrected p-value.

### Pre-trends Test

| Variable | Beta | SE | p-value | Significant (p<0.05) |
|---|---|---|---|---|
| CCCL_{t+2} | -0.0910 | 0.0358 | 0.0118 | **Yes** |
| CCCL_{t+1} | -0.0847 | 0.0405 | 0.0378 | **Yes** |
| CCCL_t | -0.0514 | 0.0624 | 0.4079 | No |

**Pre-trends test: FAILED** - Future CCCL effects are significant

### Gap Analysis: H6-C

| Metric | β_CCCL | SE | t-stat | p (one-tailed) | H6-C |
|---|---|---|---|---|---|
| uncertainty_gap | -0.0791 | 0.1018 | -0.78 | 0.2186 | No |

**Outcome:** H6-A NOT SUPPORTED (0/6 significant), H6-B NOT SUPPORTED, H6-C NOT SUPPORTED, Pre-trends FAILED
