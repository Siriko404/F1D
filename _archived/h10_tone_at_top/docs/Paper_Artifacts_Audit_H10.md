# Paper-Submission-Ready Audit Report: H10 (Tone-at-the-Top)

**Audit Date:** 2026-03-01
**Suite ID:** H10 (H_TT: Tone-at-the-Top)
**Auditor:** Adversarial Pipeline Referee
**Protocol:** Paper_Ready_artifacts.txt

---

## 1) Executive Summary

**Is suite H10 paper-submission ready?** **NO — Requires Stage 4 Rerun**

**Presence verdict: Complete package?** **PARTIAL** — Core artifacts present, reproducibility bundle incomplete

**Quality verdict: Submission-grade quality?** **NO** — Critical sample filter bug and table notes error

### Top 3 BLOCKERS

| # | Severity | Issue | Must Rerun |
|---|----------|-------|------------|
| 1 | **BLOCKER** | "Main" sample filter bug — uses ALL samples instead of FF12 non-fin/non-util | Stage 4 |
| 2 | **BLOCKER** | LaTeX table clustering note incorrect for M2 (says "Firm × CEO" but M2 uses "Firm × Call") | Stage 4 |
| 3 | **MAJOR** | No run_manifest.json — reproducibility bundle incomplete | Stage 4 |

### Additional Critical Findings

| # | Severity | Issue |
|---|----------|-------|
| 4 | MAJOR | M2 placebo test (future CEO uncertainty) has t=31.49, stronger than main IV (t=19.37) — undermines causal interpretation |
| 5 | MAJOR | Duplicate entity-time index in M1 (347 firm-quarters with >1 call) |
| 6 | MINOR | No sample attrition table in publication format |
| 7 | MINOR | Turn_Uncertainty_pct is unwinsorized (values up to 100%) |

---

## 2) Suite & Run Identification

| Field | Value |
|-------|-------|
| **Suite ID** | H10 (H_TT: Tone-at-the-Top) |
| **Stage 3 Run ID** | 2026-02-27_225254 |
| **Stage 4 Run ID** | 2026-02-27_225837 |
| **Stage 3 Panel Path** | `outputs/variables/tone_at_top/2026-02-27_225254/tone_at_top_panel.parquet` |
| **Stage 3 Turns Path** | `outputs/variables/tone_at_top/2026-02-27_225254/tone_at_top_turns_panel.parquet` |
| **Stage 4 Output Path** | `outputs/econometric/tone_at_top/2026-02-27_225837/` |
| **Git HEAD (audit time)** | `c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50` |
| **Manifest commit** | NOT FOUND — no run_manifest.json |

### Evidence Commands

```bash
# Verify Stage 3 outputs
ls outputs/variables/tone_at_top/2026-02-27_225254/
# tone_at_top_panel.parquet, tone_at_top_turns_panel.parquet, summary_stats.csv, reconciliation_table.csv

# Verify Stage 4 outputs
ls outputs/econometric/tone_at_top/2026-02-27_225837/
# 37 coefficient CSVs, 2 LaTeX tables, report.md, model_diagnostics.csv, summary_stats.*

# Git commit
git rev-parse HEAD
# c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50
```

---

## 3) Estimator Family Detection

### Model Families Detected

| Model | Family | Estimator | Evidence |
|-------|--------|-----------|----------|
| **M1 (Call-level)** | Panel OLS with Fixed Effects | `linearmodels.panel.PanelOLS` | `run_h10_tone_at_top.py:138-153` |
| **M2 (Turn-level)** | Absorbing Least Squares | `linearmodels.iv.absorbing.AbsorbingLS` | `run_h10_tone_at_top.py:242-247` |

### Model-Family Specific Requirements (from protocol)

**Panel FE (B2):**
- [x] Within R² reported
- [x] FE indicators documented (Firm + Year-Quarter)
- [x] N entities + N time reported
- [ ] Absorption/dropped variables report — NOT FOUND
- [ ] Cluster summary (#clusters, min cluster size) — NOT EXPLICITLY REPORTED

**Quality Criteria (M1):**
- Within R² label: "Within R²" — CORRECT
- FE description: "Firm FE + Year-Quarter FE" — CORRECT
- Two-way clustering documented: YES (Firm × CEO)

---

## 4) Artifact Requirements & Quality Matrix

### LAYER A — Required for All Suites

| Artifact | Required? | Expected Location | Found Path | Presence | Quality | Quality Tests | Notes |
|----------|-----------|-------------------|------------|----------|---------|---------------|-------|
| **A1) Provenance / lineage** | | | | | | | |
| Suite provenance doc | YES | `docs/provenance/H10.md` | Found | **PASS** | **PARTIAL** | Commands present, lineage formulas documented, but sample filter bug not reflected | 504 lines |
| Variable dictionary | YES | `docs/provenance/H10.md` Section F | Found | **PASS** | **PASS** | Formulas, units, timing, transforms documented | Table format |
| Machine-readable lineage (JSON) | OPTIONAL | — | NOT FOUND | **N/A** | — | — | Not required but recommended |
| Sample attrition table | YES | Stage 3 outputs | `reconciliation_table.csv` | **PARTIAL** | **PARTIAL** | Row counts present but NOT in publication format (tex/pdf) | CSV only |
| **A2) Reproducibility bundle** | | | | | | | |
| run_manifest.json | YES | Stage 4 output dir | NOT FOUND | **FAIL** | — | — | **MISSING** — cannot verify commit, config, input fingerprints |
| Environment lock/snapshot | YES | `requirements.txt` | Found | **PARTIAL** | **PARTIAL** | Requirements exist but no hash-based lock | No pdm.lock, poetry.lock, or pip-compile output |
| Stage 3 log | OPTIONAL | — | NOT FOUND | **N/A** | — | — | No log files written |
| Stage 4 log | OPTIONAL | — | NOT FOUND | **N/A** | — | — | No log files written |
| **A3) Core statistics + baseline results** | | | | | | | |
| Summary stats (tex/pdf) | YES | Stage 4 output | `summary_stats.tex` | **PASS** | **PASS** | All regression vars included, correct units | 12 vars, 3 panels |
| Summary stats (csv) | YES | Stage 4 output | `summary_stats.csv` | **PASS** | **PASS** | Matches LaTeX | — |
| Baseline results table (tex) | YES | Stage 4 output | `tone_at_top_full.tex` | **PASS** | **FAIL** | Clustering note incorrect for M2 | See Finding #3 |
| Baseline results (csv) | YES | Stage 4 output | `coefficients_Main_M1_*.csv`, `coefficients_Main_M2_*.csv` | **PASS** | **PASS** | Coefficients verified against report.md | 37 coefficient files |
| Raw txt snapshot | OPTIONAL | — | NOT FOUND | **N/A** | — | — | — |
| model_diagnostics.csv | YES | Stage 4 output | Found | **PASS** | **PASS** | N, R², n_entities present | 6 models |

### LAYER B — Model-Family Required (Panel FE / Absorbing LS)

| Artifact | Required? | Found | Presence | Quality | Notes |
|----------|-----------|-------|----------|---------|-------|
| Within R² (M1) | YES | YES | **PASS** | **PASS** | 0.0019 (Main), 0.0008 (Finance), -0.0057 (Utility) |
| FE indicators (M1) | YES | YES | **PASS** | **PASS** | Firm FE + Year-Quarter FE documented |
| N entities + N time (M1) | YES | YES | **PASS** | **PASS** | n_firms, n_quarters in LaTeX table |
| R² (M2) | YES | YES | **PASS** | **PASS** | 0.0020 (Main), 0.0014 (Finance), 0.0006 (Utility) |
| N calls + N speakers (M2) | YES | YES | **PASS** | **PASS** | In LaTeX table |
| Cluster summary | YES | NO | **FAIL** | — | #clusters, min cluster size NOT reported |

### LAYER C — Figures

| Artifact | Required? | Found | Presence | Notes |
|----------|-----------|-------|----------|-------|
| Coefficient forest plot | OPTIONAL | NO | **MISSING** | No visualization for main effects across specs |
| Distribution plots | OPTIONAL | NO | **MISSING** | No pre/post winsorization plots |

---

## 5) Notes-as-Claims Register

### Main Results Table (`tone_at_top_full.tex`)

| # | Claim | Table Location | Code Reference | Status | Evidence |
|---|-------|----------------|----------------|--------|----------|
| 1 | "Standard errors (two-way clustered by Firm × CEO)" | Line 53 | `run_h10_tone_at_top.py:146-153` | **FAIL** | M2 uses Firm × Call clustering (lines 250-253), not Firm × CEO. Table note is WRONG for M2. |
| 2 | N = 43,570 for Main M1 | Line 40 | `model_diagnostics.csv` | **PARTIAL** | Count correct but composition wrong — includes Finance + Utility due to sample filter bug |
| 3 | N = 1,697,632 for Main M2 | Line 40 | `model_diagnostics.csv` | **PARTIAL** | Same issue — all industries included in "Main" |
| 4 | Within R² = 0.0019 for Main M1 | Line 45 | `model_diagnostics.csv` | **PASS** | Matches exactly |
| 5 | R² = 0.0020 for Main M2 | Line 46 | `model_diagnostics.csv` | **PASS** | Matches exactly |
| 6 | Firm FE = Yes for M1 | Line 48 | `run_h10_tone_at_top.py:141` | **PASS** | `entity_effects=True` |
| 7 | Year-Quarter FE = Yes for M1 | Line 49 | `run_h10_tone_at_top.py:142` | **PASS** | `time_effects=True` |
| 8 | Call FE = Yes for M2 | Line 50 | `run_h10_tone_at_top.py:242-247` | **PASS** | Absorbed via AbsorbingLS |
| 9 | Speaker FE = Yes for M2 | Line 51 | `run_h10_tone_at_top.py:242-247` | **PASS** | Absorbed via AbsorbingLS |
| 10 | CEO Style (Realtime) coef = 0.0169*** | Line 13 | `coefficients_Main_M1_H_TT1_Realtime.csv` | **PASS** | Matches: 0.0169, t=4.65 |
| 11 | CEO Prior Q&A Unc. coef = 0.0426*** | Line 15 | `coefficients_Main_M2_baseline.csv` | **PASS** | Matches: 0.0426, t=19.37 |

### Summary Statistics Table (`summary_stats.tex`)

| # | Claim | Status | Evidence |
|---|-------|--------|----------|
| 1 | Variables measured at call level | **PASS** | Note on line 58 |
| 2 | Main sample N varies by variable (60K-88K) | **PASS** | Column N shows correct variation |
| 3 | ClarityStyle_Realtime standardized (mean≈0, SD≈1) | **PASS** | Mean=-0.0859, SD=0.9579 |
| 4 | IHS transformation applied to uncertainty vars | **PASS** | Variable names include "IHS" |

### Provenance Documentation (`H10.md`)

| # | Claim | Location | Status | Evidence |
|---|-------|----------|--------|----------|
| 1 | "Pooled 1%/99% winsorization for linguistic percentages" | Section G | **FAIL** | CEO_QA_Uncertainty_pct uses per-year via LinguisticEngine; Turn_Uncertainty_pct not winsorized |
| 2 | "Main sample = FF12 1-7, 9-10, 12" | Section E | **FAIL (code)** | Provenance correct but code uses ALL samples for "Main" |
| 3 | M2 clusters by Firm × Call | Section A5 | **PASS** | Code confirms at lines 250-253 |
| 4 | ClarityStyle_Realtime requires ≥4 prior calls | Section A4 | **PASS** | `ceo_style_realtime.py:134` confirms `min_calls=4` |

---

## 6) Findings (Grouped by Severity)

### Finding #1 — BLOCKER: "Main" Sample Filter Bug

**Severity:** BLOCKER

**Symptom:** The code at `run_h10_tone_at_top.py:1084-1093` uses the entire `call_panel` for `sample == "Main"` instead of filtering to `sample == "Main"` rows.

**Evidence:**
```python
# Lines 1084-1093
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

**Why it matters:**
- "Main" is supposed to be FF12 non-financial, non-utility firms (88,205 calls)
- Current code includes Finance (20,482) + Utility (4,281) in "Main"
- M1 Main N=43,570 should be ~35,399 for true Main sample
- Results are inconsistent with all other hypothesis suites (H1-H9)

**How to verify:**
```python
import pandas as pd
cp = pd.read_parquet('outputs/variables/tone_at_top/2026-02-27_225254/tone_at_top_panel.parquet')
full = cp.dropna(subset=['ClarityStyle_Realtime','CFO_QA_Uncertainty_pct','Size','BM','Lev','ROA','StockRet','MarketRet','EPS_Growth','SurpDec'])
print(full['sample'].value_counts())
# Main: 35,399 / Finance: 6,793 / Utility: 1,378 = 43,570 total
```

**Fix:**
```python
# BEFORE (buggy):
call_sub = (
    call_panel
    if sample == "Main"
    else call_panel[call_panel["sample"] == sample]
)

# AFTER (correct):
call_sub = call_panel[call_panel["sample"] == sample].copy()
```

**Rerun impact:** Stage 4 only

---

### Finding #2 — BLOCKER: LaTeX Table Clustering Note Incorrect for M2

**Severity:** BLOCKER

**Symptom:** `tone_at_top_full.tex:53` states clustering is "Firm × CEO" for all models, but M2 uses "Firm × Call" clustering.

**Evidence:**
- LaTeX line 53: `"Standard errors (two-way clustered by Firm $\times$ CEO)"`
- Code `run_h10_tone_at_top.py:250-253`: M2 uses `cluster_by_call=True` default

**Why it matters:** Published table would mislead readers about variance estimation for M2 turn-level results.

**Fix:**
```python
# Update clustering note to be model-specific
"Standard errors in parentheses. M1: two-way clustered (Firm × CEO). M2: two-way clustered (Firm × Call)."
```

**Rerun impact:** Stage 4 only (LaTeX generation)

---

### Finding #3 — BLOCKER: Missing run_manifest.json

**Severity:** BLOCKER

**Symptom:** No `run_manifest.json` in Stage 4 output directory.

**Evidence:**
```bash
ls outputs/econometric/tone_at_top/2026-02-27_225837/ | grep manifest
# (empty)
```

**Why it matters:**
- Cannot verify git commit at run time
- Cannot verify input panel path linkage
- Cannot verify config snapshot
- Protocol A2 requires manifest for reproducibility

**Fix:** Add manifest generation to `run_h10_tone_at_top.py`:
```python
manifest = {
    "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
    "timestamp": datetime.now().isoformat(),
    "command": "python -m f1d.econometric.run_h10_tone_at_top",
    "panel_path": str(panel_path),
    "turns_path": str(turns_path),
}
with open(output_dir / "run_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
```

**Rerun impact:** Stage 4 only

---

### Finding #4 — MAJOR: M2 Placebo Test Undermines Causal Claim

**Severity:** MAJOR (interpretive, not code bug)

**Symptom:** The M2 placebo specification (future CEO uncertainty → current manager uncertainty) shows β=0.0373, t=31.49, which is STRONGER than the main IV (β=0.0426, t=19.37 has smaller t-stat).

**Evidence:**
- `coefficients_Main_M2_placebo_lead.csv`: β=0.0373, SE=0.00118, t=31.49
- `coefficients_Main_M2_baseline.csv`: β=0.0426, SE=0.00220, t=19.37

**Why it matters:**
- Future CEO uncertainty predicting current manager undermines causal interpretation
- Suggests within-call uncertainty clustering dominates signal, not directional CEO→manager transmission
- Call FE absorbs call-level mean, but within-call variance drives both baseline and placebo

**Fix (interpretive):**
1. Prominently discuss placebo failure in paper
2. Consider difference-in-differences: `IHS_CEO_Prior - IHS_CEO_Lead1` as IV
3. Consider adding `IHS_CEO_Unc_Lead1` as control to partial out within-call correlation

**Rerun impact:** None (interpretive)

---

### Finding #5 — MAJOR: Duplicate Entity-Time Index in M1

**Severity:** MAJOR

**Symptom:** 347 firm-quarters have >1 earnings call in M1 sample, creating non-unique PanelOLS index.

**Evidence:**
```python
# 694 duplicate rows (0.8% of 43,570)
dups = reg.groupby(['gvkey','yq_id']).size()
dups[dups>1].sum()  # 347 firm-quarters with duplicates
```

**Why it matters:** linearmodels PanelOLS behavior with non-unique MultiIndex is undefined. May silently overwrite or average observations.

**Fix:**
```python
reg_df = reg_df.sort_values("start_date").drop_duplicates(
    subset=["gvkey", "yq_id"], keep="last"
)
```

**Rerun impact:** Stage 4 only

---

### Finding #6 — MINOR: No Sample Attrition Table in Publication Format

**Severity:** MINOR

**Symptom:** `reconciliation_table.csv` exists but no LaTeX/PDF version.

**Evidence:**
```bash
ls outputs/variables/tone_at_top/2026-02-27_225254/
# reconciliation_table.csv present, no .tex version
```

**Why it matters:** Protocol A1 requires attrition table in publication format.

**Fix:** Generate `sample_attrition.tex` with panel structure.

**Rerun impact:** Stage 3 only (optional)

---

### Finding #7 — MINOR: Turn_Uncertainty_pct Unwinsorized

**Severity:** MINOR

**Symptom:** M2 DV ranges 0-100% with 478 turns >50% uncertainty.

**Evidence:**
```python
tp['Turn_Uncertainty_pct'].max()  # 100.0
(tp['Turn_Uncertainty_pct'] > 50).sum()  # 478
```

**Why it matters:** Extreme values from short turns may influence IHS transform. Provenance incorrectly claims "pooled 1/99%" for all linguistic vars.

**Fix:** Either winsorize at Stage 3 or document intentional non-winsorization.

**Rerun impact:** Stage 3 + Stage 4 (if winsorization added)

---

## 7) Cross-Artifact Consistency Results

| Check | Status | Evidence |
|-------|--------|----------|
| **C1) N consistency** | **PARTIAL** | model_diagnostics.csv N matches LaTeX table, BUT composition wrong due to sample bug |
| **C2) Coef/SE consistency** | **PASS** | Verified: M1 coef=0.0169, SE=0.0036; M2 coef=0.0426, SE=0.0022 match across CSV, LaTeX, report.md |
| **C3) Clustering consistency** | **FAIL** | Code M2 uses Firm×Call, LaTeX says Firm×CEO |
| **C4) Run linkage consistency** | **UNVERIFIED** | No manifest to verify Stage 4 → Stage 3 panel path linkage |
| **C5) Timing/leakage check** | **PASS** | ClarityStyle_Realtime uses shift() for strictly prior; CEO_Prior uses only prior turns |

---

## 8) Rerun / Regeneration Plan

### Minimal Rerun Commands

```bash
# Step 0: Apply fixes to run_h10_tone_at_top.py
# - Fix sample filter (Finding #1)
# - Fix LaTeX clustering note (Finding #2)
# - Add run_manifest.json generation (Finding #3)
# - Add entity-time dedup (Finding #5)

# Step 1: Rerun Stage 4
cd F1D
python -m f1d.econometric.run_h10_tone_at_top
```

### Acceptance Tests

After rerun, verify:

1. **Main M1 N decreases:**
   ```python
   diag = pd.read_csv('outputs/econometric/tone_at_top/<new>/model_diagnostics.csv')
   main_m1 = diag[diag['model'].str.contains('Main_M1')]
   assert 34000 < main_m1['n_obs'].values[0] < 37000
   ```

2. **Main M2 N decreases:**
   ```python
   main_m2 = diag[diag['model'].str.contains('Main_M2')]
   assert 1200000 < main_m2['n_obs'].values[0] < 1400000
   ```

3. **run_manifest.json exists:**
   ```bash
   ls outputs/econometric/tone_at_top/<new>/run_manifest.json
   ```

4. **LaTeX clustering note is model-specific:**
   ```bash
   grep "Firm.*Call" outputs/econometric/tone_at_top/<new>/tone_at_top_full.tex
   ```

5. **Coefficient signs preserved:**
   - M1 Main ClarityStyle_Realtime: positive
   - M2 Main IHS_CEO_Prior_QA_Unc: positive

---

## 9) Hardening Recommendations

### Repo-Level

1. **Add sample filter assertion to all econometric runners:**
   ```python
   if sample == "Main":
       assert not df_sample["sample"].isin(["Finance", "Utility"]).any()
   ```

2. **Add entity-time uniqueness check before PanelOLS:**
   ```python
   if not reg_df.index.is_unique:
       warnings.warn(f"Non-unique entity-time: {reg_df.index.duplicated().sum()} dups")
       reg_df = reg_df[~reg_df.index.duplicated(keep='last')]
   ```

3. **Standardize manifest generation:** Create shared utility to write run_manifest.json.

### Suite-Level (H10)

4. **Add sample attrition table in LaTeX format**

5. **Document placebo test failure prominently** in provenance and paper

6. **Log CEO_Unc_Lag1 zero/NaN rates** in reconciliation table

7. **Add cluster summary to model_diagnostics** (#clusters, min cluster size)

---

## 10) Command Log

| # | Command | Purpose | Result |
|---|---------|---------|--------|
| 1 | `read README.md` | Extract pipeline contract | 932 lines, 4-stage architecture |
| 2 | `read docs/Prompts/Paper_Ready_artifacts.txt` | Load audit protocol | 321 lines |
| 3 | `read docs/provenance/AUDIT_H10.md` | Review prior audit | 565 lines, identified sample bug |
| 4 | `glob **/*h10*` | Find H10 source files | 2 active files |
| 5 | `ls outputs/variables/tone_at_top/` | List Stage 3 runs | Latest: 2026-02-27_225254 |
| 6 | `ls outputs/econometric/tone_at_top/` | List Stage 4 runs | Latest: 2026-02-27_225837 |
| 7 | `read docs/provenance/H10.md` | Extract suite contract | 505 lines |
| 8 | `ls outputs/variables/tone_at_top/2026-02-27_225254/` | Verify Stage 3 artifacts | 4 files present |
| 9 | `ls outputs/econometric/tone_at_top/2026-02-27_225837/` | Verify Stage 4 artifacts | 37+ files |
| 10 | `read model_diagnostics.csv` | Check fit statistics | 6 models, N and R² present |
| 11 | `read results_main.csv` | Check main results | M1: 0.0169, M2: 0.0426 |
| 12 | `read tone_at_top_full.tex` | Audit LaTeX table | 57 lines, wrong clustering note |
| 13 | `read report.md` | Cross-check values | All values match CSVs |
| 14 | `read summary_stats.csv` | Check summary stats | 17 vars, missingness documented |
| 15 | `read reconciliation_table.csv` | Check row counts | 6 stages, correct deltas |
| 16 | `read coefficients_Main_M2_baseline.csv` | Verify M2 coef | β=0.0426, t=19.37 |
| 17 | `read coefficients_Main_M2_placebo_lead.csv` | Verify placebo | β=0.0373, t=31.49 |
| 18 | `read run_h10_tone_at_top.py:1-200` | Audit code structure | PanelOLS + AbsorbingLS |
| 19 | `read run_h10_tone_at_top.py:1075-1124` | Check sample filter | BUG CONFIRMED at lines 1084-1093 |
| 20 | `read summary_stats.tex` | Audit summary table | 3 panels, correct format |
| 21 | `read tone_at_top_table.tex` | Audit summary table | Only M1 results shown |
| 22 | `grep -i manifest outputs/...` | Check for manifest | NOT FOUND |
| 23 | `git rev-parse HEAD` | Get commit hash | c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50 |
| 24 | `read build_h10_tone_at_top_panel.py:1-100` | Audit Stage 3 code | 17 variable builders |

---

## 11) Verdict

| Criterion | Status | Notes |
|-----------|--------|-------|
| **All required artifacts present** | PARTIAL | Missing run_manifest.json, sample attrition tex |
| **Artifacts are correct** | FAIL | Sample filter bug, clustering note error |
| **Cross-artifact consistency** | PARTIAL | Coefficients match, but N composition wrong |
| **Notes-as-claims verified** | FAIL | 2 of 11 claims failed |
| **Model-family requirements met** | PARTIAL | Missing cluster summary |

**SUBMISSION STATUS: NOT READY**

Required actions before submission:
1. Fix sample filter bug (BLOCKER)
2. Fix LaTeX clustering note (BLOCKER)
3. Add run_manifest.json generation (BLOCKER)
4. Rerun Stage 4
5. Document placebo test interpretation concerns

---

*End of Paper-Submission-Ready Audit Report*
*Generated: 2026-03-01*
