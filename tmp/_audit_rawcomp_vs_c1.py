"""HARDNOSED reconciliation: comp_na_daily_all (2010Q1-2016Q4) vs Campello
Table C.1 row 1 (Raw COMPUSTAT = 262,412) and row 2 (drop non-US,
duplicates excluded = 160,254). Read-only. Tests ONLY standard, defensible
Compustat-canonical screens — reports every screen's count, does NOT tune a
combination to hit the target. If nothing canonical reproduces 262,412 the
honest verdict is 'extract-vintage divergence, irreducible'.
"""
import sys
from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"

C1_ROW1 = 262_412   # Campello "Raw COMPUSTAT between 2010:Q1 and 2016:Q4"
C1_ROW2 = 160_254   # Campello "Drop non-US ... duplicates excluded"

schema = pq.read_schema(RAW)
allcols = list(schema.names)
print("=== SCHEMA: all columns ===")
print(", ".join(allcols))

want = [c for c in ["gvkey", "datadate", "fyearq", "fqtr", "indfmt",
                    "datafmt", "consol", "popsrc", "curcdq", "loc", "fic",
                    "costat", "cusip", "conm", "tic", "sic"] if c in allcols]
df = pq.read_table(RAW, columns=want).to_pandas()
df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
w = df[df["datadate"].between("2010-01-01", "2016-12-31")].copy()
w["cal_q"] = w["datadate"].dt.year * 10 + (w["datadate"].dt.month - 1) // 3 + 1
print(f"\n=== 2010Q1-2016Q4 subset ===")
print(f"rows={len(w):,}  gvkeys={w['gvkey'].nunique():,}  "
      f"target row1={C1_ROW1:,}  delta={len(w)-C1_ROW1:+,}")

print("\n=== datadate MONTH distribution (calendar vs fiscal grain test) ===")
print(w["datadate"].dt.month.value_counts().sort_index().to_string())

for c in ["indfmt", "datafmt", "consol", "popsrc", "curcdq", "costat"]:
    if c in w.columns:
        vc = w[c].value_counts(dropna=False)
        print(f"\n=== {c} value_counts ===\n{vc.head(8).to_string()}")

if "fic" in w.columns and "loc" in w.columns:
    print(f"\n=== loc=='USA' rows: {int((w['loc']=='USA').sum()):,}  "
          f"fic=='USA' rows: {int((w['fic']=='USA').sum()):,}  "
          f"loc==USA & fic==USA: {int(((w['loc']=='USA')&(w['fic']=='USA')).sum()):,} ===")

print("\n=== DUPLICATE GRAIN ===")
print(f"dup (gvkey,datadate): {int(w.duplicated(['gvkey','datadate']).sum()):,}")
print(f"dup (gvkey,cal_q)   : {int(w.duplicated(['gvkey','cal_q']).sum()):,}")
if "cusip" in w.columns:
    w["cusip6"] = w["cusip"].astype(str).str[:6]
    print(f"dup (cusip6,cal_q)  : {int(w.duplicated(['cusip6','cal_q']).sum()):,}"
          f"  (multi-gvkey-per-issuer / share-class proxy)")

print("\n=== CANONICAL SCREEN LADDER (standard WRDS canonical, in order) ===")
cur = w.copy()
def step(label, mask):
    global cur
    cur = cur[mask(cur)]
    print(f"  {label:<46s} -> {len(cur):>9,d}")
print(f"  {'start (2010Q1-2016Q4 raw)':<46s} -> {len(cur):>9,d}   "
      f"[Campello row1 {C1_ROW1:,}]")
if "popsrc" in cur.columns:
    step("popsrc=='D' (domestic)", lambda d: d["popsrc"] == "D")
if "consol" in cur.columns:
    step("consol=='C'", lambda d: d["consol"] == "C")
if "indfmt" in cur.columns:
    step("indfmt=='INDL'", lambda d: d["indfmt"] == "INDL")
if "datafmt" in cur.columns:
    step("datafmt=='STD'", lambda d: d["datafmt"] == "STD")
step("dedup to 1 row per (gvkey,cal_q)",
     lambda d: ~d.duplicated(["gvkey", "cal_q"]))
print(f"  {'^ compare to Campello row1':<46s}    {C1_ROW1:,}")
if "curcdq" in cur.columns:
    step("curcdq=='USD'", lambda d: d["curcdq"] == "USD")
if "loc" in cur.columns:
    step("loc=='USA' (US HQ)", lambda d: d["loc"] == "USA")
if "fic" in cur.columns:
    step("+ fic=='USA' (US incorporated)", lambda d: d["fic"] == "USA")
print(f"  {'^ compare to Campello row2':<46s}    {C1_ROW2:,}")
