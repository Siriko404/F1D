# F1D Data Processing Pipeline

## What This Is

A research data processing pipeline that constructs panel datasets for empirical finance research. The pipeline processes earnings call transcripts, links entities across databases, computes text-based measures (including speech uncertainty), merges financial controls, and runs econometric analyses testing hypotheses about managerial communication and corporate outcomes. Built for academic replication and thesis work.

## Core Value

Every script must produce verifiable, reproducible results with complete audit trails — if a reviewer cannot trace how a number was computed, the pipeline has failed.

## Current Milestone: v2.0 Hypothesis Testing Suite

**Goal:** Implement and test three empirical hypotheses linking speech uncertainty to corporate financial outcomes (cash holdings, investment efficiency, payout policy)

**Target features:**
- H1: Speech Uncertainty & Precautionary Cash Holdings (vague managers hoard cash, debt disciplines)
- H2: Speech Uncertainty & Investment Inefficiency (vagueness enables over/underinvestment)
- H3: Speech Uncertainty & Payout Policy Stability (vagueness increases dividend volatility)

## Requirements

### Validated

<!-- Shipped and confirmed valuable. v1.0 milestone complete. -->

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

### Active

<!-- Current scope. Building toward v2.0 hypothesis testing. -->

- [ ] Speech uncertainty measurement using Loughran-McDonald uncertainty dictionary
- [ ] Manager fixed-effect decomposition of vagueness (style vs. situational)
- [ ] Cash holdings regression with leverage interactions (H1)
- [ ] Investment efficiency metrics (over/underinvestment detection, H2)
- [ ] Payout policy stability measures (dividend volatility, flexibility, H3)
- [ ] Panel regression infrastructure with firm/year/industry fixed effects
- [ ] 2SLS instrumentation for endogeneity robustness
- [ ] Subsample analyses (leverage, growth, crisis periods)
- [ ] Publication-ready regression tables

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
*Last updated: 2026-02-04 after v2.0 milestone initialization*
