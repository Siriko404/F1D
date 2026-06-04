#!/usr/bin/env python3
"""GATE-1 / Link-1 external validity: does analyst cash-attention track firm cash?

  STOCK_score_call ~ CashRatio  + firm FE (gvkey) + time FE (cal_yr_qtr), firm-clustered SE.

Advisor design (locked):
  - STOCK sub-score only (DISPOSITION excluded -> size confound).
  - BINSCATTER FIRST: residualize both on firm+time FE, decile means -> read the SHAPE.
  - HIGH-CASH CONTRAST = PRIMARY (Jensen: high idle cash draws scrutiny; distress low-cash
    also draws liquidity Qs -> a linear ~0 is NOT a channel null, only a flat HIGH-cash region is).
  - Linear slope = weaker omnibus.

Two-way FE via iterative demeaning (Gauss-Seidel); FWL -> slope == two-way FE OLS.
Cluster-robust SE by gvkey on the residualized regression.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "outputs" / "variables" / "h1_cash_holdings" / "2026-04-19_182724" / "h1_cash_holdings_panel.parquet"
SCORE = ROOT / "tmp" / "_cash_stock_score_call.parquet"
MIN_QA = 3   # require >=3 analyst Q&A turns so the share is meaningful

def demean_2way(df, cols, g1, g2, n_iter=20, tol=1e-9):
    """Iterative two-way within transform. Returns df with cols residualized on g1,g2 FE."""
    out = df[cols].copy()
    for _ in range(n_iter):
        maxchg = 0.0
        for g in (g1, g2):
            grp = df[g].values
            for c in cols:
                m = out[c].groupby(grp).transform("mean")
                maxchg = max(maxchg, float(np.abs(m).max()))
                out[c] = out[c] - m
        if maxchg < tol:
            break
    return out

def cluster_ols(y, x, groups, label):
    """OLS y~x (both FE-residualized) with cluster-robust SE by groups. FWL slope."""
    X = sm.add_constant(x)
    res = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
    b = np.asarray(res.params)[1]; se = np.asarray(res.bse)[1]
    t = np.asarray(res.tvalues)[1]; p = np.asarray(res.pvalues)[1]
    star = "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""
    print(f"  {label:28s} beta={b:+.5f}  se={se:.5f}  t={t:+.2f}  p={p:.4f} {star}")
    return b, se, p

def main():
    if not SCORE.exists():
        raise SystemExit(f"cache missing: {SCORE} (run _build_stock_score_cache.py first)")
    score = pd.read_parquet(SCORE)
    panel = pd.read_parquet(PANEL, columns=["file_name", "gvkey", "CashRatio", "start_date", "ff12_code"])

    df = panel.merge(score, on="file_name", how="inner")
    n0 = len(df)
    df = df[~df["ff12_code"].isin([8, 11])]                 # main sample (drop fin/util)
    df = df.dropna(subset=["CashRatio", "stock_score", "gvkey"])
    df = df[df["n_qa_turns"] >= MIN_QA]
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df = df.dropna(subset=["start_date"])
    df["cal_yr_qtr"] = df["start_date"].dt.year.astype(str) + "Q" + df["start_date"].dt.quarter.astype(str)
    # light winsor CashRatio at 1/99 (ratio has fat tails); stock_score is a bounded share -> leave
    lo, hi = df["CashRatio"].quantile([.01, .99])
    df["CashRatio"] = df["CashRatio"].clip(lo, hi)
    df["gvkey"] = df["gvkey"].astype(str)

    print(f"merged {n0:,} -> analysis N={len(df):,} | firms={df['gvkey'].nunique():,} | "
          f"quarters={df['cal_yr_qtr'].nunique()} | MIN_QA={MIN_QA}")
    print(f"stock_score: mean {df['stock_score'].mean():.4f} med {df['stock_score'].median():.4f} | "
          f"CashRatio: mean {df['CashRatio'].mean():.4f} med {df['CashRatio'].median():.4f}")

    # ---- residualize on firm + time FE ----
    rd = demean_2way(df, ["stock_score", "CashRatio"], "gvkey", "cal_yr_qtr")
    ry, rx = rd["stock_score"].values, rd["CashRatio"].values
    g = df["gvkey"].values

    # ---- BINSCATTER: decile means of residualized stock vs residualized CashRatio ----
    print("\n[BINSCATTER] residualized (firm+time FE) — decile of CashRatio resid -> mean stock resid")
    dec = pd.qcut(rx, 10, labels=False, duplicates="drop")
    bs = pd.DataFrame({"dec": dec, "rx": rx, "ry": ry}).groupby("dec").agg(
        cashresid=("rx", "mean"), stockresid=("ry", "mean"), n=("ry", "size"))
    for _, r in bs.iterrows():
        bar = "#" * int(max(0, (r["stockresid"] - bs["stockresid"].min()) / (bs["stockresid"].max() - bs["stockresid"].min() + 1e-12) * 40))
        print(f"  d{int(_)+1:2d}  cashresid={r['cashresid']:+.4f}  stockresid={r['stockresid']:+.5f}  n={int(r['n']):5d} |{bar}")

    # ---- LINEAR omnibus (weaker) ----
    print("\n[LINEAR omnibus]  stock_score ~ CashRatio + firmFE + timeFE")
    cluster_ols(ry, rx, g, "CashRatio (linear)")

    # ---- HIGH-CASH PRIMARY: top-tercile dummy (Jensen-faithful) ----
    print("\n[HIGH-CASH primary]  top-tercile CashRatio dummy")
    t1, t2 = df["CashRatio"].quantile([1/3, 2/3])
    high = (df["CashRatio"] >= t2).astype(float).values
    # residualize the dummy on FE too (FWL)
    dfh = df.assign(_high=high)
    rh = demean_2way(dfh, ["stock_score", "_high"], "gvkey", "cal_yr_qtr")
    cluster_ols(rh["stock_score"].values, rh["_high"].values, g, "1[CashRatio>=p67]")

    # ---- tercile means (asymmetry read) ----
    df["_terc"] = pd.cut(df["CashRatio"], [-np.inf, t1, t2, np.inf], labels=["low", "mid", "high"])
    print("\n[TERCILE raw means] stock_score by CashRatio tercile (asymmetry check)")
    tm = df.groupby("_terc", observed=True)["stock_score"].agg(["mean", "size"])
    for k, r in tm.iterrows():
        print(f"  {k:5s}  stock_score={r['mean']:.4f}  n={int(r['size']):,}")

if __name__ == "__main__":
    main()
