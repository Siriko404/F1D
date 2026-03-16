# F1D — Uncertainty in Language and Corporate Outcomes

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)

Econometric pipeline for the thesis **"Uncertainty in Language and Corporate Outcomes."**
Processes 112,968 earnings call observations across 2,429 firms (2002–2018) through a deterministic 4-stage pipeline, testing 13 hypothesis suites on whether CEO speech uncertainty predicts corporate financial outcomes.

---

## Table of Contents

- [Pipeline Architecture](#pipeline-architecture)
- [Hypothesis Suites](#hypothesis-suites)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Pipeline](#running-the-pipeline)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Testing](#testing)
- [Data Provenance & Audit Documentation](#data-provenance--audit-documentation)
- [Technology Stack](#technology-stack)
- [Code Quality](#code-quality)
- [License](#license)

---

## Pipeline Architecture

```
Stage 1                Stage 2              Stage 3               Stage 4
Sample Construction    Text Processing      Variable Building     Econometric Analysis
───────────────────    ────────────────     ─────────────────     ────────────────────
Transcripts ──┐        Tokenization         Per-hypothesis        PanelOLS / Cox PH
Execucomp ────┤        (C++ compiler)       panel builders        regressions with
CCM Link ─────┤              │              (80+ variable         firm + year FE,
              ▼              ▼              builders via          clustered SEs
     master_sample     linguistic           Builder pattern)           │
     _manifest         variables                 │                    ▼
     .parquet          per call                  ▼              LaTeX tables,
                       per year             {hypothesis}        diagnostics CSV,
                                            _panel.parquet      markdown reports
```

Each stage reads from disk and writes to timestamped output directories under `outputs/`. Compute engines (Compustat, CRSP, IBES, Linguistic) use singleton caching for efficient data loading. All outputs are immutable and reproducible.

---

## Hypothesis Suites

| Suite | Research Question | Model | DV |
|-------|-------------------|-------|----|
| **H0.3** | Does CEO clarity FE structure hold under extended controls? | PanelOLS | Clarity residuals |
| **H1** | Does speech uncertainty predict cash holdings? | PanelOLS | CashHoldings (lead) |
| **H2** | Does uncertainty predict investment efficiency? | PanelOLS | InvestmentResidual (lead) |
| **H3** | Does uncertainty predict payout policy stability? | PanelOLS | DividendStability / PayoutFlexibility (lead) |
| **H4** | Does uncertainty predict leverage changes? | PanelOLS | Lev (lag/lead) |
| **H5** | Does uncertainty predict analyst forecast dispersion? | PanelOLS | Dispersion |
| **H6** | Does exogenous uncertainty (CCCL instrument) affect outcomes? | PanelOLS (reduced form) | Linguistic DVs |
| **H7** | Does uncertainty predict post-call illiquidity changes? | PanelOLS | delta_amihud |
| **H9** | Does uncertainty predict takeover hazard rates? | Cox PH (survival) | Takeover event |
| **H11** | Does political risk interact with speech uncertainty? | PanelOLS (base/lag/lead) | PRiskQ variants |
| **H12** | Does uncertainty predict diversification intensity? | PanelOLS | DivIntensity (lead) |
| **H13.1** | Does uncertainty predict capital expenditure? | PanelOLS | CapexAt (lead) |
| **H14** | Does uncertainty predict bid-ask spread changes? | PanelOLS | delta_spread |

**Supplementary:** `ceo_presence_probit.py` characterises determinants of CEO presence in Q&A sessions (selection analysis for H7).

All suites have full data provenance documentation and independent red-team audit reports — see [Data Provenance & Audit Documentation](#data-provenance--audit-documentation).

---

## Prerequisites

### Required Input Data

The following datasets must be present in `inputs/` before running. These are externally sourced and not included in the repository.

| Directory | Description | Source |
|-----------|-------------|--------|
| `Earnings_Calls_Transcripts/` | Earnings call transcripts with speaker data | Transcript provider |
| `LM_dictionary/` | Loughran-McDonald sentiment dictionary | [SRAF](https://sraf.nd.edu/textual-analysis/resources/) |
| `comp_na_daily_all/` | Compustat quarterly fundamentals | WRDS Compustat |
| `CRSP_DSF/` | CRSP daily stock files | WRDS CRSP |
| `tr_ibes/` | IBES EPS analyst forecasts | WRDS IBES |
| `CRSPCompustat_CCM/` | CRSP-Compustat merged link table | WRDS CCM |
| `SDC/` | SDC Platinum M&A transaction data | Refinitiv SDC |
| `CCCL_instrument/` | CEO turnover shift-intensity instrument | Constructed |
| `Execucomp/` | Executive compensation data | WRDS Execucomp |
| `FirmLevelRisk/` | Hassan et al. political risk measures | Hassan et al. |
| `Manager_roles/` | Manager role classification | Constructed |
| `FF1248/` | Fama-French industry classifications | Kenneth French |

### System Requirements

- **Python:** 3.9 – 3.13
- **Memory:** 16 GB minimum, 32 GB recommended
- **Disk:** ~50 GB for inputs, ~10 GB for outputs
- **Compiler:** g++ (C++17) for Stage 2 tokenizer

---

## Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# Install package (editable) and dependencies
pip install --upgrade pip
pip install -e .
pip install -r requirements.txt
```

### Quick Start

```bash
# Validate setup with a dry run (no input data required)
python -m f1d.econometric.run_h1_cash_holdings --dry-run

# Run a full hypothesis test (requires input data)
python -m f1d.variables.build_h1_cash_holdings_panel
python -m f1d.econometric.run_h1_cash_holdings
```

> The editable install (`pip install -e .`) is required. All scripts use `from f1d.*` imports.

---

## Running the Pipeline

### Stage-by-Stage Execution

```bash
# Stage 1: Sample Construction
python -m f1d.sample.clean_metadata
python -m f1d.sample.link_entities
python -m f1d.sample.build_tenure_map
python -m f1d.sample.assemble_manifest

# Stage 2: Text Processing
python -m f1d.text.tokenize_transcripts
python -m f1d.text.build_linguistic_variables

# Stage 3: Build hypothesis panel (one per suite)
python -m f1d.variables.build_h1_cash_holdings_panel

# Stage 4: Run regressions
python -m f1d.econometric.run_h1_cash_holdings
```

### All Econometric Scripts

| Suite | Command |
|-------|---------|
| H0.3 | `python -m f1d.econometric.run_h0_3_ceo_clarity_extended` |
| H1 | `python -m f1d.econometric.run_h1_cash_holdings` |
| H2 | `python -m f1d.econometric.run_h2_investment` |
| H3 | `python -m f1d.econometric.run_h3_payout_policy` |
| H4 | `python -m f1d.econometric.run_h4_leverage` |
| H5 | `python -m f1d.econometric.run_h5_dispersion` |
| H6 | `python -m f1d.econometric.run_h6_cccl` |
| H7 | `python -m f1d.econometric.run_h7_illiquidity` |
| H7 (selection) | `python -m f1d.econometric.ceo_presence_probit` |
| H9 | `python -m f1d.econometric.run_h9_takeover_hazards` |
| H11 | `python -m f1d.econometric.run_h11_prisk_uncertainty` |
| H11-lag | `python -m f1d.econometric.run_h11_prisk_uncertainty_lag` |
| H11-lead | `python -m f1d.econometric.run_h11_prisk_uncertainty_lead` |
| H12 | `python -m f1d.econometric.run_h12_div_intensity` |
| H13.1 | `python -m f1d.econometric.run_h13_1_capex` |
| H14 | `python -m f1d.econometric.run_h14_bidask_spread` |

### CLI Flags

All Stage 4 scripts support:
- `--dry-run` — validate configuration and imports without loading data
- `--panel-path PATH` — override the default panel artifact location

Outputs are written to `outputs/{category}/{hypothesis}/{YYYY-MM-DD_HHMMSS}/`.

---

## Project Structure

```
F1D/
├── config/
│   ├── project.yaml                 # Pipeline configuration
│   └── variables.yaml               # Variable source definitions
├── src/f1d/                         # Main package (v6.0.0)
│   ├── sample/                      # Stage 1: Sample construction
│   ├── text/                        # Stage 2: Text processing
│   ├── variables/                   # Stage 3: Per-hypothesis panel builders
│   ├── econometric/                 # Stage 4: Regression scripts
│   ├── reporting/                   # Summary statistics generation
│   └── shared/                      # Cross-cutting utilities
│       ├── config/                  #   Configuration (Pydantic models)
│       ├── logging/                 #   Structured logging (structlog)
│       ├── observability/           #   Runtime monitoring
│       ├── outputs/                 #   Manifest + attrition tables
│       ├── variables/               #   80+ individual variable builders
│       ├── panel_ols.py             #   PanelOLS regression runner
│       ├── iv_regression.py         #   IV/2SLS regression
│       └── latex_tables*.py         #   LaTeX table generation
├── inputs/                          # Raw data (not in git)
├── outputs/                         # Timestamped pipeline outputs
├── tests/                           # unit / integration / regression / verification / performance
├── docs/
│   ├── Draft/                       # Thesis LaTeX document
│   ├── provenance/                  # Data provenance docs (13 suites)
│   │   └── Audits/                  # Red-team adversarial audit reports
│   ├── audits/                      # Code audit reports
│   └── Prompts/                     # AI prompt templates
├── .planning/codebase/              # Codebase analysis documentation
├── pyproject.toml                   # Package config (PEP 621)
├── requirements.txt                 # Pinned dependencies
└── .pre-commit-config.yaml          # Pre-commit hooks
```

---

## Configuration

| File | Purpose |
|------|---------|
| `config/project.yaml` | Pipeline parameters: year range, step configs, paths, determinism settings |
| `config/variables.yaml` | Variable source definitions mapping raw data to builder outputs |
| `pyproject.toml` | Package metadata, tool configs (ruff, mypy, pytest, coverage) |

### Determinism

All pipeline runs are deterministic:
- `random_seed: 42`
- `thread_count: 1`
- `sort_inputs: true`

---

## Testing

```bash
# Unit tests
pytest tests/unit/

# Verification (dry-run all scripts)
pytest tests/verification/

# Integration tests
pytest tests/integration/

# Performance benchmarks
pytest tests/performance/

# Full suite
pytest
```

Test categories: `unit/` (shared module logic), `integration/` (cross-stage flows), `regression/` (output stability), `verification/` (dry-run all scripts), `performance/` (benchmarks).

---

## Data Provenance & Audit Documentation

Every active hypothesis suite has two layers of documentation in `docs/provenance/`:

1. **First-layer provenance doc** (`{SUITE_ID}.md`) — regression-agnostic reproducibility documentation covering:
   - Suite overview (model family, estimator, variables)
   - Reproducibility snapshot (exact commands)
   - End-to-end dependency chain
   - Raw data provenance with verified row counts
   - Merge & sample construction audit
   - Paper-grade variable dictionary
   - Estimation spec register
   - Verification log (all commands executed)
   - Corporate finance thesis referee assessment (identification, robustness, interpretation)
   - Master issue register with severity rankings

2. **Red-team adversarial audit** (`Audits/{SUITE_ID}_red_team.md`) — independent second-layer review that:
   - Treats the first-layer audit as an object to test, not a source of truth
   - Verifies every material claim against code and artifacts
   - Identifies factual errors, omissions, and severity miscalibrations
   - Reports false positives and missed issues
   - Provides a corrected master issue register

All first-layer docs have been revised to incorporate red-team findings.

Additional code audit reports are in `docs/audits/`.

---

## Technology Stack

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 2.2.3 | Data manipulation |
| numpy | 2.3.2 | Numerical operations |
| linearmodels | ≥0.6.0 | PanelOLS with FE, IV/2SLS |
| statsmodels | 0.14.6 | OLS, Probit, VIF diagnostics |
| lifelines | 0.30.0 | Cox PH survival analysis (H9) |
| scipy | 1.16.1 | Statistical tests |
| structlog | ≥25.0 | Structured logging |
| pydantic | ≥2.0 | Configuration validation |
| pyarrow | 21.0.0 | Parquet I/O |
| rapidfuzz | ≥3.14.0 | Fuzzy string matching (entity linking) |
| pandera | ≥0.20.0 | DataFrame schema validation |

Full dependency list with pinned versions in `requirements.txt`.

---

## Code Quality

- **Formatting & linting:** [ruff](https://docs.astral.sh/ruff/) (line length 88, target Python 3.9)
- **Type checking:** [mypy](https://mypy-lang.org/) with tiered strictness (strict for `f1d.shared.*`, relaxed for stage modules)
- **Pre-commit hooks:** ruff format + lint, mypy, trailing whitespace, YAML validation
- **Logging:** Structured logging via structlog with dual console + file output
- **Determinism:** Enforced random seed, single-threaded execution, sorted inputs

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
