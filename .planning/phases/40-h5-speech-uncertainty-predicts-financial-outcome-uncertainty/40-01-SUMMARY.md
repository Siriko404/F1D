---
phase: 40-h5-speech-uncertainty-predicts-financial-outcome-uncertainty
plan: 01
subsystem: financial-variables
tags: [analyst-dispersion, ibes, ccm-linking, pyarrow, forward-looking-timing]

# Dependency graph
requires:
  - phase: 28-structure-setup
    provides: V2 directory structure, CLAUDE.md conventions, shared utilities
  - phase: 29-h1-cash-holdings
    provides: H1_CashHoldings.parquet with firm_size, leverage controls
  - phase: 30-h2-investment-efficiency
    provides: H2_InvestmentEfficiency.parquet with earnings_volatility, tobins_q controls
  - phase: 2.2-textual-analysis
    provides: linguistic_variables_*.parquet with speech uncertainty measures

provides:
  - 3.5_H5Variables.py script for analyst dispersion computation
  - H5_AnalystDispersion.parquet with 850,889 observations
  - Forward-looking timing: Speech_t matched to Dispersion_{t+1}
  - Uncertainty gap measure (QA_Uncertainty - Pres_Uncertainty)

affects:
  - phase: 40-02 (regression script will use this analysis dataset)
  - phase: 40 (hypothesis testing depends on these variables)

# Tech tracking
tech-stack:
  added: [pyarrow.parquet (memory-efficient IBES loading)]
  patterns: [row-group aggregation, CCM CUSIP-GVKEY linking, forward-looking shift(-1)]

key-files:
  created: [2_Scripts/3_Financial_V2/3.5_H5Variables.py]
  modified: []

key-decisions:
  - "IBES loading via PyArrow row groups to manage 25M+ row file in memory"
  - "CCM LINKPRIM='P' (string) not integer 1 for primary link selection"
  - "GVKEY standardization to string with leading zeros (zfill(6)) for compatibility"
  - "Placeholder CUSIP filtering: 00000000, nan, NaN, None excluded"
  - "Forward-looking dispersion via groupby().shift(-1) for Speech_t -> Dispersion_{t+1}"

patterns-established:
  - "Memory-efficient pattern: read-row-group -> filter -> aggregate -> concat"
  - "CCM linking: CUSIP8 extraction, LINKPRIM='P', GVKEY string conversion"
  - "NumpyEncoder for JSON serialization of numpy types in stats.json"

# Metrics
duration: 20min
completed: 2026-02-05
---

# Phase 40: Plan 01 - H5 Analyst Dispersion Variables Summary

**Analyst forecast dispersion (STDEV/|MEANEST|) with forward-looking timing (Speech_t predicts Dispersion_{t+1}), CCM CUSIP-GVKEY linking, and uncertainty gap measure for testing whether hedging language predicts analyst disagreement beyond general uncertainty.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-02-05T21:14:16Z (first dry-run)
- **Completed:** 2026-02-05T21:32:04Z (final execution)
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments
- Created 3.5_H5Variables.py with memory-efficient IBES loading (25M+ rows via PyArrow row groups)
- Implemented CCM CUSIP-GVKEY linking with LINKPRIM='P' and GVKEY string standardization
- Generated H5_AnalystDispersion.parquet with 850,889 observations, 8,693 firms, 1996-2024 coverage
- Computed forward-looking dispersion_lead (t+1) with 0.34 persistence correlation
- Merged all 6 speech uncertainty measures and computed uncertainty_gap (-0.041 mean)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create 3.5_H5Variables.py Script** - `bb093b3` (feat)
2. **Task 2: Execute H5 Variables Script** - `f7ea6da` (feat)

## Files Created/Modified
- `2_Scripts/3_Financial_V2/3.5_H5Variables.py` - H5 variable construction script with analyst dispersion, earnings surprise, loss dummy, uncertainty gap, and speech measure merging

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed IBES memory allocation error**
- **Found during:** Task 1 (dry-run)
- **Issue:** 25M row IBES file caused MemoryError: Unable to allocate 415 MiB for filtering
- **Fix:** Implemented PyArrow row-group-by-row-group reading with inline aggregation before concat
- **Files modified:** 2_Scripts/3_Financial_V2/3.5_H5Variables.py (load_ibes function)
- **Committed in:** f7ea6da (Task 2 commit)

**2. [Rule 3 - Blocking] Fixed CCM linking returning 0 matches**
- **Found during:** Task 2 (script execution)
- **Issue:** CCM LINKPRIM column is string 'P'/'C'/'J'/'N', not integer 1 as assumed
- **Fix:** Changed filter from `LINKPRIM == 1` to `LINKPRIM == "P"`
- **Files modified:** 2_Scripts/3_Financial_V2/3.5_H5Variables.py (compute_analyst_dispersion function)
- **Committed in:** f7ea6da (Task 2 commit)

**3. [Rule 3 - Blocking] Fixed GVKEY type mismatch in merges**
- **Found during:** Task 2 (script execution)
- **Issue:** CCM returns int64 GVKEY, but Compustat/speech use string with leading zeros
- **Fix:** Added `.astype(str).str.zfill(6)` to CCM GVKEY for consistent 6-digit string format
- **Files modified:** 2_Scripts/3_Financial_V2/3.5_H5Variables.py (compute_analyst_dispersion function)
- **Committed in:** f7ea6da (Task 2 commit)

**4. [Rule 1 - Bug] Fixed placeholder CUSIP contamination**
- **Found during:** Task 2 (debugging 0 CCM matches)
- **Issue:** IBES contains CUSIP='00000000' placeholder values becoming '00000000' cusip8
- **Fix:** Added filter to exclude cusip8 in ['00000000', 'nan', 'NaN', 'None']
- **Files modified:** 2_Scripts/3_Financial_V2/3.5_H5Variables.py (load_ibes function)
- **Committed in:** f7ea6da (Task 2 commit)

**5. [Rule 2 - Missing Critical] Added JSON numpy type encoder**
- **Found during:** Task 2 (stats.json save failure)
- **Issue:** `json.dump` fails with "Object of type int64 is not JSON serializable"
- **Fix:** Added NumpyEncoder class with handlers for np.integer, np.floating, np.ndarray
- **Files modified:** 2_Scripts/3_Financial_V2/3.5_H5Variables.py (main function)
- **Committed in:** f7ea6da (Task 2 commit)

---

**Total deviations:** 5 auto-fixed (3 blocking, 1 bug, 1 missing critical)
**Impact on plan:** All auto-fixes necessary for correct operation. Memory-efficient pattern established for large file handling.

## Issues Encountered
- IBES file (25M rows) exceeded available memory - solved via PyArrow row-group aggregation
- CCM LINKPRIM documentation mismatch (integer vs string) - discovered empirically
- GVKEY type inconsistency across data sources - standardized to string format
- JSON serialization of numpy types - implemented custom encoder

## Key Results

### Sample Quality
- **Total observations:** 850,889
- **Complete cases (key variables):** 264,504
- **Unique firms:** 8,693
- **Average quarters per firm:** 97.9
- **Years covered:** 1996-2024 (29 years)
- **Sample adequate:** Yes (264,504 >> 5,000 threshold)

### Variable Distributions
- **dispersion_lead:** mean=0.191, std=0.312, max=2.200 (winsorized 1%/99%)
- **prior_dispersion:** mean=0.190, std=0.311 (consistent with lead)
- **earnings_surprise:** mean=0.406, std=0.849, max=6.124
- **uncertainty_gap:** mean=-0.041 (Q&A slightly less uncertain than Pres), std=0.441
- **Persistence:** 0.340 correlation between adjacent quarters (moderate autocorrelation)

### Merge Statistics
- IBES raw: 25.5M rows -> 637,572 unique CUSIP8-periods (after filters)
- CCM matched: 456,884 (71.6% match rate)
- Dispersion with lead: 447,994 (98% of matched)
- Speech measures merged: 268,325 observations

## Next Phase Readiness
- H5 analysis dataset ready for regression analysis
- All dependent variables computed (dispersion_lead, prior_dispersion)
- All independent variables available (6 speech measures, uncertainty_gap)
- All control variables present (earnings_surprise, analyst_coverage, loss_dummy, firm_size, leverage, earnings_volatility)
- Next step: Create 4.5_H5DispersionRegression.py for hypothesis testing

---
*Phase: 40-h5-speech-uncertainty-predicts-financial-outcome-uncertainty*
*Plan: 01*
*Completed: 2026-02-05*
