---
phase: quick-025
plan: constructvariables-descriptive-stats
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/shared/observability_utils.py
  - 2_Scripts/2_Text/2.2_ConstructVariables.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - Script generates INPUT statistics showing tokenized input files and manifest characteristics
    - Script generates PROCESS statistics showing speaker flagging distribution, variable creation counts, and NaN handling
    - Script generates OUTPUT statistics showing linguistic variable distributions, context-specific patterns, and temporal trends
    - All statistics saved to stats.json and included in report_step_2_2.md
  artifacts:
    - path: "2_Scripts/shared/observability_utils.py"
      provides: "ConstructVariables statistics functions"
      exports: ["compute_constructvariables_input_stats", "compute_constructvariables_process_stats", "compute_constructvariables_output_stats"]
    - path: "2_Scripts/2_Text/2.2_ConstructVariables.py"
      provides: "Enhanced variable construction statistics integration"
      contains: "comprehensive variable construction statistics"
  key_links:
    - from: "2_Scripts/2_Text/2.2_ConstructVariables.py"
      to: "2_Scripts/shared/observability_utils.py"
      via: "from shared.observability_utils import"
      pattern: "compute_constructvariables_(input|process|output)_stats"
---

<objective>
Add comprehensive descriptive statistics to script 2.2_ConstructVariables.py that provide publication-quality insights for the linguistic variable construction process, covering INPUT (tokenized files from step 2.1 and master manifest), PROCESS (speaker classification, context assignment, variable creation, NaN vs 0 handling), and OUTPUT (linguistic variable distributions, sample-context combinations, temporal patterns).

Purpose: Data scientists need professional, publication-ready descriptive statistics for the variable construction step to present to academic supervisors. This step constructs weighted percentage variables for 5 speaker types (Manager, Analyst, CEO, NonCEO_Manager, Entire) x 3 contexts (QA, Pres, All) x N linguistic categories (Negative, Positive, Uncertainty, etc.). Understanding speaker flagging success, variable coverage, and NaN handling is critical for methodological transparency.

Output: Extended stats.json and enhanced report_step_2_2.md with comprehensive descriptive statistics specific to variable construction.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/2_Text/2.2_ConstructVariables.py
@2_Scripts/shared/observability_utils.py
@.planning/quick/023-tokenize-descriptive-stats/023-PLAN.md

## Current State
Script 2.2_ConstructVariables.py currently collects:
- Basic counts: input rows (from manifest), output rows (per year), total rows across all years
- Speaker flagging counts: analyst_count, manager_count, ceo_count, operator_count (per year and total)
- Variables created count: number of linguistic variables created (per year)
- Standard stats: timing, memory, throughput, missing values, anomalies
- Linguistic categories: inherited from step 2.1 (Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining)

## Variable Construction Data Flow
1. INPUT: linguistic_counts_*.parquet files (from step 2.1) + master_sample_manifest.parquet (from step 1.0)
2. PROCESS: Load year files -> merge manifest info -> flag speakers (Analyst, Manager, CEO, Operator) -> assign context (QA/Pres) -> aggregate weighted percentages for 5 samples x 3 contexts x N categories
3. OUTPUT: linguistic_variables_*.parquet files (per year) with metadata + linguistic variables (e.g., Manager_QA_uncertainty_pct)

## Key Processing Details
- Speaker flagging uses: role keyword matching + employer matching + CEO name matching
- Context classification: QA (Q&A) vs Pres (Presentation) based on section type
- Weighted aggregation: (sum of category counts / sum of total_tokens) x 100
- NaN handling: Distinguishes between "No text in section" (NaN) vs "No linguistic matches" (0)
- Variable naming: {Sample}_{Context}_{Category}_pct (e.g., Manager_QA_uncertainty_pct)

## Current Statistics Gap
The script has basic per-year stats but lacks:
- INPUT: Detailed analysis of tokenized input files (rows, linguistic count distributions) and manifest characteristics
- PROCESS: Speaker flagging success rates (what % of speakers get flagged), context distribution (QA vs Pres), variable creation breakdown (how many variables per sample-context combo), NaN vs 0 analysis
- OUTPUT: Variable descriptive stats (min, max, mean, median, percentiles), sample-context specific patterns, temporal trends in variables, variable sparsity

## Existing Pattern from Quick Tasks 019-024
Previous tasks added specialized statistics functions to observability_utils.py:
- 019: General metadata stats (compute_input_stats, compute_temporal_stats, compute_entity_stats)
- 020: Entity linking stats (compute_linking_input_stats, compute_linking_process_stats, compute_linking_output_stats)
- 021: Tenure mapping stats (compute_tenure_input_stats, compute_tenure_process_stats, compute_tenure_output_stats)
- 023: Tokenization stats (compute_tokenize_input_stats, compute_tokenize_process_stats, compute_tokenize_output_stats)

For variable construction, we need specialized statistics that capture:
- Tokenized input file characteristics (rows, linguistic count distributions, total_tokens)
- Manifest info (CEO names, companies, temporal coverage)
- Speaker flagging success (flagged vs unflagged speakers, role distribution)
- Context distribution (QA vs Pres tokens)
- Variable creation metrics (5 samples x 3 contexts x N categories = total variables)
- NaN vs 0 analysis (what % of variables are NaN due to missing text vs 0 due to no matches)
- Output variable distributions (descriptive stats for each linguistic variable)
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add variable construction statistics functions to observability_utils.py</name>
  <files>2_Scripts/shared/observability_utils.py</files>
  <action>
Add three new variable construction-specific functions to observability_utils.py:

1. **compute_constructvariables_input_stats(input_dir, manifest_df, years_range)**: Analyze input data for variable construction
   - Tokenized files analysis: files present, total rows across all years, rows per year
   - Manifest analysis: unique gvkey, unique CEOs, temporal coverage (earliest/latest start_date)
   - Linguistic count columns: identify all {category}_count columns available from step 2.1
   - Total tokens analysis: sum of total_tokens across all input files
   - Returns dict with tokenized_files_stats, manifest_stats, linguistic_categories, total_tokens_available

2. **compute_constructvariables_process_stats(per_year_stats, total_speaker_flags, variables_created, duration_seconds)**: Analyze variable construction process
   - Speaker flagging metrics: total speakers flagged, flagging rate (flagged / total speakers), distribution by role (analyst, manager, ceo, operator)
   - Context distribution: QA vs Pres token counts (if available from input)
   - Variable creation metrics: total variables created, breakdown by sample-context combination (5 samples x 3 contexts = 15 combos), variables per linguistic category
   - NaN handling analysis: count of NaN values (missing sections) vs 0 values (no matches) in output
   - Efficiency metrics: calls processed per second, variables created per second
   - Returns dict with speaker_flagging_metrics, context_distribution, variable_creation_breakdown, nan_vs_zero_analysis, efficiency_metrics

3. **compute_constructvariables_output_stats(output_dfs, samples, contexts, categories)**: Analyze linguistic variables output
   - For each sample-context-category combination (e.g., Manager_QA_uncertainty_pct):
     - Descriptive statistics: mean, median, std, min, max, q25, q75
     - Percentiles: 10th, 25th, 50th, 75th, 90th, 95th, 99th
     - Zero vs NaN: count of zeros (no linguistic matches) vs NaN (no text in section)
   - Aggregate by sample: Manager variables, Analyst variables, CEO variables, etc.
   - Aggregate by context: QA variables vs Pres variables
   - Temporal trends: average variable values per year (for key variables like Manager_QA_uncertainty_pct)
   - Returns dict with variable_distributions, sample_aggregates, context_aggregates, temporal_trends

Requirements:
- All functions must be deterministic (sort outputs)
- Handle missing data gracefully (input files may not have all years)
- Return JSON-serializable types (no Timestamps, no NaN, use None or 0)
- Include docstrings following existing module style
- For output stats, accept list of DataFrames (per year) or single concatenated DataFrame
- Match the pattern established in compute_tokenize_*_stats functions
</action>
  <verify>
Run: python -c "from shared.observability_utils import compute_constructvariables_input_stats, compute_constructvariables_process_stats, compute_constructvariables_output_stats; print('Functions imported successfully')"
</verify>
  <done>
Three new variable construction statistics functions added to observability_utils.py, all importable and documented
</done>
</task>

<task type="auto">
  <name>Task 2: Integrate variable construction statistics into 2.2_ConstructVariables.py and create/enhance report</name>
  <files>2_Scripts/2_Text/2.2_ConstructVariables.py</files>
  <action>
Integrate the new statistics functions into 2.2_ConstructVariables.py:

**After loading manifest_df and identifying tokenized_dir (around line 587, after load_ceo_map):**
- Identify all years available in tokenized_dir (check for linguistic_counts_*.parquet)
- Call compute_constructvariables_input_stats(tokenized_dir, manifest_df, years_range)
- Store in stats["constructvariables_input"] = {...}

**After processing all years and aggregating stats (around line 609, after the for loop):**
- Call compute_constructvariables_process_stats(stats["processing"] if it exists, total_speaker_flags, variables_created, duration_seconds)
- Store in stats["constructvariables_process"] = {...}

**After saving output files (need to collect output DataFrames):**
- Collect per-year DataFrames during processing or load back after saving
- Identify samples = ["Manager", "Analyst", "CEO", "NonCEO_Manager", "Entire"]
- Identify contexts = ["QA", "Pres", "All"]
- Identify categories from count_cols (remove "_count" suffix)
- Call compute_constructvariables_output_stats(output_dfs, samples, contexts, categories)
- Store in stats["constructvariables_output"] = {...}

**Create report_step_2_2.md generation (add new function):**
Create a new report generation function that produces publication-ready sections:

## INPUT DATA
### Tokenized Files (from step 2.1)
- Files present and rows per year (table)
- Total rows across all years
- Total tokens available

### Master Manifest (from step 1.0)
- Unique companies (gvkey)
- Unique CEOs
- Temporal coverage (earliest/latest start_date)

### Linguistic Categories
- List of categories available (Negative, Positive, Uncertainty, etc.)

## VARIABLE CONSTRUCTION PROCESS
### Speaker Flagging Metrics
- Total speakers flagged (analyst, manager, ceo, operator)
- Flagging rate (flagged speakers / total speakers)
- Distribution by role (table)

### Context Distribution
- QA vs Pres tokens (if available)
- Percentage distribution

### Variable Creation Breakdown
- Total variables created (5 samples x 3 contexts x N categories)
- Variables per sample-context combination (table: 15 rows)
- Variables per linguistic category

### NaN vs Zero Analysis
- Count and percentage of NaN values (missing sections)
- Count and percentage of zero values (no linguistic matches)
- Methodological distinction explained

### Efficiency Metrics
- Calls processed per second
- Variables created per second

## OUTPUT SUMMARY
### Variable Distributions
For key sample-context-category combinations:
- Mean, median, std, min, max
- Percentiles (25th, 75th, 90th, 95th)
- Zero vs NaN breakdown

### Sample Aggregates
- Manager variables: average across all Manager variables
- Analyst variables: average across all Analyst variables
- CEO variables: average across all CEO variables
- NonCEO_Manager variables: average
- Entire variables: average

### Context Aggregates
- QA variables: average across all QA variables
- Pres variables: average across all Pres variables
- All variables: average across all context variables

### Temporal Trends
For key variables (e.g., Manager_QA_uncertainty_pct, Analyst_Pres_negative_pct):
- Average value per year (table)
- Trend direction (increasing/decreasing)

## PROCESS SUMMARY (existing, keep)
- Years processed, rows, duration

## OUTPUT SUMMARY (existing, keep)
- Final record count, files generated

**Update stats.json save:**
- Ensure save_stats() call includes all new stats sections

Requirements:
- Maintain existing functionality (no breaking changes)
- Use existing DualWriter for print output
- Format tables in markdown for readability
- Round percentages to 1-2 decimal places
- Match the visual style established in Quick Task 023 report
- Handle case where input files have missing years or missing columns
- Clarify the NaN vs 0 distinction (critical for methodology)
</action>
  <verify>
1. Run: python 2_Scripts/2_Text/2.2_ConstructVariables.py
2. Check stats.json contains new keys: constructvariables_input, constructvariables_process, constructvariables_output
3. Check report_step_2_2.md has new sections with properly formatted tables
4. Verify speaker flagging rate calculations are correct
5. Verify variable creation breakdown sums to total variables
</verify>
  <done>
Script runs successfully, stats.json contains all new variable construction statistics, report_step_2_2.md contains publication-ready INPUT, PROCESS, OUTPUT sections for variable construction
</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete variable construction statistics suite for step 2.2, including new functions in observability_utils.py and enhanced reporting in 2.2_ConstructVariables.py</what-built>
  <how-to-verify>
1. Run: python 2_Scripts/2_Text/2.2_ConstructVariables.py
2. Open the generated report: 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/report_step_2_2.md
3. Verify report contains:
   - INPUT DATA section with tokenized files stats (rows per year, total tokens) and manifest stats (unique companies, CEOs, temporal coverage)
   - VARIABLE CONSTRUCTION PROCESS section with speaker flagging metrics (flagging rate, distribution by role), context distribution (QA vs Pres), variable creation breakdown (5x3xN table), NaN vs zero analysis (methodological distinction), efficiency metrics
   - OUTPUT SUMMARY section with variable distributions (key sample-context-category combinations), sample aggregates, context aggregates, temporal trends
   - PROCESS SUMMARY section (existing)
   - OUTPUT SUMMARY section (existing)
4. Open stats.json and verify new keys: constructvariables_input, constructvariables_process, constructvariables_output
5. Assess if statistics accurately represent the variable construction process and are suitable for academic presentation
6. Check that the NaN vs 0 distinction is clearly explained (critical for methodology transparency)
</how-to-verify>
  <resume-signal>Type "approved" if the statistics meet presentation needs, or describe any additional metrics needed</resume-signal>
</task>

</tasks>

<verification>
After implementation:
1. Script executes without errors
2. stats.json contains new variable construction statistics keys
3. report_step_2_2.md has publication-ready tables and metrics
4. Speaker flagging rate and variable creation calculations are mathematically correct
5. NaN vs 0 analysis is clearly explained
6. Report format is suitable for academic supervisor presentation
</verification>

<success_criteria>
- Three new variable construction statistics functions in observability_utils.py
- Integration in 2.2_ConstructVariables.py adds comprehensive variable construction stats collection
- report_step_2_2.md contains INPUT (tokenized files + manifest), PROCESS (speaker flagging, context, variable creation, NaN/0 analysis), OUTPUT (distributions, aggregates, trends) sections
- All statistics are presentation-ready for academic supervisors
- NaN vs 0 distinction is clearly documented for methodology transparency
</success_criteria>

<output>
After completion, create `.planning/quick/025-add-constructvariables-descriptive-stats/025-SUMMARY.md`
</output>
