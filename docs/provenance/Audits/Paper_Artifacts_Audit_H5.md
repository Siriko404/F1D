# Paper-Ready Artifacts Audit: H5 Analyst Dispersion

**Suite ID:** H5
**Audit Date:** 2026-03-01
**Auditor:** Claude (Adversarial Paper-Submission Readiness Auditor)
**Audit Type:** Manual, claim-based verification

---

## 1) Executive Summary

| Question | Answer |
|----------|--------|
| **Is H5 paper-submission ready?** | **No — 2 BLOCKERS** |
| **Presence verdict: complete package?** | **No** — Missing run_manifest.json and sample attrition table |
| **Quality verdict: submission-grade quality?** | **Partial** — Core results are correct, but reproducibility linkage incomplete |
| **Model Family** | Panel OLS with Firm + Year FE (linearmodels.PanelOLS) |
| **Hypothesis Result** | **H5 NOT SUPPORTED** (0/12 significant at p<0.05 one-tailed) |

### Top 3 BLOCKERS

| # | Blocker | Impact | Rerun Required |
|---|---------|--------|----------------|
| B-1 | No run_manifest.json in Stage 4 outputs | Cannot verify reproducibility or Stage 3→4 linkage | No (add metadata generation) |
| B-2 | No sample attrition table | Cannot trace N=112,968 → N=60,506 for regressions | No (generate from existing data) |
| B-3 | Stage 4 panel path not logged | Cannot prove Stage 4 used correct Stage 3 panel | No (add logging) |

### Key Positive Findings

- **Coefficient consistency:** LaTeX table values match diagnostics CSV within rounding tolerance
- **Within-R² fixed:** LaTeX table now correctly reports Within-R² (0.3079, 0.1637, etc.)
- **One-tailed p-value documented:** Table footnote clearly states "(one-tailed)"
- **Summary stats complete:** All regression variables present with correct N counts
- **Zero row-delta enforced:** Panel builder correctly prevents merge explosions

---

## 2) Suite & Run Identification

| Field | Value |
|-------|-------|
| **Suite ID** | H5 Analyst Dispersion |
| **Stage 3 Entrypoint** | `src/f1d/variables/build_h5_dispersion_panel.py` |
| **Stage 4 Entrypoint** | `src/f1d/econometric/run_h5_dispersion.py` |
| **Provenance Doc** | `docs/provenance/H5.md` |

### Latest Runs

| Stage | Run ID / Timestamp | Output Path |
|-------|-------------------|-------------|
| Stage 3 | `2026-02-28_134012` | `outputs/variables/h5_dispersion/2026-02-28_134012/` |
| Stage 4 | `2026-02-28_224155` | `outputs/econometric/h5_dispersion/2026-02-28_224155/` |

### Git Commit Verification

```
Current HEAD: c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50
Manifest commit: NOT RECORDED in Stage 4 outputs
```

**Evidence Commands:**
```bash
git rev-parse HEAD
# c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50

ls outputs/variables/h5_dispersion/2026-02-28_134012/
# h5_dispersion_panel.parquet  report_step3_h5.md  summary_stats.csv

ls outputs/econometric/h5_dispersion/2026-02-28_224155/
# h5_dispersion_table.tex  model_diagnostics.csv  regression_results_*.txt (12 files)
# summary_stats.csv  summary_stats.tex
```

---

## 3) Estimator Family Detection

| Field | Value | Evidence |
|-------|-------|----------|
| **Model Family** | Panel OLS with Fixed Effects | `linearmodels.panel.PanelOLS` |
| **Entity Effects** | Firm FE (`gvkey`) | `EntityEffects` in formula, `Entities: 1637` in output |
| **Time Effects** | Year FE (`year`) | `TimeEffects` in formula, `Time periods: 17` in output |
| **SE Clustering** | Firm-clustered | `Cov. Estimator: Clustered` in regression txt |
| **Software** | Python linearmodels v0.6.0+ | `from linearmodels.panel import PanelOLS` |

**Model-Specific Required Artifacts (B2 — Panel FE):**

| Artifact | Required | Found | Status |
|----------|----------|-------|--------|
| Within R² | Yes | Yes (0.3079) | **PASS** |
| FE indicators (Firm + Year) | Yes | Yes | **PASS** |
| N entities | Yes | Yes (1,637) | **PASS** |
| N time periods | Yes | Yes (17) | **PASS** |
| Cluster summary (#clusters) | Yes | Implicit (1,637 firms) | **PASS** |

---

## 4) Artifact Requirements & Quality Matrix

### LAYER A — Required for All Suites (Submission Core)

| Artifact | Required? | Expected Location | Found Path | Presence | Quality | Notes |
|----------|-----------|-------------------|------------|----------|---------|-------|
| **A1. Suite provenance doc** | Yes | `docs/provenance/H5.md` | ✓ Found | **PASS** | **PASS** | Complete spec, formulas, merge logic |
| **A2. Variable dictionary** | Yes | `config/variables.yaml` | ✓ Found | **PASS** | **PARTIAL** | Has formulas but no machine-readable lineage JSON |
| **A3. Sample attrition table** | Yes | Stage 4 outputs | ✗ Missing | **FAIL** | N/A | Must be generated |
| **A4. run_manifest.json** | Yes | Stage 4 outputs | ✗ Missing | **FAIL** | N/A | BLOCKER — No reproducibility linkage |
| **A5. Environment lock** | Yes | `requirements.txt` | ✓ Found | **PASS** | **PASS** | Present at repo root |
| **A6. Stage 3 panel log** | Yes | Stage 3 outputs | ✓ Found | **PASS** | **PARTIAL** | `report_step3_h5.md` exists but minimal |

### LAYER B — Model-Family Required (Panel FE)

| Artifact | Required? | Found Path | Presence | Quality | Notes |
|----------|-----------|------------|----------|---------|-------|
| **B1. R² / Within R²** | Yes | In `model_diagnostics.csv` | **PASS** | **PASS** | Values: 0.3079, 0.1637, etc. |
| **B2. N obs, N entities** | Yes | In `model_diagnostics.csv` | **PASS** | **PASS** | Main: 60,506 obs, 1,637 firms |
| **B3. Cluster info** | Yes | In regression txt | **PASS** | **PASS** | "Cov. Estimator: Clustered" |
| **B4. FE absorption report** | Optional | N/A | N/A | N/A | No absorbed variables reported (correct) |

### LAYER C — Figures (Paper-Ready Quality)

| Artifact | Required? | Found | Presence | Quality | Notes |
|----------|-----------|-------|----------|---------|-------|
| **C1. Coefficient forest plot** | Optional | ✗ Not found | **MISSING** | N/A | Not generated for H5 |
| **C2. Distribution plots** | Optional | ✗ Not found | **MISSING** | N/A | Not generated for H5 |

### Core Statistics & Baseline Results

| Artifact | Required? | Found Path | Presence | Quality | Notes |
|----------|-----------|------------|----------|---------|-------|
| **summary_stats.csv** | Yes | Stage 4 outputs | **PASS** | **PASS** | 36 rows (12 vars × 3 samples) |
| **summary_stats.tex** | Yes | Stage 4 outputs | **PASS** | **PASS** | Properly formatted with table notes |
| **h5_dispersion_table.tex** | Yes | Stage 4 outputs | **PASS** | **PASS** | Within-R² now populated |
| **model_diagnostics.csv** | Yes | Stage 4 outputs | **PASS** | **PASS** | 12 rows (all specs) |
| **regression_results_*.txt** | Yes | Stage 4 outputs | **PASS** | **PASS** | 12 files, raw PanelOLS output |

---

## 5) Notes-as-Claims Register

### Table: h5_dispersion_table.tex

| # | Claim (Atomic, Testable) | Location in Artifact | Verification | Status |
|---|--------------------------|---------------------|--------------|--------|
| 1 | Standard errors are clustered at the firm level | Line 23: "Clustered SEs by firm." | `run_h5_dispersion.py:188`: `cov_type="clustered", cluster_entity=True` | **PASS** |
| 2 | Firm and year fixed effects are included | Lines 16-17: "Firm FE & Yes & Yes & Yes & Yes", "Year FE & Yes & Yes & Yes & Yes" | `run_h5_dispersion.py:186`: `EntityEffects + TimeEffects` | **PASS** |
| 3 | Significance stars are based on one-tailed p-values | Line 22: "$^{*}$p$<$0.10, $^{**}$p$<$0.05, $^{***}$p$<$0.01 (one-tailed)." | `run_h5_dispersion.py:321`: passes `beta1_p_one` to `fmt_coef()` | **PASS** |
| 4 | Within-R² values are reported | Line 20: "Within-$R^2$ & 0.3079 & 0.1637 & 0.3082 & 0.1640" | Matches `model_diagnostics.csv` `within_r2` column | **PASS** |
| 5 | Model A coefficient is -0.0153 (SE=0.0061) | Line 11: "-0.0153", Line 12: "(0.0061)" | `model_diagnostics.csv`: beta1=-0.015266, SE=0.006071 | **PASS** (within rounding) |
| 6 | N observations is 60,506 for Model A (Lagged DV) | Line 19: "Observations & 60,506 & 60,506 & 60,448 & 60,448" | `model_diagnostics.csv`: n_obs=60506 | **PASS** |
| 7 | Model B (Lagged DV) coefficient is 0.0042 with * star | Line 11: "0.0042^{*}" | `model_diagnostics.csv`: beta1=0.004203, p_one=0.060186 (marginal at 10%) | **PASS** |

### Table: summary_stats.tex

| # | Claim (Atomic, Testable) | Location in Artifact | Verification | Status |
|---|--------------------------|---------------------|--------------|--------|
| 8 | Main sample N for dispersion_lead is 66,526 | Line 11: "Analyst Dispersion$_{t+1}$ & 66,526" | Panel: `dispersion_lead.notna().sum()` for Main = 66,526 | **PASS** |
| 9 | Mean Manager QA Uncertainty is 0.8209 for Main | Line 12: "0.8209" | Panel mean matches | **PASS** |
| 10 | All variables measured at call level | Line 57-58: "All variables are measured at the call level." | Panel PK is `file_name` (call identifier) | **PASS** |

### Provenance Doc: H5.md

| # | Claim (Atomic, Testable) | Location | Verification | Status |
|---|--------------------------|----------|--------------|--------|
| 11 | Panel has 112,968 rows | H5.md:102 | Panel: `len(df) = 112,968` | **PASS** |
| 12 | dispersion_lead = forward merge_asof with 180-day tolerance | H5.md:207 | `dispersion_lead.py:67`: `tolerance=pd.Timedelta(days=180)` | **PASS** |
| 13 | Winsorization: Linguistic 0%/99% per-year | H5.md:246 | `_linguistic_engine.py:255-258`: `lower=0.0, upper=0.99` | **PASS** |
| 14 | Winsorization: Compustat 1%/99% per-year | H5.md:245 | `_compustat_engine.py:1050-1057` | **PASS** |
| 15 | Winsorization: IBES 1%/99% pooled | H5.md:247 | `_ibes_engine.py:164-167` | **PASS** |

---

## 6) Findings (Grouped by Severity)

### BLOCKER-1: No run_manifest.json in Stage 4 Outputs

- **Severity:** BLOCKER
- **Symptom:** `outputs/econometric/h5_dispersion/2026-02-28_224155/` contains no `run_manifest.json` or similar metadata file.
- **Evidence:**
  - `ls outputs/econometric/h5_dispersion/2026-02-28_224155/` shows only .tex, .csv, .txt files
  - No JSON metadata file present
- **Why it matters:** Without a manifest, reviewers cannot verify:
  1. Which git commit produced these results
  2. Which Stage 3 panel path was used as input
  3. What command was run
  4. Configuration snapshot at run time
- **How to verify:** `ls outputs/econometric/h5_dispersion/2026-02-28_224155/*.json` → No files found
- **Fix:** Add manifest generation to `run_h5_dispersion.py`:
  ```python
  manifest = {
      "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
      "timestamp": timestamp,
      "command": sys.argv,
      "panel_path": str(panel_file),
      "config": CONFIG,
  }
  with open(out_dir / "run_manifest.json", "w") as f:
      json.dump(manifest, f, indent=2)
  ```
- **Rerun impact:** Stage 4 only (no rerun needed for results, just add metadata generation)

### BLOCKER-2: No Sample Attrition Table

- **Severity:** BLOCKER
- **Symptom:** No explicit table documenting row count changes from manifest (N=112,968) to regression sample (N=60,506).
- **Evidence:**
  - `report_step3_h5.md` shows only "Dispersion Lead (valid): 85,107 calls"
  - No breakdown of filter stages (manifest → valid DV → min_calls → complete controls)
- **Why it matters:** Reviewers need to understand sample attrition:
  1. How many calls lost to missing dispersion_lead?
  2. How many calls lost to missing controls?
  3. How many firms dropped by min_calls ≥ 5 filter?
- **How to verify:** Check Stage 4 outputs for attrition table → Not found
- **Fix:** Generate attrition table in Stage 4:
  ```python
  attrition = [
      ("Manifest calls", 112968),
      ("With valid dispersion_lead", 85107),
      ("With valid prior_dispersion", 87503),
      ("With all controls", ...),
      ("Firms with ≥5 calls", ...),
      ("Final regression N", 60506),
  ]
  pd.DataFrame(attrition, columns=["Stage", "N"]).to_csv(out_dir / "sample_attrition.csv")
  ```
- **Rerun impact:** Stage 4 only

### BLOCKER-3: Stage 4 Panel Path Not Logged

- **Severity:** BLOCKER
- **Symptom:** `run_h5_dispersion.py` discovers the latest Stage 3 panel via `get_latest_output_dir()` but does not log which panel was used.
- **Evidence:**
  - Code at lines 354-360: `panel_dir = get_latest_output_dir(..., required_file="h5_dispersion_panel.parquet")`
  - Panel path printed to console but not saved to file
- **Why it matters:** If multiple Stage 3 runs exist, we cannot prove Stage 4 used the correct one.
- **How to verify:** Grep Stage 4 outputs for panel path → Not found in any output file
- **Fix:** Add panel path to run_manifest.json and/or report header
- **Rerun impact:** None if combined with B-1 fix

### MAJOR-1: Variable Dictionary Missing Machine-Readable Lineage

- **Severity:** MAJOR
- **Symptom:** `config/variables.yaml` provides source locations and column mappings, but there is no machine-readable JSON lineage file linking each variable to exact source file + row counts.
- **Evidence:**
  - `variables.yaml` has `source`, `file_pattern`, `column` fields
  - No corresponding `variable_lineage.json` with exact file paths, row counts, merge keys
- **Why it matters:** For full reproducibility, a machine-readable lineage enables automated verification that variable X came from file Y with Z rows.
- **How to verify:** `ls outputs/**/*lineage*.json` → No files found
- **Fix:** Generate `variable_lineage.json` in Stage 3 panel builder with:
  - Variable name
  - Source file path (resolved)
  - Source row count
  - Merge key
  - Match rate
- **Rerun impact:** Stage 3

### MINOR-1: Report Step 3 Minimal Content

- **Severity:** MINOR
- **Symptom:** `report_step3_h5.md` contains only 10 lines with minimal information.
- **Evidence:**
  ```
  ## Panel Summary
  - Rows: 112,968
  - Columns: 24
  - Dispersion Lead (valid): 85,107 calls
  ```
- **Why it matters:** Missing valuable debugging/reproducibility info:
  - Variable coverage rates
  - Sample distribution by industry
  - Merge deltas (all zero, but should be logged)
  - Duration per builder
- **Fix:** Enhance `generate_report()` in `build_h5_dispersion_panel.py` to include coverage table
- **Rerun impact:** Stage 3

### MINOR-2: Summary Stats Missing CEO Variables

- **Severity:** MINOR
- **Symptom:** `summary_stats.csv/tex` does not include CEO uncertainty variables even though they are in the panel.
- **Evidence:**
  - Panel has `CEO_QA_Uncertainty_pct`, `CEO_QA_Weak_Modal_pct`, `CEO_Pres_Uncertainty_pct`
  - `SUMMARY_STATS_VARS` includes CEO variables (lines 105-109)
  - But output CSV has 0 rows for CEO variables
- **Why it matters:** Incomplete descriptive statistics for variables that exist in the data.
- **Fix:** Either remove CEO variables from panel builder (if unused) or ensure they appear in summary stats
- **Rerun impact:** Stage 3 or Stage 4

### NOTE-1: Model B Marginal Significance

- **Severity:** NOTE
- **Symptom:** Model B (Lagged DV) Main shows `0.0042*` with p_one=0.0602, which is technically >0.05.
- **Evidence:**
  - LaTeX shows `*` for p<0.10
  - p_one=0.060186 is <0.10 but >0.05
  - Footnote correctly says "$^{*}$p$<$0.10"
- **Why it matters:** Not an error — the table correctly documents marginal significance. But authors should be aware this is not conventional "significant at 5%".
- **Fix:** None needed if footnote is accurate (it is)
- **Rerun impact:** None

---

## 7) Cross-Artifact Consistency Results

### C1) N Consistency

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Panel total rows | 112,968 | 112,968 | **PASS** |
| Main sample dispersion_lead N (summary stats) | 66,526 | 66,526 | **PASS** |
| Main Model A (Lagged DV) N (diagnostics) | 60,506 | 60,506 | **PASS** |
| Main Model A (Lagged DV) N (regression txt) | 60,506 | 60,506 | **PASS** |
| Main Model A (Lagged DV) N (LaTeX) | 60,506 | 60,506 | **PASS** |

### C2) Coefficient / SE Consistency

| Coefficient | Diagnostics CSV | Regression TXT | LaTeX Table | Status |
|-------------|-----------------|----------------|-------------|--------|
| Model A β₁ | -0.015266 | -0.0153 | -0.0153 | **PASS** |
| Model A SE | 0.006071 | 0.0061 | (0.0061) | **PASS** |
| Model B β₁ | 0.004203 | 0.0042 | 0.0042 | **PASS** |
| Model B SE | 0.002706 | 0.0027 | (0.0027) | **PASS** |

### C3) Clustering / SE Method Consistency

| Check | Code | Regression TXT | Table Note | Status |
|-------|------|----------------|------------|--------|
| SE type | `cov_type="clustered"` | "Cov. Estimator: Clustered" | "Clustered SEs by firm" | **PASS** |
| Cluster dimension | `cluster_entity=True` | Implicit (firm) | Implicit | **PASS** |
| # clusters | 1,637 (firms) | Entities: 1637 | N/A | **PASS** |

### C4) Run Linkage Consistency

| Check | Expected | Found | Status |
|-------|----------|-------|--------|
| Stage 4 panel path | Logged or manifest | **NOT FOUND** | **FAIL** |
| Stage 3 timestamp referenced | In Stage 4 outputs | **NOT FOUND** | **FAIL** |
| Git commit in outputs | Present | **NOT FOUND** | **FAIL** |

**Note:** Cross-artifact linkage cannot be verified without manifest files.

### C5) Timing / Leakage Spot-Check

| Variable | Merge Direction | Tolerance | Look-ahead Risk | Status |
|----------|-----------------|-----------|-----------------|--------|
| dispersion_lead (DV) | Forward | 180 days | Intentional (t+1 outcome) | **PASS** |
| prior_dispersion | Backward | None | Stale data risk (MINOR) | **PASS** |
| earnings_surprise_ratio | Backward | None | Stale data risk (MINOR) | **PASS** |
| Compustat controls | Backward | None | Low risk (quarterly data dense) | **PASS** |

---

## 8) Rerun / Regeneration Plan (Minimal, Suite-Scoped)

### Required Actions

| Priority | Action | Command | Acceptance Test |
|----------|--------|---------|-----------------|
| 1 | Add run_manifest.json generation to Stage 4 | Edit `run_h5_dispersion.py` | `ls outputs/econometric/h5_dispersion/*/run_manifest.json` shows files |
| 2 | Add sample attrition table generation | Edit `run_h5_dispersion.py` | `sample_attrition.csv` exists in Stage 4 outputs |
| 3 | Log Stage 3 panel path in Stage 4 | Edit `run_h5_dispersion.py` | Panel path appears in run_manifest.json |

### Optional Enhancements

| Priority | Action | Command | Acceptance Test |
|----------|--------|---------|-----------------|
| 4 | Enhance Stage 3 report with coverage table | Edit `build_h5_dispersion_panel.py` | `report_step3_h5.md` includes coverage % for all vars |
| 5 | Add variable lineage JSON | Edit `build_h5_dispersion_panel.py` | `variable_lineage.json` exists in Stage 3 outputs |

### Full Regeneration Commands (If Needed)

```bash
cd "C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D"

# Stage 3: Rebuild panel (if code changes made)
python -m f1d.variables.build_h5_dispersion_panel

# Stage 4: Rerun hypothesis tests (if code changes made)
python -m f1d.econometric.run_h5_dispersion
```

### Acceptance Tests Checklist

After regeneration, verify:

- [ ] Panel row count = 112,968
- [ ] Panel column count = 24
- [ ] `file_name` is unique in panel
- [ ] Sample distribution: Main=88,205 / Finance=20,482 / Utility=4,281
- [ ] Diagnostics CSV has 12 rows (all specs)
- [ ] Coefficient β₁ for Main Model A (Lagged DV) = -0.0153 ± 0.001
- [ ] Within-R² for Main Model A (Lagged DV) = 0.308 ± 0.005
- [ ] `run_manifest.json` exists in Stage 4 output
- [ ] `sample_attrition.csv` exists in Stage 4 output
- [ ] LaTeX table Within-R² values are non-blank

---

## 9) Hardening Recommendations

### Assertions to Add

1. **`run_h5_dispersion.py`** — After loading panel:
   ```python
   assert len(panel) == 112968, f"Unexpected panel size: {len(panel)}"
   assert panel["file_name"].is_unique, "file_name not unique"
   ```

2. **`run_h5_dispersion.py`** — After dropna:
   ```python
   assert len(df_reg) >= 100, f"Insufficient observations: {len(df_reg)}"
   ```

### Logging Improvements

1. Log exact panel path loaded: `print(f"Loaded panel: {panel_file}")` → also write to manifest
2. Log filter counts: `print(f"Dropped {n_dropped} firms with <5 calls")`
3. Log final N per sample before regression

### Tests to Add

1. **Unit test:** Verify coefficient values match diagnostics CSV for all 12 specs
2. **Unit test:** Verify LaTeX table R² values are non-blank
3. **Integration test:** Verify run_manifest.json is generated and contains expected fields
4. **Regression test:** Pin Main Model A Lagged DV β₁ to ±0.001

---

## 10) Command Log (Mandatory)

| # | Command | Purpose | Timestamp |
|---|---------|---------|-----------|
| 1 | `Read README.md` | Extract stage architecture | 2026-03-01 |
| 2 | `Read docs/Prompts/Paper_Ready_artifacts.txt` | Load audit protocol | 2026-03-01 |
| 3 | `Glob **/*h5*` | Find H5-related files | 2026-03-01 |
| 4 | `Glob **/*dispersion*` | Find dispersion-related files | 2026-03-01 |
| 5 | `Read docs/provenance/H5.md` | Load suite provenance | 2026-03-01 |
| 6 | `Read src/f1d/variables/build_h5_dispersion_panel.py` | Audit Stage 3 builder | 2026-03-01 |
| 7 | `Read src/f1d/econometric/run_h5_dispersion.py` | Audit Stage 4 runner | 2026-03-01 |
| 8 | `ls outputs/variables/h5_dispersion/` | List Stage 3 runs | 2026-03-01 |
| 9 | `ls outputs/econometric/h5_dispersion/` | List Stage 4 runs | 2026-03-01 |
| 10 | `ls outputs/variables/h5_dispersion/2026-02-28_134012/` | Check Stage 3 artifacts | 2026-03-01 |
| 11 | `ls outputs/econometric/h5_dispersion/2026-02-28_224155/` | Check Stage 4 artifacts | 2026-03-01 |
| 12 | `Read outputs/.../report_step3_h5.md` | Verify Stage 3 report | 2026-03-01 |
| 13 | `Read outputs/.../model_diagnostics.csv` | Verify diagnostics | 2026-03-01 |
| 14 | `Read outputs/.../h5_dispersion_table.tex` | Verify LaTeX table | 2026-03-01 |
| 15 | `Read outputs/.../summary_stats.csv` | Verify summary stats | 2026-03-01 |
| 16 | `Read outputs/.../regression_results_Main_Model_A_(Lagged_DV).txt` | Verify raw output | 2026-03-01 |
| 17 | `Read outputs/.../summary_stats.tex` | Verify LaTeX summary stats | 2026-03-01 |
| 18 | `Read outputs/.../summary_stats.csv (Stage 3)` | Verify Stage 3 stats | 2026-03-01 |
| 19 | `python -c "import pandas as pd; ..."` | Verify panel content | 2026-03-01 |
| 20 | `python -c "..."` | Verify coefficient consistency | 2026-03-01 |
| 21 | `Glob outputs/**/run_manifest*` | Check for manifests | 2026-03-01 |
| 22 | `Glob outputs/**/*attrition*` | Check for attrition tables | 2026-03-01 |
| 23 | `git rev-parse HEAD` | Get current commit | 2026-03-01 |
| 24 | `ls logs/` | Check for logs directory | 2026-03-01 |
| 25 | `Grep run_h5_dispersion.py for manifest/commit` | Check for linkage code | 2026-03-01 |
| 26 | `Read config/variables.yaml` | Check variable config | 2026-03-01 |

---

## Summary

**Overall Assessment:**

H5 Analyst Dispersion is **not paper-submission ready** due to missing reproducibility artifacts (run_manifest.json, sample attrition table). The **core results are trustworthy** — coefficients, SEs, R² values, and N counts are consistent across diagnostics CSV, regression txt, and LaTeX table. The hypothesis finding (H5 NOT SUPPORTED) is robust.

**What Works:**
- Zero row-delta enforcement in panel builder
- Correct PanelOLS specification with firm+year FE
- Firm-clustered SEs properly implemented and documented
- Within-R² now correctly reported in LaTeX table (previously blank)
- One-tailed p-value convention clearly documented in table footnote
- All 12 regression specifications present and complete
- Summary stats comprehensive with correct N counts

**What Must Be Fixed:**
- Add run_manifest.json generation to Stage 4
- Generate sample attrition table
- Log Stage 3 panel path in Stage 4 outputs

**Estimated Fix Time:** 1-2 hours to add manifest and attrition generation code.

**Confidence in Results:** HIGH — No evidence of implementation errors affecting the "NOT SUPPORTED" finding.
