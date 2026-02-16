# F1D Data Processing Pipeline

Research data processing pipeline that constructs panel datasets for empirical finance research. Processes earnings call transcripts, links entities across databases, computes text-based measures, merges financial controls, and runs econometric analyses. Built for academic replication and thesis work.

## Installation

### Prerequisites

- Python >= 3.8 (tested on Python 3.8-3.13)
- Git (for cloning the repository)

### Install Package (Required)

Install the F1D package in editable mode to enable proper namespace imports:

```bash
pip install -e .
```

This is required for all scripts to use `from f1d.shared.*` imports. Without this step, you will encounter `ModuleNotFoundError: No module named 'f1d'`.

### Core Dependencies

Install all required dependencies:

```bash
pip install -r requirements.txt
```

This installs all core dependencies (pandas, numpy, scipy, statsmodels, etc.) needed for pipeline execution.

### Optional Dependencies

**RapidFuzz** (recommended for improved entity matching):
```bash
pip install rapidfuzz>=3.14.0
```

RapidFuzz enables Tier 3 fuzzy name matching in entity linking, which significantly improves match rates for company names with spelling variations or abbreviations. The pipeline runs without RapidFuzz (graceful degradation), but match rates will be lower.

## Pipeline Flow Diagram

This diagram shows the complete data flow from raw inputs through 4 processing phases to final econometric outputs.

### Overview

The F1D pipeline processes earnings call transcripts through a 4-stage workflow:

1. **Step 0: Raw Inputs** - Earnings calls, financial data, reference files
2. **Step 1: Sample Construction** - Build master_sample_manifest.parquet
3. **Step 2: Text Processing** - Tokenize and construct linguistic_variables.parquet
4. **Step 3: Financial Features** - Build firm_controls.parquet & market_variables.parquet
5. **Step 4: Econometric Analysis** - Estimate CEO clarity, liquidity, takeover models

### Pipeline Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STEP 0: RAW INPUTS (1_Inputs/)                        │
└─────────────────────────────────────────────────────────────────────────────┘
│
├─ Earnings Call Data
│  ├─ Unified-info.parquet (55 MB) - Call metadata
│  ├─ speaker_data_2002.parquet through speaker_data_2018.parquet (2.5 GB total)
│  └─ managerial_roles_extracted.txt - Role definitions
│
├─ Text Processing Resources
│  ├─ Loughran-McDonald_MasterDictionary_1993-2024.csv (9 MB)
│  └─ Loughran-McDonald_MasterDictionary_1993-2024-profile.md
│
├─ Financial Data
│  ├─ CRSPCompustat_CCM/ - Linking table (GVKEY-PERMNO)
│  ├─ CRSP_DSF/ - Daily stock returns
│  ├─ comp_na_daily_all/ - Compustat North America daily
│  ├─ tr_ibes/ - IBES analyst forecasts
│  ├─ Execucomp/ - Executive compensation data
│  └─ master_variable_definitions.csv (60 KB)
│
├─ Event Data
│  ├─ SDC/ - M&A deal data
│  └─ CEO Dismissal Data 2021.02.03.xlsx
│
└─ Reference Data
   ├─ Siccodes12.zip, Siccodes48.zip - Industry classification
   └─ CCCL instrument/ - Instrumental variable data
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 1: SAMPLE CONSTRUCTION (1_Sample/)                         │
│           Objective: Build master_sample_manifest.parquet                    │
└─────────────────────────────────────────────────────────────────────────────┘
│
├─ 1.1_CleanMetadata.py
│  Input:  Unified-info.parquet
│  Output: 4_Outputs/1.1_CleanMetadata/metadata_cleaned.parquet
│  Process:
│    • Clean call metadata (dates, strings, formats)
│    • Validate fields and remove invalid records
│    • Generate descriptive stats
│
├─ 1.2_LinkEntities.py
│  Input:  metadata_cleaned.parquet + CRSPCompustat_CCM/
│  Output: 4_Outputs/1.2_LinkEntities/metadata_linked.parquet
│  Process:
│    • Link calls to firms (GVKEY) via 4-tier strategy:
│      - Tier 1: PERMNO + exact date match
│      - Tier 2: CUSIP8 + date match
│      - Tier 3: Fuzzy match (>=92% similarity)
│      - Tier 4: Ticker match
│    • Generate descriptive stats (tier-specific)
│
├─ 1.3_BuildTenureMap.py
│  Input:  metadata_linked.parquet + speaker_data_*.parquet
│  Output: 4_Outputs/1.3_BuildTenureMap/tenure_monthly.parquet
│  Process:
│    • Track CEO tenure by company-month
│    • Resolve overlapping tenures
│    • Identify first CEOs
│    • Generate descriptive stats (tenure timeline)
│
└─ 1.4_AssembleManifest.py
   Input:  metadata_linked.parquet + tenure_monthly.parquet + speaker_data
   Output: 4_Outputs/1.4_AssembleManifest/master_sample_manifest.parquet
   Process:
     • Merge all datasets on unique call ID
     • Assign CEO and firm identifiers
     • Compute industry (FF12, FF48)
     • Final sample: ~286,652 calls, 1,200+ CEOs, 1,000+ firms
     • Generate descriptive stats (final manifest)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                STEP 2: TEXT PROCESSING (2_Text/)                            │
│           Objective: Build linguistic_variables.parquet                       │
└─────────────────────────────────────────────────────────────────────────────┘
│
├─ 2.1_TokenizeAndCount.py
│  Input:  master_sample_manifest.parquet + speaker_data_*.parquet
│          + Loughran-McDonald_MasterDictionary_1993-2024.csv
│  Output: 4_Outputs/2.1_TokenizeAndCount/raw_counts.parquet
│  Process:
│    • Tokenize Q&A text for each call
│    • Count LM dictionary word categories:
│      - Positive, Negative, Uncertainty, Litigious, Modal, Constraining
│    • Compute word_token counts per call
│    • Aggregate to call level
│    • Generate descriptive stats (tokenization metrics)
│
└─ 2.2_ConstructVariables.py
   Input:  raw_counts.parquet
   Output: 4_Outputs/2.2_ConstructVariables/linguistic_variables.parquet
   Process:
     • Construct key linguistic variables:
       - Manager_QA_Uncertainty_pct = Uncertainty / word_tokens
       - Manager_QA_Negative_pct = Negative / word_tokens
       - NetTone = (Positive - Negative) / word_tokens
       - Manager_QA_Constraining_pct, Manager_QA_Litigious_pct
     • Apply quality filters (minimum tokens, percentage ranges)
     • Generate descriptive stats (variable construction)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 3: FINANCIAL FEATURES (3_Financial/)                       │
│  Objectives: Build firm_controls.parquet & market_variables.parquet           │
└─────────────────────────────────────────────────────────────────────────────┘
│
├─ 3.1_FirmControls.py
│  Input:  master_sample_manifest.parquet + Compustat (comp_na_daily_all/)
│  Output: 4_Outputs/3.1_FirmControls/firm_controls.parquet
│  Process:
│    • Compute firm-level controls (lagged 1 fiscal year):
│      - Size = log(MarketCap)
│      - BM = BookValue / MarketCap
│      - Lev = TotalDebt / TotalAssets
│      - ROA = NetIncome / TotalAssets
│      - CurrentRatio = CurrentAssets / CurrentLiabilities
│      - RD_Intensity = R&D / Sales
│      - Volatility (firm-level)
│    • Winsorize at 1%/99%
│    • Generate descriptive stats (financial ratios)
│
├─ 3.2_MarketVariables.py
│  Input:  master_sample_manifest.parquet + CRSP_DSF/ + tr_ibes/
│  Output: 4_Outputs/3.2_MarketVariables/market_variables.parquet
│  Process:
│    • Compute market variables around call dates:
│      - StockRet = [t-2, t+2] cumulative return
│      - MarketRet = [t-2, t+2] market return
│      - Volatility = std of returns in window
│      - Delta = change in Amihud illiquidity
│    • Apply minimum window length (5 trading days)
│    • Generate descriptive stats (return windows)
│
└─ 3.3_EventFlags.py
   Input:  master_sample_manifest.parquet + SDC/ + CEO Dismissal Data
   Output: 4_Outputs/3.3_EventFlags/event_flags.parquet
   Process:
     • Identify takeover events (3-tier matching)
     • Flag CEO dismissal events
     • Create binary indicators:
       - Takeover (0/1)
       - TakeoverType (completed, pending, withdrawn)
     • Generate descriptive stats (event counts)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│            STEP 4: ECONOMETRIC ANALYSIS (4_Econometric/)                    │
│       Objectives: Estimate CEO clarity, liquidity, takeover models             │
└─────────────────────────────────────────────────────────────────────────────┘
│
├─ 4.1_EstimateCeoClarity.py (Baseline Model)
│  Input:  master_sample_manifest.parquet + linguistic_variables.parquet
│          + firm_controls.parquet + market_variables.parquet
│  Output: 4_Outputs/4.1_EstimateCeoClarity/
│          └─ ceo_clarity_scores.parquet (CEO fixed effects)
│          └─ regression_results.csv
│          └─ table_ceo_clarity.tex (LaTeX table)
│  Process:
│    • Estimate: Manager_QA_Uncertainty_pct = α + ClarityCEO + X + FE + ε
│    • Fixed effects: CEO × Year, Industry × Year
│    • Clusters: Firm level
│    • Output: ClarityCEO (CEO-specific intercept)
│    • Generate descriptive stats (model diagnostics)
│
├─ 4.1.1_EstimateCeoClarity_CeoSpecific.py
│  Input:  Same as 4.1 + CEO-specific controls (tenure, age)
│  Output: 4_Outputs/4.1.1_EstimateCeoClarity_CeoSpecific/
│          └─ ceo_clarity_ceo_specific.parquet
│          └─ table_ceo_clarity_ceo_specific.tex
│  Process:
│    • Same model with CEO tenure and age controls
│    • Assess robustness to CEO characteristics
│    • Generate descriptive stats
│
├─ 4.1.2_EstimateCeoClarity_Extended.py
│  Input:  Same as 4.1 + extended controls (board, governance)
│  Output: 4_Outputs/4.1.2_EstimateCeoClarity_Extended/
│          └─ ceo_clarity_extended.parquet
│          └─ table_ceo_clarity_extended.tex
│  Process:
│    • Baseline + board independence, ownership, tenure controls
│    • Model comparison (AIC, BIC)
│    • Generate descriptive stats
│
├─ 4.1.3_EstimateCeoClarity_Regime.py
│  Input:  Same as 4.1
│  Output: 4_Outputs/4.1.3_EstimateCeoClarity_Regime/
│          └─ regime_clarity_scores.parquet
│          └─ table_regime_clarity.tex
│  Process:
│    • Estimate: NonCEO_Manager_QA_Uncertainty_pct = α + ClarityRegime + X + FE + ε
│    • ClarityRegime captures firm-level communication style
│    • Generate descriptive stats
│
├─ 4.1.4_EstimateCeoTone.py
│  Input:  Same as 4.1
│  Output: 4_Outputs/4.1.4_EstimateCeoTone/
│          └─ ceo_tone_scores.parquet
│          └─ table_ceo_tone.tex
│  Process:
│    • Estimate: NetTone = α + ClarityTone + X + FE + ε
│    • Separate clarity construct from tone
│    • Generate descriptive stats
│
├─ 4.2_LiquidityRegressions.py (IV Analysis)
│  Input:  ceo_clarity_scores.parquet + market_variables.parquet
│          + CCCL instrument/ (industry-level regulation changes)
│  Output: 4_Outputs/4.2_LiquidityRegressions/
│          └─ liquidity_iv_results.csv
│          └─ table_liquidity_iv.tex
│  Process:
│    • First stage: ClarityCEO = π0 + π1 * IV + X + FE + ν
│      (IV = CCCL instrument, industry-level)
│    • Second stage: ΔAmihud = β0 + β1 * ClarityCEO + X + FE + ε
│    • Check first-stage F-stat > 10 (strong instrument)
│    • Compare OLS vs IV estimates
│    • Generate descriptive stats (first/second stage)
│
└─ 4.3_TakeoverHazards.py
   Input:  ceo_clarity_scores.parquet + event_flags.parquet
          + firm_controls.parquet
   Output: 4_Outputs/4.3_TakeoverHazards/
           └─ takeover_hazard_results.csv
           └─ table_takeover_hazards.tex
   Process:
     • Estimate Cox proportional hazards model:
       - h(t) = h0(t) * exp(γ1 * ClarityCEO + X)
     • Fine-Gray competing risks model (if needed)
     • Output hazard ratios (exp(γ1))
     • Test: Does CEO clarity reduce takeover hazard?
     • Generate descriptive stats (survival analysis)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FINAL OUTPUTS (Paper-Ready Tables)                        │
└─────────────────────────────────────────────────────────────────────────────┘
│
├─ Table 1: CEO Clarity Measurement (4.1)
│  - ClarityCEO coefficient, CEO FE, R², N
│  - Variable: Manager_QA_Uncertainty_pct
│
├─ Table 2: CEO Clarity Robustness (4.1.1, 4.1.2)
│  - Baseline vs CEO-specific vs Extended
│  - Controls comparison
│
├─ Table 3: Firm Communication Regime (4.1.3)
│  - ClarityRegime coefficient
│  - Variable: NonCEO_Manager_QA_Uncertainty_pct
│
├─ Table 4: CEO Tone (4.1.4)
│  - ClarityTone coefficient
│  - Variable: NetTone
│
├─ Table 5: Liquidity Effects - IV Analysis (4.2)
│  - First stage: ClarityCEO ~ IV
│  - Second stage: ΔAmihud ~ ClarityCEO
│  - F-stat, IV estimate, OLS comparison
│
└─ Table 6: Takeover Hazards (4.3)
   - Hazard ratios for ClarityCEO
   - Concordanace, event counts
```

### Key Dependencies

```
Step 1 (Sample) → All downstream steps
  ├─ master_sample_manifest.parquet ←──┐
  │                                     │
Step 2 (Text) ───────────────────────────┤
  └─ linguistic_variables.parquet ──────┤
                                        │
Step 3 (Financial) ──────────────────────┤
  ├─ firm_controls.parquet ─────────────┼───┐
  ├─ market_variables.parquet ─────────┼───┤
  └─ event_flags.parquet ──────────────┼───┤
                                        │   │
Step 4 (Econometric) ◄──────────────────┘   │
  └─ Reads all above datasets              │
                                            │
Final Outputs ◄─────────────────────────────┘
```

### Sample Statistics

| Metric | Value |
|--------|-------|
| Total Earnings Calls (2002-2018) | ~286,652 |
| Unique CEOs | ~1,200+ |
| Unique Firms | ~1,000+ |
| Sample Period | 2002-2018 |
| Average Q&A Tokens per Call | ~1,000-2,000 |
| ClarityCEO Distribution | Mean=0, SD≈0.15 (after standardization) |

## Program-to-Output Mapping

Comprehensive mapping of each processing script to its output files and purpose in the research workflow. All scripts are run as Python modules using `python -m f1d.<module_path>`.

### Step 1: Sample Construction (f1d.sample)

| Module | Stage | Output Files | Purpose / Paper Output |
|--------|--------|--------------|----------------------|
| **f1d.sample.1.0_BuildSampleManifest** | Step 1 (Orchestrator) | `master_sample_manifest.parquet` | Orchestrates 1.1-1.4; produces final sample manifest defining analysis universe |
| **f1d.sample.1.1_CleanMetadata** | Step 1.1 | `metadata_cleaned.parquet`, `variable_reference.csv` | Deduplicates Unified-info, filters for earnings calls 2002-2018, resolves file_name collisions |
| **f1d.sample.1.2_LinkEntities** | Step 1.2 | `metadata_linked.parquet`, `variable_reference.csv` | 4-tier entity resolution: PERMNO+date, CUSIP8+date, fuzzy name match; adds GVKEY, FF12/FF48 industries via CCM |
| **f1d.sample.1.3_BuildTenureMap** | Step 1.3 | `tenure_monthly.parquet`, `variable_reference.csv` | Builds monthly CEO tenure panel from Execucomp; links predecessor CEOs via becameceo/leftofc dates |
| **f1d.sample.1.4_AssembleManifest** | Step 1.4 | `master_sample_manifest.parquet`, `variable_reference.csv` | Joins metadata with CEO tenure panel, applies minimum 5-call threshold per CEO; final universe definition |

### Step 2: Text Processing (f1d.text)

| Module | Stage | Output Files | Purpose / Paper Output |
|--------|--------|--------------|----------------------|
| **f1d.text.tokenize_and_count** | Step 2.1 | `linguistic_counts_{year}.parquet` (per year 2002-2018) | Tokenizes speaker text using Loughran-McDonald dictionary; counts 7 categories (Negative, Positive, Uncertainty, Litigious, Strong/Weak Modal, Constraining) per speaker; totals tokens |
| **f1d.text.construct_variables** | Step 2.2 | `linguistic_variables_{year}.parquet` (per year) | Flags speakers (Analyst, Manager, CEO) using role/employer/name matching; aggregates counts to weighted ratios by sample (Manager/CEO/NonCEO_Manager) and context (QA/Presentation/All); creates Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, etc. |
| **f1d.text.verify_step2** | Step 2.3 | Verification report (no data output) | Validates Step 2 outputs: checks file presence, variable completeness (Manager_QA_Uncertainty_pct), and missing value counts |

### Step 3: Financial Features (f1d.financial.v1)

| Module | Stage | Output Files | Purpose / Paper Output |
|--------|--------|--------------|----------------------|
| **f1d.financial.v1.3.0_BuildFinancialFeatures** | Step 3 (Orchestrator) | `firm_controls_{year}.parquet`, `market_variables_{year}.parquet`, `event_flags_{year}.parquet` | Orchestrates 3.1, 3.2, 3.3; produces all financial features in single timestamped output |
| **f1d.financial.v1.3.1_FirmControls** | Step 3.1 | `firm_controls_{year}.parquet` | Computes firm controls from Compustat: Size (ln assets), BM, Lev, ROA, EPS_Growth, CurrentRatio, RD_Intensity; computes earnings surprise decile (-5 to +5) from IBES; merges CCCL shift_intensity variants as competition instrument |
| **f1d.financial.v1.3.2_MarketVariables** | Step 3.2 | `market_variables_{year}.parquet` | Computes stock return (compound: prev_call+5d to call-5d), market return (VWRETD), volatility; computes liquidity measures: Amihud (|ret|/volume), Corwin-Schultz bid-ask spread, and event-minus-baseline deltas |
| **f1d.financial.v1.3.3_EventFlags** | Step 3.3 | `event_flags_{year}.parquet` | Computes takeover event flags from SDC M&A data: Takeover (1 if acquisition within 365 days), Takeover_Type (Uninvited/Friendly), Duration (quarters to event) |

### Step 4: Econometric Analysis (f1d.econometric.v1)

| Module | Stage | Output Files | Purpose / Paper Output |
|--------|--------|--------------|----------------------|
| **f1d.econometric.v1.4.1_EstimateManagerClarity** | Step 4.1 | `ceo_clarity_scores.parquet`, `regression_results_{sample}.txt`, `model_diagnostics.csv` | Estimates CEO fixed effects via OLS: Manager_QA_Uncertainty_pct ~ C(ceo_id) + controls (linguistic + firm) + C(year); runs 3 industry samples (Main, Finance, Utility); extracts gamma_i, standardizes to ClarityCEO = -gamma_i; produces paper's CEO clarity trait measure |
| **f1d.econometric.v1.4.1.1_EstimateCeoClarity** | Step 4.1.1 | `ceo_clarity_scores.parquet`, `regression_results_{sample}.txt` | CEO-specific version: CEO_QA_Uncertainty_pct ~ C(ceo_id) + controls; ClarityCEO trait measure for CEO-only analysis |
| **f1d.econometric.v1.4.1.2_EstimateCeoClarity_Extended** | Step 4.1.2 | Extended clarity estimates with additional controls | Extended model specification with additional control variables |
| **f1d.econometric.v1.4.1.3_EstimateCeoClarity_Regime** | Step 4.1.3 | Regime-based clarity estimates | Clarity measure specific to managerial regimes (excludes CEO) |
| **f1d.econometric.v1.4.1.4_EstimateCeoTone** | Step 4.1.4 | CEO tone estimates | Estimates CEO tone as alternative communication trait measure |
| **f1d.econometric.v1.4.2_LiquidityRegressions** | Step 4.2 | `first_stage_results.txt`, `ols_regime.txt`, `ols_ceo.txt`, `iv_regime.txt`, `iv_ceo.txt`, `model_diagnostics.csv` | Tests liquidity impact: Phase 1 (first-stage instrument validity: Q&A Uncertainty ~ CCCL shift_intensity_sale_ff48); Phase 2 (OLS): Delta_Amihud/Corwin-Schultz ~ Clarity + Q&A Uncertainty + controls; Phase 3 (2SLS): instruments Q&A Uncertainty; supports paper's liquidity regression tables (e.g., Table 3) |
| **f1d.econometric.v1.4.3_TakeoverHazards** | Step 4.3 | `cox_ph_all.txt`, `fine_gray_uninvited.txt`, `fine_gray_friendly.txt`, `hazard_ratios.csv`, `takeover_event_summary.csv` | Survival analysis: Model 1 (Cox PH: all takeovers), Model 2 (Fine-Gray: Uninvited/hostile+unsolicited), Model 3 (Fine-Gray: Friendly/neutral); ClarityCEO and Q&A Uncertainty predict hazard; supports paper's takeover hazard tables |
| **f1d.econometric.v1.4.4_GenerateSummaryStats** | Step 4.4 | `descriptive_statistics.csv`, `correlation_matrix.csv`, `panel_balance.csv`, `summary_report.md` | SUMM-01: Descriptive stats (N, Mean, SD, Min, P25, Median, P75, Max) for all variables; SUMM-02: Correlation matrix for key regression variables; SUMM-03: Panel balance diagnostics (firm-year coverage, time series); supports paper's Table 1 (sample characteristics) |

### Data Flow Summary

```
Step 1:  Unified-info → Sample Manifest (universe definition)
   ↓
Step 2:  Speaker text → Linguistic variables (Uncertainty measures)
   ↓
Step 3:  Compustat/IBES/CRSP/SDC/CCM → Financial controls
   ↓
Step 4:  Clarity estimation → Liquidity/Takeover regressions → Summary stats
```

### Running Scripts

All scripts are executed as Python modules using the `-m` flag:

```bash
# Sample construction
python -m f1d.sample.1.1_CleanMetadata
python -m f1d.sample.1.2_LinkEntities
python -m f1d.sample.1.3_BuildTenureMap
python -m f1d.sample.1.4_AssembleManifest

# Text processing
python -m f1d.text.tokenize_and_count
python -m f1d.text.construct_variables

# Financial features (V1)
python -m f1d.financial.v1.3.1_FirmControls
python -m f1d.financial.v1.3.2_MarketVariables
python -m f1d.financial.v1.3.3_EventFlags

# Econometric analysis (V1)
python -m f1d.econometric.v1.4.1_EstimateManagerClarity
python -m f1d.econometric.v1.4.2_LiquidityRegressions
python -m f1d.econometric.v1.4.3_TakeoverHazards

# V2 hypothesis testing
python -m f1d.financial.v2.3.1_H1Variables
python -m f1d.econometric.v2.4.1_H1CashHoldingsRegression
```

## Execution Instructions

This section provides step-by-step instructions for running the F1D Clarity Measure analysis pipeline.

### Prerequisites

#### Required Inputs

Ensure the following files are present in `1_Inputs/`:

- `Unified-info.parquet` - Main earnings call metadata
- `speaker_data_2002.parquet` through `speaker_data_2018.parquet` - Transcript data by year
- `Loughran-McDonald_MasterDictionary_1993-2024.csv` - Linguistic dictionary
- `CEO Dismissal Data 2021.02.03.xlsx` - CEO turnover data
- CRSP Compustat CCM linkage data (in `CRSPCompustat_CCM/`)
- CRSP daily stock returns (in `CRSP_DSF/`)
- Execucomp executive data (in `Execucomp/`)
- SDC merger data (in `SDC/`)
- Additional financial data: `comp_na_daily_all/`, `tr_ibes/`
- CCCL instrument data (in `CCCL instrument/`)

#### Install Dependencies

Create and activate a virtual environment, then install required packages:

```bash
pip install pandas numpy pyyaml scikit-learn lifelines
```

Or create a `requirements.txt` file:

```text
pandas>=2.0.0
numpy>=1.24.0
PyYAML>=6.0
scikit-learn>=1.3.0
lifelines>=0.28.0
```

Then install:

```bash
pip install -r requirements.txt
```

### Step-by-Step Execution

Run each script in order. All scripts read configuration from `config/project.yaml` and output to timestamped directories in `4_Outputs/`.

#### Step 1: Sample Preparation

**1.1 Clean Metadata & Event Filtering**
```bash
python -m f1d.sample.1.1_CleanMetadata
```
- Approximate runtime: 5-10 seconds
- Outputs: `4_Outputs/1.1_CleanMetadata/` → `metadata_cleaned.parquet`

**1.2 Link Entities**
```bash
python -m f1d.sample.1.2_LinkEntities
```
- Approximate runtime: 30-60 seconds
- Outputs: `4_Outputs/1.2_LinkEntities/` → `metadata_linked.parquet`

**1.3 Build Tenure Map**
```bash
python -m f1d.sample.1.3_BuildTenureMap
```
- Approximate runtime: 20-40 seconds
- Outputs: `4_Outputs/1.3_BuildTenureMap/` → `tenure_monthly.parquet`

**1.4 Assemble Manifest**
```bash
python -m f1d.sample.1.4_AssembleManifest
```
- Approximate runtime: 10-20 seconds
- Outputs: `4_Outputs/1.4_AssembleManifest/` → `master_sample_manifest.parquet`

#### Step 2: Text Processing

**2.1 Tokenize and Count**
```bash
python -m f1d.text.tokenize_and_count
```
- Approximate runtime: 2-3 minutes
- Outputs: `4_Outputs/2_Textual_Analysis/2.1_Tokenized/` → `linguistic_counts_YYYY.parquet` (one file per year, 2002-2018)

**2.2 Construct Variables**
```bash
python -m f1d.text.construct_variables
```
- Approximate runtime: 2-3 minutes
- Outputs: `4_Outputs/2_Textual_Analysis/2.2_Variables/` → `linguistic_variables_YYYY.parquet` (one file per year, 2002-2018)

**2.3 Verify Step 2**
```bash
python -m f1d.text.verify_step2
```
- Approximate runtime: 30-60 seconds
- Outputs: Logs only (verifies data integrity; no new output files)

#### Step 3: Financial Features

**3.0 Build Financial Features**
```bash
python -m f1d.financial.v1.3.0_BuildFinancialFeatures
```
- Approximate runtime: 5-10 minutes
- Note: This script orchestrates steps 3.1, 3.2, and 3.3
- Outputs: `4_Outputs/3_Financial_Features/` → multiple parquet files

**3.1 Firm Controls**
```bash
python -m f1d.financial.v1.3.1_FirmControls
```
- Approximate runtime: 3-5 minutes
- Outputs: `4_Outputs/3_Financial_Features/` → `firm_controls_YYYY.parquet`

**3.2 Market Variables**
```bash
python -m f1d.financial.v1.3.2_MarketVariables
```
- Approximate runtime: 2-3 minutes
- Outputs: `4_Outputs/3_Financial_Features/` → `market_variables_YYYY.parquet`

**3.3 Event Flags**
```bash
python -m f1d.financial.v1.3.3_EventFlags
```
- Approximate runtime: 1-2 minutes
- Outputs: `4_Outputs/3_Financial_Features/` → `event_flags_YYYY.parquet`

#### Step 4: Econometric Analysis

**4.1 Estimate CEO Clarity**
```bash
python -m f1d.econometric.v1.4.1_EstimateManagerClarity
```
- Approximate runtime: 2-3 minutes
- Outputs: `4_Outputs/4.1_CeoClarity/` → `ceo_clarity_scores.parquet`, regression results

**4.2 Liquidity Regressions**
```bash
python -m f1d.econometric.v1.4.2_LiquidityRegressions
```
- Approximate runtime: 1-2 minutes
- Outputs: `4_Outputs/4.2_LiquidityRegressions/` → regression results, diagnostics

**4.3 Takeover Hazards**
```bash
python -m f1d.econometric.v1.4.3_TakeoverHazards
```
- Approximate runtime: 30-60 seconds
- Outputs: `4_Outputs/4.3_TakeoverHazards/` → hazard models, event summaries

### Expected Outputs

#### Output Structure

All outputs are saved in `4_Outputs/` with timestamped subdirectories:

```
4_Outputs/
├── 1.1_CleanMetadata/
│   └── latest/              → symlink to most recent run
├── 1.2_LinkEntities/
│   └── latest/
├── 1.3_BuildTenureMap/
│   └── latest/
├── 1.4_AssembleManifest/
│   └── latest/
├── 2_Textual_Analysis/
│   ├── 2.1_Tokenized/
│   │   └── latest/
│   └── 2.2_Variables/
│       └── latest/
├── 3_Financial_Features/
│   └── latest/
├── 4.1_CeoClarity/
│   └── latest/
├── 4.2_LiquidityRegressions/
│   └── latest/
└── 4.3_TakeoverHazards/
    └── latest/
```

#### Key Output Files by Step

**Step 1 Outputs:**
- `metadata_cleaned.parquet` - Cleaned earnings call metadata (297,547 calls)
- `metadata_linked.parquet` - Entity-linked metadata
- `tenure_monthly.parquet` - CEO tenure panel
- `master_sample_manifest.parquet` - Final sample manifest

**Step 2 Outputs:**
- `linguistic_counts_YYYY.parquet` - Raw token counts per year (17 files)
- `linguistic_variables_YYYY.parquet` - Linguistic variables per year (17 files)

**Step 3 Outputs:**
- `firm_controls_YYYY.parquet` - Financial control variables (17 files)
- `market_variables_YYYY.parquet` - Market-level variables (17 files)
- `event_flags_YYYY.parquet` - Event indicator flags (17 files)

**Step 4 Outputs:**
- `ceo_clarity_scores.parquet` - CEO-level clarity scores
- `regression_results_main.txt` - Main regression results
- `regression_results_finance.txt` - Finance industry results
- `regression_results_utility.txt` - Utility industry results
- `cox_ph_all.txt` - Cox proportional hazards model
- `fine_gray_friendly.txt` - Fine-Gray competing risks (friendly)
- `fine_gray_uninvited.txt` - Fine-Gray competing risks (uninvited)
- `hazard_ratios.csv` - Hazard ratio summary

#### Log Files

All scripts write progress logs to `3_Logs/`:

```
3_Logs/
├── 1.1_CleanMetadata/
├── 1.2_LinkEntities/
├── 1.3_BuildTenureMap/
├── 1.4_AssembleManifest/
├── 2.1_TokenizeAndCount/
├── 2.2_ConstructVariables/
├── 2.3_VerifyStep2/
├── 3_Financial_Features/
├── 4.1_CeoClarity/
├── 4.2_LiquidityRegressions/
└── 4.3_TakeoverHazards/
```

Each log file includes:
- Script execution timestamp
- Git SHA (for reproducibility)
- Configuration snapshot
- Input file checksums
- Step-by-step progress output

### Notes

- **Total runtime:** Approximately 20-30 minutes on a standard laptop
- **Deterministic:** All scripts are configured to produce bitwise-identical outputs given the same inputs and configuration
- **No flags required:** All scripts run directly with default settings from `config/project.yaml`
- **Progress tracking:** Each script prints progress to both stdout and the log file
- **Latest symlinks:** Use `latest/` subdirectories to access the most recent outputs without needing to know the timestamp

### Troubleshooting

If you encounter errors:

1. Check that all required input files exist in `1_Inputs/`
2. Verify Python version is 3.13+
3. **If you see "ModuleNotFoundError: No module named 'f1d'"**, run `pip install -e .`
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
5. Review the log file in `3_Logs/<step_name>/` for detailed error messages
6. Verify `config/project.yaml` paths are correct

### Reproducibility

To ensure reproducibility:

- Use the exact same input files (check SHA256 hashes in log files)
- Run scripts with Python 3.13.5
- Use the same `config/project.yaml` configuration
- Scripts use pinned random seeds and single-threaded execution by default

## Variable Codebook

This document provides a comprehensive reference for all variables in the final analysis dataset. Variables are organized by their source and processing step.

### Summary

- **Total Observations**: 5,889 earnings calls
- **Total CEOs**: 2,457 unique CEOs
- **Total Firms**: 2,361 unique firms (gvkey)
- **Sample Period**: 2002-2018

### Variable Index

#### By Source

| Source | Variable Count |
|--------|---------------|
| Step 1: Sample Identifiers | 28 |
| Step 2: Text/Linguistic Variables | 72 |
| Step 3.1: Financial Controls | 13 |
| Step 3.2: Market Variables | 6 |
| Step 4: Model Variables | 13 |
| **Total** | **132** |

### Step 1: Sample Identifiers

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| file_name | String | Unique identifier for each transcript file | Step 1 | 5,889 unique values |
| company_name | String | Company name | Step 1 | From EventStudy metadata |
| start_date | Date | Earnings call date and time | Step 1 | 2002-01-01 to 2018-12-31 |
| event_type | Integer | Event type identifier | Step 1 | Earnings announcement event |
| event_type_name | String | Event type description | Step 1 | "Earnings Call" |
| call_desc | String | Call description | Step 1 | From EventStudy metadata |
| event_title | String | Event title | Step 1 | Company + date identifier |
| city | String | Location of event | Step 1 | From EventStudy metadata |
| processing_lag_hours | Float | Hours between event and processing | Step 1 | Time lag metric |
| business_quarter | Integer | Fiscal quarter (1-4) | Step 1 | Q1-Q4 |
| processing_quarter | Integer | Processing quarter identifier | Step 1 | Administrative field |
| late_arrival_flag | Integer | Flag for delayed data arrival | Step 1 | 0/1 |
| quarter_assigned | String | Quarter assigned to | Step 1 | Administrative field |
| panel_created_at | Date | Panel creation timestamp | Step 1 | Administrative field |
| source_file_year | Integer | Source file year | Step 1 | 2002-2018 |
| data_lineage_id | String | Data lineage identifier | Step 1 | Traceability |
| original_last_update | Date | Original record update date | Step 1 | From EventStudy |
| last_update | Date | Most recent update timestamp | Step 1 | From EventStudy |
| company_id | String | Company identifier | Step 1 | From EventStudy |
| cusip | String | CUSIP (8 digits) | Step 1 | 2,361 unique values |
| sedol | String | SEDOL code | Step 1 | From EventStudy |
| isin | String | ISIN code | Step 1 | From EventStudy |
| company_ticker | String | Stock ticker symbol | Step 1 | From EventStudy |
| permno | Integer | CRSP PERMNO | Step 1 | Linkage to CRSP data |
| match_type | String | Entity match method | Step 1 | Matching quality indicator |
| match_type_desc | String | Match type description | Step 1 | Quality description |
| data_quality_score | Float | Data quality assessment | Step 1 | Quality metric |
| validation_timestamp | Date | Validation timestamp | Step 1 | Administrative field |
| has_speaker_data | Integer | Flag for speaker data availability | Step 1 | 0/1 |
| speaker_record_count | Integer | Number of speaker segments | Step 1 | Count of segments |
| gvkey | String | Compustat GVKEY (6-digit, zero-padded) | Step 1 | 2,361 unique firms |
| conm | String | Company name (Compustat) | Step 1 | From Compustat |
| sic | Integer | SIC industry code (4-digit) | Step 1 | 100-9997 |
| link_method | String | Linkage method | Step 1 | CCM/CRSP linkage |
| link_quality | String | Linkage quality indicator | Step 1 | From CCM |
| sic_int | Integer | SIC code as integer | Step 1 | Numeric SIC |
| ff12_code | Integer | Fama-French 12-industry code | Step 1 | 1-12 |
| ff12_name | String | Fama-French 12-industry name | Step 1 | Industry classification |
| ff48_code | Integer | Fama-French 48-industry code | Step 1 | 1-48 |
| ff48_name | String | Fama-French 48-industry name | Step 1 | Industry classification |
| ceo_id | String | CEO identifier | Step 1 | 2,457 unique CEOs |
| ceo_name | String | CEO full name | Step 1 | From speaker data |
| prev_ceo_id | String | Previous CEO identifier | Step 1 | CEO succession tracking |
| prev_ceo_name | String | Previous CEO name | Step 1 | CEO succession tracking |
| year | Integer | Calendar year | Step 1 | 2002-2018 |

### Step 2: Text/Linguistic Variables

All linguistic variables are computed as **percentages of total tokens** in the specified text segment, based on the Loughran-McDonald Master Dictionary (1993-2024).

**Speaker Types:**
- `Manager`: All managerial speakers (including CEO)
- `CEO`: CEO only
- `NonCEO_Manager`: Managers excluding CEO
- `Analyst`: Financial analysts during Q&A
- `Entire`: All speakers combined

**Contexts:**
- `QA`: Question & Answer session
- `Pres`: Formal presentation
- `All`: Combined Q&A + Presentation

**Linguistic Categories:**
- `Negative`: Negative sentiment words
- `Positive`: Positive sentiment words
- `Uncertainty`: Uncertainty/hedging words
- `Litigious`: Legal/litigious language
- `Strong_Modal`: Strong modal verbs (must, shall, will)
- `Weak_Modal`: Weak modal verbs (could, might, may)
- `Constraining`: Constraining language

#### Manager Linguistic Variables

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| Manager_QA_Negative_pct | Continuous | % negative words in manager Q&A | Step 2.2 | Mean: 0.76, SD: 0.33, Range: 0-4.44 |
| Manager_QA_Positive_pct | Continuous | % positive words in manager Q&A | Step 2.2 | Mean: 1.19, SD: 0.46, Range: 0-11.11 |
| Manager_QA_Uncertainty_pct | Continuous | % uncertainty words in manager Q&A | Step 2.2 | Mean: 0.91, SD: 0.36, Range: 0-6.25 |
| Manager_QA_Litigious_pct | Continuous | % litigious words in manager Q&A | Step 2.2 | Mean: 0.15, SD: 0.20, Range: 0-2.83 |
| Manager_QA_Strong_Modal_pct | Continuous | % strong modal words in manager Q&A | Step 2.2 | Mean: 0.68, SD: 0.32, Range: 0-4.55 |
| Manager_QA_Weak_Modal_pct | Continuous | % weak modal words in manager Q&A | Step 2.2 | Mean: 0.37, SD: 0.22, Range: 0-6.25 |
| Manager_QA_Constraining_pct | Continuous | % constraining words in manager Q&A | Step 2.2 | Mean: 0.11, SD: 0.11, Range: 0-3.13 |
| Manager_Pres_Negative_pct | Continuous | % negative words in manager presentation | Step 2.2 | Mean: 0.88, SD: 0.48, Range: 0-4.30 |
| Manager_Pres_Positive_pct | Continuous | % positive words in manager presentation | Step 2.2 | Mean: 1.76, SD: 0.62, Range: 0-5.37 |
| Manager_Pres_Uncertainty_pct | Continuous | % uncertainty words in manager presentation | Step 2.2 | Mean: 0.88, SD: 0.38, Range: 0-5.59 |
| Manager_Pres_Litigious_pct | Continuous | % litigious words in manager presentation | Step 2.2 | Mean: 0.20, SD: 0.25, Range: 0-2.86 |
| Manager_Pres_Strong_Modal_pct | Continuous | % strong modal words in manager presentation | Step 2.2 | Mean: 0.65, SD: 0.27, Range: 0-2.61 |
| Manager_Pres_Weak_Modal_pct | Continuous | % weak modal words in manager presentation | Step 2.2 | Mean: 0.24, SD: 0.15, Range: 0-2.72 |
| Manager_Pres_Constraining_pct | Continuous | % constraining words in manager presentation | Step 2.2 | Mean: 0.13, SD: 0.11, Range: 0-0.95 |
| Manager_All_Negative_pct | Continuous | % negative words (all manager segments) | Step 2.2 | Mean: 0.82, SD: 0.33, Range: 0-3.57 |
| Manager_All_Positive_pct | Continuous | % positive words (all manager segments) | Step 2.2 | Mean: 1.47, SD: 0.44, Range: 0.23-4.14 |
| Manager_All_Uncertainty_pct | Continuous | % uncertainty words (all manager segments) | Step 2.2 | Mean: 0.89, SD: 0.27, Range: 0.14-3.24 |
| Manager_All_Litigious_pct | Continuous | % litigious words (all manager segments) | Step 2.2 | Mean: 0.17, SD: 0.19, Range: 0-2.12 |
| Manager_All_Strong_Modal_pct | Continuous | % strong modal words (all manager segments) | Step 2.2 | Mean: 0.66, SD: 0.22, Range: 0.05-1.99 |
| Manager_All_Weak_Modal_pct | Continuous | % weak modal words (all manager segments) | Step 2.2 | Mean: 0.31, SD: 0.13, Range: 0-1.39 |
| Manager_All_Constraining_pct | Continuous | % constraining words (all manager segments) | Step 2.2 | Mean: 0.12, SD: 0.08, Range: 0-0.69 |

#### CEO Linguistic Variables

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| CEO_QA_Negative_pct | Continuous | % negative words in CEO Q&A | Step 2.2 | N=4,127, Mean: 0.75, SD: 0.51, Range: 0-13.33 |
| CEO_QA_Positive_pct | Continuous | % positive words in CEO Q&A | Step 2.2 | Mean: 1.32, SD: 0.87, Range: 0-40.00 |
| CEO_QA_Uncertainty_pct | Continuous | % uncertainty words in CEO Q&A | Step 2.2 | Mean: 0.87, SD: 0.48, Range: 0-7.41 |
| CEO_QA_Litigious_pct | Continuous | % litigious words in CEO Q&A | Step 2.2 | Mean: 0.14, SD: 0.23, Range: 0-3.96 |
| CEO_QA_Strong_Modal_pct | Continuous | % strong modal words in CEO Q&A | Step 2.2 | Mean: 0.69, SD: 0.46, Range: 0-8.24 |
| CEO_QA_Weak_Modal_pct | Continuous | % weak modal words in CEO Q&A | Step 2.2 | Mean: 0.38, SD: 0.33, Range: 0-7.41 |
| CEO_QA_Constraining_pct | Continuous | % constraining words in CEO Q&A | Step 2.2 | Mean: 0.11, SD: 0.15, Range: 0-3.13 |
| CEO_Pres_Negative_pct | Continuous | % negative words in CEO presentation | Step 2.2 | N=3,998, Mean: 0.84, SD: 0.57, Range: 0-4.43 |
| CEO_Pres_Positive_pct | Continuous | % positive words in CEO presentation | Step 2.2 | Mean: 2.28, SD: 0.93, Range: 0-7.64 |
| CEO_Pres_Uncertainty_pct | Continuous | % uncertainty words in CEO presentation | Step 2.2 | Mean: 0.70, SD: 0.42, Range: 0-3.41 |
| CEO_Pres_Litigious_pct | Continuous | % litigious words in CEO presentation | Step 2.2 | Mean: 0.17, SD: 0.29, Range: 0-3.63 |
| CEO_Pres_Strong_Modal_pct | Continuous | % strong modal words in CEO presentation | Step 2.2 | Mean: 0.79, SD: 0.45, Range: 0-5.71 |
| CEO_Pres_Weak_Modal_pct | Continuous | % weak modal words in CEO presentation | Step 2.2 | Mean: 0.21, SD: 0.19, Range: 0-2.86 |
| CEO_Pres_Constraining_pct | Continuous | % constraining words in CEO presentation | Step 2.2 | Mean: 0.12, SD: 0.14, Range: 0-1.52 |
| CEO_All_Negative_pct | Continuous | % negative words (all CEO segments) | Step 2.2 | N=4,172, Mean: 0.79, SD: 0.40, Range: 0-5.00 |
| CEO_All_Positive_pct | Continuous | % positive words (all CEO segments) | Step 2.2 | Mean: 1.75, SD: 0.65, Range: 0-5.57 |
| CEO_All_Uncertainty_pct | Continuous | % uncertainty words (all CEO segments) | Step 2.2 | Mean: 0.79, SD: 0.33, Range: 0-2.86 |
| CEO_All_Litigious_pct | Continuous | % litigious words (all CEO segments) | Step 2.2 | Mean: 0.15, SD: 0.22, Range: 0-2.44 |
| CEO_All_Strong_Modal_pct | Continuous | % strong modal words (all CEO segments) | Step 2.2 | Mean: 0.73, SD: 0.33, Range: 0-4.69 |
| CEO_All_Weak_Modal_pct | Continuous | % weak modal words (all CEO segments) | Step 2.2 | Mean: 0.30, SD: 0.18, Range: 0-2.17 |
| CEO_All_Constraining_pct | Continuous | % constraining words (all CEO segments) | Step 2.2 | Mean: 0.11, SD: 0.10, Range: 0-1.21 |

#### Analyst Linguistic Variables

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| Analyst_QA_Negative_pct | Continuous | % negative words in analyst Q&A | Step 2.2 | Mean: 1.29, SD: 0.48, Range: 0-6.10 |
| Analyst_QA_Positive_pct | Continuous | % positive words in analyst Q&A | Step 2.2 | Mean: 1.01, SD: 0.45, Range: 0-5.36 |
| Analyst_QA_Uncertainty_pct | Continuous | % uncertainty words in analyst Q&A | Step 2.2 | Mean: 1.42, SD: 0.49, Range: 0-5.45 |
| Analyst_QA_Litigious_pct | Continuous | % litigious words in analyst Q&A | Step 2.2 | Mean: 0.14, SD: 0.21, Range: 0-2.30 |
| Analyst_QA_Strong_Modal_pct | Continuous | % strong modal words in analyst Q&A | Step 2.2 | Mean: 0.24, SD: 0.20, Range: 0-2.54 |
| Analyst_QA_Weak_Modal_pct | Continuous | % weak modal words in analyst Q&A | Step 2.2 | Mean: 0.96, SD: 0.43, Range: 0-5.13 |
| Analyst_QA_Constraining_pct | Continuous | % constraining words in analyst Q&A | Step 2.2 | Mean: 0.05, SD: 0.09, Range: 0-1.28 |
| Analyst_Pres_Negative_pct | Continuous | % negative words in analyst presentation | Step 2.2 | N=27, Mean: 0.77, SD: 0.61, Range: 0-2.33 |
| Analyst_Pres_Positive_pct | Continuous | % positive words in analyst presentation | Step 2.2 | Mean: 0.83, SD: 0.61, Range: 0-2.25 |
| Analyst_Pres_Uncertainty_pct | Continuous | % uncertainty words in analyst presentation | Step 2.2 | Mean: 1.19, SD: 1.19, Range: 0-4.65 |
| Analyst_Pres_Litigious_pct | Continuous | % litigious words in analyst presentation | Step 2.2 | Mean: 0.24, SD: 0.35, Range: 0-1.22 |
| Analyst_Pres_Strong_Modal_pct | Continuous | % strong modal words in analyst presentation | Step 2.2 | Mean: 0.84, SD: 0.56, Range: 0-2.16 |
| Analyst_Pres_Weak_Modal_pct | Continuous | % weak modal words in analyst presentation | Step 2.2 | Mean: 0.45, SD: 0.52, Range: 0-2.07 |
| Analyst_Pres_Constraining_pct | Continuous | % constraining words in analyst presentation | Step 2.2 | Mean: 0.10, SD: 0.23, Range: 0-1.01 |
| Analyst_All_Negative_pct | Continuous | % negative words (all analyst segments) | Step 2.2 | Mean: 1.29, SD: 0.48, Range: 0-6.10 |
| Analyst_All_Positive_pct | Continuous | % positive words (all analyst segments) | Step 2.2 | Mean: 1.01, SD: 0.45, Range: 0-5.36 |
| Analyst_All_Uncertainty_pct | Continuous | % uncertainty words (all analyst segments) | Step 2.2 | Mean: 1.42, SD: 0.49, Range: 0-5.45 |
| Analyst_All_Litigious_pct | Continuous | % litigious words (all analyst segments) | Step 2.2 | Mean: 0.14, SD: 0.21, Range: 0-2.30 |
| Analyst_All_Strong_Modal_pct | Continuous | % strong modal words (all analyst segments) | Step 2.2 | Mean: 0.24, SD: 0.20, Range: 0-2.54 |
| Analyst_All_Weak_Modal_pct | Continuous | % weak modal words (all analyst segments) | Step 2.2 | Mean: 0.96, SD: 0.43, Range: 0-5.13 |
| Analyst_All_Constraining_pct | Continuous | % constraining words (all analyst segments) | Step 2.2 | Mean: 0.05, SD: 0.09, Range: 0-1.28 |

#### Non-CEO Manager Linguistic Variables

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| NonCEO_Manager_QA_Negative_pct | Continuous | % negative words in non-CEO manager Q&A | Step 2.2 | Mean: 0.75, SD: 0.46, Range: 0-5.71 |
| NonCEO_Manager_QA_Positive_pct | Continuous | % positive words in non-CEO manager Q&A | Step 2.2 | Mean: 1.04, SD: 0.59, Range: 0-11.11 |
| NonCEO_Manager_QA_Uncertainty_pct | Continuous | % uncertainty words in non-CEO manager Q&A | Step 2.2 | Mean: 0.97, SD: 0.88, Range: 0-50.00 |
| NonCEO_Manager_QA_Litigious_pct | Continuous | % litigious words in non-CEO manager Q&A | Step 2.2 | Mean: 0.16, SD: 0.33, Range: 0-14.29 |
| NonCEO_Manager_QA_Strong_Modal_pct | Continuous | % strong modal words in non-CEO manager Q&A | Step 2.2 | Mean: 0.67, SD: 0.45, Range: 0-7.14 |
| NonCEO_Manager_QA_Weak_Modal_pct | Continuous | % weak modal words in non-CEO manager Q&A | Step 2.2 | Mean: 0.36, SD: 0.31, Range: 0-6.59 |
| NonCEO_Manager_QA_Constraining_pct | Continuous | % constraining words in non-CEO manager Q&A | Step 2.2 | Mean: 0.12, SD: 0.17, Range: 0-4.55 |
| NonCEO_Manager_Pres_Negative_pct | Continuous | % negative words in non-CEO manager presentation | Step 2.2 | Mean: 0.89, SD: 0.55, Range: 0-4.65 |
| NonCEO_Manager_Pres_Positive_pct | Continuous | % positive words in non-CEO manager presentation | Step 2.2 | Mean: 1.44, SD: 0.85, Range: 0-20.00 |
| NonCEO_Manager_Pres_Uncertainty_pct | Continuous | % uncertainty words in non-CEO manager presentation | Step 2.2 | Mean: 1.04, SD: 0.71, Range: 0-9.20 |
| NonCEO_Manager_Pres_Litigious_pct | Continuous | % litigious words in non-CEO manager presentation | Step 2.2 | Mean: 0.21, SD: 0.28, Range: 0-3.61 |
| NonCEO_Manager_Pres_Strong_Modal_pct | Continuous | % strong modal words in non-CEO manager presentation | Step 2.2 | Mean: 0.61, SD: 0.37, Range: 0-4.28 |
| NonCEO_Manager_Pres_Weak_Modal_pct | Continuous | % weak modal words in non-CEO manager presentation | Step 2.2 | Mean: 0.28, SD: 0.26, Range: 0-2.80 |
| NonCEO_Manager_Pres_Constraining_pct | Continuous | % constraining words in non-CEO manager presentation | Step 2.2 | Mean: 0.13, SD: 0.14, Range: 0-2.54 |
| NonCEO_Manager_All_Negative_pct | Continuous | % negative words (all non-CEO manager segments) | Step 2.2 | Mean: 0.83, SD: 0.42, Range: 0-5.71 |
| NonCEO_Manager_All_Positive_pct | Continuous | % positive words (all non-CEO manager segments) | Step 2.2 | Mean: 1.25, SD: 0.53, Range: 0-4.14 |
| NonCEO_Manager_All_Uncertainty_pct | Continuous | % uncertainty words (all non-CEO manager segments) | Step 2.2 | Mean: 0.99, SD: 0.46, Range: 0-7.14 |
| NonCEO_Manager_All_Litigious_pct | Continuous | % litigious words (all non-CEO manager segments) | Step 2.2 | Mean: 0.18, SD: 0.23, Range: 0-3.05 |
| NonCEO_Manager_All_Strong_Modal_pct | Continuous | % strong modal words (all non-CEO manager segments) | Step 2.2 | Mean: 0.63, SD: 0.32, Range: 0-7.14 |
| NonCEO_Manager_All_Weak_Modal_pct | Continuous | % weak modal words (all non-CEO manager segments) | Step 2.2 | Mean: 0.31, SD: 0.21, Range: 0-4.17 |
| NonCEO_Manager_All_Constraining_pct | Continuous | % constraining words (all non-CEO manager segments) | Step 2.2 | Mean: 0.13, SD: 0.12, Range: 0-2.54 |

#### Entire Transcript Linguistic Variables

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| Entire_QA_Negative_pct | Continuous | % negative words in Q&A (all speakers) | Step 2.2 | Mean: 1.11, SD: 0.35, Range: 0.25-3.85 |
| Entire_QA_Positive_pct | Continuous | % positive words in Q&A (all speakers) | Step 2.2 | Mean: 1.09, SD: 0.34, Range: 0-5.16 |
| Entire_QA_Uncertainty_pct | Continuous | % uncertainty words in Q&A (all speakers) | Step 2.2 | Mean: 1.06, SD: 0.28, Range: 0.20-2.96 |
| Entire_QA_Litigious_pct | Continuous | % litigious words in Q&A (all speakers) | Step 2.2 | Mean: 0.14, SD: 0.17, Range: 0-2.00 |
| Entire_QA_Strong_Modal_pct | Continuous | % strong modal words in Q&A (all speakers) | Step 2.2 | Mean: 0.55, SD: 0.22, Range: 0-2.04 |
| Entire_QA_Weak_Modal_pct | Continuous | % weak modal words in Q&A (all speakers) | Step 2.2 | Mean: 0.57, SD: 0.19, Range: 0-2.53 |
| Entire_QA_Constraining_pct | Continuous | % constraining words in Q&A (all speakers) | Step 2.2 | Mean: 0.09, SD: 0.08, Range: 0-0.68 |
| Entire_Pres_Negative_pct | Continuous | % negative words in presentation (all speakers) | Step 2.2 | Mean: 0.90, SD: 0.45, Range: 0.06-3.63 |
| Entire_Pres_Positive_pct | Continuous | % positive words in presentation (all speakers) | Step 2.2 | Mean: 1.71, SD: 0.58, Range: 0-4.31 |
| Entire_Pres_Uncertainty_pct | Continuous | % uncertainty words in presentation (all speakers) | Step 2.2 | Mean: 0.92, SD: 0.36, Range: 0.13-5.15 |
| Entire_Pres_Litigious_pct | Continuous | % litigious words in presentation (all speakers) | Step 2.2 | Mean: 0.20, SD: 0.24, Range: 0-2.56 |
| Entire_Pres_Strong_Modal_pct | Continuous | % strong modal words in presentation (all speakers) | Step 2.2 | Mean: 0.69, SD: 0.25, Range: 0-2.03 |
| Entire_Pres_Weak_Modal_pct | Continuous | % weak modal words in presentation (all speakers) | Step 2.2 | Mean: 0.27, SD: 0.15, Range: 0-2.58 |
| Entire_Pres_Constraining_pct | Continuous | % constraining words in presentation (all speakers) | Step 2.2 | Mean: 0.14, SD: 0.10, Range: 0-0.93 |
| Entire_All_Negative_pct | Continuous | % negative words (all segments, all speakers) | Step 2.2 | Mean: 1.02, SD: 0.32, Range: 0.23-3.17 |
| Entire_All_Positive_pct | Continuous | % positive words (all segments, all speakers) | Step 2.2 | Mean: 1.34, SD: 0.37, Range: 0.34-3.23 |
| Entire_All_Uncertainty_pct | Continuous | % uncertainty words (all segments, all speakers) | Step 2.2 | Mean: 0.99, SD: 0.23, Range: 0.30-2.87 |
| Entire_All_Litigious_pct | Continuous | % litigious words (all segments, all speakers) | Step 2.2 | Mean: 0.17, SD: 0.18, Range: 0-1.99 |
| Entire_All_Strong_Modal_pct | Continuous | % strong modal words (all segments, all speakers) | Step 2.2 | Mean: 0.60, SD: 0.18, Range: 0.09-1.58 |
| Entire_All_Weak_Modal_pct | Continuous | % weak modal words (all segments, all speakers) | Step 2.2 | Mean: 0.44, SD: 0.13, Range: 0.08-1.27 |
| Entire_All_Constraining_pct | Continuous | % constraining words (all segments, all speakers) | Step 2.2 | Mean: 0.11, SD: 0.07, Range: 0-0.63 |

### Step 3.1: Financial Controls

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| Size | Continuous | Natural log of total assets (atq) | Step 3.1 | ln(atq), clipped at 1st/99th percentile |
| BM | Continuous | Book-to-market ratio | Step 3.1 | ceqq / (cshoq * prccq), clipped at 1st/99th percentile |
| Lev | Continuous | Leverage ratio | Step 3.1 | ltq / atq, clipped at 1st/99th percentile |
| ROA | Continuous | Return on assets | Step 3.1 | niq / atq, clipped at 1st/99th percentile |
| EPS_Growth | Continuous | Year-over-year EPS growth | Step 3.1 | (EPS - EPS_lag4) / |EPS_lag4|, clipped at 1st/99th percentile |
| CurrentRatio | Continuous | Current ratio (liquidity) | Step 3.1 | actq / lctq, clipped at 1st/99th percentile |
| RD_Intensity | Continuous | R&D intensity | Step 3.1 | xrdq / atq (missing R&D = 0), clipped at 1st/99th percentile |
| SurpDec | Categorical | Earnings surprise decile | Step 3.1 | -5 to +5, ranked within quarter |
| ActualEPS | Continuous | Actual EPS from IBES | Step 3.1 | Matched within ±45 days of call |
| ForecastEPS | Continuous | Mean forecast EPS from IBES | Step 3.1 | Forecast made before call date |
| surprise_raw | Continuous | Raw earnings surprise | Step 3.1 | ActualEPS - ForecastEPS |
| shift_intensity_sale_ff12 | Continuous | Competition instrument (sales, FF12) | Step 3.1 | From CCCL instrument |
| shift_intensity_mkvalt_ff12 | Continuous | Competition instrument (market cap, FF12) | Step 3.1 | From CCCL instrument |
| shift_intensity_sale_ff48 | Continuous | Competition instrument (sales, FF48) | Step 3.1 | From CCCL instrument |
| shift_intensity_mkvalt_ff48 | Continuous | Competition instrument (market cap, FF48) | Step 3.1 | From CCCL instrument |
| shift_intensity_sale_sic2 | Continuous | Competition instrument (sales, SIC2) | Step 3.1 | From CCCL instrument |
| shift_intensity_mkvalt_sic2 | Continuous | Competition instrument (market cap, SIC2) | Step 3.1 | From CCCL instrument |

**Notes on Financial Controls:**
- All Compustat controls matched using backward merge_asof (most recent quarter ≤ call date)
- EPS Growth requires 4-quarter lag (EPS_lag4)
- SurpDec ranked separately within each quarter across all firms
- CCCL instruments matched on gvkey and year
- Missing values indicate no available data for the time window

### Step 3.2: Market Variables

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| StockRet | Continuous | Stock return (compound, %) | Step 3.2 | Mean: 6.12%, SD: 18.80%, Range: -84.10% to +235.78% |
| MarketRet | Continuous | Value-weighted market return (%) | Step 3.2 | Mean: 3.87%, SD: 5.80%, Range: -23.82% to +47.09% |
| Volatility | Continuous | Annualized stock volatility (%) | Step 3.2 | Std(daily ret) × √252 × 100 |
| Amihud | Continuous | Illiquidity measure (event window) | Step 3.2 | Mean(|ret|/volume) × 1e6, window: [t-5d, t+5d] |
| Corwin_Schultz | Continuous | Bid-ask spread estimator (event) | Step 3.2 | High-low spread, window: [t-5d, t+5d] |
| Delta_Amihud | Continuous | Change in Amihud (event - baseline) | Step 3.2 | Event: [t-5d, t+5d], Baseline: [t-35d, t-6d] |
| Delta_Corwin_Schultz | Continuous | Change in Corwin-Schultz (event - baseline) | Step 3.2 | Event minus baseline window |

**Notes on Market Variables:**
- StockRet: Compound return from (prev_call + 5d) to (current_call - 5d)
- Minimum 10 trading days required for return calculation
- Amihud: Requires at least 5 observations and positive dollar volume
- Corwin-Schultz: Requires at least 5 observations with valid bid/ask
- Baseline window: 30 trading days before event window
- CRSP data linked via permno (direct or CCM fallback)

### Step 4: Model Variables (CEO Clarity)

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| ceo_id | String | CEO identifier | Step 1 | 2,457 unique CEOs |
| sample | Categorical | Industry sample classification | Step 4.1 | Main, Finance, or Utility (based on FF12) |
| gamma_i | Continuous | CEO fixed effect coefficient | Step 4.1 | From OLS: Manager_QA_Uncertainty_pct ~ C(ceo_id) + controls |
| ClarityCEO_raw | Continuous | Raw clarity score = -gamma_i | Step 4.1 | Negative of fixed effect |
| ClarityCEO | Continuous | Standardized clarity score | Step 4.1 | Z-score of ClarityCEO_raw (mean=0, SD=1) |
| n_calls | Integer | Number of calls per CEO (in sample) | Step 4.1 | CEOs with ≥5 calls included |
| avg_uncertainty | Continuous | Mean Manager_QA_Uncertainty_pct per CEO | Step 4.1 | Calculated from call-level data |
| std_uncertainty | Continuous | Std of Manager_QA_Uncertainty_pct per CEO | Step 4.1 | Calculated from call-level data |
| ceo_name | String | CEO full name | Step 1 | From speaker data |
| first_call_date | Date | First earnings call date for CEO | Step 4.1 | Min(start_date) per CEO |
| last_call_date | Date | Last earnings call date for CEO | Step 4.1 | Max(start_date) per CEO |
| n_firms | Integer | Number of unique firms (gvkey) per CEO | Step 4.1 | CEO firm transitions |

**Regression Specification:**
```
Manager_QA_Uncertainty_pct = α + γ_i·CEO_i + β₁·Manager_Pres_Uncertainty_pct
                            + β₂·Analyst_QA_Uncertainty_pct
                            + β₃·Entire_All_Negative_pct
                            + β₄·StockRet + β₅·MarketRet
                            + β₆·EPS_Growth + β₇·SurpDec
                            + δ_t·Year_t + ε_i,t
```

**Industry Samples:**
- **Main**: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
- **Finance**: FF12 code 11 (financial firms)
- **Utility**: FF12 code 8 (utility firms)

**Clarity Interpretation:**
- Higher ClarityCEO = CEO communicates with lower uncertainty (more clearly)
- ClarityCEO standardized: values > 0 = above-average clarity, values < 0 = below-average clarity
- Regression requires ≥5 calls per CEO for inclusion

### Variable Naming Conventions

#### Linguistic Variables
Pattern: `{Speaker}_{Context}_{Category}_pct`

- **Speaker**: Manager, CEO, NonCEO_Manager, Analyst, Entire
- **Context**: QA, Pres, All
- **Category**: Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining

#### Financial Variables
- Compustat: Based on quarterly data (atq, niq, ltq, etc.)
- IBES: Earnings forecasts and actuals
- CRSP: Daily stock returns and liquidity measures
- CCCL: Competition shift intensity instruments

#### Data Dictionary
| Abbreviation | Meaning |
|--------------|---------|
| atq | Total assets (quarterly, Compustat) |
| ceqq | Common equity (quarterly, Compustat) |
| cshoq | Common shares outstanding (quarterly, Compustat) |
| prccq | Price close (quarterly, Compustat) |
| ltq | Total liabilities (quarterly, Compustat) |
| niq | Net income (quarterly, Compustat) |
| epspxq | EPS (basic, excluding extraordinary items, Compustat) |
| actq | Current assets (quarterly, Compustat) |
| lctq | Current liabilities (quarterly, Compustat) |
| xrdq | R&D expenses (quarterly, Compustat) |
| RET | Daily return (CRSP) |
| VOL | Daily trading volume (CRSP) |
| VWRETD | Value-weighted market return (CRSP) |
| FF12 | Fama-French 12-industry classification |
| FF48 | Fama-French 48-industry classification |
| IBES | Institutional Brokers' Estimate System |
| CCM | CRSP-Compustat Merged database |
| CEO | Chief Executive Officer |
| QA | Question & Answer session |
| Pres | Formal presentation |
| pct | Percentage of total tokens |

## Data Sources

Comprehensive information about all data sources used in the F1D (Financial Clarity) pipeline, including access methods, licensing, and citation information.

### Earnings Calls / Transcripts

#### Source
- **Primary Provider:** Thomson Reuters StreetEvents (now part of LSEG - London Stock Exchange Group)
- **Alternative Providers:** FactSet, Bloomberg, Refinitiv
- **Access Platform:** WRDS (Wharton Research Data Services) may provide access

#### File Information
- **File Format:** Parquet (processed)
  - Metadata: `1_Inputs/Unified-info.parquet` (55 MB)
  - Transcripts: `1_Inputs/speaker_data_YYYY.parquet` (yearly files, 2002-2018)
- **Original Format:** Text files (.txt) or PDF documents
- **Years Covered:** 2002-2018

#### Dataset Statistics
- **Total Transcripts:** 428,330 unique calls (465,434 records with duplicates)
- **Total Speaker Turns:** ~4.2 billion turns across all years
- **Unique Companies:** 14,456
- **Unique Speakers:** ~55,000+ per year
- **Time Period:** 2002-03-11 to 2018-12-29

#### Access & Licensing
- **Access Required:** Commercial subscription to Thomson Reuters StreetEvents
- **WRDS Access:** Available through institutional WRDS subscription
- **Restrictions:**
  - Academic use only under institutional license
  - Redistribution prohibited
  - Citation required in publications
  - Data cannot be shared with third parties

#### Citation
If using earnings call transcripts, cite:
```
Thomson Reuters StreetEvents Database (accessed through WRDS).
Thomson Reuters, [access year].
```

### CRSP / Compustat

#### Source
- **CRSP (Center for Research in Security Prices):** University of Chicago Booth School of Business
- **Compustat (Standard & Poor's):** S&P Global Market Intelligence
- **Linkage:** CRSP/Compustat Merged Database (CCM) for matching identifiers
- **Access Platform:** WRDS (primary access point)

#### File Information
- **File Format:** Parquet
  - CCM Linkage: `1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet` (2.4 MB)
  - Daily Stock Returns: `1_Inputs/CRSP_DSF/` (directory)
  - Compustat Quarterly: Available via WRDS
- **Years Covered:** Varies by dataset (typically 1950s-present)

#### Dataset Statistics
- **Companies:** 40,000+ public companies (historical)
- **Securities:** 100,000+ securities
- **Time Period:** CRSP: 1925-present, Compustat: 1950-present
- **Update Frequency:** Daily (CRSP), Quarterly (Compustat)

#### Access & Licensing
- **Access Required:** Institutional WRDS subscription
- **Subscription Types:**
  - Academic institutions
  - Non-profit research organizations
  - Government agencies
- **Restrictions:**
  - Academic use only
  - Prohibited from redistributing data
  - Must acknowledge data source in publications
  - Cannot use for commercial profit-making activities

#### Citation
For CRSP:
```
CRSP US Stock Database. Center for Research in Security Prices,
Graduate School of Business, University of Chicago. [access year].
```

For Compustat:
```
Compustat North America. Standard & Poor's, [access year].
```

For CCM Linkage:
```
CRSP/Compustat Merged Database (CCM). Wharton Research Data Services (WRDS),
University of Pennsylvania. [access year].
```

### IBES (I/B/E/S)

#### Source
- **Provider:** Thomson Reuters (now LSEG)
- **Full Name:** Institutional Brokers' Estimate System
- **Access Platform:** WRDS

#### File Information
- **File Format:** Parquet
  - Dataset: `1_Inputs/tr_ibes/tr_ibes.parquet` (340 MB)
  - Variable Reference: `1_Inputs/tr_ibes/IBES_Variable_reference.csv`
- **Years Covered:** 1976-present (depending on subscription level)

#### Dataset Statistics
- **Companies:** 20,000+ covered companies
- **Analysts:** 10,000+ contributing analysts
- **Forecasts:** Millions of historical forecasts
- **Time Period:** 1976-present

#### Access & Licensing
- **Access Required:** WRDS subscription with IBES module
- **Restrictions:**
  - Academic use only
  - Redistribution prohibited
  - Citation required
  - Data embargo periods may apply

#### Citation
```
I/B/E/S International Inc. (Institutional Brokers' Estimate System).
Thomson Reuters, [access year].
```

### SDC M&A Database

#### Source
- **Provider:** Thomson Reuters (now LSEG)
- **Full Name:** Securities Data Company (SDC) Platinum M&A Database
- **Access Platform:** WRDS

#### File Information
- **File Format:** Parquet
  - Dataset: `1_Inputs/SDC/sdc-ma-merged.parquet` (25 MB)
  - Profile: `1_Inputs/SDC/sdc-ma-merged-profile.md`
- **Years Covered:** 1980s-present (varies by transaction type)

#### Dataset Statistics
- **Total Transactions:** 500,000+ M&A deals
- **Time Period:** 1980s-present
- **Coverage:** Global, with strong US coverage
- **Update Frequency:** Weekly/monthly updates

#### Access & Licensing
- **Access Required:** WRDS subscription with SDC module
- **Restrictions:**
  - Academic use only
  - Strict redistribution prohibitions
  - Confidentiality agreements often required
  - Cannot identify specific deals in publications without permission

#### Citation
```
Thomson Reuters SDC Platinum M&A Database.
Thomson Reuters, [access year].
```

### CCCL Instrument Data

#### Source
- **Primary Source:** SEC EDGAR (Electronic Data Gathering, Analysis, and Retrieval) system
- **Data Type:** SEC Comment Letters (CCCL - Correspondence Comment Letters)
- **Derived Instrument:** CCCL Shift-Intensity (industry-level regulatory scrutiny measure)
- **Purpose:** Exogenous instrument for CEO clarity in liquidity analysis

#### File Information
- **File Format:** Parquet
  - Dataset: `1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet` (15 MB)
  - Variable Reference: `1_Inputs/CCCL instrument/instrument_variable_reference.csv`
- **Years Covered:** 2005-2022 (constructed instrument)
- **Underlying Data:** SEC comment letters via EDGAR

#### Instrument Construction Logic

The CCCL Shift-Intensity instrument measures how regulatory scrutiny (via SEC comment letters) shifts attention away from focal firms:

```
Industry_Shift_Intensity = Σ(CCCL_count_j × Share_i,j)

Where:
- j = all other firms in the same industry (excluding firm i)
- Share_i,j = Firm i's market share relative to firm j
- Higher values = more regulatory attention on competitors (less on firm i)
```

**Interpretation:** High shift intensity suggests the SEC is focused on industry peers, potentially reducing scrutiny on the focal firm.

#### Dataset Statistics
- **Firms:** Thousands of public companies
- **Industries:** 12 FF12 industries, 48 FF48 industries
- **Years:** 2005-2022
- **Comment Letters:** Tens of thousands of SEC comment letters

#### Access & Licensing
- **Primary Data:** SEC EDGAR (publicly available, no license required)
- **Constructed Instrument:** Project-specific derivation (no license required)
- **Access:**
  - SEC comment letters: https://www.sec.gov/edgar/search-filings
  - Automated access via SEC API

#### Citation
For SEC EDGAR data:
```
U.S. Securities and Exchange Commission. EDGAR Database.
https://www.sec.gov/edgar/search-filings. [access year].
```

For the CCCL instrument construction (if referencing methodology):
```
[Author(s)]. [Paper Title]. [Journal], [Year].
```

### Loughran-McDonald Dictionary

#### Source
- **Developers:** Tim Loughran (University of Notre Dame) and Bill McDonald (University of Notre Dame)
- **Website:** https://www.nd.edu/~mcdonald/Word_Lists.html
- **Academic Repository:** SSRN, academic websites

#### File Information
- **File Format:** CSV
  - Dictionary: `1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv` (9 MB)
  - Profile: `1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024-profile.md`
- **Version:** 2024 (covers 1993-2024)
- **Total Words:** 86,553 words

#### Sentiment Word Counts
- **Negative:** 2,345 words (2.7%)
- **Positive:** 347 words (0.4%)
- **Uncertainty:** 297 words (0.3%)
- **Litigious:** 903 words (1.0%)
- **Strong Modal:** 19 words (0.02%)
- **Weak Modal:** 27 words (0.03%)
- **Constraining:** 184 words (0.2%)
- **Complexity:** 53 words (0.06%)
- **No sentiment flags:** 82,653 words (95.5%)

#### Access & Licensing
- **Cost:** Free (publicly available for academic use)
- **License:** Open for academic research; contact authors for commercial use
- **Access:** Download from University of Notre Dame website

#### Citation
**Required Citation:**
```
Loughran, Tim, and Bill McDonald. "When is a liability not a liability?
Textual analysis, dictionaries, and 10-Ks." The Journal of Finance 66.1 (2011): 35-65.
```

**For dictionary updates (2024 version):**
```
Loughran, Tim, and Bill McDonald. "Textual analysis in finance and
accounting: A survey." Journal of Accounting Literature 41 (2016): 19-53.
```

### Managerial Roles Dictionary

#### Source
- **Development:** Project-specific derivation
- **Purpose:** Identify managerial speakers in earnings call transcripts
- **Context:** F1D Clarity pipeline speaker classification

#### File Information
- **File Format:** Plain text (one keyword per line)
  - File: `1_Inputs/managerial_roles_extracted.txt`
  - Total keywords: 45 roles
- **Last Updated:** 2026-01-14

#### Role Categories

##### C-Level Executives
- CEO - Chief Executive Officer
- CFO - Chief Financial Officer
- COO - Chief Operating Officer
- CTO - Chief Technology Officer
- CIO - Chief Information Officer
- CMO - Chief Marketing Officer
- CAO - Chief Administrative Officer
- CCO - Chief Commercial/Communications Officer

##### Senior Leadership
- President, Chairman, Chairperson, Chairwoman
- EVP - Executive Vice President
- SVP - Senior Vice President
- VP - Vice President
- AVP - Assistant Vice President

##### Functional Leadership
- Director, Officer, Executive, Manager
- Head, Senior, Lead, Leader, Principal

##### Other Leadership Roles
- Treasurer, Secretary, Controller, Deputy
- MD - Managing Director, GM - General Manager
- Coordinator, Administrator, Superintendent
- Dean, Commissioner, Governor, Supervisor, Coach, Provost, Captain
- CHO - Chief Human Resources Officer
- Rector, CA - Controller/Compliance Officer

#### Access & Licensing
- **Cost:** Free (project-specific)
- **License:** No restrictions (custom keyword list)
- **Source:** Manually curated from earnings call transcript data

### Execucomp

#### Source
- **Provider:** Standard & Poor's (S&P Global Market Intelligence)
- **Full Name:** Execucomp - Executive Compensation Database
- **Access Platform:** WRDS

#### File Information
- **File Format:** Various (Parquet, CSV in pipeline)
- **Directory:** `1_Inputs/Execucomp/`
- **Years Covered:** 1992-present (depends on subscription)

#### Dataset Statistics
- **Companies:** 3,000+ public companies (S&P 500, S&P MidCap, S&P SmallCap)
- **Executives:** 50,000+ executives (top 5 named executive officers per company)
- **Time Period:** 1992-present
- **Update Frequency:** Quarterly/annual

#### Access & Licensing
- **Access Required:** WRDS subscription with Execucomp module
- **Restrictions:**
  - Academic use only
  - Redistribution prohibited
  - Citation required
  - Cannot identify individual executives in publications

#### Citation
```
Execucomp. Standard & Poor's, [access year].
```

### Data Access Summary

#### WRDS Access (Primary Data Sources)

| Dataset        | Access Type | License       | Academic Cost |
|----------------|-------------|---------------|---------------|
| CRSP           | WRDS        | Institutional | ~$5,000-15,000/year |
| Compustat      | WRDS        | Institutional | ~$5,000-15,000/year |
| CCM Linkage    | WRDS        | Institutional | Included above |
| IBES           | WRDS        | Institutional | ~$2,000-5,000/year |
| SDC            | WRDS        | Institutional | ~$3,000-7,000/year |
| Execucomp      | WRDS        | Institutional | ~$2,000-5,000/year |
| StreetEvents   | Direct      | Commercial    | ~$10,000-50,000/year |

#### Free/Public Data Sources

| Dataset                | Access    | License  | Cost |
|------------------------|-----------|----------|------|
| Loughran-McDonald      | Download  | Academic | Free |
| SEC EDGAR (CCCL)       | Web/API   | Public   | Free |
| Managerial Roles       | Custom    | None     | Free |

## Scaling and Performance

The F1D pipeline is designed for academic replication with current dataset sizes (~50K transcripts). For larger datasets or performance optimization, see [SCALING.md](SCALING.md).

**Quick Tips:**
- **Memory**: Minimum 8GB RAM, recommended 16GB RAM
- **Parallelization**: Set `thread_count: 4` in config for multi-core systems
- **Chunked Processing**: Enable throttling via `config/project.yaml > chunk_processing`
- **Monitoring**: Check `stats.json > memory_mb` for operation-level memory usage

**For 2x-10x datasets**: See [SCALING.md](SCALING.md) for configuration recommendations.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd F1D
   ```

2. **Install the package (required for f1d.shared.* imports):**
   ```bash
   pip install -e .
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install rapidfuzz>=3.14.0  # Optional but recommended
   ```

4. **Configure the pipeline:**
   Edit `config/project.yaml` to set paths, seeds, and processing parameters.

5. **Run a sample script:**
   ```bash
   python -m f1d.sample.1.1_CleanMetadata
   ```

> **Note:** The package must be installed in editable mode (`pip install -e .`) for scripts to use `from f1d.shared.*` imports. Without this step, you will see `ModuleNotFoundError: No module named 'f1d'`.

Output files are created in timestamped directories under `4_Outputs/`, with `latest/` symlinks pointing to the most recent run.

## Pipeline Structure

The pipeline follows a 4-stage structure implemented as an installable Python package:

1. **Sample** (`f1d.sample`): Build sample manifest, clean metadata, link entities, build tenure map
2. **Text** (`f1d.text`): Tokenize transcripts, construct text variables, verify outputs
3. **Financial** (`f1d.financial.v1` and `f1d.financial.v2`): Build financial features, firm controls, market variables, event flags
4. **Econometric** (`f1d.econometric.v1` and `f1d.econometric.v2`): Run regressions for CEO clarity, tone, liquidity effects

### Package Architecture

The pipeline uses a src-layout package structure (PyPA recommended):

- **Package root:** `src/f1d/` - Installable via `pip install -e .`
- **Shared utilities:** `src/f1d/shared/` - Reusable modules (config, logging, validation, data_loading, etc.)
- **Stage modules:**
  - `src/f1d/sample/` - Sample construction scripts
  - `src/f1d/text/` - Text processing scripts
  - `src/f1d/financial/v1/` - V1 financial feature scripts
  - `src/f1d/financial/v2/` - V2 hypothesis-specific variables
  - `src/f1d/econometric/v1/` - V1 econometric analysis
  - `src/f1d/econometric/v2/` - V2 hypothesis testing regressions

All imports use the `f1d.shared.*` namespace (e.g., `from f1d.shared.config import get_settings`). No `sys.path.insert()` or PYTHONPATH manipulation is required when the package is installed in editable mode.

## Architecture

The F1D pipeline uses a src-layout package structure following PyPA recommendations:

- **Package:** `f1d` - Installable via `pip install -e .`
- **Shared modules:** `f1d.shared.*` - Reusable utilities (config, logging, data validation, data_loading, output_schemas, etc.)
- **Stage scripts:**
  - `f1d.sample.*` - Sample construction (1.1-1.4)
  - `f1d.text.*` - Text processing (tokenize_and_count, construct_variables, verify_step2)
  - `f1d.financial.v1.*` - V1 financial features (3.1-3.3)
  - `f1d.financial.v2.*` - V2 hypothesis variables (3.1-3.13)
  - `f1d.econometric.v1.*` - V1 econometric analysis (4.1-4.4)
  - `f1d.econometric.v2.*` - V2 hypothesis testing (4.1-4.11)

All scripts use proper namespace imports:

```python
from f1d.shared.config import get_settings
from f1d.shared.logging import configure_logging
from f1d.shared.path_utils import ensure_output_dir
from f1d.shared.data_loading import safe_merge
from f1d.shared.output_schemas import validate_linguistic_variables
```

No `sys.path.insert()` or PYTHONPATH manipulation is required when the package is installed in editable mode.

### v6.3 Milestone

The v6.3 milestone (Phases 83-90) completed codebase concerns resolution:

- **Global state eliminated** from TakeoverHazards.py via parameter injection
- **Silent error handling fixed** with specific exceptions + logging
- **Output schema validation** with Pandera for all script outputs
- **181 new unit tests** for financial/econometric scripts (700+ total tests)
- **safe_merge()** with validation and logging for all merge operations
- **Dependabot configuration** for automated dependency updates
- **SECURITY.md** with security policy
- **Bandit SAST** in CI pipeline
- **Test coverage threshold** increased to 30%

See [.planning/ROADMAP.md](.planning/ROADMAP.md) for detailed phase-by-phase documentation.

## Documentation

- **[.planning/ROADMAP.md](.planning/ROADMAP.md)**: Project phases, plans, and progress tracking
- **[.planning/STATE.md](.planning/STATE.md)**: Current project position and accumulated decisions
- **[SCALING.md](SCALING.md)**: Pipeline scaling limits and performance optimization

## Output Reproducibility

Every script produces:
- **Console output**: Progress statistics (row counts, timing, missing values)
- **Stats files**: `stats.json` in output directories with detailed metrics
- **Checksums**: SHA-256 file checksums for output verification

All outputs are deterministic for a given input and configuration (see `config/project.yaml` for seed settings).

## License

This project is developed for academic research purposes. Data sources used in this pipeline (WRDS, CRSP, Compustat, IBES, SDC) have their own licensing terms and restrictions - see the Data Sources section for details.

**Source Code:** This pipeline is provided as-is for academic replication and research purposes.

**Data Access:** All financial data sources require institutional subscriptions through WRDS or commercial providers. See the Data Sources section for access requirements.

## Contact

For questions about the F1D pipeline methodology, replication assistance, or collaboration inquiries, please refer to the project documentation at `.planning/ROADMAP.md` and `.planning/STATE.md`.

**Data Access:** For questions about WRDS data access, contact your institution's WRDS representative or visit https://wrds.wharton.upenn.edu/.

**Issues:** For bugs, feature requests, or code issues, please use the project's issue tracker.
