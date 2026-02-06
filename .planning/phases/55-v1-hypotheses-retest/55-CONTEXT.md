# Phase 55: V1 Hypotheses Re-Test - Context

**Gathered:** 2026-02-06
**Status:** Ready for planning

## Phase Boundary

Re-test two null-result V1 hypotheses (Uncertainty → Illiquidity and Uncertainty → Takeover Target Probability) through exhaustive literature review, rigorous methodology design, and fresh re-implementation to determine whether prior null results were due to flawed methodology or genuine empirical effects. **This phase does NOT audit V1 code** — it designs correct methodology from literature and implements from scratch.

## Implementation Decisions

### Literature Review Depth
- **Scope:** Exhaustive — 20+ years, all major finance journals, full citation tracing (2-3 days work)
- **Priorities:** Both hypotheses equal priority (uncertainty-illiquidity AND uncertainty-takeover)
- **Output format:** Synthesized brief with key findings, effect sizes, and methodological patterns
- **Integration:** Literature findings MUST explicitly guide the subsequent methodology design and implementation

### Methodology Design (Not Code Audit)
- **Approach:** NO V1 code review — this is fresh re-implementation based on literature best practices
- **Process:** Full methodology specification document BEFORE any code implementation
- **Text measures:** Reuse existing speech uncertainty measures from V2 pipeline (LM Uncertainty, etc.)
- **Regression specs:** Follow literature standards (FE, clustering, timing) — NOT V1 patterns or V2 defaults
- **Execution:** Sequential pilot — implement one hypothesis first, learn and refine approach for second

### Re-test Strategy
- **Specifications:** Full robustness suite (primary spec + all literature-based alternatives)
- **Sample:** Investigate thoroughly through literature and present recommendation (not defaulting to V2 sample)
- **Execution plan:** Always run full robustness suite regardless of primary result (pre-registered approach)
- **File organization:** Extend existing V2 folders (2_Scripts/3_Financial_V2/, 2_Scripts/4_Econometric_V2/)

### Success Criteria
- **Implementation success:** Correct implementation following literature standards
- **Findings success:** Any significance OR consistent significance across specs OR precise estimates (all valued)
- **Deliverable:** Both primary conclusion (relationship validated/refuted) AND full diagnostic report comparing to literature and explaining any differences from V1
- **Output format:** Full research report (not just summary)
- **Delivery:** Phased — literature review report first, then implementation reports per hypothesis

### Claude's Discretion
- Specific journals and databases to search for literature review
- Exact structure of methodology specification document
- Which hypothesis to pilot first (uncertainty-illiquidity or uncertainty-takeover)
- Number and nature of robustness specifications (within "full suite" directive)
- Sample construction details (after presenting recommendation based on literature)

## Specific Ideas

- "We want thorough investigation and recommendation — not just accepting V2 sample as default"
- "Success is measured by correct implementation, plus all above [diagnostic rigor, literature alignment]"
- Phased delivery suggests: (1) Literature Review Report, (2) Hypothesis 1 Implementation Report, (3) Hypothesis 2 Implementation Report, (4) Synthesis Report

## Deferred Ideas

None — discussion stayed within phase scope.

---

*Phase: 55-v1-hypotheses-retest*
*Context gathered: 2026-02-06*
