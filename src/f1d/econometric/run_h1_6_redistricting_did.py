#!/usr/bin/env python3
"""
================================================================================
STAGE 4: H1.6 Redistricting DiD on Cash + Speech (Hasan 2022 Layer 2)
================================================================================
ID: econometric/run_h1_6_redistricting_did
Description: Difference-in-differences design replicating Hasan, Alam,
             Paramati & Islam (2022) RQFA Layer-2 redistricting strategy
             verbatim, extended to a parallel speech-uncertainty regression.

             Treatment label per Hasan Section 5.1 verbatim:
                 "we take all firms located in a given congressional district
                  five years prior to redistricting and classify them into
                  three groups as per their RANKING of political risk. For
                  all firms located in the new districts, we use their
                  political risk ranking and then repeat the process as
                  measured over the five years preceding the redistricting."
                 "Treated is a categorical variable, ranging from +1 to -1.
                  +1 if firm-level political risk has increased due to
                  congressional redistricting, zero if political risk has
                  remained unchanged, and -1 if political risk has decreased
                  due to redistricting. After, an indicator variable, equals
                  to 1 after 2011, and 0 otherwise."

             Two parallel regressions per FE configuration:
                 Run 1: CashRatio   = b * DiD_Redist + ctrls + FE + e
                 Run 2: UncResCEO_c = b * DiD_Redist + ctrls + FE + e

Tail directions:
    DiD_Redist on CashRatio:    one-tail POS
    DiD_Redist on UncResCEO_c:  one-tail POS  (extension of Hasan to speech)
    Treated_redist level:       two-tailed (absorbed by firm FE)
    Post_redist level:          two-tailed (absorbed by year/YQ FE)

Channel: CH-Redistrict — Plausibly-exogenous shift in firm's political-
    representation profile via 2011 court-settled congressional redistricting.

Anchor: Hasan, Alam, Paramati & Islam (2022) RQFA — Layer 2 of their 4-layer
    endogeneity ladder. Extension: parallel speech regression (their study
    uses cash only).

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet
    - outputs/econometric/ceo_clarity_extended/<latest>/ceo_clarity_residual.parquet
    - inputs/Census_CD_Crosswalks/zcta_cd111_rel_10.txt (PRE map; weighted)
    - inputs/Census_CD_Crosswalks/natl_zccd_delim_113.txt (POST map; unweighted)
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet (addzip per gvkey-q)
    - inputs/FirmLevelRisk/firmquarter_2022q1.csv (PRisk overall)

Outputs:
    - outputs/econometric/h1_6_redistricting_did/{timestamp}/
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
from f1d.shared.variables import RedistrictingTreatmentBuilder
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

# Single key IV — DiD treatment (Treated_redist * Post_redist).
KEY_IV = "DiD_Redist"
LEVEL_DUMMIES = ["Treated_redist", "Post_redist"]

# F1D canonical controls — Lagged_DV REMOVED 2026-05-06 LATE EVENING per
# Hasan 2022 NLM-verified verbatim spec (Q11d + Q12e: "NO LAGGED DEPENDENT
# VARIABLE IN ANY HASAN 2022 SPECIFICATION"). Rule `feedback_lagged_dv.md`
# overridden for H1.6 ONLY; H1 main panel + all other suites unaffected.
# Rationale: H1.6 = exogenous-shock DiD layer aiming to capture cumulative
# response post-redistricting; Lagged_DV (β=0.864 in prior run) absorbed
# 35-54 percentage points of cash variance, leaving DiD to fit only the
# residual after AR(1) — wrong-sign null result. Replication discipline
# requires matching Hasan's verbatim Eq.2 control set.
CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO",
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
]

DISPLAY_IVS = [KEY_IV] + LEVEL_DUMMIES

IV_TAIL_DIRECTION: Dict[str, str] = {
    KEY_IV:           "positive",
    "Treated_redist": "none",
    "Post_redist":    "none",
}

VARIABLE_LABELS = {
    KEY_IV:           r"Treated $\times$ Post (DiD)",
    "Treated_redist": r"Treated (rank shift, $+1/0/-1$)",
    "Post_redist":    "Post (year > 2011)",
}

MIN_CALLS_PER_FIRM = 3
YEAR_MIN = 2006   # Hasan: 5 years preceding 2011
YEAR_MAX = 2015   # cutoff before Trump 2016 contamination

SUITE_ID = "H1.6.redistricting_did"
SUITE_DIR_NAME = "h1_6_redistricting_did"
SUITE_TITLE = (
    "Redistricting Difference-in-Differences: Cash Holdings and CEO Speech "
    "Uncertainty (Firm-Rank Within Congressional District; Hasan 2022 RQFA)"
)
SUITE_CAPTION = (
    r"H1.6 Redistricting DiD: Cash $+$ UncResCEO $\sim$ Treated$_{redist}$ "
    r"$\times$ Post(2011); F1D canonical controls; firm-clustered SEs"
)
SUITE_LABEL = "tab:h1_6_redistricting_did"
SAMPLE_LABEL = (
    "Main sample (excludes financial and utility firms). 2006-2015 (5-year pre-window "
    "per Hasan 2022 plus post-2011 redistricting effective period; cut at 2015 to avoid "
    "Trump 2016 contamination). Treated$_{redist}$ assigned per Hasan 2022 Section 5.1 "
    "verbatim methodology: firm-rank tertile within congressional district before vs "
    "after 2011 redistricting (PRE district = 111th-Congress map; POST district = "
    "113th-Congress map). Post = 1 if year > 2011 (Hasan verbatim)."
)
HYP_DIR = "positive"
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}
EXTENDED_ONLY_CONTROLS: List[str] = []

# 8 model specs: 4 FE x 2 DVs (Cash + Speech).
MODEL_SPECS: List[Dict[str, Any]] = [
    {"col": 1, "dv": "CashRatio",   "fe": "industry",    "extra_controls": []},
    {"col": 2, "dv": "CashRatio",   "fe": "firm",        "extra_controls": []},
    {"col": 3, "dv": "CashRatio",   "fe": "industry_yq", "extra_controls": []},
    {"col": 4, "dv": "CashRatio",   "fe": "firm_yq",     "extra_controls": []},
    {"col": 5, "dv": "UncResCEO_c", "fe": "industry",    "extra_controls": []},
    {"col": 6, "dv": "UncResCEO_c", "fe": "firm",        "extra_controls": []},
    {"col": 7, "dv": "UncResCEO_c", "fe": "industry_yq", "extra_controls": []},
    {"col": 8, "dv": "UncResCEO_c", "fe": "firm_yq",     "extra_controls": []},
]

DV_TEX = {
    "CashRatio":    r"Cash$_t$",
    "UncResCEO_c":  r"UncResCEO$_t$",
}

SUMMARY_STATS_VARS = [
    {"col": "CashRatio",         "label": "Cash Holdings"},
    {"col": "UncResCEO",         "label": "UncResCEO (raw)"},
    {"col": "UncResCEO_c",       "label": "UncResCEO (centered)"},
    {"col": KEY_IV,              "label": r"Treated $\times$ Post (DiD)"},
    {"col": "Treated_redist",    "label": "Treated (+1/0/-1)"},
    {"col": "Post_redist",       "label": "Post (year > 2011)"},
    {"col": "prisk_5yr_pre_mean", "label": "PRisk (5-yr pre, mean)"},
    {"col": "Leverage",          "label": "Leverage"},
    {"col": "lnAssets",          "label": "Firm Size (log AT)"},
    {"col": "TobinsQ",           "label": "Tobin's Q"},
    {"col": "ROA",               "label": "ROA"},
    {"col": "Capex",             "label": "CapEx / Assets"},
    {"col": "DivDummy",          "label": "Dividend Payer"},
    {"col": "sCFO",              "label": "OCF Volatility"},
    {"col": "SalesGrowth",       "label": "Sales Growth"},
    {"col": "RDSales",           "label": r"R\&D Intensity"},
    {"col": "CashFlowAt",        "label": "Cash Flow"},
    {"col": "DailyVola",         "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H1.6 Redistricting DiD (Cash + Speech)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(
    root_path: Path, panel_path: Optional[str] = None,
) -> Tuple[pd.DataFrame, Path]:
    print("\n" + "=" * 60)
    print("Loading H1 panel + DWZ UncResCEO")
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
        "file_name",
        "gvkey", "ceo_id", "year", "fyearq_int", "ff12_code", "start_date",
        "CashRatio", "CashRatio_lag",
        *[c for c in CONTROLS if c != "Lagged_DV"],
    ]
    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  H1 panel: {panel_file}")
    print(f"  H1 rows:  {len(panel):,}")

    full_dir = get_latest_output_dir(
        root_path / "outputs" / "econometric" / "ceo_clarity_extended",
        required_file="ceo_clarity_residual.parquet",
    )
    full_resid = pd.read_parquet(
        full_dir / "ceo_clarity_residual.parquet",
        columns=["file_name", "UncResCEO"],
    )
    panel = panel.merge(full_resid, on="file_name", how="left", validate="one_to_one")

    panel = build_cal_yr_qtr_index(panel)
    return panel, panel_file


def load_and_merge_redist(
    panel: pd.DataFrame, root_path: Path, years: range,
) -> pd.DataFrame:
    """Merge redistricting treatment (Treated_redist, Post_redist, DiD_Redist)."""
    print("\n" + "=" * 60)
    print("Merging Redistricting DiD treatment label")
    print("=" * 60)

    builder = RedistrictingTreatmentBuilder({})
    result = builder.build(years, root_path)
    redist_df = result.data

    before = len(panel)
    panel = panel.merge(redist_df, on="file_name", how="left", validate="one_to_one")
    assert len(panel) == before, "Redist merge changed row count"

    n_pos = int((panel["Treated_redist"] == 1).sum())
    n_zero = int((panel["Treated_redist"] == 0).sum())
    n_neg = int((panel["Treated_redist"] == -1).sum())
    n_nan = int(panel["Treated_redist"].isna().sum())
    print(
        f"  Per-call merge: +1={n_pos:,}  0={n_zero:,}  -1={n_neg:,}  "
        f"NaN={n_nan:,}"
    )

    return panel


def center_speech_iv(
    panel: pd.DataFrame, sample_mask: pd.Series,
) -> Tuple[pd.DataFrame, float]:
    print("\n" + "=" * 60)
    print("Centering UncResCEO on Main sample")
    print("=" * 60)
    iv_main = panel.loc[sample_mask, "UncResCEO"].dropna()
    mu = float(iv_main.mean())
    panel = panel.copy()
    panel["UncResCEO_c"] = panel["UncResCEO"] - mu
    print(f"  Main obs: {len(iv_main):,}  raw mean: {mu:+.6f}")
    return panel, mu


def attach_speech_lag(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["gvkey", "cal_yr_qtr", "start_date"], kind="stable").copy()
    panel["UncResCEO_c_lag"] = panel.groupby("gvkey", sort=False)[
        "UncResCEO_c"
    ].shift(1)
    return panel


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,}")
    return main


def filter_sample_window(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to 2006-2015 (5y pre Hasan + 4y post-2011 + cutoff before Trump)."""
    before = len(panel)
    keep = panel["year"].between(YEAR_MIN, YEAR_MAX)
    panel = panel[keep].copy()
    print(f"  Sample window {YEAR_MIN}-{YEAR_MAX}: "
          f"{len(panel):,} / {before:,} (dropped {before - len(panel):,})")
    return panel


def filter_treated_labelled(panel: pd.DataFrame) -> pd.DataFrame:
    """Keep firms with a non-NaN Treated_redist label (excludes 113-CW failures)."""
    before = len(panel)
    keep = panel["Treated_redist"].notna()
    panel = panel[keep].copy()
    print(f"  Treated-labelled: {len(panel):,} / {before:,}")
    return panel


# ==============================================================================
# Regression
# ==============================================================================


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any],
) -> pd.DataFrame:
    dv = spec["dv"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"

    if dv == "CashRatio":
        lag_col = "CashRatio_lag"
    elif dv == "UncResCEO_c":
        lag_col = "UncResCEO_c_lag"
    else:
        raise ValueError(f"Unknown DV: {dv}")
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    required = (
        [dv, KEY_IV, "Treated_redist", "Post_redist"]
        + all_controls
        + ["gvkey", time_col, "ff12_code"]
    )
    miss = [c for c in required if c not in panel.columns]
    if miss:
        raise ValueError(f"Missing cols: {miss}")

    df = panel.copy().replace([np.inf, -np.inf], np.nan)
    before_dv = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before_dv:,}")

    complete = df[required].notna().all(axis=1)
    df = df[complete].copy()
    print(f"  After complete cases: {len(df):,}")

    fc = df["gvkey"].value_counts()
    df = df[df["gvkey"].isin(fc[fc >= MIN_CALLS_PER_FIRM].index)].copy()

    n_firms = df["gvkey"].nunique()
    n_periods = df.groupby(["gvkey", time_col]).ngroups
    n_pos_pre = int(((df["Treated_redist"] == 1) & (df["Post_redist"] == 0)).sum())
    n_pos_post = int(((df["Treated_redist"] == 1) & (df["Post_redist"] == 1)).sum())
    n_zero_pre = int(((df["Treated_redist"] == 0) & (df["Post_redist"] == 0)).sum())
    n_zero_post = int(((df["Treated_redist"] == 0) & (df["Post_redist"] == 1)).sum())
    n_neg_pre = int(((df["Treated_redist"] == -1) & (df["Post_redist"] == 0)).sum())
    n_neg_post = int(((df["Treated_redist"] == -1) & (df["Post_redist"] == 1)).sum())
    print(
        f"  After >={MIN_CALLS_PER_FIRM} calls/firm: {len(df):,} calls, "
        f"{n_firms:,} firms, {n_periods:,} firm-time periods"
    )
    print(
        f"  Treated x Post cell counts (calls):\n"
        f"        Pre   Post\n"
        f"   +1: {n_pos_pre:>5,d}  {n_pos_post:>5,d}\n"
        f"    0: {n_zero_pre:>5,d}  {n_zero_post:>5,d}\n"
        f"   -1: {n_neg_pre:>5,d}  {n_neg_post:>5,d}"
    )

    return df


def _fit_one(df_panel: pd.DataFrame, dv: str, exog: List[str], base_fe: str) -> Any:
    if base_fe == "industry":
        m = PanelOLS(
            dependent=df_panel[dv],
            exog=df_panel[exog],
            entity_effects=False,
            time_effects=True,
            other_effects=df_panel["ff12_code"],
            drop_absorbed=True,
            check_rank=False,
        )
        return m.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
    else:
        formula = f"{dv} ~ 1 + " + " + ".join(exog) + " + EntityEffects + TimeEffects"
        m = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        return m.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)


def _stash_iv_to_meta(meta: Dict[str, Any], model: Any, iv: str) -> None:
    if iv not in model.params.index:
        meta[f"{iv}_beta"] = np.nan
        meta[f"{iv}_se"] = np.nan
        meta[f"{iv}_t"] = np.nan
        meta[f"{iv}_p_one"] = np.nan
        return
    beta = float(model.params[iv])
    se = float(model.std_errors[iv])
    p_two = float(model.pvalues[iv])
    t_stat = float(model.tstats[iv])
    if not np.isnan(p_two) and not np.isnan(beta):
        d = IV_TAIL_DIRECTION.get(iv, "positive")
        if d == "positive":
            p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
        elif d == "negative":
            p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
        else:
            p_one = p_two
    else:
        p_one = np.nan
    meta[f"{iv}_beta"] = beta
    meta[f"{iv}_se"] = se
    meta[f"{iv}_t"] = t_stat
    meta[f"{iv}_p_one"] = p_one
    stars = "***" if p_one < 0.01 else ("**" if p_one < 0.05 else ("*" if p_one < 0.10 else ""))
    print(f"    {iv:30s}: beta={beta:+.4f}  SE={se:.4f}  p={p_one:.4f} {stars}")


def run_regression(
    df_prep: pd.DataFrame, spec: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    dv = spec["dv"]
    col_num = spec["col"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"
    base_fe = fe.replace("_yq", "")
    fe_label = (
        f"{'Firm' if base_fe == 'firm' else 'Industry(FF12)'}"
        f" + {'CalYrQtr' if fe.endswith('_yq') else 'CalYear'}"
    )

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_label}")
    print(f"{'=' * 60}")

    if len(df_prep) < 100:
        print(f"  Too few obs ({len(df_prep)}); skipping")
        return None, {}

    exog = [KEY_IV] + LEVEL_DUMMIES + all_controls

    n_firms = df_prep["gvkey"].nunique()
    n_periods = df_prep.groupby(["gvkey", time_col]).ngroups
    print(f"  N={len(df_prep):,}, firms={n_firms:,}")

    df_panel = df_prep.set_index(["gvkey", time_col])

    t0 = datetime.now()
    try:
        model = _fit_one(df_panel, dv, exog, base_fe)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}
    elapsed = (datetime.now() - t0).total_seconds()

    print(f"  [OK] in {elapsed:.1f}s | R^2={model.rsquared:.4f} | N={int(model.nobs):,}")

    meta: Dict[str, Any] = {
        "col": col_num, "dv": dv, "fe": fe,
        "n_obs": int(model.nobs), "n_firms": n_firms, "n_time_periods": n_periods,
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / max(model.df_resid, 1),
        "dv_mean": float(model.model.dependent.dataframe.mean().iloc[0]),
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
        "sample_window": f"{YEAR_MIN}-{YEAR_MAX}",
    }

    print("  Display IV coefs:")
    for iv in DISPLAY_IVS:
        _stash_iv_to_meta(meta, model, iv)

    return model, meta


# ==============================================================================
# Output (LaTeX + suite_spec)
# ==============================================================================


def _sig_stars_one(p: float) -> str:
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    results_by_col = {r["meta"]["col"]: r["meta"] for r in all_results if r.get("meta")}

    def fmt_coef(v: float, st: str) -> str:
        return "" if np.isnan(v) else f"{v:.4f}{st}"

    def fmt_se(v: float) -> str:
        return "" if np.isnan(v) else f"({v:.4f})"

    def fmt_r2(v: float) -> str:
        if np.isnan(v): return ""
        if abs(v) < 0.001: return f"{v:.2e}"
        return f"{v:.3f}"

    display_cols = [1, 2, 3, 4, 5, 6, 7, 8]
    metas = [results_by_col.get(c, {}) for c in display_cols]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{" + SUITE_CAPTION + r"}",
        r"\label{" + SUITE_LABEL + r"}",
        r"\scriptsize",
        r"\begin{tabular}{l" + "c" * 8 + "}",
        r"\toprule",
        " & " + " & ".join(f"({i})" for i in range(1, 9)) + r" \\",
        r" & \multicolumn{4}{c}{Cash Holdings} & \multicolumn{4}{c}{UncResCEO} \\",
        r"\cmidrule(lr){2-5} \cmidrule(lr){6-9}",
        r"\midrule",
    ]
    for iv in DISPLAY_IVS:
        label = VARIABLE_LABELS.get(iv, iv).replace("_", r"\_")
        d = IV_TAIL_DIRECTION.get(iv, "positive")
        stars_fn = _sig_stars_one if d != "none" else _sig_stars_one
        # both use same thresholds; direction stored in meta p_one
        parts_b, parts_se = [], []
        for m in metas:
            beta = m.get(f"{iv}_beta", np.nan)
            p_one = m.get(f"{iv}_p_one", np.nan)
            parts_b.append(fmt_coef(beta, stars_fn(p_one)))
            parts_se.append(fmt_se(m.get(f"{iv}_se", np.nan)))
        lines.append(f"{label} & {' & '.join(parts_b)} \\\\")
        lines.append(f" & {' & '.join(parts_se)} \\\\")

    lines.append(r"\midrule")
    lines.append(r"Controls & " + " & ".join(["F1D"] * 8) + r" \\")
    ind_cells = ["Yes" if results_by_col.get(c, {}).get("fe", "").startswith("industry") else "" for c in display_cols]
    firm_cells = ["Yes" if results_by_col.get(c, {}).get("fe", "").startswith("firm") else "" for c in display_cols]
    yr_cells = ["Yes" if not results_by_col.get(c, {}).get("fe", "").endswith("_yq") else "" for c in display_cols]
    yq_cells = ["Yes" if results_by_col.get(c, {}).get("fe", "").endswith("_yq") else "" for c in display_cols]
    lines.append(r"Industry FE & " + " & ".join(ind_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_cells) + r" \\")
    lines.append(r"Calendar Year FE & " + " & ".join(yr_cells) + r" \\")
    lines.append(r"Calendar Year-Quarter FE & " + " & ".join(yq_cells) + r" \\")
    lines.append(r"\midrule")
    n_row = " & ".join(f"{m.get('n_obs', 0):,}" for m in metas)
    lines.append(f"N (calls) & {n_row} \\\\")
    r2_row = " & ".join(fmt_r2(m.get("r2", np.nan)) for m in metas)
    lines.append(f"$R^2$ & {r2_row} \\\\")
    ar2_row = " & ".join(fmt_r2(m.get("adj_r2", np.nan)) for m in metas)
    lines.append(f"Adj.~$R^2$ & {ar2_row} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"Difference-in-differences exploiting the 2010-Census federal congressional ",
        r"redistricting (settled in court 2011, effective 2013 with the 113th Congress) as a ",
        r"plausibly-exogenous shift in firms' political-representation profile. Treatment label ",
        r"per Hasan, Alam, Paramati \& Islam (2022) Section 5.1 verbatim: firm-rank tertile ",
        r"within HQ congressional district before vs after 2011 redistricting. PRE district = ",
        r"111th-Congress map (2002 boundaries); POST district = 113th-Congress map (2010 boundaries). ",
        r"Treated $=+1$ if firm's PRisk-rank tertile within district increased post-redistricting, ",
        r"$0$ if unchanged, $-1$ if decreased. Post $= 1$ if year $> 2011$. ",
        r"Cash $=$ cheq/atq (Bates 2009 form). UncResCEO $=$ DWZ (2021) Eq.5 within-quarter residual ",
        r"of CEO Q\&A uncertainty (centered on Main sample). Speech regression extends Hasan's ",
        r"cash-only design. ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for DiD; two-tailed for level dummies). ",
        r"Standard errors (in parentheses) firm-level clustered. Main sample (excludes financial and utility firms). ",
        r"Sample 2006--2015 (5-yr Hasan pre-window plus post-2011 effective period; capped at 2015 to avoid Trump 2016 contamination). ",
        r"113th-CD ZCTA crosswalk is unweighted (Census did not publish a population-weighted version); ",
        r"ZCTAs spanning multiple 113th CDs assigned to first-listed CD per ZCTA.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_6_redistricting_did_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: {tex_path.name}")


def save_outputs(all_results: List[Dict[str, Any]], out_dir: Path) -> pd.DataFrame:
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
            f.write("H1.6 Redistricting DiD\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"Key IV: {KEY_IV} (one-tail POS)\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Sample window: {meta.get('sample_window', '')}\n")
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


def _write_suite_spec_json(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    results_by_col = {r["meta"]["col"]: r for r in all_results if r.get("meta")}
    col_metadata, coefs_per_col = [], []
    display_cols = [1, 2, 3, 4, 5, 6, 7, 8]
    for col in display_cols:
        if col not in results_by_col:
            raise RuntimeError(f"H1.6 spec build: missing result for col {col}")
        entry = results_by_col[col]
        model = entry["model"]
        meta = entry["meta"]
        spec = next(s for s in MODEL_SPECS if s["col"] == col)
        fe = spec["fe"]
        base_fe = fe.replace("_yq", "")
        fe_entity = "industry" if base_fe == "industry" else "firm"
        fe_time = ("calendar_year_quarter" if fe.endswith("_yq") else "calendar_year")
        extra_controls = spec.get("extra_controls", [])
        control_vars = list(CONTROLS) + list(extra_controls)
        try:
            dv_mean = float(model.model.dependent.dataframe.mean().iloc[0])
        except Exception:
            dv_mean = None
        col_metadata.append({
            "col": len(col_metadata) + 1,
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
        })
        merged_coefs: Dict[str, Dict[str, Any]] = {}
        for direction in ("positive", "none"):
            ivs_for_dir = [
                ivc for ivc in DISPLAY_IVS
                if IV_TAIL_DIRECTION.get(ivc, "none") == direction
            ]
            if not ivs_for_dir:
                continue
            coefs = extract_coefs_panelols(
                model=model,
                key_ivs=ivs_for_dir,
                all_vars=list(DISPLAY_IVS),
                hyp_dir=direction,
            )
            for ivc in ivs_for_dir:
                if ivc in coefs:
                    merged_coefs[ivc] = coefs[ivc]
        control_coefs = extract_coefs_panelols(
            model=model, key_ivs=[], all_vars=control_vars, hyp_dir="none",
        )
        merged_coefs.update(control_coefs)
        coefs_per_col.append(merged_coefs)

    ivs = [
        {
            "name": iv,
            "label": VARIABLE_LABELS.get(iv, iv).replace("_", r"\_"),
            "tail": (
                "two" if IV_TAIL_DIRECTION.get(iv, "none") == "none"
                else "one_neg" if IV_TAIL_DIRECTION.get(iv) == "negative"
                else "one_pos"
            ),
        }
        for iv in DISPLAY_IVS
    ]

    header_rows = [[
        {"label": "Cash Holdings", "span": 4},
        {"label": "UncResCEO", "span": 4},
    ]]

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
                "col_range": list(range(1, len(col_metadata) + 1)),
                "header_rows": header_rows,
                "suite_type": "standard",
            }
        ],
        coefs_per_col=coefs_per_col,
        col_metadata=col_metadata,
        sample_label=SAMPLE_LABEL,
        clustering=CLUSTERING,
        tail=TAIL,
        ivs=ivs,
        controls={"base": list(CONTROLS), "extended_only": list(EXTENDED_ONLY_CONTROLS)},
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


def generate_report(
    all_results: List[Dict[str, Any]], out_dir: Path,
    duration: float, iv_means: Dict[str, float],
) -> None:
    iv_means_str = ", ".join(f"{k}={v:+.4f}" for k, v in iv_means.items())
    lines = [
        "# H1.6 Redistricting DiD on Cash + Speech",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Design:** Cash + UncResCEO ~ DiD_Redist + Treated_redist + Post + ctrls + FE",
        f"**Sample window:** {YEAR_MIN}–{YEAR_MAX}",
        f"**Treatment:** Hasan 2022 firm-rank-tertile within congressional district (PRE 111th-CD vs POST 113th-CD)",
        f"**Pre-window for PRisk firm-mean:** 2006q1–2010q4 (5 years preceding 2011 redistricting)",
        f"**Post:** year > 2011 (Hasan verbatim)",
        f"**Centering:** UncResCEO -> UncResCEO_c (Main sample mean = {iv_means_str})",
        "",
        "## Results",
        "",
        "| Col | DV | FE | DiD beta | p_one | N | R2 |",
        "|-----|----|----|----------|-------|---|-----|",
    ]
    for r in all_results:
        m = r.get("meta", {})
        if not m:
            continue
        b = m.get(f"{KEY_IV}_beta", np.nan)
        p = m.get(f"{KEY_IV}_p_one", np.nan)
        s = _sig_stars_one(p) if not np.isnan(p) else ""
        lines.append(
            f"| ({m['col']}) | {m['dv']} | {m['fe']} | "
            f"{b:+.4f}{s} | {p:.3f} | {m['n_obs']:,} | {m['r2']:.4f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- DiD positive on CashRatio: redistricting-induced firm-rank shift activates precautionary cash",
        "- DiD positive on UncResCEO: redistricting shock activates speech-uncertainty for treated firms (NEW)",
        "- Joint positivity = strongest support for Story B indicator-state framing",
        "- Both null: indicator-state story not detected via redistricting variation",
        "- Hasan's design = our PRE 111th-CD map ZCTA-CD weighted; POST 113th-CD map ZCTA-CD unweighted (CD-spanning ZCTAs assigned first-listed CD)",
    ]
    with open(out_dir / "report_step4_H1_6_redistricting_did.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H1_6_redistricting_did.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / SUITE_DIR_NAME / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H1_6_Redistricting_DiD",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H1.6 REDISTRICTING DiD ON CASH + SPEECH (HASAN 2022 LAYER 2)")
    print("=" * 80)
    print(f"Timestamp:    {timestamp}")
    print(f"Output:       {out_dir}")
    print(f"Design:       8 specs (4 FE x 2 DVs); single key IV = DiD_Redist")
    print(f"Channel:      CH-Redistrict — 2010-Census redistricting shock to firm CD profile")
    print(f"Sample:       {YEAR_MIN}-{YEAR_MAX}  (Hasan 5y pre + post-2011 + cutoff before Trump)")
    print(f"Post:         year > 2011 (Hasan 2022 NLM-verified verbatim)")
    print(f"Tail:         DiD_Redist POS one-tail; level dummies two-tail")

    panel, panel_file = load_panel(root, panel_path)
    panel = load_and_merge_redist(panel, root, years=range(2002, 2019))

    panel = filter_sample_window(panel)

    main_mask = ~panel["ff12_code"].isin([8, 11])
    panel, mu_uncres = center_speech_iv(panel, main_mask)
    iv_means = {"UncResCEO": mu_uncres}

    panel = attach_speech_lag(panel)

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)
    panel = filter_treated_labelled(panel)
    tc_n = len(panel)

    print(
        f"\n  Main+TC: {tc_n:,} calls, {panel['gvkey'].nunique():,} firms"
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption=f"Summary Statistics --- H1.6 Redistricting DiD (Main+TC, {YEAR_MIN}-{YEAR_MAX})",
        label="tab:summary_stats_h1_6_redistricting_did",
    )
    print("  Saved: summary_stats.csv/.tex")

    all_results: List[Dict[str, Any]] = []
    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} | FE={spec['fe']} ---")
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

    if all_results:
        first = all_results[0]["meta"]
        attrition_stages = [
            ("Full panel (H1)", 112968),
            (f"Sample window {YEAR_MIN}-{YEAR_MAX}", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("Treated-labelled (non-NaN Treated_redist)", tc_n),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(
            attrition_stages, out_dir, "H1.6 Redistricting DiD",
        )
        print("  Saved: sample_attrition.csv/.tex")

    input_paths = {
        "panel": panel_file,
        "compustat_addzip": root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
        "prisk_overall": root / "inputs" / "FirmLevelRisk" / "firmquarter_2022q1.csv",
        "cw_111": root / "inputs" / "Census_CD_Crosswalks" / "zcta_cd111_rel_10.txt",
        "cw_113": root / "inputs" / "Census_CD_Crosswalks" / "natl_zccd_delim_113.txt",
    }
    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths=input_paths,
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_results, out_dir, duration, iv_means)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")
    print("\nDiD_Redist significance summary (one-tail POS, p<0.05):")
    for r in all_results:
        m = r["meta"]
        b = m.get(f"{KEY_IV}_beta", np.nan)
        p = m.get(f"{KEY_IV}_p_one", np.nan)
        sig = "SIG" if (not np.isnan(p) and not np.isnan(b) and b > 0 and p < 0.05) else "ns"
        print(
            f"  Col ({m['col']}) DV={m['dv']:14s} FE={m['fe']:14s} "
            f"beta={b:+.4f}  p_one={p:.3f}  [{sig}]"
        )
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main(panel_path=args.panel_path))
