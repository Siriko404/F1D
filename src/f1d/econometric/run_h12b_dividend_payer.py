#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H12b Dividend Payer Hypothesis (Hoberg-Prabhala 2009 analog)
================================================================================
ID: econometric/run_h12b_dividend_payer
Description: Run H12b hypothesis test -- call-level binary dividend payer.

DV: DivPayerQ = (dvpsxq > 0).astype(float)
    Binary: 1 if firm paid any dividend this fiscal quarter (Compustat ex-date).
    Verbatim Compustat item 26 analog at quarterly frequency.
    Primary reference: Hoberg & Prabhala (2009, RFS) -- "Disappearing Dividends,
    Catering, and Risk" (annual firm-year DV; H12b extends to firm-quarter).
    Secondary reference: Chetty & Saez (2005, QJE) -- firm-quarter frequency
    precedent.

Lead DVs:
    DivPayerQ_lead1: next calendar quarter's DivPayerQ (via panel_utils
    canonical calendar-quarter helper; distinct from H12's fiscal-quarter leads).

12 Model Specifications:
    Cols 1-4:   DV = DivPayerQ (contemporaneous), Calendar Year FE
    Cols 5-6:   DV = DivPayerQ (contemporaneous), Year-Quarter FE
    Cols 7-10:  DV = DivPayerQ_lead1 (next quarter), Calendar Year FE
    Cols 11-12: DV = DivPayerQ_lead1 (next quarter), Year-Quarter FE
    Odd cols:   Industry FE (FF12)
    Even cols:  Firm FE
    Cols 1-2, 7-8:   Base controls
    Cols 3-6, 9-12:  Extended controls

Both contemp and lead specs use DivPayerQ_lag as the Lagged_DV control
(matches H12 convention -- same t-1 value regardless of contemp vs lead DV).

Key IVs (4, simultaneous, call-level):
    UncAnsCEO, UncPreCEO,
    UncAnsMgr, UncPreMgr

Hypothesis: One-tailed (beta < 0 -- higher uncertainty -> lower payer probability).
Rationale: Hoberg & Prabhala (2009) disappearing-dividends risk framing --
uncertainty reduces the likelihood of dividend payment.

Estimator: LPM via PanelOLS (Linear Probability Model).
Methodological justification: Timoneda (2021, Social Science Research) --
LPM-FE outperforms logit for binary DVs at a wide range of base rates;
no incidental parameters problem, no sample loss.

Sample: Main only (FF12 != 8, 11).
SEs: Firm-level clustered following Petersen (2009); see
     docs/Draft/DECISIONS.md §2.1 for Phase 2.5 empirical justification
     (decision committed 2026-04-13).
FE time: cal_yr (calendar year); cal_yr_qtr (calendar year-quarter) for YQ specs.

Inputs:
    - outputs/variables/h12_payout/latest/h12_payout_panel.parquet
      (shared with H12; piggybacks the H12 panel after the H12b extension).

Outputs:
    - outputs/econometric/h12b_dividend_payer/{timestamp}/...

Author: Thesis Author
Date: 2026-04-10
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
    "UncAnsCEO",
    "UncPreCEO",
    "UncAnsMgr",
    "UncPreMgr",
]

BASE_CONTROLS = [
    "lnAssets", "TobinsQ", "ROA", "Leverage", "CashRatio",
    "Capex", "sCFO",
    "Lagged_DV",
]

EXTENDED_CONTROLS = BASE_CONTROLS + [
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
]

MIN_CALLS_PER_FIRM = 5

MODEL_SPECS = [
    # Contemporaneous -- Calendar Year FE
    {"col": 1,  "dv": "DivPayerQ",       "fe": "industry",    "controls": "base",     "extra_controls": []},
    {"col": 2,  "dv": "DivPayerQ",       "fe": "firm",        "controls": "base",     "extra_controls": []},
    {"col": 3,  "dv": "DivPayerQ",       "fe": "industry",    "controls": "extended", "extra_controls": []},
    {"col": 4,  "dv": "DivPayerQ",       "fe": "firm",        "controls": "extended", "extra_controls": []},
    # Contemporaneous -- Year-Quarter FE (Extended controls only)
    {"col": 5,  "dv": "DivPayerQ",       "fe": "industry_yq", "controls": "extended", "extra_controls": []},
    {"col": 6,  "dv": "DivPayerQ",       "fe": "firm_yq",     "controls": "extended", "extra_controls": []},
    # Lead: next quarter -- Calendar Year FE
    {"col": 7,  "dv": "DivPayerQ_lead1", "fe": "industry",    "controls": "base",     "extra_controls": []},
    {"col": 8,  "dv": "DivPayerQ_lead1", "fe": "firm",        "controls": "base",     "extra_controls": []},
    {"col": 9,  "dv": "DivPayerQ_lead1", "fe": "industry",    "controls": "extended", "extra_controls": []},
    {"col": 10, "dv": "DivPayerQ_lead1", "fe": "firm",        "controls": "extended", "extra_controls": []},
    # Lead: next quarter -- Year-Quarter FE (Extended controls only)
    {"col": 11, "dv": "DivPayerQ_lead1", "fe": "industry_yq", "controls": "extended", "extra_controls": []},
    {"col": 12, "dv": "DivPayerQ_lead1", "fe": "firm_yq",     "controls": "extended", "extra_controls": []},
]

VARIABLE_LABELS = {
    "UncAnsCEO": "CEO QA Uncertainty",
    "UncPreCEO": "CEO Pres Uncertainty",
    "UncAnsMgr": "Mgr QA Uncertainty",
    "UncPreMgr": "Mgr Pres Uncertainty",
}

SUMMARY_STATS_VARS = [
    {"col": "DivPayerQ", "label": "DivPayerQ (call-level, dvpsxq>0)"},
    {"col": "DivPayerQ_lead1", "label": "DivPayerQ (next quarter)"},
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    {"col": "UncAnsMgr", "label": "Mgr QA Uncertainty"},
    {"col": "UncPreMgr", "label": "Mgr Pres Uncertainty"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "CashRatio", "label": "Cash Holdings"},
    {"col": "Capex", "label": "CapEx / Assets"},
    {"col": "sCFO", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RDSales", "label": "R\\&D Intensity"},
    {"col": "CashFlowAt", "label": "Cash Flow"},
    {"col": "DailyVola", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H12b Dividend Payer Indicator (call-level)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load call-level H12 panel (shared with H12b)."""
    print("\n" + "=" * 60)
    print("Loading H12 panel (shared with H12b)")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h12_payout",
            required_file="h12_payout_panel.parquet",
        )
        panel_file = panel_dir / "h12_payout_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}, Columns: {len(panel.columns)}")

    # Build calendar year-quarter index for YQ FE specs.
    # (Panel builder already adds cal_yr, cal_qtr, cal_yr_qtr; this is idempotent.)
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} ({100*n_yr_qtr/len(panel):.1f}%)")

    # Verify H12b columns present
    required_h12b = ["DivPayerQ", "DivPayerQ_lag", "DivPayerQ_lead1"]
    missing = [c for c in required_h12b if c not in panel.columns]
    if missing:
        raise ValueError(
            f"H12b columns missing from panel: {missing}. "
            "Rebuild the H12 panel with the H12b extension."
        )

    return panel, panel_file


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any],
) -> pd.DataFrame:
    """Prepare panel for a specific model specification."""
    dv = spec["dv"]
    ctrl_key = spec["controls"]
    fe_type = spec["fe"]
    extra_controls = spec["extra_controls"]
    controls = (BASE_CONTROLS if ctrl_key == "base" else EXTENDED_CONTROLS) + extra_controls

    # Lagged_DV routing: always DivPayerQ_lag (same t-1 value regardless of
    # contemp vs lead DV -- matches H12 convention at run_h12_payout.py:209-212).
    # `.replace("_lead1", "")` is a no-op for contemp DV "DivPayerQ" (substring
    # not present) and correctly strips the suffix for lead DV "DivPayerQ_lead1".
    base_dv = dv.replace("_lead1", "")
    lag_col = f"{base_dv}_lag"
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    required = [dv] + KEY_IVS + controls + ["gvkey", "fyearq_int", "ff12_code"]
    if fe_type.endswith("_yq"):
        required.append("cal_yr_qtr")

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Min calls per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()
    print(f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
          f"{len(df):,} calls, {df['gvkey'].nunique():,} firms")

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS LPM with FE and firm-level clustered SEs."""
    col_num = spec["col"]
    dv = spec["dv"]
    fe_type = spec["fe"]
    ctrl_key = spec["controls"]
    extra_controls = spec["extra_controls"]
    controls = (BASE_CONTROLS if ctrl_key == "base" else EXTENDED_CONTROLS) + extra_controls

    # Determine time index based on FE type (H1/H13 capex time_col-switching pattern)
    time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"
    base_fe = fe_type.replace("_yq", "")
    fe_label = f"{'Industry(FF12)' if base_fe == 'industry' else 'Firm'} + {'CalYrQtr' if fe_type.endswith('_yq') else 'CalYear'}"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_label} | Controls={ctrl_key}")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    exog = KEY_IVS + controls

    n_firms = df_prepared["gvkey"].nunique()
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}")
    if extra_controls:
        print(f"  Extra controls: {extra_controls}")
    t0 = datetime.now()

    df_panel = df_prepared.set_index(["gvkey", time_col])

    try:
        if base_fe == "industry":
            model_obj = PanelOLS(
                dependent=df_panel[dv],
                exog=df_panel[exog],
                entity_effects=False,
                time_effects=True,
                other_effects=df_panel["ff12_code"],
                drop_absorbed=True,
                check_rank=False,
            )
            model = model_obj.fit(
                cov_type="clustered",
                cluster_entity=True,
                cluster_time=False,
            )
        else:
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
            model = model_obj.fit(
                cov_type="clustered",
                cluster_entity=True,
                cluster_time=False,
            )
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"  R-squared: {model.rsquared:.4f}  Adj R-squared: {1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid:.4f}")

    # Build metadata with per-IV one-tailed p-values (H12b: beta < 0)
    meta: Dict[str, Any] = {
        "col": col_num,
        "dv": dv,
        "fe": fe_type,
        "controls": ctrl_key,
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
        "dv_mean": float(model.model.dependent.dataframe.mean().iloc[0]),
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
    }

    for iv in KEY_IVS:
        beta = float(model.params.get(iv, np.nan))
        se = float(model.std_errors.get(iv, np.nan))
        p_two = float(model.pvalues.get(iv, np.nan))

        # One-tailed: H12b expects beta < 0 (HP 2009 risk framing)
        if not np.isnan(p_two) and not np.isnan(beta):
            p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
        else:
            p_one = np.nan

        meta[f"{iv}_beta"] = beta
        meta[f"{iv}_se"] = se
        meta[f"{iv}_p_one"] = p_one

        stars = _sig_stars(p_one)
        print(f"  {VARIABLE_LABELS.get(iv, iv)}: b={beta:.4f} p1={p_one:.4f} {stars}")

    return model, meta


def _sig_stars(p: float) -> str:
    if np.isnan(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


# ==============================================================================
# Output
# ==============================================================================


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write unified 12-column LaTeX table with stars + SE in parentheses."""
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    n_cols = 12

    def fmt_coef(val, stars):
        return f"{val:.4f}{stars}" if not np.isnan(val) else ""

    def fmt_se(val):
        return f"({val:.4f})" if not np.isnan(val) else ""

    def fmt_int(val):
        return f"{val:,}"

    def fmt_r2(val):
        if np.isnan(val):
            return ""
        return f"{val:.2e}" if abs(val) < 0.001 else f"{val:.3f}"

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Speech Uncertainty and Dividend Payer Indicator (Hoberg-Prabhala 2009 analog)}",
        r"\label{tab:h12b_dividend_payer}",
        r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}",
        r"\toprule",
    ]

    # Column numbers
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")

    # DV headers with multicolumn
    lines.append(
        r" & \multicolumn{6}{c}{DivPayerQ}"
        r" & \multicolumn{6}{c}{DivPayerQ (next quarter)} \\"
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
            p_one = meta.get(f"{iv}_p_one", np.nan)
            coef_cells.append(fmt_coef(beta, _sig_stars(p_one)))
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

    # Lagged DV indicator (always Yes -- Lagged_DV is in BASE_CONTROLS)
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

    # DV Mean
    dv_mean_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        dv_mean = meta.get("dv_mean", np.nan)
        dv_mean_cells.append(f"{dv_mean:.3f}" if not np.isnan(dv_mean) else "")
    lines.append(r"DV Mean & " + " & ".join(dv_mean_cells) + r" \\")

    # R-sq
    r2_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        r2_cells.append(fmt_r2(meta.get("r2", np.nan)))
    lines.append(r"$R^2$ & " + " & ".join(r2_cells) + r" \\")

    # Adj R-sq
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
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed; $\beta < 0$). ",
        r"Standard errors (in parentheses) firm-level clustered. ",
        r"DivPayerQ = 1 if dvpsxq $>$ 0 in the fiscal quarter (Compustat ex-date). ",
        r"Primary reference: Hoberg \& Prabhala (2009, RFS) -- Compustat item 26 analog; extended from annual firm-year to firm-quarter. ",
        r"Secondary reference: Chetty \& Saez (2005, QJE) -- firm-quarter frequency precedent. ",
        r"LPM (Linear Probability Model) per Timoneda (2021). ",
        r"Main sample (excludes financial and utility firms). ",
        r"Lagged\_DV = DivPayerQ$_{t-1}$ (true calendar t-1, via create\_prior\_quarter\_lag). ",
        r"Year-quarter FE absorbs calendar year $\times$ quarter effects. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h12b_dividend_payer_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: {tex_path.name}")


def save_outputs(all_results: List[Dict[str, Any]], out_dir: Path) -> pd.DataFrame:
    """Save all outputs."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        col_num = meta["col"]
        fname = f"regression_results_col{col_num}.txt"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            f.write(f"H12b Dividend Payer Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"FE: {meta['fe']} + Year-Quarter\n")
            f.write(f"Controls: {meta['controls']}\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
            f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
            f.write(f"DV Mean: {meta.get('dv_mean', float('nan')):.6f}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    _save_latex_table(all_results, out_dir)

    return diag_df


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h12b_dividend_payer" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H12b_Dividend_Payer",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H12b Dividend Payer Indicator (Hoberg-Prabhala 2009 analog)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    4 IVs x 2 DVs x 3 FE x 2 controls = 12 models")
    print(f"FE time:   cal_yr (calendar year) + cal_yr_qtr (calendar year-quarter)")
    print(f"SEs:       Firm-level clustered")
    print(f"Direction: beta < 0 (one-tailed, HP 2009 risk framing)")

    panel, panel_file = load_panel(root, panel_path)

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    # Report dividend payer statistics
    n_dv_valid = panel["DivPayerQ"].notna().sum()
    n_dv1 = (panel["DivPayerQ"] == 1).sum()
    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    print(f"  DivPayerQ non-null: {n_dv_valid:,}")
    if n_dv_valid > 0:
        print(f"  DivPayerQ == 1 (payers): {n_dv1:,} "
              f"({100 * n_dv1 / n_dv_valid:.2f}% of non-null)")
    n_lead_valid = panel["DivPayerQ_lead1"].notna().sum()
    n_lead1 = (panel["DivPayerQ_lead1"] == 1).sum()
    print(f"  DivPayerQ_lead1 non-null: {n_lead_valid:,}")
    if n_lead_valid > 0:
        print(f"  DivPayerQ_lead1 == 1 (payers): {n_lead1:,} "
              f"({100 * n_lead1 / n_lead_valid:.2f}% of non-null)")

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H12b Dividend Payer (Main Sample)",
        label="tab:summary_stats_h12b",
    )
    print("  Saved: summary_stats.csv/.tex")

    # Run 12 regressions
    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} FE={spec['fe']} "
              f"Controls={spec['controls']} ---")
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

    # Save outputs
    diag_df = save_outputs(all_results, out_dir)

    # Attrition
    if all_results:
        first = all_results[0]["meta"]
        attrition_stages = [
            ("Full panel", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("DivPayerQ non-null", n_dv_valid),
            ("DivPayerQ == 1 (payers)", n_dv1),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H12b Dividend Payer")
        print("  Saved: sample_attrition.csv/.tex")

    # Manifest
    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")

    for iv in KEY_IVS:
        sig_count = sum(
            1 for r in all_results
            if r["meta"].get(f"{iv}_p_one", 1.0) < 0.05
            and r["meta"].get(f"{iv}_beta", 0) < 0
        )
        print(f"  {VARIABLE_LABELS.get(iv, iv)}: {sig_count}/{len(all_results)} significant (p<0.05, one-tail)")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: validating...")
        print(f"  IVs: {len(KEY_IVS)}")
        print(f"  Specs: {len(MODEL_SPECS)}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
