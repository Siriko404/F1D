#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H11 Political Risk - Language Uncertainty Hypothesis
================================================================================
ID: econometric/test_h11_prisk_uncertainty
Description: Run H11 Political Risk hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample and uncertainty measure, and outputting results.

Model Specification:
    Uncertainty_t ~ PRisk_t + UncQue_t + [UncPre*_t] +
                    NegCall + lnAssets + TobinsQ + ROA + CashRatio +
                    DivDummy + FirmMat + EarnVol +
                    C(gvkey) + C(year)

Dependent Variables:
    1. UncAnsMgr
    2. UncAnsCEO
    3. UncPreMgr
    4. UncPreCEO

Dynamic Covariates:
    - If DV is a QA measure, the corresponding Presentation measure is added as a control.
      (e.g., UncAnsMgr regressions control for UncPreMgr)
    - UncQue is always included as a control.

Hypothesis Tests (one-tailed):
    H11: beta(PRisk) > 0  -- higher political risk increases speech uncertainty

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls to be included in regression.

Inputs:
    - outputs/variables/h11_prisk_uncertainty/latest/h11_prisk_uncertainty_panel.parquet

Outputs:
    - outputs/econometric/h11_prisk_uncertainty/{timestamp}/regression_results_{sample}_{dv}.txt
    - outputs/econometric/h11_prisk_uncertainty/{timestamp}/h11_prisk_uncertainty_table.tex
    - outputs/econometric/h11_prisk_uncertainty/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h11_prisk_uncertainty/{timestamp}/summary_stats.csv
    - outputs/econometric/h11_prisk_uncertainty/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h11_prisk_uncertainty_panel)
    - Uses: statsmodels, linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-03-05
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
    "dependent_variables": [
        "UncAnsMgr",
        "UncAnsCEO",
        "UncPreMgr",
        "UncPreCEO",
    ],
    "samples": ["Main", "Finance", "Utility"],
    "fe_specs": ["industry", "firm"],
}

BASE_CONTROLS = [
    "UncQue",
    "NegCall",
    "lnAssets",
    "TobinsQ",
    "ROA",
    "CashRatio",
    "DivDummy",
    "FirmMat",
    "EarnVol",
]

PRES_CONTROL_MAP = {
    "UncAnsMgr": "UncPreMgr",
    "UncAnsCEO": "UncPreCEO",
    "UncPreMgr": None,
    "UncPreCEO": None,
}


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables (uncertainty measures)
    {"col": "UncAnsMgr", "label": "Mgr QA Uncertainty"},
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncPreMgr", "label": "Mgr Pres Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    # Main independent variable
    {"col": "PRisk", "label": "Political Risk$_{t}$"},
    # Controls
    {"col": "UncQue", "label": "Analyst QA Uncertainty"},
    {"col": "NegCall", "label": "Negative Sentiment"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CashRatio", "label": "Cash Holdings"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "FirmMat", "label": "Firm Maturity"},
    {"col": "EarnVol", "label": "Earnings Volatility"},
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H11 Political Risk Uncertainty Hypothesis (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H11 panel parquet"
    )
    return parser.parse_args()


def prepare_regression_data(
    panel: pd.DataFrame,
    dv_var: str,
) -> Tuple[pd.DataFrame, List[str]]:
    pres_control = PRES_CONTROL_MAP.get(dv_var)
    controls = list(BASE_CONTROLS)
    if pres_control:
        controls.append(pres_control)

    required = [dv_var, "PRisk"] + controls + ["gvkey", "year", "ff12_code"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing required columns in panel: {missing}")

    df = panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    return df, controls


def run_regression(
    df_sample: pd.DataFrame,
    dv_var: str,
    sample_name: str,
    controls: List[str],
    fe_type: str,
) -> Tuple[Any, Dict[str, Any]]:
    fe_label = "Firm + CalYr" if fe_type == "firm" else "Industry(FF12) + CalYr"

    print(
        f"  Formula: {dv_var} ~ PRisk + {' + '.join(controls)} + {fe_label}"
    )
    print(
        f"  N calls: {len(df_sample):,}  |  N firms: {df_sample['gvkey'].nunique():,}"
    )
    print("  Estimating with firm-clustered SEs via PanelOLS...")

    t0 = datetime.now()

    df_panel = df_sample.set_index(["gvkey", "year"])

    try:
        if fe_type == "firm":
            exog_str = " + ".join(["PRisk"] + controls)
            formula = f"{dv_var} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        else:  # industry
            model_obj = PanelOLS(
                dependent=df_panel[dv_var],
                exog=df_panel[["PRisk"] + controls],
                entity_effects=False,
                time_effects=True,
                other_effects=df_panel["ff12_code"],
                drop_absorbed=True,
                check_rank=False,
            )
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}  Adj R-squared: {1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid:.4f}")
    print(f"  N obs:              {int(model.nobs):,}")

    beta_prisk = model.params.get("PRisk", np.nan)
    p_two = model.pvalues.get("PRisk", np.nan)
    beta_se = model.std_errors.get("PRisk", np.nan)
    beta_t = model.tstats.get("PRisk", np.nan)

    # H11: beta(PRisk) > 0 (Higher political risk increases speech uncertainty)
    if not np.isnan(p_two) and not np.isnan(beta_prisk):
        p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2
    else:
        p_one = np.nan

    h11_sig = not np.isnan(p_one) and p_one < 0.05 and beta_prisk > 0
    h11_text = "YES" if h11_sig else "no"

    print(
        f"  beta1 (PRisk):   {beta_prisk:.4f}  SE={beta_se:.4f}  p(one-tail)={p_one:.4f}  H11={h11_text}"
    )

    meta = {
        "dv": dv_var,
        "sample": sample_name,
        "fe": fe_type,
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "n_clusters": df_sample["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
        "beta_prisk": float(beta_prisk),
        "beta_prisk_se": float(beta_se),
        "beta_prisk_t": float(beta_t),
        "beta_prisk_p_two": float(p_two),
        "beta_prisk_p_one": float(p_one),
        "h11_sig": h11_sig,
    }

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    tex_path = out_dir / "h11_prisk_uncertainty_table.tex"

    # Main sample, 4 DVs × 2 FE = 8 cols
    # Layout: cols 1-4 = Industry FE, cols 5-8 = Firm FE
    #         within each FE block: Mgr QA, CEO QA, Mgr Pres, CEO Pres
    def get_res(dv, fe_type):
        for r in all_results:
            if r["sample"] == "Main" and r["dv"] == dv and r.get("fe") == fe_type:
                return r
        return None

    col_order = [
        ("UncAnsMgr", "industry"),
        ("UncAnsCEO", "industry"),
        ("UncPreMgr", "industry"),
        ("UncPreCEO", "industry"),
        ("UncAnsMgr", "firm"),
        ("UncAnsCEO", "firm"),
        ("UncPreMgr", "firm"),
        ("UncPreCEO", "firm"),
    ]
    col_results = [get_res(dv, fe) for dv, fe in col_order]

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
        if abs(val) < 0.001:
            return f"{val:.2e}"
        return f"{val:.4f}"

    def build_row(label, extractor, fmt):
        cells = []
        for r in col_results:
            cells.append(fmt(extractor(r)) if r else "")
        return label + " & " + " & ".join(cells) + " \\\\"

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{H11: Political Risk and Language Uncertainty}",
        "\\label{tab:h11_prisk_uncertainty}",
        "\\scriptsize",
        "\\begin{tabular}{l" + "c" * 8 + "}",
        "\\toprule",
        " & \\multicolumn{4}{c}{Industry FE} & \\multicolumn{4}{c}{Firm FE} \\\\",
        "\\cmidrule(lr){2-5} \\cmidrule(lr){6-9}",
        " & Mgr QA & CEO QA & Mgr Pres & CEO Pres & Mgr QA & CEO QA & Mgr Pres & CEO Pres \\\\",
        " & (1) & (2) & (3) & (4) & (5) & (6) & (7) & (8) \\\\",
        "\\midrule",
    ]

    # PRisk coefficient + SE row (one-tailed β>0)
    coef_cells = []
    se_cells = []
    for r in col_results:
        if r:
            coef_cells.append(fmt_coef(r["beta_prisk"], r["beta_prisk_p_one"]))
            se_cells.append(fmt_se(r["beta_prisk_se"]))
        else:
            coef_cells.append("")
            se_cells.append("")
    lines.append("Political Risk$_{t}$ & " + " & ".join(coef_cells) + " \\\\")
    lines.append(" & " + " & ".join(se_cells) + " \\\\")

    lines.append("\\midrule")
    lines.append("Controls & " + " & ".join(["Yes"] * 8) + " \\\\")
    lines.append("Industry FE & " + " & ".join(["Yes"] * 4 + [""] * 4) + " \\\\")
    lines.append("Firm FE & " + " & ".join([""] * 4 + ["Yes"] * 4) + " \\\\")
    lines.append("Calendar Year FE & " + " & ".join(["Yes"] * 8) + " \\\\")
    lines.append("\\midrule")

    lines.append(build_row("Observations", lambda r: r["n_obs"], lambda v: f"{v:,}"))
    lines.append(build_row("$R^2$",     lambda r: r["r2"],     fmt_r2))
    lines.append(build_row("Adj.~$R^2$", lambda r: r["adj_r2"], fmt_r2))

    lines.extend(["\\bottomrule", "\\end{tabular}"])
    lines.extend([
        "\\\\[-0.5em]",
        "\\parbox{\\textwidth}{\\scriptsize ",
        "\\textit{Notes:} ",
        "This table reports the effect of quarterly political risk on language uncertainty. ",
        "Columns (1)--(4) use industry (FF12) fixed effects; columns (5)--(8) use firm fixed effects. ",
        "All models use the Main industry sample (non-financial, non-utility firms). ",
        "Political Risk is measured contemporaneously in the same calendar quarter as the earnings call. ",
        "Firms with fewer than 5 calls are excluded. ",
        "Standard errors are clustered at the firm level (Petersen 2009). ",
        "All continuous controls are standardized. ",
        "Variables are winsorized at 1\\%/99\\% by year.",
        "}",
        "\\end{table}",
    ])

    with open(tex_path, "w") as f:
        f.write("\n".join(lines))


def main(panel_path: str | None = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h11_prisk_uncertainty" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H11_PRisk_Uncertainty",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H11 Political Risk - Language Uncertainty Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h11_prisk_uncertainty",
                required_file="h11_prisk_uncertainty_panel.parquet",
            )
            panel_file = panel_dir / "h11_prisk_uncertainty_panel.parquet"
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
            # Dependent variables (uncertainty measures)
            "UncAnsMgr",
            "UncAnsCEO",
            "UncPreMgr",
            "UncPreCEO",
            # Primary predictor
            "PRisk",
            # Base controls
            "UncQue",
            "NegCall",
            "lnAssets",
            "TobinsQ",
            "ROA",
            "CashRatio",
            "DivDummy",
            "FirmMat",
            "EarnVol",
        ],
    )
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    if "sample" not in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

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
        if v["col"] in panel.columns
    ]
    make_summary_stats_table(
        df=panel,
        variables=summary_vars,
        sample_names=["Main", "Finance", "Utility"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H11 Political Risk Uncertainty",
        label="tab:summary_stats_h11",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    all_results = []

    for dv in CONFIG["dependent_variables"]:
        for sample in CONFIG["samples"]:
            df_prep, controls = prepare_regression_data(panel, dv)

            if sample == "Main":
                df_sample = df_prep[df_prep["sample"] == "Main"].copy()
            elif sample == "Finance":
                df_sample = df_prep[df_prep["sample"] == "Finance"].copy()
            else:
                df_sample = df_prep[df_prep["sample"] == "Utility"].copy()

            df_sample["gvkey_count"] = df_sample.groupby("gvkey")[
                "file_name"
            ].transform("count")
            df_filtered = df_sample[
                df_sample["gvkey_count"] >= CONFIG["min_calls"]
            ].copy()

            if len(df_filtered) < 100:
                print(f"\n--- {sample} / {dv} ---  Skipping: insufficient data ({len(df_filtered)} obs)")
                continue

            for fe_type in CONFIG["fe_specs"]:
                print(f"\n--- {sample} / {dv} / FE={fe_type} ---")
                print(
                    f"  After filters: {len(df_filtered):,} calls, {df_filtered['gvkey'].nunique():,} firms"
                )

                print(f"============================================================")
                print(f"Running regression: {sample} / {dv} / FE={fe_type}")
                print(f"============================================================")

                model, meta = run_regression(df_filtered, dv, sample, controls, fe_type)

                if model is not None:
                    all_results.append(meta)
                    with open(out_dir / f"regression_results_{sample}_{dv}_{fe_type}.txt", "w") as f:
                        f.write(f"FE: {fe_type}\n")
                        f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
                        f.write(str(model.summary))

    _save_latex_table(all_results, out_dir)
    pd.DataFrame(all_results).to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")

    # Generate sample attrition table
    if all_results:
        main_result = next((r for r in all_results if r.get("sample") == "Main"), all_results[0])
        attrition_stages = [
            ("Master manifest", len(panel)),
            ("Main sample filter", (panel["sample"] == "Main").sum()),
            ("After complete-case + min-calls filter", main_result.get("n_obs", 0)),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H11 Political Risk Uncertainty")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h11_prisk_uncertainty_table.tex",
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
