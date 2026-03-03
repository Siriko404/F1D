# Re-Verification Audit Report: Suite H2

**Date:** 2026-03-02
**Auditor:** Claude Opus 4.6 (GLM-5)
**Input Documents:** H2.md, AUDIT_H2.md, Paper_Artifacts_Audit_H2.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H2.md

---

## Executive Summary

| Total Issues Verified | Confirmed Fixed | Confirmed Not Fixed | New Issues Found | Unverifiable |
|-----------------------|-----------------|---------------------|------------------|--------------|
| 5 | 4 | 0 | 0 | 1 |

### Overall Assessment

The H2 suite has been substantially hardened since the initial audits. Four of five identified issues have been confirmed fixed: (1) Within-R2 inflation in LaTeX tables, (2) README DV notation ambiguity, (3) Missing run manifests, and (4) Missing sample attrition tables. The remaining issue (stale merge_asof matches) was documented as accepted behavior and remains in that state. Cross-artifact consistency has been verified across raw PanelOLS output, model_diagnostics.csv, and LaTeX tables. The core hypothesis results (H2a: 0/18 significant, H2b: 1/18 significant) are correctly computed and consistently reported.

---

## Claim Ledger

| ID | Severity | Claim | Fix Location | Audit Status Claimed | Re-Verification Status |
|----|----------|-------|--------------|---------------------|------------------------|
| H2-001 | ~~MAJOR~~ | LaTeX within-R2 inflated via B8 custom | `run_h2_investment.py` lines 373, 428-430, 582-584 | CLAIMED FIXED | **CONFIRMED FIXED** |
| H2-002 | MAJOR | README DV notation ambiguous | `README.md` line 385 | CLAIMED FIXED | **CONFIRMED FIXED** |
| H2-003 | MAJOR | Missing run_manifest.json | Stage 3 + Stage 4 output directories | CLAIMS NOT FIXED | **CONFIRMED FIXED** |
| H2-004 | MINOR | Stale merge_asof matches | `panel_utils.py` attach_fyearq() | DOCUMENTED (no fix needed) | **CONFIRMED DOCUMENTED** |
| H2-005 | NOTE | Missing sample attrition table | Stage 4 script | CLAIMS NOT FIXED | **CONFIRMED FIXED** |

---

## Verification Results

### H2-001: Within-R2 Inflation

**Claimed Status:** FIXED
**Verification Steps:**
1. Read `run_h2_investment.py` lines 570-615 to examine LaTeX table generator
2. Searched for `within_r2` and `rsquared` patterns in code
3. Read model_diagnostics.csv to compare column values
4. Read raw PanelOLS output to verify true within-R2
5. Read LaTeX table to verify reported values

**Evidence:**

*Code Implementation (lines 373-374, 428-430):*
```python
# Line 373-374:
within_r2 = float(model.rsquared_within)
print(f"  Within-R2: {within_r2:.4f}")

# Lines 428-430:
"rsquared": float(model.rsquared_within),
"rsquared_adj": float(model.rsquared_inclusive),
"within_r2": within_r2,  # B8 fix: within-R2 for LaTeX table
```

*model_diagnostics.csv values (latest run 2026-03-01_234421):*
```
Main/Manager_QA_Uncertainty_pct: rsquared=0.0503, within_r2=0.0503, diff=0.0000
Main/CEO_QA_Uncertainty_pct: rsquared=0.0524, within_r2=0.0524, diff=0.0000
Main/Manager_QA_Weak_Modal_pct: rsquared=0.0501, within_r2=0.0501, diff=0.0000
```

*Raw PanelOLS output (regression_results_Main_Manager_QA_Uncertainty_pct.txt line 5):*
```
R-squared (Within):               0.0503
```

*LaTeX table (h2_investment_table.tex line 17):*
```
Within-R$^2$ & 0.050 & 0.052 & 0.050 & 0.052 & 0.050 & 0.052 \\
```

*Verification command:*
```bash
grep -n "fitted_values|y_hat|y_pred|ss_res|ss_tot" src/f1d/econometric/run_h2_investment.py
# Output: No matches found (B8 custom block removed)
```

**Verdict:** **CONFIRMED FIXED**

**Rationale:** The B8 custom within-R2 computation block has been removed from the code. Both `rsquared` and `within_r2` now derive from `model.rsquared_within` and are identical. LaTeX table values (0.050) match PanelOLS raw output (0.0503) to 3 decimal places.

---

### H2-002: README DV Notation

**Claimed Status:** NOT FIXED (per Paper_Artifacts_Audit_H2.md)
**Verification Steps:**
1. Read README.md lines 380-395 for H2 DV specification
2. Searched for "InvestmentResidual" in README
3. Verified InvestmentResidual_lead distribution in panel data

**Evidence:**

*README.md line 385:*
```
DV: `InvestmentResidual_{t+1}` (Biddle et al. 2009; >0=overinvestment, <0=underinvestment).
```

*No absolute value notation (`|...|`) present.*

*InvestmentResidual_lead distribution (verified via Python):*
```
Total valid: 101,923
Mean: -0.0174
Min: -0.4539
Max: 1.4854
% negative: 72.0%
% positive: 28.0%
```

*Code search for abs() in panel builder:*
```bash
grep -n "abs\|InvestmentResidual" src/f1d/variables/build_h2_investment_panel.py | head -20
# Result: No abs() function calls on InvestmentResidual
```

**Verdict:** **CONFIRMED FIXED**

**Rationale:** The README now correctly shows `InvestmentResidual_{t+1}` without the absolute value notation. The code confirms the signed residual is used (72% negative values). The description ">0=overinvestment, <0=underinvestment" accurately reflects the implementation.

---

### H2-003: Missing Run Manifest

**Claimed Status:** NOT FIXED (per Paper_Artifacts_Audit_H2.md)
**Verification Steps:**
1. Searched for run_manifest.json in Stage 3 outputs
2. Searched for run_manifest.json in Stage 4 outputs
3. Read manifest contents to verify structure

**Evidence:**

*Stage 3 manifest found:*
```
outputs/variables/h2_investment/2026-03-01_234258/run_manifest.json
```

*Stage 3 manifest contents:*
```json
{
  "manifest_version": "1.0",
  "stage": "stage3",
  "timestamp": "2026-03-01_234258",
  "generated_at": "2026-03-01T23:44:05.452890",
  "git_commit": "c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50",
  "command": "C:\\...\\build_h2_investment_panel.py",
  "input_hashes": {
    "master_manifest": null
  },
  "output_files": {
    "panel": "C:\\...\\h2_investment_panel.parquet",
    "summary_stats": "C:\\...\\summary_stats.csv"
  },
  "config": {}
}
```

*Stage 4 manifest found:*
```
outputs/econometric/h2_investment/2026-03-01_234421/run_manifest.json
```

*Stage 4 manifest contents:*
```json
{
  "manifest_version": "1.0",
  "stage": "stage4",
  "timestamp": "2026-03-01_234421",
  "generated_at": "2026-03-01T23:44:26.071152",
  "git_commit": "c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50",
  "command": "C:\\...\\run_h2_investment.py",
  "input_hashes": {
    "panel": "a71a02c9a9d6094af90e7e22667f57eebe476479184a14bc7ab6447ba4d7602a"
  },
  "output_files": {
    "diagnostics": "C:\\...\\model_diagnostics.csv",
    "table": "C:\\...\\h2_investment_table.tex"
  },
  "config": {},
  "panel_path": "C:\\...\\h2_investment_panel.parquet",
  "panel_hash": "a71a02c9a9d6094af90e7e22667f57eebe476479184a14bc7ab6447ba4d7602a"
}
```

**Verdict:** **CONFIRMED FIXED**

**Rationale:** Both Stage 3 and Stage 4 now generate `run_manifest.json` files with complete provenance information including git commit hash, command, input hashes, and output file paths. This exceeds the minimum requirements specified in the original audit.

---

### H2-004: Stale merge_asof Matches

**Claimed Status:** DOCUMENTED (no fix needed)
**Verification Steps:**
1. Verified stale matches still exist in latest panel
2. Checked for tolerance parameter in panel_utils.py

**Evidence:**

*Stale match count (Python verification):*
```
Stale matches: 78 (0.07%)
Unique firms with stale: 6
Stale with valid lead: 0

Examples of stale matches:
  gvkey=003087, start=2017-04-14, fyearq=2007, gap=10y
  gvkey=065142, start=2017-05-04, fyearq=2010, gap=7y
  gvkey=009589, start=2017-05-12, fyearq=2006, gap=11y
```

*Tolerance parameter check:*
```bash
grep -n "tolerance|max_gap|days" src/f1d/shared/variables/panel_utils.py
# Output: No matches found
```

**Verdict:** **CONFIRMED DOCUMENTED**

**Rationale:** Stale matches persist as documented in the original audit. The count (78), number of firms (6), and percentage (0.07%) match exactly. Critically, 0 stale matches have valid InvestmentResidual_lead values, so they remain excluded from regressions. No tolerance parameter has been added, which is consistent with the "documented, no fix needed" status.

---

### H2-005: Missing Sample Attrition Table

**Claimed Status:** NOT FIXED (per Paper_Artifacts_Audit_H2.md)
**Verification Steps:**
1. Searched for attrition files in Stage 3 and Stage 4 outputs
2. Read generated attrition files

**Evidence:*

*Files found:*
```
outputs/econometric/h2_investment/2026-03-01_234421/sample_attrition.csv
outputs/econometric/h2_investment/2026-03-01_234421/sample_attrition.tex
```

*sample_attrition.csv contents:*
```csv
Filter Stage,N,N Lost,% Retained
Master manifest,112968,0,100.0
Main sample filter,88205,-24763,78.1
After lead filter,79364,-8841,70.3
After complete-case + min-calls filter,74832,-4532,66.2
```

*sample_attrition.tex contents:*
```latex
\begin{table}[htbp]
\centering
\small
\caption{Sample Attrition: H2 Investment Efficiency}
\label{tab:sample_attrition_h2_investment_efficiency}
\begin{tabular}{lrrr}
\toprule
Filter Stage & N & N Lost & \% Retained \\
\midrule
Master manifest & 112,968 & 0 & 100.0\% \\
Main sample filter & 88,205 & -24,763 & 78.1\% \\
After lead filter & 79,364 & -8,841 & 70.3\% \\
After complete-case + min-calls filter & 74,832 & -4,532 & 66.2\% \\
\bottomrule
\end{tabular}
\end{table}
```

**Verdict:** **CONFIRMED FIXED**

**Rationale:** Sample attrition table is now generated in both CSV and LaTeX formats. The table shows complete filter drop-off from master manifest (112,968) to final regression sample (74,832), retaining 66.2% of observations.

---

## Additional Findings

No new issues discovered during verification. All checked items passed:

1. **Git history check:** Only one commit (86d2dda) modified H2 scripts since the audit date, adding logging improvements (TeeOutput class) without changing core functionality.

2. **Code-docstring standardization:** Commit 2a5312c standardized docstrings but did not alter regression logic.

3. **File completeness:** All expected artifacts present in latest run directory (2026-03-01_234421).

---

## Cross-Artifact Consistency Matrix

Regression: Main / Manager_QA_Uncertainty_pct

| Source | Field | Expected Value | Actual Value | Match? |
|--------|-------|----------------|--------------|--------|
| Raw .txt (line 25) | beta1 | -0.0029 | -0.0029 | YES |
| model_diagnostics.csv | beta1 | -0.002894 | -0.002894 | YES |
| LaTeX table (line 12) | beta1 coef | -0.0029 | -0.0029 | YES |
| Raw .txt (line 25) | beta1_SE | 0.0035 | 0.0035 | YES |
| LaTeX table (line 13) | (SE) | (0.0035) | (0.0035) | YES |
| Raw .txt (line 5) | N | 74,832 | 74,832 | YES |
| model_diagnostics.csv | n_obs | 74,832 | 74,832 | YES |
| LaTeX table (line 16) | N | 74,832 | 74,832 | YES |
| Raw .txt (line 5) | R2 (Within) | 0.0503 | 0.0503 | YES |
| model_diagnostics.csv | rsquared | 0.0503 | 0.0503 | YES |
| LaTeX table (line 17) | Within-R2 | 0.050 | 0.050 | YES |

All 11 consistency checks passed.

---

## Hypothesis Results Verification

| Metric | Expected (per H2.md) | Actual | Match? |
|--------|---------------------|--------|--------|
| H2a significant (beta1<0, p<0.05) | 0/18 | 0/18 | YES |
| H2b significant (beta3>0, p<0.05) | 1/18 | 1/18 | YES |
| H2b significant spec | Finance/CEO_QA_Weak_Modal | Finance/CEO_QA_Weak_Modal_pct | YES |
| H2b beta3 | ~0.025 | 0.0253 | YES |
| H2b p-value | ~0.037 | 0.037 | YES |

**Verification command:**
```bash
python -c "
import pandas as pd
from pathlib import Path
econ_dir = Path('outputs/econometric/h2_investment')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')
print(f'H2a significant: {diag[\"beta1_signif\"].sum()}/18')
print(f'H2b significant: {diag[\"beta3_signif\"].sum()}/18')
sig = diag[diag['beta3_signif'] == True]
for _, r in sig.iterrows():
    print(f\"  {r['sample']}/{r['uncertainty_var']}: beta3={r['beta3']:.4f}, p={r['beta3_p_one']:.3f}\")
"
```

**Output:**
```
H2a significant: 0/18
H2b significant: 1/18
  Finance/CEO_QA_Weak_Modal_pct: beta3=0.0253, p=0.037
```

---

## Recommendations

All MAJOR issues identified in the original audits have been resolved. Remaining recommendations are:

1. **H2-004 (Stale matches):** Consider adding a tolerance parameter to `attach_fyearq()` for explicit documentation, though this is optional since stale rows are already excluded from regressions.

2. **H2-Special (B8 block):** The custom within-R2 computation has been removed. Ensure other H-suites (H1, H3, H4, H5, H7) have been similarly updated if they used the same pattern.

3. **Cross-suite consistency:** The run_manifest.json implementation in H2 is exemplary and should be propagated to all other suites.

---

## Command Log

| # | Timestamp | Command | Purpose |
|---|-----------|---------|---------|
| 1 | 2026-03-02 | `Glob src/**/run_h2_investment.py` | Find H2 econometric script |
| 2 | 2026-03-02 | `Read run_h2_investment.py:600-700` | Examine LaTeX table generator |
| 3 | 2026-03-02 | `Grep within_r2\|rsquared run_h2_investment.py` | Find R2 usage patterns |
| 4 | 2026-03-02 | `Read run_h2_investment.py:570-620` | Check LaTeX R2 extraction |
| 5 | 2026-03-02 | `Read run_h2_investment.py:360-440` | Check meta dict construction |
| 6 | 2026-03-02 | `Grep fitted_values\|y_hat run_h2_investment.py` | Verify B8 block removed |
| 7 | 2026-03-02 | `ls -lt outputs/econometric/h2_investment/` | Find latest Stage 4 run |
| 8 | 2026-03-02 | `Python: model_diagnostics.csv columns` | Check rsquared/within_r2 values |
| 9 | 2026-03-02 | `grep Within-R outputs/*/h2_investment_table.tex` | Extract LaTeX R2 values |
| 10 | 2026-03-02 | `Read regression_results_Main_Manager_QA_Uncertainty_pct.txt` | Get raw PanelOLS output |
| 11 | 2026-03-02 | `sed -n '380,395p' README.md` | Check README DV notation |
| 12 | 2026-03-02 | `Grep InvestmentResidual README.md` | Search DV specification |
| 13 | 2026-03-02 | `Grep abs\|InvestmentResidual build_h2_investment_panel.py` | Verify signed residual |
| 14 | 2026-03-02 | `Python: InvestmentResidual_lead distribution` | Check for negative values |
| 15 | 2026-03-02 | `find outputs/variables/h2_investment -name run_manifest.json` | Check Stage 3 manifest |
| 16 | 2026-03-02 | `find outputs/econometric/h2_investment -name run_manifest.json` | Check Stage 4 manifest |
| 17 | 2026-03-02 | `Read run_manifest.json (Stage 3)` | Verify manifest contents |
| 18 | 2026-03-02 | `Read run_manifest.json (Stage 4)` | Verify manifest contents |
| 19 | 2026-03-02 | `Python: stale merge_asof check` | Verify stale match count |
| 20 | 2026-03-02 | `Grep tolerance\|max_gap panel_utils.py` | Check for tolerance parameter |
| 21 | 2026-03-02 | `find outputs -name *attrition*` | Check for attrition files |
| 22 | 2026-03-02 | `Read sample_attrition.csv` | Verify attrition table |
| 23 | 2026-03-02 | `Read sample_attrition.tex` | Verify LaTeX attrition |
| 24 | 2026-03-02 | `git log --since=2026-02-28 -- run_h2_investment.py` | Check code changes |
| 25 | 2026-03-02 | `git show 86d2dda --stat` | Review commit details |
| 26 | 2026-03-02 | `Python: hypothesis results verification` | Verify H2a/H2b counts |
| 27 | 2026-03-02 | `Read h2_investment_table.tex` | Cross-check LaTeX values |
| 28 | 2026-03-02 | `Grep InvestmentResidual\|SalesGrowth_lag _compustat_engine.py` | Verify Biddle implementation |
| 29 | 2026-03-02 | `Grep p_one\|p_two\|beta1\|beta3 run_h2_investment.py` | Verify one-tailed logic |

---

## Appendix: Raw Evidence

### A. model_diagnostics.csv Column Values (Main/Manager_QA_Uncertainty_pct)

```
Latest run: 2026-03-01_234421
Columns: ['sample', 'uncertainty_var', 'beta1', 'beta1_se', 'beta1_t', 'beta1_p_two',
          'beta1_p_one', 'beta1_signif', 'beta3', 'beta3_se', 'beta3_t', 'beta3_p_two',
          'beta3_p_one', 'beta3_signif', 'n_obs', 'n_firms', 'n_clusters', 'cluster_var',
          'rsquared', 'rsquared_adj', 'within_r2']

Main/Manager_QA_Uncertainty_pct: rsquared=0.0503, within_r2=0.0503, diff=0.0000
```

### B. Raw PanelOLS Output (regression_results_Main_Manager_QA_Uncertainty_pct.txt)

```
No. Observations:                    74832
R-squared (Within):               0.0503

Uncertainty          -0.0029     0.0035    -0.8223     0.4109
```

### C. LaTeX Table Excerpt (h2_investment_table.tex)

```latex
Uncertainty & -0.0029 & -0.0013 & -0.0008 & 0.0032 & 0.0018 & -0.0019 \\
 & (0.0035) & (0.0030) & (0.0057) & (0.0046) & (0.0043) & (0.0038) \\
N & 74,832 & 54,992 & 74,832 & 54,992 & 76,184 & 54,849 \\
Within-R$^2$ & 0.050 & 0.052 & 0.050 & 0.052 & 0.050 & 0.052 \\
```

### D. InvestmentResidual_lead Distribution

```
Total valid: 101,923
Mean: -0.0174
Min: -0.4539
Max: 1.4854
% negative: 72.0%
% positive: 28.0%
```

### E. Stale Match Examples

```
Stale matches: 78 (0.07%)
Unique firms with stale: 6
Stale with valid lead: 0

Examples:
  gvkey=003087, start=2017-04-14, fyearq=2007, gap=10y
  gvkey=065142, start=2017-05-04, fyearq=2010, gap=7y
  gvkey=009589, start=2017-05-12, fyearq=2006, gap=11y
```

---

*Audit completed: 2026-03-02*
*Pipeline version: F1D v6.0.0*
*Audited runs: Stage 3 2026-03-01_234258, Stage 4 2026-03-01_234421*
*Git HEAD: c9b00be*
