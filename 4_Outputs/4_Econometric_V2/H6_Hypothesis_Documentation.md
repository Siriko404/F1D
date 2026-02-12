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

## Regression Results

### Table 1: H6-A CCCL Reduces Uncertainty (Primary Specification)

| Variable | (1) | (2) | (3) | (4) | (5) | (6) |
|----------|--------|--------|--------|--------|--------|--------|
| | | | | | | | |
**Dependent Variable: Uncertainty** | Manager_QA | Manager_QA_Weak | Manager_Pres | CEO_QA | CEO_QA_Weak | CEO_Pres |
| | | | | | | | |
**CCCL Exposure (β_CCCL)** | -0.0918 | -0.0376 | -0.0005 | -0.0113 | -0.0412 | 0.0688 |
| | (0.0660) | (0.0407) | (0.1066) | (0.1287) | (0.0794) | (0.0824) |
| | -1.39 | -0.92 | -0.00 | -0.09 | -0.52 | 0.84 |
| | 0.0821 | 0.1779 | 0.4980 | 0.4649 | 0.3019 | 0.7982 |
| | No | No | No | No | No | No |
| | | | | | | | |
**Fixed Effects** | Yes | Yes | Yes | Yes | Yes | Yes |
**N** | 21,988 | 21,988 | 22,089 | 16,784 | 16,784 | 16,655 |
**R²** | 0.0002 | 0.0001 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
**Firms** | 2,343 | 2,343 | 2,346 | 2,041 | 2,041 | 2,037 |

### Table 2: H6-A CCCL Reduces Uncertainty (Alternative Instruments)

| Instrument Variant | Manager_QA | Manager_QA_Weak | Manager_Pres | CEO_QA | CEO_QA_Weak | CEO_Pres |
|---|---|---|---|---|---|---|
| FF48 × market value (primary) | -0.092 | -0.038 | -0.001 | -0.011 | -0.041 | 0.069 |
| FF48 × sales | -0.097** | -0.040 | -0.005 | -0.014 | -0.045 | 0.063 |
| FF12 × market value | -0.091 | -0.039 | -0.004 | -0.012 | -0.043 | 0.067 |
| FF12 × sales | -0.101** | -0.044 | -0.009 | -0.016 | -0.049 | 0.059 |
| SIC2 × market value | -0.096 | -0.041 | -0.004 | -0.012 | -0.044 | 0.065 |
| SIC2 × sales | -0.106** | -0.047 | -0.008 | -0.017 | -0.052 | 0.056 |

**Notes:**
- *** p < 0.01, ** p < 0.05, * p < 0.10
- Dependent variable: Uncertainty (various measures, t)
- Standard errors clustered at firm level in parentheses
- H6-A expects β_CCCL < 0: None significant in primary specification
- FDR q is Benjamini-Hochberg corrected p-value
- All specifications include firm and year fixed effects

### Table 3: Pre-trends Test

| Variable | Beta | SE | p-value | Significant (p<0.05) |
|---|---|---|---|---|
| CCCL_{t+2} | -0.0910** | (0.0358) | 0.0118 | **Yes** |
| CCCL_{t+1} | -0.0847** | (0.0405) | 0.0378 | **Yes** |
| CCCL_t | -0.0514 | (0.0624) | 0.4079 | No |

**Pre-trends test: FAILED** - Future CCCL effects are significant (violates parallel trends assumption)

### Table 4: H6-C Gap Analysis

| Metric | β_CCCL | SE | t-stat | p (one-tailed) | H6-C |
|---|---|---|---|---|
| uncertainty_gap | -0.0791 | (0.1018) | -0.78 | 0.2186 | No |

**Notes:** Gap = (QA_Uncertainty - Pres_Uncertainty). H6-C expects β_CCCL < 0.

**Outcome:** H6-A NOT SUPPORTED (0/6 significant), H6-B NOT SUPPORTED, H6-C NOT SUPPORTED, Pre-trends FAILED

---

## Control Variables

H6 uses a shift-share instrument (CCCL exposure) as the key independent variable. The model includes industry and year fixed effects but no additional control variables are included in the primary specification.

**Instrument:**
- `shift_intensity_mkvalt_ff48_lag`: CCCL exposure intensity (FF48 industry × market value, lagged t-1)

**CCCL Variants (for robustness):**
| Variant | Description |
|----------|-------------|
| shift_intensity_mkvalt_ff48_lag | FF48 × market value (primary) |
| shift_intensity_sale_ff48_lag | FF48 × sales |
| shift_intensity_mkvalt_ff12_lag | FF12 × market value |
| shift_intensity_sale_ff12_lag | FF12 × sales |
| shift_intensity_mkvalt_sic2_lag | SIC2 × market value |
| shift_intensity_sale_sic2_lag | SIC2 × sales |

**Note:** H6 uses 2SLS (Two-Stage Least Squares) with shift-share instrument for causal identification. The shift-share instrument exploits industry-level variation in CCCL exposure across states over time.
