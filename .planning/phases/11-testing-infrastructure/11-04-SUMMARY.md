# Phase 11 Plan 04: Regression Tests Summary

## Overview

Added regression tests using SHA-256 checksum comparison to detect unintended output changes.

## One-Liner

Regression tests with SHA-256 checksums and helper script for baseline management.

## Metrics

- **Duration:** ~3 minutes
- **Completed:** 2026-01-23
- **Tests Created:** 5
- **Baseline Files:** 17
- **Test Files:** 2

## Tech Stack Added

- hashlib (SHA-256 checksums)
- pandas.util.hash_pandas_object (DataFrame hashing)
- JSON metadata tracking

## Tech Patterns Established

- **Regression Detection Pattern:** SHA-256 checksums computed via pandas hashing
- **Baseline Management:** Separate script to generate/update baselines
- **Graceful Skips:** Tests skip when baselines or outputs are missing
- **Metadata Tracking:** Baseline files include generation time, git commit, file count

## Key Files Created

### Created
- `tests/regression/test_output_stability.py` - Regression tests for output stability
  - `test_regression_step1_output_stability` - Step 1 output checksum
  - `test_regression_step2_output_stability` - Step 2 yearly output checksums
  - `test_regression_step3_output_stability` - Step 3 output checksum
  - `test_regression_key_outputs[path, key]` - Parametrized key output tests

- `tests/regression/generate_baseline_checksums.py` - Helper script to generate baselines
  - Computes SHA-256 checksums for all tracked output files
  - Includes metadata (generation time, git commit)
  - Handles missing files gracefully

- `tests/regression/README.md` - Documentation for regression testing
  - How to run regression tests
  - How to update baselines
  - Explanation of checksum algorithm
  - Tracked output files list

- `tests/fixtures/baseline_checksums.json` - Baseline checksums
  - 17 Step 2 yearly output checksums
  - Metadata (generated_at, git_commit, total_files, missing_files)
  - Missing: Step 1 and Step 3 outputs (not yet available)

### Modified
- None

## Dependencies

- **Requires:** Phase 11-01 (pytest framework setup), Phase 11-02 (unit tests)
- **Provides:** Regression detection for future code changes
- **Affects:** All pipeline outputs (regression tests will catch changes)

## Decisions Made

1. **SHA-256 via Pandas:** Use `pd.util.hash_pandas_object()` for checksums (bitwise-identical)
2. **Metadata Tracking:** Include git commit in baselines to trace changes to code versions
3. **Missing File Handling:** Script skips missing files and reports in metadata
4. **Baseline Update Process:** Clear documentation on when/how to update baselines

## Deviations from Plan

None - plan executed exactly as written.

## Success Criteria

✅ 1. Regression tests use SHA-256 checksum comparison pattern
✅ 2. Baseline checksums stored in tests/fixtures/baseline_checksums.json
✅ 3. Regression tests detect changes in output data
✅ 4. Helper script generates baseline checksums from existing outputs
✅ 5. Baseline update process is documented in README.md
✅ 6. All regression tests pass (or skip gracefully if baselines missing)

## Test Coverage

- **Step 1 (Sample Construction):** 1 test
  - Output stability check

- **Step 2 (Text Processing):** 1 test (17 yearly files checked)
  - Output stability check for 2002-2018 files

- **Step 3 (Financial Features):** 1 test
  - Output stability check

- **Key Outputs:** 1 test (4 parametrized)
  - Step 1: cleaned_metadata.parquet
  - Step 2: linguistic_counts_2002.parquet, linguistic_counts_2018.parquet
  - Step 3: financial_features.parquet

## Baseline Status

- **Generated Baselines:** 17 files
  - Step 2 (Text Processing): 17 yearly outputs (2002-2018)

- **Missing Baselines:** 2 files
  - Step 1 (Sample Construction): cleaned_metadata.parquet
  - Step 3 (Financial Features): financial_features.parquet

## Verification Commands

```bash
# Run all regression tests
python -m pytest tests/regression/ -v -m regression

# Generate baseline checksums
python tests/regression/generate_baseline_checksums.py

# View baseline checksums
cat tests/fixtures/baseline_checksums.json

# Show only regression tests
python -m pytest --collect-only -m regression
```

## Checksum Algorithm

Regression tests use SHA-256 checksums computed via pandas:

```python
import hashlib
import pandas as pd

def compute_dataframe_checksum(df: pd.DataFrame) -> str:
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()
```

This ensures bitwise-identical detection of data changes.

## Commits

- f7df2c1: `feat(11-04): Add regression tests for output stability`

## Next Steps

- Plan 11-05: Add data validation tests
- Plan 11-06: Add edge case tests

---

**Status:** ✅ COMPLETED
**Commit:** f7df2c1
**Date:** 2026-01-23
