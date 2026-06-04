"""Compare 4 β specifications: which matches paper anchor + UK-firm rankings?

A: vol(r) ~ VFTSE + vol_SP + vol_FX   (current)
B: standardized vol — firm-demeaned/scaled
C: monthly returns ~ FTSE_ret + SP500_ret + FX_ret  (CAPM-style)
D: log(vol) ~ log(VFTSE) + log(vol_SP) + log(vol_FX)

Paper anchor: mean β ≈ 0.45 (Table C.2); known UK firms should rank HIGH.
"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
START = pd.Timestamp("2013-01-01"); END = pd.Timestamp("2014-12-31")

# Market data
vftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"VFTSE"/"VFTSE_weeklyspliced_2010_2014.csv")
vftse["Date"] = pd.to_datetime(vftse["Date"])
vftse = vftse[(vftse["Date"]>=START)&(vftse["Date"]<=END)].sort_values("Date")
vftse["ym"] = vftse["Date"].dt.year*100 + vftse["Date"].dt.month
vftse_m = vftse.groupby("ym")["VFTSE"].mean().reset_index().rename(columns={"VFTSE":"VFTSE_m"})
vftse_m["VFTSE_m"] = vftse_m["VFTSE_m"]/100.0

ftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"]>=START)&(ftse["Date"]<=END)].sort_values("Date")
ftse["ret"] = ftse["Close"].pct_change()
ftse = ftse.dropna(subset=["ret"])
ftse["ym"] = ftse["Date"].dt.year*100+ftse["Date"].dt.month
ftse_vol = ftse.groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FTSE"})
ftse_ret = ftse.groupby("ym")["ret"].apply(lambda x: (1+x).prod()-1).reset_index().rename(columns={"ret":"ret_FTSE"})

fx = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"]>=START)&(fx["DATE"]<=END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change()
fx = fx.dropna(subset=["ret"])
fx["ym"] = fx["DATE"].dt.year*100+fx["DATE"].dt.month
fx_vol = fx.groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FX"})
fx_ret = fx.groupby("ym")["ret"].apply(lambda x: (1+x).prod()-1).reset_index().rename(columns={"ret":"ret_FX"})

crsp_frames = [pd.read_parquet(ROOT/f"inputs/CRSP_DSF/CRSP_DSF_{y}_Q{q}.parquet",
                               columns=["PERMNO","date","RET","sprtrn"])
               for y in range(2013,2015) for q in (1,2,3,4)]
crsp = pd.concat(crsp_frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"]); crsp["RET"] = pd.to_numeric(crsp["RET"],errors="coerce")
crsp = crsp.dropna(subset=["RET"]); crsp["ym"] = crsp["date"].dt.year*100+crsp["date"].dt.month

sp_uniq = crsp.drop_duplicates(["date"])
sp_vol = sp_uniq.groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn":"vol_SP500"})
sp_ret = sp_uniq.groupby("ym")["sprtrn"].apply(lambda x:(1+x).prod()-1).reset_index().rename(columns={"sprtrn":"ret_SP500"})

market_vol = vftse_m.merge(sp_vol, on="ym").merge(fx_vol, on="ym").merge(ftse_vol, on="ym")
market_ret = ftse_ret.merge(sp_ret, on="ym").merge(fx_ret, on="ym")

# Firm vol + ret
firm_vol = crsp.groupby(["PERMNO","ym"])["RET"].agg(["std","count"]).reset_index()
firm_vol = firm_vol[firm_vol["count"]>=10].rename(columns={"std":"vol_r"})
firm_ret = crsp.groupby(["PERMNO","ym"])["RET"].apply(lambda x:(1+x).prod()-1).reset_index().rename(columns={"RET":"ret_r"})

# CCM link
panel = pd.read_parquet(sorted(OUT.glob("*/variables_panel.parquet"))[-1])
sample_gv = set(panel["gvkey"].unique())
ccm = pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
                      columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["gvkey"].isin(sample_gv)]
ccm = ccm[ccm["LINKTYPE"].isin(["LU","LC"]) & ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce").fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"]>=START) & (ccm["LINKDT"]<=END)]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64").dropna().astype(int)
ccm_s = ccm[["gvkey","LPERMNO","LINKDT","LINKENDDT"]].rename(columns={"LPERMNO":"PERMNO"})

def link(firm_df):
    firm_df["ym_date"] = pd.to_datetime((firm_df["ym"]//100).astype(str)+"-"+
                                        (firm_df["ym"]%100).astype(str).str.zfill(2)+"-15")
    m = firm_df.merge(ccm_s, on="PERMNO")
    m = m[(m["ym_date"]>=m["LINKDT"]) & (m["ym_date"]<=m["LINKENDDT"])]
    return m.drop_duplicates(["gvkey","ym"], keep="first")

fv = link(firm_vol).merge(market_vol, on="ym")
fr = link(firm_ret).merge(market_ret, on="ym")

# Compustat name lookup
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","conm"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp = comp.drop_duplicates(["gvkey"], keep="last")

known = ["BP P.L.C","BARCLAYS","GLAXO","ASTRAZENECA","UNILEVER","DIAGEO","VODAFONE","HSBC",
         "FORD MOTOR","GENERAL MOTORS","MCDONALD","PROCTER","JOHNSON & JOHNSON",
         "PFIZER","MICROSOFT","IBM","WAL-MART","EXXON","CHEVRON","COCA-COLA","PEPSICO",
         "GOLDMAN","JPMORGAN","CITIGROUP","BOEING","APPLE","INTEL"]

def reg_per_firm(df, ycol, xcols, min_n=18):
    res = {}
    for gv, gr in df.groupby("gvkey"):
        g = gr.dropna(subset=[ycol]+xcols)
        if len(g) < min_n: continue
        X = np.column_stack([np.ones(len(g))]+[g[c].values for c in xcols])
        y = g[ycol].values
        try:
            b,*_ = np.linalg.lstsq(X,y,rcond=None)
            res[gv] = b[1]
        except: pass
    return pd.DataFrame([{"gvkey":k,"beta_uk":v} for k,v in res.items()])

def report(name, df, paper_t1=0.28, paper_t2=0.68):
    df2 = df.merge(comp, on="gvkey", how="left")
    b = df["beta_uk"]; pos = b[b>=0]
    print(f"\n=== {name} ===")
    print(f"  N={len(df):,} mean={b.mean():.4f} sd={b.std():.4f} %neg={(b<0).mean()*100:.1f}%")
    if (pos>0).sum() > 10:
        t30 = pos.quantile(0.30); t70 = pos.quantile(0.70)
        print(f"  pos terciles: 30%={t30:.4f} 70%={t70:.4f}  (paper {paper_t1}/{paper_t2})")
    # known UK firms in top tercile?
    df2_s = df2.sort_values("beta_uk", ascending=False)
    N = len(df2_s)
    t70_val = pos.quantile(0.70) if (pos>0).sum()>10 else b.quantile(0.70)
    in_top = 0; total = 0
    for kw in known:
        match = df2_s[df2_s["conm"].str.contains(kw, case=False, na=False)]
        for _, r in match.head(1).iterrows():
            total += 1
            if r["beta_uk"] >= t70_val: in_top += 1
    print(f"  known UK firms in TOP tercile: {in_top}/{total}")
    # Top 10 firms
    print(f"  TOP 10: {df2_s.head(10)[['conm','beta_uk']].values.tolist()}")

# Spec A: vol ~ VFTSE + vol_SP + vol_FX
A = reg_per_firm(fv, "vol_r", ["VFTSE_m","vol_SP500","vol_FX"])
report("A: vol ~ VFTSE+vol_SP+vol_FX", A)

# Spec C: ret ~ ret_FTSE + ret_SP + ret_FX
C = reg_per_firm(fr, "ret_r", ["ret_FTSE","ret_SP500","ret_FX"])
report("C: ret ~ ret_FTSE+ret_SP+ret_FX (CAPM-style)", C, 0.28, 0.68)

# Spec D: log(vol) ~ log(VFTSE) + log(vol_SP) + log(vol_FX)
fv2 = fv.copy()
fv2["log_vol_r"] = np.log(fv2["vol_r"].clip(lower=1e-6))
fv2["log_VFTSE"] = np.log(fv2["VFTSE_m"].clip(lower=1e-6))
fv2["log_vol_SP500"] = np.log(fv2["vol_SP500"].clip(lower=1e-6))
fv2["log_vol_FX"] = np.log(fv2["vol_FX"].clip(lower=1e-6))
D = reg_per_firm(fv2, "log_vol_r", ["log_VFTSE","log_vol_SP500","log_vol_FX"])
report("D: log-log vol", D)

# Spec B: standardized vol
fv3 = fv.copy()
fv3["vol_r_z"] = fv3.groupby("gvkey")["vol_r"].transform(lambda x: (x-x.mean())/(x.std() if x.std()>0 else 1))
B = reg_per_firm(fv3, "vol_r_z", ["VFTSE_m","vol_SP500","vol_FX"])
report("B: firm-standardized vol ~ raw market vols", B)
