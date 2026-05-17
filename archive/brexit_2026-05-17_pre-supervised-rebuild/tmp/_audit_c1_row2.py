"""HARDNOSED row-2 reconciliation: from the row-1-matched USD base, which
STANDARD 'US + duplicates excluded' screen reproduces Campello Table C.1
row 2 = 160,254? Read-only. Tests defensible Compustat screens, reports
EVERY count, does NOT tune to the target. If none reproduces it, the honest
verdict is 'row-2 divergence irreducible from our extract'.
"""
import sys
from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
C1_ROW1, C1_ROW2 = 262_412, 160_254

cols = ["gvkey", "datadate", "curcdq", "loc", "fic", "incorp", "costat",
        "priusa", "prican", "prirow", "cusip", "cik", "tic"]
schema = set(pq.read_schema(RAW).names)
cols = [c for c in cols if c in schema]
df = pq.read_table(RAW, columns=cols).to_pandas()
df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
w = df[df["datadate"].between("2010-01-01", "2016-12-31")].copy()
w["cal_q"] = w["datadate"].dt.year * 10 + (w["datadate"].dt.month - 1) // 3 + 1
w = w[~w.duplicated(["gvkey", "cal_q"])].copy()       # row-1 canonical grain
usd = w[w["curcdq"] == "USD"].copy()
print(f"row-1 base  (USD, 1/gvkey-calq) = {len(usd):,}   "
      f"[Campello row1 {C1_ROW1:,}]  target row2 {C1_ROW2:,}\n")

for c in ["loc", "fic", "incorp", "costat", "priusa", "prican", "prirow"]:
    if c in usd.columns:
        print(f"--- {c} value_counts (USD base) ---")
        print(usd[c].value_counts(dropna=False).head(6).to_string(), "\n")

usd["cusip6"] = usd["cusip"].astype(str).str[:6] if "cusip" in usd else ""

def n(mask):
    return int(mask.sum())

print("=== STANDARD US-SCREEN CANDIDATES (from USD base, vs row2 160,254) ===")
loc_us = usd["loc"] == "USA"
fic_us = usd["fic"] == "USA"
print(f"  loc=='USA'                              {n(loc_us):>9,}")
print(f"  fic=='USA'                              {n(fic_us):>9,}")
print(f"  loc=='USA' & fic=='USA'                 {n(loc_us & fic_us):>9,}")
if "priusa" in usd.columns:
    has_priusa = usd["priusa"].notna() & (usd["priusa"].astype(str) != "")
    print(f"  priusa present (primary US issue)       {n(has_priusa):>9,}")
    print(f"  loc=='USA' & priusa present             {n(loc_us & has_priusa):>9,}")
if "incorp" in usd.columns:
    inc_us = usd["incorp"] == "USA"
    print(f"  loc=='USA' & incorp=='USA'              {n(loc_us & inc_us):>9,}")
# 'duplicates excluded' = one gvkey per issuer(cusip6) per calendar quarter
if "cusip" in usd.columns:
    base = usd[loc_us].copy()
    ded = base[~base.duplicated(["cusip6", "cal_q"])]
    print(f"  loc=='USA' + 1/(cusip6,cal_q)           {len(ded):>9,}")
    base2 = usd[loc_us & fic_us].copy()
    ded2 = base2[~base2.duplicated(["cusip6", "cal_q"])]
    print(f"  loc&fic=='USA' + 1/(cusip6,cal_q)       {len(ded2):>9,}")
if "cik" in usd.columns:
    has_cik = usd["cik"].notna() & (usd["cik"].astype(str).str.strip() != "")
    print(f"  loc=='USA' & has CIK (SEC filer)        {n(loc_us & has_cik):>9,}")
    print(f"  loc&fic=='USA' & has CIK                {n(loc_us & fic_us & has_cik):>9,}")
print(f"\n  TARGET Campello row2                    {C1_ROW2:>9,}")
print("  (report-all; closest DEFENSIBLE screen named in summary, "
      "NOT tuned)")
