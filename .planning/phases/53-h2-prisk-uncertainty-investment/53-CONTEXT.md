# Phase 53: H2 PRisk × Uncertainty → Investment Efficiency - Context

**Gathered:** 2026-02-06
**Status:** Ready for planning

## Phase Boundary

Test whether compound uncertainty (Hassan PRisk × Managerial Uncertainty) predicts decreased investment efficiency. Investment efficiency is measured via Biddle et al. (2009) residual methodology. The hypothesis tests within-firm variation: do firms invest less efficiently when their compound uncertainty increases?

**Scope:** This phase delivers the empirical test of H2 specified in Phase 52. It does NOT include developing new PRisk or Uncertainty measures (those exist from prior phases), nor does it extend to other investment efficiency hypotheses.

---

## Implementation Decisions

### Dependent Variable: Investment Efficiency

**Specification:** Implement correct Biddle (2009) Investment residual (NOT Phase 30's `roa_residual`)

- **First-stage regression (by industry-year):**
  ```
  Investment_i,t = β0 + β1·Tobin's_Q_i,t-1 + β2·Sales_Growth_i,t-1 + ε_i,t
  ```
  where Investment = (CapEx + R&D + Acquisitions - Asset Sales) / lagged(Assets)

- **Residual interpretation:** ε_i,t = Investment inefficiency (positive = overinvestment, negative = underinvestment)

- **Critical note:** Phase 30's `roa_residual` is INCORRECT for this purpose. Phase 30 regresses ΔROA on CapEx (tests if investment → profitability). Biddle requires regressing Investment on expected investment drivers (Q, Sales Growth). Phase 53 must implement the correct specification from scratch.

- **Industry classification:** Fama-French 48-industry classification for first-stage regressions (minimum 20 observations per industry-year cell)

### Independent Variable: Interaction Term

**Specification:** Standardized × Standardized

- **Construction:**
  1. Standardize PRisk to z-score (zero mean, unit variance)
  2. Standardize Manager_Uncertainty_pct to z-score
  3. Multiply: PRisk_std × Uncertainty_std

- **Rationale:** 52-HYPOTHESIS-SPECIFICATIONS.md specifies this approach. Mean-centering does NOT reduce multicollinearity (it's an expected mathematical property). Standardization yields interpretable coefficients (one SD change).

### Primary Regression Specification

**Model structure:**
```
InvestmentResidual_i,t = α + β1·PRisk_std×Uncertainty_std_i,t + Σγ_j·Controls_j,i,t + Firm_FE + Year_FE + ε_i,t
```

**Control variables (Biddle 2009 baseline):**
- Cash Flow (CFO / Assets)
- Firm Size (log Assets)
- Leverage (Market leverage)
- Tobin's Q
- Sales Growth

**Fixed effects:** Firm + Year FE
- Rationale: Tests within-firm variation; controls for unobserved time-invariant firm heterogeneity; standard in modern investment efficiency literature

**Standard errors:** Two-way clustered at (firm, year) per Petersen (2009)

### Sample Period

**Primary:** 2002-2018 (intersection of earnings calls and FirmLevelRisk data)

**Rationale:**
- Earnings calls: 112,968 obs (2002-2018), 2,429 firms
- PRisk: 354,518 obs (2002-2022), 13,149 firms
- Perfect overlap 2002-2018; ~30,000 firm-quarter observations expected

**Robustness:** Subsample 2006-2018 (excludes sparse early years)

### Sample Filters

**Standard finance filters:**
- Exclude financial firms (SIC 6000-6999)
- Exclude utilities (SIC 4900-4999)
- Require positive total assets
- Winsorize continuous variables at 1% and 99% by year

### Lag Structure

**Primary specification:** Contemporaneous (t)

- PRisk_t × Uncertainty_t predicts InvestmentEfficiency_t
- Rationale: Earnings calls are quarterly; investment decisions respond to current information flows; captures real-time disclosure effects

**Robustness:** One-year lag (t-1) specification to address reverse causality concerns

### Robustness Checks

1. **Alternative FE specifications:**
   - Industry FF48 + Year FE (tests between-firm effects, matches Biddle 2009 first-stage approach)
   - Compare with Firm + Year FE primary to assess within vs between variation

2. **Subsample 2006-2018:** Excludes sparse early years (2002-2005)

3. **Absolute residual DV:** Test |InvestmentResidual| (inefficiency magnitude) vs signed residual (direction)

4. **Political exposure subsamples:** Split sample by high/low political exposure industries to test heterogeneity

### Claude's Discretion

- Exact winsorization implementation details
- Minimum observation thresholds for industry-year cells in first stage
- Handling of missing control variables (listwise deletion vs imputation)
- Political exposure subsample construction method

---

## Specific Ideas

### Methodological Notes

- **Biddle (2009) verification:** Phase 30 incorrectly implements the Biddle methodology. The correct specification regresses Investment on Tobin's Q and Sales Growth, NOT ΔROA on CapEx. Phase 53 must implement this correctly.

- **Industry classification:** Use FF48 for consistency with Biddle (2009) and Phase 30 (which uses FF48 for `roa_residual`)

- **First-stage residual construction:** Requires industry-year regressions with minimum 20 observations per cell. Residuals represent deviation from expected investment given growth opportunities.

### Data Sources

- **PRisk:** `1_Inputs/FirmLevelRisk/firmquarter_2022q1.csv` (tab-separated, 354,518 obs, 2002-2022)
- **Earnings calls:** `4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet` (112,968 obs, 2002-2018)
- **Financial data:** Phase 30 scripts construct controls; may need extension for any missing variables

---

## Deferred Ideas

None — discussion stayed within Phase 53 scope.

---

*Phase: 53-h2-prisk-uncertainty-investment*
*Context gathered: 2026-02-06*
