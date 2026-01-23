# Roadmap: F1D Data Pipeline

## Overview

This roadmap transforms an existing 4-stage research data pipeline into a fully documented, observable replication package ready for thesis submission and journal review. The journey starts by establishing inline statistics patterns on a pilot script, then rolls out comprehensive metrics across all pipeline stages (Sample → Text → Financial → Econometric), culminates in DCAS-compliant README documentation, and concludes with pre-submission verification ensuring paper tables match generated outputs.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Template & Pilot** - Establish inline stats pattern on 1.1_CleanMetadata
- [ ] **Phase 2: Step 1 Sample** - Roll out stats to all Step 1 scripts with sample construction metrics
- [ ] **Phase 3: Step 2 Text** - Roll out stats to all Step 2 scripts with text processing metrics
- [ ] **Phase 4: Steps 3-4 Financial & Econometric** - Roll out stats to Steps 3-4 with final dataset summaries
- [ ] **Phase 5: README & Documentation** - Create DCAS-compliant README for thesis/journal submission
- [ ] **Phase 6: Pre-Submission Verification** - Final validation ensuring outputs match paper tables

## Phase Details

### Phase 1: Template & Pilot
**Goal**: Establish inline statistics pattern proven on one representative script
**Depends on**: Nothing (first phase)
**Requirements**: STAT-01, STAT-02, STAT-03, STAT-04, STAT-05, STAT-06, STAT-07, STAT-08, STAT-09, STAT-10, STAT-11, STAT-12
**Success Criteria** (what must be TRUE):
  1. 1.1_CleanMetadata outputs input/output row counts to console via DualWriter
  2. 1.1_CleanMetadata produces stats.json in timestamped output directory
  3. stats.json contains all required metrics (row counts, missing values, timing, checksums)
  4. Pattern uses inline helper functions (print_stat, print_stats_summary, save_stats) for copy-paste reuse
  5. Merge diagnostics pattern established for scripts with joins
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Define stats schema and helper function templates
- [ ] 01-02-PLAN.md — Implement inline stats in 1.1_CleanMetadata
- [ ] 01-03-PLAN.md — Validate stats.json output and console display

### Phase 2: Step 1 Sample
**Goal**: All Step 1 scripts output comprehensive sample construction statistics
**Depends on**: Phase 1
**Requirements**: SAMP-01, SAMP-02, SAMP-03, SAMP-04, SAMP-05, SAMP-06, SAMP-07
**Success Criteria** (what must be TRUE):
  1. Each Step 1 script (1.0-1.4) outputs stats to console and stats.json
  2. Filter cascade table shows universe → filters → final N for sample construction
  3. Entity linking success rates reported by method (CUSIP, ticker, fuzzy name)
  4. CEO identification rates included (% calls matched to CEO)
  5. Industry distribution (Fama-French) and time distribution (by year) documented
**Plans**: TBD

Plans:
- [ ] 02-01: Add stats to 1.0_BuildSampleManifest
- [ ] 02-02: Add stats to 1.1_CleanMetadata (enhance from Phase 1)
- [ ] 02-03: Add stats to 1.2_LinkEntities with entity linking metrics
- [ ] 02-04: Add stats to 1.3_BuildTenureMap with CEO identification metrics
- [ ] 02-05: Add stats to 1.4_AssembleManifest with sample summary

### Phase 3: Step 2 Text
**Goal**: All Step 2 scripts output text processing statistics
**Depends on**: Phase 2
**Requirements**: (Rollout of STAT-01-12 pattern to Step 2 scripts)
**Success Criteria** (what must be TRUE):
  1. Each Step 2 script (2.1-2.3) outputs stats to console and stats.json
  2. Tokenization statistics include per-year breakdowns and word count distributions
  3. Dictionary version and vocabulary coverage documented
  4. Text variable distributions summarized (clarity, tone measures)
**Plans**: TBD

Plans:
- [ ] 03-01: Add stats to 2.1_TokenizeAndCount with tokenization metrics
- [ ] 03-02: Add stats to 2.2_ConstructVariables with text variable summaries
- [ ] 03-03: Add stats to 2.3_VerifyStep2 with verification diagnostics

### Phase 4: Steps 3-4 Financial & Econometric
**Goal**: All Steps 3-4 scripts output statistics with final dataset summaries
**Depends on**: Phase 3
**Requirements**: SUMM-01, SUMM-02, SUMM-03, SUMM-04
**Success Criteria** (what must be TRUE):
  1. Each Step 3 script (3.0-3.3) outputs stats to console and stats.json
  2. Each Step 4 script (4.1-4.3) outputs stats to console and stats.json
  3. Merge diagnostics show matched/unmatched counts for all financial data joins
  4. Final analysis dataset includes descriptive statistics (N, Mean, SD, Min, P25, Median, P75, Max)
  5. Correlation matrix for regression variables exported as CSV
**Plans**: TBD

Plans:
- [ ] 04-01: Add stats to 3.0_BuildFinancialFeatures
- [ ] 04-02: Add stats to 3.1_FirmControls with merge diagnostics
- [ ] 04-03: Add stats to 3.2_MarketVariables with merge diagnostics
- [ ] 04-04: Add stats to 3.3_EventFlags
- [ ] 04-05: Add stats to 4.1_EstimateCeoClarity suite (4.1, 4.1.1-4.1.4)
- [ ] 04-06: Add stats to 4.2_LiquidityRegressions
- [ ] 04-07: Add stats to 4.3_TakeoverHazards
- [ ] 04-08: Generate final dataset summary statistics (SUMM-01-04)

### Phase 5: README & Documentation
**Goal**: DCAS-compliant README ready for thesis/journal submission
**Depends on**: Phase 4
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04, DOC-05, DOC-06, DOC-07
**Success Criteria** (what must be TRUE):
  1. README includes requirements.txt with Python version and all pinned package versions
  2. README includes step-by-step execution instructions (numbered, copy-paste ready)
  3. README includes program-to-output mapping (script → table/figure in paper)
  4. README includes pipeline flow diagram (Mermaid or ASCII)
  5. README includes variable codebook for final analysis datasets
**Plans**: TBD

Plans:
- [ ] 05-01: Create requirements.txt with pinned dependencies
- [ ] 05-02: Write execution instructions section
- [ ] 05-03: Create pipeline flow diagram
- [ ] 05-04: Write program-to-output mapping
- [ ] 05-05: Create variable codebook
- [ ] 05-06: Document data sources (CRSP, Compustat, transcripts)
- [ ] 05-07: Assemble final README.md

### Phase 6: Pre-Submission Verification
**Goal**: Verified replication package ready for deposit
**Depends on**: Phase 5
**Requirements**: (Validation phase - verifies all prior requirements)
**Success Criteria** (what must be TRUE):
  1. Full pipeline runs end-to-end without errors on fresh environment
  2. All stats.json files validate against expected schema
  3. Generated statistics match paper tables exactly
  4. Pre-submission checklist completed (all 16 pitfalls from research addressed)
**Plans**: TBD

Plans:
- [ ] 06-01: Clean environment test (fresh Python env, run full pipeline)
- [ ] 06-02: Validate all stats.json files against schema
- [ ] 06-03: Compare generated statistics to paper tables
- [ ] 06-04: Complete pre-submission checklist

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Template & Pilot | 0/3 | Planned | - |
| 2. Step 1 Sample | 0/5 | Not started | - |
| 3. Step 2 Text | 0/3 | Not started | - |
| 4. Steps 3-4 Financial & Econometric | 0/8 | Not started | - |
| 5. README & Documentation | 0/7 | Not started | - |
| 6. Pre-Submission Verification | 0/4 | Not started | - |

---
*Roadmap created: 2026-01-22*
*Total plans: 30 | Total requirements: 30 mapped*
