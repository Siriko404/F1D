# F1D — CEO Communication Clarity Pipeline

Econometric pipeline for the thesis *"CEO Communication Clarity as a Persistent Trait"*.
Processes 112,968 earnings call observations (2002–2018) to estimate CEO-level fixed
effects in linguistic uncertainty, then runs robustness analyses by industry sample,
extended controls, and economic regime.

---

## Install

```bash
pip install -e .
pip install -r requirements.txt
```

The editable install is required for all `from f1d.*` imports to resolve. Without it,
every script raises `ModuleNotFoundError: No module named 'f1d'`.

---

## Architecture

The pipeline enforces two strict structural rules:

**One module = one variable.** Each shared variable builder in
`src/f1d/shared/variables/` returns exactly one column merged onto the manifest by
`file_name`. No builder returns multiple columns.

**Two-stage execution.** Every hypothesis test is split across exactly two scripts:

```
Stage 3 — Panel builder   (src/f1d/variables/build_<name>_panel.py)
    Loads manifest + shared variable builders → merges into one .parquet panel

Stage 4 — Hypothesis test (src/f1d/econometric/test_<name>.py)
    Loads the panel → filters → OLS with fixed effects → LaTeX table + scores .parquet
```

**Private engines for expensive loads.** `_compustat_engine.py` and `_crsp_engine.py`
are module-level singletons. Panel builders call `get_engine()` once; all individual
builders share the cached result so Compustat and CRSP are each read only once per
panel build.

---

## Prerequisites

The following upstream outputs must exist before running Stage 3/4. These are assumed
complete and are not re-documented here.

| Required path | Produced by |
|---------------|-------------|
| `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet` | Step 1.4 — `f1d.sample.assemble_manifest` |
| `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet` | Step 2.2 — `f1d.text.build_linguistic_variables` |
| `inputs/comp_na_daily_all/comp_na_daily_all.parquet` | Compustat raw (provided) |
| `inputs/CRSP_DSF/CRSP_DSF_{year}_Q{1-4}.parquet` | CRSP daily stock files (provided) |
| `inputs/tr_ibes/tr_ibes.parquet` | IBES EPS forecasts (provided) |
| `inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet` | CCM linktable (provided) |

---

## Running the Pipeline

Run in this exact order. Each Stage 4 script reads the panel written by its Stage 3
counterpart.

```bash
# Stage 3 — build panels (each ~5–6 minutes)
python -m f1d.variables.build_manager_clarity_panel
python -m f1d.variables.build_ceo_clarity_panel
python -m f1d.variables.build_ceo_clarity_extended_panel
python -m f1d.variables.build_ceo_tone_panel
python -m f1d.variables.build_liquidity_panel
python -m f1d.variables.build_takeover_panel

# Stage 4 — run hypothesis tests
python -m f1d.econometric.test_manager_clarity          # ~1 min
python -m f1d.econometric.test_ceo_clarity              # ~30 s
python -m f1d.econometric.test_ceo_clarity_extended     # ~3 min
python -m f1d.econometric.test_ceo_clarity_regime       # ~20 s
python -m f1d.econometric.test_ceo_tone                 # ~3 min
python -m f1d.econometric.test_liquidity                # ~2 min
python -m f1d.econometric.test_takeover_hazards         # ~1 min
python -m f1d.econometric.generate_summary_stats        # ~1 s (no Stage 3 needed)
```

All outputs are written to timestamped subdirectories under `outputs/`.
`get_latest_output_dir()` always resolves to the most recent run — no symlinks needed.

---

## Verified Results

Last full pipeline run: **2026-02-19**. All scripts passed end-to-end with zero errors,
zero row-delta on every panel merge, and all post-run checks passing.

### Manager Clarity (4.1) — `test_manager_clarity`

Dependent variable: `Manager_QA_Uncertainty_pct`

| Sample | N Obs | N Managers | R² |
|--------|------:|----------:|----:|
| Main (FF12 non-fin, non-util) | 57,796 | 2,605 | 0.407 |
| Finance (FF12 = 11) | 13,409 | 577 | 0.305 |
| Utility (FF12 = 8) | 2,974 | 136 | 0.216 |

`ClarityManager = −gamma_i`, standardized globally across all three samples.

### CEO Clarity (4.1.1) — `test_ceo_clarity`

Dependent variable: `CEO_QA_Uncertainty_pct`

| Sample | N Obs | N CEOs | R² |
|--------|------:|-------:|----:|
| Main | 42,488 | 2,031 | 0.344 |
| Finance | 8,309 | 384 | 0.294 |
| Utility | 1,732 | 90 | 0.161 |

`ClarityCEO = −gamma_i`, standardized globally across all three samples.

### Extended Controls Robustness (4.1.2) — `test_ceo_clarity_extended`

Main sample only. Extended controls: `CurrentRatio`, `RD_Intensity`, `Volatility`.

| Model | N Obs | N Entities | R² |
|-------|------:|-----------:|----:|
| Manager Baseline | 57,796 | 2,605 | 0.407 |
| Manager Extended | 56,404 | 2,554 | 0.409 |
| CEO Baseline | 42,488 | 2,031 | 0.344 |
| CEO Extended | 41,386 | 1,991 | 0.344 |

Extended models have fewer observations due to additional missingness in
`CurrentRatio` (83.3% coverage) and `Volatility` (93.3% coverage).
R² increases by ≤ 0.002 — CEO fixed effects are robust to extended controls.

### Regime Analysis (4.1.3) — `test_ceo_clarity_regime`

Main sample only. Same model specification as CEO Clarity (4.1.1).

| Regime | Years | N Obs | N CEOs | R² |
|--------|-------|------:|-------:|----:|
| Pre-Crisis | 2002–2007 | 9,864 | 832 | 0.347 |
| Crisis | 2008–2009 | 5,153 | 706 | 0.440 |
| Post-Crisis | 2010–2018 | 26,215 | 1,529 | 0.354 |

`ClarityCEO` standardized **within each regime separately** (not globally). Each
regime's regression is anchored to a different reference CEO, so pooling raw `gamma_i`
values across regimes conflates reference-level artifacts with real regime differences.
Spearman rank correlations for CEOs appearing in multiple regimes: Pre/Crisis ρ = 0.664,
Crisis/Post ρ = 0.735, Pre/Post ρ = 0.706 — confirming clarity is a stable trait.

### CEO Tone (4.1.4) — `test_ceo_tone`

Dependent variable: `Entire_All_Negative_pct` (net negative sentiment, all speakers).
Three models: ToneAll (all-manager FE), ToneCEO (CEO FE), ToneRegime (CEO × regime FE).

| Model | Sample | N Obs | N CEOs | R² |
|-------|--------|------:|-------:|----:|
| ToneAll | Main | 57,796 | 2,605 | 0.452 |
| ToneAll | Finance | 13,409 | 577 | 0.511 |
| ToneAll | Utility | 2,974 | 136 | 0.350 |
| ToneCEO | Main | 42,488 | 2,031 | 0.277 |
| ToneCEO | Finance | 8,309 | 384 | 0.354 |
| ToneCEO | Utility | 1,732 | 90 | 0.109 |
| ToneRegime | Main | 56,709 | 2,592 | 0.167 |
| ToneRegime | Finance | 13,242 | 576 | 0.345 |
| ToneRegime | Utility | 2,939 | 136 | 0.125 |

### Liquidity Regressions (4.2) — `test_liquidity`

Dependent variables: `Delta_Amihud` and `Delta_Corwin_Schultz` (changes in illiquidity).
OLS and 2SLS (instrument: CCCL `shift_intensity_sale_ff48`). Sample: 2005–2011.
First-stage KP F-statistics: 696–1,230 (strong instrument).

| Phase | Model | DV | N Obs | R² | Clarity coef | p |
|-------|-------|----|------:|---:|-------------:|--:|
| OLS | Regime | Delta_Amihud | 54,978 | 0.001 | 0.012 | 0.156 |
| OLS | Regime | Delta_Corwin_Schultz | 55,060 | 0.075 | 0.001 | 0.011 |
| OLS | CEO | Delta_Amihud | 40,240 | 0.001 | 0.003 | 0.851 |
| OLS | CEO | Delta_Corwin_Schultz | 40,286 | 0.073 | 0.001 | 0.006 |
| 2SLS | Regime | Delta_Amihud | 50,422 | — | −0.862 | 0.525 |
| 2SLS | Regime | Delta_Corwin_Schultz | 50,498 | — | −0.019 | 0.235 |
| 2SLS | CEO | Delta_Amihud | 37,150 | — | 139.917 | 0.987 |
| 2SLS | CEO | Delta_Corwin_Schultz | 37,189 | — | −0.127 | 0.963 |

2SLS results are imprecise for Amihud (low annual frequency coverage); Corwin-Schultz
coefficients are more stable. CCCL instrument coverage: 85.6% of OLS sample.

### Takeover Hazards (4.3) — `test_takeover_hazards`

Survival panel: firm-level (not call-level). Duration = years from first call to
takeover announcement / end of sample (2002–2018). Six Cox PH models.

| Model | Variant | Event type | N Firms | N Events | Concordance |
|-------|---------|-----------|--------:|---------:|------------:|
| Cox PH All | Regime | All bids | 1,575 | 500 | 0.601 |
| Cox PH All | CEO | All bids | 1,354 | 439 | 0.611 |
| Cox CS Uninvited | Regime | Hostile/unsolicited | 1,575 | 65 | 0.651 |
| Cox CS Uninvited | CEO | Hostile/unsolicited | 1,354 | 59 | 0.644 |
| Cox CS Friendly | Regime | Friendly | 1,575 | 409 | 0.631 |
| Cox CS Friendly | CEO | Friendly | 1,354 | 358 | 0.635 |

SDC linkage: manifest CUSIP (9-char) → SDC target CUSIP via first 6 chars.
Cause-specific Cox PH used in place of Fine-Gray (not available in lifelines).

### Summary Statistics (4.4) — `generate_summary_stats`

Main sample: 88,205 call observations, 1,884 firms, 3,533 CEOs, 2002–2018.
No Stage 3 panel builder — reads `ceo_clarity_extended_panel.parquet` directly.

| Panel | Variables | N range |
|-------|-----------|---------|
| A — Linguistic | 6 (uncertainty + sentiment pct) | 60,435–84,567 |
| B — Financial controls | 11 (Size, BM, Lev, ROA, …) | 67,965–87,994 |

---

## Output Layout

```
outputs/
├── variables/
│   ├── manager_clarity/{timestamp}/
│   │   ├── manager_clarity_panel.parquet       # 112,968 rows, 17 cols
│   │   ├── summary_stats.csv
│   │   └── report_step3_manager_clarity.md
│   ├── ceo_clarity/{timestamp}/
│   │   ├── ceo_clarity_panel.parquet           # 112,968 rows, 17 cols
│   │   └── ...
│   ├── ceo_clarity_extended/{timestamp}/
│   │   ├── ceo_clarity_extended_panel.parquet  # 112,968 rows, 26 cols
│   │   └── ...
│   ├── ceo_tone/{timestamp}/
│   │   ├── ceo_tone_panel.parquet              # 112,968 rows
│   │   └── ...
│   ├── liquidity/{timestamp}/
│   │   ├── liquidity_panel.parquet             # 112,968 rows, 32 cols
│   │   └── ...
│   └── takeover/{timestamp}/
│       ├── takeover_panel.parquet              # 2,429 rows (firm-level), 29 cols
│       └── ...
└── econometric/
    ├── manager_clarity/{timestamp}/
    │   ├── clarity_scores.parquet              # 3,315 estimated managers
    │   ├── manager_clarity_table.tex
    │   └── regression_results_{main,finance,utility}.txt
    ├── ceo_clarity/{timestamp}/
    │   ├── clarity_scores.parquet              # 2,502 estimated CEOs
    │   ├── ceo_clarity_table.tex
    │   └── regression_results_{main,finance,utility}.txt
    ├── ceo_clarity_extended/{timestamp}/
    │   ├── ceo_clarity_extended_table.tex      # 4-column table
    │   └── regression_results_{model}.txt      # 4 files
    ├── ceo_clarity_regime/{timestamp}/
    │   ├── clarity_scores.parquet              # 3,064 CEO-regime rows
    │   ├── ceo_clarity_regime_table.tex        # 3-column table
    │   └── regression_results_{regime}.txt     # 3 files
    ├── ceo_tone/{timestamp}/
    │   ├── model_diagnostics.csv               # 9 model×sample rows
    │   ├── ceo_tone_table.tex
    │   └── regression_results_{model}_{sample}.txt
    ├── liquidity/{timestamp}/
    │   ├── model_diagnostics.csv               # 10 phase×model×DV rows
    │   ├── liquidity_table.tex
    │   └── regression_results_{phase}_{model}_{dv}.txt
    ├── takeover/{timestamp}/
    │   ├── model_diagnostics.csv               # 6 model rows
    │   ├── takeover_table.tex
    │   └── regression_results_{model}_{variant}.txt
    └── summary_stats/{timestamp}/
        ├── descriptive_statistics.csv          # 17 variables
        ├── correlation_matrix.csv              # 11×11
        ├── panel_balance.csv                   # 17 years
        ├── firm_year_summary.csv
        ├── summary_table.tex
        └── report_step4_4.md
```

`clarity_scores.parquet` columns by output:

| Output | Key columns |
|--------|-------------|
| `manager_clarity` | `ceo_id`, `ceo_name`, `sample`, `gamma_i`, `ClarityManager_raw`, `ClarityManager`, `n_calls` |
| `ceo_clarity` | `ceo_id`, `ceo_name`, `sample`, `gamma_i`, `ClarityCEO_raw`, `ClarityCEO`, `n_calls` |
| `ceo_clarity_regime` | `ceo_id`, `ceo_name`, `regime`, `gamma_i`, `ClarityCEO_raw`, `ClarityCEO`, `n_calls_regime` |

Reference entities (one per regression, statsmodels normalization artifact) are always
excluded from output parquets.

---

## Shared Variable Builders

All live in `src/f1d/shared/variables/`. Each returns one column, merged by `file_name`.

### Private engines (module-level singletons, not builders)

| Module | Raw input | Columns computed |
|--------|-----------|-----------------|
| `_compustat_engine.py` | `inputs/comp_na_daily_all/comp_na_daily_all.parquet` | `Size`, `BM`, `Lev`, `ROA`, `CurrentRatio`, `RD_Intensity`, `EPS_Growth` |
| `_crsp_engine.py` | `inputs/CRSP_DSF/CRSP_DSF_{year}_Q{1-4}.parquet` + CCM | `StockRet`, `MarketRet`, `Volatility` |

### Individual builders (one column each)

| Builder module | Column | Engine |
|----------------|--------|--------|
| `size.py` | `Size` | Compustat |
| `bm.py` | `BM` | Compustat |
| `lev.py` | `Lev` | Compustat |
| `roa.py` | `ROA` | Compustat |
| `current_ratio.py` | `CurrentRatio` | Compustat |
| `rd_intensity.py` | `RD_Intensity` | Compustat |
| `eps_growth.py` | `EPS_Growth` | Compustat |
| `stock_return.py` | `StockRet` | CRSP |
| `market_return.py` | `MarketRet` | CRSP |
| `volatility.py` | `Volatility` | CRSP |
| `earnings_surprise.py` | `SurpDec` | IBES + CCM direct |
| `manager_qa_uncertainty.py` | `Manager_QA_Uncertainty_pct` | Stage 2 linguistic vars |
| `manager_pres_uncertainty.py` | `Manager_Pres_Uncertainty_pct` | Stage 2 linguistic vars |
| `ceo_qa_uncertainty.py` | `CEO_QA_Uncertainty_pct` | Stage 2 linguistic vars |
| `ceo_pres_uncertainty.py` | `CEO_Pres_Uncertainty_pct` | Stage 2 linguistic vars |
| `analyst_qa_uncertainty.py` | `Analyst_QA_Uncertainty_pct` | Stage 2 linguistic vars |
| `negative_sentiment.py` | `Entire_All_Negative_pct` | Stage 2 linguistic vars |
| `cccl_instrument.py` | `shift_intensity_sale_ff48` | `inputs/CCCL_instrument/` (firm-year level; merge key `gvkey+year`) |
| `takeover_indicator.py` | `Takeover`, `Takeover_Uninvited`, `Takeover_Friendly` | `inputs/SDC/sdc-ma-merged.parquet` (firm-level; merge key `gvkey`) |

**CUSIP join note.** IBES uses 8-char alphanumeric CUSIPs (e.g. `'87482X10'`); CCM
uses 9-char numeric CUSIPs (e.g. `'000032102'`). The join is `ibes[:8] == ccm[:8]`.
Do NOT zero-fill the IBES side — it corrupts alphanumeric CUSIPs.

---

## Architecture Rules

These constraints are enforced on every new script pair before it is committed.

| Rule | How enforced |
|------|-------------|
| One module = one column | Code review; builders may not return > 1 column |
| Zero row delta on every merge | `ValueError` raised if `len(df)` changes after any merge in a panel builder |
| Hard-fail on missing required variables | Stage 4 scripts `raise ValueError` listing missing variables — no silent fallback |
| Reference entity excluded from output parquet | `is_reference=True` rows filtered out before writing `clarity_scores.parquet` |
| Global standardization for industry-split models | `ClarityManager` / `ClarityCEO` z-scored across all samples combined |
| Per-regime standardization for regime-split models | `ClarityCEO` z-scored within each regime (different reference CEOs, incompatible raw scales) |
| Full formula logged | No `[:80]` truncation on formula string in any Stage 4 script |
| LaTeX entity label correct per model | `"N Managers"` for manager models, `"N CEOs"` for CEO models |

Canonical reference implementation:
`src/f1d/variables/build_manager_clarity_panel.py` +
`src/f1d/econometric/test_manager_clarity.py`.
All new script pairs must match their structure exactly.

Full architecture documentation and bug history: `docs/plans/refactor-master-plan.md`.

---

## Phase B — Completion Status

All six items are complete. The full pipeline (B.1–B.6) is verified end-to-end.

| Item | Description | Status |
|------|-------------|--------|
| B.1 Extended Controls (4.1.2) | 4-model robustness table | **Done** |
| B.2 Regime Analysis (4.1.3) | 3-regime split of CEO Clarity | **Done** |
| B.3 CEO Tone (4.1.4) | New DV: net sentiment. 3 new builders + new Stage 3 panel. | **Done** |
| B.4 Liquidity Regressions (4.2) | OLS + 2SLS with CCCL instrument. `linearmodels`. | **Done** |
| B.5 Takeover Hazards (4.3) | Cox PH (cause-specific). `lifelines`. SDC M&A data. | **Done** |
| B.6 Summary Statistics (4.4) | Publication-quality summary stats table + LaTeX. | **Done** |

---

## Legacy Code

The following subdirectories are **superseded** and kept for reference only.
Do not run them in a production context.

| Path | Contents | Status |
|------|----------|--------|
| `src/f1d/econometric/v1/` | 8 original v1 econometric scripts | Superseded — reference for B.3–B.6 spec |
| `src/f1d/econometric/v2/` | 11 earlier-refactor hypothesis scripts | Superseded |
| `src/f1d/financial/v2/` | v2 financial feature scripts | Superseded |
| `_archive/` | Full v5.1 legacy archive | Historical record |

`v1/` and `v2/` scripts use `load_all_data()` from the old shared infrastructure,
write to different output directories, and do not enforce the one-module-one-variable
constraint.
