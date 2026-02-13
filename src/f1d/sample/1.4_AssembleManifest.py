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
Dependencies:
    - Requires: Step 1.3
    - Uses: 1.5_Utils, pandas

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import importlib.util
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import yaml

# Add parent directory to sys.path for shared module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Dynamic import for 1.5_Utils.py to comply with naming convention
try:
    utils_path = Path(__file__).parent / "1.5_Utils.py"
    spec = importlib.util.spec_from_file_location("utils", utils_path)
    utils = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules["utils"] = utils
    spec.loader.exec_module(utils)  # type: ignore[union-attr]
    from utils import (
        generate_variable_reference,
    )
except ImportError as e:
    print(f"Critical Error importing utils: {e}")
    sys.exit(1)

from shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    calculate_throughput,
    collect_ceo_distribution_samples,
    compute_file_checksum,
    compute_manifest_input_stats,
    compute_manifest_output_stats,
    compute_manifest_process_stats,
    detect_anomalies_zscore,
    get_process_memory_mb,
    print_stat,
    print_stats_summary,
    save_stats,
)
from shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
)


def print_dual(msg: str) -> None:
    """Print message both to stdout and via DualWriter if available."""
    print(msg, flush=True)


def load_config() -> Dict[str, Any]:
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_paths(config: Dict[str, Any]) -> tuple[Dict[str, Path], str]:
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    # Resolve inputs from prior steps using timestamp-based resolution
    metadata_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.2_LinkEntities", required_file="metadata_linked.parquet"
    )
    tenure_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.3_BuildTenureMap",
        required_file="tenure_monthly.parquet",
    )

    paths = {
        "root": root,
        "metadata": metadata_dir / "metadata_linked.parquet",
        "tenure": tenure_dir / "tenure_monthly.parquet",
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config["paths"]["outputs"] / "1.4_AssembleManifest"
    paths["output_dir"] = output_base / timestamp
    paths["log_file"] = output_base / f"{timestamp}.log"

    ensure_output_dir(paths["output_dir"])

    return paths, timestamp


# ==============================================================================
# CLI argument parsing and prerequisite validation
# ==============================================================================


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for 1.4_AssembleManifest.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 1.4: Assemble Manifest

Combines linked metadata and tenure map to create final master
sample manifest. Merges CEO tenure information with firm
identifiers to produce complete analysis universe.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(root):
    """Validate all required inputs and prerequisite steps exist."""
    from shared.dependency_checker import validate_prerequisites

    required_files: Dict[str, Path] = {}

    required_steps = {
        "1.2_LinkEntities": "metadata_linked.parquet",
        "1.3_BuildTenureMap": "tenure_monthly.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# ==============================================================================
# Main processing
# ==============================================================================


def main() -> int:
    config = load_config()
    paths, timestamp = setup_paths(config)

    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()

    # Memory tracking at script start
    mem_start = get_process_memory_mb()
    all_memory_values = [mem_start["rss_mb"]]

    stats: Dict[str, Any] = {
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
            "conm",
            "sic",
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

    # Compute manifest input statistics
    print_dual("Computing manifest input statistics...")
    stats["manifest_input"] = compute_manifest_input_stats(metadata, tenure)

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

    # Compute manifest process statistics (after merge, before filtering)
    print_dual("Computing manifest process statistics...")
    stats["manifest_process"] = compute_manifest_process_stats(
        metadata, merged, df_matched, stats
    )

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
    stats["processing"]["min_call_threshold"] = min_calls

    # Drop temporary columns
    df_final = df_final.drop(columns=["year", "month"])

    # Sort for determinism
    df_final = df_final.sort_values("file_name").reset_index(drop=True)

    # Compute manifest output statistics
    print_dual("Computing manifest output statistics...")
    stats["manifest_output"] = compute_manifest_output_stats(df_final)

    # Collect CEO distribution samples
    print_dual("Collecting CEO distribution samples...")
    stats["ceo_samples"] = collect_ceo_distribution_samples(df_final, n_samples=5)

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

    # Generate comprehensive manifest report
    print_dual("Generating comprehensive manifest report...")
    report_file = paths["output_dir"] / "report_step_1_4.md"

    # Build comprehensive report
    report_lines = [
        "# Step 1.4: Manifest Assembly & CEO Filtering - Report",
        "",
        f"**Timestamp**: {timestamp}",
        "",
    ]

    # INPUT DATA SOURCES section
    report_lines.extend(
        [
            "## INPUT DATA SOURCES",
            "",
            "### Linked Metadata (from step 1.2)",
            "",
        ]
    )

    if "manifest_input" in stats and "linked_metadata" in stats["manifest_input"]:
        input_meta = stats["manifest_input"]["linked_metadata"]
        report_lines.extend(
            [
                f"- **Total calls**: {input_meta.get('total_calls', 0):,}",
                f"- **Unique firms (gvkey)**: {input_meta.get('unique_gvkey', 0):,}",
                f"- **Columns**: {input_meta.get('columns', 0)}",
                f"- **Memory footprint**: {input_meta.get('memory_mb', 0):.2f} MB",
                "",
            ]
        )

    if "manifest_input" in stats and "industry_coverage" in stats["manifest_input"]:
        ind_cov = stats["manifest_input"]["industry_coverage"]
        report_lines.extend(
            [
                "**Industry coverage:**",
                f"- FF12 unique industries: {ind_cov.get('ff12_count', 0)}",
                f"- FF48 unique industries: {ind_cov.get('ff48_count', 0)}",
                "",
            ]
        )

    if "manifest_input" in stats and "temporal_coverage" in stats["manifest_input"]:
        temp_cov = stats["manifest_input"]["temporal_coverage"]
        if "year_range" in temp_cov:
            yr = temp_cov["year_range"]
            report_lines.extend(
                [
                    "**Temporal range:**",
                    f"- Earliest call: {yr.get('earliest', 'N/A')}",
                    f"- Latest call: {yr.get('latest', 'N/A')}",
                    "",
                ]
            )

    # CEO Tenure Panel section
    report_lines.extend(
        [
            "### CEO Tenure Panel (from step 1.3)",
            "",
        ]
    )

    if "manifest_input" in stats and "tenure_panel" in stats["manifest_input"]:
        tenure = stats["manifest_input"]["tenure_panel"]
        report_lines.extend(
            [
                f"- **Total firm-months**: {tenure.get('total_firm_months', 0):,}",
                f"- **Unique firms**: {tenure.get('unique_firms', 0):,}",
                f"- **Unique CEOs**: {tenure.get('unique_ceos', 0):,}",
            ]
        )
        if "date_range" in tenure:
            dr = tenure["date_range"]
            report_lines.extend(
                [
                    f"- **Date coverage**: {dr.get('earliest', 'N/A')} to {dr.get('latest', 'N/A')} ({dr.get('span_years', 0)} years)",
                ]
            )
        report_lines.append("")

    # MERGE PROCESS section
    report_lines.extend(
        [
            "## MERGE PROCESS",
            "",
            "### Join Outcome",
            "",
        ]
    )

    if "manifest_process" in stats and "merge_outcome" in stats["manifest_process"]:
        mo = stats["manifest_process"]["merge_outcome"]
        report_lines.extend(
            [
                f"- **Left rows (metadata)**: {mo.get('left_rows', 0):,}",
                f"- **Right rows (tenure)**: {mo.get('right_rows', 0):,}",
                f"- **Matched calls**: {mo.get('matched_count', 0):,}",
                f"- **Unmatched calls**: {mo.get('unmatched_count', 0):,}",
                f"- **Match rate**: {mo.get('match_rate_pct', 0):.2f}%",
                "",
                "*Join on (gvkey, year, month) with 6-digit zero-padded gvkey*",
                "",
            ]
        )

    # Match rate by year table
    if (
        "manifest_process" in stats
        and "match_rate_by_year" in stats["manifest_process"]
    ):
        report_lines.extend(
            [
                "### Match Rate by Year",
                "",
                "| Year | Total Calls | Matched Calls | Match Rate % |",
                "|------|-------------|---------------|--------------|",
            ]
        )
        for yr in stats["manifest_process"]["match_rate_by_year"]:
            report_lines.append(
                f"| {yr['year']} | {yr['total_calls']:,} | {yr['matched_calls']:,} | {yr['match_rate_pct']:.1f}% |"
            )
        report_lines.append("")

    # Unmatched analysis
    if (
        "manifest_process" in stats
        and "unmatched_analysis" in stats["manifest_process"]
    ):
        ua = stats["manifest_process"]["unmatched_analysis"]
        report_lines.extend(
            [
                "### Unmatched Analysis",
                "",
                f"- **Unique firms (gvkey) without CEO tenure data**: {ua.get('unique_gvkey_unmatched', 0):,}",
                f"- **Calls unmatched**: {ua.get('calls_unmatched', 0):,}",
                "",
            ]
        )
        if ua.get("temporal_distribution"):
            report_lines.extend(
                [
                    "**Temporal distribution of unmatched calls:**",
                    "",
                    "| Year | Unmatched Calls |",
                    "|------|-----------------|",
                ]
            )
            for yr, count in sorted(ua["temporal_distribution"].items()):
                report_lines.append(f"| {yr} | {count:,} |")
            report_lines.append("")

    # CEO filtering
    if "manifest_process" in stats and "ceo_filtering" in stats["manifest_process"]:
        cf = stats["manifest_process"]["ceo_filtering"]
        report_lines.extend(
            [
                "### CEO Filtering",
                "",
                f"- **Minimum call threshold**: {cf.get('threshold_value', 5)}",
                f"- **CEOs before filter**: {cf.get('total_ceos_before_filter', 0):,}",
                f"- **CEOs above threshold**: {cf.get('ceos_above_threshold', 0):,}",
                f"- **CEOs dropped**: {cf.get('ceos_dropped', 0):,}",
                f"- **Calls dropped**: {cf.get('calls_dropped', 0):,}",
                "",
            ]
        )

    # OUTPUT: FINAL MANIFEST section
    report_lines.extend(
        [
            "## OUTPUT: FINAL MANIFEST",
            "",
            "### Panel Dimensions",
            "",
        ]
    )

    if "manifest_output" in stats and "panel_dimensions" in stats["manifest_output"]:
        pdims = stats["manifest_output"]["panel_dimensions"]
        report_lines.extend(
            [
                f"- **Total calls**: {pdims.get('total_calls', 0):,}",
                f"- **Unique firms (gvkey)**: {pdims.get('unique_gvkey', 0):,}",
                f"- **Unique CEOs**: {pdims.get('unique_ceos', 0):,}",
            ]
        )
        if "date_range" in pdims:
            dr = pdims["date_range"]
            report_lines.extend(
                [
                    f"- **Date range**: {dr.get('earliest', 'N/A')[:10]} to {dr.get('latest', 'N/A')[:10]}",
                ]
            )
        report_lines.append("")

    # Call concentration
    if "manifest_output" in stats and "call_concentration" in stats["manifest_output"]:
        cc = stats["manifest_output"]["call_concentration"]
        if "calls_per_ceo" in cc:
            cpc = cc["calls_per_ceo"]
            report_lines.extend(
                [
                    "### Call Concentration",
                    "",
                    f"- **Mean calls per CEO**: {cpc.get('mean', 0):.2f}",
                    f"- **Median calls per CEO**: {cpc.get('median', 0):.2f}",
                    f"- **Min calls per CEO**: {cpc.get('min', 0)}",
                    f"- **Max calls per CEO**: {cpc.get('max', 0):,}",
                    f"- **Std dev**: {cpc.get('std', 0):.2f}",
                    "",
                ]
            )
        if "distribution_buckets" in cc:
            report_lines.extend(
                [
                    "**Call distribution buckets:**",
                    "",
                    "| Bucket | Count | Percentage |",
                    "|--------|-------|------------|",
                ]
            )
            for bucket_name, bucket_data in cc["distribution_buckets"].items():
                report_lines.append(
                    f"| {bucket_name} | {bucket_data['count']:,} | {bucket_data['pct']:.1f}% |"
                )
            report_lines.append("")

    # Industry coverage FF12
    if (
        "manifest_output" in stats
        and "industry_coverage_ff12" in stats["manifest_output"]
    ):
        ff12 = stats["manifest_output"]["industry_coverage_ff12"]
        if ff12:
            report_lines.extend(
                [
                    "### Industry Coverage (FF12)",
                    "",
                    "| FF12 Code | Industry Name | Call Count | Percentage |",
                    "|-----------|---------------|------------|------------|",
                ]
            )
            for ind in ff12[:10]:  # Top 10
                report_lines.append(
                    f"| {ind['ff12_code']} | {ind['ff12_name']} | {ind['call_count']:,} | {ind['percentage']:.1f}% |"
                )
            report_lines.append("")

    # Industry coverage FF48
    if (
        "manifest_output" in stats
        and "industry_coverage_ff48" in stats["manifest_output"]
    ):
        ff48 = stats["manifest_output"]["industry_coverage_ff48"]
        report_lines.extend(
            [
                "### Industry Coverage (FF48)",
                "",
                f"- **Unique industries**: {ff48.get('unique_industries', 0)}",
                f"- **Completion percentage**: {ff48.get('completion_pct', 0):.1f}%",
                "",
            ]
        )

    # Temporal coverage
    if "manifest_output" in stats and "temporal_coverage" in stats["manifest_output"]:
        tc = stats["manifest_output"]["temporal_coverage"]
        if tc:
            report_lines.extend(
                [
                    "### Temporal Coverage",
                    "",
                    "| Year | Call Count | Unique Firms | Unique CEOs |",
                    "|------|------------|--------------|-------------|",
                ]
            )
            for yr in tc:
                report_lines.append(
                    f"| {yr['year']} | {yr['call_count']:,} | {yr['unique_firms']:,} | {yr['unique_ceos']:,} |"
                )
            report_lines.append("")

    # Predecessor coverage
    if (
        "manifest_output" in stats
        and "predecessor_coverage" in stats["manifest_output"]
    ):
        pc = stats["manifest_output"]["predecessor_coverage"]
        report_lines.extend(
            [
                "### Predecessor Coverage",
                "",
                f"- **Calls with predecessor CEO**: {pc.get('pct_with_prev_ceo', 0):.1f}%",
                f"- **Calls without predecessor**: {pc.get('pct_without_prev_ceo', 0):.1f}%",
                "",
            ]
        )

    # CEO DISTRIBUTION SAMPLES section
    report_lines.extend(
        [
            "## CEO DISTRIBUTION SAMPLES",
            "",
        ]
    )

    # Top CEOs
    if "ceo_samples" in stats and "top_ceos" in stats["ceo_samples"]:
        top_ceos = stats["ceo_samples"]["top_ceos"]
        if top_ceos:
            report_lines.extend(
                [
                    "### Top CEOs by Call Count",
                    "",
                    "| CEO ID | CEO Name | Call Count | Unique Firms | Percentage |",
                    "|--------|----------|------------|--------------|------------|",
                ]
            )
            for ceo in top_ceos:
                report_lines.append(
                    f"| {ceo['ceo_id']} | {ceo['ceo_name']} | {ceo['call_count']:,} | {ceo['unique_firms']} | {ceo['percentage']:.1f}% |"
                )
            report_lines.append("")

    # Bottom CEOs
    if "ceo_samples" in stats and "bottom_ceos" in stats["ceo_samples"]:
        bottom_ceos = stats["ceo_samples"]["bottom_ceos"]
        if bottom_ceos:
            report_lines.extend(
                [
                    "### Bottom CEOs by Call Count (above threshold)",
                    "",
                    "| CEO ID | CEO Name | Call Count | Unique Firms | Percentage |",
                    "|--------|----------|------------|--------------|------------|",
                ]
            )
            for ceo in bottom_ceos:
                report_lines.append(
                    f"| {ceo['ceo_id']} | {ceo['ceo_name']} | {ceo['call_count']} | {ceo['unique_firms']} | {ceo['percentage']:.2f}% |"
                )
            report_lines.append("")

    # Single call CEOs
    if "ceo_samples" in stats and "single_call_ceos" in stats["ceo_samples"]:
        scc = stats["ceo_samples"]["single_call_ceos"]
        report_lines.extend(
            [
                "### Single-Call CEOs",
                "",
                f"- **Count**: {scc.get('count', 0)}",
                f"- **Percentage of all CEOs**: {scc.get('percentage', 0):.1f}%",
                "",
            ]
        )

    # Multi-firm CEOs
    if "ceo_samples" in stats and "multi_firm_ceos" in stats["ceo_samples"]:
        mfc = stats["ceo_samples"]["multi_firm_ceos"]
        if mfc:
            report_lines.extend(
                [
                    "### Multi-Firm CEOs",
                    "",
                    "Sample of CEOs spanning multiple firms:",
                    "",
                    "| CEO ID | CEO Name | Call Count | Firm Count |",
                    "|--------|----------|------------|------------|",
                ]
            )
            for ceo in mfc:
                report_lines.append(
                    f"| {ceo['ceo_id']} | {ceo['ceo_name']} | {ceo['call_count']:,} | {ceo['firm_count']} |"
                )
            report_lines.append("")

    # Next Steps section
    report_lines.extend(
        [
            "## Next Steps",
            "",
            "This manifest defines the **Universe of Analysis**. All text processing",
            "in Step 2 will be restricted to `file_name` values present in this manifest.",
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
        ]
    )

    # Write report
    report_file.write_text("\n".join(report_lines), encoding="utf-8")
    print_dual(f"Report saved: {report_file}")

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
    # Parse arguments and check prerequisites
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent

    # Handle dry-run mode
    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        print("[OK] All prerequisites validated")
        sys.exit(0)

    # Check prerequisites
    check_prerequisites(root)

    # Run main processing
    sys.exit(main())
