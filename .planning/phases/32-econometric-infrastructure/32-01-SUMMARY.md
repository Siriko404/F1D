---
phase: 32-econometric-infrastructure
plan: 01
subsystem: econometrics
tags: [panel-ols, fixed-effects, vif, multicollinearity, linearmodels, statsmodels]

# Dependency graph
requires:
  - phase: 29-01, 30-01, 31-01
    provides: H1, H2, H3 dependent and independent variables
provides:
  - Panel OLS with firm + year + industry fixed effects via linearmodels.PanelOLS
  - Mean-centering utilities for interaction term creation
  - VIF calculation and multicollinearity diagnostics with threshold warnings
  - Clustered standard errors (entity, time, double-clustering)
  - HAC/Newey-West adjustment via kernel covariance
affects: [33-h1-regression, 34-h2-regression, 35-h3-regression]

# Tech tracking
tech-stack:
  added: [linearmodels.PanelOLS, statsmodels.stats.outliers_influence.variance_inflation_factor]
  patterns: [fixed-effects panel regression, mean-centered interactions, VIF-based multicollinearity detection]

key-files:
  created: [2_Scripts/shared/panel_ols.py, 2_Scripts/shared/centering.py, 2_Scripts/shared/diagnostics.py]
  modified: [2_Scripts/shared/__init__.py]

key-decisions:
  - "PanelOLS from linearmodels for FE estimation (handles high-dim FE efficiently via within-transform)"
  - "VIF threshold of 5.0 for multicollinearity warnings (balance between sensitivity and false positives)"
  - "Firm + year FE by default, industry FE optional (firm FE subsumes industry for most firms)"
  - "Clustered SE at firm level by default with double-clustering option via cov_type parameter"

patterns-established:
  - "Pattern: run_panel_ols() returns dict with model, coefficients, summary, diagnostics, warnings"
  - "Pattern: Mean-centering before interaction creation to reduce VIF"
  - "Pattern: Console output with significance stars (*, **, ***) for publication-ready tables"

# Metrics
duration: 5min
completed: 2026-02-05
---

# Phase 32 Plan 1: Econometric Infrastructure Summary

**Panel OLS with firm + year + industry FE using linearmodels, mean-centering for interactions, and VIF multicollinearity diagnostics**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-05T20:17:00Z
- **Completed:** 2026-02-05T20:22:34Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Created `panel_ols.py` with `run_panel_ols()` using linearmodels.PanelOLS for fixed effects regression
- Created `centering.py` with `center_continuous()` and `create_interaction()` for mean-centered interaction terms
- Created `diagnostics.py` with `compute_vif()` and `check_multicollinearity()` for multicollinearity detection
- Updated `shared/__init__.py` to export econometric utilities for direct import

## Task Commits

Each task was committed atomically:

1. **Task 1: Panel OLS Module** - `1eeee51` (feat)
2. **Task 2: Centering and Interaction Module** - `e283449` (feat)
3. **Task 3: Diagnostics Module** - `4b04cf6` (feat)
4. **Update shared __init__.py** - `8c5fe47` (feat)

## Files Created/Modified

### Created

- `2_Scripts/shared/panel_ols.py` (531 lines)
  - `run_panel_ols()`: Main entry point for panel regression
  - Supports entity, time, and industry fixed effects
  - Clustered SE (entity, time, double-clustering)
  - HAC/Newey-West via cov_type='kernel'
  - VIF diagnostics post-fit with threshold warnings
  - Console output with significance stars (*, **, ***)
  - Custom exceptions: CollinearityError, MulticollinearityError

- `2_Scripts/shared/centering.py` (340 lines)
  - `center_continuous()`: Mean-center variables with configurable suffix
  - `create_interaction()`: Create interaction terms with auto-centering
  - `save_centered_intermediates()`: Audit trail output (parquet + JSON)
  - `compute_marginal_effect()`: Conditional effect calculations

- `2_Scripts/shared/diagnostics.py` (413 lines)
  - `compute_vif()`: VIF calculation using statsmodels
  - `check_multicollinearity()`: Comprehensive check with VIF + condition number
  - `format_vif_table()`: Console output with threshold context
  - `compute_condition_number()`: Design matrix conditioning

### Modified

- `2_Scripts/shared/__init__.py`
  - Added exports: run_panel_ols, center_continuous, create_interaction, compute_vif, check_multicollinearity

## Decisions Made

- **linearmodels.PanelOLS**: Handles high-dimensional fixed effects efficiently via within-transformation, avoiding dummy variable explosion
- **VIF threshold 5.0**: Balances sensitivity to multicollinearity with avoiding false positives on moderately correlated variables
- **Default FE configuration**: Entity + time effects by default; industry FE optional (firm FE subsumes industry for most firms, adding both can cause rank deficiency)
- **Clustered SE at firm level**: Matches econometric convention for panel data; double-clustering available via cov_type parameter
- **Centering before interactions**: Reduces artificial multicollinearity between main effects and interaction term

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all modules created and tested successfully.

## User Setup Required

None - no external service configuration required.

## Verification

All success criteria met:

1. **Three new shared modules exist and import without error**
   - `from shared.panel_ols import run_panel_ols` - OK
   - `from shared.centering import center_continuous, create_interaction` - OK
   - `from shared.diagnostics import compute_vif, check_multicollinearity` - OK

2. **run_panel_ols() produces coefficient table with R2, N, F-stat, VIF warnings**
   - Verified with synthetic panel data (10 firms x 5 years)
   - Console output includes coefficient table, summary statistics, VIF diagnostics

3. **center_continuous() + create_interaction() enable proper interaction term creation**
   - Mean of centered column is exactly 0.0
   - Interaction term created from centered variables
   - Warns if using non-centered variables

4. **VIF diagnostics flag variables exceeding threshold with clear messaging**
   - Threshold exceeded variables marked with "*** EXCEEDS threshold"
   - Interpretation guide provided in console output

5. **All functions have docstrings, type hints, and follow CLAUDE.md contract pattern**
   - Contract headers in all three modules
   - Type hints on all function parameters and returns
   - Comprehensive docstrings with Examples

## Next Phase Readiness

**Ready for Phases 33-35 (H1/H2/H3 Regressions):**

- Panel OLS infrastructure supports all required fixed effects configurations
- Mean-centering utilities enable interaction term creation for Uncertainty x Leverage
- VIF diagnostics will catch multicollinearity issues during model specification
- Clustered SE and HAC adjustment available for robust inference

**No blockers or concerns.**

---
*Phase: 32-econometric-infrastructure*
*Completed: 2026-02-05*
