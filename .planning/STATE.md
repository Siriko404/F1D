# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Every hypothesis test must produce verifiable, reproducible regression results exactly as specified in the methodology
**Current focus:** v2.0 Hypothesis Testing Suite — CONCLUDED (all hypotheses tested showed null results)

## Current Position

Phase: 52 - LLM Literature Review & Novel Hypothesis Discovery
Plan: 01 of 5 complete
Status: In progress — Phase 52 active
Last activity: 2026-02-06 — Completed 52-01-PLAN.md (Literature Review & Evidence Matrix)

### Progress

```
v2.0 Hypothesis Testing Suite — CONCLUDED (all hypotheses tested)
[████████████████████████] 100% complete

v1.0 Foundation (27 phases)     [COMPLETE - 143/143 plans]
v2.0 Hypothesis Testing         [CONCLUDED - null results]

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
Phase 40: H5 Speech → Dispersion  [COMPLETE - 2/2 plans] → H5-A: NULL, H5-B: MIXED
Phase 41: Hypothesis Discovery    [ABANDONED - 4/4 plans] → Suite approach abandoned
Phase 42: H6 SEC Scrutiny (CCCL)  [COMPLETE - 2/2 plans] → H6-A: NULL, H6-B: NULL, H6-C: NULL
Phase 43-46: H7-H10 Hypotheses    [NOT PURSUED - abandoned with Phase 41]
Phase 52: LLM Lit Review & Novel Hyp [IN PROGRESS - 1/5 plans done]
```

## v2.0 Hypothesis Testing Results

**Conclusion**: No consistent statistical support for hypothesized relationships between managerial speech uncertainty and corporate financial policies or SEC scrutiny effects.

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
| H6-A | CCCL → ↓ Uncertainty | NULL | 0/6 (FDR-corrected) |
| H6-B | QA effect > Pres effect | NULL | 1/2 QA effects larger |
| H6-C | CCCL → ↓ Uncertainty Gap | NULL | p=0.22 |

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
- **2026-02-06**: Phase 52 started — "LLM Literature Review & Novel Hypothesis Discovery" (5-plan red-team/blue-team methodology for 5 extremely high-confidence hypotheses)

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
- [Phase 42-01 H6 Variables] H6 sample: 22,273 firm-year observations (2,357 firms, 2006-2018 after lag)
- [Phase 42-01 H6 Variables] Primary instrument: shift_intensity_mkvalt_ff48 (FF48 x market value, normalized 0-1)
- [Phase 42-01 H6 Variables] 6 CCCL variants available: FF48/Sales, FF12/Market Value, FF12/Sales, SIC2/Market Value, SIC2/Sales
- [Phase 42-01 H6 Variables] Aggregate speech measures to firm-year level to match CCCL frequency
- [Phase 42-01 H6 Variables] Lagged CCCL (t-1) via groupby().shift(1) ensures temporal ordering for causal identification
- [Phase 42-01 H6 Variables] Uncertainty_Gap = QA_Uncertainty - Pres_Uncertainty captures spontaneous vs prepared speech
- [Phase 42-02 H6 Regression] H6-A NOT SUPPORTED: 0/6 measures significant after FDR correction (Benjamini-Hochberg)
- [Phase 42-02 H6 Regression] H6-B NOT SUPPORTED: Only 1/2 QA effects larger than Pres effects
- [Phase 42-02 H6 Regression] H6-C NOT SUPPORTED: Uncertainty gap regression beta=-0.079, p=0.22
- [Phase 42-02 H6 Regression] Pre-trends test FAILED: CCCL_{t+2} (p=0.012) and CCCL_{t+1} (p=0.038) significant - anticipatory effects detected
- [Phase 42-02 H6 Regression] All 6 CCCL instrument variants tested for robustness - qualitatively similar negative but insignificant effects
- [Phase 43 Added] New hypothesis testing uncertainty dynamics (velocity, acceleration, jerk) as predictors — explores rate-of-change rather than levels
- [Phase 52 Added] LLM Literature Review & Novel Hypothesis Discovery — exhaustive lit review, data mapping, red-team/blue-team verification for 5 extremely high-confidence novel hypotheses
- [Phase 52-02 Feasibility] Kill threshold: <5K observations OR <80% power for small effects (f2=0.02)
- [Phase 52-02 Feasibility] Within-firm variation REQUIRED for primary IVs (H1-H6 lesson: dictionary measures fail with Firm FE)
- [Phase 52-02 Feasibility] Dictionary measures NOT recommended as primary IVs due to low within-firm variance
- [Phase 52-02 Feasibility] SEC Letters + Earnings Calls combination has highest novelty AND feasibility (50K-70K obs, >99% power)
- [Phase 52-02 Feasibility] HIGH feasibility directions: SEC Letter Topics → Call Shift, Narrative Inconsistency, LLM Evasiveness, PRisk×Uncertainty interaction
- [Phase 52-02 Feasibility] LOW feasibility: CEO Turnover (1,059 events, ~65% power) - use as robustness only
- [Phase 52-01 Literature] 35+ papers catalogued from 2023-2026 on LLM financial text analysis
- [Phase 52-01 Literature] SEC comment letter literature NOT unexplored (111+ SSRN papers); novelty requires specific combinations
- [Phase 52-01 Evidence Matrix] 7 IV categories × 6 DV categories: 18 TESTED, 8 PARTIAL, 16 GAP, 3 NULL
- [Phase 52-01 Top 5 Gaps] SEC topics→call shift (0.99), Narrative inconsistency (0.96), PRisk×Uncertainty (0.95), Correspondence resolution (0.94), Q&A relevance (0.91)
- [Phase 52-01 Gap Ranking] Weights: Novelty 0.35, Feasibility 0.35, Confidence 0.30; threshold ≥0.85 for "extremely high confidence"
- [Phase 52-01 Anti-Novelty] "First to use GPT-4" is NOT novel; LLM is tool, hypothesis must be novel

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

- **H6 pre-trends violation:** Significant future CCCL effects (p<0.05) suggest potential anticipatory effects or violation of parallel trends assumption, weakening causal interpretation
- **H6 null results:** All three H6 hypotheses (A, B, C) not supported; pattern of null results continues across H1-H6
- **Identification concerns:** The CCCL shift-share instrument shows significant leads at t+1 and t+2, which is concerning for the research design

## Performance Metrics

| Metric | v1.0 Final | v2.0 Final |
|--------|------------|------------|
| Phases Complete | 27/27 | 15/15 (3 cancelled, 4 abandoned) |
| Plans Complete | 143/143 | 17/17 active |
| Requirements Complete | 30/30 | 60/60 active (15 not pursued) |
| Scripts CLI-Ready | 21/21 | 10/10 |
| Hypotheses Supported | — | 0/6 (null results) |

## Session Continuity

### Current Session (2026-02-06)

**Phase 52 Started:**
- Completed 52-01: Literature Review & Evidence Matrix
- Catalogued 35+ papers from 2023-2026 on LLM finance
- Built 7×6 evidence matrix (18 TESTED, 8 PARTIAL, 16 GAP)
- Identified Top 10 literature gaps ranked by novelty + feasibility
- Confirmed SEC comment letter literature is NOT unexplored (111+ papers)
- True novelty requires data integration or unexplored IV-DV combinations

**Phase 52-01 Key Decisions:**
- SEC letter analysis novelty refined: must be specific combinations
- Top 5 priority gaps: SEC topics→call shift, narrative inconsistency, PRisk×uncertainty, correspondence resolution, Q&A relevance
- Gap ranking: Novelty (0.35) + Feasibility (0.35) + Confidence (0.30)

**Next:** 52-02-PLAN.md (Data Feasibility Verification)

---
*Last updated: 2026-02-06 (52-01 Literature Review complete)*
