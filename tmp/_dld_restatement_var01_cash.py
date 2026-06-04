"""Chen et al. (2017) — Variable-by-variable formula verification.

Paper sample: GAO restatements 1997-2006, event window [-3,-1] ∪ [+1,+3], year 0 excluded.
Paper Table 1 Panel B: matched samples, event-time, Mean + Median only (no SD/p25/p75).
Our stats: full Compustat universe, calendar-time. NOT comparable — formula check only.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FUNDA = ROOT / "inputs" / "Compustat_Annual" / "compustat_annual.csv"

VARS_NEEDED = [
    "gvkey", "fyear", "datadate", "sic",
    "che", "at",            # CASH
    "prcc_f", "csho", "ceq",  # Q
    "oancf",                # CF
    "act", "lct", "dlc",    # NWC
    "dltt",                 # LEV
]
df = pd.read_csv(FUNDA, usecols=VARS_NEEDED)
df = df.dropna(subset=["at"])
df = df[df["at"] > 0]

# SIC exclusions (paper: 6000-6999 financial, 4900-4999 utility)
sic_code = df["sic"].astype(float)
df = df[~sic_code.between(6000, 6999)]
df = df[~sic_code.between(4900, 4999)]

# Quality screen (paper: cash <= AT)
df = df[df["che"].fillna(0) <= df["at"]]

# No winsorization — paper uses hard-drop filters instead

# ── Variable 01: CASH = CHE / AT ──
df["CASH"] = df["che"] / df["at"]

# ── Variable 02: Q = [AT + (PRCC_F × CSHO) − CEQ] / AT ──
df["Q"] = (df["at"] + df["prcc_f"] * df["csho"] - df["ceq"]) / df["at"]

# ── Variable 03: SIZE = ln(AT) ──
df["SIZE"] = np.log(df["at"])

# ── Variable 04: CF = OANCF / AT ──
df["CF"] = df["oancf"] / df["at"]

# ── Variable 05: NWC = [(ACT - CHE) - (LCT - DLC)] / AT ──
df["NWC"] = ((df["act"] - df["che"].fillna(0)) - (df["lct"] - df["dlc"].fillna(0))) / df["at"]

# ── Variable 06: LEV = (DLTT + DLC) / AT ──
df["LEV"] = (df["dltt"] + df["dlc"].fillna(0)) / df["at"]

# ── Variable 07: SIGMA = industry-median[std(CF, prior 10 years)] ──
# Self-join: for each firm-year, find CF values in [t-10, t-1]
cf_cols = df[["gvkey", "fyear", "CF"]].dropna(subset=["CF"])
merged = cf_cols.merge(cf_cols, on="gvkey", suffixes=("", "_hist"))
in_window = (merged["fyear_hist"] < merged["fyear"]) & (merged["fyear_hist"] >= merged["fyear"] - 10)
hist = merged[in_window]
firm_cf_sd = hist.groupby(["gvkey", "fyear"])["CF_hist"].agg(["std", "count"])
firm_cf_sd = firm_cf_sd[firm_cf_sd["count"] >= 3].reset_index()
firm_cf_sd = firm_cf_sd.rename(columns={"std": "cf_sd"})
df = df.merge(firm_cf_sd[["gvkey", "fyear", "cf_sd"]], on=["gvkey", "fyear"], how="left")

# Industry-median: 2-digit SIC (baseline FE uses SIC)
df["sic2"] = df["sic"].fillna(0).astype(int) // 100
df["SIGMA"] = df.groupby(["sic2", "fyear"])["cf_sd"].transform("median")

# ── Variable 08: NSEG = count of business/operating segments with nonzero assets, missing→1 ──
# stype IN ('BUSSEG','OPSEG') — pre/post SFAS 131 (effective 1998) transition
# srcdate = datadate — use as-originally-reported only (not comparative from later 10-Ks)
SEG_CSV = ROOT / "inputs" / "CompustatHistoricalSegments" / "eceabmcmldcdggbz.csv.zip"
seg = pd.read_csv(SEG_CSV, usecols=["gvkey", "datadate", "srcdate", "stype", "sid", "ias"])
seg = seg[seg["stype"].isin(["BUSSEG", "OPSEG"])]
seg = seg[seg["ias"] > 0]
seg["srcdate_dt"] = pd.to_datetime(seg["srcdate"], errors="coerce")
seg["datadate_dt"] = pd.to_datetime(seg["datadate"], errors="coerce")
seg = seg[seg["srcdate_dt"] == seg["datadate_dt"]]  # as-originally-reported only
seg["gvkey"] = pd.to_numeric(seg["gvkey"], errors="coerce")
seg = seg.drop_duplicates(subset=["gvkey", "datadate", "stype", "sid"])
seg["fyear"] = seg["datadate_dt"].dt.year
seg_nseg = seg.groupby(["gvkey", "fyear"])["sid"].nunique().reset_index()
seg_nseg.columns = ["seg_gvkey", "fyear", "NSEG"]
df = df.merge(seg_nseg, left_on=["gvkey", "fyear"], right_on=["seg_gvkey", "fyear"], how="left")
df["NSEG"] = df["NSEG"].fillna(1).astype(int)
df = df.drop(columns=["seg_gvkey"], errors="ignore")

# ── Variable 09: AGE = ln(years since first appearance in Compustat) ──
first_year = df.groupby("gvkey")["fyear"].min().rename("first_fyear")
df = df.merge(first_year, on="gvkey", how="left")
df["AGE"] = np.log(np.maximum(df["fyear"] - df["first_fyear"], 1))

df_sample = df[df["fyear"].between(1994, 2009)]

print(f"Firm-years (1994-2009, no fin/util): {len(df_sample):,}  firms: {df_sample['gvkey'].nunique():,}")
print()

for var, name, paper_error, paper_irreg in [
    ("CASH", "CASH = CHE/AT",              (0.165, 0.094), (0.166, 0.088)),
    ("Q",    "Q = [AT+PRCC_F*CSHO-CEQ]/AT", (1.883, 1.495), (1.969, 1.512)),
    ("SIZE", "SIZE = ln(AT)",               (5.951, 5.851), (6.390, 6.399)),
    ("CF",   "CF = OANCF/AT",              (0.069, 0.084), (0.068, 0.076)),
    ("NWC",  "NWC = [(ACT-CHE)-(LCT-DLC)]/AT", (0.113, 0.089), (0.112, 0.103)),
    ("LEV",  "LEV = (DLTT+DLC)/AT",          (0.219, 0.171), (0.220, 0.192)),
    ("SIGMA","SIGMA = ind-med[std(CF,10y)]", (0.067, 0.068), (0.071, 0.071)),
    ("NSEG", "NSEG = count BUS segs, miss->1", (4.898, 3.000), (5.110, 3.000)),
    ("AGE",  "AGE = ln(yrs since 1st Comp)",    (2.638, 2.565), (2.658, 2.565)),
]:
    s = df_sample[var].dropna()
    p_e, p_i = paper_error, paper_irreg
    print(f"{var:5s}: mean={s.mean():.3f} med={s.median():.3f} SD={s.std():.3f} N={len(s):,}")
    print(f"       Paper error: mean={p_e[0]:.3f} med={p_e[1]:.3f}  irreg: mean={p_i[0]:.3f} med={p_i[1]:.3f}")
    print(f"       Formula: {name}  [OK]" if len(s) > 0 else "  MISSING")
    print()
