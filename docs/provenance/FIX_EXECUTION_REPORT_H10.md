# Fix Execution Report: Suite H10

**Date:** 2026-03-02
**Executor:** Claude GLM-5 (AI Model)
**Input Document:** AUDIT_REVERIFICATION_H10.md
**Target Files Modified:**
- `src/f1d/econometric/run_h10_tone_at_top.py`
- `docs/provenance/H10.md`

---

## Executive Summary

| Issues Fixed | Issues Unfixable | Issues Skipped |
|--------------|------------------|----------------|
| 5 | 0 | 1 |

### Files Modified
- `C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\src\f1d\econometric\run_h10_tone_at_top.py`
- `C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\provenance\H10.md`

### Rerun Required
- [ ] Stage 3
- [x] Stage 4
- [ ] None (documentation only)

**Note:** Stage 4 rerun is REQUIRED to apply the sample filter fix (H10-001) and deduplication fix (H10-003).

---

## Issue Fix Details

### H10-001: Sample Filter Bug

**Status Before Fix:** NOT FIXED (BLOCKER)

**Target File:** `src/f1d/econometric/run_h10_tone_at_top.py`
**Target Lines:** 1168-1177

#### Before State
```python
# Lines 1168-1177 (original)
        call_sub = (
            call_panel
            if sample == "Main"
            else call_panel[call_panel["sample"] == sample]
        )
        turns_sub = (
            turns_panel
            if sample == "Main"
            else turns_panel[turns_panel["sample"] == sample]
        )
```

#### Planned Change
```
old_string: |
        call_sub = (
            call_panel
            if sample == "Main"
            else call_panel[call_panel["sample"] == sample]
        )
        turns_sub = (
            turns_panel
            if sample == "Main"
            else turns_panel[turns_panel["sample"] == sample]
        )

new_string: |
        call_sub = call_panel[call_panel["sample"] == sample].copy()
        turns_sub = turns_panel[turns_panel["sample"] == sample].copy()
```

#### After State
```python
# Lines 1174-1175 (after fix)
        call_sub = call_panel[call_panel["sample"] == sample].copy()
        turns_sub = turns_panel[turns_panel["sample"] == sample].copy()
```

#### Verification
- [x] Edit was applied successfully
- [x] Sample filter now correctly filters "Main" to Main-only
- [x] No unintended changes made

**Verdict:** FIXED

---

### H10-003: Duplicate Entity-Time Index

**Status Before Fix:** NOT FIXED (MAJOR)

**Target File:** `src/f1d/econometric/run_h10_tone_at_top.py`
**Target Lines:** 132-135

#### Before State
```python
# Lines 132-135 (original)
    reg_df["const"] = 1

    # Set multi-index for panel
    reg_df = reg_df.set_index(["gvkey", "yq_id"])
```

#### Planned Change
```
old_string: |
    reg_df["const"] = 1

    # Set multi-index for panel
    reg_df = reg_df.set_index(["gvkey", "yq_id"])

new_string: |
    reg_df["const"] = 1

    # Deduplicate firm-quarters by keeping the last call per quarter
    # This resolves 347 firm-quarters with >1 earnings call (694 duplicate rows)
    reg_df = reg_df.sort_values("start_date").drop_duplicates(
        subset=["gvkey", "yq_id"], keep="last"
    )

    # Set multi-index for panel
    reg_df = reg_df.set_index(["gvkey", "yq_id"])
```

#### After State
```python
# Lines 132-141 (after fix)
    reg_df["const"] = 1

    # Deduplicate firm-quarters by keeping the last call per quarter
    # This resolves 347 firm-quarters with >1 earnings call (694 duplicate rows)
    reg_df = reg_df.sort_values("start_date").drop_duplicates(
        subset=["gvkey", "yq_id"], keep="last"
    )

    # Set multi-index for panel
    reg_df = reg_df.set_index(["gvkey", "yq_id"])
```

#### Verification
- [x] Edit was applied successfully
- [x] Deduplication logic added before set_index
- [x] No unintended changes made

**Verdict:** FIXED

---

### H10-006: Turn_Uncertainty_pct Unwinsorized

**Status Before Fix:** NOT FIXED (MINOR)

**Target File:** `docs/provenance/H10.md`
**Target Lines:** 279-285

**Decision:** Document as intentional (no code change required)

#### Before State
```markdown
### Winsorization

| Variable Set | Method | Thresholds | Where Applied |
|--------------|--------|------------|---------------|
| Linguistic percentages (`CFO_QA_Uncertainty_pct`, etc.) | Pooled 1%/99% | Lower=0.01, Upper=0.99 | `base.py:_finalize_data()` via `winsorize_pooled()` |
| Financial controls (Size, BM, Lev, ROA) | No winsorization | — | Raw values used |
| Returns (StockRet, MarketRet) | No winsorization | — | Raw values used |
```

#### After State
```markdown
### Winsorization

| Variable | Winsorization Method | Thresholds | Where Applied | Notes |
|----------|---------------------|------------|---------------|-------|
| CEO_QA_Uncertainty_pct | Per-year 1%/99% | Lower=0.01, Upper=0.99 | LinguisticEngine | Max varies by year (1.89-2.51) |
| CFO_QA_Uncertainty_pct | Pooled 1%/99% | Lower=0.01, Upper=0.99 | `CFOQAUncertaintyBuilder._finalize_data()` | Pooled max=3.378 |
| Turn_Uncertainty_pct | None (intentional) | N/A | N/A | IHS transform handles extremes; extreme values (>50%) retained as valid signals of short-turn uncertainty; Call + Speaker FE absorb turn-level outliers |
| Financial controls (Size, BM, Lev, ROA) | Per-year 1%/99% | Lower=0.01, Upper=0.99 | CompustatEngine | Standard Compustat processing |
| Returns (StockRet, MarketRet) | No winsorization | — | Raw values used | Inter-call compound returns |
```

#### Verification
- [x] Documentation updated to reflect intentional non-winsorization of Turn_Uncertainty_pct
- [x] Rationale documented (IHS transform, short-turn signal, Call+Speaker FE)

**Verdict:** FIXED (Documentation)

---

### H10-007: Winsorization Inconsistency Documentation

**Status Before Fix:** NOT FIXED (MINOR)

**Target File:** `docs/provenance/H10.md`
**Target Lines:** 279-285

**Decision:** Combined with H10-006 fix - updated winsorization table to correctly document each variable

#### Rationale
The provenance previously claimed "pooled 1/99%" for all linguistic percentages, but:
- CEO_QA_Uncertainty_pct uses per-year winsorization (via LinguisticEngine)
- CFO_QA_Uncertainty_pct uses pooled winsorization
- Turn_Uncertainty_pct uses no winsorization

The updated table now correctly documents each variable's winsorization method.

**Verdict:** FIXED (Documentation)

---

### H10-009: CEO_Unc_Lag1 Zero Rate

**Status Before Fix:** PARTIAL (NOTE)

**Target File:** `docs/provenance/H10.md`
**Target Lines:** Added as Section J.7

#### Added Documentation
```markdown
### 7. CEO_Unc_Lag1 Has High Zero Rate

**Issue:** CEO_Unc_Lag1 (used in robustness spec M2_lag1) is 57.9% zeros.

**Cause:** The ffill propagation means many manager turns inherit 0.0 from the first CEO turn's lag (which is NaN→0 after ffill).

**Impact:** The M2_lag1 specification (β=0.0167) has lower coefficient than baseline (β=0.0426), possibly due to the mass of zeros.

**Recommendation:** Interpret M2_lag1 results with caution. The baseline expanding mean specification is preferred.

**Status:** KNOWN — documented design consequence of ffill lag construction.
```

**Verdict:** FIXED (Documentation)

---

### H10-010: 2002 Absent from M1

**Status Before Fix:** PARTIAL (NOTE)

**Target File:** `docs/provenance/H10.md`
**Target Lines:** Added as Section J.8

#### Added Documentation
```markdown
### 8. Year 2002 Excluded from M1 Sample

**Issue:** All four quarters of 2002 are absent from the M1 regression sample (N quarters = 64, not 68).

**Cause:** ClarityStyle_Realtime requires ≥4 prior CEO calls. Since the dataset starts in 2002, CEOs don't accumulate 4 calls until late 2002/early 2003. Combined with listwise deletion on ClarityStyle_Realtime NaN (44.5%), all 2002 observations are eliminated.

**Impact:** Effective estimation period for M1 is 2003Q1–2018Q4.

**Recommendation:** This is expected behavior. Document clearly in paper.

**Status:** KNOWN — by design per real-time style estimation methodology.
```

**Verdict:** FIXED (Documentation)

---

### H10-008: LaTeX Sample Attrition Table

**Status Before Fix:** NOT FIXED (MINOR)

**Decision:** SKIPPED

**Rationale:**
- This is an optional enhancement that can be generated from existing `reconciliation_table.csv`
- The CSV already contains all necessary data
- Generating LaTeX is a formatting task that does not affect data integrity
- Can be deferred to publication preparation phase

**Verdict:** SKIPPED (Optional enhancement)

---

## Syntax Verification

```bash
python -c "import ast; ast.parse(open('src/f1d/econometric/run_h10_tone_at_top.py').read())"
```

Result: SUCCESS

---

## Post-Fix Verification

### Expected Changes After Stage 4 Rerun

| Metric | Before Fix | After Fix |
|--------|------------|-----------|
| M1 Main N | 43,570 | ~35,399 |
| M2 Main N | 1,697,632 | ~1,309,955 |
| M1 duplicate entity-time | 347 | 0 |

### Critical Acceptance Tests (After Rerun)

```python
# Test 1: Sample filter
import pandas as pd
diag = pd.read_csv('outputs/econometric/tone_at_top/LATEST/model_diagnostics.csv')
main_m1 = diag[diag['model'].str.contains('Main_M1')]
assert 34000 < main_m1['n_obs'].values[0] < 37000, f"Main M1 N = {main_m1['n_obs'].values[0]}"

# Test 2: No duplicates
cp = pd.read_parquet('outputs/variables/tone_at_top/LATEST/tone_at_top_panel.parquet')
cp['yq_id'] = (cp['year'].astype(str) + 'Q' + cp['quarter'].astype(str))
reg = cp[cp['sample'] == 'Main'].dropna(subset=['ClarityStyle_Realtime','CFO_QA_Uncertainty_pct'])
dups = reg.groupby(['gvkey','yq_id']).size()
assert (dups > 1).sum() == 0, "Duplicate entity-time still exists"
```

---

## Command Log

| # | Command | Purpose | Result |
|---|---------|---------|--------|
| 1 | Read FIX_PLAN_PROMPT_H10.md | Understand fix instructions | SUCCESS |
| 2 | Read AUDIT_REVERIFICATION_H10.md | Understand issues | SUCCESS |
| 3 | Read run_h10_tone_at_top.py (full) | Understand code structure | SUCCESS |
| 4 | Read H10.md | Understand provenance | SUCCESS |
| 5 | Edit run_h10_tone_at_top.py:1168-1177 | Fix sample filter bug (H10-001) | SUCCESS |
| 6 | Edit run_h10_tone_at_top.py:132-135 | Add deduplication (H10-003) | SUCCESS |
| 7 | python -c "ast.parse(...)" | Verify Python syntax | SUCCESS |
| 8 | Edit H10.md:279-285 | Update winsorization table (H10-006, H10-007) | SUCCESS |
| 9 | Edit H10.md:Section J | Add known issues (H10-009, H10-010) | SUCCESS |
| 10 | Re-read modified sections | Verify all changes | SUCCESS |

---

## Summary of Changes

### Code Changes (run_h10_tone_at_top.py)

1. **Line 1174-1175:** Sample filter now correctly filters "Main" sample to Main-only rows
   - Before: `call_panel if sample == "Main" else call_panel[call_panel["sample"] == sample]`
   - After: `call_panel[call_panel["sample"] == sample].copy()`

2. **Lines 134-138:** Added deduplication before set_index
   - New code: `reg_df.sort_values("start_date").drop_duplicates(subset=["gvkey", "yq_id"], keep="last")`

### Documentation Changes (H10.md)

1. **Section G (Winsorization):** Updated table to correctly document each variable's winsorization method
   - Added CEO_QA_Uncertainty_pct (per-year)
   - Added CFO_QA_Uncertainty_pct (pooled)
   - Added Turn_Uncertainty_pct (none - intentional)
   - Corrected financial controls (per-year, not "no winsorization")

2. **Section J (Known Issues):** Added two new issues
   - Issue 7: CEO_Unc_Lag1 high zero rate (57.9%)
   - Issue 8: Year 2002 excluded from M1 sample

---

## Next Steps

1. **Rerun Stage 4** to apply sample filter and deduplication fixes
2. **Verify** that M1 Main N drops from 43,570 to ~35,399
3. **Verify** that M2 Main N drops from 1,697,632 to ~1,309,955
4. **Verify** that no duplicate entity-time indices exist in M1

---

*Report generated: 2026-03-02*
*Execution completed following FIX_PLAN_PROMPT_H10.md protocol*
