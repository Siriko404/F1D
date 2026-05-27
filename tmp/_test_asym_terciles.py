"""Find tercile method that yields T≈449, C≈360 like paper."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
beta_dir = OUT / "20260527_010458"

beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
n = len(beta); nn = beta[beta["beta_uk"]>=0]
print(f"Total β firms: {n:,}, nonneg: {len(nn):,}, neg: {n-len(nn):,}")
print(f"Paper target: T=449, C=360")

specs = {}

# M1: nonneg→tercile (current)
t1 = nn["beta_uk"].quantile(1/3); t2 = nn["beta_uk"].quantile(2/3)
specs["M1: nonneg→tercile"] = (nn["beta_uk"]>=t2).sum(), ((nn["beta_uk"]>=0)&(nn["beta_uk"]<t1)).sum()

# M2: all→tercile, drop neg from bot
t1a = beta["beta_uk"].quantile(1/3); t2a = beta["beta_uk"].quantile(2/3)
T_M2 = (beta["beta_uk"]>=t2a).sum()
C_M2 = ((beta["beta_uk"]>=0)&(beta["beta_uk"]<t1a)).sum()
specs["M2: all→tercile, C=nonneg below t1"] = T_M2, C_M2
print(f"M2 cutoffs: t1={t1a:.4f} t2={t2a:.4f}")

# M3: FIXED paper cutoffs (t1=0.28, t2=0.68)
specs["M3: fixed cutoffs (0.28, 0.68)"] = (beta["beta_uk"]>0.68).sum(), ((beta["beta_uk"]>=0)&(beta["beta_uk"]<0.28)).sum()

# M4: nonneg→tercile, BOT excludes lowest 10%
nn_sorted = nn.sort_values("beta_uk")
T_M4 = (nn["beta_uk"]>=t2).sum()
C_M4_pool = nn[nn["beta_uk"]<t1]
# drop bottom 10% by β (firms closest to 0)
threshold = C_M4_pool["beta_uk"].quantile(0.10)
specs["M4: nonneg→tercile, bot excludes bottom 10% near-zero"] = T_M4, (C_M4_pool["beta_uk"]>=threshold).sum()

# M5: nonneg→tercile, BOT requires β > 0.05 (paper might exclude very-near-zero)
specs["M5: nonneg→tercile, bot>0.05"] = (nn["beta_uk"]>=t2).sum(), ((nn["beta_uk"]>=0.05)&(nn["beta_uk"]<t1)).sum()

# M6: 30/30 quantile (not 33/33)
t1b = nn["beta_uk"].quantile(0.30); t2b = nn["beta_uk"].quantile(0.70)
specs["M6: nonneg 30/70 quantile"] = (nn["beta_uk"]>=t2b).sum(), (nn["beta_uk"]<t1b).sum()

# M7: Top tercile of ALL, bottom tercile of NONNEG
specs["M7: T=top tercile all, C=bot tercile nonneg"] = (beta["beta_uk"]>=t2a).sum(), ((nn["beta_uk"]<t1)&(nn["beta_uk"]>=0)).sum()

# M8: Force C = top 360 of bottom tercile nonneg (asymmetric trim)
n_C_target = 360
bot_nn = nn[nn["beta_uk"]<t1].nlargest(n_C_target, "beta_uk")
specs["M8: T=nonneg top tercile, C=top 360 of nonneg bot tercile"] = (nn["beta_uk"]>=t2).sum(), len(bot_nn)

# Print all + diff from paper
print(f"\n{'Method':<60}{'T':>8}{'C':>8}{'|T-449|':>10}{'|C-360|':>10}")
print("-"*96)
for name, (t, c) in specs.items():
    print(f"{name:<60}{t:>8}{c:>8}{abs(t-449):>10}{abs(c-360):>10}")
