"""SIZE = log(total assets). Table 1 Panel A: N=78,062 mean=6.19 SD=2.08 p50=6.15"""
import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path("inputs/comp_na_daily_all/comp_na_daily_all.parquet")
COLS = ["gvkey", "datadate", "fyearq", "fqtr", "sic", "curcdq", "fic", "atq", "saleq"]

df = pd.read_parquet(ROOT, columns=COLS)
for c in ["atq", "saleq"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Same filters as CASH
df = df[(df["fyearq"] >= 2010) & (df["fyearq"] <= 2015)]
df = df[df["fqtr"].isin([1, 2, 3, 4])]
df = df[(df["curcdq"] == "USD") & (df["fic"] == "USA")]
df = df[(df["atq"] > 0) & (df["saleq"] > 0)]
sic_num = pd.to_numeric(df["sic"], errors="coerce")
df = df[~(sic_num.between(6000, 6999) | sic_num.between(4900, 4999))]
df = df[df["atq"] > 10]

print(f"After filters: {len(df):,} obs")

# SIZE = ln(atq)
df["SIZE_raw"] = np.log(df["atq"])
size = df.dropna(subset=["atq"])
lo, hi = size["SIZE_raw"].quantile(0.01), size["SIZE_raw"].quantile(0.99)
size = size.copy()
size["SIZE"] = size["SIZE_raw"].clip(lo, hi)

paper = {"N": 78062, "mean": 6.19, "SD": 2.08, "p50": 6.15}
our = {"N": len(size), "mean": size["SIZE"].mean(),
       "SD": size["SIZE"].std(), "p50": size["SIZE"].median()}

print("\n--- SIZE vs Paper (Table 1 Panel A) ---")
for k in ["N", "mean", "SD", "p50"]:
    p, o = paper[k], our[k]
    pct = (o - p) / p * 100 if p != 0 else float("nan")
    flag = " ***" if abs(pct) > 15 else ""
    print(f"  {k:>6s}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%{flag}")
