# Type Error Baseline Summary

**Generated:** 2026-02-11
**Purpose:** Document mypy type errors across shared modules for progressive type adoption strategy

---

## Error Summary by Module

| Module | Errors | Primary Issues |
|--------|---------|----------------|
| `data_validation.py` | 4 | Collection type issues, attribute errors |
| `industry_utils.py` | 1 | Return value type mismatch |
| `observability/memory.py` | 2 | Missing psutil type stubs |
| `observability/anomalies.py` | 1 | Missing pandas type stubs |
| `observability/centering.py` | 1 | Missing pandas type stubs |
| `observability/stats.py` | 47 | Dict type mismatches (nested dict structures), unannotated vars |
| **Total** | **56** | Across 7 files |

---

## Error Categories

| Category | Count | Description |
|----------|---------|-------------|
| `import-untyped` | 4 | Missing type stubs for pandas, psutil |
| `attr-defined` | 2 | Collection[str] missing .items() method |
| `dict-item` | 29 | Nested dict entries with incompatible value types |
| `return-value` | 1 | Function return type doesn't match annotation |
| `assignment` | 13 | Type mismatches in assignments |
| `var-annotated` | 7 | Missing type annotations for variables |

---

## Type Stub Files Created

The following stub files were created in Phase 63-05 to resolve `import-untyped` errors for linearmodels:

- `2_Scripts/stubs/linearmodels.pyi` - Package stub
- `2_Scripts/stubs/linearmodels.panel.pyi` - PanelOLS, PanelOLSResults, FStatistic
- `2_Scripts/stubs/linearmodels.iv.pyi` - IV2SLS, IV2SLSResults, FirstStageResults

These stubs resolve linearmodels import errors but do NOT address the pandas/psutil stub issues.

---

## Next Steps for Type Adoption

1. **Add pandas type stubs**: `pip install types-pandas` or create custom stubs
2. **Add psutil type stubs**: `pip install types-psutil`
3. **Fix stats.py dict types**: Major source of type errors (47/56)
4. **Enable stricter checking gradually**: As errors are resolved, tighten mypy configuration

---

## Notes

- **Baseline established**: 56 type errors across 7 files (down from 164 in original report)
- **Reduction**: 108 errors resolved by adding type hints to Tier 1 modules
- **Coverage focus**: financial_utils.py, panel_ols.py, iv_regression.py now have type hints
