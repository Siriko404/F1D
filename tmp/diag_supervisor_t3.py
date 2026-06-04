"""Supervisor Task 3: Orthogonalize SP500 (and FX) to FTSE before firm beta estimation.
Single change: usres_t = residual of vol(SP500) ~ vol(FTSE). CF-correlation is judge."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24
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

# ============================================================
# 2. CCM — P-only, date-resolved
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
# 3. DAILY RETURNS + MACRO VOL (monthly)
# ============================================================
print("3. Daily returns + macro vol")
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

# SP500 monthly vol
sp=cr[["date","sprtrn"]].drop_duplicates()
sp["ym"]=sp["date"].dt.to_period("M").astype(str)
sp_m=sp.groupby("ym")["sprtrn"].std()
sp_m=sp_m[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp_m.columns=["ym","vol_SP500"]

# FTSE monthly vol (log returns)
ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1))
ftse["ym"]=ftse["Date"].dt.to_period("M").astype(str)
ftv=ftse.groupby("ym")["lr"].std()
ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
ftv.columns=["ym","vol_FTSE100"]

# FX monthly vol (log returns)
fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1))
fx["ym"]=fx["DATE"].dt.to_period("M").astype(str)
fxv=fx.groupby("ym")["lr"].std()
fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
fxv.columns=["ym","vol_FX"]

# Merge all three
macro=sp_m.merge(ftv,on="ym").merge(fxv,on="ym")
print(f"  Macro months: {len(macro)}")

# Orthogonalization: SP500 ~ FTSE, FX ~ FTSE
# Check collinearity first
from numpy.linalg import lstsq
sp_on_ft=lstsq(np.column_stack([np.ones(len(macro)),macro["vol_FTSE100"].values]),
               macro["vol_SP500"].values,rcond=None)[0]
fx_on_ft=lstsq(np.column_stack([np.ones(len(macro)),macro["vol_FTSE100"].values]),
               macro["vol_FX"].values,rcond=None)[0]
corr_sp_ft=macro["vol_SP500"].corr(macro["vol_FTSE100"])
corr_fx_ft=macro["vol_FX"].corr(macro["vol_FTSE100"])

print(f"  corr(SP500, FTSE) = {corr_sp_ft:.4f}  beta = {sp_on_ft[1]:.4f}")
print(f"  corr(FX, FTSE) = {corr_fx_ft:.4f}  beta = {fx_on_ft[1]:.4f}")

# Build orthogonalized series
macro["usres"]=macro["vol_SP500"]-(sp_on_ft[0]+sp_on_ft[1]*macro["vol_FTSE100"])
macro["fxres"]=macro["vol_FX"]-(fx_on_ft[0]+fx_on_ft[1]*macro["vol_FTSE100"])

# ============================================================
# 4. FIRM MONTHLY VOL
# ============================================================
print("4. Firm monthly vol")
g=cr.groupby(["PERMNO","ym"])
fv=g["RET"].std()
fv=fv[g["RET"].count()>=MIN_DAYS].reset_index()
fv.columns=["PERMNO","ym","vol_r"]

# ============================================================
# 5. BETA ESTIMATION — BASELINE vs ORTHOGONALIZED
# ============================================================
print("5. Beta estimation: BASELINE vs ORTHOGONALIZED")

def estimate_betas(fv_df, macro_df, rhs, beta_idx=1):
    """Estimate firm-by-firm OLS betas. rhs: list of col names. beta_idx: which coef is beta_uk."""
    mg=fv_df.merge(macro_df[rhs+["ym"]],on="ym",how="inner")
    res=[]
    for pn,grp in mg.groupby("PERMNO"):
        grp=grp.dropna(subset=["vol_r"]+rhs)
        if len(grp)<MIN_MONTHS: continue
        yv=grp["vol_r"].values
        X=np.column_stack([np.ones(len(yv))]+[grp[c].values for c in rhs])
        try:
            b,resid,rank,sing=np.linalg.lstsq(X,yv,rcond=None)
            yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
            r2=1-ssr/sst if sst>0 else 0
            sigma2=ssr/(len(yv)-len(rhs)-1) if len(yv)>len(rhs)+1 else np.nan
            XtX_inv=np.linalg.inv(X.T@X)
            se=np.sqrt(sigma2*XtX_inv[beta_idx,beta_idx])
            t_stat=b[beta_idx]/se if se>0 else np.nan
            res.append({"PERMNO":pn,"beta_uk":b[beta_idx],"beta_sp":b[2] if len(rhs)>2 else np.nan,
                       "n":len(grp),"r2":r2,"t_stat":t_stat})
        except: continue
    betas=pd.DataFrame(res)
    betas=betas.merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
    betas=betas.drop_duplicates(subset=["gvkey"],keep="first")
    return betas

def report(label, betas):
    bpos=betas[betas["beta_uk"]>=0]; bneg=betas[betas["beta_uk"]<0]
    neg_pct=len(bneg)/len(betas)*100
    if len(bpos)>=3:
        t1,t2=bpos["beta_uk"].quantile(1/3),bpos["beta_uk"].quantile(2/3)
        hi=(betas["beta_uk"]>=t2).sum(); lo=((betas["beta_uk"]>=0)&(betas["beta_uk"]<=t1)).sum()
    else: t1,t2,hi,lo=np.nan,np.nan,0,0
    t_abs=betas["t_stat"].abs()
    print(f"  {label}: N={len(betas):,} Neg={len(bneg):,} ({neg_pct:.1f}%) T1={t1:.4f} T2={t2:.4f} H={hi:,} L={lo:,}")
    print(f"    Median beta={betas['beta_uk'].median():.4f} Mean={betas['beta_uk'].mean():.4f}")
    print(f"    |t| p50={t_abs.median():.3f}  frac |t|<1: {(t_abs<1).mean():.1%}  R2 p50={betas['r2'].median():.3f}")
    return {"n":len(betas),"neg_pct":neg_pct,"t1":t1,"t2":t2,"hi":hi,"lo":lo}

# BASELINE: vol_FTSE100 + vol_SP500 + vol_FX
betas_base=estimate_betas(fv, macro, ["vol_FTSE100","vol_SP500","vol_FX"], beta_idx=1)
bs_base=report("BASELINE (raw SP500+FX)", betas_base)

# ORTHOGONALIZED: vol_FTSE100 + usres + fxres (SP500 and FX residual to FTSE)
betas_orth=estimate_betas(fv, macro, ["vol_FTSE100","usres","fxres"], beta_idx=1)
bs_orth=report("ORTHOGONALIZED (usres+fxres)", betas_orth)

# Also test: vol_FTSE100 + usres + vol_FX (only SP500 residualized, FX raw)
betas_orth2=estimate_betas(fv, macro, ["vol_FTSE100","usres","vol_FX"], beta_idx=1)
bs_orth2=report("ORTHOG2 (usres + raw FX)", betas_orth2)

# ============================================================
# 6. CF-BETA RANK CORRELATION
# ============================================================
print(f"\n{'='*60}")
print("6. CF-beta rank correlation: BASELINE vs ORTHOGONALIZED")
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

# CF betas — use BASELINE macro (raw SP500+FX) for consistency with paper's CF exercise
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

def cf_compare(label, level_b):
    common=set(level_b["gvkey"])&set(betas_cf["gvkey"])
    if len(common)<20:
        print(f"  {label}: Too few common ({len(common)})")
        return
    bl=level_b[level_b["gvkey"].isin(common)].set_index("gvkey")["beta_uk"]
    bc=betas_cf[betas_cf["gvkey"].isin(common)].set_index("gvkey")["beta_cf"]
    rc=bl.rank().corr(bc.rank())
    bl_pos=bl[bl>=0]; bc_pos=bc[bc>=0]
    t2l=bl_pos.quantile(2/3); t2c=bc_pos.quantile(2/3)
    hl=set(bl_pos[bl_pos>=t2l].index); hc=set(bc_pos[bc_pos>=t2c].index)
    overlap=len(hl&hc)/max(len(hl|hc),1)
    print(f"  {label}: rank_corr={rc:.4f}  top-tercile overlap={overlap:.3f} ({overlap*100:.1f}%)  common={len(common):,}")

cf_compare("BASELINE", betas_base)
cf_compare("ORTHOGONALIZED", betas_orth)
cf_compare("ORTHOG2 (usres+rawFX)", betas_orth2)

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"  BASELINE:           N={bs_base['n']:,} Neg={bs_base['neg_pct']:.1f}% T1={bs_base['t1']:.4f} T2={bs_base['t2']:.4f} H={bs_base['hi']:,} L={bs_base['lo']:,}")
print(f"  ORTHOGONALIZED:     N={bs_orth['n']:,} Neg={bs_orth['neg_pct']:.1f}% T1={bs_orth['t1']:.4f} T2={bs_orth['t2']:.4f} H={bs_orth['hi']:,} L={bs_orth['lo']:,}")
print(f"  ORTHOG2 (usres+FX): N={bs_orth2['n']:,} Neg={bs_orth2['neg_pct']:.1f}% T1={bs_orth2['t1']:.4f} T2={bs_orth2['t2']:.4f} H={bs_orth2['hi']:,} L={bs_orth2['lo']:,}")
print(f"  Paper:              N=809    Neg<=20%   T1=0.28  T2=0.68  H=449 L=360  rank_corr=0.80")

# Check: did SP500 orthogonalization actually change anything or just re-label?
# Show that vol_FTSE100 + usres IS the same model as vol_FTSE100 + vol_SP500 algebraically
# (Frisch-Waugh — coefficient on FTSE is IDENTICAL in both specs)
print(f"\n  Frisch-Waugh check: beta_uk should be identical between BASELINE and ORTHOGONALIZED")
print(f"  (Orthogonalizing SP500 to FTSE does NOT change the FTSE coefficient — FWL theorem)")
# Verify numerically on first few firms
common_firms=set(betas_base["gvkey"])&set(betas_orth["gvkey"])
fw_diff=[]
for gk in list(common_firms)[:10]:
    b1=betas_base[betas_base["gvkey"]==gk]["beta_uk"].values[0]
    b2=betas_orth[betas_orth["gvkey"]==gk]["beta_uk"].values[0]
    fw_diff.append(abs(b1-b2))
print(f"  Max |diff| on first 10 firms: {max(fw_diff):.2e}")
print(f"  (FWL theorem: orthogonalization is a no-op for the FTSE coefficient)")
