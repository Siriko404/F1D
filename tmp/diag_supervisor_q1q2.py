"""Claude supervisor Q1+Q2: SP500-only slope sanity check + raw input matrices."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24

# Survivor list (same as run_did_fix1.py)
comp_raw = pd.read_parquet(CSV, columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
for c in ["atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]: comp_raw[c]=pd.to_numeric(comp_raw[c],errors="coerce")
comp_raw["txditcq"]=comp_raw["txditcq"].fillna(0); comp_raw["gvkey"]=comp_raw["gvkey"].astype(str).str.zfill(6)
comp_raw=comp_raw[(comp_raw["fyearq"]>=2010)&(comp_raw["fyearq"]<=2016)]; comp_raw=comp_raw[comp_raw["fqtr"].isin([1,2,3,4])]
comp_raw=comp_raw[(comp_raw["curcdq"]=="USD")&(comp_raw["fic"]=="USA")]; comp_raw=comp_raw[(comp_raw["atq"]>0)&(comp_raw["saleq"]>0)]
csic=pd.to_numeric(comp_raw["sic"],errors="coerce"); comp_raw=comp_raw[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp_raw["mktcap"]=comp_raw["cshoq"]*comp_raw["prccq"]; comp_raw=comp_raw[(comp_raw["atq"]>=10)&(comp_raw["mktcap"]>=10)]
comp_raw["atq_l1"]=comp_raw.groupby("gvkey")["atq"].shift(1); comp_raw["saleq_l4"]=comp_raw.groupby("gvkey")["saleq"].shift(4)
has_inv=comp_raw["capxy"].notna()&comp_raw["atq_l1"].notna(); has_cf=comp_raw["oibdpq"].notna()&comp_raw["atq_l1"].notna()
has_q=comp_raw["cshoq"].notna()&comp_raw["prccq"].notna()&comp_raw["atq"].notna()&comp_raw["ceqq"].notna()
has_sg=comp_raw["saleq"].notna()&comp_raw["saleq_l4"].notna()
comp_raw=comp_raw[has_inv&comp_raw["atq"].notna()&has_cf&has_q&has_sg]
comp_raw=comp_raw.sort_values(["gvkey","fyearq","fqtr"]); comp_raw["cyq"]=comp_raw["fyearq"].astype(int)*10+comp_raw["fqtr"].astype(int)
res_rows=[]
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
    if runs and len(best)>=12: res_rows.append(grp.loc[best])
comp_raw=pd.concat(res_rows,ignore_index=True)
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
            df=pd.read_parquet(f,columns=["PERMNO","date","RET","sprtrn"])
            df=df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames.append(df)
cr=pd.concat(frames); cr["date"]=pd.to_datetime(cr["date"])
cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce"); cr["sprtrn"]=pd.to_numeric(cr["sprtrn"],errors="coerce")
cr["ym"]=cr["date"].dt.to_period("M")

# Firm monthly vol
g=cr.groupby(["PERMNO","ym"])
fv=g["RET"].std()
fv=fv[g["RET"].count()>=MIN_DAYS].reset_index(); fv.columns=["PERMNO","ym","vol_r"]
fv["ym_str"]=fv["ym"].astype(str)

# Macro vol - ONCE, broadcast
sp=cr[["date","sprtrn","ym"]].drop_duplicates()
sp500=sp.groupby("ym")["sprtrn"].std()
sp500=sp500[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp500.columns=["ym","vol_SP500"]; sp500["ym_str"]=sp500["ym"].astype(str)

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"])
ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")]
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M")
ftv=ftse.groupby("ym")["lr"].std()
ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index(); ftv.columns=["ym","vol_FTSE100"]
ftv["ym_str"]=ftv["ym"].astype(str)

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True)
fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")]
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M")
fxv=fx.groupby("ym")["lr"].std()
fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index(); fxv.columns=["ym","vol_FX"]
fxv["ym_str"]=fxv["ym"].astype(str)

macro=sp500[["ym_str","vol_SP500"]].merge(ftv[["ym_str","vol_FTSE100"]],on="ym_str").merge(fxv[["ym_str","vol_FX"]],on="ym_str")

# =====================================================
# Q1: Regress firm vol on SP500 vol ONLY
# =====================================================
print("="*60)
print("Q1: Firm vol ~ SP500 vol (univariate)")
print("="*60)

merged=fv.merge(sp500[["ym_str","vol_SP500"]],on="ym_str",how="inner")
neg_count=0; pos_count=0; slopes=[]
for pn,grp in merged.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r","vol_SP500"])
    if len(grp)<MIN_MONTHS: continue
    X=np.column_stack([np.ones(len(grp)),grp["vol_SP500"].values])
    try:
        b=np.linalg.lstsq(X,grp["vol_r"].values,rcond=None)[0]
        slopes.append(b[1])
        if b[1]<0: neg_count+=1
        else: pos_count+=1
    except: continue

total=neg_count+pos_count
print(f"Firms: {total}")
print(f"Negative SP500 slopes: {neg_count} ({neg_count/total*100:.2f}%)")
print(f"Positive SP500 slopes: {pos_count} ({pos_count/total*100:.2f}%)")
print(f"Mean slope: {np.mean(slopes):.4f} Median: {np.median(slopes):.4f}")
print(f"Min: {np.min(slopes):.4f} Max: {np.max(slopes):.4f}")
print()
if neg_count/total>0.05:
    print("FAIL: >5% negative. Months likely MISALIGNED.")
else:
    print("PASS: <5% negative.")

# =====================================================
# Q2: Raw input matrices for two exemplar firms
# =====================================================
print()
print("="*60)
print("Q2: Raw input matrices")
print("="*60)

mg_all=fv.merge(macro,on="ym_str",how="inner")
betas=[]
for pn,grp in mg_all.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_r"].values
    X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try:
        b=np.linalg.lstsq(X,yv,rcond=None)[0]
        betas.append({"PERMNO":pn,"beta_uk":b[1],"beta_sp":b[2],"n":len(grp)})
    except: continue
betas_df=pd.DataFrame(betas).merge(ccm_surv[["gvkey","LPERMNO"]].drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
betas_df=betas_df.drop_duplicates(subset=["gvkey"],keep="first")

# Firm A: most negative beta
most_neg=betas_df.nsmallest(1,"beta_uk").iloc[0]
pn_a,ba=int(most_neg["PERMNO"]),most_neg["beta_uk"]
gk_a=most_neg["gvkey"]
print(f"\nFirm A - Most negative beta: PERMNO={pn_a} gvkey={gk_a} beta_uk={ba:.4f}")
a_data=fv[(fv["PERMNO"]==pn_a)][["ym_str","vol_r"]].merge(macro,on="ym_str",how="inner")
a_data=a_data.rename(columns={"ym_str":"ym","vol_r":"firm_vol","vol_FTSE100":"ftse_vol","vol_SP500":"sp500_vol","vol_FX":"fx_vol"})
a_data=a_data.sort_values("ym")
print(a_data[["ym","firm_vol","ftse_vol","sp500_vol","fx_vol"]].to_string(max_rows=65))

# Firm B: nearest to T2 cutpoint
bpos=betas_df[betas_df["beta_uk"]>=0]; t2=bpos["beta_uk"].quantile(2/3)
near_t2=betas_df.iloc[(betas_df["beta_uk"]-t2).abs().argsort()[:1]].iloc[0]
pn_b,bb=int(near_t2["PERMNO"]),near_t2["beta_uk"]
gk_b=near_t2["gvkey"]
print(f"\nFirm B - Near T2 cutpoint ({t2:.4f}): PERMNO={pn_b} gvkey={gk_b} beta_uk={bb:.4f}")
b_data=fv[(fv["PERMNO"]==pn_b)][["ym_str","vol_r"]].merge(macro,on="ym_str",how="inner")
b_data=b_data.rename(columns={"ym_str":"ym","vol_r":"firm_vol","vol_FTSE100":"ftse_vol","vol_SP500":"sp500_vol","vol_FX":"fx_vol"})
b_data=b_data.sort_values("ym")
print(b_data[["ym","firm_vol","ftse_vol","sp500_vol","fx_vol"]].to_string(max_rows=65))
