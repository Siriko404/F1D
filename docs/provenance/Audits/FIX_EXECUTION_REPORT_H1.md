# Fix Execution Report: Suite H1

**Date:** 2026-03-02
**Executor:** Claude (AI Model)
**Input Document:** AUDIT_REVERIFICATION_H1.md
**Target Files Modified:** docs/provenance/H1.md

---

## Executive Summary

| Issues Fixed | Issues Unfixable | Issues Skipped |
|--------------|------------------|----------------|
| 1 | 0 | 0 |

### Files Modified
- `C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\provenance\H1.md` (Section J.4, lines 428-440)

---

## Issue Fix Details

### H1-004: DV Constancy Provenance Claim

**Status Before Fix:** PARTIALLY ADDRESSED

**Target File:** docs/provenance/H1.md
**Target Section:** J.4 (Moulton Correction / MAJOR-1 Fix)

#### Before State
```
Lines 428-436:
### 4. Moulton Correction (MAJOR-1 Fix)

**Issue:** HC1 standard errors were initially used, but `CashHoldings_lead` is constant within firm-year clusters (all calls in the same fiscal year share the same DV).

**Fix:** Changed to firm-clustered SEs (`cluster_entity=True`) to correct within-firm correlation.

**Verification:** All Stage 4 regressions now use `cov_type="clustered", cluster_entity=True`.
```

#### Planned Change
```
old_string: |
  ### 4. Moulton Correction (MAJOR-1 Fix)

  **Issue:** HC1 standard errors were initially used, but `CashHoldings_lead` is constant within firm-year clusters (all calls in the same fiscal year share the same DV).

  **Fix:** Changed to firm-clustered SEs (`cluster_entity=True`) to correct within-firm correlation.

  **Verification:** All Stage 4 regressions now use `cov_type="clustered", cluster_entity=True`.

new_string: |
  ### 4. Moulton Correction (MAJOR-1 Fix)

  **Issue:** HC1 standard errors were initially used, but `CashHoldings_lead` exhibits clustering structure that requires correction.

  **Clarification on clustering structure:**
  - `CashHoldings_lead` is measured at fiscal year end (`fyearq`) and is **constant within (gvkey, fyearq) clusters** — all calls in the same fiscal year share the same DV value.
  - However, the PanelOLS estimator uses **calendar year** (`year`) for time fixed effects (via `C(year)`), not fiscal year.
  - Because calls within a calendar year can span two fiscal years (for non-December FYE firms), approximately **75% of (gvkey, calendar_year) clusters contain multiple unique DV values**.
  - Despite this calendar-year variation, **firm-level clustering** (`cluster_entity=True`) remains the econometrically correct approach, as it captures arbitrary within-firm serial correlation regardless of time dimension.

  **Fix:** Changed to firm-clustered SEs (`cluster_entity=True`) to correct within-firm correlation.

  **Verification:** All Stage 4 regressions now use `cov_type="clustered", cluster_entity=True`.
```

#### After State
```
Lines 428-440:
### 4. Moulton Correction (MAJOR-1 Fix)

**Issue:** HC1 standard errors were initially used, but `CashHoldings_lead` exhibits clustering structure that requires correction.

**Clarification on clustering structure:**
- `CashHoldings_lead` is measured at fiscal year end (`fyearq`) and is **constant within (gvkey, fyearq) clusters** — all calls in the same fiscal year share the same DV value.
- However, the PanelOLS estimator uses **calendar year** (`year`) for time fixed effects (via `C(year)`), not fiscal year.
- Because calls within a calendar year can span two fiscal years (for non-December FYE firms), approximately **75% of (gvkey, calendar_year) clusters contain multiple unique DV values**.
- Despite this calendar-year variation, **firm-level clustering** (`cluster_entity=True`) remains the econometrically correct approach, as it captures arbitrary within-firm serial correlation regardless of time dimension.

**Fix:** Changed to firm-clustered SEs (`cluster_entity=True`) to correct within-firm correlation.

**Verification:** All Stage 4 regressions now use `cov_type="clustered", cluster_entity=True`.
```

#### Verification
- [x] Edit was applied successfully
- [x] No unintended changes made
- [x] Documentation now accurately reflects implementation
- [x] Markdown formatting preserved

**Verdict:** FIXED

---

## Code Cross-Reference

### PanelOLS Time FE Implementation
```
src/f1d/econometric/run_h1_cash_holdings.py:
   21:                        C(gvkey) + C(year)
  327:                            C(gvkey) + C(year)
  363:        + " + EntityEffects + TimeEffects"
  367:        f"+ {' + '.join(controls)} + EntityEffects + TimeEffects"
  626:        r"Model includes firm FE (C(gvkey)) and year FE (C(year)).",
  663:        "    C(gvkey) + C(year)",
```

### Firm-Clustering Implementation
```
src/f1d/econometric/run_h1_cash_holdings.py:
  380:        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
```

---

## Post-Fix Verification

### Documentation Accuracy Check
The updated documentation now accurately describes:
1. **Fiscal year constancy**: `CashHoldings_lead` is constant within (gvkey, fyearq) clusters because it is measured at fiscal year end.
2. **Calendar year variation**: PanelOLS uses calendar year (`year`) for time fixed effects via `C(year)`, which differs from fiscal year for non-December FYE firms.
3. **75% statistic**: Approximately 75% of (gvkey, calendar_year) clusters contain multiple unique DV values (verified in AUDIT_REVERIFICATION_H1.md: 21,377 out of 28,338 calendar year clusters have >1 unique values).
4. **Firm-level clustering rationale**: Firm-level clustering captures arbitrary within-firm serial correlation regardless of time dimension, making it the correct approach.

### Regression Prevention
To prevent this documentation from becoming stale:
- Section J.4 now explicitly references the code implementation details (`C(year)`, `cluster_entity=True`)
- The fiscal vs calendar year distinction is documented inline
- Any future changes to the clustering approach would require updating this section

---

## Command Log

| # | Command/Action | Purpose | Timestamp |
|---|----------------|---------|-----------|
| 1 | Read `docs/provenance/FIX_PLAN_PROMPT_H1.md` | Understand fix instructions | 2026-03-02 |
| 2 | Read `docs/provenance/AUDIT_REVERIFICATION_H1.md` | Understand issue details | 2026-03-02 |
| 3 | Read `docs/provenance/H1.md` (full file) | Understand target file context | 2026-03-02 |
| 4 | Grep `C(year)\|TimeEffects\|cluster_entity` in `run_h1_cash_holdings.py` | Cross-reference code implementation | 2026-03-02 |
| 5 | Edit `docs/provenance/H1.md` Section J.4 | Apply fix | 2026-03-02 |
| 6 | Read `docs/provenance/H1.md` lines 425-460 | Verify fix applied correctly | 2026-03-02 |
| 7 | Write `docs/provenance/FIX_EXECUTION_REPORT_H1.md` | Document execution | 2026-03-02 |

---

## Appendix: Full File Diff

### Unified Diff for Section J.4

```diff
--- a/docs/provenance/H1.md (before)
+++ b/docs/provenance/H1.md (after)
@@ -426,10 +426,18 @@

 ### 4. Moulton Correction (MAJOR-1 Fix)

-**Issue:** HC1 standard errors were initially used, but `CashHoldings_lead` is constant within firm-year clusters (all calls in the same fiscal year share the same DV).
+**Issue:** HC1 standard errors were initially used, but `CashHoldings_lead` exhibits clustering structure that requires correction.
+
+**Clarification on clustering structure:**
+- `CashHoldings_lead` is measured at fiscal year end (`fyearq`) and is **constant within (gvkey, fyearq) clusters** — all calls in the same fiscal year share the same DV value.
+- However, the PanelOLS estimator uses **calendar year** (`year`) for time fixed effects (via `C(year)`), not fiscal year.
+- Because calls within a calendar year can span two fiscal years (for non-December FYE firms), approximately **75% of (gvkey, calendar_year) clusters contain multiple unique DV values**.
+- Despite this calendar-year variation, **firm-level clustering** (`cluster_entity=True`) remains the econometrically correct approach, as it captures arbitrary within-firm serial correlation regardless of time dimension.

 **Fix:** Changed to firm-clustered SEs (`cluster_entity=True`) to correct within-firm correlation.

 **Verification:** All Stage 4 regressions now use `cov_type="clustered", cluster_entity=True`.

 ---
```

---

## Conclusion

Issue H1-004 has been successfully fixed. Section J.4 of H1.md now clearly distinguishes between fiscal year (where DV is constant) and calendar year (where DV is NOT constant, used by PanelOLS time FE). The documentation accurately reflects the verified data statistics (75% of calendar year clusters have multiple DV values) and the code implementation (firm-level clustering via `cluster_entity=True`).
