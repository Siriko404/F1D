"""Raw seasonal 2x2 DiD + DV-construction sweep — does the effect exist before
any FE/controls, and which CASH build surfaces it?

Campello's identifying contrast (verbatim): 2016:Q3-Q4 vs 2015:Q3-Q4. Compute
the raw 2x2 DiD mean(CASH) for treated/control x pre/post, with NO FE and NO
controls, under three DV constructions:

  cheq_net   = cheq / (atq_{t-1} - cheq_{t-1})    [CURRENT — Table 8 net-of-cash, cheq=cash+STI]
  chq_net    = chq  / (atq_{t-1} - chq_{t-1})     [Table 8 net, "total cash holdings"=cash only]
  cheq_gross = cheq / atq_{t-1}                    [Table 1 gross def]

Each pooled-1% winsorized. Reports DV scale + the raw DiD per build, both arms.
If a build's raw 2x2 DiD ~ +0.23/+0.36, the effect IS in the data and our
FE/controls or DV scale is killing it. If all ~0, the effect isn't surfacing.
Read-only.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

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
from step7_fullpanel_hypothesis import _prev_q

COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")
PRE_Q = [20153, 20154]
POST_Q = [20163, 20164]
WINSOR = 0.01


def _cash_variants() -> pd.DataFrame:
    df = pq.read_table(COMP, columns=["gvkey", "datadate", "curcdq", "loc",
                       "consol", "indfmt", "datafmt", "atq", "cheq", "chq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"] == "USD") & (df["loc"] == "USA") & (df["consol"] == "C")
            & (df["indfmt"] == "INDL") & (df["datafmt"] == "STD")].copy()
    for c in ("atq", "cheq", "chq"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10 + df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey", "cal_yr_qtr", "datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last")
    src = df[["gvkey", "cal_yr_qtr", "atq", "cheq", "chq"]].rename(
        columns={"cal_yr_qtr": "_pq", "atq": "atq_l1", "cheq": "cheq_l1", "chq": "chq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey", "_pq"], how="left").drop(columns="_pq")

    out = df[["gvkey", "cal_yr_qtr"]].copy()
    d_cheq_net = df["atq_l1"] - df["cheq_l1"]
    out["cheq_net"] = np.where((df["cheq"].notna()) & (d_cheq_net > 0),
                               df["cheq"] / d_cheq_net, np.nan)
    d_chq_net = df["atq_l1"] - df["chq_l1"]
    out["chq_net"] = np.where((df["chq"].notna()) & (d_chq_net > 0),
                              df["chq"] / d_chq_net, np.nan)
    out["cheq_gross"] = np.where((df["cheq"].notna()) & (df["atq_l1"] > 0),
                                 df["cheq"] / df["atq_l1"], np.nan)
    return out


def _winsor(s: pd.Series) -> pd.Series:
    return s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR))


def _raw_did(df: pd.DataFrame, col: str) -> dict:
    d = df.dropna(subset=[col]).copy()
    d = d[d["cal_yr_qtr"].isin(PRE_Q + POST_Q)].copy()
    d[col] = _winsor(d[col])
    d["post"] = d["cal_yr_qtr"].isin(POST_Q)
    g = d.groupby(["HIGH_UK_EXPOSURE", "post"])[col].mean().unstack()
    tt_pre, tt_post = g.loc[1, False], g.loc[1, True]
    c_pre, c_post = g.loc[0, False], g.loc[0, True]
    did = (tt_post - tt_pre) - (c_post - c_pre)
    return {"t_pre": tt_pre, "t_post": tt_post, "c_pre": c_pre, "c_post": c_post,
            "did": did, "mean": d[col].mean(), "med": d[col].median(),
            "sd": d[col].std(), "n": len(d)}


def main() -> None:
    cv = _cash_variants()
    arms = [("MARKET", _runner._load_market_treatment(), 0.231),
            ("TEXTUAL", _runner._load_textual_treatment(), 0.357)]
    for arm, trt, target in arms:
        tt = trt.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
        df = cv.merge(tt[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
        print("=" * 74)
        print(f"{arm} arm — RAW seasonal 2x2 DiD (pre=2015Q3-Q4, post=2016Q3-Q4)"
              f"   target {target:+.3f}")
        print("=" * 74)
        print(f"  {'DV build':<12} {'mean':>6} {'med':>6} {'SD':>6} | "
              f"{'T_pre':>7} {'T_post':>7} {'C_pre':>7} {'C_post':>7} {'rawDiD':>8}")
        print("  " + "-" * 70)
        for col in ("cheq_net", "chq_net", "cheq_gross"):
            r = _raw_did(df, col)
            print(f"  {col:<12} {r['mean']:>6.3f} {r['med']:>6.3f} {r['sd']:>6.3f} | "
                  f"{r['t_pre']:>7.3f} {r['t_post']:>7.3f} {r['c_pre']:>7.3f} "
                  f"{r['c_post']:>7.3f} {r['did']:>+8.4f}")
        print()
    print("Read: does any DV build show raw DiD ~ target? Which build is best-scaled")
    print("      (mean near Campello Table1 gross ~0.20)?")


if __name__ == "__main__":
    main()
