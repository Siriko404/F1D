# Architecture

**Analysis Date:** 2026-02-14

## Pattern Overview

**Overall:** Multi-stage data processing pipeline with src-layout packaging

**Key Characteristics:**
- Pipeline stages organized by processing domain (Sample, Text, Financial, Econometric)
- Dual location pattern: scripts in `2_Scripts/` and modules in `src/f1d/`
- Timestamped output directories for reproducibility
- Versioned implementations (v1, v2) for hypothesis testing
- Shared cross-cutting utilities in `src/f1d/shared/`

## Layers

**Stage Layer (Pipeline Steps):**
- Purpose: Execute discrete processing steps in sequence
- Location: `src/f1d/{sample,text,financial,econometric}/`
- Contains: Step scripts (e.g., `1.0_BuildSampleManifest.py`, `3.1_H1Variables.py`)
- Depends on: `f1d.shared` utilities, `config/project.yaml`
- Used by: Command-line invocation, orchestrators

**Shared Utilities Layer:**
- Purpose: Cross-cutting concerns used across all stages
- Location: `src/f1d/shared/`
- Contains: Path resolution, logging, validation, regression helpers
- Depends on: pandas, numpy, statsmodels, linearmodels
- Used by: All stage modules

**Configuration Layer:**
- Purpose: Centralized configuration management with type safety
- Location: `src/f1d/shared/config/`
- Contains: Pydantic-based config classes, YAML loading
- Depends on: pydantic, pydantic-settings, pyyaml
- Used by: All modules via `get_config()`

**Observability Layer:**
- Purpose: Logging, statistics, and monitoring
- Location: `src/f1d/shared/observability/`
- Contains: DualWriter, memory tracking, throughput calculation, anomaly detection
- Depends on: Standard library, psutil
- Used by: All stage scripts for logging and stats output

## Data Flow

**Main Pipeline Flow:**

1. **Step 1: Sample Construction** - `1.0_BuildSampleManifest.py` orchestrates:
   - `1.1_CleanMetadata.py` - Deduplicate and filter earnings calls
   - `1.2_LinkEntities.py` - 4-tier CCM linking (GVKEY assignment)
   - `1.3_BuildTenureMap.py` - CEO tenure panel from Execucomp
   - `1.4_AssembleManifest.py` - Join metadata with CEO panel

2. **Step 2: Text Processing** - `2_Text/` processes:
   - `2.1_TokenizeAndCount.py` - Tokenize call transcripts
   - `2.2_ConstructVariables.py` - Compute linguistic measures (Uncertainty, Negative)
   - `2.3_VerifyStep2.py` - Validation and verification

3. **Step 3: Financial Features** - `3_Financial_V2/` computes:
   - `3.1_H1Variables.py` - Cash holdings, leverage
   - `3.2_H2Variables.py` - Investment efficiency variables
   - `3.3_H3Variables.py` - Payout policy variables
   - `3.5_H5Variables.py` through `3.8_H8TakeoverVariables.py` - Hypothesis-specific variables

4. **Step 4: Econometric Analysis** - `4_Econometric_V2/` runs:
   - `4.1_H1CashHoldingsRegression.py` through `4.11_H9_Regression.py`
   - Panel OLS with firm/year fixed effects
   - IV regression support via `shared/iv_regression.py`

**State Management:**
- Each step writes to timestamped subdirectory under `4_Outputs/{step_name}/{timestamp}/`
- `get_latest_output_dir()` resolves most recent output for downstream steps
- `stats.json` captures execution metadata at each step
- Parquet format for all data files (efficient columnar storage)

## Key Abstractions

**Pipeline Step Script:**
- Purpose: Single processing step in the pipeline
- Examples: `src/f1d/sample/1.2_LinkEntities.py`, `src/f1d/financial/v2/3.1_H1Variables.py`
- Pattern:
  ```python
  # Standard header with step ID, description, inputs/outputs
  def load_config() -> Dict[str, Any]: ...
  def setup_paths(config, timestamp) -> Dict[str, Path]: ...
  def main() -> int: ...
  if __name__ == "__main__":
      parse_arguments()
      main()
  ```

**Orchestrator Script:**
- Purpose: Coordinate substeps via subprocess
- Examples: `src/f1d/sample/1.0_BuildSampleManifest.py`
- Pattern:
  ```python
  substeps = [{"id": "1.1", "script": "1.1_CleanMetadata.py"}, ...]
  for step in substeps:
      result = subprocess.run([sys.executable, script_path], ...)
  ```

**DualWriter (Logging):**
- Purpose: Simultaneous stdout and file logging
- Location: `src/f1d/shared/observability/logging.py`
- Pattern:
  ```python
  dual_writer = DualWriter(log_file_path)
  sys.stdout = dual_writer
  # All print() calls go to both terminal and file
  ```

**Path Resolution:**
- Purpose: Find latest outputs across timestamped directories
- Location: `src/f1d/shared/path_utils.py`
- Pattern:
  ```python
  manifest_dir = get_latest_output_dir(
      root / "4_Outputs" / "1.4_AssembleManifest",
      required_file="master_sample_manifest.parquet"
  )
  ```

## Entry Points

**Main Orchestrators:**
- Location: `src/f1d/sample/1.0_BuildSampleManifest.py`
- Triggers: `python -m f1d.sample.1.0_BuildSampleManifest` or direct execution
- Responsibilities: Coordinates 4 substeps for sample construction

**Individual Stage Scripts:**
- Location: `src/f1d/{sample,text,financial,econometric}/*.py`
- Triggers: Direct execution or via orchestrator subprocess
- Responsibilities: Single processing step (e.g., entity linking, variable construction)

**Legacy Scripts (2_Scripts/):**
- Location: `2_Scripts/{1_Sample,2_Text,3_Financial,4_Econometric}/`
- Triggers: Direct execution
- Note: Duplicates of src/f1d/ modules; being migrated to src-layout

## Error Handling

**Strategy:** Fail-fast with detailed context

**Patterns:**
- Custom exceptions with context: `FinancialCalculationError`, `DataValidationError`, `PathValidationError`, `OutputResolutionError`, `MulticollinearityError`
- Validation at entry points: `validate_input_file()`, `validate_output_path()`
- Schema validation: `validate_schema()` in `shared/data_validation.py`
- Subprocess validation: `validate_script_path()` for security (prevents path traversal)

**Exception Hierarchy:**
```
Exception
├── PathValidationError (path_utils.py)
├── OutputResolutionError (path_utils.py)
├── DataValidationError (data_validation.py)
├── FinancialCalculationError (data_validation.py)
├── CollinearityError (panel_ols.py)
└── MulticollinearityError (panel_ols.py)
```

## Cross-Cutting Concerns

**Logging:** DualWriter pattern sends output to both terminal and timestamped log files in `3_Logs/{step_name}/`

**Validation:**
- Input validation via `validate_input_file()` with schema checking
- Output path validation via `validate_output_path()`
- Subprocess script path validation for security

**Configuration:**
- Central YAML file: `config/project.yaml`
- Type-safe access via Pydantic models in `shared/config/`
- Environment variable overrides supported (prefix: `F1D_`)

**Reproducibility:**
- Random seed: 42 (configurable in `determinism.random_seed`)
- Single-threaded processing: `thread_count: 1`
- Timestamped outputs preserve execution history
- Git SHA captured in regression outputs

---

*Architecture analysis: 2026-02-14*
