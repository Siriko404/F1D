---
phase: 35-h3-payout-policy-regression
plan: 01
subsystem: econometric-regression
tags: [panel-ols, linearmodels, hypothesis-testing, payout-policy, dividend-stability, leverage-interaction]

# Dependency graph
requires:
  - phase: 31-h3-payout-policy-variables
    provides: div_stability, payout_flexibility DVs and H3 controls
  - phase: 29-h1-cash-holdings-variables
    provides: leverage moderator variable
  - phase: 32-econometric-infra
    provides: panel_ols, centering, diagnostics modules
  - phase: 28-v2-structure
    provides: speech uncertainty measures
provides:
  - H3 regression results for 48 specifications (2 DVs x 6 measures x 4 specs)
  - Coefficient-level parquet with hypothesis test outcomes
  - Human-readable markdown summary with significance counts
affects: [36-robustness-checks, 37-identification, 38-publication-output]

# Tech tracking
tech-stack:
  added: []
  patterns: [one-tailed-hypothesis-tests-by-dv-direction, leverage-moderation-regression, lead-dependent-variable-structure]

key-files:
  created:
    - 2_Scripts/4_Econometric_V2/4.3_H3PayoutPolicyRegression.py
    - 4_Outputs/4_Econometric_V2/4.3_H3PayoutPolicyRegression/2026-02-05_180836/H3_Regression_Results.parquet
    - 4_Outputs/4_Econometric_V2/4.3_H3PayoutPolicyRegression/2026-02-05_180836/stats.json
    - 4_Outputs/4_Econometric_V2/4.3_H3PayoutPolicyRegression/2026-02-05_180836/H3_RESULTS.md
    - 3_Logs/4_Econometric_V2/4.3_H3PayoutPolicyRegression/2026-02-05_180836_H3.log
  modified: []

key-decisions:
  - "H3 one-tailed tests have different directions per DV: stability tests beta < 0, flexibility tests beta > 0"
  - "Sample size 243K-258K after speech merge (1566% of H3 base - many H3 obs match multiple speech calls)"

patterns-established:
  - "Pattern: DV-specific hypothesis directions - H3 tests opposite directions for stability vs flexibility"
  - "Pattern: Leverage moderation regression with centered interaction terms (shared across H1/H2/H3)"
  - "Pattern: Lead dependent variable structure (t+1 outcome predicted by t variables)"

# Metrics
duration: 5.7min
completed: 2026-02-05
---

# Phase 35: H3 Payout Policy Regression Summary

**48 panel OLS regressions testing speech uncertainty effects on dividend policy stability and flexibility with leverage moderation**

## Performance

- **Duration:** 5.7 minutes (82 seconds for regression execution)
- **Started:** 2026-02-05T23:05:39Z
- **Completed:** 2026-02-05T23:11:22Z
- **Tasks:** 1
- **Files modified:** 1 created

## Accomplishments

- Created 4.3_H3PayoutPolicyRegression.py (1,050 lines) executing 48 regressions
- Correctly implemented DV-specific one-tailed hypothesis tests (different directions for stability vs flexibility)
- Generated complete regression outputs: coefficient parquet (480 rows), stats.json, H3_RESULTS.md
- Merged H1 leverage data into H3 regression (H3 variables lack leverage column)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create and execute H3 Payout Policy regression script** - `0b8104b` (feat)

**Plan metadata:** (pending final commit)

## Files Created/Modified

- `2_Scripts/4_Econometric_V2/4.3_H3PayoutPolicyRegression.py` - Executes 48 regressions with DV-specific hypothesis tests
- `4_Outputs/4_Econometric_V2/4.3_H3PayoutPolicyRegression/2026-02-05_180836/H3_Regression_Results.parquet` - Long-format coefficient data (480 rows)
- `4_Outputs/4_Econometric_V2/4.3_H3PayoutPolicyRegression/2026-02-05_180836/stats.json` - Summary statistics and hypothesis test outcomes
- `4_Outputs/4_Econometric_V2/4.3_H3PayoutPolicyRegression/2026-02-05_180836/H3_RESULTS.md` - Human-readable results tables
- `3_Logs/4_Econometric_V2/4.3_H3PayoutPolicyRegression/2026-02-05_180836_H3.log` - Execution log

## Decisions Made

- H3 hypothesis test directions vary by DV: div_stability tests beta1 < 0 (vagueness reduces stability), payout_flexibility tests beta1 > 0 (vagueness increases flexibility)
- H3b (leverage moderation) also DV-specific: beta3 < 0 for stability (leverage amplifies instability), beta3 > 0 for flexibility (leverage amplifies volatility)
- Speech data merge creates 1566% sample expansion vs H3 base (16,616 -> 260,213) due to multiple speech calls per firm-year matching H3 dividend observations
- After lead variable creation, final samples: div_stability (258,384 obs), payout_flexibility (258,651 obs)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all regressions executed without errors.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- H3 regression complete, ready for Phase 36 (Robustness Checks)
- All three hypothesis tests (H1, H2, H3) now complete
- Pattern established for robustness checks: alternative specifications, subsample analyses
- No blockers or concerns

---
*Phase: 35-h3-payout-policy-regression*
*Completed: 2026-02-05*
