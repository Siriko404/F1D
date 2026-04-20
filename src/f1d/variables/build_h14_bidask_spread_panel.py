#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H14 Bid-Ask Spread Change Panel
================================================================================
ID: variables/build_h14_bidask_spread_panel
Description: Build CALL-LEVEL panel for H14 Language Uncertainty -> Bid-Ask Spread Change.

    Step 1: Load manifest + all call-level uncertainty measures.
    Step 2: Load thesis-consistent Compustat controls (lnAssets, TobinsQ, ROA, Leverage,
            Capex, DivDummy, sCFO).
    Step 3: Load CRSP-based controls (StockPrice, Turnover, Volatility).
    Step 4: Load BidAskSpreadChangeBuilder for DV and PreCallSpread control.
    Step 5: Load EarningsSurpriseBuilder for AbsSurpDec control (|SurpDec|).
    Step 6: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 7: Rename closing-quote columns to primary (DSPREAD, PreCallSpread).
    Step 8: Attach fiscal year-quarter (fyearq_int) for time FE.
    Step 9: Winsorize CRSP-derived variables at 1%/99%.
    Step 10: Assign industry sample (Main / Finance / Utility).
    Step 11: Save call-level panel.

Unit of observation: the individual earnings call (file_name).

Hypothesis H14:
    Higher earnings-call language uncertainty is associated with a larger
    increase in bid-ask spreads around the conference call (lower market liquidity).

    DV: DSPREAD = mean(RelSpread[+1,+3]) - mean(RelSpread[-3,-1])
        where RelSpread_d = 2*(ASK_d - BID_d)/(ASK_d + BID_d)  [closing quotes]
        Following Lee (2016, The Accounting Review).
    IV: 4 simultaneous uncertainty measures (horse-race)
    Controls (Base): lnAssets, TobinsQ, ROA, Leverage, Capex, DivDummy, sCFO, PreCallSpread
    Controls (Extended): Base + StockPrice, Turnover, DailyVola, AbsSurpDec
    Fixed Effects: Industry(FF12)/Firm FE + FiscalYear FE (fyearq_int)
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
from f1d.shared.variables.winsorization import winsorize_pooled
from f1d.shared.variables import (
    # Key IVs (4 simultaneous)
    ManagerQAUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    NonCEOManagerQAUncertaintyBuilder,
    NonCEOManagerPresUncertaintyBuilder,
    # Thesis-consistent Compustat controls
    SizeBuilder,
    TobinsQBuilder,
    ROABuilder,
    BookLevBuilder,
    CapexIntensityBuilder,
    DividendPayerBuilder,
    OCFVolatilityBuilder,
    # H14-specific CRSP controls
    VolatilityBuilder,
    StockPriceBuilder,
    TurnoverBuilder,
    # DV builder
    BidAskSpreadChangeBuilder,
    # H14c/d/e BGT (2018) 25-day window + Lee (2016) closing-quote spread
    BGTLongWindowSpreadBuilder,
    # IBES control
    EarningsSurpriseBuilder,
    # Infrastructure
    ManifestFieldsBuilder,
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
        # Key IVs (4 simultaneous)
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
        "nonceo_manager_qa_uncertainty": NonCEOManagerQAUncertaintyBuilder(
            var_config.get("nonceo_manager_qa_uncertainty", {})
        ),
        "nonceo_manager_pres_uncertainty": NonCEOManagerPresUncertaintyBuilder(
            var_config.get("nonceo_manager_pres_uncertainty", {})
        ),
        # Thesis-consistent Compustat controls
        "size": SizeBuilder(var_config.get("size", {})),
        "tobins_q": TobinsQBuilder(var_config.get("tobins_q", {})),
        "roa": ROABuilder(var_config.get("roa", {})),
        "lev": BookLevBuilder(var_config.get("lev", {})),
        "capex_intensity": CapexIntensityBuilder(
            var_config.get("capex_intensity", {})
        ),
        "dividend_payer": DividendPayerBuilder(var_config.get("dividend_payer", {})),
        "ocf_volatility": OCFVolatilityBuilder(
            var_config.get("ocf_volatility", {})
        ),
        # H14-specific CRSP controls
        "volatility": VolatilityBuilder(var_config.get("volatility", {})),
        "stock_price": StockPriceBuilder(var_config.get("stock_price", {})),
        "turnover": TurnoverBuilder(var_config.get("turnover", {})),
        # DV and pre_call_spread control (±3 trading day window)
        "bidask_spread": BidAskSpreadChangeBuilder(
            var_config.get("bidask_spread_change", {})
        ),
        # H14c/d/e BGT (2018) 25-day window + Lee (2016) closing-quote spread
        # (Level/Delta/Avg in one builder pass)
        "bgt_long_window_spread": BGTLongWindowSpreadBuilder(
            var_config.get("bgt_long_window_spread", {})
        ),
        # Earnings surprise control
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

    # Verify ff12_code is present
    if "ff12_code" not in panel.columns:
        raise ValueError(
            "build_panel: 'ff12_code' not in panel. ManifestFieldsBuilder must include ff12_code."
        )

    # Rename closing-quote columns to primary DV and control
    # Lee (2016): DSPREAD uses closing BID/ASK, not intraday ASKHI/BIDLO
    panel = panel.rename(columns={
        "delta_spread_closing": "DSPREAD",
        "pre_call_spread_closing": "PreCallSpread",
    })

    # AbsSurpDec = |SurpDec| (earnings surprise magnitude)
    if "SurpDec" in panel.columns:
        panel["AbsSurpDec"] = panel["SurpDec"].abs()

    # Assign industry sample
    panel["sample"] = assign_industry_sample(panel["ff12_code"])
    panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Attach fiscal year and create fyearq_int (CRITICAL for runner time index)
    panel = attach_fyearq(panel, root_path)
    panel["fyearq_int"] = np.floor(
        pd.to_numeric(panel["fyearq"], errors="coerce")
    ).astype("Int64")

    # Winsorize CRSP-derived variables at 1%/99% (pooled)
    # Compustat variables are already winsorized by their engines
    # Volatility is already winsorized per-year by CRSPEngine
    # The 3 new BGT spread columns are added here so they get the same pooled
    # winsorization as DSPREAD/PreCallSpread (matches existing H14 convention).
    winsorize_cols = [
        "DSPREAD", "PreCallSpread", "StockPrice", "Turnover", "AbsSurpDec",
        "BGTLevel_Spread", "BGTDelta_Spread", "BGTAvg_Spread",
    ]
    panel = winsorize_pooled(panel, winsorize_cols)
    print(f"  Winsorized {len(winsorize_cols)} columns at 1%/99% pooled")

    # ============================================================================
    # Long-window liquidity extension (2026-04-17)
    # ============================================================================
    # Phase C of the H14c/d/e + lead extension plan. Adds:
    #   1. cal_yr / cal_qtr / cal_yr_qtr index columns (required by lag/lead)
    #   2. PostCallSpread = PreCallSpread + DSPREAD (promoted from H14b runner-time)
    #   3. {DV}_lag for 5 base columns (true t-1 prior-quarter lag)
    #   4. {DV}_lead1 for 5 base columns (next-quarter lead)
    # ============================================================================

    # Step 1: calendar year-quarter time index (required by lag/lead helpers)
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} "
          f"({100*n_yr_qtr/len(panel):.1f}%)")

    # Step 2: PostCallSpread = PreCallSpread + DSPREAD
    # Promoted from H14b runner-time computation. Empirically n_neg ~= 1,006
    # negative values exist due to pooled winsorization of PreCallSpread/DSPREAD
    # independently. This artifact is preserved for backward compatibility with
    # existing H14b col 1-6 production results (the H14b runner has been emitting
    # this warning for months and the published coefficients already incorporate
    # the artifact). Re-winsorizing PostCallSpread here would silently change
    # H14b results -- DO NOT do that. Just propagate the warning to panel-build
    # time so users are aware.
    panel["PostCallSpread"] = panel["PreCallSpread"] + panel["DSPREAD"]
    n_neg_post = (panel["PostCallSpread"] < 0).sum()
    if n_neg_post > 0:
        print(f"  WARNING: {n_neg_post} negative PostCallSpread values "
              f"(winsorization artifact -- preserved for backward compat with H14b)")
    print(f"  PostCallSpread: mean={panel['PostCallSpread'].mean():.6f}, "
          f"non-null={panel['PostCallSpread'].notna().sum():,}")

    # Step 3 + 4: lag and lead for all 5 spread DVs
    # (DSPREAD, PostCallSpread, plus 3 BGT 25-day Spread variants)
    # NOTE: legacy high-low columns (pre_call_spread, delta_spread,
    # pre_spread_change) are intentionally NOT lagged/leaded -- only the
    # closing-quote columns (which are the H14 production DV family) are
    # in scope.
    spread_dvs = [
        "DSPREAD",
        "PostCallSpread",
        "BGTLevel_Spread",
        "BGTDelta_Spread",
        "BGTAvg_Spread",
    ]
    panel = create_prior_quarter_lag(panel, spread_dvs)
    panel = create_next_quarter_lead(panel, spread_dvs)

    # Coverage report for new columns
    print("  Lag/lead coverage:")
    for dv in spread_dvs:
        lag_col = f"{dv}_lag"
        lead_col = f"{dv}_lead1"
        if lag_col in panel.columns:
            print(f"    {lag_col:30s}: {panel[lag_col].notna().sum():>7,} "
                  f"({100*panel[lag_col].notna().sum()/len(panel):.1f}%)")
        if lead_col in panel.columns:
            print(f"    {lead_col:30s}: {panel[lead_col].notna().sum():>7,} "
                  f"({100*panel[lead_col].notna().sum()/len(panel):.1f}%)")


    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    # Coverage report
    print(f"\n  Final panel: {len(panel):,} rows, {len(panel.columns)} columns")
    print(f"  Valid DSPREAD (DV): {panel['DSPREAD'].notna().sum():,}")
    print(f"  Valid PreCallSpread: {panel['PreCallSpread'].notna().sum():,}")
    print(f"  Valid fyearq_int: {panel['fyearq_int'].notna().sum():,}")
    for ctrl in ["TobinsQ", "ROA", "Leverage", "Capex", "DivDummy", "sCFO"]:
        if ctrl in panel.columns:
            print(f"  Valid {ctrl}: {panel[ctrl].notna().sum():,}")

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
        "",
        "## Dependent Variable (Lee 2016)",
        f"- **DSPREAD:** {panel['DSPREAD'].notna().sum():,} calls",
        "  - RelSpread_d = 2*(ASK-BID)/(ASK+BID) [closing quotes]",
        "  - DSPREAD = mean(RelSpread[+1,+3]) - mean(RelSpread[-3,-1])",
        "",
        "## Key IVs (4 simultaneous)",
        f"- **UncAnsCEO:** {panel['UncAnsCEO'].notna().sum():,} calls",
        f"- **UncPreCEO:** {panel['UncPreCEO'].notna().sum():,} calls",
        f"- **UncAnsMgr:** {panel['UncAnsMgr'].notna().sum():,} calls",
        f"- **UncPreMgr:** {panel['UncPreMgr'].notna().sum():,} calls",
        "",
        "## Base Controls (Thesis-Consistent)",
        f"- **lnAssets:** {panel['lnAssets'].notna().sum():,} calls",
        f"- **TobinsQ:** {panel['TobinsQ'].notna().sum():,} calls",
        f"- **ROA:** {panel['ROA'].notna().sum():,} calls",
        f"- **Leverage:** {panel['Leverage'].notna().sum():,} calls",
        f"- **Capex:** {panel['Capex'].notna().sum():,} calls",
        f"- **DivDummy:** {panel['DivDummy'].notna().sum():,} calls",
        f"- **sCFO:** {panel['sCFO'].notna().sum():,} calls",
        f"- **PreCallSpread:** {panel['PreCallSpread'].notna().sum():,} calls",
        "",
        "## Extended Controls (Microstructure Literature)",
        f"- **StockPrice:** {panel['StockPrice'].notna().sum():,} calls",
        f"- **Turnover:** {panel['Turnover'].notna().sum():,} calls",
        f"- **Volatility:** {panel['DailyVola'].notna().sum():,} calls",
        f"- **AbsSurpDec:** {panel['AbsSurpDec'].notna().sum():,} calls",
        "",
        "## Fixed Effects",
        "- `gvkey`: Firm fixed effects",
        f"- `fyearq_int`: Fiscal year FE ({panel['fyearq_int'].notna().sum():,} valid)",
        "- `ff12_code`: Industry FE (Fama-French 12)",
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
