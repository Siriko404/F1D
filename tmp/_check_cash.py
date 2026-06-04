"""Quick CASH stats check against Table 1 Panel A benchmark."""
import pandas as pd
import numpy as np

p = pd.read_parquet("outputs/campello_v2/20260526_202914/sample_panel.parquet")
p = p.sort_values(["gvkey", "datadate"])

# CASH Table 1 def: cheq / atq_lag1
# STEP 46: accounting variables normalized by lagged total assets
p["atq_lag1"] = p.groupby("gvkey")["atq"].shift(1)

# Validate lag is consecutive quarter (~90 days ±45)
p["datadate_lag"] = p.groupby("gvkey")["datadate"].shift(1)
p["gap_days"] = (p["datadate"] - p["datadate_lag"]).dt.days
p.loc[(p["gap_days"] < 45) | (p["gap_days"] > 135), "atq_lag1"] = np.nan

p["CASH_t1"] = np.where(
    p["atq_lag1"].notna() & (p["atq_lag1"] > 0),
    p["cheq"] / p["atq_lag1"],
    np.nan,
)
p["CASH_t1"] = p["CASH_t1"].replace([np.inf, -np.inf], np.nan)

valid = p["CASH_t1"].notna()
print(f"CASH (Table 1 def) non-missing: {valid.sum():,}")
print(f"Mean: {p.loc[valid, 'CASH_t1'].mean():.4f}")
print(f"SD: {p.loc[valid, 'CASH_t1'].std():.4f}")
print(f"Median: {p.loc[valid, 'CASH_t1'].median():.4f}")

# Benchmark: Panel A mean=0.22, SD=0.25, median=0.12, N=78,044
print("\nBenchmark Panel A: mean=0.22, SD=0.25, median=0.12, N=78,044")

# Also check CASH Table 8 def: cheq / (atq_lag1 - cheq_lag1)
p["cheq_lag1"] = p.groupby("gvkey")["cheq"].shift(1)
p.loc[(p["gap_days"] < 45) | (p["gap_days"] > 135), "cheq_lag1"] = np.nan
denom_t8 = p["atq_lag1"] - p["cheq_lag1"]
p["CASH_t8"] = np.where(
    denom_t8.notna() & (denom_t8 > 0),
    p["cheq"] / denom_t8,
    np.nan,
)
p["CASH_t8"] = p["CASH_t8"].replace([np.inf, -np.inf], np.nan)

valid8 = p["CASH_t8"].notna()
print(f"\nCASH (Table 8 def) non-missing: {valid8.sum():,}")
print(f"Mean: {p.loc[valid8, 'CASH_t8'].mean():.4f}")
print(f"SD: {p.loc[valid8, 'CASH_t8'].std():.4f}")
print(f"Median: {p.loc[valid8, 'CASH_t8'].median():.4f}")
print(f"N gap vs benchmark: {valid.sum() - 78044:,}")
