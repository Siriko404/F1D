---
phase: 30-h2-investment-efficiency
verified: 2026-02-05T18:50:00Z
status: passed
score: 7/7 must-haves verified
re_verification:
  previous_status: gaps_found
  previous_score: 6/7
  gaps_closed:
    - "Analyst Dispersion linked from IBES via CUSIP with proper filters"
    - "All control variables computed with appropriate formulas"
  gaps_remaining: []
  regressions: []
gaps: []
---

# Phase 30: H2 Investment Efficiency Verification Report

**Phase Goal:** Construct all dependent and control variables for H2 (Investment Efficiency) hypothesis
**Verified:** 2026-02-05T18:50:00Z
**Status:** passed
**Re-verification:** Yes - gap closure verification after 30-02 execution

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Overinvestment Dummy correctly flags firms with Capex/DP > 1.5 AND SalesGrowth < industry-year median | ✓ VERIFIED | Code L413-416: `(df_unique["capex_dp"] > 1.5) & (df_unique["sales_growth"] < df_unique["sales_growth_ind_median"])`; stats.json: mean=0.4963, n=28,887 |
| 2 | Underinvestment Dummy correctly flags firms with Capex/DP < 0.75 AND Tobin's Q > 1.5 | ✓ VERIFIED | Code L445-446: `(df_unique["capex_dp"] < 0.75) & (df_unique["tobins_q"] > 1.5)`; stats.json: mean=0.0168, n=28,887 |
| 3 | Over/underinvestment dummies are mutually exclusive per firm-year | ✓ VERIFIED | `enforce_mutual_exclusivity()` at L459-481; Logic ensures both=1 rows reset to 0 |
| 4 | Efficiency Score reflects 5-year rolling proportion of efficient years | ✓ VERIFIED | `compute_efficiency_score()` L489-583; window=5, min_periods=3; stats.json: mean=0.4932, range [0,1], n=28,887 |
| 5 | ROA Residual computed from industry-year cross-sectional OLS regressions | ✓ VERIFIED | `compute_roa_residuals()` L616-695 uses `sm.OLS(Y, X).fit()` by FF48-year; stats.json: mean=0.2523, n=28,595 |
| 6 | Analyst Dispersion linked from IBES via CUSIP with proper filters | ✓ VERIFIED | Patch script 3.2a_AnalystDispersionPatch.py (637 lines) loads CCM with LINKPRIM/LINKTYPE filters, computes STDEV/|MEANEST|, aggregates by gvkey-year; stats.json: mean=0.0756, n=22,360 (77.41% coverage) |
| 7 | All control variables computed with appropriate formulas | ✓ VERIFIED | 8 controls present (tobins_q, cf_volatility, industry_capex_intensity, firm_size, roa, fcf, earnings_volatility, analyst_dispersion); all with full stats in stats.json |

**Score:** 7/7 truths verified (100%)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `2_Scripts/3_Financial_V2/3.2_H2Variables.py` | H2 variable construction script (600+ lines) | ✓ VERIFIED | 1,689 lines, substantive implementation, no stub patterns |
| `2_Scripts/3_Financial_V2/3.2a_AnalystDispersionPatch.py` | Analyst dispersion patch script | ✓ VERIFIED | 637 lines, substantive, loads CCM/IBES, computes dispersion with proper filters |
| `4_Outputs/3_Financial_V2/2026-02-05_125355/H2_InvestmentEfficiency.parquet` | H2 variables dataset with 14 columns | ✓ VERIFIED | 28,887 rows, 14 columns including analyst_dispersion |
| `4_Outputs/3_Financial_V2/2026-02-05_125355/stats.json` | Variable distribution statistics for all 12 variables | ✓ VERIFIED | Documents 12 variables (4 DVs + 8 controls) with mean/std/min/max/n/missing |
| `3_Logs/3_Financial_V2/2026-02-05_125355_H2.log` | Execution log | ✓ VERIFIED | Log shows full execution |
| `3_Logs/3_Financial_V2/2026-02-05_125355_H2_AnalystDispersion.log` | Analyst dispersion patch log | ✓ VERIFIED | Log shows CCM/IBES loading and match rates |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| 3.2_H2Variables.py | shared/industry_utils.py | parse_ff_industries import | ✓ WIRED | `from shared.industry_utils import parse_ff_industries` at L80 |
| 3.2_H2Variables.py | 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet | Compustat data loading | ✓ WIRED | Loads at L126 with required columns |
| 3.2_H2Variables.py | statsmodels OLS | Biddle regression residuals | ✓ WIRED | `model = sm.OLS(Y, X).fit()` at L647 |
| 3.2a_AnalystDispersionPatch.py | 1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet | CCM loading | ✓ WIRED | Loads at L165 with LINKPRIM/LINKTYPE filters |
| 3.2a_AnalystDispersionPatch.py | 1_Inputs/tr_ibes/tr_ibes.parquet | IBES loading | ✓ WIRED | Loads at L207 with NUMEST/MEANEST/STDEV columns |
| 3.2a_AnalystDispersionPatch.py | H2_InvestmentEfficiency.parquet | Patch existing output | ✓ WIRED | Loads at L281, merges analyst_dispersion, saves at L552 |

### Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| H2-01: Overinvestment classification (Capex/DP > 1.5 AND SalesGrowth < industry-year median) | ✓ SATISFIED | overinvest_dummy in output, mean=0.4963 |
| H2-02: Underinvestment classification (Capex/DP < 0.75 AND Tobin's Q > 1.5) | ✓ SATISFIED | underinvest_dummy in output, mean=0.0168 |
| H2-03: Efficiency Score DV (5-year rolling proportion) | ✓ SATISFIED | efficiency_score in output, mean=0.4932, range [0,1] |
| H2-04: Alternative DV (ROA residual from cross-sectional OLS) | ✓ SATISFIED | roa_residual in output, computed via FF48-year regressions |
| H2-05: Controls (Tobin's Q, CF Volatility, Industry CapEx, Analyst Dispersion) | ✓ SATISFIED | All 4 controls present; analyst_dispersion added via patch, 77.41% coverage |
| H2-06: Standard controls (Firm Size, ROA, FCF, Earnings Volatility) | ✓ SATISFIED | All 4 controls present with full statistics |

### Anti-Patterns Found

None - all scripts pass anti-pattern checks:
- No TODO/FIXME comments
- No placeholder text
- No empty implementations
- No console.log-only stubs

### Human Verification Required

None - all checks automated with structural verification.

### Gap Closure Summary

**Previous Status (30-01-VERIFICATION.md):** gaps_found (6/7 verified)

**Gaps Identified:**
1. Analyst Dispersion control variable MISSING from output (H2-05 requirement blocked)
2. Only 7/8 controls present (analyst_dispersion missing)
3. Output had 13 columns instead of 14

**Gap Closure Actions (Plan 30-02):**
1. Created standalone patch script `3.2a_AnalystDispersionPatch.py` (637 lines)
2. Implemented CUSIP-GVKEY linking via CCM (LINKPRIM in ['P','C'] AND LINKTYPE in ['LU','LC'])
3. Computed analyst_dispersion = STDEV / |MEANEST| with NUMEST >= 2 AND |MEANEST| >= 0.01 filters
4. Aggregated by gvkey-year using MEDIAN
5. Applied winsorization (1%, 99%) consistent with other variables
6. Merged into H2 output, achieving 77.41% coverage (22,360/28,887 observations)

**Current Status: passed (7/7 verified)**

All requirements satisfied. H2 output ready for Phase 34 (H2 Regression).

---

_Verified: 2026-02-05T18:50:00Z_
_Verifier: Claude (gsd-verifier)_
