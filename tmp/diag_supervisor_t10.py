"""Supervisor Task 10: Audit CF-beta construction + VAR-free CF proxy (annual vol beta)."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24
RHO_Q = 0.99

# ============================================================
# 1. COMPUSTAT SURVIVOR LIST
# ============================================================
print("1. Survivors")
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
# 2. CCM — P-only
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
# 3. MONTHLY BETAS (standard β^UK)
# ============================================================
print("3. Monthly β^UK")
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
cr["year"]=cr["date"].dt.year

sp=cr[["date","sprtrn"]].drop_duplicates(); sp["ym"]=sp["date"].dt.to_period("M").astype(str)
sp["year"]=sp["date"].dt.year
sp_m=sp.groupby("ym")["sprtrn"].std(); sp_m=sp_m[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp_m.columns=["ym","vol_SP500"]

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M").astype(str)
ftse["year"]=ftse["Date"].dt.year
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
ftv.columns=["ym","vol_FTSE100"]

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M").astype(str)
fx["year"]=fx["DATE"].dt.year
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
fxv.columns=["ym","vol_FX"]

macro_m=sp_m.merge(ftv,on="ym").merge(fxv,on="ym")

# Firm monthly vol
g=cr.groupby(["PERMNO","ym"]); fv_m=g["RET"].std(); fv_m=fv_m[g["RET"].count()>=MIN_DAYS].reset_index()
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
        sigma2=ssr/(n-4) if n>4 else np.nan
        XtX_inv=np.linalg.inv(X.T@X)
        se=np.sqrt(sigma2*XtX_inv[1,1])
        t_stat=b[1]/se if se>0 else np.nan
        res_m.append({"PERMNO":pn,"beta_uk":b[1],"n":n,"r2":r2,"t_stat":t_stat,"se":se})
    except: continue
betas_m=pd.DataFrame(res_m).merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
betas_m=betas_m.drop_duplicates(subset=["gvkey"],keep="first")
print(f"  Monthly β^UK: {len(betas_m):,} firms")

# ============================================================
# 4. CF BETAS — PER-FIRM VAR (current method)
# ============================================================
print("4. CF betas (per-firm VAR)")
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
print(f"  CF VAR firms (per-firm): {cf_df['gvkey'].nunique():,}")

# CF betas via eq(13)
cf_data=cf_monthly.merge(macro_m[["ym","vol_FTSE100","vol_SP500","vol_FX"]],on="ym",how="inner")
cf_data=cf_data[(cf_data["ym"]>="2010-01")&(cf_data["ym"]<="2014-12")]
cf_betas_list=[]
for gk,grp in cf_data.groupby("gvkey"):
    grp=grp.dropna(subset=["vol_cf","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_cf"].values; n=len(yv)
    X=np.column_stack([np.ones(n),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try:
        b,resid,rank,sing=np.linalg.lstsq(X,yv,rcond=None)
        yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
        r2=1-ssr/sst if sst>0 else 0
        sigma2=ssr/(n-4) if n>4 else np.nan
        XtX_inv=np.linalg.inv(X.T@X)
        se=np.sqrt(sigma2*XtX_inv[1,1])
        t_stat=b[1]/se if se>0 else np.nan
        cf_betas_list.append({"gvkey":gk,"beta_cf":b[1],"n":n,"r2":r2,"t_cf":t_stat})
    except: continue
betas_cf=pd.DataFrame(cf_betas_list)

# CF beta stats
print(f"\n  β^UK_CF (per-firm VAR) distribution:")
cf_vals=betas_cf["beta_cf"]
cf_pos=(cf_vals>=0).sum(); cf_neg=(cf_vals<0).sum()
cf_abs_t=betas_cf["t_cf"].abs()
print(f"    N={len(betas_cf):,}  Pos={cf_pos:,}  Neg={cf_neg:,} ({cf_neg/len(betas_cf)*100:.1f}%)")
print(f"    Mean={cf_vals.mean():.4f}  SD={cf_vals.std():.4f}  p10={cf_vals.quantile(0.1):.4f}  p50={cf_vals.median():.4f}  p90={cf_vals.quantile(0.9):.4f}")
print(f"    |t| p50={cf_abs_t.median():.3f}  frac |t|<1: {(cf_abs_t<1).mean():.1%}")
print(f"    R2 p50={betas_cf['r2'].median():.3f}")

# ============================================================
# 5. VAR-FREE CF PROXY: ANNUAL vol beta
# ============================================================
print(f"\n{'='*60}")
print("5. VAR-FREE CF PROXY: Annual vol beta")
print(f"{'='*60}")

# Annual firm vol (2010-2014)
ga=cr.groupby(["PERMNO","year"])["RET"].std()
ga=ga[cr.groupby(["PERMNO","year"])["RET"].count()>=150].reset_index()  # min 150 trading days
ga.columns=["PERMNO","year","vol_r_a"]

# Annual macro vol
sp_a=sp.groupby("year")["sprtrn"].std(); sp_a=sp_a[sp.groupby("year")["sprtrn"].count()>=150].reset_index()
sp_a.columns=["year","vol_SP500_a"]

ftse_a=ftse.groupby("year")["lr"].std(); ftse_a=ftse_a[ftse.groupby("year")["lr"].count()>=150].reset_index()
ftse_a.columns=["year","vol_FTSE100_a"]

fx_a=fx.groupby("year")["lr"].std(); fx_a=fx_a[fx.groupby("year")["lr"].count()>=150].reset_index()
fx_a.columns=["year","vol_FX_a"]

macro_a=sp_a.merge(ftse_a,on="year").merge(fx_a,on="year")

# Annual betas (5 years, 2010-2014)
mg_a=ga.merge(macro_a,on="year",how="inner")
res_a=[]
for pn,grp in mg_a.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r_a","vol_FTSE100_a","vol_SP500_a","vol_FX_a"])
    if len(grp)<4: continue  # at least 4 of 5 years
    yv=grp["vol_r_a"].values; n=len(yv)
    X=np.column_stack([np.ones(n),grp["vol_FTSE100_a"],grp["vol_SP500_a"],grp["vol_FX_a"]])
    try:
        b,resid,rank,sing=np.linalg.lstsq(X,yv,rcond=None)
        res_a.append({"PERMNO":pn,"beta_uk_ann":b[1],"n_a":n})
    except: continue
betas_a=pd.DataFrame(res_a).merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
betas_a=betas_a.drop_duplicates(subset=["gvkey"],keep="first")
print(f"  Annual β^UK: {len(betas_a):,} firms")

# ============================================================
# 6. CORRELATION MATRIX: Monthly β^UK vs CF β vs Annual β
# ============================================================
print(f"\n{'='*60}")
print("6. RANK CORRELATION MATRIX")
print(f"{'='*60}")

# Monthly vs CF
common_mc=set(betas_m["gvkey"])&set(betas_cf["gvkey"])
bm=betas_m[betas_m["gvkey"].isin(common_mc)].set_index("gvkey")["beta_uk"]
bc=betas_cf[betas_cf["gvkey"].isin(common_mc)].set_index("gvkey")["beta_cf"]
rc_mc=bm.rank().corr(bc.rank())

# Monthly vs Annual
common_ma=set(betas_m["gvkey"])&set(betas_a["gvkey"])
bm2=betas_m[betas_m["gvkey"].isin(common_ma)].set_index("gvkey")["beta_uk"]
ba=betas_a[betas_a["gvkey"].isin(common_ma)].set_index("gvkey")["beta_uk_ann"]
rc_ma=bm2.rank().corr(ba.rank())

# Annual vs CF
common_ac=set(betas_a["gvkey"])&set(betas_cf["gvkey"])
ba2=betas_a[betas_a["gvkey"].isin(common_ac)].set_index("gvkey")["beta_uk_ann"]
bc2=betas_cf[betas_cf["gvkey"].isin(common_ac)].set_index("gvkey")["beta_cf"]
rc_ac=ba2.rank().corr(bc2.rank())

# Pearson
pearson_mc=bm.corr(bc)
pearson_ma=bm2.corr(ba)
pearson_ac=ba2.corr(bc2)

print(f"  Monthly vs CF (per-firm VAR):     rank_corr={rc_mc:.4f}  pearson={pearson_mc:.4f}  N={len(common_mc):,}")
print(f"  Monthly vs Annual (VAR-free):      rank_corr={rc_ma:.4f}  pearson={pearson_ma:.4f}  N={len(common_ma):,}")
print(f"  Annual  vs CF (per-firm VAR):      rank_corr={rc_ac:.4f}  pearson={pearson_ac:.4f}  N={len(common_ac):,}")
print(f"  Paper:  Monthly vs CF rank_corr = 0.80")

# ============================================================
# 7. TRIPLE COMMON: Monthly vs CF vs Annual on same firms
# ============================================================
common_triple = common_mc & common_ma
bmt=betas_m[betas_m["gvkey"].isin(common_triple)].set_index("gvkey")["beta_uk"]
bct=betas_cf[betas_cf["gvkey"].isin(common_triple)].set_index("gvkey")["beta_cf"]
bat=betas_a[betas_a["gvkey"].isin(common_triple)].set_index("gvkey")["beta_uk_ann"]
rc_mc_t=bmt.rank().corr(bct.rank())
rc_ma_t=bmt.rank().corr(bat.rank())
rc_ac_t=bat.rank().corr(bct.rank())

print(f"\n  Triple common (N={len(common_triple):,}):")
print(f"    Monthly vs CF:     {rc_mc_t:.4f}")
print(f"    Monthly vs Annual: {rc_ma_t:.4f}")
print(f"    Annual vs CF:      {rc_ac_t:.4f}")

# Key test: does Annual correlate with Monthly better than CF does?
print(f"\n  KEY TEST: Monthly-Annual rank_corr ({rc_ma_t:.4f}) {'>' if rc_ma_t>rc_mc_t else '<'} Monthly-CF ({rc_mc_t:.4f})")
if rc_ma_t > rc_mc_t + 0.05:
    print(f"  VERDICT: Annual (VAR-free) proxy has MUCH higher agreement with monthly β^UK")
    print(f"  → CF-news from per-firm VAR is the broken component, not monthly β^UK")
else:
    print(f"  VERDICT: Both proxies give similar agreement → β^UK itself may be the noisy component")

# Annual beta distribution
print(f"\n  Annual β^UK distribution:")
apos=(betas_a["beta_uk_ann"]>=0).sum(); aneg=(betas_a["beta_uk_ann"]<0).sum()
print(f"    N={len(betas_a):,}  Pos={apos:,}  Neg={aneg:,} ({aneg/len(betas_a)*100:.1f}%)")
print(f"    p10={betas_a['beta_uk_ann'].quantile(0.1):.4f}  p50={betas_a['beta_uk_ann'].median():.4f}  p90={betas_a['beta_uk_ann'].quantile(0.9):.4f}")
