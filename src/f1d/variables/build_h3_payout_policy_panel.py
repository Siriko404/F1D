#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H3 Payout Policy Panel
================================================================================
ID: variables/build_h3_payout_policy_panel
Description: Build CALL-LEVEL panel for H3 Payout Policy hypothesis test.

    Step 1: Load manifest + all call-level variables (linguistic + financial).
    Step 2: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 3: Add call year from start_date.
    Step 4: Compute div_stability_lead and payout_flexibility_lead per call:
            - Take last value per (gvkey, fyearq)
            - Shift by -1 year within gvkey -> next-fiscal-year value
            - Merge back onto all calls by (gvkey, fyearq)
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
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from f1d.shared.config import load_variable_config, get_config
from f1d.shared.variables._compustat_engine import get_engine
from f1d.shared.variables._compustat_engine import get_engine
from f1d.shared.variables import (
    ManagerQAUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    ManagerQAWeakModalBuilder,
    CEOQAWeakModalBuilder,
    ManagerPresUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    SizeBuilder,
    LevBuilder,
    ROABuilder,
    TobinsQBuilder,
    CashHoldingsBuilder,
    DivStabilityBuilder,
    PayoutFlexibilityBuilder,
    EarningsVolatilityBuilder,
    FCFGrowthBuilder,
    FirmMaturityBuilder,
    IsDivPayer5yrBuilder,
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
    
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H3 Payout Policy Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def assign_industry_sample(ff12_code: pd.Series) -> pd.Series:
    conditions = [ff12_code == 11, ff12_code == 8]
    choices = ["Finance", "Utility"]
    return pd.Series(
        np.select(conditions, choices, default="Main"),
        index=ff12_code.index,
        dtype=object,
    )


def attach_fyearq(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    if "fyearq" in panel.columns:
        return panel

    engine = get_engine()
    comp = engine.get_data(root_path)

    fyearq_df = (
        comp[["gvkey", "datadate", "fyearq"]]
        .dropna(subset=["fyearq"])
        .sort_values("datadate")
        .copy()
    )

    panel_sorted = panel.sort_values("start_date").copy()
    panel_sorted["start_date_dt"] = pd.to_datetime(
        panel_sorted["start_date"], errors="coerce"
    )
    panel_sorted = panel_sorted.dropna(subset=["start_date_dt"])

    merged = pd.merge_asof(
        panel_sorted,
        fyearq_df,
        left_on="start_date_dt",
        right_on="datadate",
        by="gvkey",
        direction="backward",
    )

    fyearq_map = merged.set_index("file_name")["fyearq"]
    panel["fyearq"] = panel["file_name"].map(fyearq_map)

    n_missing = panel["fyearq"].isna().sum()
    if n_missing > 0:
        print(f"  WARNING: {n_missing:,} calls could not be matched to a prior fyearq")

    return panel


def create_lead_variables(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Creating forward lead variables for H3 (call-level)")
    print("=" * 60)

    panel = attach_fyearq(panel, root_path)

    df = panel.copy()
    df["start_date_dt"] = pd.to_datetime(df["start_date"], errors="coerce")

    valid_mask = (
        df["fyearq"].notna() & df["gvkey"].notna() & df["start_date_dt"].notna()
    )
    df_valid = df[valid_mask].copy()

    if len(df_valid) == 0:
        print("  WARNING: No valid rows for lead creation.")
        df["div_stability_lead"] = np.nan
        df["payout_flexibility_lead"] = np.nan
        return df

    df_valid["fyearq_int"] = df_valid["fyearq"].astype(int)

    # 1. Take the last call's DV value per fiscal year (proxy for annual value)
    firm_year = df_valid.sort_values(
        ["gvkey", "fyearq_int", "start_date_dt"]
    ).drop_duplicates(subset=["gvkey", "fyearq_int"], keep="last")[
        ["gvkey", "fyearq_int", "div_stability", "payout_flexibility"]
    ]

    # 2. Shift forward 1 fiscal year within firm
    firm_year = firm_year.sort_values(["gvkey", "fyearq_int"]).reset_index(drop=True)
    firm_year["next_fyearq"] = firm_year.groupby("gvkey")["fyearq_int"].shift(-1)

    firm_year["div_stability_next"] = firm_year.groupby("gvkey")["div_stability"].shift(
        -1
    )
    firm_year["payout_flexibility_next"] = firm_year.groupby("gvkey")[
        "payout_flexibility"
    ].shift(-1)

    # 3. Validate consecutive years
    is_consecutive = (firm_year["next_fyearq"] - firm_year["fyearq_int"]) == 1
    firm_year.loc[
        ~is_consecutive, ["div_stability_next", "payout_flexibility_next"]
    ] = np.nan

    lookup = firm_year[
        ["gvkey", "fyearq_int", "div_stability_next", "payout_flexibility_next"]
    ].copy()
    lookup = lookup.rename(
        columns={
            "div_stability_next": "div_stability_lead",
            "payout_flexibility_next": "payout_flexibility_lead",
        }
    )

    # 4. Merge leads back onto all calls via (gvkey, fyearq_int)
    df["_row_id"] = np.arange(len(df))
    df["fyearq_int"] = np.floor(pd.to_numeric(df["fyearq"], errors="coerce")).astype(
        "Int64"
    )

    merged = df.merge(lookup, on=["gvkey", "fyearq_int"], how="left")
    merged = merged.sort_values("_row_id").drop(
        columns=["_row_id", "fyearq_int", "start_date_dt"]
    )

    n_stab = merged["div_stability_lead"].notna().sum()
    n_flex = merged["payout_flexibility_lead"].notna().sum()
    print(f"  Valid div_stability_lead:     {n_stab:,} / {len(merged):,}")
    print(f"  Valid payout_flexibility_lead: {n_flex:,} / {len(merged):,}")

    return merged


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Building H3 Panel")
    print("=" * 60)

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        "manager_qa_uncertainty": ManagerQAUncertaintyBuilder(
            var_config.get("manager_qa_uncertainty", {})
        ),
        "ceo_qa_uncertainty": CEOQAUncertaintyBuilder(
            var_config.get("ceo_qa_uncertainty", {})
        ),
        "manager_qa_weak_modal": ManagerQAWeakModalBuilder(
            var_config.get("manager_qa_weak_modal", {})
        ),
        "ceo_qa_weak_modal": CEOQAWeakModalBuilder(
            var_config.get("ceo_qa_weak_modal", {})
        ),
        "manager_pres_uncertainty": ManagerPresUncertaintyBuilder(
            var_config.get("manager_pres_uncertainty", {})
        ),
        "ceo_pres_uncertainty": CEOPresUncertaintyBuilder(
            var_config.get("ceo_pres_uncertainty", {})
        ),
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(
            var_config.get("analyst_qa_uncertainty", {})
        ),
        "negative_sentiment": NegativeSentimentBuilder(
            var_config.get("negative_sentiment", {})
        ),
        "size": SizeBuilder(var_config.get("size", {})),
        "lev": LevBuilder(var_config.get("lev", {})),
        "roa": ROABuilder(var_config.get("roa", {})),
        "tobins_q": TobinsQBuilder(var_config.get("tobins_q", {})),
        "cash_holdings": CashHoldingsBuilder(var_config.get("cash_holdings", {})),
        "div_stability": DivStabilityBuilder(var_config.get("div_stability", {})),
        "payout_flexibility": PayoutFlexibilityBuilder(
            var_config.get("payout_flexibility", {})
        ),
        "earnings_volatility": EarningsVolatilityBuilder(
            var_config.get("earnings_volatility", {})
        ),
        "fcf_growth": FCFGrowthBuilder(var_config.get("fcf_growth", {})),
        "firm_maturity": FirmMaturityBuilder(var_config.get("firm_maturity", {})),
        "is_div_payer_5yr": IsDivPayer5yrBuilder(
            var_config.get("is_div_payer_5yr", {})
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

    panel = create_lead_variables(panel, root_path)

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    return panel


def save_outputs(panel: pd.DataFrame, stats: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "h3_payout_policy_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: h3_payout_policy_panel.parquet ({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_df.to_csv(out_dir / "summary_stats.csv", index=False)


def generate_report(
    panel: pd.DataFrame, stats: Dict[str, Any], out_dir: Path, duration: float
) -> None:
    n_div_payer = panel["is_div_payer_5yr"].sum()
    report_lines = [
        "# Stage 3: H3 Payout Policy Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary",
        f"- **Rows:** {len(panel):,}",
        f"- **Columns:** {len(panel.columns)}",
        f"- **Dividend Payers (5-year rolling):** {int(n_div_payer):,} calls",
        "",
    ]
    report_path = out_dir / "report_step3_h3.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h3_payout_policy_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h3_payout_policy" / timestamp

    config = get_config(root / "config" / "project.yaml")
    var_config = load_variable_config(root / "config" / "variables.yaml")

    if year_start is None:
        year_start = config.data.year_start
    if year_end is None:
        year_end = config.data.year_end
    years = range(year_start, year_end + 1)

    print("=" * 80)
    print("STAGE 3: Build H3 Payout Policy Panel")
    print("=" * 80)

    panel = build_panel(root, years, var_config, stats)
    save_outputs(panel, stats, out_dir)

    duration = (datetime.now() - start_time).total_seconds()
    generate_report(panel, stats, out_dir, duration)

    print(f"\nCOMPLETE in {duration:.1f}s")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        sys.exit(0)
    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
