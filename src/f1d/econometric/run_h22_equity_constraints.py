#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H22 Equity Financing Constraints Hypothesis
================================================================================
ID: econometric/run_h22_equity_constraints
Description: Run H22 hypothesis test — does speech uncertainty predict equity
             financing constraints?

DV: EquityDelayCon_lead = Hoberg & Maksimovic (2015) equity-specific financial
    constraint score from NEXT fiscal year's 10-K. Higher = more constrained.

4 Model Specifications:
    Cols 1-2:   DV = EquityDelayCon_lead, Calendar Year FE (Base / Extended)
    Cols 3-4:   DV = EquityDelayCon_lead, Calendar Year FE (Extended)
    Odd cols:   Industry FE (FF12)
    Even cols:  Firm FE
    Cols 1-2:   Base controls
    Cols 3-4:   Extended controls

Key IVs (4, simultaneous, fiscal-year averages):
    UncAnsCEO, UncPreCEO,
    UncAnsMgr, UncPreMgr

Hypothesis: One-tailed (beta > 0 — higher uncertainty -> more equity constraints).

Estimator: PanelOLS with firm or industry FE + fiscal year FE.
Unit of observation: firm-fiscal-year.

Sample: Main only (FF12 != 8, 11). Period: 2003-2014 (DV from 2004-2015).
SEs: Firm-clustered.
FE time: cal_yr (= fyearq_int, set in panel builder).

Inputs:
    - outputs/variables/h22_equity_constraints/latest/h22_equity_constraints_panel.parquet

Outputs:
    - outputs/econometric/h22_equity_constraints/{timestamp}/...

Reference: Hoberg, G. & Maksimovic, V. (2015). Redefining Financial Constraints:
           A Text-Based Analysis. Review of Financial Studies, 28(5), 1312-1352.

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
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir


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
    "lnAssets", "TobinsQ", "ROA", "Leverage", "Capex",
    "CashRatio", "DivDummy", "sCFO",
    "Lagged_DV",
]

EXTENDED_CONTROLS = BASE_CONTROLS + [
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
]

MIN_FIRM_YEARS = 5

MODEL_SPECS = [
    # EquityDelayCon_lead — Calendar Year FE (= fyearq_int, B1 fix)
    {"col": 1, "dv": "EquityDelayCon_lead", "fe": "industry",  "controls": "base",     "extra_controls": []},
    {"col": 2, "dv": "EquityDelayCon_lead", "fe": "firm",      "controls": "base",     "extra_controls": []},
    {"col": 3, "dv": "EquityDelayCon_lead", "fe": "industry",  "controls": "extended", "extra_controls": []},
    {"col": 4, "dv": "EquityDelayCon_lead", "fe": "firm",      "controls": "extended", "extra_controls": []},
]

VARIABLE_LABELS = {
    "UncAnsCEO": "CEO QA Uncertainty",
    "UncPreCEO": "CEO Pres Uncertainty",
    "UncAnsMgr": "Mgr QA Uncertainty",
    "UncPreMgr": "Mgr Pres Uncertainty",
}

SUMMARY_STATS_VARS = [
    {"col": "EquityDelayCon_lead", "label": "Equity Constraint (lead)"},
    {"col": "equitydelaycon", "label": "Equity Constraint (contemp.)"},
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
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "sCFO", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RDSales", "label": r"R\&D Intensity"},
    {"col": "CashFlowAt", "label": "Cash Flow"},
    {"col": "DailyVola", "label": "Stock Volatility"},
    {"col": "n_calls_in_year", "label": "Calls per Firm-Year"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H22 Equity Constraints (firm-year)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load firm-year H22 panel."""
    print("\n" + "=" * 60)
    print("Loading H22 panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h22_equity_constraints",
            required_file="h22_equity_constraints_panel.parquet",
        )
        panel_file = panel_dir / "h22_equity_constraints_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}, Columns: {len(panel.columns)}")
    print(f"  Unique firms: {panel['gvkey'].nunique():,}")
    print(f"  Fiscal year range: {panel['fyearq_int'].min()}-{panel['fyearq_int'].max()}")

    # Verify cal_yr == fyearq_int (B1 fix validation)
    if "cal_yr" in panel.columns:
        mismatches = (panel["cal_yr"] != panel["fyearq_int"]).sum()
        if mismatches > 0:
            raise ValueError(
                f"cal_yr != fyearq_int for {mismatches} rows. "
                "Panel builder B1 fix was not applied correctly."
            )
    else:
        panel["cal_yr"] = panel["fyearq_int"]
        print("  WARNING: cal_yr not in panel, set to fyearq_int")

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

    # Create Lagged_DV from EquityDelayCon_lag
    panel = panel.copy()
    panel["Lagged_DV"] = panel["EquityDelayCon_lag"]

    required = [dv] + KEY_IVS + controls + ["gvkey", "cal_yr", "ff12_code"]

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

    # Min firm-years per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_FIRM_YEARS].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()
    print(f"  After >={MIN_FIRM_YEARS} firm-years/firm: "
          f"{len(df):,} obs, {df['gvkey'].nunique():,} firms")

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS with FE and firm-clustered SEs."""
    col_num = spec["col"]
    dv = spec["dv"]
    fe_type = spec["fe"]
    ctrl_key = spec["controls"]
    extra_controls = spec["extra_controls"]
    controls = (BASE_CONTROLS if ctrl_key == "base" else EXTENDED_CONTROLS) + extra_controls

    # Annual panel: always use cal_yr (= fyearq_int) as time index
    time_col = "cal_yr"
    fe_label = f"{'Industry(FF12)' if fe_type == 'industry' else 'Firm'} + FiscalYear"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_label} | Controls={ctrl_key}")
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
        if fe_type == "industry":
            model_obj = PanelOLS(
                dependent=df_panel[dv],
                exog=df_panel[exog],
                entity_effects=False,
                time_effects=True,
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
    adj_r2 = 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid
    print(f"  R-squared: {model.rsquared:.4f}  Adj R-squared: {adj_r2:.4f}  ({elapsed:.1f}s)")

    # DV mean in regression sample
    dv_mean = float(df_prepared[dv].mean())

    meta: Dict[str, Any] = {
        "col": col_num,
        "dv": dv,
        "fe": fe_type,
        "controls": ctrl_key,
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "r2": float(model.rsquared),
        "adj_r2": adj_r2,
        "dv_mean": dv_mean,
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
    }

    for iv in KEY_IVS:
        beta = float(model.params.get(iv, np.nan))
        se = float(model.std_errors.get(iv, np.nan))
        p_two = float(model.pvalues.get(iv, np.nan))

        # One-tailed: H22 expects beta > 0
        if not np.isnan(p_two) and not np.isnan(beta):
            p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
        else:
            p_one = np.nan

        meta[f"{iv}_beta"] = beta
        meta[f"{iv}_se"] = se
        meta[f"{iv}_p_one"] = p_one

        stars = _sig_stars(p_one)
        print(f"  {VARIABLE_LABELS.get(iv, iv)}: b={beta:.6f} p1={p_one:.4f} {stars}")

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
    """Write unified 4-column LaTeX table."""
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    n_cols = 4

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
        r"\caption{Speech Uncertainty and Equity Financing Constraints}",
        r"\label{tab:h22_equity_constraints}",
        r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}",
        r"\toprule",
    ]

    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")

    lines.append(
        r" & \multicolumn{4}{c}{EquityDelayCon\_lead} \\"
    )
    lines.append(r"\cmidrule(lr){2-5}")
    lines.append(r"\midrule")

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

    ctrl_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        ctrl_cells.append("Extended" if meta.get("controls") == "extended" else "Base")
    lines.append(r"Controls & " + " & ".join(ctrl_cells) + r" \\")

    lines.append(r"Lagged DV & " + " & ".join(["Yes"] * n_cols) + r" \\")

    ind_fe_cells, firm_fe_cells, year_fe_cells = [], [], []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        fe = meta.get("fe", "")
        ind_fe_cells.append("Yes" if fe == "industry" else "")
        firm_fe_cells.append("Yes" if fe == "firm" else "")
        year_fe_cells.append("Yes")
    lines.append(r"Industry FE & " + " & ".join(ind_fe_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_fe_cells) + r" \\")
    lines.append(r"Fiscal Year FE & " + " & ".join(year_fe_cells) + r" \\")

    lines.append(r"\midrule")

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
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed; $\beta > 0$). ",
        r"Standard errors (in parentheses) clustered at firm level. ",
        r"DV is Hoberg \& Maksimovic (2015) equity-specific financial constraint score ",
        r"from next fiscal year's 10-K (higher = more equity-constrained). ",
        r"IVs are fiscal-year averages of call-level uncertainty measures. ",
        r"Unit of observation: firm-fiscal-year. ",
        r"Main sample (excludes financial and utility firms).",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h22_equity_constraints_table.tex"
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
            f.write(f"H22 Equity Financing Constraints Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Controls: {meta['controls']}\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
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


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h22_equity_constraints" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H22_EquityConstraints",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H22 Equity Financing Constraints")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    4 IVs x 1 DV x 2 FE x 2 controls = 4 models")
    print(f"FE time:   cal_yr (= fyearq_int, fiscal year)")
    print(f"Unit:      firm-fiscal-year")

    panel, panel_file = load_panel(root, panel_path)

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    n_dv_valid = panel["EquityDelayCon_lead"].notna().sum()
    print(f"\n  Main sample: {main_n:,} firm-years, {panel['gvkey'].nunique():,} firms")
    print(f"  EquityDelayCon_lead non-null: {n_dv_valid:,}")

    # Summary statistics
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H22 Equity Constraints (Main Sample)",
        label="tab:summary_stats_h22",
    )
    print("  Saved: summary_stats.csv/.tex")

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

    diag_df = save_outputs(all_results, out_dir)

    if all_results:
        first = all_results[0]["meta"]
        attrition_stages = [
            ("Full panel (all firm-years)", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("EquityDelayCon_lead non-null", n_dv_valid),
            ("After complete-case + min-firm-years (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H22 Equity Constraints")
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

    for iv in KEY_IVS:
        sig_count = sum(
            1 for r in all_results
            if r["meta"].get(f"{iv}_p_one", 1.0) < 0.05
            and r["meta"].get(f"{iv}_beta", 0) > 0
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
