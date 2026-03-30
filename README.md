# F1D: Uncertainty in Language and Corporate Outcomes

Deterministic four-stage pipeline for analyzing how managerial uncertainty language in earnings conference calls affects corporate financial outcomes. The sample covers **112,968 earnings calls** across **2,429 unique firms** from **2002--2018**.

## Pipeline Overview

```
Stage 1 (Sample)       Stage 2 (Text)           Stage 3 (Variables)      Stage 4 (Econometric)
─────────────────  →  ──────────────────────  →  ─────────────────────  →  ──────────────────────
Build master sample    Tokenize transcripts      Build hypothesis-        PanelOLS regressions
manifest from          and compute linguistic    specific panels by       with firm-clustered SEs
earnings call          variables (uncertainty,   merging linguistic,      and Calendar Year /
transcripts + CEO      sentiment, tone) per      financial, and market    Year-Quarter fixed
identification         speaker role              variables per call       effects
```

## Hypothesis Suites

21 estimation suites testing how speech uncertainty maps to corporate outcomes:

| Suite | Dependent Variable | Hypothesis | Tail | Cols | Reference |
|-------|-------------------|------------|------|------|-----------|
| H0.3 | Manager/CEO QA Uncertainty | Extended controls robustness check | two | 4 | -- |
| H1 | CashHoldings, CashHoldings_lead | Higher uncertainty → more precautionary cash | one (+) | 12 | Opler et al. (1999) |
| H1.1 | CashHoldings | Product similarity moderates H1 (continuous z(log(TSIMM))) | mixed | 2 | Hoberg & Phillips (2016) |
| H1.1b | CashHoldings | Product similarity moderates H1 (binary median split) | mixed | 2 | Hoberg & Phillips (2016) |
| H1.2 | CashHoldings | Financial constraint moderates H1 (WW/SA/KZ indices) | mixed | 2 | Whited & Wu (2006) |
| H4 | BookLev / DebtToCapital (+ leads) | Uncertainty and leverage policy | two | 24 | -- |
| H5 | PostCallDispersion | Higher uncertainty → greater analyst disagreement | one (+) | 6 | Druz et al. (2020) |
| H5b | JohnsonDISP2 (+ lead) | Uncertainty → analyst dispersion (Johnson variant) | one (+) | 12 | Johnson (2004) |
| H5b-Wang | WangDISP (+ lead) | Uncertainty → analyst dispersion (Wang variant) | one (+) | 12 | Wang (2020) |
| H7 | delta_amihud | Higher uncertainty → greater illiquidity change | one (+) | 6 | Amihud (2002) |
| H9 | Takeover hazard | Clarity residual and takeover vulnerability | two | -- | Cox PH model |
| H11 | QA/Pres Uncertainty | Political risk (PRiskQ) → more uncertain language | one (+) | 4 | Hassan et al. (2019) |
| H11-Lag | QA/Pres Uncertainty | Lagged political risk (Q-1, Q-2) → uncertainty | one (+) | 8 | Hassan et al. (2019) |
| H11-Lead | QA/Pres Uncertainty | Lead political risk (placebo/falsification) | two | 8 | Hassan et al. (2019) |
| H12 | PayoutRatio_q (+ lead) | Higher uncertainty → lower payout ratio | one (-) | 12 | -- |
| H13 | CapexAt (+ lead) | Uncertainty and capital expenditure | two | 12 | -- |
| H13.1 | CapexAt | Product competition moderates H13 (TSIMM/HHI) | two | 8 | Hoberg & Phillips (2016) |
| H14 | DSPREAD | Higher uncertainty → wider bid-ask spread change | one (+) | 6 | Lee (2016) |
| H16 | RDSales (+ lead) | Uncertainty and R&D investment intensity | two | 12 | Jiang et al. (2021) |
| H17 | RepurchaseIntensity (+ lead) | Uncertainty and share repurchase intensity | two | 12 | -- |
| H18 | CCCL | Higher uncertainty → more SEC comment letters | one (+) | 6 | -- |

**Independent variables** (4 simultaneous IVs per suite):
- `Manager_QA_Uncertainty_pct` — all managers, Q&A section
- `CEO_QA_Uncertainty_pct` — CEO only, Q&A section
- `Manager_Pres_Uncertainty_pct` — all managers, presentation
- `CEO_Pres_Uncertainty_pct` — CEO only, presentation

## Required Inputs

| Directory | Source | Used By |
|-----------|--------|---------|
| `inputs/comp_na_daily_all/` | Compustat North America Daily | CashHoldings, TobinsQ, BookLev, ROA, CapexAt, DividendPayer, OCF_Volatility, PayoutRatio_q, RepurchaseIntensity, RDSales, and more |
| `inputs/CRSP_DSF/` | CRSP Daily Stock File | Amihud illiquidity, bid-ask spreads, stock prices, turnover |
| `inputs/tr_ibes/` | IBES Summary Statistics | Analyst forecast dispersion (H5), earnings surprise |
| `inputs/IBES_Detail/` | IBES Detail History | Individual analyst forecasts for Johnson/Wang dispersion (H5b) |
| `inputs/SDC/` | SDC M&A Database | Takeover indicators (H9) |
| `inputs/TNIC/` | Hoberg-Phillips TNIC3 | Product similarity scores (H1.1, H1.1b, H13.1) |
| `inputs/Hassan_PRisk/` | Hassan et al. PRisk | Firm-level political risk (H11) |
| `inputs/Conference Calls Comment Letters/` | SEC EDGAR | Comment letter receipt dates (H18) |
| `inputs/Earnings_Calls_Transcripts/` | Thomson Reuters | Raw earnings call transcripts |

## Run Commands

### Stage 3: Panel Builders

Each panel builder assembles call-level data by merging linguistic, financial, and market variables.

| Suite | Command |
|-------|---------|
| H0.3 | `python -m f1d.variables.build_h0_3_ceo_clarity_extended_panel` |
| H1 | `python -m f1d.variables.build_h1_cash_holdings_panel` |
| H4 | `python -m f1d.variables.build_h4_leverage_panel` |
| H5 | `python -m f1d.variables.build_h5_dispersion_panel` |
| H5b Johnson | `python -m f1d.variables.build_h5b_johnson_disp_panel` |
| H5b Wang | `python -m f1d.variables.build_h5b_wang_disp_panel` |
| H7 | `python -m f1d.variables.build_h7_illiquidity_panel` |
| H9 | `python -m f1d.variables.build_h9_takeover_panel` |
| H11 | `python -m f1d.variables.build_h11_prisk_uncertainty_panel` |
| H11-Lag | `python -m f1d.variables.build_h11_prisk_uncertainty_lag_panel` |
| H11-Lead | `python -m f1d.variables.build_h11_prisk_uncertainty_lead_panel` |
| H12 | `python -m f1d.variables.build_h12_payout_panel` |
| H13 | `python -m f1d.variables.build_h13_capex_panel` |
| H14 | `python -m f1d.variables.build_h14_bidask_spread_panel` |
| H16 | `python -m f1d.variables.build_h16_rd_sales_panel` |
| H17 | `python -m f1d.variables.build_h17_repurchase_intensity_panel` |
| H18 | `python -m f1d.variables.build_h18_cccl_received_panel` |

### Stage 4: Econometric Runners

Each runner loads its panel, applies sample filters, and runs PanelOLS regressions.

| Suite | Command |
|-------|---------|
| H0.3 | `python -m f1d.econometric.run_h0_3_ceo_clarity_extended` |
| H1 | `python -m f1d.econometric.run_h1_cash_holdings` |
| H1.1 | `python -m f1d.econometric.run_h1_1_cash_tsimm` |
| H1.1b | `python -m f1d.econometric.run_h1_1b_cash_tsimm_binary` |
| H1.2 | `python -m f1d.econometric.run_h1_2_cash_constraint` |
| H4 | `python -m f1d.econometric.run_h4_leverage` |
| H5 | `python -m f1d.econometric.run_h5_dispersion` |
| H5b Johnson | `python -m f1d.econometric.run_h5b_johnson_disp` |
| H5b Wang | `python -m f1d.econometric.run_h5b_wang_disp` |
| H7 | `python -m f1d.econometric.run_h7_illiquidity` |
| H9 | `python -m f1d.econometric.run_h9_takeover_hazards` |
| H11 | `python -m f1d.econometric.run_h11_prisk_uncertainty` |
| H11-Lag | `python -m f1d.econometric.run_h11_prisk_uncertainty_lag` |
| H11-Lead | `python -m f1d.econometric.run_h11_prisk_uncertainty_lead` |
| H12 | `python -m f1d.econometric.run_h12_payout` |
| H13 | `python -m f1d.econometric.run_h13_capex` |
| H13.1 | `python -m f1d.econometric.run_h13_1_competition` |
| H14 | `python -m f1d.econometric.run_h14_bidask_spread` |
| H16 | `python -m f1d.econometric.run_h16_rd_sales` |
| H17 | `python -m f1d.econometric.run_h17_repurchase_intensity` |
| H18 | `python -m f1d.econometric.run_h18_cccl_received` |

All runners support `--dry-run` for validation without execution, and `--year-start` / `--year-end` for subsetting.

### Table Generation

```bash
python outputs/generate_all_tables.py
```

Reads regression outputs from all suites and produces a unified LaTeX document with standardized tables.

## Project Structure

```
src/f1d/
├── sample/                  # Stage 1: Sample assembly
│   ├── build_sample_manifest.py
│   ├── clean_metadata.py
│   ├── link_entities.py
│   ├── build_tenure_map.py
│   └── assemble_manifest.py
├── text/                    # Stage 2: Linguistic analysis
│   ├── tokenize_transcripts.py
│   └── build_linguistic_variables.py
├── variables/               # Stage 3: Panel construction (17 builders)
│   └── build_h{N}_{name}_panel.py
├── econometric/             # Stage 4: Regressions (21 runners)
│   └── run_h{N}_{name}.py
└── shared/                  # Shared infrastructure
    ├── variables/           # 78+ VariableBuilder subclasses
    │   ├── __init__.py      # Central builder registry
    │   ├── _compustat_engine.py
    │   ├── _crsp_engine.py
    │   ├── _ibes_engine.py
    │   ├── _ibes_detail_engine.py
    │   ├── _hassan_engine.py
    │   ├── _linguistic_engine.py
    │   ├── _clarity_residual_engine.py
    │   └── *.py             # Individual builder files
    ├── config/              # YAML configuration loading
    ├── logging/             # Structured logging
    ├── outputs/             # Manifest and attrition table generation
    └── observability/       # Stats, memory, throughput tracking
```

## Econometric Specification

All call-level suites use the same core specification:

- **Estimator**: `linearmodels.PanelOLS` with `EntityEffects` + `TimeEffects`
- **Entity FE**: Firm (`gvkey`) or Industry (`ff12_code`) depending on spec
- **Time FE**: Calendar Year (`cal_yr`) or Calendar Year-Quarter (`cal_yr_qtr`)
- **Standard errors**: Firm-clustered (`cluster_entity=True`)
- **Sample**: Main sample excludes Finance (FF12=8) and Utilities (FF12=11)
- **Controls**: Lagged DV, Size, ROA, TobinsQ, CapexAt, DividendPayer, OCF_Volatility, plus suite-specific extended controls
- **Column layout**: Odd columns use Industry + Year FE; even columns use Firm + Year FE; YQ specs add Year-Quarter FE variants

Exception: H9 uses a Cox proportional hazards model (`lifelines.CoxTimeVaryingFitter`), not PanelOLS.

## Data Architecture

Seven singleton data engines handle all external data loading with thread-safe caching:

| Engine | Source | Key Variables |
|--------|--------|---------------|
| CompustatEngine | Compustat quarterly | CashHoldings, BookLev, ROA, TobinsQ, CapexAt, PayoutRatio_q, RepurchaseIntensity, RDSales |
| CRSPEngine | CRSP daily | Amihud illiquidity, bid-ask spreads, stock price, turnover |
| IbesEngine | IBES summary | Analyst consensus dispersion, earnings surprise |
| IbesDetailEngine | IBES detail | Individual analyst forecasts (Johnson/Wang dispersion) |
| HassanEngine | Hassan et al. | Firm-quarter political risk (PRiskQ) |
| LinguisticEngine | Stage 2 output | Uncertainty, sentiment, tone per speaker role |
| ClarityResidualEngine | Stage 4 output | CEO/Manager clarity residuals (from H0.3) |

Each engine loads data once per session and caches the result. Variable builders request data from engines and apply per-variable transformations.
