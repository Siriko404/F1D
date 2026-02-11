# Pitfalls: v3.0 Codebase Cleanup & Optimization

**Domain:** Scientific Computing Codebase Cleanup
**Researched:** 2026-02-10
**Focus:** Preserving reproducibility during refactoring

## Executive Summary

The biggest risk in cleanup milestones is **accidentally changing results**. For scientific research, this is catastrophic - it invalidates all prior analysis. This document catalogs pitfalls specific to refactoring academic research codebases.

---

## Critical Pitfalls

Mistakes that compromise scientific validity or cause reproducibility failures.

---

### Pitfall 1: Silent Behavioral Changes During Refactoring

**What goes wrong:** Code is reorganized "cosmetically" but subtle behavior changes cause different results. Common culprits:
- Changing iteration order (dicts, sets are unordered pre-Python 3.7)
- Modifying how NaN/None are handled
- Altering sorting behavior
- Changing random number generation

**Why it happens:** Refactoring feels "safe" because no logic changes, but implementation details matter for bitwise reproducibility.

**Warning signs:**
- Regression outputs differ at 3rd+ decimal place
- Sample sizes change slightly (±1-5 observations)
- "It's just a refactor, results should be the same" assumption

**Prevention:**
```python
# Before refactoring: CAPTURE BASELINE
baseline_output = run_script_and_capture_output()
baseline_checksum = compute_file_checksum(baseline_output)

# After refactoring: VERIFY IDENTICAL
new_output = run_script_and_capture_output()
new_checksum = compute_file_checksum(new_output)

assert baseline_checksum == new_checksum, "Refactoring changed outputs!"
```

**Phase to address:** All refactoring phases - verify bitwise identical outputs

---

### Pitfall 2: Breaking Import Paths During Module Split

**What goes wrong:** Splitting `observability_utils.py` into submodules breaks imports across 61 scripts. Scripts fail at runtime with ImportError.

**Why it happens:**
- Incomplete import path updates
- Circular imports introduced
- Relative vs absolute import confusion
- Missing `__init__.py` files

**Warning signs:**
```python
# Broken imports after split:
from shared.observability_utils import DualWriter  # Old path, may fail
from shared.observability.logging import DualWriter  # New path
```

**Prevention:**
```python
# 1. Re-export in __init__.py for backward compatibility
# shared/observability/__init__.py
from .logging import DualWriter
from .stats import print_stat, analyze_missing_values
# ... etc

# 2. Support both old and new imports during transition
# Old: from shared.observability_utils import X
# New: from shared.observability import X

# 3. Add deprecation warnings for old imports
import warnings
if 'observability_utils' in str(__name__):
    warnings.warn(
        "Direct import from observability_utils is deprecated. "
        "Use: from shared.observability import X",
        DeprecationWarning,
        stacklevel=2
    )
```

**Phase to address:** Utility module refactoring

---

### Pitfall 3: Losing Timestamp-Based Output Resolution

**What goes wrong:** Refactoring changes how output directories are created or resolved. `get_latest_output_dir()` can't find the right outputs, causing wrong data merges.

**Why it happens:**
- Timestamp format changes
- Directory structure changes
- Symlink assumptions (already removed in Phase 27)
- Hardcoded paths introduced

**Warning signs:**
- "Required output from Step X.Y not found" errors
- Wrong timestamp in output paths
- Scripts merge stale data instead of fresh outputs

**Prevention:**
```python
# Test timestamp resolution after refactoring
def test_get_latest_output_dir():
    """Verify get_latest_output_dir works after refactor."""
    latest = get_latest_output_dir("4.1_CeoClarity")
    assert latest.exists(), f"Latest directory not found: {latest}"
    assert (latest / "ceo_clarity_scores.parquet").exists()
```

**Phase to address:** All phases that touch path handling

---

### Pitfall 4: Performance Optimizations That Change Results

**What goes wrong:** Vectorization or algorithm changes produce numerically different results. Even if "mathematically equivalent," floating-point operations differ.

**Why it happens:**
- `.apply(lambda)` replaced with vectorized operations
- Summation order changes (parallel vs sequential)
- Different NaN handling
- Type conversions (float32 vs float64)

**Warning signs:**
- Coefficients differ at 5th+ decimal place
- Different observations dropped due to NaN handling
- R² changes slightly

**Prevention:**
```python
# Test: Before and after must be bitwise identical
import numpy as np

def test_vectorization_preserves_results():
    """Verify vectorized version produces identical results."""
    # Original version
    original = df.apply(lambda x: complex_calculation(x))

    # Vectorized version
    vectorized = vectorized_complex_calculation(df)

    # Bitwise comparison
    np.testing.assert_array_equal(
        original.values,
        vectorized.values,
        err_msg="Vectorization changed results!"
    )
```

**Phase to address:** Performance optimization phase

---

## Moderate Pitfalls

Mistakes that cause delays or require rework but don't compromise validity.

---

### Pitfall 5: Incomplete Variable Documentation

**What goes wrong:** Variable catalog missing variables or has incorrect formulas. Reviewers can't trace how numbers were computed.

**Why it happens:**
- Too many variables to catalog (1,785 text measure variables)
- Formulas scattered across scripts
- Variables added during cleanup not documented
- Out-of-date documentation

**Warning signs:**
- Variables in output not in catalog
- Catalog says formula is X but code does Y
- Missing source references (Compustat field names)

**Prevention:**
```python
# Generate catalog programmatically where possible
def generate_variable_catalog():
    """Scan all scripts and extract variable definitions."""
    catalog = {}
    for script in all_scripts:
        vars = extract_variables_from_script(script)
        catalog.update(vars)

    # Write to markdown
    write_variable_catalog(catalog)
```

**Phase to address:** Documentation phase

---

### Pitfall 6: Directory READMEs Don't Match Reality

**What goes wrong:** README says "V2 is for H1-H8" but scripts don't match, or vice versa. Creates confusion about which scripts to use.

**Why it happens:**
- README written from memory without verification
- Scripts moved/renamed without updating docs
- V1/V2/V3 boundaries unclear

**Warning signs:**
- README lists scripts that don't exist
- README omits scripts that do exist
- Purpose description conflicts with actual script behavior

**Prevention:**
```bash
# Verify README accuracy automatically
grep -o "Step.*\.py" README.md | while read script; do
    if [ ! -f "$script" ]; then
        echo "WARNING: $script in README but not found"
    fi
done
```

**Phase to address:** Documentation phase

---

### Pitfall 7: Archive Contains Active Code

**What goes wrong:** `.___archive/` contains scripts that are still referenced, or active scripts are archived by mistake.

**Why it happens:**
- Over-aggressive archiving
- No verification that archived files are unused
- Archive structure unclear

**Warning signs:**
- Import errors after archival
- Missing scripts that should exist
- "Where did script X go?"

**Prevention:**
```python
# Before archiving: check for references
def safe_to_archive(filepath):
    """Check if file is referenced by any active script."""
    filename = Path(filepath).name

    # Search all active scripts for imports/references
    for script in active_scripts():
        content = script.read_text()
        if filename in content:
            return False  # Still referenced

    return True  # Safe to archive
```

**Phase to address:** Archive creation phase

---

## Minor Pitfalls

Mistakes that cause annoyance but are quickly fixable.

---

### Pitfall 8: Ruff Configuration Too Strict

**What goes wrong:** Ruff lints fail on hundreds of issues that don't matter. Developer ignores all linter output.

**Why it happens:**
- Default rules too aggressive
- Academic code has different style than production software
- Legacy code has accumulated issues

**Prevention:**
```toml
# Start permissive, tighten gradually
[tool.ruff.lint]
select = ["E", "W", "F"]  # Errors, warnings, flakes only
# Add more rules incrementally
```

---

### Pitfall 9: MyPy Too Strict on Legacy Code

**What goes wrong:** Mypy fails on thousands of type errors in legacy code. Type hints are added incrementally, but config requires 100% coverage.

**Prevention:**
```toml
# Allow incremental typing
[tool.mypy]
python_version = "3.8"
warn_return_any = false
warn_unused_configs = false
disallow_untyped_defs = false  # Enable later
```

---

### Pitfall 10: Documentation Becomes Stale Immediately

**What goes wrong:** README written, code changes, docs not updated.

**Prevention:**
- Add documentation checks to pre-commit (if using)
- Keep docs close to code (docstrings > separate docs)
- Update README during code review, not as separate task

---

## Phase-Specific Warnings

| Phase | Likely Pitfall | Mitigation |
|-------|---------------|------------|
| Bug fixes | Silent behavioral changes | Verify bitwise identical outputs |
| Utility split | Broken import paths | Re-exports in __init__.py |
| Archive creation | Active code archived | Check for references before moving |
| Documentation | Out-of-date docs | Verify docs match code |
| Performance | Results change | Bitwise comparison tests |

---

## Pre-Submission Checklist

Before concluding v3.0 cleanup:

### Reproducibility
- [ ] All regression outputs bitwise identical to pre-cleanup
- [ ] All 61 scripts run successfully
- [ ] No broken imports
- [ ] Timestamp resolution works

### Code Quality
- [ ] Ruff passes on all files
- [ ] Mypy passes on shared utilities
- [ ] Dead code identified (vulture)

### Documentation
- [ ] README.md accurate and comprehensive
- [ ] Directory READMEs for all major folders
- [ ] Script docstrings on all files
- [ ] Variable catalog complete

### Testing
- [ ] All existing tests pass
- [ ] H7-H8 regression test added and passes
- [ ] Coverage measured (even if not 70% yet)

---

## Sources

| Source | Type | Confidence |
|--------|------|------------|
| Existing codebase analysis | Direct | HIGH |
| Scientific computing best practices | Literature | MEDIUM |
| Refactoring patterns | Industry | MEDIUM |

---

*Pitfalls research: 2026-02-10*
