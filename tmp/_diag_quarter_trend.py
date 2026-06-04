"""Parallel-trends check: mean CASH per quarter, treated vs control, 2010-2016.

Uses cheq_gross (Table 1 scale, mean ~0.17 ~ Campello 0.20 — best-behaved DV),
pooled 1% winsor. Prints treated mean, control mean, and gap (T-C) per quarter
for both arms. POST window = 2016Q3-Q4 (marked *).

Reveals: (a) are pre-trends parallel (DiD validity)? (b) is there ANY
Brexit-timed divergence in the T-C gap? (c) where does the full-panel +0.076
come from? Read-only.
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
POST_Q = [20163, 20164]
WINSOR = 0.01


def _cash_gross() -> pd.DataFrame:
    df = pq.read_table(COMP, columns=["gvkey", "datadate", "curcdq", "loc",
                       "consol", "indfmt", "datafmt", "atq", "cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"] == "USD") & (df["loc"] == "USA") & (df["consol"] == "C")
            & (df["indfmt"] == "INDL") & (df["datafmt"] == "STD")].copy()
    for c in ("atq", "cheq"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10 + df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey", "cal_yr_qtr", "datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last")
    src = df[["gvkey", "cal_yr_qtr", "atq"]].rename(columns={"cal_yr_qtr": "_pq", "atq": "atq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey", "_pq"], how="left").drop(columns="_pq")
    df = df[df["cheq"].notna() & (df["atq_l1"] > 0)].copy()
    df["CASH"] = df["cheq"] / df["atq_l1"]
    return df[["gvkey", "cal_yr_qtr", "CASH"]]


def main() -> None:
    cash = _cash_gross()
    cash["CASH"] = cash["CASH"].clip(cash["CASH"].quantile(WINSOR),
                                     cash["CASH"].quantile(1 - WINSOR))
    arms = [("MARKET", _runner._load_market_treatment()),
            ("TEXTUAL", _runner._load_textual_treatment())]
    qs = [y * 10 + q for y in range(2010, 2017) for q in range(1, 5)]

    for arm, trt in arms:
        tt = trt.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
        df = cash.merge(tt[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
        g = (df.groupby(["cal_yr_qtr", "HIGH_UK_EXPOSURE"])["CASH"].mean()
             .unstack().reindex(qs))
        print("=" * 50)
        print(f"{arm} — mean CASH (cheq_gross) per quarter")
        print("=" * 50)
        print(f"  {'qtr':>6} {'treated':>8} {'control':>8} {'T-C gap':>8}")
        base_gap = None
        for q in qs:
            if q not in g.index or pd.isna(g.loc[q, 1]) or pd.isna(g.loc[q, 0]):
                continue
            t, c = g.loc[q, 1], g.loc[q, 0]
            gap = t - c
            if q == 20153:
                base_gap = gap
            mark = " *POST" if q in POST_Q else ""
            dgap = f"  Δ{gap - base_gap:+.3f}" if base_gap is not None else ""
            print(f"  {q:>6} {t:>8.3f} {c:>8.3f} {gap:>+8.3f}{mark}{dgap}")
        print()
    print("Read: is T-C gap flat pre-2016 (parallel trends)? does it JUMP at")
    print("      2016Q3-Q4 (the effect)? Δ vs 2015Q3 baseline shown.")


if __name__ == "__main__":
    main()
