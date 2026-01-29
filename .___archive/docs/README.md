# F1D Clarity Measure

Dictionary-based clarity measure for earnings call transcripts using Loughran-McDonald Uncertainty and Weak Modal words.

## Measure Definitions

The pipeline generates **4 primary measures** combining datasets and dictionaries:

1. **MaQaUnc**: Manager Q&A × Uncertainty dictionary (297 tokens)
2. **MaPresUnc**: Manager Presentation × Uncertainty dictionary
3. **AnaQaUnc**: Analyst Q&A × Uncertainty dictionary
4. **MaQaNeg**: Manager Q&A × Negative dictionary (2,345 tokens)

**Formula**: `measure_pct = (# dictionary hits) / (# total word tokens)`

Computed over speaker-specific speech within context-specific sections of earnings calls (2002-2018).

## Project Status: ✅ COMPLETE

**All 7 processing steps completed successfully with quality controls**

**Final Dataset Statistics:**
- **286,652 enriched earnings calls** (2002-2018) with **100% gvkey coverage**
- **Quality-controlled**: 121,464 unmatched calls excluded for data integrity
- **Multi-tier CCM linking**: 70.2% PERMNO, 12.5% CUSIP8, 16.9% Fuzzy (≥92%), 0.4% Ticker
- **Wide format**: All 4 measures per call (MaQaUnc, MaPresUnc, AnaQaUnc, MaQaNeg)
- **Full industry coverage**: FF12 and FF48 classifications

## Directory Structure

```
F1D/
├── README.md                   # This file
├── 1_Inputs/                   # Input datasets (read-only)
│   ├── speaker_data_*.parquet  # Earnings call transcripts (17 years)
│   ├── Loughran-McDonald_*.csv # LM Master Dictionary
│   └── Unified-info.parquet    # Transcript metadata
├── 2_Scripts/                  # Processing scripts
│   ├── 2.0_UnifiedInfoCheck.py
│   ├── 2.1_BuildLmClarityDictionary.py
│   ├── 2.2_ExtractQaManagerDocs.py
│   ├── 2.3_TokenizeAndCount.cpp
│   ├── 2.4_BuildF1dPanel.py
│   ├── 2.5_LinkCcmAndIndustries.py
│   └── 2.6_CreateVisualizationsAndReports.py
├── 3_Logs/                     # Execution logs (timestamped)
│   └── 2.<step>_<Name>/
├── 4_Outputs/                  # Results (timestamped + latest/)
│   └── 2.<step>_<Name>/
│       ├── YYYY-MM-DD_HHMMSS/
│       └── latest/
└── config/
    └── project.yaml            # Central configuration

```

## Quick Start

### 1. Verify Setup
```bash
# Check inputs are present
ls 1_Inputs/

# Expected files:
# - speaker_data_2002.parquet through speaker_data_2018.parquet
# - Loughran-McDonald_MasterDictionary_1993-2024.csv
# - Unified-info.parquet
```

### 2. Run Processing Pipeline

**No flags required** - all parameters read from `config/project.yaml`

```bash
# STEP 00: Check Unified Info for duplicates
python 2_Scripts/2.0_UnifiedInfoCheck.py

# STEP 01: Build Clarity dictionary from LM
python 2_Scripts/2.1_BuildLmClarityDictionary.py

# STEP 02: Extract QA managerial documents
python 2_Scripts/2.2_ExtractQaManagerDocs.py

# STEP 03: Tokenize and count dictionary hits (C++)
2_Scripts/2.3_TokenizeAndCount

# STEP 04: Build call-level panel with metadata
python 2_Scripts/2.4_BuildF1dPanel.py

# STEP 05: Link to CCM and Fama-French industries
python 2_Scripts/2.5_LinkCcmAndIndustries.py

# STEP 06: Create visualizations and reports
python 2_Scripts/2.6_CreateVisualizationsAndReports.py
```

### 3. Check Results

```bash
# Latest outputs always in latest/ folder
ls 4_Outputs/2.1_BuildLmClarityDictionary/latest/

# Logs with timestamps
ls 3_Logs/2.1_BuildLmClarityDictionary/
```

## Processing Steps

### STEP 00: Unified Info Sanity Check
- **Script:** `2.0_UnifiedInfoCheck.py`
- **Purpose:** Detect duplicate `file_name` entries with different metadata
- **Outputs:**
  - `unified_info_duplicate_file_names.csv` - Collision report
  - `report_step_00.md` - Summary statistics

### STEP 01: Build LM Dictionaries
- **Script:** `2.1_BuildLmClarityDictionary.py`
- **Purpose:** Extract **two dictionaries** from LM Master Dictionary
- **Outputs:**
  - `lm_Uncertainty_dictionary.parquet` - Uncertainty dictionary (297 tokens)
  - `lm_Negative_dictionary.parquet` - Negative dictionary (2,345 tokens)
  - `report_step_01.md` - Token counts and examples

### STEP 02: Extract Filtered Docs (C++ v2)
- **Script:** `2.2v2a_ParquetToJson.py` (orchestrator) + `2.2v2b_ProcessManagerDocs.cpp` (processor)
- **Purpose:** Extract **3 datasets** by context and speaker role
- **Datasets:**
  - `manager_qa` - Managerial speech in Q&A sections
  - `manager_pres` - Managerial speech in presentation sections
  - `analyst_qa` - Analyst speech in Q&A sections
- **Year Alignment Fix (2.2v2e):** Re-sort records by actual year from start_date
- **Outputs:**
  - `{dataset}_docs_YYYY.parquet` - 3 datasets × 17 years = 51 files
  - Columns: file_name, doc_text, approx_char_len, start_date, quarter

### STEP 03: Tokenize & Count (C++)
- **Script:** `2.3a_TokenizeAndCount.py` (orchestrator) + `2.3b_TokenizeText.cpp` (tokenizer)
- **Purpose:** Heavy compute - tokenize and count for **2 dictionaries** × **3 datasets**
- **Algorithm:**
  - Normalize to uppercase ASCII
  - Tokenize by `[A-Z]+` pattern
  - Count tokens in Uncertainty and Negative dictionaries separately
  - Quarter-level processing, then aggregation to year level
- **Outputs:**
  - `{dataset}_call_YYYY.parquet` - 3 datasets × 17 years = 51 files
  - Columns: file_name, start_date, total_word_tokens, Uncertainty_hits, Negative_hits, unc_pct, neg_pct

### STEP 04: Build Measure Panels
- **Script:** `2.4_BuildF1dPanel.py`
- **Purpose:** Create **4 measure panels** from dataset × dictionary combinations
- **Measure Panels:**
  - MaQaUnc, MaPresUnc, AnaQaUnc, MaQaNeg
- **Processing:**
  - LEFT JOIN with Unified-info on `file_name`
  - Preserve individual call records (call-level, NO aggregation)
  - Include both `start_date` and `business_quarter`
- **Outputs:**
  - `{measure}_panel_YYYY.parquet` - 4 measures × 17 years = 68 files
  - `report_step_04.md` - Panel statistics

### STEP 05: Link CCM and Fama-French Industries
- **Script:** `2.5_LinkCcmAndIndustries.py`
- **Purpose:** Merge all 4 measures + CCM linking + industry classification + quality filtering
- **Multi-Tier Linking Strategy:**
  - **Tier 1 (Quality 100):** PERMNO + Date range matching (70.2%)
  - **Tier 2 (Quality 90):** CUSIP8 + Date range matching (12.5%)
  - **Tier 3 (Quality 70-80):** Fuzzy name matching with **threshold ≥92** (16.9%)
  - **Tier 4 (Quality 60):** Ticker + Date matching (0.4%)
- **Quality Controls Applied:**
  - **Fix #1:** Year alignment (via Step 2.2v2e re-sorting)
  - **Fix #2:** Filter unmatched records (only keep calls with valid gvkey)
  - **Fix #3:** Fuzzy threshold 92 (minimum similarity for Tier 3)
- **Industry Classification:**
  - Fama-French 12 industries (FF12)
  - Fama-French 48 industries (FF48)
  - Mapped from SIC codes in CCM
- **Outputs:**
  - `f1d_enriched_YYYY.parquet` - Final wide-format dataset (17 files)
  - All 4 measures per call (MaQaUnc, MaPresUnc, AnaQaUnc, MaQaNeg)
  - **100% gvkey coverage** (286,652 calls, 121,464 unmatched excluded)
  - `unmatched_calls_audit.csv` - Excluded calls for documentation
  - `report_step_2_5.md` - Comprehensive linking statistics

### STEP 06: Create Visualizations and Reports ✅
- **Script:** `2.6_CreateVisualizationsAndReports.py`
- **Purpose:** Generate publication-quality visualizations and comprehensive data analysis
- **Data Scope:** Only calls successfully linked to CCM/FF (297,697 calls with gvkey)
- **Analysis Components:**
  1. **F1D Distribution & Trends**
     - Call-level F1D distribution histogram with percentile markers
     - Temporal trends across all 12 FF12 industries (2002-2018)
     - Industry heatmap sorted by mean F1D (highest to lowest)
     - Early vs. late period industry ranking comparison
  2. **Panel Coverage & Continuity**
     - Stacked area chart of industry coverage over time
     - Quartile evolution showing F1D dispersion trends
     - Firm-level coverage heatmap showing reporting patterns
     - Survival curve analyzing firm presence duration
  3. **Data Quality Assessment**
     - Gap distribution histogram (quarters between consecutive calls)
     - Gap category analysis (perfect, minor, moderate, large gaps)
     - Reporting pattern classification (quarterly, semi-annual, annual)

- **Outputs:**
  - `figures/` - **11 publication-quality visualizations** (PDF + PNG at 300 DPI)
    - `f1d_distribution.pdf` - Histogram showing call counts across F1D range
    - `f1d_temporal_trend.pdf` - All 12 industries with modern distinguishable colors
    - `f1d_industry_heatmap.pdf` - Year × Industry heatmap sorted by mean F1D
    - `industry_ranking_comparison.pdf` - Top/bottom industries early vs. late
    - `panel_coverage_area.pdf` - Stacked area ordered by volume (thickest at bottom)
    - `quartile_evolution.pdf` - 25th/50th/75th/95th percentile trends
    - `gap_distribution_histogram.pdf` - Quarters between consecutive calls
    - `firm_coverage_heatmap.pdf` - Sample of 50 firms × quarters
    - `survival_curve.pdf` - Firm retention over time
    - `gap_categories_bar.pdf` - Perfect, minor, moderate, large gaps
    - `reporting_patterns.pdf` - Quarterly, semi-annual, annual frequencies

  - `tables/` - **6 statistical CSV tables**
    - `summary_statistics.csv` - Overall F1D statistics (mean, median, percentiles)
    - `yearly_statistics.csv` - F1D statistics by year (2002-2018)
    - `industry_statistics.csv` - F1D statistics by FF12 industry
    - `industry_yearly.csv` - Year × Industry matrix of mean F1D
    - `panel_continuity.csv` - Coverage rates and gap metrics by firm
    - `reporting_patterns.csv` - Calls per year by firm

  - `report.md` - **Comprehensive markdown report** with:
    - Dataset overview and summary statistics
    - Key findings on F1D distribution and trends
    - Industry analysis and rankings
    - Panel continuity assessment
    - Data quality metrics and recommendations

**Key Findings:**
- F1D distribution is highly right-skewed (most calls < 1% vagueness)
- Utilities, Finance, and Energy show highest linguistic vagueness
- 7 outlier calls with F1D = 25% (all retail companies in 2003Q1)
- 26.3% of firms have perfect quarterly coverage (no gaps)
- 57.2% of firms report quarterly, 33.8% semi-annually, 9.0% annually
- Median firm has only 1 quarter gap between consecutive calls

## Output Schemas

### lm_Clarity_dictionary.parquet
| Column | Type | Description |
|--------|------|-------------|
| `token` | STRING | Uppercase A-Z token |
| `source_flag` | STRING | "UNCERTAINTY", "WEAK_MODAL", or "BOTH" |

### qa_manager_docs_YYYY.parquet
| Column | Type | Description |
|--------|------|-------------|
| `file_name` | STRING | Transcript ID |
| `doc_text` | STRING | Concatenated managerial Q&A text |
| `approx_char_len` | INT | Length of doc_text |
| `year` | INT | Call year |

### f1d_call_YYYY.parquet
| Column | Type | Description |
|--------|------|-------------|
| `file_name` | STRING | Transcript ID |
| `total_word_tokens` | INT | Total word count |
| `Clarity_hits` | INT | Matches in Uncertainty ∪ Weak_Modal |
| `f1d_pct` | FLOAT | Clarity_hits / total_word_tokens |
| `top5_matches` | ARRAY<STRING> | Top 5 matched tokens |
| `process_version` | STRING | Version string (e.g., "F1D.1.0") |

### {measure}_panel_YYYY.parquet (Call-Level Panels)
4 separate measure panels: MaQaUnc, MaPresUnc, AnaQaUnc, MaQaNeg

| Column | Type | Description |
|--------|------|-------------|
| `file_name` | STRING | Transcript ID |
| `start_date` | STRING | Exact call datetime (ISO format) |
| `business_quarter` | STRING | Quarter (e.g., "2014Q3") |
| `permno` | STRING | CRSP identifier |
| `company_name` | STRING | Company name |
| `company_id` | STRING | Company ID |
| `cusip` | STRING | CUSIP identifier |
| `sedol` | STRING | SEDOL identifier |
| `isin` | STRING | ISIN identifier |
| `company_ticker` | STRING | Stock ticker |
| `total_tokens_{measure}` | INT | Total word tokens for this measure |
| `{Measure}_hits` | INT | Dictionary matches for this measure |
| `{Measure}_pct` | FLOAT | Percentage metric for this call |
| `process_version` | STRING | Version string (e.g., "F1D.1.0") |
| `had_duplicate_metadata` | BOOL | Duplicate `file_name` flag |

### f1d_enriched_YYYY.parquet (Final Wide-Format Dataset)
Merged all 4 measures with CCM linkage and industry classifications

| Column | Type | Description |
|--------|------|-------------|
| **Core Identifiers** |
| `file_name` | STRING | Transcript ID |
| `start_date` | STRING | Exact call datetime (ISO format) |
| `business_quarter` | STRING | Quarter (e.g., "2014Q3") |
| `permno` | STRING | CRSP identifier |
| `company_name` | STRING | Company name |
| `company_id` | STRING | Company ID |
| `cusip` | STRING | CUSIP identifier |
| `sedol` | STRING | SEDOL identifier |
| `isin` | STRING | ISIN identifier |
| `company_ticker` | STRING | Stock ticker |
| `process_version` | STRING | Version string |
| `had_duplicate_metadata` | BOOL | Duplicate metadata flag |
| **MaQaUnc Measure** |
| `total_tokens_maqaunc` | INT | Total tokens |
| `MaQaUnc_hits` | INT | Dictionary hits |
| `MaQaUnc_pct` | FLOAT | Percentage metric |
| **MaPresUnc Measure** |
| `total_tokens_mapresunc` | INT | Total tokens |
| `MaPresUnc_hits` | INT | Dictionary hits |
| `MaPresUnc_pct` | FLOAT | Percentage metric |
| **AnaQaUnc Measure** |
| `total_tokens_anaqaunc` | INT | Total tokens |
| `AnaQaUnc_hits` | INT | Dictionary hits |
| `AnaQaUnc_pct` | FLOAT | Percentage metric |
| **MaQaNeg Measure** |
| `total_tokens_maqaneg` | INT | Total tokens |
| `MaQaNeg_hits` | INT | Dictionary hits |
| `MaQaNeg_pct` | FLOAT | Percentage metric |
| **CCM Linkage** |
| `gvkey` | STRING | Compustat Global Company Key (NEVER null) |
| `ccm_conm` | STRING | Company name from CCM |
| `ccm_sic` | INT | SIC code from CCM |
| `ccm_cusip` | STRING | 9-digit CUSIP from CCM |
| `ccm_linkprim` | STRING | Link priority (P/C/J/N) |
| `ccm_linktype` | STRING | Link type (LC/LU) |
| `link_method` | STRING | Matching method (permno_date/cusip8_date/fuzzy_name/ticker_date) |
| `link_quality_score` | INT | Quality score (100/90/70-80/60) |
| `fuzzy_match_score` | FLOAT | Similarity score ≥92 (Tier 3 only) |
| `fuzzy_matched_name` | STRING | Matched CCM name (Tier 3 only) |
| `fuzzy_needs_review` | BOOL | Manual review flag (Tier 3 only) |
| **Industry Classifications** |
| `ff12_code` | INT | Fama-French 12 industry code |
| `ff12_name` | STRING | Fama-French 12 industry name |
| `ff48_code` | INT | Fama-French 48 industry code |
| `ff48_name` | STRING | Fama-French 48 industry name |

## Determinism Guarantees

All processing is **bitwise-identical** for the same inputs:

- Fixed random seed (42)
- Pinned thread count (1)
- Stable sort orders
- No filesystem ordering dependencies
- No wall-clock time effects
- Explicit tie-breaking rules for duplicates

## Final Dataset Characteristics

### Coverage Statistics (After Quality Controls)
- **Total enriched calls:** 286,652 (2002-2018) with **100% gvkey coverage**
- **Quality-controlled exclusions:** 121,464 unmatched calls (documented in audit file)
- **Multi-tier CCM linking distribution:**
  - Tier 1 (PERMNO + Date): 201,138 calls (70.2%)
  - Tier 2 (CUSIP8 + Date): 35,969 calls (12.5%)
  - Tier 3 (Fuzzy Name ≥92): 48,407 calls (16.9%)
  - Tier 4 (Ticker + Date): 1,138 calls (0.4%)
- **Wide-format structure:** All 4 measures per call (MaQaUnc, MaPresUnc, AnaQaUnc, MaQaNeg)
- **Full industry coverage:** 100% FF12 and FF48 classifications

### Measure-Specific Statistics
Statistics vary by measure (MaQaUnc, MaPresUnc, AnaQaUnc, MaQaNeg). See `report_step_2_5.md` for detailed distributions and `4_Outputs/2.6_CreateVisualizationsAndReports/latest/` for comprehensive analysis and visualizations.

### Data Quality Controls Applied
1. **100% gvkey coverage:** Only calls successfully linked to CCM are retained in final dataset
2. **Year alignment verified:** All calls sorted by actual start_date year (Fix #1 via Step 2.2v2e)
3. **Fuzzy matching quality:** Minimum 92% similarity threshold for Tier 3 matches (Fix #3)
4. **Multi-dataset architecture:** 3 separate datasets (manager_qa, manager_pres, analyst_qa) ensure clean speaker/context separation
5. **Audit trail maintained:** 121,464 excluded calls documented in `unmatched_calls_audit.csv` for transparency
6. **Deterministic processing:** Fixed seeds, stable sorts, explicit tie-breaking ensure reproducibility

## Accessing Results

### Latest Outputs Location
All final outputs available in timestamped directories with `latest/` symlink:

```bash
# Final enriched dataset (17 parquet files)
4_Outputs/2.5_LinkCcmAndIndustries/latest/f1d_enriched_YYYY.parquet

# Visualizations and reports
4_Outputs/2.6_CreateVisualizationsAndReports/latest/
├── figures/          # 11 PDF + PNG plots
├── tables/           # 6 CSV statistical tables
└── report.md         # Comprehensive findings report

# Audit files for review
4_Outputs/2.5_LinkCcmAndIndustries/latest/
├── fuzzy_matches_review.csv    # 3,667 fuzzy matches (Tier 3)
└── unmatched_calls_audit.csv   # 70,520 unmatched calls
```

### Quick Data Access Examples

**Load full enriched dataset:**
```python
import pandas as pd

# Load all years
dfs = [pd.read_parquet(f'4_Outputs/2.5_LinkCcmAndIndustries/latest/f1d_enriched_{year}.parquet')
       for year in range(2002, 2019)]
df_full = pd.concat(dfs, ignore_index=True)

# Filter to linked calls only
df_linked = df_full[df_full['gvkey'].notna()]
print(f"Total linked calls: {len(df_linked):,}")
```

**Analyze by industry:**
```python
industry_stats = df_linked.groupby('ff12_name').agg({
    'f1d_pct': ['mean', 'median', 'std'],
    'gvkey': 'nunique',
    'file_name': 'count'
})
print(industry_stats)
```

**Time series by firm:**
```python
firm_ts = df_linked[df_linked['gvkey'] == 'XXXXX'].sort_values('start_date')
print(firm_ts[['start_date', 'business_quarter', 'f1d_pct', 'company_name']])
```

## Requirements

### Python Dependencies
```bash
pip install pyarrow pandas pyyaml rapidfuzz matplotlib seaborn
```

### C++ Dependencies
- g++ compiler (C++17)
- Standard library only (no external dependencies)
- JSON I/O handled via standard library

## Configuration

All parameters in `config/project.yaml`:
- Input/output paths
- Year range (2002-2018)
- Random seed
- Thread count
- Managerial role keywords
- Exclusion keywords
- Compilation flags

## Known Limitations

1. **Quality-controlled exclusions:** 121,464 calls (42.4% of original dataset) excluded due to lack of CCM linkage
   - Primarily affects: small-cap firms, non-US companies, private firms, REITs
   - Trade-off: 100% data quality vs. broader coverage
   - Excluded calls documented in `unmatched_calls_audit.csv` for transparency

2. **Fuzzy matching reliance:** 48,407 calls (16.9% of final dataset) matched via Tier 3 fuzzy name matching
   - Quality threshold ≥92% similarity ensures high match quality
   - All fuzzy matches have quality scores 70-80 for manual review
   - Verification recommended for publication-critical analyses

3. **Speaker attribution gaps:** Early years (2002, 2014) have many empty `role`/`employer` fields
   - Conservative inclusion rules favor clear executives
   - May under-include some managerial turns in early years

4. **Unified Info duplicates:** Same `file_name` may have different metadata
   - Deterministic selection used at join time (validation_timestamp → start_date)
   - No editing of source data; all duplicates preserved in audit files

5. **Token ambiguity:** Some tokens counted without context disambiguation
   - Example: "MAY" counted regardless of month vs. modal usage
   - Consistent with minimal dictionary-based approach

6. **Multi-measure dependencies:** 4 measures share underlying tokenization
   - Errors in Step 2.2 or 2.3 propagate across all measures
   - Benefits: consistent methodology; Risks: correlated errors

## Research Applications

This dataset enables empirical research on:

### Corporate Communication
- **Linguistic vagueness** in managerial communication and its determinants
- **Information asymmetry** between managers and investors
- **Communication strategy** across industries and time periods
- **Regulatory events** impact on communication clarity

### Financial Economics
- **Earnings quality** and clarity of managerial explanations
- **Market reactions** to vague vs. clear earnings communications
- **Analyst forecasting** difficulty and managerial clarity
- **Cost of capital** implications of communication uncertainty

### Industry Analysis
- **Cross-industry variation** in communication norms (utilities vs. tech)
- **Competitive dynamics** and strategic ambiguity
- **Regulatory intensity** effects on disclosure clarity
- **Crisis periods** (2008-2009) communication patterns

### Panel Methods
- **Firm fixed effects** to control for persistent communication styles
- **Difference-in-differences** around regulatory/market events
- **Dynamic panel models** for persistence in vagueness over time
- **Survival analysis** of firm reporting patterns

### Example Research Questions
1. Do firms increase vagueness before bad news disclosures?
2. Is linguistic vagueness associated with higher analyst forecast dispersion?
3. Do institutional investors react differently to vague vs. clear calls?
4. How does managerial vagueness relate to future stock return volatility?
5. Are vague firms more likely to face SEC enforcement actions?

## Citation

If you use this dataset in your research, please cite:

```
F1D Clarity Measure Dataset (2002-2018)
Dictionary-based clarity measure for earnings call transcripts
Version: F1D.1.0
368,217 earnings calls from 7,989 firms
Linked to CRSP-Compustat Merged and Fama-French industries
```

## Troubleshooting

### Common Issues

**"File not found" errors:**
- Ensure you've run all previous steps in order (2.0 → 2.1 → ... → 2.6)
- Check that `latest/` symlinks were created successfully
- Verify input files exist in `1_Inputs/`

**C++ compilation fails:**
- Ensure g++ supports C++17: `g++ --version` should show ≥7.0
- C++ code uses standard library only (no external dependencies needed)
- Check compilation commands in respective Makefile files

**Memory errors on large datasets:**
- Step 2.3 (C++) most memory-intensive (~4-8GB peak)
- Consider processing year-by-year if limited RAM
- Check available disk space for parquet outputs (~10GB total)

**Determinism verification:**
- Run same step twice and compare outputs with `sha256sum`
- Ensure no parallel processing outside of configured thread count
- Verify config hasn't changed between runs

**Visualization rendering issues:**
- Install matplotlib backend: `pip install pyqt5` or use `Agg` backend
- Increase figure DPI in script if plots too small/large
- Check PDF viewer supports embedded fonts

### Performance Tips

1. **Parallel year processing:** Steps 2.2, 2.4, 2.5, 2.6 can process years in parallel (modify scripts)
2. **Arrow memory mapping:** Large parquet files use memory mapping (efficient for repeated reads)
3. **Partial dataset testing:** Modify `year_start`/`year_end` in config for faster iteration
4. **SSD recommended:** Significant I/O for 17 years × multiple steps
5. **Monitor logs:** All steps write progress to `3_Logs/` with timestamps and line counts

### Reproducing Results

To exactly reproduce published results:
```bash
# 1. Verify Git commit SHA
git log -1 --format="%H"

# 2. Check config hasn't changed
cat config/project.yaml

# 3. Clear all outputs
rm -rf 4_Outputs/*/

# 4. Run full pipeline
python 2_Scripts/2.0_UnifiedInfoCheck.py
python 2_Scripts/2.1_BuildLmClarityDictionary.py
python 2_Scripts/2.2_ExtractQaManagerDocs.py
./2_Scripts/2.3_TokenizeAndCount
python 2_Scripts/2.4_BuildF1dPanel.py
python 2_Scripts/2.5_LinkCcmAndIndustries.py
python 2_Scripts/2.6_CreateVisualizationsAndReports.py

# 5. Verify checksums
sha256sum 4_Outputs/*/latest/*.parquet
```

## Contact & Support

For questions, issues, or contributions:
- Review logs in `3_Logs/` for error details
- Check `report.md` files in each step's output directory
- Consult `.claude/CLAUDE.md` for project architecture decisions

## Version

**F1D.1.0** - Initial implementation (2025)
- Complete 7-step pipeline (2.0 → 2.6)
- Multi-tier CCM linking (80.8% match rate)
- 11 publication-quality visualizations
- Comprehensive data quality assessment
- 368,217 earnings calls from 7,989 firms (2002-2018)
