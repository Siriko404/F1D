---
phase: quick-022
plan: comprehensive-descriptive-stats-manifest
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/shared/observability_utils.py
  - 2_Scripts/1_Sample/1.4_AssembleManifest.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - Script generates INPUT statistics showing linked metadata and tenure panel characteristics
    - Script generates PROCESS statistics showing merge outcomes (matched/unmatched rates)
    - Script generates OUTPUT statistics showing final manifest dimensions, CEO distribution, industry coverage
    - Script generates SAMPLE examples (CEO call distribution by CEO, top/bottom CEOs by call count)
    - All statistics saved to stats.json and included in report_step_1_4.md
  artifacts:
    - path: "2_Scripts/shared/observability_utils.py"
      provides: "Manifest assembly statistics functions"
      exports: ["compute_manifest_input_stats", "compute_manifest_process_stats", "compute_manifest_output_stats", "collect_ceo_distribution_samples"]
    - path: "2_Scripts/1_Sample/1.4_AssembleManifest.py"
      provides: "Enhanced manifest assembly statistics integration"
      contains: "comprehensive manifest statistics"
  key_links:
    - from: "2_Scripts/1_Sample/1.4_AssembleManifest.py"
      to: "2_Scripts/shared/observability_utils.py"
      via: "from shared.observability_utils import"
      pattern: "compute_manifest_(input|process|output)_stats|collect_ceo_distribution_samples"
---

<objective>
Add comprehensive descriptive statistics to script 1.4_AssembleManifest.py that provide publication-quality insights for the manifest assembly process, covering INPUT (linked metadata + tenure panel), PROCESS (merge outcomes + CEO threshold filtering), and OUTPUT (final manifest characteristics).

Purpose: Data scientists need professional, publication-ready descriptive statistics for the final manifest assembly step to present to academic supervisors. This step combines outputs from 1.2 (linked metadata) and 1.3 (tenure panel) to create the master sample manifest that defines the universe of analysis. Understanding merge success rates, CEO filtering impact, and final sample characteristics is critical for methodological transparency.

Output: Extended stats.json and enhanced report_step_1_4.md with comprehensive descriptive statistics specific to manifest assembly, including CEO distribution samples.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/1_Sample/1.4_AssembleManifest.py
@2_Scripts/shared/observability_utils.py
@2_Scripts/1_Sample/1.2_LinkEntities.py
@2_Scripts/1_Sample/1.3_BuildTenureMap.py

## Current State
Script 1.4_AssembleManifest.py currently collects:
- Basic input counts (metadata calls, tenure monthly records)
- Merge statistics (matched/unmatched counts)
- CEO filtering statistics (CEOs with >= min_calls threshold)
- Standard stats (timing, memory, throughput, missing values, anomalies)
- Industry distribution (ff12_code)
- Year distribution (by_year)
- Unique firms count

## Manifest Assembly Data Flow
1. INPUT: metadata_linked.parquet (from step 1.2) + tenure_monthly.parquet (from step 1.3)
2. PROCESS: Join on (gvkey, year, month) -> Filter unmatched calls -> Apply min call threshold per CEO
3. OUTPUT: master_sample_manifest.parquet with file_name, gvkey, ceo_id, ceo_name, prev_ceo_id, prev_ceo_name, start_date, ff48_code, ff48_name

## Key Merge Characteristics
- Join key: (gvkey, year, month) where gvkey is zero-padded to 6 digits
- Left join: metadata -> tenure (calls matched to CEO-month observations)
- Match rate: Percentage of calls that successfully link to CEO tenure information
- Filtering: CEOs below minimum call threshold (default 5) are removed

## Existing Pattern from Quick Tasks 019, 020, 021
Quick Task 019 added general-purpose stats (compute_input_stats, compute_temporal_stats, compute_entity_stats).
Quick Task 020 added entity-linking-specific stats with sample collection.
Quick Task 021 added tenure-mapping-specific stats with sample episodes/transitions.

For manifest assembly, we need specialized statistics that capture:
- Linked metadata characteristics (industry coverage, temporal range, call distribution)
- Tenure panel characteristics (firm-months, unique firms/CEOs, date coverage)
- Merge outcomes (join success by year, unmatched analysis)
- CEO filtering impact (CEOs dropped, calls retained, distribution changes)
- Final manifest characteristics (call concentration, industry coverage, temporal coverage)
- Sample CEO distribution (top/bottom CEOs by call count)

## Input Data Schemas (from 1.2 and 1.3 outputs)
metadata_linked.parquet columns: file_name, gvkey, start_date, ff12_code, ff12_name, ff48_code, ff48_name
tenure_monthly.parquet columns: gvkey, year, month, date, ceo_id, ceo_name, prev_ceo_id, prev_ceo_name
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add manifest assembly statistics functions to observability_utils.py</name>
  <files>2_Scripts/shared/observability_utils.py</files>
  <action>
Add four new manifest-assembly-specific functions to observability_utils.py:

1. **compute_manifest_input_stats(df_metadata, df_tenure)**: Analyze input data characteristics
   - Linked metadata: total_calls, unique_gvkey, columns, memory_mb
   - Tenure panel: total_firm_months, unique_firms, unique_ceos, date_range (earliest, latest, span_years)
   - Industry coverage from metadata: ff12_count (unique industries), ff48_count (unique industries)
   - Temporal coverage from metadata: year_range (earliest, latest), call_count_per_year
   - Returns dict with linked_metadata, tenure_panel, industry_coverage, temporal_coverage

2. **compute_manifest_process_stats(df_metadata, merged_df, df_matched, stats_dict)**: Analyze merge and filtering process
   - Merge outcome: left_rows (metadata), right_rows (tenure), result_rows, matched_count, unmatched_count, match_rate_pct
   - Match rate by year: [{year, total_calls, matched_calls, match_rate_pct}]
   - Unmatched analysis: unique_gvkey_unmatched, calls_unmatched, temporal_distribution_of_unmatched
   - CEO filtering: total_ceos_before_filter, ceos_above_threshold, ceos_dropped, threshold_value, calls_dropped
   - Returns dict with merge_outcome, match_rate_by_year, unmatched_analysis, ceo_filtering

3. **compute_manifest_output_stats(df_final)**: Analyze final manifest characteristics
   - Panel dimensions: total_calls, unique_gvkey, unique_ceos, date_range
   - Call concentration: calls_per_ceo (mean, median, min, max, std), call_distribution_buckets (<10, 10-50, 50-100, 100+)
   - Industry coverage (ff12): [{ff12_code, ff12_name, call_count, percentage}], top_5_industries
   - Industry coverage (ff48): unique_industries, completion_pct
   - Temporal coverage: [{year, call_count, unique_firms, unique_ceos}]
   - Predecessor coverage: pct_with_prev_ceo, pct_without_prev_ceo
   - Returns dict with panel_dimensions, call_concentration, industry_coverage_ff12, industry_coverage_ff48, temporal_coverage, predecessor_coverage

4. **collect_ceo_distribution_samples(df_final, n_samples=5)**: Collect CEO distribution examples
   Returns dict with:
   - top_ceos: List of top N CEOs by call count [{ceo_id, ceo_name, call_count, unique_firms, percentage}]
   - bottom_ceos: List of bottom N CEOs by call count (above threshold) [{ceo_id, ceo_name, call_count, unique_firms, percentage}]
   - single_call_ceos: Count and percentage of CEOs with only 1 call (if threshold allows)
   - multi_firm_ceos: Sample of CEOs spanning multiple firms [{ceo_id, ceo_name, call_count, firm_count}]

Requirements:
- All functions must be deterministic (sort outputs, no random operations)
- Handle missing columns gracefully (return error/warning in stats)
- Return JSON-serializable types (ISO strings for dates, not Timestamps)
- Include docstrings following existing module style
- For samples, use n_samples parameter with default of 5
- All percentages rounded to 2 decimal places
</action>
  <verify>
Run: python -c "from shared.observability_utils import compute_manifest_input_stats, compute_manifest_process_stats, compute_manifest_output_stats, collect_ceo_distribution_samples; print('Functions imported successfully')"
</verify>
  <done>
Four new manifest assembly statistics functions added to observability_utils.py, all importable and documented
</done>
</task>

<task type="auto">
  <name>Task 2: Integrate manifest assembly statistics into 1.4_AssembleManifest.py and enhance report</name>
  <files>2_Scripts/1_Sample/1.4_AssembleManifest.py</files>
  <action>
Integrate the new statistics functions into 1.4_AssembleManifest.py:

**After loading metadata and tenure (after line 242):**
- Call compute_manifest_input_stats(metadata, tenure)
- Store in stats["manifest_input"] = {...}

**After merge and before filtering (after line 289, using merged and df_matched):**
- Call compute_manifest_process_stats(metadata, merged, df_matched, stats)
- Store in stats["manifest_process"] = {...}

**After CEO filtering and final df_final created (after line 323):**
- Call compute_manifest_output_stats(df_final)
- Store in stats["manifest_output"] = {...}
- Call collect_ceo_distribution_samples(df_final, n_samples=5)
- Store in stats["ceo_samples"] = {...}

**Create enhanced report generation function (new section around line 367):**
Replace the existing report_lines list with a comprehensive report structure using a helper function:

Add function generate_manifest_report(stats, output_dir, print_dual) that creates report_step_1_4.md with:

## INPUT DATA SOURCES
### Linked Metadata (from step 1.2)
- Total calls, unique firms (gvkey), columns, memory footprint
- Industry coverage: FF12 unique industries, FF48 unique industries
- Temporal range: earliest call, latest call, span years

### CEO Tenure Panel (from step 1.3)
- Total firm-months, unique firms, unique CEOs
- Date coverage: earliest, latest, span years

## MERGE PROCESS
### Join Outcome
- Left rows (metadata), Right rows (tenure), Matched calls, Unmatched calls, Match rate %
- Note: Join on (gvkey, year, month) with 6-digit zero-padded gvkey

### Match Rate by Year
Table: Year | Total Calls | Matched Calls | Match Rate %

### Unmatched Analysis
- Unique firms (gvkey) without CEO tenure data
- Calls unmatched, percentage of total
- Temporal distribution of unmatched calls (by year)

### CEO Filtering
- Minimum call threshold value
- CEOs before filter, CEOs above threshold, CEOs dropped
- Calls dropped due to threshold

## OUTPUT: FINAL MANIFEST
### Panel Dimensions
- Total calls, unique firms, unique CEOs, date range

### Call Concentration
- Mean/median/min/max calls per CEO
- Call distribution buckets: <10, 10-50, 50-100, 100+ calls (with counts and percentages)

### Industry Coverage (FF12)
Table: FF12 Code | Industry Name | Call Count | Percentage
Top 10 industries by call count

### Industry Coverage (FF48)
- Unique industries, completion percentage

### Temporal Coverage
Table: Year | Call Count | Unique Firms | Unique CEOs

### Predecessor Coverage
- Calls with predecessor CEO (%), calls without predecessor (%)

## CEO DISTRIBUTION SAMPLES
### Top CEOs by Call Count
Table: CEO ID | CEO Name | Call Count | Unique Firms | Percentage

### Bottom CEOs by Call Count (above threshold)
Table: CEO ID | CEO Name | Call Count | Unique Firms | Percentage

### Multi-Firm CEOs
Sample of CEOs appearing at multiple firms

**Call generate_manifest_report after variable reference generation (around line 365):**
- Insert report generation call
- Use existing DualWriter (print_dual) for console output as well

Requirements:
- Maintain existing functionality (no breaking changes)
- Use existing DualWriter for print output
- Format tables in markdown for readability
- Round percentages to 1-2 decimal places
- Match visual style from 1.1, 1.2, 1.3 reports
- Handle missing sample data gracefully (show "No samples available" if empty)
- Ensure stats.json save includes all new statistics sections
</action>
  <verify>
1. Run: python 2_Scripts/1_Sample/1.4_AssembleManifest.py
2. Check stats.json contains new keys: manifest_input, manifest_process, manifest_output, ceo_samples
3. Check report_step_1_4.md has new sections with properly formatted tables
4. Verify match rate calculations are correct (matched / total * 100)
5. Verify CEO filtering statistics match console output
</verify>
  <done>
Script runs successfully, stats.json contains all new manifest assembly statistics, report_step_1_4.md contains publication-ready INPUT, PROCESS, OUTPUT sections with CEO distribution samples
</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete manifest assembly statistics suite for step 1.4, including new functions in observability_utils.py and enhanced reporting in 1.4_AssembleManifest.py with CEO distribution samples</what-built>
  <how-to-verify>
1. Run: python 2_Scripts/1_Sample/1.4_AssembleManifest.py
2. Open the generated report: 4_Outputs/1.4_AssembleManifest/latest/report_step_1_4.md
3. Verify report contains:
   - INPUT DATA section with linked metadata and tenure panel characteristics
   - MERGE PROCESS section with join outcome, match rate by year table, unmatched analysis, CEO filtering stats
   - OUTPUT section with panel dimensions, call concentration, industry coverage tables, temporal coverage, predecessor coverage
   - CEO DISTRIBUTION SAMPLES section with top/bottom CEOs and multi-firm CEOs
4. Open stats.json and verify new keys: manifest_input, manifest_process, manifest_output, ceo_samples
5. Verify match rate calculations are accurate (matched_calls / total_metadata_calls * 100)
6. Assess if statistics accurately represent the manifest assembly process and are suitable for academic presentation
7. Confirm the manifest defines the "Universe of Analysis" clearly
</how-to-verify>
  <resume-signal>Type "approved" if the statistics meet presentation needs, or describe any additional metrics needed</resume-signal>
</task>

</tasks>

<verification>
After implementation:
1. Script executes without errors
2. stats.json contains new manifest assembly statistics keys
3. report_step_1_4.md has publication-ready tables and metrics
4. Match rate calculations are mathematically correct
5. CEO filtering statistics accurately reflect threshold impact
6. CEO distribution samples provide meaningful insights
7. Report format is suitable for academic supervisor presentation
</verification>

<success_criteria>
- Four new manifest assembly statistics functions in observability_utils.py
- Integration in 1.4_AssembleManifest.py adds comprehensive manifest stats collection
- report_step_1_4.md contains INPUT (metadata+tenure), PROCESS (merge+filtering), OUTPUT (manifest characteristics), CEO SAMPLES sections
- All statistics are presentation-ready for academic supervisors
- CEO distribution samples illustrate sample concentration characteristics
</success_criteria>

<output>
After completion, create `.planning/quick/022-add-comprehensive-descriptive-stats-to-1/022-SUMMARY.md`
</output>
