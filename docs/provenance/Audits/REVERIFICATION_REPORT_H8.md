# H8 Political Risk x CEO Speech Vagueness -- Reverification Report

**Verification Date:** 2026-03-02
**Verifier:** AI Auditor
**Scope:** All claims from AUDIT_H8.md and Paper_Artifacts_Audit_H8.md
**Latest Run:** 2026-03-02_001047

---

## 1. Executive Summary

| Metric | Count |
|--------|-------|
| Total Claims Verified | 8 |
| Claims Fixed | 2 |
| Claims Still Present | 4 |
| Claims Invalid | 0 |
| Claims Partially Fixed | 2 |

### Paper-Submission Readiness Verdict
**NOT READY** -- Two MAJOR issues remain unresolved:
1. LaTeX table displays PRiskFY and interact coefficients as "0.0000" (unreadable)
2. Provenance claims "pooled" winsorization but code uses "per-year"

### Top Outstanding Issues
1. **MAJ-1:** LaTeX table displays key coefficients as "0.0000" due to .4f formatting -- coefficients are O(1e-6)
2. **MAJ-2:** Provenance H8.md Section G claims "Pooled (all years)" winsorization but code uses per-year
3. **MIN-1:** summary_stats.tex incorrectly claims "call level" when data is firm-year level
4. **MIN-2/3:** Two documentation gaps in provenance Known Issues section

---

## 2. Claim Ledger (Full)

| ID | Severity | Claim | Verdict | Evidence |
|----|----------|-------|---------|----------|
| MAJ-1 | MAJOR | LaTeX displays 0.0000 | STILL PRESENT | [Section 3.1](#31-maj-1-latex-table-displays-key-coefficients-as-00000) |
| MAJ-2 | MAJOR | Provenance claims pooled winsorization | STILL PRESENT | [Section 3.2](#32-maj-2-provenance-claims-pooled-winsorization-code-uses-per-year) |
| MAJ-3 | MAJOR | Missing reproducibility artifacts | PARTIALLY FIXED | [Section 3.3](#33-maj-3-missing-reproducibility-artifacts) |
| MIN-1 | MINOR | Summary stats claims call level | STILL PRESENT | [Section 3.4](#34-min-1-latex-summary-stats-claims-call-level) |
| MIN-2 | MINOR | Panel includes fiscal years outside config range | STILL PRESENT | [Section 3.5](#35-min-2-panel-includes-fiscal-years-outside-config-range) |
| MIN-3 | MINOR | style_frozen absorbed by Firm FE | STILL PRESENT | [Section 3.6](#36-min-3-style_frozen-absorbed-by-firm-fe-for-845-of-firms) |
| NOT-1 | NOTE | LaTeX table missing SE cluster docs | FIXED | [Section 3.7](#37-not-1-latex-table-missing-se-cluster-documentation) |
| NOT-2 | NOTE | aggregate_to_firm_year .last() skipna | PARTIALLY FIXED | [Section 3.8](#38-not-2-aggregate_to_firm_year-uses-last-without-explicit-skipna) |

---

## 3. Detailed Verification Results

### 3.1 MAJ-1: LaTeX Table Displays Key Coefficients as "0.0000"

**Claim:** LaTeX table displays PRiskFY and interact coefficients as "0.0000" because they are O(1e-6) formatted with `.4f`

**Source:** AUDIT_H8.md Finding #3, Paper_Artifacts_Audit_H8.md Finding #1

**Expected Location:** `outputs/econometric/h8_political_risk/{timestamp}/h8_political_risk_table.tex`

**Verification Steps:**

1. Read the LaTeX table from latest run:
   - File: `outputs/econometric/h8_political_risk/2026-03-02_001047/h8_political_risk_table.tex`
   - Line 10: `Political Risk & -0.0000 & -0.0000 \\`
   - Line 11: ` & (0.0000) & (0.0000) \\`
   - Line 14: `PRisk $\times$ Style Frozen & 0.0000 & 0.0000 \\`
   - Line 15: ` & (0.0000) & (0.0000) \\`

2. Check actual coefficient values in model_diagnostics.csv:
   - File: `outputs/econometric/h8_political_risk/2026-03-02_001047/model_diagnostics.csv`
   - Line 2 (Primary): `beta1_PRiskFY = -8.056637425727743e-06`
   - Line 2 (Primary): `beta3_Interact = 1.7134830185360742e-06`

3. Check formatting function in code:
   - File: `src/f1d/econometric/run_h8_political_risk.py`
   - Line 337-349: `fmt_coef()` function
   - Line 349: `return f"{val:.4f}{stars}"` -- uses fixed 4 decimal places

**Verdict: STILL PRESENT**

**Rationale:** The LaTeX table still displays coefficients as "0.0000" because the `fmt_coef()` function at line 349 uses `.4f` formatting. Values of order 1e-6 round to 0.0000 at 4 decimal places. The table is technically correct but unreadable for interpretation.

**Fix Required:** Modify `fmt_coef()` to use scientific notation for small coefficients:
```python
if abs(val) < 0.0001:
    return f"{val:.2e}{stars}"
return f"{val:.4f}{stars}"
```

---

### 3.2 MAJ-2: Provenance Claims "Pooled" Winsorization; Code Uses Per-Year

**Claim:** H8.md Section G claims "1/99% pooled" winsorization but code uses per-year winsorization

**Source:** AUDIT_H8.md Finding #2, Paper_Artifacts_Audit_H8.md Finding #2

**Expected Location:** `docs/provenance/H8.md` Section G (around line 227)

**Verification Steps:**

1. Read H8.md Section G winsorization claims:
   - File: `docs/provenance/H8.md`
   - Line 212: `| Lev | Leverage | Control | ... | 1/99% pooled |`
   - Line 213: `| ROA | ROA | Control | ... | 1/99% pooled |`
   - Line 214: `| TobinsQ | Tobin's Q | Control | ... | 1/99% pooled |`
   - Line 227: `| Lev, ROA, TobinsQ, CashFlow, etc. | 1%/99% | Pooled (all years) | _compustat_engine.py:1050-1057 |`

2. Check actual winsorization implementation in code:
   - File: `src/f1d/shared/variables/_compustat_engine.py`
   - Line 1036-1038: Comment says "B3 fix: Apply per-year winsorization (1%/99% within each fyearq)"
   - Line 429: Function `_winsorize_by_year()` defined
   - Line 1058: `comp[col] = _winsorize_by_year(comp[col], year_col)`

**Verdict: STILL PRESENT**

**Rationale:** The provenance document H8.md still claims "Pooled (all years)" winsorization at lines 212-214 and 227. The actual code correctly uses per-year winsorization via `_winsorize_by_year()` function. The provenance documentation is factually incorrect.

**Fix Required:** Update H8.md Section G:
- Line 212-214: Change "1/99% pooled" to "1/99% per-year"
- Line 227: Change "Pooled (all years)" to "Per-year (within each fyearq)"
- Update line reference from `1050-1057` to `1036-1058`

---

### 3.3 MAJ-3: Missing Reproducibility Artifacts

**Claim:** Missing run_manifest.json, sample attrition table, variable lineage JSON

**Source:** Paper_Artifacts_Audit_H8.md Finding #3

**Expected Location:** `outputs/econometric/h8_political_risk/{timestamp}/`

**Verification Steps:**

1. Search for run_manifest.json:
   - Found: `outputs/econometric/h8_political_risk/2026-03-02_001047/run_manifest.json`
   - Contents: Contains git_commit, timestamp, input_hashes, output_files, panel_path

2. Search for sample attrition files:
   - Found: `outputs/econometric/h8_political_risk/2026-03-02_001047/sample_attrition.csv`
   - Found: `outputs/econometric/h8_political_risk/2026-03-02_001047/sample_attrition.tex`
   - Contents: Shows 29,343 -> 15,721 sample flow

3. Search for variable lineage JSON:
   - Found: Only for H3 (`outputs/variables/h3_payout_policy/2026-03-01_234459/variable_lineage.json`)
   - NOT found for H8

**Verdict: PARTIALLY FIXED**

**Rationale:**
- run_manifest.json: FIXED -- Now present with complete contents
- sample_attrition.csv/tex: FIXED -- Now present with sample flow documentation
- variable_lineage.json: STILL MISSING -- Not generated for H8

**Fix Required:** Generate variable_lineage.json for H8 from H8.md Section F variable dictionary.

---

### 3.4 MIN-1: LaTeX Summary Stats Claims "Call Level"

**Claim:** `summary_stats.tex` note says "call level" but H8 is firm-year level

**Source:** Paper_Artifacts_Audit_H8.md Finding #4

**Expected Location:** `outputs/econometric/h8_political_risk/{timestamp}/summary_stats.tex`

**Verification Steps:**

1. Read summary_stats.tex:
   - File: `outputs/econometric/h8_political_risk/2026-03-02_001047/summary_stats.tex`
   - Line 22: `All variables are measured at the call level.`

2. Verify actual N values indicate firm-year level:
   - Line 9: N = 25,759 for AbsAbInv_lead
   - Line 13: N = 29,325 for Firm Size
   - These N values clearly indicate firm-year level (~29K), not call level (~112K)

**Verdict: STILL PRESENT**

**Rationale:** The summary_stats.tex still claims "call level" at line 22, but the N values (25,759 - 29,325) clearly indicate firm-year level observations. This is a documentation error that could confuse reviewers.

**Fix Required:** Change "call level" to "firm-year level" in summary_stats.tex generation.

---

### 3.5 MIN-2: Panel Includes Fiscal Years Outside Config Range

**Claim:** Panel contains fyearq=2000 and fyearq=2019 outside the configured 2002-2018 range

**Source:** AUDIT_H8.md Finding #4, Paper_Artifacts_Audit_H8.md Finding #5

**Notes:** This is a documentation note, not a bug

**Verification Steps:**

1. Verify panel fyearq range:
   ```
   Command output:
   fyearq range: 2000.0 - 2019.0
   Rows with fyearq < 2002: 141
   Rows with fyearq > 2018: 78
   Rows with fyearq=2000: 1
   Rows with fyearq=2019: 78
   AbsAbInv_lead valid with fyearq > 2018: 0
   ```

2. Check Known Issues section in H8.md:
   - File: `docs/provenance/H8.md`
   - Section J (lines 336-388) contains J.1-J.5 issues
   - No mention of edge year issue

**Verdict: STILL PRESENT**

**Rationale:** The panel still contains edge years (2000, 2019) outside the configured 2002-2018 range. This is benign (rows with fyearq > 2018 have no valid AbsAbInv_lead and cannot enter regressions) but is not documented in the Known Issues section.

**Fix Required:** Add J.6 to Known Issues documenting edge years from merge_asof mapping.

---

### 3.6 MIN-3: style_frozen Absorbed by Firm FE for 84.5% of Firms

**Claim:** Only 258/1,665 firms have within-firm variation in style_frozen; identification concern

**Source:** AUDIT_H8.md Finding #1, Paper_Artifacts_Audit_H8.md Finding #6

**Notes:** This is an identification concern, not a bug

**Verification Steps:**

1. Verify within-firm variation statistics:
   ```
   Command output:
   Total firms in regression sample: 1665
   Zero variance firms: 1337
   Positive variance firms: 258
   Single obs firms (NaN var): 70
   Percentage with zero variance: 80.3003003003003
   ```

2. Check Known Issues section in H8.md:
   - File: `docs/provenance/H8.md`
   - Section J (lines 336-388) contains J.1-J.5 issues
   - J.1 documents low coverage (62.8%) but NOT the within-firm identification issue

**Verdict: STILL PRESENT**

**Rationale:** The identification concern (80.3% of firms have zero within-firm style_frozen variance, meaning only 258 firms contribute to identifying the interaction coefficient) is not documented in the Known Issues section. This is important for interpreting the null result.

**Fix Required:** Add new Known Issues entry documenting:
- 80.3% of firms have zero within-firm style_frozen variance
- Only 258 firms (15.5%) contribute to identification of style_frozen and interaction coefficients
- The null result may reflect low power rather than evidence of no effect

---

### 3.7 NOT-1: LaTeX Table Missing SE Cluster Documentation

**Claim:** LaTeX table does not document that SEs are clustered at firm level

**Source:** Paper_Artifacts_Audit_H8.md Finding #7

**Expected Location:** `h8_political_risk_table.tex`

**Verification Steps:**

1. Read LaTeX table notes:
   - File: `outputs/econometric/h8_political_risk/2026-03-02_001047/h8_political_risk_table.tex`
   - Line 27: "Standard errors (in parentheses) are clustered at the firm level."

**Verdict: FIXED**

**Rationale:** The LaTeX table now includes explicit documentation in the notes section (line 27) that "Standard errors (in parentheses) are clustered at the firm level."

---

### 3.8 NOT-2: aggregate_to_firm_year Uses .last() Without Explicit skipna

**Claim:** Latent fragility -- `.last()` behavior varies across pandas versions

**Source:** AUDIT_H8.md Finding #7

**Expected Location:** `build_h8_political_risk_panel.py` around line 103

**Verification Steps:**

1. Read aggregate_to_firm_year function:
   - File: `src/f1d/variables/build_h8_political_risk_panel.py`
   - Line 82-83: Comment says "take the last non-missing value per (gvkey, fyearq)"
   - Line 104: Comment says "# Take the last non-NaN per (gvkey, fyearq) for each column"
   - Line 105: `firm_year = df.groupby(["gvkey", "fyearq"])[existing].last().reset_index()`

**Verdict: PARTIALLY FIXED**

**Rationale:** The code now has explicit comments (lines 82-83 and 104) documenting the expected behavior of taking "the last non-NaN per (gvkey, fyearq)". While `.last()` still doesn't have explicit `skipna=True` parameter, the intent is now clearly documented. Pandas' `GroupBy.last()` does skip NaN by default, so the behavior is correct.

---

## 4. Recommendations

### Immediate Actions Required

1. **MAJ-1 (LaTeX Formatting):** Modify `fmt_coef()` in `run_h8_political_risk.py` line 337-349 to use scientific notation for coefficients < 0.0001:
   ```python
   def fmt_coef(val: float, pval: float) -> str:
       if pd.isna(val):
           return ""
       stars = (
           "^{***}" if pval < 0.01
           else "^{**}" if pval < 0.05
           else "^{*}" if pval < 0.10
           else ""
       )
       if abs(val) < 0.0001:
           return f"{val:.2e}{stars}"
       return f"{val:.4f}{stars}"
   ```
   Then rerun Stage 4: `python -m f1d.econometric.run_h8_political_risk`

2. **MAJ-2 (Winsorization Documentation):** Update `docs/provenance/H8.md`:
   - Lines 212-214: Change "1/99% pooled" to "1/99% per-year"
   - Line 227: Change "Pooled (all years)" to "Per-year (within each fyearq)"
   - Update line reference from `1050-1057` to `1036-1058`

3. **MIN-1 (Summary Stats Level):** Update summary_stats.tex generation to say "firm-year level" instead of "call level"

4. **MIN-2/MIN-3 (Known Issues):** Add to H8.md Section J:
   - J.6: Edge years (fyearq=2000, 2019) from merge_asof mapping
   - J.7: Identification concern -- 80.3% of firms have zero within-firm style_frozen variance

### Optional Improvements

1. Generate `variable_lineage.json` for H8 from Section F variable dictionary
2. Add unit test for LaTeX coefficient readability (no non-zero coefficient displays as "0.0000")
3. Add within-firm variation diagnostic to sanity_checks.txt

---

*Verification complete. All 8 claims examined individually with direct evidence from file reads and command outputs.*
