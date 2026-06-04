"""Validate: do known UK multinationals now rank in TOP β tercile?"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
beta_dir = ROOT/"outputs"/"campello_v2"/"20260527_022317"
beta = pd.read_parquet(beta_dir/"beta_uk.parquet")

comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","conm","tic","sic","loc"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp = comp.drop_duplicates(["gvkey"], keep="last")
merged = beta.merge(comp, on="gvkey", how="left").sort_values("beta_uk", ascending=False)

print(f"TOP 20 by β^UK (VFTSE):")
print(merged[["gvkey","conm","tic","sic","beta_uk","r2"]].head(20).to_string(index=False))

print(f"\nBOTTOM 20 by β^UK (VFTSE):")
print(merged[["gvkey","conm","tic","sic","beta_uk","r2"]].tail(20).to_string(index=False))

print(f"\n=== Known UK-multinational firms — VFTSE β rank ===")
known_uk = ["BP P.L.C", "BARCLAYS", "GLAXOSMITHKLINE", "ASTRAZENECA",
            "UNILEVER", "DIAGEO", "VODAFONE", "HSBC", "ROLLS-ROYCE",
            "FORD MOTOR", "GENERAL MOTORS", "BOEING", "MCDONALD",
            "PROCTER", "JOHNSON & JOHNSON", "PFIZER", "MICROSOFT", "IBM",
            "WAL-MART", "EXXON", "CHEVRON", "COCA-COLA", "PEPSICO",
            "CITIGROUP", "JPMORGAN", "GOLDMAN", "VISA", "GOOGLE", "APPLE"]
N = len(merged)
hits = []
for kw in known_uk:
    matches = merged[merged["conm"].str.contains(kw, case=False, na=False)]
    if len(matches) > 0:
        for _, r in matches.head(2).iterrows():
            rank = (merged["beta_uk"] > r["beta_uk"]).sum() + 1
            pct = (1 - rank/N)*100  # higher = more UK-exposed
            hits.append((r["conm"][:40], r["beta_uk"], rank, pct))
            print(f"  {r['conm'][:40]:<40}  β={r['beta_uk']:+.4f}  rank={rank}/{N}  top-{pct:.0f}%-percentile")

# Distribution check: how many in top tercile?
pos = merged[merged["beta_uk"]>=0]
t70 = pos["beta_uk"].quantile(0.70)
top_share = sum(1 for h in hits if h[1] >= t70)
print(f"\nKnown UK-mult firms in TOP tercile: {top_share}/{len(hits)}")
print(f"  paper expects: most multinationals high; microcap energy LOW")
