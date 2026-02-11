# Econometric V3: Advanced Interaction Regressions

## Purpose and Scope

This folder contains advanced econometric regression scripts for V3 hypotheses, specifically testing interaction effects between external risk (political risk, PRisk) and managerial uncertainty on investment efficiency (H2).

**Version:** V3 (Active - H2 PRisk testing complete)
**Status:** COMPLETE - H2 PRisk interaction NOT SUPPORTED
**Prerequisites:** V3 financial variables (PRisk, investment residuals)
**Outputs:** `4_Outputs/4_Econometric_V3/`

---

## Hypothesis H2 (V3): PRisk x Uncertainty -> Investment Efficiency

**Research Question:** Does the interaction between political risk and managerial uncertainty affect investment efficiency beyond their individual effects?

**Result:** H2 NOT SUPPORTED - interaction insignificant (p=0.58, wrong direction)

---

## Scripts Overview

| Script | Purpose | Key Outputs |
|--------|---------|-------------|
| `4.3_H2_PRiskUncertainty_Investment.py` | Test PRisk x Uncertainty -> Investment | Interaction regression results |

---

## Model Specification

### Primary Model

```
InvestmentResidual_{i,t+1} = beta_0
                              + beta_1 * Uncertainty_{i,t}
                              + beta_2 * PRisk_{i,t}
                              + beta_3 * (Uncertainty x PRisk)_{i,t}
                              + gamma * Controls_{i,t}
                              + Firm_FE + Year_FE
                              + epsilon_{i,t}
```

**Where:**
- `InvestmentResidual`: Biddle (2009) investment residual (DV at t+1)
- `Uncertainty`: Managerial speech uncertainty measure
- `PRisk`: Political risk (Hassan et al. measure)
- `Uncertainty x PRisk`: Interaction term (centered variables)
- `Controls`: Cash flow, size, leverage, Tobin's Q, sales growth
- `Firm_FE`: Firm fixed effects
- `Year_FE`: Year fixed effects

### Expected Signs (Hypothesis)

- `beta_1 < 0`: Uncertainty reduces investment efficiency
- `beta_2 < 0`: Political risk reduces investment efficiency
- `beta_3 < 0`: Compound uncertainty (interaction) amplifies reduction

### Actual Results

| Coefficient | Estimate | SE | p-value | Significance |
|-------------|----------|----|----|--------------|
| beta_1 (Uncertainty) | -0.0025 | 0.0008 | 0.002 | **Significant** |
| beta_2 (PRisk) | -0.0014 | 0.0006 | 0.018 | **Significant** |
| beta_3 (Interaction) | +0.0001 | 0.0006 | 0.579 | Not significant (wrong direction) |

**Conclusion:** H2 NOT SUPPORTED. The interaction is not significant, and the coefficient is positive (opposite of hypothesized direction).

---

## Key Variables

### Dependent Variable

| Variable | Description | Source |
|----------|-------------|--------|
| InvestmentResidual | Residual from Biddle first-stage regression | 3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py |

**First-Stage Specification:**
```
Investment_{i,t} ~ TobinQ_{i,t-1} + SalesGrowth_{i,t-1}
```
Run by (FF48 industry, fiscal year) cells with N >= 30.

### Independent Variables

| Variable | Description | Source |
|----------|-------------|--------|
| Uncertainty | Managerial speech uncertainty | Text analysis (V2) |
| PRisk | Political risk (Hassan et al.) | 3_Financial_V3/5.6_PRiskFY.py |
| Uncertainty_x_PRisk | Interaction term (centered) | Constructed |
| Manager_QA_Uncertainty_pct | QA uncertainty % | Text analysis |
| Manager_Pres_Uncertainty_pct | Presentation uncertainty % | Text analysis |

### Control Variables (Biddle Controls)

| Variable | Description | Source |
|----------|-------------|--------|
| CashFlow | Operating cash flow / AT | Compustat |
| Size | log(total assets) | Compustat |
| Leverage | Total debt / AT | Compustat |
| TobinQ | Market-to-book ratio | Compustat |
| SalesGrowth | Sales growth rate | Compustat |

---

## Robustness Checks

### Specifications Tested

1. **Primary:** Firm + Year FE, firm-clustered SE
2. **Industry + Year FE:** FF48 industry instead of firm FE
3. **Absolute Residual DV:** |InvestmentResidual| instead of raw residual
4. **Lagged IVs:** All IVs lagged one additional period
5. **Subsample (2006-2018):** PRisk data available from 2006

### Robustness Results

| Specification | Interaction Coef | SE | p-value | Significant? |
|---------------|-----------------|----|----|--------------|
| Primary (Firm+Year FE) | +0.0001 | 0.0006 | 0.579 | No |
| Industry+Year FE | +0.0003 | 0.0007 | 0.654 | No |
| Absolute Residual DV | +0.0004 | 0.0008 | 0.612 | No |
| Lagged IVs | +0.0002 | 0.0007 | 0.768 | No |
| Subsample 2006-2018 | +0.0001 | 0.0006 | 0.885 | No |

**Conclusion:** 0/5 robustness specifications support H2. Results are robustly null.

---

## Input/Output Mapping

### Inputs

| Source | Location | Content |
|--------|----------|---------|
| Biddle Residuals | `4_Outputs/5_Financial_V3/4.1_H2_BiddleInvestmentResidual/` | InvestmentResidual DV |
| PRisk Data | `4_Outputs/5_Financial_V3/5.6_PRiskFY/` | Political risk measures |
| Text Variables | `4_Outputs/2_Text/` | Uncertainty measures |
| Sample Manifest | `4_Outputs/1_Sample/` | GVKEY-fyear mapping |

### Outputs

```
4_Outputs/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment/
├── H2_Regression_Results.parquet    # All regression results
├── H2_PRisk_Results.md              # Human-readable report
└── stats.json                       # Regression statistics
```

---

## Sample Construction

| Metric | Value |
|--------|-------|
| Observations | 24,826 firm-years |
| Firms | 2,242 unique firms |
| Period | 2002-2018 (full sample) |
| Period (PRisk subsample) | 2006-2018 |
| Industries | FF48 classification |

**Sample Restrictions:**
- Non-missing InvestmentResidual
- Non-missing Uncertainty and PRisk measures
- Non-missing Biddle controls
- Complete cases for regression

---

## Methodology

### Variable Construction

1. **Centering:** All continuous variables mean-centered before interaction
2. **Lagged Structure:** IVs at time t predict DV at t+1
3. **Fiscal Year Alignment:** PRisk aggregated to fiscal year

### Estimation

- **Model:** Panel OLS with Firm + Year fixed effects
- **Standard Errors:** Clustered at firm level (Cameron & Miller 2015)
- **Software:** linearmodels PanelOLS
- **Missing Data:** Complete case analysis (listwise deletion)

### Model Diagnostics

- **R-squared (within):** Firm-level variation explained
- **F-statistic:** Overall model significance
- **VIF:** Variance inflation factors (checked for multicollinearity)
- **Condition Number:** Matrix stability

---

## Relationship to V1/V2

### V3 vs V1/V2

| Aspect | V1 (4_Econometric/) | V2 (4_Econometric_V2/) | V3 (this folder) |
|--------|---------------------|------------------------|------------------|
| Purpose | CEO clarity effects | H1-H9 hypothesis testing | H2 PRisk interaction |
| IV Focus | CEO Clarity | Uncertainty, Weak Modal | PRisk x Uncertainty |
| DV Focus | Liquidity, Takeover | Hypothesis-specific DVs | Investment residual |
| FE Structure | Firm+Year | Firm+Year | Firm+Year |
| Interaction | No | Uncertainty x Leverage | Uncertainty x PRisk |
| Status | STABLE | STABLE | COMPLETE |

---

## Key Findings

### Main Effect Results

Both main effects are significant (p < 0.05):
- **Uncertainty -> -Investment:** Vague managers invest less efficiently
- **PRisk -> -Investment:** High political risk reduces investment efficiency

### Interaction Result

The interaction is NOT significant:
- **Interpretation:** Political risk and managerial uncertainty affect investment through **independent channels**, not multiplicatively
- **Economic implication:** Compound uncertainty effects not present
- **Research implication:** No need to explore additional compound uncertainty hypotheses

---

## Execution Notes

### Execution

```bash
python 2_Scripts/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment.py
```

### Dependencies

- **Biddle Residuals:** Required from 3_Financial_V3
- **PRisk Data:** Required from 3_Financial_V3
- **Text Variables:** Required from V2 text processing
- **Sample Manifest:** Required for GVKEY-fyear matching

---

## References

- **Biddle (2009):** Investment residuals and accounting quality
- **Hassan et al.:** Political risk text analysis measures
- **Cameron & Miller (2015):** Clustered standard errors practice
- **Phase 53 plans:** `53-CONTEXT.md`, `53-RESEARCH.md`

---

## Contact and Replication

For replication questions:
- Phase 53 documentation: `.planning/phases/53-h2-prisk-uncertainty-investment/`
- Results output: `4_Outputs/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment/`

---

*Last updated: 2026-02-11*
*Phase: 60-code-organization*
*Version: v3.0 H2 PRisk Interaction*
