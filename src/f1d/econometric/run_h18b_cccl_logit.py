#!/usr/bin/env python3
"""
================================================================================
STAGE 4: H18b Logit Robustness — SEC Comment Letter Receipt
================================================================================
ID: econometric/run_h18b_cccl_logit
Description: Logit robustness check for H18. Same DV (CCCL binary), same IVs,
             same controls — replaces LPM (PanelOLS) with logistic regression
             via statsmodels to confirm LPM results hold under a nonlinear model.

DV: CCCL = 1 if firm received SEC comment letter between this call and the next.

2 Model Specifications (Industry FE only):
    Col 1: Industry FE (FF12) + Calendar Year FE + Base controls
    Col 2: Industry FE (FF12) + Calendar Year FE + Extended controls

Why only 2 columns (vs 6 in H18 LPM):
    - Firm FE infeasible: ~95% of firms have CCCL=0 for ALL observations,
      causing perfect separation. Incidental parameters problem (Neyman-Scott 1948).
    - Year-Quarter FE infeasible: 26 of 67 quarters have zero CCCL events,
      guaranteeing perfect separation on those quarter dummies.
    - Timoneda (2021) warns against logit-FE at base rates <5%.

Key IVs (4, simultaneous, call-level):
    UncAnsCEO, UncPreCEO,
    UncAnsMgr, UncPreMgr

Hypothesis: One-tailed (beta > 0 — higher uncertainty -> more SEC scrutiny).
Estimator: Logit via statsmodels with BFGS optimizer.
SEs: Firm-clustered (via cov_type='cluster').
FE: Industry (C(ff12_code)) + Calendar Year (C(cal_yr)) as formula dummies.

Inputs:
    - outputs/variables/h18_cccl_received/latest/h18_cccl_received_panel.parquet
      (same panel as H18 LPM — no new variable construction)

Outputs:
    - outputs/econometric/h18b_cccl_logit/{timestamp}/...

Author: Thesis Author
Date: 2026-03-31
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
import statsmodels.formula.api as smf

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index

# Silence convergence iteration output
warnings.filterwarnings("ignore", category=RuntimeWarning)


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

MIN_CALLS_PER_FIRM = 5

MODEL_SPECS = [
    {"col": 1, "dv": "CommentLetter", "controls": "base",     "fe_formula": "C(ff12_code) + C(cal_yr)"},
    {"col": 2, "dv": "CommentLetter", "controls": "extended",  "fe_formula": "C(ff12_code) + C(cal_yr)"},
]

VARIABLE_LABELS = {
    "UncAnsCEO": "CEO QA Uncertainty",
    "UncPreCEO": "CEO Pres Uncertainty",
    "UncAnsMgr": "Mgr QA Uncertainty",
    "UncPreMgr": "Mgr Pres Uncertainty",
}

SUMMARY_STATS_VARS = [
    {"col": "CommentLetter", "label": "CCCL (call-to-next-call)"},
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
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H18b CCCL Logit Robustness",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load call-level H18 panel (reused from H18 LPM)."""
    print("\n" + "=" * 60)
    print("Loading H18 panel (reused for logit robustness)")
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

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}, Columns: {len(panel.columns)}")

    panel = build_cal_yr_qtr_index(panel)

    return panel, panel_file


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only (exclude Finance and Utility)."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any],
) -> pd.DataFrame:
    """Prepare panel for a specific model specification.

    Replicates H18 LPM filtering EXACTLY to ensure identical samples.
    """
    dv = spec["dv"]
    ctrl_key = spec["controls"]
    controls = BASE_CONTROLS if ctrl_key == "base" else EXTENDED_CONTROLS

    panel = panel.copy()
    panel["Lagged_DV"] = panel["CCCL_lag"]

    required = [dv] + KEY_IVS + controls + ["gvkey", "fyearq_int", "ff12_code"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df = panel.replace([np.inf, -np.inf], np.nan)

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

    # Cast nullable dtypes for patsy compatibility
    for col in df.columns:
        if pd.api.types.is_extension_array_dtype(df[col]):
            df[col] = df[col].astype(float)
    df["cal_yr"] = df["cal_yr"].astype(int)
    df["ff12_code"] = df["ff12_code"].astype(int)

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_logit_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    """Run logit with industry + year FE dummies and firm-clustered SEs."""
    col_num = spec["col"]
    dv = spec["dv"]
    ctrl_key = spec["controls"]
    fe_formula = spec["fe_formula"]
    controls = BASE_CONTROLS if ctrl_key == "base" else EXTENDED_CONTROLS

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_formula} | Controls={ctrl_key}")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    n_firms = df_prepared["gvkey"].nunique()
    n_events = int(df_prepared[dv].sum())
    rhs = " + ".join(KEY_IVS + controls) + " + " + fe_formula
    formula = f"{dv} ~ {rhs}"

    print(f"  N={len(df_prepared):,}, firms={n_firms:,}, events={n_events}")

    # Warn about zero-event FE groups
    for fe_var in ["ff12_code", "cal_yr"]:
        cross = df_prepared.groupby(fe_var)[dv].sum()
        zero_groups = (cross == 0).sum()
        if zero_groups > 0:
            print(f"  WARNING: {zero_groups} {fe_var} groups with zero events")

    t0 = datetime.now()

    try:
        model = smf.logit(formula, data=df_prepared).fit(
            maxiter=300, disp=False, method="bfgs",
            cov_type="cluster", cov_kwds={"groups": df_prepared["gvkey"].values},
        )
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return None, {}

    converged = model.mle_retvals.get("converged", False)
    elapsed = (datetime.now() - t0).total_seconds()
    print(f"  Converged: {converged} ({elapsed:.1f}s)")
    print(f"  Pseudo R²: {model.prsquared:.6f}")
    print(f"  Log-likelihood: {model.llf:.2f}")

    if not converged:
        print("  WARNING: Model did not converge")

    meta: Dict[str, Any] = {
        "col": col_num,
        "dv": dv,
        "fe": "industry",
        "controls": ctrl_key,
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "n_events": n_events,
        "pseudo_r2": float(model.prsquared),
        "log_likelihood": float(model.llf),
        "converged": converged,
    }

    # Store log-odds for diagnostics
    for iv in KEY_IVS:
        meta[f"{iv}_logodds"] = float(model.params.get(iv, np.nan))
        meta[f"{iv}_logodds_se"] = float(model.bse.get(iv, np.nan))

    # Average Marginal Effects (AMEs) — primary coefficients for reporting
    try:
        mfx = model.get_margeff(at="overall")
        mfx_df = mfx.summary_frame()
        meta["_mfx_df"] = mfx_df  # store full AME frame for txt output

        for iv in KEY_IVS:
            if iv in mfx_df.index:
                ame = float(mfx_df.loc[iv, "dy/dx"])
                ame_se = float(mfx_df.loc[iv, "Std. Err."])
                ame_p_two = float(mfx_df.loc[iv, "Pr(>|z|)"])
            else:
                ame = ame_se = ame_p_two = np.nan

            # One-tailed: H18b expects beta > 0
            if not np.isnan(ame_p_two) and not np.isnan(ame):
                ame_p_one = ame_p_two / 2 if ame > 0 else 1 - ame_p_two / 2
            else:
                ame_p_one = np.nan

            meta[f"{iv}_beta"] = ame
            meta[f"{iv}_se"] = ame_se
            meta[f"{iv}_p_one"] = ame_p_one

            stars = _sig_stars(ame_p_one)
            print(f"  {VARIABLE_LABELS.get(iv, iv)}: AME={ame:+.6f} se={ame_se:.6f} p1={ame_p_one:.4f} {stars}")

        print("  AMEs computed successfully")
    except Exception as e:
        print(f"  ERROR: AME computation failed: {e}", file=sys.stderr)
        return None, {}

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


def save_outputs(all_results: List[Dict[str, Any]], out_dir: Path) -> pd.DataFrame:
    """Save all outputs with AME-based parameter tables for parse_txt compatibility."""
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
        mfx_df = meta.pop("_mfx_df", None)
        fname = f"regression_results_col{col_num}.txt"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            # Header lines for parse_txt
            f.write(f"H18b CCCL Logit Robustness — Average Marginal Effects\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Controls: {meta['controls']}\n")
            f.write(f"R-squared: {meta['pseudo_r2']:.10f}\n")
            f.write(f"Adj_R2: {meta['pseudo_r2']:.10f}\n")
            f.write(f"Estimator: Logit (Average Marginal Effects)\n")
            f.write(f"Converged: {meta['converged']}\n")
            f.write(f"Log-likelihood: {meta['log_likelihood']:.2f}\n")
            f.write("=" * 80 + "\n\n")

            # AME parameter table in parse_txt-compatible format
            f.write(f"No. Observations: {meta['n_obs']}\n\n")
            f.write(f"{'':=<80}\n")
            f.write(f"{'coef':>50}{'std err':>12}{'z':>10}{'P>|z|':>10}\n")
            f.write(f"{'':->80}\n")

            if mfx_df is not None:
                for var_name in mfx_df.index:
                    if var_name.startswith("C("):
                        continue
                    dy_dx = mfx_df.loc[var_name, "dy/dx"]
                    se = mfx_df.loc[var_name, "Std. Err."]
                    z = mfx_df.loc[var_name, "z"]
                    p = mfx_df.loc[var_name, "Pr(>|z|)"]
                    f.write(f"{var_name:<30} {dy_dx:>18.6f} {se:>11.6f} {z:>9.3f} {p:>9.4f}\n")

            f.write(f"{'':=<80}\n")

            # Append full logit summary and AME summary for reference
            f.write("\n\n--- Full Logit Summary (log-odds, for reference) ---\n\n")
            f.write(str(model.summary()))
            f.write("\n\n--- Full AME Summary ---\n\n")
            try:
                mfx = model.get_margeff(at="overall")
                f.write(str(mfx.summary()))
            except Exception:
                f.write("AME summary not available.\n")
        print(f"  Saved: {fname}")

    # Clean _mfx_df from remaining metas before CSV serialization
    diag_rows = []
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            clean = {k: v for k, v in meta.items() if not k.startswith("_")}
            diag_rows.append(clean)
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    # Marginal effects CSV
    ame_rows = []
    for r in all_results:
        meta = r.get("meta", {})
        if not meta:
            continue
        for iv in KEY_IVS:
            ame_rows.append({
                "col": meta["col"],
                "variable": iv,
                "ame": meta.get(f"{iv}_beta", np.nan),
                "ame_se": meta.get(f"{iv}_se", np.nan),
                "logit_logodds": meta.get(f"{iv}_logodds", np.nan),
                "logit_logodds_se": meta.get(f"{iv}_logodds_se", np.nan),
                "p_one": meta.get(f"{iv}_p_one", np.nan),
            })
    if ame_rows:
        pd.DataFrame(ame_rows).to_csv(
            out_dir / "marginal_effects.csv", index=False, float_format="%.10f"
        )
        print("  Saved: marginal_effects.csv")

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
    out_dir = root / "outputs" / "econometric" / "h18b_cccl_logit" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H18b_CCCL_Logit",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H18b CCCL Logit Robustness Check")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    4 IVs x 1 DV x 2 specs (Industry FE + Year FE)")
    print(f"Estimator: Logit (statsmodels) with firm-clustered SEs")

    panel, panel_file = load_panel(root, panel_path)

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    n_dv_valid = panel["CommentLetter"].notna().sum()
    n_dv1 = (panel["CommentLetter"] == 1).sum()
    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    print(f"  CCCL non-null: {n_dv_valid:,}")
    print(f"  CCCL=1: {n_dv1:,} ({100*n_dv1/n_dv_valid:.2f}%)")

    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H18b CCCL Logit (Main Sample)",
        label="tab:summary_stats_h18b",
    )
    print("  Saved: summary_stats.csv/.tex")

    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} "
              f"Controls={spec['controls']} ---")
        try:
            df_prepared = prepare_regression_data(panel, spec)
        except ValueError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue
        if len(df_prepared) < 100:
            print(f"  Skipping: too few obs")
            continue

        model, meta = run_logit_regression(df_prepared, spec)
        if model is not None and meta:
            all_results.append({"model": model, "meta": meta})

    diag_df = save_outputs(all_results, out_dir)

    if all_results:
        first = all_results[0]["meta"]
        attrition_stages = [
            ("Full panel", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("CCCL=1 in Main", n_dv1),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H18b CCCL Logit")
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
        print(f"  Estimator: Logit (statsmodels)")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
