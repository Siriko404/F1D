# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Every hypothesis test must produce verifiable, reproducible regression results exactly as specified in the methodology
**Current focus:** v2.0 Hypothesis Testing Suite - Phase 28 (V2 Structure Setup)

## Current Position

Phase: 28 - V2 Structure Setup
Plan: —
Status: Ready to plan
Last activity: 2026-02-04 — Roadmap created for v2.0 milestone

### Progress

```
v2.0 Hypothesis Testing Suite
[░░░░░░░░░░░░░░░░░░░░] 0/11 phases (0%)

Phase 28: V2 Structure Setup      [READY]
Phase 29: H1 Cash Holdings Vars   [BLOCKED by 28]
Phase 30: H2 Investment Vars      [BLOCKED by 28]
Phase 31: H3 Payout Policy Vars   [BLOCKED by 28]
Phase 32: Econometric Infra       [BLOCKED by 28]
Phase 33: H1 Regression           [BLOCKED by 29, 32]
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
| Phases Complete | 27/27 | 0/11 |
| Plans Complete | 143/143 | 0/TBD |
| Requirements Mapped | 30/30 | 55/55 |
| Scripts CLI-Ready | 21/21 | — |

## Session Continuity

### Last Session (2026-02-04)

**Completed:**
- Requirements gathered and validated (55 requirements, 8 categories)
- Research summary completed (HIGH confidence, no new dependencies)
- Roadmap created (11 phases, 28-38)
- STATE.md updated with v2.0 context

**Next Session:**
- Run `/gsd-plan-phase 28` to create plans for V2 Structure Setup
- Execute Phase 28 plans to create folder structure
- Proceed to variable construction phases (29-31)

---
*Last updated: 2026-02-04*
