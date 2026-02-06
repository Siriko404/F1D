# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Every hypothesis test must produce verifiable, reproducible regression results exactly as specified in the methodology
**Current focus:** v2.0 Hypothesis Testing Suite — H1-H3 null results; Phase 40 (H5) context complete; Phase 41 (Hypothesis Suite Discovery) added

## Current Position

Phase: 41 - Hypothesis Suite Discovery
Plan: —
Status: PLANNED — 4 plans in 4 waves ready for execution
Last activity: 2026-02-05 — Phase 41 plans created (literature review, data feasibility, power analysis, hypothesis selection)

### Progress

```
v2.0 Hypothesis Testing Suite — CONCLUDED (H1-H3 null)
[████████████████████] 8/8 active phases (100%)

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

v2.0 New Hypothesis — ACTIVE
Phase 40: H5 Speech → Analyst Dispersion [CONTEXT COMPLETE - 0/TBD plans]
Phase 41: Hypothesis Suite Discovery [PLANNED - 4/4 plans in 4 waves]
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

**Implication**: Phases 36-38 (Robustness, Identification, Publication) cancelled as scientifically inappropriate for null results.

## Phase 40: H5 New Hypothesis

**Hypothesis (H5-A):** Hedging language (weak modal verbs: may/might/could) in Q&A predicts higher analyst forecast dispersion, even after controlling for general uncertainty words.

**Why High Confidence:**
- General uncertainty → dispersion is ESTABLISHED (Loughran & McDonald 2011)
- Novel contribution: Does **Weak Modal** (hedging) add beyond general uncertainty?
- Dispersion is direct measure of information processing disagreement
- Data already available (IBES, Compustat, Transcripts)

**Key Design Decisions (from 40-CONTEXT.md):**
- DV: Analyst Dispersion = STDEV / |MEANEST|, NUMEST ≥ 3, |MEANEST| ≥ 0.05
- Timing: Speech_t → Dispersion_{t+1} (next quarter)
- Primary IV: Manager_QA_Weak_Modal_pct (novel)
- Control for established effect: Manager_QA_Uncertainty_pct
- 9 control variables including Prior Dispersion, Earnings Surprise, Analyst Coverage
- FE: Firm + Year; SE: Clustered at firm level
- Robustness: Without lagged DV, without NUMEST, CEO-only measures

## Key Constraints

- Use existing sample (firms, time period) from v1.0 implementation
- Use existing text measures (speech uncertainty) from Step 2 outputs
- All V2 scripts in SEPARATE folders: `2_Scripts/3_Financial_V2/`, `2_Scripts/4_Econometric_V2/`
- Outputs to `4_Outputs/3_Financial_V2/`, `4_Outputs/4_Econometric_V2/`
- Logs to `3_Logs/3_Financial_V2/`, `3_Logs/4_Econometric_V2/`

## Accumulated Context

### Roadmap Evolution

- **2026-02-05**: Phases 36-38 cancelled (null results from H1-H3)
- **2026-02-05**: Phase 40 added — "H5 Speech Uncertainty Predicts Analyst Dispersion" (novel hypothesis with higher confidence)
- **2026-02-05**: Phase 40 context discussion completed with full specification
- **2026-02-05**: Phase 41 added — "Hypothesis Suite Discovery" (deep literature review for novel, data-feasible, high-confidence hypotheses)

### Decisions

- [v2.0 Roadmap] 11 phases (28-38) covering 55 requirements; Phase 40 added as new hypothesis
- [v2.0 Roadmap] Phase numbering continues from v1.0 (ended at Phase 27)
- [v2.0 Roadmap] Variables phases (29-31) can parallelize after structure setup
- [v2.0 Roadmap] Regression phases (33-35) can parallelize after econometric infrastructure
- [v2.0 Research] No new dependencies needed - existing pandas/statsmodels/linearmodels stack sufficient
- [Phase 40 Context] Primary IV: Manager_QA_Weak_Modal_pct (novel — LM separates weak modals from uncertainty)
- [Phase 40 Context] Control for established effect: Manager_QA_Uncertainty_pct (so Weak Modal is incremental)
- [Phase 40 Context] DV: Analyst Dispersion = STDEV / |MEANEST|, NUMEST ≥ 3, |MEANEST| ≥ 0.05, 1%/99% winsorized
- [Phase 40 Context] Timing: Speech_t → Dispersion_{t+1} (next quarter, causal design)
- [Phase 40 Context] Controls: Prior Dispersion, Earnings Surprise, Analyst Coverage, Firm Size, Earnings Volatility, Loss Dummy, Tobin's Q, Leverage
- [Phase 40 Context] FE: Firm + Year; SE: Clustered at firm level
- [Phase 40 Context] Robustness: Without lagged DV (Nickell bias), without NUMEST (bad control), CEO-only measures
- [Phase 40 Red Team] General uncertainty → dispersion is established; Weak Modal as primary IV is novel contribution
- [Phase 40 Red Team] If Weak Modal insignificant, frame as "hedging does not add beyond uncertainty" — still publishable

### From v1.0 (carry forward)

- Stats inline per script (self-contained replication)
- Pipeline follows CLAUDE.md conventions (1_Inputs, 2_Scripts, 3_Logs, 4_Outputs)
- Timestamp-based output resolution (symlinks removed in Phase 27)
- All 21 scripts support CLI with --help and --dry-run
- get_latest_output_dir() for reading prerequisite outputs

### Known Pitfalls (from research)

1. **FE Collinearity Trap:** Firm + industry FE are redundant (firms don't change industries). Use `drop_absorbed=False, check_rank=True`
2. **Interaction Multicollinearity:** Always center continuous variables before creating interactions
3. **Weak Instruments in 2SLS:** F < 10 on first stage means 2SLS is more biased than OLS. Enforce F > 10 programmatically
4. **Nickell Bias:** Including lagged DV with Firm FE creates bias ≈ 1/T. With T=17, bias ≈ 6% — acceptable but include robustness without lagged DV
5. **Bad Control:** Analyst coverage (NUMEST) is endogenous — include robustness without it

### Blockers/Concerns

None currently.

## Performance Metrics

| Metric | v1.0 Final | v2.0 Final |
|--------|------------|------------|
| Phases Complete | 27/27 | 8/8 active (3 cancelled) |
| Plans Complete | 143/143 | 13/13 |
| Requirements Complete | 30/30 | 40/40 active (15 not pursued) |
| Scripts CLI-Ready | 21/21 | 8/8 |
| Hypotheses Supported | — | 0/3 (null results) |

## Session Continuity

### Last Session (2026-02-05)

**Completed:**
- v2.0 Milestone concluded with null hypothesis results for H1-H3
- Phases 36-38 cancelled (Robustness, Identification, Publication) — not scientifically meaningful for null results
- All regression outputs preserved in 4_Outputs/4_Econometric_V2/ for documentation
- Phase 40 (H5) context discussion completed with full specification

**Phase 40 Context Discussion Summary:**
- Literature review confirmed general uncertainty → dispersion is established
- Identified Weak Modal (hedging verbs) as novel primary IV
- Specified DV: Analyst Dispersion with NUMEST ≥ 3, |MEANEST| ≥ 0.05
- Timing: Speech_t → Dispersion_{t+1} (forward-looking)
- 9 control variables including Prior Dispersion (lagged DV)
- Red-teamed specification: addressed Nickell bias, bad control, novelty concerns
- Created 40-CONTEXT.md with complete specification

**Regression Results Summary (H1-H3):**
- H1 (Cash Holdings): Primary spec N=16,667-21,690, R²=0.128-0.133. H1a: 0/6, H1b: 1/6
- H2 (Investment Efficiency): Primary spec N=256K-342K, R²=0.002-0.003. H2a: 0/6, H2b: 0/6
- H3 (Payout Policy): Primary spec N=180K-244K, R²=0.021-0.045. H3a: 1/6, H3b: 0/6

**Interpretation:**
The speech uncertainty measures derived from earnings call transcripts do not systematically predict corporate financial policies as theorized. Phase 40 (H5) tests a different mechanism: speech → analyst disagreement (information processing).

**Next Session:**
- Plan Phase 40: Break down into executable plans
- Define H5 requirements (H5-01 through H5-10)
- Create 4.5_H5DispersionRegression.py script

---
*Last updated: 2026-02-05 (Phase 41 added)*
