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
from shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
    print_stat,
    analyze_missing_values,
    print_stats_summary,
    save_stats,
    get_process_memory_mb,
    calculate_throughput,
    detect_anomalies_zscore,
    detect_anomalies_iqr,
)
from shared.symlink_utils import update_latest_link
from shared.chunked_reader import track_memory_usage

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

# Import shared path validation utilities
try:
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
    )
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path

    _script_dir = _Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
    )


def print_dual(msg):
    """Print to both terminal and log"""
    print(msg, flush=True)


# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================


def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
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
    ensure_output_dir(paths["output_dir"])

    paths["latest_dir"] = output_base / "latest"

    # Create log directory
    log_base = root / config["paths"]["logs"] / "1.1_CleanMetadata"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}.log"

    return paths, timestamp


# Variable reference generation and symlink handling imported from step1_utils

# ==============================================================================
# Memory-tracked operations
# ==============================================================================


@track_memory_usage("load_metadata")
def load_metadata_with_tracking(input_path):
    """Load metadata with memory tracking"""
    validate_input_file(input_path, must_exist=True)
    df = load_validated_parquet(
        input_path, schema_name="Unified-info.parquet", strict=True
    )
    return df


@track_memory_usage("clean_metadata")
def clean_metadata_with_tracking(df):
    """Clean metadata (dedup + collision resolution) with memory tracking"""
    # Deduplication: Exact duplicates
    original_count = len(df)
    df_dedup = df.drop_duplicates()
    exact_dupes = original_count - len(df_dedup)

    # Resolve file_name collisions
    collision_mask = df_dedup.duplicated(subset=["file_name"], keep=False)
    collisions = df_dedup[collision_mask].copy()

    if len(collisions) > 0:
        # Sort by validation_timestamp and keep first
        collisions_sorted = collisions.sort_values(
            ["file_name", "validation_timestamp"]
        )
        keep_indices = collisions_sorted.groupby("file_name").head(1).index

        # Remove all collisions, then add back kept ones
        df_clean = df_dedup[~collision_mask].copy()
        df_clean = pd.concat([df_clean, df_dedup.loc[keep_indices]], ignore_index=True)
        resolved = len(collisions) - len(keep_indices)
    else:
        df_clean = df_dedup.copy()
        resolved = 0

    return {
        "result": df_clean,
        "exact_dupes_removed": exact_dupes,
        "collision_rows_resolved": resolved,
    }


@track_memory_usage("save_output")
def save_output_with_tracking(df, output_path):
    """Save output with memory tracking"""
    df.to_parquet(output_path, index=False)
    return {"path": str(output_path)}


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

    # Initialize stats collector
    stats = {
        "step_id": "1.1_CleanMetadata",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "timing": {},
        "memory_mb": {},  # Added for operation-level memory tracking
    }

    print_dual("=" * 80)
    print_dual("STEP 1.1: Clean Metadata & Event Filtering")
    print_dual("=" * 80)
    print_dual(f"Timestamp: {timestamp}")
    print_dual(f"Output Directory: {paths['output_dir']}")
    print_dual("")

    # Load Unified-info with memory tracking
    print_dual("Loading Unified-info.parquet...")
    load_result = load_metadata_with_tracking(paths["unified_info"])
    df = load_result["result"]
    stats["memory_mb"]["load_metadata"] = load_result["memory_mb"]

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

    # Clean metadata with memory tracking
    print_dual("\nStep 1-2: Removing duplicates and resolving collisions...")
    clean_result = clean_metadata_with_tracking(df)
    df_clean = clean_result["result"]
    stats["memory_mb"]["clean_metadata"] = clean_result["memory_mb"]

    exact_dupes = clean_result["exact_dupes_removed"]
    resolved = clean_result["collision_rows_resolved"]
    stats["processing"]["exact_duplicates_removed"] = exact_dupes
    stats["processing"]["collision_rows_resolved"] = resolved

    print_dual(f"  Removed {exact_dupes:,} exact duplicate rows")
    print_dual(f"  Resolved {resolved:,} collision rows")
    print_dual(f"  Remaining: {len(df_clean):,} rows")

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

    # Record missing values and output stats
    stats["missing_values"] = analyze_missing_values(df_final)
    stats["output"]["final_rows"] = len(df_final)
    stats["output"]["final_columns"] = len(df_final.columns)

    # Save output with memory tracking
    output_file = paths["output_dir"] / "metadata_cleaned.parquet"
    print_dual(f"\nSaving cleaned metadata...")
    save_result = save_output_with_tracking(df_final, output_file)
    stats["memory_mb"]["save_output"] = save_result["memory_mb"]
    print_dual(f"Saved cleaned metadata: {output_file}")

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

    # Add memory stats to stats
    stats["memory"] = {
        "start_mb": round(mem_start["rss_mb"], 2),
        "end_mb": round(mem_end["rss_mb"], 2),
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
        f"- **Collision rows resolved**: {resolved:,}",
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
