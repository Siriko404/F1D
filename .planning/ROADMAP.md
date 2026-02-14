# Roadmap: F1D Data Processing Pipeline

## Overview

Data processing pipeline for F1D thesis research. Milestones track major project phases from infrastructure to hypothesis testing to codebase standardization.

## Milestones

- Completed **v1.0** Pipeline Observability & Documentation (Phases 1-27) - shipped 2026-01-30
- Completed **v2.0** Hypothesis Testing Suite (Phases 28-58) - shipped 2026-02-06
- Completed **v3.0** Codebase Cleanup & Optimization (Phases 59-63) - shipped 2026-02-11
- Completed **v4.0** Folder Structure Consolidation (Phase 64) - shipped 2026-02-12
- Completed **v5.0** Architecture Standard Definition (Phases 65-68) - shipped 2026-02-13
- Completed **v6.0** Architecture Standard Implementation (Phases 69-74) - shipped 2026-02-14
- Completed **v6.1** Architecture Compliance Gap Closure (Phases 75-76) - shipped 2026-02-14

## Phases

<details>
<summary>Completed Milestones</summary>

### v1.0 MVP (Phases 1-27) - SHIPPED 2026-01-30
Pipeline observability, documentation, and replication package infrastructure. 143 plans completed. See milestones/v1.0-ROADMAP.md for details.

### v2.0 Hypothesis Testing Suite (Phases 28-58) - SHIPPED 2026-02-06
H1-H9 hypothesis testing with V2/V3 folder structure. All hypotheses showed null results. See milestones/v2.0-ROADMAP.md for details.

### v3.0 Codebase Cleanup & Optimization (Phases 59-63) - SHIPPED 2026-02-11
Critical bug fixes, code organization, documentation, performance optimization, and testing. See milestones/v3.0-ROADMAP.md for details.

### v4.0 Folder Structure Consolidation (Phase 64) - SHIPPED 2026-02-12
Eliminated V3 folders by merging all scripts and outputs into V2 structure. See milestones/v4.0-ROADMAP.md for details.

### v5.0 Architecture Standard Definition (Phases 65-68) - SHIPPED 2026-02-13

**Milestone Goal:** Define comprehensive architecture and coding standards for portfolio-ready repository quality.

**Delivered:** 4 standards documents (~12,000 lines) defining 35 requirements:
- `docs/ARCHITECTURE_STANDARD.md` — Folder structure, module tiers, version management
- `docs/CODE_QUALITY_STANDARD.md` — Naming conventions, docstrings, type hints
- `docs/CONFIG_TESTING_STANDARD.md` — Configuration, logging, testing patterns
- `docs/DOC_TOOLING_STANDARD.md` — Documentation, CI/CD, linting configuration

**Key Decisions:**
- src-layout over flat layout (PyPA recommendation)
- Both V1 and V2 as active variants
- Google-style docstrings with MkDocs+mkdocstrings
- ruff as unified linter/formatter
- Tier-based type hints and coverage targets

### v6.0 Architecture Standard Implementation (Phases 69-74) - SHIPPED 2026-02-14

**Milestone Goal:** Implement all standards defined in v5.0 across the codebase, transforming the repository into a portfolio-ready, industry-standard Python package.

**Delivered:** 27 plans across 6 phases (69-74):
- src-layout package structure with proper imports
- Type hints with tier-based mypy enforcement
- Type-safe configuration via pydantic-settings
- Structured logging with structlog and context binding
- CI/CD pipeline with ruff, mypy, and pytest quality gates
- Comprehensive test suite with factory fixtures and coverage enforcement

**Key Metrics:**
- Tier 1 test coverage: financial_utils 96%, data_validation 94%
- Tier 2 test coverage: config 88%, logging 82%, path_utils 86%, chunked_reader 88%

### v6.1 Architecture Compliance Gap Closure (Phases 75-76) - SHIPPED 2026-02-14

**Milestone Goal:** Close all integration gaps identified in v6.0 audit to achieve full architecture standard compliance.

**Delivered:** 9 plans across 2 phases (75-76):
- Migrated 5 sample scripts to proper f1d.shared.* imports
- Migrated 21 test files to namespace imports
- Integrated LoggingSettings with configure_logging()
- Removed 22 obsolete xfail markers from econometric tests
- Migrated 36 stage scripts (17 financial + 19 econometric) to f1d.shared.* namespace
- Achieved full ROADMAP compliance - zero sys.path.insert() in entire codebase

**Key Metrics:**
- Zero sys.path.insert() calls in entire codebase
- Zero legacy `from shared.*` imports
- mypy passes with 0 errors on 41 migrated files

</details>

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 69. Architecture Migration | v6.0 | 3/3 | Complete | 2026-02-13 |
| 70. Type Hints | v6.0 | 12/12 | Complete | 2026-02-14 |
| 71. Configuration System | v6.0 | 3/3 | Complete | 2026-02-13 |
| 72. Structured Logging | v6.0 | 5/5 | Complete | 2026-02-13 |
| 73. CI/CD Pipeline | v6.0 | 3/3 | Complete | 2026-02-14 |
| 74. Testing Infrastructure | v6.0 | 4/4 | Complete | 2026-02-14 |
| 75. Gap Closure (v6.0 scope) | v6.1 | 5/5 | Complete | 2026-02-14 |
| 76. Stage Scripts Migration | v6.1 | 4/4 | Complete | 2026-02-14 |
| 77. Concerns Closure + Verification | v6.1 | 17/17 | Complete | 2026-02-14 |
| 78. Documentation Synchronization | v6.1 | 0/? | Not Planned | - |

### Phase 77: Concerns Closure with Parallel Agents + Full Verification

**Goal:** Close ALL concerns identified in `.planning/codebase/CONCERNS.md` using parallel gsd-executor agents

**Depends on:** Phase 76 (Stage Scripts Migration)

**Success Criteria** (what must be TRUE):
1. Zero `sys.path.insert()` in entire codebase (already achieved in v6.1, double-check)
2. Zero `from shared.*` legacy imports (already achieved, verify)
3. Zero NotImplementedError in production code paths (survival analysis implemented)
4. mypy passes with <10 type errors (down from 253 errors in verification)
5. ALL 41 scripts execute successfully on dry-run scale

**Plans:** 17 plans created

**Wave Structure:**
- Wave 1: 77-01, 77-02, 77-03, 77-13, 77-14, 77-15, 77-16 (Stage 2 migration, dynamic imports, survival analysis, mypy gap closure)
- Wave 2: 77-04, 77-07, 77-08, 77-09, 77-11 (Hypothesis tests, stats errors, V1 tests, type stubs, type ignores)
- Wave 3: 77-05, 77-10, 77-12 (Dry-run verification, stats testing, large file research)
- Wave 4: 77-06, 77-17 (Documentation update, final mypy baseline)

**Gap Closure Plans (77-13 to 77-17):**
- [ ] 77-13-PLAN.md — Reduce tokenize_and_count.py type errors from 86 to <10 (Wave 1)
- [ ] 77-14-PLAN.md — Reduce verify_step2.py type errors from 30 to <5 (Wave 1)
- [ ] 77-15-PLAN.md — Reduce construct_variables.py type errors from 19 to <5 (Wave 1)
- [ ] 77-16-PLAN.md — Document lifelines type errors with scoped ignores (Wave 1)
- [ ] 77-17-PLAN.md — Fix remaining financial and shared module errors (Wave 2)

**Original Plans:**
- [x] 77-01-PLAN.md — Migrate Stage 2 text scripts to src/f1d/text/
- [x] 77-02-PLAN.md — Eliminate dynamic module imports (sample_utils.py)
- [x] 77-03-PLAN.md — Implement survival analysis with lifelines (Wave 1)
- [x] 77-04-PLAN.md — Add tests for hypothesis scripts (Wave 2)
- [x] 77-05-PLAN.md — Verify all scripts execute on dry-run (Wave 3)
- [x] 77-06-PLAN.md — Update documentation for Phase 77 completion (Wave 4)
- [x] 77-07-PLAN.md — Reduce stats.py type errors from 56 to <10 (Wave 2)
- [x] 77-08-PLAN.md — Add test coverage for V1 legacy code (Wave 2)
- [x] 77-09-PLAN.md — Add full type stub coverage (types-pandas, types-psutil) (Wave 2)
- [x] 77-10-PLAN.md — Add tests for stats module (Wave 3)
- [x] 77-11-PLAN.md — Reduce and document type ignore comments (Wave 2)
- [x] 77-12-PLAN.md — Research: Analyze large files for Phase 78 splitting (Wave 3)

---

### Phase 78: Documentation Synchronization

**Goal:** Update ALL documentation to reflect v6.1 migrated state

**Depends on:** Phase 77 (Concerns Closure)

**Success Criteria** (what must be TRUE):
1. README.md reflects v5/6/6.1 standards and architecture
2. All legacy READMEs have deprecation notices
3. No broken internal links
4. All code examples use current import patterns (`from f1d.shared.*`)
5. New developer can clone, `pip install -e .`, and run any script without PYTHONPATH tricks

**Plans:** Not yet planned

Plans:
- [ ] TBD (run /gsd:plan-phase 78 to break down)

---

*Roadmap updated: 2026-02-14 (Phases 77-78 added to v6.1)*
