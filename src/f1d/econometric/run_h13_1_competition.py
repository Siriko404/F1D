#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H13.1 TNIC-Moderated Capital Expenditure Hypothesis (Redesigned)
================================================================================
ID: econometric/run_h13_1_competition
Description: Test whether product-market structure (Hoberg-Phillips TNIC3TSIMM
             and TNIC3HHI) moderates the Manager_QA_Uncertainty → CapexAt
             relationship.

Model Specification (per moderator):
    CapexAt = b1*Mgr_QA_Unc_c + b2*z(log(MOD)) + b3*(Mgr_QA_Unc_c x z(log(MOD)))
            + controls [+ CapexAt_t for lead specs] + IndustryFE + FiscalYearFE + e

    b3 is the coefficient of interest: does market structure moderate
    the effect of managerial Q&A uncertainty on capital expenditure?

Parent suite: H13 (Capital Expenditure)
    Manager_QA_Uncertainty_pct significant in all 4 Industry+FY specs (p<0.005).
    Moderation memo: TSIMM = primary (strong), HHI = robustness (secondary).

8 Models:
    Cols 1-4: Calendar Year FE (Industry + FY)
        1-2: Moderator = z(log(TNIC3TSIMM)) — PRIMARY
        3-4: Moderator = z(log(TNIC3HHI)) — ROBUSTNESS
    Cols 5-8: Year-Quarter FE (Industry + YQ)
        5-6: Moderator = z(log(TNIC3TSIMM)) — PRIMARY
        7-8: Moderator = z(log(TNIC3HHI)) — ROBUSTNESS
    Within each pair: CapexAt, CapexAt_lead

Expected interaction signs (tentative):
    TSIMM: positive (product similarity intensifies strategic investment response)
    HHI: negative (concentration dampens strategic investment response)

Corr(log(HHI), log(TSIMM)) ≈ -0.70 — moderators are NOT independent.

NOTE: This file REPLACES the original H13.1 competition runner which had
critical issues: uncentered interactions, HHI-only, 16 models with 4 separate
IVs, and only 1/16 significant result that failed Bonferroni correction.

Sample: Main only (FF12 not in {8, 11}).
Hypothesis: All two-tailed (matching parent H13).
Unit: Call-level (loads H13 panel, merges TNIC at load time).
Panel index: ["gvkey", "fyearq_int"].
SEs: Firm-clustered.

Inputs:
    - outputs/variables/h13_capex/latest/h13_capex_panel.parquet
    - inputs/TNIC3HHIdata/TNIC3HHIdata.txt

Outputs:
    - outputs/econometric/h13_1_competition/{timestamp}/...

Deterministic: true
Author: Thesis Author
Date: 2026-03-19
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

IV = "Manager_QA_Uncertainty_pct"
IV_CENTERED = "Manager_QA_Unc_c"

CONTROLS = [
    "Size", "TobinsQ", "ROA", "BookLev", "CashHoldings",
    "DividendPayer", "OCF_Volatility",
    "SalesGrowth", "RD_Intensity", "CashFlow", "Volatility",
    "Lagged_DV",  # Unified lagged DV
]

MODERATORS = {
    "tsimm": {
        "raw": "tnic3tsimm",
        "log": "log_tnic3tsimm",
        "z": "z_log_tnic3tsimm",
        "interaction": "MgrQAUnc_x_zlogTSIMM",
        "label": "TNIC3TSIMM",
        "tex_label": r"$z(\log(\mathrm{TSIMM}))$",
        "tex_int_label": r"Mgr QA Unc $\times$ $z(\log(\mathrm{TSIMM}))$",
    },
    "hhi": {
        "raw": "tnic3hhi",
        "log": "log_tnic3hhi",
        "z": "z_log_tnic3hhi",
        "interaction": "MgrQAUnc_x_zlogHHI",
        "label": "TNIC3HHI",
        "tex_label": r"$z(\log(\mathrm{HHI}))$",
        "tex_int_label": r"Mgr QA Unc $\times$ $z(\log(\mathrm{HHI}))$",
    },
}

MIN_CALLS_PER_FIRM = 5

MODEL_SPECS = [
    # Calendar Year FE
    {"col": 1, "dv": "CapexAt",      "mod": "tsimm", "fe": "industry",    "extra_controls": []},
    {"col": 2, "dv": "CapexAt_lead", "mod": "tsimm", "fe": "industry",    "extra_controls": []},
    {"col": 3, "dv": "CapexAt",      "mod": "hhi",   "fe": "industry",    "extra_controls": []},
    {"col": 4, "dv": "CapexAt_lead", "mod": "hhi",   "fe": "industry",    "extra_controls": []},
    # Year-Quarter FE
    {"col": 5, "dv": "CapexAt",      "mod": "tsimm", "fe": "industry_yq", "extra_controls": []},
    {"col": 6, "dv": "CapexAt_lead", "mod": "tsimm", "fe": "industry_yq", "extra_controls": []},
    {"col": 7, "dv": "CapexAt",      "mod": "hhi",   "fe": "industry_yq", "extra_controls": []},
    {"col": 8, "dv": "CapexAt_lead", "mod": "hhi",   "fe": "industry_yq", "extra_controls": []},
]

DV_TEX = {
    "CapexAt": r"CapEx/AT$_t$",
    "CapexAt_lead": r"CapEx/AT$_{t+1}$",
}

SUMMARY_STATS_VARS = [
    {"col": "CapexAt", "label": "CapEx / Assets$_t$"},
    {"col": "CapexAt_lead", "label": "CapEx / Assets$_{t+1}$"},
    {"col": IV, "label": "Mgr QA Uncertainty (raw)"},
    {"col": IV_CENTERED, "label": "Mgr QA Uncertainty (centered)"},
    {"col": "tnic3tsimm", "label": "TNIC3TSIMM (raw)"},
    {"col": "z_log_tnic3tsimm", "label": "$z(\\log(\\mathrm{TSIMM}))$"},
    {"col": "tnic3hhi", "label": "TNIC3HHI (raw)"},
    {"col": "z_log_tnic3hhi", "label": "$z(\\log(\\mathrm{HHI}))$"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "BookLev", "label": "Book Leverage"},
    {"col": "CashHoldings", "label": "Cash Holdings"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
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
        description="Stage 4: H13.1 TNIC-Moderated Capex (redesigned, call-level)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load call-level H13 capex panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading H13 capex panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h13_capex",
            required_file="h13_capex_panel.parquet",
        )
        panel_file = panel_dir / "h13_capex_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    columns = [
        "gvkey", "year", "fyearq_int", "ff12_code",
        "start_date",  # needed for cal_yr_qtr
        "CapexAt", "CapexAt_lead", "CapexAt_lag",
        IV,
        *[c for c in CONTROLS if c != "Lagged_DV"],  # lagged created dynamically
    ]

    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")

    # Build calendar year-quarter index for YQ FE specs
    panel = build_cal_yr_qtr_index(panel)
    n_yq = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yq:,} / {len(panel):,} ({100 * n_yq / len(panel):.1f}%)")

    return panel, panel_file


def load_and_merge_tnic(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Load TNIC3 data and merge both tnic3tsimm and tnic3hhi into panel."""
    print("\n" + "=" * 60)
    print("Merging TNIC3 (TSIMM + HHI)")
    print("=" * 60)

    tnic_path = root_path / "inputs" / "TNIC3HHIdata" / "TNIC3HHIdata.txt"
    if not tnic_path.exists():
        raise FileNotFoundError(f"TNIC data not found: {tnic_path}")

    tnic = pd.read_csv(tnic_path, sep="\t")
    print(f"  Loaded TNIC: {len(tnic):,} rows, years {tnic['year'].min()}-{tnic['year'].max()}")

    panel["_gvkey_int"] = pd.to_numeric(panel["gvkey"], errors="coerce")

    before = len(panel)
    panel = panel.merge(
        tnic[["gvkey", "year", "tnic3tsimm", "tnic3hhi"]].rename(
            columns={"gvkey": "_gvkey_int", "year": "fyearq_int"}
        ),
        on=["_gvkey_int", "fyearq_int"],
        how="left",
    )
    assert len(panel) == before, f"TNIC merge changed row count: {before} -> {len(panel)}"
    panel = panel.drop(columns=["_gvkey_int"])

    for mod_key, mod_info in MODERATORS.items():
        raw_col = mod_info["raw"]
        n_matched = panel[raw_col].notna().sum()
        print(f"  {mod_info['label']} match: {n_matched:,} / {len(panel):,} "
              f"({100 * n_matched / len(panel):.1f}%)")

    return panel


def transform_moderators_and_center_iv(
    panel: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Log-transform + z-score both moderators, and mean-center IV on Main sample."""
    print("\n" + "=" * 60)
    print("Transforming moderators + centering IV")
    print("=" * 60)

    main_mask = ~panel["ff12_code"].isin([8, 11])
    params: Dict[str, float] = {}

    for mod_key, mod_info in MODERATORS.items():
        raw_col = mod_info["raw"]
        log_col = mod_info["log"]
        z_col = mod_info["z"]

        mod_main = panel.loc[main_mask, raw_col].dropna()
        log_main = np.log(mod_main)
        mu = log_main.mean()
        sd = log_main.std()

        panel[log_col] = np.log(panel[raw_col])
        panel[z_col] = (panel[log_col] - mu) / sd

        params[f"{mod_key}_mu"] = mu
        params[f"{mod_key}_sd"] = sd

        z_check = panel.loc[main_mask, z_col].dropna()
        print(f"  {mod_info['label']}: N={len(mod_main):,}, "
              f"log mean={mu:.4f}, log sd={sd:.4f}, "
              f"z mean={z_check.mean():.4f}, z std={z_check.std():.4f}")

    # Cross-moderator correlation
    both_valid = main_mask & panel["z_log_tnic3hhi"].notna() & panel["z_log_tnic3tsimm"].notna()
    if both_valid.sum() > 100:
        corr = panel.loc[both_valid, "z_log_tnic3hhi"].corr(
            panel.loc[both_valid, "z_log_tnic3tsimm"]
        )
        print(f"  Corr(z(log(HHI)), z(log(TSIMM))): {corr:.4f}")
        params["cross_corr"] = corr

    # IV: mean-center on Main sample
    iv_main = panel.loc[main_mask, IV].dropna()
    iv_mu = iv_main.mean()
    panel[IV_CENTERED] = panel[IV] - iv_mu
    params["iv_mu"] = iv_mu

    print(f"  IV mean (Main): {iv_mu:.4f}")

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
    mod_key = spec["mod"]
    mod_info = MODERATORS[mod_key]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    # Create Lagged_DV: always lag of the base DV (t-1)
    base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")
    lag_col = f"{base_dv}_lag"
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    z_col = mod_info["z"]
    int_col = mod_info["interaction"]

    fe_type = spec.get("fe", "industry")
    time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"
    required = [dv, IV, IV_CENTERED, z_col] + all_controls + ["gvkey", "fyearq_int", "ff12_code", time_col]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Create interaction term using CENTERED IV
    df[int_col] = df[IV_CENTERED] * df[z_col]

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases
    all_required = required + [int_col]
    complete_mask = df[all_required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Min calls per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()

    n_firms = df["gvkey"].nunique()
    n_firm_years = df.groupby(["gvkey", "fyearq_int"]).ngroups
    print(f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
          f"{len(df):,} calls, {n_firms:,} firms, {n_firm_years:,} firm-years")

    return df


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any]
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS with Industry FE and firm-clustered SEs (Calendar Year or Year-Quarter)."""
    dv = spec["dv"]
    col_num = spec["col"]
    mod_key = spec["mod"]
    mod_info = MODERATORS[mod_key]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    z_col = mod_info["z"]
    int_col = mod_info["interaction"]

    fe_type = spec.get("fe", "industry")
    time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"
    fe_label = "Industry+YQ" if fe_type.endswith("_yq") else "Industry+FY"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | Mod={mod_info['label']} | FE={fe_label}")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    exog = [IV_CENTERED, z_col, int_col] + all_controls

    n_firms = df_prepared["gvkey"].nunique()
    n_firm_years = df_prepared.groupby(["gvkey", "fyearq_int"]).ngroups
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}, firm-years={n_firm_years:,}")
    if extra_controls:
        print(f"  Extra controls: {extra_controls}")
    t0 = datetime.now()

    df_panel = df_prepared.set_index(["gvkey", time_col])

    try:
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
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()

    # Extract coefficients — all two-tailed
    beta_iv = float(model.params.get(IV_CENTERED, np.nan))
    se_iv = float(model.std_errors.get(IV_CENTERED, np.nan))
    p_two_iv = float(model.pvalues.get(IV_CENTERED, np.nan))

    beta_mod = float(model.params.get(z_col, np.nan))
    se_mod = float(model.std_errors.get(z_col, np.nan))
    p_two_mod = float(model.pvalues.get(z_col, np.nan))

    beta_int = float(model.params.get(int_col, np.nan))
    se_int = float(model.std_errors.get(int_col, np.nan))
    p_two_int = float(model.pvalues.get(int_col, np.nan))

    # Extract lagged DV control
    beta_lag_dv = float(model.params.get("Lagged_DV", np.nan))
    se_lag_dv = float(model.std_errors.get("Lagged_DV", np.nan))
    p_two_lag_dv = float(model.pvalues.get("Lagged_DV", np.nan))

    stars_iv = _sig_stars(p_two_iv)
    stars_int = _sig_stars(p_two_int)

    print(f"  [OK] {elapsed:.1f}s | R2w={model.rsquared_within:.4f}")
    print(f"  {IV}: b={beta_iv:.4f} p2={p_two_iv:.4f} {stars_iv}")
    print(f"  {z_col}: b={beta_mod:.4f} p2={p_two_mod:.4f}")
    print(f"  INTERACTION: b={beta_int:.4f} p2={p_two_int:.4f} {stars_int}")
    if not np.isnan(beta_lag_dv):
        print(f"  Lagged_DV (control): b={beta_lag_dv:.4f}")

    meta = {
        "col": col_num,
        "dv": dv,
        "moderator": mod_key,
        "fe": fe_type,
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "n_firm_years": n_firm_years,
        "within_r2": float(model.rsquared_within),
        "beta_iv": beta_iv, "se_iv": se_iv, "p_two_iv": p_two_iv,
        "beta_moderator": beta_mod, "se_moderator": se_mod, "p_two_moderator": p_two_mod,
        "beta_interaction": beta_int, "se_interaction": se_int, "p_two_interaction": p_two_int,
        "beta_lag_dv": beta_lag_dv, "se_lag_dv": se_lag_dv, "p_two_lag_dv": p_two_lag_dv,
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
    }

    return model, meta


def _sig_stars(p: float) -> str:
    """Significance stars for two-tailed p-value."""
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
    """Write LaTeX table with Panel A (TSIMM, primary) + Panel B (HHI, robustness)."""
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    def fmt_coef(val: float, stars: str) -> str:
        if np.isnan(val):
            return ""
        return f"{val:.4f}{stars}"

    def fmt_se(val: float) -> str:
        if np.isnan(val):
            return ""
        return f"({val:.4f})"

    def fmt_r2(val: float) -> str:
        if np.isnan(val):
            return ""
        if abs(val) < 0.001:
            return f"{val:.2e}"
        return f"{val:.3f}"

    n_cols = 8  # 4 Calendar Year FE + 4 Year-Quarter FE
    col_spec = "l" + "c" * n_cols

    def _panel_lines(mod_key: str, cols_fy: List[int], cols_yq: List[int], panel_label: str) -> List[str]:
        mod_info = MODERATORS[mod_key]
        cols = cols_fy + cols_yq
        lines = []
        lines.append(f"\\multicolumn{{{n_cols + 1}}}{{l}}{{\\textit{{{panel_label}}}}} \\\\")
        lines.append("\\midrule")

        col_nums = " & ".join(f"({c})" for c in cols)
        dv_labels = " & ".join(DV_TEX.get(results_by_col.get(c, {}).get("dv", ""), "?") for c in cols)
        lines.append(f" & {col_nums} \\\\")
        lines.append(f" & {dv_labels} \\\\")
        lines.append("\\midrule")

        # IV coefficient
        coefs = " & ".join(
            fmt_coef(results_by_col.get(c, {}).get("beta_iv", np.nan),
                     _sig_stars(results_by_col.get(c, {}).get("p_two_iv", np.nan)))
            for c in cols
        )
        ses = " & ".join(fmt_se(results_by_col.get(c, {}).get("se_iv", np.nan)) for c in cols)
        lines.append(f"Mgr QA Uncertainty & {coefs} \\\\")
        lines.append(f" & {ses} \\\\")

        # Moderator coefficient
        coefs = " & ".join(
            fmt_coef(results_by_col.get(c, {}).get("beta_moderator", np.nan),
                     _sig_stars(results_by_col.get(c, {}).get("p_two_moderator", np.nan)))
            for c in cols
        )
        ses = " & ".join(fmt_se(results_by_col.get(c, {}).get("se_moderator", np.nan)) for c in cols)
        lines.append(f"{mod_info['tex_label']} & {coefs} \\\\")
        lines.append(f" & {ses} \\\\")

        # Interaction coefficient (key)
        coefs = " & ".join(
            fmt_coef(results_by_col.get(c, {}).get("beta_interaction", np.nan),
                     _sig_stars(results_by_col.get(c, {}).get("p_two_interaction", np.nan)))
            for c in cols
        )
        ses = " & ".join(fmt_se(results_by_col.get(c, {}).get("se_interaction", np.nan)) for c in cols)
        lines.append(f"{mod_info['tex_int_label']} & {coefs} \\\\")
        lines.append(f" & {ses} \\\\")

        # Lagged DV
        lag_coefs = []
        lag_ses = []
        has_lag = False
        for c in cols:
            m = results_by_col.get(c, {})
            lag_val = m.get("beta_lag_dv", np.nan)
            if not np.isnan(lag_val):
                has_lag = True
                lag_coefs.append(fmt_coef(lag_val, _sig_stars(m.get("p_two_lag_dv", np.nan))))
                lag_ses.append(fmt_se(m.get("se_lag_dv", np.nan)))
            else:
                lag_coefs.append("")
                lag_ses.append("")
        if has_lag:
            lines.append(f"Lagged\\_DV & {' & '.join(lag_coefs)} \\\\")
            lines.append(f" & {' & '.join(lag_ses)} \\\\")

        lines.append("\\midrule")

        lines.append("Controls & " + " & ".join(["Ext"] * len(cols)) + " \\\\")
        lines.append("Industry FE & " + " & ".join(["Yes"] * len(cols)) + " \\\\")

        # FE row: Calendar Year for first half, Year-Quarter for second half
        fy_vals = ["Yes"] * len(cols_fy) + [""] * len(cols_yq)
        yq_vals = [""] * len(cols_fy) + ["Yes"] * len(cols_yq)
        lines.append("Fiscal Year FE & " + " & ".join(fy_vals) + " \\\\")
        lines.append("Year-Quarter FE & " + " & ".join(yq_vals) + " \\\\")
        lines.append("\\midrule")

        n_row = " & ".join(f"{results_by_col.get(c, {}).get('n_obs', 0):,}" for c in cols)
        fy_row = " & ".join(f"{results_by_col.get(c, {}).get('n_firm_years', 0):,}" for c in cols)
        r2_row = " & ".join(fmt_r2(results_by_col.get(c, {}).get("within_r2", np.nan)) for c in cols)
        lines.append(f"N (calls) & {n_row} \\\\")
        lines.append(f"N (firm-years) & {fy_row} \\\\")
        lines.append(f"Within-R$^2$ & {r2_row} \\\\")

        return lines

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Market Structure--Moderated Speech Uncertainty and Capital Expenditure}",
        r"\label{tab:h13_1_capex_tnic}",
        r"\small",
        f"\\begin{{tabular}}{{{col_spec}}}",
        r"\toprule",
    ]

    lines += _panel_lines("tsimm", [1, 2], [5, 6], "Panel A: TNIC3TSIMM (primary)")
    lines.append("\\midrule")
    lines += _panel_lines("hhi", [3, 4], [7, 8], "Panel B: TNIC3HHI (robustness)")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (all two-tailed). ",
        r"Mgr QA Uncertainty mean-centered; coefficient = effect at sample-mean uncertainty. ",
        r"Standard errors (in parentheses) clustered at firm level. ",
        r"Main sample (excludes financial and utility firms). ",
        r"TNIC3TSIMM and TNIC3HHI from Hoberg--Phillips (2016), log-transformed and standardized. ",
        r"TSIMM is the primary moderator (product similarity $\to$ strategic investment channel); ",
        r"HHI serves as robustness (market concentration channel). ",
        r"Cols~(1)--(4): Calendar Year FE; Cols~(5)--(8): Year-Quarter FE. ",
        r"TNIC measures are firm-year variables repeated across calls within the same firm-year. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h13_1_capex_tnic_table.tex"
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
        mod_label = MODERATORS[meta["moderator"]]["label"]
        fname = f"regression_results_col{col_num}_{meta['dv']}_{meta['moderator']}.txt"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            f.write(f"H13.1 TNIC-Moderated Capex Regression (Redesigned)\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"IV: {IV} (centered)\n")
            f.write(f"Moderator: z(log({mod_label}))\n")
            f.write(f"FE: {meta['fe']}\n")
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


def generate_report(
    all_results: List[Dict[str, Any]], out_dir: Path,
    duration: float, params: Dict[str, float],
) -> None:
    """Generate markdown report."""
    lines = [
        "# H13.1 TNIC-Moderated Capital Expenditure Report (Redesigned)",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Design:** Manager_QA_Uncertainty x z(log(TNIC)) interaction",
        f"**Moderators:** TSIMM (primary) + HHI (robustness)",
        f"**Cross-corr:** {params.get('cross_corr', np.nan):.4f}",
        f"**FE:** Industry(FF12) + FiscalYear (cols 1-4), Industry(FF12) + Year-Quarter (cols 5-8)",
        f"**Parent suite:** H13 (Capital Expenditure)",
        "",
        "## Results",
        "",
        "| Col | DV | Mod | FE | b_iv | p2_iv | b_int | p2_int | N | N_fy | R2w |",
        "|-----|----|-----|----|------|-------|-------|--------|---|------|-----|",
    ]

    for r in all_results:
        m = r.get("meta", {})
        if not m:
            continue
        stars_iv = _sig_stars(m["p_two_iv"])
        stars_int = _sig_stars(m["p_two_interaction"])
        fe_short = "YQ" if m["fe"].endswith("_yq") else "FY"
        lines.append(
            f"| ({m['col']}) | {m['dv']} | {m['moderator']} | {fe_short} | "
            f"{m['beta_iv']:.4f}{stars_iv} | {m['p_two_iv']:.4f} | "
            f"{m['beta_interaction']:.4f}{stars_int} | {m['p_two_interaction']:.4f} | "
            f"{m['n_obs']:,} | {m['n_firm_years']:,} | {m['within_r2']:.4f} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- All tests two-tailed (matching parent H13)",
        "- IV mean-centered to avoid multicollinearity",
        "- TSIMM expected interaction: positive; HHI expected: negative",
        f"- Corr(z(log(HHI)), z(log(TSIMM))) = {params.get('cross_corr', np.nan):.4f}",
        "- Lagged_DV included as control in all specs",
        "- Cols 1-4: Calendar Year FE; Cols 5-8: Year-Quarter FE",
        "- TNIC measures are firm-year, repeated across calls",
        "- SEs firm-clustered throughout",
        "- This REPLACES the original H13.1 (uncentered, HHI-only, 16-model design)",
    ]

    with open(out_dir / "report_step4_H13_1.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H13_1.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h13_1_competition" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H13_1_Competition",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H13.1 TNIC-Moderated Capex (Redesigned)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    1 IV x 2 DVs x 2 moderators x 2 FE = 8 models")
    print(f"Moderators: TSIMM (primary) + HHI (robustness)")
    print(f"IV:        {IV}")

    panel, panel_file = load_panel(root, panel_path)
    panel = load_and_merge_tnic(panel, root)
    panel, transform_params = transform_moderators_and_center_iv(panel)

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    for dv in ["CapexAt", "CapexAt_lead"]:
        print(f"  {dv} non-null: {panel[dv].notna().sum():,}")
    print(f"  {IV}: {panel[IV].notna().sum():,} ({100 * panel[IV].notna().mean():.1f}%)")
    for mod_key, mod_info in MODERATORS.items():
        z_col = mod_info["z"]
        print(f"  {mod_info['label']}: {panel[z_col].notna().sum():,} "
              f"({100 * panel[z_col].notna().mean():.1f}%)")

    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H13.1 TNIC-Moderated Capex (Main Sample)",
        label="tab:summary_stats_h13_1",
    )
    print("  Saved: summary_stats.csv/.tex")

    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        mod_label = MODERATORS[spec["mod"]]["label"]
        fe_label = "Industry+YQ" if spec.get("fe", "industry").endswith("_yq") else "Industry+FY"
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} Mod={mod_label} FE={fe_label} ---")

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

    tsimm_matched = panel["tnic3tsimm"].notna().sum()
    hhi_matched = panel["tnic3hhi"].notna().sum()
    if all_results:
        first_tsimm = next((r["meta"] for r in all_results if r["meta"]["moderator"] == "tsimm"), {})
        first_hhi = next((r["meta"] for r in all_results if r["meta"]["moderator"] == "hhi"), {})
        attrition_stages = [
            ("Full panel (H13)", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("TNIC3TSIMM matched", tsimm_matched),
            ("TNIC3HHI matched", hhi_matched),
            ("After complete-case + min-calls (TSIMM, col 1)", first_tsimm.get("n_obs", 0)),
            ("After complete-case + min-calls (HHI, col 3)", first_hhi.get("n_obs", 0)),
        ]
        generate_attrition_table(
            attrition_stages, out_dir, "H13.1 TNIC-Moderated Capex",
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
    generate_report(all_results, out_dir, duration, transform_params)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")

    for r in all_results:
        m = r["meta"]
        stars_int = _sig_stars(m["p_two_interaction"])
        fe_short = "YQ" if m["fe"].endswith("_yq") else "FY"
        print(f"  Col ({m['col']}) {m['dv']} [{m['moderator']}] FE={fe_short}: "
              f"IV b={m['beta_iv']:.4f} | Int b={m['beta_interaction']:.4f}{stars_int}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: validating...")
        print(f"  IV: {IV}")
        print(f"  Specs: {len(MODEL_SPECS)}")
        print(f"  Controls: {len(CONTROLS)}")
        print(f"  Moderators: {list(MODERATORS.keys())}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
