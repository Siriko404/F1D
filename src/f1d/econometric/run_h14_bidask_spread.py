#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H14 Language Uncertainty and Bid-Ask Spread Change
================================================================================
ID: econometric/run_h14_bidask_spread
Description: Run H14 Bid-Ask Spread Change hypothesis test by loading the
             call-level panel from Stage 3, running fixed effects OLS
             regressions by industry sample, and outputting results.

Model Specification:
    delta_spread ~ Uncertainty_t + Size + StockPrice + Turnover + Volatility +
                   PreCallSpread + AbsSurprise + EntityEffects + TimeEffects

Unit of observation: individual earnings call (file_name).
DV: delta_spread = Spread[+1,+3] - Spread[-3,-1]

Hypothesis Test (one-tailed):
    H14: beta(Uncertainty) > 0 (higher uncertainty increases spread)

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls in the regression sample.

Inputs:
    - outputs/variables/h14_bidask_spread/latest/h14_bidask_spread_panel.parquet

Outputs:
    - outputs/econometric/h14_bidask_spread/{timestamp}/regression_{sample}_{spec}.txt
    - outputs/econometric/h14_bidask_spread/{timestamp}/h14_bidask_spread_table.tex
    - outputs/econometric/h14_bidask_spread/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h14_bidask_spread/{timestamp}/summary_stats.csv
    - outputs/econometric/h14_bidask_spread/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h14_bidask_spread_panel)
    - Uses: linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-03-06
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

# H14 Controls per H14.txt:
# Size, Price, Turnover, ReturnVolatility, PreCallSpread, AbsSurprise
BASE_CONTROLS = [
    "Size",
    "StockPrice",
    "Turnover",
    "Volatility",
    "PreCallSpread",
    "AbsSurprise",
]

# Specifications:
# (1) QA_Uncertainty only
# (2) Pres_Uncertainty only
# (3) Joint (both QA + Pres)
SPECS = [
    ("QA_Uncertainty", ["Manager_QA_Uncertainty_pct", "CEO_QA_Uncertainty_pct"]),
    ("Pres_Uncertainty", ["Manager_Pres_Uncertainty_pct", "CEO_Pres_Uncertainty_pct"]),
    ("Joint", [
        "Manager_QA_Uncertainty_pct", "CEO_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct", "CEO_Pres_Uncertainty_pct"
    ]),
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variable
    {"col": "delta_spread", "label": "$\\Delta$ Spread (post-pre)"},
    {"col": "PreCallSpread", "label": "Pre-Call Spread"},
    # Primary uncertainty measures
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    # Controls
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "StockPrice", "label": "Stock Price"},
    {"col": "Turnover", "label": "Share Turnover"},
    {"col": "Volatility", "label": "Return Volatility"},
    {"col": "AbsSurprise", "label": "|Earnings Surprise|"},
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H14 Language Uncertainty and Bid-Ask Spread Change (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H14 panel parquet"
    )
    return parser.parse_args()


def prepare_regression_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Derive computed columns needed for regressions."""
    df = panel.copy()

    # Year from start_date (fallback if not present)
    if "year" not in df.columns:
        df["year"] = pd.to_datetime(df["start_date"], errors="coerce").dt.year

    # Ensure quarter column exists (needed for numeric time index)
    if "quarter" not in df.columns:
        df["start_date_dt"] = pd.to_datetime(df["start_date"], errors="coerce")
        df["quarter"] = df["start_date_dt"].dt.quarter

    # Create NUMERIC quarter index for PanelOLS (time dimension must be numeric)
    # quarter_index = year * 4 + quarter (e.g., 2010Q1 = 8041, 2010Q2 = 8042)
    df["quarter_index"] = df["year"] * 4 + df["quarter"]

    # Ensure year_quarter exists for display purposes
    if "year_quarter" not in df.columns:
        df["year_quarter"] = (
            df["year"].astype(str) + "_Q" + df["quarter"].astype(str)
        )

    return df


def run_regression(
    df_sample: pd.DataFrame,
    spec_name: str,
    iv_vars: List[str],
    sample_name: str,
    min_calls: int = 5,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Run a single PanelOLS regression for the given spec.

    DV  : delta_spread (change in bid-ask spread around call)
    IVs : iv_vars (uncertainty measures per specification)
    FE  : firm (gvkey) + year_quarter, clustered by entity (gvkey)
    """
    required = (
        ["delta_spread"] + iv_vars + BASE_CONTROLS + ["gvkey", "quarter_index", "file_name"]
    )
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    # Apply min_calls filter AFTER listwise deletion to avoid singletons
    if min_calls > 1:
        call_counts = df_reg.groupby("gvkey")["file_name"].transform("count")
        df_reg = df_reg[call_counts >= min_calls].copy()

    if len(df_reg) < 100:
        return None, {}

    # Build formula using actual variable names
    iv_formula = " + ".join(iv_vars)

    formula = (
        f"delta_spread ~ {iv_formula} + "
        + " + ".join(BASE_CONTROLS)
        + " + EntityEffects + TimeEffects"
    )

    print(f"  Formula: delta_spread ~ {' + '.join(iv_vars)} + controls")
    print(f"  N calls: {len(df_reg):,}  |  N firms: {df_reg['gvkey'].nunique():,}")
    print("  Estimating with firm-clustered SEs...")

    t0 = datetime.now()

    # Use quarter_index for TimeEffects (must be numeric for PanelOLS)
    df_panel = df_reg.set_index(["gvkey", "quarter_index"])

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

    # Extract coefficients for all IVs using actual variable names
    betas = {}
    for iv in iv_vars:
        betas[iv] = {
            "beta": float(model.params.get(iv, np.nan)),
            "se": float(model.std_errors.get(iv, np.nan)),
            "t": float(model.tstats.get(iv, np.nan)),
            "p_two": float(model.pvalues.get(iv, np.nan)),
        }
        # One-tailed p-value for H14 (beta > 0)
        beta_val = betas[iv]["beta"]
        p_two = betas[iv]["p_two"]
        betas[iv]["p_one"] = p_two / 2 if beta_val > 0 else 1 - p_two / 2

    # Primary IV for H14 test is Manager_QA_Uncertainty or Manager_Pres_Uncertainty
    primary_iv = iv_vars[0]  # First IV in the spec
    beta1 = betas[primary_iv]["beta"]
    p1_one = betas[primary_iv]["p_one"]
    h14_sig = p1_one < 0.05 and beta1 > 0

    print(
        f"  beta1 ({primary_iv}):  {beta1:.4f}  SE={betas[primary_iv]['se']:.4f}"
        f"  p(one)={p1_one:.4f}  H14={'YES' if h14_sig else 'no'}"
    )

    meta: Dict[str, Any] = {
        "spec_name": spec_name,
        "sample": sample_name,
        "iv_vars": iv_vars,
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "n_clusters": df_reg["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "within_r2": float(model.rsquared_within),
        "betas": betas,
        "h14_sig": h14_sig,
    }

    # Flatten betas for CSV output
    for iv in iv_vars:
        meta[f"beta_{iv}"] = betas[iv]["beta"]
        meta[f"se_{iv}"] = betas[iv]["se"]
        meta[f"p_one_{iv}"] = betas[iv]["p_one"]

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Emit a LaTeX table of the primary (Main sample) results."""
    tex_path = out_dir / "h14_bidask_spread_table.tex"

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

    specs_order = ["QA_Uncertainty", "Pres_Uncertainty", "Joint"]
    results_main = [get_res(s) for s in specs_order]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H14: Language Uncertainty and Bid-Ask Spread Change Around Earnings Calls}",
        r"\label{tab:h14_bidask_spread}",
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r" & (1) QA Uncertainty & (2) Pres Uncertainty & (3) Joint \\",
        r"\midrule",
    ]

    # Manager QA Uncertainty row (in specs 1 and 3)
    row_b = "Manager QA Uncertainty & "
    row_se = " & "
    for i, r in enumerate(results_main):
        if r and "Manager_QA_Uncertainty_pct" in r.get("iv_vars", []):
            beta_info = r["betas"].get("Manager_QA_Uncertainty_pct", {})
            row_b += f"{fmt_coef(beta_info.get('beta', np.nan), beta_info.get('p_one', 1))} & "
            row_se += f"{fmt_se(beta_info.get('se', np.nan))} & "
        else:
            row_b += " & "
            row_se += " & "
    lines.append(row_b.rstrip(" &") + r" \\")
    lines.append(row_se.rstrip(" &") + r" \\")

    # CEO QA Uncertainty row
    row_b = "CEO QA Uncertainty & "
    row_se = " & "
    for r in results_main:
        if r and "CEO_QA_Uncertainty_pct" in r.get("iv_vars", []):
            beta_info = r["betas"].get("CEO_QA_Uncertainty_pct", {})
            row_b += f"{fmt_coef(beta_info.get('beta', np.nan), beta_info.get('p_one', 1))} & "
            row_se += f"{fmt_se(beta_info.get('se', np.nan))} & "
        else:
            row_b += " & "
            row_se += " & "
    lines.append(row_b.rstrip(" &") + r" \\")
    lines.append(row_se.rstrip(" &") + r" \\")

    # Manager Pres Uncertainty row (in specs 2 and 3)
    row_b = "Manager Pres Uncertainty & "
    row_se = " & "
    for r in results_main:
        if r and "Manager_Pres_Uncertainty_pct" in r.get("iv_vars", []):
            beta_info = r["betas"].get("Manager_Pres_Uncertainty_pct", {})
            row_b += f"{fmt_coef(beta_info.get('beta', np.nan), beta_info.get('p_one', 1))} & "
            row_se += f"{fmt_se(beta_info.get('se', np.nan))} & "
        else:
            row_b += " & "
            row_se += " & "
    lines.append(row_b.rstrip(" &") + r" \\")
    lines.append(row_se.rstrip(" &") + r" \\")

    # CEO Pres Uncertainty row
    row_b = "CEO Pres Uncertainty & "
    row_se = " & "
    for r in results_main:
        if r and "CEO_Pres_Uncertainty_pct" in r.get("iv_vars", []):
            beta_info = r["betas"].get("CEO_Pres_Uncertainty_pct", {})
            row_b += f"{fmt_coef(beta_info.get('beta', np.nan), beta_info.get('p_one', 1))} & "
            row_se += f"{fmt_se(beta_info.get('se', np.nan))} & "
        else:
            row_b += " & "
            row_se += " & "
    lines.append(row_b.rstrip(" &") + r" \\")
    lines.append(row_se.rstrip(" &") + r" \\")

    lines += [
        r"\midrule",
        r"Controls & Yes & Yes & Yes \\",
        r"Firm FE  & Yes & Yes & Yes \\",
        r"Year-Quarter FE  & Yes & Yes & Yes \\",
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
        r"Dependent variable is $\Delta$Spread, the change in relative bid-ask spread "
        r"from the pre-call window $[-3,-1]$ to the post-call window $[+1,+3]$ around the earnings call. "
        r"All models use the Main industry sample (non-financial, non-utility firms). "
        r"Firms with fewer than 5 calls are excluded. "
        r"Standard errors (in parentheses) are clustered at the firm level. "
        r"All continuous controls are standardized within each model's estimation sample. "
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for H14).",
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
    out_dir = root / "outputs" / "econometric" / "h14_bidask_spread" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H14_BidAskSpread",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H14 Language Uncertainty and Bid-Ask Spread Change")
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
                root / "outputs" / "variables" / "h14_bidask_spread",
                required_file="h14_bidask_spread_panel.parquet",
            )
            panel_file = panel_dir / "h14_bidask_spread_panel.parquet"
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
            "year_quarter",
            "ff12_code",
            "start_date",
            "delta_spread",
            # Uncertainty IVs
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            # Controls
            "Size",
            "StockPrice",
            "Turnover",
            "Volatility",
            "PreCallSpread",
            "AbsSurprise",
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
        caption="Summary Statistics — H14 Language Uncertainty and Bid-Ask Spread Change",
        label="tab:summary_stats_h14",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # Sanity: DV coverage
    n_dv = panel["delta_spread"].notna().sum()
    print(f"  DV (delta_spread) non-missing: {n_dv:,} / {len(panel):,}")
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

        for spec_name, iv_vars in SPECS:
            print(f"\n--- {sample} / {spec_name} ---")

            if len(df_sample) < 100:
                print("  Skipping: insufficient data")
                continue

            model, meta = run_regression(
                df_sample, spec_name, iv_vars, sample,
                min_calls=CONFIG["min_calls"]
            )

            if model is not None:
                all_results.append(meta)
                txt_file = (
                    out_dir / f"regression_{sample}_{spec_name.replace(' ', '_')}.txt"
                )
                with open(txt_file, "w", encoding="utf-8") as f:
                    f.write(str(model.summary))

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
        generate_attrition_table(attrition_stages, out_dir, "H14 Bid-Ask Spread")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h14_bidask_spread_table.tex",
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
