---
phase: 30-h2-investment-efficiency
plan: 02
subsystem: financial-variables
tags: [analyst-dispersion, IBES, CCM, CUSIP-GVKEY-mapping, control-variables]

# Dependency graph
requires:
  - phase: 30-h2-investment-efficiency
    plan: 01
    provides: H2 Investment Efficiency output parquet with 13 columns
provides:
  - Analyst dispersion control variable (analyst_dispersion = STDEV / |MEANEST|)
  - CUSIP-GVKEY linking via CCM (LINKPRIM in ['P','C'], LINKTYPE in ['LU','LC'])
  - H2 output patched to 14 columns including analyst_dispersion
affects: [34-h2-regression]

# Tech tracking
tech-stack:
  added: [CCM-linking, IBES-analyst-forests]
  patterns: [patch-script-pattern, CUSIP-to-GVKEY-mapping, winsorization-1-99]

key-files:
  created: [2_Scripts/3_Financial_V2/3.2a_AnalystDispersionPatch.py]
  modified: [4_Outputs/3_Financial_V2/2026-02-05_125355/H2_InvestmentEfficiency.parquet, 4_Outputs/3_Financial_V2/2026-02-05_125355/stats.json]

key-decisions:
  - "Used CCM LINKPRIM in ['P','C'] AND LINKTYPE in ['LU','LC'] for valid CUSIP-GVKEY links"
  - "Aggregated analyst dispersion by gvkey-year using MEDIAN (robust to outliers)"
  - "Applied winsorization (1%, 99%) consistent with other continuous variables"

patterns-established:
  - "Patch script pattern: standalone script to augment existing outputs"
  - "IBES filtering: NUMEST >= 2 AND |MEANEST| >= 0.01 before computing dispersion"

# Metrics
duration: ~20min
completed: 2026-02-05
---

# Phase 30 Plan 02: Analyst Dispersion Gap Closure Summary

**CUSIP-GVKEY linking via CCM with 77.41% H2 coverage, adding analyst_dispersion control variable for H2 regression**

## Performance

- **Duration:** ~20 minutes
- **Started:** 2026-02-05T18:27:59Z
- **Completed:** 2026-02-05T18:47:00Z
- **Tasks:** 2
- **Files modified:** 1 script created, outputs updated

## Accomplishments

- Created standalone patch script `3.2a_AnalystDispersionPatch.py` (637 lines) that loads CCM and IBES data
- Implemented CUSIP-GVKEY mapping using CCM with LINKPRIM/LINKTYPE filtering
- Computed analyst_dispersion = STDEV / |MEANEST| with proper filtering (NUMEST >= 2, |MEANEST| >= 0.01)
- Patched H2 output to 14 columns, achieving 77.41% coverage (22,360/28,887 observations)
- H2-05 requirement (Analyst Dispersion control variable) NOW SATISFIED

## Task Commits

Each task was committed atomically:

1. **Task 1: Create 3.2a_AnalystDispersionPatch.py Script** - `19302dd` (feat)

**Plan metadata:** N/A (outputs gitignored, only script committed)

_Note: Outputs are gitignored per project convention_

## Files Created/Modified

- `2_Scripts/3_Financial_V2/3.2a_AnalystDispersionPatch.py` - Standalone patch script for analyst dispersion computation
  - Loads CCM with LINKPRIM in ['P','C'] AND LINKTYPE in ['LU','LC'] filters
  - Loads IBES with columns: CUSIP, STATPERS, NUMEST, MEANEST, STDEV
  - Maps CUSIP to GVKEY via CCM cusip8-gvkey_str mapping
  - Computes analyst_dispersion = STDEV / |MEANEST|
  - Aggregates by gvkey-year using MEDIAN
  - Merges into H2 output and applies winsorization (1%, 99%)

- `4_Outputs/3_Financial_V2/2026-02-05_125355/H2_InvestmentEfficiency.parquet` - Updated with 14th column
  - Added analyst_dispersion column
  - 22,360 valid observations (77.41% coverage)
  - 6,527 missing (22.59%)

- `4_Outputs/3_Financial_V2/2026-02-05_125355/stats.json` - Updated with analyst_dispersion statistics
  - mean: 0.0756, std: 0.0779
  - min: 0.0082, max: 0.4712 (post-winsorization)
  - n: 22,360, missing_count: 6,527

- `3_Logs/3_Financial_V2/2026-02-05_125355_H2_AnalystDispersion.log` - Processing log with match rates

## Decisions Made

1. **CCM Filtering:** Used LINKPRIM in ['P', 'C'] AND LINKTYPE in ['LU', 'LC'] to select only valid CUSIP-GVKEY links. This filtered out 504 rows (1.6% of CCM).

2. **IBES Filtering:** Applied NUMEST >= 2 (requires 2+ analysts for meaningful dispersion) AND |MEANEST| >= 0.01 (avoids near-zero denominators). This filtered out 7.4M rows from 25.5M IBES observations.

3. **Aggregation Method:** Used MEDIAN aggregation by gvkey-year (instead of mean) for robustness to outliers in analyst forecasts.

4. **Winsorization:** Applied 1%/99% winsorization consistent with other continuous H2 variables.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed column name mismatch in dry-run mode**
- **Found during:** Task 1 (script testing)
- **Issue:** Dry-run code referenced `dispersion_gvkey["gvkey"]` but the column was named `gvkey_str`
- **Fix:** Changed reference to `dispersion_gvkey["gvkey_str"]`
- **Files modified:** 2_Scripts/3_Financial_V2/3.2a_AnalystDispersionPatch.py
- **Verification:** Dry-run executed successfully
- **Committed in:** 19302dd (part of task commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Bug fix necessary for script execution. No scope creep.

## Issues Encountered

None - script executed as designed after minor column name fix.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**H2-05 NOW SATISFIED:** Analyst dispersion control variable is available in H2 output.

**Ready for Phase 34 (H2 Regression):**
- H2 Investment Efficiency dataset has all 14 required columns
- Control variables include: tobins_q, cf_volatility, industry_capex_intensity, firm_size, roa, fcf, earnings_volatility, analyst_dispersion

**No blockers:** Phase 30 can proceed to Phase 31 (H3 Payout Policy) or Phase 32 (Econometric Infrastructure).

---
*Phase: 30-h2-investment-efficiency*
*Completed: 2026-02-05*
