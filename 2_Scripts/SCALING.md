# Scaling Documentation

**Created:** 2026-01-24
**Phase:** 15 - Scaling Preparation
**Status:** Complete

## Overview

This document describes the current capacity of the F1D data pipeline and provides paths for scaling to larger datasets. The pipeline is designed for academic replication with determinism and reproducibility as core requirements.

**Current scope:** ~50K transcripts (2002-2018), ~25M total rows
**Phase 15 focus:** Memory monitoring, parallel processing, column pruning, and memory-aware throttling

## Current Limits (As of Phase 15)

### Dataset Size Limits

| Metric | Value | Notes |
|--------|-------|-------|
| **Transcripts** | ~50K transcripts | 2002-2018 CEO call transcripts |
| **Rows per transcript** | ~500 average | Varies by call duration |
| **Total rows** | ~25M rows | Across all pipeline steps |
| **Parquet file sizes** | 100MB - 1GB per year | Annual transcript data |
| **CRSP/Compustat data** | ~5GB total | Financial controls |

### Memory Requirements

| System | RAM | Use Case | Notes |
|--------|-----|----------|-------|
| **Minimum** | 8GB RAM | Small steps, partial pipeline | May struggle with Step 1.2 (entity linking) |
| **Recommended** | 16GB RAM | Full pipeline, all steps | Current standard for complete analysis |
| **Peak memory** | ~4GB | During entity linking (1.2) | Fuzzy matching is most memory-intensive |

### Processing Time

| Metric | Value | Notes |
|--------|-------|-------|
| **Full pipeline** | ~2-4 hours | On modern hardware (i7 CPU, SSD) |
| **Per step** | 5-30 minutes | Varies by complexity |
| **Parallelization** | Single-threaded | `thread_count=1` in config (default) |
| **Bottleneck** | Step 1.2 (entity linking) | Fuzzy matching is O(n²) |

## Scaling Improvements (Phase 15)

### 1. Deterministic Parallelization (15-01)

**Status:** **Planned** - Prototype available in git history

**Note:** The `parallel_utils.py` module was prototyped in Phase 15 but not integrated into the codebase. It can be resurrected from git history for future scaling work.

**Planned Components:**
- `create_worker_seed(root_seed, worker_id)` - Deterministic seed for each worker
- `ThreadPoolExecutor` wrapper - Maintains reproducibility in parallel execution

**Intended Benefit:** Parallel workers maintain reproducibility (same input → same output)

**When to Use (Future):** Add ProcessPoolExecutor to CPU-bound operations

**Planned Examples:**
- Tokenization (2.1): Split transcript text across workers
- Fuzzy matching (1.2): Parallel candidate scoring
- Bootstrapping (Step 4): Parallel coefficient estimation

**Configuration:** `config/project.yaml > determinism > thread_count`

```yaml
determinism:
  thread_count: 4  # Number of parallel workers (default: 1)
```

---

### 2. Column Pruning (15-02)

**What Added:** Column-specific Parquet reads in 13 critical scripts

**Scripts using column pruning:**
- 1.0, 1.2, 1.3, 1.4 (Step 1 - Sample building)
- 2.1 (Step 2 - Tokenization)
- 3.0, 3.1, 3.2, 3.3 (Step 3 - Financial features)
- 4.1, 4.1.1, 4.1.2, 4.1.3 (Step 4 - Regressions)

**Benefit:** 30-50% memory reduction for large files

**When to Use:** When scripts need subset of columns

**Example:** Entity linking (1.2) only reads name columns, not full transcript text

**Implementation:**
```python
# Before (reads all columns)
df = pd.read_parquet(input_path)

# After (reads only needed columns)
df = pd.read_parquet(input_path, columns=['gvkey', 'coname'])
```

---

### 3. Memory-Aware Throttling (15-03)

**What Added:** `MemoryAwareThrottler` class in `shared/chunked_reader.py`

**Components:**
- `get_available_memory_mb()` - Total system memory
- `get_memory_usage_mb()` - Current process memory
- `get_memory_percent()` - Percent of system memory used
- `should_throttle()` - Check if throttling is needed
- `get_recommended_chunk_size()` - Dynamic chunk size based on memory
- `log_memory_status()` - Periodic memory logging

**Benefit:** Automatic chunk size adjustment based on memory pressure

**Configuration:** `config/project.yaml > chunk_processing`

```yaml
chunk_processing:
  max_memory_percent: 80.0    # Throttle when process exceeds 80%
  base_chunk_size: 10000       # Default chunk size (rows)
  enable_throttling: true      # Enable dynamic throttling
  log_memory_status: false     # Verbose logging (for debugging)
```

**When to Use:** Processing files >10GB on <32GB RAM systems

**Documentation:** [shared/chunked_reader.py](shared/chunked_reader.py)

---

### 4. Enhanced Memory Tracking (15-04)

**What Added:** `track_memory_usage` decorator, `memory_mb` in stats.json

**Components:**
- `@track_memory_usage` decorator - Tracks start/end/peak/delta memory
- Returns dict with `result`, `memory_mb`, `timing_seconds`
- Builds on Phase 12's `get_process_memory_mb()` pattern

**Benefit:** Identify memory-intensive operations

**When to Use:** All scripts processing large datasets

**Output in stats.json:**
```json
{
  "memory_mb": {
    "start": 125.3,
    "end": 847.2,
    "peak": 912.5,
    "delta": 721.9
  }
}
```

---

## Scaling Paths by Use Case

### Path A: 2x Dataset Size (~100K transcripts)

**Current:** 50K transcripts, 16GB RAM sufficient

**Improvements:**

1. **Enable parallel processing**
   ```yaml
   determinism:
     thread_count: 4  # or 8 on 8-core systems
   ```

2. **Increase chunk size**
   ```yaml
   chunk_processing:
     base_chunk_size: 50000  # Larger chunks for more throughput
   ```

3. **Add column pruning to remaining scripts**
   - 2.2 (Construct Variables)
   - 2.3 (Verify Step 2)
   - 3.x (Financial features scripts not yet using column pruning)

4. **Monitor memory**
   - Check `stats.json > memory_mb` for operation-level tracking
   - Set `log_memory_status: true` for verbose logging

**Expected:** 16GB RAM still sufficient, ~1.5x processing time (3-6 hours)

---

### Path B: 10x Dataset Size (~500K transcripts)

**Current:** 50K transcripts, 16GB recommended

**Improvements:**

1. **Enable parallel processing**
   ```yaml
   determinism:
     thread_count: 8  # Maximize parallelization
   ```

2. **Aggressive throttling**
   ```yaml
   chunk_processing:
     max_memory_percent: 60.0  # Lower threshold to prevent OOM
   ```

3. **Smaller chunk size**
   ```yaml
   chunk_processing:
     base_chunk_size: 5000  # Smaller chunks to reduce memory pressure
   ```

4. **Column pruning everywhere**
   - Add to all scripts reading Parquet files
   - Example: Regression scripts only load needed columns (gvkey, fyear, controls)

5. **PyArrow Dataset API for lazy loading**
   ```python
   import pyarrow.dataset as ds
   dataset = ds.dataset(input_path)
   df = dataset.to_table(columns=['gvkey', 'coname']).to_pandas()
   ```

6. **Faster storage**
   - Use SSD instead of HDD
   - Consider NVMe for high-throughput I/O

**Expected:** 32GB RAM required, ~3x processing time (6-12 hours)

---

### Path C: 100x Dataset Size (~5M transcripts)

**Current:** Not feasible (would exceed memory)

**Major Changes Required:**

1. **Switch to distributed processing**
   - **Dask:** Pandas-like API with distributed computation
   - **Ray:** Distributed execution framework for ML/Data
   - Both provide fault-tolerant, scalable processing

2. **Incremental database storage**
   - **PostgreSQL/ClickHouse:** Store data incrementally
   - Query subsets instead of loading full datasets
   - Supports time-series partitioning by year/quarter

3. **Stream processing architecture**
   - **Apache Flink:** Real-time stream processing
   - **Spark Streaming:** Batch + streaming hybrid
   - Revisit pipeline design for streaming vs batch

4. **Architectural redesign**
   - Batch processing may not scale to 100x
   - Consider incremental updates (new transcripts only)
   - Separate ETL from analysis layers

**Note:** This requires significant architectural changes beyond Phase 15 scope.

---

## Configuration Recommendations

### Small System (8GB RAM)

```yaml
# config/project.yaml
determinism:
  thread_count: 1  # Single-threaded to save memory

chunk_processing:
  max_memory_percent: 70.0  # Conservative threshold
  base_chunk_size: 5000     # Smaller chunks
  enable_throttling: true   # Enable throttling
  log_memory_status: true   # Verbose logging for debugging
```

**Use case:** Partial pipeline, small dataset subsets, development/testing

---

### Medium System (16GB RAM - Current Standard)

```yaml
# config/project.yaml
determinism:
  thread_count: 1  # Single-threaded (default)

chunk_processing:
  max_memory_percent: 80.0  # Default threshold
  base_chunk_size: 10000    # Default chunk size
  enable_throttling: true   # Enable throttling
  log_memory_status: false  # Minimal logging
```

**Use case:** Full pipeline, current dataset sizes (~50K transcripts)

---

### Large System (32GB RAM - 2x-5x datasets)

```yaml
# config/project.yaml
determinism:
  thread_count: 4  # Parallel processing

chunk_processing:
  max_memory_percent: 85.0  # Higher threshold
  base_chunk_size: 50000    # Larger chunks for throughput
  enable_throttling: true   # Enable throttling
  log_memory_status: false  # Minimal logging
```

**Use case:** 2x-10x datasets, multiple runs, production workloads

---

## Bottleneck Analysis

### Current Bottlenecks (Identified in Phase 15)

| Step | Script | Bottleneck | Severity | Improvement Priority |
|------|--------|------------|----------|---------------------|
| 1.2 | LinkEntities | Fuzzy matching O(n²) | HIGH | Parallelization, better indexing |
| 2.1 | TokenizeAndCount | Text processing memory-intensive | MEDIUM | Chunking, streaming |
| 3.2 | MarketVariables | CRSP data I/O intensive | MEDIUM | PyArrow Dataset API, SSD |
| 1.4 | AssembleManifest | Large intermediate results | MEDIUM | Incremental writes, column pruning |

### Improvement Priority

1. **High:** Add parallelization to fuzzy matching (1.2)
    - Implement deterministic parallel RNG (prototype available in git history)
    - Score candidates in parallel across workers
    - Expected: 2-4x speedup on 4-8 core systems

2. **Medium:** Add chunking to tokenization (2.1)
   - Use `shared/chunked_reader.py` for memory-aware processing
   - Process transcripts in chunks to reduce peak memory
   - Expected: 30-50% memory reduction

3. **Medium:** Add column pruning to remaining scripts
   - 2.2 (Construct Variables) - Only load needed columns
   - 2.3 (Verify Step 2) - Only load needed columns
   - 3.x (Financial features) - Already partially done

4. **Low:** Optimize merge operations
   - Requires data structure changes (more complex)
   - Consider incremental updates instead of full rebuilds
   - Expected: 10-20% speedup

---

## Monitoring and Debugging

### Memory Monitoring

**Check operation-level memory:**
```bash
# View memory usage for each operation
cat 4_Outputs/2.<step>_<Name>/latest/stats.json | jq '.memory_mb'
```

**Use MemoryAwareThrottler for real-time tracking:**
```python
from shared.chunked_reader import MemoryAwareThrottler
throttler = MemoryAwareThrottler(config)
throttler.log_memory_status()  # Print current memory status
```

**Enable verbose logging:**
```yaml
# config/project.yaml
chunk_processing:
  log_memory_status: true  # Log every 10 chunks + start/end
```

---

### Performance Monitoring

**Check total processing time:**
```bash
# View processing duration
cat 4_Outputs/2.<step>_<Name>/latest/stats.json | jq '.processing_duration'
```

**Use track_memory_usage decorator:**
```python
from shared.chunked_reader import track_memory_usage

@track_memory_usage
def process_chunk(chunk):
    # Processing logic here
    return result
```

**Benchmark different chunk sizes:**
```bash
# Test with 1K, 5K, 10K, 50K rows
# Modify config/project.yaml > chunk_processing > base_chunk_size
# Run script and compare processing_duration
```

---

### Troubleshooting OOM Errors

**Symptoms:** `MemoryError`, process killed by OOM killer

**Troubleshooting steps:**

1. **Reduce max_memory_percent**
   ```yaml
   chunk_processing:
     max_memory_percent: 60.0  # More conservative
   ```

2. **Reduce base_chunk_size**
   ```yaml
   chunk_processing:
     base_chunk_size: 2500  # Half the current size
   ```

3. **Add column pruning**
   ```python
   # Only load columns you need
   df = pd.read_parquet(input_path, columns=['gvkey', 'coname'])
   ```

4. **Disable parallel processing**
   ```yaml
   determinism:
     thread_count: 1  # Single-threaded
   ```

5. **Upgrade RAM or use larger machine**
   - Minimum: 8GB RAM
   - Recommended: 16GB RAM
   - Large datasets: 32GB+ RAM

**Enable verbose logging to diagnose:**
```yaml
chunk_processing:
  log_memory_status: true  # See memory at each chunk
```

---

## References

### External Documentation

- **NumPy Parallel RNG:** https://numpy.org/doc/stable/reference/random/parallel.html
- **PyArrow Dataset API:** https://arrow.apache.org/docs/python/dataset.html
- **Dask Documentation:** https://docs.dask.org/
- **Ray Documentation:** https://docs.ray.io/

### Internal Documentation

- **[Phase 15-RESEARCH.md](.planning/phases/15-scaling-preparation/15-RESEARCH.md)** - Scaling research and patterns
- **[config/project.yaml](../../config/project.yaml)** - Configuration parameters
- **[DEPENDENCIES.md](../../.planning/DEPENDENCIES.md)** - Dependency documentation
- **[UPGRADE_GUIDE.md](../../.planning/UPGRADE_GUIDE.md)** - Upgrade procedures

### Shared Modules

- **[chunked_reader.py](shared/chunked_reader.py)** - Memory-aware chunked processing
- **Note:** Deterministic parallel RNG was prototyped in Phase 15 but not integrated (available in git history)

### Phase 15 Plans

- **[15-01-SUMMARY.md](.planning/phases/15-scaling-preparation/15-01-SUMMARY.md)** - Deterministic Parallel RNG
- **[15-02-SUMMARY.md](.planning/phases/15-scaling-preparation/15-02-SUMMARY.md)** - PyArrow Column Pruning
- **[15-03-SUMMARY.md](.planning/phases/15-scaling-preparation/15-03-SUMMARY.md)** - Memory-Aware Throttling
- **[15-04-SUMMARY.md](.planning/phases/15-scaling-preparation/15-04-SUMMARY.md)** - Memory Tracking Infrastructure

---

**Last Updated:** 2026-01-24 (Phase 15 completion)
**Version:** 1.0
