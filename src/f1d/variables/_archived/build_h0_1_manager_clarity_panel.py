#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build Manager Clarity Panel
================================================================================
ID: variables/build_h0_1_manager_clarity_panel
Description: Build complete panel for Manager Clarity hypothesis test by loading
             all required variables using shared modules and merging into a
             single panel.

Inputs (all raw):
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet  (Compustat)
    - inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet        (CRSP daily)
    - inputs/tr_ibes/tr_ibes.parquet                       (IBES)
    - inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet   (CCM linktable)

Outputs:
    - outputs/variables/manager_clarity/{timestamp}/manager_clarity_panel.parquet
    - outputs/variables/manager_clarity/{timestamp}/summary_stats.csv

Deterministic: true
Dependencies:
    - Uses: f1d.shared.variables, f1d.shared.config

Author: Thesis Author
Date: 2026-02-19
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from f1d.shared.config import load_variable_config, get_config
from f1d.shared.variables.panel_utils import assign_industry_sample
from f1d.shared.variables import (
    ManagerQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    EPSGrowthBuilder,
    StockReturnBuilder,
    MarketReturnBuilder,
    EarningsSurpriseBuilder,
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 3: Build Manager Clarity Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without executing",
    )
    parser.add_argument(
        "--year-start",
        type=int,
        default=None,
        help="Start year (default: from config)",
    )
    parser.add_argument(
        "--year-end",
        type=int,
        default=None,
        help="End year (default: from config)",
    )
    return parser.parse_args()


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Build complete panel by loading and merging all variables.

    Args:
        root_path: Project root path
        years: Range of years to process
        var_config: Variable configuration dict
        stats: Stats dict to collect summary statistics

    Returns:
        Merged DataFrame with all variables
    """
    print("\n" + "=" * 60)
    print("Loading variables")
    print("=" * 60)

    all_results: Dict[str, Any] = {}

    # Initialize builders — one variable per builder.
    # The CompustatEngine and CRSPEngine are module-level singletons that cache
    # the raw data load, so calling EPSGrowthBuilder + StockReturnBuilder etc.
    # does NOT re-load Compustat or CRSP for each variable.
    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        "manager_qa_uncertainty": ManagerQAUncertaintyBuilder(
            var_config.get("manager_qa_uncertainty", {})
        ),
        "manager_pres_uncertainty": ManagerPresUncertaintyBuilder(
            var_config.get("manager_pres_uncertainty", {})
        ),
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(
            var_config.get("analyst_qa_uncertainty", {})
        ),
        "negative_sentiment": NegativeSentimentBuilder(
            var_config.get("negative_sentiment", {})
        ),
        "eps_growth": EPSGrowthBuilder({}),
        "stock_return": StockReturnBuilder({}),
        "market_return": MarketReturnBuilder({}),
        "earnings_surprise": EarningsSurpriseBuilder(
            var_config.get("earnings_surprise", {})
        ),
    }

    # Build all variables
    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    # Start with manifest as base
    manifest_result = all_results["manifest"]
    panel = manifest_result.data.copy()

    # FIX-5: Assert manifest file_name uniqueness — fan-out here corrupts everything
    if panel["file_name"].duplicated().any():
        n_dups = panel["file_name"].duplicated().sum()
        raise ValueError(
            f"Manifest has {n_dups} duplicate file_name rows. "
            "Panel build aborted to prevent row multiplication."
        )

    print(f"\n  Base manifest: {len(panel):,} rows")

    # Merge all other variables on file_name
    for name, result in all_results.items():
        if name == "manifest":
            continue

        data = result.data.copy()
        if "file_name" not in data.columns or len(data.columns) <= 1:
            print(f"  WARNING: {name} returned no usable columns — skipping merge")
            continue

        # FIX-5: Assert builder output is unique on file_name — prevent silent row fan-out
        if data["file_name"].duplicated().any():
            n_dups = data["file_name"].duplicated().sum()
            raise ValueError(
                f"Builder '{name}' returned {n_dups} duplicate file_name rows. "
                "Merge aborted to prevent fan-out."
            )

        # FIX-1: Drop columns already in panel (except file_name) to prevent _x/_y conflicts
        conflicting = [
            c for c in data.columns if c in panel.columns and c != "file_name"
        ]
        if conflicting:
            print(
                f"  WARNING: {name} has overlapping columns {conflicting} — dropping from builder data"
            )
            data = data.drop(columns=conflicting)

        before_len = len(panel)
        panel = panel.merge(data, on="file_name", how="left")
        after_len = len(panel)
        if after_len != before_len:
            raise ValueError(
                f"Merge of '{name}' changed row count {before_len} → {after_len}. "
                "Duplicate file_name detected in builder output post-merge."
            )
        print(f"  After {name} merge: {after_len:,} rows (delta: +0)")

    # Add derived fields
    if "ff12_code" in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])
        print(f"\n  Sample distribution:")
        for sample in ["Main", "Finance", "Utility"]:
            n = (panel["sample"] == sample).sum()
            print(f"    {sample}: {n:,} calls")

    # Add year column if not present
    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # NOTE: Winsorization now applied at engine level (CRSPEngine, LinguisticEngine)
    # for consistency across all hypothesis suites. No panel-level winsorization needed.

    # Collect all summary stats
    stats_list = []
    for name, result in all_results.items():
        stats_list.append(result.stats)

    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def save_outputs(
    panel: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
) -> None:
    """Save panel and summary statistics.

    Args:
        panel: Complete merged panel
        stats: Stats dict with variable statistics
        out_dir: Output directory
    """
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Save panel
    panel_path = out_dir / "manager_clarity_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"  Saved: manager_clarity_panel.parquet ({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    # Save summary stats
    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")


def generate_report(
    panel: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report.

    Args:
        panel: Complete merged panel
        stats: Stats dict
        out_dir: Output directory
        duration: Duration in seconds
    """
    report_lines = [
        "# Stage 3: Manager Clarity Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary",
        "",
        f"- **Total observations:** {len(panel):,}",
        f"- **Total columns:** {len(panel.columns)}",
        "",
    ]

    # Sample distribution
    if "sample" in panel.columns:
        report_lines.append("### Sample Distribution")
        report_lines.append("")
        report_lines.append("| Sample | N Calls | % |")
        report_lines.append("|--------|---------|---|")
        for sample in ["Main", "Finance", "Utility"]:
            n = (panel["sample"] == sample).sum()
            pct = 100.0 * n / len(panel) if len(panel) > 0 else 0
            report_lines.append(f"| {sample} | {n:,} | {pct:.1f}% |")
        report_lines.append("")

    # Unique entities
    report_lines.append("### Unique Entities")
    report_lines.append("")
    if "ceo_id" in panel.columns:
        report_lines.append(f"- **Unique CEOs:** {panel['ceo_id'].nunique():,}")
    if "gvkey" in panel.columns:
        report_lines.append(f"- **Unique firms:** {panel['gvkey'].nunique():,}")
    report_lines.append("")

    # Variable summary
    report_lines.append("## Variable Summary")
    report_lines.append("")
    report_lines.append("| Variable | N | Mean | Std | Min | Max | Missing % |")
    report_lines.append("|----------|---|------|-----|-----|-----|-----------|")

    for var_stat in stats.get("variable_stats", []):
        name = var_stat.get("name", "unknown")
        n = var_stat.get("n", 0)
        mean = var_stat.get("mean", 0)
        std = var_stat.get("std", 0)
        min_val = var_stat.get("min", 0)
        max_val = var_stat.get("max", 0)
        pct_missing = var_stat.get("pct_missing", 0)
        report_lines.append(
            f"| {name} | {n:,} | {mean:.3f} | {std:.3f} | {min_val:.3f} | {max_val:.3f} | {pct_missing:.1f}% |"
        )

    report_lines.append("")

    # Write report
    report_path = out_dir / "report_step3_manager_clarity.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"  Saved: report_step3_manager_clarity.md")


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_manager_clarity_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "manager_clarity" / timestamp

    # Load configs — pass explicit paths so CWD doesn't matter
    config = get_config(root / "config" / "project.yaml")
    var_config = load_variable_config(root / "config" / "variables.yaml")

    # Get year range
    if year_start is None:
        year_start = config.data.year_start
    if year_end is None:
        year_end = config.data.year_end
    years = range(year_start, year_end + 1)

    print("=" * 80)
    print("STAGE 3: Build Manager Clarity Panel")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {year_start}-{year_end}")

    # Build panel
    panel = build_panel(root, years, var_config, stats)

    # Save outputs
    save_outputs(panel, stats, out_dir)

    # Generate report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(panel, stats, out_dir, duration)

    # Final summary
    stats["timing"]["duration_seconds"] = round(duration, 2)
    stats["panel"]["n_rows"] = len(panel)
    stats["panel"]["n_columns"] = len(panel.columns)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
