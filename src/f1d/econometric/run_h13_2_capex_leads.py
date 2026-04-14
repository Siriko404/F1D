#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H13.2 Capex Lead Horizons Hypothesis
================================================================================
ID: econometric/run_h13_2_capex_leads
Description: Run H13.2 — does speech uncertainty predict capital expenditure
             at lead horizons t+1 through t+4?

DVs: Capex_lead (t+1), Capex_lead2 (t+2), Capex_lead3 (t+3), Capex_lead4 (t+4)
     = capxy_annual / lagged_atq (Q4 annual CapEx / Assets)

16 Model Specifications:
    4 DVs x 4 FE specs (extended controls only):
        Industry(FF12) + CalYear
        Firm + CalYear
        Industry(FF12) + CalYrQtr
        Firm + CalYrQtr

Key IVs (4, simultaneous):
    UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr

Hypothesis: Two-tailed (no directional prediction for capex).

Lagged DV: Capex_lag (t-1) for ALL specs. NOT derived from DV name stripping
           (Capex_lead2.replace("_lead","") would give "Capex2" — bug).

Sample: Main only (FF12 != 8, 11).
SEs: Firm-level clustered (Petersen 2009).

Inputs:
    - outputs/variables/h13_2_capex_leads/latest/h13_2_capex_leads_panel.parquet

Outputs:
    - outputs/econometric/h13_2_capex_leads/{timestamp}/...

Author: Thesis Author
Date: 2026-04-05
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


# ==============================================================================
# Configuration
# ==============================================================================

KEY_IVS = [
    "UncAnsCEO",
    "UncPreCEO",
    "UncAnsMgr",
    "UncPreMgr",
]

# NOTE: Capex is the DV — must NOT appear as control.
# Extended controls only (no base-only specs in H13.2).
EXTENDED_CONTROLS = [
    "lnAssets",
    "TobinsQ",
    "ROA",
    "Leverage",
    "CashRatio",
    "DivDummy",
    "sCFO",
    "Lagged_DV",
    "SalesGrowth",
    "RDSales",
    "CashFlowAt",
    "DailyVola",
]

# H13.2 uses extended controls only — "base" control spec is aliased to extended
# to keep the shared helper signature uniform.
BASE_CONTROLS = EXTENDED_CONTROLS
EXTENDED_ONLY_CONTROLS: list[str] = []

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission.
# ------------------------------------------------------------------
SUITE_ID = "H13.2"
SUITE_DIR_NAME = "h13_2_capex_leads"
SUITE_TITLE = "Speech Uncertainty and Capital Expenditure — Lead Horizons"
SUITE_CAPTION = "H13.2: Speech Uncertainty and Capital Expenditure --- Lead Horizons"
SUITE_LABEL = "tab:h13_2"
SAMPLE_LABEL = "Main sample (excludes financial and utility firms)."
HYP_DIR = "none"  # H13.2: two-tailed (no signed prediction)
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}

MIN_CALLS_PER_FIRM = 5

MODEL_SPECS = [
    # Capex_lead (t+1)
    {"col": 1,  "dv": "Capex_lead",  "fe": "industry",    "controls": "extended", "extra_controls": []},
    {"col": 2,  "dv": "Capex_lead",  "fe": "firm",        "controls": "extended", "extra_controls": []},
    {"col": 3,  "dv": "Capex_lead",  "fe": "industry_yq", "controls": "extended", "extra_controls": []},
    {"col": 4,  "dv": "Capex_lead",  "fe": "firm_yq",     "controls": "extended", "extra_controls": []},
    # Capex_lead2 (t+2)
    {"col": 5,  "dv": "Capex_lead2", "fe": "industry",    "controls": "extended", "extra_controls": []},
    {"col": 6,  "dv": "Capex_lead2", "fe": "firm",        "controls": "extended", "extra_controls": []},
    {"col": 7,  "dv": "Capex_lead2", "fe": "industry_yq", "controls": "extended", "extra_controls": []},
    {"col": 8,  "dv": "Capex_lead2", "fe": "firm_yq",     "controls": "extended", "extra_controls": []},
    # Capex_lead3 (t+3)
    {"col": 9,  "dv": "Capex_lead3", "fe": "industry",    "controls": "extended", "extra_controls": []},
    {"col": 10, "dv": "Capex_lead3", "fe": "firm",        "controls": "extended", "extra_controls": []},
    {"col": 11, "dv": "Capex_lead3", "fe": "industry_yq", "controls": "extended", "extra_controls": []},
    {"col": 12, "dv": "Capex_lead3", "fe": "firm_yq",     "controls": "extended", "extra_controls": []},
    # Capex_lead4 (t+4)
    {"col": 13, "dv": "Capex_lead4", "fe": "industry",    "controls": "extended", "extra_controls": []},
    {"col": 14, "dv": "Capex_lead4", "fe": "firm",        "controls": "extended", "extra_controls": []},
    {"col": 15, "dv": "Capex_lead4", "fe": "industry_yq", "controls": "extended", "extra_controls": []},
    {"col": 16, "dv": "Capex_lead4", "fe": "firm_yq",     "controls": "extended", "extra_controls": []},
]

VARIABLE_LABELS = {
    "UncAnsCEO": "CEO QA Uncertainty",
    "UncPreCEO": "CEO Pres Uncertainty",
    "UncAnsMgr": "Mgr QA Uncertainty",
    "UncPreMgr": "Mgr Pres Uncertainty",
}

SUMMARY_STATS_VARS = [
    {"col": "Capex_lead", "label": r"CapEx$_{t+1}$ / Assets"},
    {"col": "Capex_lead2", "label": r"CapEx$_{t+2}$ / Assets"},
    {"col": "Capex_lead3", "label": r"CapEx$_{t+3}$ / Assets"},
    {"col": "Capex_lead4", "label": r"CapEx$_{t+4}$ / Assets"},
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    {"col": "UncAnsMgr", "label": "Mgr QA Uncertainty"},
    {"col": "UncPreMgr", "label": "Mgr Pres Uncertainty"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "CashRatio", "label": "Cash Holdings"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "sCFO", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RDSales", "label": r"R\&D Intensity"},
    {"col": "CashFlowAt", "label": "Cash Flow"},
    {"col": "DailyVola", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H13.2 Capex Lead Horizons (call-level)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load call-level H13.2 panel."""
    print("\n" + "=" * 60)
    print("Loading H13.2 panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h13_2_capex_leads",
            required_file="h13_2_capex_leads_panel.parquet",
        )
        panel_file = panel_dir / "h13_2_capex_leads_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}, Columns: {len(panel.columns)}")

    # Build calendar year-quarter index for YQ FE specs
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,}")

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
    fe_type = spec["fe"]
    controls = EXTENDED_CONTROLS

    # HARDCODED Lagged_DV = Capex_lag for ALL specs
    # Cannot use dv.replace("_lead","") because Capex_lead2 -> Capex2 (bug)
    panel = panel.copy()
    panel["Lagged_DV"] = panel["Capex_lag"]

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
    """Run PanelOLS with FE and firm-level clustered SEs."""
    col_num = spec["col"]
    dv = spec["dv"]
    fe_type = spec["fe"]
    controls = EXTENDED_CONTROLS

    time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"
    base_fe = fe_type.replace("_yq", "")
    fe_label = f"{'Industry(FF12)' if base_fe == 'industry' else 'Firm'} + {'CalYrQtr' if fe_type.endswith('_yq') else 'CalYear'}"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_label} | Controls=extended")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    exog = KEY_IVS + controls
    n_firms = df_prepared["gvkey"].nunique()
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}")
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
            model = model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
        else:
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
            model = model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()
    adj_r2 = 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid
    print(f"  R-squared: {model.rsquared:.4f}  Adj R-squared: {adj_r2:.4f}  ({elapsed:.1f}s)")

    meta: Dict[str, Any] = {
        "col": col_num,
        "dv": dv,
        "fe": fe_type,
        "controls": "extended",
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "r2": float(model.rsquared),
        "adj_r2": adj_r2,
        "dv_mean": float(df_prepared[dv].mean()),
        "extra_controls": "",
    }

    # Two-tailed p-values (no directional prediction for capex)
    for iv in KEY_IVS:
        beta = float(model.params.get(iv, np.nan))
        se = float(model.std_errors.get(iv, np.nan))
        p_two = float(model.pvalues.get(iv, np.nan))

        meta[f"{iv}_beta"] = beta
        meta[f"{iv}_se"] = se
        meta[f"{iv}_p_two"] = p_two

        stars = _sig_stars(p_two)
        print(f"  {VARIABLE_LABELS.get(iv, iv)}: b={beta:.6f} p2={p_two:.4f} {stars}")

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
    """Write 16-column LaTeX table with 4 DV blocks."""
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    n_cols = 16

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
        r"\caption{Speech Uncertainty and Capital Expenditure --- Lead Horizons}",
        r"\label{tab:h13_2_capex_leads}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{l" + "c" * n_cols + "}",
        r"\toprule",
    ]

    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")

    # DV headers: 4 blocks of 4
    lines.append(
        r" & \multicolumn{4}{c}{CapEx$_{t+1}$}"
        r" & \multicolumn{4}{c}{CapEx$_{t+2}$}"
        r" & \multicolumn{4}{c}{CapEx$_{t+3}$}"
        r" & \multicolumn{4}{c}{CapEx$_{t+4}$} \\"
    )
    lines.append(
        r"\cmidrule(lr){2-5} \cmidrule(lr){6-9} \cmidrule(lr){10-13} \cmidrule(lr){14-17}"
    )
    lines.append(r"\midrule")

    # IV rows
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
    lines.append(r"Controls & " + " & ".join(["Extended"] * n_cols) + r" \\")
    lines.append(r"Lagged DV & " + " & ".join(["Yes"] * n_cols) + r" \\")

    # FE indicators
    ind_fe_cells, firm_fe_cells, year_fe_cells, yq_fe_cells = [], [], [], []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        fe = meta.get("fe", "")
        base_fe = fe.replace("_yq", "") if fe else ""
        is_yq = fe.endswith("_yq") if fe else False
        ind_fe_cells.append("Yes" if base_fe == "industry" else "")
        firm_fe_cells.append("Yes" if base_fe == "firm" else "")
        year_fe_cells.append("Yes" if not is_yq else "")
        yq_fe_cells.append("Yes" if is_yq else "")
    lines.append(r"Industry FE & " + " & ".join(ind_fe_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_fe_cells) + r" \\")
    lines.append(r"Calendar Year FE & " + " & ".join(year_fe_cells) + r" \\")
    lines.append(r"Year-Quarter FE & " + " & ".join(yq_fe_cells) + r" \\")

    lines.append(r"\midrule")

    # N and R²
    n_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        n_val = meta.get("n_obs", 0)
        n_cells.append(fmt_int(n_val) if n_val else "")
    lines.append(r"N & " + " & ".join(n_cells) + r" \\")

    r2_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        r2_cells.append(fmt_r2(meta.get("r2", np.nan)))
    lines.append(r"$R^2$ & " + " & ".join(r2_cells) + r" \\")

    adj_r2_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        adj_r2_cells.append(fmt_r2(meta.get("adj_r2", np.nan)))
    lines.append(r"Adj.~$R^2$ & " + " & ".join(adj_r2_cells) + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"}%",  # close \resizebox
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed). ",
        r"Standard errors (in parentheses) firm-level clustered. ",
        r"Main sample (excludes financial and utility firms). ",
        r"CapEx intensity is constant within firm-fiscal-year (Q4 capxy / lagged assets). ",
        r"Lagged DV = Capex$_{t-1}$ for all specifications. ",
        r"N declines across lead horizons due to consecutive fiscal year requirement. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h13_2_capex_leads_table.tex"
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
            f.write(f"H13.2 Capex Lead Horizons Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Controls: extended\n")
            f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    _save_latex_table(all_results, out_dir)

    return diag_df


def _write_suite_spec_json(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec_H13.2.json from runner state."""
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
            {"label": r"Capex\_lead", "span": 4},
            {"label": r"Capex\_lead2", "span": 4},
            {"label": r"Capex\_lead3", "span": 4},
            {"label": r"Capex\_lead4", "span": 4},
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
        ivs=[{"name": iv, "label": iv, "tail": "two"} for iv in KEY_IVS],
        controls={
            "base": list(BASE_CONTROLS),
            "extended_only": list(EXTENDED_ONLY_CONTROLS),
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h13_2_capex_leads" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H13_2_CapexLeads",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H13.2 Capex Lead Horizons")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    4 IVs x 4 DVs x 4 FE = 16 models (extended only)")
    print(f"DVs:       Capex_lead (t+1), Capex_lead2 (t+2), Capex_lead3 (t+3), Capex_lead4 (t+4)")

    panel, panel_file = load_panel(root, panel_path)

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    # Lead coverage
    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    for dv_col in ["Capex_lead", "Capex_lead2", "Capex_lead3", "Capex_lead4"]:
        n_valid = panel[dv_col].notna().sum()
        print(f"  {dv_col} non-null: {n_valid:,} ({100*n_valid/main_n:.1f}%)")

    # Summary statistics
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H13.2 Capex Lead Horizons (Main Sample)",
        label="tab:summary_stats_h13_2",
    )
    print("  Saved: summary_stats.csv/.tex")

    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} FE={spec['fe']} ---")
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
        first = all_results[0]["meta"]
        last = all_results[-1]["meta"] if len(all_results) > 1 else first
        attrition_stages = [
            ("Full panel", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("After complete-case + min-calls (t+1, col 1)", first["n_obs"]),
            ("After complete-case + min-calls (t+4, col 13)", last.get("n_obs", 0)),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H13.2 Capex Lead Horizons")
        print("  Saved: sample_attrition.csv/.tex")

    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")

    # Summary: significance by IV across all lead horizons
    for iv in KEY_IVS:
        sig_count = sum(
            1 for r in all_results
            if r["meta"].get(f"{iv}_p_two", 1.0) < 0.05
        )
        print(f"  {VARIABLE_LABELS.get(iv, iv)}: {sig_count}/{len(all_results)} significant (p<0.05, two-tail)")

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
