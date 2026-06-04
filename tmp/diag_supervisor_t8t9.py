"""Supervisor Tasks 8+9: n_obs distribution of precise negatives + min-months sweep → CF-correlation + cutpoint stability."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24
RHO_Q = 0.99

# ============================================================
# 1. COMPUSTAT SURVIVOR LIST
# ============================================================
print("1. Compustat survivors")
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

# ============================================================
# 2. CCM — P-only, date-resolved
# ============================================================
ccm_raw=pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
    columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm_raw["gvkey"]=ccm_raw["gvkey"].astype(str).str.zfill(6)
ccm_raw=ccm_raw[ccm_raw["gvkey"].isin(survivor_gvkeys)]
ccm=ccm_raw.copy()
ccm=ccm[ccm["LINKTYPE"].isin(["LU","LC"])]; ccm=ccm[ccm["LINKPRIM"]=="P"]
ccm["LINKDT"]=pd.to_datetime(ccm["LINKDT"],errors="coerce"); ccm["LINKENDDT"]=pd.to_datetime(ccm["LINKENDDT"],errors="coerce")
ccm["LINKENDDT"]=ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm=ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(ccm["LINKDT"]<=pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"]=pd.to_numeric(ccm["LPERMNO"],errors="coerce").astype("Int64"); ccm=ccm.dropna(subset=["LPERMNO"])
resolved=[]
for gk,grp in ccm.groupby("gvkey"):
    if len(grp)==1: resolved.append(grp.iloc[0])
    else:
        best_overlap=-1; best_row=None
        for _,row in grp.iterrows():
            start=max(row["LINKDT"],pd.Timestamp("2010-01-01"))
            end=min(row["LINKENDDT"],pd.Timestamp("2014-12-31"))
            overlap=(end-start).days
            if overlap>best_overlap: best_overlap=overlap; best_row=row
        resolved.append(best_row)
ccm=pd.DataFrame(resolved)
survivor_permnos=set(ccm["LPERMNO"].unique())

# ============================================================
# 3. DAILY RETURNS + MACRO VOL + FIRM VOL + BETAS
# ============================================================
print("3. Building betas")
frames=[]
for y in range(2010,2015):
    for q in range(1,5):
        f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df=pd.read_parquet(f,columns=["PERMNO","date","RET","sprtrn"])
            df=df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames.append(df)
cr=pd.concat(frames,ignore_index=True); cr["date"]=pd.to_datetime(cr["date"])
cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce"); cr["sprtrn"]=pd.to_numeric(cr["sprtrn"],errors="coerce")
cr["ym"]=cr["date"].dt.to_period("M").astype(str)

sp=cr[["date","sprtrn"]].drop_duplicates(); sp["ym"]=sp["date"].dt.to_period("M").astype(str)
sp_m=sp.groupby("ym")["sprtrn"].std(); sp_m=sp_m[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp_m.columns=["ym","vol_SP500"]

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M").astype(str)
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
ftv.columns=["ym","vol_FTSE100"]

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M").astype(str)
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
fxv.columns=["ym","vol_FX"]

macro=sp_m.merge(ftv,on="ym").merge(fxv,on="ym")

g=cr.groupby(["PERMNO","ym"]); fv=g["RET"].std(); fv=fv[g["RET"].count()>=MIN_DAYS].reset_index()
fv.columns=["PERMNO","ym","vol_r"]

mg=fv.merge(macro,on="ym",how="inner")
res=[]
for pn,grp in mg.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
    n=len(grp)
    yv=grp["vol_r"].values
    X=np.column_stack([np.ones(n),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try:
        b,resid,rank,sing=np.linalg.lstsq(X,yv,rcond=None)
        yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
        r2=1-ssr/sst if sst>0 else 0
        sigma2=ssr/(n-4) if n>4 else np.nan
        XtX_inv=np.linalg.inv(X.T@X)
        se=np.sqrt(sigma2*XtX_inv[1,1])
        t_stat=b[1]/se if se>0 else np.nan
        # Condition number of design matrix (excluding intercept)
        Xc=X[:,1:]-X[:,1:].mean(axis=0)
        cond_num=np.linalg.cond(Xc) if n>4 else np.inf
        res.append({"PERMNO":pn,"beta_uk":b[1],"beta_sp":b[2],"beta_fx":b[3],
                    "n_obs":n,"r2":r2,"t_stat":t_stat,"se":se,"cond_num":cond_num})
    except: continue

betas=pd.DataFrame(res)
betas=betas.merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
betas=betas.drop_duplicates(subset=["gvkey"],keep="first")
betas["abs_t"]=betas["t_stat"].abs()

# ============================================================
# TASK 8: n_obs distribution of precise negatives
# ============================================================
print(f"\n{'='*60}")
print("TASK 8: n_obs distribution of precise negatives (|t|>=1, beta<0)")
print(f"{'='*60}")

precise_neg = betas[(betas["beta_uk"]<0) & (betas["abs_t"]>=1)]
nobs_pn = precise_neg["n_obs"]
print(f"  N = {len(precise_neg):,}")
print(f"  n_obs: min={nobs_pn.min():.0f} p10={nobs_pn.quantile(0.1):.0f} p25={nobs_pn.quantile(0.25):.0f} p50={nobs_pn.median():.0f} p75={nobs_pn.quantile(0.75):.0f} p90={nobs_pn.quantile(0.9):.0f} max={nobs_pn.max():.0f}")

# How many fail each K?
for K in [36, 48, 54, 60]:
    fail = (nobs_pn < K).sum()
    print(f"    n<{K}: {fail:,} ({fail/len(precise_neg)*100:.1f}%)")

# n_obs distribution of ALL firms vs precise negatives
print(f"\n  n_obs distribution — ALL firms:")
all_n = betas["n_obs"]
print(f"    min={all_n.min():.0f} p10={all_n.quantile(0.1):.0f} p25={all_n.quantile(0.25):.0f} p50={all_n.median():.0f} p75={all_n.quantile(0.75):.0f} p90={all_n.quantile(0.9):.0f} max={all_n.max():.0f}")

print(f"\n  n_obs distribution — PRECISE NEGATIVES:")
print(f"    min={nobs_pn.min():.0f} p10={nobs_pn.quantile(0.1):.0f} p25={nobs_pn.quantile(0.25):.0f} p50={nobs_pn.median():.0f} p75={nobs_pn.quantile(0.75):.0f} p90={nobs_pn.quantile(0.9):.0f} max={nobs_pn.max():.0f}")

# ============================================================
# CF PIPELINE (run once, shared across all K)
# ============================================================
print(f"\n{'='*60}")
print("Building CF betas...")
print(f"{'='*60}")

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

frames_q=[]
for y in range(2002,2019):
    for q in range(1,5):
        f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df=pd.read_parquet(f,columns=["PERMNO","date","RET"])
            df=df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames_q.append(df)
cr_q=pd.concat(frames_q); cr_q["date"]=pd.to_datetime(cr_q["date"])
cr_q["RET"]=pd.to_numeric(cr_q["RET"],errors="coerce")
cr_q["yq"]=cr_q["date"].dt.year*10+cr_q["date"].dt.quarter
cr_q["lr"]=np.log(1+cr_q["RET"].fillna(0))
qr=cr_q.groupby(["PERMNO","yq"])["lr"].sum().reset_index()
qr.columns=["PERMNO","yq","r_q"]
qr=qr.merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
qr=qr.drop_duplicates(subset=["gvkey","yq"],keep="first"); qr["gvkey"]=qr["gvkey"].astype(str).str.zfill(6)

qdf=comp_qv.merge(qr[["gvkey","yq","r_q"]],on=["gvkey","yq"],how="inner")
qdf=qdf.sort_values(["gvkey","yq"])

results_cf=[]; MIN_Q=30
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

cf_df=pd.DataFrame(results_cf); cf_df["vol_cf"]=np.abs(cf_df["cf_news"])
cf_monthly=cf_df.groupby(["gvkey","ym"])["vol_cf"].mean().reset_index()

cf_data=cf_monthly.merge(macro[["ym","vol_FTSE100","vol_SP500","vol_FX"]],on="ym",how="inner")
cf_data=cf_data[(cf_data["ym"]>="2010-01")&(cf_data["ym"]<="2014-12")]
cf_betas_dict={}
for gk,grp in cf_data.groupby("gvkey"):
    grp=grp.dropna(subset=["vol_cf","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_cf"].values
    X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try: b=np.linalg.lstsq(X,yv,rcond=None)[0]; cf_betas_dict[gk]=b[1]
    except: continue
betas_cf=pd.DataFrame(list(cf_betas_dict.items()),columns=["gvkey","beta_cf"])
print(f"  CF betas: {len(betas_cf):,} firms")

# ============================================================
# TASK 9: MIN-MONTHS K-SWEEP
# ============================================================
print(f"\n{'='*60}")
print("TASK 9: Min-months K-sweep → CF-correlation + cutpoint stability")
print(f"{'='*60}")

def tercile_stats(bt):
    bp=bt[bt["beta_uk"]>=0]; bn=bt[bt["beta_uk"]<0]
    neg_pct=len(bn)/len(bt)*100
    if len(bp)>=3:
        t1,t2=bp["beta_uk"].quantile(1/3),bp["beta_uk"].quantile(2/3)
        hi=(bt["beta_uk"]>=t2).sum(); lo=((bt["beta_uk"]>=0)&(bt["beta_uk"]<=t1)).sum()
    else: t1,t2,hi,lo=np.nan,np.nan,0,0
    return len(bt),neg_pct,t1,t2,hi,lo

def cf_rank(bt):
    common=set(bt["gvkey"])&set(betas_cf["gvkey"])
    if len(common)<30: return np.nan, np.nan, len(common)
    bl=bt[bt["gvkey"].isin(common)].set_index("gvkey")["beta_uk"]
    bc=betas_cf[betas_cf["gvkey"].isin(common)].set_index("gvkey")["beta_cf"]
    rc=bl.rank().corr(bc.rank())
    bl_p=bl[bl>=0]; bc_p=bc[bc>=0]
    if len(bl_p)<3 or len(bc_p)<3: return rc, np.nan, len(common)
    t2l=bl_p.quantile(2/3); t2c=bc_p.quantile(2/3)
    hl=set(bl_p[bl_p>=t2l].index); hc=set(bc_p[bc_p>=t2c].index)
    overlap=len(hl&hc)/max(len(hl|hc),1)
    return rc, overlap, len(common)

# Baseline
n_base,neg_base,t1_base,t2_base,hi_base,lo_base = tercile_stats(betas)
rc_base,ov_base,cm_base = cf_rank(betas)

print(f"  {'K':>4} {'N':>6} {'Neg%':>7} {'T1':>7} {'T2':>7} {'H':>5} {'L':>5} {'CF_rank':>9} {'CF_ovlp':>9} {'Comm':>5} {'dT2':>7}")
print(f"  {'-'*4} {'-'*6} {'-'*7} {'-'*7} {'-'*7} {'-'*5} {'-'*5} {'-'*9} {'-'*9} {'-'*5} {'-'*7}")

for K_label, K in [("BASE", 24), ("36", 36), ("42", 42), ("48", 48), ("54", 54), ("57", 57), ("60", 60)]:
    if K_label == "BASE":
        n,nn,t1,t2,hi,lo = n_base,neg_base,t1_base,t2_base,hi_base,lo_base
        rc,ov,cm = rc_base,ov_base,cm_base
    else:
        keep = betas[betas["n_obs"] >= K]
        n,nn,t1,t2,hi,lo = tercile_stats(keep)
        rc,ov,cm = cf_rank(keep)
    dt2 = t2 - t2_base
    print(f"  {K_label:>4} {n:>6} {nn:>6.1f}% {t1:>7.4f} {t2:>7.4f} {hi:>5} {lo:>5} {rc:>9.4f} {ov:>9.3f} {cm:>5} {dt2:>+7.4f}")

print(f"\n  Paper: N~1,428  Neg<=20%  T1=0.28  T2=0.68  H=449 L=360  CF=0.80")

# Also show the nonnegative pool size at each K
print(f"\n  Nonnegative pool sizes:")
for K in [24, 36, 42, 48, 54, 57, 60]:
    keep = betas[betas["n_obs"] >= K]
    npos = (keep["beta_uk"]>=0).sum()
    print(f"    K={K}: nonneg={npos:,}  (paper implied: 1,214)")

# Show what happens to PERMNO 13643 at each K
icpt = betas[betas["PERMNO"]==13643]
if len(icpt) > 0:
    icpt_n = icpt.iloc[0]["n_obs"]
    icpt_b = icpt.iloc[0]["beta_uk"]
    icpt_t = icpt.iloc[0]["t_stat"]
    print(f"\n  PERMNO 13643: n_obs={icpt_n:.0f}  beta_uk={icpt_b:.4f}  t_stat={icpt_t:.2f}")
    print(f"    Would be killed by K >= {icpt_n+1:.0f}")
