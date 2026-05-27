"""Verify which Compustat fields are YTD-cumulative vs quarterly."""
import pandas as pd
import numpy as np

ROOT = r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D"
df = pd.read_parquet(f"{ROOT}/inputs/comp_na_daily_all/comp_na_daily_all.parquet",
                      columns=["gvkey", "datadate", "fyearq", "fqtr",
                                "oibdpq", "capxy", "xrdy", "sppey", "saleq", "oancfy"])
df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
df["datadate"] = pd.to_datetime(df["datadate"])
df = df[(df["datadate"] >= "2010-01-01") & (df["datadate"] <= "2014-12-31")]

# Take 5 firms and look at QoQ pattern. YTD = should be monotone within fyear.
# Quarterly = should NOT be monotone.
sample_gv = df["gvkey"].drop_duplicates().head(5).tolist()
print("Field-by-field QoQ pattern (YTD = monotone increasing within fiscal year):\n")
for col in ["oibdpq", "capxy", "xrdy", "sppey", "saleq", "oancfy"]:
    print(f"--- {col} ---")
    for gv in sample_gv[:2]:
        sub = df[(df["gvkey"] == gv) & df["fyearq"].notna()].sort_values("datadate")
        sub = sub[["datadate", "fyearq", "fqtr", col]].head(8)
        print(sub.to_string(index=False))
        print()
