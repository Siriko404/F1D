# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Every hypothesis test must produce verifiable, reproducible regression results exactly as specified in the methodology
**Current focus:** v2.0 Hypothesis Testing Suite — H1-H3 null results; Phase 40 (H5) complete; Phase 41 (Discovery) complete; Phases 42-46 planned (H6-H10)

## Current Position

Phase: 41 - Hypothesis Suite Discovery
Plan: 04
Status: COMPLETE — Hypothesis suite selected (H6-H10) with complete specifications; ROADMAP.md and REQUIREMENTS.md updated
Last activity: 2026-02-06 — Plan 41-04 executed, 5 hypotheses selected for Phases 42-46 implementation

### Progress

```
v2.0 Hypothesis Testing Suite — CONCLUDED (H1-H3 null), H5 null, H6-H10 selected
[████████████████████  ] 12/16 active phases (75%)

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
Phase 40: H5 Speech → Analyst Dispersion [COMPLETE - 2/2 plans] → H5-A: NOT SUPPORTED, H5-B: MIXED
Phase 41: Hypothesis Suite Discovery [COMPLETE - 4/4 plans] → H6-H10 selected
Phase 42: H6 Managerial Hedging → M&A Targeting [NOT PLANNED - 10 requirements]
Phase 43: H7 Uncertainty → CEO Turnover [NOT PLANNED - 10 requirements]
Phase 44: H8 Speech Clarity → Compensation [NOT PLANNED - 10 requirements]
Phase 45: H9 Uncertainty Gap → Returns [NOT PLANNED - 10 requirements]
Phase 46: H10 Complexity → Forecast Accuracy [NOT PLANNED - 10 requirements]
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
| H5-A | Hedging → ↑ Dispersion (beyond Uncertainty) | NOT SUPPORTED | 0/3 Weak Modal |
| H5-B | Uncertainty Gap → ↑ Dispersion | MIXED | Sig only w/o Firm FE |

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
- **2026-02-05**: Phase 42 added — "H6 SEC Scrutiny (CCCL) Reduces Manager Speech Uncertainty" (CCCL shift-share design using available data)
- **2026-02-06**: Phase 43 added — "Uncertainty Dynamics Predictors" (testing velocity, acceleration, jerk of speech uncertainty for predictive power)

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
- [Phase 40 Plan 01] IBES loading via PyArrow row-group aggregation for memory efficiency (25M+ rows)
- [Phase 40 Plan 01] CCM LINKPRIM='P' (string) not integer for primary link selection
- [Phase 40 Plan 01] GVKEY standardization to string with leading zeros (zfill(6)) for cross-dataset compatibility
- [Phase 40 Plan 01] Placeholder CUSIP filtering: 00000000, nan, NaN, None excluded
- [Phase 40 Plan 01] NumpyEncoder for JSON serialization of numpy types in stats.json
- [Phase 41-01 Data Inventory] 11 input sources verified: earnings calls (112K), LM dict (86K words), IBES (25.5M), Execucomp (370K), CEO dismissal (1,059 events), SDC M&A (95K deals), CRSP DSF (96 quarters), CCCL (145K)
- [Phase 41-01 Data Inventory] 1,785 text measure variables available (15 speaker roles x 8 categories x 3 contexts)
- [Phase 41-01 Feasibility] HIGH: Weak Modal -> M&A Target (95K deals), Stock Returns (CRSP), Analyst Dispersion (264K H5 verified)
- [Phase 41-01 Feasibility] MEDIUM: Weak Modal -> CEO Turnover (1,059 events), Compensation (4,170 firms)
- [Phase 41-02 Literature Review] 10 novel hypotheses identified, 6 Tier-1 (>=0.85) prioritized for power analysis
- [Phase 41-02 Literature Review] H6: Weak Modals->M&A Target (1.00), H9: Uncertainty Gap->Returns (1.00), H11: Uncertainty->M&A Premium (1.00), H4: Gap->Volatility (1.00), H15: Cross-Speaker->Q (0.85), H7: Uncertainty->Turnover (0.85)
- [Phase 41-02 Literature Review] Established relationships to skip: tone->returns (LM 2011), uncertainty->dispersion (Price 2012), H1-H3 null results
- [Phase 41-02 Literature Review] Evidence gaps: minimal literature on speech->M&A, speech->turnover, speech->compensation, gap->returns
- [Phase 41-03 Power Analysis] All 11 hypotheses have >80% power for small effects; 9/11 Excellent (>90%), 2/11 Adequate (80-90%)
- [Phase 41-03 Power Analysis] H1-H3 null results NOT due to low power (99%+ power confirmed)
- [Phase 41-03 Power Analysis] Perfect scores (1.00): H6, H9, H11, H4, H15 (SELECT for Phase 42)
- [Phase 41-03 Power Analysis] Effect size benchmarks: 5% cash/assets, 10% M&A probability, 50 bps returns, 20% turnover risk, 10% comp change
- [Phase 41-03 Power Analysis] H7/H12 (turnover) have adequate 82% power with 1,059 dismissal events; rated RESERVE
- [Phase 41-04 Hypothesis Suite Selection] Selected 5 hypotheses (H6-H10) for Phases 42-46 implementation
- [Phase 41-04 Hypothesis Suite Selection] H6: Managerial Hedging and M&A Targeting (score 1.00) - weak modals -> M&A likelihood/premium
- [Phase 41-04 Hypothesis Suite Selection] H7: CEO Vagueness and Forced Turnover Risk (score 0.85) - uncertainty -> forced turnover
- [Phase 41-04 Hypothesis Suite Selection] H8: Speech Clarity and Executive Compensation (score 0.85) - uncertainty -> total compensation/PPS
- [Phase 41-04 Hypothesis Suite Selection] H9: Uncertainty Gap and Future Stock Returns (score 1.00) - QA-Pres gap -> abnormal returns
- [Phase 41-04 Hypothesis Suite Selection] H10: Language Complexity and Analyst Forecast Accuracy (score 0.65) - complexity -> forecast error
- [Phase 41-04 Hypothesis Suite Selection] Reserved H11 (M&A Premium), H4 (Gap->Volatility), H15 (Cross-Speaker Gap) for future extension
- [Phase 41-04 Hypothesis Suite Selection] Renumbered existing SEC Scrutiny hypothesis to Phase 50 (reserved)
- [Phase 42-01 H6 Variables] CCCL instrument is ANNUAL (year column) not quarterly - merge on gvkey+year
- [Phase 42-01 H6 Variables] Aggregate speech measures to firm-year level to match CCCL frequency
- [Phase 42-01 H6 Variables] Lagged CCCL (t-1) via groupby().shift(1) ensures temporal ordering for causal identification
- [Phase 42-01 H6 Variables] Uncertainty_Gap = QA_Uncertainty - Pres_Uncertainty captures spontaneous vs prepared speech
- [Phase 42-01 H6 Variables] H6 sample: 22,273 firm-year observations (2,357 firms, 2006-2018 after lag)
- [Phase 42-01 H6 Variables] Primary instrument: shift_intensity_mkvalt_ff48 (FF48 x market value, normalized 0-1)
- [Phase 42-01 H6 Variables] 6 CCCL variants available: FF48/Sales, FF12/Market Value, FF12/Sales, SIC2/Market Value, SIC2/Sales
- [Phase 43 Added] New hypothesis testing uncertainty dynamics (velocity, acceleration, jerk) as predictors — explores rate-of-change rather than levels

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

### Current Session (2026-02-06)

**Completed:**
- Phase 41 Plan 04 executed successfully
- Selected 5 hypotheses (H6-H10) for Phases 42-46 implementation
- Created complete formal specifications for all 5 hypotheses (8 sections each)
  - H6: Managerial Hedging and M&A Targeting
  - H7: CEO Vagueness and Forced Turnover Risk
  - H8: Speech Clarity and Executive Compensation
  - H9: Uncertainty Gap and Future Stock Returns
  - H10: Language Complexity and Analyst Forecast Accuracy
- Updated ROADMAP.md with Phase 42-46 placeholders
- Updated REQUIREMENTS.md with 50 new requirements (10 per hypothesis)
- Created 41-04-SUMMARY.md with complete documentation

**Phase 41 Plan 04 Results:**
- 5 hypotheses selected from 11 candidates
- All selected have scores >= 0.85 (multi-dimensional: novelty + feasibility + power)
- Mechanism diversity: M&A targeting, CEO turnover, compensation, returns, analyst accuracy
- Requirements added: 50 total (105 total requirements now)
- Hypothesis H6 renumbered: H6 (M&A Targeting) takes Phase 42; SEC Scrutiny moved to Phase 50 (reserved)

**Next Session:**
- Choose which hypothesis to develop first (Phases 42-46 available)
- Run /gsd:plan-phase 42 (or 43-46) to break down hypothesis into plans
- Variable construction scripts needed for M&A, CEO turnover, compensation, returns, forecast accuracy

### Previous Session (2026-02-05)

**Phase 40 Plan 01 executed:**
- Created 3.5_H5Variables.py with memory-efficient IBES loading (PyArrow row groups)
- Generated H5_AnalystDispersion.parquet with 850,889 observations (264,504 complete cases)
- Implemented CCM CUSIP-GVKEY linking (LINKPRIM='P', 71.6% match rate)
- Computed forward-looking dispersion_lead (Speech_t → Dispersion_{t+1})
- Merged all 6 speech uncertainty measures and computed uncertainty_gap

**Phase 40 Plan 02 executed:**
- Created 4.5_H5DispersionRegression.py following H1 regression pattern
- Executed 28 regressions (6 measures x 4 specs + gap model)
- Primary spec: 0/3 Weak Modal measures significant
- Gap model: Significant only in pooled OLS, not with Firm FE
- Key finding: H5-A NOT supported; hedging does not add power beyond uncertainty

**H5 Regression Results:**
- Primary spec (Firm + Year FE): beta1(Weak_Modal) = -0.0124, p = 0.99
- Pooled OLS (no FE): Uncertainty significant, but not with Firm FE
- Interpretation: Speech-dispersion relationship driven by firm heterogeneity

---
*Last updated: 2026-02-06 (Phase 41 Plan 04 complete: Hypothesis suite H6-H10 selected for Phases 42-46 implementation with complete formal specifications)*
