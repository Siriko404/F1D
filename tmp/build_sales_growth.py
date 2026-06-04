"""SALES_GROWTH = YoY % change in quarterly sales. Table 1 Panel A: N=71,637 mean=0.16 SD=0.62 p50=0.06"""
import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path("inputs/comp_na_daily_all/comp_na_daily_all.parquet")
COLS = ["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq"]

df = pd.read_parquet(ROOT, columns=COLS)
for c in ["atq","saleq"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df[(df["fyearq"]>=2009)&(df["fyearq"]<=2015)]  # need 2009 for YoY lag
df = df[df["fqtr"].isin([1,2,3,4])]
df = df[(df["curcdq"]=="USD")&(df["fic"]=="USA")]
df = df[(df["atq"]>0)&(df["saleq"]>0)]
sic = pd.to_numeric(df["sic"], errors="coerce")
df = df[~(sic.between(6000,6999)|sic.between(4900,4999))]
df = df[df["atq"]>10]

print(f"After filters: {len(df):,} obs")

# YoY % change: saleq_t / saleq_{t-4} - 1
df = df.sort_values(["gvkey","datadate"])
df["saleq_lag4"] = df.groupby("gvkey")["saleq"].shift(4)
df["SG_raw"] = df["saleq"] / df["saleq_lag4"] - 1

sg = df.dropna(subset=["saleq","saleq_lag4"]).copy()
sg = sg[sg["fyearq"] >= 2010]  # Table 1 reports 2010-2015 only
del df

lo, hi = sg["SG_raw"].quantile(0.01), sg["SG_raw"].quantile(0.99)
sg["SALES_GROWTH"] = sg["SG_raw"].clip(lo, hi)

paper = {"N":71637, "mean":0.16, "SD":0.62, "p50":0.06}
our = {"N":len(sg), "mean":sg["SALES_GROWTH"].mean(),
       "SD":sg["SALES_GROWTH"].std(), "p50":sg["SALES_GROWTH"].median()}

print("\n--- SALES_GROWTH vs Paper (Table 1 Panel A) ---")
for k in ["N","mean","SD","p50"]:
    p, o = paper[k], our[k]
    pct = (o-p)/p*100 if p!=0 else float("nan")
    flag = " ***" if abs(pct)>15 else ""
    print(f"  {k:>6s}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%{flag}")
