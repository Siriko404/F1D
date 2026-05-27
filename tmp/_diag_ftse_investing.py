"""Compare investing.com FTSE100 with yfinance/Yahoo."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
INV = Path(r"C:\Users\sinas\Downloads\FTSE 100 Historical Data.csv")

inv = pd.read_csv(INV)
print(f"investing.com rows: {len(inv)}")
print(f"columns: {inv.columns.tolist()}")
inv["Date"] = pd.to_datetime(inv["Date"], format="%m/%d/%Y")
inv["Price"] = inv["Price"].str.replace(",", "").astype(float)
print(f"Date range: {inv['Date'].min()} to {inv['Date'].max()}")

# Filter 2010-2014
inv14 = inv[(inv["Date"] >= "2010-01-01") & (inv["Date"] <= "2014-12-31")].sort_values("Date").reset_index(drop=True)
print(f"\n2010-2014 rows: {len(inv14)}")

# Load yfinance
yf = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
yf["Date"] = pd.to_datetime(yf["Date"])
yf14 = yf[(yf["Date"] >= "2010-01-01") & (yf["Date"] <= "2014-12-31")].sort_values("Date").reset_index(drop=True)
print(f"yfinance 2010-2014 rows: {len(yf14)}")

# Merge on date
mrg = inv14[["Date", "Price"]].rename(columns={"Price": "Price_inv"}).merge(
    yf14[["Date", "Close"]].rename(columns={"Close": "Price_yf"}),
    on="Date", how="inner"
)
print(f"\nMerged (date intersection): {len(mrg)}")

# In Inv only / Yf only
only_inv = set(inv14["Date"]) - set(yf14["Date"])
only_yf = set(yf14["Date"]) - set(inv14["Date"])
print(f"In investing.com only: {len(only_inv)}  ({sorted(only_inv)[:5]}...)")
print(f"In yfinance only: {len(only_yf)}  ({sorted(only_yf)[:5]}...)")

mrg["diff"] = mrg["Price_inv"] - mrg["Price_yf"]
mrg["diff_abs"] = mrg["diff"].abs()
mrg["diff_pct"] = mrg["diff_abs"] / mrg["Price_yf"] * 100
print(f"\nPrice diff (inv - yf):")
print(f"  max abs diff: {mrg['diff_abs'].max():.4f}")
print(f"  mean abs diff: {mrg['diff_abs'].mean():.4f}")
print(f"  max pct diff: {mrg['diff_pct'].max():.4f}%")
print(f"  mean pct diff: {mrg['diff_pct'].mean():.4f}%")
print(f"  identical rows (<0.01 abs diff): {(mrg['diff_abs'] < 0.01).sum()} / {len(mrg)}")
print(f"  diff > 1: {(mrg['diff_abs'] > 1).sum()}")
print(f"  diff > 10: {(mrg['diff_abs'] > 10).sum()}")

if (mrg["diff_abs"] > 1).sum():
    print("\nTop 10 largest diffs:")
    print(mrg.nlargest(10, "diff_abs")[["Date", "Price_inv", "Price_yf", "diff_abs"]].to_string(index=False))

# Monthly vol comparison
def mvol(df, c):
    df = df.copy()
    df["ret"] = df[c].pct_change()
    df = df.dropna(subset=["ret"])
    df["ym"] = df["Date"].dt.year * 100 + df["Date"].dt.month
    g = df.groupby("ym")["ret"].std().reset_index().rename(columns={"ret": "vol"})
    return g

v_inv = mvol(inv14, "Price").rename(columns={"vol": "vol_inv"})
v_yf = mvol(yf14, "Close").rename(columns={"vol": "vol_yf"})
v_mrg = v_inv.merge(v_yf, on="ym")
print(f"\n--- Monthly vol comparison ---")
print(f"  N months: {len(v_mrg)}")
print(f"  correlation: {v_mrg[['vol_inv','vol_yf']].corr().iloc[0,1]:.6f}")
print(f"  max abs diff: {(v_mrg['vol_inv']-v_mrg['vol_yf']).abs().max():.6f}")
print(f"  mean vol (inv): {v_mrg['vol_inv'].mean():.6f}")
print(f"  mean vol (yf): {v_mrg['vol_yf'].mean():.6f}")
