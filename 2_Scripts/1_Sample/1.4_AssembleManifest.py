#!/usr/bin/env python3
"""
==============================================================================
STEP 1.4: Manifest Assembly & CEO Filtering
==============================================================================
ID: 1.4_AssembleManifest
Description: Joins linked metadata with CEO tenure panel, filters for
             CEOs with minimum call threshold, and produces final manifest.

Inputs:
    - 4_Outputs/1.2_LinkEntities/latest/metadata_linked.parquet
    - 4_Outputs/1.3_BuildTenureMap/latest/tenure_monthly.parquet
    - config/project.yaml

Outputs:
    - 4_Outputs/1.4_AssembleManifest/{timestamp}/master_sample_manifest.parquet
    - 4_Outputs/1.4_AssembleManifest/{timestamp}/variable_reference.csv
    - 4_Outputs/1.4_AssembleManifest/{timestamp}/report_step_1_4.md
    - 3_Logs/1.4_AssembleManifest/{timestamp}.log

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
import importlib.util
import sys
from pathlib import Path
import time
import json
import hashlib
import psutil

# Dynamic import for 1.5_Utils.py to comply with naming convention
try:
    utils_path = Path(__file__).parent / "1.5_Utils.py"
    spec = importlib.util.spec_from_file_location("utils", utils_path)
    utils = importlib.util.module_from_spec(spec)
    sys.modules["utils"] = utils
    spec.loader.exec_module(utils)
    from utils import (
        generate_variable_reference,
        get_latest_output_dir,
    )
    from shared.symlink_utils import update_latest_link
except ImportError as e:
    print(f"Criticial Error importing utils: {e}")
    sys.exit(1)

# ==============================================================================
# Dual-write logging utility
# ==============================================================================


class DualWriter:
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
    print(msg, flush=True)


def compute_file_checksum(filepath, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(label, before=None, after=None, value=None, indent=2):
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
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)

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

    if stats["processing"]:
        print(f"\n{'Processing Step':<30} {'Removed':>10}")
        print("-" * 42)
        for step, count in stats["processing"].items():
            print(f"{step:<30} {count:>10,}")

    # SAMP-06: Unique firms
    if stats.get("sample", {}).get("unique_firms"):
        print(f"\n{'Unique Firms':<25} {stats['sample']['unique_firms']:>15,}")

    # SAMP-04: Industry distribution (top 5)
    if stats.get("distributions", {}).get("industry_ff12"):
        print(f"\n{'Top 5 Industries (FF12)':<25}")
        sorted_industries = sorted(
            stats["distributions"]["industry_ff12"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        for code, count in sorted_industries:
            print(f"  {code:<23} {count:>15,}")
    elif stats.get("distributions", {}).get("industry_ff48"):
        print(f"\n{'Top 5 Industries (FF48)':<25}")
        sorted_industries = sorted(
            stats["distributions"]["industry_ff48"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        for code, count in sorted_industries:
            print(f"  {code:<23} {count:>15,}")

    # SAMP-05: Time distribution (year range and sample)
    if stats.get("distributions", {}).get("by_year"):
        years = sorted([int(y) for y in stats["distributions"]["by_year"].keys()])
        print(f"\n{'Year Range':<25} {years[0]:>5} - {years[-1]:<5}")
        print(f"{'Total Years':<25} {len(years):>15,}")

    print("=" * 60)


def save_stats(stats, out_dir):
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
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_paths(config):
    root = Path(__file__).parent.parent.parent

    # Use get_latest_output_dir to robustly find inputs even if symlinks are broken
    metadata_base = root / "4_Outputs" / "1.2_LinkEntities"
    tenure_base = root / "4_Outputs" / "1.3_BuildTenureMap"

    paths = {
        "root": root,
        "metadata": get_latest_output_dir(metadata_base, "metadata_linked.parquet")
        / "metadata_linked.parquet",
        "tenure": get_latest_output_dir(tenure_base, "tenure_monthly.parquet")
        / "tenure_monthly.parquet",
    }

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config["paths"]["outputs"] / "1.4_AssembleManifest"
    paths["output_dir"] = output_base / timestamp
    paths["output_dir"].mkdir(parents=True, exist_ok=True)

    paths["latest_dir"] = output_base / "latest"

    log_base = root / config["paths"]["logs"] / "1.4_AssembleManifest"
    log_base.mkdir(parents=True, exist_ok=True)
    paths["log_file"] = log_base / f"{timestamp}.log"

    return paths, timestamp


# Generate_variable_reference and update_latest_symlink imported from step1_utils

# ==============================================================================
# Main processing
# ==============================================================================


def main():
    config = load_config()
    paths, timestamp = setup_paths(config)

    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()

    # Memory tracking at script start
    mem_start = get_process_memory_mb()
    all_memory_values = [mem_start["rss_mb"]]

    stats = {
        "step_id": "1.4_AssembleManifest",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "sample": {},
        "distributions": {},
        "timing": {},
    }

    print_dual("=" * 80)
    print_dual("STEP 1.4: Manifest Assembly & CEO Filtering")
    print_dual("=" * 80)
    print_dual(f"Timestamp: {timestamp}\n")

    # Load inputs
    print_dual("Loading linked metadata...")
    # Column pruning: only reading needed columns
    metadata = pd.read_parquet(
        paths["metadata"],
        columns=[
            "file_name",
            "gvkey",
            "start_date",
            "ff12_code",
            "ff12_name",
            "ff48_code",
            "ff48_name",
        ],
    )

    # Record metadata input stats
    metadata_checksum = compute_file_checksum(paths["metadata"])
    stats["input"]["files"].append(str(paths["metadata"].name))
    stats["input"]["checksums"][str(paths["metadata"].name)] = metadata_checksum
    stats["input"]["total_rows"] = len(metadata)

    print_stat("Metadata file checksum", value=metadata_checksum[:16] + "...")
    print_dual(f"  Loaded {len(metadata):,} calls\n")

    print_dual("Loading CEO tenure panel...")
    # Column pruning: only reading needed columns
    tenure = pd.read_parquet(
        paths["tenure"],
        columns=[
            "gvkey",
            "year",
            "month",
            "ceo_id",
            "ceo_name",
            "prev_ceo_id",
            "prev_ceo_name",
        ],
    )

    # Record tenure input stats
    tenure_checksum = compute_file_checksum(paths["tenure"])
    stats["input"]["files"].append(str(paths["tenure"].name))
    stats["input"]["checksums"][str(paths["tenure"].name)] = tenure_checksum

    print_stat("Tenure file checksum", value=tenure_checksum[:16] + "...")
    print_dual(f"  Loaded {len(tenure):,} monthly CEO records")
    print_dual(f"  Unique firms: {tenure['gvkey'].nunique():,}")
    print_dual(f"  Unique CEOs: {tenure['ceo_id'].nunique():,}\n")

    # Prepare for join
    print_dual("Preparing data for join...")
    metadata["start_date"] = pd.to_datetime(metadata["start_date"])
    metadata["year"] = metadata["start_date"].dt.year
    metadata["month"] = metadata["start_date"].dt.month

    # Convert gvkey to string with 6-digit zero-padding for consistent join
    # Metadata gvkey is numeric (e.g., 3082), tenure gvkey is string with leading zeros ('001004')
    metadata["gvkey"] = metadata["gvkey"].apply(
        lambda x: str(int(x)).zfill(6) if pd.notna(x) else None
    )
    tenure["gvkey"] = tenure["gvkey"].astype(str).str.zfill(6)

    print_dual(f"  Metadata gvkey sample: {metadata['gvkey'].dropna().iloc[0]}")
    print_dual(f"  Tenure gvkey sample: {tenure['gvkey'].iloc[0]}")
    print_dual(
        f"  Metadata calls by year: {metadata['year'].min()}-{metadata['year'].max()}"
    )
    print_dual(
        f"  Tenure panel by year: {tenure['year'].min()}-{tenure['year'].max()}\n"
    )

    # Join on (gvkey, year, month)
    print_dual("Joining metadata with CEO tenure on (gvkey, year, month)...")
    merged = metadata.merge(
        tenure[
            [
                "gvkey",
                "year",
                "month",
                "ceo_id",
                "ceo_name",
                "prev_ceo_id",
                "prev_ceo_name",
            ]
        ],
        on=["gvkey", "year", "month"],
        how="left",
    )

    matched = merged["ceo_id"].notna().sum()
    unmatched = merged["ceo_id"].isna().sum()
    print_dual(f"  Matched: {matched:,} calls ({matched / len(merged) * 100:.1f}%)")
    print_dual(
        f"  Unmatched: {unmatched:,} calls ({unmatched / len(merged) * 100:.1f}%)\n"
    )

    # Track merge stats
    stats["merges"] = {
        "ceo_tenure_join": {
            "left_rows": len(metadata),
            "right_rows": len(tenure),
            "result_rows": len(merged),
            "matched": int(matched),
            "unmatched": int(unmatched),
        }
    }

    # Filter unmatched
    print_dual("Filtering out unmatched calls...")
    df_matched = merged[merged["ceo_id"].notna()].copy()
    print_dual(f"  Remaining: {len(df_matched):,} calls\n")

    # Apply minimum call threshold
    min_calls = config.get("step_02_5c", {}).get("min_calls_threshold", 5)
    print_dual(f"Applying minimum call threshold (>= {min_calls} calls per CEO)...")

    # Count calls per CEO
    ceo_counts = df_matched["ceo_id"].value_counts()
    valid_ceos = set(ceo_counts[ceo_counts >= min_calls].index)

    print_dual(f"  Total unique CEOs: {len(ceo_counts):,}")
    print_dual(f"  CEOs with >= {min_calls} calls: {len(valid_ceos):,}")
    print_dual(f"  CEOs dropped: {len(ceo_counts) - len(valid_ceos):,}\n")

    # Filter for valid CEOs
    df_final = df_matched[df_matched["ceo_id"].isin(valid_ceos)].copy()
    dropped_calls = len(df_matched) - len(df_final)
    print_dual(f"  Calls dropped: {dropped_calls:,}")
    print_dual(f"  Final manifest size: {len(df_final):,} calls\n")

    # Track processing stats
    stats["processing"]["unmatched_calls_removed"] = int(unmatched)
    stats["processing"]["below_threshold_calls_removed"] = dropped_calls

    # Drop temporary columns
    df_final = df_final.drop(columns=["year", "month"])

    # Sort for determinism
    df_final = df_final.sort_values("file_name").reset_index(drop=True)

    # Save output
    output_file = paths["output_dir"] / "master_sample_manifest.parquet"
    df_final.to_parquet(output_file, index=False)
    print_dual(f"Saved master sample manifest: {output_file}")

    # Record output stats
    stats["output"]["final_rows"] = len(df_final)
    stats["output"]["final_columns"] = len(df_final.columns)
    stats["output"]["files"].append(output_file.name)
    stats["missing_values"] = analyze_missing_values(df_final)

    # SAMP-04: Industry distribution (ff12_code)
    if "ff12_code" in df_final.columns:
        industry_counts = df_final["ff12_code"].value_counts().to_dict()
        stats["distributions"]["industry_ff12"] = industry_counts
    elif "ff48_code" in df_final.columns:
        industry_counts = df_final["ff48_code"].value_counts().to_dict()
        stats["distributions"]["industry_ff48"] = industry_counts

    # SAMP-05: Time distribution (by year)
    years = pd.to_datetime(df_final["start_date"]).dt.year
    year_counts = years.value_counts().sort_index().to_dict()
    stats["distributions"]["by_year"] = {str(k): int(v) for k, v in year_counts.items()}

    # SAMP-06: Unique firms count
    stats["sample"]["unique_firms"] = int(df_final["gvkey"].nunique())

    # Generate variable reference
    var_ref_file = paths["output_dir"] / "variable_reference.csv"
    generate_variable_reference(df_final, var_ref_file, print_dual)

    # Generate summary report
    report_lines = [
        "# Step 1.4: Manifest Assembly & CEO Filtering - Report",
        "",
        f"**Timestamp**: {timestamp}",
        "",
        "## Summary",
        "",
        f"- **Input calls (linked metadata)**: {len(metadata):,}",
        f"- **Matched to CEO**: {matched:,} ({matched / len(metadata) * 100:.1f}%)",
        f"- **Unmatched to CEO**: {unmatched:,} ({unmatched / len(metadata) * 100:.1f}%)",
        f"- **Minimum call threshold**: {min_calls}",
        f"- **Valid CEOs**: {len(valid_ceos):,}",
        f"- **Dropped CEOs**: {len(ceo_counts) - len(valid_ceos):,}",
        f"- **Final manifest size**: {len(df_final):,} calls",
        "",
        "## CEO Distribution",
        "",
        f"- **Mean calls per CEO**: {df_final.groupby('ceo_id').size().mean():.1f}",
        f"- **Median calls per CEO**: {df_final.groupby('ceo_id').size().median():.0f}",
        f"- **Max calls (single CEO)**: {df_final.groupby('ceo_id').size().max():.0f}",
        "",
        "## Columns in Manifest",
        "",
        f"Total columns: {len(df_final.columns)}",
        "",
        "Key columns:",
        "- `file_name`: Unique call identifier",
        "- `gvkey`: Compustat firm identifier",
        "- `ceo_id`: Executive ID (execid)",
        "- `ceo_name`: CEO full name",
        "- `prev_ceo_id`: Previous CEO's execid",
        "- `prev_ceo_name`: Previous CEO's full name",
        "- `start_date`: Call date",
        "- `ff48_code`, `ff48_name`: Industry classification",
        "",
        "## Next Steps",
        "",
        "This manifest defines the **Universe of Analysis**. All text processing",
        "in Step 2 will be restricted to `file_name` values present in this manifest.",
    ]

    report_file = paths["output_dir"] / "report_step_1_4.md"
    report_file.write_text("\n".join(report_lines), encoding="utf-8")
    print_dual(f"Report saved: {report_file}")

    # Update latest symlink using shared utility (handles symlinks, junctions, copy fallback)
    update_latest_link(
        target_dir=paths["output_dir"], link_path=paths["latest_dir"], verbose=True
    )

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
    for filepath in [output_file]:
        if filepath.exists():
            checksum = compute_file_checksum(filepath)
            stats["output"]["checksums"][filepath.name] = checksum

    # Add anomaly detection for numeric columns (year distribution)
    # Check if there are any numeric columns suitable for anomaly detection
    numeric_cols = df_final.select_dtypes(include=[np.number]).columns.tolist()
    # Filter to relevant numeric columns for sample manifest (e.g., year counts)
    anomaly_cols = [col for col in numeric_cols if col.startswith("year_")]
    if anomaly_cols:
        stats["quality_anomalies"] = detect_anomalies_zscore(
            df_final, anomaly_cols, threshold=3.0
        )

    print_stats_summary(stats)
    save_stats(stats, paths["output_dir"])

    print_dual("\n" + "=" * 80)
    print_dual("Step 1.4 completed successfully.")
    print_dual("=" * 80)

    sys.stdout = dual_writer.terminal
    dual_writer.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
