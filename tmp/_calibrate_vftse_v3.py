"""Drill into 5d-window family + multi-asset HAR + add lagged VFTSE persistence.
Realized vol = backward; implied = forward. Test if 5d window catches the regime."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\Data_Processing\F1D")
ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
INV = Path(r"C:\Users\sinas\Downloads\FTSE 100 VIX Historical Data 1.csv")

inv = pd.read_csv(INV)
inv["Date"] = pd.to_datetime(inv["Date"], format="%m/%d/%Y")
inv["VFTSE"] = inv["Price"].astype(str).str.replace(",", "").astype(float)
inv = inv[["Date", "VFTSE"]].sort_values("Date").reset_index(drop=True)

ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[["Date", "Open", "High", "Low", "Close"]].sort_values("Date").reset_index(drop=True)
ftse = ftse.dropna(subset=["Close"])
ftse["log_ret"] = np.log(ftse["Close"] / ftse["Close"].shift(1))
ANN = np.sqrt(252)

# Various short windows
for w in [3, 5, 7, 10, 14, 20]:
    ftse[f"std_{w}d"] = ftse["log_ret"].rolling(w, min_periods=max(2,w//2)).std() * ANN * 100
    park_inst = (np.log(ftse["High"]/ftse["Low"])**2) / (4*np.log(2))
    ftse[f"park_{w}d"] = np.sqrt(park_inst.rolling(w, min_periods=max(2,w//2)).mean()) * ANN * 100

m = inv.merge(ftse, on="Date", how="inner")

print(f"{'Variant':<14}{'corr':>8}{'RMSE':>10}{'best_scale':>20}")
print("-" * 55)
for w in [3, 5, 7, 10, 14, 20]:
    for kind in ["std", "park"]:
        v = f"{kind}_{w}d"
        sub = m.dropna(subset=[v, "VFTSE"])
        if len(sub) < 100:
            continue
        corr = sub[[v, "VFTSE"]].corr().iloc[0,1]
        X = np.column_stack([np.ones(len(sub)), sub[v].values])
        y = sub["VFTSE"].values
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        rmse = np.sqrt(((y - X@b)**2).mean())
        print(f"{v:<14}{corr:>8.4f}{rmse:>10.3f}{f'{b[0]:.2f}+{b[1]:.3f}*x':>20}")

# HAR-RV with optimal short window + adding VFTSE persistence (AR(1) on lagged VFTSE)
print("\n=== HAR-RV with optimal short window combos ===")
m_full = m.dropna(subset=["park_5d", "park_22d", "VFTSE"]).copy()
m_full = m_full.sort_values("Date").reset_index(drop=True)
m_full["VFTSE_lag"] = m_full["VFTSE"].shift(1)
m_full = m_full.dropna(subset=["VFTSE_lag"])

# Pure HAR (no VFTSE lag)
for combo in [["park_5d", "park_22d"],
              ["park_3d", "park_22d"],
              ["park_5d", "park_10d", "park_22d"],
              ["std_5d", "std_22d"],
              ["std_5d", "park_22d"]]:
    sub = m.dropna(subset=combo + ["VFTSE"])
    X = np.column_stack([np.ones(len(sub))] + [sub[c].values for c in combo])
    y = sub["VFTSE"].values
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    yp = X @ b
    rmse = np.sqrt(((y - yp)**2).mean())
    corr = np.corrcoef(y, yp)[0,1]
    coefs = " ".join(f"b{i}={b[i+1]:.3f}" for i in range(len(combo)))
    print(f"  HAR({'+'.join(combo)}): a={b[0]:.2f} {coefs}  corr={corr:.4f} rmse={rmse:.3f}")
