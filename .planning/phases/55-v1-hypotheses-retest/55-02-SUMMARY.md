---
phase: 55-v1-hypotheses-retest
plan: 02
subsystem: methodology-specification
tags: [illiquidity, takeover, amihud-2002, roll-1984, logit-regression, panel-data, fixed-effects, robustness]

# Dependency graph
requires:
  - phase: 55-v1-hypotheses-retest
    plan: 01
    provides: Literature review identifying Dang et al. (2022) as H1 template, M&A prediction standards for H2
provides:
  - Complete methodology specification for H1 (Uncertainty -> Illiquidity) with Amihud (2002) measure
  - Complete methodology specification for H2 (Uncertainty -> Takeover) with logit model
  - Exact regression equations with Greek notation for both hypotheses
  - Variable definitions with formulas and data sources
  - Sample construction procedures with code examples
  - Full robustness specifications (11 for H1, 12 for H2)
  - Implementation plan for remaining 7 plans (55-03 through 55-09)
  - Success criteria for implementation and scientific outcomes
affects: [55-03, 55-04, 55-05, 55-06, 55-07, 55-08, 55-09]

# Tech tracking
tech-stack:
  added:
    - Amihud (2002) illiquidity ratio calculation
    - Roll (1984) implicit spread calculation
    - PanelOLS with Firm + Year FE (linearmodels)
    - Logistic regression with firm clustering (statsmodels)
    - Cox Proportional Hazards model (lifelines)
  patterns:
    - Literature-based methodology design (not V1 code patterns)
    - Pre-registered research design (all specs defined before implementation)
    - Full robustness suite execution (all specs reported regardless of outcome)
    - Sequential implementation (H1 pilot, then H2)

key-files:
  created: [.planning/phases/55-v1-hypotheses-retest/55-METHODOLOGY.md]
  modified: []

key-decisions:
  - "Pilot H1 (Illiquidity) first - Dang et al. (2022) provides clear methodological template"
  - "Use Amihud (2002) as primary illiquidity measure (6000+ citations, literature standard)"
  - "Use Roll (1984) and bid-ask spread as robustness DVs for H1"
  - "Panel OLS with Firm + Year FE, firm-clustered SE for H1"
  - "Logit with Year FE, firm-clustered SE for H2 (primary)"
  - "Cox Proportional Hazards as H2 alternative (survival analysis)"
  - "Timing: Uncertainty_t -> Outcome_{t+1} for causal ordering"
  - "Full robustness suite: 11 specs for H1, 12 specs for H2"
  - "SDC Platinum for takeover identification (completed deals primary)"
  - "Pre-registered approach - all specs defined before implementation"

patterns-established:
  - "Literature-first methodology design: Identify foundational paper (Dang 2022), extract exact specifications"
  - "Complete specification before implementation: Equations, variables, data sources, robustness all documented"
  - "Sequential learning: Implement H1 first to learn approach, apply to H2"
  - "Pre-registered robustness: All 11-12 specifications must be run and reported"
  - "Multiple hypothesis correction: FDR applied across 4 IVs per hypothesis"

# Metrics
duration: 8min
completed: 2026-02-06
---

# Phase 55 Plan 02: Methodology Specification Summary

**Literature-based methodology specification for V1 hypothesis re-testing: Amihud (2002) illiquidity for H1, logit/Cox PH for H2, with 1,960-line comprehensive design document**

## Performance

- **Duration:** 8 min
- **Started:** 2026-02-06T23:11:40Z
- **Completed:** 2026-02-06T23:19:30Z
- **Tasks:** 4
- **Files created:** 2 (55-METHODOLOGY.md, 55-02-SUMMARY.md)

## Accomplishments

- **Complete methodology specification** created BEFORE any code implementation (per CONTEXT locked decision)
- **H1 (Illiquidity) fully specified:** Amihud (2002) primary DV, Roll (1984) robustness, 8 controls, Panel OLS with Firm+Year FE
- **H2 (Takeover) fully specified:** Binary takeover indicator from SDC, logit primary model, Cox PH alternative, 8 controls
- **Exact regression equations** with Greek notation for both hypotheses
- **All variable definitions** with formulas, data sources (CRSP, Compustat, SDC, V2 text)
- **Sample construction procedures** with step-by-step Python code examples
- **Robustness specifications enumerated:** 11 specs for H1, 12 specs for H2 (pre-registered)
- **Implementation plan** for remaining 7 plans (55-03 through 55-09)
- **Success criteria** defined for both implementation and scientific outcomes
- **V1 suspected flaws documented** with V2 improvements mapped
- **Literature alignment verified:** Dang et al. (2022), Amihud (2002), Roll (1984), Petersen (2009), Cameron & Miller (2015)

## Task Commits

Each task was committed atomically:

1. **Task 1: Specify H1 Research Design** - `bebd3f6` (feat)
   - Amihud (2002) as primary DV with exact formula
   - Roll (1984) and bid-ask spread as robustness DVs
   - V2 uncertainty measures as IVs
   - Literature-based controls specified
   - Primary regression equation with FE and clustering
   - Forward-looking DV (t+1) specified

2. **Task 2: H1 Sample Construction and Data Sources** - `7e10c77` (feat)
   - Data sources mapped: CRSP (illiquidity), Compustat (controls), V2 text (uncertainty)
   - Sample construction rules: Exclude financial/utilities, require positive assets, 50+ trading days
   - Winsorization at 1%/99% for continuous variables
   - Power analysis: 99%+ power, sample size not limiting factor
   - 11 robustness specifications enumerated
   - Complete data merge procedures with code examples

3. **Task 3: Specify H2 Research Design** - `f20fc16` (feat)
   - Binary takeover indicator from SDC Platinum as primary DV
   - Logit model with Year FE and firm-clustered SE as primary
   - Cox PH survival model as alternative
   - Literature-based controls: Size, Leverage, ROA, MTB, Liquidity, Efficiency, Returns, R&D Intensity
   - SDC matching procedure via CUSIP
   - 12 robustness specifications enumerated
   - Timing tests (t, t+1, t+2) specified

4. **Task 4: Implementation Plan and Success Criteria** - `8486b14` (feat)
   - Sequential approach: H1 first, then H2 (Dang 2022 template)
   - Implementation plans for all 9 remaining plans (55-03 through 55-09)
   - Success criteria defined for implementation and scientific outcomes
   - V1 suspected flaws documented with V2 improvements
   - Pre-registration framework established

**Plan metadata:** Will be committed separately

## Files Created/Modified

- `.planning/phases/55-v1-hypotheses-retest/55-METHODOLOGY.md` - 1,963-line comprehensive methodology specification
  - Hypothesis 1 (H7): Uncertainty -> Illiquidity
  - Hypothesis 2 (H8): Uncertainty -> Takeover Target Probability
  - Complete regression equations, variable definitions, data sources
  - Sample construction procedures with code examples
  - Robustness specifications (23 total across both hypotheses)
  - Implementation plan for remaining 7 plans
  - Success criteria and pre-registration framework

- `.planning/phases/55-v1-hypotheses-retest/55-02-SUMMARY.md` - This summary document

## Decisions Made

### Sequential Implementation Approach

**Decision:** Implement H1 (Illiquidity) first, then apply learnings to H2 (Takeover)

**Rationale:**
1. **Dang et al. (2022) provides clear template** for H1 - direct methodological guidance
2. **Data availability is simpler** - CRSP data already integrated, no SDC access needed initially
3. **Stronger literature base** - Amihud (2002) is dominant standard vs more fragmented M&A literature
4. **Learnings transfer to H2** - Panel regression approach, data merging, variable construction all applicable
5. **Risk mitigation** - Easier to debug on continuous DV (illiquidity) than binary DV (takeover)

### Primary Methodological Choices

**For H1 (Illiquidity):**
- **Primary DV:** Amihud (2002) illiquidity ratio (industry standard, 6000+ citations)
- **Robustness DVs:** Roll (1984) spread, bid-ask spread
- **Model:** PanelOLS with Firm + Year FE, firm-clustered SE
- **Timing:** Uncertainty_t -> Illiquidity_{t+1} (causal ordering)

**For H2 (Takeover):**
- **Primary DV:** Binary takeover indicator (completed deals from SDC Platinum)
- **Primary Model:** Logit with Year FE, firm-clustered SE
- **Alternative Model:** Cox Proportional Hazards (survival analysis)
- **Timing:** Uncertainty_t -> Takeover_{t+1}

### Robustness Framework

**Decision:** Pre-register full robustness suite (all specs must be run and reported)

**Rationale:**
- Prevents p-hacking and specification searching
- All outcomes valued (null, mixed, significant)
- Enables assessment of result consistency
- Aligns with best practices for empirical research

**Robustness Counts:**
- H1: 11 specifications (primary + 10 alternatives)
- H2: 12 specifications (primary + 11 alternatives)

### Variable Construction Standards

**Decision:** Use exact formulas from literature with code examples

**Standards:**
- Amihud: ILLIQ = (1/D) * sum(|RET| / (|PRC| * VOL)) * 1e6
- Roll: SPRD = 2 * sqrt(-cov(r_t, r_{t-1}))
- Minimum 50 trading days for illiquidity calculation
- Winsorization at 1%/99% for all continuous variables
- Industry exclusions: Financial (SIC 6000-6999), Utilities (SIC 4900-4999)

## Deviations from Plan

None - plan executed exactly as specified.

## Issues Encountered

None - methodology specification proceeded smoothly.

## Next Phase Readiness

### Ready for Implementation (Plans 55-03 through 55-09)

**Available:**
- Complete methodology specification (55-METHODOLOGY.md, 1,963 lines)
- Exact regression equations for both hypotheses
- Variable definitions with formulas and data sources
- Sample construction procedures with code examples
- Robustness specifications fully enumerated
- Success criteria clearly stated
- Implementation plan for remaining 7 plans

**Blockers:** None

**Next Steps:**
1. Plan 55-03: Construct H1 illiquidity variables (Amihud, Roll)
2. Plan 55-04: Run H1 primary regression
3. Plan 55-05: Run H1 robustness suite
4. Plan 55-06: Construct H2 takeover variables (SDC merge)
5. Plan 55-07: Run H2 primary regression (logit)
6. Plan 55-08: Run H2 robustness suite
7. Plan 55-09: Synthesis and reporting

### What This Enables

- **Plan 55-03 (H1 Variables):** Use exact Amihud formula, data merge procedures
- **Plan 55-04 (H1 Primary):** Use specified regression equation, FE/clustering
- **Plan 55-05 (H1 Robustness):** Run all 10 alternative specifications per enumeration
- **Plan 55-06 (H2 Variables):** Use SDC matching procedure, takeover definitions
- **Plan 55-07 (H2 Primary):** Use specified logit equation, Year FE, clustering
- **Plan 55-08 (H2 Robustness):** Run all 11 alternative specifications per enumeration
- **Plan 55-09 (Synthesis):** Compare to V1 results, literature benchmarks, generate report

---

*Phase: 55-v1-hypotheses-retest*
*Plan: 02*
*Completed: 2026-02-06*
