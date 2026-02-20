# Regression Tests

## Purpose

Regression tests ensure that refactoring changes don't silently alter output data. They compare SHA-256 checksums of output files against baseline checksums.

## Running Regression Tests

```bash
# Run all regression tests
python -m pytest tests/regression/ -v -m regression

# Run specific regression test
python -m pytest tests/regression/test_output_stability.py::test_regression_stage3_panels -v

# Run all tests except regression (faster)
python -m pytest -m "not regression"
```

## Updating Baselines

When code changes intentionally alter outputs (e.g. fixing a bug or adding a control), update the baseline checksums:

1. Run the pipeline scripts to generate new outputs:
   ```bash
   python -m f1d.variables.build_manager_clarity_panel
   python -m f1d.variables.build_ceo_clarity_panel
   # ... run all scripts that should change ...
   ```
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

If a regression test skips with "No baseline checksum", it means the baseline checksums haven't been generated yet for the current output state. Run `python tests/regression/generate_baseline_checksums.py` to create them.

## Intentional Regressions

If a regression test fails but the change is intentional:
1. Review the diff in checksums
2. Verify the output changes are expected (e.g., verifying `clarity_scores.parquet` now correctly excludes the reference entity)
3. Update the baseline checksums (see above)
4. Commit the changes with a clear message explaining the reason

## Checksum Algorithm

Regression tests use SHA-256 checksums computed via pandas. This ensures bitwise-identical detection of data changes without being sensitive to filesystem metadata:
```python
hashlib.sha256(pd.util.hash_pandas_object(df, index=False).values.tobytes()).hexdigest()
```

## Tracked Output Files

The following output files are tracked for regression testing. The test uses `get_latest_output_dir()` to always test the most recent run.

### Stage 3: Panels
- `outputs/variables/manager_clarity/latest/manager_clarity_panel.parquet`
- `outputs/variables/ceo_clarity/latest/ceo_clarity_panel.parquet`
- `outputs/variables/ceo_clarity_extended/latest/ceo_clarity_extended_panel.parquet`

### Stage 4: Clarity Scores
- `outputs/econometric/manager_clarity/latest/clarity_scores.parquet`
- `outputs/econometric/ceo_clarity/latest/clarity_scores.parquet`
- `outputs/econometric/ceo_clarity_regime/latest/clarity_scores.parquet`

## Baseline Metadata

The `baseline_checksums.json` file includes metadata:

```json
{
  "_metadata": {
    "generated_at": "2026-02-19T20:30:00",
    "git_commit": "abc123...",
    "total_files": 6,
    "missing_files": []
  }
}
```

- `generated_at`: When baselines were computed
- `git_commit`: Git commit hash at time of generation
- `total_files`: Number of files with valid baselines tracked
- `missing_files`: Files that couldn't be found (tests will skip these)