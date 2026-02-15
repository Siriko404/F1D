# Phase 79: Test Stage 1 Sample Scripts - Context

**Gathered:** 2026-02-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Validate the Stage 1 sample pipeline (5 scripts: 1.0-1.4) runs correctly at production scale, conforms to v5/v6 architecture standards, and produces verifiable outputs. This is an audit and debugging phase for existing infrastructure — not building new features.

</domain>

<decisions>
## Implementation Decisions

### Testing Scope & Scale

- **Scripts to test:** All 5 sample scripts (1.0_BuildSampleManifest, 1.1_CleanMetadata, 1.2_LinkEntities, 1.3_BuildTenureMap, 1.4_AssembleManifest)
- **Data years:** All years (2002-2018) — full historical range
- **Quarters:** All quarters (Q1-Q4) — complete annual cycles
- **Data source:** Real data from inputs folder (actual production data, not synthetic fixtures)

### Pass/Fail Criteria

- **No prior outputs to compare against** — this is first comprehensive validation
- **Primary success metric:** Code review for logical correctness + flawless execution
- **Validation approach:** Read scripts to understand expected behavior, then verify outputs match expectations
- **Schema validation:** Outputs match expected columns/types from script analysis
- **Value validation:** Values are logically consistent with script purpose and input data

### Issue Handling

- **Fix mode:** Fix issues immediately as discovered during testing
- **Stop criteria:** Stop on first error, fix, then continue
- **Issue tracking:** Formal issue tracking (TODOs/issues in codebase)
- **Regression prevention:** Add tests for each fixed issue

### Audit Depth & Reporting

- **Audit scope:** Comprehensive — full dataflow trace + standards compliance + performance metrics
- **Report format:** Both markdown report AND structured data file (JSON/YAML)
- **Metrics to capture:**
  - Performance timing (wall-clock time per script, throughput)
  - Data profile stats (row counts, column counts, null rates, type distribution)
  - Code quality metrics (import patterns, legacy code usage, standard compliance)
  - Resource utilization (memory usage, disk I/O)
- **Output persistence:** Keep all test outputs in dedicated folder for inspection

### Claude's Discretion

- Exact report file names and locations
- Specific performance thresholds that constitute "acceptable"
- Structured data file format (JSON vs YAML)
- Organization of output storage folder

</decisions>

<specifics>
## Specific Ideas

- "Read the scripts, make sure they make sense logically for the purpose they have in the pipeline"
- "Make sure they execute flawlessly, exactly according to the expected output understood from reading the scripts yourself"
- No prior outputs to compare against — first comprehensive validation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 79-test-stage-1-sample-scripts*
*Context gathered: 2026-02-14*
