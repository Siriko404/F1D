#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H5b Wang (2020) Analyst Dispersion Panel
================================================================================
ID: variables/build_h5b_wang_disp_panel
Description: Build CALL-LEVEL panel for H5b Wang Dispersion hypothesis test.

    Unit of observation: individual earnings call (file_name).
    DV: WangDISP = SD(analyst forecasts T-31..T-1) / prccq_prior
    Lead DV: WangDISP_lead = next fiscal quarter's WangDISP
    Lagged DV control: WangDISP_lag = prior fiscal quarter's WangDISP

Reference: Wang (2020, Review of Accounting and Finance 19(3): 289-312).
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
    # Key IVs (4 simultaneous)
    ManagerQAUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    # DV
    WangDispBuilder,
    # Base controls
    SizeBuilder,
    BookLevBuilder,
    ROABuilder,
    TobinsQBuilder,
    CapexIntensityBuilder,
    DividendPayerBuilder,
    OCFVolatilityBuilder,
    # Extended controls
    EarningsSurpriseBuilder,
    LossDummyBuilder,
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    # Infrastructure
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H5b Wang Dispersion Panel",
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
    print("Building H5b Wang Dispersion Panel")
    print("=" * 60)

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        # Key IVs
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
        # DV (Wang 2020 dispersion)
        "wang_disp": WangDispBuilder(var_config.get("wang_disp", {})),
        # Base controls
        "size": SizeBuilder(var_config.get("size", {})),
        "lev": BookLevBuilder(var_config.get("lev", {})),
        "roa": ROABuilder(var_config.get("roa", {})),
        "tobins_q": TobinsQBuilder(var_config.get("tobins_q", {})),
        "capex_intensity": CapexIntensityBuilder(
            var_config.get("capex_intensity", {})
        ),
        "dividend_payer": DividendPayerBuilder(var_config.get("dividend_payer", {})),
        "ocf_volatility": OCFVolatilityBuilder(
            var_config.get("ocf_volatility", {})
        ),
        # Extended controls
        "earnings_surprise": EarningsSurpriseBuilder(
            var_config.get("earnings_surprise", {})
        ),
        "loss_dummy": LossDummyBuilder(var_config.get("loss_dummy", {})),
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(
            var_config.get("analyst_qa_uncertainty", {})
        ),
        "negative_sentiment": NegativeSentimentBuilder(
            var_config.get("negative_sentiment", {})
        ),
    }

    all_results = {}
    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    panel = all_results["manifest"].data.copy()

    assert panel["file_name"].is_unique, (
        f"Manifest file_name not unique: {panel['file_name'].duplicated().sum()} duplicates"
    )

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

    if "ff12_code" not in panel.columns:
        raise ValueError("'ff12_code' not in panel.")
    panel["sample"] = assign_industry_sample(panel["ff12_code"])
    panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Attach fiscal year
    panel = attach_fyearq(panel, root_path)
    panel["fyearq_int"] = np.floor(
        pd.to_numeric(panel["fyearq"], errors="coerce")
    ).astype("Int64")

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    return panel


def create_lead_lag_variables(panel: pd.DataFrame, root_path: Optional[Path] = None) -> pd.DataFrame:
    """Create lead and lag WangDISP at call level using fiscal quarter shifting.

    Adapts H12Q's lead construction pattern (fiscal_qtr_id shifting).
    """
    print("\n" + "=" * 60)
    print("Creating lead/lag variables for WangDISP")
    print("=" * 60)

    if "WangDISP" not in panel.columns:
        raise ValueError("'WangDISP' column missing.")

    # Attach fqtr if not present
    if root_path is not None and "fyearq" not in panel.columns:
        panel = attach_fyearq(panel, root_path)

    panel["fyearq_int"] = pd.to_numeric(
        panel.get("fyearq", panel.get("fyearq_int")), errors="coerce"
    )

    # Get fqtr from CompustatEngine if not present
    if "fqtr" not in panel.columns:
        from f1d.shared.variables._compustat_engine import get_engine
        engine = get_engine()
        comp = engine.get_data(root_path)
        panel["start_date_dt"] = pd.to_datetime(panel["start_date"], errors="coerce")
        panel["gvkey_z"] = panel["gvkey"].astype(str).str.zfill(6)
        comp_fqtr = comp[["gvkey", "datadate", "fqtr"]].copy()
        comp_fqtr = comp_fqtr.rename(columns={"gvkey": "gvkey_z"})
        comp_fqtr = comp_fqtr.sort_values(["gvkey_z", "datadate"])

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
        print(f"  Attached fqtr: {panel['fqtr'].notna().sum():,} / {len(panel):,}")

    panel["fqtr_int"] = pd.to_numeric(panel["fqtr"], errors="coerce")

    # Create fiscal quarter identifier
    panel["fiscal_qtr_id"] = panel["fyearq_int"] * 10 + panel["fqtr_int"]

    print(f"  Total calls: {len(panel):,}")
    print(f"  Calls with valid fiscal_qtr_id: {panel['fiscal_qtr_id'].notna().sum():,}")

    # --- Build firm-quarter lookup table ---
    panel_dt = panel.copy()
    panel_dt["start_date_dt"] = pd.to_datetime(panel_dt["start_date"], errors="coerce")

    valid_mask = panel_dt["fiscal_qtr_id"].notna()
    panel_valid = panel_dt[valid_mask].copy()

    # For each (gvkey, fiscal_qtr_id), take WangDISP from call with latest start_date
    latest_idx = panel_valid.groupby(["gvkey", "fiscal_qtr_id"])["start_date_dt"].idxmax()
    firm_qtr = panel_valid.loc[
        latest_idx, ["gvkey", "fiscal_qtr_id", "fyearq_int", "fqtr_int", "WangDISP"]
    ].copy()
    firm_qtr = firm_qtr.sort_values(["gvkey", "fiscal_qtr_id"]).reset_index(drop=True)

    print(f"  Unique firm-quarters: {len(firm_qtr):,}")

    # --- Lead: Next fiscal quarter's WangDISP ---
    firm_qtr["fiscal_qtr_id_next"] = firm_qtr.groupby("gvkey")["fiscal_qtr_id"].shift(-1)
    firm_qtr["WangDISP_lead_raw"] = firm_qtr.groupby("gvkey")["WangDISP"].shift(-1)

    # Validate consecutive quarters
    curr_fq = firm_qtr["fiscal_qtr_id"]
    next_fq = firm_qtr["fiscal_qtr_id_next"]
    expected_next = np.where(
        firm_qtr["fqtr_int"] < 4,
        curr_fq + 1,
        (firm_qtr["fyearq_int"] + 1) * 10 + 1,
    )
    consecutive_qtr = next_fq == expected_next
    firm_qtr["WangDISP_lead"] = np.where(
        consecutive_qtr, firm_qtr["WangDISP_lead_raw"], np.nan
    )

    n_lead = firm_qtr["WangDISP_lead"].notna().sum()
    print(f"  Firm-quarters with valid next-quarter lead: {n_lead:,}")

    # --- Lag: Prior fiscal quarter's WangDISP ---
    firm_qtr["fiscal_qtr_id_prev"] = firm_qtr.groupby("gvkey")["fiscal_qtr_id"].shift(1)
    firm_qtr["WangDISP_lag_raw"] = firm_qtr.groupby("gvkey")["WangDISP"].shift(1)

    # Validate consecutive (backwards)
    prev_fq = firm_qtr["fiscal_qtr_id_prev"]
    expected_prev = np.where(
        firm_qtr["fqtr_int"] > 1,
        curr_fq - 1,
        (firm_qtr["fyearq_int"] - 1) * 10 + 4,
    )
    consecutive_prev = prev_fq == expected_prev
    firm_qtr["WangDISP_lag"] = np.where(
        consecutive_prev, firm_qtr["WangDISP_lag_raw"], np.nan
    )

    n_lag = firm_qtr["WangDISP_lag"].notna().sum()
    print(f"  Firm-quarters with valid prior-quarter lag: {n_lag:,}")

    # --- Merge lead + lag back to call level ---
    lead_lag_lookup = firm_qtr[["gvkey", "fiscal_qtr_id", "WangDISP_lead", "WangDISP_lag"]].copy()

    before_len = len(panel)
    panel = panel.merge(lead_lag_lookup, on=["gvkey", "fiscal_qtr_id"], how="left")
    if len(panel) != before_len:
        raise ValueError(f"Lead/lag merge changed row count {before_len} -> {len(panel)}.")

    print(f"  Calls with next-quarter lead: {panel['WangDISP_lead'].notna().sum():,}")
    print(f"  Calls with prior-quarter lag: {panel['WangDISP_lag'].notna().sum():,}")

    return panel


def save_outputs(panel: pd.DataFrame, stats: Dict[str, Any], out_dir: Path, root: Path, timestamp: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "h5b_wang_disp_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(f"\n  Saved: h5b_wang_disp_panel.parquet ({len(panel):,} rows, {len(panel.columns)} cols)")

    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

    generate_manifest(
        output_dir=out_dir,
        stage="stage3",
        timestamp=timestamp,
        input_paths={},
        output_files={
            "panel": panel_path,
            "summary_stats": stats_path,
        },
    )
    print("  Saved: run_manifest.json")


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h5b_wang_disp_panel",
        "timestamp": timestamp,
        "variable_stats": [],
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h5b_wang_disp" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H5b_WangDisp",
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
    print("STAGE 3: Build H5b Wang Dispersion Panel")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")

    panel = build_panel(root, years, var_config, stats)
    panel = create_lead_lag_variables(panel, root)
    save_outputs(panel, stats, out_dir, root, timestamp)

    duration = (datetime.now() - start_time).total_seconds()
    print(f"\nCOMPLETE in {duration:.1f}s")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        sys.exit(0)
    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
