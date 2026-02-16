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
python -m f1d.sample.1.1_CleanMetadata
python -m f1d.sample.1.2_LinkEntities
python -m f1d.sample.1.3_BuildTenureMap
python -m f1d.sample.1.4_AssembleManifest
python -m f1d.text.tokenize_and_count
python -m f1d.text.construct_variables
python -m f1d.text.verify_step2
python -m f1d.financial.v1.3.0_BuildFinancialFeatures
python -m f1d.financial.v1.3.1_FirmControls
python -m f1d.financial.v1.3.2_MarketVariables
python -m f1d.financial.v1.3.3_EventFlags
python -m f1d.econometric.v1.4.1_EstimateManagerClarity
python -m f1d.econometric.v1.4.2_LiquidityRegressions
python -m f1d.econometric.v1.4.3_TakeoverHazards
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
python -m f1d.econometric.v1.4.1_EstimateManagerClarity
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

## Python Upgrade Procedure

Before upgrading to a new Python version, validate compatibility:

**1. Check Dependency Support**:
   - Review DEPENDENCIES.md for Python version constraints
   - Check each dependency's release notes for Python support
   - Ensure all dependencies support target Python version

**2. Local Testing**:
   ```bash
   # Install target Python version
   # Windows: Download from python.org or use winget
   # macOS: brew install python@3.X
   # Linux: Use pyenv or system package manager

   # Create virtual environment
   python3.X -m venv venv
   source venv/bin/activate  # Unix
   # or
   venv\Scripts\activate  # Windows

   # Install dependencies
   pip install -r requirements.txt

   # Run pytest to check for compatibility issues
   pytest tests/ -v --tb=short

   # Fix any compatibility issues (usually dependency version conflicts)
   ```

**3. GitHub Actions Validation**:
   ```bash
   # Update .github/workflows/test.yml matrix to include new version
   # Add to matrix.python-version array: ['3.8', '3.9', '3.10', '3.11', '3.12', '3.13', '3.14']

   git add .github/workflows/test.yml
   git commit -m "test(ci): add Python 3.14 to matrix testing"

   # Push changes and verify CI/CD passes
   git push origin master

   # Review test results for any Python-specific failures
   ```

**4. Full Pipeline Validation**:
   ```bash
   # Run full pipeline on new Python version
   python -m f1d.sample.1.1_CleanMetadata
   python -m f1d.sample.1.2_LinkEntities
   python -m f1d.sample.1.3_BuildTenureMap
   python -m f1d.sample.1.4_AssembleManifest
   python -m f1d.text.tokenize_and_count
   python -m f1d.text.construct_variables
   python -m f1d.text.verify_step2
   python -m f1d.financial.v1.3.0_BuildFinancialFeatures
   python -m f1d.financial.v1.3.1_FirmControls
   python -m f1d.financial.v1.3.2_MarketVariables
   python -m f1d.financial.v1.3.3_EventFlags
   python -m f1d.econometric.v1.4.1_EstimateManagerClarity
   python -m f1d.econometric.v1.4.2_LiquidityRegressions
   python -m f1d.econometric.v1.4.3_TakeoverHazards

   # Compare outputs with baseline (from Python 3.10 or 3.11)
   # Use checksum comparison for binary files
   python tests/compare_outputs.py \
     --baseline ./4_Outputs/4_Econometric/baseline/ \
     --new ./4_Outputs/4_Econometric/latest/

   # Verify identical results (accounting for floating-point tolerance)
   ```

**5. Update Documentation**:
   ```bash
   # Add new version to DEPENDENCIES.md "Supported Versions" list
   # Update minimum/maximum version annotations

   # Update .github/workflows/test.yml matrix (already done in step 3)

   # Document any Python-specific workarounds in DEPENDENCIES.md
   ```

**6. Deprecate Old Versions** (optional):
   ```bash
   # If dropping old versions, update requirements.txt comment
   # Example: Change "# Python >= 3.8" to "# Python >= 3.10"

   # Update DEPENDENCIES.md compatibility section
   # Remove old versions from "Supported Versions" list
   # Update "Minimum Version" annotation

   # Update GitHub Actions matrix
   # Remove old versions from matrix.python-version array

   # Announce deprecation in project README.md
   # Add note to DEPENDENCIES.md documenting deprecation
   ```

**Example: Upgrading from Python 3.8 to 3.14 (future upgrade)**

```bash
# Step 1: Check dependency support
# Review DEPENDENCIES.md - all dependencies support Python 3.8+
# Check PyArrow: 23.0.0+ requires Python 3.10+ (compatible with 3.14)
# Check NumPy: 2.x supports Python 3.9+ (compatible with 3.14)
# Check Pandas: 2.x supports Python 3.9+ (compatible with 3.14)

# Step 2: Local testing
python3.14 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
# If fails: Check for NumPy/PyArrow version conflicts

# Step 3: GitHub Actions validation
# Edit .github/workflows/test.yml:
# matrix:
#   python-version: ['3.8', '3.9', '3.10', '3.11', '3.12', '3.13', '3.14']
git add .github/workflows/test.yml
git commit -m "test(ci): add Python 3.14 to matrix testing"
git push origin master
# Verify CI/CD passes for Python 3.14

# Step 4: Full pipeline validation
# Run all scripts (see command list above)
# Compare outputs with Python 3.11 baseline
# Verify identical results

# Step 5: Update documentation
# Add "Python 3.14" to DEPENDENCIES.md "Supported Versions" list
# Update "Latest Tested" to "Python 3.14"

# Step 6: Deprecate Python 3.8 and 3.9 (optional)
# Update requirements.txt comment: "# Python >= 3.10"
# Remove 3.8 and 3.9 from DEPENDENCIES.md "Supported Versions" list
# Remove 3.8 and 3.9 from GitHub Actions matrix
# Add deprecation note to README.md
```

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
