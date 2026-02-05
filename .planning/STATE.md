# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Every hypothesis test must produce verifiable, reproducible regression results exactly as specified in the methodology
**Current focus:** v2.0 Hypothesis Testing Suite - Phase 28 complete, ready for Phases 29-31

## Current Position

Phase: 29 - H1 Cash Holdings Variables
Plan: 01 of 01
Status: In Progress
Last activity: 2026-02-04 — Completed H1 Cash Holdings variables construction (plan 29-01)

### Progress

```
v2.0 Hypothesis Testing Suite
[██░░░░░░░░░░░░░░░░░] 2/11 phases (18%)

Phase 28: V2 Structure Setup      [COMPLETE - 3/3 plans done]
Phase 29: H1 Cash Holdings Vars   [COMPLETE - 1/1 plans done]
Phase 30: H2 Investment Vars      [READY]
Phase 31: H3 Payout Policy Vars   [READY]
Phase 32: Econometric Infra       [READY]
Phase 33: H1 Regression           [BLOCKED by 32]
Phase 34: H2 Regression           [BLOCKED by 30, 32]
Phase 35: H3 Regression           [BLOCKED by 31, 32]
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
| Phases Complete | 27/27 | 1/11 |
| Plans Complete | 143/143 | 3/154 |
| Requirements Mapped | 30/30 | 55/55 |
| Scripts CLI-Ready | 21/21 | — |

## Session Continuity

### Last Session (2026-02-05)

**Completed:**
- 29-01: H1 Cash Holdings Variables construction
  - Fixed Compustat column mappings (cshoq, dvy)
  - Added PyArrow schema inspection to avoid OOM
  - Generated H1_CashHoldings.parquet with 448,004 observations
  - All 9 H1 variables computed: Cash Holdings, Leverage, OCF Volatility, Current Ratio, Tobin's Q, ROA, Capex/AT, Dividend Payer, Firm Size
  - Winsorization applied at 1%/99%
  - stats.json documents variable distributions

**Next Session:**
- Phase 29 is complete - can proceed to Phase 30 (H2 Investment Vars) or Phase 31 (H3 Payout Policy Vars)
- Can parallelize Phases 30, 31 (H2/H3 variable construction)
- Phase 32 (Econometric Infrastructure) can also proceed in parallel
- Once Phase 32 completes, Phase 33 (H1 Regression) can proceed with H1_CashHoldings.parquet as input

---
*Last updated: 2026-02-05*
