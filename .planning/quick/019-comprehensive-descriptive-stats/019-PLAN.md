---
phase: quick-019
plan: comprehensive-descriptive-stats
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/shared/observability_utils.py
  - 2_Scripts/1_Sample/1.1_CleanMetadata.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - Script generates comprehensive input statistics showing raw data characteristics
    - Script generates process statistics showing transformation steps
    - Script generates output statistics suitable for academic presentation
    - All statistics are saved to both stats.json and included in report_step_1_1.md
  artifacts:
    - path: "2_Scripts/shared/observability_utils.py"
      provides: "Extended descriptive statistics functions"
      exports: ["compute_input_stats", "compute_temporal_stats", "compute_entity_stats"]
    - path: "2_Scripts/1_Sample/1.1_CleanMetadata.py"
      provides: "Enhanced statistics integration"
      contains: "comprehensive descriptive statistics"
  key_links:
    - from: "2_Scripts/1_Sample/1.1_CleanMetadata.py"
      to: "2_Scripts/shared/observability_utils.py"
      via: "from shared.observability_utils import"
      pattern: "compute_(input|temporal|entity)_stats"
---

<objective>
Add comprehensive descriptive statistics to script 1.1_CleanMetadata.py that provide publication-quality insights for presenting to academic supervisors.

Purpose: Data scientists need professional, publication-ready descriptive statistics covering INPUT (what raw data looks like), PROCESS (what transformations happened), and OUTPUT (what cleaned data looks like) stages for supervisor presentations and method sections.

Output: Extended stats.json and enhanced report_step_1_1.md with comprehensive descriptive statistics including distributions, temporal coverage, entity characteristics, and data quality metrics.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/1_Sample/1.1_CleanMetadata.py
@2_Scripts/shared/observability_utils.py
@config/project.yaml

## Current State
Script 1.1_CleanMetadata.py currently collects:
- Basic counts (input rows, output rows, rows removed per step)
- Missing value analysis per column
- Timing and memory metrics
- Z-score anomaly detection on numeric columns

## Data Schema (from variable_reference.csv)
Key columns in metadata_cleaned.parquet:
- Identifiers: file_name, company_id, company_ticker, cusip, permno
- Temporal: start_date, business_quarter, source_file_year (2002-2018)
- Classification: event_type, event_type_name, city
- Quality: data_quality_score, processing_lag_hours
- Speaker: has_speaker_data, speaker_record_count

## Existing Statistics Framework
- observability_utils.py provides: analyze_missing_values, detect_anomalies_zscore, detect_anomalies_iqr
- stats.json structure: input, processing, output, missing_values, timing, memory, throughput, quality_anomalies
- report_step_1_1.md: Basic summary with row counts and column list
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add comprehensive descriptive statistics functions to observability_utils.py</name>
  <files>2_Scripts/shared/observability_utils.py</files>
  <action>
Add three new functions to observability_utils.py:

1. **compute_input_stats(df)**: Analyze raw input data characteristics
   - Record count, column count, memory footprint (MB)
   - Column type distribution (numeric, datetime, string, bool)
   - For numeric columns: min, max, mean, median, std, quartiles (25%, 75%)
   - For datetime columns: min date, max date, date range span
   - For string columns: avg length, max length, unique count, empty count
   - Cardinality analysis: distinct counts for key categorical columns
   - Returns dict with all metrics

2. **compute_temporal_stats(df, date_col='start_date')**: Temporal coverage analysis
   - Year distribution (count per year 2002-2018)
   - Month distribution (count per month)
   - Quarter distribution (count per quarter)
   - Day of week distribution
   - Date range: earliest, latest, span_days
   - Calls per year summary: mean, median, min, max
   - Completeness: coverage % of target years (2002-2018)
   - Returns dict with all temporal metrics

3. **compute_entity_stats(df)**: Entity and quality characteristics
   - Company coverage: unique companies, avg calls per company
   - Geographic coverage: unique cities, top N cities by call count
   - Data quality score distribution: mean, median, histogram buckets
   - Speaker data coverage: % with speaker data, speaker_record_count distribution
   - Processing lag stats: mean, median, min, max hours
   - Returns dict with all entity metrics

Requirements:
- All functions must be deterministic (sort outputs, no random operations)
- Handle missing values gracefully (skip or report)
- Return serializable types (no Timestamp objects, convert to ISO strings)
- Include docstrings following existing module style
</action>
  <verify>
Run pytest if tests exist, otherwise verify by:
python -c "from shared.observability_utils import compute_input_stats, compute_temporal_stats, compute_entity_stats; print('Functions imported successfully')"
</verify>
  <done>
Three new descriptive statistics functions added to observability_utils.py, all importable and documented
</done>
</task>

<task type="auto">
  <name>Task 2: Integrate comprehensive statistics into 1.1_CleanMetadata.py and enhance report</name>
  <files>2_Scripts/1_Sample/1.1_CleanMetadata.py</files>
  <action>
Integrate the new statistics functions into 1.1_CleanMetadata.py:

**After loading df (line ~304):**
- Call compute_input_stats(df) on raw input data
- Store in stats["input_descriptive"] = {...}

**After df_final is created (line ~366):**
- Call compute_temporal_stats(df_final, 'start_date')
- Store in stats["temporal_coverage"] = {...}
- Call compute_entity_stats(df_final)
- Store in stats["entity_characteristics"] = {...}

**Update report_step_1_1.md generation (lines ~428-458):**
Enhance the report with sections for INPUT, PROCESS, OUTPUT:

## INPUT DATA CHARACTERISTICS
- Total records, columns, memory footprint
- Column type breakdown
- Key distributions (data_quality_score, processing_lag_hours)
- Date range of source data

## TEMPORAL COVERAGE
- Calls per year (table format)
- Monthly distribution
- Quarter distribution
- Day of week pattern

## ENTITY CHARACTERISTICS
- Unique companies count, calls per company (mean, median, min, max)
- Geographic coverage (unique cities, top 5 cities)
- Data quality score distribution
- Speaker data availability

## PROCESS SUMMARY (existing, keep)
- Rows removed per step

## OUTPUT SUMMARY (existing, keep)
- Final record count

**Update stats.json save:**
- The save_stats() call at line 425 already handles nested structures, ensure new stats are included

Requirements:
- Maintain existing functionality (no breaking changes)
- Use existing DualWriter for all print output
- Format tables in markdown for report readability
- Round numeric values to 2-4 decimal places as appropriate
</action>
  <verify>
1. Run script locally: python 2_Scripts/1_Sample/1.1_CleanMetadata.py
2. Check stats.json contains new keys: input_descriptive, temporal_coverage, entity_characteristics
3. Check report_step_1_1.md has new sections with properly formatted tables
</verify>
  <done>
Script runs successfully, stats.json contains all new descriptive statistics, report_step_1_1.md contains publication-ready INPUT, TEMPORAL, ENTITY, PROCESS, and OUTPUT sections
</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete comprehensive descriptive statistics suite for step 1.1, including new functions in observability_utils.py and enhanced reporting in 1.1_CleanMetadata.py</what-built>
  <how-to-verify>
1. Run: python 2_Scripts/1_Sample/1.1_CleanMetadata.py
2. Open the generated report: 4_Outputs/1.1_CleanMetadata/latest/report_step_1_1.md
3. Verify report contains:
   - INPUT DATA CHARACTERISTICS section with record counts, column types, distributions
   - TEMPORAL COVERAGE section with calls per year table, monthly/quarterly distributions
   - ENTITY CHARACTERISTICS section with company stats, geographic coverage, quality metrics
   - PROCESS SUMMARY section (existing)
   - OUTPUT SUMMARY section (existing)
4. Open stats.json and verify new keys: input_descriptive, temporal_coverage, entity_characteristics
5. Assess if statistics are suitable for academic presentation
</how-to-verify>
  <resume-signal>Type "approved" if the statistics meet presentation needs, or describe any additional metrics needed</resume-signal>
</task>

</tasks>

<verification>
After implementation:
1. Script executes without errors
2. stats.json contains new descriptive statistics keys
3. report_step_1_1.md has publication-ready tables and metrics
4. All statistics are accurate and reproducible
5. Report format is suitable for academic supervisor presentation
</verification>

<success_criteria>
- Three new descriptive statistics functions in observability_utils.py
- Integration in 1.1_CleanMetadata.py adds comprehensive stats collection
- report_step_1_1.md contains INPUT, TEMPORAL, ENTITY, PROCESS, OUTPUT sections
- All statistics are presentation-ready for academic supervisors
</success_criteria>

<output>
After completion, create `.planning/quick/019-comprehensive-descriptive-stats/019-SUMMARY.md`
</output>
