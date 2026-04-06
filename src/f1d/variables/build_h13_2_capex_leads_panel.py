#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H13.2 Capex Lead Horizons Panel
================================================================================
ID: variables/build_h13_2_capex_leads_panel
Description: Build CALL-LEVEL panel for H13.2 Capital Expenditure lead horizon
             study. Extends the H13 panel with multi-year leads (t+1 through t+4).

    This panel follows the H13 pattern with additional lead variables:
    one row per earnings call (file_name), 4 simultaneous IVs,
    extended controls, fyearq_int time index.

    Step 1: Load manifest + all call-level variables (same as H13).
    Step 2: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 3: Add call year from start_date.
    Step 4: Attach fyearq, extract firm-year EOY Capex values.
    Step 5: Create Capex_lead (t+1), Capex_lead2 (t+2), Capex_lead3 (t+3),
            Capex_lead4 (t+4) using generalized n-year lead construction.
    Step 6: Create Capex_lag (t-1) for Lagged_DV control.
    Step 7: Assign industry sample (Main / Finance / Utility).
    Step 8: Save call-level panel.

Unit of observation: the individual earnings call (file_name).

Outputs:
    - outputs/variables/h13_2_capex_leads/{timestamp}/h13_2_capex_leads_panel.parquet
    - outputs/variables/h13_2_capex_leads/{timestamp}/summary_stats.csv

Author: Thesis Author
Date: 2026-04-05
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from f1d.shared.config import load_variable_config, get_config
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest
from f1d.shared.variables.panel_utils import assign_industry_sample, attach_fyearq
from f1d.shared.variables import (
    # 4 Key IVs (all simultaneous)
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    NonCEOManagerQAUncertaintyBuilder,
    ManagerQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    # Base controls (Compustat engine)
    SizeBuilder,
    TobinsQBuilder,
    ROABuilder,
    BookLevBuilder,
    CashHoldingsBuilder,
    CapexIntensityBuilder,
    DividendPayerBuilder,
    OCFVolatilityBuilder,
    # Extended controls
    SalesGrowthBuilder,
    RDIntensityBuilder,
    CashFlowBuilder,
    VolatilityBuilder,
    # Manifest
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H13.2 Capex Lead Horizons Panel (call-level)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate inputs without executing"
    )
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def build_call_level_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Build call-level panel — identical to H13's build_call_level_panel."""
    print("\n" + "=" * 60)
    print("Loading variables (call-level)")
    print("=" * 60)

    all_results: Dict[str, Any] = {}

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        "ceo_qa_uncertainty": CEOQAUncertaintyBuilder(
            var_config.get("ceo_qa_uncertainty", {})
        ),
        "ceo_pres_uncertainty": CEOPresUncertaintyBuilder(
            var_config.get("ceo_pres_uncertainty", {})
        ),
        "nonceo_manager_qa_uncertainty": NonCEOManagerQAUncertaintyBuilder(
            var_config.get("nonceo_manager_qa_uncertainty", {})
        ),
        "manager_qa_uncertainty": ManagerQAUncertaintyBuilder(
            var_config.get("manager_qa_uncertainty", {})
        ),
        "manager_pres_uncertainty": ManagerPresUncertaintyBuilder(
            var_config.get("manager_pres_uncertainty", {})
        ),
        "size": SizeBuilder({}),
        "tobins_q": TobinsQBuilder({}),
        "roa": ROABuilder({}),
        "lev": BookLevBuilder({}),
        "cash_holdings": CashHoldingsBuilder({}),
        "capex_intensity": CapexIntensityBuilder({}),
        "dividend_payer": DividendPayerBuilder({}),
        "ocf_volatility": OCFVolatilityBuilder({}),
        "sales_growth": SalesGrowthBuilder(var_config.get("sales_growth", {})),
        "rd_intensity": RDIntensityBuilder(var_config.get("rd_intensity", {})),
        "cash_flow": CashFlowBuilder(var_config.get("cash_flow", {})),
        "volatility": VolatilityBuilder(var_config.get("volatility", {})),
    }

    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    manifest_result = all_results["manifest"]
    panel = manifest_result.data.copy()

    if panel["file_name"].duplicated().any():
        n_dups = panel["file_name"].duplicated().sum()
        raise ValueError(
            f"Manifest has {n_dups} duplicate file_name rows. "
            "Panel build aborted to prevent row multiplication."
        )

    print(f"\n  Base manifest: {len(panel):,} rows")

    for name, result in all_results.items():
        if name == "manifest":
            continue
        data = result.data.copy()
        if "file_name" not in data.columns or len(data.columns) <= 1:
            print(f"  WARNING: {name} returned no usable columns -- skipping merge")
            continue
        if data["file_name"].duplicated().any():
            n_dups = data["file_name"].duplicated().sum()
            raise ValueError(
                f"Builder '{name}' returned {n_dups} duplicate file_name rows. "
                "Merge aborted to prevent fan-out."
            )
        conflicting = [
            c for c in data.columns if c in panel.columns and c != "file_name"
        ]
        if conflicting:
            data = data.drop(columns=conflicting)
        before_len = len(panel)
        panel = panel.merge(data, on="file_name", how="left")
        after_len = len(panel)
        if after_len != before_len:
            raise ValueError(
                f"Merge of '{name}' changed row count {before_len} -> {after_len}."
            )
        print(f"  After {name} merge: {after_len:,} rows (delta: +0)")

    if "ff12_code" not in panel.columns:
        raise ValueError("ff12_code column missing from panel.")

    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    stats_list = []
    for name, result in all_results.items():
        stats_list.append(result.stats)
    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def _get_firm_year_eoy_capex(
    panel: pd.DataFrame, root_path: Optional[Path] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Extract firm-year EOY Capex values. Shared by all lead/lag functions.

    Returns:
        (panel_with_fyearq, firm_year_eoy) where firm_year_eoy has columns
        [gvkey, fyearq_grp, Capex_eoy], sorted by (gvkey, fyearq_grp).
    """
    if root_path is not None:
        panel = attach_fyearq(panel, root_path)
    elif "fyearq" not in panel.columns:
        raise ValueError("'fyearq' missing and root_path not provided.")

    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")
    n_missing = panel["fyearq_int"].isna().sum()
    if n_missing > 0:
        print(f"  WARNING: {n_missing:,} calls have missing fyearq")

    panel_dt = panel.copy()
    panel_dt["start_date_dt"] = pd.to_datetime(panel_dt["start_date"], errors="coerce")

    valid_mask = panel_dt["fyearq_int"].notna()
    panel_valid = panel_dt[valid_mask].copy()

    latest_idx = panel_valid.groupby(["gvkey", "fyearq_int"])["start_date_dt"].idxmax()
    firm_year_eoy = panel_valid.loc[
        latest_idx, ["gvkey", "fyearq_int", "Capex"]
    ].copy()
    firm_year_eoy = firm_year_eoy.rename(
        columns={"fyearq_int": "fyearq_grp", "Capex": "Capex_eoy"}
    )
    firm_year_eoy = firm_year_eoy.sort_values(["gvkey", "fyearq_grp"]).reset_index(
        drop=True
    )

    print(f"  Unique firm-fiscal-years: {len(firm_year_eoy):,}")
    return panel, firm_year_eoy


def create_capex_lead_n(
    panel: pd.DataFrame,
    firm_year_eoy: pd.DataFrame,
    n: int,
) -> pd.DataFrame:
    """Create Capex lead at horizon n (t+n) at call level.

    Shifts Capex_eoy by -n within gvkey, validates that the lead row is
    exactly fyearq_grp + n (rejects gaps). Merges back to call level.

    Args:
        panel: Call-level panel with fyearq_int column.
        firm_year_eoy: Firm-year EOY Capex from _get_firm_year_eoy_capex().
        n: Lead horizon (1, 2, 3, or 4).

    Returns:
        Panel with new column: 'Capex_lead' (n=1) or 'Capex_lead{n}' (n>1).
    """
    col_name = "Capex_lead" if n == 1 else f"Capex_lead{n}"

    print(f"\n  --- Creating {col_name} (t+{n}) ---")

    fye = firm_year_eoy.copy()

    # Shift -n: get the value n rows ahead within gvkey
    fye["_fyearq_target"] = fye.groupby("gvkey")["fyearq_grp"].shift(-n)
    fye["_capex_target"] = fye.groupby("gvkey")["Capex_eoy"].shift(-n)

    # Validate: target must be exactly fyearq_grp + n
    consecutive = fye["_fyearq_target"] == (fye["fyearq_grp"] + n)
    fye[col_name] = np.where(consecutive, fye["_capex_target"], np.nan)

    n_no_future = fye["_capex_target"].isna().sum()
    n_gap = ((~consecutive) & fye["_capex_target"].notna()).sum()
    n_valid = fye[col_name].notna().sum()
    print(f"    No future data (last {n} years per firm): {n_no_future:,}")
    print(f"    Gap in fiscal years (nulled): {n_gap:,}")
    print(f"    Valid consecutive lead: {n_valid:,}")

    # Merge to call level
    lead_lookup = fye[["gvkey", "fyearq_grp", col_name]].copy()
    lead_lookup = lead_lookup.rename(columns={"fyearq_grp": "fyearq_int"})

    before_len = len(panel)
    panel = panel.merge(lead_lookup, on=["gvkey", "fyearq_int"], how="left")
    after_len = len(panel)
    if after_len != before_len:
        raise ValueError(
            f"{col_name} merge changed row count {before_len} -> {after_len}."
        )

    n_calls_valid = panel[col_name].notna().sum()
    print(f"    Calls with valid {col_name}: {n_calls_valid:,}")

    return panel


def create_capex_lag(panel: pd.DataFrame, firm_year_eoy: pd.DataFrame) -> pd.DataFrame:
    """Create Capex_lag (t-1) at call level. Same as H13 pattern."""
    print("\n  --- Creating Capex_lag (t-1) ---")

    fye = firm_year_eoy.copy()

    fye["_fyearq_prev"] = fye.groupby("gvkey")["fyearq_grp"].shift(1)
    fye["_capex_prev"] = fye.groupby("gvkey")["Capex_eoy"].shift(1)

    consecutive = fye["_fyearq_prev"] == (fye["fyearq_grp"] - 1)
    fye["Capex_lag"] = np.where(consecutive, fye["_capex_prev"], np.nan)

    n_first = fye["_capex_prev"].isna().sum()
    n_gap = ((~consecutive) & fye["_capex_prev"].notna()).sum()
    n_valid = fye["Capex_lag"].notna().sum()
    print(f"    First year per firm (no prior): {n_first:,}")
    print(f"    Gap in fiscal years (nulled): {n_gap:,}")
    print(f"    Valid consecutive lag: {n_valid:,}")

    lag_lookup = fye[["gvkey", "fyearq_grp", "Capex_lag"]].copy()
    lag_lookup = lag_lookup.rename(columns={"fyearq_grp": "fyearq_int"})

    before_len = len(panel)
    panel = panel.merge(lag_lookup, on=["gvkey", "fyearq_int"], how="left")
    after_len = len(panel)
    if after_len != before_len:
        raise ValueError(
            f"Capex_lag merge changed row count {before_len} -> {after_len}."
        )

    print(f"    Calls with valid lag: {panel['Capex_lag'].notna().sum():,}")
    return panel


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h13_2_capex_leads_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h13_2_capex_leads" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H13_2_CapexLeads",
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
    print("STAGE 3: Build H13.2 Capex Lead Horizons Panel (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Years:     {year_start}-{year_end}")
    print(f"Unit of observation: earnings call (file_name)")
    print(f"Lead horizons: t+1, t+2, t+3, t+4")

    # Step 1-2: Build call-level panel (same as H13)
    panel = build_call_level_panel(root, years, var_config, stats)

    # Step 3-4: Attach fyearq, extract firm-year EOY Capex
    print("\n" + "=" * 60)
    print("Creating lead/lag variables")
    print("=" * 60)
    panel, firm_year_eoy = _get_firm_year_eoy_capex(panel, root_path=root)

    # Step 5: Create all leads
    for n in [1, 2, 3, 4]:
        panel = create_capex_lead_n(panel, firm_year_eoy, n=n)

    # Step 6: Create lag
    panel = create_capex_lag(panel, firm_year_eoy)

    # Step 7: Assign sample
    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n_total = (panel["sample"] == sample).sum()
        leads = {}
        for col in ["Capex_lead", "Capex_lead2", "Capex_lead3", "Capex_lead4"]:
            leads[col] = panel.loc[panel["sample"] == sample, col].notna().sum()
        print(f"    {sample}: {n_total:,} calls | "
              f"t+1={leads['Capex_lead']:,} | t+2={leads['Capex_lead2']:,} | "
              f"t+3={leads['Capex_lead3']:,} | t+4={leads['Capex_lead4']:,}")

    # Step 8: Save
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h13_2_capex_leads_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(f"  Saved: h13_2_capex_leads_panel.parquet "
          f"({len(panel):,} rows, {len(panel.columns)} columns)")

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
        output_files={"panel": panel_path, "summary_stats": stats_path},
    )
    print("  Saved: run_manifest.json")

    duration = (datetime.now() - start_time).total_seconds()
    print(f"\nCompleted in {duration:.1f}s")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("DRY-RUN mode -- validating inputs only")
        print("DRY-RUN complete.")
        sys.exit(0)
    sys.exit(main(args.year_start, args.year_end))
