"""
Compute summary statistics for variables missing from econometric CSVs.

Variables: SurpDec, CurrentRatio, RD_Intensity, StockRet, MarketRet, EPS_Growth
Source: H0.3 ceo_clarity_extended_panel.parquet, filtered to Main sample.

Output: outputs/summary_stats_missing_vars.csv
"""

import pandas as pd
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PANEL = ROOT / "outputs" / "variables" / "ceo_clarity_extended" / "2026-03-13_024110" / "ceo_clarity_extended_panel.parquet"
OUT = ROOT / "outputs" / "summary_stats_missing_vars.csv"

VARS = ["SurpDec", "CurrentRatio", "RD_Intensity", "StockRet", "MarketRet", "EPS_Growth"]

df = pd.read_parquet(PANEL)
df_main = df[df["sample"] == "Main"]

print(f"Main sample rows: {len(df_main):,}")

rows = []
for var in VARS:
    s = df_main[var].dropna()
    rows.append({
        "Variable": var,
        "N": len(s),
        "Mean": round(s.mean(), 4),
        "SD": round(s.std(), 4),
        "Min": round(s.min(), 3),
        "P25": round(s.quantile(0.25), 3),
        "Median": round(s.quantile(0.50), 3),
        "P75": round(s.quantile(0.75), 3),
        "Max": round(s.max(), 3),
    })

result = pd.DataFrame(rows)
result.to_csv(OUT, index=False)
print(result.to_string(index=False))
print(f"\nSaved to {OUT}")
