"""Supervisor Tasks 4+5: Universe arithmetic + |t|-based screen → CF-correlation."""
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
# Save key firm characteristics for cross-tab
comp_raw["log_at"]=np.log(comp_raw["atq"])
comp_raw["log_mktcap"]=np.log(comp_raw["mktcap"])
firm_chars=comp_raw.groupby("gvkey")[["log_at","log_mktcap"]].last().reset_index()
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

# Macro
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

# Firm vol
g=cr.groupby(["PERMNO","ym"]); fv=g["RET"].std(); fv=fv[g["RET"].count()>=MIN_DAYS].reset_index()
fv.columns=["PERMNO","ym","vol_r"]

# Betas + full diagnostics
mg=fv.merge(macro,on="ym",how="inner")
res=[]
for pn,grp in mg.groupby("PERMNO"):
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
        se_beta=np.sqrt(sigma2*XtX_inv[1,1])
        t_stat=b[1]/se_beta if se_beta>0 else np.nan
        res.append({"PERMNO":pn,"beta_uk":b[1],"n_obs":n,"r2":r2,"t_stat":t_stat})
    except: continue
betas=pd.DataFrame(res)
betas=betas.merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
betas=betas.drop_duplicates(subset=["gvkey"],keep="first")
betas["abs_t"]=betas["t_stat"].abs()
betas=betas.merge(firm_chars,on="gvkey",how="left")

# ============================================================
# TASK 4: UNIVERSE ARITHMETIC + CROSS-TAB
# ============================================================
print(f"\n{'='*60}")
print("TASK 4: Universe arithmetic")
print(f"{'='*60}")

# Paper arithmetic
paper_hi, paper_lo = 449, 360
paper_hl = paper_hi + paper_lo  # 809
# If HIGH+LOW = 2/3 of nonnegative pool:
paper_nonneg_implied = round(paper_hl * 3/2)  # top+bottom terciles = 2/3 of nonneg
# If negatives ≤ 20%:
# total = nonneg / (1 - neg_frac)
for neg_frac in [0.10, 0.15, 0.20]:
    paper_total = round(paper_nonneg_implied / (1 - neg_frac))
    paper_neg = paper_total - paper_nonneg_implied
    print(f"  Paper: H+L={paper_hl} -> nonneg={paper_nonneg_implied} (={paper_hl} * 3/2)")
    print(f"    If neg%={neg_frac:.0%}: total={paper_total:,}  neg={paper_neg:,}")

# Our numbers
our_total = len(betas)
our_pos = (betas["beta_uk"]>=0).sum()
our_neg = (betas["beta_uk"]<0).sum()
our_neg_pct = our_neg / our_total * 100
our_bpos = betas[betas["beta_uk"]>=0]
our_t1 = our_bpos["beta_uk"].quantile(1/3)
our_t2 = our_bpos["beta_uk"].quantile(2/3)
our_hi = (betas["beta_uk"]>=our_t2).sum()
our_lo = ((betas["beta_uk"]>=0)&(betas["beta_uk"]<=our_t1)).sum()

print(f"\n  Ours: total={our_total:,}  pos={our_pos:,}  neg={our_neg:,} ({our_neg_pct:.1f}%)")
print(f"    T1={our_t1:.4f} T2={our_t2:.4f}  H={our_hi:,} L={our_lo:,}")
print(f"  Surplus vs paper (15% neg): total {our_total-paper_total:+,}  neg {our_neg-paper_neg:+,}  nonneg {our_pos-paper_nonneg_implied:+,}")

# Cross-tab: negative vs positive firm characteristics
print(f"\n{'='*60}")
print("TASK 4: Negative vs Positive firm profile")
print(f"{'='*60}")

pos_mask = betas["beta_uk"] >= 0
neg_mask = betas["beta_uk"] < 0

for label, mask in [("POSITIVE", pos_mask), ("NEGATIVE", neg_mask)]:
    sub = betas[mask]
    print(f"\n  {label} (N={len(sub):,}):")
    print(f"    log(AT) p10={sub['log_at'].quantile(0.1):.2f} p50={sub['log_at'].median():.2f} p90={sub['log_at'].quantile(0.9):.2f}")
    print(f"    log(MKTCAP) p10={sub['log_mktcap'].quantile(0.1):.2f} p50={sub['log_mktcap'].median():.2f} p90={sub['log_mktcap'].quantile(0.9):.2f}")
    print(f"    |t| p10={sub['abs_t'].quantile(0.1):.3f} p50={sub['abs_t'].median():.3f} p90={sub['abs_t'].quantile(0.9):.3f}")
    print(f"    n_obs p50={sub['n_obs'].median():.0f}")
    print(f"    R2 p50={sub['r2'].median():.3f}")
    print(f"    beta_uk p50={sub['beta_uk'].median():.4f}")

# Size decile cross-tab
betas["size_decile"] = pd.qcut(betas["log_at"].rank(method="first"), 10, labels=False) + 1
print(f"\n  Negatives by size decile:")
for d in range(1, 11):
    sub = betas[betas["size_decile"]==d]
    n_neg = (sub["beta_uk"]<0).sum()
    print(f"    Decile {d:2d}: N={len(sub):4d}  Neg={n_neg:4d} ({n_neg/len(sub)*100:5.1f}%)  Med|t|={sub['abs_t'].median():.3f}")

# ============================================================
# TASK 4b: How does the negative share change with |t| screening?
# ============================================================
print(f"\n{'='*60}")
print("TASK 4b: Negative share by |t| threshold")
print(f"{'='*60}")

betas_sorted = betas.sort_values("abs_t")
for t_cut in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    keep = betas_sorted[betas_sorted["abs_t"] >= t_cut]
    n_neg = (keep["beta_uk"]<0).sum()
    neg_pct = n_neg/len(keep)*100
    print(f"  |t| >= {t_cut:.1f}: N={len(keep):,}  Neg={n_neg:,} ({neg_pct:.1f}%)")

# ============================================================
# TASK 5: |t|-based screening → CF-correlation
# ============================================================
print(f"\n{'='*60}")
print("TASK 5: |t|-screened CF-correlation sweep")
print(f"{'='*60}")

# CF pipeline (same as before)
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

def cf_corr_for_subset(betas_subset, betas_cf_df, label):
    common=set(betas_subset["gvkey"])&set(betas_cf_df["gvkey"])
    if len(common)<30:
        return {"label":label,"n":len(betas_subset),"common":len(common),
                "rank_corr":np.nan,"overlap":np.nan}
    bl=betas_subset[betas_subset["gvkey"].isin(common)].set_index("gvkey")["beta_uk"]
    bc=betas_cf_df[betas_cf_df["gvkey"].isin(common)].set_index("gvkey")["beta_cf"]
    rc=bl.rank().corr(bc.rank())
    bl_pos=bl[bl>=0]; bc_pos=bc[bc>=0]
    if len(bl_pos)<3 or len(bc_pos)<3:
        return {"label":label,"n":len(betas_subset),"common":len(common),
                "rank_corr":rc,"overlap":np.nan}
    t2l=bl_pos.quantile(2/3); t2c=bc_pos.quantile(2/3)
    hl=set(bl_pos[bl_pos>=t2l].index); hc=set(bc_pos[bc_pos>=t2c].index)
    overlap=len(hl&hc)/max(len(hl|hc),1)
    return {"label":label,"n":len(betas_subset),"common":len(common),
            "rank_corr":rc,"overlap":overlap}

def tercile_report(betas_subset, label):
    bpos=betas_subset[betas_subset["beta_uk"]>=0]
    bneg=betas_subset[betas_subset["beta_uk"]<0]
    neg_pct=len(bneg)/len(betas_subset)*100
    if len(bpos)>=3:
        t1,t2=bpos["beta_uk"].quantile(1/3),bpos["beta_uk"].quantile(2/3)
        hi=(betas_subset["beta_uk"]>=t2).sum()
        lo=((betas_subset["beta_uk"]>=0)&(betas_subset["beta_uk"]<=t1)).sum()
    else: t1,t2,hi,lo=np.nan,np.nan,0,0
    return {"label":label,"n":len(betas_subset),"neg_pct":neg_pct,"t1":t1,"t2":t2,"hi":hi,"lo":lo}

# Sweep |t| thresholds
print(f"\n  {'Threshold':<12} {'N':>6} {'Neg%':>7} {'T1':>7} {'T2':>7} {'H':>5} {'L':>5} {'nonneg':>7} {'CF_rank':>9} {'CF_overlap':>10}")
print(f"  {'-'*12} {'-'*6} {'-'*7} {'-'*7} {'-'*7} {'-'*5} {'-'*5} {'-'*7} {'-'*9} {'-'*10}")

# Baseline
tr=tercile_report(betas, "BASELINE")
cfr=cf_corr_for_subset(betas, betas_cf, "BASELINE")
print(f"  {'BASELINE':<12} {tr['n']:>6} {tr['neg_pct']:>6.1f}% {tr['t1']:>7.4f} {tr['t2']:>7.4f} {tr['hi']:>5} {tr['lo']:>5} {(tr['n']-int(tr['n']*tr['neg_pct']/100)):>7} {cfr['rank_corr']:>9.4f} {cfr['overlap']:>10.3f}")

# Paper targets: total ~1,400-1,500, nonneg ~1,214
paper_nonneg_target = 1214
paper_total_targets = [1400, 1500, 1600]

betas_by_t = betas.sort_values("abs_t")

for target_n in [1800, 1600, 1500, 1400, 1300, 1200, 1100, 1000, 900]:
    if target_n > len(betas_by_t): continue
    keep = betas_by_t.tail(target_n)  # keep the top-N by |t|
    t_cut = keep["abs_t"].min()
    tr2 = tercile_report(keep, f"N={target_n}")
    cfr2 = cf_corr_for_subset(keep, betas_cf, f"N={target_n}")
    nonneg_n = keep[keep["beta_uk"]>=0].pipe(len)
    print(f"  |t|>={t_cut:.3f}     {tr2['n']:>6} {tr2['neg_pct']:>6.1f}% {tr2['t1']:>7.4f} {tr2['t2']:>7.4f} {tr2['hi']:>5} {tr2['lo']:>5} {nonneg_n:>7} {cfr2['rank_corr']:>9.4f} {cfr2['overlap']:>10.3f}")

print(f"\n  Paper target: N~1,500  Neg<=20%  T1=0.28  T2=0.68  H=449 L=360  rank_corr=0.80")

# ============================================================
# BONUS: What observable filter matches the |t| screen?
# ============================================================
print(f"\n{'='*60}")
print("BONUS: What observable filter matches the |t| threshold?")
print(f"{'='*60}")

# For the paper's implied total (~1,500), what |t| cut is needed?
target_total = 1500
keep_target = betas_by_t.tail(target_total)
t_cut_target = keep_target["abs_t"].min()
print(f"  To get N={target_total}: keep |t| >= {t_cut_target:.4f}")
print(f"  Neg% = {(keep_target['beta_uk']<0).mean()*100:.1f}%")

# What size/price cut achieves similar selectivity?
print(f"\n  Size decile of firms with |t| >= {t_cut_target:.4f}:")
keep_above = betas[betas["abs_t"]>=t_cut_target]
print(f"    N={len(keep_above):,}  Neg%={keep_above['beta_uk'].lt(0).mean()*100:.1f}%")
for d in range(1, 11):
    all_in_d = betas[betas["size_decile"]==d]
    keep_in_d = keep_above[keep_above["size_decile"]==d]
    pct = len(keep_in_d)/len(all_in_d)*100 if len(all_in_d)>0 else 0
    print(f"    Decile {d}: {len(keep_in_d):4d}/{len(all_in_d):4d} ({pct:.0f}%)")
