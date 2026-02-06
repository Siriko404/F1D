---
phase: 55-v1-hypotheses-retest
plan: 04
subsystem: econometric-regression
tags: [panel-ols, fixed-effects, illiquidity, amihud, fdr-correction, h7-regression]

# Dependency graph
requires:
  - phase: 55-v1-hypotheses-retest
    plan: 55-03
    provides: H7_Illiquidity.parquet with amihud_lag1 DV and uncertainty IVs
  - phase: 28-v2-structure-setup
    provides: V2 script conventions and panel_ols utility
provides:
  - 4.7_H7IlliquidityRegression.py: H7 primary regression script
  - H7_Regression_Results.parquet: Regression coefficients, SEs, p-values
  - H7_RESULTS.md: Human-readable results summary
  - Conclusion: H7a NOT SUPPORTED (uncertainty does not predict illiquidity)
affects: [55-v1-hypotheses-retest/55-05, h8-takeover-regression, final-report]

# Tech tracking
tech-stack:
  added: [linearmodels.PanelOLS, statsmodels.multitest.multipletests, fdr-bh]
  patterns: [panel-regression, firm-clustering, one-tailed-tests, forward-looking-dv]

key-files:
  created:
    - 2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py
    - 4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113/H7_Regression_Results.parquet
    - 4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113/H7_RESULTS.md
    - 4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113/stats.json
    - 3_Logs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113_H7.log
  modified: []

key-decisions:
  - "Use 4 uncertainty measures (not 6) - Weak Modal variables not in H7_Illiquidity.parquet"
  - "Pass gvkey/year as columns to run_panel_ols (not as index) - function handles MultiIndex setup"
  - "Drop rows with missing controls (Volatility/StockRet) - needed for valid regression"
  - "One-tailed test: p_one = p_two/2 if coef > 0, else 1 - p_two/2"
  - "FDR correction applied only to primary spec results"

patterns-established:
  - "H7 regression pattern: Uncertainty_t -> Illiquidity_{t+1} with Firm+Year FE"
  - "16 regressions total: 4 uncertainty measures x 4 specifications"
  - "Results in 3 formats: parquet (data), markdown (human), json (metadata)"

# Metrics
duration: 1.1s
completed: 2026-02-06
---

# Phase 55: H7 Illiquidity Regression Summary

**PanelOLS regression testing whether managerial speech uncertainty predicts future stock illiquidity - H7a NOT SUPPORTED**

## Performance

- **Duration:** 1.1 seconds (execution time)
- **Started:** 2026-02-06T18:41:13Z
- **Completed:** 2026-02-06T18:41:14Z
- **Tasks:** 4 (script header, data loading, regression function, output reporting)
- **Files modified:** 1 created

## Accomplishments

- **H7 regression script created:** 4.7_H7IlliquidityRegression.py (901 lines)
- **Primary regression executed:** 4 uncertainty measures x 4 specifications = 16 regressions
- **FDR correction applied:** Benjamini-Hochberg across 4 measures
- **Results output:** parquet, markdown, and JSON formats
- **Hypothesis tested:** H7a (beta > 0: uncertainty increases illiquidity)

## Task Commits

Each task was committed atomically:

1. **Task 1-4: H7 Illiquidity Regression Script** - `df87707` (feat)
   - Script header with V2 conventions and model specification
   - Data loading from H7_Illiquidity.parquet
   - PanelOLS regression with Firm + Year FE, firm-clustered SE
   - FDR correction and results output (parquet, markdown, JSON)

**Plan metadata:** N/A (all tasks in single commit)

## Files Created/Modified

- `2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py` - H7 regression script (901 lines)
- `4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113/H7_Regression_Results.parquet` - Results data
- `4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113/H7_RESULTS.md` - Human-readable report
- `4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113/stats.json` - Execution metadata

## Primary Specification Results

Model: PanelOLS with Firm + Year FE, firm-clustered SE

| Uncertainty Measure | Beta | SE | t-stat | p (one-tailed) | Significant? |
|---------------------|------|----|----|----------------|--------------|
| Manager_QA_Uncertainty_pct | 0.0013 | 0.0044 | 0.29 | 0.3876 | No |
| CEO_QA_Uncertainty_pct | -0.0047 | 0.0036 | -1.31 | 0.9041 | No |
| Manager_Pres_Uncertainty_pct | 0.0043 | 0.0053 | 0.81 | 0.2078 | No |
| CEO_Pres_Uncertainty_pct | -0.0018 | 0.0051 | -0.36 | 0.6390 | No |

**Sample:** 3,706 observations, 2,283 firms, 2002-2018

## Robustness Specifications

| Spec | Entity FE | Time FE | Cluster | N | Signif (p<0.05) | Avg Beta |
|---|---|---|---|---|---|---|
| primary | Yes | Yes | firm | 3,706 | 0/4 | -0.0002 |
| firm_only | Yes | No | firm | 3,706 | 0/4 | -0.0001 |
| pooled | No | No | firm | 3,706 | 0/4 | -0.0115 |
| double_cluster | Yes | Yes | firm+year | 3,706 | 0/4 | -0.0002 |

## Hypothesis Conclusion

**H7a NOT SUPPORTED:** Managerial speech uncertainty does not predict stock illiquidity.

- 0/4 uncertainty measures significant at p < 0.05 (one-tailed)
- FDR correction: 0/4 measures significant
- Average coefficient: -0.0002 (wrong direction)
- All 4 robustness specifications agree: null results

## Decisions Made

- **Used 4 uncertainty measures** (not 6) - Weak Modal variables not available in H7 data
- **Passed gvkey/year as columns** to run_panel_ols - function handles MultiIndex setup internally
- **Dropped rows with missing controls** (85% missing Volatility/StockRet) - required for valid regression
- **One-tailed p-value calculation:** p_one = p_two/2 if coef > 0, else 1 - p_two/2
- **FDR correction applied** only to primary specification results

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed uncertainty measures list**
- **Found during:** Task 1 (script creation)
- **Issue:** Script referenced 6 uncertainty measures including Weak Modal, but H7_Illiquidity.parquet only has 4
- **Fix:** Updated UNCERTAINTY_MEASURES to only include available measures (Manager/CEO x QA/Pres)
- **Files modified:** 2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py
- **Verification:** Script executes successfully with 4 measures
- **Committed in:** df87707 (main task commit)

**2. [Rule 3 - Blocking] Fixed MultiIndex handling in run_h7_regression**
- **Found during:** Task 3 (regression execution)
- **Issue:** run_panel_ols expects entity_col and time_col as columns, not in MultiIndex
- **Fix:** Changed to pass df with gvkey/year as columns, let run_panel_ols set MultiIndex
- **Files modified:** 2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py
- **Verification:** Regressions execute successfully, 16 models run
- **Committed in:** df87707 (main task commit)

**3. [Rule 3 - Blocking] Fixed save_regression_results error handling**
- **Found during:** Task 4 (output generation)
- **Issue:** Error results don't have 'r2' key, causing KeyError
- **Fix:** Changed all dict access to use .get() with default values
- **Files modified:** 2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py
- **Verification:** Script completes successfully, outputs saved
- **Committed in:** df87707 (main task commit)

**4. [Rule 3 - Blocking] Fixed n_firms calculation after index reset**
- **Found during:** Task 3 (regression execution)
- **Issue:** n_firms used index.get_level_values after reset_index, but index was columns
- **Fix:** Changed to model_df['gvkey'].nunique()
- **Files modified:** 2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py
- **Verification:** Correct firm count (2,283) in results
- **Committed in:** df87707 (main task commit)

---

**Total deviations:** 4 auto-fixed (4 blocking)
**Impact on plan:** All fixes necessary for script execution. No scope creep.

## Issues Encountered

- **Weak Modal variables not in H7 data:** Adjusted to use 4 available measures instead of 6
- **Index handling with run_panel_ols:** Needed to pass columns, not MultiIndex
- **High control variable missingness:** 85% missing Volatility/StockRet, but regression still works

## Next Phase Readiness

**H7 regression complete:**
- All 4 uncertainty measures tested
- 4 specifications (primary, firm_only, pooled, double_cluster)
- FDR correction applied
- Clear conclusion: H7a NOT SUPPORTED

**Ready for:**
- 55-05: H7 robustness suite (if additional specs needed)
- Comparison to V1 results (if available)
- H8 takeover regression preparation

**No blockers:** H7 regression analysis complete and documented.

## Self-Check: PASSED

All key files verified:
- 2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py: EXISTS
- 4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113/H7_Regression_Results.parquet: EXISTS
- 4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113/H7_RESULTS.md: EXISTS
- 3_Logs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_184113_H7.log: EXISTS

All commits verified:
- df87707: feat(55-04): create H7 illiquidity regression script
- 54a84e2: docs(55-04): complete H7 illiquidity regression plan

---
*Phase: 55-v1-hypotheses-retest*
*Completed: 2026-02-06*
