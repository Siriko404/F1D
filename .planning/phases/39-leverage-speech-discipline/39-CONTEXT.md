# Phase 39: Leverage Disciplines Managers and Lowers Speech Uncertainty - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Test the reverse causal direction from H1-H3: Does higher leverage discipline managers and reduce speech uncertainty? This phase examines whether debt monitoring (covenant restrictions, lender oversight) constrains vague managerial language in earnings calls.

**Scope:** Panel OLS regressions with 6 speech uncertainty measures as dependent variables, leverage as independent variable, and comprehensive controls including analyst uncertainty and speaker presentation uncertainty.

**Out of scope:** 2SLS/IV estimation, interaction terms, subsample analyses (these are future robustness if H4 finds support).

</domain>

<decisions>
## Implementation Decisions

### Regression Approach
- **Simple OLS with controls only** — No IV/2SLS
- **Fixed Effects**: Firm + Year + Industry (FF48) — Same as H1-H3
- **Standard Errors**: Clustered at firm level
- **6 separate regressions** — One for each uncertainty measure as DV

### Variable Specification

**Dependent Variables (6 measures):**
1. `Manager_QA_Uncertainty_pct`
2. `CEO_QA_Uncertainty_pct`
3. `Manager_QA_Weak_Modal_pct`
4. `CEO_QA_Weak_Modal_pct`
5. `Manager_Pres_Uncertainty_pct`
6. `CEO_Pres_Uncertainty_pct`

**Independent Variable:**
- `leverage` = (DLTT + DLC) / AT — **Lagged t-1** for causal interpretation

**Required Controls (per your specification):**
- `Analyst_QA_Uncertainty_pct` — Controls for information environment
- Speaker's own presentation uncertainty:
  - For Manager QA DVs: `Manager_Pres_Uncertainty_pct`
  - For CEO QA DVs: `CEO_Pres_Uncertainty_pct`
  - For Presentation DVs: No presentation control (or lagged t-1 if needed)

**Additional Financial Controls (from existing data):**
- `firm_size` — ln(AT)
- `tobins_q` — Tobin's Q
- `roa` — Return on Assets
- `cash_holdings` — CHE/AT
- `dividend_payer` — Indicator
- `firm_maturity` — RE/TE (from H3)
- `earnings_volatility` — StdDev EPS (from H3)

### Hypothesis Testing
- **H4**: β₁ < 0 (Higher leverage → Lower speech uncertainty / Discipline effect)
- **Test type**: One-tailed at α = 0.05
- **Significance levels**: *** p<0.01, ** p<0.05, * p<0.10

### Timing Structure
- **Primary specification**: Leverage_{t-1} → Uncertainty_t (lagged IV)
- **Controls**: Contemporaneous with DV (period t)
- **Sample**: Same firm-year observations as H1-H3 (filtered to earnings calls in manifest)

### Interaction Terms
- **None in primary specification** — Keep simple
- Moderators (size, profitability effects) reserved for robustness if primary results are significant

### OpenCode's Discretion
- Exact column availability for presentation weak modal measures (fallback to general uncertainty if needed)
- Presentation DV control handling (exclude vs. lagged t-1)
- Exact subset of financial controls if multicollinearity concerns arise
- Specification ordering for regression table output

</decisions>

<specifics>
## Specific Ideas

**Model structure mirrors H1-H3 for comparability:**
- Same fixed effects structure (firm + year + industry)
- Same clustering approach (firm-level)
- Same significance thresholds

**Key identification strategy:**
- Analyst uncertainty control isolates leverage effect from general information environment
- Speaker's own presentation uncertainty controls for inherent vagueness tendency
- Lagged leverage improves causal interpretation

**Expected output format:**
- Coefficient table with 6 columns (one per DV)
- Rows: Leverage, Analyst Uncertainty, Presentation Uncertainty, Controls, N, R²
- stats.json with regression diagnostics for each specification

</specifics>

<deferred>
## Deferred Ideas

**Robustness checks** (if H4 finds support):
- Contemporaneous specification (Leverage_t)
- Industry-median leverage as instrument
- Subsample: High vs. low covenant intensity
- Subsample: Bank debt vs. bond debt
- Interaction: Leverage × Firm Size
- Interaction: Leverage × ROA

**Alternative specifications:**
- 2SLS with industry leverage as instrument
- Manager fixed effects (if enough movers)
- Firm-year level aggregation vs. call-level

**Scope note:** These belong in future phases if primary H4 results warrant investigation.

</deferred>

---

*Phase: 39-leverage-speech-discipline*
*Context gathered: 2026-02-05*
*Model: Speech Uncertainty_{t} = β₀ + β₁·Leverage_{t-1} + β₂·Analyst_Uncertainty_{t} + β₃·Presentation_Uncertainty_{t} + γ·Controls_{t} + Firm_FE + Year_FE + Industry_FE + ε*
*Hypothesis: H4: β₁ < 0 (one-tailed)*
