# H11-Lead Political Risk (Lead) -- Provenance Document

**Generated:** 2026-03-30 (manual trace)
**Auditor method:** Manual file reading, grep, line-level verification.
Every claim cites file path + line number. No documentation generators used.

---

## A. SUITE IDENTITY

```yaml
Suite ID:        H11-Lead
Title:           H11-Lead: Lead Political Risk and Language Uncertainty (Placebo)
Hypothesis:      Future political risk (1- and 2-quarter leads) should NOT predict
                 current earnings-call language uncertainty. This is a placebo/
                 falsification test for reverse causality -- if future PRisk predicts
                 current speech, it would suggest the H11 contemporaneous result is
                 driven by reverse causation rather than a causal effect.
Direction:       Two-tailed (beta = 0 under null; expected insignificance)
Model Family:    Linear panel regression with absorbed fixed effects
Estimator:       linearmodels.panel.PanelOLS
Unit of Obs:     Individual earnings call (file_name)
Panel Index:     (gvkey, year) -- calendar year derived from start_date
Columns:         8 (Main sample: 4 DVs x lead1 + 4 DVs x lead2)
                 24 total regressions run (3 samples x 4 DVs x 2 leads)
Reference:       Hassan, Hollander, van Lent & Tahoun (2019) -- quarterly PRisk data
Runner:          src/f1d/econometric/run_h11_prisk_uncertainty_lead.py
Panel Builder:   src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py
```

**Critical distinction from H11 and H11-Lag:** H11 and H11-Lag use ONE-TAILED tests
(beta > 0), testing whether contemporaneous/lagged political risk increases speech
uncertainty. H11-Lead uses a TWO-TAILED test (beta = 0), because as a placebo test
the *expected* result is insignificance -- future political risk should not predict
current speech. The two-tailed p-value `p_two` is used directly (runner line 223:
`p_test = p_two`) with no halving applied.

*Source: run_h11_prisk_uncertainty_lead.py, lines 32--37 (docstring), line 223 (p_test = p_two).*

---

## B. MODEL SPECIFICATION

### B1. Regression Equation

For each (DV, IV) pair:

$$
\text{DV}_{i,t} = \beta_1 \cdot \text{IV}_{i,t} + \gamma \mathbf{X}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

where:
- $\alpha_i$ = firm fixed effects (EntityEffects, absorbed via `gvkey` index)
- $\delta_t$ = calendar year fixed effects (TimeEffects, absorbed via `year` index)
- $\text{IV}$ is either `PRiskQ_lead` (t+1) or `PRiskQ_lead2` (t+2)
- $\mathbf{X}_{i,t}$ = controls (including dynamic Presentation control for QA DVs)

Exact formula string (runner line 187--191):
```
{dv_var} ~ 1 + {iv_var} + {controls} + EntityEffects + TimeEffects
```

*Source: run_h11_prisk_uncertainty_lead.py, lines 187--191.*

### B2. Dependent Variable(s)

| Variable Name (code) | Description | Formula | Source Engine | Timing |
|---|---|---|---|---|
| `Manager_QA_Uncertainty_pct` | All managers' Q&A uncertainty word percentage | (LM uncertainty word count by managers in Q&A / total manager Q&A word count) * 100 | LinguisticEngine | Contemporaneous (call-level) |
| `CEO_QA_Uncertainty_pct` | CEO Q&A uncertainty word percentage | (LM uncertainty word count by CEO in Q&A / total CEO Q&A word count) * 100 | LinguisticEngine | Contemporaneous (call-level) |
| `Manager_Pres_Uncertainty_pct` | All managers' presentation uncertainty word percentage | (LM uncertainty word count by managers in presentation / total manager presentation word count) * 100 | LinguisticEngine | Contemporaneous (call-level) |
| `CEO_Pres_Uncertainty_pct` | CEO presentation uncertainty word percentage | (LM uncertainty word count by CEO in presentation / total CEO presentation word count) * 100 | LinguisticEngine | Contemporaneous (call-level) |

*Source: run_h11_prisk_uncertainty_lead.py CONFIG lines 93--98; builder files: manager_qa_uncertainty.py, ceo_qa_uncertainty.py, manager_pres_uncertainty.py, ceo_pres_uncertainty.py.*

### B3. Independent Variable(s)

| Variable Name (code) | Description | Formula | Source Engine | Timing |
|---|---|---|---|---|
| `PRiskQ_lead` | 1-quarter lead political risk | Hassan et al. (2019) PRisk from calendar quarter Q+1, matched to call in quarter Q via (gvkey, cal_q_lead) | PRiskQLeadBuilder (inputs/FirmLevelRisk/firmquarter_2022q1.csv) | Lead t+1 (next quarter) |
| `PRiskQ_lead2` | 2-quarter lead political risk | Hassan et al. (2019) PRisk from calendar quarter Q+2, matched to call in quarter Q via (gvkey, cal_q_lead2) | PRiskQLead2Builder (inputs/FirmLevelRisk/firmquarter_2022q1.csv) | Lead t+2 (two quarters ahead) |

Lead construction logic:
- PRiskQ_lead: `_get_next_quarter("2010q2")` returns `"2010q3"`; `"2010q4"` returns `"2011q1"` (prisk_q_lead.py line 69--82).
- PRiskQ_lead2: `_get_next2_quarter("2010q2")` returns `"2010q4"`; `"2010q3"` returns `"2011q1"` (prisk_q_lead2.py line 69--85).

Both are merged via `manifest.merge(prisk_df, left_on=["gvkey", "cal_q_lead*"], right_on=["gvkey", "cal_q"], how="left")`.

*Source: prisk_q_lead.py lines 69--82, 172--180; prisk_q_lead2.py lines 69--85, 176--183.*

### B4. Control Variables

**Base Controls** (applied to all specs):

| Variable Name (code) | Description | Formula | Source Engine |
|---|---|---|---|
| `Analyst_QA_Uncertainty_pct` | Analyst Q&A uncertainty word percentage | (LM uncertainty word count by analysts in Q&A / total analyst Q&A word count) * 100 | LinguisticEngine |
| `Entire_All_Negative_pct` | Negative sentiment (entire call) | (LM negative word count entire call / total word count entire call) * 100 | LinguisticEngine |
| `Size` | Firm size | ln(atq) where atq > 0 | CompustatEngine |
| `TobinsQ` | Tobin's Q | (cshoq * prccq + dlcq + dlttq) / atq | CompustatEngine |
| `ROA` | Return on assets | iby_annual (Q4) / avg_assets, where avg_assets = (atq_t + atq_{t-1}) / 2 | CompustatEngine |
| `CashHoldings` | Cash holdings ratio | cheq / atq | CompustatEngine |
| `DividendPayer` | Dividend payer indicator | 1 if dvy_annual > 0 (Q4 annual value), else 0 | CompustatEngine |
| `firm_maturity` | Firm maturity (retained earnings/assets) | req / atq | CompustatEngine |
| `earnings_volatility` | Earnings volatility | Rolling 5-year std dev of annual ROA (iby/atq), min 3 obs | CompustatEngine |

**Dynamic Presentation Control** (QA DVs only):

| DV | Additional Control Added |
|---|---|
| `Manager_QA_Uncertainty_pct` | `Manager_Pres_Uncertainty_pct` |
| `CEO_QA_Uncertainty_pct` | `CEO_Pres_Uncertainty_pct` |
| `Manager_Pres_Uncertainty_pct` | None |
| `CEO_Pres_Uncertainty_pct` | None |

The PRES_CONTROL_MAP (runner lines 115--120) adds the corresponding Presentation measure
as a control when the DV is a QA measure. This ensures QA regressions control for
presentation-section uncertainty content.

**No Lagged_DV:** This runner does not include a lagged dependent variable as a control.

*Source: run_h11_prisk_uncertainty_lead.py, lines 103--120, 164--166.*

### B5. Fixed Effects

| FE Type | Column Used | Description | How Applied |
|---|---|---|---|
| Entity | `gvkey` | Firm FE | Absorbed via PanelOLS `EntityEffects` (first level of MultiIndex) |
| Time | `year` | Calendar year FE | Absorbed via PanelOLS `TimeEffects` (second level of MultiIndex) |

The panel index is set via `df_sample.set_index(["gvkey", "year"])` (runner line 203).
Calendar year is derived from `start_date` (panel builder line 156).

There are no Industry FE specs -- all columns use firm FE.

*Source: run_h11_prisk_uncertainty_lead.py, line 203 (set_index), line 206 (from_formula with EntityEffects + TimeEffects).*

### B6. Standard Errors and Clustering

- **cov_type:** `"clustered"` (runner line 207)
- **cluster_entity:** `True` (runner line 207) -- clusters at the firm (`gvkey`) level
- **cluster_time:** not set (default `False`)
- **Small-sample corrections:** PanelOLS default

*Source: run_h11_prisk_uncertainty_lead.py, line 207.*

### B7. Hypothesis Test

- **Direction:** Two-tailed (beta = 0)
- **P-value computation:** `p_test = p_two` -- the two-tailed p-value from PanelOLS is used directly, with NO halving (runner line 223). This is the critical difference from H11/H11-Lag which halve the p-value for one-tailed tests.
- **Significance thresholds:** `*** p < 0.01, ** p < 0.05, * p < 0.10` (LaTeX table formatter, runner lines 287--293)
- **Expected result:** Insignificance. As a placebo test, significant lead coefficients would *undermine* the H11 causal interpretation.
- **Significance flagging:** `h_sig = not np.isnan(p_test) and p_test < 0.05` (runner line 225). Note: this uses p < 0.05 as the threshold for the significance flag in the diagnostics CSV, but the LaTeX table uses the three-tier star system above.

*Source: run_h11_prisk_uncertainty_lead.py, lines 222--225, 287--293.*

---

## C. MODEL SPECIFICATION REGISTER

The runner iterates over 2 IVs x 4 DVs x 3 samples = 24 regressions. The main LaTeX table (built by `_save_latex_table`) uses only the **Main sample** (8 columns). The `generate_all_tables.py` entry also uses 8 columns.

| Col | DV | IV | Entity FE | Time FE | Controls | Pres Control |
|-----|---|---|---|---|---|---|
| 1 | Manager_QA_Uncertainty_pct | PRiskQ_lead | Firm | Cal Year | Base | Manager_Pres_Uncertainty_pct |
| 2 | CEO_QA_Uncertainty_pct | PRiskQ_lead | Firm | Cal Year | Base | CEO_Pres_Uncertainty_pct |
| 3 | Manager_Pres_Uncertainty_pct | PRiskQ_lead | Firm | Cal Year | Base | -- |
| 4 | CEO_Pres_Uncertainty_pct | PRiskQ_lead | Firm | Cal Year | Base | -- |
| 5 | Manager_QA_Uncertainty_pct | PRiskQ_lead2 | Firm | Cal Year | Base | Manager_Pres_Uncertainty_pct |
| 6 | CEO_QA_Uncertainty_pct | PRiskQ_lead2 | Firm | Cal Year | Base | CEO_Pres_Uncertainty_pct |
| 7 | Manager_Pres_Uncertainty_pct | PRiskQ_lead2 | Firm | Cal Year | Base | -- |
| 8 | CEO_Pres_Uncertainty_pct | PRiskQ_lead2 | Firm | Cal Year | Base | -- |

All 8 columns use identical FE (Firm + Calendar Year) and clustering (entity-level).

*Source: run_h11_prisk_uncertainty_lead.py, CONFIG lines 92--101; _save_latex_table lines 256--404.*

---

## D. SAMPLE CONSTRUCTION

### D1. Population

- Starting dataset: `master_sample_manifest.parquet`
- Year range: 2002--2018 (from project config)

### D2. Exclusion Criteria

Attrition cascade from actual `sample_attrition.csv` output (latest run 2026-03-27):

| Step | Filter | Rows After | Rows Lost |
|------|--------|------------|-----------|
| 1 | Master manifest (full) | 112,968 | -- |
| 2 | Main sample filter (FF12 excl 8, 11) | 88,205 | 24,763 |
| 3 | Complete-case + min-calls filter (>= 5) | 75,224 | 12,981 |

Note: The attrition reported is for the Main sample with PRiskQ_lead and DV = Manager_QA_Uncertainty_pct. Other DV/IV/sample combinations have slightly different N due to variable-specific missingness.

Filtering steps in code order:
1. Panel builder loads manifest, filters by year range (builder line 152).
2. `assign_industry_sample(ff12_code)` partitions into Main/Finance/Utility (builder line 155).
3. `prepare_regression_data()` replaces inf with NaN, drops rows with any NaN in required columns (runner line 175).
4. Firms with < 5 calls in the sample are excluded (runner lines 527--530).

*Source: run_h11_prisk_uncertainty_lead.py, lines 175, 527--530; sample_attrition.csv.*

### D3. Sample Counts per Specification

From `model_diagnostics.csv` (Main sample only):

| Col | DV | IV | N (obs) | N (firms) |
|-----|---|---|---------|-----------|
| 1 | Manager_QA_Uncertainty_pct | PRiskQ_lead | 75,224 | 1,805 |
| 2 | CEO_QA_Uncertainty_pct | PRiskQ_lead | 54,661 | 1,578 |
| 3 | Manager_Pres_Uncertainty_pct | PRiskQ_lead | 75,243 | 1,805 |
| 4 | CEO_Pres_Uncertainty_pct | PRiskQ_lead | 54,979 | 1,580 |
| 5 | Manager_QA_Uncertainty_pct | PRiskQ_lead2 | 74,942 | 1,802 |
| 6 | CEO_QA_Uncertainty_pct | PRiskQ_lead2 | 54,453 | 1,574 |
| 7 | Manager_Pres_Uncertainty_pct | PRiskQ_lead2 | 74,961 | 1,802 |
| 8 | CEO_Pres_Uncertainty_pct | PRiskQ_lead2 | 54,774 | 1,577 |

CEO DVs have fewer observations because CEO identification yields more missingness.
Lead2 has slightly fewer observations than lead1 because Q+2 matching requires data
further into the future (edge-of-sample loss).

*Source: model_diagnostics.csv (2026-03-27_095003 run).*

---

## E. VARIABLE DICTIONARY

| Variable (code) | Label | Type | Formula | Source | Winsorized | Timing |
|---|---|---|---|---|---|---|
| `Manager_QA_Uncertainty_pct` | Mgr QA Uncertainty | DV | (LM uncertainty words by managers in Q&A / total manager Q&A words) * 100 | LinguisticEngine: Stage 2 parquet | 0%/99% upper-only per year | Contemporaneous |
| `CEO_QA_Uncertainty_pct` | CEO QA Uncertainty | DV | (LM uncertainty words by CEO in Q&A / total CEO Q&A words) * 100 | LinguisticEngine: Stage 2 parquet | 0%/99% upper-only per year | Contemporaneous |
| `Manager_Pres_Uncertainty_pct` | Mgr Pres Uncertainty | DV | (LM uncertainty words by managers in pres / total manager pres words) * 100 | LinguisticEngine: Stage 2 parquet | 0%/99% upper-only per year | Contemporaneous |
| `CEO_Pres_Uncertainty_pct` | CEO Pres Uncertainty | DV | (LM uncertainty words by CEO in pres / total CEO pres words) * 100 | LinguisticEngine: Stage 2 parquet | 0%/99% upper-only per year | Contemporaneous |
| `PRiskQ_lead` | Political Risk (t+1) | IV | Hassan et al. (2019) quarterly PRisk for (gvkey, cal_quarter+1) | firmquarter_2022q1.csv | 1%/99% per year | Lead (Q+1) |
| `PRiskQ_lead2` | Political Risk (t+2) | IV | Hassan et al. (2019) quarterly PRisk for (gvkey, cal_quarter+2) | firmquarter_2022q1.csv | 1%/99% per year | Lead (Q+2) |
| `Analyst_QA_Uncertainty_pct` | Analyst QA Uncertainty | Control | (LM uncertainty words by analysts in Q&A / total analyst Q&A words) * 100 | LinguisticEngine: Stage 2 parquet | 0%/99% upper-only per year | Contemporaneous |
| `Entire_All_Negative_pct` | Negative Sentiment | Control | (LM negative words entire call / total words entire call) * 100 | LinguisticEngine: Stage 2 parquet | 0%/99% upper-only per year | Contemporaneous |
| `Size` | Firm Size (log AT) | Control | ln(atq) where atq > 0 | CompustatEngine: atq | 1%/99% per fiscal year (fyearq) | Contemporaneous (merge_asof backward) |
| `TobinsQ` | Tobin's Q | Control | (cshoq * prccq + dlcq + dlttq) / atq | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq | 1%/99% per fiscal year (fyearq) | Contemporaneous |
| `ROA` | Return on Assets | Control | iby_annual (Q4) / ((atq_t + atq_{t-1}) / 2) | CompustatEngine: iby, atq | 1%/99% per fiscal year (fyearq) | Contemporaneous |
| `CashHoldings` | Cash Holdings | Control | cheq / atq | CompustatEngine: cheq, atq | 1%/99% per fiscal year (fyearq) | Contemporaneous |
| `DividendPayer` | Dividend Payer | Control | 1 if dvy_annual (Q4) > 0, else 0 | CompustatEngine: dvy | No (binary) | Contemporaneous |
| `firm_maturity` | Firm Maturity | Control | req / atq | CompustatEngine: req, atq | 1%/99% per fiscal year (fyearq) | Contemporaneous |
| `earnings_volatility` | Earnings Volatility | Control | Rolling 5-fiscal-year std dev of (iby/atq), min 3 observations | CompustatEngine: iby, atq | 1%/99% per fiscal year (fyearq) | Contemporaneous |
| `gvkey` | Firm identifier | FE (entity) | 6-digit zero-padded Compustat identifier | Manifest | N/A | N/A |
| `year` | Calendar year | FE (time) | Derived from start_date via `.dt.year` | Manifest: start_date | N/A | N/A |

*Sources: _compustat_engine.py lines 938, 962, 981, 988, 1005, 802--803, 806--821; _linguistic_engine.py lines 255--257; prisk_q_lead.py lines 170, 182--183; prisk_q_lead2.py lines 173, 185--186.*

---

## F. DATA PIPELINE

### F1. Dependency Chain

1. **Raw inputs:**
   - `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (Hassan quarterly PRisk, TAB-separated)
   - `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet` (master manifest)
   - `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet` (Stage 2 linguistic variables)
   - Compustat quarterly fundamentals (via CompustatEngine)

2. **Engine loading:**
   - LinguisticEngine: loads Stage 2 year-partitioned parquets, applies 0%/99% upper-only per-year winsorization
   - CompustatEngine: loads Compustat quarterly, computes derived variables, applies 1%/99% per-year winsorization
   - PRiskQLeadBuilder and PRiskQLead2Builder: load Hassan CSV, apply 1%/99% per-year winsorization

3. **Panel builder** (`build_h11_prisk_uncertainty_lead_panel.py`):
   - Loads manifest via ManifestFieldsBuilder
   - Builds each variable via its builder
   - Merges all on `file_name` (left join, zero row-delta enforced)
   - Assigns industry sample via `assign_industry_sample(ff12_code)`
   - Derives `year` from `start_date`
   - Outputs parquet panel

4. **Runner loading:** Reads panel parquet with explicit column selection (runner lines 448--473)

5. **Sample filtering:** Per (DV, IV, sample) combination:
   - Industry sample filter (Main/Finance/Utility)
   - inf -> NaN, dropna on required columns
   - min_calls >= 5 filter

6. **Regression estimation:** PanelOLS with firm-clustered SEs, 24 models (3 samples x 4 DVs x 2 IVs)

7. **Table generation:** `generate_all_tables.py` uses "type": "moderation" with 8 col_files (Main sample only)

### F2. Data Engines Used

| Engine | Source Data | Variables Provided to This Suite |
|--------|------------|--------------------------------|
| LinguisticEngine | Stage 2 year-partitioned parquet files | Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct |
| CompustatEngine | Compustat quarterly fundamentals | Size, TobinsQ, ROA, CashHoldings, DividendPayer, firm_maturity, earnings_volatility |
| PRiskQLeadBuilder (standalone) | inputs/FirmLevelRisk/firmquarter_2022q1.csv | PRiskQ_lead |
| PRiskQLead2Builder (standalone) | inputs/FirmLevelRisk/firmquarter_2022q1.csv | PRiskQ_lead2 |

### F3. Merge Operations

All merges occur in `build_h11_prisk_uncertainty_lead_panel.py`:

| Left | Right | Keys | Type | Notes |
|------|-------|------|------|-------|
| manifest (ManifestFieldsBuilder output) | ManagerQAUncertaintyBuilder output | `file_name` | Left | Zero row-delta enforced (builder line 152) |
| panel | CEOQAUncertaintyBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | ManagerPresUncertaintyBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | CEOPresUncertaintyBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | PRiskQLeadBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | PRiskQLead2Builder output | `file_name` | Left | Zero row-delta enforced |
| panel | AnalystQAUncertaintyBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | NegativeSentimentBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | SizeBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | BookLevBuilder output | `file_name` | Left | Zero row-delta enforced; BookLev built but NOT used in regressions |
| panel | ROABuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | TobinsQBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | CashHoldingsBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | DividendPayerBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | FirmMaturityBuilder output | `file_name` | Left | Zero row-delta enforced |
| panel | EarningsVolatilityBuilder output | `file_name` | Left | Zero row-delta enforced |

Within the PRiskQLeadBuilder:

| Left | Right | Keys | Type | Notes |
|------|-------|------|------|-------|
| manifest (with cal_q_lead) | prisk_df | left: (gvkey, cal_q_lead), right: (gvkey, cal_q) | Left | Matches Q+1 PRisk to call |

Within the PRiskQLead2Builder:

| Left | Right | Keys | Type | Notes |
|------|-------|------|------|-------|
| manifest (with cal_q_lead2) | prisk_df | left: (gvkey, cal_q_lead2), right: (gvkey, cal_q) | Left | Matches Q+2 PRisk to call |

*Source: build_h11_prisk_uncertainty_lead_panel.py, lines 136--153; prisk_q_lead.py lines 172--180; prisk_q_lead2.py lines 176--183.*

---

## G. OUTPUTS

### G1. Stage 3 Outputs (Panel Builder)

| File | Description |
|------|-------------|
| `h11_prisk_uncertainty_lead_panel.parquet` | Call-level panel with all variables |
| `summary_stats.csv` | Variable-level build statistics |
| `report_step3_h11_lead.md` | Build report |
| `run_manifest.json` | Reproducibility manifest |

*Source: build_h11_prisk_uncertainty_lead_panel.py, lines 190--213, 219--242.*

### G2. Stage 4 Outputs (Runner)

| File | Description |
|------|-------------|
| `h11_prisk_uncertainty_lead_table.tex` | Built-in LaTeX table (4 columns, Main sample, both leads) |
| `model_diagnostics.csv` | Per-model regression metadata (all 24 models) |
| `summary_stats.csv` | Main sample summary statistics |
| `summary_stats.tex` | LaTeX version of summary statistics |
| `sample_attrition.csv` | Sample attrition cascade |
| `sample_attrition.tex` | LaTeX version of attrition |
| `regression_results_{sample}_{dv}_{lead}.txt` | Individual model outputs (24 files) |
| `run_manifest.json` | Reproducibility manifest |

Regression result files follow the pattern:
`regression_results_{Main|Finance|Utility}_{DV}_{lead1|lead2}.txt`

Verified from latest output directory (2026-03-27_095003): 24 individual regression .txt files, plus diagnostics, summary stats, attrition, table, and manifest.

*Source: run_h11_prisk_uncertainty_lead.py, lines 552--554, 556--557, 570--571, 574--584.*

### G3. Summary Statistics

Variables included (runner lines 127--146):

| Variable | Label |
|---|---|
| Manager_QA_Uncertainty_pct | Mgr QA Uncertainty |
| CEO_QA_Uncertainty_pct | CEO QA Uncertainty |
| Manager_Pres_Uncertainty_pct | Mgr Pres Uncertainty |
| CEO_Pres_Uncertainty_pct | CEO Pres Uncertainty |
| PRiskQ_lead | Political Risk$_{t+1}$ |
| PRiskQ_lead2 | Political Risk$_{t+2}$ |
| Analyst_QA_Uncertainty_pct | Analyst QA Uncertainty |
| Entire_All_Negative_pct | Negative Sentiment |
| Size | Firm Size (log AT) |
| TobinsQ | Tobin's Q |
| ROA | ROA |
| CashHoldings | Cash Holdings |
| DividendPayer | Dividend Payer |
| firm_maturity | Firm Maturity |
| earnings_volatility | Earnings Volatility |

Metrics computed: N, Mean, SD, Min, P25, Median, P75, Max (via `make_summary_stats_table`). Stratified by sample (Main, Finance, Utility).

---

## H. OUTLIER AND MISSING DATA TREATMENT

### H1. Winsorization

**Compustat variables** (Size, TobinsQ, ROA, CashHoldings, firm_maturity, earnings_volatility):
- Level: 1%/99% per fiscal year (fyearq)
- Applied at CompustatEngine level before merge to manifest
- Skip list: DividendPayer (binary), CashFlow, SalesGrowth (_compustat_engine.py lines 1121--1128)

**Linguistic variables** (all _pct columns including DVs, Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct):
- Level: 0%/99% upper-only per year (lower bound at 0th percentile = no lower clipping)
- Applied at LinguisticEngine level (_linguistic_engine.py lines 255--257)

**PRiskQ_lead and PRiskQ_lead2:**
- Level: 1%/99% per year
- Applied within each builder via `winsorize_by_year(prisk_df, ["PRisk"], year_col="year")`
- prisk_q_lead.py line 170; prisk_q_lead2.py line 173

### H2. Missing Data Policy

- Complete-case deletion: `panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required)` (runner line 175)
- Required columns checked per (DV, IV) combination
- Rows with any NaN in DV, IV, or controls are dropped

### H3. Transformations

- `Size` = ln(atq) -- log transform (CompustatEngine line 938)
- No centering or z-scoring applied to any variables
- No standardization applied despite LaTeX table note stating "All continuous controls are standardized" -- this note is inaccurate per the code

---

## I. GENERATE_ALL_TABLES.PY ENTRY

```python
{
    "id": "H11-Lead",
    "type": "moderation",
    "dir": "h11_prisk_uncertainty_lead/2026-03-27_095003",
    "caption": "H11-Lead: Lead Political Risk and Language Uncertainty (Placebo)",
    "label": "tab:h11_lead",
    "cols": 8,
    "col_files": {
        1: "regression_results_Main_Manager_QA_Uncertainty_pct_lead1.txt",
        2: "regression_results_Main_CEO_QA_Uncertainty_pct_lead1.txt",
        3: "regression_results_Main_Manager_Pres_Uncertainty_pct_lead1.txt",
        4: "regression_results_Main_CEO_Pres_Uncertainty_pct_lead1.txt",
        5: "regression_results_Main_Manager_QA_Uncertainty_pct_lead2.txt",
        6: "regression_results_Main_CEO_QA_Uncertainty_pct_lead2.txt",
        7: "regression_results_Main_Manager_Pres_Uncertainty_pct_lead2.txt",
        8: "regression_results_Main_CEO_Pres_Uncertainty_pct_lead2.txt",
    },
    "dvs": [
        (r"PRiskQ\_lead", 4),
        (r"PRiskQ\_lead2", 4),
    ],
    "col_dv_labels": [
        "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
        "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
    ],
    "key_vars": ["PRiskQ_lead", "PRiskQ_lead2"],
    "key_labels": [r"PRiskQ\_lead", r"PRiskQ\_lead2"],
    "key_tails": ["two", "two"],
}
```

**Verification:**

| Check | Expected | Actual | Match |
|---|---|---|---|
| `key_tails` = "two" | Two-tailed (placebo test) | Runner line 223: `p_test = p_two` (no halving) | YES |
| `cols` = 8 | 4 DVs x 2 leads (Main sample) | 8 col_files entries, all Main sample | YES |
| `key_vars` | PRiskQ_lead, PRiskQ_lead2 | CONFIG["iv_vars"] = same | YES |
| `col_dv_labels` | 4 DVs repeated for each lead | Mgr QA, CEO QA, Mgr Pres, CEO Pres x 2 | YES |

*Source: generate_all_tables.py, lines 248--276.*

---

## J. REPRODUCTION COMMANDS

```bash
# Stage 3: Build panel
python -m f1d.variables.build_h11_prisk_uncertainty_lead_panel

# Stage 4: Run regressions
python -m f1d.econometric.run_h11_prisk_uncertainty_lead

# Generate tables (if applicable)
python outputs/generate_all_tables.py
```

---

## K. MODEL-FAMILY ADDENDUM

### K1. PanelOLS Specifics

- **Entity effects:** Absorbed via `EntityEffects` in PanelOLS formula. The entity dimension is `gvkey` (first level of the `["gvkey", "year"]` MultiIndex set at runner line 203).
- **Time effects:** Absorbed via `TimeEffects` in PanelOLS formula. The time dimension is `year` (calendar year, second level of MultiIndex).
- **other_effects:** Not used. All columns use firm FE (no Industry FE specs in this suite).
- **drop_absorbed:** `True` (runner line 206: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`)
- **Singleton handling:** Singletons (firm-year cells with only one observation after FE absorption) are automatically handled by PanelOLS with `drop_absorbed=True`.
- **R-squared:** `model.rsquared` (within-R2) reported. Adj R-squared computed manually: `1 - (1 - r2) * (nobs - 1) / df_resid` (runner lines 214, 244).

*Source: run_h11_prisk_uncertainty_lead.py, lines 203, 206--207, 214, 244.*

### K2. Cox Proportional Hazards Specifics
N/A

### K3. Logit/Probit/LPM Specifics
N/A

### K4. IV/2SLS Specifics
N/A

### K5. OLS (non-panel) Specifics
N/A

### K6. Other Model Family
N/A

---

## L. KNOWN ISSUES AND NOTES

1. **BookLevBuilder is imported and built in the panel builder (line 116) but NOT used in any regression.** The variable `BookLev` does not appear in `BASE_CONTROLS` or `PRES_CONTROL_MAP`. This is dead weight in the panel but does not affect results.

2. **No Lagged_DV control.** Unlike most other suites in this thesis, H11-Lead does not include a lagged dependent variable as a control. This is consistent with the H11 family's design (H11 and H11-Lag also lack Lagged_DV).

3. **LaTeX table note inaccuracy.** The built-in LaTeX table (runner line 399) states "All continuous controls are standardized" but the code does NOT standardize any variables. This note is incorrect per the code.

4. **Duplicate key in meta dict.** Runner line 249 assigns `"beta_prisk_p_two": float(p_test)` which overwrites the identical key set on line 248 (`"beta_prisk_p_two": float(p_two)`). Since `p_test = p_two` for this two-tailed suite, the overwrite has no effect, but it indicates a copy-paste artifact.

5. **N varies across columns.** The CEO DVs have materially fewer observations (~54K vs ~75K for Manager DVs), and lead2 specs have slightly fewer than lead1 due to edge-of-sample loss.

6. **Built-in LaTeX table structure differs from generate_all_tables.py output.** The runner's `_save_latex_table` produces a 4-column table (one row for PRiskQ_lead, one for PRiskQ_lead2), while `generate_all_tables.py` produces an 8-column table (cols 1-4 for lead1, cols 5-8 for lead2). The 8-column version is what appears in the thesis.

7. **All regressions run across 3 industry samples.** While only the Main sample appears in the published table, Finance and Utility sample regressions are also estimated and saved. This enables robustness checking.
