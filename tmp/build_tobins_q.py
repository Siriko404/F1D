"""TOBIN_Q = (cshoq*prccq + atq - ceqq + txditcq) / atq. Table 1 Panel A: N=73,353 mean=2.11 SD=1.59 p50=1.57"""
import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path("inputs/comp_na_daily_all/comp_na_daily_all.parquet")
COLS = ["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic",
        "atq","saleq","cshoq","prccq","ceqq","txditcq"]

df = pd.read_parquet(ROOT, columns=COLS)
for c in ["atq","saleq","cshoq","prccq","ceqq","txditcq"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["txditcq"] = df["txditcq"].fillna(0)  # standard: missing = no deferred taxes

df = df[(df["fyearq"]>=2010)&(df["fyearq"]<=2015)]
df = df[df["fqtr"].isin([1,2,3,4])]
df = df[(df["curcdq"]=="USD")&(df["fic"]=="USA")]
df = df[(df["atq"]>0)&(df["saleq"]>0)]
sic = pd.to_numeric(df["sic"], errors="coerce")
df = df[~(sic.between(6000,6999)|sic.between(4900,4999))]
df = df[df["atq"]>10]

print(f"After filters: {len(df):,} obs")

# Tobin's Q = (MVE + ATQ - CEQQ + TXDITCQ) / ATQ
df["MVE"] = df["cshoq"] * df["prccq"]
df["Q_raw"] = (df["MVE"] + df["atq"] - df["ceqq"] + df["txditcq"]) / df["atq"]

q = df.dropna(subset=["cshoq","prccq","ceqq","txditcq","atq"]).copy()
del df

lo, hi = q["Q_raw"].quantile(0.01), q["Q_raw"].quantile(0.99)
q["TOBIN_Q"] = q["Q_raw"].clip(lo, hi)

paper = {"N":73353, "mean":2.11, "SD":1.59, "p50":1.57}
our = {"N":len(q), "mean":q["TOBIN_Q"].mean(),
       "SD":q["TOBIN_Q"].std(), "p50":q["TOBIN_Q"].median()}

print("\n--- TOBIN_Q vs Paper (Table 1 Panel A) ---")
for k in ["N","mean","SD","p50"]:
    p, o = paper[k], our[k]
    pct = (o-p)/p*100 if p!=0 else float("nan")
    flag = " ***" if abs(pct)>15 else ""
    print(f"  {k:>6s}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%{flag}")

# Sensitivity: no txditcq
q2 = q.copy()
q2["Q_notx"] = ((q["MVE"] + q["atq"] - q["ceqq"]) / q["atq"]).clip(
    ((q["MVE"] + q["atq"] - q["ceqq"]) / q["atq"]).quantile(.01),
    ((q["MVE"] + q["atq"] - q["ceqq"]) / q["atq"]).quantile(.99))
print("\n--- Sensitivity: without deferred taxes ---")
our2 = {"N":len(q2), "mean":q2["Q_notx"].mean(),
        "SD":q2["Q_notx"].std(), "p50":q2["Q_notx"].median()}
for k in ["N","mean","SD","p50"]:
    p, o = paper[k], our2[k]
    pct = (o-p)/p*100 if p!=0 else float("nan")
    print(f"  {k:>6s}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%")
