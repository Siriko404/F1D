---
phase: quick-020
plan: entity-linking-stats
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/shared/observability_utils.py
  - 2_Scripts/1_Sample/1.2_LinkEntities.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - Script generates INPUT statistics showing metadata_cleaned.parquet and CCM reference data characteristics
    - Script generates PROCESS statistics showing 4-tier matching outcomes (match rates at each tier)
    - Script generates OUTPUT statistics showing linked entities, quality metrics, industry coverage
    - All statistics saved to stats.json and included in report_step_1_2.md
  artifacts:
    - path: "2_Scripts/shared/observability_utils.py"
      provides: "Entity linking statistics functions"
      exports: ["compute_linking_input_stats", "compute_linking_process_stats", "compute_linking_output_stats"]
    - path: "2_Scripts/1_Sample/1.2_LinkEntities.py"
      provides: "Enhanced entity linking statistics integration"
      contains: "comprehensive linking statistics"
  key_links:
    - from: "2_Scripts/1_Sample/1.2_LinkEntities.py"
      to: "2_Scripts/shared/observability_utils.py"
      via: "from shared.observability_utils import"
      pattern: "compute_linking_(input|process|output)_stats"
---

<objective>
Add comprehensive descriptive statistics to script 1.2_LinkEntities.py that provide publication-quality insights for the entity linking process, covering INPUT (source and reference data), PROCESS (4-tier matching strategy), and OUTPUT (linked entities with quality metrics).

Purpose: Data scientists need professional, publication-ready descriptive statistics for the entity resolution step to present to academic supervisors. This step links company names to CRSP/Compustat CCM database using a sophisticated 4-tier matching strategy (PERMNO+date, CUSIP8+date, fuzzy name, ticker). Understanding match rates at each tier and final linkage quality is critical for methodological transparency.

Output: Extended stats.json and enhanced report_step_1_2.md with comprehensive descriptive statistics specific to entity linking.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/1_Sample/1.2_LinkEntities.py
@2_Scripts/shared/observability_utils.py
@2_Scripts/1_Sample/1.1_CleanMetadata.py

## Current State
Script 1.2_LinkEntities.py currently collects:
- Basic input counts (calls, CCM records)
- Dedup-index compression ratio
- Tier 1, 2, 3 match counts (PERMNO, CUSIP8, fuzzy name)
- Total matched companies and calls
- FF12/FF48 industry mapping counts
- Standard stats (timing, memory, throughput, missing values, anomalies)

## Entity Linking Data Flow
1. INPUT: metadata_cleaned.parquet (from step 1.1) + CRSPCompustat_CCM.parquet (reference)
2. PROCESS: Dedup-index (unique companies) -> 4-tier matching -> broadcast results
3. OUTPUT: metadata_linked.parquet with gvkey, conm, sic, link_method, link_quality, ff12_code, ff48_name

## 4-Tier Matching Strategy
- Tier 1: PERMNO + Date Range (link_quality=100)
- Tier 2: CUSIP8 + Date Range (link_quality=90)
- Tier 3: Fuzzy Name Match (link_quality=80, threshold=92)
- Tier 4: Ticker (mentioned in comments, currently not implemented)

## Existing Pattern from Quick Task 019
Quick Task 019 added compute_input_stats, compute_temporal_stats, compute_entity_stats to observability_utils.py. These functions are general-purpose. For entity linking, we need specialized statistics that capture:
- Reference data characteristics (CCM database size, date coverage)
- Matching funnel (candidates at each tier, attrition)
- Linkage quality distribution by method
- Industry assignment completeness
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add entity linking statistics functions to observability_utils.py</name>
  <files>2_Scripts/shared/observability_utils.py</files>
  <action>
Add three new entity-linking-specific functions to observability_utils.py:

1. **compute_linking_input_stats(df_input, df_ccm)**: Analyze input and reference data
   - Input metadata: record count, unique companies, columns, memory_mb
   - CCM reference: total records, unique gvkey, unique LPERMNO, date range (LINKDT to LINKENDDT)
   - Coverage analysis: what percentage of input companies have PERMNO, CUSIP, ticker, name
   - Returns dict with input_metadata, reference_database, coverage_metrics

2. **compute_linking_process_stats(unique_df, stats_dict)**: Analyze 4-tier matching process
   - Funnel analysis: candidates at each tier, matches at each tier, cumulative matches
   - Match rate calculations: tier-specific and cumulative percentages
   - Attrition tracking: records lost between tiers
   - Link quality distribution: count by link_quality value (100, 90, 80)
   - Link method distribution: count by method (permno_date, cusip8_date, name_fuzzy)
   - Returns dict with funnel_analysis, match_rates, link_quality_distribution, link_method_distribution

3. **compute_linking_output_stats(df_linked)**: Analyze linked entities output
   - Overall linkage: unique gvkey, unique companies linked, linkage success rate
   - Industry coverage: FF12 assignments (count, unique industries, completion %), FF48 assignments
   - SIC code distribution: unique SICs, top industries
   - Temporal coverage of linked entities (date range)
   - Quality metrics: avg link_quality, distribution by method
   - Returns dict with linkage_summary, industry_coverage, sic_distribution, quality_metrics

Requirements:
- All functions must be deterministic (sort outputs)
- Handle missing columns gracefully
- Return JSON-serializable types (ISO strings, not Timestamps)
- Include docstrings following existing module style
- Accept stats_dict parameter for process_stats to access tier counts from main execution
</action>
  <verify>
Run: python -c "from shared.observability_utils import compute_linking_input_stats, compute_linking_process_stats, compute_linking_output_stats; print('Functions imported successfully')"
</verify>
  <done>
Three new entity linking statistics functions added to observability_utils.py, all importable and documented
</done>
</task>

<task type="auto">
  <name>Task 2: Integrate entity linking statistics into 1.2_LinkEntities.py and enhance report</name>
  <files>2_Scripts/1_Sample/1.2_LinkEntities.py</files>
  <action>
Integrate the new statistics functions into 1.2_LinkEntities.py:

**After loading df and ccm (after line 376):**
- Call compute_linking_input_stats(df, ccm)
- Store in stats["linking_input"] = {...}

**After tier matching completes (after line 673, before broadcast):**
- Call compute_linking_process_stats(unique_df, stats)
- Store in stats["linking_process"] = {...}
- Note: unique_df contains the tier match results, stats["linking"] has tier counts

**After FF industry mapping and filtering (after line 762):**
- Call compute_linking_output_stats(df_linked)
- Store in stats["linking_output"] = {...}

**Update report_step_1_2.md generation (locate and modify existing report generation):**
Enhance the report with publication-ready sections:

## INPUT DATA
### Source Metadata (from step 1.1)
- Total calls, unique companies, memory footprint
- Column count

### Reference Database (CCM)
- Total CCM records, unique GVKEYs, unique LPERMNOs
- Date coverage range

### Identifier Coverage
- Percentage with PERMNO, CUSIP, ticker, company_name

## MATCHING PROCESS
### 4-Tier Matching Funnel
| Tier | Method | Candidates | Matched | Cumulative | Match Rate |
|------|--------|------------|---------|------------|------------|
| 1 | PERMNO+Date | X | X | X | XX% |
| 2 | CUSIP8+Date | X | X | X | XX% |
| 3 | Fuzzy Name | X | X | X | XX% |

### Link Quality Distribution
- Quality 100 (PERMNO): X companies (XX%)
- Quality 90 (CUSIP8): X companies (XX%)
- Quality 80 (Fuzzy): X companies (XX%)

### Dedup-Index Optimization
- Compression ratio: X:1 (Y calls -> Z unique companies)

## OUTPUT SUMMARY
### Linkage Success
- Total calls linked: X (XX% of input)
- Unique companies linked: Y
- Unique GVKEYs assigned: Z

### Industry Coverage
- FF12: X assigned (XX%), Y unique industries
- FF48: X assigned (XX%), Y unique industries

### SIC Distribution
- Unique SIC codes: X
- Top 5 SIC industries (table)

**Update stats.json save:**
- Ensure save_stats() call includes all new stats sections
- All new stats should be in stats dictionary before save_stats() is called

Requirements:
- Maintain existing functionality (no breaking changes)
- Use existing DualWriter for print output
- Format tables in markdown for readability
- Round percentages to 1-2 decimal places
- Match the visual style established in 1.1 report
</action>
  <verify>
1. Run: python 2_Scripts/1_Sample/1.2_LinkEntities.py
2. Check stats.json contains new keys: linking_input, linking_process, linking_output
3. Check report_step_1_2.md has new sections with properly formatted tables
4. Verify match rate calculations are correct
</verify>
  <done>
Script runs successfully, stats.json contains all new entity linking statistics, report_step_1_2.md contains publication-ready INPUT, PROCESS, OUTPUT sections for entity linking
</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete entity linking statistics suite for step 1.2, including new functions in observability_utils.py and enhanced reporting in 1.2_LinkEntities.py</what-built>
  <how-to-verify>
1. Run: python 2_Scripts/1_Sample/1.2_LinkEntities.py
2. Open the generated report: 4_Outputs/1.2_LinkEntities/latest/report_step_1_2.md
3. Verify report contains:
   - INPUT DATA section with source metadata, reference database, identifier coverage
   - MATCHING PROCESS section with 4-tier funnel table, quality distribution, dedup-index stats
   - OUTPUT SUMMARY section with linkage success, industry coverage, SIC distribution
4. Open stats.json and verify new keys: linking_input, linking_process, linking_output
5. Assess if statistics accurately represent the entity linking process and are suitable for academic presentation
</how-to-verify>
  <resume-signal>Type "approved" if the statistics meet presentation needs, or describe any additional metrics needed</resume-signal>
</task>

</tasks>

<verification>
After implementation:
1. Script executes without errors
2. stats.json contains new entity linking statistics keys
3. report_step_1_2.md has publication-ready tables and metrics
4. Match rate calculations are mathematically correct
5. Report format is suitable for academic supervisor presentation
</verification>

<success_criteria>
- Three new entity linking statistics functions in observability_utils.py
- Integration in 1.2_LinkEntities.py adds comprehensive linking stats collection
- report_step_1_2.md contains INPUT (source+reference), PROCESS (4-tier funnel), OUTPUT (linkage+industry) sections
- All statistics are presentation-ready for academic supervisors
</success_criteria>

<output>
After completion, create `.planning/quick/020-entity-linking-stats/020-SUMMARY.md`
</output>
