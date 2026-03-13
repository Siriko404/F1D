#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H7 Speech Vagueness and Stock Illiquidity Hypothesis
================================================================================
ID: econometric/run_h7_illiquidity
Description: Run H7 Illiquidity hypothesis test by loading the call-level panel
             from Stage 3, running fixed effects OLS regressions by industry
             sample, and outputting results.

Model Specification (event-window DV):
    delta_amihud ~ Uncertainty_IV_t + Entire_All_Negative_pct + Analyst_QA_Uncertainty_pct +
                   Size + Lev + ROA + TobinsQ + pre_call_amihud +
                   EntityEffects + TimeEffects

Unit of observation: individual earnings call (file_name).
DV: delta_amihud (change in Amihud illiquidity around call, [+1,+3] - [-3,-1] trading days).
    Parallels H14's delta_spread construction for methodological consistency.

Specifications (6 single-IV regressions + 1 joint Manager spec):
    A1: CEO_QA_Uncertainty_pct
    A2: CEO_Pres_Uncertainty_pct
    A3: Manager_QA_Uncertainty_pct
    A4: Manager_Pres_Uncertainty_pct
    A5: Joint (Manager_QA + Manager_Pres) — H7-C Wald test
    B1: CEO_Clarity_Residual
    B2: Manager_Clarity_Residual

Hypothesis Tests (one-tailed):
    H7: beta(Uncertainty_IV) > 0 (vagueness increases illiquidity)
    H7-C: beta(QA) > beta(Pres) (spontaneous speech has larger effect)

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)

Note: Finance (FF12 code 11) and Utility (FF12 code 8) samples are excluded
from this analysis. The panel still contains these observations for data
provenance purposes, but regressions are run only on the Main sample.

Minimum Calls Filter:
    Firms must have >= 5 calls in the regression sample.
    amihud_illiq must be non-missing (DV).

Inputs:
    - outputs/variables/h7_illiquidity/latest/h7_illiquidity_panel.parquet

Outputs:
    - outputs/econometric/h7_illiquidity/{timestamp}/regression_Main_{spec}.txt
    - outputs/econometric/h7_illiquidity/{timestamp}/h7_illiquidity_table.tex
    - outputs/econometric/h7_illiquidity/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h7_illiquidity/{timestamp}/summary_stats.csv
    - outputs/econometric/h7_illiquidity/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h7_illiquidity_panel)
    - Uses: linearmodels, f1d.shared.latex_tables_accounting

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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample

warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)
warnings.filterwarnings("ignore", category=FutureWarning, module="linearmodels.*")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG = {
    "min_calls": 5,
    "samples": ["Main"],
}

BASE_CONTROLS = [
    "Entire_All_Negative_pct",
    "Analyst_QA_Uncertainty_pct",
    "Size",
    "Lev",
    "ROA",
    "TobinsQ",
    "pre_call_amihud",
]

SPECS = [
    # A specs: raw uncertainty measures (all samples)
    ("A1", "CEO_QA_Uncertainty_pct", "CEO QA Uncertainty"),
    ("A2", "CEO_Pres_Uncertainty_pct", "CEO Pres Uncertainty"),
    ("A3", "Manager_QA_Uncertainty_pct", "Manager QA Uncertainty"),
    ("A4", "Manager_Pres_Uncertainty_pct", "Manager Pres Uncertainty"),
    # B specs: clarity residuals (Main sample ONLY)
    ("B1", "CEO_Clarity_Residual", "CEO Clarity Residual"),
    ("B2", "Manager_Clarity_Residual", "Mgr Clarity Residual"),
]

# B specs only run for Main sample (residuals computed from Main-only H0.3)
MAIN_ONLY_SPECS = {"B1", "B2"}


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables
    {"col": "delta_amihud", "label": "$\\Delta$Amihud (post$-$pre call)"},
    {"col": "amihud_illiq", "label": "Amihud Illiquidity (inter-call)"},
    {"col": "pre_call_amihud", "label": "Pre-Call Amihud"},
    # Uncertainty measures (IVs)
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    # Linguistic controls
    {"col": "Entire_All_Negative_pct", "label": "Entire Call Negative"},
    {"col": "Analyst_QA_Uncertainty_pct", "label": "Analyst QA Uncertainty"},
    # Financial controls
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "ROA", "label": "ROA"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    # Clarity residuals (B specs)
    {"col": "CEO_Clarity_Residual", "label": "CEO Clarity Residual"},
    {"col": "Manager_Clarity_Residual", "label": "Mgr Clarity Residual"},
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H7 Speech Vagueness and Stock Illiquidity (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H7 panel parquet"
    )
    return parser.parse_args()


def prepare_regression_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Derive computed columns needed for regressions."""
    df = panel.copy()

    # Integer quarter index for linearmodels (pd.Period not accepted as time index)
    # call_quarter_int encodes (gvkey, quarter) uniquely: 2007Q3 → 8030
    if "call_quarter" in df.columns:
        df["call_quarter_int"] = (
            df["call_quarter"].dt.year * 4 + df["call_quarter"].dt.quarter - 1
        )

    return df


def run_regression(
    df_sample: pd.DataFrame,
    spec_id: str,
    iv_var: str,
    sample_name: str,
    min_calls: int = 5,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Run a single PanelOLS regression for the given spec.

    DV  : delta_amihud (event-window change in Amihud illiquidity)
    IV  : iv_var (single uncertainty measure)
    FE  : firm (gvkey) + call_quarter (integer), clustered by entity (gvkey)
    """
    required = (
        ["delta_amihud", iv_var] + BASE_CONTROLS + ["gvkey", "call_quarter_int", "file_name"]
    )
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    # Apply min_calls filter AFTER listwise deletion to avoid singletons
    if min_calls > 1:
        call_counts = df_reg.groupby("gvkey")["file_name"].transform("count")
        df_reg = df_reg[call_counts >= min_calls].copy()

    if len(df_reg) < 100:
        return None, {}

    formula = (
        f"delta_amihud ~ {iv_var} + "
        + " + ".join(BASE_CONTROLS)
        + " + EntityEffects + TimeEffects"
    )

    print(f"  Formula: delta_amihud ~ {iv_var} + controls")
    print(f"  N calls: {len(df_reg):,}  |  N firms: {df_reg['gvkey'].nunique():,}")
    print("  Estimating with firm-clustered SEs...")

    t0 = datetime.now()

    if not df_reg.set_index(["gvkey", "call_quarter_int"]).index.is_unique:
        n_dupes = df_reg.duplicated(subset=["gvkey", "call_quarter_int"]).sum()
        warnings.warn(
            f"[{spec_id}] Panel index (gvkey, call_quarter_int) has {n_dupes} non-unique pairs."
        )
    df_panel = df_reg.set_index(["gvkey", "call_quarter_int"])

    try:
        model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: PanelOLS failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared (within): {model.rsquared_within:.4f}")
    print(f"  N obs:              {int(model.nobs):,}")

    expected_regressors = {iv_var} | set(BASE_CONTROLS)
    absorbed = expected_regressors - set(model.params.index)
    if absorbed:
        warnings.warn(f"[{spec_id}] Absorbed regressors: {absorbed}")

    beta1 = float(model.params.get(iv_var, np.nan))
    beta1_se = float(model.std_errors.get(iv_var, np.nan))
    beta1_t = float(model.tstats.get(iv_var, np.nan))
    p1_two = float(model.pvalues.get(iv_var, np.nan))

    # H7: one-tailed p-value for beta1 > 0
    p1_one = p1_two / 2 if beta1 > 0 else 1 - p1_two / 2
    h7_sig = p1_one < 0.05 and beta1 > 0

    print(
        f"  beta ({iv_var}):  {beta1:.4f}  SE={beta1_se:.4f}"
        f"  p(one)={p1_one:.4f}  H7={'YES' if h7_sig else 'no'}"
    )

    meta: Dict[str, Any] = {
        "spec_id": spec_id,
        "sample": sample_name,
        "iv_var": iv_var,
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "n_clusters": df_reg["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "within_r2": float(model.rsquared_within),
        "beta1": beta1,
        "beta1_se": beta1_se,
        "beta1_t": beta1_t,
        "beta1_p_two": p1_two,
        "beta1_p_one": p1_one,
        "h7_sig": h7_sig,
    }

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Emit a LaTeX table of the primary (Main sample) results."""
    tex_path = out_dir / "h7_illiquidity_table.tex"

    def get_res(spec_id: str, sample: str = "Main") -> Optional[Dict[str, Any]]:
        for r in all_results:
            if r["sample"] == sample and r["spec_id"] == spec_id:
                return r
        return None

    def fmt_coef(val: float, pval: float) -> str:
        if val is None or pd.isna(val):
            return ""
        stars = (
            "^{***}"
            if pval < 0.01
            else "^{**}"
            if pval < 0.05
            else "^{*}"
            if pval < 0.10
            else ""
        )
        return f"{val:.4f}{stars}"

    def fmt_se(val: float) -> str:
        return "" if (val is None or pd.isna(val)) else f"({val:.4f})"

    # 6 columns: A1-A4 (raw uncertainty) + B1-B2 (clarity residuals)
    specs_order = ["A1", "A2", "A3", "A4", "B1", "B2"]
    results_main = [get_res(s) for s in specs_order]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H7: Speech Vagueness and $\Delta$Amihud Illiquidity}",
        r"\label{tab:h7_illiquidity}",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r" & (A1) & (A2) & (A3) & (A4) & (B1) & (B2) \\",
        r" & CEO QA & CEO Pres & Mgr QA & Mgr Pres & CEO Resid & Mgr Resid \\",
        r"\midrule",
    ]

    # Single row for uncertainty coefficient
    row_b = "Uncertainty Measure & "
    row_se = " & "
    for r in results_main:
        if r:
            row_b += f"{fmt_coef(r['beta1'], r['beta1_p_one'])} & "
            row_se += f"{fmt_se(r['beta1_se'])} & "
        else:
            row_b += " & "
            row_se += " & "
    lines.append(row_b.rstrip(" &") + r" \\")
    lines.append(row_se.rstrip(" &") + r" \\")

    lines += [
        r"\midrule",
        r"Negative Sentiment & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"Analyst Uncertainty & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"Controls & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"Firm FE  & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"Quarter FE & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"\midrule",
    ]

    row_n = "Observations & "
    row_r2 = "Within-$R^2$ & "
    for r in results_main:
        if r:
            row_n += f"{r['n_obs']:,} & "
            row_r2 += f"{r['within_r2']:.4f} & "
        else:
            row_n += " & "
            row_r2 += " & "
    lines.append(row_n.rstrip(" &") + r" \\")
    lines.append(row_r2.rstrip(" &") + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\\[-0.5em]",
        r"\parbox{\textwidth}{\scriptsize ",
        r"\textit{Notes:} "
        r"Dependent variable is $\Delta$Amihud$_{t}$ = Amihud$_{[+1,+3]}$ $-$ Amihud$_{[-3,-1]}$ "
        r"(change in Amihud illiquidity around the call, $\pm$3 trading days). "
        r"All models use the Main industry sample (non-financial, non-utility firms). "
        r"Columns (A1)--(A4) use raw uncertainty measures; "
        r"columns (B1)--(B2) use clarity residuals (idiosyncratic uncertainty after firm/linguistic controls). "
        r"Firms with fewer than 5 calls are excluded. "
        r"Standard errors (in parentheses) are clustered at the firm level. "
        r"CRSP and Compustat financial variables are winsorized at the 1st/99th percentile per year. "
        r"Linguistic variables (all \textit{\_pct} columns) are winsorized at the 0th/99th percentile per year "
        r"(upper-tail only, given their natural lower bound of zero). "
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for H7).",
        r"}",
        r"\end{table}",
    ]

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  LaTeX table saved: {tex_path.name}")


def _run_h7c_joint_regression(
    df_sample: pd.DataFrame,
    out_dir: Path,
    min_calls: int = 5,
) -> Optional[Dict[str, Any]]:
    """Run joint Manager spec (A5) and formal Wald test for H7-C.

    Tests H₀: β(Manager_QA) = β(Manager_Pres) via Wald χ² test.
    H7-C uses Manager specs only; CEO specs excluded due to selection concerns (L5).
    """
    iv_qa = "Manager_QA_Uncertainty_pct"
    iv_pres = "Manager_Pres_Uncertainty_pct"
    required = (
        ["delta_amihud", iv_qa, iv_pres] + BASE_CONTROLS + ["gvkey", "call_quarter_int", "file_name"]
    )
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    if min_calls > 1:
        call_counts = df_reg.groupby("gvkey")["file_name"].transform("count")
        df_reg = df_reg[call_counts >= min_calls].copy()

    if len(df_reg) < 100:
        print("  A5: insufficient data for joint Manager spec")
        return None

    formula = (
        f"delta_amihud ~ {iv_qa} + {iv_pres} + "
        + " + ".join(BASE_CONTROLS)
        + " + EntityEffects + TimeEffects"
    )

    # Report correlation between the two IVs (multicollinearity check)
    try:
        corr = df_reg[[iv_qa, iv_pres]].corr().iloc[0, 1]
        print(f"  A5: Pearson r(Manager_QA, Manager_Pres) = {corr:.3f}")
    except Exception:
        pass

    print(f"  A5 Formula: delta_amihud ~ {iv_qa} + {iv_pres} + controls")
    print(f"  N calls: {len(df_reg):,}  |  N firms: {df_reg['gvkey'].nunique():,}")

    df_panel = df_reg.set_index(["gvkey", "call_quarter_int"])

    try:
        model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: A5 PanelOLS failed: {e}", file=sys.stderr)
        return None

    beta_qa = float(model.params.get(iv_qa, np.nan))
    beta_pres = float(model.params.get(iv_pres, np.nan))
    se_qa = float(model.std_errors.get(iv_qa, np.nan))
    se_pres = float(model.std_errors.get(iv_pres, np.nan))
    p_qa = float(model.pvalues.get(iv_qa, np.nan))
    p_pres = float(model.pvalues.get(iv_pres, np.nan))

    print(f"  beta(Manager_QA)   = {beta_qa:.4f}  SE={se_qa:.4f}  p={p_qa:.4f}")
    print(f"  beta(Manager_Pres) = {beta_pres:.4f}  SE={se_pres:.4f}  p={p_pres:.4f}")

    # Wald test: H₀: β_QA = β_Pres → β_QA − β_Pres = 0
    wald_chi2 = np.nan
    wald_pval = np.nan
    h7c_supported = False
    try:
        params_names = list(model.params.index)
        r = np.zeros(len(params_names))
        r[params_names.index(iv_qa)] = 1.0
        r[params_names.index(iv_pres)] = -1.0
        wald = model.wald_test(
            restriction=np.array([r]),
            value=np.array([0.0]),
        )
        wald_chi2 = float(wald.stat)
        wald_pval = float(wald.pval)
        h7c_supported = (beta_qa > beta_pres) and (wald_pval < 0.05)
        print(f"  Wald test (H0: b_QA=b_Pres): chi2={wald_chi2:.4f}  p={wald_pval:.4f}")
        print(f"  H7-C: {'SUPPORTED' if h7c_supported else 'not supported'}")
    except Exception as e:
        print(f"  Wald test failed: {e}")

    txt_file = out_dir / "regression_Main_A5.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(str(model.summary))

    return {
        "spec_id": "A5",
        "sample": "Main",
        "iv_var": "Joint_Manager",
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "n_clusters": df_reg["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "within_r2": float(model.rsquared_within),
        "beta1": beta_qa,
        "beta1_se": se_qa,
        "beta1_t": float(model.tstats.get(iv_qa, np.nan)),
        "beta1_p_two": p_qa,
        "beta1_p_one": p_qa / 2 if beta_qa > 0 else 1 - p_qa / 2,
        "h7_sig": False,
        "beta_mgr_pres": beta_pres,
        "wald_chi2": wald_chi2,
        "wald_pval": wald_pval,
        "h7c_supported": h7c_supported,
    }


def _run_robustness_battery(
    df_prep: pd.DataFrame,
    out_dir: Path,
    min_calls: int = 5,
) -> None:
    """Run robustness checks for H7 primary Manager specs (A3/A4).

    Checks:
        1. Two-way cluster (firm × quarter) SEs
        2. Subperiod: pre-GFC (year < 2008) and post-GFC (year >= 2008)
        3. Large-firm sensitivity (firms with >= 50 calls over sample period)
        4. Industry subsamples (within-Main FF12 groups)
    """
    robustness_results: List[Dict[str, Any]] = []
    df_main = df_prep[df_prep["sample"] == "Main"].copy()

    ROBUSTNESS_SPECS = [
        ("A3", "Manager_QA_Uncertainty_pct"),
        ("A4", "Manager_Pres_Uncertainty_pct"),
    ]

    def _fit_spec(df_r: pd.DataFrame, spec_id: str, iv_var: str, check_label: str, two_way: bool = False) -> Optional[Dict[str, Any]]:
        required = (
            ["delta_amihud", iv_var] + BASE_CONTROLS + ["gvkey", "call_quarter_int", "file_name"]
        )
        df_reg = df_r.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()
        if min_calls > 1:
            cc = df_reg.groupby("gvkey")["file_name"].transform("count")
            df_reg = df_reg[cc >= min_calls].copy()
        if len(df_reg) < 50:
            return None
        formula = (
            f"delta_amihud ~ {iv_var} + " + " + ".join(BASE_CONTROLS)
            + " + EntityEffects + TimeEffects"
        )
        df_panel = df_reg.set_index(["gvkey", "call_quarter_int"])
        try:
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
            if two_way:
                model = model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
            else:
                model = model_obj.fit(cov_type="clustered", cluster_entity=True)
            beta = float(model.params.get(iv_var, np.nan))
            se = float(model.std_errors.get(iv_var, np.nan))
            p = float(model.pvalues.get(iv_var, np.nan))
            print(f"  {spec_id} [{check_label}]: beta={beta:.4f}  SE={se:.4f}  p={p:.4f}  N={int(model.nobs):,}")
            return {
                "check": check_label, "spec_id": spec_id, "iv_var": iv_var,
                "n_obs": int(model.nobs), "n_firms": df_reg["gvkey"].nunique(),
                "beta1": beta, "beta1_se": se, "beta1_p_two": p,
            }
        except Exception as e:
            print(f"  {spec_id} [{check_label}] failed: {e}")
            return None

    # (1) Two-way cluster (firm × quarter)
    print("\n--- Robustness 1: Two-way cluster (firm × quarter) ---")
    for spec_id, iv_var in ROBUSTNESS_SPECS:
        res = _fit_spec(df_main, spec_id, iv_var, "two_way_cluster", two_way=True)
        if res:
            robustness_results.append(res)

    # (2) Subperiod: pre-GFC (< 2008) and post-GFC (>= 2008)
    print("\n--- Robustness 2: Subperiod (pre/post-GFC, split 2008) ---")
    if "year" in df_main.columns:
        for period_label, mask in [
            ("pre_GFC", df_main["year"] < 2008),
            ("post_GFC", df_main["year"] >= 2008),
        ]:
            df_sub = df_main[mask].copy()
            print(f"  {period_label}: N={len(df_sub):,}  firms={df_sub['gvkey'].nunique():,}")
            for spec_id, iv_var in ROBUSTNESS_SPECS:
                res = _fit_spec(df_sub, spec_id, iv_var, period_label)
                if res:
                    robustness_results.append(res)

    # (3) Large-firm sensitivity (firms with >= 50 calls over sample period)
    print("\n--- Robustness 3: Large-firm sensitivity (>= 50 calls) ---")
    call_freq = df_main.groupby("gvkey")["file_name"].transform("count")
    df_large = df_main[call_freq >= 50].copy()
    print(f"  Firms >= 50 calls: {df_large['gvkey'].nunique():,}  |  Obs: {len(df_large):,}")
    for spec_id, iv_var in ROBUSTNESS_SPECS:
        res = _fit_spec(df_large, spec_id, iv_var, "large_firm")
        if res:
            robustness_results.append(res)

    # (4) Industry subsamples (within-Main FF12 groups)
    print("\n--- Robustness 4: Industry subsamples (FF12) ---")
    if "ff12_code" in df_main.columns:
        ff12_groups = sorted(df_main["ff12_code"].dropna().unique())
        for ff12 in ff12_groups:
            df_ind = df_main[df_main["ff12_code"] == ff12].copy()
            for spec_id, iv_var in ROBUSTNESS_SPECS:
                res = _fit_spec(df_ind, spec_id, iv_var, f"ff12_{ff12}")
                if res:
                    res["ff12_code"] = ff12
                    robustness_results.append(res)

    # Save robustness results
    if robustness_results:
        rob_df = pd.DataFrame(robustness_results)
        rob_path = out_dir / "robustness_results.csv"
        rob_df.to_csv(rob_path, index=False)
        print(f"\n  Saved: {rob_path.name} ({len(rob_df)} robustness checks)")
    else:
        print("  No robustness results to save.")


def main(panel_path: Optional[str] = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h7_illiquidity" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H7_Illiquidity",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H7 Speech Vagueness and Stock Illiquidity")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    # ------------------------------------------------------------------
    # Load Stage 3 panel
    # ------------------------------------------------------------------
    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h7_illiquidity",
                required_file="h7_illiquidity_panel.parquet",
            )
            panel_file = panel_dir / "h7_illiquidity_panel.parquet"
        except Exception as e:
            print(f"ERROR: Could not find Stage 3 panel: {e}")
            return 1
    else:
        panel_file = Path(panel_path)

    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)
    print(f"  File:    {panel_file}")
    # Load all columns available in panel (delta_amihud added in updated Stage 3)
    panel = pd.read_parquet(panel_file)
    print(f"  Rows:    {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    if "sample" not in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

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
        sample_names=["Main"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H7 Speech Vagueness and Stock Illiquidity",
        label="tab:summary_stats_h7",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # Sanity: DV coverage
    n_dv = panel["delta_amihud"].notna().sum() if "delta_amihud" in panel.columns else 0
    n_dv_old = panel["amihud_illiq"].notna().sum() if "amihud_illiq" in panel.columns else 0
    print(f"  DV (delta_amihud) non-missing: {n_dv:,} / {len(panel):,}")
    print(f"  Legacy (amihud_illiq) non-missing: {n_dv_old:,} / {len(panel):,}")
    if n_dv == 0:
        print("  FATAL: delta_amihud is entirely NaN — rebuild panel with AmihudChangeBuilder.")
        return 1

    df_prep = prepare_regression_data(panel)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_results: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Run regressions by sample × spec
    # ------------------------------------------------------------------
    for sample in CONFIG["samples"]:
        df_sample = df_prep[df_prep["sample"] == sample].copy()

        for spec_id, iv_var, iv_label in SPECS:
            print(f"\n--- {sample} / {spec_id}: {iv_label} ---")

            # B-specs are Main-only by design; enforced via CONFIG["samples"] = ["Main"]
            if spec_id in MAIN_ONLY_SPECS and df_sample[iv_var].isna().all():
                raise RuntimeError(
                    f"{spec_id} ({iv_var}) is all-NaN. "
                    f"Run H0.3 (ceo_clarity_extended) first and rebuild panel."
                )
            model, meta = run_regression(
                df_sample, spec_id, iv_var, sample,
                min_calls=CONFIG["min_calls"]
            )

            if model is not None:
                all_results.append(meta)
                txt_file = (
                    out_dir / f"regression_{sample}_{spec_id}.txt"
                )
                with open(txt_file, "w", encoding="utf-8") as f:
                    f.write(str(model.summary))

    # ------------------------------------------------------------------
    # H7-C: Joint Manager spec (A5) with formal Wald test
    # H7-C is the Manager QA vs Pres comparison. CEO specs (A1/A2) are NOT
    # included in the H7-C comparison due to CEO presence selection concerns.
    # ------------------------------------------------------------------
    print("\n--- H7-C: Joint Manager Spec (Wald Test) ---")
    df_main_h7c = df_prep[df_prep["sample"] == "Main"].copy()
    h7c_result = _run_h7c_joint_regression(df_main_h7c, out_dir, min_calls=CONFIG["min_calls"])
    if h7c_result:
        all_results.append(h7c_result)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    _save_latex_table(all_results, out_dir)

    # ------------------------------------------------------------------
    # Robustness Battery (L12/L13)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Robustness Battery")
    print("=" * 60)
    _run_robustness_battery(df_prep, out_dir, min_calls=CONFIG["min_calls"])

    # Generate sample attrition table
    if all_results:
        main_result = next(
            (r for r in all_results if r.get("sample") == "Main"), all_results[0]
        )
        attrition_stages = [
            ("Master manifest", len(panel)),
            ("Main sample filter", (panel["sample"] == "Main").sum()),
            ("After complete-case + min-calls filter", main_result.get("n_obs", 0)),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H7 Illiquidity")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h7_illiquidity_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    results_df = pd.DataFrame(all_results)
    results_df.to_csv(out_dir / "model_diagnostics.csv", index=False)
    print(f"\n  Diagnostics saved: {out_dir / 'model_diagnostics.csv'}")

    duration = (datetime.now() - t0).total_seconds()
    print("\n" + "=" * 80)
    print(f"COMPLETE in {duration:.1f}s")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main(panel_path=args.panel_path))
