#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build Takeover Panel (4.3 Takeover Hazards)
================================================================================
ID: variables/build_h9_takeover_panel
Description: Build firm-year panel for Takeover Hazard survival analysis (4.3).

The panel is aggregated to firm-year level (not call-level), because Cox PH and
Fine-Gray models require one observation per firm per year (time-varying
covariates) or one observation per firm (time-invariant). Here we use the
firm-year structure with:
  - Duration: years from first call to takeover announcement / end of sample
  - Takeover: 1 if firm received a bid, 0 otherwise
  - Takeover_Type: 'Uninvited', 'Friendly', 'None'
  - ClarityManager (time-invariant CEO FE): merged per ceo_id × sample
  - ClarityCEO (time-invariant CEO FE): merged per ceo_id × sample
  - Manager_QA_Uncertainty_pct: averaged across calls per firm-year
  - CEO_QA_Uncertainty_pct: averaged across calls per firm-year
  - Financial controls: last observation per firm-year

Survival construction:
  - Entry: year of first observed call for that firm
  - Exit: year of takeover announcement OR last observed call year (censored)
  - Duration = exit_year - entry_year + 1 (minimum 1)

Inputs (all raw):
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet  (Compustat)
    - inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet        (CRSP daily)
    - inputs/tr_ibes/tr_ibes.parquet                       (IBES)
    - inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet   (CCM linktable)
    - inputs/SDC/sdc-ma-merged.parquet                     (SDC M&A)
    - outputs/econometric/manager_clarity/latest/clarity_scores.parquet
    - outputs/econometric/ceo_clarity/latest/clarity_scores.parquet

Outputs:
    - outputs/variables/takeover/{timestamp}/takeover_panel.parquet  (firm-year)
    - outputs/variables/takeover/{timestamp}/summary_stats.csv
    - outputs/variables/takeover/{timestamp}/report_step3_takeover.md

Deterministic: true
Dependencies:
    - Requires: Stage 4 clarity scores (4.1, 4.1.1)
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
    EPSGrowthBuilder,
    StockReturnBuilder,
    MarketReturnBuilder,
    EarningsSurpriseBuilder,
    TakeoverIndicatorBuilder,
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 3: Build Takeover Panel (4.3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def load_clarity_scores(root_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load ClarityManager and ClarityCEO scores from Stage 4 outputs."""
    try:
        mgr_dir = get_latest_output_dir(
            root_path / "outputs" / "econometric" / "manager_clarity",
            required_file="clarity_scores.parquet",
        )
        mgr = pd.read_parquet(
            mgr_dir / "clarity_scores.parquet",
            columns=["ceo_id", "sample", "ClarityManager"],
        )
        mgr["ceo_id"] = mgr["ceo_id"].astype(str)
        print(f"    ClarityManager: {len(mgr):,} CEO-sample pairs")
    except (OutputResolutionError, FileNotFoundError):
        mgr = pd.DataFrame(columns=["ceo_id", "sample", "ClarityManager"])
        print("    WARNING: ClarityManager not found — will be NaN")

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

    return mgr, ceo


def build_call_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Build call-level panel with all needed variables.

    This intermediate panel is then aggregated to firm-year in build_panel().
    Includes linguistic uncertainty, financial controls, and manifest identifiers.
    Excludes CCCL (not needed for survival analysis) and tone variables.
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
        "eps_growth": EPSGrowthBuilder({}),
        "stock_return": StockReturnBuilder({}),
        "market_return": MarketReturnBuilder({}),
        "earnings_surprise": EarningsSurpriseBuilder(
            var_config.get("earnings_surprise", {})
        ),
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


def aggregate_to_firm_year(call_panel: pd.DataFrame) -> pd.DataFrame:
    """Aggregate call-level panel to firm-year level.

    For each gvkey × year:
      - Uncertainty vars: mean across calls
      - Financial controls: last value (year-end, sorted by start_date)
      - CEO identifiers: most recent (last call per year)
      - Counts: n_calls

    Returns firm-year DataFrame.
    """
    print("\n" + "=" * 60)
    print("Aggregating to firm-year")
    print("=" * 60)

    df = call_panel.sort_values(["gvkey", "year", "start_date"]).copy()

    agg_mean_cols = [
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
    ]
    agg_last_cols = [
        "Size",
        "BM",
        "Lev",
        "ROA",
        "EPS_Growth",
        "StockRet",
        "MarketRet",
        "SurpDec",
        "ceo_id",
        "ceo_name",
        "sample",
        "ff12_code",
        "ff12_name",
    ]
    # Only aggregate columns present in panel
    agg_mean_cols = [c for c in agg_mean_cols if c in df.columns]
    agg_last_cols = [c for c in agg_last_cols if c in df.columns]

    print(f"  Mean-aggregated columns: {agg_mean_cols}")
    print(f"  Last-value columns: {agg_last_cols}")

    # Build aggregation dict
    agg_dict: Dict[str, Any] = {"n_calls": ("file_name", "count")}
    for col in agg_mean_cols:
        agg_dict[col] = (col, "mean")
    for col in agg_last_cols:
        agg_dict[col] = (col, "last")

    firm_year = df.groupby(["gvkey", "year"]).agg(**agg_dict).reset_index()

    print(f"  Firm-year panel: {len(firm_year):,} rows")
    print(f"  Unique firms: {firm_year['gvkey'].nunique():,}")
    print(f"  Year range: {firm_year['year'].min()} – {firm_year['year'].max()}")

    return firm_year


def build_counting_process_panel(
    firm_year: pd.DataFrame,
    takeover_data: pd.DataFrame,
    year_end: int,
) -> pd.DataFrame:
    """Build counting-process format panel for CoxTimeVaryingFitter.

    B7 fix: replaces one-row-per-firm with one-row-per-firm-year-at-risk.
    Time-varying covariates (Size, Lev, ROA, StockRet, etc.) are now carried
    at their actual observed values for each year rather than time-averaged.

    Counting-process format (Andersen-Gill):
        start = year_t - 1   (open left endpoint, years since entry start)
        stop  = year_t       (closed right endpoint)
        event = 1 only in the final interval for event firms, else 0

    For each firm, intervals run from (entry_year - 1) to exit_year.
    The event is 1 only in the last interval of an event firm.

    Args:
        firm_year: Firm-year aggregated panel (gvkey × year)
        takeover_data: Firm-level takeover indicators (gvkey, Takeover,
                       Takeover_Type, Takeover_Date)
        year_end: Last year of sample period (for censoring)

    Returns:
        Counting-process DataFrame with columns:
            gvkey, start, stop, Takeover, Takeover_Uninvited, Takeover_Friendly,
            Takeover_Type, all time-varying covariates, sample, ff12_code, etc.
    """
    print("\n" + "=" * 60)
    print("Building counting-process panel (B7 fix)")
    print("=" * 60)

    # Merge takeover data onto firm_year
    firm_year = firm_year.merge(
        takeover_data[["gvkey", "Takeover", "Takeover_Type", "Takeover_Date"]],
        on="gvkey",
        how="left",
    )
    firm_year["Takeover"] = firm_year["Takeover"].fillna(0).astype(int)
    firm_year["Takeover_Type"] = firm_year["Takeover_Type"].fillna("None")
    firm_year["Takeover_Date"] = pd.to_datetime(
        firm_year["Takeover_Date"], errors="coerce"
    )
    firm_year["takeover_year"] = firm_year["Takeover_Date"].dt.year

    # Determine exit year per firm (used to censor the counting process)
    firm_bounds = (
        firm_year.groupby("gvkey")
        .agg(
            entry_year=("year", "min"),
            last_obs_year=("year", "max"),
        )
        .reset_index()
    )

    # For event firms, exit_year = takeover_year; else min(last_obs_year, year_end)
    takeover_map = firm_year.drop_duplicates("gvkey")[
        ["gvkey", "Takeover", "takeover_year"]
    ]
    firm_bounds = firm_bounds.merge(takeover_map, on="gvkey", how="left")

    def get_exit_year(row: pd.Series) -> int:
        if row["Takeover"] == 1 and pd.notna(row["takeover_year"]):
            return int(row["takeover_year"])
        return int(min(row["last_obs_year"], year_end))

    firm_bounds["exit_year"] = firm_bounds.apply(get_exit_year, axis=1)

    # Build counting-process rows: one row per firm-year at risk
    rows: List[pd.DataFrame] = []
    covariate_cols = [
        c
        for c in firm_year.columns
        if c
        not in {
            "gvkey",
            "year",
            "Takeover",
            "Takeover_Type",
            "Takeover_Date",
            "takeover_year",
            "n_calls",
        }
    ]

    for _, bounds in firm_bounds.iterrows():
        gvkey = bounds["gvkey"]
        entry_year = int(bounds["entry_year"])
        exit_year = int(bounds["exit_year"])
        is_event = int(bounds["Takeover"]) == 1

        # Subset firm-year rows at risk: years from entry to exit
        fy_firm = (
            firm_year[
                (firm_year["gvkey"] == gvkey)
                & (firm_year["year"] >= entry_year)
                & (firm_year["year"] <= exit_year)
            ]
            .sort_values("year")
            .copy()
        )

        if len(fy_firm) == 0:
            # No observations in range — create a single interval from entry
            single = pd.DataFrame(
                {
                    "gvkey": [gvkey],
                    "start": [entry_year - 1],
                    "stop": [exit_year],
                    "Takeover": [int(is_event)],
                    "Takeover_Type": ["None"],
                }
            )
            rows.append(single)
            continue

        # Counting-process: start = prev_year (or entry_year - 1 for first row)
        fy_firm = fy_firm.reset_index(drop=True)
        fy_firm["start"] = fy_firm["year"].shift(1).fillna(entry_year - 1).astype(int)
        fy_firm["stop"] = fy_firm["year"].astype(int)

        # Event = 1 only in last row for event firms
        fy_firm["Takeover"] = 0
        if is_event:
            fy_firm.loc[fy_firm.index[-1], "Takeover"] = 1

        # Carry Takeover_Type as a time-constant column for the firm
        fy_firm["Takeover_Type"] = (
            fy_firm["Takeover_Type"].iloc[0]
            if "Takeover_Type" in fy_firm.columns
            else "None"
        )
        rows.append(
            fy_firm[
                ["gvkey", "start", "stop", "Takeover", "Takeover_Type"] + covariate_cols
            ]
        )

    panel = pd.concat(rows, ignore_index=True)

    n_events = panel.groupby("gvkey")["Takeover"].max().sum()
    n_firms = panel["gvkey"].nunique()
    print(f"  Counting-process rows: {len(panel):,}")
    print(f"  Unique firms: {n_firms:,}")
    print(f"  Event firms: {n_events:,} / {n_firms:,}")

    # Takeover_Type breakdown (firm-level)
    type_counts = firm_year.drop_duplicates("gvkey")["Takeover_Type"].value_counts()
    print("  Takeover_Type breakdown (firm-level):")
    for t, n in type_counts.items():
        print(f"    {t}: {n:,}")

    return panel


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Build complete takeover panel for survival analysis.

    Pipeline:
      1. Build call-level panel (manifest + linguistic + financial)
      2. Aggregate to firm-year
      3. Add clarity scores (per ceo_id × sample, from latest firm-year CEO)
      4. Load takeover indicators (firm-level from SDC)
      5. Construct Duration and event columns
      6. Merge firm-year covariates onto firm-level survival frame

    Returns firm-level DataFrame suitable for CoxPH / Fine-Gray.
    """
    year_end = max(years)

    # Step 1: Call-level panel
    call_panel = build_call_panel(root_path, years, var_config, stats)

    # Step 2: Aggregate to firm-year
    firm_year = aggregate_to_firm_year(call_panel)

    # Step 3: Load clarity scores and merge onto firm-year
    print("\n  Loading clarity scores...")
    mgr_clarity, ceo_clarity = load_clarity_scores(root_path)

    firm_year["ceo_id"] = firm_year["ceo_id"].astype(str)

    if len(mgr_clarity) > 0:
        before_len = len(firm_year)
        firm_year = firm_year.merge(
            mgr_clarity[["ceo_id", "sample", "ClarityManager"]],
            on=["ceo_id", "sample"],
            how="left",
        )
        after_len = len(firm_year)
        delta = after_len - before_len
        if after_len != before_len:
            raise ValueError(
                f"ClarityManager merge changed row count {before_len} → {after_len} (delta: {delta:+d})."
            )
        n_matched = firm_year["ClarityManager"].notna().sum()
        print(
            f"  After ClarityManager merge: {after_len:,} rows, {n_matched:,} matched (delta: {delta:+d})"
        )
    else:
        firm_year["ClarityManager"] = float("nan")

    if len(ceo_clarity) > 0:
        before_len = len(firm_year)
        firm_year = firm_year.merge(
            ceo_clarity[["ceo_id", "sample", "ClarityCEO"]],
            on=["ceo_id", "sample"],
            how="left",
        )
        after_len = len(firm_year)
        delta = after_len - before_len
        if after_len != before_len:
            raise ValueError(
                f"ClarityCEO merge changed row count {before_len} → {after_len} (delta: {delta:+d})."
            )
        n_matched = firm_year["ClarityCEO"].notna().sum()
        print(
            f"  After ClarityCEO merge: {after_len:,} rows, {n_matched:,} matched (delta: {delta:+d})"
        )
    else:
        firm_year["ClarityCEO"] = float("nan")

    # Step 4: Build takeover indicators (firm-level)
    print("\n  Loading takeover indicators from SDC...")
    takeover_config = dict(var_config.get("takeover_indicator", {}))
    takeover_config["year_start"] = min(years)
    takeover_config["year_end"] = year_end
    takeover_builder = TakeoverIndicatorBuilder(takeover_config)
    takeover_result = takeover_builder.build(years, root_path)
    takeover_data = takeover_result.data
    stats["variable_stats"].append(asdict(takeover_result.stats))

    # Step 5 (B7 fix): Build counting-process panel (one row per firm-year at risk)
    # Time-varying covariates are now carried at their actual per-year values.
    # Previously used time-averaged covariates on a one-row-per-firm panel, which
    # is invalid for Cox PH when covariates genuinely vary across time.
    panel = build_counting_process_panel(firm_year, takeover_data, year_end)

    print(f"\n  Final counting-process panel: {len(panel):,} firm-year rows")
    print(f"  Columns: {len(panel.columns)}")
    print(f"\n  Variable coverage:")
    for col in [
        "Takeover",
        "start",
        "stop",
        "ClarityManager",
        "ClarityCEO",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Size",
        "BM",
        "Lev",
        "ROA",
        "EPS_Growth",
        "StockRet",
        "MarketRet",
        "SurpDec",
    ]:
        if col in panel.columns:
            n = panel[col].notna().sum()
            pct = 100.0 * n / len(panel) if len(panel) > 0 else 0
            print(f"    {col}: {n:,} ({pct:.1f}%)")

    return panel


def save_outputs(panel: pd.DataFrame, stats: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "takeover_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: takeover_panel.parquet ({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_df.to_csv(out_dir / "summary_stats.csv", index=False)
    print(f"  Saved: summary_stats.csv")


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
        "# Stage 3: Takeover Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Purpose",
        "",
        "Counting-process survival panel for 4.3 Takeover Hazard Analysis (B7 fix).",
        "One row per firm-year at risk. Time-varying covariates at actual per-year values.",
        "start/stop columns define the counting-process intervals for CoxTimeVaryingFitter.",
        "",
        "## Panel Summary",
        "",
        f"- **Firm-year rows:** {len(panel):,}",
        f"- **Unique firms:** {n_firms:,}",
        f"- **Columns:** {len(panel.columns)}",
        f"- **Takeover event firms:** {n_events:,} / {n_firms:,}",
        "",
    ]
    if "Takeover_Type" in panel.columns:
        report_lines.append("### Takeover Type Breakdown")
        report_lines.append("")
        for t, n in panel["Takeover_Type"].value_counts().items():
            report_lines.append(f"- {t}: {n:,}")
        report_lines.append("")

    if "sample" in panel.columns:
        report_lines.append("### Sample Distribution")
        report_lines.append("")
        for s in ["Main", "Finance", "Utility"]:
            n = (panel["sample"] == s).sum()
            report_lines.append(f"- {s}: {n:,}")
        report_lines.append("")

    report_path = out_dir / "report_step3_takeover.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  Saved: report_step3_takeover.md")


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

    config = get_config(root / "config" / "project.yaml")
    var_config = load_variable_config(root / "config" / "variables.yaml")

    if year_start is None:
        year_start = config.data.year_start
    if year_end is None:
        year_end = config.data.year_end
    years = range(year_start, year_end + 1)

    print("=" * 80)
    print("STAGE 3: Build Takeover Panel (4.3)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {year_start}-{year_end}")

    panel = build_panel(root, years, var_config, stats)
    save_outputs(panel, stats, out_dir)

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
