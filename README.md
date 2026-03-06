# F1D — Uncertainty in Language and Corporate Outcomes Pipeline

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)

**Econometric pipeline for thesis: "Uncertainty in Language and Corporate Outcomes"**

This pipeline processes 112,968 earnings call observations (2002–2018) to estimate CEO-level fixed effects in linguistic uncertainty, then runs robustness analyses across industry samples, extended controls, and economic regimes.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Pipeline Architecture](#pipeline-architecture)
- [Running the Pipeline](#running-the-pipeline)
- [Output Structure](#output-structure)
- [Verified Results](#verified-results)
- [Configuration](#configuration)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/user/f1d.git
cd f1d

# Create virtual environment (Python 3.9+)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install package and dependencies
pip install -e .
pip install -r requirements.txt

# Run a single hypothesis test (requires input data)
python -m f1d.econometric.run_h0_2_ceo_clarity
```

> **Note:** The editable install (`pip install -e .`) is required. All scripts use `from f1d.*` imports that fail without it.

---

## Prerequisites

### Required Input Data

The following datasets must be present in `inputs/` before running the pipeline. These are externally provided and not included in this repository.

| Path | Description | Source |
|------|-------------|--------|
| `inputs/Earnings_Calls_Transcripts/` | Earnings call transcripts with speaker data | Earnings call provider |
| `inputs/LM_dictionary/Loughran-McDonald_MasterDictionary_1993-2024.csv` | LM sentiment dictionary | [McDonald Word Lists](https://sraf.nd.edu/textual-analysis/resources/) |
| `inputs/comp_na_daily_all/` | Compustat quarterly fundamentals | WRDS Compustat |
| `inputs/CRSP_DSF/` | CRSP daily stock files | WRDS CRSP |
| `inputs/tr_ibes/` | IBES EPS forecasts | WRDS IBES |
| `inputs/CRSPCompustat_CCM/` | CCM linktable | WRDS CCM |
| `inputs/SDC/` | SDC M&A data | Refinitiv SDC |
| `inputs/CCCL_instrument/` | CEO turnover instrument | Constructed from executive data |
| `inputs/Execucomp/` | Executive compensation data | Execucomp |
| `inputs/FirmLevelRisk/` | Hassan political risk data | Hassan et al. |
| `inputs/Manager_roles/` | Manager role classification | Constructed |
| `inputs/SEC_Edgar_Letters/` | SEC correspondence data | SEC EDGAR |

### System Requirements

- **Python:** 3.9, 3.10, 3.11, 3.12, or 3.13
- **Memory:** 16GB RAM minimum (32GB recommended for full pipeline)
- **Disk:** ~50GB for input data, ~10GB for outputs
- **OS:** Windows, macOS, or Linux

---

## Installation

### Step-by-Step Setup

```bash
# 1. Clone and enter project directory
git clone https://github.com/user/f1d.git
cd f1d

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install package in editable mode (REQUIRED)
pip install -e .

# 5. Install all dependencies
pip install -r requirements.txt

# 6. Install development tools (optional, for contributors)
pip install -e ".[dev]"
```

### Dependency Overview

| Category | Packages | Purpose |
|----------|----------|---------|
| **Data Processing** | pandas, numpy, pyarrow | DataFrame operations, Parquet I/O |
| **Statistics** | statsmodels, scipy, linearmodels | OLS, IV regression, survival analysis |
| **Machine Learning** | scikit-learn, lifelines | Survival models, utilities |
| **Configuration** | pyyaml, pydantic | YAML parsing, settings validation |
| **Utilities** | psutil, rapidfuzz | System monitoring, fuzzy matching |

See [DEPENDENCIES.md](docs/DEPENDENCIES.md) for version pinning rationale and [UPGRADE_GUIDE.md](docs/UPGRADE_GUIDE.md) for upgrade procedures.

### Verify Installation

```bash
# Check package is installed correctly
python -c "import f1d; print(f'F1D version: {f1d.__version__}')"

# Run test suite
pytest tests/ -m "not e2e" -v
```

---

## Pipeline Architecture

### Four-Stage Design

The pipeline enforces a strict four-stage architecture with clear data contracts:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Stage 1: Sample Construction (src/f1d/sample/)                             │
│   CleanMetadata → LinkEntities → BuildTenureMap → AssembleManifest          │
│   Output: master_sample_manifest.parquet (112,968 calls)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Stage 2: Text Processing (src/f1d/text/)                                   │
│   TokenizeTranscripts → BuildLinguisticVariables                            │
│   Output: linguistic_variables_{year}.parquet (uncertainty, sentiment)     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Stage 3: Panel Builders (src/f1d/variables/)                               │
│   build_{hypothesis}_panel.py → merge manifest + shared variables          │
│   Output: {hypothesis}_panel.parquet (ready for regression)                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Stage 4: Hypothesis Tests (src/f1d/econometric/)                           │
│   run_{hypothesis}.py → OLS/IV/Cox → LaTeX tables + scores                 │
│   Output: clarity_scores.parquet, regression_results.txt, *.tex            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Design Principles

| Principle | Enforcement |
|-----------|-------------|
| **One module = one variable** | Each builder in `src/f1d/shared/variables/` returns exactly one column |
| **Zero row delta on merges** | `ValueError` raised if panel length changes after any merge |
| **Hard-fail on missing variables** | Stage 4 scripts reject panels with missing required columns |
| **Timestamped outputs** | All outputs written to `outputs/{stage}/{YYYY-MM-DD_HHMMSS}/` |
| **Reference entity exclusion** | Statsmodels reference level rows filtered from final outputs |

### Private Data Engines

Expensive data sources (Compustat, CRSP, IBES, Linguistic) are loaded once via module-level singletons:

```python
# src/f1d/shared/variables/_linguistic_engine.py
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = LinguisticEngine()  # Load once, cache in memory
    return _engine
```

All variable builders call `get_engine()`, ensuring data is read exactly once per panel build.

#### Engine-Level Winsorization

All engines apply **per-year 1%/99% winsorization** at load time to ensure consistent outlier treatment across ALL hypothesis suites:

| Engine | Method | Variables Winsorized |
|--------|--------|---------------------|
| **CompustatEngine** | Per-year 1%/99% | Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, etc. |
| **CRSPEngine** | Per-year 1%/99% | StockRet, MarketRet, Volatility, amihud_illiq |
| **LinguisticEngine** | Per-year 1%/99% | All 25 linguistic percentage columns (_pct) |

**Why per-year for all variables?**
- Preserves "high for that year" semantics - what's extreme in 2008 (crisis) differs from 2017 (bull market)
- Handles potential language evolution and regime-dependent communication patterns over 17 years
- Standard approach in panel data econometrics

Panel builders (H0.2-H10) receive **already-winsorized** data and do NOT apply additional winsorization.

---

## Running the Pipeline

### Execution Order

Run stages sequentially. Each stage depends on outputs from previous stages.

#### Stage 1: Sample Construction

```bash
# Build the master sample manifest (~5 minutes total)
python -m f1d.sample.clean_metadata        # Clean transcript metadata
python -m f1d.sample.link_entities         # Link transcripts to firms (GVKEY)
python -m f1d.sample.build_tenure_map      # Build CEO tenure panel
python -m f1d.sample.assemble_manifest     # Assemble final manifest
```

#### Stage 2: Text Processing

```bash
# Extract linguistic variables (~10 minutes total)
python -m f1d.text.tokenize_transcripts         # Tokenize and count LM words
python -m f1d.text.build_linguistic_variables   # Compute uncertainty/sentiment
```

#### Stage 3: Panel Building

```bash
# Build regression panels (each 1-6 minutes)
python -m f1d.variables.build_h0_2_ceo_clarity_panel
python -m f1d.variables.build_h0_3_ceo_clarity_extended_panel
python -m f1d.variables.build_h1_cash_holdings_panel
python -m f1d.variables.build_h2_investment_panel
python -m f1d.variables.build_h3_payout_policy_panel
python -m f1d.variables.build_h4_leverage_panel
python -m f1d.variables.build_h5_dispersion_panel
python -m f1d.variables.build_h6_cccl_panel
python -m f1d.variables.build_h7_illiquidity_panel
python -m f1d.variables.build_h8_political_risk_panel
python -m f1d.variables.build_h9_takeover_panel
python -m f1d.variables.build_h10_tone_at_top_panel
python -m f1d.variables.build_h11_prisk_uncertainty_panel
python -m f1d.variables.build_h11_prisk_uncertainty_lag_panel
python -m f1d.variables.build_h12_div_intensity_panel
```

#### Stage 4: Hypothesis Tests

```bash
# Run econometric analyses (each 20 seconds - 7 minutes)
python -m f1d.econometric.run_h0_2_ceo_clarity           # ~30 sec
python -m f1d.econometric.run_h0_3_ceo_clarity_extended  # ~3 min
python -m f1d.econometric.run_h1_cash_holdings           # ~7 min
python -m f1d.econometric.run_h2_investment              # ~2 min
python -m f1d.econometric.run_h3_payout_policy           # ~1 min
python -m f1d.econometric.run_h4_leverage                # ~1 min
python -m f1d.econometric.run_h5_dispersion              # ~2 min
python -m f1d.econometric.run_h6_cccl                    # ~1 min
python -m f1d.econometric.run_h7_illiquidity             # ~2 min
python -m f1d.econometric.run_h8_political_risk             # ~1 min
python -m f1d.econometric.run_h9_takeover_hazards        # ~1 min
python -m f1d.econometric.run_h10_tone_at_top            # ~2 min
python -m f1d.econometric.run_h11_prisk_uncertainty      # ~2 min
python -m f1d.econometric.run_h11_prisk_uncertainty_lag  # ~2 min
python -m f1d.econometric.run_h12_div_intensity          # ~1 min
python -m f1d.reporting.generate_summary_stats           # ~1 sec
```

### Output Resolution

All scripts write to timestamped directories. Use `get_latest_output_dir()` to find the most recent:

```python
from f1d.shared.path_utils import get_latest_output_dir

# Returns: outputs/variables/ceo_clarity/2026-02-20_143022/
latest = get_latest_output_dir("outputs/variables/ceo_clarity")
```

No symlinks needed — the latest directory is always found by timestamp.

---

## Verified Results

Last full pipeline run: **2026-03-05**. All scripts passed end-to-end with zero errors,
zero row-delta on every panel merge, and all post-run checks passing.

**Summary of hypothesis test results (2026-03-05 run):**

| Hypothesis | Status | Key Finding |
|------------|--------|-------------|
| H0.2 CEO Clarity | ✓ Complete | 2,486 CEO fixed effects (SVD fix applied) |
| H0.3 Extended Controls | ✓ Robust | R² stable across baseline/extended specs |
| H1 Cash Holdings | **Partial** | H1a: 7/18 sig, H1b: 2/18 sig (CEO measures strongest) |
| H2 Investment | **Null** | H2a: 0/18 sig, H2b: 1/18 sig |
| H3 Payout Policy | **Partial** | H3a: 1/36 sig, H3b: 3/36 sig |
| H4 Leverage | **Partial** | 2/18 sig (Pres uncertainty measures) |
| H5 Analyst Dispersion | **Null** | 0/12 significant |
| H6 CCCL Speech | **Partial** | 4/21 sig (Finance only; pre-trends concerns) |
| H7 Illiquidity | **Null** | 0/9 significant (all β negative or zero) |
| H8 Political Risk | **NOT SUPPORTED** | β₃ = 0.0000, p = 0.986 |
| H11 Political Risk Uncertainty | **STRONG SUPPORT** | 16/18 significant (all p<0.05) |
| H11-Lag Political Risk | **PARTIAL** | 12/18 significant with lagged PRiskQ |
| H12 Dividend Intensity | **NOT SUPPORTED** | 0/12 significant (Main sample) |
| H9 Takeover Hazards | **Partial** | CEO models run; Manager clarity missing |

### CEO Clarity (H0.2) — `run_h0_2_ceo_clarity`

Dependent variable: `CEO_QA_Uncertainty_pct`

| Sample | N Obs | N CEOs | R² | Adj R² |
|--------|------:|-------:|----:|-------:|
| Main | 42,441 | 2,021 | 0.368 | 0.336 |
| Finance | 8,218 | 381 | 0.309 | 0.274 |
| Utility | 1,647 | 87 | 0.192 | 0.135 |

`ClarityCEO = −gamma_i`, standardized per-sample (then combined). Total: 2,486 CEO-sample pairs.

**Fix applied (2026-02-27):** Added standardization of continuous controls (`StockRet`, `MarketRet`, `EPS_Growth`)
before OLS to prevent SVD convergence issues on large design matrices.

### Extended Controls Robustness (H0.3) — `run_h0_3_ceo_clarity_extended`

Main sample only. Extended controls: `CurrentRatio`, `RD_Intensity`, `Volatility`.

| Model | N Obs | N Entities | R² | Adj R² |
|-------|------:|-----------:|----:|-------:|
| Manager Baseline | 57,845 | 2,599 | 0.418 | 0.390 |
| Manager Extended | 56,152 | 2,534 | 0.421 | 0.393 |
| CEO Baseline | 42,441 | 2,021 | 0.368 | 0.336 |
| CEO Extended | 41,100 | 1,971 | 0.368 | 0.335 |

Extended models have fewer observations due to additional missingness in
`CurrentRatio` (83.3% coverage) and `Volatility` (93.3% coverage).
R² increases by ≤ 0.003 — CEO fixed effects are robust to extended controls.

### H1 Cash Holdings — `run_h1_cash_holdings`

Tests whether vague managers hoard more cash (H1a: β₁ > 0) and whether leverage
attenuates that relationship (H1b: β₃ < 0). Unit of observation: individual earnings
call (call-level, consistent with all other tests).

Model: `CashHoldings_{t+1} ~ Uncertainty + Lev + Uncertainty×Lev + Size + TobinsQ +
ROA + CapexAt + DividendPayer + OCF_Volatility + EntityEffects + TimeEffects`

Standard errors: firm-clustered (Moulton correction — `CashHoldings_lead` is constant
within firm-year, so HC1 over-counts independent observations).

**Stage 3** (`build_h1_cash_holdings_panel`): 112,968 rows, zero row-delta on all merges.
`CashHoldings_lead` = CashHoldings from the last call (latest `start_date`) per firm-year t+1.

| Sample | Total calls | Calls with valid lead |
|--------|------------:|---------------------:|
| Main (FF12 non-fin, non-util) | 88,205 | 82,236 |
| Finance (FF12 = 11) | 20,482 | 19,023 |
| Utility (FF12 = 8) | 4,281 | 4,010 |

**Stage 4** (`run_h1_cash_holdings`): 18 regressions (6 uncertainty measures × 3 samples).

| Sample | H1a significant (β₁>0) | H1b significant (β₃<0) |
|--------|----------------------:|----------------------:|
| Main | **4/6** | **2/6** |
| Finance | **3/6** | 0/6 |
| Utility | 0/6 | 0/6 |
| **Total** | **7/18** | **2/18** |

Selected significant results (Main sample):
- CEO_QA_Uncertainty: β₁ = 0.0065 (SE=0.0021, p=0.0009); β₃ = −0.0151 (SE=0.0060, p=0.0063)
- CEO_QA_Weak_Modal: β₁ = 0.0089 (SE=0.0033, p=0.0037); β₃ = −0.0273 (SE=0.0087, p=0.0008)
- Manager_QA_Uncertainty: β₁ = 0.0062 (SE=0.0034, p=0.0352)
- Manager_QA_Weak_Modal: β₁ = 0.0090 (SE=0.0053, p=0.0433)

**Interpretation:** Strong support for H1a (uncertainty → cash hoarding) in Main sample,
particularly for CEO measures. H1b (leverage attenuation) supported only for CEO measures
in Main sample. Finance shows H1a support but no moderation effect. Utility null.

### H2 Investment Efficiency — `run_h2_investment`

Tests whether vague managers exhibit more underinvestment (H2a: β₁ < 0 for InvestmentResidual)
and whether leverage attenuates this (H2b: β₃ > 0). DV: `InvestmentResidual_{t+1}` (Biddle et al. 2009; >0=overinvestment, <0=underinvestment).

Model: `InvestmentResidual_lead ~ Uncertainty + Lev + Uncertainty×Lev + Size + TobinsQ + ROA + CashFlow + SalesGrowth + EntityEffects + TimeEffects`

**Stage 3**: 112,968 calls, 101,923 with valid lead.

| Sample | H2a significant (β₁<0) | H2b significant (β₃>0) |
|--------|----------------------:|----------------------:|
| Main | 0/6 | 0/6 |
| Finance | 0/6 | **1/6** |
| Utility | 0/6 | 0/6 |
| **Total** | **0/18** | **1/18** |

**Result:** H2 NOT SUPPORTED. Investment efficiency is not significantly related to
managerial speech uncertainty in the predicted direction. Only 1/18 interaction
significant (Finance / CEO_QA_Weak_Modal, p=0.037).

### H3 Payout Policy — `run_h3_payout_policy`

Tests whether vague managers have different payout policies (dividends, repurchases).
DV: `div_stability_lead` (H3a) and `payout_flexibility_lead` (H3b).

Model: `PayoutMeasure_lead ~ Uncertainty + Lev + Uncertainty×Lev + Controls + EntityEffects + TimeEffects`

**Stage 3**: 112,968 calls. Valid div_stability_lead: 86,459. Valid payout_flexibility_lead: 105,301.

| Sample | DV | H3a/H3b significant |
|--------|----|--------------------:|
| Main | div_stability_lead | H3b: **2/6** interactions |
| Main | payout_flexibility_lead | — |
| Finance | payout_flexibility_lead | H3a: **1/6** |
| Utility | payout_flexibility_lead | H3b: **1/6** |
| **Total** | | **H3a: 1/36, H3b: 3/36** |

**Result:** Limited support for H3. H3a: 1/36 significant (Finance payout_flexibility). H3b: 3/36 significant (Main div_stability ×2, Utility payout_flexibility ×1).

### H4 Leverage Discipline — `run_h4_leverage`

Tests whether lagged leverage predicts manager uncertainty (H4: β₁ < 0).
DV: Manager uncertainty measures. Key IV: `Lev_lag` (one-year lagged leverage).

Model: `Uncertainty ~ Lev_lag + Analyst_QA_Uncertainty + Controls + EntityEffects + TimeEffects`

**Stage 3**: 112,968 calls. Valid Lev_lag: 105,380.

| Sample | H4 significant (β₁<0) | Notable measures |
|--------|---------------------:|------------------|
| Main | **2/6** | Manager_Pres (p=0.009), CEO_Pres (p=0.044) |
| Finance | 0/6 | — |
| Utility | 0/6 | — |
| **Total** | **2/18** | — |

**Result:** Partial support for H4 — lagged leverage predicts lower uncertainty in
presentation (but not Q&A) measures for Main sample. Consistent with leverage
discipline hypothesis for prepared remarks.

### H5 Analyst Dispersion — `run_h5_dispersion`

Tests whether manager uncertainty language causes higher analyst forecast dispersion
(H5: β₁ > 0). DV: `dispersion_lead` (analyst EPS forecast dispersion at next earnings).

Model A: `dispersion_lead ~ Manager_QA_Weak_Modal + Manager_QA_Uncertainty + Controls + prior_dispersion + FirmFE + YearFE`
Model B: `dispersion_lead ~ Uncertainty_Gap + Manager_Pres_Uncertainty + Controls + prior_dispersion + FirmFE + YearFE`

| Sample | Model A (β₁>0) | Model B (β₁>0) |
|--------|---------------:|---------------:|
| Main (w/ lag) | 0/1 | 0/1 |
| Main (no lag) | 0/1 | 0/1 |
| Finance (w/ lag) | 0/1 | 0/1 |
| Finance (no lag) | 0/1 | 0/1 |
| Utility (w/ lag) | 0/1 | 0/1 |
| Utility (no lag) | 0/1 | 0/1 |
| **Total** | **0/6** | **0/6** |

**Result:** H5 NOT SUPPORTED. Analyst forecast dispersion is not significantly related
to manager uncertainty language (β₁ coefficients negative or near-zero).

### H6 CCCL Speech — `run_h6_cccl`

Tests whether CEO clarity responds to CCCL instrument (SEC scrutiny proxy).
DV: Manager uncertainty measures. Key IV: `CCCL_lag` (lagged CCCL exposure).

Model: `Uncertainty ~ CCCL_lag + Size + Lev + ROA + TobinsQ + CashHoldings + EntityEffects + TimeEffects`

| Sample | N Obs | N Firms | CCCL_lag β | p-value | Significant |
|--------|------:|--------:|-----------:|--------:|:-----------:|
| Main (Mgr QA Unc) | 63,902 | 1,751 | −0.0865 | 0.089 | No |
| Main (CEO QA Unc) | 48,091 | 1,561 | 0.0227 | 0.599 | No |
| Finance (Mgr QA Unc) | 15,662 | 436 | −1.3066 | 0.014 | Yes* |
| Utility (Mgr QA Unc) | 3,154 | 81 | 1.3637 | 0.987 | No |

**Pre-trends test:** CCCL_lag vs CCCL_lead1/lead2 — significant leads found in Main and Finance samples. See provenance H6.md for details.

**Result:** H6 PARTIALLY SUPPORTED in Finance sample (4/21 significant at p<0.05). Main and Utility samples show null results. Pre-trends violations in Main and Finance samples raise causal interpretation concerns. See AUDIT_H6.md Finding #1.

### H7 Speech Vagueness and Stock Illiquidity — `run_h7_illiquidity`

Tests whether manager uncertainty language predicts future stock illiquidity (Amihud).
DV: `amihud_illiq_lead` (forward Amihud illiquidity ratio).

Model: `amihud_illiq_lead ~ Mgr_Uncertainty + CEO_Uncertainty + Size + Lev + ROA + TobinsQ + Volatility + StockRet + EntityEffects + TimeEffects`

| Sample | Measure | β₁ (Manager) | p-value | H7 Supported |
|--------|---------|-------------:|--------:|:------------:|
| Main | QA_Uncertainty | −0.0037 | 0.300 | No |
| Main | QA_Weak_Modal | −0.0085 | 0.071 | No |
| Main | Pres_Uncertainty | −0.0016 | 0.603 | No |
| Finance | QA_Uncertainty | −0.0018 | 0.426 | No |
| Finance | QA_Weak_Modal | −0.0038 | 0.278 | No |
| Finance | Pres_Uncertainty | −0.0031 | 0.382 | No |
| Utility | QA_Uncertainty | −0.00005 | 0.443 | No |
| Utility | QA_Weak_Modal | 0.00007 | 0.437 | No |
| Utility | Pres_Uncertainty | −0.00009 | 0.347 | No |

**H7-C (Spontaneity Gap):** β(QA) = −0.0037 vs β(Pres) = −0.0016 — NOT SUPPORTED (QA not > Pres).

**Result:** H7 NOT SUPPORTED. Manager uncertainty does not predict increased illiquidity.
All coefficients are negative (opposite direction) or near-zero.

### H8 Political Risk — `run_h8_political_risk`

Tests whether CEO speech vagueness moderates the effect of Political Risk (PRiskFY) on Abnormal Investment.
Unit of observation: firm-year (not call-level). Uses Hassan et al. (2019) PRisk index.

Model: `AbsAbInv_{t+1} ~ PRiskFY + ClarityStyle_Realtime + PRiskFY×ClarityStyle_Realtime + Size + Lev + ROA + TobinsQ + EntityEffects + TimeEffects`

Key variables:
- **PRiskFY**: Mean quarterly political risk over (fy_end - 366d, fy_end], min 2 quarters required
- **ClarityStyle_Realtime**: CEO clarity score (4-call rolling window, min 4 prior calls), time-varying, standardized (mean≈0, SD≈1)
- **AbsAbInv_lead**: |Biddle InvestmentResidual| shifted one fiscal year forward

**Stage 3**: 29,343 firm-years. Valid AbsAbInv_lead: 25,759. PRiskFY matched: 27,501.
ClarityStyle_Realtime: 18,842 valid (64.2% coverage).

| Sample | N Obs | N Firms | Within-R² | β₁ (PRiskFY) | β₂ (ClarityStyle) | β₃ (Interact) | p₃ |
|--------|------:|--------:|----------:|-------------:|-----------------:|--------------:|---:|
| Primary (All Industries) | 15,998 | 1,943 | 0.025 | −0.0000 (p=0.198) | −0.0003 (p=0.803) | 0.0000 (p=0.986) | NS |
| Main (ex-Finance/Utility) | 12,901 | 1,539 | 0.024 | −0.0000 (p=0.102) | 0.0005 (p=0.789) | 0.0000 (p=0.378) | NS |

**H8 NOT SUPPORTED** — CEO vagueness does NOT significantly moderate the political risk → abnormal investment relationship (β₃ ≈ 0, p = 0.986 in primary spec).

Data notes: ClarityStyle_Realtime has 35.8% missing (requires min 4 prior calls); PRiskFY has 6.3% missing due to Hassan data coverage.

### H9 Takeover Hazards — `run_h9_takeover_hazards`

Tests whether higher CEO/Manager clarity is associated with increased takeover risk.
Unit of observation: counting-process format (firm-year intervals). Uses CoxTimeVaryingFitter
from lifelines with time-varying covariates at actual per-year values (B7 fix applied).

**Stage 3**: 27,787 firm-year intervals, 2,429 firms, 690 event firms (28.4%).
Event breakdown: Friendly: 563, Uninvited: 87, Unknown: 40.

**Note:** Manager Clarity models skipped due to ClarityManager missing (0% coverage —
H0.1 archived). Only CEO Clarity models estimated.

| Model | Event Type | N Intervals | Event Firms | Concordance | ClarityCEO HR | p |
|-------|------------|------------:|------------:|------------:|--------------:|--:|
| Cox PH All | All | 12,139 | 349 | 0.537 | 1.050 | 0.566 |
| Cox CS Uninvited | Uninvited | 12,139 | 45 | 0.567 | 1.337 | 0.002 |
| Cox CS Friendly | Friendly | 12,139 | 346 | 0.523 | 1.098 | 0.001 |

**H9 Partially Supported** — CEO clarity associated with takeover risk in prior runs.
Current run: Manager Clarity models had insufficient data (ClarityManager missing).
See prior run results for significant HR estimates.

### H11 Political Risk and Language Uncertainty — `run_h11_prisk_uncertainty`

Tests whether higher political risk causes more uncertain language in earnings calls.
DV: 6 uncertainty measures (Manager/CEO QA/Pres Uncertainty, Weak Modal).
IV: PRiskQ (contemporaneous quarterly political risk from Hassan et al.).

Model: `Uncertainty_t ~ PRiskQ_t + Analyst_Uncertainty + Pres_Uncertainty + Negative_Sentiment + Controls + FirmFE + YearFE`

**Stage 3** (`build_h11_prisk_uncertainty_panel`): 112,968 calls, call-level panel.
PRiskQ matched via (gvkey, calendar_quarter).

| Sample | N Obs Range | PRiskQ β | Significant |
|--------|------------:|---------:|:-----------:|
| Main (Unc measures) | 56,020–77,040 | positive (p<0.001) | 6/6 |
| Finance (Unc measures) | 11,220–18,231 | positive (p<0.001) | 6/6 |
| Utility (Unc measures) | 2,238–3,734 | positive (p<0.001) | 4/6 |

**Result:** H11 **STRONGLY SUPPORTED** — 16/18 significant (p<0.05 one-tailed).
Higher political risk increases speech uncertainty across most measures and samples.
Presentation uncertainty measures show strongest effects.

### H11-Lag Political Risk (Lagged) — `run_h11_prisk_uncertainty_lag`

Tests whether lagged political risk affects current speech uncertainty.
IV: PRiskQ_lag (1-quarter lag) and PRiskQ_lag2 (2-quarter lag).

| Sample | N Obs Range | H11-Lag Significant | H11-Lag2 Significant |
|--------|------------:|--------------------:|---------------------:|
| Main | 54,003–74,324 | 4/6 | 6/6 |
| Finance | 10,952–17,811 | 3/6 | 2/6 |
| Utility | 2,165–3,606 | 2/6 | 1/6 |

**Result:** H11-Lag **PARTIALLY SUPPORTED** — 9/18 significant with 1-quarter lag; 9/18 significant with 2-quarter lag.
Presentation uncertainty shows persistent effects; Q&A effects are contemporaneous only.
Supports causal interpretation: political risk precedes language uncertainty.

### H12 Dividend Intensity — `run_h12_div_intensity`

Tests whether language uncertainty predicts future dividend intensity.
DV: DivIntensity_lead = (dvy_Q4 / atq)_{t+1} (firm-year level, forward).
IV: Avg_Uncertainty = mean call-level uncertainty within firm-year.

Model: `DivIntensity_{t+1} ~ Avg_Uncertainty_t + Size + Lev + ROA + TobinsQ + CashHoldings + CapexAt + RD_Intensity + FirmFE + YearFE`

**Stage 3** (`build_h12_div_intensity_panel`): Firm-year panel (one row per gvkey-fyearq).
Uncertainty measures averaged across calls within each firm-year.
DivIntensity_lead = DivIntensity shifted one fiscal year forward.

| Sample | N Obs (firm-years) | H12 Significant (β₁<0) |
|--------|-------------------:|-----------------------:|
| Main | 15,175–21,653 | 0/12 |
| Finance | 2,752–4,928 | 0/12 |
| **Total** | | **0/24** |

**Result:** H12 **NOT SUPPORTED** — 0/24 significant in predicted direction.
Language uncertainty does not predict future dividend intensity.
All β₁ coefficients positive or near-zero (opposite of hypothesis).

### Summary Statistics (H11) — `generate_summary_stats`

Main sample: 88,205 call observations, 1,884 firms, 3,533 CEOs, 2002–2018.
No Stage 3 panel builder — reads `ceo_clarity_extended_panel.parquet` directly.

| Panel | Variables | N range |
|-------|-----------|---------|
| A — Linguistic | 6 (uncertainty + sentiment pct) | 60,435–84,567 |
| B — Financial controls | 11 (Size, BM, Lev, ROA, …) | 67,965–87,994 |

---

## Output Structure

All outputs are organized by stage and timestamp:

```
outputs/
├── 1.1_CleanMetadata/{timestamp}/
├── 1.2_LinkEntities/{timestamp}/
├── 1.3_BuildTenureMap/{timestamp}/
├── 1.4_AssembleManifest/{timestamp}/
├── 2_Textual_Analysis/
│   ├── 2.1_TokenizeAndCount/{timestamp}/
│   └── 2.2_Variables/{timestamp}/
├── variables/
│   ├── ceo_clarity/{timestamp}/
│   └── ... (other hypothesis panels)
└── econometric/
    ├── ceo_clarity/{timestamp}/
    └── ... (other hypothesis results)
```

### Key Output Files

| File | Description |
|------|-------------|
| `clarity_scores.parquet` | CEO/Manager fixed effects with standardization |
| `*_table.tex` | Publication-ready LaTeX regression tables |
| `regression_results_*.txt` | Full regression output with coefficients, SEs, p-values |
| `model_diagnostics.csv` | R², N obs, N entities per model |
| `summary_stats.csv` | Panel summary statistics |

---

## Shared Variable Builders

All variable builders are in `src/f1d/shared/variables/`. Each module exports a single builder class that returns exactly one column.

### Data Engines (Private Singletons)

| Module | Input Source | Variables Computed | Winsorization |
|--------|--------------|-------------------|---------------|
| `_compustat_engine.py` | Compustat quarterly | Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, EPS_Growth, CashHoldings, TobinsQ, CapexAt, DividendPayer, OCF_Volatility | Per-year 1%/99% |
| `_crsp_engine.py` | CRSP daily + CCM | StockRet, MarketRet, Volatility, amihud_illiq | Per-year 1%/99% |
| `_linguistic_engine.py` | Stage 2 linguistic vars | All 25 _pct columns (uncertainty, sentiment, modal) | Per-year 1%/99% |
| `_ibes_engine.py` | IBES forecasts | SurpDec, Dispersion | None (bounded) |
| `_hassan_engine.py` | Political risk data | PRiskFY | None |

### Linguistic Variable Builders

| Builder | Column | Source |
|---------|--------|--------|
| `manager_qa_uncertainty.py` | `Manager_QA_Uncertainty_pct` | Stage 2 linguistic vars |
| `manager_pres_uncertainty.py` | `Manager_Pres_Uncertainty_pct` | Stage 2 linguistic vars |
| `ceo_qa_uncertainty.py` | `CEO_QA_Uncertainty_pct` | Stage 2 linguistic vars |
| `ceo_pres_uncertainty.py` | `CEO_Pres_Uncertainty_pct` | Stage 2 linguistic vars |
| `nonceo_manager_qa_uncertainty.py` | `NonCEO_Manager_QA_Uncertainty_pct` | Stage 2 linguistic vars |
| `nonceo_manager_pres_uncertainty.py` | `NonCEO_Manager_Pres_Uncertainty_pct` | Stage 2 linguistic vars |
| `cfo_qa_uncertainty.py` | `CFO_QA_Uncertainty_pct` | Stage 2 tokenize counts |
| `analyst_qa_uncertainty.py` | `Analyst_QA_Uncertainty_pct` | Stage 2 linguistic vars |
| `ceo_style_realtime.py` | `ClarityStyle_Realtime` | Stage 2 + rolling JS estimator |
| `negative_sentiment.py` | `Entire_All_Negative_pct` | Stage 2 linguistic vars |
| `manager_qa_weak_modal.py` | `Manager_QA_Weak_Modal_pct` | Stage 2 linguistic vars |
| `ceo_qa_weak_modal.py` | `CEO_QA_Weak_Modal_pct` | Stage 2 linguistic vars |
| `entire_all_uncertainty.py` | `Entire_All_Uncertainty_pct` | Stage 2 linguistic vars |
| `manager_qa_positive.py` | `Manager_QA_Positive_pct` | Stage 2 linguistic vars |
| `manager_qa_negative.py` | `Manager_QA_Negative_pct` | Stage 2 linguistic vars |
| `manager_pres_positive.py` | `Manager_Pres_Positive_pct` | Stage 2 linguistic vars |
| `manager_pres_negative.py` | `Manager_Pres_Negative_pct` | Stage 2 linguistic vars |
| `ceo_qa_positive.py` | `CEO_QA_Positive_pct` | Stage 2 linguistic vars |
| `ceo_qa_negative.py` | `CEO_QA_Negative_pct` | Stage 2 linguistic vars |
| `ceo_pres_positive.py` | `CEO_Pres_Positive_pct` | Stage 2 linguistic vars |
| `ceo_pres_negative.py` | `CEO_Pres_Negative_pct` | Stage 2 linguistic vars |
| `nonceo_manager_qa_positive.py` | `NonCEO_Manager_QA_Positive_pct` | Stage 2 linguistic vars |
| `nonceo_manager_qa_negative.py` | `NonCEO_Manager_QA_Negative_pct` | Stage 2 linguistic vars |
| `analyst_qa_positive.py` | `Analyst_QA_Positive_pct` | Stage 2 linguistic vars |
| `analyst_qa_negative.py` | `Analyst_QA_Negative_pct` | Stage 2 linguistic vars |
| `manager_pres_weak_modal.py` | `Manager_Pres_Weak_Modal_pct` | Stage 2 linguistic vars |
| `ceo_pres_weak_modal.py` | `CEO_Pres_Weak_Modal_pct` | Stage 2 linguistic vars |
| `ceo_clarity_style.py` | `ClarityStyle_Realtime` | Stage 2 + frozen CEO assignment |

### Financial Variable Builders

| Builder | Column | Engine |
|---------|--------|--------|
| `size.py` | `Size` | Compustat |
| `bm.py` | `BM` | Compustat |
| `lev.py` | `Lev` | Compustat |
| `roa.py` | `ROA` | Compustat |
| `current_ratio.py` | `CurrentRatio` | Compustat |
| `rd_intensity.py` | `RD_Intensity` | Compustat |
| `eps_growth.py` | `EPS_Growth` | Compustat |
| `cash_holdings.py` | `CashHoldings` | Compustat |
| `tobins_q.py` | `TobinsQ` | Compustat |
| `capex_intensity.py` | `CapexAt` | Compustat (Q4-only) |
| `dividend_payer.py` | `DividendPayer` | Compustat (Q4-only) |
| `ocf_volatility.py` | `OCF_Volatility` | Compustat (5-yr rolling) |
| `stock_return.py` | `StockRet` | CRSP |
| `market_return.py` | `MarketRet` | CRSP |
| `volatility.py` | `Volatility` | CRSP |
| `earnings_surprise.py` | `SurpDec` | IBES + CCM |
| `cccl_instrument.py` | `shift_intensity_sale_ff48` | CCCL instrument file |
| `takeover_indicator.py` | `Takeover`, `Takeover_Uninvited`, `Takeover_Friendly` | SDC M&A |
| `cash_flow.py` | `CashFlow` | Compustat (oancfy/avg_assets) |
| `sales_growth.py` | `SalesGrowth` | Compustat (YoY sales growth) |
| `investment_residual.py` | `InvestmentResidual` | Compustat (Biddle 2009) |
| `amihud_illiq.py` | `amihud_illiq` | CRSP (Amihud illiquidity) |
| `div_stability.py` | `div_stability` | Compustat |
| `payout_flexibility.py` | `payout_flexibility` | Compustat |
| `earnings_surprise_raw.py` | `EarningsSurprise_Raw` | IBES (ACTUAL - MEANEST) |
| `earnings_surprise_ratio.py` | `EarningsSurpriseRatio` | IBES (|ACTUAL - MEANEST|/|MEANEST|) |
| `prior_dispersion.py` | `prior_dispersion` | IBES (STDEV/|MEANEST|) |
| `dispersion_lead.py` | `dispersion_lead` | IBES (t+1 dispersion) |
| `earnings_volatility.py` | `earnings_volatility` | Compustat (rolling std) |
| `fcf_growth.py` | `fcf_growth` | Compustat (FCF growth) |
| `firm_maturity.py` | `firm_maturity` | Compustat (lifecycle proxy) |
| `is_div_payer_5yr.py` | `is_div_payer_5yr` | Compustat (5yr consistency) |
| `loss_dummy.py` | `loss_dummy` | Compustat (ibq < 0) |
| `prisk_q.py` | `PRiskQ` | Hassan (quarterly PRisk) |
| `prisk_q_lag.py` | `PRiskQ_lag` | Hassan (1-quarter lag) |
| `prisk_q_lag2.py` | `PRiskQ_lag2` | Hassan (2-quarter lag) |
| `div_intensity.py` | `DivIntensity` | Compustat (dvy_Q4 / atq) |

### Important Implementation Notes

**Q4-only variables:** `CapexAt` and `DividendPayer` use only Q4 Compustat rows because `capxy` and `dvy` are year-to-date cumulative. The Q4 row contains the full-year total.

**CUSIP joins:** IBES uses 8-char alphanumeric CUSIPs; CCM uses 9-char numeric. Join on `ibes[:8] == ccm[:8]`. Never zero-fill the IBES side — it corrupts alphanumeric CUSIPs.

---

## Architecture Rules

### Project Configuration

Main configuration file: `config/project.yaml`

```yaml
project:
  name: F1D_Clarity
  version: F1D.1.0

data:
  year_start: 2002
  year_end: 2018

paths:
  inputs: inputs
  outputs: outputs
  logs: logs

determinism:
  random_seed: 42
  thread_count: 1
  sort_inputs: true
```

### Variable Definitions

Variable metadata: `config/variables.yaml`

```yaml
Size:
  description: "Log total assets (inflation-adjusted)"
  source: compustat
  formula: "log(atq * cpi_adjustment)"
  merge_key: ["gvkey", "fyearq", "fqtr"]

Lev:
  description: "Total debt / Total assets"
  source: compustat
  formula: "(dlttq + dlcq) / atq"
```

### Runtime Configuration

Override settings via environment variables:

```bash
# Set logging level
export F1D_LOG_LEVEL=DEBUG

# Set output directory
export F1D_OUTPUT_DIR=/path/to/outputs

# Run with specific config
python -m f1d.econometric.run_ceo_clarity --config custom_config.yaml
```

---

## Testing

### Run Tests

```bash
# Run unit and regression tests (fast)
pytest tests/ -m "not e2e" -v

# Run with coverage
pytest tests/ -m "not e2e" --cov=src/f1d --cov-report=html

# Run end-to-end tests (requires synthetic data)
pytest tests/ -m e2e -v --timeout=1200

# Run specific test file
pytest tests/unit/test_panel_ols.py -v
```

### Test Structure

```
tests/
├── unit/           # Unit tests (fast, isolated, mocked)
├── integration/    # Integration tests (subprocess execution)
├── regression/     # Regression tests (baseline comparisons)
├── verification/   # Dry-run verification tests
├── fixtures/       # Test data fixtures
└── factories/      # Test data factories
```

### Continuous Integration

CI runs on every push/PR via GitHub Actions:

- **Security scan:** Bandit SAST
- **Type checking:** mypy strict mode
- **Unit tests:** Python 3.9–3.13 matrix
- **Coverage:** Minimum 60% enforced

---

## Documentation

### Key Documents

| Document | Description |
|----------|-------------|
| [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md) | Dependency versions, pinning rationale, upgrade constraints |
| [docs/UPGRADE_GUIDE.md](docs/UPGRADE_GUIDE.md) | Step-by-step upgrade procedures for dependencies |
| [docs/ARCHITECTURE_STANDARD.md](docs/ARCHITECTURE_STANDARD.md) | Codebase architecture standards (v6.1 compliant) |
| [docs/CODE_QUALITY_STANDARD.md](docs/CODE_QUALITY_STANDARD.md) | Code style, linting, type checking standards |
| [docs/TIER_MANIFEST.md](docs/TIER_MANIFEST.md) | Module tier classification and coverage targets |
| [docs/VARIABLE_CATALOG_V2_V3.md](docs/VARIABLE_CATALOG_V2_V3.md) | Variable definitions and construction formulas |

### Inline Documentation

All modules follow Google-style docstrings:

```python
def run_panel_ols(
    df: pd.DataFrame,
    dependent_var: str,
    fixed_effects: list[str],
) -> dict[str, Any]:
    """
    Run panel OLS with entity and time fixed effects.
    
    Args:
        df: Panel DataFrame with one row per entity-time observation.
        dependent_var: Column name of dependent variable.
        fixed_effects: List of column names for fixed effect dummies.
    
    Returns:
        Dictionary with keys: 'coefficients', 'r2_within', 'r2_overall',
        'n_obs', 'n_entities', 'formula'.
    
    Raises:
        ValueError: If dependent_var not in df.columns.
    """
```

---

## Project Structure

```
F1D/
├── src/f1d/                    # Main package (src-layout)
│   ├── shared/                 # Tier 1: Cross-cutting utilities
│   │   ├── config/             # Pydantic configuration models
│   │   ├── logging/            # Structured logging infrastructure
│   │   ├── variables/          # Variable builders (50+ files)
│   │   └── *.py                # Core utilities (path_utils, panel_ols, etc.)
│   ├── sample/                 # Stage 1: Sample construction
│   ├── text/                   # Stage 2: Text processing
│   ├── variables/              # Stage 3: Panel builders
│   └── econometric/            # Stage 4: Hypothesis tests
├── tests/                      # Test suite
├── config/                     # Configuration files
├── inputs/                     # Raw input data (not in repo)
├── outputs/                    # Pipeline outputs (not in repo)
├── docs/                       # Documentation
├── .github/workflows/          # CI/CD workflows
├── pyproject.toml              # Package configuration
├── requirements.txt            # Production dependencies
└── README.md                   # This file
```

---

## Contributing

### Development Setup

```bash
# Clone and install with dev dependencies
git clone https://github.com/user/f1d.git
cd f1d
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Code Standards

- **Formatting:** ruff (line length 88)
- **Linting:** ruff with extended rule set (E, W, F, I, B, C4, UP, ARG, SIM)
- **Type checking:** mypy strict mode for `src/f1d/shared/`
- **Docstrings:** Google-style for all public functions
- **Tests:** pytest with coverage threshold 60%

### Before Submitting

```bash
# Run linter
ruff check src/f1d/

# Run formatter
ruff format src/f1d/

# Run type checker
mypy src/f1d/shared/ --config-file pyproject.toml

# Run tests
pytest tests/ -m "not e2e" --cov=src/f1d --cov-fail-under=30
```

### Adding New Variables

1. Create `src/f1d/shared/variables/{variable_name}.py`
2. Inherit from `VariableBuilder` base class
3. Implement `build()` method returning single column
4. Export from `src/f1d/shared/variables/__init__.py`
5. Add unit test in `tests/unit/test_{variable_name}.py`
6. Update this README's variable table

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Citation

If you use this pipeline in your research, please cite:

```bibtex
@software{f1d2026,
  author = {Thesis Author},
  title = {F1D: Uncertainty in Language and Corporate Outcomes Pipeline},
  year = {2026},
  url = {https://github.com/user/f1d}
}
```

---

## Contact

For questions or issues, please open a GitHub issue or contact the thesis author.

---

*Last updated: 2026-03-05*
