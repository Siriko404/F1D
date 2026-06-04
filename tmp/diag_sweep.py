"""Sensitivity sweep: min-months, min-days for beta estimation."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"

# 1. Build vol data once (firm + macro), then sweep regression params
# --- Compustat survivors (same as always) ---
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
comp_raw=pd.concat(res_rows,ignore_index=True) if res_rows else pd.DataFrame()
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f: fic=pd.read_csv(io.BytesIO(f.read()),sep="\t",usecols=["gvkey","year","icode100"])
fic["gvkey"]=fic["gvkey"].astype(str).str.zfill(6); comp_raw["year"]=comp_raw["cal_yr_qtr"]//10
comp_raw=comp_raw.merge(fic,on=["gvkey","year"],how="inner")
survivor_gvkeys=set(comp_raw["gvkey"].unique()); del comp_raw

ccm=pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"]=ccm["gvkey"].astype(str).str.zfill(6); ccm=ccm[ccm["LINKTYPE"].isin(["LU","LC"])]; ccm=ccm[ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"]=pd.to_datetime(ccm["LINKDT"],errors="coerce"); ccm["LINKENDDT"]=pd.to_datetime(ccm["LINKENDDT"],errors="coerce")
ccm["LINKENDDT"]=ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm=ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(ccm["LINKDT"]<=pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"]=pd.to_numeric(ccm["LPERMNO"],errors="coerce").astype("Int64"); ccm=ccm.dropna(subset=["LPERMNO"])
ccm_surv=ccm[ccm["gvkey"].isin(survivor_gvkeys)]; survivor_permnos=set(ccm_surv["LPERMNO"].unique())

# 2. Build raw daily CRSP vol data (firm-level, minimum filtering done per-sweep)
# Store all firm-daily data for survivors, plus macro series
frames_ret=[]
for y in range(2010,2015):
    for q in range(1,5):
        f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df=pd.read_parquet(f,columns=["PERMNO","date","RET","sprtrn"])
            df=df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames_ret.append(df)
cr=pd.concat(frames_ret,ignore_index=True); cr["date"]=pd.to_datetime(cr["date"])
cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce"); cr["sprtrn"]=pd.to_numeric(cr["sprtrn"],errors="coerce")
cr["ym"]=cr["date"].dt.to_period("M")

# Macro vol series (these are NOT affected by min-days sweep for firm data; use standard >=15)
sp=cr[["date","sprtrn","ym"]].drop_duplicates(); spg=sp.groupby("ym")
sp500=spg["sprtrn"].std(); sp500=sp500[spg["sprtrn"].count()>=15].reset_index(); sp500.columns=["ym","vol_SP500"]

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M")
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=15].reset_index(); ftv.columns=["ym","vol_FTSE100"]

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M")
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=15].reset_index(); fxv.columns=["ym","vol_FX"]

macro=sp500.merge(ftv,on="ym").merge(fxv,on="ym")

# 3. Sweep function
def run_beta(firm_vol, min_months):
    """Given firm monthly vol data, run OLS per firm with >=min_months"""
    firm_vol["ym"]=firm_vol["ym"].astype(str); macro["ym"]=macro["ym"].astype(str)
    mg=firm_vol.merge(macro,on="ym",how="inner")
    res=[]
    for pn,grp in mg.groupby("PERMNO"):
        grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
        if len(grp)<min_months: continue
        yv=grp["vol_r"].values; X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
        try:
            b=np.linalg.lstsq(X,yv,rcond=None)[0]; yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
            res.append({"PERMNO":pn,"beta_uk":b[1],"n":len(grp),"r2":1-ssr/sst if sst>0 else 0})
        except: continue
    betas=pd.DataFrame(res)
    betas=betas.merge(ccm_surv[["gvkey","LPERMNO"]].drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
    betas=betas.drop_duplicates(subset=["gvkey"],keep="first")
    bpos=betas[betas["beta_uk"]>=0]; t1,t2=bpos["beta_uk"].quantile(1/3),bpos["beta_uk"].quantile(2/3)
    return {"n_total":len(betas),"n_nonneg":len(bpos),"n_neg":len(betas[betas["beta_uk"]<0]),
            "t1":t1,"t2":t2,"high":(betas["beta_uk"]>=t2).sum(),"low":((betas["beta_uk"]>=0)&(betas["beta_uk"]<=t1)).sum()}

# Build firm vol at different min_days thresholds
from collections import defaultdict
firm_vols = defaultdict(dict)
for md in [10, 13, 15, 17, 20]:
    g=cr.groupby(["PERMNO","ym"])
    rv=g["RET"].std(); rv=rv[g["RET"].count()>=md].reset_index()
    rv.columns=["PERMNO","ym","vol_r"]
    # Also filter macro consistently (macro already uses >=15, keep as is)
    firm_vols[md] = rv

print(f"{'MinDays':<10} {'MinMon':<10} {'Total':>8} {'Nonneg':>8} {'Neg':>8} {'T1':>8} {'T2':>8} {'HIGH':>8} {'LOW':>8}")
print("-"*90)
for md in [10, 13, 15, 17, 20]:
    for mm in [12, 18, 24, 30, 36]:
        r = run_beta(firm_vols[md], mm)
        print(f"{md:<10} {mm:<10} {r['n_total']:>8,} {r['n_nonneg']:>8,} {r['n_neg']:>8,} {r['t1']:>8.4f} {r['t2']:>8.4f} {r['high']:>8,} {r['low']:>8,}")
    print()
