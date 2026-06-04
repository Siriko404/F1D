"""Supervisor merge fix: P-only CCM, date-range resolution, before/after comparison + CF-correlation."""
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
print(f"  Survivor gvkeys: {len(survivor_gvkeys):,}")

# ============================================================
# 2. CCM MERGE — BEFORE vs AFTER
# ============================================================
print("\n2. CCM MERGE COMPARISON")

# Load CCM
ccm_raw=pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
    columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm_raw["gvkey"]=ccm_raw["gvkey"].astype(str).str.zfill(6)
ccm_raw=ccm_raw[ccm_raw["gvkey"].isin(survivor_gvkeys)]

def build_ccm_before():
    """OLD: P+C, date filter, arbitrary dedup."""
    c=ccm_raw.copy()
    c=c[c["LINKTYPE"].isin(["LU","LC"])]; c=c[c["LINKPRIM"].isin(["P","C"])]
    c["LINKDT"]=pd.to_datetime(c["LINKDT"],errors="coerce"); c["LINKENDDT"]=pd.to_datetime(c["LINKENDDT"],errors="coerce")
    c["LINKENDDT"]=c["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
    c=c[(c["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(c["LINKDT"]<=pd.Timestamp("2014-12-31"))]
    c["LPERMNO"]=pd.to_numeric(c["LPERMNO"],errors="coerce").astype("Int64"); c=c.dropna(subset=["LPERMNO"])
    per_gv=c.groupby("gvkey")["LPERMNO"].apply(list)
    multi=(per_gv.apply(len)>1).sum()
    # Dedup: keep first
    c=c.sort_values(["gvkey","LINKDT"]).drop_duplicates(subset=["gvkey"],keep="first")
    return c, multi

def build_ccm_after():
    """NEW: P-only, date-range resolution for multi-PERMNO survivors."""
    c=ccm_raw.copy()
    c=c[c["LINKTYPE"].isin(["LU","LC"])]; c=c[c["LINKPRIM"]=="P"]  # P-only
    c["LINKDT"]=pd.to_datetime(c["LINKDT"],errors="coerce"); c["LINKENDDT"]=pd.to_datetime(c["LINKENDDT"],errors="coerce")
    c["LINKENDDT"]=c["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
    # Keep links active during 2010-01-01 to 2014-12-31
    c=c[(c["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(c["LINKDT"]<=pd.Timestamp("2014-12-31"))]
    c["LPERMNO"]=pd.to_numeric(c["LPERMNO"],errors="coerce").astype("Int64"); c=c.dropna(subset=["LPERMNO"])

    per_gv=c.groupby("gvkey")["LPERMNO"].apply(list)
    multi_per_gv=per_gv[per_gv.apply(len)>1]
    multi=len(multi_per_gv)

    # For GVKEYs with >1 PERMNO: pick the one whose LINKDT-LINKENDDT covers most of 2010-2014
    resolved=[]
    for gk,grp in c.groupby("gvkey"):
        if len(grp)==1:
            resolved.append(grp.iloc[0])
        else:
            # Score each link by overlap with [2010-01, 2014-12]
            best_overlap=-1; best_row=None
            for _,row in grp.iterrows():
                start=max(row["LINKDT"],pd.Timestamp("2010-01-01"))
                end=min(row["LINKENDDT"],pd.Timestamp("2014-12-31"))
                overlap=(end-start).days
                if overlap>best_overlap:
                    best_overlap=overlap; best_row=row
            resolved.append(best_row)
    c=pd.DataFrame(resolved)

    per_gv_after=c.groupby("gvkey")["LPERMNO"].nunique()
    max_nunique=per_gv_after.max()
    return c, multi, max_nunique

ccm_before, multi_before = build_ccm_before()
ccm_after, multi_after, max_nunique_after = build_ccm_after()

print(f"  BEFORE (P+C, first): {len(ccm_before):,} GVKEYs, {multi_before} with >1 PERMNO")
print(f"  AFTER  (P-only, date-resolved): {len(ccm_after):,} GVKEYs, {multi_after} with >1 PERMNO")
print(f"  AFTER max PERMNO per GVKEY: {max_nunique_after} (must be 1)")

lost_gvkeys=set(ccm_before["gvkey"])-set(ccm_after["gvkey"])
gained_gvkeys=set(ccm_after["gvkey"])-set(ccm_before["gvkey"])
print(f"  Lost GVKEYs: {len(lost_gvkeys)} (had C-link in old, now gone)")
print(f"  Gained GVKEYs: {len(gained_gvkeys)} (P-only dedup resolved differently)")

# ============================================================
# 3. MACRO VOL
# ============================================================
print("\n3. Macro vol")
# Load returns for BOTH PERMNO sets
def load_returns(permno_set):
    frames=[]
    for y in range(2010,2015):
        for q in range(1,5):
            f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
            if f.exists():
                df=pd.read_parquet(f,columns=["PERMNO","date","RET","sprtrn"])
                df=df[df["PERMNO"].isin(permno_set)]
                if len(df)>0: frames.append(df)
    cr=pd.concat(frames); cr["date"]=pd.to_datetime(cr["date"])
    cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce"); cr["sprtrn"]=pd.to_numeric(cr["sprtrn"],errors="coerce")
    return cr

permnos_before=set(ccm_before["LPERMNO"].unique())
permnos_after=set(ccm_after["LPERMNO"].unique())
print(f"  PERMNOs before: {len(permnos_before):,}  after: {len(permnos_after):,}")

# Load once for the union
all_permnos=permnos_before|permnos_after
cr_all=load_returns(all_permnos)

# Macro vol (same for both)
sp=cr_all[["date","sprtrn"]].drop_duplicates()
sp["ym"]=sp["date"].dt.to_period("M")
sp500=sp.groupby("ym")["sprtrn"].std()
sp500=sp500[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp500.columns=["ym","vol_SP500"]; sp500["ym_str"]=sp500["ym"].astype(str)

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M")
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
ftv.columns=["ym","vol_FTSE100"]; ftv["ym_str"]=ftv["ym"].astype(str)

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M")
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
fxv.columns=["ym","vol_FX"]; fxv["ym_str"]=fxv["ym"].astype(str)

macro=sp500[["ym_str","vol_SP500"]].merge(ftv[["ym_str","vol_FTSE100"]],on="ym_str").merge(fxv[["ym_str","vol_FX"]],on="ym_str")

# ============================================================
# 4. BETA ESTIMATION — BEFORE vs AFTER
# ============================================================
print("\n4. Beta estimation")

def estimate_betas(crf, ccm_df):
    """Build firm vol + estimate eq(13) betas."""
    # Firm monthly vol
    crf["ym"]=crf["date"].dt.to_period("M").astype(str)
    g=crf.groupby(["PERMNO","ym"])
    fv=g["RET"].std()
    fv=fv[g["RET"].count()>=MIN_DAYS].reset_index()
    fv.columns=["PERMNO","ym","vol_r"]

    mg=fv.merge(macro,left_on="ym",right_on="ym_str",how="inner")
    res=[]
    for pn,grp in mg.groupby("PERMNO"):
        grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
        if len(grp)<MIN_MONTHS: continue
        yv=grp["vol_r"].values
        X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
        try:
            b=np.linalg.lstsq(X,yv,rcond=None)[0]; yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
            res.append({"PERMNO":pn,"beta_uk":b[1],"n":len(grp),"r2":1-ssr/sst if sst>0 else 0})
        except: continue
    betas=pd.DataFrame(res)
    betas=betas.merge(ccm_df[["gvkey","LPERMNO"]].drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
    # After P-only date-resolved merge, should be 1:1
    # But keep dedup just in case
    betas=betas.drop_duplicates(subset=["gvkey"],keep="first")
    return betas

def report(label, betas):
    bpos=betas[betas["beta_uk"]>=0]; bneg=betas[betas["beta_uk"]<0]
    neg_pct=len(bneg)/len(betas)*100
    if len(bpos)>=3:
        t1,t2=bpos["beta_uk"].quantile(1/3),bpos["beta_uk"].quantile(2/3)
        hi=(betas["beta_uk"]>=t2).sum(); lo=((betas["beta_uk"]>=0)&(betas["beta_uk"]<=t1)).sum()
    else: t1,t2,hi,lo=np.nan,np.nan,0,0
    print(f"  {label}: N={len(betas):,} Neg={len(bneg):,} ({neg_pct:.1f}%) T1={t1:.4f} T2={t2:.4f} H={hi:,} L={lo:,}")
    print(f"    Median beta_uk={betas['beta_uk'].median():.4f} Mean={betas['beta_uk'].mean():.4f}")
    return {"n":len(betas),"neg_pct":neg_pct,"t1":t1,"t2":t2,"hi":hi,"lo":lo}

# BEFORE
cr_before=cr_all[cr_all["PERMNO"].isin(permnos_before)]
betas_before=estimate_betas(cr_before, ccm_before)
bs_before=report("BEFORE (P+C, first)", betas_before)

# AFTER
cr_after=cr_all[cr_all["PERMNO"].isin(permnos_after)]
betas_after=estimate_betas(cr_after, ccm_after)
bs_after=report("AFTER  (P-only, date-resolved)", betas_after)

# ============================================================
# 5. CF-BETA RANK CORRELATION — BEFORE vs AFTER
# ============================================================
print("\n5. CF-beta rank correlation")

# CF beta pipeline (same as diag_supervisor_2and3.py)
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

# Quarterly returns for all PERMNOs
cr_q=load_returns(all_permnos)  # same function, 2010-2014 only
# Need 2002-2018 for CF
def load_crsp_wide(permno_set):
    frames=[]
    for y in range(2002,2019):
        for q in range(1,5):
            f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
            if f.exists():
                df=pd.read_parquet(f,columns=["PERMNO","date","RET"])
                df=df[df["PERMNO"].isin(permno_set)]
                if len(df)>0: frames.append(df)
    cr=pd.concat(frames); cr["date"]=pd.to_datetime(cr["date"])
    cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce")
    return cr

cr_q_wide=load_crsp_wide(all_permnos)
cr_q_wide["yq"]=cr_q_wide["date"].dt.year*10+cr_q_wide["date"].dt.quarter
cr_q_wide["lr"]=np.log(1+cr_q_wide["RET"].fillna(0))
qr=cr_q_wide.groupby(["PERMNO","yq"])["lr"].sum().reset_index()
qr.columns=["PERMNO","yq","r_q"]

# Use the AFTER CCM for the CF merge (cleaner)
qr=qr.merge(ccm_after[["gvkey","LPERMNO"]].drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
qr=qr.drop_duplicates(subset=["gvkey","yq"],keep="first"); qr["gvkey"]=qr["gvkey"].astype(str).str.zfill(6)

qdf=comp_qv.merge(qr[["gvkey","yq","r_q"]],on=["gvkey","yq"],how="inner")
qdf=qdf.sort_values(["gvkey","yq"])

# CF news extraction
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
print(f"  CF VAR firms: {cf_df['gvkey'].nunique():,}")

# CF betas
cf_data=cf_monthly.merge(macro,left_on="ym",right_on="ym_str",how="inner")
cf_data=cf_data[(cf_data["ym"]>="2010-01")&(cf_data["ym"]<="2014-12")]
cf_betas_dict={}
for gk,grp in cf_data.groupby("gvkey"):
    grp=grp.dropna(subset=["vol_cf","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_cf"].values; X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try:
        b=np.linalg.lstsq(X,yv,rcond=None)[0]
        cf_betas_dict[gk]=b[1]
    except: continue
betas_cf=pd.DataFrame(list(cf_betas_dict.items()),columns=["gvkey","beta_cf"])
print(f"  CF betas: {len(betas_cf):,} firms")

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

cf_compare("BEFORE", betas_before)
cf_compare("AFTER", betas_after)
print(f"\n  Paper: rank_corr=0.80  top-tercile overlap=0.86")

# ============================================================
# 6. SUMMARY
# ============================================================
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"  BEFORE: N={bs_before['n']:,} Neg={bs_before['neg_pct']:.1f}% T1={bs_before['t1']:.4f} T2={bs_before['t2']:.4f} H={bs_before['hi']:,} L={bs_before['lo']:,}")
print(f"  AFTER:  N={bs_after['n']:,} Neg={bs_after['neg_pct']:.1f}% T1={bs_after['t1']:.4f} T2={bs_after['t2']:.4f} H={bs_after['hi']:,} L={bs_after['lo']:,}")
print(f"  Paper target: N=809  Neg<=20%  T1=0.28 T2=0.68  H=449 L=360")
