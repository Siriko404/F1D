#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H23 Competition → Uncertainty Language Panel
================================================================================
ID: variables/build_h23_competition_uncertainty_panel
Description: Build FIRM-YEAR panel for H23 Competition hypothesis test.

    Tests whether product-market competition (Hoberg-Phillips TNIC3 TSIMM)
    predicts managerial uncertainty language on earnings calls.

    This is a firm-year panel (like H22). Linguistic variables are averaged
    across all calls within a fiscal year; financial controls are taken from
    the latest call.

    Step 1: Load manifest + all call-level variables (linguistic + financial).
    Step 2: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 3: Attach fyearq via merge_asof (Compustat fiscal year).
    Step 4: Collapse to firm-year:
            - Linguistic: mean across calls within (gvkey, fyearq_int)
            - Financial controls: value from latest call per firm-year
    Step 5: Merge TNIC3HHIdata on (gvkey_int, fyearq_int) → TotalSimilarity.
    Step 6: Log-transform: log_TotalSimilarity = ln(TotalSimilarity).
    Step 7: Set cal_yr = fyearq_int (B1 fix — NOT from start_date).
    Step 8: Assign industry sample, save.

Unit of observation: firm-fiscal-year (gvkey, fyearq_int).

DV: UncAnsMgr, UncAnsCEO, UncPreMgr, UncPreCEO (firm-year averages).
IV: log(TotalSimilarity) — Hoberg & Phillips (2016, JPE).
Direction: Two-tailed.

Inputs:
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet  (Compustat)
    - inputs/TNIC3HHIdata/TNIC3HHIdata.txt

Outputs:
    - outputs/variables/h23_competition_uncertainty/{timestamp}/h23_competition_uncertainty_panel.parquet
    - outputs/variables/h23_competition_uncertainty/{timestamp}/summary_stats.csv

Reference: Hoberg, G. & Phillips, G. (2016). Text-Based Network Industries and
           Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465.

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
    # Linguistic uncertainty (DVs — averaged to firm-year)
    ManagerQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    NonCEOManagerQAUncertaintyBuilder,
    NonCEOManagerPresUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,      # → UncQue (control)
    NegativeSentimentBuilder,          # → NegCall (control)
    # Financial controls (from H11 pattern — uncertainty-DV appropriate)
    SizeBuilder,                       # → lnAssets
    TobinsQBuilder,                    # → TobinsQ
    ROABuilder,                        # → ROA
    CashHoldingsBuilder,               # → CashRatio
    DividendPayerBuilder,              # → DivDummy
    FirmMaturityBuilder,               # → FirmMat
    EarningsVolatilityBuilder,         # → EarnVol
    # Manifest
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


# Linguistic columns to average across calls within fiscal year
# Note: 2026-04-19 — fixed stale `UncAnsNoCEOMgr` typo (engine column is `UncAnsNoCEO`,
# rename map at `_linguistic_engine.py:183`). Added `UncPreNoCEO` for partition-variant
# robustness suites. Without these the firm-year collapse silently dropped NoCEO QA.
LING_COLS = [
    "UncAnsMgr",
    "UncAnsCEO",
    "UncPreMgr",
    "UncPreCEO",
    "UncAnsNoCEO",
    "UncPreNoCEO",
    "UncQue",       # analyst QA uncertainty (control)
    "NegCall",      # negative sentiment (control)
]

# Financial controls: take from latest call per firm-year
CONTROL_COLS = [
    "lnAssets",
    "TobinsQ",
    "ROA",
    "CashRatio",
    "DivDummy",
    "FirmMat",
    "EarnVol",
]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H23 Competition → Uncertainty Panel (firm-year)",
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
        # Linguistic — DVs + controls
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
        # Financial controls (H11 pattern — uncertainty-DV appropriate)
        "size": SizeBuilder({}),
        "tobins_q": TobinsQBuilder({}),
        "roa": ROABuilder({}),
        "cash_holdings": CashHoldingsBuilder({}),
        "dividend_payer": DividendPayerBuilder({}),
        "firm_maturity": FirmMaturityBuilder({}),
        "earnings_volatility": EarningsVolatilityBuilder({}),
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

    if "ff12_code" not in panel.columns:
        raise ValueError(
            "ff12_code column missing from panel after manifest merge. "
            "Cannot assign industry sample."
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
        - Linguistic vars: mean across calls (fiscal-year average)
        - Financial controls: value from latest call (proxy for year-end)
        - ff12_code: first (constant within firm)
        - start_date: latest call date
        - n_calls: count of calls in that fiscal year
    """
    print("\n" + "=" * 60)
    print("Collapsing to firm-year")
    print("=" * 60)

    # Attach fyearq via merge_asof with Compustat
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

    # Average linguistic vars across all calls within fiscal year
    ling_present = [c for c in LING_COLS if c in panel.columns]

    if ling_present:
        ling_means = (
            panel.groupby(["gvkey", "fyearq_int"])[ling_present]
            .mean()
            .reset_index()
        )

        before_len = len(firm_year)
        firm_year = firm_year.merge(ling_means, on=["gvkey", "fyearq_int"], how="left")
        assert len(firm_year) == before_len, (
            f"Linguistic mean merge changed row count: {before_len} -> {len(firm_year)}"
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


def merge_tnic_data(
    firm_year: pd.DataFrame, root_path: Path
) -> pd.DataFrame:
    """Merge Hoberg-Phillips TNIC3 TotalSimilarity data.

    Merge key: (gvkey_int, fyearq_int) — same pattern as H1.1/H13.1.
    Known limitation: TNIC year = first 4 digits of Compustat datadate,
    which differs from fyearq for ~10% of non-December FYE firms.
    We follow the existing pipeline pattern for consistency.
    """
    print("\n" + "=" * 60)
    print("Merging TNIC3 TotalSimilarity data")
    print("=" * 60)

    tnic_path = root_path / "inputs" / "TNIC3HHIdata" / "TNIC3HHIdata.txt"
    if not tnic_path.exists():
        raise FileNotFoundError(f"TNIC data not found: {tnic_path}")

    tnic = pd.read_csv(tnic_path, sep="\t")
    print(f"  Loaded TNIC: {len(tnic):,} rows, "
          f"{tnic['gvkey'].nunique():,} firms, "
          f"years {tnic['year'].min()}-{tnic['year'].max()}")

    # Convert panel gvkey to int for merge
    firm_year["_gvkey_int"] = pd.to_numeric(firm_year["gvkey"], errors="coerce")

    before_len = len(firm_year)
    firm_year = firm_year.merge(
        tnic[["gvkey", "year", "tnic3tsimm"]].rename(
            columns={"gvkey": "_gvkey_int", "year": "fyearq_int",
                      "tnic3tsimm": "TotalSimilarity"}
        ),
        on=["_gvkey_int", "fyearq_int"],
        how="left",
    )
    assert len(firm_year) == before_len, (
        f"TNIC merge changed row count: {before_len} -> {len(firm_year)}"
    )

    firm_year = firm_year.drop(columns=["_gvkey_int"])

    # Match diagnostics
    n_matched = firm_year["TotalSimilarity"].notna().sum()
    n_total = len(firm_year)
    print(f"  Matched: {n_matched:,} / {n_total:,} ({100 * n_matched / n_total:.1f}%)")
    print(f"  Unmatched: {n_total - n_matched:,}")

    # Log-transform then z-score on Main sample (consistent with H1.1/H13.1)
    firm_year["log_TotalSimilarity"] = np.log(firm_year["TotalSimilarity"])

    main_mask = ~firm_year["ff12_code"].isin([8, 11])
    log_main = firm_year.loc[main_mask, "log_TotalSimilarity"].dropna()
    tsimm_mu = log_main.mean()
    tsimm_sd = log_main.std()

    firm_year["z_log_TotalSimilarity"] = (
        firm_year["log_TotalSimilarity"] - tsimm_mu
    ) / tsimm_sd

    # Distribution diagnostics
    ts = firm_year["TotalSimilarity"].dropna()
    lts = firm_year["log_TotalSimilarity"].dropna()
    zts = firm_year.loc[main_mask, "z_log_TotalSimilarity"].dropna()
    print(f"  TotalSimilarity: mean={ts.mean():.2f}, median={ts.median():.2f}, "
          f"min={ts.min():.2f}, max={ts.max():.2f}")
    print(f"  log(TSIMM): mean={lts.mean():.4f}, std={lts.std():.4f}")
    print(f"  z(log(TSIMM)) on Main: mean={zts.mean():.4f}, std={zts.std():.4f}")
    print(f"  z-score params: mu={tsimm_mu:.4f}, sd={tsimm_sd:.4f}")

    return firm_year


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h23_competition_uncertainty_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h23_competition_uncertainty" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H23_CompetitionUncertainty",
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
    print("STAGE 3: Build H23 Competition → Uncertainty Panel (firm-year)")
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

    # Step 5-6: Merge TNIC data + log-transform
    firm_year = merge_tnic_data(firm_year, root)

    # Step 7: Set cal_yr from calendar year of latest call (NOT fiscal year)
    # Per feedback_calendar_yr_qtr_fe.md: Year FE must use CALENDAR year
    firm_year["cal_yr"] = pd.to_datetime(
        firm_year["start_date"], errors="coerce"
    ).dt.year

    # Step 8: Assign sample
    if "ff12_code" not in firm_year.columns:
        raise ValueError("ff12_code missing from panel. Cannot assign sample.")
    firm_year["sample"] = assign_industry_sample(firm_year["ff12_code"])

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (firm_year["sample"] == sample).sum()
        n_tnic = firm_year.loc[
            firm_year["sample"] == sample, "TotalSimilarity"
        ].notna().sum()
        print(f"    {sample}: {n:,} firm-years, "
              f"{n_tnic:,} with TNIC data")

    # Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h23_competition_uncertainty_panel.parquet"
    firm_year.to_parquet(panel_path, index=False)
    print(
        f"  Saved: h23_competition_uncertainty_panel.parquet "
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
    tnic_input = root / "inputs" / "TNIC3HHIdata" / "TNIC3HHIdata.txt"
    generate_manifest(
        output_dir=out_dir,
        stage="stage3",
        timestamp=timestamp,
        input_paths={
            "master_manifest": manifest_input,
            "tnic_data": tnic_input,
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
