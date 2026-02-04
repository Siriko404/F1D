# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Every script must produce verifiable, reproducible results with complete audit trails
**Current focus:** v2.0 Hypothesis Testing Suite

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-02-04 — Milestone v2.0 started

## v2.0 Milestone Goals

**Hypothesis 1:** Speech Uncertainty & Precautionary Cash Holdings
- Vague managers hoard more cash
- Leverage moderates the effect (debt discipline)
- Regression: Cash/Assets ~ Uncertainty + Leverage + Uncertainty×Leverage + Controls + FEs

**Hypothesis 2:** Speech Uncertainty & Investment Inefficiency
- Vagueness correlates with over/underinvestment
- Measure against Tobin's Q benchmarks
- Regression: Efficiency ~ Uncertainty + Leverage + Uncertainty×Leverage + Controls + FEs

**Hypothesis 3:** Speech Uncertainty & Payout Policy Stability
- Vague managers have volatile dividend policies
- Leverage promotes smoothing
- Regression: Stability ~ Uncertainty + Leverage + Uncertainty×Leverage + Controls + FEs

## Accumulated Context

### Decisions

- [v2.0 Init] Implementing all 3 hypotheses in single milestone
- [v2.0 Init] Major version (v2.0) selected for new hypothesis testing capability

### From v1.0 (carry forward)

- Stats inline per script (self-contained replication)
- Pipeline follows CLAUDE.md conventions (1_Inputs, 2_Scripts, 3_Logs, 4_Outputs)
- Timestamp-based output resolution (no symlinks)
- All 21 scripts support CLI with --help and --dry-run

### Blockers/Concerns

None currently.

---
*Last updated: 2026-02-04*
