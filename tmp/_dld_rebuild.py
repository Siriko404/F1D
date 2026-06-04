"""Boasiako-Keefe 2021 — Table 2 Column 1 pure replication.
Greenfield rebuild. Process-locked per 02c adversarial review.
Single script: raw data -> DiD estimate.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")

# ── PAPER ANCHORS ──
T2C1 = {"beta": 0.0076, "se": 0.0031, "N": 56646, "adj_r2": 0.4939}

# ── STEP 1: Load data 1997-2015 ──
FIELDS = ["gvkey","datadate","fyear","sic","state","at","che","dlc","dltt",
          "ceq","prcc_f","csho","oibdp","xint","txt","dvc","capx","aqc","xrd","act","lct","wcap"]
dtypes = {c: float for c in ["at","che","dlc","dltt","ceq","prcc_f","csho",
                              "oibdp","xint","txt","dvc","capx","aqc","xrd","act","lct","wcap"]}
dtypes.update({"gvkey": "Int64", "fyear": "Int64", "sic": str, "state": str})
print("1. Loading Compustat...")
df = pd.read_csv(ROOT / "inputs/Compustat_Annual/compustat_annual.csv",
                 usecols=FIELDS, dtype=dtypes, low_memory=False)
df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
for c in dtypes:
    if dtypes[c] == float:
        df[c] = pd.to_numeric(df[c], errors="coerce")
n0 = len(df); print(f"   Raw: {n0:,}")

# ── STEP 2: Sample filters ──
df = df[(df["fyear"] >= 1997) & (df["fyear"] <= 2015)].copy()
n1 = len(df); print(f"   1997-2015: {n1:,}  (drop {n0-n1:,})")

# SIC: drop 4900-4999, 6000-6999
sic4 = df["sic"].str[:4]
bad = sic4.str.fullmatch(r"49[0-9]{2}|6[0-9]{4}", na=False)
df = df[~bad].copy()
n2 = len(df); print(f"   Drop financials+utilities: {n2:,}  (drop {n1-n2:,})")

# AT > 0
df.dropna(subset=["at"], inplace=True)
df = df[df["at"] > 0].copy()
n3 = len(df); print(f"   AT>0: {n3:,}  (drop {n2-n3:,})")

# Dedup (gvkey, fyear) — keep last datadate
df.sort_values(["gvkey","fyear","datadate"], inplace=True)
df.drop_duplicates(subset=["gvkey","fyear"], keep="last", inplace=True)
n4 = len(df); print(f"   Dedup (gvkey,fyear): {n4:,}  (drop {n3-n4:,})")

# AT_lag1 for BoY denominators
df["at_lag1"] = df.groupby("gvkey")["at"].shift(1)
df.dropna(subset=["at_lag1"], inplace=True)
df = df[df["at_lag1"] > 0].copy()
n5 = len(df); print(f"   AT_lag1>0: {n5:,}  (drop {n4-n5:,})")

# State non-missing (needed for treatment)
df = df[df["state"].notna() & (df["state"] != "")].copy()
valid_states = {"AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID",
    "IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV",
    "NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT",
    "VT","VA","WA","WV","WI","WY","PR","VI","GU"}
df = df[df["state"].isin(valid_states)].copy()
n6 = len(df); print(f"   State valid (50+DC): {n6:,}  (drop {n5-n6:,})")

# CRSP/Compustat link (paper-verbatim: "merged CRSP/Compustat database")
ccm = pd.read_parquet(ROOT / "inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet",
                       columns=["gvkey","LINKTYPE","LINKPRIM"])
ccm = ccm[ccm["LINKTYPE"].isin(["LU","LC"]) & ccm["LINKPRIM"].isin(["P","C"])]
crsp_gvkeys = set(ccm["gvkey"].dropna().astype(int))
df = df[df["gvkey"].astype(int).isin(crsp_gvkeys)].copy()
n7 = len(df); print(f"   CRSP-linked: {n7:,}  (drop {n6-n7:,})")

# ── STEP 3: Construct all variables (RAW, pre-winsorize) ──
print("2. Constructing variables...")
# DV: Cash = che / at_lag1
df["cash"] = df["che"].fillna(0) / df["at_lag1"]

# Firm Size = log(at)
df["firm_size"] = np.log(df["at"])

# Firm Age = ln(years in CRSP/Compustat)
ccm_dates = pd.read_parquet(ROOT / "inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet",
    columns=["gvkey","LINKDT","LINKTYPE","LINKPRIM"])
ccm_dates = ccm_dates[ccm_dates["LINKTYPE"].isin(["LU","LC"]) & ccm_dates["LINKPRIM"].isin(["P","C"])]
ccm_dates["LINKDT"] = pd.to_datetime(ccm_dates["LINKDT"], errors="coerce")
first_listing = ccm_dates.groupby("gvkey")["LINKDT"].min().reset_index()
first_listing["first_fyear"] = first_listing["LINKDT"].dt.year
df = df.merge(first_listing[["gvkey","first_fyear"]], on="gvkey", how="left")
df["age_years"] = df["fyear"].astype(int) - df["first_fyear"]
df["firm_age"] = np.log(df["age_years"].clip(lower=1).astype(float))

# Book Leverage = (dlc + dltt) / at
df["book_leverage"] = (df["dlc"].fillna(0) + df["dltt"].fillna(0)) / df["at"]

# Market-to-book = (at - ceq + prcc_f*csho) / at
df["market_to_book"] = (df["at"] - df["ceq"] + df["prcc_f"] * df["csho"]) / df["at"]

# Cash Flow = (oibdp - xint - txt - dvc) / at
df["cash_flow"] = (df["oibdp"].fillna(0) - df["xint"].fillna(0)
                   - df["txt"].fillna(0) - df["dvc"].fillna(0)) / df["at"]

# CapEx = capx / at_lag1
df["capital_expenditure"] = df["capx"] / df["at_lag1"]

# Acq Exp = aqc / at_lag1; missing->0 (Bates 2009 inheritance)
df["acquisition_expenditure"] = df["aqc"].fillna(0) / df["at_lag1"]

# Dividend Payer = 1 if dvc>0; missing->0 (paper-explicit)
df["dividend_paying"] = (df["dvc"].fillna(0) > 0).astype(int)

# R&D = xrd / at_lag1; missing->0 (Bates 2009 inheritance)
df["rd_expenditure"] = df["xrd"].fillna(0) / df["at_lag1"]

# NWC = (wc_or_actlct - che) / at — WCAP preferred, ACT-LCT fallback, AT denom
nwc_num = np.where(df["wcap"].notna(), df["wcap"], df["act"] - df["lct"])
df["nwc"] = (nwc_num - df["che"].fillna(0)) / df["at"]

# ── STEP 4: Disclosure Law Treatment ──
print("3. Assigning Disclosure Law treatment...")
# Load NCSL passage years
passage = pd.read_csv(ROOT / "inputs/Boasiako_replication/NCSL/disclosure_law_passage_years.csv")
passage_map = dict(zip(passage["state_code"], passage["year_passed"].astype(int)))
# Y+1: Disclosure Law = 1 if fyear >= passage_year + 1
def assign_dl(row):
    s = row["state"]
    fy = row["fyear"]
    if pd.isna(fy) or s not in passage_map:
        return 0
    return 1 if int(fy) >= passage_map[s] + 1 else 0
df["Disclosure_Law"] = df.apply(assign_dl, axis=1).astype(int)
print(f"   Treated (DL=1): {(df['Disclosure_Law']==1).sum():,} / {len(df):,}")

# ── STEP 5: Winsorize pooled (ALL continuous vars at once on post-filter panel) ──
print("4. Winsorizing pooled 1%/99%...")
CONTINUOUS = ["cash","firm_size","firm_age","book_leverage","market_to_book",
              "cash_flow","capital_expenditure","acquisition_expenditure",
              "rd_expenditure","nwc"]
for col in CONTINUOUS:
    s = df[col].dropna()
    if len(s) < 10: continue
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    df[col + "_w"] = df[col].clip(lo, hi)

# ── STEP 6: Industry CF Vol ──
print("5. Computing Industry CF Volatility...")
# FF49 classification (import from F1D for consistency)
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from f1d.shared.variables.ff49_industry_classifier import FF49IndustryClassifierBuilder
ff49 = FF49IndustryClassifierBuilder().build(years=range(1997, 2016), root_path=ROOT).data
ff49["gvkey"] = ff49["gvkey"].astype(str).str.zfill(6).astype("Int64")
df["gvkey"] = df["gvkey"].astype("Int64")
df = df.merge(ff49[["gvkey","fyear","ff49_code"]], on=["gvkey","fyear"], how="left")

# Use WINSORIZED CF for industry vol (process-locked: winsorize before aggregation)
ind_cf = df.dropna(subset=["ff49_code"]).copy()
ind_mean = ind_cf.groupby(["ff49_code","fyear"])["cash_flow_w"].mean().reset_index()
ind_mean.rename(columns={"cash_flow_w":"ind_mean_cf"}, inplace=True)
ind_mean = ind_mean.sort_values(["ff49_code","fyear"])

# Rolling sigma [t-10, t-1], >=3 obs
icv_rows = []
for ff, grp in ind_mean.groupby("ff49_code"):
    yr_map = dict(zip(grp["fyear"], grp["ind_mean_cf"]))
    for _, row in grp.iterrows():
        t = int(row["fyear"])
        window = [yr_map[y] for y in range(t-10, t) if y in yr_map and not pd.isna(yr_map[y])]
        sigma = float(np.std(window, ddof=1)) if len(window) >= 3 else np.nan
        icv_rows.append({"ff49_code": ff, "fyear": t, "industry_cf_vol": sigma})
icv_df = pd.DataFrame(icv_rows)
df = df.merge(icv_df, on=["ff49_code","fyear"], how="left")
# Winsorize IndCFVol itself
s_icv = df["industry_cf_vol"].dropna()
if len(s_icv) >= 10:
    lo_icv, hi_icv = s_icv.quantile(0.01), s_icv.quantile(0.99)
    df["industry_cf_vol_w"] = df["industry_cf_vol"].clip(lo_icv, hi_icv)

# Add dummy column for unwinsorized binary
df["dividend_paying_w"] = df["dividend_paying"]  # no winsorize on binary

# ── STEP 7: Complete-case ──
print("6. Complete-case merge...")
ALL_W = ["cash_w","firm_size_w","firm_age_w","book_leverage_w","market_to_book_w",
         "cash_flow_w","capital_expenditure_w","acquisition_expenditure_w",
         "rd_expenditure_w","nwc_w","dividend_paying_w","industry_cf_vol_w"]
cc = df[ALL_W + ["gvkey","fyear","state","ff49_code","Disclosure_Law"]].dropna()
print(f"   N = {len(cc):,}  (paper: 56,646)  gap = {len(cc)-56646:+,}")

# Per-variable drop diagnostic
print("   Per-variable valid counts (pre-complete-case):")
for col in ALL_W:
    n_valid = df[col].notna().sum()
    n_drop = len(df) - n_valid
    print(f"     {col}: {n_valid:,} valid, {n_drop:,} dropped" if n_drop else f"     {col}: {n_valid:,} valid")

# Which variable has the FEWEST valid obs before complete-case?
min_var = min(ALL_W, key=lambda c: df[c].notna().sum())
print(f"   BOTTLENECK variable: {min_var} ({df[min_var].notna().sum():,} valid)")

# ── STEP 8: Summary stats ──
print("\n" + "="*70)
print("SUMMARY STATS (winsorized, complete-case)")
print("="*70)
ANCHORS = {
    "cash_w": (0.2008, 0.2231, 0.0285, 0.1044, 0.2913),
    "firm_size_w": (5.6136, 2.0593, 4.0819, 5.5717, 7.0455),
    "firm_age_w": (7.3003, 0.8889, 2.0179, 5.0435, 11.0918),
    "book_leverage_w": (0.2362, 0.3177, 0.0229, 0.1863, 0.3528),
    "market_to_book_w": (2.1592, 2.9919, 1.1104, 1.5113, 2.3119),
    "cash_flow_w": (-0.3758, 4.8386, -0.0150, 0.0684, 0.1210),
    "capital_expenditure_w": (0.0657, 0.1248, 0.0174, 0.0364, 0.0729),
    "acquisition_expenditure_w": (0.0451, 0.1672, 0, 0, 0.0144),
    "rd_expenditure_w": (0.0709, 0.1895, 0, 0.0021, 0.0738),
    "nwc_w": (-0.0584, 1.0372, -0.0589, 0.0636, 0.2157),
    "dividend_paying_w": (0.2767, None, 0, 0, 1),
    "industry_cf_vol_w": (0.3440, 0.5270, 0.0825, 0.1403, 0.2499),
}
SUMSTAT = {}
for var, (a_mean, a_sd, a_p25, a_p50, a_p75) in ANCHORS.items():
    s = cc[var]
    print(f"  {var}: N={len(s):,}  mean={s.mean():.4f} (a={a_mean})  "
          f"p50={s.median():.4f} (a={a_p50})  "
          f"SD={s.std():.4f} (a={a_sd})" if a_sd else
          f"p50={s.median():.4f} (a={a_p50})")
    SUMSTAT[var] = {"N": len(s), "mean": float(s.mean()), "sd": float(s.std()) if a_sd else None,
                    "p25": float(s.quantile(0.25)), "p50": float(s.median()),
                    "p75": float(s.quantile(0.75))}

# Save to outputs for table generator
import json
sumstat_out = ROOT / "outputs" / "econometric" / "h1_5_disclosure_law_did" / "summary_stats" / "latest_summary_stats.json"
sumstat_out.parent.mkdir(parents=True, exist_ok=True)
sumstat_out.write_text(json.dumps(SUMSTAT, indent=2), encoding="utf-8")
print(f"Summary stats saved: {sumstat_out}")

# ── STEP 9: Estimate DiD (Table 2 Col 1: year + industry + state FE, state-cluster SE) ──
print("\n" + "="*70)
print("DiD ESTIMATION — Table 2 Column (1)")
print("="*70)

from linearmodels.panel import PanelOLS

CTRLS = ["firm_size_w","firm_age_w","book_leverage_w","market_to_book_w",
         "cash_flow_w","capital_expenditure_w","acquisition_expenditure_w",
         "rd_expenditure_w","nwc_w","dividend_paying_w","industry_cf_vol_w"]
COLS_DID = ["cash_w","Disclosure_Law"] + CTRLS + ["gvkey","fyear","state","ff49_code"]
did_df = cc[COLS_DID].dropna().copy()

# State dummies (drop_first), Industry + Year absorbed
state_dum = pd.get_dummies(did_df["state"], prefix="st", drop_first=True, dtype=float)
exog = pd.concat([did_df[["Disclosure_Law"] + CTRLS], state_dum], axis=1)

did_df = did_df.set_index(["gvkey","fyear"])
exog.index = did_df.index

# State-cluster SE
state_clusters = pd.DataFrame({"state": did_df["state"]}, index=did_df.index)

model = PanelOLS(
    dependent=did_df["cash_w"],
    exog=exog,
    entity_effects=False,
    time_effects=True,
    other_effects=did_df["ff49_code"].astype("category").cat.codes,
    drop_absorbed=True,
    check_rank=False,
)
result = model.fit(cov_type="clustered", clusters=state_clusters, cluster_entity=False)
beta = result.params["Disclosure_Law"]
se = result.std_errors["Disclosure_Law"]
t = result.tstats["Disclosure_Law"]
p2 = result.pvalues["Disclosure_Law"]
p1 = p2 / 2 if beta > 0 else 1 - p2 / 2
stars = "***" if p1<0.01 else "**" if p1<0.05 else "*" if p1<0.10 else ""

print(f"  beta(Disclosure Law) = {beta:+.4f}{stars}  (paper: {T2C1['beta']:+.4f}**)")
print(f"  SE                   = {se:.4f}         (paper: {T2C1['se']:.4f})")
print(f"  t                    = {t:+.2f}")
print(f"  p_one                = {p1:.4f}")
print(f"  N                    = {result.nobs:,}         (paper: {T2C1['N']:,})")
print(f"  R^2                  = {result.rsquared:.4f}   (paper Adj R^2: {T2C1['adj_r2']:.4f})")

# All control coefficients
print("\n  Control coefficients:")
for c in CTRLS:
    if c in result.params.index:
        b = result.params[c]; s = result.std_errors[c]; p = result.pvalues[c]
        sig = "***" if p<0.01 else "**" if p<0.05 else "*" if p<0.10 else ""
        print(f"    {c}: {b:+.4f}{sig}  (SE={s:.4f})")
