#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H14c BGTLevel_Spread (12-col 2-DV)
================================================================================
ID: econometric/run_h14c_spread_bgt_level
Description: Run H14 Bid-Ask Spread hypothesis test using 12 model specifications
             with 4 simultaneous uncertainty IVs and a contemp + t+1 lead DV.

Model Specifications (12 columns):
    Cols 1-6:  DV = BGTLevel_Spread (contemporaneous)
    Cols 7-12: DV = BGTLevel_Spread_lead1 (next-quarter lead)

DV: BGTLevel_Spread = mean(RelSpread[+1,+3]) - mean(RelSpread[-3,-1])
    where RelSpread_d = 2*(ASK_d - BID_d)/(ASK_d + BID_d)  [closing quotes]
    Following Lee (2016, The Accounting Review).

Key Independent Variables (4):
    UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr

Base Controls (8):
    lnAssets, TobinsQ, ROA, Leverage, Capex, DivDummy, sCFO, Lagged_DV
    NOTE: Lagged_DV placeholder routed at spec-prep time.
    NOTE: PreCallSpread REMOVED from controls (replaced by true t-1 lag).

Extended Controls (Base + 4):
    + StockPrice, Turnover, DailyVola, AbsSurpDec

Sample: Main only (FF12 codes 1-7, 9-10, 12).

Hypothesis Test: One-tailed (beta > 0).
Standard Errors: Firm-level clustered following Petersen (2009); see
    docs/Draft/DECISIONS.md §2.1 for Phase 2.5 empirical justification.

Author: Thesis Author
Date: 2026-04-17 (12-col 2-DV upgrade)
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
    build_col_data_from_panelols,
    generate_attrition_table,
    generate_manifest,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index

warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)



# ----------------------------------------------------------------------
# H14c window construction:
# BGT (2018) 25-day post-call window applied to Lee (2016) closing-quote bid-ask spread formula. Window = [0, +25] trading days, day 0 INCLUDED per BGT verbatim. Hybrid construction (window from BGT, formula from Lee).
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

# Lagged_DV placeholder routed at spec-prep time (PreCallSpread removed)
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
    "StockPrice",
    "Turnover",
    "DailyVola",
    "AbsSurpDec",
]

EXTENDED_ONLY_CONTROLS = [c for c in EXTENDED_CONTROLS if c not in BASE_CONTROLS]

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission.
# ------------------------------------------------------------------
SUITE_ID = "H14c"
SUITE_DIR_NAME = "h14c_spread_bgt_level"
SUITE_TITLE = 'H14c: Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Level (, day 0 included)'
SUITE_CAPTION = r'H14c: Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Level ($[0,+25]$, day 0 included)'
SUITE_LABEL = "tab:h14c"
SAMPLE_LABEL = "Main sample (excludes financial and utility firms)."
HYP_DIR = "positive"
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}

MODEL_SPECS = [
    {"col": 1,  "dv": "BGTLevel_Spread",       "fe": "industry",    "controls": "base"},
    {"col": 2,  "dv": "BGTLevel_Spread",       "fe": "firm",        "controls": "base"},
    {"col": 3,  "dv": "BGTLevel_Spread",       "fe": "industry",    "controls": "extended"},
    {"col": 4,  "dv": "BGTLevel_Spread",       "fe": "firm",        "controls": "extended"},
    {"col": 5,  "dv": "BGTLevel_Spread",       "fe": "industry_yq", "controls": "extended"},
    {"col": 6,  "dv": "BGTLevel_Spread",       "fe": "firm_yq",     "controls": "extended"},
    {"col": 7,  "dv": "BGTLevel_Spread_lead1", "fe": "industry",    "controls": "base"},
    {"col": 8,  "dv": "BGTLevel_Spread_lead1", "fe": "firm",        "controls": "base"},
    {"col": 9,  "dv": "BGTLevel_Spread_lead1", "fe": "industry",    "controls": "extended"},
    {"col": 10, "dv": "BGTLevel_Spread_lead1", "fe": "firm",        "controls": "extended"},
    {"col": 11, "dv": "BGTLevel_Spread_lead1", "fe": "industry_yq", "controls": "extended"},
    {"col": 12, "dv": "BGTLevel_Spread_lead1", "fe": "firm_yq",     "controls": "extended"},
]

MIN_CALLS_PER_FIRM = 5

VARIABLE_LABELS = {
    "UncAnsCEO": "CEO QA Uncertainty",
    "UncPreCEO": "CEO Pres Uncertainty",
    "UncAnsMgr": "Mgr QA Uncertainty",
    "UncPreMgr": "Mgr Pres Uncertainty",
}

SUMMARY_STATS_VARS = [
    {"col": "BGTLevel_Spread", "label": r"$\Delta$Spread$_t$"},
    {"col": "BGTLevel_Spread_lead1", "label": r"$\Delta$Spread$_{t+1}$"},
    {"col": "PreCallSpread", "label": "Pre-Call Spread"},
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
    {"col": "StockPrice", "label": "Stock Price"},
    {"col": "Turnover", "label": "Share Turnover"},
    {"col": "DailyVola", "label": "Return Volatility"},
    {"col": "AbsSurpDec", "label": r"$|$Earnings Surprise Decile$|$"},
]


def _lag_column_for_dv(dv: str) -> str:
    if dv.endswith("_lead1"):
        return dv[: -len("_lead1")]
    return f"{dv}_lag"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Stage 4: Test H14 Bid-Ask Spread (12-col 2-DV)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)
    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h14_bidask_spread",
            required_file="h14_bidask_spread_panel.parquet",
        )
        panel_file = panel_dir / "h14_bidask_spread_panel.parquet"
    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    columns = [
        "start_date",
        "gvkey", "year", "fyearq_int", "ff12_code",
        "cal_yr", "cal_qtr", "cal_yr_qtr",
        "BGTLevel_Spread", "BGTLevel_Spread_lag", "BGTLevel_Spread_lead1",
        "PreCallSpread",
        "UncAnsCEO", "UncPreCEO",
        "UncAnsMgr", "UncPreMgr",
        "lnAssets", "TobinsQ", "ROA", "Leverage",
        "Capex", "DivDummy", "sCFO",
        "StockPrice", "Turnover", "DailyVola", "AbsSurpDec",
    ]
    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}  |  Columns: {len(panel.columns)}")
    print(f"  BGTLevel_Spread non-null: {panel['BGTLevel_Spread'].notna().sum():,}")
    print(f"  BGTLevel_Spread_lead1 non-null: {panel['BGTLevel_Spread_lead1'].notna().sum():,}")

    # Bug 4 fix (Phase 7): spread ~1e-3 with coefs ~1e-5. Rescale by 10^4.
    panel["BGTLevel_Spread"] = panel["BGTLevel_Spread"] * 1e4
    panel["BGTLevel_Spread_lag"] = panel["BGTLevel_Spread_lag"] * 1e4
    panel["BGTLevel_Spread_lead1"] = panel["BGTLevel_Spread_lead1"] * 1e4

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
            p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
        else:
            p_one = np.nan
        meta[f"{iv}_beta"] = beta
        meta[f"{iv}_se"] = se
        meta[f"{iv}_t"] = t_stat
        meta[f"{iv}_p_one"] = p_one
        stars = _sig_stars(p_one)
        print(f"  {iv}: beta={beta:.6f} SE={se:.6f} p1={p_one:.4f} {stars}")

    return model, meta


def _sig_stars(p):
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


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
        r"\caption{H14c: Speech Uncertainty and BGT-Window 25-Day Closing-Quote Bid-Ask Spread LEVEL (contemp + $t+1$ lead)}",
        r"\label{tab:h14c_bgt_level_spread}", r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}", r"\toprule",
    ]
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")
    lines.append(
        r" & \multicolumn{6}{c}{$\Delta$Spread$_t$}"
        r" & \multicolumn{6}{c}{$\Delta$Spread$_{t+1}$} \\"
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
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed; H14: $\beta > 0$). ",
        r"Standard errors (in parentheses) firm-level clustered. ",
        r"Main sample (excludes financial and utility firms). ",
        r"BGTLevel_Spread$_t$ = BGT (2018) 25-day window applied to Lee (2016) closing-quote spread formula. ",
        r"BGTLevel_Spread$_{t+1}$ = next-quarter call's BGTLevel_Spread (calendar quarter, strict consecutive). ",
        r"Lagged\_DV control = true t-1 prior-quarter lag. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}", r"\end{table}",
    ]
    with open(out_dir / "h14c_spread_bgt_level_table.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: h14_bidask_spread_table.tex")


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
    """Emit canonical suite_spec_H14c.json from runner state."""
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
            {"label": r"BGTLevel\_Spread", "span": 6},
            {"label": r"BGTLevel\_Spread\_lead1", "span": 6},
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
        render_hints={
            "scaling_note": (
                r"BGTLevel\_Spread values rescaled by $10^4$ for readability; "
                r"multiply coefficients by $10^{-4}$ to recover raw units."
            ),
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
    out_dir = root / "outputs" / "econometric" / "h14c_spread_bgt_level" / timestamp
    log_dir = setup_run_logging(log_base_dir=root / "logs", suite_name="H14c_BGTLevel_Spread", timestamp=timestamp)

    print("=" * 80)
    print("STAGE 4: Test H14c BGTLevel_Spread (12-col 2-DV)")
    print("=" * 80)

    panel = load_panel(root, panel_path)
    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "h14_bidask_spread",
        required_file="h14_bidask_spread_panel.parquet",
    ) / "h14_bidask_spread_panel.parquet"

    full_panel_n = len(panel)
    panel = filter_main_sample(panel)
    main_panel_n = len(panel)

    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv", output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics -- H14c BGTLevel_Spread (Main Sample)",
        label="tab:summary_stats_h14c",
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
            ("BGTLevel_Spread non-null", panel["BGTLevel_Spread"].notna().sum()),
            ("BGTLevel_Spread_lead1 non-null", panel["BGTLevel_Spread_lead1"].notna().sum()),
            ("Complete-case + min-calls (col 1)", first_meta.get("n_obs", 0)),
        ], out_dir, "H14c BGTLevel_Spread")

    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv",
                      "table": out_dir / "h14c_spread_bgt_level_table.tex"},
        panel_path=panel_file,
    )

    duration = (datetime.now() - start_time).total_seconds()
    with open(out_dir / "report_step4_H14c.md", "w", encoding="utf-8") as f:
        f.write(f"# H14c Report (12-col 2-DV)\n\n**Duration:** {duration:.1f}s\n")

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
