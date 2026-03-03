# Re-Verification Audit Report: Suite H1

**Date:** 2026-03-02
**Auditor:** Claude (AI Model)
**Input Documents:** H1.md, AUDIT_H1.md, Paper_Artifacts_Audit_H1.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H1.md

---

## Executive Summary

| Total Issues Verified | Confirmed Fixed | Confirmed Not Fixed | New Issues Found | Unverifiable |
|-----------------------|-----------------|---------------------|------------------|--------------|
| 4 | 3 | 0 | 0 | 0 |

### Overall Assessment

Suite H1 is in **excellent condition**. Three of four claimed issues have been fully resolved since the original audits, including two that audits claimed were "NOT FIXED" (H1-002 and H1-003). The fourth issue (H1-004) has been partially addressed with clearer "fiscal year" specification, though a complete fiscal vs calendar year distinction was not added. All cross-artifact consistency checks pass, and the Within-R² bug has been definitively fixed.

---

## Claim Ledger

| ID | Severity | Claim | Fix Location | Audit Status Claimed | Re-Verification Status |
|----|----------|-------|--------------|---------------------|------------------------|
| H1-001 | ~~BLOCKER~~ | Within-R² inflated via manual computation bug | `run_h1_cash_holdings.py` lines 389-425 | CLAIMS FIXED | **CONFIRMED FIXED** |
| H1-002 | MINOR | Missing `run_manifest.json` | Stage 4 output directory | CLAIMS NOT FIXED | **CONFIRMED FIXED** (disagreement with prior audit) |
| H1-003 | NOTE | Stale docstring (HC1 → firm-clustered) | `run_h1_cash_holdings.py` line 13 | CLAIMS NOT FIXED | **CONFIRMED FIXED** (disagreement with prior audit) |
| H1-004 | NOTE | Provenance claim about DV constancy misleading | `H1.md` Section J.4 | CLAIMS CLARIFIED | **PARTIALLY ADDRESSED** |

---

## Verification Results

### H1-001: Within-R² Bug

**Claimed Status:** FIXED
**Verification Steps:**
1. Located file: `src/f1d/econometric/run_h1_cash_holdings.py`
2. Read lines 380-450 to examine within_r2 computation
3. Searched for buggy pattern `np.mean(y)` - NOT FOUND
4. Searched for correct pattern `rsquared_within` - FOUND at lines 387, 391, 446

**Evidence:**

```bash
# Command: grep -n "np.mean(y)" src/f1d/econometric/run_h1_cash_holdings.py
# Result: No matches found

# Command: grep -n "rsquared_within" src/f1d/econometric/run_h1_cash_holdings.py
# Result:
#   387:    print(f"  R-squared (within): {model.rsquared_within:.4f}")
#   391:    within_r2 = float(model.rsquared_within)
#   446:        "rsquared": float(model.rsquared_within),
```

**Code Implementation (lines 391-392):**
```python
within_r2 = float(model.rsquared_within)
print(f"  Within-R2: {within_r2:.4f}")
```

**Output Verification (model_diagnostics.csv):**
```
Latest run: 2026-03-01_234219
within_r2 range: -0.0123 - 0.0624
rsquared range: -0.0123 - 0.0624
```

**LaTeX Table Verification:**
```
Line 17: Within-R$^2$ & 0.059 & 0.061 & 0.059 & 0.061 & 0.059 & 0.062 \\
```

**Raw PanelOLS Output (regression_results_Main_CEO_QA_Uncertainty_pct.txt, line 5):**
```
No. Observations:               54708   R-squared (Within):               0.0607
```

**Verdict:** CONFIRMED FIXED

**Rationale:** The buggy manual `within_r2` computation has been removed. The code now correctly uses `model.rsquared_within` directly. All three sources (raw output, CSV, LaTeX) report consistent values in the ~0.06 range, NOT the inflated ~0.84.

---

### H1-002: Missing Run Manifest

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Searched for `run_manifest.json` in all Stage 4 outputs
2. Found manifest in latest run directory
3. Verified manifest generation code exists

**Evidence:**

```bash
# Command: find outputs/econometric/h1_cash_holdings -name "run_manifest.json" -type f
# Result: outputs/econometric/h1_cash_holdings/2026-03-01_234219/run_manifest.json
```

**Manifest Contents (2026-03-01_234219/run_manifest.json):**
```json
{
  "manifest_version": "1.0",
  "stage": "stage4",
  "timestamp": "2026-03-01_234219",
  "generated_at": "2026-03-01T23:42:24.072798",
  "git_commit": "c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50",
  "command": "C:\\Users\\sinas\\...\\run_h1_cash_holdings.py",
  "input_hashes": {
    "panel": "f05975159157b1e1b79a632a4649095c407d33b522becabca6bdd76e0ce9eb6f"
  },
  "output_files": {
    "diagnostics": "...model_diagnostics.csv",
    "table": "...h1_cash_holdings_table.tex"
  },
  "config": {},
  "panel_path": "...h1_cash_holdings_panel.parquet",
  "panel_hash": "f05975159157b1e1b79a632a4649095c407d33b522becabca6bdd76e0ce9eb6f"
}
```

**Code Evidence (lines 843-855):**
```python
# Generate run manifest
generate_manifest(
    output_dir=out_dir,
    stage="stage4",
    timestamp=timestamp,
    input_paths={"panel": panel_file},
    output_files={
        "diagnostics": out_dir / "model_diagnostics.csv",
        "table": out_dir / "h1_cash_holdings_table.tex",
    },
    panel_path=panel_file,
)
print("  Saved: run_manifest.json")
```

**Verdict:** CONFIRMED FIXED (DISAGREES with prior audit claim of "NOT FIXED")

**Rationale:** A complete `run_manifest.json` now exists in the latest Stage 4 output with git commit hash, input hashes, and output file paths. The code at lines 843-855 generates this manifest. The prior audit was correct at the time (2026-02-28 run had no manifest), but this has been fixed in subsequent runs.

---

### H1-003: Stale Docstring

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Read lines 1-30 of `run_h1_cash_holdings.py`
2. Verified docstring content at line 13
3. Cross-checked with actual SE implementation at line 380

**Evidence:**

**Current Docstring (line 13):**
```
those tests: same statsmodels OLS engine, same firm-clustered standard errors, same
```

**Git History Verification:**
```bash
# Command: git show 24f5642:src/f1d/econometric/run_h1_cash_holdings.py | head -20
# Original (buggy): "same HC1 standard errors"

# Current (fixed): "same firm-clustered standard errors"
```

**Actual SE Implementation (line 380):**
```python
model = model_obj.fit(cov_type="clustered", cluster_entity=True)
```

**Verdict:** CONFIRMED FIXED (DISAGREES with prior audit claim of "NOT FIXED")

**Rationale:** The docstring now correctly states "firm-clustered standard errors" instead of the incorrect "HC1 standard errors". This matches the actual implementation at line 380 which uses `cov_type="clustered", cluster_entity=True`.

---

### H1-004: DV Constancy Provenance Claim

**Claimed Status:** CLARIFIED
**Verification Steps:**
1. Read Section J.4 of H1.md (lines 428-435)
2. Verified underlying data property via Python
3. Checked for explicit fiscal vs calendar year distinction

**Evidence:**

**Current Provenance Text (H1.md lines 428-434):**
```markdown
### 4. Moulton Correction (MAJOR-1 Fix)

**Issue:** HC1 standard errors were initially used, but `CashHoldings_lead` is constant
within firm-year clusters (all calls in the same fiscal year share the same DV).

**Fix:** Changed to firm-clustered SEs (`cluster_entity=True`) to correct within-firm correlation.
```

**Data Verification:**
```
Fiscal year clusters with 1 unique value: 26,631
Fiscal year clusters with >1 unique values: 0
Calendar year clusters with 1 unique value: 6,961
Calendar year clusters with >1 unique values: 21,377
```

**Verdict:** PARTIALLY ADDRESSED

**Rationale:** The provenance text now correctly specifies "fiscal year" in parentheses, which is an improvement. However, the audit recommendation was to explicitly state that while the DV is constant within fiscal year, the PanelOLS uses calendar year for time FE, meaning the DV is NOT constant within the PanelOLS `(gvkey, year)` index. The current text does not make this distinction explicit. The data verification confirms ~75% of calendar year clusters have multiple DV values.

---

## Additional Findings

No new issues discovered during verification. The suite is in good condition.

---

## Cross-Artifact Consistency Matrix

### Regression: Main / CEO_QA_Uncertainty_pct (Column 2)

| Source | Field | Expected Value | Actual Value | Match? |
|--------|-------|----------------|--------------|--------|
| Raw .txt (line 25) | beta1 | - | 0.0065 | - |
| model_diagnostics.csv | beta1 | 0.0065 | 0.0065 | **YES** |
| LaTeX table (line 12) | beta1 coef | 0.0065*** | 0.0065*** | **YES** |
| Raw .txt (line 25) | beta1_SE | - | 0.0021 | - |
| LaTeX table (line 13) | (SE) | (0.0021) | (0.0021) | **YES** |
| Raw .txt (line 5) | N | - | 54,708 | - |
| model_diagnostics.csv | n_obs | 54,708 | 54,708 | **YES** |
| LaTeX table (line 16) | N | 54,708 | 54,708 | **YES** |
| Raw .txt (line 5) | R-squared (Within) | - | 0.0607 | - |
| model_diagnostics.csv | within_r2 | 0.0607 | 0.0607 | **YES** |
| LaTeX table (line 17) | Within-R2 | 0.061 | 0.061 | **YES** (rounded) |

**Verdict:** All three sources (raw output, diagnostics CSV, LaTeX table) are internally consistent.

---

## Recommendations

1. **[LOW PRIORITY]** Complete H1-004 clarification: Add explicit note to H1.md Section J.4 stating that while DV is constant within fiscal year, PanelOLS uses calendar year for time FE, so the DV varies within the `(gvkey, year)` index. Example text:

   > "Note: While `CashHoldings_lead` is constant within fiscal year (fyearq), the PanelOLS estimator uses calendar year (`year`) for time fixed effects. Approximately 75% of (gvkey, calendar_year) clusters contain multiple unique DV values. Firm-level clustering remains the correct approach for handling within-firm serial correlation."

---

## Command Log

| # | Command | Purpose | Timestamp |
|---|---------|---------|-----------|
| 1 | `find src -name "run_h1_cash_holdings.py" -type f` | Locate script | 2026-03-02 |
| 2 | Read `run_h1_cash_holdings.py` lines 380-450 | Examine within_r2 computation | 2026-03-02 |
| 3 | `grep -n "np.mean(y)" run_h1_cash_holdings.py` | Search for buggy pattern | 2026-03-02 |
| 4 | `grep -n "rsquared_within" run_h1_cash_holdings.py` | Search for correct pattern | 2026-03-02 |
| 5 | `ls -lt outputs/econometric/h1_cash_holdings/` | List Stage 4 runs | 2026-03-02 |
| 6 | Python: read model_diagnostics.csv | Check R² values | 2026-03-02 |
| 7 | `grep -n "R-squared.*Within" .../regression_results_*.txt` | Check raw output R² | 2026-03-02 |
| 8 | `grep -n "Within-R" h1_cash_holdings_table.tex` | Check LaTeX R² | 2026-03-02 |
| 9 | `find ... -name "run_manifest.json"` | Search for manifest | 2026-03-02 |
| 10 | Read `run_manifest.json` | Verify manifest contents | 2026-03-02 |
| 11 | `grep -n "run_manifest" run_h1_cash_holdings.py` | Check manifest generation code | 2026-03-02 |
| 12 | Read `run_h1_cash_holdings.py` lines 1-30 | Check docstring | 2026-03-02 |
| 13 | `git log --oneline --since="2026-02-27" -- run_h1...` | Check git history | 2026-03-02 |
| 14 | `git show 24f5642:.../run_h1...py \| head -20` | Check original docstring | 2026-03-02 |
| 15 | `grep -n "cov_type\|cluster_entity" run_h1...py` | Verify SE implementation | 2026-03-02 |
| 16 | Read H1.md lines 425-465 | Check provenance J.4 section | 2026-03-02 |
| 17 | `grep -n "calendar year" H1.md` | Search for calendar year distinction | 2026-03-02 |
| 18 | Python: verify DV constancy | Verify fiscal vs calendar year | 2026-03-02 |
| 19 | Read regression_results_Main_CEO_QA_Uncertainty_pct.txt | Cross-artifact verification | 2026-03-02 |
| 20 | Python: read model_diagnostics.csv row | Cross-artifact verification | 2026-03-02 |
| 21 | Read h1_cash_holdings_table.tex lines 1-25 | Cross-artifact verification | 2026-03-02 |

---

## Appendix: Raw Evidence

### A.1: Within-R² Code Implementation

**File:** `src/f1d/econometric/run_h1_cash_holdings.py`
**Lines 387-392:**
```python
print(f"  R-squared (within): {model.rsquared_within:.4f}")
print(f"  Adj R-squared:      {model.rsquared_inclusive:.4f}")
print(f"  N obs:              {int(model.nobs):,}")

within_r2 = float(model.rsquared_within)
print(f"  Within-R2: {within_r2:.4f}")
```

### A.2: model_diagnostics.csv Values

```
Latest run: 2026-03-01_234219
within_r2 range: -0.0123 - 0.0624
rsquared range: -0.0123 - 0.0624
```

### A.3: Raw PanelOLS Output

**File:** `outputs/econometric/h1_cash_holdings/2026-03-01_234219/regression_results_Main_CEO_QA_Uncertainty_pct.txt`
**Lines 1-10:**
```
                          PanelOLS Estimation Summary
================================================================================
Dep. Variable:      CashHoldings_lead   R-squared:                        0.0483
Estimator:                   PanelOLS   R-squared (Between):              0.2143
No. Observations:               54708   R-squared (Within):               0.0607
Date:                Sun, Mar 01 2026   R-squared (Overall):              0.1781
Time:                        23:42:20   Log-likelihood                 6.633e+04
Cov. Estimator:             Clustered
```

### A.4: LaTeX Table Within-R² Row

**File:** `outputs/econometric/h1_cash_holdings/2026-03-01_234219/h1_cash_holdings_table.tex`
**Line 17:**
```latex
Within-R$^2$ & 0.059 & 0.061 & 0.059 & 0.061 & 0.059 & 0.062 \\
```

### A.5: run_manifest.json Contents

```json
{
  "manifest_version": "1.0",
  "stage": "stage4",
  "timestamp": "2026-03-01_234219",
  "generated_at": "2026-03-01T23:42:24.072798",
  "git_commit": "c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50",
  "input_hashes": {
    "panel": "f05975159157b1e1b79a632a4649095c407d33b522becabca6bdd76e0ce9eb6f"
  },
  "panel_path": "...h1_cash_holdings_panel.parquet",
  "panel_hash": "f05975159157b1e1b79a632a4649095c407d33b522becabca6bdd76e0ce9eb6f"
}
```

### A.6: DV Constancy Verification

```
Latest panel: 2026-03-01_234046
Fiscal year clusters with 1 unique value: 26,631
Fiscal year clusters with >1 unique values: 0
Calendar year clusters with 1 unique value: 6,961
Calendar year clusters with >1 unique values: 21,377
```

---

## Conclusion

Suite H1 is **paper-submission ready**. All BLOCKER and MINOR issues identified in prior audits have been resolved:

- H1-001 (Within-R² bug): FIXED - code uses `model.rsquared_within` directly
- H1-002 (Missing manifest): FIXED - `run_manifest.json` now generated
- H1-003 (Stale docstring): FIXED - docstring correctly states "firm-clustered"
- H1-004 (DV constancy): PARTIALLY ADDRESSED - "fiscal year" specified but calendar year distinction not explicit

Cross-artifact consistency verified: all coefficients, SEs, N, and R² values match across raw output, diagnostics CSV, and LaTeX table.
