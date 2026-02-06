# Roadmap: F1D Data Pipeline

## Overview

This roadmap extends the existing F1D data processing pipeline with hypothesis testing capabilities for empirical finance research. Building on the v1.0 foundation (27 phases, 143 plans) that established observability and documentation, v2.0 implements three empirical hypotheses: H1 (Speech Uncertainty & Cash Holdings), H2 (Speech Uncertainty & Investment Efficiency), and H3 (Speech Uncertainty & Payout Policy). The work leverages existing sample construction and text measures from v1.0 while adding new variable construction and panel econometric regressions with fixed effects, interaction terms, and robustness checks.

**Milestone:** v2.0 Hypothesis Testing Suite — ACTIVE
**Phases:** 28-38 completed/cancelled; Phase 40 complete (H5 null results); Phase 41 complete (Hypothesis Suite Discovery); Phases 42+ planned (H6-H10 selected hypotheses)
**Requirements:** 50/105 completed (15 requirements in cancelled phases not pursued; 50 new requirements from H6-H10)

**v2.0 Summary:** H1-H3 hypotheses showed null results. Phases 36-38 cancelled. Phase 40 (H5) complete with null results. Phase 41 complete: selected 5 novel hypotheses (H6-H10) for Phases 42+ testing.

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
**Status**: COMPLETE
**Results**: H3a_stability 1/6 significant (CEO_Pres_Uncertainty_pct); H3b_stability 0/6; H3a_flexibility 1/6 (Manager_QA_Weak_Modal_pct); H3b_flexibility 0/6
**Completed**: 2026-02-05 — 1/1 plans executed

Plans:
- [x] 35-01-PLAN.md — Create 4.3_H3PayoutPolicyRegression.py and execute 48 regressions

### Phase 36: Robustness Checks — CANCELLED
**Status**: CANCELLED (H1-H3 hypotheses not supported)
**Reason**: All three core hypotheses showed minimal to no statistical support. Pursuing robustness checks for null results would not be scientifically meaningful.
**Requirements**: ROBUST-01 through ROBUST-07 — NOT PURSUED

### Phase 37: Identification Strategies — CANCELLED
**Status**: CANCELLED (H1-H3 hypotheses not supported)
**Reason**: Identification strategies are designed to strengthen causal claims from supported hypotheses. With null results, these are not applicable.
**Requirements**: IDENT-01 through IDENT-03 — NOT PURSUED

### Phase 38: Publication Output — CANCELLED
**Status**: CANCELLED (H1-H3 hypotheses not supported)
**Reason**: Publication tables for null results would document absence of predicted relationships. The regression outputs from Phases 33-35 already contain all necessary documentation.
**Requirements**: PUB-01 through PUB-05 — NOT PURSUED

---

## v2.0 New Hypotheses (Post Null Results)

### Phase 40: H5 Speech Uncertainty Predicts Analyst Forecast Dispersion ✓
**Goal**: Test whether hedging language (weak modal verbs) predicts analyst disagreement beyond what general uncertainty words predict
**Depends on**: Phase 32 (Econometric Infrastructure)
**Requirements**: H5-01 through H5-10
**Status**: COMPLETE — 2 plans in 2 waves executed
**Results**: H5 NOT SUPPORTED — Weak Modal measures do not predict dispersion with Firm+Year FE. Gap significant in pooled OLS but not with Firm FE (between-firm vs within-firm effect).
**Completed**: 2026-02-05 — 2/2 plans executed, 9/9 must-haves verified

**Success Criteria** (what must be TRUE):
  1. H5 analysis dataset created with forward dispersion (t+1) and all uncertainty measures ✓
  2. Primary regression tests Weak_Modal effect controlling for Uncertainty (incremental contribution) ✓
  3. Secondary regression tests Q&A-Presentation gap as novel predictor ✓
  4. Robustness checks without lagged DV, without NUMEST, CEO-only measures ✓
  5. Results document whether hedging adds beyond general uncertainty ✓
**Plans**: 2 plans in 2 waves

Plans:
- [x] 40-01-PLAN.md — Create 3.5_H5Variables.py with refined analyst dispersion and controls
- [x] 40-02-PLAN.md — Create 4.5_H5DispersionRegression.py with primary, gap, and robustness models

**Literature Position:**
- General uncertainty → dispersion is ESTABLISHED (Loughran & McDonald 2011, Price et al. 2012)
- Novel contribution tested: Does **hedging language** (weak modals: may/might/could) add beyond general uncertainty?
- Secondary contribution tested: Does **spontaneous-scripted gap** (Q&A - Presentation) reveal hidden uncertainty?

**Key Design Decisions (from CONTEXT.md):**
- DV: Analyst Dispersion = STDEV / |MEANEST|, NUMEST ≥ 3, |MEANEST| ≥ 0.05
- Timing: Speech_t → Dispersion_{t+1} (next quarter)
- Primary IV: Manager_QA_Weak_Modal_pct (novel)
- Control for established effect: Manager_QA_Uncertainty_pct
- FE: Firm + Year; SE: Clustered at firm level

**H5 Results Summary:**
- H5-A (Weak Modal): NOT SUPPORTED in primary spec (Firm + Year FE). Weak Modal coefficients insignificant.
- H5-B (Gap): MIXED. Significant in pooled OLS (beta=0.014, p<0.001) but insignificant with Firm FE.
- Interpretation: Speech-dispersion relationship driven by firm heterogeneity, not within-firm causal effects.
- Sample: 258,560 observations (primary spec), 2,027 firms, 2002-2018, R²_within=0.079

### Phase 41: Hypothesis Suite Discovery — Novel Hypotheses with Data-Feasibility & Statistical Confidence
**Goal**: Conduct an extremely thorough and deep literature review to identify untested hypotheses that are: (1) feasible with currently available data, (2) novel with true research gaps, and (3) have high confidence of statistically significant results
**Depends on**: Phase 40 (H5 Analyst Dispersion) — COMPLETE
**Status**: COMPLETE — 4 plans in 4 waves executed
**Results:** Selected 5 novel hypotheses (H6-H10) with complete specifications for Phase 42+ development
**Completed**: 2026-02-06 — 4/4 plans executed, hypothesis suite selected

**Success Criteria** (what must be TRUE):
  1. Comprehensive literature review completed across relevant domains (accounting, finance, linguistics, psychology) ✓
  2. Data feasibility matrix created mapping all available data sources to potential hypothesis variables ✓
  3. Novel research gaps identified with no prior published tests ✓
  4. Statistical power analysis conducted to ensure high confidence in significant results ✓
  5. Hypothesis suite selected and formally specified ✓
**Plans**: 4 plans in 4 waves

Plans:
- [x] 41-01-PLAN.md — Data inventory: 11 sources, 1,785 text measures, merge feasibility matrix
- [x] 41-02-PLAN.md — Literature review: PRISMA 2020, evidence matrix, 10 novel hypotheses
- [x] 41-03-PLAN.md — Statistical power analysis: all hypotheses >80% power for meaningful effects
- [x] 41-04-PLAN.md — Hypothesis suite selection: H6-H10 selected with full specifications

**Details:**
Discovery phase completed with 4 sequential plans: (01) Data inventory documenting 11 input sources and 1,785 text measures; (02) Literature review using PRISMA 2020 methodology identifying 10 novel hypotheses; (03) Statistical power analysis confirming all hypotheses have adequate power; (04) Hypothesis suite selection choosing 5 hypotheses (H6-H10) for Phase 42+ development.

**Selected Hypotheses (H6-H10):**
- **H6:** Managerial Hedging and M&A Targeting (weak modals -> M&A likelihood/premium)
- **H7:** CEO Vagueness and Forced Turnover Risk (uncertainty -> forced turnover)
- **H8:** Speech Clarity and Executive Compensation (uncertainty -> total compensation/PPS)
- **H9:** Uncertainty Gap and Future Stock Returns (QA-Pres gap -> abnormal returns)
- **H10:** Language Complexity and Analyst Forecast Accuracy (complexity -> forecast error)

### Phase 42: H6 SEC Scrutiny (CCCL) Reduces Manager Speech Uncertainty ✓
**Goal**: Test whether SEC scrutiny through Conference Call Comment Letters (CCCL) exposure causes managers to speak with less uncertainty
**Depends on**: Phase 41 (Hypothesis Suite Discovery)
**Requirements**: H6-01 through H6-10
**Status**: COMPLETE — 2 plans in 2 waves executed
**Results**: H6-A NOT SUPPORTED (0/6 measures significant), H6-B NOT SUPPORTED (mixed), H6-C NOT SUPPORTED (p=0.22). Pre-trends test FAILED (future CCCL significant).
**Completed**: 2026-02-06 — 2/2 plans executed, 11/12 must-haves verified

**Success Criteria** (what must be TRUE):
  1. CCCL data from inputs folder successfully loaded and processed ✓
  2. Industry-level CCCL shift-share computed (how much each industry received comment letters) ✓
  3. Firm-level CCCL exposure computed (shift-share x firm size proxy: sales or market cap) ✓
  4. Regression tests SEC scrutiny -> reduced speech uncertainty measures ✓
  5. Results document whether larger/more exposed firms hedge less in speech ✓
**Plans**: 2 plans in 2 waves

Plans:
- [x] 42-01-PLAN.md — Create 3.6_H6Variables.py merging CCCL instrument with speech measures
- [x] 42-02-PLAN.md — Create 4.6_H6CCCLRegression.py with FDR correction and pre-trends

**Details:**
Novel hypothesis: SEC scrutiny through audit letters (CCCL = Conference Call Comment Letters) makes manager speech LESS uncertain. Identification strategy uses shift-share design: industry CCCL exposure x firm size (sales/market cap). Larger firms are more exposed to scrutiny. Data available in 1_Inputs folder. This reverses the typical "uncertainty is bad" framing — here scrutiny disciplines vague speech.

**H6 Results Summary:**
- H6-A (CCCL reduces uncertainty): NOT SUPPORTED (0/6 measures FDR-significant)
- H6-B (Stronger in Q&A than Pres): NOT SUPPORTED (mixed evidence)
- H6-C (CCCL reduces gap): NOT SUPPORTED (p=0.2186)
- Pre-trends: FAILED (future CCCL significant at p<0.05)
- Sample: 22,273 firm-year observations (2,357 firms, 2006-2018)

### Phase 42-A: H6 Managerial Hedging and M&A Targeting — MOVED
**Status**: The original "H6 Managerial Hedging and M&A Targeting" hypothesis from Phase 41 discovery has been moved to a future phase. Phase 42 was used for the CCCL SEC Scrutiny hypothesis instead.
**Note**: Phase 42 in the ROADMAP was originally planned for M&A targeting, but the CCCL hypothesis was prioritized and executed. The M&A targeting hypothesis remains available for future testing.

---

### Phase 43: H7 CEO Vagueness and Forced Turnover Risk
**Goal**: Test whether managerial speech uncertainty/vagueness in Q&A predicts higher probability of forced CEO turnover
**Depends on**: Phase 41 (Hypothesis Suite Discovery)
**Requirements**: H7-01 through H7-10
**Status**: NOT PLANNED YET
**Success Criteria** (what must be TRUE):
  1. H7 analysis dataset created with CEO turnover dummy and uncertainty measures
  2. Logistic regression tests uncertainty -> forced turnover likelihood
  3. Survival analysis alternative for time-to-turnover
  4. Controls for performance, tenure, firm characteristics
  5. Results document whether boards discipline unclear communicators
**Plans**: TBD (run /gsd:plan-phase 43 to break down)

Plans:
- [ ] TBD (run /gsd:plan-phase 43 to break down)

**Details:**
Novel hypothesis: Boards discipline unclear communicators; vagueness signals problems or incompetence. Data: CEO dismissal (1,059 events 2002-2018) + text measures. IV: CEO_QA_Uncertainty_pct. DV: Forced turnover dummy. Methodology: Logistic regression or Cox proportional hazards.

---

### Phase 44: H8 Speech Clarity and Executive Compensation
**Goal**: Test whether CEO speech clarity (lower uncertainty) predicts higher total compensation and pay-for-performance sensitivity
**Depends on**: Phase 41 (Hypothesis Suite Discovery)
**Requirements**: H8-01 through H8-10
**Status**: NOT PLANNED YET
**Success Criteria** (what must be TRUE):
  1. H8 analysis dataset created with compensation data and uncertainty measures
  2. OLS regression tests uncertainty -> total compensation
  3. OLS regression with interaction tests uncertainty -> pay-for-performance sensitivity
  4. Controls for performance, firm characteristics, governance
  5. Results document whether boards price communication quality into CEO pay
**Plans**: TBD (run /gsd:plan-phase 44 to break down)

Plans:
- [ ] TBD (run /gsd:plan-phase 44 to break down)

**Details:**
Novel hypothesis: Clear communication valued by boards; unclear speech reduces perceived compensation. Data: Execucomp (370K obs, 4,170 firms) + text measures. IV: CEO_QA_Uncertainty_pct (inverse clarity). DV: Total compensation (tdc1), pay-for-performance sensitivity.

---

### Phase 45: H9 Uncertainty Gap and Future Stock Returns
**Goal**: Test whether Q&A-Presentation uncertainty gap predicts future abnormal stock returns
**Depends on**: Phase 41 (Hypothesis Suite Discovery)
**Requirements**: H9-01 through H9-10
**Status**: NOT PLANNED YET
**Success Criteria** (what must be TRUE):
  1. H9 analysis dataset created with uncertainty gap and future returns
  2. OLS regression tests gap -> future abnormal returns (multiple horizons)
  3. Portfolio analysis of high-gap vs. low-gap firms
  4. Controls for prior returns, volatility, earnings surprise
  5. Results document whether inconsistency predicts returns
**Plans**: TBD (run /gsd:plan-phase 45 to break down)

Plans:
- [ ] TBD (run /gsd:plan-phase 45 to break down)

**Details:**
Novel hypothesis: Large gap (QA >> Pres) = scripted + unprepared = bad signal to markets. Data: CRSP DSF (1999-2022) + text measures. IV: uncertainty_gap = QA_Uncertainty - Pres_Uncertainty. DV: Future abnormal returns (3-day, 1-month, 1-quarter). Large sample: 113K observations.

---

### Phase 46: H10 Language Complexity and Analyst Forecast Accuracy
**Goal**: Test whether earnings call complexity predicts higher analyst forecast error (lower accuracy)
**Depends on**: Phase 41 (Hypothesis Suite Discovery)
**Requirements**: H10-01 through H10-10
**Status**: NOT PLANNED YET
**Success Criteria** (what must be TRUE):
  1. H10 analysis dataset created with complexity measures and forecast error
  2. OLS regression tests complexity -> forecast error
  3. Quantile regression for different accuracy levels
  4. Controls for firm characteristics, forecast environment
  5. Results document whether complexity confuses analysts or signals competence
**Plans**: TBD (run /gsd:plan-phase 46 to break down)

Plans:
- [ ] TBD (run /gsd:plan-phase 46 to break down)

**Details:**
Novel hypothesis: Complex speech confuses analysts OR signals sophisticated operations. Data: IBES (264K complete cases verified in H5) + text measures. IV: Complexity score (Fog index, word length). DV: Forecast error = |MEANEST - ACTUAL| / |ACTUAL|. Direction ambiguous.

---

## Reserved Phases (Future Extension)

### Phase 50: SEC Scrutiny (CCCL) Reduces Manager Speech Uncertainty
**Goal**: Test whether SEC scrutiny through Conference Call Comment Letters (CCCL) exposure causes managers to speak with less uncertainty
**Depends on**: Phase 41
**Requirements**: H50-01 through H50-10 (TBD)
**Status**: NOT PLANNED YET
**Success Criteria** (what must be TRUE):
  1. CCCL data from inputs folder successfully loaded and processed
  2. Industry-level CCCL shift-share computed (how much each industry received comment letters)
  3. Firm-level CCCL exposure computed (shift-share x firm size proxy: sales or market cap)
  4. Regression tests SEC scrutiny -> reduced speech uncertainty measures
  5. Results document whether larger/more exposed firms hedge less in speech
**Plans**: TBD (run /gsd:plan-phase 50 to break down)

Plans:
- [ ] TBD (run /gsd:plan-phase 50 to break down)

**Details:**
Novel hypothesis: SEC scrutiny through audit letters (CCCL = Conference Call Comment Letters) makes manager speech LESS uncertain. Identification strategy uses shift-share design: industry CCCL exposure x firm size (sales/market cap). Larger firms are more exposed to scrutiny. Data available in 1_Inputs folder. This reverses the typical "uncertainty is bad" framing — here scrutiny disciplines vague speech.

### Phase 51: Uncertainty Dynamics Predictors
**Goal**: Test whether changes in uncertainty (velocity, acceleration, jerk) in manager and analyst speech have predictive power for market outcomes and information processing
**Depends on**: Phase 42
**Requirements**: H43-01 through H43-10 (TBD)
**Status**: NOT PLANNED — 0 plans in 0 waves
**Success Criteria** (what must be TRUE):
  1. Temporal derivatives of uncertainty measures computed (velocity, acceleration, jerk)
  2. Manager uncertainty dynamics compared to analyst uncertainty dynamics
  3. Regression models test predictive power of uncertainty changes vs. levels
  4. Market reaction outcomes (returns, volatility, dispersion) linked to uncertainty dynamics
  5. Results document whether rate of change contains information beyond uncertainty levels
**Plans**: 0 plans (run /gsd-plan-phase 43 to break down)

Plans:
- [ ] 43-01-PLAN.md — TBD (run /gsd-plan-phase 43 to break down)

**Details:**
Novel hypothesis exploring dynamic properties of speech uncertainty. Instead of testing uncertainty levels, test whether the *rate of change* in uncertainty (velocity), *acceleration* in uncertainty, and *jerk* (rate of change of acceleration) predict market outcomes. Compare manager vs. analyst uncertainty dynamics — do they converge/diverge predictably? Does rapid increase in uncertainty signal information arrival? Uses existing speech measures from Step 2 outputs with temporal differencing.

## Progress

**v2.0 Execution Summary:**
- Phases 28-35: Completed (H1-H3 variable construction and regressions)
- Phases 36-38: Cancelled (null results make robustness/identification/publication scientifically inappropriate)
- Phase 40: COMPLETE — H5 hypothesis null results (weak modal does not predict dispersion with Firm FE)
- Phase 41: COMPLETE — Hypothesis Suite Discovery (selected 5 novel hypotheses: H6-H10)
- Phases 42-46: NOT PLANNED YET — H6-H10 hypothesis testing phases
- Phase 50: RESERVED — SEC Scrutiny (CCCL) hypothesis (future extension)
- Phase 51: RESERVED — Uncertainty Dynamics (future extension)

**v2.0 Hypothesis Testing Results:**

| Hypothesis | Prediction | Result | Significant Measures |
|------------|------------|--------|---------------------|
| H1a | Uncertainty → ↑ Cash | NOT SUPPORTED | 0/6 |
| H1b | Leverage attenuates H1a | WEAK | 1/6 (QA_Weak_Modal) |
| H2a | Uncertainty → ↓ Efficiency | NOT SUPPORTED | 0/6 |
| H2b | Leverage improves H2a | NOT SUPPORTED | 0/6 |
| H3a | Uncertainty → ↓ Stability | WEAK | 1/6 (CEO_Pres_Uncertainty) |
| H3b | Leverage → ↑ Stability | NOT SUPPORTED | 0/6 |
| H5a | Weak Modal → ↑ Dispersion (controlling for Uncertainty) | NOT SUPPORTED | 0/6 (primary spec) |
| H5b | Uncertainty Gap → ↑ Dispersion | MIXED | Sig. pooled OLS, insig. Firm FE |
| H6a | SEC Scrutiny (CCCL) → ↓ Uncertainty | NOT SUPPORTED | 0/6 (FDR-corrected) |
| H6b | CCCL effect stronger in Q&A than Pres | NOT SUPPORTED | Mixed evidence |
| H6c | CCCL → ↓ Uncertainty Gap | NOT SUPPORTED | p=0.2186 |

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
| 40 | H5 Speech → Analyst Dispersion | 2/2 | COMPLETE | 2026-02-05 |
| 41 | Hypothesis Suite Discovery | 4/4 | COMPLETE | 2026-02-06 |
| 42 | H6 SEC Scrutiny (CCCL) → ↓ Uncertainty | 2/2 | COMPLETE | 2026-02-06 |
| 43 | H7 Uncertainty → CEO Turnover | 0/TBD | NOT PLANNED | — |
| 44 | H8 Speech Clarity → Compensation | 0/TBD | NOT PLANNED | — |
| 45 | H9 Uncertainty Gap → Returns | 0/TBD | NOT PLANNED | — |
| 46 | H10 Complexity → Forecast Accuracy | 0/TBD | NOT PLANNED | — |
| 50 | Managerial Hedging → M&A Targeting | 0/TBD | RESERVED | — |
| 51 | Uncertainty Dynamics Predictors | 0/TBD | RESERVED | — |

## Requirement Coverage

v2.0 requirements by status:

| Category | Requirements | Phase | Status |
|----------|--------------|-------|--------|
| V2 Structure | STRUCT-01 through STRUCT-06 | Phase 28 | COMPLETE |
| H1 Variables | H1-01 through H1-05 | Phase 29 | COMPLETE |
| H2 Variables | H2-01 through H2-06 | Phase 30 | COMPLETE |
| H3 Variables | H3-01 through H3-05 | Phase 31 | COMPLETE |
| Econometrics | ECON-01 through ECON-07 | Phase 32 | COMPLETE |
| H1 Regression | H1-06 through H1-10 | Phase 33 | COMPLETE |
| H2 Regression | H2-07 through H2-10 | Phase 34 | COMPLETE |
| H3 Regression | H3-06 through H3-09 | Phase 35 | COMPLETE |
| Robustness | ROBUST-01 through ROBUST-07 | Phase 36 | NOT PURSUED |
| Identification | IDENT-01 through IDENT-03 | Phase 37 | NOT PURSUED |
| Publication | PUB-01 through PUB-05 | Phase 38 | NOT PURSUED |
| H5 Hypothesis | H5-01 through H5-10 | Phase 40 | COMPLETE |
| H6 Hypothesis | H6-01 through H6-10 | Phase 42 | COMPLETE |
| H7 Hypothesis | H7-01 through H7-10 | Phase 43 | NOT PLANNED |
| H8 Hypothesis | H8-01 through H8-10 | Phase 44 | NOT PLANNED |
| H9 Hypothesis | H9-01 through H9-10 | Phase 45 | NOT PLANNED |
| H10 Hypothesis | H10-01 through H10-10 | Phase 46 | NOT PLANNED |

**Coverage:** 60/105 requirements completed (57%); 15 requirements not pursued (cancelled phases); 40 new requirements from H7-H10 (Phases 43-46)

---
*Roadmap created: 2026-01-22 (v1.0)*
*v1.0 completed: 2026-01-30 (27 phases, 143 plans)*
*v2.0 roadmap created: 2026-02-04 (11 phases, 55 requirements)*
*v2.0 updated: 2026-02-06 (H1-H3 null results; Phases 36-38 cancelled; Phase 40 complete with null results; Phase 41 complete with H6-H10 selected)*
