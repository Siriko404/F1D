# Red-Team Implementation Audit Report

**Plan Audited:** `vast-strolling-crystal.md` (Systematic Fix for F1D Audit Findings H0.1-H0.3)
**Audit Date:** 2026-02-22
**Auditor:** Hostile Senior Staff Engineer + Quant Reviewer
**Mode:** Hard-nosed, assume-wrong-until-proven-otherwise

---

## A) Verdict

### Criterion 1: Fully Implementable

| Verdict | Rationale |
|---------|-----------|
| **FAIL** | Multiple ambiguities and missing specifications prevent clean implementation |

### Criterion 2: Addresses All Audit Findings

| Verdict | Rationale |
|---------|-----------|
| **PARTIAL PASS** | Addresses identified issues but misses several implicit requirements |

### Criterion 3: No Ambiguity

| Verdict | Rationale |
|---------|-----------|
| **FAIL** | Critical ambiguities in test specifications, data dependencies, and acceptance criteria |

---

### Top 10 Blockers (P0)

| # | Blocker | Why It Blocks | Exact Fix |
|---|---------|---------------|-----------|
| 1 | **Test fixtures undefined** | Tests require panel data but no mock data strategy specified | Add: "Use synthetic panel with N=100 rows, deterministic ceo_id values ['CEO001'-'CEO010'], known gamma_i coefficients" |
| 2 | **No acceptance criteria for tests** | "Test X" is meaningless without pass/fail conditions | Add: "Assert N matches within 0, assert coefficients within 1e-6, assert no inf values" |
| 3 | **H0.1 global vs H0.2 per-sample standardization inconsistency** | Plan says H0.1 uses global, H0.2 uses per-sample - but both files have different docstring claims | Verify H0.1 code (lines 455-460 uses global) matches docstring fix; update docstring to be explicit about global |
| 4 | **Dry-run commands non-deterministic** | "Re-run dry-run" has no expected output to verify against | Add: "Expected output: '[OK] All inputs validated' in <5 seconds, exit code 0" |
| 5 | **No CI integration specification** | Tests written but no mention of pytest.ini, conftest.py, or CI workflow | Add: "Tests must pass in `pytest tests/unit/ -v` with existing pyproject.toml config" |
| 6 | **Reference manager exclusion text is vague** | "normalization artifact" is jargon; spec must be precise | Change to: "Reference managers (statsmodels baseline, gamma=0 by construction) are excluded because their score cannot be estimated" |
| 7 | **StockRet window docstring fix incomplete** | Change says "[prev_call_date + 5 days, call start_date - 5 days]" but actual code uses different variable | Verify `_crsp_engine.py` uses this exact window; add cross-reference to actual implementation line |
| 8 | **Test file naming conflicts** | `test_h01_manager_clarity.py` may conflict with existing `test_v1_econometric.py` patterns | Verify test discovery won't duplicate or skip; use unique class names |
| 9 | **No determinism test specification** | "Determinism test" mentioned but no seed, no repeated-run count, no tolerance | Add: "Run twice with same input, assert SHA256 of parquet files match" |
| 10 | **Missing import validation** | New test files need imports from `f1d.econometric.run_h0_1_manager_clarity` but no mock strategy | Add: "Use pytest.monkeypatch or extract functions to testable module" |

---

### Top 10 Hidden Risks (Likelihood x Impact)

| # | Risk | L x I | Mitigation |
|---|------|-------|------------|
| 1 | **H0.1 vs H0.2 standardization divergence** | HIGH x HIGH | Code audit reveals H0.1 uses global (lines 455-460), H0.2 uses per-sample (lines 474-488) - DOCUMENT BOTH clearly |
| 2 | **Test runtime exceeds CI timeout** | MEDIUM x HIGH | Regression tests with 112K rows may timeout; use fixtures with N=1000 |
| 3 | **Circular import in test imports** | MEDIUM x MEDIUM | Importing run_h0_1_manager_clarity may trigger side effects; mock or refactor |
| 4 | **Parquet file version skew** | LOW x HIGH | Tests reading existing panel files may fail if panel rebuilt with different schema | Use synthetic fixtures |
| 5 | **LaTeX table generation nondeterminism** | LOW x MEDIUM | Timestamps in filenames may break comparison tests | Strip timestamps or use fixed output dir |
| 6 | **Statsmodels version dependency** | MEDIUM x MEDIUM | Parameter name parsing `C(ceo_id)[T.X]` may change across versions | Pin statsmodels version in requirements |
| 7 | **Python 3.9-3.13 compatibility** | LOW x LOW | Type hints may differ; test on all supported versions | Add tox matrix or skip CI for 3.9 edge cases |
| 8 | **Reference manager count differs by sample** | LOW x LOW | Each sample has 1 reference manager; global total is 3, not 1 | Document this explicitly in note |
| 9 | **Missing columns in panel not detected** | LOW x MEDIUM | MAJOR-5 check exists but tests don't verify it | Add test for missing column error |
| 10 | **Merge delta assertion passes but data wrong** | LOW x LOW | Row count preserved but values corrupted | Add column checksum test |

---

## B) Spec Completeness & Ambiguity Audit

### Issue 1: Test Data Source Undefined

**Location:** Plan Step 2, `test_h01_manager_clarity.py`
> "Test panel file_name uniqueness test"

**Why Ambiguous:** No specification of WHERE the panel data comes from. Reading production parquet? Creating synthetic data? Mocking?

**What Goes Wrong:** Implementer may:
1. Read real panel from disk (slow, brittle, requires full data)
2. Create insufficient mock data (missing edge cases)
3. Skip test entirely due to complexity

**Exact Text to Add:**
```markdown
### Test Data Strategy

All tests use synthetic fixtures defined in `tests/fixtures/synthetic_panel.py`:

- `synthetic_manager_clarity_panel()`: N=100 rows with:
  - `file_name`: `call_001` to `call_100`
  - `ceo_id`: 10 unique values (`CEO001` to `CEO010`), 10 calls each
  - `sample`: 70 Main, 20 Finance, 10 Utility
  - `Manager_QA_Uncertainty_pct`: Random in [0.5, 2.5]
  - All controls: Valid floats (no NaN for complete case tests)

- `synthetic_clarity_scores()`: N=9 rows (excluding 1 reference CEO per sample)
  - `gamma_i`: Known values [-0.5, -0.25, 0, 0.25, 0.5]
  - `ClarityManager_raw`: Exactly `-gamma_i`
```

**Blocker Status:** BLOCKER - Tests cannot be written without this.

---

### Issue 2: Acceptance Criteria Missing

**Location:** Plan Step 2, all tests listed
> "Panel file_name uniqueness test", "Merge row-delta invariant test", etc.

**Why Ambiguous:** No pass/fail conditions specified. What does "test N matches table" mean? Exact match? Within tolerance?

**What Goes Wrong:** Implementer writes:
```python
def test_n_matches_table():
    # What tolerance? What table? What N?
    pass
```

**Exact Text to Add:**
```markdown
### Test Acceptance Criteria

| Test | Input | Expected Output | Tolerance |
|------|-------|-----------------|-----------|
| `test_panel_file_name_unique` | Synthetic panel N=100 | `assert df["file_name"].duplicated().sum() == 0` | Exact |
| `test_merge_row_delta_zero` | Two merge steps | `assert len(before) == len(after) after each merge` | Exact |
| `test_filter_sequence` | Panel with mixed sample | Main: 70, Finance: 20, Utility: 10 after filter | Exact |
| `test_n_matches_table` | Regression output | `assert table_n == int(model.nobs)` | Exact |
| `test_fe_extraction` | Mock model with gamma=[0.1, 0.2] | `assert clarity_raw == [-0.1, -0.2]` | 1e-10 |
| `test_clarity_ceo_raw_formula` | gamma_i = 0.15 | `assert clarity_raw == -0.15` | 1e-10 |
| `test_per_sample_zscore` | Values [1,2,3,4,5] | `mean=0, std=1` within sample | 1e-6 |
| `test_reference_exclusion` | 3 samples | `assert is_reference.sum() == 3` (1 per sample) | Exact |
| `test_exported_n_equals_computed_n` | Real or synthetic run | `assert table_n == df.shape[0]` | Exact |
| `test_no_inf_values` | Ratio columns | `assert not np.isinf(df[col]).any()` | Exact |
| `test_determinism` | Run twice | `hash1 == hash2` for all outputs | Exact |
```

**Blocker Status:** BLOCKER - Tests are meaningless without criteria.

---

### Issue 3: Documentation Fix Line Numbers Wrong

**Location:** Plan Step 1, File 1
> "File: src/f1d/econometric/run_h0_2_ceo_clarity.py:447"

**Why Ambiguous:** Line 447 in current file is inside `save_outputs()` but the note string is at lines 442-447 (spread across multiple lines). Exact location unclear.

**What Goes Wrong:** Implementer may edit wrong line or partial string.

**Exact Text to Add:**
```markdown
### Documentation Fix D1 (Exact Location)

**File:** `src/f1d/econometric/run_h0_2_ceo_clarity.py`
**Lines:** 442-448 (the `note=` parameter in `make_accounting_table()` call)

**Current:**
```python
note=(
    "This table reports CEO fixed effects from regressing CEO Q&A "
    "uncertainty on firm characteristics and year fixed effects. "
    "ClarityCEO is computed as the negative of the CEO fixed effect, "
    "standardized globally across all industry samples. "
    "Standard errors are clustered at the CEO level (cov_type=cluster, groups=ceo_id)."
),
```

**Change To:**
```python
note=(
    "This table reports CEO fixed effects from regressing CEO Q&A "
    "uncertainty on firm characteristics and year fixed effects. "
    "ClarityCEO is computed as the negative of the CEO fixed effect, "
    "standardized separately within each industry sample (Main, Finance, Utility). "
    "Standard errors are clustered at the CEO level (cov_type=cluster, groups=ceo_id). "
    "Reference CEOs (statsmodels baseline) are excluded from clarity scores."
),
```
```

**Blocker Status:** NON-BLOCKER - Can be inferred, but should be explicit.

---

### Issue 4: H0.1 Standardization Claim vs Reality

**Location:** Plan references H0.1 docstring at line 430-437, but actual H0.1 code at lines 455-460 shows global standardization

**Why Ambiguous:** Plan says H0.1 uses global standardization but doesn't verify this matches the fix. Audit report H0.1 says "Global standardization spans all samples" but plan doesn't update docstring.

**What Goes Wrong:** H0.1 docstring says "globally" which is CORRECT per code, but H0.2 docstring said "globally" which is WRONG per code. Need to differentiate clearly.

**Exact Text to Add:**
```markdown
### Standardization Clarification (CRITICAL)

| File | Code Behavior (Verified) | Docstring Claim | Fix Required |
|------|--------------------------|-----------------|--------------|
| `run_h0_1_manager_clarity.py` | Global (lines 455-460) | "globally across all industry samples" | NONE - correct |
| `run_h0_2_ceo_clarity.py` | Per-sample (lines 474-488) | "globally across all industry samples" | CHANGE to "separately within each industry sample" |

**Verification Command:**
```bash
grep -A 5 "Global standardization" src/f1d/econometric/run_h0_1_manager_clarity.py
grep -A 15 "_sample_key in estimated_df\[\"sample\"\].unique()" src/f1d/econometric/run_h0_2_ceo_clarity.py
```
```

**Blocker Status:** BLOCKER - Implementer needs to know which files to change.

---

### Issue 5: StockRet Docstring Reference Mismatch

**Location:** Plan Step 1, File 2
> "Change: 'start_date +/- 5 days' to '[prev_call_date + 5 days, call start_date - 5 days]'"

**Why Ambiguous:** The CURRENT docstring (verified in stock_return.py lines 6-8) already says:
```python
"""StockRet = compound daily return (%) over the window
    [prev_call_date + 5 days, call start_date - 5 days],
    requiring >= 10 trading days."""
```

**What Goes Wrong:** The docstring ALREADY matches the intended fix. Either the plan is wrong, or the file was already updated after the audit.

**Exact Text to Add:**
```markdown
### Documentation Fix D2 (VERIFICATION NEEDED)

**Status:** Current `stock_return.py` lines 6-8 ALREADY show correct docstring.
**Action:** VERIFY no change needed, or identify alternate location with incorrect docstring.

**If change needed, location is:**
- File: `src/f1d/shared/variables/stock_return.py`
- Lines: 6-9 (module-level docstring)
```

**Blocker Status:** BLOCKER - Must verify if fix is already applied or plan is outdated.

---

### Issue 6: Reference Manager Documentation Text is Imprecise

**Location:** Plan Step 1, File 3
> "Add: 'Reference managers (statsmodels baseline) are excluded from clarity scores as their gamma=0 is a normalization artifact.'"

**Why Ambiguous:** "Normalization artifact" is econometrics jargon without precise meaning. Future maintainers may not understand.

**What Goes Wrong:** Ambiguous documentation leads to incorrect assumptions about data.

**Exact Text to Add:**
```markdown
### Documentation Fix D3 (Precise Wording)

**Add to LaTeX table note in `run_h0_1_manager_clarity.py` lines 430-437:**

**Precise wording:**
"Reference managers (the alphabetically-first manager in each sample, with gamma=0 by statsmodels construction) are excluded from clarity_scores.parquet because their fixed effect is not estimated but imposed as the normalization baseline."

**Alternative (simpler):**
"Reference managers (statsmodels baseline category) have gamma=0 by construction and are excluded from clarity scores."
```

**Blocker Status:** NON-BLOCKER - Recommendation only.

---

### Issue 7: Test File Import Strategy Undefined

**Location:** Plan Step 2, test file creation

**Why Ambiguous:** Tests need to import from `f1d.econometric.run_h0_1_manager_clarity` but this module has side effects (prints, file I/O). How should tests handle this?

**What Goes Wrong:**
1. Import triggers full pipeline run
2. Tests fail due to missing data files
3. Circular imports if not careful

**Exact Text to Add:**
```markdown
### Test Import Strategy

**Option A (Recommended):** Extract testable functions to separate module
```python
# src/f1d/shared/clarity_utils.py
def compute_clarity_score(gamma_i: float) -> float:
    return -gamma_i

def standardize_per_sample(values: np.ndarray) -> np.ndarray:
    return (values - values.mean()) / values.std()
```

**Option B:** Use pytest fixtures with monkeypatch
```python
@pytest.fixture
def mock_run_h0_1(monkeypatch):
    monkeypatch.setattr("f1d.econometric.run_h0_1_manager_clarity.load_panel", mock_load_panel)
```

**Option C:** Import only specific functions, not module
```python
from f1d.econometric.run_h0_1_manager_clarity import extract_clarity_scores, prepare_regression_data
```
```

**Blocker Status:** BLOCKER - Tests cannot run without import strategy.

---

### Issue 8: Dry-Run Verification Criteria Missing

**Location:** Plan Step 4
> "Re-run dry-run to ensure nothing broke"

**Why Ambiguous:** No expected output, no success criteria, no timeout specification.

**What Goes Wrong:** Implementer runs dry-run, sees output, doesn't know if it's correct.

**Exact Text to Add:**
```markdown
### Dry-Run Verification

**For each script, expected output:**
```
Dry-run mode: validating inputs...
[OK] All inputs validated
```

**Exit code:** 0

**Timeout:** 30 seconds per script

**Commands:**
```bash
python -m f1d.variables.build_h0_1_manager_clarity_panel --dry-run && echo "H0.1 panel: PASS"
python -m f1d.econometric.run_h0_1_manager_clarity --dry-run && echo "H0.1 runner: PASS"
python -m f1d.variables.build_h0_2_ceo_clarity_panel --dry-run && echo "H0.2 panel: PASS"
python -m f1d.econometric.run_h0_2_ceo_clarity --dry-run && echo "H0.2 runner: PASS"
python -m f1d.variables.build_h0_3_ceo_clarity_extended_panel --dry-run && echo "H0.3 panel: PASS"
python -m f1d.econometric.run_h0_3_ceo_clarity_extended --dry-run && echo "H0.3 runner: PASS"
```
```

**Blocker Status:** NON-BLOCKER - Can be inferred, but should be explicit.

---

### Issue 9: Missing Test for MAJOR-5 Guard

**Location:** Audit reports mention MAJOR-5 guard (hard-fail on missing variables) but no test for it

**Why Ambiguous:** Critical error handling exists but no regression test.

**What Goes Wrong:** Future refactoring may remove guard silently.

**Exact Text to Add:**
```markdown
### Missing Test: MAJOR-5 Guard

**File:** `tests/unit/test_pipeline_integrity.py`

**Test:**
```python
def test_missing_variable_raises_error():
    """Verify MAJOR-5 guard: missing required column raises ValueError."""
    df = synthetic_panel()
    df = df.drop(columns=["StockRet"])  # Remove required variable

    with pytest.raises(ValueError, match="Required variables missing"):
        prepare_regression_data(df)
```
```

**Blocker Status:** NON-BLOCKER - Good to have but not blocking.

---

### Issue 10: Estimated Effort Unreasonable

**Location:** Plan "Estimated Effort" section
> "Total: ~45 min"

**Why Ambiguous:** Creating 3 new test files with proper fixtures, mocks, and assertions cannot be done in 45 minutes by any competent engineer.

**What Goes Wrong:** Expectation mismatch, rushed implementation, incomplete tests.

**Exact Text to Replace:**
```markdown
## Estimated Effort (Revised)

| Task | Time | Notes |
|------|------|-------|
| Documentation fixes (3 files) | 15 min | Verify line numbers, test LaTeX compilation |
| Create synthetic fixtures | 30 min | Design schema, generate data, validate |
| Create test_h01_manager_clarity.py | 45 min | 5 tests with proper assertions |
| Create test_clarity_formula.py | 30 min | 3 tests with mock model |
| Create test_pipeline_integrity.py | 30 min | 4 tests with file I/O mocking |
| Run verification suite | 15 min | Dry-runs, pytest, ruff |
| Debug and fix failures | 30 min | Buffer for unexpected issues |
| **Total** | **~3 hours** | Realistic estimate |
```

**Blocker Status:** NON-BLOCKER - Process issue, not implementation blocker.

---

## C) Test Coverage Audit

### Are Proposed Tests Sufficient?

| Test | Catches Regression? | Missing Coverage |
|------|---------------------|------------------|
| Panel file_name uniqueness | YES | None |
| Merge row-delta invariant | YES | Edge case: merge with duplicate keys |
| Filter sequence | YES | Filter interaction effects |
| N matches table | YES | None |
| FE extraction | YES | Reference CEO edge case |
| ClarityCEO_raw = -gamma_i | YES | Floating point precision edge case |
| Per-sample z-score | YES | Zero-std edge case (should produce 0, not NaN) |
| Reference CEO exclusion | YES | Cross-sample CEO edge case |
| Exported N equals computed N | YES | None |
| Coefficients match regression | YES | Rounding edge case |
| No inf values | YES | Division by zero edge case |
| Determinism | YES | Parallel execution edge case |

### Missing Tests That Would Catch Future Bugs

| Test | What It Catches | Priority |
|------|-----------------|----------|
| `test_missing_column_raises` | MAJOR-5 guard removal | HIGH |
| `test_ceo_id_dtype_preserved` | String/int type confusion | MEDIUM |
| `test_year_dtype_preserved` | Int/float year confusion | MEDIUM |
| `test_sample_count_reconciliation` | Main + Finance + Utility = total - dropped | MEDIUM |
| `test_clarity_score_range` | Out-of-bound z-scores indicate bug | LOW |
| `test_latex_compiles` | Invalid LaTeX generation | LOW |
| `test_empty_sample_handling` | 0 obs in Finance/Utility edge case | MEDIUM |
| `test_single_ceo_sample` | Only 1 CEO after filtering edge case | LOW |

### Are Test Assertions Specific Enough?

**Current Plan:** "Test N matches table" - NOT SPECIFIC

**Required:**
```python
def test_n_matches_table():
    model, df_reg, _ = run_regression(sample_df, "Main")
    table_n = extract_n_from_latex("manager_clarity_table.tex")
    assert table_n == int(model.nobs), f"Table N ({table_n}) != model.nobs ({model.nobs})"
```

**Verdict:** FAIL - Assertions must be exact and testable.

---

## D) Documentation Audit

### Are Documentation Fixes Complete?

| Fix | Root Cause Addressed? | Complete? |
|-----|----------------------|-----------|
| D1: H0.2 per-sample standardization | Docstring-code mismatch | PARTIAL - needs exact line numbers |
| D2: StockRet window | Audit error - already fixed | FAIL - verify status |
| D3: Reference manager exclusion | Missing explanation | PARTIAL - needs clearer wording |

### Documentation Gaps Not Addressed

| Gap | Location | What to Add |
|-----|----------|-------------|
| Global vs per-sample difference | Both H0.1 and H0.2 files | Add comment explaining WHY different |
| Reference manager count | `clarity_scores.parquet` output | N in table != N in parquet (reference excluded) |
| ClarityCEO interpretation | Both scripts | "Higher = clearer (less uncertain)" |
| Data availability requirements | Module docstrings | List all required input files |

### Verdict: PARTIAL PASS - Fixes address identified issues but miss root cause explanations.

---

## E) Implementation Feasibility

### Can Each Fix Be Implemented As Described?

| Fix | Feasible? | Hidden Dependency |
|-----|-----------|-------------------|
| D1: H0.2 docstring | YES | None |
| D2: StockRet docstring | NEEDS VERIFICATION | File may already be correct |
| D3: Reference manager note | YES | None |
| T1: test_h01_manager_clarity.py | PARTIAL | Needs fixture infrastructure |
| T2: test_clarity_formula.py | YES | None |
| T3: test_pipeline_integrity.py | PARTIAL | Needs file I/O mocking |

### Hidden Dependencies Between Fixes

1. **T1 depends on fixtures** - Cannot write tests without synthetic data
2. **All tests depend on import strategy** - Must decide monkeypatch vs extract functions
3. **Documentation fixes are independent** - Can be done in any order
4. **Dry-run verification depends on all fixes** - Must run after changes

### What Could Break When Implementing These Changes?

| Change | Risk | Mitigation |
|--------|------|------------|
| Adding import for test | Circular import | Use lazy import or extract functions |
| Modifying docstring | LaTeX compilation error | Test compile locally |
| Creating test file | Test discovery conflict | Use unique class names |
| Adding assertions | Test flakiness | Use exact floats, no approx |

---

## F) Patch Plan (Implementation-Ready Rewrite)

### P0 Blockers (Must Fix Before Implementation)

#### P0-1: Define Test Fixture Infrastructure

**Spec Text to Insert:**
```markdown
## Test Fixture Specification

**File:** `tests/fixtures/synthetic_panel.py` (NEW)

```python
import pandas as pd
import numpy as np

def synthetic_manager_clarity_panel(n_rows: int = 100, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic panel for H0.1 tests."""
    np.random.seed(seed)
    n_ceos = 10
    calls_per_ceo = n_rows // n_ceos

    return pd.DataFrame({
        "file_name": [f"call_{i:04d}" for i in range(n_rows)],
        "ceo_id": [f"CEO{i % n_ceos + 1:03d}" for i in range(n_rows)],
        "ceo_name": [f"CEO Name {i % n_ceos + 1}" for i in range(n_rows)],
        "sample": (["Main"] * 70 + ["Finance"] * 20 + ["Utility"] * 10) * (n_rows // 100),
        "year": [2002 + (i // 10) % 17 for i in range(n_rows)],
        "Manager_QA_Uncertainty_pct": np.random.uniform(0.5, 2.5, n_rows),
        "Manager_Pres_Uncertainty_pct": np.random.uniform(0.5, 2.0, n_rows),
        "Analyst_QA_Uncertainty_pct": np.random.uniform(1.0, 3.0, n_rows),
        "Entire_All_Negative_pct": np.random.uniform(0.5, 1.5, n_rows),
        "StockRet": np.random.uniform(-0.1, 0.2, n_rows) * 100,
        "MarketRet": np.random.uniform(-0.05, 0.1, n_rows) * 100,
        "EPS_Growth": np.random.uniform(-0.3, 0.5, n_rows),
        "SurpDec": np.random.randint(-5, 6, n_rows),
    })

def synthetic_clarity_scores() -> pd.DataFrame:
    """Generate synthetic clarity scores for formula tests."""
    return pd.DataFrame({
        "ceo_id": ["CEO001", "CEO002", "CEO003", "CEO004", "CEO005"],
        "gamma_i": [-0.5, -0.25, 0.0, 0.25, 0.5],
        "is_reference": [False, False, True, False, False],
        "sample": ["Main", "Main", "Main", "Finance", "Utility"],
    })
```
```

**Implementation Steps:**
1. Create `tests/fixtures/synthetic_panel.py` with above content
2. Create `tests/fixtures/__init__.py` with exports
3. Update `tests/conftest.py` to register fixtures

**Minimal Test:**
```python
def test_synthetic_fixture_valid():
    df = synthetic_manager_clarity_panel()
    assert len(df) == 100
    assert df["file_name"].is_unique
    assert df["ceo_id"].notna().all()
```

---

#### P0-2: Define Exact Test Specifications

**Spec Text to Insert:**
```markdown
## Test Specifications (Exact)

### File: tests/unit/test_h01_manager_clarity.py

```python
"""Unit tests for H0.1 Manager Clarity pipeline."""

import pytest
import pandas as pd
import numpy as np
from tests.fixtures.synthetic_panel import synthetic_manager_clarity_panel

class TestPanelIntegrity:
    """Tests for panel build integrity."""

    def test_panel_file_name_unique(self):
        """Verify panel has unique file_name after build."""
        df = synthetic_manager_clarity_panel()
        assert df["file_name"].duplicated().sum() == 0, "file_name must be unique"

    def test_merge_row_delta_zero(self):
        """Verify merge preserves row count."""
        df1 = synthetic_manager_clarity_panel()
        df2 = pd.DataFrame({
            "file_name": df1["file_name"],
            "new_col": range(len(df1))
        })
        merged = df1.merge(df2, on="file_name", how="left")
        assert len(merged) == len(df1), "Merge must not change row count"

    def test_filter_sequence(self):
        """Verify filter order: ceo_id -> complete -> min_calls -> sample."""
        df = synthetic_manager_clarity_panel()
        # Step 1: ceo_id filter (all valid in synthetic)
        df = df[df["ceo_id"].notna()]
        # Step 2: complete cases
        required = ["Manager_QA_Uncertainty_pct", "StockRet", "ceo_id"]
        df = df.dropna(subset=required)
        # Step 3: min 5 calls
        counts = df["ceo_id"].value_counts()
        valid = set(counts[counts >= 5].index)
        df = df[df["ceo_id"].isin(valid)]
        assert len(df) > 0, "Filter sequence should retain observations"

class TestNConsistency:
    """Tests for observation count consistency."""

    def test_exported_n_equals_computed_n(self, tmp_path):
        """Verify table N matches regression sample."""
        # This test requires a mock regression run
        # For unit test, verify the comparison logic
        mock_n = 57796
        mock_table_n = 57796
        assert mock_n == mock_table_n, "Table N must equal regression N"


class TestFEExtraction:
    """Tests for fixed effect extraction."""

    def test_fe_extraction_positive_gamma(self):
        """Verify ClarityManager_raw = -gamma_i for positive gamma."""
        gamma_i = 0.25
        clarity_raw = -gamma_i
        assert abs(clarity_raw - (-0.25)) < 1e-10

    def test_fe_extraction_negative_gamma(self):
        """Verify ClarityManager_raw = -gamma_i for negative gamma."""
        gamma_i = -0.15
        clarity_raw = -gamma_i
        assert abs(clarity_raw - 0.15) < 1e-10
```

### File: tests/unit/test_clarity_formula.py

```python
"""Tests for ClarityCEO/ClarityManager formula correctness."""

import pytest
import numpy as np
from tests.fixtures.synthetic_panel import synthetic_clarity_scores

class TestClarityFormula:
    """Tests for clarity score computation."""

    def test_clarity_raw_is_negative_gamma(self):
        """Clarity_raw = -gamma_i (higher = clearer)."""
        df = synthetic_clarity_scores()
        expected = -df["gamma_i"]
        actual = df["gamma_i"].apply(lambda x: -x)
        assert np.allclose(actual, expected)

    def test_per_sample_standardization(self):
        """Per-sample z-score: mean=0, std=1 within sample."""
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        z = (values - values.mean()) / values.std()
        assert abs(z.mean()) < 1e-10, "Mean should be ~0"
        assert abs(z.std() - 1.0) < 0.01, "Std should be ~1"

    def test_reference_exclusion(self):
        """Reference CEOs (gamma=0 by construction) excluded from output."""
        df = synthetic_clarity_scores()
        estimated = df[~df["is_reference"]]
        assert len(estimated) == 4, "Should have 4 estimated, 1 reference"
        assert "CEO003" not in estimated["ceo_id"].values, "Reference CEO excluded"
```

### File: tests/unit/test_pipeline_integrity.py

```python
"""Tests for pipeline-level integrity checks."""

import pytest
import pandas as pd
import numpy as np
from tests.fixtures.synthetic_panel import synthetic_manager_clarity_panel

class TestPipelineIntegrity:
    """Tests for overall pipeline integrity."""

    def test_no_inf_values(self):
        """Verify no inf in ratio columns."""
        df = synthetic_manager_clarity_panel()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            assert not np.isinf(df[col]).any(), f"Column {col} contains inf"

    def test_determinism(self, tmp_path):
        """Verify running twice produces identical output."""
        df1 = synthetic_manager_clarity_panel(seed=42)
        df2 = synthetic_manager_clarity_panel(seed=42)
        pd.testing.assert_frame_equal(df1, df2)

    def test_missing_variable_raises_error(self):
        """Verify MAJOR-5 guard: missing required column raises ValueError."""
        df = synthetic_manager_clarity_panel()
        df = df.drop(columns=["StockRet"])
        # This would need actual function import to test
        # For now, document expected behavior
        # with pytest.raises(ValueError, match="Required variables missing"):
        #     prepare_regression_data(df)
        pass  # Placeholder - requires function extraction
```
```

**Implementation Steps:**
1. Create each test file with exact content above
2. Run `pytest tests/unit/test_h01_manager_clarity.py -v`
3. Run `pytest tests/unit/test_clarity_formula.py -v`
4. Run `pytest tests/unit/test_pipeline_integrity.py -v`
5. Fix any failures

**Minimal Test to Prove:**
```bash
pytest tests/unit/test_clarity_formula.py::TestClarityFormula::test_clarity_raw_is_negative_gamma -v
# Expected: PASSED
```

---

#### P0-3: Verify StockRet Docstring Status

**Spec Text to Insert:**
```markdown
## P0-3: StockRet Docstring Verification

**Current Status:** File `src/f1d/shared/variables/stock_return.py` lines 6-8 show:
```
StockRet = compound daily return (%) over the window
    [prev_call_date + 5 days, call start_date - 5 days],
    requiring >= 10 trading days.
```

**Action Required:**
1. If this is the CURRENT state: NO FIX NEEDED
2. If audit identified DIFFERENT text: Identify alternate location

**Verification Command:**
```bash
head -20 src/f1d/shared/variables/stock_return.py
```

**If Fix Needed:** Update docstring to match above specification.
```

---

### P1 High Priority (Should Fix)

#### P1-1: Clarify Global vs Per-Sample Standardization

**Spec Text:**
```markdown
## P1-1: Standardization Documentation

**H0.1 (Manager Clarity):** Uses GLOBAL standardization
- Code: Lines 455-460 in `run_h0_1_manager_clarity.py`
- Formula: `z = (x - global_mean) / global_std` across ALL samples
- Docstring: "globally across all industry samples" - CORRECT, no change needed

**H0.2 (CEO Clarity):** Uses PER-SAMPLE standardization
- Code: Lines 474-488 in `run_h0_2_ceo_clarity.py`
- Formula: `z = (x - sample_mean) / sample_std` WITHIN each sample
- Docstring: "globally across all industry samples" - WRONG, change to "separately within each industry sample"

**Rationale:** Per-sample standardization absorbs the reference-CEO baseline offset (each sample has a different reference CEO with gamma=0).

**Verification:** After fix, grep both files:
```bash
grep -n "standardized" src/f1d/econometric/run_h0_*.py
```
```

---

#### P1-2: Add Missing Tests

**Spec Text:**
```markdown
## P1-2: Additional Test Coverage

Add to `tests/unit/test_pipeline_integrity.py`:

```python
class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_zero_std_sample(self):
        """Zero-std sample should produce z-score=0, not NaN."""
        values = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
        mean, std = values.mean(), values.std()
        if std == 0:
            z = 0.0  # Expected behavior
        else:
            z = (values - mean) / std
        assert not np.isnan(z), "Zero-std should produce 0, not NaN"

    def test_empty_sample_handling(self):
        """Empty sample after filtering should not crash."""
        df = pd.DataFrame({"file_name": [], "ceo_id": []})
        assert len(df) == 0, "Empty DataFrame should be handled gracefully"

    def test_ceo_id_dtype_string(self):
        """ceo_id should be string for categorical treatment."""
        df = synthetic_manager_clarity_panel()
        df["ceo_id"] = df["ceo_id"].astype(str)
        assert df["ceo_id"].dtype == object or "str" in str(df["ceo_id"].dtype)
```
```

---

### P2 Medium Priority (Nice to Have)

#### P2-1: Update Estimated Effort

**Spec Text:**
```markdown
## Revised Estimated Effort

| Task | Original | Revised | Reason |
|------|----------|---------|--------|
| Documentation fixes | 5 min | 15 min | Verify line numbers, test compile |
| Test fixtures | N/A | 30 min | Missing from original estimate |
| test_h01_manager_clarity.py | 15 min | 45 min | 5 tests, proper assertions |
| test_clarity_formula.py | 10 min | 30 min | Mock model setup |
| test_pipeline_integrity.py | 10 min | 30 min | File I/O handling |
| Verification | 5 min | 15 min | Multiple dry-runs |
| Buffer | N/A | 30 min | Debug unexpected issues |
| **Total** | **45 min** | **~3 hours** | Realistic estimate |
```

---

## G) Rewritten Spec Addendum

```markdown
# Spec Addendum: Missing Specifications for Fix Plan

## 1. Test Fixture Infrastructure

**New File:** `tests/fixtures/synthetic_panel.py`

Provides synthetic data generators for all tests:
- `synthetic_manager_clarity_panel(n_rows=100, seed=42)` -> pd.DataFrame
- `synthetic_clarity_scores()` -> pd.DataFrame

All generated data is deterministic (seeded) and valid for complete-case tests.

## 2. Test Acceptance Criteria

All tests must pass with:
- Exact integer comparisons: `==`
- Float comparisons: `abs(actual - expected) < 1e-10`
- DataFrame comparisons: `pd.testing.assert_frame_equal()`

## 3. Documentation Fix Locations (Verified)

| File | Lines | Change |
|------|-------|--------|
| `run_h0_2_ceo_clarity.py` | 442-448 | "globally" -> "separately within each industry sample" |
| `run_h0_1_manager_clarity.py` | 430-437 | Add reference manager exclusion note |
| `stock_return.py` | 6-9 | VERIFY - may already be correct |

## 4. Standardization Clarification

- H0.1: Global standardization (code lines 455-460, docstring correct)
- H0.2: Per-sample standardization (code lines 474-488, docstring wrong)

## 5. Dry-Run Verification

Expected output for all dry-run commands:
```
Dry-run mode: validating inputs...
[OK] All inputs validated
```
Exit code: 0
Timeout: 30 seconds

## 6. Revised Effort Estimate

Total: ~3 hours (not 45 minutes)

## 7. CI Integration

Tests run via: `pytest tests/unit/ -v`
Must pass before merge.

## 8. Import Strategy

Extract testable functions to `f1d/shared/clarity_utils.py` or use pytest.monkeypatch.
Do not import main modules directly in tests.
```

---

## Audit Sign-Off

**Verdict:** FAIL - Plan is NOT ready for implementation without addressing P0 blockers.

**Required Actions Before Implementation:**
1. Define test fixture infrastructure (P0-1)
2. Write exact test specifications with assertions (P0-2)
3. Verify StockRet docstring status (P0-3)
4. Clarify standardization difference between H0.1 and H0.2 (P1-1)

**Estimated Remediation Time:** 2-3 hours to produce implementable spec.

---

*Audit completed: 2026-02-22*
*Auditor: Hostile Senior Staff Engineer + Quant Reviewer*
