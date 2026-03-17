#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H4 Leverage Discipline Panel
================================================================================
ID: variables/build_h4_leverage_panel
Description: Build CALL-LEVEL panel for H4 Leverage Discipline hypothesis test.

    Step 1: Load manifest + all call-level variables (linguistic + financial).
    Step 2: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 3: Add call year from start_date.
    Step 4: Compute temporal leverage variables per call:
            - Lev_lag: t-1 leverage (prior fiscal year)
            - Lev_t: current leverage (same fiscal year)
            - Lev_lead: t+1 leverage (next fiscal year)
            All require consecutive fiscal years within gvkey.
    Step 5: Assign industry sample (Main / Finance / Utility).
    Step 6: Save call-level panel.

Unit of observation: the individual earnings call (file_name).
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
    LevBuilder,
    ROABuilder,
    TobinsQBuilder,
    CashHoldingsBuilder,
    DividendPayerBuilder,
    CapexIntensityBuilder,
    OCFVolatilityBuilder,
    SalesGrowthBuilder,
    RDIntensityBuilder,
    CashFlowBuilder,
    VolatilityBuilder,
    ManifestFieldsBuilder,
    CEOClarityResidualBuilder,
    ManagerClarityResidualBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H4 Leverage Discipline Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def create_leverage_temporal_vars(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """
    Create Lev_lag (t-1), Lev_t (current), and Lev_lead (t+1) for H4.

    Coverage expectations:
    - Lev_t:    ~99.8% (same as Lev)
    - Lev_lag:  ~93.3% (requires prior consecutive year)
    - Lev_lead: ~85% (requires next consecutive year; 2018 calls lose it)
    """
    print("\n" + "=" * 60)
    print("Creating temporal leverage variables for H4 (call-level)")
    print("=" * 60)

    panel = attach_fyearq(panel, root_path)

    df = panel.copy()
    df["start_date_dt"] = pd.to_datetime(df["start_date"], errors="coerce")

    valid_mask = (
        df["fyearq"].notna() & df["gvkey"].notna() & df["start_date_dt"].notna()
    )
    df_valid = df[valid_mask].copy()

    if len(df_valid) == 0:
        print("  WARNING: No valid rows for temporal variable creation.")
        df["Lev_lag"] = np.nan
        df["Lev_t"] = np.nan
        df["Lev_lead"] = np.nan
        return df

    df_valid["fyearq_int"] = df_valid["fyearq"].astype(int)

    # 1. Take the last call's Leverage per fiscal year (proxy for annual value)
    firm_year = df_valid.sort_values(
        ["gvkey", "fyearq_int", "start_date_dt"]
    ).drop_duplicates(subset=["gvkey", "fyearq_int"], keep="last")[
        ["gvkey", "fyearq_int", "Lev"]
    ]

    # 2. Sort by firm and fiscal year
    firm_year = firm_year.sort_values(["gvkey", "fyearq_int"]).reset_index(drop=True)

    # 3. Create previous and next fiscal year columns for validation
    firm_year["prev_fyearq"] = firm_year.groupby("gvkey")["fyearq_int"].shift(1)
    firm_year["next_fyearq"] = firm_year.groupby("gvkey")["fyearq_int"].shift(-1)

    # 4. Lev_lag: previous year's leverage (shift(1) on ascending years = t-1)
    firm_year["Lev_lag"] = firm_year.groupby("gvkey")["Lev"].shift(1)
    is_consecutive_prev = (firm_year["fyearq_int"] - firm_year["prev_fyearq"]) == 1
    firm_year.loc[~is_consecutive_prev, "Lev_lag"] = np.nan

    # 5. Lev_t: current year's leverage (direct copy)
    firm_year["Lev_t"] = firm_year["Lev"]

    # 6. Lev_lead: next year's leverage (shift(-1) on ascending years = t+1)
    firm_year["Lev_lead"] = firm_year.groupby("gvkey")["Lev"].shift(-1)
    is_consecutive_next = (firm_year["next_fyearq"] - firm_year["fyearq_int"]) == 1
    firm_year.loc[~is_consecutive_next, "Lev_lead"] = np.nan

    # 7. Create lookup table for merging
    lookup = firm_year[["gvkey", "fyearq_int", "Lev_lag", "Lev_t", "Lev_lead"]].copy()

    # 8. Merge temporal vars back onto all calls via (gvkey, fyearq_int)
    df["_row_id"] = np.arange(len(df))
    df["fyearq_int"] = np.floor(pd.to_numeric(df["fyearq"], errors="coerce")).astype(
        "Int64"
    )

    merged = df.merge(lookup, on=["gvkey", "fyearq_int"], how="left")
    merged = merged.sort_values("_row_id").drop(
        columns=["_row_id", "start_date_dt"]
    )

    # 9. Log coverage for all three variables
    print("\n  Temporal Leverage Variables Coverage:")
    for col in ["Lev_t", "Lev_lag", "Lev_lead"]:
        n_valid = merged[col].notna().sum()
        pct = 100 * n_valid / len(merged)
        print(f"    {col:12s}: {n_valid:,} / {len(merged):,} ({pct:.1f}%)")

    return merged


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Building H4 Panel")
    print("=" * 60)

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
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
        "size": SizeBuilder(var_config.get("size", {})),
        "lev": LevBuilder(var_config.get("lev", {})),
        "roa": ROABuilder(var_config.get("roa", {})),
        "tobins_q": TobinsQBuilder(var_config.get("tobins_q", {})),
        "cash_holdings": CashHoldingsBuilder(var_config.get("cash_holdings", {})),
        "dividend_payer": DividendPayerBuilder(var_config.get("dividend_payer", {})),
        "capex_intensity": CapexIntensityBuilder(
            var_config.get("capex_intensity", {})
        ),
        "ocf_volatility": OCFVolatilityBuilder(
            var_config.get("ocf_volatility", {})
        ),
        "sales_growth": SalesGrowthBuilder(var_config.get("sales_growth", {})),
        "rd_intensity": RDIntensityBuilder(var_config.get("rd_intensity", {})),
        "cash_flow": CashFlowBuilder(var_config.get("cash_flow", {})),
        "volatility": VolatilityBuilder(var_config.get("volatility", {})),
        "ceo_clarity_residual": CEOClarityResidualBuilder(
            var_config.get("ceo_clarity_residual", {})
        ),
        "manager_clarity_residual": ManagerClarityResidualBuilder(
            var_config.get("manager_clarity_residual", {})
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

    panel["sample"] = assign_industry_sample(panel["ff12_code"])
    panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    panel = create_leverage_temporal_vars(panel, root_path)

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    return panel


def save_outputs(panel: pd.DataFrame, stats: Dict[str, Any], out_dir: Path, root: Path, timestamp: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "h4_leverage_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: h4_leverage_panel.parquet ({len(panel):,} rows, {len(panel.columns)} columns)"
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
        "# Stage 3: H4 Leverage Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary",
        f"- **Rows:** {len(panel):,}",
        f"- **Columns:** {len(panel.columns)}",
        "",
        "## Dependent Variables (Leverage)",
        f"- **Lev (t):** {panel['Lev'].notna().sum():,} calls",
        f"- **Lev_lead (t+1):** {panel['Lev_lead'].notna().sum():,} calls",
        "",
        "## Key IVs (6 simultaneous)",
        f"- **CEO_QA_Uncertainty_pct:** {panel['CEO_QA_Uncertainty_pct'].notna().sum():,} calls",
        f"- **CEO_Pres_Uncertainty_pct:** {panel['CEO_Pres_Uncertainty_pct'].notna().sum():,} calls",
        f"- **Manager_QA_Uncertainty_pct:** {panel['Manager_QA_Uncertainty_pct'].notna().sum():,} calls",
        f"- **Manager_Pres_Uncertainty_pct:** {panel['Manager_Pres_Uncertainty_pct'].notna().sum():,} calls",
        f"- **CEO_Clarity_Residual:** {panel['CEO_Clarity_Residual'].notna().sum():,} calls",
        f"- **Manager_Clarity_Residual:** {panel['Manager_Clarity_Residual'].notna().sum():,} calls",
        "",
        "## Extended Controls",
        f"- **CapexAt:** {panel['CapexAt'].notna().sum():,} calls",
        f"- **OCF_Volatility:** {panel['OCF_Volatility'].notna().sum():,} calls",
        f"- **SalesGrowth:** {panel['SalesGrowth'].notna().sum():,} calls",
        f"- **RD_Intensity:** {panel['RD_Intensity'].notna().sum():,} calls",
        f"- **CashFlow:** {panel['CashFlow'].notna().sum():,} calls",
        f"- **Volatility:** {panel['Volatility'].notna().sum():,} calls",
        "",
    ]
    report_path = out_dir / "report_step3_h4.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h4_leverage_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h4_leverage" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H4_Leverage",
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
    print("STAGE 3: Build H4 Leverage Discipline Panel")
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
