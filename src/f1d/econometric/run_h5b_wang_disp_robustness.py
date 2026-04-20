#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H5 Wang (2020) Analyst Dispersion — ROBUSTNESS (Orthogonal Speaker Partition)
================================================================================
ID: econometric/run_h5b_wang_disp_robustness
Description: H5 robustness test that swaps the joint-IV stack from the all-manager
             pool (UncAnsMgr / UncPreMgr) — which definitionally NESTS UncAnsCEO /
             UncPreCEO since the all-manager pool includes CEO speakers — to a
             speaker-orthogonal partition: CEO + non-CEO managers. Identical 12-spec
             ladder, controls, FE, sample, and clustering as parent H5.

DV: DISP = SD(analyst forecasts T-31..T-1) / prccq_prior

Key IVs (4, speaker-orthogonal, all enter simultaneously):
    UncAnsCEO, UncAnsNoCEO,
    UncPreCEO, UncPreNoCEO

Hypothesis: One-tailed (beta > 0).
Sample: Main only (FF12 != 8, 11).
SEs: Firm-clustered.
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
from f1d.shared.outputs import (
    extract_coefs_panelols,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

KEY_IVS = [
    "UncAnsCEO",
    "UncAnsNoCEO",
    "UncPreCEO",
    "UncPreNoCEO",
]

BASE_CONTROLS = [
    "lnAssets", "TobinsQ", "ROA", "Leverage", "Capex", "DivDummy",
    "sCFO", "DISP_lag",
]

EXTENDED_CONTROLS = BASE_CONTROLS + [
    "SurpDec", "Loss", "UncQue",
    "NegCall",
]

EXTENDED_ONLY_CONTROLS = [c for c in EXTENDED_CONTROLS if c not in BASE_CONTROLS]

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission.
# ------------------------------------------------------------------
SUITE_ID = "H5.r"
SUITE_DIR_NAME = "h5b_wang_disp_robustness"
SUITE_TITLE = "Speech Uncertainty and Analyst Forecast Dispersion (Orthogonal Speaker Partition)"
SUITE_CAPTION = (
    "H5 Robustness: Orthogonal Speaker Partition"
)
SUITE_LABEL = "tab:h5_robust"
SAMPLE_LABEL = "Main sample (excludes financial and utility firms)."
HYP_DIR = "positive"  # H5: beta(uncertainty) > 0 — dispersion increases with speech uncertainty
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}

MIN_CALLS_PER_FIRM = 5

MODEL_SPECS = [
    # Contemporaneous — Calendar Year FE
    {"col": 1,  "dv": "DISP",      "fe": "industry",    "controls": "base",     "extra_controls": []},
    {"col": 2,  "dv": "DISP",      "fe": "firm",        "controls": "base",     "extra_controls": []},
    {"col": 3,  "dv": "DISP",      "fe": "industry",    "controls": "extended", "extra_controls": []},
    {"col": 4,  "dv": "DISP",      "fe": "firm",        "controls": "extended", "extra_controls": []},
    # Contemporaneous — Year-Quarter FE (Extended controls only)
    {"col": 5,  "dv": "DISP",      "fe": "industry_yq", "controls": "extended", "extra_controls": []},
    {"col": 6,  "dv": "DISP",      "fe": "firm_yq",     "controls": "extended", "extra_controls": []},
    # Lead: next quarter — Calendar Year FE
    {"col": 7,  "dv": "DISP_lead", "fe": "industry",    "controls": "base",     "extra_controls": []},
    {"col": 8,  "dv": "DISP_lead", "fe": "firm",        "controls": "base",     "extra_controls": []},
    {"col": 9,  "dv": "DISP_lead", "fe": "industry",    "controls": "extended", "extra_controls": []},
    {"col": 10, "dv": "DISP_lead", "fe": "firm",        "controls": "extended", "extra_controls": []},
    # Lead: next quarter — Year-Quarter FE (Extended controls only)
    {"col": 11, "dv": "DISP_lead", "fe": "industry_yq", "controls": "extended", "extra_controls": []},
    {"col": 12, "dv": "DISP_lead", "fe": "firm_yq",     "controls": "extended", "extra_controls": []},
]

SUMMARY_STATS_VARS = [
    {"col": "DISP", "label": "Wang DISP (contemporaneous)"},
    {"col": "DISP_lead", "label": "Wang DISP (next quarter)"},
    {"col": "DISP_lag", "label": "Wang DISP (prior quarter)"},
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncAnsNoCEO", "label": "Non-CEO Mgr QA Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    {"col": "UncPreNoCEO", "label": "Non-CEO Mgr Pres Uncertainty"},
    {"col": "lnAssets", "label": "Firm Size"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "Capex", "label": "CapEx/Assets"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "sCFO", "label": "OCF Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H5 Wang (2020) Analyst Dispersion Robustness Test",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load the H5b panel from Stage 3 output (parent panel — has NoCEO columns)."""
    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root / "outputs" / "variables" / "h5b_wang_disp",
            required_file="h5b_wang_disp_panel.parquet",
        )
        panel_file = panel_dir / "h5b_wang_disp_panel.parquet"

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

    # Build calendar year-quarter index for YQ FE specs
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} ({100*n_yr_qtr/len(panel):.1f}%)")

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
    fe_type = spec["fe"]

    required = [dv] + KEY_IVS + all_controls + ["gvkey", "fyearq_int", "ff12_code"]
    if fe_type.endswith("_yq"):
        required.append("cal_yr_qtr")

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

    # Determine time index based on FE type
    time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"
    base_fe = fe_type.replace("_yq", "")
    fe_label = f"{'Industry(FF12)' if base_fe == 'industry' else 'Firm'} + {'CalYrQtr' if fe_type.endswith('_yq') else 'CalYear'}"

    print(f"  FE: {fe_label}")
    print(f"  N calls: {len(df_prepared):,}  |  N firms: {df_prepared['gvkey'].nunique():,}")
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
    print(f"  [OK] {elapsed:.1f}s | R²: {model.rsquared:.4f} | Adj R²: {1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid:.4f} | N: {int(model.nobs):,}")

    meta: Dict[str, Any] = {
        "col": col_num, "dv": dv, "fe": fe_type, "controls": spec["controls"],
        "n_obs": int(model.nobs), "n_firms": df_prepared["gvkey"].nunique(),
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
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
            f.write(f"H5 Wang Dispersion Robustness Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Controls: {meta['controls']}\n")
            extra = [c for c in meta.get("extra_controls", []) if c]
            if extra:
                f.write(f"Extra controls: {', '.join(extra)}\n")
            f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    return diag_df


def _write_suite_spec_json(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec_H5.r.json from runner state."""
    results_by_col = {r["meta"]["col"]: r for r in all_results if r.get("meta")}

    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Optional[float]]]] = []

    for spec in MODEL_SPECS:
        col_num = spec["col"]
        if col_num not in results_by_col:
            raise RuntimeError(
                f"suite_spec emission: col {col_num} missing from all_results; "
                f"cannot emit suite_spec_{SUITE_ID}.json"
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

        dv_mean = float(model.model.dependent.dataframe.mean().iloc[0])

        col_metadata.append(
            {
                "col": col_num,
                "dv": spec["dv"],
                "fe_entity": fe_entity,
                "fe_time": fe_time,
                "control_vars": control_list,
                "n_obs": int(meta["n_obs"]),
                "n_firms": int(meta["n_firms"]),
                "r2": float(meta["r2"]),
                "adj_r2": float(meta["adj_r2"]),
                "dv_mean": dv_mean,
                "cluster_fallback": False,
            }
        )

        coefs_per_col.append(
            extract_coefs_panelols(
                model=model,
                key_ivs=KEY_IVS,
                all_vars=KEY_IVS + control_list,
                hyp_dir=HYP_DIR,
            )
        )

    ivs_payload = [
        {"name": iv, "label": iv, "tail": "one_pos"} for iv in KEY_IVS
    ]

    # DISP_lag is the Wang panel's lagged-DV column,
    # but renders as "Lagged_DV" to match the unified convention across suites.
    controls_labels = {"DISP_lag": r"Lagged\_DV"}

    controls_payload = {
        "base": list(BASE_CONTROLS),
        "extended_only": list(EXTENDED_ONLY_CONTROLS),
        "labels": controls_labels,
    }
    header_rows = [
        [
            {"label": "DISP", "span": 6},
            {"label": r"DISP\_lead", "span": 6},
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
        ivs=ivs_payload,
        controls=controls_payload,
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


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
    out_dir = root / "outputs" / "econometric" / "h5b_wang_disp_robustness" / timestamp

    setup_run_logging(log_base_dir=root / "logs", suite_name="H5b_WangDisp_robust", timestamp=timestamp)

    print("=" * 80)
    print("STAGE 4: Test H5 Wang (2020) Analyst Dispersion Robustness")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Specs:     {len(MODEL_SPECS)} models")
    print(f"Test:      One-tailed (beta > 0)")

    panel = load_panel(root, panel_path)

    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "h5b_wang_disp",
        required_file="h5b_wang_disp_panel.parquet",
    ) / "h5b_wang_disp_panel.parquet"

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    print(f"\n  DISP non-null: {panel['DISP'].notna().sum():,}")
    print(f"  DISP_lead non-null: {panel['DISP_lead'].notna().sum():,}")
    print(f"  DISP_lag non-null: {panel['DISP_lag'].notna().sum():,}")

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H5 Wang Dispersion Robustness (Main Sample)",
        label="tab:summary_stats_h5_robust",
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

    # Emit canonical suite_spec.json (consumed by generate_all_tables.py)
    _write_suite_spec_json(all_results, out_dir)

    # Attrition
    if all_results:
        first_n = all_results[0]["meta"].get("n_obs", 0)
        stages = [
            ("Full panel", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("DISP non-null", panel["DISP"].notna().sum()),
            ("After complete-case + min-calls (col 1)", first_n),
        ]
        generate_attrition_table(stages, out_dir, "H5 Wang Dispersion Robustness")

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
