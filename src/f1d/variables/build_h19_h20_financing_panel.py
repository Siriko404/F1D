#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H19/H20 Financing Classification Panel
================================================================================
ID: variables/build_h19_h20_financing_panel
Description: Build CALL-LEVEL panel for H19 (External vs Internal Funding) and
    H20 (Debt vs Equity Choice) hypothesis suites.

    Unit of observation: individual earnings call (file_name).

    DVs (Leary & Roberts 2010, JFE):
        ExternalFunding = 1 if external (debt or equity issuance >5% of lagged
            assets), 0 if internal (neither threshold met)
        DebtChoice = 1 if debt-only issuance, 0 if equity or dual issuance
            (NaN if internal)

    Classification rules:
        Debt issuance:   Δ(dlcq + dlttq) / lagged_atq > 5% (balance sheet change)
        Equity issuance: (sstky − prstkcy) / lagged_atq > 5% (cash flow statement)
        Internal: neither threshold met
        Dual: both met → classified as equity per L&R convention

    Lead/Lag DVs (annual, shifted by fiscal year ±1):
        ExternalFunding_lead: next fiscal year's classification
        ExternalFunding_lag:  previous fiscal year's classification (Lagged_DV for H19 AND H20)
        DebtChoice_lead:      next fiscal year's debt choice (NaN if next year = internal)
        DebtChoice_lag:       previous fiscal year's debt choice (NaN if prev year = internal)

Inputs:
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - Compustat (via shared engine)
    - CRSP (via VolatilityBuilder)
    - Linguistic variables (via shared builders)

Outputs:
    - outputs/variables/h19_h20_financing/{timestamp}/h19_h20_financing_panel.parquet

Author: Thesis Author
Date: 2026-03-31
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
    ExternalFundingBuilder,
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
        description="Stage 3: Build H19/H20 Financing Classification Panel (call-level)",
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
        "external_funding": ExternalFundingBuilder({}),
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


def create_financing_dvs(panel: pd.DataFrame, root_path: Optional[Path] = None) -> pd.DataFrame:
    """Create annual lead/lag DVs for ExternalFunding and DebtChoice.

    Since both DVs are ANNUAL (same value for all calls in a fiscal year),
    lead = next fiscal year's classification (fyearq + 1)
    lag  = previous fiscal year's classification (fyearq - 1)
    """
    print("\n" + "=" * 60)
    print("Creating annual lead/lag variables for financing classification")
    print("=" * 60)

    if "ExternalFunding" not in panel.columns:
        raise ValueError("'ExternalFunding' column missing.")

    # Attach fyearq if not present
    if root_path is not None and "fyearq" not in panel.columns:
        panel = attach_fyearq(panel, root_path)

    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")

    print(f"  Total calls: {len(panel):,}")
    print(f"  Calls with valid fyearq: {panel['fyearq_int'].notna().sum():,}")

    # --- Build firm-year lookup table ---
    # For each (gvkey, fyearq), take the DV value.
    # Since the DV is annual (same for all calls in a fiscal year), any call works.
    valid_mask = panel["fyearq_int"].notna()
    panel_valid = panel[valid_mask].copy()

    firm_yr = (
        panel_valid.groupby(["gvkey", "fyearq_int"])[["ExternalFunding", "DebtChoice"]]
        .first()
        .reset_index()
    )
    firm_yr = firm_yr.sort_values(["gvkey", "fyearq_int"]).reset_index(drop=True)
    print(f"  Unique firm-years: {len(firm_yr):,}")

    # --- Lead: next fiscal year (fyearq + 1) ---
    firm_yr_lead = firm_yr.copy()
    firm_yr_lead["fyearq_int"] -= 1  # shift backward so it joins to current year
    firm_yr_lead = firm_yr_lead.rename(columns={
        "ExternalFunding": "ExternalFunding_lead",
        "DebtChoice": "DebtChoice_lead",
    })

    before_len = len(panel)
    panel = panel.merge(
        firm_yr_lead[["gvkey", "fyearq_int", "ExternalFunding_lead", "DebtChoice_lead"]],
        on=["gvkey", "fyearq_int"],
        how="left",
    )
    if len(panel) != before_len:
        raise ValueError(f"Lead merge changed row count {before_len} -> {len(panel)}.")

    n_lead = panel["ExternalFunding_lead"].notna().sum()
    print(f"  Calls with ExternalFunding_lead: {n_lead:,} / {len(panel):,}")

    # --- Lag: previous fiscal year (fyearq - 1) ---
    firm_yr_lag = firm_yr.copy()
    firm_yr_lag["fyearq_int"] += 1  # shift forward so it joins to current year
    firm_yr_lag = firm_yr_lag.rename(columns={
        "ExternalFunding": "ExternalFunding_lag",
        "DebtChoice": "DebtChoice_lag",
    })

    before_len2 = len(panel)
    panel = panel.merge(
        firm_yr_lag[["gvkey", "fyearq_int", "ExternalFunding_lag", "DebtChoice_lag"]],
        on=["gvkey", "fyearq_int"],
        how="left",
    )
    if len(panel) != before_len2:
        raise ValueError(f"Lag merge changed row count {before_len2} -> {len(panel)}.")

    n_lag = panel["ExternalFunding_lag"].notna().sum()
    print(f"  Calls with ExternalFunding_lag: {n_lag:,} / {len(panel):,}")

    # Calendar year-quarter identifier for FE
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
        "step_id": "build_h19_h20_financing_panel",
        "timestamp": timestamp,
        "variable_stats": [],
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h19_h20_financing" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H19_H20_Financing",
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
    print("STAGE 3: Build H19/H20 Financing Classification Panel (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Years:     {year_start}-{year_end}")

    # Build panel
    panel = build_call_level_panel(root, years, var_config, stats)

    # Create annual lead/lag DVs
    panel = create_financing_dvs(panel, root_path=root)

    # Assign sample
    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    # Report DV coverage
    n_ef = panel["ExternalFunding"].notna().sum()
    n_ext = (panel["ExternalFunding"] == 1).sum()
    n_int = (panel["ExternalFunding"] == 0).sum()
    n_dc = panel["DebtChoice"].notna().sum()
    n_debt = (panel["DebtChoice"] == 1).sum()
    n_eq = (panel["DebtChoice"] == 0).sum()

    print(f"\n  ExternalFunding non-null: {n_ef:,}")
    print(f"    External=1: {n_ext:,} ({100 * n_ext / n_ef:.1f}%)")
    print(f"    Internal=0: {n_int:,} ({100 * n_int / n_ef:.1f}%)")
    print(f"  DebtChoice non-null (external only): {n_dc:,}")
    print(f"    Debt-only=1:   {n_debt:,} ({100 * n_debt / n_dc:.1f}%)")
    print(f"    Equity/Dual=0: {n_eq:,} ({100 * n_eq / n_dc:.1f}%)")

    # Save
    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h19_h20_financing_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(f"\n  Saved: h19_h20_financing_panel.parquet ({len(panel):,} rows, {len(panel.columns)} cols)")

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
