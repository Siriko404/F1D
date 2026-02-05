# Phase 34: H2 Investment Efficiency Regression - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Run and validate OLS/2SLS regressions for H2 (Speech Uncertainty & Investment Efficiency). Merge speech uncertainty measures from Step 2 with H2 variables (from Phase 30), run panel regressions with firm/year/industry fixed effects, clustered standard errors, and interaction terms. Generate coefficient tables with expected signs: beta1 < 0 (vagueness lowers efficiency), beta3 > 0 (leverage improves efficiency). Test both primary DV (Efficiency Score) and alternative DV (ROA residual).

</domain>

<decisions>
## Implementation Decisions

### Regression Structure
- Follow exact pattern from Phase 33 (H1 Cash Holdings Regression)
- 24 regressions per DV: 6 uncertainty measures × 4 specifications
- Two dependent variables tested independently: efficiency_score and roa_residual
- Separate output files/tables for each DV with clear labeling

### Model Specifications
- **Primary spec**: Firm + Year FE, clustered SE at firm level (same as H1)
- **Pooled spec**: No fixed effects, heteroskedasticity-robust SE
- **Year-only spec**: Year FE only, clustered SE at firm level
- **Double-cluster spec**: Firm + Year FE, double-clustered SE (firm + year)
- Use existing panel_ols.py infrastructure (already fixed for double-clustering)

### Hypothesis Testing
- One-tailed tests for directional hypotheses
- H2a: beta1 < 0 (vagueness decreases investment efficiency)
- H2b: beta3 > 0 (leverage attenuates negative effect)
- Significance levels: *** p<0.01, ** p<0.05, * p<0.10
- Report both coefficient significance and economic significance

### Output Format
- stats.json with all regression diagnostics (same structure as H1)
- LaTeX tables via existing latex_tables.py infrastructure
- Console output with significance stars
- Parquet file with all regression results
- H2_RESULTS.md summary report

### Variables
- **DV 1**: efficiency_score (1 - % inefficient years over 5-year window)
- **DV 2**: roa_residual (from Biddle et al. 2009 methodology, cross-sectional regression residual)
- **Main IVs**: 6 speech uncertainty measures (from Step 2 outputs)
- **Moderator**: firm_leverage (already mean-centered for interaction)
- **Controls**: tobins_q, cf_volatility, industry_capex_intensity, analyst_dispersion, firm_size, roa, fcf, earnings_volatility
- **Interaction**: Uncertainty × Leverage (mean-centered before multiplication)

### Sample Handling
- Use H2_InvestmentEfficiency.parquet from Phase 30 as base
- Merge with uncertainty measures on firm_key/year
- Handle missing values via listwise deletion (same as H1)
- Report sample sizes for each regression

### Diagnostics
- VIF < 5 threshold for multicollinearity
- Condition number check (relaxed threshold 1000 for FE models)
- First-stage F > 10 for 2SLS validity
- Hansen J overidentification test for IV specifications

### OpenCode's Discretion
- Exact console output formatting (follow H1 pattern)
- Table column ordering and labeling
- Additional diagnostic plots (if any)
- Error message wording
- File naming conventions within established pattern

</decisions>

<specifics>
## Specific Ideas

- Mirror the H1 regression script structure exactly: 4.1_H1CashHoldingsRegression.py → 4.2_H2InvestmentEfficiencyRegression.py
- H1 results showed weak support for moderation hypothesis; expect similar pattern for H2
- Use existing econometric infrastructure from Phase 32 (panel_ols.py, iv_regression.py, etc.)
- Both DVs should be tested in the same script (efficiency_score primary, roa_residual robustness)

</specifics>

<deferred>
## Deferred Ideas

None — Phase 34 follows established H1 pattern without scope expansion

</deferred>

---

*Phase: 34-h2-investment-efficiency-regression*
*Context gathered: 2026-02-05*
