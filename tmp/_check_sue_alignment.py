"""Check CONSENSUS_EPS cal_yr_qtr alignment with sample panel."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d/fname).exists()], reverse=True)
    return runs[0]
ceps = pd.read_parquet(latest("consensus_eps.parquet") / "consensus_eps.parquet")
panel = pd.read_parquet(latest("variables_panel.parquet") / "variables_panel.parquet")

# Check: what cal_yr_qtr values exist in ceps vs panel in DiD window
PRE_POST = [20153, 20154, 20163, 20164]
ceps_did = ceps[ceps["cal_yr_qtr"].isin(PRE_POST)]
panel_did = panel[panel["cal_yr_qtr"].isin(PRE_POST)]

print(f"CONSENSUS_EPS in DiD quarters: {len(ceps_did):,}")
print(f"Unique gvkeys: {ceps_did['gvkey'].nunique():,}")
print(f"By quarter: {ceps_did['cal_yr_qtr'].value_counts().sort_index().to_dict()}")
print(f"\nPanel in DiD quarters: {len(panel_did):,}")
print(f"Unique gvkeys: {panel_did['gvkey'].nunique():,}")

# Merge directly
merged = panel_did.merge(ceps_did, on=["gvkey","cal_yr_qtr"], how="inner")
print(f"\nDirect merge (no ticker mapping needed): {len(merged):,}")
print(f"Unique gvkeys matched: {merged['gvkey'].nunique():,}")

# Now check: what % of sample gvkeys have ANY CONSENSUS_EPS during 2010-2017
all_ceps_gvkeys = set(ceps["gvkey"].unique())
sample_gvkeys = set(panel["gvkey"].unique())
print(f"\nTotal sample gvkeys: {len(sample_gvkeys):,}")
print(f"Sample gvkeys with ANY CONSENSUS_EPS: {len(sample_gvkeys & all_ceps_gvkeys):,} ({len(sample_gvkeys & all_ceps_gvkeys)/len(sample_gvkeys)*100:.1f}%)")

# Check: which cal_yr_qtr has most CONSENSUS_EPS?
print(f"\nCONSENSUS_EPS by cal_yr_qtr (top 10):")
for q, n in ceps["cal_yr_qtr"].value_counts().sort_values(ascending=False).head(10).items():
    print(f"  {q}: {n:,}")

print(f"\nPanel obs by cal_yr_qtr (DiD window):")
for q, n in panel_did.groupby("cal_yr_qtr").size().items():
    print(f"  {q}: {n:,}")
