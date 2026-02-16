# F1D Data Processing Pipeline

## What This Is

A research data processing pipeline that constructs panel datasets for empirical finance research. The pipeline processes earnings call transcripts, links entities across databases, computes text-based measures (including speech uncertainty), merges financial controls, and runs econometric analyses testing hypotheses about managerial communication and corporate outcomes. Built for academic replication and thesis work.

## Core Value

Every script must produce verifiable, reproducible results with complete audit trails — if a reviewer cannot trace how a number was computed, the pipeline has failed.

## Current Milestone: v6.3 Codebase Concerns Resolution

**Previous:** v6.2 Full-Scale Pipeline Testing (COMPLETE 2026-02-15)
**Current:** v6.3 Codebase Concerns Resolution (COMPLETE 2026-02-15)
**Phases:** 83-90

### v6.3 Deliverables

- **Phase 83:** Critical Tech Debt Fix (global state, silent error handling)
- **Phase 84:** Output Schema Validation (Pandera integration)
- **Phase 85:** V2 Financial Scripts Testing (53 new unit tests)
- **Phase 86:** V1/V2 Econometric Testing Gaps (36 new unit tests)
- **Phase 87:** Merge Validation & Data Loading (safe_merge with validation)
- **Phase 88:** Security & Dependency Infrastructure (Dependabot, SECURITY.md)
- **Phase 89:** Code Organization & Splitting (timestamp validation)
- **Phase 90:** Performance & Quality Gates (Bandit SAST, coverage threshold increase)

### Key Improvements in v6.3

- Eliminated global state in TakeoverHazards.py (parameter injection)
- Fixed silent error handling with specific exceptions + logging
- Added Pandera schema validation for output files
- Created 105 new unit tests (181 total new tests)
- Added safe_merge() with validation and diagnostics
- Configured Dependabot for automated dependency updates
- Added secrets patterns to .gitignore
- Created SECURITY.md with security policy
- Added Bandit SAST to CI pipeline
- Increased test coverage threshold from 25% to 30%

## Requirements

### Validated

<!-- Shipped and confirmed valuable. v1.0-v6.1 milestones complete. -->

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
- ✓ H7-H8 data truncation bug fixed — v3.0
- ✓ Exception-based error handling — v3.0
- ✓ Observability package structure — v3.0
- ✓ Ruff linting and formatting — v3.0
- ✓ Type hints and progressive type checking — v3.0
- ✓ Repository README enhancement — v3.0
- ✓ Script header standardization — v3.0
- ✓ V1/V2/V3 variable catalogs — v3.0
- ✓ Performance optimizations — v3.0
- ✓ Testing and validation infrastructure — v3.0
- ✓ Folder structure consolidated (V3 eliminated) — v4.0
- ✓ ARCHITECTURE_STANDARD.md created — v5.0
- ✓ CODE_QUALITY_STANDARD.md created — v5.0
- ✓ CONFIG_TESTING_STANDARD.md created — v5.0
- ✓ DOC_TOOLING_STANDARD.md created — v5.0
- ✓ src-layout package structure — v6.0
- ✓ Type hints with tier-based mypy enforcement — v6.0
- ✓ pydantic-settings configuration — v6.0
- ✓ Structured logging with structlog — v6.0
- ✓ CI/CD pipeline with ruff, mypy, pytest — v6.0
- ✓ Comprehensive test suite with factory fixtures — v6.0
- ✓ Full src-layout compliance (zero sys.path.insert) — v6.1
- ✓ All imports use f1d.shared.* namespace — v6.1
- ✓ LoggingSettings integrated with configure_logging() — v6.1
- ✓ SDC takeover event linkage (100% CUSIP, 2% match rate) — v6.2
- ✓ Global state eliminated from TakeoverHazards.py — v6.3
- ✓ Silent error handling fixed with specific exceptions — v6.3
- ✓ Output schema validation with Pandera — v6.3
- ✓ 105 new unit tests for financial/econometric scripts — v6.3
- ✓ safe_merge() with validation and logging — v6.3
- ✓ Dependabot configuration for automated updates — v6.3
- ✓ SECURITY.md with security policy — v6.3
- ✓ Secrets patterns in .gitignore — v6.3
- ✓ Bandit SAST in CI pipeline — v6.3
- ✓ Test coverage threshold increased to 30% — v6.3

### Active

<!-- Current scope. Building toward these. Next milestone. -->

(None — ready for next milestone planning)

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
- Adding new features or hypotheses — thesis research complete, now focused on code quality

## Context

This is a thesis research project with an existing 4-stage pipeline:
1. **Sample** (1_Sample): Build sample manifest, clean metadata, link entities, build tenure map
2. **Text** (2_Text): Tokenize transcripts, construct text variables, verify outputs
3. **Financial** (3_Financial): Build financial features, firm controls, market variables, event flags
4. **Econometric** (4_Econometric): Run regressions for CEO clarity, tone, liquidity effects

V2 extensions added:
- **Financial_V2** (3_Financial_V2): Hypothesis-specific variable construction (H1-H3, H5, H6)
- **Econometric_V2** (4_Econometric_V2): Hypothesis testing regressions with FE and clustering

**Current State (v6.3):**
- 58,000+ lines of Python code in src/f1d/
- src-layout package structure with proper f1d.shared.* imports
- Type hints with tier-based mypy enforcement
- Type-safe configuration via pydantic-settings
- Structured logging with structlog and context binding
- CI/CD pipeline with ruff, mypy, pytest, and Bandit SAST
- Comprehensive test suite with factory fixtures
- 700+ tests passing (181 new tests in v6.3)
- Pandera schema validation for output files
- Automated dependency updates via Dependabot

**Standards Documents (v5.0):**
- `docs/ARCHITECTURE_STANDARD.md` (1,696 lines) — Defines src-layout, module tiers, data lifecycle
- `docs/CODE_QUALITY_STANDARD.md` (3,377 lines) — Defines naming, docstrings, type hints, error handling
- `docs/CONFIG_TESTING_STANDARD.md` (3,084 lines) — Defines configuration, logging, testing patterns
- `docs/DOC_TOOLING_STANDARD.md` (2,316 lines) — Defines documentation, CI/CD, linting

## Thesis Research Requirements

**CRITICAL: This is a thesis research pipeline, NOT a general data processing project.**

All econometric scripts and regression outputs MUST generate complete "paper bundles" suitable for academic publication. Agents implementing or modifying regression scripts MUST research and include:

### Required Output Components

1. **Sample Descriptive Statistics**
   - Tailored to each input dataset
   - Summary statistics (N, mean, std, min, max, quartiles)
   - Variable definitions and sources
   - Sample construction flow

2. **Regression Tables in Academic Format**
   - LaTeX vertical style (NOT horizontal)
   - Traditional corporate finance table formatting
   - Standard errors in parentheses below coefficients
   - Significance stars (* p<0.10, ** p<0.05, *** p<0.01)
   - Fixed effects indicators (Yes/No or checkmarks)
   - Observation counts, R-squared values
   - Variable names matching paper notation

3. **Additional Academic Best Practices** (research before implementing)
   - Correlation matrices with significance
   - Variance Inflation Factors (VIF) for multicollinearity
   - First-stage F-statistics for IV/2SLS
   - Economic significance (standardized coefficients)
   - Robustness check summaries
   - Subsample analyses where appropriate

### Agent Responsibilities

When working on ANY regression or econometric code:
1. **Research first**: Look up current best practices for academic table formatting in finance journals
2. **Reference existing standards**: Check SCRIPT_DOCSTANDARD.md and any existing regression outputs
3. **Generate complete bundles**: Never output just coefficients — include all supporting statistics
4. **Format for publication**: Tables should be copy-paste ready for LaTeX manuscripts

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
| Stats inline per script | Self-contained for replication; reviewers can trace any number | ✓ Implemented v1.0 |
| Stats to console + files | Human review during runs + machine-readable for analysis | ✓ Implemented v1.0 |
| README for academic reviewers | Primary audience is thesis committee and journal reviewers | ✓ Implemented v1.0 |
| Skip methodology in README | Methodology belongs in paper; README covers "how to run" | ✓ Implemented v1.0 |
| Cancel robustness phases on null results | Scientifically inappropriate to pursue robustness for unsupported hypotheses | Phases 36-38 cancelled |
| Abandon hypothesis suite discovery | Single hypothesis (H6) tested directly; remaining H7-H10 not pursued | Phase 41 abandoned |
| Document null results | Null findings are valid scientific results; documented in VERIFICATION.md | All phases documented |
| Sonnet-only model policy | Cost optimization and consistent performance; Opus/Haiku not needed | config.json: model_profile="quality" |
| src-layout over flat layout | PyPA recommendation for proper package imports | ✓ Implemented v6.0 |
| V1 and V2 as active variants | Both pipeline versions maintained, no V1 archival | ✓ Implemented v6.0 |
| Google-style docstrings | Enables mkdocstrings API documentation | ✓ Implemented v6.0 |
| Tier-based type hints | 100% Tier 1, 80% Tier 2, optional Tier 3 | ✓ Implemented v6.0 |
| ruff as unified linter/formatter | Replaces flake8 + black + isort | ✓ Implemented v6.0 |
| MkDocs + mkdocstrings | Simpler than Sphinx, Markdown-native | ✓ Decided v5.0 |
| pydantic-settings | Type-safe configuration with env vars | ✓ Implemented v6.0 |
| structlog | Structured JSON logging with context binding | ✓ Implemented v6.0 |
| Installed package imports | All scripts use f1d.shared.* namespace without sys.path manipulation | ✓ Implemented v6.1 |
| TYPE_CHECKING imports | Avoid circular imports at runtime while maintaining type safety | ✓ Implemented v6.1 |

---
*Last updated: 2026-02-15 (v6.3 milestone complete)*
