#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H12Q Quarterly Payout Ratio Hypothesis
================================================================================
ID: econometric/run_h12q_payout
Description: Run H12Q hypothesis test — quarterly PayoutRatio at call level.

DV: PayoutRatio_q = (dvpspq × cshoq) / ibq
    Quarterly payout ratio. NaN when ibq <= 0 (explicit negative earnings filter).

Lead DVs:
    PayoutRatio_q_lead_qtr: next fiscal quarter's PayoutRatio_q

8 Model Specifications:
    Cols 1-4:   DV = PayoutRatio_q (contemporaneous)
    Cols 5-8:   DV = PayoutRatio_q_lead_qtr (next quarter)
    Odd cols:   Industry FE (FF12) + Fiscal Year-Quarter FE
    Even cols:  Firm FE + Fiscal Year-Quarter FE
    Cols 1-2, 5-6:  Base controls
    Cols 3-4, 7-8:  Extended controls

Lead specs (cols 5-8) include PayoutRatio_q as lagged DV control.

Key IVs (4, simultaneous, call-level):
    CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct,
    Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct

Hypothesis: One-tailed (β < 0 — higher uncertainty → lower payout).

Sample: Main only (FF12 ≠ 8, 11).
SEs: Firm-clustered.
FE time: Fiscal year (fyearq_int), consistent with other suites.

Known limitation: ~57% of firm-quarters with ibq > 0 have PayoutRatio_q = 0
(dividend lumpiness). OLS with continuous DV; documented as limitation.

Inputs:
    - outputs/variables/h12q_payout/latest/h12q_payout_panel.parquet

Outputs:
    - outputs/econometric/h12q_payout/{timestamp}/...

Author: Thesis Author
Date: 2026-03-21
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
]

BASE_CONTROLS = [
    "Size", "TobinsQ", "ROA", "BookLev", "CashHoldings",
    "CapexAt", "OCF_Volatility",
]

EXTENDED_CONTROLS = BASE_CONTROLS + [
    "SalesGrowth", "RD_Intensity", "CashFlow", "Volatility",
]

MIN_CALLS_PER_FIRM = 5

MODEL_SPECS = [
    # Contemporaneous
    {"col": 1,  "dv": "PayoutRatio_q",          "fe": "industry", "controls": "base",     "extra_controls": []},
    {"col": 2,  "dv": "PayoutRatio_q",          "fe": "firm",     "controls": "base",     "extra_controls": []},
    {"col": 3,  "dv": "PayoutRatio_q",          "fe": "industry", "controls": "extended", "extra_controls": []},
    {"col": 4,  "dv": "PayoutRatio_q",          "fe": "firm",     "controls": "extended", "extra_controls": []},
    # Lead: next quarter
    {"col": 5,  "dv": "PayoutRatio_q_lead_qtr", "fe": "industry", "controls": "base",     "extra_controls": ["PayoutRatio_q"]},
    {"col": 6,  "dv": "PayoutRatio_q_lead_qtr", "fe": "firm",     "controls": "base",     "extra_controls": ["PayoutRatio_q"]},
    {"col": 7,  "dv": "PayoutRatio_q_lead_qtr", "fe": "industry", "controls": "extended", "extra_controls": ["PayoutRatio_q"]},
    {"col": 8,  "dv": "PayoutRatio_q_lead_qtr", "fe": "firm",     "controls": "extended", "extra_controls": ["PayoutRatio_q"]},
]

VARIABLE_LABELS = {
    "CEO_QA_Uncertainty_pct": "CEO QA Uncertainty",
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
    "Manager_QA_Uncertainty_pct": "Mgr QA Uncertainty",
    "Manager_Pres_Uncertainty_pct": "Mgr Pres Uncertainty",
}

SUMMARY_STATS_VARS = [
    {"col": "PayoutRatio_q", "label": "PayoutRatio$_q$ (quarterly)"},
    {"col": "PayoutRatio_q_lead_qtr", "label": "PayoutRatio$_q$ (next quarter)"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "BookLev", "label": "Leverage"},
    {"col": "CashHoldings", "label": "Cash Holdings"},
    {"col": "CapexAt", "label": "CapEx / Assets"},
    {"col": "OCF_Volatility", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RD_Intensity", "label": "R\\&D Intensity"},
    {"col": "CashFlow", "label": "Cash Flow"},
    {"col": "Volatility", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H12Q Quarterly Payout Ratio (call-level)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load call-level H12Q panel."""
    print("\n" + "=" * 60)
    print("Loading H12Q panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h12q_payout",
            required_file="h12q_payout_panel.parquet",
        )
        panel_file = panel_dir / "h12q_payout_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}, Columns: {len(panel.columns)}")
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
    extra_controls = spec["extra_controls"]
    controls = (BASE_CONTROLS if ctrl_key == "base" else EXTENDED_CONTROLS) + extra_controls
    required = [dv] + KEY_IVS + controls + ["gvkey", "fyearq_int", "ff12_code"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Drop NaN in DV (includes ibq <= 0 cases)
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
    """Run PanelOLS with calendar year-quarter FE and firm-clustered SEs."""
    col_num = spec["col"]
    dv = spec["dv"]
    fe_type = spec["fe"]
    ctrl_key = spec["controls"]
    extra_controls = spec["extra_controls"]
    controls = (BASE_CONTROLS if ctrl_key == "base" else EXTENDED_CONTROLS) + extra_controls

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_type}+YQ | Controls={ctrl_key}")
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

    # Set panel index: gvkey × calendar year-quarter
    df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])

    try:
        if fe_type == "industry":
            model_obj = PanelOLS(
                dependent=df_panel[dv],
                exog=df_panel[exog],
                entity_effects=False,
                time_effects=True,  # absorbs fyearq_int FE
                other_effects=df_panel["ff12_code"],
                drop_absorbed=True,
                check_rank=False,
            )
            model = model_obj.fit(cov_type="clustered", cluster_entity=True)
        else:
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
            model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"  [OK] {elapsed:.1f}s | R2w={model.rsquared_within:.4f}")

    # Build metadata with per-IV one-tailed p-values (H12: β < 0)
    meta: Dict[str, Any] = {
        "col": col_num,
        "dv": dv,
        "fe": fe_type,
        "controls": ctrl_key,
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "within_r2": float(model.rsquared_within),
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
    }

    for iv in KEY_IVS:
        beta = float(model.params.get(iv, np.nan))
        se = float(model.std_errors.get(iv, np.nan))
        p_two = float(model.pvalues.get(iv, np.nan))

        # One-tailed: H12 expects β < 0
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
    """Write 12-column LaTeX table (3 panels of 4 columns)."""
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    def fmt_coef(val, stars):
        return f"{val:.4f}{stars}" if not np.isnan(val) else ""

    def fmt_se(val):
        return f"({val:.4f})" if not np.isnan(val) else ""

    def fmt_r2(val):
        if np.isnan(val):
            return ""
        return f"{val:.2e}" if abs(val) < 0.001 else f"{val:.3f}"

    def _panel_lines(cols, panel_label, dv_label):
        lines = []
        lines.append(f"\\multicolumn{{{len(cols)+1}}}{{l}}{{\\textit{{{panel_label}: {dv_label}}}}} \\\\")
        lines.append("\\midrule")
        col_nums = " & ".join(f"({c})" for c in cols)
        lines.append(f" & {col_nums} \\\\")
        lines.append("\\midrule")

        for iv in KEY_IVS:
            label = VARIABLE_LABELS.get(iv, iv)
            coefs = " & ".join(
                fmt_coef(results_by_col.get(c, {}).get(f"{iv}_beta", np.nan),
                         _sig_stars(results_by_col.get(c, {}).get(f"{iv}_p_one", np.nan)))
                for c in cols
            )
            ses = " & ".join(
                fmt_se(results_by_col.get(c, {}).get(f"{iv}_se", np.nan))
                for c in cols
            )
            lines.append(f"{label} & {coefs} \\\\")
            lines.append(f" & {ses} \\\\")

        lines.append("\\midrule")

        ctrl_cells = " & ".join(
            "Extended" if results_by_col.get(c, {}).get("controls") == "extended" else "Base"
            for c in cols
        )
        ind_cells = " & ".join(
            "Yes" if results_by_col.get(c, {}).get("fe") == "industry" else ""
            for c in cols
        )
        firm_cells = " & ".join(
            "Yes" if results_by_col.get(c, {}).get("fe") == "firm" else ""
            for c in cols
        )
        lines.append(f"Controls & {ctrl_cells} \\\\")
        lines.append(f"Industry FE & {ind_cells} \\\\")
        lines.append(f"Firm FE & {firm_cells} \\\\")
        lines.append(f"Year-Quarter FE & " + " & ".join(["Yes"] * len(cols)) + " \\\\")

        # Lagged DV indicator
        has_lag = any(results_by_col.get(c, {}).get("extra_controls", "") for c in cols)
        if has_lag:
            lag_cells = " & ".join(
                "Yes" if results_by_col.get(c, {}).get("extra_controls", "") else ""
                for c in cols
            )
            lines.append(f"Lagged DV & {lag_cells} \\\\")

        lines.append("\\midrule")
        n_cells = " & ".join(f"{results_by_col.get(c, {}).get('n_obs', 0):,}" for c in cols)
        r2_cells = " & ".join(fmt_r2(results_by_col.get(c, {}).get("within_r2", np.nan)) for c in cols)
        lines.append(f"N & {n_cells} \\\\")
        lines.append(f"Within-R$^2$ & {r2_cells} \\\\")

        return lines

    n_cols = 4
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Speech Uncertainty and Quarterly Payout Ratio}",
        r"\label{tab:h12q_payout}",
        r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}",
        r"\toprule",
    ]

    lines += _panel_lines([1, 2, 3, 4], "Panel A", "PayoutRatio$_q$ (contemporaneous)")
    lines.append("\\midrule")
    lines += _panel_lines([5, 6, 7, 8], "Panel B", "PayoutRatio$_q$ (next quarter)")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed; $\beta < 0$). ",
        r"Standard errors (in parentheses) clustered at firm level. ",
        r"PayoutRatio$_q$ = (dvpspq $\times$ cshoq) / ibq; NaN when ibq $\leq$ 0. ",
        r"Main sample (excludes financial and utility firms). ",
        r"~57\% of firm-quarters with positive earnings have PayoutRatio$_q$ = 0 (dividend lumpiness). ",
        r"Lead specs (Panels B, C) include PayoutRatio$_q$ as lagged DV control. ",
        r"Year-quarter FE absorbs calendar year $\times$ quarter effects. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h12q_payout_table.tex"
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
            f.write(f"H12Q Quarterly Payout Ratio Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"FE: {meta['fe']} + Year-Quarter\n")
            f.write(f"Controls: {meta['controls']}\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
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
    out_dir = root / "outputs" / "econometric" / "h12q_payout" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H12Q_Payout",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H12Q Quarterly Payout Ratio")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    4 IVs × 3 DVs × 2 FE × 2 controls = 12 models")
    print(f"FE time:   Calendar year-quarter")

    panel, panel_file = load_panel(root, panel_path)

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    # Report negative earnings filter
    n_dv_valid = panel["PayoutRatio_q"].notna().sum()
    n_dv_zero = (panel["PayoutRatio_q"] == 0).sum()
    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    print(f"  PayoutRatio_q non-null (ibq > 0): {n_dv_valid:,}")
    if n_dv_valid > 0:
        print(f"  PayoutRatio_q == 0 (no div this quarter): {n_dv_zero:,} "
              f"({100 * n_dv_zero / n_dv_valid:.1f}%)")
    print(f"  PayoutRatio_q_lead_qtr non-null: {panel['PayoutRatio_q_lead_qtr'].notna().sum():,}")

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H12Q Quarterly Payout Ratio (Main Sample)",
        label="tab:summary_stats_h12q",
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
            ("PayoutRatio_q non-null (ibq > 0)", n_dv_valid),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H12Q Quarterly Payout Ratio")
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
