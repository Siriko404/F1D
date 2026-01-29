---
phase: quick-023
plan: tokenize-descriptive-stats
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/shared/observability_utils.py
  - 2_Scripts/2_Text/2.1_TokenizeAndCount.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - Script generates INPUT statistics showing manifest file and LM dictionary characteristics
    - Script generates PROCESS statistics showing tokenization performance, vocabulary coverage, and category hit rates
    - Script generates OUTPUT statistics showing linguistic counts distribution, speaker-level analysis, and per-year breakdowns
    - All statistics saved to stats.json and included in report_step_2_1.md
  artifacts:
    - path: "2_Scripts/shared/observability_utils.py"
      provides: "Tokenization statistics functions"
      exports: ["compute_tokenize_input_stats", "compute_tokenize_process_stats", "compute_tokenize_output_stats"]
    - path: "2_Scripts/2_Text/2.1_TokenizeAndCount.py"
      provides: "Enhanced tokenization statistics integration"
      contains: "comprehensive tokenization statistics"
  key_links:
    - from: "2_Scripts/2_Text/2.1_TokenizeAndCount.py"
      to: "2_Scripts/shared/observability_utils.py"
      via: "from shared.observability_utils import"
      pattern: "compute_tokenize_(input|process|output)_stats"
---

<objective>
Add comprehensive descriptive statistics to script 2.1_TokenizeAndCount.py that provide publication-quality insights for the text tokenization and linguistic counting process, covering INPUT (manifest file and LM dictionary), PROCESS (tokenization performance, vocabulary coverage, category hit rates), and OUTPUT (linguistic counts distribution, speaker-level analysis, per-year breakdowns).

Purpose: Data scientists need professional, publication-ready descriptive statistics for the tokenization step to present to academic supervisors. This step tokenizes earnings call transcripts using the Loughran-McDonald master dictionary and calculates linguistic measures (positive, negative, uncertainty words). Understanding vocabulary coverage, category hit rates, and tokenization performance is critical for methodological transparency.

Output: Extended stats.json and enhanced report_step_2_1.md with comprehensive descriptive statistics specific to tokenization and linguistic counting.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/2_Text/2.1_TokenizeAndCount.py
@2_Scripts/shared/observability_utils.py
@.planning/quick/019-comprehensive-descriptive-stats/019-PLAN.md

## Current State
Script 2.1_TokenizeAndCount.py currently collects:
- Basic counts (input rows, output rows, filtered rows per year)
- Total tokens and vocabulary hits (aggregate)
- Vocabulary size
- Per-year stats (input_rows, output_rows, filtered_rows, total_tokens, vocab_hits, avg_tokens_per_doc)
- Standard stats (timing, memory, throughput, missing values, anomalies)
- LM dictionary categories: Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining

## Tokenization Data Flow
1. INPUT: master_sample_manifest.parquet (from step 1.4) + Loughran-McDonald_MasterDictionary_1993-2024.csv
2. PROCESS: Load year files -> filter by manifest -> vectorize with CountVectorizer -> count per category
3. OUTPUT: linguistic_counts_*.parquet files (per year) with category counts and total_tokens

## Linguistic Categories (Loughran-McDonald)
- Negative: Words indicating negative sentiment
- Positive: Words indicating positive sentiment
- Uncertainty: Words indicating uncertainty/hedging
- Litigious: Words indicating legal/litigious language
- Strong_Modal: Words indicating strong modality (shall, must, etc.)
- Weak_Modal: Words indicating weak modality (could, might, etc.)
- Constraining: Words indicating constraints/restrictions

## Current Statistics Gap
The script has basic per-year stats but lacks:
- INPUT: Detailed analysis of manifest file (date range, unique companies, event types) and LM dictionary (word counts per category)
- PROCESS: Category hit rates (what % of tokens match each category), vocabulary coverage (OOV rate), tokenization efficiency metrics
- OUTPUT: Distribution of linguistic counts (percentiles, zero counts), speaker-level analysis (role breakdown), correlation between categories

## Existing Pattern from Quick Tasks 019, 020, 021
Previous tasks added specialized statistics functions to observability_utils.py:
- 019: compute_input_stats, compute_temporal_stats, compute_entity_stats (general metadata)
- 020: compute_linking_input_stats, compute_linking_process_stats, compute_linking_output_stats (entity linking)
- 021: compute_tenure_input_stats, compute_tenure_process_stats, compute_tenure_output_stats (tenure mapping)

For tokenization, we need specialized statistics that capture:
- LM dictionary characteristics (words per category, overlap between categories)
- Tokenization performance (docs/sec, tokens/sec)
- Category hit rates (coverage % of total tokens)
- Linguistic count distributions (min, max, mean, median, percentiles per category)
- Speaker-level breakdown (by role: CEO, CFO, Analyst, etc.)
- Per-year trends in linguistic measures
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add tokenization statistics functions to observability_utils.py</name>
  <files>2_Scripts/shared/observability_utils.py</files>
  <action>
Add three new tokenization-specific functions to observability_utils.py:

1. **compute_tokenize_input_stats(manifest_df, lm_dict_path, vocab_list, cat_sets)**: Analyze input data and dictionary
   - Manifest analysis: total files, unique companies (if available), date range (if available), event type distribution
   - LM dictionary analysis: total words, words per category (Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining)
   - Category overlap analysis: how many words belong to multiple categories
   - Vocabulary characteristics: avg word length, word length distribution
   - Returns dict with manifest_stats, dictionary_stats, category_breakdown, overlap_analysis

2. **compute_tokenize_process_stats(per_year_stats, cat_sets, vocab_list, duration_seconds)**: Analyze tokenization process
   - Volume metrics: total input rows, total output rows, total tokens, total vocab hits
   - Coverage metrics: vocab_hit_rate (vocab_hits / total_tokens), oov_rate (1 - hit_rate)
   - Category hit rates: per category, what % of total tokens match
   - Efficiency metrics: docs per second, tokens per second, tokens per doc (mean, median, min, max)
   - Year-over-year trends: tokens per year trend, vocab_hits per year trend
   - Parallelization efficiency: workers used, years processed
   - Returns dict with volume_metrics, coverage_metrics, category_hit_rates, efficiency_metrics, yearly_trends

3. **compute_tokenize_output_stats(output_dfs, cat_sets)**: Analyze linguistic counts output
   - For each category (Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining):
     - Count statistics: mean, median, std, min, max, q25, q75, zeros_count
     - Distribution analysis: percentile values (10th, 25th, 50th, 75th, 90th, 95th, 99th)
   - total_tokens statistics: mean, median, std, min, max, percentiles
   - Speaker-level analysis (if role column exists): counts by role, avg tokens per role, category counts per role
   - Sparsity analysis: % of zero counts per category
   - Correlation analysis (optional, computationally expensive): correlation between major categories (Positive vs Negative, Uncertainty vs others)
   - Returns dict with category_distributions, total_tokens_stats, speaker_analysis, sparsity_analysis

Requirements:
- All functions must be deterministic (sort outputs)
- Handle missing columns gracefully (role, speaker_name may not exist)
- Return JSON-serializable types (no Timestamps, no NaN, use None or 0)
- Include docstrings following existing module style
- For output stats, accept list of DataFrames (per year) or single concatenated DataFrame
</action>
  <verify>
Run: python -c "from shared.observability_utils import compute_tokenize_input_stats, compute_tokenize_process_stats, compute_tokenize_output_stats; print('Functions imported successfully')"
</verify>
  <done>
Three new tokenization statistics functions added to observability_utils.py, all importable and documented
</done>
</task>

<task type="auto">
  <name>Task 2: Integrate tokenization statistics into 2.1_TokenizeAndCount.py and create/enhance report</name>
  <files>2_Scripts/2_Text/2.1_TokenizeAndCount.py</files>
  <action>
Integrate the new statistics functions into 2.1_TokenizeAndCount.py:

**After loading manifest and LM dictionary (after line 715, where vocab_list and cat_sets are available):**
- Load full manifest with columns for input analysis (need more columns than just file_name)
- Call compute_tokenize_input_stats(manifest, lm_path, vocab_list, cat_sets)
- Store in stats["tokenize_input"] = {...}

**After processing all years and aggregating stats (after line 798, before summary stats):**
- Call compute_tokenize_process_stats(stats["processing"]["per_year"], cat_sets, vocab_list, duration_seconds)
- Store in stats["tokenize_process"] = {...}

**After saving output files (need to load back or collect during processing):**
Two approaches:
   A) Collect per-year DataFrames during processing in a list
   B) Load output files after saving
- Call compute_tokenize_output_stats(output_dfs, cat_sets)
- Store in stats["tokenize_output"] = {...}

**Create report_step_2_1.md generation (add new function):**
Create a new report generation function that produces publication-ready sections:

## INPUT DATA
### Manifest File (from step 1.4)
- Total files in manifest
- Date range (if available in manifest)
- Unique companies (if available)
- Event type distribution

### Loughran-McDonald Dictionary
- Total vocabulary words
- Words per category (table)
- Category overlap analysis (words in multiple categories)
- Word length characteristics

## TOKENIZATION PROCESS
### Volume Metrics
- Total input rows, output rows
- Total tokens processed
- Total vocabulary hits

### Coverage Metrics
- Vocabulary hit rate (vocab_hits / total_tokens)
- Out-of-vocabulary rate
- Per-category hit rates (table)

### Efficiency Metrics
- Documents per second
- Tokens per second
- Avg tokens per document (mean, median, min, max)
- Years processed with parallelization (workers used)

### Yearly Trends
- Tokens per year (table)
- Vocabulary hits per year (table)

## OUTPUT SUMMARY
### Category Count Distributions
For each category (Negative, Positive, Uncertainty, etc.):
- Mean, median, std, min, max
- Percentiles (25th, 75th, 90th, 95th, 99th)
- Zero count (% of documents with zero hits)

### Total Tokens Statistics
- Mean, median, std, min, max
- Percentiles

### Speaker-Level Analysis (if role available)
- Documents per role
- Avg tokens per role
- Avg category counts per role

### Sparsity Analysis
- Percentage of zero counts per category
- Documents with no linguistic matches

## PROCESS SUMMARY (existing, keep)
- Years processed, rows removed, duration

## OUTPUT SUMMARY (existing, keep)
- Final record count, files generated

**Update stats.json save:**
- Ensure save_stats() call includes all new stats sections

Requirements:
- Maintain existing functionality (no breaking changes)
- Use existing DualWriter for print output
- Format tables in markdown for readability
- Round percentages to 1-2 decimal places
- Match the visual style established in 1.1, 1.2, 1.3 reports
- Handle case where manifest columns are limited (may need to load more columns or skip some analyses)
</action>
  <verify>
1. Run: python 2_Scripts/2_Text/2.1_TokenizeAndCount.py
2. Check stats.json contains new keys: tokenize_input, tokenize_process, tokenize_output
3. Check report_step_2_1.md has new sections with properly formatted tables
4. Verify category hit rate calculations are correct
</verify>
  <done>
Script runs successfully, stats.json contains all new tokenization statistics, report_step_2_1.md contains publication-ready INPUT, PROCESS, OUTPUT sections for tokenization
</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete tokenization statistics suite for step 2.1, including new functions in observability_utils.py and enhanced reporting in 2.1_TokenizeAndCount.py</what-built>
  <how-to-verify>
1. Run: python 2_Scripts/2_Text/2.1_TokenizeAndCount.py
2. Open the generated report: 4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/report_step_2_1.md
3. Verify report contains:
   - INPUT DATA section with manifest file stats and LM dictionary breakdown (words per category, overlaps)
   - TOKENIZATION PROCESS section with volume metrics, coverage metrics (hit rates), efficiency metrics, yearly trends
   - OUTPUT SUMMARY section with category count distributions, total tokens stats, speaker analysis (if available), sparsity analysis
   - PROCESS SUMMARY section (existing)
   - OUTPUT SUMMARY section (existing)
4. Open stats.json and verify new keys: tokenize_input, tokenize_process, tokenize_output
5. Assess if statistics accurately represent the tokenization process and are suitable for academic presentation
</how-to-verify>
  <resume-signal>Type "approved" if the statistics meet presentation needs, or describe any additional metrics needed</resume-signal>
</task>

</tasks>

<verification>
After implementation:
1. Script executes without errors
2. stats.json contains new tokenization statistics keys
3. report_step_2_1.md has publication-ready tables and metrics
4. Hit rate and coverage calculations are mathematically correct
5. Report format is suitable for academic supervisor presentation
</verification>

<success_criteria>
- Three new tokenization statistics functions in observability_utils.py
- Integration in 2.1_TokenizeAndCount.py adds comprehensive tokenization stats collection
- report_step_2_1.md contains INPUT (manifest+LM dictionary), PROCESS (volume, coverage, efficiency, trends), OUTPUT (distributions, speaker analysis, sparsity) sections
- All statistics are presentation-ready for academic supervisors
</success_criteria>

<output>
After completion, create `.planning/quick/023-tokenize-descriptive-stats/023-SUMMARY.md`
</output>
