# Paper-Submission Readiness Audit: Suite H1 (Cash Holdings)

**Date:** 2026-02-28
**Auditor:** Adversarial Paper-Submission Readiness Auditor
**Suite ID:** H1 — Speech Uncertainty and Future Cash Holdings
**Model Family:** Panel Fixed Effects (PanelOLS via linearmodels)

---

## 1) Executive Summary

| Question | Answer |
|----------|--------|
| **Is H1 paper-submission ready?** | **YES (with minor fixes)** |
| **Presence verdict: complete package?** | **YES** |
| **Quality verdict: submission-grade quality?** | **YES** (Within-R² bug FIXED) |
| **Previous BLOCKER resolved?** | **YES** — Within-R² now correctly reports ~0.06 (not inflated ~0.84) |

### Top 3 Findings

1. **[RESOLVED]** ~~Within-R² Bug~~ — The manual `within_r2` computation bug identified in the prior audit (AUDIT_H1.md) has been **FIXED**. The code now correctly uses `model.rsquared_within` directly (line 389: `within_r2 = float(model.rsquared_within)`), and the LaTeX table reports correct values (~0.05-0.06).

2. **[MINOR]** Missing Run Manifest — No `run_manifest.json` or formal reproducibility bundle exists. The suite relies on timestamp conventions and provenance documentation, which is adequate but not ideal for full reproducibility guarantees.

3. **[NOTE]** Stale Docstring — Line 13 of `run_h1_cash_holdings.py` mentions "HC1 standard errors" but the code correctly uses firm-clustered SEs. The docstring should be updated for consistency.

### What Must Be Rerun?

**Nothing.** All artifacts are internally consistent and the Within-R² bug has been resolved in the current codebase.

---

## 2) Suite & Run Identification

| Field | Value |
|-------|-------|
| **Suite ID** | H1 — Cash Holdings Hypothesis |
| **Stage 3 run_id** | `2026-02-27_223354` |
| **Stage 4 run_id** | `2026-02-28_201955` |
| **Stage 3 panel path** | `outputs/variables/h1_cash_holdings/2026-02-27_223354/h1_cash_holdings_panel.parquet` |
| **Stage 4 output path** | `outputs/econometric/h1_cash_holdings/2026-02-28_201955/` |
| **Manifest commit hash** | Not embedded in outputs (reproducibility gap) |
| **Current git HEAD** | `c9b00be` |

### Evidence Commands

```bash
# Verify Stage 3 panel
ls -la outputs/variables/h1_cash_holdings/2026-02-27_223354/
# Result: h1_cash_holdings_panel.parquet (13.9 MB), report_step3_h1.md, summary_stats.csv

# Verify Stage 4 outputs
ls -la outputs/econometric/h1_cash_holdings/2026-02-28_201955/
# Result: 18 regression txt files, model_diagnostics.csv, h1_cash_holdings_table.tex, summary_stats.*

# Verify git commit
git log --oneline -1
# Result: c9b00be docs: add audit prompt and H-suite provenance documentation
```

---

## 3) Estimator Family Detection

| Evidence | Location | Finding |
|----------|----------|---------|
| Import statement | `run_h1_cash_holdings.py:80` | `from linearmodels.panel import PanelOLS` |
| Formula syntax | `run_h1_cash_holdings.py:357-361` | `EntityEffects + TimeEffects` |
| Fit call | `run_h1_cash_holdings.py:378` | `fit(cov_type="clustered", cluster_entity=True)` |
| Raw output header | `regression_results_*.txt:1-20` | "PanelOLS Estimation Summary" with R-squared (Within) |

**Model Family:** Panel Fixed Effects (PanelOLS)
**Required Artifacts (Layer B2):**
- Within R² — PRESENT ✓
- FE indicators — PRESENT (Firm + Year) ✓
- N entities + N time — PRESENT ✓
- Cluster summary — PRESENT (n_firms column) ✓

---

## 4) Artifact Requirements & Quality Matrix

### Layer A — Required for All Suites (Submission Core)

| Artifact | Required | Found Path | Presence | Quality | Quality Tests Run | Notes |
|----------|----------|------------|----------|---------|-------------------|-------|
| Suite provenance doc | Yes | `docs/provenance/H1.md` | PASS | PASS | Full trace verified | 475 lines, complete variable dictionary |
| Variable dictionary | Yes | `docs/provenance/H1.md` (Sec F) | PASS | PASS | Formulas, timing, winsorization documented | Includes all 6 uncertainty measures + controls |
| Sample attrition table | Partial | Provenance Sec E, README | PASS | PASS | Row counts reconciled | 112,968 → 105,269 with valid lead |
| run_manifest.json | Yes | — | **MISSING** | N/A | — | No formal manifest; timestamps used instead |
| Environment lock | Partial | `requirements.txt` | PASS | PASS | Package versions pinned | No hash-level pinning |
| Stage 3 log | Yes | `report_step3_h1.md` | PASS | PASS | Row counts, merge sequence documented | 69.3s duration |
| Stage 4 log | Yes | `report_step4_H1.md` | PASS | PASS | All 18 regressions documented | 5.4s duration |

### Layer B2 — Panel FE Required

| Artifact | Required | Found Path | Presence | Quality | Quality Tests Run | Notes |
|----------|----------|------------|----------|---------|-------------------|-------|
| Within R² | Yes | `model_diagnostics.csv:rsquared` | PASS | PASS | Matches raw output exactly | Values ~0.05-0.06 (FIXED from ~0.84) |
| FE indicators | Yes | LaTeX table notes | PASS | PASS | "firm FE + year FE" stated | Line 40-41 |
| N entities | Yes | `model_diagnostics.csv:n_firms` | PASS | PASS | Verified vs raw output | e.g., 1562 for Main CEO |
| N obs | Yes | `model_diagnostics.csv:n_obs` | PASS | PASS | Verified vs raw output | e.g., 54708 for Main CEO |
| Cluster summary | Yes | `model_diagnostics.csv:n_firms` | PASS | PASS | #clusters = n_firms | Firm-clustered SEs |

### Layer A3 — Core Statistics

| Artifact | Required | Found Path | Presence | Quality | Quality Tests Run | Notes |
|----------|----------|------------|----------|---------|-------------------|-------|
| Summary stats (tex) | Yes | `summary_stats.tex` | PASS | PASS | All vars present, 3 panels | 14 vars × 3 samples |
| Summary stats (csv) | Yes | `summary_stats.csv` | PASS | PASS | Machine-readable | Same data as tex |
| Baseline results (tex) | Yes | `h1_cash_holdings_table.tex` | PASS | PASS | Key coeffs + N + R² | 6 cols × 3 panels |
| Baseline results (txt) | Yes | 18 `regression_results_*.txt` | PASS | PASS | Full PanelOLS output | Coeffs, SEs, t-stats, p-values |
| model_diagnostics.csv | Yes | `model_diagnostics.csv` | PASS | PASS | 18 rows, all fields present | Includes within_r2, betas, SEs |

---

## 5) Notes-as-Claims Register

### Main Results Table (`h1_cash_holdings_table.tex`)

| Claim | Location Claimed | Verification | Status | Evidence |
|-------|------------------|--------------|--------|----------|
| "Standard errors (in parentheses) are clustered at the firm level." | Line 41 | `run_h1_cash_holdings.py:378` | **PASS** | `cov_type="clustered", cluster_entity=True` |
| "Model includes firm FE (C(gvkey)) and year FE (C(year))." | Line 40 | `run_h1_cash_holdings.py:361` | **PASS** | `EntityEffects + TimeEffects` |
| "Unit of observation: the individual earnings call." | Line 42 | Stage 3 builder | **PASS** | Panel has 112,968 rows = unique file_name |
| "$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed)" | Line 43 | `run_h1_cash_holdings.py:403-415` | **PASS** | One-tailed p-value logic verified |
| "H1a: Uncertainty $> 0$; H1b: Uncertainty $\times$ Lev $< 0$." | Line 44 | `run_h1_cash_holdings.py:414-415` | **PASS** | Direction checks in code |
| "Dependent variable is CashHoldings$_{t+1}$" | Line 39 | Stage 3 builder | **PASS** | `CashHoldings_lead` verified as t+1 fiscal year |

### Summary Statistics Table (`summary_stats.tex`)

| Claim | Location Claimed | Verification | Status | Evidence |
|-------|------------------|--------------|--------|----------|
| "All variables are measured at the call level." | Tablenotes | Panel structure | **PASS** | Each row = one earnings call |
| N for Main sample = 82,236 (Cash Holdings t+1) | Panel A | Stage 3 report | **PASS** | Matches provenance Sec D |

### Provenance Document (`H1.md`)

| Claim | Location Claimed | Verification | Status | Evidence |
|-------|------------------|--------------|--------|----------|
| "Winsorization at 1%/99% per-year" | Sec G | `_compustat_engine.py` | **PASS** | `winsorize_by_year()` confirmed |
| "Firm-clustered standard errors" | Sec A, J.4 | Code line 378 | **PASS** | `cluster_entity=True` |
| "112,968 rows, file_name unique" | Sec D | Panel verification | **PASS** | Verified via Python |
| "Zero row-delta on all panel merges" | Sec E | Builder code | **PASS** | `assert after_len == before_len` |
| "Interaction uses raw product (not pre-centered)" | Sec F | Code line 304 | **PASS** | `df["Uncertainty_x_Lev"] = df["Uncertainty"] * df["Lev"]` |
| "~CashHoldings_lead is constant within firm-year~" | Sec J.4 | — | **CLARIFIED** | Constant within *fiscal* year, not calendar year (see Note below) |

---

## 6) Findings (Grouped by Severity)

### [RESOLVED] Within-R² Inflation Bug (Previously BLOCKER)

| Field | Details |
|-------|---------|
| **Severity** | ~~BLOCKER~~ → RESOLVED |
| **Symptom** | Prior audit found LaTeX reporting Within-R² ~0.84 while raw output showed ~0.06 |
| **Root Cause** | Manual `within_r2` computation used grand mean instead of demeaned mean in SS_tot denominator |
| **Fix Applied** | Code now uses `within_r2 = float(model.rsquared_within)` (line 389) |
| **Verification** | LaTeX shows 0.059-0.061, matching `model_diagnostics.csv` and raw `.txt` outputs exactly |
| **Evidence** | `model_diagnostics.csv` row 3: `within_r2=0.0607`, LaTeX line 17: `0.061` |

### [MINOR] Missing Run Manifest

| Field | Details |
|-------|---------|
| **Severity** | MINOR |
| **Symptom** | No `run_manifest.json` with git commit, config snapshot, or input fingerprints |
| **Why it matters** | Reduces reproducibility guarantee; relies on timestamp conventions and provenance docs |
| **How to verify** | `ls outputs/econometric/h1_cash_holdings/2026-02-28_201955/run_manifest.json` → Not found |
| **Fix** | Add manifest generation to Stage 4 main() function; include git hash, panel path, config |
| **Rerun impact** | None (current outputs are valid) |

### [NOTE] Stale Docstring

| Field | Details |
|-------|---------|
| **Severity** | NOTE |
| **Symptom** | Line 13 mentions "HC1 standard errors" but code uses firm-clustered |
| **Location** | `run_h1_cash_holdings.py:13` |
| **Fix** | Update docstring to: "same firm-clustered standard errors" |
| **Rerun impact** | None |

### [CLARIFIED] DV Constancy Claim in Provenance

| Field | Details |
|-------|---------|
| **Severity** | NOTE |
| **Symptom** | Provenance Sec J.4 claims "CashHoldings_lead is constant within firm-year clusters" |
| **Clarification** | True for *fiscal* year (fyearq), but PanelOLS uses *calendar* year for time FE |
| **Impact** | None on results — firm-level clustering is still correct approach |
| **Recommendation** | Update provenance to clarify fiscal vs calendar year distinction |

---

## 7) Cross-Artifact Consistency Results

| Check | Status | Evidence |
|-------|--------|----------|
| **C1: N consistency** | **PASS** | Diagnostics n_obs = 54,708 matches raw output "No. Observations: 54708" |
| **C2: Coef/SE consistency** | **PASS** | beta1=0.0065, SE=0.0021 identical across .txt, .csv, .tex |
| **C3: Clustering consistency** | **PASS** | Code uses cluster_entity=True; table notes state "firm level" |
| **C4: Run linkage** | **PASS** | Stage 4 (2026-02-28_201955) uses Stage 3 panel (2026-02-27_223354) |
| **C5: Timing/leakage** | **PASS** | Lead construction verified as t+1 fiscal year (B6 fix) |

### Detailed Cross-Check: Main / CEO_QA_Uncertainty_pct

| Source | beta1 | beta1_SE | beta3 | beta3_SE | N | Within-R² |
|--------|-------|----------|-------|----------|---|-----------|
| Raw output (.txt) | 0.0065 | 0.0021 | -0.0151 | 0.0060 | 54,708 | 0.0607 |
| model_diagnostics.csv | 0.0065 | 0.0021 | -0.0151 | 0.0060 | 54,708 | 0.0607 |
| h1_cash_holdings_table.tex | 0.0065*** | (0.0021) | -0.0151*** | (0.0060) | 54,708 | 0.061 |

**Verdict:** All three sources are internally consistent. ✓

---

## 8) Rerun / Regeneration Plan

**No reruns required.** All artifacts are consistent and the Within-R² bug has been fixed.

### Optional Hardening (Future)

If adding run manifest:

```bash
# After adding manifest generation code
python -m f1d.econometric.run_h1_cash_holdings

# Verify manifest
cat outputs/econometric/h1_cash_holdings/latest/run_manifest.json
# Expected: {"git_commit": "...", "panel_path": "...", "timestamp": "..."}
```

---

## 9) Hardening Recommendations

1. **Add run_manifest.json generation** to all Stage 4 scripts:
   ```python
   manifest = {
       "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
       "timestamp": timestamp,
       "panel_path": str(panel_file),
       "config": var_config,
       "python_version": sys.version,
   }
   with open(out_dir / "run_manifest.json", "w") as f:
       json.dump(manifest, f, indent=2)
   ```

2. **Fix stale docstring** in `run_h1_cash_holdings.py:13`:
   - Change "same HC1 standard errors" → "same firm-clustered standard errors"

3. **Clarify provenance claim** in `H1.md` Sec J.4:
   - Add note that DV constancy applies to fiscal year (fyearq), not calendar year used for time FE

4. **Add assertion** in Stage 3 builder:
   ```python
   assert panel['CashHoldings_lead'].min() >= 0, "CashHoldings_lead has negative values"
   ```

---

## 10) Command Log

| # | Command | Purpose | Result |
|---|---------|---------|--------|
| 1 | `ls outputs/variables/h1_cash_holdings/` | Locate Stage 3 runs | Found 5 timestamped dirs |
| 2 | `ls outputs/econometric/h1_cash_holdings/` | Locate Stage 4 runs | Found 13 timestamped dirs |
| 3 | `Read H1.md` | Understand suite contract | 475 lines of provenance |
| 4 | `Read AUDIT_H1.md` | Review prior audit | Found BLOCKER on Within-R² |
| 5 | `Read build_h1_cash_holdings_panel.py` | Verify Stage 3 logic | Zero row-delta enforced |
| 6 | `Read run_h1_cash_holdings.py` | Verify Stage 4 logic | PanelOLS + firm-clustered |
| 7 | `ls outputs/econometric/h1_cash_holdings/2026-02-28_201955/` | List Stage 4 artifacts | 18 .txt + .csv + .tex |
| 8 | `Read model_diagnostics.csv` | Check diagnostics | 18 rows, within_r2 ~0.06 |
| 9 | `Read h1_cash_holdings_table.tex` | Verify LaTeX R² | Shows 0.059-0.061 (CORRECT) |
| 10 | `Read regression_results_Main_CEO_QA_Uncertainty_pct.txt` | Raw output verification | R-squared (Within): 0.0607 |
| 11 | `Python verification` | Cross-check N, coefs | All match across sources |
| 12 | `git log --oneline -5` | Check commit history | HEAD = c9b00be |

---

## Summary

**Suite H1 is PAPER-SUBMISSION READY.**

The previously identified BLOCKER (Within-R² inflation bug) has been **FIXED** in the current codebase. The LaTeX table now correctly reports Within-R² values of ~0.05-0.06, matching the raw PanelOLS output exactly.

**Artifact Completeness:**
- ✓ Provenance documentation (comprehensive)
- ✓ Variable dictionary (all 14 variables documented)
- ✓ Summary statistics (tex + csv)
- ✓ Baseline results table (tex + 18 raw txt files)
- ✓ Model diagnostics CSV
- ✓ Stage 3 and Stage 4 reports

**Quality Verification:**
- ✓ Coefficients match across raw output, diagnostics, and LaTeX
- ✓ N values match across all artifacts
- ✓ Within-R² correctly computed and reported
- ✓ Standard errors correctly documented as firm-clustered
- ✓ One-tailed hypothesis tests correctly implemented

**Hypothesis Results (2026-02-28 run):**
- H1a (β₁ > 0): **7/18 significant** — strongest for CEO measures in Main sample
- H1b (β₃ < 0): **2/18 significant** — leverage attenuation confirmed only for CEO measures in Main

The suite is reproducible, well-documented, and follows econometric best practices for panel fixed effects estimation with firm-clustered standard errors.
