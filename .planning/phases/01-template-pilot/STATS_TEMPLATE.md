# Statistics Template Pattern

This document contains copy-paste ready Python code for implementing inline statistics in pipeline scripts.
This ensures consistency across all scripts while maintaining the no-shared-module constraint.

## 1. Stats Dictionary Schema
Initialize this at the start of `main()`:

```python
stats = {
    'step_id': '1.X_ScriptName',
    'timestamp': timestamp,
    'git_sha': get_git_sha(),  # optional helper
    'input': {
        'files': [],           # list of input file paths
        'checksums': {},       # {filename: sha256_hash}
        'total_rows': 0,
        'total_columns': 0
    },
    'processing': {},          # step-specific metrics (filters, transforms)
    'output': {
        'final_rows': 0,
        'final_columns': 0,
        'files': []            # list of output file names
    },
    'missing_values': {},      # {column: {'count': N, 'percent': X.X}}
    'timing': {
        'start_iso': '',
        'end_iso': '',
        'duration_seconds': 0.0
    }
}
```

## 2. Helper: compute_file_checksum()
Use this to generate SHA256 checksums for input files to ensure data provenance.

```python
import hashlib

def compute_file_checksum(filepath, algorithm='sha256'):
    """Compute checksum for a file."""
    h = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()
```

## 3. Helper: print_stat()
Use this for consistent metric printing during execution.
Supports delta mode (showing change) and simple value mode.

```python
def print_stat(label, before=None, after=None, value=None, indent=2):
    """Print a statistic with consistent formatting.
    
    Modes:
        - Delta mode (before/after): "  Label: 1,000 -> 800 (-20.0%)"
        - Value mode: "  Label: 1,000"
    """
    prefix = " " * indent
    if before is not None and after is not None:
        delta = after - before
        pct = (delta / before * 100) if before != 0 else 0
        sign = "+" if delta >= 0 else ""
        print(f"{prefix}{label}: {before:,} -> {after:,} ({sign}{pct:.1f}%)")
    else:
        v = value if value is not None else after
        if isinstance(v, float):
            print(f"{prefix}{label}: {v:,.2f}")
        elif isinstance(v, int):
            print(f"{prefix}{label}: {v:,}")
        else:
            print(f"{prefix}{label}: {v}")
```

## 4. Helper: analyze_missing_values()
Use this before saving output to capture data quality metrics.

```python
def analyze_missing_values(df):
    """Analyze missing values per column."""
    missing = {}
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            missing[col] = {
                'count': int(null_count),
                'percent': round(null_count / len(df) * 100, 2)
            }
    return missing
```

## 5. Helper: print_stats_summary()
Call this at the very end of the script to show a standardized ASCII summary table.

```python
def print_stats_summary(stats):
    """Print formatted summary table."""
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)
    
    # Input/Output comparison
    inp = stats['input']
    out = stats['output']
    delta = inp['total_rows'] - out['final_rows']
    delta_pct = (delta / inp['total_rows'] * 100) if inp['total_rows'] > 0 else 0
    
    print(f"\n{'Metric':<25} {'Value':>15}")
    print("-" * 42)
    print(f"{'Input Rows':<25} {inp['total_rows']:>15,}")
    print(f"{'Output Rows':<25} {out['final_rows']:>15,}")
    print(f"{'Rows Removed':<25} {delta:>15,}")
    print(f"{'Removal Rate':<25} {delta_pct:>14.1f}%")
    print(f"{'Duration (seconds)':<25} {stats['timing']['duration_seconds']:>15.2f}")
    
    # Processing breakdown if available
    if stats['processing']:
        print(f"\n{'Processing Step':<30} {'Removed':>10}")
        print("-" * 42)
        for step, count in stats['processing'].items():
            print(f"{step:<30} {count:>10,}")
    
    print("=" * 60)
```

## 6. Helper: save_stats()
Call this to write the machine-readable JSON record.

```python
import json

def save_stats(stats, out_dir):
    """Save statistics to JSON file."""
    stats_path = out_dir / 'stats.json'
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")
```

## 7. Pattern: Timing wrapper
Wrap your main execution flow with this timing logic.

```python
import time
from datetime import datetime

# At start of main():
start_time = time.perf_counter()
start_iso = datetime.now().isoformat()

# At end of main(), before save:
end_time = time.perf_counter()
stats['timing'] = {
    'start_iso': start_iso,
    'end_iso': datetime.now().isoformat(),
    'duration_seconds': round(end_time - start_time, 2)
}
```

## 8. Pattern: Merge diagnostics (Template)
For scripts that perform joins, add this structure to the stats dictionary.

```python
# For scripts that perform merges/joins:
stats['merges'] = {
    'merge_name': {
        'left_rows': len(df_left),
        'right_rows': len(df_right),
        'result_rows': len(df_merged),
        'matched': matched_count,
        'unmatched_left': unmatched_left,
        'unmatched_right': unmatched_right,
        'merge_type': '1:1'  # or '1:m', 'm:1', 'm:m'
    }
}
```
