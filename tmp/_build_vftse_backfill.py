"""Build full-window VFTSE_proxy via calibration.

Recipe:
- Aug 2012-Dec 2015: use investing.com VFTSE actual
- Pre Aug 2012: use park_5d-calibrated proxy (formula 8.91 + 0.518 * park_5d)
- Save daily + monthly aggregates."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
INV = Path(r"C:\Users\sinas\Downloads\FTSE 100 VIX Historical Data 1.csv")

# 1. Load investing.com VFTSE actual
inv = pd.read_csv(INV)
inv["Date"] = pd.to_datetime(inv["Date"], format="%m/%d/%Y")
inv["VFTSE"] = inv["Price"].astype(str).str.replace(",", "").astype(float)
inv = inv[["Date", "VFTSE"]].sort_values("Date").reset_index(drop=True)
print(f"VFTSE actual: {len(inv)} rows ({inv['Date'].min().date()} to {inv['Date'].max().date()})")

# 2. Load FTSE OHLC for proxy
ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[["Date", "Open", "High", "Low", "Close"]].sort_values("Date").reset_index(drop=True)
ANN = np.sqrt(252)

# Parkinson 5d
park_inst = (np.log(ftse["High"]/ftse["Low"])**2) / (4*np.log(2))
ftse["park_5d"] = np.sqrt(park_inst.rolling(5, min_periods=3).mean()) * ANN * 100

# 3. Refit calibration on full overlap (use ALL overlap days, not just early sample)
m = inv.merge(ftse, on="Date", how="inner").dropna(subset=["park_5d", "VFTSE"])
X = np.column_stack([np.ones(len(m)), m["park_5d"].values])
y = m["VFTSE"].values
b, *_ = np.linalg.lstsq(X, y, rcond=None)
yp = X @ b
rmse = np.sqrt(((y - yp)**2).mean())
corr = np.corrcoef(y, yp)[0,1]
print(f"\nCalibration: VFTSE = {b[0]:.4f} + {b[1]:.4f} * park_5d")
print(f"  N={len(m)}  corr={corr:.4f}  RMSE={rmse:.3f}")
print(f"  Residual sd={np.std(y-yp):.3f}  mean(actual)={y.mean():.2f}  mean(pred)={yp.mean():.2f}")

# 4. Build proxy for full window
ftse["VFTSE_proxy"] = b[0] + b[1] * ftse["park_5d"]

# 5. Splice: actual where available, proxy otherwise
result = ftse[["Date", "park_5d", "VFTSE_proxy"]].merge(inv, on="Date", how="left")
result["VFTSE_final"] = result["VFTSE"].fillna(result["VFTSE_proxy"])
result["source"] = np.where(result["VFTSE"].notna(), "actual", "proxy")
print(f"\nSplice: {(result['source']=='actual').sum()} actual / {(result['source']=='proxy').sum()} proxy days")

# Window check 2010-2014
START = pd.Timestamp("2010-01-01")
END = pd.Timestamp("2014-12-31")
window = result[(result["Date"] >= START) & (result["Date"] <= END)].copy()
print(f"\n2010-2014 window: {len(window)} days")
print(f"  Actual: {(window['source']=='actual').sum()}  Proxy: {(window['source']=='proxy').sum()}")
print(f"  VFTSE_final mean={window['VFTSE_final'].mean():.2f}  sd={window['VFTSE_final'].std():.2f}  range=[{window['VFTSE_final'].min():.2f}, {window['VFTSE_final'].max():.2f}]")

# 6. Save
out_dir = ROOT / "inputs" / "Brexit_replication" / "VFTSE"
out_dir.mkdir(parents=True, exist_ok=True)
out = window[["Date", "VFTSE_final", "source"]].rename(columns={"VFTSE_final": "VFTSE"})
out.to_csv(out_dir / "VFTSE_backfilled_2010_2014.csv", index=False)
print(f"\nSaved {len(out)} rows -> {out_dir / 'VFTSE_backfilled_2010_2014.csv'}")

# 7. Calibration sanity: how does proxy compare to actual on overlap?
overlap_window = window[window["source"]=="actual"]
print(f"\nOverlap window stats (actual vs predicted):")
print(f"  Actual mean={overlap_window['VFTSE'].mean():.2f}")
print(f"  Proxy on same days mean={overlap_window['VFTSE_proxy'].mean():.2f}")
print(f"  Diff (actual - proxy): mean={(overlap_window['VFTSE'] - overlap_window['VFTSE_proxy']).mean():.3f}  sd={(overlap_window['VFTSE'] - overlap_window['VFTSE_proxy']).std():.3f}")

# Monthly aggregates
window["ym"] = window["Date"].dt.year * 100 + window["Date"].dt.month
vftse_eom = window.groupby("ym").agg(VFTSE_eom=("VFTSE_final", "last"),
                                       VFTSE_mean=("VFTSE_final", "mean"),
                                       VFTSE_std=("VFTSE_final", "std"),
                                       n_days=("Date", "count"),
                                       pct_actual=("source", lambda s: (s=="actual").mean())).reset_index()
print(f"\nMonthly: {len(vftse_eom)} months")
print(vftse_eom.head(8))
print(f"\nMonths fully actual: {(vftse_eom['pct_actual']==1).sum()}")
print(f"Months fully proxy: {(vftse_eom['pct_actual']==0).sum()}")
print(f"Months mixed: {((vftse_eom['pct_actual']>0) & (vftse_eom['pct_actual']<1)).sum()}")
