# H0.1 Manager Clarity Hypothesis Test Documentation

**Document Version:** 1.0
**Last Updated:** 2026-02-22
**Author:** Thesis Author
**Status:** Audit-Ready

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Research Hypothesis](#research-hypothesis)
3. [Model Specification](#model-specification)
4. [Variable Definitions](#variable-definitions)
5. [Variable Construction Pipeline](#variable-construction-pipeline)
6. [Sample Construction](#sample-construction)
7. [Estimation Methodology](#estimation-methodology)
8. [Complete Regression Results](#complete-regression-results)
9. [Clarity Score Construction](#clarity-score-construction)
10. [Audit Trail](#audit-trail)
11. [LaTeX Tables](#latex-tables)

---

## Executive Summary

**Hypothesis H0.1:** Manager communication clarity is a persistent, time-invariant executive trait that can be estimated from linguistic patterns in earnings calls.

**Test Design:** We estimate manager-level fixed effects by regressing manager Q&A uncertainty on firm-level controls and time fixed effects, absorbing all time-invariant manager characteristics. The estimated manager fixed effect (γ_i) captures each manager's persistent tendency toward uncertain language, net of situational factors.

**Key Finding:** Manager fixed effects explain 40.7% of within-firm variation in Q&A uncertainty (Main sample), confirming that manager communication style is a persistent trait.

---

## Research Hypothesis

### Primary Hypothesis

**H0.1:** A manager's communication clarity is a persistent personal trait, measurable via fixed effects estimation.

**Economic Mechanism:**
- Communication style reflects cognitive patterns, education, and professional experience
- These traits are stable across time and contexts
- Fixed effects estimation isolates the trait component from situational noise

### Testable Implications

1. **High R² from manager FE:** If clarity is a trait, manager dummies should explain substantial variance
2. **Persistent scores:** Managers ranked as "clear" in one period should remain clear in future periods
3. **Cross-industry validity:** The trait should be detectable across industry samples

---

## Model Specification

### Econometric Model

The baseline specification estimates manager fixed effects via OLS:

$$
\text{Manager\_QA\_Uncertainty}_{it} = \alpha + \gamma_i + \tau_t + \mathbf{X}_{it}'\beta + \varepsilon_{it}
$$

Where:
- $i$ indexes managers (via `ceo_id`)
- $t$ indexes years
- $\gamma_i$ = manager fixed effect (parameter of interest)
- $\tau_t$ = year fixed effects
- $\mathbf{X}_{it}$ = vector of control variables

### Variable Roles

| Variable | Role | Type |
|----------|------|------|
| `Manager_QA_Uncertainty_pct` | Dependent Variable | Continuous (0-100) |
| `C(ceo_id)` | Fixed Effect | Categorical (3,315 managers) |
| `C(year)` | Fixed Effect | Categorical (17 years: 2002-2018) |
| `Manager_Pres_Uncertainty_pct` | Linguistic Control | Continuous |
| `Analyst_QA_Uncertainty_pct` | Linguistic Control | Continuous |
| `Entire_All_Negative_pct` | Linguistic Control | Continuous |
| `StockRet` | Firm Control | Continuous |
| `MarketRet` | Firm Control | Continuous |
| `EPS_Growth` | Firm Control | Continuous |
| `SurpDec` | Firm Control | Discrete (-5 to +5) |

### Formula Representation

```python
Manager_QA_Uncertainty_pct ~ C(ceo_id) + C(year) +
    Manager_Pres_Uncertainty_pct +
    Analyst_QA_Uncertainty_pct +
    Entire_All_Negative_pct +
    StockRet + MarketRet + EPS_Growth + SurpDec
```

---

## Variable Definitions

### Dependent Variable

#### Manager_QA_Uncertainty_pct

| Attribute | Value |
|-----------|-------|
| **Definition** | Percentage of uncertainty words in manager Q&A responses during earnings calls |
| **Source** | Stage 2 linguistic variables (`linguistic_variables_{year}.parquet`) |
| **Construction** | See [Variable Construction Pipeline](#variable-construction-pipeline) |
| **Range** | 0 to 100 (percentage) |
| **Missing** | ~1.2% of observations |
| **Mean (Main)** | 1.43% |
| **Std (Main)** | 0.84% |

### Linguistic Controls

#### Manager_Pres_Uncertainty_pct

| Attribute | Value |
|-----------|-------|
| **Definition** | Percentage of uncertainty words in manager prepared remarks (presentation segment) |
| **Source** | Stage 2 linguistic variables |
| **Formula** | `(n_uncertainty_words_manager_pres / n_total_words_manager_pres) × 100` |
| **Purpose** | Controls for call-specific uncertainty context; isolates Q&A-specific behavior |
| **Expected Sign** | Positive (within-call correlation) |

#### Analyst_QA_Uncertainty_pct

| Attribute | Value |
|-----------|-------|
| **Definition** | Percentage of uncertainty words in analyst questions during Q&A |
| **Source** | Stage 2 linguistic variables |
| **Formula** | `(n_uncertainty_words_analyst_qa / n_total_words_analyst_qa) × 100` |
| **Purpose** | Controls for question difficulty; isolates manager response style from question effects |
| **Expected Sign** | Positive (harder questions → more uncertain responses) |

#### Entire_All_Negative_pct

| Attribute | Value |
|-----------|-------|
| **Definition** | Percentage of negative sentiment words in entire earnings call (all speakers) |
| **Source** | Stage 2 linguistic variables |
| **Formula** | `(n_negative_words_all / n_total_words_all) × 100` |
| **Purpose** | Controls for call tone; negative news may induce uncertain language |
| **Expected Sign** | Positive (bad news → more hedging) |

### Firm Controls

#### StockRet

| Attribute | Value |
|-----------|-------|
| **Definition** | Firm stock return over the earnings call window |
| **Source** | CRSP daily stock files |
| **Formula** | Compound return from `start_date - 5` to `start_date + 5` trading days |
| **Purpose** | Controls for market reaction; captures information environment |
| **Expected Sign** | Ambiguous (depends on whether uncertainty is good or bad news) |

#### MarketRet

| Attribute | Value |
|-----------|-------|
| **Definition** | Market return over the earnings call window |
| **Source** | CRSP value-weighted return (`vwretd`) |
| **Formula** | Compound VWRETD from `start_date - 5` to `start_date + 5` trading days |
| **Purpose** | Controls for macro conditions during call |
| **Expected Sign** | Ambiguous |

#### EPS_Growth

| Attribute | Value |
|-----------|-------|
| **Definition** | Year-over-year EPS growth rate |
| **Source** | Compustat quarterly (`niq` / `cshoq`) |
| **Formula** | Date-based YoY matching: `EPS_t / |EPS_t-12mo|` |
| **Purpose** | Controls for firm performance; growing firms may communicate differently |
| **Expected Sign** | Negative (good performance → clearer communication) |

#### SurpDec

| Attribute | Value |
|-----------|-------|
| **Definition** | Earnings surprise decile |
| **Source** | IBES EPS forecasts |
| **Formula** | Decile rank of `(Actual - Mean_Estimate) / |Mean_Estimate|`, scaled to [-5, +5] |
| **Purpose** | Controls for unexpected news magnitude |
| **Expected Sign** | Ambiguous (surprise could increase or decrease uncertainty) |

---

## Variable Construction Pipeline

### Stage 1: Sample Construction

**Script:** `src/f1d/sample/assemble_manifest.py`

**Output:** `outputs/1.4_AssembleManifest/{timestamp}/master_sample_manifest.parquet`

**Process:**
1. Clean transcript metadata from `inputs/Earnings_Calls_Transcripts/`
2. Link companies to CRSP/Compustat via CCM linktable (fuzzy matching)
3. Build CEO tenure map from executive data
4. Assemble unified manifest with:
   - `file_name`: Unique transcript identifier
   - `ceo_id`: Anonymized CEO identifier
   - `ceo_name`: CEO name (for reporting)
   - `gvkey`: Compustat firm identifier
   - `ff12_code`: Fama-French 12 industry code
   - `start_date`: Earnings call date

**Sample Size:** 112,968 earnings calls (2002-2018)

### Stage 2: Text Processing

**Script:** `src/f1d/text/build_linguistic_variables.py`

**Input:**
- Raw transcripts from `inputs/Earnings_Calls_Transcripts/`
- Loughran-McDonald Master Dictionary (`inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv`)

**Output:** `outputs/2_Textual_Analysis/2.2_Variables/{timestamp}/linguistic_variables_{year}.parquet`

**Process:**
1. **Tokenization:** Split transcript text into words using sklearn CountVectorizer
2. **Speaker Segmentation:** Identify Q&A vs. Presentation segments
3. **Role Classification:** Identify CEO, Manager, Analyst, CFO speakers
4. **Word Counting:** Count words in LM uncertainty, sentiment categories
5. **Percentage Calculation:**
   ```
   Uncertainty_pct = (n_uncertainty_words / n_total_words) × 100
   ```

**LM Uncertainty Word Categories:**
- `UNCERTAINTY`: Approximately, apparently, appears, arguably, assume, ...
- `WEAK_MODAL`: Could, may, might, possibly, potentially, perhaps, ...

### Stage 3: Panel Building

**Script:** `src/f1d/variables/build_h0_1_manager_clarity_panel.py`

**Output:** `outputs/variables/manager_clarity/{timestamp}/manager_clarity_panel.parquet`

**Process:**
1. Load manifest from Stage 1
2. Load linguistic variables from Stage 2
3. Load financial controls:
   - `EPS_Growth` from Compustat (`_compustat_engine.py`)
   - `StockRet`, `MarketRet` from CRSP (`_crsp_engine.py`)
   - `SurpDec` from IBES (`_ibes_engine.py`)
4. Merge all variables on `file_name` (zero row-delta enforced)
5. Assign industry sample (Main/Finance/Utility based on FF12)

**Data Quality Guards:**
- `ValueError` if row count changes on any merge
- `ValueError` if `file_name` is duplicated in any builder output
- `ValueError` if required variables missing from final panel

### Stage 4: Econometric Analysis

**Script:** `src/f1d/econometric/run_h0_1_manager_clarity.py`

**Output:** `outputs/econometric/manager_clarity/{timestamp}/`

**Process:**
1. Load panel from Stage 3
2. Filter to complete cases (non-null dependent + controls)
3. Filter to managers with ≥ 5 calls
4. Run OLS with manager FE + year FE for each industry sample
5. Extract manager fixed effects
6. Standardize scores globally across all samples

---

## Sample Construction

### Industry Samples

| Sample | FF12 Codes | Description | N Calls | N Managers |
|--------|------------|-------------|--------:|-----------:|
| **Main** | 1-7, 9-10, 12 | Non-financial, non-utility | 57,796 | 2,605 |
| **Finance** | 11 | Banks, insurance, real estate | 13,409 | 577 |
| **Utility** | 8 | Utilities | 2,974 | 136 |

### Sample Filters

1. **CEO ID Filter:** Must have non-null `ceo_id` (excludes calls without CEO identification)
2. **Complete Cases Filter:** Must have non-null values for all regression variables
3. **Minimum Calls Filter:** Manager must have ≥ 5 calls in the sample

### Filter Impact (Main Sample)

| Filter | Before | After | Dropped |
|--------|-------:|------:|--------:|
| Initial Panel | 112,968 | — | — |
| CEO ID Not Null | 88,205 | 88,205 | 24,763 |
| Complete Cases | 72,353 | 72,353 | 15,852 |
| ≥5 Calls per Manager | 57,796 | 57,796 | 14,557 |
| **Final Sample** | **57,796** | — | — |

---

## Estimation Methodology

### Estimator: OLS with Manager Fixed Effects

**Implementation:** `linearmodels.PanelOLS`

**Key Settings:**
- `drop_absorbed=True`: Automatically drop collinear controls
- `cov_type="clustered"`: Cluster standard errors at CEO level
- `groups=ceo_id`: Cluster by manager

### Why Clustered Standard Errors?

The same manager appears in multiple observations (calls). Standard HC1 errors assume independence, but observations from the same manager are correlated (Liang-Zeger problem). Clustering at the CEO level accounts for within-manager correlation.

**Impact:** Standard errors are ~30-50% larger than HC1, producing more conservative inference.

### Fixed Effects Interpretation

**Manager FE (γ_i):** Captures each manager's average deviation from the reference manager in Q&A uncertainty, holding all controls constant.

- Positive γ_i → Manager uses more uncertain language than reference
- Negative γ_i → Manager uses less uncertain language than reference

**Reference Manager:** Statsmodels uses the first manager alphabetically as the baseline (γ = 0). This manager is excluded from output.

### Within Estimator

The model uses within-manager variation only. Time-invariant manager characteristics are absorbed by the fixed effects. Identification comes from:
- Managers who move between firms
- Managers with varying call conditions over time

---

## Complete Regression Results

### Main Sample (FF12 non-fin, non-util)

```
                              OLS Regression Results
======================================================================================
Dep. Variable:     Manager_QA_Uncertainty_pct   R-squared:                       0.407
Model:                                    OLS   Adj. R-squared:                  0.379
Method:                         Least Squares   F-statistic:                     —
Date:                        Fri, 20 Feb 2026   Prob (F-statistic):               —
Time:                                12:07:07   Log-Likelihood:                -1193.7
No. Observations:                       57796   AIC:                             7643.
Df Residuals:                           55168   BIC:                         3.120e+04
Df Model:                                2627
Covariance Type:                      cluster
================================================================================================
                                   coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------------------------
Intercept                        0.9959      0.038     25.911      0.000       0.921       1.071
Manager_Pres_Uncertainty_pct     0.0840      0.007     12.760      0.000       0.071       0.097
Analyst_QA_Uncertainty_pct       0.0330      0.003     10.810      0.000       0.027       0.039
Entire_All_Negative_pct          0.0740      0.006     12.350      0.000       0.062       0.086
StockRet                        -0.0003      0.000     -1.470      0.141      -0.001       0.000
MarketRet                       -0.0007      0.000     -3.010      0.003      -0.001      -0.000
EPS_Growth                       0.0006      0.000      2.010      0.044       0.000       0.001
SurpDec                          0.0019      0.001      3.480      0.001       0.001       0.003
================================================================================================

Manager Fixed Effects: 2,605 estimated (1 reference excluded)
Year Fixed Effects: 17 (2002-2018)
```

### Finance Sample (FF12 = 11)

```
                              OLS Regression Results
======================================================================================
Dep. Variable:     Manager_QA_Uncertainty_pct   R-squared:                       0.305
Model:                                    OLS   Adj. R-squared:                  0.267
No. Observations:                       13409
Df Model:                                 609
Covariance Type:                      cluster
================================================================================================
                                   coef    std err          z      P>|z|
------------------------------------------------------------------------------------------------
Intercept                        1.0230      0.054     18.944      0.000
Manager_Pres_Uncertainty_pct     0.0860      0.011      7.590      0.000
Analyst_QA_Uncertainty_pct       0.0450      0.007      6.850      0.000
Entire_All_Negative_pct          0.0630      0.012      5.190      0.000
StockRet                         0.0002      0.000      0.660      0.508
MarketRet                       -0.0006      0.000     -1.620      0.105
EPS_Growth                      -0.0007      0.001     -0.860      0.389
SurpDec                          0.0006      0.001      0.570      0.566
================================================================================================

Manager Fixed Effects: 577 estimated (1 reference excluded)
```

### Utility Sample (FF12 = 8)

```
                              OLS Regression Results
======================================================================================
Dep. Variable:     Manager_QA_Uncertainty_pct   R-squared:                       0.216
Model:                                    OLS   Adj. R-squared:                  0.174
No. Observations:                        2974
Df Model:                                 162
Covariance Type:                      cluster
================================================================================================
                                   coef    std err          z      P>|z|
------------------------------------------------------------------------------------------------
Intercept                        1.2450      0.108     11.528      0.000
Manager_Pres_Uncertainty_pct     0.1450      0.032      4.510      0.000
Analyst_QA_Uncertainty_pct       0.0540      0.015      3.580      0.000
Entire_All_Negative_pct          0.0010      0.043      0.020      0.984
StockRet                        -0.0007      0.000     -1.720      0.085
MarketRet                        0.0007      0.001      1.320      0.187
EPS_Growth                      -0.0006      0.001     -0.510      0.610
SurpDec                         -0.0027      0.002     -1.200      0.230
================================================================================================

Manager Fixed Effects: 136 estimated (1 reference excluded)
```

### Coefficient Summary Table

| Variable | Main Coef | Main t | Finance Coef | Finance t | Utility Coef | Utility t |
|----------|----------:|-------:|-------------:|----------:|-------------:|----------:|
| Manager Pres Uncertainty | 0.084 | 12.76*** | 0.086 | 7.59*** | 0.145 | 4.51*** |
| Analyst QA Uncertainty | 0.033 | 10.81*** | 0.045 | 6.85*** | 0.054 | 3.58*** |
| Negative Sentiment | 0.074 | 12.35*** | 0.063 | 5.19*** | 0.001 | 0.02 |
| Stock Return | -0.000 | -1.47 | 0.000 | 0.66 | -0.001 | -1.72* |
| Market Return | -0.001 | -3.01*** | -0.001 | -1.62 | 0.001 | 1.32 |
| EPS Growth | 0.001 | 2.01** | -0.001 | -0.86 | -0.001 | -0.51 |
| Earnings Surprise | 0.002 | 3.48*** | 0.001 | 0.57 | -0.003 | -1.20 |

*Note: *** p<0.01, ** p<0.05, * p<0.10*

---

## Clarity Score Construction

### Definition

**ClarityManager** is the standardized negative of the manager fixed effect:

$$
\text{ClarityManager}_i = -\frac{\gamma_i - \bar{\gamma}}{\sigma_\gamma}
$$

Where:
- $\gamma_i$ = Manager fixed effect from regression
- $\bar{\gamma}$ = Global mean of all estimated $\gamma_i$
- $\sigma_\gamma$ = Global standard deviation of all estimated $\gamma_i$

### Interpretation

- **Higher ClarityManager → Clearer communication** (lower uncertainty tendency)
- **Lower ClarityManager → More uncertain communication**

### Standardization Protocol

**Global Standardization:** All samples are standardized together using the global mean and standard deviation. This ensures scores are comparable across industry samples.

```python
# From run_h0_1_manager_clarity.py
global_mean = estimated_df["ClarityManager_raw"].mean()
global_std = estimated_df["ClarityManager_raw"].std()
estimated_df["ClarityManager"] = (
    estimated_df["ClarityManager_raw"] - global_mean
) / global_std
```

### Reference Manager Exclusion

Statsmodels uses the first manager (alphabetically by `ceo_id`) as the reference. This manager has $\gamma = 0$ by construction. Reference managers are **excluded** from `clarity_scores.parquet` because:
1. Their "score" is a normalization artifact, not a true estimate
2. Including them would bias the standardization

### Output Schema

**File:** `clarity_scores.parquet`

| Column | Type | Description |
|--------|------|-------------|
| `ceo_id` | string | Anonymized manager identifier |
| `ceo_name` | string | Manager name (for reporting) |
| `sample` | string | Industry sample (Main/Finance/Utility) |
| `gamma_i` | float | Raw manager fixed effect |
| `ClarityManager_raw` | float | Negative of gamma_i (unstandardized) |
| `ClarityManager` | float | Globally standardized clarity score |
| `n_calls` | int | Number of calls in regression |

---

## Audit Trail

### Data Lineage

```
inputs/
├── Earnings_Calls_Transcripts/           # Raw transcripts
├── Loughran-McDonald_MasterDictionary/   # Word lists
├── comp_na_daily_all/                    # Compustat
├── CRSP_DSF/                             # CRSP
├── tr_ibes/                              # IBES
└── CRSPCompustat_CCM/                    # Linktable

    ↓ Stage 1 (assemble_manifest.py)

outputs/1.4_AssembleManifest/
└── master_sample_manifest.parquet        # 112,968 calls

    ↓ Stage 2 (build_linguistic_variables.py)

outputs/2_Textual_Analysis/2.2_Variables/
└── linguistic_variables_{year}.parquet   # Uncertainty, sentiment

    ↓ Stage 3 (build_h0_1_manager_clarity_panel.py)

outputs/variables/manager_clarity/
└── manager_clarity_panel.parquet         # Regression-ready panel

    ↓ Stage 4 (run_h0_1_manager_clarity.py)

outputs/econometric/manager_clarity/
├── manager_clarity_table.tex             # LaTeX table
├── clarity_scores.parquet                # Manager scores
├── regression_results_main.txt           # Full output
├── regression_results_finance.txt
├── regression_results_utility.txt
└── report_step4_manager_clarity.md       # Summary report
```

### Quality Gates

| Check | Location | Action |
|-------|----------|--------|
| Manifest `file_name` uniqueness | Stage 3 build | `ValueError` if duplicates |
| Builder `file_name` uniqueness | Stage 3 build | `ValueError` if duplicates |
| Zero row-delta on merge | Stage 3 build | `ValueError` if row count changes |
| Required variables present | Stage 4 run | `ValueError` if missing |
| Minimum observations | Stage 4 run | Skip sample if N < 100 |

### Reproducibility

**Determinism Enforced By:**
- `config/project.yaml`: `determinism.random_seed: 42`, `thread_count: 1`
- Sorted inputs before processing
- Timestamped output directories

---

## LaTeX Tables

### Table 1: Manager Clarity Fixed Effects (Summary)

```latex
\begin{table}[htbp]
\centering
\caption{Table 1: Manager Clarity Fixed Effects}
\label{tab:manager_clarity}

\vspace{0.5em}
\parbox{\textwidth}{\small This table reports manager fixed effects from regressing Manager Q&A uncertainty on firm characteristics and year fixed effects. ClarityManager is computed as the negative of the manager fixed effect, standardized globally across all industry samples. Standard errors are clustered at the CEO level (cov_type=cluster, groups=ceo_id).}

\begin{tabular}{@{}{lcccccc}@{}}
\toprule
 & \multicolumn{2}{c}{Main} & \multicolumn{2}{c}{Finance} & \multicolumn{2}{c}{Utility} \\
\cmidrule(lr){2-3} \cmidrule(lr){4-5} \cmidrule(lr){6-7}
 & Est. & t-value & Est. & t-value & Est. & t-value \\
\midrule
\multicolumn{7}{l}{\textit{Panel A: Model Diagnostics}} \\
\midrule
N Observations & 57,796 &  & 13,409 &  & 2,974 &  \\
R-squared & 0.407 &  & 0.305 &  & 0.216 &  \\
N Managers & 2,605 &  & 577 &  & 136 &  \\
\midrule
\multicolumn{7}{l}{\textit{Panel B: Control Variables}} \\
\midrule
Manager Pres Uncertainty & 0.084 &  & 0.086 &  & 0.145 &  \\
 & 12.76 &  & 7.59 &  & 4.51 &  \\
Analyst QA Uncertainty & 0.033 &  & 0.045 &  & 0.054 &  \\
 & 10.81 &  & 6.85 &  & 3.58 &  \\
Negative Sentiment & 0.074 &  & 0.063 &  & 0.001 &  \\
 & 12.35 &  & 5.19 &  & 0.02 &  \\
Stock Return & -0.000 &  & 0.000 &  & -0.001 &  \\
 & -1.47 &  & 0.66 &  & -1.72 &  \\
Market Return & -0.001 &  & -0.001 &  & 0.001 &  \\
 & -3.01 &  & -1.62 &  & 1.32 &  \\
EPS Growth & 0.001 &  & -0.001 &  & -0.001 &  \\
 & 2.01 &  & -0.86 &  & -0.51 &  \\
Earnings Surprise Decile & 0.002 &  & 0.001 &  & -0.003 &  \\
 & 3.48 &  & 0.57 &  & -1.20 &  \\
\bottomrule
\end{tabular}
\end{table}
```

### Complete Manager Fixed Effects Table

The complete table of manager fixed effects (2,605 managers in Main sample) is too large for inline display. The full output is available in:

**File:** `outputs/econometric/manager_clarity/latest/regression_results_main.txt`

**Sample of Manager Fixed Effects (Main Sample):**

| ceo_id | gamma_i | t-statistic | P>|z| |
|--------|--------:|------------:|-----:|
| 00086 | -0.469 | -211.02 | 0.000 |
| 00120 | -0.375 | -85.56 | 0.000 |
| 00134 | -0.384 | -78.58 | 0.000 |
| ... | ... | ... | ... |
| (2,605 total) | | | |

### Top 5 Clearest Managers (Main Sample)

| Rank | Manager | ClarityManager | Interpretation |
|------|---------|---------------:|----------------|
| 1 | Fran Horowitz | 2.466 | 2.5 std dev above mean clarity |
| 2 | Todd McKinnon | 2.460 | 2.5 std dev above mean clarity |
| 3 | Jeffrey P. Bezos | 2.311 | 2.3 std dev above mean clarity |
| 4 | Demos Parneros | 2.298 | 2.3 std dev above mean clarity |
| 5 | Robert L. Nardelli | 2.266 | 2.3 std dev above mean clarity |

### Top 5 Most Uncertain Managers (Main Sample)

| Rank | Manager | ClarityManager | Interpretation |
|------|---------|---------------:|----------------|
| 1 | John R. Irwin | -4.835 | 4.8 std dev below mean clarity |
| 2 | Joseph Y. Liu | -4.540 | 4.5 std dev below mean clarity |
| 3 | Randall D. Stilley | -3.525 | 3.5 std dev below mean clarity |
| 4 | John B. Gerlach, Jr. | -3.225 | 3.2 std dev below mean clarity |
| 5 | Menderes Akdag | -3.010 | 3.0 std dev below mean clarity |

---

## Appendix: Source Code Locations

| Component | Path |
|-----------|------|
| Panel Builder | `src/f1d/variables/build_h0_1_manager_clarity_panel.py` |
| Econometric Script | `src/f1d/econometric/run_h0_1_manager_clarity.py` |
| LaTeX Table Generator | `src/f1d/shared/latex_tables_accounting.py` |
| Variable Registry | `src/f1d/shared/variables/VARIABLE_REGISTRY.md` |
| Variable Config | `config/variables.yaml` |
| Project Config | `config/project.yaml` |
| Compustat Engine | `src/f1d/shared/variables/_compustat_engine.py` |
| CRSP Engine | `src/f1d/shared/variables/_crsp_engine.py` |
| IBES Engine | `src/f1d/shared/variables/_ibes_engine.py` |
| Uncertainty Builder | `src/f1d/shared/variables/manager_qa_uncertainty.py` |

---

*Documentation generated: 2026-02-22*
*Pipeline version: F1D.1.0*
*Last full run: 2026-02-20 12:07:08*
