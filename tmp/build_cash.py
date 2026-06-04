"""Build CASH variable per Campello et al. (2022) definition.
CASH = cash and short-term investments / lagged total assets.
Validates against Table 1 Panel A: N=78,044, mean=0.22, SD=0.25, p50=0.12.

MEMORY-AWARE: reads only required columns, drops intermediates.
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path("inputs/comp_na_daily_all/comp_na_daily_all.parquet")
COLS = ["gvkey", "datadate", "fyearq", "fqtr", "sic",
        "curcdq", "fic", "cheq", "atq", "saleq"]

# ── Load (columns only) ──────────────────────────────────────────────────
df = pd.read_parquet(ROOT, columns=COLS)

# ── Filters (Compustat-level, from paper Table C1) ──────────────────────
# 1. Time: 2010:Q1–2015:Q4 (Table 1 pre-Brexit)
df = df[(df["fyearq"] >= 2010) & (df["fyearq"] <= 2015)].copy()
df = df[df["fqtr"].isin([1, 2, 3, 4])]

# 2. US firms
df = df[(df["curcdq"] == "USD") & (df["fic"] == "USA")]

# 3. Non-negative fundamentals
df = df[(df["atq"] > 0) & (df["saleq"] > 0)]

# 4. Drop financials/utilities
sic_num = pd.to_numeric(df["sic"], errors="coerce")
df = df[~(sic_num.between(6000, 6999) | sic_num.between(4900, 4999))]

# 5. Assets > $10M
df = df[df["atq"] > 10]

print(f"After Compustat filters: {len(df):,} obs, {df['gvkey'].nunique():,} firms")

# ── Convert Decimal to float ──────────────────────────────────────────────
for c in ["cheq", "atq", "saleq"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# ── Construct CASH ────────────────────────────────────────────────────────
df = df.sort_values(["gvkey", "datadate"])
df["atq_lag1"] = df.groupby("gvkey")["atq"].shift(1)
df["CASH_raw"] = df["cheq"] / df["atq_lag1"]

cash = df.dropna(subset=["cheq", "atq_lag1"]).copy()
del df  # free memory

# ── Winsorize 1% two-sided ───────────────────────────────────────────────
lo = cash["CASH_raw"].quantile(0.01)
hi = cash["CASH_raw"].quantile(0.99)
cash["CASH"] = cash["CASH_raw"].clip(lo, hi)

# ── Compare ───────────────────────────────────────────────────────────────
paper = {"N": 78044, "mean": 0.22, "SD": 0.25, "p50": 0.12}
our = {"N": len(cash), "mean": cash["CASH"].mean(),
       "SD": cash["CASH"].std(), "p50": cash["CASH"].median()}

print("\n--- CASH vs Paper (Table 1 Panel A) ---")
for k in ["N", "mean", "SD", "p50"]:
    p, o = paper[k], our[k]
    pct = (o - p) / p * 100 if p != 0 else float("nan")
    flag = " ***" if abs(pct) > 15 else ""
    print(f"  {k:>6s}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%{flag}")

print(f"\nCASH winsor bounds: [{lo:.4f}, {hi:.4f}]")
print(f"CASH quantiles: p25={cash['CASH'].quantile(.25):.4f}  p75={cash['CASH'].quantile(.75):.4f}")

# ── Sensitivity: contemporaneous denominator ─────────────────────────────
df2 = pd.read_parquet(ROOT, columns=COLS)
df2 = df2[(df2["fyearq"] >= 2010) & (df2["fyearq"] <= 2015)]
df2 = df2[df2["fqtr"].isin([1, 2, 3, 4])]
df2 = df2[(df2["curcdq"] == "USD") & (df2["fic"] == "USA")]
df2 = df2[(df2["atq"] > 0) & (df2["saleq"] > 0)]
sic2 = pd.to_numeric(df2["sic"], errors="coerce")
df2 = df2[~(sic2.between(6000, 6999) | sic2.between(4900, 4999))]
df2 = df2[df2["atq"] > 10]
for c in ["cheq", "atq", "saleq"]:
    df2[c] = pd.to_numeric(df2[c], errors="coerce")
df2["CASH_raw"] = df2["cheq"] / df2["atq"]
cash2 = df2.dropna(subset=["cheq", "atq"]).copy()
del df2
lo2, hi2 = cash2["CASH_raw"].quantile(0.01), cash2["CASH_raw"].quantile(0.99)
cash2["CASH"] = cash2["CASH_raw"].clip(lo2, hi2)

print("\n--- Sensitivity: contemporaneous ATQ ---")
our2 = {"N": len(cash2), "mean": cash2["CASH"].mean(),
        "SD": cash2["CASH"].std(), "p50": cash2["CASH"].median()}
for k in ["N", "mean", "SD", "p50"]:
    p, o = paper[k], our2[k]
    pct = (o - p) / p * 100 if p != 0 else float("nan")
    flag = " ***" if abs(pct) > 15 else ""
    print(f"  {k:>6s}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%{flag}")
