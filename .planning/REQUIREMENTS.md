# Requirements: F1D Hypothesis Testing Pipeline

**Defined:** 2026-02-04
**Core Value:** Every hypothesis test must produce verifiable, reproducible regression results exactly as specified in the methodology

## v2.0 Requirements

Requirements for hypothesis testing implementation. V2 extends existing pipeline with separate scripts in dedicated folders.

**Key Constraints:**
- Use existing sample (firms, time period) from v1.0 implementation
- Use existing text measures (speech uncertainty) from Step 2
- All V2 scripts in separate folders: `3_Financial_V2/`, `4_Econometric_V2/`, etc.
- Outputs to `4_Outputs/3_Financial_V2/`, `4_Outputs/4_Econometric_V2/`, etc.

### H1: Cash Holdings Variables & Regression

- [x] **H1-01**: Construct Cash Holdings DV = Cash and Cash Equivalents (CHE) / Total Assets (AT)
- [x] **H1-02**: Construct Firm Leverage moderator = Total Debt (DLTT + DLC) / Total Assets (AT)
- [x] **H1-03**: Construct Operating Cash Flow Volatility control = StdDev(OANCF/AT) over trailing 5 years
- [x] **H1-04**: Construct Current Ratio control = Current Assets (ACT) / Current Liabilities (LCT)
- [x] **H1-05**: Include standard controls: Tobin's Q, ROA, Capex/AT, Dividend Payer dummy, Firm Size
- [x] **H1-06**: Merge with existing speech uncertainty measures from Step 2 outputs
- [x] **H1-07**: Run OLS: CashHoldings_{t+1} ~ Uncertainty_t + Leverage_t + Uncertainty×Leverage + Controls + Firm_FE + Year_FE + Industry_FE
- [x] **H1-08**: Cluster standard errors at firm level
- [x] **H1-09**: Test β1 > 0 (vagueness increases cash) and β3 < 0 (leverage attenuates)
- [x] **H1-10**: Output coefficient table and stats.json

### H2: Investment Efficiency Variables & Regression

- [x] **H2-01**: Construct Overinvestment Dummy = 1 if Capex/Depreciation > 1.5 AND Sales Growth < industry-year median
- [x] **H2-02**: Construct Underinvestment Dummy = 1 if Capex/Depreciation < 0.75 AND Tobin's Q > 1.5
- [x] **H2-03**: Construct Efficiency Score DV = 1 - (% Overinvestment + % Underinvestment years) over 5-year window
- [x] **H2-04**: Alternative DV: Residual from ∆ROA(t+2) ~ Capex(t)/AT regression
- [x] **H2-05**: Include controls: Tobin's Q, Cash Flow Volatility, Industry CapEx Intensity, Analyst Dispersion
- [x] **H2-06**: Include standard controls: Firm Size, ROA, Free Cash Flow, Earnings Volatility
- [x] **H2-07**: Merge with existing speech uncertainty measures from Step 2 outputs
- [x] **H2-08**: Run OLS: Efficiency_{t+1} ~ Uncertainty_t + Leverage_t + Uncertainty×Leverage + Controls + Firm_FE + Year_FE + Industry_FE
- [x] **H2-09**: Test β1 < 0 (vagueness lowers efficiency) and β3 > 0 (leverage improves efficiency)
- [x] **H2-10**: Output coefficient table and stats.json

### H3: Payout Policy Variables & Regression

- [x] **H3-01**: Construct Dividend Policy Stability DV = -StdDev(∆DPS/mean DPS) over trailing 5 years
- [x] **H3-02**: Construct Payout Flexibility DV = % years with dividend change (|∆DPS| > 5%) over 5-year window
- [x] **H3-03**: Include controls: Earnings Volatility (StdDev EPS over 5 years), FCF Growth, Firm Maturity
- [x] **H3-04**: Include standard controls: Firm Size, ROA, Tobin's Q, Cash Holdings
- [ ] **H3-05**: Merge with existing speech uncertainty measures from Step 2 outputs
- [ ] **H3-06**: Run OLS for Stability: Stability_{t+1} ~ Uncertainty_t + Leverage_t + Uncertainty×Leverage + Controls + FEs
- [ ] **H3-07**: Run OLS for Flexibility: Flexibility_{t+1} ~ Uncertainty_t + Leverage_t + Uncertainty×Leverage + Controls + FEs
- [ ] **H3-08**: Test for Stability: β1 < 0, β3 < 0; for Flexibility: β1 > 0, β3 > 0
- [ ] **H3-09**: Output coefficient table and stats.json

### Econometric Infrastructure

- [x] **ECON-01**: Implement panel OLS with firm + year + industry fixed effects (Fama-French 48)
- [x] **ECON-02**: Implement interaction term creation with mean-centering (avoid multicollinearity)
- [x] **ECON-03**: Implement clustered standard errors (firm-level with double-clustering option)
- [x] **ECON-04**: Implement 2SLS with instruments: manager's prior-firm vagueness, industry-peer average vagueness
- [x] **ECON-05**: Validate instruments with first-stage F > 10, Hansen J overidentification test
- [x] **ECON-06**: Apply Newey-West adjustment for heteroskedasticity and autocorrelation
- [x] **ECON-07**: Check multicollinearity with VIF < 5 threshold

### Robustness Checks

- [ ] **ROBUST-01**: Subsample by leverage (below/above median debt/assets)
- [ ] **ROBUST-02**: Subsample by growth (Tobin's Q above/below 1.5)
- [ ] **ROBUST-03**: Subsample by free cash flow (above/below median FCF/assets)
- [ ] **ROBUST-04**: Subsample by time period (pre/post-2008 crisis)
- [ ] **ROBUST-05**: Alternative uncertainty measure: weak modals only
- [ ] **ROBUST-06**: Exclude crisis years (2008-2009) sensitivity
- [ ] **ROBUST-07**: Reverse causality check: regress uncertainty on lagged outcome

### Identification Strategies

- [ ] **IDENT-01**: Manager fixed effects with within-manager variation
- [ ] **IDENT-02**: Propensity score matching for high/low vagueness firms
- [ ] **IDENT-03**: Falsification test on placebo DV (e.g., inventory/assets for H1)

### Publication Output

- [ ] **PUB-01**: Generate coefficient tables with β, SE, t-stat, p-value, R², N
- [ ] **PUB-02**: Generate LaTeX-formatted regression tables
- [ ] **PUB-03**: Calculate economic significance (1-SD change interpretation)
- [ ] **PUB-04**: Report marginal effects at mean leverage
- [ ] **PUB-05**: Output stats.json with all regression diagnostics

### V2 Pipeline Structure

- [x] **STRUCT-01**: Create 2_Scripts/3_Financial_V2/ folder for H1/H2/H3 variable construction
- [x] **STRUCT-02**: Create 2_Scripts/4_Econometric_V2/ folder for hypothesis regressions
- [x] **STRUCT-03**: Output to 4_Outputs/3_Financial_V2/ with timestamped directories
- [x] **STRUCT-04**: Output to 4_Outputs/4_Econometric_V2/ with timestamped directories
- [x] **STRUCT-05**: Logs to 3_Logs/3_Financial_V2/ and 3_Logs/4_Econometric_V2/
- [x] **STRUCT-06**: Follow existing script naming convention: {step}.{substep}_{Name}.py

### H5: Analyst Dispersion Variables & Regression

- [x] **H5-01**: Construct Analyst Dispersion DV = STDEV / |MEANEST| with filters (NUMEST >= 3, |MEANEST| >= 0.05)
- [x] **H5-02**: Merge IBES data via CCM CUSIP-GVKEY linking with LINKPRIM='P'
- [x] **H5-03**: Construct forward dispersion (t+1) for causal design
- [x] **H5-04**: Merge with speech uncertainty measures and compute uncertainty_gap
- [x] **H5-05**: Include controls: Prior Dispersion, Earnings Surprise, Analyst Coverage, Firm Size, etc.
- [x] **H5-06**: Run primary regression: Dispersion_{t+1} ~ Weak_Modal_t + Uncertainty_t + Controls + Firm_FE + Year_FE
- [x] **H5-07**: Run gap regression: Dispersion_{t+1} ~ Uncertainty_Gap_t + Controls + Firm_FE + Year_FE
- [x] **H5-08**: Run robustness: Without lagged DV, without NUMEST, CEO-only measures
- [x] **H5-09**: Cluster standard errors at firm level
- [x] **H5-10**: Output coefficient table and stats.json with all regression diagnostics

### H6: Managerial Hedging and M&A Targeting

- [ ] **H6-01**: M&A Target Variable Construction — Create M&A target dummy (1 if firm announces M&A in quarter t+1, else 0)
- [ ] **H6-02**: Deal Premium Variable Construction — Calculate premium = (Offer price - Price 1 day prior) / Price 1 day prior
- [ ] **H6-03**: H6 Analysis Dataset Construction — Merge earnings call text measures, M&A variables, and controls (N > 20,000)
- [ ] **H6-04**: H6a Targeting Logistic Regression — Test M&A_target ~ Weak_Modal + Controls + FEs (converges)
- [ ] **H6-05**: H6b Premium OLS Regression — Test Deal_Premium ~ Weak_Modal + Controls + FEs (VIF < 5)
- [ ] **H6-06**: H6 Robustness — Alternative text measure specifications (CEO-only, Presentation-only)
- [ ] **H6-07**: H6 Robustness — Subsample tests (high vs low leverage, growth firms)
- [ ] **H6-08**: H6 Robustness — Timing sensitivity (speech at t vs t-1 vs t-2)
- [ ] **H6-09**: H6 Identification — Industry-year M&A intensity as instrument
- [ ] **H6-10**: H6 Output — Coefficient table with beta, SE, t-stat, p-value, R-squared, N

### H7: CEO Vagueness and Forced Turnover Risk

- [ ] **H7-01**: CEO Turnover Variable Construction — Create forced turnover dummy from ceo_dismissal flag
- [ ] **H7-02**: H7 Analysis Dataset Construction — Merge earnings call text measures with CEO dismissal data (N > 1,000 events)
- [ ] **H7-03**: H7a Turnover Logistic Regression — Test Forced_Turnover ~ Uncertainty + Performance_Controls + FEs
- [ ] **H7-04**: H7b Survival Analysis — Cox proportional hazards model for time-to-turnover
- [ ] **H7-05**: H7 Controls — Include prior ROA, prior returns, tenure, firm size, governance
- [ ] **H7-06**: H7 Robustness — Manager vs CEO uncertainty measures
- [ ] **H7-07**: H7 Robustness — Presentation vs Q&A uncertainty
- [ ] **H7-08**: H7 Robustness — Non-forced turnover comparison
- [ ] **H7-09**: H7 Identification — Industry-year turnover shock as instrument
- [ ] **H7-10**: H7 Output — Hazard ratios or odds ratios with SE, p-value, event count

### H8: Speech Clarity and Executive Compensation

- [ ] **H8-01**: Compensation Variable Construction — Merge Execucomp tdc1 (total compensation) via gvkey+year
- [ ] **H8-02**: Pay-for-Performance Sensitivity — Calculate delta(tdc1)/delta(returns)
- [ ] **H8-03**: H8 Analysis Dataset Construction — Merge text measures with Execucomp (N > 15,000)
- [ ] **H8-04**: H8a Compensation OLS Regression — Test log(Compensation) ~ Uncertainty + Performance_Controls + FEs
- [ ] **H8-05**: H8b PPS Interaction Regression — Test Compensation ~ Uncertainty*Returns + Controls + FEs
- [ ] **H8-06**: H8 Controls — Include ROA, returns, firm size, tenure, governance
- [ ] **H8-07**: H8 Robustness — CEO vs Manager uncertainty measures
- [ ] **H8-08**: H8 Robustness — Salary vs Bonus vs Total compensation components
- [ ] **H8-09**: H8 Identification — Industry compensation norms as instrument
- [ ] **H8-10**: H8 Output — Coefficient table with economic interpretation ($ per SD uncertainty)

### H9: Uncertainty Gap and Future Stock Returns

- [ ] **H9-01**: Uncertainty Gap Variable Construction — Calculate QA_Uncertainty - Pres_Uncertainty
- [ ] **H9-02**: Future Returns Construction — Calculate abnormal returns (3-day, 1-month, 1-quarter)
- [ ] **H9-03**: H9 Analysis Dataset Construction — Merge text measures with CRSP DSF via CCM (N > 100,000)
- [ ] **H9-04**: H9 Returns OLS Regression — Test Abnormal_Returns ~ Uncertainty_Gap + Controls + Firm_FE + Time_FE
- [ ] **H9-05**: H9 Portfolio Analysis — Form high-gap vs low-gap portfolios, compare returns
- [ ] **H9-06**: H9 Controls — Include prior returns, volatility, earnings surprise, analyst coverage
- [ ] **H9-07**: H9 Robustness — Different return windows (3-day, 1-month, 1-quarter)
- [ ] **H9-08**: H9 Robustness — CEO vs Manager gap measures
- [ ] **H9-09**: H9 Identification — Cross-sectional gap variation instrument
- [ ] **H9-10**: H9 Output — Coefficient table with annualized return interpretation

### H10: Language Complexity and Analyst Forecast Accuracy

- [ ] **H10-01**: Complexity Variable Construction — Compute Fog index, word length, syllables per word
- [ ] **H10-02**: Forecast Error Construction — Calculate |MEANEST - ACTUAL| / |ACTUAL|
- [ ] **H10-03**: H10 Analysis Dataset Construction — Merge text measures with IBES (verified in H5, N > 250,000)
- [ ] **H10-04**: H10 Accuracy OLS Regression — Test Forecast_Error ~ Complexity + Controls + Firm_FE + Year_FE
- [ ] **H10-05**: H10 Quantile Regression — Test complexity effects across accuracy distribution
- [ ] **H10-06**: H10 Controls — Include firm size, earnings volatility, analyst coverage, prior accuracy
- [ ] **H10-07**: H10 Robustness — Different complexity measures (Fog, word length, jargon)
- [ ] **H10-08**: H10 Robustness — CEO vs Manager complexity
- [ ] **H10-09**: H10 Identification — Industry complexity norms as instrument
- [ ] **H10-10**: H10 Output — Coefficient table with error rate interpretation

## v3.0 Requirements (Future)

Deferred to future release. Tracked but not in current roadmap.

### Advanced Econometrics

- **ADV-01**: Quantile regression at 25th/50th/75th percentiles
- **ADV-02**: Difference-in-differences around CEO turnovers or leverage shocks
- **ADV-03**: Coefficient stability bounds (Oster 2019)
- **ADV-04**: Wild bootstrap for small-cluster inference

### Extended Scope

- **EXT-01**: Cross-country analysis with Global Compustat
- **EXT-02**: LLM-based uncertainty (FinBERT/GPT embeddings)
- **EXT-03**: Interactive exploration dashboard

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Rebuilding speech uncertainty | Already exists in Step 2 outputs |
| New sample construction | Use existing v1.0 sample (firms, time period) |
| Modifying existing scripts | V2 is extension only, separate folders |
| Real-time analysis | Batch processing for replication |
| Video/audio analysis | Text transcripts per methodology |
| Cross-country analysis | U.S. firms only per thesis scope |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| STRUCT-01 | Phase 28 | Complete |
| STRUCT-02 | Phase 28 | Complete |
| STRUCT-03 | Phase 28 | Complete |
| STRUCT-04 | Phase 28 | Complete |
| STRUCT-05 | Phase 28 | Complete |
| STRUCT-06 | Phase 28 | Complete |
| H1-01 | Phase 29 | Complete |
| H1-02 | Phase 29 | Complete |
| H1-03 | Phase 29 | Complete |
| H1-04 | Phase 29 | Complete |
| H1-05 | Phase 29 | Complete |
| H2-01 | Phase 30 | Complete |
| H2-02 | Phase 30 | Complete |
| H2-03 | Phase 30 | Complete |
| H2-04 | Phase 30 | Complete |
| H2-05 | Phase 30 | Complete |
| H2-06 | Phase 30 | Complete |
| H3-01 | Phase 31 | Complete |
| H3-02 | Phase 31 | Complete |
| H3-03 | Phase 31 | Complete |
| H3-04 | Phase 31 | Complete |
| H3-05 | Phase 31 | Pending |
| ECON-01 | Phase 32 | Complete |
| ECON-02 | Phase 32 | Complete |
| ECON-03 | Phase 32 | Complete |
| ECON-04 | Phase 32 | Complete |
| ECON-05 | Phase 32 | Complete |
| ECON-06 | Phase 32 | Complete |
| ECON-07 | Phase 32 | Complete |
| H1-06 | Phase 33 | Complete |
| H1-07 | Phase 33 | Complete |
| H1-08 | Phase 33 | Complete |
| H1-09 | Phase 33 | Complete |
| H1-10 | Phase 33 | Complete |
| H2-07 | Phase 34 | Complete |
| H2-08 | Phase 34 | Complete |
| H2-09 | Phase 34 | Complete |
| H2-10 | Phase 34 | Complete |
| H3-06 | Phase 35 | Pending |
| H3-07 | Phase 35 | Pending |
| H3-08 | Phase 35 | Pending |
| H3-09 | Phase 35 | Pending |
| ROBUST-01 | Phase 36 | Pending |
| ROBUST-02 | Phase 36 | Pending |
| ROBUST-03 | Phase 36 | Pending |
| ROBUST-04 | Phase 36 | Pending |
| ROBUST-05 | Phase 36 | Pending |
| ROBUST-06 | Phase 36 | Pending |
| ROBUST-07 | Phase 36 | Pending |
| IDENT-01 | Phase 37 | Pending |
| IDENT-02 | Phase 37 | Pending |
| IDENT-03 | Phase 37 | Pending |
| PUB-01 | Phase 38 | Pending |
| PUB-02 | Phase 38 | Pending |
| PUB-03 | Phase 38 | Pending |
| PUB-04 | Phase 38 | Pending |
| PUB-05 | Phase 38 | Pending |
| H5-01 | Phase 40 | Complete |
| H5-02 | Phase 40 | Complete |
| H5-03 | Phase 40 | Complete |
| H5-04 | Phase 40 | Complete |
| H5-05 | Phase 40 | Complete |
| H5-06 | Phase 40 | Complete |
| H5-07 | Phase 40 | Complete |
| H5-08 | Phase 40 | Complete |
| H5-09 | Phase 40 | Complete |
| H5-10 | Phase 40 | Complete |
| H6-01 | Phase 42 | Pending |
| H6-02 | Phase 42 | Pending |
| H6-03 | Phase 42 | Pending |
| H6-04 | Phase 42 | Pending |
| H6-05 | Phase 42 | Pending |
| H6-06 | Phase 42 | Pending |
| H6-07 | Phase 42 | Pending |
| H6-08 | Phase 42 | Pending |
| H6-09 | Phase 42 | Pending |
| H6-10 | Phase 42 | Pending |
| H7-01 | Phase 43 | Pending |
| H7-02 | Phase 43 | Pending |
| H7-03 | Phase 43 | Pending |
| H7-04 | Phase 43 | Pending |
| H7-05 | Phase 43 | Pending |
| H7-06 | Phase 43 | Pending |
| H7-07 | Phase 43 | Pending |
| H7-08 | Phase 43 | Pending |
| H7-09 | Phase 43 | Pending |
| H7-10 | Phase 43 | Pending |
| H8-01 | Phase 44 | Pending |
| H8-02 | Phase 44 | Pending |
| H8-03 | Phase 44 | Pending |
| H8-04 | Phase 44 | Pending |
| H8-05 | Phase 44 | Pending |
| H8-06 | Phase 44 | Pending |
| H8-07 | Phase 44 | Pending |
| H8-08 | Phase 44 | Pending |
| H8-09 | Phase 44 | Pending |
| H8-10 | Phase 44 | Pending |
| H9-01 | Phase 45 | Pending |
| H9-02 | Phase 45 | Pending |
| H9-03 | Phase 45 | Pending |
| H9-04 | Phase 45 | Pending |
| H9-05 | Phase 45 | Pending |
| H9-06 | Phase 45 | Pending |
| H9-07 | Phase 45 | Pending |
| H9-08 | Phase 45 | Pending |
| H9-09 | Phase 45 | Pending |
| H9-10 | Phase 45 | Pending |
| H10-01 | Phase 46 | Pending |
| H10-02 | Phase 46 | Pending |
| H10-03 | Phase 46 | Pending |
| H10-04 | Phase 46 | Pending |
| H10-05 | Phase 46 | Pending |
| H10-06 | Phase 46 | Pending |
| H10-07 | Phase 46 | Pending |
| H10-08 | Phase 46 | Pending |
| H10-09 | Phase 46 | Pending |
| H10-10 | Phase 46 | Pending |

**Coverage:**
- v2.0 requirements: 105 total
- Mapped to phases: 105
- Unmapped: 0
- Complete: 60/105 (57%)
- Pending: 45/105 (43%)

---
*Requirements defined: 2026-02-04*
*Traceability updated: 2026-02-06 (all 105 requirements mapped to phases 28-46)*
