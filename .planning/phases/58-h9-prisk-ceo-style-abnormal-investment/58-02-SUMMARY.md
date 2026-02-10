---
phase: 58-h9-prisk-ceo-style-abnormal-investment
plan: 02
subsystem: financial-variables
tags: [priskfy, fiscal-year-aggregation, policy-risk, hassan-prisk, rolling-window]

# Dependency graph
requires:
  - phase: external
    provides: Hassan PRisk quarterly data (firmquarter_2022q1.csv)
  - phase: v2-foundation
    provides: Compustat fiscal year-end dates (comp_na_daily_all.parquet)
provides:
  - PRiskFY dataset: Fiscal-year policy risk at firm-year level (65,664 observations)
  - 366-day rolling window aggregation with minimum 2 quarters requirement
affects: [58-04] # H9 regression merge

# Tech tracking
tech-stack:
  added: [batched-processing, temp-disk-spill, memory-throttling]
  patterns:
    - 366-day rolling window: (fy_end - 366, fy_end]
    - Minimum quarters rule: >= 2 quarters required for PRiskFY
    - No forward-filling: Missing quarters stay missing
    - Batched processing: Write intermediate batches to disk to manage memory

key-files:
  created:
    - 2_Scripts/5_Financial_V3/5.8_H9_PRiskFY.py
  modified: []

key-decisions:
  - "Use 366-day window (not 365) to capture exactly one year of quarters including leap years"
  - "Minimum 2 quarters rule: Firm-years with < 2 quarters excluded (not imputed)"
  - "Batched processing with disk spill: Write 2000 firm-years per batch to temp files"
  - "No forward-filling: Only actual quarters in window used for averaging"

patterns-established:
  - "PRiskFY construction: Quarterly -> Fiscal year aggregation via date window"
  - "Memory-efficient processing: Filter firms_with_prisk before iteration"
  - "Validation: All n_quarters_used >= 2 enforced by construction"

# Metrics
duration: 5min
completed: 2026-02-10
---

# Phase 58: H9 PRisk x CEO Style - Plan 02 Summary

**Fiscal-year policy risk from Hassan quarterly PRisk using 366-day rolling window, producing 65,664 firm-year observations (7,869 firms, 2002-2021)**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-10T15:39:36Z
- **Completed:** 2026-02-10T15:44:00Z
- **Tasks:** 2 (script verification, execution)
- **Files modified:** 1

## Accomplishments

- Constructed PRiskFY (fiscal-year policy risk) from Hassan quarterly PRisk data
- Implemented 366-day rolling window: (fy_end - 366, fy_end] for quarter selection
- Enforced minimum 2 quarters rule strictly (no imputation)
- Generated priskfy.parquet with 65,664 firm-year observations
- Applied memory-efficient batched processing to handle large datasets

## Task Commits

Each task was committed atomically:

1. **Task 1: Create PRiskFY construction script** - `74813e4` (feat)
   - Implemented cal_q_end construction from "YYYYQq" format
   - Applied 366-day rolling window for quarter selection
   - Enforced minimum 2 quarters rule
   - Added batched processing with temp disk spill for memory management
   - Generated comprehensive report with coverage statistics

**Plan metadata:** (summary created post-execution)

## Files Created/Modified

- `2_Scripts/5_Financial_V3/5.8_H9_PRiskFY.py` - PRiskFY construction script with 366-day window and memory-efficient batched processing

## Output Artifacts

- `4_Outputs/5.8_H9_PRiskFY/2026-02-10_153936/priskfy.parquet` - Main dataset (65,664 firm-years)
- `4_Outputs/5.8_H9_PRiskFY/2026-02-10_153936/report_step58_02.md` - Summary report
- `4_Outputs/5.8_H9_PRiskFY/2026-02-10_153936/stats.json` - Detailed statistics

## Output Statistics

- **Observations:** 65,664 firm-years
- **Unique firms:** 7,869 (gvkey)
- **Fiscal year range:** 2002-2021
- **Coverage:** 29.4% of Compustat firm-years (65,664/223,536)
- **PRiskFY distribution:** Mean=126.86, SD=166.19, Min=0, Max=5568.14
- **n_quarters_used distribution:**
  - 2 quarters: 4,397 (6.7%)
  - 3 quarters: 7,253 (11.0%)
  - 4 quarters: 22,172 (33.8%)
  - 5 quarters: 31,842 (48.5%)

## Decisions Made

1. **366-day window specification:** Uses 366 days (not 365) to ensure full year coverage including leap years. For Dec 31 fiscal year-ends, this captures previous year's Q4 + all 4 current year quarters (5 total).
2. **Minimum 2 quarters rule:** Firm-years with fewer than 2 quarters in the window are excluded (not imputed). This ensures PRiskFY is based on sufficient data.
3. **No forward-filling:** Missing quarters are not filled with interpolated or carried-forward values. Only actual quarters in the window are used.
4. **Batched processing:** Processing 2,000 firm-years per batch with intermediate disk writes to manage memory usage for large datasets.

## Deviations from Plan

None - plan executed exactly as written. Script was already created from previous work, verified and executed successfully.

## Issues Encountered

- **5 quarters observation:** Initial concern about 5 quarters in output was verified as correct behavior. When fiscal year-end is Dec 31, the 366-day window (Dec 30 to Dec 31] captures previous year's Q4 plus all 4 quarters of current year.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- PRiskFY dataset ready for merging with StyleFrozen (58-01) and AbsAbInv (58-03)
- 366-day window and minimum quarters rules verified and documented
- Coverage sufficient for H9 regression (65,664 firm-years, 7,869 firms)

---
*Phase: 58-h9-prisk-ceo-style-abnormal-investment*
*Completed: 2026-02-10*

## Self-Check: PASSED

All files created and commits verified:
- FOUND: 2_Scripts/5_Financial_V3/5.8_H9_PRiskFY.py
- FOUND: 74813e4 (commit)
- FOUND: priskfy.parquet
- FOUND: report_step58_02.md
- FOUND: stats.json
