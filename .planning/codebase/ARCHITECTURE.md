# Architecture

**Analysis Date:** 2026-02-20

## Pattern Overview

**Overall:** Multi-stage data processing pipeline with modular variable builders

**Key Characteristics:**
- **Two-tier module structure**: Tier 1 (shared utilities) and Tier 2 (stage-specific modules)
- **One module = one variable**: Each variable builder returns exactly one column
- **Two-stage execution per hypothesis**: Stage 3 builds panels, Stage 4 runs regressions
- **Private compute engines**: Singleton pattern for expensive data loads (Compustat, CRSP)
- **Timestamp-based output versioning**: All outputs go to `YYYY-MM-DD_HHMMSS/` subdirectories

## Layers

**Tier 1: Shared Utilities (`src/f1d/shared/`):**
- Purpose: Cross-cutting utilities used across all pipeline stages
- Location: `src/f1d/shared/`
- Contains: Path utilities, panel OLS, logging, config, observability, variable builders
- Depends on: pandas, numpy, linearmodels, pydantic, yaml
- Used by: All Stage 2, 3, 4 modules

**Tier 2: Stage-Specific Modules:**
- Purpose: Implement individual pipeline stages
- Location: `src/f1d/{sample,text,variables,econometric}/`
- Contains: Executable scripts for each processing step
- Depends on: Tier 1 shared utilities, external data sources
- Used by: CLI invocation via `python -m f1d.<module>`

**Variable Builders Layer (`src/f1d/shared/variables/`):**
- Purpose: Build individual variables from various data sources
- Location: `src/f1d/shared/variables/`
- Contains: Base classes and 50+ individual variable builders
- Pattern: Each builder inherits from `VariableBuilder`, implements `build()` returning `VariableResult`
- Depends on: Compustat engine, CRSP engine, IBES engine, Stage 2 outputs
- Used by: Stage 3 panel builders

## Data Flow

**4-Stage Pipeline Flow:**

1. **Stage 1 - Sample Construction**: Build analyst-CEO manifest
   - Input: Raw earnings call transcripts, CEO tenure data
   - Process: Link entities, filter by call threshold, assemble manifest
   - Output: `outputs/1.4_AssembleManifest/{timestamp}/master_sample_manifest.parquet`

2. **Stage 2 - Text Processing**: Tokenize and analyze conference calls
   - Input: Manifest + raw transcripts
   - Process: Extract filtered docs, tokenize, count words, build linguistic variables
   - Output: `outputs/2_Textual_Analysis/2.2_Variables/{timestamp}/linguistic_variables_{year}.parquet`

3. **Stage 3 - Financial Features**: Build analysis panels
   - Input: Manifest + Stage 2 outputs + Compustat + CRSP + IBES
   - Process: Load variable builders, merge by `file_name`, produce complete panel
   - Output: `outputs/3_Variables/{hypothesis}_panel/{timestamp}/{hypothesis}_panel.parquet`

4. **Stage 4 - Econometric Analysis**: Run panel regressions
   - Input: Stage 3 panel
   - Process: Filter sample, run OLS with fixed effects, generate LaTeX tables
   - Output: `outputs/4_Econometric/{hypothesis}/{timestamp}/`

**Variable Build Flow:**

```python
# Each Stage 3 panel builder follows this pattern:
manifest = load_manifest()
variables = [
    ManifestFieldsBuilder(config),
    CEOQAUncertaintyBuilder(config),
    SizeBuilder(config),
    # ... 10-30 more builders
]
for builder in variables:
    result = builder.build(years, root_path)
    manifest = manifest.merge(result.data, on="file_name")
```

**State Management:**
- No in-memory state between stages
- Each stage reads prior outputs from disk
- Private engines cache loaded data within a single stage execution

## Key Abstractions

**VariableBuilder (`src/f1d/shared/variables/base.py`):**
- Purpose: Base class for all variable builders
- Examples: `src/f1d/shared/variables/size.py`, `src/f1d/shared/variables/ceo_qa_uncertainty.py`
- Pattern: Abstract base class with `build(years, root_path) -> VariableResult`
- Returns: `VariableResult(data=DataFrame, stats=VariableStats, metadata=dict)`

**Private Compute Engines:**
- Purpose: Load expensive datasets once and cache for all builders
- Examples:
  - `src/f1d/shared/variables/_compustat_engine.py` - Compustat quarterly data
  - `src/f1d/shared/variables/_crsp_engine.py` - CRSP daily stock files
  - `src/f1d/shared/variables/_ibes_engine.py` - IBES analyst forecasts
  - `src/f1d/shared/variables/_hassan_engine.py` - Hassan policy risk data
- Pattern: Module-level singleton with `get_engine()` function

**PanelOLS Wrapper (`src/f1d/shared/panel_ols.py`):**
- Purpose: Standardized panel regression with fixed effects
- Features: Entity/time/industry FE, clustered SEs, HAC, VIF diagnostics
- Returns: Dict with `model`, `coefficients`, `summary`, `diagnostics`, `warnings`

**Config System (`src/f1d/shared/config/`):**
- Purpose: Pydantic-based configuration with validation
- Pattern: `ProjectConfig.from_yaml(path)` loads and validates `config/project.yaml`
- Supports: Environment variable overrides via `F1D_*` prefix

## Entry Points

**CLI Entry Points:**
- Location: `src/f1d/{sample,text,variables,econometric}/*.py`
- Triggers: `python -m f1d.<module>.<script>` (e.g., `python -m f1d.variables.build_h1_cash_holdings_panel`)
- Responsibilities: Load config, setup paths, run processing, save outputs

**Module Entry Points (`__init__.py`):**
- `src/f1d/__init__.py`: Re-exports `get_latest_output_dir`, `run_panel_ols`
- `src/f1d/shared/__init__.py`: Re-exports core utilities
- `src/f1d/shared/variables/__init__.py`: Re-exports all 50+ variable builders

**Dry-Run Mode:**
- All scripts support `--dry-run` flag for prerequisite validation
- Tests can use `tests/verification/test_*_dryrun.py` for CI validation

## Error Handling

**Strategy:** Fail-fast with detailed error context

**Patterns:**
- Custom exceptions: `PathValidationError`, `OutputResolutionError`, `CollinearityError`, `MulticollinearityError`
- Validation before processing: `validate_input_file()`, `validate_prerequisites()`
- Comprehensive stats collection: Every script collects `stats` dict with timing, memory, checksums
- Dual logging: `DualWriter` class writes to both stdout and log file

**Error Classes:**
- `src/f1d/shared/path_utils.py`: `PathValidationError`, `OutputResolutionError`
- `src/f1d/shared/panel_ols.py`: `CollinearityError`, `MulticollinearityError`

## Cross-Cutting Concerns

**Logging:** 
- `src/f1d/shared/observability/` - `DualWriter`, throughput tracking, memory monitoring
- Config: `config/project.yaml` logging section
- Output: `logs/{step_id}/{timestamp}.log`

**Validation:**
- Pydantic models for config validation
- `validate_input_file()` for file existence checks
- `check_prerequisites()` for dependency validation
- VIF checks in panel regressions

**Authentication:**
- Not applicable - no external API authentication
- All data is local filesystem-based

**Output Management:**
- Timestamped directories: `outputs/{step_id}/{timestamp}/`
- Resolution: `get_latest_output_dir()` finds most recent valid output
- Stats files: `stats.json` alongside outputs for reproducibility tracking
- Checksums: SHA-256 hashes for all input/output files

---

*Architecture analysis: 2026-02-20*
