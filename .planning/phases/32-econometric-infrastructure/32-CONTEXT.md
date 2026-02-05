# Phase 32: Econometric Infrastructure - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Build reusable econometric utilities for panel regressions with fixed effects, interaction terms, and robustness diagnostics. This phase creates the infrastructure that Phases 33-35 (H1/H2/H3 Regressions) will use. It does NOT run the actual hypothesis regressions — those are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Diagnostic Reporting
- Comprehensive diagnostics by default: R², N, F-stat, VIF for key variables, first-stage F (2SLS), Hansen J, condition number, residual diagnostics
- Prominent alerts for multicollinearity (VIF > 5): bold/highlighted warning in console AND log file
- Hard fail if first-stage F < 10: raise error, do not produce 2SLS results when instruments are weak
- Values shown with thresholds and context (e.g., "VIF 4.2 — acceptable, below 5 threshold")

### Output Structure
- stats.json contains: coefficients (beta, SE, t-stat, p-value) + summary (R², N, F-stat, fixed effects used)
- One file per hypothesis: H1_results.json, H2_results.json, H3_results.json
- Always save intermediate outputs: centered variables, first-stage predictions (for debugging/auditing)
- Timestamps match existing v1.0 pattern (per-run folders: YYYY-MM-DD_HHMMSS/)

### Regression Table Format
- Console output: summary table with key coefficients + significance stars in aligned columns
- Always generate LaTeX tables (.tex files) alongside JSON output
- LaTeX style: booktabs three-line format (\toprule, \midrule, \bottomrule)
- Significance: both stars (*, **, *** for 10%, 5%, 1%) AND p-values available in output

### Error Handling Behavior
- Hard fail on perfect collinearity: stop execution, require user to fix specification before proceeding
- Confirmation required if sample drops >20% after merge: pause and display "Sample dropped from X to Y (Z% loss)" with prompt
- Auto-collapse thin FE cells: if industry-year FE has <5 firms, fall back to FF12 instead of FF48
- No coefficient sign validation: compute and report results, user interprets whether signs match theory

### OpenCode's Discretion
- Exact column alignment and formatting for console tables
- LaTeX table column widths and spacing
- How confirmation prompts are implemented (input() vs flag)
- Intermediate file naming conventions

</decisions>

<specifics>
## Specific Ideas

- Diagnostics should feel like a quality gate — if something is wrong, you know immediately
- LaTeX tables should be publication-ready without manual editing
- The infrastructure should make Phases 33-35 straightforward: call a function, get results + diagnostics + tables

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 32-econometric-infrastructure*
*Context gathered: 2026-02-05*
