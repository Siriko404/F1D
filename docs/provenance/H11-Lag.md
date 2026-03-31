# H11-Lag Political Risk (Lagged) -- Provenance Document

**Generated:** 2026-03-30 (manual trace)
**Auditor method:** Manual file reading, grep, line-level verification.
Every claim cites file path + line number. No documentation generators used.

---

## A. SUITE IDENTITY

```yaml
Suite ID:        H11-Lag
Title:           H11-Lag: Lagged Political Risk and Language Uncertainty
Hypothesis:      Higher political risk in quarter t-1 (and t-2) is associated
                 with higher language uncertainty in subsequent earnings calls.
                 Lagged variant of H11 to establish temporal ordering.
Direction:       One-tailed (beta > 0)
Model Family:    Linear panel regression with absorbed fixed effects
Estimator:       linearmodels.panel.PanelOLS
Unit of Obs:     Individual earnings call (file_name)
Panel Index:     (gvkey, year)  -- year = calendar year from start_date
Columns:         8 (in generate_all_tables.py); runner also produces Finance
                 and Utility sub-sample regressions (24 total regressions)
Reference:       Hassan, Hollander, van Lent & Tahoun (2019) -- PRisk source
Runner:          src/f1d/econometric/run_h11_prisk_uncertainty_lag.py
Panel Builder:   src/f1d/variables/build_h11_prisk_uncertainty_lag_panel.py
```

---

## B. MODEL SPECIFICATION

### B1. Regression Equation

Each specification estimates a single IV against a single DV (not all 4 IVs simultaneously). Two IVs are tested: PRiskQ_lag (t-1) and PRiskQ_lag2 (t-2).

**For QA dependent variables (cols 1, 2, 5, 6):**

$$
\text{DV}_{i,t} = \beta_1 \cdot \text{IV}_{i,t}
+ \gamma_1 \cdot \text{Presentation\_control}_{i,t}
+ \gamma_2 \cdot \text{Analyst\_QA\_Uncertainty\_pct}_{i,t}
+ \gamma \mathbf{X}_{i,t}
+ \alpha_i + \delta_t + \varepsilon_{i,t}
$$

**For Presentation dependent variables (cols 3, 4, 7, 8):**

$$
\text{DV}_{i,t} = \beta_1 \cdot \text{IV}_{i,t}
+ \gamma_1 \cdot \text{Analyst\_QA\_Uncertainty\_pct}_{i,t}
+ \gamma \mathbf{X}_{i,t}
+ \alpha_i + \delta_t + \varepsilon_{i,t}
$$

where $\alpha_i$ is firm FE (EntityEffects, absorbed via gvkey index) and $\delta_t$ is calendar year FE (TimeEffects, absorbed via year index).

*Source: run_h11_prisk_uncertainty_lag.py, lines 184--188 (formula construction), lines 200--203 (PanelOLS.from_formula).*

### B2. Dependent Variable(s)

| Variable Name (code) | Description | Formula | Source Engine | Timing |
|---|---|---|---|---|
| `Manager_QA_Uncertainty_pct` | All managers' Q&A uncertainty word percentage | (LM uncertainty word count by managers in Q&A / total manager Q&A words) * 100 | LinguisticEngine | Contemporaneous (call-level) |
| `CEO_QA_Uncertainty_pct` | CEO Q&A uncertainty word percentage | (LM uncertainty word count by CEO in Q&A / total CEO Q&A words) * 100 | LinguisticEngine | Contemporaneous (call-level) |
| `Manager_Pres_Uncertainty_pct` | All managers' presentation uncertainty word percentage | (LM uncertainty word count by managers in presentation / total manager presentation words) * 100 | LinguisticEngine | Contemporaneous (call-level) |
| `CEO_Pres_Uncertainty_pct` | CEO presentation uncertainty word percentage | (LM uncertainty word count by CEO in presentation / total CEO presentation words) * 100 | LinguisticEngine | Contemporaneous (call-level) |

Note: This is the reverse IV/DV structure compared to the standard 4-IV suites. Here, the uncertainty measures are DVs and political risk is the IV.

*Source: run_h11_prisk_uncertainty_lag.py, lines 90--96 (CONFIG["dependent_variables"]); build_linguistic_variables.py, line 496 (pct formula).*

### B3. Independent Variable(s)

| Variable Name (code) | Description | Formula | Source Engine | Timing |
|---|---|---|---|---|
| `PRiskQ_lag` | Quarterly political risk exposure, 1-quarter lag | PRisk from Hassan et al. (2019) for calendar quarter Q-1, matched to call in quarter Q via (gvkey, cal_q_lag) | PRiskQLagBuilder: inputs/FirmLevelRisk/firmquarter_2022q1.csv | Lag t-1 (prior quarter) |
| `PRiskQ_lag2` | Quarterly political risk exposure, 2-quarter lag | PRisk from Hassan et al. (2019) for calendar quarter Q-2, matched to call in quarter Q via (gvkey, cal_q_lag2) | PRiskQLag2Builder: inputs/FirmLevelRisk/firmquarter_2022q1.csv | Lag t-2 (two quarters prior) |

Each specification tests exactly ONE IV against ONE DV. The two IVs are never in the same regression.

*Source: run_h11_prisk_uncertainty_lag.py, line 97 (CONFIG["iv_vars"]); prisk_q_lag.py, lines 119--209; prisk_q_lag2.py, lines 122--212.*

### B4. Control Variables

**Base Controls (all specifications):**

| Variable Name (code) | Description | Formula | Source Engine |
|---|---|---|---|
| `Analyst_QA_Uncertainty_pct` | Analyst Q&A uncertainty word percentage | (LM uncertainty word count by analysts in Q&A / total analyst Q&A words) * 100 | LinguisticEngine |
| `Entire_All_Negative_pct` | Entire-call negative sentiment percentage | (LM negative word count for entire call / total call words) * 100 | LinguisticEngine |
| `Size` | Firm size | ln(atq) | CompustatEngine: atq |
| `TobinsQ` | Tobin's Q | (cshoq * prccq + dlcq + dlttq) / atq | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq |
| `ROA` | Return on assets | iby_annual / avg_assets, where avg_assets = (atq_t + atq_{t-1}) / 2 | CompustatEngine: iby, atq |
| `CashHoldings` | Cash and equivalents ratio | cheq / atq | CompustatEngine: cheq, atq |
| `DividendPayer` | Binary dividend payer indicator | 1 if dvy_annual > 0, else 0 | CompustatEngine: dvy |
| `firm_maturity` | Firm maturity (retained earnings ratio) | req / atq | CompustatEngine: req, atq |
| `earnings_volatility` | Earnings volatility | Rolling std(iby/atq) over trailing 5 fiscal years (1826 days), min 3 obs | CompustatEngine: iby, atq |

**Dynamic Presentation Control (QA DVs only):**

| DV | Added Control |
|---|---|
| `Manager_QA_Uncertainty_pct` | `Manager_Pres_Uncertainty_pct` |
| `CEO_QA_Uncertainty_pct` | `CEO_Pres_Uncertainty_pct` |
| `Manager_Pres_Uncertainty_pct` | None |
| `CEO_Pres_Uncertainty_pct` | None |

**No Lagged_DV:** This suite does not include a lagged dependent variable control.

*Source: run_h11_prisk_uncertainty_lag.py, lines 100--110 (BASE_CONTROLS), lines 112--117 (PRES_CONTROL_MAP), lines 161--163 (dynamic addition).*

### B5. Fixed Effects

| FE Type | Column Used | Description |
|---|---|---|
| Entity | `gvkey` | Firm FE (absorbed via PanelOLS EntityEffects) |
| Time | `year` | Calendar year FE (absorbed via PanelOLS TimeEffects) |

The panel index is `["gvkey", "year"]` (line 200). `year` is derived from `start_date.dt.year` in the panel builder (line 151), making it calendar year. PanelOLS absorbs firm FE via the first index level and time FE via the second.

*Source: run_h11_prisk_uncertainty_lag.py, line 200 (set_index); build_h11_prisk_uncertainty_lag_panel.py, line 151 (year construction).*

### B6. Standard Errors and Clustering

- **cov_type:** `"clustered"` (line 204)
- **Clustering dimension:** Entity only (`cluster_entity=True`, line 204)
- **Cluster variable:** `gvkey` (firm-level)
- No small-sample corrections beyond what PanelOLS provides by default.

*Source: run_h11_prisk_uncertainty_lag.py, line 204.*

### B7. Hypothesis Test

- **Direction:** One-tailed, beta > 0 (higher prior-quarter political risk -> higher speech uncertainty)
- **P-value computation:** Two-tailed p from PanelOLS is halved if beta > 0; set to 1 - p_two/2 if beta < 0 (lines 221--222)
- **Significance thresholds:** *** p < 0.01, ** p < 0.05, * p < 0.10 (lines 287--291, fmt_coef function)
- **Hypothesis confirmed at:** p_one < 0.05 AND beta > 0 (line 225)

*Source: run_h11_prisk_uncertainty_lag.py, lines 219--225 (p-value logic), lines 283--291 (stars).*

---

## C. MODEL SPECIFICATION REGISTER

The published table (generate_all_tables.py) shows 8 columns, all from the Main sample. The runner also produces Finance and Utility sub-sample regressions (not in the table).

| Col | DV | IV | Entity FE | Time FE | Controls | Notes |
|-----|---|---|-----------|---------|----------|-------|
| 1 | Manager_QA_Uncertainty_pct | PRiskQ_lag | Firm | Cal Year | Base + Manager_Pres_Uncertainty_pct | Main sample, lag-1 |
| 2 | CEO_QA_Uncertainty_pct | PRiskQ_lag | Firm | Cal Year | Base + CEO_Pres_Uncertainty_pct | Main sample, lag-1 |
| 3 | Manager_Pres_Uncertainty_pct | PRiskQ_lag | Firm | Cal Year | Base only | Main sample, lag-1 |
| 4 | CEO_Pres_Uncertainty_pct | PRiskQ_lag | Firm | Cal Year | Base only | Main sample, lag-1 |
| 5 | Manager_QA_Uncertainty_pct | PRiskQ_lag2 | Firm | Cal Year | Base + Manager_Pres_Uncertainty_pct | Main sample, lag-2 |
| 6 | CEO_QA_Uncertainty_pct | PRiskQ_lag2 | Firm | Cal Year | Base + CEO_Pres_Uncertainty_pct | Main sample, lag-2 |
| 7 | Manager_Pres_Uncertainty_pct | PRiskQ_lag2 | Firm | Cal Year | Base only | Main sample, lag-2 |
| 8 | CEO_Pres_Uncertainty_pct | PRiskQ_lag2 | Firm | Cal Year | Base only | Main sample, lag-2 |

All 8 columns use identical FE structure (firm + calendar year). The variation is in DV and IV.

*Source: run_h11_prisk_uncertainty_lag.py, lines 508--553 (loop structure); generate_all_tables.py, lines 219--247 (col_files mapping).*

---

## D. SAMPLE CONSTRUCTION

### D1. Population

- **Starting dataset:** `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`
- **Total calls:** 112,968 (per project scope)
- **Unique firms:** ~2,429
- **Year range:** 2002--2018

### D2. Exclusion Criteria (in order applied)

| Step | Filter | Description | Row Count |
|------|--------|-------------|-----------|
| 1 | Full manifest | All calls loaded from parquet | [RUNTIME] |
| 2 | Industry sample assignment | `assign_industry_sample(ff12_code)`: FF12=11 -> Finance, FF12=8 -> Utility, all others -> Main | [RUNTIME] |
| 3 | Sample selection | Runner filters to one sample at a time (Main / Finance / Utility) | [RUNTIME] |
| 4 | Complete case | `replace([inf, -inf], NaN).dropna(subset=required)` removes rows with any missing required variable (line 172) | [RUNTIME] |
| 5 | Min calls per firm | Firms with < 5 calls in sample are excluded (lines 526--531) | [RUNTIME] |
| 6 | Minimum rows check | Specifications with < 100 rows after filtering are skipped (line 537) | [RUNTIME] |

[UNVERIFIED -- row counts require runtime execution of the panel builder and runner. The runner's attrition table (lines 564--568) records only 3 coarse stages at runtime: Master manifest count, Main sample filter count, and final after complete-case + min-calls count. Per-step counts are not available without execution.]

Note: The exact row counts per step depend on runtime data and vary by DV (because QA specs have one more control than Pres specs, so complete-case drops may differ).

*Source: run_h11_prisk_uncertainty_lag.py, lines 172 (complete case), 526--531 (min calls), 537 (min 100 check), 559--569 (attrition).*

### D3. Sample Counts per Specification

N varies across model specs due to:
- Different DVs having different missingness patterns
- QA specs include an extra Presentation control (one more column to be non-missing)
- PRiskQ_lag vs PRiskQ_lag2 have different coverage (lag-2 loses an extra quarter of edge data)

Exact counts are recorded in `model_diagnostics.csv` at runtime (lines 236--251, written at line 556).

---

## E. VARIABLE DICTIONARY

| Variable (code) | Label | Type | Formula | Source | Winsorized | Timing |
|---|---|---|---|---|---|---|
| `Manager_QA_Uncertainty_pct` | Mgr QA Uncertainty | DV | (LM uncertainty count / total words) * 100, for managers in Q&A section | LinguisticEngine: Stage 2 year-partitioned parquets | 0%/99% upper-only per-year (engine level) | Contemporaneous |
| `CEO_QA_Uncertainty_pct` | CEO QA Uncertainty | DV | (LM uncertainty count / total words) * 100, for CEO in Q&A section | LinguisticEngine | 0%/99% upper-only per-year (engine level) | Contemporaneous |
| `Manager_Pres_Uncertainty_pct` | Mgr Pres Uncertainty | DV / Control | (LM uncertainty count / total words) * 100, for managers in presentation | LinguisticEngine | 0%/99% upper-only per-year (engine level) | Contemporaneous |
| `CEO_Pres_Uncertainty_pct` | CEO Pres Uncertainty | DV / Control | (LM uncertainty count / total words) * 100, for CEO in presentation | LinguisticEngine | 0%/99% upper-only per-year (engine level) | Contemporaneous |
| `PRiskQ_lag` | Political Risk (t-1) | IV | PRisk from Hassan et al. (2019) for cal quarter Q-1 | PRiskQLagBuilder: firmquarter_2022q1.csv | 1%/99% per-year (builder level) | Lag t-1 |
| `PRiskQ_lag2` | Political Risk (t-2) | IV | PRisk from Hassan et al. (2019) for cal quarter Q-2 | PRiskQLag2Builder: firmquarter_2022q1.csv | 1%/99% per-year (builder level) | Lag t-2 |
| `Analyst_QA_Uncertainty_pct` | Analyst QA Uncertainty | Control | (LM uncertainty count / total words) * 100, for analysts in Q&A section | LinguisticEngine | 0%/99% upper-only per-year (engine level) | Contemporaneous |
| `Entire_All_Negative_pct` | Negative Sentiment | Control | (LM negative count / total words) * 100, for entire call | LinguisticEngine | 0%/99% upper-only per-year (engine level) | Contemporaneous |
| `Size` | Firm Size (log AT) | Control | ln(atq) where atq > 0; else NaN | CompustatEngine: atq | 1%/99% per fiscal year (engine level) | Contemporaneous (merge_asof backward) |
| `TobinsQ` | Tobin's Q | Control | (cshoq * prccq + debt_book) / atq | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq | 1%/99% per fiscal year (engine level) | Contemporaneous |
| `ROA` | Return on Assets | Control | iby_annual (Q4 value) / avg_assets, where avg_assets = (atq_t + atq_{t-1}) / 2 | CompustatEngine: iby, atq | 1%/99% per fiscal year (engine level) | Contemporaneous |
| `CashHoldings` | Cash Holdings | Control | cheq / atq | CompustatEngine: cheq, atq | 1%/99% per fiscal year (engine level) | Contemporaneous |
| `DividendPayer` | Dividend Payer | Control | 1 if dvy_annual (Q4 cumulative) > 0, else 0 | CompustatEngine: dvy | No (binary variable, skip_winsorize) | Contemporaneous |
| `firm_maturity` | Firm Maturity | Control | req / atq (retained earnings / total assets) | CompustatEngine: req, atq | 1%/99% per fiscal year (engine level) | Contemporaneous |
| `earnings_volatility` | Earnings Volatility | Control | rolling std(iby/atq) over trailing 1826 days (~5 years), min 3 obs | CompustatEngine: iby, atq | 1%/99% per fiscal year (engine level) | Contemporaneous |
| `gvkey` | Firm identifier | FE (Entity) | 6-digit Compustat identifier | Manifest | N/A | N/A |
| `year` | Calendar year | FE (Time) | start_date.dt.year | Manifest: start_date | N/A | N/A |

*Source: Builder files enumerated in Sections B2--B5; _compustat_engine.py lines 938 (Size), 981 (CashHoldings), 943 (BookLev), 962 (ROA), 988 (TobinsQ), 1005 (DividendPayer), 802 (firm_maturity), 807--821 (earnings_volatility); _linguistic_engine.py lines 255--258 (winsorization); build_linguistic_variables.py line 496 (pct formula).*

---

## F. DATA PIPELINE

### F1. Dependency Chain

1. **Raw inputs:**
   - `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet` (call manifest with file_name, gvkey, start_date, ff12_code)
   - `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (Hassan et al. quarterly PRisk, TAB-separated)
   - Compustat quarterly fundamentals (via CompustatEngine, raw source files)
   - Stage 2 linguistic variables: `outputs/2_Textual_Analysis/2.2_Variables/latest/` (year-partitioned parquet files)

2. **Engine loading:**
   - LinguisticEngine: loads year-partitioned linguistic parquets, applies per-year 0%/99% upper-only winsorization to all _pct columns, caches result
   - CompustatEngine: loads raw Compustat quarterly, computes all ratio variables, applies per-fiscal-year 1%/99% winsorization, matches to manifest via merge_asof backward on (gvkey, datadate)

3. **Panel builder** (`build_h11_prisk_uncertainty_lag_panel.py`):
   - Loads manifest via ManifestFieldsBuilder (base DataFrame)
   - Builds all variables via 16 builders (see F2 below)
   - Merges each builder's output onto manifest by `file_name` (left join, zero row-delta enforced)
   - Assigns industry sample: `assign_industry_sample(ff12_code)`
   - Derives `year = start_date.dt.year` and `cal_q` for reference
   - Saves `h11_prisk_uncertainty_lag_panel.parquet`

4. **Runner loading** (`run_h11_prisk_uncertainty_lag.py`):
   - Loads panel parquet, selecting 19 specific columns (lines 448--471)
   - Assigns sample if not already present (line 477)

5. **Sample filtering:**
   - Per (DV, IV, sample) combination:
     - Replace inf/-inf with NaN, drop rows missing any required variable (line 172)
     - Filter to target sample (Main / Finance / Utility)
     - Drop firms with < 5 calls (lines 526--531)

6. **Regression estimation:**
   - PanelOLS.from_formula with EntityEffects + TimeEffects, cov_type="clustered", cluster_entity=True
   - One regression per (DV, IV, sample) = 4 * 2 * 3 = 24 regressions maximum
   - Results saved to individual .txt files and model_diagnostics.csv

7. **Table generation:**
   - Runner produces its own h11_prisk_uncertainty_lag_table.tex (lines 256--406)
   - generate_all_tables.py reads the 8 Main-sample .txt files to produce a unified publication table

### F2. Data Engines Used

| Engine | Source Data | Variables Provided to This Suite |
|---|---|---|
| LinguisticEngine | Stage 2 year-partitioned parquets | Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct |
| CompustatEngine | Compustat quarterly fundamentals | Size, TobinsQ, ROA, CashHoldings, DividendPayer, firm_maturity, earnings_volatility, BookLev (built but not used in regressions) |
| PRiskQLagBuilder (standalone) | inputs/FirmLevelRisk/firmquarter_2022q1.csv | PRiskQ_lag |
| PRiskQLag2Builder (standalone) | inputs/FirmLevelRisk/firmquarter_2022q1.csv | PRiskQ_lag2 |

### F3. Merge Operations

All merges occur in the panel builder (lines 130--148). Every merge is a left join on `file_name` with zero row-delta enforcement.

| Left | Right | Keys | Type | Notes |
|---|---|---|---|---|
| manifest (base) | manager_qa_uncertainty | file_name | left | LinguisticEngine data |
| panel | ceo_qa_uncertainty | file_name | left | LinguisticEngine data |
| panel | manager_pres_uncertainty | file_name | left | LinguisticEngine data |
| panel | ceo_pres_uncertainty | file_name | left | LinguisticEngine data |
| panel | prisk_q_lag | file_name | left | PRiskQLagBuilder: manifest merged with PRisk on (gvkey, cal_q_lag) internally |
| panel | prisk_q_lag2 | file_name | left | PRiskQLag2Builder: manifest merged with PRisk on (gvkey, cal_q_lag2) internally |
| panel | analyst_qa_uncertainty | file_name | left | LinguisticEngine data |
| panel | negative_sentiment | file_name | left | LinguisticEngine data |
| panel | size | file_name | left | CompustatEngine data |
| panel | lev (BookLev) | file_name | left | CompustatEngine data; built but NOT used in runner |
| panel | roa | file_name | left | CompustatEngine data |
| panel | tobins_q | file_name | left | CompustatEngine data |
| panel | cash_holdings | file_name | left | CompustatEngine data |
| panel | dividend_payer | file_name | left | CompustatEngine data |
| panel | firm_maturity | file_name | left | CompustatEngine data |
| panel | earnings_volatility | file_name | left | CompustatEngine data |

*Source: build_h11_prisk_uncertainty_lag_panel.py, lines 130--148.*

---

## G. OUTPUTS

### G1. Stage 3 Outputs (Panel Builder)

| File | Description |
|---|---|
| `h11_prisk_uncertainty_lag_panel.parquet` | Call-level panel with all variables |
| `summary_stats.csv` | Variable summary statistics from builders |
| `report_step3_h11_lag.md` | Build report with panel summary and timing |
| `run_manifest.json` | Reproducibility manifest with input/output paths |

Output directory: `outputs/variables/h11_prisk_uncertainty_lag/{timestamp}/`

*Source: build_h11_prisk_uncertainty_lag_panel.py, lines 183--208 (save_outputs), lines 211--237 (generate_report).*

### G2. Stage 4 Outputs (Runner)

| File | Description |
|---|---|
| `h11_prisk_uncertainty_lag_table.tex` | Publication LaTeX table (4-column format with lag-1 and lag-2 rows) |
| `model_diagnostics.csv` | Per-model regression metadata (24 rows max) |
| `summary_stats.csv` | Main sample summary statistics |
| `summary_stats.tex` | LaTeX version of summary statistics |
| `sample_attrition.csv` | Sample attrition cascade |
| `sample_attrition.tex` | LaTeX version of attrition cascade |
| `regression_results_{sample}_{dv}_{lag}.txt` | Individual model output (up to 24 files) |
| `run_manifest.json` | Reproducibility manifest |

Output directory: `outputs/econometric/h11_prisk_uncertainty_lag/{timestamp}/`

Filename pattern for individual results: `regression_results_{Main|Finance|Utility}_{DV}_lag{1|2}.txt`

*Source: run_h11_prisk_uncertainty_lag.py, lines 551 (individual results), 555 (LaTeX table), 556 (diagnostics), 497--503 (summary stats), 569 (attrition), 573--583 (manifest).*

### G3. Summary Statistics

Variables included in summary stats (lines 124--143):

| Variable | Label |
|---|---|
| Manager_QA_Uncertainty_pct | Mgr QA Uncertainty |
| CEO_QA_Uncertainty_pct | CEO QA Uncertainty |
| Manager_Pres_Uncertainty_pct | Mgr Pres Uncertainty |
| CEO_Pres_Uncertainty_pct | CEO Pres Uncertainty |
| PRiskQ_lag | Political Risk$_{t-1}$ |
| PRiskQ_lag2 | Political Risk$_{t-2}$ |
| Analyst_QA_Uncertainty_pct | Analyst QA Uncertainty |
| Entire_All_Negative_pct | Negative Sentiment |
| Size | Firm Size (log AT) |
| TobinsQ | Tobin's Q |
| ROA | ROA |
| CashHoldings | Cash Holdings |
| DividendPayer | Dividend Payer |
| firm_maturity | Firm Maturity |
| earnings_volatility | Earnings Volatility |

Summary statistics are computed by sample (Main, Finance, Utility) via `make_summary_stats_table` (lines 492--503).

---

## H. OUTLIER AND MISSING DATA TREATMENT

### H1. Winsorization

**Linguistic variables (DVs + linguistic controls):**
- Level: 0%/99% upper-only per calendar year
- Applied to: All _pct columns (Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct)
- Applied at: LinguisticEngine level (shared across all suites)
- Source: _linguistic_engine.py, lines 255--258

**Compustat variables (financial controls):**
- Level: 1%/99% per fiscal year (fyearq)
- Applied to: Size, TobinsQ, ROA, CashHoldings, firm_maturity, earnings_volatility, BookLev (built but unused)
- NOT applied to: DividendPayer (binary; in skip_winsorize set)
- Applied at: CompustatEngine level (shared across all suites)
- Source: _compustat_engine.py, lines 1130--1136

**PRisk variables (IVs):**
- Level: 1%/99% per calendar year
- Applied to: PRiskQ_lag, PRiskQ_lag2 (PRisk values winsorized before lag matching)
- Applied at: Builder level (prisk_q_lag.py line 165, prisk_q_lag2.py line 168)
- Source: prisk_q_lag.py lines 164--166, prisk_q_lag2.py lines 167--169

### H2. Missing Data Policy

- Complete-case deletion: rows dropped if any required variable is NaN (line 172 of runner)
- inf/-inf replaced with NaN before dropna (line 172)
- PRisk lag matching: calls with no matching PRisk data get NaN (left join); these are dropped in complete-case step

### H3. Transformations

| Variable | Transformation |
|---|---|
| `Size` | Natural logarithm of atq (atq must be > 0; otherwise NaN) |
| All others | No additional transformations beyond ratio construction |

No centering, z-scoring, or scaling is applied to IVs.

---

## I. GENERATE_ALL_TABLES.PY ENTRY

```python
{
    "id": "H11-Lag",
    "type": "moderation",
    "dir": "h11_prisk_uncertainty_lag/2026-03-27_095002",
    "caption": "H11-Lag: Lagged Political Risk and Language Uncertainty",
    "label": "tab:h11_lag",
    "cols": 8,
    "col_files": {
        1: "regression_results_Main_Manager_QA_Uncertainty_pct_lag1.txt",
        2: "regression_results_Main_CEO_QA_Uncertainty_pct_lag1.txt",
        3: "regression_results_Main_Manager_Pres_Uncertainty_pct_lag1.txt",
        4: "regression_results_Main_CEO_Pres_Uncertainty_pct_lag1.txt",
        5: "regression_results_Main_Manager_QA_Uncertainty_pct_lag2.txt",
        6: "regression_results_Main_CEO_QA_Uncertainty_pct_lag2.txt",
        7: "regression_results_Main_Manager_Pres_Uncertainty_pct_lag2.txt",
        8: "regression_results_Main_CEO_Pres_Uncertainty_pct_lag2.txt",
    },
    "dvs": [
        (r"PRiskQ\_lag", 4),
        (r"PRiskQ\_lag2", 4),
    ],
    "col_dv_labels": [
        "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
        "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
    ],
    "key_vars": ["PRiskQ_lag", "PRiskQ_lag2"],
    "key_labels": [r"PRiskQ\_lag", r"PRiskQ\_lag2"],
    "key_tails": ["one_pos", "one_pos"],
}
```

**Verification:**

| Check | Status |
|---|---|
| key_tails `["one_pos", "one_pos"]` matches runner one-tailed beta > 0 | PASS |
| cols = 8 matches 4 DVs * 2 IVs (Main sample only) | PASS |
| key_vars `["PRiskQ_lag", "PRiskQ_lag2"]` match runner CONFIG["iv_vars"] | PASS |
| col_files naming matches runner output naming pattern (lag1/lag2 suffix) | PASS |
| No top-level "tail" or "hyp_dir" field (type="moderation" uses key_tails instead) | Noted |

*Source: generate_all_tables.py, lines 219--247.*

---

## J. REPRODUCTION COMMANDS

```bash
# Stage 3: Build panel
python -m f1d.variables.build_h11_prisk_uncertainty_lag_panel

# Stage 4: Run regressions
python -m f1d.econometric.run_h11_prisk_uncertainty_lag

# Generate tables (if applicable)
python outputs/generate_all_tables.py
```

---

## K. MODEL-FAMILY ADDENDUM

### K1. PanelOLS Specifics

- **Entity effects:** Absorbed via `EntityEffects` in PanelOLS formula; first level of MultiIndex `(gvkey, year)` = gvkey (firm FE)
- **Time effects:** Absorbed via `TimeEffects` in PanelOLS formula; second level of MultiIndex = year (calendar year FE)
- **other_effects usage:** Not used. All specs use firm FE (no industry FE variant in this suite).
- **drop_absorbed:** `True` (line 203) -- collinear regressors are dropped automatically
- **Singleton handling:** PanelOLS default behavior; no explicit singleton filter

*Source: run_h11_prisk_uncertainty_lag.py, lines 200--203.*

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

1. **BookLev built but not used in regressions.** The panel builder imports and builds `BookLevBuilder` (line 47 of panel builder), but `BookLev` is not in BASE_CONTROLS and is not loaded by the runner (the runner's column list at lines 448--472 does not include BookLev). This is harmless dead weight in the panel parquet.

2. **No Lagged_DV control.** Unlike most other suites in the thesis pipeline, H11-Lag does not include a lagged dependent variable control. This is consistent with the H11 family design where the DV is a call-level linguistic measure without a natural prior-call lag structure.

3. **Panel index is (gvkey, year), not (gvkey, cal_yr_qtr).** Unlike call-level suites that use Year-Quarter FE, H11-Lag uses calendar year FE only. Multiple calls per firm per year share the same panel index value, which is handled natively by PanelOLS (duplicate panel indices are not a blocker).

4. **Runner LaTeX table is 4-column format, not 8-column.** The runner's internal `_save_latex_table` function (lines 256--406) produces a 4-column table with separate rows for lag-1 and lag-2 coefficients. The generate_all_tables.py entry uses an 8-column layout where each lag gets its own 4 columns. These are two different table presentations of the same results.

5. **generate_all_tables.py "dvs" field is misleading.** The entry lists `dvs` as `[(r"PRiskQ\_lag", 4), (r"PRiskQ\_lag2", 4)]`, but PRiskQ_lag/lag2 are IVs, not DVs. This field appears to be used by the table generator to label column groups (IV variant, not DV), which is specific to the H11 family's reversed IV/DV structure. The `type: "moderation"` classification in generate_all_tables.py drives a different table layout than the standard suite type.

6. **Attrition table is simplified.** The runner's attrition cascade (lines 564--568) only records three stages: Master manifest, Main sample filter, and final post-filter count. It does not separately report DV non-missing, IV non-missing, and min-calls stages. Detailed per-step attrition is not available without runtime data.

7. **Linguistic winsorization is asymmetric (0%/99% upper-only).** The LinguisticEngine applies upper-only winsorization (lower=0.0, upper=0.99) because linguistic percentage variables are bounded at 0 by construction. This differs from the symmetric 1%/99% winsorization used for Compustat and PRisk variables.
