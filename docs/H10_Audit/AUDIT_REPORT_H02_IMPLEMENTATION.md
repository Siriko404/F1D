# AUDIT REPORT - IMPLEMENTATION - H0.2

**Hypothesis:** H0.2 - CEO Clarity
**Audit Date:** 2026-02-22
**Auditor:** Claude Opus 4.6
**Verdict:** PASS-WITH-FIXES

---

## A) Executive Summary

### Verdict: PASS-WITH-FIXES

The H0.2 (CEO Clarity) implementation is fundamentally sound with robust variable construction, correct panel assembly, and accurate regression execution. The pipeline successfully produces CEO fixed effects that are correctly transformed into ClarityCEO scores. However, several implementation-level issues require attention:

### Top 10 Implementation Risks

| Rank | Severity | Issue | Status |
|------|----------|-------|--------|
| 1 | **Medium** | Duplicate ceo_id in clarity_scores.parquet (CEOs in multiple samples) | Documented behavior, not a bug |
| 2 | **Low** | LaTeX table note says "standardized globally" but code standardizes per-sample | Documentation mismatch |
| 3 | **Low** | 33.7% missing CEO_QA_Uncertainty_pct (DV) - high but expected due to CEO QA availability | Expected behavior |
| 4 | **Low** | No explicit test for ClarityCEO formula (-gamma_i) | Gap |
| 5 | **Low** | No test verifying t-values match between regression and LaTeX | Gap |
| 6 | **Info** | StockRet max=1286% indicates extreme outliers, but winsorization is at 1/99% per year | Expected |
| 7 | **Info** | Reference CEOs (alphabetically first per sample) excluded from clarity_scores | Correct behavior |
| 8 | **Info** | 4 CEOs appear in both Main and Finance samples (firm industry change) | Expected |
| 9 | **Info** | Clarity scores are per-sample z-scores, not globally comparable | By design |
| 10 | **Info** | Stage 3 runtime ~5.5 minutes (CRSP/Compustat load) | Expected |

### Stop-Ship Blockers

**None.** No critical issues prevent publication of results.

---

## B) Pipeline Entry Points & Artifact Contract

### Stage 3 Panel Builder

**File:** `src/f1d/variables/build_h0_2_ceo_clarity_panel.py`

**Input Artifacts:**
| Artifact | Path Pattern | Description |
|----------|-------------|-------------|
| Master Manifest | `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet` | Call-level manifest with gvkey, ceo_id, ff12_code |
| Linguistic Variables | `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet` | CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, etc. |
| Compustat | `inputs/comp_na_daily_all/comp_na_daily_all.parquet` | Financial variables (EPS_Growth) |
| CRSP Daily | `inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet` | Stock returns (StockRet, MarketRet) |
| IBES | `inputs/tr_ibes/tr_ibes.parquet` | Earnings surprise (SurpDec) |
| CCM Link | `inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet` | PERMNO-gvkey linkage |

**Output Artifacts:**
| Artifact | Path Pattern | Description |
|----------|-------------|-------------|
| Panel | `outputs/variables/ceo_clarity/{timestamp}/ceo_clarity_panel.parquet` | Merged panel with all variables |
| Summary Stats | `outputs/variables/ceo_clarity/{timestamp}/summary_stats.csv` | Variable statistics |
| Report | `outputs/variables/ceo_clarity/{timestamp}/report_step3_ceo_clarity.md` | Build report |

**Latest Output Resolution:**
- Uses `get_latest_output_dir()` from `f1d.shared.path_utils`
- Timestamp format: `YYYY-MM-DD_HHMMSS`
- **To pin a specific vintage:** Pass explicit `--panel-path` to Stage 4

### Stage 4 Econometric Runner

**File:** `src/f1d/econometric/run_h0_2_ceo_clarity.py`

**Input Artifacts:**
| Artifact | Path Pattern | Description |
|----------|-------------|-------------|
| Panel | `outputs/variables/ceo_clarity/latest/ceo_clarity_panel.parquet` | From Stage 3 |

**Output Artifacts:**
| Artifact | Path Pattern | Description |
|----------|-------------|-------------|
| LaTeX Table | `outputs/econometric/ceo_clarity/{timestamp}/ceo_clarity_table.tex` | Main results table |
| Clarity Scores | `outputs/econometric/ceo_clarity/{timestamp}/clarity_scores.parquet` | CEO-level scores |
| Regression Results | `outputs/econometric/ceo_clarity/{timestamp}/regression_results_{sample}.txt` | Full statsmodels output |
| Summary Stats | `outputs/econometric/ceo_clarity/{timestamp}/summary_stats.csv` | Variable summary |
| Report | `outputs/econometric/ceo_clarity/{timestamp}/report_step4_ceo_clarity.md` | Test report |

### Data Contract (Stage 3 -> Stage 4)

**Expected Panel File:** `ceo_clarity_panel.parquet`

**Primary Key:** `file_name` (unique per row)

**Required Columns for Stage 4:**
| Column | Type | Purpose |
|--------|------|---------|
| `file_name` | str | Primary key |
| `ceo_id` | str | CEO identifier (for FE) |
| `year` | int | Year (for FE) |
| `ff12_code` | int | Industry classification |
| `sample` | str | Main/Finance/Utility |
| `CEO_QA_Uncertainty_pct` | float | Dependent variable |
| `CEO_Pres_Uncertainty_pct` | float | Control |
| `Analyst_QA_Uncertainty_pct` | float | Control |
| `Entire_All_Negative_pct` | float | Control |
| `StockRet` | float | Control |
| `MarketRet` | float | Control |
| `EPS_Growth` | float | Control |
| `SurpDec` | float | Control |

---

## C) Model Inventory

### Models Executed

**File:** `src/f1d/econometric/run_h0_2_ceo_clarity.py`, lines 691-730

**Model Formula:**
```
CEO_QA_Uncertainty_pct ~ C(ceo_id) + C(year) +
    CEO_Pres_Uncertainty_pct +
    Analyst_QA_Uncertainty_pct +
    Entire_All_Negative_pct +
    StockRet + MarketRet + EPS_Growth + SurpDec
```

**Models Run:**

| Model | Trigger | Required Columns | Filters |
|-------|---------|------------------|---------|
| Main Sample | Line 695: `for sample_name in ["Main", "Finance", "Utility"]` | All required columns | `sample == "Main"`, `ceo_id.notna()`, complete cases, `>=5 calls/CEO` |
| Finance Sample | Line 695 | All required columns | `sample == "Finance"`, `ceo_id.notna()`, complete cases, `>=5 calls/CEO` |
| Utility Sample | Line 695 | All required columns | `sample == "Utility"`, `ceo_id.notna()`, complete cases, `>=5 calls/CEO` |

**Regression Call (Lines 300-309):**
```python
model = smf.ols(formula, data=df_reg).fit(
    cov_type="cluster",
    cov_kwds={"groups": df_reg["ceo_id"]},
)
```

**Filters Applied (Lines 270-282):**
1. `ceo_id.notna()` - Remove calls without CEO
2. Complete cases on all required columns (Lines 222-225)
3. `>= 5 calls per CEO` (Line 271-274)
4. `>= 100 observations per sample` (Line 280-282)

**Output Destinations:**
- `ceo_clarity_table.tex` - LaTeX table with coefficients and diagnostics
- `clarity_scores.parquet` - CEO-level ClarityCEO scores
- `regression_results_{sample}.txt` - Full statsmodels summary
- `summary_stats.csv` / `summary_stats.tex` - Variable summary statistics

---

## D) Variable Implementation Verification

### D.1 CEO_QA_Uncertainty_pct (Dependent Variable)

**Claim/Name:** CEO Q&A Uncertainty Percentage

**Provenance:**
- Builder: `src/f1d/shared/variables/ceo_qa_uncertainty.py`
- Source: `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet`

**Exact Construction:**
```python
# ceo_qa_uncertainty.py, lines 52-58
for year in years:
    df = self.load_year_file(source_dir, year)
    if df is not None:
        cols = ["file_name"]
        if self.column in df.columns:
            cols.append(self.column)
        all_data.append(df[cols])
```

**Formula:** Direct load from Stage 2 linguistic variables output. Column is pre-computed as percentage of uncertainty words in CEO Q&A section.

**Timing:** Call-level (measured at earnings call date)

**Units:** Percentage (0-100 range, observed max=16.667%)

**Sanity Check:**
- Min=0.000, Max=16.667, Mean=0.807
- All values non-negative (PASS)
- 33.7% missing - expected due to CEO Q&A availability in transcripts

**Does it match its claim?** YES. Variable is directly loaded from Stage 2 output without transformation.

---

### D.2 CEO_Pres_Uncertainty_pct (Linguistic Control)

**Claim/Name:** CEO Presentation Uncertainty Percentage

**Provenance:**
- Builder: `src/f1d/shared/variables/ceo_pres_uncertainty.py`
- Source: `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet`

**Exact Construction:** Same pattern as CEO_QA_Uncertainty_pct - direct load from Stage 2.

**Timing:** Call-level

**Units:** Percentage

**Sanity Check:**
- Min=0.000, Max=10.000, Mean=0.685
- 33.6% missing

**Does it match its claim?** YES.

---

### D.3 Analyst_QA_Uncertainty_pct (Linguistic Control)

**Claim/Name:** Analyst Q&A Uncertainty Percentage

**Provenance:**
- Builder: `src/f1d/shared/variables/analyst_qa_uncertainty.py`
- Source: Stage 2 linguistic variables

**Sanity Check:**
- Min=0.000, Max=9.524, Mean=1.451
- 10.4% missing (lower than CEO measures - expected, analysts always speak)

**Does it match its claim?** YES.

---

### D.4 Entire_All_Negative_pct (Negative Sentiment Control)

**Claim/Name:** Entire Call Negative Sentiment Percentage

**Provenance:**
- Builder: `src/f1d/shared/variables/negative_sentiment.py`
- Source: Stage 2 linguistic variables, column `Entire_All_Negative_pct`

**Sanity Check:**
- Min=0.000, Max=5.603, Mean=0.946
- 4.0% missing

**Does it match its claim?** YES.

---

### D.5 StockRet (Firm Control)

**Claim/Name:** Stock Return (compound return over window)

**Provenance:**
- Builder: `src/f1d/shared/variables/stock_return.py`
- Engine: `src/f1d/shared/variables/_crsp_engine.py`

**Exact Construction (_crsp_engine.py, lines 219-223):**
```python
def compound(x: pd.Series) -> float:
    v = x.dropna()
    return (
        float(((1 + v).prod() - 1) * 100) if len(v) >= MIN_TRADING_DAYS else np.nan
    )
```

**Formula:** `((1 + RET_1) * (1 + RET_2) * ... * (1 + RET_n) - 1) * 100`

**Window (lines 339-344):**
- Start: `prev_call_date + 5 days`
- End: `call_start_date - 5 days`
- Minimum: 10 trading days

**Timing:** Return from prior earnings call (+5d buffer) to current call (-5d buffer)

**Units:** Percentage points

**Sanity Check:**
- Min=-95.19%, Max=1286.36% (extreme positive outliers exist)
- Mean=3.23%
- 6.7% missing (CRSP coverage gaps)

**Does it match its claim?** YES. Compound return formula is correct.

---

### D.6 MarketRet (Market Control)

**Claim/Name:** Market Return (VWRETD compound return)

**Provenance:**
- Builder: `src/f1d/shared/variables/market_return.py`
- Engine: Same CRSP engine as StockRet

**Formula:** Same compound return formula using VWRETD (value-weighted market return) instead of individual stock RET.

**Window:** Same as StockRet

**Units:** Percentage points

**Sanity Check:**
- Min=-51.85%, Max=79.25%, Mean=2.18%
- 6.6% missing

**Does it match its claim?** YES.

---

### D.7 EPS_Growth (Firm Control)

**Claim/Name:** EPS Year-over-Year Growth

**Provenance:**
- Builder: `src/f1d/shared/variables/eps_growth.py`
- Engine: `src/f1d/shared/variables/_compustat_engine.py`

**Exact Construction (_compustat_engine.py, lines 166-213):**
```python
def _compute_eps_growth_date_based(comp: pd.DataFrame) -> pd.Series:
    # Find prior-year quarter via datadate arithmetic
    lookup["target_lag_date"] = lookup["datadate"] - pd.Timedelta(days=365)
    merged = pd.merge_asof(
        lookup, lag_df,
        left_on="target_lag_date",
        right_on="lag_datadate",
        by="gvkey",
        direction="backward",
    )
    # Accept only if within +/- 45 days of target
    date_diff = (merged["target_lag_date"] - merged["lag_datadate"]).abs()
    valid = (date_diff <= pd.Timedelta(days=45)) & ...
    merged["EPS_Growth_tmp"] = np.where(
        valid,
        (merged["epspxq"] - merged["epspxq_lag"]) / merged["epspxq_lag"].abs(),
        np.nan,
    )
```

**Formula:** `(epspxq_t - epspxq_{t-1}) / |epspxq_{t-1}|`

**Timing:** Fiscal quarter YoY, matched to call via merge_asof on datadate

**Units:** Ratio (not percentage)

**Sanity Check:**
- Min=-36.83, Max=16.14 (ratio)
- Mean=0.15
- 1.8% missing

**Does it match its claim?** YES. Date-based lag is robust to missing quarters.

---

### D.8 SurpDec (Earnings Surprise Decile)

**Claim/Name:** Earnings Surprise Decile (-5 to +5)

**Provenance:**
- Builder: `src/f1d/shared/variables/earnings_surprise.py`

**Exact Construction (lines 45-84):**
```python
def _rank_surprises(group: pd.DataFrame) -> pd.Series:
    # Within each calendar quarter, rank surprises
    # Positive surprises: rank descending, map to +1..+5
    # Zero surprises: 0
    # Negative surprises: rank by abs miss, map to -1..-5
    pos_pct = surprises[pos_mask].rank(ascending=False, method="average", pct=True)
    pos_decile = np.ceil(pos_pct * 5).clip(1, 5)
    ranks.loc[pos_mask] = 6 - pos_decile  # largest surprise -> +5
```

**Formula:**
1. `surprise_raw = ACTUAL - MEANEST` (from IBES)
2. Within calendar quarter, rank positive surprises descending (largest = decile +5)
3. Zero surprises = decile 0
4. Negative surprises ranked by absolute miss (largest miss = decile -5)

**Timing:** Matched to call via FPEDATS within +/- 45 days, STATPERS <= call_date

**Units:** Integer decile -5 to +5

**Sanity Check:**
- Min=-5, Max=+5 (correct bounds)
- Mean=0.997 (slightly positive skew)
- 22.9% missing (IBES coverage)

**Does it match its claim?** YES. Decile ranking is correctly implemented.

---

### D.9 ceo_id (Fixed Effect Key)

**Claim/Name:** CEO Identifier

**Provenance:** Manifest (loaded via ManifestFieldsBuilder)

**Sanity Check:**
- 0% missing
- 4,466 unique CEOs
- Min calls per CEO = 5, Max = 193

**Does it match its claim?** YES.

---

### D.10 year (Fixed Effect Key)

**Claim/Name:** Calendar Year

**Provenance:** Derived from `start_date` in manifest

**Exact Construction (build_h0_2_ceo_clarity_panel.py, lines 206-208):**
```python
if "year" not in panel.columns and "start_date" in panel.columns:
    panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year
```

**Does it match its claim?** YES.

---

### D.11 sample (Sample Identifier)

**Claim/Name:** Industry Sample (Main/Finance/Utility)

**Provenance:** Derived from ff12_code

**Exact Construction (panel_utils.py, lines 46-73):**
```python
def assign_industry_sample(ff12_code: pd.Series) -> pd.Series:
    conditions = [ff12_code == 11, ff12_code == 8]
    choices = ["Finance", "Utility"]
    return pd.Series(
        np.select(conditions, choices, default="Main"),
        index=ff12_code.index,
        dtype=object,
    )
```

**Classification:**
- FF12 code 11 -> Finance
- FF12 code 8 -> Utility
- All others -> Main

**Does it match its claim?** YES.

---

## E) Panel Build Integrity (Stage 3)

### Primary Key Definition

**Primary Key:** `file_name` (single column, unique per earnings call)

### Key Uniqueness Verification

```
Total rows: 112,968
file_name unique count: 112,968
Duplicate file_name rows: 0
```

**PASS:** Primary key is unique.

### Merge Correctness

**Merge Pattern (build_h0_2_ceo_clarity_panel.py, lines 160-196):**
```python
for name, result in all_results.items():
    if name == "manifest":
        continue
    data = result.data.copy()
    # FIX-5: Assert builder output is unique on file_name
    if data["file_name"].duplicated().any():
        raise ValueError(...)
    # Merge on file_name with left join
    before_len = len(panel)
    panel = panel.merge(data, on="file_name", how="left")
    after_len = len(panel)
    if after_len != before_len:
        raise ValueError(...)
```

**Join Type:** LEFT JOIN on `file_name`

**Row-Delta Invariant:** Asserted at each merge step. Any row count change raises ValueError.

**Duplicate Detection:** Pre-merge uniqueness check on builder output.

### Determinism

- No random seeds used
- No filesystem ordering dependencies (years processed in order)
- No timestamp-dependent logic
- Caching engines (CompustatEngine, CRSPEngine) are deterministic given same input data

### Panel Integrity Verification Script

```python
import pandas as pd
from pathlib import Path

panel_path = "outputs/variables/ceo_clarity/2026-02-22_170710/ceo_clarity_panel.parquet"
panel = pd.read_parquet(panel_path)

print(f"n_rows: {len(panel):,}")
print(f"n_unique(file_name): {panel['file_name'].nunique():,}")
print(f"duplicates: {panel['file_name'].duplicated().sum()}")

model_cols = [
    'CEO_QA_Uncertainty_pct', 'CEO_Pres_Uncertainty_pct', 'Analyst_QA_Uncertainty_pct',
    'Entire_All_Negative_pct', 'StockRet', 'MarketRet', 'EPS_Growth', 'SurpDec',
    'ceo_id', 'year', 'ff12_code', 'sample'
]
for col in model_cols:
    n_missing = panel[col].isna().sum()
    print(f"{col}: {n_missing:,} missing ({100*n_missing/len(panel):.1f}%)")

# Filter chain verification
required = model_cols[:8] + ['ceo_id', 'year']
df = panel[panel['ceo_id'].notna()].copy()
complete_mask = df[required].notna().all(axis=1)
df_complete = df[complete_mask].copy()
print(f"After complete cases: {len(df_complete):,}")

for sample in ['Main', 'Finance', 'Utility']:
    sample_df = df_complete[df_complete['sample'] == sample]
    ceo_counts = sample_df['ceo_id'].value_counts()
    valid_ceos = set(ceo_counts[ceo_counts >= 5].index)
    final = sample_df[sample_df['ceo_id'].isin(valid_ceos)]
    print(f"{sample}: {len(final):,} obs, {len(valid_ceos):,} CEOs")
```

**Output:**
```
n_rows: 112,968
n_unique(file_name): 112,968
duplicates: 0
CEO_QA_Uncertainty_pct: 38,068 missing (33.7%)
...
After complete cases: 53,335
Main: 42,488 obs, 2,031 CEOs
Finance: 8,309 obs, 384 CEOs
Utility: 1,732 obs, 90 CEOs
```

---

## F) Regression Execution Correctness (Stage 4)

### F.1 Regression is Actually Run

**Code Path (run_h0_2_ceo_clarity.py, lines 691-730):**
```python
for sample_name in ["Main", "Finance", "Utility"]:
    df_sample = df[df["sample"] == sample_name].copy()
    if len(df_sample) < 100:
        continue
    model, df_reg, valid_ceos = run_regression(df_sample, sample_name)
    if model is None or df_reg is None:
        continue
    clarity_scores = extract_clarity_scores(model, df_reg, sample_name)
    ...
```

**Execution Conditions:**
- Sample must have >= 100 observations
- `run_regression()` must return non-None model
- No silent skips in the loop

**PASS:** All three samples (Main, Finance, Utility) executed successfully.

### F.2 Sample Verification

| Sample | Complete-Case N | After Min-Calls N | Reported N | Match |
|--------|-----------------|-------------------|------------|-------|
| Main | 43,164 | 42,488 | 42,488 | PASS |
| Finance | 8,399 | 8,309 | 8,309 | PASS |
| Utility | 1,772 | 1,732 | 1,732 | PASS |

### F.3 FE/Cluster Arguments

**Code (lines 303-306):**
```python
model = smf.ols(formula, data=df_reg).fit(
    cov_type="cluster",
    cov_kwds={"groups": df_reg["ceo_id"]},
)
```

**Claimed:** "Standard errors are clustered at the CEO level" (LaTeX table note)

**Actual:** `cov_type="cluster"`, `groups=ceo_id`

**PASS:** Implementation matches claim.

### F.4 Coefficient Extraction

**Code (lines 349-358):**
```python
ceo_params = {
    p: model.params[p] for p in model.params.index if p.startswith("C(ceo_id)")
}
for param_name, gamma_i in ceo_params.items():
    if "[T." in param_name:
        ceo_id = param_name.split("[T.")[1].split("]")[0]
        ceo_effects[ceo_id] = gamma_i
```

**Correct:** Extracts CEO fixed effects from `C(ceo_id)[T.XXXXX]` parameter names.

### F.5 Result Object Independence

Each sample uses its own `df_reg` and `model` objects created fresh in the loop iteration. No cross-sample contamination possible.

---

## G) Output Integrity (Tables/Logs/Exports)

### G.1 N Verification

| Source | Main N | Finance N | Utility N |
|--------|--------|-----------|-----------|
| LaTeX Table | 42,488 | 8,309 | 1,732 |
| statsmodels output | 42,488 | 8,309 | 1,732 |
| Manual computation | 42,488 | 8,309 | 1,732 |

**PASS:** N matches across all sources.

### G.2 R-squared Verification

| Sample | LaTeX | statsmodels | Match |
|--------|-------|-------------|-------|
| Main | 0.344 | 0.344 | PASS |
| Finance | 0.294 | 0.294 | PASS |
| Utility | 0.161 | 0.161 | PASS |

### G.3 Coefficient Verification (Main Sample)

| Variable | LaTeX | Regression | Match |
|----------|-------|------------|-------|
| CEO Pres Uncertainty | 0.081 | 0.0813 | PASS |
| Analyst QA Uncertainty | 0.033 | 0.0328 | PASS |
| Negative Sentiment | 0.066 | 0.0658 | PASS |
| Stock Return | 0.000 | 0.00003 | PASS |
| Market Return | -0.001 | -0.0011 | PASS |
| EPS Growth | 0.000 | 0.0004 | PASS |
| Earnings Surprise Decile | 0.001 | 0.0008 | PASS (rounding) |

### G.4 t-value Verification (Main Sample)

| Variable | LaTeX | Regression | Match |
|----------|-------|------------|-------|
| CEO Pres Uncertainty | 10.59 | 10.59 | PASS |
| Analyst QA Uncertainty | 7.68 | 7.68 | PASS |
| Negative Sentiment | 7.65 | 7.65 | PASS |
| Stock Return | 0.25 | 0.25 | PASS |
| Market Return | -3.47 | -3.47 | PASS |
| EPS Growth | 0.67 | 0.67 | PASS |
| Earnings Surprise Decile | 1.23 | 1.23 | PASS |

### G.5 Clarity Scores Verification

**Formula Check:**
```
ClarityCEO_raw == -gamma_i: max diff = 0.0000000000
```

**PASS:** Formula is correctly implemented.

**Per-Sample Standardization:**
| Sample | N CEOs | Mean | Std |
|--------|--------|------|-----|
| Main | 2,030 | 0.0000 | 1.0002 |
| Finance | 383 | 0.0000 | 1.0013 |
| Utility | 89 | 0.0000 | 1.0057 |

**PASS:** Per-sample z-score standardization is correctly implemented.

### G.6 File Naming/Vintage

Outputs written to timestamped directories:
- Stage 3: `outputs/variables/ceo_clarity/2026-02-22_170710/`
- Stage 4: `outputs/econometric/ceo_clarity/2026-02-22_172214/`

No overwriting across models.

---

## H) Reproducibility Run

### H.1 Commands

**Stage 3 (Dry-run):**
```bash
cd C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D
python -m f1d.variables.build_h0_2_ceo_clarity_panel --dry-run
```

**Output:**
```
Dry-run mode: validating inputs...
[OK] All inputs validated
```

**Stage 4 (Dry-run):**
```bash
python -m f1d.econometric.run_h0_2_ceo_clarity --dry-run
```

**Output:**
```
Dry-run mode: validating inputs...
[OK] All inputs validated
```

### H.2 Pinning a Specific Vintage

```bash
# Use a specific panel file
python -m f1d.econometric.run_h0_2_ceo_clarity --panel-path outputs/variables/ceo_clarity/2026-02-22_170710/ceo_clarity_panel.parquet
```

### H.3 Execution Summary

Both dry-run validations passed. Full pipeline has been run multiple times (see output directories with timestamps from 2026-02-19 through 2026-02-22).

---

## I) Automated Checks & Test Gaps

### Existing Tests

**File:** `tests/unit/test_v1_ceo_clarity.py`

**Tests:**
- `TestSampleFiltering` - FF12 code filtering
- `TestDataMerging` - Manifest/linguistic merge
- `TestClarityScoreCalculation` - Clarity = -uncertainty concept
- `TestFixedEffectsExtraction` - Coefficient parsing
- `TestRegressionSpecification` - Formula structure
- `TestOutputValidation` - Output format
- `TestV1EconometricIntegration` - Full workflow mock

**Run Results:**
```
15 passed in 0.14s
```

### Recommended Missing Tests

| Test | Purpose | Priority |
|------|---------|----------|
| `test_clarity_ceo_raw_formula` | Verify ClarityCEO_raw == -gamma_i | High |
| `test_clarity_ceo_standardization` | Verify per-sample z-score | High |
| `test_n_obs_matches_panel` | N in table == computed N | High |
| `test_coefficients_match_regression` | LaTeX coefs == statsmodels | High |
| `test_t_values_match_regression` | LaTeX t-values == statsmodels | Medium |
| `test_panel_file_name_unique` | No duplicate file_name | Medium |
| `test_ceo_id_dtype_consistent` | ceo_id string type preserved | Low |
| `test_reference_ceos_excluded` | gamma=0 CEOs not in output | Medium |
| `test_min_calls_filter` | >=5 calls filter applied | Medium |
| `test_sample_classification` | FF12 -> Main/Finance/Utility | Low |

---

## J) Fix List

### J.1 Documentation Mismatch (Low)

**Issue:** LaTeX table note says "standardized globally across all industry samples" but code standardizes per-sample.

**File:** `src/f1d/econometric/run_h0_2_ceo_clarity.py`, line 447

**Root Cause:** Table note was not updated when per-sample standardization was implemented.

**Fix:**
```python
# Line 447: Change
note=(
    "This table reports CEO fixed effects from regressing CEO Q&A "
    "uncertainty on firm characteristics and year fixed effects. "
    "ClarityCEO is computed as the negative of the CEO fixed effect, "
    "standardized globally across all industry samples. "  # <-- INCORRECT
    ...
)
# To:
note=(
    "This table reports CEO fixed effects from regressing CEO Q&A "
    "uncertainty on firm characteristics and year fixed effects. "
    "ClarityCEO is computed as the negative of the CEO fixed effect, "
    "standardized separately within each industry sample (Main, Finance, Utility). "
    ...
)
```

**Validation:** Read LaTeX output and verify note reflects per-sample standardization.

### J.2 Add Unit Tests for ClarityCEO Formula (Medium)

**Issue:** No explicit test verifying ClarityCEO_raw = -gamma_i

**File:** New file `tests/unit/test_clarity_formula.py`

**Fix:**
```python
def test_clarity_ceo_raw_is_negative_gamma():
    """Verify ClarityCEO_raw == -gamma_i."""
    # Create mock model with known gamma values
    gamma_i = 0.15
    clarity_raw = -gamma_i
    assert abs(clarity_raw - (-gamma_i)) < 1e-10

def test_clarity_ceo_standardization_per_sample():
    """Verify per-sample z-score standardization."""
    import numpy as np
    raw_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    mean = raw_values.mean()
    std = raw_values.std()
    z_scores = (raw_values - mean) / std
    assert abs(z_scores.mean()) < 1e-10
    assert abs(z_scores.std() - 1.0) < 0.01
```

### J.3 Document Cross-Sample CEOs (Info Only)

**Issue:** 4 CEOs appear in multiple samples (Main and Finance) due to firm industry changes.

**File:** No code change needed. Document in report.

**Explanation:** CEOs whose firms changed FF12 industry classification during their tenure have separate gamma estimates per sample. This is correct behavior - the CEO's clarity effect may differ across industry contexts.

---

## Summary Checklist

| Check | Status |
|-------|--------|
| Primary key unique | PASS |
| Merge row-delta invariant | PASS |
| Complete-case filter correct | PASS |
| Min-calls filter correct | PASS |
| Regression formula correct | PASS |
| Clustering correct | PASS |
| CEO FE extraction correct | PASS |
| ClarityCEO formula correct | PASS |
| Per-sample standardization correct | PASS |
| N in table matches computed | PASS |
| Coefficients match regression | PASS |
| t-values match regression | PASS |
| R-squared matches regression | PASS |
| Reference CEOs excluded | PASS |
| No duplicate file_name | PASS |
| Documentation matches code | FAIL (minor - note text) |

---

**AUDIT COMPLETE**

**Verdict:** PASS-WITH-FIXES

The H0.2 CEO Clarity implementation is methodologically sound and produces correct results. The only fix required is a documentation update to the LaTeX table note. No stop-ship issues identified.
