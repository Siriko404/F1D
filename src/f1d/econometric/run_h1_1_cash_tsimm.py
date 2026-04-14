#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H1.1 TNIC-Moderated Cash Holdings Hypothesis
================================================================================
ID: econometric/run_h1_1_cash_tsimm
Description: Test whether product-market similarity (Hoberg-Phillips TNIC3TSIMM)
             moderates the UncAnsMgr → CashRatio relationship.

Model Specification:
    CashRatio = b1*Mgr_QA_Unc_c + b2*z(log(TSIMM))
               + b3*(Mgr_QA_Unc_c x z(log(TSIMM)))
               + controls + IndustryFE + CalendarYearFE + e

    b3 is the coefficient of interest: does product similarity moderate
    the effect of managerial QA uncertainty on cash holdings?

Parent suite: H1 (Cash Holdings)

2 Models:
    Col 1: DV = CashRatio_t, Industry + Calendar Year FE, Extended controls
    Col 2: DV = CashRatio_t, Industry + Calendar Year-Quarter FE, Extended controls

Moderator: TNIC3TSIMM (Hoberg & Phillips JPE 2016)
    Log-transformed then z-scored on Main sample.

Sample: Main only (FF12 not in {8, 11}).
Hypothesis: One-tailed on main IV (b1 > 0); two-tailed on interaction (b3 != 0).
Unit: Call-level (loads H1 panel, merges TNIC at load time).
Panel index: ["gvkey", "cal_yr"] or ["gvkey", "cal_yr_qtr"].
SEs: Firm-clustered.

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet
    - inputs/TNIC3HHIdata/TNIC3HHIdata.txt

Outputs:
    - outputs/econometric/h1_1_cash_tsimm/{timestamp}/...

Deterministic: true
Author: Thesis Author
Date: 2026-03-18
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
    extract_coefs_panelols,
    generate_attrition_table,
    generate_manifest,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

IV = "UncAnsMgr"
IV_CENTERED = "Manager_QA_Unc_c"

CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO",
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
    "Lagged_DV",
]

MODERATOR_RAW = "TotalSimilarity"
MODERATOR = "z_log_TotalSimilarity"
INTERACTION = "MgrQAUnc_x_zlogTSIMM"

MIN_CALLS_PER_FIRM = 5

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission (moderation, 4 cols, single DV).
# Note: Manager_QA_Unc_c is the intermediate centered variable name (Bug 8);
# rename to UncAnsMgr_c is deferred to Phase 7 per the plan.
# ------------------------------------------------------------------
SUITE_ID = "H1.1"
SUITE_DIR_NAME = "h1_1_cash_tsimm"
SUITE_TITLE = "Product Similarity-Moderated Speech Uncertainty and Cash Holdings"
SUITE_CAPTION = (
    "H1.1: Product Similarity--Moderated Speech Uncertainty and Cash Holdings"
)
SUITE_LABEL = "tab:h1_1"
SAMPLE_LABEL = "Main sample (excludes financial and utility firms)."
HYP_DIR = "positive"  # main IV expected beta > 0; moderator + interaction two-tailed
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}
EXTENDED_ONLY_CONTROLS: List[str] = []  # H1.1 uses a single flat control set

MODEL_SPECS = [
    {"col": 1, "dv": "CashRatio", "fe": "industry",    "extra_controls": []},
    {"col": 2, "dv": "CashRatio", "fe": "firm",        "extra_controls": []},
    {"col": 3, "dv": "CashRatio", "fe": "industry_yq", "extra_controls": []},
    {"col": 4, "dv": "CashRatio", "fe": "firm_yq",     "extra_controls": []},
]

SUMMARY_STATS_VARS = [
    {"col": "CashRatio", "label": "Cash Holdings$_t$"},
    {"col": IV, "label": "Mgr QA Uncertainty (raw)"},
    {"col": IV_CENTERED, "label": "Mgr QA Uncertainty (centered)"},
    {"col": MODERATOR_RAW, "label": "TNIC3TSIMM (raw)"},
    {"col": MODERATOR, "label": "$z(\\log(\\mathrm{TSIMM}))$"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Capex", "label": "CapEx / Assets"},
    {"col": "DivDummy", "label": "Dividend Payer"},
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
        description="Stage 4: H1.1 TNIC-Moderated Cash Holdings (call-level)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load call-level H1 panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading H1 panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h1_cash_holdings",
            required_file="h1_cash_holdings_panel.parquet",
        )
        panel_file = panel_dir / "h1_cash_holdings_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    columns = [
        "start_date",
        "gvkey", "year", "fyearq_int", "ff12_code",
        "CashRatio", "CashRatio_lag",
        IV,
        *[c for c in CONTROLS if c != "Lagged_DV"],
    ]

    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")

    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} ({100*n_yr_qtr/len(panel):.1f}%)")

    return panel, panel_file


def load_and_merge_tnic(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Load TNIC3 data and merge TotalSimilarity into panel."""
    print("\n" + "=" * 60)
    print("Merging TNIC3TSIMM")
    print("=" * 60)

    tnic_path = root_path / "inputs" / "TNIC3HHIdata" / "TNIC3HHIdata.txt"
    if not tnic_path.exists():
        raise FileNotFoundError(f"TNIC data not found: {tnic_path}")

    tnic = pd.read_csv(tnic_path, sep="\t")
    print(f"  Loaded TNIC: {len(tnic):,} rows, years {tnic['year'].min()}-{tnic['year'].max()}")

    panel["_gvkey_int"] = pd.to_numeric(panel["gvkey"], errors="coerce")

    before = len(panel)
    panel = panel.merge(
        tnic[["gvkey", "year", "tnic3tsimm"]].rename(
            columns={"gvkey": "_gvkey_int", "year": "fyearq_int", "tnic3tsimm": "TotalSimilarity"}
        ),
        on=["_gvkey_int", "fyearq_int"],
        how="left",
    )
    assert len(panel) == before, f"TNIC merge changed row count: {before} -> {len(panel)}"
    panel = panel.drop(columns=["_gvkey_int"])

    n_matched = panel[MODERATOR_RAW].notna().sum()
    print(f"  TNIC match: {n_matched:,} / {len(panel):,} ({100 * n_matched / len(panel):.1f}%)")

    return panel


def transform_moderator_and_center_iv(
    panel: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Log-transform + z-score TSIMM, and mean-center IV on Main sample."""
    print("\n" + "=" * 60)
    print("Transforming moderator + centering IV")
    print("=" * 60)

    main_mask = ~panel["ff12_code"].isin([8, 11])

    tsimm_main = panel.loc[main_mask, MODERATOR_RAW].dropna()
    log_tsimm_main = np.log(tsimm_main)
    tsimm_mu = log_tsimm_main.mean()
    tsimm_sd = log_tsimm_main.std()

    panel["log_TotalSimilarity"] = np.log(panel[MODERATOR_RAW])
    panel[MODERATOR] = (panel["log_TotalSimilarity"] - tsimm_mu) / tsimm_sd

    print(f"  Main sample TSIMM obs: {len(tsimm_main):,}")
    print(f"  log(TSIMM) mean: {tsimm_mu:.4f}, std: {tsimm_sd:.4f}")

    z_main = panel.loc[main_mask, MODERATOR].dropna()
    print(f"  z(log(TSIMM)) on Main: mean={z_main.mean():.4f}, std={z_main.std():.4f}")

    iv_main = panel.loc[main_mask, IV].dropna()
    iv_mu = iv_main.mean()
    panel[IV_CENTERED] = panel[IV] - iv_mu

    print(f"  IV mean (Main): {iv_mu:.4f}")

    params = {
        "tsimm_mu": tsimm_mu,
        "tsimm_sd": tsimm_sd,
        "iv_mu": iv_mu,
    }

    return panel, params


# ==============================================================================
# Regression
# ==============================================================================


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only (exclude Finance ff12=8, Utility ff12=11)."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any]
) -> pd.DataFrame:
    """Prepare data for one regression spec with interaction term."""
    dv = spec["dv"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"

    lag_col = f"{dv}_lag"
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    required = [dv, IV, IV_CENTERED, MODERATOR] + all_controls + ["gvkey", time_col, "ff12_code"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Create interaction term using CENTERED IV
    df[INTERACTION] = df[IV_CENTERED] * df[MODERATOR]

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases
    all_required = required + [INTERACTION]
    complete_mask = df[all_required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Min calls per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()

    n_firms = df["gvkey"].nunique()
    n_time_periods = df.groupby(["gvkey", time_col]).ngroups
    print(f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
          f"{len(df):,} calls, {n_firms:,} firms, {n_time_periods:,} firm-time-periods")

    return df


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any]
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS with Industry FE + Calendar Year or Year-Quarter FE."""
    dv = spec["dv"]
    col_num = spec["col"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"
    base_fe = fe.replace("_yq", "")
    fe_label = f"{'Firm' if base_fe == 'firm' else 'Industry(FF12)'} + {'CalYrQtr' if fe.endswith('_yq') else 'CalYear'}"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_label}")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    exog = [IV_CENTERED, MODERATOR, INTERACTION] + all_controls

    n_firms = df_prepared["gvkey"].nunique()
    n_time_periods = df_prepared.groupby(["gvkey", time_col]).ngroups
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}, firm-time-periods={n_time_periods:,}")
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
        else:  # firm
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()

    beta_iv = float(model.params.get(IV_CENTERED, np.nan))
    se_iv = float(model.std_errors.get(IV_CENTERED, np.nan))
    p_two_iv = float(model.pvalues.get(IV_CENTERED, np.nan))

    # One-tailed p for main IV (expected positive)
    if not np.isnan(p_two_iv) and not np.isnan(beta_iv):
        p_one_iv = p_two_iv / 2 if beta_iv > 0 else 1 - p_two_iv / 2
    else:
        p_one_iv = np.nan

    beta_mod = float(model.params.get(MODERATOR, np.nan))
    se_mod = float(model.std_errors.get(MODERATOR, np.nan))
    p_two_mod = float(model.pvalues.get(MODERATOR, np.nan))

    beta_int = float(model.params.get(INTERACTION, np.nan))
    se_int = float(model.std_errors.get(INTERACTION, np.nan))
    p_two_int = float(model.pvalues.get(INTERACTION, np.nan))

    stars_iv = _sig_stars_one(p_one_iv)
    stars_int = _sig_stars_two(p_two_int)

    print(f"  [OK] {elapsed:.1f}s | R2={model.rsquared:.4f}  Adj R2={1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid:.4f}")
    print(f"  {IV}: b={beta_iv:.4f} p1={p_one_iv:.4f} {stars_iv}")
    print(f"  {MODERATOR}: b={beta_mod:.4f} p2={p_two_mod:.4f}")
    print(f"  INTERACTION: b={beta_int:.4f} p2={p_two_int:.4f} {stars_int}")

    meta = {
        "col": col_num,
        "dv": dv,
        "fe": fe,
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "n_time_periods": n_time_periods,
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
        "beta_iv": beta_iv, "se_iv": se_iv,
        "p_one_iv": p_one_iv, "p_two_iv": p_two_iv,
        "beta_moderator": beta_mod, "se_moderator": se_mod, "p_two_moderator": p_two_mod,
        "beta_interaction": beta_int, "se_interaction": se_int, "p_two_interaction": p_two_int,
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
    }

    return model, meta


def _sig_stars_one(p: float) -> str:
    if np.isnan(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def _sig_stars_two(p: float) -> str:
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
            f.write(f"H1.1 TNIC-Moderated Cash Holdings Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"IV: {IV}\n")
            f.write(f"Moderator: z(log(TNIC3TSIMM))\n")
            f.write(f"Interaction: {INTERACTION}\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
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
    """Emit canonical suite_spec_H1.1.json from moderation runner state.

    H1.1 structure: 4 cols = 2 FE entities (industry/firm) x 2 time-FE
    granularities (cal_yr / cal_yr_qtr). Three top-of-table IVs with
    per-IV tails: main IV one-tailed positive, moderator and interaction
    two-tailed.
    """
    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    results_by_col = {
        r["meta"]["col"]: r for r in all_results if r.get("meta")
    }

    for spec in MODEL_SPECS:
        col_num = spec["col"]
        if col_num not in results_by_col:
            raise RuntimeError(
                f"H1.1 spec build: missing result for col {col_num}"
            )
        result = results_by_col[col_num]
        model = result["model"]
        meta = result["meta"]

        fe = spec["fe"]
        base_fe = fe.replace("_yq", "")
        fe_entity = "industry" if base_fe == "industry" else "firm"
        fe_time = (
            "calendar_year_quarter" if fe.endswith("_yq") else "calendar_year"
        )

        extra_controls = spec.get("extra_controls", [])
        control_vars = list(CONTROLS) + list(extra_controls)

        try:
            dv_mean: Optional[float] = float(
                model.model.dependent.dataframe.mean().iloc[0]
            )
        except Exception:
            dv_mean = None

        col_metadata.append(
            {
                "col": col_num,
                "dv": spec["dv"],
                "fe_entity": fe_entity,
                "fe_time": fe_time,
                "control_vars": control_vars,
                "n_obs": int(meta["n_obs"]),
                "n_firms": int(meta.get("n_firms", 0)) or None,
                "r2": float(meta["r2"]),
                "adj_r2": float(meta.get("adj_r2", float("nan"))),
                "dv_mean": dv_mean,
                "cluster_fallback": False,
            }
        )

        # IV key names: centered main IV, moderator, interaction
        iv_key_names = [IV_CENTERED, MODERATOR, INTERACTION]
        coefs_per_col.append(
            extract_coefs_panelols(
                model=model,
                key_ivs=iv_key_names,
                all_vars=iv_key_names + control_vars,
                hyp_dir=HYP_DIR,
            )
        )

    header_rows = [
        [{"label": "CashRatio", "span": len(MODEL_SPECS)}]
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
                "suite_type": "moderation",
            }
        ],
        coefs_per_col=coefs_per_col,
        col_metadata=col_metadata,
        sample_label=SAMPLE_LABEL,
        clustering=CLUSTERING,
        tail=TAIL,
        # All three H1.1 key vars are one-tailed positive per
        # feedback_moderation_tails.md (user explicitly corrected twice —
        # IV, moderator, AND interaction must all be one-tailed positive).
        ivs=[
            {"name": IV_CENTERED, "label": r"Manager\_QA\_Unc\_c", "tail": "one_pos"},
            {"name": MODERATOR, "label": r"z\_log\_TotalSimilarity", "tail": "one_pos"},
            {"name": INTERACTION, "label": r"MgrQAUnc\_x\_zlogTSIMM", "tail": "one_pos"},
        ],
        controls={
            "base": list(CONTROLS),
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
    out_dir = root / "outputs" / "econometric" / "h1_1_cash_tsimm" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H1_1_CashTSIMM",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H1.1 TNIC-Moderated Cash Holdings")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    1 IV x 1 DV x 2 FE types = 2 models")
    print(f"Moderator: z(log(TNIC3TSIMM))")
    print(f"IV:        {IV}")

    panel, panel_file = load_panel(root, panel_path)

    panel = load_and_merge_tnic(panel, root)

    panel, transform_params = transform_moderator_and_center_iv(panel)

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    print(f"  CashRatio non-null: {panel['CashRatio'].notna().sum():,}")
    print(f"  {IV}: {panel[IV].notna().sum():,} "
          f"({100 * panel[IV].notna().mean():.1f}%)")
    print(f"  {MODERATOR}: {panel[MODERATOR].notna().sum():,} "
          f"({100 * panel[MODERATOR].notna().mean():.1f}%)")

    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H1.1 TNIC-Moderated Cash Holdings (Main Sample)",
        label="tab:summary_stats_h1_1",
    )
    print("  Saved: summary_stats.csv/.tex")

    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} FE={spec['fe']} ---")

        try:
            df_prep = prepare_regression_data(panel, spec)
        except ValueError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue
        if len(df_prep) < 100:
            print(f"  Skipping: too few obs")
            continue

        model, meta = run_regression(df_prep, spec)
        if model is not None and meta:
            all_results.append({"model": model, "meta": meta})

    diag_df = save_outputs(all_results, out_dir)
    _write_suite_spec_json(all_results, out_dir)

    # Attrition
    tnic_matched = panel[MODERATOR_RAW].notna().sum()
    if all_results:
        first = all_results[0]["meta"]
        attrition_stages = [
            ("Full panel (H1)", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("TNIC3TSIMM matched", tnic_matched),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(
            attrition_stages, out_dir, "H1.1 TNIC-Moderated Cash Holdings",
        )
        print("  Saved: sample_attrition.csv/.tex")

    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={
            "panel": panel_file,
            "tnic": root / "inputs" / "TNIC3HHIdata" / "TNIC3HHIdata.txt",
        },
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

    for r in all_results:
        m = r["meta"]
        stars_iv = _sig_stars_one(m["p_one_iv"])
        stars_int = _sig_stars_two(m["p_two_interaction"])
        print(f"  Col ({m['col']}) {m['dv']}: "
              f"IV b={m['beta_iv']:.4f}{stars_iv} | "
              f"Interaction b={m['beta_interaction']:.4f}{stars_int}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: validating...")
        print(f"  IV: {IV}")
        print(f"  Specs: {len(MODEL_SPECS)}")
        print(f"  Controls: {len(CONTROLS)}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
