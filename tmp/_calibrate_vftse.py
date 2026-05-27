"""Calibrate VFTSE formula: try multiple realized-vol constructions from
FTSE OHLC and pick the one closest to investing.com VFTSE values.

Investing.com VFTSE 854 obs span 2012-08-28 to 2015-12-31 (irregular gaps —
need to check)."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
INV = Path(r"C:\Users\sinas\Downloads\FTSE 100 VIX Historical Data 1.csv")

# Load investing.com VFTSE
inv = pd.read_csv(INV)
inv["Date"] = pd.to_datetime(inv["Date"], format="%m/%d/%Y")
inv["VFTSE"] = inv["Price"].astype(str).str.replace(",", "").astype(float)
inv = inv[["Date", "VFTSE"]].sort_values("Date").reset_index(drop=True)
print(f"investing.com VFTSE: {len(inv)} rows, range {inv['Date'].min()} to {inv['Date'].max()}")
print(f"  Mean={inv['VFTSE'].mean():.2f}  SD={inv['VFTSE'].std():.2f}  range=[{inv['VFTSE'].min():.2f}, {inv['VFTSE'].max():.2f}]")

# Load FTSE 100 OHLC
ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[["Date", "Open", "High", "Low", "Close"]].sort_values("Date").reset_index(drop=True)
ftse = ftse.dropna(subset=["Close"])
ftse["log_ret"] = np.log(ftse["Close"] / ftse["Close"].shift(1))
print(f"\nFTSE OHLC: {len(ftse)} rows, range {ftse['Date'].min()} to {ftse['Date'].max()}")

# Annualization factor (sqrt of 252 trading days)
ANN = np.sqrt(252)

# Variant 1: 30-day rolling std of daily log returns, annualized as %
ftse["v1_30d_std"] = ftse["log_ret"].rolling(30, min_periods=20).std() * ANN * 100

# Variant 2: 22-day rolling std (≈1 trading month)
ftse["v2_22d_std"] = ftse["log_ret"].rolling(22, min_periods=15).std() * ANN * 100

# Variant 3: 21-day rolling std
ftse["v3_21d_std"] = ftse["log_ret"].rolling(21, min_periods=15).std() * ANN * 100

# Variant 4: 60-day rolling std
ftse["v4_60d_std"] = ftse["log_ret"].rolling(60, min_periods=40).std() * ANN * 100

# Variant 5: 90-day rolling std
ftse["v5_90d_std"] = ftse["log_ret"].rolling(90, min_periods=60).std() * ANN * 100

# Variant 6: Parkinson (HL-based) 30-day annualized
ftse["log_hl"] = np.log(ftse["High"] / ftse["Low"])
ftse["park_inst"] = ftse["log_hl"] ** 2 / (4 * np.log(2))
ftse["v6_park_30d"] = np.sqrt(ftse["park_inst"].rolling(30, min_periods=20).mean()) * ANN * 100
ftse["v7_park_22d"] = np.sqrt(ftse["park_inst"].rolling(22, min_periods=15).mean()) * ANN * 100

# Variant 8: Garman-Klass (OHLC) 30-day
ftse["gk_inst"] = (0.5 * (np.log(ftse["High"] / ftse["Low"]) ** 2) -
                    (2 * np.log(2) - 1) * (np.log(ftse["Close"] / ftse["Open"]) ** 2))
ftse["v8_gk_30d"] = np.sqrt(ftse["gk_inst"].rolling(30, min_periods=20).mean()) * ANN * 100

# Variant 9: simple return std (not log) 30-day
ftse["simp_ret"] = ftse["Close"] / ftse["Close"].shift(1) - 1
ftse["v9_simp_30d"] = ftse["simp_ret"].rolling(30, min_periods=20).std() * ANN * 100

# Variant 10: monthly std on calendar month
ftse["ym"] = ftse["Date"].dt.year * 100 + ftse["Date"].dt.month
monthly_std = ftse.groupby("ym")["log_ret"].std().reset_index().rename(columns={"log_ret": "monthly_std"})
monthly_std["monthly_std"] = monthly_std["monthly_std"] * ANN * 100
ftse = ftse.merge(monthly_std, on="ym", how="left")

# Compare each variant against investing.com VFTSE
m = inv.merge(ftse, on="Date", how="inner")
print(f"\nMerged with FTSE OHLC: {len(m)} rows (overlap with FTSE data)")

variants = ["v1_30d_std", "v2_22d_std", "v3_21d_std", "v4_60d_std", "v5_90d_std",
            "v6_park_30d", "v7_park_22d", "v8_gk_30d", "v9_simp_30d", "monthly_std"]

print(f"\n{'Variant':<20}{'corr(VFTSE)':>14}{'RMSE':>10}{'mean_diff':>12}{'best_scale':>12}")
print("-" * 70)
results = {}
for v in variants:
    sub = m.dropna(subset=[v, "VFTSE"])
    if len(sub) < 100:
        continue
    corr = sub[[v, "VFTSE"]].corr().iloc[0,1]
    # Find best scaling: VFTSE = a + b * variant. Fit OLS.
    X = np.column_stack([np.ones(len(sub)), sub[v].values])
    y = sub["VFTSE"].values
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    yp = X @ b
    rmse = np.sqrt(((y - yp) ** 2).mean())
    mean_diff = (sub["VFTSE"].mean() - sub[v].mean())
    results[v] = (corr, rmse, mean_diff, b[0], b[1])
    print(f"{v:<20}{corr:>14.4f}{rmse:>10.3f}{mean_diff:>12.3f}{f'{b[0]:.2f}+{b[1]:.3f}*x':>16}")

# Best by correlation
best = max(results.items(), key=lambda x: x[1][0])
print(f"\nBest correlation: {best[0]}  corr={best[1][0]:.4f}")
print(f"  VFTSE ≈ {best[1][3]:.3f} + {best[1][4]:.3f} × {best[0]}")

# Best by RMSE
best_rmse = min(results.items(), key=lambda x: x[1][1])
print(f"\nBest RMSE: {best_rmse[0]}  rmse={best_rmse[1][1]:.3f}")

# Show distribution comparison side-by-side
print(f"\nDistribution comparison (overlap days):")
print(f"  VFTSE: mean={m['VFTSE'].mean():.2f}  sd={m['VFTSE'].std():.2f}  min={m['VFTSE'].min():.2f}  max={m['VFTSE'].max():.2f}")
for v in ["v1_30d_std", "v2_22d_std", "v6_park_30d", "v8_gk_30d"]:
    sub = m.dropna(subset=[v])
    print(f"  {v:<14}: mean={sub[v].mean():.2f}  sd={sub[v].std():.2f}  min={sub[v].min():.2f}  max={sub[v].max():.2f}")
