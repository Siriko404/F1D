# Requirements: F1D Data Processing Pipeline

**Defined:** 2026-02-12
**Core Value:** Every script must produce verifiable, reproducible results with complete audit trails
**Status:** Active — v5.0 Architecture Standard Definition

## v5.0 Requirements

Requirements for Architecture Standard Definition milestone. v5.0 defines comprehensive standards for portfolio-ready repository quality. The output is ARCHITECTURE_STANDARD.md that guides subsequent implementation milestones (v6.0+).

**Key Deliverable:** Single ARCHITECTURE_STANDARD.md document defining all standards.

**Implementation:** Standards definition only. Actual refactoring deferred to v6.0+.

---

### ARCH — Architecture & Folder Structure

- [ ] **ARCH-01**: Define canonical folder structure (src/f1d/, tests/, docs/, config/, data/)
- [ ] **ARCH-02**: Define module organization with __init__.py pattern
- [ ] **ARCH-03**: Define data directory structure (data/raw/, data/processed/, results/)
- [ ] **ARCH-04**: Define version management approach (deprecate V1, single active version)
- [ ] **ARCH-05**: Define archive and legacy code handling strategy

### NAM — Naming Conventions

- [ ] **NAM-01**: Define script naming convention (Stage.Step_Description.py pattern)
- [ ] **NAM-02**: Define module naming convention (snake_case with clarity)
- [ ] **NAM-03**: Define function/class naming (snake_case for functions, PascalCase for classes)
- [ ] **NAM-04**: Define variable naming patterns (descriptive, consistent)
- [ ] **NAM-05**: Define output file naming patterns (timestamped, script-identified)

### CODE — Code Quality Standards

- [ ] **CODE-01**: Define docstring standard (Google-style with Args/Returns/Raises/Examples)
- [ ] **CODE-02**: Define type hint coverage requirements (strict mode targets per module tier)
- [ ] **CODE-03**: Define import organization pattern (stdlib → third-party → local, no fallbacks)
- [ ] **CODE-04**: Define error handling pattern (custom exceptions, no bare except, explicit propagation)
- [ ] **CODE-05**: Define function size limits and module organization (max lines, single responsibility)

### CONF — Configuration & I/O

- [ ] **CONF-01**: Define config file structure (project.yaml schema with validation)
- [ ] **CONF-02**: Define environment variable handling (secrets, optional dependencies)
- [ ] **CONF-03**: Define path resolution pattern (eliminate sys.path.insert, proper package imports)
- [ ] **CONF-04**: Define output directory pattern (timestamped runs, latest symlink, checksums)
- [ ] **CONF-05**: Define logging pattern (structured logging, levels, output destinations)

### TEST — Testing Standards

- [ ] **TEST-01**: Define test structure (unit/integration/regression/e2e/performance)
- [ ] **TEST-02**: Define coverage targets (Tier 1: 90%, Tier 2: 80%, Overall: 70%)
- [ ] **TEST-03**: Define test naming convention (test_<module>_<function>_<scenario>)
- [ ] **TEST-04**: Define fixture organization pattern (conftest.py, fixtures/, factories)
- [ ] **TEST-05**: Define mocking and test data patterns (fixtures, fakes, mocks)

### DOC — Documentation Standards

- [ ] **DOC-01**: Define README structure (badges, description, quickstart, usage, API, license)
- [ ] **DOC-02**: Define CHANGELOG format (Keep a Changelog format)
- [ ] **DOC-03**: Define CONTRIBUTING guide structure (setup, workflow, standards, PR process)
- [ ] **DOC-04**: Define API documentation approach (docstrings → MkDocs/Sphinx)
- [ ] **DOC-05**: Define code comments and inline documentation standard (when to comment)

### TOOL — Tooling & CI/CD

- [ ] **TOOL-01**: Define pyproject.toml structure (build system, dependencies, tool configs)
- [ ] **TOOL-02**: Define pre-commit hooks configuration (ruff, mypy, trailing whitespace)
- [ ] **TOOL-03**: Define GitHub Actions workflow structure (test matrix, coverage, linting)
- [ ] **TOOL-04**: Define .gitignore patterns (Python, data, IDE, OS-specific)
- [ ] **TOOL-05**: Define linting/formatting configuration (ruff rules, mypy strictness levels)

---

## v4.0 Requirements (COMPLETE)

Requirements for Script Organization & Refactoring milestone. V4 focuses on consolidating folder structure, standardizing I/O patterns, unifying logging, and enforcing naming conventions.

**Key Constraints:**
- **Two active versions only** — V1 and V2 (V3 was created by mistake, merge into V2)
- **Sequential refactoring** — Each script refactored and verified immediately
- **Config-driven I/O** — All paths from config/project.yaml
- **Output pattern** — 4_Outputs/[family]/[script]/[timestamp]

---

## Folder Structure (STR)

### STR-01: Merge 3_Financial_V3 into 3_Financial_V2

- [ ] **STR-01-01**: Move 4.1_H2_BiddleInvestmentResidual.py to 3_Financial_V2 (rename to 3.9_H2_BiddleInvestmentResidual.py)
- [ ] **STR-01-02**: Move 4.2_H2_PRiskUncertaintyMerge.py to 3_Financial_V2 (rename to 3.10_H2_PRiskUncertaintyMerge.py)
- [ ] **STR-01-03**: Update imports in moved scripts
- [ ] **STR-01-04**: Update all references to moved scripts
- [ ] **STR-01-05**: Verify moved scripts run correctly

### STR-02: Merge 4_Econometric_V3 into 4_Econometric_V2

- [ ] **STR-02-01**: Move 4.3_H2_PRiskUncertainty_Investment.py to 4_Econometric_V2 (rename to 4.10_H2_PRiskUncertainty_Investment.py)
- [ ] **STR-02-02**: Update imports in moved script
- [ ] **STR-02-03**: Update all references to moved script
- [ ] **STR-02-04**: Verify moved script runs correctly

### STR-03: Merge 5_Financial_V3 into V2 folders

- [ ] **STR-03-01**: Move 5.8_H9_StyleFrozen.py to 3_Financial_V2 (rename to 3.11_H9_StyleFrozen.py)
- [ ] **STR-03-02**: Move 5.8_H9_PRiskFY.py to 3_Financial_V2 (rename to 3.12_H9_PRiskFY.py)
- [ ] **STR-03-03**: Move 5.8_H9_AbnormalInvestment.py to 3_Financial_V2 (rename to 3.13_H9_AbnormalInvestment.py)
- [ ] **STR-03-04**: Move 5.8_H9_FinalMerge.py to 4_Econometric_V2 (rename to 4.11_H9_Regression.py - it's a regression script)
- [ ] **STR-03-05**: Update imports in all moved scripts
- [ ] **STR-03-06**: Update all references to moved scripts
- [ ] **STR-03-07**: Verify all moved scripts run correctly

### STR-04: Remove V3 folders

- [ ] **STR-04-01**: Remove empty 3_Financial_V3/ folder
- [ ] **STR-04-02**: Remove empty 4_Econometric_V3/ folder
- [ ] **STR-04-03**: Remove empty 5_Financial_V3/ folder
- [ ] **STR-04-04**: Update any documentation referencing V3 folders

### STR-05: Update Output folder structure

- [ ] **STR-05-01**: Move outputs from 4_Outputs/5.8_H9_*/ to 4_Outputs/3_Financial_V2/3.11_H9_StyleFrozen/
- [ ] **STR-05-02**: Move outputs from 4_Outputs/5.8_H9_*/ to 4_Outputs/3_Financial_V2/3.12_H9_PRiskFY/
- [ ] **STR-05-03**: Move outputs from 4_Outputs/5.8_H9_*/ to 4_Outputs/3_Financial_V2/3.13_H9_AbnormalInvestment/
- [ ] **STR-05-04**: Move outputs from 4_Outputs/5.8_H9_*/ to 4_Outputs/4_Econometric_V2/4.11_H9_Regression/
- [ ] **STR-05-05**: Update config paths to new output locations

---

## I/O Pattern (IO)

### IO-01: Define Config-Driven Path Standard

- [ ] **IO-01-01**: Audit current I/O patterns across all scripts
- [ ] **IO-01-02**: Define standard input path retrieval function (get_input_path)
- [ ] **IO-01-03**: Define standard output path generation function (get_output_path)
- [ ] **IO-01-04**: Update config/project.yaml with path templates for all stages
- [ ] **IO-01-05**: Document I/O pattern in CLAUDE.md

### IO-02: V1 Sample Scripts I/O

- [ ] **IO-02-01**: Update 1.0_BuildSampleManifest.py to use config-driven I/O
- [ ] **IO-02-02**: Update 1.1_CleanMetadata.py to use config-driven I/O
- [ ] **IO-02-03**: Update 1.2_EntityLinking.py to use config-driven I/O
- [ ] **IO-02-04**: Update 1.3_BuildTenureMap.py to use config-driven I/O
- [ ] **IO-02-05**: Verify V1 Sample scripts produce correct outputs

### IO-03: V1 Text Scripts I/O

- [ ] **IO-03-01**: Update 2.0_ValidateV2Structure.py to use config-driven I/O
- [ ] **IO-03-02**: Update 2.1_TokenizeAndCount.py to use config-driven I/O
- [ ] **IO-03-03**: Update 2.2_ConstructVariables.py to use config-driven I/O
- [ ] **IO-03-04**: Update 2.3_VerifyTextOutputs.py to use config-driven I/O
- [ ] **IO-03-05**: Verify V1 Text scripts produce correct outputs

### IO-04: V1 Financial Scripts I/O

- [ ] **IO-04-01**: Update 3.0_BuildFinancialFeatures.py to use config-driven I/O
- [ ] **IO-04-02**: Update 3.1_MergeFirmControls.py to use config-driven I/O
- [ ] **IO-04-03**: Update 3.2_MarketVariables.py to use config-driven I/O
- [ ] **IO-04-04**: Update 3.3_EventFlags.py to use config-driven I/O
- [ ] **IO-04-05**: Verify V1 Financial scripts produce correct outputs

### IO-05: V1 Econometric Scripts I/O

- [ ] **IO-05-01**: Update 4.0_EstimateCeoClarity.py to use config-driven I/O
- [ ] **IO-05-02**: Update 4.1.4_EstimateCeoTone.py to use config-driven I/O
- [ ] **IO-05-03**: Update 4.2_EstimateLiquidityEffect.py to use config-driven I/O
- [ ] **IO-05-04**: Update 4.3_TakeoverHazards.py to use config-driven I/O
- [ ] **IO-05-05**: Verify V1 Econometric scripts produce correct outputs

### IO-06: V2 Financial Scripts I/O

- [ ] **IO-06-01**: Update 3.1_H1Variables.py to use config-driven I/O
- [ ] **IO-06-02**: Update 3.2_H2Variables.py to use config-driven I/O
- [ ] **IO-06-03**: Update 3.3_H3Variables.py to use config-driven I/O
- [ ] **IO-06-04**: Update 3.5_H5Variables.py to use config-driven I/O
- [ ] **IO-06-05**: Update 3.6_H6Variables.py to use config-driven I/O
- [ ] **IO-06-06**: Update 3.7_H7IlliquidityVariables.py to use config-driven I/O
- [ ] **IO-06-07**: Update 3.8_H8TakeoverVariables.py to use config-driven I/O
- [ ] **IO-06-08**: Update 3.9_H2_BiddleInvestmentResidual.py (moved) to use config-driven I/O
- [ ] **IO-06-09**: Update 3.10_H2_PRiskUncertaintyMerge.py (moved) to use config-driven I/O
- [ ] **IO-06-10**: Update 3.11_H9_StyleFrozen.py (moved) to use config-driven I/O
- [ ] **IO-06-11**: Update 3.12_H9_PRiskFY.py (moved) to use config-driven I/O
- [ ] **IO-06-12**: Update 3.13_H9_AbnormalInvestment.py (moved) to use config-driven I/O
- [ ] **IO-06-13**: Verify all V2 Financial scripts produce correct outputs

### IO-07: V2 Econometric Scripts I/O

- [ ] **IO-07-01**: Update 4.1_H1CashHoldingsRegression.py to use config-driven I/O
- [ ] **IO-07-02**: Update 4.2_H2InvestmentEfficiencyRegression.py to use config-driven I/O
- [ ] **IO-07-03**: Update 4.3_H3PayoutPolicyRegression.py to use config-driven I/O
- [ ] **IO-07-04**: Update 4.4_H4_LeverageDiscipline.py to use config-driven I/O
- [ ] **IO-07-05**: Update 4.5_H5DispersionRegression.py to use config-driven I/O
- [ ] **IO-07-06**: Update 4.6_H6CCCLRegression.py to use config-driven I/O
- [ ] **IO-07-07**: Update 4.7_H7IlliquidityRegression.py to use config-driven I/O
- [ ] **IO-07-08**: Update 4.8_H8TakeoverRegression.py to use config-driven I/O
- [ ] **IO-07-09**: Update 4.9_CEOFixedEffects.py to use config-driven I/O
- [ ] **IO-07-10**: Update 4.10_H2_PRiskUncertainty_Investment.py (moved) to use config-driven I/O
- [ ] **IO-07-11**: Update 4.11_H9_Regression.py (moved) to use config-driven I/O
- [ ] **IO-07-12**: Verify all V2 Econometric scripts produce correct outputs

### IO-08: Shared Utilities I/O Support

- [ ] **IO-08-01**: Create get_input_path() in shared/path_utils.py
- [ ] **IO-08-02**: Create get_output_path() in shared/path_utils.py
- [ ] **IO-08-03**: Create get_latest_output_dir() wrapper for config-driven paths
- [ ] **IO-08-04**: Document path utility functions in module docstring

---

## Logging (LOG)

### LOG-01: Audit Current Logging

- [ ] **LOG-01-01**: Audit logging implementation in V1 Sample scripts
- [ ] **LOG-01-02**: Audit logging implementation in V1 Text scripts
- [ ] **LOG-01-03**: Audit logging implementation in V1 Financial scripts
- [ ] **LOG-01-04**: Audit logging implementation in V1 Econometric scripts
- [ ] **LOG-01-05**: Audit logging implementation in V2 Financial scripts
- [ ] **LOG-01-06**: Audit logging implementation in V2 Econometric scripts
- [ ] **LOG-01-07**: Document logging inconsistencies and gaps

### LOG-02: Define Standard Logging Pattern

- [ ] **LOG-02-01**: Decide: Use observability_utils.logging or create new standard
- [ ] **LOG-02-02**: Define required log fields (timestamp, script, level, message)
- [ ] **LOG-02-03**: Define dual logging pattern (console + file)
- [ ] **LOG-02-04**: Create setup_logging() function if not using existing
- [ ] **LOG-02-05**: Document logging standard in CLAUDE.md

### LOG-03: V1 Scripts Logging Standardization

- [ ] **LOG-03-01**: Standardize logging in 1_Sample/ scripts
- [ ] **LOG-03-02**: Standardize logging in 2_Text/ scripts
- [ ] **LOG-03-03**: Standardize logging in 3_Financial/ scripts
- [ ] **LOG-03-04**: Standardize logging in 4_Econometric/ scripts
- [ ] **LOG-03-05**: Verify V1 scripts produce consistent logs

### LOG-04: V2 Scripts Logging Standardization

- [ ] **LOG-04-01**: Standardize logging in 3_Financial_V2/ scripts
- [ ] **LOG-04-02**: Standardize logging in 4_Econometric_V2/ scripts
- [ ] **LOG-04-03**: Verify V2 scripts produce consistent logs

---

## Naming Conventions (NAM)

### NAM-01: Define Naming Standard

- [ ] **NAM-01-01**: Define script naming pattern: {Stage}.{Step}_{PascalCaseName}.py
- [ ] **NAM-01-02**: Define output folder naming: {Stage}_{Family}/{Stage}.{Step}_{Name}/
- [ ] **NAM-01-03**: Document naming conventions in CLAUDE.md
- [ ] **NAM-01-04**: Create naming validation script

### NAM-02: Audit Current Names

- [ ] **NAM-02-01**: Audit V1 Sample script names for compliance
- [ ] **NAM-02-02**: Audit V1 Text script names for compliance
- [ ] **NAM-02-03**: Audit V1 Financial script names for compliance
- [ ] **NAM-02-04**: Audit V1 Econometric script names for compliance
- [ ] **NAM-02-05**: Audit V2 Financial script names for compliance
- [ ] **NAM-02-06**: Audit V2 Econometric script names for compliance
- [ ] **NAM-02-07**: Create list of non-compliant names

### NAM-03: Rename Non-Compliant Scripts

- [ ] **NAM-03-01**: Rename non-compliant V1 scripts
- [ ] **NAM-03-02**: Rename non-compliant V2 scripts
- [ ] **NAM-03-03**: Update all import references after renaming
- [ ] **NAM-03-04**: Update config paths after renaming
- [ ] **NAM-03-05**: Verify renamed scripts run correctly

---

## Verification (VER)

### VER-01: V1 Sample Verification

- [ ] **VER-01-01**: Run 1.0_BuildSampleManifest.py and verify output
- [ ] **VER-01-02**: Run 1.1_CleanMetadata.py and verify output
- [ ] **VER-01-03**: Run 1.2_EntityLinking.py and verify output
- [ ] **VER-01-04**: Run 1.3_BuildTenureMap.py and verify output
- [ ] **VER-01-05**: Compare outputs to pre-refactoring baselines

### VER-02: V1 Text Verification

- [ ] **VER-02-01**: Run 2.1_TokenizeAndCount.py and verify output
- [ ] **VER-02-02**: Run 2.2_ConstructVariables.py and verify output
- [ ] **VER-02-03**: Run 2.3_VerifyTextOutputs.py and verify output
- [ ] **VER-02-04**: Compare outputs to pre-refactoring baselines

### VER-03: V1 Financial Verification

- [ ] **VER-03-01**: Run 3.0_BuildFinancialFeatures.py and verify output
- [ ] **VER-03-02**: Run 3.1_MergeFirmControls.py and verify output
- [ ] **VER-03-03**: Run 3.2_MarketVariables.py and verify output
- [ ] **VER-03-04**: Run 3.3_EventFlags.py and verify output
- [ ] **VER-03-05**: Compare outputs to pre-refactoring baselines

### VER-04: V1 Econometric Verification

- [ ] **VER-04-01**: Run 4.0_EstimateCeoClarity.py and verify output
- [ ] **VER-04-02**: Run 4.1.4_EstimateCeoTone.py and verify output
- [ ] **VER-04-03**: Run 4.2_EstimateLiquidityEffect.py and verify output
- [ ] **VER-04-04**: Compare outputs to pre-refactoring baselines

### VER-05: V2 Financial Verification

- [ ] **VER-05-01**: Run all 3_Financial_V2/ scripts and verify outputs
- [ ] **VER-05-02**: Compare outputs to pre-refactoring baselines
- [ ] **VER-05-03**: Verify H1-H9 variable construction

### VER-06: V2 Econometric Verification

- [ ] **VER-06-01**: Run all 4_Econometric_V2/ scripts and verify outputs
- [ ] **VER-06-02**: Compare outputs to pre-refactoring baselines
- [ ] **VER-06-03**: Verify H1-H9 regression results

### VER-07: Test Suite Verification

- [ ] **VER-07-01**: Run pytest on tests/ directory
- [ ] **VER-07-02**: Verify all tests pass
- [ ] **VER-07-03**: Update any broken tests

### VER-08: End-to-End Pipeline Verification

- [ ] **VER-08-01**: Run full V1 pipeline from start to finish
- [ ] **VER-08-02**: Run full V2 pipeline from start to finish
- [ ] **VER-08-03**: Compare final outputs to pre-refactoring baselines
- [ ] **VER-08-04**: Document any differences and their causes

---

## Out of Scope

Explicitly excluded from v5.0:

| Feature | Reason |
|---------|--------|
| Actual refactoring | Implementation deferred to v6.0+ |
| New features | Standards definition only |
| New hypotheses | Complete in v2.0 |
| Real-time processing | Batch processing per thesis scope |
| Web interface | CLI only for replication |

## v6.0 Requirements (Deferred)

Implementation of the standards defined in v5.0. Will be replanned after v5.0 completes.

---

## v4.0 Out of Scope (Historical)

Explicitly excluded from v4.0:

| Feature | Reason |
|---------|--------|
| New hypotheses | This milestone is refactoring only |
| New features | Refactoring only, no functionality changes |
| Performance optimization | Already addressed in v3.0 |
| Documentation enhancement | Already addressed in v3.0 |
| Data changes | No changes to data processing logic |
| Archive V1 or V2 | Both versions are active and in use |

---

## Traceability

### v5.0 Requirements (Architecture Standard)

Which phases cover which requirements. To be updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | TBD | Pending |
| ARCH-02 | TBD | Pending |
| ARCH-03 | TBD | Pending |
| ARCH-04 | TBD | Pending |
| ARCH-05 | TBD | Pending |
| NAM-01 | TBD | Pending |
| NAM-02 | TBD | Pending |
| NAM-03 | TBD | Pending |
| NAM-04 | TBD | Pending |
| NAM-05 | TBD | Pending |
| CODE-01 | TBD | Pending |
| CODE-02 | TBD | Pending |
| CODE-03 | TBD | Pending |
| CODE-04 | TBD | Pending |
| CODE-05 | TBD | Pending |
| CONF-01 | TBD | Pending |
| CONF-02 | TBD | Pending |
| CONF-03 | TBD | Pending |
| CONF-04 | TBD | Pending |
| CONF-05 | TBD | Pending |
| TEST-01 | TBD | Pending |
| TEST-02 | TBD | Pending |
| TEST-03 | TBD | Pending |
| TEST-04 | TBD | Pending |
| TEST-05 | TBD | Pending |
| DOC-01 | TBD | Pending |
| DOC-02 | TBD | Pending |
| DOC-03 | TBD | Pending |
| DOC-04 | TBD | Pending |
| DOC-05 | TBD | Pending |
| TOOL-01 | TBD | Pending |
| TOOL-02 | TBD | Pending |
| TOOL-03 | TBD | Pending |
| TOOL-04 | TBD | Pending |
| TOOL-05 | TBD | Pending |

**v5.0 Coverage:**
- Requirements: 35 total
- Mapped to phases: 0
- Unmapped: 35 ⚠️

---

### v4.0 Requirements (Folder Consolidation) - COMPLETE

| Requirement Category | Requirements | Phase | Sub-requirements | Status |
|---------------------|--------------|-------|------------------|--------|
| STR-01 | Merge 3_Financial_V3 into 3_Financial_V2 | 64 | 5 | Pending |
| STR-02 | Merge 4_Econometric_V3 into 4_Econometric_V2 | 64 | 4 | Pending |
| STR-03 | Merge 5_Financial_V3 into V2 folders | 64 | 7 | Pending |
| STR-04 | Remove V3 folders | 64 | 4 | Pending |
| STR-05 | Update Output folder structure | 64 | 5 | Pending |
| IO-01 | Define Config-Driven Path Standard | 65 | 5 | Pending |
| IO-02 | V1 Sample Scripts I/O | 65 | 5 | Pending |
| IO-03 | V1 Text Scripts I/O | 65 | 5 | Pending |
| IO-04 | V1 Financial Scripts I/O | 65 | 5 | Pending |
| IO-05 | V1 Econometric Scripts I/O | 65 | 5 | Pending |
| IO-06 | V2 Financial Scripts I/O | 65 | 13 | Pending |
| IO-07 | V2 Econometric Scripts I/O | 65 | 12 | Pending |
| IO-08 | Shared Utilities I/O Support | 65 | 4 | Pending |
| LOG-01 | Audit Current Logging | 66 | 7 | Pending |
| LOG-02 | Define Standard Logging Pattern | 66 | 5 | Pending |
| LOG-03 | V1 Scripts Logging Standardization | 66 | 5 | Pending |
| LOG-04 | V2 Scripts Logging Standardization | 66 | 3 | Pending |
| NAM-01 | Define Naming Standard | 67 | 4 | Pending |
| NAM-02 | Audit Current Names | 67 | 7 | Pending |
| NAM-03 | Rename Non-Compliant Scripts | 67 | 5 | Pending |
| VER-01 | V1 Sample Verification | 68 | 5 | Pending |
| VER-02 | V1 Text Verification | 68 | 4 | Pending |
| VER-03 | V1 Financial Verification | 68 | 5 | Pending |
| VER-04 | V1 Econometric Verification | 68 | 4 | Pending |
| VER-05 | V2 Financial Verification | 68 | 3 | Pending |
| VER-06 | V2 Econometric Verification | 68 | 3 | Pending |
| VER-07 | Test Suite Verification | 68 | 3 | Pending |
| VER-08 | End-to-End Pipeline Verification | 68 | 4 | Pending |

**Total Requirements:** 28 categories, 134 sub-requirements
**Coverage:** 100% mapped to phases 64-68

---

## v3.0 Requirements (COMPLETE)

All v3.0 requirements have been completed. See git history for details.

---

*Requirements defined: 2026-02-12*
*Last updated: 2026-02-12 (v5.0 requirements defined)*
