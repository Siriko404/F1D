# Requirements: F1D Data Pipeline

**Defined:** 2026-01-22
**Core Value:** Every script must produce verifiable, reproducible results with complete audit trails

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Per-Script Statistics

- [ ] **STAT-01**: Each script outputs input row count at start of processing
- [ ] **STAT-02**: Each script outputs output row count at end of processing
- [ ] **STAT-03**: Each script outputs row delta (input - output) with percentage
- [ ] **STAT-04**: Each script outputs per-variable missing value counts
- [ ] **STAT-05**: Each script outputs per-variable missing value percentages
- [ ] **STAT-06**: Each script outputs processing duration in seconds
- [ ] **STAT-07**: Each script outputs timestamp of execution start/end
- [ ] **STAT-08**: Each script outputs stats.json file alongside data outputs
- [ ] **STAT-09**: Each script outputs input file MD5/SHA256 checksums
- [ ] **STAT-10**: Each script with merges outputs merge diagnostics (matched/unmatched counts)
- [ ] **STAT-11**: Each script with merges outputs merge type verification (1:1, 1:m, m:1)
- [ ] **STAT-12**: Stats designed from data scientist POV with script-specific metrics

### Sample Construction Documentation

- [ ] **SAMP-01**: Step 1 outputs filter cascade table (universe → filter₁ → filter₂ → final N)
- [ ] **SAMP-02**: Step 1.2 outputs entity linking success rates by method (CUSIP, ticker, fuzzy name)
- [ ] **SAMP-03**: Step 1.3/1.4 outputs CEO identification rates (% calls matched to CEO)
- [ ] **SAMP-04**: Step 1 outputs industry distribution (calls by Fama-French industry)
- [ ] **SAMP-05**: Step 1 outputs time distribution (calls by year)
- [ ] **SAMP-06**: Step 1 outputs unique firm count (distinct GVKEYs)
- [ ] **SAMP-07**: Step 1 outputs unique CEO count

### README Documentation

- [ ] **DOC-01**: README includes requirements.txt with Python version and all package versions
- [ ] **DOC-02**: README includes step-by-step execution instructions
- [ ] **DOC-03**: README includes program-to-output mapping (script → table/figure)
- [ ] **DOC-04**: README includes pipeline flow diagram (Mermaid or ASCII)
- [ ] **DOC-05**: README includes variable codebook for final analysis datasets
- [ ] **DOC-06**: README documents each script's purpose, inputs, and outputs
- [ ] **DOC-07**: README documents data sources (CRSP, Compustat, transcripts)

### Summary Statistics

- [ ] **SUMM-01**: Final dataset includes descriptive statistics (N, Mean, SD, Min, P25, Median, P75, Max)
- [ ] **SUMM-02**: Final dataset includes correlation matrix for regression variables
- [ ] **SUMM-03**: Final dataset includes panel balance diagnostics (coverage by firm-year)
- [ ] **SUMM-04**: Summary statistics exportable as CSV for paper Table 1

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
| STAT-01 | Phase 1 | Pending |
| STAT-02 | Phase 1 | Pending |
| STAT-03 | Phase 1 | Pending |
| STAT-04 | Phase 1 | Pending |
| STAT-05 | Phase 1 | Pending |
| STAT-06 | Phase 1 | Pending |
| STAT-07 | Phase 1 | Pending |
| STAT-08 | Phase 1 | Pending |
| STAT-09 | Phase 1 | Pending |
| STAT-10 | Phase 1 | Pending |
| STAT-11 | Phase 1 | Pending |
| STAT-12 | Phase 1 | Pending |
| SAMP-01 | Phase 2 | Pending |
| SAMP-02 | Phase 2 | Pending |
| SAMP-03 | Phase 2 | Pending |
| SAMP-04 | Phase 2 | Pending |
| SAMP-05 | Phase 2 | Pending |
| SAMP-06 | Phase 2 | Pending |
| SAMP-07 | Phase 2 | Pending |
| DOC-01 | Phase 5 | Pending |
| DOC-02 | Phase 5 | Pending |
| DOC-03 | Phase 5 | Pending |
| DOC-04 | Phase 5 | Pending |
| DOC-05 | Phase 5 | Pending |
| DOC-06 | Phase 5 | Pending |
| DOC-07 | Phase 5 | Pending |
| SUMM-01 | Phase 4 | Pending |
| SUMM-02 | Phase 4 | Pending |
| SUMM-03 | Phase 4 | Pending |
| SUMM-04 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30 ✓
- Unmapped: 0

**Phase Distribution:**
- Phase 1 (Template & Pilot): 12 requirements (STAT-01-12)
- Phase 2 (Step 1 Sample): 7 requirements (SAMP-01-07)
- Phase 3 (Step 2 Text): rollout phase (inherits STAT pattern)
- Phase 4 (Steps 3-4): 4 requirements (SUMM-01-04)
- Phase 5 (README): 7 requirements (DOC-01-07)
- Phase 6 (Verification): validation phase (verifies all)

---
*Requirements defined: 2026-01-22*
*Last updated: 2026-01-22 after roadmap creation*
