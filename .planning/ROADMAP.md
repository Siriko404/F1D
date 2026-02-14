# Roadmap: F1D Data Processing Pipeline

## Overview

Data processing pipeline for F1D thesis research. Milestones track major project phases from infrastructure to hypothesis testing to codebase standardization.

## Milestones

- Completed **v1.0** Pipeline Observability & Documentation (Phases 1-27) - shipped 2026-01-30
- Completed **v2.0** Hypothesis Testing Suite (Phases 28-58) - shipped 2026-02-06
- Completed **v3.0** Codebase Cleanup & Optimization (Phases 59-63) - shipped 2026-02-11
- Completed **v4.0** Folder Structure Consolidation (Phase 64) - shipped 2026-02-12
- Completed **v5.0** Architecture Standard Definition (Phases 65-68) - shipped 2026-02-13
- **Active:** v6.0 Architecture Standard Implementation (Phases 69-74)

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

</details>

---

## v6.0 Architecture Standard Implementation (In Progress)

**Milestone Goal:** Implement all standards defined in v5.0 across the codebase, transforming the repository into a portfolio-ready, industry-standard Python package.

**Target Outcomes:**
- src-layout package structure with proper imports
- Type-safe configuration via pydantic-settings
- Structured logging with context binding
- CI/CD pipeline with automated quality gates
- Comprehensive test suite with tier-based coverage

### Phase 69: Architecture Migration

**Goal:** Codebase uses src-layout structure with organized data directories and module tier classification.

**Depends on:** Phase 68 (Architecture Standard defined)

**Requirements:** ARCH-01, ARCH-02, ARCH-03

**Success Criteria** (what must be TRUE):
1. All code imports work from `src/f1d/` package structure
2. Every module has a documented tier classification (1/2/3) in its docstring
3. Data directories are organized by lifecycle (raw/interim/processed/external)
4. Existing scripts continue to run with zero behavioral changes

**Plans:** 3 plans

Plans:
- [x] 69-01-PLAN.md — Migrate to src-layout structure (Wave 1)
- [x] 69-02-PLAN.md — Migrate stage scripts and establish tier classification (Wave 2)
- [x] 69-03-PLAN.md — Organize data directories by lifecycle (Wave 3)

---

### Phase 70: Type Hints Implementation

**Goal:** Codebase has comprehensive type hints with mypy enforcement matching tier requirements.

**Depends on:** Phase 69 (Architecture Migration)

**Requirements:** TYPE-01, TYPE-02, TYPE-03

**Success Criteria** (what must be TRUE):
1. All Tier 1 modules have 100% type hint coverage (mypy passes with strict mode)
2. All Tier 2 modules have 80% type hint coverage (mypy passes with moderate mode)
3. mypy configuration in pyproject.toml enforces tier-based strictness
4. Type checker passes without errors on full codebase

**Plans:** 12 plans

Plans:
- [x] 70-01-PLAN.md — Add type hints to Tier 1 modules (src/f1d/shared/) (Wave 1)
- [x] 70-02-PLAN.md — Add type hints to Tier 2 modules (sample/text/financial/econometric) (Wave 1)
- [x] 70-03-PLAN.md — Configure mypy with tier-based strictness in pyproject.toml (Wave 2)
- [x] 70-04-PLAN.md — Fix stats.py TypedDict refactoring (gap closure)
- [x] 70-05-PLAN.md — Fix Tier 2 module type errors (gap closure)
- [x] 70-06-PLAN.md — Fix financial v2 high-error modules (gap closure)
- [x] 70-07-PLAN.md — Fix financial v2 medium-error modules (gap closure)
- [x] 70-08-PLAN.md — Fix financial v1 modules (gap closure)
- [x] 70-09-PLAN.md — Fix econometric v1 high-error modules (gap closure)
- [x] 70-10-PLAN.md — Fix econometric return type mismatches (gap closure)
- [x] 70-11-PLAN.md — Fix remaining econometric modules (gap closure)
- [x] 70-12-PLAN.md — Clean up remaining Tier 2 files (gap closure)

---

### Phase 71: Configuration System

**Goal:** Configuration is type-safe, validated, and supports environment variable overrides.

**Depends on:** Phase 70 (Type Hints)

**Requirements:** CONF-01, CONF-02, CONF-03

**Success Criteria** (what must be TRUE):
1. All configuration loaded through pydantic-settings BaseSettings subclass
2. Existing config/project.yaml settings migrated to typed settings classes
3. Environment variables override settings without code changes
4. Invalid configuration values raise clear validation errors

**Plans:** 3 plans

Plans:
- [x] 71-01-PLAN.md — Implement pydantic-settings base configuration (Wave 1)
- [x] 71-02-PLAN.md — Create step-specific and environment variable configs (Wave 2)
- [x] 71-03-PLAN.md — Create configuration loader with tests (Wave 3)

---

### Phase 72: Structured Logging

**Goal:** All logging is structured, JSON-formatted, with request/operation context binding.

**Depends on:** Phase 71 (Configuration System)

**Requirements:** LOGG-01, LOGG-02, LOGG-03

**Success Criteria** (what must be TRUE):
1. All scripts use structlog for logging (not standard logging module)
2. Log entries include bound context (operation ID, script name, timing)
3. Console output is human-readable (colored, formatted)
4. File output is JSON-formatted for machine parsing
5. Existing log files continue to be written with enhanced structure

**Plans:** TBD

Plans:
- [ ] 72-01: Integrate structlog for structured logging
- [ ] 72-02: Implement context binding for tracking
- [ ] 72-03: Configure dual output (console/file)

---

### Phase 73: CI/CD Pipeline

**Goal:** Automated quality gates run on every commit with matching pre-commit hooks.

**Depends on:** Phase 72 (Structured Logging)

**Requirements:** CICD-01, CICD-02, CICD-03

**Success Criteria** (what must be TRUE):
1. pyproject.toml contains all tool configurations (ruff, mypy, pytest)
2. GitHub Actions workflow runs lint, type-check, and test on push/PR
3. Pre-commit hooks match CI configuration exactly
4. CI fails on any quality gate violation (lint errors, type errors, test failures)

**Plans:** TBD

Plans:
- [ ] 73-01: Create pyproject.toml with consolidated configs
- [ ] 73-02: Set up GitHub Actions workflow
- [ ] 73-03: Configure pre-commit hooks

---

### Phase 74: Testing Infrastructure

**Goal:** Comprehensive test suite with factory fixtures and tier-based coverage targets.

**Depends on:** Phase 73 (CI/CD Pipeline)

**Requirements:** TEST-01, TEST-02, TEST-03, TEST-04

**Success Criteria** (what must be TRUE):
1. pytest infrastructure established with conftest.py at package root
2. Tier 1 modules have 90% test coverage (unit tests)
3. Tier 2 modules have 80% test coverage (integration tests)
4. Factory fixtures generate test data without fixture pyramids
5. CI reports coverage numbers and fails below thresholds

**Plans:** TBD

Plans:
- [ ] 74-01: Establish pytest infrastructure
- [ ] 74-02: Add Tier 1 unit tests
- [ ] 74-03: Add Tier 2 integration tests
- [ ] 74-04: Implement factory fixtures

---

## Progress

**Execution Order:**
Phases execute in numeric order: 69 -> 70 -> 71 -> 72 -> 73 -> 74

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 69. Architecture Migration | v6.0 | 3/3 | Complete | 2026-02-13 |
| 70. Type Hints | v6.0 | 12/12 | Complete | 2026-02-14 |
| 71. Configuration System | v6.0 | 3/3 | Complete | 2026-02-13 |
| 72. Structured Logging | v6.0 | 0/3 | Not started | - |
| 73. CI/CD Pipeline | v6.0 | 0/3 | Not started | - |
| 74. Testing Infrastructure | v6.0 | 0/4 | Not started | - |

---

*Roadmap updated: 2026-02-13 (Phase 71 complete)*
