#!/usr/bin/env python3
"""
==============================================================================
STEP 1.1: Clean Metadata & Event Filtering
==============================================================================
ID: 1.1_CleanMetadata
Description: Loads Unified-info, deduplicates exact rows, resolves file_name
             collisions, and filters for earnings calls (event_type='1') in
             the target date range (2002-2018).

Inputs:
    - 1_Inputs/Unified-info.parquet
    - config/project.yaml

Outputs:
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/variable_reference.csv
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/report_step_1_1.md
    - 3_Logs/1.1_CleanMetadata/{timestamp}.log

Deterministic: true
==============================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import shutil
import time
import json
import hashlib
import importlib.util
import sys
from pathlib import Path
import psutil

# Dynamic import for 1.5_Utils.py to comply with naming convention
# (Python modules cannot start with numbers, so we use importlib)
utils_path = Path(__file__).parent / "1.5_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)

from utils import generate_variable_reference
from shared.symlink_utils import update_latest_link

# Import shared validation module (for opt-in data validation)
try:
    from shared.data_validation import load_validated_parquet
except ImportError:
    # Fallback if shared/__init__.py hasn't run yet
    import sys as _sys
    from pathlib import Path as _Path

    _script_dir = _Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.data_validation import load_validated_parquet

# ==============================================================================
# Dual-write logging utility
# ==============================================================================


class DualWriter:
    """Writes to both stdout and log file verbatim"""

    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


def print_dual(msg):
    """Print to both terminal and log"""
    print(msg, flush=True)


# ==============================================================================
# Statistics Helpers
# ==============================================================================


def compute_file_checksum(filepath, algorithm="sha256"):
    """Compute checksum for a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


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


def analyze_missing_values(df):
    """Analyze missing values per column."""
    missing = {}
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            missing[col] = {
                "count": int(null_count),
                "percent": round(null_count / len(df) * 100, 2),
            }
    return missing


def print_stats_summary(stats):
    """Print formatted summary table."""
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)

    # Input/Output comparison
    inp = stats["input"]
    out = stats["output"]
    delta = inp["total_rows"] - out["final_rows"]
    delta_pct = (delta / inp["total_rows"] * 100) if inp["total_rows"] > 0 else 0

    print(f"\n{'Metric':<25} {'Value':>15}")
    print("-" * 42)
    print(f"{'Input Rows':<25} {inp['total_rows']:>15,}")
    print(f"{'Output Rows':<25} {out['final_rows']:>15,}")
    print(f"{'Rows Removed':<25} {delta:>15,}")
    print(f"{'Removal Rate':<25} {delta_pct:>14.1f}%")
    if "duration_seconds" in stats["timing"]:
        print(
            f"{'Duration (seconds)':<25} {stats['timing']['duration_seconds']:>15.2f}"
        )

    # Processing breakdown if available
    if stats["processing"]:
        print(f"\n{'Processing Step':<30} {'Removed':>10}")
        print("-" * 42)
        for step, count in stats["processing"].items():
            print(f"{step:<30} {count:>10,}")

    print("=" * 60)


def save_stats(stats, out_dir):
    """Save statistics to JSON file."""
    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


# ==============================================================================
# Observability Helpers
# ==============================================================================


def get_process_memory_mb():
    """
    Get current process memory usage in MB.

    Returns:
        Dict with keys:
        - rss_mb: Resident Set Size (actual physical memory in use)
        - vms_mb: Virtual Memory Size (total memory allocated)
        - percent: Memory usage as percentage of system memory
    """
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_percent = process.memory_percent()

    return {
        "rss_mb": mem_info.rss / (1024 * 1024),  # Resident Set Size
        "vms_mb": mem_info.vms / (1024 * 1024),  # Virtual Memory Size
        "percent": mem_percent,
    }


def calculate_throughput(rows_processed, duration_seconds):
    """
    Calculate throughput in rows per second.

    Args:
        rows_processed: Number of rows processed
        duration_seconds: Duration in seconds

    Returns:
        Throughput in rows per second (rounded to 2 decimals)
        Returns 0.0 if duration_seconds <= 0 to avoid division by zero
    """
    if duration_seconds <= 0:
        return 0.0
    return round(rows_processed / duration_seconds, 2)


def detect_anomalies_zscore(df, columns, threshold=3.0):
    """
    Detect anomalies using z-score (standard deviation) method.

    Deterministic: Same input produces same output.

    Args:
        df: DataFrame to analyze
        columns: List of column names to analyze
        threshold: Number of standard deviations for cutoff (default 3.0)

    Returns:
        Dict mapping column_name -> anomaly info
    """
    anomalies = {}

    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue

        # Drop NaN for z-score calculation
        series = df[col].dropna()

        if len(series) == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        mean = series.mean()
        std = series.std()

        if std == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        # Calculate z-scores: (value - mean) / std
        z_scores = abs((series - mean) / std)

        # Flag anomalies beyond threshold
        anomaly_mask = z_scores > threshold
        anomaly_indices = df[anomaly_mask].index.tolist()

        anomalies[col] = {
            "count": int(anomaly_mask.sum()),
            "sample_anomalies": anomaly_indices[:10],  # Top 10 for review
            "threshold": threshold,
            "mean": round(mean, 4),
            "std": round(std, 4),
        }

    return anomalies


def detect_anomalies_iqr(df, columns, multiplier=3.0):
    """
    Detect anomalies using IQR (Interquartile Range) method.

    Deterministic: Same input produces same output.

    Args:
        df: DataFrame to analyze
        columns: List of column names to analyze
        multiplier: IQR multiplier for cutoff (default 3.0 = strong outliers)

    Returns:
        Dict mapping column_name -> anomaly info
    """
    anomalies = {}

    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue

        # Drop NaN for IQR calculation
        series = df[col].dropna()

        if len(series) == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        # Calculate IQR: Q3 - Q1 (75th - 25th percentile)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        # Flag anomalies
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        anomaly_mask = (series < lower_bound) | (series > upper_bound)
        anomaly_indices = df[anomaly_mask].index.tolist()

        anomalies[col] = {
            "count": int(anomaly_mask.sum()),
            "sample_anomalies": anomaly_indices[:10],
            "iqr_bounds": [round(lower_bound, 4), round(upper_bound, 4)],
        }

    return anomalies


# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================


def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_paths(config):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    paths = {
        "root": root,
        "unified_info": root / "1_Inputs" / "Unified-info.parquet",
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config["paths"]["outputs"] / "1.1_CleanMetadata"
    paths["output_dir"] = output_base / timestamp
    paths["output_dir"].mkdir(parents=True, exist_ok=True)

    paths["latest_dir"] = output_base / "latest"

    # Create log directory
    log_base = root / config["paths"]["logs"] / "1.1_CleanMetadata"
    log_base.mkdir(parents=True, exist_ok=True)
    paths["log_file"] = log_base / f"{timestamp}.log"

    return paths, timestamp


# Variable reference generation and symlink handling imported from step1_utils

# ==============================================================================
# Main processing
# ==============================================================================


def main():
    """Main processing function"""

    # Load config
    config = load_config()
    paths, timestamp = setup_paths(config)

    # Setup dual logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    # Initialize timing
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()

    # Memory tracking at script start
    mem_start = get_process_memory_mb()
    all_memory_values = [mem_start["rss_mb"]]

    # Initialize stats collector
    stats = {
        "step_id": "1.1_CleanMetadata",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "timing": {},
    }

    print_dual("=" * 80)
    print_dual("STEP 1.1: Clean Metadata & Event Filtering")
    print_dual("=" * 80)
    print_dual(f"Timestamp: {timestamp}")
    print_dual(f"Output Directory: {paths['output_dir']}")
    print_dual("")

    # Load Unified-info with schema validation
    print_dual("Loading Unified-info.parquet...")
    df = load_validated_parquet(
        paths["unified_info"], schema_name="Unified-info.parquet", strict=True
    )
    original_count = len(df)

    # Record input stats
    input_checksum = compute_file_checksum(paths["unified_info"])
    stats["input"]["files"].append(str(paths["unified_info"].name))
    stats["input"]["checksums"][str(paths["unified_info"].name)] = input_checksum
    stats["input"]["total_rows"] = original_count
    stats["input"]["total_columns"] = len(df.columns)

    print_stat("Input file checksum (SHA256)", value=input_checksum[:16] + "...")
    print_stat("Input rows", value=original_count)
    print_stat("Input columns", value=len(df.columns))

    # Deduplication: Exact duplicates
    print_dual("\nStep 1: Removing exact duplicate rows...")
    df_dedup = df.drop_duplicates()
    exact_dupes = original_count - len(df_dedup)
    stats["processing"]["exact_duplicates_removed"] = exact_dupes
    print_dual(f"  Removed {exact_dupes:,} exact duplicate rows")
    print_dual(f"  Remaining: {len(df_dedup):,} rows")

    # Memory tracking after deduplication
    mem_after_dedup = get_process_memory_mb()
    all_memory_values.append(mem_after_dedup["rss_mb"])

    # Resolve file_name collisions
    resolved = 0  # Initialize for stats tracking
    print_dual("\nStep 2: Resolving file_name collisions...")
    collision_mask = df_dedup.duplicated(subset=["file_name"], keep=False)
    collisions = df_dedup[collision_mask].copy()

    if len(collisions) > 0:
        print_dual(
            f"  Found {collisions['file_name'].nunique():,} file_names with multiple rows"
        )

        # Sort by validation_timestamp and keep first
        collisions_sorted = collisions.sort_values(
            ["file_name", "validation_timestamp"]
        )
        keep_indices = collisions_sorted.groupby("file_name").head(1).index

        # Remove all collisions, then add back the kept ones
        df_clean = df_dedup[~collision_mask].copy()
        df_clean = pd.concat([df_clean, df_dedup.loc[keep_indices]], ignore_index=True)

        resolved = len(collisions) - len(keep_indices)
        print_dual(
            f"  Resolved {resolved:,} collision rows (kept earliest validation_timestamp)"
        )
    else:
        df_clean = df_dedup.copy()
        print_dual("  No file_name collisions found")

    stats["processing"]["collision_rows_resolved"] = resolved
    print_dual(f"  Remaining: {len(df_clean):,} rows")

    # Memory tracking after collision resolution
    mem_after_collision = get_process_memory_mb()
    all_memory_values.append(mem_after_collision["rss_mb"])

    # Event Filter: event_type == '1'
    print_dual("\nStep 3: Filtering for earnings calls (event_type='1')...")
    non_earnings_removed = 0  # Initialize for stats tracking
    if "event_type" not in df_clean.columns:
        print_dual("  WARNING: 'event_type' column not found. Skipping event filter.")
        df_filtered = df_clean.copy()
    else:
        df_filtered = df_clean[df_clean["event_type"] == "1"].copy()
        non_earnings_removed = len(df_clean) - len(df_filtered)
        print_dual(f"  Removed {non_earnings_removed:,} non-earnings calls")
        print_dual(f"  Remaining: {len(df_filtered):,} rows")

    stats["processing"]["non_earnings_removed"] = non_earnings_removed

    # Temporal Filter: 2002-2018
    print_dual("\nStep 4: Filtering for years 2002-2018...")
    year_start = config["data"].get("year_start", 2002)
    year_end = config["data"].get("year_end", 2018)

    df_filtered["start_date"] = pd.to_datetime(df_filtered["start_date"])
    df_filtered["year"] = df_filtered["start_date"].dt.year

    df_final = df_filtered[
        (df_filtered["year"] >= year_start) & (df_filtered["year"] <= year_end)
    ].copy()
    removed = len(df_filtered) - len(df_final)
    print_dual(f"  Removed {removed:,} rows outside {year_start}-{year_end} range")
    print_dual(f"  Final count: {len(df_final):,} rows")

    stats["processing"]["out_of_range_removed"] = removed

    # Drop temporary year column
    df_final = df_final.drop(columns=["year"])

    # Memory tracking after filtering
    mem_after_filter = get_process_memory_mb()
    all_memory_values.append(mem_after_filter["rss_mb"])

    # Record missing values and output stats
    stats["missing_values"] = analyze_missing_values(df_final)
    stats["output"]["final_rows"] = len(df_final)
    stats["output"]["final_columns"] = len(df_final.columns)

    # Save output
    output_file = paths["output_dir"] / "metadata_cleaned.parquet"
    df_final.to_parquet(output_file, index=False)
    print_dual(f"\nSaved cleaned metadata: {output_file}")

    # Generate variable reference
    var_ref_file = paths["output_dir"] / "variable_reference.csv"
    generate_variable_reference(df_final, var_ref_file, print_dual)

    # Finalize timing and save stats
    end_time = time.perf_counter()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 3)
    stats["timing"]["end_time"] = datetime.now().isoformat()
    stats["timing"]["start_time"] = start_iso

    # Memory tracking at script end
    mem_end = get_process_memory_mb()
    all_memory_values.append(mem_end["rss_mb"])

    # Add memory stats to stats
    stats["memory"] = {
        "start_mb": round(mem_start["rss_mb"], 2),
        "end_mb": round(mem_end["rss_mb"], 2),
        "peak_mb": round(max(all_memory_values), 2),
        "delta_mb": round(mem_end["rss_mb"] - mem_start["rss_mb"], 2),
    }

    # Add throughput to stats
    duration_seconds = end_time - start_time
    throughput = calculate_throughput(stats["output"]["final_rows"], duration_seconds)
    stats["throughput"] = {
        "rows_per_second": throughput,
        "total_rows": stats["output"]["final_rows"],
        "duration_seconds": round(duration_seconds, 3),
    }

    # Add output checksums
    stats["output"]["checksums"] = {}
    for filepath in [output_file, var_ref_file]:
        if filepath.exists():
            checksum = compute_file_checksum(filepath)
            stats["output"]["checksums"][filepath.name] = checksum

    # Add anomaly detection for numeric columns (1.1 has minimal numeric columns)
    # Check if there are any numeric columns suitable for anomaly detection
    numeric_cols = df_final.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        stats["quality_anomalies"] = detect_anomalies_zscore(
            df_final, numeric_cols, threshold=3.0
        )

    print_stats_summary(stats)
    save_stats(stats, paths["output_dir"])

    # Generate report
    report_lines = [
        "# Step 1.1: Clean Metadata & Event Filtering - Report",
        "",
        f"**Timestamp**: {timestamp}",
        "",
        "## Summary",
        "",
        f"- **Input rows**: {original_count:,}",
        f"- **Exact duplicates removed**: {exact_dupes:,}",
        f"- **Collision rows resolved**: {resolved if len(collisions) > 0 else 0:,}",
        f"- **Non-earnings calls removed**: {len(df_clean) - len(df_filtered) if 'event_type' in df_clean.columns else 0:,}",
        f"- **Out-of-range years removed**: {removed:,}",
        f"- **Final output rows**: {len(df_final):,}",
        "",
        "## Output Files",
        "",
        f"- Cleaned metadata: `{output_file.name}`",
        f"- Variable reference: `{var_ref_file.name}`",
        "",
        "## Columns",
        "",
        f"Total columns: {len(df_final.columns)}",
        "",
        "```",
        ", ".join(df_final.columns.tolist()),
        "```",
    ]

    report_file = paths["output_dir"] / "report_step_1_1.md"
    report_file.write_text("\n".join(report_lines), encoding="utf-8")
    print_dual(f"Report saved: {report_file}")

    # Update latest symlink using shared utility (handles symlinks, junctions, copy fallback)
    update_latest_link(
        target_dir=paths["output_dir"], link_path=paths["latest_dir"], verbose=True
    )

    print_dual("\n" + "=" * 80)
    print_dual("Step 1.1 completed successfully.")
    print_dual("=" * 80)

    # Restore stdout and close log
    sys.stdout = dual_writer.terminal
    dual_writer.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
