"""Test: Table 1 DV vs Table 8 DV in DiD regression"""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path
from linearmodels.panel import PanelOLS

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"

# Build DiD panel (Fix 1 base)
comp = pd.read_parquet(CSV, columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq","cheq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
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
comp_f7=pd.concat(res_rows,ignore_index=True)
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f: fic=pd.read_csv(io.BytesIO(f.read()),sep="\t",usecols=["gvkey","year","icode100"])
fic["gvkey"]=fic["gvkey"].astype(str).str.zfill(6); comp_f7["year"]=comp_f7["cal_yr_qtr"]//10
comp_f7=comp_f7.merge(fic,on=["gvkey","year"],how="inner")
comp_f7=comp_f7[(comp_f7["fyearq"]>=2010)&(comp_f7["fyearq"]<=2016)]

# 3 DV definitions
t1_series=comp_f7["cheq"]/comp_f7["atq_l1"]; lo_t1,hi_t1=t1_series.quantile(0.01),t1_series.quantile(0.99)
comp_f7["DV_T1"]=(comp_f7["cheq"]/comp_f7["atq_l1"]).clip(lo_t1,hi_t1)  # Table 1: cheq/atq_lag
raw_t8=comp_f7["cheq"]/(comp_f7["atq_l1"]-comp_f7["cheq"])
lo_t8,hi_t8=raw_t8.quantile(0.01),raw_t8.quantile(0.99)
comp_f7["DV_T8_direct"]=raw_t8.clip(lo_t8,hi_t8)  # Table 8 direct winsor
comp_f7["DV_T8_transform"]=comp_f7["DV_T1"]/(1-comp_f7["DV_T1"])  # current method

# Controls
comp_f7["SIZE"]=np.log(comp_f7["atq"]); comp_f7["CASH_FLOW"]=comp_f7["oibdpq"]/comp_f7["atq_l1"]
comp_f7["TOBIN_Q"]=(comp_f7["cshoq"]*comp_f7["prccq"]+comp_f7["atq"]-comp_f7["ceqq"]+comp_f7["txditcq"])/comp_f7["atq"]
comp_f7["SALES_GROWTH"]=comp_f7["saleq"]/comp_f7["saleq_l4"]-1
for v in ["CASH_FLOW","TOBIN_Q","SALES_GROWTH"]: comp_f7[v]=comp_f7[v].clip(*comp_f7[v].quantile([0.01,0.99]).values)
comp_f7["SIZE"]=comp_f7["SIZE"].clip(*comp_f7["SIZE"].quantile([0.01,0.99]).values)
comp_f7["entity"]=comp_f7["gvkey"]; comp_f7["time"]=comp_f7["cal_yr_qtr"]
comp_f7=comp_f7.set_index(["entity","time"]).sort_index()
for v in ["SIZE","CASH_FLOW","TOBIN_Q","SALES_GROWTH"]: comp_f7[f"{v}_lag"]=comp_f7.groupby(level=0)[v].shift(1)
comp_f7["POST"]=comp_f7.index.get_level_values("time").isin([20163,20164]).astype(int)
comp_f7=comp_f7.reset_index(); comp_f7["gvkey"]=comp_f7["entity"]

# Beta
betas=pd.read_parquet("tmp/beta_uk_final.parquet")
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
ccm=pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",columns=["gvkey","LPERMNO"])
ccm["gvkey"]=ccm["gvkey"].astype(str).str.zfill(6); ccm["LPERMNO"]=pd.to_numeric(ccm["LPERMNO"],errors="coerce").astype("Int64")
sr=sr.merge(ccm.drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
sr=sr.drop_duplicates(subset=["gvkey","cyq"],keep="first"); sr["gvkey"]=sr["gvkey"].astype(str).str.zfill(6)
lo3,hi3=sr["SR_raw"].quantile(0.01),sr["SR_raw"].quantile(0.99); sr["SR"]=sr["SR_raw"].clip(lo3,hi3)
sr=sr[(sr["cyq"]>=20101)&(sr["cyq"]<=20164)][["gvkey","cyq","SR"]]
sr["time"]=sr["cyq"]; sr["entity"]=sr["gvkey"]; sr=sr.set_index(["entity","time"])[["SR"]]
sr["STOCK_RETURNS_lag"]=sr.groupby(level=0)["SR"].shift(1)
did=did.merge(sr[["STOCK_RETURNS_lag"]],left_on=["entity","time"],right_index=True,how="left")

# Run 3 specs
for dv_col,dv_label in [("DV_T1","T1: cheq/atq_lag"),("DV_T8_direct","T8: cheq/(atq-cheq) direct winsor"),("DV_T8_transform","T8: transform from winsorized T1")]:
    vars_need=[dv_col,"SIZE_lag","CASH_FLOW_lag","TOBIN_Q_lag","SALES_GROWTH_lag","STOCK_RETURNS_lag","icode100","POST","HIGH","interaction"]
    did_cc=did.dropna(subset=vars_need).set_index(["entity","time"]).sort_index()
    did_cc["ind_time"]=did_cc["icode100"].astype(str)+"_"+did_cc.index.get_level_values("time").astype(str)
    Y=did_cc[dv_col]; X=did_cc[["interaction","SIZE_lag","CASH_FLOW_lag","TOBIN_Q_lag","SALES_GROWTH_lag","STOCK_RETURNS_lag"]]
    did_cc["ind_time_cat"]=pd.Categorical(did_cc["ind_time"])
    mod=PanelOLS(Y,X,entity_effects=True,other_effects=did_cc["ind_time_cat"],drop_absorbed=True)
    res=mod.fit(cov_type="clustered",cluster_entity=True,cluster_time=True)
    d=res.params["interaction"]; se=res.std_errors["interaction"]; p=res.pvalues["interaction"]
    print(f"{dv_label}: delta={d:.4f}, SE={se:.4f}, p={p:.4f}, N={len(did_cc):,}, w/in R2={res.rsquared:.4f}")
print(f"Paper: delta=0.231, SE=0.059, p<0.01, N=17,170, R2=0.21")
