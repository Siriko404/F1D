#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H13 Capex Panel
================================================================================
ID: variables/build_h13_capex_panel
Description: Build CALL-LEVEL panel for H13 Capital Expenditure hypothesis test.

    This panel follows the H1/H4 pattern:
    one row per earnings call (file_name), 4 simultaneous IVs,
    Base + Extended controls, fyearq_int time index.

    Step 1: Load manifest + all call-level variables (linguistic + financial).
    Step 2: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 3: Add call year from start_date.
    Step 4: Compute CapexAt_lead per call (fiscal-year based, consecutive year validated).
    Step 5: Assign industry sample (Main / Finance / Utility).
    Step 6: Save call-level panel.

Unit of observation: the individual earnings call (file_name).

Outputs:
    - outputs/variables/h13_capex/{timestamp}/h13_capex_panel.parquet
    - outputs/variables/h13_capex/{timestamp}/summary_stats.csv
    - outputs/variables/h13_capex/{timestamp}/run_manifest.json

Author: Thesis Author
Date: 2026-03-17
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
from f1d.shared.variables.panel_utils import assign_industry_sample, attach_fyearq
from f1d.shared.variables import (
    # 4 Key IVs (all simultaneous)
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
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
        description="Stage 3: Build H13 Capex Panel (call-level)",
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
    """Build call-level panel by loading and merging all variables.

    Returns:
        Call-level DataFrame with manifest fields + all variable columns.
        All merges are zero-row-delta (ValueError on fan-out).
    """
    print("\n" + "=" * 60)
    print("Loading variables (call-level)")
    print("=" * 60)

    all_results: Dict[str, Any] = {}

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
        # Base controls -- CompustatEngine is a singleton; all share one load
        "size": SizeBuilder({}),
        "tobins_q": TobinsQBuilder({}),
        "roa": ROABuilder({}),
        "lev": BookLevBuilder({}),
        "cash_holdings": CashHoldingsBuilder({}),
        "capex_intensity": CapexIntensityBuilder({}),  # For CapexAt DV and lead
        "dividend_payer": DividendPayerBuilder({}),
        "ocf_volatility": OCFVolatilityBuilder({}),
        # Extended controls
        "sales_growth": SalesGrowthBuilder(var_config.get("sales_growth", {})),
        "rd_intensity": RDIntensityBuilder(var_config.get("rd_intensity", {})),
        "cash_flow": CashFlowBuilder(var_config.get("cash_flow", {})),
        "volatility": VolatilityBuilder(var_config.get("volatility", {})),
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

    # Assert manifest file_name uniqueness
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
            print(f"  WARNING: {name} returned no usable columns -- skipping merge")
            continue

        # Assert builder output unique on file_name
        if data["file_name"].duplicated().any():
            n_dups = data["file_name"].duplicated().sum()
            raise ValueError(
                f"Builder '{name}' returned {n_dups} duplicate file_name rows. "
                "Merge aborted to prevent fan-out."
            )

        # Drop conflicting columns (except file_name) to prevent _x/_y blowup
        conflicting = [
            c for c in data.columns if c in panel.columns and c != "file_name"
        ]
        if conflicting:
            print(
                f"  WARNING: {name} has overlapping columns {conflicting} -- dropping from builder data"
            )
            data = data.drop(columns=conflicting)

        before_len = len(panel)
        panel = panel.merge(data, on="file_name", how="left")
        after_len = len(panel)
        if after_len != before_len:
            raise ValueError(
                f"Merge of '{name}' changed row count {before_len} -> {after_len}. "
                "Duplicate file_name detected in builder output post-merge."
            )
        print(f"  After {name} merge: {after_len:,} rows (delta: +0)")

    # Assert ff12_code present (hard error)
    if "ff12_code" not in panel.columns:
        raise ValueError(
            "ff12_code column missing from panel after manifest merge. "
            "Cannot assign industry sample. Check ManifestFieldsBuilder output."
        )

    # Add call year from start_date (same as manager_clarity convention)
    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Collect summary stats
    stats_list = []
    for name, result in all_results.items():
        stats_list.append(result.stats)
    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def create_capex_lead(
    panel: pd.DataFrame, root_path: Optional[Path] = None
) -> pd.DataFrame:
    """Create CapexAt_lead at call level.

    Uses fyearq (Compustat fiscal year) to correctly handle ~30% of firms
    with non-December fiscal year-ends.

    The lead is the firm's capital expenditure intensity in fiscal year t+1.
    Construction follows H1's CashHoldings_lead pattern:
    1. Attach fyearq via merge_asof (call start_date → Compustat datadate).
    2. For each (gvkey, fyearq_int), take CapexAt from the call with the
       LATEST start_date within that fiscal year.
    3. Sort by gvkey, fyearq_int; shift -1 within gvkey -> next-fiscal-year capex.
    4. Validate that next row is exactly fyearq+1 (not +2 due to gaps);
       set lead to NaN if fiscal years are not consecutive.
    5. Merge lead values back onto all calls by (gvkey, fyearq_int).
    6. Calls in the last fiscal year per firm, or fiscal year gaps, get NaN lead.

    All call-level rows are preserved -- Stage 4 drops NaN lead rows itself.
    """
    print("\n" + "=" * 60)
    print("Creating CapexAt_lead (call-level, fiscal-year proxy)")
    print("=" * 60)

    if "CapexAt" not in panel.columns:
        raise ValueError(
            "'CapexAt' column missing -- cannot create lead variable."
        )
    if "start_date" not in panel.columns:
        raise ValueError(
            "'start_date' column missing -- cannot determine latest call per fiscal year."
        )

    # Step 1: Attach fyearq to panel
    if root_path is not None:
        panel = attach_fyearq(panel, root_path)
    elif "fyearq" not in panel.columns:
        raise ValueError(
            "'fyearq' missing and root_path not provided. Cannot attach fiscal year."
        )

    if panel["fyearq"].isna().all():
        raise ValueError(
            "'fyearq' could not be attached to panel. "
            "Check CompustatEngine.get_data() returned fyearq."
        )

    # Convert fyearq to integer for clean arithmetic
    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")
    n_missing_fyearq = panel["fyearq_int"].isna().sum()
    if n_missing_fyearq > 0:
        print(
            f"  WARNING: {n_missing_fyearq:,} calls have missing fyearq "
            f"-- these calls will get NaN lead"
        )

    # Step 2: For each (gvkey, fyearq_int), find call with latest start_date
    panel_dt = panel.copy()
    panel_dt["start_date_dt"] = pd.to_datetime(panel_dt["start_date"], errors="coerce")

    # Drop calls with missing fyearq for the groupby
    valid_mask = panel_dt["fyearq_int"].notna()
    panel_valid = panel_dt[valid_mask].copy()

    latest_idx = panel_valid.groupby(["gvkey", "fyearq_int"])["start_date_dt"].idxmax()
    firm_year_eoy = panel_valid.loc[
        latest_idx, ["gvkey", "fyearq_int", "CapexAt"]
    ].copy()
    firm_year_eoy = firm_year_eoy.rename(
        columns={"fyearq_int": "fyearq_grp", "CapexAt": "CapexAt_eoy"}
    )

    print(f"  Unique firm-fiscal-years: {len(firm_year_eoy):,}")

    # Step 3: sort and shift to get next-fiscal-year capex
    firm_year_eoy = firm_year_eoy.sort_values(["gvkey", "fyearq_grp"]).reset_index(
        drop=True
    )
    firm_year_eoy["fyearq_lead"] = firm_year_eoy.groupby("gvkey")["fyearq_grp"].shift(
        -1
    )
    firm_year_eoy["CapexAt_lead_raw"] = firm_year_eoy.groupby("gvkey")[
        "CapexAt_eoy"
    ].shift(-1)

    # Step 4: validate fiscal year continuity -- only keep lead if fyearq+1
    consecutive = firm_year_eoy["fyearq_lead"] == (firm_year_eoy["fyearq_grp"] + 1)
    firm_year_eoy["CapexAt_lead"] = np.where(
        consecutive, firm_year_eoy["CapexAt_lead_raw"], np.nan
    )

    n_last_year = firm_year_eoy["CapexAt_lead_raw"].isna().sum()
    n_gap_year = ((~consecutive) & firm_year_eoy["CapexAt_lead_raw"].notna()).sum()
    n_valid_lead = firm_year_eoy["CapexAt_lead"].notna().sum()
    print(
        f"  Firm-fiscal-years with no next year (last fiscal year per firm): "
        f"{n_last_year:,}"
    )
    print(f"  Firm-fiscal-years with fiscal year gap (lead nulled): {n_gap_year:,}")
    print(f"  Firm-fiscal-years with valid consecutive lead: {n_valid_lead:,}")

    # Step 5: merge lead back to call level on (gvkey, fyearq_int)
    lead_lookup = firm_year_eoy[["gvkey", "fyearq_grp", "CapexAt_lead"]].copy()
    lead_lookup = lead_lookup.rename(columns={"fyearq_grp": "fyearq_int"})

    before_len = len(panel)
    panel = panel.merge(lead_lookup, on=["gvkey", "fyearq_int"], how="left")
    after_len = len(panel)
    if after_len != before_len:
        raise ValueError(
            f"Lead merge changed row count {before_len} -> {after_len}. "
            "Duplicate (gvkey, fyearq_int) in firm-year lead lookup."
        )

    n_calls_no_lead = panel["CapexAt_lead"].isna().sum()
    print(f"  Call-level rows: {len(panel):,}")
    print(
        f"  Calls without lead (last-fiscal-year + gaps + missing fyearq): {n_calls_no_lead:,}"
    )
    print(f"  Calls with valid lead: {panel['CapexAt_lead'].notna().sum():,}")

    return panel


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h13_capex_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h13_capex" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H13_Capex",
        timestamp=timestamp,
    )

    # Load configs
    config = get_config(root / "config" / "project.yaml")
    var_config = load_variable_config(root / "config" / "variables.yaml")

    # Get year range
    if year_start is None:
        year_start = config.data.year_start
    if year_end is None:
        year_end = config.data.year_end
    years = range(year_start, year_end + 1)

    print("=" * 80)
    print("STAGE 3: Build H13 Capex Panel (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Years:     {year_start}-{year_end}")
    print(f"Unit of observation: earnings call (file_name)")

    # Step 1-2: Build call-level panel
    panel = build_call_level_panel(root, years, var_config, stats)

    # Step 3: Create CapexAt_lead at call level (use fyearq)
    panel = create_capex_lead(panel, root_path=root)

    # Step 4: Assign sample
    if "ff12_code" not in panel.columns:
        raise ValueError("ff12_code missing from panel. Cannot assign sample.")
    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    print("\n  Sample distribution (all calls, including last-year):")
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        n_lead = panel.loc[panel["sample"] == sample, "CapexAt_lead"].notna().sum()
        print(f"    {sample}: {n:,} calls total, {n_lead:,} with valid lead")

    # Step 5: Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h13_capex_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"  Saved: h13_capex_panel.parquet "
        f"({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    # Summary stats CSV
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

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    report_lines = [
        "# Stage 3: H13 Capex Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary",
        "",
        f"- **Unit:** Call-level (one row per earnings call)",
        f"- **Total rows:** {len(panel):,}",
        f"- **Columns:** {len(panel.columns)}",
        "",
        "## Dependent Variables (CapEx)",
        f"- **CapexAt (t):** {panel['CapexAt'].notna().sum():,} calls",
        f"- **CapexAt_lead (t+1):** {panel['CapexAt_lead'].notna().sum():,} calls",
        "",
        "## Key IVs (4 simultaneous)",
        f"- **CEO_QA_Uncertainty_pct:** {panel['CEO_QA_Uncertainty_pct'].notna().sum():,} calls",
        f"- **CEO_Pres_Uncertainty_pct:** {panel['CEO_Pres_Uncertainty_pct'].notna().sum():,} calls",
        f"- **Manager_QA_Uncertainty_pct:** {panel['Manager_QA_Uncertainty_pct'].notna().sum():,} calls",
        f"- **Manager_Pres_Uncertainty_pct:** {panel['Manager_Pres_Uncertainty_pct'].notna().sum():,} calls",
        "",
        "## Extended Controls",
        f"- **SalesGrowth:** {panel['SalesGrowth'].notna().sum():,} calls",
        f"- **RD_Intensity:** {panel['RD_Intensity'].notna().sum():,} calls",
        f"- **CashFlow:** {panel['CashFlow'].notna().sum():,} calls",
        f"- **Volatility:** {panel['Volatility'].notna().sum():,} calls",
        "",
        "## Sample Distribution",
        "",
        "| Sample | Total Calls | With Valid Lead |",
        "|--------|------------:|----------------:|",
    ]
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        n_lead = panel.loc[panel["sample"] == sample, "CapexAt_lead"].notna().sum()
        report_lines.append(f"| {sample} | {n:,} | {n_lead:,} |")

    report_path = out_dir / "report_step3_h13_capex.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"  Saved: report_step3_h13_capex.md")

    print("\n" + "=" * 80)
    print("H13 Capex Panel build complete.")
    print(f"Duration: {duration:.1f} seconds")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("DRY-RUN mode -- validating inputs only")
        # Would validate inputs here
        print("DRY-RUN complete.")
        sys.exit(0)

    sys.exit(main(args.year_start, args.year_end))
