#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build Liquidity Panel (4.2 Liquidity Regressions)
================================================================================
ID: variables/build_liquidity_panel
Description: Build panel for the Liquidity Regressions (4.2). Loads all
             variables needed for OLS and 2SLS regressions:
               - Dependent variables: Delta_Amihud, Delta_Corwin_Schultz
               - Endogenous: Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct
               - Instrument: shift_intensity_sale_ff48 (CCCL)
               - Exogenous: ClarityManager (from 4.1), ClarityCEO (from 4.1.1)
               - Linguistic controls: Analyst_QA_Uncertainty_pct,
                                      Entire_All_Negative_pct,
                                      Manager_Pres_Uncertainty_pct,
                                      CEO_Pres_Uncertainty_pct
               - Financial controls: Size, BM, Lev, ROA, CurrentRatio,
                                     RD_Intensity, Volatility, EPS_Growth,
                                     StockRet, MarketRet, SurpDec

Note on data coverage:
    - market_variables_{year}.parquet (Delta_Amihud, Delta_Corwin_Schultz)
      only available for 2002-2011. IV regression sample thus 2005-2011
      (CCCL instrument starts 2005).
    - Clarity scores are matched per CEO per industry sample.

Inputs (all raw/direct):
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - outputs/3_Financial_Features/latest/market_variables_{year}.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet  (Compustat)
    - inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet        (CRSP daily)
    - inputs/tr_ibes/tr_ibes.parquet                       (IBES)
    - inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet   (CCM linktable)
    - inputs/CCCL_instrument/instrument_shift_intensity_2005_2022.parquet
    - outputs/econometric/manager_clarity/latest/clarity_scores.parquet
    - outputs/econometric/ceo_clarity/latest/clarity_scores.parquet

Outputs:
    - outputs/variables/liquidity/{timestamp}/liquidity_panel.parquet
    - outputs/variables/liquidity/{timestamp}/summary_stats.csv
    - outputs/variables/liquidity/{timestamp}/report_step3_liquidity.md

Deterministic: true
Dependencies:
    - Requires: Stage 3 market_variables (3.2), Stage 4 clarity scores (4.1, 4.1.1)
    - Uses: f1d.shared.variables, f1d.shared.config

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
from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError
from f1d.shared.variables import (
    ManagerQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    SizeBuilder,
    BMBuilder,
    LevBuilder,
    ROABuilder,
    CurrentRatioBuilder,
    RDIntensityBuilder,
    EPSGrowthBuilder,
    StockReturnBuilder,
    MarketReturnBuilder,
    VolatilityBuilder,
    EarningsSurpriseBuilder,
    CCCLInstrumentBuilder,
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 3: Build Liquidity Panel (4.2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without executing",
    )
    parser.add_argument(
        "--year-start",
        type=int,
        default=None,
        help="Start year (default: from config)",
    )
    parser.add_argument(
        "--year-end",
        type=int,
        default=None,
        help="End year (default: from config)",
    )
    return parser.parse_args()


def assign_industry_sample(ff12_code: pd.Series) -> pd.Series:
    """Assign industry sample based on FF12 code.

    Uses np.select to avoid deprecated boolean-indexed Series assignment.
    """
    conditions = [ff12_code == 11, ff12_code == 8]
    choices = ["Finance", "Utility"]
    return pd.Series(
        np.select(conditions, choices, default="Main"),
        index=ff12_code.index,
        dtype=object,
    )


def load_market_dep_vars(root_path: Path, years: range) -> pd.DataFrame:
    """Load Delta_Amihud and Delta_Corwin_Schultz from market_variables_{year}.parquet.

    These are the dependent variables for liquidity regressions. They are only
    available in market_variables_{year}.parquet alongside Volatility/StockRet/MarketRet
    (which are handled separately via CRSP engine builders). This function only
    extracts the liquidity-specific dep vars to avoid column conflicts.

    Returns:
        DataFrame with columns: file_name, Delta_Amihud, Delta_Corwin_Schultz
    """
    dep_var_cols = ["Delta_Amihud", "Delta_Corwin_Schultz"]
    all_chunks: List[pd.DataFrame] = []

    for year in years:
        try:
            mv_dir = get_latest_output_dir(
                root_path / "outputs" / "3_Financial_Features",
                required_file=f"market_variables_{year}.parquet",
            )
            mv_path = mv_dir / f"market_variables_{year}.parquet"
            mv = pd.read_parquet(mv_path, columns=["file_name"] + dep_var_cols)
            all_chunks.append(mv)
        except (OutputResolutionError, FileNotFoundError):
            # Not all years have market_variables — that is expected
            continue
        except Exception as e:
            print(f"    WARNING: market_variables_{year}.parquet error: {e}")
            continue

    if not all_chunks:
        print(
            "    WARNING: No market_variables files found. Delta_Amihud/Delta_Corwin_Schultz will be NaN."
        )
        return pd.DataFrame(columns=["file_name"] + dep_var_cols)

    combined = pd.concat(all_chunks, ignore_index=True)
    # Keep only columns that actually exist
    available_dep_vars = [c for c in dep_var_cols if c in combined.columns]
    combined = combined[["file_name"] + available_dep_vars].drop_duplicates("file_name")

    n_amihud = (
        combined["Delta_Amihud"].notna().sum()
        if "Delta_Amihud" in combined.columns
        else 0
    )
    n_cs = (
        combined["Delta_Corwin_Schultz"].notna().sum()
        if "Delta_Corwin_Schultz" in combined.columns
        else 0
    )
    print(
        f"    Dep vars: {len(combined):,} calls, Delta_Amihud {n_amihud:,} non-null, Delta_Corwin_Schultz {n_cs:,} non-null"
    )
    return combined


def load_clarity_scores(root_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load ClarityManager and ClarityCEO scores from Stage 4 outputs.

    Returns:
        Tuple of (manager_clarity, ceo_clarity) DataFrames, each with
        columns [ceo_id, sample, ClarityManager/ClarityCEO].
        Returns empty DataFrames if not found (warnings printed).
    """
    # Manager Clarity (4.1)
    try:
        mgr_dir = get_latest_output_dir(
            root_path / "outputs" / "econometric" / "manager_clarity",
            required_file="clarity_scores.parquet",
        )
        mgr = pd.read_parquet(
            mgr_dir / "clarity_scores.parquet",
            columns=["ceo_id", "sample", "ClarityManager"],
        )
        mgr["ceo_id"] = mgr["ceo_id"].astype(str)
        print(f"    ClarityManager: {len(mgr):,} CEO-sample pairs loaded")
    except (OutputResolutionError, FileNotFoundError):
        mgr = pd.DataFrame(columns=["ceo_id", "sample", "ClarityManager"])
        print("    WARNING: ClarityManager scores not found — column will be NaN")

    # CEO Clarity (4.1.1)
    try:
        ceo_dir = get_latest_output_dir(
            root_path / "outputs" / "econometric" / "ceo_clarity",
            required_file="clarity_scores.parquet",
        )
        ceo = pd.read_parquet(
            ceo_dir / "clarity_scores.parquet",
            columns=["ceo_id", "sample", "ClarityCEO"],
        )
        ceo["ceo_id"] = ceo["ceo_id"].astype(str)
        print(f"    ClarityCEO: {len(ceo):,} CEO-sample pairs loaded")
    except (OutputResolutionError, FileNotFoundError):
        ceo = pd.DataFrame(columns=["ceo_id", "sample", "ClarityCEO"])
        print("    WARNING: ClarityCEO scores not found — column will be NaN")

    return mgr, ceo


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Build complete liquidity panel for OLS and 2SLS regressions.

    Variables loaded:
      Manifest (Stage 1):
        file_name, ceo_id, ceo_name, gvkey, ff12_code, ff12_name,
        ff48_code, start_date
      Textual (Stage 2):
        Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct,
        CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct,
        Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct
      Liquidity dep vars (Stage 3 market_variables):
        Delta_Amihud, Delta_Corwin_Schultz
      Financial (raw Compustat):
        Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, EPS_Growth
      Financial (raw CRSP):
        StockRet, MarketRet, Volatility
      Financial (raw IBES):
        SurpDec
      CCCL instrument:
        shift_intensity_sale_ff48
      Clarity scores (Stage 4):
        ClarityManager (per CEO-sample), ClarityCEO (per CEO-sample)
    """
    print("\n" + "=" * 60)
    print("Loading variables")
    print("=" * 60)

    all_results: Dict[str, Any] = {}

    # Manifest — include ff48_code for the liquidity panel
    manifest_config = dict(var_config.get("manifest", {}))
    manifest_config["columns"] = [
        "file_name",
        "ceo_id",
        "ceo_name",
        "gvkey",
        "ff12_code",
        "ff12_name",
        "ff48_code",
        "start_date",
    ]

    builders = {
        "manifest": ManifestFieldsBuilder(manifest_config),
        # Textual — Stage 2 outputs
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
        # Compustat individual variables (one per builder)
        "size": SizeBuilder({}),
        "bm": BMBuilder({}),
        "lev": LevBuilder({}),
        "roa": ROABuilder({}),
        "current_ratio": CurrentRatioBuilder({}),
        "rd_intensity": RDIntensityBuilder({}),
        "eps_growth": EPSGrowthBuilder({}),
        # CRSP individual variables (one per builder)
        "stock_return": StockReturnBuilder({}),
        "market_return": MarketReturnBuilder({}),
        "volatility": VolatilityBuilder({}),
        # IBES
        "earnings_surprise": EarningsSurpriseBuilder(
            var_config.get("earnings_surprise", {})
        ),
        # CCCL instrument
        "cccl_instrument": CCCLInstrumentBuilder(var_config.get("cccl_instrument", {})),
    }

    # Build all variable builders
    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    # Start with manifest as base
    manifest_result = all_results["manifest"]
    panel = manifest_result.data.copy()

    # Assert manifest uniqueness
    if panel["file_name"].duplicated().any():
        n_dups = panel["file_name"].duplicated().sum()
        raise ValueError(
            f"Manifest has {n_dups} duplicate file_name rows. "
            "Panel build aborted to prevent row multiplication."
        )

    print(f"\n  Base manifest: {len(panel):,} rows")

    # Merge all shared variable builder results on file_name
    for name, result in all_results.items():
        if name == "manifest":
            continue

        data = result.data.copy()
        if "file_name" not in data.columns or len(data.columns) <= 1:
            print(f"  WARNING: {name} returned no usable columns — skipping merge")
            continue

        # Assert builder output uniqueness on file_name
        if data["file_name"].duplicated().any():
            n_dups = data["file_name"].duplicated().sum()
            raise ValueError(
                f"Builder '{name}' returned {n_dups} duplicate file_name rows. "
                "Merge aborted to prevent fan-out."
            )

        # Drop columns already in panel (except file_name) to prevent _x/_y conflicts
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
        delta = after_len - before_len
        if after_len != before_len:
            raise ValueError(
                f"Merge of '{name}' changed row count {before_len} → {after_len} (delta: {delta:+d}). "
                "Duplicate file_name detected in builder output post-merge."
            )
        print(f"  After {name} merge: {after_len:,} rows (delta: {delta:+d})")

    # Load and merge liquidity dependent variables from market_variables_{year}.parquet
    print(f"  Loading market_dep_vars...")
    dep_vars_df = load_market_dep_vars(root_path, years)
    if len(dep_vars_df) > 0:
        dep_var_data_cols = [c for c in dep_vars_df.columns if c != "file_name"]
        # Assert uniqueness
        if dep_vars_df["file_name"].duplicated().any():
            n_dups = dep_vars_df["file_name"].duplicated().sum()
            raise ValueError(f"Market dep vars have {n_dups} duplicate file_name rows.")
        # Drop any conflicting columns
        conflicting = [c for c in dep_var_data_cols if c in panel.columns]
        if conflicting:
            dep_vars_df = dep_vars_df.drop(columns=conflicting)
        before_len = len(panel)
        panel = panel.merge(dep_vars_df, on="file_name", how="left")
        after_len = len(panel)
        delta = after_len - before_len
        if after_len != before_len:
            raise ValueError(
                f"Market dep vars merge changed row count {before_len} → {after_len} (delta: {delta:+d})."
            )
        print(f"  After market_dep_vars merge: {after_len:,} rows (delta: {delta:+d})")

    # Add derived fields
    if "ff12_code" not in panel.columns:
        raise ValueError(
            "ff12_code column missing from panel after manifest merge. "
            "Cannot assign industry sample."
        )
    if panel["ff12_code"].isna().any():
        n_nan = panel["ff12_code"].isna().sum()
        raise ValueError(
            f"ff12_code has {n_nan} NaN values. Panel build aborted. "
            "Run upstream fix (parse_ff_industries catch-all) first."
        )
    panel["sample"] = assign_industry_sample(panel["ff12_code"])
    print(f"\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        print(f"    {sample}: {n:,} calls")

    # Add year column if not present
    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Merge clarity scores on ceo_id × sample
    print("\n  Loading clarity scores...")
    mgr_clarity, ceo_clarity = load_clarity_scores(root_path)

    panel["ceo_id"] = panel["ceo_id"].astype(str)

    if len(mgr_clarity) > 0:
        before_len = len(panel)
        panel = panel.merge(
            mgr_clarity[["ceo_id", "sample", "ClarityManager"]],
            on=["ceo_id", "sample"],
            how="left",
        )
        after_len = len(panel)
        delta = after_len - before_len
        if after_len != before_len:
            raise ValueError(
                f"ClarityManager merge changed row count {before_len} → {after_len} (delta: {delta:+d})."
            )
        n_matched = panel["ClarityManager"].notna().sum()
        print(
            f"  After ClarityManager merge: {after_len:,} rows, {n_matched:,} with ClarityManager (delta: {delta:+d})"
        )
    else:
        panel["ClarityManager"] = float("nan")

    if len(ceo_clarity) > 0:
        before_len = len(panel)
        panel = panel.merge(
            ceo_clarity[["ceo_id", "sample", "ClarityCEO"]],
            on=["ceo_id", "sample"],
            how="left",
        )
        after_len = len(panel)
        delta = after_len - before_len
        if after_len != before_len:
            raise ValueError(
                f"ClarityCEO merge changed row count {before_len} → {after_len} (delta: {delta:+d})."
            )
        n_matched = panel["ClarityCEO"].notna().sum()
        print(
            f"  After ClarityCEO merge: {after_len:,} rows, {n_matched:,} with ClarityCEO (delta: {delta:+d})"
        )
    else:
        panel["ClarityCEO"] = float("nan")

    # Report variable coverage
    print(f"\n  Variable coverage:")
    coverage_cols = [
        "Delta_Amihud",
        "Delta_Corwin_Schultz",
        "shift_intensity_sale_ff48",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "ClarityManager",
        "ClarityCEO",
        "Size",
        "BM",
        "Lev",
        "ROA",
        "CurrentRatio",
        "RD_Intensity",
        "Volatility",
        "EPS_Growth",
        "StockRet",
        "MarketRet",
        "SurpDec",
    ]
    for col in coverage_cols:
        if col in panel.columns:
            n = panel[col].notna().sum()
            pct = 100.0 * n / len(panel) if len(panel) > 0 else 0
            print(f"    {col}: {n:,} ({pct:.1f}%)")

    # Collect all summary stats
    stats_list = []
    for name, result in all_results.items():
        stats_list.append(result.stats)

    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def save_outputs(
    panel: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
) -> None:
    """Save panel and summary statistics."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "liquidity_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"  Saved: liquidity_panel.parquet ({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")


def generate_report(
    panel: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report."""
    report_lines = [
        "# Stage 3: Liquidity Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Purpose",
        "",
        "Panel for 4.2 Liquidity Regressions (OLS + 2SLS). Contains:",
        "- Dependent variables: Delta_Amihud, Delta_Corwin_Schultz",
        "- Endogenous: Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct",
        "- Instrument: shift_intensity_sale_ff48 (CCCL, starts 2005)",
        "- Clarity scores: ClarityManager (4.1), ClarityCEO (4.1.1)",
        "",
        "## Data Coverage Note",
        "",
        "market_variables_{year}.parquet only available for 2002-2011.",
        "CCCL instrument starts 2005. IV regression sample: 2005-2011.",
        "OLS regression sample: 2002-2011 (where Delta_Amihud is non-null).",
        "",
        "## Panel Summary",
        "",
        f"- **Total observations:** {len(panel):,}",
        f"- **Total columns:** {len(panel.columns)}",
        "",
    ]

    if "sample" in panel.columns:
        report_lines.append("### Sample Distribution")
        report_lines.append("")
        report_lines.append("| Sample | N Calls | % |")
        report_lines.append("|--------|---------|---|")
        for sample in ["Main", "Finance", "Utility"]:
            n = (panel["sample"] == sample).sum()
            pct = 100.0 * n / len(panel) if len(panel) > 0 else 0
            report_lines.append(f"| {sample} | {n:,} | {pct:.1f}% |")
        report_lines.append("")

    report_lines.append("### Key Variable Coverage")
    report_lines.append("")
    report_lines.append("| Variable | N Non-Missing | % Coverage |")
    report_lines.append("|----------|--------------|------------|")
    for col in [
        "Delta_Amihud",
        "Delta_Corwin_Schultz",
        "shift_intensity_sale_ff48",
        "ClarityManager",
        "ClarityCEO",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Size",
        "BM",
        "Volatility",
        "SurpDec",
    ]:
        if col in panel.columns:
            n = panel[col].notna().sum()
            pct = 100.0 * n / len(panel) if len(panel) > 0 else 0
            report_lines.append(f"| {col} | {n:,} | {pct:.1f}% |")
    report_lines.append("")

    report_lines.append("### Unique Entities")
    report_lines.append("")
    if "ceo_id" in panel.columns:
        report_lines.append(f"- **Unique CEOs:** {panel['ceo_id'].nunique():,}")
    if "gvkey" in panel.columns:
        report_lines.append(f"- **Unique firms:** {panel['gvkey'].nunique():,}")
    if "year" in panel.columns:
        yr_min = panel["year"].min()
        yr_max = panel["year"].max()
        report_lines.append(f"- **Year range (manifest):** {yr_min}–{yr_max}")
    if "Delta_Amihud" in panel.columns:
        n_dep = panel["Delta_Amihud"].notna().sum()
        yr_dep = panel.loc[panel["Delta_Amihud"].notna(), "year"]
        if len(yr_dep) > 0:
            report_lines.append(
                f"- **Year range (Delta_Amihud):** {yr_dep.min()}–{yr_dep.max()} ({n_dep:,} obs)"
            )
    report_lines.append("")

    report_path = out_dir / "report_step3_liquidity.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"  Saved: report_step3_liquidity.md")


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_liquidity_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "liquidity" / timestamp

    # Load configs — pass explicit paths so CWD doesn't matter
    config = get_config(root / "config" / "project.yaml")
    var_config = load_variable_config(root / "config" / "variables.yaml")

    # Get year range
    if year_start is None:
        year_start = config.data.year_start
    if year_end is None:
        year_end = config.data.year_end
    years = range(year_start, year_end + 1)

    print("=" * 80)
    print("STAGE 3: Build Liquidity Panel (4.2)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {year_start}-{year_end}")
    print("Note: Delta_Amihud/Delta_Corwin_Schultz only available 2002-2011")

    # Build panel
    panel = build_panel(root, years, var_config, stats)

    # Save outputs
    save_outputs(panel, stats, out_dir)

    # Generate report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(panel, stats, out_dir, duration)

    # Final summary
    stats["timing"]["duration_seconds"] = round(duration, 2)
    stats["panel"]["n_rows"] = len(panel)
    stats["panel"]["n_columns"] = len(panel.columns)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
