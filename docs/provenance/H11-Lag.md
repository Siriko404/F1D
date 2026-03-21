# H11-Lag Suite Provenance + Referee Audit

**Suite ID:** H11-Lag
**Generated:** 2026-03-21 (manual code-tracing provenance + referee audit)
**Method:** Independent line-by-line code verification against source files
**Version:** 1.1 (2026-03-21) -- Updated per red-team audit (H11-Lag_red_team.md): corrected firm_maturity label (RE/TE -> RE/TA), added docstring bug note for _get_prev2_quarter, added LaTeX star one-tailed p-value issue, added n_firms/n_clusters overcount note, recalibrated I-01 severity from HIGH to MEDIUM, added I-10 (LaTeX stars use one-tailed p without disclosure).

---

## A. Suite Overview

| Field | Value |
|-------|-------|
| Hypothesis ID | H11-Lag -- Lagged Political Risk & Language Uncertainty |
| Research question | Does prior-quarter firm-level political risk exposure (Hassan et al. 2019) predict managerial speech uncertainty in subsequent earnings calls? |
| Unit of observation | Individual earnings call (`file_name`) |
| Panel index passed to PanelOLS | `gvkey` (entity) x `year` (time). **Not unique per call**: most (gvkey, year) cells contain multiple calls (quarterly earnings). PanelOLS accepts this silently; entity FE demeans at gvkey level, time FE at year level. |
| Estimator | `linearmodels.panel.PanelOLS` with `EntityEffects + TimeEffects`, `drop_absorbed=True` |
| Standard errors | Clustered by entity (`gvkey`), `cov_type="clustered", cluster_entity=True` |
| Hypothesis test | One-tailed: beta(PRiskQ_lag) > 0 and beta(PRiskQ_lag2) > 0 |
| Regression count | 4 DVs x 3 samples x 2 IVs = **24 regressions** |
| Sample period | 2002--2018 (config/project.yaml: `year_start: 2002`, `year_end: 2018`) |

### Independent variables

| IV Variable | Timing | Description |
|-------------|--------|-------------|
| `PRiskQ_lag` | Q-1 (1-quarter lag) | Hassan et al. PRisk from the calendar quarter immediately preceding the call quarter |
| `PRiskQ_lag2` | Q-2 (2-quarter lag) | Hassan et al. PRisk from two calendar quarters before the call quarter |

### Dependent variables (4)

1. `Manager_QA_Uncertainty_pct` -- % uncertainty words in manager Q&A turns (LM dictionary)
2. `CEO_QA_Uncertainty_pct` -- % uncertainty words in CEO Q&A turns
3. `Manager_Pres_Uncertainty_pct` -- % uncertainty words in manager presentation turns
4. `CEO_Pres_Uncertainty_pct` -- % uncertainty words in CEO presentation turns

### Controls (9 base + dynamic presentation control)

| Variable | Definition | Source |
|----------|-----------|--------|
| `Analyst_QA_Uncertainty_pct` | Analyst uncertainty in Q&A (always included) | LinguisticEngine / Stage 2 |
| `Entire_All_Negative_pct` | Negative sentiment, entire call (LM dictionary) | LinguisticEngine / Stage 2 |
| `Size` | ln(atq), atq > 0 only (MAJOR-6 fix) | CompustatEngine |
| `TobinsQ` | (mktcap + debt_book) / atq | CompustatEngine |
| `ROA` | iby_annual / avg_assets | CompustatEngine |
| `CashHoldings` | cheq / atq | CompustatEngine |
| `DividendPayer` | Binary: dvy_annual > 0 (Q4-only full-year, CRITICAL-2 fix) | CompustatEngine |
| `firm_maturity` | RE / TA (req / atq) | CompustatEngine (_compute_h3_payout_policy) |
| `earnings_volatility` | Rolling 5-year std of annual ROA (iby/atq) | CompustatEngine (_compute_h3_payout_policy) |

**Dynamic presentation control:** When the DV is a Q&A measure, the corresponding Presentation measure is added as a 10th control (`Manager_Pres_Uncertainty_pct` for Manager_QA DV, `CEO_Pres_Uncertainty_pct` for CEO_QA DV). No presentation control is added when the DV is itself a Presentation measure. Source: `PRES_CONTROL_MAP` dict in runner (lines 112--117).

### Industry samples

| Sample | Definition | Source |
|--------|-----------|--------|
| Main | FF12 codes != 8 and != 11 | `panel_utils.py::assign_industry_sample()` via `np.select` |
| Finance | FF12 code == 11 | Same function |
| Utility | FF12 code == 8 | Same function |

### Minimum calls filter

Firms must have >= 5 calls after complete-case deletion within each (sample, DV, IV) combination. Applied via `groupby("gvkey")["file_name"].transform("count") >= 5` in runner (lines 523--528). Specs with fewer than 100 remaining observations are skipped entirely (line 534).

---

## B. Reproducibility Snapshot

### Commands

```bash
# Stage 3: Build panel
python -m f1d.variables.build_h11_prisk_uncertainty_lag_panel

# Stage 4: Run regressions
python -m f1d.econometric.run_h11_prisk_uncertainty_lag
```

### Prerequisites

| Prerequisite | Path |
|-------------|------|
| Master manifest | `outputs/1.4_AssembleManifest/{timestamp}/master_sample_manifest.parquet` |
| Linguistic variables | `outputs/2_Textual_Analysis/2.2_Variables/{timestamp}/linguistic_variables_{year}.parquet` |
| PRisk quarterly data | `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (TAB-separated) |
| Compustat quarterly | `inputs/comp_na_daily_all/comp_na_daily_all.parquet` |
| Python 3.9+ | `linearmodels`, `pandas`, `numpy`, `statsmodels`, `pyarrow` |
| Config | `config/project.yaml` (year_start=2002, year_end=2018, random_seed=42) |

### Expected outputs

| Stage | Output | Location |
|-------|--------|----------|
| Stage 3 | Panel parquet | `outputs/variables/h11_prisk_uncertainty_lag/{ts}/h11_prisk_uncertainty_lag_panel.parquet` |
| Stage 3 | Summary stats | `outputs/variables/h11_prisk_uncertainty_lag/{ts}/summary_stats.csv` |
| Stage 3 | Run manifest | `outputs/variables/h11_prisk_uncertainty_lag/{ts}/run_manifest.json` |
| Stage 4 | 24 regression text files | `outputs/econometric/h11_prisk_uncertainty_lag/{ts}/regression_results_{sample}_{dv}_{lag1\|lag2}.txt` |
| Stage 4 | Model diagnostics CSV | `outputs/econometric/h11_prisk_uncertainty_lag/{ts}/model_diagnostics.csv` |
| Stage 4 | LaTeX regression table | `outputs/econometric/h11_prisk_uncertainty_lag/{ts}/h11_prisk_uncertainty_lag_table.tex` |
| Stage 4 | Summary stats CSV + TeX | `outputs/econometric/h11_prisk_uncertainty_lag/{ts}/summary_stats.{csv,tex}` |
| Stage 4 | Attrition table | `outputs/econometric/h11_prisk_uncertainty_lag/{ts}/sample_attrition.{csv,tex}` |

### Verified output (latest run: 2026-03-18_164810)

24/24 regression text files present. Summary stats CSV + TeX present.
**Missing from latest run:** `model_diagnostics.csv`, `h11_prisk_uncertainty_lag_table.tex`, `sample_attrition.csv`, `sample_attrition.tex`. These files exist in earlier runs (e.g., 2026-03-09). This indicates the latest run crashed or exited before the post-regression aggregation step. See Issue Register I-01.

---

## C. Dependency Chain

```
config/project.yaml
  --> build_h11_prisk_uncertainty_lag_panel.py (Stage 3)
        |-- ManifestFieldsBuilder --> outputs/1.4_AssembleManifest/.../master_sample_manifest.parquet
        |-- ManagerQAUncertaintyBuilder --> LinguisticEngine --> outputs/2_Textual_Analysis/2.2_Variables/.../linguistic_variables_{year}.parquet
        |-- CEOQAUncertaintyBuilder --> LinguisticEngine (cached)
        |-- ManagerPresUncertaintyBuilder --> LinguisticEngine (cached)
        |-- CEOPresUncertaintyBuilder --> LinguisticEngine (cached)
        |-- AnalystQAUncertaintyBuilder --> LinguisticEngine (cached)
        |-- NegativeSentimentBuilder --> LinguisticEngine (cached)
        |-- PRiskQLagBuilder --> inputs/FirmLevelRisk/firmquarter_2022q1.csv
        |-- PRiskQLag2Builder --> inputs/FirmLevelRisk/firmquarter_2022q1.csv
        |-- SizeBuilder --> CompustatEngine --> inputs/comp_na_daily_all/comp_na_daily_all.parquet
        |-- BookLevBuilder --> CompustatEngine (cached)
        |-- ROABuilder --> CompustatEngine (cached)
        |-- TobinsQBuilder --> CompustatEngine (cached)
        |-- CashHoldingsBuilder --> CompustatEngine (cached)
        |-- DividendPayerBuilder --> CompustatEngine (cached)
        |-- FirmMaturityBuilder --> CompustatEngine (cached)
        |-- EarningsVolatilityBuilder --> CompustatEngine (cached)
        --> outputs/variables/h11_prisk_uncertainty_lag/{ts}/h11_prisk_uncertainty_lag_panel.parquet
  --> run_h11_prisk_uncertainty_lag.py (Stage 4)
        |-- pd.read_parquet(panel, columns=[19 cols])
        |-- assign_industry_sample() for sample classification
        |-- PanelOLS.from_formula() with entity+time FE, clustered SEs
        --> outputs/econometric/h11_prisk_uncertainty_lag/{ts}/
```

### Shared modules consumed

| Module | File | Purpose |
|--------|------|---------|
| `_compustat_engine.py` | `src/f1d/shared/variables/_compustat_engine.py` | Singleton; loads Compustat, computes all accounting controls, caches |
| `_linguistic_engine.py` | `src/f1d/shared/variables/_linguistic_engine.py` | Singleton; loads Stage 2 linguistic vars, applies per-year winsorization, caches |
| `panel_utils.py` | `src/f1d/shared/variables/panel_utils.py` | `assign_industry_sample()` |
| `winsorization.py` | `src/f1d/shared/variables/winsorization.py` | `winsorize_by_year()` used by PRisk builders |
| `base.py` | `src/f1d/shared/variables/base.py` | `VariableBuilder`, `VariableResult`, `VariableStats` |
| `path_utils.py` | `src/f1d/shared/path_utils.py` | `get_latest_output_dir()` |
| `latex_tables_accounting.py` | `src/f1d/shared/latex_tables_accounting.py` | `make_summary_stats_table()` |
| `outputs/` | `src/f1d/shared/outputs/` | `generate_manifest()`, `generate_attrition_table()` |

---

## D. Data Provenance

### D1. Master manifest

| Field | Value |
|-------|-------|
| Source file | `outputs/1.4_AssembleManifest/{latest}/master_sample_manifest.parquet` |
| Columns loaded | `file_name`, `ceo_id`, `ceo_name`, `gvkey`, `ff12_code`, `ff12_name`, `start_date` |
| Year filter | Manifest rows filtered to `start_date.year in [2002..2018]` |
| Upstream | Stages 1.0--1.4 (earnings call transcript linking + CEO matching + filtering) |

### D2. Linguistic variables

| Field | Value |
|-------|-------|
| Source files | `outputs/2_Textual_Analysis/2.2_Variables/{latest}/linguistic_variables_{year}.parquet` (year = 2002..2018) |
| Columns used | `Manager_QA_Uncertainty_pct`, `CEO_QA_Uncertainty_pct`, `Manager_Pres_Uncertainty_pct`, `CEO_Pres_Uncertainty_pct`, `Analyst_QA_Uncertainty_pct`, `Entire_All_Negative_pct` |
| Winsorization | Per-year 0%/99% (upper-only) applied at LinguisticEngine level |
| Dictionary | Loughran-McDonald Uncertainty word list |

### D3. Hassan et al. (2019) Political Risk

| Field | Value |
|-------|-------|
| Source file | `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (TAB-separated) |
| Citation | Hassan, Hollander, van Lent, Tahoun (2019), "Firm-Level Political Risk: Measurement and Effects", *QJE* |
| Total rows | 354,518 firm-quarter observations |
| Year coverage | 2002--2022 (only 2001--2018 used for lag matching) |
| Unique gvkeys | 13,149 |
| Key column | `PRisk` (continuous; range 0--11,057) |
| Duplicate check | **Zero** duplicate (gvkey, date) rows in source data |
| Processing | (1) Parse "YYYYqQ" date, (2) zero-pad gvkey to 6 digits, (3) filter to sample years + year-1 (lag) or year-2 (lag2), (4) per-year 1%/99% winsorize, (5) merge on (gvkey, lagged_cal_q) |

### D4. Compustat quarterly

| Field | Value |
|-------|-------|
| Source file | `inputs/comp_na_daily_all/comp_na_daily_all.parquet` |
| Dedup | (gvkey, datadate) deduplicated, keep last (CRITICAL-2 fix) |
| Match method | `merge_asof` backward on (gvkey, start_date <= datadate) |
| Variables extracted | Size, BookLev, ROA, TobinsQ, CashHoldings, DividendPayer, firm_maturity, earnings_volatility |
| Winsorization | Per-fyearq 1%/99% for continuous vars (DividendPayer excluded as binary) |

---

## E. Merge & Sample Construction Audit

### E1. Panel builder merge logic

The panel builder performs left-merge for each builder's output onto the manifest backbone, keyed on `file_name`. Zero row-delta is enforced (lines 142--147 of panel builder) -- any merge that changes the row count raises a `ValueError`.

### E2. PRiskQ_lag merge

1. Builder loads manifest (file_name, gvkey, start_date), filters to sample years
2. Computes `cal_q` from `start_date` (e.g., "2010q2")
3. Computes `cal_q_lag = _get_prev_quarter(cal_q)` (e.g., "2010q1")
4. Loads Hassan PRisk data, filters to years + (min_year - 1), deduplicates (gvkey, cal_q) keeping max PRisk, applies per-year winsorization
5. Left-merges manifest on `(gvkey, cal_q_lag) = PRisk.(gvkey, cal_q)`
6. Drops duplicate file_names after merge
7. **Match rate:** 105,152/112,968 = 93.1%

### E3. PRiskQ_lag2 merge

Same as E2 but `cal_q_lag2 = _get_prev2_quarter(cal_q)`, year filter includes min_year - 2.
**Match rate:** 103,595/112,968 = 91.7%

### E4. Panel dimensions (verified from latest panel parquet)

| Metric | Value |
|--------|-------|
| Total rows | 112,968 |
| Total columns | 26 |
| Unique gvkeys | 2,429 |
| Year range | 2002--2018 |
| Main sample rows | 88,205 |
| Finance sample rows | 20,482 |
| Utility sample rows | 4,281 |

### E5. Variable missingness (panel level)

| Variable | Non-null | Missing | % Missing |
|----------|----------|---------|-----------|
| Manager_QA_Uncertainty_pct | 108,215 | 4,753 | 4.2% |
| CEO_QA_Uncertainty_pct | 76,818 | 36,150 | **32.0%** |
| Manager_Pres_Uncertainty_pct | 110,205 | 2,763 | 2.4% |
| CEO_Pres_Uncertainty_pct | 76,928 | 36,040 | **31.9%** |
| PRiskQ_lag | 105,152 | 7,816 | 6.9% |
| PRiskQ_lag2 | 103,595 | 9,373 | 8.3% |
| Size | 112,692 | 276 | 0.2% |
| TobinsQ | 111,259 | 1,709 | 1.5% |
| ROA | 112,194 | 774 | 0.7% |
| CashHoldings | 112,678 | 290 | 0.3% |
| DividendPayer | 112,855 | 113 | 0.1% |
| firm_maturity | 112,211 | 757 | 0.7% |
| earnings_volatility | 112,449 | 519 | 0.5% |
| Analyst_QA_Uncertainty_pct | 103,858 | 9,110 | 8.1% |
| Entire_All_Negative_pct | 111,248 | 1,720 | 1.5% |
| BookLev | 112,692 | 276 | 0.2% |

**Note:** BookLev is built in the panel but never loaded by the runner (it is not in the runner's explicit column list at lines 446--468). This is dead weight but does not affect results.

### E6. Effective regression sample (Main, Manager_QA, PRiskQ_lag)

From verified regression output (`regression_results_Main_Manager_QA_Uncertainty_pct_lag1.txt`):
- N observations: 74,306
- N entities (firms): 1,801
- Time periods: 17

Attrition from 88,205 Main-sample rows to 74,306 regression rows (~15.8% attrition) due to: (1) complete-case deletion across DV + IV + 10 controls, (2) min-5-calls filter, (3) absorbed entities/time periods.

---

## F. Variable Dictionary

| Variable | Role | Definition | Source | Winsorization | Temporal alignment |
|----------|------|-----------|--------|---------------|-------------------|
| `Manager_QA_Uncertainty_pct` | DV | % LM uncertainty words in manager Q&A turns | Stage 2 linguistic | Per-year 0%/99% (upper-only) | Contemporaneous (call date) |
| `CEO_QA_Uncertainty_pct` | DV | % LM uncertainty words in CEO Q&A turns | Stage 2 linguistic | Per-year 0%/99% (upper-only) | Contemporaneous (call date) |
| `Manager_Pres_Uncertainty_pct` | DV | % LM uncertainty words in manager presentation turns | Stage 2 linguistic | Per-year 0%/99% (upper-only) | Contemporaneous (call date) |
| `CEO_Pres_Uncertainty_pct` | DV | % LM uncertainty words in CEO presentation turns | Stage 2 linguistic | Per-year 0%/99% (upper-only) | Contemporaneous (call date) |
| `PRiskQ_lag` | IV | Quarterly political risk, 1-quarter lag (Q-1) | Hassan et al. (2019) | Per-year 1%/99% | Calendar quarter t-1 |
| `PRiskQ_lag2` | IV | Quarterly political risk, 2-quarter lag (Q-2) | Hassan et al. (2019) | Per-year 1%/99% | Calendar quarter t-2 |
| `Analyst_QA_Uncertainty_pct` | Control | % LM uncertainty words in analyst Q&A turns | Stage 2 linguistic | Per-year 0%/99% (upper-only) | Contemporaneous |
| `Entire_All_Negative_pct` | Control | % LM negative words across entire call | Stage 2 linguistic | Per-year 0%/99% (upper-only) | Contemporaneous |
| `Size` | Control | ln(atq), atq > 0 only | Compustat | Per-fyearq 1%/99% | Backward merge_asof |
| `TobinsQ` | Control | (mktcap + debt_book) / atq | Compustat | Per-fyearq 1%/99% | Backward merge_asof |
| `ROA` | Control | iby_annual / avg_assets | Compustat | Per-fyearq 1%/99% | Backward merge_asof |
| `CashHoldings` | Control | cheq / atq | Compustat | Per-fyearq 1%/99% | Backward merge_asof |
| `DividendPayer` | Control | Binary: dvy_annual(Q4) > 0 | Compustat | Not winsorized (binary) | Backward merge_asof |
| `firm_maturity` | Control | RE / TA (req / atq) | Compustat | Per-fyearq 1%/99% | Backward merge_asof |
| `earnings_volatility` | Control | Rolling 5-yr std of annual ROA | Compustat | Per-fyearq 1%/99% | Backward merge_asof |
| `Manager_Pres_Uncertainty_pct` | Dynamic control | Added when DV is Manager_QA | Stage 2 linguistic | Per-year 0%/99% | Contemporaneous |
| `CEO_Pres_Uncertainty_pct` | Dynamic control | Added when DV is CEO_QA | Stage 2 linguistic | Per-year 0%/99% | Contemporaneous |

---

## G. Outliers / Missing / Scaling

### G1. Winsorization summary

| Variable group | Method | Bounds | Stage |
|---------------|--------|--------|-------|
| PRiskQ_lag, PRiskQ_lag2 | Per-year (year of PRisk quarter) | 1%/99% | PRiskQLagBuilder / PRiskQLag2Builder |
| Linguistic _pct variables | Per-year (year from parquet filename) | 0%/99% (upper-only) | LinguisticEngine |
| Compustat controls (Size, TobinsQ, ROA, CashHoldings, firm_maturity, earnings_volatility) | Per-fyearq (Compustat fiscal year) | 1%/99% | CompustatEngine `_compute_and_winsorize()` |
| DividendPayer | Not winsorized | Binary | CompustatEngine |
| BookLev | Per-fyearq 1%/99% | Built but unused | CompustatEngine |

### G2. Missing data treatment

- `inf` and `-inf` replaced with `NaN` in `prepare_regression_data()` (runner line 172) and in CompustatEngine (MINOR-9)
- Complete-case deletion via `dropna(subset=required)` in `prepare_regression_data()` (runner line 172)
- No imputation of any variable

### G3. Scaling / standardization

**None applied.** The LaTeX table notes claim "All continuous controls are standardized" (runner line 397) but no standardization code exists in the runner. This is a documentation error. See Issue Register I-05.

---

## H. Estimation Spec Register

### H1. Model formula (all 24 regressions)

```
DV ~ 1 + IV + Analyst_QA_Uncertainty_pct + Entire_All_Negative_pct + Size + TobinsQ
     + ROA + CashHoldings + DividendPayer + firm_maturity + earnings_volatility
     [+ Pres_control_if_QA_DV] + EntityEffects + TimeEffects
```

### H2. Regression grid

| IV | DV | Samples | Total |
|----|-----|---------|-------|
| PRiskQ_lag | Manager_QA_Uncertainty_pct | Main, Finance, Utility | 3 |
| PRiskQ_lag | CEO_QA_Uncertainty_pct | Main, Finance, Utility | 3 |
| PRiskQ_lag | Manager_Pres_Uncertainty_pct | Main, Finance, Utility | 3 |
| PRiskQ_lag | CEO_Pres_Uncertainty_pct | Main, Finance, Utility | 3 |
| PRiskQ_lag2 | (same 4 DVs) | (same 3 samples) | 12 |
| **Total** | | | **24** |

### H3. Estimator details

| Parameter | Value | Code reference |
|-----------|-------|----------------|
| Estimator | `PanelOLS.from_formula()` | runner line 203 |
| `drop_absorbed` | `True` | runner line 203 |
| `cov_type` | `"clustered"` | runner line 204 |
| `cluster_entity` | `True` | runner line 204 |
| Fixed effects | Entity (gvkey) + Time (year) | Formula string |
| Panel index | `df.set_index(["gvkey", "year"])` | runner line 200 |

### H4. One-tailed test implementation

```python
p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2
h_sig = not np.isnan(p_one) and p_one < 0.05 and beta_prisk > 0
```

Correct: divides two-sided p by 2 when sign matches predicted direction (positive), takes complement otherwise.

### H5. Verified result (Main, Manager_QA, PRiskQ_lag)

| Metric | Value |
|--------|-------|
| N obs | 74,306 |
| N firms | 1,801 |
| Time periods | 17 |
| Within-R2 | 0.0321 |
| beta(PRiskQ_lag) | 4.313e-05 |
| SE (clustered) | 8.187e-06 |
| t-stat | 5.2679 |
| p (two-tailed) | 0.0000 |
| F-statistic (robust) | 82.567 |

---

## I. Verification Log

| Check | Result | Method |
|-------|--------|--------|
| Panel row count | 112,968 | `pd.read_parquet(); len()` |
| Panel column count | 26 | `pd.read_parquet(); len(columns)` |
| Unique gvkeys | 2,429 | `panel['gvkey'].nunique()` |
| Year range | 2002--2018 | `panel['year'].min(), .max()` |
| Sample distribution | Main=88,205, Finance=20,482, Utility=4,281 | `panel['sample'].value_counts()` |
| PRiskQ_lag match rate | 93.1% (105,152/112,968) | `panel['PRiskQ_lag'].notna().sum()` |
| PRiskQ_lag2 match rate | 91.7% (103,595/112,968) | `panel['PRiskQ_lag2'].notna().sum()` |
| CEO_QA missing rate | 32.0% | `panel['CEO_QA_Uncertainty_pct'].isna().mean()` |
| PRisk source duplicates | 0 | Checked raw CSV for (gvkey, date) duplicates |
| Quarter lag function correctness | Verified: 2010q1->2009q4, 2010q2->2010q1, etc. | Manual test of `_get_prev_quarter()` |
| Quarter lag2 function correctness | Verified: 2010q1->2009q3, 2010q2->2009q4, etc. Code logic is correct. **Note:** docstring at `prisk_q_lag2.py` line 71 contains a bug -- says "2010q3 -> 2009q1" but code correctly returns "2010q1". Docstring-only error. | Manual test of `_get_prev2_quarter()` |
| Regression output file count | 24/24 | `ls` on latest econometric output dir |
| Regression N for Main/MgrQA/lag1 | 74,306 | Parsed from regression text file |
| Zero row-delta enforced in merges | Yes | Panel builder lines 142--147 |
| BookLev built but unused | Confirmed | Runner column list (lines 446--468) excludes BookLev |
| model_diagnostics.csv missing | Confirmed missing in latest run | `os.path.exists()` |

---

## J. Known Issues (Code-Level)

| ID | Severity | Description |
|----|----------|-------------|
| J-01 | Minor | BookLevBuilder is invoked by panel builder (line 112) but the runner never loads BookLev. Wasted computation, no effect on results. |
| J-02 | Info | PRisk dedup logic (`sort_values("PRisk", ascending=False).drop_duplicates(keep="first")`) keeps max PRisk per (gvkey, cal_q). In practice, zero duplicates exist in the source data, so this is defensive code. |
| J-03 | Info | `year` column is derived from `start_date` (calendar year of the call), not from Compustat fiscal year. PanelOLS time effects absorb calendar years, not fiscal years. |

---

## K. Referee Assessment

### K1. Identification Strategy

**Strength:** The lag design provides temporal ordering -- PRisk measured at Q-1 (or Q-2) unambiguously precedes the earnings call at Q. This mitigates the reverse-causality concern present in the contemporaneous H11-Base specification (where the Hassan et al. PRisk measure is derived from the same earnings call transcript that provides the DV).

**Weakness -- PRisk endogeneity even with lag:** The Hassan et al. (2019) PRisk measure is computed from earnings call transcripts. While the lagged version measures PRisk from the *prior quarter's* earnings call, both the prior-quarter and current-quarter calls are made by the same CEO at the same firm. Any persistent firm-level or CEO-level communication style (e.g., some CEOs always use more political language AND more uncertain language) creates a within-entity correlation between lagged PRisk and current DV that is NOT addressed by entity fixed effects alone. Entity FE remove time-invariant levels but cannot remove time-varying confounders that are autocorrelated within entity.

**Weakness -- No firm-level time-varying confounders:** The model lacks controls for firm-level political exposure drivers (lobbying expenditure, government contracts, regulatory filings) that would vary over time and plausibly confound the PRisk-uncertainty relationship. Missing time-varying confounders are a standard concern for within-estimator designs.

**Weakness -- Calendar quarter vs. fiscal quarter misalignment:** PRisk is matched on *calendar* quarters (derived from `start_date`), while most Compustat controls are matched via backward `merge_asof` on `datadate` (fiscal quarter end). For firms with non-December fiscal year ends (~30% of firms), the Compustat controls may reflect a different reporting period than the PRisk quarter, creating temporal misalignment in the conditioning set.

### K2. Inference Quality

**Clustering level:** Firm-level clustering (`cluster_entity=True`) is appropriate given the panel structure. However, the effective cluster count varies by DV (CEO DVs lose ~32% of observations). For Finance and Utility subsamples, the number of clusters may be insufficient for reliable clustered SE inference (rule of thumb: >= 50 clusters).

**Multiple testing:** 24 regressions are run (4 DVs x 3 samples x 2 IVs). No correction for multiple comparisons (Bonferroni, Holm, or FDR). At alpha=0.05 one-tailed, approximately 1.2 rejections expected by chance alone even under the null. The paper should report all 24 results and discuss which survive multiple-testing adjustment.

**One-tailed test:** The one-tailed test is correctly implemented (`p_two/2` when beta sign matches prediction). However, the *a priori* justification for a one-tailed test requires theoretical commitment: if there is any reason to believe lagged political risk could *reduce* uncertainty language (e.g., managers have time to prepare clearer responses), the two-tailed test is more appropriate.

### K3. Robustness Gaps

1. **No standardized coefficients:** All variables enter in raw units. Without standardization, the economic magnitude of beta(PRiskQ_lag) = 4.3e-05 is difficult to interpret. A 1-unit increase in PRisk (which ranges from 0 to 1,192 post-winsorization) increases Manager_QA_Uncertainty_pct by 0.004 percentage points. A one-standard-deviation increase (SD=147) would increase uncertainty by ~0.006 pp, which is approximately 0.8% of the mean (0.82 pp). This is economically small.
2. **No placebo test integration:** The lead specification (H11-Lead) serves as a placebo test, but results are not compared within this document. A referee would expect the lead coefficients to be insignificant if the lag relationship is truly causal.
3. **No lag length sensitivity:** Only lag-1 and lag-2 are tested. No discussion of why exactly 1 and 2 quarters, as opposed to 3 or 4.
4. **No Granger-causality framework:** The lag design is *suggestive* of temporal precedence but does not constitute a Granger-causality test (which would require controlling for lagged DV). Omitting lagged DV risks bias from autocorrelation in uncertainty language.
5. **No interaction with political exposure:** The effect of lagged political risk on language may differ by firm-level political exposure (lobbying, government dependence). No interaction terms are tested.

### K4. Variable Construction Concerns

1. **firm_maturity definition:** Coded as `req / atq` (retained earnings / total assets, i.e., RE/TA) in the CompustatEngine, not as "years since first Compustat appearance" as might be expected from the name. This ratio captures earnings reinvestment history, not chronological age. While economically meaningful, the variable name is misleading. Verified: `_compute_h3_payout_policy()` line 848: `df["firm_maturity"] = np.where((df["atq"].notna()) & (df["atq"] > 0), df["req"] / df["atq"], np.nan)`.
2. **Linguistic winsorization asymmetry:** PRisk variables are winsorized symmetrically (1%/99%) while linguistic _pct variables are winsorized upper-only (0%/99%). The 0% lower bound is natural for percentages (cannot be negative), but this asymmetry means the two variable types have different tail treatments.
3. **DividendPayer classification:** Uses annual `dvy` from Q4 filing, joined back to all quarters. A firm classified as dividend-payer in Q4 is retroactively classified for Q1--Q3, even though the dividend decision may have occurred mid-year. This is conventional but worth noting.
4. **PRisk dedup keeps maximum:** In `_load_prisk_quarterly()`, duplicates (if any existed) would be resolved by keeping the row with the highest PRisk value. This creates an upward bias for any firm-quarter with multiple observations. In practice, zero duplicates exist, making this a non-issue.

### K5. Sample Selection & Survivorship

1. **CEO DV missingness:** CEO_QA and CEO_Pres DVs are missing for ~32% of calls. This reflects calls where the CEO did not speak (or was not identified). The regression sample for CEO DVs is substantially smaller and may be non-randomly selected (e.g., biased toward firms where the CEO is a prominent public speaker).
2. **Min-calls filter:** The 5-call minimum within each (sample, DV, IV) cell is applied *after* complete-case deletion. This means a firm could have 10 calls total but only 4 with non-missing CEO_QA_Uncertainty_pct, causing exclusion from CEO specifications but inclusion in Manager specifications. This differential attrition is not documented.
3. **Finance and Utility subsamples:** These are included for completeness but the Finance sample (20,482 calls) and Utility sample (4,281 calls) may have insufficient within-entity variation for reliable fixed-effects estimation, especially after the min-calls filter.

### K6. LaTeX Table Accuracy

The LaTeX table notes (runner lines 389--398) contain the claim: "All continuous controls are standardized." **This is false.** No standardization code exists anywhere in the runner or panel builder. Variables enter in raw units. This is a documentation error that must be corrected before submission.

The LaTeX table notes also state: "Variables are winsorized at 1%/99% by year." This is partially correct: PRisk and Compustat controls are winsorized at 1%/99%, but linguistic variables use 0%/99% (upper-only) and are winsorized per-year at the LinguisticEngine level, not in the panel builder.

### K7. Academic Integrity & Replicability

1. **Deterministic:** `config/project.yaml` sets `random_seed=42`, `thread_count=1`, `sort_inputs=true`. PanelOLS estimation is deterministic. The pipeline should produce identical results across runs.
2. **Incomplete latest run:** The latest run (2026-03-18_164810) is missing 3 key output files (model_diagnostics.csv, LaTeX table, attrition table). All 24 regression text files exist. The run appears to have failed during post-regression aggregation. Earlier runs (2026-03-09) contain all expected outputs.
3. **No version pinning of key packages:** `linearmodels` and `pandas` version are not pinned in the runner. PanelOLS behavior (especially `drop_absorbed`) can change across versions.

---

## L. Issue Register

| ID | Severity | Category | Description | Remediation |
|----|----------|----------|-------------|-------------|
| I-01 | **MEDIUM** | Reproducibility | Latest run (2026-03-18) missing model_diagnostics.csv, LaTeX table, and attrition table. Run appears to have crashed during post-regression aggregation. Core 24/24 regression files exist; missing files are post-hoc aggregation artifacts. | Re-run Stage 4 and verify all output files are produced. |
| I-02 | **HIGH** | Documentation | LaTeX table notes claim "All continuous controls are standardized" -- this is false. No standardization is applied. | Remove the claim from the LaTeX template (runner line 397) or implement standardization. |
| I-03 | **MEDIUM** | Identification | No control for lagged DV. Autocorrelation in uncertainty language means the lag coefficient may be capturing persistence in DV rather than the effect of lagged PRisk. | Add lagged DV as control or implement Granger-causality test. |
| I-04 | **MEDIUM** | Robustness | No multiple-testing correction across 24 regressions. | Report Holm-corrected p-values or FDR-adjusted q-values. |
| I-05 | **MEDIUM** | Robustness | No standardized coefficients reported. Economic magnitude of beta(PRiskQ_lag) = 4.3e-05 is difficult to interpret without standardization. | Report beta in SD units. |
| I-06 | **LOW** | Efficiency | BookLevBuilder runs in panel builder but the runner never loads BookLev. | Remove BookLevBuilder from panel builder imports and builders dict. |
| I-07 | **LOW** | Documentation | `firm_maturity` is RE/TA (retained earnings / total assets, i.e., req/atq), not chronological age. Variable name is misleading. | Rename to `re_ratio` or document clearly. |
| I-08 | **LOW** | Winsorization | PRisk (1%/99% symmetric) and linguistic vars (0%/99% upper-only) have asymmetric winsorization. Intentional but undocumented. | Document in paper methodology section. |
| I-09 | **INFO** | Panel structure | Panel index is (gvkey, year) but unit of observation is the call. Multiple calls per (gvkey, year) exist. PanelOLS handles this correctly but entity/time FE interpretation differs from true firm-year panels. | Document in paper. |
| I-10 | **MEDIUM** | Presentation | LaTeX table stars use one-tailed p-values (`beta_prisk_p_one`) without disclosure (runner lines 287--297, applied at lines 327--330). Standard academic convention assumes two-tailed p-values unless explicitly stated. A coefficient with two-tailed p=0.015 would receive `**` (one-tailed p=0.0075 < 0.01), which readers would interpret as p<0.01 two-tailed. This overstates significance. | Either change stars to use two-tailed p-values, or add explicit note to table: "Significance levels based on one-tailed tests." |
| I-11 | **LOW** | Metadata | `n_firms` and `n_clusters` in metadata dict (runner lines 244--245) are computed from the input DataFrame (`df_sample`/`df_filtered`), but PanelOLS with `drop_absorbed=True` may drop additional singleton entities. The actual cluster count used in estimation may be lower than reported. | Compute `n_clusters` from the model object rather than the input DataFrame. |

---

## M. Priority Fixes

### Must-fix before submission

1. **I-02:** Remove false "standardized" claim from LaTeX table notes (runner line 397) or implement actual standardization.
2. **I-10:** Disclose that LaTeX table stars are based on one-tailed p-values, or switch to two-tailed p-values for star assignment.

### Should-fix for robustness

3. **I-01:** Re-run Stage 4 to produce all expected output files (model_diagnostics.csv, LaTeX table, attrition table).
4. **I-03:** Add lagged DV as control in a robustness specification to address autocorrelation concern.
5. **I-05:** Report standardized coefficients for economic interpretation.
6. **I-04:** Report multiple-testing adjustments (at minimum, note the number of tests in the paper).

### Nice-to-fix

6. **I-06:** Remove unused BookLevBuilder from panel builder.
7. **I-07:** Rename or document `firm_maturity` more clearly.

---

## N. Final Readiness Statement

**Readiness: CONDITIONAL -- requires 2 must-fixes before submission.**

The H11-Lag suite is mechanically correct in its core estimation logic: temporal lag construction is verified, one-tailed tests are correctly implemented, and entity+time fixed effects with firm-clustered SEs follow standard practice. The lag design provides meaningful improvement over the contemporaneous H11-Base specification for causal interpretation.

However, two issues must be resolved before submission:
1. The LaTeX table notes falsely claim controls are standardized (I-02) -- this is a factual error in the submitted artifact.
2. The LaTeX table stars use one-tailed p-values without disclosure (I-10) -- readers would assume two-tailed convention, overstating significance.

Additionally, the latest run is incomplete (I-01, MEDIUM) -- the final aggregation output files should be regenerated.

The identification concern (I-03, omitted lagged DV) is the most substantive referee vulnerability. A robustness table with the lagged DV as an additional control would substantially strengthen the paper's causal claims. The multiple-testing concern (I-04) is standard for multi-specification papers and can be addressed with a brief discussion of correction methods.
