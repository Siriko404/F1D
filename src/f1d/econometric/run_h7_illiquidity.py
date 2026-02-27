#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H7 Speech Vagueness and Stock Illiquidity Hypothesis
================================================================================
ID: econometric/run_h7_illiquidity
Description: Run H7 Illiquidity hypothesis test by loading the call-level panel
             from Stage 3, running fixed effects OLS regressions by industry
             sample, and outputting results.

Model Specification (primary — forward-looking DV):
    Amihud_Illiq_{t+1} ~ Uncertainty_t + Weak_Modal_t +
                          Size + Lev + ROA + TobinsQ + Volatility + StockRet +
                          EntityEffects + TimeEffects

Unit of observation: individual earnings call (file_name).
DV: amihud_illiq_lead (the next fiscal year's Amihud illiquidity measure).

Hypothesis Tests (one-tailed):
    H7-A: beta(Manager_QA_Uncertainty) > 0 (vagueness increases illiquidity)
    H7-B: beta(Manager_Pres_Uncertainty) > 0 (presentation vagueness too)
    H7-C: beta(QA) > beta(Pres) (spontaneous speech has larger effect)

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls in the regression sample.
    amihud_illiq_lead must be non-missing (DV).

Inputs:
    - outputs/variables/h7_illiquidity/latest/h7_illiquidity_panel.parquet

Outputs:
    - outputs/econometric/h7_illiquidity/{timestamp}/regression_{sample}_{spec}.txt
    - outputs/econometric/h7_illiquidity/{timestamp}/h7_illiquidity_table.tex
    - outputs/econometric/h7_illiquidity/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h7_illiquidity/{timestamp}/summary_stats.csv
    - outputs/econometric/h7_illiquidity/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h7_illiquidity_panel)
    - Uses: linearmodels, f1d.shared.latex_tables_accounting

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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
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
    "samples": ["Main", "Finance", "Utility"],
}

BASE_CONTROLS = [
    "Size",
    "Lev",
    "ROA",
    "TobinsQ",
    "Volatility",
    "StockRet",
]

# Each tuple: (spec_label, uncertainty_var, base_uncertainty_var)
SPECS = [
    ("QA_Uncertainty", "Manager_QA_Uncertainty_pct", "CEO_QA_Uncertainty_pct"),
    ("QA_Weak_Modal", "Manager_QA_Weak_Modal_pct", "CEO_QA_Weak_Modal_pct"),
    ("Pres_Uncertainty", "Manager_Pres_Uncertainty_pct", "CEO_Pres_Uncertainty_pct"),
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variable
    {"col": "amihud_illiq_lead", "label": "Amihud Illiquidity$_{t+1}$"},
    # Primary uncertainty measures
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_QA_Weak_Modal_pct", "label": "Mgr QA Weak Modal"},
    {"col": "CEO_QA_Weak_Modal_pct", "label": "CEO QA Weak Modal"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    # Controls
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "ROA", "label": "ROA"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "Volatility", "label": "Return Volatility"},
    {"col": "StockRet", "label": "Stock Return"},
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

    # QA-Presentation spontaneity gap (H7-C test)
    df["Uncertainty_Gap"] = (
        df["Manager_QA_Uncertainty_pct"] - df["Manager_Pres_Uncertainty_pct"]
    )
    df["Weak_Modal_Gap"] = (
        (df["Manager_QA_Weak_Modal_pct"] - df["Manager_Pres_Weak_Modal_pct"])
        if "Manager_Pres_Weak_Modal_pct" in df.columns
        else np.nan
    )

    # Year from start_date (time FE axis)
    if "year" not in df.columns:
        df["year"] = pd.to_datetime(df["start_date"], errors="coerce").dt.year

    return df


def run_regression(
    df_sample: pd.DataFrame,
    spec_name: str,
    iv_var: str,
    second_iv: str,
    sample_name: str,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Run a single PanelOLS regression for the given spec.

    DV  : amihud_illiq_lead (t+1 illiquidity — forward looking, no leakage)
    IV1 : iv_var  (primary uncertainty/vagueness measure)
    IV2 : second_iv (comparison measure — e.g. CEO vs Manager)
    FE  : firm (gvkey) + year, clustered by entity (gvkey)
    """
    required = (
        ["amihud_illiq_lead", iv_var, second_iv] + BASE_CONTROLS + ["gvkey", "year"]
    )
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    if len(df_reg) < 100:
        return None, {}

    # Alias the IVs so the formula is generic
    df_reg["_iv1"] = df_reg[iv_var]
    df_reg["_iv2"] = df_reg[second_iv]

    formula = (
        "amihud_illiq_lead ~ _iv1 + _iv2 + "
        + " + ".join(BASE_CONTROLS)
        + " + EntityEffects + TimeEffects"
    )

    print(f"  Formula: amihud_illiq_lead ~ {iv_var} + {second_iv} + controls")
    print(f"  N calls: {len(df_reg):,}  |  N firms: {df_reg['gvkey'].nunique():,}")
    print("  Estimating with firm-clustered SEs...")

    t0 = datetime.now()

    df_panel = df_reg.set_index(["gvkey", "year"])

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

    beta1 = float(model.params.get("_iv1", np.nan))
    beta1_se = float(model.std_errors.get("_iv1", np.nan))
    beta1_t = float(model.tstats.get("_iv1", np.nan))
    p1_two = float(model.pvalues.get("_iv1", np.nan))

    beta2 = float(model.params.get("_iv2", np.nan))
    beta2_se = float(model.std_errors.get("_iv2", np.nan))
    beta2_t = float(model.tstats.get("_iv2", np.nan))
    p2_two = float(model.pvalues.get("_iv2", np.nan))

    # H7: one-tailed p-value for beta1 > 0
    p1_one = p1_two / 2 if beta1 > 0 else 1 - p1_two / 2
    h7_sig = p1_one < 0.05 and beta1 > 0

    print(
        f"  beta1 ({iv_var}):  {beta1:.4f}  SE={beta1_se:.4f}"
        f"  p(one)={p1_one:.4f}  H7={'YES' if h7_sig else 'no'}"
    )
    print(f"  beta2 ({second_iv}): {beta2:.4f}  SE={beta2_se:.4f}")

    meta: Dict[str, Any] = {
        "spec_name": spec_name,
        "sample": sample_name,
        "iv_var": iv_var,
        "second_iv": second_iv,
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "within_r2": float(model.rsquared_within),
        "beta1": beta1,
        "beta1_se": beta1_se,
        "beta1_t": beta1_t,
        "beta1_p_two": p1_two,
        "beta1_p_one": p1_one,
        "beta2": beta2,
        "beta2_se": beta2_se,
        "beta2_t": beta2_t,
        "beta2_p_two": p2_two,
        "h7_sig": h7_sig,
    }

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Emit a LaTeX table of the primary (Main sample) results."""
    tex_path = out_dir / "h7_illiquidity_table.tex"

    def get_res(spec: str, sample: str = "Main") -> Optional[Dict[str, Any]]:
        for r in all_results:
            if r["sample"] == sample and r["spec_name"] == spec:
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

    specs_order = ["QA_Uncertainty", "QA_Weak_Modal", "Pres_Uncertainty"]
    results_main = [get_res(s) for s in specs_order]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H7: Speech Vagueness and Stock Illiquidity (Amihud 2002)}",
        r"\label{tab:h7_illiquidity}",
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r" & (1) QA Uncertainty & (2) QA Weak Modal & (3) Pres Uncertainty \\",
        r"\midrule",
    ]

    row_b = "Manager IV & "
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

    row_b2 = "CEO IV & "
    row_se2 = " & "
    for r in results_main:
        if r:
            row_b2 += f"{fmt_coef(r['beta2'], r['beta2_p_two'])} & "
            row_se2 += f"{fmt_se(r['beta2_se'])} & "
        else:
            row_b2 += " & "
            row_se2 += " & "
    lines.append(row_b2.rstrip(" &") + r" \\")
    lines.append(row_se2.rstrip(" &") + r" \\")

    lines += [
        r"\midrule",
        r"Controls & Yes & Yes & Yes \\",
        r"Firm FE  & Yes & Yes & Yes \\",
        r"Year FE  & Yes & Yes & Yes \\",
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

    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  LaTeX table saved: {tex_path.name}")


def main(panel_path: Optional[str] = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h7_illiquidity" / timestamp

    print("=" * 80)
    print("STAGE 4: Test H7 Speech Vagueness and Stock Illiquidity")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")

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
    panel = pd.read_parquet(
        panel_file,
        columns=[
            "file_name",
            "gvkey",
            "year",
            "ff12_code",
            "start_date",
            "amihud_illiq_lead",
            # All uncertainty specs (primary + baseline per SPECS list)
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            # Base controls
            "Size",
            "Lev",
            "ROA",
            "TobinsQ",
            "Volatility",
            "StockRet",
        ],
    )
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
        sample_names=["Main", "Finance", "Utility"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H7 Speech Vagueness and Stock Illiquidity",
        label="tab:summary_stats_h7",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # Sanity: DV coverage
    n_dv = panel["amihud_illiq_lead"].notna().sum()
    print(f"  DV (amihud_illiq_lead) non-missing: {n_dv:,} / {len(panel):,}")
    if n_dv == 0:
        print("  FATAL: DV is entirely NaN — Stage 3 must be re-run after CRSP fix.")
        return 1

    df_prep = prepare_regression_data(panel)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_results: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Run regressions by sample × spec
    # ------------------------------------------------------------------
    for sample in CONFIG["samples"]:
        df_sample = df_prep[df_prep["sample"] == sample].copy()

        # Min-calls filter (per firm within the regression sample)
        call_counts = df_sample.groupby("gvkey")["file_name"].transform("count")
        df_filtered = df_sample[call_counts >= CONFIG["min_calls"]].copy()

        for spec_name, iv_var, second_iv in SPECS:
            print(f"\n--- {sample} / {spec_name} ---")

            if len(df_filtered) < 100:
                print("  Skipping: insufficient data")
                continue

            model, meta = run_regression(
                df_filtered, spec_name, iv_var, second_iv, sample
            )

            if model is not None:
                all_results.append(meta)
                txt_file = (
                    out_dir / f"regression_{sample}_{spec_name.replace(' ', '_')}.txt"
                )
                with open(txt_file, "w", encoding="utf-8") as f:
                    f.write(str(model.summary))

    # ------------------------------------------------------------------
    # Spontaneity gap test (H7-C): QA beta > Pres beta for Main sample
    # ------------------------------------------------------------------
    print("\n--- H7-C: Spontaneity Gap ---")
    qa_main = next(
        (
            r
            for r in all_results
            if r["sample"] == "Main" and r["spec_name"] == "QA_Uncertainty"
        ),
        None,
    )
    pres_main = next(
        (
            r
            for r in all_results
            if r["sample"] == "Main" and r["spec_name"] == "Pres_Uncertainty"
        ),
        None,
    )

    if qa_main and pres_main:
        beta_qa = qa_main["beta1"]
        beta_pres = pres_main["beta1"]
        gap_sig = beta_qa > beta_pres and qa_main["h7_sig"]
        print(f"  beta(Manager_QA_Uncertainty)   = {beta_qa:.4f}")
        print(f"  beta(Manager_Pres_Uncertainty) = {beta_pres:.4f}")
        print(f"  H7-C (QA > Pres): {'SUPPORTED' if gap_sig else 'not supported'}")
    else:
        print("  H7-C: insufficient results for comparison")

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    _save_latex_table(all_results, out_dir)

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
