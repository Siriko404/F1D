# Shared Utilities

This directory contains reusable utility modules for the F1D data pipeline.

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
