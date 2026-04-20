#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H22 Equity Financing Constraints Panel
================================================================================
ID: variables/build_h22_equity_constraints_panel
Description: Build FIRM-YEAR panel for H22 Equity Constraints hypothesis test.

    This is the first firm-year (not call-level) panel in the pipeline.
    It collapses call-level linguistic variables to fiscal-year averages
    and merges with the Hoberg & Maksimovic (2015, RFS) financial
    constraints database.

    Step 1: Load manifest + all call-level variables (linguistic + financial).
    Step 2: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 3: Attach fyearq via merge_asof (Compustat fiscal year).
    Step 4: Collapse to firm-year:
            - IVs: mean across calls within (gvkey, fyearq_int)
            - Financial controls: value from latest call in that fiscal year
            - ff12_code, start_date: from latest call
    Step 5: Merge Hoberg-Maksimovic constraints data on (gvkey_int, fyearq_int).
    Step 6: Create EquityDelayCon_lead (fyearq+1) and EquityDelayCon_lag (fyearq-1).
    Step 7: Set cal_yr = fyearq_int (NOT from start_date — B1 fix).
    Step 8: Assign industry sample, save.

Unit of observation: firm-fiscal-year (gvkey, fyearq_int).

DV: EquityDelayCon_lead — Hoberg & Maksimovic (2015) equity-specific financial
    constraint score from NEXT fiscal year's 10-K. Higher = more equity-constrained.
    Based on cosine similarity of CAPLIQ text to equity-delay training set,
    with boilerplate purging. Mean ~ 0 by construction.

Inputs:
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet  (Compustat)
    - inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet        (CRSP daily)
    - inputs/ConstraintsDatabase_ext2015/ConstraintsDatabase_ext2015.txt

Outputs:
    - outputs/variables/h22_equity_constraints/{timestamp}/h22_equity_constraints_panel.parquet
    - outputs/variables/h22_equity_constraints/{timestamp}/summary_stats.csv

Reference: Hoberg, G. & Maksimovic, V. (2015). Redefining Financial Constraints:
           A Text-Based Analysis. Review of Financial Studies, 28(5), 1312-1352.

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
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from f1d.shared.config import load_variable_config, get_config
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest
from f1d.shared.variables.panel_utils import assign_industry_sample, attach_fyearq
from f1d.shared.variables import (
    # Linguistic uncertainty (H22 key IVs — averaged to firm-year)
    ManagerQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    NonCEOManagerQAUncertaintyBuilder,
    NonCEOManagerPresUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    # Financial controls — base (Compustat engine singleton)
    CashHoldingsBuilder,
    BookLevBuilder,
    SizeBuilder,
    TobinsQBuilder,
    ROABuilder,
    CapexIntensityBuilder,
    DividendPayerBuilder,
    OCFVolatilityBuilder,
    CurrentRatioBuilder,
    # Financial controls — extended
    SalesGrowthBuilder,
    RDIntensityBuilder,
    CashFlowBuilder,
    VolatilityBuilder,
    # Manifest
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


# IVs to average across calls within fiscal year
IV_COLS = [
    "UncAnsCEO",
    "UncPreCEO",
    "UncAnsMgr",
    "UncPreMgr",
]

# Financial controls: take from latest call per firm-year
CONTROL_COLS = [
    "CashRatio",
    "Leverage",
    "lnAssets",
    "TobinsQ",
    "ROA",
    "Capex",
    "DivDummy",
    "sCFO",
    "CurrentRatio",
    # Extended
    "SalesGrowth",
    "RDSales",
    "CashFlowAt",
    "DailyVola",
]

# Additional linguistic cols to average (for downstream consumers)
# Note: 2026-04-19 — fixed stale `UncAnsNoCEOMgr` typo (engine column is `UncAnsNoCEO`,
# rename map at `_linguistic_engine.py:183`). Added `UncPreNoCEO` for partition-variant
# robustness suites (H22.r). Without these the firm-year collapse silently dropped the
# NoCEO QA column despite the builder running successfully.
EXTRA_LING_COLS = [
    "UncAnsNoCEO",
    "UncPreNoCEO",
    "UncAnsAnalyst",
    "NegSent",
]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H22 Equity Constraints Panel (firm-year)",
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
        # Linguistic uncertainty
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
        "nonceo_manager_qa_uncertainty": NonCEOManagerQAUncertaintyBuilder(
            var_config.get("nonceo_manager_qa_uncertainty", {})
        ),
        "nonceo_manager_pres_uncertainty": NonCEOManagerPresUncertaintyBuilder(
            var_config.get("nonceo_manager_pres_uncertainty", {})
        ),
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(
            var_config.get("analyst_qa_uncertainty", {})
        ),
        "negative_sentiment": NegativeSentimentBuilder(
            var_config.get("negative_sentiment", {})
        ),
        # Financial controls — CompustatEngine is a singleton; all share one load
        "cash_holdings": CashHoldingsBuilder({}),
        "lev": BookLevBuilder({}),
        "size": SizeBuilder({}),
        "tobins_q": TobinsQBuilder({}),
        "roa": ROABuilder({}),
        "capex_intensity": CapexIntensityBuilder({}),
        "dividend_payer": DividendPayerBuilder({}),
        "ocf_volatility": OCFVolatilityBuilder({}),
        "current_ratio": CurrentRatioBuilder({}),
        # Extended controls
        "sales_growth": SalesGrowthBuilder({}),
        "rd_intensity": RDIntensityBuilder({}),
        "cash_flow": CashFlowBuilder({}),
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

        # Drop conflicting columns (except file_name)
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

    # Assert ff12_code present
    if "ff12_code" not in panel.columns:
        raise ValueError(
            "ff12_code column missing from panel after manifest merge. "
            "Cannot assign industry sample. Check ManifestFieldsBuilder output."
        )

    # Collect summary stats
    stats_list = []
    for name, result in all_results.items():
        stats_list.append(result.stats)
    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def collapse_to_firm_year(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Collapse call-level panel to firm-year unit.

    For each (gvkey, fyearq_int):
        - IVs: mean across calls (fiscal-year average uncertainty)
        - Financial controls: value from latest call (proxy for year-end)
        - ff12_code: first (constant within firm)
        - start_date: latest call date
        - n_calls: count of calls in that fiscal year

    Returns:
        Firm-year DataFrame with one row per (gvkey, fyearq_int).
    """
    print("\n" + "=" * 60)
    print("Collapsing to firm-year")
    print("=" * 60)

    # Attach fyearq via merge_asof
    panel = attach_fyearq(panel, root_path)
    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")

    n_missing = panel["fyearq_int"].isna().sum()
    if n_missing > 0:
        print(f"  WARNING: {n_missing:,} calls have missing fyearq -- dropped from collapse")
        panel = panel[panel["fyearq_int"].notna()].copy()

    panel["fyearq_int"] = panel["fyearq_int"].astype(int)
    panel["start_date_dt"] = pd.to_datetime(panel["start_date"], errors="coerce")

    n_calls_before = len(panel)
    n_firm_years = panel.groupby(["gvkey", "fyearq_int"]).ngroups
    print(f"  Calls: {n_calls_before:,}")
    print(f"  Unique (gvkey, fyearq_int): {n_firm_years:,}")

    # Identify the latest call per firm-year for controls
    latest_idx = panel.groupby(["gvkey", "fyearq_int"])["start_date_dt"].idxmax()
    latest_calls = panel.loc[latest_idx].copy()

    # Build firm-year panel: start with latest call's data for controls + metadata
    keep_cols = (
        ["gvkey", "fyearq_int", "start_date", "ff12_code"]
        + [c for c in CONTROL_COLS if c in latest_calls.columns]
    )
    firm_year = latest_calls[keep_cols].copy()

    # Average IVs across all calls within fiscal year
    iv_cols_present = [c for c in IV_COLS if c in panel.columns]
    extra_ling_present = [c for c in EXTRA_LING_COLS if c in panel.columns]
    all_ling = iv_cols_present + extra_ling_present

    if all_ling:
        ling_means = (
            panel.groupby(["gvkey", "fyearq_int"])[all_ling]
            .mean()
            .reset_index()
        )

        before_len = len(firm_year)
        firm_year = firm_year.merge(ling_means, on=["gvkey", "fyearq_int"], how="left")
        assert len(firm_year) == before_len, (
            f"IV mean merge changed row count: {before_len} -> {len(firm_year)}"
        )

    # Count calls per firm-year (diagnostic)
    call_counts = (
        panel.groupby(["gvkey", "fyearq_int"])
        .size()
        .reset_index(name="n_calls_in_year")
    )
    firm_year = firm_year.merge(call_counts, on=["gvkey", "fyearq_int"], how="left")

    # Assert uniqueness
    if firm_year[["gvkey", "fyearq_int"]].duplicated().any():
        raise ValueError("Duplicate (gvkey, fyearq_int) after collapse!")

    # Diagnostics
    print(f"  Firm-year panel: {len(firm_year):,} rows")
    print(f"  Unique firms: {firm_year['gvkey'].nunique():,}")
    print(f"  Fiscal year range: {firm_year['fyearq_int'].min()}-{firm_year['fyearq_int'].max()}")
    print(f"  Calls per firm-year distribution:")
    cc = firm_year["n_calls_in_year"]
    print(f"    Mean: {cc.mean():.1f}, Median: {cc.median():.0f}, "
          f"Min: {cc.min()}, Max: {cc.max()}")
    for n in [1, 2, 3, 4]:
        pct = (cc == n).sum() / len(cc) * 100
        print(f"    {n} call(s): {(cc == n).sum():,} ({pct:.1f}%)")
    pct_5plus = (cc >= 5).sum() / len(cc) * 100
    print(f"    5+ calls: {(cc >= 5).sum():,} ({pct_5plus:.1f}%)")

    return firm_year


def merge_constraints_data(
    firm_year: pd.DataFrame, root_path: Path
) -> pd.DataFrame:
    """Merge Hoberg-Maksimovic (2015) financial constraints data.

    Merge key: (gvkey_int, fyearq_int) — same pattern as TNIC merge.
    Constraints year = Compustat fyearq (empirically verified despite
    misleading README that says "calendar year of fiscal year end").

    Per Hoberg-Maksimovic README: do NOT impute 0 for missing values.
    Leave as NaN — complete-case filter in runner drops them.
    """
    print("\n" + "=" * 60)
    print("Merging Hoberg-Maksimovic financial constraints data")
    print("=" * 60)

    constraints_path = (
        root_path / "inputs" / "ConstraintsDatabase_ext2015"
        / "ConstraintsDatabase_ext2015.txt"
    )
    if not constraints_path.exists():
        raise FileNotFoundError(f"Constraints data not found: {constraints_path}")

    constraints = pd.read_csv(constraints_path, sep="\t")
    print(f"  Loaded constraints: {len(constraints):,} rows, "
          f"{constraints['gvkey'].nunique():,} firms, "
          f"years {constraints['year'].min()}-{constraints['year'].max()}")

    # Convert panel gvkey to int for merge
    firm_year["_gvkey_int"] = pd.to_numeric(firm_year["gvkey"], errors="coerce")

    before_len = len(firm_year)
    firm_year = firm_year.merge(
        constraints[["gvkey", "year", "equitydelaycon", "debtdelaycon", "delaycon"]].rename(
            columns={"gvkey": "_gvkey_int", "year": "fyearq_int"}
        ),
        on=["_gvkey_int", "fyearq_int"],
        how="left",
    )
    assert len(firm_year) == before_len, (
        f"Constraints merge changed row count: {before_len} -> {len(firm_year)}"
    )

    # Drop temp column
    firm_year = firm_year.drop(columns=["_gvkey_int"])

    # Match diagnostics
    n_matched = firm_year["equitydelaycon"].notna().sum()
    n_total = len(firm_year)
    print(f"  Matched: {n_matched:,} / {n_total:,} ({100 * n_matched / n_total:.1f}%)")
    print(f"  Unmatched: {n_total - n_matched:,} (no CAPLIQ in 10-K or outside 1997-2015)")

    # DV distribution
    edc = firm_year["equitydelaycon"].dropna()
    print(f"  equitydelaycon: mean={edc.mean():.4f}, std={edc.std():.4f}, "
          f"min={edc.min():.4f}, max={edc.max():.4f}")

    return firm_year


def create_lead_lag_variables(firm_year: pd.DataFrame) -> pd.DataFrame:
    """Create EquityDelayCon_lead (t+1) and EquityDelayCon_lag (t-1).

    Lead: next fiscal year's equitydelaycon (shift -1 within gvkey).
    Lag: previous fiscal year's equitydelaycon (shift +1 within gvkey).
    Both validated for consecutive fiscal years only.

    Pattern from build_h1_cash_holdings_panel.py, adapted to firm-year level.
    """
    print("\n" + "=" * 60)
    print("Creating lead/lag variables (firm-year level)")
    print("=" * 60)

    firm_year = firm_year.sort_values(["gvkey", "fyearq_int"]).reset_index(drop=True)

    # --- Lead (t+1) ---
    firm_year["_fyearq_next"] = firm_year.groupby("gvkey")["fyearq_int"].shift(-1)
    firm_year["_edc_lead_raw"] = firm_year.groupby("gvkey")["equitydelaycon"].shift(-1)

    consecutive_lead = firm_year["_fyearq_next"] == (firm_year["fyearq_int"] + 1)
    firm_year["EquityDelayCon_lead"] = np.where(
        consecutive_lead, firm_year["_edc_lead_raw"], np.nan
    )

    n_last_year = firm_year["_edc_lead_raw"].isna().sum()
    n_gap_lead = ((~consecutive_lead) & firm_year["_edc_lead_raw"].notna()).sum()
    n_valid_lead = firm_year["EquityDelayCon_lead"].notna().sum()
    print(f"  Lead: last year per firm (no next): {n_last_year:,}")
    print(f"  Lead: fiscal year gap (nulled): {n_gap_lead:,}")
    print(f"  Lead: valid consecutive: {n_valid_lead:,}")

    # --- Lag (t-1) ---
    firm_year["_fyearq_prev"] = firm_year.groupby("gvkey")["fyearq_int"].shift(1)
    firm_year["_edc_lag_raw"] = firm_year.groupby("gvkey")["equitydelaycon"].shift(1)

    consecutive_lag = firm_year["_fyearq_prev"] == (firm_year["fyearq_int"] - 1)
    firm_year["EquityDelayCon_lag"] = np.where(
        consecutive_lag, firm_year["_edc_lag_raw"], np.nan
    )

    n_first_year = firm_year["_edc_lag_raw"].isna().sum()
    n_gap_lag = ((~consecutive_lag) & firm_year["_edc_lag_raw"].notna()).sum()
    n_valid_lag = firm_year["EquityDelayCon_lag"].notna().sum()
    print(f"  Lag: first year per firm (no prior): {n_first_year:,}")
    print(f"  Lag: fiscal year gap (nulled): {n_gap_lag:,}")
    print(f"  Lag: valid consecutive: {n_valid_lag:,}")

    # Cleanup temp columns
    firm_year = firm_year.drop(
        columns=["_fyearq_next", "_edc_lead_raw", "_fyearq_prev", "_edc_lag_raw"]
    )

    return firm_year


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h22_equity_constraints_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h22_equity_constraints" / timestamp

    # Setup logging
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H22_EquityConstraints",
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
    print("STAGE 3: Build H22 Equity Financing Constraints Panel (firm-year)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Years:     {year_start}-{year_end}")
    print(f"Unit of observation: firm-fiscal-year (gvkey, fyearq_int)")

    # Step 1-2: Build call-level panel (standard pattern)
    panel = build_call_level_panel(root, years, var_config, stats)

    # Step 3-4: Collapse to firm-year
    firm_year = collapse_to_firm_year(panel, root)

    # Free call-level panel memory
    del panel

    # Step 5: Merge constraints data
    firm_year = merge_constraints_data(firm_year, root)

    # Step 6: Create lead/lag
    firm_year = create_lead_lag_variables(firm_year)

    # Step 7: Set cal_yr = fyearq_int (B1 fix — NOT from start_date)
    firm_year["cal_yr"] = firm_year["fyearq_int"]

    # Step 8: Assign sample
    if "ff12_code" not in firm_year.columns:
        raise ValueError("ff12_code missing from panel. Cannot assign sample.")
    firm_year["sample"] = assign_industry_sample(firm_year["ff12_code"])

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (firm_year["sample"] == sample).sum()
        n_lead = firm_year.loc[
            firm_year["sample"] == sample, "EquityDelayCon_lead"
        ].notna().sum()
        n_edc = firm_year.loc[
            firm_year["sample"] == sample, "equitydelaycon"
        ].notna().sum()
        print(f"    {sample}: {n:,} firm-years, "
              f"{n_edc:,} with constraints data, "
              f"{n_lead:,} with valid lead")

    # Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h22_equity_constraints_panel.parquet"
    firm_year.to_parquet(panel_path, index=False)
    print(
        f"  Saved: h22_equity_constraints_panel.parquet "
        f"({len(firm_year):,} rows, {len(firm_year.columns)} columns)"
    )

    # Summary stats CSV
    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

    # Generate run manifest
    manifest_input = (
        root / "outputs" / "1.4_AssembleManifest" / "latest"
        / "master_sample_manifest.parquet"
    )
    constraints_input = (
        root / "inputs" / "ConstraintsDatabase_ext2015"
        / "ConstraintsDatabase_ext2015.txt"
    )
    generate_manifest(
        output_dir=out_dir,
        stage="stage3",
        timestamp=timestamp,
        input_paths={
            "master_manifest": manifest_input,
            "constraints_data": constraints_input,
        },
        output_files={
            "panel": panel_path,
            "summary_stats": stats_path,
        },
        panel_path=panel_path,
    )
    print("  Saved: run_manifest.json")

    duration = (datetime.now() - start_time).total_seconds()
    print(f"\nCompleted in {duration:.1f}s")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main(args.year_start, args.year_end))
