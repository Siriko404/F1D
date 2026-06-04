"""Supervisor Task 11: Split-half β^UK — is UK exposure a real persistent firm attribute?"""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_HALF = 15, 24

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
# 3. DAILY RETURNS + MACRO VOL
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

# Macro vol per month
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
# 4. SPLIT-HALF β^UK ESTIMATION
# ============================================================
print("4. Split-half β^UK")
HALF1_END = "2012-07"  # 2010:M1–2012:M6
HALF2_START = "2012-08"  # 2012:M7–2014:M12

def estimate_betas(fv_df, macro_df, ym_cut_start=None, ym_cut_end=None):
    mg=fv_df.merge(macro_df,on="ym",how="inner")
    if ym_cut_start: mg=mg[mg["ym"]<=ym_cut_start]
    if ym_cut_end: mg=mg[mg["ym"]>=ym_cut_end]
    res=[]
    for pn,grp in mg.groupby("PERMNO"):
        grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
        if len(grp)<MIN_HALF: continue
        yv=grp["vol_r"].values; n=len(yv)
        X=np.column_stack([np.ones(n),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
        try:
            b=np.linalg.lstsq(X,yv,rcond=None)[0]
            res.append({"PERMNO":pn,"beta_uk":b[1],"n":n})
        except: continue
    betas=pd.DataFrame(res)
    betas=betas.merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
    betas=betas.drop_duplicates(subset=["gvkey"],keep="first")
    return betas

# FULL SAMPLE (reference)
betas_full = estimate_betas(fv, macro)
print(f"  Full sample: {len(betas_full):,} firms")

# HALF 1: 2010:M1–2012:M6
betas_h1 = estimate_betas(fv, macro, ym_cut_start=HALF1_END)
print(f"  Half 1 (2010:M1–2012:M6): {len(betas_h1):,} firms")

# HALF 2: 2012:M7–2014:M12
betas_h2 = estimate_betas(fv, macro, ym_cut_end=HALF2_START)
print(f"  Half 2 (2012:M7–2014:M12): {len(betas_h2):,} firms")

# ============================================================
# 5. SPLIT-HALF RANK CORRELATION
# ============================================================
print(f"\n{'='*60}")
print("5. SPLIT-HALF RANK CORRELATION")
print(f"{'='*60}")

common_half = set(betas_h1["gvkey"]) & set(betas_h2["gvkey"])
b1 = betas_h1[betas_h1["gvkey"].isin(common_half)].set_index("gvkey")["beta_uk"]
b2 = betas_h2[betas_h2["gvkey"].isin(common_half)].set_index("gvkey")["beta_uk"]

rc_half = b1.rank().corr(b2.rank())
pc_half = b1.corr(b2)

print(f"  Common firms: {len(common_half):,}")
print(f"  Rank correlation (split-half): {rc_half:.4f}")
print(f"  Pearson correlation: {pc_half:.4f}")

# Distribution comparison
print(f"\n  Half 1 distribution:")
print(f"    N={len(betas_h1):,}  Neg={(betas_h1['beta_uk']<0).mean()*100:.1f}%  p50={betas_h1['beta_uk'].median():.4f}")
print(f"\n  Half 2 distribution:")
print(f"    N={len(betas_h2):,}  Neg={(betas_h2['beta_uk']<0).mean()*100:.1f}%  p50={betas_h2['beta_uk'].median():.4f}")

# Also compare with full sample
common_all = set(betas_full["gvkey"]) & common_half
bf = betas_full[betas_full["gvkey"].isin(common_all)].set_index("gvkey")["beta_uk"]
b1c = b1[b1.index.isin(common_all)]
b2c = b2[b2.index.isin(common_all)]
rc_f1 = bf.rank().corr(b1c.rank())
rc_f2 = bf.rank().corr(b2c.rank())
print(f"\n  Full vs Half1 rank_corr: {rc_f1:.4f}")
print(f"  Full vs Half2 rank_corr: {rc_f2:.4f}")

# Decisive test
print(f"\n{'='*60}")
if rc_half < 0.1:
    print("SPLIT-HALF ≈ 0: Firm-level β^UK NOT a recoverable attribute from OLS.")
    print("Paper CANNOT be using raw firm-by-firm OLS. Must be structured/shrunk.")
elif rc_half < 0.4:
    print(f"SPLIT-HALF = {rc_half:.4f}: Weak but nonzero signal. Some real UK exposure.")
    print("β^UK partially identifiable. Shrinkage may help but won't fully rescue.")
else:
    print(f"SPLIT-HALF = {rc_half:.4f}: Real signal. UK exposure is a persistent firm attribute.")
    print("Raw OLS has signal; noise reduction (shrinkage) should substantially improve it.")

# Show the top tercile overlap between halves (same logic as paper's CF check)
b1p=b1[b1>=0]; b2p=b2[b2>=0]
if len(b1p)>=3 and len(b2p)>=3:
    t2_1=b1p.quantile(2/3); t2_2=b2p.quantile(2/3)
    h1_top=set(b1p[b1p>=t2_1].index)
    h2_top=set(b2p[b2p>=t2_2].index)
    overlap=len(h1_top&h2_top)/max(len(h1_top|h2_top),1)
    print(f"\n  Top-tercile overlap (H1 vs H2): {overlap:.3f} ({overlap*100:.1f}%)")
    print(f"  Paper: top-tercile overlap (β^UK vs β^UK_CF) = 0.86")
