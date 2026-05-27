"""Download fresh FTSE100 via yfinance + compare with existing file."""
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OLD = ROOT / "inputs/Brexit_replication/Yahoo_FTSE100/FTSE100_yfinance_daily.csv"

import yfinance as yf
new_df = yf.download("^FTSE", start="2009-12-01", end="2015-01-31", progress=False, auto_adjust=False)
print(f"yfinance new download: {len(new_df)} rows")
if isinstance(new_df.columns, pd.MultiIndex):
    new_df.columns = new_df.columns.get_level_values(0)
new_df = new_df.reset_index()
new_df["Date"] = pd.to_datetime(new_df["Date"]).dt.date
print(new_df.head(3))
print(f"\nNew Close range: {new_df['Close'].min():.1f} to {new_df['Close'].max():.1f}")

# Save
out_path = ROOT / "inputs/Brexit_replication/Yahoo_FTSE100/FTSE100_yfinance_REFRESH.csv"
new_df.to_csv(out_path, index=False)
print(f"Saved fresh to: {out_path}")

# Compare with existing
old = pd.read_csv(OLD)
old["Date"] = pd.to_datetime(old["Date"]).dt.date
old = old.sort_values("Date").reset_index(drop=True)
print(f"\nOld file: {len(old)} rows | range {old['Date'].min()} to {old['Date'].max()}")
print(f"New file: {len(new_df)} rows | range {new_df['Date'].min()} to {new_df['Date'].max()}")

# Align on date
mrg = old[["Date", "Close"]].rename(columns={"Close": "Close_old"}).merge(
    new_df[["Date", "Close"]].rename(columns={"Close": "Close_new"}),
    on="Date", how="inner"
)
print(f"\nMerged rows (date intersection): {len(mrg)}")

# Restrict to 2010-2014 (β estimation window)
mrg["Date"] = pd.to_datetime(mrg["Date"])
mrg14 = mrg[(mrg["Date"] >= "2010-01-01") & (mrg["Date"] <= "2014-12-31")]
print(f"2010-2014 intersection: {len(mrg14)} days")

if len(mrg14):
    mrg14["diff_abs"] = (mrg14["Close_old"] - mrg14["Close_new"]).abs()
    mrg14["diff_pct"] = mrg14["diff_abs"] / mrg14["Close_old"] * 100
    print(f"\nClose Old vs New (2010-2014):")
    print(f"  max abs diff: {mrg14['diff_abs'].max():.4f}")
    print(f"  mean abs diff: {mrg14['diff_abs'].mean():.4f}")
    print(f"  max pct diff: {mrg14['diff_pct'].max():.6f}%")
    print(f"  identical rows: {(mrg14['diff_abs'] < 0.01).sum()} / {len(mrg14)}")
    n_diff = (mrg14["diff_abs"] > 0.5).sum()
    print(f"  rows with diff > 0.5: {n_diff}")
    if n_diff:
        print("\n  Top 5 largest diffs:")
        top = mrg14.nlargest(5, "diff_abs")[["Date", "Close_old", "Close_new", "diff_abs"]]
        print(top.to_string(index=False))

# Monthly vol from each
def monthly_vol(df, close_col):
    d = df.sort_values("Date").copy()
    d["Date"] = pd.to_datetime(d["Date"])
    d["ret"] = d[close_col].pct_change()
    d = d.dropna(subset=["ret"])
    d["ym"] = d["Date"].dt.year * 100 + d["Date"].dt.month
    g = d.groupby("ym")["ret"].std().reset_index()
    g.columns = ["ym", "vol"]
    return g

# Restrict source data to 2010-2014 before computing vol
old14 = old[(pd.to_datetime(old["Date"]) >= "2010-01-01") & (pd.to_datetime(old["Date"]) <= "2014-12-31")].copy()
new14 = new_df[(pd.to_datetime(new_df["Date"]) >= "2010-01-01") & (pd.to_datetime(new_df["Date"]) <= "2014-12-31")].copy()

vol_old = monthly_vol(old14, "Close")
vol_new = monthly_vol(new14, "Close")
vol_mrg = vol_old.merge(vol_new, on="ym", suffixes=("_old", "_new"))
vol_mrg["diff"] = (vol_mrg["vol_old"] - vol_mrg["vol_new"]).abs()
print(f"\n--- Monthly vol comparison (2010M1-2014M12) ---")
print(f"  N months: {len(vol_mrg)}")
print(f"  Correlation: {vol_mrg[['vol_old','vol_new']].corr().iloc[0,1]:.6f}")
print(f"  Max abs diff: {vol_mrg['diff'].max():.6f}")
print(f"  Mean abs diff: {vol_mrg['diff'].mean():.6f}")
print(f"  Mean vol (old): {vol_mrg['vol_old'].mean():.6f}")
print(f"  Mean vol (new): {vol_mrg['vol_new'].mean():.6f}")
