#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build H24 / H24b / H25 — Macro Uncertainty Shared Panel
================================================================================
ID: variables/build_h24_h24b_h25_macro_uncertainty_panel
Description: Build CALL-LEVEL panel for the H24 / H24b / H25 macro uncertainty
             suites. One shared panel feeds three runners (H24 = US EPU,
             H24b = GEPU, H25 = GPR). The runners only differ by which macro
             IV column they select from this panel.

    Step 1: Load manifest + all call-level variables (linguistic DVs + finance
            controls + macro uncertainty IVs).
    Step 2: Merge everything onto manifest by file_name (zero row-delta enforced).
    Step 3: Derive calendar year / quarter / year-quarter index from call start_date.
    Step 4: Build call-level next-quarter leads for the 4 uncertainty DVs
            (via create_next_quarter_lead on calendar-time).
    Step 5: Build call-level prior-quarter lags for the 4 uncertainty DVs
            (Lagged_DV controls; standing pipeline rule).
    Step 6: Assign industry sample (Main / Finance / Utility).
    Step 7: Save shared call-level panel.

Unit of observation: the individual earnings call (file_name).

Temporal Structure:
    Macro IVs (GPR, US_EPU, GEPU_current and log variants) are matched to each
    call by the calendar month of the call's start_date — NO aggregation, NO
    lag. Identification variance is preserved within quarter; downstream
    runners rely on firm FE with two-way clustering (firm, cal_yr_qtr) to
    handle the common macro shock without absorbing the IV through time FE.

    Lead DVs:
        {UncAns,UncPre}{Mgr,CEO}_lead1  — next calendar quarter's (latest) call
    Lag DV controls (standing rule):
        {UncAns,UncPre}{Mgr,CEO}_lag    — prior calendar quarter's (latest) call

Downstream suites:
    H24  — US EPU         (IV: US_EPU_log)   — BBD 2016
    H24b — Global EPU     (IV: GEPU_log)     — Davis 2016
    H25  — Geopolitical R (IV: GPR_log)      — Caldara & Iacoviello 2022

Outputs:
    - outputs/variables/h24_h24b_h25_macro/{timestamp}/h24_h24b_h25_macro_panel.parquet
    - outputs/variables/h24_h24b_h25_macro/{timestamp}/summary_stats.csv
    - outputs/variables/h24_h24b_h25_macro/{timestamp}/run_manifest.json
    - outputs/variables/h24_h24b_h25_macro/{timestamp}/report_step3_h24_h24b_h25.md

Author: Thesis Author
Date: 2026-04-09
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
from f1d.shared.variables.panel_utils import (
    assign_industry_sample,
    build_cal_yr_qtr_index,
    create_next_quarter_lead,
    create_prior_quarter_lag,
)
from f1d.shared.variables import (
    # Dependent variables (4 uncertainty measures — per H11 convention)
    ManagerQAUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    ManagerPresUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    NonCEOManagerQAUncertaintyBuilder,
    NonCEOManagerPresUncertaintyBuilder,
    # Main Independent Variable — aggregate monthly macro series
    MacroUncertaintyBuilder,
    # Linguistic controls
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    # Finance controls (H11 set)
    SizeBuilder,
    BookLevBuilder,
    ROABuilder,
    TobinsQBuilder,
    CashHoldingsBuilder,
    DividendPayerBuilder,
    FirmMaturityBuilder,
    EarningsVolatilityBuilder,
    # Manifest
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 3: Build H24/H24b/H25 Macro Uncertainty Shared Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


# ==============================================================================
# Panel construction
# ==============================================================================

# Base uncertainty DVs — used for lead/lag construction and final column list
# Note: 2026-04-19 — extended with UncAnsNoCEO + UncPreNoCEO for partition-variant
# DV-side rollout (per BLOCKER B1 fix in plan). Without this extension, the
# create_next_quarter_lead and create_prior_quarter_lag calls would not produce
# `_lead`/`_lag` columns for the new NoCEO DVs, causing KeyError when the
# DV-side runners (run_h24_us_epu, etc.) try `df[f"{dv_var}_lag"]`.
UNCERTAINTY_DVS = ["UncAnsMgr", "UncPreMgr", "UncAnsCEO", "UncPreCEO", "UncAnsNoCEO", "UncPreNoCEO"]


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Building H24/H24b/H25 Macro Uncertainty Panel")
    print("=" * 60)

    builders = {
        # Manifest (file_name, gvkey, start_date, ff12_code, ...)
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        # Dependent Variables (4 uncertainty measures)
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
        "nonceo_manager_qa_uncertainty": NonCEOManagerQAUncertaintyBuilder(
            var_config.get("nonceo_manager_qa_uncertainty", {})
        ),
        "nonceo_manager_pres_uncertainty": NonCEOManagerPresUncertaintyBuilder(
            var_config.get("nonceo_manager_pres_uncertainty", {})
        ),
        # Main Independent Variables — 3 monthly macro series matched by calendar month
        # Single builder emits GPR, US_EPU, GEPU_current + their log variants
        "macro_uncertainty": MacroUncertaintyBuilder(
            var_config.get("macro_uncertainty_gpr", {})
        ),
        # Linguistic controls
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(
            var_config.get("analyst_qa_uncertainty", {})
        ),
        "negative_sentiment": NegativeSentimentBuilder(
            var_config.get("negative_sentiment", {})
        ),
        # Finance controls (H11 set)
        "size": SizeBuilder(var_config.get("size", {})),
        "lev": BookLevBuilder(var_config.get("lev", {})),
        "roa": ROABuilder(var_config.get("roa", {})),
        "tobins_q": TobinsQBuilder(var_config.get("tobins_q", {})),
        "cash_holdings": CashHoldingsBuilder(var_config.get("cash_holdings", {})),
        "dividend_payer": DividendPayerBuilder(var_config.get("dividend_payer", {})),
        "FirmMat": FirmMaturityBuilder(var_config.get("FirmMat", {})),
        "EarnVol": EarningsVolatilityBuilder(var_config.get("EarnVol", {})),
    }

    all_results: Dict[str, Any] = {}
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
            data = data.drop(columns=conflicting)

        before_len = len(panel)
        panel = panel.merge(data, on="file_name", how="left")
        after_len = len(panel)
        delta = after_len - before_len
        if delta != 0:
            raise ValueError(
                f"Merge '{name}' changed rows {before_len} -> {after_len}"
            )
        print(f"  After {name} merge: {after_len:,} rows (delta: {delta:+d})")

    # Calendar derivations
    panel["sample"] = assign_industry_sample(panel["ff12_code"])
    panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Build calendar year / quarter / year-quarter index — needed for:
    #   1. Downstream PanelOLS time dimension (two-way cluster via cal_yr_qtr)
    #   2. create_next_quarter_lead / create_prior_quarter_lag validators
    panel = build_cal_yr_qtr_index(panel)

    # --- Lead construction (next calendar quarter's call) ---
    print("\n" + "=" * 60)
    print("Creating call-level next-quarter leads for 4 uncertainty DVs")
    print("=" * 60)
    panel = create_next_quarter_lead(panel, UNCERTAINTY_DVS)

    # --- Lag construction (prior calendar quarter's call — for Lagged_DV controls) ---
    print("\n" + "=" * 60)
    print("Creating call-level prior-quarter lags for 4 uncertainty DVs")
    print("=" * 60)
    panel = create_prior_quarter_lag(panel, UNCERTAINTY_DVS)

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]

    # --- Diagnostics: macro match rates, lead/lag coverage ---
    print("\n" + "=" * 60)
    print("Match & coverage diagnostics")
    print("=" * 60)
    n_total = len(panel)
    print(f"  Panel rows: {n_total:,}")

    print("  Macro IV match rates (should be ~100% for thesis window 2002-2018):")
    for col in ["GPR", "US_EPU", "GEPU_current", "GPR_log", "US_EPU_log", "GEPU_log"]:
        if col in panel.columns:
            n_match = panel[col].notna().sum()
            pct = 100.0 * n_match / n_total if n_total else 0.0
            print(f"    {col:15s}: {n_match:,}/{n_total:,} ({pct:.1f}%)")
        else:
            print(f"    {col:15s}: MISSING FROM PANEL")

    print("  Lead1 coverage (typical ~80% — last call per firm drops out):")
    for col in UNCERTAINTY_DVS:
        lead_col = f"{col}_lead1"
        if lead_col in panel.columns:
            n_match = panel[lead_col].notna().sum()
            pct = 100.0 * n_match / n_total if n_total else 0.0
            print(f"    {lead_col:20s}: {n_match:,}/{n_total:,} ({pct:.1f}%)")
        else:
            print(f"    {lead_col:20s}: MISSING FROM PANEL")

    print("  Lag coverage (typical ~80% — first call per firm drops out):")
    for col in UNCERTAINTY_DVS:
        lag_col = f"{col}_lag"
        if lag_col in panel.columns:
            n_match = panel[lag_col].notna().sum()
            pct = 100.0 * n_match / n_total if n_total else 0.0
            print(f"    {lag_col:20s}: {n_match:,}/{n_total:,} ({pct:.1f}%)")
        else:
            print(f"    {lag_col:20s}: MISSING FROM PANEL")

    # Log macro build metadata from MacroUncertaintyBuilder (if provided)
    macro_result = all_results.get("macro_uncertainty")
    if macro_result and getattr(macro_result, "metadata", None):
        meta = macro_result.metadata
        print(
            f"\n  MacroUncertaintyBuilder metadata: n_total={meta.get('n_total', 'N/A')}"
        )

    return panel


def save_outputs(
    panel: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
    root: Path,
    timestamp: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = out_dir / "h24_h24b_h25_macro_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(
        f"\n  Saved: h24_h24b_h25_macro_panel.parquet "
        f"({len(panel):,} rows, {len(panel.columns)} columns)"
    )

    stats_df = stats_list_to_dataframe(
        [s for s in stats.get("variable_stats", [])]
    )
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")

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
    panel: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
    duration: float,
) -> None:
    macro_cols = ["GPR", "US_EPU", "GEPU_current", "GPR_log", "US_EPU_log", "GEPU_log"]
    lead_cols = [f"{c}_lead1" for c in UNCERTAINTY_DVS]
    lag_cols = [f"{c}_lag" for c in UNCERTAINTY_DVS]
    n = len(panel)

    def _match(col: str) -> str:
        if col not in panel.columns:
            return "MISSING"
        k = int(panel[col].notna().sum())
        return f"{k:,}/{n:,} ({100 * k / max(n, 1):.1f}%)"

    report_lines = [
        "# Stage 3: H24 / H24b / H25 Macro Uncertainty Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary",
        f"- **Rows:** {len(panel):,}",
        f"- **Columns:** {len(panel.columns)}",
        "",
        "## Macro IV match rates (calendar-month lookup)",
    ]
    for col in macro_cols:
        report_lines.append(f"- `{col}`: {_match(col)}")
    report_lines.extend(
        [
            "",
            "## Next-quarter lead coverage (`*_lead1`)",
        ]
    )
    for col in lead_cols:
        report_lines.append(f"- `{col}`: {_match(col)}")
    report_lines.extend(
        [
            "",
            "## Prior-quarter lag coverage (`*_lag`, for Lagged_DV control)",
        ]
    )
    for col in lag_cols:
        report_lines.append(f"- `{col}`: {_match(col)}")
    report_lines.extend(
        [
            "",
            "## Model Specifications (downstream runners)",
            "",
            "| Suite | IV | Paper |",
            "|---|---|---|",
            "| H24  | `US_EPU_log` | Baker, Bloom & Davis (2016, QJE)   |",
            "| H24b | `GEPU_log`   | Davis (2016, NBER WP 22740)        |",
            "| H25  | `GPR_log`    | Caldara & Iacoviello (2022, AER)   |",
            "",
            "All runners share this panel. Panel index is `(gvkey, cal_yr_qtr)`, "
            "FE are firm-only (EntityEffects, NO TimeEffects — would absorb the "
            "macro IV), SEs two-way clustered (firm, cal_yr_qtr).",
            "",
            "## Temporal Structure",
            "- Macro IV: calendar month of call (no aggregation, no lag)",
            "- `*_lead1`: next calendar quarter's (latest) call by start_date, "
            "validated to be strictly the next consecutive calendar quarter",
            "- `*_lag`: prior calendar quarter's (latest) call, same validator",
            "",
        ]
    )
    report_path = out_dir / "report_step3_h24_h24b_h25.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  Saved: {report_path.name}")


def main(
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_h24_h24b_h25_macro_uncertainty_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "h24_h24b_h25_macro" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H24_H24b_H25_MacroUncertainty",
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
    print("STAGE 3: Build H24 / H24b / H25 Macro Uncertainty Panel")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Years:     {year_start}-{year_end}")

    panel = build_panel(root, years, var_config, stats)
    save_outputs(panel, stats, out_dir, root, timestamp)

    duration = (datetime.now() - start_time).total_seconds()
    generate_report(panel, stats, out_dir, duration)

    print(f"\nCOMPLETE in {duration:.1f}s")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("DRY-RUN mode -- validating inputs only")
        print("DRY-RUN complete.")
        sys.exit(0)
    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
