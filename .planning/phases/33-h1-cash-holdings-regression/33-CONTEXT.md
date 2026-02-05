# Phase 33: H1 Cash Holdings Regression - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Run and validate OLS panel regressions for Hypothesis 1 (H1): Speech Uncertainty & Cash Holdings. Tests whether vagueness in earnings calls predicts higher cash holdings, and whether leverage moderates this effect. Uses existing H1 variables from Phase 29 and econometric infrastructure from Phase 32. 2SLS/IV regressions are deferred to Phase 36/37.

</domain>

<decisions>
## Implementation Decisions

### Regression Specification
- **Primary spec:** Firm + Year fixed effects with firm-clustered standard errors
- **Alternative specs to run alongside:**
  1. Pooled OLS (no fixed effects)
  2. Year FE only (no firm FE)
  3. Firm + Year FE with double-clustered SE (firm + year)
- **CEO fixed effects:** Deferred to Phase 37 (Identification Strategies) — absorbs the manager trait variation we're trying to measure
- **Centering:** Center BOTH Uncertainty and Leverage before creating interaction term (reduces VIF, coefficients interpretable at mean values)
- **Diagnostics:** STRICT — halt entire script if VIF > 5 or specification tests fail

### Uncertainty Measure Handling
- **Primary measures (run both):**
  - `Manager_QA_Uncertainty_pct` — entire management board during Q&A (broader signal)
  - `CEO_QA_Uncertainty_pct` — CEO only during Q&A (direct decision-maker signal)
- **Robustness measures (also run):**
  - `Manager_QA_Weak_Modal_pct` and `CEO_QA_Weak_Modal_pct` — alternative vagueness operationalization
  - `Manager_Pres_Uncertainty_pct` and `CEO_Pres_Uncertainty_pct` — scripted presentation section (contrast with spontaneous Q&A)
- **Total:** 6 uncertainty measures x 4 regression specs = 24 regressions
- **Variable format:** Use raw percentages (not standardized); save mean/SD in stats.json for Phase 38 economic significance calculations
- **Aggregation:** Average uncertainty across all earnings calls in the fiscal year (call-level to firm-year)

### Output and Reporting
- **Console verbosity:** Standard — announce each regression, show R²/N/significance, surface warnings
- **Output files:**
  - `H1_Regression_Results.parquet` — all coefficients, SEs, p-values, diagnostics
  - `stats.json` — variable distributions, merge rates, execution metadata
  - `H1_RESULTS.md` — summary markdown with coefficient tables and key findings
  - Per-specification `.txt` files with detailed regression output
- **Failure behavior:** Fail entire script on diagnostic failure (forces investigation before any results saved)
- **LaTeX tables:** Deferred to Phase 38 (Publication Output)

### 2SLS Instrument Usage
- **Deferred to Phase 36/37** — Phase 33 is OLS-only
- Instruments (manager's prior-firm vagueness, industry-peer average) handled in Robustness or Identification phases

### OpenCode's Discretion
- Exact file naming conventions for per-specification outputs
- Order of regressions within script execution
- Progress bar implementation details
- Handling of edge cases in call-to-year aggregation (firms with single call)

</decisions>

<specifics>
## Specific Ideas

- Manager variables (`Manager_QA_*`) capture entire management board speech; CEO variables (`CEO_QA_*`) isolate the CEO specifically — run both to test whether decision-maker signal differs from broader management signal
- Q&A section is spontaneous (less scripted) vs. presentation section (prepared remarks) — contrast is meaningful for interpretation
- Centering rationale: Without centering, coefficients are interpretable at zero leverage/uncertainty (theoretical extremes); with centering, coefficients are at typical values

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 33-h1-cash-holdings-regression*
*Context gathered: 2026-02-05*
