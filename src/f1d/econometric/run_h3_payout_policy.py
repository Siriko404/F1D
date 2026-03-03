#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H3 Payout Policy Hypothesis
================================================================================
ID: econometric/test_h3_payout_policy
Description: Run H3 Payout Policy hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample and uncertainty measure, and outputting results.

Model Specification:
    DV_lead ~ Uncertainty + Lev + Uncertainty_x_Lev +
              earnings_volatility + fcf_growth + firm_maturity +
              Size + ROA + TobinsQ + CashHoldings +
              C(gvkey) + C(year)

Dependent Variables:
    1. div_stability_lead (higher = more stable)
    2. payout_flexibility_lead (higher = more flexible)

Hypothesis Tests (one-tailed):
    For div_stability:
        H3a: beta(Uncertainty) < 0 (vagueness reduces stability)
        H3b: beta(Uncertainty x Lev) < 0 (leverage amplifies negative effect)

    For payout_flexibility:
        H3a: beta(Uncertainty) > 0 (vagueness increases flexibility)
        H3b: beta(Uncertainty x Lev) > 0 (leverage amplifies positive effect)

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls to be included in regression.
    Additional filter: is_div_payer_5yr == 1 (firm must have paid dividends in trailing 5 years).

Inputs:
    - outputs/variables/h3_payout_policy/latest/h3_payout_policy_panel.parquet

Outputs:
    - outputs/econometric/h3_payout_policy/{timestamp}/regression_results_{sample}_{dv}_{measure}.txt
    - outputs/econometric/h3_payout_policy/{timestamp}/h3_payout_policy_table.tex
    - outputs/econometric/h3_payout_policy/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h3_payout_policy/{timestamp}/summary_stats.csv
    - outputs/econometric/h3_payout_policy/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h3_payout_policy_panel)
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
    "uncertainty_measures": [
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ],
    "dependent_variables": [
        "div_stability_lead",
        "payout_flexibility_lead",
    ],
    "samples": ["Main", "Finance", "Utility"],
}

CONTROL_VARS = [
    "earnings_volatility",
    "fcf_growth",
    "firm_maturity",
    "Size",
    "ROA",
    "TobinsQ",
    "CashHoldings",
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables
    {"col": "div_stability_lead", "label": "Dividend Stability$_{t+1}$"},
    {"col": "payout_flexibility_lead", "label": "Payout Flexibility$_{t+1}$"},
    # Main independent variables
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_QA_Weak_Modal_pct", "label": "Mgr QA Weak Modal"},
    {"col": "CEO_QA_Weak_Modal_pct", "label": "CEO QA Weak Modal"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    # Leverage (interaction term)
    {"col": "Lev", "label": "Leverage"},
    # Controls
    {"col": "earnings_volatility", "label": "Earnings Volatility"},
    {"col": "fcf_growth", "label": "FCF Growth"},
    {"col": "firm_maturity", "label": "Firm Maturity"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "ROA", "label": "ROA"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "CashHoldings", "label": "Cash Holdings"},
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H3 Payout Policy Hypothesis (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H3 panel parquet"
    )
    return parser.parse_args()


def prepare_regression_data(
    panel: pd.DataFrame,
    dv_var: str,
    uncertainty_var: str,
) -> pd.DataFrame:
    required = (
        [
            dv_var,
            uncertainty_var,
            "Lev",
            "is_div_payer_5yr",
        ]
        + CONTROL_VARS
        + ["gvkey", "year"]
    )

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing required columns in panel: {missing}")

    df = panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    # Filter to only firms that paid dividends in the trailing 5-year window
    df = df[df["is_div_payer_5yr"] == 1].copy()

    df["Uncertainty"] = df[uncertainty_var]
    df["Uncertainty_x_Lev"] = df["Uncertainty"] * df["Lev"]

    return df


def run_regression(
    df_sample: pd.DataFrame,
    dv_var: str,
    sample_name: str,
    uncertainty_var: str,
) -> Tuple[Any, Dict[str, Any]]:
    controls = [c for c in CONTROL_VARS if c in df_sample.columns]

    formula = (
        f"{dv_var} ~ 1 + Uncertainty + Lev + Uncertainty_x_Lev + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )

    print(
        f"  Formula: {dv_var} ~ Uncertainty + Lev + Uncertainty_x_Lev + {' + '.join(controls)} + EntityEffects + TimeEffects"
    )
    print(
        f"  N calls: {len(df_sample):,}  |  N firms: {df_sample['gvkey'].nunique():,}"
    )
    print("  Estimating with firm-clustered SEs via PanelOLS...")

    t0 = datetime.now()

    df_panel = df_sample.set_index(["gvkey", "year"])

    try:
        model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared (within): {model.rsquared_within:.4f}")
    print(f"  Adj R-squared:      {model.rsquared_inclusive:.4f}")
    print(f"  N obs:              {int(model.nobs):,}")

    within_r2 = float(model.rsquared_within)
    print(f"  Within-R²: {within_r2:.4f}")

    beta1 = model.params.get("Uncertainty", np.nan)
    beta3 = model.params.get("Uncertainty_x_Lev", np.nan)
    p1_two = model.pvalues.get("Uncertainty", np.nan)
    p3_two = model.pvalues.get("Uncertainty_x_Lev", np.nan)
    beta1_se = model.std_errors.get("Uncertainty", np.nan)
    beta3_se = model.std_errors.get("Uncertainty_x_Lev", np.nan)
    beta1_t = model.tstats.get("Uncertainty", np.nan)
    beta3_t = model.tstats.get("Uncertainty_x_Lev", np.nan)

    # Direction tests depend on DV
    if dv_var == "div_stability_lead":
        # H3a: beta1 < 0
        if not np.isnan(p1_two) and not np.isnan(beta1):
            p1_one = p1_two / 2 if beta1 < 0 else 1 - p1_two / 2
        else:
            p1_one = np.nan
        # H3b: beta3 < 0
        if not np.isnan(p3_two) and not np.isnan(beta3):
            p3_one = p3_two / 2 if beta3 < 0 else 1 - p3_two / 2
        else:
            p3_one = np.nan
        h3a_sig = not np.isnan(p1_one) and p1_one < 0.05 and beta1 < 0
        h3b_sig = not np.isnan(p3_one) and p3_one < 0.05 and beta3 < 0
        h3a_text = "YES" if h3a_sig else "no"
        h3b_text = "YES" if h3b_sig else "no"
        print(
            f"  beta1 (Uncertainty):  {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H3a={h3a_text}"
        )
        print(
            f"  beta3 (Unc x Lev):    {beta3:.4f}  SE={beta3_se:.4f}  p(one-tail)={p3_one:.4f}  H3b={h3b_text}"
        )

    else:
        # payout_flexibility_lead
        # H3a: beta1 > 0
        if not np.isnan(p1_two) and not np.isnan(beta1):
            p1_one = p1_two / 2 if beta1 > 0 else 1 - p1_two / 2
        else:
            p1_one = np.nan
        # H3b: beta3 > 0
        if not np.isnan(p3_two) and not np.isnan(beta3):
            p3_one = p3_two / 2 if beta3 > 0 else 1 - p3_two / 2
        else:
            p3_one = np.nan
        h3a_sig = not np.isnan(p1_one) and p1_one < 0.05 and beta1 > 0
        h3b_sig = not np.isnan(p3_one) and p3_one < 0.05 and beta3 > 0
        h3a_text = "YES" if h3a_sig else "no"
        h3b_text = "YES" if h3b_sig else "no"
        print(
            f"  beta1 (Uncertainty):  {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H3a={h3a_text}"
        )
        print(
            f"  beta3 (Unc x Lev):    {beta3:.4f}  SE={beta3_se:.4f}  p(one-tail)={p3_one:.4f}  H3b={h3b_text}"
        )

    meta = {
        "dv": dv_var,
        "sample": sample_name,
        "uncertainty_measure": uncertainty_var,
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "n_clusters": df_sample["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "rsquared": float(model.rsquared_within),
        "rsquared_inclusive": float(model.rsquared_inclusive),
        "within_r2": within_r2,
        "beta1": float(beta1),
        "beta1_se": float(beta1_se),
        "beta1_t": float(beta1_t),
        "beta1_p_two": float(p1_two),
        "beta1_p_one": float(p1_one),
        "beta3": float(beta3),
        "beta3_se": float(beta3_se),
        "beta3_t": float(beta3_t),
        "beta3_p_two": float(p3_two),
        "beta3_p_one": float(p3_one),
        "h3a_sig": h3a_sig,
        "h3b_sig": h3b_sig,
    }

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    # Build custom LaTeX table for the two main DVs (Main sample, Manager QA and CEO QA only)
    tex_path = out_dir / "h3_payout_policy_table.tex"

    # We will pick: Main sample
    # DV: Div Stability and Payout Flexibility
    # Unc: Manager QA and CEO QA

    # Simple mapping
    def get_res(dv, unc):
        for r in all_results:
            if (
                r["sample"] == "Main"
                and r["dv"] == dv
                and r["uncertainty_measure"] == unc
            ):
                return r
        return None

    res_ds_m = get_res("div_stability_lead", "Manager_QA_Uncertainty_pct")
    res_ds_c = get_res("div_stability_lead", "CEO_QA_Uncertainty_pct")
    res_pf_m = get_res("payout_flexibility_lead", "Manager_QA_Uncertainty_pct")
    res_pf_c = get_res("payout_flexibility_lead", "CEO_QA_Uncertainty_pct")

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
        "\\caption{H3: Uncertainty, Leverage, and Payout Policy}",
        "\\label{tab:h3_payout_policy}",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        " & \\multicolumn{2}{c}{Dividend Stability} & \\multicolumn{2}{c}{Payout Flexibility} \\\\",
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}",
        " & (1) & (2) & (3) & (4) \\\\",
        " & Mgr Q\\&A & CEO Q\\&A & Mgr Q\\&A & CEO Q\\&A \\\\",
        "\\midrule",
    ]

    # Row 1: Uncertainty
    r1 = "Uncertainty & "
    r1 += (
        f"{fmt_coef(res_ds_m['beta1'], res_ds_m['beta1_p_one'])} & "
        if res_ds_m
        else " & "
    )
    r1 += (
        f"{fmt_coef(res_ds_c['beta1'], res_ds_c['beta1_p_one'])} & "
        if res_ds_c
        else " & "
    )
    r1 += (
        f"{fmt_coef(res_pf_m['beta1'], res_pf_m['beta1_p_one'])} & "
        if res_pf_m
        else " & "
    )
    r1 += (
        f"{fmt_coef(res_pf_c['beta1'], res_pf_c['beta1_p_one'])} \\\\"
        if res_pf_c
        else " \\\\"
    )
    lines.append(r1)

    # Row 2: SE Uncertainty
    r2 = " & "
    r2 += f"{fmt_se(res_ds_m['beta1_se'])} & " if res_ds_m else " & "
    r2 += f"{fmt_se(res_ds_c['beta1_se'])} & " if res_ds_c else " & "
    r2 += f"{fmt_se(res_pf_m['beta1_se'])} & " if res_pf_m else " & "
    r2 += f"{fmt_se(res_pf_c['beta1_se'])} \\\\" if res_pf_c else " \\\\"
    lines.append(r2)

    # Row 3: Unc x Lev
    r3 = "Uncertainty $\\times$ Lev & "
    r3 += (
        f"{fmt_coef(res_ds_m['beta3'], res_ds_m['beta3_p_one'])} & "
        if res_ds_m
        else " & "
    )
    r3 += (
        f"{fmt_coef(res_ds_c['beta3'], res_ds_c['beta3_p_one'])} & "
        if res_ds_c
        else " & "
    )
    r3 += (
        f"{fmt_coef(res_pf_m['beta3'], res_pf_m['beta3_p_one'])} & "
        if res_pf_m
        else " & "
    )
    r3 += (
        f"{fmt_coef(res_pf_c['beta3'], res_pf_c['beta3_p_one'])} \\\\"
        if res_pf_c
        else " \\\\"
    )
    lines.append(r3)

    # Row 4: SE Unc x Lev
    r4 = " & "
    r4 += f"{fmt_se(res_ds_m['beta3_se'])} & " if res_ds_m else " & "
    r4 += f"{fmt_se(res_ds_c['beta3_se'])} & " if res_ds_c else " & "
    r4 += f"{fmt_se(res_pf_m['beta3_se'])} & " if res_pf_m else " & "
    r4 += f"{fmt_se(res_pf_c['beta3_se'])} \\\\" if res_pf_c else " \\\\"
    lines.append(r4)

    lines.extend(
        [
            "\\midrule",
            "Controls & Yes & Yes & Yes & Yes \\\\",
            "Firm FE & Yes & Yes & Yes & Yes \\\\",
            "Year FE & Yes & Yes & Yes & Yes \\\\",
            "\\midrule",
        ]
    )

    rn = "Observations & "
    rn += f"{res_ds_m['n_obs']:,} & " if res_ds_m else " & "
    rn += f"{res_ds_c['n_obs']:,} & " if res_ds_c else " & "
    rn += f"{res_pf_m['n_obs']:,} & " if res_pf_m else " & "
    rn += f"{res_pf_c['n_obs']:,} \\\\" if res_pf_c else " \\\\"
    lines.append(rn)

    # Add Firms row (m1 fix)
    rf = "Firms & "
    rf += f"{res_ds_m['n_firms']:,} & " if res_ds_m else " & "
    rf += f"{res_ds_c['n_firms']:,} & " if res_ds_c else " & "
    rf += f"{res_pf_m['n_firms']:,} & " if res_pf_m else " & "
    rf += f"{res_pf_c['n_firms']:,} \\\\" if res_pf_c else " \\\\"
    lines.append(rf)

    rr = "Within-$R^2$ & "
    rr += f"{fmt_r2(res_ds_m['within_r2'])} & " if res_ds_m else " & "
    rr += f"{fmt_r2(res_ds_c['within_r2'])} & " if res_ds_c else " & "
    rr += f"{fmt_r2(res_pf_m['within_r2'])} & " if res_pf_m else " & "
    rr += f"{fmt_r2(res_pf_c['within_r2'])} \\\\" if res_pf_c else " \\\\"
    lines.append(rr)

    lines.extend(["\\bottomrule", "\\end{tabular}"])
    # Add table notes
    lines.extend([
        "\\\\[-0.5em]",
        "\\parbox{\\textwidth}{\\scriptsize ",
        "\\textit{Notes:} "
        "This table reports the effect of managerial uncertainty on payout policy. "
        "Columns (1)--(2) use dividend stability as the dependent variable; "
        "columns (3)--(4) use payout flexibility. "
        "All models use the Main industry sample (non-financial, non-utility firms). "
        "Sample restricted to firms with dividend payments in trailing 5 years (is\\_div\\_payer\\_5yr==1). "
        "Firms with fewer than 5 calls are excluded. "
        "Standard errors are clustered at the firm level. "
        "All continuous controls are standardized. "
        "Variables are winsorized at 1\\%/99\\% by year. "
        "* $p<0.10$, ** $p<0.05$, *** $p<0.01$ (one-tailed tests).",
        "}",
        "\\end{table}",
    ])

    with open(tex_path, "w") as f:
        f.write("\n".join(lines))


def main(panel_path: str | None = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h3_payout_policy" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H3_PayoutPolicy",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H3 Payout Policy Hypothesis (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h3_payout_policy",
                required_file="h3_payout_policy_panel.parquet",
            )
            panel_file = panel_dir / "h3_payout_policy_panel.parquet"
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
            "div_stability_lead",
            "payout_flexibility_lead",
            "Lev",
            "is_div_payer_5yr",
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            "earnings_volatility",
            "fcf_growth",
            "firm_maturity",
            "Size",
            "ROA",
            "TobinsQ",
            "CashHoldings",
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
        caption="Summary Statistics — H3 Payout Policy",
        label="tab:summary_stats_h3",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    all_results = []

    for dv in CONFIG["dependent_variables"]:
        for sample in CONFIG["samples"]:
            for unc in CONFIG["uncertainty_measures"]:
                print(f"\n--- {sample} / {dv} / {unc} ---")

                df_prep = prepare_regression_data(panel, dv, unc)

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

                print(
                    f"  After filters: {len(df_filtered):,} calls, {df_filtered['gvkey'].nunique():,} firms"
                )

                if len(df_filtered) < 100:
                    print("  Skipping: insufficient data")
                    continue

                print(f"\n============================================================")
                print(f"Running regression: {sample} / {dv} / {unc}")
                print(f"============================================================")

                model, meta = run_regression(df_filtered, dv, sample, unc)

                if model is not None:
                    all_results.append(meta)
                    with open(
                        out_dir / f"regression_results_{sample}_{dv}_{unc}.txt", "w"
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
        generate_attrition_table(attrition_stages, out_dir, "H3 Payout Policy")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h3_payout_policy_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    # Copy run.log from logs directory to output directory for discoverability
    log_file = log_dir / "run.log"
    if log_file.exists():
        import shutil
        shutil.copy(log_file, out_dir / "run.log")
        print(f"  Saved: run.log (copied from {log_dir})")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    parser = parse_arguments()
    sys.exit(main(panel_path=parser.panel_path))
