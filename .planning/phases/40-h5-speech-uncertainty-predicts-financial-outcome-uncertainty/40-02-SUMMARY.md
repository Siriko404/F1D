---
phase: 40-h5-speech-uncertainty-predicts-financial-outcome-uncertainty
plan: 02
subsystem: econometric-regression
tags: [h5-analyst-dispersion, panel-ols, weak-modal-hedging, hypothesis-testing]

# Dependency graph
requires:
  - phase: 40-01
    provides: H5_AnalystDispersion.parquet with dispersion_lead, uncertainty_gap, and controls

provides:
  - 2_Scripts/4_Econometric_V2/4.5_H5DispersionRegression.py script
  - H5_Regression_Results.parquet with all regression coefficients
  - H5_RESULTS.md with hypothesis test outcomes and interpretation
  - stats.json with hypothesis summary and diagnostics

affects:
  - phase: 40 (H5 hypothesis testing - conclusion of hypothesis)

# Tech tracking
tech-stack:
  added: []
  patterns: [panel-ols, fixed-effects, one-tailed-hypothesis-tests, incremental-contribution-test]

key-files:
  created: [2_Scripts/4_Econometric_V2/4.5_H5DispersionRegression.py]
  modified: []

key-decisions:
  - "H5-A NOT supported: Weak Modal measures do not predict dispersion in primary spec (Firm + Year FE)"
  - "H5-B mixed: Gap significant in pooled OLS but not with Firm FE (between-firm vs within-firm effect)"
  - "Interpretation: Speech-dispersion relationship driven by firm heterogeneity, not causal effect"

patterns-established:
  - "One-tailed hypothesis tests for directional predictions (beta1 > 0)"
  - "Incremental contribution test: include established effect as control"
  - "Specification comparison: primary (Firm+Year FE), pooled, year_only, double_cluster"

# Metrics
duration: 25min
completed: 2026-02-05
---

# Phase 40: Plan 02 - H5 Dispersion Regression Summary

**Panel OLS regressions testing whether hedging language (weak modal verbs) predicts analyst forecast dispersion beyond what general uncertainty words predict. Results show H5 is NOT supported in the primary specification with Firm and Year fixed effects.**

## Performance

- **Duration:** 25 min (including debugging and fixes)
- **Started:** 2026-02-05T21:42:00Z (first script creation)
- **Completed:** 2026-02-05T22:07:00Z (final results)
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments

- Created `4.5_H5DispersionRegression.py` following H1 regression script pattern
- Implemented primary model (H5-A): Weak Modal controlling for Uncertainty
- Implemented gap model (H5-B): uncertainty_gap controlling for Pres_Uncertainty
- Executed 28 regressions (6 measures x 4 specs + gap model)
- Generated comprehensive H5_RESULTS.md with interpretation framework
- Created H5_Regression_Results.parquet with all coefficients
- Fixed 3 bugs during execution (missing ID columns, JSON bool encoding, missing gap column)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create 4.5_H5DispersionRegression.py Script** - `953d5ed` (feat)
2. **Bug fixes** - `71e1aff` (fix)

## Files Created/Modified

- `2_Scripts/4_Econometric_V2/4.5_H5DispersionRegression.py` - H5 regression script with primary/gap models, one-tailed tests, 4 specification variants

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed missing gvkey/fiscal_year in regression subset**

- **Found during:** Task 2 (script execution)
- **Issue:** `complete_cols` didn't include `gvkey` and `fiscal_year`, causing panel OLS to fail with "Missing required columns" error
- **Fix:** Added `gvkey` and `fiscal_year` to `complete_cols` when creating regression subset
- **Files modified:** 2_Scripts/4_Econometric_V2/4.5_H5DispersionRegression.py (run_single_h5_regression function)
- **Committed in:** 71e1aff

**2. [Rule 1 - Bug] Fixed JSON bool serialization**

- **Found during:** Task 2 (stats.json save)
- **Issue:** NumpyEncoder didn't handle `bool` type, causing "Object of type bool is not JSON serializable"
- **Fix:** Added `if isinstance(obj, (bool, np.bool_)): return bool(obj)` to NumpyEncoder
- **Files modified:** 2_Scripts/4_Econometric_V2/4.5_H5DispersionRegression.py (save_stats function)
- **Committed in:** 71e1aff

**3. [Rule 2 - Missing Critical] Added uncertainty_gap to regression dataframe**

- **Found during:** Task 2 (gap model returning NaN coefficients)
- **Issue:** `uncertainty_gap` was not added to `strict_df` in `prepare_regression_data`, causing gap model to fail
- **Fix:** Added explicit code to add `uncertainty_gap` column after uncertainty measures loop
- **Files modified:** 2_Scripts/4_Econometric_V2/4.5_H5DispersionRegression.py (prepare_regression_data function)
- **Committed in:** 71e1aff

---

**Total deviations:** 3 auto-fixed (1 blocking, 1 bug, 1 missing critical)
**Impact on plan:** All auto-fixes necessary for correct operation. Script now runs all 28 regressions successfully.

## Key Results

### Hypothesis Test Outcomes

**H5-A (Weak Modal Hedging): NOT SUPPORTED**

| Uncertainty Measure | N | beta1 (SE) | p1 (one-tail) | Significant? |
|---------------------|---|-----------:|---------------:|:------------:|
| Manager_QA_Weak_Modal_pct (ctrl: Uncertainty) | 258,560 | -0.0124 (0.0053) | 0.991 | No |
| CEO_QA_Weak_Modal_pct (ctrl: Uncertainty) | 191,159 | -0.0051 (0.0046) | 0.867 | No |
| Manager_Pres_Weak_Modal_pct (ctrl: Uncertainty) | 261,604 | -0.0037 (0.0075) | 0.689 | No |

**H5-B (Uncertainty Gap): MIXED**

| Specification | beta1 (SE) | p1 | Significant? |
|--------------|-----------:|---:|:------------:|
| primary (Firm + Year FE) | -0.0025 (0.0028) | 0.84 | No |
| pooled (No FE) | 0.0138 (0.0018) | <0.001 | **Yes** |
| year_only (Year FE) | 0.0090 (0.0029) | 0.001 | **Yes** |

**Interpretation:** The gap effect is significant without firm FE but insignificant with firm FE,
suggesting the gap is driven by between-firm heterogeneity rather than within-firm causal effects.

### Sample Characteristics

- **Observations:** 258,560 (primary spec, complete cases)
- **Firms:** 2,027 unique firms
- **Years:** 2002-2018 (17 years)
- **R-squared (within):** 0.079 (7.9% of within-firm variation explained)

### Incremental Contribution Test

Does hedging add predictive power beyond general uncertainty?

- **Weak Modal (beta1):** -0.0124 (SE=0.0053, p=0.99) - NOT significant
- **Uncertainty control (beta2):** 0.0036 (NOT significant)
- **Conclusion:** Neither hedging nor uncertainty significantly predicts dispersion with Firm + Year FE

## Next Phase Readiness

- H5 hypothesis testing complete
- Results show null finding for H5 in primary specification
- Both hedging and uncertainty do NOT predict analyst dispersion with Firm FE
- Next steps: Consider robustness checks or proceed to literature review (Phase 41)

---

*Phase: 40-h5-speech-uncertainty-predicts-financial-outcome-uncertainty*
*Plan: 02*
*Completed: 2026-02-05*
