# PAPER ARTIFACTS AUDIT REPORT: H6 SEC Scrutiny (CCCL) and Speech Vagueness

**Suite ID:** H6
**Audit Date:** 2026-03-01
**Auditor:** Claude Code (AI Coding Assistant)
**Audit Protocol:** Paper_Ready_artifacts.txt

---

## 1) Executive Summary

**Is suite H6 paper-submission ready?** **NO** — Documentation artifacts require correction before submission.

| Verdict | Status | Notes |
|---------|--------|-------|
| **Presence verdict** | **Partial** | Core outputs present; missing run_manifest, attrition table, variable lineage JSON |
| **Quality verdict** | **Partial** | LaTeX/diagnostics match; README detailed table has incorrect values |
| **Top BLOCKERS** | 2 | (1) README table has wrong coefficients; (2) Pre-trends violations undocumented in paper-ready form |

### Top 3 Issues Requiring Action:
1. **BLOCKER:** README H6 detailed table (lines 469-474) has incorrect beta values — appears to show within-R² instead of coefficients
2. **MAJOR:** Pre-trends violations (7 significant leads) require explicit documentation in paper-ready summary
3. **MAJOR:** Missing reproducibility artifacts: no run_manifest.json, no attrition table, no variable lineage JSON

---

## 2) Suite & Run Identification

| Field | Value | Evidence Command |
|-------|-------|------------------|
| **Suite ID** | H6 | `docs/provenance/H6.md` |
| **Stage 3 Builder** | `src/f1d/variables/build_h6_cccl_panel.py` | File exists |
| **Stage 4 Runner** | `src/f1d/econometric/run_h6_cccl.py` | File exists |
| **Stage 3 Run ID** | `2026-02-27_224247` | `ls outputs/variables/h6_cccl/` |
| **Stage 4 Run ID** | `2026-02-28_230834` | `ls outputs/econometric/h6_cccl/` |
| **Stage 3 Panel Path** | `outputs/variables/h6_cccl/2026-02-27_224247/h6_cccl_panel.parquet` | 10.6 MB |
| **Stage 4 Output Path** | `outputs/econometric/h6_cccl/2026-02-28_230834/` | 46 files |
| **Git Commit (HEAD)** | `c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50` | `git rev-parse HEAD` |
| **Git Commit (from run)** | NOT CAPTURED | No run_manifest.json exists |

**Stage 3 → Stage 4 Linkage Verification:**
```python
from f1d.shared.path_utils import get_latest_output_dir
panel_dir = get_latest_output_dir('outputs/variables/h6_cccl', required_file='h6_cccl_panel.parquet')
# Returns: outputs\variables\h6_cccl\2026-02-27_224247
# Stage 4 (2026-02-28_230834) uses this panel via get_latest_output_dir()
```
**Status:** PASS — Stage 4 correctly references Stage 3 panel.

---

## 3) Estimator Family Detection

| Field | Value | Evidence |
|-------|-------|----------|
| **Model Family** | Panel OLS with Fixed Effects | `linearmodels.panel.PanelOLS` |
| **Estimator** | `PanelOLS.from_formula()` with `EntityEffects + TimeEffects` | `run_h6_cccl.py:199-201` |
| **Variance Estimator** | Firm-clustered SEs (`cov_type="clustered", cluster_entity=True`) | `run_h6_cccl.py:201` |
| **Within-transformation** | Yes — entity and time effects absorbed | `drop_absorbed=True` |
| **Software** | Python `linearmodels` v0.6.0+, `statsmodels` v0.14.6 | `requirements.txt` |

**Model-Specific Requirements (Panel FE):**
- Within-R²: Required ✓ (present in diagnostics and LaTeX)
- FE indicators: Required ✓ (noted in table)
- Cluster summary (# firms): Required ✓ (in diagnostics)
- N entities + N time periods: Required ✓ (in raw output)

---

## 4) Artifact Requirements & Quality Matrix

### Layer A — Required for All Suites

| Artifact | Required? | Found Path | Presence | Quality | Tests Run | Notes |
|----------|-----------|------------|----------|---------|-----------|-------|
| **A1: Provenance Doc** | Yes | `docs/provenance/H6.md` | ✅ Present | ✅ PASS | 24 claims verified | Comprehensive; 440 lines |
| **A1: Variable Dictionary** | Yes | `H6.md Section F` | ✅ Present | ✅ PASS | Formula/source verified | 18 variables documented |
| **A1: Variable Lineage JSON** | Yes | — | ❌ Missing | N/A | — | Not generated; only MD exists |
| **A1: Sample Attrition Table** | Yes | — | ❌ Missing | N/A | — | No tex/pdf attrition table |
| **A2: run_manifest.json** | Yes | — | ❌ Missing | N/A | — | No manifest generated |
| **A2: Environment Lock** | Yes | `requirements.txt` | ⚠️ Partial | ⚠️ PARTIAL | — | No hash freeze; pinned versions exist |
| **A2: Stage 3 Log** | Yes | `report_step3_h6.md` | ✅ Present | ✅ PASS | Row count verified | Minimal but present |
| **A2: Stage 4 Log** | Yes | Console output only | ⚠️ Partial | ⚠️ PARTIAL | — | No saved log file |
| **A3: Summary Stats CSV** | Yes | `summary_stats.csv` | ✅ Present | ✅ PASS | Cross-checked vs panel | 13 vars × 3 samples |
| **A3: Summary Stats TeX** | Yes | `summary_stats.tex` | ✅ Present | ✅ PASS | Compiles, correct format | 63 lines |
| **A3: Baseline Results TeX** | Yes | `h6_cccl_table.tex` | ✅ Present | ✅ PASS | Coefficients verified | Main sample, 5 DVs |
| **A3: Baseline Results CSV** | Yes | `model_diagnostics.csv` | ✅ Present | ✅ PASS | 21 rows, all fields valid | Complete |
| **A3: Raw Regression Output** | Yes | `regression_results_*.txt` | ✅ Present | ✅ PASS | 42 files (21+21 pretrends) | All present |

### Layer B — Model-Family Required (Panel FE)

| Artifact | Required? | Found Path | Presence | Quality | Notes |
|----------|-----------|------------|----------|---------|-------|
| **Within-R²** | Yes | `model_diagnostics.csv` | ✅ Present | ✅ PASS | All 21 values valid (bug fixed) |
| **FE Indicators** | Yes | `h6_cccl_table.tex` | ✅ Present | ✅ PASS | "Firm FE" and "Year FE" rows |
| **N Firms (Clusters)** | Yes | `model_diagnostics.csv` | ✅ Present | ✅ PASS | Column `n_firms` |
| **SE Type Documentation** | Yes | `h6_cccl_table.tex` | ✅ Present | ✅ PASS | Note: "Clustered SEs by firm" |

### Layer C — Figures (Paper-Ready)

| Artifact | Required? | Found Path | Presence | Quality | Notes |
|----------|-----------|------------|----------|---------|-------|
| **Coefficient Forest Plot** | Recommended | — | ❌ Missing | N/A | No forest plot generated |
| **Distribution Plots** | Optional | — | ❌ Missing | N/A | Not generated |

---

## 5) Notes-as-Claims Register

### 5.1) LaTeX Table Claims (`h6_cccl_table.tex`)

| # | Claim | Location | Verification | Status |
|---|-------|----------|--------------|--------|
| 1 | "Standard errors are clustered at the firm level" | Table note line 23 | Code: `run_h6_cccl.py:201` — `cov_type="clustered", cluster_entity=True` | **PASS** |
| 2 | "Firm and year fixed effects are included" | Table rows 16-17 | Code: `run_h6_cccl.py:199` — `EntityEffects + TimeEffects` | **PASS** |
| 3 | "p-values are one-tailed" | Table note line 22 | Code: `run_h6_cccl.py:222-225` — `p1_one = p1_two / 2 if beta1 < 0` | **PASS** |
| 4 | "Coefficient for Main/Mgr QA Unc is -0.0865" | Table row 12 | CSV: `beta1 = -0.0864734...` | **PASS** (matches to 4dp) |
| 5 | "SE for Main/Mgr QA Unc is 0.0642" | Table row 13 | CSV: `beta1_se = 0.0642004...` | **PASS** |
| 6 | "N obs for Main/Mgr QA Unc is 63,902" | Table row 19 | Raw output: `No. Observations: 63902` | **PASS** |
| 7 | "Within-R² for Main/Mgr QA Unc is 0.0007" | Table row 20 | CSV: `within_r2 = 0.0007051...` | **PASS** |

### 5.2) README Table Claims (Lines 469-474)

| # | Claim | Location | Actual Value | Status |
|---|-------|----------|--------------|--------|
| 8 | "Main (Mgr QA Unc) β = −0.0007" | README:471 | β = -0.0865, within_r2 = 0.0007 | **FAIL** — Confuses β with within-R² |
| 9 | "Main (Mgr QA Unc) p = 0.414" | README:471 | p(one-tail) = 0.089 | **FAIL** |
| 10 | "Main (CEO QA Unc) N = 63,902" | README:471 | N = 48,091 | **FAIL** — Uses wrong N |
| 11 | "Finance N = 12,376" | README:473 | N = 15,662 (Mgr QA Unc) | **FAIL** |

### 5.3) Provenance Document Claims (`H6.md`)

| # | Claim | Location | Verification | Status |
|---|-------|----------|--------------|--------|
| 12 | "Panel has 112,968 rows, 25 columns" | H6.md:107 | Ad-hoc: `panel.shape = (112968, 25)` | **PASS** |
| 13 | "CCCL_lag valid for 86,189 calls (76.3%)" | H6.md:229 | Ad-hoc: `86,189 / 112,968 = 76.3%` | **PASS** |
| 14 | "Zero row-delta on all merges" | H6.md:208 | Code: `build_h6_cccl_panel.py:220-221` raises ValueError | **PASS** |
| 15 | "file_name is unique (call-level)" | H6.md:19 | Ad-hoc: `panel['file_name'].is_unique = True` | **PASS** |
| 16 | "Sample split: Main=88,205, Finance=20,482, Utility=4,281" | H6.md:183 | Ad-hoc: verified exactly | **PASS** |
| 17 | "21 regressions (7 DVs × 3 samples)" | H6.md:108 | `len(diag) = 21` | **PASS** |
| 18 | "Pre-trends violations found" | H6.md:475-478 | 7 significant leads at p<0.10 | **PASS** — Documented |

---

## 6) Findings (Grouped by Severity)

### Finding #1 — BLOCKER: README H6 Detailed Table Has Incorrect Coefficient Values

**Severity:** BLOCKER

**Symptom:** The README H6 detailed table (lines 469-474) reports coefficient values that match within-R² values, not actual beta coefficients. Additionally, N obs values are incorrect for CEO specifications.

**Evidence:**
```
README claims:
  Main (Mgr QA Unc): β = −0.0007, p = 0.414
  Main (CEO QA Unc): β = −0.0005, p = 0.510, N = 63,902
  Finance: N = 12,376

Actual values (from model_diagnostics.csv):
  Main (Mgr QA Unc): β = -0.0865, p(one-tail) = 0.089, within_r2 = 0.0007
  Main (CEO QA Unc): β = 0.0227, p(one-tail) = 0.599, N = 48,091, within_r2 = -0.0006
  Finance (Mgr QA Unc): N = 15,662
```

The README values appear to be within-R² values mislabeled as coefficients. This is a critical documentation error that would mislead readers.

**Why it matters:** The README is the primary entry point. Incorrect coefficient values constitute a material misrepresentation of results.

**How to verify:**
```bash
cd "C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D"
python -c "
import pandas as pd
diag = pd.read_csv('outputs/econometric/h6_cccl/2026-02-28_230834/model_diagnostics.csv')
main_mgr = diag[(diag['sample']=='Main') & (diag['dv']=='Manager_QA_Uncertainty_pct')].iloc[0]
print(f'beta1: {main_mgr[\"beta1\"]:.4f}, within_r2: {main_mgr[\"within_r2\"]:.4f}')
"
```

**Fix:** Update README lines 469-474 with correct values from `model_diagnostics.csv`:
```markdown
| Sample | N Obs | N Firms | CCCL_lag β | p-value | Significant |
|--------|------:|--------:|-----------:|--------:|:-----------:|
| Main (Mgr QA Unc) | 63,902 | 1,751 | −0.0865 | 0.089 | No |
| Main (CEO QA Unc) | 48,091 | 1,561 | 0.0227 | 0.599 | No |
| Finance (Mgr QA Unc) | 15,662 | 436 | −1.3066 | 0.014 | Yes* |
| Utility (Mgr QA Unc) | 3,154 | 81 | 1.3637 | 0.987 | No |
```
*Finance results subject to pre-trends concerns (see Finding #2).

**Rerun impact:** Documentation update only — no code rerun needed.

---

### Finding #2 — MAJOR: Pre-Trends Violations Undermine Causal Interpretation

**Severity:** MAJOR

**Symptom:** 7 significant lead coefficients (p<0.10) in pre-trends falsification tests, indicating that future CCCL exposure predicts current uncertainty language.

**Evidence:**
| File | Variable | Lead | β | p-value |
|------|----------|------|---|---------|
| Main_Mgr_QA_Uncertainty_PRETRENDS | lead1 | -0.1021 | 0.0052 | *** |
| Main_Mgr_QA_Weak_Modal_PRETRENDS | lead1 | -0.0770 | 0.0013 | *** |
| Main_CEO_QA_Weak_Modal_PRETRENDS | lead1 | -0.1504 | 0.0032 | *** |
| Main_Uncertainty_Gap_PRETRENDS | lead2 | -0.1733 | 0.0164 | ** |
| Finance_CEO_QA_Uncertainty_PRETRENDS | lead1 | -1.3281 | 0.0803 | * |
| Finance_Uncertainty_Gap_PRETRENDS | lead1 | -1.4316 | 0.0412 | ** |
| Utility_CEO_Pres_Uncertainty_PRETRENDS | lead1 | -2.1202 | 0.0074 | *** |

**Why it matters:** Pre-trends violations indicate the CCCL instrument may not satisfy the exclusion restriction. Firms facing future SEC scrutiny already show different uncertainty patterns today, suggesting reverse causality or confounding. This undermines causal interpretation of the 4 significant Finance results.

**How to verify:**
```bash
cd "C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D"
python -c "
import os
for f in sorted(os.listdir('outputs/econometric/h6_cccl/2026-02-28_230834')):
    if 'PRETRENDS' in f and f.endswith('.txt'):
        with open(f'outputs/econometric/h6_cccl/2026-02-28_230834/{f}') as fh:
            for line in fh:
                if 'lead' in line and 'shift_intensity' in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        try:
                            if float(parts[4]) < 0.10:
                                print(f'{f}: {parts[0][-5:]} beta={parts[1]} p={parts[4]}')
                        except: pass
"
```

**Fix:**
1. The provenance doc (H6.md) already documents this — ensure paper discussion addresses pre-trends concerns
2. Add pre-trends summary to `model_diagnostics.csv` (columns: `lead1_beta`, `lead1_p`, `lead2_beta`, `lead2_p`)
3. Consider robustness check restricting to firms without pre-trends

**Rerun impact:** Code enhancement recommended; no mandatory rerun for current results.

---

### Finding #3 — MAJOR: Missing Reproducibility Artifacts

**Severity:** MAJOR

**Symptom:** The following reproducibility artifacts are missing:
1. No `run_manifest.json` with git commit, timestamp, config snapshot
2. No sample attrition table (tex/pdf)
3. No machine-readable variable lineage (JSON)

**Evidence:**
```bash
ls outputs/**/run_manifest*.json  # No files found
ls outputs/**/*attrition*         # No files found
ls **/*lineage*.json              # No files found
```

**Why it matters:** Without a run manifest, the link between outputs and code version is not captured. Without an attrition table, sample flow from 112,968 → 63,902 is not documented in paper-ready form.

**How to verify:**
```bash
find outputs -name "*manifest*" -o -name "*attrition*"
```

**Fix:**
1. Generate `run_manifest.json` at Stage 4 completion with: git_commit, timestamp, panel_path, config snapshot
2. Create attrition table showing: Total calls → After CCCL_lag filter → After controls dropna → After min_calls filter
3. Optional: Generate variable lineage JSON from `H6.md` Section F

**Rerun impact:** Code enhancement for future runs; manual generation possible for current run.

---

### Finding #4 — MINOR: LaTeX Table Only Shows Main Sample

**Severity:** MINOR

**Symptom:** The LaTeX table `h6_cccl_table.tex` only presents Main sample results for 5 DVs. The 4 significant Finance results are not shown in any publication table.

**Evidence:**
```latex
% h6_cccl_table.tex only queries Main sample:
r_1 = get_res("Manager_QA_Uncertainty_pct")  # defaults to sample="Main"
```

**Why it matters:** A reader looking only at the LaTeX table would conclude H6 is entirely null, missing the Finance sample partial support.

**Fix:**
1. Create a second LaTeX table for Finance sample, OR
2. Add Finance column to existing table, OR
3. Add note to table caption: "Finance sample shows 4/7 significant results (see model_diagnostics.csv)"

**Rerun impact:** Code change + Stage 4 rerun to generate additional/modified table.

---

### Finding #5 — MINOR: Stale merge_asof Matches (78 rows)

**Severity:** MINOR

**Symptom:** 78 calls have `|calendar_year - fyearq| > 2` due to merge_asof without tolerance parameter. 72 of these have valid CCCL_lag values from the wrong fiscal year.

**Evidence:**
```python
panel['cal_year'] = pd.to_datetime(panel['start_date']).dt.year
stale = panel[abs(panel['cal_year'] - panel['fyearq']) > 2]
# len(stale) = 78, 72 with valid CCCL_lag
```

**Why it matters:** For 0.07% of the panel, CCCL_lag values come from stale Compustat matches (e.g., 2017 call matched to fyearq=2007). Minimal impact on results but represents data contamination.

**Fix:** Add tolerance to `panel_utils.attach_fyearq()`:
```python
pd.merge_asof(..., tolerance=pd.Timedelta(days=548))  # 1.5 years
```

**Rerun impact:** Stage 3 + Stage 4 rerun required. Impact on results: negligible (0.07%).

---

### Finding #6 — NOTE: Heavy Zero-Inflation in CCCL mkvalt Weighting

**Severity:** NOTE (methodological)

**Symptom:** The `shift_intensity_mkvalt_ff48_lag` variable is heavily zero-inflated:
- Main: 47.9% zeros
- Finance: 36.6% zeros
- Utility: 77.7% zeros

**Why it matters:** Nearly half the sample has CCCL_lag=0, contributing no variation to coefficient estimation but inflating N and deflating SEs. May attenuate Main sample results toward null.

**Fix:** Consider sensitivity analysis with sale-weighted version (0% zeros). Document in paper.

---

## 7) Cross-Artifact Consistency Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| **C1: N consistency** | diag N == raw output N | 63,902 == 63,902 | **PASS** |
| **C2: Coef consistency** | LaTeX == CSV == raw | -0.0865 == -0.0865 == -0.0865 | **PASS** |
| **C3: SE consistency** | LaTeX == CSV == raw | 0.0642 == 0.0642 == 0.0642 | **PASS** |
| **C4: Run linkage** | Stage 4 uses correct Stage 3 panel | `get_latest_output_dir()` → 2026-02-27_224247 | **PASS** |
| **C5: Within-R² consistency** | LaTeX == CSV | 0.0007 == 0.0007 | **PASS** |

**Note:** README detailed table is NOT consistent with actual outputs — see Finding #1.

---

## 8) Rerun / Regeneration Plan (Minimal)

### Stage 4 Only (for documentation fixes):

```bash
# Rerun Stage 4 to regenerate tables (no code changes)
python -m f1d.econometric.run_h6_cccl
```

**Acceptance tests:**
- [ ] `model_diagnostics.csv` has 21 rows
- [ ] All `within_r2` values are valid (not NaN)
- [ ] LaTeX table coefficients match diagnostics CSV to 4dp
- [ ] Summary stats N values match panel by sample

### Full Rerun (if tolerance fix applied):

```bash
# Stage 3
python -m f1d.variables.build_h6_cccl_panel

# Stage 4
python -m f1d.econometric.run_h6_cccl
```

---

## 9) Hardening Recommendations

### 9.1 Assertions to Add

1. **run_manifest.json generation** — Add at end of Stage 4:
```python
manifest = {
    "git_commit": subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
    "timestamp": timestamp,
    "panel_path": str(panel_file),
    "config": var_config,
    "python_version": sys.version,
}
with open(out_dir / "run_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
```

2. **Pre-trends auto-detection** — Flag significant leads in diagnostics:
```python
if model_pt is not None:
    for lead in ['lead1', 'lead2']:
        p = model_pt.pvalues.get(f'shift_intensity_mkvalt_ff48_{lead}', np.nan)
        if p < 0.05:
            meta[f'{lead}_p'] = p
            meta[f'{lead}_sig'] = True
```

3. **README auto-generation** — Generate README table from diagnostics to prevent drift.

### 9.2 Tests to Add

1. **Unit test: README vs diagnostics consistency** — Compare README H6 table values against latest `model_diagnostics.csv`
2. **Integration test: attrition reconciliation** — Verify 112,968 → final N is documented
3. **Regression test: coefficient stability** — Alert if Main/Mgr QA Unc β drifts > 0.01

---

## 10) Command Log

| # | Command | Purpose | Result |
|---|---------|---------|--------|
| 1 | `ls outputs/variables/h6_cccl/` | List Stage 3 runs | 4 directories found |
| 2 | `ls outputs/econometric/h6_cccl/` | List Stage 4 runs | 14 directories found |
| 3 | `python -c "import pandas as pd; ..."` | Verify panel shape | (112968, 25) |
| 4 | `python -c "... diag['within_r2']..."` | Check within-R² fix | All 21 values valid |
| 5 | `python -c "... pre-trends violations..."` | Count significant leads | 7 violations found |
| 6 | `python -c "... stale matches..."` | Count stale merge_asof | 78 stale, 72 with valid lag |
| 7 | `python -c "... zero inflation..."` | Check CCCL zeros | 47.9% Main, 36.6% Fin, 77.7% Util |
| 8 | `git rev-parse HEAD` | Get commit hash | c9b00bef... |
| 9 | `ls outputs/**/run_manifest*.json` | Find manifests | None found |
| 10 | `cat h6_cccl_table.tex` | Verify LaTeX content | Within-R² present |
| 11 | `python -c "... README vs diag..."` | Compare values | 4 mismatches found |

---

## Summary

**H6 CCCL suite is mechanically sound:**
- Panel construction: zero row-delta, unique keys, proper lags
- Output generation: 42 regression files, complete diagnostics, valid within-R²
- Cross-artifact consistency: LaTeX ↔ CSV ↔ raw outputs all match

**Two issues block paper submission:**

1. **README detailed table has incorrect coefficient values** — Shows within-R² instead of β, wrong N values
2. **Missing reproducibility artifacts** — No run_manifest, no attrition table

**Pre-trends violations remain a scientific concern** — 7 significant leads undermine causal interpretation of the 4 Finance-significant results. This is documented in provenance but requires paper-ready summary.

**Prior audit (AUDIT_H6.md) findings resolved:**
- ✅ within_r2 bug: Fixed — all 21 values now valid
- ✅ README summary row: Fixed — correctly says "4/21 sig (Finance only)"
- ⚠️ README detailed table: Still has incorrect values (new finding)

**Recommended actions before submission:**
1. Correct README H6 detailed table (Finding #1)
2. Generate run_manifest.json (Finding #3)
3. Create sample attrition table (Finding #3)
4. Add pre-trends summary to paper appendix (Finding #2)
