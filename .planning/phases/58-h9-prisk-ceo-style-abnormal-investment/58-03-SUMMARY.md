---
phase: 58-h9-prisk-ceo-style-abnormal-investment
plan: 03
subsystem: financial-variables
tags: [biddle-investment, abnormal-investment, statsmodels, winsorization, ols]

# Dependency graph
requires:
  - phase: 58-01
    provides: StyleFrozen construction script pattern
  - phase: 53-01
    provides: Biddle investment residual reference implementation
provides:
  - abnormal_investment.parquet: Biddle-style AbsAbInv with controls (80,048 obs)
  - 5.8_H9_AbnormalInvestment.py: Production script with memory-efficient processing
affects:
  - phase: 58-04 (merge and regression) - needs AbsAbInv as dependent variable

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Biddle first-stage by industry-year cells with ind1 fallback
    - Memory-efficient Compustat processing with PyArrow filters
    - Processed indices tracking to avoid duplicates in regression

key-files:
  created:
    - 2_Scripts/5_Financial_V3/5.8_H9_AbnormalInvestment.py
  modified: []

key-decisions:
  - "Use ind2 (2-digit SIC) for first-stage with ind1 fallback when N < 30"
  - "Denominator for TotalInv is at_t (current year assets), not at_{t+1}"
  - "CAPX required non-missing; R&D/AQC/SPPE optional (set to 0 if missing)"
  - "Winsorize AFTER first-stage regression, not before"
  - "Track processed_indices to avoid duplicate rows from ind1 fallback"

patterns-established:
  - "First-stage OLS by (industry, year) cells with minimum size threshold"
  - "Two-pass regression: sufficient cells first, then fallback for unprocessed"

# Metrics
duration: 3min
completed: 2026-02-10
---

# Phase 58: H9 PRisk x CEO Style -> Abnormal Investment Summary

**Biddle (2009) abnormal investment construction with 80,048 firm-year observations, industry-year first-stage regressions, and comprehensive control variables**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-10T15:40:24Z
- **Completed:** 2026-02-10T15:43:16Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Created production script for Biddle abnormal investment with proper first-stage regressions
- Fixed duplicate rows bug from ind1 fallback (327K -> 80K observations)
- Generated AbsAbInv dependent variable and all control variables for H9 regression

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Biddle Abnormal Investment construction script** - `f55416d` (fix)
   - Script already existed, fixed critical duplicate rows bug in first-stage regression

2. **Task 2: Execute Biddle Abnormal Investment construction** - (outputs gitignored)

**Plan metadata:** N/A (outputs gitignored)

## Files Created/Modified

- `2_Scripts/5_Financial_V3/5.8_H9_AbnormalInvestment.py` - Biddle abnormal investment construction script (1,259 lines)
  - load_compustat(): Memory-efficient PyArrow filtering by fyear
  - assign_industry(): SIC-based ind2/ind1 classification, exclude utilities/financials
  - create_panel_with_leads_lags(): Lead/lag construction for investment variables
  - construct_investment(): TotalInv with CAPX required, R&D/AQC/SPPE optional
  - construct_sales_growth(): SalesGrowth with lagged sales denominator validation
  - run_first_stage_regression(): OLS by (ind2, fyear) with ind1 fallback
  - construct_controls(): ln_at, lev, cash, roa, mb control variables
  - winsorize_by_fyear(): 1%/99% winsorization by fiscal year

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed duplicate rows bug in first-stage regression**
- **Found during:** Task 2 (Execute abnormal investment construction)
- **Issue:** First execution produced 327,231 observations instead of expected ~80,000. Root cause: ind1 fallback was creating duplicate entries when multiple thin ind2 cells fell back to the same ind1 cell.
- **Fix:** Rewrote regression to use two-pass approach:
  1. Process all ind2 cells with N >= 30 first, track processed_indices
  2. Handle ind1 fallback only for unprocessed observations
  This prevents duplicate entries from overlapping ind1 cells.
- **Files modified:** 2_Scripts/5_Financial_V3/5.8_H9_AbnormalInvestment.py
- **Verification:** Re-ran script, output now correctly 80,048 observations (matching input filter stage)
- **Committed in:** f55416d

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Bug fix was necessary for correct output. No scope creep.

## Issues Encountered

- Initial script execution produced 327K observations (4x expected) due to duplicate rows from ind1 fallback
- Fixed with two-pass regression approach tracking processed indices

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- AbsAbInv dataset ready for 58-04 (merge and regression)
- Controls have low missingness (mb_t has 6.4% missing, others 0%)
- Sample size (80K obs) sufficient for H9 regression interaction test

**Blockers:** None - ready to proceed with 58-04 (PRiskFY dataset needed first)

## Self-Check: PASSED

- [OK] SUMMARY.md created: .planning/phases/58-h9-prisk-ceo-style-abnormal-investment/58-03-SUMMARY.md
- [OK] Script exists: 2_Scripts/5_Financial_V3/5.8_H9_AbnormalInvestment.py
- [OK] Bug fix commit: f55416d (fix duplicate rows in first-stage regression)
- [OK] Summary commit: 6a6ad33 (docs: complete Biddle abnormal investment summary)
- [OK] STATE.md updated: Position at 58-03 complete, decisions added

---
*Phase: 58-h9-prisk-ceo-style-abnormal-investment*
*Completed: 2026-02-10*
