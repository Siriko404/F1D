# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Every hypothesis test must produce verifiable, reproducible regression results exactly as specified in the methodology
**Current focus:** v2.0 Hypothesis Testing Suite — ACTIVE (Phase 40: H5 variance-to-variance hypothesis, PLANNED)

## Current Position

Phase: 39 - Leverage Disciplines Managers and Lowers Speech Uncertainty
Plan: —
Status: PHASE COMPLETE — 2/2 plans done, 10/10 requirements verified
Last activity: 2026-02-05 — Phase 39 complete, H4 partially supported (3/6 measures significant)

### Progress

```
v2.0 Hypothesis Testing Suite — ACTIVE
[████████████████░░░] 9/10 phases (90%)

Phase 28: V2 Structure Setup      [COMPLETE - 3/3 plans done]
Phase 29: H1 Cash Holdings Vars   [COMPLETE - 1/1 plans done]
Phase 30: H2 Investment Vars      [COMPLETE - 2/2 plans done]
Phase 31: H3 Payout Policy Vars   [COMPLETE - 1/1 plans done]
Phase 32: Econometric Infra       [COMPLETE - 2/2 plans done]
Phase 33: H1 Regression           [COMPLETE - 1/1 plans done] → H1a: 0/6, H1b: 1/6
Phase 34: H2 Regression           [COMPLETE - 1/1 plans done] → H2a: 0/6, H2b: 0/6
Phase 35: H3 Regression           [COMPLETE - 1/1 plans done] → H3a: 1/6, H3b: 0/6
Phase 36: Robustness Checks       [CANCELLED - null results]
Phase 37: Identification          [CANCELLED - null results]
Phase 38: Publication Output      [CANCELLED - null results]
Phase 39: Leverage → Speech Discipline [COMPLETE - 2/2 plans] → H4: 3/6 significant
Phase 40: H5 Speech → Outcome Volatility [PLANNED - 0/0 plans]
```

## v2.0 Hypothesis Testing Results

**Conclusion**: No consistent statistical support for hypothesized relationships between managerial speech uncertainty and corporate financial policies.

| Hypothesis | Prediction | Result | Significant Measures |
|------------|------------|--------|---------------------|
| H1a | Uncertainty → ↑ Cash | NOT SUPPORTED | 0/6 |
| H1b | Leverage attenuates H1a | WEAK | 1/6 (QA_Weak_Modal) |
| H2a | Uncertainty → ↓ Efficiency | NOT SUPPORTED | 0/6 |
| H2b | Leverage improves H2a | NOT SUPPORTED | 0/6 |
| H3a | Uncertainty → ↓ Stability | WEAK | 1/6 (CEO_Pres_Uncertainty) |
| H3b | Leverage → ↑ Stability | NOT SUPPORTED | 0/6 |
| H4 | Leverage → ↓ Uncertainty | PARTIAL | 3/6 (Mgr QA, Mgr/CEO Weak Modal) |

**Implication**: Phases 36-38 (Robustness, Identification, Publication) cancelled as scientifically inappropriate for null results.

## v2.0 Milestone Goals — CONCLUDED

**Hypothesis 1: Cash Holdings (H1)**
- Vague managers hoard more cash (precautionary motive)
- Leverage moderates the effect (debt discipline)
- Regression: Cash/Assets ~ Uncertainty + Leverage + Uncertainty×Leverage + Controls + FEs

**Hypothesis 2: Investment Efficiency (H2)**
- Vagueness correlates with over/underinvestment
- Measure against Tobin's Q benchmarks
- Regression: Efficiency ~ Uncertainty + Leverage + Uncertainty×Leverage + Controls + FEs

**Hypothesis 3: Payout Policy Stability (H3)**
- Vague managers have volatile dividend policies
- Leverage promotes smoothing
- Regression: Stability ~ Uncertainty + Leverage + Uncertainty×Leverage + Controls + FEs

**Hypothesis 4: Leverage Disciplines Speech (H4)** — *NEW*
- Higher leverage disciplines managers (debt monitoring hypothesis)
- Debt holders and covenant restrictions constrain vague language
- Regression: Speech Uncertainty ~ Leverage + Controls + FEs (reverse direction from H1-H3)

**Hypothesis 5: Speech Uncertainty Predicts Financial Outcome Uncertainty (H5)** — *NEW*
- Higher speech uncertainty (possibly Shannon's entropy) predicts uncertainty of financial outcomes
- Variance-to-variance relationship: uncertain speech → volatile earnings/returns/cash flows
- Regression: Financial Outcome Volatility ~ Speech Uncertainty + Controls + FEs

## Key Constraints

- Use existing sample (firms, time period) from v1.0 implementation
- Use existing text measures (speech uncertainty) from Step 2 outputs
- All V2 scripts in SEPARATE folders: `2_Scripts/3_Financial_V2/`, `2_Scripts/4_Econometric_V2/`
- Outputs to `4_Outputs/3_Financial_V2/`, `4_Outputs/4_Econometric_V2/`
- Logs to `3_Logs/3_Financial_V2/`, `3_Logs/4_Econometric_V2/`

## Accumulated Context

### Roadmap Evolution

- **2026-02-05**: Phase 39 added — "Higher leverage disciplines managers and lowers uncertainty in speech" (reverse causal hypothesis: leverage → speech discipline)
- **2026-02-05**: Phase 40 added — "H5 Speech Uncertainty Predicts Financial Outcome Uncertainty" (variance-to-variance: speech uncertainty → financial outcome uncertainty, e.g. Shannon's entropy)

### Decisions

- [v2.0 Roadmap] 11 phases (28-38) covering 55 requirements; Phases 39-40 added as 12th-13th phases
- [v2.0 Roadmap] Phase numbering continues from v1.0 (ended at Phase 27)
- [v2.0 Roadmap] Variables phases (29-31) can parallelize after structure setup
- [v2.0 Roadmap] Regression phases (33-35) can parallelize after econometric infrastructure
- [v2.0 Research] No new dependencies needed - existing pandas/statsmodels/linearmodels stack sufficient
- [v2.0 Research] Investment efficiency calculation (Biddle et al. 2009) needs verification during implementation
- [28-01 Financial_V2] README includes all three hypotheses with exact formulas and Compustat field sources
- [28-01 Financial_V2] Scripts numbered 3.1_H1Variables.py, 3.2_H2Variables.py, 3.3_H3Variables.py
- [28-01 Financial_V2] H1, H2, H3 can run in parallel (no interdependencies)
- [28-02 Econometric_V2] Econometric script numbering: 4.0_Infra, 4.1-4.3_Regressions, 4.4-4.6_Robustness, 4.7_Identification, 4.8_Publication
- [28-02 Econometric_V2] Mean-centering required before creating interaction terms
- [28-02 Econometric_V2] First-stage F > 10 threshold enforced for 2SLS validity
- [28-03 Validation] Automated validation script confirms all 6 STRUCT requirements satisfied
- [28-03 Validation] Smart project root detection for nested directory execution
- [28-03 Validation] ASCII console output for Windows compatibility
- [29-01 Variables] Compustat column mappings: `cshoq` (not `cshopq`), `dvy` (not `dvcy`) based on actual schema
- [29-01 Variables] Use PyArrow schema inspection before reading Compustat to avoid OOM from reading all 679 columns
- [29-01 Variables] Multiple observations per gvkey-year from firm controls merge retained for analysis flexibility
- [30-01 Variables] Analyst dispersion skipped in initial run (requires CUSIP-GVKEY linking via CCM)
- [30-02 Variables] CCM linking for analyst dispersion: LINKPRIM in ['P','C'] AND LINKTYPE in ['LU','LC']
- [30-02 Variables] Analyst dispersion = STDEV / |MEANEST|, filtered NUMEST >= 2 AND |MEANEST| >= 0.01
- [30-02 Variables] 77.41% H2 coverage for analyst_dispersion (22,360/28,887 obs)
- [30-02 Variables] H2-05 requirement SATISFIED via CCM CUSIP-GVKEY mapping
- [30-01 Variables] Filter base to sample manifest BEFORE merging to reduce memory usage (10x improvement)
- [30-01 Variables] FF48 industry classification with FF12 fallback for thin cells (<5 firms)
- [30-01 Variables] Mutual exclusivity enforced: firms cannot be both over and under-investing
- [31-01 Variables] Dividend Policy Stability = -StdDev(Delta DPS) / |Mean(DPS)| over trailing 5 years (H3-01 DV)
- [31-01 Variables] Payout Flexibility = % years with |Delta DPS| > 5% of prior DPS over 5-year window (H3-02 DV)
- [31-01 Variables] Annualize quarterly DPS/EPS BEFORE computing rolling windows (avoids within-year distortion)
- [31-01 Variables] Filter to dividend payers only (stability/flexibility undefined for never-payers)
- [31-01 Variables] FCF Growth uses absolute value in denominator to handle negative FCF gracefully
- [31-01 Variables] Allow negative RE/TE as valid immaturity signal (per DeAngelo et al.)
- [31-01 Variables] Minimum 2 years required in 5-year rolling window for variable computation
- [31-01 Variables] H1 controls aggregated via mean to get one row per gvkey-year (H1 has multiple obs per firm-year)
- [31-01 Variables] H3 variables computed: div_stability (99.8%), payout_flexibility (100%), earnings_volatility (100%), fcf_growth (97.2%), firm_maturity (97.8%)
- [32-01 Econometric Infra] Panel OLS with firm + year + industry FE via run_panel_ols() in panel_ols.py (531 lines)
- [32-01 Econometric Infra] Clustered standard errors at firm level with double-clustering option
- [32-01 Econometric Infra] HAC/Newey-West adjustment via cov_type='kernel'
- [32-01 Econometric Infra] VIF diagnostics with threshold 5.0 for multicollinearity warnings
- [32-01 Econometric Infra] Mean-centering for interaction terms via center_continuous() in centering.py (340 lines)
- [32-01 Econometric Infra] Centering reduces artificial multicollinearity between main effects and interactions
- [32-01 Econometric Infra] VIF calculation using statsmodels variance_inflation_factor() in diagnostics.py (413 lines)
- [32-01 Econometric Infra] Condition number detection for ill-conditioned design matrices (>30 threshold)
- [32-02 Econometric Infra] IV2SLS regression wrapper via run_iv2sls() in iv_regression.py (530 lines)
- [32-02 Econometric Infra] First-stage F-stat validation with threshold 10.0; WeakInstrumentError raised if F < 10
- [32-02 Econometric Infra] Hansen J / Sargan overidentification test for over-identified models
- [32-02 Econometric Infra] Publication-ready LaTeX table generation via make_regression_table() in latex_tables.py (533 lines)
- [39-01 H4 Data Prep] H4 data preparation script 4.4_H4_LeverageDiscipline.py (946 lines)
- [39-01 H4 Data Prep] Lagged leverage (t-1) created via groupby shift on gvkey, dropping first year per firm
- [39-01 H4 Data Prep] H4_Analysis_Dataset.parquet: 445,563 obs, 2,428 firms, 19 columns
- [39-01 H4 Data Prep] All 6 uncertainty DVs available (75.5%-99.1% coverage)
- [39-01 H4 Data Prep] VIF diagnostics: All values < 5.0 (max 1.79 for tobins_q)
- [39-01 H4 Data Prep] Weak correlations between leverage_lag1 and uncertainty DVs (-0.02 to +0.02)
- [39-01 H4 Data Prep] Fixed pandas 3.x compatibility: aggregate() split, Series.int() conversion, duplicate column handling
- [39-02 H4 Regression] H4 regression execution extended with one-tailed p-value testing (beta < 0)
- [39-02 H4 Regression] one_tailed_pvalue() function for directional hypothesis testing
- [39-02 H4 Regression] run_all_h4_regressions() executes 6 PanelOLS regressions with conditional controls
- [39-02 H4 Regression] Presentation control included for QA regressions (controls for presentation uncertainty)
- [39-02 H4 Regression] H4 results: 3/6 measures significant at p < 0.05 (one-tailed)
- [39-02 H4 Regression] Significant: Manager_QA_Uncertainty (beta=-0.066), Manager_QA_Weak_Modal (beta=-0.046), CEO_QA_Weak_Modal (beta=-0.048)
- [39-02 H4 Regression] All regressions use Firm + Year FE, firm-clustered SE (N=180K-245K, R2=0.002-0.032)
- [32-02 Econometric Infra] Significance stars: *** p<0.01, ** p<0.05, * p<0.10; booktabs format (toprule, midrule, bottomrule)
- [33-01 H1 Regression] H1 Cash Holdings regression script 4.1_H1CashHoldingsRegression.py (887 lines)
- [33-01 H1 Regression] 24 regressions executed: 6 uncertainty measures x 4 specifications (primary, pooled, year_only, double_cluster)
- [33-01 H1 Regression] One-tailed hypothesis tests: H1a (beta1 > 0), H1b (beta3 < 0)
- [33-01 H1 Regression] Primary spec results: N=16,667-21,690, R2=0.128-0.133
- [33-01 H1 Regression] H1a: 0/6 measures significant; H1b: 1/6 significant (Manager_QA_Weak_Modal_pct, p=0.0216)
- [33-01 H1 Regression] Fixed double-clustering bug in panel_ols.py (cluster columns in MultiIndex after set_index)
- [33-01 H1 Regression] Relaxed condition number threshold to 1000 (VIF is primary diagnostic for FE models)
- [34-01 H2 Regression] H2 Investment Efficiency regression script 4.2_H2InvestmentEfficiencyRegression.py (999 lines)
- [34-01 H2 Regression] 48 regressions executed: 2 DVs x 6 uncertainty measures x 4 specifications
- [34-01 H2 Regression] DVs: efficiency_score (primary), roa_residual (alternative)
- [34-01 H2 Regression] Primary spec results: N=256K-342K, R2=0.002-0.003 (efficiency_score), R2=0.0004-0.0005 (roa_residual)
- [34-01 H2 Regression] H2a (beta1 < 0): 0/6 measures significant for both DVs
- [34-01 H2 Regression] H2b (beta3 > 0): 0/6 measures significant for both DVs
- [34-01 H2 Regression] Merged H1 leverage data into H2 regression (H2 variables lack leverage column)
- [34-01 H2 Regression] No support found for speech uncertainty reducing investment efficiency
- [35-01 H3 Regression] H3 Payout Policy regression script 4.3_H3PayoutPolicyRegression.py (1,050 lines)
- [35-01 H3 Regression] 48 regressions executed: 2 DVs x 6 uncertainty measures x 4 specifications
- [35-01 H3 Regression] DVs: div_stability (higher = more stable), payout_flexibility (higher = more flexible)
- [35-01 H3 Regression] Primary spec results: N=180K-244K, R2=0.021-0.045
- [35-01 H3 Regression] H3a_stability (beta1 < 0): 1/6 significant (CEO_Pres_Uncertainty_pct, p=0.0010)
- [35-01 H3 Regression] H3b_stability (beta3 < 0): 0/6 significant
- [35-01 H3 Regression] H3a_flexibility (beta1 > 0): 1/6 significant (Manager_QA_Weak_Modal_pct, p=0.0037)
- [35-01 H3 Regression] H3b_flexibility (beta3 > 0): 0/6 significant
- [35-01 H3 Regression] DV-specific hypothesis directions: stability tests beta < 0, flexibility tests beta > 0
- [35-01 H3 Regression] Sample expands 1566% after speech merge (16K -> 260K obs) due to multiple speech calls per firm-year
- [39-01 H4 Data Prep] H4 data preparation script 4.4_H4_LeverageDiscipline.py (946 lines)
- [39-01 H4 Data Prep] Lagged leverage (t-1) created via groupby shift on gvkey, dropping first year per firm
- [39-01 H4 Data Prep] H4_Analysis_Dataset.parquet: 445,563 obs, 2,428 firms, 19 columns
- [39-01 H4 Data Prep] All 6 uncertainty DVs available (75.5%-99.1% coverage)
- [39-01 H4 Data Prep] VIF diagnostics: All values < 5.0 (max 1.79 for tobins_q)
- [39-01 H4 Data Prep] Weak correlations between leverage_lag1 and uncertainty DVs (-0.02 to +0.02)
- [39-01 H4 Data Prep] Fixed pandas 3.x compatibility: aggregate() split, Series.int() conversion, duplicate column handling

### From v1.0 (carry forward)

- Stats inline per script (self-contained replication)
- Pipeline follows CLAUDE.md conventions (1_Inputs, 2_Scripts, 3_Logs, 4_Outputs)
- Timestamp-based output resolution (symlinks removed in Phase 27)
- All 21 scripts support CLI with --help and --dry-run
- get_latest_output_dir() for reading prerequisite outputs

### Research Flags

- **Phase 30 (H2 Variables):** Investment efficiency residual calculation (Biddle et al. 2009) is non-trivial - verify exact methodology

### Known Pitfalls (from research)

1. **FE Collinearity Trap:** Firm + industry FE are redundant (firms don't change industries). Use `drop_absorbed=False, check_rank=True`
2. **Interaction Multicollinearity:** Always center continuous variables before creating interactions
3. **Weak Instruments in 2SLS:** F < 10 on first stage means 2SLS is more biased than OLS. Enforce F > 10 programmatically
4. **Manager FE Connectivity:** With few CEO "movers" between firms, CEO FE conflates manager style with firm culture
5. **Multiple Testing in Subsamples:** Use interaction terms instead of separate regressions to avoid false positives

### Blockers/Concerns

None currently.

## Performance Metrics

| Metric | v1.0 Final | v2.0 Final |
|--------|------------|------------|
| Phases Complete | 27/27 | 9/9 active (3 cancelled) |
| Plans Complete | 143/143 | 15/15 |
| Requirements Complete | 30/30 | 50/50 active (15 not pursued) |
| Scripts CLI-Ready | 21/21 | 9/9 |
| Hypotheses Supported | — | H4: 3/6 partial; H1-H3: null |

## Session Continuity

### Last Session (2026-02-05)

**Completed:**
- Phase 39-01: H4 Data Preparation
  - Created 4.4_H4_LeverageDiscipline.py (946 lines)
  - Generated H4_Analysis_Dataset.parquet (445,563 obs, 2,428 firms)
  - Lagged leverage (t-1) properly computed with groupby shift
  - VIF diagnostics passed (all < 5.0)
  - Fixed pandas 3.x compatibility issues

- Phase 39-02: H4 Regression Execution
  - Extended 4.4_H4_LeverageDiscipline.py with regression functions
  - Implemented one_tailed_pvalue() for directional hypothesis testing
  - Executed 6 PanelOLS regressions (one per uncertainty DV)
  - H4 results: 3/6 measures significant at p < 0.05 (one-tailed)
  - Significant: Manager_QA_Uncertainty (beta=-0.066, p=0.007)
  - Significant: Manager_QA_Weak_Modal (beta=-0.046, p=0.002)
  - Significant: CEO_QA_Weak_Modal (beta=-0.048, p=0.025)
  - Generated H4_Regression_Results.parquet, H4_Coefficient_Table.tex, H4_RESULTS.md

**H4 Results Summary:**
- Manager measures show discipline effect (QA Uncertainty, Weak Modal significant)
- CEO measures show weaker/no effect (only Weak Modal marginally significant)
- Presentation uncertainty measures show no significant leverage effect

**Next Session:**
- Plan 40-01: H5 Speech Uncertainty Predicts Financial Outcome Volatility
- New hypothesis: Speech uncertainty -> outcome volatility (variance-to-variance)
- Requires outcome volatility variable construction


---
*Last updated: 2026-02-05 (Phase 40 added)*
