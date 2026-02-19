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
    - inputs/Earnings_Calls_Transcripts/Unified-info.parquet
    - config/project.yaml

Outputs:
    - outputs/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet
    - outputs/1.1_CleanMetadata/{timestamp}/variable_reference.csv
    - outputs/1.1_CleanMetadata/{timestamp}/report_step_1_1.md
    - logs/1.1_CleanMetadata/{timestamp}.log

Deterministic: true
Dependencies:
    - Requires: Step 1.0
    - Uses: 1.5_Utils, pandas, yaml

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import yaml

from f1d.shared.sample_utils import generate_variable_reference

from f1d.shared.chunked_reader import track_memory_usage
from f1d.shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    calculate_throughput,
    compute_entity_stats,
    compute_file_checksum,
    compute_input_stats,
    compute_temporal_stats,
    detect_anomalies_zscore,
    get_process_memory_mb,
    print_stat,
    print_stats_summary,
    save_stats,
)
from f1d.shared.data_validation import load_validated_parquet
from f1d.shared.path_utils import (
    ensure_output_dir,
    validate_input_file,
    validate_output_path,
)


def print_dual(msg: str) -> None:
    """Print to both terminal and log"""
    print(msg, flush=True)


# ==============================================================================
# CLI argument parsing and prerequisite validation
# ==============================================================================


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for 1.1_CleanMetadata.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 1.1: Clean Metadata & Event Filtering

Cleans Unified-info, deduplicates exact rows, resolves file_name
collisions, and filters for earnings calls (event_type='1') in
target date range (2002-2018).
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    parser.add_argument(
        "--year-start", type=int, help="Start year for filtering (default: from config)"
    )

    parser.add_argument(
        "--year-end", type=int, help="End year for filtering (default: from config)"
    )

    return parser.parse_args()


def check_prerequisites(root: Path, args: argparse.Namespace) -> argparse.Namespace:
    """Validate all required inputs exist."""
    from f1d.shared.dependency_checker import validate_prerequisites

    required_files = {
        "Unified-info.parquet": root
        / "inputs"
        / "Earnings_Calls_Transcripts"
        / "Unified-info.parquet",
    }

    # 1.1 has no prerequisite steps (first in pipeline)
    required_steps: Dict[str, str] = {}

    validate_prerequisites(required_files, required_steps)

    return args


# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================


def load_config() -> Dict[str, Any]:
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_paths(config: Dict[str, Any]) -> tuple[Dict[str, Path], str]:
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent.parent

    paths = {
        "root": root,
        "unified_info": root
        / "inputs"
        / "Earnings_Calls_Transcripts"
        / "Unified-info.parquet",
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config["paths"]["outputs"] / "1.1_CleanMetadata"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Create log directory
    log_base = root / config["paths"]["logs"] / "1.1_CleanMetadata"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}.log"

    return paths, timestamp


# Variable reference generation and symlink handling imported from step1_utils

# ==============================================================================
# Memory-tracked operations
# ==============================================================================
# TYPE ERROR BASELINE: 3 type ignores in this module
# - Lines 170, 180, 214: @track_memory_usage decorator transforms return type
#   from original to Dict[str, Any] with result/memory_mb/timing_seconds keys.
#   Rationale: Decorator uses callable TypeVar, mypy cannot infer transformed
#   return type. Safe because all callers unpack result["result"] pattern.


@track_memory_usage("load_metadata")  # type: ignore[misc]  # Decorator transforms return type
def load_metadata_with_tracking(input_path: Path) -> Dict[str, Any]:
    """Load metadata with memory tracking"""
    validate_input_file(input_path, must_exist=True)
    df = load_validated_parquet(
        input_path, schema_name="Unified-info.parquet", strict=True
    )
    return df  # type: ignore[return-value]


@track_memory_usage("clean_metadata")  # type: ignore[misc]  # Decorator transforms return type
def clean_metadata_with_tracking(df: pd.DataFrame) -> Dict[str, Any]:
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


@track_memory_usage("save_output")  # type: ignore[misc]  # Decorator transforms return type
def save_output_with_tracking(df: pd.DataFrame, output_path: Path) -> Dict[str, str]:
    """Save output with memory tracking"""
    df.to_parquet(output_path, index=False)
    return {"path": str(output_path)}


# ==============================================================================
# Main processing
# ==============================================================================


def main() -> int:
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
    stats: Dict[str, Any] = {
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

    # Collect comprehensive input statistics
    print_dual("\nCollecting input data characteristics...")
    stats["input_descriptive"] = compute_input_stats(df)

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
    df_clean = clean_result["result"]["result"]
    stats["memory_mb"]["clean_metadata"] = clean_result["memory_mb"]

    exact_dupes = clean_result["result"]["exact_dupes_removed"]
    resolved = clean_result["result"]["collision_rows_resolved"]
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

    # Collect comprehensive temporal and entity statistics
    print_dual("\nCollecting temporal coverage statistics...")
    stats["temporal_coverage"] = compute_temporal_stats(df_final, "start_date")

    print_dual("Collecting entity and quality characteristics...")
    stats["entity_characteristics"] = compute_entity_stats(df_final)

    # Record missing values and output stats
    stats["missing_values"] = analyze_missing_values(df_final)
    stats["output"]["final_rows"] = len(df_final)
    stats["output"]["final_columns"] = len(df_final.columns)

    # Save output with memory tracking
    output_file = paths["output_dir"] / "metadata_cleaned.parquet"
    print_dual("\nSaving cleaned metadata...")
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

    # Generate report with comprehensive statistics
    report_lines = [
        "# Step 1.1: Clean Metadata & Event Filtering - Report",
        "",
        f"**Timestamp**: {timestamp}",
        "",
        "## INPUT DATA CHARACTERISTICS",
        "",
        f"- **Total records**: {stats.get('input_descriptive', {}).get('record_count', original_count):,}",
        f"- **Total columns**: {stats.get('input_descriptive', {}).get('column_count', len(df_final.columns))}",
        f"- **Memory footprint**: {stats.get('input_descriptive', {}).get('memory_mb', 0):.2f} MB",
        "",
        "### Column Type Distribution",
        "",
        "| Type | Count |",
        "|------|-------|",
    ]

    # Add column type distribution
    col_types = stats.get("input_descriptive", {}).get("column_types", {})
    for col_type, count in col_types.items():
        report_lines.append(f"| {col_type.capitalize()} | {count} |")

    report_lines.extend(
        [
            "",
            "### Key Distributions",
            "",
        ]
    )

    # Add data quality score distribution if available
    if "data_quality_score" in stats.get("input_descriptive", {}).get(
        "numeric_stats", {}
    ):
        qs = stats["input_descriptive"]["numeric_stats"]["data_quality_score"]
        report_lines.extend(
            [
                "**Data Quality Score**:",
                f"- Mean: {qs.get('mean', 0):.4f}",
                f"- Median: {qs.get('median', 0):.4f}",
                f"- Std: {qs.get('std', 0):.4f}",
                f"- Range: [{qs.get('min', 0):.4f}, {qs.get('max', 0):.4f}]",
                "",
            ]
        )

    # Add processing lag distribution if available
    if "processing_lag_hours" in stats.get("input_descriptive", {}).get(
        "numeric_stats", {}
    ):
        lag = stats["input_descriptive"]["numeric_stats"]["processing_lag_hours"]
        report_lines.extend(
            [
                "**Processing Lag (hours)**:",
                f"- Mean: {lag.get('mean', 0):.2f}",
                f"- Median: {lag.get('median', 0):.2f}",
                f"- Range: [{lag.get('min', 0):.2f}, {lag.get('max', 0):.2f}]",
                "",
            ]
        )

    # Add date range from datetime stats
    if "start_date" in stats.get("input_descriptive", {}).get("datetime_stats", {}):
        ds = stats["input_descriptive"]["datetime_stats"]["start_date"]
        report_lines.extend(
            [
                "**Date Range (Source Data)**:",
                f"- Earliest: {ds.get('min_date', 'N/A')}",
                f"- Latest: {ds.get('max_date', 'N/A')}",
                f"- Span: {ds.get('span_days', 0)} days",
                "",
            ]
        )

    report_lines.extend(
        [
            "## TEMPORAL COVERAGE",
            "",
            "### Calls per Year",
            "",
            "| Year | Count | Percentage |",
            "|------|-------|------------|",
        ]
    )

    # Add year distribution
    year_dist = stats.get("temporal_coverage", {}).get("year_distribution", {})
    total_calls = sum(year_dist.values())
    for year in sorted(year_dist.keys()):
        count = year_dist[year]
        pct = (count / total_calls * 100) if total_calls > 0 else 0
        report_lines.append(f"| {year} | {count:,} | {pct:.2f}% |")

    report_lines.extend(
        [
            "",
            "### Monthly Distribution",
            "",
            "| Month | Count |",
            "|-------|-------|",
        ]
    )

    # Add month distribution
    month_names = [
        "",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    month_dist = stats.get("temporal_coverage", {}).get("month_distribution", {})
    for month_num in sorted(month_dist.keys()):
        count = month_dist[month_num]
        month_name = (
            month_names[month_num]
            if month_num < len(month_names)
            else f"Month {month_num}"
        )
        report_lines.append(f"| {month_name} | {count:,} |")

    report_lines.extend(
        [
            "",
            "### Quarter Distribution",
            "",
            "| Quarter | Count |",
            "|---------|-------|",
        ]
    )

    # Add quarter distribution
    q_dist = stats.get("temporal_coverage", {}).get("quarter_distribution", {})
    for q in sorted(q_dist.keys()):
        count = q_dist[q]
        report_lines.append(f"| Q{q} | {count:,} |")

    report_lines.extend(
        [
            "",
            "### Day of Week Distribution",
            "",
            "| Day | Count |",
            "|-----|-------|",
        ]
    )

    # Add day of week distribution
    dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dow_dist = stats.get("temporal_coverage", {}).get("day_of_week_distribution", {})
    for dow in sorted(dow_dist.keys()):
        count = dow_dist[dow]
        day_name = dow_names[dow] if dow < len(dow_names) else f"Day {dow}"
        report_lines.append(f"| {day_name} | {count:,} |")

    # Add date range from temporal stats
    if "date_range" in stats.get("temporal_coverage", {}):
        dr = stats["temporal_coverage"]["date_range"]
        report_lines.extend(
            [
                "",
                f"**Date Range (Filtered Data)**: {dr.get('earliest', 'N/A')} to {dr.get('latest', 'N/A')} ({dr.get('span_days', 0)} days)",
                "",
            ]
        )

    report_lines.extend(
        [
            "## ENTITY CHARACTERISTICS",
            "",
        ]
    )

    # Add company coverage
    if "company_coverage" in stats.get("entity_characteristics", {}):
        cc = stats["entity_characteristics"]["company_coverage"]
        report_lines.extend(
            [
                "**Company Coverage**:",
                f"- Unique companies: {cc.get('unique_companies', 0):,}",
                f"- Average calls per company: {cc.get('avg_calls_per_company', 0):.2f}",
                "",
            ]
        )

    # Add geographic coverage
    if "geographic_coverage" in stats.get("entity_characteristics", {}):
        gc = stats["entity_characteristics"]["geographic_coverage"]
        report_lines.extend(
            [
                "**Geographic Coverage**:",
                f"- Unique cities: {gc.get('unique_cities', 0):,}",
                "",
                "Top 5 Cities:",
                "",
                "| City | Count |",
                "|------|-------|",
            ]
        )
        for city_info in gc.get("top_cities", [])[:5]:
            report_lines.append(f"| {city_info['city']} | {city_info['count']:,} |")
        report_lines.append("")

    # Add data quality distribution
    if "data_quality_distribution" in stats.get("entity_characteristics", {}):
        dq = stats["entity_characteristics"]["data_quality_distribution"]
        if "error" not in dq:
            report_lines.extend(
                [
                    "**Data Quality Score Distribution**:",
                    f"- Mean: {dq.get('mean', 0):.4f}",
                    f"- Median: {dq.get('median', 0):.4f}",
                    "",
                ]
            )
            if "histogram" in dq and "error" not in dq["histogram"]:
                report_lines.extend(
                    [
                        "Histogram:",
                        "",
                        "| Bucket | Count |",
                        "|--------|-------|",
                    ]
                )
                for bucket, count in dq["histogram"].items():
                    report_lines.append(f"| {bucket} | {count:,} |")
                report_lines.append("")

    # Add speaker coverage
    if "speaker_coverage" in stats.get("entity_characteristics", {}):
        sc = stats["entity_characteristics"]["speaker_coverage"]
        if "error" not in sc:
            report_lines.extend(
                [
                    f"**Speaker Data Coverage**: {sc.get('percent_with_speaker_data', 0):.2f}%",
                    "",
                ]
            )
            if "speaker_record_distribution" in sc:
                srd = sc["speaker_record_distribution"]
                report_lines.extend(
                    [
                        "Speaker Record Count Distribution:",
                        f"- Mean: {srd.get('mean', 0):.2f}",
                        f"- Median: {srd.get('median', 0):.2f}",
                        f"- Range: [{srd.get('min', 0):,}, {srd.get('max', 0):,}]",
                        "",
                    ]
                )

    report_lines.extend(
        [
            "## PROCESS SUMMARY",
            "",
            f"- **Input rows**: {original_count:,}",
            f"- **Exact duplicates removed**: {exact_dupes:,}",
            f"- **Collision rows resolved**: {resolved:,}",
            f"- **Non-earnings calls removed**: {len(df_clean) - len(df_filtered) if 'event_type' in df_clean.columns else 0:,}",
            f"- **Out-of-range years removed**: {removed:,}",
            "",
            "## OUTPUT SUMMARY",
            "",
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
    )

    report_file = paths["output_dir"] / "report_step_1_1.md"
    report_file.write_text("\n".join(report_lines), encoding="utf-8")
    print_dual(f"Report saved: {report_file}")

    print_dual("\n" + "=" * 80)
    print_dual("Step 1.1 completed successfully.")
    print_dual("=" * 80)

    # Restore stdout and close log
    sys.stdout = dual_writer.terminal
    dual_writer.close()

    return 0


if __name__ == "__main__":
    # Parse arguments and check prerequisites
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent.parent

    # Handle dry-run mode
    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root, args)
        print("[OK] All prerequisites validated")
        sys.exit(0)

    # Check prerequisites
    check_prerequisites(root, args)

    # Override config values if arguments provided
    config = load_config()
    if args.year_start:
        config["data"]["year_start"] = args.year_start
    if args.year_end:
        config["data"]["year_end"] = args.year_end

    # Run main processing with updated config
    sys.exit(main())
