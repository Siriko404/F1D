#!/usr/bin/env python3
"""
==============================================================================
STEP 1.3: CEO Tenure Map Construction
==============================================================================
ID: 1.3_BuildTenureMap
Description: Constructs monthly CEO tenure panel from Execucomp data.
             Aggregates annual records into episodes, links predecessors,
             and expands to monthly panel with current + previous CEO info.

Inputs:
    - 1_Inputs/Execucomp/comp_execucomp.parquet
    - config/project.yaml

Outputs:
    - 4_Outputs/1.3_BuildTenureMap/{timestamp}/tenure_monthly.parquet
    - 4_Outputs/1.3_BuildTenureMap/{timestamp}/variable_reference.csv
    - 4_Outputs/1.3_BuildTenureMap/{timestamp}/report_step_1_3.md
    - 3_Logs/1.3_BuildTenureMap/{timestamp}.log

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
import hashlib
import json
import time
import psutil

from shared.symlink_utils import update_latest_link
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


def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def validate_input_file(file_path: Path, must_exist: bool = True) -> None:
    """Validate that input file exists if required"""
    if must_exist and not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    return None


def setup_paths(config):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    paths = {
        "root": root,
        "execucomp": root / "1_Inputs" / "Execucomp" / "comp_execucomp.parquet",
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config["paths"]["outputs"] / "1.3_BuildTenureMap"
    paths["output_dir"] = output_base / timestamp
    paths["log_file"] = output_base / f"{timestamp}.log"

    # Update latest symlink
    update_latest_link(paths["output_dir"], link_path=paths["output_dir"])

    return paths, timestamp


# ==============================================================================
# Dual-write logging utility
# ==============================================================================


def main():
    config = load_config()
    paths, timestamp = setup_paths(config)

    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print_dual("=" * 80)
    print_dual("STEP 1.3: CEO Tenure Map Construction")
    print_dual("=" * 80)
    print_dual(f"Timestamp: {timestamp}\n")

    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()

    # Memory tracking at script start
    mem_start = get_process_memory_mb()
    all_memory_values = [mem_start["rss_mb"]]

    stats = {
        "step_id": "1.3_BuildTenureMap",
        "timestamp": timestamp,
        "input": {
            "files": [str(paths["execucomp"])],
            "checksums": {},
            "total_rows": 0,
            "total_columns": 0,
        },
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    # Load Execucomp
    print_dual("Loading Execucomp data...")
    df = pd.read_parquet(paths["execucomp"])
    print_dual(f"  Loaded {len(df):,} records\n")

    stats["input"]["checksums"][paths["execucomp"].name] = compute_file_checksum(
        paths["execucomp"]
    )
    stats["input"]["total_rows"] = len(df)
    stats["input"]["total_columns"] = len(df.columns)

    # Filter for CEO records (ceoann == 'CEO' or becameceo is not null)
    print_dual("Identifying CEO records...")
    ceo_records = df[(df["ceoann"] == "CEO") | (df["becameceo"].notna())].copy()
    print_dual(f"  Found {len(ceo_records):,} CEO-related records")
    print_dual(f"  Unique firms (gvkey): {ceo_records['gvkey'].nunique():,}")
    print_dual(f"  Unique executives (execid): {ceo_records['execid'].nunique():,}\n")

    stats["processing"]["ceo_filter"] = stats["input"]["total_rows"] - len(ceo_records)
    print_stat("Records filtered (non-CEO)", value=stats["processing"]["ceo_filter"])

    # Build tenure episodes
    print_dual("Building tenure episodes per (gvkey, execid)...")

    episodes = []
    for (gvkey, execid), group in ceo_records.groupby(["gvkey", "execid"]):
        # Get start and end dates
        became_ceo_dates = group["becameceo"].dropna()
        left_dates = group["leftofc"].dropna()

        if len(became_ceo_dates) == 0:
            continue  # Skip if no becameceo date (not strictly a CEO)

        start_date = became_ceo_dates.min()

        if len(left_dates) > 0:
            end_date = left_dates.max()
        else:
            # Active CEO: check if in latest fiscal year
            max_year = group["year"].max()
            latest_dataset_year = ceo_records["year"].max()

            if max_year >= latest_dataset_year:
                # Active CEO, impute future end date
                end_date = pd.Timestamp("2025-12-31")
            else:
                # Missing data, use last year's end
                end_date = pd.Timestamp(f"{int(max_year)}-12-31")

        episodes.append(
            {
                "gvkey": gvkey,
                "execid": execid,
                "exec_fullname": group["exec_fullname"].iloc[0]
                if "exec_fullname" in group.columns
                else None,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

    episodes_df = pd.DataFrame(episodes)
    print_dual(f"  Created {len(episodes_df):,} tenure episodes\n")

    stats["processing"]["episodes_created"] = len(episodes_df)
    print_stat("Tenure episodes created", value=stats["processing"]["episodes_created"])

    # Link predecessors
    print_dual("Linking predecessors (prev_execid)...")

    episodes_df["start_date"] = pd.to_datetime(episodes_df["start_date"])
    episodes_df["end_date"] = pd.to_datetime(episodes_df["end_date"])

    episodes_df = episodes_df.sort_values(["gvkey", "start_date"]).reset_index(
        drop=True
    )

    # Compute prev_execid
    episodes_df["prev_execid"] = None
    episodes_df["prev_exec_fullname"] = None

    for gvkey, group in episodes_df.groupby("gvkey"):
        indices = group.index.tolist()
        for i in range(1, len(indices)):
            current_idx = indices[i]
            prev_idx = indices[i - 1]

            episodes_df.at[current_idx, "prev_execid"] = episodes_df.at[
                prev_idx, "execid"
            ]
            episodes_df.at[current_idx, "prev_exec_fullname"] = episodes_df.at[
                prev_idx, "exec_fullname"
            ]

    linked_count = episodes_df["prev_execid"].notna().sum()
    print_dual(f"  Linked {linked_count:,} episodes to predecessors\n")

    stats["processing"]["predecessors_linked"] = linked_count
    print_stat(
        "Episodes linked to predecessors",
        value=stats["processing"]["predecessors_linked"],
    )

    # Expand to monthly panel
    print_dual("Expanding to monthly panel...")

    monthly_records = []
    total_episodes = len(episodes_df)
    progress_interval = max(500, total_episodes // 20)

    for i, (idx, row) in enumerate(episodes_df.iterrows(), 1):
        # Generate monthly dates
        months = pd.date_range(
            start=row["start_date"].to_period("M").to_timestamp(),
            end=row["end_date"].to_period("M").to_timestamp(),
            freq="MS",
        )

        for month_start in months:
            monthly_records.append(
                {
                    "gvkey": row["gvkey"],
                    "year": month_start.year,
                    "month": month_start.month,
                    "date": month_start,
                    "ceo_id": row["execid"],
                    "ceo_name": row["exec_fullname"],
                    "prev_ceo_id": row["prev_execid"],
                    "prev_ceo_name": row["prev_exec_fullname"],
                }
            )

        # Progress indicator
        if i % progress_interval == 0 or i == total_episodes:
            pct = (i / total_episodes) * 100
            print_dual(
                f"    Progress: {i:,}/{total_episodes:,} episodes ({pct:.1f}%) - {len(monthly_records):,} monthly records"
            )

    monthly_df = pd.DataFrame(monthly_records)
    print_dual(f"  Generated {len(monthly_df):,} monthly records")

    stats["processing"]["monthly_records_before_overlap"] = len(monthly_df)
    print_stat(
        "Monthly records (before overlap resolution)",
        value=stats["processing"]["monthly_records_before_overlap"],
    )

    # Resolve overlaps (if CEO A ends after CEO B starts, B takes precedence)
    print_dual("\nResolving overlaps...")
    monthly_df = monthly_df.sort_values(["gvkey", "year", "month", "date"])
    monthly_df = monthly_df.drop_duplicates(
        subset=["gvkey", "year", "month"], keep="last"
    )
    print_dual(f"  Final monthly panel: {len(monthly_df):,} records")
    print_dual(
        f"  Date range: {monthly_df['date'].min()} to {monthly_df['date'].max()}\n"
    )

    stats["processing"]["overlap_duplicates_removed"] = stats["processing"][
        "monthly_records_before_overlap"
    ] - len(monthly_df)
    print_stat(
        "Overlap duplicates removed",
        value=stats["processing"]["overlap_duplicates_removed"],
    )
    print_stat(
        "Final monthly records",
        before=stats["processing"]["monthly_records_before_overlap"],
        after=len(monthly_df),
    )

    # Save output
    output_file = paths["output_dir"] / "tenure_monthly.parquet"
    monthly_df.to_parquet(output_file, index=False)
    print_dual(f"Saved monthly tenure panel: {output_file}")

    stats["output"]["final_rows"] = len(monthly_df)
    stats["output"]["final_columns"] = len(monthly_df.columns)
    stats["output"]["files"] = [output_file.name]

    # Analyze missing values
    stats["missing_values"] = analyze_missing_values(monthly_df)
    if stats["missing_values"]:
        print_dual("\nMissing value analysis:")
        for col, info in stats["missing_values"].items():
            print_dual(f"  {col}: {info['count']:,} ({info['percent']:.2f}%)")

    # Generate variable reference
    var_ref_file = paths["output_dir"] / "variable_reference.csv"
    generate_variable_reference(monthly_df, var_ref_file, print_dual)

    # Update latest symlink using shared utility (handles symlinks, junctions, copy fallback)
    update_latest_link(
        target_dir=paths["output_dir"], link_path=paths["latest_dir"], verbose=True
    )

    # Finalize timing and save stats
    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

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

    # Add anomaly detection for numeric columns (tenure_range, ceo_count)
    # Check if there are any numeric columns suitable for anomaly detection
    numeric_cols = monthly_df.select_dtypes(include=[np.number]).columns.tolist()
    # Filter to relevant numeric columns for tenure map
    anomaly_cols = [col for col in numeric_cols if col in ["tenure_range", "ceo_count"]]
    if anomaly_cols:
        stats["quality_anomalies"] = detect_anomalies_zscore(
            monthly_df, anomaly_cols, threshold=3.0
        )

    # Print stats summary
    print_stats_summary(stats)

    # Save stats JSON
    save_stats(stats, paths["output_dir"])

    print_dual("\n" + "=" * 80)
    print_dual("Step 1.3 completed successfully.")
    print_dual("=" * 80)

    sys.stdout = dual_writer.terminal
    dual_writer.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
