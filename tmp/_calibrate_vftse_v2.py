"""Push VFTSE proxy harder: EWMA (RiskMetrics), HAR-RV, hybrid blends.
Goal: beat v7_park_22d corr=0.6161, RMSE=1.926."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

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

# === EWMA (RiskMetrics) - lambda=0.94 standard ===
def ewma_var(r, lam):
    v = np.zeros(len(r))
    r_sq = r.fillna(0).values ** 2
    v[0] = r_sq[0]
    for i in range(1, len(r)):
        v[i] = lam * v[i-1] + (1 - lam) * r_sq[i]
    return v

ftse["ewma94"] = np.sqrt(ewma_var(ftse["log_ret"], 0.94)) * ANN * 100
ftse["ewma97"] = np.sqrt(ewma_var(ftse["log_ret"], 0.97)) * ANN * 100
ftse["ewma90"] = np.sqrt(ewma_var(ftse["log_ret"], 0.90)) * ANN * 100
ftse["ewma85"] = np.sqrt(ewma_var(ftse["log_ret"], 0.85)) * ANN * 100

# === HAR-RV components (1d, 5d, 22d realized) ===
ftse["log_hl_sq"] = np.log(ftse["High"] / ftse["Low"]) ** 2 / (4 * np.log(2))
ftse["rv_1d"] = np.sqrt(ftse["log_hl_sq"]) * ANN * 100
ftse["rv_5d"] = np.sqrt(ftse["log_hl_sq"].rolling(5, min_periods=3).mean()) * ANN * 100
ftse["rv_22d"] = np.sqrt(ftse["log_hl_sq"].rolling(22, min_periods=15).mean()) * ANN * 100
ftse["rv_60d"] = np.sqrt(ftse["log_hl_sq"].rolling(60, min_periods=30).mean()) * ANN * 100

# === Hybrid Parkinson + close-to-close ===
ftse["std_22d"] = ftse["log_ret"].rolling(22, min_periods=15).std() * ANN * 100
ftse["park_22d"] = np.sqrt((np.log(ftse["High"]/ftse["Low"])**2 / (4*np.log(2))).rolling(22, min_periods=15).mean()) * ANN * 100
ftse["hybrid_avg"] = (ftse["std_22d"] + ftse["park_22d"]) / 2
ftse["hybrid_max"] = ftse[["std_22d", "park_22d"]].max(axis=1)

m = inv.merge(ftse, on="Date", how="inner")
print(f"Merged: {len(m)} obs\n")

candidates = ["ewma94", "ewma97", "ewma90", "ewma85", "rv_5d", "rv_22d", "rv_60d",
              "park_22d", "hybrid_avg", "hybrid_max"]

print(f"{'Variant':<14}{'corr':>8}{'RMSE':>10}{'best_scale':>20}")
print("-" * 55)
results = {}
for v in candidates:
    sub = m.dropna(subset=[v, "VFTSE"])
    if len(sub) < 100:
        continue
    corr = sub[[v, "VFTSE"]].corr().iloc[0,1]
    X = np.column_stack([np.ones(len(sub)), sub[v].values])
    y = sub["VFTSE"].values
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    rmse = np.sqrt(((y - X@b)**2).mean())
    results[v] = (corr, rmse, b[0], b[1])
    print(f"{v:<14}{corr:>8.4f}{rmse:>10.3f}{f'{b[0]:.2f}+{b[1]:.3f}*x':>20}")

# === HAR-RV multi-component regression ===
print("\n=== HAR-RV multi-component (1d + 5d + 22d Parkinson) ===")
sub = m.dropna(subset=["rv_5d", "rv_22d", "VFTSE", "park_22d"])
X = np.column_stack([np.ones(len(sub)), sub["rv_5d"].values, sub["rv_22d"].values])
y = sub["VFTSE"].values
b, *_ = np.linalg.lstsq(X, y, rcond=None)
yp = X @ b
rmse = np.sqrt(((y - yp)**2).mean())
corr = np.corrcoef(y, yp)[0,1]
print(f"  HAR-RV(5d+22d): a={b[0]:.3f} b1={b[1]:.4f} b2={b[2]:.4f}  corr={corr:.4f} rmse={rmse:.3f}")

X = np.column_stack([np.ones(len(sub)), sub["rv_5d"].values, sub["rv_22d"].values, sub["park_22d"].values])
b, *_ = np.linalg.lstsq(X, y, rcond=None)
yp = X @ b
rmse = np.sqrt(((y - yp)**2).mean())
corr = np.corrcoef(y, yp)[0,1]
print(f"  HAR-RV(5d+22d+park22d): a={b[0]:.3f} b1={b[1]:.4f} b2={b[2]:.4f} b3={b[3]:.4f}  corr={corr:.4f} rmse={rmse:.3f}")

# Add log-level transformation (vol clustering -> AR in log)
print("\n=== Log-VFTSE on log-realized ===")
sub = m.dropna(subset=["park_22d", "VFTSE"])
sub = sub[(sub["park_22d"] > 0) & (sub["VFTSE"] > 0)]
X = np.column_stack([np.ones(len(sub)), np.log(sub["park_22d"]).values])
y = np.log(sub["VFTSE"]).values
b, *_ = np.linalg.lstsq(X, y, rcond=None)
yp_log = X @ b
yp = np.exp(yp_log)
rmse = np.sqrt(((sub["VFTSE"].values - yp)**2).mean())
corr_level = np.corrcoef(sub["VFTSE"].values, yp)[0,1]
print(f"  log(VFTSE) = {b[0]:.3f} + {b[1]:.4f}*log(park_22d)  corr_level={corr_level:.4f} rmse={rmse:.3f}")
