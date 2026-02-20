#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H1 Cash Holdings Panel
================================================================================
ID: variables/build_h1_cash_holdings_panel
Description: Build firm-year panel for H1 Cash Holdings hypothesis test.

    Step 1: Load manifest + all call-level variables (linguistic + financial).
    Step 2: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 3: Aggregate call-level panel to firm-year level (mean of all variables
            within gvkey × fiscal_year; retain n_calls count).
    Step 4: Create CashHoldings_lead = next-year CashHoldings per firm (shift -1).
    Step 5: Drop firms' last year (no lead available).
    Step 6: Assign industry sample (Main / Finance / Utility).
    Step 7: Save firm-year panel.

Inputs (all raw — no reuse of prior panels):
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet  (Compustat)
    - inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet        (CRSP daily)
    - inputs/tr_ibes/tr_ibes.parquet                       (IBES)
    - inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet   (CCM linktable)

Outputs:
    - outputs/variables/h1_cash_holdings/{timestamp}/h1_cash_holdings_panel.parquet
    - outputs/variables/h1_cash_holdings/{timestamp}/summary_stats.csv
    - outputs/variables/h1_cash_holdings/{timestamp}/report_step3_h1.md

Panel is firm-year level (gvkey × fiscal_year), NOT call-level.

Author: Thesis Author
Date: 2026-02-19
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
from f1d.shared.variables import (
    # Linguistic uncertainty
    ManagerQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    # Weak modal (H1 primary regressors)
    ManagerQAWeakModalBuilder,
    CEOQAWeakModalBuilder,
    ManagerPresWeakModalBuilder,
    CEOPresWeakModalBuilder,
    # Financial controls (Compustat engine)
    CashHoldingsBuilder,
    LevBuilder,
    SizeBuilder,
    TobinsQBuilder,
    ROABuilder,
    CapexIntensityBuilder,
    DividendPayerBuilder,
    OCFVolatilityBuilder,
    CurrentRatioBuilder,
    # Manifest
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H1 Cash Holdings Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate inputs without executing"
    )
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def assign_industry_sample(ff12_code: pd.Series) -> pd.Series:
    """Assign industry sample based on FF12 code using np.select (not deprecated boolean indexing)."""
    conditions = [ff12_code == 11, ff12_code == 8]
    choices = ["Finance", "Utility"]
    return pd.Series(
        np.select(conditions, choices, default="Main"),
        index=ff12_code.index,
        dtype=object,
    )


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
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(
            var_config.get("analyst_qa_uncertainty", {})
        ),
        "negative_sentiment": NegativeSentimentBuilder(
            var_config.get("negative_sentiment", {})
        ),
        # Weak modal
        "manager_qa_weak_modal": ManagerQAWeakModalBuilder(
            var_config.get("manager_qa_weak_modal", {})
        ),
        "ceo_qa_weak_modal": CEOQAWeakModalBuilder(
            var_config.get("ceo_qa_weak_modal", {})
        ),
        "manager_pres_weak_modal": ManagerPresWeakModalBuilder(
            var_config.get("manager_pres_weak_modal", {})
        ),
        "ceo_pres_weak_modal": CEOPresWeakModalBuilder(
            var_config.get("ceo_pres_weak_modal", {})
        ),
        # Financial controls — CompustatEngine is a singleton; all 9 share one load
        "cash_holdings": CashHoldingsBuilder({}),
        "lev": LevBuilder({}),
        "size": SizeBuilder({}),
        "tobins_q": TobinsQBuilder({}),
        "roa": ROABuilder({}),
        "capex_intensity": CapexIntensityBuilder({}),
        "dividend_payer": DividendPayerBuilder({}),
        "ocf_volatility": OCFVolatilityBuilder({}),
        "current_ratio": CurrentRatioBuilder({}),
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
            print(f"  WARNING: {name} returned no usable columns — skipping merge")
            continue

        # Assert builder output unique on file_name
        if data["file_name"].duplicated().any():
            n_dups = data["file_name"].duplicated().sum()
            raise ValueError(
                f"Builder '{name}' returned {n_dups} duplicate file_name rows. "
                "Merge aborted to prevent fan-out."
            )

        # Drop conflicting columns (except file_name) to prevent _x/_y blowup
        conflicting = [
            c for c in data.columns if c in panel.columns and c != "file_name"
        ]
        if conflicting:
            print(
                f"  WARNING: {name} has overlapping columns {conflicting} — dropping from builder data"
            )
            data = data.drop(columns=conflicting)

        before_len = len(panel)
        panel = panel.merge(data, on="file_name", how="left")
        after_len = len(panel)
        if after_len != before_len:
            raise ValueError(
                f"Merge of '{name}' changed row count {before_len} → {after_len}. "
                "Duplicate file_name detected in builder output post-merge."
            )
        print(f"  After {name} merge: {after_len:,} rows (delta: +0)")

    # Assert ff12_code present (hard error)
    if "ff12_code" not in panel.columns:
        raise ValueError(
            "ff12_code column missing from panel after manifest merge. "
            "Cannot assign industry sample. Check ManifestFieldsBuilder output."
        )

    # Add year column from start_date
    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Collect summary stats
    stats_list = []
    for name, result in all_results.items():
        stats_list.append(result.stats)
    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def aggregate_to_firm_year(panel: pd.DataFrame) -> pd.DataFrame:
    """Aggregate call-level panel to firm-year level.

    Groups by (gvkey, year) and takes the mean of all numeric variables.
    Counts n_calls per firm-year.
    Retains ff12_code via mode (should be constant within firm).

    Returns:
        Firm-year DataFrame with gvkey, fiscal_year, n_calls, ff12_code,
        and all variable columns averaged.
    """
    print("\n" + "=" * 60)
    print("Aggregating call-level -> firm-year")
    print("=" * 60)

    if "year" not in panel.columns:
        raise ValueError("'year' column missing — cannot aggregate to firm-year.")

    # Rename year → fiscal_year for clarity
    panel = panel.rename(columns={"year": "fiscal_year"})

    # Columns to aggregate as mean
    linguistic_cols = [
        "Manager_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Weak_Modal_pct",
        "CEO_Pres_Weak_Modal_pct",
    ]
    financial_cols = [
        "CashHoldings",
        "Lev",
        "Size",
        "TobinsQ",
        "ROA",
        "CapexAt",
        "DividendPayer",
        "OCF_Volatility",
        "CurrentRatio",
    ]

    # Only aggregate columns that exist
    all_agg_cols = [c for c in linguistic_cols + financial_cols if c in panel.columns]

    agg_dict = {col: "mean" for col in all_agg_cols}
    # ff12_code: take first (constant within firm)
    if "ff12_code" in panel.columns:
        agg_dict["ff12_code"] = "first"

    firm_year = panel.groupby(["gvkey", "fiscal_year"], as_index=False).agg(
        {**agg_dict, "file_name": "count"}
    )
    firm_year = firm_year.rename(columns={"file_name": "n_calls"})

    print(f"  Call-level: {len(panel):,} rows")
    print(f"  Firm-year:  {len(firm_year):,} rows")
    print(f"  Unique firms: {firm_year['gvkey'].nunique():,}")
    print(
        f"  Year range: {int(firm_year['fiscal_year'].min())}–{int(firm_year['fiscal_year'].max())}"
    )
    print(f"  Mean calls per firm-year: {firm_year['n_calls'].mean():.2f}")

    return firm_year


def create_lead_variable(firm_year: pd.DataFrame) -> pd.DataFrame:
    """Create CashHoldings_lead = next-year CashHoldings per firm.

    Sorts by gvkey, fiscal_year. Shifts CashHoldings within gvkey by -1.
    Drops the last year per firm (no lead available).
    """
    print("\n  Creating CashHoldings_lead (shift -1 within gvkey)...")
    firm_year = firm_year.sort_values(["gvkey", "fiscal_year"]).copy()
    firm_year["CashHoldings_lead"] = firm_year.groupby("gvkey")["CashHoldings"].shift(
        -1
    )

    before = len(firm_year)
    firm_year = firm_year.dropna(subset=["CashHoldings_lead"])
    after = len(firm_year)
    print(f"  Dropped {before - after:,} obs (last year per firm, no lead)")
    print(f"  Final firm-year obs: {after:,}")

    return firm_year


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h1_cash_holdings_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h1_cash_holdings" / timestamp

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
    print("STAGE 3: Build H1 Cash Holdings Panel")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Years:     {year_start}–{year_end}")

    # Step 1-2: Build call-level panel
    call_panel = build_call_level_panel(root, years, var_config, stats)

    # Step 3: Aggregate to firm-year
    firm_year = aggregate_to_firm_year(call_panel)

    # Step 4-5: Create lead variable + drop last year
    firm_year = create_lead_variable(firm_year)

    # Step 6: Assign sample
    if "ff12_code" not in firm_year.columns:
        raise ValueError(
            "ff12_code missing from firm-year panel. Cannot assign sample."
        )
    firm_year["sample"] = assign_industry_sample(firm_year["ff12_code"])

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (firm_year["sample"] == sample).sum()
        print(f"    {sample}: {n:,} firm-years")

    # Step 7: Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h1_cash_holdings_panel.parquet"
    firm_year.to_parquet(panel_path, index=False)
    print(
        f"  Saved: h1_cash_holdings_panel.parquet "
        f"({len(firm_year):,} rows, {len(firm_year.columns)} columns)"
    )

    # Summary stats CSV
    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    report_lines = [
        "# Stage 3: H1 Cash Holdings Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary (firm-year level)",
        "",
        f"- **Total firm-year observations:** {len(firm_year):,}",
        f"- **Unique firms:** {firm_year['gvkey'].nunique():,}",
        f"- **Year range:** {int(firm_year['fiscal_year'].min())}–{int(firm_year['fiscal_year'].max())}",
        f"- **Total columns:** {len(firm_year.columns)}",
        "",
        "### Sample Distribution",
        "",
        "| Sample | N Firm-Years | % |",
        "|--------|-------------|---|",
    ]
    for sample in ["Main", "Finance", "Utility"]:
        n = (firm_year["sample"] == sample).sum()
        pct = 100.0 * n / len(firm_year) if len(firm_year) > 0 else 0
        report_lines.append(f"| {sample} | {n:,} | {pct:.1f}% |")

    report_lines += [
        "",
        "### Key Variable Coverage",
        "",
        "| Variable | N non-missing | Mean | Std |",
        "|----------|--------------|------|-----|",
    ]
    for col in [
        "CashHoldings",
        "CashHoldings_lead",
        "Lev",
        "Size",
        "TobinsQ",
        "ROA",
        "CapexAt",
        "DividendPayer",
        "OCF_Volatility",
        "CurrentRatio",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
    ]:
        if col in firm_year.columns:
            n_valid = firm_year[col].notna().sum()
            mean = firm_year[col].mean()
            std = firm_year[col].std()
            report_lines.append(f"| {col} | {n_valid:,} | {mean:.4f} | {std:.4f} |")

    report_lines.append("")
    report_path = out_dir / "report_step3_h1.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  Saved: report_step3_h1.md")

    # Final summary
    stats["timing"]["duration_seconds"] = round(duration, 2)
    stats["panel"]["n_rows"] = len(firm_year)
    stats["panel"]["n_columns"] = len(firm_year.columns)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output:   {out_dir}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
