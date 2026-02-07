---
title: "Phase 55 Plan 05: H7 Robustness Suite Summary"
phase: 55
plan: 05
subsystem: "Hypothesis Retesting - H7"
tags: [h7, robustness, panel-ols, fdr, illiquidity]
---

# Phase 55 Plan 05: H7 Robustness Suite Summary

**Date Completed:** 2026-02-06
**Duration:** ~3 minutes
**Commits:** 4

---

## One-Liner
Implemented and executed full robustness suite for H7 (Speech Uncertainty -> Stock Illiquidity), testing alternative DVs, IVs, and specifications.

---

## Objective

Execute full robustness suite for Hypothesis 1 (H7) following pre-registered approach. Per CONTEXT locked decision: "Always run full robustness suite regardless of primary result."

---

## Tasks Completed

### Task 1: Add Robustness Framework to 4.7 Script
**Commit:** `d9d082d`

Added robustness configuration and helper functions to `4.7_H7IlliquidityRegression.py`:

- `ROBUSTNESS_CONFIG` dictionary with 4 robustness dimensions:
  - Alternative DVs: Roll (1984) spread, bid-ask spread
  - Alternative specs: Firm only, Pooled, Double-clustered SE
  - Alternative IVs: CEO-only, Presentation-only, QA-only
  - Timing tests: Concurrent, Forward, Lead
- `create_alternative_dvs()` function for creating forward-looking alternative DVs
- `create_timing_variants()` function for timing robustness testing

### Task 2: Implement Robustness Regression Suite
**Commit:** `7847c68`

Implemented full robustness suite execution:

- Modified `run_h7_regression()` to accept `dv_type`, `iv_type`, `timing` metadata parameters
- Added `run_robustness_suite()` function implementing all 4 robustness dimensions
- Updated `save_regression_results()` to include robustness metadata columns
- Updated `generate_results_markdown()` to display robustness results
- Integrated robustness suite into main() execution flow

### Task 3: Execute Robustness Suite
**Commits:** `b67035e`

Fixed bugs and executed full robustness suite:

- **Bug Fix 1:** Positional argument bug where `dw` parameter was being assigned to `timing` parameter
- **Bug Fix 2:** Added alternative DVs (`roll_spread_lag1`, `log_amihud_lag1`) to aggregation columns
- Executed full robustness suite: 30 total regressions (16 primary + 14 robustness)
- Results saved to parquet and markdown

### Task 4: Update H7_RESULTS.md with Robustness Summary
**Commit:** `e0cf711`

Fixed markdown generation:

- Filtered primary results table to only show primary DV (Amihud) and primary IVs
- Fixed denominator from 6 to 4 (H7 has 4 uncertainty measures, not 6)
- Primary results table now correctly shows only 4 rows
- Robustness tests section shows all alternative DV and IV results

---

## Results Summary

### Primary Specification Results (H7a)
**Hypothesis:** Higher speech uncertainty predicts HIGHER stock illiquidity (beta > 0)

| Uncertainty Measure | Beta | SE | t-stat | p (one-tailed) | Significant? |
|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 0.0013 | 0.0044 | 0.29 | 0.3876 | No |
| CEO_QA_Uncertainty_pct | -0.0047 | 0.0036 | -1.31 | 0.9041 | No |
| Manager_Pres_Uncertainty_pct | 0.0043 | 0.0053 | 0.81 | 0.2078 | No |
| CEO_Pres_Uncertainty_pct | -0.0018 | 0.0051 | -0.36 | 0.6390 | No |

**Conclusion:** H7a NOT SUPPORTED - 0/4 measures significant

### Robustness Tests

| Dimension | Tests | Significant | Avg Beta |
|---|---|---|---|
| Alternative DVs: Roll (1984) | 4 | 0/4 | -0.0002 |
| Alternative DVs: Log Amihud | 4 | 0/4 | ~0.0000 |
| Alternative IVs: CEO-only | 2 | 0/2 | -0.0033 |
| Alternative IVs: Presentation-only | 2 | 0/2 | 0.0012 |
| Alternative IVs: QA-only | 2 | 0/2 | -0.0017 |
| Timing: Concurrent/Forward/Lead | - | SKIPPED | N/A |

**Robustness Summary:** 0/14 (0.0%) robustness tests significant (p < 0.05)

### Sample Characteristics
- N (observations): 26,135 firm-years
- N (firms): 2,283
- Period: 2002-2018

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed positional argument bug in run_h7_regression call**
- **Found during:** Task 3 execution
- **Issue:** `dw` parameter was being passed positionally and assigned to `timing` parameter
- **Fix:** Changed call from `run_h7_regression(..., dw)` to `run_h7_regression(..., dw=dw)`
- **Files modified:** `2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py`
- **Commit:** `b67035e`

**2. [Rule 2 - Missing Critical] Include alternative DVs in data aggregation**
- **Found during:** Task 3 execution
- **Issue:** `prepare_regression_data()` only kept primary DV column, alternative DVs were dropped
- **Fix:** Added `roll_spread_lag1` and `log_amihud_lag1` to `agg_cols` list
- **Files modified:** `2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py`
- **Commit:** `b67035e`

**3. [Rule 1 - Bug] Fixed primary results table showing duplicate rows**
- **Found during:** Task 4 verification
- **Issue:** `generate_results_markdown()` included all primary-spec results, including alternative DV/IV tests
- **Fix:** Filtered `primary_results` to only include Amihud DV with no alternative IV/timing
- **Files modified:** `2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py`
- **Commit:** `e0cf711`

### Planned Adjustments

**4. Timing tests skipped due to data availability**
- **Reason:** H7 data only contains forward-looking DVs (`amihud_lag1`, `roll_spread_lag1`)
- **Current-period illiquidity (`amihud_illiquidity`) not available**
- **Impact:** Timing robustness dimension not tested
- **Status:** Documented in output as "SKIPPED"

---

## Decisions Made

1. **Use existing forward-looking DVs for alternative DV tests** - Since H7 data contains `roll_spread_lag1` and `log_amihud_lag1` (already forward-looking), these are used directly rather than creating new forward-looking versions

2. **Skip timing tests** - Current-period illiquidity not available in H7 data; timing tests would require access to `amihud_illiquidity` (current period)

3. **Filter primary results table** - Only show results with Amihud DV and no alternative IV/timing in the primary results table for clarity

---

## Outputs

**Files Created/Modified:**
- `2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py` - Updated with robustness suite
- `4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_185937/H7_Regression_Results.parquet` - All regression results
- `4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_185937/H7_RESULTS.md` - Human-readable results
- `4_Outputs/4_Econometric_V2/4.7_H7IlliquidityRegression/2026-02-06_185937/stats.json` - Execution statistics

**Regression Results:**
- 30 total regressions (16 primary + 14 robustness)
- 4 primary specs x 4 uncertainty measures = 16 primary regressions
- 8 alternative DV tests (Roll: 4, Log Amihud: 4)
- 6 alternative IV tests (CEO-only: 2, Presentation-only: 2, QA-only: 2)

---

## Next Phase Readiness

**H7 Robustness Complete:**
- Full robustness suite executed per pre-registered approach
- Results documented in H7_RESULTS.md
- Data saved to parquet for future reference

**Ready for:**
- Phase 55-06: H8 Robustness (similar pattern)
- Or any other hypothesis requiring robustness testing

**No blockers identified.**

---

## Self-Check: PASSED

All files created and committed correctly:
- `2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py` - EXISTS
- `H7_Regression_Results.parquet` - EXISTS
- `H7_RESULTS.md` - EXISTS

All commits verified:
- `d9d082d` - FOUND
- `7847c68` - FOUND
- `b67035e` - FOUND
- `e0cf711` - FOUND
