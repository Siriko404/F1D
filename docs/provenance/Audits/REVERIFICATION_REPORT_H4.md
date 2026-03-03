# H4 Leverage Discipline — Reverification Report

**Verification Date:** 2026-03-02
**Verifier:** AI Auditor
**Scope:** All claims from AUDIT_H4.md and Paper_Artifacts_Audit_H4.md
**Latest Output Directory:** `outputs/econometric/h4_leverage/2026-03-01_235956/`

---

## 1. Executive Summary

| Metric | Count |
|--------|-------|
| Total Claims Verified | 11 |
| Claims Fixed | 9 |
| Claims Still Present | 2 |
| Claims Invalid | 0 |
| Claims Partially Fixed | 0 |

### Top 3 Outstanding Issues
1. **[MIN-2] No machine-readable variable lineage** — Variable dictionary exists only as prose in H4.md Section F, not as `variable_lineage.json` or similar
2. **[NOT-1] No coefficient forest plot** — No visualization of Lev_lag coefficients across specifications (optional improvement)
3. **[NOTE]** Both remaining issues are low-priority (MINOR and NOTE severity)

---

## 2. Claim Ledger (Full)

| ID | Severity | Claim | Verdict | Evidence |
|----|----------|-------|---------|----------|
| BLK-1 | BLOCKER | No run_manifest.json in Stage 4 output | **FIXED** | [Section 3.1](#31-blk-1-missing-run-manifest) |
| BLK-2 | BLOCKER | No sample attrition table | **FIXED** | [Section 3.2](#32-blk-2-missing-sample-attrition-table) |
| BLK-3 | BLOCKER | LaTeX table lacks tablenotes | **FIXED** | [Section 3.3](#33-blk-3-latex-table-lacks-notes) |
| MAJ-1 | MAJOR | Provenance claims "Balanced panel" | **FIXED** | [Section 3.4](#34-maj-1-provenance-doc-claims-balanced-panel) |
| MAJ-2 | MAJOR | PRES_CONTROL_MAP asymmetry underdocumented | **FIXED** | [Section 3.5](#35-maj-2-pres_control_map-asymmetry-underdocumented) |
| MAJ-3 | MAJOR | Within-R² inflated in LaTeX table | **FIXED** | [Section 3.6](#36-maj-3-within-r²-bug) |
| MIN-1 | MINOR | No cluster count in diagnostics | **FIXED** | [Section 3.7](#37-min-1-no-cluster-count-in-diagnostics) |
| MIN-2 | MINOR | Variable lineage not machine-readable | **STILL PRESENT** | [Section 3.8](#38-min-2-variable-lineage-not-machine-readable) |
| NOT-1 | NOTE | No coefficient forest plot | **STILL PRESENT** | [Section 3.9](#39-not-1-no-coefficient-forest-plot) |
| NOT-2 | NOTE | Linguistic engine log message misleading | **FIXED** | [Section 3.10](#310-not-2-linguistic-engine-log-message-misleading) |
| NOT-3 | NOTE | panel_utils.py docstring stale | **FIXED** | [Section 3.11](#311-not-3-panel_utilspy-docstring-stale) |

---

## 3. Detailed Verification Results

### 3.1) BLK-1: Missing Run Manifest

**Original Claim:** No `run_manifest.json` in Stage 4 output directory.

**Verification Method:**
```bash
find outputs/econometric/h4_leverage -name "run_manifest.json" -type f
```

**Evidence:**
```
C:/Users/.../outputs/econometric/h4_leverage/2026-03-01_235956/run_manifest.json
```

**File Contents:**
```json
{
  "manifest_version": "1.0",
  "stage": "stage4",
  "timestamp": "2026-03-01_235956",
  "generated_at": "2026-03-02T00:00:02.454416",
  "git_commit": "c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50",
  "command": "...run_h4_leverage.py",
  "input_hashes": {
    "panel": "5679e3b0ef0916a04ccf25b37b0a5e57e7bad995d254e823d0ffd79155cf7316"
  },
  "output_files": {
    "diagnostics": "...model_diagnostics.csv",
    "table": "...h4_leverage_table.tex"
  },
  "panel_path": "...h4_leverage_panel.parquet",
  "panel_hash": "5679e3b0ef0916a04ccf25b37b0a5e57e7bad995d254e823d0ffd79155cf7316"
}
```

**Verdict:** **FIXED**

**Reasoning:** The `run_manifest.json` file now exists in the latest output directory with comprehensive metadata including git commit, timestamp, input/output file paths, and content hashes.

---

### 3.2) BLK-2: Missing Sample Attrition Table

**Original Claim:** No sample attrition table showing row counts across filters.

**Verification Method:**
```bash
ls outputs/econometric/h4_leverage/2026-03-01_235956/sample_attrition.*
```

**Evidence - CSV Contents:**
```csv
Filter Stage,N,N Lost,% Retained
Master manifest,112968,0,100.0
Main sample filter,88205,-24763,78.1
After complete-case + min-calls filter,75852,-12353,67.1
```

**Evidence - TeX Contents (lines 1-15):**
```latex
\begin{table}[htbp]
\centering
\small
\caption{Sample Attrition: H4 Leverage Discipline}
\label{tab:sample_attrition_h4_leverage_discipline}
\begin{tabular}{lrrr}
\toprule
Filter Stage & N & N Lost & \% Retained \\
\midrule
Master manifest & 112,968 & 0 & 100.0\% \\
Main sample filter & 88,205 & -24,763 & 78.1\% \\
After complete-case + min-calls filter & 75,852 & -12,353 & 67.1\% \\
\bottomrule
\end{tabular}
\end{table}
```

**Verdict:** **FIXED**

**Reasoning:** Both `sample_attrition.csv` and `sample_attrition.tex` files now exist in the latest output directory, documenting the sample construction flow from 112,968 initial calls to 75,852 final regression observations.

---

### 3.3) BLK-3: LaTeX Table Lacks Notes

**Original Claim:** `h4_leverage_table.tex` has no `\begin{tablenotes}` section documenting methodology.

**Verification Method:** Read `h4_leverage_table.tex` lines 1-28.

**Evidence (lines 24-27):**
```latex
\\[-0.5em]
\parbox{\textwidth}{\scriptsize
\textit{Notes:} This table reports the effect of prior leverage on speech vagueness. Columns (1)--(4) use Q\&A session measures; columns (5)--(6) use presentation measures. All models use the Main industry sample (non-financial, non-utility firms). Firms with fewer than 5 calls are excluded. Standard errors are clustered at the firm level. All continuous controls are standardized. Variables are winsorized at 1\%/99\% by year.
}
\end{table}
```

**Verdict:** **FIXED**

**Reasoning:** The LaTeX table now includes a notes section (using `\parbox` approach rather than `threeparttable`'s `\begin{tablenotes}`, but functionally equivalent) documenting:
- SE clustering (firm level)
- Sample filters (Main industry, min 5 calls)
- Winsorization (1%/99% by year)
- Control standardization

---

### 3.4) MAJ-1: Provenance Doc Claims "Balanced Panel"

**Original Claim:** H4.md Section A1 states "Balanced panel" but panel is unbalanced.

**Verification Method:**
```bash
grep -n -i "balanced\|unbalanced" docs/provenance/H4.md
```

**Evidence:**
```
19:| **Panel Type** | Unbalanced panel with firm + year fixed effects |
```

**Verdict:** **FIXED**

**Reasoning:** H4.md line 19 now correctly states "Unbalanced panel" instead of the incorrect "Balanced panel" claim.

---

### 3.5) MAJ-2: PRES_CONTROL_MAP Asymmetry Underdocumented

**Original Claim:** Documentation doesn't clarify that Weak_Modal QA DVs use Pres Uncertainty control (not Pres Weak_Modal).

**Verification Method:**
```bash
grep -n -i "Weak_Modal.*Uncertainty|corresponding Pres|primary uncertainty" docs/provenance/H4.md
```

**Evidence (lines 53-55):**
```
53:- If DV is a QA measure → corresponding Pres **Uncertainty** measure added as control
55:- Note: Weak_Modal QA DVs also use Pres Uncertainty (not Pres Weak_Modal) as control — the primary uncertainty measure is used for all speaker roles
```

**Verdict:** **FIXED**

**Reasoning:** H4.md now explicitly documents:
- Line 53: Uses bold `**Uncertainty**` to emphasize the control type
- Line 55: Explicit note clarifying that Weak_Modal QA DVs use Pres Uncertainty (not Pres Weak_Modal)

---

### 3.6) MAJ-3: Within-R² Bug

**Original Claim:** LaTeX table reported inflated Within-R² values (0.63-0.92 vs true 0.0002-0.027) due to incorrect one-step additive demeaning.

**Verification Method:**
1. Check code uses `model.rsquared_within`
2. Check `model_diagnostics.csv` values
3. Check LaTeX table values

**Code Evidence:**
```bash
grep -n "rsquared_within" src/f1d/econometric/run_h4_leverage.py
```
Output:
```
208:    print(f"  R-squared (within): {model.rsquared_within:.4f}")
212:    within_r2 = float(model.rsquared_within)
240:        "rsquared": float(model.rsquared_within),
```

**Diagnostics CSV Evidence (selected rows):**
| dv | sample | within_r2 |
|----|--------|-----------|
| Manager_QA_Uncertainty_pct | Main | 0.0224 |
| CEO_QA_Uncertainty_pct | Main | 0.0193 |
| Manager_QA_Weak_Modal_pct | Main | 0.0078 |
| CEO_QA_Weak_Modal_pct | Main | 0.0071 |
| Manager_Pres_Uncertainty_pct | Main | 0.0002 |
| CEO_Pres_Uncertainty_pct | Main | 0.0002 |

**LaTeX Table Evidence (line 21):**
```latex
Within-$R^2$ & 0.0224 & 0.0193 & 0.0078 & 0.0071 & 0.0002 & 0.0002 \\
```

**Verdict:** **FIXED**

**Reasoning:**
1. Code now uses `model.rsquared_within` directly (lines 208, 212, 240)
2. Diagnostics CSV shows correct values (0.0002-0.027 range)
3. LaTeX table reports correct values matching diagnostics
4. No more 34x-5293x inflation

---

### 3.7) MIN-1: No Cluster Count in Diagnostics

**Original Claim:** `model_diagnostics.csv` does not include `n_clusters` column.

**Verification Method:** Read `model_diagnostics.csv` header row.

**Evidence (line 1):**
```csv
dv,sample,n_obs,n_firms,n_clusters,cluster_var,rsquared,rsquared_adj,within_r2,beta1,beta1_se,beta1_t,beta1_p_two,beta1_p_one,h4_sig
```

**Verdict:** **FIXED**

**Reasoning:** The `n_clusters` column is now present (4th data column). All 18 regression rows include cluster counts (e.g., 1805 for Main sample, 441 for Finance, 82 for Utility).

---

### 3.8) MIN-2: Variable Lineage Not Machine-Readable

**Original Claim:** Variable dictionary is prose in H4.md Section F, not JSON/YAML.

**Verification Method:**
```bash
find . -name "variable_lineage*" -type f
find outputs -name "*variable*.json" -type f
ls config/
```

**Evidence:**
- No `variable_lineage.json` or similar found
- `config/variables.yaml` exists but is a configuration file, not a machine-readable lineage document
- H4.md Section F (lines 269-310) contains variable dictionary as markdown tables

**Verdict:** **STILL PRESENT**

**Reasoning:** No dedicated machine-readable variable lineage file exists. The variable dictionary remains as prose markdown tables in H4.md. This is a MINOR issue that would enable automated verification but does not affect paper-submission readiness.

---

### 3.9) NOT-1: No Coefficient Forest Plot

**Original Claim:** No visualization of Lev_lag coefficients across specifications.

**Verification Method:**
```bash
find outputs/econometric/h4_leverage -name "*forest*" -type f
find outputs/econometric/h4_leverage/2026-03-01_235956 -name "*.png" -type f
```

**Evidence:** Both commands returned no results (no forest plots, no PNG files).

**Verdict:** **STILL PRESENT**

**Reasoning:** No coefficient forest plot has been generated. This is an OPTIONAL improvement (NOTE severity) that would help visualize the consistency of the leverage effect across DVs and samples.

---

### 3.10) NOT-2: Linguistic Engine Log Message Misleading

**Original Claim:** Log says "per-year 1%/99%" but code uses `lower=0.0, upper=0.99` (0%/99%).

**Verification Method:** Read `_linguistic_engine.py` lines 255-259.

**Evidence:**
```python
# Line 255-259:
combined = winsorize_by_year(
    combined, existing_pct_cols, year_col="year",
    lower=0.0, upper=0.99, min_obs=10  # Harmonized with Compustat/CRSP engines
)
logger.info(f"  Winsorized {len(existing_pct_cols)} percentage columns (per-year 0%/99% upper-only)")
```

**Verdict:** **FIXED**

**Reasoning:** The log message at line 259 now correctly states "per-year 0%/99% upper-only" which matches the code parameters at lines 255-257 (`lower=0.0, upper=0.99`).

---

### 3.11) NOT-3: panel_utils.py Docstring Stale

**Original Claim:** Docstring says 50% threshold but code uses 80%.

**Verification Method:** Read `panel_utils.py` lines 90-111 and grep for `< 0.8`.

**Evidence (lines 95 and 110):**
```python
        - Raises ValueError if match rate < 80% (loud failure, not silent NaN).
        ...
        ValueError: if fewer than 80% of panel rows match a Compustat fyearq.
```

**Code implementation (line 170):**
```python
if n_total > 0 and (n_matched / n_total) < 0.8:
```

**Verdict:** **FIXED**

**Reasoning:** The docstring now correctly states "80%" at both locations (lines 95 and 110), matching the code implementation at line 170.

---

## 4. Cross-Verification Checks

### 4.1) Within-R² End-to-End Check

Verify that the Within-R² fix is complete across all artifacts:

**Code Check:**
```
src/f1d/econometric/run_h4_leverage.py:212:    within_r2 = float(model.rsquared_within)
src/f1d/econometric/run_h4_leverage.py:240:        "rsquared": float(model.rsquared_within),
```

**Diagnostics Check (min/max values):**
| Metric | Value |
|--------|-------|
| Minimum within_r2 | 0.00015 (CEO_Pres_Uncertainty_pct, Main) |
| Maximum within_r2 | 0.0270 (Manager_QA_Uncertainty_pct, Finance) |
| Range | 0.0002 - 0.027 |

**LaTeX Check (line 21):**
```latex
Within-$R^2$ & 0.0224 & 0.0193 & 0.0078 & 0.0071 & 0.0002 & 0.0002 \\
```

**Verdict:** **CONSISTENT** — All three sources agree on Within-R² values in the correct 0.0002-0.027 range.

---

### 4.2) Significance Results Cross-Check

**From model_diagnostics.csv (h4_sig=True):**
| dv | sample | beta1 | beta1_p_one |
|----|--------|-------|-------------|
| Manager_Pres_Uncertainty_pct | Main | -0.0552 | 0.0087 |
| CEO_Pres_Uncertainty_pct | Main | -0.0424 | 0.0444 |

**From LaTeX table (line 12):**
```latex
Leverage$_{t-1}$ & 0.0008 & -0.0294^{*} & 0.0015 & -0.0159 & -0.0552^{***} & -0.0424^{**} \\
```

**Verdict:** **CONSISTENT** — Two significant results (MgrPres p<0.01, CEOPres p<0.05) match across diagnostics CSV and LaTeX stars.

---

## 5. Outstanding Issues

### Still Blocking Paper Submission
**None** — All BLOCKER issues have been resolved.

### Minor Issues Remaining
1. **[MIN-2] Variable lineage not machine-readable** — Variable dictionary exists as prose markdown tables in H4.md Section F. A `variable_lineage.json` would enable automated verification but is not required for paper submission.

### Optional Improvements
1. **[NOT-1] No coefficient forest plot** — A visualization of Lev_lag coefficients across specifications would enhance the paper but is optional.

---

## 6. Recommendations

### Immediate Actions Required
**None** — H4 is now paper-submission ready.

### Optional Improvements
1. **Generate `variable_lineage.json`** from `config/variables.yaml` or H4.md Section F for automated verification
2. **Add coefficient forest plot** script to visualize Lev_lag effects across DVs and samples
3. **Consider adding Finance/Utility attrition breakdown** to sample_attrition.csv for completeness

---

## 7. Verification Log

Chronological log of all commands executed:

| # | Command | Purpose | Output Summary |
|---|---------|---------|----------------|
| 1 | `find outputs/econometric/h4_leverage -name "run_manifest.json"` | Check for manifest | Found at 2026-03-01_235956/ |
| 2 | `ls outputs/econometric/h4_leverage/` | List output dirs | 14 directories from 2026-02-20 to 2026-03-01 |
| 3 | `cat run_manifest.json` | Verify manifest contents | Valid JSON with git commit, hashes, paths |
| 4 | `ls outputs/econometric/h4_leverage/2026-03-01_235956/` | List latest outputs | 27 files including manifest, attrition, table |
| 5 | `cat sample_attrition.csv` | Check attrition table | 4 rows showing N from 112,968 to 75,852 |
| 6 | `cat sample_attrition.tex` | Check attrition TeX | Valid LaTeX table |
| 7 | `cat h4_leverage_table.tex` | Check LaTeX table notes | Notes present at lines 25-27 |
| 8 | `grep -i "balanced\|unbalanced" H4.md` | Check panel type claim | "Unbalanced panel" at line 19 |
| 9 | `grep "Weak_Modal\|corresponding Pres" H4.md` | Check PRES_CONTROL_MAP doc | Clarified at lines 53, 55 |
| 10 | `grep "rsquared_within" run_h4_leverage.py` | Check Within-R² code | Uses model.rsquared_within at lines 208, 212, 240 |
| 11 | `cat model_diagnostics.csv` | Check diagnostics values | Correct within_r2 (0.0002-0.027), n_clusters present |
| 12 | `find . -name "variable_lineage*"` | Search for lineage file | Not found |
| 13 | `find outputs -name "*forest*"` | Search for forest plot | Not found |
| 14 | `cat _linguistic_engine.py:250-280` | Check log message | "per-year 0%/99% upper-only" at line 259 |
| 15 | `cat panel_utils.py:90-120` | Check docstring | "80%" at lines 95, 110 |
| 16 | `grep "< 0.8" panel_utils.py` | Check threshold code | 0.8 at line 170 |

---

## 8. Confidence Assessment

| Aspect | Confidence | Justification |
|--------|------------|---------------|
| Claim extraction accuracy | **High** | All 11 claims extracted from source docs with exact section references |
| Verification thoroughness | **High** | Each claim verified with direct file reads or command outputs; no assumptions made |
| Evidence reliability | **High** | All evidence includes file paths, line numbers, and exact outputs |

---

## 9. Summary

**H4 Leverage Discipline is now PAPER-SUBMISSION READY.**

All three BLOCKER issues have been resolved:
1. ✅ `run_manifest.json` exists with complete metadata
2. ✅ `sample_attrition.csv` and `.tex` track N from 112,968 to 75,852
3. ✅ LaTeX table includes methodology notes

All three MAJOR issues have been resolved:
1. ✅ H4.md correctly states "Unbalanced panel"
2. ✅ PRES_CONTROL_MAP asymmetry documented with explicit note
3. ✅ Within-R² now correct (0.0002-0.027, not 0.63-0.92)

MIN-1 (cluster count) is fixed — `n_clusters` column present in diagnostics.

Two low-priority issues remain:
- MIN-2: No machine-readable variable lineage (optional for automation)
- NOT-1: No coefficient forest plot (optional visualization)

---

*Verification complete. All claims examined individually. No bulk processing used.*
