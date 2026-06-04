"""β^UK with VFTSE (implied vol) on RHS — paper p17 eq(13) verbatim.
24-month rolling window 2013-2014 per p32 fn27.
DV: monthly realized vol of firm returns
IV: monthly mean of daily VFTSE
Controls: monthly realized vol of SP500, monthly realized vol of FX$£
"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d/fname).exists()], reverse=True)
    return runs[0]

START = pd.Timestamp("2013-01-01")
END   = pd.Timestamp("2014-12-31")

# --- VFTSE (implied vol, spliced) ---
vftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"VFTSE"/"VFTSE_weeklyspliced_2010_2014.csv")
vftse["Date"] = pd.to_datetime(vftse["Date"])
vftse = vftse[(vftse["Date"]>=START)&(vftse["Date"]<=END)].sort_values("Date")
vftse["ym"] = vftse["Date"].dt.year*100 + vftse["Date"].dt.month
# Monthly mean of daily VFTSE (in pct units; convert to decimal for scale-matched β)
vftse_m = vftse.groupby("ym")["VFTSE"].mean().reset_index().rename(columns={"VFTSE":"VFTSE_m"})
vftse_m["VFTSE_m"] = vftse_m["VFTSE_m"] / 100.0  # decimal
print(f"VFTSE: {len(vftse_m)} months ({vftse_m['ym'].min()}-{vftse_m['ym'].max()}) mean={vftse_m['VFTSE_m'].mean():.4f}")

# --- FX$£ (realized vol of daily FX returns) ---
fx = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"]>=START)&(fx["DATE"]<=END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change()
fx = fx.dropna(subset=["ret"])
fx["ym"] = fx["DATE"].dt.year*100+fx["DATE"].dt.month
fx_vol = fx.groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FX"})

# --- CRSP for firm vol + SP500 ---
crsp_frames = [pd.read_parquet(ROOT/f"inputs/CRSP_DSF/CRSP_DSF_{y}_Q{q}.parquet",
                               columns=["PERMNO","date","RET","sprtrn"])
               for y in range(2013,2015) for q in (1,2,3,4)]
crsp = pd.concat(crsp_frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"])
crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
crsp = crsp.dropna(subset=["RET"])
crsp["ym"] = crsp["date"].dt.year*100 + crsp["date"].dt.month

sp_vol = crsp.drop_duplicates(["date"]).groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn":"vol_SP500"})

market = vftse_m.merge(sp_vol, on="ym").merge(fx_vol, on="ym")
print(f"Market panel: {len(market)} months")
print(market.head(3))

# --- Firm-level monthly vol ---
firm_vol = crsp.groupby(["PERMNO","ym"])["RET"].agg(["std","count"]).reset_index()
firm_vol = firm_vol[firm_vol["count"]>=10].rename(columns={"std":"vol_r"})
firm_vol = firm_vol.merge(market, on="ym")

# --- Link to sample firms via CCM ---
panel = pd.read_parquet(latest("variables_panel.parquet")/"variables_panel.parquet")
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

firm_vol["ym_date"] = pd.to_datetime((firm_vol["ym"]//100).astype(str)+"-"+
                                     (firm_vol["ym"]%100).astype(str).str.zfill(2)+"-15")
m = firm_vol.merge(ccm_s, on="PERMNO")
m = m[(m["ym_date"]>=m["LINKDT"]) & (m["ym_date"]<=m["LINKENDDT"])]
m = m.drop_duplicates(["gvkey","ym"], keep="first")
print(f"Firm-month obs: {len(m):,} firms={m['gvkey'].nunique():,}")

# --- Run β regression per firm: vol_r ~ VFTSE_m + vol_SP500 + vol_FX ---
ctrls = ["VFTSE_m","vol_SP500","vol_FX"]
results = {}
for gv, gr in m.groupby("gvkey"):
    g = gr.dropna(subset=["vol_r"]+ctrls)
    if len(g) < 18: continue
    X = np.column_stack([np.ones(len(g))]+[g[c].values for c in ctrls])
    y = g["vol_r"].values
    try:
        b,*_ = np.linalg.lstsq(X,y,rcond=None)
        yp = X@b; ssr=((y-yp)**2).sum(); sst=((y-y.mean())**2).sum()
        results[gv] = (b[1], len(g), 1-ssr/sst if sst>0 else np.nan)
    except: pass

df = pd.DataFrame([{"gvkey":k,"beta_uk":v[0],"n_months":v[1],"r2":v[2]} for k,v in results.items()])
b = df["beta_uk"]; pos = b[b>=0]
print(f"\nβ^UK (VFTSE-implied, 24m, 3 controls):")
print(f"  N={len(df):,} mean={b.mean():.4f} sd={b.std():.4f} %neg={(b<0).mean()*100:.1f}%")
print(f"  paper benchmark: mean β ≈ 0.45 (Table C.2)")
print(f"  pos terciles: 30%={pos.quantile(0.30):.4f} 70%={pos.quantile(0.70):.4f}")
print(f"  paper terciles: t1=0.28 t2=0.68")

# --- Save ---
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = OUT/ts; out_dir.mkdir(parents=True, exist_ok=True)
df.to_parquet(out_dir/"beta_uk.parquet", index=False)
for fn in ["variables_panel.parquet","stock_returns.parquet","consensus_eps.parquet"]:
    src_dir = latest(fn); shutil.copy(str(src_dir/fn), str(out_dir/fn))
print(f"\nSaved: {out_dir}")
