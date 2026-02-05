# Phase 35: H3 Payout Policy Regression - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Run and validate OLS/2SLS regressions for H3 (Speech Uncertainty & Payout Policy). Test whether speech uncertainty correlates with dividend policy stability and flexibility, with leverage as a moderator. Variables already constructed in Phase 31.

</domain>

<decisions>
## Implementation Decisions

### Regression Pattern
- Follow H1/H2 pattern exactly: 6 uncertainty measures × 4 specifications × 2 DVs = 48 regressions
- 4 specifications: primary (Firm + Year FE), pooled, year_only, double_cluster
- 2 DVs: div_stability (primary), payout_flexibility (alternative)

### Hypothesis Testing
- One-tailed tests matching predicted direction:
  - H3a (Stability): β1 < 0 (vagueness reduces stability), β3 < 0 (leverage amplifies)
  - H3b (Flexibility): β1 > 0 (vagueness increases flexibility), β3 > 0 (leverage amplifies)
- Report "X/6 measures significant" per DV

### Output Structure
- `H3_Regression_Results.parquet` — all 48 regression results
- `stats.json` — N, R², F-stat, coefficients, p-values
- `H3_RESULTS.md` — human-readable summary with significance counts

### Null Result Handling
- Same framing as H1/H2: "No support found for H3" if 0/6 significant
- Document results factually without spin

### OpenCode's Discretion
- Exact control variable ordering in regression formula
- Console progress output formatting
- LaTeX table generation (if needed for publication phase)

</decisions>

<specifics>
## Specific Ideas

- Mirror 4.1_H1CashHoldingsRegression.py and 4.2_H2InvestmentEfficiencyRegression.py structure
- Merge H1 leverage data into H3 (same pattern as H2 regression)
- Use existing econometric infrastructure from Phase 32 (panel_ols.py, centering.py, diagnostics.py)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 35-h3-payout-policy-regression*
*Context gathered: 2026-02-05*
