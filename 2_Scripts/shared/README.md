# Shared Utilities

This directory contains reusable utility modules for the F1D data pipeline.

## Scaling Documentation

For comprehensive information on pipeline scaling limits and improvement paths, see: **[SCALING.md](../SCALING.md)**

**Topics covered:**
- Current dataset size limits and memory requirements
- Phase 15 scaling improvements (parallelization, column pruning, throttling)
- Scaling paths for 2x, 10x, and 100x dataset sizes
- Configuration recommendations for different system capacities
- Bottleneck analysis and improvement priorities
- Memory monitoring and performance debugging
- Troubleshooting OOM errors

**Quick Reference:**
- Memory monitoring: `stats.json > memory_mb`
- Throttling config: `config/project.yaml > chunk_processing`
- Chunked processing: `shared/chunked_reader.py`


## chunked_reader.py

PyArrow-based utilities for memory-efficient processing of large Parquet files.

### When to Use

- **Large files (>100MB)**: When files exceed available RAM
- **Memory-constrained environments**: When processing on limited resources
- **Column selection**: When only a subset of columns is needed
- **Stream processing**: When processing independent row groups

### Current Files (Phase 10)

Current Parquet files in the pipeline:
- `metadata_cleaned.parquet`: 32MB
- `metadata_linked.parquet`: 24MB
- `master_sample_manifest.parquet`: 13MB
- `linguistic_variables_*.parquet`: 2-6MB each (17 files, ~80-100MB total)

These files currently fit in memory for most systems. Chunked processing is
primarily future-proofing for larger datasets.

### API Reference

#### `read_in_chunks(file_path, columns=None, chunk_size=None)`

Read Parquet file in chunks using PyArrow row groups.

```python
from pathlib import Path
from shared.chunked_reader import read_in_chunks

for chunk in read_in_chunks(Path("large_file.parquet"), chunk_size=10000):
    process(chunk)
```

**Parameters:**
- `file_path`: Path to Parquet file
- `columns`: List of columns to read (None = all)
- `chunk_size`: Rows per chunk (None = use row groups)

**Yields:** DataFrame chunks

#### `read_selected_columns(file_path, columns)`

Read only selected columns to reduce memory.

```python
from shared.chunked_reader import read_selected_columns

df = read_selected_columns(
    Path("large_file.parquet"),
    ["col1", "col2", "col3"]
)
```

#### `process_in_chunks(file_path, process_func, columns=None, chunk_size=None, combine_func=None)`

Process file in chunks, combining results.

```python
def count_rows(chunk):
    return len(chunk)

total = process_in_chunks(
    Path("large_file.parquet"),
    count_rows,
    chunk_size=10000
)
```

### Performance Characteristics

| Operation | Memory Impact | Speed Impact | Use Case |
|-----------|---------------|--------------|----------|
| `read_in_chunks()` | O(chunk_size) | ~10% overhead | Large files |
| `read_selected_columns()` | O(rows * selected_cols) | 0% overhead | Few columns needed |
| `process_in_chunks()` | O(chunk_size * result_size) | 10-20% overhead | Streaming/aggregation |

### Determinism

All functions preserve deterministic processing:
- Row groups read in order
- Results combined in order
- Bitwise-identical to full read

### References

- Ref: 10-RESEARCH.md Pattern 5 - PyArrow Dataset API
- PyArrow docs: https://arrow.apache.org/docs/python/dataset.html
- Pandas docs: https://pandas.pydata.org/docs/user_guide/scale.html

---

## data_validation.py

Schema-based validation for input files to catch corrupted or malicious data early.

### When to Use

- **Input validation**: Before processing user-provided files
- **Data quality checks**: Detect corrupted or malformed data
- **Security**: Validate against injection attacks in file formats
- **Pipeline health**: Fail fast on invalid data

### Security Features

- Validates input files against expected schemas before processing
- Checks required columns, column types, and value ranges
- Supports strict mode (raise error) vs non-strict (warn and continue)

### API Reference

#### `validate_dataframe_schema(df, schema_name, file_path, strict=True)`

Validate DataFrame against expected schema.

```python
from shared.data_validation import validate_dataframe_schema

validate_dataframe_schema(
    df,
    "Unified-info.parquet",
    Path("data/Unified-info.parquet"),
    strict=True
)
```

**Parameters:**
- `df`: DataFrame to validate
- `schema_name`: Name of schema to use (key in INPUT_SCHEMAS)
- `file_path`: Path to source file (for error messages)
- `strict`: If True, raise on validation failure; if False, warn and continue

**Raises:** `DataValidationError` if validation fails and strict=True

#### `load_validated_parquet(file_path, schema_name=None, strict=True)`

Load Parquet file with schema validation.

```python
from shared.data_validation import load_validated_parquet

df = load_validated_parquet(
    Path("data/Unified-info.parquet"),
    schema_name="Unified-info.parquet"
)
```

**Returns:** Validated pandas DataFrame

**Raises:** `DataValidationError` if validation fails and strict=True

### Available Schemas

- `Unified-info.parquet`: Validates event metadata (event_type, date, speakers)
- `Loughran-McDonald_MasterDictionary_1993-2024.csv`: Validates sentiment dictionary

### Determinism

Validation is deterministic:
- Same data always produces same validation result
- Schemas defined as constants in module
- No random or time-based checks

---

## regression_utils.py

Fixed effects OLS regression patterns for econometric analysis.

### When to Use

- **Econometric analysis**: Running OLS regressions with firm/CEO fixed effects
- **Clustered standard errors**: Accounting for within-firm correlation
- **Diagnostics extraction**: Extracting R², F-statistic, condition number
- **Fixed effects extraction**: Extracting CEO/firm-level effects

### Dependencies

- `pandas`: Required
- `statsmodels.formula.api`: Optional (raises ImportError if missing)

### API Reference

#### `run_fixed_effects_ols(df, formula, sample_name, cov_type='HC1', cluster_col=None)`

Run fixed effects OLS regression with statsmodels.

```python
from shared.regression_utils import run_fixed_effects_ols

model = run_fixed_effects_ols(
    df,
    "linguistic_uncertainty ~ firm_controls + C(ceo_id)",
    sample_name="Sample A",
    cov_type="HC1",
    cluster_col="gvkey"
)
```

**Parameters:**
- `df`: DataFrame with regression data
- `formula`: R-style formula (e.g., "y ~ x1 + x2")
- `sample_name`: Name of sample for logging
- `cov_type`: Covariance type (HC1, cluster, etc.)
- `cluster_col`: Column to cluster standard errors (if cov_type='cluster')

**Returns:** Fitted statsmodels OLS model

#### `extract_ceo_fixed_effects(model, ceo_col='ceo_id')`

Extract CEO fixed effects from fitted model.

```python
from shared.regression_utils import extract_ceo_fixed_effects

ceo_effects = extract_ceo_fixed_effects(model, ceo_col="ceo_id")
# Returns Series indexed by CEO ID
```

**Returns:** Series of CEO fixed effects indexed by CEO ID

#### `extract_regression_diagnostics(model)`

Extract common regression diagnostics from fitted model.

```python
from shared.regression_utils import extract_regression_diagnostics

diagnostics = extract_regression_diagnostics(model)
# Returns: {n_obs, rsquared, rsquared_adj, f_statistic, aic, bic, condno}
```

**Returns:** Dictionary with regression diagnostics

### Determinism

All functions are deterministic:
- statsmodels OLS produces identical results for same data and formula
- Diagnostics extracted deterministically from fitted model
- Graceful error handling for missing dependencies
---

## regression_validation.py

Regression input validation to catch data issues before model estimation.

### When to Use

- **Input validation**: Validate regression inputs before running models
- **Data quality checks**: Detect missing columns, type mismatches, missing values
- **Sample size validation**: Ensure sufficient observations for regression
- **Multicollinearity detection**: Check for high VIF in independent variables
- **Fail fast**: Catch issues early with clear error messages

### Security Features

- Validates regression inputs before model estimation
- Catches missing columns, type mismatches, and missing values
- Provides clear error messages for debugging
- Checks sample size and multicollinearity

### API Reference

#### `validate_columns(df, required_columns, optional_columns=None)`

Validate that all required columns exist in DataFrame.

```python
from shared.regression_validation import validate_columns

validate_columns(
    df,
    required_columns=['gvkey', 'year', 'ceo_id'],
    optional_columns=['returns', 'market_cap']
)
```

**Parameters:**
- `df`: DataFrame to validate
- `required_columns`: List of columns that must exist
- `optional_columns`: List of columns that may exist (for validation only)

**Raises:** `RegressionValidationError` if required columns missing

#### `validate_data_types(df, type_requirements)`

Validate DataFrame columns have expected data types.

```python
from shared.regression_validation import validate_data_types

validate_data_types(
    df,
    type_requirements={
        'year': 'int',
        'ceo_id': 'int',
        'returns': 'float'
    }
)
```

**Parameters:**
- `df`: DataFrame to validate
- `type_requirements`: Dict mapping column name to expected type (int, float, str, bool)

**Raises:** `RegressionValidationError` if columns have unexpected types

#### `validate_no_missing_independent(df, independent_vars, allow_na_ratio=0.0)`

Validate independent variables have no missing values (or within threshold).

```python
from shared.regression_validation import validate_no_missing_independent

validate_no_missing_independent(
    df,
    independent_vars=['size', 'leverage', 'profitability'],
    allow_na_ratio=0.0  # No missing allowed
)
```

**Parameters:**
- `df`: DataFrame to validate
- `independent_vars`: List of independent variable column names
- `allow_na_ratio`: Maximum ratio of missing values allowed (0.0 = none allowed)

**Raises:** `RegressionValidationError` if missing values exceed threshold

#### `validate_regression_data(df, formula, required_columns=None, type_requirements=None, allow_na_independent=0.0)`

Comprehensive validation of regression data before model estimation.

```python
from shared.regression_validation import validate_regression_data

validate_regression_data(
    df,
    formula="linguistic_uncertainty ~ firm_controls + C(ceo_id)",
    required_columns=['gvkey', 'year'],
    allow_na_independent=0.0
)
```

**Parameters:**
- `df`: DataFrame to validate
- `formula`: Regression formula (for parsing variable names)
- `required_columns`: List of columns that must exist
- `type_requirements`: Dict mapping column names to expected types
- `allow_na_independent`: Max missing ratio for independent variables

**Returns:** Validated DataFrame

**Raises:** `RegressionValidationError` if validation fails

**Note:** Parses formula to extract dependent and independent variables.

#### `validate_sample_size(df, min_observations=30)`

Validate DataFrame has minimum number of observations for regression.

```python
from shared.regression_validation import validate_sample_size

validate_sample_size(df, min_observations=50)
```

**Parameters:**
- `df`: DataFrame to validate
- `min_observations`: Minimum number of observations required

**Raises:** `RegressionValidationError` if sample size insufficient

#### `check_multicollinearity(df, independent_vars, vif_threshold=10.0)`

Check for multicollinearity using VIF (Variance Inflation Factor).

```python
from shared.regression_validation import check_multicollinearity

vif_dict = check_multicollinearity(
    df,
    independent_vars=['size', 'leverage', 'profitability'],
    vif_threshold=10.0
)
```

**Parameters:**
- `df`: DataFrame with independent variables
- `independent_vars`: List of independent variable names
- `vif_threshold`: VIF threshold for warning

**Returns:** Dict mapping variable names to VIF values

**Warning:** Logs warning if any variable has VIF > vif_threshold

### Dependencies

- `pandas`: Required
- `numpy`: Required
- `statsmodels`: Optional (raises ImportError if missing, skips VIF check)

### Determinism

All functions are deterministic:
- Same data always produces same validation result
- Type checks are consistent
- Missing value thresholds are exact

---

## financial_utils.py

Financial metrics and control variable calculations from Compustat data.

### When to Use

- **Firm controls**: Calculate standard control variables (size, leverage, profitability)
- **Feature engineering**: Create financial features for regression
- **Missing data handling**: Graceful NaN handling for incomplete Compustat data
- **Panel data**: Compute features for all firms in dataset

### Calculated Variables

- **Size**: log(total assets)
- **Leverage**: total debt / total assets
- **Profitability**: operating income / total assets
- **Market-to-book**: market cap / book equity
- **Capex intensity**: capex / total assets
- **R&D intensity**: R&D / total assets
- **Dividend payer**: indicator (1 if pays dividends, 0 otherwise)

### API Reference

#### `calculate_firm_controls(row, compustat_df, year)`

Calculate firm-level control variables from Compustat data.

```python
from shared.financial_utils import calculate_firm_controls

controls = calculate_firm_controls(
    row,  # DataFrame row with gvkey, datadate
    compustat_df,  # Compustat data
    year=2020
)
# Returns: {size, leverage, profitability, market_to_book, ...}
```

**Returns:** Dictionary with firm-level control variables

#### `compute_financial_features(df, compustat_df)`

Compute financial features for all firms in dataset.

```python
from shared.financial_utils import compute_financial_features

df_with_features = compute_financial_features(df, compustat_df)
```

**Returns:** DataFrame with added financial control variables

### Determinism

All functions are deterministic:
- Same Compustat data produces identical control values
- NaN handling is consistent (np.nan for missing data)
- No random operations or external state

---

## reporting_utils.py

Markdown report generation and diagnostic saving for regression results.

### When to Use

- **Human-readable reports**: Generate markdown summaries of regression results
- **Machine-readable outputs**: Save diagnostics as CSV for analysis
- **Variable documentation**: Track variables used in regression
- **Result archiving**: Save regression outputs for reproducibility

### API Reference

#### `generate_regression_report(model, sample_name, output_dir, formula=None)`

Generate markdown report for regression results.

```python
from shared.reporting_utils import generate_regression_report
from pathlib import Path

report_path = generate_regression_report(
    model,
    sample_name="Sample A",
    output_dir=Path("4_Outputs/4.1.1_FinancialControls"),
    formula="linguistic_uncertainty ~ firm_controls"
)
```

**Returns:** Path to generated markdown report

**Report contents:**
- Sample name and formula
- Model summary (R², F-statistic, etc.)
- Coefficient table with standard errors, t-stats, p-values

#### `save_model_diagnostics(model, sample_name, output_dir)`

Save regression diagnostics to CSV.

```python
from shared.reporting_utils import save_model_diagnostics

diag_path = save_model_diagnostics(
    model,
    sample_name="Sample A",
    output_dir=Path("4_Outputs/4.1.1_FinancialControls")
)
```

**Returns:** Path to saved diagnostics CSV

**Diagnostics saved:**
- sample, n_obs, rsquared, rsquared_adj
- f_statistic, aic, bic, condno

#### `save_variable_reference(df, sample_name, output_dir)`

Save variable reference table (name, dtype, non_null_count).

```python
from shared.reporting_utils import save_variable_reference

ref_path = save_variable_reference(
    df,
    sample_name="Sample A",
    output_dir=Path("4_Outputs/4.1.1_FinancialControls")
)
```

**Returns:** Path to saved variable reference CSV

**Reference includes:**
- variable, dtype, non_null_count, null_count

### Determinism

All functions are deterministic:
- Same model produces identical markdown report
- Diagnostics extracted consistently from fitted model
- CSV files saved in reproducible format

---

## path_utils.py

Path validation and directory creation helpers using pathlib.

### When to Use

- **Path validation**: Verify directories exist and are writable
- **Directory creation**: Create output directories with parents
- **Input validation**: Verify input files exist and are files
- **Disk space checking**: Check available disk space before large writes

### API Reference

#### `validate_output_path(path, must_exist=False, must_be_writable=True)`

Validate output path exists and is accessible.

```python
from shared.path_utils import validate_output_path
from pathlib import Path

validated_path = validate_output_path(
    Path("4_Outputs/step1"),
    must_exist=False,
    must_be_writable=True
)
```

**Parameters:**
- `path`: Path to validate
- `must_exist`: If True, raise error if path doesn't exist
- `must_be_writable`: If True, check path is writable

**Returns:** Validated Path object (resolved to absolute)

**Raises:** `PathValidationError` if validation fails

#### `ensure_output_dir(path)`

Ensure output directory exists, creating if necessary.

```python
from shared.path_utils import ensure_output_dir

resolved_path = ensure_output_dir(
    Path("4_Outputs/step1/timestamp")
)
```

**Returns:** Resolved Path object (absolute)

#### `validate_input_file(path, must_exist=True)`

Validate input file exists and is readable.

```python
from shared.path_utils import validate_input_file

validated_file = validate_input_file(
    Path("inputs/data.parquet"),
    must_exist=True
)
```

**Returns:** Validated Path object (resolved to absolute)

#### `get_available_disk_space(path)`

Get available disk space in GB for a given path.

```python
from shared.path_utils import get_available_disk_space

free_gb = get_available_disk_space(Path("4_Outputs"))
print(f"Available: {free_gb:.2f} GB")
```

**Returns:** Available disk space in GB (float)

### Determinism

All functions are deterministic:
- Path resolution is deterministic (absolute paths)
- Write test files for validation are temporary and cleaned up
- Disk space queries reflect current system state (external factor)

### Cross-Platform Compatibility

Uses `pathlib.Path` for cross-platform path handling:
- Works on Windows, macOS, Linux
- Handles different path separators automatically
- Resolves symlinks and relative paths

---

## symlink_utils.py

Cross-platform symlink and junction creation for 'latest' output links.

### When to Use

- **Latest links**: Create 'latest' symlinks to most recent output directory
- **Cross-platform**: Works on Unix (symlinks) and Windows (junctions)
- **Fallback handling**: Copies directory if link creation unavailable
- **Output organization**: Maintain stable 'latest/' reference for consumers

### Cross-Platform Behavior

| Platform | Primary Method | Fallback 1 | Fallback 2 |
|----------|---------------|------------|------------|
| Unix | symlink | - | - |
| Windows (admin) | symlink | junction | copy |
| Windows (no admin) | - | junction | copy |

### API Reference

#### `update_latest_link(target_dir, link_path, verbose=True)`

Update 'latest' link using symlink or junction.

```python
from shared.symlink_utils import update_latest_link
from pathlib import Path

update_latest_link(
    target_dir=Path("4_Outputs/step1/2026-01-23_120000"),
    link_path=Path("4_Outputs/step1/latest"),
    verbose=True
)
```

**Parameters:**
- `target_dir`: Directory to link to
- `link_path`: Path where link should be created (e.g., 'latest')
- `verbose`: If True, log warnings and status

**Raises:** `SymlinkError` if all fallback methods fail

**Behavior:**
- On Unix: creates symlink
- On Windows: tries symlink (admin required), then junction, then copy
- Removes existing link if present
- Logs warnings when using fallback methods

#### `create_junction(target, link_path)`

Create a Windows junction (directory link).

```python
from shared.symlink_utils import create_junction

create_junction(
    target=Path("4_Outputs/step1/2026-01-23_120000"),
    link_path=Path("4_Outputs/step1/latest")
)
```

**Raises:**
- `OSError`: If junction creation fails
- `NotImplementedError`: If not on Windows

#### `is_junction(path)`

Check if path is a Windows junction.

```python
from shared.symlink_utils import is_junction

if is_junction(Path("4_Outputs/step1/latest")):
    print("Path is a Windows junction")
```

**Returns:** True if path is a junction, False otherwise

**Note:** Uses `Path.is_junction()` on Python 3.12+, fallback for older versions

### Dependencies

- `shared.path_utils.ensure_output_dir`: Validates target directory exists
- `pathlib.Path`: Cross-platform path operations
- `ctypes`: Windows junction detection (Python <3.12 fallback)

### Determinism

Functions are deterministic:
- Same inputs produce same outputs
- Fallback behavior is deterministic (symlink → junction → copy)
- Copy operation preserves file contents identically

### Windows Permissions

- **Symlinks**: Require admin privileges or developer mode
- **Junctions**: Work without admin (directories only)
- **Copy**: Works everywhere, uses more disk space

### Security

- Validates target directory exists before creating links
- Uses absolute resolved paths (no relative path vulnerabilities)
- Removes existing links cleanly (handles junctions, directories, files)

---

## string_matching.py

Config-driven fuzzy name matching using RapidFuzz library.

### When to Use

- **Entity linking**: Match company names across different datasets
- **Fuzzy matching**: Find approximate matches when exact matching fails
- **Config-driven**: Thresholds and scoring methods from config/project.yaml
- **Many-to-many**: Efficiently match multiple queries to multiple targets

### Dependencies

- `yaml`: Required (config loading)
- `rapidfuzz`: Required (fuzzy matching, optional with graceful degradation)

### API Reference

#### `load_matching_config()`

Load string matching configuration from config/project.yaml.

```python
from shared.string_matching import load_matching_config

config = load_matching_config()
# Returns: {'company_name': {'default_threshold': 92.0, ...}, ...}
```

**Returns:** Dict with string matching settings (or empty dict if config missing)

**Raises:**
- `FileNotFoundError`: If config/project.yaml not found
- `yaml.YAMLError`: If config file is invalid YAML

#### `get_scorer(name)`

Get RapidFuzz scorer function by name.

```python
from shared.string_matching import get_scorer

scorer = get_scorer('token_sort_ratio')
# Returns: fuzz.token_sort_ratio function
```

**Parameters:**
- `name`: Scorer name (ratio, partial_ratio, token_sort_ratio, token_set_ratio, WRatio, QRatio)

**Returns:** Scorer function from rapidfuzz.fuzz

**Raises:**
- `ValueError`: If scorer name unknown
- `ImportError`: If RapidFuzz not available

#### `match_company_names(query, candidates, threshold=None, scorer_name='WRatio', preprocess=True)`

Find best matching company name using RapidFuzz.

```python
from shared.string_matching import match_company_names

best_match, score = match_company_names(
    query="Apple Inc.",
    candidates=["Apple", "Microsoft", "Google"],
    threshold=92.0,
    scorer_name='token_sort_ratio'
)
# Returns: ('Apple', 100.0) if score >= threshold
```

**Parameters:**
- `query`: Company name to search for
- `candidates`: List of candidate company names
- `threshold`: Minimum similarity score (0-100). If None, uses config default.
- `scorer_name`: Scorer to use (default: WRatio)
- `preprocess`: If True, apply default preprocessing

**Returns:** (best_match, score) tuple. If no match above threshold, returns (query, 0.0)

**Note:** WRatio provides weighted ratio combining multiple metrics. Works well for company names with word order variations.

#### `match_many_to_many(queries, targets, threshold=None, scorer_name='WRatio', preprocess=True)`

Match multiple queries against targets using RapidFuzz.

This is significantly faster than nested loops for large datasets.

```python
from shared.string_matching import match_many_to_many

results = match_many_to_many(
    queries=["Apple Inc.", "Microsoft Corp."],
    targets=["Apple", "Microsoft", "Google", "Amazon"],
    threshold=92.0
)
# Returns: [('Apple Inc.', 'Apple', 100.0), ('Microsoft Corp.', 'Microsoft', 100.0)]
```

**Parameters:**
- `queries`: List of query strings
- `targets`: List of target strings
- `threshold`: Minimum similarity score (0-100)
- `scorer_name`: Scorer to use
- `preprocess`: If True, apply default preprocessing

**Returns:** List of (query, target, score) tuples for matches above threshold

**Note:** Uses process.cdist for efficient many-to-many matching. Falls back to extractOne if cdist fails.

#### `_match_many_to_many_fallback(queries, targets, targets_processed, threshold, scorer, preprocess)`

Fallback method for many-to-many matching (slower but more robust).

**Parameters:**
- `queries`: List of query strings
- `targets`: List of target strings (original, not processed)
- `targets_processed`: List of target strings (processed for matching)
- `threshold`: Minimum similarity score
- `scorer`: Scorer function
- `preprocess`: If preprocessing was applied

**Returns:** List of (query, target, score) tuples for matches above threshold

**Note:** Internal helper function used when process.cdist fails.

### Configuration

Matching thresholds and scoring methods are configurable in `config/project.yaml`:

```yaml
string_matching:
  company_name:
    default_threshold: 92.0
    min_threshold: 85.0
    scorer: "token_sort_ratio"
    preprocess: true
  entity_name:
    default_threshold: 85.0
    min_threshold: 80.0
    scorer: "WRatio"
    preprocess: true
```

**Settings:**
- `default_threshold`: Minimum similarity score to accept match (0-100)
- `min_threshold`: Lowest acceptable score for edge cases
- `scorer`: RapidFuzz scoring algorithm
- `preprocess`: If True, apply default preprocessing (lowercase, remove special chars)

### Available Scorers

| Scorer | Description | Use Case |
|--------|-------------|----------|
| `ratio` | Simple string similarity | Exact-ish matches |
| `partial_ratio` | Best partial match | Substrings |
| `token_sort_ratio` | Token order insensitive | Word order variations |
| `token_set_ratio` | Token subset insensitive | Partial word matches |
| `WRatio` | Weighted ratio | General purpose (default) |
| `QRatio` | Quick ratio | Fast general matching |

### Determinism

All functions are deterministic:
- Same inputs produce identical match results
- Config loading is deterministic (same config produces same thresholds)
- Scoring algorithms are deterministic (no randomness)
- Graceful degradation for missing dependencies

### Cross-Platform Compatibility

- Config path resolution uses module-relative paths (works from any working directory)
- YAML parsing is consistent across platforms
- RapidFuzz is cross-platform (works on Windows, macOS, Linux)

---

## Utility Functions

The following utility functions are available across shared modules for logging, statistics tracking, and data analysis.

### Logging and Output
**Module:** `shared.observability_utils`

#### `DualWriter`

Class for dual-write logging (outputs to both stdout and log file).

```python
from shared.observability_utils import DualWriter

# Initialize with log file path
dw = DualWriter("path/to/log.txt")
dw.write("Processing started\n")
dw.write(f"Processed {n} rows\n")

# Context manager usage
with DualWriter("path/to/log.txt") as dw:
    dw.write("Processing started\n")
    # ... processing ...
```

**Features:**
- Simultaneously writes to stdout and log file
- Context manager support (automatic file closing)
- Ensures log file directory exists before writing
- Preserves exact formatting between console and log

#### `compute_file_checksum(filepath, algorithm="sha256")`

Compute file checksum for reproducibility verification.

```python
from shared.observability_utils import compute_file_checksum

checksum = compute_file_checksum("output.parquet")
# Returns: "a3f5c9..." (SHA-256 hex digest)
```

**Parameters:**
- `filepath`: Path to file to checksum
- `algorithm`: Hash algorithm to use (default: "sha256", supports any hashlib algorithm)

**Returns:** Hexadecimal digest string

#### `print_stat(label, before=None, after=None, value=None, indent=2)`

Print formatted statistics with optional before/after values.

```python
from shared.observability_utils import print_stat

print_stat("Rows processed", value=1000)
# Output: "Rows processed: 1,000"

print_stat("Memory usage", before=100, after=250)
# Output: "Memory usage: 100 → 250 (+150)"
```

**Parameters:**
- `label`: Description of the statistic
- `before`: Initial value (optional)
- `after`: Final value (optional)
- `value`: Single value to display (optional)
- `indent`: Number of spaces to indent (default: 2)

**Behavior:**
- If `value` provided: displays single value with thousands separator
- If `before` and `after` provided: displays change with delta
- Numbers formatted with commas for readability

#### `print_stats_summary(stats)`

Print formatted summary table from statistics dictionary.

```python
from shared.observability_utils import print_stats_summary

stats = {
    "input_rows": 10000,
    "output_rows": 8500,
    "duration_seconds": 2.5
}
print_stats_summary(stats)
# Prints formatted table with all stats
```

**Parameters:**
- `stats`: Dictionary of statistic names and values

#### `save_stats(stats, out_dir)`

Save statistics dictionary to JSON file.

```python
from shared.observability_utils import save_stats
from pathlib import Path

stats = {"n": 1000, "mean": 42.5}
save_stats(stats, Path("4_Outputs/step1/2026-01-23_120000"))
# Creates: 4_Outputs/step1/2026-01-23_120000/stats.json
```

**Parameters:**
- `stats`: Dictionary of statistics to save
- `out_dir`: Output directory path

**Output:** Creates `stats.json` in specified directory with timestamped metadata

### Data Analysis
**Module:** `shared.observability_utils`

#### `analyze_missing_values(df)`

Analyze missing values per column in DataFrame.

```python
from shared.observability_utils import analyze_missing_values

missing = analyze_missing_values(df)
# Returns: {"col1": {"count": 10, "percent": 0.01}, ...}
```

**Returns:** Dictionary mapping column names to missing count and percentage

**Output format:**
```python
{
    "column_name": {
        "count": 42,
        "percent": 0.042  # 4.2% missing
    }
}
```

#### `get_process_memory_mb()`

Get current process memory usage in megabytes.

```python
from shared.observability_utils import get_process_memory_mb

memory = get_process_memory_mb()
# Returns: {"rss_mb": 125.3, "vms_mb": 450.2, "percent": 6.2}
```

**Returns:** Dictionary with:
- `rss_mb`: Resident Set Size (actual RAM used)
- `vms_mb`: Virtual Memory Size (total memory allocated)
- `percent`: Percentage of system RAM used

#### `calculate_throughput(rows_processed, duration_seconds)`

Calculate rows/second throughput.

```python
from shared.observability_utils import calculate_throughput

throughput = calculate_throughput(10000, 5.0)
# Returns: 2000.0 (rows per second)
```

**Parameters:**
- `rows_processed`: Number of rows processed
- `duration_seconds`: Time elapsed in seconds

**Returns:** Rows per second (float)

#### `detect_anomalies_zscore(df, columns, threshold=3.0)`

Detect outliers using z-score method.

```python
from shared.observability_utils import detect_anomalies_zscore

anomalies = detect_anomalies_zscore(df, columns=['returns', 'volume'])
# Returns: {"returns": [index_list], "volume": [index_list]}
```

**Parameters:**
- `df`: DataFrame to analyze
- `columns`: List of column names to check
- `threshold`: Z-score threshold (default: 3.0 = 3 standard deviations)

**Returns:** Dictionary mapping column names to lists of anomalous row indices

**Method:** Values beyond `threshold * std_dev` from mean are flagged

#### `detect_anomalies_iqr(df, columns, multiplier=3.0)`

Detect outliers using IQR (Interquartile Range) method.

```python
from shared.observability_utils import detect_anomalies_iqr

anomalies = detect_anomalies_iqr(df, columns=['returns', 'volume'])
# Returns: {"returns": [index_list], "volume": [index_list]}
```

**Parameters:**
- `df`: DataFrame to analyze
- `columns`: List of column names to check
- `multiplier`: IQR multiplier (default: 3.0)

**Returns:** Dictionary mapping column names to lists of anomalous row indices

**Method:** Values outside `[Q1 - multiplier*IQR, Q3 + multiplier*IQR]` are flagged

### Symlink and Link Management
**Module:** `shared.symlink_utils`

#### `update_latest_link(target_dir, link_path, verbose=True)`

Update 'latest' symlink/junction to point to most recent output directory.

```python
from shared.symlink_utils import update_latest_link
from pathlib import Path

update_latest_link(
    target_dir=Path("4_Outputs/step1/2026-01-23_120000"),
    link_path=Path("4_Outputs/step1/latest"),
    verbose=True
)
```

**Parameters:**
- `target_dir`: Directory to link to
- `link_path`: Path where link should be created (e.g., 'latest')
- `verbose`: If True, log warnings and status messages

**Cross-platform behavior:**
- **Unix**: Creates symbolic link
- **Windows (admin)**: Tries symlink, then junction, then copy
- **Windows (no admin)**: Tries junction, then copy
- Falls back gracefully if primary method unavailable

**See full documentation:** [symlink_utils.py](#symlink_utilspy) section below

### Usage Example

```python
#!/usr/bin/env python3
"""Example script using utility functions."""
from pathlib import Path
from shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
    print_stat,
    analyze_missing_values,
    get_process_memory_mb,
)
from shared.symlink_utils import update_latest_link

# Set up dual-write logging
output_dir = Path("4_Outputs/my_step/2026-01-23_120000")
with DualWriter(output_dir / "process.log") as dw:
    dw.write("Processing started\n")

    # Compute checksum for reproducibility
    checksum = compute_file_checksum("data.parquet")
    dw.write(f"Data checksum: {checksum}\n")

    # Print statistics with formatting
    print_stat("Rows processed", value=1000)
    print_stat("Memory usage (MB)", value=get_process_memory_mb()["rss_mb"])

    # Analyze missing data
    missing = analyze_missing_values(df)
    dw.write(f"Missing values: {missing}\n")

    # Update latest symlink
    update_latest_link(output_dir, output_dir.parent / "latest")
```

### Module Reference Summary

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `shared.observability_utils` | Core statistics and logging utilities | `DualWriter`, `compute_file_checksum`, `print_stat`, `analyze_missing_values`, `get_process_memory_mb` |
| `shared.symlink_utils` | Cross-platform symlink/junction management | `update_latest_link`, `create_junction`, `is_junction` |
| `shared.path_utils` | Path validation and directory creation | `validate_output_path`, `ensure_output_dir`, `validate_input_file` |
| `shared.data_validation` | Input data validation layers | `validate_dataframe_schema`, `load_validated_parquet` |

---

## Module Usage Example

```python
#!/usr/bin/env python3
"""
Example script using shared utilities.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Path validation
from shared.path_utils import ensure_output_dir, validate_input_file

output_dir = ensure_output_dir(Path("4_Outputs/my_step/latest"))
input_file = validate_input_file(Path("inputs/data.parquet"))

# Chunked reading
from shared.chunked_reader import read_in_chunks

for chunk in read_in_chunks(input_file, chunk_size=10000):
    process(chunk)

# Data validation
from shared.data_validation import validate_dataframe_schema

df = pd.read_parquet(input_file)
validate_dataframe_schema(df, "schema_name", input_file)

# Regression analysis
from shared.regression_utils import run_fixed_effects_ols

model = run_fixed_effects_ols(df, "y ~ x1 + x2", "Sample A")

# Reporting
from shared.reporting_utils import generate_regression_report

report = generate_regression_report(model, "Sample A", output_dir)

# Update latest link
from shared.symlink_utils import update_latest_link

update_latest_link(
    output_dir.parent / "2026-01-23_120000",
    output_dir
)
```

---

## Design Principles

All shared modules follow these principles:

1. **Deterministic**: Same inputs produce identical outputs (no random state)
2. **Type hints**: All function signatures have type annotations
3. **Comprehensive docs**: Docstrings with Args, Returns, Raises sections
4. **Error handling**: Custom exception classes, graceful degradation
5. **Cross-platform**: Works on Windows, macOS, Linux
6. **Minimal dependencies**: Prefer standard library over external packages
7. **Copy-paste ready**: Functions can be inlined without complex setup
8. **Contract headers**: Each module has ID, Description, Inputs, Outputs, Deterministic

---

## Adding New Modules

When adding new shared utilities:

1. Follow contract header pattern (ID, Description, Inputs, Outputs, Deterministic)
2. Add type hints to all functions
3. Include comprehensive docstrings
4. Create custom exception classes if needed
5. Prefer standard library over external dependencies
6. Add unit tests in `tests/test_shared/`
7. Update this README with module documentation

Example module header:

```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: [Module Name]
================================================================================
ID: shared/[module_name]
Description: [One-line description]

Inputs:
    - [Input 1]
    - [Input 2]

Outputs:
    - [Output 1]
    - [Output 2]

Deterministic: true
================================================================================
"""
```
