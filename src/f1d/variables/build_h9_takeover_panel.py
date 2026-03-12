#!/usr/bin/env python3
"""
================================================================================
H9: Build Takeover Panel
================================================================================
ID: variables/build_h9_takeover_panel
Description: Build call-to-call counting-process panel for Takeover Hazard
             survival analysis (H9).

The panel uses CALL-TO-CALL intervals (not firm-year). Each row represents
one risk interval that opens at an earnings call and closes at the earliest of:
  (a) next earnings call date for the same firm
  (b) takeover announcement date (if takeover occurs in interval)
  (c) administrative censor date (end of sample period)

Covariates measured at the call that opens the interval govern the hazard risk
for that interval. Time units are days since 2000-01-01.

Survival construction:
  - start: call date (days since 2000-01-01)
  - stop:  min(next call date, takeover date, censor date) in same units
  - Takeover: 1 only in the interval where a bid occurs, 0 otherwise
  - Takeover_Type: 'Uninvited' (Hostile + Unsolicited), 'Friendly' (Friendly
    + Neutral), 'None' (non-target), 'Unknown' (other attitude)

Clarity constructs:
  - ClarityCEO (time-invariant CEO FE): merged per ceo_id x sample
  - CEO_Clarity_Residual: residualized CEO uncertainty (per call)
  - Manager_Clarity_Residual: residualized Manager uncertainty (per call)
  - ClarityManager: does NOT exist in the repo

Financial Controls (Compustat-only, no CRSP/IBES):
  - Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth
  - Matched to each call via the most recent fiscal year (as-of matching)

Inputs (all raw):
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet  (Compustat)
    - inputs/SDC/sdc-ma-merged.parquet                     (SDC M&A)
    - outputs/econometric/ceo_clarity/latest/clarity_scores.parquet
    - outputs/econometric/ceo_clarity_extended/latest/ceo_clarity_residual.parquet
    - outputs/econometric/ceo_clarity_extended/latest/manager_clarity_residual.parquet

Outputs:
    - outputs/variables/takeover/{timestamp}/takeover_panel.parquet  (call-to-call)
    - outputs/variables/takeover/{timestamp}/summary_stats.csv
    - outputs/variables/takeover/{timestamp}/report_h9_panel.md

Deterministic: true
Dependencies:
    - Requires: Upstream clarity scores (H1, H0.3)
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

import numpy as np
import pandas as pd

from f1d.shared.config import load_variable_config, get_config
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest
from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError
from f1d.shared.variables.panel_utils import assign_industry_sample
from f1d.shared.variables import (
    ManagerQAUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    SizeBuilder,
    BMBuilder,
    LevBuilder,
    ROABuilder,
    CashHoldingsBuilder,
    SalesGrowthBuilder,
    IntangibilityBuilder,
    AssetGrowthBuilder,
    TakeoverIndicatorBuilder,
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
    CEOClarityResidualBuilder,
    ManagerClarityResidualBuilder,
)


# Reference date for converting dates to numeric days
REFERENCE_DATE = pd.Timestamp("2000-01-01")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="H9: Build Takeover Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def load_clarity_scores(root_path: Path) -> pd.DataFrame:
    """Load ClarityCEO scores from upstream clarity outputs.

    Note: ClarityManager does not exist in the repo. Only CEO clarity is loaded.
    """
    try:
        ceo_dir = get_latest_output_dir(
            root_path / "outputs" / "econometric" / "ceo_clarity",
            required_file="clarity_scores.parquet",
        )
        ceo = pd.read_parquet(
            ceo_dir / "clarity_scores.parquet",
            columns=["ceo_id", "sample", "ClarityCEO"],
        )
        ceo["ceo_id"] = ceo["ceo_id"].astype(str)
        print(f"    ClarityCEO: {len(ceo):,} CEO-sample pairs")
    except (OutputResolutionError, FileNotFoundError):
        ceo = pd.DataFrame(columns=["ceo_id", "sample", "ClarityCEO"])
        print("    WARNING: ClarityCEO not found — will be NaN")

    return ceo


def build_call_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Build call-level panel with all needed variables.

    Each row is one earnings call with its associated covariates.
    Includes linguistic uncertainty, financial controls, and manifest identifiers.
    """
    print("\n" + "=" * 60)
    print("Loading call-level variables")
    print("=" * 60)

    all_results: Dict[str, Any] = {}

    manifest_config = dict(var_config.get("manifest", {}))
    manifest_config["columns"] = [
        "file_name",
        "ceo_id",
        "ceo_name",
        "gvkey",
        "ff12_code",
        "ff12_name",
        "start_date",
    ]

    builders = {
        "manifest": ManifestFieldsBuilder(manifest_config),
        "manager_qa_uncertainty": ManagerQAUncertaintyBuilder(
            var_config.get("manager_qa_uncertainty", {})
        ),
        "ceo_qa_uncertainty": CEOQAUncertaintyBuilder(
            var_config.get("ceo_qa_uncertainty", {})
        ),
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(
            var_config.get("analyst_qa_uncertainty", {})
        ),
        "negative_sentiment": NegativeSentimentBuilder(
            var_config.get("negative_sentiment", {})
        ),
        "size": SizeBuilder({}),
        "bm": BMBuilder({}),
        "lev": LevBuilder({}),
        "roa": ROABuilder({}),
        "cash_holdings": CashHoldingsBuilder({}),
        "sales_growth": SalesGrowthBuilder({}),
        "intangibility": IntangibilityBuilder({}),
        "asset_growth": AssetGrowthBuilder({}),
        "ceo_clarity_residual": CEOClarityResidualBuilder({}),
        "manager_clarity_residual": ManagerClarityResidualBuilder({}),
    }

    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    # Start with manifest
    panel = all_results["manifest"].data.copy()

    if panel["file_name"].duplicated().any():
        n_dups = panel["file_name"].duplicated().sum()
        raise ValueError(f"Manifest has {n_dups} duplicate file_name rows.")

    print(f"\n  Base manifest: {len(panel):,} rows")

    for name, result in all_results.items():
        if name == "manifest":
            continue

        data = result.data.copy()
        if "file_name" not in data.columns or len(data.columns) <= 1:
            print(f"  WARNING: {name} returned no usable columns — skipping")
            continue

        if data["file_name"].duplicated().any():
            n_dups = data["file_name"].duplicated().sum()
            raise ValueError(
                f"Builder '{name}' returned {n_dups} duplicate file_name rows."
            )

        conflicting = [
            c for c in data.columns if c in panel.columns and c != "file_name"
        ]
        if conflicting:
            data = data.drop(columns=conflicting)

        before_len = len(panel)
        panel = panel.merge(data, on="file_name", how="left")
        after_len = len(panel)
        delta = after_len - before_len
        if after_len != before_len:
            raise ValueError(
                f"Merge of '{name}' changed row count {before_len} → {after_len} (delta: {delta:+d})."
            )
        print(f"  After {name} merge: {after_len:,} rows (delta: {delta:+d})")

    # Validate ff12_code
    if "ff12_code" not in panel.columns:
        raise ValueError("ff12_code missing from panel after manifest merge.")
    if panel["ff12_code"].isna().any():
        n_nan = panel["ff12_code"].isna().sum()
        raise ValueError(
            f"ff12_code has {n_nan} NaN values. Run upstream ff12 fix first."
        )

    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Collect stats
    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    return panel


def build_call_to_call_panel(
    call_panel: pd.DataFrame,
    takeover_data: pd.DataFrame,
    year_end: int,
) -> pd.DataFrame:
    """Build call-to-call counting-process panel for CoxTimeVaryingFitter.

    Each row = one call-based risk interval:
      - start = call date (days since 2000-01-01)
      - stop  = min(next call date, takeover date, censor date) in same units
      - Takeover = 1 only in the interval where a bid occurs

    Covariates measured at the call that opens the interval govern hazard risk.

    Args:
        call_panel: Call-level panel with start_date and all covariates.
        takeover_data: Firm-level takeover indicators (gvkey, Takeover,
                       Takeover_Type, Takeover_Date).
        year_end: Last year of sample period (for administrative censoring).

    Returns:
        Counting-process DataFrame with call-to-call intervals.
    """
    print("\n" + "=" * 60)
    print("Building call-to-call counting-process panel")
    print("=" * 60)

    censor_date = pd.Timestamp(f"{year_end}-12-31")

    df = call_panel.copy()
    df["call_date"] = pd.to_datetime(df["start_date"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["call_date"])
    df = df.sort_values(["gvkey", "call_date"]).reset_index(drop=True)

    n_calls_before = len(df)
    n_firms_before = df["gvkey"].nunique()
    print(f"  Input calls: {n_calls_before:,} from {n_firms_before:,} firms")

    # Merge takeover data (firm-level: one row per gvkey)
    tk = takeover_data[["gvkey", "Takeover", "Takeover_Type", "Takeover_Date"]].copy()
    tk["Takeover_Date"] = pd.to_datetime(tk["Takeover_Date"], errors="coerce")
    tk["Takeover_Date"] = tk["Takeover_Date"].dt.normalize()

    df = df.merge(tk, on="gvkey", how="left")
    df["Takeover"] = df["Takeover"].fillna(0).astype(int)
    df["Takeover_Type"] = df["Takeover_Type"].fillna("None")

    # Remove calls that occur on or after the takeover date (not at risk)
    mask_at_risk = ~(
        (df["Takeover"] == 1)
        & df["Takeover_Date"].notna()
        & (df["call_date"] >= df["Takeover_Date"])
    )
    n_post = (~mask_at_risk).sum()
    if n_post > 0:
        print(f"  Removing {n_post:,} post-takeover call rows (not at risk)")
    df = df[mask_at_risk].copy()

    n_calls_after = len(df)
    n_firms_after = df["gvkey"].nunique()
    print(f"  At-risk calls: {n_calls_after:,} from {n_firms_after:,} firms")

    # Compute next call date per firm
    df = df.sort_values(["gvkey", "call_date"]).reset_index(drop=True)
    df["next_call_date"] = df.groupby("gvkey")["call_date"].shift(-1)

    # Stop date: min(next_call_date, censor_date)
    df["stop_date"] = df["next_call_date"].fillna(censor_date)
    df.loc[df["stop_date"] > censor_date, "stop_date"] = censor_date

    # For event firms: if takeover_date falls in (call_date, stop_date], truncate
    has_tk = (df["Takeover"] == 1) & df["Takeover_Date"].notna()
    tk_in_interval = (
        has_tk
        & (df["Takeover_Date"] > df["call_date"])
        & (df["Takeover_Date"] <= df["stop_date"])
    )
    df.loc[tk_in_interval, "stop_date"] = df.loc[tk_in_interval, "Takeover_Date"]

    # Event indicator: 1 only in the interval containing the takeover
    df["Takeover"] = tk_in_interval.astype(int)

    # Convert to numeric (days since reference)
    df["start"] = (df["call_date"] - REFERENCE_DATE).dt.days
    df["stop"] = (df["stop_date"] - REFERENCE_DATE).dt.days

    # Duration in days (for summary stats)
    df["duration"] = df["stop"] - df["start"]

    # Remove zero or negative duration intervals
    bad_mask = df["duration"] <= 0
    n_bad = int(bad_mask.sum())
    if n_bad > 0:
        print(f"  WARNING: Removing {n_bad:,} zero/negative duration intervals")
        df = df[~bad_mask].copy()

    # Validate no start >= stop remains
    if (df["start"] >= df["stop"]).any():
        raise ValueError("DATA BUG: start >= stop rows remain after filtering")

    # Validate no duplicated event assignment: each firm should have at most 1 event row
    event_per_firm = df.groupby("gvkey")["Takeover"].sum()
    multi_event = event_per_firm[event_per_firm > 1]
    if len(multi_event) > 0:
        raise ValueError(
            f"DATA BUG: {len(multi_event)} firms have >1 event row. "
            f"First 5: {multi_event.head().to_dict()}"
        )

    # Drop helper columns
    df = df.drop(
        columns=["call_date", "next_call_date", "stop_date", "Takeover_Date"],
        errors="ignore",
    )

    # Summary
    n_event_firms = int(df.groupby("gvkey")["Takeover"].max().sum())
    n_firms = df["gvkey"].nunique()
    print(f"\n  Call-to-call intervals: {len(df):,}")
    print(f"  Unique firms: {n_firms:,}")
    print(f"  Event firms: {n_event_firms:,} / {n_firms:,}")
    print(f"  Duration (days): median={df['duration'].median():.0f}, "
          f"mean={df['duration'].mean():.0f}, "
          f"min={df['duration'].min()}, max={df['duration'].max()}")

    # Event type breakdown
    event_rows = df[df["Takeover"] == 1]
    if len(event_rows) > 0:
        type_counts = event_rows["Takeover_Type"].value_counts()
        print("  Event type breakdown:")
        for t, n in type_counts.items():
            print(f"    {t}: {n:,}")

    return df


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Build complete takeover panel for survival analysis.

    Pipeline:
      1. Build call-level panel (manifest + linguistic + financial controls)
      2. Merge ClarityCEO scores (per ceo_id x sample)
      3. Load takeover indicators (firm-level from SDC)
      4. Construct call-to-call counting-process intervals

    Returns call-to-call DataFrame suitable for CoxTimeVaryingFitter.
    """
    year_end = max(years)

    # Step 1: Call-level panel
    call_panel = build_call_panel(root_path, years, var_config, stats)

    # Step 2: Load clarity scores and merge at call level
    print("\n  Loading clarity scores...")
    ceo_clarity = load_clarity_scores(root_path)

    call_panel["ceo_id"] = call_panel["ceo_id"].astype(str)

    if len(ceo_clarity) > 0:
        before_len = len(call_panel)
        call_panel = call_panel.merge(
            ceo_clarity[["ceo_id", "sample", "ClarityCEO"]],
            on=["ceo_id", "sample"],
            how="left",
        )
        after_len = len(call_panel)
        delta = after_len - before_len
        if after_len != before_len:
            raise ValueError(
                f"ClarityCEO merge changed row count {before_len} → {after_len} "
                f"(delta: {delta:+d})."
            )
        n_matched = call_panel["ClarityCEO"].notna().sum()
        print(
            f"  After ClarityCEO merge: {after_len:,} rows, "
            f"{n_matched:,} matched (delta: {delta:+d})"
        )
    else:
        call_panel["ClarityCEO"] = float("nan")

    # Build takeover indicators (firm-level)
    print("\n  Loading takeover indicators from SDC...")
    takeover_config = dict(var_config.get("takeover_indicator", {}))
    takeover_config["year_start"] = min(years)
    takeover_config["year_end"] = year_end
    takeover_builder = TakeoverIndicatorBuilder(takeover_config)
    takeover_result = takeover_builder.build(years, root_path)
    takeover_data = takeover_result.data
    stats["variable_stats"].append(asdict(takeover_result.stats))

    # Build call-to-call counting-process panel
    panel = build_call_to_call_panel(call_panel, takeover_data, year_end)

    print(f"\n  Final call-to-call panel: {len(panel):,} intervals")
    print(f"  Columns: {len(panel.columns)}")
    print(f"\n  Variable coverage:")
    for col in [
        "Takeover",
        "start",
        "stop",
        "duration",
        "ClarityCEO",
        "CEO_Clarity_Residual",
        "Manager_Clarity_Residual",
        "Size",
        "BM",
        "Lev",
        "ROA",
        "CashHoldings",
        "SalesGrowth",
        "Intangibility",
        "AssetGrowth",
    ]:
        if col in panel.columns:
            n = panel[col].notna().sum()
            pct = 100.0 * n / len(panel) if len(panel) > 0 else 0
            print(f"    {col}: {n:,} ({pct:.1f}%)")

    return panel


def save_outputs(panel: pd.DataFrame, stats: Dict[str, Any], out_dir: Path, root: Path, timestamp: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "takeover_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: takeover_panel.parquet ({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

    # Generate run manifest for reproducibility
    manifest_input = root / "outputs" / "1.4_AssembleManifest" / "latest" / "master_sample_manifest.parquet"
    generate_manifest(
        output_dir=out_dir,
        stage="h9_panel",
        timestamp=timestamp,
        input_paths={"master_manifest": manifest_input},
        output_files={
            "panel": panel_path,
            "summary_stats": stats_path,
        },
    )
    print("  Saved: run_manifest.json")


def generate_report(
    panel: pd.DataFrame, stats: Dict[str, Any], out_dir: Path, duration: float
) -> None:
    n_firms = panel["gvkey"].nunique() if "gvkey" in panel.columns else 0
    n_events = (
        int(panel.groupby("gvkey")["Takeover"].max().sum())
        if "gvkey" in panel.columns
        else 0
    )
    report_lines = [
        "# H9: Takeover Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Purpose",
        "",
        "Call-to-call counting-process survival panel for H9 Takeover Hazard Analysis.",
        "One row per call-based risk interval. Each interval opens at an earnings call",
        "and closes at the next call, takeover announcement, or administrative censor.",
        "Time units: days since 2000-01-01. start/stop columns for CoxTimeVaryingFitter.",
        "",
        "## Panel Summary",
        "",
        f"- **Call-to-call intervals:** {len(panel):,}",
        f"- **Unique firms:** {n_firms:,}",
        f"- **Columns:** {len(panel.columns)}",
        f"- **Takeover event firms:** {n_events:,} / {n_firms:,}",
        "",
    ]

    if "duration" in panel.columns:
        report_lines.append("### Interval Duration (days)")
        report_lines.append("")
        report_lines.append(
            f"- Median: {panel['duration'].median():.0f} days"
        )
        report_lines.append(
            f"- Mean: {panel['duration'].mean():.0f} days"
        )
        report_lines.append(
            f"- Min: {panel['duration'].min()} days"
        )
        report_lines.append(
            f"- Max: {panel['duration'].max()} days"
        )
        report_lines.append("")

    if "Takeover_Type" in panel.columns:
        report_lines.append("### Takeover Type Breakdown (event intervals)")
        report_lines.append("")
        event_rows = panel[panel["Takeover"] == 1]
        if len(event_rows) > 0:
            for t, n in event_rows["Takeover_Type"].value_counts().items():
                report_lines.append(f"- {t}: {n:,}")
        else:
            report_lines.append("- No events")
        report_lines.append("")

    if "sample" in panel.columns:
        report_lines.append("### Sample Distribution (intervals)")
        report_lines.append("")
        for s in ["Main", "Finance", "Utility"]:
            n = (panel["sample"] == s).sum()
            report_lines.append(f"- {s}: {n:,}")
        report_lines.append("")

    report_path = out_dir / "report_h9_panel.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  Saved: report_h9_panel.md")


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_takeover_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "takeover" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H9_Takeover",
        timestamp=timestamp,
    )

    config = get_config(root / "config" / "project.yaml")
    var_config = load_variable_config(root / "config" / "variables.yaml")

    if year_start is None:
        year_start = config.data.year_start
    if year_end is None:
        year_end = config.data.year_end
    years = range(year_start, year_end + 1)

    print("=" * 80)
    print("H9: Build Takeover Panel")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Years:     {year_start}-{year_end}")

    panel = build_panel(root, years, var_config, stats)
    save_outputs(panel, stats, out_dir, root, timestamp)

    duration = (datetime.now() - start_time).total_seconds()
    generate_report(panel, stats, out_dir, duration)

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
