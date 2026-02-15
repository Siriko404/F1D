#!/usr/bin/env python3
"""
==============================================================================
STEP3.3: Build Event Flags
==============================================================================
ID: 3.3_EventFlags
Description: Computes takeover event flags from SDC M&A data.

Variables Computed:
    - Takeover: Binary flag (1 if firm was takeover target within 365 days)
    - Takeover_Type: "Friendly" or "Uninvited" (from Deal Attitude)
    - Duration: Quarters until takeover event (for survival analysis)

Inputs:
    - 4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet
    - 1_Inputs/SDC/sdc-ma-merged.parquet

Outputs:
    - 4_Outputs/3_Financial_Features/{timestamp}/event_flags_{year}.parquet

Deterministic: true

Note: MemoryAwareThrottler from shared/chunked_reader.py is available for future
      chunked processing. Current implementation uses column pruning for memory optimization.
Dependencies:
    - Requires: Step 3.1
    - Uses: 3.4_Utils, pandas

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import psutil
import yaml

# Dynamic import for 3.4_Utils.py
utils_path = Path(__file__).parent / "3.4_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Could not load module from {utils_path}")
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)


# Import shared path validation utilities
# Import DualWriter from f1d.shared.observability_utils
from f1d.shared.observability_utils import DualWriter
from f1d.shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
)

# Import shared observability utilities (new Step 3.3 statistics functions)
try:
    from f1d.shared.observability_utils import (
        calculate_throughput,
        compute_step33_input_stats,
        compute_step33_output_stats,
        compute_step33_process_stats,
        detect_anomalies_iqr,
        detect_anomalies_zscore,
        generate_financial_report_markdown,
        get_process_memory_mb,
    )

    HAS_OBSERVABILITY = True
except ImportError:
    HAS_OBSERVABILITY = False

# ==============================================================================
# Statistics Helpers
# ==============================================================================


def compute_file_checksum(filepath: Path, algorithm: str = "sha256") -> str:
    """Compute checksum for a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(
    label: str,
    before: Optional[int] = None,
    after: Optional[int] = None,
    value: Optional[Any] = None,
    indent: int = 2,
) -> None:
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


def analyze_missing_values(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
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


def print_stats_summary(stats: Dict[str, Any]) -> None:
    """Print formatted summary table."""
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
    print(f"{'Duration (seconds)':<25} {stats['timing']['duration_seconds']:>15.2f}")

    if stats["processing"]:
        print(f"\n{'Processing Step':<30} {'Count':>10}")
        print("-" * 42)
        for step, count in stats["processing"].items():
            print(f"{step:<30} {count:>10,}")

    print("=" * 60)


def save_stats(stats: Dict[str, Any], out_dir: Path) -> None:
    """Save statistics to JSON file."""
    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


# ==============================================================================
# Observability Helper Functions (imported from observability_utils)
# ==============================================================================


# ==============================================================================
# Configuration
# ==============================================================================


def load_config() -> Dict[str, Any]:
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent.parent.parent / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_paths(config: Dict[str, Any], timestamp: str) -> Dict[str, Path]:
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent.parent.parent

    # Resolve manifest directory using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.0_BuildSampleManifest",
        required_file="master_sample_manifest.parquet",
    )

    paths = {
        "root": root,
        "manifest_dir": manifest_dir,
        "sdc_file": root / "1_Inputs" / "SDC" / "sdc-ma-merged.parquet",
    }

    # Output directory
    output_base = root / config["paths"]["outputs"] / "3_Financial_Features"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / config["paths"]["logs"] / "3_Financial_Features"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_events.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_manifest(manifest_dir: Path) -> pd.DataFrame:
    """Load manifest data"""
    manifest_file = manifest_dir / "master_sample_manifest.parquet"
    # Column pruning: Load only required columns (including cusip for SDC matching)
    df = pd.read_parquet(manifest_file, columns=["file_name", "gvkey", "start_date", "cusip"])

    df["start_date"] = pd.to_datetime(df["start_date"])
    df["year"] = df["start_date"].dt.year

    # Extract CUSIP6 for SDC matching
    if "cusip" in df.columns:
        df["cusip6"] = df["cusip"].astype(str).str[:6]
    else:
        df["cusip6"] = None

    print(f"  Loaded manifest: {len(df):,} calls")
    print(f"  Calls with CUSIP: {df['cusip6'].notna().sum():,}")

    return df


def load_sdc(sdc_file: Path) -> pd.DataFrame:
    """Load SDC M&A data"""
    print("  Loading SDC M&A data...")

    # Column pruning: Load all SDC columns needed for takeover flag computation
    df = pd.read_parquet(
        sdc_file,
        columns=[
            "Target 6-digit CUSIP",
            "Date Announced",
            "Date Effective",
            "Date Withdrawn",
            "Deal Attitude",
            "Deal Status",
        ],
    )
    print(f"  Raw SDC: {len(df):,} deals")

    # Normalize column names (SDC has spaces in names)
    col_mapping = {
        "Target 6-digit CUSIP": "target_cusip6",
        "Date Announced": "date_announced",
        "Date Effective": "date_effective",
        "Date Withdrawn": "date_withdrawn",
        "Deal Attitude": "deal_attitude",
        "Deal Status": "deal_status",
    }

    for old_name, new_name in col_mapping.items():
        if old_name in df.columns:
            df.rename(columns={old_name: new_name}, inplace=True)

    # Ensure dates are datetime
    for col in ["date_announced", "date_effective", "date_withdrawn"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Clean CUSIP
    df["target_cusip6"] = df["target_cusip6"].astype(str).str[:6]

    print(
        f"  SDC date range: {df['date_announced'].min()} to {df['date_announced'].max()}"
    )
    print(f"  Unique target CUSIPs: {df['target_cusip6'].nunique():,}")

    # Categorize deal attitude
    print("\n  Deal Attitude distribution:")
    if "deal_attitude" in df.columns:
        print(df["deal_attitude"].value_counts())

    return df


# ==============================================================================
# Variable Computation
# ==============================================================================


def compute_takeover_flags(manifest: pd.DataFrame, sdc: pd.DataFrame) -> pd.DataFrame:
    """Compute takeover flags for each call"""
    print("\n" + "=" * 60)
    print("Computing Takeover Flags")
    print("=" * 60)

    # Create lookup: cusip6 -> list of (date_announced, deal_attitude)
    sdc_by_cusip: Dict[str, List[Dict[str, Any]]] = {}
    for _, row in sdc.iterrows():
        cusip6 = row["target_cusip6"]
        if pd.notna(row["date_announced"]):
            if cusip6 not in sdc_by_cusip:
                sdc_by_cusip[cusip6] = []
            sdc_by_cusip[cusip6].append(
                {
                    "date_announced": row["date_announced"],
                    "deal_attitude": row.get("deal_attitude", "Unknown"),
                }
            )

    print(f"  SDC lookup built: {len(sdc_by_cusip):,} unique target CUSIPs")

    results = []
    takeover_count = 0

    for idx, row in manifest.iterrows():
        cusip6 = row.get("cusip6")
        call_date = row["start_date"]

        result = {
            "file_name": row["file_name"],
            "Takeover": 0,
            "Takeover_Type": None,
            "Duration": 4.0,  # Default: censored at 4 quarters
        }

        if pd.isna(cusip6) or cusip6 not in sdc_by_cusip:
            results.append(result)
            continue

        # Check for takeover within 365 days of call
        for deal in sdc_by_cusip[cusip6]:
            days_until = (deal["date_announced"] - call_date).days

            if 0 <= days_until <= 365:
                result["Takeover"] = 1

                # Classify deal type
                attitude = (
                    str(deal["deal_attitude"]).lower() if deal["deal_attitude"] else ""
                )
                if "hostile" in attitude or "unsolicited" in attitude:
                    result["Takeover_Type"] = "Uninvited"
                else:
                    result["Takeover_Type"] = "Friendly"

                # Duration in quarters
                result["Duration"] = max(
                    0.25, days_until / 91.25
                )  # ~91.25 days per quarter

                takeover_count += 1
                break  # Take first matching deal

        results.append(result)

        if isinstance(idx, int) and (idx + 1) % 10000 == 0:
            print(f"  Processed {idx + 1:,} calls...")

    results_df = pd.DataFrame(results)

    print(
        f"\n  Takeover events: {takeover_count:,} / {len(manifest):,} ({takeover_count / len(manifest) * 100:.2f}%)"
    )
    print("\n  Takeover Type distribution:")
    print(results_df[results_df["Takeover"] == 1]["Takeover_Type"].value_counts())

    return results_df


# ==============================================================================
# CLI and Prerequisites
# ==============================================================================


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for 3.3_EventFlags.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.3: Build Event Flags

Constructs event flags from SDC merger data (takeover
attempts, acquisition targets). Creates binary indicators
for corporate events affecting sample firms.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(root: Path) -> None:
    """Validate all required inputs and prerequisite steps exist."""
    from f1d.shared.dependency_checker import validate_prerequisites

    required_files = {
        "SDC/": root / "1_Inputs" / "SDC",
    }

    required_steps = {
        "1.4_AssembleManifest": "master_sample_manifest.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# ==============================================================================
# Main
# ==============================================================================


def main() -> int:
    """Main execution"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    config = load_config()
    paths = setup_paths(config, timestamp)

    # Initialize stats with observability sections
    stats: Dict[str, Any] = {
        "step_id": "3.3_EventFlags",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "merges": {},
        "timing": {"start_iso": "", "end_iso": "", "duration_seconds": 0.0},
        "memory": {
            "start_mb": 0.0,
            "end_mb": 0.0,
            "peak_mb": 0.0,
            "delta_mb": 0.0,
        },
        "throughput": {
            "rows_per_second": 0.0,
            "total_rows": 0,
            "duration_seconds": 0.0,
        },
        "quality_anomalies": {},
    }

    # Timing
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    stats["timing"]["start_iso"] = start_iso
    mem_start = get_process_memory_mb()
    stats["memory"]["start_mb"] = mem_start["rss_mb"]
    memory_readings = [mem_start["rss_mb"]]

    # Setup logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print("=" * 60)
    print("STEP 3.3: Build Event Flags")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Load data
    print("\nLoading data...")

    # Input stats
    manifest_file = paths["manifest_dir"] / "master_sample_manifest.parquet"
    stats["input"]["files"].append(str(manifest_file))
    stats["input"]["checksums"]["master_sample_manifest.parquet"] = (
        compute_file_checksum(manifest_file)
    )

    manifest = load_manifest(paths["manifest_dir"])
    stats["input"]["total_rows"] = len(manifest)
    stats["input"]["total_columns"] = len(manifest.columns)
    print_stat("Manifest rows", value=len(manifest))
    print_stat("Manifest columns", value=len(manifest.columns))

    sdc = load_sdc(paths["sdc_file"])
    print_stat("SDC deals", value=len(sdc))

    # Collect INPUT statistics for Step 3.3 (if observability available)
    if HAS_OBSERVABILITY:
        print("\nCollecting INPUT statistics...")
        stats["step33_input"] = compute_step33_input_stats(
            manifest_df=manifest,
            sdc_df=sdc,
        )

    # Compute takeover flags
    event_flags = compute_takeover_flags(manifest, sdc)
    stats["processing"]["takeover_events"] = int(event_flags["Takeover"].sum())
    stats["processing"]["takeover_pct"] = round(
        float(event_flags["Takeover"].mean() * 100), 2
    )
    print_stat("Takeover events", value=int(event_flags["Takeover"].sum()))

    # Merge with manifest
    print("\nMerging with manifest...")
    before_rows = len(manifest)
    result = manifest[["file_name", "gvkey", "start_date", "year"]].merge(
        event_flags, on="file_name"
    )
    after_rows = len(result)

    stats["merges"]["event_flags_merge"] = {
        "left_rows": before_rows,
        "result_rows": after_rows,
        "matched": after_rows,
        "unmatched_left": before_rows - after_rows,
        "merge_type": "1:1",
    }
    print_stat("Rows after merge", before=before_rows, after=after_rows)

    # Collect PROCESS statistics for Step 3.3 (if observability available)
    if HAS_OBSERVABILITY:
        print("\nCollecting PROCESS statistics...")
        match_results = {
            "manifest_rows": len(manifest),
            "sdc_rows": len(sdc),
            "matched_rows": len(event_flags[event_flags["Takeover"] == 1]),
        }
        stats["step33_process"] = compute_step33_process_stats(
            match_results=match_results,
            takeover_flags_df=event_flags,
            window_days=365,
        )

    # Analyze missing values
    print("\nAnalyzing missing values...")
    missing = analyze_missing_values(result)
    stats["missing_values"] = missing
    for col, info in missing.items():
        print(f"  {col}: {info['count']:,} ({info['percent']:.2f}%)")

    # Save by year
    print("\nSaving outputs by year...")
    for year, group in result.groupby("year"):
        output_file = paths["output_dir"] / f"event_flags_{year}.parquet"
        group.to_parquet(output_file, index=False)
        print(f"  Saved {year}: {len(group):,} calls -> {output_file.name}")
        stats["output"]["files"].append(f"event_flags_{year}.parquet")

    stats["output"]["final_rows"] = len(result)
    stats["output"]["final_columns"] = len(result.columns)

    # Collect OUTPUT statistics for Step 3.3 (if observability available)
    if HAS_OBSERVABILITY:
        print("\nCollecting OUTPUT statistics...")
        stats["step33_output"] = compute_step33_output_stats(
            output_df=result,
        )

        # Generate report
        print("\nGenerating Step 3.3 report...")
        report_path = paths["output_dir"] / "report_step_3_3.md"
        generate_financial_report_markdown(
            input_stats=stats.get("step33_input", {}),
            process_stats=stats.get("step33_process", {}),
            output_stats=stats.get("step33_output", {}),
            step_name="3.3_EventFlags",
            output_path=report_path,
        )
        print(f"  Report saved to: {report_path.name}")

    # Finalize timing
    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    # Final memory tracking
    mem_end = get_process_memory_mb()
    memory_readings.append(mem_end["rss_mb"])
    stats["memory"]["end_mb"] = mem_end["rss_mb"]
    stats["memory"]["peak_mb"] = round(max(memory_readings), 2)
    stats["memory"]["delta_mb"] = round(mem_end["rss_mb"] - mem_start["rss_mb"], 2)

    # Calculate throughput
    duration_seconds = end_time - start_time
    if duration_seconds > 0 and stats["output"]["final_rows"] > 0:
        throughput = calculate_throughput(
            stats["output"]["final_rows"], duration_seconds
        )
        stats["throughput"]["rows_per_second"] = throughput
        stats["throughput"]["total_rows"] = stats["output"]["final_rows"]
        stats["throughput"]["duration_seconds"] = round(duration_seconds, 3)

    # Compute output file checksums
    stats["output"]["checksums"] = {}
    for fname in stats["output"]["files"]:
        if fname.endswith(".parquet"):
            output_path = paths["output_dir"] / fname
            if output_path.exists():
                checksum = compute_file_checksum(output_path)
                stats["output"]["checksums"][fname] = checksum
    print(f"  Computed output checksums: {len(stats['output']['checksums'])} files")

    # Note: 3.3 produces binary event flags (Takeover, Takeover_Type, Duration)
    # These are categorical/binary variables, not suitable for numeric anomaly detection
    stats["quality_anomalies"] = {}
    print("  Anomaly detection skipped (event flags are binary/categorical)")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total calls processed: {len(result):,}")
    print("\nVariable coverage:")
    print(
        f"  Takeover: {result['Takeover'].sum():,} events ({result['Takeover'].mean() * 100:.2f}%)"
    )
    print(
        f"  Duration mean (takeovers only): {result[result['Takeover'] == 1]['Duration'].mean():.2f} quarters"
    )

    print(f"\nOutputs saved to: {paths['output_dir']}")

    # Stats summary
    print_stats_summary(stats)
    save_stats(stats, paths["output_dir"])

    dual_writer.close()
    sys.stdout = dual_writer.terminal

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        sys.exit(0)

    check_prerequisites(root)
    main()
