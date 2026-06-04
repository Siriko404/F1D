"""Supervisor Task 6: Autopsy precisely-estimated negative betas (|t|>=1).
Full input matrices, SHRCD cross-tab, foreign/ADR detection."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24

# ============================================================
# 1. COMPUSTAT SURVIVOR LIST
# ============================================================
print("1. Compustat survivors")
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
# 2. CCM — P-only, date-resolved
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
# 3. LOAD CRSP WITH SHRCD + EXCHCD
# ============================================================
print("3. Loading CRSP daily + SHRCD")
frames=[]
for y in range(2010,2015):
    for q in range(1,5):
        f=ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df=pd.read_parquet(f)
            df=df[df["PERMNO"].isin(survivor_permnos)]
            if len(df)>0: frames.append(df)
cr=pd.concat(frames,ignore_index=True); cr["date"]=pd.to_datetime(cr["date"])
cr["RET"]=pd.to_numeric(cr["RET"],errors="coerce"); cr["sprtrn"]=pd.to_numeric(cr["sprtrn"],errors="coerce")
cr["ym"]=cr["date"].dt.to_period("M").astype(str)

# Extract SHRCD per PERMNO (first observation)
permno_shrcd=cr.groupby("PERMNO")["SHRCD"].first().reset_index()
permno_exchcd=cr.groupby("PERMNO")["EXCHCD"].first().reset_index()
print(f"  SHRCD values: {sorted(permno_shrcd['SHRCD'].dropna().unique())}")

# ============================================================
# 4. MACRO + FIRM VOL + BETAS
# ============================================================
print("4. Macro + firm vol + betas")
sp=cr[["date","sprtrn"]].drop_duplicates(); sp["ym"]=sp["date"].dt.to_period("M").astype(str)
sp_m=sp.groupby("ym")["sprtrn"].std(); sp_m=sp_m[sp.groupby("ym")["sprtrn"].count()>=MIN_DAYS].reset_index()
sp_m.columns=["ym","vol_SP500"]

ftse=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"]=pd.to_datetime(ftse["Date"]); ftse=ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"]=np.log(ftse["Close"]/ftse["Close"].shift(1)); ftse["ym"]=ftse["Date"].dt.to_period("M").astype(str)
ftv=ftse.groupby("ym")["lr"].std(); ftv=ftv[ftse.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
ftv.columns=["ym","vol_FTSE100"]

fx=pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"]=pd.to_datetime(fx["DATE"],dayfirst=True); fx=fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"]=np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1)); fx["ym"]=fx["DATE"].dt.to_period("M").astype(str)
fxv=fx.groupby("ym")["lr"].std(); fxv=fxv[fx.groupby("ym")["lr"].count()>=MIN_DAYS].reset_index()
fxv.columns=["ym","vol_FX"]

macro=sp_m.merge(ftv,on="ym").merge(fxv,on="ym")

g=cr.groupby(["PERMNO","ym"]); fv=g["RET"].std(); fv=fv[g["RET"].count()>=MIN_DAYS].reset_index()
fv.columns=["PERMNO","ym","vol_r"]

mg=fv.merge(macro,on="ym",how="inner")
res=[]
for pn,grp in mg.groupby("PERMNO"):
    grp=grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp)<MIN_MONTHS: continue
    yv=grp["vol_r"].values; n=len(yv)
    X=np.column_stack([np.ones(n),grp["vol_FTSE100"],grp["vol_SP500"],grp["vol_FX"]])
    try:
        b,resid,rank,sing=np.linalg.lstsq(X,yv,rcond=None)
        yh=X@b; ssr=np.sum((yv-yh)**2); sst=np.sum((yv-yv.mean())**2)
        r2=1-ssr/sst if sst>0 else 0
        sigma2=ssr/(n-4) if n>4 else np.nan
        XtX_inv=np.linalg.inv(X.T@X)
        se=np.sqrt(sigma2*XtX_inv[1,1])
        t_stat=b[1]/se if se>0 else np.nan
        res.append({"PERMNO":pn,"beta_uk":b[1],"beta_sp":b[2],"beta_fx":b[3],
                    "n":n,"r2":r2,"t_stat":t_stat,"se":se})
    except: continue

betas=pd.DataFrame(res)
betas=betas.merge(ccm[["gvkey","LPERMNO"]],left_on="PERMNO",right_on="LPERMNO",how="inner")
betas=betas.drop_duplicates(subset=["gvkey"],keep="first")
betas["abs_t"]=betas["t_stat"].abs()
betas=betas.merge(permno_shrcd,on="PERMNO",how="left")
betas=betas.merge(permno_exchcd,on="PERMNO",how="left")

# ============================================================
# TASK 6: PRECISE NEGATIVES AUTOPSY
# ============================================================
print(f"\n{'='*60}")
print("TASK 6: Precise negatives (|t|>=1, beta_uk<0)")
print(f"{'='*60}")

precise_neg = betas[(betas["beta_uk"]<0) & (betas["abs_t"]>=1)]
mush_neg = betas[(betas["beta_uk"]<0) & (betas["abs_t"]<1)]
print(f"  Total firms: {len(betas):,}")
print(f"  Total negatives: {(betas['beta_uk']<0).sum():,}")
print(f"  Precise negatives (|t|>=1): {len(precise_neg):,}")
print(f"  Mush negatives (|t|<1): {len(mush_neg):,}")
print(f"  Precise as % of negatives: {len(precise_neg)/(betas['beta_uk']<0).sum()*100:.1f}%")

# SHRCD cross-tab of precise negatives
print(f"\n  SHRCD distribution — Precise Negatives vs All Firms:")
shrcd_labels = {10:"Common Stock", 11:"Common Stock", 12:"Common Stock",
                30:"ADR", 31:"ADR", 32:"ADR",
                70:"CERTS", 71:"CERTS", 72:"CERTS",
                20:"Closed-end fund", 40:"SBBI", 73:"Other"}
for label, grp in [("ALL FIRMS", betas), ("PRECISE NEG", precise_neg)]:
    print(f"\n  {label} (N={len(grp):,}):")
    shrcd_counts = grp["SHRCD"].value_counts().sort_index()
    for sc, cnt in shrcd_counts.items():
        desc = shrcd_labels.get(int(sc), "UNKNOWN")
        pct = cnt/len(grp)*100
        print(f"    SHRCD {int(sc):.0f} ({desc}): {cnt:,} ({pct:.1f}%)")

# EXCHCD cross-tab
print(f"\n  EXCHCD distribution — Precise Negatives:")
exchcd_counts = precise_neg["EXCHCD"].value_counts().sort_index()
for ec, cnt in exchcd_counts.items():
    pct = cnt/len(precise_neg)*100
    print(f"    EXCHCD {int(ec)}: {cnt:,} ({pct:.1f}%)")

# ============================================================
# SHOW 3 EXAMPLE PRECISE NEGATIVES — FULL INPUT MATRICES
# ============================================================
print(f"\n{'='*60}")
print("3 EXAMPLE PRECISE NEGATIVES — Full 60-month input matrices")
print(f"{'='*60}")

example_perms = precise_neg.nsmallest(3, "beta_uk")["PERMNO"].tolist()

for i, pn in enumerate(example_perms):
    row = precise_neg[precise_neg["PERMNO"]==pn].iloc[0]
    gk = row["gvkey"]
    bt = row["beta_uk"]
    t = row["t_stat"]
    r2 = row["r2"]
    shrcd = row["SHRCD"]
    exchcd = row["EXCHCD"]
    bsp = row["beta_sp"]
    bfx = row["beta_fx"]

    print(f"\n  --- Firm {i+1}: PERMNO={pn} GVKEY={gk} ---")
    print(f"  beta_uk={bt:.4f}  t_stat={t:.2f}  R2={r2:.3f}  beta_sp={bsp:.4f}  beta_fx={bfx:.4f}")
    print(f"  SHRCD={shrcd}  EXCHCD={exchcd}")

    # Get the full input matrix
    fv_pn = fv[fv["PERMNO"]==pn][["ym","vol_r"]].merge(macro,on="ym",how="inner")
    fv_pn = fv_pn.sort_values("ym").dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
    fv_pn = fv_pn[["ym","vol_r","vol_FTSE100","vol_SP500","vol_FX"]]
    fv_pn.columns = ["ym","firm_vol","ftse_vol","sp500_vol","fx_vol"]
    print(f"  n_obs={len(fv_pn)}")
    # Print first and last 5 rows
    print(f"  First 5 rows:")
    print(fv_pn.head(5).to_string(index=False))
    print(f"  ...")
    print(f"  Last 5 rows:")
    print(fv_pn.tail(5).to_string(index=False))

    # Check: what is corr(firm_vol, ftse_vol) and corr(firm_vol, sp500_vol) for this firm?
    corr_ftse = fv_pn["firm_vol"].corr(fv_pn["ftse_vol"])
    corr_sp = fv_pn["firm_vol"].corr(fv_pn["sp500_vol"])
    print(f"  corr(firm_vol, ftse_vol)={corr_ftse:.4f}  corr(firm_vol, sp500_vol)={corr_sp:.4f}")

# ============================================================
# PRECISE NEGATIVES vs ALL — summary
# ============================================================
print(f"\n{'='*60}")
print("PRECISE NEGATIVES — Summary stats vs All")
print(f"{'='*60}")

for label, grp in [("ALL", betas), ("PRECISE NEG", precise_neg), ("MUSH NEG", mush_neg)]:
    print(f"\n  {label} (N={len(grp):,}):")
    print(f"    beta_uk p10={grp['beta_uk'].quantile(0.1):.4f} p50={grp['beta_uk'].median():.4f} p90={grp['beta_uk'].quantile(0.9):.4f}")
    print(f"    |t| p10={grp['abs_t'].quantile(0.1):.3f} p50={grp['abs_t'].median():.3f} p90={grp['abs_t'].quantile(0.9):.3f}")
    print(f"    beta_sp p50={grp['beta_sp'].median():.4f}")
    print(f"    R2 p50={grp['r2'].median():.3f}")

# ADR check
adr_shrcds = [30, 31, 32]
adr_count = precise_neg[precise_neg["SHRCD"].isin(adr_shrcds)].pipe(len)
print(f"\n  Precise negatives with SHRCD 30/31/32 (ADR): {adr_count} ({adr_count/len(precise_neg)*100:.1f}%)")

# UK-flag check: firms with FIC == "GBR" or incorporated in UK
# Check if any precise negs have SHRCD suggesting foreign
foreign_shrcds = [30, 31, 32, 40, 70, 71, 72, 73]
foreign_count = precise_neg[precise_neg["SHRCD"].isin(foreign_shrcds)].pipe(len)
print(f"  Precise negatives with any foreign/ADR SHRCD: {foreign_count} ({foreign_count/len(precise_neg)*100:.1f}%)")

# What SHRCD are the common stock ones?
common_shrcds = [10, 11, 12]
common_count = precise_neg[precise_neg["SHRCD"].isin(common_shrcds)].pipe(len)
print(f"  Precise negatives with SHRCD 10/11/12 (Common Stock): {common_count} ({common_count/len(precise_neg)*100:.1f}%)")
