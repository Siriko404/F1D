# Roadmap: F1D Data Pipeline

## Overview

This roadmap extends the existing F1D data processing pipeline with hypothesis testing capabilities for empirical finance research. Building on the v1.0 foundation (27 phases, 143 plans) that established observability and documentation, v2.0 implements three empirical hypotheses: H1 (Speech Uncertainty & Cash Holdings), H2 (Speech Uncertainty & Investment Efficiency), and H3 (Speech Uncertainty & Payout Policy). The work leverages existing sample construction and text measures from v1.0 while adding new variable construction and panel econometric regressions with fixed effects, interaction terms, and robustness checks.

**Milestone:** v2.0 Hypothesis Testing Suite
**Phases:** 28-38 (11 phases, continuing from v1.0 Phase 27)
**Requirements:** 55 total across 8 categories

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

### Phase 34: H2 Investment Efficiency Regression
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
- [ ] 34-01-PLAN.md — Create 4.2_H2InvestmentEfficiencyRegression.py and execute 48 regressions (6 measures x 4 specs x 2 DVs)

### Phase 35: H3 Payout Policy Regression
**Goal**: Run and validate OLS/2SLS regressions for H3 (Speech Uncertainty & Payout Policy)
**Depends on**: Phase 31, Phase 32
**Requirements**: H3-06, H3-07, H3-08, H3-09
**Success Criteria** (what must be TRUE):
  1. Speech uncertainty measures from Step 2 successfully merged with H3 variables
  2. Stability regression runs with expected signs (beta1 < 0, beta3 < 0)
  3. Flexibility regression runs with expected signs (beta1 > 0, beta3 > 0)
  4. Both DVs (Stability and Flexibility) tested independently
  5. stats.json output includes all regression diagnostics for both models
**Plans**: TBD

### Phase 36: Robustness Checks
**Goal**: Validate hypothesis results across subsamples and alternative specifications
**Depends on**: Phase 33, Phase 34, Phase 35
**Requirements**: ROBUST-01, ROBUST-02, ROBUST-03, ROBUST-04, ROBUST-05, ROBUST-06, ROBUST-07
**Success Criteria** (what must be TRUE):
  1. Leverage subsample analysis (above/below median) shows coefficient pattern consistency
  2. Growth subsample (Tobin's Q above/below 1.5) shows expected moderation effects
  3. FCF subsample analysis completed
  4. Pre/post-2008 time period splits show temporal stability
  5. Alternative uncertainty measure (weak modals only) replicates main findings
  6. Crisis year exclusion (2008-2009) sensitivity documented
  7. Reverse causality check (regress uncertainty on lagged outcome) shows no evidence of reverse causation
**Plans**: TBD

### Phase 37: Identification Strategies
**Goal**: Address endogeneity concerns with manager fixed effects, propensity score matching, and falsification tests
**Depends on**: Phase 36
**Requirements**: IDENT-01, IDENT-02, IDENT-03
**Success Criteria** (what must be TRUE):
  1. Manager fixed effects regression runs with sufficient within-manager variation (mover check)
  2. Propensity score matching for high/low vagueness firms shows consistent treatment effects
  3. Falsification test on placebo DV (e.g., inventory/assets for H1) shows null effect
**Plans**: TBD

### Phase 38: Publication Output
**Goal**: Generate publication-ready tables and economic significance calculations
**Depends on**: Phase 37
**Requirements**: PUB-01, PUB-02, PUB-03, PUB-04, PUB-05
**Success Criteria** (what must be TRUE):
  1. Coefficient tables include beta, SE, t-stat, p-value, R-squared, N for all hypotheses
  2. LaTeX-formatted regression tables ready for paper submission
  3. Economic significance calculated (1-SD change in uncertainty effect on outcomes)
  4. Marginal effects reported at mean leverage for interaction terms
  5. Complete stats.json with all regression diagnostics for replication
**Plans**: TBD

## Progress

**v2.0 Execution Order:**
Phase 28 (Structure) → Phases 29-31 (Variables, can parallelize) → Phase 32 (Infrastructure) → Phases 33-35 (Regressions, can parallelize) → Phase 36 (Robustness) → Phase 37 (Identification) → Phase 38 (Publication)

| Phase | Name | Plans Complete | Status | Completed |
|-------|------|----------------|--------|-----------|
| 28 | V2 Structure Setup | 3/3 | COMPLETE | 2026-02-04 |
| 29 | H1 Cash Holdings Variables | 1/1 | COMPLETE | 2026-02-04 |
| 30 | H2 Investment Efficiency Variables | 2/2 | COMPLETE | 2026-02-05 |
| 31 | H3 Payout Policy Variables | 1/1 | COMPLETE | 2026-02-05 |
| 32 | Econometric Infrastructure | 2/2 | COMPLETE | 2026-02-05 |
| 33 | H1 Cash Holdings Regression | 1/1 | COMPLETE | 2026-02-05 |
| 34 | H2 Investment Efficiency Regression | 0/TBD | PLANNED | — |
| 35 | H3 Payout Policy Regression | 0/TBD | PLANNED | — |
| 36 | Robustness Checks | 0/TBD | PLANNED | — |
| 37 | Identification Strategies | 0/TBD | PLANNED | — |
| 38 | Publication Output | 0/TBD | PLANNED | — |

## Requirement Coverage

All 55 v2.0 requirements mapped to phases:

| Category | Requirements | Phase |
|----------|--------------|-------|
| V2 Structure | STRUCT-01, STRUCT-02, STRUCT-03, STRUCT-04, STRUCT-05, STRUCT-06 | Phase 28 |
| H1 Variables | H1-01, H1-02, H1-03, H1-04, H1-05 | Phase 29 |
| H2 Variables | H2-01, H2-02, H2-03, H2-04, H2-05, H2-06 | Phase 30 |
| H3 Variables | H3-01, H3-02, H3-03, H3-04, H3-05 | Phase 31 |
| Econometrics | ECON-01, ECON-02, ECON-03, ECON-04, ECON-05, ECON-06, ECON-07 | Phase 32 |
| H1 Regression | H1-06, H1-07, H1-08, H1-09, H1-10 | Phase 33 |
| H2 Regression | H2-07, H2-08, H2-09, H2-10 | Phase 34 |
| H3 Regression | H3-06, H3-07, H3-08, H3-09 | Phase 35 |
| Robustness | ROBUST-01, ROBUST-02, ROBUST-03, ROBUST-04, ROBUST-05, ROBUST-06, ROBUST-07 | Phase 36 |
| Identification | IDENT-01, IDENT-02, IDENT-03 | Phase 37 |
| Publication | PUB-01, PUB-02, PUB-03, PUB-04, PUB-05 | Phase 38 |

**Coverage:** 55/55 requirements mapped (100%)

---
*Roadmap created: 2026-01-22 (v1.0)*
*v1.0 completed: 2026-01-30 (27 phases, 143 plans)*
*v2.0 roadmap created: 2026-02-04 (11 phases, 55 requirements)*
