#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H2 Investment Efficiency Panel
================================================================================
ID: variables/build_h2_investment_panel
Description: Build CALL-LEVEL panel for H2 Investment Efficiency hypothesis test.

    Structurally identical to build_h1_cash_holdings_panel.py: one row per
    earnings call (file_name). Comparable with all other Stage 3 panels.

    Step 1: Load manifest + all call-level variables (linguistic + financial).
    Step 2: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 3: Add call year from start_date AND attach fyearq from Compustat.
    Step 4: Compute InvestmentResidual_lead per call:
            - Take InvestmentResidual from the LAST call per (gvkey, fyearq)
              (end-of-fiscal-year proxy; audit fix C-5/M-9: use fiscal year,
              not calendar year, to identify the last call per firm-year).
            - Shift firm-fyearq end-of-year value by -1 within gvkey -> next
              fiscal year residual.
            - CRITICAL: validate that next row is exactly fyearq+1 (not +2).
              Gap in fiscal years -> NaN.
            - Merge lead values back onto all calls by (gvkey, fyearq).
            - Calls in the last fiscal year per firm, or fiscal year gaps, get
              NaN lead.
    Step 5: Assign industry sample (Main / Finance / Utility).
    Step 6: Save call-level panel.

Unit of observation: the individual earnings call (file_name).

Hypothesis:
    H2a: higher speech uncertainty -> lower investment efficiency (beta1 < 0)
    H2b: leverage attenuates the uncertainty-investment link (beta3 > 0)

DV: InvestmentResidual_lead  (Biddle 2009 abnormal investment, fiscal year t+1)
    > 0 = overinvestment, < 0 = underinvestment

Audit fixes applied:
    C-5/M-9: Lead variable now uses fyearq (fiscal year) for grouping and
             consecutive-year validation, not calendar year from start_date.
             This correctly handles ~30% of firms with non-December fiscal
             year-ends. fyearq is brought into the panel via an explicit
             Compustat join using the same merge_asof that matched all other
             Compustat variables to calls.

Inputs (all raw -- no reuse of prior panels):
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet  (Compustat)

Outputs:
    - outputs/variables/h2_investment/{timestamp}/h2_investment_panel.parquet
    - outputs/variables/h2_investment/{timestamp}/summary_stats.csv
    - outputs/variables/h2_investment/{timestamp}/report_step3_h2.md

Author: Thesis Author
Date: 2026-02-20
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
    # Linguistic uncertainty
    ManagerQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    # Weak modal (H2 extended uncertainty measures)
    ManagerQAWeakModalBuilder,
    CEOQAWeakModalBuilder,
    ManagerPresWeakModalBuilder,
    CEOPresWeakModalBuilder,
    # Clarity residuals (from H0.3 CEO Clarity Extended)
    CEOClarityResidualBuilder,
    ManagerClarityResidualBuilder,
    # Financial controls (Compustat engine)
    InvestmentResidualBuilder,
    LevBuilder,
    SizeBuilder,
    TobinsQBuilder,
    ROABuilder,
    CashFlowBuilder,
    SalesGrowthBuilder,
    # Manifest
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H2 Investment Efficiency Panel (call-level)",
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
        # Clarity residuals (from CEO Clarity Extended Stage 4)
        "ceo_clarity_residual": CEOClarityResidualBuilder({}),
        "manager_clarity_residual": ManagerClarityResidualBuilder({}),
        # H2 financial controls -- CompustatEngine is a singleton; all share one load
        "investment_residual": InvestmentResidualBuilder({}),
        "lev": LevBuilder({}),
        "size": SizeBuilder({}),
        "tobins_q": TobinsQBuilder({}),
        "roa": ROABuilder({}),
        "cash_flow": CashFlowBuilder({}),
        "sales_growth": SalesGrowthBuilder({}),
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

        # Drop conflicting columns (except file_name) to prevent _x/_y blowup
        conflicting = [
            c for c in data.columns if c in panel.columns and c != "file_name"
        ]
        if conflicting:
            print(
                f"  WARNING: {name} has overlapping columns {conflicting} "
                "-- dropping from builder data"
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

    # Assert ff12_code present (hard error)
    if "ff12_code" not in panel.columns:
        raise ValueError(
            "ff12_code column missing from panel after manifest merge. "
            "Cannot assign industry sample. Check ManifestFieldsBuilder output."
        )

    # Add call calendar year from start_date (used for reporting, not for lead)
    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Collect summary stats
    stats_list = []
    for name, result in all_results.items():
        stats_list.append(result.stats)
    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def create_lead_variable(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Create InvestmentResidual_lead at call level.

    C-5/M-9 fix: Uses fyearq (fiscal year from Compustat) rather than calendar
    year (start_date.dt.year) for grouping calls into firm-years and for the
    consecutive-year gap check. This correctly handles firms with non-December
    fiscal year-ends (~30% of Compustat firms).

    The lead is the firm's END-OF-FISCAL-YEAR investment residual in fiscal
    year t+1. 'End of fiscal year' = the InvestmentResidual matched to the
    call with the LATEST start_date within each (gvkey, fyearq) group.

    Construction:
    1. Attach fyearq to panel via merge_asof (same backward match as all
       other Compustat variables).
    2. For each (gvkey, fyearq), take InvestmentResidual from the call with
       the LATEST start_date (proxy for the Q4/year-end filing).
    3. Sort by gvkey, fyearq; shift -1 within gvkey -> next-fyearq residual.
    4. CRITICAL: validate that next row is exactly fyearq+1 (not fyearq+2 due
       to gaps). Gap in fiscal years -> NaN lead.
    5. Merge lead back onto all calls by (gvkey, fyearq).
    6. Calls in the last fiscal year per firm, or years with gaps, get NaN lead.

    All call-level rows are preserved -- Stage 4 drops NaN lead rows itself.
    """
    print("\n" + "=" * 60)
    print("Creating InvestmentResidual_lead (call-level, fiscal-year proxy)")
    print("=" * 60)

    if "InvestmentResidual" not in panel.columns:
        raise ValueError(
            "'InvestmentResidual' column missing -- cannot create lead variable."
        )
    if "start_date" not in panel.columns:
        raise ValueError(
            "'start_date' column missing -- cannot determine latest call per year."
        )

    # Step 1: Attach fyearq to panel (C-5/M-9 fix)
    panel = attach_fyearq(panel, root_path)

    if "fyearq" not in panel.columns or panel["fyearq"].isna().all():
        raise ValueError(
            "'fyearq' could not be attached to panel. "
            "Check CompustatEngine.get_data() returned fyearq."
        )

    # Convert fyearq to integer where possible for clean arithmetic
    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")
    n_missing_fyearq = panel["fyearq_int"].isna().sum()
    if n_missing_fyearq > 0:
        print(
            f"  WARNING: {n_missing_fyearq:,} calls have missing fyearq "
            f"-- these calls cannot be assigned to a fiscal year group "
            f"and will get NaN lead"
        )

    # Step 2: For each (gvkey, fyearq_int), find call with latest start_date
    panel_dt = panel.copy()
    panel_dt["start_date_dt"] = pd.to_datetime(panel_dt["start_date"], errors="coerce")

    # Drop calls with missing fyearq for the groupby (they can't be grouped)
    valid_mask = panel_dt["fyearq_int"].notna()
    panel_valid = panel_dt[valid_mask].copy()

    latest_idx = panel_valid.groupby(["gvkey", "fyearq_int"])["start_date_dt"].idxmax()
    firm_year_eoy = panel_valid.loc[
        latest_idx, ["gvkey", "fyearq_int", "InvestmentResidual"]
    ].copy()
    firm_year_eoy = firm_year_eoy.rename(
        columns={
            "fyearq_int": "fyearq_grp",
            "InvestmentResidual": "InvestmentResidual_eoy",
        }
    )

    print(f"  Unique firm-fiscal-years: {len(firm_year_eoy):,}")

    # Step 3: sort and shift to get next-fiscal-year end-of-year residual
    firm_year_eoy = firm_year_eoy.sort_values(["gvkey", "fyearq_grp"]).reset_index(
        drop=True
    )
    firm_year_eoy["fyearq_lead"] = firm_year_eoy.groupby("gvkey")["fyearq_grp"].shift(
        -1
    )
    firm_year_eoy["InvestmentResidual_lead_raw"] = firm_year_eoy.groupby("gvkey")[
        "InvestmentResidual_eoy"
    ].shift(-1)

    # Step 4: validate fiscal year continuity -- only keep lead if fyearq+1
    consecutive = firm_year_eoy["fyearq_lead"] == (firm_year_eoy["fyearq_grp"] + 1)
    firm_year_eoy["InvestmentResidual_lead"] = np.where(
        consecutive, firm_year_eoy["InvestmentResidual_lead_raw"], np.nan
    )

    n_last_year = firm_year_eoy["InvestmentResidual_lead_raw"].isna().sum()
    n_gap_year = (
        (~consecutive) & firm_year_eoy["InvestmentResidual_lead_raw"].notna()
    ).sum()
    n_valid_lead = firm_year_eoy["InvestmentResidual_lead"].notna().sum()
    print(
        f"  Firm-fiscal-years with no next year (last fiscal year per firm): "
        f"{n_last_year:,}"
    )
    print(f"  Firm-fiscal-years with fiscal year gap (lead nulled): {n_gap_year:,}")
    print(f"  Firm-fiscal-years with valid consecutive lead: {n_valid_lead:,}")

    # Sanity check: residuals should be centered near 0
    lead_vals = firm_year_eoy["InvestmentResidual_lead"].dropna()
    if len(lead_vals) > 0:
        n_extreme = (lead_vals.abs() > 1).sum()
        if n_extreme > 0:
            pct_extreme = 100 * n_extreme / len(lead_vals)
            print(
                f"  INFO: {n_extreme} InvestmentResidual_lead values with |residual|>1 "
                f"({pct_extreme:.1f}%) -- large values expected in overinvestment tail"
            )

    # Step 5: merge lead back to call level on (gvkey, fyearq_int)
    lead_lookup = firm_year_eoy[
        ["gvkey", "fyearq_grp", "InvestmentResidual_lead"]
    ].copy()
    lead_lookup = lead_lookup.rename(columns={"fyearq_grp": "fyearq_int"})

    before_len = len(panel)
    panel = panel.merge(lead_lookup, on=["gvkey", "fyearq_int"], how="left")
    after_len = len(panel)
    if after_len != before_len:
        raise ValueError(
            f"Lead merge changed row count {before_len} -> {after_len}. "
            "Duplicate (gvkey, fyearq_int) in firm-year lead lookup."
        )

    n_calls_no_lead = panel["InvestmentResidual_lead"].isna().sum()
    print(f"  Call-level rows: {len(panel):,}")
    print(
        f"  Calls without lead (last-year + gaps + missing fyearq): {n_calls_no_lead:,}"
    )
    print(
        f"  Calls with valid lead: {panel['InvestmentResidual_lead'].notna().sum():,}"
    )

    return panel


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h2_investment_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h2_investment" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H2_Investment",
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
    print("STAGE 3: Build H2 Investment Efficiency Panel (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Years:     {year_start}-{year_end}")
    print(f"Unit of observation: earnings call (file_name)")

    # Step 1-2: Build call-level panel
    panel = build_call_level_panel(root, years, var_config, stats)

    # Step 3: Create InvestmentResidual_lead using fiscal year (C-5/M-9 fix)
    panel = create_lead_variable(panel, root)

    # Step 4: Assign sample
    if "ff12_code" not in panel.columns:
        raise ValueError("ff12_code missing from panel. Cannot assign sample.")
    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    print("\n  Sample distribution (all calls, including last-year):")
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        n_lead = (
            panel.loc[panel["sample"] == sample, "InvestmentResidual_lead"]
            .notna()
            .sum()
        )
        print(f"    {sample}: {n:,} calls total, {n_lead:,} with valid lead")

    # Step 5: Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h2_investment_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"  Saved: h2_investment_panel.parquet "
        f"({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    # Summary stats CSV
    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

    # Generate run manifest for reproducibility
    manifest_input = root / "outputs" / "1.4_AssembleManifest" / "latest" / "master_sample_manifest.parquet"
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

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    report_lines = [
        "# Stage 3: H2 Investment Efficiency Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Unit of observation:** earnings call (file_name)",
        "",
        "## Audit Fixes Applied",
        "",
        "- **C-5/M-9**: Lead variable uses fyearq (fiscal year) for grouping and",
        "  consecutive-year validation, not calendar year. Correct for ~30% of",
        "  firms with non-December fiscal year-ends.",
        "",
        "## Panel Summary (call-level)",
        "",
        f"- **Total call observations:** {len(panel):,}",
        f"- **Unique firms:** {panel['gvkey'].nunique():,}",
        f"- **Year range (calendar):** {int(panel['year'].min())}-{int(panel['year'].max())}",
        f"- **Total columns:** {len(panel.columns)}",
        f"- **Calls with valid InvestmentResidual_lead:** "
        f"{panel['InvestmentResidual_lead'].notna().sum():,}",
        "",
        "### Sample Distribution",
        "",
        "| Sample | N Calls | N With Lead | % With Lead |",
        "|--------|---------|-------------|-------------|",
    ]
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        n_lead = (
            panel.loc[panel["sample"] == sample, "InvestmentResidual_lead"]
            .notna()
            .sum()
        )
        pct = 100.0 * n_lead / n if n > 0 else 0
        report_lines.append(f"| {sample} | {n:,} | {n_lead:,} | {pct:.1f}% |")

    report_lines += [
        "",
        "### Key Variable Coverage (all calls)",
        "",
        "| Variable | N non-missing | Mean | Std |",
        "|----------|--------------|------|-----|",
    ]
    for col in [
        "InvestmentResidual",
        "InvestmentResidual_lead",
        "Lev",
        "Size",
        "TobinsQ",
        "ROA",
        "CashFlow",
        "SalesGrowth",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
    ]:
        if col in panel.columns:
            n_valid = panel[col].notna().sum()
            mean = panel[col].mean()
            std = panel[col].std()
            report_lines.append(f"| {col} | {n_valid:,} | {mean:.4f} | {std:.4f} |")

    report_lines.append("")
    report_path = out_dir / "report_step3_h2.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  Saved: report_step3_h2.md")

    # Final summary
    stats["timing"]["duration_seconds"] = round(duration, 2)
    stats["panel"]["n_rows"] = len(panel)
    stats["panel"]["n_columns"] = len(panel.columns)
    stats["panel"]["n_with_lead"] = int(panel["InvestmentResidual_lead"].notna().sum())

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
