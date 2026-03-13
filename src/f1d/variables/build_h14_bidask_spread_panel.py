#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H14 Bid-Ask Spread Change Panel
================================================================================
ID: variables/build_h14_bidask_spread_panel
Description: Build CALL-LEVEL panel for H14 Language Uncertainty -> Bid-Ask Spread Change.

    Step 1: Load manifest + all call-level uncertainty measures.
    Step 2: Load base financial controls (Size, Volatility).
    Step 3: Load CRSP-based controls (StockPrice, Turnover).
    Step 4: Load BidAskSpreadChangeBuilder for DV (delta_spread) and control (pre_call_spread).
    Step 5: Load EarningsSurpriseBuilder for AbsSurpDec control (|SurpDec|).
    Step 6: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 7: Create year_quarter variable for TimeEffects.
    Step 8: Assign industry sample (Main).
    Step 9: Save call-level panel.

Unit of observation: the individual earnings call (file_name).

Hypothesis H14:
    Higher earnings-call language uncertainty is associated with a larger
    increase in bid-ask spreads around the conference call (lower market liquidity).

    DV: delta_spread = Spread[+1,+3] - Spread[-3,-1]
    IV: Uncertainty measures (QA, Presentation)
    Controls: Size, StockPrice, Turnover, Volatility, pre_call_spread, AbsSurpDec
    Fixed Effects: Firm FE + year_quarter FE
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
from f1d.shared.variables.panel_utils import assign_industry_sample, attach_fyearq
from f1d.shared.variables import (
    ManagerQAUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    SizeBuilder,
    VolatilityBuilder,
    ManifestFieldsBuilder,
    BidAskSpreadChangeBuilder,
    StockPriceBuilder,
    TurnoverBuilder,
    EarningsSurpriseBuilder,
    CEOClarityResidualBuilder,
    ManagerClarityResidualBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H14 Bid-Ask Spread Change Panel",
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
    print("Building H14 Bid-Ask Spread Change Panel")
    print("=" * 60)

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        # Uncertainty IVs
        "manager_qa_uncertainty": ManagerQAUncertaintyBuilder(
            var_config.get("manager_qa_uncertainty", {})
        ),
        "ceo_qa_uncertainty": CEOQAUncertaintyBuilder(
            var_config.get("ceo_qa_uncertainty", {})
        ),
        "manager_pres_uncertainty": ManagerPresUncertaintyBuilder(
            var_config.get("manager_pres_uncertainty", {})
        ),
        "ceo_pres_uncertainty": CEOPresUncertaintyBuilder(
            var_config.get("ceo_pres_uncertainty", {})
        ),
        # Clarity Residuals (from CEO Clarity Extended Stage 4)
        "ceo_clarity_residual": CEOClarityResidualBuilder(
            var_config.get("ceo_clarity_residual", {})
        ),
        "manager_clarity_residual": ManagerClarityResidualBuilder(
            var_config.get("manager_clarity_residual", {})
        ),
        # Controls
        "size": SizeBuilder(var_config.get("size", {})),
        "volatility": VolatilityBuilder(var_config.get("volatility", {})),
        # H14-specific CRSP controls
        "stock_price": StockPriceBuilder(var_config.get("stock_price", {})),
        "turnover": TurnoverBuilder(var_config.get("turnover", {})),
        # DV and pre_call_spread control (default ±3 window)
        "bidask_spread": BidAskSpreadChangeBuilder(var_config.get("bidask_spread_change", {})),
        # Alternative event windows for robustness (L3)
        "bidask_spread_w1": BidAskSpreadChangeBuilder(
            {**var_config.get("bidask_spread_change", {}), "window_days": 1, "column_suffix": "_w1"}
        ),
        "bidask_spread_w5": BidAskSpreadChangeBuilder(
            {**var_config.get("bidask_spread_change", {}), "window_days": 5, "column_suffix": "_w5"}
        ),
        # Earnings surprise control (|SurpDec| replaces old AbsSurprise ratio)
        "earnings_surprise": EarningsSurpriseBuilder(
            var_config.get("earnings_surprise", {})
        ),
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

    # Assign industry sample
    panel["sample"] = assign_industry_sample(panel["ff12_code"])
    panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Create year_quarter variable for TimeEffects
    # Per H14.txt: "time fixed effects, typically quarter or year-quarter"
    panel["start_date_dt"] = pd.to_datetime(panel["start_date"], errors="coerce")
    panel["quarter"] = panel["start_date_dt"].dt.quarter
    panel["year_quarter"] = (
        panel["year"].astype(str) + "_Q" + panel["quarter"].astype(str)
    )

    # Also attach fyearq for potential alternative FE specifications
    panel = attach_fyearq(panel, root_path)

    # Rename variables to match H14 spec
    panel = panel.rename(columns={
        "pre_call_spread": "PreCallSpread",
        "pre_call_spread_closing": "PreCallSpreadClosing",
    })

    # AbsSurpDec = |SurpDec| (replaces old AbsSurprise ratio which had ~23% coverage)
    if "SurpDec" in panel.columns:
        panel["AbsSurpDec"] = panel["SurpDec"].abs()

    # L5: Verify H0.3 clarity residuals are actually populated (not all-NaN)
    for resid_col in ["Manager_Clarity_Residual", "CEO_Clarity_Residual"]:
        if resid_col in panel.columns and panel[resid_col].notna().sum() == 0:
            raise ValueError(
                f"H0.3 CEO Clarity Extended output required for H14 specs 5-6: "
                f"'{resid_col}' is entirely NaN. Run H0.3 first."
            )

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    print(f"\n  Final panel: {len(panel):,} rows, {len(panel.columns)} columns")
    print(f"  Valid delta_spread: {panel['delta_spread'].notna().sum():,}")
    print(f"  Valid PreCallSpread: {panel['PreCallSpread'].notna().sum():,}")
    for rob_col in ["delta_spread_closing", "delta_spread_w1", "delta_spread_w5", "pre_spread_change"]:
        if rob_col in panel.columns:
            print(f"  Valid {rob_col}: {panel[rob_col].notna().sum():,}")

    return panel


def save_outputs(panel: pd.DataFrame, stats: Dict[str, Any], out_dir: Path, root: Path, timestamp: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "h14_bidask_spread_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: h14_bidask_spread_panel.parquet ({len(panel):,} rows, {len(panel.columns)} columns)"
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
        "# Stage 3: H14 Bid-Ask Spread Change Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary",
        f"- **Rows:** {len(panel):,}",
        f"- **Columns:** {len(panel.columns)}",
        f"- **Valid delta_spread (DV):** {panel['delta_spread'].notna().sum():,} calls",
        f"- **Valid PreCallSpread:** {panel['PreCallSpread'].notna().sum():,} calls",
        "",
        "## Key Variables",
        "",
        "### Dependent Variable",
        "- `delta_spread`: Change in bid-ask spread around call (Spread[+1,+3] - Spread[-3,-1])",
        "",
        "### Independent Variables (Uncertainty)",
        "- `Manager_QA_Uncertainty_pct`: Manager Q&A language uncertainty",
        "- `CEO_QA_Uncertainty_pct`: CEO Q&A language uncertainty",
        "- `Manager_Pres_Uncertainty_pct`: Manager presentation language uncertainty",
        "- `CEO_Pres_Uncertainty_pct`: CEO presentation language uncertainty",
        "- `Manager_Clarity_Residual`: Manager Q&A uncertainty residual (after firm/linguistic controls)",
        "- `CEO_Clarity_Residual`: CEO Q&A uncertainty residual (after firm/linguistic controls)",
        "",
        "### Controls",
        "- `Size`: Firm size (ln(atq))",
        "- `StockPrice`: Stock price at call date",
        "- `Turnover`: Share turnover at call date (VOL/SHROUT)",
        "- `Volatility`: Return volatility over call window",
        "- `PreCallSpread`: Pre-call average bid-ask spread",
        "- `AbsSurpDec`: Absolute earnings surprise decile (|SurpDec|)",
        "",
        "### Fixed Effects",
        "- `gvkey`: Firm fixed effects",
        "- `year_quarter`: Year-Quarter fixed effects (e.g., '2010_Q1')",
        "",
    ]
    report_path = out_dir / "report_step3_h14.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h14_bidask_spread_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h14_bidask_spread" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H14_BidAskSpread",
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
    print("STAGE 3: Build H14 Bid-Ask Spread Change Panel")
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
