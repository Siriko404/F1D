"""RA Round 5, Lead #1: Jump/outlier-robust realized vol.
Winsorize daily returns BEFORE computing within-month SD.
Hypothesis: removing idiosyncratic daily jumps from weakly-exposed firms
pulls their betas from negative toward zero/positive, while upper-tail
(genuinely UK-exposed) firms barely move.
Target: negatives 39%-><=20%, cutpoints 0.25/0.67->0.28/0.68, CF-correlation improves."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24

# ============================================================
# 1. Compustat survivors (same as run_did_fix1.py)
# ============================================================
print("=" * 60)
print("1. Build Compustat survivor list")
print("=" * 60)

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

ccm=pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"]=ccm["gvkey"].astype(str).str.zfill(6); ccm=ccm[ccm["LINKTYPE"].isin(["LU","LC"])]; ccm=ccm[ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"]=pd.to_datetime(ccm["LINKDT"],errors="coerce"); ccm["LINKENDDT"]=pd.to_datetime(ccm["LINKENDDT"],errors="coerce")
ccm["LINKENDDT"]=ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm=ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(ccm["LINKDT"]<=pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"]=pd.to_numeric(ccm["LPERMNO"],errors="coerce").astype("Int64"); ccm=ccm.dropna(subset=["LPERMNO"])
ccm_surv=ccm[ccm["gvkey"].isin(survivor_gvkeys)]; survivor_permnos=set(ccm_surv["LPERMNO"].unique())
print(f"Survivors: {len(survivor_gvkeys):,} gvkeys, {len(survivor_permnos):,} permnos")

# ============================================================
# 2. Load daily CRSP returns (survivor permnos only)
# ============================================================
print(f"\n{'='*60}")
print("2. Load daily returns")
print("=" * 60)

frames_ret=[]
for y in range(2010,2015):
    for q in range(1,5):
        f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df=pd.read_parquet(f,columns=["PERMNO","date","RET","sprtrn"])
            df=df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames_ret.append(df)
cr=pd.concat(frames_ret,ignore_index=True); cr["date"]=pd.to_datetime(cr["date"])
cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce"); cr["sprtrn"]=pd.to_numeric(cr["sprtrn"],errors="coerce")
print(f"Daily returns: {len(cr):,} obs, {cr['PERMNO'].nunique():,} permnos")

# ============================================================
# 3. Macro vol (standard, from daily macro returns)
# ============================================================
print(f"\n{'='*60}")
print("3. Macro vol series")
print("=" * 60)

cr_m=cr[["date","sprtrn"]].drop_duplicates()
cr_m["ym"]=cr_m["date"].dt.to_period("M")
sp=cr_m.groupby("ym")["sprtrn"].std()
sp=sp[cr_m.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index(); sp.columns=["ym","vol_SP500"]

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M")
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index(); ftv.columns=["ym","vol_FTSE100"]

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M")
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index(); fxv.columns=["ym","vol_FX"]

macro=sp.merge(ftv,on="ym").merge(fxv,on="ym")
macro["ym"]=macro["ym"].astype(str)
print(f"Macro months: {len(macro)}")

# Ftse/SP500 correlation and variance ratio (Lead #3 diagnostic)
ftse_sp=sp.merge(ftv,on="ym")
corr_ftse_sp=ftse_sp["vol_SP500"].corr(ftse_sp["vol_FTSE100"])
var_ratio=ftse_sp["vol_SP500"].var()/ftse_sp["vol_FTSE100"].var()
print(f"FTSE-SP500 vol corr: {corr_ftse_sp:.4f}")
print(f"Var(SP500)/Var(FTSE100): {var_ratio:.4f}")

# ============================================================
# 4. Build beta variants at different daily-return winsor levels
# ============================================================
print(f"\n{'='*60}")
print("4. Daily-return winsor sweep -> beta distribution")
print("=" * 60)

def build_firm_vol(ret_df, winsor_q=0.0):
    """Build monthly firm vol from daily returns with optional winsorization."""
    r=ret_df.copy()
    if winsor_q > 0:
        # Winsorize daily returns GLOBALLY (cross-sectionally within each day)
        r["RET_w"] = np.nan
        for dt, ix in r.groupby("date").groups.items():
            v = r.loc[ix, "RET"]
            lo, hi = v.quantile(winsor_q), v.quantile(1 - winsor_q)
            r.loc[ix, "RET_w"] = v.clip(lo, hi)
    else:
        r["RET_w"] = r["RET"]

    r["ym"] = r["date"].dt.to_period("M").astype(str)
    g = r.groupby(["PERMNO", "ym"])
    vol = g["RET_w"].std()
    vol = vol[g["RET_w"].count() >= MIN_DAYS].reset_index()
    vol.columns = ["PERMNO", "ym", "vol_r"]
    return vol

def run_beta_estimation(firm_vol):
    """Run eq(13) firm-by-firm OLS and return beta stats."""
    mg = firm_vol.merge(macro, on="ym", how="inner")
    res = []
    for pn, grp in mg.groupby("PERMNO"):
        grp = grp.dropna(subset=["vol_r", "vol_FTSE100", "vol_SP500", "vol_FX"])
        if len(grp) < MIN_MONTHS:
            continue
        yv = grp["vol_r"].values
        X = np.column_stack([np.ones(len(yv)), grp["vol_FTSE100"], grp["vol_SP500"], grp["vol_FX"]])
        try:
            b = np.linalg.lstsq(X, yv, rcond=None)[0]
            yh = X @ b; ssr = np.sum((yv - yh) ** 2); sst = np.sum((yv - yv.mean()) ** 2)
            res.append({"PERMNO": pn, "beta_uk": b[1], "beta_sp": b[2], "beta_fx": b[3],
                        "n": len(grp), "r2": 1 - ssr / sst if sst > 0 else 0})
        except:
            continue
    betas = pd.DataFrame(res)
    betas = betas.merge(ccm_surv[["gvkey", "LPERMNO"]].drop_duplicates(), left_on="PERMNO", right_on="LPERMNO", how="inner")
    betas = betas.drop_duplicates(subset=["gvkey"], keep="first")
    return betas

# Test: global winsor
for wq_label, wq in [("NONE (current)", 0.0), ("0.5%", 0.005), ("1%", 0.01), ("2%", 0.02)]:
    fv = build_firm_vol(cr, wq)
    b = run_beta_estimation(fv)
    bpos = b[b["beta_uk"] >= 0]
    bneg = b[b["beta_uk"] < 0]
    neg_pct = len(bneg) / len(b) * 100
    if len(bpos) >= 3:
        t1, t2 = bpos["beta_uk"].quantile(1/3), bpos["beta_uk"].quantile(2/3)
        hi = (b["beta_uk"] >= t2).sum()
        lo = ((b["beta_uk"] >= 0) & (b["beta_uk"] <= t1)).sum()
    else:
        t1, t2, hi, lo = np.nan, np.nan, 0, 0
    print(f"\n  Winsor {wq_label}:")
    print(f"    N={len(b):,}  Neg={len(bneg):,} ({neg_pct:.1f}%)  Nonneg={len(bpos):,}")
    print(f"    Cutpoints: T1={t1:.4f} T2={t2:.4f}  HIGH={hi:,} LOW={lo:,}")
    print(f"    Paper: T1=0.28 T2=0.68  HIGH=449 LOW=360  Neg<=20%")

# ============================================================
# 5. Also try: PERMNO-level winsorization
# ============================================================
print(f"\n{'='*60}")
print("5. PERMNO-level daily return winsor")
print("=" * 60)

for wq in [0.005, 0.01, 0.02]:
    r=cr.copy()
    r["RET_w"] = np.nan
    for pn, ix in r.groupby("PERMNO").groups.items():
        v = r.loc[ix, "RET"]
        lo, hi = v.quantile(wq), v.quantile(1 - wq)
        r.loc[ix, "RET_w"] = v.clip(lo, hi)
    r["ym"] = r["date"].dt.to_period("M").astype(str)
    g = r.groupby(["PERMNO", "ym"])
    vol = g["RET_w"].std()
    vol = vol[g["RET_w"].count() >= MIN_DAYS].reset_index()
    vol.columns = ["PERMNO", "ym", "vol_r"]

    b = run_beta_estimation(vol)
    bpos = b[b["beta_uk"] >= 0]
    bneg = b[b["beta_uk"] < 0]
    neg_pct = len(bneg) / len(b) * 100
    if len(bpos) >= 3:
        t1, t2 = bpos["beta_uk"].quantile(1/3), bpos["beta_uk"].quantile(2/3)
        hi = (b["beta_uk"] >= t2).sum()
        lo = ((b["beta_uk"] >= 0) & (b["beta_uk"] <= t1)).sum()
    else:
        t1, t2, hi, lo = np.nan, np.nan, 0, 0
    print(f"\n  PERMNO winsor {wq*100:.0f}%:")
    print(f"    N={len(b):,}  Neg={len(bneg):,} ({neg_pct:.1f}%)  Nonneg={len(bpos):,}")
    print(f"    Cutpoints: T1={t1:.4f} T2={t2:.4f}  HIGH={hi:,} LOW={lo:,}")

# ============================================================
# 6. Also try: fixed-return trimming (drop extreme daily returns)
# ============================================================
print(f"\n{'='*60}")
print("6. Fixed-threshold daily return trim")
print("=" * 60)

for threshold in [0.10, 0.15, 0.20, 0.25, 0.30]:
    r=cr.copy()
    r["RET_w"] = r["RET"].clip(-threshold, threshold)
    r["ym"] = r["date"].dt.to_period("M").astype(str)
    g = r.groupby(["PERMNO", "ym"])
    vol = g["RET_w"].std()
    vol = vol[g["RET_w"].count() >= MIN_DAYS].reset_index()
    vol.columns = ["PERMNO", "ym", "vol_r"]

    b = run_beta_estimation(vol)
    bpos = b[b["beta_uk"] >= 0]
    bneg = b[b["beta_uk"] < 0]
    neg_pct = len(bneg) / len(b) * 100
    if len(bpos) >= 3:
        t1, t2 = bpos["beta_uk"].quantile(1/3), bpos["beta_uk"].quantile(2/3)
        hi = (b["beta_uk"] >= t2).sum()
        lo = ((b["beta_uk"] >= 0) & (b["beta_uk"] <= t1)).sum()
    else:
        t1, t2, hi, lo = np.nan, np.nan, 0, 0
    print(f"  Trim +/-{threshold:.0%}: N={len(b):,} Neg={len(bneg):,} ({neg_pct:.1f}%) T1={t1:.4f} T2={t2:.4f} H={hi:,} L={lo:,}")

print(f"\nPaper target: T1=0.28 T2=0.68  HIGH=449 LOW=360  Neg<=20%")
