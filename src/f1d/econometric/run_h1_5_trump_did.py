#!/usr/bin/env python3
"""
================================================================================
STAGE 4: H1.5 Trump 2016 DiD on Cash + Speech (BothHigh trade x tax design)
================================================================================
ID: econometric/run_h1_5_trump_did
Description: Difference-in-differences design exploiting the November 2016 Trump
             election as a plausibly-exogenous shock to firm political-risk
             exposure. Treatment = "BothHigh" trade x tax exposure (mean
             PRiskT_trade and mean PRiskT_tax both above FF12-industry-own
             median over the 5-year pre-window 2011q4-2016q3).

             Two parallel regressions per FE configuration (Story B framing):
               Run 1: CashRatio = beta * DiD_Trump + ctrls + FE + e
               Run 2: UncResCEO_c = beta * DiD_Trump + ctrls + FE + e

             beta on cash = treatment effect on precautionary holdings.
             beta on speech = treatment effect on speech-uncertainty (NEW
             contribution; speech as joint indicator under Trump shock).

             Both POSITIVE betas would support the "joint indicator" story:
             Trump shock activates precautionary state -> BOTH cash UP AND
             speech-uncertainty UP for firms exposed on both Trump levers.

Tail directions:
    DiD_Trump on CashRatio:    one-tail POS  (treatment increases cash)
    DiD_Trump on UncResCEO_c:  one-tail POS  (treatment increases speech unc)
    BothHigh level dummy:      two-tailed (no directional prior; absorbed by firm FE)
    Post_trump level dummy:    two-tailed (no directional prior; absorbed by YQ FE)

Channel:
    CH-Trump2016 — Plausibly-exogenous political-risk shock from Trump's
    election. Treatment population: firms with both high trade exposure
    (tariff lever) and high tax exposure (TCJA lever).

Anchor: Hu, Kang, Li & Lin (2024) RAST — Trump 2016 DiD template; ours
    differs by treatment definition (firm exposure to Trump's specific
    levers, not minority-CEO status), DV stack (cash + speech, not Q&A
    pessimism), and panel scope (whole F1D universe, not S&P 500).

Model Specification:
    DV ~ b1*DiD_Trump + b2*BothHigh + b3*Post_trump
       + 12 F1D canonical controls + FE + e

8 Models (8 displayed):
    Block 1 (cols 1-4): DV = CashRatio
    Block 2 (cols 5-8): DV = UncResCEO_c

FE Ladder (per col within block):
    industry        Industry FF12 + CalendarYear (TimeEffects via PanelOLS)
    firm            Firm + CalendarYear
    industry_yq     Industry FF12 + CalendarYearQuarter
    firm_yq         Firm + CalendarYearQuarter (canonical TWFE-DiD)

Sample: Main (FF12 not in {8 Utility, 11 Finance}). Q3 2014 - Q4 2018
    (Hu 2024 cutoff window). BothHigh OR BothLow firms only — off-diagonal
    (HighTrade-LowTax + LowTrade-HighTax) DROPPED at runner.

Unit: Call-level. Panel index: ["gvkey", "cal_yr"] or ["gvkey", "cal_yr_qtr"].
SEs: Firm-clustered (matches H1.3 + H1.0 convention).

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet
    - outputs/econometric/ceo_clarity_extended/<latest>/ceo_clarity_residual.parquet
    - inputs/FirmLevelRisk/firmquarter_2022q1.csv (via PRiskSubtopicsBuilder)

Outputs:
    - outputs/econometric/h1_5_trump_did/{timestamp}/
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
from f1d.shared.variables import TrumpDiDTreatmentBuilder
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

# Single key IV — DiD treatment indicator (BothHigh * Post_trump).
KEY_IV = "DiD_Trump"
LEVEL_DUMMIES = ["BothHigh", "Post_trump"]  # absorbed by FE in some specs

# F1D canonical 12-var controls (matches H1.3 cfvol moderation runner verbatim).
# Lagged_DV is dynamic per DV (CashRatio_lag for cash spec; UncResCEO_c_lag for speech spec).
CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO",
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
    "Lagged_DV",
]

DISPLAY_IVS = [KEY_IV] + LEVEL_DUMMIES

IV_TAIL_DIRECTION: Dict[str, str] = {
    KEY_IV:        "positive",  # one-tail POS (treatment effect)
    "BothHigh":    "none",       # two-tailed (absorbed by firm FE in cols 2/4/6/8)
    "Post_trump":  "none",       # two-tailed (absorbed by YQ FE in cols 3/4/7/8)
}

VARIABLE_LABELS = {
    KEY_IV:        r"BothHigh $\times$ Post (DiD)",
    "BothHigh":    "BothHigh (Trade $\\times$ Tax)",
    "Post_trump":  "Post (Trump 2016)",
}

MIN_CALLS_PER_FIRM = 3   # Lower than H1.3 (=5) because shorter sample window Q3 2014 - Q4 2018.
YEAR_MIN = 2014
YEAR_MAX = 2018
# Sample period filter (cal_yr_qtr): Q3 2014 - Q4 2018 inclusive.
CAL_YR_QTR_MIN = 20143  # 2014 Q3
CAL_YR_QTR_MAX = 20184  # 2018 Q4

SUITE_ID = "H1.5.trump_did"
SUITE_DIR_NAME = "h1_5_trump_did"
SUITE_TITLE = (
    "Trump 2016 Difference-in-Differences: Cash Holdings and CEO Speech "
    "Uncertainty (BothHigh Trade x Tax Treatment; Hu 2024 RAST template)"
)
SUITE_CAPTION = (
    r"H1.5 Trump 2016 DiD: Cash $+$ UncResCEO $\sim$ "
    r"BothHigh $\times$ Post(2016q4); F1D canonical controls; firm-clustered SEs"
)
SUITE_LABEL = "tab:h1_5_trump_did"
SAMPLE_LABEL = (
    "Main sample (excludes financial and utility firms). Q3 2014--Q4 2018 "
    "(Hu 2024 RAST cutoff window). Treatment fixed pre-event over 2011q4-2016q3 "
    "via FF12-industry-own median split on PRiskT\\_trade and PRiskT\\_tax. "
    "BothHigh and BothLow firms only; off-diagonal cohorts dropped."
)
HYP_DIR = "positive"
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}
EXTENDED_ONLY_CONTROLS: List[str] = []

# 8 model specs: 4 FE x 2 DVs.
MODEL_SPECS: List[Dict[str, Any]] = [
    # Block 1: DV = CashRatio
    {"col": 1, "dv": "CashRatio",   "fe": "industry",    "extra_controls": []},
    {"col": 2, "dv": "CashRatio",   "fe": "firm",        "extra_controls": []},
    {"col": 3, "dv": "CashRatio",   "fe": "industry_yq", "extra_controls": []},
    {"col": 4, "dv": "CashRatio",   "fe": "firm_yq",     "extra_controls": []},
    # Block 2: DV = UncResCEO_c (centered residual; load-bearing speech novelty)
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
    {"col": "CashRatio",     "label": "Cash Holdings"},
    {"col": "UncResCEO",     "label": "UncResCEO (raw)"},
    {"col": "UncResCEO_c",   "label": "UncResCEO (centered)"},
    {"col": KEY_IV,          "label": r"BothHigh $\times$ Post (DiD)"},
    {"col": "BothHigh",      "label": r"BothHigh (Trade $\times$ Tax)"},
    {"col": "Post_trump",    "label": "Post (Trump 2016)"},
    {"col": "trade_pre_mean", "label": "PRiskT trade (pre, mean)"},
    {"col": "tax_pre_mean",   "label": "PRiskT tax (pre, mean)"},
    {"col": "Leverage",      "label": "Leverage"},
    {"col": "lnAssets",      "label": "Firm Size (log AT)"},
    {"col": "TobinsQ",       "label": "Tobin's Q"},
    {"col": "ROA",           "label": "ROA"},
    {"col": "Capex",         "label": "CapEx / Assets"},
    {"col": "DivDummy",      "label": "Dividend Payer"},
    {"col": "sCFO",          "label": "OCF Volatility"},
    {"col": "SalesGrowth",   "label": "Sales Growth"},
    {"col": "RDSales",       "label": r"R\&D Intensity"},
    {"col": "CashFlowAt",    "label": "Cash Flow"},
    {"col": "DailyVola",     "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H1.5 Trump 2016 DiD (Cash + Speech)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(
    root_path: Path, panel_path: Optional[str] = None
) -> Tuple[pd.DataFrame, Path]:
    """Load H1 panel + merge UncResCEO (DWZ Eq.5 residual)."""
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

    # Merge UncResCEO from DWZ Full residual parquet.
    full_dir = get_latest_output_dir(
        root_path / "outputs" / "econometric" / "ceo_clarity_extended",
        required_file="ceo_clarity_residual.parquet",
    )
    full_resid_file = full_dir / "ceo_clarity_residual.parquet"
    full_resid = pd.read_parquet(
        full_resid_file, columns=["file_name", "UncResCEO"]
    )
    panel = panel.merge(
        full_resid, on="file_name", how="left", validate="one_to_one"
    )
    n_unc = panel["UncResCEO"].notna().sum()
    print(
        f"  UncResCEO merge: {n_unc:,} non-null ({100*n_unc/len(panel):.1f}%)"
    )

    panel = build_cal_yr_qtr_index(panel)
    n_yq = panel["cal_yr_qtr"].notna().sum()
    print(
        f"  cal_yr_qtr coverage: {n_yq:,}/{len(panel):,} ({100*n_yq/len(panel):.1f}%)"
    )

    return panel, panel_file


def load_and_merge_did(
    panel: pd.DataFrame, root_path: Path, years: range
) -> pd.DataFrame:
    """Merge Trump DiD treatment (BothHigh, BothLow, Post_trump, DiD_Trump)."""
    print("\n" + "=" * 60)
    print("Merging Trump 2016 DiD treatment label")
    print("=" * 60)

    builder = TrumpDiDTreatmentBuilder({})
    result = builder.build(years, root_path)
    did_df = result.data

    before = len(panel)
    panel = panel.merge(did_df, on="file_name", how="left", validate="one_to_one")
    assert len(panel) == before, "DiD merge changed row count"

    n_bh = int((panel["BothHigh"] == 1).sum())
    n_bl = int((panel["BothLow"] == 1).sum())
    n_off = int(panel["BothHigh"].isna().sum())
    n_did1 = int((panel["DiD_Trump"] == 1).sum())
    print(
        f"  Per-call merge: BothHigh={n_bh:,} BothLow={n_bl:,} "
        f"off-diagonal={n_off:,}; DiD_Trump==1: {n_did1:,}"
    )

    return panel


def center_speech_iv(
    panel: pd.DataFrame, sample_mask: pd.Series
) -> Tuple[pd.DataFrame, float]:
    """Mean-center UncResCEO on Main sample (per H1.3 convention)."""
    print("\n" + "=" * 60)
    print("Centering UncResCEO on Main sample")
    print("=" * 60)
    iv_main = panel.loc[sample_mask, "UncResCEO"].dropna()
    mu = float(iv_main.mean())
    panel = panel.copy()
    panel["UncResCEO_c"] = panel["UncResCEO"] - mu
    print(f"  Main obs: {len(iv_main):,}  raw mean: {mu:+.6f}  "
          f"centered mean: {panel.loc[sample_mask, 'UncResCEO_c'].dropna().mean():+.6e}")
    return panel, mu


def attach_speech_lag(panel: pd.DataFrame) -> pd.DataFrame:
    """Compute UncResCEO_c_lag via groupby(gvkey).shift on cal_yr_qtr-sorted panel.

    Required for the speech regression's Lagged_DV control. F1D convention:
    Lagged_DV = base_dv shifted 1 quarter within firm. CashRatio has CashRatio_lag
    pre-merged in H1 panel; UncResCEO_c does not so we compute it here.
    """
    panel = panel.sort_values(["gvkey", "cal_yr_qtr", "start_date"], kind="stable").copy()
    panel["UncResCEO_c_lag"] = panel.groupby("gvkey", sort=False)[
        "UncResCEO_c"
    ].shift(1)
    n_lag = panel["UncResCEO_c_lag"].notna().sum()
    print(f"  UncResCEO_c_lag computed: {n_lag:,} non-null "
          f"({100*n_lag/len(panel):.1f}%)")
    return panel


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def filter_sample_window(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Hu 2024 cutoff window: Q3 2014 - Q4 2018."""
    before = len(panel)
    keep = panel["cal_yr_qtr"].between(CAL_YR_QTR_MIN, CAL_YR_QTR_MAX)
    panel = panel[keep].copy()
    print(f"  Sample window {CAL_YR_QTR_MIN}-{CAL_YR_QTR_MAX}: "
          f"{len(panel):,} / {before:,} (dropped {before - len(panel):,})")
    return panel


def filter_treated_control_only(panel: pd.DataFrame) -> pd.DataFrame:
    """Keep only BothHigh OR BothLow firms (drop off-diagonal cohort)."""
    before = len(panel)
    keep = panel["BothHigh"].notna()  # NaN means off-diagonal
    panel = panel[keep].copy()
    n_bh = int((panel["BothHigh"] == 1).sum())
    n_bl = int((panel["BothLow"] == 1).sum())
    print(f"  Treated/Control: {len(panel):,} / {before:,} "
          f"(BothHigh={n_bh:,} BothLow={n_bl:,})")
    return panel


# ==============================================================================
# Regression
# ==============================================================================


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any]
) -> pd.DataFrame:
    """Prepare data for one regression spec.

    DV-conditional Lagged_DV mapping:
      CashRatio    -> CashRatio_lag (pre-merged in H1 panel)
      UncResCEO_c  -> UncResCEO_c_lag (computed in attach_speech_lag)
    """
    dv = spec["dv"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"

    # Lagged_DV: CashRatio_lag (pre-merged) or UncResCEO_c_lag (computed).
    if dv == "CashRatio":
        lag_col = "CashRatio_lag"
    elif dv == "UncResCEO_c":
        lag_col = "UncResCEO_c_lag"
    else:
        raise ValueError(f"Unknown DV for Lagged_DV mapping: {dv}")

    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    required = (
        [dv, KEY_IV, "BothHigh", "Post_trump"]
        + all_controls
        + ["gvkey", time_col, "ff12_code"]
    )
    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    before_dv = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before_dv:,}")

    complete = df[required].notna().all(axis=1)
    df = df[complete].copy()
    print(f"  After complete cases: {len(df):,}")

    firm_counts = df["gvkey"].value_counts()
    keep_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(keep_firms)].copy()

    n_firms = df["gvkey"].nunique()
    n_periods = df.groupby(["gvkey", time_col]).ngroups
    n_treated = int((df[KEY_IV] == 1).sum())
    n_control_pre = int(((df["BothHigh"] == 0) & (df["Post_trump"] == 0)).sum())
    n_control_post = int(((df["BothHigh"] == 0) & (df["Post_trump"] == 1)).sum())
    n_treat_pre = int(((df["BothHigh"] == 1) & (df["Post_trump"] == 0)).sum())
    print(
        f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
        f"{len(df):,} calls, {n_firms:,} firms, {n_periods:,} firm-time periods"
    )
    print(
        f"  2x2 cell counts: BothLow-Pre={n_control_pre:,}  BothLow-Post={n_control_post:,}  "
        f"BothHigh-Pre={n_treat_pre:,}  BothHigh-Post={n_treated:,}"
    )

    return df


def _fit_one(df_panel: pd.DataFrame, dv: str, exog: List[str], base_fe: str) -> Any:
    """Single PanelOLS fit. Industry FE via other_effects; Firm FE via from_formula."""
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
        return model_obj.fit(
            cov_type="clustered", cluster_entity=True, cluster_time=False
        )
    else:  # firm
        exog_str = " + ".join(exog)
        formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
        model_obj = PanelOLS.from_formula(
            formula, data=df_panel, drop_absorbed=True
        )
        return model_obj.fit(
            cov_type="clustered", cluster_entity=True, cluster_time=False
        )


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
        direction = IV_TAIL_DIRECTION.get(iv, "positive")
        if direction == "positive":
            p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
        elif direction == "negative":
            p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
        else:
            p_one = p_two
    else:
        p_one = np.nan

    meta[f"{iv}_beta"] = beta
    meta[f"{iv}_se"] = se
    meta[f"{iv}_t"] = t_stat
    meta[f"{iv}_p_one"] = p_one

    stars = (
        "***" if p_one < 0.01
        else ("**" if p_one < 0.05 else ("*" if p_one < 0.10 else ""))
    )
    print(f"    {iv:30s}: beta={beta:+.4f}  SE={se:.4f}  p={p_one:.4f} {stars}")


def run_regression(
    df_prep: pd.DataFrame, spec: Dict[str, Any]
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

    # exog: KEY_IV + 2 level dummies + controls
    exog = [KEY_IV] + LEVEL_DUMMIES + all_controls

    n_firms = df_prep["gvkey"].nunique()
    n_periods = df_prep.groupby(["gvkey", time_col]).ngroups
    print(f"  N={len(df_prep):,}, firms={n_firms:,}, firm-time periods={n_periods:,}")

    df_panel = df_prep.set_index(["gvkey", time_col])

    t0 = datetime.now()
    try:
        model = _fit_one(df_panel, dv, exog, base_fe)
    except Exception as e:
        print(f"  ERROR regression failed: {e}", file=sys.stderr)
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
        "sample_window": f"{CAL_YR_QTR_MIN}-{CAL_YR_QTR_MAX}",
    }

    print("  Display IV coefs:")
    for iv in DISPLAY_IVS:
        _stash_iv_to_meta(meta, model, iv)

    return model, meta


# ==============================================================================
# Output
# ==============================================================================


def _sig_stars_one(p: float) -> str:
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def _sig_stars_two(p: float) -> str:
    return _sig_stars_one(p)  # alias; numeric thresholds identical


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write 8-column LaTeX table: 4 Cash + 4 UncResCEO_c, all interaction-DiD."""
    results_by_col = {r["meta"]["col"]: r["meta"] for r in all_results if r.get("meta")}

    def fmt_coef(val: float, stars: str) -> str:
        if np.isnan(val): return ""
        return f"{val:.4f}{stars}"

    def fmt_se(val: float) -> str:
        if np.isnan(val): return ""
        return f"({val:.4f})"

    def fmt_r2(val: float) -> str:
        if np.isnan(val): return ""
        if abs(val) < 0.001: return f"{val:.2e}"
        return f"{val:.3f}"

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

    # IV rows
    for iv in DISPLAY_IVS:
        label = VARIABLE_LABELS.get(iv, iv).replace("_", r"\_")
        direction = IV_TAIL_DIRECTION.get(iv, "positive")
        stars_fn = _sig_stars_two if direction == "none" else _sig_stars_one
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

    ind_cells = [
        "Yes" if results_by_col.get(c, {}).get("fe", "").startswith("industry") else ""
        for c in display_cols
    ]
    firm_cells = [
        "Yes" if results_by_col.get(c, {}).get("fe", "").startswith("firm") else ""
        for c in display_cols
    ]
    yr_cells = [
        "Yes" if not results_by_col.get(c, {}).get("fe", "").endswith("_yq") else ""
        for c in display_cols
    ]
    yq_cells = [
        "Yes" if results_by_col.get(c, {}).get("fe", "").endswith("_yq") else ""
        for c in display_cols
    ]
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
        r"Difference-in-differences exploiting the November 2016 Trump election as a ",
        r"plausibly-exogenous shock to firm political-risk exposure (cf. Hu, Kang, Li \& Lin 2024 ",
        r"RAST template). Treatment $=$ \textit{BothHigh} firms whose mean PRiskT\_trade and PRiskT\_tax ",
        r"both sit above the FF12-industry-own median over the 5-year pre-window 2011q4--2016q3. ",
        r"$Post = 1$ if cal\_yr\_qtr $\geq$ 2016q4. Off-diagonal cohorts (HighTrade-LowTax and LowTrade-HighTax) dropped. ",
        r"Cash $=$ cheq/atq (Bates 2009 form). UncResCEO $=$ DWZ (2021) Eq.5 within-quarter residual ",
        r"of CEO Q\&A uncertainty (centered on Main sample). ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for DiD; two-tailed for level dummies). ",
        r"Standard errors (in parentheses) firm-level clustered. Main sample (excludes financial and utility firms). ",
        r"Sample window Q3 2014--Q4 2018 (Hu 2024 cutoff to avoid 2019 trade-war + Covid shocks). ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_5_trump_did_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: {tex_path.name}")


def save_outputs(
    all_results: List[Dict[str, Any]], out_dir: Path
) -> pd.DataFrame:
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
            f.write(f"H1.5 Trump 2016 DiD\n")
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


def _write_suite_spec_json(
    all_results: List[Dict[str, Any]], out_dir: Path
) -> None:
    """Emit canonical suite_spec_H1.5.trump_did.json."""
    results_by_col = {r["meta"]["col"]: r for r in all_results if r.get("meta")}

    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    display_cols = [1, 2, 3, 4, 5, 6, 7, 8]
    for col in display_cols:
        if col not in results_by_col:
            raise RuntimeError(f"H1.5 spec build: missing result for col {col}")

        entry = results_by_col[col]
        model = entry["model"]
        meta = entry["meta"]
        spec = next(s for s in MODEL_SPECS if s["col"] == col)
        fe = spec["fe"]
        base_fe = fe.replace("_yq", "")
        fe_entity = "industry" if base_fe == "industry" else "firm"
        fe_time = (
            "calendar_year_quarter" if fe.endswith("_yq") else "calendar_year"
        )
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
        # IV coefs: KEY_IV (positive), level dummies (none/two-tailed)
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

        # Controls
        control_coefs = extract_coefs_panelols(
            model=model,
            key_ivs=[],
            all_vars=control_vars,
            hyp_dir="none",
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

    header_rows = [
        [
            {"label": "Cash Holdings", "span": 4},
            {"label": "UncResCEO", "span": 4},
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
        controls={
            "base": list(CONTROLS),
            "extended_only": list(EXTENDED_ONLY_CONTROLS),
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


# ==============================================================================
# Report
# ==============================================================================


def generate_report(
    all_results: List[Dict[str, Any]], out_dir: Path,
    duration: float, iv_means: Dict[str, float],
) -> None:
    iv_means_str = ", ".join(f"{k}={v:+.4f}" for k, v in iv_means.items())
    lines = [
        "# H1.5 Trump 2016 DiD on Cash + Speech",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Design:** Cash + UncResCEO ~ DiD_Trump + BothHigh + Post + ctrls + FE",
        f"**Sample window:** Q3 {YEAR_MIN}–Q4 {YEAR_MAX} (cal_yr_qtr {CAL_YR_QTR_MIN}-{CAL_YR_QTR_MAX})",
        f"**Treatment:** BothHigh = (PRiskT_trade >= FF12-median) AND (PRiskT_tax >= FF12-median)",
        f"**Pre-window for treatment label:** 2011q4–2016q3 (5 years, fixed pre-event)",
        f"**Post:** cal_yr_qtr >= 2016q4 (Trump elected Nov 2016)",
        f"**Off-diagonal cohorts dropped:** yes (HighTrade-LowTax + LowTrade-HighTax)",
        f"**Centering:** UncResCEO -> UncResCEO_c (Main sample mean = {iv_means_str})",
        "",
        "## Results (Cash regressions: cols 1-4; Speech regressions: cols 5-8)",
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
        "## Interpretation (Story B framing per spec v3 + plan v3)",
        "",
        "- DiD positive on CashRatio: Trump shock activates precautionary cash for BothHigh firms",
        "- DiD positive on UncResCEO: Trump shock activates speech-uncertainty for BothHigh firms",
        "- Joint positivity is the LOAD-BEARING evidence for the indicator-state Story B",
        "- DiD null on either side: weakens but does not break the indicator-state story",
        "  (alternative-channel control regressions in Phase 4 robustness)",
        "- Forward-only causation from Trump 2016 to Cash + Speech is plausible because Trump's election",
        "  was unexpected (Wolfers-Zitzewitz 2017 prediction-market jump) AND treatment label is fixed pre-event",
    ]
    with open(out_dir / "report_step4_H1_5_trump_did.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H1_5_trump_did.md")


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
        suite_name="H1_5_Trump_DiD",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H1.5 TRUMP 2016 DiD ON CASH + SPEECH")
    print("=" * 80)
    print(f"Timestamp:    {timestamp}")
    print(f"Output:       {out_dir}")
    print(f"Design:       8 specs (4 FE x 2 DVs); single key IV = DiD_Trump")
    print(f"Channel:      CH-Trump2016 — exogenous political-risk shock")
    print(f"Pre-window:   2011q4..2016q3 (5 years, treatment-label fixation)")
    print(f"Sample:       Q3 2014..Q4 2018 (Hu 2024 RAST cutoff)")
    print(f"Post:         cal_yr_qtr >= 2016q4")
    print(f"Tail:         DiD_Trump POS (one-tail); level dummies two-tail")

    # Load + merge
    panel, panel_file = load_panel(root, panel_path)
    panel = load_and_merge_did(panel, root, years=range(2002, 2019))

    # Pre-filter for sample window (memory: drop pre-2014 + post-2018 calls).
    panel = filter_sample_window(panel)

    # Center UncResCEO on Main sample (within sample window).
    main_mask = ~panel["ff12_code"].isin([8, 11])
    panel, mu_uncres = center_speech_iv(panel, main_mask)
    iv_means = {"UncResCEO": mu_uncres}

    # Compute UncResCEO_c lag for speech regression's Lagged_DV
    panel = attach_speech_lag(panel)

    # Filter Main + treated/control
    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)
    panel = filter_treated_control_only(panel)
    tc_n = len(panel)

    print(
        f"\n  Main+TC: {tc_n:,} calls, {panel['gvkey'].nunique():,} firms"
    )

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H1.5 Trump 2016 DiD (Main+TC, Q3 2014--Q4 2018)",
        label="tab:summary_stats_h1_5_trump_did",
    )
    print("  Saved: summary_stats.csv/.tex")

    # Run regressions
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

    # Save
    diag_df = save_outputs(all_results, out_dir)
    _write_suite_spec_json(all_results, out_dir)

    # Attrition
    if all_results:
        first = all_results[0]["meta"]
        attrition_stages = [
            ("Full panel (H1)", 112968),
            (f"Sample window {CAL_YR_QTR_MIN}-{CAL_YR_QTR_MAX}", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("Treated+Control (BothHigh OR BothLow)", tc_n),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(
            attrition_stages, out_dir, "H1.5 Trump 2016 DiD",
        )
        print("  Saved: sample_attrition.csv/.tex")

    # Manifest
    input_paths = {
        "panel": panel_file,
        "prisk_subtopics": root / "inputs" / "FirmLevelRisk" / "firmquarter_2022q1.csv",
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

    # DiD significance summary
    print("\nDiD_Trump significance summary (one-tail POS, p<0.05):")
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
