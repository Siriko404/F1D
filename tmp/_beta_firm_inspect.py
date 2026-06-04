"""Inspect WHO our high-β^UK firms are. Are they actually UK-exposed?
Check top 20 by β + their characteristics."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
beta_dir = OUT / "20260527_010458"

beta = pd.read_parquet(beta_dir / "beta_uk.parquet")

# Load Compustat for firm names
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","conm","tic","sic","loc"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp = comp.drop_duplicates(["gvkey"], keep="last")

merged = beta.merge(comp, on="gvkey", how="left")
merged = merged.sort_values("beta_uk", ascending=False)

print(f"β^UK distribution:")
print(merged["beta_uk"].describe())

print(f"\nTOP 30 by β^UK (high-UK exposure per our model):")
print(merged[["gvkey","conm","tic","sic","beta_uk","r2"]].head(30).to_string(index=False))

print(f"\nBOTTOM 30 by β^UK (low-UK exposure):")
print(merged[["gvkey","conm","tic","sic","beta_uk","r2"]].tail(30).to_string(index=False))

# SIC distribution by β tercile
nn = merged[merged["beta_uk"]>=0]
t1 = nn["beta_uk"].quantile(0.30); t2 = nn["beta_uk"].quantile(0.70)
top = nn[nn["beta_uk"]>=t2]
bot = nn[nn["beta_uk"]<t1]
print(f"\nSIC2 distribution — TOP tercile (treated, {len(top)}):")
top["sic2"] = pd.to_numeric(top["sic"], errors="coerce").fillna(0).astype(int)//100
print(top["sic2"].value_counts().head(15))
print(f"\nSIC2 distribution — BOT tercile (control, {len(bot)}):")
bot["sic2"] = pd.to_numeric(bot["sic"], errors="coerce").fillna(0).astype(int)//100
print(bot["sic2"].value_counts().head(15))

# Known UK-exposed firms — search by name
print(f"\n=== Known UK-multinational firms — what's their β^UK rank? ===")
known_uk = ["BP", "ROYAL DUTCH SHELL", "BARCLAYS", "GLAXOSMITHKLINE", "ASTRAZENECA",
            "UNILEVER", "DIAGEO", "VODAFONE", "HSBC", "ROLLS-ROYCE",
            "FORD MOTOR", "GENERAL MOTORS", "BOEING", "MCDONALDS", "PEPSI",
            "PROCTER", "JOHNSON & JOHNSON", "PFIZER", "MICROSOFT", "IBM", "WAL-MART"]
for kw in known_uk:
    matches = merged[merged["conm"].str.contains(kw, case=False, na=False)]
    if len(matches) > 0:
        for _, r in matches.head(2).iterrows():
            rank = (merged["beta_uk"] >= r["beta_uk"]).sum()
            pct = rank/len(merged)*100
            print(f"  {r['conm'][:40]:<40}  β={r['beta_uk']:+.4f}  rank={rank}/{len(merged)} ({pct:.0f}th pct)")
