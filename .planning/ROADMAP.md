# Roadmap: F1D Data Processing Pipeline

## Overview

The v4.0 milestone organizes and refactors all scripts to follow consistent patterns for folder structure, I/O, logging, and naming conventions. This refactoring consolidates three accidentally-created V3 folders into V2, implements config-driven I/O across all scripts, standardizes logging patterns, enforces naming conventions, and verifies all changes through comprehensive testing. The pipeline maintains bitwise-identical reproducibility throughout.

## Milestones

- Completed **v1.0** Pipeline Observability & Documentation (Phases 1-27) - shipped 2026-01-30
- Completed **v2.0** Hypothesis Testing Suite (Phases 28-58) - shipped 2026-02-06
- Completed **v3.0** Codebase Cleanup & Optimization (Phases 59-63) - shipped 2026-02-11
- Active **v4.0** Script Organization & Refactoring (Phases 64-68) - in progress

## Phases

<details>
<summary>Completed Milestones</summary>

### v1.0 MVP (Phases 1-27) - SHIPPED 2026-01-30
Pipeline observability, documentation, and replication package infrastructure. 143 plans completed. See MILESTONES.md for details.

### v2.0 Hypothesis Testing Suite (Phases 28-58) - SHIPPED 2026-02-06
H1-H9 hypothesis testing with V2/V3 folder structure. All hypotheses showed null results. See MILESTONES.md for details.

### v3.0 Codebase Cleanup & Optimization (Phases 59-63) - SHIPPED 2026-02-11
Critical bug fixes, code organization, documentation, performance optimization, and testing. See git history for details.

**v3.0 Phase Summary:**
| Phase | Name | Status |
|-------|------|--------|
| 59 | Critical Bug Fixes | COMPLETE |
| 60 | Code Organization | COMPLETE |
| 61 | Documentation | COMPLETE |
| 62 | Performance Optimization | COMPLETE |
| 63 | Testing & Validation | COMPLETE |

</details>

### v4.0 Script Organization & Refactoring (In Progress)

**Milestone Goal:** All scripts follow consistent patterns for folder structure, I/O, logging, and naming with two active versions (V1 and V2) only.

**Key Constraints:**
- Two active versions only: V1 and V2 (V3 was created by mistake, merge into V2)
- Sequential refactoring with immediate verification after each script
- Config-driven I/O: All paths from config/project.yaml
- Output pattern: 4_Outputs/[family]/[script]/[timestamp]

---

#### Phase 64: Folder Structure Consolidation

**Goal:** V3 folders merged into V2, with all scripts and outputs correctly relocated.

**Depends on:** Phase 63 (v3.0 Testing & Validation)

**Requirements:** STR-01, STR-02, STR-03, STR-04, STR-05 (22 sub-requirements)

**Success Criteria** (what must be TRUE):
1. No V3 folders exist in the repository (3_Financial_V3, 4_Econometric_V3, 5_Financial_V3 removed)
2. All V3 scripts have been moved to appropriate V2 folders with correct naming
3. All imports and references to moved scripts have been updated
4. All moved scripts execute successfully in their new locations
5. Output folder structure reflects new script locations (4_Outputs/[family]/[script]/[timestamp])

**Plans:** 5 plans

Plans:
- [ ] 64-01: Merge 3_Financial_V3 into 3_Financial_V2 (STR-01)
- [ ] 64-02: Merge 4_Econometric_V3 into 4_Econometric_V2 (STR-02)
- [ ] 64-03: Merge 5_Financial_V3 into V2 folders (STR-03)
- [ ] 64-04: Remove empty V3 folders and update documentation (STR-04)
- [ ] 64-05: Reorganize output folder structure (STR-05)

---

#### Phase 65: Config-Driven I/O

**Goal:** All scripts read input paths and generate output paths from config/project.yaml.

**Depends on:** Phase 64 (Folder Structure Consolidation)

**Requirements:** IO-01, IO-02, IO-03, IO-04, IO-05, IO-06, IO-07, IO-08 (52 sub-requirements)

**Success Criteria** (what must be TRUE):
1. Path utility functions (get_input_path, get_output_path) exist in shared/path_utils.py
2. All path definitions centralized in config/project.yaml with templates for all stages
3. V1 Sample scripts (1_Sample/) use config-driven I/O and produce correct outputs
4. V1 Text scripts (2_Text/) use config-driven I/O and produce correct outputs
5. V1 Financial scripts (3_Financial/) use config-driven I/O and produce correct outputs
6. V1 Econometric scripts (4_Econometric/) use config-driven I/O and produce correct outputs
7. V2 Financial scripts (3_Financial_V2/) use config-driven I/O and produce correct outputs
8. V2 Econometric scripts (4_Econometric_V2/) use config-driven I/O and produce correct outputs

**Plans:** 8 plans

Plans:
- [ ] 65-01: Define config-driven path standard and utilities (IO-01, IO-08)
- [ ] 65-02: V1 Sample scripts I/O refactor (IO-02)
- [ ] 65-03: V1 Text scripts I/O refactor (IO-03)
- [ ] 65-04: V1 Financial scripts I/O refactor (IO-04)
- [ ] 65-05: V1 Econometric scripts I/O refactor (IO-05)
- [ ] 65-06: V2 Financial scripts I/O refactor (IO-06)
- [ ] 65-07: V2 Econometric scripts I/O refactor (IO-07)
- [ ] 65-08: Path utilities documentation (IO-08 completion)

---

#### Phase 66: Logging Standardization

**Goal:** All scripts produce consistent log output with dual logging (console + file).

**Depends on:** Phase 65 (Config-Driven I/O)

**Requirements:** LOG-01, LOG-02, LOG-03, LOG-04 (18 sub-requirements)

**Success Criteria** (what must be TRUE):
1. Logging inconsistencies across all scripts have been identified and documented
2. A standard logging pattern is defined and documented in CLAUDE.md
3. All V1 scripts (Sample, Text, Financial, Econometric) use the standard logging pattern
4. All V2 scripts (Financial_V2, Econometric_V2) use the standard logging pattern
5. All scripts produce dual output (console and log file) with consistent formatting

**Plans:** 4 plans

Plans:
- [ ] 66-01: Audit current logging implementations (LOG-01)
- [ ] 66-02: Define standard logging pattern (LOG-02)
- [ ] 66-03: V1 scripts logging standardization (LOG-03)
- [ ] 66-04: V2 scripts logging standardization (LOG-04)

---

#### Phase 67: Naming Conventions

**Goal:** All scripts follow consistent naming pattern: {Stage}.{Step}_{PascalCaseName}.py.

**Depends on:** Phase 66 (Logging Standardization)

**Requirements:** NAM-01, NAM-02, NAM-03 (16 sub-requirements)

**Success Criteria** (what must be TRUE):
1. Naming convention is defined and documented in CLAUDE.md
2. All current script names have been audited for compliance
3. Non-compliant scripts have been renamed with updated imports
4. Config paths reflect new script names
5. All renamed scripts execute successfully

**Plans:** 3 plans

Plans:
- [ ] 67-01: Define naming standard and validation (NAM-01)
- [ ] 67-02: Audit current names for compliance (NAM-02)
- [ ] 67-03: Rename non-compliant scripts (NAM-03)

---

#### Phase 68: Verification

**Goal:** All refactored scripts produce identical outputs to pre-refactoring baselines.

**Depends on:** Phase 67 (Naming Conventions)

**Requirements:** VER-01, VER-02, VER-03, VER-04, VER-05, VER-06, VER-07, VER-08 (26 sub-requirements)

**Success Criteria** (what must be TRUE):
1. V1 Sample scripts produce outputs matching pre-refactoring baselines
2. V1 Text scripts produce outputs matching pre-refactoring baselines
3. V1 Financial scripts produce outputs matching pre-refactoring baselines
4. V1 Econometric scripts produce outputs matching pre-refactoring baselines
5. V2 Financial scripts produce outputs matching pre-refactoring baselines
6. V2 Econometric scripts produce outputs matching pre-refactoring baselines
7. All pytest tests pass
8. Full V1 and V2 pipelines execute end-to-end without errors

**Plans:** 8 plans

Plans:
- [ ] 68-01: V1 Sample verification (VER-01)
- [ ] 68-02: V1 Text verification (VER-02)
- [ ] 68-03: V1 Financial verification (VER-03)
- [ ] 68-04: V1 Econometric verification (VER-04)
- [ ] 68-05: V2 Financial verification (VER-05)
- [ ] 68-06: V2 Econometric verification (VER-06)
- [ ] 68-07: Test suite verification (VER-07)
- [ ] 68-08: End-to-end pipeline verification (VER-08)

---

## Progress

**Execution Order:**
Phases execute in numeric order: 64 -> 65 -> 66 -> 67 -> 68

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 64. Folder Structure Consolidation | v4.0 | 0/5 | Not started | - |
| 65. Config-Driven I/O | v4.0 | 0/8 | Not started | - |
| 66. Logging Standardization | v4.0 | 0/4 | Not started | - |
| 67. Naming Conventions | v4.0 | 0/3 | Not started | - |
| 68. Verification | v4.0 | 0/8 | Not started | - |

---

## Requirement Coverage

**v4.0 Requirements by Phase:**

| Category | Requirements | Phase | Sub-requirements |
|----------|--------------|-------|------------------|
| STR (Folder Structure) | STR-01 through STR-05 | 64 | 22 |
| IO (I/O Pattern) | IO-01 through IO-08 | 65 | 52 |
| LOG (Logging) | LOG-01 through LOG-04 | 66 | 18 |
| NAM (Naming) | NAM-01 through NAM-03 | 67 | 16 |
| VER (Verification) | VER-01 through VER-08 | 68 | 26 |

**Total:** 28 category requirements, 134 sub-requirements (100% mapped)

---

*Roadmap created: 2026-02-12 for v4.0 milestone*
*Previous milestones: v1.0 (27 phases), v2.0 (31 phases), v3.0 (5 phases)*
