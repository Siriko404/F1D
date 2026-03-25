#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H5b Johnson (2004) Analyst Dispersion Hypothesis
================================================================================
ID: econometric/run_h5b_johnson_disp
Description: Run H5b hypothesis test — Johnson (2004) analyst forecast dispersion.

DV: JohnsonDISP2 = SD(current-FY analyst forecasts at month-end) / atq
    Price-scaled pre-announcement analyst forecast dispersion.
    Reference: Johnson (2020, Review of Accounting and Finance 19(3): 289-312).

Lead DV:
    JohnsonDISP2_lead: next fiscal quarter's JohnsonDISP2

8 Model Specifications:
    Cols 1-4:   DV = JohnsonDISP2 (contemporaneous)
    Cols 5-8:   DV = JohnsonDISP2_lead (next quarter)
    Odd cols:   Industry FE (FF12) + Fiscal Year FE
    Even cols:  Firm FE + Fiscal Year FE
    Cols 1-2, 5-6:  Base controls
    Cols 3-4, 7-8:  Extended controls

Lead specs (cols 5-8) include JohnsonDISP2 as lagged DV control.

Key IVs (4, simultaneous, call-level):
    CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct,
    Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct

Hypothesis: One-tailed (beta > 0 — higher uncertainty -> higher dispersion).

Sample: Main only (FF12 != 8, 11).
SEs: Firm-clustered.
FE time: fyearq_int (fiscal year).
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
    "Size", "TobinsQ", "ROA", "BookLev", "CapexAt", "DividendPayer",
    "OCF_Volatility", "JohnsonDISP2_lag",
]

EXTENDED_CONTROLS = BASE_CONTROLS + [
    "SurpDec", "loss_dummy", "Analyst_QA_Uncertainty_pct",
    "Entire_All_Negative_pct",
]

MIN_CALLS_PER_FIRM = 5

MODEL_SPECS = [
    # Contemporaneous
    {"col": 1, "dv": "JohnsonDISP2",      "fe": "industry", "controls": "base",     "extra_controls": []},
    {"col": 2, "dv": "JohnsonDISP2",      "fe": "firm",     "controls": "base",     "extra_controls": []},
    {"col": 3, "dv": "JohnsonDISP2",      "fe": "industry", "controls": "extended", "extra_controls": []},
    {"col": 4, "dv": "JohnsonDISP2",      "fe": "firm",     "controls": "extended", "extra_controls": []},
    # Lead: next quarter
    {"col": 5, "dv": "JohnsonDISP2_lead", "fe": "industry", "controls": "base",     "extra_controls": ["JohnsonDISP2"]},
    {"col": 6, "dv": "JohnsonDISP2_lead", "fe": "firm",     "controls": "base",     "extra_controls": ["JohnsonDISP2"]},
    {"col": 7, "dv": "JohnsonDISP2_lead", "fe": "industry", "controls": "extended", "extra_controls": ["JohnsonDISP2"]},
    {"col": 8, "dv": "JohnsonDISP2_lead", "fe": "firm",     "controls": "extended", "extra_controls": ["JohnsonDISP2"]},
]

SUMMARY_STATS_VARS = [
    {"col": "JohnsonDISP2", "label": "Johnson DISP2 (contemporaneous)"},
    {"col": "JohnsonDISP2_lead", "label": "Johnson DISP2 (next quarter)"},
    {"col": "JohnsonDISP2_lag", "label": "Johnson DISP2 (prior quarter)"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "Size", "label": "Firm Size"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "BookLev", "label": "Leverage"},
    {"col": "CapexAt", "label": "CapEx/Assets"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
    {"col": "OCF_Volatility", "label": "OCF Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H5b Johnson (2004) Analyst Dispersion Test",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load the H5b panel from Stage 3 output."""
    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root / "outputs" / "variables" / "h5b_johnson_disp",
            required_file="h5b_johnson_disp_panel.parquet",
        )
        panel_file = panel_dir / "h5b_johnson_disp_panel.parquet"

    # Determine required columns
    all_dvs = list({s["dv"] for s in MODEL_SPECS})
    all_extra = list({c for s in MODEL_SPECS for c in s.get("extra_controls", [])})
    columns = list(set(
        all_dvs + KEY_IVS + EXTENDED_CONTROLS + all_extra
        + ["gvkey", "fyearq_int", "ff12_code", "start_date", "file_name"]
    ))

    panel = pd.read_parquet(panel_file, columns=[c for c in columns if c != "start_date"] + ["start_date"])
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    return panel


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only (exclude Finance ff12=11, Utility ff12=8)."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(panel: pd.DataFrame, spec: Dict[str, Any]) -> pd.DataFrame:
    """Prepare panel for a specific model specification."""
    dv = spec["dv"]
    controls = BASE_CONTROLS if spec["controls"] == "base" else EXTENDED_CONTROLS
    extra = spec.get("extra_controls", [])
    all_controls = controls + extra
    required = [dv] + KEY_IVS + all_controls + ["gvkey", "fyearq_int", "ff12_code"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

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
# Regression
# ==============================================================================


def run_regression(
    df_prepared: pd.DataFrame,
    spec: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS regression for a given model specification."""
    col_num = spec["col"]
    dv = spec["dv"]
    fe_type = spec["fe"]
    controls = BASE_CONTROLS if spec["controls"] == "base" else EXTENDED_CONTROLS
    extra = spec.get("extra_controls", [])
    all_controls = controls + extra

    print(f"\n" + "=" * 60)
    print(f"Col ({col_num}) | DV={dv} | FE={fe_type} | Controls={spec['controls']}")
    print("=" * 60)

    if len(df_prepared) < 100:
        print(f"  WARNING: Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    exog = KEY_IVS + all_controls

    print(f"  N calls: {len(df_prepared):,}  |  N firms: {df_prepared['gvkey'].nunique():,}")
    t0 = datetime.now()

    df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])

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
    print(f"  [OK] {elapsed:.1f}s | Within-R²: {model.rsquared_within:.4f} | N: {int(model.nobs):,}")

    meta: Dict[str, Any] = {
        "col": col_num, "dv": dv, "fe": fe_type, "controls": spec["controls"],
        "n_obs": int(model.nobs), "n_firms": df_prepared["gvkey"].nunique(),
        "within_r2": float(model.rsquared_within),
    }

    for iv in KEY_IVS:
        beta = float(model.params.get(iv, np.nan))
        se = float(model.std_errors.get(iv, np.nan))
        p_two = float(model.pvalues.get(iv, np.nan))
        p_one = p_two / 2 if (not np.isnan(p_two) and beta > 0) else (1 - p_two / 2 if not np.isnan(p_two) else np.nan)
        meta[f"{iv}_beta"] = beta
        meta[f"{iv}_se"] = se
        meta[f"{iv}_p_one"] = p_one
        stars = "***" if p_one < 0.01 else "**" if p_one < 0.05 else "*" if p_one < 0.10 else ""
        print(f"  {iv}: b={beta:.4f} p1={p_one:.4f} {stars}")

    return model, meta


# ==============================================================================
# Output
# ==============================================================================


def save_outputs(all_results: List[Dict[str, Any]], out_dir: Path) -> pd.DataFrame:
    """Save regression outputs."""
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
        fpath = out_dir / fname
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"H5b Johnson Dispersion Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"FE: {'industry' if meta['fe'] == 'industry' else 'firm'} + Fiscal Year\n")
            f.write(f"Controls: {meta['controls']}\n")
            extra = [c for c in meta.get("extra_controls", []) if c]
            if extra:
                f.write(f"Extra controls: {', '.join(extra)}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    return diag_df


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h5b_johnson_disp" / timestamp

    setup_run_logging(log_base_dir=root / "logs", suite_name="H5b_JohnsonDisp", timestamp=timestamp)

    print("=" * 80)
    print("STAGE 4: Test H5b Johnson (2004) Analyst Dispersion Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Specs:     {len(MODEL_SPECS)} models")
    print(f"Test:      One-tailed (beta > 0)")

    panel = load_panel(root, panel_path)

    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "h5b_johnson_disp",
        required_file="h5b_johnson_disp_panel.parquet",
    ) / "h5b_johnson_disp_panel.parquet"

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    print(f"\n  JohnsonDISP2 non-null: {panel['JohnsonDISP2'].notna().sum():,}")
    print(f"  JohnsonDISP2_lead non-null: {panel['JohnsonDISP2_lead'].notna().sum():,}")
    print(f"  JohnsonDISP2_lag non-null: {panel['JohnsonDISP2_lag'].notna().sum():,}")

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H5b Johnson Dispersion (Main Sample)",
        label="tab:summary_stats_h5b",
    )

    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        try:
            df_prepared = prepare_regression_data(panel, spec)
        except ValueError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue

        if len(df_prepared) < 100:
            print(f"  Skipping col {spec['col']}: too few obs")
            continue

        model, meta = run_regression(df_prepared, spec)
        if model is not None and meta:
            all_results.append({"model": model, "meta": meta})

    diag_df = save_outputs(all_results, out_dir)

    # Attrition
    if all_results:
        first_n = all_results[0]["meta"].get("n_obs", 0)
        stages = [
            ("Full panel", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("JohnsonDISP2 non-null", panel["JohnsonDISP2"].notna().sum()),
            ("After complete-case + min-calls (col 1)", first_n),
        ]
        generate_attrition_table(stages, out_dir, "H5b Johnson Dispersion")

    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
        panel_path=panel_file,
    )

    duration = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")

    for iv in KEY_IVS:
        sig = sum(1 for r in all_results
                  if r["meta"].get(f"{iv}_p_one", 1.0) < 0.05 and r["meta"].get(f"{iv}_beta", 0) > 0)
        print(f"  {iv}: {sig}/{len(all_results)} significant (p<0.05, one-tail)")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run OK")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
