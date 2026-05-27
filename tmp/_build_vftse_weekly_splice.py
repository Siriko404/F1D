"""Splice VFTSE: actual daily where we have it (Aug 2012+),
weekly forward-filled to daily where we only have weekly (2009-Aug 2012)."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
VFTSE_DIR = ROOT / "inputs" / "Brexit_replication" / "VFTSE"

# 1. Load DAILY VFTSE (Aug 2012 - Dec 2015)
daily = pd.read_csv(r"C:\Users\sinas\Downloads\FTSE 100 VIX Historical Data 1.csv")
daily["Date"] = pd.to_datetime(daily["Date"], format="%m/%d/%Y")
daily["VFTSE"] = daily["Price"].astype(str).str.replace(",", "").astype(float)
daily = daily[["Date", "VFTSE"]].sort_values("Date").reset_index(drop=True)
print(f"Daily VFTSE: {len(daily)} rows ({daily['Date'].min().date()} to {daily['Date'].max().date()})")

# 2. Load WEEKLY VFTSE (Jul 2009 - Dec 2016)
weekly = pd.read_csv(VFTSE_DIR / "VFTSE_weekly_investing_2009_2016.csv")
weekly["Date"] = pd.to_datetime(weekly["Date"], format="%m/%d/%Y")
weekly["VFTSE_wk"] = weekly["Price"].astype(str).str.replace(",", "").astype(float)
weekly = weekly[["Date", "VFTSE_wk"]].sort_values("Date").reset_index(drop=True)
print(f"Weekly VFTSE: {len(weekly)} rows ({weekly['Date'].min().date()} to {weekly['Date'].max().date()})")
print(f"  Weekday distribution: {weekly['Date'].dt.day_name().value_counts().to_dict()}")

# 3. Check: each weekly row is week-end (Sunday). Treat as latest known VFTSE for that week.
#    Apply forward-fill on trading-day calendar: for each trading day, find most recent weekly row.

# Build trading-day calendar from FTSE OHLC
ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[["Date"]].sort_values("Date").reset_index(drop=True)
ftse = ftse[(ftse["Date"] >= "2009-07-01") & (ftse["Date"] <= "2014-12-31")]
print(f"\nTrading days 2009-07 to 2014-12: {len(ftse)}")

# 4. For each trading day, find weekly VFTSE that is closest PRIOR week-end (typical convention)
# weekly Date = Sunday → week-end. Use as-of-merge.
weekly_sorted = weekly.sort_values("Date")
ftse_sorted = ftse.sort_values("Date")
merged_wk = pd.merge_asof(ftse_sorted, weekly_sorted, on="Date", direction="backward",
                          tolerance=pd.Timedelta("8D"))
print(f"After merge_asof with weekly: {merged_wk['VFTSE_wk'].notna().sum()}/{len(merged_wk)} days have weekly value")

# 5. Splice: daily actual where available, weekly otherwise
final = merged_wk.merge(daily, on="Date", how="left")
final["VFTSE_final"] = final["VFTSE"].fillna(final["VFTSE_wk"])
final["source"] = np.where(final["VFTSE"].notna(), "daily",
                  np.where(final["VFTSE_wk"].notna(), "weekly", "missing"))

# Window: 2010-2014 for downstream
window = final[(final["Date"] >= "2010-01-01") & (final["Date"] <= "2014-12-31")].copy()
print(f"\n2010-2014 window: {len(window)} trading days")
print(f"  Daily source: {(window['source']=='daily').sum()}")
print(f"  Weekly source: {(window['source']=='weekly').sum()}")
print(f"  Missing: {(window['source']=='missing').sum()}")

# Stats
print(f"\nVFTSE_final 2010-2014:")
print(f"  Mean={window['VFTSE_final'].mean():.2f}  SD={window['VFTSE_final'].std():.2f}")
print(f"  Range=[{window['VFTSE_final'].min():.2f}, {window['VFTSE_final'].max():.2f}]")

# Verify continuity: avg jump at splice boundaries
print(f"\nDaily-only window stats:")
d_only = window[window["source"]=="daily"]
print(f"  Mean={d_only['VFTSE_final'].mean():.2f}  SD={d_only['VFTSE_final'].std():.2f}")
print(f"Weekly-only window stats:")
w_only = window[window["source"]=="weekly"]
print(f"  Mean={w_only['VFTSE_final'].mean():.2f}  SD={w_only['VFTSE_final'].std():.2f}")

# 6. Save
out = window[["Date", "VFTSE_final", "source"]].rename(columns={"VFTSE_final": "VFTSE"})
out.to_csv(VFTSE_DIR / "VFTSE_weeklyspliced_2010_2014.csv", index=False)
print(f"\nSaved -> {VFTSE_DIR / 'VFTSE_weeklyspliced_2010_2014.csv'}")

# Show first ~30 days to verify boundary
print("\nFirst 15 trading days:")
print(window.head(15)[["Date", "VFTSE", "VFTSE_wk", "VFTSE_final", "source"]].to_string(index=False))
print("\nSplice boundary (last weekly, first daily):")
splice_idx = window.index[window["source"]=="daily"].min()
if not pd.isna(splice_idx):
    print(window.loc[splice_idx-3:splice_idx+3, ["Date", "VFTSE", "VFTSE_wk", "VFTSE_final", "source"]].to_string(index=False))
