"""RA Round 4 action #5: I/B/E/S asymmetric attrition audit.
Test whether stricter I/B/E/S criteria unbalances HIGH/LOW split toward paper's 449/360.
Hypothesis: low-beta firms less analyst-covered → stricter criteria drop more control firms → lift delta."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"

# ============================================================
# 1. Load betas (from run_did_fix1.py's current best)
# ============================================================
print("=" * 60)
print("1. Load betas + build DiD sample")
print("=" * 60)

# Rebuild the exact same Compustat survivor set as run_did_fix1.py
comp_raw = pd.read_parquet(CSV, columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
for c in ["atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]: comp_raw[c]=pd.to_numeric(comp_raw[c],errors="coerce")
comp_raw["txditcq"]=comp_raw["txditcq"].fillna(0); comp_raw["gvkey"]=comp_raw["gvkey"].astype(str).str.zfill(6)
comp_raw=comp_raw[(comp_raw["fyearq"]>=2010)&(comp_raw["fyearq"]<=2016)]; comp_raw=comp_raw[comp_raw["fqtr"].isin([1,2,3,4])]
comp_raw=comp_raw[(comp_raw["curcdq"]=="USD")&(comp_raw["fic"]=="USA")]; comp_raw=comp_raw[(comp_raw["atq"]>0)&(comp_raw["saleq"]>0)]
csic=pd.to_numeric(comp_raw["sic"],errors="coerce"); comp_raw=comp_raw[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp_raw["mktcap"]=comp_raw["cshoq"]*comp_raw["prccq"]; comp_raw=comp_raw[(comp_raw["atq"]>=10)&(comp_raw["mktcap"]>=10)]
comp_raw["atq_l1"]=comp_raw.groupby("gvkey")["atq"].shift(1); comp_raw["saleq_l4"]=comp_raw.groupby("gvkey")["saleq"].shift(4)
has_inv=comp_raw["capxy"].notna()&comp_raw["atq_l1"].notna(); has_cf=comp_raw["oibdpq"].notna()&comp_raw["atq_l1"].notna()
has_q=comp_raw["cshoq"].notna()&comp_raw["prccq"].notna()&comp_raw["atq"].notna()&comp_raw["ceqq"].notna()
has_sg=comp_raw["saleq"].notna()&comp_raw["saleq_l4"].notna()
comp_raw=comp_raw[has_inv&comp_raw["atq"].notna()&has_cf&has_q&has_sg]
comp_raw=comp_raw.sort_values(["gvkey","fyearq","fqtr"]); comp_raw["cal_yr_qtr"]=comp_raw["fyearq"].astype(int)*10+comp_raw["fqtr"].astype(int)
res_rows=[]
for gk,grp in comp_raw.groupby("gvkey"):
    grp=grp.sort_values("cal_yr_qtr"); runs,cur=[],[]
    for _,row in grp.iterrows():
        if not cur: cur=[row.name]
        else:
            pq=grp.loc[cur[-1],"cal_yr_qtr"]; tq=row["cal_yr_qtr"]; exp=pq+1
            if pq%10==4: exp=(pq//10+1)*10+1
            if tq==exp: cur.append(row.name)
            else: runs.append(cur); cur=[row.name]
    runs.append(cur)
    if runs: best=max(runs,key=len)
    if runs and len(best)>=12: res_rows.append(grp.loc[best])
comp_f7=pd.concat(res_rows,ignore_index=True) if res_rows else pd.DataFrame()
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f: fic=pd.read_csv(io.BytesIO(f.read()),sep="\t",usecols=["gvkey","year","icode100"])
fic["gvkey"]=fic["gvkey"].astype(str).str.zfill(6); comp_f7["year"]=comp_f7["cal_yr_qtr"]//10
comp_f7=comp_f7.merge(fic,on=["gvkey","year"],how="inner")
comp_f7["gvkey"]=comp_f7["gvkey"].astype(str).str.zfill(6)
comp_f7=comp_f7.set_index(["gvkey","cal_yr_qtr"]).sort_index()
print(f"F1-F8 survivors: {len(comp_f7):,} obs, {comp_f7.reset_index()['gvkey'].nunique():,} firms")
survivor_gvkeys=set(comp_f7.reset_index()["gvkey"].unique())

# Load betas (current best)
betas=pd.read_parquet(ROOT/"tmp"/"beta_uk_final.parquet")
print(f"Beta file: {len(betas):,} firms")
# Note: this is full-CRSP betas. Filter to survivors.
betas=betas[betas["gvkey"].isin(survivor_gvkeys)]
print(f"Beta on survivors: {len(betas):,} firms")

# Rank tercile on nonnegative (same as run_did_fix1.py)
bpos=betas[betas["beta_uk"]>=0]
t1,t2=bpos["beta_uk"].quantile(1/3),bpos["beta_uk"].quantile(2/3)
betas["HIGH"]=(betas["beta_uk"]>=t2).astype(int)
betas["LOW"]=((betas["beta_uk"]>=0)&(betas["beta_uk"]<=t1)).astype(int)
print(f"Tercile cutpoints: T1={t1:.4f}, T2={t2:.4f}")
print(f"HIGH={betas['HIGH'].sum()}, LOW={betas['LOW'].sum()}, NEG={len(betas[betas['beta_uk']<0])}")
beta_groups=betas[["gvkey","beta_uk","HIGH","LOW"]].copy()

del comp_raw

# ============================================================
# 2. Load I/B/E/S raw and trace merge paths
# ============================================================
print(f"\n{'='*60}")
print("2. I/B/E/S merge-path audit")
print("="*60)

with zipfile.ZipFile(ROOT/"inputs"/"tr_ibes"/"ibes_statsum.zip") as z:
    with z.open(z.namelist()[0]) as f:
        ibes=pd.read_csv(f,usecols=["TICKER","CUSIP","OFTIC","STATPERS","MEASURE","FISCALP","FPI","MEANEST","FPEDATS","USFIRM","CURCODE","NUMEST"],
            dtype={"TICKER":"str","CUSIP":"str","OFTIC":"str"},low_memory=False)
ibes["FPI_n"]=pd.to_numeric(ibes["FPI"],errors="coerce")
ibes["NUMEST_n"]=pd.to_numeric(ibes["NUMEST"],errors="coerce")
ibes=ibes[(ibes["MEASURE"]=="EPS")&(ibes["FISCALP"]=="QTR")&(ibes["FPI_n"]==6)&(ibes["CURCODE"]=="USD")&(ibes["USFIRM"]==1)]
ibes["STATPERS"]=pd.to_datetime(ibes["STATPERS"]); ibes["FPEDATS"]=pd.to_datetime(ibes["FPEDATS"])
ibes=ibes[(ibes["FPEDATS"]>="2010-01-01")&(ibes["FPEDATS"]<="2017-03-31")]; ibes=ibes[ibes["STATPERS"]<ibes["FPEDATS"]]
ibes=ibes.sort_values(["TICKER","FPEDATS","STATPERS"]); ibes=ibes.drop_duplicates(subset=["TICKER","FPEDATS"],keep="last")
ibes["M"]=pd.to_numeric(ibes["MEANEST"],errors="coerce")
fy=ibes["FPEDATS"].dt.year*10+ibes["FPEDATS"].dt.quarter; yr,qtr=fy//10,fy%10
ibes["cyq"]=(np.where(qtr==1,yr-1,yr)*10+np.where(qtr==1,4,qtr-1)).astype(np.int64)
ibes["CUSIP8"]=ibes["CUSIP"].astype(str).str[:8]

# Compustat identifiers
cm2=pd.read_parquet(CSV,columns=["gvkey","tic","cusip","datadate"]); cm2["gvkey"]=cm2["gvkey"].astype(str).str.zfill(6)
cm2["datadate"]=pd.to_datetime(cm2["datadate"]); cm2=cm2[(cm2["datadate"]>="2010-01-01")&(cm2["datadate"]<="2017-03-31")]
cm2["cyq"]=(cm2["datadate"].dt.year*10+cm2["datadate"].dt.quarter).astype(np.int64); cm2["cusip8"]=cm2["cusip"].astype(str).str[:8]

# CUSIP merge
vcc=ibes.merge(cm2[["gvkey","cusip8","cyq"]].drop_duplicates(),left_on=["CUSIP8","cyq"],right_on=["cusip8","cyq"],how="inner")
# Ticker merge
vtt=ibes.merge(cm2[["gvkey","tic","cyq"]].drop_duplicates(),left_on=["OFTIC","cyq"],right_on=["tic","cyq"],how="inner")

# Tag merge source per (gvkey, cyq)
cusip_pairs=set(zip(vcc["gvkey"],vcc["cyq"]))
ticker_pairs=set(zip(vtt["gvkey"],vtt["cyq"]))
cusip_only=cusip_pairs-ticker_pairs
ticker_only=ticker_pairs-cusip_pairs
both_pairs=cusip_pairs&ticker_pairs

print(f"CUSIP match: {len(cusip_pairs):,} (gvkey,cyq) pairs")
print(f"Ticker match: {len(ticker_pairs):,}")
print(f"CUSIP only: {len(cusip_only):,}")
print(f"Ticker only: {len(ticker_only):,}")
print(f"Both: {len(both_pairs):,}")

# ============================================================
# 3. Coverage by beta tercile
# ============================================================
print(f"\n{'='*60}")
print("3. I/B/E/S coverage by beta tercile")
print("="*60)

# Tag each survivor gvkey with its I/B/E/S merge method
ibes_gvkeys_cusip=set(p[0] for p in cusip_pairs)
ibes_gvkeys_ticker=set(p[0] for p in ticker_pairs)
ibes_gvkeys_cusip_only=set(p[0] for p in cusip_only)
ibes_gvkeys_ticker_only=set(p[0] for p in ticker_only)
ibes_gvkeys_both=set(p[0] for p in both_pairs)
ibes_gvkeys_any=ibes_gvkeys_cusip|ibes_gvkeys_ticker

for label, gvkeys in [("HIGH", set(beta_groups[beta_groups["HIGH"]==1]["gvkey"])),
                        ("LOW", set(beta_groups[beta_groups["LOW"]==1]["gvkey"])),
                        ("MID", set(bpos[~bpos["gvkey"].isin(beta_groups[beta_groups["HIGH"]==1]["gvkey"])&~bpos["gvkey"].isin(beta_groups[beta_groups["LOW"]==1]["gvkey"])]["gvkey"]))]:
    n=len(gvkeys)
    any_ibes=len(gvkeys&ibes_gvkeys_any)
    c_only=len(gvkeys&ibes_gvkeys_cusip_only)
    t_only=len(gvkeys&ibes_gvkeys_ticker_only)
    both=len(gvkeys&ibes_gvkeys_both)
    no_ibes=n-any_ibes
    print(f"\n{label} (n={n}):")
    print(f"  Any IBES: {any_ibes} ({any_ibes/n*100:.1f}%)")
    print(f"  No IBES: {no_ibes} ({no_ibes/n*100:.1f}%)")
    print(f"  CUSIP only: {c_only} ({c_only/n*100:.1f}%)")
    print(f"  Ticker only: {t_only} ({t_only/n*100:.1f}%)")
    print(f"  Both: {both} ({both/n*100:.1f}%)")

# ============================================================
# 4. Simulate: what happens under stricter I/B/E/S criteria?
# ============================================================
print(f"\n{'='*60}")
print("4. Stricter I/B/E/S criteria — impact on HIGH/LOW counts")
print("="*60)

criteria = {
    "Current (CUSIP OR ticker)": ibes_gvkeys_any,
    "CUSIP match ONLY": ibes_gvkeys_cusip,
    "Ticker match ONLY": ibes_gvkeys_ticker,
    "Both CUSIP AND ticker": ibes_gvkeys_both,
    "CUSIP only (NO ticker fallback)": ibes_gvkeys_cusip_only,
}

for crit_name, allowed_gvkeys in criteria.items():
    h=beta_groups[(beta_groups["HIGH"]==1)&(beta_groups["gvkey"].isin(allowed_gvkeys))]
    l=beta_groups[(beta_groups["LOW"]==1)&(beta_groups["gvkey"].isin(allowed_gvkeys))]
    print(f"\n{crit_name}:")
    print(f"  HIGH: {len(h)}  LOW: {len(l)}  ratio H/L: {len(h)/max(len(l),1):.2f}")
    print(f"  Paper: HIGH=449  LOW=360  ratio=1.25")

# ============================================================
# 5. Analyst count (NUMEST) asymmetry
# ============================================================
print(f"\n{'='*60}")
print("5. Analyst following (NUMEST) by beta tercile")
print("="*60)

# Per firm-quarter NUMEST
ibes_fq=ibes[["CUSIP8","cyq","NUMEST_n","M"]].copy()
ibes_fq=ibes_fq[ibes_fq["NUMEST_n"].notna()]

# Merge to beta groups via CUSIP8
cm_lookup_ibes=cm2[["gvkey","cusip8","cyq"]].drop_duplicates()
ibes_w_gvkey=ibes_fq.merge(cm_lookup_ibes,left_on=["CUSIP8","cyq"],right_on=["cusip8","cyq"],how="inner")
ibes_w_gvkey=ibes_w_gvkey.merge(beta_groups[["gvkey","HIGH","LOW"]],on="gvkey",how="inner")

for label, mask in [("HIGH", ibes_w_gvkey["HIGH"]==1), ("LOW", ibes_w_gvkey["LOW"]==1)]:
    sub=ibes_w_gvkey[mask]
    if len(sub)==0: continue
    print(f"\n{label}:")
    print(f"  Obs: {len(sub):,}")
    print(f"  Mean NUMEST: {sub['NUMEST_n'].mean():.2f}")
    print(f"  Median NUMEST: {sub['NUMEST_n'].median():.2f}")
    print(f"  P25/P75: {sub['NUMEST_n'].quantile(0.25):.1f}/{sub['NUMEST_n'].quantile(0.75):.1f}")
    print(f"  % NUMEST>=3: {(sub['NUMEST_n']>=3).mean()*100:.1f}%")
    print(f"  % NUMEST>=5: {(sub['NUMEST_n']>=5).mean()*100:.1f}%")

# ============================================================
# 6. NUMEST threshold sweep: how does DiD sample split change?
# ============================================================
print(f"\n{'='*60}")
print("6. NUMEST threshold sweep — DiD sample HIGH/LOW counts")
print("="*60)

# For each gvkey, get typical NUMEST (median across quarters)
gvkey_numest=ibes_w_gvkey.groupby("gvkey")["NUMEST_n"].median()

for thresh in [0, 2, 3, 4, 5]:
    gk_covered=set(gvkey_numest[gvkey_numest>=thresh].index)
    h=beta_groups[(beta_groups["HIGH"]==1)&(beta_groups["gvkey"].isin(gk_covered))]
    l=beta_groups[(beta_groups["LOW"]==1)&(beta_groups["gvkey"].isin(gk_covered))]
    # Also check: of those EXCLUDED, what's their HIGH/LOW split?
    h_ex=beta_groups[(beta_groups["HIGH"]==1)&(~beta_groups["gvkey"].isin(gk_covered))]
    l_ex=beta_groups[(beta_groups["LOW"]==1)&(~beta_groups["gvkey"].isin(gk_covered))]
    print(f"  NUMEST >= {thresh}: HIGH={len(h)} LOW={len(l)} (H/L={len(h)/max(len(l),1):.2f})  |  EXCLUDED: HIGH={len(h_ex)} LOW={len(l_ex)}")
    if thresh>0:
        h_drop=len(h_ex)/max(len(h)+len(h_ex),1)*100
        l_drop=len(l_ex)/max(len(l)+len(l_ex),1)*100
        print(f"    Drop rate: HIGH={h_drop:.1f}%  LOW={l_drop:.1f}%")

print(f"\nPaper target: HIGH=449  LOW=360  H/L=1.25")
