#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H13.2 Employment Growth Panel
================================================================================
ID: variables/build_h13_2_employment_panel
Description: Build FIRM-YEAR panel for H13.2: Language Uncertainty predicts
             Future Employment Growth.

    H13.2 Hypothesis:
        EmploymentGrowth_lead_{i} = β0 + β1·Avg_CEO_Pres_Uncertainty_{i,t}
                                   + γ'·Controls_{i,t}
                                   + FirmFE_i + YearFE_t + ε

    Key coefficient: β1 (one-tailed test)
        β1 < 0 (sig): Higher CEO presentation uncertainty → lower employment growth
        β1 ≈ 0: Uncertainty language does NOT predict employment growth

Unit of observation: firm-fiscal-year (gvkey, fyearq).
DV: EmploymentGrowth_lead = ln(EMP_{t+1}) - ln(EMP_t) from Compustat empq (Q4).

Step 1: Load manifest + CEO_Pres_Uncertainty_pct (single IV).
Step 2: Load EmploymentGrowth_lead (from EmploymentGrowthLeadBuilder) and controls.
Step 3: Aggregate call-level uncertainty to firm-year level:
            Avg_CEO_Pres_Uncertainty_pct = mean per (gvkey, fyearq)
            EmploymentGrowth_lead, controls = last non-missing per (gvkey, fyearq)
Step 4: Assign industry sample, save firm-year panel.

Note: EmploymentGrowth_lead is already computed in EmploymentGrowthLeadBuilder
      as ln(EMP_{t+1}) - ln(EMP_t), so no need to shift again.
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
    SizeBuilder,
    LevBuilder,
    ROABuilder,
    TobinsQBuilder,
    CashHoldingsBuilder,
    DividendPayerBuilder,
    OCFVolatilityBuilder,
    CEOPresUncertaintyBuilder,
    EmploymentGrowthLeadBuilder,
    stats_list_to_dataframe,
)


# ---------------------------------------------------------------------------
# Single uncertainty measure to average across calls within firm-year
# ---------------------------------------------------------------------------
UNCERTAINTY_MEASURES: List[str] = [
    "CEO_Pres_Uncertainty_pct",  # Only this one for H13.2
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H13.2 Employment Growth Panel",
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

    For uncertainty measure: take the MEAN across all calls within each
    (gvkey, fyearq). This gives the average uncertainty in the firm's
    earnings calls during the year.

    For financial variables (EmploymentGrowth_lead, controls, ff12_code):
    take the last non-missing value per (gvkey, fyearq) — these are
    constant within a firm-year from the Compustat merge.

    Returns a DataFrame indexed on (gvkey, fyearq).
    """
    if "fyearq" not in panel.columns:
        raise ValueError("Panel must have a 'fyearq' column for firm-year aggregation.")

    # Financial controls: take last value per firm-year (constant within FY)
    financial_cols = [
        "EmploymentGrowth_lead",
        "Size",
        "Lev",
        "ROA",
        "TobinsQ",
        "CashHoldings",
        "DividendPayer",
        "OCF_Volatility",
        "ff12_code",
    ]
    existing_financial = [c for c in financial_cols if c in panel.columns]

    # Uncertainty measure: take mean per firm-year
    existing_uncertainty = [c for c in UNCERTAINTY_MEASURES if c in panel.columns]

    # Sort by (gvkey, fyearq, start_date) so "last" = last call in the FY
    df = panel.sort_values(["gvkey", "fyearq", "start_date"], na_position="last")

    # Financial: last non-NaN per (gvkey, fyearq)
    firm_year_financial = (
        df.groupby(["gvkey", "fyearq"])[existing_financial].last().reset_index()
    )

    # Uncertainty: mean across all calls in the firm-year
    if existing_uncertainty:
        firm_year_uncertainty = (
            df.groupby(["gvkey", "fyearq"])[existing_uncertainty].mean().reset_index()
        )
        # Rename uncertainty column to indicate firm-year averaging
        rename_map = {col: f"Avg_{col}" for col in existing_uncertainty}
        firm_year_uncertainty = firm_year_uncertainty.rename(columns=rename_map)

        # Merge financial + uncertainty
        firm_year = firm_year_financial.merge(
            firm_year_uncertainty, on=["gvkey", "fyearq"], how="left"
        )
    else:
        firm_year = firm_year_financial

    # Also count calls per firm-year (useful for diagnostics / min-calls filter)
    call_counts = df.groupby(["gvkey", "fyearq"]).size().reset_index(name="n_calls")
    firm_year = firm_year.merge(call_counts, on=["gvkey", "fyearq"], how="left")

    return firm_year


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
    print("Building H13.2 Employment Growth Panel")
    print("=" * 60)

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        # Primary IV (call-level, to be averaged to firm-year)
        "ceo_pres_uncertainty": CEOPresUncertaintyBuilder(
            var_config.get("ceo_pres_uncertainty", {})
        ),
        # DV source (already computed as ln(EMP_{t+1}) - ln(EMP_t))
        "employment_growth_lead": EmploymentGrowthLeadBuilder({}),
        # Financial controls
        "size": SizeBuilder(var_config.get("size", {})),
        "lev": LevBuilder(var_config.get("lev", {})),
        "roa": ROABuilder(var_config.get("roa", {})),
        "tobins_q": TobinsQBuilder(var_config.get("tobins_q", {})),
        "cash_holdings": CashHoldingsBuilder(var_config.get("cash_holdings", {})),
        "dividend_payer": DividendPayerBuilder(var_config.get("dividend_payer", {})),
        "ocf_volatility": OCFVolatilityBuilder(var_config.get("ocf_volatility", {})),
        # Note: NO CapexAt in H13.2 controls
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

    # Coerce start_date to datetime64 before fyearq attachment and aggregation.
    panel["start_date"] = pd.to_datetime(panel["start_date"], errors="coerce")
    panel = attach_fyearq(panel, root_path)

    # Aggregate to firm-year
    print("\n  Aggregating to firm-year level...")
    print("  Uncertainty measure: averaged across calls per (gvkey, fyearq)")
    print("  Financial variables: last non-missing per (gvkey, fyearq)")
    firm_year = aggregate_to_firm_year(panel)
    print(f"  Firm-year observations: {len(firm_year):,}")

    # Diagnostics: call counts
    if "n_calls" in firm_year.columns:
        print(
            f"  Calls per firm-year: "
            f"mean={firm_year['n_calls'].mean():.1f}, "
            f"median={firm_year['n_calls'].median():.0f}, "
            f"min={firm_year['n_calls'].min():.0f}, "
            f"max={firm_year['n_calls'].max():.0f}"
        )

    # DV already computed in EmploymentGrowthLeadBuilder
    n_dv = firm_year["EmploymentGrowth_lead"].notna().sum()
    print(f"  EmploymentGrowth_lead (valid): {n_dv:,} / {len(firm_year):,}")

    # Assign industry sample (Main/Finance/Utility) for filtering
    if "ff12_code" in firm_year.columns:
        firm_year["sample"] = assign_industry_sample(firm_year["ff12_code"])

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
    panel_path = out_dir / "h13_2_employment_panel.parquet"
    firm_year.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: h13_2_employment_panel.parquet "
        f"({len(firm_year):,} rows, {len(firm_year.columns)} columns)"
    )
    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

    # Generate run manifest for reproducibility
    manifest_input = (
        root
        / "outputs"
        / "1.4_AssembleManifest"
        / "latest"
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
    n_dv = (
        firm_year["EmploymentGrowth_lead"].notna().sum()
        if "EmploymentGrowth_lead" in firm_year.columns
        else 0
    )
    avg_unc_cols = [c for c in firm_year.columns if c.startswith("Avg_")]
    report_lines = [
        "# Stage 3: H13.2 Employment Growth Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary (Firm-Year Level)",
        f"- **Rows (firm-years):** {len(firm_year):,}",
        f"- **Columns:** {len(firm_year.columns)}",
        f"- **EmploymentGrowth_lead (DV, valid):** {n_dv:,}",
        f"- **Uncertainty measure (averaged):** {len(avg_unc_cols)}",
        "",
        "## Uncertainty Measure Coverage",
    ]
    for col in avg_unc_cols:
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

    # Sample distribution
    if "sample" in firm_year.columns:
        report_lines += [
            "## Sample Distribution",
            "",
            "| Sample | Firm-Years | With Valid DV |",
            "|--------|-----------:|---------------:|",
        ]
        for sample in ["Main", "Finance", "Utility"]:
            n = (firm_year["sample"] == sample).sum()
            n_dv_s = firm_year.loc[firm_year["sample"] == sample, "EmploymentGrowth_lead"].notna().sum()
            report_lines.append(f"| {sample} | {n:,} | {n_dv_s:,} |")
        report_lines.append("")

    with open(out_dir / "report_step3_h13_2.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h13_2_employment_panel",
        "timestamp": timestamp,
        "variable_stats": [],
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h13_2_employment" / timestamp

    # Setup logging
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H13_2_Employment",
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
    print("STAGE 3: Build H13.2 Employment Growth Panel (firm-year level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Years:     {year_start}-{year_end}")
    print(f"Unit of observation: firm-fiscal-year (gvkey, fyearq)")
    print(f"DV: EmploymentGrowth_lead = ln(EMP_t+1) - ln(EMP_t)")
    print(f"IV: Avg_CEO_Pres_Uncertainty_pct (mean across calls in firm-year)")

    # Build panel
    firm_year = build_panel(root, years, var_config, stats)

    # Save outputs
    save_outputs(firm_year, stats, out_dir, root, timestamp)

    # Generate report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(firm_year, stats, out_dir, duration)

    # Summary
    print("\n" + "=" * 80)
    print("H13.2 Employment Growth Panel build complete.")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Firm-year observations: {len(firm_year):,}")
    print(f"With valid EmploymentGrowth_lead: {firm_year['EmploymentGrowth_lead'].notna().sum():,}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("DRY-RUN mode -- validating inputs only")
        print("DRY-RUN complete.")
        sys.exit(0)

    sys.exit(main(args.year_start, args.year_end))
