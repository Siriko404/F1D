#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H12 Payout Ratio Panel
================================================================================
ID: variables/build_h12_div_intensity_panel
Description: Build FIRM-YEAR panel for H12: Speech Uncertainty predicts
             Payout Ratio (DVC / IB, per Attig et al.).

    H12 Hypothesis:
        PayoutRatio_{i,t+1} = β0 + Σ β_k·Avg_Uncertainty_k_{i,t}
                              + γ'·Controls_{i,t}
                              + FE + ε

    4 Key IVs (all simultaneous):
        CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct,
        Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct

    Key coefficient: β_k (one-tailed test)
        β_k < 0 (sig): Higher uncertainty → lower payout
        β_k ≈ 0: No predictive relationship

Unit of observation: firm-fiscal-year (gvkey, fyearq_int).
DV: PayoutRatio = dvy / iby (Attig et al.), PayoutRatio_lead = t+1.

Step 1: Load manifest + 4 call-level IVs (uncertainty).
Step 2: Load PayoutRatio (Compustat engine) and financial controls.
Step 3: Attach fyearq, aggregate call-level to firm-year:
            IVs = mean across calls per (gvkey, fyearq)
            Financials = last non-missing per (gvkey, fyearq)
Step 4: Create PayoutRatio_lead = PayoutRatio_{t+1}.
Step 5: Save firm-year panel.

Aggregation rule (literature-backed):
    Brochet, Loumioti & Serafeim: "firm-year level by averaging all ...
    measures across quarterly conference calls."
    Hassan, Hollander, van Lent & Tahoun (QJE): "at the annual frequency,
    we take an arithmetic mean across all transcripts of a given firm and year."
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
from f1d.shared.variables.panel_utils import attach_fyearq, assign_industry_sample
from f1d.shared.variables import (
    ManifestFieldsBuilder,
    # Key IVs (call-level, to be averaged to firm-year)
    ManagerQAUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    # DV source
    PayoutRatioBuilder,
    # Base controls
    SizeBuilder,
    BookLevBuilder,
    ROABuilder,
    TobinsQBuilder,
    CashHoldingsBuilder,
    CapexIntensityBuilder,
    OCFVolatilityBuilder,
    # Extended controls
    SalesGrowthBuilder,
    RDIntensityBuilder,
    CashFlowBuilder,
    VolatilityBuilder,
    stats_list_to_dataframe,
)


# ---------------------------------------------------------------------------
# Call-level IVs to average across calls within firm-year
# ---------------------------------------------------------------------------
CALL_LEVEL_IVS: List[str] = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H12 Payout Ratio Panel (firm-year)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helper: aggregate call-level panel → firm-year panel
# ---------------------------------------------------------------------------


def aggregate_to_firm_year(panel: pd.DataFrame) -> pd.DataFrame:
    """Collapse call-level panel to firm-year (gvkey, fyearq).

    For IVs (uncertainty): take the MEAN across all
    calls within each (gvkey, fyearq). Rename with Avg_ prefix.

    For financial variables (PayoutRatio, controls, ff12_code): take the
    last non-missing value per (gvkey, fyearq) — these are constant within
    a firm-year from the Compustat merge.

    For Volatility: take last value per firm-year (CRSP-based, varies
    across calls within firm-year; last call's value is most recent).
    """
    if "fyearq" not in panel.columns:
        raise ValueError("Panel must have a 'fyearq' column for firm-year aggregation.")

    # Financial controls + DV: take last value per firm-year (constant within FY)
    financial_cols = [
        "PayoutRatio",
        "Size",
        "BookLev",
        "ROA",
        "TobinsQ",
        "CashHoldings",
        "CapexAt",
        "OCF_Volatility",
        "SalesGrowth",
        "RD_Intensity",
        "CashFlow",
        "Volatility",
        "ff12_code",
    ]
    existing_financial = [c for c in financial_cols if c in panel.columns]

    # IVs: take mean per firm-year
    existing_ivs = [c for c in CALL_LEVEL_IVS if c in panel.columns]

    # Sort by (gvkey, fyearq, start_date) so "last" = last call in the FY
    df = panel.sort_values(["gvkey", "fyearq", "start_date"], na_position="last")

    # Financial: last non-NaN per (gvkey, fyearq)
    firm_year_financial = (
        df.groupby(["gvkey", "fyearq"])[existing_financial].last().reset_index()
    )

    # IVs: mean across all calls in the firm-year, with Avg_ prefix
    if existing_ivs:
        firm_year_ivs = (
            df.groupby(["gvkey", "fyearq"])[existing_ivs].mean().reset_index()
        )
        rename_map = {col: f"Avg_{col}" for col in existing_ivs}
        firm_year_ivs = firm_year_ivs.rename(columns=rename_map)

        firm_year = firm_year_financial.merge(
            firm_year_ivs, on=["gvkey", "fyearq"], how="left"
        )
    else:
        firm_year = firm_year_financial

    # Count calls per firm-year (diagnostics)
    call_counts = df.groupby(["gvkey", "fyearq"]).size().reset_index(name="n_calls")
    firm_year = firm_year.merge(call_counts, on=["gvkey", "fyearq"], how="left")

    return firm_year


def create_lead_payout_ratio(firm_year: pd.DataFrame) -> pd.DataFrame:
    """Create PayoutRatio_lead = PayoutRatio shifted one FY forward.

    - PayoutRatio_lead_t = PayoutRatio_{t+1} (DV: next-year payout ratio)
    - Gap years (non-consecutive fyearq) → NaN (no survivorship selection)
    """
    df = firm_year.copy()
    df = df.sort_values(["gvkey", "fyearq"]).reset_index(drop=True)
    df["next_fyearq"] = df.groupby("gvkey")["fyearq"].shift(-1)
    df["PayoutRatio_next"] = df.groupby("gvkey")["PayoutRatio"].shift(-1)

    # Null out non-consecutive years (gap > 1)
    fyearq_int = df["fyearq"].astype("Int64")
    next_fyearq_int = df["next_fyearq"].astype("Int64")
    is_consecutive = (next_fyearq_int - fyearq_int) == 1
    df.loc[~is_consecutive, "PayoutRatio_next"] = np.nan

    df = df.rename(columns={"PayoutRatio_next": "PayoutRatio_lead"})
    df = df.drop(columns=["next_fyearq"], errors="ignore")
    return df


def create_lag_payout_ratio(firm_year: pd.DataFrame) -> pd.DataFrame:
    """Create PayoutRatio_lag = PayoutRatio shifted one FY backward.

    - PayoutRatio_lag_t = PayoutRatio_{t-1} (previous-year payout ratio)
    - Gap years (non-consecutive fyearq) → NaN
    """
    df = firm_year.copy()
    df = df.sort_values(["gvkey", "fyearq"]).reset_index(drop=True)
    df["prev_fyearq"] = df.groupby("gvkey")["fyearq"].shift(1)
    df["PayoutRatio_prev"] = df.groupby("gvkey")["PayoutRatio"].shift(1)

    fyearq_int = df["fyearq"].astype("Int64")
    prev_fyearq_int = df["prev_fyearq"].astype("Int64")
    is_consecutive = (fyearq_int - prev_fyearq_int) == 1
    df.loc[~is_consecutive, "PayoutRatio_prev"] = np.nan

    df = df.rename(columns={"PayoutRatio_prev": "PayoutRatio_lag"})
    df = df.drop(columns=["prev_fyearq"], errors="ignore")
    return df


# ---------------------------------------------------------------------------
# Main panel builder
# ---------------------------------------------------------------------------


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Building H12 Payout Ratio Panel")
    print("=" * 60)

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        # Key IVs (call-level, to be averaged to firm-year)
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
        # DV source
        "payout_ratio": PayoutRatioBuilder(var_config.get("payout_ratio", {})),
        # Base controls
        "size": SizeBuilder(var_config.get("size", {})),
        "lev": BookLevBuilder(var_config.get("lev", {})),
        "roa": ROABuilder(var_config.get("roa", {})),
        "tobins_q": TobinsQBuilder(var_config.get("tobins_q", {})),
        "cash_holdings": CashHoldingsBuilder(var_config.get("cash_holdings", {})),
        "capex_at": CapexIntensityBuilder(var_config.get("capex_intensity", {})),
        "ocf_volatility": OCFVolatilityBuilder(var_config.get("ocf_volatility", {})),
        # Extended controls
        "sales_growth": SalesGrowthBuilder(var_config.get("sales_growth", {})),
        "rd_intensity": RDIntensityBuilder(var_config.get("rd_intensity", {})),
        "cash_flow": CashFlowBuilder(var_config.get("cash_flow", {})),
        "volatility": VolatilityBuilder(var_config.get("volatility", {})),
    }

    all_results = {}
    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    # Assemble call-level panel
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
            raise ValueError(f"Merge '{name}' changed rows: {before_len} → {after_len}")
        print(f"  After {name} merge: {after_len:,} rows (delta: {delta:+d})")

    # Coerce start_date to datetime64
    panel["start_date"] = pd.to_datetime(panel["start_date"], errors="coerce")
    panel = attach_fyearq(panel, root_path)

    # Aggregate to firm-year
    print("\n  Aggregating to firm-year level...")
    print("  IVs (uncertainty): averaged across calls per (gvkey, fyearq)")
    print("  Financial variables: last non-missing per (gvkey, fyearq)")
    firm_year = aggregate_to_firm_year(panel)
    print(f"  Firm-year observations: {len(firm_year):,}")

    # Create fyearq_int for regression time index
    firm_year["fyearq_int"] = np.floor(
        pd.to_numeric(firm_year["fyearq"], errors="coerce")
    ).astype("Int64")

    # Add year column for summary stats compatibility
    firm_year["year"] = firm_year["fyearq_int"]

    # Diagnostics: call counts
    if "n_calls" in firm_year.columns:
        print(
            f"  Calls per firm-year: "
            f"mean={firm_year['n_calls'].mean():.1f}, "
            f"median={firm_year['n_calls'].median():.0f}, "
            f"min={firm_year['n_calls'].min():.0f}, "
            f"max={firm_year['n_calls'].max():.0f}"
        )

    # Create forward DV
    firm_year = create_lead_payout_ratio(firm_year)
    n_dv = firm_year["PayoutRatio_lead"].notna().sum()
    n_dv_t = firm_year["PayoutRatio"].notna().sum()
    print(f"  PayoutRatio (valid): {n_dv_t:,} / {len(firm_year):,}")
    print(f"  PayoutRatio_lead (valid): {n_dv:,} / {len(firm_year):,}")

    # Assign industry sample
    if "ff12_code" in firm_year.columns:
        firm_year["sample"] = assign_industry_sample(firm_year["ff12_code"])

    # Create lagged DV
    firm_year = create_lag_payout_ratio(firm_year)
    n_lag = firm_year["PayoutRatio_lag"].notna().sum()
    print(f"  PayoutRatio_lag (valid): {n_lag:,} / {len(firm_year):,}")

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    return firm_year


def save_outputs(
    firm_year: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
    root: Path,
    timestamp: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "h12_payout_panel.parquet"
    firm_year.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: h12_payout_panel.parquet "
        f"({len(firm_year):,} rows, {len(firm_year.columns)} columns)"
    )
    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

    manifest_input = (
        root / "outputs" / "1.4_AssembleManifest" / "latest"
        / "master_sample_manifest.parquet"
    )
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


def generate_report(
    firm_year: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
    duration: float,
) -> None:
    n_dv_lead = (
        firm_year["PayoutRatio_lead"].notna().sum()
        if "PayoutRatio_lead" in firm_year.columns
        else 0
    )
    n_dv = (
        firm_year["PayoutRatio"].notna().sum()
        if "PayoutRatio" in firm_year.columns
        else 0
    )
    avg_cols = [c for c in firm_year.columns if c.startswith("Avg_")]
    report_lines = [
        "# Stage 3: H12 Payout Ratio Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**DV:** PayoutRatio = DVC / IB (Attig et al.)",
        "",
        "## Panel Summary (Firm-Year Level)",
        f"- **Rows (firm-years):** {len(firm_year):,}",
        f"- **Columns:** {len(firm_year.columns)}",
        f"- **PayoutRatio (DV, t, valid):** {n_dv:,}",
        f"- **PayoutRatio_lead (DV, t+1, valid):** {n_dv_lead:,}",
        f"- **IVs (averaged):** {len(avg_cols)}",
        "",
        "## IV Coverage (firm-year averages)",
    ]
    for col in avg_cols:
        n_valid = firm_year[col].notna().sum()
        report_lines.append(f"- {col}: {n_valid:,} / {len(firm_year):,}")
    report_lines.append("")

    if "n_calls" in firm_year.columns:
        report_lines += [
            "## Calls Per Firm-Year",
            f"- Mean:   {firm_year['n_calls'].mean():.1f}",
            f"- Median: {firm_year['n_calls'].median():.0f}",
            f"- Min:    {firm_year['n_calls'].min():.0f}",
            f"- Max:    {firm_year['n_calls'].max():.0f}",
            "",
        ]

    with open(out_dir / "report_step3_h12.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h12_payout_panel",
        "timestamp": timestamp,
        "variable_stats": [],
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h12_payout" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H12_Payout",
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
    print("STAGE 3: Build H12 Payout Ratio Panel (Attig et al.)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"DV:        PayoutRatio = DVC / IB (NaN when IB <= 0)")
    print(f"IVs:       4 call-level measures -> firm-year mean")

    firm_year = build_panel(root, years, var_config, stats)
    save_outputs(firm_year, stats, out_dir, root, timestamp)

    duration = (datetime.now() - start_time).total_seconds()
    generate_report(firm_year, stats, out_dir, duration)

    print(f"\nCOMPLETE in {duration:.1f}s")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        sys.exit(0)
    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
