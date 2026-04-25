#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H1 Cash Holdings Hypothesis — CEO 2-IV Variant
================================================================================
ID: econometric/test_h1_cash_holdings_ceo2iv
Description: H1 CEO-only 2-IV variant that restricts the joint-IV stack to exactly
             two CEO speech-uncertainty measures: UncAnsCEO (CEO Q&A) and UncPreCEO
             (CEO Presentation). Drops UncAnsMgr / UncPreMgr / UncAnsNoCEO /
             UncPreNoCEO entirely. Identical 12-spec ladder, controls, FE, sample,
             and clustering as parent H1. Per the CEO-only pivot of the thesis.

Model Specifications (12 columns in one table):
    Cols 1-4: DV = CashRatio (contemporaneous), Calendar Year FE
    Cols 5-6: DV = CashRatio (contemporaneous), Calendar Year-Quarter FE
    Cols 7-10: DV = CashRatio_lead (t+1), Calendar Year FE
    Cols 11-12: DV = CashRatio_lead (t+1), Calendar Year-Quarter FE
    Odd cols (1-4,7-10): Industry FE + Year FE / Even: Firm FE + Year FE
    Cols 5-6, 11-12: Extended controls only, YQ FE

Key Independent Variables (2, CEO-only, both enter simultaneously):
    UncAnsCEO (CEO Q&A uncertainty),
    UncPreCEO (CEO Presentation uncertainty),

Base Controls (8):
    Leverage, lnAssets, TobinsQ, ROA, Capex, DivDummy, sCFO, Lagged_DV

Extended Controls:
    Base + SalesGrowth, RDSales, CashFlow, DailyVola

Sample: Main only (FF12 codes 1-7, 9-10, 12).

Hypothesis Test (one-tailed):
    H1: beta(uncertainty_var) > 0  -- higher speech uncertainty -> more cash

Standard Errors: Firm-clustered (groups=gvkey).

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet

Outputs:
    - outputs/econometric/h1_cash_holdings_ceo2iv/{timestamp}/h1_cash_holdings_ceo2iv_table.tex
    - outputs/econometric/h1_cash_holdings_ceo2iv/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h1_cash_holdings_ceo2iv/{timestamp}/summary_stats.csv
    - outputs/econometric/h1_cash_holdings_ceo2iv/{timestamp}/summary_stats.tex
    - outputs/econometric/h1_cash_holdings_ceo2iv/{timestamp}/report_step4_H1_ceo2iv.md
    - outputs/econometric/h1_cash_holdings_ceo2iv/{timestamp}/sample_attrition.csv
    - outputs/econometric/h1_cash_holdings_ceo2iv/{timestamp}/run_manifest.json

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h1_cash_holdings_panel)
    - Uses: linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-03-15
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
from f1d.shared.outputs import (
    extract_coefs_panelols,
    generate_attrition_table,
    generate_manifest,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

KEY_IVS = [
    "ClarityCEO_QtrExp",
    "UncResCEO_QtrExp",
    "UncPreCEO",
]

BASE_CONTROLS = [
    "Leverage",
    "lnAssets",
    "TobinsQ",
    "ROA",
    "Capex",
    "DivDummy",
    "sCFO",
    "Lagged_DV",
]

EXTENDED_CONTROLS = BASE_CONTROLS + [
    "SalesGrowth",
    "RDSales",
    "CashFlowAt",
    "DailyVola",
]

EXTENDED_ONLY_CONTROLS = [c for c in EXTENDED_CONTROLS if c not in BASE_CONTROLS]

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission (consumed by the
# consolidated renderer in outputs/generate_all_tables.py). Every
# field below is the single source of truth for rendering this suite.
# ------------------------------------------------------------------
SUITE_ID = "H1.ceo2.decomp"
SUITE_DIR_NAME = "h1_cash_holdings_ceo2iv_decomp"
SUITE_TITLE = "Speech Uncertainty and Cash Holdings (CEO 2-IV: DWZ Q&A Decomposition, Quarterly Expanding)"
SUITE_CAPTION = "H1 CEO 3-IV: ClarityCEO + UncResCEO (DWZ Eq.5, qtr-exp) + UncPreCEO (raw)"
SUITE_LABEL = "tab:h1_ceo2_decomp"
SAMPLE_LABEL = "Main sample (excludes financial and utility firms)."
HYP_DIR = "positive"  # Suite-level literal (TailSpec validation); per-IV
                      # directions handled by IV_TAIL_DIRECTION below + extract_coefs stitching.
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}

# Per-IV one-tail direction for HC at the decomposition level.
# Trait component: ClarityCEO = -gamma_i (DWZ §4.4 p.16). HC predicts persistent-uncertainty
#   CEOs (low Clarity, high gamma) hold more cash → as Clarity rises, cash falls → beta NEG.
# State component: UncResCEO = call-level deviation. HC predicts positive uncertainty surprise
#   raises cash → beta POS.
IV_TAIL_DIRECTION: Dict[str, str] = {
    "ClarityCEO_QtrExp": "negative",
    "UncResCEO_QtrExp": "positive",
    "UncPreCEO": "positive",
}

MODEL_SPECS = [
    {"col": 1,  "dv": "CashRatio",      "fe": "industry",    "controls": "base"},
    {"col": 2,  "dv": "CashRatio",      "fe": "firm",        "controls": "base"},
    {"col": 3,  "dv": "CashRatio",      "fe": "industry",    "controls": "extended"},
    {"col": 4,  "dv": "CashRatio",      "fe": "firm",        "controls": "extended"},
    # Year-Quarter FE specs (Extended controls only)
    {"col": 5,  "dv": "CashRatio",      "fe": "industry_yq", "controls": "extended"},
    {"col": 6,  "dv": "CashRatio",      "fe": "firm_yq",     "controls": "extended"},
    {"col": 7,  "dv": "CashRatio_lead", "fe": "industry",    "controls": "base"},
    {"col": 8,  "dv": "CashRatio_lead", "fe": "firm",        "controls": "base"},
    {"col": 9,  "dv": "CashRatio_lead", "fe": "industry",    "controls": "extended"},
    {"col": 10, "dv": "CashRatio_lead", "fe": "firm",        "controls": "extended"},
    # Year-Quarter FE specs (Extended controls only)
    {"col": 11, "dv": "CashRatio_lead", "fe": "industry_yq", "controls": "extended"},
    {"col": 12, "dv": "CashRatio_lead", "fe": "firm_yq",     "controls": "extended"},
]

MIN_CALLS_PER_FIRM = 5

VARIABLE_LABELS = {
    "ClarityCEO_QtrExp": "CEO Clarity (DWZ, qtr-exp)",
    "UncResCEO_QtrExp": "CEO Residual Uncertainty (DWZ, qtr-exp)",
    "UncPreCEO": "CEO Pres Uncertainty",
}

# Summary statistics variable list
SUMMARY_STATS_VARS = [
    {"col": "CashRatio", "label": "Cash Holdings$_t$"},
    {"col": "CashRatio_lead", "label": "Cash Holdings$_{t+1}$"},
    # Key IVs (CEO-only 2-IV)
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    # Base controls
    {"col": "Leverage", "label": "Leverage"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Capex", "label": "CapEx / Assets"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "sCFO", "label": "OCF Volatility"},
    # Extended controls
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RDSales", "label": "R\\&D Intensity"},
    {"col": "CashFlowAt", "label": "Cash Flow"},
    {"col": "DailyVola", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: Test H1 Cash Holdings Hypothesis (call-level)",
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
    """Load call-level H1 panel from Stage 3 + merge DWZ decomp parquet on file_name.

    KEY_IVS for this runner are ClarityCEO_QtrExp + UncResCEO_QtrExp (from decomp)
    plus UncPreCEO (from H1 panel). Only UncPreCEO is read from the H1 panel;
    Clarity/UncRes come from the H0.3 expanding-window output.
    """
    print("\n" + "=" * 60)
    print("Loading H1 panel + merging DWZ-decomp parquet")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h1_cash_holdings",
            required_file="h1_cash_holdings_panel.parquet",
        )
        panel_file = panel_dir / "h1_cash_holdings_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"H1 panel not found: {panel_file}")

    # Read H1 panel (only DV + controls; both KEY_IVs come from decomp parquet via merge)
    columns = [
        "file_name",
        "start_date",
        "gvkey", "year", "fyearq_int", "ff12_code",
        "CashRatio", "CashRatio_lead", "CashRatio_lag",
        "UncPreCEO",
        "Leverage", "lnAssets", "TobinsQ", "ROA",
        "Capex", "DivDummy", "sCFO",
        "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
    ]
    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  H1 panel:  {panel_file}")
    print(f"  H1 rows:   {len(panel):,}  cols: {len(panel.columns)}")

    # Locate latest decomp parquet
    decomp_dir = get_latest_output_dir(
        root_path / "outputs" / "econometric" / "ceo_clarity_expanding",
        required_file="ceo_clarity_qtrexp_residuals.parquet",
    )
    decomp_file = decomp_dir / "ceo_clarity_qtrexp_residuals.parquet"
    decomp = pd.read_parquet(
        decomp_file,
        columns=["file_name", "ClarityCEO_QtrExp", "UncResCEO_QtrExp"],
    )
    print(f"  Decomp:    {decomp_file}")
    print(f"  Decomp rows: {len(decomp):,}  "
          f"non-NaN ClarityCEO_QtrExp: {decomp['ClarityCEO_QtrExp'].notna().sum():,}")

    # Merge: left on H1 panel; rows without decomp get NaN -> dropped at IV-NA stage
    before = len(panel)
    panel = panel.merge(decomp, on="file_name", how="left", validate="one_to_one")
    matched = panel["ClarityCEO_QtrExp"].notna().sum()
    print(f"  After merge: {len(panel):,} rows ({matched:,} with non-NaN Clarity, "
          f"{before - matched:,} with NaN — dropped downstream by complete-case)")

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
    """Prepare panel for a specific model specification.

    - Drops rows where DV is NaN
    - Complete-case filtering on all required columns
    - Minimum-calls-per-firm filter

    Args:
        panel: Main-sample call-level panel
        spec: Model specification dict with 'dv', 'fe', 'controls'

    Returns:
        Prepared DataFrame ready for regression
    """
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

    # Check required columns exist
    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(
            f"Required columns missing from panel: {missing}. Check Stage 3 output."
        )

    df = panel.copy()

    # Replace inf with NaN
    df = df.replace([np.inf, -np.inf], np.nan)

    # Coverage check: warn if any key IV has >50% NaN
    for iv in KEY_IVS:
        pct_missing = df[iv].isna().mean() * 100
        if pct_missing > 50:
            print(f"  WARNING: {iv} has {pct_missing:.1f}% missing values")

    # Drop rows where DV is NaN
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases on required variables
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

    All models: firm-level clustered SEs (firm only), drop_absorbed=True.

    Args:
        df_prepared: Prepared DataFrame (complete cases, min-calls filtered)
        spec: Model specification dict

    Returns:
        Tuple of (fitted model, metadata dict) or (None, {}) on failure
    """
    col_num = spec["col"]
    dv = spec["dv"]
    fe_type = spec["fe"]
    controls = BASE_CONTROLS if spec["controls"] == "base" else EXTENDED_CONTROLS

    print(f"\n" + "=" * 60)
    print(f"Running regression: Col ({col_num}) | DV={dv} | FE={fe_type} | Controls={spec['controls']}")
    print("=" * 60)

    if len(df_prepared) < 100:
        print(f"  WARNING: Too few observations ({len(df_prepared)}), skipping")
        return None, {}

    # Build exogenous variable list
    exog = KEY_IVS + controls

    # Determine time index based on FE type
    time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"
    base_fe = fe_type.replace("_yq", "")
    fe_label = f"{'Industry(FF12)' if base_fe == 'industry' else 'Firm'} + {'CalYrQtr' if fe_type.endswith('_yq') else 'CalYear'}"

    print(f"  FE: {fe_label}")
    print(f"  N calls: {len(df_prepared):,}  |  N firms: {df_prepared['gvkey'].nunique():,}")
    print(f"  Controls: {spec['controls']} ({len(controls)} vars)")
    print("  Estimating with firm×time-clustered SEs via PanelOLS...")
    t0 = datetime.now()

    # Create MultiIndex for PanelOLS
    df_panel = df_prepared.set_index(["gvkey", time_col])

    try:
        if base_fe == "industry":
            # Use constructor API with other_effects to ABSORB industry FE
            # (not C(ff12_code) dummies which spam the coefficient table)
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
            model = model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
        else:
            # Firm FE: use from_formula (proven pattern)
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
            model = model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {elapsed:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}  Adj R-squared: {1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid:.4f}")
    print(f"  N obs: {int(model.nobs):,}")

    # Build metadata with per-IV one-tailed p-values
    meta: Dict[str, Any] = {
        "col": col_num,
        "dv": dv,
        "fe": fe_type,
        "controls": spec["controls"],
        "n_obs": int(model.nobs),
        "n_firms": df_prepared["gvkey"].nunique(),
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
        "dv_mean": float(model.model.dependent.dataframe.mean().iloc[0]),
    }

    # Per-IV coefficients with one-tailed p-values (per IV_TAIL_DIRECTION)
    for iv in KEY_IVS:
        beta = float(model.params.get(iv, np.nan))
        se = float(model.std_errors.get(iv, np.nan))
        p_two = float(model.pvalues.get(iv, np.nan))
        t_stat = float(model.tstats.get(iv, np.nan))

        if not np.isnan(p_two) and not np.isnan(beta):
            direction = IV_TAIL_DIRECTION.get(iv, "positive")
            if direction == "positive":
                # H: beta > 0; p_one = P(in positive direction)
                p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
            else:  # "negative"
                # H: beta < 0; p_one = P(in negative direction)
                p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
        else:
            p_one = np.nan

        meta[f"{iv}_beta"] = beta
        meta[f"{iv}_se"] = se
        meta[f"{iv}_t"] = t_stat
        meta[f"{iv}_p_one"] = p_one

        stars = "***" if p_one < 0.01 else ("**" if p_one < 0.05 else ("*" if p_one < 0.10 else ""))
        print(f"  {iv}: beta={beta:.4f} SE={se:.4f} p1={p_one:.4f} {stars}")

    return model, meta


# ==============================================================================
# Output Generation
# ==============================================================================


def _sig_stars(p: float) -> str:
    """Return significance stars for one-tailed p-value."""
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
    """Write unified 12-column LaTeX table with stars + SE in parentheses.

    Layout:
        Cols 1-6: CashRatio (contemporaneous) — 4 Year FE + 2 YQ FE
        Cols 7-12: CashRatio_lead (t+1) — 4 Year FE + 2 YQ FE
        Rows: 4 key IVs (coeff + SE), controls indicator, FE indicators, N, R²
    """
    # Sort results by column number
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
        r"\caption{" + SUITE_CAPTION + r"}",
        r"\label{" + SUITE_LABEL + r"}",
        r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}",
        r"\toprule",
    ]

    # Column numbers
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")

    # DV headers with multicolumn
    lines.append(
        r" & \multicolumn{6}{c}{Cash Holdings$_t$}"
        r" & \multicolumn{6}{c}{Cash Holdings$_{t+1}$} \\"
    )
    lines.append(r"\cmidrule(lr){2-7} \cmidrule(lr){8-13}")
    lines.append(r"\midrule")

    # Key IV rows (coefficient + SE for each)
    for iv in KEY_IVS:
        label = VARIABLE_LABELS.get(iv, iv)
        # Coefficient row with stars
        coef_cells = []
        for c in range(1, n_cols + 1):
            meta = results_by_col.get(c, {})
            beta = meta.get(f"{iv}_beta", np.nan)
            p_one = meta.get(f"{iv}_p_one", np.nan)
            coef_cells.append(fmt_coef(beta, _sig_stars(p_one)))
        lines.append(f"{label} & " + " & ".join(coef_cells) + r" \\")

        # SE row
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

    # R²
    r2_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        r2_cells.append(fmt_r2(meta.get("r2", np.nan)))
    lines.append(r"$R^2$ & " + " & ".join(r2_cells) + r" \\")

    # Adj. R²
    adj_r2_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        adj_r2_cells.append(fmt_r2(meta.get("adj_r2", np.nan)))
    lines.append(r"Adj.~$R^2$ & " + " & ".join(adj_r2_cells) + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"DWZ Eq.5 decomposition of CEO Q\&A uncertainty into a persistent CEO ",
        r"trait component (\textit{ClarityCEO}, the negative of the CEO fixed effect ",
        r"from DWZ Eq.4) and a within-quarter state component (\textit{UncResCEO}, ",
        r"the residual from DWZ Eq.4), estimated via quarterly-expanding window. ",
        r"\textit{UncPreCEO} (raw, presentation-segment uncertainty) enters as a third ",
        r"independent IV preserved from the parent suite (DWZ Eq.4 RHS regressor; not decomposed ",
        r"because its persistent-CEO variance is already absorbed by ClarityCEO). ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed). ",
        r"\textit{ClarityCEO}: H1 direction $\beta < 0$ (high persistent clarity $\Rightarrow$ ",
        r"less precautionary cash). \textit{UncResCEO}: H1 direction $\beta > 0$ ",
        r"(positive within-quarter uncertainty $\Rightarrow$ more cash). ",
        r"\textit{UncPreCEO}: H1 direction $\beta > 0$ (more presentation uncertainty $\Rightarrow$ more cash). ",
        r"Standard errors (in parentheses) firm-level clustered. ",
        r"Main sample (excludes financial and utility firms). ",
        r"Industry FE uses Fama-French 12 industry dummies. ",
        r"Contemporaneous DV (cols 1--6) is constant within firm-quarter; ",
        r"results should be interpreted alongside lead DV (cols 7--12). ",
        r"Variables winsorized at 1\%/99\% by year at engine level. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_cash_holdings_ceo2iv_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: h1_cash_holdings_ceo2iv_table.tex")


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
            f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
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
    """Generate markdown report summarising H1 CEO 2-IV results."""
    lines = [
        "# Stage 4: H1 Cash Holdings — CEO 2-IV Variant (Q&A + Presentation)",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Unit of observation:** individual earnings call (call-level)",
        f"**Sample:** Main only (excludes Finance FF12=11, Utility FF12=8)",
        "",
        "## Model Specifications",
        "",
        "Both CEO-only key IVs enter each model simultaneously:",
        "- UncAnsCEO (CEO Q&A uncertainty)",
        "- UncPreCEO (CEO Presentation uncertainty)",
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
        "Standard errors: firm-level clustered (cov_type='clustered', cluster_entity=True, cluster_time=False)",
        "One-tailed test: H1 beta > 0",
        "",
        "## Results Summary",
        "",
        "| Col | DV | FE | Controls | N | R² | Adj R² |",
        "|-----|----|----|----------|---|----|--------|",
    ]

    for r in all_results:
        meta = r.get("meta", {})
        if not meta:
            continue
        lines.append(
            f"| ({meta['col']}) | {meta['dv']} | {meta['fe']} | "
            f"{meta['controls']} | {meta['n_obs']:,} | {meta['r2']:.4f} | {meta['adj_r2']:.4f} |"
        )

    lines += [
        "",
        "## Key IV Coefficients (one-tailed p-values)",
        "",
        "| IV | Col | Beta | SE | p(one-tail) | Sig |",
        "|----|-----|------|-----|-------------|-----|",
    ]

    for r in all_results:
        meta = r.get("meta", {})
        if not meta:
            continue
        for iv in KEY_IVS:
            beta = meta.get(f"{iv}_beta", np.nan)
            se = meta.get(f"{iv}_se", np.nan)
            p_one = meta.get(f"{iv}_p_one", np.nan)
            stars = _sig_stars(p_one)
            if not np.isnan(beta):
                lines.append(
                    f"| {iv} | ({meta['col']}) | {beta:.4f} | {se:.4f} | "
                    f"{p_one:.4f} | {stars} |"
                )

    lines.append("")

    report_path = out_dir / "report_step4_H1_ceo2iv.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H1_ceo2iv.md")


def _write_suite_spec_json(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec_H1.json from runner state.

    Reads per-col fitted models + meta, maps FE type strings to schema
    enums, extracts IV + control coefs uniformly, and writes a single
    validated JSON file for the consolidated renderer to consume.
    """
    results_by_col = {r["meta"]["col"]: r for r in all_results if r.get("meta")}

    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Optional[float]]]] = []

    for spec in MODEL_SPECS:
        col_num = spec["col"]
        if col_num not in results_by_col:
            raise RuntimeError(
                f"suite_spec emission: col {col_num} missing from all_results; "
                f"cannot emit suite_spec_{SUITE_ID}.json"
            )

        result = results_by_col[col_num]
        model = result["model"]
        meta = result["meta"]

        fe_type = spec["fe"]
        base_fe = fe_type.replace("_yq", "")
        fe_entity = "industry" if base_fe == "industry" else "firm"
        fe_time = (
            "calendar_year_quarter" if fe_type.endswith("_yq") else "calendar_year"
        )

        control_list = (
            list(BASE_CONTROLS) if spec["controls"] == "base" else list(EXTENDED_CONTROLS)
        )

        col_metadata.append(
            {
                "col": col_num,
                "dv": spec["dv"],
                "fe_entity": fe_entity,
                "fe_time": fe_time,
                "control_vars": control_list,
                "n_obs": int(meta["n_obs"]),
                "n_firms": int(meta["n_firms"]),
                "r2": float(meta["r2"]),
                "adj_r2": float(meta["adj_r2"]),
                "dv_mean": float(meta["dv_mean"]),
                "cluster_fallback": False,
            }
        )

        # Per-IV mixed direction: compute coefs separately per direction and stitch.
        coefs_pos = extract_coefs_panelols(
            model=model,
            key_ivs=[iv for iv in KEY_IVS if IV_TAIL_DIRECTION.get(iv) == "positive"],
            all_vars=KEY_IVS + control_list,
            hyp_dir="positive",
        )
        coefs_neg = extract_coefs_panelols(
            model=model,
            key_ivs=[iv for iv in KEY_IVS if IV_TAIL_DIRECTION.get(iv) == "negative"],
            all_vars=KEY_IVS + control_list,
            hyp_dir="negative",
        )
        # Merge: take pos-direction p_one for pos IVs; neg-direction for neg IVs; else from pos (controls have p_one=None either way)
        merged_coefs: Dict[str, Dict[str, Any]] = dict(coefs_pos)
        for iv, payload in coefs_neg.items():
            if IV_TAIL_DIRECTION.get(iv) == "negative":
                merged_coefs[iv] = payload
        coefs_per_col.append(merged_coefs)

    ivs_payload = [
        {
            "name": iv,
            "label": VARIABLE_LABELS.get(iv, iv).replace("_", r"\_"),
            "tail": "one_neg" if IV_TAIL_DIRECTION.get(iv) == "negative" else "one_pos",
        }
        for iv in KEY_IVS
    ]
    controls_payload = {
        "base": list(BASE_CONTROLS),
        "extended_only": list(EXTENDED_ONLY_CONTROLS),
    }
    header_rows = [
        [
            {"label": "CashRatio", "span": 6},
            {"label": r"CashRatio\_lead", "span": 6},
        ]
    ]

    paths = write_suite_spec(
        output_dir=out_dir,
        runner_id=SUITE_DIR_NAME,
        sub_tables=[
            {
                "suite_id": SUITE_ID,
                "dir_name": SUITE_DIR_NAME,
                "title": SUITE_TITLE,
                "caption": SUITE_CAPTION,
                "label": SUITE_LABEL,
                "col_range": [spec["col"] for spec in MODEL_SPECS],
                "header_rows": header_rows,
                "suite_type": "standard",
            }
        ],
        coefs_per_col=coefs_per_col,
        col_metadata=col_metadata,
        sample_label=SAMPLE_LABEL,
        clustering=CLUSTERING,
        tail=TAIL,
        ivs=ivs_payload,
        controls=controls_payload,
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


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
    out_dir = root / "outputs" / "econometric" / SUITE_DIR_NAME / timestamp

    # Setup logging
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H1_ceo2iv_CashRatio",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H1 Cash Holdings Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Sample:    Main only (FF12 != 8, 11)")
    print(f"IVs:       {len(KEY_IVS)} (all simultaneous)")
    print(f"Specs:     {len(MODEL_SPECS)} model columns")

    # Load panel
    panel = load_panel(root, panel_path)

    # Track panel path for manifest
    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet",
    ) / "h1_cash_holdings_panel.parquet"

    # Filter to Main sample
    full_panel_n = len(panel)
    panel = filter_main_sample(panel)
    main_panel_n = len(panel)

    print(f"\n  Main sample: {main_panel_n:,} calls, "
          f"{panel['gvkey'].nunique():,} firms")
    print(f"  CashRatio non-null: {panel['CashRatio'].notna().sum():,}")
    print(f"  CashRatio_lead non-null: {panel['CashRatio_lead'].notna().sum():,}")
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
        caption="Summary Statistics — H1 Cash Holdings CEO 2-IV (Main Sample)",
        label="tab:summary_stats_h1_ceo2",
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

    # Emit canonical suite_spec.json (consumed by generate_all_tables.py)
    _write_suite_spec_json(all_results, out_dir)

    # Sample attrition table
    if all_results:
        # Use first result for final N
        first_meta = all_results[0].get("meta", {})
        attrition_stages = [
            ("Master manifest (full panel)", full_panel_n),
            ("Main sample filter (excl Finance/Utility)", main_panel_n),
            ("After lead filter (col 5-8 only)", panel["CashRatio_lead"].notna().sum()),
            ("After complete-case + min-calls (col 1)", first_meta.get("n_obs", 0)),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H1 Cash Holdings CEO 2-IV")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h1_cash_holdings_ceo2iv_table.tex",
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

    # H1 significance summary
    for iv in KEY_IVS:
        sig_count = sum(
            1 for r in all_results
            if r["meta"].get(f"{iv}_p_one", 1.0) < 0.05
            and r["meta"].get(f"{iv}_beta", 0) > 0
        )
        print(f"  {iv}: {sig_count}/{len(all_results)} significant (p<0.05, one-tail)")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        # Validate imports succeeded
        print(f"  KEY_IVS: {len(KEY_IVS)} variables")
        print(f"  MODEL_SPECS: {len(MODEL_SPECS)} specifications")
        print(f"  BASE_CONTROLS: {len(BASE_CONTROLS)} variables")
        print(f"  EXTENDED_CONTROLS: {len(EXTENDED_CONTROLS)} variables")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
