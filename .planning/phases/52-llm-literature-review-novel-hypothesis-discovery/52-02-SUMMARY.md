---
phase: 52-llm-literature-review-novel-hypothesis-discovery
plan: 02
subsystem: research
tags: [data-feasibility, power-analysis, within-firm-variation, sample-size, linkage]

# Dependency graph
requires:
  - phase: 52-01
    provides: Literature gap analysis and evidence matrix
  - phase: 41
    provides: Prior feasibility estimates (H5, H6 verified counts)
  - phase: 42
    provides: CCCL sample verification (22,273 firm-years)
provides:
  - Complete feasibility matrix for all IV-DV combinations
  - Power analysis with small effect thresholds
  - Within-firm variation assessment for measure types
  - Kill criteria (<5K obs, <80% power) application
  - Recommendations for Blue Team hypothesis generation
affects: [52-03, 52-04, 52-05]

# Tech tracking
tech-stack:
  added: []
  patterns: [feasibility-rating-system, kill-threshold-criteria]

key-files:
  created:
    - .planning/phases/52-llm-literature-review-novel-hypothesis-discovery/52-02-FEASIBILITY-MATRIX.md
  modified: []

key-decisions:
  - "Kill threshold: <5K observations OR <80% power for small effects (f2=0.02)"
  - "High within-firm variation required for IVs (lesson from H1-H6 null results)"
  - "Dictionary measures NOT recommended as primary IVs due to low within-firm variance"
  - "SEC Letters + Earnings Calls combination has highest novelty AND feasibility"

patterns-established:
  - "Feasibility Rating: HIGH (>20K, >95% power, high variation) / MEDIUM (5-20K, 80-95%) / LOW (<5K, <80%)"
  - "Within-Firm Variation assessment required before hypothesis selection"

# Metrics
duration: 2min
completed: 2026-02-06
---

# Phase 52 Plan 02: Data Feasibility Verification Summary

**Complete feasibility matrix documenting 11 datasets, 9 IV-DV combinations with power analysis, and within-firm variation assessment addressing H1-H6 null results lesson**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-06T20:18:49Z
- **Completed:** 2026-02-06T20:21:15Z
- **Tasks:** 3/3
- **Files created:** 1

## Accomplishments

- Documented 11 datasets with exact observation counts (112K calls, 190K SEC letters, 354K PRisk obs)
- Mapped all linkage paths including complex multi-step joins (SEC → GVKEY → CRSP)
- Calculated temporal overlap for 9 dataset pairs (2005-2018 main window)
- Estimated sample sizes for 9 IV-DV combinations with power calculations
- Created feasibility rating system (HIGH/MEDIUM/LOW) with kill thresholds
- Addressed within-firm variation lesson from H1-H6 null results

## Task Commits

Each task was committed atomically:

1. **Task 1-3: Complete feasibility matrix** - `6808b4b` (docs)
   - All three tasks produced a single research document
   - Research phases produce documents, not code

**Note:** For research document phases, all tasks contribute to a single output file. This is the efficient approach for document creation.

## Files Created/Modified

- `.planning/phases/52-llm-literature-review-novel-hypothesis-discovery/52-02-FEASIBILITY-MATRIX.md` - Complete data feasibility verification matrix (324 lines)

## Decisions Made

1. **Kill Threshold:** <5,000 observations OR <80% power for small effects (f2=0.02)
   - Rationale: Below these thresholds, cannot reliably detect economically meaningful effects with Firm FE

2. **Within-Firm Variation Requirement:** Primary IVs must have HIGH within-firm variation
   - Rationale: H5 and H6 showed dictionary measures become insignificant with Firm FE due to low within-firm variance
   - Implication: Prefer event-driven, temporal, or context-specific measures over firm-trait-like measures

3. **Dictionary Measures NOT Recommended as Primary IVs**
   - Rationale: H1-H6 all null with Firm FE; dictionary measures have low within-firm variation
   - Alternative: Use LLM context-aware measures or first-differenced specifications

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Key Feasibility Findings

### Highest-Feasibility Combinations (PURSUE)

| Rank | IV → DV | Sample | Power | Variation | Rating |
|------|---------|--------|-------|-----------|--------|
| 1 | SEC Letter Topics → Earnings Call Shift | 50K-70K | >99% | HIGH | **HIGH** |
| 2 | Narrative Inconsistency → Volatility | 50K+ | >99% | HIGH | **HIGH** |
| 3 | SEC Resolution Quality → Returns | 30K-50K | >99% | HIGH | **HIGH** |
| 4 | LLM Evasiveness → Returns | 100K+ | >99% | HIGH | **HIGH** |
| 5 | PRisk × Uncertainty → Investment | 30K+ | >99% | HIGH | **HIGH** |

### Lowest-Feasibility Combinations (AVOID)

| IV | DV | Reason | Rating |
|----|----|--------|--------|
| Dictionary Uncertainty | Any with Firm FE | Low within-firm variation | **LOW** |
| Any text measure | CEO Turnover | Only 1,059 events, ~65% power | **LOW** |
| Tone/Sentiment | Returns | Heavily studied, minimal novelty | AVOID |

## Next Phase Readiness

**Ready for Plan 52-03 (Blue Team - Hypothesis Generation):**
- Feasibility matrix provides instant lookup for any IV-DV combination
- Kill thresholds clearly defined for rapid elimination
- Within-firm variation guidance prevents repeating H1-H6 mistakes
- Top 5 highest-feasibility directions identified for prioritization

**No blockers or concerns.**

---
*Phase: 52-llm-literature-review-novel-hypothesis-discovery*
*Completed: 2026-02-06*
