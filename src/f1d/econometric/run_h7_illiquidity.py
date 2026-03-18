#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H7 Post-Call Illiquidity Hypothesis
================================================================================
ID: econometric/test_h7_illiquidity
Description: Run H7 Illiquidity hypothesis test using 4 model specifications
             with 6 simultaneous uncertainty/clarity IVs, varying FE type and
             control set. Main sample only.

Model Specifications (4 columns in one table):
    Col 1: Industry FE (FF12) + FiscalYear FE, Base controls
    Col 2: Firm FE + FiscalYear FE, Base controls
    Col 3: Industry FE (FF12) + FiscalYear FE, Extended controls
    Col 4: Firm FE + FiscalYear FE, Extended controls

DV: delta_amihud — change in Amihud illiquidity around call ([+1,+3] - [-3,-1] days).

Key Independent Variables (6, all enter simultaneously):
    CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct,
    Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct,
    CEO_Clarity_Residual, Manager_Clarity_Residual

Base Controls (8, mirrors H14):
    Size, TobinsQ, ROA, Lev, CapexAt, DividendPayer, OCF_Volatility, pre_call_amihud

Extended Controls (Base + 4):
    + Volatility, StockPrice, Turnover, Analyst_QA_Uncertainty_pct

Sample: Main only (FF12 codes 1-7, 9-10, 12).

Hypothesis Test (one-tailed):
    H7: beta(uncertainty_var) > 0 — higher uncertainty -> more illiquidity.
    Stars based on one-tailed p-values.

FE Time Index: fyearq_int (fiscal year).
Standard Errors: Firm-clustered (groups=gvkey).
Industry FE: Absorbed via PanelOLS constructor other_effects (not C() dummies).

Author: Thesis Author
Date: 2026-03-17
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


# ==============================================================================
# Configuration
# ==============================================================================

KEY_IVS = [
    "CEO_QA_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
    "Manager_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Clarity_Residual",
    "Manager_Clarity_Residual",
]

# Mirrors H14 bid-ask spread pattern: standard 7 + lagged-DV control
BASE_CONTROLS = [
    "Size",
    "TobinsQ",
    "ROA",
    "Lev",
    "CapexAt",
    "DividendPayer",
    "OCF_Volatility",
    "pre_call_amihud",
]

EXTENDED_CONTROLS = BASE_CONTROLS + [
    "Volatility",
    "StockPrice",
    "Turnover",
    "Analyst_QA_Uncertainty_pct",
]

MODEL_SPECS = [
    {"col": 1, "dv": "delta_amihud", "fe": "industry", "controls": "base"},
    {"col": 2, "dv": "delta_amihud", "fe": "firm",     "controls": "base"},
    {"col": 3, "dv": "delta_amihud", "fe": "industry", "controls": "extended"},
    {"col": 4, "dv": "delta_amihud", "fe": "firm",     "controls": "extended"},
]

MIN_CALLS_PER_FIRM = 5

VARIABLE_LABELS = {
    "CEO_QA_Uncertainty_pct": "CEO QA Uncertainty",
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
    "Manager_QA_Uncertainty_pct": "Mgr QA Uncertainty",
    "Manager_Pres_Uncertainty_pct": "Mgr Pres Uncertainty",
    "CEO_Clarity_Residual": "CEO Clarity Residual",
    "Manager_Clarity_Residual": "Mgr Clarity Residual",
}

SUMMARY_STATS_VARS = [
    {"col": "delta_amihud", "label": "$\\Delta$Amihud (post$-$pre call)"},
    {"col": "pre_call_amihud", "label": "Pre-Call Amihud"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Clarity_Residual", "label": "CEO Clarity Residual"},
    {"col": "Manager_Clarity_Residual", "label": "Mgr Clarity Residual"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "CapexAt", "label": "CapEx / Assets"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
    {"col": "OCF_Volatility", "label": "OCF Volatility"},
    {"col": "Volatility", "label": "Stock Volatility"},
]


def parse_arguments():
    parser = argparse.ArgumentParser(description="Stage 4: Test H7 Illiquidity (call-level)")
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
            root_path / "outputs" / "variables" / "h7_illiquidity",
            required_file="h7_illiquidity_panel.parquet",
        )
        panel_file = panel_dir / "h7_illiquidity_panel.parquet"
    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    columns = [
        "gvkey", "year", "fyearq_int", "ff12_code",
        "delta_amihud", "pre_call_amihud",
        "CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct",
        "Manager_QA_Uncertainty_pct", "Manager_Pres_Uncertainty_pct",
        "CEO_Clarity_Residual", "Manager_Clarity_Residual",
        "Size", "TobinsQ", "ROA", "Lev", "CapexAt",
        "DividendPayer", "OCF_Volatility",
        "Volatility", "StockPrice", "Turnover",
        "Analyst_QA_Uncertainty_pct",
    ]
    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}  |  Columns: {len(panel.columns)}")
    return panel


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample filter: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(panel: pd.DataFrame, spec: Dict[str, Any]) -> pd.DataFrame:
    dv = spec["dv"]
    controls = BASE_CONTROLS if spec["controls"] == "base" else EXTENDED_CONTROLS
    required = [dv] + KEY_IVS + controls + ["gvkey", "fyearq_int", "ff12_code"]
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
        print(f"  WARNING: Too few observations ({len(df_prepared)}), skipping")
        return None, {}

    exog = KEY_IVS + controls
    print(f"  FE: {'Industry(FF12) + FiscalYear' if fe_type == 'industry' else 'Firm + FiscalYear'}")
    print(f"  N calls: {len(df_prepared):,}  |  N firms: {df_prepared['gvkey'].nunique():,}")
    print("  Estimating with firm-clustered SEs via PanelOLS...")
    t0 = datetime.now()

    df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])

    try:
        if fe_type == "industry":
            model_obj = PanelOLS(
                dependent=df_panel[dv], exog=df_panel[exog],
                entity_effects=False, time_effects=True,
                other_effects=df_panel["ff12_code"],
                drop_absorbed=True, check_rank=False,
            )
            model = model_obj.fit(cov_type="clustered", cluster_entity=True)
        else:
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

    meta: Dict[str, Any] = {
        "col": col_num, "dv": dv, "fe": fe_type, "controls": spec["controls"],
        "n_obs": int(model.nobs), "n_firms": df_prepared["gvkey"].nunique(),
        "within_r2": float(model.rsquared_within),
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


def _save_latex_table(all_results, out_dir):
    results_by_col = {r["meta"]["col"]: r["meta"] for r in all_results if r.get("meta")}
    n_cols = 4

    def fmt_coef(v, s): return "" if np.isnan(v) else f"{v:.4f}{s}"
    def fmt_se(v): return "" if np.isnan(v) else f"({v:.4f})"
    def fmt_int(v): return f"{v:,}"
    def fmt_r2(v): return "" if np.isnan(v) else f"{v:.3f}"

    lines = [
        r"\begin{table}[htbp]", r"\centering",
        r"\caption{Speech Uncertainty and Post-Call Illiquidity}",
        r"\label{tab:h7_illiquidity}", r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}", r"\toprule",
    ]
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")
    lines.append(r" & \multicolumn{4}{c}{$\Delta$Amihud Illiquidity} \\")
    lines.append(r"\cmidrule(lr){2-5}")
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
    ind = ["Yes" if results_by_col.get(c, {}).get("fe") == "industry" else "" for c in range(1, n_cols + 1)]
    firm = ["Yes" if results_by_col.get(c, {}).get("fe") == "firm" else "" for c in range(1, n_cols + 1)]
    lines.append(r"Industry FE & " + " & ".join(ind) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm) + r" \\")
    lines.append(r"Fiscal Year FE & " + " & ".join(["Yes"] * n_cols) + r" \\")
    lines.append(r"\midrule")
    ns = [fmt_int(results_by_col.get(c, {}).get("n_obs", 0)) for c in range(1, n_cols + 1)]
    lines.append(r"N & " + " & ".join(ns) + r" \\")
    r2s = [fmt_r2(results_by_col.get(c, {}).get("within_r2", np.nan)) for c in range(1, n_cols + 1)]
    lines.append(r"Within-R$^2$ & " + " & ".join(r2s) + r" \\")

    lines += [
        r"\bottomrule", r"\end{tabular}",
        r"\begin{minipage}{\linewidth}", r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed; H7: $\beta > 0$). ",
        r"Standard errors (in parentheses) clustered at firm level. ",
        r"Main sample (excludes financial and utility firms). ",
        r"$\Delta$Amihud = post-call ([+1,+3] days) minus pre-call ([-3,-1] days) Amihud illiquidity. ",
        r"Industry FE uses Fama-French 12 industry dummies. ",
        r"Time FE uses fiscal year (\texttt{fyearq\_int}). ",
        r"Variables winsorized at 1\%/99\% by year at engine level. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}", r"\end{table}",
    ]
    with open(out_dir / "h7_illiquidity_table.tex", "w", encoding="utf-8") as f:
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
            f.write("=" * 60 + "\n\n" + str(model.summary))
        print(f"  Saved: regression_results_col{col_num}.txt")

    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False)
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} regressions)")
    _save_latex_table(all_results, out_dir)
    return diag_df


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h7_illiquidity" / timestamp
    log_dir = setup_run_logging(log_base_dir=root / "logs", suite_name="H7_Illiquidity", timestamp=timestamp)

    print("=" * 80)
    print("STAGE 4: Test H7 Post-Call Illiquidity Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Sample:    Main only (FF12 != 8, 11)")
    print(f"IVs:       {len(KEY_IVS)} (all simultaneous)")
    print(f"Specs:     {len(MODEL_SPECS)} model columns")
    print(f"Time FE:   fyearq_int (fiscal year)")
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
    print(f"  delta_amihud non-null: {panel['delta_amihud'].notna().sum():,}")
    for iv in KEY_IVS:
        n_valid = panel[iv].notna().sum()
        print(f"  {iv}: {n_valid:,} ({100.0 * n_valid / main_panel_n:.1f}%)")

    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv", output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics -- H7 Illiquidity (Main Sample)",
        label="tab:summary_stats_h7",
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

    if all_results:
        first_meta = all_results[0].get("meta", {})
        generate_attrition_table([
            ("Full panel", full_panel_n),
            ("Main sample", main_panel_n),
            ("delta_amihud non-null", panel["delta_amihud"].notna().sum()),
            ("Complete-case + min-calls (col 1)", first_meta.get("n_obs", 0)),
        ], out_dir, "H7 Illiquidity")

    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv",
                      "table": out_dir / "h7_illiquidity_table.tex"},
        panel_path=panel_file,
    )

    duration = (datetime.now() - start_time).total_seconds()
    with open(out_dir / "report_step4_H7.md", "w", encoding="utf-8") as f:
        f.write(f"# H7 Illiquidity Report\n\n**Duration:** {duration:.1f}s\n**Sample:** Main only\n")
    print(f"  Saved: report_step4_H7.md")

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
