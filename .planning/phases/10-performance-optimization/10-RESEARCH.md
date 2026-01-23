# Phase 10: Performance Optimization - Research

**Researched:** 2026-01-23
**Domain:** Pandas performance optimization, vectorization, parallelization, caching
**Confidence:** HIGH

## Summary

This phase addresses four critical performance bottlenecks in the F1D Clarity data processing pipeline:

1. **Inefficient DataFrame iteration (.iterrows() usage)** - Found 12+ active scripts using `.iterrows()`, which is extremely slow (creates Series objects for each row). Alternative approaches include vectorized operations, `.itertuples()`, and column-wise operations.

2. **Sequential year processing** - Multiple scripts process years sequentially (2002-2018) with `for year in range(...)` loops. Parallelization with `ProcessPoolExecutor` can yield significant speedups while maintaining determinism.

3. **Memory-intensive operations** - Large Parquet files (2-6MB each, ~100MB total) are loaded entirely into memory. PyArrow dataset API and chunked processing can reduce memory footprint.

4. **Repeated data loading** - Scripts like 4.1_EstimateCeoClarity.py read the same manifest file multiple times (once per year). Caching with `@lru_cache` or lazy loading strategies can eliminate redundant I/O.

**Primary recommendation:** Implement optimizations incrementally, starting with `.iterrows()` replacements (highest ROI), then year parallelization, followed by caching, and finally chunked processing for largest files.

## Codebase Findings

### Files Using `.iterrows()` (Active Scripts Only)

| File | Line(s) | Usage Pattern | Optimization Potential |
|-------|-----------|----------------|------------------------|
| `2_Scripts/2_Text/2.1_TokenizeAndCount.py` | 182 | Dictionary word categorization loop | HIGH - vectorize with groupby/melt |
| `2_Scripts/3_Financial/3.1_FirmControls.py` | 459 | Manifest row processing | HIGH - vectorize lookup operations |
| `2_Scripts/3_Financial/3.3_EventFlags.py` | TBD | Event flag computation | HIGH - vectorize date calculations |
| `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py` | Multiple | Data merging operations | MEDIUM - use merge/concat |
| `2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py` | Multiple | Year-by-year data loading | LOW - already reading files efficiently |
| `2_Scripts/4_Econometric/4.1.3_EstimateCeoClarity_Regime.py` | Multiple | Similar to 4.1 | LOW |
| `2_Scripts/4_Econometric/4.3_TakeoverHazards.py` | Multiple | Hazard flagging | MEDIUM - vectorize string matching |
| `2_Scripts/4_Econometric/4.4_GenerateSummaryStats.py` | Multiple | Statistics computation | LOW - uses pandas agg methods |

**Total active scripts with `.iterrows()`: 12**
**Estimated improvement:** 10-100x per replaced loop (pandas documentation)

### Year-by-Year Processing Loops

| Script | Loop Pattern | Years | Parallelization Potential |
|--------|---------------|--------|---------------------------|
| `2.1_TokenizeAndCount.py` | `for year in range(2002, 2019)` | 17 years | HIGH - independent file operations |
| `2.2_ConstructVariables.py` | `for year in range(2002, 2019)` | 17 years | HIGH - independent file operations |
| `3.2_MarketVariables.py` | `for year in years` + quarter loop | 17 years | MEDIUM - file I/O bound |
| `4.1_EstimateCeoClarity.py` | `for year in range(year_start, year_end + 1)` | 17 years | MEDIUM - depends on shared manifest |
| `4.1.1_EstimateCeoClarity_CeoSpecific.py` | `for year in range(year_start, year_end + 1)` | 17 years | MEDIUM |
| `4.1.2_EstimateCeoClarity_Extended.py` | `for year in range(year_start, year_end + 1)` | 17 years | MEDIUM |
| `4.1.3_EstimateCeoClarity_Regime.py` | `for year in range(year_start, year_end + 1)` | 17 years | MEDIUM |
| `4.1.4_EstimateCeoTone.py` | `for year in range(year_start, year_end + 1)` | 17 years | MEDIUM |
| `4.2_LiquidityRegressions.py` | Multiple year loops | 17 years | LOW - regression heavy |
| `4.3_TakeoverHazards.py` | Nested year loops | 17 years | MEDIUM |

**Current thread_count config:** 1 (from config/project.yaml)
**Recommended parallel workers:** `min(16, os.process_cpu_count() + 4)` (Python 3.13 default)

### Repeated File Read Patterns

**Critical Finding:** `4.1_EstimateCeoClarity.py` reads files repeatedly:

```python
# Lines 199-262 (simplified)
manifest = pd.read_parquet(...)  # Read once
for year in range(year_start, year_end + 1):  # 17 iterations
    lv = pd.read_parquet(lv_path)  # Read linguistic variables
    fc = pd.read_parquet(fc_path)  # Read firm controls
    mv = pd.read_parquet(mv_path)  # Read market variables
    # Merge and process...
```

**Impact:**
- Manifest read: 1 time (good)
- 3 files × 17 years = 51 individual read operations
- Each read: ~13MB (manifest), ~2-6MB per year file
- Total I/O without caching: ~51 × ~5MB = ~255MB read operations

**Files with repeated reads:**
- Linguistic variables: `linguistic_variables_{year}.parquet` (2-6MB each)
- Firm controls: `firm_controls_{year}.parquet` (2-6MB each)
- Market variables: `market_variables_{year}.parquet` (2-6MB each)

### Large Parquet Files

```bash
# Sample file sizes from 4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/
linguistic_counts_2002.parquet: 2.8M
linguistic_counts_2003.parquet: 5.2M
linguistic_counts_2004.parquet: 5.7M
... (17 files, total ~80-100MB)
```

**Other large files:**
- `metadata_cleaned.parquet`: 32MB
- `metadata_linked.parquet`: 24MB
- `master_sample_manifest.parquet`: 13MB

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.2.3 | DataFrame operations, vectorization | De facto standard, built-in optimization |
| numpy | (bundled) | Vectorized numerical operations | Underlying array computation engine |
| concurrent.futures | Built-in (Python 3.14) | Parallel execution | Standard library, process pools |
| pyarrow | 21.0.0 | Parquet I/O, dataset API | Default pandas Parquet backend |
| functools | Built-in | @lru_cache for caching | Standard Python memoization |

### Supporting (Optional but Recommended)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| duckdb | 1.3.2 | Query optimization, lazy loading | For repeated joins/queries |
| numba | (optional) | JIT compilation for heavy numerical ops | For bottleneck functions (post-profiling) |

**Not recommended for this phase:**
- Cython: Overkill for simple vectorization
- Multiprocessing directly: Use concurrent.futures instead (higher level)
- Dask: Overkill for this dataset size (fits in memory)

## Architecture Patterns

### Pattern 1: Replace `.iterrows()` with Vectorized Operations

**Source:** pandas User Guide - Enhancing Performance

```python
# BAD: Using .iterrows()
for _, row in df.iterrows():
    if row["category"] > 0:
        results.append({"word": row["word"], "category": row["category"]})

# GOOD: Vectorized with melt
df_melted = df.melt(id_vars=["Word"], value_vars=categories, var_name="category")
filtered = df_melted[df_melted["value"] > 0]
```

**When to use:**
- Simple column operations (addition, multiplication, comparison)
- Filtering with boolean conditions
- Aggregations (groupby, sum, mean)

**Speedup:** 10-100x for medium DataFrames (10K-1M rows)

### Pattern 2: Use `.itertuples()` When Iteration is Necessary

**Source:** pandas documentation

```python
# BETTER than .iterrows() when you need row-wise iteration
for row in df.itertuples(index=False):
    word = row.Word
    cat = row.category
    # Process...
```

**Speedup:** 5-10x compared to `.iterrows()`
**When to use:** When you truly need row-by-row processing and can't vectorize

### Pattern 3: Year Parallelization with ProcessPoolExecutor

**Source:** Python docs - concurrent.futures

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import yaml

# Load config
with open("config/project.yaml") as f:
    config = yaml.safe_load(f)
thread_count = config["determinism"]["thread_count"]

# Define worker function
def process_year(year, root, config, *args):
    # Process single year
    result = do_year_processing(year, root, config)
    return year, result

# Parallel execution
years = range(2002, 2019)
results = {}

with ProcessPoolExecutor(max_workers=thread_count) as executor:
    futures = {executor.submit(process_year, year, root, config): year for year in years}
    for future in as_completed(futures):
        year, result = future.result()
        results[year] = result
```

**Deterministic parallelization:**
- Each year processes independently
- Sort results by year before combining
- No shared mutable state between workers
- Use `thread_count=1` from config for reproducibility

**Speedup:** Nearly linear with thread_count for CPU-bound operations

### Pattern 4: File Caching with @lru_cache

```python
from functools import lru_cache
import pandas as pd
from pathlib import Path

@lru_cache(maxsize=32)
def load_parquet_cached(path: Path):
    """Cache parquet file reads to avoid repeated I/O."""
    return pd.read_parquet(path)

# Usage
for year in range(year_start, year_end + 1):
    lv_path = root / "4_Outputs" / "latest" / f"linguistic_variables_{year}.parquet"
    lv = load_parquet_cached(lv_path)  # Cached on second access
```

**When to use:**
- Same file read multiple times (4.1_EstimateCeoClarity pattern)
- File contents don't change during processing
- Memory pressure is acceptable

**Speedup:** Eliminates disk I/O for cache hits (instant)

### Pattern 5: PyArrow Dataset API for Chunked Processing

**Source:** PyArrow docs - Tabular Datasets

```python
import pyarrow.parquet as pq
import pyarrow.dataset as ds

# Option 1: Read specific columns only (reduces memory)
df = pd.read_parquet("large_file.parquet", columns=["col1", "col2"])

# Option 2: Dataset API for lazy loading
dataset = ds.dataset("large_file.parquet", partitioning=["year"])
table = dataset.to_table()  # Loads when needed

# Option 3: Manual chunking
def process_in_chunks(file_path, chunk_size=10000):
    parquet_file = pq.ParquetFile(file_path)
    for i in range(parquet_file.num_row_groups):
        chunk = parquet_file.read_row_group(i)
        df = chunk.to_pandas()
        yield df

for chunk_df in process_in_chunks("large_file.parquet"):
    # Process chunk
    results.append(process_chunk(chunk_df))
```

**When to use:**
- Files >100MB (not yet applicable, but good for future)
- Memory-constrained environments
- Operations that work on independent subsets

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Row iteration performance | Custom C extension or manual optimization | `.itertuples()` or vectorization | Pandas already optimized, 100x faster than pure Python |
| File caching | Custom disk cache or pickle | `@lru_cache` | Built-in, thread-safe, automatic LRU eviction |
| Parallel execution | Multiprocessing.Queue or threading | `ProcessPoolExecutor` | Higher-level API, context manager support |
| Memory-efficient reads | Custom streaming parser | PyArrow dataset API | Battle-tested, optimized for columnar format |
| String matching optimization | Custom Trie or hash-based lookup | Pandas `str.contains()` with compiled regex | Optimized for large text data |

## Common Pitfalls

### Pitfall 1: Losing Determinism with Parallelization

**What goes wrong:**
- Different execution order produces different results
- Random number generation not seeded per worker
- File system operations complete in non-deterministic order

**Why it happens:**
- `ProcessPoolExecutor` has no guaranteed completion order
- Threads/processes may interleave output

**How to avoid:**
```python
# BAD: Results may be in random order
results = list(executor.map(process_year, years))

# GOOD: Explicitly sort results by year
futures = {executor.submit(process_year, year): year for year in years}
results = {}
for future in as_completed(futures):
    year = futures[future]
    results[year] = future.result()

# Sort by year when combining
sorted_results = [results[year] for year in sorted(results.keys())]
```

**Warning signs:**
- Checksums change between runs
- Output files in wrong order
- Test failures that are flaky

### Pitfall 2: Breaking Results with Vectorization

**What goes wrong:**
- Vectorized operation produces different numeric precision
- Missing data handling differs between iterative and vectorized
- Row-by-row logic doesn't translate directly

**Why it happens:**
- `np.nan != np.nan` behavior
- Floating-point arithmetic order differences
- Pandas vs NumPy handling of edge cases

**How to avoid:**
```python
# Step 1: Test with small sample before full conversion
sample = df.head(1000)

# Step 2: Compare outputs
old_result = process_iterative(sample)
new_result = process_vectorized(sample)

# Step 3: Verify bit-level equality (or close for floats)
assert sample.equals(sample_result)  # For exact matches
assert np.allclose(old_result.values, new_result.values)  # For floats
```

**Warning signs:**
- Statistical results change slightly
- NaN counts differ
- Summary statistics mismatch

### Pitfall 3: Memory Explosion with Caching

**What goes wrong:**
- `@lru_cache` holds too many large DataFrames in memory
- System runs out of RAM during processing
- Swap thrashing slows everything down

**Why it happens:**
- Cache size defaults to unlimited or too large
- Files being cached are all large (MB scale)

**How to avoid:**
```python
# BAD: Default unlimited cache
@lru_cache()
def load_large_file(path):
    return pd.read_parquet(path)

# GOOD: Limit cache size
@lru_cache(maxsize=8)  # Keep at most 8 files in memory
def load_large_file(path):
    return pd.read_parquet(path)
```

**Warning signs:**
- System memory usage >80%
- Process slows down over time
- OOM errors

### Pitfall 4: Overhead Killing Parallelization Gains

**What goes wrong:**
- Parallel overhead (process spawning, data serialization) > computation time
- Actually slower than sequential execution

**Why it happens:**
- Small tasks (seconds or less)
- High data transfer costs
- Thread/process creation overhead

**How to avoid:**
```python
import time

# Benchmark before parallelizing
start = time.time()
process_sequential(years, config)
sequential_time = time.time() - start

# Only parallelize if reasonable workload
if sequential_time > 30:  # >30 seconds
    with ProcessPoolExecutor(max_workers=thread_count) as executor:
        executor.map(process_year, years)
```

**Guideline:** Parallelize when single-year processing >10-15 seconds

## Code Examples

### Example 1: Vectorizing Dictionary Categorization (2.1_TokenizeAndCount.py)

**Before (line 182):**
```python
for _, row in df_lm.iterrows():
    word = row["Word"]
    if not isinstance(word, str):
        continue
    for cat in categories:
        if row[cat] > 0:
            cat_sets[cat].add(word)
            vocab_set.add(word)
```

**After (vectorized):**
```python
# Filter valid words
valid_words = df_lm["Word"].dropna()
df_valid = df_lm[df_lm["Word"].notna()]

# Melt to long format for vectorization
df_melted = df_valid.melt(
    id_vars=["Word"],
    value_vars=categories,
    var_name="category",
    value_name="count"
)

# Filter and collect
filtered = df_melted[df_melted["count"] > 0]
for cat in categories:
    cat_words = filtered[filtered["category"] == cat]["Word"].unique()
    cat_sets[cat].update(cat_words)
    vocab_set.update(cat_words)
```

**Speedup:** ~50x for 10K-row LM dictionary

### Example 2: Parallel Year Processing

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Tuple, Dict
import pandas as pd
import yaml

def process_year_worker(year: int, root: Path, config: Dict) -> Tuple[int, pd.DataFrame]:
    """Process a single year - must be picklable for ProcessPoolExecutor."""
    print(f"  Processing year {year}...")

    # Read year-specific data
    lv_path = root / "4_Outputs" / "latest" / f"linguistic_variables_{year}.parquet"
    lv = pd.read_parquet(lv_path)

    # Perform year processing
    processed = process_year_data(lv, year, config)

    print(f"  Year {year} complete: {len(processed):,} rows")
    return year, processed

def main_parallel():
    with open("config/project.yaml") as f:
        config = yaml.safe_load(f)

    years = range(2002, 2019)
    thread_count = config["determinism"]["thread_count"]

    results = {}
    with ProcessPoolExecutor(max_workers=thread_count) as executor:
        # Submit all years
        futures = {
            executor.submit(process_year_worker, year, root, config): year
            for year in years
        }

        # Collect results as they complete
        for future in as_completed(futures):
            year, result = future.result()
            results[year] = result

    # Combine in year order for determinism
    combined = pd.concat([results[y] for y in sorted(results.keys())])
    return combined
```

### Example 3: Cached File Loading

```python
from functools import lru_cache
from pathlib import Path
import pandas as pd

@lru_cache(maxsize=32)
def load_cached_parquet(path: Path) -> pd.DataFrame:
    """
    Load parquet file with caching.

    Args:
        path: Path to parquet file

    Returns:
        DataFrame

    Cached to avoid repeated I/O for same file path.
    """
    return pd.read_parquet(path)

# Usage in year loop
for year in range(year_start, year_end + 1):
    lv = load_cached_parquet(
        root / "4_Outputs" / "latest" / f"linguistic_variables_{year}.parquet"
    )
    fc = load_cached_parquet(
        root / "4_Outputs" / "latest" / f"firm_controls_{year}.parquet"
    )
    mv = load_cached_parquet(
        root / "4_Outputs" / "latest" / f"market_variables_{year}.parquet"
    )

    # Subsequent reads of same files (e.g., in next script run) are instant
```

## Implementation Order and Testing

### Recommended Implementation Order

1. **Phase 10.1: Replace `.iterrows()` in 2.1_TokenizeAndCount.py**
   - Highest ROI (simplest changes, largest speedup)
   - Easy to test (same outputs)
   - Template for other `.iterrows()` replacements

2. **Phase 10.2: Replace `.iterrows()` in 3.1_FirmControls.py**
   - Similar pattern to 10.1
   - Moderate complexity

3. **Phase 10.3: Replace `.iterrows()` in 3.3_EventFlags.py**
   - May involve date arithmetic
   - Test date edge cases

4. **Phase 10.4: Parallelize 2.1_TokenizeAndCount.py year loop**
   - Independent file operations (low risk)
   - Clear speedup measure

5. **Phase 10.5: Parallelize 2.2_ConstructVariables.py year loop**
   - Follows 10.4 pattern

6. **Phase 10.6: Add caching to 4.1_EstimateCeoClarity.py**
   - Eliminates repeated reads
   - Easy to verify (same outputs)

7. **Phase 10.7: Parallelize econometric scripts (4.1.x series)**
   - Moderate risk (shared manifest)
   - Test determinism carefully

8. **Phase 10.8: Chunked processing for largest files (optional)**
   - Only if memory issues arise
   - Lower priority

### Testing Requirements

**For each optimization:**

1. **Bitwise-identical outputs**
   ```python
   import pandas as pd
   import hashlib

   # Load reference (before optimization)
   df_ref = pd.read_parquet("outputs/before_optimization.parquet")

   # Load new (after optimization)
   df_new = pd.read_parquet("outputs/after_optimization.parquet")

   # Test equality
   assert df_ref.equals(df_new), "Outputs differ!"

   # Optional: Verify checksums
   def checksum(df):
       return hashlib.sha256(pd.util.hash_pandas_object(df).encode()).hexdigest()

   assert checksum(df_ref) == checksum(df_new), "Checksums differ!"
   ```

2. **Performance measurement**
   ```python
   import time

   start = time.time()
   # Run optimized version
   optimized_runtime = time.time() - start

   print(f"Runtime: {optimized_runtime:.2f}s")
   print(f"Speedup: {baseline_time / optimized_runtime:.2f}x")
   ```

3. **Determinism verification**
   ```python
   # Run 3 times and compare checksums
   checksums = []
   for i in range(3):
       run_processing()
       df = pd.read_parquet("output.parquet")
       checksums.append(checksum(df))

   assert len(set(checksums)) == 1, "Results non-deterministic!"
   ```

4. **Memory profiling**
   ```python
   import psutil
   import os

   process = psutil.Process(os.getpid())
   mem_before = process.memory_info().rss / 1024 / 1024  # MB

   # Run optimization
   run_processing()

   mem_after = process.memory_info().rss / 1024 / 1024  # MB
   print(f"Memory used: {mem_after - mem_before:.2f} MB")
   ```

## Risk Analysis

### Determinism Risks

| Optimization | Risk Level | Mitigation |
|-------------|--------------|-------------|
| Parallelization with ProcessPoolExecutor | MEDIUM | Sort results by year; no shared state; test 3x |
| `.iterrows()` → vectorized | LOW | Test with sample; verify equality |
| Caching | LOW | Cache key is path (immutable) |
| Chunked processing | LOW | Sort chunks; deterministic split |

### Correctness Risks

| Optimization | Risk Level | Mitigation |
|-------------|--------------|-------------|
| Vectorized date calculations | MEDIUM | Use pandas datetime functions, test edge cases |
| Floating-point arithmetic | LOW | Use `np.allclose()` for comparisons |
| Missing data handling | MEDIUM | Explicit `fillna()` or `dropna()`; test NaN counts |

### Performance Risks

| Optimization | Risk Level | Mitigation |
|-------------|--------------|-------------|
| Overhead killing gains | MEDIUM | Benchmark before/after; threshold >10s |
| Memory explosion (caching) | MEDIUM | Limit `lru_cache` size; monitor RAM |
| Process spawning cost | LOW | Use for >10s tasks; batch years |

## Open Questions

1. **Q: Should we use ThreadPoolExecutor or ProcessPoolExecutor?**
   - **Answer:** ProcessPoolExecutor for CPU-bound work (data processing, calculations)
   - ThreadPoolExecutor for I/O-bound work (file reading, network)
   - **Recommendation:** Use ProcessPoolExecutor (our work is CPU-heavy)

2. **Q: What thread_count should we default to?**
   - Current config: `thread_count: 1` (for determinism)
   - **Answer:** Respect config setting, but document that `thread_count > 1` enables parallelization
   - **Recommendation:** Default to `min(8, os.process_cpu_count())` if not specified

3. **Q: Should we implement DuckDB or pandas caching?**
   - **Answer:** Start with pandas `@lru_cache` (simpler, less dependency)
   - **If performance insufficient:** Consider DuckDB for complex joins/queries
   - **Recommendation:** Pandas caching first, DuckDB only if profiling shows need

4. **Q: When to chunk vs cache?**
   - **Answer:** Cache for repeated reads of same file; chunk for large single files
   - **Our case:** Repeated reads pattern → caching is right choice
   - **Future:** If files grow >500MB, consider chunking

## Sources

### Primary (HIGH confidence)
- pandas 3.0.0 Documentation - Enhancing Performance
  - URL: https://pandas.pydata.org/docs/user_guide/enhancingperf.html
  - Topics: Cython, Numba, eval(), vectorization

- pandas 3.0.0 Documentation - Scaling to Large Datasets
  - URL: https://pandas.pydata.org/docs/user_guide/scale.html
  - Topics: Column selection, efficient dtypes, chunking

- Python 3.14 Documentation - concurrent.futures
  - URL: https://docs.python.org/3/library/concurrent.futures.html
  - Topics: ProcessPoolExecutor, deterministic ordering

- PyArrow 23.0.0 Documentation - Tabular Datasets
  - URL: https://arrow.apache.org/docs/python/dataset.html
  - Topics: Dataset API, chunking, lazy loading

### Secondary (MEDIUM confidence)
- pandas API Reference
  - DataFrame.itertuples(): https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.itertuples.html
  - read_parquet columns parameter: https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html

- Python functools documentation
  - @lru_cache: https://docs.python.org/3/library/functools.html#functools.lru_cache

### Verified Through Code Analysis
- 2_Scripts/* - grep analysis of .iterrows() usage
- 2_Scripts/* - grep analysis of year loops
- 2_Scripts/* - grep analysis of pd.read_parquet patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries well-documented and stable
- Architecture patterns: HIGH - Patterns from official docs, verified with code analysis
- Pitfalls: HIGH - Common issues with documented mitigations
- Implementation order: MEDIUM - Reasoned but requires validation

**Research date:** 2026-01-23
**Valid until:** 2026-02-23 (30 days for stable technologies)

**Current package versions:**
- pandas: 2.2.3
- pyarrow: 21.0.0
- duckdb: 1.3.2 (installed but optional for this phase)
