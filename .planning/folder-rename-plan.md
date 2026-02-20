# Folder Rename Plan: inputs, logs, outputs

**Date:** 2026-02-17
**Team:** folder-rename-planning
**Status:** READY FOR REVIEW

---

## Executive Summary

This plan documents the comprehensive renaming of three numbered folders to lowercase:
- `inputs/` -> `inputs/`
- `logs/` -> `logs/`
- `outputs/` -> `outputs/`

**Impact Scope:**
- **Total files needing modifications:** ~303 files
- **Python files:** ~78 files
- **Configuration files:** 4 files (project.yaml, paths.py, GitHub workflow)
- **Documentation files:** ~80 files
- **Planning/documentation archives:** ~140 files

---

## 1. Critical Files (MUST MODIFY)

### 1.1 Configuration Files

| File | Changes Required |
|------|-----------------|
| `config/project.yaml` | Line 9: `inputs` -> `inputs`<br>Line 11: `logs` -> `logs`<br>Line 12: `outputs` -> `outputs`<br>Line 13: `inputs/Loughran-McDonald_...` -> `inputs/Loughran-McDonald_...`<br>Line 14: `inputs/Earnings_Calls_Transcripts/...` -> `inputs/Earnings_Calls_Transcripts/...`<br>Line 15: `inputs/Earnings_Calls_Transcripts/...` -> `inputs/Earnings_Calls_Transcripts/...`<br>Line 142: `inputs/CCCL instrument/...` -> `inputs/CCCL instrument/...` |

### 1.2 Core Path Utilities (HIGH PRIORITY)

| File | Changes Required |
|------|-----------------|
| `src/f1d/shared/path_utils.py` | Line 133: `INPUTS_DIR = Path("inputs")` -> `Path("inputs")`<br>Line 136: `OUTPUTS_DIR = Path("outputs")` -> `Path("outputs")`<br>Line 139: `OLD_LOGS_DIR = Path("logs")` -> `Path("logs")`<br>Line 356: `"inputs": "raw"` -> `"inputs": "raw"`<br>Line 357: `"inputs": "raw"` (unchanged)<br>Line 358: `"outputs": "interim"` -> `"outputs": "interim"`<br>Line 359: `"outputs": "interim"` (unchanged)<br>Line 360: `"logs": "logs"` -> `"logs": "logs"`<br>Line 379: Update `INPUTS_DIR` reference |

### 1.3 Config/Paths Module

| File | Changes Required |
|------|-----------------|
| `src/f1d/shared/config/paths.py` | Line 41: `logs: str = Field(default="logs", ...)` -> `default="logs"` |

### 1.4 Logging Module

| File | Changes Required |
|------|-----------------|
| `src/f1d/shared/logging/handlers.py` | Line 28: `DEFAULT_LOG_DIR = Path("logs")` -> `Path("logs")`<br>All docstring examples using `logs` to use `logs` |
| `src/f1d/shared/logging/__init__.py` | Line 19: Update docstring example |

### 1.5 GitHub Workflow (CRITICAL - External CI/CD)

| File | Changes Required |
|------|-----------------|
| `.github/workflows/test.yml` | Line 200: `logs/` -> `logs/` |

---

## 2. Sample Stage Scripts (src/f1d/sample/)

| File | Changes Required |
|------|-----------------|
| `src/f1d/sample/1.0_BuildSampleManifest.py` | All `inputs` references -> `inputs`<br>All `logs` references -> `logs`<br>All `outputs` references -> `outputs` |
| `src/f1d/sample/1.1_CleanMetadata.py` | All `inputs` references -> `inputs`<br>All `logs` references -> `logs`<br>All `outputs` references -> `outputs` |
| `src/f1d/sample/1.2_LinkEntities.py` | All `logs` references -> `logs`<br>All `outputs` references -> `outputs` |
| `src/f1d/sample/1.3_BuildTenureMap.py` | All `logs` references -> `logs`<br>All `outputs` references -> `outputs` |
| `src/f1d/sample/1.4_AssembleManifest.py` | All `logs` references -> `logs`<br>All `outputs` references -> `outputs` |
| `src/f1d/sample/1.5_Utils.py` | Any path references |

---

## 3. Text Processing Scripts (src/f1d/text/)

| File | Changes Required |
|------|-----------------|
| `src/f1d/text/tokenize_and_count.py` | All `inputs` references -> `inputs`<br>All `logs` references -> `logs`<br>All `outputs` references -> `outputs` |
| `src/f1d/text/construct_variables.py` | All `inputs` references -> `inputs`<br>All `logs` references -> `logs`<br>All `outputs` references -> `outputs` |
| `src/f1d/text/verify_step2.py` | All `logs` references -> `logs`<br>All `outputs` references -> `outputs` |
| `src/f1d/text/report_step2.py` | All `logs` references -> `logs`<br>All `outputs` references -> `outputs` |

---

## 4. Financial V2 Scripts (src/f1d/financial/v2/)

All files in this directory require path updates:

| File | Changes Required |
|------|-----------------|
| `3.1_H1Variables.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.2_H2Variables.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.2a_AnalystDispersionPatch.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.3_H3Variables.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.5_H5Variables.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.6_H6Variables.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.7_H7IlliquidityVariables.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.8_H8TakeoverVariables.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.9_H2_BiddleInvestmentResidual.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.10_H2_PRiskUncertaintyMerge.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.11_H9_StyleFrozen.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.12_H9_PRiskFY.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `3.13_H9_AbnormalInvestment.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |

---

## 5. Econometric Scripts

### 5.1 V2 Scripts (src/f1d/econometric/v2/)

| File | Changes Required |
|------|-----------------|
| `4.1_H1CashHoldingsRegression.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.2_H2InvestmentEfficiencyRegression.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.3_H3PayoutPolicyRegression.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.4_H4_LeverageDiscipline.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.5_H5DispersionRegression.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.6_H6CCCLRegression.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.7_H7IlliquidityRegression.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.8_H8TakeoverRegression.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.9_CEOFixedEffects.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.10_H2_PRiskUncertainty_Investment.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.11_H9_Regression.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |

### 5.2 V1 Scripts (src/f1d/econometric/v1/)

| File | Changes Required |
|------|-----------------|
| `4.1_EstimateManagerClarity.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.1.1_EstimateCeoClarity.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.1.2_EstimateCeoClarity_Extended.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.1.3_EstimateCeoClarity_Regime.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.1.4_EstimateCeoTone.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.2_LiquidityRegressions.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.3_TakeoverHazards.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |
| `4.4_GenerateSummaryStats.py` | All `logs` -> `logs`<br>All `outputs` -> `outputs` |

---

## 6. Test Files

| File | Changes Required |
|------|-----------------|
| `tests/unit/test_path_utils.py` | Line 59: `assert OLD_LOGS_DIR == Path("logs")` -> `Path("logs")` |
| `tests/integration/test_config_integration.py` | Lines 506, 532: Update test paths for `inputs` and `logs` |
| `tests/verification/test_stage1_dryrun.py` | Update path references |
| `tests/verification/test_stage2_dryrun.py` | Update path references |

---

## 7. Documentation Files

### 7.1 Core Documentation

| File | Changes Required |
|------|-----------------|
| `README.md` | All `inputs/`, `logs/`, `outputs/` references |
| `SCALING.md` | All path references |
| `docs/ARCHITECTURE_STANDARD.md` | All path references |
| `docs/CODE_QUALITY_STANDARD.md` | All path references |
| `docs/SCRIPT_DOCSTANDARD.md` | All path references |
| `docs/DOC_TOOLING_STANDARD.md` | All path references |
| `.gitignore` | Lines 165-167: Update folder names |

### 7.2 Planning/Documentation Archives

All files in `.planning/` directory containing references to the old folder names need updates. These are primarily historical documentation that should be updated for consistency.

---

## 8. Order of Operations

### Phase 1: Preparation (DO NOT COMMIT YET)

1. **Create backup of current state**
   ```bash
   cp -r config/project.yaml config/project.yaml.backup
   ```

2. **Verify current folder structure exists**
   ```bash
   ls -la | grep -E "inputs|logs|outputs"
   ```

### Phase 2: Code Updates (COMMIT AFTER EACH SUB-PHASE)

2.1 **Update configuration files first**
   - `config/project.yaml`

2.2 **Update core path utilities**
   - `src/f1d/shared/path_utils.py`
   - `src/f1d/shared/config/paths.py`
   - `src/f1d/shared/logging/handlers.py`
   - `src/f1d/shared/logging/__init__.py`

2.3 **Update sample stage scripts**
   - All `src/f1d/sample/*.py` files

2.4 **Update text processing scripts**
   - All `src/f1d/text/*.py` files

2.5 **Update financial scripts**
   - All `src/f1d/financial/v2/*.py` files
   - All `src/f1d/financial/v1/*.py` files (if any exist)

2.6 **Update econometric scripts**
   - All `src/f1d/econometric/v2/*.py` files
   - All `src/f1d/econometric/v1/*.py` files

2.7 **Update shared utilities**
   - `src/f1d/shared/data_loading.py`
   - Any other shared files with path references

2.8 **Update test files**
   - All files in `tests/` directory

2.9 **Update GitHub workflow (CRITICAL)**
   - `.github/workflows/test.yml`

### Phase 3: Documentation Updates (COMMIT)

3.1 **Update core documentation**
   - `README.md`
   - `SCALING.md`
   - All files in `docs/` directory

3.2 **Update .gitignore**
   - Update folder name entries

### Phase 4: Actual Folder Renaming (FINAL COMMIT)

4.1 **Rename the folders**
   ```bash
   git mv inputs inputs
   git mv logs logs
   git mv outputs outputs
   ```

4.2 **Verify no hardcoded references remain**
   ```bash
   grep -r "inputs" --include="*.py" --include="*.yaml" --include="*.md" .
   grep -r "logs" --include="*.py" --include="*.yaml" --include="*.md" .
   grep -r "outputs" --include="*.py" --include="*.yaml" --include="*.md" .
   ```

4.3 **Run basic validation tests**
   ```bash
   pytest tests/unit/test_path_utils.py
   pytest tests/integration/test_config_integration.py
   ```

---

## 9. Potential Risks and Edge Cases

### 9.1 High-Risk Areas

1. **Hard-coded paths in external dependencies or pipelines**
   - Risk: External CI/CD or data pipelines may reference old folder names
   - Mitigation: Check `.github/workflows/` and any external job scripts

2. **Symlinks or junctions pointing to old folders**
   - Risk: Existing symlinks will break
   - Mitigation: Check for symlinks and update targets

3. **Large dataset files in folders**
   - Risk: Git rename operations with large files may be slow or problematic
   - Mitigation: Use `git mv` to preserve history, verify no data loss

4. **User workflows/expectations**
   - Risk: Documentation or user scripts may assume old folder names
   - Mitigation: Update all user-facing documentation first

### 9.2 Medium-Risk Areas

1. **Legacy code paths**
   - Risk: The codebase has backward compatibility functions that reference old paths
   - Mitigation: Update `path_utils.py` deprecation mappings appropriately

2. **Backup/archive files**
   - Risk: Backup files may reference old paths
   - Mitigation: Update backup procedures after rename

3. **Test fixtures and mocks**
   - Risk: Test fixtures may mock old paths
   - Mitigation: Update all test files comprehensively

### 9.3 Low-Risk Areas

1. **Historical planning documents**
   - Risk: Inconsistent documentation in `.planning/` archives
   - Mitigation: These are historical, may not need updates (add disclaimer)

---

## 10. Verification Steps

### 10.1 Pre-Rename Verification

- [ ] All Python files have been updated
- [ ] All configuration files have been updated
- [ ] All documentation files have been updated
- [ ] All test files have been updated
- [ ] No remaining references to old folder names in tracked files

### 10.2 Post-Rename Verification

- [ ] Folders have been renamed using `git mv`
- [ ] Git history is preserved for renamed files
- [ ] No broken imports or path references
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Documentation builds successfully (if applicable)
- [ ] No new warnings in IDE/linting

### 10.3 Functionality Verification

- [ ] Sample scripts can access input data from `inputs/`
- [ ] Sample scripts can write to `outputs/`
- [ ] Log files are written to `logs/`
- [ ] Configuration loads correctly with new paths
- [ ] Path resolution works correctly
- [ ] Backward compatibility functions (if kept) work correctly

---

## 11. Rollback Plan

If issues arise after the rename:

1. **Immediate rollback using git:**
   ```bash
   git revert HEAD
   # Or reset to commit before rename
   git reset --hard <commit-before-rename>
   ```

2. **If folders were renamed without git mv:**
   ```bash
   mv inputs inputs
   mv logs logs
   mv outputs outputs
   git restore config/project.yaml
   git restore src/f1d/shared/path_utils.py
   # ... restore other modified files
   ```

3. **Document the rollback** in issue tracker with detailed analysis of what failed

---

## 12. Post-Implementation Tasks

1. **Update any external references**
   - Documentation in other repos
   - External CI/CD configuration
   - Data pipeline documentation

2. **Update version/release notes**
   - Document the breaking change
   - Provide migration guide for users

3. **Clean up deprecated code**
   - Remove or update backward compatibility functions in `path_utils.py`
   - Update deprecation warnings if any remain

4. **Update automated checks**
   - Add linter rule to prevent reintroduction of old folder names
   - Add pre-commit hook to validate path usage

---

## 13. Summary Statistics

| Category | File Count |
|----------|------------|
| Python Scripts | ~78 |
| Configuration Files | 4 |
| Documentation Files | ~80 |
| Test Files | 5+ |
| Planning Archives | ~140 |
| **TOTAL** | **~303** |

| Folder | Old Name | New Name | Files Affected |
|--------|----------|----------|----------------|
| Inputs | `inputs/` | `inputs/` | ~151 files |
| Logs | `logs/` | `logs/` | ~141 files |
| Outputs | `outputs/` | `outputs/` | ~302 files |

---

## 14. Commands for Batch Replacement (Reference)

For use during implementation:

```bash
# Find all Python files with references
find . -name "*.py" -type f | xargs grep -l "inputs\|logs\|outputs"

# Batch replacement using sed (test first!)
# WARNING: Review each file carefully before applying
find . -name "*.py" -type f -exec sed -i 's/"inputs"/"inputs"/g' {} +
find . -name "*.py" -type f -exec sed -i 's/"logs"/"logs"/g' {} +
find . -name "*.py" -type f -exec sed -i 's/"outputs"/"outputs"/g' {} +

# For documentation files
find . -name "*.md" -type f -exec sed -i 's/inputs\/inputs/g' {} +
find . -name "*.md" -type f -exec sed -i 's/logs/logs/g' {} +
find . -name "*.md" -type f -exec sed -i 's/outputs/outputs/g' {} +
```

**IMPORTANT:** Manual review is required for each file due to context-specific requirements (e.g., docstrings, comments, string concatenations).

---

## 15. Approval Required

- [ ] Team Lead: _________________ Date: _______
- [ ] Code Reviewer: _________________ Date: _______
- [ ] Documentation Reviewer: _________________ Date: _______

---

**END OF PLAN**
