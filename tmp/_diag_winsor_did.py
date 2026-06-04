"""Winsorization-dimension test (auditor H1 / branch-b).

The paper says only "All variables are winsorized at the 1% level" — SILENT on
whether winsorization is WITHIN calendar quarter or POOLED across all
firm-quarters. Our runner winsorizes WITHIN cal_yr_qtr. If the Brexit cash
response is concentrated in 2016:Q3-Q4, within-quarter 1% clipping can remove
exactly the treated post-period spikes -> attenuating BOTH arms and BOTH DVs
(matches our universal null).

This reruns CASH (market + textual) under three winsor modes, holding the rest
of the pipeline byte-identical to run_h1_5_brexit_did._build_and_fit:
  within_quarter  (current)
  pooled          (clip on the whole column)
  none            (no winsorization)

The build body is copied from _build_and_fit with ONLY the winsor line
parametrized; all imports/helpers come from the runner + step7 so nothing
else can drift.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_rp = ROOT / "src" / "f1d" / "econometric" / "run_h1_5_brexit_did.py"
_rs = importlib.util.spec_from_file_location("_runner", _rp)
_runner = importlib.util.module_from_spec(_rs)
_rs.loader.exec_module(_runner)

from step7_fullpanel_hypothesis import (
    FIRM_BUILDERS, POST_Q, _build, _calendar_lag1, _latest,
)

_cash_dv_t8 = _runner._cash_dv_t8
_statsum_meanest_z = _runner._statsum_meanest_z
WINSOR = 0.01


def _winsorize(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    if mode == "within_quarter":
        df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
            lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
    elif mode == "pooled":
        lo, hi = df["CASH"].quantile(WINSOR), df["CASH"].quantile(1 - WINSOR)
        df["CASH"] = df["CASH"].clip(lo, hi)
    elif mode == "none":
        pass
    else:
        raise ValueError(mode)
    return df


def _build_and_fit_winsor(treatment_df, mode: str) -> dict:
    """Copy of runner._build_and_fit with ONLY the winsor step swapped."""
    from linearmodels.panel import PanelOLS

    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq", "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(tt[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_cash_dv_t8(), on=["gvkey", "cal_yr_qtr"], how="inner")
    df = df[df["atq"] > 0].copy(); df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls); col = [c for c in b.columns if c not in ("gvkey", "cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey", "cal_yr_qtr"], how="left")
        firm_cols.append(col)
    df = df.merge(_calendar_lag1(
        df[["gvkey", "cal_yr_qtr", "log_assets"]], "log_assets").rename(
        columns={"log_assets": "log_assets_l1"}), on=["gvkey", "cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    cons = _statsum_meanest_z()
    df = df.merge(_calendar_lag1(cons, "cons_fwd"), on=["gvkey", "cal_yr_qtr"], how="left")

    df = _winsorize(df, mode)  # <-- ONLY change

    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)

    reg_cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH", "indqtr_code"] + reg_cols).copy()
    pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    res = PanelOLS(pdat["CASH"], pdat[reg_cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    return {"delta_hat": float(res.params["POST_x_HIGH"]),
            "se": float(res.std_errors["POST_x_HIGH"]),
            "pvalue": float(res.pvalues["POST_x_HIGH"]), "nobs": int(res.nobs)}


def main() -> None:
    print("=" * 72)
    print("WINSORIZATION-DIMENSION TEST — CASH (T8 net-of-cash), both arms")
    print("=" * 72)
    print("Campello: market +0.231*** | textual +0.357***\n")

    mkt = _runner._load_market_treatment()
    txt = _runner._load_textual_treatment()

    print(f"{'arm':<16} {'winsor':<16} {'δ̂':>9} {'SE':>7} {'p':>7} {'N':>8}")
    print("-" * 72)
    for arm_name, trt in (("MARKET", mkt), ("TEXTUAL", txt)):
        for mode in ("within_quarter", "pooled", "none"):
            r = _build_and_fit_winsor(trt, mode)
            print(f"{arm_name:<16} {mode:<16} {r['delta_hat']:>+9.4f} "
                  f"{r['se']:>7.4f} {r['pvalue']:>7.4f} {r['nobs']:>8,}")
        print()
    print("-" * 72)
    print("Read: if pooled/none jump toward +0.231 / +0.357, winsor dim is the lever.")


if __name__ == "__main__":
    main()
