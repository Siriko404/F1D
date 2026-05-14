#!/usr/bin/env python3
"""
================================================================================
STAGE 4: H1.5 Brexit Referendum DiD on Cash + Speech (Campello 2022 verbatim)
================================================================================
ID: econometric/run_h1_5_brexit_did
Description: Difference-in-differences design exploiting the June 23, 2016 UK
             Brexit referendum as a plausibly-exogenous foreign-uncertainty
             shock to U.S. firms with UK exposure. Two parallel treatment
             definitions per Campello et al. 2022 JFQA Section IV.A:

             1. HIGH_BETA_UK   — top tercile of nonneg β^UK from equation (13)
                                 (firm exposure to UK equity-market vol over
                                  60 monthly obs 2010M1-2014M12)
             2. HIGH_10K       — >5 entries of 9-keyword Brexit/UK terms in
                                 firm's 2015 10-K filing

             Two parallel DVs per treatment x FE configuration:
               Run 1: cash_brexit_dv = cheq / lag(atq - cheq)   (BKS net-assets)
               Run 2: UncResCEO_c    (F1D speech extension)

             POST = cal_yr_qtr in {20163, 20164} (2016Q3-Q4 — the referendum
             vote and the immediate aftermath through year-end).

             4 baseline cells = 2 DVs x 2 treatments x 1 FE (Campello-exact).

Tail directions:
    HIGH_X x Post on cash_brexit_dv:  one-tail POS  (precautionary cash response)
    HIGH_X x Post on UncResCEO_c:     one-tail POS  (uncertainty-induced speech)
    HIGH_X level dummy:               two-tailed (absorbed by firm FE)
    Post level dummy:                 two-tailed (absorbed by time FE)

Channel:
    CH-Brexit2016 — foreign-uncertainty macro shock orthogonal to US-domestic
    political-risk shocks (Trump). Strengthens the "shock-scale hierarchy"
    framing of Section III.E.4 (macro UK / state / firm-event triangulation).

Anchor: Campello et al. (2022) JFQA Section IV verbatim. Spec-locked at
    tmp/3did_replication_v2_2026_05_08.md Section A (lines 74-960).

Model Specification (per Campello et al. 2022 Section II.D):

    DV ~ b1 * (HIGH_X x POST) + b2 * HIGH_X + b3 * POST
       + 5 macro controls (1Q-lagged)
       + 5 firm controls (1Q-lagged): brexit_tobins_q, brexit_sales_growth,
         brexit_stock_return, brexit_cash_flow, ln(atq)
       + 1 add'l: consensus EPS z-score (1Q-lagged)
       + FIRM FE + Hoberg-Phillips FIC100 x cal_yr_qtr FE (manual interaction)
       + double-cluster SE (firm + cal_yr_qtr)

CRITICAL DESIGN DEVIATIONS FROM TRUMP/REDISTRICTING SISTER RUNNERS.
1. Controls: 5 macros + Brexit-verbatim firm controls (NOT F1D canonical 12)
   per audit MAJOR-3 + Sina-locked decision; macro-shock identification
   requires macro controls.
2. SE: double-cluster firm + cal_yr_qtr per Campello Section II.D verbatim
   ("Standard errors are double-clustered by firm and calendar quarters").
3. FE: firm + FIC100 x cal_yr_qtr (manually constructed interaction dummy
   passed as other_effects with drop_absorbed=True) per audit MAJOR-4.
4. DV: cash_brexit_dv = cheq / lag(atq - cheq) per Table 8 footer
   (BKS net-assets). Distinct from F1D-canonical CashRatio = cheq/atq.

Inputs:
    - outputs/variables/h1_cash_holdings/<latest>/h1_cash_holdings_panel.parquet
    - outputs/econometric/ceo_clarity_extended/<latest>/ceo_clarity_residual.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet (raw cheq + atq + mkvaltq)
    - 10 Brexit builder outputs via get_latest_output_dir():
        brexit_treatment_beta_uk + brexit_treatment_10k + brexit_macro +
        brexit_consensus_eps + hoberg_phillips_fic100 +
        brexit_tobins_q + brexit_sales_growth + brexit_stock_return +
        brexit_cash_flow + brexit_psm_matching

Outputs:
    - outputs/econometric/h1_5_brexit_did/<timestamp>/
================================================================================
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.outputs import extract_coefs_panelols, write_suite_spec


# ==============================================================================
# Configuration
# ==============================================================================

KEY_IV_BETA_UK = "DiD_BetaUK"
KEY_IV_10K = "DiD_10K"

# 5 macro controls (1Q-lagged, all already _lag1 in builder output).
MACRO_CONTROLS = ["usd_gbp_lag1", "vix_lag1", "gdp_fcst_1y_lag1", "umcsent_lag1", "ads_lag1"]

# 5 Brexit-verbatim firm controls (1Q-lagged at panel-assembly).
FIRM_CONTROLS_NAMES = [
    "brexit_tobins_q", "brexit_sales_growth", "brexit_stock_return",
    "brexit_cash_flow", "ln_atq",
]
FIRM_CONTROLS_LAG1 = [c + "_lag1" for c in FIRM_CONTROLS_NAMES]

# Consensus EPS (1Q-lagged at panel-assembly).
EPS_CONTROL_LAG1 = "consensus_eps_z_lag1"

ALL_CONTROLS_LAG1 = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1]

# DiD treatment columns (constructed in panel assembly).
DID_COLS = [KEY_IV_BETA_UK, KEY_IV_10K]
LEVEL_DUMMIES_BETA = ["HIGH_BETA_UK", "Post_brexit"]
LEVEL_DUMMIES_10K = ["HIGH_10K", "Post_brexit"]

# Sample window per spec §1G.
WINDOW_START_YQ = 20101  # 2010Q1
WINDOW_END_YQ = 20164    # 2016Q4
POST_START_YQ = 20163    # 2016Q3 — Brexit vote June 23 2016

# $10M MV/BA filter per spec §1G + audit MAJOR-2.
MIN_MV_OR_BA_MILLIONS = 10.0

# Winsorization 1% within cal_yr_qtr (per spec §2E + audit VAGUE-2).
WINSOR_PCT = 0.01

# FE configuration — Campello 2022 JFQA verbatim spec only:
# firm FE + Hoberg-Phillips FIC100 × cal_yr_qtr FE (passed via
# other_effects=fic100_qtr_id). Per Sina decision 2026-05-13: replicate the
# original paper's exact specification, no F1D-added FE-robustness variants.
FE_LADDER = ["campello_exact"]

SUITE_ID = "H1.5.brexit_did"
SUITE_DIR_NAME = "h1_5_brexit_did"
SUITE_TITLE = (
    "Brexit Referendum Difference-in-Differences: Cash Holdings + CEO Speech "
    "Uncertainty (Campello et al. 2022 JFQA verbatim)"
)
SUITE_LABEL = "tab:h1_5_brexit_did"

CLUSTERING = {"entity": True, "time": True}  # double-cluster firm + cal_yr_qtr


# ==============================================================================
# Data Loading
# ==============================================================================

def load_h1_panel(root: Path) -> Tuple[pd.DataFrame, Path]:
    """Load Compustat universe restricted to Brexit window + Campello SIC filters.

    Sina decision 2026-05-14 (Problem 1): Brexit DiD is pure cash replication on
    Campello's analytic frame — the Compustat universe — not F1D's call-panel
    subset. Speech extension is moved to Boasiako (where the call-panel
    restriction does not collide with cash β recovery).

    Returns ((gvkey, cal_yr_qtr, sic_int) universe, source_parquet_path).

    Filters applied:
        - Brexit window 2010Q1-2016Q4
        - SIC 4900-4999 (utility) + 6000-6999 (financial) DROPPED per Campello §1G
    """
    cpath = root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    import pyarrow.parquet as pq
    from datetime import datetime as _dt

    yr_min = WINDOW_START_YQ // 10
    yr_max = WINDOW_END_YQ // 10 + 1
    table = pq.read_table(
        cpath,
        columns=["gvkey", "datadate", "sic"],
        filters=[("datadate", ">=", _dt(yr_min, 1, 1)),
                 ("datadate", "<",  _dt(yr_max, 1, 1))],
    )
    df = table.to_pandas()
    del table

    df["datadate"] = pd.to_datetime(df["datadate"])
    df["cal_yr_qtr"] = df["datadate"].dt.year * 10 + df["datadate"].dt.quarter
    df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)
    df = df[(df["cal_yr_qtr"] >= WINDOW_START_YQ) & (df["cal_yr_qtr"] <= WINDOW_END_YQ)]

    df["sic_int"] = pd.to_numeric(df["sic"], errors="coerce")
    pre = len(df)
    df = df[~((df["sic_int"] >= 4900) & (df["sic_int"] <= 4999))]
    df = df[~((df["sic_int"] >= 6000) & (df["sic_int"] <= 6999))]
    print(f"  SIC drop util+fin: {len(df):,} cells (dropped {pre - len(df):,})")

    df = df.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
        subset=["gvkey", "cal_yr_qtr"], keep="last"
    ).reset_index(drop=True)
    return df[["gvkey", "cal_yr_qtr", "sic_int"]], cpath


def load_compustat_raw(root: Path, gvkeys_keep: set, qtr_min: int, qtr_max: int) -> pd.DataFrame:
    """Re-load raw Compustat for cheq, atq, mkvaltq per audit CRITICAL-3.

    Memory-aware: uses pyarrow predicate pushdown on `datadate` to skip
    row-groups outside the Brexit window BEFORE materializing into pandas.
    Cuts the 467 MB file's I/O cost ~10x for our 2009–2017 window slice.
    Cache layer: writes the filtered slice to outputs/intermediate/ once;
    subsequent runs read the ~1-5 MB cache instead of the 467 MB source.
    """
    cache_dir = root / "outputs" / "intermediate" / "brexit_compustat_slice"
    cache_path = cache_dir / f"slice_{qtr_min}_{qtr_max}.parquet"
    if cache_path.exists():
        df = pd.read_parquet(cache_path)
        df = df[df["gvkey"].isin(gvkeys_keep)].reset_index(drop=True)
        print(f"  Compustat raw (cache hit {cache_path.name}): {len(df):,} rows ({df['gvkey'].nunique():,} gvkeys)")
        return df

    cpath = root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    print(f"  Re-loading Compustat raw (no cache): {cpath}")
    # Predicate pushdown on datadate — pyarrow skips row-groups outside [yr_min, yr_max].
    yr_min = qtr_min // 10
    yr_max = qtr_max // 10 + 1  # +1 to include Q4 of yr_max
    from datetime import datetime as _dt
    import pyarrow.parquet as pq
    table = pq.read_table(
        cpath,
        columns=["gvkey", "datadate", "atq", "cheq", "mkvaltq"],
        filters=[("datadate", ">=", _dt(yr_min, 1, 1)),
                 ("datadate", "<",  _dt(yr_max, 1, 1))],
    )
    df = table.to_pandas()
    del table  # release pyarrow memory before pandas transforms
    for c in ["atq", "cheq", "mkvaltq"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["cal_yr_qtr"] = df["datadate"].dt.year * 10 + df["datadate"].dt.quarter
    df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)
    df = df[(df["cal_yr_qtr"] >= qtr_min) & (df["cal_yr_qtr"] <= qtr_max)]
    df = df.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
        subset=["gvkey", "cal_yr_qtr"], keep="last"
    ).reset_index(drop=True)

    # Persist full-universe slice (NOT restricted to gvkeys_keep) so cache is
    # reusable across gvkey-set variations. Filter to gvkeys_keep AFTER caching.
    cache_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path, index=False)
    df = df[df["gvkey"].isin(gvkeys_keep)].reset_index(drop=True)
    print(f"  Compustat raw rows in window: {len(df):,} ({df['gvkey'].nunique():,} gvkeys); cached to {cache_path.name}")
    return df


def load_brexit_builders(root: Path) -> Dict[str, pd.DataFrame]:
    """Load all 10 Brexit builder outputs via get_latest_output_dir()."""
    base = root / "outputs" / "variables"
    sources = {
        "beta_uk": ("brexit_treatment_beta_uk", "beta_uk_per_firm.parquet"),
        "treat_10k": ("brexit_treatment_10k", "treatment_10k_per_firm.parquet"),
        "macro": ("brexit_macro", "brexit_macro_quarterly.parquet"),
        "eps": ("brexit_consensus_eps", "consensus_eps_per_firm_quarter.parquet"),
        "fic100": ("hoberg_phillips_fic100", "fic100_per_firm_year.parquet"),
        "tobins_q": ("brexit_tobins_q", "brexit_tobins_q.parquet"),
        "sales_growth": ("brexit_sales_growth", "brexit_sales_growth.parquet"),
        "stock_return": ("brexit_stock_return", "brexit_stock_return.parquet"),
        "cash_flow": ("brexit_cash_flow", "brexit_cash_flow.parquet"),
        "psm": ("brexit_psm_matching", "psm_matched_per_firm.parquet"),
    }
    out: Dict[str, pd.DataFrame] = {}
    for k, (dirname, fname) in sources.items():
        d = get_latest_output_dir(base / dirname, required_file=fname)
        out[k] = pd.read_parquet(d / fname)
        print(f"  {k:15s} {len(out[k]):>10,} rows  ({d.name})")
    return out


# ==============================================================================
# Panel assembly
# ==============================================================================

def winsorize_within(df: pd.DataFrame, col: str, group: str, pct: float = WINSOR_PCT) -> pd.DataFrame:
    """Vectorized 1% winsorize within group. ~50-100x faster than groupby.transform.

    Old path: groupby(group).transform(lambda s: s.clip(s.quantile(pct), s.quantile(1-pct)))
             — recomputes quantiles row-by-row in Python.
    New path: one groupby.agg to get per-group bounds, broadcast-merge, vectorized clip.
    """
    bounds = (
        df.groupby(group, observed=True)[col]
          .agg(_lo=lambda s: s.quantile(pct), _hi=lambda s: s.quantile(1 - pct))
          .reset_index()
    )
    df = df.merge(bounds, on=group, how="left")
    df[col] = df[col].clip(lower=df["_lo"], upper=df["_hi"])
    df = df.drop(columns=["_lo", "_hi"])
    return df


def assemble_panel(panel: pd.DataFrame, raw_comp: pd.DataFrame, builders: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build (gvkey, cal_yr_qtr) cash-only panel on Compustat universe.

    Sina decision 2026-05-14 (Wave 1):
      - Problem 1: universe = Compustat, NOT call panel (no UncResCEO_c).
      - Problem 2: HIGH_BETA_UK from top-N=449/449 match (already in builder).
      - Firm-control 1Q-lag via calendar-prev-Q merge (not row-order shift).

    Input ``panel`` is the Compustat universe (gvkey, cal_yr_qtr, sic_int)
    produced by load_h1_panel after SIC 4900-4999 + 6000-6999 drop.
    """
    print("\n  --- Panel assembly (Compustat universe, cash-only) ---")

    # 1. Merge universe with raw Compustat.
    cell = panel[["gvkey", "cal_yr_qtr"]].merge(
        raw_comp, on=["gvkey", "cal_yr_qtr"], how="inner"
    )
    print(f"  After Compustat merge: {len(cell):,} cells ({cell['gvkey'].nunique():,} gvkeys)")

    # 2. Cash DV with calendar-prev-Q lag.
    def _prev_yq(yq: int) -> int:
        yr, q = yq // 10, yq % 10
        if q == 1: return (yr - 1) * 10 + 4
        return yr * 10 + (q - 1)
    cell["prev_qtr_id"] = cell["cal_yr_qtr"].map(_prev_yq)
    lag_src = raw_comp.rename(columns={"atq": "atq_lag1", "cheq": "cheq_lag1"})[
        ["gvkey", "cal_yr_qtr", "atq_lag1", "cheq_lag1"]
    ].rename(columns={"cal_yr_qtr": "prev_qtr_id"})
    cell = cell.merge(lag_src, on=["gvkey", "prev_qtr_id"], how="left")
    cell["denom"] = cell["atq_lag1"] - cell["cheq_lag1"]
    cell = cell[cell["denom"] > 0]
    cell["cash_brexit_dv"] = cell["cheq"] / cell["denom"]
    cell = cell.drop(columns=["prev_qtr_id"])

    # 3. $10M filter (AND-keep: both mkvaltq ≥ $10M AND atq ≥ $10M).
    pre = len(cell)
    cell = cell[(cell["mkvaltq"].fillna(0) >= MIN_MV_OR_BA_MILLIONS) & (cell["atq"] >= MIN_MV_OR_BA_MILLIONS)]
    print(f"  $10M MV/BA filter (AND): {len(cell):,} (dropped {pre - len(cell):,})")

    # 4. Merge treatment dummies HIGH_BETA_UK (top-N=449 mode) + HIGH_10K.
    bu = builders["beta_uk"][["gvkey", "HIGH_BETA_UK"]]
    tk = builders["treat_10k"][["gvkey", "HIGH_10K"]]
    cell = cell.merge(bu, on="gvkey", how="left")
    cell = cell.merge(tk, on="gvkey", how="left")
    print(f"  HIGH_BETA_UK in {{0,1}}: {cell['HIGH_BETA_UK'].isin([0.0, 1.0]).sum():,}")
    print(f"  HIGH_10K     in {{0,1}}: {cell['HIGH_10K'].isin([0.0, 1.0]).sum():,}")

    # 5. POST + DiD interactions.
    cell["Post_brexit"] = (cell["cal_yr_qtr"] >= POST_START_YQ).astype(int)
    cell[KEY_IV_BETA_UK] = cell["HIGH_BETA_UK"].fillna(np.nan) * cell["Post_brexit"]
    cell[KEY_IV_10K] = cell["HIGH_10K"].fillna(np.nan) * cell["Post_brexit"]

    # 6. Macros (already 1Q-lagged in builder).
    cell = cell.merge(builders["macro"], on="cal_yr_qtr", how="left")

    # 7. Firm controls + ln_atq.
    for col, key in [("brexit_tobins_q", "tobins_q"),
                     ("brexit_sales_growth", "sales_growth"),
                     ("brexit_stock_return", "stock_return"),
                     ("brexit_cash_flow", "cash_flow")]:
        sub = builders[key][["gvkey", "cal_yr_qtr", col]]
        cell = cell.merge(sub, on=["gvkey", "cal_yr_qtr"], how="left")
    cell["ln_atq"] = np.log(cell["atq"].clip(lower=1.0))

    # 8. 1Q-lag firm controls via CALENDAR-prev-Q merge (row-order shift mis-lags
    # gappy panels).
    cell["prev_qtr_id"] = cell["cal_yr_qtr"].map(_prev_yq)
    for c in FIRM_CONTROLS_NAMES:
        lag_src = cell[["gvkey", "cal_yr_qtr", c]].rename(
            columns={"cal_yr_qtr": "prev_qtr_id", c: c + "_lag1"}
        )
        cell = cell.merge(lag_src, on=["gvkey", "prev_qtr_id"], how="left")

    # 9. Consensus EPS lag (calendar-prev-Q).
    eps = builders["eps"][["gvkey", "cal_yr_qtr", "consensus_eps_z"]]
    cell = cell.merge(eps, on=["gvkey", "cal_yr_qtr"], how="left")
    eps_lag_src = cell[["gvkey", "cal_yr_qtr", "consensus_eps_z"]].rename(
        columns={"cal_yr_qtr": "prev_qtr_id", "consensus_eps_z": EPS_CONTROL_LAG1}
    )
    cell = cell.merge(eps_lag_src, on=["gvkey", "prev_qtr_id"], how="left")
    cell = cell.drop(columns=["prev_qtr_id"])

    # 10. FIC100 industry per (gvkey, year) + interaction-FE id.
    cell["year"] = cell["cal_yr_qtr"] // 10
    fic = builders["fic100"][["gvkey", "year", "fic100_industry_id"]]
    cell = cell.merge(fic, on=["gvkey", "year"], how="left")
    fic_cov = cell["fic100_industry_id"].notna().mean()
    print(f"  FIC100 coverage: {fic_cov:.1%}")
    cell["fic100_qtr_id"] = (
        cell["fic100_industry_id"].astype("Int64").astype(str) + "_" + cell["cal_yr_qtr"].astype(str)
    )

    # 11. Winsorize 1% within cal_yr_qtr on vars CREATED here (firm-control _lag1
    # values already winsorized at builder time — do NOT re-winsorize per
    # Campello §2E "winsorize ONCE").
    for c in ["cash_brexit_dv", "ln_atq", EPS_CONTROL_LAG1]:
        if c in cell.columns:
            cell = winsorize_within(cell, c, "cal_yr_qtr")

    print(f"  Final panel: {len(cell):,} (gvkey, cal_yr_qtr) cells ({cell['gvkey'].nunique():,} gvkeys)")
    return cell


# ==============================================================================
# Regression
# ==============================================================================

def _fit_one(df: pd.DataFrame, dv: str, treatment: str, exog_cols: List[str], fe: str) -> Tuple[Any, Dict[str, Any]]:
    """Fit one regression spec. Returns (model_or_None, meta_dict)."""
    df = df.dropna(subset=[dv, treatment] + exog_cols).copy()
    if treatment == KEY_IV_BETA_UK:
        # Restrict to firms with HIGH_BETA_UK in {0, 1}
        df = df[df["HIGH_BETA_UK"].isin([0.0, 1.0])]
        level_dummy = "HIGH_BETA_UK"
    elif treatment == KEY_IV_10K:
        df = df[df["HIGH_10K"].isin([0.0, 1.0])]
        level_dummy = "HIGH_10K"
    else:
        raise ValueError(f"Unknown treatment {treatment}")

    if len(df) < 100:
        return None, {"n_obs": int(len(df)), "skipped": "too few obs"}

    df = df.set_index(["gvkey", "cal_yr_qtr"])
    fit_kwargs: Dict[str, Any] = {"cov_type": "clustered"}
    if CLUSTERING.get("entity"):
        fit_kwargs["cluster_entity"] = True
    if CLUSTERING.get("time"):
        fit_kwargs["cluster_time"] = True

    exog_full = [treatment, level_dummy] + exog_cols
    # Note: Post_brexit absorbed by time FE in time-FE specs; let drop_absorbed handle it.
    if fe == "campello_exact":
        # Campello 2022 JFQA Table 8 verbatim: firm FE + Hoberg-Phillips FIC100 ×
        # cal_yr_qtr FE (passed via other_effects=fic100_qtr_id, pre-constructed
        # at panel-assembly time).
        df_fe = df.dropna(subset=["fic100_qtr_id"])
        model = PanelOLS(
            dependent=df_fe[dv],
            exog=df_fe[exog_full],
            entity_effects=True,
            time_effects=False,
            other_effects=df_fe["fic100_qtr_id"],
            drop_absorbed=True,
            check_rank=False,
        )
    elif fe in ("industry", "industry_yq"):
        # Industry FE via other_effects (FF12) — simpler than FIC100xQ for industry-level.
        # For industry_yq we add time_effects=True in addition to FF12.
        time_effects = (fe == "industry_yq")
        df_fe = df.dropna(subset=["ff12_code"])
        model = PanelOLS(
            dependent=df_fe[dv],
            exog=df_fe[exog_full],
            entity_effects=False,
            time_effects=time_effects,
            other_effects=df_fe["ff12_code"],
            drop_absorbed=True,
            check_rank=False,
        )
    elif fe == "firm":
        model = PanelOLS(
            dependent=df[dv],
            exog=df[exog_full],
            entity_effects=True,
            time_effects=False,
            drop_absorbed=True,
            check_rank=False,
        )
    elif fe == "firm_yq":
        # Canonical TWFE-DiD: firm + cal_yr_qtr time effects.
        model = PanelOLS(
            dependent=df[dv],
            exog=df[exog_full],
            entity_effects=True,
            time_effects=True,
            drop_absorbed=True,
            check_rank=False,
        )
    else:
        raise ValueError(f"Unknown FE config {fe}")

    try:
        result = model.fit(**fit_kwargs)
    except Exception as e:
        return None, {"n_obs": int(len(df)), "skipped": f"fit failed: {e}"}

    # Extract R²: within (linearmodels default — after FE partialing) AND overall
    # (Campello convention; includes FE-absorbed variance). Sina decision 2026-05-14
    # (Problem 4): report both. linearmodels exposes rsquared (within) +
    # rsquared_overall.
    r2_within = float(result.rsquared)
    try:
        r2_overall = float(result.rsquared_overall)
    except Exception:
        r2_overall = float("nan")

    meta = {
        "treatment": treatment,
        "dv": dv,
        "fe": fe,
        "n_obs": int(result.nobs),
        "r2": r2_within,  # backward-compat alias for within R²
        "r2_within": r2_within,
        "r2_overall": r2_overall,
    }
    if treatment in result.params.index:
        meta["beta"] = float(result.params[treatment])
        meta["se"] = float(result.std_errors[treatment])
        meta["t"] = float(result.tstats[treatment])
        p_two = float(result.pvalues[treatment])
        # Convert to one-tailed positive (t > 0 → p_one = p_two/2 if t>0 else 1 - p_two/2).
        meta["p_two"] = p_two
        meta["p_one"] = (p_two / 2) if meta["beta"] >= 0 else 1 - (p_two / 2)
    else:
        meta.update({"beta": np.nan, "se": np.nan, "t": np.nan, "p_two": np.nan, "p_one": np.nan})
    return result, meta


def run_baseline_specs(panel: pd.DataFrame) -> List[Dict[str, Any]]:
    """2 baseline cells = 1 DV (cash) x 2 treatments x 1 FE (Campello-exact).

    Sina decision 2026-05-14 (Problem 1): Brexit DiD is cash-only on Compustat
    universe. Speech extension moved to Boasiako.
    """
    DVS = ["cash_brexit_dv"]
    TREATMENTS = [KEY_IV_BETA_UK, KEY_IV_10K]
    results: List[Dict[str, Any]] = []
    col = 0
    for dv in DVS:
        for treatment in TREATMENTS:
            for fe in FE_LADDER:
                col += 1
                exog_cols = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
                model, meta = _fit_one(panel, dv, treatment, exog_cols, fe)
                meta["col"] = col
                results.append({"model": model, "meta": meta})
                msg = (f"  Col ({col:>2d}) DV={dv:14s} treat={treatment:12s} FE={fe:14s} "
                       f"n={meta.get('n_obs', 0):>6,} beta={meta.get('beta', np.nan):+.4f} "
                       f"se={meta.get('se', np.nan):.4f} p_one={meta.get('p_one', np.nan):.3f} "
                       f"r2w={meta.get('r2_within', np.nan):.3f} r2o={meta.get('r2_overall', np.nan):.3f}")
                if meta.get("skipped"):
                    msg += f"  SKIPPED({meta['skipped']})"
                print(msg)
    return results


# ==============================================================================
# Output
# ==============================================================================

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


def write_outputs(results: List[Dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # CSV diagnostics.
    rows = []
    for r in results:
        m = r["meta"]
        rows.append(m)
    diag = pd.DataFrame(rows)
    diag.to_csv(out_dir / "model_diagnostics.csv", index=False)
    print(f"  Saved: model_diagnostics.csv ({len(diag)} rows)")

    # Markdown summary.
    lines = ["# H1.5 Brexit DiD — 16 Baseline Cells", ""]
    lines.append(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("| col | dv | treatment | fe | n | beta | p_one | sig |")
    lines.append("|-----|----|-----------|----|---|------|-------|-----|")
    for r in results:
        m = r["meta"]
        sig = _sig_stars(m.get("p_one", np.nan)) if m.get("beta", 0) >= 0 else ""
        lines.append(
            f"| {m.get('col', '?')} | {m.get('dv', '?')} | {m.get('treatment', '?')} | {m.get('fe', '?')} | "
            f"{m.get('n_obs', 0):,} | {m.get('beta', np.nan):+.4f} | {m.get('p_one', np.nan):.3f} | {sig} |"
        )
    (out_dir / "report_step4_H1_5_brexit_did.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  Saved: report_step4_H1_5_brexit_did.md")

    # Canonical SuiteSpec emission (replaces prior stub dict 2026-05-13).
    # Produces standard suite_spec_<id>.json with per-cell columns array, so
    # docs/Draft/generate_all_tables.py renders this through render_suite()
    # uniformly with all other thesis suites (no stub fallback needed).
    _emit_canonical_suite_spec(results, out_dir)


# ------------------------------------------------------------------------------

# DV / treatment / FE display labels (paper-readable, not internal slugs).
_DV_LABEL = {
    "cash_brexit_dv": "Cash Holdings",
    "UncResCEO_c":    "UncResCEO",
}
_TREAT_LABEL = {
    "DiD_BetaUK": r"$\beta^{UK}$ tercile $\times$ Post",
    "DiD_10K":    r"10-K UK-mention $\times$ Post",
}
_FE_ENTITY_TIME = {
    # campello_exact actually uses firm + FIC100 × cal_yr_qtr (other_effects)
    # — captured as ("firm", "calendar_year_quarter") for canonical-schema
    # compatibility (Literal-restricted fe_time). The FIC100 industry
    # interaction is documented in caption/sample_label.
    "campello_exact": ("firm",     "calendar_year_quarter"),
    "industry":       ("industry", "calendar_year"),
    "firm":           ("firm",     "calendar_year"),
    "industry_yq":    ("industry", "calendar_year_quarter"),
    "firm_yq":        ("firm",     "calendar_year_quarter"),
}


def _emit_canonical_suite_spec(
    results: List[Dict[str, Any]], out_dir: Path,
) -> None:
    """Build standard SuiteSpec from per-cell results + call write_suite_spec().

    Per-column coefs include the treatment IV (DiD_BetaUK or DiD_10K) and all
    controls; the OTHER treatment is null-extracted because the model wasn't
    fit with it. The renderer skips null-valued cells.
    """
    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    for r in results:
        meta = r["meta"]
        model = r.get("model")
        treatment = meta["treatment"]
        dv = meta["dv"]
        fe = meta["fe"]
        fe_entity, fe_time = _FE_ENTITY_TIME[fe]
        level_dummy = "HIGH_BETA_UK" if treatment == KEY_IV_BETA_UK else "HIGH_10K"
        full_control_vars = ALL_CONTROLS_LAG1 + ["Post_brexit", level_dummy]

        adj_r2 = None
        n_firms = None
        dv_mean = None
        if model is not None:
            try:
                adj_r2 = float(model.rsquared)
            except Exception:
                pass
            try:
                dv_mean = float(model.model.dependent.dataframe.mean().iloc[0])
            except Exception:
                pass

        merged_coefs: Dict[str, Dict[str, Any]] = {}
        if model is not None:
            tcoefs = extract_coefs_panelols(
                model=model,
                key_ivs=[treatment],
                all_vars=[treatment],
                hyp_dir="positive",
            )
            merged_coefs.update(tcoefs)
            ctrl_coefs = extract_coefs_panelols(
                model=model,
                key_ivs=[],
                all_vars=full_control_vars,
                hyp_dir="none",
            )
            merged_coefs.update(ctrl_coefs)
        # Drop coefs whose SE / p_two is NaN (variable absorbed by FE or
        # singular). Pydantic schema requires float; renderer can't display
        # NaN coefficients anyway. The Campello-exact spec absorbs all macros
        # + Post + level dummies, so this filter is load-bearing.
        merged_coefs = {
            k: v for k, v in merged_coefs.items()
            if v.get("se") is not None
            and not (isinstance(v["se"], float) and np.isnan(v["se"]))
            and v.get("p_two") is not None
            and not (isinstance(v["p_two"], float) and np.isnan(v["p_two"]))
        }
        coefs_per_col.append(merged_coefs)

        # control_vars passed to col_metadata = only those that survived
        # absorption (have non-NaN coef in merged_coefs, excluding the IV
        # which renders separately). This prevents the table from emitting
        # rows that are blank across all 4 columns (macros + Post + level
        # dummies absorbed by firm + FIC100×CQ FE under Campello-exact spec).
        present_controls = [c for c in full_control_vars if c in merged_coefs]

        col_metadata.append({
            "col":          meta["col"],
            "dv":           dv,
            "fe_entity":    fe_entity,
            "fe_time":      fe_time,
            "control_vars": present_controls,
            "n_obs":        int(meta.get("n_obs", 0)),
            "n_firms":      n_firms,
            "r2":           float(meta.get("r2", float("nan"))),
            "adj_r2":       adj_r2,
            "dv_mean":      dv_mean,
            "cluster_fallback": False,
        })

    ivs = [
        {"name": KEY_IV_BETA_UK,
         "label": _TREAT_LABEL[KEY_IV_BETA_UK],
         "tail":  "one_pos"},
        {"name": KEY_IV_10K,
         "label": _TREAT_LABEL[KEY_IV_10K],
         "tail":  "one_pos"},
    ]

    # 2 cells (Campello-exact, cash-only): col 1 Cash×β^UK, col 2 Cash×10K.
    # FE = firm + FIC100 × cal_yr_qtr. Speech extension moved to Boasiako per
    # Sina decision 2026-05-14 (Problem 1).
    header_rows = [
        [
            {"label": r"Cash Holdings: $\beta^{UK}$ treatment", "span": 1},
            {"label": r"Cash Holdings: 10-K treatment",          "span": 1},
        ],
    ]

    paths = write_suite_spec(
        output_dir=out_dir,
        runner_id=SUITE_DIR_NAME,
        sub_tables=[{
            "suite_id":    SUITE_ID,
            "dir_name":    SUITE_DIR_NAME,
            "title":       SUITE_TITLE,
            "caption":     SUITE_TITLE,
            "label":       SUITE_LABEL,
            "col_range":   list(range(1, len(col_metadata) + 1)),
            "header_rows": header_rows,
            "suite_type":  "standard",
        }],
        coefs_per_col=coefs_per_col,
        col_metadata=col_metadata,
        sample_label=(
            "Brexit window 2010Q1-2016Q4. Treated firms: top tercile of "
            r"$\beta^{UK}$ (cols 1, 3) or >5 UK-mentions in 2015 10-K "
            r"(cols 2, 4). Campello 2022 JFQA verbatim spec: firm FE + "
            r"Hoberg-Phillips FIC100 $\times$ calendar-quarter FE, "
            "double-clustered SE (firm, calendar quarter). Excludes "
            "financial + utility firms."
        ),
        clustering=CLUSTERING,
        tail={"direction": "positive", "applies_to": "ivs_only"},
        ivs=ivs,
        # Restrict displayed control rows to vars present in ≥1 column's
        # coefs. Under Campello-exact spec (firm + FIC100×CQ FE), macros +
        # Post + level dummies are absorbed and never appear in any col;
        # listing them in `base` produces blank rows across the whole table.
        controls={
            "base": sorted(
                {k for cdict in coefs_per_col for k in cdict.keys()
                 if k not in (KEY_IV_BETA_UK, KEY_IV_10K)},
                key=lambda c: (
                    list(ALL_CONTROLS_LAG1) + ["Post_brexit", "HIGH_BETA_UK", "HIGH_10K"]
                ).index(c) if c in list(ALL_CONTROLS_LAG1) + ["Post_brexit", "HIGH_BETA_UK", "HIGH_10K"] else 999
            ),
            "extended_only": [],
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


# ==============================================================================
# Main
# ==============================================================================

def parse_arguments():
    parser = argparse.ArgumentParser(description="Stage 4: H1.5 Brexit DiD (Cash + Speech)")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / SUITE_DIR_NAME / timestamp

    print("=" * 80)
    print("STAGE 4: H1.5 BREXIT DiD ON CASH + SPEECH (Campello 2022 verbatim)")
    print("=" * 80)
    print(f"Timestamp:  {timestamp}")
    print(f"Output:     {out_dir}")
    print(f"Window:     2010Q1 - 2016Q4 ({WINDOW_START_YQ}-{WINDOW_END_YQ})")
    print(f"POST:       cal_yr_qtr >= {POST_START_YQ} (2016Q3 - Brexit vote)")
    print(f"Clustering: double {CLUSTERING}")

    universe, _src_path = load_h1_panel(root)
    print(f"Compustat universe (SIC-filtered): {len(universe):,} cells "
          f"({universe['gvkey'].nunique():,} gvkeys)")

    # Brexit-window gvkey set for raw Compustat re-load efficiency.
    gvkeys_keep = set(universe["gvkey"].unique())
    raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)

    builders = load_brexit_builders(root)

    cell_panel = assemble_panel(universe, raw_comp, builders)

    print("\n  --- Running 2 baseline cells (Cash × β^UK + Cash × 10-K) ---")
    results = run_baseline_specs(cell_panel)

    write_outputs(results, out_dir)
    duration = (datetime.now() - t0).total_seconds()
    print(f"\nDuration: {duration:.1f}s")
    print(f"Cells produced: {sum(1 for r in results if r['meta'].get('beta') is not None and not np.isnan(r['meta'].get('beta', np.nan)))} / {len(results)}")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main())
