#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H5 Analyst Dispersion Hypothesis
================================================================================
ID: econometric/test_h5_dispersion
Description: Run H5 Analyst Dispersion hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample, and outputting results.

Model Specification A (Hedging predicts dispersion):
    Dispersion_{t+1} ~ Weak_Modal_t + Uncertainty_t + Prior_Dispersion_t +
                       Analyst_Uncertainty_t + earnings_surprise + loss_dummy +
                       Size + Lev + TobinsQ + earnings_volatility +
                       C(gvkey) + C(year)

Model Specification B (Spontaneous Gap predicts dispersion):
    Dispersion_{t+1} ~ Uncertainty_Gap_t + Pres_Uncertainty_t + Prior_Dispersion_t +
                       Analyst_Uncertainty_t + earnings_surprise + loss_dummy +
                       Size + Lev + TobinsQ + earnings_volatility +
                       C(gvkey) + C(year)

Where Uncertainty_Gap = Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct

Hypothesis Tests (one-tailed):
    H5-A: beta(Weak_Modal) > 0 (hedging increases future dispersion)
    H5-B: beta(Uncertainty_Gap) > 0 (gap reveals hidden uncertainty, increasing dispersion)

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
Date: 2026-02-26
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

BASE_CONTROLS = [
    "Analyst_QA_Uncertainty_pct",
    "earnings_surprise_ratio",
    "loss_dummy",
    "Size",
    "Lev",
    "TobinsQ",
    "earnings_volatility",
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variable
    {"col": "dispersion_lead", "label": "Analyst Dispersion$_{t+1}$"},
    # Main independent variables
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_QA_Weak_Modal_pct", "label": "Mgr QA Weak Modal"},
    {"col": "CEO_QA_Weak_Modal_pct", "label": "CEO QA Weak Modal"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    # QA-Pres gap (computed)
    {"col": "Uncertainty_Gap", "label": "QA-Pres Uncertainty Gap"},
    # Controls
    {"col": "Analyst_QA_Uncertainty_pct", "label": "Analyst QA Uncertainty"},
    {"col": "earnings_surprise_ratio", "label": "Earnings Surprise Ratio"},
    {"col": "loss_dummy", "label": "Loss Dummy"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "earnings_volatility", "label": "Earnings Volatility"},
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
    df = panel.copy()
    df["Uncertainty_Gap"] = (
        df["Manager_QA_Uncertainty_pct"] - df["Manager_Pres_Uncertainty_pct"]
    )
    return df


def run_regression(
    df_sample: pd.DataFrame,
    spec_name: str,
    target_var: str,  # Weak_Modal or Uncertainty_Gap
    base_var: str,  # QA_Uncertainty or Pres_Uncertainty
    sample_name: str,
    include_lag: bool,
) -> Tuple[Any, Dict[str, Any]]:
    controls = list(BASE_CONTROLS)
    if include_lag:
        controls.append("prior_dispersion")

    required = ["dispersion_lead", target_var, base_var] + controls + ["gvkey", "year"]
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    df_reg["target_var"] = df_reg[target_var]
    df_reg["base_var"] = df_reg[base_var]

    if len(df_reg) < 100:
        return None, {}

    formula = (
        "dispersion_lead ~ target_var + base_var + "
        + " + ".join(controls)
        + " + C(gvkey) + C(year)"
    )

    print(
        f"  Formula: dispersion_lead ~ {target_var} + {base_var} + {' + '.join(controls)} + C(gvkey) + C(year)"
    )
    print(f"  N calls: {len(df_reg):,}  |  N firms: {df_reg['gvkey'].nunique():,}")
    print("  Estimating with firm-clustered SEs... (this may take a moment)")

    t0 = datetime.now()

    # Convert to multi-index for PanelOLS
    df_reg["gvkey_cat"] = df_reg["gvkey"].astype("category")
    df_reg["year_cat"] = df_reg["year"].astype("category")
    df_panel = df_reg.set_index(["gvkey", "year"])

    # We drop C(gvkey) and C(year) from the formula and use PanelOLS entity_effects
    form_clean = formula.replace(" + C(gvkey) + C(year)", "")
    form_clean = form_clean.replace("~", "~ 1 +")  # ensure intercept is explicit

    try:
        form_clean = form_clean + " + EntityEffects + TimeEffects"
        model_obj = PanelOLS.from_formula(form_clean, data=df_panel, drop_absorbed=True)
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

    beta1 = model.params.get("target_var", np.nan)
    p1_two = model.pvalues.get("target_var", np.nan)
    beta1_se = model.std_errors.get("target_var", np.nan)
    beta1_t = model.tstats.get("target_var", np.nan)

    # H5: beta1 > 0
    if not np.isnan(p1_two) and not np.isnan(beta1):
        p1_one = p1_two / 2 if beta1 > 0 else 1 - p1_two / 2
    else:
        p1_one = np.nan

    h5_sig = not np.isnan(p1_one) and p1_one < 0.05 and beta1 > 0
    h5_text = "YES" if h5_sig else "no"

    print(
        f"  beta1 ({target_var}):  {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H5={h5_text}"
    )

    meta = {
        "spec_name": spec_name,
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
    tex_path = out_dir / "h5_dispersion_table.tex"

    def get_res(spec, sample="Main"):
        for r in all_results:
            if r["sample"] == sample and r["spec_name"] == spec:
                return r
        return None

    r_A1 = get_res("Model A (Lagged DV)")
    r_A2 = get_res("Model A (No Lag)")
    r_B1 = get_res("Model B (Lagged DV)")
    r_B2 = get_res("Model B (No Lag)")

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

    def fmt_r2(val):
        if val is None or pd.isna(val):
            return ""
        return f"{val:.4f}"

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{H5: Speech Vagueness and Analyst Dispersion}",
        "\\label{tab:h5_dispersion}",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        " & \\multicolumn{2}{c}{Model A (Hedging)} & \\multicolumn{2}{c}{Model B (Gap)} \\\\",
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}",
        " & (1) & (2) & (3) & (4) \\\\",
        "\\midrule",
    ]

    # Row 1: Target Var (Weak Modal or Gap)
    r1 = "Hedging / Gap & "
    r1 += f"{fmt_coef(r_A1['beta1'], r_A1['beta1_p_one'])} & " if r_A1 else " & "
    r1 += f"{fmt_coef(r_A2['beta1'], r_A2['beta1_p_one'])} & " if r_A2 else " & "
    r1 += f"{fmt_coef(r_B1['beta1'], r_B1['beta1_p_one'])} & " if r_B1 else " & "
    r1 += f"{fmt_coef(r_B2['beta1'], r_B2['beta1_p_one'])} \\\\" if r_B2 else " \\\\"
    lines.append(r1)

    # Row 2: SE
    r2 = " & "
    r2 += f"{fmt_se(r_A1['beta1_se'])} & " if r_A1 else " & "
    r2 += f"{fmt_se(r_A2['beta1_se'])} & " if r_A2 else " & "
    r2 += f"{fmt_se(r_B1['beta1_se'])} & " if r_B1 else " & "
    r2 += f"{fmt_se(r_B2['beta1_se'])} \\\\" if r_B2 else " \\\\"
    lines.append(r2)

    lines.extend(
        [
            "\\midrule",
            "Lagged Dispersion & Yes & No & Yes & No \\\\",
            "Controls & Yes & Yes & Yes & Yes \\\\",
            "Firm FE & Yes & Yes & Yes & Yes \\\\",
            "Year FE & Yes & Yes & Yes & Yes \\\\",
            "\\midrule",
        ]
    )

    rn = "Observations & "
    rn += f"{r_A1['n_obs']:,} & " if r_A1 else " & "
    rn += f"{r_A2['n_obs']:,} & " if r_A2 else " & "
    rn += f"{r_B1['n_obs']:,} & " if r_B1 else " & "
    rn += f"{r_B2['n_obs']:,} \\\\" if r_B2 else " \\\\"
    lines.append(rn)

    rr = "Within-$R^2$ & "
    rr += f"{fmt_r2(r_A1['within_r2'])} & " if r_A1 else " & "
    rr += f"{fmt_r2(r_A2['within_r2'])} & " if r_A2 else " & "
    rr += f"{fmt_r2(r_B1['within_r2'])} & " if r_B1 else " & "
    rr += f"{fmt_r2(r_B2['within_r2'])} \\\\" if r_B2 else " \\\\"
    lines.append(rr)

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\\\[-0.5em]",
        "\\parbox{\\textwidth}{\\scriptsize ",
        "\\textit{Notes:} "
        "Model A tests whether weak modal language predicts analyst dispersion. "
        "Model B tests whether the QA-Pres uncertainty gap predicts dispersion. "
        "All models use the Main industry sample (non-financial, non-utility firms). "
        "Firms with fewer than 5 calls are excluded. "
        "Standard errors are clustered at the firm level. "
        "All continuous controls are standardized. "
        "Variables are winsorized at 1\\%/99\\% by year. "
        "$^{*}$p$<$0.10, $^{**}$p$<$0.05, $^{***}$p$<$0.01 (one-tailed).",
        "}",
        "\\end{table}",
    ])

    with open(tex_path, "w") as f:
        f.write("\n".join(lines))


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
    panel = pd.read_parquet(
        panel_file,
        columns=[
            "file_name",
            "gvkey",
            "year",
            "ff12_code",
            "dispersion_lead",
            "prior_dispersion",
            "Manager_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "Analyst_QA_Uncertainty_pct",
            "earnings_surprise_ratio",
            "loss_dummy",
            "Size",
            "Lev",
            "TobinsQ",
            "earnings_volatility",
        ],
    )
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

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

    specs = [
        (
            "Model A (Lagged DV)",
            "Manager_QA_Weak_Modal_pct",
            "Manager_QA_Uncertainty_pct",
            True,
        ),
        (
            "Model A (No Lag)",
            "Manager_QA_Weak_Modal_pct",
            "Manager_QA_Uncertainty_pct",
            False,
        ),
        (
            "Model B (Lagged DV)",
            "Uncertainty_Gap",
            "Manager_Pres_Uncertainty_pct",
            True,
        ),
        ("Model B (No Lag)", "Uncertainty_Gap", "Manager_Pres_Uncertainty_pct", False),
    ]

    for sample in CONFIG["samples"]:
        if sample == "Main":
            df_sample = df_prep[df_prep["sample"] == "Main"].copy()
        elif sample == "Finance":
            df_sample = df_prep[df_prep["sample"] == "Finance"].copy()
        else:
            df_sample = df_prep[df_prep["sample"] == "Utility"].copy()

        df_sample["gvkey_count"] = df_sample.groupby("gvkey")["file_name"].transform(
            "count"
        )
        df_filtered = df_sample[df_sample["gvkey_count"] >= CONFIG["min_calls"]].copy()

        for spec_name, target_var, base_var, include_lag in specs:
            print(f"\n--- {sample} / {spec_name} ---")

            if len(df_filtered) < 100:
                print("  Skipping: insufficient data")
                continue

            model, meta = run_regression(
                df_filtered, spec_name, target_var, base_var, sample, include_lag
            )

            if model is not None:
                all_results.append(meta)
                with open(
                    out_dir
                    / f"regression_results_{sample}_{spec_name.replace(' ', '_')}.txt",
                    "w",
                ) as f:
                    f.write(str(model.summary))

    _save_latex_table(all_results, out_dir)
    pd.DataFrame(all_results).to_csv(out_dir / "model_diagnostics.csv", index=False)

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
    print("COMPLETE")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    parser = parse_arguments()
    sys.exit(main(panel_path=parser.panel_path))
