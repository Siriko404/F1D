# F1D: CEO Communication Clarity and Market Outcomes

## Project Description

This project investigates how **CEO communication clarity** during earnings calls affects market outcomes such as **liquidity** and **takeover probability**. Using natural language processing on earnings call transcripts, we:

1. **Estimate CEO Clarity** as a persistent personal communication trait using fixed effects regression.
2. **Test market liquidity effects** — whether unclear communication increases bid-ask spreads and trading costs.
3. **Predict takeover probability** — whether uncertain CEOs become acquisition targets.

The analysis uses the Loughran-McDonald financial dictionary to quantify uncertainty, negativity, and other linguistic features in manager and analyst speech.

**Key Findings**: The dataset covers ~75,000 earnings calls from 2002-2018, linked to CRSP/Compustat financial data, Execucomp CEO identifiers, and SDC M&A events.

---

## Repository Structure

```
F1D/
├── 1_Inputs/               # Raw data files (CRSP, Compustat, SDC, transcripts)
├── 2_Scripts/              # All processing and analysis scripts
│   ├── 1_Sample/           # Step 1: Build sample manifest
│   ├── 2_Text/             # Step 2: Tokenize transcripts, compute linguistic variables
│   ├── 3_Financial/        # Step 3: Firm controls, market variables
│   └── 4_Econometric/      # Step 4: CEO Clarity, Liquidity, Takeover regressions
├── 3_Logs/                 # Timestamped execution logs per step
├── 4_Outputs/              # Timestamped output directories with 'latest' symlinks
│   ├── 1.0_BuildSampleManifest/
│   ├── 2_Textual_Analysis/
│   ├── 3_Financial_Features/
│   ├── 4.1_CeoClarity/, 4.1.1_..., 4.1.2_..., 4.1.3_..., 4.1.4_CeoTone/
│   ├── 4.2_LiquidityRegressions/, 4.2.1_SurpriseLiquidity/
│   └── 4.3_TakeoverHazards/, 4.3.1_SurpriseTakeover/
├── config/                 # project.yaml configuration
└── README.md               # This documentation
```

**Output Naming Convention**: Each script run creates a timestamped directory (e.g., `2025-12-28_163716/`) with a `latest` symlink pointing to the most recent successful run.

---

## Scripts

### 1.0_BuildSampleManifest.py (Orchestrator)

**Description**:
This is the master orchestrator script for Step 1. It does not perform data processing directly but manages the execution of the four substeps required to build the master sample manifest. It ensures that the sample universe is defined consistently before any text processing occurs.

**1. Inputs Info and Schema**:
*   **File**: `config/project.yaml`
    *   **Description**: Main configuration file defining paths and parameters.
    *   **Schema**: YAML format containing `paths` and `data` sections.

**2. Process Logic**:
1.  **Setup**: Loads configuration and sets up timestamped output/log directories.
2.  **Orchestration**: Sequentially executes the following substeps as separate processes:
    *   `1.1_CleanMetadata.py`: Cleans raw metadata and filters for events.
    *   `1.2_LinkEntities.py`: Links entities to Compustat/CRSP (to be documented).
    *   `1.3_BuildTenureMap.py`: Builds CEO tenure data (to be documented).
    *   `1.4_AssembleManifest.py`: Assembles the final manifest (to be documented).
3.  **Finalization**:
    *   Checks for successful completion of all substeps.
    *   Copies the final `master_sample_manifest.parquet` from Step 1.4's output to this script's output directory.
    *   Updates the `latest` symlink to point to the current run's output.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/1.0_BuildSampleManifest/{timestamp}/master_sample_manifest.parquet`
    *   **Description**: The final master sample manifest copied from Step 1.4.
*   **File**: `report_step_1_0.md`
    *   **Description**: Execution summary report.
*   **File**: `{timestamp}.log`
    *   **Description**: Full execution log capturing stdout/stderr from all substeps.

---

### 1.1_CleanMetadata.py

**Description**:
This script is the first substep in the pipeline. It is responsible for loading the raw Unified-info dataset, deduplicating records, resolving filename collisions, and applying strict filtering criteria to define the initial universe of earnings calls.

**1. Inputs Info and Schema**:
*   **File**: `1_Inputs/Unified-info.parquet`
    *   **Description**: The raw metadata file containing information about available call transcripts.
    *   **Schema**: Parquet file containing columns such as `file_name`, `validation_timestamp`, `event_type`, and `start_date`.
*   **File**: `config/project.yaml`
    *   **Description**: Configuration file defining the date range (`year_start`, `year_end`).

**2. Process Logic**:
1.  **Load Data**: Reads the `Unified-info.parquet` file.
2.  **Deduplicate**: Removes exact duplicate rows to ensure data integrity.
3.  **Resolve Collisions**: Identifies records with the same `file_name`. If collisions exist, it resolves them by keeping the record with the earliest `validation_timestamp`.
4.  **Event Filtering**: Filters the dataset to include *only* earnings calls.
    *   **Criterion**: `event_type == '1'`.
5.  **Temporal Filtering**: Filters the dataset to specific years defined in the config.
    *   **Criterion**: `start_date` year must be between 2002 and 2018 (inclusive).
6.  **Reporting**: Generates a detailed markdown report (`report_step_1_1.md`) summarising the row counts at each stage (duplicates removed, filtered rows, etc.).

**3. Output Info and Schema**:
*   **File**: `4_Outputs/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet`
    *   **Description**: The cleaned and filtered metadata file.
    *   **Schema**: Same columns as input `Unified-info.parquet`. Key columns preserved/validated are `file_name`, `start_date`, and `event_type`.
*   **File**: `variable_reference.csv`
    *   **Description**: A CSV listing the variables present in the output file.
*   **File**: `report_step_1_1.md`
    *   **Description**: Markdown report detailing the cleaning statistics.

---

### 1.2_LinkEntities.py

**Description**:
This script links the cleaned metadata to the CRSP/Compustat Merged (CCM) database. It uses a 4-tier linking strategy to assign GVKEYs and industry codes to each earnings call. It is optimized to perform linking at the company level (deduplicated) before broadcasting results to all calls.

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/1.1_CleanMetadata/latest/metadata_cleaned.parquet`
    *   **Description**: Cleaned metadata from the previous step.
*   **File**: `1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet`
    *   **Description**: The master CCM database file.
*   **File**: `1_Inputs/Siccodes12.zip` & `Siccodes48.zip`
    *   **Description**: ZIP files containing mapping logic for Fama-French 12 and 48 industry classifications.

**2. Process Logic**:
1.  **Dedup-Index Optimization**: Aggregates calls by `company_id` to create a list of unique companies, significantly reducing the computational load (approx. 11k companies vs 297k calls).
2.  **Tier 1 Linking (PERMNO + Date)**: Matches companies that have a valid `permno` to CCM records where the call date falls within the `LINKDT` and `LINKENDDT`.
3.  **Tier 2 Linking (CUSIP8 + Date)**: Matches remaining companies using the first 8 digits of the `cusip` code.
4.  **Tier 3 Linking (Fuzzy Name)**: Uses `rapidfuzz` to match remaining companies by normalized name (threshold score: 92).
5.  **Broadcast**: Merges the linked company data (GVKEY, SIC, etc.) back to the original full list of earnings calls.
6.  **Industry Mapping**: Maps SIC codes to Fama-French 12 and 48 industry codes using the provided ZIP files.
7.  **Filter**: Drops calls that could not be linked to a GVKEY.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/1.2_LinkEntities/{timestamp}/metadata_linked.parquet`
    *   **Description**: Metadata with added keys for CRSP/Compustat linking.
    *   **Schema**: Adds `gvkey`, `conm` (company name), `sic`, `ff12_code`, `ff12_name`, `ff48_code`, `ff48_name`, `link_method`, and `link_quality`.

---

### 1.3_BuildTenureMap.py

**Description**:
This script constructs a monthly panel of CEO tenure data from Execucomp. It transforms the annual Execucomp data into continuous tenure episodes and then expands them into a monthly time-series for every company.

**1. Inputs Info and Schema**:
*   **File**: `1_Inputs/Execucomp/comp_execucomp.parquet`
    *   **Description**: Raw Execucomp data containing executive compensation and tenure details.

**2. Process Logic**:
1.  **Identify CEOs**: Filters for records where `ceoann == 'CEO'` or `becameceo` date is present.
2.  **Build Episodes**: Aggregates annual records into continuous "episodes" defined by a `start_date` and `end_date`.
    *   Handles active CEOs by imputing a future end date.
3.  **Link Predecessors**: Sorts episodes by date and links each CEO to their immediate predecessor (`prev_execid`).
4.  **Expand to Monthly**: Expands the episodes into a monthly panel (one row per firm-month).
5.  **Resolve Overlaps**: Ensures that if tenure dates overlap, the incoming CEO takes precedence.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/1.3_BuildTenureMap/{timestamp}/tenure_monthly.parquet`
    *   **Description**: A monthly panel keyed by `gvkey`, `year`, and `month`.
    *   **Schema**: `gvkey`, `year`, `month`, `date`, `ceo_id` (execid), `ceo_name`, `prev_ceo_id`, `prev_ceo_name`.

---

### 1.4_AssembleManifest.py

**Description**:
This is the final assembly script for Step 1. It joins the linked metadata (from 1.2) with the CEO tenure map (from 1.3), applies a minimum call frequency filter to ensure sufficient data per CEO, and produces the final Master Sample Manifest.

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/1.2_LinkEntities/latest/metadata_linked.parquet`
*   **File**: `4_Outputs/1.3_BuildTenureMap/latest/tenure_monthly.parquet`

**2. Process Logic**:
1.  **Join**: Merges the Linked Metadata with the CEO Tenure Panel on `gvkey`, `year`, and `month`.
2.  **Filter Unmatched**: Drops calls that do not match to a valid CEO in the tenure panel.
3.  **Minimum Call Filter**:
    *   Calculates the number of calls per `ceo_id`.
    *   Filters out CEOs who have fewer than `min_calls_threshold` (default 5, configurable in `project.yaml`).
4.  **Final Polish**: Sorts by `file_name` and saves the final manifest.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/1.4_AssembleManifest/{timestamp}/master_sample_manifest.parquet`
    *   **Description**: The definitive list of calls to be processed in subsequent steps.
    *   **Schema**: Combined schema including call metadata, company info (GVKEY, Industry), and CEO info.

---

## Step 2: Text Processing (`2_Scripts/2_Text`)

### 2.1_TokenizeAndCount.py

**Description**:
This script performs text tokenization and dictionary-based word counting on speaker-level transcript data. It uses the Loughran-McDonald Master Dictionary to count occurrences of words in sentiment categories (Negative, Positive, Uncertainty, etc.) for each speaker turn.

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet`
    *   **Description**: The master manifest defining the universe of valid calls.
    *   **Columns Used**: `file_name`.
*   **File**: `1_Inputs/speaker_data_{year}.parquet` (for years 2002-2018)
    *   **Description**: Raw speaker-level transcript data containing each speaker's text turn.
    *   **Key Columns**: `file_name`, `speaker_number`, `context`, `role`, `speaker_name`, `employer`, `speaker_text`.
*   **File**: `1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv`
    *   **Description**: The Loughran-McDonald dictionary mapping words to sentiment categories.

**2. Process Logic**:
1.  **Load Manifest**: Reads the master manifest to get the set of valid `file_name` values.
2.  **Load Dictionary**: Parses the LM Dictionary CSV and builds sets of words for each category (Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining).
3.  **Process Each Year (2002-2018)**:
    1.  Load `speaker_data_{year}.parquet`.
    2.  Filter rows to only include `file_name` values present in the manifest.
    3.  Vectorize the `speaker_text` column using `CountVectorizer` (alpha-only tokens, case-insensitive matching against the LM vocabulary).
    4.  Aggregate word counts per sentiment category for each row.
    5.  Count `total_tokens` (alpha-only words) per row.
4.  **Save**: Outputs a parquet file for each year.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/2_Textual_Analysis/2.1_Tokenized/{timestamp}/linguistic_counts_{year}.parquet`
    *   **Description**: Speaker-level counts of dictionary words.
    *   **Schema**: `file_name`, `speaker_number`, `context`, `role`, `speaker_name`, `employer`, `Negative_count`, `Positive_count`, `Uncertainty_count`, `Litigious_count`, `Strong_Modal_count`, `Weak_Modal_count`, `Constraining_count`, `total_tokens`.

---

### 2.2_ConstructVariables.py

**Description**:
This script aggregates the speaker-level linguistic counts from Step 2.1 into call-level linguistic variables. It flags speakers by role (Analyst, Manager, CEO) and computes weighted percentage measures for each sample/context combination.

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_{year}.parquet`
    *   **Description**: Speaker-level counts from Step 2.1.
*   **File**: `4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet`
    *   **Description**: Master manifest for CEO name matching and metadata.
*   **File**: `managerial_roles_extracted.txt` (root directory)
    *   **Description**: List of keywords to identify managerial roles.

**2. Process Logic**:
1.  **Load References**: Load manager keywords and the CEO name map from the manifest.
2.  **Flag Speakers**: For each speaker turn, assign boolean flags:
    *   `is_analyst`: Role contains "analyst".
    *   `is_operator`: Role contains "operator".
    *   `is_manager`: Role matches manager keywords OR employer matches company name.
    *   `is_ceo`: Speaker name matches current or previous CEO name.
3.  **Aggregate by Sample/Context**: For each combination of sample (Manager, Analyst, CEO, Entire) and context (QA, Pres, All), compute weighted percentage: `(Sum of Category Counts / Sum of Total Tokens) * 100`.
4.  **Output**: One parquet file per year with call-level linguistic variables.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/2.4_Linguistic_Variables/{timestamp}/linguistic_variables_{year}.parquet`
    *   **Description**: Call-level linguistic variable percentages.
    *   **Schema**: `file_name`, `start_date`, `gvkey`, `conm`, `sic`, plus columns like `Manager_QA_Uncertainty_pct`, `Analyst_QA_Negative_pct`, etc.

---

### 2.3_VerifyStep2.py

**Description**:
A verification utility script that checks the integrity of Step 2 outputs. It confirms that all expected files exist and that key columns are present.

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_{year}.parquet`
*   **File**: `4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet`

**2. Process Logic**:
1.  Iterates through years 2002-2018.
2.  Checks if both `linguistic_counts_{year}.parquet` and `linguistic_variables_{year}.parquet` exist.
3.  Validates presence of key column `Manager_QA_Uncertainty_pct`.
4.  Reports missing values in the dependent variable.

**3. Output Info and Schema**:
*   **Output**: Console report (no file output).

---

## Step 3: Financial Features (`2_Scripts/3_Financial`)

### 3.0_BuildFinancialFeatures.py (Orchestrator)

**Description**:
Master orchestrator for Step 3. Coordinates substeps 3.1, 3.2, and 3.3 to write all financial feature outputs to a single timestamped folder.

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet`
*   Also loads all input files needed by substeps (Compustat, IBES, CRSP, CCCL, SDC).

**2. Process Logic**:
1.  **Setup**: Creates timestamped output folder.
2.  **Import Substeps**: Dynamically imports 3.1, 3.2, 3.3 modules.
3.  **Execute 3.1**: Computes firm controls (Size, BM, Lev, ROA, EPS_Growth, SurpDec, shift_intensity).
4.  **Execute 3.2**: Computes market variables (StockRet, MarketRet, Amihud, Corwin_Schultz, Volatility).
5.  **Execute 3.3**: Computes event flags (Takeover indicators).
6.  **Report Generation**: Generates `report_step3.md` and `variable_reference.csv`.

**3. Output Info and Schema**:
*   All outputs saved to `4_Outputs/3_Financial_Features/{timestamp}/`:
    *   `firm_controls_{year}.parquet` (from 3.1)
    *   `market_variables_{year}.parquet` (from 3.2)
    *   `event_flags_{year}.parquet` (from 3.3)

---

### 3.1_FirmControls.py

**Description**:
Computes firm-level control variables from Compustat quarterly data, IBES earnings forecasts, and CCCL competition instrument.

**1. Inputs Info and Schema**:
*   **File**: `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet`
    *   **Description**: Compustat quarterly fundamentals.
    *   **Key Columns**: `gvkey`, `datadate`, `atq`, `ceqq`, `cshoq`, `prccq`, `ltq`, `niq`, `epspxq`.
*   **File**: `1_Inputs/tr_ibes/tr_ibes.parquet`
    *   **Description**: IBES earnings forecasts and actuals.
    *   **Key Columns**: `TICKER`, `CUSIP`, `FPEDATS`, `MEANEST`, `ACTUAL`.
*   **File**: `1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet`
    *   **Description**: Competition (CCCL) shift-share instrument.

**2. Process Logic**:
1.  **Load Compustat**: Compute controls using `merge_asof` to match call date to latest quarter:
    *   `Size = ln(atq)`
    *   `BM = ceqq / (cshoq * prccq)`
    *   `Lev = ltq / atq`
    *   `ROA = niq / atq`
    *   `EPS_Growth = (epspxq - epspxq_lag4) / |epspxq_lag4|`
    *   `CurrentRatio = actq / lctq`
    *   `RD_Intensity = xrdq / atq`
2.  **Load IBES**: Compute earnings surprise:
    *   `surprise_raw = ACTUAL - MEANEST`
    *   `SurpDec`: Within-quarter decile ranking (-5 to +5).
3.  **Load CCCL**: Merge shift_intensity variants on (gvkey, year).
4.  **Winsorize**: 1st/99th percentile for all controls.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet`
    *   **Schema**: `file_name`, `gvkey`, `start_date`, `year`, `Size`, `BM`, `Lev`, `ROA`, `EPS_Growth`, `CurrentRatio`, `RD_Intensity`, `ActualEPS`, `ForecastEPS`, `surprise_raw`, `SurpDec`, `shift_intensity_sale_ff12`, `shift_intensity_mkvalt_ff12`, etc.

---

### 3.2_MarketVariables.py

**Description**:
Computes stock returns and liquidity measures from CRSP daily stock data. Uses vectorized pandas operations with year-based chunking for memory efficiency.

**1. Inputs Info and Schema**:
*   **File**: `1_Inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet`
    *   **Description**: CRSP daily stock file (quarterly chunks).
    *   **Key Columns**: `PERMNO`, `date`, `RET`, `VOL`, `VWRETD`, `ASKHI`, `BIDLO`, `PRC`.
*   **File**: `1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet`
    *   **Description**: CCM link for PERMNO lookup fallback.

**2. Process Logic**:
1.  **Load Manifest with PERMNO**: Uses direct PERMNO if available, falls back to CCM gvkey mapping.
2.  **Compute Returns**:
    *   Window: previous call + 5 days to current call - 5 days.
    *   `StockRet`: Compound stock return (%).
    *   `MarketRet`: Compound value-weighted market return (%).
    *   `Volatility`: Annualized standard deviation of daily returns.
3.  **Compute Liquidity**:
    *   Event window: call +/- 5 days.
    *   Baseline window: 35 to 6 days before call.
    *   `Amihud`: Mean of |ret|/dollar_volume (x10^6).
    *   `Corwin_Schultz`: High-low spread estimator.
    *   `Delta_Amihud`, `Delta_Corwin_Schultz`: Event - Baseline change.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/3_Financial_Features/{timestamp}/market_variables_{year}.parquet`
    *   **Schema**: `file_name`, `gvkey`, `start_date`, `year`, `StockRet`, `MarketRet`, `Amihud`, `Corwin_Schultz`, `Delta_Amihud`, `Delta_Corwin_Schultz`.

---

### 3.3_EventFlags.py

**Description**:
Computes takeover event flags from SDC M&A data. Identifies firms that become takeover targets within a year of an earnings call.

**1. Inputs Info and Schema**:
*   **File**: `1_Inputs/SDC/sdc-ma-merged.parquet`
    *   **Description**: SDC Platinum M&A database.
    *   **Key Columns**: `Target 6-digit CUSIP`, `Date Announced`, `Deal Attitude`.

**2. Process Logic**:
1.  **Build SDC Lookup**: Creates a dictionary mapping target CUSIP6 to (date_announced, deal_attitude).
2.  **Match Calls to Takeovers**: For each call, checks if a takeover was announced within 365 days.
3.  **Classify Deal Type**:
    *   `Uninvited`: Hostile or unsolicited bids.
    *   `Friendly`: All other bids.
4.  **Compute Duration**: Quarters until takeover (for survival analysis).

**3. Output Info and Schema**:
*   **File**: `4_Outputs/3_Financial_Features/{timestamp}/event_flags_{year}.parquet`
    *   **Schema**: `file_name`, `gvkey`, `start_date`, `year`, `Takeover`, `Takeover_Type`, `Duration`.

---

### 3.4_Utils.py (Utility Module)

**Description**:
Shared utility functions for Step 3 scripts. Provides common functionality for logging, symlink management, and variable reference generation.

**Key Functions**:
*   `DualWriter`: Writes to both stdout and log file.
*   `get_latest_output_dir`: Resolves 'latest' symlink or falls back to most recent timestamped folder.
*   `generate_variable_reference`: Creates `variable_reference.csv` with column metadata.
*   `update_latest_symlink`: Updates 'latest' symlink (with copytree fallback on Windows).

**No direct outputs** (imported by other scripts).

---

## Step 4: Econometric Analysis (`2_Scripts/4_Econometric`)

### 4.1_EstimateCeoClarity.py

**Description**:
Estimates CEO "Clarity" as a personal communication trait using fixed effects OLS regression. The core idea is that some CEOs consistently use more uncertain language than others, even after controlling for firm circumstances. This persistent individual component is captured as a CEO fixed effect.

**Conceptual Overview**:
During earnings calls, managers respond to analyst questions. The percentage of "uncertainty words" (from the Loughran-McDonald dictionary) in their responses varies. Some of this variation comes from:
1. **Firm circumstances**: Bad earnings, volatile markets, or surprises naturally increase uncertainty.
2. **Situational factors**: The specific questions asked, time period, etc.
3. **CEO personality**: Some individuals are inherently more hedging/cautious communicators.

By including CEO fixed effects in the regression, we isolate component #3 — the CEO's personal communication style. A CEO with a high fixed effect (high γᵢ) uses more uncertain language *regardless* of circumstances, suggesting lower clarity. We invert this to get "Clarity" = −γᵢ.

**Regression Model**:
The script estimates the following OLS regression separately for each industry sample (Main, Finance, Utility):

```
Manager_QA_Uncertainty_pctᵢₜ = α + γᵢ + δₜ + β₁·Manager_Pres_Uncertainty_pctᵢₜ
                              + β₂·Analyst_QA_Uncertainty_pctᵢₜ + β₃·Entire_All_Negative_pctᵢₜ
                              + β₄·StockRetᵢₜ + β₅·MarketRetᵢₜ + β₆·EPS_Growthᵢₜ + β₇·SurpDecᵢₜ + εᵢₜ
```

Where:
- **Manager_QA_Uncertainty_pctᵢₜ**: Dependent variable. The weighted percentage of uncertainty words in manager Q&A responses for call *t* by CEO *i*.
- **γᵢ**: CEO fixed effect. This captures the CEO's personal tendency to use uncertain language. A high γᵢ means this CEO consistently uses more uncertainty words than average.
- **δₜ**: Year fixed effect. Controls for time trends (e.g., if 2008-2009 crisis caused all CEOs to be more uncertain).
- **Manager_Pres_Uncertainty_pct**: Uncertainty during the presentation section (scripted portion).
- **Analyst_QA_Uncertainty_pct**: Uncertainty in analyst questions (controls for the "tone" of questions asked).
- **Entire_All_Negative_pct**: Overall negative tone of the call.
- **StockRet, MarketRet**: Stock and market returns since previous call (controls for recent performance).
- **EPS_Growth, SurpDec**: Earnings growth and earnings surprise decile (controls for fundamental news).

**Interpreting the Output**:
- **γᵢ** is extracted for each CEO from the fitted model.
- **ClarityCEO_raw = −γᵢ**: Inverted so that *higher* values mean *clearer* communication.
- **ClarityCEO**: Standardized (mean=0, std=1) for comparability across samples.

**Sample Splits**:
Three separate regressions are run to account for industry-specific communication norms:
- **Main**: Non-financial, non-utility (FF12 codes 1-7, 9-10, 12)
- **Finance**: Financial firms (FF12 code 11)
- **Utility**: Utility firms (FF12 code 8)

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet`
*   **File**: `4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet`
*   **File**: `4_Outputs/3_Financial_Features/latest/firm_controls_{year}.parquet`
*   **File**: `4_Outputs/3_Financial_Features/latest/market_variables_{year}.parquet`

**2. Process Logic**:
1.  **Load All Data**: Merge manifest (file_name, ceo_id, ff12_code), linguistic variables (Manager_QA_Uncertainty_pct, etc.), firm controls (EPS_Growth, SurpDec), and market variables (StockRet, MarketRet).
2.  **Prepare Regression Data**: Filter to complete cases (no missing values) and CEOs with >=5 calls (to ensure stable fixed effect estimates).
3.  **Run OLS with Fixed Effects**: Using `statsmodels`, estimate the regression with robust standard errors (HC1).
4.  **Extract CEO Fixed Effects**: Parse γᵢ from the model parameters.
5.  **Compute Clarity Scores**: ClarityCEO = standardize(−γᵢ).

**3. Output Info and Schema**:
*   **File**: `4_Outputs/4.1_CeoClarity/{timestamp}/ceo_clarity_scores.parquet`
    *   **Schema**: 
        - `ceo_id`: CEO identifier.
        - `gamma_i`: The CEO fixed effect coefficient from regression.
        - `ClarityCEO_raw`: Raw clarity score (= −γᵢ).
        - `ClarityCEO`: Standardized clarity score (mean=0, std=1).
        - `sample`: Industry sample (Main/Finance/Utility).
        - `n_calls`: Number of calls by this CEO.
        - `avg_uncertainty`: Mean uncertainty percentage for this CEO.
        - `ceo_name`: CEO full name.
*   **File**: `4_Outputs/4.1_CeoClarity/{timestamp}/regression_results_{sample}.txt` — Full statsmodels output.
*   **File**: `4_Outputs/4.1_CeoClarity/{timestamp}/model_diagnostics.csv` — R², F-stat, N obs, etc.
*   **File**: `4_Outputs/4.1_CeoClarity/{timestamp}/report_step4_1.md` — Summary report with top/bottom CEOs.

---

### 4.1.1_EstimateCeoClarity_CeoSpecific.py

**Description**:
This is a variant of 4.1 that uses **CEO-only** linguistic variables instead of manager-level aggregates. While 4.1 uses `Manager_QA_Uncertainty_pct` (which includes CFO and other executives), this script uses `CEO_QA_Uncertainty_pct` (only the CEO's own speech). This provides a more targeted measure of the CEO's personal communication style.

**Regression Model**:
```
CEO_QA_Uncertainty_pctᵢₜ = α + γᵢ + δₜ + β₁·CEO_Pres_Uncertainty_pctᵢₜ
                          + β₂·Analyst_QA_Uncertainty_pctᵢₜ + β₃·Entire_All_Negative_pctᵢₜ
                          + β₄·StockRetᵢₜ + β₅·MarketRetᵢₜ + β₆·EPS_Growthᵢₜ + β₇·SurpDecᵢₜ + εᵢₜ
```

The key difference: both the dependent variable and the presentation control are now CEO-specific.

**1. Inputs Info and Schema**:
*   Same as 4.1_EstimateCeoClarity.py.

**2. Process Logic**:
*   Same regression structure as 4.1, but uses:
    *   Dependent variable: `CEO_QA_Uncertainty_pct` (only CEO's Q&A speech)
    *   Presentation control: `CEO_Pres_Uncertainty_pct` (only CEO's presentation speech)

**3. Output Info and Schema**:
*   **File**: `4_Outputs/4.1.1_CeoClarity_CEO_Only/{timestamp}/ceo_clarity_scores.parquet`
*   **File**: `4_Outputs/4.1.1_CeoClarity_CEO_Only/{timestamp}/regression_results_{sample}.txt`
*   **File**: `4_Outputs/4.1.1_CeoClarity_CEO_Only/{timestamp}/model_diagnostics.csv`

---

### 4.1.2_EstimateCeoClarity_Extended.py

**Description**:
This script performs a **robustness check** on the CEO Clarity estimates. The concern being addressed is: *Are the CEO fixed effects capturing true personality differences, or are they confounded by omitted firm characteristics?*

For example, if CEOs of highly-levered firms always sound more uncertain (because their firms are riskier), the fixed effect might capture "runs a levered firm" rather than "inherently uncertain communicator." By adding extended financial controls and comparing the results to the baseline, we can assess robustness.

**Conceptual Overview**:
The script runs **4 separate regressions** for each industry sample:

| Model | Dependent Variable | Controls |
|-------|-------------------|----------|
| Manager_Baseline | `Manager_QA_Uncertainty_pct` | Base controls only |
| Manager_Extended | `Manager_QA_Uncertainty_pct` | Base + Extended controls |
| CEO_Baseline | `CEO_QA_Uncertainty_pct` | Base controls only |
| CEO_Extended | `CEO_QA_Uncertainty_pct` | Base + Extended controls |

**Base Controls** (same as 4.1):
- `StockRet`, `MarketRet`, `EPS_Growth`, `SurpDec`

**Extended Controls** (new):
- `Size` (log total assets) — large firms may communicate differently
- `BM` (Book-to-Market) — value vs. growth companies
- `Lev` (Leverage) — financial distress risk
- `ROA` (Return on Assets) — profitability
- `CurrentRatio` (Current Assets / Liabilities) — liquidity position
- `RD_Intensity` (R&D / Assets) — innovation-oriented firms
- `Volatility` (Stock return volatility) — market uncertainty about the firm

**Regression Models**:

**Baseline Model** (same as 4.1):
```
Uncertainty_pctᵢₜ = α + γᵢ + δₜ + β₁·Pres_Uncertainty + β₂·Analyst_Uncertainty + β₃·Negative_pct
                    + β₄·StockRet + β₅·MarketRet + β₆·EPS_Growth + β₇·SurpDec + εᵢₜ
```

**Extended Model** (adds 7 controls):
```
Uncertainty_pctᵢₜ = α + γᵢ + δₜ + β₁·Pres_Uncertainty + β₂·Analyst_Uncertainty + β₃·Negative_pct
                    + β₄·StockRet + β₅·MarketRet + β₆·EPS_Growth + β₇·SurpDec
                    + β₈·Size + β₉·BM + β₁₀·Lev + β₁₁·ROA + β₁₂·CurrentRatio + β₁₃·RD_Intensity + β₁₄·Volatility + εᵢₜ
```

**Interpreting the Results**:
The key diagnostic is comparing R² between Baseline and Extended:
- If R² increases **substantially**, the extended controls explain additional variation in uncertainty. The CEO fixed effects may have been absorbing firm-level variation that should be controlled for.
- If R² increases only **marginally** (e.g., +0.01), the CEO fixed effects are robust — they capture true personal communication style, not confounded firm characteristics.

Additionally, comparing the `ClarityCEO` scores across models tests whether individual CEO rankings change significantly.

**1. Inputs Info and Schema**:
*   Same as 4.1_EstimateCeoClarity.py.

**2. Process Logic**:
1.  **Load All Data**: Include all base and extended control variables.
2.  **Prepare Regression Data** (per model): Filter to complete cases. Extended models may have fewer observations if some firms are missing Size/BM/etc.
3.  **Run 4 × 3 Regressions**: 4 models × 3 industry samples = up to 12 regressions.
4.  **Extract and Compare**: Save CEO fixed effects and clarity scores for each model.
5.  **Generate Comparative Report**: Table showing R², N, and number of controls for each model.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/4.1.2_CeoClarity_Extended/{timestamp}/ceo_clarity_scores_all.parquet`
    *   Combined results for all 4 models.
    *   **Schema**: `ceo_id`, `gamma_i`, `ClarityCEO_raw`, `ClarityCEO`, `model`, `sample`, `n_calls`, `ceo_name`.
*   **File**: `4_Outputs/4.1.2_CeoClarity_Extended/{timestamp}/regression_results_{model}_{sample}.txt`
*   **File**: `4_Outputs/4.1.2_CeoClarity_Extended/{timestamp}/model_diagnostics.csv`
    *   Comparison table: R², Adj R², N obs, N CEOs, N controls for each model.
*   **File**: `4_Outputs/4.1.2_CeoClarity_Extended/{timestamp}/report_step4_1_2.md`
    *   Summary report with robustness interpretation.

---

### 4.1.3_EstimateCeoClarity_Regime.py

**Description**:
This script estimates the CEO's **influence on team communication style** — sometimes called "regime" effects. The key insight is that CEOs may affect not just their own speech, but also how other executives (CFO, COO, etc.) on the same call communicate. This is a form of leadership spillover.

**Conceptual Overview**:
If a CEO sets a "clear communication culture," the CFO and other managers might also use less uncertain language during earnings calls. By regressing `NonCEO_Manager_QA_Uncertainty_pct` (speech of **other managers, excluding the CEO**) on CEO fixed effects, we capture the CEO's influence on their team's communication style.

A CEO with high clarity in this model isn't just personally clear — they create an environment where *everyone* on their management team communicates more clearly.

**Regression Model**:
```
NonCEO_Manager_QA_Uncertainty_pctᵢₜ = α + γᵢ + δₜ + β₁·Manager_Pres_Uncertainty_pctᵢₜ
                                      + β₂·Analyst_QA_Uncertainty_pctᵢₜ + β₃·Entire_All_Negative_pctᵢₜ
                                      + β₄·StockRetᵢₜ + β₅·MarketRetᵢₜ + β₆·EPS_Growthᵢₜ + β₇·SurpDecᵢₜ + εᵢₜ
```

Where:
- **NonCEO_Manager_QA_Uncertainty_pctᵢₜ**: Dependent variable. The percentage of uncertainty words in Q&A responses by **non-CEO managers** (CFO, COO, etc.) during CEO *i*'s tenure.
- **γᵢ**: CEO fixed effect. Captures the CEO's persistent influence on their team's communication clarity.
- Other controls are the same as 4.1.

**Interpreting the Output**:
- A CEO with a **negative γᵢ** (high Clarity) leads a team that uses *less* uncertain language.
- This provides evidence for **leadership culture effects** — the CEO shapes how their entire executive team communicates.

**1. Inputs Info and Schema**:
*   Same as 4.1_EstimateCeoClarity.py, but uses `NonCEO_Manager_QA_Uncertainty_pct` instead of `Manager_QA_Uncertainty_pct`.

**2. Process Logic**:
1.  Same structure as 4.1, but with different dependent variable.
2.  Regress non-CEO manager uncertainty on CEO fixed effects.
3.  Extract and standardize clarity scores.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/4.1.3_CeoClarity_Regime/{timestamp}/ceo_clarity_scores.parquet`
*   **File**: `4_Outputs/4.1.3_CeoClarity_Regime/{timestamp}/regression_results_{sample}.txt`
*   **File**: `4_Outputs/4.1.3_CeoClarity_Regime/{timestamp}/model_diagnostics.csv`

---

### 4.1.4_EstimateCeoTone.py

**Description**:
This script estimates CEO **Tone** — the net sentiment (Positive − Negative) of communications — as a persistent personal trait. While 4.1 focuses on *uncertainty*, this focuses on *sentiment polarity*. Some CEOs are consistently more optimistic/positive, even after controlling for firm circumstances.

**Conceptual Overview**:
Net Tone = Positive% − Negative%. A CEO with high tone uses more positive words and fewer negative words relative to their peers. This could reflect:
- Personality (inherently optimistic communicator)
- Strategic choice (deliberately framing news positively)
- Leadership style (motivational vs. cautious)

The script runs **3 models** to capture different facets:

| Model | Dependent Variable | Interpretation |
|-------|-------------------|----------------|
| **ToneAll** | `Manager_QA_NetTone` | CEO's effect on all manager speech tone |
| **ToneCEO** | `CEO_QA_NetTone` | CEO's own personal tone |
| **ToneRegime** | `NonCEO_Manager_QA_NetTone` | CEO's influence on team tone (spillover) |

**Variable Construction**:
Net Tone variables are computed as:
```
{Sample}_{Context}_NetTone = {Sample}_{Context}_Positive_pct − {Sample}_{Context}_Negative_pct
```

For example: `CEO_QA_NetTone = CEO_QA_Positive_pct − CEO_QA_Negative_pct`

**Regression Model** (shown for ToneCEO):
```
CEO_QA_NetToneᵢₜ = α + γᵢ + δₜ + β₁·CEO_Pres_NetToneᵢₜ + β₂·Analyst_QA_NetToneᵢₜ
                   + β₃·Entire_All_Uncertainty_pctᵢₜ
                   + β₄·StockRetᵢₜ + β₅·MarketRetᵢₜ + β₆·EPS_Growthᵢₜ + β₇·SurpDecᵢₜ + εᵢₜ
```

Where:
- **CEO_QA_NetToneᵢₜ**: Net sentiment in CEO's Q&A responses.
- **γᵢ**: CEO fixed effect. High γᵢ = CEO consistently more positive.
- Controls include tone in presentation section, analyst question tone, and overall uncertainty.

**Interpreting the Output**:
- Unlike Clarity, **high γᵢ = high Tone** (no negation needed, since positive tone is good).
- **ToneCEO**: Personal optimism/negativity trait.
- **ToneRegime**: Whether the CEO creates a more positive communication culture for the team.

**1. Inputs Info and Schema**:
*   Same as 4.1_EstimateCeoClarity.py.

**2. Process Logic**:
1.  **Compute NetTone** variables: Positive% − Negative% for each sample/context.
2.  **Run 3 × 3 Regressions**: 3 models × 3 industry samples = up to 9 regressions.
3.  **Extract Tone Scores**: Standardized fixed effects (high = more positive).

**3. Output Info and Schema**:
*   **File**: `4_Outputs/4.1.4_CeoTone/{timestamp}/ceo_tone_scores.parquet`
    *   **Schema**: `ceo_id`, `gamma_i`, `Tone_raw`, `ToneAll`/`ToneCEO`/`ToneRegime` (standardized), `model`, `sample`, `n_calls`, `ceo_name`.
*   **File**: `4_Outputs/4.1.4_CeoTone/{timestamp}/regression_results_{model}_{sample}.txt`
*   **File**: `4_Outputs/4.1.4_CeoTone/{timestamp}/model_diagnostics.csv`
*   **File**: `4_Outputs/4.1.4_CeoTone/{timestamp}/report_step4_1_4.md`

---

### 4.2_LiquidityRegressions.py

**Description**:
Tests whether CEO/Manager communication affects **market liquidity** around earnings calls. Uses both OLS and **2SLS (instrumental variables)** to address endogeneity concerns. The idea is that unclear communication increases information asymmetry, which should worsen liquidity (higher bid-ask spreads, lower trading activity).

**Conceptual Overview**:
There are two key variables:
1. **ClarityCEO/ClarityRegime**: The CEO's *persistent* communication style (from 4.1). This is treated as **exogenous** — it's a stable personality trait that doesn't change with firm circumstances.
2. **Manager_QA_Uncertainty_pct**: The *time-varying* uncertainty in a specific call. This is potentially **endogenous** — a CEO might hedge more when they know bad news is coming.

To address endogeneity, we use the **CCCL instrument** (`shift_intensity_sale_ff48`). CCCL events in the same industry create exogenous shocks to uncertainty expectations — they affect how uncertain managers sound but are unrelated to the specific firm's news.

**Regression Structure**:

**Phase 1: First Stage** (Instrument Validity)
```
Manager_QA_Uncertainty_pctᵢₜ = α + π·shift_intensity_sale_ff48ᵢₜ + Controls + δₜ + εᵢₜ
```
Tests whether the instrument is strong (F-statistic ≥ 10).

**Phase 2: OLS** (No Instrument)
```
Delta_Amihudᵢₜ = α + β₁·ClarityCEOᵢ + β₂·Manager_QA_Uncertainty_pctᵢₜ + Controls + δₜ + εᵢₜ
```

**Phase 3: 2SLS/IV** (Uncertainty Instrumented)
```
Stage 1: Manager_QA_Uncertainty_pctᵢₜ = π·Instrumentᵢₜ + [exog controls]
Stage 2: Delta_Amihudᵢₜ = β₁·ClarityCEOᵢ + β₂·Uncertainty_hatᵢₜ + Controls + δₜ + εᵢₜ
```

**Key Variables**:
- **Delta_Amihud**: Change in Amihud illiquidity (event - baseline). Higher = worse liquidity.
- **Delta_Corwin_Schultz**: Change in spread estimator (event - baseline). Higher = worse liquidity.
- **shift_intensity_sale_ff48**: CCCL instrument — sales-weighted competition intensity from court decisions in FF48 industry.

**Interpreting Results**:
- **ClarityCEO < 0**: Clearer CEOs → lower illiquidity (better liquidity).
- **Uncertainty > 0**: More uncertain speech → higher illiquidity (worse liquidity).
- **IV vs OLS**: If IV coefficient for Uncertainty is larger than OLS, it suggests OLS is biased toward zero (attenuation).

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/4.1_CeoClarity/latest/ceo_clarity_scores.parquet` — ClarityRegime
*   **File**: `4_Outputs/4.1.1_CeoClarity_CEO_Only/latest/ceo_clarity_scores.parquet` — ClarityCEO
*   **File**: `4_Outputs/3_Financial_Features/latest/firm_controls_{year}.parquet` — includes `shift_intensity_sale_ff48`
*   **File**: `4_Outputs/3_Financial_Features/latest/market_variables_{year}.parquet` — Delta_Amihud, Delta_Corwin_Schultz

**2. Process Logic**:
1.  **Load Data**: Merge manifest, linguistic variables, firm controls, market variables, and clarity scores.
2.  **Phase 1**: Run first-stage regressions to test instrument strength.
3.  **Phase 2**: Run OLS for Regime and CEO models.
4.  **Phase 3**: Run 2SLS with `linearmodels.IV2SLS`.
5.  **Report**: Generate Kleibergen-Paap F-statistics and coefficient comparison.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/4.2_LiquidityRegressions/{timestamp}/first_stage_results.txt` — Instrument validity tests.
*   **File**: `4_Outputs/4.2_LiquidityRegressions/{timestamp}/ols_regime.txt` / `ols_ceo.txt` — OLS results.
*   **File**: `4_Outputs/4.2_LiquidityRegressions/{timestamp}/iv_regime.txt` / `iv_ceo.txt` — 2SLS results.
*   **File**: `4_Outputs/4.2_LiquidityRegressions/{timestamp}/model_diagnostics.csv` — Summary table with R², N, KP F-stat.
*   **File**: `4_Outputs/4.2_LiquidityRegressions/{timestamp}/report_step4_2.md`

---

### 4.2.1_SurpriseLiquidity.py

**Description**:
Estimates the effect of **unexpected** communication uncertainty on market liquidity. Instead of using raw uncertainty levels, this script measures *surprise* — how much more uncertain was this call compared to:
1. **Peer Surprise**: Other firms in the same industry at the same time.
2. **Historical Surprise**: The CEO's own historical calls.

**Conceptual Overview**:
Markets may only react to *unexpected* information. If a CEO always sounds uncertain, markets have already priced this in. But if a CEO is *surprisingly* uncertain (relative to peers or own history), this is new information that affects liquidity.

**Surprise Measures**:

**Peer Surprise** (3 groupings):
For each call, we compute the CEO's percentile rank in uncertainty within their industry-quarter group:
- `Peer_FF12`: Rank within Fama-French 12 industry
- `Peer_FF48`: Rank within Fama-French 48 industry
- `Peer_SIC2`: Rank within 2-digit SIC industry

**Historical Surprise** (3 windows):
For each call, we compute the CEO's percentile rank vs. their own rolling history:
- `Hist_4Q`: Rank vs. last 4 quarters (1 year)
- `Hist_8Q`: Rank vs. last 8 quarters (2 years)
- `Hist_12Q`: Rank vs. last 12 quarters (3 years)

**Interaction Terms** (9 combinations):
`Hist_{window}Q × Peer_{group}` — Captures whether combined surprise (both vs. peers AND vs. history) has an amplified effect.

**Regression Model**:
```
Delta_Amihudᵢₜ = α + β₁·Peer_FF12ᵢₜ + β₂·Peer_FF48ᵢₜ + β₃·Peer_SIC2ᵢₜ
                 + β₄·Hist_4Qᵢₜ + β₅·Hist_8Qᵢₜ + β₆·Hist_12Qᵢₜ
                 + ∑ γⱼ·(Hist × Peer)ⱼᵢₜ + Controls + δₜ + εᵢₜ
```

**Interpreting Results**:
- **Peer Surprise > 0**: Being more uncertain than industry peers → worse liquidity.
- **Historical Surprise > 0**: Being more uncertain than own history → worse liquidity.
- **Interaction > 0**: Being a double surprise (both dimensions) → amplified effect.

**1. Inputs Info and Schema**:
*   Same as 4.2_LiquidityRegressions.py.

**2. Process Logic**:
1.  **Compute Peer Surprises**: Percentile rank within industry × quarter for FF12, FF48, SIC2.
2.  **Compute Historical Surprises**: Rolling percentile rank vs. own 4/8/12 quarter history.
3.  **Compute Interactions**: All 9 H × P combinations.
4.  **Run Regression Matrix**: Single regression with all surprise terms.
5.  **Generate Coefficient Matrix**: Table of all surprise coefficients with significance.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/surprise_variables.parquet`
    *   Contains all computed surprise variables per call.
*   **File**: `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/regression_matrix.csv`
    *   Coefficient, SE, t-stat, p-value for each surprise term.
*   **File**: `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/report_step4_2_1.md`

---

### 4.3_TakeoverHazards.py

**Description**:
Analyzes whether CEO Clarity and Q&A Uncertainty predict **takeover probability** using survival analysis. Uses two types of models:
1. **Cox Proportional Hazards** (all takeovers)
2. **Fine-Gray Competing Risks** (separates hostile/unsolicited vs. friendly takeovers)

**Conceptual Overview**:
The research question is: *Do companies with uncertain CEO communication become acquisition targets?*

The hypothesis is that uncertain communication signals:
- Information asymmetry (acquirers may exploit)
- Weak governance (CEO unable to articulate strategy)
- Hidden problems (acquirer can "fix" the firm)

This script tests whether `ClarityCEO` and `Manager_QA_Uncertainty_pct` predict takeover events within 365 days of earnings calls.

**Survival Analysis Framework**:
- **Duration**: Time from earnings call to takeover (or censoring at 365 days).
- **Event**: Takeover announcement (from SDC M&A data).
- **Competing Risks**: Friendly vs. Uninvited takeovers are competing events — observing one precludes observing the other.

**Models**:

**Model 1: Cox Proportional Hazards** (all takeovers):
```
h(t|X) = h₀(t) · exp(β₁·ClarityCEOᵢ + β₂·Manager_QA_Uncertainty_pctᵢₜ + ∑ βⱼ·Controlsᵢₜ)
```

Where:
- **h(t|X)**: Hazard rate (instantaneous takeover probability at time t).
- **h₀(t)**: Baseline hazard function.
- **exp(β)**: Hazard Ratio (HR). HR > 1 means higher takeover risk.

**Model 2: Fine-Gray Competing Risks** (Uninvited):
```
CIF(t|X) = 1 - exp(-H(t) · exp(β₁·ClarityCEOᵢ + β₂·Uncertainty_pctᵢₜ + Controls))
```

Estimates subdistribution hazard for Uninvited (Hostile + Unsolicited) takeovers, treating Friendly takeovers as competing events.

**Model 3: Fine-Gray Competing Risks** (Friendly):
Same structure, but for Friendly (Friendly + Neutral) takeovers.

**Key Variables**:
- **ClarityRegime / ClarityCEO**: CEO fixed effects from 4.1 (time-invariant).
- **Manager_QA_Uncertainty_pct**: Call-level uncertainty (time-varying).
- **Controls**: Size, BM, Lev, ROA.

**Interpreting Results**:
- **HR > 1 for Uncertainty**: More uncertain CEOs → higher takeover risk.
- **HR < 1 for Clarity**: Clearer CEOs → lower takeover risk (protected).
- **Concordance Index**: Model discrimination power (0.5 = random, 1.0 = perfect).

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/4.1_CeoClarity/latest/ceo_clarity_scores.parquet` — ClarityRegime
*   **File**: `4_Outputs/4.1.1_CeoClarity_CEO_Only/latest/ceo_clarity_scores.parquet` — ClarityCEO
*   **File**: `1_Inputs/SDC/sdc-ma-merged.parquet` — M&A deal announcements
*   **File**: `4_Outputs/3_Financial_Features/latest/firm_controls_{year}.parquet`

**2. Process Logic**:
1.  **Load Data**: Match SDC M&A events to firms via CUSIP6, ticker, and company name (multi-tier).
2.  **Classify Deals**: Hostile/Unsolicited → "Uninvited"; Friendly/Neutral → "Friendly".
3.  **Build Survival Dataset**: Mark calls with takeover events within 365 days.
4.  **Run Cox PH**: All takeovers.
5.  **Run Fine-Gray**: Uninvited vs. Friendly as competing risks.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/4.3_TakeoverHazards/{timestamp}/cox_ph_all.txt` — Cox PH results.
*   **File**: `4_Outputs/4.3_TakeoverHazards/{timestamp}/fine_gray_uninvited.txt` — Uninvited competing risks.
*   **File**: `4_Outputs/4.3_TakeoverHazards/{timestamp}/fine_gray_friendly.txt` — Friendly competing risks.
*   **File**: `4_Outputs/4.3_TakeoverHazards/{timestamp}/hazard_ratios.csv` — Summary of all HRs.
*   **File**: `4_Outputs/4.3_TakeoverHazards/{timestamp}/takeover_event_summary.csv`

---

### 4.3.1_SurpriseTakeover.py

**Description**:
Extends 4.3 by replacing raw uncertainty with **surprise measures** (from 4.2.1). Tests whether *unexpectedly* uncertain communication predicts takeover probability better than raw uncertainty levels.

**Conceptual Overview**:
The idea is that acquirers react to *unexpected* information signals. If a CEO is always vague, the market has priced this in. But if a CEO becomes *surprisingly* vague (relative to peers or own history), this signals new negative information.

**Surprise Measures** (from 4.2.1):
- **Peer_FF12, Peer_FF48, Peer_SIC2**: Percentile rank vs. industry peers.
- **Hist_4Q, Hist_8Q, Hist_12Q**: Percentile rank vs. own rolling history.
- **Interaction Terms**: Hist × Peer combinations.

**Model Specifications**:

| Model | Variables | Description |
|-------|-----------|-------------|
| Peer_FF12 | Peer_FF12 + Controls | Single peer term |
| AllPeer | Peer_FF12 + Peer_FF48 + Peer_SIC2 + Controls | All peer terms |
| AllHist | Hist_4Q + Hist_8Q + Hist_12Q + Controls | All history terms |
| Combined | Peer_FF48 + Hist_4Q + Controls | Primary specification |
| FullMatrix | All Peer + All Hist + All Interactions + Controls | Complete model |

**Cox PH Model**:
```
h(t|X) = h₀(t) · exp(β₁·Peer_FF48ᵢₜ + β₂·Hist_4Qᵢₜ + ∑ βⱼ·Controlsᵢₜ)
```

**VIF Diagnostic**:
The script includes **Variance Inflation Factor (VIF)** calculation to detect multicollinearity among surprise terms:
- VIF > 5: Moderate multicollinearity
- VIF > 10: High multicollinearity (coefficients unstable)

This is important because Peer and History surprise terms may be correlated, which can inflate standard errors.

**Interpreting Results**:
- **HR > 1 for Peer Surprise**: Being more uncertain than peers → higher takeover risk.
- **HR > 1 for History Surprise**: Being more uncertain than own history → higher takeover risk.

**1. Inputs Info and Schema**:
*   **File**: `4_Outputs/4.2.1_SurpriseLiquidity/latest/surprise_variables.parquet` — Peer/History surprise.
*   **File**: `4_Outputs/4.1.1_CeoClarity_CEO_Only/latest/ceo_clarity_scores.parquet` — ClarityCEO.
*   **File**: `1_Inputs/SDC/sdc-ma-merged.parquet` — M&A events.

**2. Process Logic**:
1.  **Load Surprise Data**: From 4.2.1 output.
2.  **Aggregate to Firm-Quarter**: Take last call per quarter.
3.  **Build Survival Dataset**: Match SDC events to firms, compute duration.
4.  **Run Cox PH Models**: 10 specifications × 3 event types = up to 30 models.
5.  **Calculate VIF**: Multicollinearity diagnostic for surprise terms.

**3. Output Info and Schema**:
*   **File**: `4_Outputs/4.3.1_SurpriseTakeover/{timestamp}/survival_data.parquet`
*   **File**: `4_Outputs/4.3.1_SurpriseTakeover/{timestamp}/hazard_ratio_matrix.csv`
    *   HR, coefficient, p-value for each surprise term × event type.
*   **File**: `4_Outputs/4.3.1_SurpriseTakeover/{timestamp}/vif_diagnostic.csv`
*   **File**: `4_Outputs/4.3.1_SurpriseTakeover/{timestamp}/report_step4_3_1.md`

---

## Variable Definition Table

| Variable Name | Description | Source |
| :--- | :--- | :--- |
| `file_name` | Unique identifier for the transcript file. | `1_Inputs/Unified-info.parquet` |
| `start_date` | The date the call took place. | `1_Inputs/Unified-info.parquet` |
| `event_type` | Type of event (filtered to '1' for Earnings Calls). | `1_Inputs/Unified-info.parquet` |
| `validation_timestamp` | Timestamp used for collision resolution (kept earliest). | `1_Inputs/Unified-info.parquet` |
| `gvkey` | Compustat unique company identifier. | `1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet` |
| `conm` | Standardized company name from Compustat. | `1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet` |
| `sic` | Standard Industrial Classification code. | `1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet` |
| `ff48_code` / `ff48_name` | Fama-French 48-industry classification. | `1_Inputs/Siccodes48.zip` &#8594; `4_Outputs/OLD/1.2_LinkEntities/{timestamp}/metadata_linked.parquet` |
| `link_method` | Method used to link to GVKEY (permno, cusip, or fuzzy). | Generated &#8594; `4_Outputs/OLD/1.2_LinkEntities/{timestamp}/metadata_linked.parquet` |
| `link_quality` | Confidence score/rank of the entity link. | Generated &#8594; `4_Outputs/OLD/1.2_LinkEntities/{timestamp}/metadata_linked.parquet` |
| `ceo_id` | Unique executive identifier (execid) from Execucomp. | `1_Inputs/Execucomp/comp_execucomp.parquet` |
| `ceo_name` | Full name of the CEO. | `1_Inputs/Execucomp/comp_execucomp.parquet` |
| `prev_ceo_id` | Identifier of the CEO's predecessor. | Derived &#8594; `4_Outputs/OLD/1.3_BuildTenureMap/{timestamp}/tenure_monthly.parquet` |
| `speaker_text` | Raw text of a speaker's turn in a call. | `1_Inputs/speaker_data_{year}.parquet` |
| `speaker_number` | Sequential speaker turn number within a call. | `1_Inputs/speaker_data_{year}.parquet` |
| `context` | Section of the call (qa, pres). | `1_Inputs/speaker_data_{year}.parquet` |
| `role` | Speaker's role/title. | `1_Inputs/speaker_data_{year}.parquet` |
| `speaker_name` | Speaker's name. | `1_Inputs/speaker_data_{year}.parquet` |
| `employer` | Speaker's employer. | `1_Inputs/speaker_data_{year}.parquet` |
| `Negative_count` | Count of LM Negative words in a speaker turn. | Generated &#8594; `4_Outputs/2_Textual_Analysis/2.1_Tokenized/{timestamp}/linguistic_counts_{year}.parquet` |
| `Positive_count` | Count of LM Positive words in a speaker turn. | Generated &#8594; `4_Outputs/2_Textual_Analysis/2.1_Tokenized/{timestamp}/linguistic_counts_{year}.parquet` |
| `Uncertainty_count` | Count of LM Uncertainty words in a speaker turn. | Generated &#8594; `4_Outputs/2_Textual_Analysis/2.1_Tokenized/{timestamp}/linguistic_counts_{year}.parquet` |
| `Litigious_count` | Count of LM Litigious words in a speaker turn. | Generated &#8594; `4_Outputs/2_Textual_Analysis/2.1_Tokenized/{timestamp}/linguistic_counts_{year}.parquet` |
| `Strong_Modal_count` | Count of LM Strong Modal words in a speaker turn. | Generated &#8594; `4_Outputs/2_Textual_Analysis/2.1_Tokenized/{timestamp}/linguistic_counts_{year}.parquet` |
| `Weak_Modal_count` | Count of LM Weak Modal words in a speaker turn. | Generated &#8594; `4_Outputs/2_Textual_Analysis/2.1_Tokenized/{timestamp}/linguistic_counts_{year}.parquet` |
| `Constraining_count` | Count of LM Constraining words in a speaker turn. | Generated &#8594; `4_Outputs/2_Textual_Analysis/2.1_Tokenized/{timestamp}/linguistic_counts_{year}.parquet` |
| `total_tokens` | Total alpha-only word count per speaker turn. | Generated &#8594; `4_Outputs/2_Textual_Analysis/2.1_Tokenized/{timestamp}/linguistic_counts_{year}.parquet` |
| `is_analyst` | Boolean flag indicating speaker is an analyst. | Generated &#8594; `2.2_ConstructVariables.py` (intermediate) |
| `is_manager` | Boolean flag indicating speaker is a manager. | Generated &#8594; `2.2_ConstructVariables.py` (intermediate) |
| `is_ceo` | Boolean flag indicating speaker is CEO. | Generated &#8594; `2.2_ConstructVariables.py` (intermediate) |
| `{Sample}_{Context}_{Category}_pct` | **1014 columns** following pattern: Sample={Manager, Analyst, CEO, NonCEO_Manager, Entire}, Context={QA, Pres, All}, Category={Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining}. Example: `Manager_QA_Uncertainty_pct`. | Generated &#8594; `4_Outputs/2.4_Linguistic_Variables/{timestamp}/linguistic_variables_{year}.parquet` |
| `Size` | Log of total assets: ln(atq). | `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet` |
| `BM` | Book-to-market: ceqq / (cshoq * prccq). | `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet` |
| `Lev` | Leverage: ltq / atq. | `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet` |
| `ROA` | Return on assets: niq / atq. | `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet` |
| `EPS_Growth` | YoY EPS growth: (EPS - EPS_lag4) / abs(EPS_lag4). | `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet` |
| `CurrentRatio` | Current ratio: actq / lctq. | `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet` |
| `RD_Intensity` | R&D intensity: xrdq / atq. | `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet` |
| `SurpDec` | Earnings surprise decile (-5 to +5). | `1_Inputs/tr_ibes/tr_ibes.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet` |
| `shift_intensity_*` | CCCL competition instrument variants (6 columns). | `1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet` |
| `StockRet` | Compound stock return (%) over inter-call window. | `1_Inputs/CRSP_DSF/` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/market_variables_{year}.parquet` |
| `MarketRet` | Compound value-weighted market return (%) over inter-call window. | `1_Inputs/CRSP_DSF/` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/market_variables_{year}.parquet` |
| `Volatility` | Annualized stock return volatility (%). | `1_Inputs/CRSP_DSF/` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/market_variables_{year}.parquet` |
| `Amihud` | Illiquidity: mean of abs(ret)/dollar_volume (x10^6). | `1_Inputs/CRSP_DSF/` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/market_variables_{year}.parquet` |
| `Corwin_Schultz` | High-low spread estimator. | `1_Inputs/CRSP_DSF/` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/market_variables_{year}.parquet` |
| `Delta_Amihud` | Amihud change: event window - baseline window. | Generated &#8594; `4_Outputs/3_Financial_Features/{timestamp}/market_variables_{year}.parquet` |
| `Delta_Corwin_Schultz` | Corwin-Schultz change: event - baseline. | Generated &#8594; `4_Outputs/3_Financial_Features/{timestamp}/market_variables_{year}.parquet` |
| `Takeover` | Binary flag: 1 if firm was takeover target within 365 days. | `1_Inputs/SDC/sdc-ma-merged.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/event_flags_{year}.parquet` |
| `Takeover_Type` | Deal type: "Friendly" or "Uninvited". | `1_Inputs/SDC/sdc-ma-merged.parquet` &#8594; `4_Outputs/3_Financial_Features/{timestamp}/event_flags_{year}.parquet` |
| `Duration` | Quarters until takeover (for survival analysis). | Generated &#8594; `4_Outputs/3_Financial_Features/{timestamp}/event_flags_{year}.parquet` |
| `gamma_i` | CEO fixed effect coefficient from regression. | Generated &#8594; `4_Outputs/4.1_CeoClarity/{timestamp}/ceo_clarity_scores.parquet` |
| `ClarityCEO_raw` | Raw clarity score: -gamma_i (higher = clearer). | Generated &#8594; `4_Outputs/4.1_CeoClarity/{timestamp}/ceo_clarity_scores.parquet` |
| `ClarityCEO` | Standardized CEO clarity score (mean=0, std=1). | Generated &#8594; `4_Outputs/4.1_CeoClarity/{timestamp}/ceo_clarity_scores.parquet` |
| `ClarityRegime` | CEO clarity from Manager-level model (4.1). | Generated &#8594; `4_Outputs/4.1_CeoClarity/{timestamp}/ceo_clarity_scores.parquet` |
| `Tone_raw` | Raw net sentiment fixed effect (gamma_i). | Generated &#8594; `4_Outputs/4.1.4_CeoTone/{timestamp}/ceo_tone_scores.parquet` |
| `ToneAll` | Standardized tone from all manager speech. | Generated &#8594; `4_Outputs/4.1.4_CeoTone/{timestamp}/ceo_tone_scores.parquet` |
| `ToneCEO` | Standardized tone from CEO's own speech. | Generated &#8594; `4_Outputs/4.1.4_CeoTone/{timestamp}/ceo_tone_scores.parquet` |
| `ToneRegime` | Standardized tone from non-CEO managers (spillover). | Generated &#8594; `4_Outputs/4.1.4_CeoTone/{timestamp}/ceo_tone_scores.parquet` |
| `{Sample}_{Context}_NetTone` | Net sentiment: Positive_pct - Negative_pct. | Generated &#8594; `4.1.4_EstimateCeoTone.py` (intermediate) |
| `Peer_FF12` | Percentile rank of uncertainty vs. FF12 industry-quarter peers. | Generated &#8594; `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/surprise_variables.parquet` |
| `Peer_FF48` | Percentile rank of uncertainty vs. FF48 industry-quarter peers. | Generated &#8594; `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/surprise_variables.parquet` |
| `Peer_SIC2` | Percentile rank of uncertainty vs. SIC2 industry-quarter peers. | Generated &#8594; `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/surprise_variables.parquet` |
| `Hist_4Q` | Percentile rank of uncertainty vs. own last 4 quarters. | Generated &#8594; `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/surprise_variables.parquet` |
| `Hist_8Q` | Percentile rank of uncertainty vs. own last 8 quarters. | Generated &#8594; `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/surprise_variables.parquet` |
| `Hist_12Q` | Percentile rank of uncertainty vs. own last 12 quarters. | Generated &#8594; `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/surprise_variables.parquet` |
| `Hist_{w}QxPeer_{g}` | Interaction: History × Peer surprise (9 combinations). | Generated &#8594; `4_Outputs/4.2.1_SurpriseLiquidity/{timestamp}/surprise_variables.parquet` |
| `HR` / `SHR` | Hazard Ratio / Subdistribution Hazard Ratio from Cox/Fine-Gray models. | Generated &#8594; `4_Outputs/4.3_TakeoverHazards/{timestamp}/hazard_ratios.csv` |
| `event_any` | Binary: 1 if any takeover occurred within window. | Generated &#8594; `4_Outputs/4.3.1_SurpriseTakeover/{timestamp}/survival_data.parquet` |
| `event_uninvited` | Binary: 1 if Hostile/Unsolicited takeover occurred. | Generated &#8594; `4_Outputs/4.3.1_SurpriseTakeover/{timestamp}/survival_data.parquet` |
| `event_friendly` | Binary: 1 if Friendly/Neutral takeover occurred. | Generated &#8594; `4_Outputs/4.3.1_SurpriseTakeover/{timestamp}/survival_data.parquet` |
| `VIF` | Variance Inflation Factor (multicollinearity diagnostic). | Generated &#8594; `4_Outputs/4.3.1_SurpriseTakeover/{timestamp}/vif_diagnostic.csv` |
