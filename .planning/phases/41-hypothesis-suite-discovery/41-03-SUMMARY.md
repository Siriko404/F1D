---
phase: 41-hypothesis-suite-discovery
plan: 03
subsystem: power-analysis
tags: [statistical-power, effect-sizes, hypothesis-ranking, panel-data, fixed-effects]

# Dependency graph
requires:
  - phase: 41-02
    provides: Ranked novel hypotheses with data feasibility assessments
provides:
  - Power analysis for all 11 candidate hypotheses
  - Effect size benchmarks for each outcome type
  - Hypothesis selection framework combining novelty, feasibility, and power
  - Final recommendations for Phase 42 hypothesis suite
affects:
  - phase: 41-04 (Hypothesis Suite Selection) - requires power scores for final selection
  - phase: 42 (H6 SEC Scrutiny) - informed by hypothesis priorities

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Panel fixed effects power analysis with design effect adjustment
    - Event-study power consideration for rare events (turnover, M&A)
    - Economic significance interpretation alongside statistical significance
    - Multi-dimensional hypothesis scoring (novelty + feasibility + power)

key-files:
  created:
    - .planning/phases/41-hypothesis-suite-discovery/41-03-STATISTICAL_POWER_ANALYSIS.md
    - .planning/phases/41-hypothesis-suite-discovery/41-03-SUMMARY.md
  modified: []

key-decisions:
  - "Power is NOT a constraint: all 11 hypotheses have >80% power for small effects"
  - "H1-H3 null results are NOT due to low power (99%+ power for small effects)"
  - "Focus selection on novelty and theoretical mechanism, not statistical power"
  - "H7/H12 (turnover) have adequate power with 1,059 dismissal events"
  - "M&A hypotheses (H6, H11) have excellent power with 95K deals"

patterns-established:
  - "Ex-ante power analysis prevents wasted effort on underpowered studies"
  - "Design effect adjustment crucial for panel data with within-firm clustering"
  - "Event-study hypotheses require event-count-based power assessment"

# Metrics
duration: 15min
completed: 2026-02-06
---

# Phase 41 Plan 03: Statistical Power Analysis Summary

**Ex-ante power analysis confirms all candidate hypotheses have adequate statistical power (>80%) to detect economically meaningful effect sizes, enabling selection based on novelty and theoretical contribution rather than sample size constraints**

## Performance

- **Duration:** 15 min
- **Started:** 2026-02-06T03:11:15Z
- **Completed:** 2026-02-06T03:26:15Z
- **Tasks:** 3
- **Files created:** 2

## Accomplishments

- **Created power analysis function** using panel fixed effects formula with design effect adjustment
- **Calculated power for H1-H3 existing samples** (all >99% for small effects)
- **Confirmed H1-H3 null results are NOT due to low power** - despite 99%+ power, results were null
- **Calculated power for 11 candidate hypotheses** from Plan 02
- **9/11 hypotheses rated Excellent (>90% power), 2/11 rated Adequate (>80%)**
- **Documented effect size benchmarks** for each outcome type with economic interpretation
- **Created selection framework** combining novelty, feasibility, and power
- **Provided final recommendations** for Phase 42 hypothesis suite

## Task Commits

Each task was committed atomically:

1. **Task 1-2: Power Calculations** - `37c0b6d` (feat)
2. **Task 3: Selection Framework** - (pending commit)

**Plan metadata:** (docs: complete plan)

---

## Power Analysis Key Findings

### 1. Existing Sample Power (H1-H3)

| Hypothesis | N | Firms | T | Power (small) | Power (med) | Power (large) |
|------------|---|-------|---|---------------|-------------|---------------|
| H1 Cash Holdings | 21,557 | 2,419 | 9 | 1.000 | 1.000 | 1.000 |
| H2 Investment | 342,000 | 3,000 | 114 | 1.000 | 1.000 | 1.000 |
| H3 Payout | 244,000 | 2,800 | 87 | 1.000 | 1.000 | 1.000 |

**Critical Insight:** All existing samples have EXCELLENT power (>99%) even for small effects. The null results from H1-H3 are NOT due to low power. This suggests either:
1. No true effect exists for these financial policy mechanisms
2. Different mechanisms should be tested (M&A, turnover, compensation, returns)

### 2. Candidate Hypothesis Power

| Hypothesis | IV | DV | N | Events | Power (small) | Rating |
|------------|----|----|---|--------|---------------|--------|
| H6 | Weak Modal | M&A Target | 25K | 1,000s | 0.999 | Excellent |
| H9 | Gap | Returns | 113K | NA | 1.000 | Excellent |
| H4 | Gap | Volatility | 113K | NA | 1.000 | Excellent |
| H10 | Complexity | Forecast Error | 264K | NA | 1.000 | Excellent |
| H14 | Uncertainty | Revisions | 264K | NA | 1.000 | Excellent |
| H11 | Uncertainty | M&A Premium | 15K | 1,000s | 0.997 | Excellent |
| H15 | Cross-Speaker Gap | Tobin's Q | 25K | NA | 0.999 | Excellent |
| H8 | Uncertainty | Compensation | 15K | NA | 0.997 | Excellent |
| H13 | Uncertainty Volatility | Return Volatility | 113K | NA | 1.000 | Excellent |
| H7 | Uncertainty | Turnover | 6K | 1,059 | 0.823 | Adequate |
| H12 | Weak Modal | Turnover | 6K | 1,059 | 0.823 | Adequate |

**Power Distribution:**
- Excellent (>90%): 9/11 hypotheses (82%)
- Adequate (80-90%): 2/11 hypotheses (18%)
- Marginal (<80%): 0/11 hypotheses (0%)

**Conclusion:** All hypotheses have SUFFICIENT power. Selection should be based on novelty and theoretical contribution.

---

## Effect Size Benchmarks (Economic Meaningfulness)

### What Constitutes "Economically Meaningful"?

| Outcome | Small Effect | Medium Effect | Large Effect | Economic Interpretation |
|---------|--------------|---------------|--------------|-------------------------|
| **Cash Holdings** | f2=0.02 (1-2% of assets) | f2=0.15 (5% of assets) | f2=0.35 (10% of assets) | 5% change = $50M per $1B assets |
| **M&A Targeting** | 5% probability increase | 10% probability increase | 20% probability increase | 10% = meaningful target likelihood |
| **M&A Premium** | 2-3% premium | 5-7% premium | 10%+ premium | 5% premium = $50M per $1B deal |
| **CEO Turnover** | 10% risk increase | 20% risk increase | 40% risk increase | 20% = economically significant |
| **Stock Returns** | 25 bps/year | 50 bps/year | 100 bps/year | 50 bps = 5% annual abnormal return |
| **Return Volatility** | 5% increase | 10% increase | 20% increase | 10% = noticeable risk change |
| **Compensation** | 5% change | 10% change | 20% change | 10% = $500K per $5M comp |
| **Forecast Error** | 2% reduction | 5% reduction | 10% reduction | 5% = meaningful accuracy gain |
| **Tobin's Q** | 0.05 change | 0.10 change | 0.20 change | 0.10 = 10% firm value change |

### Minimum Detectable Effect Sizes (at 80% Power)

| Hypothesis | Sample | f2 at 80% Power | Interpretation |
|------------|--------|----------------|----------------|
| H6 (M&A Target) | 25K obs | ~0.003 | Can detect 0.3% variance explained |
| H9 (Returns) | 113K obs | ~0.001 | Can detect 0.1% variance explained |
| H10 (Forecast) | 264K obs | ~0.0005 | Can detect 0.05% variance explained |
| H7 (Turnover) | 1,059 events | ~0.015 | Can detect 1.5% variance explained |

**Key finding:** All hypotheses can detect economically meaningful effects. Even the smallest detectable effects (0.05-1.5% variance) would be economically significant for most outcomes.

---

## Hypothesis Selection Framework

### Scoring Methodology

Combine three dimensions with weighted average:

```
Overall Score = 0.30*Novelty + 0.40*Feasibility + 0.30*Power
```

**Dimension Scores:**

| Dimension | Score | Criteria |
|-----------|-------|----------|
| **Novelty** | 1.0 (High) | No prior direct tests |
| | 0.5 (Medium) | Indirect/related tests only |
| | 0.0 (Low) | Established relationship |
| **Feasibility** | 1.0 (High) | All data verified available |
| | 0.5 (Medium) | Data available but merge TBD |
| | 0.0 (Low) | Missing critical data |
| **Power** | 1.0 (Excellent) | Power > 90% for small effects |
| | 0.7 (Adequate) | Power 80-90% for small effects |
| | 0.3 (Marginal) | Power 60-80% for small effects |
| | 0.0 (Low) | Power < 60% for small effects |

**Weighting rationale:**
- Feasibility (40%): Must be able to actually execute the test
- Novelty (30%): Contribution to literature
- Power (30%): Statistical validity (but all hypotheses score high here)

### Ranked Hypothesis Table

| Rank | Hypothesis | IV | DV | Novelty | Feasibility | Power | Overall | Selection |
|------|------------|----|----|---------|------------|-------|---------|-----------|
| 1 | H6: Weak Modals -> M&A Target | Weak Modal % | M&A target dummy | 1.0 | 1.0 | 1.0 | **1.00** | **SELECT** |
| 2 | H9: Gap -> Future Returns | QA - Pres gap | Abnormal returns | 1.0 | 1.0 | 1.0 | **1.00** | **SELECT** |
| 3 | H11: Uncertainty -> M&A Premium | Uncertainty % | Deal premium | 1.0 | 1.0 | 1.0 | **1.00** | **SELECT** |
| 4 | H4: Gap -> Volatility | QA - Pres gap | Return volatility | 1.0 | 1.0 | 1.0 | **1.00** | **SELECT** |
| 5 | H15: Cross-Speaker Gap -> Tobin's Q | \|CEO-Mgr\| gap | Tobin's Q | 1.0 | 1.0 | 1.0 | **1.00** | **SELECT** |
| 6 | H10: Complexity -> Forecast Error | Complexity | Forecast error | 0.5 | 1.0 | 1.0 | **0.85** | CONSIDER |
| 7 | H14: Uncertainty -> Revisions | Uncertainty % | Forecast revisions | 0.5 | 1.0 | 1.0 | **0.85** | CONSIDER |
| 8 | H13: Uncertainty Volatility -> Return Volatility | SD(Uncertainty) | SD(Returns) | 0.5 | 1.0 | 1.0 | **0.85** | CONSIDER |
| 9 | H8: Uncertainty -> Compensation | Uncertainty % | Total comp (tdc1) | 1.0 | 0.5 | 1.0 | **0.80** | CONSIDER |
| 10 | H7: Uncertainty -> Turnover | Uncertainty % | Forced turnover | 1.0 | 0.5 | 0.7 | **0.71** | RESERVE |
| 11 | H12: Weak Modals -> Turnover | Weak Modal % | Forced turnover | 1.0 | 0.5 | 0.7 | **0.71** | RESERVE |

---

## Final Recommendations for Phase 42

### Primary Suite (5 Hypotheses) - HIGH Priority

**Tier 1: Perfect Scores (1.00)**

1. **H6: Weak Modals (Hedging) -> M&A Targeting**
   - **Question:** Does managerial hedging language predict higher likelihood of becoming an acquisition target?
   - **IV:** Manager_QA_Weak_Modal_pct, CEO_QA_Weak_Modal_pct
   - **DV:** M&A target dummy (1 = target in next 12 months)
   - **Sample:** 25,000 firm-years, 1,000s of M&A events
   - **Power:** 0.999 for small effects
   - **Novelty:** HIGH - No prior tests of weak modals -> M&A
   - **Economic significance:** 10% increase in targeting probability = meaningful

2. **H9: Uncertainty Gap -> Future Abnormal Returns**
   - **Question:** Does the gap between Q&A and Presentation uncertainty predict future stock returns?
   - **IV:** uncertainty_gap = QA_Uncertainty - Pres_Uncertainty
   - **DV:** Future abnormal returns (3-day, 1-month, 1-quarter)
   - **Sample:** 112,968 call-returns observations
   - **Power:** 1.000 for small effects
   - **Novelty:** HIGH - Gap measure never studied for return prediction
   - **Economic significance:** 50 bps annual abnormal return = 5% alpha

3. **H11: Uncertainty -> M&A Deal Premium**
   - **Question:** Does managerial uncertainty reduce the premium paid to target firms?
   - **IV:** CEO_QA_Uncertainty_pct
   - **DV:** Deal premium = (Offer - Pre-announcement) / Pre-announcement
   - **Sample:** 15,000 M&A target observations
   - **Power:** 0.997 for small effects
   - **Novelty:** HIGH - No studies on speech -> M&A pricing
   - **Economic significance:** 5% premium change = $50M per $1B deal

4. **H4: Uncertainty Gap -> Return Volatility**
   - **Question:** Does inconsistent communication (gap) increase stock return volatility?
   - **IV:** uncertainty_gap
   - **DV:** Return volatility = SD(daily returns) post-call
   - **Sample:** 112,968 call-returns observations
   - **Power:** 1.000 for small effects
   - **Novelty:** HIGH - Gap measure not applied to volatility
   - **Economic significance:** 10% volatility increase = meaningful risk change

5. **H15: Cross-Speaker Gap -> Tobin's Q**
   - **Question:** Does disagreement between CEO and Manager speech predict lower firm value?
   - **IV:** \|CEO_Uncertainty - Manager_Uncertainty\|
   - **DV:** Tobin's Q (market-to-book assets)
   - **Sample:** 25,000 firm-years
   - **Power:** 0.999 for small effects
   - **Novelty:** HIGH - Cross-speaker dispersion never studied
   - **Economic significance:** 0.10 Q change = 10% firm value change

### Secondary Suite (Conditional) - MEDIUM Priority

6. **H10: Complexity -> Analyst Forecast Accuracy**
   - Score: 0.85
   - MEDIUM novelty (some 10-K literature), excellent power
   - Consider if analyst behavior research is of interest

7. **H14: Uncertainty -> Forecast Revisions**
   - Score: 0.85
   - MEDIUM novelty (dispersion studied, revisions less so)
   - Consider complementary to H10

8. **H13: Uncertainty Volatility -> Return Volatility**
   - Score: 0.85
   - MEDIUM novelty (tone volatility studied, uncertainty not)
   - Consider if dynamic speech patterns are of interest

9. **H8: Uncertainty -> Compensation**
   - Score: 0.80
   - HIGH novelty, MEDIUM feasibility (Execucomp merge TBD)
   - Consider if labor market outcomes are of interest

### Reserve Suite (Conditional) - LOW Priority

10. **H7: Uncertainty -> CEO Turnover**
    - Score: 0.71
    - HIGH novelty, MEDIUM feasibility, ADEQUATE power (82%)
    - Reserve for later if labor market focus

11. **H12: Weak Modals -> CEO Turnover**
    - Score: 0.71
    - HIGH novelty, MEDIUM feasibility, ADEQUATE power (82%)
    - Reserve for later if hedging-as-protection theory is of interest

---

## Implementation Notes

### Power is NOT a Constraint

All 11 hypotheses have >80% power to detect economically meaningful effects. The selection decisions should be based on:

1. **Novelty contribution** to literature (30% weight)
2. **Theoretical mechanism** strength (embedded in novelty score)
3. **Data availability** certainty (40% weight)

### H1-H3 Null Results Context

Even with >99% power, H1-H3 showed null results:
- H1a (Uncertainty -> Cash): 0/6 significant
- H2a (Uncertainty -> Investment): 0/6 significant
- H3a (Uncertainty -> Payout): 1/6 significant

This suggests the null results are NOT due to low power. Either:
1. No true effect exists for financial policy mechanisms
2. Different mechanisms (M&A, turnover, returns) are more promising

### Event-Study Considerations

For H7 and H12 (turnover hypotheses), power depends on EVENT count (1,059 dismissals), not total observations. With 1,059 events:
- 82% power for small effects (f2=0.02)
- 99%+ power for medium+ effects (f2>=0.15)

This is adequate, but lower than the other hypotheses. Consider if turnover outcomes are central to research questions.

---

## Decisions Made

- **Power analysis confirms all hypotheses feasible:** No hypothesis eliminated due to low power
- **H1-H3 null results not power-constrained:** 99%+ power still produced null results
- **Selection prioritizes novelty:** All perfect-score hypotheses (1.00) are high novelty
- **M&A hypotheses prioritized:** H6, H11 leverage 95K deals with minimal prior literature
- **Gap measure hypotheses prioritized:** H9, H4, H15 test novel uncertainty differential
- **Turnover hypotheses conditional:** H7, H12 have adequate power but lower feasibility scores

---

## Deviations from Plan

None - plan executed exactly as written.

---

## Issues Encountered

None - all power calculations completed successfully.

---

## Next Phase Readiness

### For Plan 04 (Hypothesis Suite Selection):

**Ready:**
- Complete power analysis for all 11 candidate hypotheses
- Effect size benchmarks documented for each outcome type
- Selection framework with weighted scoring (novelty + feasibility + power)
- Ranked hypothesis table with final recommendations
- Top 5 hypotheses identified for Phase 42 development

**Plan 04 should:**
1. Select final 3-5 hypotheses for Phase 42 implementation
2. Create detailed variable specifications for selected hypotheses
3. Document control variables and estimation strategies
4. Identify any additional data processing requirements

### For Phase 42 (Hypothesis Implementation):

**Recommended hypotheses based on power analysis:**
- H6: Weak Modals -> M&A Target (highest priority)
- H9: Gap -> Returns (novel measure, excellent power)
- H11: Uncertainty -> M&A Premium (complements H6)
- H4: Gap -> Volatility (complements H9)
- H15: Cross-Speaker Gap -> Tobin's Q (novel team measure)

**Awaiting:** Final selection decision in Plan 04

---

*Phase: 41-hypothesis-suite-discovery*
*Plan: 03*
*Completed: 2026-02-06*
