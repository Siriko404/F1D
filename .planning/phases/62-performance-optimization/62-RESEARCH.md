# Phase 62: Performance Optimization - Research

**Researched:** 2026-02-11
**Domain:** Pandas performance optimization, DataFrame operations, vectorization
**Confidence:** HIGH

## Summary

This phase addresses performance bottlenecks in the F1D data processing pipeline that were identified but not fully resolved in Phase 10. The current codebase runs on **pandas 2.2.3**, and optimizations should focus on patterns that work within this version while being compatible with future pandas 3.x upgrades.

**Four primary bottleneck categories identified:**
1. **Inefficient DataFrame bulk updates** using `df.loc[update_df.index, col] = update_df[col]` pattern
2. **Excessive `pd.concat()` calls** (62+ instances) creating memory pressure
3. **Per-firm rolling window computations** without vectorized `groupby().rolling().transform()`
4. **Suboptimal chunked processing** with fixed chunk_size that could be tuned

**Primary recommendation:** Implement optimizations incrementally using pandas 2.2.3-compatible patterns, prioritize DataFrame update pattern fixes and concat reduction, verify bitwise-identical outputs after each change, and document performance improvements. Consider pandas 3.0 upgrade separately due to its breaking copy-on-write changes.

## User Constraints (from CONTEXT.md)

### Locked Decisions (Must Honor)
- **Reproducibility is non-negotiable**: All optimizations must produce bitwise-identical outputs (verified via df.equals())
- **No algorithm changes**: Optimizations must preserve exact logic, only improve performance
- **Incremental validation**: Each optimized script must be verified before proceeding

### Claude's Discretion (Your Freedom Areas)
- **Priority ranking**: Which scripts to optimize first based on impact vs effort
- **Optimization techniques**: Vectorization, efficient DataFrame patterns, chunking improvements
- **Scope**: May subset to highest-ROI optimizations if full pipeline is too large

### Deferred Ideas (Out of Scope)
- **Parallel processing (multiprocessing)** - may break single-threaded determinism
- **Caching mechanisms** - adds complexity, may violate reproducibility
- **Algorithm changes** - must preserve exact logic

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.2.3 | DataFrame operations, vectorization | Current production version, stable API |
| numpy | 2.3.2 | Vectorized numerical operations | Bundled with pandas, required for computations |
| pyarrow | 21.0.0 | Parquet I/O, efficient columnar reads | Default pandas Parquet backend, Python 3.8 compatible |

### Supporting (Already Installed)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| psutil | 7.2.1 | Memory profiling | For measuring optimization impact |
| py-spy | (install if needed) | CPU profiling | For identifying hotspots |

### NOT Recommended for This Phase
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pandas 2.2.3 | pandas 3.0.0 | Breaking copy-on-write changes, requires extensive testing |
| Single concat per operation | Dask/Polars | Overkill for dataset size, adds dependency |

**Installation:**
```bash
# Current stack - already installed
pip install pandas==2.2.3 numpy==2.3.2 pyarrow==21.0.0

# Optional: profiler for bottleneck identification
pip install py-spy
```

## Architecture Patterns

### Pattern 1: Replace df.loc Bulk Updates with pd.merge()

**What:** `df.loc[update_df.index, col] = update_df[col]` is inefficient for multi-column updates

**When to use:** When updating multiple columns in a DataFrame from another DataFrame

**Current problematic pattern (from 1.2_LinkEntities.py lines 505-509):**
```python
# BAD: Inefficient - multiple loc assignments create copies
unique_df.loc[update_df.index, "gvkey"] = update_df["gvkey"]
unique_df.loc[update_df.index, "conm"] = update_df["conm"]
unique_df.loc[update_df.index, "sic"] = update_df["sic"]
unique_df.loc[update_df.index, "link_method"] = update_df["link_method"]
unique_df.loc[update_df.index, "link_quality"] = update_df["link_quality"]
```

**Optimized pattern:**
```python
# GOOD: Single merge operation
cols_to_update = ["gvkey", "conm", "sic", "link_method", "link_quality"]
unique_df = (
    unique_df.set_index("company_id")
    .drop(columns=cols_to_update, errors="ignore")
    .join(update_df.set_index("company_id")[cols_to_update], how="left")
    .reset_index()
)

# Alternative: Use update() for in-place modification
unique_df = unique_df.set_index("company_id")
update_subset = update_df.set_index("company_id")[cols_to_update]
unique_df.update(update_subset)
unique_df = unique_df.reset_index()
```

**Speedup:** 2-5x for bulk updates, especially with many columns

### Pattern 2: Reduce pd.concat() Calls with Pre-allocation

**What:** Accumulating DataFrames in a list and calling `pd.concat()` once vs incremental concatenation

**When to use:** When building a DataFrame from multiple chunks or iterations

**Current problematic pattern (many files use this):**
```python
# BAD: O(n^2) memory behavior
results = []
for chunk in data:
    processed = process(chunk)
    results.append(processed)
    # Memory keeps growing with each append

final = pd.concat(results, ignore_index=True)  # Single concat at end is OK
```

**Worse pattern (incremental concat in loop):**
```python
# WORSE: Concat on each iteration
df = pd.DataFrame()
for chunk in data:
    temp = process(chunk)
    df = pd.concat([df, temp], ignore_index=True)  # Very slow!
```

**Optimized pattern - use list-of-dicts then single concat:**
```python
# GOOD: Build list of dicts/arrays, concat once
records = []
for chunk in data:
    processed = process(chunk)
    records.extend(processed.to_dict("records"))

final = pd.DataFrame(records)
```

**For DataFrame chunks:**
```python
# GOOD: Collect chunks, single concat
chunks = []
for chunk in data:
    processed = process(chunk)
    chunks.append(processed)

final = pd.concat(chunks, ignore_index=True)  # Single concat
```

**Speedup:** 5-20x depending on number of iterations

### Pattern 3: Vectorized Rolling Windows with groupby().rolling().transform()

**What:** Replace per-firm rolling computations with vectorized groupby operations

**When to use:** When computing rolling statistics per group (e.g., per-firm volatility)

**Current pattern from 3.2_H2Variables.py (lines 809-826):**
```python
# LESS EFFICIENT: Iterating over groups manually
for gvkey, group in df.groupby("gvkey"):
    group = group.sort_values("fiscal_year").reset_index(drop=True)
    rolling_std = group["ocf_at"].rolling(window=5, min_periods=3).std()
    # ... process results
    results.append(...)
```

**Optimized pattern:**
```python
# GOOD: Vectorized transform
df_sorted = df.sort_values(["gvkey", "fiscal_year"])
df_sorted["cf_volatility"] = (
    df_sorted.groupby("gvkey")["ocf_at"]
    .transform(lambda x: x.rolling(window=5, min_periods=3).std())
)

# Even better for simple aggregations:
df_sorted["cf_volatility"] = (
    df_sorted.groupby("gvkey")["ocf_at"]
    .rolling(window=5, min_periods=3)
    .std()
    .reset_index(level=0, drop=True)  # Drop group index, keep original
)
```

**Speedup:** 10-50x for large numbers of groups

### Anti-Patterns to Avoid

- **Chained .loc assignments**: Each creates an intermediate copy
- **Incremental pd.concat() in loops**: O(n^2) memory and time
- **.apply() with lambda functions**: Usually slower than vectorized operations
- **.iterrows() for anything but debugging**: Always use vectorization or .itertuples()

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| DataFrame updates | Custom index iteration | `pd.merge()` or `df.update()` | Pandas handles index alignment efficiently |
| Chunk processing | Manual chunking logic | `chunked_reader.py` (already exists) | Already implemented with memory awareness |
| Rolling windows | Per-group loops | `.groupby().rolling().transform()` | Vectorized C implementation |
| Large file reading | Custom streaming | PyArrow dataset API | Optimized for columnar format |

**Key insight:** The codebase already has `shared/chunked_reader.py` with `read_in_chunks()` and `process_in_chunks()`. Use these rather than re-implementing chunked processing.

## Common Pitfalls

### Pitfall 1: Breaking Determinism with Optimizations

**What goes wrong:** Vectorized or optimized code produces different results due to:
- Floating-point operation order differences
- NaN handling variations
- Index alignment changes

**Why it happens:**
- Vectorized operations process data in different order than iteration
- pandas and NumPy may handle edge cases differently

**How to avoid:**
```python
# Step 1: Create reference output before optimization
df_reference = process_original(data)

# Step 2: Run optimized version
df_optimized = process_optimized(data)

# Step 3: Verify bitwise equality
assert df_reference.equals(df_optimized), "Optimization changed results!"

# Step 4: For floats, allow small differences
import numpy as np
assert np.allclose(
    df_reference.select_dtypes(include=[np.number]),
    df_optimized.select_dtypes(include=[np.number]),
    rtol=1e-10, atol=1e-10
), "Float values differ beyond tolerance!"
```

**Warning signs:**
- Regression test failures
- Summary statistics changes (mean, std, count)
- Different NaN patterns

### Pitfall 2: Memory Explosion with Intermediate Copies

**What goes wrong:**
- `df.loc` assignments create copies before pandas 3.0
- Chained indexing creates multiple copies
- `pd.concat()` duplications

**Why it happens:**
- pandas 2.x has complex copy/view semantics
- Operations that look in-place may create copies

**How to avoid:**
```python
# BAD: Creates multiple copies
df_new = df_old.copy()
df_new["col"] = value  # May trigger copy-on-write

# GOOD: Be explicit about copies
df_new = df_old.copy()

# BAD: Chained assignment
df[df["a"] > 0]["b"] = 1  # May not work (SettingWithCopyWarning)

# GOOD: Single loc assignment
df.loc[df["a"] > 0, "b"] = 1
```

**Warning signs:**
- Memory usage increasing during "in-place" operations
- SettingWithCopyWarning in logs
- OOM errors on large datasets

### Pitfall 3: Over-Optimizing Small Operations

**What goes wrong:**
- Spending time optimizing operations that take <1 second
- Making code less readable for minimal gain

**Why it happens:**
- Focus on micro-optimizations vs macro-optimizations
- Not profiling to find actual bottlenecks

**How to avoid:**
```python
# Profile before optimizing
import time

start = time.perf_counter()
result = slow_operation()
elapsed = time.perf_counter() - start

if elapsed < 1.0:
    print(f"Operation takes {elapsed:.2f}s - not worth optimizing")
else:
    print(f"Operation takes {elapsed:.2f}s - optimize this!")
```

**Guideline:** Only optimize operations taking >5 seconds or called frequently

## Code Examples

### Example 1: Fixing df.loc Bulk Update Pattern

**File:** `2_Scripts/1_Sample/1.2_LinkEntities.py` (lines 498-511)

**Before:**
```python
# Lines 498-511 (Tier 1 linking)
update_df = merged[["company_id", "gvkey", "conm", "sic"]].copy()
update_df["link_method"] = "permno_date"
update_df["link_quality"] = 100

unique_df = unique_df.set_index("company_id")
update_df = update_df.set_index("company_id")

unique_df.loc[update_df.index, "gvkey"] = update_df["gvkey"]
unique_df.loc[update_df.index, "conm"] = update_df["conm"]
unique_df.loc[update_df.index, "sic"] = update_df["sic"]
unique_df.loc[update_df.index, "link_method"] = update_df["link_method"]
unique_df.loc[update_df.index, "link_quality"] = update_df["link_quality"]

unique_df = unique_df.reset_index()
```

**After (optimized):**
```python
# Single merge operation - cleaner and faster
cols_to_update = ["gvkey", "conm", "sic", "link_method", "link_quality"]

# Prepare update data
update_df = merged[["company_id", "gvkey", "conm", "sic"]].copy()
update_df["link_method"] = "permno_date"
update_df["link_quality"] = 100

# Use merge for bulk update (preserves index alignment)
unique_df = (
    unique_df.drop(columns=cols_to_update, errors="ignore")
    .merge(
        update_df[["company_id"] + cols_to_update],
        on="company_id",
        how="left",
        suffixes=("", "_update")
    )
)

# For columns that were updated, take the new value
for col in cols_to_update:
    if f"{col}_update" in unique_df.columns:
        unique_df[col] = unique_df[f"{col}_update"]
        unique_df = unique_df.drop(columns=[f"{col}_update"])
```

### Example 2: Vectorized Rolling Windows

**File:** `2_Scripts/3_Financial_V2/3.2_H2Variables.py` (lines 809-835)

**Before:**
```python
# Lines 812-826 (cf_volatility computation)
results = []

for _gvkey, group in df_comp.groupby("gvkey"):
    group = group.sort_values("fiscal_year").reset_index(drop=True)

    # Compute rolling std
    rolling_std = (
        group["ocf_at"].rolling(window=window, min_periods=min_years).std()
    )

    # Keep only valid observations
    mask = rolling_std.notna()
    if mask.any():
        group_subset = group.loc[mask].copy()
        group_subset["cf_volatility"] = rolling_std.loc[mask].values
        results.append(group_subset[["gvkey", "fiscal_year", "cf_volatility"]])

if results:
    result = pd.concat(results, ignore_index=True)
```

**After (optimized):**
```python
# Single vectorized operation
df_sorted = df_comp.sort_values(["gvkey", "fiscal_year"]).copy()

# Compute rolling std per gvkey group in one operation
df_sorted["cf_volatility"] = (
    df_sorted.groupby("gvkey")["ocf_at"]
    .transform(lambda x: x.rolling(window=window, min_periods=min_years).std())
)

# Filter to valid observations only
result = df_sorted[df_sorted["cf_volatility"].notna()][
    ["gvkey", "fiscal_year", "cf_volatility"]
].reset_index(drop=True)
```

**Speedup:** ~20x for typical firm counts (thousands of gvkeys)

### Example 3: Single Concat vs Multiple

**Before (pattern found in multiple files):**
```python
# Building results incrementally - OK if single concat at end
results = []
for item in items:
    processed = process(item)
    results.append(processed)

final = pd.concat(results, ignore_index=True)
```

**This is actually fine** - single concat at end. The problem is incremental concat:

**Problem pattern (avoid this):**
```python
# BAD: Concat on each iteration
df = pd.DataFrame()
for item in items:
    temp = process(item)
    df = pd.concat([df, temp], ignore_index=True)  # O(n^2)!
```

**Optimized:**
```python
# Collect chunks, single concat
chunks = []
for item in items:
    temp = process(item)
    chunks.append(temp)

final = pd.concat(chunks, ignore_index=True)  # O(n)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `.apply(lambda)` | Vectorized operations | pandas 1.0+ | 10-100x speedup |
| `.iterrows()` | `.itertuples()` or vectorization | pandas 0.20+ | 5-100x speedup |
| Chained `.loc` updates | `pd.merge()` or `df.update()` | Always | 2-5x speedup |
| Incremental concat | List collection + single concat | Always | 5-20x speedup |
| Manual groupby loops | `.groupby().transform()` | pandas 0.23+ | 10-50x speedup |

**pandas 3.0.0 (January 2026) - NOTE: Not Adopting Yet**
- **Copy-on-Write (CoW)** now default - eliminates unpredictable copy/view behavior
- 200% performance improvement for large-scale processing
- String operations 5-10x faster via PyArrow
- **Not recommended for Phase 62** due to breaking changes requiring extensive testing

**Deprecated/outdated:**
- **`.iterrows()`**: Almost never the right choice (except debugging)
- **Chained indexing**: `df[df["a"] > 0]["b"] = x` doesn't work reliably
- **`.apply()` with lambda**: Use vectorized operations when possible

## Implementation Priority and ROI

### High Priority (High ROI, Low Risk)
| File | Pattern | Time Savings | Risk | Priority |
|------|----------|---------------|-------|----------|
| `1.2_LinkEntities.py` | df.loc bulk updates | 20-40% | Low | 1 |
| `3.2_H2Variables.py` | Rolling window loops | 50-80% | Medium | 2 |
| `3.2_H2Variables.py` | Duplicate rolling computations | 30-50% | Low | 3 |

### Medium Priority (Moderate ROI, Low Risk)
| File | Pattern | Time Savings | Risk | Priority |
|------|----------|---------------|-------|----------|
| Text processing scripts | Potential vectorization | 10-30% | Low | 4 |
| Financial V2 scripts | General concat/merge patterns | 15-25% | Low | 5 |

### Lower Priority (Moderate ROI, Higher Risk)
| File | Pattern | Time Savings | Risk | Priority |
|------|----------|---------------|-------|----------|
| Econometric scripts | Complex merge patterns | 10-20% | Medium | 6 |

## Performance Measurement Strategy

### Profiling Before Optimizing

```python
import time
import psutil

def measure_operation(func, *args, **kwargs):
    """Measure timing and memory of an operation."""
    process = psutil.Process()
    mem_before = process.memory_info().rss / (1024 * 1024)
    start = time.perf_counter()

    result = func(*args, **kwargs)

    elapsed = time.perf_counter() - start
    mem_after = process.memory_info().rss / (1024 * 1024)

    return {
        "result": result,
        "time_seconds": elapsed,
        "memory_mb": mem_after - mem_before
    }

# Usage
baseline = measure_operation(process_original, data)
optimized = measure_operation(process_new, data)

speedup = baseline["time_seconds"] / optimized["time_seconds"]
print(f"Speedup: {speedup:.2f}x")
```

### Bitwise Verification

```python
import pandas as pd
import hashlib

def verify_identical(df_before, df_after, name="comparison"):
    """Verify two DataFrames are bitwise identical."""
    # Check dtypes match
    if df_before.dtypes.tolist() != df_after.dtypes.tolist():
        print(f"  WARNING: Dtype mismatch in {name}")
        print(f"    Before: {df_before.dtypes.tolist()}")
        print(f"    After: {df_after.dtypes.tolist()}")
        return False

    # Check exact equality
    if not df_before.equals(df_after):
        # Identify differences
        diff_cols = []
        for col in df_before.columns:
            if col in df_after.columns:
                if not df_before[col].equals(df_after[col]):
                    diff_cols.append(col)
        print(f"  ERROR: Values differ in {name}")
        print(f"    Different columns: {diff_cols}")
        return False

    print(f"  OK: Bitwise identical - {name}")
    return True

# Usage
verify_identical(before_df, after_df, "optimization test")
```

## Open Questions

1. **Q: Should we upgrade to pandas 3.0 for Copy-on-Write benefits?**
   - **What we know:** pandas 3.0 (January 2026) has 200% performance improvements for large operations
   - **What's unclear:** Full extent of breaking changes in our codebase
   - **Recommendation:** Defer pandas 3.0 upgrade to separate phase. It requires extensive testing due to semantic changes. Focus Phase 62 on pandas 2.2.3-compatible optimizations.

2. **Q: What's the optimal chunk_size for different operations?**
   - **What we know:** Current default is 10,000 rows from project.yaml
   - **What's unclear:** Whether this is optimal for all file sizes and operations
   - **Recommendation:** Use `shared/chunked_reader.py` memory-aware throttling. The existing `MemoryAwareThrottler` class already handles dynamic chunk sizing.

3. **Q: Can we use .update() instead of merge for bulk updates?**
   - **What we know:** `df.update()` exists for in-place updates
   - **What's unclear:** Whether it preserves index alignment correctly in all cases
   - **Recommendation:** Test `df.update()` pattern. It should be faster than merge for simple overwrites, but verify bitwise identical results first.

## Sources

### Primary (HIGH confidence)
- **pandas 2.2.3 Documentation**
  - User Guide: Enhancing Performance
  - API Reference: DataFrame.update(), DataFrame.merge()
  - URL: https://pandas.pydata.org/docs/2.2.3/

- **pandas 3.0.0 Release Notes**
  - Copy-on-Write semantics (future reference)
  - Performance improvements
  - URL: https://pandas.pydata.org/docs/whatsnew/v3.0.0.html

- **PyArrow 21.0.0 Documentation**
  - Tabular Datasets
  - Chunked reading
  - URL: https://arrow.apache.org/docs/21.0/python/

### Secondary (MEDIUM confidence)
- **8 Pandas Performance Hacks for 2026** (Medium, Captain Solaris, February 2026)
  - dtype optimization for strings and integers
  - New 2025-2026 engine improvements
  - URL: https://captain-solaris.medium.com/8-pandas-performance-hacks-for-2026-that-actually-work-0c47fd9d8a61

- **Pandas GroupBy Optimizations** (Medium, Hadi Yolworld, September 2025)
  - transform() preserves shape and index
  - Group results aligned to each row
  - URL: https://medium.com/@hadiyolworld007/pandas-groupby-optimizations-nobody-uses-86d224d67653

- **Vectorized Feature Engineering** (Medium, Harish Parmar, November 2024)
  - Stop looping over rows
  - Think in columns for performance
  - URL: https://medium.com/@hjparmar1944/pandas-vectorized-feature-engineering-turn-minutes-into-milliseconds-9b98c50acc8f

- **Optimizing pd.concat with Dictionaries** (Medium, Tz Hao Nj, 2024)
  - Dictionary-based concatenation vs repeated concat
  - Memory-efficient DataFrame construction
  - URL: https://medium.com/@tzhaonj/optimizing-pd-concat-with-dictionaries-for-efficient-data-processing-0c3dfec87161

### Tertiary (LOW confidence)
- Stack Overflow discussions on specific patterns
- General pandas performance blog posts (pre-2024)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries well-documented and current
- Architecture patterns: HIGH - Patterns verified against pandas 2.2.3 docs
- Pitfalls: HIGH - Based on well-known pandas gotchas
- Implementation priority: MEDIUM - Estimated based on typical patterns, actual profiling may differ

**Research date:** 2026-02-11
**Valid until:** 2026-03-13 (30 days for stable technologies)

**Current package versions (from requirements.txt):**
- pandas: 2.2.3
- numpy: 2.3.2
- pyarrow: 21.0.0
- psutil: 7.2.1

**Key constraint:** Optimizations must be compatible with pandas 2.2.3 (Python 3.8-3.13 compatible). pandas 3.0+ requires Python 3.10+ and has breaking changes.
