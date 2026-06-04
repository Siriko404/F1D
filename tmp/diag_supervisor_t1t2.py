"""Supervisor Tasks 1+2: t-stat/R2 distribution + weekly vol beta estimation."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS_M, MIN_MONTHS = 15, 24
MIN_DAYS_W = 3   # >=3 trading days per week
MIN_WEEKS = 104  # ~2 years of weeks (comparable to 24 months)
RHO_Q = 0.99

# ============================================================
# 1. COMPUSTAT SURVIVOR LIST
# ============================================================
print("1. Compustat survivor list")
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
print(f"  Survivor gvkeys: {len(survivor_gvkeys):,}")

# ============================================================
# 2. CCM — P-only, date-resolved (fixed)
# ============================================================
print("2. CCM (P-only, date-resolved)")
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
# Date-range resolution for multi-PERMNO
resolved=[]
for gk,grp in ccm.groupby("gvkey"):
    if len(grp)==1:
        resolved.append(grp.iloc[0])
    else:
        best_overlap=-1; best_row=None
        for _,row in grp.iterrows():
            start=max(row["LINKDT"],pd.Timestamp("2010-01-01"))
            end=min(row["LINKENDDT"],pd.Timestamp("2014-12-31"))
            overlap=(end-start).days
            if overlap>best_overlap: best_overlap=overlap; best_row=row
        resolved.append(best_row)
ccm=pd.DataFrame(resolved)
max_nu=ccm.groupby("gvkey")["LPERMNO"].nunique().max()
survivor_permnos=set(ccm["LPERMNO"].unique())
print(f"  GVKEYs: {len(ccm):,}  PERMNOs: {len(survivor_permnos):,}  max PERMNO/GVKEY: {max_nu}")

# ============================================================
# 3. LOAD DAILY RETURNS (2010-2014)
# ============================================================
print("3. Daily returns")
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
print(f"  {len(cr):,} obs, {cr['PERMNO'].nunique():,} PERMNOs")

# ISO week (use isocalendar year+week for proper week boundaries)
cr["iso_year"]=cr["date"].dt.isocalendar().year.astype(int)
cr["iso_week"]=cr["date"].dt.isocalendar().week.astype(int)
cr["week_id"]=cr["iso_year"].astype(str)+"-W"+cr["iso_week"].astype(str).str.zfill(2)
cr["ym"]=cr["date"].dt.to_period("M").astype(str)

# ============================================================
# 4. MACRO VOL — monthly + weekly
# ============================================================
print("4. Macro vol (monthly + weekly)")

# SP500
sp=cr[["date","sprtrn"]].drop_duplicates()
sp["ym"]=sp["date"].dt.to_period("M").astype(str)
sp["iso_year"]=sp["date"].dt.isocalendar().year.astype(int)
sp["iso_week"]=sp["date"].dt.isocalendar().week.astype(int)
sp["week_id"]=sp["iso_year"].astype(str)+"-W"+sp["iso_week"].astype(str).str.zfill(2)

# Monthly SP500 vol
sp_m=sp.groupby("ym")["sprtrn"].std()
sp_m=sp_m[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS_M].reset_index()
sp_m.columns=["ym","vol_SP500"]

# Weekly SP500 vol
sp_w=sp.groupby("week_id")["sprtrn"].std()
sp_w=sp_w[sp.groupby("week_id")["sprtrn"].count()>=MIN_DAYS_W].reset_index()
sp_w.columns=["week_id","vol_SP500_w"]

# FTSE
ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1))
ftse["ym"]=ftse["Date"].dt.to_period("M").astype(str)
ftse["iso_year"]=ftse["Date"].dt.isocalendar().year.astype(int)
ftse["iso_week"]=ftse["Date"].dt.isocalendar().week.astype(int)
ftse["week_id"]=ftse["iso_year"].astype(str)+"-W"+ftse["iso_week"].astype(str).str.zfill(2)

ftv_m=ftse.groupby("ym")["lr"].std()
ftv_m=ftv_m[ftse.groupby("ym")["lr"].count()>=MIN_DAYS_M].reset_index()
ftv_m.columns=["ym","vol_FTSE100"]

ftv_w=ftse.groupby("week_id")["lr"].std()
ftv_w=ftv_w[ftse.groupby("week_id")["lr"].count()>=MIN_DAYS_W].reset_index()
ftv_w.columns=["week_id","vol_FTSE100_w"]

# FX
fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1))
fx["ym"]=fx["DATE"].dt.to_period("M").astype(str)
fx["iso_year"]=fx["DATE"].dt.isocalendar().year.astype(int)
fx["iso_week"]=fx["DATE"].dt.isocalendar().week.astype(int)
fx["week_id"]=fx["iso_year"].astype(str)+"-W"+fx["iso_week"].astype(str).str.zfill(2)

fxv_m=fx.groupby("ym")["lr"].std()
fxv_m=fxv_m[fx.groupby("ym")["lr"].count()>=MIN_DAYS_M].reset_index()
fxv_m.columns=["ym","vol_FX"]

fxv_w=fx.groupby("week_id")["lr"].std()
fxv_w=fxv_w[fx.groupby("week_id")["lr"].count()>=MIN_DAYS_W].reset_index()
fxv_w.columns=["week_id","vol_FX_w"]

macro_m=sp_m.merge(ftv_m,on="ym").merge(fxv_m,on="ym")
macro_w=sp_w.merge(ftv_w,on="week_id").merge(fxv_w,on="week_id")
print(f"  Monthly macro: {len(macro_m)} months")
print(f"  Weekly macro:  {len(macro_w)} weeks")

# ============================================================
# TASK 1: t-stat / R2 distribution (MONTHLY, current method)
# ============================================================
print(f"\n{'='*60}")
print("TASK 1: Monthly beta t-stats and R2 distribution")
print(f"{'='*60}")

# Firm monthly vol
g_m=cr.groupby(["PERMNO","ym"])
fv_m=g_m["RET"].std()
fv_m=fv_m[g_m["RET"].count()>=MIN_DAYS_M].reset_index()
fv_m.columns=["PERMNO","ym","vol_r"]

mg_m=fv_m.merge(macro_m,on="ym",how="inner")

res_m=[]
for pn,grp in mg_m.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_r"].values; n=len(yv)
    X=np.column_stack([np.ones(n),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try:
        b,resid,rank,sing=np.linalg.lstsq(X,yv,rcond=None)
        yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
        r2=1-ssr/sst if sst>0 else 0
        # OLS SE: sigma2 * inv(X'X), then SE = sqrt(diag)
        sigma2=ssr/(n-4) if n>4 else np.nan
        XtX_inv=np.linalg.inv(X.T@X)
        se_beta=np.sqrt(sigma2*XtX_inv[1,1])  # FTSE coef is index 1
        t_stat=b[1]/se_beta if se_beta>0 else np.nan
        res_m.append({"PERMNO":pn,"beta_uk":b[1],"n":n,"r2":r2,"t_stat":t_stat,"se":se_beta})
    except: continue

betas_m=pd.DataFrame(res_m)
betas_m=betas_m.merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
betas_m=betas_m.drop_duplicates(subset=["gvkey"],keep="first")

t_stats=betas_m["t_stat"].dropna()
r2s=betas_m["r2"].dropna()
abs_t=betas_m["t_stat"].abs().dropna()
frac_lt1=(abs_t<1).mean()

print(f"  N firms: {len(betas_m):,}")
print(f"  t-stat p10={t_stats.quantile(0.1):.3f} p25={t_stats.quantile(0.25):.3f} p50={t_stats.quantile(0.5):.3f} p75={t_stats.quantile(0.75):.3f} p90={t_stats.quantile(0.9):.3f}")
print(f"  |t| p10={abs_t.quantile(0.1):.3f} p50={abs_t.quantile(0.5):.3f} p90={abs_t.quantile(0.9):.3f}")
print(f"  Fraction |t| < 1: {frac_lt1:.1%} ({abs_t[abs_t<1].count():,}/{len(abs_t):,})")
print(f"  Fraction |t| < 2: {(abs_t<2).mean():.1%}")
print(f"  R2 p10={r2s.quantile(0.1):.4f} p50={r2s.quantile(0.5):.4f} p90={r2s.quantile(0.9):.4f}")
print(f"  Mean R2={r2s.mean():.4f}")

# Also show how many firms have "reliable" betas
print(f"\n  |t| >= 2.0: {((abs_t>=2.0).sum()):,} firms ({(abs_t>=2.0).mean():.1%})")
print(f"  |t| >= 1.64: {((abs_t>=1.64).sum()):,} firms ({(abs_t>=1.64).mean():.1%})")
print(f"  |t| >= 1.0: {((abs_t>=1.0).sum()):,} firms ({(abs_t>=1.0).mean():.1%})")

# Quick check: fraction positive vs t-stat
pos_mask=betas_m["beta_uk"]>=0
print(f"\n  POSITIVE betas: {pos_mask.sum():,} ({pos_mask.mean():.1%})")
print(f"    Median |t| of positive: {abs_t[pos_mask].median():.3f}")
print(f"    Median |t| of negative: {abs_t[~pos_mask].median():.3f}")
print(f"    Frac |t|<1 of positive: {(abs_t[pos_mask]<1).mean():.1%}")
print(f"    Frac |t|<1 of negative: {(abs_t[~pos_mask]<1).mean():.1%}")

# ============================================================
# TASK 2: WEEKLY vol -> beta estimation + CF correlation
# ============================================================
print(f"\n{'='*60}")
print("TASK 2: Weekly vol betas")
print(f"{'='*60}")

# Firm weekly vol
g_w=cr.groupby(["PERMNO","week_id"])
fv_w=g_w["RET"].std()
fv_w=fv_w[g_w["RET"].count()>=MIN_DAYS_W].reset_index()
fv_w.columns=["PERMNO","week_id","vol_r_w"]

print(f"  Firm-weeks: {len(fv_w):,}")

mg_w=fv_w.merge(macro_w,on="week_id",how="inner")

res_w=[]
for pn,grp in mg_w.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r_w","vol_FTSE100_w","vol_SP500_w","vol_FX_w"])
    if len(grp)<MIN_WEEKS: continue
    yv=grp["vol_r_w"].values; n=len(yv)
    X=np.column_stack([np.ones(n),grp["vol_FTSE100_w"],grp["vol_SP500_w"],grp["vol_FX_w"]])
    try:
        b,resid,rank,sing=np.linalg.lstsq(X,yv,rcond=None)
        yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
        r2=1-ssr/sst if sst>0 else 0
        sigma2=ssr/(n-4) if n>4 else np.nan
        XtX_inv=np.linalg.inv(X.T@X)
        se_beta=np.sqrt(sigma2*XtX_inv[1,1])
        t_stat=b[1]/se_beta if se_beta>0 else np.nan
        res_w.append({"PERMNO":pn,"beta_uk_w":b[1],"n_w":n,"r2_w":r2,"t_stat_w":t_stat})
    except: continue

betas_w=pd.DataFrame(res_w)
betas_w=betas_w.merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
betas_w=betas_w.drop_duplicates(subset=["gvkey"],keep="first")

bpos_w=betas_w[betas_w["beta_uk_w"]>=0]; bneg_w=betas_w[betas_w["beta_uk_w"]<0]
neg_pct_w=len(bneg_w)/len(betas_w)*100
if len(bpos_w)>=3:
    t1w,t2w=bpos_w["beta_uk_w"].quantile(1/3),bpos_w["beta_uk_w"].quantile(2/3)
    hi_w=(betas_w["beta_uk_w"]>=t2w).sum()
    lo_w=((betas_w["beta_uk_w"]>=0)&(betas_w["beta_uk_w"]<=t1w)).sum()
else: t1w,t2w,hi_w,lo_w=np.nan,np.nan,0,0

print(f"  N={len(betas_w):,}  Neg={len(bneg_w):,} ({neg_pct_w:.1f}%)  Pos={len(bpos_w):,}")
print(f"  T1={t1w:.4f} T2={t2w:.4f}  HIGH={hi_w:,} LOW={lo_w:,}")
print(f"  Median beta_w={betas_w['beta_uk_w'].median():.4f}  Mean={betas_w['beta_uk_w'].mean():.4f}")

# t-stat distribution for weekly
t_w=betas_w["t_stat_w"].dropna()
abs_t_w=t_w.abs()
r2w=betas_w["r2_w"].dropna()
print(f"\n  Weekly t-stat: p10={t_w.quantile(0.1):.3f} p50={t_w.quantile(0.5):.3f} p90={t_w.quantile(0.9):.3f}")
print(f"  Weekly |t|: p50={abs_t_w.quantile(0.5):.3f}  frac |t|<1: {(abs_t_w<1).mean():.1%}  frac |t|>=2: {(abs_t_w>=2).mean():.1%}")
print(f"  Weekly R2: p10={r2w.quantile(0.1):.4f} p50={r2w.quantile(0.5):.4f} p90={r2w.quantile(0.9):.4f}  mean={r2w.mean():.4f}")
print(f"  Median n per firm: {betas_w['n_w'].median():.0f}")

# ============================================================
# CF CORRELATION — monthly vs weekly
# ============================================================
print(f"\n{'='*60}")
print("CF-beta rank correlation: Monthly vs Weekly")
print(f"{'='*60}")

# CF beta pipeline
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

# Load 2002-2018 quarterly returns
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

# CF betas (monthly — same for both comparisons)
cf_data=cf_monthly.merge(macro_m,left_on="ym",right_on="ym",how="inner")
cf_data=cf_data[(cf_data["ym"]>="2010-01")&(cf_data["ym"]<="2014-12")]
cf_betas_dict={}
for gk,grp in cf_data.groupby("gvkey"):
    grp=grp.dropna(subset=["vol_cf","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_cf"].values
    X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try:
        b=np.linalg.lstsq(X,yv,rcond=None)[0]; cf_betas_dict[gk]=b[1]
    except: continue
betas_cf=pd.DataFrame(list(cf_betas_dict.items()),columns=["gvkey","beta_cf"])

def cf_compare(label, level_b, beta_col):
    common=set(level_b["gvkey"])&set(betas_cf["gvkey"])
    if len(common)<20:
        print(f"  {label}: Too few common ({len(common)})")
        return
    bl=level_b[level_b["gvkey"].isin(common)].set_index("gvkey")[beta_col]
    bc=betas_cf[betas_cf["gvkey"].isin(common)].set_index("gvkey")["beta_cf"]
    rc=bl.rank().corr(bc.rank())
    bl_pos=bl[bl>=0]; bc_pos=bc[bc>=0]
    t2l=bl_pos.quantile(2/3); t2c=bc_pos.quantile(2/3)
    hl=set(bl_pos[bl_pos>=t2l].index); hc=set(bc_pos[bc_pos>=t2c].index)
    overlap=len(hl&hc)/max(len(hl|hc),1)
    print(f"  {label}: rank_corr={rc:.4f}  top-tercile overlap={overlap:.3f} ({overlap*100:.1f}%)  common={len(common):,}")

cf_compare("MONTHLY", betas_m, "beta_uk")
cf_compare("WEEKLY", betas_w, "beta_uk_w")
print(f"  Paper: rank_corr=0.80  top-tercile overlap=0.86")

# ============================================================
# COMPARISON TABLE
# ============================================================
print(f"\n{'='*60}")
print("SUMMARY: Monthly vs Weekly")
print(f"{'='*60}")
bpos_m=betas_m[betas_m["beta_uk"]>=0]; t1m,t2m=bpos_m["beta_uk"].quantile(1/3),bpos_m["beta_uk"].quantile(2/3)
bneg_m=betas_m[betas_m["beta_uk"]<0]
neg_m=len(bneg_m)/len(betas_m)*100
hi_m=(betas_m["beta_uk"]>=t2m).sum()
lo_m=((betas_m["beta_uk"]>=0)&(betas_m["beta_uk"]<=t1m)).sum()

print(f"  MONTHLY: N={len(betas_m):,} Neg={neg_m:.1f}% T1={t1m:.4f} T2={t2m:.4f} H={hi_m:,} L={lo_m:,}  |t|p50={abs_t.median():.2f}  R2p50={r2s.median():.3f}")
print(f"  WEEKLY:  N={len(betas_w):,} Neg={neg_pct_w:.1f}% T1={t1w:.4f} T2={t2w:.4f} H={hi_w:,} L={lo_w:,}  |t|p50={abs_t_w.median():.2f}  R2p50={r2w.median():.3f}")
print(f"  Paper:   N=809    Neg<=20%   T1=0.28  T2=0.68  H=449 L=360  rank_corr=0.80")
