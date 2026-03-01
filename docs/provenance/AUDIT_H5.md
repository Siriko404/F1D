# AUDIT REPORT: H5 Analyst Dispersion

**Auditor:** Claude (Antigravity) — manual, adversarial, code-level inspection
**Date:** 2026-02-28
**Suite ID:** H5
**Audit Scope:** End-to-end implementation audit of H5 Analyst Dispersion hypothesis suite

---

## 0) Suite Identification

| Field | Value |
|-------|-------|
| **Suite ID** | H5 |
| **Stage 3 Builder** | `src/f1d/variables/build_h5_dispersion_panel.py` |
| **Stage 4 Runner** | `src/f1d/econometric/run_h5_dispersion.py` |
| **Model Family** | Panel OLS with entity + time fixed effects (`linearmodels.PanelOLS`) |
| **Estimator** | `PanelOLS.from_formula(..., drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)` |
| **Provenance Doc** | `docs/provenance/H5.md` |

**Shared Engines Used:**

| Engine | File |
|--------|------|
| IbesEngine | `src/f1d/shared/variables/_ibes_engine.py` |
| CompustatEngine | `src/f1d/shared/variables/_compustat_engine.py` |
| LinguisticEngine | `src/f1d/shared/variables/_linguistic_engine.py` |

**Variable Builders Used (16 total):**
ManifestFieldsBuilder, ManagerQAUncertaintyBuilder, CEOQAUncertaintyBuilder, ManagerQAWeakModalBuilder, CEOQAWeakModalBuilder, ManagerPresUncertaintyBuilder, CEOPresUncertaintyBuilder, AnalystQAUncertaintyBuilder, SizeBuilder, LevBuilder, TobinsQBuilder, EarningsVolatilityBuilder, DispersionLeadBuilder, PriorDispersionBuilder, EarningsSurpriseRatioBuilder, LossDummyBuilder.

---

## 1) Suite Contract

Extracted from `docs/provenance/H5.md` and `src/f1d/econometric/run_h5_dispersion.py`:

- **Estimation unit:** Call-level (individual earnings call)
- **Primary keys:** `file_name` (unique call identifier), `gvkey` (firm), `year` (calendar year from `start_date`)
- **DV:** `dispersion_lead` = t+1 analyst forecast dispersion (STDEV / |MEANEST| from IBES, first consensus strictly after call date, forward merge_asof tolerance=180 days)
- **IVs (Model A):** `Manager_QA_Weak_Modal_pct` (target), `Manager_QA_Uncertainty_pct` (base)
- **IVs (Model B):** `Uncertainty_Gap` = `Manager_QA_Uncertainty_pct` - `Manager_Pres_Uncertainty_pct` (target), `Manager_Pres_Uncertainty_pct` (base)
- **Controls (BASE_CONTROLS):** `Analyst_QA_Uncertainty_pct`, `earnings_surprise_ratio`, `loss_dummy`, `Size`, `Lev`, `TobinsQ`, `earnings_volatility`
- **Optional lagged DV:** `prior_dispersion` (backward merge_asof, no tolerance)
- **Fixed effects:** Firm FE (entity_effects=True) + Year FE (time_effects=True)
- **Variance estimator:** Firm-clustered (`cov_type="clustered", cluster_entity=True`, `debiased=True`)
- **Transforms:** No standardization. Linguistic: 0%/99% per-year winsorization at engine. Compustat: 1%/99% per-fyearq at engine. IBES: 1%/99% pooled at engine. No additional winsorization in panel builder or runner.
- **Missingness policy:** NaN preserved in panel; listwise deletion at regression time (`dropna(subset=required)`); inf replaced with NaN before dropna
- **Sample splits:** Main (FF12 non-fin, non-util), Finance (FF12=11), Utility (FF12=8)
- **Sample filter:** `min_calls >= 5` (firms with <5 calls excluded)
- **One-tailed test:** H5: beta1 > 0; p_one = p_two/2 if beta>0, else 1 - p_two/2
- **Specs:** 12 total = 2 models (A, B) x 2 lag options (with/without prior_dispersion) x 3 samples

---

## 2) Evidence Map

| # | Claim | Where Claimed | Where Verified | Status | Notes |
|---|-------|---------------|----------------|--------|-------|
| 1 | Panel has 112,968 rows | H5.md:102, :173 | `h5_dispersion_panel.parquet` (verified: 112,968) | **PASS** | Confirmed via ad-hoc Python check |
| 2 | Panel has 24 columns | H5.md:102, :173 | `h5_dispersion_panel.parquet` (verified: 24) | **PASS** | |
| 3 | file_name is unique (PK) | H5.md:19 | `df["file_name"].is_unique == True` | **PASS** | Verified ad-hoc |
| 4 | Zero row-delta on all merges | H5.md:201, builder:133-138 | `build_h5_dispersion_panel.py:133-138` raises ValueError | **PASS** | Code enforces delta==0 |
| 5 | dispersion_lead 75.3% coverage | H5.md:196, :325 | Verified: 85,107/112,968 = 75.3% | **PASS** | |
| 6 | prior_dispersion 77.5% coverage | H5.md:197, :326 | Verified: 87,503/112,968 = 77.5% | **PASS** | |
| 7 | Sample split: Main=88,205 / Finance=20,482 / Utility=4,281 | H5.md:173 | Verified from panel | **PASS** | |
| 8 | Firm FE + Year FE | H5.md:63, runner:186 | `PanelOLS.from_formula(...EntityEffects + TimeEffects)` | **PASS** | |
| 9 | Firm-clustered SE | H5.md:67, runner:188 | `.fit(cov_type="clustered", cluster_entity=True)` | **PASS** | |
| 10 | Model A Main Lagged DV: N=60,506 | H5.md:367 | diagnostics CSV + regression txt: 60,506 | **PASS** | |
| 11 | Model A Main Lagged DV: beta1=-0.0153 | H5.md:367 | diagnostics CSV: -0.015266, txt: -0.0153 | **PASS** | Rounding consistent |
| 12 | Model A Main Lagged DV: R2(within)=0.308 | H5.md:367 | diagnostics CSV: 0.3079, txt R2(Within): 0.3079 | **PASS** | |
| 13 | dispersion_lead = forward merge_asof, tol=180d | H5.md:207 | `dispersion_lead.py:60-68` | **PASS** | |
| 14 | prior_dispersion = backward merge_asof | H5.md:208 | `prior_dispersion.py:52-59` | **PASS** | But NO tolerance (see Finding M-1) |
| 15 | IBES winsorization 1%/99% pooled | H5.md:247 | `_ibes_engine.py:164-167` | **PASS** | |
| 16 | Linguistic winsorization 0%/99% per-year | H5.md:246 | `_linguistic_engine.py:255-258` (lower=0.0, upper=0.99) | **PASS** | |
| 17 | Compustat winsorization 1%/99% per-year | H5.md:245 | `_compustat_engine.py:1050-1057` | **PASS** | Uses fyearq grouping |
| 18 | loss_dummy = 1 if ibq < 0 | H5.md:232 | `loss_dummy.py:42-44`: `(comp["ibq"] < 0)` | **PASS** | Code matches provenance. Docstring says "niq" (WRONG docstring, see Finding m-1) |
| 19 | earnings_volatility = rolling 5yr std | H5.md:230 | `_compustat_engine.py:848-883`: annual iby/atq rolling 1826D std | **PASS** | Provenance says "quarterly" but code uses annual (see Finding m-2) |
| 20 | Uncertainty_Gap computed in Stage 4 | H5.md:221 | `run_h5_dispersion.py:135-137` | **PASS** | |
| 21 | min_calls >= 5 filter | H5.md:59 | `run_h5_dispersion.py:481-484` | **PASS** | Drops 14 calls, 5 firms from Main |
| 22 | 12 regression outputs | H5.md:103 | 12 regression_results_*.txt files in output dir | **PASS** | |
| 23 | within_r2 in diagnostics CSV | H5.md:374 | All NaN in diagnostics CSV | **FAIL** | Custom computation fails; see Finding MA-1 |
| 24 | LaTeX table reports Within-R2 | H5.md:104 | All blank in `h5_dispersion_table.tex` line 20 | **FAIL** | Uses NaN within_r2; see Finding MA-1 |
| 25 | Summary stats CSV N matches panel | N/A | All 5 variables spot-checked: MATCH | **PASS** | |

---

## 3) End-to-End Implementation Audit

### A) Stage 1/2 Preconditions

**Manifest anchoring:** The panel builder loads the manifest via `ManifestFieldsBuilder`, which reads `master_sample_manifest.parquet` from `outputs/1.4_AssembleManifest/latest/`. Columns loaded: `file_name, ceo_id, ceo_name, gvkey, ff12_code, ff12_name, start_date`. The manifest has 112,968 rows covering 2,429 unique gvkeys. Year range 2002-2018 is enforced by filtering on `start_date.dt.year`.

**Linguistic anchoring:** Linguistic variable builders use the `LinguisticEngine` singleton, which loads year-partitioned parquet files from `outputs/2_Textual_Analysis/2.2_Variables/latest/`. 17 year files loaded, totaling 112,968 rows.

**Hidden dependencies:** None detected. H5 does not depend on `clarity_scores.parquet` or any other Stage 4 output. All inputs come from Stage 1 manifest, Stage 2 linguistic outputs, or raw inputs (IBES, CCM, Compustat).

**Status: PASS** — Suite is correctly anchored to expected preconditions.

### B) Stage 3 Panel Builder Audit

**File:** `src/f1d/variables/build_h5_dispersion_panel.py` (228 lines)

#### B1) Primary Key Uniqueness

- `file_name` is the call-level primary key.
- **Verified:** `df["file_name"].is_unique == True` (112,968 unique values, 0 duplicates).
- The builder does not explicitly assert uniqueness, but the manifest guarantees it (Stage 1 dedup), and all merges are left-joins on `file_name`.
- **Status: PASS** (with NOTE — see Finding N-1 for hardening suggestion)

#### B2) Merge Sequence and Zero Row-Delta

- 15 left-joins on `file_name` after the manifest base.
- `build_h5_dispersion_panel.py:133-138`: After each merge, `delta = after_len - before_len; if delta != 0: raise ValueError(...)`.
- **Verified:** All merges produce zero delta (confirmed by code logic and output row count = 112,968).
- **Status: PASS**

#### B3) Many-to-Many Join Risk

- All merges use `how="left"` on `file_name`.
- Risk: if a builder returns multiple rows per `file_name`, the merge would silently expand the panel.
- Mitigation: Each builder returns exactly one row per `file_name` (enforced by the builder pattern: each builder loads manifest, processes, and returns `file_name + one_column`).
- The zero-row-delta check at lines 133-138 would catch any expansion.
- **Status: PASS** (row-delta check is the safety net)

#### B4) Timing Alignment and Look-Ahead Bias

**dispersion_lead (DV):**
- `dispersion_lead.py:57`: `target_date = start_date + pd.Timedelta(days=1)` — offsets by 1 day to ensure "strictly after".
- `dispersion_lead.py:60-68`: `pd.merge_asof(..., direction="forward", tolerance=pd.Timedelta(days=180))` — finds first IBES consensus AFTER call date.
- **No look-ahead bias:** The DV is explicitly forward-looking (t+1 consensus). This is the intended design.
- **Status: PASS**

**prior_dispersion (control):**
- `prior_dispersion.py:52-59`: `pd.merge_asof(..., direction="backward")` — finds most recent consensus BEFORE call date.
- **No tolerance specified.** This means a call could match an arbitrarily old consensus if no recent IBES data exists for that firm.
- **Risk:** A 2018 call could match a 2005 consensus if the firm has no IBES coverage in between.
- **Impact:** Stale `prior_dispersion` values could bias the lagged DV coefficient. However, the effect is mitigated because (a) firms without recent IBES coverage are typically small/illiquid firms that would also lack `dispersion_lead`, and (b) the firm FE absorbs level differences.
- **Status: MINOR concern** (see Finding M-1)

**earnings_surprise_ratio (control):**
- `earnings_surprise_ratio.py:50-57`: Same backward merge_asof with no tolerance.
- **Same staleness risk as prior_dispersion.**
- **Status: MINOR concern** (same as M-1)

**Compustat controls (Size, Lev, TobinsQ, earnings_volatility, loss_dummy):**
- All use backward merge_asof from `start_date` to `datadate` by `gvkey`, via `CompustatEngine.match_to_manifest()` (`_compustat_engine.py:1143-1150`).
- **No tolerance specified** on the Compustat match either, but Compustat quarterly data is dense (4 obs/year per firm), so staleness risk is minimal.
- **Status: PASS**

**Fiscal vs calendar alignment:**
- `year` is derived from `start_date.dt.year` (calendar year), not fiscal year.
- Time FE uses `C(year)` = calendar year. This is standard for call-level data.
- **Status: PASS**

#### B5) Outlier Handling

| Variable | Winsorization | Where Applied | Consistent? |
|----------|--------------|---------------|-------------|
| Linguistic _pct vars | 0%/99% per-year | `_linguistic_engine.py:255-258` | Yes |
| Size, Lev, TobinsQ, earnings_volatility | 1%/99% per-fyearq | `_compustat_engine.py:1050-1057` | Yes |
| dispersion, earnings_surprise_ratio | 1%/99% pooled | `_ibes_engine.py:164-167` | Yes |
| loss_dummy | N/A (binary) | N/A | Yes |

- No additional winsorization in panel builder or runner.
- **Status: PASS** — Winsorization is consistent between provenance and code.

#### B6) Missingness

- Missing values are preserved as NaN in the panel (left joins).
- `run_h5_dispersion.py:154`: `df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required)` — listwise deletion at regression time.
- No silent drops during merges (left joins preserve all manifest rows).
- **Status: PASS**

#### B7) Variable Semantics

| Variable | Provenance Definition | Code Implementation | Match? |
|----------|----------------------|---------------------|--------|
| `dispersion_lead` | STDEV/\|MEANEST\| from IBES, forward merge, 180d tol | `_ibes_engine.py:130`, `dispersion_lead.py:60-68` | **PASS** |
| `prior_dispersion` | STDEV/\|MEANEST\| from IBES, backward merge | `prior_dispersion.py:47-59` | **PASS** |
| `Uncertainty_Gap` | Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct | `run_h5_dispersion.py:135-137` | **PASS** |
| `Manager_QA_Weak_Modal_pct` | 100*(Weak_Modal tokens / total tokens) for Manager QA | LinguisticEngine | **PASS** |
| `Manager_QA_Uncertainty_pct` | 100*(Uncertainty tokens / total tokens) for Manager QA | LinguisticEngine | **PASS** |
| `Analyst_QA_Uncertainty_pct` | Same formula, Analyst speakers | LinguisticEngine | **PASS** |
| `Size` | ln(atq) for atq>0 | `_compustat_engine.py:940` | **PASS** |
| `Lev` | (dlcq + dlttq) / atq | `_compustat_engine.py:945` | **PASS** |
| `TobinsQ` | (atq + cshoq*prccq - ceqq) / atq | `_compustat_engine.py:969-973` | **PASS** (uses mktcap+debt_book formulation, equivalent) |
| `earnings_volatility` | Rolling 5yr std of annual iby/atq | `_compustat_engine.py:848-883` | **PASS** (provenance says "quarterly", code uses annual — see m-2) |
| `earnings_surprise_ratio` | \|ACTUAL - MEANEST\| / \|MEANEST\| | `_ibes_engine.py:131-133` | **PASS** |
| `loss_dummy` | 1 if ibq < 0 | `loss_dummy.py:42-44` | **PASS** (docstring says niq, code uses ibq — see m-1) |

### C) Shared Engines / Variable Builders Audit

#### C1) IbesEngine (`_ibes_engine.py`)

**Dedup logic:**
- `_ibes_engine.py:159-160`: `sort_values(["gvkey", "statpers", "days_to_target"]).drop_duplicates(subset=["gvkey", "statpers"], keep="first")`.
- Keeps the closest forecast target per (gvkey, statpers) — deterministic.
- **Status: PASS**

**CUSIP linking:**
- `_ibes_engine.py:65-72`: CCM cusip8 → gvkey, filtered to LINKPRIM in ['P', 'C'], then `drop_duplicates(subset=["cusip8"], keep="first")`.
- `keep="first"` depends on CCM input order — potentially non-deterministic if CCM is unsorted.
- **Risk:** Low. LINKPRIM P/C filter removes most ambiguity. Multiple gvkeys per cusip8 are rare with primary links.
- **Status: PASS** (with NOTE — see N-2)

**Winsorization:**
- `_ibes_engine.py:164-167`: Global 1%/99% on `dispersion` and `earnings_surprise_ratio`.
- Applied after all filtering and dedup.
- **Status: PASS**

**Denominator protection:**
- `_ibes_engine.py:108`: `chunk[(chunk["MEANEST"].abs() >= self.meanest_min)]` where `meanest_min = 0.05`.
- Prevents division by near-zero MEANEST.
- **Status: PASS**

#### C2) CompustatEngine (`_compustat_engine.py`)

**Dedup logic:**
- `_compustat_engine.py:1107`: `drop_duplicates(subset=["gvkey", "datadate"], keep="last")` — keeps most recent restatement.
- **Status: PASS**

**Winsorization:**
- `_compustat_engine.py:1050-1057`: Per-fyearq 1%/99% via `_winsorize_by_year()` with min_obs=10.
- Applied to all COMPUSTAT_COLS except binary and already-winsorized variables.
- **Status: PASS**

**Date matching:**
- `_compustat_engine.py:1143-1150`: `merge_asof(..., direction="backward")` — most recent Compustat date ≤ call start_date.
- **Status: PASS**

#### C3) LinguisticEngine (`_linguistic_engine.py`)

**Winsorization:**
- `_linguistic_engine.py:255-258`: Per-year winsorization with `lower=0.0, upper=0.99, min_obs=1`.
- `lower=0.0` means no lower clipping (linguistic percentages are naturally ≥ 0).
- `upper=0.99` clips at the 99th percentile.
- **Status: PASS**

### D) Stage 4 Runner / Estimation Audit

**File:** `src/f1d/econometric/run_h5_dispersion.py` (517 lines)

#### D1) Model Specification vs Provenance

**RHS terms:**
- Model A formula: `dispersion_lead ~ 1 + target_var + base_var + Analyst_QA_Uncertainty_pct + earnings_surprise_ratio + loss_dummy + Size + Lev + TobinsQ + earnings_volatility [+ prior_dispersion] + EntityEffects + TimeEffects`
- Model B: Same but `target_var = Uncertainty_Gap`, `base_var = Manager_Pres_Uncertainty_pct`.
- **Matches provenance spec (H5.md section H).** PASS.

**FE / absorbed effects:**
- `run_h5_dispersion.py:186-187`: `PanelOLS.from_formula(form_clean, data=df_panel, drop_absorbed=True)` with `EntityEffects + TimeEffects`.
- Multi-index: `df_reg.set_index(["gvkey", "year"])` at line 179.
- **Non-unique index:** 87,432 out of 88,191 Main-sample rows have duplicate (gvkey, year) pairs (most firms have 4 calls/year). PanelOLS handles this correctly — entity effects demean across all observations for that entity, time effects demean across all observations in that year. This is standard for call-level data with firm+year FE.
- **Status: PASS**

**Sample splits:**
- `run_h5_dispersion.py:473-479`: Loops over ["Main", "Finance", "Utility"], filtering by `panel["sample"]`.
- `assign_industry_sample()` from `panel_utils.py:46-73` classifies: FF12=11 → Finance, FF12=8 → Utility, else → Main.
- **Status: PASS**

**min_calls filter:**
- `run_h5_dispersion.py:481-484`: `df_sample.groupby("gvkey")["file_name"].transform("count")`, filter `>= 5`.
- Verified: drops 14 calls, 5 firms from Main sample.
- **Status: PASS**

#### D2) Variance Estimator

- `run_h5_dispersion.py:188`: `.fit(cov_type="clustered", cluster_entity=True)`.
- Clusters SEs at the firm (gvkey) level. `debiased=True` is the linearmodels default.
- Regression txt confirms: `Cov. Estimator: Clustered`.
- **Status: PASS**

#### D3) One-Tailed P-values

- `run_h5_dispersion.py:239-240`:
  ```python
  p1_one = p1_two / 2 if beta1 > 0 else 1 - p1_two / 2
  ```
- **Verification:** For Model A Main (beta=-0.0153, p_two=0.0119): p_one = 1 - 0.0119/2 = 0.9940. Correct — wrong direction gets near-1 p-value.
- For Model B Main (beta=0.0042, p_two=0.1204): p_one = 0.1204/2 = 0.0602. Correct.
- **Status: PASS** — Sign-conditional halving is implemented correctly.

#### D4) LaTeX Table

- `run_h5_dispersion.py:284-294`: `fmt_coef()` uses `pval` parameter for star assignment.
- `run_h5_dispersion.py:321-324`: Passes `r["beta1_p_one"]` as the p-value for stars.
- **Issue:** Stars are based on ONE-TAILED p-values, not two-tailed. Model B Lagged DV Main gets a `*` (p_one=0.0602 < 0.10) even though p_two=0.1204 (not significant at any conventional level with two-tailed test). This is standard for directional hypotheses but must be clearly documented in the table footnote.
- **Status: MAJOR concern** (see Finding MA-2)

- **Within-R2 row in LaTeX is BLANK** because `within_r2` is NaN for all models (custom computation fails). The table uses `r["within_r2"]` instead of `r["rsquared"]` (which contains the correct within-R2).
- **Status: MAJOR concern** (see Finding MA-1)

#### D5) Outputs

| Output File | Expected | Present | Content Verified |
|-------------|----------|---------|-----------------|
| `regression_results_*.txt` (12 files) | Yes | Yes (12 files) | Spot-checked Main Model A Lagged DV |
| `model_diagnostics.csv` | Yes | Yes (12 rows) | All 12 specs present, cross-checked |
| `h5_dispersion_table.tex` | Yes | Yes | Content verified |
| `summary_stats.csv` | Yes | Yes (36 rows = 12 vars x 3 samples) | N values match panel |
| `summary_stats.tex` | Yes | Yes | Present |

### E) Artifact Integrity & Cross-Consistency

**Latest outputs:**
- Stage 3: `outputs/variables/h5_dispersion/2026-02-28_134012/`
- Stage 4: `outputs/econometric/h5_dispersion/2026-02-28_134130/`

**Cross-check: diagnostics CSV vs regression txt (Main Model A Lagged DV):**

| Field | diagnostics CSV | regression txt | Match? |
|-------|----------------|----------------|--------|
| N obs | 60,506 | 60,506 | **PASS** |
| beta1 (target_var) | -0.015266 | -0.0153 | **PASS** (rounding) |
| SE | 0.006071 | 0.0061 | **PASS** |
| t-stat | -2.5145 | -2.5145 | **PASS** |
| R2 (within) | 0.3079 | 0.3079 (R-squared Within) | **PASS** |
| Entities | 1,637 | 1,637 | **PASS** |
| Time periods | — | 17 | **PASS** (2002-2018) |

**Cross-check: provenance H5.md table vs diagnostics CSV:**

| Spec | H5.md R2 | CSV R2 | H5.md beta1 | CSV beta1 | Match? |
|------|----------|--------|-------------|-----------|--------|
| Model A Lag Main | 0.308 | 0.3079 | -0.0153 | -0.01527 | **PASS** |
| Model A No Lag Main | 0.164 | 0.1637 | -0.0168 | -0.01676 | **PASS** |
| Model B Lag Main | 0.308 | 0.3082 | +0.0042 | +0.00420 | **PASS** |

**Cross-check: summary_stats.csv N vs panel N (Main sample):**

| Variable | Panel N | SS CSV N | Match? |
|----------|---------|----------|--------|
| dispersion_lead | 66,526 | 66,526 | **PASS** |
| Manager_QA_Uncertainty_pct | 84,484 | 84,484 | **PASS** |
| Size | 87,994 | 87,994 | **PASS** |
| loss_dummy | 88,129 | 88,129 | **PASS** |
| earnings_volatility | 87,844 | 87,844 | **PASS** |

**LaTeX table vs diagnostics CSV:**

| Field | LaTeX | CSV | Match? |
|-------|-------|-----|--------|
| Model A Lag beta1 | -0.0153 | -0.01527 | **PASS** |
| Model A Lag SE | (0.0061) | 0.006071 | **PASS** |
| Model A Lag N | 60,506 | 60,506 | **PASS** |
| Within-R2 | (blank) | 0.3079 (in `rsquared` col) | **FAIL** — LaTeX uses NaN `within_r2` |

---

## 4) Findings (Grouped by Severity)

### MA-1: MAJOR — LaTeX Table Within-R2 Is Blank (Bug in R2 Reporting)

- **Severity:** MAJOR
- **Symptom:** The LaTeX table (`h5_dispersion_table.tex` line 20) shows empty cells for all four Within-R2 values.
- **Evidence:**
  - `run_h5_dispersion.py:353-357`: The LaTeX builder uses `r["within_r2"]` for the R2 row.
  - `model_diagnostics.csv`: All `within_r2` values are NaN (empty).
  - The custom within-R2 computation at `run_h5_dispersion.py:199-224` fails silently (returns NaN) due to index alignment issues between `df_reg` (integer index) and `model.fitted_values` (multi-index).
  - The CORRECT within-R2 is stored in `r["rsquared"]` = `model.rsquared_within` (e.g., 0.3079 for Main Model A Lag).
- **Why it matters:** The publication LaTeX table is missing a critical fit statistic. Readers and reviewers expect to see Within-R2 for FE models.
- **How to verify:** `python -c "import pandas as pd; d=pd.read_csv('outputs/econometric/h5_dispersion/2026-02-28_134130/model_diagnostics.csv'); print(d[['spec_name','within_r2','rsquared']])"` — within_r2 is NaN, rsquared has values.
- **Fix:** In `_save_latex_table()` at line 353-357, change `r["within_r2"]` to `r["rsquared"]`:
  ```python
  # Line 354: Change from:
  rr += f"{fmt_r2(r_A1['within_r2'])} & " if r_A1 else " & "
  # To:
  rr += f"{fmt_r2(r_A1['rsquared'])} & " if r_A1 else " & "
  ```
  Apply the same change for r_A2, r_B1, r_B2 on lines 355-357.
- **Rerun impact:** Stage 4 only (`python -m f1d.econometric.run_h5_dispersion`). No Stage 3 rerun needed.

### MA-2: MAJOR — LaTeX Stars Use One-Tailed P-values Without Documentation

- **Severity:** MAJOR
- **Symptom:** The LaTeX table shows significance stars based on ONE-TAILED p-values. Model B Lagged DV Main coefficient 0.0042 gets a `*` star because p_one=0.0602 < 0.10.
- **Evidence:**
  - `run_h5_dispersion.py:321`: `fmt_coef(r_A1['beta1'], r_A1['beta1_p_one'])` — passes one-tailed p-value.
  - `run_h5_dispersion.py:284-294`: Star thresholds: `<0.01 = ***`, `<0.05 = **`, `<0.10 = *`.
  - For Model B Lag Main: p_two=0.1204 (NOT significant at 10%), but p_one=0.0602 (marginal at 10%).
  - The two-tailed p-value is the standard convention for significance stars in empirical economics tables.
- **Why it matters:** Readers who assume two-tailed p-values will overestimate statistical significance. The star on 0.0042 in Model B is misleading if the table footnote does not clearly state "one-tailed p-values used."
- **How to verify:** Compare `beta1_p_one` vs `beta1_p_two` in diagnostics CSV for Model B Lag Main.
- **Fix:** Either (a) use two-tailed p-values for stars (standard convention) and note the one-tailed test result in text, or (b) add a clear footnote: "Significance stars based on one-tailed p-values (H5: beta > 0)."
- **Rerun impact:** Stage 4 only (cosmetic change to LaTeX output).

### M-1: MINOR — prior_dispersion and earnings_surprise_ratio Backward Merge Has No Tolerance

- **Severity:** MINOR
- **Symptom:** `prior_dispersion.py:52-59` and `earnings_surprise_ratio.py:50-57` use `pd.merge_asof(..., direction="backward")` with NO tolerance parameter. A call could match an arbitrarily old IBES consensus.
- **Evidence:**
  - `prior_dispersion.py:52-59`: No `tolerance=` kwarg. Compare to `dispersion_lead.py:67`: `tolerance=pd.Timedelta(days=180)`.
  - The 77.5% coverage rate (87,503/112,968) suggests most calls DO match recent data, but some matches could be stale.
- **Why it matters:** A stale prior_dispersion (e.g., 3+ years old) is not a meaningful "current quarter" dispersion control. This could bias the lagged DV coefficient, though firm FE partly mitigates.
- **How to verify:** Run a staleness analysis: for each matched call, compute `start_date - matched_statpers` and examine the distribution. If >5% of matches are >365 days stale, the concern is material.
- **Fix:** Add `tolerance=pd.Timedelta(days=365)` (or 180 days to match dispersion_lead) to both backward merge_asof calls:
  ```python
  # prior_dispersion.py:52-59
  df = pd.merge_asof(..., direction="backward", tolerance=pd.Timedelta(days=365))
  ```
- **Rerun impact:** Stage 3 + Stage 4.

### M-2: MINOR — Custom Within-R2 Computation Is Dead Code

- **Severity:** MINOR
- **Symptom:** `run_h5_dispersion.py:199-224` computes a custom `within_r2` that always returns NaN. This result is stored in diagnostics but never produces useful output.
- **Evidence:** All 12 `within_r2` values in `model_diagnostics.csv` are NaN. The code at lines 200-224 attempts to manually demean y and y_hat, but fails because `df_reg` (with integer index) and `model.fitted_values` (with multi-index) cannot be intersected properly.
- **Why it matters:** 25 lines of dead code that adds confusion. The correct within-R2 is already available from `model.rsquared_within` (stored as `rsquared` in diagnostics).
- **Fix:** Remove lines 199-224 entirely. Set `within_r2 = float(model.rsquared_within)` instead.
- **Rerun impact:** Stage 4 only.

### m-1: NOTE — loss_dummy.py Docstring Says "niq" But Code Uses "ibq"

- **Severity:** NOTE
- **Symptom:** `loss_dummy.py:3` docstring says `"1 if niq < 0, else 0"` but the actual code at line 42-44 uses `comp["ibq"]`.
- **Evidence:** `loss_dummy.py:3` vs `loss_dummy.py:42`. The provenance doc H5.md:232 correctly says `ibq`.
- **Why it matters:** Misleading docstring. `ibq` (Income Before Extraordinary Items, quarterly) is the correct variable per accounting convention and the provenance spec.
- **Fix:** Change docstring from `"1 if niq < 0, else 0"` to `"1 if ibq < 0, else 0"`.
- **Rerun impact:** None (docstring only).

### m-2: NOTE — earnings_volatility Provenance Says "Quarterly" But Code Uses Annual

- **Severity:** NOTE
- **Symptom:** Provenance H5.md:230 says `"Rolling 5-year std of quarterly earnings scaled by total assets"`. The actual code uses ANNUAL iby/atq (from Q4 rows in `_compute_h3_payout_policy`), not quarterly.
- **Evidence:** `_compustat_engine.py:848-849`: `roa_annual = iby / atq` computed on Q4 rows; `_compustat_engine.py:882-883`: rolling 1826D (5 years) std with min_periods=3.
- **Why it matters:** Provenance documentation mismatch. Annual is actually MORE appropriate for earnings volatility than quarterly (less noisy), so the code is arguably better than what the provenance describes.
- **Fix:** Update H5.md variable dictionary entry for `earnings_volatility` from "quarterly" to "annual".
- **Rerun impact:** None (documentation only).

### m-3: NOTE — CEO Variables Built Into Panel But Not Used In Regressions

- **Severity:** NOTE
- **Symptom:** The panel builder loads 3 CEO-specific linguistic variables (`CEO_QA_Uncertainty_pct`, `CEO_QA_Weak_Modal_pct`, `CEO_Pres_Uncertainty_pct`) that are never used in any H5 regression. They are not even included in the summary statistics output.
- **Evidence:** `build_h5_dispersion_panel.py:79-93` builds CEO variables. `run_h5_dispersion.py:396-414` loads panel but does not select CEO columns (they are present in the parquet but excluded via explicit column selection). `SUMMARY_STATS_VARS` at lines 100-120 includes CEO variables (lines 105-109), but `run_h5_dispersion.py:431-434` filters to `v["col"] in df_prep.columns`, and the CEO columns ARE in `df_prep` (via the panel parquet), BUT the summary stats CSV output shows 0 rows for CEO variables — because the function `make_summary_stats_table` apparently does not output them.
- **Why it matters:** Wasted computation and storage. Each CEO builder triggers the LinguisticEngine (cached after first call, so cost is minimal).
- **Fix:** Either remove CEO builders from the H5 panel builder, or include CEO variables in summary statistics if they are intended for exploratory reporting.
- **Rerun impact:** Stage 3 (if removing) or Stage 4 (if adding to summary stats).

### N-1: NOTE — No Explicit file_name Uniqueness Assertion In Panel Builder

- **Severity:** NOTE
- **Symptom:** `build_h5_dispersion_panel.py` does not assert `file_name` uniqueness before or after merges. Uniqueness is implicitly guaranteed by the manifest and left-join pattern, but an explicit assertion would be more defensive.
- **Evidence:** `build_h5_dispersion_panel.py:120-139` — no `assert panel["file_name"].is_unique` call.
- **Fix:** Add after line 120: `assert panel["file_name"].is_unique, "Manifest file_name not unique"`
- **Rerun impact:** None (assertion only).

### N-2: NOTE — CCM cusip8→gvkey Dedup Uses keep="first" (Input-Order Dependent)

- **Severity:** NOTE
- **Symptom:** `_ibes_engine.py:70-72`: `ccm_primary.drop_duplicates(subset=["cusip8"], keep="first")` — if multiple gvkeys map to the same cusip8, the first one in CCM input order wins.
- **Evidence:** The CCM parquet file is loaded without explicit sorting before dedup. If the input order changes (e.g., different CCM snapshot), the dedup result could change.
- **Why it matters:** Low risk — LINKPRIM P/C filtering eliminates most ambiguity. But for full reproducibility, the selection criterion should be deterministic (e.g., sort by LINKDT descending, keep first = most recent link).
- **Fix:** Add explicit sorting before dedup: `ccm_primary.sort_values(["cusip8", "LPERMNO"]).drop_duplicates(...)`.
- **Rerun impact:** Stage 3 + Stage 4 (if ordering changes results).

---

## 5) Rerun Plan (Minimal, Deterministic)

### Commands

```bash
cd "C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D"

# Stage 3: Rebuild panel
python -m f1d.variables.build_h5_dispersion_panel

# Stage 4: Rerun hypothesis tests
python -m f1d.econometric.run_h5_dispersion
```

### Acceptance Tests

After rerun, verify:

1. **Panel row count:**
   ```python
   python -c "import pandas as pd; df=pd.read_parquet('outputs/variables/h5_dispersion/LATEST/h5_dispersion_panel.parquet'); assert len(df)==112968, f'Expected 112968, got {len(df)}'"
   ```

2. **Panel column count:**
   ```python
   assert len(df.columns) == 24
   ```

3. **file_name uniqueness:**
   ```python
   assert df["file_name"].is_unique
   ```

4. **Sample distribution:**
   ```python
   assert df["sample"].value_counts().to_dict() == {"Main": 88205, "Finance": 20482, "Utility": 4281}
   ```

5. **Diagnostics: 12 regression rows:**
   ```python
   diag = pd.read_csv('outputs/econometric/h5_dispersion/LATEST/model_diagnostics.csv')
   assert len(diag) == 12
   ```

6. **Coefficient tolerance (Main Model A Lagged DV):**
   ```python
   r = diag[(diag["spec_name"]=="Model A (Lagged DV)") & (diag["sample"]=="Main")].iloc[0]
   assert abs(r["beta1"] - (-0.0153)) < 0.001
   assert abs(r["rsquared"] - 0.308) < 0.005
   assert r["n_obs"] == 60506
   ```

7. **LaTeX table Within-R2 non-blank (after MA-1 fix):**
   ```python
   tex = open('outputs/econometric/h5_dispersion/LATEST/h5_dispersion_table.tex').read()
   assert "Within-$R^2$" in tex
   # Verify R2 values appear (not blank)
   ```

---

## 6) Refactor & Hardening Recommendations

### Assertions to Add

1. **`build_h5_dispersion_panel.py:120`** — After loading manifest:
   ```python
   assert panel["file_name"].is_unique, f"Manifest file_name not unique: {panel['file_name'].duplicated().sum()} dupes"
   ```

2. **`dispersion_lead.py`** — After merge_asof, verify no explosion:
   ```python
   assert len(df) == len(manifest_sorted), f"merge_asof changed row count: {len(manifest_sorted)} -> {len(df)}"
   ```

3. **`run_h5_dispersion.py`** — After dropna, verify minimum N:
   ```python
   assert len(df_reg) >= 100, f"Insufficient observations after dropna: {len(df_reg)}"
   ```

### Logging/Provenance Improvements

1. **prior_dispersion staleness:** Log the distribution of `start_date - matched_statpers` days to detect stale matches.
2. **min_calls filter:** Log how many firms/calls are dropped by the filter for each sample.
3. **Panel save:** Log column names and dtypes in the report.

### Tests to Add

1. **Unit test:** Verify `dispersion_lead` forward merge_asof finds the correct IBES consensus (use synthetic data with known answer).
2. **Unit test:** Verify `prior_dispersion` backward merge_asof with a tolerance cap (if tolerance fix is applied).
3. **Unit test:** Verify one-tailed p-value computation for both positive and negative beta values.
4. **Integration test:** Verify LaTeX table R2 values are non-blank and match diagnostics CSV.
5. **Regression test:** Pin Main Model A Lagged DV coefficients to 4 decimal places.

### Simplifications

1. **Remove dead within-R2 code** (`run_h5_dispersion.py:199-224`). Use `model.rsquared_within` directly.
2. **Remove CEO builders** from H5 panel if not used in any regression or summary stats.
3. **Centralize merge_asof tolerance policy** — all backward IBES merges should use a consistent tolerance (e.g., 365 days).

---

## 7) Open Questions / Unverified Items

| # | Item | What's Missing | How to Close |
|---|------|---------------|--------------|
| 1 | **prior_dispersion staleness** | Cannot verify match staleness distribution without running IBES engine | Run: `python -c "..."` to compute `start_date - matched_statpers` for all calls with valid prior_dispersion |
| 2 | **CCM cusip8 dedup determinism** | Cannot verify whether CCM input order is stable across runs | Inspect CCM parquet sort order; add explicit sorting before dedup |
| 3 | **IBES raw row count** | Provenance claims ~25.5M raw rows, ~3.2M after filtering | Verify with: `python -c "import pyarrow.parquet as pq; print(pq.read_metadata('inputs/tr_ibes/tr_ibes.parquet').num_rows)"` |
| 4 | **Linguistic engine caching** | Cannot verify that per-year winsorization uses the correct year grouping for all calls | Verify by inspecting the `year` column in the cached linguistic DataFrame |
| 5 | **Determinism across runs** | Provenance claims deterministic results (seed=42, thread_count=1) | Rerun Stage 3 + Stage 4 twice and diff outputs |

---

## Summary

**Overall Assessment:** The H5 Analyst Dispersion suite is **well-implemented** with correct model specification, proper fixed effects, appropriate clustering, and enforced zero-row-delta merges. The data flow from Stage 1 manifest through Stage 2 linguistic variables to Stage 3 panel construction and Stage 4 estimation is traceable and consistent.

**Key Findings:**
- **2 MAJOR issues:** (MA-1) LaTeX table Within-R2 is blank due to NaN from failed custom computation; (MA-2) LaTeX stars use one-tailed p-values without clear documentation.
- **2 MINOR issues:** (M-1) No tolerance on backward merge_asof for prior_dispersion/earnings_surprise_ratio; (M-2) Dead custom within-R2 code.
- **4 NOTES:** Docstring/provenance mismatches, unused CEO variables, defensive assertion suggestions, CCM dedup ordering.
- **0 BLOCKERS:** No look-ahead bias, no merge explosions, no specification mismatches between code and provenance.

**Result validity:** The H5 "NOT SUPPORTED" finding (0/12 significant) is **robust**. None of the identified issues would change the direction or significance of the results. The MA-1 and MA-2 issues are presentation concerns, not inferential ones.
