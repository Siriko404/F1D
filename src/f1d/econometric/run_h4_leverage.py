#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H4 Leverage Discipline Hypothesis
================================================================================
ID: econometric/test_h4_leverage
Description: Run H4 Leverage Discipline hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample and uncertainty measure, and outputting results.

Model Specification:
    Uncertainty_t ~ Lev_{t-1} + Analyst_Uncertainty_t + [Pres_Uncertainty_t] +
                    Size + TobinsQ + ROA + CashHoldings + DividendPayer +
                    firm_maturity + earnings_volatility +
                    C(gvkey) + C(year)

Dependent Variables:
    1. Manager_QA_Uncertainty_pct
    2. CEO_QA_Uncertainty_pct
    3. Manager_QA_Weak_Modal_pct
    4. CEO_QA_Weak_Modal_pct
    5. Manager_Pres_Uncertainty_pct
    6. CEO_Pres_Uncertainty_pct

Dynamic Covariates:
    - If DV is a QA measure, the corresponding Presentation measure is added as a control.
      (e.g., Manager_QA regressions control for Manager_Pres_Uncertainty_pct)
    - Analyst_QA_Uncertainty_pct is always included as a control.

Hypothesis Test (one-tailed):
    H4: beta(Lev_lag) < 0  -- higher prior leverage reduces current vagueness

Filters:
    - >= 5 calls per firm
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
    ],
    "samples": ["Main", "Finance", "Utility"],
}

BASE_CONTROLS = [
    "Analyst_QA_Uncertainty_pct",
    "Size",
    "TobinsQ",
    "ROA",
    "CashHoldings",
    "DividendPayer",
    "firm_maturity",
    "earnings_volatility",
]

PRES_CONTROL_MAP = {
    "Manager_QA_Uncertainty_pct": "Manager_Pres_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct": "CEO_Pres_Uncertainty_pct",
    "Manager_QA_Weak_Modal_pct": "Manager_Pres_Uncertainty_pct",
    "CEO_QA_Weak_Modal_pct": "CEO_Pres_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct": None,
    "CEO_Pres_Uncertainty_pct": None,
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H4 Leverage Discipline Hypothesis (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H4 panel parquet"
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

    required = [dv_var, "Lev_lag"] + controls + ["gvkey", "year"]

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
) -> Tuple[Any, Dict[str, Any]]:
    formula = (
        f"{dv_var} ~ 1 + Lev_lag + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )

    print(
        f"  Formula: {dv_var} ~ Lev_lag + {' + '.join(controls)} + EntityEffects + TimeEffects"
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

    try:
        y_full = df_panel[dv_var]
        y_hat_full = model.fitted_values
        common_idx = y_full.index.intersection(y_hat_full.index)
        y = y_full.loc[common_idx].to_numpy(dtype=float)
        y_hat = y_hat_full.loc[common_idx].to_numpy(dtype=float).flatten()
        df_used = df_panel.loc[common_idx].reset_index()
        df_used["_yhat"] = y_hat

        y_dm = (
            y
            - df_used.groupby("gvkey")[dv_var].transform("mean").to_numpy(dtype=float)
            - df_used.groupby("year")[dv_var].transform("mean").to_numpy(dtype=float)
            + float(np.mean(y))
        )
        y_hat_dm = (
            y_hat
            - df_used.groupby("gvkey")["_yhat"].transform("mean").to_numpy(dtype=float)
            - df_used.groupby("year")["_yhat"].transform("mean").to_numpy(dtype=float)
            + float(np.mean(y_hat))
        )
        ss_res = float(((y_dm - y_hat_dm) ** 2).sum())
        ss_tot = float(((y_dm - float(np.mean(y))) ** 2).sum())
        within_r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    except Exception as _e:
        within_r2 = np.nan
        print(f"  WARNING: within-R² computation failed: {_e}")

    print(
        f"  Within-R²:        {within_r2:.4f}"
        if not np.isnan(within_r2)
        else "  Within-R²:        N/A"
    )

    beta1 = model.params.get("Lev_lag", np.nan)
    p1_two = model.pvalues.get("Lev_lag", np.nan)
    beta1_se = model.std_errors.get("Lev_lag", np.nan)
    beta1_t = model.tstats.get("Lev_lag", np.nan)

    # H4: beta1 < 0 (Higher leverage reduces speech uncertainty)
    if not np.isnan(p1_two) and not np.isnan(beta1):
        p1_one = p1_two / 2 if beta1 < 0 else 1 - p1_two / 2
    else:
        p1_one = np.nan

    h4_sig = not np.isnan(p1_one) and p1_one < 0.05 and beta1 < 0
    h4_text = "YES" if h4_sig else "no"

    print(
        f"  beta1 (Lev_lag):  {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H4={h4_text}"
    )

    meta = {
        "dv": dv_var,
        "sample": sample_name,
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "rsquared": float(model.rsquared_within),
        "rsquared_adj": float(model.rsquared_inclusive),
        "within_r2": within_r2,
        "beta1": float(beta1),
        "beta1_se": float(beta1_se),
        "beta1_t": float(beta1_t),
        "beta1_p_two": float(p1_two),
        "beta1_p_one": float(p1_one),
        "h4_sig": h4_sig,
    }

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    tex_path = out_dir / "h4_leverage_table.tex"

    # We will pick: Main sample, all 6 DVs
    def get_res(dv):
        for r in all_results:
            if r["sample"] == "Main" and r["dv"] == dv:
                return r
        return None

    r_mq = get_res("Manager_QA_Uncertainty_pct")
    r_cq = get_res("CEO_QA_Uncertainty_pct")
    r_mw = get_res("Manager_QA_Weak_Modal_pct")
    r_cw = get_res("CEO_QA_Weak_Modal_pct")
    r_mp = get_res("Manager_Pres_Uncertainty_pct")
    r_cp = get_res("CEO_Pres_Uncertainty_pct")

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
        "\\caption{H4: Leverage Discipline and Speech Vagueness}",
        "\\label{tab:h4_leverage}",
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        " & \\multicolumn{4}{c}{Q\\&A Session} & \\multicolumn{2}{c}{Presentation} \\\\",
        "\\cmidrule(lr){2-5} \\cmidrule(lr){6-7}",
        " & Mgr Unc & CEO Unc & Mgr Weak & CEO Weak & Mgr Unc & CEO Unc \\\\",
        " & (1) & (2) & (3) & (4) & (5) & (6) \\\\",
        "\\midrule",
    ]

    # Row 1: Lev_lag
    r1 = "Leverage$_{t-1}$ & "
    r1 += f"{fmt_coef(r_mq['beta1'], r_mq['beta1_p_one'])} & " if r_mq else " & "
    r1 += f"{fmt_coef(r_cq['beta1'], r_cq['beta1_p_one'])} & " if r_cq else " & "
    r1 += f"{fmt_coef(r_mw['beta1'], r_mw['beta1_p_one'])} & " if r_mw else " & "
    r1 += f"{fmt_coef(r_cw['beta1'], r_cw['beta1_p_one'])} & " if r_cw else " & "
    r1 += f"{fmt_coef(r_mp['beta1'], r_mp['beta1_p_one'])} & " if r_mp else " & "
    r1 += f"{fmt_coef(r_cp['beta1'], r_cp['beta1_p_one'])} \\\\" if r_cp else " \\\\"
    lines.append(r1)

    # Row 2: SE
    r2 = " & "
    r2 += f"{fmt_se(r_mq['beta1_se'])} & " if r_mq else " & "
    r2 += f"{fmt_se(r_cq['beta1_se'])} & " if r_cq else " & "
    r2 += f"{fmt_se(r_mw['beta1_se'])} & " if r_mw else " & "
    r2 += f"{fmt_se(r_cw['beta1_se'])} & " if r_cw else " & "
    r2 += f"{fmt_se(r_mp['beta1_se'])} & " if r_mp else " & "
    r2 += f"{fmt_se(r_cp['beta1_se'])} \\\\" if r_cp else " \\\\"
    lines.append(r2)

    lines.extend(
        [
            "\\midrule",
            "Pres. Uncertainty & Yes & Yes & Yes & Yes & No & No \\\\",
            "Controls & Yes & Yes & Yes & Yes & Yes & Yes \\\\",
            "Firm FE & Yes & Yes & Yes & Yes & Yes & Yes \\\\",
            "Year FE & Yes & Yes & Yes & Yes & Yes & Yes \\\\",
            "\\midrule",
        ]
    )

    rn = "Observations & "
    rn += f"{r_mq['n_obs']:,} & " if r_mq else " & "
    rn += f"{r_cq['n_obs']:,} & " if r_cq else " & "
    rn += f"{r_mw['n_obs']:,} & " if r_mw else " & "
    rn += f"{r_cw['n_obs']:,} & " if r_cw else " & "
    rn += f"{r_mp['n_obs']:,} & " if r_mp else " & "
    rn += f"{r_cp['n_obs']:,} \\\\" if r_cp else " \\\\"
    lines.append(rn)

    rr = "Within-$R^2$ & "
    rr += f"{fmt_r2(r_mq['within_r2'])} & " if r_mq else " & "
    rr += f"{fmt_r2(r_cq['within_r2'])} & " if r_cq else " & "
    rr += f"{fmt_r2(r_mw['within_r2'])} & " if r_mw else " & "
    rr += f"{fmt_r2(r_cw['within_r2'])} & " if r_cw else " & "
    rr += f"{fmt_r2(r_mp['within_r2'])} & " if r_mp else " & "
    rr += f"{fmt_r2(r_cp['within_r2'])} \\\\" if r_cp else " \\\\"
    lines.append(rr)

    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])

    with open(tex_path, "w") as f:
        f.write("\n".join(lines))


def main(panel_path: str | None = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h4_leverage" / timestamp

    print("=" * 80)
    print("STAGE 4: Test H4 Leverage Discipline Hypothesis (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")

    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h4_leverage",
                required_file="h4_leverage_panel.parquet",
            )
            panel_file = panel_dir / "h4_leverage_panel.parquet"
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
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            # Primary predictor
            "Lev_lag",
            # Base controls
            "Analyst_QA_Uncertainty_pct",
            "Size",
            "TobinsQ",
            "ROA",
            "CashHoldings",
            "DividendPayer",
            "firm_maturity",
            "earnings_volatility",
        ],
    )
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    if "sample" not in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    out_dir.mkdir(parents=True, exist_ok=True)
    all_results = []

    for dv in CONFIG["dependent_variables"]:
        for sample in CONFIG["samples"]:
            print(f"\n--- {sample} / {dv} ---")

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

            print(
                f"  After filters: {len(df_filtered):,} calls, {df_filtered['gvkey'].nunique():,} firms"
            )

            if len(df_filtered) < 100:
                print("  Skipping: insufficient data")
                continue

            print(f"\n============================================================")
            print(f"Running regression: {sample} / {dv}")
            print(f"============================================================")

            model, meta = run_regression(df_filtered, dv, sample, controls)

            if model is not None:
                all_results.append(meta)
                with open(out_dir / f"regression_results_{sample}_{dv}.txt", "w") as f:
                    f.write(str(model.summary))

    _save_latex_table(all_results, out_dir)
    pd.DataFrame(all_results).to_csv(out_dir / "model_diagnostics.csv", index=False)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    parser = parse_arguments()
    sys.exit(main(panel_path=parser.panel_path))
