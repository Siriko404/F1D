---
phase: quick-021
plan: tenure-mapping-stats
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/shared/observability_utils.py
  - 2_Scripts/1_Sample/1.3_BuildTenureMap.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - Script generates INPUT statistics showing Execucomp data characteristics (records, firms, CEOs, date coverage)
    - Script generates PROCESS statistics showing episode building, predecessor linking, overlap resolution
    - Script generates OUTPUT statistics showing monthly panel (date range, firm/CEO coverage, tenure distribution, transition patterns)
    - Script generates SAMPLE examples (tenure episodes, transitions, overlaps) for qualitative review
    - All statistics saved to stats.json and included in report_step_1_3.md
  artifacts:
    - path: "2_Scripts/shared/observability_utils.py"
      provides: "Tenure mapping statistics functions"
      exports: ["compute_tenure_input_stats", "compute_tenure_process_stats", "compute_tenure_output_stats", "collect_tenure_samples"]
    - path: "2_Scripts/1_Sample/1.3_BuildTenureMap.py"
      provides: "Enhanced tenure mapping statistics integration"
      contains: "comprehensive tenure statistics"
  key_links:
    - from: "2_Scripts/1_Sample/1.3_BuildTenureMap.py"
      to: "2_Scripts/shared/observability_utils.py"
      via: "from shared.observability_utils import"
      pattern: "compute_tenure_(input|process|output)_stats|collect_tenure_samples"
---

<objective>
Add comprehensive descriptive statistics to script 1.3_BuildTenureMap.py that provide publication-quality insights for the CEO tenure mapping process, covering INPUT (Execucomp CEO data), PROCESS (episode building, predecessor linking, overlap resolution), and OUTPUT (monthly panel with transitions).

Purpose: Data scientists need professional, publication-ready descriptive statistics for the tenure mapping step to present to academic supervisors. This step constructs the monthly CEO tenure panel by aggregating Execucomp records into episodes, linking predecessors, expanding to monthly observations, and resolving overlaps. Understanding the completeness of tenure tracking, transition patterns, and data quality is critical for methodological transparency.

Output: Extended stats.json and enhanced report_step_1_3.md with comprehensive descriptive statistics specific to tenure mapping, including sample episodes and transitions for qualitative review.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/1_Sample/1.3_BuildTenureMap.py
@2_Scripts/shared/observability_utils.py

## Current State
Script 1.3_BuildTenureMap.py currently collects:
- Basic input counts (total records, CEO records, unique firms, unique executives)
- Processing stats (non-CEO filtered, episodes created, predecessors linked, overlap duplicates removed)
- Standard stats (timing, memory, throughput, missing values, anomalies)

## Tenure Mapping Data Flow
1. INPUT: comp_execucomp.parquet (CEO/executive records with becameceo, leftofc dates)
2. PROCESS: Filter CEO records -> Build episodes per (gvkey, execid) -> Link predecessors -> Expand to monthly -> Resolve overlaps
3. OUTPUT: tenure_monthly.parquet with gvkey, year, month, date, ceo_id, ceo_name, prev_ceo_id, prev_ceo_name

## Key Tenure Mapping Concepts
- Tenure episode: Continuous period where an executive is CEO of a firm (from becameceo to leftofc)
- Predecessor linking: Each CEO episode linked to previous CEO of same firm
- Monthly expansion: Episodes expanded to monthly observations for panel analysis
- Overlap resolution: If two CEOs overlap for same firm-month, keep the later one (new CEO takes precedence)
- Active CEOs: CEOs without leftofc date get imputed end date (2025-12-31 if in latest year)

## Existing Pattern from Quick Tasks 019 and 020
Quick Task 019 added general-purpose descriptive stats (compute_input_stats, compute_temporal_stats, compute_entity_stats).
Quick Task 020 added entity-linking-specific stats (compute_linking_input_stats, compute_linking_process_stats, compute_linking_output_stats) and sample collection functions (collect_fuzzy_match_samples, collect_tier_match_samples, collect_unmatched_samples, collect_before_after_samples).

For tenure mapping, we need specialized statistics that capture:
- Execucomp CEO data characteristics (record types, date completeness, becameceo/leftofc coverage)
- Episode construction outcomes (tenure length distribution, episodes per firm, episodes per CEO)
- Predecessor linking success (link rate, orphan episodes, first-episode flags)
- Monthly panel characteristics (unique firm-months, CEO turnover rate, transition patterns)
- Sample episodes (short vs long tenures, transitions, overlaps)

## Sample Fields Required (like Quick Task 020)
- Sample tenure episodes: Short tenures (<1 year), medium tenures (3-5 years), long tenures (10+ years)
- Sample CEO transitions: Predecessor -> successor pairs with gap/overlap analysis
- Sample overlap resolutions: Cases where two CEOs overlapped and how resolved
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add tenure mapping statistics functions to observability_utils.py</name>
  <files>2_Scripts/shared/observability_utils.py</files>
  <action>
Add four new tenure-mapping-specific functions to observability_utils.py:

1. **compute_tenure_input_stats(df_input, df_ceo)**: Analyze Execucomp input data
   - Overall Execucomp: total records, unique gvkey, unique execid, date range (year column)
   - CEO subset: CEO record count, percentage of total, unique CEO firms, unique CEO executives
   - Date field coverage: becameceo availability (% non-null), leftofc availability (% non-null)
   - CEO indicator coverage: ceoann='CEO' count, becameceo non-null count
   - Executive name availability: exec_fullname coverage percentage
   - Returns dict with overall_execucomp, ceo_subset, date_field_coverage, ceo_indicators, name_coverage

2. **compute_tenure_process_stats(episodes_df)**: Analyze episode building and linking
   - Episode construction: total episodes, episodes per firm (mean, median, min, max), episodes per CEO (mean, median, min, max)
   - Tenure length distribution: mean_months, median_months, min_months, max_months, std_months
        - Tenure buckets: <1 year, 1-3 years, 3-5 years, 5-10 years, 10+ years (counts and percentages)
   - Predecessor linking: linked_count, orphan_count (no predecessor), link_rate_pct
   - Episode date validity: episodes with future dates, episodes with end < start, active_ceo_count (end_date imputed)
   - Returns dict with episode_counts, tenure_distribution, predecessor_linking, date_validity

3. **compute_tenure_output_stats(monthly_df)**: Analyze monthly panel output
   - Panel dimensions: total_firm_months, unique_firms, unique_ceos, date_range (earliest, latest, span_years)
   - Temporal coverage: firm_months per year, firms per year, ceos per year
   - CEO turnover: turnover_events (prev_ceo_id changes), turnover_rate (per 100 firm-years)
   - Predecessor coverage: firm_months with predecessor info (%), firm_months without predecessor (%)
   - Multi-CEO firms: firms with multiple CEOs, max CEOs per firm
   - CEO careers: CEOs spanning multiple firms, CEOs with multiple episodes at same firm
   - Returns dict with panel_dimensions, temporal_coverage, turnover_metrics, predecessor_coverage, multi_ceo_analysis

4. **collect_tenure_samples(episodes_df, monthly_df, n_samples=3)**: Collect qualitative examples
   Returns dict with:
   - short_tenures: List of short tenure examples (<12 months) with gvkey, ceo_name, start_date, end_date, tenure_months
   - long_tenures: List of long tenure examples (>120 months) with gvkey, ceo_name, start_date, end_date, tenure_months
   - transitions: List of CEO transitions with gvkey, prev_ceo_name, new_ceo_name, transition_date, gap_days (negative if overlap)
   - overlaps: List of overlap resolution examples with gvkey, resolved_ceo, overlapped_ceo, overlap_period, resolution_reason

Requirements:
- All functions must be deterministic (sort outputs, use random_state for sampling)
- Handle missing columns gracefully (return error/warning in stats)
- Return JSON-serializable types (ISO strings for dates, not Timestamps)
- Include docstrings following existing module style
- For samples, use n_samples parameter with default of 3
</action>
  <verify>
Run: python -c "from shared.observability_utils import compute_tenure_input_stats, compute_tenure_process_stats, compute_tenure_output_stats, collect_tenure_samples; print('Functions imported successfully')"
</verify>
  <done>
Four new tenure mapping statistics functions added to observability_utils.py, all importable and documented
</done>
</task>

<task type="auto">
  <name>Task 2: Integrate tenure mapping statistics into 1.3_BuildTenureMap.py and enhance report</name>
  <files>2_Scripts/1_Sample/1.3_BuildTenureMap.py</files>
  <action>
Integrate the new statistics functions into 1.3_BuildTenureMap.py:

**After loading df and creating ceo_records (after line 205):**
- Call compute_tenure_input_stats(df, ceo_records)
- Store in stats["tenure_input"] = {...}

**After building episodes_df (after line 251):**
- Call compute_tenure_process_stats(episodes_df)
- Store in stats["tenure_process"] = {...}

**After creating monthly_df and resolving overlaps (after line 346):**
- Call compute_tenure_output_stats(monthly_df)
- Store in stats["tenure_output"] = {...}
- Call collect_tenure_samples(episodes_df, monthly_df, n_samples=3)
- Store in stats["tenure_samples"] = {...}

**Create report generation function (new section before main() ends):**
Add a function generate_tenure_report(stats, output_dir) that creates report_step_1_3.md with:

## INPUT DATA: EXECUCOMP CEO RECORDS
### Overall Execucomp
- Total records, unique firms (gvkey), unique executives (execid), date range

### CEO Subset
- CEO records, percentage of total, unique CEO firms, unique CEO executives

### Date Field Coverage
- becameceo available (%), leftofc available (%)

### CEO Indicators
- Records with ceoann='CEO', records with becameceo non-null

## PROCESS: TENURE EPISODE CONSTRUCTION
### Episode Counts
- Total episodes, episodes per firm (mean, median, min, max), episodes per CEO

### Tenure Length Distribution
- Table: Tenure Bucket | Count | Percentage
- (<1 year, 1-3 years, 3-5 years, 5-10 years, 10+ years)
- Overall: mean, median, min, max months

### Predecessor Linking
- Episodes linked to predecessor (%), orphan episodes (no predecessor)

### Date Validity
- Active CEOs (end date imputed), episodes with valid dates

## OUTPUT: MONTHLY TENURE PANEL
### Panel Dimensions
- Total firm-months, unique firms, unique CEOs, date range

### Temporal Coverage
- Table: Year | Firm-Months | Unique Firms | Unique CEOs

### CEO Turnover
- Turnover events (transitions), turnover rate per 100 firm-years

### Predecessor Coverage
- Firm-months with predecessor info (%)

### Multi-CEO Firms
- Firms with multiple CEOs, maximum CEOs per firm

## SAMPLE EPISODES AND TRANSITIONS
### Short Tenure Examples (<1 year)
Table with sample columns

### Long Tenure Examples (10+ years)
Table with sample columns

### CEO Transition Examples
Table showing predecessor -> successor with gap/overlap analysis

**Call generate_tenure_report before saving stats (around line 430):**
- Insert report generation call
- Use DualWriter for console output as well

Requirements:
- Maintain existing functionality (no breaking changes)
- Use existing DualWriter for print output
- Format tables in markdown for readability
- Round percentages to 1-2 decimal places
- Match visual style from 1.1 and 1.2 reports
- Handle missing sample data gracefully (show "No samples available" if empty)
</action>
  <verify>
1. Run: python 2_Scripts/1_Sample/1.3_BuildTenureMap.py
2. Check stats.json contains new keys: tenure_input, tenure_process, tenure_output, tenure_samples
3. Check report_step_1_3.md has new sections with properly formatted tables and samples
4. Verify tenure length calculations are correct (months between dates)
5. Verify turnover rate calculation is meaningful
</verify>
  <done>
Script runs successfully, stats.json contains all new tenure mapping statistics, report_step_1_3.md contains publication-ready INPUT, PROCESS, OUTPUT sections with sample episodes and transitions
</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete tenure mapping statistics suite for step 1.3, including new functions in observability_utils.py and enhanced reporting in 1.3_BuildTenureMap.py with sample episodes and transitions</what-built>
  <how-to-verify>
1. Run: python 2_Scripts/1_Sample/1.3_BuildTenureMap.py
2. Open the generated report: 4_Outputs/1.3_BuildTenureMap/latest/report_step_1_3.md
3. Verify report contains:
   - INPUT DATA section with Execucomp characteristics, CEO subset, date field coverage
   - PROCESS section with episode counts, tenure length distribution table, predecessor linking stats
   - OUTPUT section with panel dimensions, temporal coverage table, CEO turnover metrics
   - SAMPLE EPISODES section with short/long tenure examples and CEO transitions
4. Open stats.json and verify new keys: tenure_input, tenure_process, tenure_output, tenure_samples
5. Review sample transitions for meaningful examples (gap vs overlap cases)
6. Assess if statistics accurately represent the tenure mapping process and are suitable for academic presentation
</how-to-verify>
  <resume-signal>Type "approved" if the statistics meet presentation needs, or describe any additional metrics needed</resume-signal>
</task>

</tasks>

<verification>
After implementation:
1. Script executes without errors
2. stats.json contains new tenure mapping statistics keys
3. report_step_1_3.md has publication-ready tables and metrics
4. Tenure length calculations are accurate (date differences in months)
5. Turnover rate is calculated correctly
6. Sample episodes and transitions provide meaningful qualitative insights
7. Report format is suitable for academic supervisor presentation
</verification>

<success_criteria>
- Four new tenure mapping statistics functions in observability_utils.py
- Integration in 1.3_BuildTenureMap.py adds comprehensive tenure stats collection
- report_step_1_3.md contains INPUT (Execucomp), PROCESS (episodes, linking), OUTPUT (monthly panel, turnover), SAMPLES sections
- All statistics are presentation-ready for academic supervisors
- Sample episodes and transitions provide qualitative insights for methodology discussions
</success_criteria>

<output>
After completion, create `.planning/quick/021-tenure-mapping-stats/021-SUMMARY.md`
</output>
