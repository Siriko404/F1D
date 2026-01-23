# Upgrade Guide

This guide provides detailed procedures for upgrading dependencies in the F1D data processing pipeline. Upgrades are performed systematically to minimize risk and maintain reproducibility.

## Overview

**Principles:**
1. **Reproducibility first**: All upgrades must preserve output checksums
2. **Performance baseline**: Benchmark before and after upgrades
3. **Compatibility validation**: Test on all target Python versions (3.8-3.13)
4. **Minimum risk**: Upgrade one dependency at a time
5. **Rollback plan**: Document downgrade steps for each upgrade

## General Upgrade Process

For any dependency upgrade:

1. **Review release notes**: Check for breaking changes, API changes, known issues
2. **Create test branch**: `git checkout -b upgrade-{dependency}-{version}`
3. **Update requirements.txt**: Change version pin
4. **Install new version**: `pip install -r requirements.txt --upgrade`
5. **Run test suite**: `pytest tests/ -v`
6. **Benchmark performance**: Measure timing, memory, throughput
7. **Run full pipeline**: Validate on test data
8. **Compare outputs**: Verify checksums match baseline
9. **Update documentation**: Update DEPENDENCIES.md, UPGRADE_GUIDE.md
10. **Commit changes**: Document rationale and testing performed
11. **Merge to master**: Only after full validation

## PyArrow Upgrade Procedure

Before upgrading PyArrow, verify Python version compatibility and performance:

### 1. Check Python Compatibility

```bash
# Review PyArrow release notes for minimum Python version
# Example: PyArrow 23.0.0 requires Python >= 3.10
```

**Validation checklist:**
- [ ] Review PyArrow release notes on GitHub or PyPI
- [ ] Identify minimum Python version requirement
- [ ] Ensure target Python versions (3.8-3.13) are supported
- [ ] PyArrow 23.0.0+ requires Python >= 3.10 (not compatible with 3.8-3.9)

**If Python 3.8/3.9 support required:**
- Stay on PyArrow 21.0.0 (last version supporting Python 3.8)
- Document Python version constraint in DEPENDENCIES.md
- Consider Python version upgrade as separate initiative

### 2. Performance Benchmarking

Create performance baseline with current version:

```python
import time
import pandas as pd
import psutil
import hashlib

def benchmark_parquet_io(file_path, num_runs=5):
    """Benchmark Parquet read/write performance."""
    # Memory tracking
    start_mem = psutil.Process().memory_info().rss / (1024 * 1024)

    # Read benchmark
    read_times = []
    for _ in range(num_runs):
        t0 = time.time()
        df = pd.read_parquet(file_path)
        read_times.append(time.time() - t0)

    # Write benchmark
    write_times = []
    output_path = "test_output_benchmark.parquet"
    for _ in range(num_runs):
        t0 = time.time()
        df.to_parquet(output_path)
        write_times.append(time.time() - t0)

    # Memory tracking
    end_mem = psutil.Process().memory_info().rss / (1024 * 1024)
    mem_delta = end_mem - start_mem

    # Compute checksums for reproducibility
    with open(file_path, 'rb') as f:
        read_checksum = hashlib.sha256(f.read()).hexdigest()
    with open(output_path, 'rb') as f:
        write_checksum = hashlib.sha256(f.read()).hexdigest()

    # Clean up
    import os
    os.remove(output_path)

    return {
        "avg_read_time": sum(read_times) / len(read_times),
        "avg_write_time": sum(write_times) / len(write_times),
        "memory_mb": mem_delta,
        "read_checksum": read_checksum,
        "write_checksum": write_checksum,
        "file_size_mb": os.path.getsize(file_path) / (1024 * 1024)
    }

# Benchmark with typical dataset sizes
# Example: Small (<100MB), Medium (100MB-1GB), Large (>1GB)
```

**Test with typical dataset sizes:**
- Small: Sample metadata files (<100MB)
- Medium: Financial features datasets (100MB-1GB)
- Large: Text processing outputs (1GB-10GB)

**Metrics to record:**
- Average read time (seconds)
- Average write time (seconds)
- Peak memory usage (MB)
- File size (MB)
- SHA-256 checksum (for integrity validation)

**Record baseline in DEPENDENCIES.md:**

```markdown
### PyArrow Performance Baseline (21.0.0)

| Dataset Size | Read Time | Write Time | Memory | File Size |
|--------------|-----------|-------------|---------|-----------|
| Small (<100MB) | 0.5s | 0.3s | 50MB | 25MB |
| Medium (100MB-1GB) | 2.1s | 1.8s | 200MB | 450MB |
| Large (>1GB) | 12.4s | 10.2s | 800MB | 2.3GB |

Tested on: [system configuration]
Date: [date]
```

### 3. Test New Version

After upgrading PyArrow:

1. **Upgrade in requirements.txt:**
   ```
   # Change from:
   pyarrow==21.0.0
   # To:
   pyarrow==23.0.0
   ```

2. **Install new version:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Run benchmarking again:**
   - Use same benchmark script from Step 2
   - Test with same dataset sizes
   - Record all metrics

4. **Compare with baseline:**

   ```python
   # Compare performance
   def compare_performance(old_metrics, new_metrics, tolerance=0.10):
       """Check if performance regression exceeds tolerance."""
       read_regression = (new_metrics['avg_read_time'] - old_metrics['avg_read_time']) / old_metrics['avg_read_time']
       write_regression = (new_metrics['avg_write_time'] - old_metrics['avg_write_time']) / old_metrics['avg_write_time']

       if read_regression > tolerance or write_regression > tolerance:
           print(f"WARNING: Performance regression detected!")
           print(f"  Read time: {read_regression:.1%} slower")
           print(f"  Write time: {write_regression:.1%} slower")
           return False
       else:
           print(f"Performance within tolerance (+/- {tolerance:.0%})")
           return True
   ```

5. **Performance regression threshold:**
   - **Acceptable**: <10% regression
   - **Acceptable with investigation**: 10-20% regression (investigate cause)
   - **Defer upgrade**: >20% regression (significant degradation)

### 4. Full Pipeline Validation

After performance benchmarking passes:

1. **Run full pipeline:**
   ```bash
   # Run all pipeline steps sequentially
   python 2_Scripts/1_Sample/1.0_BuildSampleManifest.py
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

2. **Verify no errors or warnings:**
   - Check log files in 3_Logs/ for errors
   - Look for PyArrow-specific warnings (e.g., deprecated features)
   - Confirm all Parquet I/O operations succeed

3. **Check output file integrity:**
   ```bash
   # Compute checksums of all output files
   find 4_Outputs/ -name "*.parquet" -exec sha256sum {} \; > output_checksums_new.txt

   # Compare with baseline
   diff output_checksums_baseline.txt output_checksums_new.txt
   ```

   - **Expected**: All checksums match (bitwise-identical outputs)
   - **If checksums differ**: Investigate root cause
     - Check for non-deterministic operations (sorting with ties, parallel processing)
     - Verify PyArrow version doesn't change serialization
     - Confirm pandas version compatibility

### 5. Update Documentation

After successful upgrade:

1. **Update version in requirements.txt:**
   ```python
   # Add comment explaining upgrade
   # Upgraded from 21.0.0 to 23.0.0 on [date]
   # Rationale: [performance gains, bug fixes, new features]
   # Validation: Performance within +/-5% tolerance, all outputs identical
   pyarrow==23.0.0
   ```

2. **Update Python compatibility note in DEPENDENCIES.md:**
   ```markdown
   ### PyArrow
   - **Version**: 23.0.0 (pinned)
   - **Compatibility**: Python 3.10+ (upgraded from 3.8+)
   - **Rationale**:
     - Requires Python >= 3.10 (no longer supports 3.8-3.9)
     - Performance improvement: [X% faster reads/writes]
   - **Performance Baseline**:
     - Updated on [date] with [system configuration]
     - See performance table below
   ```

3. **Document performance changes in DEPENDENCIES.md:**
   ```markdown
   ### PyArrow Performance Baseline (23.0.0)

   | Dataset Size | Read Time | Write Time | Memory | File Size |
   |--------------|-----------|-------------|---------|-----------|
   | Small (<100MB) | 0.45s | 0.28s | 48MB | 24MB |
   | Medium (100MB-1GB) | 1.9s | 1.6s | 190MB | 440MB |
   | Large (>1GB) | 11.2s | 9.1s | 750MB | 2.2GB |

   **Comparison to 21.0.0:**
   - Small: 10% faster reads, 7% faster writes
   - Medium: 10% faster reads, 11% faster writes
   - Large: 10% faster reads, 11% faster writes

   Tested on: [system configuration]
   Date: [date]
   ```

4. **Update UPGRADE_GUIDE.md with findings:**
   ```markdown
   ### PyArrow Upgrade History

   **[date]: 21.0.0 → 23.0.0**
   - Python compatibility: 3.8-3.13 → 3.10-3.13
   - Performance improvement: ~10% faster reads/writes
   - Memory usage: ~6% reduction
   - Issues: None
   - Validation: All outputs identical, full pipeline passes
   ```

### Example: PyArrow 21.0.0 → 23.0.0 (Not Recommended for 3.8-3.9)

**Why this upgrade is NOT recommended for Python 3.8-3.9:**

- Python compatibility change: 3.8+ → 3.10+
- Would drop support for Python 3.8 and 3.9
- Current target range: 3.8-3.13 (see CLAUDE.md)

**If Python 3.10+ support is acceptable:**

1. Update Python version constraint in requirements.txt:
   ```
   # Python Version
   # Python >= 3.10 (upgraded from 3.8 for PyArrow 23.0.0)
   ```

2. Follow Steps 1-5 above

3. Document in DEPENDENCIES.md:
   ```markdown
   ## Python Version Support

   ### Target Range: 3.10 - 3.13 (Updated [date])
   - Previous range: 3.8 - 3.13
   - Rationale: PyArrow 23.0.0 requires Python >= 3.10
   - Impact: No longer supports Python 3.8 and 3.9
   ```

## Statsmodels Upgrade Procedure

### 1. Check API Compatibility

```bash
# Review statsmodels release notes
# Look for breaking changes in:
# - Formula API (patsy syntax)
# - Fixed effects models (PanelOLS)
# - Model results attributes
# - Summary output format
```

### 2. Test Regression Models

Create test script for key models:

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd

def test_regression_api():
    """Test statsmodels API compatibility."""
    # Create dummy data
    df = pd.DataFrame({
        'y': [1, 2, 3, 4, 5],
        'x1': [1, 2, 1, 2, 1],
        'x2': [2, 1, 2, 1, 2],
        'group': ['A', 'A', 'B', 'B', 'A']
    })

    # Test OLS
    model = sm.OLS(df['y'], sm.add_constant(df[['x1', 'x2']]))
    results = model.fit()

    # Verify attributes exist
    assert hasattr(results, 'params'), "Missing params attribute"
    assert hasattr(results, 'rsquared'), "Missing rsquared attribute"
    assert hasattr(results, 'summary'), "Missing summary method"

    # Test formula API
    formula_model = smf.ols('y ~ x1 + x2', data=df)
    formula_results = formula_model.fit()

    assert hasattr(formula_results, 'params'), "Missing params attribute in formula model"

    print("Statsmodels API test passed!")

if __name__ == "__main__":
    test_regression_api()
```

### 3. Pipeline Validation

Run Step 4 scripts (all use statsmodels):

```bash
python 2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py
python 2_Scripts/4_Econometric/4.2_LiquidityRegressions.py
python 2_Scripts/4_Econometric/4.3_TakeoverHazards.py
```

### 4. Compare Output Coefficients

**Expected:** Coefficients match within numerical precision (±1e-10)

**If coefficients differ:**
- Investigate API changes (e.g., default solver, convergence criteria)
- Check for deprecated features (warnings indicate changes)
- Verify numerical stability (random seeds, starting values)

## Python Version Upgrade Procedure

### 1. Dependency Compatibility Check

```bash
# Create compatibility matrix
# For each dependency in requirements.txt:
# 1. Check minimum Python version
# 2. Check maximum Python version
# 3. Identify any blockers

# Example table:
# | Dependency | Min Python | Max Python | Upgrade Path |
# |------------|-------------|------------|--------------|
# | pandas | 3.8 | 3.13 | OK |
# | PyArrow 21.0.0 | 3.8 | 3.13 | OK |
# | PyArrow 23.0.0 | 3.10 | 3.13 | Requires Python 3.10+ |
```

### 2. Test on Target Python Version

1. **Create Python virtual environment:**
   ```bash
   python3.12 -m venv venv_test_py312
   source venv_test_py312/bin/activate  # Linux/Mac
   # or
   venv_test_py312\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run test suite:**
   ```bash
   pytest tests/ -v
   ```

4. **Run full pipeline** (subset for validation):
   ```bash
   python 2_Scripts/1_Sample/1.0_BuildSampleManifest.py
   python 2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py
   ```

### 3. Performance Comparison

Compare performance between Python versions:

```python
import time
import sys

def benchmark_python_version():
    """Compare performance across Python versions."""
    print(f"Python version: {sys.version}")

    # Simple benchmark
    t0 = time.time()
    for _ in range(1_000_000):
        sum([i for i in range(100)])
    elapsed = time.time() - t0

    print(f"Computation time: {elapsed:.3f}s")

if __name__ == "__main__":
    benchmark_python_version()
```

**Expected:** Performance within ±20% across versions

## Rollback Procedure

If upgrade causes issues:

### 1. Quick Rollback

```bash
# Restore previous version in requirements.txt
git checkout HEAD~1 requirements.txt

# Reinstall previous version
pip install -r requirements.txt --upgrade

# Verify pipeline works
pytest tests/ -v
```

### 2. Document Rollback

In UPGRADE_GUIDE.md:

```markdown
### PyArrow Upgrade History

**[date]: 23.0.0 → 21.0.0 (Rollback)**
- Issue: [describe problem]
- Symptoms: [error messages, performance regression, incorrect outputs]
- Resolution: Rolled back to 21.0.0
- Impact: Deferred upgrade until [condition for retry]
```

## Validation Checklist

For any dependency upgrade:

- [ ] Release notes reviewed, breaking changes identified
- [ ] Test branch created from master
- [ ] requirements.txt updated with new version
- [ ] New version installed in isolated environment
- [ ] Unit tests pass (pytest tests/)
- [ ] Integration tests pass (pytest -m integration)
- [ ] Performance benchmarked (within ±10% of baseline)
- [ ] Full pipeline runs without errors
- [ ] Output checksums match baseline (±0% tolerance)
- [ ] Documentation updated (DEPENDENCIES.md, UPGRADE_GUIDE.md)
- [ ] Rollback procedure documented
- [ ] Changes committed with detailed message
- [ ] PR created for review (if using branches)
- [ ] All CI/CD checks pass (if applicable)

## Minimum Risk Upgrade Sequence

Recommended order for dependency upgrades (low risk first):

1. **psutil** (observability only, no data impact)
2. **python-dateutil** (date parsing, well-tested)
3. **PyYAML** (config file reading, simple API)
4. **scipy** (scientific functions, stable API)
5. **numpy** (foundational, test carefully)
6. **pandas** (core library, test extensively)
7. **statsmodels** (regression models, verify coefficients)
8. **PyArrow** (I/O performance, benchmark thoroughly)
9. **lifelines** (hazard models, niche use case)

**Why this order:**
- Low-risk first (isolated, simple APIs)
- Build confidence with early successes
- Leave high-impact changes for last
- Can stop mid-sequence if issues arise

## Security Updates

When security patches are released:

### 1. Rapid Assessment

- Check CVSS score (severity)
- Review exploitability (local/remote)
- Identify affected functionality in pipeline

### 2. Emergency Upgrade (if high-severity)

1. **Skip extensive performance testing** (security > performance)
2. **Focus on functional testing** (does it still work?)
3. **Accept temporary performance regression** (fix in follow-up)
4. **Document emergency nature** (why we rushed)

Example commit message:

```
fix(14-02): emergency upgrade pandas due to CVE-2024-XXXXX

- Upgraded from 2.2.3 to 2.2.4 (security patch)
- CVSS: 9.8 (critical), Remote code execution possible
- Emergency upgrade: Skipped performance testing
- Functional testing: Full pipeline passes, outputs identical
- Performance: Will benchmark and optimize in follow-up task

Refs: https://github.com/pandas-dev/pandas/issues/XXXXX
```

---

*Last updated: 2026-01-23*
*See also: DEPENDENCIES.md, requirements.txt*
