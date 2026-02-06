---
phase: 53-h2-prisk-uncertainty-investment
plan: 01
subsystem: financial-variables
tags: [biddle-2009, investment-residual, first-stage-regression, ff48-industries, statsmodels]

# Dependency graph
requires:
  - phase: 01-sample
    provides: master_sample_manifest.parquet (sample firm identification)
provides:
  - InvestmentResidual dependent variable for H2 regression (PRisk x Uncertainty -> Investment Efficiency)
  - Biddle controls: CashFlow, Size, Leverage, TobinQ, SalesGrowth
  - First-stage regression diagnostics by FF48-year (R2, N, F-stat)
affects: [53-02, 54-h2-regression]

# Tech tracking
tech-stack:
  added: [statsmodels.api.OLS, pyarrow.parquet, gc memory management]
  patterns: [first-stage industry-year regression, sample-filtering-first optimization, intermediate-disk-spill for memory efficiency]

key-files:
  created:
    - 2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py
    - 4_Outputs/3_Financial_V3/4.1_H2_BiddleInvestmentResidual/2026-02-06_173856/H2_InvestmentResiduals.parquet
    - 4_Outputs/3_Financial_V3/4.1_H2_BiddleInvestmentResidual/2026-02-06_173856/stats.json
    - 3_Logs/3_Financial_V3/4.1_H2_BiddleInvestmentResidual/2026-02-06_173856_Biddle.log
  modified: []

key-decisions:
  - "Deduplicate Compustat quarterly data to annual using keep='last' on gvkey-fyear (standard practice for quarterly Compustat)"
  - "Filter to sample firms BEFORE variable construction to avoid processing 956K observations when only 42K needed"
  - "Use intermediate disk spill for residuals before merging controls to avoid MemoryError on large dataframes"
  - "V3 folder structure separates external risk (PRisk) interaction hypotheses from V2 linguistic uncertainty main effects"

patterns-established:
  - "Sample-filtering-first: filter Compustat to manifest gvkeys before expensive operations"
  - "Memory-efficient merging: deduplicate dataframes before merge, use gc.collect() between operations"
  - "Progress indicators: print progress every N cells for long-running loops"

# Metrics
duration: 32min
completed: 2026-02-06
---

# Phase 53 Plan 1: Biddle (2009) Investment Residual Summary

**Biddle (2009) first-stage investment efficiency residual from FF48-year regressions of Investment on Tobin's Q and Sales Growth, with 33,862 firm-year observations and mean R2 of 0.147**

## Performance

- **Duration:** 32 min (from 2026-02-06T17:06:55Z to 2026-02-06T17:38:56Z)
- **Started:** 2026-02-06T17:06:55Z
- **Completed:** 2026-02-06T17:38:56Z
- **Tasks:** 4
- **Files modified:** 1 (script created)

## Accomplishments

- Implemented correct Biddle (2009) investment residual specification (NOT Phase 30's roa_residual)
- Constructed Investment = (CapEx + R&D + Acq - AssetSales) / lagged(AT) with winsorization
- Ran 558 first-stage regressions across 985 FF48-year cells (427 cells too thin for regression)
- Generated firm-year level dataset with InvestmentResidual DV and Biddle controls ready for H2 regression

## Task Commits

Each task was committed atomically:

1. **Task 1: Create V3 folder structure and Biddle investment residual script** - `94be560` (feat)
2. **Task 2-4: Load data, construct variables, run regressions (fixes included)** - `a067ccb` (fix)

**Plan metadata:** (summary creation pending)

## Files Created/Modified

- `2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py` - Main script implementing Biddle (2009) first-stage regression with memory-efficient processing
- `4_Outputs/3_Financial_V3/4.1_H2_BiddleInvestmentResidual/2026-02-06_173856/H2_InvestmentResiduals.parquet` - 33,862 firm-year observations with InvestmentResidual DV and all controls
- `4_Outputs/3_Financial_V3/4.1_H2_BiddleInvestmentResidual/2026-02-06_173856/stats.json` - First-stage diagnostics including R2, residual distribution, sample statistics

## Output Specification

| Variable | Description | Source |
|----------|-------------|--------|
| InvestmentResidual | DV for H2: deviation from expected investment given growth opportunities | First-stage residual |
| Investment | Raw investment = (CapEx + R&D + Acq - AssetSales) / lag(AT) | Compustat annual |
| TobinQ_lag | Lagged Tobin's Q (first-stage predictor) | (AT + MKVALT - CEQ) / AT |
| SalesGrowth_lag | Lagged sales growth (first-stage predictor) | (SALE_t - SALE_t-1) / \|SALE_t-1\| |
| CashFlow | Operating cash flow / Assets | OANCF / AT |
| Size | Log of total assets | log(AT) |
| Leverage | Market leverage | (DLTT + DLC) / (DLTT + DLC + MKVALT) |
| first_stage_r2 | First-stage R2 by FF48-year cell | OLS regression |

## Decisions Made

- **V3 folder structure:** Created separate `3_Financial_V3/` folder to distinguish external risk (PRisk) interaction hypotheses from V2 linguistic uncertainty main effects
- **Sample filtering first:** Filter Compustat to sample firms BEFORE variable construction to avoid processing 956K observations when only 42K needed (164,997 -> 42,020 after deduplication)
- **Quarterly to annual:** Use `keep='last'` on gvkey-fyear to get Q4/most recent quarterly observation as annual value (standard practice with Compustat daily/quarterly data)
- **Memory optimization:** Use intermediate disk spill for residuals and gc.collect() between merge operations to avoid MemoryError on large dataframes

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed Compustat column names (q/y suffixes not in plan)**
- **Found during:** Task 2 (Load Compustat and construct Investment)
- **Issue:** Compustat uses quarterly (q) and annual (y) suffixes (atq, capxy, xrdy) not the simple names (at, capx, xrd) specified in plan
- **Fix:** Updated load_compustat_investment() to read correct column names and rename them for consistency
- **Files modified:** 2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py
- **Verification:** Script successfully loads and constructs Investment variable
- **Committed in:** a067ccb (fix commit)

**2. [Rule 3 - Blocking] Fixed quarterly data causing duplicate firm-year observations**
- **Found during:** Output verification after first run
- **Issue:** Compustat contains quarterly data; without deduplication, output had 2.4M rows with 64+ duplicates per gvkey-fyear
- **Fix:** Added deduplication step: `drop_duplicates(subset=['gvkey', 'fyear'], keep='last')` after sample filtering
- **Files modified:** 2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py
- **Verification:** Output now has 33,862 unique firm-year observations (max 1 per gvkey-fyear)
- **Committed in:** a067ccb (fix commit)

**3. [Rule 1 - Bug] Fixed MemoryError during control variable merge**
- **Found during:** Task 4 (Merge with controls)
- **Issue:** Merging 2.4M-row dataframes caused MemoryError due to duplicate rows creating memory bloat
- **Fix:** (1) Deduplicate quarterly data first, (2) Save intermediate residuals to disk, (3) Reload and merge controls one at a time with gc.collect()
- **Files modified:** 2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py
- **Verification:** Script completes without memory error, output has correct 33,862 observations
- **Committed in:** a067ccb (fix commit)

---

**Total deviations:** 3 auto-fixed (3 blocking)
**Impact on plan:** All auto-fixes necessary for correctness and script execution. Deduplication critical for valid regression output (multiple quarters per firm-year would bias results).

## Issues Encountered

- **MemoryError during merge:** Initial attempt to merge 2.4M-row dataframes failed with MemoryError. Fixed by (a) quarterly deduplication reducing data size, and (b) intermediate disk spill for residuals before merging controls.
- **Column name mismatch:** Compustat parquet uses q/y suffixes not simple names. Fixed by mapping columns during load.

## Next Phase Readiness

- InvestmentResidual DV ready for merge with PRisk (Plan 53-02)
- Biddle controls (CashFlow, Size, Leverage) included in output
- First-stage R2 statistics available for diagnostic tables
- V3 folder structure established for external risk interaction hypotheses

**Output location:** `4_Outputs/3_Financial_V3/4.1_H2_BiddleInvestmentResidual/latest/`

---
*Phase: 53-h2-prisk-uncertainty-investment*
*Plan: 01*
*Completed: 2026-02-06*
