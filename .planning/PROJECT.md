# F1D Data Processing Pipeline

## What This Is

A research data processing pipeline that constructs panel datasets for empirical finance research. The pipeline processes earnings call transcripts, links entities across databases, computes text-based measures (including speech uncertainty), merges financial controls, and runs econometric analyses testing hypotheses about managerial communication and corporate outcomes. Built for academic replication and thesis work.

## Core Value

Every script must produce verifiable, reproducible results with complete audit trails — if a reviewer cannot trace how a number was computed, the pipeline has failed.

## Current Milestone: v3.0 Codebase Cleanup & Optimization

**Started:** 2026-02-10
**Goal:** Fix critical bugs, improve code organization, add comprehensive documentation, and optimize performance while preserving all functionality

**Target outcomes:**
- Fix H7-H8 data truncation bug
- Archive backup files only (keep all V1/V2/V3 active)
- Split monolithic utilities for maintainability
- Comprehensive documentation (repo README, script docstrings, variable catalog)
- Performance optimizations (vectorization, eliminate anti-patterns)
- Enhanced testing (regression tests, coverage improvement)

## Requirements

### Validated

<!-- Shipped and confirmed valuable. Both v1.0 and v2.0 milestones complete. -->

- ✓ Sample construction from speaker data with entity linking — v1.0
- ✓ Text tokenization and word counting with dictionary lookups — v1.0
- ✓ Financial feature construction from CRSP/Compustat — v1.0
- ✓ Econometric regressions (CEO clarity, liquidity) — v1.0
- ✓ Configuration-driven execution via project.yaml — v1.0
- ✓ Timestamped output versioning — v1.0
- ✓ Dual logging to console and log files — v1.0
- ✓ Comprehensive descriptive statistics in every script — v1.0
- ✓ Statistics output to both console and structured files (JSON/CSV) — v1.0
- ✓ Data quality stats: row counts, missing values, distributions, anomalies — v1.0
- ✓ Processing metrics: timing, memory usage, throughput — v1.0
- ✓ Comprehensive README for academic reviewers — v1.0
- ✓ Pipeline flow diagram and variable codebook — v1.0
- ✓ CLI support with --help and --dry-run flags — v1.0
- ✓ Manual script execution without orchestrator — v1.0
- ✓ V2 folder structure for hypothesis testing scripts — v2.0
- ✓ Cash holdings variables (CHE/AT, leverage, controls) — v2.0
- ✓ Investment efficiency variables (over/underinvestment, Biddle residuals) — v2.0
- ✓ Payout policy variables (dividend stability, flexibility) — v2.0
- ✓ Panel econometric infrastructure (FE, clustering, 2SLS) — v2.0
- ✓ H1-H3 regression execution (144 regressions) — v2.0
- ✓ H5 analyst dispersion analysis (IBES merge, 28 regressions) — v2.0
- ✓ H6 SEC scrutiny analysis (CCCL instrument, 39 regressions) — v2.0

### Not Pursued

<!-- Requirements from cancelled/abandoned phases. Documented for completeness. -->

- Robustness checks (subsample analyses) — cancelled due to null results
- Identification strategies (manager FE, PSM) — cancelled due to null results
- Publication output (LaTeX tables) — cancelled due to null results
- H7-H10 hypotheses (turnover, compensation, returns, forecast accuracy) — abandoned with Phase 41

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Real-time chat/LLM-based uncertainty — dictionary-based approach per methodology
- Cross-country analysis — U.S. firms only for thesis scope
- Video/audio analysis — text transcripts only
- Interactive dashboards — batch processing for replication
- Causality claims without instrumentation — 2SLS required for causal inference

## Context

This is a thesis research project with an existing 4-stage pipeline:
1. **Sample** (1_Sample): Build sample manifest, clean metadata, link entities, build tenure map
2. **Text** (2_Text): Tokenize transcripts, construct text variables, verify outputs
3. **Financial** (3_Financial): Build financial features, firm controls, market variables, event flags
4. **Econometric** (4_Econometric): Run regressions for CEO clarity, tone, liquidity effects

V2 extensions added:
- **Financial_V2** (3_Financial_V2): Hypothesis-specific variable construction (H1-H3, H5, H6)
- **Econometric_V2** (4_Econometric_V2): Hypothesis testing regressions with FE and clustering

The pipeline follows strict conventions from CLAUDE.md:
- Root structure: `1_Inputs/`, `2_Scripts/`, `3_Logs/`, `4_Outputs/`, `config/`
- Naming: `<Stage>.<Step>_<PascalCaseName>.py`
- All scripts read from `config/project.yaml`
- Outputs go to timestamped directories

## Constraints

- **Reproducibility**: All outputs must be bitwise-identical for same inputs/config (seed 42, single thread)
- **Self-contained scripts**: Each script must be runnable independently without external orchestration
- **Academic standards**: Documentation must meet journal/thesis replication package requirements
- **Existing structure**: Must preserve current directory layout and naming conventions
- **No mocks**: Real data only; never fabricate test data without explicit approval
- **Model requirement**: ALL GSD agents must use Sonnet model only (no Opus, no Haiku) - set via model_profile="budget" in config.json

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Stats inline per script | Self-contained for replication; reviewers can trace any number | Implemented v1.0 |
| Stats to console + files | Human review during runs + machine-readable for analysis | Implemented v1.0 |
| README for academic reviewers | Primary audience is thesis committee and journal reviewers | Implemented v1.0 |
| Skip methodology in README | Methodology belongs in paper; README covers "how to run" | Implemented v1.0 |
| Cancel robustness phases on null results | Scientifically inappropriate to pursue robustness for unsupported hypotheses | Phases 36-38 cancelled |
| Abandon hypothesis suite discovery | Single hypothesis (H6) tested directly; remaining H7-H10 not pursued | Phase 41 abandoned |
| Document null results | Null findings are valid scientific results; documented in VERIFICATION.md | All phases documented |
| Sonnet-only model policy | Cost optimization and consistent performance; Opus/Haiku not needed | config.json: model_profile="budget" |

---
*Last updated: 2026-02-11 (model policy: Sonnet-only for all GSD agents)*
