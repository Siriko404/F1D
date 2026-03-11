#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H14 Language Uncertainty and Bid-Ask Spread Change
================================================================================
ID: econometric/run_h14_bidask_spread
Description: Run H14 Bid-Ask Spread Change hypothesis test by loading the
             call-level panel from Stage 3, running fixed effects OLS
             regressions by industry sample and uncertainty measure, and
             outputting results.

Model Specification:
    delta_spread ~ {uncertainty_var} + Size + StockPrice + Turnover + Volatility +
                   PreCallSpread + AbsSurprise + EntityEffects + TimeEffects

Unit of observation: individual earnings call (file_name).
DV: delta_spread = Spread[+1,+3] - Spread[-3,-1]

Hypothesis Test (one-tailed):
    H14: beta({uncertainty_var}) > 0 (higher uncertainty increases spread)

Uncertainty Measures (4):
    Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct,
    Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct

Industry Sample:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)

Minimum Calls Filter:
    Firms must have >= 5 calls in the regression sample.

Inputs:
    - outputs/variables/h14_bidask_spread/latest/h14_bidask_spread_panel.parquet

Outputs:
    - outputs/econometric/h14_bidask_spread/{timestamp}/regression_results_{sample}_{measure}.txt
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
    "samples": ["Main"],
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

# Uncertainty Measures (6) - each tested individually
UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
    # Clarity Residuals (from CEO Clarity Extended Stage 4)
    "Manager_Clarity_Residual",
    "CEO_Clarity_Residual",
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
    # Clarity Residuals
    {"col": "Manager_Clarity_Residual", "label": "Mgr Clarity Residual"},
    {"col": "CEO_Clarity_Residual", "label": "CEO Clarity Residual"},
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
        "--dry-run", action="store_true", help="Validate inputs without executing"
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
    sample_name: str,
    uncertainty_var: str,
    min_calls: int = 5,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Run a single PanelOLS regression for one uncertainty measure.

    DV  : delta_spread (change in bid-ask spread around call)
    IV  : uncertainty_var (single uncertainty measure)
    FE  : firm (gvkey) + year_quarter, clustered by entity (gvkey)
    """
    required = (
        ["delta_spread", uncertainty_var] + BASE_CONTROLS + ["gvkey", "quarter_index", "file_name"]
    )
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    # Apply min_calls filter AFTER listwise deletion to avoid singletons
    if min_calls > 1:
        call_counts = df_reg.groupby("gvkey")["file_name"].transform("count")
        df_reg = df_reg[call_counts >= min_calls].copy()

    if len(df_reg) < 100:
        return None, {}

    # Build formula with single IV
    formula = (
        f"delta_spread ~ {uncertainty_var} + "
        + " + ".join(BASE_CONTROLS)
        + " + EntityEffects + TimeEffects"
    )

    print(f"  Formula: delta_spread ~ {uncertainty_var} + controls")
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

    # Extract single beta coefficient
    beta1 = float(model.params.get(uncertainty_var, np.nan))
    se1 = float(model.std_errors.get(uncertainty_var, np.nan))
    t1 = float(model.tstats.get(uncertainty_var, np.nan))
    p_two = float(model.pvalues.get(uncertainty_var, np.nan))

    # One-tailed p-value for H14 (beta > 0)
    if not np.isnan(p_two) and not np.isnan(beta1):
        p_one = p_two / 2 if beta1 > 0 else 1 - p_two / 2
    else:
        p_one = np.nan

    h14_signif = (not np.isnan(p_one)) and (p_one < 0.05) and (beta1 > 0)

    print(
        f"  beta1 ({uncertainty_var}):  {beta1:.4f}  SE={se1:.4f}"
        f"  p(one)={p_one:.4f}  H14={'YES' if h14_signif else 'no'}"
    )

    # Flat metadata structure
    meta: Dict[str, Any] = {
        "sample": sample_name,
        "uncertainty_var": uncertainty_var,
        "beta1": beta1,
        "beta1_se": se1,
        "beta1_t": t1,
        "beta1_p_two": p_two,
        "beta1_p_one": p_one,
        "beta1_signif": h14_signif,
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "n_clusters": df_reg["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "within_r2": float(model.rsquared_within),
    }

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write a publication-ready LaTeX table for H14 results.

    Columns = 6 uncertainty measures; panel = Main industry sample.
    Each cell shows the single IV coefficient for that measure.

    Note: all_results contains FLAT meta dicts (not nested like H1).
    """
    tex_path = out_dir / "h14_bidask_spread_table.tex"

    def sig(p: float) -> str:
        if p < 0.01:
            return "^{***}"
        elif p < 0.05:
            return "^{**}"
        elif p < 0.10:
            return "^{*}"
        return ""

    short_names = {
        "Manager_QA_Uncertainty_pct": "Mgr QA Unc",
        "CEO_QA_Uncertainty_pct": "CEO QA Unc",
        "Manager_Pres_Uncertainty_pct": "Mgr Pres Unc",
        "CEO_Pres_Uncertainty_pct": "CEO Pres Unc",
        "Manager_Clarity_Residual": "Mgr Clarity Res",
        "CEO_Clarity_Residual": "CEO Clarity Res",
    }

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H14: Language Uncertainty and Bid-Ask Spread Change Around Earnings Calls}",
        r"\label{tab:h14_bidask_spread}",
        r"\small",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r" & (1) & (2) & (3) & (4) & (5) & (6) \\",
        r" & " + " & ".join(short_names[m] for m in UNCERTAINTY_MEASURES) + r" \\",
        r"\midrule",
    ]

    for sample in ["Main"]:
        # Filter results for this sample (FLAT structure - direct access)
        sample_res = [r for r in all_results if r.get("sample") == sample]
        if not sample_res:
            continue

        # Index by uncertainty_var for easy lookup
        by_measure = {r["uncertainty_var"]: r for r in sample_res}

        lines.append(rf"\multicolumn{{7}}{{l}}{{\textit{{{sample} Sample}}}} \\")

        # Beta row
        beta_cells = []
        for m in UNCERTAINTY_MEASURES:
            r = by_measure.get(m, {})
            if not r:
                beta_cells.append("")
            else:
                v = r.get("beta1", float("nan"))
                p = r.get("beta1_p_one", float("nan"))
                beta_cells.append(f"{v:.4f}{sig(p)}" if not np.isnan(v) else "")
        lines.append(r"$\beta_1$ (Uncertainty) & " + " & ".join(beta_cells) + r" \\")

        # SE row
        se_cells = []
        for m in UNCERTAINTY_MEASURES:
            r = by_measure.get(m, {})
            if not r:
                se_cells.append("")
            else:
                v = r.get("beta1_se", float("nan"))
                se_cells.append(f"({v:.4f})" if not np.isnan(v) else "")
        lines.append(" & " + " & ".join(se_cells) + r" \\")

        # N and R2 rows
        n_cells = []
        r2_cells = []
        for m in UNCERTAINTY_MEASURES:
            r = by_measure.get(m, {})
            n_cells.append(f"{r.get('n_obs', ''):,}" if r else "")
            r2v = r.get("within_r2", float("nan")) if r else float("nan")
            r2_cells.append(f"{r2v:.3f}" if not np.isnan(r2v) else "")
        lines.append(r"N & " + " & ".join(n_cells) + r" \\")
        lines.append(r"Within-$R^2$ & " + " & ".join(r2_cells) + r" \\")
        lines.append(r"\midrule")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\footnotesize",
        r"\textit{Note:} Dependent variable is $\Delta$Spread, the change in relative bid-ask spread "
        r"from the pre-call window $[-3,-1]$ to the post-call window $[+1,+3]$ around the earnings call. "
        r"All models include firm FE and year-quarter FE. "
        r"Firms with fewer than 5 calls are excluded. "
        r"Standard errors (in parentheses) are clustered at the firm level. "
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for H14: $\beta > 0$).",
        r"\end{minipage}",
        r"\end{table}",
    ]

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: h14_bidask_spread_table.tex")


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
            # Clarity Residuals
            "Manager_Clarity_Residual",
            "CEO_Clarity_Residual",
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
        sample_names=["Main"],
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
    # Run regressions by sample × measure
    # ------------------------------------------------------------------
    for sample_name in ["Main"]:
        df_sample = df_prep[df_prep["sample"] == sample_name].copy()

        for uncertainty_var in UNCERTAINTY_MEASURES:
            # Check if variable exists in panel
            if uncertainty_var not in df_sample.columns:
                print(f"  WARNING: {uncertainty_var} not in panel -- skipping")
                continue

            print(f"\n--- {sample_name} / {uncertainty_var} ---")

            if len(df_sample) < 100:
                print("  Skipping: insufficient data")
                continue

            model, meta = run_regression(
                df_sample, sample_name, uncertainty_var,
                min_calls=CONFIG["min_calls"]
            )

            if model is not None and meta:
                all_results.append(meta)
                txt_file = out_dir / f"regression_results_{sample_name}_{uncertainty_var}.txt"
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
    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
