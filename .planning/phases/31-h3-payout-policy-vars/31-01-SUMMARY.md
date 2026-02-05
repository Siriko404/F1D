---
phase: 31-h3-payout-policy-vars
plan: 01
subsystem: financial-variables
tags: [dividend-stability, payout-flexibility, earnings-volatility, fcf-growth, firm-maturity, compustat, pandas]

# Dependency graph
requires:
  - phase: 29-h1-cash-holdings-vars
    provides: standard controls (firm_size, roa, tobins_q, cash_holdings)
  - phase: 28-v2-structure
    provides: Financial_V2 folder structure and shared utilities
provides:
  - H3 dependent variables (div_stability, payout_flexibility) for regression analysis
  - H3-specific controls (earnings_volatility, fcf_growth, firm_maturity)
  - 16,616 dividend-paying firm-year observations ready for Phase 35 regression
affects:
  - phase: 35-h3-regression (requires H3 variables as inputs)
  - phase: 32-econometric-infra (needs variable schema for interaction terms)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Annualize quarterly financials before rolling window calculations
    - Filter to sample gvkeys BEFORE loading full Compustat (memory optimization)
    - Aggregate H1 multiple observations per firm-year via mean
    - Take first file_name per gvkey-year to avoid cartesian product

key-files:
  created:
    - 2_Scripts/3_Financial_V2/3.3_H3Variables.py (1,140 lines)
    - 4_Outputs/3_Financial_V2/2026-02-05_142731/H3_PayoutPolicy.parquet (1.4 MB, 16,616 obs)
    - 3_Logs/3_Financial_V2/2026-02-05_142731_H3.log
  modified:
    - 2_Scripts/shared/observability_utils.py (skip list values in stats summary)

key-decisions:
  - "Aggregate quarterly DPS/EPS to annual BEFORE computing rolling windows (avoids within-year volatility distortion)"
  - "Use absolute value in FCF growth denominator to handle negative FCF gracefully"
  - "Allow negative RE/TE as valid immaturity signal (per DeAngelo et al.)"
  - "Filter output to dividend payers only (stability/flexibility undefined for never-payers)"

patterns-established:
  - "H3 variable construction: Annualize -> Compute rolling metrics -> Merge to manifest -> Filter to subsample"
  - "Memory optimization pattern: Filter Compustat to sample gvkeys before heavy computation"

# Metrics
duration: 12min
completed: 2026-02-05
---

# Phase 31 Plan 1: H3 Payout Policy Variables Summary

**Dividend policy variables constructed: stability (-CV of DPS changes) and flexibility (% significant changes) with earnings volatility, FCF growth, and firm maturity controls for 16,616 dividend-paying firm-years**

## Performance

- **Duration:** 12 minutes
- **Started:** 2026-02-05T19:18:32Z
- **Completed:** 2026-02-05T19:30:31Z
- **Tasks:** 2 completed
- **Files modified:** 2

## Accomplishments

- Created 3.3_H3Variables.py (1,140 lines) implementing all H3-01 through H3-05 requirements
- Generated H3_PayoutPolicy.parquet with 16,616 dividend-paying firm observations
- Both dependent variables have excellent coverage: div_stability (99.8%), payout_flexibility (100%)
- All 5 controls computed with high coverage (97-100%)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create H3 payout policy variables script** - `5410840` (feat)
2. **Task 2: Fix cartesian product and unicode issues; execute H3 script** - `09a33b9` (fix)

## Files Created/Modified

- `2_Scripts/3_Financial_V2/3.3_H3Variables.py` - H3 variable construction script with annualization, rolling windows, and dividend payer filtering
- `2_Scripts/shared/observability_utils.py` - Fixed to skip list values in stats summary (prevents formatting errors)
- `4_Outputs/3_Financial_V2/2026-02-05_142731/H3_PayoutPolicy.parquet` - H3 variables for regression (16,616 obs x 13 cols)
- `3_Logs/3_Financial_V2/2026-02-05_142731_H3.log` - Execution log with timing and variable statistics

## Output Specifications

**H3_PayoutPolicy.parquet (16,616 observations, 13 columns):**

| Column | Type | Description | Coverage |
|--------|------|-------------|----------|
| gvkey | str | Firm identifier | 100% |
| fiscal_year | int64 | Fiscal year | 100% |
| div_stability | float64 | -StdDev(ΔDPS)/|Mean(DPS)| over 5y | 99.8% |
| payout_flexibility | float64 | % years with \|ΔDPS\|>5% over 5y | 100% |
| earnings_volatility | float64 | StdDev(annual EPS) over 5y | 100% |
| fcf_growth | float64 | YoY growth in (OANCF-CAPX)/AT | 97.2% |
| firm_maturity | float64 | RE / TE ratio (DeAngelo proxy) | 97.8% |
| firm_size | float64 | ln(Assets) from H1 | 100% |
| roa | float64 | IB / AT from H1 | 100% |
| tobins_q | float64 | (AT + ME - CEQ) / AT from H1 | 99.4% |
| cash_holdings | float64 | CHE / AT from H1 | 100% |
| is_div_payer | bool | Dividend payer flag | 100% |
| file_name | str | Reference speech file | 100% |

## Decisions Made

- **Aggregate H1 controls:** H1 output has multiple observations per gvkey-year (from different speeches). Aggregated via mean to get one row per firm-year for H3 merge.
- **File_name handling:** Multiple files exist per gvkey-year. Took first file as reference to avoid cartesian product. file_name is for reference, not a unique identifier.
- **Minimum window requirement:** Set min_years=2 for rolling calculations (per CONTEXT.md guidance), balancing data availability with statistical validity.
- **Division guards:** Added abs(mean_dps) > 0.001 guard for div_stability and abs(prior_dps) > 0.001 for payout_flexibility to avoid division by zero.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed Unicode Delta character causing encoding error**
- **Found during:** Task 1 (dry-run validation)
- **Issue:** Delta symbol (Δ) in docstrings caused UnicodeEncodeError on Windows
- **Fix:** Replaced all Δ with "Delta" string in docstrings and print statements
- **Files modified:** 2_Scripts/3_Financial_V2/3.3_H3Variables.py
- **Verification:** Dry-run passed without errors
- **Committed in:** 09a33b9

**2. [Rule 1 - Bug] Fixed cartesian product in H1 controls merge**
- **Found during:** Task 2 (first execution)
- **Issue:** H1 output has 448,004 rows but only 28,887 unique gvkey-year combinations. Merge created 1.9M rows (cartesian product).
- **Fix:** Added groupby mean aggregation in load_h1_standard_controls() to get one row per gvkey-year
- **Files modified:** 2_Scripts/3_Financial_V2/3.3_H3Variables.py
- **Verification:** Output now 16,616 rows (expected)
- **Committed in:** 09a33b9

**3. [Rule 1 - Bug] Fixed cartesian product in file_name merge**
- **Found during:** Task 2 (first execution)
- **Issue:** Manifest has multiple files (up to 38) per gvkey-year. Merge with drop_duplicates() still created cartesian product.
- **Fix:** Use drop_duplicates(subset=["gvkey", "year"], keep="first") to take one file per firm-year
- **Files modified:** 2_Scripts/3_Financial_V2/3.3_H3Variables.py
- **Verification:** Output row count matches manifest base (28,975 before dividend payer filter)
- **Committed in:** 09a33b9

**4. [Rule 1 - Bug] Fixed stats summary formatting error**
- **Found during:** Task 2 (first execution)
- **Issue:** print_stats_summary() tried to format list values (variables_computed) as numbers
- **Fix:** Updated observability_utils.py to skip both dict and list values in processing stats
- **Files modified:** 2_Scripts/shared/observability_utils.py
- **Verification:** Script completes with proper stats summary
- **Committed in:** 09a33b9

---

**Total deviations:** 4 auto-fixed (all Rule 1 - Bug fixes)
**Impact on plan:** All fixes necessary for correct operation. No scope creep.

## Issues Encountered

- None - all issues were auto-fixed via deviation rules.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for Phase 35 (H3 Regression):**
- H3_PayoutPolicy.parquet contains both dependent variables (div_stability, payout_flexibility)
- All 5 controls computed with high coverage
- Variable schema matches regression requirements

**Depends on Phase 32 (Econometric Infrastructure):**
- Phase 32 must provide interaction term construction (uncertainty × leverage)
- Phase 32 must provide fixed effects infrastructure
- Phase 32 must provide 2SLS instrumentation if needed

**No blockers or concerns**

---
*Phase: 31-h3-payout-policy-vars*
*Completed: 2026-02-05*
