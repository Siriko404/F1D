---
phase: 42-h6-sec-scrutiny-cccl-reduces-manager-speech-uncertainty
plan: 02
subsystem: econometrics
tags: [panel-ols, fixed-effects, fdr-correction, shift-share-instrument, cccl]

# Dependency graph
requires:
  - phase: 42-01
    provides: H6_CCCL_Speech.parquet with CCCL instruments, lagged exposure, and speech uncertainty measures
provides:
  - Panel OLS regression results testing CCCL exposure effects on 6 speech uncertainty measures
  - FDR-corrected hypothesis tests (Benjamini-Hochberg across 7 measures)
  - Pre-trends falsification test using future CCCL leads
  - Mechanism test comparing Q&A vs Presentation effects
  - Gap analysis testing CCCL effect on uncertainty gap
  - Robustness checks across 6 CCCL instrument variants
affects: [43, discussion-section]

# Tech tracking
tech-stack:
  added: []
  patterns: [panel-ols-with-firm-year-fe, fdr-bh-correction, pre-trends-falsification]

key-files:
  created:
    - 2_Scripts/4_Econometric_V2/4.6_H6CCCLRegression.py
    - 4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/{timestamp}/H6_Regression_Results.parquet
    - 4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/{timestamp}/H6_RESULTS.md
    - 4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/{timestamp}/stats.json
    - 3_Logs/4_Econometric_V2/4.6_H6CCCLRegression/{timestamp}_H6.log
  modified: []

key-decisions:
  - "Pre-trends test reveals significant future CCCL effects (p<0.05), indicating potential anticipatory effects or pre-trends violation"
  - "No FDR-significant results for H6-A - CCCL exposure does not significantly reduce speech uncertainty after correction"
  - "All 6 CCCL instrument variants tested for robustness - qualitatively similar negative but insignificant effects"

patterns-established:
  - "Panel OLS with Firm + Year FE, clustered SE at firm level"
  - "FDR correction (Benjamini-Hochberg) across multiple hypothesis tests"
  - "Pre-trends testing using future treatment leads for falsification"

# Metrics
duration: 8min
completed: 2026-02-05
---

# Phase 42 Plan 02: H6 CCCL Regression Analysis Summary

**Panel OLS regressions testing SEC scrutiny (CCCL) effects on speech uncertainty find no significant reduction after FDR correction, with pre-trends test showing concerning anticipatory effects**

## Performance

- **Duration:** 8 min (started 2026-02-05T22:47:39Z, completed 2026-02-05T22:55:42Z)
- **Started:** 2026-02-05T22:47:39Z
- **Completed:** 2026-02-05T22:55:42Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Created 4.6_H6CCCLRegression.py implementing panel OLS regressions for H6 hypothesis testing
- Ran 39 regressions: 7 primary measures x 4 specs + 6 instrument variants
- Applied FDR correction (Benjamini-Hochberg) across 7 primary tests
- Executed pre-trends falsification test showing significant future CCCL effects
- Completed mechanism test (H6-B) comparing Q&A vs Presentation effects
- Ran gap analysis (H6-C) testing CCCL effect on uncertainty gap
- Tested all 6 CCCL instrument variants for robustness

## Task Commits

Each task was committed atomically:

1. **Task 1: Create 4.6_H6CCCLRegression.py script** - `2f6defe` (feat)
2. **Task 2: Execute 4.6_H6CCCLRegression.py** - `1469bd0` (feat)

**Plan metadata:** Regression outputs included in same commits (parquet, markdown, stats.json)

## Files Created/Modified

- `2_Scripts/4_Econometric_V2/4.6_H6CCCLRegression.py` - Panel OLS regression script for H6 testing
- `4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/2026-02-05_225849/H6_Regression_Results.parquet` - Regression coefficients and diagnostics (39 rows)
- `4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/2026-02-05_225849/H6_RESULTS.md` - Human-readable results summary
- `4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/2026-02-05_225849/stats.json` - Complete regression statistics
- `3_Logs/4_Econometric_V2/4.6_H6CCCLRegression/2026-02-05_225849_H6.log` - Execution log

## Regression Results Summary

### Primary Hypothesis (H6-A): CCCL reduces speech uncertainty

| Uncertainty Measure | N | beta_CCCL (SE) | p1 (one-tail) | FDR q | Significant |
|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 21,988 | -0.0918 (0.0660) | 0.0821 | 0.4926 | No |
| Manager_QA_Weak_Modal_pct | 21,988 | -0.0376 (0.0407) | 0.1779 | 0.5246 | No |
| Manager_Pres_Uncertainty_pct | 22,089 | -0.0005 (0.1066) | 0.4980 | 0.5976 | No |
| CEO_QA_Uncertainty_pct | 16,784 | -0.0113 (0.1287) | 0.4649 | 0.5976 | No |
| CEO_Weak_Modal_pct | 16,784 | -0.0412 (0.0794) | 0.3019 | 0.5976 | No |
| CEO_Pres_Uncertainty_pct | 16,655 | 0.0688 (0.0824) | 0.7982 | 0.7982 | No |

**H6-A Result:** NOT SUPPORTED - 0/6 measures significant after FDR correction

### Pre-trends Test (Falsification)

| Variable | Beta | p-value | Significant |
|---|---|---|---|
| CCCL_{t+2} | -0.0910 | 0.0118 | Yes |
| CCCL_{t+1} | -0.0847 | 0.0378 | Yes |
| CCCL_t | -0.0514 | 0.4079 | No |

**Pre-trends Result:** FAILED - Future CCCL effects are significant, suggesting potential anticipatory effects or pre-trends violation. This weakens the causal interpretation of H6.

### Mechanism Test (H6-B): QA > Pres effects

| Comparison | QA beta | Pres beta | |QA| > |Pres| |
|---|---|---|---|
| Manager QA vs Pres | -0.0918 | -0.0005 | Yes |
| CEO QA vs Pres | -0.0113 | 0.0688 | No |

**H6-B Result:** NOT SUPPORTED - Only 1/2 QA effects larger than Pres

### Gap Analysis (H6-C)

| Metric | Result |
|---|---|
| beta_CCCL | -0.0791 (SE: 0.1018) |
| p-value (one-tail) | 0.2186 |
| H6-C supported | No |

**H6-C Result:** NOT SUPPORTED - CCCL does not significantly reduce the uncertainty gap

### Robustness Checks

All 6 CCCL instrument variants tested:

| Instrument | beta_CCCL | p1 (one-tail) |
|---|---|---|
| shift_intensity_mkvalt_ff48_lag (PRIMARY) | -0.0918 | 0.0821* |
| shift_intensity_sale_ff48_lag | -0.1154 | 0.0629* |
| shift_intensity_mkvalt_ff12_lag | -0.0876 | 0.0877* |
| shift_intensity_sale_ff12_lag | -0.1059 | 0.0812* |
| shift_intensity_mkvalt_sic2_lag | -0.0994 | 0.0853* |
| shift_intensity_sale_sic2_lag | -0.1241 | 0.0557* |

*All instruments show negative effects, with some marginal significance (p < 0.10) but none surviving FDR correction.*

## Decisions Made

- **Gap analysis included:** uncertainty_gap variable was not in the original uncertainty_cols list but is now included in regression data preparation for H6-C testing
- **FDR includes gap analysis:** uncertainty_gap is treated as a 7th test in FDR correction (total 7 primary tests)
- **All 6 CCCL instruments tested:** Script now tests all 6 instrument variants for robustness (previously only tested primary)
- **Pre-trends reported correctly:** Future CCCL effects are significant, which is a falsification concern for the research design

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed gap analysis data preparation**
- **Found during:** Task 2 (Execute 4.6_H6CCCLRegression.py)
- **Issue:** uncertainty_gap was not included in available_measures because prepare_regression_data() only included predefined UNCERTAINTY_MEASURES
- **Fix:** Modified prepare_regression_data() to append 'uncertainty_gap' to available_measures if present in data
- **Files modified:** 2_Scripts/4_Econometric_V2/4.6_H6CCCLRegression.py
- **Verification:** Gap analysis now runs and produces beta=-0.0791, p=0.2186
- **Committed in:** 1469bd0 (Task 2 commit)

**2. [Rule 3 - Blocking] Fixed instrument robustness data preparation**
- **Found during:** Task 2 (Execute 4.6_H6CCCLRegression.py)
- **Issue:** Instrument robustness test only ran 1/6 instruments because reg_df only contained primary CCCL column. Other CCCL variants were dropped during prepare_regression_data()
- **Fix:** Modified run_instrument_robustness() to accept full h6_df and prepare subset data for each instrument variant separately
- **Files modified:** 2_Scripts/4_Econometric_V2/4.6_H6CCCLRegression.py
- **Verification:** All 6 CCCL instrument variants now tested
- **Committed in:** 1469bd0 (Task 2 commit)

**3. [Rule 3 - Blocking] Fixed pre-trends test data preparation**
- **Found during:** Task 2 (Execute 4.6_H6CCCLRegression.py)
- **Issue:** Pre-trends test used reg_df which only had primary CCCL column, limiting ability to create proper lead variables
- **Fix:** Modified pre-trends test to use full h6_df for creating lead/lag variables
- **Files modified:** 2_Scripts/4_Econometric_V2/4.6_H6CCCLRegression.py
- **Verification:** Pre-trends test now runs and shows significant future effects
- **Committed in:** 1469bd0 (Task 2 commit)

**4. [Rule 2 - Missing Critical] Fixed markdown output for pre-trends test**
- **Found during:** Task 2 (Output verification)
- **Issue:** Pre-trends test section showed "SKIPPED - success" when test actually ran with meaningful results
- **Fix:** Modified generate_results_markdown() to properly handle pre_trends dict with 'note=success' case and display coefficient table
- **Files modified:** 2_Scripts/4_Econometric_V2/4.6_H6CCCLRegression.py
- **Verification:** Pre-trends section now shows future CCCL effects with significance indicators
- **Committed in:** 1469bd0 (Task 2 commit)

**5. [Rule 2 - Missing Critical] Fixed primary results table duplicates**
- **Found during:** Task 2 (Output verification)
- **Issue:** Primary results table showed duplicate rows because mechanism test QA/Pres results were also being included in primary spec table
- **Fix:** Modified generate_results_markdown() to only include predefined primary_measures list in primary spec table
- **Files modified:** 2_Scripts/4_Econometric_V2/4.6_H6CCCLRegression.py
- **Verification:** Primary results table now shows exactly 6 uncertainty measures
- **Committed in:** 1469bd0 (Task 2 commit)

---

**Total deviations:** 5 auto-fixed (3 blocking, 2 missing critical)
**Impact on plan:** All auto-fixes were necessary for correct execution and output completeness. No scope creep.

## Issues Encountered

- **Pre-trends test shows significant future effects:** This is a research design concern, not a code issue. The significant CCCL_{t+2} (p=0.012) and CCCL_{t+1} (p=0.038) coefficients suggest potential anticipatory effects or violation of the parallel trends assumption, which weakens causal interpretation of the H6 results.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready:**
- H6 regression analysis complete with null results documented
- All regression outputs available (parquet, markdown, stats.json)
- Robustness checks completed across 6 instrument variants

**Concerns:**
- Pre-trends test failed (future CCCL effects significant) - this weakens causal interpretation
- H6-A, H6-B, H6-C all not supported - hypothesis should be reported as null in discussion section
- Consider discussing the pre-trends violation as a limitation in the thesis

**For next phases:**
- Discussion section should reference these null H6 results
- Consider H6 as part of the broader pattern of null speech uncertainty results

---
*Phase: 42-h6-sec-scrutiny-cccl-reduces-manager-speech-uncertainty*
*Completed: 2026-02-05*

## Self-Check: PASSED

All key files created:
- 2_Scripts/4_Econometric_V2/4.6_H6CCCLRegression.py: FOUND
- 4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/2026-02-05_225849/H6_Regression_Results.parquet: FOUND
- 4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/2026-02-05_225849/H6_RESULTS.md: FOUND
- 4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/2026-02-05_225849/stats.json: FOUND
- 3_Logs/4_Econometric_V2/4.6_H6CCCLRegression/2026-02-05_225849_H6.log: FOUND

All commits verified:
- 2f6defe: FOUND (feat: create H6 CCCL regression script)
- 1469bd0: FOUND (feat: improve H6 CCCL regression script)
- 6c50d87: FOUND (docs: complete H6 CCCL regression plan)

Regression count verified: 39 regressions in results file
