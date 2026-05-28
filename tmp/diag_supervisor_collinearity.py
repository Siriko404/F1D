"""Supervisor collinearity audit: nested regressions + day counts + vol construction."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT=Path("."); CSV=ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet"
MIN_DAYS,MIN_MONTHS=15,24

# Survivors
comp=pd.read_parquet(CSV,columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
for c in ["atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]: comp[c]=pd.to_numeric(comp[c],errors="coerce")
comp["txditcq"]=comp["txditcq"].fillna(0); comp["gvkey"]=comp["gvkey"].astype(str).str.zfill(6)
comp=comp[(comp["fyearq"]>=2010)&(comp["fyearq"]<=2016)]; comp=comp[comp["fqtr"].isin([1,2,3,4])]
comp=comp[(comp["curcdq"]=="USD")&(comp["fic"]=="USA")]; comp=comp[(comp["atq"]>0)&(comp["saleq"]>0)]
csic=pd.to_numeric(comp["sic"],errors="coerce"); comp=comp[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp["mktcap"]=comp["cshoq"]*comp["prccq"]; comp=comp[(comp["atq"]>=10)&(comp["mktcap"]>=10)]
comp["atq_l1"]=comp.groupby("gvkey")["atq"].shift(1); comp["saleq_l4"]=comp.groupby("gvkey")["saleq"].shift(4)
hi=comp["capxy"].notna()&comp["atq_l1"].notna(); hc=comp["oibdpq"].notna()&comp["atq_l1"].notna()
hq=comp["cshoq"].notna()&comp["prccq"].notna()&comp["atq"].notna()&comp["ceqq"].notna()
hs=comp["saleq"].notna()&comp["saleq_l4"].notna()
comp=comp[hi&comp["atq"].notna()&hc&hq&hs]
comp=comp.sort_values(["gvkey","fyearq","fqtr"]); comp["cyq"]=comp["fyearq"].astype(int)*10+comp["fqtr"].astype(int)
rows=[]
for gk,grp in comp.groupby("gvkey"):
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
comp=pd.concat(rows,ignore_index=True)
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f: fic=pd.read_csv(io.BytesIO(f.read()),sep="\t",usecols=["gvkey","year","icode100"])
fic["gvkey"]=fic["gvkey"].astype(str).str.zfill(6); comp["year"]=comp["cyq"]//10
comp=comp.merge(fic,on=["gvkey","year"],how="inner")
survivor_gvkeys=set(comp["gvkey"].unique()); del comp

ccm=pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"]=ccm["gvkey"].astype(str).str.zfill(6); ccm=ccm[ccm["LINKTYPE"].isin(["LU","LC"])]; ccm=ccm[ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"]=pd.to_datetime(ccm["LINKDT"],errors="coerce"); ccm["LINKENDDT"]=pd.to_datetime(ccm["LINKENDDT"],errors="coerce")
ccm["LINKENDDT"]=ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm=ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(ccm["LINKDT"]<=pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"]=pd.to_numeric(ccm["LPERMNO"],errors="coerce").astype("Int64"); ccm=ccm.dropna(subset=["LPERMNO"])
ccm_surv=ccm[ccm["gvkey"].isin(survivor_gvkeys)]; survivor_permnos=set(ccm_surv["LPERMNO"].unique())

# Daily returns
frames=[]
for y in range(2010,2015):
    for q in range(1,5):
        f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df=pd.read_parquet(f,columns=["PERMNO","date","RET","sprtrn"])
            df=df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames.append(df)
cr=pd.concat(frames); cr["date"]=pd.to_datetime(cr["date"])
cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce"); cr["sprtrn"]=pd.to_numeric(cr["sprtrn"],errors="coerce")
cr["ym"]=cr["date"].dt.to_period("M").astype(str)

# Firm monthly vol
g=cr.groupby(["PERMNO","ym"])
fv=g["RET"].std()
fv=fv[g["RET"].count()>=MIN_DAYS].reset_index(); fv.columns=["PERMNO","ym","vol_r"]

# SP500 vol
sp=cr[["date","sprtrn","ym"]].drop_duplicates()
sp500=sp.groupby("ym")["sprtrn"].std()
n_sp=sp.groupby("ym")["sprtrn"].count()
sp500=sp500[n_sp>=MIN_DAYS].reset_index(); sp500.columns=["ym","vol_SP500"]

# FTSE vol
ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"])
ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")]
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M").astype(str)
ftv=ftse.groupby("ym")["lr"].std()
n_ft=ftse.groupby("ym")["lr"].count()
ftv=ftv[n_ft>=MIN_DAYS].reset_index(); ftv.columns=["ym","vol_FTSE100"]

# FX vol
fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True)
fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")]
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M").astype(str)
fxv=fx.groupby("ym")["lr"].std()
n_fx=fx.groupby("ym")["lr"].count()
fxv=fxv[n_fx>=MIN_DAYS].reset_index(); fxv.columns=["ym","vol_FX"]

macro_all=sp500.merge(ftv,on="ym").merge(fxv,on="ym")
sp_ft=sp500.merge(ftv,on="ym")

def nest_run(fv_df,macro_df,rhs_vars,label):
    neg=0;pos=0;betas=[]
    for pn,grp in fv_df.groupby("PERMNO"):
        mg=grp.merge(macro_df,on="ym",how="inner")
        mg=mg.dropna(subset=["vol_r"]+rhs_vars)
        if len(mg)<MIN_MONTHS: continue
        yv=mg["vol_r"].values
        X=mg[rhs_vars].values
        X=np.column_stack([np.ones(len(yv)),X])
        try:
            b=np.linalg.lstsq(X,yv,rcond=None)[0]
            betas.append(b[1])
            if b[1]<0: neg+=1
            else: pos+=1
        except: continue
    n=neg+pos
    print(f"{label}: N={n:,} Neg={neg} ({neg/n*100:.1f}%) Pos={pos} ({pos/n*100:.1f}%) Median b={np.median(betas):.4f} Mean b={np.mean(betas):.4f}")

# =====================================================
# #1: Nested regressions
# =====================================================
print("="*60)
print("#1: NESTED REGRESSIONS")
print("="*60)
nest_run(fv,sp_ft,["vol_FTSE100"],"(a) firm_vol ~ FTSE-vol ONLY")
nest_run(fv,sp_ft,["vol_FTSE100","vol_SP500"],"(b) firm_vol ~ FTSE-vol + SP500-vol")
nest_run(fv,macro_all,["vol_FTSE100","vol_SP500","vol_FX"],"(c) firm_vol ~ FTSE-vol + SP500-vol + FX-vol")

# =====================================================
# #2: Raw vol series stats
# =====================================================
print()
print("="*60)
print("#2: RAW VOL SERIES")
print("="*60)
ftse_vals=ftv["vol_FTSE100"].dropna()
sp_vals=sp500["vol_SP500"].dropna()
fx_vals=fxv["vol_FX"].dropna()
for label,vals in [("FTSE100 vol",ftse_vals),("SP500 vol",sp_vals),("FX vol",fx_vals)]:
    print(f"{label}: mean={vals.mean():.6f} SD={vals.std():.6f} p50={vals.median():.6f} p10={vals.quantile(0.1):.6f} p90={vals.quantile(0.9):.6f}")

ft_sp=pd.merge(ftv[["ym","vol_FTSE100"]],sp500[["ym","vol_SP500"]],on="ym")
corr=ft_sp["vol_FTSE100"].corr(ft_sp["vol_SP500"])
vr=ft_sp["vol_SP500"].var()/ft_sp["vol_FTSE100"].var()
print(f"\ncorr(FTSE-vol, SP500-vol) = {corr:.4f}")
print(f"Var(SP500)/Var(FTSE100) = {vr:.4f}")

# Show which covaries more: regress SP500 vol on FTSE vol
from numpy.linalg import lstsq
X=np.column_stack([np.ones(len(ft_sp)),ft_sp["vol_FTSE100"].values])
b_sp_on_ft=lstsq(X,ft_sp["vol_SP500"].values,rcond=None)[0]
print(f"SP500_vol = {b_sp_on_ft[0]:.4f} + {b_sp_on_ft[1]:.4f}*FTSE_vol")
# How many months is SP500 > FTSE?
higher=ft_sp[ft_sp["vol_SP500"]>ft_sp["vol_FTSE100"]]
print(f"Months where SP500 vol > FTSE vol: {len(higher)}/60 ({len(higher)/60*100:.0f}%)")

# =====================================================
# #3: Day counts
# =====================================================
print()
print("="*60)
print("#3: DAY COUNTS")
print("="*60)
for ym_label in ["2011-08","2012-12","2014-01"]:
    print(f"\n{ym_label}:")
    sp_days=sp[sp["ym"]==ym_label]
    ft_days=ftse[ftse["ym"]==ym_label]
    fx_days=fx[fx["ym"]==ym_label]
    print(f"  SP500: {len(sp_days)} days  (from CRSP sprtrn)")
    print(f"  FTSE100: {len(ft_days)} days  (from Yahoo CSV)")
    print(f"  FX USD/GBP: {len(fx_days)} days  (from BoE CSV)")
    if len(sp_days)>0 and len(ft_days)>0:
        print(f"  SP500 vol={sp_days['sprtrn'].std():.6f}  FTSE vol={ft_days['lr'].std():.6f}  FX vol={fx_days['lr'].std():.6f}")

# Full day-count distribution
print(f"\nDay-count distribution across all 60 months:")
for label,s in [("SP500",n_sp),("FTSE100",n_ft),("FX",n_fx)]:
    vals=s.dropna().astype(int)
    print(f"  {label}: min={vals.min()} p10={vals.quantile(0.1):.0f} p50={vals.median():.0f} p90={vals.quantile(0.9):.0f} max={vals.max()} mean={vals.mean():.1f}")
