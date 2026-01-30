---
phase: quick-024
plan: debug-script-21
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/2_Text/2.1_TokenizeAndCount.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - Script runs successfully at full scale (17 years of data)
    - All 17 output files (linguistic_counts_2002-2018.parquet) are generated
    - Log file is properly written (not empty)
    - stats.json contains all expected statistics
    - report_step_2_1.md is generated with comprehensive statistics
    - No incomplete/corrupted output directories
  artifacts:
    - path: "4_Outputs/2_Textual_Analysis/2.1_Tokenized"
      provides: "17 yearly linguistic count parquet files"
      exports: ["linguistic_counts_2002.parquet", ..., "linguistic_counts_2018.parquet"]
    - path: "3_Logs/2.1_TokenizeAndCount"
      provides: "Execution log with full trace"
      exports: ["timestamp.log"]
  key_links:
    - from: "2.1_TokenizeAndCount.py"
      to: "shared/observability_utils.py"
      via: "from shared.observability_utils import"
      pattern: "compute_tokenize_(input|process|output)_stats"
---

<objective>
Debug and run script 2.1_TokenizeAndCount.py at full scale and verify the outputs thoroughly.

Purpose: Recent runs have shown incomplete outputs (only 4-9 year files instead of 17) and empty log files, indicating the script may be crashing or being interrupted. Need to identify the root cause and ensure reliable full-scale execution.

Output: Complete set of 17 yearly parquet files, complete log file, stats.json and report_step_2_1.md.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/2_Text/2.1_TokenizeAndCount.py
@.planning/quick/023-tokenize-descriptive-stats/023-SUMMARY.md

## Current State
Script 2.1_TokenizeAndCount.py has been running with partial success:
- **Last successful full run:** 2026-01-30 13:41:19 (execution_20260130_134119.log) - All 17 years processed
- **Recent runs:** 2026-01-30 14:03, 14:05, 14:07 - Only 4-9 years processed, empty log files
- **Config:** thread_count = 1 (sequential mode)

## Issues Identified
1. **Empty log files:** Recent runs have 0-byte log files, suggesting DualWriter may not be flushing properly or script is interrupted before flush
2. **Incomplete outputs:** Only 4-9 parquet files generated instead of 17
3. **Multiple output directories:** Several timestamped directories with partial outputs suggest repeated failures

## Potential Root Causes
1. **Memory issue:** Script may run out of memory during later years (9-17 have similar sizes to earlier years)
2. **Exception handling:** Unhandled exceptions may cause script to exit without proper cleanup/logging
3. **DualWriter buffering:** Logs may be buffered but not flushed on interruption
4. **ProcessPoolExecutor:** Even with thread_count=1, there's a ProcessPoolExecutor code path that may have issues on Windows
5. **File handle limits:** Too many open parquet files

## Verification Requirements
1. Run script with verbose error handling
2. Monitor memory usage during execution
3. Ensure all 17 output files are created
4. Verify stats.json completeness
5. Verify report_step_2_1.md generation
6. Check log file is properly written
</context>

<tasks>

<task type="auto">
  <name>Task 1: Investigate root cause of incomplete runs</name>
  <files>2_Scripts/2_Text/2.1_TokenizeAndCount.py</files>
  <action>
Investigate why recent runs are producing incomplete outputs and empty logs:

1. **Check for unhandled exceptions:**
   - Review the main() function for try/except blocks
   - Ensure exceptions are logged before exiting
   - Check if DualWriter flushes on exception

2. **Check memory handling:**
   - Review @track_memory_usage decorator implementation
   - Check if memory limits are being exceeded
   - Look for potential memory leaks in the processing loop

3. **Check log file handling:**
   - Verify DualWriter implementation ensures flush on exit
   - Check if log file is opened with proper buffering settings
   - Ensure log path exists before writing

4. **Test script manually:**
   - Run with --dry-run to verify prerequisites
   - Run script and capture stderr separately
   - Monitor memory usage during execution

Based on findings, implement fixes:
- Add try/except around main processing with proper logging
- Ensure DualWriter.flush() is called on all exit paths
- Add explicit gc.collect() calls between year processing
- Add verbose progress output for each year
- Ensure all file handles are properly closed
</action>
  <verify>
1. Run: python 2_Scripts/2_Text/2.1_TokenizeAndCount.py --dry-run
2. Check that any errors are properly displayed
3. Verify DualWriter flush implementation
</verify>
  <done>
Root cause identified and documented. Fixes implemented for:
- Exception handling with proper logging
- Log file flushing on all exit paths
- Memory management improvements
- Progress output enhancements
</done>
</task>

<task type="auto">
  <name>Task 2: Run script at full scale and monitor execution</name>
  <files>2_Scripts/2_Text/2.1_TokenizeAndCount.py</files>
  <action>
Execute script 2.1_TokenizeAndCount.py at full scale with monitoring:

1. **Before execution:**
   - Verify all input files exist (speaker_data_2002-2018.parquet)
   - Clean up any incomplete output directories
   - Ensure sufficient disk space

2. **Execute with monitoring:**
   - Run: python 2_Scripts/2_Text/2.1_TokenizeAndCount.py
   - Monitor progress through log file output
   - Track memory usage during execution
   - Verify each year file is created as processing progresses

3. **After completion:**
   - Count output files (should be 17)
   - Verify log file is non-empty
   - Check stats.json exists and is valid JSON
   - Check report_step_2_1.md exists

4. **Data verification:**
   - For each output file, verify row counts match expectations
   - Check for missing or corrupted data
   - Verify total tokens and vocabulary hit counts
   - Validate category counts are non-negative
</action>
  <verify>
1. ls 4_Outputs/2_Textual_Analysis/2.1_Tokenized/[timestamp]/linguistic_counts_*.parquet | wc -l (should be 17)
2. Check log file size > 0
3. python -c "import json; print(json.load(open('stats.json')))" (should parse without error)
4. Verify report_step_2_1.md exists and is non-empty
</verify>
  <done>
Script executed successfully. All 17 output files generated.
Log file properly written with complete execution trace.
stats.json and report_step_2_1.md generated successfully.
</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete set of linguistic count outputs for all 17 years (2002-2018)</what-built>
  <how-to-verify>
1. Open the latest output directory: 4_Outputs/2_Textual_Analysis/2.1_Tokenized/[timestamp]/
2. Verify all 17 files exist: linguistic_counts_2002.parquet through linguistic_counts_2018.parquet
3. Open stats.json and verify:
   - tokenize_input section exists
   - tokenize_process section exists with category_hit_rates
   - tokenize_output section exists with category distributions
   - processing.years_processed == 17
4. Open report_step_2_1.md and verify comprehensive statistics are presented
5. Check log file in 3_Logs/2.1_TokenizeAndCount/[timestamp].log is non-empty
6. Load a few parquet files and verify data integrity (row counts, non-negative values)
</how-to-verify>
  <resume-signal>Type "approved" if the outputs are complete and verified, or describe any issues found</resume-signal>
</task>

</tasks>

<verification>
After implementation:
1. Script executes without premature termination
2. All 17 yearly output files are generated
3. Log file contains complete execution trace
4. stats.json contains all expected sections
5. report_step_2_1.md contains comprehensive statistics
6. No incomplete/corrupted output directories remain
</verification>

<success_criteria>
- Root cause of incomplete runs identified and fixed
- Script successfully processes all 17 years
- All 17 output files generated in a single execution
- Log file properly written with complete trace
- stats.json and report_step_2_1.md generated
- Data integrity verified across all outputs
</success_criteria>

<output>
After completion, create `.planning/quick/024-debug-script-21/024-SUMMARY.md`
</output>
