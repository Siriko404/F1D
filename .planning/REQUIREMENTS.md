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
- [ ] **H2-07**: Merge with existing speech uncertainty measures from Step 2 outputs
- [ ] **H2-08**: Run OLS: Efficiency_{t+1} ~ Uncertainty_t + Leverage_t + Uncertainty×Leverage + Controls + Firm_FE + Year_FE + Industry_FE
- [ ] **H2-09**: Test β1 < 0 (vagueness lowers efficiency) and β3 > 0 (leverage improves efficiency)
- [ ] **H2-10**: Output coefficient table and stats.json

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
| H2-07 | Phase 34 | Pending |
| H2-08 | Phase 34 | Pending |
| H2-09 | Phase 34 | Pending |
| H2-10 | Phase 34 | Pending |
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

**Coverage:**
- v2.0 requirements: 55 total
- Mapped to phases: 55 ✓
- Unmapped: 0

---
*Requirements defined: 2026-02-04*
*Traceability updated: 2026-02-04 (all 55 requirements mapped to phases 28-38)*
