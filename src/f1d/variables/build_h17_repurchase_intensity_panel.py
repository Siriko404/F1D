#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H17 Repurchase Intensity Panel
================================================================================
ID: variables/build_h17_repurchase_intensity_panel
Description: Build CALL-LEVEL panel for H17 Repurchase Intensity hypothesis.

    Unit of observation: individual earnings call (file_name).
    DV: RepurchaseIntensity = quarterly_prstkcy / atq_{t-1}
        (de-cumulated YTD prstkcy divided by previous quarter's total assets)
    Lead DVs:
        RepurchaseIntensity_lead_qtr: next fiscal quarter's RepurchaseIntensity

    Known limitation: ~77% of firm-quarters have RepurchaseIntensity = 0
    (many firms do not repurchase every quarter). OLS with continuous DV.
    prstkcy includes both common AND preferred stock repurchases (standard).

Inputs:
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - Compustat (via shared engine)
    - CRSP (via VolatilityBuilder)
    - Linguistic variables (via shared builders)

Outputs:
    - outputs/variables/h17_repurchase_intensity/{timestamp}/h17_repurchase_intensity_panel.parquet

Author: Thesis Author
Date: 2026-03-26
================================================================================
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
    ManagerPresUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    RepurchaseIntensityBuilder,
    SizeBuilder,
    BookLevBuilder,
    TobinsQBuilder,
    ROABuilder,
    CashHoldingsBuilder,
    CapexIntensityBuilder,
    DividendPayerBuilder,
    OCFVolatilityBuilder,
    SalesGrowthBuilder,
    RDIntensityBuilder,
    CashFlowBuilder,
    VolatilityBuilder,
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H17 Repurchase Intensity Panel (call-level)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def build_call_level_panel(
    root_path: Path, years: range, var_config: Dict[str, Any], stats: Dict[str, Any],
) -> pd.DataFrame:
    """Build call-level panel by loading and merging all variables."""
    print("\n" + "=" * 60)
    print("Loading variables (call-level)")
    print("=" * 60)

    all_results: Dict[str, Any] = {}

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        "manager_qa_uncertainty": ManagerQAUncertaintyBuilder(
            var_config.get("manager_qa_uncertainty", {})
        ),
        "manager_pres_uncertainty": ManagerPresUncertaintyBuilder(
            var_config.get("manager_pres_uncertainty", {})
        ),
        "ceo_qa_uncertainty": CEOQAUncertaintyBuilder(
            var_config.get("ceo_qa_uncertainty", {})
        ),
        "ceo_pres_uncertainty": CEOPresUncertaintyBuilder(
            var_config.get("ceo_pres_uncertainty", {})
        ),
        "repurchase_intensity": RepurchaseIntensityBuilder({}),
        "size": SizeBuilder({}),
        "book_lev": BookLevBuilder({}),
        "tobins_q": TobinsQBuilder({}),
        "roa": ROABuilder({}),
        "cash_holdings": CashHoldingsBuilder({}),
        "capex_intensity": CapexIntensityBuilder({}),
        "dividend_payer": DividendPayerBuilder({}),
        "ocf_volatility": OCFVolatilityBuilder({}),
        "sales_growth": SalesGrowthBuilder({}),
        "rd_intensity": RDIntensityBuilder({}),
        "cash_flow": CashFlowBuilder({}),
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
        raise ValueError(f"Manifest has {n_dups} duplicate file_name rows.")

    print(f"\n  Base manifest: {len(panel):,} rows")

    for name, result in all_results.items():
        if name == "manifest":
            continue
        data = result.data.copy()
        if "file_name" not in data.columns or len(data.columns) <= 1:
            continue
        if data["file_name"].duplicated().any():
            n_dups = data["file_name"].duplicated().sum()
            raise ValueError(f"Builder '{name}' returned {n_dups} duplicate file_name rows.")
        conflicting = [c for c in data.columns if c in panel.columns and c != "file_name"]
        if conflicting:
            data = data.drop(columns=conflicting)
        before_len = len(panel)
        panel = panel.merge(data, on="file_name", how="left")
        if len(panel) != before_len:
            raise ValueError(f"Merge of '{name}' changed row count.")
        print(f"  After {name} merge: {len(panel):,} rows (delta: +0)")

    if "ff12_code" not in panel.columns:
        raise ValueError("ff12_code missing after manifest merge.")

    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    stats_list = [result.stats for result in all_results.values()]
    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def create_lead_variables(panel: pd.DataFrame, root_path: Optional[Path] = None) -> pd.DataFrame:
    """Create lead and lag DVs at call level.

    1. RepurchaseIntensity_lead_qtr: next fiscal quarter's RepurchaseIntensity
    2. RepurchaseIntensity_lag: previous fiscal quarter's RepurchaseIntensity

    Uses fiscal quarter from Compustat (fqtr) and fiscal year (fyearq).
    """
    print("\n" + "=" * 60)
    print("Creating lead/lag variables for RepurchaseIntensity")
    print("=" * 60)

    if "RepurchaseIntensity" not in panel.columns:
        raise ValueError("'RepurchaseIntensity' column missing.")

    # Attach fyearq if not present
    if root_path is not None and "fyearq" not in panel.columns:
        panel = attach_fyearq(panel, root_path)

    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")

    # We need fqtr (fiscal quarter) to construct quarterly leads.
    # fqtr comes from the RepurchaseIntensityBuilder (via CompustatEngine).
    if "fqtr" not in panel.columns:
        # Get fqtr from CompustatEngine via merge_asof (per-group to avoid sort issues)
        from f1d.shared.variables._compustat_engine import get_engine
        engine = get_engine()
        comp = engine.get_data(root_path)
        panel["start_date_dt"] = pd.to_datetime(panel["start_date"], errors="coerce")
        panel["gvkey_z"] = panel["gvkey"].astype(str).str.zfill(6)
        comp_fqtr = comp[["gvkey", "datadate", "fqtr"]].copy()
        comp_fqtr = comp_fqtr.rename(columns={"gvkey": "gvkey_z"})
        comp_fqtr = comp_fqtr.sort_values(["gvkey_z", "datadate"])

        # Per-group merge_asof (safe, avoids global sort requirement)
        chunks = []
        for gvkey, grp in panel.sort_values("start_date_dt").groupby("gvkey_z"):
            comp_grp = comp_fqtr[comp_fqtr["gvkey_z"] == gvkey]
            if len(comp_grp) == 0:
                grp = grp.copy()
                grp["fqtr"] = np.nan
                chunks.append(grp)
                continue
            m = pd.merge_asof(
                grp.sort_values("start_date_dt"),
                comp_grp.sort_values("datadate"),
                left_on="start_date_dt",
                right_on="datadate",
                direction="backward",
                suffixes=("", "_comp"),
            )
            if "gvkey_z_comp" in m.columns:
                m = m.drop(columns=["gvkey_z_comp"])
            if "datadate" in m.columns:
                m = m.drop(columns=["datadate"])
            chunks.append(m)

        panel = pd.concat(chunks, ignore_index=True)
        panel = panel.drop(columns=["gvkey_z", "start_date_dt"], errors="ignore")
        print(f"  Attached fqtr via merge_asof: {panel['fqtr'].notna().sum():,} / {len(panel):,}")

    panel["fqtr_int"] = pd.to_numeric(panel["fqtr"], errors="coerce")

    # Create a unique fiscal quarter identifier for sorting/shifting
    # fiscal_qtr_id = fyearq_int * 10 + fqtr_int (e.g., 20103 = FY2010 Q3)
    panel["fiscal_qtr_id"] = panel["fyearq_int"] * 10 + panel["fqtr_int"]

    print(f"  Total calls: {len(panel):,}")
    print(f"  Calls with valid fiscal_qtr_id: {panel['fiscal_qtr_id'].notna().sum():,}")

    # --- Build firm-quarter lookup table ---
    panel_dt = panel.copy()
    panel_dt["start_date_dt"] = pd.to_datetime(panel_dt["start_date"], errors="coerce")

    valid_mask = panel_dt["fiscal_qtr_id"].notna()
    panel_valid = panel_dt[valid_mask].copy()

    # For each (gvkey, fiscal_qtr_id), take RepurchaseIntensity from the call with latest start_date
    latest_idx = panel_valid.groupby(["gvkey", "fiscal_qtr_id"])["start_date_dt"].idxmax()
    firm_qtr = panel_valid.loc[
        latest_idx, ["gvkey", "fiscal_qtr_id", "fyearq_int", "fqtr_int", "RepurchaseIntensity"]
    ].copy()
    firm_qtr = firm_qtr.sort_values(["gvkey", "fiscal_qtr_id"]).reset_index(drop=True)

    print(f"  Unique firm-quarters: {len(firm_qtr):,}")

    # --- Lead 1: Next fiscal quarter ---
    firm_qtr["fiscal_qtr_id_next"] = firm_qtr.groupby("gvkey")["fiscal_qtr_id"].shift(-1)
    firm_qtr["RepurchaseIntensity_lead_qtr_raw"] = firm_qtr.groupby("gvkey")["RepurchaseIntensity"].shift(-1)

    # Check consecutive: next quarter should be current + 1 within year,
    # or Q1 of next year if current is Q4
    curr_fq = firm_qtr["fiscal_qtr_id"]
    next_fq = firm_qtr["fiscal_qtr_id_next"]
    expected_next = np.where(
        firm_qtr["fqtr_int"] < 4,
        curr_fq + 1,           # e.g., 20102 -> 20103
        (firm_qtr["fyearq_int"] + 1) * 10 + 1,  # e.g., 20104 -> 20111
    )
    consecutive_qtr = next_fq == expected_next
    firm_qtr["RepurchaseIntensity_lead_qtr"] = np.where(
        consecutive_qtr, firm_qtr["RepurchaseIntensity_lead_qtr_raw"], np.nan
    )

    n_valid_lead_qtr = firm_qtr["RepurchaseIntensity_lead_qtr"].notna().sum()
    print(f"  Firm-quarters with valid next-quarter lead: {n_valid_lead_qtr:,}")

    # --- Merge leads back to call level ---
    lead_lookup = firm_qtr[["gvkey", "fiscal_qtr_id", "RepurchaseIntensity_lead_qtr"]].copy()

    before_len = len(panel)
    panel = panel.merge(lead_lookup, on=["gvkey", "fiscal_qtr_id"], how="left")
    if len(panel) != before_len:
        raise ValueError(f"Lead merge changed row count {before_len} -> {len(panel)}.")

    print(f"  Calls with next-quarter lead: {panel['RepurchaseIntensity_lead_qtr'].notna().sum():,}")

    # --- Lag: Previous fiscal quarter ---
    firm_qtr["fiscal_qtr_id_prev"] = firm_qtr.groupby("gvkey")["fiscal_qtr_id"].shift(1)
    firm_qtr["RepurchaseIntensity_lag_raw"] = firm_qtr.groupby("gvkey")["RepurchaseIntensity"].shift(1)

    # Check consecutive: prev quarter should be current - 1 within year,
    # or Q4 of prev year if current is Q1
    prev_fq = firm_qtr["fiscal_qtr_id_prev"]
    expected_prev = np.where(
        firm_qtr["fqtr_int"] > 1,
        curr_fq - 1,
        (firm_qtr["fyearq_int"] - 1) * 10 + 4,
    )
    consecutive_prev = prev_fq == expected_prev
    firm_qtr["RepurchaseIntensity_lag"] = np.where(
        consecutive_prev, firm_qtr["RepurchaseIntensity_lag_raw"], np.nan
    )
    n_valid_lag = firm_qtr["RepurchaseIntensity_lag"].notna().sum()
    print(f"  Firm-quarters with valid prev-quarter lag: {n_valid_lag:,}")

    lag_lookup = firm_qtr[["gvkey", "fiscal_qtr_id", "RepurchaseIntensity_lag"]].copy()
    before_len2 = len(panel)
    panel = panel.merge(lag_lookup, on=["gvkey", "fiscal_qtr_id"], how="left")
    if len(panel) != before_len2:
        raise ValueError(f"Lag merge changed row count {before_len2} -> {len(panel)}.")
    print(f"  Calls with prev-quarter lag: {panel['RepurchaseIntensity_lag'].notna().sum():,}")

    # Create calendar year-quarter identifier for FE
    panel["start_date_dt"] = pd.to_datetime(panel["start_date"], errors="coerce")
    panel["cal_yearqtr"] = (
        panel["start_date_dt"].dt.year * 10 + panel["start_date_dt"].dt.quarter
    )
    panel = panel.drop(columns=["start_date_dt"], errors="ignore")

    return panel


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h17_repurchase_intensity_panel",
        "timestamp": timestamp,
        "variable_stats": [],
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h17_repurchase_intensity" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H17_RepurchaseIntensity",
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
    print("STAGE 3: Build H17 Repurchase Intensity Panel (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Years:     {year_start}-{year_end}")

    # Build panel
    panel = build_call_level_panel(root, years, var_config, stats)

    # Create lead variables
    panel = create_lead_variables(panel, root_path=root)

    # Assign sample
    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    # Report DV coverage
    n_with_dv = panel["RepurchaseIntensity"].notna().sum()
    n_missing = panel["RepurchaseIntensity"].isna().sum()
    print(f"\n  RepurchaseIntensity non-null: {n_with_dv:,}")
    print(f"  RepurchaseIntensity NaN: {n_missing:,}")

    # Report zero mass point
    if n_with_dv > 0:
        n_zeros = (panel["RepurchaseIntensity"] == 0).sum()
        print(f"  RepurchaseIntensity == 0 (no repurchase this quarter): {n_zeros:,} "
              f"({100 * n_zeros / n_with_dv:.1f}% of non-null)")

    # Save
    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h17_repurchase_intensity_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(f"\n  Saved: h17_repurchase_intensity_panel.parquet ({len(panel):,} rows, {len(panel.columns)} cols)")

    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv")

    manifest_input = root / "outputs" / "1.4_AssembleManifest" / "latest" / "master_sample_manifest.parquet"
    generate_manifest(
        output_dir=out_dir, stage="stage3", timestamp=timestamp,
        input_paths={"master_manifest": manifest_input},
        output_files={"panel": panel_path},
    )
    print("  Saved: run_manifest.json")

    duration = (datetime.now() - start_time).total_seconds()
    print(f"\n  Duration: {duration:.1f}s")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: OK")
        sys.exit(0)
    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
