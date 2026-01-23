# Phase 15: Scaling Preparation - Context

**Gathered:** 2026-01-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove scaling limits for future growth - identify and remove hardcoded constraints that prevent the pipeline from handling larger datasets or more complex analyses.

</domain>

<decisions>
## Implementation Decisions

### Limit identification approach
- Manual code review to find hardcoded constants, size checks, and capacity constraints in scripts
- Search through all pipeline scripts for suspicious numerical limits, array size constraints, and conditional checks

### Removal priority
- Focus on critical path limits first (limits in the main pipeline flow)
- Prioritize limits in the data processing flow: Step 1 (Sample) → Step 2 (Text) → Step 3 (Financial) → Step 4 (Econometric)
- After critical path limits, address limits in utility functions and helper modules

### Limit types to address
- All types of scaling limits:
  - Data size limits (row counts, file size constraints, memory limits)
  - Processing limits (batch sizes, parallelization caps, timeout values)
  - Time range limits (hardcoded date ranges, year constraints)
  - Entity count limits (number of companies, CEOs, transcripts)
  - Dictionary/vocabulary size limits (text processing token counts)

### Error handling for unscalable operations
- Resource-aware throttling: monitor system resources (memory, CPU, disk I/O), adapt or throttle as needed when truly unscalable operations are attempted
- If system resources become constrained, gracefully adjust processing parameters rather than failing
- Log throttling decisions for observability

### OpenCode's Discretion

**Testing strategy:**
- Choose appropriate approach for verifying scaling limit removals (benchmark datasets, load testing, or enhanced test coverage)

**Documentation scope:**
- Determine appropriate level of documentation for removed limits (before/after comparisons, inline comments, or architecture updates)

**Configuration approach:**
- Decide whether to make new constraints configurable via config/project.yaml, fully dynamic, or a mixed approach based on use case

**Performance tradeoffs:**
- Balance capacity and performance considering the user's PC resource capacity
- Determine how to optimize the pipeline to handle larger datasets without degrading performance on normal-sized data

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for scaling data pipelines

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 15-scaling-preparation*
*Context gathered: 2026-01-23*
