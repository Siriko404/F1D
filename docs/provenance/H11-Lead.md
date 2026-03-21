# H11-Lead Suite Provenance + Referee Audit

> **Version note (2026-03-21):** Updated after second-layer red-team audit (`H11-Lead_red_team.md`). Key changes: corrected L3 clustering directionality, added missed issues (LaTeX table N/R2, one-tailed stars, Compustat docstring, attrition gap), recalibrated L4/L5/L7 severities.

**Suite ID:** H11-Lead (Political Risk Lead -- Placebo Tests for Reverse Causality)
**Generated:** 2026-03-21
**Method:** Manual code tracing, line-by-line verification against source files

---

## A. Suite Overview

| Field | Value |
|-------|-------|
| Hypothesis ID | H11-Lead |
| Research question | Does *future* firm-level political risk (t+1, t+2) predict *current* managerial speech uncertainty? (Placebo test: expected null result) |
| Unit of observation | Individual earnings call (`file_name`) |
| Panel index passed to PanelOLS | `gvkey` (entity) x `year` (time). **Not unique** -- most (gvkey, year) cells contain multiple calls. PanelOLS treats entity FE at gvkey level, time FE at year level, but the true grain is the call, not the firm-year. |
| Estimator | `linearmodels.panel.PanelOLS` with `EntityEffects + TimeEffects`, `drop_absorbed=True` |
| Standard errors | Clustered by entity (`gvkey`), `cov_type="clustered", cluster_entity=True` |
| Hypothesis test | One-tailed: beta(PRiskQ_lead) > 0, beta(PRiskQ_lead2) > 0 |
| Expected outcome | Insignificant lead coefficients (future PRisk should not cause current speech uncertainty) |
| Regression count | 24 = 4 DVs x 3 samples x 2 IVs |

### Independent Variables

| Variable | Timing | Description |
|----------|--------|-------------|
| `PRiskQ_lead` | Q+1 | Hassan et al. (2019) PRisk from calendar quarter after the call |
| `PRiskQ_lead2` | Q+2 | Hassan et al. (2019) PRisk from two calendar quarters after the call |

### Dependent Variables (4)

1. `Manager_QA_Uncertainty_pct` -- % uncertainty words in manager Q&A turns
2. `CEO_QA_Uncertainty_pct` -- % uncertainty words in CEO Q&A turns
3. `Manager_Pres_Uncertainty_pct` -- % uncertainty words in manager presentation turns
4. `CEO_Pres_Uncertainty_pct` -- % uncertainty words in CEO presentation turns

### Controls (9 base + dynamic presentation control)

| Variable | Description | Source |
|----------|-------------|--------|
| `Analyst_QA_Uncertainty_pct` | Analyst uncertainty in Q&A (always included) | LinguisticEngine |
| `Entire_All_Negative_pct` | Negative sentiment, entire call (LM dictionary) | LinguisticEngine |
| `Size` | ln(atq), natural log of total assets | CompustatEngine |
| `TobinsQ` | (atq + cshoq*prccq - ceqq) / atq | CompustatEngine |
| `ROA` | iby_annual / avg_assets | CompustatEngine |
| `CashHoldings` | cheq / atq | CompustatEngine |
| `DividendPayer` | Binary: dvy_annual (Q4) > 0 | CompustatEngine |
| `firm_maturity` | req / atq (retained earnings / total assets) | CompustatEngine (_compute_h3_payout_policy) |
| `earnings_volatility` | Rolling 5yr std of annual ROA (min 3 obs) | CompustatEngine (_compute_h3_payout_policy) |

**Dynamic presentation control:** When the DV is a Q&A measure, the corresponding Presentation measure is added as a 10th control. Source: `PRES_CONTROL_MAP` dict in runner (lines 115-120).

### Industry Samples

| Sample | Definition |
|--------|-----------|
| Main | FF12 codes not equal to 8 or 11 |
| Finance | FF12 code 11 |
| Utility | FF12 code 8 |

Source: `panel_utils.py::assign_industry_sample()` using `np.select`.

### Minimum Calls Filter

Firms must have >= 5 calls after complete-case deletion within each (sample, DV, IV) combination. Applied via `groupby("gvkey")["file_name"].transform("count") >= 5`. Specs with < 100 remaining observations are skipped entirely.

---

## B. Reproducibility Snapshot

### Commands

```bash
# Stage 3: Build panel
python -m f1d.variables.build_h11_prisk_uncertainty_lead_panel

# Stage 4: Run regressions
python -m f1d.econometric.run_h11_prisk_uncertainty_lead
```

### Key Files

| Role | Path |
|------|------|
| Runner (Stage 4) | `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py` |
| Panel builder (Stage 3) | `src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py` |
| PRiskQ_lead builder | `src/f1d/shared/variables/prisk_q_lead.py` |
| PRiskQ_lead2 builder | `src/f1d/shared/variables/prisk_q_lead2.py` |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` |
| Linguistic engine | `src/f1d/shared/variables/_linguistic_engine.py` |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` |
| Winsorization | `src/f1d/shared/variables/winsorization.py` |
| LaTeX tables | `src/f1d/shared/latex_tables_accounting.py` |
| Project config | `config/project.yaml` |
| Variable config | `config/variables.yaml` |

### Output Artifacts

| Artifact | Path Pattern |
|----------|-------------|
| Panel (parquet) | `outputs/variables/h11_prisk_uncertainty_lead/{timestamp}/h11_prisk_uncertainty_lead_panel.parquet` |
| Regression results | `outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/regression_results_{sample}_{dv}_{lead}.txt` |
| LaTeX table | `outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/h11_prisk_uncertainty_lead_table.tex` |
| Model diagnostics | `outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/model_diagnostics.csv` |
| Summary stats | `outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/summary_stats.csv` |
| Attrition table | `outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/sample_attrition.csv` |

### Year Range

`config/project.yaml`: `year_start: 2002`, `year_end: 2018`.

### Determinism

- `random_seed: 42`, `thread_count: 1`, `sort_inputs: true` (from project.yaml)
- No randomization in the pipeline -- deterministic given same inputs

---

## C. Dependency Chain

```
Stage 1: master_sample_manifest.parquet
    |
    +-- ManifestFieldsBuilder (file_name, gvkey, ff12_code, start_date, ceo_id, ceo_name)
    |
Stage 2: linguistic_variables_{year}.parquet (via LinguisticEngine)
    |
    +-- ManagerQAUncertaintyBuilder   --> Manager_QA_Uncertainty_pct
    +-- CEOQAUncertaintyBuilder       --> CEO_QA_Uncertainty_pct
    +-- ManagerPresUncertaintyBuilder  --> Manager_Pres_Uncertainty_pct
    +-- CEOPresUncertaintyBuilder      --> CEO_Pres_Uncertainty_pct
    +-- AnalystQAUncertaintyBuilder    --> Analyst_QA_Uncertainty_pct
    +-- NegativeSentimentBuilder       --> Entire_All_Negative_pct
    |
External: inputs/FirmLevelRisk/firmquarter_2022q1.csv (Hassan et al. 2019)
    |
    +-- PRiskQLeadBuilder   --> PRiskQ_lead  (cal Q+1)
    +-- PRiskQLead2Builder  --> PRiskQ_lead2 (cal Q+2)
    |
Compustat quarterly (via CompustatEngine, merge_asof backward by gvkey)
    |
    +-- SizeBuilder             --> Size
    +-- BookLevBuilder          --> BookLev  (LOADED BUT NOT USED IN REGRESSION)
    +-- ROABuilder              --> ROA
    +-- TobinsQBuilder          --> TobinsQ
    +-- CashHoldingsBuilder     --> CashHoldings
    +-- DividendPayerBuilder    --> DividendPayer
    +-- FirmMaturityBuilder     --> firm_maturity
    +-- EarningsVolatilityBuilder --> earnings_volatility
    |
    v
Panel Builder (build_h11_prisk_uncertainty_lead_panel.py)
    |-- Left-merge all builders onto manifest by file_name (zero row-delta enforced)
    |-- assign_industry_sample(ff12_code)
    |-- year = start_date.dt.year
    |-- cal_q = year + "q" + quarter
    |-- Save parquet
    |
    v
Runner (run_h11_prisk_uncertainty_lead.py)
    |-- Load panel parquet
    |-- assign_industry_sample if missing
    |-- For each (iv, dv, sample): complete-case + min-calls filter -> PanelOLS
    |-- One-tailed p-value: p_two/2 if beta > 0, else 1 - p_two/2
    |-- Save LaTeX table, diagnostics CSV, attrition table
```

---

## D. Data Provenance

### D1. Master Manifest

- **Source:** `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`
- **Key columns used:** `file_name`, `gvkey`, `ff12_code`, `start_date`, `ceo_id`, `ceo_name`
- **Resolution:** latest timestamp subdirectory via `get_latest_output_dir()`

### D2. Linguistic Variables

- **Source:** `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet`
- **Engine:** `_linguistic_engine.py::LinguisticEngine` (singleton, cached)
- **Winsorization:** Per-year 0%/99% (upper-only, `lower=0.0, upper=0.99`) via `winsorize_by_year()`
- **Columns used:** `Manager_QA_Uncertainty_pct`, `CEO_QA_Uncertainty_pct`, `Manager_Pres_Uncertainty_pct`, `CEO_Pres_Uncertainty_pct`, `Analyst_QA_Uncertainty_pct`, `Entire_All_Negative_pct`

### D3. Hassan et al. (2019) Political Risk

- **Source:** `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (TAB-separated)
- **Columns:** `gvkey`, `date` (format "YYYYqQ"), `PRisk`
- **gvkey formatting:** zero-padded to 6 digits
- **Deduplication:** `sort_values("PRisk", ascending=False).drop_duplicates(subset=["gvkey", "cal_q"], keep="first")` -- keeps **max PRisk** per firm-quarter
- **Year filter (lead-1):** `years` + `max(years) + 1` -- extends one year forward for Q4 lead matches
- **Year filter (lead-2):** `years` + `max(years) + 1` + `max(years) + 2` -- extends two years forward
- **Winsorization:** Per-year 1%/99% via `winsorize_by_year()` applied BEFORE merge to calls

### D4. Compustat Quarterly

- **Source:** Raw Compustat quarterly file loaded by `CompustatEngine`
- **Match to calls:** `merge_asof` backward on `start_date` by `gvkey`
- **Deduplication:** `(gvkey, datadate)` deduplicated, keeps last row (most recent restatement)
- **Winsorization:** Per-year (fyearq) 1%/99% via internal `_winsorize_by_year()` on all ratio columns

---

## E. Merge & Sample Construction Audit

### E1. Panel Builder Merge Strategy

All builders return `(file_name, variable_column)` DataFrames. They are merged sequentially onto the manifest via `panel.merge(data, on="file_name", how="left")`. After each merge, a row-delta check enforces zero change:

```python
delta = after_len - before_len
if delta != 0:
    raise ValueError(f"Merge '{name}' changed rows {before_len} -> {after_len}")
```

**Code ref:** `build_h11_prisk_uncertainty_lead_panel.py`, lines 147-152.

### E2. Lead Variable Construction

**PRiskQ_lead (1-quarter lead):**
1. Compute `cal_q` from `start_date` (e.g., "2010q2")
2. Compute `cal_q_lead = _get_next_quarter(cal_q)` (e.g., "2010q3"; "2010q4" -> "2011q1")
3. Merge manifest on `(gvkey, cal_q_lead)` with PRisk data on `(gvkey, cal_q)`
4. `drop_duplicates(subset=["file_name"])` to ensure one row per call

**PRiskQ_lead2 (2-quarter lead):**
1. Same as above but uses `_get_next2_quarter()` (e.g., "2010q2" -> "2010q4"; "2010q3" -> "2011q1")
2. Year filter extends 2 years forward for cross-year matches

### E3. Runner Sample Filtering

For each (IV, DV, sample) combination:
1. `prepare_regression_data()`: complete-case deletion on `[dv, iv] + controls + ["gvkey", "year"]` after replacing inf with NaN
2. Filter by sample (Main/Finance/Utility)
3. `min_calls` filter: `groupby("gvkey")["file_name"].transform("count") >= 5`
4. Skip if < 100 observations remain

**Code ref:** `run_h11_prisk_uncertainty_lead.py`, lines 159-177 (prepare), lines 520-539 (filter).

---

## F. Variable Dictionary

| Variable | Role | Formula/Source | Winsorization | Standardization |
|----------|------|----------------|---------------|-----------------|
| `Manager_QA_Uncertainty_pct` | DV | LM uncertainty dictionary / Q&A manager turns | Per-year 0%/99% (upper-only) | None |
| `CEO_QA_Uncertainty_pct` | DV | LM uncertainty dictionary / Q&A CEO turns | Per-year 0%/99% (upper-only) | None |
| `Manager_Pres_Uncertainty_pct` | DV | LM uncertainty dictionary / Presentation manager turns | Per-year 0%/99% (upper-only) | None |
| `CEO_Pres_Uncertainty_pct` | DV | LM uncertainty dictionary / Presentation CEO turns | Per-year 0%/99% (upper-only) | None |
| `PRiskQ_lead` | IV | Hassan et al. (2019) PRisk, calendar quarter Q+1 | Per-year 1%/99% | None |
| `PRiskQ_lead2` | IV | Hassan et al. (2019) PRisk, calendar quarter Q+2 | Per-year 1%/99% | None |
| `Analyst_QA_Uncertainty_pct` | Control | LM uncertainty dictionary / Q&A analyst turns | Per-year 0%/99% (upper-only) | None |
| `Entire_All_Negative_pct` | Control | LM negative dictionary / entire call | Per-year 0%/99% (upper-only) | None |
| `Size` | Control | ln(atq), atq > 0 only | Per-year (fyearq) 1%/99% | None |
| `TobinsQ` | Control | (atq + cshoq*prccq - ceqq) / atq | Per-year (fyearq) 1%/99% | None |
| `ROA` | Control | iby_annual / avg_assets | Per-year (fyearq) 1%/99% | None |
| `CashHoldings` | Control | cheq / atq | Per-year (fyearq) 1%/99% | None |
| `DividendPayer` | Control (binary) | dvy_annual (Q4) > 0 | Not winsorized | None |
| `firm_maturity` | Control | req / atq | Per-year (fyearq) 1%/99% | None |
| `earnings_volatility` | Control | Rolling 5yr std of annual ROA (min 3 periods) | Per-year (fyearq) 1%/99% | None |
| `BookLev` | Loaded, unused | (dlcq + dlttq) / atq | Per-year (fyearq) 1%/99% | None |

---

## G. Outliers / Missing / Scaling

### G1. Winsorization Summary

| Variable group | Method | Bounds | Year grouping | Code location |
|----------------|--------|--------|---------------|---------------|
| Linguistic _pct variables | Per-year, upper-only | 0%/99% | Year from filename | `_linguistic_engine.py` line 255 |
| PRiskQ (lead/lead2) | Per-year | 1%/99% | Year from cal_q | `prisk_q_lead.py` line 170, `prisk_q_lead2.py` line 173 |
| Compustat ratios (Size, TobinsQ, ROA, CashHoldings, firm_maturity, earnings_volatility) | Per-year | 1%/99% | fyearq | `_compustat_engine.py` lines 1191-1215 |
| DividendPayer | Not winsorized | N/A | N/A | Binary variable, excluded from winsorization |

### G2. Missing Data Handling

- **inf replacement:** Runner replaces `[np.inf, -np.inf]` with NaN before complete-case deletion (`run_h11_prisk_uncertainty_lead.py` line 175)
- **Complete-case deletion:** `.dropna(subset=required)` on all required columns (line 175)
- **PRisk missing:** Left merge, so calls without PRisk match get NaN and are dropped during complete-case deletion
- **Compustat missing:** merge_asof backward -- calls without Compustat match get NaN

### G3. Scaling

**No standardization is applied to any variable.** The LaTeX table notes claim "All continuous controls are standardized" (line 399) but this claim is **FALSE** -- there is no standardization code anywhere in the runner or panel builder.

---

## H. Estimation Spec Register

### H1. Model Formula

For each (DV, IV, sample) combination:

```
DV ~ 1 + IV + Analyst_QA_Uncertainty_pct + Entire_All_Negative_pct + Size + TobinsQ + ROA + CashHoldings + DividendPayer + firm_maturity + earnings_volatility [+ Pres_control if DV is QA] + EntityEffects + TimeEffects
```

### H2. Dynamic Control Logic

| DV | Dynamic Pres Control Added |
|----|---------------------------|
| Manager_QA_Uncertainty_pct | Manager_Pres_Uncertainty_pct |
| CEO_QA_Uncertainty_pct | CEO_Pres_Uncertainty_pct |
| Manager_Pres_Uncertainty_pct | None |
| CEO_Pres_Uncertainty_pct | None |

Source: `PRES_CONTROL_MAP` dict, runner lines 115-120.

### H3. Full Spec Grid

| # | IV | DV | Sample | Controls (count) |
|---|----|----|--------|-----------------|
| 1-4 | PRiskQ_lead | 4 DVs | Main | 10 (QA) or 9 (Pres) |
| 5-8 | PRiskQ_lead | 4 DVs | Finance | 10 or 9 |
| 9-12 | PRiskQ_lead | 4 DVs | Utility | 10 or 9 |
| 13-16 | PRiskQ_lead2 | 4 DVs | Main | 10 or 9 |
| 17-20 | PRiskQ_lead2 | 4 DVs | Finance | 10 or 9 |
| 21-24 | PRiskQ_lead2 | 4 DVs | Utility | 10 or 9 |

Total: **24 regressions** (some may be skipped if < 100 obs).

### H4. PanelOLS Mechanics

- `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`
- `fit(cov_type="clustered", cluster_entity=True)`
- Panel index: `df_sample.set_index(["gvkey", "year"])` (runner line 203)
- Entity FE = gvkey, Time FE = year

### H5. Hypothesis Test

- One-tailed: `p_one = p_two / 2` if `beta > 0`, else `p_one = 1 - p_two / 2`
- Significance threshold: `p_one < 0.05 and beta > 0`
- **Expected result for placebo:** insignificant (failure to reject null)

---

## I. Verification Log

| Check | Method | Result |
|-------|--------|--------|
| Zero row-delta merge in panel builder | Code inspection: lines 147-152 of panel builder | Confirmed: raises ValueError on delta != 0 |
| PRiskQ_lead next-quarter logic | `_get_next_quarter`: Q4 -> next year Q1, else Q+1 | Correct (prisk_q_lead.py lines 69-82) |
| PRiskQ_lead2 two-quarter logic | `_get_next2_quarter`: Q3->Y+1Q1, Q4->Y+1Q2, else Q+2 | Correct (prisk_q_lead2.py lines 69-85) |
| Year extension for lead matches | Lead-1: appends max(years)+1. Lead-2: appends max(years)+1 AND +2 | Correct: ensures cross-year lead matches are available |
| PRisk deduplication | Keeps max PRisk per (gvkey, cal_q) | Confirmed: sort descending, drop_duplicates keep="first" |
| Complete-case deletion | inf -> NaN, then dropna on required cols | Confirmed: runner line 175 |
| min_calls filter | groupby gvkey count >= 5 | Confirmed: runner lines 527-530 |
| One-tailed p-value formula | p/2 if beta > 0, 1-p/2 otherwise | Correct for one-sided H_a: beta > 0 |
| Standardization claim in LaTeX notes | Searched for standardize/zscore/normalize/scale in runner | **FALSE CLAIM**: no standardization code exists |
| BookLev loaded but unused | Panel builder loads BookLevBuilder; runner BASE_CONTROLS does not include BookLev | Confirmed: dead variable in panel |
| Winsorization claim in LaTeX notes | "Variables are winsorized at 1%/99% by year" | Partially accurate: PRisk and Compustat use 1%/99%, but linguistic variables use 0%/99% (upper-only) |

---

## J. Known Issues

### J1. FALSE: "All continuous controls are standardized" claim in LaTeX table

The LaTeX table note (runner line 399) states: "All continuous controls are standardized." This is **false**. There is no standardization (z-scoring, min-max, or any other scaling) applied to any variable at any point in the pipeline. The regression coefficients are in raw (winsorized) units, not standardized units.

**Severity:** HIGH -- misleads readers about coefficient interpretation.

### J2. Non-unique panel index (gvkey x year)

The panel is indexed by `(gvkey, year)` for PanelOLS, but the unit of observation is the individual call. Multiple calls per firm-year are common. PanelOLS treats this as an unbalanced panel without complaint, but:
- Entity FE demeans at gvkey level, time FE at year level
- Within-R-squared may be misleadingly low or high
- Standard errors are clustered at gvkey (correct for within-firm correlation)

**Severity:** LOW-MEDIUM -- standard practice in earnings-call research, but should be disclosed.

### J3. BookLev loaded but unused

`BookLevBuilder` is instantiated and merged in the panel builder (line 116) but `BookLev` never appears in `BASE_CONTROLS` in the runner. This is dead code that wastes memory and processing time.

**Severity:** LOW -- no impact on results, minor code hygiene issue.

### J4. Inconsistent winsorization bounds across variable types

| Variable type | Lower | Upper |
|---------------|-------|-------|
| Linguistic _pct | 0% | 99% |
| PRisk | 1% | 99% |
| Compustat ratios | 1% | 99% |

Linguistic variables use asymmetric (upper-only) winsorization because percentage values have a natural floor of 0. The LaTeX table note says "Variables are winsorized at 1%/99% by year" which is incomplete -- linguistic variables use 0%/99%.

**Severity:** LOW -- the asymmetry is defensible for percentage variables, but the table note is imprecise.

### J5. max-PRisk deduplication strategy

When multiple PRisk values exist for the same (gvkey, cal_q), the code keeps the maximum. This is an undisclosed assumption. The original Hassan et al. data should have one observation per firm-quarter; duplicates suggest data quality issues in the source file.

**Severity:** LOW-MEDIUM -- depends on actual duplicate prevalence.

---

## K. Referee Assessment

### K1. Identification

**Design:** H11-Lead is a placebo test. The identification claim is that if contemporaneous PRisk causes speech uncertainty (H11-Base), then *future* PRisk (lead) should NOT predict current speech uncertainty. Insignificant lead coefficients support the causal direction Base -> speech.

**Assessment:**
- The placebo design is standard and well-motivated.
- However, the one-tailed test (H_a: beta > 0) is inappropriate for a placebo test. A placebo test should use a **two-tailed** test or simply report significance, because the null hypothesis *is* the desired outcome. Testing one-tailed against the alternative that lead PRisk *increases* uncertainty is conceptually confused -- the point is to show the lead coefficient is *not significant in either direction*.
- If the lead coefficient is significantly *negative*, the one-tailed test would report it as "no" (insignificant), potentially hiding a problematic negative association.

**Recommendation:** Report two-tailed p-values for placebo tests.

### K2. Inference

**Clustering:** Entity-clustered standard errors (gvkey). This accounts for within-firm serial correlation across calls.

**Issues:**
1. **No double-clustering (firm + time):** If political risk has cross-sectional correlation within calendar quarters (as it likely does -- political risk is partly aggregate), entity-only clustering understates standard errors. Double-clustering by (gvkey, year) or (gvkey, cal_q) would be more conservative. However, for a placebo test where the desired outcome is insignificance, entity-only clustering is actually **conservative** for the researcher's conclusion -- understated SEs produce smaller p-values, making it *harder* to show insignificance (more likely to find spurious significance). Double-clustering would *increase* SEs and make it *easier* to show non-significance, which would be *anti-conservative* for the placebo claim. The recommendation to double-cluster remains reasonable for robustness, but the directionality concern is favorable, not adverse.
2. **Multiple testing:** 24 regressions with no family-wise error rate correction. Even under the null, ~1.2 of 24 tests may appear significant at 5%. No Bonferroni, Holm, or FDR adjustment is applied or discussed. However, for a placebo test seeking non-significance, the absence of correction is conservative for the researcher's argument: it makes it easier for any one test to appear significant, which would undermine the placebo claim. Severity downgraded to LOW-MEDIUM.
3. **Call-level clustering within firm-years:** Multiple calls per firm-year create within-group correlation that is absorbed by firm FE but may affect residual variance estimation.

### K3. Robustness

**Missing robustness checks:**
1. No Newey-West or HAC standard errors as alternative.
2. No subsample stability analysis (e.g., pre/post-2008, by firm size quartile).
3. No permutation test or randomization inference to validate the placebo structure.
4. No comparison with contemporaneous PRisk effect in the same table (the reader must look at H11-Base separately).
5. No Granger-causality framework that would jointly test lags and leads.

### K4. Variable Construction

**PRisk lead matching:**
- The lead is based on *calendar* quarter, not fiscal quarter. This is appropriate since Hassan et al. (2019) report PRisk by calendar quarter.
- The `_get_next_quarter` and `_get_next2_quarter` functions are correctly implemented (verified in Section I).
- PRisk is winsorized *before* merging to calls, which is correct (avoids look-ahead bias from call-conditional winsorization).

**Control variables:**
- `firm_maturity` is defined as `req / atq` (retained earnings / total assets), which is the DeAngelo et al. (2006) RE/TA ratio, not years since IPO or first Compustat appearance. The runner docstring reference to "Years since first Compustat appearance" could not be verified at the cited location (see L7, reclassified as UNVERIFIABLE). Additionally, the Compustat engine's own docstring (`_compute_h3_payout_policy`, line 784) incorrectly labels this as "RE / TE (retained earnings / total equity)" when the code actually divides by total assets (`req / atq`, line 849) -- see L13.
- `earnings_volatility` is rolling 5-year std of annual ROA (iby/atq), computed on Q4-only annual data with a `1826D` rolling window and `min_periods=3`. This is well-specified.

### K5. Interpretation

**Placebo logic:**
- A well-designed placebo test. If lead coefficients are insignificant while contemporaneous/lag coefficients are significant, it supports the temporal ordering of the causal mechanism.
- However, the interpretation depends on the *relative* magnitude: a lead coefficient that is insignificant but of similar magnitude to the contemporaneous coefficient would be concerning (suggests lack of power, not causal direction).
- The table should ideally present base, lag, and lead results side-by-side for direct comparison.

**Coefficient interpretation:**
- The LaTeX table notes falsely claim standardization (see J1). If coefficients are presented as raw, readers need variable units to interpret magnitude. This is not harmful per se, but the false claim undermines trust.

### K6. Academic Integrity

**Issues identified:**
1. **False standardization claim** (J1): The LaTeX table notes assert "All continuous controls are standardized" but no standardization is performed. This is a material misrepresentation.
2. **Imprecise winsorization claim** (J4): "Variables are winsorized at 1%/99% by year" omits that linguistic variables use 0%/99%.
3. **Incorrect firm_maturity description**: The runner docstring (line 111) allegedly describes `firm_maturity` as "Years since first Compustat appearance" but the actual variable is RE/TA. **Red-team reclassified as UNVERIFIABLE** -- cited text not found at the stated location. Separately, the Compustat engine docstring (line 784) mislabels the denominator as "TE" (total equity) when the code uses "TA" (total assets).

### K7. Completeness

**What is present:**
- Model diagnostics CSV with all coefficients, SEs, p-values, R-squared
- LaTeX table with lead-1 and lead-2 results
- Summary statistics
- Sample attrition table
- Run manifest for reproducibility

**What is missing:**
- No comparison table with contemporaneous H11-Base results
- No power analysis (can this test detect a meaningful positive effect if it existed?)
- No coefficient comparison across base/lag/lead to show the attenuation pattern
- No discussion of what "insignificance" means quantitatively (what effect size can be ruled out?)

---

## L. Issue Register

| ID | Severity | Category | Description | Location |
|----|----------|----------|-------------|----------|
| L1 | HIGH | Integrity | LaTeX table notes falsely claim "All continuous controls are standardized" -- no standardization exists | `run_h11_prisk_uncertainty_lead.py` line 399 |
| L2 | MEDIUM | Identification | One-tailed test inappropriate for placebo design -- should use two-tailed | `run_h11_prisk_uncertainty_lead.py` lines 226-232 |
| L3 | MEDIUM | Inference | Entity-only clustering may understate SEs when PRisk has cross-sectional correlation. **Note:** directionality is actually *conservative* for placebo (understated SEs make it harder to show insignificance). Double-clustering recommended for robustness but is not adverse. | `run_h11_prisk_uncertainty_lead.py` line 207 |
| L4 | LOW-MEDIUM | Inference | 24 regressions with no multiple testing correction. Absence of correction is conservative for placebo claims (makes it easier for any one test to appear significant, undermining the placebo). | Runner loop structure, lines 509-553 |
| L5 | LOW-MEDIUM | Panel index | Non-unique (gvkey, year) panel index not disclosed; multiple calls per firm-year. Standard practice in earnings-call research. | `run_h11_prisk_uncertainty_lead.py` line 203 |
| L6 | LOW | Integrity | Imprecise winsorization claim: "1%/99%" omits linguistic variables use 0%/99% | `run_h11_prisk_uncertainty_lead.py` line 400 |
| L7 | UNVERIFIABLE | Integrity | Runner docstring allegedly describes firm_maturity as "Years since first Compustat appearance" -- actual formula is RE/TA. **Red-team could not find cited text at runner line 111; reclassified as unverifiable in this runner.** | Docstring at runner line 111 (implicit from control list) |
| L8 | LOW | Code hygiene | BookLev variable loaded in panel builder but never used in regression | `build_h11_prisk_uncertainty_lead_panel.py` line 116 |
| L9 | LOW | Data quality | PRisk deduplication keeps max value per (gvkey, cal_q) -- undisclosed assumption | `prisk_q_lead.py` lines 116-118 |
| L10 | LOW | Robustness | No power analysis or minimum detectable effect size reported for placebo test | Missing from outputs |
| L11 | LOW-MEDIUM | Presentation | LaTeX table shows Observations and Within-R-squared from lead-1 regressions only; lead-2 regressions may have different sample sizes due to differential missingness. A reader seeing both lead horizons with a single N row may assume they share the same estimation sample. | `run_h11_prisk_uncertainty_lead.py` lines 371-384 |
| L12 | LOW | Presentation | LaTeX significance stars use one-tailed p-values (via `fmt_coef` receiving `beta_prisk_p_one`), compounding the one-tailed test concern (L2). For a placebo test, this inflates apparent significance of positive coefficients. | `run_h11_prisk_uncertainty_lead.py` lines 290, 330-333 |
| L13 | LOW | Documentation | Compustat engine docstring (`_compute_h3_payout_policy`, line 784) describes `firm_maturity` as "RE / TE (retained earnings / total equity)" but the actual formula (line 849) computes `req / atq` (retained earnings / total assets). | `src/f1d/shared/variables/_compustat_engine.py` lines 784, 849 |
| L14 | LOW | Documentation | Attrition table covers only one DV path (`n_obs` from the first Main/PRiskQ_lead result). Different DVs (especially CEO measures) have different missingness patterns, so the attrition table underrepresents variation in sample loss across specifications. | `run_h11_prisk_uncertainty_lead.py` lines 558-569 |

---

## M. Priority Fixes

### M1 (HIGH) -- Remove false standardization claim

**File:** `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`, line 399

**Current:** `"All continuous controls are standardized. ",`

**Fix:** Either (a) remove the claim, or (b) implement actual standardization. If standardizing, apply z-score transformation within the `prepare_regression_data()` function after complete-case deletion, and document the transformation.

### M2 (MEDIUM) -- Switch placebo test to two-tailed

**File:** `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`, lines 226-232

For a placebo test, report two-tailed p-values. The one-tailed test tests for the *presence* of a positive effect, but the placebo's value is in demonstrating the *absence* of any effect.

### M3 (MEDIUM) -- Consider double-clustering or discuss limitation

Entity-only clustering may understate SEs when PRisk has cross-sectional correlation. For a placebo test, this is actually *conservative* (understated SEs make it harder to show insignificance). Double-clustering by (gvkey, year) remains recommended for robustness and transparency, but the directionality is favorable for the placebo conclusion.

### M4 (LOW) -- Fix firm_maturity docstring in Compustat engine

The Compustat engine docstring (`_compute_h3_payout_policy`, line 784) says "RE / TE (retained earnings / total equity)" but the code computes `req / atq` (RE / TA). Correct the docstring to say "RE / TA (retained earnings / total assets)." The runner docstring claim (L7) could not be verified at the cited location.

### M5 (LOW) -- Remove unused BookLev from panel builder

Remove the `BookLevBuilder` instantiation from `build_h11_prisk_uncertainty_lead_panel.py` line 116 since the variable is not used in any H11-Lead regression.

---

## N. Final Readiness Statement

**Status: CONDITIONALLY READY -- requires fixes before submission**

The H11-Lead suite implements a standard placebo test for reverse causality in the political risk / uncertainty relationship. The core pipeline is mechanically sound: lead variable construction is correct, merge integrity is enforced, winsorization is consistent with other suites, and the estimation uses appropriate fixed effects.

However, three issues must be resolved before thesis submission:

1. **Critical fix required:** The false "standardized" claim in the LaTeX table notes (L1) is a material misrepresentation that would fail any referee or replication audit.

2. **Design concern:** The one-tailed hypothesis test (L2) is conceptually inappropriate for a placebo test. Placebos demonstrate the *absence* of effect, not the presence of a directional one. Two-tailed p-values should be reported.

3. **Inference concern:** Entity-only clustering (L3) may understate SEs when the IV has cross-sectional dependence. For a placebo test, this is actually *conservative* (harder to show insignificance), but double-clustered SEs should be reported as a robustness check for transparency.

The remaining issues (L4-L14) are minor and can be addressed through documentation fixes and code cleanup without affecting the core results.
