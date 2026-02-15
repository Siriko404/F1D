---
phase: 80-test-stage-2-text-scripts
plan: 00
type: overview
wave: 0
depends_on: ["79"]
files_modified:
  - .planning/verification/
  - 4_Outputs/2_Textual_Analysis/2.1_TokenizeAndCount/
  - 4_Outputs/2_Textual_Analysis/2.2_ConstructVariables/
autonomous: false
must_haves:
  truths:
    - "All Stage 2 scripts execute successfully with --dry-run"
    - "All Stage 2 scripts execute successfully at full scale"
    - "Text tokenization produces valid word count files"
    - "Variable construction produces valid linguistic measures"
    - "All outputs have expected schema and logical values"
    - "All scripts comply with V6.1 architecture standards"
    - "Audit report generated in markdown AND JSON formats"
    - "Any issues found are fixed and documented"
  artifacts:
    - path: ".planning/verification/80-audit-report.md"
      provides: "Human-readable audit report"
    - path: ".planning/verification/80-audit-report.json"
      provides: "Machine-readable audit data"
    - path: "4_Outputs/2_Textual_Analysis/2.2_ConstructVariables/*/linguistic_variables.parquet"
      provides: "Final linguistic variables for downstream analysis"
  key_links:
    - from: "4_Outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet"
      to: "2.1_TokenizeAndCount"
      via: "load_validated_parquet"
    - from: "1_Inputs/transcript/*.txt"
      to: "2.1_TokenizeAndCount"
      via: "file reading"
    - from: "4_Outputs/2.1_TokenizeAndCount/*/word_counts.parquet"
      to: "2.2_ConstructVariables"
      via: "get_latest_output_dir"
    - from: "2.2_ConstructVariables"
      to: "Downstream hypothesis testing"
      via: "linguistic_variables.parquet"
---

# Phase 80: Test Stage 2 Text Scripts at Full Scale

**Goal:** Test Stage 2 text processing scripts at full scale, audit dataflow, fix to V6 standards, verify outputs, debug problems

**Depends on:** Phase 79 (Stage 1 Sample Scripts Testing)

**Status:** PLANNED

## Overview

Phase 80 validates the complete Stage 2 text processing pipeline at production scale:
- Processes all 112,968 earnings calls from Stage 1
- Tokenizes transcripts and counts word occurrences
- Constructs linguistic variables for analysis
- First comprehensive validation since architecture migration to V6.1

## User Constraints (Locked Decisions)

1. **Testing Scope:** All Stage 2 scripts (2.1, 2.2, report, verify), real data
2. **Pass/Fail:** Validate via code review + execution correctness
3. **Issue Handling:** Fix immediately as discovered, stop on first error, formal tracking
4. **Audit Depth:** Comprehensive - full dataflow trace, standards compliance, performance metrics
5. **Reports:** Both markdown AND structured data file (JSON)
6. **Output Persistence:** Keep all test outputs in dedicated folder

## V6.1 Standards to Verify

- All imports use f1d.shared.* namespace
- Zero sys.path.insert() calls
- mypy passes with 0 errors
- Scripts execute with --dry-run validation

## Scripts to Test

| Script | Purpose | Dependencies |
|--------|---------|--------------|
| 2.1_TokenizeAndCount | Tokenize transcripts, count words | Stage 1 manifest, transcript files |
| 2.2_ConstructVariables | Build linguistic variables | 2.1 word_counts output |
| report_step2.py | Generate Stage 2 reports | 2.2 output |
| verify_step2.py | Verify Stage 2 outputs | 2.2 output |

## Dataflow

```
4_Outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet (113K rows)
    |
    v 2.1_TokenizeAndCount
4_Outputs/2_Textual_Analysis/2.1_TokenizeAndCount/*/word_counts.parquet
    |
    v 2.2_ConstructVariables
4_Outputs/2_Textual_Analysis/2.2_ConstructVariables/*/linguistic_variables.parquet
```

**Expected Processing:**
- Input: 112,968 earnings call file_names from manifest
- Tokenization: Process transcript .txt files, count word occurrences
- Variable Construction: Aggregate word stats into call-level linguistic measures

## Plan Structure

| Plan | Wave | Objective | Tasks |
|------|------|-----------|-------|
| 80-01 | 1 | Standards compliance + dry-run validation | 3 |
| 80-02 | 2 | Full-scale execution of all Stage 2 scripts | 4 |
| 80-03 | 3 | Schema and data quality validation | 3 |
| 80-04 | 4 | Generate audit reports (MD + JSON) | 2 |

**Total Plans:** 4
**Total Tasks:** 12

## Wave Structure

- **Wave 1 (80-01):** Standards audit and dry-run validation (parallel)
- **Wave 2 (80-02):** Full-scale execution (sequential dependencies)
- **Wave 3 (80-03):** Output validation (depends on Wave 2)
- **Wave 4 (80-04):** Report generation (depends on Waves 1-3)

## Success Criteria

1. All Stage 2 scripts execute successfully with --dry-run
2. All Stage 2 scripts execute successfully at full scale
3. Text tokenization produces valid word count files
4. Variable construction produces valid linguistic measures
5. All outputs have expected schema and logical values
6. All scripts comply with V6.1 architecture standards
7. Audit report generated with all required metrics
8. Any issues found are fixed and documented

## Output Files

### Verification Reports
- `.planning/verification/80-standards-audit.json` - V6.1 compliance audit
- `.planning/verification/80-dry-run-results.json` - Dry-run execution results
- `.planning/verification/80-execution-audit.json` - Full execution metrics
- `.planning/verification/80-schema-validation.json` - Schema check results
- `.planning/verification/80-data-profile.json` - Data quality statistics
- `.planning/verification/80-audit-report.md` - Human-readable report
- `.planning/verification/80-audit-report.json` - Machine-readable report

### Stage 2 Outputs
- `4_Outputs/2_Textual_Analysis/2.1_TokenizeAndCount/*/word_counts.parquet`
- `4_Outputs/2_Textual_Analysis/2.2_ConstructVariables/*/linguistic_variables.parquet`

## Execution Notes

- **Stop on first error:** If any script fails, stop and fix before continuing
- **Issue tracking:** Document all issues in audit report
- **Fix-on-find:** Plans 80-01 and 80-03 include remediation tasks to fix issues discovered during audit/validation
- **Regression prevention:** Add tests for any issues discovered
- **Output persistence:** All outputs saved to 4_Outputs/ with timestamps
- **Re-validation:** After fixes in 80-01 or 80-03, re-run affected validations to confirm resolution

---

*Phase 80 planned: 2026-02-15*
