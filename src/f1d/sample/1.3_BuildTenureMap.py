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
Dependencies:
    - Requires: Step 1.2
    - Uses: pandas, numpy

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

from f1d.shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    calculate_throughput,
    collect_tenure_samples,
    compute_file_checksum,
    compute_tenure_input_stats,
    compute_tenure_output_stats,
    compute_tenure_process_stats,
    detect_anomalies_zscore,
    get_process_memory_mb,
    print_stat,
    print_stats_summary,
    save_stats,
)
from f1d.shared.path_utils import ensure_output_dir, validate_input_file


def print_dual(msg: str) -> None:
    """Print message both to stdout and via DualWriter if available."""
    print(msg, flush=True)


def load_config() -> Dict[str, Any]:
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# ==============================================================================
# CLI argument parsing and prerequisite validation
# ==============================================================================


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for 1.3_BuildTenureMap.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 1.3: Build Tenure Map

Constructs CEO/firm monthly tenure mapping by tracking CEO
appointments from metadata. Creates panel dataset linking
CEOs to firms over time.
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
        "comp_execucomp.parquet": root
        / "1_Inputs"
        / "Execucomp"
        / "comp_execucomp.parquet",
    }

    required_steps = {
        "1.2_LinkEntities": "metadata_linked.parquet",
    }

    validate_prerequisites(required_files, required_steps)


def setup_paths(config: Dict[str, Any]) -> tuple[Dict[str, Path], str]:
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

    ensure_output_dir(paths["output_dir"])

    return paths, timestamp


def generate_tenure_report(stats, output_dir, print_func=print):
    """
    Generate comprehensive tenure mapping report in markdown format.

    Creates publication-ready report with INPUT, PROCESS, OUTPUT sections,
    including tenure length distribution tables, temporal coverage, and sample episodes.

    Args:
        stats: Statistics dictionary containing tenure_input, tenure_process, tenure_output, tenure_samples
        output_dir: Output directory path
        print_func: Print function to use (defaults to print)
    """
    report_path = output_dir / "report_step_1_3.md"

    lines = []
    lines.append("# Step 1.3: CEO Tenure Map Construction Report")
    lines.append("")
    lines.append(f"Generated: {stats.get('timestamp', 'N/A')}")
    lines.append("")

    # ========================================================================
    # INPUT DATA: EXECUCOMP CEO RECORDS
    # ========================================================================
    lines.append("## INPUT DATA: EXECUCOMP CEO RECORDS")
    lines.append("")

    if "tenure_input" in stats:
        ti = stats["tenure_input"]

        # Overall Execucomp
        if "overall_execucomp" in ti:
            lines.append("### Overall Execucomp")
            lines.append("")
            oe = ti["overall_execucomp"]
            lines.append(f"- **Total records:** {oe.get('total_records', 0):,}")
            lines.append(f"- **Unique firms (gvkey):** {oe.get('unique_gvkey', 0):,}")
            lines.append(
                f"- **Unique executives (execid):** {oe.get('unique_execid', 0):,}"
            )
            if "date_range" in oe:
                dr = oe["date_range"]
                lines.append(
                    f"- **Date range:** {dr.get('earliest_year', 'N/A')} - {dr.get('latest_year', 'N/A')} ({dr.get('span_years', 0)} years)"
                )
            lines.append("")

        # CEO Subset
        if "ceo_subset" in ti:
            lines.append("### CEO Subset")
            lines.append("")
            cs = ti["ceo_subset"]
            lines.append(
                f"- **CEO records:** {cs.get('ceo_records', 0):,} ({cs.get('pct_of_total', 0):.1f}% of total)"
            )
            lines.append(f"- **Unique CEO firms:** {cs.get('unique_ceo_firms', 0):,}")
            lines.append(
                f"- **Unique CEO executives:** {cs.get('unique_ceo_executives', 0):,}"
            )
            lines.append("")

        # Date Field Coverage
        if "date_field_coverage" in ti:
            lines.append("### Date Field Coverage")
            lines.append("")
            dfc = ti["date_field_coverage"]
            lines.append(
                f"- **becameceo available:** {dfc.get('becameceo_available_pct', 0):.1f}%"
            )
            lines.append(
                f"- **leftofc available:** {dfc.get('leftofc_available_pct', 0):.1f}%"
            )
            lines.append("")

        # CEO Indicators
        if "ceo_indicators" in ti:
            lines.append("### CEO Indicators")
            lines.append("")
            ci = ti["ceo_indicators"]
            lines.append(
                f"- **Records with ceoann='CEO':** {ci.get('ceoann_ceo_count', 0):,}"
            )
            lines.append(
                f"- **Records with becameceo non-null:** {ci.get('becameceo_nonnull_count', 0):,}"
            )
            lines.append("")

        # Name Coverage
        if "name_coverage" in ti:
            lines.append("### Executive Name Coverage")
            lines.append("")
            nc = ti["name_coverage"]
            lines.append(
                f"- **exec_fullname available:** {nc.get('exec_fullname_available_pct', 0):.1f}%"
            )
            lines.append("")

    # ========================================================================
    # PROCESS: TENURE EPISODE CONSTRUCTION
    # ========================================================================
    lines.append("## PROCESS: TENURE EPISODE CONSTRUCTION")
    lines.append("")

    if "tenure_process" in stats:
        tp = stats["tenure_process"]

        # Episode Counts
        if "episode_counts" in tp:
            lines.append("### Episode Counts")
            lines.append("")
            ec = tp["episode_counts"]
            lines.append(f"- **Total episodes:** {ec.get('total_episodes', 0):,}")
            if "episodes_per_firm" in ec:
                epf = ec["episodes_per_firm"]
                lines.append(
                    f"- **Episodes per firm:** mean={epf.get('mean', 0):.1f}, median={epf.get('median', 0):.1f}, min={epf.get('min', 0)}, max={epf.get('max', 0)}"
                )
            if "episodes_per_ceo" in ec:
                epc = ec["episodes_per_ceo"]
                lines.append(
                    f"- **Episodes per CEO:** mean={epc.get('mean', 0):.1f}, median={epc.get('median', 0):.1f}, min={epc.get('min', 0)}, max={epc.get('max', 0)}"
                )
            lines.append("")

        # Tenure Length Distribution
        if "tenure_distribution" in tp:
            lines.append("### Tenure Length Distribution")
            lines.append("")
            td = tp["tenure_distribution"]
            lines.append(f"- **Mean:** {td.get('mean_months', 0):.1f} months")
            lines.append(f"- **Median:** {td.get('median_months', 0):.1f} months")
            lines.append(
                f"- **Range:** {td.get('min_months', 0):.1f} - {td.get('max_months', 0):.1f} months"
            )
            lines.append(f"- **Std dev:** {td.get('std_months', 0):.1f} months")
            lines.append("")
            lines.append("| Tenure Bucket | Count | Percentage |")
            lines.append("|---------------|-------|------------|")
            if "buckets" in td:
                buckets = td["buckets"]
                for bucket_name in [
                    "<1 year",
                    "1-3 years",
                    "3-5 years",
                    "5-10 years",
                    "10+ years",
                ]:
                    if bucket_name in buckets:
                        b = buckets[bucket_name]
                        lines.append(
                            f"| {bucket_name} | {b.get('count', 0):,} | {b.get('pct', 0):.1f}% |"
                        )
            lines.append("")

        # Predecessor Linking
        if "predecessor_linking" in tp:
            lines.append("### Predecessor Linking")
            lines.append("")
            pl = tp["predecessor_linking"]
            lines.append(
                f"- **Episodes linked to predecessor:** {pl.get('linked_count', 0):,} ({pl.get('link_rate_pct', 0):.1f}%)"
            )
            lines.append(
                f"- **Orphan episodes (no predecessor):** {pl.get('orphan_count', 0):,}"
            )
            lines.append("")

        # Date Validity
        if "date_validity" in tp:
            lines.append("### Date Validity")
            lines.append("")
            dv = tp["date_validity"]
            lines.append(
                f"- **Episodes with future start dates:** {dv.get('future_dates', 0)}"
            )
            lines.append(
                f"- **Episodes with end before start:** {dv.get('end_before_start', 0)}"
            )
            lines.append(
                f"- **Active CEOs (end date imputed):** {dv.get('active_ceo_count', 0)}"
            )
            lines.append("")

    # ========================================================================
    # OUTPUT: MONTHLY TENURE PANEL
    # ========================================================================
    lines.append("## OUTPUT: MONTHLY TENURE PANEL")
    lines.append("")

    if "tenure_output" in stats:
        tos = stats["tenure_output"]

        # Panel Dimensions
        if "panel_dimensions" in tos:
            lines.append("### Panel Dimensions")
            lines.append("")
            pdim = tos["panel_dimensions"]
            lines.append(
                f"- **Total firm-months:** {pdim.get('total_firm_months', 0):,}"
            )
            lines.append(f"- **Unique firms:** {pdim.get('unique_firms', 0):,}")
            lines.append(f"- **Unique CEOs:** {pdim.get('unique_ceos', 0):,}")
            if "date_range" in pdim:
                dr = pdim["date_range"]
                lines.append(
                    f"- **Date range:** {dr.get('earliest', 'N/A')} to {dr.get('latest', 'N/A')} ({dr.get('span_years', 0):.1f} years)"
                )
            lines.append("")

        # Temporal Coverage
        if "temporal_coverage" in tos:
            lines.append("### Temporal Coverage")
            lines.append("")
            lines.append("| Year | Firm-Months | Unique Firms | Unique CEOs |")
            lines.append("|------|-------------|--------------|-------------|")
            for year_data in tos["temporal_coverage"]:
                lines.append(
                    f"| {year_data.get('year', 'N/A')} | {year_data.get('firm_months', 0):,} | {year_data.get('unique_firms', 0):,} | {year_data.get('unique_ceos', 0):,} |"
                )
            lines.append("")

        # CEO Turnover
        if "turnover_metrics" in tos:
            lines.append("### CEO Turnover")
            lines.append("")
            tm = tos["turnover_metrics"]
            lines.append(f"- **Turnover events:** {tm.get('turnover_events', 0):,}")
            lines.append(
                f"- **Turnover rate:** {tm.get('turnover_rate_per_100_firm_years', 0):.1f} per 100 firm-years"
            )
            lines.append("")

        # Predecessor Coverage
        if "predecessor_coverage" in tos:
            lines.append("### Predecessor Coverage")
            lines.append("")
            pc = tos["predecessor_coverage"]
            lines.append(
                f"- **Firm-months with predecessor info:** {pc.get('with_predecessor_pct', 0):.1f}%"
            )
            lines.append(
                f"- **Firm-months without predecessor:** {pc.get('without_predecessor_pct', 0):.1f}%"
            )
            lines.append("")

        # Multi-CEO Firms
        if "multi_ceo_analysis" in tos:
            lines.append("### Multi-CEO Firms")
            lines.append("")
            mc = tos["multi_ceo_analysis"]
            lines.append(
                f"- **Firms with multiple CEOs:** {mc.get('firms_with_multiple_ceos', 0):,}"
            )
            lines.append(
                f"- **Maximum CEOs per firm:** {mc.get('max_ceos_per_firm', 0)}"
            )
            lines.append("")

        # CEO Careers
        if "ceo_careers" in tos:
            lines.append("### CEO Career Analysis")
            lines.append("")
            cc = tos["ceo_careers"]
            lines.append(
                f"- **CEOs spanning multiple firms:** {cc.get('ceos_multiple_firms', 0):,}"
            )
            lines.append("")

    # ========================================================================
    # SAMPLE EPISODES AND TRANSITIONS
    # ========================================================================
    lines.append("## SAMPLE EPISODES AND TRANSITIONS")
    lines.append("")

    if "tenure_samples" in stats:
        ts = stats["tenure_samples"]

        # Short Tenures
        if "short_tenures" in ts and len(ts["short_tenures"]) > 0:
            lines.append("### Short Tenure Examples (<1 year)")
            lines.append("")
            lines.append(
                "| GVKEY | CEO Name | Start Date | End Date | Tenure (Months) |"
            )
            lines.append(
                "|-------|----------|------------|----------|-----------------|"
            )
            for sample in ts["short_tenures"]:
                lines.append(
                    f"| {sample.get('gvkey', 'N/A')} | {sample.get('ceo_name', 'N/A')} | {sample.get('start_date', 'N/A')[:10]} | {sample.get('end_date', 'N/A')[:10]} | {sample.get('tenure_months', 0):.1f} |"
                )
            lines.append("")

        # Long Tenures
        if "long_tenures" in ts and len(ts["long_tenures"]) > 0:
            lines.append("### Long Tenure Examples (10+ years)")
            lines.append("")
            lines.append(
                "| GVKEY | CEO Name | Start Date | End Date | Tenure (Months) |"
            )
            lines.append(
                "|-------|----------|------------|----------|-----------------|"
            )
            for sample in ts["long_tenures"]:
                lines.append(
                    f"| {sample.get('gvkey', 'N/A')} | {sample.get('ceo_name', 'N/A')} | {sample.get('start_date', 'N/A')[:10]} | {sample.get('end_date', 'N/A')[:10]} | {sample.get('tenure_months', 0):.1f} |"
                )
            lines.append("")

        # Transitions
        if "transitions" in ts and len(ts["transitions"]) > 0:
            lines.append("### CEO Transition Examples")
            lines.append("")
            lines.append(
                "| GVKEY | Predecessor CEO | Successor CEO | Transition Date | Gap Days |"
            )
            lines.append(
                "|-------|-----------------|---------------|-----------------|----------|"
            )
            for sample in ts["transitions"]:
                gap = sample.get("gap_days")
                gap_str = f"{gap}" if gap is not None else "N/A"
                lines.append(
                    f"| {sample.get('gvkey', 'N/A')} | {sample.get('prev_ceo_name', 'N/A')} | {sample.get('new_ceo_name', 'N/A')} | {sample.get('transition_date', 'N/A')[:10]} | {gap_str} |"
                )
            lines.append("")

        # Overlaps
        if "overlaps" in ts and len(ts["overlaps"]) > 0:
            lines.append("### Overlap Resolution Examples")
            lines.append("")
            lines.append(
                "| GVKEY | Resolved CEO | Overlapped CEO | Period | Resolution |"
            )
            lines.append(
                "|-------|--------------|----------------|--------|------------|"
            )
            for sample in ts["overlaps"]:
                lines.append(
                    f"| {sample.get('gvkey', 'N/A')} | {sample.get('resolved_ceo', 'N/A')} | {sample.get('overlapped_ceo', 'N/A')} | {sample.get('overlap_period', 'N/A')} | {sample.get('resolution_reason', 'N/A')} |"
                )
            lines.append("")

    # Write report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print_func(f"Generated tenure mapping report: {report_path.name}")


# ==============================================================================
# Dual-write logging utility
# ==============================================================================


def main() -> int:
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

    stats: Dict[str, Any] = {
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
    ceo_records: pd.DataFrame = df[(df["ceoann"] == "CEO") | (df["becameceo"].notna())].copy()  # type: ignore[assignment]
    print_dual(f"  Found {len(ceo_records):,} CEO-related records")
    print_dual(f"  Unique firms (gvkey): {ceo_records['gvkey'].nunique():,}")
    print_dual(f"  Unique executives (execid): {ceo_records['execid'].nunique():,}\n")

    stats["processing"]["ceo_filter"] = stats["input"]["total_rows"] - len(ceo_records)
    print_stat("Records filtered (non-CEO)", value=stats["processing"]["ceo_filter"])

    # Collect tenure input statistics
    print_dual("Computing tenure input statistics...")
    stats["tenure_input"] = compute_tenure_input_stats(df, ceo_records)

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

    for gvkey, group in episodes_df.groupby("gvkey"):  # type: ignore[assignment]
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

    # Collect tenure process statistics
    print_dual("Computing tenure process statistics...")
    stats["tenure_process"] = compute_tenure_process_stats(episodes_df)

    # Expand to monthly panel
    print_dual("Expanding to monthly panel...")

    monthly_records = []
    total_episodes = len(episodes_df)
    progress_interval = max(500, total_episodes // 20)

    for i, (_idx, row) in enumerate(episodes_df.iterrows(), 1):
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

    # Collect tenure output statistics and samples
    print_dual("Computing tenure output statistics...")
    stats["tenure_output"] = compute_tenure_output_stats(monthly_df)

    print_dual("Collecting tenure samples...")
    stats["tenure_samples"] = collect_tenure_samples(
        episodes_df, monthly_df, n_samples=3
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

    # Generate tenure mapping report
    print_dual("\nGenerating tenure mapping report...")
    generate_tenure_report(stats, paths["output_dir"], print_dual)

    # Save stats JSON
    save_stats(stats, paths["output_dir"])

    print_dual("\n" + "=" * 80)
    print_dual("Step 1.3 completed successfully.")
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
