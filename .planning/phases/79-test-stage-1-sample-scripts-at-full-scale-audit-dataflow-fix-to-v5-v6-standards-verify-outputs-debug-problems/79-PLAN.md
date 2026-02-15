---
phase: 79-test-stage-1-sample-scripts
plan: 00
type: overview
wave: 0
depends_on: ["78"]
files_modified:
  - .planning/verification/
  - 4_Outputs/1.0_BuildSampleManifest/
  - 4_Outputs/1.1_CleanMetadata/
  - 4_Outputs/1.2_LinkEntities/
  - 4_Outputs/1.3_BuildTenureMap/
  - 4_Outputs/1.4_AssembleManifest/
autonomous: false
must_haves:
  truths:
    - "All 5 sample scripts execute successfully with --dry-run"
    - "All 5 sample scripts execute successfully at full scale (2002-2018)"
    - "All outputs have expected schema and logical values"
    - "All scripts comply with V6.1 architecture standards"
    - "Audit report generated in markdown AND JSON formats"
    - "Any issues found are fixed and documented"
  artifacts:
    - path: ".planning/verification/79-audit-report.md"
      provides: "Human-readable audit report"
    - path: ".planning/verification/79-audit-report.json"
      provides: "Machine-readable audit data"
    - path: "4_Outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet"
      provides: "Final sample universe for downstream analysis"
  key_links:
    - from: "1_Inputs/Unified-info.parquet"
      to: "1.1_CleanMetadata"
      via: "load_validated_parquet"
    - from: "1.1_CleanMetadata"
      to: "1.2_LinkEntities"
      via: "get_latest_output_dir"
    - from: "1_Inputs/Execucomp/comp_execucomp.parquet"
      to: "1.3_BuildTenureMap"
      via: "load_validated_parquet"
    - from: "1.2_LinkEntities + 1.3_BuildTenureMap"
      to: "1.4_AssembleManifest"
      via: "merge on gvkey/year/month"
    - from: "1.4_AssembleManifest"
      to: "1.0_BuildSampleManifest"
      via: "orchestrator copy"
---

# Phase 79: Test Stage 1 Sample Scripts at Full Scale

**Goal:** Test Stage 1 sample scripts at full scale, audit dataflow, fix to V5/V6 standards, verify outputs, debug problems

**Depends on:** Phase 78 (Documentation Synchronization)

**Status:** ✅ COMPLETE - All 4 plans finished, Stage 1 pipeline production-ready

## Overview

Phase 79 validates the complete Stage 1 sample construction pipeline at production scale:
- Full historical range (2002-2018)
- All quarters (Q1-Q4)
- Real production data from 1_Inputs/

This is the first comprehensive validation since architecture migration to V6.1.

## User Constraints (Locked Decisions)

From CONTEXT.md research:

1. **Testing Scope:** All 5 sample scripts (1.0-1.4), all years, all quarters, real data
2. **Pass/Fail:** No prior outputs to compare - validate via code review + execution correctness
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
| 1.0_BuildSampleManifest | Orchestrator | None (calls substeps) |
| 1.1_CleanMetadata | Clean and filter raw metadata | None |
| 1.2_LinkEntities | Link calls to CRSP/Compustat CCM | 1.1 output |
| 1.3_BuildTenureMap | Build CEO tenure panel | None |
| 1.4_AssembleManifest | Join and filter final manifest | 1.2, 1.3 outputs |

## Dataflow

```
1_Inputs/Unified-info.parquet (55MB, ~500K rows)
    |
    v 1.1_CleanMetadata
4_Outputs/1.1_CleanMetadata/*/metadata_cleaned.parquet (~250K rows)
    |
    v 1.2_LinkEntities
4_Outputs/1.2_LinkEntities/*/metadata_linked.parquet (~200K rows)
    |
    v 1.4_AssembleManifest <-- 1.3_BuildTenureMap
    |                          |
    |                          v
    |                    4_Outputs/1.3_BuildTenureMap/*/tenure_monthly.parquet
    v
4_Outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet (~150K rows)
```

## Plan Structure

| Plan | Wave | Objective | Tasks | Status |
|------|------|-----------|-------|--------|
| 79-01 | 1 | Standards compliance + dry-run validation | 2 | ✅ COMPLETE |
| 79-02 | 2 | Full-scale execution of all 5 scripts | 5 | ✅ COMPLETE |
| 79-03 | 3 | Schema and data quality validation | 2 | ✅ COMPLETE |
| 79-04 | 4 | Generate audit reports (MD + JSON) | 2 | ✅ COMPLETE |

**Total Plans:** 4
**Completed:** 4 ✅
**Total Tasks:** 11
**Completed:** 11 ✅

## Wave Structure

- **Wave 1 (79-01):** Standards audit and dry-run validation (parallel) ✅ COMPLETE
- **Wave 2 (79-02):** Full-scale execution (sequential dependencies) ✅ COMPLETE
- **Wave 3 (79-03):** Output validation (depends on Wave 2) ✅ COMPLETE
- **Wave 4 (79-04):** Report generation (depends on Waves 1-3) ✅ COMPLETE

## Success Criteria

1. All 5 scripts execute successfully with --dry-run
2. All 5 scripts execute successfully at full scale (2002-2018)
3. All outputs have expected schema and logical values
4. All scripts comply with V6.1 architecture standards
5. Audit report generated with all required metrics
6. Any issues found are fixed and documented

## Output Files

### Verification Reports
- `.planning/verification/79-standards-audit.json` - V6.1 compliance audit
- `.planning/verification/79-dry-run-results.json` - Dry-run execution results
- `.planning/verification/79-execution-audit.json` - Full execution metrics
- `.planning/verification/79-schema-validation.json` - Schema check results
- `.planning/verification/79-data-profile.json` - Data quality statistics
- `.planning/verification/79-audit-report.md` - Human-readable report
- `.planning/verification/79-audit-report.json` - Machine-readable report

### Stage 1 Outputs
- `4_Outputs/1.1_CleanMetadata/*/metadata_cleaned.parquet`
- `4_Outputs/1.2_LinkEntities/*/metadata_linked.parquet`
- `4_Outputs/1.3_BuildTenureMap/*/tenure_monthly.parquet`
- `4_Outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet`
- `4_Outputs/1.0_BuildSampleManifest/*/master_sample_manifest.parquet`

## Execution Notes

- **Stop on first error:** If any script fails, stop and fix before continuing
- **Issue tracking:** Document all issues in audit report
- **Regression prevention:** Add tests for any issues discovered
- **Output persistence:** All outputs saved to 4_Outputs/ with timestamps

---

*Phase 79 planned: 2026-02-14*
