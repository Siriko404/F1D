# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Every hypothesis test must produce verifiable, reproducible regression results exactly as specified in the methodology
**Current focus:** v2.0 Hypothesis Testing Suite - Phase 31 complete, ready for Phase 32

## Current Position

Phase: 31 - H3 Payout Policy Variables
Plan: 01 of 01
Status: Phase Complete
Last activity: 2026-02-05 — Completed H3 payout policy variables (plan 31-01)

### Progress

```
v2.0 Hypothesis Testing Suite
[████░░░░░░░░░░░░░░░] 4/11 phases (36%)

Phase 28: V2 Structure Setup      [COMPLETE - 3/3 plans done]
Phase 29: H1 Cash Holdings Vars   [COMPLETE - 1/1 plans done]
Phase 30: H2 Investment Vars      [COMPLETE - 2/2 plans done]
Phase 31: H3 Payout Policy Vars   [COMPLETE - 1/1 plans done]
Phase 32: Econometric Infra       [READY]
Phase 33: H1 Regression           [BLOCKED by 32]
Phase 34: H2 Regression           [BLOCKED by 32]
Phase 35: H3 Regression           [BLOCKED by 32]
Phase 36: Robustness Checks       [BLOCKED by 33, 34, 35]
Phase 37: Identification          [BLOCKED by 36]
Phase 38: Publication Output      [BLOCKED by 37]
```

## v2.0 Milestone Goals

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

## Key Constraints

- Use existing sample (firms, time period) from v1.0 implementation
- Use existing text measures (speech uncertainty) from Step 2 outputs
- All V2 scripts in SEPARATE folders: `2_Scripts/3_Financial_V2/`, `2_Scripts/4_Econometric_V2/`
- Outputs to `4_Outputs/3_Financial_V2/`, `4_Outputs/4_Econometric_V2/`
- Logs to `3_Logs/3_Financial_V2/`, `3_Logs/4_Econometric_V2/`

## Accumulated Context

### Decisions

- [v2.0 Roadmap] 11 phases (28-38) covering 55 requirements
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
- [31-01 Variables] Dividend Policy Stability = -StdDev(ΔDPS) / |Mean(DPS)| over trailing 5 years (H3-01 DV)
- [31-01 Variables] Payout Flexibility = % years with |ΔDPS| > 5% of prior DPS over 5-year window (H3-02 DV)
- [31-01 Variables] Annualize quarterly DPS/EPS BEFORE computing rolling windows (avoids within-year distortion)
- [31-01 Variables] Filter to dividend payers only (stability/flexibility undefined for never-payers)
- [31-01 Variables] FCF Growth uses absolute value in denominator to handle negative FCF gracefully
- [31-01 Variables] Allow negative RE/TE as valid immaturity signal (per DeAngelo et al.)
- [31-01 Variables] Minimum 2 years required in 5-year rolling window for variable computation
- [31-01 Variables] H1 controls aggregated via mean to get one row per gvkey-year (H1 has multiple obs per firm-year)

### From v1.0 (carry forward)

- Stats inline per script (self-contained replication)
- Pipeline follows CLAUDE.md conventions (1_Inputs, 2_Scripts, 3_Logs, 4_Outputs)
- Timestamp-based output resolution (symlinks removed in Phase 27)
- All 21 scripts support CLI with --help and --dry-run
- get_latest_output_dir() for reading prerequisite outputs

### Research Flags

- **Phase 30 (H2 Variables):** Investment efficiency residual calculation (Biddle et al. 2009) is non-trivial - verify exact methodology
- **Phase 32 (Econometrics):** linearmodels API for `first_stage.diagnostics` syntax may need version verification

### Known Pitfalls (from research)

1. **FE Collinearity Trap:** Firm + industry FE are redundant (firms don't change industries). Use `drop_absorbed=False, check_rank=True`
2. **Interaction Multicollinearity:** Always center continuous variables before creating interactions
3. **Weak Instruments in 2SLS:** F < 10 on first stage means 2SLS is more biased than OLS. Enforce F > 10 programmatically
4. **Manager FE Connectivity:** With few CEO "movers" between firms, CEO FE conflates manager style with firm culture
5. **Multiple Testing in Subsamples:** Use interaction terms instead of separate regressions to avoid false positives

### Blockers/Concerns

None currently.

## Performance Metrics

| Metric | v1.0 Final | v2.0 Current |
|--------|------------|--------------|
| Phases Complete | 27/27 | 4/11 |
| Plans Complete | 143/143 | 8/154 |
| Requirements Complete | 30/30 | 28/55 |
| Scripts CLI-Ready | 21/21 | 5/5 |

## Session Continuity

### Last Session (2026-02-05)

**Completed:**
- 31-01: H3 Payout Policy Variables construction
  - Created 3.3_H3Variables.py (1,140 lines)
  - Fixed Unicode Delta character, cartesian product issues in H1 controls merge
  - Fixed observability_utils to skip list values in stats summary
  - Generated H3_PayoutPolicy.parquet with 16,616 dividend-paying firm observations
  - 2 DVs: div_stability (99.8% coverage), payout_flexibility (100% coverage)
  - 3 H3 controls: earnings_volatility, fcf_growth, firm_maturity
  - Standard controls from H1: firm_size, roa, tobins_q, cash_holdings
  - Filtered to dividend payers only (DVs undefined for never-payers)
- 30-02: Analyst Dispersion Gap Closure
  - Created 3.2a_AnalystDispersionPatch.py (637 lines)
  - Implemented CCM CUSIP-GVKEY linking with LINKPRIM/LINKTYPE filtering
  - Computed analyst_dispersion = STDEV / |MEANEST| from IBES
  - Patched H2 output to 14 columns, 77.41% coverage (22,360/28,887 obs)
  - H2-05 requirement NOW SATISFIED
- 30-01: H2 Investment Efficiency Variables construction
  - Created 3.2_H2Variables.py (1,679 lines)
  - Fixed IBES column names (uppercase), memory optimization, datadate handling
  - Generated H2_InvestmentEfficiency.parquet with 28,887 observations
  - 13 variables computed: overinvest_dummy, underinvest_dummy, efficiency_score, roa_residual
  - Controls: tobins_q, cf_volatility, industry_capex_intensity, firm_size, roa, fcf, earnings_volatility
  - FF48/FF12 industry classification with fallback for thin cells
  - Biddle et al. (2009) ROA residual via cross-sectional OLS by industry-year

**Next Session:**
- Phase 31 is complete - should proceed to Phase 32 (Econometric Infrastructure)
- Once Phase 32 completes, Phases 33-35 (H1/H2/H3 Regression) can proceed
- Phase 35 (H3 Regression) now has H3 variables available from Phase 31

---
*Last updated: 2026-02-05*
