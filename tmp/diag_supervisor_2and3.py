"""Supervisor #2 and #3: Jump asymmetry test + blind |RET|>0.25 daily filter."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24
RHO_Q = 0.99

# ------------- Survivor list (same as always) -------------
comp_raw = pd.read_parquet(CSV, columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
for c in ["atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]: comp_raw[c]=pd.to_numeric(comp_raw[c],errors="coerce")
comp_raw["txditcq"]=comp_raw["txditcq"].fillna(0); comp_raw["gvkey"]=comp_raw["gvkey"].astype(str).str.zfill(6)
comp_raw=comp_raw[(comp_raw["fyearq"]>=2010)&(comp_raw["fyearq"]<=2016)]; comp_raw=comp_raw[comp_raw["fqtr"].isin([1,2,3,4])]
comp_raw=comp_raw[(comp_raw["curcdq"]=="USD")&(comp_raw["fic"]=="USA")]; comp_raw=comp_raw[(comp_raw["atq"]>0)&(comp_raw["saleq"]>0)]
csic=pd.to_numeric(comp_raw["sic"],errors="coerce"); comp_raw=comp_raw[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp_raw["mktcap"]=comp_raw["cshoq"]*comp_raw["prccq"]; comp_raw=comp_raw[(comp_raw["atq"]>=10)&(comp_raw["mktcap"]>=10)]
comp_raw["atq_l1"]=comp_raw.groupby("gvkey")["atq"].shift(1); comp_raw["saleq_l4"]=comp_raw.groupby("gvkey")["saleq"].shift(4)
hi=comp_raw["capxy"].notna()&comp_raw["atq_l1"].notna(); hc=comp_raw["oibdpq"].notna()&comp_raw["atq_l1"].notna()
hq=comp_raw["cshoq"].notna()&comp_raw["prccq"].notna()&comp_raw["atq"].notna()&comp_raw["ceqq"].notna()
hs=comp_raw["saleq"].notna()&comp_raw["saleq_l4"].notna()
comp_raw=comp_raw[hi&comp_raw["atq"].notna()&hc&hq&hs]
comp_raw=comp_raw.sort_values(["gvkey","fyearq","fqtr"]); comp_raw["cyq"]=comp_raw["fyearq"].astype(int)*10+comp_raw["fqtr"].astype(int)
rows=[]
for gk,grp in comp_raw.groupby("gvkey"):
    grp=grp.sort_values("cyq"); runs,cur=[],[]
    for _,row in grp.iterrows():
        if not cur: cur=[row.name]
        else:
            pq=grp.loc[cur[-1],"cyq"]; tq=row["cyq"]; exp=pq+1
            if pq%10==4: exp=(pq//10+1)*10+1
            if tq==exp: cur.append(row.name)
            else: runs.append(cur); cur=[row.name]
    runs.append(cur)
    if runs: best=max(runs,key=len)
    if runs and len(best)>=12: rows.append(grp.loc[best])
comp_raw=pd.concat(rows,ignore_index=True)
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f: fic=pd.read_csv(io.BytesIO(f.read()),sep="\t",usecols=["gvkey","year","icode100"])
fic["gvkey"]=fic["gvkey"].astype(str).str.zfill(6); comp_raw["year"]=comp_raw["cyq"]//10
comp_raw=comp_raw.merge(fic,on=["gvkey","year"],how="inner")
survivor_gvkeys=set(comp_raw["gvkey"].unique()); del comp_raw

ccm=pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"]=ccm["gvkey"].astype(str).str.zfill(6); ccm=ccm[ccm["LINKTYPE"].isin(["LU","LC"])]; ccm=ccm[ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"]=pd.to_datetime(ccm["LINKDT"],errors="coerce"); ccm["LINKENDDT"]=pd.to_datetime(ccm["LINKENDDT"],errors="coerce")
ccm["LINKENDDT"]=ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm=ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(ccm["LINKDT"]<=pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"]=pd.to_numeric(ccm["LPERMNO"],errors="coerce").astype("Int64"); ccm=ccm.dropna(subset=["LPERMNO"])
ccm_surv=ccm[ccm["gvkey"].isin(survivor_gvkeys)]; survivor_permnos=set(ccm_surv["LPERMNO"].unique())

# Daily returns - 2010-2014 for beta, 2002-2018 for CF
def load_crsp(y_start, y_end):
    frames=[]
    for y in range(y_start, y_end+1):
        for q in range(1,5):
            f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
            if f.exists():
                df=pd.read_parquet(f)
                df=df[df["PERMNO"].isin(survivor_permnos)]
                if len(df)>0: frames.append(df)
    cr=pd.concat(frames); cr["date"]=pd.to_datetime(cr["date"])
    cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce")
    return cr

cr_beta=load_crsp(2010, 2014)

# Macro vol
sp=cr_beta[["date","sprtrn"]].drop_duplicates()
sp["ym"]=sp["date"].dt.to_period("M")
sp500=sp.groupby("ym")["sprtrn"].std()
sp500=sp500[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp500.columns=["ym","vol_SP500"]; sp500["ym_str"]=sp500["ym"].astype(str)

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")]
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M")
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
ftv.columns=["ym","vol_FTSE100"]; ftv["ym_str"]=ftv["ym"].astype(str)

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")]
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M")
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
fxv.columns=["ym","vol_FX"]; fxv["ym_str"]=fxv["ym"].astype(str)

macro=sp500[["ym_str","vol_SP500"]].merge(ftv[["ym_str","vol_FTSE100"]],on="ym_str").merge(fxv[["ym_str","vol_FX"]],on="ym_str")

def build_firm_vol(ret_df, jump_filter=None):
    """Build monthly firm vol from daily returns, optionally filtering jumps."""
    r=ret_df.copy()
    if jump_filter is not None:
        r["RET"]=r["RET"].where(r["RET"].abs()<=jump_filter)
    r["ym"]=r["date"].dt.to_period("M").astype(str)
    g=r.groupby(["PERMNO","ym"])
    vol=g["RET"].std()
    vol=vol[g["RET"].count()>=MIN_DAYS].reset_index()
    vol.columns=["PERMNO","ym","vol_r"]
    return vol

def estimate_betas(firm_vol):
    """Run eq(13) firm-by-firm OLS. Return beta DataFrame."""
    mg=firm_vol.merge(macro,left_on="ym",right_on="ym_str",how="inner")
    res=[]
    for pn,grp in mg.groupby("PERMNO"):
        grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
        if len(grp)<MIN_MONTHS: continue
        yv=grp["vol_r"].values
        X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
        try:
            b=np.linalg.lstsq(X,yv,rcond=None)[0]; yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
            res.append({"PERMNO":pn,"beta_uk":b[1],"beta_sp":b[2],"n":len(grp),
                        "r2":1-ssr/sst if sst>0 else 0})
        except: continue
    betas=pd.DataFrame(res).merge(ccm_surv[["gvkey","LPERMNO"]].drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
    betas=betas.drop_duplicates(subset=["gvkey"],keep="first")
    return betas

def report_beta_stats(betas, label):
    bpos=betas[betas["beta_uk"]>=0]; bneg=betas[betas["beta_uk"]<0]
    neg_pct=len(bneg)/len(betas)*100
    if len(bpos)>=3:
        t1,t2=bpos["beta_uk"].quantile(1/3),bpos["beta_uk"].quantile(2/3)
        hi=(betas["beta_uk"]>=t2).sum(); lo=((betas["beta_uk"]>=0)&(betas["beta_uk"]<=t1)).sum()
    else: t1,t2,hi,lo=np.nan,np.nan,0,0
    print(f"\n{label}:")
    print(f"  N={len(betas):,}  Neg={len(bneg):,} ({neg_pct:.1f}%)  Nonneg={len(bpos):,}")
    print(f"  Cutpoints: T1={t1:.4f} T2={t2:.4f}  HIGH={hi:,} LOW={lo:,}")
    print(f"  Median beta: {betas['beta_uk'].median():.4f}")
    return {"n":len(betas),"neg_pct":neg_pct,"t1":t1,"t2":t2,"hi":hi,"lo":lo,"median":betas["beta_uk"].median()}

# =====================================================
# #2: Asymmetry test — jumpy vs non-jumpy
# =====================================================
print("="*60)
print("#2: Asymmetry test — jumpy vs non-jumpy firms")
print("="*60)

fv_no_filter=build_firm_vol(cr_beta)
firm_max_vol=fv_no_filter.groupby("PERMNO")["vol_r"].max()
jumpy_perms=set(firm_max_vol[firm_max_vol>0.10].index)
nonjumpy_perms=set(firm_max_vol[firm_max_vol<=0.10].index)
print(f"Jumpy firms (>=1 month >0.10): {len(jumpy_perms)}")
print(f"Non-jumpy firms: {len(nonjumpy_perms)}")

# Betas on full pooled data
betas_all=estimate_betas(fv_no_filter)

# Split betas
betas_all_pn=betas_all.set_index("PERMNO")
b_jumpy=betas_all_pn[betas_all_pn.index.isin(jumpy_perms)].reset_index()
b_nonjumpy=betas_all_pn[betas_all_pn.index.isin(nonjumpy_perms)].reset_index()

print(f"\n--- ALL FIRMS (baseline) ---")
report_beta_stats(betas_all, "ALL")
print(f"\n--- JUMPY firms (>=1 month vol>0.10) ---")
report_beta_stats(b_jumpy, "JUMPY")
print(f"\n--- NON-JUMPY firms ---")
report_beta_stats(b_nonjumpy, "NON-JUMPY")

# =====================================================
# #3: Blind |RET|>0.25 daily filter
# =====================================================
print(f"\n{'='*60}")
print("#3: Blind |RET|>0.25 daily jump filter")
print("="*60)

fv_filtered=build_firm_vol(cr_beta, jump_filter=0.25)
betas_filtered=estimate_betas(fv_filtered)

# Firm counts
n_firms_before=fv_no_filter["PERMNO"].nunique()
n_firms_after=fv_filtered["PERMNO"].nunique()
n_months_before=len(fv_no_filter)
n_months_after=len(fv_filtered)

print(f"\nPanel dimensions BEFORE filter:")
print(f"  Firms: {n_firms_before:,}  Firm-months: {n_months_before:,}")
print(f"Panel dimensions AFTER filter:")
print(f"  Firms: {n_firms_after:,}  Firm-months: {n_months_after:,}")
print(f"  Firms lost: {n_firms_before-n_firms_after}")
print(f"  Firm-months lost: {n_months_before-n_months_after}")

print(f"\n--- BEFORE filter (baseline) ---")
bs_before=report_beta_stats(betas_all, "BEFORE")
print(f"\n--- AFTER |RET|>0.25 filter ---")
bs_after=report_beta_stats(betas_filtered, "AFTER")

# =====================================================
# #3: CF-beta rank correlation (before vs after)
# =====================================================
print(f"\n{'='*60}")
print("#3-CF: CF-beta rank correlation (before vs after filter)")
print("="*60)

# CF beta: re-use the methodology from build_beta_cf_v2.py
# Quarterly data 2002-2018 for CF decomposition
comp_q=pd.read_parquet(CSV,columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","oibdpq","cshoq","prccq","ceqq","txditcq"])
for c in ["atq","oibdpq","cshoq","prccq","ceqq","txditcq"]: comp_q[c]=pd.to_numeric(comp_q[c],errors="coerce")
comp_q["txditcq"]=comp_q["txditcq"].fillna(0); comp_q["gvkey"]=comp_q["gvkey"].astype(str).str.zfill(6)
comp_q=comp_q[(comp_q["fyearq"]>=2001)&(comp_q["fyearq"]<=2018)]; comp_q=comp_q[comp_q["fqtr"].isin([1,2,3,4])]
comp_q=comp_q[(comp_q["curcdq"]=="USD")&(comp_q["fic"]=="USA")]; comp_q=comp_q[(comp_q["atq"]>0)]
comp_q["yq"]=comp_q["fyearq"].astype(int)*10+comp_q["fqtr"].astype(int); comp_q=comp_q.sort_values(["gvkey","yq"])
comp_q["be"]=comp_q["ceqq"]+comp_q["txditcq"]; comp_q["be_lag"]=comp_q.groupby("gvkey")["be"].shift(1)
comp_q["roe"]=comp_q["oibdpq"]/comp_q["be_lag"]; comp_q["roe"]=comp_q["roe"].clip(-1,1)
comp_q["mktcap"]=comp_q["cshoq"]*comp_q["prccq"]; comp_q["bm"]=comp_q["be"]/comp_q["mktcap"]; comp_q["bm"]=comp_q["bm"].clip(1e-6,100)
comp_q["roe_log"]=np.log(1+comp_q["roe"].clip(-0.99,10)); comp_q["bm_log"]=np.log(comp_q["bm"])
comp_qv=comp_q[["gvkey","yq","roe_log","bm_log"]].dropna()

cr_q=load_crsp(2002,2018)
cr_q["yq"]=cr_q["date"].dt.year*10+cr_q["date"].dt.quarter; cr_q["lr"]=np.log(1+cr_q["RET"].fillna(0))
qr=cr_q.groupby(["PERMNO","yq"])["lr"].sum().reset_index(); qr.columns=["PERMNO","yq","r_q"]
qr=qr.merge(ccm_surv[["gvkey","LPERMNO"]].drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
qr=qr.drop_duplicates(subset=["gvkey","yq"],keep="first"); qr["gvkey"]=qr["gvkey"].astype(str).str.zfill(6)

qdf=comp_qv.merge(qr[["gvkey","yq","r_q"]],on=["gvkey","yq"],how="inner")
qdf=qdf.sort_values(["gvkey","yq"])

# CF news extraction (same as build_beta_cf_v2.py)
results_cf=[]; n_var=0; MIN_Q=30
for gk,grp in qdf.groupby("gvkey"):
    grp=grp.sort_values("yq"); Z=grp[["r_q","roe_log","bm_log"]].values
    if len(Z)<MIN_Q: continue
    Z_lag=Z[:-1]; Z_lead=Z[1:]
    try: Gamma=np.linalg.lstsq(Z_lag,Z_lead,rcond=None)[0].T
    except: continue
    eigvals=np.linalg.eigvals(Gamma)
    if np.max(np.abs(eigvals))>=0.999: continue
    try: inv_term=np.linalg.inv(np.eye(3)-RHO_Q*Gamma)
    except: continue
    e1=np.array([1.0,0.0,0.0]); cf_coeff=e1@inv_term; U=Z[1:]-(Gamma@Z[:-1].T).T; cf_news_q=U@cf_coeff
    for t_idx,cf_val in enumerate(cf_news_q):
        yq=grp["yq"].iloc[t_idx+1]; yr,qq=yq//10,yq%10; ms=(qq-1)*3+1
        for m in range(ms,ms+3):
            results_cf.append({"gvkey":gk,"ym":f"{yr}-{m:02d}","cf_news":cf_val})
    n_var+=1

cf_df=pd.DataFrame(results_cf); cf_df["vol_cf"]=np.abs(cf_df["cf_news"])
cf_monthly=cf_df.groupby(["gvkey","ym"])["vol_cf"].mean().reset_index()
print(f"CF VAR firms: {n_var:,}")

# CF betas - BEFORE
cf_data=cf_monthly.merge(macro,left_on="ym",right_on="ym_str",how="inner")
cf_data=cf_data[(cf_data["ym"]>="2010-01")&(cf_data["ym"]<="2014-12")]
cf_betas=[]
for gk,grp in cf_data.groupby("gvkey"):
    grp=grp.dropna(subset=["vol_cf","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_cf"].values; X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try:
        b=np.linalg.lstsq(X,yv,rcond=None)[0]; yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
        cf_betas.append({"gvkey":gk,"beta_cf":b[1],"n":len(grp),"r2":1-ssr/sst if sst>0 else 0})
    except: continue
betas_cf=pd.DataFrame(cf_betas)

# CF vs Level comparison — BEFORE
def cf_compare(level_b, cf_b, label):
    common=set(level_b["gvkey"])&set(cf_b["gvkey"])
    if len(common)<20:
        print(f"  {label}: Too few common firms ({len(common)})")
        return {"rank_corr":np.nan,"overlap":np.nan}
    bl=level_b[level_b["gvkey"].isin(common)].set_index("gvkey")["beta_uk"]
    bc=cf_b[cf_b["gvkey"].isin(common)].set_index("gvkey")["beta_cf"]
    rc=bl.rank().corr(bc.rank())
    bl_pos=bl[bl>=0]; bc_pos=bc[bc>=0]
    if len(bl_pos)<3 or len(bc_pos)<3:
        return {"rank_corr":rc,"overlap":np.nan}
    t2l=bl_pos.quantile(2/3); t2c=bc_pos.quantile(2/3)
    hl=set(bl_pos[bl_pos>=t2l].index); hc=set(bc_pos[bc_pos>=t2c].index)
    overlap=len(hl&hc)/max(len(hl|hc),1)
    print(f"  {label}: rank_corr={rc:.4f}, top-tercile overlap={overlap:.3f} ({overlap*100:.1f}%), common={len(common):,}")
    return {"rank_corr":rc,"overlap":overlap,"common":len(common)}

print(f"\n--- CF-beta rank correlation: BEFORE ---")
cf_compare(betas_all, betas_cf, "BEFORE")

print(f"\n--- CF-beta rank correlation: AFTER |RET|>0.25 ---")
cf_compare(betas_filtered, betas_cf, "AFTER")

print(f"\nPaper: rank_corr=0.80, top-tercile overlap=0.86")
print(f"\nGATE: CF-correlation MUST move toward 0.80 for jump filter to be correct.")
