#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H15 Share Repurchase Panel
================================================================================
ID: variables/build_h15_repurchase_panel
Description: Build CALL-LEVEL panel for H15 Share Repurchase hypothesis test.

    This panel follows the H1/H4/H13 pattern:
    one row per earnings call (file_name), 4 simultaneous IVs,
    Base + Extended controls, fyearq_int time index.

    DV: REPO_callqtr — binary indicator (1 if cshopq > 0 in the call quarter).
    Following Duong, Do, and Do (2025), the call is matched to the fiscal quarter
    containing the call (one quarter AFTER the reporting quarter matched by
    merge_asof). Construction uses fiscal-quarter-validated lead of REPO.

    Year restriction: 2004-2018 (cshopq is 100% NaN in 2002, 99.7% in 2003).

Outputs:
    - outputs/variables/h15_repurchase/{timestamp}/h15_repurchase_panel.parquet
    - outputs/variables/h15_repurchase/{timestamp}/summary_stats.csv
    - outputs/variables/h15_repurchase/{timestamp}/run_manifest.json

Author: Thesis Author
Date: 2026-03-17
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
    # 4 Key IVs (all simultaneous)
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    ManagerQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    # Base controls (Compustat engine) — all 8 (REPO is DV, not in control set)
    SizeBuilder,
    TobinsQBuilder,
    ROABuilder,
    BookLevBuilder,
    CapexIntensityBuilder,
    CashHoldingsBuilder,
    DividendPayerBuilder,
    OCFVolatilityBuilder,
    # Extended controls
    SalesGrowthBuilder,
    RDIntensityBuilder,
    CashFlowBuilder,
    VolatilityBuilder,
    # DV builder
    RepurchaseIndicatorBuilder,
    # Manifest
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H15 Share Repurchase Panel (call-level)",
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
    """Build call-level panel by loading and merging all variables."""
    print("\n" + "=" * 60)
    print("Loading variables (call-level)")
    print("=" * 60)

    all_results: Dict[str, Any] = {}

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        # 4 Key IVs (all simultaneous)
        "ceo_qa_uncertainty": CEOQAUncertaintyBuilder(
            var_config.get("ceo_qa_uncertainty", {})
        ),
        "ceo_pres_uncertainty": CEOPresUncertaintyBuilder(
            var_config.get("ceo_pres_uncertainty", {})
        ),
        "manager_qa_uncertainty": ManagerQAUncertaintyBuilder(
            var_config.get("manager_qa_uncertainty", {})
        ),
        "manager_pres_uncertainty": ManagerPresUncertaintyBuilder(
            var_config.get("manager_pres_uncertainty", {})
        ),
        # Base controls — all 8 (REPO ∉ {BookLev, CashHoldings, CapexAt})
        "size": SizeBuilder({}),
        "tobins_q": TobinsQBuilder({}),
        "roa": ROABuilder({}),
        "lev": BookLevBuilder({}),
        "capex_intensity": CapexIntensityBuilder({}),
        "cash_holdings": CashHoldingsBuilder({}),
        "dividend_payer": DividendPayerBuilder({}),
        "ocf_volatility": OCFVolatilityBuilder({}),
        # Extended controls
        "sales_growth": SalesGrowthBuilder(var_config.get("sales_growth", {})),
        "rd_intensity": RDIntensityBuilder(var_config.get("rd_intensity", {})),
        "cash_flow": CashFlowBuilder(var_config.get("cash_flow", {})),
        "volatility": VolatilityBuilder(var_config.get("volatility", {})),
        # DV source (reporting-quarter REPO — will be led in create_repo_callqtr)
        "repurchase_indicator": RepurchaseIndicatorBuilder({}),
    }

    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    panel = all_results["manifest"].data.copy()

    if panel["file_name"].duplicated().any():
        n_dups = panel["file_name"].duplicated().sum()
        raise ValueError(
            f"Manifest has {n_dups} duplicate file_name rows. "
            "Panel build aborted to prevent row multiplication."
        )

    print(f"\n  Base manifest: {len(panel):,} rows")

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
            "Cannot assign industry sample. Check ManifestFieldsBuilder output."
        )

    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    stats_list = []
    for name, result in all_results.items():
        stats_list.append(result.stats)
    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def create_repo_callqtr(
    panel: pd.DataFrame, root_path: Path
) -> pd.DataFrame:
    """Create REPO_callqtr: repurchase indicator for the call quarter.

    The CompustatEngine's merge_asof matches each call to the REPORTING quarter
    (datadate <= start_date). Duong et al. (2025) match calls to the CALL quarter
    (the quarter containing the call = one quarter AFTER the reporting quarter).

    Construction:
    1. Attach fyearq + fqtr via merge_asof to get reporting quarter identity.
    2. Build (gvkey, fyearq, fqtr) -> REPO lookup from full Compustat quarterly panel.
    3. Compute next-quarter indices (fqtr+1, with fiscal year rollover at Q4->Q1).
    4. Merge to get REPO for the call quarter.
    5. Validate: if next quarter doesn't exist in Compustat -> NaN.
    """
    print("\n" + "=" * 60)
    print("Creating REPO_callqtr (call-quarter repurchase indicator)")
    print("=" * 60)

    if "REPO" not in panel.columns:
        raise ValueError("'REPO' column missing -- cannot create call-quarter variable.")

    # Step 1: Attach fyearq to panel (for fiscal year identity)
    panel = attach_fyearq(panel, root_path)
    panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")

    n_missing = panel["fyearq_int"].isna().sum()
    if n_missing > 0:
        print(f"  WARNING: {n_missing:,} calls have missing fyearq")

    # fqtr comes from the engine via merge_asof (now in COMPUSTAT_COLS)
    if "fqtr" not in panel.columns:
        raise ValueError(
            "'fqtr' column missing from panel. Ensure fqtr is in COMPUSTAT_COLS."
        )

    panel["fqtr_int"] = pd.to_numeric(panel["fqtr"], errors="coerce")

    # Step 2: Build (gvkey, fyearq, fqtr) -> REPO lookup from full Compustat
    comp = pd.read_parquet(
        root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
        columns=["gvkey", "fyearq", "fqtr", "cshopq"],
    )
    comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
    comp["fyearq_int"] = pd.to_numeric(comp["fyearq"], errors="coerce")
    comp["fqtr_int"] = pd.to_numeric(comp["fqtr"], errors="coerce")

    # Compute REPO at Compustat quarterly level
    comp["REPO_qtr"] = np.where(
        comp["cshopq"].notna() & (comp["cshopq"] > 0),
        1.0,
        np.where(comp["cshopq"].notna(), 0.0, np.nan),
    )

    # Deduplicate: keep one row per (gvkey, fyearq, fqtr) — take last by datadate
    repo_lookup = (
        comp.dropna(subset=["fyearq_int", "fqtr_int"])
        .drop_duplicates(subset=["gvkey", "fyearq_int", "fqtr_int"], keep="last")
        [["gvkey", "fyearq_int", "fqtr_int", "REPO_qtr"]]
        .copy()
    )
    print(f"  Compustat quarterly REPO lookup: {len(repo_lookup):,} firm-quarters")
    print(f"  REPO_qtr=1: {(repo_lookup['REPO_qtr']==1).sum():,}")
    print(f"  REPO_qtr=0: {(repo_lookup['REPO_qtr']==0).sum():,}")
    print(f"  REPO_qtr=NaN: {repo_lookup['REPO_qtr'].isna().sum():,}")

    # Step 3: For each call, compute next-quarter indices
    # The reporting quarter is (fyearq_int, fqtr_int). The call quarter is one ahead.
    panel["next_fqtr"] = panel["fqtr_int"] % 4 + 1  # 1->2, 2->3, 3->4, 4->1
    panel["next_fyearq"] = panel["fyearq_int"] + (panel["fqtr_int"] == 4).astype(float)

    # Step 4: Merge to get REPO for the call quarter
    repo_lookup = repo_lookup.rename(columns={
        "fyearq_int": "next_fyearq",
        "fqtr_int": "next_fqtr",
        "REPO_qtr": "REPO_callqtr",
    })

    before_len = len(panel)
    panel = panel.merge(
        repo_lookup,
        on=["gvkey", "next_fyearq", "next_fqtr"],
        how="left",
    )
    after_len = len(panel)
    if after_len != before_len:
        raise ValueError(
            f"REPO_callqtr merge changed row count {before_len} -> {after_len}. "
            "Duplicate (gvkey, next_fyearq, next_fqtr) in lookup."
        )

    # Clean up temp columns
    panel = panel.drop(columns=["next_fqtr", "next_fyearq"])

    n_valid = panel["REPO_callqtr"].notna().sum()
    n_repo1 = (panel["REPO_callqtr"] == 1).sum()
    n_repo0 = (panel["REPO_callqtr"] == 0).sum()
    print(f"\n  REPO_callqtr coverage: {n_valid:,} / {len(panel):,} ({100*n_valid/len(panel):.1f}%)")
    print(f"  REPO_callqtr=1 (repurchased): {n_repo1:,}")
    print(f"  REPO_callqtr=0 (did not): {n_repo0:,}")
    print(f"  REPO_callqtr=NaN (missing): {panel['REPO_callqtr'].isna().sum():,}")

    return panel


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h15_repurchase_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h15_repurchase" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H15_Repurchase",
        timestamp=timestamp,
    )

    config = get_config(root / "config" / "project.yaml")
    var_config = load_variable_config(root / "config" / "variables.yaml")

    # Year restriction: cshopq is 100% NaN in 2002, 99.7% NaN in 2003
    if year_start is None:
        year_start = max(config.data.year_start, 2004)
    else:
        year_start = max(year_start, 2004)
    if year_end is None:
        year_end = config.data.year_end
    years = range(year_start, year_end + 1)

    print("=" * 80)
    print("STAGE 3: Build H15 Share Repurchase Panel (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Years:     {year_start}-{year_end} (cshopq unavailable before 2004)")
    print(f"Unit of observation: earnings call (file_name)")

    # Step 1-2: Build call-level panel
    panel = build_call_level_panel(root, years, var_config, stats)

    # Step 3: Create REPO_callqtr (call-quarter repurchase indicator)
    panel = create_repo_callqtr(panel, root_path=root)

    # Step 4: Assign sample
    if "ff12_code" not in panel.columns:
        raise ValueError("ff12_code missing from panel. Cannot assign sample.")
    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        n_repo = panel.loc[panel["sample"] == sample, "REPO_callqtr"].notna().sum()
        print(f"    {sample}: {n:,} calls total, {n_repo:,} with REPO_callqtr")

    # Step 5: Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h15_repurchase_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"  Saved: h15_repurchase_panel.parquet "
        f"({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

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
        "# Stage 3: H15 Share Repurchase Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary",
        "",
        f"- **Unit:** Call-level (one row per earnings call)",
        f"- **Total rows:** {len(panel):,}",
        f"- **Columns:** {len(panel.columns)}",
        f"- **Years:** {year_start}-{year_end}",
        "",
        "## Dependent Variable (Share Repurchase)",
        f"- **REPO_callqtr=1:** {(panel['REPO_callqtr']==1).sum():,} calls",
        f"- **REPO_callqtr=0:** {(panel['REPO_callqtr']==0).sum():,} calls",
        f"- **REPO_callqtr=NaN:** {panel['REPO_callqtr'].isna().sum():,} calls",
        "",
        "## Key IVs (4 simultaneous)",
        f"- **CEO_QA_Uncertainty_pct:** {panel['CEO_QA_Uncertainty_pct'].notna().sum():,} calls",
        f"- **CEO_Pres_Uncertainty_pct:** {panel['CEO_Pres_Uncertainty_pct'].notna().sum():,} calls",
        f"- **Manager_QA_Uncertainty_pct:** {panel['Manager_QA_Uncertainty_pct'].notna().sum():,} calls",
        f"- **Manager_Pres_Uncertainty_pct:** {panel['Manager_Pres_Uncertainty_pct'].notna().sum():,} calls",
        "",
        "## Sample Distribution",
        "",
        "| Sample | Total Calls | With REPO_callqtr |",
        "|--------|------------:|------------------:|",
    ]
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        n_repo = panel.loc[panel["sample"] == sample, "REPO_callqtr"].notna().sum()
        report_lines.append(f"| {sample} | {n:,} | {n_repo:,} |")

    report_path = out_dir / "report_step3_h15_repurchase.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"  Saved: report_step3_h15_repurchase.md")

    print("\n" + "=" * 80)
    print("H15 Share Repurchase Panel build complete.")
    print(f"Duration: {duration:.1f} seconds")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("DRY-RUN mode -- validating inputs only")
        print("DRY-RUN complete.")
        sys.exit(0)

    sys.exit(main(args.year_start, args.year_end))
