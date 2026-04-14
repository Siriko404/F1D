#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H7d BGTDelta_Amihud (12-col 2-DV)
================================================================================
ID: econometric/run_h7d_amihud_bgt_delta
Description: Run H7 Illiquidity hypothesis test using 12 model specifications
             with 4 simultaneous uncertainty IVs and a contemp + t+1 lead DV.

Model Specifications (12 columns in one table):
    Cols 1-6:  DV = BGTDelta_Amihud (contemporaneous)
    Cols 7-12: DV = BGTDelta_Amihud_lead1 (next-quarter lead)

    Within each DV block:
      Col 1/7:   Industry FE + CalYear FE,  Base controls
      Col 2/8:   Firm FE     + CalYear FE,  Base controls
      Col 3/9:   Industry FE + CalYear FE,  Extended controls
      Col 4/10:  Firm FE     + CalYear FE,  Extended controls
      Col 5/11:  Industry FE + CalYrQtr FE, Extended controls
      Col 6/12:  Firm FE     + CalYrQtr FE, Extended controls

DV: BGTDelta_Amihud -- change in Amihud illiquidity around call ([+1,+3] - [-3,-1] days).
DV (lead): BGTDelta_Amihud_lead1 -- next-quarter call's BGTDelta_Amihud.

Key Independent Variables (4, all enter simultaneously):
    UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr

Base Controls (8):
    lnAssets, TobinsQ, ROA, Leverage, Capex, DivDummy, sCFO, Lagged_DV
    NOTE: Lagged_DV is a placeholder routed at spec-prep time:
          contemp DV -> {base}_lag; lead DV -> {base} (current value).
    NOTE: PreCallILLIQ has been REMOVED from controls (replaced by true t-1
          Lagged_DV via create_prior_quarter_lag at panel build time).

Extended Controls (Base + 4):
    + DailyVola, StockPrice, Turnover, UncQue

Sample: Main only (FF12 codes 1-7, 9-10, 12).

Hypothesis Test (one-tailed):
    H7: beta(uncertainty_var) > 0 -- higher uncertainty -> more illiquidity.
    Stars based on one-tailed p-values.

FE Time Index: cal_yr (cols 1-4, 7-10) or cal_yr_qtr (cols 5-6, 11-12).
Standard Errors: Firm-level clustered following Petersen (2009). Phase 2.5
    decision (2026-04-13) committed uniform firm-only clustering across
    non-macro suites; see docs/Draft/DECISIONS.md §2.1 for empirical
    justification from the H1 comparison test.
Industry FE: absorbed via PanelOLS constructor other_effects (not C() dummies).

Author: Thesis Author
Date: 2026-04-17 (12-col 2-DV upgrade)
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
    build_col_data_from_panelols,
    generate_attrition_table,
    generate_manifest,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index



# ----------------------------------------------------------------------
# H7d window construction:
# F1D extension of BGT (2018): mean Amihud over [+1, +25] minus mean over [-25, -1]. Day 0 EXCLUDED from both sides. Window length is BGT-verbatim, shape is F1D-pipeline convention.
# ----------------------------------------------------------------------

# ==============================================================================
# Configuration
# ==============================================================================

KEY_IVS = [
    "UncAnsCEO",
    "UncPreCEO",
    "UncAnsMgr",
    "UncPreMgr",
]

# Lagged_DV is a placeholder routed at spec-prep time via _lag_column_for_dv().
# PreCallILLIQ has been REMOVED -- replaced by the true t-1 prior-quarter lag.
BASE_CONTROLS = [
    "lnAssets",
    "TobinsQ",
    "ROA",
    "Leverage",
    "Capex",
    "DivDummy",
    "sCFO",
    "Lagged_DV",
]

EXTENDED_CONTROLS = BASE_CONTROLS + [
    "DailyVola",
    "StockPrice",
    "Turnover",
    "UncQue",
]

EXTENDED_ONLY_CONTROLS = [c for c in EXTENDED_CONTROLS if c not in BASE_CONTROLS]

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission.
# ------------------------------------------------------------------
SUITE_ID = "H7d"
SUITE_DIR_NAME = "h7d_amihud_bgt_delta"
SUITE_TITLE = 'H7d: Speech Uncertainty and BGT-Window 25-Day Amihud Delta ()'
SUITE_CAPTION = r'H7d: Speech Uncertainty and BGT-Window 25-Day Amihud Delta ($[+1,+25]-[-25,-1]$)'
SUITE_LABEL = "tab:h7d"
SAMPLE_LABEL = "Main sample (excludes financial and utility firms)."
HYP_DIR = "positive"
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}

MODEL_SPECS = [
    # Contemporaneous DV (cols 1-6)
    {"col": 1,  "dv": "BGTDelta_Amihud",       "fe": "industry",    "controls": "base"},
    {"col": 2,  "dv": "BGTDelta_Amihud",       "fe": "firm",        "controls": "base"},
    {"col": 3,  "dv": "BGTDelta_Amihud",       "fe": "industry",    "controls": "extended"},
    {"col": 4,  "dv": "BGTDelta_Amihud",       "fe": "firm",        "controls": "extended"},
    {"col": 5,  "dv": "BGTDelta_Amihud",       "fe": "industry_yq", "controls": "extended"},
    {"col": 6,  "dv": "BGTDelta_Amihud",       "fe": "firm_yq",     "controls": "extended"},
    # Next-quarter lead DV (cols 7-12)
    {"col": 7,  "dv": "BGTDelta_Amihud_lead1", "fe": "industry",    "controls": "base"},
    {"col": 8,  "dv": "BGTDelta_Amihud_lead1", "fe": "firm",        "controls": "base"},
    {"col": 9,  "dv": "BGTDelta_Amihud_lead1", "fe": "industry",    "controls": "extended"},
    {"col": 10, "dv": "BGTDelta_Amihud_lead1", "fe": "firm",        "controls": "extended"},
    {"col": 11, "dv": "BGTDelta_Amihud_lead1", "fe": "industry_yq", "controls": "extended"},
    {"col": 12, "dv": "BGTDelta_Amihud_lead1", "fe": "firm_yq",     "controls": "extended"},
]

MIN_CALLS_PER_FIRM = 5

VARIABLE_LABELS = {
    "UncAnsCEO": "CEO QA Uncertainty",
    "UncPreCEO": "CEO Pres Uncertainty",
    "UncAnsMgr": "Mgr QA Uncertainty",
    "UncPreMgr": "Mgr Pres Uncertainty",
}

SUMMARY_STATS_VARS = [
    {"col": "BGTDelta_Amihud", "label": "BGTDelta_Amihud$_t$"},
    {"col": "BGTDelta_Amihud_lead1", "label": "BGTDelta_Amihud$_{t+1}$"},
    {"col": "PreCallILLIQ", "label": "Pre-Call Amihud"},
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    {"col": "UncAnsMgr", "label": "Mgr QA Uncertainty"},
    {"col": "UncPreMgr", "label": "Mgr Pres Uncertainty"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "Capex", "label": "CapEx / Assets"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "sCFO", "label": "OCF Volatility"},
    {"col": "DailyVola", "label": "Stock Volatility"},
]


# ==============================================================================
# Lagged DV routing (placeholder pattern from run_h24_us_epu.py:149)
# ==============================================================================

def _lag_column_for_dv(dv: str) -> str:
    """Map a DV name to its actual t-1 lag column.

    For contemporaneous DV: returns {dv}_lag (true prior-quarter lag created
    by create_prior_quarter_lag at panel build time).
    For lead DV (e.g., BGTDelta_Amihud_lead1): returns the base DV name (the
    current-quarter value IS the lag of the next-quarter lead).
    """
    if dv.endswith("_lead1"):
        return dv[: -len("_lead1")]
    return f"{dv}_lag"


# ==============================================================================
# Argument parsing
# ==============================================================================

def parse_arguments():
    parser = argparse.ArgumentParser(description="Stage 4: Test H7 Illiquidity (12-col 2-DV)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data loading
# ==============================================================================

def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)
    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h7_illiquidity",
            required_file="h7_illiquidity_panel.parquet",
        )
        panel_file = panel_dir / "h7_illiquidity_panel.parquet"
    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    columns = [
        "start_date",
        "gvkey", "year", "fyearq_int", "ff12_code",
        # Cal-quarter index (built at panel time)
        "cal_yr", "cal_qtr", "cal_yr_qtr",
        # DV (contemp + lag + lead)
        "BGTDelta_Amihud", "BGTDelta_Amihud_lag", "BGTDelta_Amihud_lead1",
        # Pre-call (kept for summary stats; no longer in BASE_CONTROLS)
        "PreCallILLIQ",
        # Key IVs
        "UncAnsCEO", "UncPreCEO",
        "UncAnsMgr", "UncPreMgr",
        # Base + extended controls
        "lnAssets", "TobinsQ", "ROA", "Leverage", "Capex",
        "DivDummy", "sCFO",
        "DailyVola", "StockPrice", "Turnover",
        "UncQue",
    ]
    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}  |  Columns: {len(panel.columns)}")

    # cal_yr_qtr already exists in the panel (built at Phase C). Sanity check.
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} ({100*n_yr_qtr/len(panel):.1f}%)")

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

    # Route Lagged_DV placeholder to the actual lag column for this DV
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


# ==============================================================================
# Regression (H13 capex template — firm-level clustered, time_col switching)
# ==============================================================================

def run_regression(df_prepared: pd.DataFrame, spec: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
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

    exog = KEY_IVS + controls

    # Time index switches with FE type (matches H1 / H13 capex production pattern)
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
        else:  # "firm"
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

    meta: Dict[str, Any] = {
        "col": col_num, "dv": dv, "fe": fe_type, "controls": spec["controls"],
        "n_obs": int(model.nobs), "n_firms": df_prepared["gvkey"].nunique(),
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
        "dv_mean": float(model.model.dependent.dataframe.mean().iloc[0]),
    }

    # One-tailed: H7 beta > 0 (higher uncertainty -> more illiquidity)
    for iv in KEY_IVS:
        beta = float(model.params.get(iv, np.nan))
        se = float(model.std_errors.get(iv, np.nan))
        p_two = float(model.pvalues.get(iv, np.nan))
        t_stat = float(model.tstats.get(iv, np.nan))
        if not np.isnan(p_two) and not np.isnan(beta):
            p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
        else:
            p_one = np.nan
        meta[f"{iv}_beta"] = beta
        meta[f"{iv}_se"] = se
        meta[f"{iv}_t"] = t_stat
        meta[f"{iv}_p_one"] = p_one
        stars = _sig_stars(p_one)
        print(f"  {iv}: beta={beta:.4f} SE={se:.4f} p1={p_one:.4f} {stars}")

    return model, meta


def _sig_stars(p):
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


# ==============================================================================
# 12-col LaTeX table (H1 / H13 capex template)
# ==============================================================================

def _save_latex_table(all_results, out_dir):
    results_by_col = {r["meta"]["col"]: r["meta"] for r in all_results if r.get("meta")}
    n_cols = 12

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
        r"\caption{H7d: Speech Uncertainty and BGT-Window 25-Day Amihud DELTA (contemp + $t+1$ lead) [F1D extension]}",
        r"\label{tab:h7d_bgt_delta_amihud}", r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}", r"\toprule",
    ]
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")
    lines.append(
        r" & \multicolumn{6}{c}{$\Delta$Amihud$_t$}"
        r" & \multicolumn{6}{c}{$\Delta$Amihud$_{t+1}$} \\"
    )
    lines.append(r"\cmidrule(lr){2-7} \cmidrule(lr){8-13}")
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
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed; H7: $\beta > 0$). ",
        r"Standard errors (in parentheses) firm-level clustered. ",
        r"Main sample (excludes financial and utility firms). ",
        r"BGTDelta_Amihud$_t$ from BGT (2018, JAR) 25-day post-call window. ",
        r"BGTDelta_Amihud$_{t+1}$ = next-quarter call's BGTDelta_Amihud (calendar quarter, strict consecutive). ",
        r"Industry FE uses Fama-French 12 industry dummies. ",
        r"Time FE uses calendar year (\texttt{cal\_yr}) for cols 1--4, 7--10 or calendar year-quarter (\texttt{cal\_yr\_qtr}) for cols 5--6, 11--12. ",
        r"Lagged\_DV control = true t-1 prior-quarter lag (\texttt{create\_prior\_quarter\_lag}); replaces the former PreCallILLIQ control as of 2026-04-17. ",
        r"All variables winsorized at 1\%/99\% per year (controls at engine level; $\Delta$Amihud at builder level). ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}", r"\end{table}",
    ]
    with open(out_dir / "h7d_amihud_bgt_delta_table.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: h7_illiquidity_table.tex")


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
    """Emit canonical suite_spec_H7d.json from runner state."""
    col_metadata, coefs_per_col = build_col_data_from_panelols(
        all_results=all_results,
        model_specs=MODEL_SPECS,
        key_ivs=KEY_IVS,
        base_controls=BASE_CONTROLS,
        extended_controls=EXTENDED_CONTROLS,
        hyp_dir=HYP_DIR,
    )
    header_rows = [
        [
            {"label": r"BGTDelta\_Amihud", "span": 6},
            {"label": r"BGTDelta\_Amihud\_lead1", "span": 6},
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
        ivs=[{"name": iv, "label": iv, "tail": "one_pos"} for iv in KEY_IVS],
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
    out_dir = root / "outputs" / "econometric" / "h7d_amihud_bgt_delta" / timestamp
    log_dir = setup_run_logging(log_base_dir=root / "logs", suite_name="H7d_BGTDelta_Amihud", timestamp=timestamp)

    print("=" * 80)
    print("STAGE 4: Test H7d BGTDelta_Amihud (12-col 2-DV)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Sample:    Main only (FF12 != 8, 11)")
    print(f"IVs:       {len(KEY_IVS)} (all simultaneous)")
    print(f"Specs:     {len(MODEL_SPECS)} model columns (6 contemp + 6 lead)")
    print(f"Time FE:   cal_yr (cols 1-4, 7-10) + cal_yr_qtr (cols 5-6, 11-12)")
    print(f"Cluster:   Firm-level (Petersen 2009)")
    print(f"Test:      One-tailed (beta > 0)")

    panel = load_panel(root, panel_path)
    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "h7_illiquidity",
        required_file="h7_illiquidity_panel.parquet",
    ) / "h7_illiquidity_panel.parquet"

    full_panel_n = len(panel)
    panel = filter_main_sample(panel)
    main_panel_n = len(panel)

    print(f"\n  Main sample: {main_panel_n:,} calls, {panel['gvkey'].nunique():,} firms")
    print(f"  BGTDelta_Amihud non-null: {panel['BGTDelta_Amihud'].notna().sum():,}")
    print(f"  BGTDelta_Amihud_lead1 non-null: {panel['BGTDelta_Amihud_lead1'].notna().sum():,}")
    for iv in KEY_IVS:
        n_valid = panel[iv].notna().sum()
        print(f"  {iv}: {n_valid:,} ({100.0 * n_valid / main_panel_n:.1f}%)")

    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv", output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics -- H7d BGTDelta_Amihud (Main Sample)",
        label="tab:summary_stats_h7d",
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
            print(f"  Skipping: too few obs")
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
            ("BGTDelta_Amihud non-null", panel["BGTDelta_Amihud"].notna().sum()),
            ("BGTDelta_Amihud_lead1 non-null", panel["BGTDelta_Amihud_lead1"].notna().sum()),
            ("Complete-case + min-calls (col 1)", first_meta.get("n_obs", 0)),
        ], out_dir, "H7d BGTDelta_Amihud")

    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv",
                      "table": out_dir / "h7d_amihud_bgt_delta_table.tex"},
        panel_path=panel_file,
    )

    duration = (datetime.now() - start_time).total_seconds()
    with open(out_dir / "report_step4_H7d.md", "w", encoding="utf-8") as f:
        f.write(f"# H7d Report (12-col 2-DV)\n\n**Duration:** {duration:.1f}s\n**Sample:** Main only\n")
    print(f"  Saved: report_step4_H7d.md")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s  |  Regressions: {len(all_results)}/{len(MODEL_SPECS)}")
    for iv in KEY_IVS:
        sig = sum(1 for r in all_results
                  if r["meta"].get(f"{iv}_p_one", 1.0) < 0.05 and r["meta"].get(f"{iv}_beta", 0) > 0)
        print(f"  {iv}: {sig}/{len(all_results)} significant (p<0.05, one-tail, beta>0)")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print(f"KEY_IVS: {len(KEY_IVS)}, MODEL_SPECS: {len(MODEL_SPECS)}, BASE: {len(BASE_CONTROLS)}, EXT: {len(EXTENDED_CONTROLS)}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
