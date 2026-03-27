#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H18 SEC Comment Letters Received Panel
================================================================================
ID: variables/build_h18_cccl_received_panel
Description: Build CALL-LEVEL panel for H18 SEC Comment Letter receipt hypothesis.

    Unit of observation: individual earnings call (file_name).
    DV: CCCL_next1q = 1 if firm received SEC comment letter in next calendar quarter
        CCCL_next2q = 1 if firm received SEC comment letter in next 2 calendar quarters

    CIK-gvkey linkage: Combined CCM linktable + Compustat CIK field (integer match).
    Known: ~330 of 693 linked CCCL letters are from firms in our earnings call manifest.

    Estimator: LPM via PanelOLS. Timoneda (2021): LPM-FE outperforms logit at <5% base rate.
    Treatment rate: ~0.3-0.6% at call level (rare binary DV).

Inputs:
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - inputs/Conference Calls Comment Letters/cccl_conversations_all_years.parquet
    - inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet
    - Compustat (via shared engine, for CIK + controls)
    - CRSP (via VolatilityBuilder)
    - Linguistic variables (via shared builders)

Outputs:
    - outputs/variables/h18_cccl_received/{timestamp}/h18_cccl_received_panel.parquet

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
        description="Stage 3: Build H18 CCCL Received Panel (call-level)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def _build_cik_gvkey_map(root_path: Path) -> pd.DataFrame:
    """Build CIK -> gvkey mapping from CCM linktable + Compustat.

    Uses integer CIK comparison to avoid zero-padding issues.
    Returns DataFrame with columns [cik_int, gvkey], deduplicated by cik_int.
    """
    # Source 1: CCM linktable
    ccm_path = root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
    ccm = pd.read_parquet(ccm_path, columns=["gvkey", "cik"])
    ccm["cik_int"] = pd.to_numeric(ccm["cik"], errors="coerce").astype("Int64")
    ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
    ccm_map = ccm[ccm["cik_int"].notna()][["gvkey", "cik_int"]].drop_duplicates("cik_int")

    # Source 2: Compustat direct
    comp = pd.read_parquet(
        root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
        columns=["gvkey", "cik"],
    )
    comp = comp.dropna(subset=["cik"]).copy()
    comp["cik_int"] = pd.to_numeric(comp["cik"], errors="coerce").astype("Int64")
    comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
    comp_map = comp[comp["cik_int"].notna()][["gvkey", "cik_int"]].drop_duplicates("cik_int")

    # Combine: CCM first (preferred), then Compustat for any CIKs not in CCM
    combined = pd.concat([ccm_map, comp_map]).drop_duplicates("cik_int")
    print(f"  CIK-gvkey map: {len(combined):,} unique CIKs (CCM={len(ccm_map):,}, Compustat adds {len(combined)-len(ccm_map):,})")
    return combined


def _next_cal_qtr(cal_qtr_id: int) -> int:
    """Advance a cal_qtr_id (year*10+quarter) by one quarter."""
    yr, q = divmod(cal_qtr_id, 10)
    if q < 4:
        return yr * 10 + q + 1
    return (yr + 1) * 10 + 1


def _prev_cal_qtr(cal_qtr_id: int) -> int:
    """Go back one quarter from a cal_qtr_id."""
    yr, q = divmod(cal_qtr_id, 10)
    if q > 1:
        return yr * 10 + q - 1
    return (yr - 1) * 10 + 4


def _load_cccl_events(root_path: Path, cik_gvkey_map: pd.DataFrame) -> pd.DataFrame:
    """Load CCCL letters and return DataFrame with gvkey + filing_date.

    Uses the all_years file and links CIK to gvkey via the provided mapping.
    """
    cccl_path = (
        root_path / "inputs" / "Conference Calls Comment Letters"
        / "cccl_conversations_all_years.parquet"
    )
    cccl = pd.read_parquet(cccl_path)
    cccl["cik_int"] = pd.to_numeric(cccl["cik"], errors="coerce").astype("Int64")
    cccl["filing_date"] = pd.to_datetime(cccl["filing_date"])

    # Link CIK to gvkey
    cccl = cccl.merge(cik_gvkey_map, on="cik_int", how="inner")
    print(f"  CCCL letters linked to gvkey: {len(cccl):,}")

    return cccl[["gvkey", "filing_date"]].copy()


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


def create_cccl_dvs(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Create CCCL binary DV: received comment letter in the next calendar quarter.

    For each call at date d in calendar quarter Q:
        CCCL = 1 if firm received any CCCL in calendar quarter Q+1
        CCCL_lag = 1 if firm received any CCCL in calendar quarter Q-1
    """
    print("\n" + "=" * 60)
    print("Creating CCCL DV (next calendar quarter)")
    print("=" * 60)

    # Build CIK-gvkey map and load CCCL events
    cik_gvkey_map = _build_cik_gvkey_map(root_path)
    cccl_df = _load_cccl_events(root_path, cik_gvkey_map)
    cccl_df["gvkey"] = cccl_df["gvkey"].astype(str).str.zfill(6)

    # Build set of (gvkey, cal_qtr_id) that received CCCL
    cccl_df["cal_qtr_id"] = (
        cccl_df["filing_date"].dt.year * 10 + cccl_df["filing_date"].dt.quarter
    ).astype(int)
    cccl_set = set(zip(cccl_df["gvkey"], cccl_df["cal_qtr_id"]))
    print(f"  Unique (gvkey, cal_qtr) CCCL events: {len(cccl_set):,}")

    # For each call: calendar quarter and lookup
    panel["gvkey"] = panel["gvkey"].astype(str).str.zfill(6)
    dt = pd.to_datetime(panel["start_date"], errors="coerce")
    panel["cal_qtr_id"] = (dt.dt.year * 10 + dt.dt.quarter).astype("Int64")

    gvkeys = panel["gvkey"].values
    cal_qtrs = panel["cal_qtr_id"].values

    cccl_fwd = np.zeros(len(panel), dtype=np.float64)
    cccl_lag = np.zeros(len(panel), dtype=np.float64)

    for i in range(len(panel)):
        g = gvkeys[i]
        q = cal_qtrs[i]
        if pd.isna(q):
            cccl_fwd[i] = np.nan
            cccl_lag[i] = np.nan
            continue
        q = int(q)
        q_next = _next_cal_qtr(q)
        q_prev = _prev_cal_qtr(q)

        cccl_fwd[i] = 1.0 if (g, q_next) in cccl_set else 0.0
        cccl_lag[i] = 1.0 if (g, q_prev) in cccl_set else 0.0

    panel["CCCL"] = cccl_fwd
    panel["CCCL_lag"] = cccl_lag

    n_fwd = (panel["CCCL"] == 1).sum()
    n_lag = (panel["CCCL_lag"] == 1).sum()
    print(f"  CCCL=1: {n_fwd:,} / {len(panel):,} ({100*n_fwd/len(panel):.2f}%)")
    print(f"  CCCL_lag=1: {n_lag:,}")

    return panel


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h18_cccl_received_panel",
        "timestamp": timestamp,
        "variable_stats": [],
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h18_cccl_received" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H18_CCCL_Received",
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
    print("STAGE 3: Build H18 CCCL Received Panel (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Years:     {year_start}-{year_end}")

    # Build panel (controls + IVs)
    panel = build_call_level_panel(root, years, var_config, stats)

    # Attach fyearq for FE
    panel = attach_fyearq(panel, root)
    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")

    # Create CCCL DVs
    panel = create_cccl_dvs(panel, root)

    # Assign sample
    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    # Save
    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h18_cccl_received_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(f"\n  Saved: h18_cccl_received_panel.parquet ({len(panel):,} rows, {len(panel.columns)} cols)")

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
