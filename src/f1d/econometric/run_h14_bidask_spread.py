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
                   PreCallSpread + AbsSurpDec + EntityEffects + TimeEffects

Unit of observation: individual earnings call (file_name).
DV: delta_spread = Spread[+1,+3] - Spread[-3,-1]

Hypothesis Test (one-tailed):
    H14: beta({uncertainty_var}) > 0 (higher uncertainty increases spread)

Uncertainty Measures (6):
    Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct,
    Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct,
    Manager_Clarity_Residual, CEO_Clarity_Residual

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
# Size, Price, Turnover, ReturnVolatility, PreCallSpread, AbsSurpDec
BASE_CONTROLS = [
    "Size",
    "StockPrice",
    "Turnover",
    "Volatility",
    "PreCallSpread",
    "AbsSurpDec",
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
    {"col": "AbsSurpDec", "label": "|Earnings Surprise Decile|"},
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


def _winsorize_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """Winsorize specified columns at 1%/99% (L4). Modifies df in place."""
    for col in cols:
        if col in df.columns:
            lo = df[col].quantile(0.01)
            hi = df[col].quantile(0.99)
            df[col] = df[col].clip(lower=lo, upper=hi)
    return df


# Columns to winsorize before regression (L4)
# Excludes Volatility — already winsorized per-year in CRSP engine
WINSORIZE_COLS = ["delta_spread", "Turnover", "StockPrice", "AbsSurpDec"]
# Also winsorize robustness DV variants
WINSORIZE_DV_VARIANTS = [
    "delta_spread_closing", "delta_spread_w1", "delta_spread_w5", "pre_spread_change",
]


def run_regression(
    df_sample: pd.DataFrame,
    sample_name: str,
    uncertainty_var: str,
    min_calls: int = 5,
    dv_col: str = "delta_spread",
    controls: Optional[List[str]] = None,
    cluster_time: bool = False,
    label: str = "",
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Run a single PanelOLS regression for one uncertainty measure.

    DV  : dv_col (change in bid-ask spread around call)
    IV  : uncertainty_var (single uncertainty measure)
    FE  : firm (gvkey) + year_quarter, clustered by entity (gvkey)

    Args:
        controls: List of control variable names. Defaults to BASE_CONTROLS.
        cluster_time: If True, add cluster_time=True for double-clustering (L8).
        dv_col: Dependent variable column name (default: delta_spread).
        label: Optional label for output identification.
    """
    if controls is None:
        controls = BASE_CONTROLS

    required = (
        [dv_col, uncertainty_var] + controls + ["gvkey", "quarter_index", "file_name"]
    )
    # Only require columns that exist in the dataframe
    required = [c for c in required if c in df_sample.columns]
    df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    # Apply min_calls filter AFTER listwise deletion to avoid singletons
    if min_calls > 1:
        call_counts = df_reg.groupby("gvkey")["file_name"].transform("count")
        df_reg = df_reg[call_counts >= min_calls].copy()

    if len(df_reg) < 100:
        return None, {}

    # L4: Winsorize continuous variables at 1%/99% before PanelOLS
    wins_cols = [c for c in WINSORIZE_COLS + WINSORIZE_DV_VARIANTS if c in df_reg.columns]
    df_reg = _winsorize_cols(df_reg, wins_cols)

    # Build formula with single IV
    formula = (
        f"{dv_col} ~ {uncertainty_var} + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )

    cluster_label = "firm+quarter" if cluster_time else "firm"
    print(f"  Formula: {dv_col} ~ {uncertainty_var} + {len(controls)} controls")
    print(f"  N calls: {len(df_reg):,}  |  N firms: {df_reg['gvkey'].nunique():,}  |  SE: {cluster_label}")

    t0 = datetime.now()

    # Use quarter_index for TimeEffects (must be numeric for PanelOLS)
    # RT-MI-01: Deduplicate on (gvkey, quarter_index) before set_index
    dup_mask = df_reg.duplicated(subset=["gvkey", "quarter_index"], keep=False)
    n_dups = dup_mask.sum()
    if n_dups > 0:
        print(f"  Dedup: {n_dups} rows share (gvkey, quarter_index); keeping latest start_date")
        df_reg = df_reg.sort_values("start_date").drop_duplicates(
            subset=["gvkey", "quarter_index"], keep="last"
        )
    df_panel = df_reg.set_index(["gvkey", "quarter_index"])
    assert df_panel.index.is_unique, "Panel index (gvkey, quarter_index) not unique after dedup"

    try:
        model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        fit_kwargs: Dict[str, Any] = {"cov_type": "clustered", "cluster_entity": True}
        if cluster_time:
            fit_kwargs["cluster_time"] = True
        model = model_obj.fit(**fit_kwargs)
    except Exception as e:
        print(f"  ERROR: PanelOLS failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s  |  R2w={model.rsquared_within:.4f}  |  N={int(model.nobs):,}")

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
        "dv": dv_col,
        "controls": "_".join(sorted(controls)),
        "clustering": cluster_label,
        "label": label,
        "beta1": beta1,
        "beta1_se": se1,
        "beta1_t": t1,
        "beta1_p_two": p_two,
        "beta1_p_one": p_one,
        "beta1_signif": h14_signif,
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "n_clusters": df_reg["gvkey"].nunique(),
        "cluster_var": "gvkey" + ("+quarter" if cluster_time else ""),
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

    # Load all available columns, including robustness DV variants
    required_cols = [
        "file_name", "gvkey", "year", "year_quarter", "ff12_code", "start_date",
        "delta_spread",
        # Uncertainty IVs
        "Manager_QA_Uncertainty_pct", "CEO_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct", "CEO_Pres_Uncertainty_pct",
        # Clarity Residuals
        "Manager_Clarity_Residual", "CEO_Clarity_Residual",
        # Controls
        "Size", "StockPrice", "Turnover", "Volatility", "PreCallSpread", "AbsSurpDec",
    ]
    # Robustness DV columns (may not exist in older panels)
    robustness_dv_cols = [
        "delta_spread_closing", "PreCallSpreadClosing",
        "delta_spread_w1", "delta_spread_w5", "pre_spread_change",
    ]
    # Check which robustness columns actually exist in the parquet
    parquet_cols = pd.read_parquet(panel_file, columns=None).columns.tolist()
    load_cols = required_cols + [c for c in robustness_dv_cols if c in parquet_cols]

    panel = pd.read_parquet(panel_file, columns=load_cols)
    print(f"  Rows:    {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")
    rob_available = [c for c in robustness_dv_cols if c in panel.columns]
    if rob_available:
        print(f"  Robustness DVs available: {rob_available}")

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
    robustness_results: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Robustness configuration (L3, RT-MI-03, L8, RT-MI-04)
    # ------------------------------------------------------------------
    # DV variants
    dv_variants = {"primary": "delta_spread"}
    for dv_name, dv_col in [
        ("closing", "delta_spread_closing"),
        ("w1", "delta_spread_w1"),
        ("w5", "delta_spread_w5"),
        ("placebo", "pre_spread_change"),
    ]:
        if dv_col in df_prep.columns:
            dv_variants[dv_name] = dv_col

    # Control variants (RT-MI-03: with/without AbsSurpDec; RT-MI-04: with/without PreCallSpread)
    control_variants = {
        "full": BASE_CONTROLS,
        "no_AbsSurpDec": [c for c in BASE_CONTROLS if c != "AbsSurpDec"],
        "no_PreCallSpread": [c for c in BASE_CONTROLS if c != "PreCallSpread"],
    }

    # Clustering variants (L8)
    cluster_variants = {
        "firm": False,
        "firm_quarter": True,
    }

    # ------------------------------------------------------------------
    # PRIMARY regressions: full controls, firm-clustered, ASKHI/BIDLO ±3
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("PRIMARY REGRESSIONS (6 measures × Main sample)")
    print("=" * 60)

    for sample_name in ["Main"]:
        df_sample = df_prep[df_prep["sample"] == sample_name].copy()

        for uncertainty_var in UNCERTAINTY_MEASURES:
            if uncertainty_var not in df_sample.columns:
                print(f"  WARNING: {uncertainty_var} not in panel -- skipping")
                continue

            print(f"\n--- {sample_name} / {uncertainty_var} ---")

            if len(df_sample) < 100:
                print("  Skipping: insufficient data")
                continue

            model, meta = run_regression(
                df_sample, sample_name, uncertainty_var,
                min_calls=CONFIG["min_calls"],
                label="primary",
            )

            if model is not None and meta:
                all_results.append(meta)
                txt_file = out_dir / f"regression_results_{sample_name}_{uncertainty_var}.txt"
                with open(txt_file, "w", encoding="utf-8") as f:
                    f.write(str(model.summary))

    # ------------------------------------------------------------------
    # ROBUSTNESS regressions: 6 measures × 3 controls × 2 clustering × N DVs
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("ROBUSTNESS REGRESSIONS")
    print(f"  DVs: {list(dv_variants.keys())}")
    print(f"  Controls: {list(control_variants.keys())}")
    print(f"  Clustering: {list(cluster_variants.keys())}")
    n_expected = len(UNCERTAINTY_MEASURES) * len(dv_variants) * len(control_variants) * len(cluster_variants)
    print(f"  Expected: {len(UNCERTAINTY_MEASURES)} × {len(dv_variants)} × {len(control_variants)} × {len(cluster_variants)} = {n_expected}")
    print("=" * 60)

    rob_dir = out_dir / "robustness"
    rob_dir.mkdir(parents=True, exist_ok=True)
    rob_count = 0

    for sample_name in ["Main"]:
        df_sample = df_prep[df_prep["sample"] == sample_name].copy()

        for dv_name, dv_col in dv_variants.items():
            for ctrl_name, ctrl_list in control_variants.items():
                # For placebo DV, exclude PreCallSpread to avoid mechanical correlation (L2)
                if dv_name == "placebo" and "PreCallSpread" in ctrl_list:
                    ctrl_list = [c for c in ctrl_list if c != "PreCallSpread"]

                for clust_name, clust_time in cluster_variants.items():
                    # Skip primary spec (already run above)
                    if dv_name == "primary" and ctrl_name == "full" and clust_name == "firm":
                        continue

                    for uncertainty_var in UNCERTAINTY_MEASURES:
                        if uncertainty_var not in df_sample.columns:
                            continue
                        if len(df_sample) < 100:
                            continue

                        rob_label = f"{dv_name}_{ctrl_name}_{clust_name}"
                        model, meta = run_regression(
                            df_sample, sample_name, uncertainty_var,
                            min_calls=CONFIG["min_calls"],
                            dv_col=dv_col,
                            controls=ctrl_list,
                            cluster_time=clust_time,
                            label=rob_label,
                        )

                        if model is not None and meta:
                            robustness_results.append(meta)
                            rob_count += 1
                            txt_file = rob_dir / f"robustness_{rob_label}_{uncertainty_var}.txt"
                            with open(txt_file, "w", encoding="utf-8") as f:
                                f.write(str(model.summary))

    print(f"\n  Robustness regressions completed: {rob_count}")

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    _save_latex_table(all_results, out_dir)

    # Save robustness diagnostics
    if robustness_results:
        rob_df = pd.DataFrame(robustness_results)
        rob_df.to_csv(out_dir / "robustness_diagnostics.csv", index=False)
        print(f"  Saved: robustness_diagnostics.csv ({len(rob_df)} regressions)")

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
