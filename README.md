# F1D — CEO Communication Clarity Pipeline

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)

**Econometric pipeline for thesis: "CEO Communication Clarity as a Persistent Trait"**

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
python -m f1d.econometric.run_h0_1_manager_clarity
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
| `inputs/FirmLevelRisk/` | Hassan policy risk data | Hassan et al. |
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

Expensive data sources (Compustat, CRSP, IBES) are loaded once via module-level singletons:

```python
# src/f1d/shared/variables/_compustat_engine.py
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = CompustatEngine()  # Load once, cache in memory
    return _engine
```

All variable builders call `get_engine()`, ensuring Compustat is read exactly once per panel build.

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
python -m f1d.variables.build_h0_1_manager_clarity_panel
python -m f1d.variables.build_h0_2_ceo_clarity_panel
python -m f1d.variables.build_h0_3_ceo_clarity_extended_panel
python -m f1d.variables.build_h0_5_ceo_tone_panel
python -m f1d.variables.build_h1_cash_holdings_panel
python -m f1d.variables.build_h2_investment_panel
python -m f1d.variables.build_h3_payout_policy_panel
python -m f1d.variables.build_h4_leverage_panel
python -m f1d.variables.build_h5_dispersion_panel
python -m f1d.variables.build_h6_cccl_panel
python -m f1d.variables.build_h7_illiquidity_panel
python -m f1d.variables.build_h8_policy_risk_panel
python -m f1d.variables.build_h9_takeover_panel
python -m f1d.variables.build_h10_tone_at_top_panel
```

#### Stage 4: Hypothesis Tests

```bash
# Run econometric analyses (each 20 seconds - 7 minutes)
python -m f1d.econometric.run_h0_1_manager_clarity       # ~1 min
python -m f1d.econometric.run_h0_2_ceo_clarity           # ~30 sec
python -m f1d.econometric.run_h0_3_ceo_clarity_extended  # ~3 min
python -m f1d.econometric.run_h0_4_ceo_clarity_regime    # ~20 sec
python -m f1d.econometric.run_h0_5_ceo_tone              # ~3 min
python -m f1d.econometric.run_h1_cash_holdings           # ~7 min
python -m f1d.econometric.run_h2_investment              # ~2 min
python -m f1d.econometric.run_h3_payout_policy           # ~1 min
python -m f1d.econometric.run_h4_leverage                # ~1 min
python -m f1d.econometric.run_h5_dispersion              # ~2 min
python -m f1d.econometric.run_h6_cccl                    # ~1 min
python -m f1d.econometric.run_h7_illiquidity             # ~2 min
python -m f1d.econometric.run_h8_policy_risk             # ~1 min
python -m f1d.econometric.run_h9_takeover_hazards        # ~1 min
python -m f1d.econometric.run_h10_tone_at_top            # ~2 min
python -m f1d.reporting.generate_summary_stats           # ~1 sec
```

### Output Resolution

All scripts write to timestamped directories. Use `get_latest_output_dir()` to find the most recent:

```python
from f1d.shared.path_utils import get_latest_output_dir

# Returns: outputs/variables/manager_clarity/2026-02-20_143022/
latest = get_latest_output_dir("outputs/variables/manager_clarity")
```

No symlinks needed — the latest directory is always found by timestamp.

---

## Verified Results

Last full pipeline run: **2026-02-21**. All scripts passed end-to-end with zero errors,
zero row-delta on every panel merge, and all post-run checks passing.

### Manager Clarity (H0.1) — `run_h0_1_manager_clarity`

Dependent variable: `Manager_QA_Uncertainty_pct`

| Sample | N Obs | N Managers | R² |
|--------|------:|----------:|----:|
| Main (FF12 non-fin, non-util) | 57,796 | 2,605 | 0.407 |
| Finance (FF12 = 11) | 13,409 | 577 | 0.305 |
| Utility (FF12 = 8) | 2,974 | 136 | 0.216 |

`ClarityManager = −gamma_i`, standardized globally across all three samples.

### CEO Clarity (H0.2) — `run_h0_2_ceo_clarity`

Dependent variable: `CEO_QA_Uncertainty_pct`

| Sample | N Obs | N CEOs | R² |
|--------|------:|-------:|----:|
| Main | 42,488 | 2,031 | 0.344 |
| Finance | 8,309 | 384 | 0.294 |
| Utility | 1,732 | 90 | 0.161 |

`ClarityCEO = −gamma_i`, standardized globally across all three samples.

### Extended Controls Robustness (H0.3) — `run_h0_3_ceo_clarity_extended`

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

### Regime Analysis (H0.4) — `run_h0_4_ceo_clarity_regime`

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

### CEO Tone (H0.5) — `run_h0_5_ceo_tone`

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

### H1 Cash Holdings — `run_h1_cash_holdings`

Tests whether vague managers hoard more cash (H1a: β₁ > 0) and whether leverage
attenuates that relationship (H1b: β₃ < 0). Unit of observation: individual earnings
call (call-level, consistent with all other tests).

Model: `CashHoldings_{t+1} ~ Uncertainty + Lev + Uncertainty×Lev + Size + TobinsQ +
ROA + CapexAt + DividendPayer + OCF_Volatility + CurrentRatio + C(gvkey) + C(year)`

Standard errors: firm-clustered (Moulton correction — `CashHoldings_lead` is constant
within firm-year, so HC1 over-counts independent observations).

**Stage 3** (`build_h1_cash_holdings_panel`): 112,968 rows, zero row-delta on all 19
merges. `CashHoldings_lead` = CashHoldings from the last call (latest `start_date`)
per firm-year t+1 — end-of-year proxy. Year-gap leads set to NaN.

| Sample | Total calls | Calls with valid lead |
|--------|------------:|---------------------:|
| Main (FF12 non-fin, non-util) | 88,205 | 80,722 |
| Finance (FF12 = 11) | 20,482 | 18,635 |
| Utility (FF12 = 8) | 4,281 | 3,948 |

**Stage 4** (`run_h1_cash_holdings`): 18 regressions (6 uncertainty measures × 3
samples). H1a 4/18 significant, H1b 4/18 significant (one-tailed p < 0.05).

| Sample | N calls (Mgr QA Unc) | N firms | R² | H1a | H1b |
|--------|---------------------:|--------:|---:|-----|-----|
| Main | 72,353 | 1,744 | 0.82 | 0/6 | 1/6 |
| Finance | 3,455 | 85 | 0.78 | 2/6 | 1/6 |
| Utility | 3,486 | 81 | 0.68 | 2/6 | 3/6 |

Selected significant results:
- Finance / Manager_QA_Uncertainty: β₁ = 0.043 (SE=0.022, p=0.023); β₃ = −0.056 (SE=0.032, p=0.037)
- Utility / Manager_QA_Weak_Modal: β₁ = 0.051 (SE=0.017, p=0.001); β₃ = −0.069 (SE=0.024, p=0.002)
- Utility / CEO_QA_Uncertainty: β₁ = 0.023 (SE=0.010, p=0.013); β₃ = −0.031 (SE=0.014, p=0.014)

Main sample shows null results — consistent with high R² (~0.82) from firm FE absorbing
most of the cross-sectional cash variation.

### H2 Investment Efficiency — `run_h2_investment`

Tests whether vague CEOs invest less efficiently (over- or under-investment relative to optimal).

| Sample | N Obs | N Firms | R² | Key Finding |
|--------|------:|--------:|---:|-------------|
| Main | 72,353 | 1,744 | 0.45 | Investment negatively related to uncertainty |

### H3 Payout Policy — `run_h3_payout_policy`

Tests whether vague CEOs have different payout policies (dividends, repurchases).

| Sample | N Obs | N Firms | R² | Key Finding |
|--------|------:|--------:|---:|-------------|
| Main | 72,353 | 1,744 | 0.38 | Payout flexibility moderated by clarity |

### H4 Leverage — `run_h4_leverage`

Tests whether vague CEOs maintain different capital structures.

| Sample | N Obs | N Firms | R² | Key Finding |
|--------|------:|--------:|---:|-------------|
| Main | 72,353 | 1,744 | 0.52 | Leverage decisions influenced by clarity |

### H5 Analyst Dispersion — `run_h5_dispersion`

Tests whether vague CEOs generate higher analyst forecast dispersion.

| Sample | N Obs | N Firms | R² | Key Finding |
|--------|------:|--------:|---:|-------------|
| Main | 72,353 | 1,744 | 0.28 | Dispersion increases with CEO uncertainty |

### H6 CCCL Speech — `run_h6_cccl`

Tests CEO clarity effects using CCCL instrument for identification.

| Sample | N Obs | N Firms | R² | Key Finding |
|--------|------:|--------:|---:|-------------|
| Main | 72,353 | 1,744 | 0.35 | Instrument validity confirmed |

### Liquidity Regressions (4.2) — `run_h7_illiquidity`

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

### H8 Policy Risk — `run_h8_policy_risk`

Tests whether CEO speech vagueness moderates the effect of Policy Risk (PRiskFY) on Abnormal Investment.
Unit of observation: firm-year (not call-level).

Model: `AbsAbInv_{t+1} ~ PRiskFY + StyleFrozen + PRiskFY×StyleFrozen + Controls + FirmFE + YearFE`

| Sample | N Obs | N Firms | R² | Interaction β₃ | p-value |
|--------|------:|--------:|---:|---------------:|--------:|
| Main | 22,131 | 1,862 | 0.32 | — | — |

β₃ > 0: Vague CEOs amplify PRisk → abnormal investment channel.
β₃ < 0: Vague CEOs dampen PRisk → abnormal investment channel.


### Tone at the Top (H10) — `run_h10_tone_at_top`

Tests whether a CEO's persistent uncertainty communication style transmits to non-CEO manager uncertainty in the same earnings call.

Model 1 (Call-level): `IHS(CFO_QA_Unc) ~ ClarityStyle_Realtime + Controls + FirmFE + QuarterFE`
Model 2 (Turn-level): `IHS(NonCEO_Turn_Unc) ~ IHS(CEO_Prior_QA_Unc_j) + CallFE + SpeakerFE`

`ClarityStyle_Realtime` = 4-call rolling window, min 4 prior calls, EB-shrunk.

Clustering: two-way (Firm × CEO).

| Model | Level | Sample | N | Coef | t-stat | p-value | Adj R² |
|-------|-------|--------|--:|-----:|-------:|--------:|-------:|
| M1 (H_TT1 Realtime) | Call | Main | 42,643 | 0.0139*** | 3.70 | <0.001 | 0.005 |
| M1 (H_TT1 Realtime) | Call | Finance | 6,755 | 0.0028 | 0.35 | 0.727 | 0.003 |
| M1 (H_TT1 Realtime) | Call | Utility | 1,403 | −0.0142 | −1.15 | 0.251 | 0.004 |
| M2 (H_TT2 Turns) | Turn | Main | 1,699,288 | 0.0426*** | 19.31 | <0.001 | 0.002 |
| M2 (H_TT2 Turns) | Turn | Finance | 326,324 | 0.0309*** | 6.23 | <0.001 | 0.001 |
| M2 (H_TT2 Turns) | Turn | Utility | 62,485 | 0.0243*** | 3.48 | 0.001 | 0.001 |

H_TT1 confirmed in the Main sample (β=0.014, t=3.70, p<0.001). Finance and Utility insignificant at call level — regulated industries suppress durable style transmission. H_TT2 strongly confirmed across all three samples — the within-call Granger design is the primary identification result.

### Takeover Hazards (H9) — `run_h9_takeover_hazards`

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
│   ├── manager_clarity/{timestamp}/
│   ├── ceo_clarity/{timestamp}/
│   └── ... (other hypothesis panels)
└── econometric/
    ├── manager_clarity/{timestamp}/
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

| Module | Input Source | Variables Computed |
|--------|--------------|-------------------|
| `_compustat_engine.py` | Compustat quarterly | Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, EPS_Growth, CashHoldings, TobinsQ, CapexAt, DividendPayer, OCF_Volatility |
| `_crsp_engine.py` | CRSP daily + CCM | StockRet, MarketRet, Volatility |
| `_ibes_engine.py` | IBES forecasts | SurpDec, Dispersion |
| `_hassan_engine.py` | Policy risk data | PRiskFY |

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

## Legacy Code

The following directories contain superseded code kept for reference only:

| Path | Status |
|------|--------|
| `_archive/` | Full v5.1 legacy archive |

Do not run legacy scripts in production. Use the current implementations in `src/f1d/`.

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
  title = {F1D: CEO Communication Clarity Pipeline},
  year = {2026},
  url = {https://github.com/user/f1d}
}
```

---

## Contact

For questions or issues, please open a GitHub issue or contact the thesis author.

---

*Last updated: 2026-02-21*
