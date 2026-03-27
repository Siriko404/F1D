#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H16 R&D Investment Intensity Hypothesis
================================================================================
ID: econometric/test_h16_rd_sales
Description: Run H16 R&D Investment Intensity hypothesis test using 8 model specifications
             with 4 simultaneous uncertainty IVs, varying DV, FE type,
             and control set. Main sample only.

Following Jiang, John, and Larsen (2021): RDSales = xrdy / saley.
Missing R&D expense set to zero; nonpositive sales excluded.

Model Specifications (12 columns in one table):
    Cols 1-4:   DV = RDSales (contemporaneous), Calendar Year FE
    Cols 5-6:   DV = RDSales (contemporaneous), Year-Quarter FE
    Cols 7-10:  DV = RDSales_lead (t+1), Calendar Year FE
    Cols 11-12: DV = RDSales_lead (t+1), Year-Quarter FE
    Odd cols:  Industry FE (FF12 dummies)
    Even cols: Firm FE
    Cols 1-2, 7-8:   Base controls
    Cols 3-6, 9-12:  Extended controls

Key Independent Variables (4, all enter simultaneously):
    CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct,
    Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct,

Base Controls (8):
    Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, DividendPayer, OCF_Volatility
    NOTE: RD_Intensity EXCLUDED — DV is R&D-based (bad control).
    NOTE: CapexAt included (not the DV here, unlike H13).

Extended Controls (Base + 3):
    + SalesGrowth, CashFlow, Volatility

Lead specs (cols 5-8) include RDSales as lagged DV control.

Sample: Main only (FF12 codes 1-7, 9-10, 12).

Hypothesis Test (two-tailed):
    H16: beta(uncertainty_var) != 0 — no directional prediction.
    Stars based on two-tailed p-values.

FE Time Index: fyearq_int (fiscal year); cal_yr_qtr (calendar year-quarter) for YQ specs.
Standard Errors: Firm-clustered (groups=gvkey).
Industry FE: Absorbed via PanelOLS constructor other_effects (not C() dummies).

Inputs:
    - outputs/variables/h16_rd_sales/latest/h16_rd_sales_panel.parquet

Outputs:
    - outputs/econometric/h16_rd_sales/{timestamp}/regression_results_col{1-12}.txt
    - outputs/econometric/h16_rd_sales/{timestamp}/h16_rd_sales_table.tex
    - outputs/econometric/h16_rd_sales/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h16_rd_sales/{timestamp}/summary_stats.csv
    - outputs/econometric/h16_rd_sales/{timestamp}/summary_stats.tex
    - outputs/econometric/h16_rd_sales/{timestamp}/report_step4_H16.md
    - outputs/econometric/h16_rd_sales/{timestamp}/sample_attrition.csv
    - outputs/econometric/h16_rd_sales/{timestamp}/run_manifest.json

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h16_rd_sales_panel)
    - Uses: linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-03-24
================================================================================
"""

from __future__ import annotations

import argparse
import sys
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
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

KEY_IVS = [
    "CEO_QA_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
    "Manager_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
]

# NOTE: RD_Intensity EXCLUDED — DV is R&D-based (bad control: same numerator concept).
# NOTE: CapexAt included (not the DV here, unlike H13).
BASE_CONTROLS = [
    "Size",
    "TobinsQ",
    "ROA",
    "BookLev",
    "CashHoldings",
    "CapexAt",
    "DividendPayer",
    "OCF_Volatility",
    "Lagged_DV",
]

EXTENDED_CONTROLS = BASE_CONTROLS + [
    "SalesGrowth",
    "CashFlow",
    "Volatility",
]

MODEL_SPECS = [
    # Contemporaneous — Calendar Year FE
    {"col": 1,  "dv": "RDSales",      "fe": "industry",    "controls": "base"},
    {"col": 2,  "dv": "RDSales",      "fe": "firm",        "controls": "base"},
    {"col": 3,  "dv": "RDSales",      "fe": "industry",    "controls": "extended"},
    {"col": 4,  "dv": "RDSales",      "fe": "firm",        "controls": "extended"},
    # Contemporaneous — Year-Quarter FE (Extended controls only)
    {"col": 5,  "dv": "RDSales",      "fe": "industry_yq", "controls": "extended"},
    {"col": 6,  "dv": "RDSales",      "fe": "firm_yq",     "controls": "extended"},
    # Lead: next fiscal year — Calendar Year FE
    {"col": 7,  "dv": "RDSales_lead", "fe": "industry",    "controls": "base"},
    {"col": 8,  "dv": "RDSales_lead", "fe": "firm",        "controls": "base"},
    {"col": 9,  "dv": "RDSales_lead", "fe": "industry",    "controls": "extended"},
    {"col": 10, "dv": "RDSales_lead", "fe": "firm",        "controls": "extended"},
    # Lead: next fiscal year — Year-Quarter FE (Extended controls only)
    {"col": 11, "dv": "RDSales_lead", "fe": "industry_yq", "controls": "extended"},
    {"col": 12, "dv": "RDSales_lead", "fe": "firm_yq",     "controls": "extended"},
]

MIN_CALLS_PER_FIRM = 5

VARIABLE_LABELS = {
    "CEO_QA_Uncertainty_pct": "CEO QA Uncertainty",
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
    "Manager_QA_Uncertainty_pct": "Mgr QA Uncertainty",
    "Manager_Pres_Uncertainty_pct": "Mgr Pres Uncertainty",
}

# Summary statistics variable list
SUMMARY_STATS_VARS = [
    {"col": "RDSales", "label": "R\\&D / Sales (t)"},
    {"col": "RDSales_lead", "label": "R\\&D / Sales (t+1)"},
    # Key IVs
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    # Base controls
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "BookLev", "label": "Leverage"},
    {"col": "CashHoldings", "label": "Cash Holdings"},
    {"col": "CapexAt", "label": "CapEx / Assets"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
    {"col": "OCF_Volatility", "label": "OCF Volatility"},
    # Extended controls
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "CashFlow", "label": "Cash Flow"},
    {"col": "Volatility", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: Test H16 R&D Investment Intensity Hypothesis (call-level)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate inputs without executing"
    )
    parser.add_argument(
        "--panel-path",
        type=str,
        default=None,
        help="Path to panel parquet file (default: latest from Stage 3)",
    )
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load call-level H16 panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h16_rd_sales",
            required_file="h16_rd_sales_panel.parquet",
        )
        panel_file = panel_dir / "h16_rd_sales_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    columns = [
        "gvkey", "year", "fyearq_int", "ff12_code", "start_date",
        # DVs + lagged DV
        "RDSales", "RDSales_lead", "RDSales_lag",
        # Key IVs
        "CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct",
        "Manager_QA_Uncertainty_pct", "Manager_Pres_Uncertainty_pct",
        # Base controls
        "Size", "TobinsQ", "ROA",
        "BookLev", "CashHoldings", "CapexAt", "DividendPayer", "OCF_Volatility",
        # Extended controls
        "SalesGrowth", "CashFlow", "Volatility",
    ]

    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    # Build calendar year-quarter index for YQ FE specs
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} ({100*n_yr_qtr/len(panel):.1f}%)")

    return panel


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only (exclude Finance ff12=11, Utility ff12=8)."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample filter: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(
    panel: pd.DataFrame,
    spec: Dict[str, Any],
) -> pd.DataFrame:
    """Prepare panel for a specific model specification."""
    dv = spec["dv"]
    fe_type = spec["fe"]
    controls = BASE_CONTROLS if spec["controls"] == "base" else EXTENDED_CONTROLS

    # Create Lagged_DV: always lag of the base DV (t-1)
    base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")
    lag_col = f"{base_dv}_lag"
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    required = [dv] + KEY_IVS + controls + ["gvkey", "fyearq_int", "ff12_code"]
    if fe_type.endswith("_yq"):
        required.append("cal_yr_qtr")

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(
            f"Required columns missing from panel: {missing}. Check Stage 3 output."
        )

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Coverage check
    for iv in KEY_IVS:
        pct_missing = df[iv].isna().mean() * 100
        if pct_missing > 50:
            print(f"  WARNING: {iv} has {pct_missing:.1f}% missing values")

    # Drop rows where DV is NaN
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Minimum calls per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()
    print(
        f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
        f"{len(df):,} calls, {df['gvkey'].nunique():,} firms"
    )

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_prepared: pd.DataFrame,
    spec: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS regression for a given model specification.

    Industry FE: absorbed via other_effects (not dummies) + TimeEffects
    Firm FE: EntityEffects + TimeEffects (via from_formula)

    All models: firm-clustered SEs, drop_absorbed=True.
    Time index: fyearq_int (fiscal year).
    """
    col_num = spec["col"]
    dv = spec["dv"]
    fe_type = spec["fe"]
    controls = BASE_CONTROLS if spec["controls"] == "base" else EXTENDED_CONTROLS

    # Determine time index based on FE type
    time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"
    base_fe = fe_type.replace("_yq", "")
    fe_label = f"{'Industry(FF12)' if base_fe == 'industry' else 'Firm'} + {'CalYrQtr' if fe_type.endswith('_yq') else 'CalYear'}"

    print(f"\n" + "=" * 60)
    print(f"Running regression: Col ({col_num}) | DV={dv} | FE={fe_label} | Controls={spec['controls']}")
    print("=" * 60)

    if len(df_prepared) < 100:
        print(f"  WARNING: Too few observations ({len(df_prepared)}), skipping")
        return None, {}

    exog = KEY_IVS + controls

    print(f"  FE: {fe_label}")
    print(f"  N calls: {len(df_prepared):,}  |  N firms: {df_prepared['gvkey'].nunique():,}")
    print(f"  Controls: {spec['controls']} ({len(controls)} vars)")
    print("  Estimating with firm-clustered SEs via PanelOLS...")
    t0 = datetime.now()

    # MultiIndex: gvkey (entity) x time_col
    df_panel = df_prepared.set_index(["gvkey", time_col])

    try:
        if base_fe == "industry":
            # Absorb industry FE via other_effects (not C() dummies)
            dependent_data = df_panel[dv]
            exog_data = df_panel[exog]
            industry_data = df_panel["ff12_code"]
            model_obj = PanelOLS(
                dependent=dependent_data,
                exog=exog_data,
                entity_effects=False,
                time_effects=True,
                other_effects=industry_data,
                drop_absorbed=True,
                check_rank=False,
            )
            model = model_obj.fit(cov_type="clustered", cluster_entity=True)
        else:
            # Firm FE: EntityEffects + TimeEffects
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
            model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {elapsed:.1f}s")
    print(f"  R-squared (within): {model.rsquared_within:.4f}")
    print(f"  N obs: {int(model.nobs):,}")

    # Build metadata with per-IV two-tailed p-values (H16: no directional prediction)
    meta: Dict[str, Any] = {
        "col": col_num,
        "dv": dv,
        "fe": fe_type,
        "controls": spec["controls"],
        "n_obs": int(model.nobs),
        "n_firms": df_prepared["gvkey"].nunique(),
        "within_r2": float(model.rsquared_within),
    }

    # Per-IV coefficients with two-tailed p-values
    for iv in KEY_IVS:
        beta = float(model.params.get(iv, np.nan))
        se = float(model.std_errors.get(iv, np.nan))
        p_two = float(model.pvalues.get(iv, np.nan))
        t_stat = float(model.tstats.get(iv, np.nan))

        meta[f"{iv}_beta"] = beta
        meta[f"{iv}_se"] = se
        meta[f"{iv}_t"] = t_stat
        meta[f"{iv}_p_two"] = p_two

        stars = _sig_stars(p_two)
        print(f"  {iv}: beta={beta:.4f} SE={se:.4f} p2={p_two:.4f} {stars}")

    return model, meta


# ==============================================================================
# Output Generation
# ==============================================================================


def _sig_stars(p: float) -> str:
    """Return significance stars for two-tailed p-value."""
    if np.isnan(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write unified 12-column LaTeX table with stars + SE in parentheses."""
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    n_cols = 12

    def fmt_coef(val: float, stars: str) -> str:
        if np.isnan(val):
            return ""
        return f"{val:.4f}{stars}"

    def fmt_se(val: float) -> str:
        if np.isnan(val):
            return ""
        return f"({val:.4f})"

    def fmt_int(val: int) -> str:
        return f"{val:,}"

    def fmt_r2(val: float) -> str:
        if np.isnan(val):
            return ""
        if abs(val) < 0.001:
            return f"{val:.2e}"
        return f"{val:.3f}"

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Speech Uncertainty and R\&D Investment Intensity}",
        r"\label{tab:h16_rd_sales}",
        r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}",
        r"\toprule",
    ]

    # Column numbers
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")

    # DV headers with multicolumn
    lines.append(
        r" & \multicolumn{6}{c}{RDSales}"
        r" & \multicolumn{6}{c}{RDSales\_lead} \\"
    )
    lines.append(r"\cmidrule(lr){2-7} \cmidrule(lr){8-13}")
    lines.append(r"\midrule")

    # Key IV rows (coefficient + SE for each)
    for iv in KEY_IVS:
        label = VARIABLE_LABELS.get(iv, iv)
        coef_cells = []
        for c in range(1, n_cols + 1):
            meta = results_by_col.get(c, {})
            beta = meta.get(f"{iv}_beta", np.nan)
            p_two = meta.get(f"{iv}_p_two", np.nan)
            coef_cells.append(fmt_coef(beta, _sig_stars(p_two)))
        lines.append(f"{label} & " + " & ".join(coef_cells) + r" \\")

        se_cells = []
        for c in range(1, n_cols + 1):
            meta = results_by_col.get(c, {})
            se = meta.get(f"{iv}_se", np.nan)
            se_cells.append(fmt_se(se))
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # Controls indicator
    ctrl_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        ctrl_cells.append("Extended" if meta.get("controls") == "extended" else "Base")
    lines.append(r"Controls & " + " & ".join(ctrl_cells) + r" \\")

    # Lagged DV indicator (always Yes — Lagged_DV is in BASE_CONTROLS)
    lines.append(r"Lagged DV & " + " & ".join(["Yes"] * n_cols) + r" \\")

    # FE indicators
    ind_fe_cells = []
    firm_fe_cells = []
    year_fe_cells = []
    yr_qtr_fe_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        fe = meta.get("fe", "")
        base_fe = fe.replace("_yq", "") if fe else ""
        is_yq = fe.endswith("_yq") if fe else False
        ind_fe_cells.append("Yes" if base_fe == "industry" else "")
        firm_fe_cells.append("Yes" if base_fe == "firm" else "")
        year_fe_cells.append("Yes" if not is_yq else "")
        yr_qtr_fe_cells.append("Yes" if is_yq else "")
    lines.append(r"Industry FE & " + " & ".join(ind_fe_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_fe_cells) + r" \\")
    lines.append(r"Calendar Year FE & " + " & ".join(year_fe_cells) + r" \\")
    lines.append(r"Year-Quarter FE & " + " & ".join(yr_qtr_fe_cells) + r" \\")

    lines.append(r"\midrule")

    # N
    n_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        n_val = meta.get("n_obs", 0)
        n_cells.append(fmt_int(n_val) if n_val else "")
    lines.append(r"N & " + " & ".join(n_cells) + r" \\")

    # Within R-sq
    r2_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        r2_cells.append(fmt_r2(meta.get("within_r2", np.nan)))
    lines.append(r"Within-R$^2$ & " + " & ".join(r2_cells) + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed). ",
        r"Standard errors (in parentheses) clustered at firm level. ",
        r"Main sample (excludes financial and utility firms). ",
        r"Industry FE uses Fama-French 12 industry dummies. ",
        r"R\&D investment intensity follows Jiang, John, and Larsen (2021): ",
        r"xrdy / saley (annual Q4-only). Missing R\&D set to zero; nonpositive sales excluded. ",
        r"Lead specs (cols 7--12) include contemporaneous RDSales as lagged DV control. ",
        r"Variables winsorized at 1\%/99\% by year at engine level. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h16_rd_sales_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: h16_rd_sales_table.tex")


def save_outputs(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> pd.DataFrame:
    """Save regression outputs."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Save individual regression result text files
    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        col_num = meta.get("col", 0)
        fname = f"regression_results_col{col_num}.txt"
        fpath = out_dir / fname
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"Model Specification: Col ({col_num})\n")
            f.write(f"DV: {meta.get('dv')}\n")
            f.write(f"FE: {meta.get('fe')}\n")
            f.write(f"Controls: {meta.get('controls')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    # Build model_diagnostics.csv
    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_path = out_dir / "model_diagnostics.csv"
    diag_df.to_csv(diag_path, index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} regressions)")

    # LaTeX table
    _save_latex_table(all_results, out_dir)

    return diag_df


def generate_report(
    all_results: List[Dict[str, Any]],
    diag_df: pd.DataFrame,
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report summarising H16 results."""
    lines = [
        "# Stage 4: H16 R&D Investment Intensity Hypothesis Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Unit of observation:** individual earnings call (call-level)",
        f"**Sample:** Main only (excludes Finance FF12=11, Utility FF12=8)",
        f"**Time index:** fyearq_int (fiscal year)",
        f"**Hypothesis test:** Two-tailed (no directional prediction)",
        f"**DV construction:** Jiang, John, Larsen (2021): xrdy / saley",
        "",
        "## Model Specifications",
        "",
        "All 4 key IVs enter each model simultaneously:",
        "- CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct",
        "- Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct",
        "",
        "| Col | DV | FE | Controls |",
        "|-----|----|----|----------|",
    ]
    for spec in MODEL_SPECS:
        lines.append(
            f"| ({spec['col']}) | {spec['dv']} | {spec['fe']} | {spec['controls']} |"
        )

    lines += [
        "",
        "Standard errors: firm-clustered (cov_type='clustered', cluster_entity=True)",
        "Two-tailed test: H16 beta != 0",
        "",
        "## Results Summary",
        "",
        "| Col | DV | FE | Controls | N | Within-R-sq |",
        "|-----|----|----|----------|---|-------------|",
    ]

    for r in all_results:
        meta = r.get("meta", {})
        if not meta:
            continue
        lines.append(
            f"| ({meta['col']}) | {meta['dv']} | {meta['fe']} | "
            f"{meta['controls']} | {meta['n_obs']:,} | {meta['within_r2']:.4f} |"
        )

    lines += [
        "",
        "## Key IV Coefficients (two-tailed p-values)",
        "",
        "| IV | Col | Beta | SE | p(two-tail) | Sig |",
        "|----|-----|------|-----|-------------|-----|",
    ]

    for r in all_results:
        meta = r.get("meta", {})
        if not meta:
            continue
        for iv in KEY_IVS:
            beta = meta.get(f"{iv}_beta", np.nan)
            se = meta.get(f"{iv}_se", np.nan)
            p_two = meta.get(f"{iv}_p_two", np.nan)
            stars = _sig_stars(p_two)
            if not np.isnan(beta):
                lines.append(
                    f"| {iv} | ({meta['col']}) | {beta:.4f} | {se:.4f} | "
                    f"{p_two:.4f} | {stars} |"
                )

    lines.append("")

    report_path = out_dir / "report_step4_H16.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H16.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h16_rd_sales" / timestamp

    # Setup logging
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H16_RDSales",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H16 R&D Investment Intensity Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Sample:    Main only (FF12 != 8, 11)")
    print(f"IVs:       {len(KEY_IVS)} (all simultaneous)")
    print(f"Specs:     {len(MODEL_SPECS)} model columns")
    print(f"Time FE:   fyearq_int (fiscal year) + cal_yr_qtr (calendar year-quarter)")
    print(f"Test:      Two-tailed (no directional prediction)")

    # Load panel
    panel = load_panel(root, panel_path)

    # Track panel path for manifest
    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "h16_rd_sales",
        required_file="h16_rd_sales_panel.parquet",
    ) / "h16_rd_sales_panel.parquet"

    # Filter to Main sample
    full_panel_n = len(panel)
    panel = filter_main_sample(panel)
    main_panel_n = len(panel)

    print(f"\n  Main sample: {main_panel_n:,} calls, "
          f"{panel['gvkey'].nunique():,} firms")
    print(f"  RDSales non-null: {panel['RDSales'].notna().sum():,}")
    print(f"  RDSales_lead non-null: {panel['RDSales_lead'].notna().sum():,}")
    for iv in KEY_IVS:
        n_valid = panel[iv].notna().sum()
        pct = 100.0 * n_valid / main_panel_n if main_panel_n > 0 else 0
        print(f"  {iv}: {n_valid:,} ({pct:.1f}%)")

    # Generate summary stats (Main sample only)
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel,
        variables=SUMMARY_STATS_VARS,
        sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics -- H16 R\\&D Investment Intensity (Main Sample)",
        label="tab:summary_stats_h16",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # Run regressions: 8 model specifications
    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} FE={spec['fe']} "
              f"Controls={spec['controls']} ---")

        try:
            df_prepared = prepare_regression_data(panel, spec)
        except ValueError as e:
            print(f"  ERROR preparing data: {e}", file=sys.stderr)
            continue

        if len(df_prepared) < 100:
            print(f"  Skipping: too few obs ({len(df_prepared)})")
            continue

        model, meta = run_regression(df_prepared, spec)

        if model is not None and meta:
            all_results.append({"model": model, "meta": meta})

    # Save outputs
    diag_df = save_outputs(all_results, out_dir)

    # Sample attrition table
    if all_results:
        first_meta = all_results[0].get("meta", {})
        attrition_stages = [
            ("Master manifest (full panel)", full_panel_n),
            ("Main sample filter (excl Finance/Utility)", main_panel_n),
            ("After nonpositive-sales exclusion (RDSales NaN)", panel["RDSales"].notna().sum()),
            ("After lead filter (col 5-8 only)", panel["RDSales_lead"].notna().sum()),
            ("After complete-case + min-calls (col 1)", first_meta.get("n_obs", 0)),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H16 R&D Investment Intensity")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h16_rd_sales_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_results, diag_df, out_dir, duration)

    # Final summary
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output:   {out_dir}")
    print(f"Total regressions completed: {len(all_results)}/{len(MODEL_SPECS)}")

    # H16 significance summary (two-tailed)
    for iv in KEY_IVS:
        sig_count = sum(
            1 for r in all_results
            if r["meta"].get(f"{iv}_p_two", 1.0) < 0.05
        )
        print(f"  {iv}: {sig_count}/{len(all_results)} significant (p<0.05, two-tail)")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print(f"  KEY_IVS: {len(KEY_IVS)} variables")
        print(f"  MODEL_SPECS: {len(MODEL_SPECS)} specifications")
        print(f"  BASE_CONTROLS: {len(BASE_CONTROLS)} variables")
        print(f"  EXTENDED_CONTROLS: {len(EXTENDED_CONTROLS)} variables")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
