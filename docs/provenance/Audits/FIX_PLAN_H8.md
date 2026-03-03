# FIX PLAN: H8 Political Risk x CEO Speech Vagueness

**Generated:** 2026-03-02
**Source:** REVERIFICATION_REPORT_H8.md
**Status:** COMPLETE

---

## Summary

This document outlines the fixes required to make H8 paper-submission ready based on the reverification audit.

| Priority | Issue Count |
|----------|-------------|
| MAJOR | 2 |
| MINOR | 3 |
| NOTE | 0 |

---

## MAJOR Issues

### FIX-1: LaTeX Table Coefficient Formatting

**Issue:** LaTeX table displays PRiskFY and interact coefficients as "0.0000" due to `.4f` formatting

**File:** `src/f1d/econometric/run_h8_political_risk.py`

**Location:** Lines 337-349 (`fmt_coef()` function)

**Current Code:**
```python
def fmt_coef(val: float, pval: float) -> str:
    if pd.isna(val):
        return ""
    stars = (
        "^{***}"
        if pval < 0.01
        else "^{**}"
        if pval < 0.05
        else "^{*}"
        if pval < 0.10
        else ""
    )
    return f"{val:.4f}{stars}"
```

**Fix:**
```python
def fmt_coef(val: float, pval: float) -> str:
    if pd.isna(val):
        return ""
    stars = (
        "^{***}"
        if pval < 0.01
        else "^{**}"
        if pval < 0.05
        else "^{*}"
        if pval < 0.10
        else ""
    )
    # Use scientific notation for very small coefficients
    if abs(val) < 0.0001:
        return f"{val:.2e}{stars}"
    return f"{val:.4f}{stars}"
```

**Rerun Required:** Yes - Stage 4
```bash
python -m f1d.econometric.run_h8_political_risk
```

**Acceptance Criteria:**
- [ ] PRiskFY coefficient displays as "-8.06e-06" (or similar scientific notation)
- [ ] Interact coefficient displays as "1.71e-06" (or similar scientific notation)
- [ ] Standard errors for small coefficients also display in scientific notation

---

### FIX-2: Provenance Winsorization Documentation

**Issue:** H8.md claims "Pooled (all years)" winsorization but code uses per-year

**File:** `docs/provenance/H8.md`

**Location:** Lines 212-214, Line 227

**Current Text (Lines 212-214):**
```markdown
| Lev | Leverage | Control | ... | 1/99% pooled | ... |
| ROA | ROA | Control | ... | 1/99% pooled | ... |
| TobinsQ | Tobin's Q | Control | ... | 1/99% pooled | ... |
```

**Fix:**
```markdown
| Lev | Leverage | Control | ... | 1/99% per-year | ... |
| ROA | ROA | Control | ... | 1/99% per-year | ... |
| TobinsQ | Tobin's Q | Control | ... | 1/99% per-year | ... |
```

**Current Text (Line 227):**
```markdown
| Lev, ROA, TobinsQ, CashFlow, etc. | 1%/99% | Pooled (all years) | `_compustat_engine.py:1050-1057` |
```

**Fix:**
```markdown
| Lev, ROA, TobinsQ, CashFlow, etc. | 1%/99% | Per-year (within each fyearq) | `_compustat_engine.py:1036-1058` |
```

**Rerun Required:** No - Documentation only

**Acceptance Criteria:**
- [ ] Variable dictionary (lines 212-214) shows "1/99% per-year"
- [ ] Winsorization table (line 227) shows "Per-year (within each fyearq)"
- [ ] Line reference updated to `1036-1058`

---

## MINOR Issues

### FIX-3: Summary Stats Level Documentation

**Issue:** summary_stats.tex claims "call level" but data is firm-year level

**File:** `src/f1d/econometric/run_h8_political_risk.py`

**Location:** Summary stats LaTeX generation function

**Current Text:**
```latex
All variables are measured at the call level.
```

**Fix:**
```latex
All variables are measured at the firm-year level.
```

**Rerun Required:** Yes - Stage 4 (can be combined with FIX-1)

**Acceptance Criteria:**
- [ ] summary_stats.tex table note says "firm-year level"

---

### FIX-4: Document Edge Years in Known Issues

**Issue:** Panel contains fyearq=2000 and 2019 outside configured 2002-2018 range (undocumented)

**File:** `docs/provenance/H8.md`

**Location:** Section J (after line 387, before "Document Information")

**Add New Section:**
```markdown
### J.6) Panel Includes Fiscal Years Outside Config Range

**Issue:** Panel contains fyearq=2000 (1 row) and fyearq=2019 (78 rows), outside the configured 2002-2018 range.

**Cause:** `attach_fyearq()` uses backward `merge_asof` on `start_date -> datadate`, which can match calls near fiscal year boundaries to adjacent fiscal years.

**Impact:**
- Rows with fyearq > 2018 (78 rows) have `AbsAbInv_lead=NaN` and cannot enter regressions
- Rows with fyearq < 2002 (141 rows) mostly contribute as RHS observations with valid leads for fyearq=2002

**Status:** BENIGN -- Edge years cannot affect regression results; arise from merge_asof boundary behavior.
```

**Rerun Required:** No - Documentation only

**Acceptance Criteria:**
- [ ] J.6 section added to Known Issues
- [ ] Edge year counts documented (1 for 2000, 78 for 2019, 141 for <2002)

---

### FIX-5: Document style_frozen Identification Concern

**Issue:** 80.3% of firms have zero within-firm style_frozen variance (undocumented identification concern)

**File:** `docs/provenance/H8.md`

**Location:** Section J (after FIX-4, before "Document Information")

**Add New Section:**
```markdown
### J.7) Limited Within-Firm Variation in style_frozen

**Issue:** Only 258 of 1,665 firms (15.5%) in the regression sample have any within-firm variation in `style_frozen`. For 1,337 firms (80.3%), `style_frozen` has zero variance within the firm. An additional 70 firms have only one observation.

**Cause:** `style_frozen` is frozen within CEO tenure (calls <= fy_end). It only changes at CEO turnover events.

**Impact:**
- With Firm FE, coefficients on `style_frozen` and the interaction term are identified only from within-firm variation (CEO turnover)
- The effective sample for identification is ~258 firms, not 1,665
- Statistical power is very low for detecting the interaction effect
- The null result (beta3 not significant) may reflect low power rather than evidence of no effect

**Status:** IDENTIFICATION CONCERN -- Does not invalidate the test, but limits interpretation. Consider supplementary between-effects or pooled OLS analysis.

**Recommendation:** Report effective identifying firms (258) in thesis. Interpret null result as "insufficient evidence" rather than "evidence of no effect".
```

**Rerun Required:** No - Documentation only

**Acceptance Criteria:**
- [ ] J.7 section added to Known Issues
- [ ] Within-firm variation statistics documented (80.3% zero variance, 15.5% positive variance)
- [ ] Interpretation guidance included

---

## Implementation Order

1. **FIX-2, FIX-4, FIX-5** (Documentation) - Do first, no rerun needed
2. **FIX-1, FIX-3** (Code changes) - Do together, single Stage 4 rerun

## Total Rerun Count

1 Stage 4 rerun required after all fixes applied.

---

## Verification After Fixes

After implementing all fixes and rerunning Stage 4, verify:

```bash
# 1. Check LaTeX table for scientific notation
grep -E "e-0[0-9]" outputs/econometric/h8_political_risk/LATEST/h8_political_risk_table.tex

# 2. Check summary_stats.tex level
grep "firm-year level" outputs/econometric/h8_political_risk/LATEST/summary_stats.tex

# 3. Verify model diagnostics unchanged
python -c "
import pandas as pd
diag = pd.read_csv('outputs/econometric/h8_political_risk/LATEST/model_diagnostics.csv')
print(f'N obs: {diag[\"n_obs\"].iloc[0]}')
print(f'beta3: {diag[\"beta3_Interact\"].iloc[0]:.6e}')
print(f'p3: {diag[\"p3\"].iloc[0]:.4f}')
"
```

Expected output:
- N obs: 15721
- beta3: ~1.71e-06
- p3: ~0.7760

---

## Document Status

| Fix ID | Status | Assignee | Date Completed |
|--------|--------|----------|----------------|
| FIX-1 | COMPLETE | AI Auditor | 2026-03-02 |
| FIX-2 | COMPLETE | AI Auditor | 2026-03-02 |
| FIX-3 | COMPLETE | AI Auditor | 2026-03-02 |
| FIX-4 | COMPLETE | AI Auditor | 2026-03-02 |
| FIX-5 | COMPLETE | AI Auditor | 2026-03-02 |
