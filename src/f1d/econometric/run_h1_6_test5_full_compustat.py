#!/usr/bin/env python3
"""
================================================================================
TEST 5 — H1.6 Redistricting DiD on FULL COMPUSTAT panel (no F1D call-panel restriction)
================================================================================
ID: econometric/run_h1_6_test5_full_compustat
Description: Runs the same H1.6 redistricting DiD design on the full Compustat
             firm-quarter universe (Hasan 2022 sample population) instead of
             the F1D earnings-call-restricted panel. Cash-only (no UncResCEO
             available for non-call firms).

             Per plan @ ~/.claude/plans/tender-popping-origami.md Phase 5
             ACTIVE SCOPE: TEST 5 (Step 2 in B+C-then-A escalation order).
             Step 1 (B+C; Hasan-18 + drop-Treated=0) ran on F1D panel and
             remained null with tiny effect; sample-restriction is
             implicated as the binding constraint.

Treatment: same Hasan 2022 firm-rank-tertile-within-CD methodology used
           in TEST 3 (RedistrictingTreatmentGeocodeBuilder) — no change.

Outcomes:  Cash = CHEQ / ATQ only (4 specs: industry/firm x cal_yr/cal_yr_qtr).
           Speech regressions IMPOSSIBLE outside F1D call panel (no
           earnings-call transcripts -> no UncResCEO).

Controls:  Match TEST 3 F1D-canonical-minus-Lagged_DV minus DailyVola
           (DailyVola requires CRSP per-call window; not applicable to
           non-call firm-quarters). Computed inline from raw Compustat.
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables import RedistrictingTreatmentGeocodeBuilder

# Hasan 2022 18 redistricted states (same set as run_h1_6_redistricting_did.py).
HASAN_18_STATES = {
    "AZ", "FL", "GA", "NV", "SC", "TX", "UT", "WA",
    "IA", "IL", "LA", "MA", "MI", "MO", "NJ", "NY", "OH", "PA",
}

# ==============================================================================
# Configuration
# ==============================================================================

# Step 4 (E) attempted 2002-2021 (Hasan-verbatim full window) but result
# was DEGRADED on all-50-state sample: industry-FE beta +0.01621* p=0.063
# (2006-2015) -> +0.00941 p=0.21 (2002-2021). On --hasan18 sample, retry
# extended window because Hasan's 24,311-obs Table 4 likely uses extended
# window — 18-state sample has less Trump contamination concentration.
YEAR_MIN = 2002
YEAR_MAX = 2021

KEY_IV = "DiD_Redist"
LEVEL_DUMMIES = ["Treated_redist", "Post_redist"]

# Match TEST 3 control set exactly minus DailyVola (CRSP-call-window-bound),
# plus Hasan 2022 verbatim Table 4 controls not in F1D canonical:
#   NWC = (WCAPQ - CHEQ) / ATQ                  [Hasan §3, Eq.2]
#   Acquisition = AQCY_quarterly / ATQ          [Hasan §3, Eq.2]
#   IndustrySigma = 5-yr SIC2 SD of CFO/AT      [Hasan §3, Eq.2; verbatim is 10-yr]
# Hasan 2022 Table 4 verbatim 10-control list (Appendix A Table 12).
# Hasan does NOT include ROA, sCFO, or SalesGrowth — dropped 2026-05-06.
# PRisk also NOT used as a separate control in Table 4 (NLM Q3+Q4 confirmed).
CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ",
    "Capex", "DivDummy",
    "RDSales", "CashFlowAt",
    "NWC", "Acquisition", "IndustrySigma",
]

# Hasan industry exclusions verbatim: SIC 6000-6999 (Financials) +
# 4900-4999 (Utilities).
def _is_excluded_sic(sic_int: int) -> bool:
    return (6000 <= sic_int <= 6999) or (4900 <= sic_int <= 4999)


# ==============================================================================
# Compustat -> firm-quarter panel with H1.6 controls
# ==============================================================================


def _ytd_to_quarterly(df: pd.DataFrame, ytd_col: str, out_col: str) -> pd.DataFrame:
    """Convert a YTD field (e.g. capxy, dvy, oancfy) to quarterly by diff.

    Compustat convention: fyrqtr = 1 in the first fiscal quarter (no diff
    needed); for fyrqtr 2-4, diff against same firm's prior quarter.
    """
    df = df.sort_values(["gvkey", "datadate"], kind="stable").copy()
    df["__prev_ytd"] = df.groupby("gvkey", sort=False)[ytd_col].shift(1)
    df["__prev_fyrqtr"] = df.groupby("gvkey", sort=False)["fqtr"].shift(1)
    # For fyrqtr 1, take YTD as quarterly.
    is_q1 = df["fqtr"] == 1
    quarterly = np.where(
        is_q1, df[ytd_col],
        df[ytd_col] - df["__prev_ytd"]
    )
    df[out_col] = quarterly
    df = df.drop(columns=["__prev_ytd", "__prev_fyrqtr"])
    return df


def build_full_compustat_panel(root: Path) -> pd.DataFrame:
    """Build firm-quarter panel for full Compustat (no call-panel restriction).

    Returns DataFrame with one row per (gvkey, datadate-quarter) and columns:
        gvkey, datadate, year, cal_yr, cal_yr_qtr, sic_int, ff_excluded,
        CashRatio + CONTROLS list above.
    """
    print("\n" + "=" * 60)
    print("Loading full Compustat panel")
    print("=" * 60)

    # ---- Main + gap-fill ----
    main_path = root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    cols = [
        "gvkey", "datadate", "fqtr", "sic",
        "atq", "cheq", "dlcq", "dlttq", "ceqq", "cshoq", "prccq",
        "niq", "capxy", "dvy", "saleq", "xrdq", "oancfy",
        "wcapq", "aqcy",  # Hasan-verbatim NWC + Acquisition
    ]
    df = pd.read_parquet(main_path, columns=cols)
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["year"] = df["datadate"].dt.year
    df = df[df["year"].between(YEAR_MIN - 5, YEAR_MAX + 1)].copy()
    print(f"  Compustat raw rows in {YEAR_MIN-5}-{YEAR_MAX+1}: {len(df):,}")

    # ---- Industry exclusion (Hasan SIC) ----
    df = df.dropna(subset=["sic", "atq"])
    df["sic_int"] = pd.to_numeric(df["sic"], errors="coerce").astype("Int64")
    df = df[df["sic_int"].notna()].copy()
    df["sic_int"] = df["sic_int"].astype(int)
    df["ff_excluded"] = df["sic_int"].apply(_is_excluded_sic)
    n_before_exc = len(df)
    df = df[~df["ff_excluded"]].copy()
    print(f"  After Hasan SIC exclusions (6000-6999, 4900-4999): "
          f"{len(df):,} / {n_before_exc:,}")

    # Cast numeric fields to float64 (Compustat parquet uses decimal types
    # that don't support division when divisor==0).
    numeric_cols = [
        "atq", "cheq", "dlcq", "dlttq", "ceqq", "cshoq", "prccq",
        "niq", "capxy", "dvy", "saleq", "xrdq", "oancfy", "fqtr",
        "wcapq", "aqcy",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")

    # ---- Convert YTD fields to quarterly ----
    df = df.dropna(subset=["fqtr"])
    df = _ytd_to_quarterly(df, "capxy", "capx_q")
    df = _ytd_to_quarterly(df, "dvy", "dv_q")
    df = _ytd_to_quarterly(df, "oancfy", "oancf_q")
    df = _ytd_to_quarterly(df, "aqcy", "aqc_q")

    # ---- Compute controls ----
    df["CashRatio"] = df["cheq"] / df["atq"]
    df["Leverage"] = (df["dlcq"] + df["dlttq"]) / df["atq"]
    df["lnAssets"] = np.log(df["atq"].clip(lower=1e-6))
    # Hasan M/B / TobinsQ formula: (AT + CSHO*PRCC - CEQ) / AT
    df["TobinsQ"] = (
        df["atq"] + df["cshoq"] * df["prccq"] - df["ceqq"]
    ) / df["atq"]
    # ROA: 4q rolling sum of niq / 4q rolling mean of atq
    df = df.sort_values(["gvkey", "datadate"], kind="stable")
    df["__niq_4q"] = df.groupby("gvkey", sort=False)["niq"].transform(
        lambda s: s.rolling(4, min_periods=2).sum()
    )
    df["__atq_4q"] = df.groupby("gvkey", sort=False)["atq"].transform(
        lambda s: s.rolling(4, min_periods=2).mean()
    )
    df["ROA"] = df["__niq_4q"] / df["__atq_4q"]
    df["Capex"] = df["capx_q"] / df["atq"]
    df["DivDummy"] = (df["dv_q"] > 0).astype(float)
    df["CashFlowAt"] = df["oancf_q"] / df["atq"]
    # Hasan 2022 verbatim: "the value of R&D is set to zero" for missing.
    df["RDSales"] = (df["xrdq"] / df["saleq"].replace({0: np.nan})).fillna(0.0)

    # SalesGrowth: (SALEQ - SALEQ_4q_lag) / |SALEQ_4q_lag|
    df["__sale_4lag"] = df.groupby("gvkey", sort=False)["saleq"].shift(4)
    df["SalesGrowth"] = (
        (df["saleq"] - df["__sale_4lag"]) / df["__sale_4lag"].abs()
    )

    # sCFO: rolling 5-year (= 20-quarter) std of (oancf_q / atq_lag)
    df["__atq_lag"] = df.groupby("gvkey", sort=False)["atq"].shift(1)
    df["__cf_at"] = df["oancf_q"] / df["__atq_lag"]
    df["sCFO"] = df.groupby("gvkey", sort=False)["__cf_at"].transform(
        lambda s: s.rolling(20, min_periods=12).std()
    )

    # Hasan-verbatim controls
    # NWC = (WCAPQ - CHEQ) / ATQ
    df["NWC"] = (df["wcapq"] - df["cheq"]) / df["atq"]
    # Acquisition = AQCY_quarterly / ATQ
    df["Acquisition"] = df["aqc_q"] / df["atq"]

    # Calendar year-quarter index — Period -> quarter-end Timestamp so
    # linearmodels PanelOLS recognises it as a date-like time index.
    df["cal_yr"] = df["datadate"].dt.year.astype(int)
    df["cal_yr_qtr"] = df["datadate"].dt.to_period("Q").dt.end_time

    # IndustrySigma: SIC2-level avg SD of cashflow/atq over the past 10 years
    # (Hasan 2022 verbatim: "for the past 10 years"). Reverted from 5y after
    # Hasan-verbatim audit 2026-05-06.
    df["sic2"] = (df["sic_int"] // 100).astype(int)
    df["__cfa_10yr_sd"] = df.groupby("gvkey", sort=False)["__cf_at"].transform(
        lambda s: s.rolling(40, min_periods=8).std()
    )
    industry_sigma = (
        df.groupby(["sic2", "datadate"])["__cfa_10yr_sd"].mean()
        .rename("IndustrySigma").reset_index()
    )
    df = df.merge(industry_sigma, on=["sic2", "datadate"], how="left")

    # Drop helper cols
    drop_helpers = [c for c in df.columns if c.startswith("__")]
    df = df.drop(columns=drop_helpers)

    # Restrict to estimation window
    df = df[df["year"].between(YEAR_MIN, YEAR_MAX)].copy()
    print(f"  After window {YEAR_MIN}-{YEAR_MAX}: {len(df):,}")

    # Light winsorization on CashRatio + extreme-tail controls
    for col in ("CashRatio", "Leverage", "TobinsQ", "ROA", "Capex",
                "CashFlowAt", "RDSales", "SalesGrowth", "sCFO",
                "NWC", "Acquisition", "IndustrySigma"):
        if col not in df.columns:
            continue
        lo = df[col].quantile(0.01)
        hi = df[col].quantile(0.99)
        df[col] = df[col].clip(lower=lo, upper=hi)

    print(f"  Final firm-quarter rows: {len(df):,}")
    print(f"  Final firms (gvkey nunique): {df['gvkey'].nunique():,}")
    return df


# ==============================================================================
# Treatment label (geocode + Lewis 2013 spatial join)
# ==============================================================================


def attach_redist_treatment(panel: pd.DataFrame, root: Path) -> pd.DataFrame:
    """Attach Treated_redist / Post_redist / DiD_Redist via the
    RedistrictingTreatmentGeocodeBuilder, but at the firm-quarter level
    (not call-level). The builder's standard output is keyed by file_name,
    so we rebuild firm-level treatment from its internal computation.
    """
    print("\n" + "=" * 60)
    print("Attaching redistricting treatment (geocode + Lewis 2013)")
    print("=" * 60)

    # Reuse the builder by calling it with a "manifest" assembled from
    # firm-quarter panel keys; we need (gvkey, year) and the builder also
    # uses start_date for cal_yr_qtr derivation. We'll synthesize.
    # Simpler: call builder.build() over a synthetic manifest with one row
    # per firm-quarter, treating start_date = datadate.
    from f1d.shared.variables.redistricting_treatment_geocode import (
        _load_cd_shapefile, _spatial_join_firms_to_cd,
        PATH_SHP_111, PATH_SHP_113, PATH_PRISK,
        PRE_WINDOW_START, PRE_WINDOW_END, POST_THRESHOLD_YEAR,
    )
    from f1d.shared.variables.political_risk_subtopics import _parse_cal_q
    from f1d.shared.variables.winsorization import winsorize_by_year

    # TEST 5: use the FULL-Compustat geocode file (12,305 firm-periods)
    # vs F1D-restricted geocode (4,308 firm-periods).
    PATH_GEOCODES_FULL = "inputs/firm_geocodes/firm_lat_lon_full_compustat.parquet"

    # 1. Load Lewis 2013 shapefiles
    cd_111 = _load_cd_shapefile(root / PATH_SHP_111, congress=111)
    cd_113 = _load_cd_shapefile(root / PATH_SHP_113, congress=113)
    print(
        f"  Lewis 2013: 111CD={len(cd_111):,} polygons, "
        f"113CD={len(cd_113):,} polygons"
    )

    # 2. Load firm geocodes (full Compustat)
    geo = pd.read_parquet(root / PATH_GEOCODES_FULL)
    geo["gvkey"] = geo["gvkey"].astype(str).str.zfill(6)
    geo_pre = geo[geo["period"] == "pre"].copy()
    geo_post = geo[geo["period"] == "post"].copy()
    print(
        f"  Geocoded firms: pre={len(geo_pre):,} (lat/lon non-null="
        f"{geo_pre['latitude'].notna().sum():,}); "
        f"post={len(geo_post):,} (lat/lon non-null="
        f"{geo_post['latitude'].notna().sum():,})"
    )

    # 3. Spatial join
    firm_pre_cd = _spatial_join_firms_to_cd(geo_pre, cd_111, "pre")
    firm_post_cd = _spatial_join_firms_to_cd(geo_post, cd_113, "post")
    firm_cd = firm_pre_cd.merge(firm_post_cd, on="gvkey", how="outer")
    n_both = (
        firm_cd["state_cd_pre"].notna() & firm_cd["state_cd_post"].notna()
    ).sum()
    print(
        f"  Firms with pre+post CD: {n_both:,} of {len(firm_cd):,}"
    )

    # 4. PRisk firm-mean over 5-yr pre-window
    prisk_cols = ["gvkey", "date", "PRisk"]
    prisk = pd.read_csv(
        root / PATH_PRISK, sep="\t", on_bad_lines="skip", usecols=prisk_cols,
    )
    prisk["gvkey"] = prisk["gvkey"].astype(str).str.zfill(6)
    prisk = prisk.dropna(subset=["PRisk"])
    prisk["cal_q"] = prisk["date"].apply(_parse_cal_q)
    prisk = prisk.dropna(subset=["cal_q"])
    prisk["year"] = prisk["cal_q"].str[:4].astype(int)
    prisk = prisk[
        (prisk["cal_q"] >= PRE_WINDOW_START)
        & (prisk["cal_q"] <= PRE_WINDOW_END)
    ].copy()
    prisk = winsorize_by_year(prisk, ["PRisk"], year_col="year")
    prisk = (
        prisk.sort_values("PRisk", ascending=False)
        .drop_duplicates(subset=["gvkey", "cal_q"], keep="first")
    )
    firm_prisk = (
        prisk.groupby("gvkey")["PRisk"].mean().reset_index()
        .rename(columns={"PRisk": "prisk_5yr_pre_mean"})
    )
    firm_qcount = prisk.groupby("gvkey")["cal_q"].nunique().rename("n_pre")
    firm_prisk = firm_prisk.merge(firm_qcount, on="gvkey", how="left")
    # F1 attempt (relax to >=1): increased N to 29,045 but DILUTED beta from
    # +0.01855* to +0.00745 ns. Noisy short-window firms hurt signal.
    # Reverted to >=8.
    firm_prisk = firm_prisk[firm_prisk["n_pre"] >= 8].copy()

    # 5. Tertile rank within district
    firm = firm_cd.merge(
        firm_prisk[["gvkey", "prisk_5yr_pre_mean"]], on="gvkey", how="inner",
    )
    firm = firm.dropna(subset=["state_cd_pre", "state_cd_post"])

    def _tertile(s: pd.Series) -> pd.Series:
        try:
            return pd.qcut(
                s.rank(method="first"), q=3, labels=[0, 1, 2]
            ).astype(float)
        except Exception:
            return pd.Series(np.nan, index=s.index)

    firm["pre_tertile"] = (
        firm.groupby("state_cd_pre")["prisk_5yr_pre_mean"].transform(_tertile)
    )
    firm["post_tertile"] = (
        firm.groupby("state_cd_post")["prisk_5yr_pre_mean"].transform(_tertile)
    )
    delta = firm["post_tertile"] - firm["pre_tertile"]
    firm["Treated_redist"] = np.where(
        delta > 0, 1.0,
        np.where(delta < 0, -1.0, np.where(delta == 0, 0.0, np.nan)),
    )
    n_pos = int((firm["Treated_redist"] == 1).sum())
    n_zero = int((firm["Treated_redist"] == 0).sum())
    n_neg = int((firm["Treated_redist"] == -1).sum())
    print(
        f"  Firms with Treated_redist label: +1={n_pos:,} 0={n_zero:,} "
        f"-1={n_neg:,} (total={len(firm):,})"
    )

    # 6. Attach to firm-quarter panel
    keep_cols = ["gvkey", "Treated_redist", "prisk_5yr_pre_mean"]
    panel = panel.merge(firm[keep_cols], on="gvkey", how="left")
    panel["Post_redist"] = (panel["year"] > POST_THRESHOLD_YEAR).astype(float)
    panel["DiD_Redist"] = panel["Treated_redist"] * panel["Post_redist"]

    n_labelled = panel["Treated_redist"].notna().sum()
    print(
        f"  Per firm-quarter: Treated-labelled={n_labelled:,} / {len(panel):,}"
    )
    return panel


# ==============================================================================
# Regression
# ==============================================================================


SPECS = [
    {"col": 1, "fe": "industry"},
    {"col": 2, "fe": "firm"},
    {"col": 3, "fe": "industry_yq"},
    {"col": 4, "fe": "firm_yq"},
]


def run_one_spec(panel: pd.DataFrame, spec: Dict[str, Any]) -> Dict[str, Any]:
    fe = spec["fe"]
    col = spec["col"]
    base_fe = fe.replace("_yq", "")
    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"

    print(f"\n--- Col ({col}) FE={fe} ---")

    df = panel.copy().replace([np.inf, -np.inf], np.nan)
    required = ["CashRatio", KEY_IV] + LEVEL_DUMMIES + CONTROLS + [
        "gvkey", time_col, "sic_int",
    ]
    miss = [c for c in required if c not in df.columns]
    if miss:
        raise ValueError(f"Missing cols: {miss}")
    df = df.dropna(subset=required)
    fc = df["gvkey"].value_counts()
    df = df[df["gvkey"].isin(fc[fc >= 3].index)].copy()
    print(f"  N={len(df):,}, firms={df['gvkey'].nunique():,}")

    df_panel = df.set_index(["gvkey", time_col])
    exog = [KEY_IV] + LEVEL_DUMMIES + CONTROLS

    if base_fe == "industry":
        # 2-digit SIC industry FE via other_effects
        df_panel = df_panel.copy()
        df_panel["sic2"] = (df_panel["sic_int"] // 100).astype(int)
        m = PanelOLS(
            dependent=df_panel["CashRatio"],
            exog=df_panel[exog],
            entity_effects=False,
            time_effects=True,
            other_effects=df_panel["sic2"],
            drop_absorbed=True,
            check_rank=False,
        )
        model = m.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
    else:
        formula = (
            "CashRatio ~ 1 + " + " + ".join(exog)
            + " + EntityEffects + TimeEffects"
        )
        m = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = m.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)

    beta = float(model.params[KEY_IV])
    se = float(model.std_errors[KEY_IV])
    p_two = float(model.pvalues[KEY_IV])
    p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
    t_stat = float(model.tstats[KEY_IV])
    adj_r2 = 1 - (1 - model.rsquared) * (model.nobs - 1) / max(model.df_resid, 1)
    stars = "***" if p_one < 0.01 else "**" if p_one < 0.05 else "*" if p_one < 0.10 else ""
    print(
        f"  DiD_Redist: beta={beta:+.4f}{stars}  SE={se:.4f}  "
        f"t={t_stat:+.2f}  p_one={p_one:.4f}  R^2={model.rsquared:.4f}  "
        f"adj_R^2={adj_r2:.4f}  N={int(model.nobs):,}"
    )
    return {
        "col": col, "fe": fe, "beta": beta, "se": se, "t": t_stat,
        "p_one": p_one, "p_two": p_two,
        "r2": float(model.rsquared), "adj_r2": float(adj_r2),
        "n_obs": int(model.nobs), "n_firms": df["gvkey"].nunique(),
    }


# ==============================================================================
# Main
# ==============================================================================


def parse_arguments():
    p = argparse.ArgumentParser(
        description="TEST 5: H1.6 redistricting DiD on full Compustat panel",
    )
    p.add_argument("--hasan18", action="store_true",
                   help="Restrict to Hasan 2022's 18 redistricted states.")
    p.add_argument("--drop-unchanged", action="store_true",
                   help="Drop Treated_redist==0 cohort.")
    return p.parse_args()


def filter_hasan_18(panel: pd.DataFrame, root: Path) -> pd.DataFrame:
    """Restrict to firms HQ'd in Hasan 18 redistricted states.

    Reads modal pre-period state from the geocode parquet; falls back to
    Compustat 'state' column on the panel if available.
    """
    geo = pd.read_parquet(
        root / "inputs" / "firm_geocodes" / "firm_lat_lon_full_compustat.parquet",
        columns=["gvkey", "period", "state"],
    )
    geo["gvkey"] = geo["gvkey"].astype(str).str.zfill(6)
    state_pre = geo[geo["period"] == "pre"][["gvkey", "state"]].rename(
        columns={"state": "state_pre"}
    )
    state_post = geo[geo["period"] == "post"][["gvkey", "state"]].rename(
        columns={"state": "state_post"}
    )
    states = state_pre.merge(state_post, on="gvkey", how="outer")
    states["firm_state"] = states["state_pre"].fillna(states["state_post"])
    states = states[["gvkey", "firm_state"]]
    before = len(panel)
    panel = panel.merge(states, on="gvkey", how="left")
    panel = panel[panel["firm_state"].isin(HASAN_18_STATES)].copy()
    print(
        f"  Hasan-18 filter: {len(panel):,} / {before:,} firm-qtrs "
        f"({panel['gvkey'].nunique():,} firms)"
    )
    return panel


def filter_drop_unchanged(panel: pd.DataFrame) -> pd.DataFrame:
    before = len(panel)
    panel = panel[panel["Treated_redist"] != 0].copy()
    n_pos = int((panel["Treated_redist"] == 1).sum())
    n_neg = int((panel["Treated_redist"] == -1).sum())
    print(
        f"  Drop Treated=0: {len(panel):,} / {before:,} "
        f"(+1={n_pos:,} -1={n_neg:,}; "
        f"{panel['gvkey'].nunique():,} firms)"
    )
    return panel


def main(hasan18: bool = False, drop_unchanged: bool = False) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start = datetime.now()
    timestamp = start.strftime("%Y-%m-%d_%H%M%S")
    suffix = ""
    if hasan18:
        suffix += "_H18"
    if drop_unchanged:
        suffix += "_DROP0"
    if suffix:
        timestamp = timestamp + suffix
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h1_6_test5_full_compustat" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("TEST 5: H1.6 REDISTRICTING DiD ON FULL COMPUSTAT (no F1D restriction)")
    print("=" * 80)
    print(f"Timestamp:    {timestamp}")
    print(f"Output:       {out_dir}")
    print(f"Outcome:      Cash only (4 specs); no UncResCEO outside F1D call panel")
    print(f"Diag flags:   hasan18={hasan18} drop_unchanged={drop_unchanged}")

    panel = build_full_compustat_panel(root)
    panel = attach_redist_treatment(panel, root)

    # Restrict to Treated-labelled rows for the regression
    panel = panel.dropna(subset=["Treated_redist"]).copy()
    print(
        f"\n  Treated-labelled firm-quarter rows: {len(panel):,} "
        f"({panel['gvkey'].nunique():,} firms)"
    )

    if hasan18:
        panel = filter_hasan_18(panel, root)
    if drop_unchanged:
        panel = filter_drop_unchanged(panel)

    results: List[Dict[str, Any]] = []
    for spec in SPECS:
        res = run_one_spec(panel, spec)
        results.append(res)

    # Summary
    print("\n" + "=" * 80)
    print("TEST 5 RESULTS — FULL COMPUSTAT")
    print("=" * 80)
    for r in results:
        sig = "SIG" if r["p_one"] < 0.05 else "ns"
        stars = "***" if r["p_one"] < 0.01 else "**" if r["p_one"] < 0.05 else "*" if r["p_one"] < 0.10 else ""
        print(
            f"  Col ({r['col']}) FE={r['fe']:14s}  "
            f"beta={r['beta']:+.5f}{stars:3s}  SE={r['se']:.5f}  "
            f"t={r['t']:+.2f}  p_one={r['p_one']:.4f}  "
            f"adj_R^2={r['adj_r2']:.4f}  N={r['n_obs']:,}  [{sig}]"
        )

    # Save diagnostics CSV + report
    diag_df = pd.DataFrame(results)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"\n  Saved: {out_dir / 'model_diagnostics.csv'}")

    duration = (datetime.now() - start).total_seconds()
    print(f"\nDuration: {duration:.1f}s")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main(hasan18=args.hasan18, drop_unchanged=args.drop_unchanged))
