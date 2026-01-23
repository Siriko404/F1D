# F1D Data Processing Pipeline

## What This Is

A research data processing pipeline that constructs panel datasets for empirical finance research. The pipeline processes earnings call transcripts, links entities across databases, computes text-based measures, merges financial controls, and runs econometric analyses. Built for academic replication and thesis work.

## Core Value

Every script must produce verifiable, reproducible results with complete audit trails — if a reviewer cannot trace how a number was computed, the pipeline has failed.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. Inferred from existing codebase. -->

- ✓ Sample construction from speaker data with entity linking — existing
- ✓ Text tokenization and word counting with dictionary lookups — existing
- ✓ Financial feature construction from CRSP/Compustat — existing
- ✓ Econometric regressions (CEO clarity, liquidity) — existing
- ✓ Configuration-driven execution via project.yaml — existing
- ✓ Timestamped output versioning with latest symlinks — existing
- ✓ Dual logging to console and log files — existing

### Active

<!-- Current scope. Building toward these. -->

- [ ] Comprehensive descriptive statistics in every script (input/process/output)
- [ ] Statistics output to both console and structured files (JSON/CSV)
- [ ] Data quality stats: row counts, missing values, distributions, anomalies
- [ ] Processing metrics: timing, memory usage, throughput, transformation summaries
- [ ] Script-specific stats tailored to each processing step
- [ ] Comprehensive README for academic reviewers
- [ ] Script-by-script documentation in README
- [ ] Pipeline flow diagram (visual)
- [ ] Data sources documentation with setup instructions
- [ ] Sample statistics summary in README

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Shared stats module — stats logic stays inline in each script for self-contained replication
- Aggregate pipeline summary report — per-script stats are sufficient
- Methodology rationale in README — belongs in the paper/thesis, not code docs
- Automated testing framework — verification scripts exist, formal testing deferred
- Mobile/web interface — this is a batch processing pipeline

## Context

This is a thesis research project with an existing 4-stage pipeline:
1. **Sample** (1_Sample): Build sample manifest, clean metadata, link entities, build tenure map
2. **Text** (2_Text): Tokenize transcripts, construct text variables, verify outputs
3. **Financial** (3_Financial): Build financial features, firm controls, market variables, event flags
4. **Econometric** (4_Econometric): Run regressions for CEO clarity, tone, liquidity effects

The pipeline follows strict conventions from CLAUDE.md:
- Root structure: `1_Inputs/`, `2_Scripts/`, `3_Logs/`, `4_Outputs/`, `config/`
- Naming: `<Stage>.<Step>_<PascalCaseName>.py`
- All scripts read from `config/project.yaml`
- Outputs go to timestamped directories with `latest` symlinks

Current gaps identified in codebase mapping:
- No requirements.txt (dependency management)
- Scripts lack comprehensive statistics reporting
- No README documenting the full pipeline

## Constraints

- **Reproducibility**: All outputs must be bitwise-identical for same inputs/config (seed 42, single thread)
- **Self-contained scripts**: Each script must be runnable independently without external orchestration
- **Academic standards**: Documentation must meet journal/thesis replication package requirements
- **Existing structure**: Must preserve current directory layout and naming conventions
- **No mocks**: Real data only; never fabricate test data without explicit approval

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Stats inline per script | Self-contained for replication; reviewers can trace any number | — Pending |
| Stats to console + files | Human review during runs + machine-readable for analysis | — Pending |
| README for academic reviewers | Primary audience is thesis committee and journal reviewers | — Pending |
| Skip methodology in README | Methodology belongs in paper; README covers "how to run" | — Pending |

---
*Last updated: 2026-01-22 after initialization*
