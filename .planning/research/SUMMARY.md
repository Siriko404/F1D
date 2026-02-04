# Project Research Summary

**Project:** F1D Hypothesis Testing Pipeline (v2.0 Milestone)
**Domain:** Empirical Finance Panel Econometrics
**Researched:** 2026-02-04
**Confidence:** HIGH

## Executive Summary

This research synthesis covers adding hypothesis testing capabilities (H1-H3) to the existing F1D data pipeline, which already has a mature 4-stage architecture (Sample → Text → Financial → Econometric). The good news: **no fundamental architecture changes are required**. The existing patterns for fixed-effects regression (4.1), 2SLS instrumentation (4.2), and subsample analysis (4.1.3) provide proven templates. New hypothesis scripts integrate naturally as stage 4 extensions (4.5, 4.6, 4.7) following established conventions.

The recommended approach is **incremental extension**: build a new outcome variable construction step (3.5), create a small shared module for hypothesis-specific utilities (`hypothesis_utils.py`), then implement each hypothesis as a separate script following existing patterns. Stack additions are minimal—the current pandas/numpy/statsmodels/linearmodels stack handles all requirements. The only new capability needed is proper interaction term handling with mean-centering.

**Key risks and mitigations:**
1. **FE Collinearity Trap** — Using firm + year + industry FE simultaneously can absorb time-invariant variables silently. Mitigation: Use `drop_absorbed=False` in linearmodels, run VIF diagnostics before adding FE dimensions.
2. **Weak Instruments in 2SLS** — Existing IV infrastructure from 4.2 works, but weak instruments produce worse-than-OLS bias. Mitigation: Enforce F > 10 rule with automatic validation.
3. **Manager FE Connectivity** — CEO fixed effects require "movers" between firms; with low mover fraction, CEO FE conflates with firm culture. Mitigation: Check connectivity before running manager FE regressions.

## Key Findings

### Recommended Stack

The existing stack (pandas 3.0.x, numpy 2.x, statsmodels, linearmodels) is fully sufficient. **No new major dependencies required.** For enhanced observability during hypothesis testing, skimpy provides lightweight console statistics. scipy.stats can be added if advanced statistical tests (normality, distribution fitting) are needed beyond descriptive statistics.

**Core technologies (already in place):**
- **pandas 3.0.x / numpy 2.x:** Core data manipulation and array statistics
- **statsmodels:** OLS with formula API, fixed effects via categorical encoding
- **linearmodels:** PanelOLS with entity/time FE, IV2SLS for endogeneity correction
- **PyYAML:** Config loading from project.yaml

**Optional additions (lightweight):**
- **skimpy 0.0.20:** Console statistics display (like R's `skimr`)
- **scipy.stats 1.17.x:** Only if statistical tests beyond descriptive stats are needed

### Expected Features

The hypothesis testing pipeline must produce publication-quality econometric results that satisfy academic reviewers and thesis committees.

**Must have (table stakes):**
- Baseline OLS with firm + year + industry fixed effects
- Interaction terms (Speech_Uncertainty × Firm_Leverage) with proper centering
- Clustered standard errors (firm-level minimum)
- Complete case filtering with sample size reporting
- Winsorization at 1%/99% percentiles
- Coefficient tables (β, SE, t-stat, p-value, R², F-stat)
- Lag structure for outcomes (t+1)

**Should have (differentiators):**
- Subsample analysis (leverage splits, crisis periods, growth opportunities)
- Alternative specifications (different control sets)
- 2SLS with instrument diagnostics (F-stat, J-test)
- Economic significance calculations (1-SD change interpretation)
- LaTeX table output for publication

**Defer (post-thesis):**
- Propensity score matching
- Difference-in-differences event studies
- Coefficient stability bounds (Oster 2019)
- Quantile regression

### Architecture Approach

The existing architecture extends naturally. New scripts slot into Stage 3 (outcome variables) and Stage 4 (hypothesis regressions) without modifying upstream stages. All scripts follow the established naming convention (`{step}.{substep}_{Name}.py`), use shared modules for path resolution and validation, and output to timestamped directories with dual logging.

**New components:**
1. **3.5_HypothesisOutcomes.py** — Constructs DV variables (CashHoldings, InvestmentEfficiency, PayoutStability)
2. **shared/hypothesis_utils.py** — Interaction term centering, subsample splitting, IV diagnostics
3. **4.5_CashHoldingsRegression.py (H1)** — OLS + 2SLS for cash holdings hypothesis
4. **4.6_InvestmentEfficiencyRegression.py (H2)** — OLS + 2SLS for investment efficiency hypothesis
5. **4.7_PayoutStabilityRegression.py (H3)** — OLS + 2SLS for payout stability hypothesis
6. **4.8_SubsampleAnalysis.py** — Consolidated subsample analysis across H1-H3

### Critical Pitfalls

The top 5 pitfalls from research, ranked by severity:

1. **FE Collinearity Trap (H1)** — Firm + industry FE are redundant (firms don't change industries). Use `drop_absorbed=False, check_rank=True` in linearmodels. Run VIF before adding FE dimensions. If condition number > 30, investigate.

2. **Interaction Multicollinearity (H2)** — Raw `X × Z` is correlated with both `X` and `Z`. **Always center continuous variables before creating interactions.** Use within-group centering for panel data.

3. **Weak Instruments in 2SLS (H3)** — F < 10 on first stage means 2SLS is more biased than OLS. **Enforce F > 10 programmatically.** Report first-stage diagnostics prominently. Use LIML instead of 2SLS if instruments are weak.

4. **Manager FE Connectivity (H5)** — With few CEO "movers" between firms, CEO FE conflates manager style with firm culture. Check mover fraction before running manager FE. If < 5% movers, interpret carefully or use alternative approaches.

5. **Multiple Testing in Subsamples (H7)** — Running 10+ subsample tests guarantees false positives. **Use interaction terms instead of separate regressions** (one test for heterogeneity, not 10 subsample tests). If subsample tests necessary, apply Bonferroni correction.

## Implications for Roadmap

Based on research, suggested 4-phase structure:

### Phase 1: Variable Construction Foundation
**Rationale:** All hypothesis regressions depend on outcome variables (CashHoldings, InvestmentEfficiency, PayoutStability) that don't yet exist. Build data foundation before any regressions.
**Delivers:** 
- `3.5_HypothesisOutcomes.py` with hypothesis-specific DVs
- Validated outcome variables merged with manifest
- Control variable completeness check
**Addresses:** Variable Construction (Priority P0 from FEATURES.md)
**Avoids:** Missing transformation code (Pitfall 4 from replication section)

### Phase 2: Shared Infrastructure
**Rationale:** Avoid code duplication across H1-H3. Build reusable utilities before implementing individual hypotheses.
**Delivers:**
- `shared/hypothesis_utils.py` module
- Interaction term creation with centering
- IV diagnostics wrapper (F-stat check, J-test)
- Subsample splitting utilities
- Panel connectivity check for manager FE
**Uses:** statsmodels, linearmodels (existing stack)
**Implements:** Core utilities referenced by all 4.5-4.7 scripts

### Phase 3: Core Hypothesis Implementation
**Rationale:** With foundation in place, implement each hypothesis following established 4.1/4.2 patterns. Scripts are independent after shared infrastructure exists.
**Delivers:**
- `4.5_CashHoldingsRegression.py` (H1: Uncertainty → Cash Holdings)
- `4.6_InvestmentEfficiencyRegression.py` (H2: Uncertainty → Investment)
- `4.7_PayoutStabilityRegression.py` (H3: Uncertainty → Payout Stability)
- Baseline OLS + 2SLS for each hypothesis
- stats.json, regression_results.txt, report.md outputs
**Addresses:** Baseline regressions, interaction terms, clustered SEs (P0 from FEATURES.md)
**Avoids:** Formula errors (Pitfall H11), clustering inconsistency (Pitfall H6)

### Phase 4: Robustness & Publication Polish
**Rationale:** After core results established, add robustness checks and publication-ready output.
**Delivers:**
- `4.8_SubsampleAnalysis.py` — tenure, leverage, crisis period splits
- LaTeX table generation
- Economic significance calculations
- Falsification tests (placebo outcomes)
**Addresses:** Subsample analysis, alternative specs, LaTeX output (P1-P2 from FEATURES.md)
**Avoids:** Multiple testing inflation (Pitfall H7)

### Phase Ordering Rationale

- **Phase 1 before Phase 2:** Variable construction must exist before utilities that operate on them can be tested.
- **Phase 2 before Phase 3:** Shared utilities prevent 3x code duplication and ensure consistent pitfall prevention across hypotheses.
- **Phase 3 as single phase (not 3 separate):** H1, H2, H3 scripts are independent after Phase 2; can be parallelized.
- **Phase 4 after Phase 3:** Robustness checks only make sense after baseline results exist.

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 1 (Variable Construction):** Investment efficiency calculation (Biddle et al. 2009 residual method) is non-trivial. Need to verify exact methodology.
- **Phase 2 (IV Diagnostics):** linearmodels API for `first_stage.diagnostics` syntax may need verification against current library version.

**Phases with standard patterns (skip research-phase):**
- **Phase 3 (Hypothesis Regressions):** Follows established 4.1/4.2 patterns exactly. Well-documented in existing codebase.
- **Phase 4 (Subsample Analysis):** Follows established 4.1.3 pattern. Standard econometric practice.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | No new dependencies; pandas/statsmodels/linearmodels verified on PyPI |
| Features | HIGH | Based on standard empirical finance publication requirements |
| Architecture | HIGH | Derived from direct codebase analysis of existing 4.1-4.4 scripts |
| Pitfalls | MEDIUM-HIGH | Econometric theory verified; linearmodels syntax needs version check |

**Overall confidence:** HIGH

### Gaps to Address

1. **linearmodels version verification:** Some syntax (e.g., `other_effects`, `first_stage.diagnostics`) should be verified against installed version during implementation.

2. **Investment efficiency calculation:** The Biddle et al. (2009) residual-based method requires two-stage estimation. Implementation details need verification against original paper.

3. **Wild bootstrap for small clusters:** If subsample analysis produces < 50 clusters, wild bootstrap may be needed for inference. This requires additional library (not in current stack).

4. **CRSP-Compustat link methodology:** Existing pipeline handles this, but merge success rates should be documented for each hypothesis sample.

## Sources

### Primary (HIGH confidence)
- **Existing codebase:** `regression_utils.py`, `regression_helpers.py`, `regression_validation.py` — established patterns
- **PyPI verified:** pandas 3.0.0, scipy 1.17.0, skimpy 0.0.20, linearmodels (Jan 2026)
- **AEA Data Editor guidelines:** Replication package requirements

### Secondary (MEDIUM confidence)
- **linearmodels documentation:** bashtage.github.io/linearmodels/ — IV2SLS, PanelOLS syntax
- **Econometric theory:** Stock-Yogo weak instrument thresholds, AKM connectivity requirements

### Tertiary (LOW confidence - verify during implementation)
- **Biddle et al. (2009):** Investment efficiency residual methodology
- **Oster (2019):** Coefficient stability bounds (deferred to post-thesis)

---
*Research completed: 2026-02-04*
*Ready for roadmap: yes*
