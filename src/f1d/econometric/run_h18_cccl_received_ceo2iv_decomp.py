#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H18 — CEO 3-IV DWZ DECOMP (6-col, CCCL Linear Probability Model)
================================================================================
ID: econometric/run_h18_cccl_received_ceo2iv_decomp
Description: DWZ-decomposition variant of H18 reaction suite (Conference Call
             Comment Letters, Lerman et al. 2024 Management Science). Replaces
             the 4-IV CEO+Mgr-pool stack (UncAnsCEO + UncPreCEO + UncAnsMgr +
             UncPreMgr) with the DWZ Eq.5 3-IV CEO-only decomposition:
             ClarityCEO (persistent CEO trait, = -CEO FE) + UncResCEO
             (call-level state residual) + UncPreCEO (raw, presentation-segment
             uncertainty). Full method: single full-panel DWZ Eq.4 fit.

             Per locked design (drivers + reaction = Full method only),
             companion QtrExp variant NOT built for §4.2 reaction suite.

             Lerman et al. (2024) document that the SEC references voluntary
             earnings-conference-call disclosures in comment letters when
             mandatory filings appear insufficient or inconsistent — this
             channel constitutes a regulatory reaction to call uncertainty,
             complementing H14c.ceo2.decomp's market-reaction (bid-ask spread)
             channel.

Tail directions (asymmetric per Lerman et al. 2024 + DWZ decomposition logic):
    ClarityCEO: one-tail NEG
        (high persistent CEO clarity → less SEC scrutiny → lower CCCL receipt)
    UncResCEO: one-tail POS
        (positive within-quarter uncertainty surprise → more SEC scrutiny →
         higher CCCL receipt; Lerman 2024 mechanism)
    UncPreCEO: one-tail POS
        (presentation-segment uncertainty → more SEC scrutiny → higher CCCL
         receipt)

Model Specifications (6 columns; CCCL is forward-window indicator, no lead):
    Cols 1-2:  DV = CCCL, Industry/Firm FE, Base controls,    cal_yr
    Cols 3-4:  DV = CCCL, Industry/Firm FE, Extended controls, cal_yr
    Cols 5-6:  DV = CCCL, Industry/Firm FE, Extended controls, cal_yr_qtr

DV: CCCL = 1 if firm received SEC comment letter in window
    (start_date_current, start_date_next_call]. Binary indicator with
    ~0.4% treatment rate. Estimated via Linear Probability Model (LPM) on
    PanelOLS, justified by Timoneda (2021) Monte Carlo: LPM-FE outperforms
    logit at base rates <5%; no incidental parameters problem; preserves
    sample.

Base Controls (8):
    lnAssets, TobinsQ, ROA, Leverage, Capex, CashRatio, DivDummy, sCFO,
    Lagged_DV
Extended Controls (Base + 4):
    + SalesGrowth, RDSales, CashFlowAt, DailyVola

Sample: Main only (FF12 codes 1-7, 9-10, 12). Decomp parquet merge drops
    rows with NaN Clarity/UncRes.

Inputs:
    - outputs/variables/h18_cccl_received/latest/h18_cccl_received_panel.parquet
    - outputs/econometric/ceo_clarity_extended/<latest>/ceo_clarity_residual.parquet
    - outputs/econometric/ceo_clarity_extended/<latest>/ceo_clarity_fe.parquet

Standard Errors: Firm-level clustered following Petersen (2009).

Author: Thesis Author
Date: 2026-04-27
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
from f1d.shared.outputs import (
    generate_attrition_table,
    generate_manifest,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index

warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)



# ==============================================================================
# Configuration
# ==============================================================================

KEY_IVS = [
    "ClarityCEO",
    "UncResCEO",
    "UncPreCEO",
]

# Per-IV tail directions (asymmetric per DWZ decomposition + Lerman 2024 logic).
IV_TAIL_DIRECTION: Dict[str, str] = {
    "ClarityCEO": "negative",
    "UncResCEO":  "positive",
    "UncPreCEO":  "positive",
}

# Lagged_DV placeholder routed at spec-prep time (CCCL_lag for CCCL DV).
BASE_CONTROLS = [
    "lnAssets",
    "TobinsQ",
    "ROA",
    "Leverage",
    "Capex",
    "CashRatio",
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
# Suite metadata for suite_spec.json emission.
# ------------------------------------------------------------------
SUITE_ID = "H18.ceo2.decomp"
SUITE_DIR_NAME = "h18_cccl_received_ceo2iv_decomp"
SUITE_TITLE = (
    'H18 CEO 3-IV Decomp: DWZ Full QA Decomposition + Raw UncPreCEO and '
    'SEC Conference-Call Comment Letter Receipt (Lerman et al. 2024)'
)
SUITE_CAPTION = (
    r'H18 CEO 3-IV Decomp: ClarityCEO + UncResCEO (DWZ Eq.5 Full) + UncPreCEO (raw) and '
    r'SEC Conference-Call Comment Letter Receipt (LPM, $[\textit{call}_t, \textit{call}_{t+1}]$ window)'
)
SUITE_LABEL = "tab:h18_ceo2_decomp"
SAMPLE_LABEL = (
    "Main sample (excludes financial and utility firms). "
    "DWZ Full decomposition: Clarity = -CEO FE; UncRes = call-level residual."
)
HYP_DIR = "positive"  # Suite-level Pydantic placeholder; per-IV via IV_TAIL_DIRECTION + spec stitching.
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}

MODEL_SPECS = [
    {"col": 1, "dv": "CCCL", "fe": "industry",    "controls": "base"},
    {"col": 2, "dv": "CCCL", "fe": "firm",        "controls": "base"},
    {"col": 3, "dv": "CCCL", "fe": "industry",    "controls": "extended"},
    {"col": 4, "dv": "CCCL", "fe": "firm",        "controls": "extended"},
    {"col": 5, "dv": "CCCL", "fe": "industry_yq", "controls": "extended"},
    {"col": 6, "dv": "CCCL", "fe": "firm_yq",     "controls": "extended"},
]

MIN_CALLS_PER_FIRM = 5

VARIABLE_LABELS = {
    "ClarityCEO": "CEO Clarity (DWZ)",
    "UncResCEO":  "CEO Residual Uncertainty (DWZ)",
    "UncPreCEO":  "CEO Pres Uncertainty",
}

SUMMARY_STATS_VARS = [
    {"col": "CCCL", "label": "CCCL (call-to-next-call)"},
    {"col": "ClarityCEO", "label": "CEO Clarity (DWZ)"},
    {"col": "UncResCEO", "label": "CEO UncRes (DWZ)"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "Capex", "label": "CapEx / Assets"},
    {"col": "CashRatio", "label": "Cash Holdings"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "sCFO", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RDSales", "label": r"R\&D Intensity"},
    {"col": "CashFlowAt", "label": "Cash Flow"},
    {"col": "DailyVola", "label": "Stock Volatility"},
]


def _lag_column_for_dv(dv: str) -> str:
    return f"{dv}_lag"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Stage 4: Test H18 CCCL CEO 3-IV Decomp (6-col)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load H18 panel + merge DWZ Full decomp parquets.

    Full method 3-IV design:
      - UncPreCEO: H18 panel (raw).
      - UncResCEO: ceo_clarity_extended/{latest}/ceo_clarity_residual.parquet (file_name).
      - ClarityCEO: ceo_clarity_extended/{latest}/ceo_clarity_fe.parquet (ceo_id).
    """
    print("\n" + "=" * 60)
    print("Loading H18 panel + merging DWZ Full decomp parquets")
    print("=" * 60)
    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h18_cccl_received",
            required_file="h18_cccl_received_panel.parquet",
        )
        panel_file = panel_dir / "h18_cccl_received_panel.parquet"
    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    # H18 panel: DV + controls + UncPreCEO + identifiers (incl ceo_id for Full FE merge).
    columns = [
        "file_name",
        "start_date",
        "gvkey", "ceo_id", "year", "fyearq_int", "ff12_code",
        "CCCL", "CCCL_lag",
        "UncPreCEO",
        "lnAssets", "TobinsQ", "ROA", "Leverage",
        "Capex", "CashRatio", "DivDummy", "sCFO",
        "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
    ]
    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  H18 panel:  {panel_file}")
    print(f"  H18 rows:   {len(panel):,}")
    print(f"  CCCL treatment rate: {panel['CCCL'].mean()*100:.3f}% ({panel['CCCL'].sum():,}/{panel['CCCL'].notna().sum():,})")

    # Build calendar year-quarter index (H18 panel does not pre-emit cal_yr_qtr).
    panel = build_cal_yr_qtr_index(panel)
    print(f"  cal_yr_qtr coverage: {panel['cal_yr_qtr'].notna().sum():,}/{len(panel):,}")

    # ----- Merge 1: DWZ Full residual (UncResCEO) on file_name -----
    full_dir = get_latest_output_dir(
        root_path / "outputs" / "econometric" / "ceo_clarity_extended",
        required_file="ceo_clarity_residual.parquet",
    )
    full_resid_file = full_dir / "ceo_clarity_residual.parquet"
    full_resid = pd.read_parquet(full_resid_file, columns=["file_name", "UncResCEO"])
    print(f"  Full residual:   {full_resid_file}")
    print(f"  Full resid rows: {len(full_resid):,}")
    panel = panel.merge(full_resid, on="file_name", how="left", validate="one_to_one")
    print(f"  After Full UncResCEO merge: {panel['UncResCEO'].notna().sum():,} matched")

    # ----- Merge 2: DWZ Full FE (ClarityCEO) on ceo_id (per-CEO constant) -----
    full_fe_file = full_dir / "ceo_clarity_fe.parquet"
    full_fe = pd.read_parquet(full_fe_file, columns=["ceo_id", "ClarityCEO"])
    print(f"  Full FE:         {full_fe_file}")
    print(f"  Full FE rows:    {len(full_fe):,} CEOs")
    if panel["ceo_id"].dtype != full_fe["ceo_id"].dtype:
        full_fe["ceo_id"] = full_fe["ceo_id"].astype(panel["ceo_id"].dtype)
    panel = panel.merge(full_fe, on="ceo_id", how="left", validate="many_to_one")
    print(f"  After Full ClarityCEO merge: {panel['ClarityCEO'].notna().sum():,} matched")

    return panel


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample filter: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(panel: pd.DataFrame, spec: Dict[str, Any]) -> pd.DataFrame:
    dv = spec["dv"]
    fe_type = spec["fe"]
    controls = BASE_CONTROLS if spec["controls"] == "base" else EXTENDED_CONTROLS

    panel = panel.copy()
    panel["Lagged_DV"] = panel[_lag_column_for_dv(dv)]

    required = [dv] + KEY_IVS + controls + ["gvkey", "fyearq_int", "ff12_code"]
    if fe_type.endswith("_yq"):
        required.append("cal_yr_qtr")
    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)
    for iv in KEY_IVS:
        pct_missing = df[iv].isna().mean() * 100
        if pct_missing > 50:
            print(f"  WARNING: {iv} has {pct_missing:.1f}% missing values")

    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()
    print(f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
          f"{len(df):,} calls, {df['gvkey'].nunique():,} firms")
    return df


def run_regression(df_prepared: pd.DataFrame, spec: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
    col_num = spec["col"]
    dv = spec["dv"]
    fe_type = spec["fe"]
    controls = BASE_CONTROLS if spec["controls"] == "base" else EXTENDED_CONTROLS

    print(f"\n" + "=" * 60)
    print(f"Running regression: Col ({col_num}) | DV={dv} | FE={fe_type} | Controls={spec['controls']}")
    print("=" * 60)

    if len(df_prepared) < 100:
        return None, {}

    exog = KEY_IVS + controls

    time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"
    base_fe = fe_type.replace("_yq", "")
    fe_label = (
        f"{'Industry(FF12)' if base_fe == 'industry' else 'Firm'}"
        f" + {'CalYrQtr' if fe_type.endswith('_yq') else 'CalYear'}"
    )

    print(f"  FE: {fe_label}")
    print(f"  N calls: {len(df_prepared):,}  |  N firms: {df_prepared['gvkey'].nunique():,}")
    print("  Estimating with firm-level clustered SEs via PanelOLS...")
    t0 = datetime.now()

    df_panel = df_prepared.set_index(["gvkey", time_col])

    try:
        if base_fe == "industry":
            model_obj = PanelOLS(
                dependent=df_panel[dv], exog=df_panel[exog],
                entity_effects=False, time_effects=True,
                other_effects=df_panel["ff12_code"],
                drop_absorbed=True, check_rank=False,
            )
            model = model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
        else:
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
            model = model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {elapsed:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}  N obs: {int(model.nobs):,}")

    meta: Dict[str, Any] = {
        "col": col_num, "dv": dv, "fe": fe_type, "controls": spec["controls"],
        "n_obs": int(model.nobs), "n_firms": df_prepared["gvkey"].nunique(),
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
        "dv_mean": float(model.model.dependent.dataframe.mean().iloc[0]),
    }

    for iv in KEY_IVS:
        beta = float(model.params.get(iv, np.nan))
        se = float(model.std_errors.get(iv, np.nan))
        p_two = float(model.pvalues.get(iv, np.nan))
        t_stat = float(model.tstats.get(iv, np.nan))
        if not np.isnan(p_two) and not np.isnan(beta):
            direction = IV_TAIL_DIRECTION.get(iv, "positive")
            if direction == "negative":
                p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
            else:  # "positive"
                p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
        else:
            p_one = np.nan
        meta[f"{iv}_beta"] = beta
        meta[f"{iv}_se"] = se
        meta[f"{iv}_t"] = t_stat
        meta[f"{iv}_p_one"] = p_one
        stars = _sig_stars(p_one)
        dir_label = "neg" if IV_TAIL_DIRECTION.get(iv) == "negative" else "pos"
        print(f"  {iv}: beta={beta:.6f} SE={se:.6f} p1({dir_label})={p_one:.4f} {stars}")

    return model, meta


def _sig_stars(p):
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def _save_latex_table(all_results, out_dir):
    results_by_col = {r["meta"]["col"]: r["meta"] for r in all_results if r.get("meta")}
    n_cols = 6

    def fmt_coef(v, s): return "" if np.isnan(v) else f"{v:.4f}{s}"
    def fmt_se(v): return "" if np.isnan(v) else f"({v:.4f})"
    def fmt_int(v): return f"{v:,}"
    def fmt_r2(v):
        if np.isnan(v):
            return ""
        if abs(v) < 0.001:
            return f"{v:.2e}"
        return f"{v:.3f}"

    lines = [
        r"\begin{table}[htbp]", r"\centering",
        r"\caption{" + SUITE_CAPTION + r"}",
        r"\label{" + SUITE_LABEL + r"}", r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}", r"\toprule",
    ]
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")
    lines.append(r" & \multicolumn{6}{c}{CCCL (Lerman et al. 2024)} \\")
    lines.append(r"\cmidrule(lr){2-7}")
    lines.append(r"\midrule")

    for iv in KEY_IVS:
        label = VARIABLE_LABELS.get(iv, iv)
        coefs = [fmt_coef(results_by_col.get(c, {}).get(f"{iv}_beta", np.nan),
                          _sig_stars(results_by_col.get(c, {}).get(f"{iv}_p_one", np.nan)))
                 for c in range(1, n_cols + 1)]
        lines.append(f"{label} & " + " & ".join(coefs) + r" \\")
        ses = [fmt_se(results_by_col.get(c, {}).get(f"{iv}_se", np.nan))
               for c in range(1, n_cols + 1)]
        lines.append(f" & " + " & ".join(ses) + r" \\")

    lines.append(r"\midrule")
    ctrl = ["Extended" if results_by_col.get(c, {}).get("controls") == "extended" else "Base" for c in range(1, n_cols + 1)]
    lines.append(r"Controls & " + " & ".join(ctrl) + r" \\")
    ind_fe_cells, firm_fe_cells, year_fe_cells, yr_qtr_fe_cells = [], [], [], []
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
    ns = [fmt_int(results_by_col.get(c, {}).get("n_obs", 0)) for c in range(1, n_cols + 1)]
    lines.append(r"N & " + " & ".join(ns) + r" \\")
    r2s = [fmt_r2(results_by_col.get(c, {}).get("r2", np.nan)) for c in range(1, n_cols + 1)]
    lines.append(r"$R^2$ & " + " & ".join(r2s) + r" \\")
    adj_r2s = [fmt_r2(results_by_col.get(c, {}).get("adj_r2", np.nan)) for c in range(1, n_cols + 1)]
    lines.append(r"Adj.~$R^2$ & " + " & ".join(adj_r2s) + r" \\")
    dv_means = [fmt_r2(results_by_col.get(c, {}).get("dv_mean", np.nan)) for c in range(1, n_cols + 1)]
    lines.append(r"DV Mean & " + " & ".join(dv_means) + r" \\")

    lines += [
        r"\bottomrule", r"\end{tabular}",
        r"\begin{minipage}{\linewidth}", r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$. ",
        r"DWZ Eq.5 decomposition variant: replaces UncAnsCEO with ",
        r"\textit{ClarityCEO} (= negated CEO fixed effect from DWZ Eq.4) and ",
        r"\textit{UncResCEO} (call-level residual), Full method (single full-panel Eq.4 fit). ",
        r"\textit{UncPreCEO} (raw, presentation-segment uncertainty) is preserved as a ",
        r"third IV from the parent suite (DWZ Eq.4 RHS regressor; not decomposed because ",
        r"its persistent CEO-trait variance is already absorbed by ClarityCEO). ",
        r"\textit{ClarityCEO}: one-tailed NEG ($\beta < 0$; clear CEO $\Rightarrow$ less SEC scrutiny). ",
        r"\textit{UncResCEO}: one-tailed POS ($\beta > 0$; uncertainty surprise $\Rightarrow$ more SEC scrutiny; \citeA{lerman2024}). ",
        r"\textit{UncPreCEO}: one-tailed POS ($\beta > 0$; pres uncertainty $\Rightarrow$ more SEC scrutiny). ",
        r"Standard errors (in parentheses) firm-level clustered. ",
        r"Main sample (excludes financial and utility firms). ",
        r"CCCL (\textit{Conference Call Comment Letter}) is a binary indicator equal to 1 if the firm received an SEC comment letter referencing the earnings conference call within the window $(\textit{call}_t, \textit{call}_{t+1}]$ and 0 otherwise. Treatment rate $\sim 0.4\%$. Estimated via Linear Probability Model (LPM) on PanelOLS, justified by Timoneda (2021) Monte Carlo: LPM-FE outperforms logit at low base rates. ",
        r"Lagged\_DV control = true t-1 prior-quarter CCCL receipt. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}", r"\end{table}",
    ]
    with open(out_dir / "h18_cccl_received_ceo2iv_decomp_table.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: h18_cccl_received_ceo2iv_decomp_table.tex")


def save_outputs(all_results, out_dir):
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)
    out_dir.mkdir(parents=True, exist_ok=True)
    for r in all_results:
        model, meta = r.get("model"), r.get("meta", {})
        if model is None or not meta: continue
        col_num = meta["col"]
        with open(out_dir / f"regression_results_col{col_num}.txt", "w", encoding="utf-8") as f:
            f.write(f"Col ({col_num}) | DV: {meta['dv']} | FE: {meta['fe']} | Controls: {meta['controls']}\n")
            f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
            f.write(f"DV_Mean: {meta.get('dv_mean', float('nan')):.10f}\n")
            f.write("=" * 60 + "\n\n" + str(model.summary))
        print(f"  Saved: regression_results_col{col_num}.txt")

    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} regressions)")
    _save_latex_table(all_results, out_dir)
    return diag_df




def _write_suite_spec_json(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec_H18.ceo2.decomp.json with per-IV directional p_one.

    Per-IV directional stitching across (positive, negative) per IV_TAIL_DIRECTION.
    Controls extracted explicitly via separate call (p_one always None for controls).
    """
    from f1d.shared.outputs import extract_coefs_panelols

    results_by_col = {r["meta"]["col"]: r for r in all_results if r.get("meta")}

    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    for spec in MODEL_SPECS:
        col_num = spec["col"]
        if col_num not in results_by_col:
            raise RuntimeError(
                f"H18.ceo2.decomp spec build: missing result for col {col_num}"
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

        try:
            dv_mean: Optional[float] = float(
                model.model.dependent.dataframe.mean().iloc[0]
            )
        except Exception:
            dv_mean = None

        col_metadata.append(
            {
                "col": col_num,
                "dv": spec["dv"],
                "fe_entity": fe_entity,
                "fe_time": fe_time,
                "control_vars": control_list,
                "n_obs": int(meta["n_obs"]),
                "n_firms": int(meta["n_firms"]) if meta.get("n_firms") is not None else None,
                "r2": float(meta["r2"]),
                "adj_r2": float(meta["adj_r2"]) if meta.get("adj_r2") is not None else None,
                "dv_mean": dv_mean,
                "cluster_fallback": False,
            }
        )

        # Per-IV directional stitching
        merged: Dict[str, Dict[str, Any]] = {}
        for direction in ("positive", "negative"):
            ivs_for_dir = [
                iv for iv in KEY_IVS if IV_TAIL_DIRECTION.get(iv) == direction
            ]
            if not ivs_for_dir:
                continue
            coefs = extract_coefs_panelols(
                model=model,
                key_ivs=ivs_for_dir,
                all_vars=KEY_IVS + control_list,
                hyp_dir=direction,
            )
            for iv in ivs_for_dir:
                if iv in coefs:
                    merged[iv] = coefs[iv]

        # Carry-over control coefs (no direction matters; controls always p_one=None)
        control_coefs = extract_coefs_panelols(
            model=model,
            key_ivs=[],
            all_vars=control_list,
            hyp_dir="none",
        )
        merged.update(control_coefs)
        coefs_per_col.append(merged)

    header_rows = [
        [
            {"label": r"CCCL", "span": 6},
        ]
    ]
    ivs_payload = [
        {
            "name": iv,
            "label": VARIABLE_LABELS.get(iv, iv).replace("_", r"\_"),
            "tail": "one_neg" if IV_TAIL_DIRECTION.get(iv) == "negative" else "one_pos",
        }
        for iv in KEY_IVS
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
                "col_range": [s["col"] for s in MODEL_SPECS],
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
        controls={
            "base": list(BASE_CONTROLS),
            "extended_only": list(EXTENDED_ONLY_CONTROLS),
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / SUITE_DIR_NAME / timestamp
    log_dir = setup_run_logging(log_base_dir=root / "logs", suite_name="H18_CCCL_ceo2iv_decomp", timestamp=timestamp)

    print("=" * 80)
    print("STAGE 4: Test H18 CEO 3-IV DECOMP CCCL (6-col, LPM)")
    print("=" * 80)
    print(f"IVs:  {', '.join(KEY_IVS)}  (DWZ Eq.5 Full method)")
    print(f"Tails: Clarity NEG / UncRes POS / UncPre POS")

    panel = load_panel(root, panel_path)
    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "h18_cccl_received",
        required_file="h18_cccl_received_panel.parquet",
    ) / "h18_cccl_received_panel.parquet"

    full_panel_n = len(panel)
    panel = filter_main_sample(panel)
    main_panel_n = len(panel)

    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv", output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics -- H18 CEO 3-IV Decomp CCCL (Main Sample)",
        label="tab:summary_stats_h18_ceo2_decomp",
    )

    all_results: List[Dict[str, Any]] = []
    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} FE={spec['fe']} Controls={spec['controls']} ---")
        try:
            df_prepared = prepare_regression_data(panel, spec)
        except ValueError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue
        if len(df_prepared) < 100:
            continue
        model, meta = run_regression(df_prepared, spec)
        if model is not None and meta:
            all_results.append({"model": model, "meta": meta})

    diag_df = save_outputs(all_results, out_dir)

    # Emit canonical suite_spec.json (consumed by generate_all_tables.py)
    _write_suite_spec_json(all_results, out_dir)

    if all_results:
        first_meta = all_results[0].get("meta", {})
        generate_attrition_table([
            ("Full panel", full_panel_n),
            ("Main sample", main_panel_n),
            ("CCCL non-null", panel["CCCL"].notna().sum()),
            ("CCCL receipt count", int(panel["CCCL"].sum())),
            ("Complete-case + min-calls (col 1)", first_meta.get("n_obs", 0)),
        ], out_dir, "H18 CEO 3-IV Decomp CCCL")

    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv",
                      "table": out_dir / "h18_cccl_received_ceo2iv_decomp_table.tex"},
        panel_path=panel_file,
    )

    duration = (datetime.now() - start_time).total_seconds()
    with open(out_dir / "report_step4_H18_ceo2iv_decomp.md", "w", encoding="utf-8") as f:
        f.write(f"# H18 CEO 3-IV Decomp Report (6-col, CCCL LPM)\n\n**Duration:** {duration:.1f}s\n")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s  |  Regressions: {len(all_results)}/{len(MODEL_SPECS)}")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
