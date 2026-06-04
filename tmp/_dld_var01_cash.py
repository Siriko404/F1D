"""Build Cash DV per Boasiako_Keefe_2021 paper-verbatim. ONE variable only.
Recipe: Cash = che / at_lag1, 1997-2015, drop SIC 4900-4999 + 6000-6999,
        drop AT<=0 or missing, US-only (loc=USA), CRSP-linked firms only
        (paper requires merged CRSP/Compustat per Firm Age definition Appendix A1),
        winsorize 1%/99% pooled.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
CSV = ROOT / "inputs" / "Compustat_Annual" / "compustat_annual.csv"

# ANCHOR (Panel A, Table 1, p537)
ANCHOR = {"N": 56646, "mean": 0.2008, "sd": 0.2231, "p25": 0.0285, "p50": 0.1044, "p75": 0.2913}

# Compustat columns needed
COLS = ["gvkey", "datadate", "fyear", "at", "che", "sic", "loc",
       "dlc", "dltt", "ceq", "prcc_f", "csho", "oibdp", "xint", "txt", "dvc",
       "capx", "aqc", "xrd", "act", "lct"]
# Load with dtypes to speed up - use Int64 for gvkey (nullable int)
dtypes = {"gvkey": "Int64", "fyear": "Int64", "sic": str, "loc": str}
num_cols = ["at", "che", "dlc", "dltt", "ceq", "prcc_f", "csho", "oibdp",
            "xint", "txt", "dvc", "capx", "aqc", "xrd", "act", "lct"]
for c in num_cols:
    dtypes[c] = float

print("Loading Compustat...")
df = pd.read_csv(CSV, usecols=COLS, dtype=dtypes, low_memory=False)
# Parse dates
df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
df.dropna(subset=["datadate"], inplace=True)
# Numeric fields
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")
print(f"Raw load: {len(df):,}")

# CRSP/Compustat merged link (required per Firm Age definition)
print("Loading CCM linker...")
ccm = pd.read_parquet(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
                       columns=["gvkey", "LINKTYPE", "LINKPRIM"])
ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"]) & ccm["LINKPRIM"].isin(["P", "C"])]
crsp_gvkeys = set(ccm["gvkey"].dropna().astype(int))
print(f"  CRSP-linked gvkeys: {len(crsp_gvkeys):,}")

# Filter 1997-2015
df = df[(df["fyear"] >= 1997) & (df["fyear"] <= 2015)].copy()
print(f"After year filter (1997-2015): {len(df):,}")

# US only (loc=USA)
df = df[df["loc"] == "USA"].copy()
print(f"After US-only: {len(df):,}")

# CRSP-linked firms only (paper sample is merged CRSP/Compustat)
df = df[df["gvkey"].astype(int).isin(crsp_gvkeys)].copy()
print(f"After CRSP-link filter: {len(df):,}")

# Drop SIC 4900-4999 (utilities) + 6000-6999 (financials)
df["sic_clean"] = df["sic"].str[:4].str.strip()
bad_sic = df["sic_clean"].str.fullmatch(r"49[0-9]{2}|6[0-9]{4}", na=False)
if bad_sic.any():
    df = df[~bad_sic].copy()
del df["sic_clean"]
print(f"After SIC filter (excl 49xx, 6xxx): {len(df):,}")

# Drop missing or non-positive AT
df.dropna(subset=["at"], inplace=True)
df = df[df["at"] > 0].copy()
print(f"After AT>0: {len(df):,}")

# Sort + lag for BoY
df = df.sort_values(["gvkey", "fyear", "datadate"])
df.drop_duplicates(subset=["gvkey", "fyear"], keep="last", inplace=True)
df["at_lag1"] = df.groupby("gvkey")["at"].shift(1)
df.dropna(subset=["at_lag1"], inplace=True)
df = df[df["at_lag1"] > 0].copy()
print(f"After AT_lag1>0: {len(df):,}")

# Cash = che / at_lag1
df["cash"] = df["che"].fillna(0) / df["at_lag1"]
# Handle extreme outliers before winsorize (inf from near-zero denominators)
df["cash"] = df["cash"].replace([np.inf, -np.inf], np.nan)
df.dropna(subset=["cash"], inplace=True)
print(f"After Cash computed: {len(df):,}")

# Winsorize 1%/99% pooled (paper: "at the 1st and 99th percentiles")
lo, hi = df["cash"].quantile(0.01), df["cash"].quantile(0.99)
df["cash_w"] = df["cash"].clip(lo, hi)
print(f"Winsorize: lo={lo:.6f} hi={hi:.6f}")

# --- Variable 2: Firm Size = log(AT) ---
df["firm_size"] = np.log(df["at"])
FS_ANCHOR = {"N": 56646, "mean": 5.6136, "sd": 2.0593, "p25": 4.0819, "p50": 5.5717, "p75": 7.0455}
lo_fs, hi_fs = df["firm_size"].quantile(0.01), df["firm_size"].quantile(0.99)
df["firm_size_w"] = df["firm_size"].clip(lo_fs, hi_fs)

# --- Variable 3: Firm Age = ln(years in merged CRSP/Compustat) ---
# Get CRSP listing start from CCM (first LINKDT per gvkey)
ccm_full = pd.read_parquet(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
                            columns=["gvkey", "LINKDT", "LINKTYPE", "LINKPRIM"])
ccm_full = ccm_full[ccm_full["LINKTYPE"].isin(["LU", "LC"]) & ccm_full["LINKPRIM"].isin(["P", "C"])]
ccm_full["LINKDT"] = pd.to_datetime(ccm_full["LINKDT"], errors="coerce")
ccm_full = ccm_full.dropna(subset=["LINKDT"])
first_listing = ccm_full.groupby("gvkey")["LINKDT"].min().reset_index()
first_listing["first_fyear"] = first_listing["LINKDT"].dt.year
first_listing = first_listing[["gvkey", "first_fyear"]]

df = df.merge(first_listing, on="gvkey", how="left")
# age_years = fyear - first CRSP/Compustat listing year
df["age_years"] = df["fyear"].astype(int) - df["first_fyear"]
# Clip at 1 (avoid log(0) for IPO year)
df["age_years"] = df["age_years"].clip(lower=1)
df["firm_age"] = np.log(df["age_years"].astype(float))
FA_ANCHOR = {"N": 56646, "mean": 7.3003, "sd": 0.8889, "p25": 2.0179, "p50": 5.0435, "p75": 11.0918}
lo_fa, hi_fa = df["firm_age"].quantile(0.01), df["firm_age"].quantile(0.99)
df["firm_age_w"] = df["firm_age"].clip(lo_fa, hi_fa)

# --- Variable 4: Book Leverage = (DLC + DLTT) / AT ---
df["book_leverage"] = (df["dlc"].fillna(0) + df["dltt"].fillna(0)) / df["at"]
BL_ANCHOR = {"N": 56646, "mean": 0.2362, "sd": 0.3177, "p25": 0.0229, "p50": 0.1863, "p75": 0.3528}
lo_bl, hi_bl = df["book_leverage"].quantile(0.01), df["book_leverage"].quantile(0.99)
df["book_leverage_w"] = df["book_leverage"].clip(lo_bl, hi_bl)

# --- Variable 5: Cash Flow = (OIBDP - XINT - TXT - DVC) / AT ---
df["cash_flow"] = (df["oibdp"].fillna(0) - df["xint"].fillna(0) - df["txt"].fillna(0) - df["dvc"].fillna(0)) / df["at"]
CF_ANCHOR = {"N": 56646, "mean": -0.3758, "sd": 4.8386, "p25": -0.0150, "p50": 0.0684, "p75": 0.1210}
lo_cf, hi_cf = df["cash_flow"].quantile(0.01), df["cash_flow"].quantile(0.99)
df["cash_flow_w"] = df["cash_flow"].clip(lo_cf, hi_cf)

# --- Variable 6: CapEx = CAPX / AT_lag1 ---
df["capital_expenditure"] = df["capx"] / df["at_lag1"]
CX_ANCHOR = {"N": 56646, "mean": 0.0657, "sd": 0.1248, "p25": 0.0174, "p50": 0.0364, "p75": 0.0729}
lo_cx, hi_cx = df["capital_expenditure"].quantile(0.01), df["capital_expenditure"].quantile(0.99)
df["capital_expenditure_w"] = df["capital_expenditure"].clip(lo_cx, hi_cx)

# --- Variable 7: Acquisition Expenditure = AQC / AT_lag1, missing→0 ---
df["acquisition_expenditure"] = df["aqc"].fillna(0) / df["at_lag1"]
ACQ_ANCHOR = {"N": 56646, "mean": 0.0451, "sd": 0.1672, "p25": 0, "p50": 0, "p75": 0.0144}
lo_acq, hi_acq = df["acquisition_expenditure"].quantile(0.01), df["acquisition_expenditure"].quantile(0.99)
df["acquisition_expenditure_w"] = df["acquisition_expenditure"].clip(lo_acq, hi_acq)

# --- Variable 8: Dividend Paying Firms(0/1) = 1 if DVC>0; missing→0 ---
df["dividend_paying"] = ((df["dvc"].fillna(0) > 0)).astype(int)
DV_ANCHOR = {"N": 56646, "mean": 0.2767, "p25": 0, "p50": 0, "p75": 1}

# --- Variable 9: Market-to-book = (AT - CEQ + PRCC_F*CSHO) / AT ---
df["market_to_book"] = (df["at"] - df["ceq"] + df["prcc_f"] * df["csho"]) / df["at"]
MTB_ANCHOR = {"N": 56646, "mean": 2.1592, "sd": 2.9919, "p25": 1.1104, "p50": 1.5113, "p75": 2.3119}
lo_mtb, hi_mtb = df["market_to_book"].quantile(0.01), df["market_to_book"].quantile(0.99)
df["market_to_book_w"] = df["market_to_book"].clip(lo_mtb, hi_mtb)

# --- Variable 10: R&D Expenditure = XRD / AT_lag1, missing→0 ---
df["rd_expenditure"] = df["xrd"].fillna(0) / df["at_lag1"]
RD_ANCHOR = {"N": 56646, "mean": 0.0709, "sd": 0.1895, "p25": 0, "p50": 0.0021, "p75": 0.0738}
lo_rd, hi_rd = df["rd_expenditure"].quantile(0.01), df["rd_expenditure"].quantile(0.99)
df["rd_expenditure_w"] = df["rd_expenditure"].clip(lo_rd, hi_rd)

# --- Variable 11: NWC = (ACT - LCT - CHE) / (AT - CHE) (Bates num + Opler denom) ---
net_assets = df["at"] - df["che"].fillna(0)
df["nwc"] = np.where(net_assets > 0, (df["act"] - df["lct"] - df["che"].fillna(0)) / net_assets, np.nan)
NWC_ANCHOR = {"N": 56646, "mean": -0.0584, "sd": 1.0372, "p25": -0.0589, "p50": 0.0636, "p75": 0.2157}
lo_nwc, hi_nwc = df["nwc"].quantile(0.01), df["nwc"].quantile(0.99)
df["nwc_w"] = df["nwc"].clip(lo_nwc, hi_nwc)

# --- Variable 12: Industry CF Vol ---
# Requires FF49 classifier. Use F1D's existing builder.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from f1d.shared.variables.ff49_industry_classifier import FF49IndustryClassifierBuilder

ff49_builder = FF49IndustryClassifierBuilder()
ff49_result = ff49_builder.build(years=range(1997, 2016), root_path=ROOT)
ff49 = ff49_result.data[["gvkey", "fyear", "ff49_code"]].copy()
ff49["gvkey"] = ff49["gvkey"].astype(str).str.zfill(6).astype("Int64")
df["gvkey"] = df["gvkey"].astype("Int64")
df = df.merge(ff49, on=["gvkey", "fyear"], how="left")

# Build industry-CF vol per paper recipe
# Step 1: industry-MEAN CF per (ff49_code, fyear) — use WINSORIZED CF
ind_cf = df.dropna(subset=["ff49_code"]).copy()
ind_mean = ind_cf.groupby(["ff49_code", "fyear"])["cash_flow_w"].mean().reset_index()
ind_mean.rename(columns={"cash_flow_w": "ind_mean_cf"}, inplace=True)

# Step 2: rolling σ over [t-10, t-1] with ≥3 obs floor
ind_mean = ind_mean.sort_values(["ff49_code", "fyear"])
rows = []
for ff, grp in ind_mean.groupby("ff49_code"):
    yr_to_mean = dict(zip(grp["fyear"], grp["ind_mean_cf"]))
    for _, row in grp.iterrows():
        t = int(row["fyear"])
        window = [yr_to_mean[y] for y in range(t-10, t) if y in yr_to_mean and not pd.isna(yr_to_mean[y])]
        sigma = float(np.std(window, ddof=1)) if len(window) >= 3 else np.nan
        rows.append({"ff49_code": ff, "fyear": t, "industry_cf_vol": sigma})
icv = pd.DataFrame(rows)

# Merge back
df = df.merge(icv, on=["ff49_code", "fyear"], how="left")
ICV_ANCHOR = {"N": 56646, "mean": 0.3440, "sd": 0.5270, "p25": 0.0825, "p50": 0.1403, "p75": 0.2499}
lo_icv, hi_icv = df["industry_cf_vol"].quantile(0.01), df["industry_cf_vol"].quantile(0.99)
df["industry_cf_vol_w"] = df["industry_cf_vol"].clip(lo_icv, hi_icv)

# Stats
c = df["cash_w"]
print("\n=== VAR 1: CASH (winsorized 1%/99%) ===")
print(f"  N    = {len(c):,}     anchor: {ANCHOR['N']:,}")
print(f"  mean = {c.mean():.4f}     anchor: {ANCHOR['mean']:.4f}")
print(f"  sd   = {c.std():.4f}     anchor: {ANCHOR['sd']:.4f}")
print(f"  p25  = {c.quantile(0.25):.4f}     anchor: {ANCHOR['p25']:.4f}")
print(f"  p50  = {c.quantile(0.50):.4f}     anchor: {ANCHOR['p50']:.4f}")
print(f"  p75  = {c.quantile(0.75):.4f}     anchor: {ANCHOR['p75']:.4f}")
print(f"  p01  = {c.quantile(0.01):.4f}")
print(f"  p99  = {c.quantile(0.99):.4f}")

s = df["firm_size_w"]
print(f"\n=== VAR 2: FIRM SIZE = log(AT) (winsorized 1%/99%) ===")
print(f"  N    = {len(s):,}     anchor: {FS_ANCHOR['N']:,}")
print(f"  mean = {s.mean():.4f}     anchor: {FS_ANCHOR['mean']:.4f}")
print(f"  sd   = {s.std():.4f}     anchor: {FS_ANCHOR['sd']:.4f}")
print(f"  p25  = {s.quantile(0.25):.4f}     anchor: {FS_ANCHOR['p25']:.4f}")
print(f"  p50  = {s.quantile(0.50):.4f}     anchor: {FS_ANCHOR['p50']:.4f}")
print(f"  p75  = {s.quantile(0.75):.4f}     anchor: {FS_ANCHOR['p75']:.4f}")
for k, v in FS_ANCHOR.items():
    ours = s.mean() if k == "mean" else s.std() if k == "sd" else s.quantile(float(k[1:])/100) if k[0]=="p" else len(s)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

a = df["firm_age_w"]
# Also show raw age_years for diagnostics
raw_years = df["age_years"]
print(f"\n=== VAR 3: FIRM AGE = ln(years in CRSP/Compustat) (winsorized 1%/99%) ===")
print(f"  N    = {len(a):,}     anchor: {FA_ANCHOR['N']:,}")
print(f"  mean = {a.mean():.4f}     anchor: {FA_ANCHOR['mean']:.4f}")
print(f"  sd   = {a.std():.4f}     anchor: {FA_ANCHOR['sd']:.4f}")
print(f"  p25  = {a.quantile(0.25):.4f}     anchor: {FA_ANCHOR['p25']:.4f}")
print(f"  p50  = {a.quantile(0.50):.4f}     anchor: {FA_ANCHOR['p50']:.4f}")
print(f"  p75  = {a.quantile(0.75):.4f}     anchor: {FA_ANCHOR['p75']:.4f}")
print(f"  winsor lo ln(yrs)={lo_fa:.4f} hi={hi_fa:.4f}")
print(f"  DIAGNOSTIC — raw age_years distribution:")
print(f"    mean={raw_years.mean():.1f} yrs  p50={raw_years.median():.1f} yrs  p25={raw_years.quantile(0.25):.1f}  p75={raw_years.quantile(0.75):.1f}")
for k, v in FA_ANCHOR.items():
    ours = a.mean() if k == "mean" else a.std() if k == "sd" else a.quantile(float(k[1:])/100) if k[0]=="p" else len(a)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

b = df["book_leverage_w"]
print(f"\n=== VAR 4: BOOK LEVERAGE = (DLC+DLTT)/AT (winsorized 1%/99%) ===")
print(f"  N    = {len(b):,}     anchor: {BL_ANCHOR['N']:,}")
print(f"  mean = {b.mean():.4f}     anchor: {BL_ANCHOR['mean']:.4f}")
print(f"  sd   = {b.std():.4f}     anchor: {BL_ANCHOR['sd']:.4f}")
print(f"  p25  = {b.quantile(0.25):.4f}     anchor: {BL_ANCHOR['p25']:.4f}")
print(f"  p50  = {b.quantile(0.50):.4f}     anchor: {BL_ANCHOR['p50']:.4f}")
print(f"  p75  = {b.quantile(0.75):.4f}     anchor: {BL_ANCHOR['p75']:.4f}")
for k, v in BL_ANCHOR.items():
    ours = b.mean() if k == "mean" else b.std() if k == "sd" else b.quantile(float(k[1:])/100) if k[0]=="p" else len(b)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

f = df["cash_flow_w"]
print(f"\n=== VAR 5: CASH FLOW = (OIBDP-XINT-TXT-DVC)/AT (winsorized 1%/99%) ===")
print(f"  N    = {len(f):,}     anchor: {CF_ANCHOR['N']:,}")
print(f"  mean = {f.mean():.4f}     anchor: {CF_ANCHOR['mean']:.4f}")
print(f"  sd   = {f.std():.4f}     anchor: {CF_ANCHOR['sd']:.4f}")
print(f"  p25  = {f.quantile(0.25):.4f}     anchor: {CF_ANCHOR['p25']:.4f}")
print(f"  p50  = {f.quantile(0.50):.4f}     anchor: {CF_ANCHOR['p50']:.4f}")
print(f"  p75  = {f.quantile(0.75):.4f}     anchor: {CF_ANCHOR['p75']:.4f}")
for k, v in CF_ANCHOR.items():
    ours = f.mean() if k == "mean" else f.std() if k == "sd" else f.quantile(float(k[1:])/100) if k[0]=="p" else len(f)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

cx = df["capital_expenditure_w"]
print(f"\n=== VAR 6: CAPEX = CAPX/AT_lag1 (winsorized 1%/99%) ===")
print(f"  N    = {len(cx):,}     anchor: {CX_ANCHOR['N']:,}")
print(f"  mean = {cx.mean():.4f}     anchor: {CX_ANCHOR['mean']:.4f}")
print(f"  sd   = {cx.std():.4f}     anchor: {CX_ANCHOR['sd']:.4f}")
print(f"  p25  = {cx.quantile(0.25):.4f}     anchor: {CX_ANCHOR['p25']:.4f}")
print(f"  p50  = {cx.quantile(0.50):.4f}     anchor: {CX_ANCHOR['p50']:.4f}")
print(f"  p75  = {cx.quantile(0.75):.4f}     anchor: {CX_ANCHOR['p75']:.4f}")
for k, v in CX_ANCHOR.items():
    ours = cx.mean() if k == "mean" else cx.std() if k == "sd" else cx.quantile(float(k[1:])/100) if k[0]=="p" else len(cx)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

ac = df["acquisition_expenditure_w"]
print(f"\n=== VAR 7: ACQ EXP = AQC/AT_lag1 (winsorized 1%/99%) ===")
print(f"  N    = {len(ac):,}     anchor: {ACQ_ANCHOR['N']:,}")
print(f"  mean = {ac.mean():.4f}     anchor: {ACQ_ANCHOR['mean']:.4f}")
print(f"  sd   = {ac.std():.4f}     anchor: {ACQ_ANCHOR['sd']:.4f}")
print(f"  p25  = {ac.quantile(0.25):.4f}     anchor: {ACQ_ANCHOR['p25']:.4f}")
print(f"  p50  = {ac.quantile(0.50):.4f}     anchor: {ACQ_ANCHOR['p50']:.4f}")
print(f"  p75  = {ac.quantile(0.75):.4f}     anchor: {ACQ_ANCHOR['p75']:.4f}")
for k, v in ACQ_ANCHOR.items():
    ours = ac.mean() if k == "mean" else ac.std() if k == "sd" else ac.quantile(float(k[1:])/100) if k[0]=="p" else len(ac)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

dv = df["dividend_paying"]
print(f"\n=== VAR 8: DIVIDEND PAYER (0/1) = DVC>0 ===")
print(f"  N        = {len(dv):,}     anchor: {DV_ANCHOR['N']:,}")
print(f"  mean     = {dv.mean():.4f}     anchor: {DV_ANCHOR['mean']:.4f}")
print(f"  p25      = {dv.quantile(0.25):.0f}     anchor: {DV_ANCHOR['p25']}")
print(f"  p50      = {dv.quantile(0.50):.0f}     anchor: {DV_ANCHOR['p50']}")
print(f"  p75      = {dv.quantile(0.75):.0f}     anchor: {DV_ANCHOR['p75']}")
print(f"  % payers = {dv.mean()*100:.1f}%  paper: {DV_ANCHOR['mean']*100:.1f}%")
for k, v in DV_ANCHOR.items():
    ours = dv.mean() if k == "mean" else dv.quantile(float(k[1:])/100) if k[0]=="p" else len(dv)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

mt = df["market_to_book_w"]
print(f"\n=== VAR 9: MARKET-TO-BOOK = (AT-CEQ+PRCC_F*CSHO)/AT (winsorized 1%/99%) ===")
print(f"  N    = {len(mt):,}     anchor: {MTB_ANCHOR['N']:,}")
print(f"  mean = {mt.mean():.4f}     anchor: {MTB_ANCHOR['mean']:.4f}")
print(f"  sd   = {mt.std():.4f}     anchor: {MTB_ANCHOR['sd']:.4f}")
print(f"  p25  = {mt.quantile(0.25):.4f}     anchor: {MTB_ANCHOR['p25']:.4f}")
print(f"  p50  = {mt.quantile(0.50):.4f}     anchor: {MTB_ANCHOR['p50']:.4f}")
print(f"  p75  = {mt.quantile(0.75):.4f}     anchor: {MTB_ANCHOR['p75']:.4f}")
for k, v in MTB_ANCHOR.items():
    ours = mt.mean() if k == "mean" else mt.std() if k == "sd" else mt.quantile(float(k[1:])/100) if k[0]=="p" else len(mt)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

rd = df["rd_expenditure_w"]
print(f"\n=== VAR 10: R&D EXP = XRD/AT_lag1, missing->0 (winsorized 1%/99%) ===")
print(f"  N    = {len(rd):,}     anchor: {RD_ANCHOR['N']:,}")
print(f"  mean = {rd.mean():.4f}     anchor: {RD_ANCHOR['mean']:.4f}")
print(f"  sd   = {rd.std():.4f}     anchor: {RD_ANCHOR['sd']:.4f}")
print(f"  p25  = {rd.quantile(0.25):.4f}     anchor: {RD_ANCHOR['p25']:.4f}")
print(f"  p50  = {rd.quantile(0.50):.4f}     anchor: {RD_ANCHOR['p50']:.4f}")
print(f"  p75  = {rd.quantile(0.75):.4f}     anchor: {RD_ANCHOR['p75']:.4f}")
for k, v in RD_ANCHOR.items():
    ours = rd.mean() if k == "mean" else rd.std() if k == "sd" else rd.quantile(float(k[1:])/100) if k[0]=="p" else len(rd)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

nw = df["nwc_w"]
print(f"\n=== VAR 11: NWC = (ACT-LCT-DLC)/(AT-CHE) (winsorized 1%/99%) ===")
print(f"  N    = {len(nw):,}     anchor: {NWC_ANCHOR['N']:,}")
print(f"  mean = {nw.mean():.4f}     anchor: {NWC_ANCHOR['mean']:.4f}")
print(f"  sd   = {nw.std():.4f}     anchor: {NWC_ANCHOR['sd']:.4f}")
print(f"  p25  = {nw.quantile(0.25):.4f}     anchor: {NWC_ANCHOR['p25']:.4f}")
print(f"  p50  = {nw.quantile(0.50):.4f}     anchor: {NWC_ANCHOR['p50']:.4f}")
print(f"  p75  = {nw.quantile(0.75):.4f}     anchor: {NWC_ANCHOR['p75']:.4f}")
for k, v in NWC_ANCHOR.items():
    ours = nw.mean() if k == "mean" else nw.std() if k == "sd" else nw.quantile(float(k[1:])/100) if k[0]=="p" else len(nw)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

ic = df["industry_cf_vol_w"]
print(f"\n=== VAR 12: Ind CF Vol = sigma(FF49 mean CF, [t-10,t-1], >=3y) ===")
print(f"  N    = {len(ic):,}     anchor: {ICV_ANCHOR['N']:,}")
print(f"  n_valid = {ic.notna().sum():,}  (non-NaN after >=3y floor)")
print(f"  mean = {ic.mean():.4f}     anchor: {ICV_ANCHOR['mean']:.4f}")
print(f"  sd   = {ic.std():.4f}     anchor: {ICV_ANCHOR['sd']:.4f}")
print(f"  p25  = {ic.quantile(0.25):.4f}     anchor: {ICV_ANCHOR['p25']:.4f}")
print(f"  p50  = {ic.quantile(0.50):.4f}     anchor: {ICV_ANCHOR['p50']:.4f}")
print(f"  p75  = {ic.quantile(0.75):.4f}     anchor: {ICV_ANCHOR['p75']:.4f}")
for k, v in ICV_ANCHOR.items():
    ours = ic.mean() if k == "mean" else ic.std() if k == "sd" else ic.quantile(float(k[1:])/100) if k[0]=="p" else len(ic)
    if v > 0:
        pct = (ours - v) / v * 100
        print(f"  DIFF {k}: ours={ours:.4f} paper={v:.4f} ({pct:+.1f}%)")

# ===================================================================
# FINAL: Complete-case merge + side-by-side comparison
# ===================================================================
ALL_VARS = {
    "cash": (df["cash_w"], {"N": 56646, "mean": 0.2008, "sd": 0.2231, "p25": 0.0285, "p50": 0.1044, "p75": 0.2913}),
    "firm_size": (df["firm_size_w"], {"N": 56646, "mean": 5.6136, "sd": 2.0593, "p25": 4.0819, "p50": 5.5717, "p75": 7.0455}),
    "firm_age": (df["firm_age_w"], {"N": 56646, "mean": 7.3003, "sd": 0.8889, "p25": 2.0179, "p50": 5.0435, "p75": 11.0918}),
    "book_leverage": (df["book_leverage_w"], {"N": 56646, "mean": 0.2362, "sd": 0.3177, "p25": 0.0229, "p50": 0.1863, "p75": 0.3528}),
    "cash_flow": (df["cash_flow_w"], {"N": 56646, "mean": -0.3758, "sd": 4.8386, "p25": -0.0150, "p50": 0.0684, "p75": 0.1210}),
    "capital_expenditure": (df["capital_expenditure_w"], {"N": 56646, "mean": 0.0657, "sd": 0.1248, "p25": 0.0174, "p50": 0.0364, "p75": 0.0729}),
    "acquisition_expenditure": (df["acquisition_expenditure_w"], {"N": 56646, "mean": 0.0451, "sd": 0.1672, "p25": 0, "p50": 0, "p75": 0.0144}),
    "dividend_paying": (df["dividend_paying"], {"N": 56646, "mean": 0.2767, "sd": None, "p25": 0, "p50": 0, "p75": 1}),
    "market_to_book": (df["market_to_book_w"], {"N": 56646, "mean": 2.1592, "sd": 2.9919, "p25": 1.1104, "p50": 1.5113, "p75": 2.3119}),
    "rd_expenditure": (df["rd_expenditure_w"], {"N": 56646, "mean": 0.0709, "sd": 0.1895, "p25": 0, "p50": 0.0021, "p75": 0.0738}),
    "nwc": (df["nwc_w"], {"N": 56646, "mean": -0.0584, "sd": 1.0372, "p25": -0.0589, "p50": 0.0636, "p75": 0.2157}),
    "industry_cf_vol": (df["industry_cf_vol_w"], {"N": 56646, "mean": 0.3440, "sd": 0.5270, "p25": 0.0825, "p50": 0.1403, "p75": 0.2499}),
}

# Build complete-case panel — collect all series, concat, drop NaN
cc_cols = {name: data for name, (data, _) in ALL_VARS.items()}
cc = pd.concat(cc_cols, axis=1)
cc = cc.dropna()

print("\n" + "="*80)
print("COMPLETE-CASE MERGE: All 12 variables non-missing")
print(f"  N = {len(cc):,}  (paper: 56,646)")
print(f"  Gap = {len(cc) - 56646:+,}")
print("="*80)

for name, (_, anchor) in ALL_VARS.items():
    s = cc[name]
    a_mean = anchor.get("mean")
    a_sd = anchor.get("sd")
    a_p50 = anchor.get("p50", 0)
    print(f"\n  {name}:")
    print(f"    N={len(s):,}  mean={s.mean():.4f} (paper {a_mean})  p50={s.median():.4f} (paper {a_p50})")
    if a_sd:
        print(f"    SD={s.std():.4f} (paper {a_sd})")
    if a_mean and a_mean != 0:
        print(f"    diffmean={((s.mean()-a_mean)/abs(a_mean)*100):+.1f}%  diffp50={((s.median()-a_p50)/abs(a_p50)*100):+.1f}%" if a_p50 != 0 else f"    diffmean={((s.mean()-a_mean)/abs(a_mean)*100):+.1f}%")
