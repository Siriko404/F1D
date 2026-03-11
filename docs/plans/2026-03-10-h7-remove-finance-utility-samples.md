# H7 Remove Finance and Utility Samples — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove Finance and Utility industry samples from the H7 Illiquidity pipeline, maintaining only the Main sample.

**Architecture:** Modify only the Stage 4 regression script (`run_h7_illiquidity.py`) to loop over Main sample only. The Stage 3 panel builder (`build_h7_illiquidity_panel.py`) will continue to assign sample labels for data provenance, but regressions will run only on Main. Update provenance documentation to reflect the change.

**Tech Stack:** Python, pandas, linearmodels, pytest

---

## Red Team Audit Status

**Verdict: APPROVED WITH CHANGES** (0 critical, 5 minor issues)

All core claims verified manually:
- ✅ CONFIG["samples"] is the ONLY iteration control point (line 88, 474)
- ✅ No downstream dependencies on H7 outputs
- ✅ Tests have no sample-specific assertions
- ✅ LaTeX table already hardcoded to Main (get_res defaults sample="Main")
- ✅ Panel builder only labels rows, doesn't filter

---

## Files Affected

| File | Change Type | Notes |
|------|-------------|-------|
| `src/f1d/econometric/run_h7_illiquidity.py` | Modify | Lines 88, 450, 29-46 |
| `docs/provenance/H7.md` | Modify | Lines 5, 79, 126, 128, 223-224, 291, 295-298, 356-363, 392, 394, 407, 409 |
| `tests/unit/test_h7_regression.py` | Review only | No changes needed |

---

## Task 1: Modify CONFIG in run_h7_illiquidity.py

**File:** `src/f1d/econometric/run_h7_illiquidity.py:88`

Change from:
```python
    "samples": ["Main", "Finance", "Utility"],
```
To:
```python
    "samples": ["Main"],
```

**Commit:**
```bash
git add src/f1d/econometric/run_h7_illiquidity.py
git commit -m "refactor(h7): remove Finance and Utility samples, keep Main only

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Update summary statistics sample_names

**File:** `src/f1d/econometric/run_h7_illiquidity.py:450`

Change from:
```python
        sample_names=["Main", "Finance", "Utility"],
```
To:
```python
        sample_names=["Main"],
```

**Commit:**
```bash
git add src/f1d/econometric/run_h7_illiquidity.py
git commit -m "refactor(h7): generate summary stats for Main sample only

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Update docstring in run_h7_illiquidity.py

**File:** `src/f1d/econometric/run_h7_illiquidity.py:29-46`

**3a. Update Industry Samples section (lines 29-32):**

Change from:
```
Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8
```

To:
```
Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)

Note: Finance (FF12 code 11) and Utility (FF12 code 8) samples are excluded
from this analysis. The panel still contains these observations for data
provenance purposes, but regressions are run only on the Main sample.
```

**3b. Update Outputs section (line 42):**

Change from:
```
    - outputs/econometric/h7_illiquidity/{timestamp}/regression_{sample}_{spec}.txt
```
To:
```
    - outputs/econometric/h7_illiquidity/{timestamp}/regression_Main_{spec}.txt
```

**Commit:**
```bash
git add src/f1d/econometric/run_h7_illiquidity.py
git commit -m "docs(h7): update docstring to reflect Main-only analysis

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: Update provenance documentation (H7.md)

**File:** `docs/provenance/H7.md`

### 4a. Update "Last Verified" date (line 5)
Update date to implementation date.

### 4b. Update Sample Filters (line 79)
Change from:
```
- Industry samples: Main (FF12 1-7,9-10,12), Finance (FF12 11), Utility (FF12 8)
```
To:
```
- Industry sample: Main only (FF12 1-7, 9-10, 12)
- Finance (FF12 11) and Utility (FF12 8) samples are excluded from this analysis
```

### 4c. Update Expected Outputs (line 126)
Change from:
```
| `regression_{sample}_{spec}.txt` | ... | 14 regression outputs (6 Main + 4 Finance + 4 Utility) |
```
To:
```
| `regression_Main_{spec}.txt` | ... | 6 regression outputs (Main sample only) |
```

### 4d. Update model_diagnostics description (line 128)
Change from:
```
| `model_diagnostics.csv` | ... | Summary of all 14 regressions |
```
To:
```
| `model_diagnostics.csv` | ... | Summary of all 6 regressions |
```

### 4e. Update Industry Sample Assignment table (lines 223-224)
Add note to Finance and Utility rows:
```
| Finance | 11 | 20,482 | 18.1% | (excluded from regression) |
| Utility | 8 | 4,281 | 3.8% | (excluded from regression) |
```

### 4f. Update Estimation Spec Register header (line 291)
Change from:
```
**Total: 14 specifications (6 Main + 4 Finance + 4 Utility)**
```
To:
```
**Total: 6 specifications (Main sample only)**
```

### 4g. Update Spec Register table Sample column (lines 295-298)
Change from `Main / Finance / Utility` to `Main` for all A specs.

### 4h. Remove Finance/Utility rows from Regression Diagnostics (lines 356-363)
DELETE lines 356-363 (Finance A1-A4 and Utility A1-A4 rows).

### 4i. Update Known Issues section (lines 392, 394)
- **Line 392**: REMOVE "Utility Sample Small" row (no longer relevant)
- **Line 394**: Change "Cannot test residuals in Finance/Utility" to "N/A (Finance/Utility not analyzed)"

### 4j. Update Summary section (lines 407, 409)
**Line 407:** Change from:
```
**Total Regressions:** 14 (6 Main + 4 Finance + 4 Utility)
```
To:
```
**Total Regressions:** 6 (Main sample only)
```

**Line 409:** REMOVE the Utility significance sentence:
```
Only A1 in Utility sample is significant at 5% (one-tailed) with β = 0.00009 (SE = 0.00005), though this finding should be interpreted with caution due to small sample size (N = 2,306 observations across 72 firms).
```

**Commit:**
```bash
git add docs/provenance/H7.md
git commit -m "docs(h7): update provenance to reflect Main-only analysis

- Remove Finance and Utility regression specs
- Update expected outputs count from 14 to 6
- Clarify that panel still contains all samples for provenance
- Remove obsolete Known Issues about Utility sample

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: Run tests and verify imports

**Step 1: Run H7 regression tests**
```bash
pytest tests/unit/test_h7_regression.py -v
```
Expected: All tests pass (verified: no sample-specific assertions).

**Step 2: Verify module imports correctly**
```bash
python -c "from f1d.econometric.run_h7_illiquidity import main, CONFIG, SPECS; print('samples:', CONFIG['samples']); print('specs:', [s[0] for s in SPECS])"
```
Expected output:
```
samples: ['Main']
specs: ['A1', 'A2', 'A3', 'A4', 'B1', 'B2']
```

---

## Task 6: Run H7 pipeline and verify output count

**Step 1: Run the H7 regression script**
```bash
python -m f1d.econometric.run_h7_illiquidity
```

**Step 2: Verify exactly 6 regression files are produced**
```bash
python -c "
from pathlib import Path
from f1d.shared.path_utils import get_latest_output_dir

root = Path('.')
out_dir = get_latest_output_dir(
    root / 'outputs' / 'econometric' / 'h7_illiquidity',
    required_file='model_diagnostics.csv',
)
txt_files = list(out_dir.glob('regression_*.txt'))
print(f'Regression files: {len(txt_files)} (expected: 6)')
for f in sorted(txt_files):
    print(f'  - {f.name}')

import pandas as pd
diag = pd.read_csv(out_dir / 'model_diagnostics.csv')
print(f'Diagnostics rows: {len(diag)} (expected: 6)')
"
```

Expected output:
```
Regression files: 6 (expected: 6)
  - regression_Main_A1.txt
  - regression_Main_A2.txt
  - regression_Main_A3.txt
  - regression_Main_A4.txt
  - regression_Main_B1.txt
  - regression_Main_B2.txt
Diagnostics rows: 6 (expected: 6)
```

---

## Summary of Changes

| Component | Before | After |
|-----------|--------|-------|
| `CONFIG["samples"]` (line 88) | `["Main", "Finance", "Utility"]` | `["Main"]` |
| `sample_names` (line 450) | `["Main", "Finance", "Utility"]` | `["Main"]` |
| Regression count | 14 (6+4+4) | 6 (Main only) |
| Summary stats columns | 3 samples | 1 sample (Main) |
| Panel builder | Unchanged | Unchanged |
| Tests | No change | No change needed |

---

## Safety Guarantees (Red Team Verified)

1. **Panel builder unchanged**: `build_h7_illiquidity_panel.py` only calls `assign_industry_sample()` which labels rows but doesn't filter.

2. **Only iteration point**: Line 474 `for sample in CONFIG["samples"]:` is the single control point. No hardcoded sample lists elsewhere.

3. **B specs unaffected**: `MAIN_ONLY_SPECS = {"B1", "B2"}` at line 114 already handles Main-only.

4. **LaTeX table already Main-only**: `get_res()` at line 262 defaults `sample="Main"`.

5. **No downstream dependencies**: No other scripts import from or consume H7 outputs.

6. **Tests have no sample assertions**: `test_h7_regression.py` verified to have no Finance/Utility references.

7. **Easy to revert**: Restore `["Main", "Finance", "Utility"]` in CONFIG to revert.

---

## Execution Checklist

- [ ] Task 1: Modify CONFIG["samples"] (line 88)
- [ ] Task 2: Update sample_names (line 450)
- [ ] Task 3: Update docstring (lines 29-46)
- [ ] Task 4: Update provenance documentation (all 10 sub-steps)
- [ ] Task 5: Run tests and verify imports
- [ ] Task 6: Run pipeline and verify exactly 6 regression outputs
