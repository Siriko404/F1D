"""Check: is high β^UK correlated with negative CONSENSUS_EPS in our data?"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
beta_dir = OUT / "20260527_010458"

beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")
panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
panel = panel[panel["cal_yr_qtr"] <= 20154].merge(ceps, on=["gvkey","cal_yr_qtr"], how="inner")

firm_avg_ceps = panel.groupby("gvkey")["CONSENSUS_EPS"].mean().reset_index()
merged = beta.merge(firm_avg_ceps, on="gvkey", how="inner")

print(f"N firms with both β and CONSENSUS_EPS: {len(merged):,}")
print(f"Correlation β^UK with mean SUE: {merged[['beta_uk','CONSENSUS_EPS']].corr().iloc[0,1]:.4f}")

# Bin firms by β tercile, show CONSENSUS_EPS by tercile
nn = merged[merged["beta_uk"]>=0]
t1 = nn["beta_uk"].quantile(0.30); t2 = nn["beta_uk"].quantile(0.70)
nn["tercile"] = pd.cut(nn["beta_uk"], bins=[-np.inf, t1, t2, np.inf], labels=["Bot","Mid","Top"])
print(f"\nCONSENSUS_EPS by β tercile:")
for tier, grp in nn.groupby("tercile"):
    print(f"  {tier}: N={len(grp):,}  mean CONSENSUS_EPS={grp['CONSENSUS_EPS'].mean():.4f}  median={grp['CONSENSUS_EPS'].median():.4f}")

# What about by β quintile?
print(f"\nCONSENSUS_EPS by β quintile:")
nn["q5"] = pd.qcut(nn["beta_uk"], q=5, labels=[1,2,3,4,5])
for q, grp in nn.groupby("q5"):
    print(f"  Q{q}: N={len(grp):,}  mean β={grp['beta_uk'].mean():.4f}  mean CONSENSUS_EPS={grp['CONSENSUS_EPS'].mean():.4f}")
