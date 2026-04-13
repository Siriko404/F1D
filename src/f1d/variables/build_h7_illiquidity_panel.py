#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H7 Illiquidity Panel
================================================================================
ID: variables/build_h7_illiquidity_panel
Description: Build CALL-LEVEL panel for H7 Speech Vagueness -> Stock Illiquidity.

    Step 1: Load manifest + all call-level uncertainty measures.
    Step 2: Load base financial controls (lnAssets, Leverage, ROA, TobinsQ, DailyVola, StockRet).
    Step 3: Load the Amihud (2002) Illiquidity measure (post-call window).
    Step 4: Load linguistic controls (NegCall, UncQue).
    Step 5: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 6: Assign industry sample (Main / Finance / Utility).
    Step 7: Save call-level panel.

Unit of observation: the individual earnings call (file_name).
DV: DeltaILLIQ (post-call minus pre-call Amihud illiquidity change).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from f1d.shared.config import load_variable_config, get_config
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest
from f1d.shared.variables.panel_utils import (
    assign_industry_sample,
    attach_fyearq,
    build_cal_yr_qtr_index,
    create_prior_quarter_lag,
    create_next_quarter_lead,
)
from f1d.shared.variables import (
    # 4 Key IVs (all simultaneous)
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    ManagerQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    # DV builder (produces DeltaILLIQ + PreCallILLIQ)
    AmihudChangeBuilder,
    # H7c/d/e BGT (2018) 25-day post-call Amihud (Level/Delta/Avg)
    BGTLongWindowAmihudBuilder,
    # Base controls
    SizeBuilder,
    TobinsQBuilder,
    ROABuilder,
    BookLevBuilder,
    CapexIntensityBuilder,
    DividendPayerBuilder,
    OCFVolatilityBuilder,
    # Extended controls
    VolatilityBuilder,
    StockPriceBuilder,
    TurnoverBuilder,
    AnalystQAUncertaintyBuilder,
    # Manifest
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H7 Illiquidity Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Building H7 Illiquidity Panel")
    print("=" * 60)

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        # 4 Key IVs (all simultaneous)
        "ceo_qa_uncertainty": CEOQAUncertaintyBuilder(
            var_config.get("ceo_qa_uncertainty", {})
        ),
        "ceo_pres_uncertainty": CEOPresUncertaintyBuilder(
            var_config.get("ceo_pres_uncertainty", {})
        ),
        "manager_qa_uncertainty": ManagerQAUncertaintyBuilder(
            var_config.get("manager_qa_uncertainty", {})
        ),
        "manager_pres_uncertainty": ManagerPresUncertaintyBuilder(
            var_config.get("manager_pres_uncertainty", {})
        ),
        # DV (produces DeltaILLIQ + PreCallILLIQ)
        "amihud_change": AmihudChangeBuilder(var_config.get("amihud_change", {})),
        # H7c/d/e BGT (2018) 25-day post-call Amihud — Level/Delta/Avg in one builder
        "bgt_long_window_amihud": BGTLongWindowAmihudBuilder(
            var_config.get("bgt_long_window_amihud", {})
        ),
        # Base controls
        "size": SizeBuilder(var_config.get("size", {})),
        "tobins_q": TobinsQBuilder(var_config.get("tobins_q", {})),
        "roa": ROABuilder(var_config.get("roa", {})),
        "lev": BookLevBuilder(var_config.get("lev", {})),
        "capex_intensity": CapexIntensityBuilder({}),
        "dividend_payer": DividendPayerBuilder({}),
        "ocf_volatility": OCFVolatilityBuilder({}),
        # Extended controls
        "volatility": VolatilityBuilder(var_config.get("volatility", {})),
        "stock_price": StockPriceBuilder(var_config.get("stock_price", {})),
        "turnover": TurnoverBuilder(var_config.get("turnover", {})),
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(var_config.get("analyst_qa_uncertainty", {})),
    }

    all_results = {}
    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    panel = all_results["manifest"].data.copy()

    for name, result in all_results.items():
        if name == "manifest":
            continue

        data = result.data.copy()
        conflicting = [
            c for c in data.columns if c in panel.columns and c != "file_name"
        ]
        if conflicting:
            data = data.drop(columns=conflicting)

        before_len = len(panel)
        panel = panel.merge(data, on="file_name", how="left")
        after_len = len(panel)
        delta = after_len - before_len
        if delta != 0:
            raise ValueError(f"Merge '{name}' changed rows {before_len} -> {after_len}")
        print(f"  After {name} merge: {after_len:,} rows (delta: {delta:+d})")

    panel["sample"] = assign_industry_sample(panel["ff12_code"])
    panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Attach fyearq for fiscal year FE (switching from call_quarter_int)
    panel = attach_fyearq(panel, root_path)
    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")

    # ============================================================================
    # Long-window liquidity extension (2026-04-17)
    # ============================================================================
    # Phase C of the H7c/d/e + lead extension plan. Adds:
    #   1. cal_yr / cal_qtr / cal_yr_qtr index columns (required by lag/lead)
    #   2. PostCallAmihud = PreCallILLIQ + DeltaILLIQ (promoted from H7b runner-time)
    #   3. {DV}_lag for 5 base columns (true t-1 prior-quarter lag)
    #   4. {DV}_lead1 for 5 base columns (next-quarter lead)
    # ============================================================================

    # Step 1: calendar year-quarter time index (required by lag/lead helpers)
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} "
          f"({100*n_yr_qtr/len(panel):.1f}%)")

    # Step 2: PostCallAmihud = PreCallILLIQ + DeltaILLIQ
    # Promoted from H7b runner-time computation to panel-time so the lag/lead
    # helpers can produce PostCallAmihud_lag and PostCallAmihud_lead1 columns.
    # NOTE: this is NOT the same as winsorizing PostCallILLIQ directly --
    # PreCallILLIQ and DeltaILLIQ are independently winsorized per-year inside
    # AmihudChangeBuilder, so the sum can in principle be negative. Empirically
    # n_neg = 0 on the 2026-04-02 H7 panel (the per-year winsorization keeps
    # the sum positive in the Amihud case, unlike the H14 spread case which
    # has ~1,006 negatives due to pooled winsorization).
    panel["PostCallAmihud"] = panel["PreCallILLIQ"] + panel["DeltaILLIQ"]
    n_neg_post = (panel["PostCallAmihud"] < 0).sum()
    if n_neg_post > 0:
        print(f"  WARNING: {n_neg_post} negative PostCallAmihud values "
              f"(winsorization artifact -- preserved for backward compat with H7b)")
    print(f"  PostCallAmihud: mean={panel['PostCallAmihud'].mean():.6f}, "
          f"non-null={panel['PostCallAmihud'].notna().sum():,}")

    # Step 3 + 4: lag and lead for all 5 liquidity DVs
    # (DeltaILLIQ, PostCallAmihud, plus 3 BGT 25-day Amihud variants)
    liquidity_dvs = [
        "DeltaILLIQ",
        "PostCallAmihud",
        "BGTLevel_Amihud",
        "BGTDelta_Amihud",
        "BGTAvg_Amihud",
    ]
    panel = create_prior_quarter_lag(panel, liquidity_dvs)
    panel = create_next_quarter_lead(panel, liquidity_dvs)

    # Coverage report for new columns
    print("  Lag/lead coverage:")
    for dv in liquidity_dvs:
        lag_col = f"{dv}_lag"
        lead_col = f"{dv}_lead1"
        if lag_col in panel.columns:
            print(f"    {lag_col:30s}: {panel[lag_col].notna().sum():>7,} "
                  f"({100*panel[lag_col].notna().sum()/len(panel):.1f}%)")
        if lead_col in panel.columns:
            print(f"    {lead_col:30s}: {panel[lead_col].notna().sum():>7,} "
                  f"({100*panel[lead_col].notna().sum()/len(panel):.1f}%)")

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    return panel


def save_outputs(panel: pd.DataFrame, stats: Dict[str, Any], out_dir: Path, root: Path, timestamp: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "h7_illiquidity_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: h7_illiquidity_panel.parquet ({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

    # Generate run manifest for reproducibility
    manifest_input = root / "outputs" / "1.4_AssembleManifest" / "latest" / "master_sample_manifest.parquet"
    generate_manifest(
        output_dir=out_dir,
        stage="stage3",
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
    report_lines = [
        "# Stage 3: H7 Illiquidity Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary",
        f"- **Rows:** {len(panel):,}",
        f"- **Columns:** {len(panel.columns)}",
        f"- **DeltaILLIQ (valid):** {panel['DeltaILLIQ'].notna().sum():,} calls",
        f"- **PreCallILLIQ (valid):** {panel['PreCallILLIQ'].notna().sum():,} calls",
        "",
    ]
    report_path = out_dir / "report_step3_h7.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h7_illiquidity_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h7_illiquidity" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H7_Illiquidity",
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
    print("STAGE 3: Build H7 Illiquidity Panel")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    panel = build_panel(root, years, var_config, stats)
    save_outputs(panel, stats, out_dir, root, timestamp)

    duration = (datetime.now() - start_time).total_seconds()
    generate_report(panel, stats, out_dir, duration)

    print(f"\nCOMPLETE in {duration:.1f}s")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        sys.exit(0)
    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
