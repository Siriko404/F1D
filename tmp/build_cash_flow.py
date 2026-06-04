"""CASH_FLOW = oibdpq / atq_lag1. Table 1 Panel A: N=75,287 mean=0.01 SD=0.06 p50=0.03"""
import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path("inputs/comp_na_daily_all/comp_na_daily_all.parquet")
COLS = ["gvkey", "datadate", "fyearq", "fqtr", "sic", "curcdq", "fic",
        "atq", "saleq", "oibdpq"]

df = pd.read_parquet(ROOT, columns=COLS)
for c in ["atq", "saleq", "oibdpq"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df[(df["fyearq"] >= 2010) & (df["fyearq"] <= 2015)]
df = df[df["fqtr"].isin([1, 2, 3, 4])]
df = df[(df["curcdq"] == "USD") & (df["fic"] == "USA")]
df = df[(df["atq"] > 0) & (df["saleq"] > 0)]
sic_num = pd.to_numeric(df["sic"], errors="coerce")
df = df[~(sic_num.between(6000, 6999) | sic_num.between(4900, 4999))]
df = df[df["atq"] > 10]

print(f"After filters: {len(df):,} obs")

# Lagged assets
df = df.sort_values(["gvkey", "datadate"])
df["atq_lag1"] = df.groupby("gvkey")["atq"].shift(1)

# CASH_FLOW = oibdpq / lagged atq
# CRITICAL: oibdpq in Compustat Quarterly is ALREADY quarterly (NOT YTD)
# per Campello sample.py line 183: "FIX 2026-05-26: oibdpq is QUARTERLY in Compustat"
df["CF_raw"] = df["oibdpq"] / df["atq_lag1"]

cf = df.dropna(subset=["oibdpq", "atq_lag1"]).copy()
del df

lo, hi = cf["CF_raw"].quantile(0.01), cf["CF_raw"].quantile(0.99)
cf["CASH_FLOW"] = cf["CF_raw"].clip(lo, hi)

paper = {"N": 75287, "mean": 0.01, "SD": 0.06, "p50": 0.03}
our = {"N": len(cf), "mean": cf["CASH_FLOW"].mean(),
       "SD": cf["CASH_FLOW"].std(), "p50": cf["CASH_FLOW"].median()}

print("\n--- CASH_FLOW vs Paper (Table 1 Panel A) ---")
for k in ["N", "mean", "SD", "p50"]:
    p, o = paper[k], our[k]
    pct = (o - p) / p * 100 if p != 0 else float("nan")
    flag = " ***" if abs(pct) > 15 else ""
    print(f"  {k:>6s}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%{flag}")
