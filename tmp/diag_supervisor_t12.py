"""Supervisor Task 12: EB shrinkage to FIC-100 industry mean + residual split-half firewall."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS, MIN_HALF = 15, 24, 24
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
survivor_gvkeys=set(comp_raw["gvkey"].unique())
# Get FIC-100 mapping
fic_map = comp_raw.groupby("gvkey")["icode100"].first().reset_index()
del comp_raw

# ============================================================
# 2. CCM
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
# 3. DAILY RETURNS + MACRO
# ============================================================
print("3. Daily returns + macro")
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

# Firm monthly vol
g=cr.groupby(["PERMNO","ym"]); fv=g["RET"].std(); fv=fv[g["RET"].count()>=MIN_DAYS].reset_index()
fv.columns=["PERMNO","ym","vol_r"]

# ============================================================
# 4. FULL-SAMPLE + SPLIT-HALF RAW BETAS (with SE)
# ============================================================
print("4. Estimating raw betas (full + split-half)")
HALF1_END, HALF2_START = "2012-07", "2012-08"

def est_betas(fv_df, macro_df, ym_start=None, ym_end=None):
    mg=fv_df.merge(macro_df,on="ym",how="inner")
    if ym_start: mg=mg[mg["ym"]<=ym_start]
    if ym_end: mg=mg[mg["ym"]>=ym_end]
    res=[]
    for pn,grp in mg.groupby("PERMNO"):
        grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
        min_obs = MIN_HALF if (ym_start or ym_end) else MIN_MONTHS
        if len(grp)<min_obs: continue
        yv=grp["vol_r"].values; n=len(yv)
        X=np.column_stack([np.ones(n),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
        try:
            b,resid,rank,sing=np.linalg.lstsq(X,yv,rcond=None)
            yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
            r2=1-ssr/sst if sst>0 else 0
            sigma2=ssr/(n-4) if n>4 else np.nan
            XtX_inv=np.linalg.inv(X.T@X)
            se_b=sigma2*XtX_inv[1,1]  # variance, not SE — for EB shrinkage
            res.append({"PERMNO":pn,"beta_uk":b[1],"n":n,"r2":r2,"se2":se_b})
        except: continue
    betas=pd.DataFrame(res).merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
    betas=betas.drop_duplicates(subset=["gvkey"],keep="first")
    return betas

betas_full = est_betas(fv, macro)
betas_h1 = est_betas(fv, macro, ym_start=HALF1_END)
betas_h2 = est_betas(fv, macro, ym_end=HALF2_START)
print(f"  Full: {len(betas_full):,}  H1: {len(betas_h1):,}  H2: {len(betas_h2):,}")

# ============================================================
# 5. MERGE FIC-100 + EB SHRINKAGE
# ============================================================
print("5. EB shrinkage to FIC-100 industry mean")

def apply_shrinkage(betas_df, label):
    """Apply EB shrinkage to FIC-100 industry mean. Returns DataFrame with shrunk betas."""
    bt = betas_df.merge(fic_map, on="gvkey", how="inner")
    bt = bt.dropna(subset=["se2"])
    # Industry means (raw)
    ind_mean = bt.groupby("icode100")["beta_uk"].mean()
    ind_var = bt.groupby("icode100")["beta_uk"].var()
    # τ² = between-industry variance of true betas
    tau2 = max(ind_mean.var() - bt["se2"].mean(), 0.01)  # floor at 0.01 to avoid zero
    bt["ind_mean"] = bt["icode100"].map(ind_mean)
    # Shrinkage weight: w = se2 / (se2 + tau2)
    bt["shrink_w"] = bt["se2"] / (bt["se2"] + tau2)
    bt["beta_shrunk"] = bt["beta_uk"] - bt["shrink_w"] * (bt["beta_uk"] - bt["ind_mean"])
    # Within-industry residual (for firewall)
    bt["beta_resid"] = bt["beta_uk"] - bt["ind_mean"]
    return bt

betas_full_s = apply_shrinkage(betas_full, "FULL")
betas_h1_s = apply_shrinkage(betas_h1, "H1")
betas_h2_s = apply_shrinkage(betas_h2, "H2")

# ============================================================
# 6. GATE NUMBERS: neg%, cutpoints, H/L
# ============================================================
print(f"\n{'='*60}")
print("6. GATE: RAW vs SHRUNK")
print(f"{'='*60}")

def tercile_stats(bt, beta_col="beta_uk"):
    bp=bt[bt[beta_col]>=0]; bn=bt[bt[beta_col]<0]
    neg_pct=len(bn)/len(bt)*100
    if len(bp)>=3:
        t1,t2=bp[beta_col].quantile(1/3),bp[beta_col].quantile(2/3)
        hi=(bt[beta_col]>=t2).sum(); lo=((bt[beta_col]>=0)&(bt[beta_col]<=t1)).sum()
    else: t1,t2,hi,lo=np.nan,np.nan,0,0
    return len(bt),neg_pct,t1,t2,hi,lo

for label, bt, col in [("RAW", betas_full, "beta_uk"), ("SHRUNK", betas_full_s, "beta_shrunk")]:
    n,nn,t1,t2,hi,lo = tercile_stats(bt, col)
    vals=bt[col]; abs_t=bt.get("abs_t", pd.Series(np.nan, index=bt.index))
    med=vals.median()
    print(f"  {label:>7}: N={n:,} Neg={nn:.1f}% T1={t1:.4f} T2={t2:.4f} H={hi:,} L={lo:,}  p50={med:.4f}")
    # Show industry means distribution
    if col == "beta_shrunk":
        ind_means_shrunk = bt.groupby("icode100")[col].mean()
        print(f"           Industry means: p10={ind_means_shrunk.quantile(0.1):.4f} p50={ind_means_shrunk.median():.4f} p90={ind_means_shrunk.quantile(0.9):.4f}")

print(f"  Paper:   N~1,428 Neg<=20% T1=0.28 T2=0.68 H=449 L=360")

# ============================================================
# 7. CF RANK CORRELATION (raw vs shrunk)
# ============================================================
print(f"\n{'='*60}")
print("7. CF RANK CORRELATION")
print(f"{'='*60}")

# CF pipeline (per-firm VAR, same as before)
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

def cf_rank(bt, beta_col):
    common=set(bt["gvkey"])&set(betas_cf["gvkey"])
    if len(common)<30: return np.nan, np.nan, len(common)
    bl=bt[bt["gvkey"].isin(common)].set_index("gvkey")[beta_col]
    bc=betas_cf[betas_cf["gvkey"].isin(common)].set_index("gvkey")["beta_cf"]
    rc=bl.rank().corr(bc.rank())
    bl_p=bl[bl>=0]; bc_p=bc[bc>=0]
    if len(bl_p)<3 or len(bc_p)<3: return rc, np.nan, len(common)
    t2l=bl_p.quantile(2/3); t2c=bc_p.quantile(2/3)
    hl=set(bl_p[bl_p>=t2l].index); hc=set(bc_p[bc_p>=t2c].index)
    overlap=len(hl&hc)/max(len(hl|hc),1)
    return rc, overlap, len(common)

rc_raw,ov_raw,cm_raw = cf_rank(betas_full, "beta_uk")
rc_shr,ov_shr,cm_shr = cf_rank(betas_full_s, "beta_shrunk")
print(f"  RAW vs CF:     rank_corr={rc_raw:.4f}  overlap={ov_raw:.3f}  N={cm_raw:,}")
print(f"  SHRUNK vs CF:  rank_corr={rc_shr:.4f}  overlap={ov_shr:.3f}  N={cm_shr:,}")
print(f"  Paper:         rank_corr=0.80  overlap=0.86")

# ============================================================
# 8. SPLIT-HALF FIREWALL (raw vs shrunk)
# ============================================================
print(f"\n{'='*60}")
print("8. SPLIT-HALF FIREWALL: RAW vs SHRUNK")
print(f"{'='*60}")

def split_half_corr(bt_h1, bt_h2, beta_col):
    common=set(bt_h1["gvkey"])&set(bt_h2["gvkey"])
    b1=bt_h1[bt_h1["gvkey"].isin(common)].set_index("gvkey")[beta_col]
    b2=bt_h2[bt_h2["gvkey"].isin(common)].set_index("gvkey")[beta_col]
    rc=b1.rank().corr(b2.rank())
    return rc, len(common)

# RAW split-half
rc_sh_raw, n_sh_raw = split_half_corr(betas_h1, betas_h2, "beta_uk")
print(f"  RAW split-half:       rank_corr={rc_sh_raw:.4f}  N={n_sh_raw:,}")

# SHRUNK split-half
rc_sh_shrunk, n_sh_shrunk = split_half_corr(betas_h1_s, betas_h2_s, "beta_shrunk")
print(f"  SHRUNK split-half:    rank_corr={rc_sh_shrunk:.4f}  N={n_sh_shrunk:,}")

# RESIDUAL split-half (within-industry)
rc_sh_resid, n_sh_resid = split_half_corr(betas_h1_s, betas_h2_s, "beta_resid")
print(f"  RESIDUAL split-half:  rank_corr={rc_sh_resid:.4f}  N={n_sh_resid:,}")

# ============================================================
# 9. VERDICT
# ============================================================
print(f"\n{'='*60}")
print("VERDICT")
print(f"{'='*60}")

checks = []
checks.append(("CF→0.80", rc_shr, rc_shr >= 0.7 if not np.isnan(rc_shr) else False))
nfull,nn,t1,t2,hi,lo = tercile_stats(betas_full_s, "beta_shrunk")
checks.append(("T1→0.28", t1, 0.15 <= t1 <= 0.40))
checks.append(("T2→0.68", t2, 0.55 <= t2 <= 0.80))
checks.append(("Neg%→≤20%", nn, nn <= 25))
checks.append(("Split-half RISE", rc_sh_shrunk, rc_sh_shrunk > rc_sh_raw + 0.05 if not np.isnan(rc_sh_shrunk) else False))
checks.append(("Resid split-half >0", rc_sh_resid, rc_sh_resid > 0.05 if not np.isnan(rc_sh_resid) else False))

all_pass = all(p for _,_,p in checks)
print(f"\n  {'Check':<25} {'Value':>10} {'Pass':>6}")
print(f"  {'-'*25} {'-'*10} {'-'*6}")
for name, val, passed in checks:
    print(f"  {name:<25} {val:>10.4f} {'YES' if passed else 'NO  ':>6}")

print(f"\n  ALL PASS: {'YES' if all_pass else 'NO — see failures above'}")

if rc_sh_resid < 0.05:
    print(f"\n  RESIDUAL SPLIT-HALF ≈ 0 ({rc_sh_resid:.4f}):")
    print(f"  Shrinkage added ZERO firm-level signal beyond industry membership.")
    print(f"  Treatment assignment is essentially an industry sort.")
    print(f"  The paper's terciles are identifying industries, not firms.")
