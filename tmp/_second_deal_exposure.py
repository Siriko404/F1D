import glob, numpy as np, pandas as pd
from pathlib import Path
ROOT = Path(".").resolve()
def latest(pat):
    return sorted(glob.glob(str(ROOT/pat)))[-1]

# panel firms (those actually in the regression universe)
p = pd.read_parquet(latest("outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet"),
                    columns=["file_name","start_date","gvkey"])
p["gvkey"]=p["gvkey"].astype(str).str.zfill(6)
panel_firms=set(p["gvkey"].unique())

# manifest c6 -> gvkey
m = pd.read_parquet(latest("outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet"),
                    columns=["gvkey","cusip"])
m["gvkey"]=m["gvkey"].astype(str).str.zfill(6)
m["c6"]=m["cusip"].astype(str).str[:6]
m=m[["gvkey","c6"]].drop_duplicates("gvkey")

# SDC cash deals (>=50% cash), known universe
s=pd.read_parquet(ROOT/"inputs"/"SDC"/"sdc-ma-merged.parquet",
    columns=["Acquiror 6-digit CUSIP","Acquiror Nation","Acquiror Public Status",
             "Date Announced","Deal Status","Percentage of Cash"]).rename(
    columns={"Acquiror 6-digit CUSIP":"c6","Percentage of Cash":"pc"})
s["da"]=pd.to_datetime(s["Date Announced"],errors="coerce")
yr=s["da"].dt.year
known=((yr>=2002)&(yr<=2018)&(s["Acquiror Nation"]=="United States")
       &(s["Acquiror Public Status"]=="Public")
       &(s["Deal Status"].isin(["Completed","Pending","Withdrawn"]))&(s["pc"].notna()))
cd=s[known & (s["pc"]>=50)].copy()
cd["dq"]=cd["da"].dt.year*4+(cd["da"].dt.quarter-1)
# map to gvkey, keep firms in panel
cd=cd.merge(m,on="c6",how="inner")
cd=cd[cd["gvkey"].isin(panel_firms)]

# per firm: sorted distinct cash-deal quarters
g=cd.groupby("gvkey")["dq"].apply(lambda x:sorted(set(x)))
n_treated=g.size
n_multi=(g.apply(len)>=2).sum()
# gap (quarters) between first and second cash deal
gaps=g[g.apply(len)>=2].apply(lambda x:x[1]-x[0])
within4=(gaps<=4).sum()
within8=(gaps<=8).sum()
print(f"Treated cash firms (in panel)      : {n_treated}")
print(f"  with >=2 cash deals 2002-2018    : {n_multi}  ({100*n_multi/n_treated:.1f}%)")
print(f"  with only ONE cash deal          : {n_treated-n_multi}  ({100*(n_treated-n_multi)/n_treated:.1f}%)")
print(f"Among multi-deal firms, gap 1st->2nd cash deal (quarters):")
if len(gaps):
    print(f"  median={gaps.median():.0f}  mean={gaps.mean():.1f}  min={gaps.min()}  p25={gaps.quantile(.25):.0f} p75={gaps.quantile(.75):.0f}")
print(f"  2nd deal within 4 qtrs of 1st    : {within4}  ({100*within4/n_treated:.1f}% of all treated)")
print(f"  2nd deal within 8 qtrs of 1st    : {within8}  ({100*within8/n_treated:.1f}% of all treated)")
