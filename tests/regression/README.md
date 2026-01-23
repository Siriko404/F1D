# Regression Tests

## Purpose

Regression tests ensure that code changes don't silently alter output data. They compare SHA-256 checksums of output files against baseline checksums.

## Running Regression Tests

```bash
# Run all regression tests
python -m pytest tests/regression/ -v -m regression

# Run specific regression test
python -m pytest tests/regression/test_output_stability.py::test_regression_step1_output_stability -v

# Run all tests except regression (faster)
python -m pytest -m "not regression"
```

## Updating Baselines

When code changes intentionally alter outputs, update the baseline checksums:

1. Run the pipeline scripts to generate new outputs
2. Generate new baseline checksums:
   ```bash
   python tests/regression/generate_baseline_checksums.py
   ```
3. Verify the changes are intentional:
   ```bash
   git diff tests/fixtures/baseline_checksums.json
   ```
4. Commit the updated baseline:
   ```bash
   git add tests/fixtures/baseline_checksums.json
   git commit -m "test(regression): update baseline for [reason]"
   ```

## Missing Baselines

If a regression test skips with "No baseline checksum", it means the baseline checksums haven't been generated yet. Run `python tests/regression/generate_baseline_checksums.py` to create them.

## Intentional Regressions

If a regression test fails but the change is intentional:
1. Review the diff in checksums
2. Verify the output changes are expected
3. Update the baseline checksums (see above)
4. Commit the changes with a clear message explaining the reason

## Checksum Algorithm

Regression tests use SHA-256 checksums computed via pandas:
```python
hashlib.sha256(pd.util.hash_pandas_object(df, index=False).values.tobytes()).hexdigest()
```

This ensures bitwise-identical detection of data changes.

## Tracked Output Files

The following output files are tracked for regression testing:

### Step 1: Sample Construction
- `4_Outputs/1.1_CleanMetadata/latest/cleaned_metadata.parquet`

### Step 2: Text Processing
- `4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_2002.parquet`
- `4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_2003.parquet`
- ... (one per year, 2002-2018)

### Step 3: Financial Features
- `4_Outputs/3_Financial_Features/3.0_BuildFinancialFeatures/latest/financial_features.parquet`

## Baseline Metadata

The `baseline_checksums.json` file includes metadata:

```json
{
  "_metadata": {
    "generated_at": "2026-01-23T14:30:00",
    "git_commit": "abc123...",
    "total_files": 17,
    "missing_files": ["step1_cleaned_metadata", "step3_financial_features"]
  }
}
```

- `generated_at`: When baselines were computed
- `git_commit`: Git commit hash (if available)
- `total_files`: Number of files with baselines
- `missing_files`: Files that don't exist yet (tests will skip these)
