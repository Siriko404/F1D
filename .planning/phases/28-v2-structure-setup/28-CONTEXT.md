# Phase 28: V2 Structure Setup - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the folder structure and naming conventions for V2 hypothesis testing scripts. This is pure infrastructure: creating directories, READMEs, and conventions that downstream variable construction (Phases 29-31) and regression phases (Phases 33-35) will use. No actual variable construction or analysis happens in this phase.

</domain>

<decisions>
## Implementation Decisions

### README Documentation Depth
- Comprehensive READMEs with full reference documentation
- Include all three hypotheses (H1: Cash Holdings, H2: Investment Efficiency, H3: Payout Policy) with exact variables
- Full variable specifications: variable name, formula, Compustat source fields
- Include input/output mapping showing how V2 uses v1.0 outputs (from `4_Outputs/2.X_*` folders)
- Econometric_V2 README includes execution flow diagram showing regression dependency chain
- Econometric_V2 README includes regression specifications (e.g., `Cash ~ Uncertainty + Leverage + Uncertainty*Leverage + Controls + FEs`)
- Academic literature references belong in scripts, not READMEs

### Folder Initialization
- Create 6 folders total as specified in ROADMAP success criteria:
  - `2_Scripts/3_Financial_V2/`
  - `2_Scripts/4_Econometric_V2/`
  - `3_Logs/3_Financial_V2/`
  - `3_Logs/4_Econometric_V2/`
  - `4_Outputs/3_Financial_V2/`
  - `4_Outputs/4_Econometric_V2/`
- Include READMEs in script folders, .gitkeep in output/log folders
- Folder naming matches v1.0 pattern (e.g., `3_Financial_V2` mirrors `3_Financial`)
- Two separate log folders mirroring script folder structure

### Script Numbering Scheme
- Financial_V2: Start at 3.1 (fresh sequence)
  - 3.1_H1Variables.py (Cash Holdings)
  - 3.2_H2Variables.py (Investment Efficiency)
  - 3.3_H3Variables.py (Payout Policy)
- Econometric_V2: Infrastructure first at 4.0
  - 4.0_EconometricInfra.py (shared infrastructure)
  - 4.1_H1Regression.py (Cash Holdings regression)
  - 4.2_H2Regression.py (Investment Efficiency regression)
  - 4.3_H3Regression.py (Payout Policy regression)
  - 4.4_H1Robust.py, 4.5_H2Robust.py, 4.6_H3Robust.py (per-hypothesis robustness)
- One script per hypothesis for variable construction (not finer granularity)
- Robustness checks are separate scripts per hypothesis

### Validation Approach
- Dedicated validation script: `2.0_ValidateV2Structure.py`
- Automated checks for:
  - All 6 required folders exist
  - README content validation (expected sections: hypotheses, variables, formulas)
  - .gitkeep files present in output/log folders
  - No conflicts with v1.0 files in V2 folders
- Fail on any error (non-zero exit code + clear error message)

### OpenCode's Discretion
- README format (prose vs. tabular) for variable specifications
- Exact README section organization
- Validation script implementation details

</decisions>

<specifics>
## Specific Ideas

- User emphasized wanting "extreme depth" on models and variables for each hypothesis - this context feeds into Phases 29-31 discussions
- Variable construction scripts should be one per hypothesis, not fragmented by individual variable
- Infrastructure script (4.0) is explicitly separate from regression scripts

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 28-v2-structure-setup*
*Context gathered: 2026-02-04*
