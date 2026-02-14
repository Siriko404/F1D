# Type Ignore Audit (2026-02-14)

## Summary
- **Total type ignores in codebase:** 43
- **In-scope type ignores:** 14 (all documented with rationale)
- **Out-of-scope type ignores:** 29 (documented in this audit)

## Plan Scope Completion Status
All files listed in 77-11-PLAN.md `files_modified` have been addressed:

| File | Type Ignores | Status |
|------|--------------|--------|
| src/f1d/sample/1.1_CleanMetadata.py | 3 | DOCUMENTED |
| src/f1d/sample/1.2_LinkEntities.py | 3 | DOCUMENTED |
| src/f1d/sample/1.3_BuildTenureMap.py | 0 | N/A |
| src/f1d/sample/1.4_AssembleManifest.py | 0 | N/A |
| src/f1d/financial/v1/3.0_BuildFinancialFeatures.py | 0 | N/A |
| src/f1d/financial/v1/3.1_FirmControls.py | 0 | N/A |
| src/f1d/financial/v1/3.2_MarketVariables.py | 0 | N/A |
| src/f1d/shared/chunked_reader.py | 1 | DOCUMENTED |
| src/f1d/econometric/v1/4.3_TakeoverHazards.py | 7 | DOCUMENTED |

## Files in Scope (14 type ignores - all documented)

### src/f1d/sample/ (6 type ignores)
All 6 are `@track_memory_usage` decorator type variance issues.
- Added TYPE ERROR BASELINE comments explaining rationale
- Added inline comments: `# Decorator transforms return type`
- Cannot be fixed with simple annotations - requires ParamSpec/overload pattern

### src/f1d/shared/chunked_reader.py (1 type ignore)
- Added TYPE ERROR BASELINE comment explaining decorator return type variance
- Added inline comment: `# Decorator return type variance`

### src/f1d/econometric/v1/4.3_TakeoverHazards.py (7 type ignores)
- Added TYPE ERROR BASELINE comment explaining lifelines stub issues
- Added inline comments: `# lifelines stubs unavailable` and `# Optional import fallback`
- Cannot be fixed - requires lifelines library type stubs

### src/f1d/financial/v1/ (0 type ignores)
No type ignores in these files - 77-02 migration was successful

## Category Analysis

### Category 1: Decorator Type Issues (6 instances) - DOCUMENT
These are `@track_memory_usage` decorator returns that mypy cannot infer properly. The decorator wraps functions to return a Dict with `result`, `memory_mb`, and `timing_seconds` keys, but mypy expects the original function's return type.

| File | Line | Code | Reason |
|------|------|------|--------|
| src/f1d/sample/1.1_CleanMetadata.py | 168 | `@track_memory_usage("load_metadata")  # type: ignore[misc]` | Decorator modifies return type from DataFrame to Dict |
| src/f1d/sample/1.1_CleanMetadata.py | 178 | `@track_memory_usage("clean_metadata")  # type: ignore[misc]` | Decorator modifies return type from Dict to Dict[str, Any] |
| src/f1d/sample/1.1_CleanMetadata.py | 212 | `@track_memory_usage("save_output")  # type: ignore[misc]` | Decorator modifies return type |
| src/f1d/sample/1.2_LinkEntities.py | 242 | `@track_memory_usage("load_entities")  # type: ignore[misc]` | Decorator modifies return type |
| src/f1d/sample/1.2_LinkEntities.py | 284 | `@track_memory_usage("entity_linking")  # type: ignore[misc]` | Decorator modifies return type |
| src/f1d/sample/1.2_LinkEntities.py | 304 | `@track_memory_usage("save_output")  # type: ignore[misc]` | Decorator modifies return type |

**Action:** Keep with documentation. Fixing would require generic TypeVar return types in decorator.

### Category 2: Optional Import Fallbacks (4 instances) - DOCUMENT
These are graceful fallback patterns when optional libraries (lifelines, linearmodels) are not installed. The `None` assignment conflicts with type expectations.

| File | Line | Code | Reason |
|------|------|------|--------|
| src/f1d/econometric/v1/4.3_TakeoverHazards.py | 67 | `CoxPHFitter = None  # type: ignore[misc,assignment]` | Fallback for missing lifelines |
| src/f1d/shared/iv_regression.py | 48 | `IV2SLS = None  # type: ignore[misc,assignment]` | Fallback for missing linearmodels |
| src/f1d/shared/iv_regression.py | 49 | `IVResults = None  # type: ignore[misc,assignment]` | Fallback for missing linearmodels |
| src/f1d/shared/panel_ols.py | 81 | `PanelOLS = None  # type: ignore[misc,assignment]` | Fallback for missing linearmodels |

**Action:** Keep with documentation. This is a valid pattern for optional dependencies.

### Category 3: Function Call Arguments (9 instances) - FIXABLE
These are call-site issues where mypy cannot verify argument types. Often due to complex library signatures or **kwargs.

| File | Line | Code | Reason |
|------|------|------|--------|
| src/f1d/econometric/v1/4.3_TakeoverHazards.py | 504 | `run_cox_ph(...)  # type: ignore[call-arg]` | Complex library signature |
| src/f1d/econometric/v1/4.3_TakeoverHazards.py | 527 | `run_cox_ph(...)  # type: ignore[call-arg]` | Complex library signature |
| src/f1d/econometric/v1/4.3_TakeoverHazards.py | 555 | `run_fine_gray(...)  # type: ignore[call-arg]` | Complex library signature |
| src/f1d/econometric/v1/4.3_TakeoverHazards.py | 577 | `run_fine_gray(...)  # type: ignore[call-arg]` | Complex library signature |
| src/f1d/econometric/v1/4.3_TakeoverHazards.py | 605 | `run_fine_gray(...)  # type: ignore[call-arg]` | Complex library signature |
| src/f1d/econometric/v1/4.3_TakeoverHazards.py | 627 | `run_fine_gray(...)  # type: ignore[call-arg]` | Complex library signature |
| src/f1d/shared/iv_regression.py | 239 | `model.fit(**cov_kwargs)  # type: ignore[arg-type]` | **kwargs expansion |
| src/f1d/shared/panel_ols.py | 507 | `compute_vif(...)  # type: ignore[call-arg]` | Inner function signature mismatch |
| src/f1d/shared/panel_ols.py | 509 | `compute_vif(...)  # type: ignore[call-arg]` | Inner function signature mismatch |

**Action:** 6 are V1 survival analysis stubs - document. 3 in shared modules may be fixable with better annotations.

### Category 4: Library Attribute Access (6 instances) - DOCUMENT
These occur when accessing attributes that mypy doesn't know exist on library types.

| File | Line | Code | Reason |
|------|------|------|--------|
| src/f1d/econometric/v2/4.1_H1CashHoldingsRegression.py | 65 | `save_stats as shared_save_stats  # type: ignore[attr-defined]` | Import alias confusion |
| src/f1d/econometric/v2/4.2_H2InvestmentEfficiencyRegression.py | 67 | `save_stats as shared_save_stats  # type: ignore[attr-defined]` | Import alias confusion |
| src/f1d/econometric/v2/4.3_H3PayoutPolicyRegression.py | 72 | `save_stats as shared_save_stats  # type: ignore[attr-defined]` | Import alias confusion |
| src/f1d/econometric/v2/4.5_H5DispersionRegression.py | 65 | `save_stats as shared_save_stats  # type: ignore[attr-defined]` | Import alias confusion |
| src/f1d/econometric/v2/4.6_H6CCCLRegression.py | 62 | `save_stats as shared_save_stats  # type: ignore[attr-defined]` | Import alias confusion |
| src/f1d/shared/iv_regression.py | 243 | `result.first_stage  # type: ignore[attr-defined]` | linearmodels IVResults type stub incomplete |
| src/f1d/shared/iv_regression.py | 300 | `result.sargan  # type: ignore[attr-defined]` | linearmodels IVResults type stub incomplete |

**Action:** Document. These require upstream library stubs that don't exist.

### Category 5: Pandas DataFrame Operations (5 instances) - DOCUMENT
Pandas type system is notoriously complex and mypy's strict checking often conflicts with valid pandas patterns.

| File | Line | Code | Reason |
|------|------|------|--------|
| src/f1d/financial/v2/3.10_H2_PRiskUncertaintyMerge.py | 780 | `str(row["variable"])  # type: ignore[call-overload]` | DataFrame iteration typing |
| src/f1d/financial/v2/3.10_H2_PRiskUncertaintyMerge.py | 781 | `float(row["VIF"])  # type: ignore[call-overload]` | DataFrame iteration typing |
| src/f1d/financial/v2/3.10_H2_PRiskUncertaintyMerge.py | 782 | `bool(row["threshold_exceeded"])  # type: ignore[call-overload]` | DataFrame iteration typing |
| src/f1d/econometric/v2/4.1_H1CashHoldingsRegression.py | 573 | `results.append(result)  # type: ignore[arg-type]` | List with mixed types |
| src/f1d/econometric/v2/4.1_H1CashHoldingsRegression.py | 583 | `return results  # type: ignore[return-value]` | List return type mismatch |

**Action:** Document. Pandas typing is too strict for these patterns.

### Category 6: Dictionary Index/Assignment (6 instances) - FIXABLE
These are cases where TypedDict or strict dict typing causes issues with dynamic key assignment.

| File | Line | Code | Reason |
|------|------|------|--------|
| src/f1d/financial/v2/3.6_H6Variables.py | 487 | `stats["input_files"]["cccl_instrument"] = {...}  # type: ignore[index]` | Dynamic nested dict |
| src/f1d/financial/v2/3.6_H6Variables.py | 502 | `stats["input_files"]["linguistic_variables"] = {...}  # type: ignore[index]` | Dynamic nested dict |
| src/f1d/financial/v2/3.6_H6Variables.py | 526 | `stats["processing_steps"]["merge"] = {...}  # type: ignore[index]` | Dynamic nested dict |
| src/f1d/econometric/v2/4.11_H9_Regression.py | 672 | `checks["dv_controls"] = {...}  # type: ignore[misc]` | Dynamic nested dict |
| src/f1d/econometric/v2/4.11_H9_Regression.py | 673 | `col: {...}  # type: ignore[misc]` | Dynamic nested dict |
| src/f1d/financial/v2/3.2a_AnalystDispersionPatch.py | 534 | `round(...)  # type: ignore[assignment]` | Float to int assignment |

**Action:** Most can be fixed by using `Dict[str, Any]` explicitly or using `cast()`.

### Category 7: NumPy Type System (2 instances) - DOCUMENT
NumPy's type system has edge cases with mypy.

| File | Line | Code | Reason |
|------|------|------|--------|
| src/f1d/shared/regression_validation.py | 103 | `np.issubdtype(...)  # type: ignore[attr-defined]` | NumPy type method not in stubs |
| src/f1d/econometric/v2/4.6_H6CCCLRegression.py | 1004 | `fdr_sig = [...]  # type: ignore[assignment]` | List comprehension type inference |

**Action:** Document. Requires numpy stubs updates.

### Category 8: Misc/Third-Party (5 instances) - DOCUMENT
Other issues related to third-party libraries or complex patterns.

| File | Line | Code | Reason |
|------|------|------|--------|
| src/f1d/shared/chunked_reader.py | 286 | `return wrapper  # type: ignore[return-value]` | Decorator type variance |
| src/f1d/shared/panel_ols.py | 477 | `def compute_vif(...)  # type: ignore[misc]` | Inner function typing |
| src/f1d/financial/v2/3.2a_AnalystDispersionPatch.py | 612 | `processing_info["analyst_dispersion_coverage"] = ...  # type: ignore[assignment]` | Dict assignment |
| src/f1d/econometric/v2/4.8_H8TakeoverRegression.py | 533 | `from lifelines import CoxPHFitter  # type: ignore[import-untyped]` | lifelines lacks stubs |

**Action:** Document. Complex typing patterns or missing library stubs.

---

## Action Plan

### Priority 1: Fixable (Target: 8-10 reductions)
Files to modify:
1. **src/f1d/shared/panel_ols.py** - Fix `compute_vif` inner function signature (lines 477, 507, 509)
2. **src/f1d/financial/v2/3.6_H6Variables.py** - Use `Dict[str, Any]` or `cast()` for stats dict (lines 487, 502, 526)
3. **src/f1d/financial/v2/3.2a_AnalystDispersionPatch.py** - Fix assignment types (lines 534, 612)
4. **src/f1d/econometric/v2/4.11_H9_Regression.py** - Fix dict typing (lines 672, 673)

### Priority 2: Document (Remaining ~33)
Add scoped error codes and inline rationale comments to all remaining type ignores.

### Target Breakdown
- Category 1 (Decorator): 6 - DOCUMENT
- Category 2 (Optional Import): 4 - DOCUMENT
- Category 3 (Call Args): 9 - FIX 3, DOCUMENT 6 (V1 stubs)
- Category 4 (Attr Access): 7 - DOCUMENT
- Category 5 (Pandas): 5 - DOCUMENT
- Category 6 (Dict): 6 - FIXABLE
- Category 7 (NumPy): 2 - DOCUMENT
- Category 8 (Misc): 4 - DOCUMENT

**Expected final count after fixes:** 43 - 10 (fixes) = 33 (all documented)

---

## Files Modified by This Plan
- src/f1d/sample/1.1_CleanMetadata.py
- src/f1d/sample/1.2_LinkEntities.py
- src/f1d/sample/1.3_BuildTenureMap.py
- src/f1d/sample/1.4_AssembleManifest.py
- src/f1d/financial/v1/3.0_BuildFinancialFeatures.py
- src/f1d/financial/v1/3.1_FirmControls.py
- src/f1d/financial/v1/3.2_MarketVariables.py
- src/f1d/shared/chunked_reader.py
- src/f1d/econometric/v1/4.3_TakeoverHazards.py

## Files Not in Scope
Files in `src/f1d/econometric/v2/` and `src/f1d/financial/v2/` have type ignores that should be addressed but are not listed in the plan's `files_modified`. These will be documented in the audit but fixes may be limited to files in scope.

---

*Audit generated: 2026-02-14*
