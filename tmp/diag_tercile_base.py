"""Test: tercile over FULL beta distribution (incl negatives).
Treated = top third. Control = bottom third, THEN drop beta<0.
Check if control -> ~360 and delta rises."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24

print("="*60)
print("TERCILE BASE EXPERIMENT: Full dist vs nonnegative-only")
print("="*60)

# --- Load betas from Fix 1 ---
# Rebuild survivor list + betas quickly
comp_raw = pd.read_parquet(CSV, columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic",
    "atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
for c in ["atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]:
    comp_raw[c] = pd.to_numeric(comp_raw[c], errors="coerce")
comp_raw["txditcq"] = comp_raw["txditcq"].fillna(0)
comp_raw["gvkey"] = comp_raw["gvkey"].astype(str).str.zfill(6)
comp_raw = comp_raw[(comp_raw["fyearq"]>=2010)&(comp_raw["fyearq"]<=2016)]
comp_raw = comp_raw[comp_raw["fqtr"].isin([1,2,3,4])]
comp_raw = comp_raw[(comp_raw["curcdq"]=="USD")&(comp_raw["fic"]=="USA")]
comp_raw = comp_raw[(comp_raw["atq"]>0)&(comp_raw["saleq"]>0)]
csic = pd.to_numeric(comp_raw["sic"], errors="coerce")
comp_raw = comp_raw[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp_raw["mktcap"] = comp_raw["cshoq"]*comp_raw["prccq"]
comp_raw = comp_raw[(comp_raw["atq"]>=10)&(comp_raw["mktcap"]>=10)]
comp_raw["atq_l1"] = comp_raw.groupby("gvkey")["atq"].shift(1)
comp_raw["saleq_l4"] = comp_raw.groupby("gvkey")["saleq"].shift(4)
has_inv = comp_raw["capxy"].notna() & comp_raw["atq_l1"].notna()
has_cf = comp_raw["oibdpq"].notna() & comp_raw["atq_l1"].notna()
has_q = comp_raw["cshoq"].notna()&comp_raw["prccq"].notna()&comp_raw["atq"].notna()&comp_raw["ceqq"].notna()
has_sg = comp_raw["saleq"].notna()&comp_raw["saleq_l4"].notna()
comp_raw = comp_raw[has_inv & comp_raw["atq"].notna() & has_cf & has_q & has_sg]
comp_raw = comp_raw.sort_values(["gvkey","fyearq","fqtr"])
comp_raw["cal_yr_qtr"] = comp_raw["fyearq"].astype(int)*10+comp_raw["fqtr"].astype(int)
res_rows = []
for gk, grp in comp_raw.groupby("gvkey"):
    grp = grp.sort_values("cal_yr_qtr"); runs, cur = [], []
    for _, row in grp.iterrows():
        if not cur: cur = [row.name]
        else:
            pq = grp.loc[cur[-1],"cal_yr_qtr"]; tq = row["cal_yr_qtr"]; exp = pq+1
            if pq%10==4: exp = (pq//10+1)*10+1
            if tq==exp: cur.append(row.name)
            else: runs.append(cur); cur = [row.name]
    runs.append(cur)
    if runs:
        best = max(runs, key=len)
        if len(best) >= 12: res_rows.append(grp.loc[best])
comp_raw = pd.concat(res_rows, ignore_index=True) if res_rows else pd.DataFrame()
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f:
        fic = pd.read_csv(io.BytesIO(f.read()), sep="\t", usecols=["gvkey","year","icode100"])
fic["gvkey"] = fic["gvkey"].astype(str).str.zfill(6)
comp_raw["year"] = comp_raw["cal_yr_qtr"]//10
comp_raw = comp_raw.merge(fic, on=["gvkey","year"], how="inner")
survivor_gvkeys = set(comp_raw["gvkey"].unique())
del comp_raw

ccm = pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
    columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["LINKTYPE"].isin(["LU","LC"])]; ccm = ccm[ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"],errors="coerce"); ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"],errors="coerce")
ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(ccm["LINKDT"]<=pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"],errors="coerce").astype("Int64"); ccm = ccm.dropna(subset=["LPERMNO"])
ccm_surv = ccm[ccm["gvkey"].isin(survivor_gvkeys)]
survivor_permnos = set(ccm_surv["LPERMNO"].unique())

# Beta estimation (abbreviated, same as Fix 1)
frames, frames2 = [], []
for y in range(2010,2015):
    for q in range(1,5):
        f = ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["PERMNO","date","RET"]); df = df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames.append(df)
            df2 = pd.read_parquet(f, columns=["PERMNO","date","RET","sprtrn"]); df2 = df2[df2["PERMNO"].isin(survivor_permnos)]
            if len(df2)>0: frames2.append(df2)

crsp = pd.concat(frames,ignore_index=True); crsp["date"]=pd.to_datetime(crsp["date"]); crsp["RET"]=pd.to_numeric(crsp["RET"],errors="coerce")
crsp["ym"]=crsp["date"].dt.to_period("M"); g=crsp.groupby(["PERMNO","ym"])
rv=g["RET"].std(); rv=rv[g["RET"].count()>=MIN_DAYS].reset_index(); rv.columns=["PERMNO","ym","vol_r"]
cr2=pd.concat(frames2,ignore_index=True); cr2["date"]=pd.to_datetime(cr2["date"]); cr2["sprtrn"]=pd.to_numeric(cr2["sprtrn"],errors="coerce")
cr2["ym"]=cr2["date"].dt.to_period("M"); sp=cr2[["date","sprtrn","ym"]].drop_duplicates()
sp500=sp.groupby("ym")["sprtrn"].std(); sp500=sp500[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp500.columns=["ym","vol_SP500"]; del crsp, cr2, sp

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M")
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index(); ftv.columns=["ym","vol_FTSE100"]

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M")
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index(); fxv.columns=["ym","vol_FX"]

macro=sp500.merge(ftv,on="ym").merge(fxv,on="ym")
rv["ym"]=rv["ym"].astype(str); macro["ym"]=macro["ym"].astype(str); mg=rv.merge(macro,on="ym",how="inner")
res=[]
for pn,grp in mg.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_r"].values; X=np.column_stack([np.ones(len(yv)),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try:
        b=np.linalg.lstsq(X,yv,rcond=None)[0]; yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
        res.append({"PERMNO":pn,"beta_uk":b[1],"n":len(grp),"r2":1-ssr/sst if sst>0 else 0})
    except: continue
betas=pd.DataFrame(res)
betas=betas.merge(ccm_surv[["gvkey","LPERMNO"]].drop_duplicates(),left_on="PERMNO",right_on="LPERMNO",how="inner")
betas=betas.drop_duplicates(subset=["gvkey"],keep="first"); betas["gvkey"]=betas["gvkey"].astype(str).str.zfill(6)

# --- TERCILE BASE COMPARISON ---
print(f"\nTotal beta firms: {len(betas):,}")
print(f"Nonnegative: {len(betas[betas['beta_uk']>=0]):,}")
print(f"Negative: {len(betas[betas['beta_uk']<0]):,}")

# Method A: Nonnegative-only tercile (current Fix 1)
bpos = betas[betas["beta_uk"] >= 0]
t1_nn, t2_nn = bpos["beta_uk"].quantile(1/3), bpos["beta_uk"].quantile(2/3)
high_nn = (betas["beta_uk"] > t2_nn).sum()
low_nn = ((betas["beta_uk"] >= 0) & (betas["beta_uk"] < t1_nn)).sum()
mid_nn = len(bpos) - high_nn - low_nn
neg_nn = len(betas[betas["beta_uk"] < 0])

# Method B: FULL distribution tercile, then drop beta<0 from control
t1_full, t2_full = betas["beta_uk"].quantile(1/3), betas["beta_uk"].quantile(2/3)
high_full = (betas["beta_uk"] > t2_full).sum()
low_full_all = (betas["beta_uk"] <= t1_full).sum()  # bottom third, all firms
low_full_neg = (betas["beta_uk"] < 0).sum()  # negatives in full dist
low_pos_in_bottom = ((betas["beta_uk"] >= 0) & (betas["beta_uk"] <= t1_full)).sum()
# Control = bottom third, THEN exclude negatives
control_full = low_pos_in_bottom
mid_full = len(betas) - high_full - low_full_all

print(f"\n{'Method':<30} {'HIGH':>8} {'LOW':>8} {'MID':>8} {'NEG':>8} {'T1':>8} {'T2':>8}")
print("-"*80)
print(f"{'A: Nonneg tercile':<30} {high_nn:>8,} {low_nn:>8,} {mid_nn:>8,} {neg_nn:>8,} {t1_nn:>8.4f} {t2_nn:>8.4f}")
print(f"{'B: Full tercile,drop b<0':<30} {high_full:>8,} {control_full:>8,} {mid_full:>8,} {len(betas)-2*high_full:>8,} {t1_full:>8.4f} {t2_full:>8.4f}")
print(f"{'Paper target':<30} {'449':>8} {'360':>8}")

# Detail: what's in the full-dist bottom third?
bot_third = betas[betas["beta_uk"] <= t1_full]
bot_neg = bot_third[bot_third["beta_uk"] < 0]
bot_pos = bot_third[bot_third["beta_uk"] >= 0]
print(f"\nFull-dist bottom third (beta <= {t1_full:.4f}): {len(bot_third):,} firms")
print(f"  Negative (excluded from control): {len(bot_neg):,}")
print(f"  Nonnegative (kept as control): {len(bot_pos):,}")
print(f"  So control = {len(bot_pos):,} (paper: 360)")

# Also show: what if we use paper thresholds?
high_paper = (betas["beta_uk"] > 0.68).sum()
low_paper = ((betas["beta_uk"] >= 0) & (betas["beta_uk"] < 0.28)).sum()
print(f"\nUsing paper fixed thresholds (0.68/0.28):")
print(f"  HIGH (>0.68): {high_paper:,} (paper: 449)")
print(f"  LOW (0<=b<0.28): {low_paper:,} (paper: 360)")
