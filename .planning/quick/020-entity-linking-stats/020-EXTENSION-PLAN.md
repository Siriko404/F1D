---
phase: quick-020
plan: entity-linking-stats-extension
type: execute
wave: 2
depends_on: ["020"]
files_modified:
  - 2_Scripts/shared/observability_utils.py
  - 2_Scripts/1_Sample/1.2_LinkEntities.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - Samples of fuzzy name matches show query-to-match alignment with scores
    - Samples of Tier 1 (PERMNO) and Tier 2 (CUSIP8) matches demonstrate high-quality linkages
    - Edge case samples explain why certain companies could not be matched
    - Report displays sample tables for supervisor review
  artifacts:
    - path: "2_Scripts/shared/observability_utils.py"
      provides: "Entity linking sample collection functions"
      exports: ["collect_fuzzy_match_samples", "collect_tier_match_samples", "collect_unmatched_samples"]
    - path: "2_Scripts/1_Sample/1.2_LinkEntities.py"
      provides: "Sample collection integration and report generation"
      contains: "samples section in report"
  key_links:
    - from: "2_Scripts/1_Sample/1.2_LinkEntities.py"
      to: "2_Scripts/shared/observability_utils.py"
      via: "from shared.observability_utils import"
      pattern: "collect_.*_samples"
---

<objective>
Add sample record collection to the entity linking statistics suite, providing supervisors with concrete examples of fuzzy matches, tier matches, and edge cases to assess matching quality.

Purpose: Supervisors need to see actual examples of how the 4-tier matching strategy performs, including good matches, borderline cases, and companies that could not be matched. Samples provide transparency and build confidence in the linkage methodology.

Output: Extended stats.json with sample records and enhanced report_step_1_2.md with sample tables.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/1_Sample/1.2_LinkEntities.py
@2_Scripts/shared/observability_utils.py
@.planning/quick/020-entity-linking-stats/020-PLAN.md

## Current State (from Quick Task 020)
Quick Task 020 added three entity linking statistics functions:
- compute_linking_input_stats: Input and reference data characteristics
- compute_linking_process_stats: 4-tier matching funnel and quality distribution
- compute_linking_output_stats: Linkage success and industry coverage

## What We're Adding
Sample collection functions to capture actual matching examples:

1. **Fuzzy Match Samples** - Show Tier 3 fuzzy name matches:
   - Query name (from earnings calls)
   - Matched name (from CCM)
   - Fuzzy score
   - GVKEY assigned
   - Include both high-score (>98) and borderline (92-95) cases

2. **Tier 1/2 Samples** - High-quality match examples:
   - PERMNO match example with company details
   - CUSIP8 match example with company details

3. **Unmatched Samples** - Companies that couldn't be matched:
   - Company name
   - Available identifiers (PERMNO, CUSIP, ticker)
   - Potential reason for no match

4. **Before/After Examples** - Show linking transformation:
   - Original company fields
   - Linked CCM fields (gvkey, conm, sic, ff12_name)

## Sample Format (JSON)
```json
{
  "samples": {
    "fuzzy_matches": [
      {
        "query_name": "APPLE INC",
        "matched_name": "APPLE CORP",
        "score": 95.2,
        "gvkey": "001234",
        "tier": 3
      }
    ],
    "tier1_examples": [
      {
        "company_id": "12345",
        "permno": "12345",
        "gvkey": "001234",
        "conm": "EXXON MOBIL CORP"
      }
    ],
    "unmatched_samples": [
      {
        "company_name": "Unknown Company",
        "has_permno": false,
        "has_cusip": false,
        "has_ticker": false
      }
    ]
  }
}
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add sample collection functions to observability_utils.py</name>
  <files>2_Scripts/shared/observability_utils.py</files>
  <action>
Add four new sample collection functions to observability_utils.py:

1. **collect_fuzzy_match_samples(unique_df, n_samples=5)**: Collect fuzzy name match examples
   - Filter unique_df where link_method == "name_fuzzy"
   - Sort by link_quality descending (best matches first) - OR if fuzzy_score column exists during Tier 3
   - Select top n_samples high-score matches (>98) and borderline matches (92-95)
   - For each sample, extract: company_id, company_name (query), conm (matched), fuzzy_score if available, gvkey, sic
   - Returns: {high_score: [...], borderline: [...]}

2. **collect_tier_match_samples(unique_df, n_samples=3)**: Collect Tier 1 and Tier 2 examples
   - Tier 1: Filter link_method == "permno_date", select n_samples random examples
   - Tier 2: Filter link_method == "cusip8_date", select n_samples random examples
   - Extract: company_id, permno/cusip8, gvkey, conm, sic, link_quality
   - Returns: {tier1: [...], tier2: [...]}

3. **collect_unmatched_samples(df_original, unique_df, n_samples=5)**: Collect unmatched companies
   - Find companies where unique_df.gvkey is NaN
   - For each, extract: company_id, company_name, has_permno, has_cusip, has_ticker
   - Classify reason: "missing_identifiers", "no_ccm_match", or "unknown"
   - Returns: list of unmatched samples

4. **collect_before_after_samples(df_original, df_linked, n_samples=3)**: Show linking transformation
   - Select n_samples companies that were successfully linked
   - Extract from original: company_id, company_name, company_ticker, permno, cusip
   - Extract from linked: gvkey, conm, sic, ff12_name, ff48_name, link_method, link_quality
   - Returns: list of before/after examples

Requirements:
- All functions must be deterministic (set random seed if sampling)
- Handle empty results gracefully (return empty lists)
- Return JSON-serializable types (no NaN, use None)
- Include docstrings following existing module style
- Default n_samples should be small (3-5) to keep stats.json manageable
</action>
  <verify>
Run: python -c "from shared.observability_utils import collect_fuzzy_match_samples, collect_tier_match_samples, collect_unmatched_samples, collect_before_after_samples; print('Sample collection functions imported successfully')"
</verify>
  <done>
Four new sample collection functions added to observability_utils.py, all importable and documented
</done>
</task>

<task type="auto">
  <name>Task 2: Integrate sample collection into 1.2_LinkEntities.py and update report</name>
  <files>2_Scripts/1_Sample/1.2_LinkEntities.py</files>
  <action>
Integrate sample collection into 1.2_LinkEntities.py:

**After Tier 3 matching completes (after line 683, after compute_linking_process_stats):**
- Store the matched_records list from Tier 3 for fuzzy sample collection
- OR collect samples from unique_df after all tiers complete
- Call collect_fuzzy_match_samples(unique_df, n_samples=5)
- Call collect_tier_match_samples(unique_df, n_samples=3)
- Store in stats["linking_process"]["samples"] = {...}

**After broadcasting results (after line 725):**
- Call collect_unmatched_samples(df_original=df, unique_df=unique_df, n_samples=5)
- Store in stats["linking_process"]["samples"]["unmatched"] = [...]

**After filtering and linking (after line 774, after compute_linking_output_stats):**
- Call collect_before_after_samples(df_original=df, df_linked=df_linked, n_samples=3)
- Store in stats["linking_output"]["samples"]["before_after"] = [...]

**Update report_step_1_2.md generation (after line 890, before OUTPUT SUMMARY):**
Add new section "## MATCHING SAMPLES" with subsections:

### Fuzzy Name Match Examples
Table showing query name, matched name, score, GVKEY:
| Query Name | Matched Name | Score | GVKEY | SIC |
|------------|--------------|-------|-------|-----|
| APPLE INC | APPLE CORP | 95.2 | 001234 | 3571 |

Include both high-score and borderline examples.

### Tier 1 (PERMNO) Match Examples
| Company | PERMNO | GVKEY | Matched Name | SIC |
|---------|--------|-------|--------------|-----|

### Tier 2 (CUSIP8) Match Examples
| Company | CUSIP8 | GVKEY | Matched Name | SIC |
|---------|--------|-------|--------------|-----|

### Unmatched Companies (Sample)
| Company Name | Has PERMNO | Has CUSIP | Has Ticker | Likely Reason |
|--------------|------------|-----------|------------|---------------|

### Before/After Examples
Show the transformation from original to linked fields.

**Update imports (around line 77-91):**
Add import for new sample collection functions.

Requirements:
- Maintain existing functionality (no breaking changes)
- Format tables in markdown for readability
- Handle empty sample lists gracefully (show "No samples available")
- Round scores to 1 decimal place
- Use consistent table styling with rest of report
</action>
  <verify>
1. Run: python 2_Scripts/1_Sample/1.2_LinkEntities.py
2. Check stats.json contains new keys: linking_process.samples, linking_output.samples
3. Check report_step_1_2.md has new MATCHING SAMPLES section with sample tables
4. Verify samples are readable and informative
</verify>
  <done>
Script runs successfully, stats.json contains sample records, report_step_1_2.md contains MATCHING SAMPLES section with fuzzy match examples, tier examples, unmatched samples, and before/after examples
</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete sample collection extension for entity linking statistics, including new sample collection functions and enhanced reporting with sample tables</what-built>
  <how-to-verify>
1. Run: python 2_Scripts/1_Sample/1.2_LinkEntities.py
2. Open the generated report: 4_Outputs/1.2_LinkEntities/latest/report_step_1_2.md
3. Verify report contains MATCHING SAMPLES section with:
   - Fuzzy Name Match Examples table (showing query/match alignment)
   - Tier 1 (PERMNO) Match Examples
   - Tier 2 (CUSIP8) Match Examples
   - Unmatched Companies table
   - Before/After Examples
4. Open stats.json and verify new samples keys exist with actual data
5. Assess if samples demonstrate matching quality effectively for supervisor presentation
</how-to-verify>
  <resume-signal>Type "approved" if the samples meet presentation needs, or describe adjustments needed</resume-signal>
</task>

</tasks>

<verification>
After implementation:
1. Script executes without errors
2. stats.json contains samples under linking_process and linking_output
3. report_step_1_2.md has MATCHING SAMPLES section with all tables
4. Samples are readable and informative
5. Tables are properly formatted in markdown
</verification>

<success_criteria>
- Four new sample collection functions in observability_utils.py
- Integration in 1.2_LinkEntities.py collects samples during execution
- report_step_1_2.md contains MATCHING SAMPLES section with tables
- Samples demonstrate matching quality for supervisor review
</success_criteria>

<output>
After completion, create `.planning/quick/020-entity-linking-stats/020-EXTENSION-SUMMARY.md`
</output>
