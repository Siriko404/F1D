"""Test β^UK with yfinance ^GSPC instead of CRSP sprtrn."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

START = pd.Timestamp("2010-01-01")
END = pd.Timestamp("2014-12-31")

print("Downloading ^GSPC from yfinance...")
sp_yf = yf.download("^GSPC", start="2009-12-15", end="2015-01-31", progress=False, auto_adjust=False)
if isinstance(sp_yf.columns, pd.MultiIndex):
    sp_yf.columns = sp_yf.columns.get_level_values(0)
sp_yf = sp_yf.reset_index()
sp_yf["Date"] = pd.to_datetime(sp_yf["Date"])
sp_yf = sp_yf.sort_values("Date")
sp_yf["ret"] = sp_yf["Close"].pct_change()
sp_yf = sp_yf[(sp_yf["Date"] >= START) & (sp_yf["Date"] <= END)].dropna(subset=["ret"])

print(f"^GSPC: {len(sp_yf)} days  range {sp_yf['Date'].min()} to {sp_yf['Date'].max()}")

# Compare with CRSP sprtrn
crsp_frames = []
for year in range(2010, 2015):
    for q in (1, 2, 3, 4):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["date", "sprtrn"])
            crsp_frames.append(df)
crsp_sp = pd.concat(crsp_frames, ignore_index=True)
crsp_sp["date"] = pd.to_datetime(crsp_sp["date"])
crsp_sp = crsp_sp.dropna(subset=["sprtrn"]).drop_duplicates(subset=["date"]).sort_values("date")
print(f"CRSP sprtrn: {len(crsp_sp)} days")

mrg = sp_yf[["Date", "ret"]].rename(columns={"Date": "date", "ret": "ret_yf"}).merge(
    crsp_sp.rename(columns={"sprtrn": "ret_crsp"}), on="date"
)
print(f"\nMerged days: {len(mrg)}")
mrg["diff"] = (mrg["ret_yf"] - mrg["ret_crsp"]).abs()
print(f"Daily return diff: max={mrg['diff'].max():.6f}  mean={mrg['diff'].mean():.6f}  median={mrg['diff'].median():.6f}")
print(f"Correlation: {mrg[['ret_yf','ret_crsp']].corr().iloc[0,1]:.6f}")

# Monthly vol from each
def monthly_vol(df, ret_col, date_col):
    df = df.copy()
    df["ym"] = pd.to_datetime(df[date_col]).dt.year * 100 + pd.to_datetime(df[date_col]).dt.month
    g = df.groupby("ym")[ret_col].std().reset_index()
    g.columns = ["ym", "vol"]
    return g

vol_yf = monthly_vol(sp_yf, "ret", "Date").rename(columns={"vol": "vol_yf"})
vol_crsp = monthly_vol(crsp_sp, "sprtrn", "date").rename(columns={"vol": "vol_crsp"})
vol_mrg = vol_yf.merge(vol_crsp, on="ym")
vol_mrg["diff"] = (vol_mrg["vol_yf"] - vol_mrg["vol_crsp"]).abs()
print(f"\nMonthly vol: max diff={vol_mrg['diff'].max():.6f}  mean={vol_mrg['diff'].mean():.6f}")
print(f"vol_yf mean={vol_mrg['vol_yf'].mean():.6f}  vol_crsp mean={vol_mrg['vol_crsp'].mean():.6f}")
print(f"Correlation: {vol_mrg[['vol_yf','vol_crsp']].corr().iloc[0,1]:.6f}")
