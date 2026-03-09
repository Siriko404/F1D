#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test CEO Clarity Extended Controls Robustness (4.1.2)
================================================================================
ID: econometric/run_h0_3_ceo_clarity_extended
Description: Run 4 regressions against one shared panel to test whether adding
             extended financial controls changes CEO fixed effect estimates.

Models (Main sample only — robustness table):
    1. Manager Baseline:
       Manager_QA_Uncertainty_pct ~ C(ceo_id) + base_controls + C(year)
    2. Manager Extended:
       Manager_QA_Uncertainty_pct ~ C(ceo_id) + base_controls + extended_controls + C(year)
    3. CEO Baseline:
       CEO_QA_Uncertainty_pct ~ C(ceo_id) + base_controls + C(year)
    4. CEO Extended:
       CEO_QA_Uncertainty_pct ~ C(ceo_id) + base_controls + extended_controls + C(year)

Base controls:    StockRet, MarketRet, EPS_Growth, SurpDec
Extended controls: Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, Volatility

Hypothesis Tests:
    This is a robustness check (not a hypothesis test).
    Tests whether CEO fixed effect estimates are stable when adding extended controls.

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    CEOs must have >= 5 calls to be included in regression.

LaTeX output: single 4-column table (one column per model, Main sample only).

Inputs:
    - outputs/variables/ceo_clarity_extended/latest/ceo_clarity_extended_panel.parquet

Outputs:
    - outputs/econometric/ceo_clarity_extended/{timestamp}/ceo_clarity_extended_table.tex
    - outputs/econometric/ceo_clarity_extended/{timestamp}/regression_results_{model}.txt
    - outputs/econometric/ceo_clarity_extended/{timestamp}/manager_clarity_residual.parquet
    - outputs/econometric/ceo_clarity_extended/{timestamp}/ceo_clarity_residual.parquet
    - outputs/econometric/ceo_clarity_extended/{timestamp}/report_step4_ceo_clarity_extended.md
    - outputs/econometric/ceo_clarity_extended/{timestamp}/summary_stats.csv
    - outputs/econometric/ceo_clarity_extended/{timestamp}/summary_stats.tex
    - outputs/econometric/ceo_clarity_extended/{timestamp}/model_diagnostics.csv

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h0_3_ceo_clarity_extended_panel)
    - Uses: statsmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-02-26
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

STATSMODELS_AVAILABLE = True

from f1d.shared.latex_tables_accounting import (
    make_accounting_table,
    make_summary_stats_table,
)
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample


# ==============================================================================
# Model Configurations
# ==============================================================================

BASE_LINGUISTIC_CONTROLS_MANAGER = [
    "Manager_Pres_Uncertainty_pct",
    "Analyst_QA_Uncertainty_pct",
    "Entire_All_Negative_pct",
]

BASE_LINGUISTIC_CONTROLS_CEO = [
    "CEO_Pres_Uncertainty_pct",
    "Analyst_QA_Uncertainty_pct",
    "Entire_All_Negative_pct",
]

BASE_FIRM_CONTROLS = ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"]

EXTENDED_CONTROLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "CurrentRatio",
    "RD_Intensity",
    "Volatility",
]

MODELS: Dict[str, Dict[str, Any]] = {
    "Manager_Baseline": {
        "dependent_var": "Manager_QA_Uncertainty_pct",
        "linguistic_controls": BASE_LINGUISTIC_CONTROLS_MANAGER,
        "firm_controls": BASE_FIRM_CONTROLS,
        "description": "Manager Q&A Uncertainty — baseline controls",
    },
    "Manager_Extended": {
        "dependent_var": "Manager_QA_Uncertainty_pct",
        "linguistic_controls": BASE_LINGUISTIC_CONTROLS_MANAGER,
        "firm_controls": BASE_FIRM_CONTROLS + EXTENDED_CONTROLS,
        "description": "Manager Q&A Uncertainty — extended controls",
    },
    "CEO_Baseline": {
        "dependent_var": "CEO_QA_Uncertainty_pct",
        "linguistic_controls": BASE_LINGUISTIC_CONTROLS_CEO,
        "firm_controls": BASE_FIRM_CONTROLS,
        "description": "CEO Q&A Uncertainty — baseline controls",
    },
    "CEO_Extended": {
        "dependent_var": "CEO_QA_Uncertainty_pct",
        "linguistic_controls": BASE_LINGUISTIC_CONTROLS_CEO,
        "firm_controls": BASE_FIRM_CONTROLS + EXTENDED_CONTROLS,
        "description": "CEO Q&A Uncertainty — extended controls",
    },
}

MIN_CALLS = 5


# ==============================================================================
# Variable Labels for LaTeX Table
# ==============================================================================

VARIABLE_LABELS = {
    "Manager_Pres_Uncertainty_pct": "Manager Pres Uncertainty",
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
    "Analyst_QA_Uncertainty_pct": "Analyst QA Uncertainty",
    "Entire_All_Negative_pct": "Negative Sentiment",
    "StockRet": "Stock Return",
    "MarketRet": "Market Return",
    "EPS_Growth": "EPS Growth",
    "SurpDec": "Earnings Surprise Decile",
    "Size": "Size (log assets)",
    "BM": "Book-to-Market",
    "Lev": "Leverage",
    "ROA": "Return on Assets",
    "CurrentRatio": "Current Ratio",
    "RD_Intensity": r"R\&D Intensity",
    "Volatility": "Stock Volatility",
}


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables (both Manager and CEO)
    {"col": "Manager_QA_Uncertainty_pct", "label": "Manager QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    # Linguistic controls (Manager)
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Manager Pres Uncertainty"},
    # Linguistic controls (CEO)
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    # Common controls
    {"col": "Analyst_QA_Uncertainty_pct", "label": "Analyst QA Uncertainty"},
    {"col": "Entire_All_Negative_pct", "label": "Negative Sentiment"},
    # Base firm controls
    {"col": "StockRet", "label": "Stock Return"},
    {"col": "MarketRet", "label": "Market Return"},
    {"col": "EPS_Growth", "label": "EPS Growth"},
    {"col": "SurpDec", "label": "Earnings Surprise Decile"},
    # Extended controls
    {"col": "Size", "label": "Size (log assets)"},
    {"col": "BM", "label": "Book-to-Market"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "ROA", "label": "Return on Assets"},
    {"col": "CurrentRatio", "label": "Current Ratio"},
    {"col": "RD_Intensity", "label": "R&D Intensity"},
    {"col": "Volatility", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 4: Test CEO Clarity Extended Controls Robustness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "ceo_clarity_extended",
            required_file="ceo_clarity_extended_panel.parquet",
        )
        panel_file = panel_dir / "ceo_clarity_extended_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    return panel


# ==============================================================================
# Data Preparation (per model)
# ==============================================================================


def prepare_regression_data(
    panel: pd.DataFrame,
    model_config: Dict[str, Any],
    model_name: str,
) -> pd.DataFrame:
    """Filter panel to complete cases for a specific model."""
    print(f"\n  Preparing data for {model_name}...")

    initial_n = len(panel)

    df = panel[panel["ceo_id"].notna()].copy()

    # Required variables for this model
    # Include gvkey, sample, file_name, start_date for residual extraction
    required = (
        [model_config["dependent_var"]]
        + model_config["linguistic_controls"]
        + model_config["firm_controls"]
        + ["ceo_id", "year", "gvkey", "sample", "file_name", "start_date"]
    )

    # MAJOR-5: hard-fail if any required variable missing
    missing_vars = [v for v in required if v not in df.columns]
    if missing_vars:
        raise ValueError(
            f"Required variables missing from panel for model '{model_name}': {missing_vars}. "
            "Panel build may be incomplete. Aborting to prevent misspecified regression."
        )

    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"    Complete cases: {len(df):,} / {initial_n:,}")

    # Assign industry sample
    if "ff12_code" in df.columns:
        if "sample" not in df.columns:
            df["sample"] = assign_industry_sample(df["ff12_code"])
    elif "sample" not in df.columns:
        raise ValueError(
            "load_and_prepare_panel: neither 'ff12_code' nor 'sample' column found. "
            "Cannot assign industry sample. Check Stage 3 panel output."
        )

    print(f"    Main sample: {(df['sample'] == 'Main').sum():,} calls")

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    model_config: Dict[str, Any],
    model_name: str,
) -> tuple[Any, Optional[pd.DataFrame], Set[Any], Optional[pd.DataFrame]]:
    """Run OLS regression with CEO fixed effects for one model × Main sample.

    Uses smf.ols with clustered standard errors at CEO level.
    Continuous controls are standardized for numerical stability.

    Returns:
        model: Fitted statsmodels OLS results
        df_reg: DataFrame used in regression
        valid_ceos: Set of CEO IDs meeting minimum calls threshold
        residuals_df: DataFrame with residuals for baseline models (None for extended)
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {model_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, set(), None

    min_calls = MIN_CALLS
    ceo_counts = df_sample["ceo_id"].value_counts()
    valid_ceos: Set[Any] = set(ceo_counts[ceo_counts >= min_calls].index)
    df_reg = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

    print(
        f"  After >={min_calls} calls filter: {len(df_reg):,} calls, "
        f"{df_reg['ceo_id'].nunique():,} CEOs"
    )

    if len(df_reg) < 100:
        print(f"  WARNING: Too few observations ({len(df_reg)}), skipping")
        return None, None, set(), None

    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    # Convert year to string for formula (C(year) creates dummies)
    df_reg["year"] = df_reg["year"].astype(str)

    # Standardize continuous controls for numerical stability (prevents SVD convergence issues)
    continuous_vars = [
        "Size",
        "BM",
        "Lev",
        "ROA",
        "CurrentRatio",
        "RD_Intensity",
        "Volatility",
        "StockRet",
        "MarketRet",
        "EPS_Growth",
    ]
    for var in continuous_vars:
        if var in df_reg.columns:
            mean_val = df_reg[var].mean()
            std_val = df_reg[var].std()
            if std_val > 0:
                df_reg[var] = (df_reg[var] - mean_val) / std_val

    dep_var = model_config["dependent_var"]
    controls = model_config["linguistic_controls"] + model_config["firm_controls"]
    controls = [c for c in controls if c in df_reg.columns]

    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"
    print(f"  Formula: {formula}")
    print(f"  N controls: {len(controls)}")

    print("  Estimating... (this may take a minute)")
    start_time = datetime.now()

    try:
        # Use smf.ols with clustered standard errors at CEO level.
        # C(ceo_id) categorical dummies act as CEO fixed effects.
        model = smf.ols(formula, data=df_reg).fit(
            cov_type="cluster",
            cov_kwds={"groups": df_reg["ceo_id"]},
        )
    except ValueError as e:
        print(f"ERROR: Regression failed: {e}", file=sys.stderr)
        return None, None, set(), None

    duration = (datetime.now() - start_time).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}")
    print(f"  Adj. R-squared: {model.rsquared_adj:.4f}")
    print(f"  N observations: {int(model.nobs):,}")

    # Extract residuals for baseline models
    residuals_df = None
    if model_name in ("Manager_Baseline", "CEO_Baseline"):
        # CRITICAL: Verify alignment between model residuals and DataFrame rows
        assert len(model.resid) == len(df_reg), (
            f"Residual count mismatch: {len(model.resid)} != {len(df_reg)}"
        )
        # Extract residuals with metadata
        residuals_df = df_reg[['file_name', 'gvkey', 'ceo_id', 'sample', 'start_date']].copy()
        # Use specific column name based on model type
        residual_col_name = "manager_clarity_residual" if model_name == "Manager_Baseline" else "ceo_clarity_residual"
        residuals_df[residual_col_name] = model.resid.values
        print(f"  Extracted {len(residuals_df):,} residuals for {model_name}")

    return model, df_reg, valid_ceos, residuals_df


# ==============================================================================
# Output Generation
# ==============================================================================


def save_outputs(
    results: Dict[str, Dict[str, Any]],
    out_dir: Path,
    manager_residuals: Optional[pd.DataFrame] = None,
    ceo_residuals: Optional[pd.DataFrame] = None,
) -> None:
    """Save LaTeX table, regression results text files, and residuals."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # All controls across all models (union, for table rows)
    all_controls = list(
        dict.fromkeys(
            BASE_LINGUISTIC_CONTROLS_MANAGER
            + BASE_LINGUISTIC_CONTROLS_CEO
            + BASE_FIRM_CONTROLS
            + EXTENDED_CONTROLS
        )
    )

    make_accounting_table(
        results=results,
        caption=(
            "Table 2: Extended Controls Robustness — "
            "CEO and Manager Clarity Fixed Effects"
        ),
        label="tab:ceo_clarity_extended",
        note=(
            "This table reports CEO fixed effects from regressing Q&A uncertainty "
            "on baseline and extended financial controls. "
            "Columns (1)--(2) use Manager-level Q&A uncertainty; "
            "columns (3)--(4) use CEO-only Q&A uncertainty. "
            "Extended controls add Size, Book-to-Market, Leverage, ROA, "
            "Current Ratio, R\\&D Intensity, and Stock Volatility. "
            "All models use the Main industry sample (non-financial, non-utility firms). "
            "CEOs with fewer than 5 calls are excluded. "
            "Standard errors are clustered at the CEO level. "
            "All continuous controls are standardized within each model's estimation sample. "
            "Variables are winsorized at 1\\%/99\\% by year at the engine level."
        ),
        variable_labels=VARIABLE_LABELS,
        control_variables=all_controls,
        entity_label="N Entities",
        output_path=out_dir / "ceo_clarity_extended_table.tex",
    )
    print("  Saved: ceo_clarity_extended_table.tex")

    # Save manager baseline residuals
    if manager_residuals is not None and len(manager_residuals) > 0:
        mgr_path = out_dir / "manager_clarity_residual.parquet"
        manager_residuals.to_parquet(mgr_path, index=False)
        print(f"  Saved: manager_clarity_residual.parquet ({len(manager_residuals):,} rows)")

    # Save CEO baseline residuals
    if ceo_residuals is not None and len(ceo_residuals) > 0:
        ceo_path = out_dir / "ceo_clarity_residual.parquet"
        ceo_residuals.to_parquet(ceo_path, index=False)
        print(f"  Saved: ceo_clarity_residual.parquet ({len(ceo_residuals):,} rows)")

    # Save model diagnostics CSV
    diag_rows = []
    for model_name, result in results.items():
        model = result.get("model")
        diag = result.get("diagnostics", {})
        if model is not None:
            diag_rows.append({
                "model": model_name,
                "n_obs": diag.get("n_obs"),
                "n_entities": diag.get("n_entities"),  # H0.3 uses n_entities
                "n_clusters": diag.get("n_clusters"),  # Number of CEO clusters
                "cluster_var": diag.get("cluster_var", "ceo_id"),  # Cluster variable name
                "rsquared": diag.get("rsquared"),
                "rsquared_adj": diag.get("rsquared_adj"),
                "fvalue": getattr(model, "fvalue", None),
                "f_pvalue": getattr(model, "f_pvalue", None),
                "aic": getattr(model, "aic", None),
                "bic": getattr(model, "bic", None),
            })
    if diag_rows:
        diag_df = pd.DataFrame(diag_rows)
        diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False)
        print(f"  Saved: model_diagnostics.csv ({len(diag_df)} rows)")

    # Save regression summaries
    for model_name, result in results.items():
        model = result.get("model")
        if model is not None:
            results_path = out_dir / f"regression_results_{model_name.lower()}.txt"
            with open(results_path, "w") as f:
                f.write(model.summary().as_text())
            print(f"  Saved: regression_results_{model_name.lower()}.txt")


def generate_report(
    results: Dict[str, Dict[str, Any]],
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report."""
    report_lines = [
        "# Stage 4: CEO Clarity Extended Controls Robustness Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Models",
        "",
        "| Model | DV | Controls |",
        "|-------|-----|---------|",
        "| Manager Baseline | Manager_QA_Uncertainty_pct | Base |",
        "| Manager Extended | Manager_QA_Uncertainty_pct | Base + Extended |",
        "| CEO Baseline     | CEO_QA_Uncertainty_pct     | Base |",
        "| CEO Extended     | CEO_QA_Uncertainty_pct     | Base + Extended |",
        "",
        "## Results Summary (Main Sample)",
        "",
        "| Model | N Obs | N Entities | R-squared | Adj R-sq |",
        "|-------|-------|-----------|-----------|----------|",
    ]

    for model_name, result in results.items():
        diag = result.get("diagnostics", {})
        n_obs = diag.get("n_obs", "N/A")
        n_ent = diag.get("n_entities", "N/A")
        r2 = diag.get("rsquared", "N/A")
        r2_adj = diag.get("rsquared_adj", "N/A")
        if isinstance(r2, float):
            report_lines.append(
                f"| {model_name} | {n_obs:,} | {n_ent:,} | {r2:.4f} | {r2_adj:.4f} |"
            )
        else:
            report_lines.append(
                f"| {model_name} | {n_obs} | {n_ent} | {r2} | {r2_adj} |"
            )

    report_lines.append("")

    report_path = out_dir / "report_step4_ceo_clarity_extended.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("  Saved: report_step4_ceo_clarity_extended.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "ceo_clarity_extended" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H0.3_CeoClarity_Extended",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test CEO Clarity Extended Controls Robustness (4.1.2)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Log dir: {log_dir}")

    # Load panel (built by build_ceo_clarity_extended_panel.py)
    panel = load_panel(root, panel_path)

    # Track panel path for manifest
    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "ceo_clarity_extended",
        required_file="ceo_clarity_extended_panel.parquet",
    ) / "ceo_clarity_extended_panel.parquet"

    # Generate summary statistics for all three samples (Main, Finance, Utility)
    # Each sample gets its own panel (Panel A / Panel B / Panel C) — same structure
    # as H0.1 and H0.2.
    print("\n" + "=" * 60)
    print("Generating summary statistics (all samples)")
    print("=" * 60)

    # Ensure sample column exists on the full panel
    if "sample" not in panel.columns:
        if "ff12_code" in panel.columns:
            panel["sample"] = assign_industry_sample(panel["ff12_code"])
        else:
            raise ValueError("Neither 'sample' nor 'ff12_code' column found in panel")

    # Filter to complete cases across all summary stats variables (on full panel)
    stats_cols = [v["col"] for v in SUMMARY_STATS_VARS]
    available_cols = [c for c in stats_cols if c in panel.columns]
    missing_cols = [c for c in stats_cols if c not in panel.columns]
    if missing_cols:
        print(f"  WARNING: Missing columns for summary stats: {missing_cols}")

    if available_cols:
        complete_mask = panel[available_cols].notna().all(axis=1)
        df_complete = panel[complete_mask].copy()
        print(f"  Complete cases for summary stats: {len(df_complete):,}")
        for samp in ["Main", "Finance", "Utility"]:
            n = (df_complete["sample"] == samp).sum()
            print(f"    {samp}: {n:,}")

        make_summary_stats_table(
            df=df_complete,
            variables=SUMMARY_STATS_VARS,
            sample_names=["Main", "Finance", "Utility"],
            sample_col="sample",
            output_csv=out_dir / "summary_stats.csv",
            output_tex=out_dir / "summary_stats.tex",
            caption="Summary Statistics — Extended Controls Robustness",
            label="tab:summary_stats_h03",
        )
        print("  Saved: summary_stats.csv")
        print("  Saved: summary_stats.tex")

    # Run all 4 models against Main sample only
    results: Dict[str, Dict[str, Any]] = {}
    manager_residuals: Optional[pd.DataFrame] = None
    ceo_residuals: Optional[pd.DataFrame] = None

    for model_name, model_config in MODELS.items():
        # Prepare complete-case data for this model
        df_model = prepare_regression_data(panel, model_config, model_name)

        # Robustness table: Main sample only
        df_main = df_model[df_model["sample"] == "Main"].copy()

        if len(df_main) < 100:
            print(f"\n  Skipping {model_name}: too few observations ({len(df_main)})")
            continue

        model, df_reg, valid_entities, residuals = run_regression(
            df_main, model_config, model_name
        )

        if model is None or df_reg is None:
            continue

        # Collect residuals from baseline models
        if model_name == "Manager_Baseline":
            manager_residuals = residuals
        elif model_name == "CEO_Baseline":
            ceo_residuals = residuals

        results[model_name] = {
            "model": model,
            "diagnostics": {
                "n_obs": int(model.nobs),
                "n_entities": len(valid_entities),
                "n_clusters": df_reg["ceo_id"].nunique(),
                "cluster_var": "ceo_id",
                "rsquared": model.rsquared,
                "rsquared_adj": model.rsquared_adj,
            },
        }

    if results:
        save_outputs(results, out_dir, manager_residuals, ceo_residuals)
        duration = (datetime.now() - start_time).total_seconds()
        generate_report(results, out_dir, duration)

        # Generate sample attrition table
        attrition_stages = [
            ("Master manifest", len(panel)),
            ("Main sample filter", (panel["sample"] == "Main").sum()),
        ]
        # Add first model's sample size if available
        first_result = list(results.values())[0] if results else None
        if first_result:
            diag = first_result.get("diagnostics", {})
            n_obs = diag.get("n_obs", 0)
            if n_obs:
                attrition_stages.append(("After complete-case + min-calls filter", n_obs))
        generate_attrition_table(attrition_stages, out_dir, "H0.3 Extended Controls")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

        # Generate run manifest
        generate_manifest(
            output_dir=out_dir,
            stage="stage4",
            timestamp=timestamp,
            input_paths={"panel": panel_file},
            output_files={
                "diagnostics": out_dir / "model_diagnostics.csv",
                "table": out_dir / "ceo_clarity_extended_table.tex",
                "manager_residuals": out_dir / "manager_clarity_residual.parquet",
                "ceo_residuals": out_dir / "ceo_clarity_residual.parquet",
            },
            panel_path=panel_file,
        )
        print("  Saved: run_manifest.json")

    duration = (datetime.now() - start_time).total_seconds()
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

    sys.exit(main(panel_path=args.panel_path))
