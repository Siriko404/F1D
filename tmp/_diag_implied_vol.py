"""Download VIX + VFTSE (if available) and rebuild β^UK with implied vols."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")

START = "2009-12-01"
END = "2015-02-01"

# VIX (CBOE S&P 500 implied vol)
print("Downloading VIX (^VIX)...")
vix = yf.download("^VIX", start=START, end=END, progress=False, auto_adjust=False)
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.get_level_values(0)
vix = vix.reset_index()
print(f"VIX: {len(vix)} rows; range {vix['Date'].min()} - {vix['Date'].max()}")
print(vix.head(3))

# VFTSE (FTSE 100 Volatility Index) — yfinance ticker often ^VFTSE
print("\nDownloading VFTSE (^VFTSE)...")
vftse = yf.download("^VFTSE", start=START, end=END, progress=False, auto_adjust=False)
if isinstance(vftse.columns, pd.MultiIndex):
    vftse.columns = vftse.columns.get_level_values(0)
vftse = vftse.reset_index()
print(f"VFTSE: {len(vftse)} rows")
if len(vftse):
    print(vftse.head(3))
else:
    print("VFTSE not available via yfinance — try alt sources")

# Bloomberg Index of Currency Volatility? — try GBPUSDV1M (1-month implied)
# Probably not free. Try realized vol for FX as fallback.
