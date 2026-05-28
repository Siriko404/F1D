"""Supervisor Q-A: Quantify firm-month vol corruption + trace PERMNO 13643."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS = 15

# Survivors
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

# Daily returns
frames=[]
for y in range(2010,2015):
    for q in range(1,5):
        f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df=pd.read_parquet(f)
            df=df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames.append(df)
cr=pd.concat(frames); cr["date"]=pd.to_datetime(cr["date"])
cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce")
cr["ym"]=cr["date"].dt.to_period("M")

# PART A: Firm-month vol distribution
g=cr.groupby(["PERMNO","ym"])
fv=g["RET"].std()
fv=fv[g["RET"].count()>=MIN_DAYS].reset_index(); fv.columns=["PERMNO","ym","vol_r"]

print("PART A: Firm-month vol distribution")
print("="*60)
vols=fv["vol_r"].dropna()
for q_val in [0,0.01,0.05,0.10,0.25,0.50,0.75,0.90,0.95,0.99,0.999,1.0]:
    v=vols.quantile(q_val)
    if q_val<0.01: print(f"  min: {v:.6f}")
    elif q_val>=0.999: print(f"  max: {v:.6f}")
    else: print(f"  p{q_val*100:4.0f}: {v:.6f}")

print()
v015=(vols>0.15).sum(); v010=(vols>0.10).sum()
print(f"Firm-months vol > 0.15: {v015:,} ({v015/len(vols)*100:.2f}%)")
print(f"Firm-months vol > 0.10: {v010:,} ({v010/len(vols)*100:.2f}%)")

firm_max_vol=fv.groupby("PERMNO")["vol_r"].max()
firms_poison_015=(firm_max_vol>0.15).sum()
firms_poison_010=(firm_max_vol>0.10).sum()
total_firms=fv["PERMNO"].nunique()
print(f"\nFirms with >=1 month vol>0.15: {firms_poison_015:,} ({firms_poison_015/total_firms*100:.1f}%)")
print(f"Firms with >=1 month vol>0.10: {firms_poison_010:,} ({firms_poison_010/total_firms*100:.1f}%)")
print(f"Total firms: {total_firms:,}")

print(f"\nTop 30 worst firm-month vols:")
for _,r in fv.nlargest(30,"vol_r").iterrows():
    print(f"  PERMNO={int(r['PERMNO']):6d}  {str(r['ym'])}  vol={r['vol_r']:.6f}")

# PART E: SP500 slopes outside [-1, 4]
print(f"\nPART E: SP500 slopes outside [-1, 4]")
sp=cr[["date","sprtrn","ym"]].drop_duplicates()
sp500=sp.groupby("ym")["sprtrn"].std()
sp500=sp500[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp500.columns=["ym","vol_SP500"]; sp500["ym_str"]=sp500["ym"].astype(str)
fv["ym_str"]=fv["ym"].astype(str)
mg=fv.merge(sp500[["ym_str","vol_SP500"]],on="ym_str",how="inner")

lo=0; hi=0; slopes2=[]
for pn,grp in mg.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r","vol_SP500"])
    if len(grp)<24: continue
    X=np.column_stack([np.ones(len(grp)),grp["vol_SP500"].values])
    try:
        b=np.linalg.lstsq(X,grp["vol_r"].values,rcond=None)[0]; slopes2.append(b[1])
        if b[1]<-1: lo+=1
        if b[1]>4: hi+=1
    except: continue
print(f"SP500 slope < -1: {lo}  |  SP500 slope > 4: {hi}")
print(f"Outside [-1, 4]: {lo+hi} of {len(slopes2)} ({(lo+hi)/len(slopes2)*100:.1f}%)")
