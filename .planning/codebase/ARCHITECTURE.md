# Architecture

**Analysis Date:** 2026-02-12

## Pattern Overview

**Overall:** Stage-based data processing pipeline with numbered scripts organized by processing phase.

**Key Characteristics:**
- Numbered script naming convention (`Stage.Step_Description.py`)
- Timestamp-based output versioning with `latest` symlink
- V1 (legacy) and V2 (current) parallel structures for Financial and Econometric stages
- Shared utilities module for cross-cutting concerns
- Deterministic processing with YAML configuration
- No formal Python package structure (scripts import via sys.path manipulation)

## Layers

**Input Layer:**
- Purpose: Raw data storage (no processing logic)
- Location: `1_Inputs/`
- Contains: Parquet files, CSVs, Excel files from external databases (CRSP, Compustat, IBES, SDC, Execucomp)
- Depends on: External data providers
- Used by: All Stage 1-3 scripts

**Processing Layer:**
- Purpose: Data transformation and analysis
- Location: `2_Scripts/`
- Contains: Processing scripts organized by stage
  - `1_Sample/` - Sample construction (5 scripts)
  - `2_Text/` - Text processing (4 scripts)
  - `3_Financial/` - V1 financial features (5 scripts)
  - `3_Financial_V2/` - V2 hypothesis-specific variables (13 scripts)
  - `4_Econometric/` - V1 econometric analysis (8 scripts)
  - `4_Econometric_V2/` - V2 hypothesis-specific regressions (11 scripts)
- Depends on: `1_Inputs/`, `config/project.yaml`, `2_Scripts/shared/`
- Used by: Downstream processing scripts

**Output Layer:**
- Purpose: Persist processed data and logs
- Location: `4_Outputs/`, `3_Logs/`
- Contains: Timestamped directories with parquet files, JSON stats, MD reports
- Depends on: Processing scripts
- Used by: Downstream scripts, researchers

**Shared Infrastructure Layer:**
- Purpose: Reusable utilities and observability
- Location: `2_Scripts/shared/`
- Contains: 22 utility modules including:
  - `panel_ols.py` - Panel OLS regression with fixed effects
  - `iv_regression.py` - Instrumental variable regression
  - `financial_utils.py` - Financial calculations
  - `path_utils.py` - Output directory resolution
  - `observability_utils.py` - Logging and statistics
  - `observability/` - Sub-package with anomaly detection, memory tracking
- Depends on: External packages (pandas, linearmodels, numpy, statsmodels)
- Used by: All processing scripts

## Data Flow

**Main Pipeline Flow:**

```
1_Inputs/
    |
    v
Stage 1: Sample Construction (1_Sample/)
    1.0_BuildSampleManifest.py [ORCHESTRATOR]
        -> 1.1_CleanMetadata.py
        -> 1.2_LinkEntities.py (4-tier entity matching)
        -> 1.3_BuildTenureMap.py
        -> 1.4_AssembleManifest.py
    |
    v
4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    |
    v
Stage 2: Text Processing (2_Text/)
    2.1_TokenizeAndCount.py (LM dictionary word counts)
    2.2_ConstructVariables.py (linguistic measures)
    2.3_Report.py / 2.3_VerifyStep2.py
    |
    v
4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet
    |
    v
Stage 3: Financial Features (3_Financial/ or 3_Financial_V2/)
    V1: 3.0_BuildFinancialFeatures.py, 3.1_FirmControls.py, 3.2_MarketVariables.py, 3.3_EventFlags.py
    V2: 3.1_H1Variables.py through 3.13_H9_AbnormalInvestment.py
    |
    v
4_Outputs/3_Financial_V2/latest/H*_*.parquet
    |
    v
Stage 4: Econometric Analysis (4_Econometric/ or 4_Econometric_V2/)
    V1: 4.1_EstimateCeoClarity.py, 4.2_LiquidityRegressions.py, 4.3_TakeoverHazards.py
    V2: 4.1_H1CashHoldingsRegression.py through 4.11_H9_Regression.py
    |
    v
4_Outputs/4_Econometric_V2/{script_name}/{timestamp}/results.parquet
```

**State Management:**
- Latest outputs resolved via `get_latest_output_dir()` symlink resolution
- Each run creates new timestamped directory (e.g., `2026-02-11_141310/`)
- `latest` symlink points to most recent successful output
- Checksums computed via SHA-256 for reproducibility verification
- Processing stats saved as `stats.json` alongside outputs

## Key Abstractions

**Script Header Pattern:**
- Purpose: Self-documenting script metadata
- Examples: All scripts in `2_Scripts/`
- Pattern:
  ```python
  #!/usr/bin/env python3
  """
  ==============================================================================
  STEP X.Y: Description
  ==============================================================================
  ID: X.Y_ScriptName
  Description: What the script does

  Inputs:
      - Path to input files

  Outputs:
      - Path to output files

  Deterministic: true
  Dependencies:
      - Requires: Previous steps
      - Uses: External packages

  Author: Thesis Author
  Date: YYYY-MM-DD
  ==============================================================================
  """
  ```

**Timestamped Output Pattern:**
- Purpose: Reproducibility and version control
- Examples: `4_Outputs/1.4_AssembleManifest/2026-02-11_141310/`
- Pattern:
  ```python
  timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
  output_dir = root / "4_Outputs" / script_name / timestamp
  ```

**Path Resolution Pattern:**
- Purpose: Find latest outputs from upstream scripts
- Location: `2_Scripts/shared/path_utils.py`
- Usage:
  ```python
  from shared.path_utils import get_latest_output_dir, OutputResolutionError

  manifest_dir = get_latest_output_dir(
      root / "4_Outputs" / "1.4_AssembleManifest",
      required_file="master_sample_manifest.parquet"
  )
  ```

**Import Fallback Pattern:**
- Purpose: Handle script execution from any directory
- Examples: All scripts using try/except import blocks
- Pattern:
  ```python
  try:
      from shared.path_utils import get_latest_output_dir
  except ImportError:
      import sys as _sys
      from pathlib import Path as _Path
      _script_dir = _Path(__file__).parent.parent
      _sys.path.insert(0, str(_script_dir))
      from shared.path_utils import get_latest_output_dir
  ```

**Panel OLS Regression:**
- Purpose: Standardized panel regression with fixed effects
- Location: `2_Scripts/shared/panel_ols.py`
- Usage:
  ```python
  from shared.panel_ols import run_panel_ols, CollinearityError, MulticollinearityError

  result = run_panel_ols(
      df=panel_df,
      dependent="CashHoldings",
      exog=["Uncertainty", "Leverage", "Uncertainty_x_Leverage"],
      entity_col="gvkey",
      time_col="year",
      industry_col="ff48_code",
      cluster_by_entity=True,
  )
  ```

## Entry Points

**Orchestrator Script:**
- Location: `2_Scripts/1_Sample/1.0_BuildSampleManifest.py`
- Triggers: Manual execution via command line
- Responsibilities: Runs Stage 1 substeps 1.1-1.4 via subprocess

**Individual Scripts:**
- Location: All `*.py` files in `2_Scripts/*/`
- Triggers: Manual execution or via orchestrator
- Responsibilities: Single processing step with defined inputs/outputs

**Validation Script:**
- Location: `2_Scripts/2.0_ValidateV2Structure.py`
- Triggers: Manual or CI/CD
- Responsibilities: Verify pipeline structure, check dependencies

**Test Runner:**
- Location: `tests/` via pytest
- Triggers: `pytest tests/` command
- Responsibilities: Unit, integration, regression tests

**CLI Interface:**
- All scripts accept `--dry-run` flag for validation without execution
- All scripts use `argparse` for argument parsing
- Example:
  ```bash
  python 2_Scripts/1_Sample/1.1_CleanMetadata.py --dry-run
  ```

## Error Handling

**Strategy:** Fail-fast with detailed logging

**Custom Exceptions (in `2_Scripts/shared/`):**
- `OutputResolutionError` (`path_utils.py`) - Cannot resolve output directory
- `CollinearityError` (`panel_ols.py`) - Perfect collinearity in design matrix
- `MulticollinearityError` (`panel_ols.py`, `diagnostics.py`) - VIF threshold exceeded
- `FinancialCalculationError` (`financial_utils.py`) - Invalid financial metric computation

**Patterns:**
- `validate_input_file()` raises `FileNotFoundError` if input missing
- `validate_output_path()` raises `ValueError` if output directory not writable
- All exceptions logged via `DualWriter` to both console and timestamped log file

## Cross-Cutting Concerns

**Logging:**
- Framework: Python `logging` module + custom `DualWriter`
- Location: `2_Scripts/shared/observability_utils.py`, `observability/` sub-package
- Pattern:
  ```python
  from shared.observability_utils import DualWriter
  log_path = log_dir / f"{timestamp}.log"
  sys.stdout = DualWriter(log_path)
  ```

**Validation:**
- Approach: Pre-flight checks before processing
- Location: `2_Scripts/shared/path_utils.py`, `data_validation.py`
- Pattern: `validate_input_file(path, must_exist=True)`

**Configuration:**
- Location: `config/project.yaml`
- Loading:
  ```python
  import yaml
  with open("config/project.yaml") as f:
      config = yaml.safe_load(f)
  ```

**Determinism:**
- Random seed: 42 (configurable in `project.yaml`)
- Single-threaded processing by default (`thread_count: 1`)
- Sorted inputs before processing (`sort_inputs: true`)

**Memory Management:**
- Location: `2_Scripts/shared/chunked_reader.py`
- Pattern: `MemoryAwareThrottler` and `track_memory_usage` decorator
- Configuration: `max_memory_percent: 80.0` in `project.yaml`

**Type Hints:**
- Gradual mypy adoption with stubs for untyped packages
- Stubs location: `2_Scripts/stubs/linearmodels*.pyi`
- Strict mode enabled for `shared.observability.*` modules

## Version Management (V1 vs V2)

**V1 (Legacy):**
- Location: `2_Scripts/3_Financial/`, `2_Scripts/4_Econometric/`
- Status: Functional but superseded
- Contains: Hypothesis-agnostic variable construction
- Scripts: `3.0_BuildFinancialFeatures.py`, `3.1_FirmControls.py`, `3.2_MarketVariables.py`, `3.3_EventFlags.py`

**V2 (Current):**
- Location: `2_Scripts/3_Financial_V2/`, `2_Scripts/4_Econometric_V2/`
- Status: Active development
- Contains: Hypothesis-specific variable scripts (H1-H9)
- Scripts: `3.1_H1Variables.py` through `3.13_H9_AbnormalInvestment.py`
- Regression scripts: `4.1_H1CashHoldingsRegression.py` through `4.11_H9_Regression.py`

**Migration Pattern:**
- V2 scripts named by hypothesis (e.g., `3.1_H1Variables.py`)
- V2 outputs stored in parallel directory structure
- V1 excluded from coverage in `pyproject.toml`: `*/V1*` in omit list

## Testing Infrastructure

**Location:** `tests/`

**Structure:**
```
tests/
├── conftest.py              # Shared fixtures
├── fixtures/                # Test data files
├── unit/                    # Unit tests (test_*.py)
├── integration/             # Integration tests
├── regression/              # Output stability tests
└── performance/             # Performance benchmarks
```

**Key Fixtures (from `conftest.py`):**
- `subprocess_env`: Sets PYTHONPATH for subprocess tests to find shared modules
- `test_data_dir`: Path to `tests/fixtures/`
- `sample_dataframe`: Minimal test DataFrame

**Execution:**
```bash
pytest                              # Run all tests
pytest tests/unit/                  # Unit tests only
pytest -m integration               # Integration tests only
pytest --cov=2_Scripts --cov-report=html  # With coverage
```

## Gaps vs Industry Standard Python Projects

**Missing from Standard Layout:**

1. **No `src/` Package Structure**
   - Current: Flat scripts with sys.path manipulation
   - Standard: `src/f1d/` package with `__init__.py` and proper imports
   - Impact: Requires try/except import fallbacks; no namespace isolation

2. **No `pyproject.toml` Build System**
   - Current: `pyproject.toml` only for tool config (pytest, ruff, mypy)
   - Standard: Build system configuration with `[build-system]`, package metadata
   - Impact: Cannot `pip install -e .`; no version management

3. **No `__init__.py` in Script Directories**
   - Current: `2_Scripts/1_Sample/` etc. have no `__init__.py`
   - Standard: Each directory is a Python package
   - Impact: Cannot import across stages; scripts are isolated

4. **No `setup.py` or `setup.cfg`**
   - Current: No entry points defined
   - Standard: Console scripts for CLI entry points
   - Impact: Cannot run `f1d-run-stage 1` or similar

5. **No Type Stub Generation**
   - Current: Manual stubs in `stubs/` for linearmodels
   - Standard: `py.typed` marker and distributed stubs
   - Impact: Manual maintenance of type stubs

6. **Mixed Output/Data Directories**
   - Current: `4_Outputs/` contains both generated data and results
   - Standard: Separate `data/processed/` and `results/` directories
   - Impact: Difficult to gitignore only generated files

7. **No CI/CD Artifact Publishing**
   - Current: Outputs stay local
   - Standard: Publish to artifact storage (S3, GCS) for reproducibility
   - Impact: No remote backup of processed data

**What Works Well:**

1. **Timestamped Outputs** - Excellent for reproducibility
2. **Shared Utilities** - Good DRY principle application
3. **Script Headers** - Self-documenting with clear I/O contracts
4. **Configuration-Driven** - YAML config for parameters
5. **Comprehensive Testing** - Unit, integration, regression, performance

---

*Architecture analysis: 2026-02-12*
