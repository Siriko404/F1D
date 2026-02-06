---
phase: 40-h5-speech-uncertainty-predicts-financial-outcome-uncertainty
verified: 2026-02-06T03:00:30Z
status: passed
score: 9/9 must-haves verified
---

# Phase 40: H5 Speech Uncertainty Predicts Analyst Forecast Dispersion - Verification Report

**Phase Goal:** Test whether hedging language (weak modal verbs) predicts analyst forecast dispersion beyond what general uncertainty words predict

**Verified:** 2026-02-06T03:00:30Z
**Status:** PASSED
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1   | H5 analysis dataset includes forward dispersion (t+1) matched to speech at time t | VERIFIED | 3.5_H5Variables.py implements groupby().shift(-1) creating dispersion_lead; 850,889 observations |
| 2   | Analyst dispersion computed with NUMEST >= 3 and |MEANEST| >= 0.05 filtering | VERIFIED | load_ibes() and compute_analyst_dispersion() accept numest_min=3, meanest_min=0.05 parameters |
| 3   | Prior dispersion (lagged DV) available for persistence control | VERIFIED | prior_dispersion column exists; included as regression control |
| 4   | Earnings surprise computed as |actual - meanest| / |meanest| | VERIFIED | compute_earnings_surprise() implements formula correctly |
| 5   | Uncertainty gap computed as Manager_QA - Manager_Pres difference | VERIFIED | compute_uncertainty_gap(): QA_Uncertainty_pct - Pres_Uncertainty_pct |
| 6   | Primary regression tests Weak_Modal effect controlling for Uncertainty | VERIFIED | Primary model includes Manager_QA_Weak_Modal_pct controlling for Manager_QA_Uncertainty_pct |
| 7   | Secondary regression tests Uncertainty_Gap effect controlling for Presentation | VERIFIED | Gap model implements uncertainty_gap controlling for Manager_Pres_Uncertainty_pct |
| 8   | Robustness checks: without lagged DV, without NUMEST, CEO-only measures | VERIFIED | ROBUSTNESS_SPECS includes no_lagged_dv, no_numest variants; CEO measures tested |
| 9   | Results document whether hedging adds beyond general uncertainty | VERIFIED | H5_RESULTS.md: Hedging does not add beyond uncertainty; stats.json confirms H5A_weak_modal_significant: false |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| 2_Scripts/3_Financial_V2/3.5_H5Variables.py | H5 variable construction script (>=400 lines) | VERIFIED | 1,166 lines, 18 functions, substantive implementation |
| 4_Outputs/3_Financial_V2/3.5_H5Variables/*/H5_AnalystDispersion.parquet | H5 analysis dataset | VERIFIED | 850,889 rows x 18 columns, all required columns present |
| 2_Scripts/4_Econometric_V2/4.5_H5DispersionRegression.py | H5 regression script (>=500 lines) | VERIFIED | 979 lines, 12 functions, uses shared utilities |
| 4_Outputs/4_Econometric_V2/4.5_H5DispersionRegression/*/H5_Regression_Results.parquet | Regression results | VERIFIED | 44 regression results across 4 specs |
| 4_Outputs/4_Econometric_V2/4.5_H5DispersionRegression/*/H5_RESULTS.md | Results summary | VERIFIED | Complete with hypothesis outcomes and interpretation |

### Key Link Verification

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| 3.5_H5Variables.py | IBES tr_ibes.parquet | CCM CUSIP-GVKEY linking | WIRED | CCM linking via LINKPRIM='P' and CUSIP8-GVKEY matching |
| dispersion_lead | fiscal_quarter | shift(-1) by firm | WIRED | groupby('gvkey')['dispersion'].shift(-1) creates t+1 timing |
| 4.5_H5DispersionRegression.py | shared/panel_ols.py | run_panel_ols import | WIRED | Imports and calls run_panel_ols() for all regressions |
| 4.5_H5DispersionRegression.py | shared/centering.py | center_continuous import | WIRED | Uses center_continuous() for control variable centering |
| H5_Regression_Results.parquet | H5_RESULTS.md | generate_results_markdown | WIRED | Function reads parquet and generates markdown |
| prior_dispersion | regression controls | prepare_regression_data | WIRED | Included in CONTROL_VARS and complete_cols check |

### Requirements Coverage

No H5-specific requirements in REQUIREMENTS.md. Phase 40 is novel hypothesis. All must-haves from plan frontmatter verified.

### Anti-Patterns Found

None. All scripts contain substantive implementations with proper error handling and logging.

### Human Verification Required

None required. All verification criteria are programmatically assessable.

Optional human review items:
1. Interpretation alignment with economic theory
2. Sample composition assessment (258,560 complete cases is adequate)

### Gaps Summary

No gaps found. All must-haves verified. Phase 40 successfully achieves its goal: tests whether hedging predicts dispersion beyond uncertainty, documents that H5 is NOT supported with Firm + Year FE.

---

_Verified: 2026-02-06T03:00:30Z_
_Verifier: Claude (gsd-verifier)_
