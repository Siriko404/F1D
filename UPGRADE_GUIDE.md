# Upgrade Guide

This document provides step-by-step procedures for upgrading dependencies in the F1D data processing pipeline.

## Overview

The upgrade process is designed to prevent regressions and maintain reproducibility. All upgrades require:
1. Review of release notes for breaking changes
2. Full pipeline run with new version
3. Comparison of outputs with baseline
4. Validation that changes are within expected tolerance
5. Documentation updates

**Goal:** Upgrade dependencies without breaking reproducibility or changing research results.

---

## Statsmodels Upgrade Procedure

### Current Version
- **Pinned Version:** 0.14.6
- **Stability:** Stable for basic OLS regression use cases
- **Breaking Changes:** 0.14.0 introduced deprecated GLM link names
- **Scripts Affected:** All Step 4 econometric scripts (4.1_EstimateCeoClarity, 4.2_LiquidityRegressions, 4.3_TakeoverHazards)

### Upgrade Steps

**1. Review Release Notes**
```bash
# Check statsmodels release notes
# https://www.statsmodels.org/stable/release/index.html

# Look for:
# - Breaking changes in API
# - Deprecated methods/functions
# - Changes to regression model behavior
# - Changes to statistical output (p-values, coefficients)
```

**2. Create Test Branch**
```bash
git checkout -b upgrade-statsmodels-0.15.0
```

**3. Install New Version**
```bash
pip install statsmodels==0.15.0
# Verify installation
python -c "import statsmodels; print(statsmodels.__version__)"
```

**4. Run Full Pipeline with New Version**
```bash
# Run entire pipeline with test data
python 2_Scripts/1_Sample/1.1_CleanMetadata.py
python 2_Scripts/1_Sample/1.2_LinkEntities.py
python 2_Scripts/1_Sample/1.3_BuildTenureMap.py
python 2_Scripts/1_Sample/1.4_AssembleManifest.py
python 2_Scripts/2_Text/2.1_TokenizeAndCount.py
python 2_Scripts/2_Text/2.2_ConstructVariables.py
python 2_Scripts/2_Text/2.3_VerifyStep2.py
python 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
python 2_Scripts/3_Financial/3.1_FirmControls.py
python 2_Scripts/3_Financial/3.2_MarketVariables.py
python 2_Scripts/3_Financial/3.3_EventFlags.py
python 2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py
python 2_Scripts/4_Econometric/4.2_LiquidityRegressions.py
python 2_Scripts/4_Econometric/4.3_TakeoverHazards.py
```

**5. Compare Regression Outputs with Baseline**
```bash
# Step A: Generate baseline checksums (before upgrade)
python tests/generate_baseline_checksums.py

# Step B: After upgrade, compare outputs
python tests/compare_regression_outputs.py \
  --baseline ./4_Outputs/4_Econometric/4.1_EstimateCeoClarity/latest/ \
  --new ./4_Outputs/4_Econometric/4.1_EstimateCeoClarity/latest/ \
  --tolerance 1e-6

# Expected: Coefficients should be identical (within floating-point tolerance)
# If different: Investigate API changes, model implementation changes
```

**6. Validate No Numerical Differences Beyond Tolerance**
```bash
# Check regression coefficients
python -c "
import pandas as pd

baseline = pd.read_csv('./4_Outputs/4_Econometric/4.1_EstimateCeoClarity/latest/ceo_clarity_regression_coefficients.csv')
new = pd.read_csv('./4_Outputs/4_Econometric/4.1_EstimateCeoClarity/latest/ceo_clarity_regression_coefficients.csv')

# Compare coefficients
diff = (baseline['Coefficient'] - new['Coefficient']).abs()
max_diff = diff.max()

print(f'Max coefficient difference: {max_diff}')
if max_diff < 1e-6:
    print('PASS: Differences within floating-point tolerance')
else:
    print('FAIL: Coefficients differ significantly')
    print('Investigate API changes in statsmodels')
"
```

**7. Run pytest Test Suite**
```bash
# Run all tests to ensure compatibility
pytest tests/ -v --tb=short

# Check for:
# - Test failures related to statsmodels API
# - Numerical precision issues
# - Output format changes
```

**8. Update Version in requirements.txt**
```bash
# Only if all checks pass
sed -i 's/statsmodels==0.14.6/statsmodels==0.15.0/' requirements.txt
```

**9. Update DEPENDENCIES.md**
```bash
# Document the upgrade with rationale
# - New version number
# - Breaking changes handled
# - Compatibility notes
# - Upgrade date
```

**10. Commit and Merge**
```bash
git add requirements.txt DEPENDENCIES.md
git commit -m "chore(upgrade): upgrade statsmodels from 0.14.6 to 0.15.0

- Reviewed release notes: [summary of changes]
- Tested full pipeline: [pass/fail]
- Regression outputs: [identical/within tolerance]
- pytest: [all passed/X failures]
- Breaking changes: [documented]
"

git checkout master
git merge upgrade-statsmodels-0.15.0
```

### Rollback Plan

**If upgrade fails:**
```bash
# Revert to previous version
git checkout master
git branch -D upgrade-statsmodels-0.15.0

# Restore previous version
pip install statsmodels==0.14.6

# Verify baseline still works
python 2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py
```

**If upgrade causes numerical differences:**
1. Investigate API changes in release notes
2. Check for changes to model implementation
3. If unavoidable: Document differences in thesis/paper
4. Consider pinning to older version if reproducibility is critical

---

## PyArrow Upgrade Procedure

### Current Version
- **Pinned Version:** 21.0.0
- **Compatibility:** Python 3.8-3.13
- **Constraint:** 23.0.0+ requires Python >= 3.10
- **Scripts Affected:** All scripts reading/writing Parquet files

### Placeholder Upgrade Steps

**Note:** Current version (21.0.0) is stable and compatible. Future upgrades will require:

1. Review Python version requirements (23.0.0+ needs Python 3.10+)
2. Benchmark performance for typical dataset sizes (1GB - 10GB Parquet files)
3. Test read/write operations on all Parquet files in pipeline
4. Compare output file sizes and memory usage
5. Validate no breaking changes to pandas.read_parquet() API

**See DEPENDENCIES.md for current performance notes.**

---

## Testing Requirements

### Full Pipeline Run (Required for Critical Upgrades)

**Applies to:** statsmodels, PyArrow, pandas, numpy

These dependencies directly affect regression outputs and data processing. Full pipeline validation required.

**Procedure:**
1. Run all scripts in sequence (Steps 1-4)
2. Generate output checksums for all output files
3. Compare with baseline checksums
4. Investigate any differences

### Regression Coefficient Comparison (Required for statsmodels)

**Applies to:** statsmodels upgrades

**Procedure:**
1. Extract regression coefficients from baseline outputs
2. Extract regression coefficients from new outputs
3. Compare coefficient values
4. Verify differences are within floating-point tolerance (< 1e-6)
5. Check p-values, R-squared, standard errors for consistency

### pytest Test Suite (Required for All Upgrades)

**Applies to:** All dependency upgrades

**Procedure:**
```bash
# Run full test suite
pytest tests/ -v --tb=short

# Check for:
# - Unit test failures (API changes)
# - Integration test failures (compatibility issues)
# - Regression test failures (output differences)
```

### Performance Benchmarking (Optional for Performance-Critical Upgrades)

**Applies to:** PyArrow, pandas, numpy

**Procedure:**
1. Measure runtime for typical datasets
2. Compare with baseline performance
3. Check memory usage
4. Verify no performance degradation (> 10% slower is concerning)

---

## Rollback Procedures

### General Rollback Strategy

**1. Identify Breaking Changes**
```bash
# Check what changed
git diff HEAD~1 requirements.txt

# Review release notes
# Look for API changes, deprecations, breaking behavior
```

**2. Revert to Previous Version**
```bash
# Method A: Git revert (if upgrade already committed)
git revert HEAD --no-edit
git commit -m "revert(upgrade): rollback [dependency] due to breaking changes"

# Method B: Git checkout (if not yet committed)
git checkout HEAD~1 -- requirements.txt DEPENDENCIES.md
```

**3. Restore Previous Version in Environment**
```bash
# Reinstall previous version
pip install [dependency]==[previous-version]

# Verify installation
python -c "import [dependency]; print([dependency].__version__)"
```

**4. Validate Baseline Works**
```bash
# Run
