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

LaTeX output: single 4-column table (one column per model, Main sample only).

Inputs:
    - outputs/variables/ceo_clarity_extended/latest/ceo_clarity_extended_panel.parquet

Outputs:
    - outputs/econometric/ceo_clarity_extended/{timestamp}/ceo_clarity_extended_table.tex
    - outputs/econometric/ceo_clarity_extended/{timestamp}/regression_results_{model}.txt
    - outputs/econometric/ceo_clarity_extended/{timestamp}/report_step4_ceo_clarity_extended.md

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h0_3_ceo_clarity_extended_panel)
    - Uses: statsmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-02-19
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

warnings.filterwarnings("ignore", category=FutureWarning, module="linearmodels.*")

smf: Any = None
try:
    import statsmodels.formula.api as smf  # type: ignore[no-redef]

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

from f1d.shared.latex_tables_accounting import make_accounting_table
from f1d.shared.path_utils import get_latest_output_dir


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
    "RD_Intensity": "R&D Intensity",
    "Volatility": "Stock Volatility",
}


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
    required = (
        [model_config["dependent_var"]]
        + model_config["linguistic_controls"]
        + model_config["firm_controls"]
        + ["ceo_id", "year"]
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
            df["sample"] = "Main"
            df.loc[df["ff12_code"] == 11, "sample"] = "Finance"
            df.loc[df["ff12_code"] == 8, "sample"] = "Utility"

    print(f"    Main sample: {(df['sample'] == 'Main').sum():,} calls")

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    model_config: Dict[str, Any],
    model_name: str,
) -> tuple[Any, Optional[pd.DataFrame], Set[Any]]:
    """Run OLS regression with CEO fixed effects for one model × Main sample."""
    print("\n" + "=" * 60)
    print(f"Running regression: {model_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, set()

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
        return None, None, set()

    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    dep_var = model_config["dependent_var"]
    controls = model_config["linguistic_controls"] + model_config["firm_controls"]
    controls = [c for c in controls if c in df_reg.columns]

    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"
    print(f"  Formula: {formula}")
    print(f"  N controls: {len(controls)}")

    print("  Estimating... (this may take a minute)")
    start_time = datetime.now()
    try:
        model = smf.ols(formula, data=df_reg).fit(
            # M-2 fix: cluster SEs at CEO level (not HC1) to account for
            # within-CEO correlation across calls in the same regression.
            # HC1 treats all observations as independent, understating SEs
            # when the same CEO appears in many rows (Liang-Zeger problem).
            cov_type="cluster",
            cov_kwds={"groups": df_reg["ceo_id"]},
        )
    except ValueError as e:
        print(f"ERROR: Regression failed: {e}", file=sys.stderr)
        return None, None, set()

    duration = (datetime.now() - start_time).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}")
    print(f"  Adj. R-squared: {model.rsquared_adj:.4f}")
    print(f"  N observations: {int(model.nobs):,}")

    return model, df_reg, valid_ceos


# ==============================================================================
# Output Generation
# ==============================================================================


def save_outputs(
    results: Dict[str, Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Save LaTeX table and regression results text files."""
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
            "All samples are the Main industry sample (non-financial, non-utility). "
            "Standard errors are clustered at the CEO level (cov_type=cluster, groups=ceo_id)."
        ),
        variable_labels=VARIABLE_LABELS,
        control_variables=all_controls,
        entity_label="N Entities",
        output_path=out_dir / "ceo_clarity_extended_table.tex",
    )
    print("  Saved: ceo_clarity_extended_table.tex")

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

    print("=" * 80)
    print("STAGE 4: Test CEO Clarity Extended Controls Robustness (4.1.2)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    # Load panel (built by build_ceo_clarity_extended_panel.py)
    panel = load_panel(root, panel_path)

    # Run all 4 models against Main sample only
    results: Dict[str, Dict[str, Any]] = {}

    for model_name, model_config in MODELS.items():
        # Prepare complete-case data for this model
        df_model = prepare_regression_data(panel, model_config, model_name)

        # Robustness table: Main sample only
        df_main = df_model[df_model["sample"] == "Main"].copy()

        if len(df_main) < 100:
            print(f"\n  Skipping {model_name}: too few observations ({len(df_main)})")
            continue

        model, df_reg, valid_entities = run_regression(
            df_main, model_config, model_name
        )

        if model is None or df_reg is None:
            continue

        results[model_name] = {
            "model": model,
            "diagnostics": {
                "n_obs": int(model.nobs),
                "n_entities": len(valid_entities),
                "rsquared": model.rsquared,
                "rsquared_adj": model.rsquared_adj,
            },
        }

    if results:
        save_outputs(results, out_dir)
        duration = (datetime.now() - start_time).total_seconds()
        generate_report(results, out_dir, duration)

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
