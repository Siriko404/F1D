"""Test: winsorization order + FE-inclusive R² check"""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path
from linearmodels.panel import PanelOLS

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24

# --- Rebuild entire pipeline (Fix 1 base) ---
# Compustat survivors
comp_raw = pd.read_parquet(CSV, columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
for c in ["atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]: comp_raw[c]=pd.to_numeric(comp_raw[c],errors="coerce")
comp_raw["txditcq"]=comp_raw["txditcq"].fillna(0); comp_raw["gvkey"]=comp_raw["gvkey"].astype(str).str.zfill(6)
comp_raw=comp_raw[(comp_raw["fyearq"]>=2010)&(comp_raw["fyearq"]<=2016)]; comp_raw=comp_raw[comp_raw["fqtr"].isin([1,2,3,4])]
comp_raw=comp_raw[(comp_raw["curcdq"]=="USD")&(comp_raw["fic"]=="USA")]; comp_raw=comp_raw[(comp_raw["atq"]>0)&(comp_raw["saleq"]>0)]
csic=pd.to_numeric(comp_raw["sic"],errors="coerce"); comp_raw=comp_raw[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp_raw["mktcap"]=comp_raw["cshoq"]*comp_raw["prccq"]; comp_raw=comp_raw[(comp_raw["atq"]>=10)&(comp_raw["mktcap"]>=10)]
comp_raw["atq_l1"]=comp_raw.groupby("gvkey")["atq"].shift(1); comp_raw["saleq_l4"]=comp_raw.groupby("gvkey")["saleq"].shift(4)
has_inv=comp_raw["capxy"].notna()&comp_raw["atq_l1"].notna()
has_cf=comp_raw["oibdpq"].notna()&comp_raw["atq_l1"].notna()
has_q=comp_raw["cshoq"].notna()&comp_raw["prccq"].notna()&comp_raw["atq"].notna()&comp_raw["ceqq"].notna()
has_sg=comp_raw["saleq"].notna()&comp_raw["saleq_l4"].notna()
comp_raw=comp_raw[has_inv&comp_raw["atq"].notna()&has_cf&has_q&has_sg]
comp_raw=comp_raw.sort_values(["gvkey","fyearq","fqtr"]); comp_raw["cal_yr_qtr"]=comp_raw["fyearq"].astype(int)*10+comp_raw["fqtr"].astype(int)
res_rows=[]
for gk,grp in comp_raw.groupby("gvkey"):
    grp=grp.sort_values("cal_yr_qtr"); runs,cur=[],[]
    for _,row in grp.iterrows():
        if not cur: cur=[row.name]
        else:
            pq=grp.loc[cur[-1],"cal_yr_qtr"]; tq=row["cal_yr_qtr"]; exp=pq+1
            if pq%10==4: exp=(pq//10+1)*10+1
            if tq==exp: cur.append(row.name)
            else: runs.append(cur); cur=[row.name]
    runs.append(cur)
    if runs: best=max(runs,key=len)
    if runs and len(best)>=12: res_rows.append(grp.loc[best])
comp_raw=pd.concat(res_rows,ignore_index=True) if res_rows else pd.DataFrame()
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f: fic=pd.read_csv(io.BytesIO(f.read()),sep="\t",usecols=["gvkey","year","icode100"])
fic["gvkey"]=fic["gvkey"].astype(str).str.zfill(6); comp_raw["year"]=comp_raw["cal_yr_qtr"]//10
comp_raw=comp_raw.merge(fic,on=["gvkey","year"],how="inner")
survivor_gvkeys=set(comp_raw["gvkey"].unique()); del comp_raw

# CCM
ccm=pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"]=ccm["gvkey"].astype(str).str.zfill(6); ccm=ccm[ccm["LINKTYPE"].isin(["LU","LC"])]; ccm=ccm[ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"]=pd.to_datetime(ccm["LINKDT"],errors="coerce"); ccm["LINKENDDT"]=pd.to_datetime(ccm["LINKENDDT"],errors="coerce")
ccm["LINKENDDT"]=ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm=ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(ccm["LINKDT"]<=pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"]=pd.to_numeric(ccm["LPERMNO"],errors="coerce").astype("Int64"); ccm=ccm.dropna(subset=["LPERMNO"])
ccm_surv=ccm[ccm["gvkey"].isin(survivor_gvkeys)]; survivor_permnos=set(ccm_surv["LPERMNO"].unique())

# Beta
frames,frames2=[],[]
for y in range(2010,2015):
    for q in range(1,5):
        f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df=pd.read_parquet(f,columns=["PERMNO","date","RET"]); df=df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames.append(df)
            df2=pd.read_parquet(f,columns=["PERMNO","date","RET","sprtrn"]); df2=df2[df2["PERMNO"].isin(survivor_permnos)]
            if len(df2)>0: frames2.append(df2)
crsp=pd.concat(frames,ignore_index=True); crsp["date"]=pd.to_datetime(crsp["date"]); crsp["RET"]=pd.to_numeric(crsp["RET"],errors="coerce")
crsp["ym"]=crsp["date"].dt.to_period("M"); g=crsp.groupby(["PERMNO","ym"]); rv=g["RET"].std()
rv=rv[g["RET"].count()>=MIN_DAYS].reset_index(); rv.columns=["PERMNO","ym","vol_r"]
cr2=pd.concat(frames2,ignore_index=True); cr2["date"]=pd.to_datetime(cr2["date"]); cr2["sprtrn"]=pd.to_numeric(cr2["sprtrn"],errors="coerce")
cr2["ym"]=cr2["date"].dt.to_period("M"); sp=cr2[["date","sprtrn","ym"]].drop_duplicates()
sp500=sp.groupby("ym")["sprtrn"].std(); sp500=sp500[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp500.columns=["ym","vol_SP500"]; del crsp,cr2,sp
ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M")
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index(); ftv.columns=["ym","vol_FTSE100"]
fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M")
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index(); fxv.columns=["ym","vol_FX"]
macro=sp500.merge(ftv,on="ym").merge(fxv,on="ym"); rv["ym"]=rv["ym"].astype(str); macro["ym"]=macro["ym"].astype(str)
mg=rv.merge(macro,on="ym",how="inner")
res=[]
for pn,grp in mg.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_r"].values; X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try: b=np.linalg.lstsq(X,yv,rcond=None)[0]; yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
    except: continue
    res.append({"PERMNO":pn,"beta_uk":b[1],"n":len(grp),"r2":1-ssr/sst if sst>0 else 0})
betas=pd.DataFrame(res)
betas=betas.merge(ccm_surv[["gvkey","LPERMNO"]].drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
betas=betas.drop_duplicates(subset=["gvkey"],keep="first"); betas["gvkey"]=betas["gvkey"].astype(str).str.zfill(6)
betas["HIGH"]=(betas["beta_uk"]>0.68).astype(int); betas["LOW"]=((betas["beta_uk"]>=0)&(betas["beta_uk"]<0.28)).astype(int)
print(f"Beta: {len(betas):,} firms, HIGH={betas['HIGH'].sum():,}, LOW={betas['LOW'].sum():,}")

# --- DiD panel with TWO CASH_DV methods ---
comp=pd.read_parquet(CSV,columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq","cheq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
for c in ["atq","saleq","cheq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]: comp[c]=pd.to_numeric(comp[c],errors="coerce")
comp["txditcq"]=comp["txditcq"].fillna(0); comp["gvkey"]=comp["gvkey"].astype(str).str.zfill(6)
comp=comp[(comp["fyearq"]>=2009)&(comp["fyearq"]<=2017)]; comp=comp[comp["fqtr"].isin([1,2,3,4])]
comp=comp[(comp["curcdq"]=="USD")&(comp["fic"]=="USA")]; comp=comp[(comp["atq"]>0)&(comp["saleq"]>0)]
csic=pd.to_numeric(comp["sic"],errors="coerce"); comp=comp[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp=comp[comp["atq"]>10]; comp=comp.sort_values(["gvkey","datadate"])
comp["atq_l1"]=comp.groupby("gvkey")["atq"].shift(1); comp["saleq_l4"]=comp.groupby("gvkey")["saleq"].shift(4)
comp["cal_yr_qtr"]=comp["fyearq"].astype(int)*10+comp["fqtr"].astype(int)
comp["f6"]=(comp[["capxy","atq","oibdpq"]].notna().all(axis=1)&comp[["cshoq","prccq","ceqq"]].notna().all(axis=1)&comp["saleq_l4"].notna())
comp_f6=comp[comp["f6"]].copy(); comp_f6=comp_f6.sort_values(["gvkey","cal_yr_qtr"])
res_rows=[]
for gk,grp in comp_f6.groupby("gvkey"):
    grp=grp.sort_values("cal_yr_qtr"); runs,cur=[],[]
    for _,row in grp.iterrows():
        if not cur: cur=[row.name]
        else:
            pq=grp.loc[cur[-1],"cal_yr_qtr"]; tq=row["cal_yr_qtr"]; exp=pq+1
            if pq%10==4: exp=(pq//10+1)*10+1
            if tq==exp: cur.append(row.name)
            else: runs.append(cur); cur=[row.name]
    runs.append(cur)
    if runs: best=max(runs,key=len)
    if runs and len(best)>=12: res_rows.append(grp.loc[best])
comp_f7=pd.concat(res_rows,ignore_index=True); comp_f7["year"]=comp_f7["cal_yr_qtr"]//10
comp_f7=comp_f7.merge(fic,on=["gvkey","year"],how="inner")
comp_f7=comp_f7[(comp_f7["fyearq"]>=2010)&(comp_f7["fyearq"]<=2016)]

comp_f7["CASH"]=comp_f7["cheq"]/comp_f7["atq_l1"]
comp_f7["CASH_w"]=comp_f7["CASH"].clip(comp_f7["CASH"].quantile(0.01),comp_f7["CASH"].quantile(0.99))
comp_f7["CASH_DV_M1"]=comp_f7["CASH_w"]/(1-comp_f7["CASH_w"])
comp_f7["CASH_DV_raw"]=comp_f7["CASH"]/(1-comp_f7["CASH"])
comp_f7["CASH_DV_M2"]=comp_f7["CASH_DV_raw"].clip(comp_f7["CASH_DV_raw"].quantile(0.01),comp_f7["CASH_DV_raw"].quantile(0.99))
comp_f7["SIZE"]=np.log(comp_f7["atq"]); comp_f7["CASH_FLOW"]=comp_f7["oibdpq"]/comp_f7["atq_l1"]
comp_f7["TOBIN_Q"]=(comp_f7["cshoq"]*comp_f7["prccq"]+comp_f7["atq"]-comp_f7["ceqq"]+comp_f7["txditcq"])/comp_f7["atq"]
comp_f7["SALES_GROWTH"]=comp_f7["saleq"]/comp_f7["saleq_l4"]-1
for v in ["CASH_FLOW","TOBIN_Q","SALES_GROWTH"]: comp_f7[v]=comp_f7[v].clip(comp_f7[v].quantile(0.01),comp_f7[v].quantile(0.99))
comp_f7["SIZE"]=comp_f7["SIZE"].clip(comp_f7["SIZE"].quantile(0.01),comp_f7["SIZE"].quantile(0.99))
comp_f7["entity"]=comp_f7["gvkey"]; comp_f7["time"]=comp_f7["cal_yr_qtr"]
comp_f7=comp_f7.set_index(["entity","time"]).sort_index()
for v in ["SIZE","CASH_FLOW","TOBIN_Q","SALES_GROWTH"]: comp_f7[f"{v}_lag"]=comp_f7.groupby(level=0)[v].shift(1)

# Merge beta
comp_f7["POST"]=comp_f7.index.get_level_values("time").isin([20163,20164]).astype(int)
comp_f7=comp_f7.reset_index(); comp_f7["gvkey"]=comp_f7["entity"]
comp_f7=comp_f7.merge(betas[["gvkey","beta_uk","HIGH","LOW"]],on="gvkey",how="inner")
did=comp_f7[(comp_f7["HIGH"]==1)|(comp_f7["LOW"]==1)].copy()
did["interaction"]=did["POST"]*did["HIGH"]

# STOCK_RETURNS
frames3=[]
for y in range(2009,2017):
    for q in range(1,5):
        f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists(): frames3.append(pd.read_parquet(f,columns=["PERMNO","date","RET"]))
cr3=pd.concat(frames3); cr3["date"]=pd.to_datetime(cr3["date"]); cr3["RET"]=pd.to_numeric(cr3["RET"],errors="coerce")
cr3["cyq"]=cr3["date"].dt.year*10+cr3["date"].dt.quarter; cr3["r1"]=1+cr3["RET"].fillna(0)
bhr=cr3.groupby(["PERMNO","cyq"])["r1"].prod()-1; sr=bhr.reset_index(); sr.columns=["PERMNO","cyq","SR_raw"]
sr=sr.merge(ccm[["gvkey","LPERMNO"]].drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
sr=sr.drop_duplicates(subset=["gvkey","cyq"],keep="first"); sr["gvkey"]=sr["gvkey"].astype(str).str.zfill(6)
lo3,hi3=sr["SR_raw"].quantile(0.01),sr["SR_raw"].quantile(0.99); sr["SR"]=sr["SR_raw"].clip(lo3,hi3)
sr=sr[(sr["cyq"]>=20101)&(sr["cyq"]<=20164)][["gvkey","cyq","SR"]]
sr["time"]=sr["cyq"]; sr["entity"]=sr["gvkey"]; sr=sr.set_index(["entity","time"])[["SR"]]
sr["STOCK_RETURNS_lag"]=sr.groupby(level=0)["SR"].shift(1); del cr3,bhr
did=did.merge(sr[["STOCK_RETURNS_lag"]],left_on=["entity","time"],right_index=True,how="left")

# CONSENSUS_EPS (quick)
with zipfile.ZipFile(ROOT/"inputs"/"tr_ibes"/"ibes_statsum.zip") as z:
    with z.open(z.namelist()[0]) as f: ibes=pd.read_csv(f,usecols=["TICKER","CUSIP","OFTIC","STATPERS","MEASURE","FISCALP","FPI","MEANEST","FPEDATS","USFIRM","CURCODE"],dtype={"TICKER":"str","CUSIP":"str","OFTIC":"str"},low_memory=False)
ibes["FPI_n"]=pd.to_numeric(ibes["FPI"],errors="coerce")
ibes=ibes[(ibes["MEASURE"]=="EPS")&(ibes["FISCALP"]=="QTR")&(ibes["FPI_n"]==6)&(ibes["CURCODE"]=="USD")&(ibes["USFIRM"]==1)]
ibes["STATPERS"]=pd.to_datetime(ibes["STATPERS"]); ibes["FPEDATS"]=pd.to_datetime(ibes["FPEDATS"])
ibes=ibes[(ibes["FPEDATS"]>="2010-01-01")&(ibes["FPEDATS"]<="2017-03-31")]; ibes=ibes[ibes["STATPERS"]<ibes["FPEDATS"]]
ibes=ibes.sort_values(["TICKER","FPEDATS","STATPERS"]); ibes=ibes.drop_duplicates(subset=["TICKER","FPEDATS"],keep="last")
ibes["M"]=pd.to_numeric(ibes["MEANEST"],errors="coerce"); fy=ibes["FPEDATS"].dt.year*10+ibes["FPEDATS"].dt.quarter
yr,qtr=fy//10,fy%10; ibes["cyq"]=(np.where(qtr==1,yr-1,yr)*10+np.where(qtr==1,4,qtr-1)).astype(np.int64)
cm2=pd.read_parquet(CSV,columns=["gvkey","tic","cusip","datadate"]); cm2["gvkey"]=cm2["gvkey"].astype(str).str.zfill(6)
cm2["datadate"]=pd.to_datetime(cm2["datadate"]); cm2=cm2[(cm2["datadate"]>="2010-01-01")&(cm2["datadate"]<="2017-03-31")]
cm2["cyq"]=(cm2["datadate"].dt.year*10+cm2["datadate"].dt.quarter).astype(np.int64); cm2["cusip8"]=cm2["cusip"].astype(str).str[:8]
ibes["CUSIP8"]=ibes["CUSIP"].astype(str).str[:8]
vcc=ibes.merge(cm2[["gvkey","cusip8","cyq"]].drop_duplicates(),left_on=["CUSIP8","cyq"],right_on=["cusip8","cyq"],how="inner")
vtt=ibes.merge(cm2[["gvkey","tic","cyq"]].drop_duplicates(),left_on=["OFTIC","cyq"],right_on=["tic","cyq"],how="inner")
cep=pd.concat([vcc[["gvkey","cyq","M"]],vtt[["gvkey","cyq","M"]]],ignore_index=True)
cep=cep.drop_duplicates(subset=["gvkey","cyq"],keep="first"); cep["gvkey"]=cep["gvkey"].astype(str).str.zfill(6)
f7_keys=set(did["gvkey"].unique()); cep=cep[cep["gvkey"].isin(f7_keys)]; cep["Mw"]=np.nan
for qt,ix in cep.groupby("cyq").groups.items():
    v=cep.loc[ix,"M"]
    if v.notna().sum()<10: continue
    lo,hi=v.quantile(0.015),v.quantile(0.985); cep.loc[ix,"Mw"]=v.clip(lo,hi)
cep["CONSENSUS_EPS"]=np.nan
for qt,ix in cep.groupby("cyq").groups.items():
    v=cep.loc[ix,"Mw"]
    if v.notna().sum()<10: continue
    cep.loc[ix,"CONSENSUS_EPS"]=v-v.mean()
cep["entity"]=cep["gvkey"]; cep["time"]=cep["cyq"]; cep=cep.set_index(["entity","time"])[["CONSENSUS_EPS"]]
did=did.merge(cep,left_on=["entity","time"],right_index=True,how="left")

# Complete-case + regressions
for dv_col, dv_label in [("CASH_DV_M1","M1: winsor CASH then CASH/(1-CASH)"),("CASH_DV_M2","M2: CASH/(1-CASH) then winsor")]:
    vars_need=[dv_col,"SIZE_lag","CASH_FLOW_lag","TOBIN_Q_lag","SALES_GROWTH_lag","STOCK_RETURNS_lag","CONSENSUS_EPS","beta_uk","icode100","POST","HIGH","interaction"]
    did_cc=did.dropna(subset=vars_need).copy()
    did_cc=did_cc.set_index(["entity","time"]).sort_index()
    did_cc["ind_time"]=did_cc["icode100"].astype(str)+"_"+did_cc.index.get_level_values("time").astype(str)
    Y=did_cc[dv_col]; X=did_cc[["interaction","SIZE_lag","CASH_FLOW_lag","TOBIN_Q_lag","SALES_GROWTH_lag","STOCK_RETURNS_lag","CONSENSUS_EPS"]]
    did_cc["ind_time_cat"]=pd.Categorical(did_cc["ind_time"])
    mod=PanelOLS(Y,X,entity_effects=True,other_effects=did_cc["ind_time_cat"],drop_absorbed=True)
    res=mod.fit(cov_type="clustered",cluster_entity=True,cluster_time=True)
    d=res.params["interaction"]; se=res.std_errors["interaction"]; p=res.pvalues["interaction"]
    # FE-inclusive R2
    y_raw=did_cc[dv_col].values; rss=np.sum(res.resids.values.flatten()**2)
    tss=np.sum((y_raw-y_raw.mean())**2); r2_fe=1-rss/tss
    print(f"\n{dv_label}:")
    print(f"  delta={d:.4f}, SE={se:.4f}, p={p:.4f}, N={len(did_cc):,}")
    print(f"  Within R2 (PanelOLS): {res.rsquared:.4f}")
    print(f"  FE-inclusive R2 (1 - RSS/TSS): {r2_fe:.4f}")
    print(f"  Paper: delta=0.231, SE=0.059, R2=0.21")
