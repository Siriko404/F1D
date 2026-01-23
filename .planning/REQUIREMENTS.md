# Requirements: F1D Data Pipeline

**Defined:** 2026-01-22
**Core Value:** Every script must produce verifiable, reproducible results with complete audit trails

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Per-Script Statistics

- [x] **STAT-01**: Each script outputs input row count at start of processing
- [x] **STAT-02**: Each script outputs output row count at end of processing
- [x] **STAT-03**: Each script outputs row delta (input - output) with percentage
- [x] **STAT-04**: Each script outputs per-variable missing value counts
- [x] **STAT-05**: Each script outputs per-variable missing value percentages
- [x] **STAT-06**: Each script outputs processing duration in seconds
- [x] **STAT-07**: Each script outputs timestamp of execution start/end
- [x] **STAT-08**: Each script outputs stats.json file alongside data outputs
- [x] **STAT-09**: Each script outputs input file MD5/SHA256 checksums
- [x] **STAT-10**: Each script with merges outputs merge diagnostics (matched/unmatched counts)
- [x] **STAT-11**: Each script with merges outputs merge type verification (1:1, 1:m, m:1)
- [x] **STAT-12**: Stats designed from data scientist POV with script-specific metrics

### Sample Construction Documentation

- [x] **SAMP-01**: Step 1 outputs filter cascade table (universe → filter₁ → filter₂ → final N)
- [x] **SAMP-02**: Step 1.2 outputs entity linking success rates by method (CUSIP, ticker, fuzzy name)
- [x] **SAMP-03**: Step 1.3/1.4 outputs CEO identification rates (% calls matched to CEO)
- [x] **SAMP-04**: Step 1 outputs industry distribution (calls by Fama-French industry)
- [x] **SAMP-05**: Step 1 outputs time distribution (calls by year)
- [x] **SAMP-06**: Step 1 outputs unique firm count (distinct GVKEYs)
- [x] **SAMP-07**: Step 1 outputs unique CEO count

### README Documentation

- [x] **DOC-01**: README includes requirements.txt with Python version and all package versions
- [x] **DOC-02**: README includes step-by-step execution instructions
- [x] **DOC-03**: README includes program-to-output mapping (script → table/figure)
- [x] **DOC-04**: README includes pipeline flow diagram (Mermaid or ASCII)
- [x] **DOC-05**: README includes variable codebook for final analysis datasets
- [x] **DOC-06**: README documents each script's purpose, inputs, and outputs
- [x] **DOC-07**: README documents data sources (CRSP, Compustat, transcripts)

### Summary Statistics

- [x] **SUMM-01**: Final dataset includes descriptive statistics (N, Mean, SD, Min, P25, Median, P75, Max)
- [x] **SUMM-02**: Final dataset includes correlation matrix for regression variables
- [x] **SUMM-03**: Final dataset includes panel balance diagnostics (coverage by firm-year)
- [x] **SUMM-04**: Summary statistics exportable as CSV for paper Table 1

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Enhanced Observability

- **OBS-01**: Memory usage tracking per script
- **OBS-02**: Throughput metrics (rows/second)
- **OBS-03**: Intermediate file checksums between steps
- **OBS-04**: Data quality anomaly flags

### Advanced Documentation

- **ADOC-01**: Data Availability Statement (WRDS access instructions)
- **ADOC-02**: Computational requirements (runtime, memory estimates)
- **ADOC-03**: Interactive Jupyter sample explorer
- **ADOC-04**: Transformation summaries (before/after for each step)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Shared statistics module | Breaks self-contained replication; each script must stand alone |
| Aggregate pipeline summary | Per-script stats are sufficient |
| Methodology rationale in README | Belongs in paper/thesis, not code docs |
| Automated testing framework | Verification scripts exist, formal testing deferred |
| Interactive dashboards/web UI | Batch processing for replication |
| Real-time monitoring | Timestamped logs are sufficient |
| Cross-platform compatibility testing | Document platform; don't test all |
| ydata-profiling or similar | Overkill for embedded stats |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

 | Requirement | Phase | Status |
|-------------|-------|--------|
| STAT-01 | Phase 1 | ✅ COMPLETED |
| STAT-02 | Phase 1 | ✅ COMPLETED |
| STAT-03 | Phase 1 | ✅ COMPLETED |
| STAT-04 | Phase 1 | ✅ COMPLETED |
| STAT-05 | Phase 1 | ✅ COMPLETED |
| STAT-06 | Phase 1 | ✅ COMPLETED |
| STAT-07 | Phase 1 | ✅ COMPLETED |
| STAT-08 | Phase 1 | ✅ COMPLETED |
| STAT-09 | Phase 1 | ✅ COMPLETED |
| STAT-10 | Phase 1 | ✅ COMPLETED |
| STAT-11 | Phase 1 | ✅ COMPLETED |
| STAT-12 | Phase 1 | ✅ COMPLETED |
| SAMP-01 | Phase 2 | ✅ COMPLETED |
| SAMP-02 | Phase 2 | ✅ COMPLETED |
| SAMP-03 | Phase 2 | ✅ COMPLETED |
| SAMP-04 | Phase 2 | ✅ COMPLETED |
| SAMP-05 | Phase 2 | ✅ COMPLETED |
| SAMP-06 | Phase 2 | ✅ COMPLETED |
| SAMP-07 | Phase 2 | ✅ COMPLETED |
| DOC-01 | Phase 5 | ✅ COMPLETED |
| DOC-02 | Phase 5 | ✅ COMPLETED |
| DOC-03 | Phase 5 | ✅ COMPLETED |
| DOC-04 | Phase 5 | ✅ COMPLETED |
| DOC-05 | Phase 5 | ✅ COMPLETED |
| DOC-06 | Phase 5 | ✅ COMPLETED |
| DOC-07 | Phase 5 | ✅ COMPLETED |
| SUMM-01 | Phase 4 | ✅ COMPLETED |
| SUMM-02 | Phase 4 | ✅ COMPLETED |
| SUMM-03 | Phase 4 | ✅ COMPLETED |
| SUMM-04 | Phase 4 | ✅ COMPLETED |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30 ✓
- Unmapped: 0
- Completed: 30/30 (100%)

**Phase Distribution:**
- Phase 1 (Template & Pilot): 12 requirements (STAT-01-12) ✅ COMPLETED
- Phase 2 (Step 1 Sample): 7 requirements (SAMP-01-07) ✅ COMPLETED
- Phase 3 (Step 2 Text): rollout phase (inherits STAT pattern) ✅ COMPLETED
- Phase 4 (Steps 3-4): 4 requirements (SUMM-01-04) ✅ COMPLETED
- Phase 5 (README): 7 requirements (DOC-01-07) ✅ COMPLETED
- Phase 6 (Verification): validation phase (verifies all) ✅ COMPLETED

---
*Requirements defined: 2026-01-22*
*Last updated: 2026-01-22 after Phase 6 completion*
*Status: ALL REQUIREMENTS MET (30/30)*
