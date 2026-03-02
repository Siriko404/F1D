#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H8 Political Risk Panel
================================================================================
ID: variables/build_h8_political_risk_panel
Description: Build FIRM-YEAR panel for H8: CEO Speech Vagueness moderates the
             effect of Political Risk (PRiskFY) on Abnormal Investment.

    H8 Hypothesis:
        AbsAbInv_{i,t+1} = β0 + β1·PRiskFY_t + β2·StyleFrozen_t
                          + β3·(PRiskFY_t × StyleFrozen_t)
                          + γ'·Controls_t + FirmFE_i + YearFE_t + ε

    Key coefficient: β3 (interaction term)
        β3 > 0: Vague CEOs amplify PRisk → abnormal investment
        β3 < 0: Vague CEOs dampen PRisk → abnormal investment

Unit of observation: firm-fiscal-year (gvkey, fyearq).
DV: |InvestmentResidual| shifted one fiscal year forward (t+1).

Step 1: Load manifest + all linguistic uncertainty measures.
Step 2: Load PRiskFY (Hassan engine), StyleFrozen (CEO Clarity builder),
        InvestmentResidual (Compustat engine), and financial controls.
Step 3: Aggregate call-level vagueness to firm-year level:
            StyleFrozen  = frozen CEO ClarityCEO (time-invariant per CEO-FY)
            PRiskFY      = already at firm-year level
            AbsAbInv     = |InvestmentResidual|, shifted t+1 within firm
Step 4: Create interaction term: interact = PRiskFY × style_frozen
Step 5: Save firm-year panel.
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
from f1d.shared.variables.panel_utils import attach_fyearq, assign_industry_sample
from f1d.shared.variables import (
    ManifestFieldsBuilder,
    SizeBuilder,
    LevBuilder,
    ROABuilder,
    TobinsQBuilder,
    InvestmentResidualBuilder,
    stats_list_to_dataframe,
)
from f1d.shared.variables.prisk_fy import PRiskFYBuilder
from f1d.shared.variables.ceo_clarity_style import CEOClarityStyleBuilder


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H8 Political Risk × CEO Clarity Panel",
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

    For variables that are already firm-year level (PRiskFY, InvestmentResidual,
    style_frozen, financial controls), take the last non-missing value per
    (gvkey, fyearq) — they should be constant within (gvkey, fyearq).

    Returns a DataFrame indexed on (gvkey, fyearq).
    """
    if "fyearq" not in panel.columns:
        raise ValueError("Panel must have a 'fyearq' column for firm-year aggregation.")

    agg_cols = [
        "PRiskFY",
        "style_frozen",
        "InvestmentResidual",
        "Size",
        "Lev",
        "ROA",
        "TobinsQ",
        "ff12_code",
    ]
    existing = [c for c in agg_cols if c in panel.columns]

    # Sort by (gvkey, fyearq, start_date) so "last" = last call in the FY
    df = panel.sort_values(["gvkey", "fyearq", "start_date"], na_position="last")
    # Take the last non-NaN per (gvkey, fyearq) for each column
    firm_year = df.groupby(["gvkey", "fyearq"])[existing].last().reset_index()
    return firm_year


def create_lead_absabinv(firm_year: pd.DataFrame) -> pd.DataFrame:
    """Create AbsAbInv_lead = |InvestmentResidual| shifted one FY forward.

    - AbsAbInv_t = |InvestmentResidual_t|  (absolute abnormal investment)
    - AbsAbInv_lead_t = AbsAbInv_{t+1}  (DV: next-year's overinvestment)
    - Gap years (non-consecutive fyearq) → NaN (no survivorship selection)
    """
    df = firm_year.copy()
    df["AbsAbInv"] = df["InvestmentResidual"].abs()

    df = df.sort_values(["gvkey", "fyearq"]).reset_index(drop=True)
    df["next_fyearq"] = df.groupby("gvkey")["fyearq"].shift(-1)
    df["AbsAbInv_next"] = df.groupby("gvkey")["AbsAbInv"].shift(-1)

    # Null out non-consecutive years (gap > 1).
    # Cast to Int64 before arithmetic to avoid IEEE 754 float precision risk
    # (e.g. 2011.0 - 2010.0 occasionally yields 0.9999... not 1.0 for some years).
    fyearq_int = df["fyearq"].astype("Int64")
    next_fyearq_int = df["next_fyearq"].astype("Int64")
    is_consecutive = (next_fyearq_int - fyearq_int) == 1
    df.loc[~is_consecutive, "AbsAbInv_next"] = np.nan

    df = df.rename(columns={"AbsAbInv_next": "AbsAbInv_lead"})
    df = df.drop(columns=["next_fyearq"], errors="ignore")
    return df


def create_interaction(firm_year: pd.DataFrame) -> pd.DataFrame:
    """Create the moderation interaction: interact = PRiskFY × style_frozen."""
    df = firm_year.copy()
    df["interact"] = df["PRiskFY"] * df["style_frozen"]
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
    print("Building H8 Political Risk Panel")
    print("=" * 60)

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        "size": SizeBuilder(var_config.get("size", {})),
        "lev": LevBuilder(var_config.get("lev", {})),
        "roa": ROABuilder(var_config.get("roa", {})),
        "tobins_q": TobinsQBuilder(var_config.get("tobins_q", {})),
        "investment_residual": InvestmentResidualBuilder(
            var_config.get("investment_residual", {})
        ),
        "prisk_fy": PRiskFYBuilder(var_config.get("prisk_fy", {})),
        "style_frozen": CEOClarityStyleBuilder(var_config.get("style_frozen", {})),
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

    # Coerce start_date to datetime64 UNCONDITIONALLY before fyearq attachment
    # and firm-year aggregation. aggregate_to_firm_year() sorts by start_date to
    # select the last call per (gvkey, fyearq); it must be datetime-comparable,
    # not a string — regardless of whether fyearq is already present.
    # This coercion is H8-specific because H8 is the only panel builder that
    # performs a downstream sort on start_date after attach_fyearq.
    # attach_fyearq() creates its own internal temp column and does NOT mutate
    # panel["start_date"] — so the coercion must be explicit here.
    # NOTE: Must be outside the fyearq guard — if attach_fyearq hits its
    # idempotency path (fyearq already present), start_date would otherwise
    # remain as object dtype and the downstream sort silently uses lexicographic
    # ordering (wrong for non-ISO or inconsistently formatted dates).
    panel["start_date"] = pd.to_datetime(panel["start_date"], errors="coerce")
    panel = attach_fyearq(panel, root_path)

    # Aggregate to firm-year
    print("\n  Aggregating to firm-year level...")
    firm_year = aggregate_to_firm_year(panel)
    print(f"  Firm-year observations: {len(firm_year):,}")

    # Create forward DV
    firm_year = create_lead_absabinv(firm_year)
    n_dv = firm_year["AbsAbInv_lead"].notna().sum()
    print(f"  AbsAbInv_lead (valid): {n_dv:,} / {len(firm_year):,}")

    # Create interaction
    firm_year = create_interaction(firm_year)

    # Assign industry sample (Main/Finance/Utility) for filtering
    if "ff12_code" in firm_year.columns:
        firm_year["sample"] = assign_industry_sample(firm_year["ff12_code"])

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    return firm_year


def save_outputs(firm_year: pd.DataFrame, stats: Dict[str, Any], out_dir: Path, root: Path, timestamp: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "h8_political_risk_panel.parquet"
    firm_year.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: h8_political_risk_panel.parquet "
        f"({len(firm_year):,} rows, {len(firm_year.columns)} columns)"
    )
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


def generate_report(
    firm_year: pd.DataFrame, stats: Dict[str, Any], out_dir: Path, duration: float
) -> None:
    n_dv = (
        firm_year["AbsAbInv_lead"].notna().sum()
        if "AbsAbInv_lead" in firm_year.columns
        else 0
    )
    n_interact = (
        firm_year["interact"].notna().sum() if "interact" in firm_year.columns else 0
    )
    report_lines = [
        "# Stage 3: H8 Political Risk Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary (Firm-Year Level)",
        f"- **Rows (firm-years):** {len(firm_year):,}",
        f"- **Columns:** {len(firm_year.columns)}",
        f"- **AbsAbInv_lead (DV, t+1, valid):** {n_dv:,}",
        f"- **Interaction term (valid):** {n_interact:,}",
        "",
    ]
    with open(out_dir / "report_step3_h8.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


def main(year_start: Optional[int] = None, year_end: Optional[int] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h8_political_risk_panel",
        "timestamp": timestamp,
        "variable_stats": [],
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h8_political_risk" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H8_PoliticalRisk",
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
    print("STAGE 3: Build H8 Political Risk × CEO Clarity Panel")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

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
