# Roadmap: F1D Data Pipeline

## Overview

This roadmap extends the existing F1D data processing pipeline with hypothesis testing capabilities for empirical finance research. Building on the v1.0 foundation (27 phases, 143 plans) that established observability and documentation, v2.0 implements three empirical hypotheses: H1 (Speech Uncertainty & Cash Holdings), H2 (Speech Uncertainty & Investment Efficiency), and H3 (Speech Uncertainty & Payout Policy). The work leverages existing sample construction and text measures from v1.0 while adding new variable construction and panel econometric regressions with fixed effects, interaction terms, and robustness checks.

**Milestone:** v2.0 Hypothesis Testing Suite — ACTIVE
**Phases:** 28-35 completed; 36-38 cancelled; 39-40 planned (new hypotheses H4, H5)
**Requirements:** 40/55 completed (15 requirements in cancelled phases not pursued); H5 requirements TBD

## v1.0 Completed Phases (1-27)

All v1.0 phases are complete. See archived v1.0 ROADMAP section below for reference.

<details>
<summary>v1.0 Phases (1-27) - COMPLETED</summary>

**Core Documentation Phases (1-6):**
- [x] Phase 1: Template & Pilot - Establish inline stats pattern
- [x] Phase 2: Step 1 Sample - Roll out stats to Step 1 scripts
- [x] Phase 3: Step 2 Text - Roll out stats to Step 2 scripts
- [x] Phase 4: Steps 3-4 Financial & Econometric - Roll out stats to Steps 3-4
- [x] Phase 5: README & Documentation - DCAS-compliant README
- [x] Phase 6: Pre-Submission Verification - Final validation

**Technical Remediation Phases (7-15):**
- [x] Phase 7: Critical Bug Fixes
- [x] Phase 8: Tech Debt Cleanup
- [x] Phase 9: Security Hardening
- [x] Phase 10: Performance Optimization
- [x] Phase 11: Testing Infrastructure
- [x] Phase 12: Data Quality & Observability
- [x] Phase 13: Script Refactoring
- [x] Phase 14: Dependency Management
- [x] Phase 15: Scaling Preparation
- [x] Phase 16: Critical Path Fixes

**Gap Closure Phases (17-24):**
- [x] Phase 17: Verification Reports
- [x] Phase 18: Complete Phase 13 Refactoring
- [x] Phase 19: Scaling Infrastructure & Testing Integration
- [x] Phase 20: Restore Root README Documentation
- [x] Phase 21: Fix Testing Infrastructure
- [x] Phase 22: Recreate Missing Script & Evidence
- [x] Phase 23: Core Tech Debt Cleanup
- [x] Phase 24: Complete Script Refactoring

**Post-Audit Validation (25-27):**
- [x] Phase 25: Execute Full Pipeline E2E Test
- [x] Phase 25.1: Fix Pipeline Scripts for Manual Execution (INSERTED)
- [x] Phase 26: Repository Cleanup & Archive Organization
- [x] Phase 27: Remove Symlink Mechanism

**v1.0 Summary:** 143 plans completed, 30 requirements mapped.

</details>

## v2.0 Phases (28-38)

### Phase 28: V2 Structure Setup ✓
**Goal**: Establish folder structure and naming conventions for V2 hypothesis testing scripts
**Depends on**: Phase 27 (v1.0 complete)
**Requirements**: STRUCT-01, STRUCT-02, STRUCT-03, STRUCT-04, STRUCT-05, STRUCT-06
**Success Criteria** (what must be TRUE):
  1. `2_Scripts/3_Financial_V2/` folder exists with README documenting purpose
  2. `2_Scripts/4_Econometric_V2/` folder exists with README documenting purpose
  3. `4_Outputs/3_Financial_V2/` folder accepts timestamped outputs from V2 scripts
  4. `3_Logs/3_Financial_V2/` and `3_Logs/4_Econometric_V2/` folders exist for logs
  5. V2 script naming follows existing convention: `{step}.{substep}_{Name}.py`
**Plans**: 3 plans in 2 waves

Plans:
- [x] 28-01-PLAN.md — Create Financial_V2 folder structure with comprehensive README
- [x] 28-02-PLAN.md — Create Econometric_V2 folder structure with comprehensive README
- [x] 28-03-PLAN.md — Create and run V2 structure validation script
**Completed**: 2026-02-04 — 3/3 plans executed, 6/6 requirements verified

### Phase 29: H1 Cash Holdings Variables ✓
**Goal**: Construct all dependent, moderator, and control variables for H1 (Cash Holdings) hypothesis
**Depends on**: Phase 28
**Requirements**: H1-01, H1-02, H1-03, H1-04, H1-05
**Success Criteria** (what must be TRUE):
  1. Cash Holdings DV (CHE/AT) computed for all firm-years in sample
  2. Firm Leverage moderator (DLTT+DLC)/AT merged from existing Compustat data
  3. Operating Cash Flow Volatility control (trailing 5-year StdDev OANCF/AT) computed
  4. Current Ratio control (ACT/LCT) and standard controls (Tobin's Q, ROA, Capex/AT, Dividend Payer, Firm Size) available
  5. Output saved to `4_Outputs/3_Financial_V2/` with stats.json documenting variable distributions
**Plans**: 1 plan in 1 wave

Plans:
- [x] 29-01-PLAN.md — Create 3.1_H1Variables.py script with all H1 variables and execute
**Completed**: 2026-02-04 — 1/1 plans executed, 5/5 requirements verified

### Phase 30: H2 Investment Efficiency Variables ✓
**Goal**: Construct all dependent and control variables for H2 (Investment Efficiency) hypothesis
**Depends on**: Phase 28
**Requirements**: H2-01, H2-02, H2-03, H2-04, H2-05, H2-06
**Success Criteria** (what must be TRUE):
  1. Overinvestment Dummy computed (Capex/Depreciation > 1.5 AND Sales Growth < industry-year median)
  2. Underinvestment Dummy computed (Capex/Depreciation < 0.75 AND Tobin's Q > 1.5)
  3. Efficiency Score DV computed (1 - % inefficient years over 5-year window)
  4. Alternative DV (residual from Delta-ROA regression) computed per Biddle et al. methodology
  5. Controls (Tobin's Q, Cash Flow Volatility, Industry CapEx Intensity, Analyst Dispersion, Firm Size, ROA, FCF, Earnings Volatility) available
**Plans**: 2 plans in 1 wave

Plans:
- [x] 30-01-PLAN.md — Create 3.2_H2Variables.py with investment efficiency variables and Biddle ROA residuals
- [x] 30-02-PLAN.md — (Gap Closure) Add analyst_dispersion via CCM CUSIP-GVKEY linking to IBES
**Completed**: 2026-02-05 — 2/2 plans executed, 6/6 requirements verified (gap closed)

### Phase 31: H3 Payout Policy Variables ✓
**Goal**: Construct all dependent and control variables for H3 (Payout Policy) hypothesis
**Depends on**: Phase 28
**Requirements**: H3-01, H3-02, H3-03, H3-04, H3-05
**Success Criteria** (what must be TRUE):
  1. Dividend Policy Stability DV computed (-StdDev of DPS changes over trailing 5 years)
  2. Payout Flexibility DV computed (% years with dividend change |Delta-DPS| > 5%)
  3. Controls (Earnings Volatility, FCF Growth, Firm Maturity) computed
  4. Standard controls (Firm Size, ROA, Tobin's Q, Cash Holdings) available from existing pipeline
  5. Output saved with stats.json documenting distributions for both DVs
**Plans**: 1 plan in 1 wave

Plans:
- [x] 31-01-PLAN.md — Create 3.3_H3Variables.py with payout policy variables and execute
**Completed**: 2026-02-05 — 1/1 plans executed, 4/4 requirements verified (H3-05 text measure merge in Phase 35)

### Phase 32: Econometric Infrastructure ✓
**Goal**: Build reusable econometric utilities for panel regressions with fixed effects, interaction terms, and robustness diagnostics
**Depends on**: Phase 28
**Requirements**: ECON-01, ECON-02, ECON-03, ECON-04, ECON-05, ECON-06, ECON-07
**Success Criteria** (what must be TRUE):
  1. Panel OLS module supports firm + year + industry (FF48) fixed effects
  2. Interaction term creation uses mean-centering to avoid multicollinearity
  3. Clustered standard errors (firm-level) implemented with double-clustering option
  4. 2SLS infrastructure supports manager's prior-firm vagueness and industry-peer average instruments
  5. Instrument validation includes first-stage F > 10 test and Hansen J overidentification test
  6. VIF < 5 multicollinearity diagnostics automatically computed
**Plans**: 2 plans in 1 wave

Plans:
- [x] 32-01-PLAN.md — Panel OLS, mean-centering, and diagnostics modules (ECON-01, ECON-02, ECON-03, ECON-06, ECON-07)
- [x] 32-02-PLAN.md — IV2SLS infrastructure and LaTeX table generation (ECON-04, ECON-05)
**Completed**: 2026-02-05 — 2/2 plans executed, 7/7 requirements verified

### Phase 33: H1 Cash Holdings Regression ✓
**Goal**: Run and validate OLS/2SLS regressions for H1 (Speech Uncertainty & Cash Holdings)
**Depends on**: Phase 29, Phase 32
**Requirements**: H1-06, H1-07, H1-08, H1-09, H1-10
**Success Criteria** (what must be TRUE):
  1. Speech uncertainty measures from Step 2 successfully merged with H1 variables
  2. OLS regression runs: CashHoldings_{t+1} ~ Uncertainty_t + Leverage_t + Uncertainty*Leverage + Controls + FEs
  3. Standard errors clustered at firm level
  4. Coefficient table reports beta1 > 0 (vagueness increases cash) and beta3 < 0 (leverage attenuates) with significance tests
  5. stats.json output includes R-squared, N, F-stat, and all coefficients
**Plans**: 1 plan in 1 wave

Plans:
- [x] 33-01-PLAN.md — Create 4.1_H1CashHoldingsRegression.py and execute 24 regressions (6 measures x 4 specs)
**Completed**: 2026-02-05 — 1/1 plans executed, 5/5 requirements verified

### Phase 34: H2 Investment Efficiency Regression ✓
**Goal**: Run and validate OLS/2SLS regressions for H2 (Speech Uncertainty & Investment Efficiency)
**Depends on**: Phase 30, Phase 32
**Requirements**: H2-07, H2-08, H2-09, H2-10
**Success Criteria** (what must be TRUE):
  1. Speech uncertainty measures from Step 2 successfully merged with H2 variables
  2. OLS regression runs: Efficiency_{t+1} ~ Uncertainty_t + Leverage_t + Uncertainty*Leverage + Controls + FEs
  3. Coefficient table reports beta1 < 0 (vagueness lowers efficiency) and beta3 > 0 (leverage improves efficiency)
  4. Both primary DV (Efficiency Score) and alternative DV (ROA residual) tested
  5. stats.json output includes all regression diagnostics
**Plans**: 1 plan in 1 wave

Plans:
- [x] 34-01-PLAN.md — Create 4.2_H2InvestmentEfficiencyRegression.py and execute 48 regressions (6 measures x 4 specs x 2 DVs)
**Completed**: 2026-02-05 — 1/1 plans executed, 4/4 requirements verified. Results: No support for H2 hypotheses (0/6 measures significant for both H2a and H2b).

### Phase 35: H3 Payout Policy Regression ✓
**Goal**: Run and validate OLS/2SLS regressions for H3 (Speech Uncertainty & Payout Policy)
**Depends on**: Phase 31, Phase 32
**Requirements**: H3-06, H3-07, H3-08, H3-09
**Success Criteria** (what must be TRUE):
  1. Speech uncertainty measures from Step 2 successfully merged with H3 variables
  2. Stability regression runs with expected signs (beta1 < 0, beta3 < 0)
  3. Flexibility regression runs with expected signs (beta1 > 0, beta3 > 0)
  4. Both DVs (Stability and Flexibility) tested independently
  5. stats.json output includes all regression diagnostics for both models
**Plans**: 1 plan in 1 wave

Plans:
- [x] 35-01-PLAN.md — Create 4.3_H3PayoutPolicyRegression.py and execute 48 regressions (6 measures x 4 specs x 2 DVs)
**Completed**: 2026-02-05 — 1/1 plans executed, 4/4 requirements verified. Results: H3a_stability 1/6 significant (CEO_Pres_Uncertainty_pct), H3b_stability 0/6; H3a_flexibility 1/6 (Manager_QA_Weak_Modal_pct), H3b_flexibility 0/6.

### Phase 36: Robustness Checks — CANCELLED
**Status**: CANCELLED (Hypotheses not supported)
**Reason**: All three core hypotheses (H1, H2, H3) showed minimal to no statistical support in primary regressions. Pursuing robustness checks for null results would not be scientifically meaningful.
**Requirements**: ROBUST-01 through ROBUST-07 — NOT PURSUED

### Phase 37: Identification Strategies — CANCELLED
**Status**: CANCELLED (Hypotheses not supported)
**Reason**: Identification strategies (manager FE, PSM, falsification tests) are designed to strengthen causal claims from supported hypotheses. With null results, these are not applicable.
**Requirements**: IDENT-01 through IDENT-03 — NOT PURSUED

### Phase 38: Publication Output — CANCELLED
**Status**: CANCELLED (Hypotheses not supported)
**Reason**: Publication tables for null results would document absence of predicted relationships. The regression outputs from Phases 33-35 already contain all necessary documentation of the null findings.
**Requirements**: PUB-01 through PUB-05 — NOT PURSUED

### Phase 39: Leverage Disciplines Managers and Lowers Speech Uncertainty ✓
**Goal**: Test reverse causal direction - does leverage discipline managers and lower speech uncertainty?
**Depends on**: Phase 32
**Requirements**: H4-01 through H4-10 (see phase documentation)
**Success Criteria** (what must be TRUE):
  1. H4 analysis dataset created with lagged leverage (t-1) and all 6 uncertainty measures
  2. 6 PanelOLS regressions executed with identical FE structure (Firm + Year + Industry)
  3. H4 hypothesis (β₁ < 0) tested with one-tailed p-values at α = 0.05
  4. Results document how many of 6 measures support the discipline hypothesis
  5. Coefficient table and H4_RESULTS.md generated for documentation
**Plans**: 2 plans in 2 waves

Plans:
- [x] 39-01-PLAN.md — H4 data preparation: merge sources, create lagged leverage, verify variables, VIF diagnostics
- [x] 39-02-PLAN.md — H4 regression execution: 6 PanelOLS regressions, one-tailed tests, results summary
**Completed**: 2026-02-05 — 2/2 plans executed, 10/10 requirements verified. Results: H4 partially supported (3/6 measures significant). Manager speech measures show debt discipline effect; CEO measures do not.

### Phase 40: H5 Speech Uncertainty Predicts Financial Outcome Uncertainty
**Goal**: Test whether higher speech uncertainty predicts uncertainty (volatility) of financial outcomes of the firm
**Depends on**: Phase 39
**Requirements**: H5-01 through H5-10 (to be defined)
**Success Criteria** (what must be TRUE):
  1. [To be planned]
**Plans**: 0 plans

Plans:
- [ ] TBD (run /gsd-plan-phase 40 to break down)

**Details:**
This hypothesis examines whether managerial speech uncertainty (potentially measured via Shannon's entropy or existing vagueness measures) predicts the uncertainty/volatility of financial outcomes such as earnings volatility, return volatility, or cash flow volatility. Unlike H1-H3 which tested level effects, H5 tests variance-to-variance relationships.

---

## v2.0 Hypothesis Testing Summary

**Conclusion**: The empirical analysis found no consistent support for the hypothesized relationships between managerial speech uncertainty and corporate financial policies.

### H1: Cash Holdings
- **H1a** (vagueness → higher cash): 0/6 uncertainty measures significant
- **H1b** (leverage attenuates effect): 1/6 measures significant (Manager_QA_Weak_Modal_pct only)

### H2: Investment Efficiency
- **H2a** (vagueness → lower efficiency): 0/6 uncertainty measures significant
- **H2b** (leverage improves efficiency): 0/6 measures significant

### H3: Payout Policy
- **H3a_stability** (vagueness → less stability): 1/6 measures significant (CEO_Pres_Uncertainty_pct)
- **H3b_stability** (leverage → more stability): 0/6 measures significant
- **H3a_flexibility** (vagueness → more flexibility): 1/6 measures significant (Manager_QA_Weak_Modal_pct)
- **H3b_flexibility** (leverage → less flexibility): 0/6 measures significant

**Interpretation**: The speech uncertainty measures derived from earnings call transcripts do not systematically predict cash holdings, investment efficiency, or payout policy stability as theorized. This null result is itself a finding that contributes to the literature by documenting what does NOT work.

## Progress

**v2.0 Execution Order:**
Phase 28 (Structure) → Phases 29-31 (Variables, parallelized) → Phase 32 (Infrastructure) → Phases 33-35 (Regressions, parallelized) → [Phases 36-38 CANCELLED]

| Phase | Name | Plans Complete | Status | Completed |
|-------|------|----------------|--------|-----------|
| 28 | V2 Structure Setup | 3/3 | COMPLETE | 2026-02-04 |
| 29 | H1 Cash Holdings Variables | 1/1 | COMPLETE | 2026-02-04 |
| 30 | H2 Investment Efficiency Variables | 2/2 | COMPLETE | 2026-02-05 |
| 31 | H3 Payout Policy Variables | 1/1 | COMPLETE | 2026-02-05 |
| 32 | Econometric Infrastructure | 2/2 | COMPLETE | 2026-02-05 |
| 33 | H1 Cash Holdings Regression | 1/1 | COMPLETE | 2026-02-05 |
| 34 | H2 Investment Efficiency Regression | 1/1 | COMPLETE | 2026-02-05 |
| 35 | H3 Payout Policy Regression | 1/1 | COMPLETE | 2026-02-05 |
| 36 | Robustness Checks | — | CANCELLED | — |
| 37 | Identification Strategies | — | CANCELLED | — |
| 38 | Publication Output | — | CANCELLED | — |
| 39 | Leverage Disciplines Managers and Lowers Speech Uncertainty | 2/2 | COMPLETE | 2026-02-05 |
| 40 | H5 Speech Uncertainty Predicts Financial Outcome Uncertainty | 0/0 | PLANNED | — |

**v2.0 Summary:** 9/9 active phases completed, 15 plans executed, 50 requirements verified. 3 phases cancelled due to null hypothesis results. Phase 40 planned with variance-to-variance hypothesis.

## Requirement Coverage

v2.0 requirements by status:

| Category | Requirements | Phase | Status |
|----------|--------------|-------|--------|
| V2 Structure | STRUCT-01 through STRUCT-06 | Phase 28 | ✓ COMPLETE |
| H1 Variables | H1-01 through H1-05 | Phase 29 | ✓ COMPLETE |
| H2 Variables | H2-01 through H2-06 | Phase 30 | ✓ COMPLETE |
| H3 Variables | H3-01 through H3-05 | Phase 31 | ✓ COMPLETE |
| Econometrics | ECON-01 through ECON-07 | Phase 32 | ✓ COMPLETE |
| H1 Regression | H1-06 through H1-10 | Phase 33 | ✓ COMPLETE |
| H2 Regression | H2-07 through H2-10 | Phase 34 | ✓ COMPLETE |
| H3 Regression | H3-06 through H3-09 | Phase 35 | ✓ COMPLETE |
| Robustness | ROBUST-01 through ROBUST-07 | Phase 36 | ✗ NOT PURSUED |
| Identification | IDENT-01 through IDENT-03 | Phase 37 | ✗ NOT PURSUED |
| Publication | PUB-01 through PUB-05 | Phase 38 | ✗ NOT PURSUED |
| H4 Variables | H4-01 through H4-05 | Phase 39 | ✓ COMPLETE |
| H4 Regression | H4-06 through H4-10 | Phase 39 | ✓ COMPLETE |
| H5 Variables | H5-01 through H5-05 | Phase 40 | ○ PLANNED |
| H5 Regression | H5-06 through H5-10 | Phase 40 | ○ PLANNED |

**Phase 39 Plan Breakdown:**
| Plan | Wave | Objective | Requirements |
|------|------|-----------|--------------|
| 39-01 | 1 | H4 Data Preparation & VIF Diagnostics | H4-01 through H4-05 |
| 39-02 | 2 | H4 Regression Execution & Results | H4-06 through H4-10 |

**Coverage:** 50/55 requirements completed (91%); 15 requirements not pursued; 10 requirements planned for Phase 40

---
*Roadmap created: 2026-01-22 (v1.0)*
*v1.0 completed: 2026-01-30 (27 phases, 143 plans)*
*v2.0 roadmap created: 2026-02-04 (11 phases, 55 requirements)*
