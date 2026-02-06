---
phase: 39-leverage-speech-discipline
plan: 02
subsystem: econometric-analysis
tags: [panel-ols, linearmodels, one-tailed-test, fixed-effects, hypothesis-testing]

# Dependency graph
requires:
  - phase: 39-01
    provides: H4_Analysis_Dataset.parquet with lagged leverage and uncertainty measures
provides:
  - H4 regression execution framework with one-tailed p-value testing
  - 6 PanelOLS regression results testing leverage -> speech uncertainty
  - H4_Coefficient_Table.tex publication-ready output
  - H4_RESULTS.md human-readable findings summary
affects: [phase-40-h5-speech-outcome-volatility, phase-41-publication-output]

# Tech tracking
tech-stack:
  added: [scipy.stats for one-tailed p-values, panel_ols regression infrastructure]
  patterns: [one-tailed hypothesis testing for directional predictions, multi-DV regression loops]

key-files:
  created:
    - 4.4_H4_LeverageDiscipline.py (regression execution functions)
    - H4_Regression_Results.parquet (regression coefficients)
    - H4_Coefficient_Table.tex (publication table)
    - H4_RESULTS.md (findings summary)
  modified:
    - 2_Scripts/4_Econometric_V2/4.4_H4_LeverageDiscipline.py (extended from data prep only)

key-decisions:
  - "Use Firm + Year FE (not Industry) consistent with H1-H3 v2.0 regressions"
  - "One-tailed p-value calculation for H4: beta1 < 0 (leverage reduces uncertainty)"
  - "Presentation control included for QA regressions to isolate channel effect"

patterns-established:
  - "Pattern: run_all_h4_regressions() executes multi-DV regression loop with conditional controls"
  - "Pattern: one_tailed_pvalue() handles directional hypothesis testing (less/greater alternatives)"
  - "Pattern: --regressions-only CLI flag enables re-running regressions without data prep"

# Metrics
duration: 9min
completed: 2026-02-05
---

# Phase 39: Leverage Disciplines Speech - H4 Regression Execution Summary

**H4 (leverage discipline hypothesis) partially supported: 3/6 uncertainty measures show significant negative relationship between lagged leverage and speech uncertainty using one-tailed tests**

## Performance

- **Duration:** 9 minutes
- **Started:** 2026-02-06T00:44:50Z
- **Completed:** 2026-02-06T00:54:28Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Implemented H4 regression execution with one-tailed p-value testing (beta < 0)
- Executed 6 PanelOLS regressions testing lagged leverage -> speech uncertainty
- Generated publication-ready LaTeX coefficient table (6 columns, one per DV)
- Documented hypothesis support: 3/6 measures significant at p < 0.05 (one-tailed)

## H4 Results Summary

| Dependent Variable | Leverage Coef | SE | p-value (1-tailed) | Significant | N |
|-------------------|---------------|-----|-------------------|-------------|---------|
| Manager_QA_Uncertainty_pct | -0.066 | 0.027 | 0.007 | **Yes** | 245,731 |
| Manager_QA_Weak_Modal_pct | -0.046 | 0.016 | 0.002 | **Yes** | 245,731 |
| CEO_QA_Weak_Modal_pct | -0.048 | 0.025 | 0.025 | **Yes** | 180,910 |
| CEO_QA_Uncertainty_pct | -0.050 | 0.041 | 0.110 | No | 180,910 |
| Manager_Pres_Uncertainty_pct | 0.023 | 0.040 | 0.714 | No | 245,731 |
| CEO_Pres_Uncertainty_pct | -0.013 | 0.045 | 0.391 | No | 181,404 |

**H4 Interpretation:** Manager speech measures (QA Uncertainty, Weak Modal) show significant discipline effects. CEO measures and presentation uncertainty do not show consistent effects.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add H4 regression execution functions** - `8e3fb84` (feat)
2. **Task 2: Execute H4 regressions and generate outputs** - `90eb7d8` (feat)

**Plan metadata:** N/A (docs committed separately if needed)

## Files Created/Modified

- `2_Scripts/4_Econometric_V2/4.4_H4_LeverageDiscipline.py` - Extended with regression execution functions
  - `one_tailed_pvalue()` - Directional hypothesis testing
  - `run_all_h4_regressions()` - Multi-DV regression loop with conditional controls
  - `save_regression_results()` - Parquet output of coefficients
  - `generate_h4_summary()` - Human-readable markdown results
  - `generate_latex_table()` - Publication-ready LaTeX table
- `4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/{timestamp}/` - Output directory
  - `H4_Regression_Results.parquet` - All coefficients, SEs, p-values
  - `H4_Coefficient_Table.tex` - 6-column publication table
  - `H4_RESULTS.md` - Findings summary
  - `stats.json` - Complete regression diagnostics

## Decisions Made

- **Firm + Year FE only:** Consistent with H1-H3 v2.0 regressions. Industry FE redundant with firm FE for most firms.
- **One-tailed p-value:** H4 requires directional test (beta < 0), not two-tailed. Implemented custom `one_tailed_pvalue()` function.
- **Presentation control for QA regressions:** Controls for presentation uncertainty when QA measures are DV to isolate the discipline channel.
- **Default clustering:** When `cov_type='clustered'` and `cluster_cols=None`, panel_ols automatically clusters at entity level.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed panel_ols parameter names**
- **Found during:** Task 2 (regression execution)
- **Issue:** Used incorrect parameter names `dependent_var` and `independent_vars` instead of `dependent` and `exog`
- **Fix:** Changed to `dependent=dv, exog=exog_vars` and removed `cluster_entity=True` (not a valid parameter)
- **Files modified:** 2_Scripts/4_Econometric_V2/4.4_H4_LeverageDiscipline.py
- **Verification:** Regressions ran successfully with correct clustering at entity level
- **Committed in:** `90eb7d8` (Task 2 commit)

**2. [Rule 3 - Blocking] Fixed start_time initialization for --regressions-only mode**
- **Found during:** Task 2 (regression execution)
- **Issue:** `start_time` undefined in --regressions-only branch, causing UnboundLocalError
- **Fix:** Added `start_time = time.time()` and `start_mem = get_process_memory_mb()` to --regressions-only branch
- **Files modified:** 2_Scripts/4_Econometric_V2/4.4_H4_LeverageDiscipline.py
- **Verification:** Script completes without error, timing stats populated correctly
- **Committed in:** `90eb7d8` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both fixes necessary for correct execution. No scope creep.

## Issues Encountered

- Initial run failed due to incorrect panel_ols parameter names. Fixed by checking function signature in shared/panel_ols.py.
- Second run failed due to missing start_time in --regressions-only branch. Fixed by adding initialization.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- H4 regression execution complete and reproducible via `--regressions-only` flag
- Results available for H5 (Speech Uncertainty -> Outcome Volatility) and final publication phases
- LaTeX table ready for inclusion in thesis/paper

---
*Phase: 39-leverage-speech-discipline*
*Plan: 02*
*Completed: 2026-02-05*
