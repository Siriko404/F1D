"""Supervisor Task 13: Idiosyncratic vol β^UK — the decisive test."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS_M, MIN_MONTHS, MIN_HALF = 15, 24, 24

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
# 2. CCM
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
# 3. DAILY RETURNS — FULL PERMNO SET
# ============================================================
print("3. Daily returns")
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
print(f"  {len(cr):,} obs, {cr['PERMNO'].nunique():,} PERMNOs")

# ============================================================
# 4. BUILD IDIOSYNCRATIC VOL + TOTAL VOL (per firm-month)
# ============================================================
print("4. Building idiosyncratic vol + total vol")

# For each firm-month: regress daily RET on daily sprtrn, take residual SD
results_m = []
for (pn, ym_val), grp in cr.groupby(["PERMNO", "ym"]):
    n_days = len(grp)
    if n_days < MIN_DAYS_M:
        continue
    # Total vol
    total_vol = grp["RET"].std()
    # Idiosyncratic vol: regress RET on sprtrn (with intercept), residual SD
    y = grp["RET"].values
    X = np.column_stack([np.ones(n_days), grp["sprtrn"].values])
    try:
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        resid = y - X @ b
        idio_vol = np.std(resid, ddof=1)  # same df as total vol
    except:
        idio_vol = np.nan
    results_m.append({"PERMNO": pn, "ym": ym_val, "vol_total": total_vol, "vol_idio": idio_vol, "n_days": n_days})

fv = pd.DataFrame(results_m)
print(f"  Firm-months: {len(fv):,}")

# ============================================================
# 5. MACRO VOL (monthly)
# ============================================================
print("5. Macro vol")
sp=cr[["date","sprtrn"]].drop_duplicates(); sp["ym"]=sp["date"].dt.to_period("M").astype(str)
sp_m=sp.groupby("ym")["sprtrn"].std(); sp_m=sp_m[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS_M].reset_index()
sp_m.columns=["ym","vol_SP500"]

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M").astype(str)
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS_M].reset_index()
ftv.columns=["ym","vol_FTSE100"]

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M").astype(str)
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS_M].reset_index()
fxv.columns=["ym","vol_FX"]

macro=sp_m.merge(ftv,on="ym").merge(fxv,on="ym")

# ============================================================
# 6. β^UK ESTIMATION: TOTAL vs IDIOSYNCRATIC, FULL + SPLIT-HALF
# ============================================================
print("6. β^UK — TOTAL vs IDIOSYNCRATIC")

HALF1_END, HALF2_START = "2012-07", "2012-08"

def est_betas(fv_df, macro_df, vol_col, rhs_vars, ym_start=None, ym_end=None):
    """Estimate β^UK using specified vol column and RHS vars."""
    mg = fv_df.merge(macro_df, on="ym", how="inner")
    if ym_start: mg = mg[mg["ym"] <= ym_start]
    if ym_end: mg = mg[mg["ym"] >= ym_end]
    min_obs = MIN_HALF if (ym_start or ym_end) else MIN_MONTHS
    res = []
    for pn, grp in mg.groupby("PERMNO"):
        grp = grp.dropna(subset=[vol_col] + rhs_vars)
        if len(grp) < min_obs: continue
        yv = grp[vol_col].values; n = len(yv)
        X = np.column_stack([np.ones(n)] + [grp[c].values for c in rhs_vars])
        try:
            b = np.linalg.lstsq(X, yv, rcond=None)[0]
            res.append({"PERMNO": pn, "beta_uk": b[1], "n": n})
        except: continue
    bt = pd.DataFrame(res).merge(ccm[["gvkey", "LPERMNO"]], left_on="PERMNO", right_on="LPERMNO", how="inner")
    bt = bt.drop_duplicates(subset=["gvkey"], keep="first")
    return bt

# THREE variants:
# A: TOTAL vol ~ FTSE + SP500 + FX (baseline)
# B: IDIO vol ~ FTSE + SP500 + FX (idiosyncratic, with SP500)
# C: IDIO vol ~ FTSE + FX (idiosyncratic, no SP500 — market already removed)

variants = [
    ("TOTAL (FTSE+SP+FX)", "vol_total", ["vol_FTSE100", "vol_SP500", "vol_FX"]),
    ("IDIO (FTSE+SP+FX)", "vol_idio", ["vol_FTSE100", "vol_SP500", "vol_FX"]),
    ("IDIO (FTSE+FX)", "vol_idio", ["vol_FTSE100", "vol_FX"]),
]

for label, vcol, rhs in variants:
    bt_full = est_betas(fv, macro, vcol, rhs)
    bt_h1 = est_betas(fv, macro, vcol, rhs, ym_start=HALF1_END)
    bt_h2 = est_betas(fv, macro, vcol, rhs, ym_end=HALF2_START)

    # Split-half
    common = set(bt_h1["gvkey"]) & set(bt_h2["gvkey"])
    b1 = bt_h1[bt_h1["gvkey"].isin(common)].set_index("gvkey")["beta_uk"]
    b2 = bt_h2[bt_h2["gvkey"].isin(common)].set_index("gvkey")["beta_uk"]
    rc_sh = b1.rank().corr(b2.rank())

    # Full stats
    bp = bt_full[bt_full["beta_uk"] >= 0]
    bn = bt_full[bt_full["beta_uk"] < 0]
    neg_pct = len(bn) / len(bt_full) * 100
    if len(bp) >= 3:
        t1, t2 = bp["beta_uk"].quantile(1 / 3), bp["beta_uk"].quantile(2 / 3)
        hi = (bt_full["beta_uk"] >= t2).sum()
        lo = ((bt_full["beta_uk"] >= 0) & (bt_full["beta_uk"] <= t1)).sum()
    else:
        t1, t2, hi, lo = np.nan, np.nan, 0, 0

    print(f"\n  {label}:")
    print(f"    N={len(bt_full):,}  Neg={neg_pct:.1f}%  T1={t1:.4f}  T2={t2:.4f}  H={hi:,} L={lo:,}")
    print(f"    p50={bt_full['beta_uk'].median():.4f}")
    print(f"    ** SPLIT-HALF rank_corr = {rc_sh:.4f} **  (common={len(common):,})")

print(f"\n  Paper: split-half ~0.80 implied, T1=0.28 T2=0.68, Neg<=20%")
print(f"\n  DECISIVE: If idio-vol split-half > 0.3, we found it.")
print(f"            If idio-vol split-half ~ 0, the paper's UK exposure is not from return comovement.")
