---
phase: 05-readme-documentation
plan: 01
type: execute
wave: 1
depends_on: ["04-financial-econometric"]
files_modified: []
autonomous: true

must_haves:
  truths:
    - "requirements.txt exists in project root"
    - "requirements.txt contains Python version specification"
    - "requirements.txt contains pinned dependencies"
    - "README.md exists in project root"
    - "README.md contains step-by-step execution instructions"
    - "README.md contains program-to-output mapping table"
    - "README.md contains pipeline flow diagram"
    - "README.md contains variable codebook section"
    - "README.md documents data sources"
    - "README.md documents each script's purpose, inputs, outputs"
    - "SUMMARY.md exists in .planning/phases/05-readme-documentation/"
  artifacts:
    - path: "requirements.txt"
      provides: "Python environment specification (DOC-01)"
    - path: "README.md"
      provides: "Complete project documentation (DOC-01 through DOC-07)"
    - path: ".planning/phases/05-readme-documentation/SUMMARY.md"
      provides: "Phase 5 implementation summary"
  key_links:
    - from: "requirements.txt"
      to: "DOC-01"
      via: "file creation"
      pattern: "^python|^[a-z0-9_-]+"
    - from: "README.md sections"
      to: "DOC-01 through DOC-07"
      via: "markdown documentation"
      pattern: "execution instructions|program-to-output|pipeline flow|variable codebook|data sources"
---

<objective>
Create a comprehensive, DCAS-compliant README.md for thesis/journal submission with all required documentation elements.

Purpose: Document the complete pipeline for reproducibility and submission, including environment setup, execution instructions, output mappings, pipeline architecture, variable definitions, and data source descriptions.

Output: requirements.txt and comprehensive README.md at project root with all DOC-01 through DOC-07 requirements satisfied, plus SUMMARY.md documenting the documentation phase.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/04-financial-econometric/SUMMARY.md
@CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create requirements.txt</name>
  <files>requirements.txt</files>
  <action>
  Create a requirements.txt file in the project root with Python version and pinned dependencies (DOC-01):

  1. **Examine existing scripts for dependencies:**
  ```bash
  grep -h "^import\|^from" 2_Scripts/*.py | sort | uniq
  ```

  2. **Create requirements.txt with explicit versions:**
  ```
  # Python version requirement
  # Minimum Python 3.9 required

  # Core data processing
  pandas>=2.0.0
  numpy>=1.24.0

  # Database access
  sqlalchemy>=2.0.0
  psycopg2-binary>=2.9.0

  # Text processing
  nltk>=3.8.0
  textblob>=0.17.0
  spacy>=3.6.0

  # Financial data
  wrds>=3.1.0

  # Statistical analysis
  statsmodels>=0.14.0
  scipy>=1.11.0

  # Machine learning
  scikit-learn>=1.3.0

  # Econometrics
  linearmodels>=4.29.0
  lifelines>=0.28.0

  # Utilities
  pyyaml>=6.0.0
  python-dotenv>=1.0.0
  tqdm>=4.66.0
  ```

  3. **Add Python version comment:**
  ```
  # Python >= 3.9.0
  ```

  4. **Verify requirements.txt:**
  ```bash
  cat requirements.txt
  ```
  </action>
  <verify>
  requirements.txt exists, contains Python version specification, and lists all project dependencies with pinned versions.
  </verify>
  <done>
  requirements.txt created with Python version and pinned dependencies.
  </done>
</task>

<task type="auto">
  <name>Task 2: Write README.md structure and overview</name>
  <files>README.md</files>
  <action>
  Create README.md with project overview, directory structure, and setup instructions:

  1. **Project Overview Section:**
  ```markdown
  # DCAS CEO Clarity and Firm Outcomes Analysis

  Complete pipeline for analyzing the relationship between CEO clarity in earnings conference calls and firm outcomes (liquidity, takeover hazards). This repository contains all data processing, feature construction, econometric analysis, and documentation for thesis/journal submission.

  ## Overview

  This project implements a reproducible pipeline for:
  1. Retrieving and preprocessing financial data (CRSP, Compustat, Execucomp)
  2. Processing earnings conference call transcripts
  3. Extracting linguistic features and measuring CEO clarity
  4. Constructing financial control variables
  5. Estimating econometric models (liquidity regressions, takeover hazards)

  ## Directory Structure

  ```
  README.md
  requirements.txt
  config/
    └── project.yaml          # Configuration parameters (paths, seeds, threads)
  1_Inputs/                   # Raw data files
  2_Scripts/                  # All processing scripts
    ├── 1.0_RetrieveData.py
    ├── 2.0_PreprocessText.py
    ├── 3.0_BuildFinancialFeatures.py
    ├── 4.1_EstimateCeoClarity.py
    └── ...
  3_Logs/                     # Execution logs (text + optional JSONL)
  4_Outputs/                  # Timestamped outputs + latest/ symlinks
    ├── 1.0_RetrieveData/
    │   ├── 2024-01-15_103045/
    │   └── latest/
    └── ...
  .planning/                  # Project planning documentation
  CLAUDE.md                   # Claude project memory
  ```

  ## Requirements

  - Python >= 3.9.0
  - All dependencies in `requirements.txt`
  - WRDS account for financial data access (CRSP, Compustat)
  ```

  2. **Installation Instructions:**
  ```markdown
  ## Installation

  1. Clone the repository:
  ```bash
  git clone <repository-url>
  cd <repository-name>
  ```

  2. Create virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

  3. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

  4. Configure WRDS credentials:
  ```bash
  export WRDS_USERNAME='your_username'
  export WRDS_PASSWORD='your_password'
  ```
  Or create `.env` file:
  ```
  WRDS_USERNAME=your_username
  WRDS_PASSWORD=your_password
  ```
  ```
  </action>
  <verify>
  README.md exists with project overview, directory structure, and installation instructions.
  </verify>
  <done>
  README.md overview section created with project structure and setup instructions.
  </done>
</task>

<task type="auto">
  <name>Task 3: Add step-by-step execution instructions (DOC-02)</name>
  <files>README.md</files>
  <action>
  Add numbered, copy-paste ready execution instructions to README.md:

  1. **Add Execution Section:**
  ```markdown
  ## Execution Instructions

  ### Complete Pipeline Execution

  Run the entire pipeline from start to finish:

  1. **Step 1: Retrieve Financial Data**
  ```bash
  python 2_Scripts/1.0_RetrieveData.py
  ```
  Output: `4_Outputs/1.0_RetrieveData/latest/`

  2. **Step 2: Preprocess Text Data**
  ```bash
  python 2_Scripts/2.0_PreprocessText.py
  ```
  Output: `4_Outputs/2.0_PreprocessText/latest/`

  3. **Step 3: Extract Text Features**
  ```bash
  python 2_Scripts/2.1_ExtractFeatures.py
  ```
  Output: `4_Outputs/2.1_ExtractFeatures/latest/`

  4. **Step 4: Build Financial Features**
  ```bash
  python 2_Scripts/3.0_BuildFinancialFeatures.py
  ```
  Output: `4_Outputs/3.0_BuildFinancialFeatures/latest/`

  5. **Step 5: Construct Firm Controls**
  ```bash
  python 2_Scripts/3.1_FirmControls.py
  ```
  Output: `4_Outputs/3.1_FirmControls/latest/`

  6. **Step 6: Create Market Variables**
  ```bash
  python 2_Scripts/3.2_MarketVariables.py
  ```
  Output: `4_Outputs/3.2_MarketVariables/latest/`

  7. **Step 7: Generate Event Flags**
  ```bash
  python 2_Scripts/3.3_EventFlags.py
  ```
  Output: `4_Outputs/3.3_EventFlags/latest/`

  8. **Step 8: Estimate CEO Clarity**
  ```bash
  python 2_Scripts/4.1_EstimateCeoClarity.py
  ```
  Output: `4_Outputs/4.1_EstimateCeoClarity/latest/`

  9. **Step 9: Run Liquidity Regressions**
  ```bash
  python 2_Scripts/4.2_LiquidityRegressions.py
  ```
  Output: `4_Outputs/4.2_LiquidityRegressions/latest/`

  10. **Step 10: Estimate Takeover Hazards**
  ```bash
  python 2_Scripts/4.3_TakeoverHazards.py
  ```
  Output: `4_Outputs/4.3_TakeoverHazards/latest/`

  ### One-Line Execution

  Run all steps in sequence:
  ```bash
  python 2_Scripts/1.0_RetrieveData.py && \
  python 2_Scripts/2.0_PreprocessText.py && \
  python 2_Scripts/2.1_ExtractFeatures.py && \
  python 2_Scripts/3.0_BuildFinancialFeatures.py && \
  python 2_Scripts/3.1_FirmControls.py && \
  python 2_Scripts/3.2_MarketVariables.py && \
  python 2_Scripts/3.3_EventFlags.py && \
  python 2_Scripts/4.1_EstimateCeoClarity.py && \
  python 2_Scripts/4.2_LiquidityRegressions.py && \
  python 2_Scripts/4.3_TakeoverHazards.py
  ```

  ### Verifying Outputs

  Check that all output directories exist:
  ```bash
  ls -d 4_Outputs/*/latest/
  ```

  Verify log files:
  ```bash
  ls -l 3_Logs/*.log
  ```
  ```
  </action>
  <verify>
  README.md contains numbered step-by-step execution instructions that are copy-paste ready.
  </verify>
  <done>
  Step-by-step execution instructions added to README.md.
  </done>
</task>

<task type="auto">
  <name>Task 4: Add program-to-output mapping (DOC-03)</name>
  <files>README.md</files>
  <action>
  Add program-to-output mapping table to README.md:

  1. **Add Mapping Section:**
  ```markdown
  ## Program-to-Output Mapping

  The following table maps each script to the outputs it produces for analysis and paper tables/figures:

  | Script | Outputs | Paper Table/Figure | Description |
  |--------|---------|-------------------|-------------|
  | 1.0_RetrieveData.py | crsp_monthly.csv, compustat_annual.csv, execucomp.csv | - | Raw financial data retrieval |
  | 2.0_PreprocessText.py | cleaned_transcripts.csv | - | Text preprocessing and cleaning |
  | 2.1_ExtractFeatures.py | text_features.csv | Table 1 | Linguistic feature extraction (vagueness, readability, sentiment) |
  | 3.0_BuildFinancialFeatures.py | financial_features.csv | Table 2 | Financial feature construction (market cap, book-to-market, leverage) |
  | 3.1_FirmControls.py | firm_controls.csv | Table 2 | Firm control variables (size, age, profitability) |
  | 3.2_MarketVariables.py | market_variables.csv | Table 2 | Market variables (returns, volatility, volume) |
  | 3.3_EventFlags.py | event_flags.csv | Table 2 | Event flags (earnings announcements, management changes) |
  | 4.1_EstimateCeoClarity.py | ceo_clarity_estimates.csv | Table 3 | CEO clarity coefficient estimates and significance |
  | 4.2_LiquidityRegressions.py | liquidity_results.csv | Table 4 | Liquidity regression results (illiquidity, bid-ask spread) |
  | 4.3_TakeoverHazards.py | takeover_hazards.csv | Table 5 | Takeover hazard model results (hazard ratios, survival probabilities) |

  ### Final Dataset

  All intermediate datasets are merged into the final analysis dataset:
  - **File:** `4_Outputs/final_dataset.csv`
  - **Purpose:** Complete dataset with all variables for regression analysis
  - **Table/Figure:** Used in all regression tables (Tables 3-5)
  ```
  </action>
  <verify>
  README.md contains program-to-output mapping table linking scripts to paper tables/figures.
  </verify>
  <done>
  Program-to-output mapping added to README.md.
  </done>
</task>

<task type="auto">
  <name>Task 5: Add pipeline flow diagram (DOC-04)</name>
  <files>README.md</files>
  <action>
  Add pipeline flow diagram (Mermaid) to README.md:

  1. **Add Flow Diagram Section:**
  ```markdown
  ## Pipeline Flow

  The following diagram illustrates the complete pipeline from raw data to econometric results:

  ```mermaid
  graph TD
      A[1.0_RetrieveData.py] -->|crsp_monthly.csv<br/>compustat_annual.csv<br/>execucomp.csv| B[3.0_BuildFinancialFeatures.py]
      C[Transcripts] -->|raw text| D[2.0_PreprocessText.py]
      D -->|cleaned_transcripts.csv| E[2.1_ExtractFeatures.py]
      E -->|text_features.csv| F[4.1_EstimateCeoClarity.py]

      B -->|financial_features.csv| G[3.1_FirmControls.py]
      B -->|financial_features.csv| H[3.2_MarketVariables.py]
      B -->|financial_features.csv| I[3.3_EventFlags.py]

      G -->|firm_controls.csv| J[final_dataset.csv]
      H -->|market_variables.csv| J
      I -->|event_flags.csv| J
      F -->|ceo_clarity_estimates.csv| J

      J --> K[4.2_LiquidityRegressions.py]
      J --> L[4.3_TakeoverHazards.py]

      K -->|liquidity_results.csv| M[Tables/Figures]
      L -->|takeover_hazards.csv| M

      style A fill:#e1f5ff
      style D fill:#e1f5ff
      style E fill:#e1f5ff
      style F fill:#ffe1f5
      style G fill:#fff5e1
      style H fill:#fff5e1
      style I fill:#fff5e1
      style K fill:#e1ffe1
      style L fill:#e1ffe1
      style M fill:#f0e1ff
  ```

  ### Pipeline Stages

  - **Stage 1 (Blue):** Data retrieval and preprocessing
  - **Stage 2 (Pink):** Text feature extraction and CEO clarity estimation
  - **Stage 3 (Yellow):** Financial feature construction
  - **Stage 4 (Green):** Econometric analysis
  - **Stage 5 (Purple):** Final outputs for paper
  ```
  </action>
  <verify>
  README.md contains pipeline flow diagram showing data flow from scripts to outputs.
  </verify>
  <done>
  Pipeline flow diagram added to README.md.
  </done>
</task>

<task type="auto">
  <name>Task 6: Add variable codebook (DOC-05)</name>
  <files>README.md</files>
  <action>
  Add variable codebook section to README.md:

  1. **Add Codebook Section:**
  ```markdown
  ## Variable Codebook

  ### Linguistic Features

  | Variable | Type | Description | Source | Range |
  |----------|------|-------------|--------|-------|
  | ceo_clarity | Continuous | CEO clarity score estimated from linguistic features | 4.1_EstimateCeoClarity.py | -∞ to +∞ |
  | vagueness_score | Continuous | Average vagueness index in CEO speech | 2.1_ExtractFeatures.py | 0 to 1 |
  | readability_score | Continuous | Flesch-Kincaid readability grade level | 2.1_ExtractFeatures.py | 0 to 20+ |
  | sentiment_score | Continuous | Average sentiment polarity (negative to positive) | 2.1_ExtractFeatures.py | -1 to +1 |

  ### Financial Features

  | Variable | Type | Description | Source | Range |
  |----------|------|-------------|--------|-------|
  | firm_size | Continuous | Log of market capitalization | 3.0_BuildFinancialFeatures.py | -∞ to +∞ |
  | market_to_book | Continuous | Market-to-book ratio | 3.0_BuildFinancialFeatures.py | 0 to ∞ |
  | leverage | Continuous | Total debt / total assets | 3.0_BuildFinancialFeatures.py | 0 to 1 |
  | profitability | Continuous | ROA (return on assets) | 3.0_BuildFinancialFeatures.py | -∞ to +∞ |
  | cash_holdings | Continuous | Cash / total assets | 3.0_BuildFinancialFeatures.py | 0 to 1 |

  ### Firm Controls

  | Variable | Type | Description | Source | Range |
  |----------|------|-------------|--------|-------|
  | firm_age | Continuous | Years since IPO | 3.1_FirmControls.py | 0 to ∞ |
  | rd_intensity | Continuous | R&D expenses / total assets | 3.1_FirmControls.py | 0 to 1 |
  | capex_intensity | Continuous | Capital expenditures / total assets | 3.1_FirmControls.py | 0 to 1 |
  | dividend_payer | Binary | 1 if pays dividend, 0 otherwise | 3.1_FirmControls.py | 0 or 1 |

  ### Market Variables

  | Variable | Type | Description | Source | Range |
  |----------|------|-------------|--------|-------|
  | market_return | Continuous | Stock return over period | 3.2_MarketVariables.py | -1 to +∞ |
  | volatility | Continuous | Standard deviation of returns | 3.2_MarketVariables.py | 0 to ∞ |
  | trading_volume | Continuous | Average daily trading volume | 3.2_MarketVariables.py | 0 to ∞ |
  | bid_ask_spread | Continuous | Bid-ask spread (percentage) | 3.2_MarketVariables.py | 0 to ∞ |

  ### Event Flags

  | Variable | Type | Description | Source | Range |
  |----------|------|-------------|--------|-------|
  | earnings_announcement | Binary | 1 if earnings announcement in period | 3.3_EventFlags.py | 0 or 1 |
  | ceo_turnover | Binary | 1 if CEO turnover in period | 3.3_EventFlags.py | 0 or 1 |
  | m_a_activity | Binary | 1 if M&A activity in period | 3.3_EventFlags.py | 0 or 1 |

  ### Dependent Variables (Outcomes)

  | Variable | Type | Description | Source | Range |
  |----------|------|-------------|--------|-------|
  | illiquidity | Continuous | Amihud illiquidity measure | 4.2_LiquidityRegressions.py | 0 to ∞ |
  | takeover_hazard | Continuous | Hazard rate of takeover | 4.3_TakeoverHazards.py | 0 to ∞ |

  ### Identifiers

  | Variable | Type | Description | Source | Range |
  |----------|------|-------------|--------|-------|
  | firm_id | Categorical | Unique firm identifier | All scripts | Integer |
  | year | Integer | Fiscal year | All scripts | YYYY |
  | date | Date | Observation date | All scripts | YYYY-MM-DD |
  ```
  </action>
  <verify>
  README.md contains comprehensive variable codebook with all final analysis variables.
  </verify>
  <done>
  Variable codebook added to README.md.
  </done>
</task>

<task type="auto">
  <name>Task 7: Document data sources (DOC-07)</name>
  <files>README.md</files>
  <action>
  Add data sources section to README.md:

  1. **Add Data Sources Section:**
  ```markdown
  ## Data Sources

  ### CRSP (Center for Research in Security Prices)

  - **Database:** CRSP US Stock Database
  - **Access:** WRDS (Wharton Research Data Services)
  - **Tables Used:**
    - `msf` (Monthly Stock File) - Monthly stock prices, returns, trading volume
    - `mse` (Monthly Stock Events) - Delisting events
  - **Variables Retrieved:**
    - Stock prices (PRC, BID, ASK)
    - Returns (RET)
    - Trading volume (VOL)
    - Market capitalization (SHROUT * PRC)
  - **Coverage:** 1925-present
  - **Frequency:** Monthly
  - **Retrieval Script:** `1.0_RetrieveData.py`

  ### Compustat (Standard & Poor's)

  - **Database:** Compustat North America
  - **Access:** WRDS
  - **Tables Used:**
    - `funda` (Fundamental Annual) - Annual financial statements
  - **Variables Retrieved:**
    - Total assets (AT)
    - Total debt (DLC + DLTT)
    - Cash and equivalents (CHE)
    - Net income (NI)
    - R&D expenses (XRD)
    - Capital expenditures (CAPX)
    - Common shares outstanding (CSHO)
  - **Coverage:** 1950-present
  - **Frequency:** Annual
  - **Retrieval Script:** `1.0_RetrieveData.py`

  ### Execucomp (Executive Compensation)

  - **Database:** Execucomp
  - **Access:** WRDS
  - **Tables Used:**
    - `anncomp` (Annual Compensation) - Executive compensation data
  - **Variables Retrieved:**
    - CEO identifier (EXECID)
    - CEO name (CEOANNU)
    - CEO tenure (TENURE)
    - CEO age (AGE)
  - **Coverage:** 1992-present
  - **Frequency:** Annual
  - **Retrieval Script:** `1.0_RetrieveData.py`

  ### Earnings Conference Call Transcripts

  - **Source:** Thomson Reuters StreetEvents / Bloomberg / FactSet
  - **Format:** Text transcripts (PDF, HTML, or plain text)
  - **Content:** CEO/CFO Q&A sessions from earnings calls
  - **Sample Period:** 2005-2023 (example)
  - **Frequency:** Quarterly
  - **Processing Scripts:**
    - `2.0_PreprocessText.py` - Preprocessing and cleaning
    - `2.1_ExtractFeatures.py` - Feature extraction
  - **Notes:** Transcripts require manual download and placement in `1_Inputs/transcripts/`

  ### Sample Selection

  - **Initial Universe:** All US public firms
  - **Inclusion Criteria:**
    - Available in CRSP and Compustat
    - Have earnings conference call transcripts
    - S&P 1500 firms (optional filter)
  - **Exclusion Criteria:**
    - Financial firms (SIC codes 6000-6999)
    - Utility firms (SIC codes 4900-4999)
    - Firms with insufficient financial data
  - **Final Sample:** Approximately X firms over Y years

  ### Data Limitations

  - CRSP and Compustat data are subject to restatements
  - Execucomp coverage is limited to S&P 1500 firms pre-2006
  - Transcript availability varies by firm and period
  - Missing data handled via forward-fill or exclusion depending on variable
  ```
  </action>
  <verify>
  README.md documents all data sources (CRSP, Compustat, Execucomp, transcripts).
  </verify>
  <done>
  Data sources section added to README.md.
  </done>
</task>

<task type="auto">
  <name>Task 8: Document each script (DOC-06)</name>
  <files>README.md</files>
  <action>
  Add script documentation section to README.md:

  1. **Add Script Documentation Section:**
  ```markdown
  ## Script Documentation

  ### Step 1: Data Retrieval

  #### 1.0_RetrieveData.py

  **Purpose:** Retrieve raw financial data from WRDS (CRSP, Compustat, Execucomp)

  **Inputs:**
  - None (connects directly to WRDS via API)
  - WRDS credentials (username/password)

  **Outputs:**
  - `1_Inputs/crsp_monthly.csv` - Monthly stock data
  - `1_Inputs/compustat_annual.csv` - Annual financial statements
  - `1_Inputs/execucomp.csv` - Executive compensation data
  - `4_Outputs/1.0_RetrieveData/latest/stats.json` - Retrieval statistics

  **Key Operations:**
  - Connect to WRDS PostgreSQL database
  - Query CRSP monthly stock file (msf)
  - Query Compustat annual fundamentals (funda)
  - Query Execucomp compensation data (anncomp)
  - Export to CSV files
  - Record retrieval statistics (rows, columns, date range)

  **Configuration:**
  - Sample period: defined in `config/project.yaml`
  - Firm universe: defined in `config/project.yaml`

  ### Step 2: Text Processing

  #### 2.0_PreprocessText.py

  **Purpose:** Clean and preprocess earnings conference call transcripts

  **Inputs:**
  - `1_Inputs/transcripts/*.txt` - Raw transcript files

  **Outputs:**
  - `4_Outputs/2.0_PreprocessText/latest/cleaned_transcripts.csv` - Cleaned text
  - `4_Outputs/2.0_PreprocessText/latest/stats.json` - Preprocessing statistics

  **Key Operations:**
  - Remove headers/footers and metadata
  - Remove speaker labels and timestamps
  - Lowercase conversion
  - Remove special characters and numbers (context-dependent)
  - Tokenization and sentence splitting
  - Remove stopwords (optional)
  - Lemmatization (optional)

  **Configuration:**
  - Preprocessing options: defined in `config/project.yaml`

  #### 2.1_ExtractFeatures.py

  **Purpose:** Extract linguistic features from cleaned transcripts

  **Inputs:**
  - `4_Outputs/2.0_PreprocessText/latest/cleaned_transcripts.csv` - Cleaned text

  **Outputs:**
  - `4_Outputs/2.1_ExtractFeatures/latest/text_features.csv` - Linguistic features
  - `4_Outputs/2.1_ExtractFeatures/latest/stats.json` - Feature statistics

  **Key Operations:**
  - Calculate vagueness score (frequency of vague words)
  - Calculate readability (Flesch-Kincaid grade level)
  - Calculate sentiment (VADER or similar)
  - Calculate word/sentence counts
  - Calculate lexical diversity
  - Calculate parts-of-speech distribution

  **Configuration:**
  - Feature definitions: defined in `config/project.yaml`

  ### Step 3: Financial Features

  #### 3.0_BuildFinancialFeatures.py

  **Purpose:** Construct financial features from CRSP/Compustat data

  **Inputs:**
  - `1_Inputs/crsp_monthly.csv` - CRSP monthly data
  - `1_Inputs/compustat_annual.csv` - Compustat annual data
  - `1_Inputs/execucomp.csv` - Execucomp data

  **Outputs:**
  - `4_Outputs/3.0_BuildFinancialFeatures/latest/financial_features.csv` - Financial features
  - `4_Outputs/3.0_BuildFinancialFeatures/latest/stats.json` - Construction statistics

  **Key Operations:**
  - Merge CRSP and Compustat by GVKEY and date
  - Calculate market capitalization
  - Calculate market-to-book ratio
  - Calculate leverage (debt/assets)
  - Calculate profitability (ROA, ROE)
  - Calculate cash holdings
  - Calculate firm age (years since IPO)
  - Handle missing data and outliers

  **Configuration:**
  - Feature definitions: defined in `config/project.yaml`
  - Merge methods: defined in `config/project.yaml`

  #### 3.1_FirmControls.py

  **Purpose:** Construct firm-level control variables

  **Inputs:**
  - `4_Outputs/3.0_BuildFinancialFeatures/latest/financial_features.csv`

  **Outputs:**
  - `4_Outputs/3.1_FirmControls/latest/firm_controls.csv` - Firm controls
  - `4_Outputs/3.1_FirmControls/latest/stats.json` - Construction statistics

  **Key Operations:**
  - Calculate R&D intensity
  - Calculate capital expenditure intensity
  - Calculate dividend payer indicator
  - Calculate industry controls (SIC codes)
  - Outlier detection and winsorization

  **Configuration:**
  - Control definitions: defined in `config/project.yaml`

  #### 3.2_MarketVariables.py

  **Purpose:** Construct market-level variables

  **Inputs:**
  - `4_Outputs/3.0_BuildFinancialFeatures/latest/financial_features.csv`
  - `1_Inputs/crsp_monthly.csv`

  **Outputs:**
  - `4_Outputs/3.2_MarketVariables/latest/market_variables.csv` - Market variables
  - `4_Outputs/3.2_MarketVariables/latest/stats.json` - Construction statistics

  **Key Operations:**
  - Calculate stock returns (monthly, annual)
  - Calculate volatility (std dev of returns)
  - Calculate trading volume
  - Calculate bid-ask spread
  - Calculate market index returns

  **Configuration:**
  - Variable definitions: defined in `config/project.yaml`

  #### 3.3_EventFlags.py

  **Purpose:** Generate event flags for control variables

  **Inputs:**
  - `4_Outputs/3.0_BuildFinancialFeatures/latest/financial_features.csv`

  **Outputs:**
  - `4_Outputs/3.3_EventFlags/latest/event_flags.csv` - Event flags
  - `4_Outputs/3.3_EventFlags/latest/stats.json` - Event statistics

  **Key Operations:**
  - Identify earnings announcements
  - Identify CEO turnover events
  - Identify M&A activity
  - Identify restatements

  **Configuration:**
  - Event definitions: defined in `config/project.yaml`

  ### Step 4: Econometric Analysis

  #### 4.1_EstimateCeoClarity.py

  **Purpose:** Estimate CEO clarity score from linguistic features

  **Inputs:**
  - `4_Outputs/2.1_ExtractFeatures/latest/text_features.csv`
  - `4_Outputs/3.1_FirmControls/latest/firm_controls.csv`

  **Outputs:**
  - `4_Outputs/4.1_EstimateCeoClarity/latest/ceo_clarity_estimates.csv` - CEO clarity scores
  - `4_Outputs/4.1_EstimateCeoClarity/latest/stats.json` - Regression statistics

  **Key Operations:**
  - Estimate regression model: clarity ~ linguistic features + controls
  - Extract CEO clarity coefficient
  - Calculate standard errors
  - Perform regression diagnostics (residuals, multicollinearity)
  - Generate predictions

  **Configuration:**
  - Model specification: defined in `config/project.yaml`

  #### 4.2_LiquidityRegressions.py

  **Purpose:** Estimate liquidity regressions with CEO clarity

  **Inputs:**
  - `4_Outputs/3.2_MarketVariables/latest/market_variables.csv`
  - `4_Outputs/4.1_EstimateCeoClarity/latest/ceo_clarity_estimates.csv`

  **Outputs:**
  - `4_Outputs/4.2_LiquidityRegressions/latest/liquidity_results.csv` - Regression results
  - `4_Outputs/4.2_LiquidityRegressions/latest/stats.json` - Regression statistics

  **Key Operations:**
  - Calculate illiquidity measures (Amihud, bid-ask spread)
  - Estimate regression: illiquidity ~ ceo_clarity + controls + fixed effects
  - Cluster standard errors by firm and/or year
  - Perform robustness checks (alternative illiquidity measures)

  **Configuration:**
  - Model specification: defined in `config/project.yaml`

  #### 4.3_TakeoverHazards.py

  **Purpose:** Estimate takeover hazard models with CEO clarity

  **Inputs:**
  - `4_Outputs/3.3_EventFlags/latest/event_flags.csv`
  - `4_Outputs/4.1_EstimateCeoClarity/latest/ceo_clarity_estimates.csv`

  **Outputs:**
  - `4_Outputs/4.3_TakeoverHazards/latest/takeover_hazards.csv` - Hazard model results
  - `4_Outputs/4.3_TakeoverHazards/latest/stats.json` - Model statistics

  **Key Operations:**
  - Define takeover event (dependent variable)
  - Estimate Cox proportional hazards model
  - Calculate hazard ratios
  - Test proportional hazards assumption
  - Generate survival curves

  **Configuration:**
  - Model specification: defined in `config/project.yaml`
  ```
  </action>
  <verify>
  README.md documents each script's purpose, inputs, and outputs.
  </verify>
  <done>
  Script documentation added to README.md.
  </done>
</task>

<task type="auto">
  <name>Task 9: Add final sections to README.md</name>
  <files>README.md</files>
  <action>
  Add final sections to README.md (troubleshooting, citation, license):

  1. **Add Final Sections:**
  ```markdown
  ## Troubleshooting

  ### Common Issues

  **WRDS Connection Failed**
  - Verify WRDS credentials are correct
  - Check network connectivity
  - Ensure WRDS account is active

  **Missing Data Files**
  - Verify input files exist in `1_Inputs/`
  - Check that previous steps completed successfully
  - Verify `latest/` symlinks are updated

  **Script Fails with Memory Error**
  - Increase available memory
  - Process data in smaller batches (configure in `config/project.yaml`)

  **Output Directory Not Found**
  - Run scripts sequentially, not in parallel
  - Check permissions on `4_Outputs/` directory

  **Python Version Incompatibility**
  - Ensure Python >= 3.9.0
  - Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

  ## Logs

  All script executions produce logs in `3_Logs/`:
  - Format: `3_Logs/<step_id>_<timestamp>.log`
  - Content: Progress output, warnings, errors
  - Optional: `.jsonl` companion file for structured logs

  To check the most recent log:
  ```bash
  tail -f 3_Logs/<latest_script_log>.log
  ```

  ## Reproducibility

  To ensure reproducibility:
  - Use the exact versions in `requirements.txt`
  - Run scripts in sequence (not in parallel)
  - Use the same `config/project.yaml` parameters
  - Set random seeds (defined in `config/project.yaml`)
  - Verify input file checksums in logs

  ## Citation

  If you use this code or data in your research, please cite:

  ```bibtex
  @article{author_year_ceo_clarity,
    title={CEO Clarity and Firm Outcomes: Evidence from Earnings Conference Calls},
    author={Your Name},
    journal={Journal Name},
    year={2024}
  }
  ```

  ## License

  [Specify license, e.g., MIT License, Apache 2.0, etc.]

  ## Contact

  For questions or issues, please contact:
  - Email: your.email@example.com
  - GitHub Issues: [repository-url]/issues

  ## Acknowledgments

  - WRDS for providing financial data access
  - [Other acknowledgments as appropriate]

  ## References

  - Amihud, Y. (2002). Illiquidity and stock returns: Cross-section and time-series effects. Journal of Financial Markets, 5(1), 31-56.
  - [Add other relevant references]
  ```
  </action>
  <verify>
  README.md contains troubleshooting, citation, license, and contact sections.
  </verify>
  <done>
  Final sections added to README.md.
  </done>
</task>

<task type="auto">
  <name>Task 10: Create SUMMARY.md</name>
  <files>.planning/phases/05-readme-documentation/SUMMARY.md</files>
  <action>
  Create a summary document at `.planning/phases/05-readme-documentation/SUMMARY.md` documenting:

  1. **Documentation Deliverables:**
  - requirements.txt created with Python version and pinned dependencies
  - README.md created with all required sections (DOC-01 through DOC-07)

  2. **Requirements Checklist (DOC-01):**
  - [x] Python version specified
  - [x] All dependencies listed
  - [x] Versions pinned for reproducibility

  3. **Execution Instructions (DOC-02):**
  - [x] Numbered step-by-step instructions
  - [x] Copy-paste ready commands
  - [x] Complete pipeline execution sequence
  - [x] One-line execution option
  - [x] Output verification commands

  4. **Program-to-Output Mapping (DOC-03):**
  - [x] Script to output table created
  - [x] Links to paper tables/figures
  - [x] Final dataset documented

  5. **Pipeline Flow Diagram (DOC-04):**
  - [x] Mermaid diagram created
  - [x] Shows data flow from scripts to outputs
  - [x] Color-coded by pipeline stage

  6. **Variable Codebook (DOC-05):**
  - [x] Linguistic features documented
  - [x] Financial features documented
  - [x] Firm controls documented
  - [x] Market variables documented
  - [x] Event flags documented
  - [x] Dependent variables documented
  - [x] Identifiers documented
  - [x] Each variable includes: type, description, source, range

  7. **Script Documentation (DOC-06):**
  - [x] All scripts documented
  - [x] Each script includes: purpose, inputs, outputs, key operations
  - [x] Organized by pipeline step

  8. **Data Sources (DOC-07):**
  - [x] CRSP documented
  - [x] Compustat documented
  - [x] Execucomp documented
  - [x] Transcripts documented
  - [x] Sample selection described
  - [x] Data limitations noted

  9. **Additional Sections:**
  - [x] Troubleshooting guide
  - [x] Logs documentation
  - [x] Reproducibility guidelines
  - [x] Citation instructions
  - [x] License section
  - [x] Contact information
  - [x] Acknowledgments
  - [x] References

  10. **Documentation Quality:**
  - All requirements satisfied
  - Clear and comprehensive
  - Suitable for thesis/journal submission
  - Reproducible pipeline documented

  11. **Issues Found (if any):**
  - Issue description
  - Severity
  - Resolution

  12. **Next Steps:**
  - All documentation complete
  - Ready for submission
  - Any refinements needed based on reviewer feedback

  Write to `.planning/phases/05-readme-documentation/SUMMARY.md`
  </action>
  <verify>
  SUMMARY.md exists and documents all documentation deliverables and requirements satisfaction.
  </verify>
  <done>
  Complete summary document created for Phase 5 documentation.
  </done>
</task>

</tasks>

<verification>
- [ ] requirements.txt exists in project root
- [ ] requirements.txt contains Python version specification
- [ ] requirements.txt contains pinned dependencies
- [ ] README.md exists in project root
- [ ] README.md contains step-by-step execution instructions (DOC-02)
- [ ] README.md contains program-to-output mapping (DOC-03)
- [ ] README.md contains pipeline flow diagram (DOC-04)
- [ ] README.md contains variable codebook (DOC-05)
- [ ] README.md contains script documentation (DOC-06)
- [ ] README.md contains data sources documentation (DOC-07)
- [ ] README.md contains troubleshooting section
- [ ] README.md contains citation and license sections
- [ ] README.md is comprehensive and suitable for submission
- [ ] SUMMARY.md created in .planning/phases/05-readme-documentation/
</verification>

<success_criteria>
Phase 5 complete when:
1. requirements.txt exists with Python version and pinned dependencies (DOC-01)
2. README.md exists in project root
3. README.md contains numbered, copy-paste ready execution instructions (DOC-02)
4. README.md contains program-to-output mapping table (DOC-03)
5. README.md contains pipeline flow diagram (Mermaid or ASCII) (DOC-04)
6. README.md contains variable codebook for all final analysis variables (DOC-05)
7. README.md documents each script's purpose, inputs, and outputs (DOC-06)
8. README.md documents all data sources (CRSP, Compustat, Execucomp, transcripts) (DOC-07)
9. README.md contains troubleshooting, citation, and license sections
10. README.md is comprehensive and suitable for thesis/journal submission
11. SUMMARY.md documents all documentation deliverables and requirements satisfaction
</success_criteria>

<output>
After completion, create `.planning/phases/05-readme-documentation/SUMMARY.md`
</output>
