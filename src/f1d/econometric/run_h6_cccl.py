#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H6 SEC Scrutiny (CCCL) Hypothesis
================================================================================
ID: econometric/run_h6_cccl
Description: Run H6 SEC Scrutiny hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample, and outputting results.

Model Specification:
    Uncertainty_t ~ CCCL_lag_{t-1} + Size + Lev + ROA + TobinsQ + CashHoldings +
                    C(gvkey) + C(year)

Dependent Variables:
    1. Manager_QA_Uncertainty_pct
    2. CEO_QA_Uncertainty_pct
    3. Manager_QA_Weak_Modal_pct
    4. CEO_QA_Weak_Modal_pct
    5. Manager_Pres_Uncertainty_pct
    6. CEO_Pres_Uncertainty_pct
    7. Uncertainty_Gap (QA - Pres)

Hypothesis Tests (one-tailed):
    H6-A: beta(CCCL_lag) < 0 (Scrutiny reduces uncertainty)
    H6-B: |beta(QA)| > |beta(Pres)| (Stronger effect in spontaneous speech)
    H6-C: beta(CCCL_lag) < 0 for Uncertainty_Gap

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls to be included in regression.

Inputs:
    - outputs/variables/h6_cccl/latest/h6_cccl_panel.parquet

Outputs:
    - outputs/econometric/h6_cccl/{timestamp}/regression_results_{sample}_{dv}.txt
    - outputs/econometric/h6_cccl/{timestamp}/h6_cccl_table.tex
    - outputs/econometric/h6_cccl/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h6_cccl/{timestamp}/summary_stats.csv
    - outputs/econometric/h6_cccl/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h6_cccl_panel)
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
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample

# Silence statsmodels covariance warnings
warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)

CONFIG = {
    "min_calls": 5,
    "dependent_variables": [
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
        "Uncertainty_Gap",
    ],
    "samples": ["Main", "Finance", "Utility"],
}

BASE_CONTROLS = [
    "Size",
    "Lev",
    "ROA",
    "TobinsQ",
    "CashHoldings",
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables (uncertainty / gap measures)
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_QA_Weak_Modal_pct", "label": "Mgr QA Weak Modal"},
    {"col": "CEO_QA_Weak_Modal_pct", "label": "CEO QA Weak Modal"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "Uncertainty_Gap", "label": "QA-Pres Uncertainty Gap"},
    # Main independent variable (CCCL shift intensity)
    {"col": "shift_intensity_mkvalt_ff48_lag", "label": "CCCL$_{t-1}$"},
    # Controls
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "ROA", "label": "ROA"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "CashHoldings", "label": "Cash Holdings"},
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H6 SEC Scrutiny (CCCL) Hypothesis (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H6 panel parquet"
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
    dv_var: str,
    sample_name: str,
    pre_trends: bool = False,
) -> Tuple[Any, Dict[str, Any]]:
    if pre_trends:
        iv_cols = [
            "shift_intensity_mkvalt_ff48_lag",
            "shift_intensity_mkvalt_ff48_lead1",
            "shift_intensity_mkvalt_ff48_lead2",
        ]
    else:
        iv_cols = ["shift_intensity_mkvalt_ff48_lag"]

    required = [dv_var] + iv_cols + BASE_CONTROLS + ["gvkey", "year"]
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    if len(df_reg) < 100:
        return None, {}

    if pre_trends:
        formula = (
            f"{dv_var} ~ shift_intensity_mkvalt_ff48_lag + shift_intensity_mkvalt_ff48_lead1 + shift_intensity_mkvalt_ff48_lead2 + "
            + " + ".join(BASE_CONTROLS)
            + " + C(gvkey) + C(year)"
        )
        print(
            f"  Formula: {dv_var} ~ CCCL_t-1 + CCCL_t+1 + CCCL_t+2 + {' + '.join(BASE_CONTROLS)} + C(gvkey) + C(year)"
        )
    else:
        formula = (
            f"{dv_var} ~ shift_intensity_mkvalt_ff48_lag + "
            + " + ".join(BASE_CONTROLS)
            + " + C(gvkey) + C(year)"
        )
        print(
            f"  Formula: {dv_var} ~ CCCL_lag + {' + '.join(BASE_CONTROLS)} + C(gvkey) + C(year)"
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
    print(f"  R-squared (LSDV): {model.rsquared_within:.4f}")
    print(f"  Adj R-squared:    {model.rsquared_inclusive:.4f}")
    print(f"  N obs:            {int(model.nobs):,}")

    try:
        y_full = df_reg[dv_var]
        y_hat_full = model.fitted_values
        common_idx = y_full.index.intersection(y_hat_full.index)
        y = y_full.loc[common_idx]
        y_hat = y_hat_full.loc[common_idx]
        df_used = df_reg.loc[common_idx].copy()
        df_used["_yhat"] = y_hat.values

        y_dm = (
            y
            - df_used.groupby("gvkey")[dv_var].transform("mean")
            - df_used.groupby("year")[dv_var].transform("mean")
            + y.mean()
        )
        y_hat_dm = (
            y_hat
            - df_used.groupby("gvkey")["_yhat"].transform("mean")
            - df_used.groupby("year")["_yhat"].transform("mean")
            + float(y_hat.mean())
        )
        ss_res = float(((y_dm - y_hat_dm) ** 2).sum())
        ss_tot = float(((y_dm - float(y_dm.mean())) ** 2).sum())
        within_r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    except Exception as _e:
        within_r2 = np.nan
        print(f"  WARNING: within-R² computation failed: {_e}")

    print(
        f"  Within-R²:        {within_r2:.4f}"
        if not np.isnan(within_r2)
        else "  Within-R²:        N/A"
    )

    beta1 = model.params.get("shift_intensity_mkvalt_ff48_lag", np.nan)
    p1_two = model.pvalues.get("shift_intensity_mkvalt_ff48_lag", np.nan)
    beta1_se = model.std_errors.get("shift_intensity_mkvalt_ff48_lag", np.nan)
    beta1_t = model.tstats.get("shift_intensity_mkvalt_ff48_lag", np.nan)

    # H6: beta1 < 0
    if not np.isnan(p1_two) and not np.isnan(beta1):
        p1_one = p1_two / 2 if beta1 < 0 else 1 - p1_two / 2
    else:
        p1_one = np.nan

    h6_sig = not np.isnan(p1_one) and p1_one < 0.05 and beta1 < 0
    h6_text = "YES" if h6_sig else "no"

    print(
        f"  beta1 (CCCL_lag): {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H6={h6_text}"
    )

    meta = {
        "dv": dv_var,
        "sample": sample_name,
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "rsquared": float(model.rsquared_within),
        "rsquared_adj": float(model.rsquared_inclusive),
        "within_r2": within_r2,
        "beta1": float(beta1),
        "beta1_se": float(beta1_se),
        "beta1_t": float(beta1_t),
        "beta1_p_two": float(p1_two),
        "beta1_p_one": float(p1_one),
        "h6_sig": h6_sig,
    }

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    tex_path = out_dir / "h6_cccl_table.tex"

    def get_res(dv, sample="Main"):
        for r in all_results:
            if r["sample"] == sample and r["dv"] == dv:
                return r
        return None

    r_1 = get_res("Manager_QA_Uncertainty_pct")
    r_2 = get_res("CEO_QA_Uncertainty_pct")
    r_3 = get_res("Manager_Pres_Uncertainty_pct")
    r_4 = get_res("CEO_Pres_Uncertainty_pct")
    r_5 = get_res("Uncertainty_Gap")

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
        "\\caption{H6: SEC Scrutiny (CCCL) and Speech Vagueness}",
        "\\label{tab:h6_cccl}",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        " & \\multicolumn{2}{c}{Q\\&A Session} & \\multicolumn{2}{c}{Presentation} & \\multicolumn{1}{c}{Gap} \\\\",
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5} \\cmidrule(lr){6-6}",
        " & Mgr Unc & CEO Unc & Mgr Unc & CEO Unc & Unc Gap \\\\",
        " & (1) & (2) & (3) & (4) & (5) \\\\",
        "\\midrule",
    ]

    # Row 1: CCCL_lag
    r1 = "CCCL Exposure$_{t-1}$ & "
    r1 += f"{fmt_coef(r_1['beta1'], r_1['beta1_p_one'])} & " if r_1 else " & "
    r1 += f"{fmt_coef(r_2['beta1'], r_2['beta1_p_one'])} & " if r_2 else " & "
    r1 += f"{fmt_coef(r_3['beta1'], r_3['beta1_p_one'])} & " if r_3 else " & "
    r1 += f"{fmt_coef(r_4['beta1'], r_4['beta1_p_one'])} & " if r_4 else " & "
    r1 += f"{fmt_coef(r_5['beta1'], r_5['beta1_p_one'])} \\\\" if r_5 else " \\\\"
    lines.append(r1)

    # Row 2: SE
    r2 = " & "
    r2 += f"{fmt_se(r_1['beta1_se'])} & " if r_1 else " & "
    r2 += f"{fmt_se(r_2['beta1_se'])} & " if r_2 else " & "
    r2 += f"{fmt_se(r_3['beta1_se'])} & " if r_3 else " & "
    r2 += f"{fmt_se(r_4['beta1_se'])} & " if r_4 else " & "
    r2 += f"{fmt_se(r_5['beta1_se'])} \\\\" if r_5 else " \\\\"
    lines.append(r2)

    lines.extend(
        [
            "\\midrule",
            "Controls & Yes & Yes & Yes & Yes & Yes \\\\",
            "Firm FE & Yes & Yes & Yes & Yes & Yes \\\\",
            "Year FE & Yes & Yes & Yes & Yes & Yes \\\\",
            "\\midrule",
        ]
    )

    rn = "Observations & "
    rn += f"{r_1['n_obs']:,} & " if r_1 else " & "
    rn += f"{r_2['n_obs']:,} & " if r_2 else " & "
    rn += f"{r_3['n_obs']:,} & " if r_3 else " & "
    rn += f"{r_4['n_obs']:,} & " if r_4 else " & "
    rn += f"{r_5['n_obs']:,} \\\\" if r_5 else " \\\\"
    lines.append(rn)

    rr = "Within-$R^2$ & "
    rr += f"{fmt_r2(r_1['within_r2'])} & " if r_1 else " & "
    rr += f"{fmt_r2(r_2['within_r2'])} & " if r_2 else " & "
    rr += f"{fmt_r2(r_3['within_r2'])} & " if r_3 else " & "
    rr += f"{fmt_r2(r_4['within_r2'])} & " if r_4 else " & "
    rr += f"{fmt_r2(r_5['within_r2'])} \\\\" if r_5 else " \\\\"
    lines.append(rr)

    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])

    with open(tex_path, "w") as f:
        f.write("\n".join(lines))


def main(panel_path: str | None = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h6_cccl" / timestamp

    print("=" * 80)
    print("STAGE 4: Test H6 SEC Scrutiny (CCCL) Hypothesis (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")

    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h6_cccl",
                required_file="h6_cccl_panel.parquet",
            )
            panel_file = panel_dir / "h6_cccl_panel.parquet"
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
            "gvkey",
            "year",
            "ff12_code",
            # Dependent variables (uncertainty measures)
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            # Primary predictor (CCCL institutional shift intensity)
            "shift_intensity_mkvalt_ff48_lag",
            "shift_intensity_mkvalt_ff48_lead1",
            "shift_intensity_mkvalt_ff48_lead2",
            # Base controls
            "Size",
            "Lev",
            "ROA",
            "TobinsQ",
            "CashHoldings",
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
        caption="Summary Statistics — H6 SEC Scrutiny (CCCL)",
        label="tab:summary_stats_h6",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    all_results = []

    for dv in CONFIG["dependent_variables"]:
        for sample in CONFIG["samples"]:
            print(f"\n--- {sample} / {dv} ---")

            if sample == "Main":
                df_sample = df_prep[df_prep["sample"] == "Main"].copy()
            elif sample == "Finance":
                df_sample = df_prep[df_prep["sample"] == "Finance"].copy()
            else:
                df_sample = df_prep[df_prep["sample"] == "Utility"].copy()

            # The CCCL instrument dataset begins in 2005.
            # Filter gvkeys to those with >= 5 calls strictly within the non-null window.
            df_sample["gvkey_count"] = df_sample.groupby("gvkey")[
                "shift_intensity_mkvalt_ff48_lag"
            ].transform("count")
            df_filtered = df_sample[
                df_sample["gvkey_count"] >= CONFIG["min_calls"]
            ].copy()

            if len(df_filtered) < 100:
                print("  Skipping: insufficient data")
                continue

            model, meta = run_regression(df_filtered, dv, sample)

            if model is not None:
                all_results.append(meta)
                with open(out_dir / f"regression_results_{sample}_{dv}.txt", "w") as f:
                    f.write(str(model.summary))

            # Run pre-trends variant
            print(f"\n--- {sample} / {dv} (Pre-Trends Falsification) ---")
            model_pt, _ = run_regression(df_filtered, dv, sample, pre_trends=True)
            if model_pt is not None:
                with open(
                    out_dir / f"regression_results_{sample}_{dv}_PRETRENDS.txt", "w"
                ) as f:
                    f.write(str(model_pt.summary))

    _save_latex_table(all_results, out_dir)
    pd.DataFrame(all_results).to_csv(out_dir / "model_diagnostics.csv", index=False)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    parser = parse_arguments()
    sys.exit(main(panel_path=parser.panel_path))
