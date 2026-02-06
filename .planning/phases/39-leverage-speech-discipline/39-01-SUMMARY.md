# Phase 39 Plan 01: H4 Data Preparation Summary

**One-liner:** H4 analysis dataset with lagged leverage (t-1) for testing whether higher leverage disciplines managers and reduces speech uncertainty.

---

## Frontmatter

```yaml
phase: 39-leverage-speech-discipline
plan: 01
title: H4 Data Preparation
completed: 2026-02-05
subsystem: econometric_infra
tags: [h4, leverage_discipline, reverse_causality, lagged_leverage, vif_diagnostics]
```

---

## Dependency Graph

```
requires:
  - Phase 29: H1 Cash Holdings Variables (leverage, firm_size, tobins_q, roa, cash_holdings, dividend_payer)
  - Phase 31: H3 Payout Policy Variables (firm_maturity, earnings_volatility)
  - Phase 25: Textual Analysis Variables (6 uncertainty measures, analyst uncertainty, presentation controls)

provides:
  - H4_Analysis_Dataset.parquet: Complete analysis dataset for 6 H4 regressions
  - vif_diagnostics.json: Multicollinearity check results
  - H4_DATA_SUMMARY.md: Human-readable dataset documentation

affects:
  - Phase 39-02: H4 Regression Execution (depends on this analysis dataset)
```

---

## Tech Stack

**Added:** None (uses existing pandas, numpy, statsmodels stack)

**Patterns:**
- Lagged variable creation via groupby shift for panel data
- VIF diagnostics for multicollinearity detection
- Deduplication handling for pandas merge operations with duplicate columns

---

## Files Created/Modified

**Created:**
- `2_Scripts/4_Econometric_V2/4.4_H4_LeverageDiscipline.py` (946 lines)
  - Contract header with H4 model specification
  - Data loading: H1 (leverage + controls), H3 (firm_maturity, earnings_volatility), speech uncertainty
  - Lagged leverage creation with groupby shift, no cross-entity leakage validation
  - VIF diagnostics integration (threshold 5.0)
  - Analysis dataset merge on (gvkey, fiscal_year)
  - Output: parquet, stats.json, markdown summary

**Generated (gitignored):**
- `4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/2026-02-05_193751/H4_Analysis_Dataset.parquet`
  - 445,563 observations, 2,428 firms, 19 columns
  - 6 uncertainty DVs: Manager_QA_Uncertainty_pct (98.7%), CEO_QA_Uncertainty_pct (75.5%), Manager_QA_Weak_Modal_pct (98.7%), CEO_QA_Weak_Modal_pct (75.5%), Manager_Pres_Uncertainty_pct (99.1%), CEO_Pres_Uncertainty_pct (74.7%)
  - Lagged leverage: leverage_lag1 (100% coverage)
  - Analyst uncertainty: analyst_qa_uncertainty (97.0%)
  - Financial controls: firm_size, tobins_q, roa, cash_holdings, dividend_payer, firm_maturity, earnings_volatility

---

## Decisions Made

1. **Lagged leverage creation:** Used groupby shift(1) on gvkey to create leverage_{t-1}, dropping first year per firm (no lag available)
2. **VIF threshold:** Maintained 5.0 threshold from econometric infrastructure (all values passed: 1.03-1.79)
3. **Duplicate column handling:** Added suffix-based deduplication in merge operations (pandas 3.x compatibility fix)
4. **Presentation controls:** Not added as separate controls (already in DV list for presentation uncertainty measures)

---

## Execution Results

**Commits:**
- `bfeaa37`: feat(39-01): create H4 data preparation script
- `0ed6aba`: fix(39-01): fix pandas 3.x compatibility and execute H4 data preparation

**Duration:** ~8 minutes (including debugging and fixes)

**VIF Diagnostics:**
| Variable | VIF | Status |
|----------|-----|--------|
| leverage_lag1 | 1.21 | OK |
| analyst_qa_uncertainty | 1.03 | OK |
| firm_size | 1.17 | OK |
| tobins_q | 1.79 | OK |
| roa | 1.66 | OK |
| cash_holdings | 1.38 | OK |
| firm_maturity | 1.16 | OK |
| earnings_volatility | 1.09 | OK |

Condition number: 168.76 (acceptable)

**Correlations (leverage_lag1 vs uncertainty DVs):**
- Manager_QA_Uncertainty_pct: -0.0082
- CEO_QA_Uncertainty_pct: -0.0196
- Manager_QA_Weak_Modal_pct: +0.0155
- CEO_QA_Weak_Modal_pct: +0.0015
- Manager_Pres_Uncertainty_pct: -0.0161
- CEO_Pres_Uncertainty_pct: +0.0215

All correlations are very weak, suggesting no strong bivariate relationship.

---

## Deviations from Plan

### Auto-fixed Issues (Rule 3 - Blocking)

**1. [Rule 3 - Blocking] Pandas 3.x aggregate() dictionary incompatibility**
- **Found during:** Task 2 execution
- **Issue:** pandas 3.x changed behavior of groupby.agg(dict) - no longer supports mixed aggregation types (mean + count) in single dict
- **Fix:** Split aggregation into two operations: mean() for numeric columns, count() for file_name, then merge results
- **Files modified:** 4.4_H4_LeverageDiscipline.py (aggregate_speech_to_firmyear function)
- **Commit:** 0ed6aba

**2. [Rule 3 - Blocking] Pandas 3.x Series.int() conversion error**
- **Found during:** Task 2 execution
- **Issue:** pandas 3.x Series no longer supports direct int() conversion (raises TypeError)
- **Fix:** Added try/except with iloc[0] or .item() extraction for scalar conversion
- **Files modified:** 4.4_H4_LeverageDiscipline.py (prepare_analysis_dataset, variable availability logging, stats collection)
- **Commit:** 0ed6aba

**3. [Rule 3 - Blocking] Duplicate column names from merge operations**
- **Found during:** Task 2 execution
- **Issue:** H1 and H3 both have firm_size, roa, tobins_q, cash_holdings; speech merge also created duplicates
- **Fix:** Added suffix-based merge with coalescing; added explicit DataFrame column deduplication after selection
- **Files modified:** 4.4_H4_LeverageDiscipline.py (prepare_analysis_dataset function)
- **Commit:** 0ed6aba

### No Architectural Changes
All deviations were compatibility fixes for pandas 3.x. No changes to H4 model specification or data structure.

---

## Next Phase Readiness

**Plan 39-02 (H4 Regression Execution) prerequisites:**
- [x] H4_Analysis_Dataset.parquet exists with all required variables
- [x] Lagged leverage (leverage_lag1) properly computed
- [x] All 6 uncertainty DVs available
- [x] VIF diagnostics passed (< 5.0)
- [x] Analyst uncertainty control available
- [x] Financial controls merged from H1 and H3

**No blockers.** Ready for H4 regression execution.

---

## Verification Checklist

- [x] Script 4.4_H4_LeverageDiscipline.py exists with contract header
- [x] H4_Analysis_Dataset.parquet contains: gvkey, fiscal_year, 6 uncertainty DVs, leverage_lag1, analyst_qa_uncertainty, all financial controls
- [x] Lagged leverage created with proper within-firm shift
- [x] VIF diagnostics show all values < 5.0
- [x] stats.json documents N=445,563, merge success, variable coverage
- [x] Log file shows successful execution with no errors

---

## Success Criteria Met

1. [x] Analysis dataset ready for 6 H4 regressions with all required variables
2. [x] VIF diagnostics confirm no multicollinearity concerns (max VIF = 1.79)
3. [x] Variable availability documented - all DVs and controls present
4. [x] Data preparation reproducible via script execution (--prepare-only flag)

---

## Output Location

```
4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/2026-02-05_193751/
├── H4_Analysis_Dataset.parquet  (4.3 MB, 445,563 rows, 19 cols)
├── stats.json                    (execution metadata, VIF results)
├── vif_diagnostics.json          (VIF detail)
└── H4_DATA_SUMMARY.md            (human-readable summary)

3_Logs/4_Econometric_V2/4.4_H4_LeverageDiscipline/2026-02-05_193751_H4.log
```
