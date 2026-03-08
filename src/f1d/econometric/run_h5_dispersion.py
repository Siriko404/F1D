#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H5 Analyst Dispersion Hypothesis
================================================================================
ID: econometric/test_h5_dispersion
Description: Run H5 Analyst Dispersion hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample, and outputting results.

Model A (Uncertainty → Dispersion) — 4 regressions per sample:
    A1: dispersion ~ CEO_QA_Uncertainty_pct + Controls + lagged_dispersion + FirmFE + YearFE
    A2: dispersion ~ CEO_Pres_Uncertainty_pct + Controls + lagged_dispersion + FirmFE + YearFE
    A3: dispersion ~ Manager_QA_Uncertainty_pct + Controls + lagged_dispersion + FirmFE + YearFE
    A4: dispersion ~ Manager_Pres_Uncertainty_pct + Controls + lagged_dispersion + FirmFE + YearFE

Model B (Gaps → Dispersion) — 4 regressions per sample:
    B1: dispersion ~ CEO_Pres_QA_Gap + Controls + lagged_dispersion + FirmFE + YearFE
    B2: dispersion ~ Mgr_Pres_QA_Gap + Controls + lagged_dispersion + FirmFE + YearFE
    B3: dispersion ~ CEO_Mgr_QA_Gap + Controls + lagged_dispersion + FirmFE + YearFE
    B4: dispersion ~ CEO_Mgr_Pres_Gap + Controls + lagged_dispersion + FirmFE + YearFE

Gap Definitions (Pres - QA, positive = more uncertain in prepared remarks):
    CEO_Pres_QA_Gap = CEO_Pres_Uncertainty_pct - CEO_QA_Uncertainty_pct
    Mgr_Pres_QA_Gap = Manager_Pres_Uncertainty_pct - Manager_QA_Uncertainty_pct
    CEO_Mgr_QA_Gap = CEO_QA_Uncertainty_pct - Manager_QA_Uncertainty_pct (regime gap)
    CEO_Mgr_Pres_Gap = CEO_Pres_Uncertainty_pct - Manager_Pres_Uncertainty_pct (regime gap)

Control Variables:
    Linguistic: Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct
    Financial: Size, Lev, TobinsQ, earnings_volatility, earnings_surprise_ratio, loss_dummy
    Lagged DV: lagged_dispersion

Total: 24 regressions (8 specs × 3 samples)

Hypothesis Tests (one-tailed):
    H5-A: beta(Uncertainty) > 0 (higher uncertainty -> higher dispersion)
    H5-B: beta(Gap) > 0 (positive gap = more rehearsed uncertainty -> higher dispersion)

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls to be included in regression.

Inputs:
    - outputs/variables/h5_dispersion/latest/h5_dispersion_panel.parquet

Outputs:
    - outputs/econometric/h5_dispersion/{timestamp}/regression_results_{sample}_{spec}.txt
    - outputs/econometric/h5_dispersion/{timestamp}/h5_dispersion_table.tex
    - outputs/econometric/h5_dispersion/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h5_dispersion/{timestamp}/summary_stats.csv
    - outputs/econometric/h5_dispersion/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h5_dispersion_panel)
    - Uses: statsmodels, linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-03-08
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf  # type: ignore[import]
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample

# Silence statsmodels covariance warnings
warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)

CONFIG = {
    "min_calls": 5,
    "samples": ["Main", "Finance", "Utility"],
}

# ==============================================================================
# Model Specifications
# ==============================================================================

# Model A: Uncertainty measures (4 specs)
MODEL_A_SPECS = [
    ("A1", "CEO_QA_Uncertainty_pct", "CEO QA Uncertainty"),
    ("A2", "CEO_Pres_Uncertainty_pct", "CEO Pres Uncertainty"),
    ("A3", "Manager_QA_Uncertainty_pct", "Manager QA Uncertainty"),
    ("A4", "Manager_Pres_Uncertainty_pct", "Manager Pres Uncertainty"),
]

# Model B: Gap measures (4 specs)
# Gap direction: Pres - QA (positive = more uncertain in prepared remarks)
MODEL_B_SPECS = [
    ("B1", "CEO_Pres_QA_Gap", "CEO Pres-QA Gap", "CEO_Pres_Uncertainty_pct - CEO_QA_Uncertainty_pct"),
    ("B2", "Mgr_Pres_QA_Gap", "Mgr Pres-QA Gap", "Manager_Pres_Uncertainty_pct - Manager_QA_Uncertainty_pct"),
    ("B3", "CEO_Mgr_QA_Gap", "CEO-Mgr QA Gap", "CEO_QA_Uncertainty_pct - Manager_QA_Uncertainty_pct"),
    ("B4", "CEO_Mgr_Pres_Gap", "CEO-Mgr Pres Gap", "CEO_Pres_Uncertainty_pct - Manager_Pres_Uncertainty_pct"),
]

# Base controls (common to all specs)
BASE_CONTROLS = [
    "Analyst_QA_Uncertainty_pct",
    "Entire_All_Negative_pct",
    "Size",
    "Lev",
    "TobinsQ",
    "earnings_volatility",
    "earnings_surprise_ratio",
    "loss_dummy",
    "lagged_dispersion",  # Lagged DV for persistence
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variable
    {"col": "dispersion", "label": "Analyst Dispersion$_{t}$"},
    # Lagged DV
    {"col": "lagged_dispersion", "label": "Lagged Dispersion"},
    # Model A: Uncertainty measures
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    # Model B: Gap measures (computed)
    {"col": "CEO_Pres_QA_Gap", "label": "CEO Pres-QA Gap"},
    {"col": "Mgr_Pres_QA_Gap", "label": "Mgr Pres-QA Gap"},
    {"col": "CEO_Mgr_QA_Gap", "label": "CEO-Mgr QA Gap"},
    {"col": "CEO_Mgr_Pres_Gap", "label": "CEO-Mgr Pres Gap"},
    # Controls
    {"col": "Analyst_QA_Uncertainty_pct", "label": "Analyst QA Uncertainty"},
    {"col": "Entire_All_Negative_pct", "label": "Entire Call Negative"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "earnings_volatility", "label": "Earnings Volatility"},
    {"col": "earnings_surprise_ratio", "label": "Earnings Surprise Ratio"},
    {"col": "loss_dummy", "label": "Loss Dummy"},
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H5 Analyst Dispersion Hypothesis (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H5 panel parquet"
    )
    return parser.parse_args()


def prepare_regression_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Compute gap measures for Model B specs.

    Gap direction: Pres - QA (positive = more uncertain in prepared remarks)
    Regime gaps: CEO - Manager (positive = CEO more uncertain than team)
    """
    df = panel.copy()

    # Pres-QA gaps (positive = more uncertain in prepared remarks)
    df["CEO_Pres_QA_Gap"] = df["CEO_Pres_Uncertainty_pct"] - df["CEO_QA_Uncertainty_pct"]
    df["Mgr_Pres_QA_Gap"] = df["Manager_Pres_Uncertainty_pct"] - df["Manager_QA_Uncertainty_pct"]

    # Regime gaps: CEO - Manager (positive = CEO more uncertain than broader team)
    df["CEO_Mgr_QA_Gap"] = df["CEO_QA_Uncertainty_pct"] - df["Manager_QA_Uncertainty_pct"]
    df["CEO_Mgr_Pres_Gap"] = df["CEO_Pres_Uncertainty_pct"] - df["Manager_Pres_Uncertainty_pct"]

    return df


def run_regression(
    df_sample: pd.DataFrame,
    spec_id: str,
    key_iv: str,
    sample_name: str,
    model_type: str,  # "A" or "B"
) -> Tuple[Any, Dict[str, Any]]:
    """Run a single regression specification.

    Args:
        df_sample: Filtered sample data
        spec_id: Specification ID (e.g., "A1", "B3")
        key_iv: Key independent variable name
        sample_name: Sample name (Main, Finance, Utility)
        model_type: "A" for uncertainty, "B" for gaps

    Returns:
        Tuple of (model, metadata dict)
    """
    controls = list(BASE_CONTROLS)

    # Required columns: DV, key IV, controls, FE vars
    required = ["dispersion", key_iv] + controls + ["gvkey", "year"]
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    if len(df_reg) < 100:
        return None, {}

    # Build formula
    formula_parts = [key_iv] + controls
    formula = "dispersion ~ " + " + ".join(formula_parts)

    print(f"  Formula: {formula} + EntityEffects + TimeEffects")
    print(f"  N calls: {len(df_reg):,}  |  N firms: {df_reg['gvkey'].nunique():,}")
    print("  Estimating with firm-clustered SEs... (this may take a moment)")

    t0 = datetime.now()

    # Convert to multi-index for PanelOLS
    df_reg["gvkey_cat"] = df_reg["gvkey"].astype("category")
    df_reg["year_cat"] = df_reg["year"].astype("category")
    df_panel = df_reg.set_index(["gvkey", "year"])

    try:
        formula_panel = formula + " + EntityEffects + TimeEffects"
        model_obj = PanelOLS.from_formula(formula_panel, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: PanelOLS Regression failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared (within): {model.rsquared_within:.4f}")
    print(f"  Adj R-squared:      {model.rsquared_inclusive:.4f}")
    print(f"  N obs:              {int(model.nobs):,}")

    # Use PanelOLS native within-R² directly
    within_r2 = float(model.rsquared_within)
    print(f"  Within-R²:          {within_r2:.4f}")

    beta1 = model.params.get(key_iv, np.nan)
    p1_two = model.pvalues.get(key_iv, np.nan)
    beta1_se = model.std_errors.get(key_iv, np.nan)
    beta1_t = model.tstats.get(key_iv, np.nan)

    # H5: beta1 > 0 (one-tailed)
    if not np.isnan(p1_two) and not np.isnan(beta1):
        p1_one = p1_two / 2 if beta1 > 0 else 1 - p1_two / 2
    else:
        p1_one = np.nan

    h5_sig = not np.isnan(p1_one) and p1_one < 0.05 and beta1 > 0
    h5_text = "YES" if h5_sig else "no"

    print(
        f"  beta1 ({key_iv}):  {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H5={h5_text}"
    )

    meta = {
        "spec_id": spec_id,
        "model_type": model_type,
        "key_iv": key_iv,
        "sample": sample_name,
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "n_clusters": df_reg["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "rsquared": float(model.rsquared_within),
        "rsquared_adj": float(model.rsquared_inclusive),
        "within_r2": within_r2,
        "beta1": float(beta1),
        "beta1_se": float(beta1_se),
        "beta1_t": float(beta1_t),
        "beta1_p_two": float(p1_two),
        "beta1_p_one": float(p1_one),
        "h5_sig": h5_sig,
    }

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Save LaTeX table with two panels: Model A (A1-A4) and Model B (B1-B4)."""
    tex_path = out_dir / "h5_dispersion_table.tex"

    def get_res(spec_id, sample="Main"):
        for r in all_results:
            if r["sample"] == sample and r["spec_id"] == spec_id:
                return r
        return None

    def fmt_coef(val, pval):
        if val is None or pd.isna(val):
            return ""
        stars = ""
        if pval < 0.01:
            stars = "^{***}"
        elif pval < 0.05:
            stars = "^{**}"
        elif pval < 0.10:
            stars = "^{*}"
        return f"{val:.4f}{stars}"

    def fmt_se(val):
        if val is None or pd.isna(val):
            return ""
        return f"({val:.4f})"

    def fmt_int(val):
        if val is None or pd.isna(val):
            return ""
        return f"{int(val):,}"

    def fmt_r2(val):
        if val is None or pd.isna(val):
            return ""
        return f"{val:.4f}"

    # Get Main sample results for all specs
    main_A = [get_res(f"A{i}") for i in range(1, 5)]
    main_B = [get_res(f"B{i}") for i in range(1, 5)]

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{H5: Manager Uncertainty and Analyst Dispersion}",
        "\\label{tab:h5_dispersion}",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        " & \\multicolumn{4}{c}{Model A: Uncertainty Measures} \\\\",
        "\\cmidrule(lr){2-5}",
        " & (A1) & (A2) & (A3) & (A4) \\\\",
        " & CEO QA & CEO Pres & Mgr QA & Mgr Pres \\\\",
        "\\midrule",
    ]

    # Panel A: Uncertainty coefficients
    iv_labels_A = ["CEO QA Uncertainty", "CEO Pres Uncertainty",
                   "Manager QA Uncertainty", "Manager Pres Uncertainty"]

    row1 = "Uncertainty Measure & "
    row1 += " & ".join([
        fmt_coef(r["beta1"], r["beta1_p_one"]) if r else ""
        for r in main_A
    ]) + " \\\\"
    lines.append(row1)

    row2 = " & "
    row2 += " & ".join([
        fmt_se(r["beta1_se"]) if r else ""
        for r in main_A
    ]) + " \\\\"
    lines.append(row2)

    # Add rows for controls and FE
    lines.extend([
        "\\midrule",
        "Lagged Dispersion & Yes & Yes & Yes & Yes \\\\",
        "Controls & Yes & Yes & Yes & Yes \\\\",
        "Firm FE & Yes & Yes & Yes & Yes \\\\",
        "Year FE & Yes & Yes & Yes & Yes \\\\",
        "\\midrule",
    ])

    # Observations and R²
    row_n = "Observations & "
    row_n += " & ".join([
        fmt_int(r["n_obs"]) if r else ""
        for r in main_A
    ]) + " \\\\"
    lines.append(row_n)

    row_r2 = "Within-$R^2$ & "
    row_r2 += " & ".join([
        fmt_r2(r["within_r2"]) if r else ""
        for r in main_A
    ]) + " \\\\"
    lines.append(row_r2)

    # Panel B: Gap measures
    lines.extend([
        "\\bottomrule",
        "\\addlinespace",
        "\\toprule",
        " & \\multicolumn{4}{c}{Model B: Gap Measures} \\\\",
        "\\cmidrule(lr){2-5}",
        " & (B1) & (B2) & (B3) & (B4) \\\\",
        " & CEO & Mgr & CEO-Mgr & CEO-Mgr \\\\",
        " & Pres-QA & Pres-QA & QA & Pres \\\\",
        "\\midrule",
    ])

    # Gap coefficients
    row1_B = "Gap Measure & "
    row1_B += " & ".join([
        fmt_coef(r["beta1"], r["beta1_p_one"]) if r else ""
        for r in main_B
    ]) + " \\\\"
    lines.append(row1_B)

    row2_B = " & "
    row2_B += " & ".join([
        fmt_se(r["beta1_se"]) if r else ""
        for r in main_B
    ]) + " \\\\"
    lines.append(row2_B)

    # Add rows for controls and FE
    lines.extend([
        "\\midrule",
        "Lagged Dispersion & Yes & Yes & Yes & Yes \\\\",
        "Controls & Yes & Yes & Yes & Yes \\\\",
        "Firm FE & Yes & Yes & Yes & Yes \\\\",
        "Year FE & Yes & Yes & Yes & Yes \\\\",
        "\\midrule",
    ])

    # Observations and R²
    row_n_B = "Observations & "
    row_n_B += " & ".join([
        fmt_int(r["n_obs"]) if r else ""
        for r in main_B
    ]) + " \\\\"
    lines.append(row_n_B)

    row_r2_B = "Within-$R^2$ & "
    row_r2_B += " & ".join([
        fmt_r2(r["within_r2"]) if r else ""
        for r in main_B
    ]) + " \\\\"
    lines.append(row_r2_B)

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\\\[-0.5em]",
        "\\parbox{\\textwidth}{\\scriptsize ",
        "\\textit{Notes:} ",
        "Model A tests whether manager uncertainty language predicts contemporaneous analyst dispersion. ",
        "Model B tests whether uncertainty gaps (Pres-QA) and regime gaps (CEO-Mgr) predict dispersion. ",
        "Positive gap = more uncertain in prepared remarks (B1-B2) or CEO more uncertain than broader team (B3-B4). ",
        "All models use the Main industry sample (non-financial, non-utility firms). ",
        "Firms with fewer than 5 calls are excluded. ",
        "Standard errors are clustered at the firm level. ",
        "All continuous controls are standardized. ",
        "Variables are winsorized at 1\\%/99\\% by year. ",
        "$^{*}$p$<$0.10, $^{**}$p$<$0.05, $^{***}$p$<$0.01 (one-tailed).",
        "}",
        "\\end{table}",
    ])

    with open(tex_path, "w") as f:
        f.write("\n".join(lines))

    print(f"  Saved: h5_dispersion_table.tex")


def main(panel_path: str | None = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h5_dispersion" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H5_Dispersion",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H5 Analyst Dispersion Hypothesis (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h5_dispersion",
                required_file="h5_dispersion_panel.parquet",
            )
            panel_file = panel_dir / "h5_dispersion_panel.parquet"
        except Exception as e:
            print(f"ERROR: Could not find Stage 3 panel: {e}")
            return 1
    else:
        panel_file = Path(panel_path)

    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)
    print(f"  Loaded: {panel_file}")

    # Load columns needed for new specs
    panel = pd.read_parquet(
        panel_file,
        columns=[
            "file_name",
            "gvkey",
            "year",
            "ff12_code",
            # DV (current period)
            "dispersion",
            # Lagged DV control
            "lagged_dispersion",
            # Uncertainty measures (Model A IVs)
            "CEO_QA_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            "Manager_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
            # Linguistic controls
            "Analyst_QA_Uncertainty_pct",
            "Entire_All_Negative_pct",
            # Financial controls
            "Size",
            "Lev",
            "TobinsQ",
            "earnings_volatility",
            "earnings_surprise_ratio",
            "loss_dummy",
        ],
    )
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    # Check for dispersion column
    if "dispersion" not in panel.columns:
        print("ERROR: 'dispersion' column not found in panel. Re-run panel builder.")
        return 1

    if "sample" not in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    df_prep = prepare_regression_data(panel)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Summary Statistics (call-level, by sample)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    summary_vars = [
        {"col": v["col"], "label": v["label"]}
        for v in SUMMARY_STATS_VARS
        if v["col"] in df_prep.columns
    ]
    make_summary_stats_table(
        df=df_prep,
        variables=summary_vars,
        sample_names=["Main", "Finance", "Utility"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H5 Analyst Dispersion",
        label="tab:summary_stats_h5",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    all_results = []

    # ------------------------------------------------------------------
    # Run Model A Specs (Uncertainty → Dispersion)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Running Model A (Uncertainty Measures)")
    print("=" * 60)

    for sample in CONFIG["samples"]:
        df_sample = df_prep[df_prep["sample"] == sample].copy()
        df_sample["gvkey_count"] = df_sample.groupby("gvkey")["file_name"].transform("count")
        df_filtered = df_sample[df_sample["gvkey_count"] >= CONFIG["min_calls"]].copy()

        for spec_id, key_iv, iv_label in MODEL_A_SPECS:
            print(f"\n--- {sample} / {spec_id}: {iv_label} ---")

            if len(df_filtered) < 100:
                print("  Skipping: insufficient data")
                continue

            model, meta = run_regression(
                df_filtered, spec_id, key_iv, sample, model_type="A"
            )

            if model is not None:
                all_results.append(meta)
                with open(
                    out_dir / f"regression_results_{sample}_{spec_id}.txt",
                    "w",
                ) as f:
                    f.write(str(model.summary))

    # ------------------------------------------------------------------
    # Run Model B Specs (Gaps → Dispersion)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Running Model B (Gap Measures)")
    print("=" * 60)

    for sample in CONFIG["samples"]:
        df_sample = df_prep[df_prep["sample"] == sample].copy()
        df_sample["gvkey_count"] = df_sample.groupby("gvkey")["file_name"].transform("count")
        df_filtered = df_sample[df_sample["gvkey_count"] >= CONFIG["min_calls"]].copy()

        for spec_id, key_iv, iv_label, gap_formula in MODEL_B_SPECS:
            print(f"\n--- {sample} / {spec_id}: {iv_label} ---")
            print(f"  Gap Formula: {gap_formula}")

            if len(df_filtered) < 100:
                print("  Skipping: insufficient data")
                continue

            model, meta = run_regression(
                df_filtered, spec_id, key_iv, sample, model_type="B"
            )

            if model is not None:
                all_results.append(meta)
                with open(
                    out_dir / f"regression_results_{sample}_{spec_id}.txt",
                    "w",
                ) as f:
                    f.write(str(model.summary))

    # ------------------------------------------------------------------
    # Save outputs
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    _save_latex_table(all_results, out_dir)
    pd.DataFrame(all_results).to_csv(out_dir / "model_diagnostics.csv", index=False)
    print("  Saved: model_diagnostics.csv")

    # Generate sample attrition table
    if all_results:
        main_result = next((r for r in all_results if r.get("sample") == "Main"), all_results[0])
        attrition_stages = [
            ("Master manifest", len(panel)),
            ("Main sample filter", (panel["sample"] == "Main").sum()),
            ("After complete-case + min-calls filter", main_result.get("n_obs", 0)),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H5 Analyst Dispersion")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h5_dispersion_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    print("\n" + "=" * 80)
    print(f"COMPLETE: {len(all_results)} regressions across {len(CONFIG['samples'])} samples")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    parser = parse_arguments()
    sys.exit(main(panel_path=parser.panel_path))
