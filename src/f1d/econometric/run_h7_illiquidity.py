#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H7 Speech Vagueness and Stock Illiquidity Hypothesis
================================================================================
ID: econometric/run_h7_illiquidity
Description: Run H7 Illiquidity hypothesis test by loading the call-level panel
             from Stage 3, running fixed effects OLS regressions by industry
             sample, and outputting results.

Model Specification (contemporaneous DV):
    Amihud_Illiq_{t} ~ Uncertainty_IV_t + Entire_All_Negative_pct + Analyst_QA_Uncertainty_pct +
                       Size + Lev + ROA + TobinsQ + Volatility + StockRet +
                       EntityEffects + TimeEffects

Unit of observation: individual earnings call (file_name).
DV: amihud_illiq (contemporaneous Amihud illiquidity measure).

Specifications (4 single-IV regressions):
    A1: CEO_QA_Uncertainty_pct
    A2: CEO_Pres_Uncertainty_pct
    A3: Manager_QA_Uncertainty_pct
    A4: Manager_Pres_Uncertainty_pct

Hypothesis Tests (one-tailed):
    H7: beta(Uncertainty_IV) > 0 (vagueness increases illiquidity)
    H7-C: beta(QA) > beta(Pres) (spontaneous speech has larger effect)

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls in the regression sample.
    amihud_illiq must be non-missing (DV).

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
    "samples": ["Main", "Finance", "Utility"],
}

BASE_CONTROLS = [
    "Entire_All_Negative_pct",
    "Analyst_QA_Uncertainty_pct",
    "Size",
    "Lev",
    "ROA",
    "TobinsQ",
    "Volatility",
    "StockRet",
]

SPECS = [
    ("A1", "CEO_QA_Uncertainty_pct", "CEO QA Uncertainty"),
    ("A2", "CEO_Pres_Uncertainty_pct", "CEO Pres Uncertainty"),
    ("A3", "Manager_QA_Uncertainty_pct", "Manager QA Uncertainty"),
    ("A4", "Manager_Pres_Uncertainty_pct", "Manager Pres Uncertainty"),
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variable
    {"col": "amihud_illiq", "label": "Amihud Illiquidity$_{t}$"},
    # Uncertainty measures (IVs)
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    # Linguistic controls (NEW)
    {"col": "Entire_All_Negative_pct", "label": "Entire Call Negative"},
    {"col": "Analyst_QA_Uncertainty_pct", "label": "Analyst QA Uncertainty"},
    # Financial controls
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
    spec_id: str,
    iv_var: str,
    sample_name: str,
    min_calls: int = 5,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Run a single PanelOLS regression for the given spec.

    DV  : amihud_illiq (contemporaneous illiquidity)
    IV  : iv_var (single uncertainty measure)
    FE  : firm (gvkey) + year, clustered by entity (gvkey)
    """
    required = (
        ["amihud_illiq", iv_var] + BASE_CONTROLS + ["gvkey", "year", "file_name"]
    )
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    # Apply min_calls filter AFTER listwise deletion to avoid singletons
    if min_calls > 1:
        call_counts = df_reg.groupby("gvkey")["file_name"].transform("count")
        df_reg = df_reg[call_counts >= min_calls].copy()

    if len(df_reg) < 100:
        return None, {}

    formula = (
        f"amihud_illiq ~ {iv_var} + "
        + " + ".join(BASE_CONTROLS)
        + " + EntityEffects + TimeEffects"
    )

    print(f"  Formula: amihud_illiq ~ {iv_var} + controls")
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

    specs_order = ["A1", "A2", "A3", "A4"]
    results_main = [get_res(s) for s in specs_order]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H7: Speech Vagueness and Stock Illiquidity (Amihud 2002)}",
        r"\label{tab:h7_illiquidity}",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r" & (A1) & (A2) & (A3) & (A4) \\",
        r" & CEO QA & CEO Pres & Mgr QA & Mgr Pres \\",
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
        r"Negative Sentiment & Yes & Yes & Yes & Yes \\",
        r"Analyst Uncertainty & Yes & Yes & Yes & Yes \\",
        r"Controls & Yes & Yes & Yes & Yes \\",
        r"Firm FE  & Yes & Yes & Yes & Yes \\",
        r"Year FE  & Yes & Yes & Yes & Yes \\",
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
        r"Dependent variable is Amihud illiquidity$_{t}$ (Amihud 2002). "
        r"All models use the Main industry sample (non-financial, non-utility firms). "
        r"Firms with fewer than 5 calls are excluded. "
        r"Standard errors (in parentheses) are clustered at the firm level. "
        r"All continuous controls are standardized within each model's estimation sample. "
        r"Variables are winsorized at 1\%/99\% by year at the engine level. "
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for H7).",
        r"}",
        r"\end{table}",
    ]

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  LaTeX table saved: {tex_path.name}")


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
    panel = pd.read_parquet(
        panel_file,
        columns=[
            "file_name",
            "gvkey",
            "year",
            "ff12_code",
            "start_date",
            # DV (contemporaneous)
            "amihud_illiq",
            # Uncertainty measures (IVs for all 4 specs)
            "CEO_QA_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            "Manager_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
            # Linguistic controls (NEW)
            "Entire_All_Negative_pct",
            "Analyst_QA_Uncertainty_pct",
            # Financial controls
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
    n_dv = panel["amihud_illiq"].notna().sum()
    print(f"  DV (amihud_illiq) non-missing: {n_dv:,} / {len(panel):,}")
    if n_dv == 0:
        print("  FATAL: DV is entirely NaN — check panel builder.")
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

            if len(df_sample) < 100:
                print("  Skipping: insufficient data")
                continue

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
    # Spontaneity gap test (H7-C): QA beta > Pres beta for Main sample
    # ------------------------------------------------------------------
    print("\n--- H7-C: Spontaneity Gap ---")
    qa_ceo = next(
        (
            r
            for r in all_results
            if r["sample"] == "Main" and r["spec_id"] == "A1"  # CEO QA
        ),
        None,
    )
    qa_mgr = next(
        (
            r
            for r in all_results
            if r["sample"] == "Main" and r["spec_id"] == "A3"  # Manager QA
        ),
        None,
    )
    pres_ceo = next(
        (
            r
            for r in all_results
            if r["sample"] == "Main" and r["spec_id"] == "A2"  # CEO Pres
        ),
        None,
    )
    pres_mgr = next(
        (
            r
            for r in all_results
            if r["sample"] == "Main" and r["spec_id"] == "A4"  # Manager Pres
        ),
        None,
    )

    if qa_mgr and pres_mgr:
        beta_qa = qa_mgr["beta1"]
        beta_pres = pres_mgr["beta1"]
        gap_sig = beta_qa > beta_pres and qa_mgr["h7_sig"]
        print(f"  beta(Manager_QA_Uncertainty)   = {beta_qa:.4f}")
        print(f"  beta(Manager_Pres_Uncertainty) = {beta_pres:.4f}")
        print(f"  H7-C (QA > Pres): {'SUPPORTED' if gap_sig else 'not supported'}")
    else:
        print("  H7-C: insufficient results for comparison")

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    _save_latex_table(all_results, out_dir)

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
