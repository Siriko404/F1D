#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H21 SEC Comment Letters Count Panel
================================================================================
ID: variables/build_h21_sec_letters_panel
Description: Build CALL-LEVEL panel for H21 SEC comment letter count hypothesis.

    Unit of observation: individual earnings call (file_name).
    DV: SEC_Letters_fwd = COUNT of EDGAR UPLOAD letters firm received in next calendar quarter
        SEC_Letters_lag = COUNT of EDGAR UPLOAD letters firm received in previous calendar quarter

    Data source: inputs/EDGAR_CommentLetters/letters_all.parquet (full EDGAR universe)
    Filter: form == "UPLOAD" only (SEC-originated correspondence; excludes CORRESP = firm responses)
    CIK-gvkey linkage: Combined CCM linktable + Compustat CIK field (integer match).

    Estimator: PanelOLS (OLS on count DV — standard in empirical finance).

Inputs:
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - inputs/EDGAR_CommentLetters/letters_all.parquet
    - inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet
    - Compustat (via shared engine, for CIK + controls)
    - CRSP (via VolatilityBuilder)
    - Linguistic variables (via shared builders)

Outputs:
    - outputs/variables/h21_sec_letters/{timestamp}/h21_sec_letters_panel.parquet

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
        description="Stage 3: Build H21 SEC Letters Count Panel (call-level)",
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
    print(f"  CIK-gvkey map: {len(combined):,} unique CIKs "
          f"(CCM={len(ccm_map):,}, Compustat adds {len(combined)-len(ccm_map):,})")
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


def _load_edgar_upload_counts(
    root_path: Path, cik_gvkey_map: pd.DataFrame,
) -> Dict[tuple, int]:
    """Load EDGAR UPLOAD letters and return {(gvkey, cal_qtr_id): count} dict.

    Filters to form == "UPLOAD" only (SEC-originated correspondence).
    CORRESP letters (firm responses) are excluded.
    """
    edgar_path = root_path / "inputs" / "EDGAR_CommentLetters" / "letters_all.parquet"
    edgar = pd.read_parquet(edgar_path, columns=["cik", "form", "filing_date"])

    n_total = len(edgar)
    edgar = edgar[edgar["form"] == "UPLOAD"].copy()
    n_upload = len(edgar)
    print(f"  EDGAR total: {n_total:,}, UPLOAD only: {n_upload:,} "
          f"(excluded {n_total - n_upload:,} CORRESP)")

    edgar["cik_int"] = pd.to_numeric(edgar["cik"], errors="coerce").astype("Int64")
    edgar["filing_date"] = pd.to_datetime(edgar["filing_date"])

    # Link CIK to gvkey
    edgar = edgar.merge(cik_gvkey_map, on="cik_int", how="inner")
    edgar["gvkey"] = edgar["gvkey"].astype(str).str.zfill(6)
    print(f"  UPLOAD letters linked to gvkey: {len(edgar):,}")

    # Compute calendar quarter
    edgar["cal_qtr_id"] = (
        edgar["filing_date"].dt.year * 10 + edgar["filing_date"].dt.quarter
    ).astype(int)

    # Count per (gvkey, quarter)
    counts = edgar.groupby(["gvkey", "cal_qtr_id"]).size()
    count_dict = {(g, q): int(c) for (g, q), c in counts.items()}
    print(f"  Unique (gvkey, quarter) with letters: {len(count_dict):,}")
    print(f"  Count distribution: mean={counts.mean():.2f}, "
          f"median={counts.median():.1f}, max={counts.max()}")

    return count_dict


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


def create_sec_letters_dvs(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Create SEC letter count DVs from EDGAR UPLOAD data.

    For each call at date d in calendar quarter Q:
        SEC_Letters_fwd = COUNT of UPLOAD letters in quarter Q+1
        SEC_Letters_lag = COUNT of UPLOAD letters in quarter Q-1
    """
    print("\n" + "=" * 60)
    print("Creating SEC Letters Count DV (EDGAR UPLOAD, next quarter)")
    print("=" * 60)

    cik_gvkey_map = _build_cik_gvkey_map(root_path)
    count_dict = _load_edgar_upload_counts(root_path, cik_gvkey_map)

    panel["gvkey"] = panel["gvkey"].astype(str).str.zfill(6)
    dt = pd.to_datetime(panel["start_date"], errors="coerce")
    panel["cal_qtr_id"] = (dt.dt.year * 10 + dt.dt.quarter).astype("Int64")

    gvkeys = panel["gvkey"].values
    cal_qtrs = panel["cal_qtr_id"].values

    fwd = np.zeros(len(panel), dtype=np.float64)
    lag = np.zeros(len(panel), dtype=np.float64)

    for i in range(len(panel)):
        g = gvkeys[i]
        q = cal_qtrs[i]
        if pd.isna(q):
            fwd[i] = np.nan
            lag[i] = np.nan
            continue
        q = int(q)
        fwd[i] = float(count_dict.get((g, _next_cal_qtr(q)), 0))
        lag[i] = float(count_dict.get((g, _prev_cal_qtr(q)), 0))

    panel["SEC_Letters_fwd"] = fwd
    panel["SEC_Letters_lag"] = lag

    n_pos = (panel["SEC_Letters_fwd"] > 0).sum()
    mean_val = panel["SEC_Letters_fwd"].mean()
    max_val = panel["SEC_Letters_fwd"].max()
    print(f"  SEC_Letters_fwd > 0: {n_pos:,} / {len(panel):,} ({100*n_pos/len(panel):.2f}%)")
    print(f"  Mean: {mean_val:.3f}, Max: {max_val:.0f}")
    print(f"  Distribution:")
    vc = panel["SEC_Letters_fwd"].value_counts().sort_index().head(10)
    for val, cnt in vc.items():
        print(f"    {int(val):3d}: {cnt:,} ({100*cnt/len(panel):.2f}%)")

    return panel


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h21_sec_letters_panel",
        "timestamp": timestamp,
        "variable_stats": [],
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h21_sec_letters" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H21_SEC_Letters",
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
    print("STAGE 3: Build H21 SEC Letters Count Panel (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Years:     {year_start}-{year_end}")

    panel = build_call_level_panel(root, years, var_config, stats)

    panel = attach_fyearq(panel, root)
    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")

    panel = create_sec_letters_dvs(panel, root)

    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h21_sec_letters_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(f"\n  Saved: h21_sec_letters_panel.parquet ({len(panel):,} rows, {len(panel.columns)} cols)")

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
